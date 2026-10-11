"""Full täckning kontrolleras mot oberoende inventarium, aldrig mot kartan själv."""
from datetime import date
import pytest
from riskanalys.regelverk.laddning import ladda_regelbas, STANDARD_REGELBAS
from riskanalys.regelverk.validering import validera
from riskanalys.regelverk.urval import valj, UrvalsFel

@pytest.fixture(scope="module")
def rb():
    return ladda_regelbas(STANDARD_REGELBAS)

def test_v1_ar_giltig_och_ogranskad(rb):
    assert rb.version == "1.2.0"
    assert validera(rb) == []
    assert all(k.sakkunnig.status == "ej_granskad" for k in rb.krav.values())

@pytest.mark.parametrize("paket,lan,fs", [
 ("RP-RED-VG","Västra Götaland","SRC-14FS-2024-11"),
 ("RP-RED-SKANE","Skåne","SRC-12FS-2024-8"),
 ("RP-RED-STHLM","Stockholm","SRC-01FS-2024-20"),
])
def test_full_karta_och_ratt_kalla(rb,paket,lan,fs):
    p=rb.regelpaket[paket]
    for source,antal in (("SRC-PTL",141),("SRC-PTF",29),(fs,31)):
        inventerat={r.lagrum for r in rb.inventarium if r.kalla==source}
        assert len(inventerat)==antal
        assert {r.lagrum for r in p.paragrafkarta.rader if r.kalla==source}==inventerat
    assert not p.paragrafkarta.ohanterade()
    assert all(k.mal for k in (rb.krav[i] for i in p.krav))
    u=valj(rb,paket,date(2026,10,10),lan)
    assert next(k for k in u.krav if k.krav.id=="KRV-LSF-001").lydelse.kalla==fs
    assert {k.krav.lagrum for k in u.krav if k.krav.kalla=="SRC-PTL"} >= {"7 kap. 3 §","7 kap. 6 §"}
    with pytest.raises(UrvalsFel,match="giltighet"):
        valj(rb,paket,date(2026,10,9),lan)

def test_v1_utan_typat_mal_avvisas(rb):
    k=next(iter(rb.krav.values()))
    fel=validera(rb.model_copy(update={"krav":{**rb.krav,k.id:k.model_copy(update={"mal":()})}}))
    assert any("mål" in f for f in fel)

def test_bokstavskapitel_ingar(rb):
    p=rb.regelpaket["RP-RED-VG"]
    assert any(r.lagrum.startswith("4 a kap.") and r.ej_tillamplig for r in p.paragrafkarta.rader)
    assert any(r.lagrum.startswith("7 a kap.") and r.ej_tillamplig for r in p.paragrafkarta.rader)
