"""Reproduktion av Claudes PDF-fynd på f653eea; bara syntetiska data."""
import pytest
from tester.fixturer.resultatrapport import resultatfall
from tester.enhet.test_resultatrapport_v9 import bygg, text


GAMLA = (
    'Motorns PT-utfall: hög; kvarstående hög. Lokal rimlighetsprövning återstår.',
    'Motorns TF-utfall: mycket hög. Separat lokal prövning återstår.',
)


@pytest.mark.parametrize('varde', GAMLA)
def test_gammal_oforandrad_standardmotivering_ar_inte_saktext(varde):
    from riskanalys.analys.provning import _saktext
    assert not _saktext(varde)


def test_nya_forifyllda_motiveringar_har_kompletteringsmarkor(resultatfall):
    from riskanalys.analys.utkast import forifyll_analys
    f=resultatfall
    p=forifyll_analys(f.regelbas,f.profil,f.bedomning,f.analys.bindning)
    assert all('[KOMPLETTERA:' in getattr(a,falt) for a in p.tjanster
               for falt in ('pt_motivering','tf_motivering'))


@pytest.mark.parametrize('falt,varde',tuple(zip(('pt_motivering','tf_motivering'), GAMLA)))
def test_orord_motivering_sparrar_analys_och_markerar_resultatrapport(resultatfall,falt,varde):
    from riskanalys.analys.provning import analysbrister
    f=resultatfall;a=f.analys.tjanster[0].model_copy(update={falt:varde})
    p=f.analys.model_copy(update={'tjanster':(a,*f.analys.tjanster[1:])})
    fel=analysbrister(f.regelbas,f.profil,f.bedomning,p)
    assert any(falt+' saknar ett färdigt svar' in s for s in fel)
    b=bygg(f,p)
    assert any(falt in x.kod and x.kallor[0].pointer.endswith('/'+falt) for x in b.underlag.brister)
    r5=next(x for x in b.dokument.avsnitt if x.id.startswith('D-ARB.R5.'))
    assert any('[KOMPLETTERA:' in s.text and varde in s.text for s in r5.stycken)


def test_matris_och_lokal_analys_markerar_varje_icke_godtagen_sankning(resultatfall):
    from riskanalys.analys.provning import ej_godtagna_sankningar
    f=resultatfall;b=bygg(f);r4=b.dokument.avsnitt_med_id()['D-ARB.R4'];antal=0
    for a in f.analys.tjanster:
        t=next(t for t in f.bedomning.tjanster if t.tjanst==a.tjanst)
        brister=ej_godtagna_sankningar(f.regelbas,f.profil,f.analys,a,t)
        antal+=len(brister)
        for brist in brister:
            row=next(r for r in b.underlag.matris if r.hot==brist.scenario.hot
                     and r.dimension=='pt' and any(c.tjanst==t.tjanst and c.scenario for c in r.celler))
            r5=next(x for x in b.dokument.avsnitt if x.id.startswith('D-ARB.R5.') and t.tjanst in x.stycken[0].referenser)
            markering='sänkning ej prövad lokalt' if brist.orsak=='oprovat' else 'sänkning ej godtagen lokalt'
            if row.id.startswith('R4-'):
                tr=next(r for tab in r4.tabeller for r in tab.rader if row.id+' ' in r.celler[0].text)
                ci=next(i for i,c in enumerate(row.celler) if c.tjanst==t.tjanst)+1
                assert markering in tr.celler[ci].text.lower()
            else:assert markering in ' '.join(s.text for s in r5.stycken).lower()
            orsak='lokal scenarioprövning' if brist.orsak=='oprovat' else 'positiv lokal prövning'
            assert any(brist.scenario.hot in s.text and 'inte godtagen' in s.text
                       and orsak in s.text for s in r5.stycken)
    assert antal>0


def test_godtagen_sankning_far_inte_markeras_oprovad():
    from riskanalys.dokument.resultatrapport_v9 import celltext
    from types import SimpleNamespace
    s=SimpleNamespace(risk='hög',kvarstaende='måttlig',avgorande=True)
    c=SimpleNamespace(scenario=s,medlemmar=(),status='beraknad')
    assert 'ej prövad' not in celltext(c,())
    assert 'ej godtagen' in celltext(c,('obelagd',))


def test_mandatfixturen_har_lokala_avvikelser_med_ratt_mekanism(regelbas_v1,tmp_path):
    from tester.fixturer.rapportlasprov import bygg_rapportlasprov
    from riskanalys.dokument.resultatunderlag_v9 import mekanism
    f=bygg_rapportlasprov(regelbas_v1,tmp_path,'med_betalningsmandat')
    a=next(a for a in f.analys.tjanster if a.tjanst=='T-RED-04')
    for g in f.analys.gemensamma_scenarier:
        for hot in g.hot:
            scen=mekanism(f.analys,a,hot)
            assert scen and all('kunden attesterar och verkställer samtliga betalningar' not in s.handelseforlopp.lower()
                                for s,_ in scen)
            assert any('byrån verkställer' in s.handelseforlopp.lower() for s,_ in scen)
    assert any(k.tillampning=='avviker' for k in a.scenariokopplingar)
    assert not any('rimlighetsprövning återstår' in t.pt_motivering for t in f.analys.tjanster)
    assert 'avsaknad av betalningsmandat' not in a.model_dump_json()
    assert 'även utan betalningsmandat' not in a.model_dump_json()


def test_r5_utan_delade_kedjor_har_ingen_tom_upprakning(resultatfall):
    f=resultatfall;a=f.analys.tjanster[0]
    egna=tuple(g.model_copy(update={'id':'egen:'+g.id,'motivering':'Denna tjänst har egen mekanism.'})
               for g in f.analys.gemensamma_scenarier)
    kop=tuple(k.model_copy(update={'tillampning':'avviker','lokal_scenario':'egen:'+k.scenario})
              for k in a.scenariokopplingar)
    a=a.model_copy(update={'scenarier':(*a.scenarier,*egna),'scenariokopplingar':kop})
    p=f.analys.model_copy(update={'tjanster':(a,*f.analys.tjanster[1:])})
    r5=next(x for x in bygg(f,p).dokument.avsnitt if x.id.startswith('D-ARB.R5.'))
    v=' '.join(s.text for s in r5.stycken)
    assert 'Gemensamma kedjor: .' not in v and 'egen mekanism' in v


def test_svenska_etiketter_kontrollnamn_och_rena_scenarioid(resultatfall):
    b=bygg(resultatfall);v=text(type('D',(),{'avsnitt':tuple(a for a in b.dokument.avsnitt if a.id.startswith('D-ARB.R'))})())
    assert 'bekraftad' not in v and 'foreslagen' not in v and 'oppet' not in v
    assert 'föreslagen' in v
    for row in b.underlag.matris:
        if sum(c.scenario is not None for c in row.celler)==1:assert row.id.startswith('R5-')
    for id in ('C-07','C-TJ-02'):
        assert resultatfall.regelbas.kontroller[id].namn+' ('+id+')' in v


def test_r1_slutsats_kommer_fran_utfallet_och_oppna_luckor(resultatfall):
    r1=bygg(resultatfall).dokument.avsnitt_med_id()['D-ARB.R1']
    v=' '.join(s.text for s in r1.stycken)
    assert '4 tjänster' in v and 'hög PT-risk' in v and 'mycket hög TF-risk' in v
    assert '4 öppna luckor' in v and 'sänker inte någon tjänsts' in v


def test_identiska_hela_tf_motiveringar_skrivs_en_gang_med_alla_kallor(resultatfall):
    b=bygg(resultatfall);ids=[]
    for i,a in enumerate(resultatfall.analys.tjanster):
        if a.tf_motivering==resultatfall.analys.tjanster[0].tf_motivering:ids.append(i)
    assert len(ids)>1
    huvud=tuple(a for a in b.dokument.avsnitt if a.id.startswith('D-ARB.R'))
    hits=[s for a in huvud for s in a.stycken if resultatfall.analys.tjanster[0].tf_motivering in s.text]
    assert len(hits)==1
    assert all('kalla:analys#/tjanster/'+str(i)+'/tf_motivering' in hits[0].referenser for i in ids)


def test_r6_dubbel_lucktext_visas_bara_en_gang(resultatfall):
    f=resultatfall;a=f.analys.tjanster[0];g=a.gap[0]
    a=a.model_copy(update={'gap':(g.model_copy(update={'motivering':g.beskrivning}),)})
    p=f.analys.model_copy(update={'tjanster':(a,*f.analys.tjanster[1:])})
    r6=bygg(f,p).dokument.avsnitt_med_id()['D-ARB.R6']
    v=text(type('D',(),{'avsnitt':(r6,)})())
    for a in p.tjanster:
        for g in a.gap:
            if g.beskrivning==g.motivering and g.status=='oppet':assert v.count(g.beskrivning)==1
