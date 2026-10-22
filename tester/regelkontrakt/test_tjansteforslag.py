"""Katalogbeskrivningar är ogranskade förslag, inte uppgifter om en viss byrå."""
from riskanalys.regelverk.modeller import Tjanst


def test_elva_tjanster_har_kallbundna_ogranskade_forslag(regelbas_v1):
    assert len(regelbas_v1.tjanster) == 11
    for t in regelbas_v1.tjanster.values():
        assert t.arbetsmoment and t.befogenheter and len(t.kompletteringsfragor) >= 5
        assert t.kallor and t.grund == 'metodval'
        assert t.sakkunnig.status == 'ej_granskad'


def test_tomma_metadata_bevarar_aldre_katalogserialisering(regelbas_v1):
    t = next(iter(regelbas_v1.tjanster.values()))
    data = t.model_dump(mode='json')
    for k in ('arbetsmoment', 'befogenheter', 'kompletteringsfragor'):
        data.pop(k, None)
    gammal = Tjanst.model_validate(data)
    assert gammal.arbetsmoment == () and gammal.befogenheter == ()
    assert gammal.model_dump(mode='json') == data
