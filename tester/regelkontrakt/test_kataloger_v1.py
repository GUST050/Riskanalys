from datetime import date
import pytest
from riskanalys.bedomning.motor import bedom_tjanst
from riskanalys.profil.modeller import Profil, Byra, Uppgift
from riskanalys.profil.hantering import saknade_kritiska
from riskanalys.regelverk.urval import valj

IDS=[*(f"T-RED-{n:02d}" for n in range(1,8)),"T-SKATT-01",*(f"T-BOLAG-{n:02d}" for n in range(1,4))]

@pytest.mark.parametrize("id",IDS)
@pytest.mark.parametrize("erbjuds",[True,False,None])
def test_elva_tjanster_har_separata_erbjudanden(regelbas_v1,id,erbjuds):
    t=regelbas_v1.tjanster[id]
    u={} if erbjuds is None else {t.erbjuds_falt:Uppgift(varde=erbjuds,status="bekräftad",kalla="Test",datum=date(2026,10,10),bekraftad_av="Test")}
    p=Profil(byra=Byra(id="test",regelpaket="RP-RED-VG",lan="Västra Götaland",datum=date(2026,10,10)),uppgifter=u)
    b=bedom_tjanst(regelbas_v1,t,p)
    assert b.erbjuds is erbjuds
    assert t.grund=="metodval"
    assert t.kallhanvisningar and all(h.sida for h in t.kallhanvisningar)
    if erbjuds is False:
        assert b.inneboende is None and b.status=="slutlig"
        missing=saknade_kritiska(p,regelbas_v1,valj(regelbas_v1,p.byra.regelpaket,p.byra.datum,p.byra.lan))
        assert not any(f.startswith(t.erbjuds_falt.removesuffix("_erbjuds")+"_omsattning") for f in missing)
    else:assert b.status=="preliminär"

def test_ej_erbjuda_kraver_inte_kontroll_for_tjansten(regelbas_v1):
    t=regelbas_v1.tjanster["T-RED-05"]
    p=Profil(byra=Byra(id="test",regelpaket="RP-RED-VG",lan="Västra Götaland",datum=date(2026,10,10)),
      uppgifter={s.erbjuds_falt:Uppgift(varde=False,status="bekräftad",kalla="Test",datum=date(2026,10,10),bekraftad_av="Test") for s in regelbas_v1.tjanster.values()})
    missing=saknade_kritiska(p,regelbas_v1,valj(regelbas_v1,p.byra.regelpaket,p.byra.datum,p.byra.lan))
    assert not any(f.startswith("P-KONTROLL.") for f in missing)
    assert "P-ORG.namn" in missing
