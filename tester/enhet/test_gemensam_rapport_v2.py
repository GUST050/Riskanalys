from dataclasses import replace
import pytest
from tester.enhet.test_arb_v8 import v8fall,bygg,texter
from riskanalys.analys.gemensam import forifyll_gemensamt,postsumma


def schema2(f):
    p=forifyll_gemensamt(f.regelbas,f.analys)
    g=p.gemensamma_sarbarhetsprovningar[0].model_copy(update={
        'beskrivning':'Gemensam unik mekanism för fryst syntetiskt rapportprov',
        'motivering':'Det gemensamma förhållandet påverkar underlagens tillförlitlighet.',
        'belagg':(p.belagg[0].id,),'status':'bekraftad','relevans':'relevant','forfattare':'Syntetisk'})
    p=p.model_copy(update={'gemensamma_sarbarhetsprovningar':(g,*p.gemensamma_sarbarhetsprovningar[1:])})
    ts=[]
    for t in p.tjanster:
        appar=tuple(x.model_copy(update={'postsumma':postsumma(g),'bekraftad':True}) if x.post==g.id else x for x in t.sarbarhetstillampningar)
        ts.append(t.model_copy(update={'sarbarhetstillampningar':appar}))
    return replace(f,analys=p.model_copy(update={'tjanster':tuple(ts)}))


def test_gemensam_text_skrivs_en_gang_och_tjanster_hanvisar(v8fall):
    f,r=v8fall;f=schema2(f);fore=f.analys.model_dump_json();d=bygg(f,r)
    gem=d.avsnitt_med_id()['D-ARB.5'];text=f.analys.gemensamma_sarbarhetsprovningar[0].beskrivning
    assert texter(gem).count(text)==1
    for a in d.avsnitt:
        if a.id.startswith('D-ARB.6.'):
            assert text not in texter(a)
            assert 'Gemensamt faktaunderlag' in texter(a)
    assert f.analys.model_dump_json()==fore


def test_b1_bevarar_alla_nya_original_och_referensmotivering(v8fall):
    from riskanalys.dokument.radata_v8 import fria_analysfalt
    f,r=v8fall;f=schema2(f);d=bygg(f,r);b1=texter(d.avsnitt_med_id()['D-ARB.B1'])
    nya=[x for x in fria_analysfalt(f.analys) if x.sokvag.startswith('/gemensamma_sarbarhetsprovningar')]
    assert nya
    assert all(x.text in b1 for x in nya)


def test_ny_rapport_aterbyggs_och_fanger_andrad_tillampning(v8fall):
    from riskanalys.granskning.dokument_v8 import analysfynd_v8
    from riskanalys.drift.historik import Historik
    f,r=v8fall;f=schema2(f);d=bygg(f,r);p=f.analys;a=p.tjanster[0]
    app=a.sarbarhetstillampningar[0].model_copy(update={'stallningstagande':'beror_inte','motivering':'Belagd lokal avvikelse i just denna tjänst','belagg':(p.belagg[0].id,)})
    a=a.model_copy(update={'sarbarhetstillampningar':(app,*a.sarbarhetstillampningar[1:])})
    p=p.model_copy(update={'tjanster':(a,*p.tjanster[1:])})
    fynd=analysfynd_v8(f.regelbas,f.bedomning,f.profil,d,Historik(),r,analys=p)
    assert any('avviker från den frysta analysen' in x['beskrivning'] for x in fynd)



def test_schema_tvas_proveniens_pekar_pa_lagrade_kallor(v8fall):
    from riskanalys.dokument.ursprung_v8 import bygg_ursprungskarta,los_pointer
    from riskanalys.drift.historik import Historik
    f,r=v8fall;f=schema2(f);d=bygg(f,r)
    karta=bygg_ursprungskarta(d,f.regelbas,f.profil,f.bedomning,r,Historik(),f.analys)
    data={'analys':f.analys.model_dump(mode='json'),'profil':f.profil.model_dump(mode='json'),'bedomning':f.bedomning.model_dump(mode='json'),
          'regelbas':f.regelbas.model_dump(mode='json'),'historik':Historik().model_dump(mode='json'),'resultat':{k:v.model_dump(mode='json') for k,v in r.items()}}
    for post in karta:
        for ing in post['ingangar']:los_pointer(data[ing['kalla']],ing['pointer'])
    assert any(i['pointer'].startswith('/gemensamma_sarbarhetsprovningar/') for x in karta for i in x['ingangar'])


def test_d9_underlaget_samlar_upplysningar_utan_att_besluta_metod(v8fall):
    from riskanalys.dokument.gemensam_provning_v8 import d9_upplysningar
    from riskanalys.bedomning.motor import bedom
    from riskanalys.regelverk.urval import valj
    from riskanalys.profil.lagring import profilrevision
    f,_=v8fall;f=schema2(f);upp=dict(f.profil.uppgifter)
    upp['P-KUND.antal_kontant']=upp['P-KUND.antal_kontant'].model_copy(update={'varde':1})
    from riskanalys.profil.omfattning import harled_andelar
    profil=harled_andelar(f.profil.model_copy(update={'uppgifter':upp}),f.regelbas)
    b=bedom(f.regelbas,valj(f.regelbas,profil.byra.regelpaket,profil.byra.datum,profil.byra.lan),profil)
    p=f.analys.model_copy(update={'bindning':f.analys.bindning.model_copy(update={'profilrevision':profilrevision(profil)})})
    text='\n'.join(x.text for x in d9_upplysningar(f.regelbas,profil,p,b))
    assert 'S-KUND-02' in text and 'P-KUND.andel_kontant' in text and 'D9 C' in text
    assert 'inget beslutat metodfel' in text and '0.1' in text


def test_tillampningsrapporten_anvander_lasbara_svenska_statusar(v8fall):
    from riskanalys.dokument.gemensam_provning_v8 import tjanstens_tillampningsstycken
    f,_=v8fall;f=schema2(f);p=f.analys;a=p.tjanster[0]
    app=a.sarbarhetstillampningar[0].model_copy(update={'stallningstagande':'beror_inte','motivering':'Belagd lokal avgränsning','belagg':(p.belagg[0].id,)})
    p=p.model_copy(update={'tjanster':(a.model_copy(update={'sarbarhetstillampningar':(app,*a.sarbarhetstillampningar[1:])}),*p.tjanster[1:])})
    t=next(t for t in f.bedomning.tjanster if t.tjanst==a.tjanst)
    text='\n'.join(s.text for s in tjanstens_tillampningsstycken(f.regelbas,f.profil,p,t))
    assert 'berör inte tjänsten' in text and 'beror_inte' not in text and 'bekraftad' not in text
