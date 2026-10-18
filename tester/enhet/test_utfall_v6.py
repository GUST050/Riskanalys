"""Lokala utfall redovisar skyddade värden utan att ändra villkor eller AI-underlag."""
from datetime import date

import pytest

from riskanalys.bedomning.motor import bedom
from riskanalys.profil.modeller import Period, Uppgift
from riskanalys.regelverk.urval import valj
from tester.enhet.test_arb_v6 import v6underlag


@pytest.fixture
def lokalt_fall(minimal_regelbas, profil_fabrik):
    lista = minimal_regelbas.tillatelselistor['risk_per_tjanst'].model_copy(update={'falt': ()})
    rb = minimal_regelbas.model_copy(update={'tillatelselistor': {lista.id: lista}})

    def bygg(varde, *, inaktuell=False, villkor=None):
        r = rb
        if villkor is not None:
            s = rb.sarbarheter['S-1'].model_copy(update={'villkor': villkor})
            r = rb.model_copy(update={'sarbarheter': {s.id: s}})
        p = profil_fabrik(r, {'P-A': varde, 'P-TJ.T-1.erbjuds': True})
        u = p.uppgifter['P-A']
        u = u.model_copy(update={'inaktuell': inaktuell,
            'period': Period(fran=date(2026, 1, 1), till=date(2026, 9, 30))})
        if varde is None:
            u = Uppgift()
        p = p.model_copy(update={'uppgifter': {**p.uppgifter, 'P-A': u}})
        t = bedom(r, valj(r, p.byra.regelpaket, p.byra.datum, p.byra.lan), p).tjanster[0]
        return r, p, t

    return bygg


@pytest.mark.parametrize(('varde', 'inaktuell', 'utfall', 'fras'), [
    (0.2, False, 'galler', 'gäller'),
    (0, False, 'ej_uppfyllt', 'villkoret är inte uppfyllt'),
    (0.1, False, 'under_grans', 'under metodens gräns'),
    (None, False, 'okant', '[VERIFIERA]'),
    (0.2, True, 'inaktuellt', 'inaktuellt underlag'),
])
def test_utfallet_formuleras_per_status(lokalt_fall, varde, inaktuell, utfall, fras):
    from riskanalys.dokument.utfall_v6 import sarbarhetsutfall, utfallsstycken
    rb, p, t = lokalt_fall(varde, inaktuell=inaktuell)
    assert sarbarhetsutfall(rb, p, 'S-1', gransindex={}) == utfall
    text = ' '.join(s.text for s in utfallsstycken(rb, p, t, gransindex={}))
    assert fras in text
    if varde is not None:
        assert '2026-01-01–2026-09-30' in text
    if inaktuell:
        assert '20 %' not in text
        assert '[VERIFIERA]' in text


def test_ej_uppfyllt_beskrivs_inte_som_franvaro_av_risk(lokalt_fall):
    from riskanalys.dokument.utfall_v6 import utfallsstycken
    rb, p, t = lokalt_fall(0)
    text = ' '.join(s.text for s in utfallsstycken(rb, p, t, gransindex={}))
    assert text.count('Ett villkor som inte är uppfyllt visar inte att risken saknas.') == 1
    assert 'gäller inte' not in text
    assert '0 %' in text


def test_grupperade_utfall_visar_gemensam_period_omfang_och_negativstatus_en_gang(lokalt_fall):
    from riskanalys.dokument.utfall_v6 import utfallsstycken
    rb, p, t = lokalt_fall(0)
    s = rb.sarbarheter['S-1'].model_copy(update={'id': 'S-2', 'namn': 'Annan sårbarhet'})
    tj = rb.tjanster[t.tjanst].model_copy(update={'sarbarheter': ('S-1', 'S-2')})
    rb = rb.model_copy(update={'sarbarheter': {**rb.sarbarheter, s.id: s}, 'tjanster': {tj.id: tj}})
    stycke, = utfallsstycken(rb, p, t, gransindex={})
    assert stycke.text.count('2026-01-01–2026-09-30') == 1
    assert stycke.text.count('byråövergripande') == 1
    assert stycke.text.count('inte uppfyllt') == 1
    assert stycke.text.count('0 %') == 2
    assert 'Testsårbarhet' in stycke.text and 'Annan sårbarhet' in stycke.text
    assert set(stycke.referenser) >= {'S-1', 'S-2', 'P-A', 'SRC-1', 'T-1'}


def test_ett_stycke_per_omrade_och_bara_lokalt_provade(lokalt_fall):
    from riskanalys.dokument.utfall_v6 import utfallsstycken
    rb, p, t = lokalt_fall(0.3)
    ursprung = rb.sarbarheter['S-1']
    sarbarheter = {f'S-{n}': ursprung.model_copy(update={'id': f'S-{n}', 'omrade': omrade})
        for n, omrade in enumerate(('kund', 'kund', 'kanal', 'geo', 'verk', 'tj'), start=1)}
    tj = rb.tjanster[t.tjanst].model_copy(update={'sarbarheter': tuple(sarbarheter)})
    rb = rb.model_copy(update={'sarbarheter': sarbarheter, 'tjanster': {tj.id: tj}})
    stycken = utfallsstycken(rb, p, t, gransindex={})
    assert [s.text.split(' enligt')[0] for s in stycken] == [
        'Kunder', 'Distributionskanaler', 'Geografi', 'Egen verksamhet', 'Tjänstespecifika förhållanden']
    assert all(s.proveniens == 'lokal' for s in stycken)
    assert set(stycken[0].referenser) >= {t.tjanst, 'S-1', 'S-2', 'P-A', 'SRC-1'}
    lista = rb.tillatelselistor['risk_per_tjanst'].model_copy(update={'falt': ('P-A',)})
    offentligt = rb.model_copy(update={'tillatelselistor': {lista.id: lista}})
    assert utfallsstycken(offentligt, p, t, gransindex={}) == ()


@pytest.mark.parametrize(('kombinator', 'varde', 'extra', 'inaktuell', 'forvantat'), [
    ('nagon', 0.1, True, False, 'galler'),
    ('nagon', 0.3, None, False, 'galler'),
    ('nagon', 0.3, False, True, 'galler'),
    ('alla', 0, None, False, 'ej_uppfyllt'),
    ('alla', 0, False, True, 'ej_uppfyllt'),
    ('alla', 0.1, None, False, 'ej_uppfyllt'),
])
def test_sammansatt_sanningsvarde_bevaras_med_kunskapslucka(
        lokalt_fall, kombinator, varde, extra, inaktuell, forvantat):
    from riskanalys.dokument.utfall_v6 import sarbarhetsutfall, utfallsstycken
    villkor = {kombinator: [
        {'falt': 'P-A', 'op': '>=', 'varde': 0.2},
        {'falt': 'P-TJ.T-1.erbjuds', 'op': '==', 'varde': True},
    ]}
    rb, p, t = lokalt_fall(varde, villkor=villkor)
    u = p.uppgifter['P-TJ.T-1.erbjuds'].model_copy(update={'inaktuell': inaktuell})
    if extra is None:
        u = Uppgift()
    else:
        u = u.model_copy(update={'varde': extra})
    p = p.model_copy(update={'uppgifter': {**p.uppgifter, 'P-TJ.T-1.erbjuds': u}})
    assert sarbarhetsutfall(rb, p, 'S-1', gransindex={}) == forvantat
    text = ' '.join(s.text for s in utfallsstycken(rb, p, t, gransindex={}))
    assert 'under metodens gräns' not in text
    if extra is None or inaktuell:
        assert '[VERIFIERA]' in text
    if inaktuell:
        assert 'inaktuellt underlag' in text


@pytest.mark.parametrize('antal', [None, 0, 2])
def test_fordelning_ar_lokalt_tillagg_och_andrar_inte_byrautfallet(lokalt_fall, antal):
    from riskanalys.dokument.utfall_v6 import utfallsstycken
    rb, p, t = lokalt_fall(0.3)
    stycken = utfallsstycken(rb, p, t, gransindex={}, fordelning=None if antal is None else {'P-A': antal})
    text = stycken[0].text
    assert 'byråövergripande' in text
    assert 'Testsårbarhet gäller' in text
    if antal is None:
        assert 'varav' not in text
    else:
        assert f'varav {antal} i tjänsten' in text


def test_undergransmeningen_visar_befintlig_metodgrans(lokalt_fall):
    from riskanalys.dokument.utfall_v6 import utfallsstycken
    rb, p, t = lokalt_fall(0.1)
    text = ' '.join(s.text for s in utfallsstycken(rb, p, t, gransindex={}))
    assert 'gräns på 20 %' in text
    assert 'automatiskt riskpåslag' in text


def test_skyddat_litet_komplement_far_lokalt_utfall(regelbas_v1, profil_fabrik):
    from riskanalys.dokument.utfall_v6 import utfallsstycken
    from riskanalys.profil.omfattning import harled_andelar
    from tester.fixturer.m2 import komplett_profil
    rb = regelbas_v1
    p = komplett_profil(rb, profil_fabrik(rb, {}))
    p = p.model_copy(update={'byra': p.byra.model_copy(update={'regelpaket': 'RP-RED-VG'})})
    falt = 'P-KUND.antal_riskbransch'
    u = p.uppgifter[falt].model_copy(update={'varde': 97})
    p = harled_andelar(p.model_copy(update={'uppgifter': {**p.uppgifter, falt: u}}), rb, frozenset({falt}))
    t = bedom(rb, valj(rb, p.byra.regelpaket, p.byra.datum, p.byra.lan), p).tjanster[0]
    stycken = utfallsstycken(rb, p, t, gransindex={})
    assert any('97 %' in s.text and 'S-KUND-01' in s.referenser for s in stycken)


def test_utfall_infogas_efter_ai_och_fore_lasta_stycken(v6underlag):
    from riskanalys.dokument.tjanstavsnitt_v6 import bygg_tjanstavsnitt_v6
    from riskanalys.dokument.utfall_v6 import utfallsstycken
    from riskanalys.dokument.lasta_v6 import lasta_stycken_v6
    from riskanalys.dokument.underlag import tjanster_med_avsnitt
    rb, p, b, resultat, _ = v6underlag
    id, t = tjanster_med_avsnitt(b)[0]
    a = bygg_tjanstavsnitt_v6(rb, p, t, resultat[id], id, gransindex={})
    utfall = utfallsstycken(rb, p, t, gransindex={})
    assert utfall
    sista_utfall = a.stycken.index(utfall[-1])
    assert all(a.stycken.index(s) > sista_utfall for s in lasta_stycken_v6(rb, p, t, 'sarbarheter', gransindex={}))
    assert max(i for i, s in enumerate(a.stycken) if s.proveniens == 'ai') < a.stycken.index(utfall[0])


@pytest.mark.parametrize('antal', [0, 2])
def test_bekraftad_intagsfordelning_fogas_lokalt_till_tjansten(regelbas_v1, profil_fabrik, antal):
    from riskanalys.dokument.tjanstavsnitt_v6 import bygg_tjanstavsnitt_v6
    from riskanalys.intag.modeller import IntagSvar
    from riskanalys.intag.svar import besvara
    from riskanalys.profil.omfattning import harled_andelar
    from tester.fixturer.m2 import DAG, PERIOD, komplett_profil
    rb = regelbas_v1
    p = komplett_profil(rb, profil_fabrik(rb, {}))
    p = p.model_copy(update={'byra': p.byra.model_copy(update={'regelpaket': 'RP-RED-VG'}),
        'uppgifter': {**p.uppgifter, 'P-GEO.antal_utland_transaktion': p.uppgifter['P-GEO.antal_utland_transaktion'].model_copy(update={'varde': 6})}})
    p = harled_andelar(p, rb, frozenset({'P-GEO.antal_utland_transaktion'}))
    p = besvara(rb, p, IntagSvar(falt='P-TJ.red01_antal_utland_transaktion', text=str(antal),
        kalla='Syntetisk fördelning', roll='Ansvarig', datum=DAG, period=PERIOD))
    t = bedom(rb, valj(rb, p.byra.regelpaket, p.byra.datum, p.byra.lan), p).tjanster[0]
    a = bygg_tjanstavsnitt_v6(rb, p, t, None, 'D-ARB.6.1', gransindex={})
    stycken = [s for s in a.stycken if f'varav {antal} i tjänsten' in s.text]
    assert stycken and all(s.proveniens == 'lokal' for s in stycken)
    assert all('byråövergripande' in s.text for s in stycken)
    assert 'S-GEO-01' in t.tillampade_sarbarheter


def test_obesvarade_valfria_fordelningar_skapar_ingen_b1_blockering(v6underlag):
    from riskanalys.dokument.arb_v6 import bygg_arb_v6
    from riskanalys.dokument.delskrivning import skriv_tjanst
    from riskanalys.dokument.leverantor import Testleverantor
    from riskanalys.dokument.rendering import har_verifiera
    from riskanalys.dokument.underlag import tjanster_med_avsnitt
    from riskanalys.granskning.kontroller import granska
    from riskanalys.profil.omfattning import harled_andelar
    from tester.fixturer.m2 import DAG, godkant_delsvar
    rb, p, _, _, h = v6underlag
    ids = {f.id for f in rb.falt.values() if f.id.startswith('P-TJ.') and
        f.id.endswith(('_antal_utland_transaktion', '_antal_utland_agare', '_antal_riskbransch', '_antal_kontant'))}
    assert len(ids) == 44
    upp = {k: u for k, u in p.uppgifter.items() if k not in ids}
    upp['P-GEO.antal_utland_transaktion'] = upp['P-GEO.antal_utland_transaktion'].model_copy(update={'varde': 6})
    p = harled_andelar(p.model_copy(update={'uppgifter': upp}), rb, frozenset({'P-GEO.antal_utland_transaktion'}))
    urval = valj(rb, p.byra.regelpaket, p.byra.datum, p.byra.lan)
    b = bedom(rb, urval, p)
    resultat = {id: skriv_tjanst(Testleverantor([godkant_delsvar(d, t) for d in ('hot', 'sarbarheter')]),
        rb, p, t, id, effort='medium', personnamn=(), spara=lambda *a: None, formatversion="D-ARB-tjanst-v6") for id, t in tjanster_med_avsnitt(b)}
    d = bygg_arb_v6(rb, p, b, resultat, h, analys=None)
    b1 = d.avsnitt_med_id()['D-ARB.B1']
    bas_rb = rb.model_copy(update={'falt': {id: f for id, f in rb.falt.items() if id not in ids}})
    bas_d = bygg_arb_v6(bas_rb, p, b, resultat, h, analys=None)
    assert d == bas_d
    assert har_verifiera(b1, p) == har_verifiera(bas_d.avsnitt_med_id()['D-ARB.B1'], p)
    assert not any(set(s.referenser) & ids for s in b1.stycken)
    fynd = granska(rb, urval, p, b, d, h, DAG, skrivresultat=resultat)
    bas_fynd = granska(bas_rb, urval, p, b, bas_d, h, DAG, skrivresultat=resultat)
    assert fynd == bas_fynd
