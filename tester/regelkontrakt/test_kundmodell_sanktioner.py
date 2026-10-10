from datetime import date
import pytest
from tester.fixturer.kundmodell import syntetisk_mall
from riskanalys.bedomning.kundmodell.utvardering import utvardera_kundmall

def test_mojlig_namntraff_ar_inte_bekraftat_forbud(regelbas_v1):
 m,v=syntetisk_mall(regelbas_v1,**{"K-SANK.mojlig_traff":True,"K-SANK.identitet_faststalld":False})
 a=utvardera_kundmall(m,v,date(2026,10,10))
 assert a.A=="preliminart"
 assert "KA-SANK-UTRED" in a.regelspar
 assert next(r for r in m.rader if r.id=="KA-SANK-UTRED").grund=="metodval"

@pytest.mark.parametrize("missing",[None,"K-SANK.primarkalla","K-SANK.utrett_agande_kontroll","K-SANK.tillstand"])
def test_forbud_kraver_exakt_kalla_och_sjalvstandig_provning(regelbas_v1,missing):
 vals={"K-SANK.mojlig_traff":True,"K-SANK.identitet_faststalld":True,"K-SANK.utrett_agande_kontroll":True,"K-SANK.forbud_tillampligt":True,"K-SANK.tillstand":False,"K-SANK.primarkalla":"EU-269-2014-art2"}
 if missing:vals[missing]=None
 m,v=syntetisk_mall(regelbas_v1,**vals)
 a=utvardera_kundmall(m,v,date(2026,10,10))
 assert a.A==("stopp" if missing is None else "preliminart")

def test_tillstand_ar_inte_generell_frikanning(regelbas_v1):
 m,v=syntetisk_mall(regelbas_v1,**{"K-SANK.mojlig_traff":True,"K-SANK.identitet_faststalld":True,"K-SANK.utrett_agande_kontroll":True,"K-SANK.forbud_tillampligt":True,"K-SANK.tillstand":True,"K-SANK.primarkalla":"EU-269-2014-art2"})
 assert utvardera_kundmall(m,v,date(2026,10,10)).A=="preliminart"

def test_mojlig_traff_med_ogjord_agandekontroll_blir_inte_tillatet(regelbas_v1):
 m,v=syntetisk_mall(regelbas_v1,**{'K-SANK.mojlig_traff':True,'K-SANK.identitet_faststalld':True,'K-SANK.utrett_agande_kontroll':False,'K-SANK.forbud_tillampligt':False,'K-SANK.tillstand':False,'K-SANK.primarkalla':'EU-269-2014-art2'})
 a=utvardera_kundmall(m,v,date(2026,10,10))
 assert a.A=='preliminart' and 'KA-SANK-UTRED' in a.regelspar
