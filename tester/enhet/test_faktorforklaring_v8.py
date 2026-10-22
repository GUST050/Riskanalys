from dataclasses import replace
from tester.enhet.test_arb_v8 import v8fall, bygg


def test_gemensamma_definitioner_begransas_till_aktiverade_faktorer_i_erbjudna_tjanster(v8fall):
    from riskanalys.dokument.gemensamt_v8 import gemensamma_faktormekanismer
    f,_=v8fall
    ids={id for t in f.bedomning.tjanster if t.erbjuds is True for s in t.scenarier for id in s.sarbarheter}
    poster=gemensamma_faktormekanismer(f.regelbas,f.bedomning)
    assert len(poster)==len(ids)>0
    for id in ids:
        s=f.regelbas.sarbarheter[id]
        post=next(p for p in poster if id in p.referenser)
        assert (s.metodmotivering or s.beskrivning) in post.text
        assert set(s.kallor)<=set(post.referenser)
        hot={sc.hot for t in f.bedomning.tjanster if t.erbjuds is True for sc in t.scenarier if id in sc.sarbarheter}
        assert all(f.regelbas.hot[h].namn in post.text for h in hot)
    assert not gemensamma_faktormekanismer(f.regelbas,f.bedomning.model_copy(update={'tjanster':tuple(t.model_copy(update={'erbjuds':False}) for t in f.bedomning.tjanster)}))


def test_faktorinledning_skrivs_en_gang_och_lokala_skal_hanvisar_till_sakprovningen(v8fall):
    from riskanalys.dokument.nivamotivering_v8 import lokala_faktorskal
    f,r=v8fall;d=bygg(f,r)
    text=' '.join(s.text for a in d.avsnitt for s in a.stycken)
    assert text.count('Aktivering i motorunderlaget är inte i sig bekräftad exponering.')==1
    t=next(t for t in f.bedomning.tjanster if t.erbjuds is True)
    s=' '.join(s.text for s in lokala_faktorskal(f.regelbas,f.profil,f.analys,t))
    assert 'sårbarhetsprövningen' in s and 'belägg' in s
    assert 'H-03/PT' not in s and 'S-ARB-18: relevant' not in s


def test_historiska_resultat_och_samma_namn_bevarar_id(v8fall):
    from riskanalys.dokument.gemensamt_v8 import gemensamma_faktormekanismer
    f,_=v8fall
    t=next(t for t in f.bedomning.tjanster if t.erbjuds is True)
    ids=tuple(f.regelbas.sarbarheter)[:2]
    b=f.bedomning.model_copy(update={'tjanster':(t.model_copy(update={'scenarier':(),'tillampade_sarbarheter':ids}),)})
    rb=f.regelbas.model_copy(update={'sarbarheter':{**f.regelbas.sarbarheter,**{id:f.regelbas.sarbarheter[id].model_copy(update={'namn':'Samma namn'}) for id in ids}}})
    assert len(gemensamma_faktormekanismer(rb,b))==2


def test_gruppens_original_och_bindning_finns_i_ratt_tjanst(v8fall):
    from riskanalys.profil.modeller import Kombinationsgrupp
    from riskanalys.dokument.ursprung_v8 import bygg_ursprungskarta,los_pointer
    f,r=v8fall
    t=next(t for t in f.bedomning.tjanster if t.erbjuds is True)
    u=f.profil.uppgifter['P-KUND.antal_aktiva']
    g=Kombinationsgrupp(id='atta',tjanst=t.tjanst,population='uppdrag',avgransning='Samma uppdrag under perioden',
        beskrivning='Åtta uppdrag med båda egenskaperna {roll:FfR}.',sarbarheter=tuple(f.regelbas.tjanster[t.tjanst].sarbarheter[:2]),antal=u.model_copy(update={'varde':8}),bas=u.model_copy(update={'varde':100}))
    f=replace(f,profil=f.profil.model_copy(update={'kombinationsgrupper':(g,)}))
    d=bygg(f,r)
    a=next(a for a in d.avsnitt if a.id.startswith('D-ARB.6.') and any('LOKAL-GRUPP:atta' in s.referenser for s in a.stycken))
    assert g.beskrivning in ' '.join(s.text for s in a.stycken)
    karta=bygg_ursprungskarta(d,f.regelbas,f.profil,f.bedomning,r,__import__('riskanalys.drift.historik',fromlist=['Historik']).Historik(),f.analys)
    assert any(i['kalla']=='profil' and i['pointer']=='/kombinationsgrupper/0' for p in karta for i in p['ingangar'])
    assert not any('Åtta uppdrag' in s.text for b in d.avsnitt if b.id.startswith('D-ARB.6.') and b.id!=a.id for s in b.stycken)
