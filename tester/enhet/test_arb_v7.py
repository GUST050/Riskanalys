"""V7 behåller den lokala kedjan och versionsbundna äldre dokument."""
from datetime import date

import docx
import pytest

from riskanalys.dokument.arb_v6 import bygg_arb_v6
from riskanalys.dokument.delskrivning import skriv_tjanst
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.kallhanvisningar import utan_kallhanvisning
from riskanalys.dokument.matning import dokumentord
from riskanalys.dokument.skrivversion import V6, V7
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.drift.historik import Historik
from riskanalys.fel import RiskanalysFel
from tester.fixturer.analys_hela_kedjan import skapa_fall
from tester.fixturer.m2 import bygg_delsvar
from tester.enhet.test_arb_v6 import v6underlag  # noqa: F401


@pytest.fixture(scope='module')
def v7fall(regelbas_v1, tmp_path_factory):
    fall = skapa_fall(regelbas_v1, tmp_path_factory.mktemp('v7-normal'), variation=False)
    lev = Testleverantor(bygg_delsvar(fall.regelbas, fall.profil, fall.bedomning, formatversion=V7))
    resultat = {id: skriv_tjanst(lev, fall.regelbas, fall.profil, t, id, effort='medium',
        personnamn=(), spara=lambda *a: None, formatversion=V7)
        for id, t in tjanster_med_avsnitt(fall.bedomning)}
    assert len(lev.delanrop) == 4
    assert all(not d.mall for r in resultat.values() for d in r.delar)
    return fall, resultat


def bygg(v7fall, **kwargs):
    f, r = v7fall
    return bygg_arb_v6(f.regelbas, f.profil, f.bedomning, r, Historik(), analys=f.analys, **kwargs)


def test_v7_fyra_delar_kategorier_och_riktig_nivamotivering(v7fall):
    f, _ = v7fall
    d = bygg(v7fall)
    assert d.formatversion == V7
    for id, t in tjanster_med_avsnitt(f.bedomning):
        a = d.avsnitt_med_id()[id]
        assert [u.rubrik for u in a.underrubriker] == ['Analys', 'Scenarier', 'Lokal analys och slutsats', 'Risknivå och motivering']
        assert len({u.fore_stycke for u in a.underrubriker}) == 4
        tab = next(tab for tab in a.tabeller if tab.id.endswith('-motorscenarier'))
        assert len(tab.rader) == len(t.scenarier)
        assert all(c.proveniens == 'regelbas' for r in tab.rader for c in r.celler)
        assert not any(tab.id.endswith('-kategorier') for tab in a.tabeller)
        lokal = next(x for x in f.analys.tjanster if x.tjanst == t.tjanst)
        nivatext = ' '.join(s.text for s in a.stycken[a.underrubriker[-1].fore_stycke:])
        assert lokal.pt_motivering in nivatext and lokal.tf_motivering in nivatext
        assert all('2026-' not in c.text and lokal.samverkan not in c.text for rad in tab.rader for c in rad.celler)


def test_v7_normal_matning_utan_trunkering(v7fall):
    from riskanalys.dokument.rendering import synliga_texter
    f, r = v7fall
    d = bygg(v7fall)
    huvud = '\n'.join(s for a in d.avsnitt if a.id != 'D-ARB.B1' for s in synliga_texter(a))
    for t in f.analys.tjanster:
        for text in (t.samverkan, t.pt_motivering, t.tf_motivering, t.erfarenhetsprovning, t.slutsats):
            assert text in huvud
    for res in r.values():
        assert all(s.text in huvud for s in res.del_('analys').godkant_svar.stycken)
    matt = dokumentord(d, f.profil)
    print({'fall': 'V7-normal', **matt})


def test_v7_avvisar_blandning_och_ommarkning(v7fall):
    f, r = v7fall
    id = next(iter(r))
    blandat = {**r, id: r[id].model_copy(update={'formatversion': V6})}
    with pytest.raises(RiskanalysFel, match='format|identitet|Skriv'):
        bygg_arb_v6(f.regelbas, f.profil, f.bedomning, blandat, Historik(), analys=f.analys)
    with pytest.raises(RiskanalysFel, match='format|identitet|Skriv'):
        bygg(v7fall, formatversion=V6)


def test_v7_senare_nej_far_inte_ersattas_av_aldre_matchande_ja(v7fall):
    from riskanalys.faststallelse.sakgranskning import registrera_sakgranskning, galler_sakgranskning
    f, _ = v7fall
    d = bygg(v7fall)
    a = d.avsnitt[0]
    ja = registrera_sakgranskning((), d, f.profil, a.id, True, 'FfR', 'Syntetisk', date(2026, 10, 10), analysbindning='a')
    nej = registrera_sakgranskning(ja, d, f.profil, a.id, False, 'FfR', 'Syntetisk', date(2026, 10, 11), 'Fel', analysbindning='b')
    assert galler_sakgranskning(nej, a, f.profil, d, analysbindning='a') is None


def test_v7_word_och_b1_lankar(v7fall, tmp_path):
    from riskanalys.dokument.rendering import rendera_docx
    from docx.oxml.ns import qn
    f, _ = v7fall
    d = bygg(v7fall)
    word = docx.Document(rendera_docx(d, f.profil, 'UTKAST', tmp_path / 'v7.docx'))
    assert len(word.tables) == sum(len(a.tabeller) for a in d.avsnitt)
    lankar = word.element.xpath('.//w:tbl//w:hyperlink')
    mal = {x.get(qn('w:name')) for x in word.element.xpath('.//w:bookmarkStart')}
    assert lankar and all(x.get(qn('w:anchor')) in mal for x in lankar)


def test_v7_samordning_bevarar_en_faktisk_lokal_del(v7fall):
    from riskanalys.dokument.gemensam_analys import sammanfor_identisk_lokaltext
    from riskanalys.dokument.modeller import Avsnitt
    from riskanalys.dokument.tjanstavsnitt_v6 import lokaltext
    from riskanalys.dokument.tjanstavsnitt_v7 import bygg_tjanstavsnitt_v7
    from riskanalys.regelverk.granser import metodgransindex
    f, _ = v7fall
    text = lokaltext('Slutsats: Byråns handskrivna identiska bedömning av uppdraget och dess belagda insynsluckor står här.')
    avsnitt = [bygg_tjanstavsnitt_v7(f.regelbas, f.profil, t, None, id,
        gransindex=metodgransindex(f.regelbas), lokal=(text,)) for id, t in tjanster_med_avsnitt(f.bedomning)]
    nya, gemensamma, _ = sammanfor_identisk_lokaltext(avsnitt)
    assert any(text.text in s.text for s in gemensamma)
    for a in nya:
        Avsnitt.model_validate(a.model_dump())
        start, slut = [u.fore_stycke for u in a.underrubriker[-2:]]
        assert start < slut
        assert any('gemensamm' in s.text.lower() for s in a.stycken[start:slut])


def test_v7_modellen_avvisar_blandade_dokument(v7fall):
    from riskanalys.dokument.modeller import Dokument
    from pydantic import ValidationError
    d = bygg(v7fall)
    data = d.model_dump()
    data['avsnitt'][0]['formatversion'] = V6
    with pytest.raises(ValidationError, match='format'):
        Dokument.model_validate(data)


def test_v7_kallrackvidd_slas_upp_och_godtyckligt_prefix_avvisas(v7fall):
    from riskanalys.dokument.kallhanvisningar import bygg_kallregister
    from riskanalys.granskning.kontroller import _sparbarhet
    from riskanalys.dokument.modeller import Textstycke
    f, _ = v7fall
    rackvidd = next(r for k in f.regelbas.kontroller.values() for r in k.rackvidd)
    d = bygg(v7fall)
    a = d.avsnitt[0].model_copy(update={'stycken': (Textstycke(typ='analys', text='Källbunden kontrollräckvidd.', referenser=[rackvidd.id]),)})
    d = d.model_copy(update={'avsnitt': (a,)})
    assert not _sparbarhet(f.regelbas, d, f.analys)
    assert {h.kalla for h in rackvidd.kallhanvisningar} <= set(bygg_kallregister(d, f.regelbas))
    fel = a.model_copy(update={'stycken': (a.stycken[0].model_copy(update={'referenser': ['KR-GODTYCKLIG']}),)})
    assert any('KR-GODTYCKLIG' in x['beskrivning'] for x in _sparbarhet(f.regelbas, d.model_copy(update={'avsnitt': (fel,)}), f.analys))


def test_v7_utan_tjanstspecifika_faktorer_kraver_ingen_pahittad_femte_katalogprovning(v7fall):
    from riskanalys.dokument.kallhanvisningar import utan_kallhanvisning
    d = bygg(v7fall)
    for a in d.avsnitt:
        for tab in a.tabeller:
            if tab.id.endswith('-kategorier'):
                rad = tab.rader[-1]
                assert utan_kallhanvisning(rad.celler[1].text) == 'Inga katalogfaktorer'
                assert '[VERIFIERA]' not in rad.celler[2].text
                assert 'uppdrag' in rad.celler[2].text.lower()


def test_forifyll_erbjuder_tjanstprovning_nar_katalogen_har_faktorer(v7fall):
    from riskanalys.analys.utkast import forifyll_analys
    f, _ = v7fall
    tj = f.analys.tjanster[0].tjanst
    id = f.regelbas.tjanster[tj].sarbarheter[0]
    s = f.regelbas.sarbarheter[id].model_copy(update={'omrade': 'tj'})
    rb = f.regelbas.model_copy(update={'sarbarheter': {**f.regelbas.sarbarheter, id: s}})
    a = forifyll_analys(rb, f.profil, f.bedomning, f.analys.bindning)
    t = next(t for t in a.tjanster if t.tjanst == tj)
    assert any(p.omrade == 'tjanst' and id in p.sarbarheter and p.relevans == 'okant' for p in t.sarbarhetsprovningar)


def test_tjanstfaktor_kan_inte_utelamnas_ur_lokal_katalogprovning(v7fall):
    from riskanalys.analys.provning import _sarbarheter
    f, _ = v7fall
    t = f.analys.tjanster[0]
    kat = f.regelbas.tjanster[t.tjanst]
    id = kat.sarbarheter[0]
    rb = f.regelbas.model_copy(update={'sarbarheter': {**f.regelbas.sarbarheter,
        id: f.regelbas.sarbarheter[id].model_copy(update={'omrade': 'tj'})}})
    t = t.model_copy(update={'sarbarhetsprovningar': tuple(p.model_copy(update={
        'sarbarheter': tuple(x for x in p.sarbarheter if x != id)}) for p in t.sarbarhetsprovningar)})
    fel = []
    _sarbarheter(t, rb, kat, {}, set(), lambda *a: None, lambda *a: None,
        lambda giltigt, text: fel.append(text) if not giltigt else None)
    assert 'Sårbarhetsområdet tjanst saknas.' in fel


def test_generiskt_v7_testsvar_ger_fortsatt_likhetsfynd(v7fall):
    from riskanalys.dokument.likhet import likhetsfynd
    _, r = v7fall
    assert len(likhetsfynd(list(r.values()))) == 6


def test_v6_resultat_bevaras_och_far_inte_tvingas_till_v7(v6underlag):
    rb, p, b, r, h = v6underlag
    assert bygg_arb_v6(rb, p, b, r, h, analys=None).formatversion == V6
    with pytest.raises(RiskanalysFel, match='identitet'):
        bygg_arb_v6(rb, p, b, r, h, analys=None, formatversion=V7)


def test_v7_korta_hanvisningar_och_enbart_entydig_hotkolumn_tas_bort(v7fall):
    d = bygg(v7fall)
    text = ' '.join(s.text for a in d.avsnitt for s in a.stycken)
    assert 'Hänvisningar.' in text
    assert 'Gemensamma hänvisningar inom avsnittet.' not in text
    assert 'Fältkoppling och belägg: bilaga B1.' not in text
    gem = d.avsnitt_med_id()['D-ARB.4'].tabeller[0]
    assert 'Hot' not in gem.kolumner
    f, _ = v7fall
    for s, r in zip(f.analys.gemensamma_scenarier, gem.rader):
        assert set(s.hot) <= set(r.celler[0].referenser)


def test_v7_tf_samma_faktorer_kraver_exakt_overensstammelse(v7fall):
    from riskanalys.dokument.nivamotivering_v6 import nivamotivering_stycken
    f, _ = v7fall
    from riskanalys.bedomning.motor import bedom
    from riskanalys.regelverk.urval import valj
    rb = f.regelbas.model_copy(update={'metod': f.regelbas.metod.model_copy(update={'scenario': None})})
    urval = valj(rb, f.profil.byra.regelpaket, f.profil.byra.datum, f.profil.byra.lan)
    t = tjanster_med_avsnitt(bedom(rb, urval, f.profil))[0][1]
    texter = [s.text for s in nivamotivering_stycken(rb, t, None, formatversion=V7)]
    assert any('TF-risk:' in s and 'samma faktorer och vikter som PT' in s for s in texter)
    # En kundfaktor räknas för PT men inte TF; samma-nämning får då inte användas.
    id = next(id for id in f.regelbas.tjanster[t.tjanst].sarbarheter if f.regelbas.sarbarheter[id].omrade == 'kund')
    annan = t.model_copy(update={'tillampade_sarbarheter': (*t.tillampade_sarbarheter, id)})
    texter = [s.text for s in nivamotivering_stycken(rb, annan, None, formatversion=V7)]
    assert not any('samma faktorer och vikter som PT' in s for s in texter)


def test_v7_metadatagruppering_bevarar_fritext_och_skilda_belagg(v7fall):
    from riskanalys.dokument.redaktion_v7 import grupperade_profilbelagg
    f, _ = v7fall
    ids = ('P-BEVAKNING.ansvarig', 'P-BEVAKNING.relevans')
    etiketter = dict(zip(ids, ('Ansvar', 'Relevans')))
    text = grupperade_profilbelagg(f.regelbas, f.profil, ids, etiketter, gransindex={})
    assert text.count('Syntetisk testkälla') == 1
    for id in ids:
        assert str(f.profil.uppgifter[id].varde) in text
    upp = f.profil.uppgifter[ids[1]].model_copy(update={'kalla': 'En annan källa', 'datum': date(2026,10,11),
        'varde': 'Författad text (med parentes)\nbevaras exakt'})
    p = f.profil.model_copy(update={'uppgifter': {**f.profil.uppgifter, ids[1]: upp}})
    text = grupperade_profilbelagg(f.regelbas, p, ids, etiketter, gransindex={})
    assert upp.varde in text
    assert 'Syntetisk testkälla' in text and 'En annan källa' in text
    assert '2026-10-10' in text and '2026-10-11' in text


def test_v7_konstant_betydelse_staar_ordagrant_en_gang_direkt_vid_tabellen(v7fall):
    from riskanalys.dokument.redaktion_v7 import samla_konstant_betydelse
    from riskanalys.dokument.analystabeller import scenariorad
    from riskanalys.dokument.analysreferenser import bygg_analysreferenser
    from riskanalys.dokument.tabeller import tabell
    f, _ = v7fall
    rader = tuple(scenariorad(s, f.regelbas, bygg_analysreferenser(f.analys)) for s in f.analys.gemensamma_scenarier)
    tab = tabell('prov', 'Scenario', ('Scenario', 'Händelseförlopp', 'Betydelse', 'Hot', 'Belägg'), rader)
    nytt, text = samla_konstant_betydelse(tab)
    assert 'Betydelse' not in nytt.kolumner
    assert text.text.endswith(rader[0].celler[2].text)
    assert all(ref in text.referenser for r in rader for ref in r.celler[2].referenser)
    andra = rader[0].model_copy(update={'celler': (*rader[0].celler[:2], rader[0].celler[2].model_copy(update={'text': 'Annan saklig prövning.'}), *rader[0].celler[3:])})
    annan = tab.model_copy(update={'rader': (andra, *rader[1:])})
    assert samla_konstant_betydelse(annan) == (annan, None)
    d = bygg(v7fall)
    a = d.avsnitt_med_id()['D-ARB.4']
    assert 'Betydelse' not in a.tabeller[0].kolumner
    assert any(rader[0].celler[2].text in s.text for s in a.stycken)
    assert not any('Myndighetsunderlag:' in s.text for s in a.stycken)


@pytest.mark.parametrize('yta', ['b1-rubrik', 'kategori-tabell', 'geografi', 'rapporter'])
def test_v7_aterbygge_upptacker_andrade_rubriker_tabeller_och_lasta_stycken(v7fall, yta):
    from riskanalys.granskning.dokument_v6 import analysfynd_v6
    f, r = v7fall
    d = bygg(v7fall)
    id = 'D-ARB.B1' if yta == 'b1-rubrik' else next(iter(r))
    a = d.avsnitt_med_id()[id]
    if yta == 'b1-rubrik':
        nytt = a.model_copy(update={'underrubriker': (a.underrubriker[0].model_copy(update={'rubrik': 'Felaktig rubrik'}), *a.underrubriker[1:])})
    elif yta == 'kategori-tabell':
        tab = a.tabeller[0]
        rad = tab.rader[0]
        cell = rad.celler[1].model_copy(update={'text': 'Felaktigt utfall'})
        tab = tab.model_copy(update={'rader': (rad.model_copy(update={'celler': (rad.celler[0], cell, rad.celler[2])}), *tab.rader[1:])})
        nytt = a.model_copy(update={'tabeller': (tab, *a.tabeller[1:])})
    else:
        ref = 'P-VERK.antal_rapporter' if yta == 'rapporter' else 'P-BESK.geografi'
        stycken = tuple(s.model_copy(update={'text': 'Underlaget saknar betydelse.'}) if s.proveniens == 'regelbas' and ref in s.referenser else s for s in a.stycken)
        assert stycken != a.stycken
        nytt = a.model_copy(update={'stycken': stycken})
    andrat = d.model_copy(update={'avsnitt': tuple(nytt if x.id == id else x for x in d.avsnitt)})
    fynd = analysfynd_v6(f.regelbas, f.bedomning, f.profil, andrat, Historik(), r, analys=f.analys)
    assert any(x['avsnitt'] == id and 'avviker från den frysta analysen' in x['beskrivning'] for x in fynd)
    if yta in ('geografi', 'rapporter'):
        assert any(x.get('regel') == ('B-10' if yta == 'geografi' else 'B-15') for x in fynd)


def test_v7_maxsvar_bevaras_och_langdvarning_trunkerar_inte(v7fall):
    from riskanalys.dokument.rendering import synliga_texter
    from riskanalys.dokument.modeller import AIStycke
    f, _ = v7fall
    svar = bygg_delsvar(f.regelbas, f.profil, f.bedomning, formatversion=V7)
    maxsvar = []
    for s in svar:
        kvar = 320 - sum(len(x.text.split()) for x in s.stycken)
        maxsvar.append(s.model_copy(update={'stycken': [*s.stycken,
            AIStycke(typ='analys', text=' '.join(['Kontrollunderlag'] * kvar), referenser=['P-KUND.antal_aktiva'])]}))
    lev = Testleverantor(maxsvar)
    r = {id: skriv_tjanst(lev, f.regelbas, f.profil, t, id, effort='medium', personnamn=(), spara=lambda *a: None,
        formatversion=V7) for id, t in tjanster_med_avsnitt(f.bedomning)}
    assert all(not d.mall for x in r.values() for d in x.delar)
    d = bygg_arb_v6(f.regelbas, f.profil, f.bedomning, r, Historik(), analys=f.analys)
    huvud = '\n'.join(text for a in d.avsnitt if a.id != 'D-ARB.B1' for text in synliga_texter(a))
    for s in maxsvar:
        assert sum(len(x.text.split()) for x in s.stycken) == 320
        assert all(x.text in huvud for x in s.stycken)
    assert 'Redaktionell längdvarning' in huvud
    print({'fall': 'V7-max', **dokumentord(d, f.profil)})


def test_v7_numrerar_gemensamma_resonemang_utan_dubbla_etiketter(v7fall):
    import re
    d = bygg(v7fall)
    gem = d.avsnitt_med_id()['D-ARB.5']
    assert [int(re.match(r'(\d+)\. ', s.text)[1]) for s in gem.stycken] == list(range(1, len(gem.stycken) + 1))
    assert any('Gemensam scenarioberäkning' in s.text for s in gem.stycken)
    assert not any('Gemensamt resonemang ' in s.text for s in gem.stycken)
    for a in d.avsnitt:
        if a.id.startswith('D-ARB.6.'):
            assert any(s.text.startswith('Se gemensamma resonemang ') for s in a.stycken)


@pytest.mark.parametrize('saknat', [False, True])
def test_v7_reservtext_ar_kort_och_hela_unika_katalogen_bevaras_i_b1(v7fall, saknat):
    from riskanalys.dokument.tjanstavsnitt_v6 import _mall
    from riskanalys.regelverk.granser import metodgransindex
    from riskanalys.granskning.analys import mallfynd
    from riskanalys.dokument.lasta_v6 import lasta_stycken_v6
    f, resultat = v7fall
    fryst = {id: r.model_dump_json() for id, r in resultat.items()}
    reserv = {id: r.model_copy(update={'delar': (r.del_('analys').model_copy(update={'mall': True}),)})
              for id, r in resultat.items()}
    d = bygg_arb_v6(f.regelbas, f.profil, f.bedomning, {} if saknat else reserv, Historik(),
        analys=f.analys, formatversion=V7)
    index = metodgransindex(f.regelbas)
    for id, t in tjanster_med_avsnitt(f.bedomning):
        a = d.avsnitt_med_id()[id]
        slut_analys = a.underrubriker[1].fore_stycke
        lastatexter = {s.text for del_id in ('hot', 'sarbarheter')
            for s in lasta_stycken_v6(f.regelbas, f.profil, t, del_id, gransindex=index)}
        reservord = len(a.stycken[0].text.split()) + sum(len(s.text.split())
            for s in a.stycken[1:slut_analys] if s.proveniens == 'regelbas'
            and utan_kallhanvisning(s.text) not in lastatexter)
        assert reservord <= 110, (id, reservord)
    b1 = d.avsnitt_med_id()['D-ARB.B1']
    rubrik = next(u for u in b1.underrubriker if u.rubrik == 'Katalogunderlag när AI-text saknas')
    slut = next((u.fore_stycke for u in b1.underrubriker if u.fore_stycke > rubrik.fore_stycke), len(b1.stycken))
    katalog = b1.stycken[rubrik.fore_stycke:slut]
    index = metodgransindex(f.regelbas)
    huvud = ' '.join(post.text for avsnitt in d.avsnitt if avsnitt.id != 'D-ARB.B1' for post in avsnitt.stycken)
    unika = {}
    for id, t in tjanster_med_avsnitt(f.bedomning):
        a = d.avsnitt_med_id()[id]
        assert '[VERIFIERA]' in a.stycken[0].text and 'Validerad AI-text saknas' in a.stycken[0].text
        assert 'bilaga B1' in a.stycken[0].text and a.stycken[0].proveniens == 'lokal'
        assert len(a.stycken[0].text.split()) <= 110
        for del_id in ('hot', 'sarbarheter'):
            for s in lasta_stycken_v6(f.regelbas, f.profil, t, del_id, gransindex=index):
                assert any(utan_kallhanvisning(n.text) == s.text for n in a.stycken)
        lokal = next(x for x in f.analys.tjanster if x.tjanst == t.tjanst)
        assert lokal.pt_motivering in huvud and lokal.tf_motivering in huvud and lokal.slutsats in huvud
        fulla = (*_mall(f.regelbas, f.profil, t, 'hot', 'analys', index)[1:],
                 *_mall(f.regelbas, f.profil, t, 'sarbarheter', 'sårbarhetsanalys', index)[1:])
        for s in fulla:
            key = (s.typ, s.text, s.proveniens)
            unika.setdefault(key, set()).update((*s.referenser, id))
            assert not any(utan_kallhanvisning(n.text) == s.text for n in a.stycken)
        if not saknat:
            assert any(x['allvar'] == 'blockerande' for x in mallfynd(reserv[id]))
    assert len(katalog) == len(unika)
    for (typ, text, proveniens), refs in unika.items():
        (post,) = [s for s in katalog if (s.typ, utan_kallhanvisning(s.text), s.proveniens) == (typ, text, proveniens)]
        assert refs <= set(post.referenser)
    assert {id: r.model_dump_json() for id, r in resultat.items()} == fryst
    print({'fall': 'V7-reserv', 'saknat': saknat, 'unika_katalogstycken': len(unika), **dokumentord(d, f.profil)})


def test_v7_reservkatalogens_b1_rubrik_och_text_binds_vid_aterbygge(v7fall):
    from riskanalys.granskning.dokument_v6 import analysfynd_v6
    f, r = v7fall
    reserv = {id: post.model_copy(update={'delar': (post.del_('analys').model_copy(update={'mall': True}),)})
              for id, post in r.items()}
    d = bygg_arb_v6(f.regelbas, f.profil, f.bedomning, reserv, Historik(), analys=f.analys)
    b1 = d.avsnitt_med_id()['D-ARB.B1']
    u = next(u for u in b1.underrubriker if u.rubrik == 'Katalogunderlag när AI-text saknas')
    for ny in (b1.model_copy(update={'underrubriker': tuple(x for x in b1.underrubriker if x != u)}),
               b1.model_copy(update={'stycken': tuple(s.model_copy(update={'text': s.text + ' Ändrat.'})
                   if i == u.fore_stycke else s for i, s in enumerate(b1.stycken))})):
        andrat = d.model_copy(update={'avsnitt': tuple(ny if a.id == b1.id else a for a in d.avsnitt)})
        fynd = analysfynd_v6(f.regelbas, f.bedomning, f.profil, andrat, Historik(), reserv, analys=f.analys)
        assert any(x['avsnitt'] == b1.id and 'avviker från den frysta analysen' in x['beskrivning'] for x in fynd)
