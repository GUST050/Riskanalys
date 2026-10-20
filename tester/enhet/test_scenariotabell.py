"""Scenariodokument visar sparade beräkningar, aldrig nya riskbeslut."""
import hashlib
import json

import pytest

from riskanalys.dokument.nivamotivering_v6 import nivamotivering_stycken
from riskanalys.dokument.nivatext import utfallsforklaring
from riskanalys.dokument.skrivversion import V7
from tester.enhet.test_arb_v7 import v7fall, bygg  # noqa: F401


@pytest.fixture
def tjanst(v7fall):
    return v7fall[0].bedomning.tjanster[0]


def test_tabell_har_alla_scenarier_kolumner_och_avgorande_markering(v7fall, tjanst):
    from riskanalys.dokument.scenariotabell import bygg_scenariotabell
    rb = v7fall[0].regelbas
    tab = bygg_scenariotabell(rb, tjanst)
    assert tab.kolumner == ('Hot', 'Hotnivå', 'Möjliggörande sårbarheter', 'Sannolikhet', 'Risk', 'Täckande kontroll', 'Kvarstående')
    assert len(tab.rader) == len(tjanst.scenarier)
    for s, rad in zip(tjanst.scenarier, tab.rader):
        assert rb.hot[s.hot].namn in rad.celler[0].text
        assert ('TF' in rad.celler[0].text) == (s.dimension == 'tf')
        assert ('avgör nivån' in rad.celler[0].text) == s.avgorande
        assert set(s.sarbarheter) <= set(rad.celler[2].referenser)
        if 'S-GEO-01' in s.sarbarheter:
            assert 'Utlandstransaktioner' in rad.celler[2].text
        if 'S-ARB-10' in s.sarbarheter:
            assert 'Extern KYC/AML-leverantör' in rad.celler[2].text
        assert all(c.proveniens == 'regelbas' for c in rad.celler)


def test_aldre_bedomning_har_ingen_scenariotabell(v7fall, tjanst):
    from riskanalys.dokument.scenariotabell import bygg_scenariotabell
    assert bygg_scenariotabell(v7fall[0].regelbas, tjanst.model_copy(update={'scenarier': ()})) is None


def test_iakttaget_och_belagd_kontroll_aterges(v7fall, tjanst):
    from riskanalys.dokument.scenariotabell import bygg_scenariotabell
    rb = v7fall[0].regelbas
    s = next(s for s in tjanst.scenarier if s.dimension == 'pt')
    kid = tjanst.kontroller[0].id
    s = s.model_copy(update={'iakttaget': True, 'tackande_kontroller': (kid,), 'avgorande': True})
    t = tjanst.model_copy(update={'scenarier': (s,)})
    assert '(iakttaget)' in bygg_scenariotabell(rb, t).rader[0].celler[1].text
    text = nivamotivering_stycken(rb, t, None, formatversion=V7)[0].text
    assert text.startswith('Avgörande scenario (PT): ' + rb.hot[s.hot].namn)
    assert '(iakttaget)' in text
    assert rb.kontroller[kid].namn + ' täcker scenariot och har belagd effekt' in text
    assert 'Sannolikhet ' + s.sannolikhet in text


def test_alla_avgorande_namn_bevaras_vid_gruppering(v7fall, tjanst):
    rb = v7fall[0].regelbas
    s = tjanst.scenarier[0].model_copy(update={'avgorande': True})
    annat = next(x.hot for x in tjanst.scenarier if x.hot != s.hot)
    t = tjanst.model_copy(update={'scenarier': (s, s.model_copy(update={'hot': annat}))})
    texter = [x.text for x in nivamotivering_stycken(rb, t, None, formatversion=V7) if 'Avgörande scenario' in x.text]
    assert len(texter) == 1
    assert rb.hot[s.hot].namn in texter[0] and rb.hot[annat].namn in texter[0]


def test_scenariots_egna_faktorer_och_dimensionens_bas_anvands(v7fall, tjanst):
    rb = v7fall[0].regelbas
    s = next(s for s in tjanst.scenarier if s.dimension == 'tf').model_copy(update={'avgorande': True})
    id = next(iter(rb.sarbarheter))
    s = s.model_copy(update={'sarbarheter': (id,)})
    t = tjanst.model_copy(update={'scenarier': (s,), 'tillampade_sarbarheter': ()})
    text = nivamotivering_stycken(rb, t, None, formatversion=V7)[0].text
    assert 'TF' in text
    assert rb.sarbarheter[id].namn in text
    assert 'tjänstens egen nivå ' + rb.tjanster[t.tjanst].grund_tf_sannolikhet in text


def test_kvarstaende_max_kan_avgoras_av_annat_scenario(v7fall, tjanst):
    rb = v7fall[0].regelbas
    a, b = [s for s in tjanst.scenarier if s.dimension == 'pt'][:2]
    a = a.model_copy(update={'risk': 'mycket hög', 'avgorande': True, 'kvarstaende': 'hög'})
    b = b.model_copy(update={'risk': 'hög', 'avgorande': False, 'kvarstaende': 'hög'})
    t = tjanst.model_copy(update={'scenarier': (a, b), 'kvarstaende': 'hög'})
    text = ' '.join(x.text for x in nivamotivering_stycken(rb, t, None, formatversion=V7))
    assert 'Högsta kvarstående PT-risk: hög' in text
    assert rb.hot[a.hot].namn in text
    assert 'Avgörande scenarier ändras; se B1.' in text
    assert 'Lokal reduktionsprövning:' in text
    b1 = ' '.join(c.text for r in utfallsforklaring(t, rb).rader for c in r.celler)
    assert rb.hot[b.hot].namn in b1 and 'metodval' in b1.lower()


def test_b1_har_hela_berakningen_och_samtliga_regelspar(v7fall, tjanst):
    rb = v7fall[0].regelbas
    tab = utfallsforklaring(tjanst, rb)
    assert len(tab.rader) == len(tjanst.scenarier) + 2  # maxaggregering + separat sanktion
    for s, rad in zip(tjanst.scenarier, tab.rader):
        text = ' '.join(c.text for c in rad.celler)
        assert rb.hot[s.hot].namn in text
        assert all(regel in text for regel in s.regelspar)
        for v in (s.hotniva, s.sarbarhetsniva, s.sannolikhet, s.konsekvens, s.risk):
            assert v in text
        assert all(rb.sarbarheter[id].namn in text for id in s.sarbarheter)
        assert 'Begränsning:' not in text
    assert 'Sanktioner' == tab.rader[-1].celler[0].text


def test_b1_okant_scenarioregelspar_ger_begransning(v7fall, tjanst):
    s = tjanst.scenarier[0].model_copy(update={'regelspar': ()})
    t = tjanst.model_copy(update={'scenarier': (s, *tjanst.scenarier[1:])})
    assert 'Begränsning:' in ' '.join(c.text for r in utfallsforklaring(t, v7fall[0].regelbas).rader for c in r.celler)


def test_v7_scenarier_ersatter_kategorier_men_bevarar_lokal_tabell(v7fall):
    f, _ = v7fall
    d = bygg(v7fall)
    for a in d.avsnitt:
        if a.id.startswith('D-ARB.6.'):
            assert 'Scenarier' in [u.rubrik for u in a.underrubriker]
            assert any(t.id.endswith('-motorscenarier') for t in a.tabeller)
            assert not any(t.id.endswith('-kategorier') for t in a.tabeller)
            assert any(t.id.endswith('-scenarier') for t in a.tabeller)
    b1 = d.avsnitt_med_id()['D-ARB.B1']
    assert any('Lokala faktorutfall' == u.rubrik for u in b1.underrubriker)


def test_ai_begarans_hela_payload_bevaras(v7fall):
    """Föreprovet från 1.6.0 omfattar prompt, schema, instruktion och skyddat faktablad."""
    from riskanalys.dokument.leverantor import Testleverantor
    from riskanalys.dokument.delskrivning import skriv_tjanst
    from riskanalys.dokument.underlag import tjanster_med_avsnitt
    from tester.fixturer.m2 import bygg_delsvar
    f, _ = v7fall
    lev = Testleverantor(bygg_delsvar(f.regelbas, f.profil, f.bedomning, formatversion=V7))
    for id, t in tjanster_med_avsnitt(f.bedomning):
        skriv_tjanst(lev, f.regelbas, f.profil, t, id, effort='medium', personnamn=(), spara=lambda *a: None, formatversion=V7)
    hashes = [hashlib.sha256(json.dumps(a.model_dump(mode='json', by_alias=True), sort_keys=True, ensure_ascii=False).encode()).hexdigest() for a in lev.delanrop]
    assert hashes == ['f43db955de63dccff2f2bb24dd4296c5c9b09b0c84f58cd4f128f158c9bae5b8', 'eeb73a57545bb1a42a22f3ff520bd00486a9a048100a8295953e503c2cd93006', 'a42f394fe0af840388a638e0dbb06a83614ba5eb373a66aa07cb8c31d9a9128d', '77b11b509a996c41321dd66f5732ea525c06f742c9d9241e31f171688f7b86e2']


def test_identiska_berakningar_samlas_med_alla_tjanster_och_dimensioner(v7fall):
    d = bygg(v7fall)
    gem = d.avsnitt_med_id()['D-ARB.5']
    berakningar = [s for s in gem.stycken if 'Gemensam scenarioberäkning' in s.text]
    assert {('PT' if '(PT)' in s.text else 'TF') for s in berakningar} == {'PT', 'TF'}
    for s in berakningar:
        assert all(v7fall[0].regelbas.tjanster[t.tjanst].namn in s.text for t in v7fall[0].bedomning.tjanster if t.erbjuds)
    for a in d.avsnitt:
        if a.id.startswith('D-ARB.6.'):
            assert any('Se resonemang' in s.text for s in a.stycken)
            assert any('täcker scenariot och har belagd effekt' in s.text for s in a.stycken)


def test_hotflerval_visar_namn_utan_interna_hotid(v7fall):
    from riskanalys.bedomning.scenarier import iakttagelsefalt
    from riskanalys.dokument.klartext import uppgiftstext
    from riskanalys.profil.modeller import Uppgift
    from tester.fixturer.m2 import DAG
    f, _ = v7fall
    t = f.bedomning.tjanster[0]
    id = iakttagelsefalt(f.regelbas.tjanster[t.tjanst])
    hot = t.hot[:2]
    u = Uppgift(varde=list(hot), status='bekräftad', kalla='Syntetisk observation', datum=DAG, bekraftad_av='FfR')
    p = f.profil.model_copy(update={'uppgifter': {**f.profil.uppgifter, id: u}})
    text = uppgiftstext(f.regelbas, p, id)
    assert all(f.regelbas.hot[h].namn in text for h in hot)
    assert all(h not in text for h in hot)


@pytest.mark.parametrize('status', ['saknas', 'föreslagen', 'bekräftad'])
def test_frivillig_iakttagelse_utan_belagg_skapa_inte_dokumentstopp(v7fall, status):
    from riskanalys.bedomning.scenarier import iakttagelsefalt
    from riskanalys.dokument.intagsunderlag import bygg_underlagsbilaga
    from riskanalys.profil.modeller import Uppgift
    f, _ = v7fall
    id = iakttagelsefalt(f.regelbas.tjanster[f.bedomning.tjanster[0].tjanst])
    p = f.profil.model_copy(update={'uppgifter': {**f.profil.uppgifter,
        id: Uppgift(varde=list(f.bedomning.tjanster[0].hot[:1]), status=status)}})
    bilaga = bygg_underlagsbilaga(f.regelbas, p)
    rad = next(s for s in bilaga.stycken if s.referenser == [id])
    assert '[VERIFIERA]' not in rad.text
    assert 'katalogens hotnivå' in rad.text.lower()
    assert 'Inga iakttagna hot' not in rad.text
    assert f.regelbas.hot[f.bedomning.tjanster[0].hot[0]].namn not in rad.text


def test_ny_scenariotabell_har_lasbara_kolumnbredder(v7fall, tmp_path):
    import docx
    from riskanalys.dokument.wordstil import formatera_tabell
    word = docx.Document()
    tab = word.add_table(rows=1, cols=7)
    formatera_tabell(word, tab, 'T-RED-01-motorscenarier')
    assert tab.columns[0].width > tab.columns[1].width
    assert tab.columns[2].width > tab.columns[3].width
    assert tab.columns[5].width > tab.columns[4].width


def test_gruppering_skiljer_faktoridentitet_och_vikt_trots_samma_namn(v7fall):
    from riskanalys.dokument.modeller import Avsnitt, Textstycke
    from riskanalys.dokument.scenariotabell import sammanfor_scenarioforklaringar
    f, _ = v7fall
    rb = f.regelbas
    id1, id2 = list(rb.sarbarheter)[:2]
    original = rb.sarbarheter[id1]
    annan = rb.sarbarheter[id2].model_copy(update={'namn': original.namn,
        'effekt': original.effekt.model_copy(update={'sannolikhet': 2})})
    rb = rb.model_copy(update={'sarbarheter': {**rb.sarbarheter, id2: annan}})
    text = ('Avgörande scenario (PT): Samma hot. Hotnivå medel; sårbarhetsnivå hög: '
            'tjänstens egen nivå medel, höjd av ' + original.namn + '. '
            'Sannolikhet hög, konsekvens betydande, risk hög. Egen kontrollmening.')
    poster = tuple(Avsnitt(id=f'D-ARB.6.{n}', rubrik='Test', kalla='regelbas', stycken=(
        Textstycke(typ='motivering', text=text, referenser=[id], proveniens='regelbas'),))
        for n, id in enumerate((id1, id2), 1))
    nya, gem = sammanfor_scenarioforklaringar(poster, rb, startnummer=1)
    assert nya == poster and gem == ()


def test_historiskt_v7_bevarar_kategorioversikten(v7fall):
    from riskanalys.bedomning.motor import bedom
    from riskanalys.regelverk.urval import valj
    from riskanalys.regelverk.granser import metodgransindex
    from riskanalys.dokument.tjanstavsnitt_v7 import bygg_tjanstavsnitt_v7
    f, _ = v7fall
    rb = f.regelbas.model_copy(update={'metod': f.regelbas.metod.model_copy(update={'scenario': None})})
    b = bedom(rb, valj(rb, f.profil.byra.regelpaket, f.profil.byra.datum, f.profil.byra.lan), f.profil)
    t = b.tjanster[0]
    assert not t.scenarier
    a = bygg_tjanstavsnitt_v7(rb, f.profil, t, None, 'D-ARB.6.1', gransindex=metodgransindex(rb))
    assert a.tabeller[0].id.endswith('-kategorier')
    assert a.tabeller[0].kolumner == ('Område', 'Utfall', 'Byråns prövning')
    assert 'Kategorier' in [u.rubrik for u in a.underrubriker]
