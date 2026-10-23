"""Resultatrapporten återanvänder hela motiveringar och delar gemensamma kedjor."""
import pytest
from tester.fixturer.resultatrapport import resultatfall


def bygg(f, analys=None):
    from riskanalys.dokument.arb_v9 import bygg_resultatpaket_v9
    return bygg_resultatpaket_v9(f.regelbas,f.profil,f.bedomning,f.resultat,f.historik,
                                analys=analys or f.analys)


def text(d):
    return '\n'.join([*(s.text for a in d.avsnitt for s in a.stycken),
                      *(c.text for a in d.avsnitt for t in a.tabeller for r in t.rader for c in r.celler)])


def test_r4_matris_visar_gemensam_kedja_en_gang_for_fyra_tjanster(resultatfall):
    d = bygg(resultatfall).dokument
    r4 = d.avsnitt_med_id()['D-ARB.R4']
    assert all(len(t.kolumner)<=5 for t in r4.tabeller)
    assert sum('H-01' in r.celler[0].text and 'PT' in r.celler[0].text
               for t in r4.tabeller for r in t.rader)==1
    row=next(r for t in r4.tabeller for r in t.rader if 'H-01' in r.celler[0].text and 'PT' in r.celler[0].text)
    assert [c.text.split('\n')[0].replace('*','').replace('†','') for c in row.celler[1:]] == ['hög → hög','hög → måttlig','hög → måttlig','hög → hög']


def test_r4_och_r5_tillsammans_tacker_varje_tjansts_hela_kedja(resultatfall):
    b=bygg(resultatfall)
    for row in b.underlag.matris:
        for c in row.celler:
            if c.medlemmar:
                a=next(a for a in b.dokument.avsnitt if a.id.startswith('D-ARB.R5.')
                       and c.tjanst in a.stycken[0].referenser)
                assert row.id in text(type('D',(),{'avsnitt':(a,)})())
    assert 'Sannolikhet' in text(b.dokument) and 'konsekvens' in text(b.dokument)


def test_r5_visar_egna_scenarier_och_avvikande_kontrollutfall(resultatfall):
    b=bygg(resultatfall)
    for a in b.dokument.avsnitt:
        if a.id.startswith('D-ARB.R5.'):
            assert 'H-TJ-' in text(type('D',(),{'avsnitt':(a,)})())
            assert 'Kontroll' in text(type('D',(),{'avsnitt':(a,)})())


def test_hela_pt_tf_motiveringen_stannar_i_r5_men_exponering_hanvisas_till_a(resultatfall):
    b=bygg(resultatfall)
    r5='\n'.join(s.text for a in b.dokument.avsnitt if a.id.startswith(('D-ARB.R4','D-ARB.R5.')) for s in a.stycken)
    for a in resultatfall.analys.tjanster:
        assert a.pt_motivering in r5 and a.tf_motivering in r5
        assert a.exponering not in r5
        assert a.exponering in text(b.analysdokument)
    assert 'Bilaga A' in r5


def test_flera_scenarier_som_var_for_sig_avgor_nivan_forklaras(resultatfall):
    assert 'var för sig' in text(bygg(resultatfall).dokument)


def test_r2_har_exakta_pt_och_tf_varden_utan_pahittad_tf_reduktion(resultatfall):
    b=bygg(resultatfall)
    rows=b.dokument.avsnitt_med_id()['D-ARB.R2'].tabeller[0].rader
    for r,t in zip(rows,(t for t in resultatfall.bedomning.tjanster if t.erbjuds),strict=True):
        assert [c.text for c in r.celler[1:4]]==[t.inneboende.risk,t.kvarstaende,t.terrorfinansiering.risk]
    assert 'ej beräknad' in text(b.dokument.avsnitt_med_id()['D-ARB.R4'].__class__ and
                                type('D',(),{'avsnitt':(b.dokument.avsnitt_med_id()['D-ARB.R4'],)})())


def test_atgardsmedlemmar_bevarar_status_och_ej_beslutad_prioritet(resultatfall):
    r6=bygg(resultatfall).dokument.avsnitt_med_id()['D-ARB.R6']
    v=text(type('D',(),{'avsnitt':(r6,)})())
    for a in resultatfall.analys.tjanster:
        for r in a.rutinatgarder:
            from riskanalys.dokument.resultattexter_v9 import etikett
            assert r.id in v and etikett(r.status) in v
    assert 'ej beslutad' in v


def test_lang_motivering_aterges_hel_utan_nytt_sammanfattningsfalt(resultatfall):
    f=resultatfall
    long='Detta är en lång fullständig riskmotivering. '*200
    a=f.analys.tjanster[0].model_copy(update={'pt_motivering':long})
    paket=f.analys.model_copy(update={'tjanster':(a,*f.analys.tjanster[1:])})
    d=bygg(f,paket).dokument
    assert long in text(d)


def test_fler_an_fyra_tjanster_delar_matrisen_utan_att_tappa_celler():
    from riskanalys.dokument.resultatrapport_v9 import kolumngrupper
    ids=tuple('T-'+str(i) for i in range(11))
    delar=kolumngrupper(ids)
    assert tuple(x for g in delar for x in g)==ids
    assert all(1<=len(g)<=4 for g in delar)


def test_tomt_utkast_med_v9_standard_byggs_som_v9_och_aldrig_v6(resultatfall,monkeypatch):
    from riskanalys.dokument import rapportversion, arb_v6
    from riskanalys.dokument.arb import bygg_arb
    monkeypatch.setattr(rapportversion,'AKTUELL_DOKUMENTVERSION',rapportversion.V9)
    def fel(*args,**kwargs):pytest.fail('Tomt V9-utkast föll till V6.')
    monkeypatch.setattr(arb_v6,'bygg_arb_v6',fel)
    f=resultatfall
    d=bygg_arb(f.regelbas,f.profil,f.bedomning,{},f.historik,analys=None)
    assert d.formatversion==rapportversion.V9
    assert '[VERIFIERA]' in text(d)


def test_egen_tf_sarbarhet_visar_dimension_och_hot_i_huvudrapport(resultatfall):
    from riskanalys.analys.modeller import GemensamSarbarhetsprovning
    f=resultatfall
    p=GemensamSarbarhetsprovning(id='ny-tf',omrade='verk',dimension='tf',hot=('H-TF-01',),
        beskrivning='Egen identifierad finansieringsrisk.',relevans='relevant',status='antagande')
    paket=f.analys.model_copy(update={'gemensamma_sarbarhetsprovningar':(*f.analys.gemensamma_sarbarhetsprovningar,p)})
    r4=bygg(f,paket).dokument.avsnitt_med_id()['D-ARB.R4']
    p=next(s for s in r4.stycken if 'Egen identifierad finansieringsrisk.' in s.text)
    assert 'TF' in p.text and 'H-TF-01' in p.text and 'antagande' in p.text


def test_eget_scenario_visar_handelseforlopp_inte_bara_hotnamn(resultatfall):
    b=bygg(resultatfall)
    for a in resultatfall.analys.tjanster:
        for s in a.scenarier:
            if any(h.startswith('H-TJ-') for h in s.hot):
                assert s.handelseforlopp in text(type('D',(),{'avsnitt':tuple(
                    x for x in b.dokument.avsnitt if x.id.startswith('D-ARB.R5.'))})())


@pytest.mark.parametrize('status,etikett',[('saknas','Saknas'),('ej_relevant','Ej relevant'),('okant','Okänt')])
def test_r4_visar_cellens_faktiska_status(resultatfall,status,etikett):
    from tester.fixturer.resultatrapport import underlag
    from riskanalys.dokument.resultatrapport_v9 import bygg_resultatavsnitt
    f=resultatfall;u=underlag(f)
    row=next(r for r in u.matris if r.hot=='H-01' and r.dimension=='pt')
    cell=row.celler[-1].model_copy(update={'status':status,'scenario':None,'medlemmar':()})
    changed=row.model_copy(update={'celler':(*row.celler[:-1],cell)})
    u=u.model_copy(update={'matris':tuple(changed if r.id==row.id else r for r in u.matris)})
    d=bygg_resultatavsnitt(f.regelbas,f.profil,f.bedomning,f.resultat,f.historik,analys=f.analys,underlag=u)
    r4=next(a for a in d if a.id=='D-ARB.R4')
    r=next(r for t in r4.tabeller for r in t.rader if 'H-01' in r.celler[0].text and 'PT' in r.celler[0].text)
    assert etikett in r.celler[-1].text


def test_ett_avgorande_scenario_per_dimension_far_inte_kallas_flera(resultatfall):
    from types import SimpleNamespace
    f=resultatfall;ts=[]
    for t in f.bedomning.tjanster:
        seen=set();sc=[]
        for s in t.scenarier:
            sc.append(s.model_copy(update={'avgorande':s.dimension not in seen}))
            seen.add(s.dimension)
        ts.append(t.model_copy(update={'scenarier':tuple(sc)}))
    nytt=SimpleNamespace(**(vars(f)|{'bedomning':f.bedomning.model_copy(update={'tjanster':tuple(ts)})}))
    d=bygg(nytt).dokument
    assert not any('var för sig' in s.text for a in d.avsnitt if a.id.startswith('D-ARB.R5.') for s in a.stycken)
