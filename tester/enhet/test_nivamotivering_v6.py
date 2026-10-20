"""Risknivå och motivering: programmets beräkning i ord och byråns egen bedömning, skilda åt i varje tjänst."""
import pytest

from riskanalys.dokument.arb_v6 import bygg_arb_v6
from riskanalys.dokument.nivamotivering_v6 import berakningsmotivering, nivamotivering_stycken
from riskanalys.granskning.kontroller import RISKAVSNITT
from tester.enhet.test_arb_v6 import v6underlag as _v6underlag
from tester.enhet.test_lokalt_dokument_v6 import lokal  # noqa: F401  pytest-fixtur

PT_BYRA = 'Byråns bedömning av penningtvättsrisken: '
TF_BYRA = 'Byråns bedömning av TF-risken: '
LIKA_PT = 'Byrån bedömer att fakturaflödenas ekonomiska innebörd avgör penningtvättsrisken i varje uppdrag.'
LIKA_TF = 'Byrån bedömer att betalningsändamål och mottagare avgör risken för finansiering av terrorism här.'


@pytest.fixture(scope='module')
def v6underlag(regelbas_v1):
    """Frys uttryckligen äldre summeringsmetod; scenariovägen provas separat."""
    rb = regelbas_v1.model_copy(update={'metod': regelbas_v1.metod.model_copy(update={'scenario': None})})
    return _v6underlag.__wrapped__(rb)


def _bedomd(v6underlag, tjanst_id):
    return next(t for t in v6underlag[2].tjanster if t.tjanst == tjanst_id)


def tjansteavsnitt(d):
    return [a for a in d.avsnitt if a.id.startswith(RISKAVSNITT)]


@pytest.fixture
def regelbas(v6underlag):
    return v6underlag[0]


@pytest.fixture
def tjanst(v6underlag):
    """Löpande bokföring: inga tillämpade faktorer; belagda kontroller ger sänkningen."""
    return _bedomd(v6underlag, 'T-RED-01')


@pytest.fixture
def tjanst_med_tak(v6underlag, regelbas):
    """Bolagsbildning: grundnivån hög och en höjande faktor, så taket nås."""
    t = _bedomd(v6underlag, 'T-BOLAG-01')
    assert regelbas.tjanster[t.tjanst].grund_sannolikhet == 'hög' and t.tillampade_sarbarheter
    return t


@pytest.fixture
def tjanst_med_sankning(v6underlag, regelbas):
    t = _bedomd(v6underlag, 'T-SKATT-01')
    assert regelbas.metod.kvarstaende_sankning.id in t.regelspar and t.kvarstaende != t.inneboende.risk
    return t


@pytest.fixture
def analys(lokal, tjanst):
    return next(a for a in lokal.tjanster if a.tjanst == tjanst.tjanst)


@pytest.fixture
def v6_dokument(v6underlag, lokal):
    return bygg_arb_v6(*v6underlag, analys=lokal)


@pytest.fixture
def v6_dokument_med_lika_motiveringar(v6underlag, lokal):
    tjanster = tuple(a.model_copy(update={'pt_motivering': LIKA_PT, 'tf_motivering': LIKA_TF}) for a in lokal.tjanster)
    return bygg_arb_v6(*v6underlag, analys=lokal.model_copy(update={'tjanster': tjanster}))


def test_berakningen_namner_alla_tillampade_faktorer_och_taket(regelbas, tjanst_med_tak):
    pt = berakningsmotivering(tjanst_med_tak, regelbas)[0]
    for sid in tjanst_med_tak.tillampade_sarbarheter:
        if regelbas.sarbarheter[sid].galler in {'penningtvatt', 'bada'}:
            assert regelbas.sarbarheter[sid].namn in pt
    assert 'taket hög' in pt and 'ändrar inte nivån' in pt


def test_kvarstaende_sankning_markeras_som_ogranskat_metodval(regelbas, tjanst_med_sankning):
    kvar = berakningsmotivering(tjanst_med_sankning, regelbas)[1]
    assert 'ogranskat metodval' in kvar and 'scenariotäckning' in kvar
    assert 'BT-KVAR-02' not in kvar  # regel-ID står i referenserna, inte i texten


def test_byrans_bedomning_star_skild_fran_berakningen(regelbas, tjanst, analys):
    texter = [s.text for s in nivamotivering_stycken(regelbas, tjanst, analys)]
    assert any(t.startswith('Byråns bedömning av penningtvättsrisken: ') for t in texter)
    assert any(t.startswith('Byråns bedömning av TF-risken: ') for t in texter)


def test_saknad_motivering_ger_verifiera(regelbas, tjanst):
    texter = ' '.join(s.text for s in nivamotivering_stycken(regelbas, tjanst, None))
    assert '[VERIFIERA]' in texter and 'Grundnivå' in texter


def test_motiveringar_samordnas_inte(v6_dokument_med_lika_motiveringar):
    for a in tjansteavsnitt(v6_dokument_med_lika_motiveringar):
        assert any(s.text.startswith('Byråns bedömning av penningtvättsrisken: ') for s in a.stycken)


def test_tjanst_har_underrubriken_risknivå_och_motivering(v6_dokument):
    for a in tjansteavsnitt(v6_dokument):
        assert [u.rubrik for u in a.underrubriker][-1] == 'Risknivå och motivering'


# Kompletterande prov av formuleringar, referenser och placering.

def test_berakningen_foljer_formuleringsmonstret_utan_faktorer(regelbas, tjanst):
    pt, kvar, tf, *sank = berakningsmotivering(tjanst, regelbas)
    katalog = regelbas.tjanster[tjanst.tjanst]
    assert pt == (f'Penningtvättsrisk före kontroller: {tjanst.inneboende.risk}. Grundnivå {katalog.grund_sannolikhet}; '
                  f'inga tillämpade faktorer höjer den; konsekvens {tjanst.inneboende.konsekvens}.')
    namn = [regelbas.kontroller[k.id].namn for k in tjanst.kontroller if k.fungerar_och_ar_belagd]
    assert kvar.startswith(f'Efter kontroller: {tjanst.kvarstaende}. Sänkningen bygger på belagd utformning och '
                           f'genomförande för {namn[0]}')
    assert all(n in kvar for n in namn)
    assert kvar.endswith('Lokal reduktionsprövning: inte gjord.')
    assert tf == (f'TF-risk: {tjanst.terrorfinansiering.risk}. Grundnivå {katalog.grund_tf_sannolikhet}; '
                  'inga tillämpade faktorer höjer den; konsekvensen är alltid allvarlig enligt metoden.')
    s = tjanst.sanktionsrisk
    assert sank == [f'Sanktionsrisk: {s.inneboende.risk} före och {s.kvarstaende} efter kontroll, '
                    'enligt den separata sanktionsmetoden.']


def test_bara_faktorer_som_galler_dimensionen_namns(regelbas, tjanst):
    pt_faktor = next(s for s in regelbas.sarbarheter.values() if s.galler == 'penningtvatt')
    bada = next(s for s in regelbas.sarbarheter.values() if s.galler == 'bada')
    t = tjanst.model_copy(update={'tillampade_sarbarheter': (pt_faktor.id,)})
    pt, _, tf, *_ = berakningsmotivering(t, regelbas)
    assert f'höjs av {pt_faktor.namn} (+{pt_faktor.effekt.sannolikhet}); konsekvens' in pt
    assert 'taket' not in pt  # medel + 1 når hög men överstiger den inte
    assert pt_faktor.namn not in tf and 'inga tillämpade faktorer höjer den' in tf
    t = tjanst.model_copy(update={'tillampade_sarbarheter': (pt_faktor.id, bada.id)})
    pt, _, tf, *_ = berakningsmotivering(t, regelbas)
    assert f'höjs av {pt_faktor.namn} (+1), {bada.namn} (+1); taket hög nås' in pt
    assert f'höjs av {bada.namn} (+1); konsekvensen' in tf


def test_utan_belagd_kontroll_sanker_motorn_inte(regelbas, tjanst):
    m = regelbas.metod
    t = tjanst.model_copy(update={
        'kontroller': tuple(k.model_copy(update={'fungerar_och_ar_belagd': False}) for k in tjanst.kontroller),
        'kvarstaende': tjanst.inneboende.risk,
        'regelspar': tuple(m.kvarstaende_ej_belagd.id if r == m.kvarstaende_sankning.id else r for r in tjanst.regelspar)})
    assert berakningsmotivering(t, regelbas)[1] == (
        f'Efter kontroller: {t.kvarstaende}; ingen kontroll har belagd funktion, så nivån sänks inte.')


def test_sankning_vid_lagsta_niva_pastar_ingen_faktisk_sankning(regelbas, tjanst):
    rad = next(r for r in regelbas.metod.riskmatris if r.risk == 'låg')
    gammal = next(r.id for r in regelbas.metod.riskmatris if r.id in tjanst.regelspar
                  and r.risk == tjanst.inneboende.risk and r.konsekvens == tjanst.inneboende.konsekvens)
    t = tjanst.model_copy(update={
        'inneboende': tjanst.inneboende.model_copy(update={'sannolikhet': rad.sannolikhet, 'konsekvens': rad.konsekvens, 'risk': 'låg'}),
        'kvarstaende': 'låg', 'regelspar': tuple(rad.id if r == gammal else r for r in tjanst.regelspar)})
    kvar = berakningsmotivering(t, regelbas)[1]
    assert 'redan skalans lägsta nivå' in kvar and 'ogranskat metodval' in kvar


def test_reduktionsstatus_kommer_fran_lokal_provning(regelbas, tjanst_med_sankning):
    kvar = berakningsmotivering(tjanst_med_sankning, regelbas, reduktionsprovning='metodkonflikt')[1]
    assert kvar.endswith('Lokal reduktionsprövning: öppen metodkonflikt.')
    for kod, fras in (('ej_reduktion', 'ingen reduktion redovisas'), ('motiverad', 'motiverad')):
        assert berakningsmotivering(tjanst_med_sankning, regelbas, reduktionsprovning=kod)[1].endswith(f': {fras}.')


def test_sanktionsmening_bara_nar_utfall_finns(regelbas, tjanst):
    assert len(berakningsmotivering(tjanst.model_copy(update={'sanktionsrisk': None}), regelbas)) == 3
    utan = tjanst.sanktionsrisk.model_copy(update={'inneboende': None, 'kvarstaende': None})
    assert len(berakningsmotivering(tjanst.model_copy(update={'sanktionsrisk': utan}), regelbas)) == 3


def test_okant_regelspar_ger_begransning_i_stallet_for_forklaring(regelbas, tjanst):
    pt, kvar, tf, *_ = berakningsmotivering(tjanst.model_copy(update={'regelspar': ()}), regelbas)
    for text in (pt, kvar, tf):
        assert 'Begränsning:' in text and 'Grundnivå' not in text and 'Sänkningen' not in text


def test_saknad_katalogpost_ger_begransning(regelbas, tjanst):
    pt, _, tf, *_ = berakningsmotivering(tjanst.model_copy(update={'tjanst': 'T-SAKNAS'}), regelbas)
    assert 'basnivå saknas' in pt and 'basnivå saknas' in tf


def test_alla_stycken_ar_motiveringar_med_sparbara_referenser(regelbas, tjanst, analys):
    stycken = nivamotivering_stycken(regelbas, tjanst, analys)
    assert {s.typ for s in stycken} == {'motivering'}
    berakning = stycken[:len(berakningsmotivering(tjanst, regelbas))]
    for s in berakning:
        assert s.proveniens == 'regelbas'
        assert {tjanst.tjanst, *tjanst.regelspar, *tjanst.tillampade_sarbarheter, 'D-ARB.B1'} <= set(s.referenser)
    assert set(tjanst.sanktionsrisk.regelspar) <= set(berakning[3].referenser)
    byran = stycken[len(berakning):]
    assert [s.text.split(': ')[0] for s in byran] == ['Byråns bedömning av penningtvättsrisken', 'Byråns bedömning av TF-risken']
    assert all(s.proveniens == 'lokal' for s in byran)
    assert byran[0].text.startswith(PT_BYRA + analys.pt_motivering)
    assert byran[1].text == TF_BYRA + analys.tf_motivering


def test_reduktionsmotivering_laggs_i_pt_stycket(regelbas, tjanst, analys):
    a = analys.model_copy(update={'reduktionsprovning': 'motiverad', 'reduktionsmotivering': 'Kontrollen täcker fakturahotet.'})
    pt = nivamotivering_stycken(regelbas, tjanst, a)[-2].text
    assert pt == f'{PT_BYRA}{a.pt_motivering} Reduktionsprövning: Kontrollen täcker fakturahotet.'
    utan = a.model_copy(update={'reduktionsprovning': 'ej_reduktion', 'reduktionsmotivering': ''})
    assert nivamotivering_stycken(regelbas, tjanst, utan)[-2].text == PT_BYRA + a.pt_motivering


def test_tom_motivering_ger_verifiera(regelbas, tjanst, analys):
    a = analys.model_copy(update={'pt_motivering': '  ', 'tf_motivering': '', 'reduktionsprovning': 'ej_reduktion'})
    pt, tf = (s.text for s in nivamotivering_stycken(regelbas, tjanst, a)[-2:])
    saknas = 'Saknas; förklara vilka förhållanden i tjänsten som motiverar nivån. [VERIFIERA]'
    assert pt == PT_BYRA + saknas and tf == TF_BYRA + saknas


def test_nivadelen_star_sist_och_lokala_raderna_ar_flyttade(v6_dokument, lokal):
    for a in tjansteavsnitt(v6_dokument):
        start = a.underrubriker[-1].fore_stycke
        assert a.stycken[start].text.startswith('Penningtvättsrisk före kontroller: ')
        assert all(s.typ == 'motivering' for s in a.stycken[start:])
        assert not any(s.text.startswith(('Motivering av PT-utfallet', 'Separat TF-prövning', 'Reduktionsprövning ('))
                       for s in a.stycken)
        assert not any(s.text == 'Motorns beräkning och fullständiga regelspår finns i bilaga B1.' for s in a.stycken)
        lokalstart = next(u.fore_stycke for u in a.underrubriker if u.rubrik == 'Lokal analys och slutsats')
        assert all(tab.fore_stycke == lokalstart for tab in a.tabeller)


def test_placeringen_haller_nar_lokal_text_samordnas(v6_dokument_med_lika_motiveringar):
    d = v6_dokument_med_lika_motiveringar
    assert any(s.text.startswith('Gemensamt resonemang') for s in d.avsnitt_med_id()['D-ARB.5'].stycken)
    for a in tjansteavsnitt(d):
        assert a.stycken[a.underrubriker[-1].fore_stycke].text.startswith('Penningtvättsrisk före kontroller: ')
        assert sum(LIKA_PT in s.text for s in a.stycken) == 1
    assert not any(LIKA_PT in s.text for s in d.avsnitt_med_id()['D-ARB.5'].stycken)


def test_oversikten_hanvisar_till_tjanstens_motivering(v6_dokument):
    forsta = v6_dokument.avsnitt_med_id()['D-ARB.8'].stycken[0].text
    assert forsta.startswith('Nivåerna är motorns utfall. Varje tjänsteavsnitt förklarar vilka faktorer som avgör nivån och '
                             'byråns egen bedömning. Hela beräkningen finns i bilaga B1.')
    assert 'Ingen sammanvägd byrånivå beräknas.' in forsta
