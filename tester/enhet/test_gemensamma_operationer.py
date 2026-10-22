"""Gemensamma handlingar använder CAS, bevarar sakstatus och skapar inga beslut."""
import pytest
from riskanalys.analys import modeller as m
from riskanalys.analys.provning import registersumma
from riskanalys.analys.gemensam import postsumma
from riskanalys.analys.tjanst import Analystjanst
from riskanalys.fel import RiskanalysFel
from tester.enhet.test_gemensam_analys_v2 import paket

class Minne(Analystjanst):
    def __init__(self,p,rb,mapp):
        super().__init__(mapp,rb);self.p=p
    def _last(self,revision,**kwargs):
        if revision!=registersumma(self.p):raise RiskanalysFel('Analysen har ändrats i annan flik.')
        return self.p,None,None,self.p.bindning
    def _spara(self,paket,*,forvantad_summa):
        assert forvantad_summa==registersumma(self.p)
        self.p=m.Analyspaket.model_validate(paket.model_copy(update={'revision':paket.revision+1}).model_dump(mode='json'))
        return registersumma(self.p)

@pytest.fixture
def minne(tmp_path,regelbas_v1):
    return Minne(paket(),regelbas_v1,tmp_path)

def referens(p):
    g=p.gemensamma_sarbarhetsprovningar[0]
    return m.GemensamReferens(slag='sarbarhet',post=g.id,summa=postsumma(g))

def test_samlad_bekraftelse_ateranvander_samma_post_for_fyra_tjanster(minne):
    for a in tuple(minne.p.tjanster):
        minne.bekrafta_tillampningar(a.tjanst,(referens(minne.p),),registersumma(minne.p),'Syntetisk')
    assert len(minne.p.gemensamma_sarbarhetsprovningar)==1
    assert all(a.sarbarhetstillampningar[0].bekraftad for a in minne.p.tjanster)
    assert not minne.p.beslut

@pytest.mark.parametrize('stallning',['beror_inte','otillrackligt','galler_annorlunda'])
def test_samlad_bekraftelse_skriver_aldrig_over_avvikelse(minne,stallning):
    a=minne.p.tjanster[0];app=a.sarbarhetstillampningar[0].model_copy(update={'stallningstagande':stallning})
    minne.p=minne.p.model_copy(update={'tjanster':(a.model_copy(update={'sarbarhetstillampningar':(app,)}),)})
    fore=minne.p
    with pytest.raises(RiskanalysFel):minne.bekrafta_tillampningar(a.tjanst,(referens(minne.p),),registersumma(minne.p),'Syntetisk')
    assert minne.p==fore

def test_samlad_bekraftelse_andrar_inte_antagandets_sakstatus(minne):
    g=minne.p.gemensamma_sarbarhetsprovningar[0].model_copy(update={'status':'antagande'})
    minne.p=minne.p.model_copy(update={'gemensamma_sarbarhetsprovningar':(g,)})
    a=minne.p.tjanster[0]
    minne.bekrafta_tillampningar(a.tjanst,(referens(minne.p),),registersumma(minne.p),'Syntetisk')
    assert minne.p.gemensamma_sarbarhetsprovningar[0].status=='antagande'

@pytest.mark.parametrize('fel',['stale','dublett','okand'])
def test_hela_bekraftelsen_ar_atomisk_vid_fel(minne,fel):
    ref=referens(minne.p);a=minne.p.tjanster[0]
    refs=(ref,ref) if fel=='dublett' else (ref,ref.model_copy(update={'post':'saknas'})) if fel=='okand' else (ref.model_copy(update={'summa':'sha256:'+'0'*64}),)
    fore=minne.p
    with pytest.raises(RiskanalysFel):minne.bekrafta_tillampningar(a.tjanst,refs,registersumma(minne.p),'Syntetisk')
    assert minne.p==fore

def test_andrad_gemensam_post_gor_tidigare_tillampning_inaktuell(minne):
    from riskanalys.analys.gemensam import tillampning_aktuell
    gammal=registersumma(minne.p);g=minne.p.gemensamma_sarbarhetsprovningar[0]
    minne.spara_gemensam_sarbarhet(g.model_copy(update={'beskrivning':'Ny syntetisk text'}),gammal,'Syntetisk')
    assert not tillampning_aktuell(minne.p.gemensamma_sarbarhetsprovningar[0],minne.p.tjanster[0].sarbarhetstillampningar[0])
    with pytest.raises(RiskanalysFel):minne.spara_gemensam_sarbarhet(g,gammal,'Syntetisk')
