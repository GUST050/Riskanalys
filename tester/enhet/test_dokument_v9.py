"""R4: V9 prövar både originalanalysen och exakt återbyggd presentation."""
import pytest
from tester.fixturer.resultatrapport import resultatfall
from tester.enhet.test_resultatrapport_v9 import bygg


def fynd(f,b,**kw):
    from riskanalys.granskning.dokument_v9 import resultatfynd_v9
    return resultatfynd_v9(f.regelbas,f.profil,f.bedomning,f.resultat,f.historik,
        analys=f.analys,bygge=b,dokument=kw.get('dokument',b.dokument))


def test_v9_granskas_med_v8_skrivresultat(resultatfall):
    from riskanalys.granskning.kontroller import granska
    from riskanalys.regelverk.urval import valj
    f=resultatfall;b=bygg(f)
    posts=granska(f.regelbas,valj(f.regelbas,f.bedomning.regelpaket,f.bedomning.datum,f.bedomning.lan),f.profil,f.bedomning,b.dokument,f.historik,f.bedomning.datum,skrivresultat=f.resultat,analys=f.analys,bygge=b)
    assert not any('inte finns i regelbasen' in x.beskrivning or 'versionsbundna skrivdelar saknas' in x.beskrivning for x in posts)
    assert any(x.allvar=='blockerande' for x in posts) # provets verkliga analysbrister består


@pytest.mark.parametrize('id',['D-ARB.R2','D-ARB.R4','D-ARB.R5.1','D-ARB.R6','D-ARB.6.1'])
def test_niva_eller_atgardsstatus_som_avviker_ger_fynd(resultatfall,id):
    f=resultatfall;b=bygg(f);a=b.dokument.avsnitt_med_id()[id]
    a=a.model_copy(update={'stycken':(*a.stycken,a.stycken[0].model_copy(update={'text':'Falskt ändrat utfall: låg risk.'}))})
    d=b.dokument.model_copy(update={'avsnitt':tuple(a if x.id==id else x for x in b.dokument.avsnitt)})
    assert any(x['allvar']=='blockerande' and x['avsnitt']==id for x in fynd(f,b,dokument=d))


def test_utelamnat_tf_eller_egen_sarbarhet_ger_fynd(resultatfall):
    f=resultatfall;b=bygg(f)
    d=b.dokument.model_copy(update={'avsnitt':tuple(x for x in b.dokument.avsnitt if x.id!='D-ARB.R4')})
    assert any(x['avsnitt']=='D-ARB.R4' for x in fynd(f,b,dokument=d))


def test_trasig_eller_fel_typad_pointer_ger_fynd(resultatfall):
    f=resultatfall;b=bygg(f);p=b.underlag.poster[0];r=p.kallor[0].model_copy(update={'pointer':'/saknas'})
    p=p.model_copy(update={'kallor':(r,)})
    b=b.model_copy(update={'underlag':b.underlag.model_copy(update={'poster':(p,*b.underlag.poster[1:])})})
    assert any('pointer' in x['beskrivning'].lower() or 'käll' in x['beskrivning'].lower() for x in fynd(f,b))


def test_matris_med_borttappad_tjanstemedlem_ger_fynd(resultatfall):
    f=resultatfall;b=bygg(f);row=b.underlag.matris[0].model_copy(update={'celler':b.underlag.matris[0].celler[1:]})
    b=b.model_copy(update={'underlag':b.underlag.model_copy(update={'matris':(row,*b.underlag.matris[1:])})})
    assert any(x['allvar']=='blockerande' and 'urval' in x['beskrivning'].lower() for x in fynd(f,b))


def test_kravkartans_gallande_element_har_r_sammanfattning_och_analysplats(resultatfall):
    from riskanalys.granskning.dokument_v9 import KRAVKARTA
    from riskanalys.dokument.omfattning import krav_for_dokument,dokumentmal
    from riskanalys.regelverk.urval import valj
    f=resultatfall;b=bygg(f);ids=tuple(b.dokument.avsnitt_med_id())
    u=valj(f.regelbas,f.bedomning.regelpaket,f.bedomning.datum,f.bedomning.lan)
    for k in krav_for_dokument(f.regelbas,u,f.profil,'D-ARB'):
        for a in dokumentmal(k.krav,'D-ARB'):
            assert any(x==a or x.startswith(a+'.') for x in ids),k.krav.id
            assert a in KRAVKARTA,k.krav.id
            assert all(any(x==r or x.startswith(r+'.') for x in ids) for r in KRAVKARTA[a])
    assert all(k.kallor for k in b.konstruktioner)


def test_b09_b10_b15_provas_i_analysen_och_sammanfattas(resultatfall):
    f=resultatfall;b=bygg(f)
    text=' '.join(s.text for a in b.dokument.avsnitt if a.id.startswith('D-ARB.R') for s in a.stycken)
    assert f.analys.tjanster[0].erfarenhetsprovning in text
    assert f.analys.tjanster[0].pt_motivering in text
    assert 'TF' in text and 'sannolikhet' in text.lower() and 'konsekvens' in text.lower()


def test_obelagd_reduktion_och_otackt_tf_sparrar_som_forut(resultatfall):
    from riskanalys.granskning.kontroller import granska
    from riskanalys.regelverk.urval import valj
    f=resultatfall;b=bygg(f);u=valj(f.regelbas,f.bedomning.regelpaket,f.bedomning.datum,f.bedomning.lan)
    args=(f.regelbas,u,f.profil,f.bedomning)
    kw=dict(skrivresultat=f.resultat,analys=f.analys)
    v8=granska(*args,b.analysdokument,f.historik,f.bedomning.datum,**kw)
    v9=granska(*args,b.dokument,f.historik,f.bedomning.datum,bygge=b,**kw)
    assert [x.model_dump() for x in v9[:len(v8)]]==[x.model_dump() for x in v8]
    assert any('kontroll' in x.beskrivning.lower() for x in v8 if x.allvar=='blockerande')
