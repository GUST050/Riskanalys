from datetime import date
import pytest
from tester.fixturer.kundmodell import syntetisk_mall
from riskanalys.bedomning.kundmodell.utvardering import utvardera_kundmall

@pytest.mark.parametrize("genomford",[True,False])
@pytest.mark.parametrize("skyddad,expected",[(True,"undantag"),(False,"rapportera")])
def test_rapportering_ar_sjalvstandig_och_undantag_provas_per_uppgift(regelbas_v1,genomford,skyddad,expected):
 m,v=syntetisk_mall(regelbas_v1,**{"K-D.skalig_misstanke":True,"K-D.transaktion_genomford":genomford,"K-ROLL.skatteradgivare":True,"K-UPPDRAG.rattsligt":True,"K-D.uppgift_undantagen":skyddad,"K-KK.tillracklig":False})
 a=utvardera_kundmall(m,v,date(2026,10,10))
 assert a.D==expected and a.A=="undantag"
 assert "KB-D-MEDDELANDEFORBUD" in a.B

def test_okant_uppgiftsskydd_ar_inte_rapportera_false(regelbas_v1):
 m,v=syntetisk_mall(regelbas_v1,**{"K-D.skalig_misstanke":True,"K-ROLL.skatteradgivare":True,"K-UPPDRAG.rattsligt":True,"K-D.uppgift_undantagen":None})
 a=utvardera_kundmall(m,v,date(2026,10,10))
 assert a.D=="preliminart" and "K-D.uppgift_undantagen" in a.okanda_uppgifter

def test_avvikelse_kraver_bedomning_innan_ingen_misstanke(regelbas_v1):
 m,v=syntetisk_mall(regelbas_v1,**{"K-D.avvikelse_misstankt":True,"K-D.utredning_klar":False,"K-D.skalig_misstanke":False})
 assert utvardera_kundmall(m,v,date(2026,10,10)).D=="preliminart"


@pytest.mark.parametrize('okant', ['K-D.utredning_klar', 'K-D.avvikelse_misstankt'])
def test_bekraftad_rapportering_kvarstar_nar_annan_utredningsuppgift_ar_okand(regelbas_v1, okant):
 m,v=syntetisk_mall(regelbas_v1,**{'K-D.skalig_misstanke':True,okant:None})
 assert utvardera_kundmall(m,v,date(2026,10,10)).D=='rapportera'
