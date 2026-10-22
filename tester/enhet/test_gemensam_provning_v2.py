import pytest
from riskanalys.analys import modeller as m
from tester.enhet.test_riktning_v2 import fall, med_post


def provfall(fall,dimension='pt',riskled='inneboende'):
    from riskanalys.analys.gemensam import tackningssumma
    p,t=med_post(fall,faktor=None,hot=('H-03',))
    from riskanalys.analys.gemensam import postsumma
    g=p.gemensamma_sarbarhetsprovningar[0].model_copy(update={'dimension':'pt'})
    old=p.tjanster[0];app=old.sarbarhetstillampningar[0].model_copy(update={'postsumma':postsumma(g)})
    p=p.model_copy(update={'gemensamma_sarbarhetsprovningar':(g,),'tjanster':(old.model_copy(update={'sarbarhetstillampningar':(app,)}),)})
    from riskanalys.analys.provning import effektiva_scenarier
    a=p.tjanster[0];scenarier,_=effektiva_scenarier(p,a);s=next(s for s in scenarier.values() if 'H-03' in s.hot)
    prov=m.Tackningsprovning(ursprung='gemensam',post='prov',hot='H-03',dimension=dimension,
        stallningstagande='tacks_av_scenario',lokalt_scenario=s.id,riskled=riskled,
        jamforelseniva='låg',referensmotivering='Gemensam orsak som redan omfattas av underlagets faktor; ingen dubbelräkning.',
        motivering='Den beskrivna mekanismen täcks av scenariots lokala händelseförlopp.',belagg=(p.belagg[0].id,),forfattare='Syntetisk sakkunnig')
    a=a.model_copy(update={'tackningsprovningar':(prov,)})
    p=p.model_copy(update={'tjanster':(a,)})
    prov=prov.model_copy(update={'visad_summa':tackningssumma(fall.rb,p,t,prov)})
    p=p.model_copy(update={'tjanster':(a.model_copy(update={'tackningsprovningar':(prov,)}),)})
    return p,t,prov

def test_egen_sarbarhet_tacks_av_ratt_scenario(fall):
    from riskanalys.analys.provning_v2 import tackningsbrister
    p,t,_=provfall(fall)
    assert not tackningsbrister(fall.rb,p,t)

@pytest.mark.parametrize('andring',[
    {'motivering':''},{'lokalt_scenario':'saknas'},{'stallningstagande':'oklar'},
    {'stallningstagande':'tacks_inte'},{'visad_summa':None},{'jamforelseniva':'mycket hög','riskled':'kvarstaende'},
    {'belagg':()},{'forfattare':None},{'referensmotivering':''}])
def test_ogiltig_tackning_sparrar(fall,andring):
    from riskanalys.analys.provning_v2 import tackningsbrister
    p,t,prov=provfall(fall);a=p.tjanster[0]
    from riskanalys.analys.gemensam import tackningssumma
    n=prov.model_copy(update=andring)
    p=p.model_copy(update={'tjanster':(a.model_copy(update={'tackningsprovningar':(n,)}),)})
    if 'visad_summa' not in andring:
        n=n.model_copy(update={'visad_summa':tackningssumma(fall.rb,p,t,n)})
        p=p.model_copy(update={'tjanster':(a.model_copy(update={'tackningsprovningar':(n,)}),)})
    assert tackningsbrister(fall.rb,p,t)

def test_andrad_post_gor_tackning_inaktuell(fall):
    from riskanalys.analys.provning_v2 import tackningsbrister
    p,t,_=provfall(fall)
    g=p.gemensamma_sarbarhetsprovningar[0].model_copy(update={'beskrivning':'Ändrad mekanism'})
    assert tackningsbrister(fall.rb,p.model_copy(update={'gemensamma_sarbarhetsprovningar':(g,)}),t)

def test_hog_pt_niva_tacker_inte_tf(fall):
    from riskanalys.analys.provning_v2 import tackningsbrister
    p,t,_=provfall(fall,dimension='tf')
    assert tackningsbrister(fall.rb,p,t)
