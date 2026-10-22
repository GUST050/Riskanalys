"""Schema2-rutter genom riktig loopback-HTTP. Endast syntetiska fakta."""
import pytest
from riskanalys.analys.lagring import las_analys
from riskanalys.analys.provning import registersumma
from riskanalys.analys.gemensam import postsumma
from riskanalys.analys.tjanst import Analystjanst
from tester.intag.test_analys import analysmiljo
from tester.intag.test_webb import anrop

@pytest.fixture
def gemensam_miljo(analysmiljo):
    s,t=analysmiljo;Analystjanst(t.mapp,t.rb).starta('',schema=2)
    return s,t


def test_tre_arbetsvyer_finns_utan_nya_ai_anrop(gemensam_miljo):
    s,t=gemensam_miljo;p=las_analys(t.mapp);antal=len(s.leverantor.delanrop)
    for vag in ('analys?byraanalys=ja','analys?tjanst='+p.tjanster[0].tjanst+'&tillampningar=ja','analys?tjanst='+p.tjanster[0].tjanst+'&granska=ja'):
        kod,html,_=anrop(s,vag);assert kod==200
        assert 'analysbeslut' in html or 'Gemensam byråanalys' in html or 'Tjänstens tillämpning' in html
    assert len(s.leverantor.delanrop)==antal and not las_analys(t.mapp).beslut


def test_gemensamt_formular_sparar_evidens_och_stoppar_gammal_flik(gemensam_miljo):
    s,t=gemensam_miljo;p=las_analys(t.mapp);g=p.gemensamma_sarbarhetsprovningar[0]
    d={**g.model_dump(mode='json'),'typ':'sarbarhet','csrf':s.csrf,'revision':registersumma(p),'forfattare':'Syntetisk',
       'beskrivning':'Gemensamt belagt underlag för hela den syntetiska byrån','motivering':'Syntetiskt belagd lokal mekanism','belagg':p.belagg[0].id,'status':'bekraftad','relevans':'relevant'}
    for key in ('sarbarheter','profilfalt','hot'):d[key]=','.join(d[key])
    assert anrop(s,'analysgemensampost',d)[0]==200
    n=las_analys(t.mapp);ny=n.gemensamma_sarbarhetsprovningar[0]
    assert ny.beskrivning==d['beskrivning'] and ny.forfattare=='Syntetisk' and ny.belagg==(p.belagg[0].id,)
    assert anrop(s,'analysgemensampost',d)[0]==409
    assert las_analys(t.mapp)==n


@pytest.mark.parametrize('fel',['csrf','riktning','origin'])
def test_felaktig_tillampningspost_ar_utan_sidoeffekt(gemensam_miljo,fel):
    s,t=gemensam_miljo;p=las_analys(t.mapp);g=p.gemensamma_sarbarhetsprovningar[0]
    d=dict(csrf=s.csrf,revision=registersumma(p),tjanst=p.tjanster[0].tjanst,slag='sarbarhet',post=g.id,postsumma=postsumma(g),stallningstagande='beror_inte',motivering='Syntetiskt belagd avvikelse',belagg=p.belagg[0].id,forfattare='Syntetisk')
    if fel=='csrf':d['csrf']='fel'
    if fel=='riktning':d['riktning']='lagre'
    extra={'Origin':'https://example.invalid'} if fel=='origin' else None
    assert anrop(s,'analystillampning',d,headers=extra)[0] in (400,403)
    assert las_analys(t.mapp)==p


def test_visat_stallningstagande_skapar_inga_svar_eller_beslut(gemensam_miljo):
    s,t=gemensam_miljo;p=las_analys(t.mapp);g=p.gemensamma_sarbarhetsprovningar[0]
    data=dict(csrf=s.csrf,revision=registersumma(p),tjanst=p.tjanster[0].tjanst,slag='sarbarhet',post=g.id,
              postsumma=postsumma(g),stallningstagande='galler_annorlunda',operation='visa')
    kod,html,_=anrop(s,'analystillampning',data)
    assert kod==200 and 'name="riktningsval.riktning"' in html
    assert las_analys(t.mapp)==p and not p.beslut


def test_okand_tjanst_i_gemensam_vy_ger_lasbart_fel(gemensam_miljo):
    s,t=gemensam_miljo
    kod,html,_=anrop(s,'analys?tjanst=FINNS-INTE&tillampningar=ja')
    assert kod==400 and 'Välj en tjänst' in html
