"""Handskrivna rättsliga exempel per produktionsrad, oberoende av YAML-villkoren.

Direkt radprov isolerar förutsättningar/undantag. Separata kedjeprov testar de
härledda PEP/C-fälten och beslutens prioritetsordning. Inget juridiskt godkännande.
"""
from datetime import date
import pytest
from riskanalys.regelverk.villkor import Faltvarde, Kunskap, Sanning
from riskanalys.bedomning.kundmodell.tabeller import radutfall
from riskanalys.bedomning.kundmodell.utvardering import utvardera_kundmall
from riskanalys.regelverk.modeller import Kundrad, Sakkunnig
from tester.fixturer.kundmodell import syntetisk_mall

# ID, positiva förutsättningar, fält vars ändring gör raden falsk/okänd.
FALL = [
 ('KA-1-STOPP', {'K-KK.tillracklig':False}, 'K-KK.tillracklig'),
 ('KA-1-UNDANTAG', {'K-KK.tillracklig':False,'K-ROLL.skatteradgivare':True,'K-UPPDRAG.rattsligt':True}, 'K-UPPDRAG.rattsligt'),
 ('KA-2-STOPP', {'K-A.etableringsmisstanke':True}, 'K-A.etableringsmisstanke'),
 ('KA-3-STOPP', {'K-A.transaktionsmisstanke':True}, 'K-A.transaktionsmisstanke'),
 ('KA-3-UNDANTAG', {'K-A.transaktionsmisstanke':True,'K-A.omojligt_avsta':True}, 'K-A.omojligt_avsta'),
 ('KA-RISK-STOPP', {'K-A.risk_hanterbar':False}, 'K-A.risk_hanterbar'),
 ('KA-C-HOG', {'K-C.hog':True,'K-A.risk_hanterbar':False}, 'K-C.hog'),
 ('KA-TILLATET', {}, 'K-KK.tillracklig'),
 ('KB-C-HOG', {'K-C.hog':True}, 'K-C.hog'),
 ('KB-C-LAG', {'K-C.lag':True}, 'K-C.lag'),
 ('KB-HRTL', {'K-HRTL.etablerad':True}, 'K-HRTL.etablerad'),
 ('KB-PEP', {'K-PEP.atgarder_kravs':True}, 'K-PEP.atgarder_kravs'),
 ('KD-3-RAPPORT', {'K-D.skalig_misstanke':True}, 'K-D.skalig_misstanke'),
 ('KD-8-UNDANTAG', {'K-D.skalig_misstanke':True,'K-ROLL.skatteradgivare':True,'K-UPPDRAG.rattsligt':True,'K-D.uppgift_undantagen':True}, 'K-D.uppgift_undantagen'),
 ('KD-2-UTRED', {'K-D.avvikelse_misstankt':True}, 'K-D.avvikelse_misstankt'),
 ('KD-INGEN', {'K-D.utredning_klar':True}, 'K-D.utredning_klar'),
 ('KB-D-9', {'K-D.skalig_misstanke':True}, 'K-D.skalig_misstanke'),
 ('KA-SANK-UTRED', {'K-SANK.mojlig_traff':True,'K-SANK.identitet_faststalld':False,'K-SANK.utrett_agande_kontroll':True,'K-SANK.forbud_tillampligt':True,'K-SANK.primarkalla':'EU-269-2014-art2'}, 'K-SANK.identitet_faststalld'),
 ('KA-SANK-STOPP', {'K-SANK.mojlig_traff':True,'K-SANK.identitet_faststalld':True,'K-SANK.utrett_agande_kontroll':True,'K-SANK.forbud_tillampligt':True,'K-SANK.primarkalla':'EU-269-2014-art2'}, 'K-SANK.identitet_faststalld'),
 ('KA-SANK-TILLSTAND', {'K-SANK.mojlig_traff':True,'K-SANK.tillstand':True}, 'K-SANK.tillstand'),
 ('KC-METOD-PEP', {'K-PEP.atgarder_kravs':True}, 'K-PEP.atgarder_kravs'),
]


def test_varje_kundrad_har_ett_positivt_negativt_och_okant_kontrakt(regelbas_v1):
    assert {r.id for r in regelbas_v1.kundmall.rader} == {id for id,_,_ in FALL}
    assert len(FALL) == len({id for id,_,_ in FALL})


@pytest.mark.parametrize('id,positiv,falt', FALL, ids=[f[0] for f in FALL])
@pytest.mark.parametrize('lage,expected',[('positivt',Sanning.SANT),('negativt',Sanning.FALSKT),('okant',Sanning.OKANT)])
def test_radkontrakt(regelbas_v1,id,positiv,falt,lage,expected):
    _, v = syntetisk_mall(regelbas_v1, **positiv)
    if lage=='negativt':
        v[falt]=Faltvarde(Kunskap.KAND,not v[falt].varde)
    elif lage=='okant':
        v.pop(falt,None)
    mall=regelbas_v1.kundmall
    rad=next(r for r in mall.rader if r.id==id)
    utfall=radutfall(mall,rad,v,date(2026,10,10))
    assert utfall.sanning is expected
    if lage=='okant':
        assert falt in utfall.okanda


@pytest.mark.parametrize('risk',['låg','hög'])
@pytest.mark.parametrize('hanterbar',[False,True])
def test_c_till_a_och_b_sjalvstandigt_stopp(regelbas_v1,risk,hanterbar):
    mall,v=syntetisk_mall(regelbas_v1,**{'K-A.risk_hanterbar':hanterbar})
    c=Kundrad(id='KC-KONTRAKT',spar='C',villkor={'alla':[]},utfall={'risk':risk},grund='metodval',lydelser=(),forklaring='Syntetisk testmetod')
    mall=mall.model_copy(update={'rader':(*(r for r in mall.rader if r.spar!='C'),c)})
    mall=mall.model_copy(update={'c_granskning':Sakkunnig(status='verifierad',av='Testsakkunnig',datum=date(2026,10,10),kontrollsumma=mall.c_innehallssumma())})
    utfall=utvardera_kundmall(mall,v,date(2026,10,10))
    assert utfall.C==risk
    assert utfall.A==('tillatet' if hanterbar else 'stopp')
    assert ('KA-RISK-STOPP' in utfall.regelspar)==(not hanterbar)
    assert ('KA-C-HOG' in utfall.regelspar)==(risk=='hög' and not hanterbar)
    assert ('KB-SKARPT' in utfall.B)==(risk=='hög')
    assert ('KB-FORENKLAT-KAN-PROVAS' in utfall.B)==(risk=='låg')
