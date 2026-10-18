"""Flervalsfält i intaget: sorterad tuple av giltiga val, kryssrutor på webben och aldrig kritiskt eller blockerande."""
import threading

import pytest
from pydantic import ValidationError

from riskanalys.bedomning.scenarier import iakttagna_hot
from riskanalys.fel import RiskanalysFel
from riskanalys.intag.fragor import fragor
from riskanalys.intag.modeller import IntagSvar
from riskanalys.intag.svar import besvara
from riskanalys.intag.tackning import tackning
from riskanalys.intag.tjanst import Intagstjanst, profilrevision
from riskanalys.intag.webb import skapa_server
from riskanalys.profil.hantering import beskriv_uppgift, kontrollera_profil, kritiska_falt, visa_varde
from riskanalys.profil.lagring import las_profil, spara_profil
from riskanalys.regelverk.modeller import Falt
from riskanalys.regelverk.urval import valj
from riskanalys.regelverk.villkor import Faltdef, Kunskap, VillkorsFel, kontrollera_varde, tolka_villkor
from tester.fixturer.m2 import DAG
from tester.intag.test_webb import anrop

FALT_ID = 'P-TJ.red01_iakttagna_hot'
VAL = ('H-01', 'H-02', 'H-03')


def _falt(rb, **andringar):
    mall = rb.falt['P-TJ.red01_attest']
    data = dict(id=FALT_ID, typ='flerval', fraga='Vilka av tjänstens hot har byrån iakttagit?',
                varfor='Syntetiskt prov av flervalsfält.', val=VAL,
                intag=mall.intag.model_copy(update={'obligatorisk': False}))
    return Falt(**{**data, **andringar})


@pytest.fixture
def rb_flerval(rb_intag):
    return rb_intag.model_copy(update={'falt': {**rb_intag.falt, FALT_ID: _falt(rb_intag)}})


def _svar(text, **andringar):
    return IntagSvar(**{**dict(falt=FALT_ID, text=text, kalla='Syntetisk incidentlogg', roll='Ansvarig', datum=DAG),
                        **andringar})


def _tjanst(rb):
    return next(t for t in rb.tjanster.values() if t.erbjuds_falt == 'P-TJ.red01_erbjuds')


def test_flerval_sparas_som_sorterad_unik_tuple(rb_flerval, klar):
    p = besvara(rb_flerval, klar, _svar('H-03, H-01,H-03'))
    assert p.uppgifter[FALT_ID].varde == ('H-01', 'H-03')
    assert p.ar_bekraftad(FALT_ID)
    assert p.faltvarden()[FALT_ID].kunskap is Kunskap.KAND


def test_flerval_overlever_lagring_och_kontroll(tmp_path, rb_flerval, klar):
    p = besvara(rb_flerval, klar, _svar('H-02,H-01'))
    spara_profil(tmp_path, p)
    last = las_profil(tmp_path)
    assert last.uppgifter[FALT_ID].varde == ('H-01', 'H-02')
    assert profilrevision(last) == profilrevision(p)
    kontrollera_profil(last, rb_flerval)


def test_okant_val_avvisas_med_svenskt_fel(rb_flerval, klar):
    with pytest.raises(RiskanalysFel, match='Välj inget, ett eller flera av: H-01, H-02, H-03'):
        besvara(rb_flerval, klar, _svar('H-01,H-FINNS-INTE'))


def test_tomt_val_sparas_som_inga_iakttagna(rb_flerval, klar):
    p = besvara(rb_flerval, klar, _svar(''))
    u = p.uppgifter[FALT_ID]
    assert u.varde == () and p.ar_bekraftad(FALT_ID)
    assert iakttagna_hot(_tjanst(rb_flerval), p.faltvarden(), frozenset()) == frozenset()
    assert visa_varde(rb_flerval.falt[FALT_ID], u.varde) == 'inga'


def test_motorn_laser_sparat_flerval(rb_flerval, klar):
    p = besvara(rb_flerval, klar, _svar('H-02,H-01'))
    assert iakttagna_hot(_tjanst(rb_flerval), p.faltvarden(), frozenset()) == {'H-01', 'H-02'}


def test_cli_visar_kommaseparerade_varden(rb_flerval, klar):
    p = besvara(rb_flerval, klar, _svar('H-02,H-01'))
    f = rb_flerval.falt[FALT_ID]
    assert visa_varde(f, p.uppgifter[FALT_ID].varde) == 'H-01, H-02'
    assert beskriv_uppgift(f, p.uppgifter[FALT_ID]).startswith('H-01, H-02 (bekräftad')


@pytest.mark.parametrize('varde', [(), ('H-01',), ('H-01', 'H-03'), ['H-02']])
def test_kontrollera_varde_godtar_giltiga_flerval(varde):
    kontrollera_varde(Faltdef(FALT_ID, 'flerval', VAL), varde)


@pytest.mark.parametrize('varde', ['H-01', ('H-01', 'H-01'), ('H-09',), (1,), None])
def test_kontrollera_varde_avvisar_ogiltiga_flerval(varde):
    with pytest.raises(VillkorsFel, match='passar inte typen flerval'):
        kontrollera_varde(Faltdef(FALT_ID, 'flerval', VAL), varde)


@pytest.mark.parametrize('andring', [{'kritisk': True}, 'obligatorisk'])
def test_flerval_kan_aldrig_vara_kritiskt(rb_intag, andring):
    if andring == 'obligatorisk':
        andring = {'intag': rb_intag.falt['P-TJ.red01_attest'].intag.model_copy(update={'obligatorisk': True})}
    with pytest.raises(ValidationError, match='flerval'):
        _falt(rb_intag, **andring)


def test_flerval_visas_bara_nar_tjansten_erbjuds_och_blir_inte_kritiskt(rb_intag, klar, tom):
    gating = {'falt': 'P-TJ.red01_erbjuds', 'op': '==', 'varde': True}
    rb = rb_intag.model_copy(update={'falt': {**rb_intag.falt, FALT_ID: _falt(rb_intag, kritisk_om=gating)}})
    urval = valj(rb, klar.byra.regelpaket, klar.byra.datum, klar.byra.lan)
    assert FALT_ID not in kritiska_falt(rb, urval, klar)
    assert FALT_ID in {q.falt.id for q in fragor(rb, klar)}
    ej = tom.model_copy(update={'uppgifter': {**tom.uppgifter, 'P-TJ.red01_erbjuds': klar.uppgifter['P-TJ.red01_erbjuds']
                                               .model_copy(update={'varde': False})}})
    assert FALT_ID not in {q.falt.id for q in fragor(rb, ej)}
    with pytest.raises(RiskanalysFel, match='inte tillämplig'):
        besvara(rb, ej, _svar('H-01'))


def test_flerval_far_inte_anvandas_i_villkor(rb_flerval):
    with pytest.raises(VillkorsFel, match='flerval'):
        tolka_villkor({'falt': FALT_ID, 'op': 'finns'}, rb_flerval.faltdefinitioner())


@pytest.mark.parametrize('svar', [None, 'okänt'])
def test_obesvarat_eller_okant_flerval_blockerar_inte(rb_flerval, klar, svar):
    p = klar if svar is None else besvara(rb_flerval, klar, _svar('', status='okänt', motivering='Loggen gås igenom.'))
    t = tackning(rb_flerval, p)
    assert t.komplett and FALT_ID not in t.saknade
    urval = valj(rb_flerval, p.byra.regelpaket, p.byra.datum, p.byra.lan)
    assert FALT_ID not in kritiska_falt(rb_flerval, urval, p)
    fraga = next(q for q in fragor(rb_flerval, p) if q.falt.id == FALT_ID)
    assert not fraga.falt.intag.obligatorisk


def test_exponering_tar_inte_med_flerval(rb_flerval, klar):
    from riskanalys.analys.exponering import exponeringsposter
    p = besvara(rb_flerval, klar, _svar('H-01'))
    tjanst = _tjanst(rb_flerval).id
    poster = exponeringsposter(rb_flerval, p, tjanst, set(p.uppgifter))
    assert FALT_ID not in {f for f, _, _ in poster}


@pytest.fixture
def webb_flerval(tmp_path, monkeypatch, rb_flerval, klar):
    monkeypatch.setenv('RISKANALYS_DATA', str(tmp_path))
    t = Intagstjanst('syntetisk', rb_flerval)
    s = skapa_server(t)
    trad = threading.Thread(target=s.serve_forever, daemon=True)
    trad.start()
    t.skapa('Västra Götaland', False, DAG, 'Syntetisk källa', 'Ansvarig')
    spara_profil(t.mapp, klar)
    yield s, t
    s.shutdown()
    s.server_close()
    trad.join(timeout=2)


def _post(s, t, rutor, **extra):
    data = dict(csrf=s.csrf, revision=profilrevision(t.profil()), falt=FALT_ID, status='bekräftad',
                kalla='Syntetisk incidentlogg', roll='Ansvarig', datum=str(DAG), **extra)
    data.update({'flerval:' + v: 'ja' for v in rutor})
    return anrop(s, 'svar', data)


def test_webben_visar_kryssrutor_med_hotnamn(webb_flerval, rb_flerval):
    s, _ = webb_flerval
    status, html, _ = anrop(s, '?falt=' + FALT_ID)
    assert status == 200
    for v in VAL:
        assert f'name="flerval:{v}" type="checkbox" value="ja"' in html
        assert rb_flerval.hot[v].namn in html
    assert '<select id="text"' not in html


def test_webben_tar_emot_flera_varden_och_visar_dem_ikryssade(webb_flerval):
    s, t = webb_flerval
    assert _post(s, t, ('H-03', 'H-01'))[0] == 200
    assert t.profil().uppgifter[FALT_ID].varde == ('H-01', 'H-03')
    _, html, _ = anrop(s, '?falt=' + FALT_ID)
    assert 'name="flerval:H-01" type="checkbox" value="ja" checked' in html
    assert 'name="flerval:H-02" type="checkbox" value="ja">' in html
    _, oversikt, _ = anrop(s, '?oversikt=1')
    assert 'H-01, H-03' in oversikt


def test_webben_sparar_tomt_val(webb_flerval):
    s, t = webb_flerval
    assert _post(s, t, ())[0] == 200
    u = t.profil().uppgifter[FALT_ID]
    assert u.varde == () and u.status == 'bekräftad'


def test_webben_avvisar_okant_val_och_bevarar_kryss(webb_flerval):
    s, t = webb_flerval
    status, html, _ = _post(s, t, ('H-01', 'H-FINNS-INTE'))
    assert status == 400 and 'Välj bara alternativ ur listan' in html
    assert 'name="flerval:H-01" type="checkbox" value="ja" checked' in html
    assert t.profil().uppgifter.get(FALT_ID) is None or t.profil().uppgifter[FALT_ID].status == 'saknas'


def test_webben_godtar_alla_alternativ_trots_faltgrans(webb_flerval, rb_intag):
    s, t = webb_flerval
    alla = rb_intag.tjanster[_tjanst(rb_intag).id].hot
    rb = t.rb.model_copy(update={'falt': {**t.rb.falt, FALT_ID: _falt(rb_intag, val=alla)}})
    t.rb = rb
    status, _, _ = _post(s, t, alla, underlag='eget', motivering='', period_fran='', period_till='')
    assert status == 200
    assert t.profil().uppgifter[FALT_ID].varde == tuple(sorted(alla))
