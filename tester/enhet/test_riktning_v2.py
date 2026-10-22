"""Riktning följer verkligt villkor och scenario, aldrig frånvaro ensam."""
from dataclasses import replace
import pytest
from riskanalys.analys import modeller as m
from riskanalys.analys.gemensam import postsumma
from tester.fixturer.gemensam_analys import bygg_gemensamt_fall

@pytest.fixture(scope='module')
def fall(regelbas_v1,tmp_path_factory):
    return bygg_gemensamt_fall(regelbas_v1,tmp_path_factory.mktemp('gemensam'))

def med_post(fall,faktor='S-KUND-02',stallning='galler',hot=('H-03',),kopplingar=()):
    g=m.GemensamSarbarhetsprovning(id='prov',omrade='kund',sarbarheter=(faktor,) if faktor else (),
        hot=hot,dimension='bada',relevans='relevant',status='bekraftad',
        beskrivning='Syntetisk belagd sårbarhetsmekanism',motivering='Påverkar granskningen av underlag',belagg=(fall.paket.belagg[0].id,),forfattare='Syntetisk')
    app=m.Sarbarhetstillampning(post=g.id,stallningstagande=stallning,postsumma=postsumma(g),bekraftad=True,
        motivering='Syntetisk lokal tillämpning',belagg=g.belagg,hotkopplingar=kopplingar)
    t=fall.paket.tjanster[0].model_copy(update={'sarbarhetstillampningar':(app,)})
    p=fall.paket.model_copy(update={'gemensamma_sarbarhetsprovningar':(g,),'tjanster':(t,)})
    b=next(b for b in fall.bedomning.tjanster if b.tjanst==t.tjanst and b.erbjuds)
    return p,b

def profilvarde(f, id, varde):
    upp=dict(f.profil.uppgifter)
    upp[id]=upp[id].model_copy(update={'varde':varde})
    return f.profil.model_copy(update={'uppgifter':upp})

def test_falskt_troskelvillkor_ger_upplysning(fall):
    from riskanalys.analys.riktning import harled_riktningar
    from riskanalys.bedomning.motor import bedom_tjanst
    p,t=med_post(fall);profil=profilvarde(fall,'P-KUND.andel_kontant',.05)
    # Samma källa som motorn använder, inklusive kompatibilitetsvyn.
    profil=profil.model_copy(update={'uppgifter':{k:v for k,v in profil.uppgifter.items() if k!='P-KUND.antal_kontant'}})
    t=bedom_tjanst(fall.rb,fall.rb.tjanster[t.tjanst],profil)
    fore=t.model_dump_json()
    r=harled_riktningar(fall.rb,profil,p,t)
    assert any(x.riktning=='under_troskel' for x in r)
    assert not any(x.riktning=='mojlig_underskattning' for x in r)
    assert t.model_dump_json()==fore

def test_okant_villkor_ar_inte_under_troskel(fall):
    from riskanalys.analys.riktning import harled_riktningar
    p,t=med_post(fall)
    profil=fall.profil.model_copy(update={'uppgifter':{k:v for k,v in fall.profil.uppgifter.items() if k not in ('P-KUND.andel_kontant','P-KUND.antal_kontant')}})
    r=harled_riktningar(fall.rb,profil,p,t)
    assert any(x.riktning=='oklar' for x in r)
    assert not any(x.riktning=='under_troskel' for x in r)

def test_bada_skapar_inte_saknad_tf_koppling(fall):
    from riskanalys.analys.riktning import harled_riktningar
    p,t=med_post(fall,'S-KUND-01',hot=('H-03','H-TF-01'))
    assert not any(x.riktning=='mojlig_underskattning' for x in harled_riktningar(fall.rb,fall.profil,p,t))
    a=p.tjanster[0];app=a.sarbarhetstillampningar[0].model_copy(update={'hotkopplingar':(m.Hotanknytning(hot='H-TF-01',dimension='tf'),)})
    p=p.model_copy(update={'tjanster':(a.model_copy(update={'sarbarhetstillampningar':(app,)}),)})
    assert any(x.riktning=='mojlig_underskattning' and x.dimension=='tf' for x in harled_riktningar(fall.rb,fall.profil,p,t))

def test_beror_inte_aktiv_faktor_ar_lagre_och_negativ_ar_oklar(fall):
    from riskanalys.analys.riktning import harled_riktningar
    p,t=med_post(fall,'S-KUND-01','beror_inte')
    r=harled_riktningar(fall.rb,fall.profil,p,t)
    assert any(x.riktning=='lagre' and x.kalla=='harledd' for x in r)
    faktorer=dict(fall.rb.sarbarheter);s=faktorer['S-KUND-01']
    faktorer[s.id]=s.model_copy(update={'effekt':s.effekt.model_copy(update={'sannolikhet':-1})})
    rb=fall.rb.model_copy(update={'sarbarheter':faktorer})
    assert any(x.riktning=='oklar' for x in harled_riktningar(rb,fall.profil,p,t))


def test_ersatt_faktor_ar_inte_modellucka(fall):
    from riskanalys.analys.riktning import harled_riktningar
    from riskanalys.bedomning.motor import bedom_tjanst
    p,t=med_post(fall,'S-KUND-01')
    faktorer=dict(fall.rb.sarbarheter)
    original=faktorer['S-KUND-01']
    ersattare=original.model_copy(update={'id':'S-PROV-ERSATTARE','ersatter':(original.id,)})
    faktorer[ersattare.id]=ersattare
    kats=dict(fall.rb.tjanster);kat=kats[t.tjanst]
    kats[t.tjanst]=kat.model_copy(update={'sarbarheter':(*kat.sarbarheter,ersattare.id)})
    rb=fall.rb.model_copy(update={'sarbarheter':faktorer,'tjanster':kats})
    b=bedom_tjanst(rb,kats[t.tjanst],fall.profil)
    r=harled_riktningar(rb,fall.profil,p,b)
    assert any(x.riktning=='ersatt_av_faktor' and x.ersatt_av==ersattare.id for x in r)
    assert not any(x.riktning=='mojlig_underskattning' for x in r)


def test_manuell_riktning_far_inte_skickas_in_i_mekaniskt_fall():
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        m.Sarbarhetstillampning(post='p',postsumma='sha256:'+'0'*64,stallningstagande='beror_inte',riktningsval=m.Riktningsval(riktning='lagre'))
