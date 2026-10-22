from tester.enhet.test_riktning_v2 import fall,med_post
from tester.enhet.test_gemensam_provning_v2 import provfall
from riskanalys.analys import modeller as m
from riskanalys.analys.gemensam import postsumma,tackningssumma


def test_explicit_hotkoppling_galler_hela_posten_inte_varje_korsprodukt(fall):
    from riskanalys.analys.riktning import harled_riktningar
    p,t=med_post(fall,'S-KUND-01',hot=('H-03',),kopplingar=(m.Hotanknytning(hot='H-03',dimension='tf'),))
    g=p.gemensamma_sarbarhetsprovningar[0].model_copy(update={'sarbarheter':('S-KUND-01','S-KUND-02')})
    a=p.tjanster[0];app=a.sarbarhetstillampningar[0].model_copy(update={'postsumma':postsumma(g)})
    p=p.model_copy(update={'gemensamma_sarbarhetsprovningar':(g,),'tjanster':(a.model_copy(update={'sarbarhetstillampningar':(app,)}),)})
    rows=harled_riktningar(fall.rb,fall.profil,p,t)
    assert not any(r.riktning=='mojlig_underskattning' for r in rows)


def test_egen_sarbarhets_lokala_tf_ansprak_kraver_egen_tackning(fall):
    from riskanalys.analys.provning_v2 import egna_ansprak,tackningsbrister
    p,t,prov=provfall(fall);a=p.tjanster[0]
    app=a.sarbarhetstillampningar[0].model_copy(update={'hotkopplingar':(m.Hotanknytning(hot='H-03',dimension='tf'),)})
    a=a.model_copy(update={'sarbarhetstillampningar':(app,)})
    p=p.model_copy(update={'tjanster':(a,)})
    prov=prov.model_copy(update={'visad_summa':tackningssumma(fall.rb,p,t,prov)})
    p=p.model_copy(update={'tjanster':(a.model_copy(update={'tackningsprovningar':(prov,)}),)})
    assert ('gemensam','prov','H-03','tf') in egna_ansprak(fall.rb,p,t)
    assert any('tf' in x and 'saknar' in x for x in tackningsbrister(fall.rb,p,t))


def test_beror_inte_med_uttryckligt_riskansprak_ar_motstridigt(fall):
    from riskanalys.analys.riktning import harled_riktningar
    p,t=med_post(fall,'S-KUND-02','beror_inte',kopplingar=(m.Hotanknytning(hot='H-03',dimension='tf'),))
    assert any(r.riktning=='oklar' for r in harled_riktningar(fall.rb,fall.profil,p,t))


def test_aldre_analys_for_ej_erbjuden_tjanst_kraver_inte_tillampning(fall):
    from riskanalys.analys.provning_v2 import gemensamma_analysbrister
    from riskanalys.bedomning.motor import bedom
    from riskanalys.regelverk.urval import valj
    p,t=med_post(fall);kat=fall.rb.tjanster[t.tjanst];upp=dict(fall.profil.uppgifter)
    upp[kat.erbjuds_falt]=upp[kat.erbjuds_falt].model_copy(update={'varde':False})
    profil=fall.profil.model_copy(update={'uppgifter':upp})
    b=bedom(fall.rb,valj(fall.rb,profil.byra.regelpaket,profil.byra.datum,profil.byra.lan),profil)
    a=p.tjanster[0].model_copy(update={'sarbarhetstillampningar':()})
    p=p.model_copy(update={'tjanster':(a,)})
    fel=gemensamma_analysbrister(fall.rb,profil,b,p)
    assert not any(x.startswith((t.tjanst+':',t.tjanst+'/')) for x in fel)
