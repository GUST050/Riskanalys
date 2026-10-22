"""Reproduktioner från den oberoende helgranskningen; syntetiska data."""
import pytest
from riskanalys.analys import modeller as m
from riskanalys.analys.gemensam import postsumma
from tester.enhet.test_riktning_v2 import fall,med_post
from tester.enhet.test_gemensam_provning_v2 import provfall


@pytest.mark.parametrize('riskled,saknas',[('inneboende','kvarstående'),('kvarstaende','inneboende')])
def test_egen_risk_kraver_varje_nodvandigt_riskled(fall,riskled,saknas):
    from riskanalys.analys.provning_v2 import tackningsbrister
    p,t,_=provfall(fall,riskled=riskled)
    scenario=next(s for s in t.scenarier if s.hot=='H-03' and s.dimension=='pt')
    assert scenario.risk=='hög' and scenario.kvarstaende=='måttlig'
    assert any('saknar' in x and saknas in x for x in tackningsbrister(fall.rb,p,t))


@pytest.mark.parametrize('hot,dimension',[('H-TF-01','pt'),('H-01','tf')])
def test_oforenligt_hot_och_dimension_skapar_aldrig_tyst_egen_risk(fall,hot,dimension):
    from riskanalys.analys.provning_v2 import gemensamma_analysbrister
    p,t=med_post(fall,faktor=None,hot=(hot,));g=p.gemensamma_sarbarhetsprovningar[0].model_copy(update={'dimension':dimension})
    a=p.tjanster[0];app=a.sarbarhetstillampningar[0].model_copy(update={'postsumma':postsumma(g)})
    p=p.model_copy(update={'gemensamma_sarbarhetsprovningar':(g,),'tjanster':(a.model_copy(update={'sarbarhetstillampningar':(app,)}),)})
    assert any(g.id in x and 'dimension' in x for x in gemensamma_analysbrister(fall.rb,fall.profil,fall.bedomning,p))


def test_samma_id_i_skilda_typade_postregister_kan_statusprovas(fall):
    from riskanalys.analys.provning_v2 import gemensamma_analysbrister
    p,t=med_post(fall);v=m.GemensamVerksamhetspost(id='prov',slag='erfarenhet',text='Syntetisk gemensam erfarenhet',
        status='bekraftad',forfattare='Syntetisk',belagg=p.gemensamma_sarbarhetsprovningar[0].belagg)
    p=p.model_copy(update={'gemensamma_verksamhetsposter':(v,)})
    p=m.Analyspaket.model_validate(p.model_dump(mode='json'))
    assert isinstance(gemensamma_analysbrister(fall.rb,fall.profil,fall.bedomning,p),tuple)


def test_tackningsformular_oppnar_ratt_sparad_riskled(fall):
    from riskanalys.intag.gemensamvy import tackningsformular
    p,t,prov=provfall(fall);a=p.tjanster[0]
    kvar=prov.model_copy(update={'riskled':'kvarstaende','motivering':'Unik sparad prövning av kvarstående risk och kontrollens räckvidd.'})
    p=p.model_copy(update={'tjanster':(a.model_copy(update={'tackningsprovningar':(prov,kvar)}),)})
    html=tackningsformular(fall.rb,p,t,'/','csrf','revision',{'ursprung':['gemensam'],'post':['prov'],'hot':['H-03'],'dimension':['pt'],'riskled':['kvarstaende']})
    assert kvar.motivering in html and '<option value="kvarstaende" selected>' in html
