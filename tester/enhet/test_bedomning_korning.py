from datetime import date

import pytest

from riskanalys.bedomning.korning import (
    BEDOMNINGSFIL,
    aktualitetshinder,
    kontrollera_aktuell,
    kor_bedomning,
    las_bedomning,
    las_bedomningsprofil,
    profilen_har_andrats,
    regelbasen_har_andrats,
)
from riskanalys.cli import main
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.datamapp import skapa_byramapp
from riskanalys.lagring.manifest import las_manifest, verifiera_manifest
from riskanalys.profil.hantering import bekrafta
from riskanalys.profil.lagring import las_profil, spara_profil


def test_korningen_sparar_bedomning_profilkopia_och_manifest(byra_med_profil, regelbas):
    mapp = kor_bedomning(byra_med_profil, regelbas)
    assert verifiera_manifest(mapp) == []
    metadata = las_manifest(mapp).metadata
    assert metadata["typ"] == "bedomning"
    assert metadata["regelbas_kontrollsumma"] == regelbas.kontrollsumma
    assert metadata["status"] == "slutlig"
    assert las_bedomning(mapp).tjanster[0].kvarstaende == "hög"
    assert las_bedomningsprofil(mapp) == las_profil(byra_med_profil)


def test_andrad_profil_upptacks(byra_med_profil, regelbas):
    mapp = kor_bedomning(byra_med_profil, regelbas)
    assert not profilen_har_andrats(byra_med_profil, mapp)
    profil = bekrafta(
        las_profil(byra_med_profil), regelbas, "P-KUND.andel_kontant", "20 %", "Kassarapport", "FfR", date(2026, 10, 2)
    )
    spara_profil(byra_med_profil, profil)
    assert profilen_har_andrats(byra_med_profil, mapp)


def test_andrad_regelbas_upptacks(byra_med_profil, regelbas, minimal_regelbas):
    mapp = kor_bedomning(byra_med_profil, regelbas)
    assert not regelbasen_har_andrats(mapp, regelbas)
    assert regelbasen_har_andrats(mapp, minimal_regelbas)


def test_aktuell_bedomning_har_inga_hinder(byra_med_profil, regelbas):
    mapp = kor_bedomning(byra_med_profil, regelbas)
    assert aktualitetshinder(byra_med_profil, mapp, regelbas) == []
    kontrollera_aktuell(byra_med_profil, mapp, regelbas)


def test_andrad_profil_ger_hinder_som_sager_vad_som_ska_goras(byra_med_profil, regelbas):
    mapp = kor_bedomning(byra_med_profil, regelbas)
    profil = bekrafta(
        las_profil(byra_med_profil), regelbas, "P-ORG.antal_anstallda", "9", "Lönelistan", "FfR", date(2026, 10, 2)
    )
    spara_profil(byra_med_profil, profil)
    with pytest.raises(RiskanalysFel, match="Profilen har ändrats sedan bedömningen. Kör 'riskanalys bedom' igen."):
        kontrollera_aktuell(byra_med_profil, mapp, regelbas)


def test_manipulerad_bedomningsfil_ger_hinder(byra_med_profil, regelbas):
    mapp = kor_bedomning(byra_med_profil, regelbas)
    fil = mapp / BEDOMNINGSFIL
    fil.write_text(fil.read_text(encoding="utf-8").replace('"hög"', '"låg"'), encoding="utf-8")
    assert any("Fil ändrad: bedomning.json" in rad for rad in aktualitetshinder(byra_med_profil, mapp, regelbas))


def test_bedom_kommandot_visar_nivaerna(byra_med_profil, capsys):
    assert main(["bedom", "testbyra"]) == 0
    utskrift = capsys.readouterr().out
    assert "T-RED-01 Löpande bokföring: inneboende risk hög, terrorfinansiering måttlig, kvarstående risk hög." in utskrift


def test_bedom_med_okand_uppgift_ar_preliminar(datamapp, regelbas, profil_fabrik, real_varden, capsys):
    mapp = skapa_byramapp("testbyra")
    spara_profil(mapp, profil_fabrik(regelbas, real_varden, okanda=("P-KUND.andel_kontant",)))
    assert main(["bedom", "testbyra"]) == 0
    assert "preliminär" in capsys.readouterr().out


def test_bedom_for_okand_byra(datamapp, capsys):
    assert main(["bedom", "saknas"]) == 1
    assert "finns inte" in capsys.readouterr().err


# Slutgranskningen 2026-10-10, Important #5: profilens värden prövas mot fältregistret innan de används.


def _andra_profilfil(byramapp, falt_id, **andringar):
    import yaml

    from riskanalys.profil.lagring import PROFILFIL

    fil = byramapp / PROFILFIL
    data = yaml.safe_load(fil.read_text(encoding="utf-8"))
    data["uppgifter"][falt_id] = {**data["uppgifter"][falt_id], **andringar}
    fil.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


@pytest.mark.parametrize(
    "falt_id, varde",
    [("P-KUND.andel_riskbransch", "30 %"), ("P-KANAL.bankdata_andel", 40), ("P-VERK.juniora_konsulter", "nej")],
)
def test_handredigerat_varde_av_fel_typ_stoppar_bedomningen(byra_med_profil, regelbas, falt_id, varde):
    from riskanalys.bedomning.korning import BEDOMNINGAR
    from riskanalys.lagring.korningar import avslutade_korningar
    from riskanalys.profil.hantering import ProfilFel

    _andra_profilfil(byra_med_profil, falt_id, varde=varde)
    with pytest.raises(ProfilFel) as fel:
        kor_bedomning(byra_med_profil, regelbas)
    assert falt_id in str(fel.value)
    assert "riskanalys bekrafta" in str(fel.value)
    assert avslutade_korningar(byra_med_profil, BEDOMNINGAR) == []


def test_profil_som_inte_foljer_schemat_ger_begripligt_fel(byra_med_profil, capsys):
    _andra_profilfil(byra_med_profil, "P-KUND.andel_kontant", status="kanske")
    assert main(["bedom", "testbyra"]) == 1
    fel = capsys.readouterr().err
    assert "Profilen i" in fel
    assert "kan inte läsas" in fel


@pytest.mark.parametrize(
    "falt_id, andringar, saknas",
    [
        ("P-KUND.andel_kontant", {"kalla": None}, "källa"),
        ("P-KUND.andel_kontant", {"kalla": "  "}, "källa"),
        ("P-KUND.andel_kontant", {"datum": None}, "datum"),
        ("P-KUND.andel_kontant", {"bekraftad_av": None}, "vem som bekräftat"),
        ("P-VERK.juniora_konsulter", {"status": "ej_tillämplig", "varde": None, "motivering": None}, "motivering"),
    ],
)
def test_uppgift_utan_belagg_for_sin_status_stoppar_bedomningen(byra_med_profil, regelbas, falt_id, andringar, saknas):
    """Codex 2026-10-10, P2: status bekräftad eller ej tillämplig gäller bara med sina belägg (spec 6.2 och 10)."""
    from riskanalys.bedomning.korning import BEDOMNINGAR
    from riskanalys.lagring.korningar import avslutade_korningar
    from riskanalys.profil.hantering import ProfilFel

    _andra_profilfil(byra_med_profil, falt_id, **andringar)
    with pytest.raises(ProfilFel) as fel:
        kor_bedomning(byra_med_profil, regelbas)
    assert falt_id in str(fel.value)
    assert saknas in str(fel.value)
    assert avslutade_korningar(byra_med_profil, BEDOMNINGAR) == []
