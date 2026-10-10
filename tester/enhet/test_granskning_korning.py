from datetime import date

import pytest

from riskanalys.bedomning.korning import BEDOMNINGAR, kor_bedomning
from riskanalys.cli import main
from riskanalys.dokument.skrivning import UTKAST
from riskanalys.fel import RiskanalysFel
from riskanalys.granskning.korning import (
    andrade_kallor,
    granskningens_profil,
    kontrollera_kallor,
    kor_granskning,
    las_granskning,
)
from riskanalys.lagring.korningar import avslutade_korningar
from riskanalys.lagring.manifest import las_manifest
from riskanalys.profil.hantering import bekrafta
from riskanalys.profil.lagring import las_profil, spara_profil

DAG = date(2026, 11, 2)


def test_granska_fore_bedom_sager_vilket_steg_som_saknas(byra_med_profil, regelbas):
    with pytest.raises(RiskanalysFel, match="Kör 'riskanalys bedom testbyra' först"):
        kor_granskning(byra_med_profil, regelbas, DAG)


def test_granskning_av_skriven_byra(skriven_byra, regelbas):
    mapp = kor_granskning(skriven_byra, regelbas, DAG)
    dokument, fynd = las_granskning(mapp)
    assert fynd == ()
    assert "D-ARB.6.1" in dokument.avsnitt_med_id()
    metadata = las_manifest(mapp).metadata
    assert metadata["bedomning"] == avslutade_korningar(skriven_byra, BEDOMNINGAR)[-1].name
    assert metadata["blockerande"] == "0"
    assert metadata["historik"].startswith("sha256:")


def test_profil_andrad_efter_bedomningen_stoppar_granskningen(skriven_byra, regelbas):
    profil = bekrafta(las_profil(skriven_byra), regelbas, "P-ORG.antal_anstallda", "9", "Lönelistan", "FfR", DAG)
    spara_profil(skriven_byra, profil)
    with pytest.raises(RiskanalysFel, match="Profilen har ändrats sedan bedömningen"):
        kor_granskning(skriven_byra, regelbas, DAG)


def test_utkast_fran_en_aldre_bedomning_anvands_inte(skriven_byra, regelbas):
    kor_bedomning(skriven_byra, regelbas)
    dokument, fynd = las_granskning(kor_granskning(skriven_byra, regelbas, DAG))
    assert "D-ARB.6.1" not in dokument.avsnitt_med_id()
    assert {"KRV-LSF-005", "B-04"} <= {post.regel for post in fynd}


def test_kallorna_till_en_ny_granskning_ar_oforandrade(skriven_byra, regelbas):
    assert andrade_kallor(skriven_byra, kor_granskning(skriven_byra, regelbas, DAG)) == []


def test_granskningens_profil_ar_bedomningens_kopia(skriven_byra, regelbas):
    assert granskningens_profil(skriven_byra, kor_granskning(skriven_byra, regelbas, DAG)) == las_profil(skriven_byra)


def _andra_fil(fil):
    fil.write_text(fil.read_text(encoding="utf-8").replace("Testbyrån AB", "Annan byrå AB"), encoding="utf-8")


def test_andrad_profilkopia_i_bedomningen_upptacks(skriven_byra, regelbas):
    mapp = kor_granskning(skriven_byra, regelbas, DAG)
    bedomningsmapp = skriven_byra / BEDOMNINGAR / las_manifest(mapp).metadata["bedomning"]
    _andra_fil(bedomningsmapp / "profil.yaml")
    assert andrade_kallor(skriven_byra, mapp) == ["Bedömningen är ändrad efter körningen. Fil ändrad: profil.yaml"]
    with pytest.raises(RiskanalysFel, match="Kör om kedjan från 'riskanalys bedom'"):
        kontrollera_kallor(skriven_byra, mapp)


def test_andrat_ai_utkast_upptacks(skriven_byra, regelbas):
    mapp = kor_granskning(skriven_byra, regelbas, DAG)
    utkastfil = skriven_byra / UTKAST / las_manifest(mapp).metadata["utkast"] / "D-ARB.6.1.json"
    utkastfil.write_text(utkastfil.read_text(encoding="utf-8").replace("byggkund", "kund"), encoding="utf-8")
    assert andrade_kallor(skriven_byra, mapp) == ["AI-utkasten är ändrade efter skrivningen. Fil ändrad: D-ARB.6.1.json"]


def test_andrad_granskning_upptacks_forst(skriven_byra, regelbas):
    mapp = kor_granskning(skriven_byra, regelbas, DAG)
    _andra_fil(mapp / "dokument.json")
    assert andrade_kallor(skriven_byra, mapp) == ["Granskningen är ändrad efter körningen. Fil ändrad: dokument.json"]


def test_granska_kommandot(skriven_byra, capsys):
    assert main(["granska", "testbyra", "--datum", "2026-11-02"]) == 0
    assert "Fynd: 0." in capsys.readouterr().out


def test_blockerande_fynd_ger_felkod_2(byra_med_profil, capsys):
    main(["bedom", "testbyra"])
    assert main(["granska", "testbyra"]) == 2
    assert "blockerande" in capsys.readouterr().out


def test_oppen_fraga_i_ai_utkastet_blir_granskningsfynd(skriven_byra_med_oppen_fraga, regelbas):
    """Codex 2026-10-10, P1: en öppen fråga från AI får inte stanna i utkastets åtgärdslista."""
    _, fynd = las_granskning(kor_granskning(skriven_byra_med_oppen_fraga, regelbas, DAG))
    (post,) = [post for post in fynd if "öppen fråga" in post.beskrivning]
    assert (post.typ, post.allvar, post.grund, post.avsnitt, post.status) == (
        "sparbarhet",
        "hög",
        "ska_krav",
        "D-ARB.6.1",
        "öppen",
    )
    assert post.beskrivning == (
        "Avsnitt D-ARB.6.1 har en öppen fråga från AI-utkastet: Har byrån bankkoppling för alla kunder? "
        "Uppgift som saknas: P-KANAL.bankdata_andel."
    )
