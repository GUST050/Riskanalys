"""Typfall för M1: hela kedjan via kommandoraden med syntetiska uppgifter (spec 15).

Filen innehåller också regressionstester för tre brister som Codex reproducerade 2026-10-09.
De går genom kommandoraden, så att de kan köras mot planens kod både före och efter rättningen.
"""

import shutil

import pytest
import yaml

from riskanalys.cli import main
from riskanalys.faststallelse.faststall import FASTSTALLDA
from riskanalys.lagring.manifest import las_manifest, verifiera_manifest
from riskanalys.regelverk.laddning import ladda_regelbas, lydelsetextens_kontrollsumma

NY = ["ny", "testbyra", "--regelpaket", "RP-RED-VG", "--lan", "Västra Götaland", "--datum", "2026-11-01"]
BESLUT = ["--organ", "styrelsen", "--datum", "2026-11-15", "--namn", "Testa Testsson"]
SENARE_BESLUT = ["--organ", "styrelsen", "--datum", "2026-11-20", "--namn", "Testa Testsson"]
LYDELSE = "LYD-LSF-2-3-2024-07-01"
GODKANN = ["--godkann", "--namn", "Testa Testsson", "--datum", "2026-11-03"]


def _kor_fram_till_faststallelse(regelbasargument, real_varden_text, testsvarsfil, capsys):
    """Kör varje steg som en användare gör och kontrollerar att det lyckas."""
    assert main([*NY, *regelbasargument]) == 0
    for falt_id, text in real_varden_text:
        bekraftelse = ["bekrafta", "testbyra", falt_id, text, "--kalla", "Syntetiskt testfall", "--datum", "2026-10-01"]
        assert main([*bekraftelse, *regelbasargument]) == 0
    capsys.readouterr()
    assert main(["profil", "testbyra", *regelbasargument]) == 0
    assert "Kritiska uppgifter som saknas: 0" in capsys.readouterr().out
    assert main(["bedom", "testbyra", *regelbasargument]) == 0
    assert main(["skriv", "testbyra", "--leverantor", "test", "--testsvar", str(testsvarsfil), *regelbasargument]) == 0
    assert main(["utvardera", "testbyra", "--beskrivning", "Första riskbedömningen.", "--datum", "2026-11-01"]) == 0
    assert main(["granska", "testbyra", "--datum", "2026-11-02", *regelbasargument]) == 0
    assert main(["exportera", "testbyra", "--utkast", "--datum", "2026-11-02"]) == 0
    capsys.readouterr()
    assert main(["sakgranska", "testbyra"]) == 0
    avsnitt = [rad.split()[0] for rad in capsys.readouterr().out.splitlines() if rad.startswith("D-ARB.")]
    assert avsnitt == ["D-ARB.1", "D-ARB.3", "D-ARB.4", "D-ARB.5", "D-ARB.6.1", "D-ARB.10"]
    for avsnitt_id in avsnitt:
        assert main(["sakgranska", "testbyra", "--avsnitt", avsnitt_id, *GODKANN]) == 0


def test_hela_kedjan_med_signerad_regelbas(datamapp, signerad_regelbas_rot, real_varden_text, testsvarsfil, capsys):
    regelbasargument = ["--regelbas", str(signerad_regelbas_rot)]
    _kor_fram_till_faststallelse(regelbasargument, real_varden_text, testsvarsfil, capsys)
    assert main(["faststall", "testbyra", *BESLUT, *regelbasargument]) == 0
    assert main(["verifiera", "testbyra", "1"]) == 0


def test_repots_regelbas_kan_inte_faststallas_utan_sakkunnig(datamapp, real_varden_text, testsvarsfil, capsys):
    _kor_fram_till_faststallelse([], real_varden_text, testsvarsfil, capsys)
    capsys.readouterr()
    assert main(["faststall", "testbyra", *BESLUT]) == 1
    assert "inte verifierat av sakkunnig" in capsys.readouterr().err
    assert not (datamapp / "testbyra" / FASTSTALLDA).exists()


def test_aterstallningsprov(
    datamapp, tmp_path, monkeypatch, signerad_regelbas_rot, real_varden_text, testsvarsfil, capsys
):
    """Ett fastställt paket återställs från säkerhetskopia i en tom datamapp och verifieras (spec 5.3 och 16)."""
    regelbasargument = ["--regelbas", str(signerad_regelbas_rot)]
    _kor_fram_till_faststallelse(regelbasargument, real_varden_text, testsvarsfil, capsys)
    assert main(["faststall", "testbyra", *BESLUT, *regelbasargument]) == 0
    sakerhetskopia = tmp_path / "sakerhetskopia" / "v1"
    shutil.copytree(datamapp / "testbyra" / FASTSTALLDA / "v1", sakerhetskopia)

    ny_datamapp = tmp_path / "ny_dator" / "data"
    monkeypatch.setenv("RISKANALYS_DATA", str(ny_datamapp))
    aterstalld = ny_datamapp / "testbyra" / FASTSTALLDA / "v1"
    shutil.copytree(sakerhetskopia, aterstalld)
    capsys.readouterr()
    assert main(["verifiera", "testbyra", "1"]) == 0
    assert "Version 1 stämmer med manifestet." in capsys.readouterr().out
    assert verifiera_manifest(aterstalld) == []
    regelbas = ladda_regelbas(aterstalld / "regelbas")
    assert regelbas.kontrollsumma == las_manifest(aterstalld).metadata["regelbas_kontrollsumma"]


def _skriv_yaml(fil, data):
    fil.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _andra_paragraftext(rot, lydelse_id, ny_text):
    """Ändrar en paragraftext och dess textkontrollsumma, så att regelbasen fortfarande går att läsa in."""
    (rot / "lydelsetexter" / f"{lydelse_id}.txt").write_text(ny_text, encoding="utf-8")
    fil = rot / "lydelser.yaml"
    lydelser = yaml.safe_load(fil.read_text(encoding="utf-8"))
    summa = lydelsetextens_kontrollsumma(ny_text)
    _skriv_yaml(fil, [{**post, "text_kontrollsumma": summa} if post["id"] == lydelse_id else post for post in lydelser])


def _signera_om(rot, summor):
    """Det en sakkunnig gör efter ny granskning: skriver in de nya summorna."""
    for fil in (rot / "krav").glob("*.yaml"):
        poster = yaml.safe_load(fil.read_text(encoding="utf-8"))
        _skriv_yaml(fil, [{**post, "sakkunnig": {**post["sakkunnig"], "kontrollsumma": summor[post["id"]]}} for post in poster])
    for fil in (rot / "regelpaket").glob("*.yaml"):
        paket = yaml.safe_load(fil.read_text(encoding="utf-8"))
        karta = paket["paragrafkarta"]
        ny_signatur = {**karta["sakkunnig"], "kontrollsumma": summor[f"{paket['id']} paragrafkarta"]}
        _skriv_yaml(fil, {**paket, "paragrafkarta": {**karta, "sakkunnig": ny_signatur}})


def test_regression_andrad_paragraftext_kraver_ny_sakkunniggranskning(datamapp, signerad_regelbas_rot, capsys):
    """Fel A: ett godkänt krav fortsatte att gälla när den paragraf det bygger på fick ny text."""
    regelbasargument = ["--regelbas", str(signerad_regelbas_rot)]
    _andra_paragraftext(signerad_regelbas_rot, LYDELSE, "Verksamhetsutövaren ska utvärdera riskbedömningen vartannat år.")
    assert main(["regelbas", "validera", *regelbasargument]) == 1
    assert "KRV-LSF-006: innehållet har ändrats efter sakkunniggranskningen." in capsys.readouterr().err
    assert main([*NY, *regelbasargument]) == 1
    assert not (datamapp / "testbyra").exists()
    capsys.readouterr()
    assert main(["regelbas", "summor", *regelbasargument]) == 0
    summor = dict(rad.rsplit(" ", 1) for rad in capsys.readouterr().out.splitlines())
    _signera_om(signerad_regelbas_rot, summor)
    assert main(["regelbas", "validera", *regelbasargument]) == 0


def test_regression_byte_av_ansvarig_person_kraver_ny_sakgranskning(
    datamapp, signerad_regelbas_rot, real_varden_text, testsvarsfil, capsys
):
    """Fel B: godkännandet av mallen med {roll:FfR} följde med när ett annat namn sattes in vid exporten."""
    regelbasargument = ["--regelbas", str(signerad_regelbas_rot)]
    _kor_fram_till_faststallelse(regelbasargument, real_varden_text, testsvarsfil, capsys)
    bekraftelse = ["bekrafta", "testbyra", "P-ROLL.ffr_namn", "Ny Person", "--kalla", "Styrelseprotokoll"]
    assert main([*bekraftelse, "--datum", "2026-11-04", *regelbasargument]) == 0
    assert main(["bedom", "testbyra", *regelbasargument]) == 0
    assert main(["skriv", "testbyra", "--leverantor", "test", "--testsvar", str(testsvarsfil), *regelbasargument]) == 0
    assert main(["granska", "testbyra", "--datum", "2026-11-05", *regelbasargument]) == 0
    capsys.readouterr()
    assert main(["faststall", "testbyra", *BESLUT, *regelbasargument]) == 1
    assert "Avsnitt D-ARB.1 är inte sakgranskat i nuvarande lydelse." in capsys.readouterr().err
    assert not (datamapp / "testbyra" / FASTSTALLDA).exists()


def test_regression_andrat_tidigare_paket_foljer_inte_med(
    datamapp, signerad_regelbas_rot, real_varden_text, testsvarsfil, capsys
):
    """Fel C: ett ändrat beslut i v1 lästes in i versionshistoriken och följde med till v2."""
    regelbasargument = ["--regelbas", str(signerad_regelbas_rot)]
    _kor_fram_till_faststallelse(regelbasargument, real_varden_text, testsvarsfil, capsys)
    assert main(["faststall", "testbyra", *BESLUT, *regelbasargument]) == 0
    beslut = datamapp / "testbyra" / FASTSTALLDA / "v1" / "beslut.yaml"
    beslut.write_text(beslut.read_text(encoding="utf-8").replace("styrelsen", "ledningsgruppen"), encoding="utf-8")
    assert main(["granska", "testbyra", "--datum", "2026-11-16", *regelbasargument]) == 0
    capsys.readouterr()
    assert main(["faststall", "testbyra", *SENARE_BESLUT, *regelbasargument]) == 1
    assert "Version 1 stämmer inte med sitt manifest: Fil ändrad: beslut.yaml" in capsys.readouterr().err
    assert not (datamapp / "testbyra" / FASTSTALLDA / "v2").exists()


def test_regression_ofullstandigt_tidigare_paket_ger_begripligt_fel(
    datamapp, signerad_regelbas_rot, real_varden_text, testsvarsfil, capsys
):
    """Fel C: ett tidigare paket utan manifest gav en krasch i stället för ett meddelande."""
    regelbasargument = ["--regelbas", str(signerad_regelbas_rot)]
    _kor_fram_till_faststallelse(regelbasargument, real_varden_text, testsvarsfil, capsys)
    assert main(["faststall", "testbyra", *BESLUT, *regelbasargument]) == 0
    (datamapp / "testbyra" / FASTSTALLDA / "v1" / "manifest.json").unlink()
    assert main(["granska", "testbyra", "--datum", "2026-11-16", *regelbasargument]) == 0
    capsys.readouterr()
    assert main(["faststall", "testbyra", *SENARE_BESLUT, *regelbasargument]) == 1
    assert "Version 1 stämmer inte med sitt manifest: Manifest saknas" in capsys.readouterr().err


@pytest.mark.parametrize("innehall", ["{inte json", "{}"], ids=["trasig_json", "saknade_falt"])
def test_regression_skadat_manifest_i_tidigare_paket_ger_begripligt_fel(
    datamapp, signerad_regelbas_rot, real_varden_text, testsvarsfil, capsys, innehall
):
    """Codex 2026-10-09: ett skadat manifest gav en krasch i både verifiera och faststall."""
    regelbasargument = ["--regelbas", str(signerad_regelbas_rot)]
    _kor_fram_till_faststallelse(regelbasargument, real_varden_text, testsvarsfil, capsys)
    assert main(["faststall", "testbyra", *BESLUT, *regelbasargument]) == 0
    (datamapp / "testbyra" / FASTSTALLDA / "v1" / "manifest.json").write_text(innehall, encoding="utf-8")
    capsys.readouterr()
    assert main(["verifiera", "testbyra", "1"]) == 2
    utskrift = capsys.readouterr().out
    assert "är skadat och kan inte läsas." in utskrift
    assert "Återställ versionen från säkerhetskopian" in utskrift
    assert main(["granska", "testbyra", "--datum", "2026-11-16", *regelbasargument]) == 0
    capsys.readouterr()
    assert main(["faststall", "testbyra", *SENARE_BESLUT, *regelbasargument]) == 1
    fel = capsys.readouterr().err
    assert "Version 1 stämmer inte med sitt manifest: Manifestet i" in fel
    assert "Återställ paketet från säkerhetskopian." in fel
    assert not (datamapp / "testbyra" / FASTSTALLDA / "v2").exists()
