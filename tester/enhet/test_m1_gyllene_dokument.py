"""Gyllene prov för den frysta M1-kedjan: dokumentets JSON ska vara byte för byte oförändrat.

Provet bygger dokumentet som typfallen i tester/typfall gör, via kommandoraden mot den frysta v0-regelbasen
(tester/fixturer/regelbas_v0, bytt in av conftest.py i den här mappen) och en fast syntetisk profil.
Kontrollsumman gäller bara den frysta v0-kedjan, inte repots regelbas. Den ändras bara om M1-dokumentets
innehåll medvetet ändras; klartext, kortnamn och v4-format ska inte påverka den.
"""

import hashlib

from riskanalys.cli import main

NY = ["ny", "testbyra", "--regelpaket", "RP-RED-VG", "--lan", "Västra Götaland", "--datum", "2026-11-01"]
M1_DOKUMENT_SUMMA = "sha256:64512acfeb56328ae4da50dffdbac3ebde9ad720591a43eafec218d4cc4dff1d"


def _bygg_m1_dokument(datamapp, real_varden_text, testsvarsfil, capsys):
    assert main(NY) == 0
    for falt_id, text in real_varden_text:
        bekraftelse = ["bekrafta", "testbyra", falt_id, text, "--kalla", "Syntetiskt testfall", "--datum", "2026-10-01"]
        assert main(bekraftelse) == 0
    assert main(["bedom", "testbyra"]) == 0
    assert main(["skriv", "testbyra", "--leverantor", "test", "--testsvar", str(testsvarsfil)]) == 0
    assert main(["utvardera", "testbyra", "--beskrivning", "Första riskbedömningen.", "--datum", "2026-11-01"]) == 0
    assert main(["granska", "testbyra", "--datum", "2026-11-02"]) == 0
    capsys.readouterr()
    (fil,) = (datamapp / "testbyra" / "granskning").glob("*/dokument.json")
    return fil.read_bytes()


def test_m1_dokumentet_ar_byte_for_byte_oforandrat(datamapp, real_varden_text, testsvarsfil, capsys):
    dokument = _bygg_m1_dokument(datamapp, real_varden_text, testsvarsfil, capsys)
    assert "sha256:" + hashlib.sha256(dokument).hexdigest() == M1_DOKUMENT_SUMMA
