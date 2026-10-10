"""Oberoende källinventarium upptäcker luckor även när kartan också ändrats."""

from datetime import date

import pytest
from pydantic import ValidationError

from riskanalys.regelverk.laddning import ladda_regelbas
from riskanalys.regelverk.validering import validera


def test_inventarium_fangar_borttagen_paragraf(tmp_path, minimal_filer, skriv_minimal_regelbas):
    minimal_filer["inventering/test.yaml"] = [
        {"kalla": "SRC-1", "lagrum": "2 kap. 1 §", "text": "Test."},
        {"kalla": "SRC-1", "lagrum": "2 kap. 2 §", "text": "En annan regel."},
    ]
    minimal_filer["kallor.yaml"][0]["paragrafer"].remove("2 kap. 2 §")
    minimal_filer["regelpaket/test.yaml"]["paragrafkarta"]["rader"].pop()
    rb = ladda_regelbas(skriv_minimal_regelbas(tmp_path / "rb", minimal_filer))
    assert any("2 kap. 2 §" in fel and "inventari" in fel.lower() for fel in validera(rb))


def test_sfs_inventering_behaller_datumversioner_och_bokstavskapitel():
    from riskanalys.regelverk.inventering import inventera_sfs

    text = """1 kap. Inledning
1 § Första regeln.
2 § /Upphör att gälla U:2026-11-20/ Äldre regel. Lag (2025:1).
2 § /Träder i kraft I:2026-11-20/ Ny regel. Lag (2026:2).
4 a kap. Särskilda uppgifter
1 § En särskild regel.
7 a kap. Samarbete
1 § En annan särskild regel.
Övergångsbestämmelser
2017:630
1. Denna lag träder i kraft den 1 augusti 2017.
"""
    inv = inventera_sfs(text, "SRC-PTL")
    assert [(r.lagrum, r.ikraft, r.upphor) for r in inv] == [
        ("1 kap. 1 §", None, None),
        ("1 kap. 2 §", None, date(2026, 11, 20)),
        ("1 kap. 2 §", date(2026, 11, 20), None),
        ("4 a kap. 1 §", None, None),
        ("7 a kap. 1 §", None, None),
    ]
    assert inv[1].text == "Äldre regel."
    assert inv[2].inford_genom == "SFS 2026:2"
    assert "Övergångsbestämmelser" not in inv[-1].text


def test_sfs_inventering_utan_kapitel_och_med_nummerlucka():
    from riskanalys.regelverk.inventering import inventera_sfs

    inv = inventera_sfs("Förordning\n1 § Första.\n3 § Tredje. Förordning (2026:3).\n", "SRC-PTF")
    assert [r.lagrum for r in inv] == ["1 §", "3 §"]
    assert inv[1].inford_genom == "SFS 2026:3"


def test_inventarium_laddas_som_frysta_poster(tmp_path, minimal_filer, skriv_minimal_regelbas):
    minimal_filer["inventering/test.yaml"] = [
        {"kalla": "SRC-1", "lagrum": "2 kap. 1 §", "text": "Test."}
    ]
    rb = ladda_regelbas(skriv_minimal_regelbas(tmp_path / "rb", minimal_filer))
    assert len(getattr(rb, "inventarium", ())) == 1
    with pytest.raises(ValidationError, match="frozen"):
        rb.inventarium[0].text = "Ändrat"


def test_inventariesumma_inte_kallfilens_summa(tmp_path, minimal_filer, skriv_minimal_regelbas):
    minimal_filer["inventering/test.yaml"] = [
        {"kalla": "SRC-1", "lagrum": "2 kap. 1 §", "text": "Test."}
    ]
    minimal_filer["kallor.yaml"][0]["inventarium_kontrollsumma"] = "sha256:" + "0" * 64
    rb = ladda_regelbas(skriv_minimal_regelbas(tmp_path / "rb", minimal_filer))
    assert any("inventari" in fel.lower() and "summa" in fel for fel in validera(rb))


def test_inventering_tom_kalla_ger_atgardbart_fel():
    from riskanalys.fel import RiskanalysFel
    from riskanalys.regelverk.inventering import inventera_sfs

    with pytest.raises(RiskanalysFel, match="Kontrollera"):
        inventera_sfs("Ingen författning", "SRC-PTL")


def test_hanvisning_i_brodtext_ar_inte_kapitel_eller_ny_paragraf():
    from riskanalys.regelverk.inventering import inventera_sfs

    inv = inventera_sfs("1 kap. Inledning\n1 § En regel.\n2 kap. 3 § samma lag används som stöd.\n2 § En annan regel.\n1 § ska också följas.\n", "SRC-PTL")
    assert [r.lagrum for r in inv] == ["1 kap. 1 §", "1 kap. 2 §"]
    assert "2 kap. 3 § samma lag" in inv[0].text
    assert "1 § ska också följas." in inv[1].text


def test_hanvisning_med_komma_efter_nummer_ar_inte_paragraf():
    from riskanalys.regelverk.inventering import inventera_sfs

    inv = inventera_sfs("8 kap. Bemyndiganden\n1 § Föreskrifter om rutiner enligt 2 kap.\n13 §,\noch rapportering. Lag (2025:637).\n", "SRC-PTL")
    assert len(inv) == 1
    assert "13 §," in inv[0].text


def test_datumrubrik_pa_egen_rad_behalls():
    from riskanalys.regelverk.inventering import inventera_sfs

    inv = inventera_sfs("1 kap. Inledning\n1 § /Träder i kraft I:2026-11-20/\nEn ny regel. Lag (2026:1023).\n", "SRC-PTL")
    assert inv[0].ikraft == date(2026, 11, 20)
    assert inv[0].text == "En ny regel."


def test_offentliga_kallor_har_fullt_daterat_inventarium():
    from riskanalys.regelverk.laddning import STANDARD_REGELBAS
    from riskanalys.regelverk.inventering import inventariesumma

    rb = ladda_regelbas(STANDARD_REGELBAS)
    for kalla_id, antal, unika in (("SRC-PTL", 142, 141), ("SRC-PTF", 29, 29),
                                  ("SRC-14FS-2024-11", 31, 31), ("SRC-12FS-2024-8", 31, 31),
                                  ("SRC-01FS-2024-20", 31, 31)):
        poster = tuple(r for r in rb.inventarium if r.kalla == kalla_id)
        assert len(poster) == antal
        assert len({r.lagrum for r in poster}) == unika
        assert all(r.ikraft is not None for r in poster)
        assert rb.kallor[kalla_id].inventarium_kontrollsumma == inventariesumma(poster)
        assert rb.kallor[kalla_id].kontrollsumma.startswith("sha256:")
    ptl16 = next(r for r in rb.inventarium if r.kalla == "SRC-PTL" and r.lagrum == "2 kap. 16 §")
    assert "sin verksamhet som anställd hos en juridisk person" in ptl16.text
    assert ptl16.ikraft == date(2021, 7, 1)
    framtida = next(r for r in rb.inventarium if r.kalla == "SRC-PTL" and r.lagrum == "1 kap. 2 §" and r.upphor is None)
    assert framtida.ikraft == date(2026, 11, 20)
    lydelser = [r for r in rb.lydelser.values() if r.kalla == "SRC-PTL" and r.lagrum == "1 kap. 2 §"]
    assert [(r.ikraft, r.upphor) for r in sorted(lydelser, key=lambda r: r.ikraft)] == [
        (date(2025, 7, 1), date(2026, 11, 20)), (date(2026, 11, 20), None)
    ]
