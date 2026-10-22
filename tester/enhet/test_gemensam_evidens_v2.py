from tester.enhet.test_riktning_v2 import fall,med_post
from riskanalys.analys import modeller as m


def test_manuellt_riktningsval_kraver_registrerade_belagg(fall):
    from riskanalys.analys.provning_v2 import gemensamma_analysbrister
    p,t=med_post(fall,stallning='galler_annorlunda');a=p.tjanster[0]
    app=a.sarbarhetstillampningar[0].model_copy(update={'riktningsval':m.Riktningsval(riktning='lagre',motivering='Syntetiskt påstående',belagg=('FINNS-INTE',))})
    p=p.model_copy(update={'tjanster':(a.model_copy(update={'sarbarhetstillampningar':(app,)}),)})
    assert any('riktningsval' in x and 'belägg' in x for x in gemensamma_analysbrister(fall.rb,fall.profil,fall.bedomning,p))


def test_gemensamma_profilfalt_maste_vara_bekraftade(fall):
    from riskanalys.analys.provning_v2 import gemensamma_analysbrister
    p,t=med_post(fall);g=p.gemensamma_sarbarhetsprovningar[0].model_copy(update={'profilfalt':('P-BESK.ovrigt',)})
    p=p.model_copy(update={'gemensamma_sarbarhetsprovningar':(g,)})
    profil=fall.profil.model_copy(update={'uppgifter':{id:u for id,u in fall.profil.uppgifter.items() if id!='P-BESK.ovrigt'}})
    assert any('P-BESK.ovrigt' in x and 'bekräftat' in x for x in gemensamma_analysbrister(fall.rb,profil,fall.bedomning,p))


def test_plus_ett_beraknas_fore_befintliga_golv_och_tak(fall):
    from riskanalys.bedomning.scenarier import _scenario
    from riskanalys.analys.referens import referensniva
    t=next(t for t in fall.bedomning.tjanster if t.erbjuds);kat=fall.rb.tjanster[t.tjanst].model_copy(update={'grund_sannolikhet':'låg','grund_konsekvens':'allvarlig'})
    hot=fall.rb.hot['H-03'].model_copy(update={'niva':'medel'})
    neg=fall.rb.sarbarheter['S-KUND-01'];neg=neg.model_copy(update={'effekt':neg.effekt.model_copy(update={'sannolikhet':-2}),'hot':(hot.id,),'ersatter':()})
    rb=fall.rb.model_copy(update={'tjanster':{**fall.rb.tjanster,kat.id:kat},'hot':{**fall.rb.hot,hot.id:hot},'sarbarheter':{**fall.rb.sarbarheter,neg.id:neg}})
    s=_scenario(rb,kat,hot,'pt',(neg,),(),frozenset())
    extra=neg.model_copy(update={'id':'extra','effekt':neg.effekt.model_copy(update={'sannolikhet':1})})
    expected=_scenario(rb,kat,hot,'pt',(neg,extra),(),frozenset())
    t=t.model_copy(update={'scenarier':(s,),'kontroller':(),'status':'slutlig','okanda_uppgifter':()})
    assert referensniva(rb,fall.profil,t,hot.id,'pt','inneboende')==expected.risk
