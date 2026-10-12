from datetime import date
import pytest
from riskanalys.regelverk.villkor import Faltvarde, Kunskap
from riskanalys.regelverk.modeller import Kundrad, Sakkunnig
from riskanalys.bedomning.kundmodell.utvardering import utvardera_kundmall

from tester.fixturer.kundmodell import syntetisk_mall

@pytest.mark.parametrize("uppdrag,misstanke,expected",[(False,False,"stopp"),(True,False,"undantag"),(True,True,"stopp")])
def test_skatteundantag_upphaver_inte_sjalvstandig_etableringsmisstanke(regelbas_v1,uppdrag,misstanke,expected):
 m,v=syntetisk_mall(regelbas_v1,**{"K-KK.tillracklig":False,"K-ROLL.skatteradgivare":True,"K-UPPDRAG.rattsligt":uppdrag,"K-A.etableringsmisstanke":misstanke})
 assert utvardera_kundmall(m,v,date(2026,10,10)).A==expected

def test_okant_undantag_blir_aldrig_tillatet(regelbas_v1):
 m,v=syntetisk_mall(regelbas_v1,**{"K-KK.tillracklig":False,"K-ROLL.skatteradgivare":True,"K-UPPDRAG.rattsligt":None})
 a=utvardera_kundmall(m,v,date(2026,10,10))
 assert a.A not in ("tillatet","undantag") and "K-UPPDRAG.rattsligt" in a.okanda_uppgifter

def test_transaktionsundantag_provas_for_sig(regelbas_v1):
 m,v=syntetisk_mall(regelbas_v1,**{"K-A.transaktionsmisstanke":True,"K-A.avstaende_forsvarar_utredning":True})
 a=utvardera_kundmall(m,v,date(2026,10,10))
 assert "KA-3-UNDANTAG" in a.regelspar
 assert a.A=="undantag"

@pytest.mark.parametrize("missing",[None,"K-HRTL.moder_omfattas","K-HRTL.lag_risk","K-HRTL.rutiner"])
def test_hrtl_kraver_fem_atgarder_och_alla_undantagsvillkor(regelbas_v1,missing):
 vals={"K-HRTL.etablerad":True,"K-HRTL.ees_filial_dotter":True,"K-HRTL.moder_omfattas":True,"K-HRTL.lag_risk":True,"K-HRTL.rutiner":True}
 if missing:vals[missing]=None
 m,v=syntetisk_mall(regelbas_v1,**vals)
 a=utvardera_kundmall(m,v,date(2026,10,10))
 ids={"KB-HRTL-OVERVAKNING","KB-HRTL-KUND-VH","KB-HRTL-SYFTE","KB-HRTL-MEDEL","KB-HRTL-GODKANNANDE"}
 if missing:assert a.status=="preliminär"
 else:assert not (ids & set(a.B))
 m,v=syntetisk_mall(regelbas_v1,**{"K-HRTL.etablerad":True})
 assert ids <= set(utvardera_kundmall(m,v,date(2026,10,10)).B)

@pytest.mark.parametrize("falt",["K-PEP.kund","K-PEP.vh","K-PEP.familj_rca"])
def test_pep_kund_vh_och_rca_ger_samma_tre_lagbundna_atgarder(regelbas_v1,falt):
 m,v=syntetisk_mall(regelbas_v1,**{falt:True})
 a=utvardera_kundmall(m,v,date(2026,10,10))
 assert {"KB-PEP-MEDEL","KB-PEP-UPPFOLJNING","KB-PEP-GODKANNANDE-INGA-AVBRYTA"} <= set(a.B)

def test_pep_18_manader_ar_kalendermanader_och_hog_risk_kvarstar(regelbas_v1):
 vals={"K-PEP.kund":True,"K-PEP.funktion_upphort":True,"K-PEP.slutdatum":date(2025,1,31)}
 m,v=syntetisk_mall(regelbas_v1,**vals)
 assert "KB-PEP-MEDEL" in utvardera_kundmall(m,v,date(2026,7,30)).B
 assert "KB-PEP-MEDEL" not in utvardera_kundmall(m,v,date(2026,7,31)).B
 v["K-PEP.hog_risk_efter18"]=Faltvarde(Kunskap.KAND,True)
 assert "KB-PEP-MEDEL" in utvardera_kundmall(m,v,date(2026,8,1)).B


@pytest.mark.parametrize('risk',[False,True])
def test_undantaget_i_3_1_galler_aven_riskhanteringsledet(regelbas_v1,risk):
 m,v=syntetisk_mall(regelbas_v1,**{'K-KK.tillracklig':True,'K-A.risk_hanterbar':risk,'K-ROLL.skatteradgivare':True,'K-UPPDRAG.rattsligt':True})
 a=utvardera_kundmall(m,v,date(2026,10,10))
 assert a.A==('tillatet' if risk else 'undantag')
 assert 'KA-RISK-STOPP' not in a.regelspar
 assert 'KA-C-HOG' not in a.regelspar


@pytest.mark.parametrize('saknat',['K-ROLL.skatteradgivare','K-UPPDRAG.rattsligt'])
def test_okant_undantag_vid_riskhanteringsbrist_kraver_mansklig_provning(regelbas_v1,saknat):
 vals={'K-KK.tillracklig':True,'K-A.risk_hanterbar':False,'K-ROLL.skatteradgivare':True,'K-UPPDRAG.rattsligt':True,saknat:None}
 m,v=syntetisk_mall(regelbas_v1,**vals)
 a=utvardera_kundmall(m,v,date(2026,10,10))
 assert a.A=='preliminart' and saknat in a.okanda_uppgifter


@pytest.mark.parametrize('stopp',['K-A.etableringsmisstanke','K-A.transaktionsmisstanke'])
def test_3_1_undantaget_upphaver_aldrig_sjalvstandiga_2_3_stopp(regelbas_v1,stopp):
 m,v=syntetisk_mall(regelbas_v1,**{'K-KK.tillracklig':False,'K-A.risk_hanterbar':False,'K-ROLL.skatteradgivare':True,'K-UPPDRAG.rattsligt':True,stopp:True})
 assert utvardera_kundmall(m,v,date(2026,10,10)).A=='stopp'


@pytest.mark.parametrize('sanktion', [False, True])
def test_hog_c_med_3_1_undantag_upphaver_inte_sanktionsstopp(regelbas_v1, sanktion):
 m,v=syntetisk_mall(regelbas_v1,**{'K-A.risk_hanterbar':False,'K-ROLL.skatteradgivare':True,'K-UPPDRAG.rattsligt':True,'K-SANK.mojlig_traff':sanktion,'K-SANK.identitet_faststalld':True,'K-SANK.utrett_agande_kontroll':True,'K-SANK.forbud_tillampligt':sanktion,'K-SANK.tillstand':False,'K-SANK.primarkalla':'EU-269-2014-art2'})
 m=m.model_copy(update={'rader':tuple(r.model_copy(update={'utfall':{'risk':'hög'}}) if r.spar=='C' else r for r in m.rader)})
 m=m.model_copy(update={'c_granskning':Sakkunnig(status='verifierad',av='Syntetisk granskare',datum=date(2026,10,10),kontrollsumma=m.c_innehallssumma())})
 a=utvardera_kundmall(m,v,date(2026,10,10))
 assert a.C=='hög' and a.A==('stopp' if sanktion else 'undantag')
 assert 'KA-C-HOG' not in a.regelspar
