"""Alternativa länskällor väljs efter lydelsen, inte huvudkällan."""

from datetime import date

import pytest

from riskanalys.regelverk.laddning import ladda_regelbas
from riskanalys.regelverk.urval import UrvalsFel, valj, vantande_andringar
from riskanalys.regelverk.validering import validera


@pytest.fixture
def lansbas(tmp_path, minimal_filer, skriv_minimal_regelbas):
    kalla = minimal_filer["kallor.yaml"][0]
    lyd = minimal_filer["lydelser.yaml"][0]
    for suffix, lan in (("SK", "Skåne"), ("ST", "Stockholm")):
        minimal_filer["kallor.yaml"].append({**kalla, "id": "SRC-" + suffix, "geografi": [lan]})
        minimal_filer["lydelser.yaml"].append({**lyd, "id": "LYD-" + suffix, "kalla": "SRC-" + suffix})
        minimal_filer["lydelsetexter/LYD-" + suffix + ".txt"] = minimal_filer["lydelsetexter/LYD-1.txt"]
    minimal_filer["krav/test.yaml"][0]["lydelser"] = ["LYD-1", "LYD-SK", "LYD-ST"]
    minimal_filer["regelpaket/test.yaml"]["lan"] = ["Västra Götaland", "Skåne", "Stockholm"]
    return ladda_regelbas(skriv_minimal_regelbas(tmp_path / "rb", minimal_filer))


@pytest.mark.parametrize("lan,lyd", [("Västra Götaland", "LYD-1"), ("Skåne", "LYD-SK"), ("Stockholm", "LYD-ST")])
def test_alternativ_lydelse_valjs_per_lan(lansbas, lan, lyd):
    urval = valj(lansbas, "RP-1", date(2026, 10, 10), lan)
    assert [k.lydelse.id for k in urval.krav] == [lyd]
    assert validera(lansbas) == []


def test_verkligt_overlapp_inom_lanet_avvisas(lansbas):
    andra = lansbas.kallor["SRC-SK"].model_copy(update={"geografi": ("Västra Götaland",)})
    rb = lansbas.model_copy(update={"kallor": {**lansbas.kallor, "SRC-SK": andra}})
    with pytest.raises(UrvalsFel, match="flera giltiga"):
        valj(rb, "RP-1", date(2026, 10, 10), "Västra Götaland")


def test_alternativ_kallas_geografi_binds_till_sakkunnigsumma(lansbas):
    summa = lansbas.kravets_innehallssumma("KRV-1")
    andra = lansbas.kallor["SRC-SK"].model_copy(update={"geografi": ("Kalmar",)})
    rb = lansbas.model_copy(update={"kallor": {**lansbas.kallor, "SRC-SK": andra}})
    assert rb.kravets_innehallssumma("KRV-1") != summa


@pytest.mark.parametrize("lan", ["Västra Götaland", "Skåne", "Stockholm"])
def test_nationell_lydelse_galler_i_alla_lan(lansbas, lan):
    nationell = lansbas.kallor["SRC-1"].model_copy(update={"geografi": ()})
    krav = lansbas.krav["KRV-1"].model_copy(update={"lydelser": ("LYD-1",)})
    rb = lansbas.model_copy(update={"kallor": {**lansbas.kallor, "SRC-1": nationell}, "krav": {"KRV-1": krav}})
    assert valj(rb, "RP-1", date(2026, 10, 10), lan).krav[0].lydelse.id == "LYD-1"


def test_vantande_andringar_filtreras_pa_lydelsens_geografi(lansbas):
    ny = lansbas.lydelser["LYD-SK"].model_copy(update={"ikraft": date(2026, 11, 20)})
    rb = lansbas.model_copy(update={"lydelser": {**lansbas.lydelser, "LYD-SK": ny}})
    urval = valj(rb, "RP-1", date(2026, 10, 10), "Västra Götaland")
    assert vantande_andringar(rb, urval) == ()


def test_v1_saknad_bindande_lydelse_far_inte_tyst_falla_bort(minimal_regelbas):
    lydelse = minimal_regelbas.lydelser["LYD-1"].model_copy(update={"upphor": date(2026, 1, 1)})
    rb = minimal_regelbas.model_copy(update={"version": "1.0.0", "lydelser": {"LYD-1": lydelse}})
    with pytest.raises(UrvalsFel, match="saknar giltig"):
        valj(rb, "RP-1", date(2026, 10, 10), "Västra Götaland")
