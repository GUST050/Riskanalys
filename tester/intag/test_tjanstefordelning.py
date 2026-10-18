"""Frivillig lokal tjänsteexponering med giltiga baser, aldrig en ny motorfaktor."""
from types import SimpleNamespace

import pytest

from riskanalys.fel import RiskanalysFel
from riskanalys.intag.fragor import fragor
from riskanalys.intag.kvalitet import kvalitetsbrister
from riskanalys.intag.modeller import IntagSvar
from riskanalys.intag.svar import besvara
from riskanalys.intag.tackning import tackning
from riskanalys.profil.modeller import Period, Uppgift
from tester.fixturer.m2 import DAG, PERIOD

FAKTOR = 'P-GEO.antal_utland_transaktion'
FALT = 'P-TJ.red04_antal_utland_transaktion'
TJ = 'T-RED-04'


def andra(p, id, **kw):
    u = p.uppgifter.get(id, Uppgift()).model_copy(update=kw)
    return p.model_copy(update={'uppgifter': {**p.uppgifter, id: u}})


@pytest.fixture
def fordelningsprofil(klar):
    p = andra(klar, FAKTOR, varde=6)
    return andra(p, 'P-TJ.red04_erbjuds', varde=True)


def spara(rb, p, antal=2, **kw):
    return besvara(rb, p, IntagSvar(falt=FALT, text=str(antal), kalla='Syntetisk tjänstestatistik',
        roll='Ansvarig', datum=DAG, period=PERIOD, **kw))


def fordelning(rb, p, tjanst=TJ):
    from riskanalys.intag.fordelning import tjanstefordelning
    return tjanstefordelning(rb, p, tjanst)


def test_falt_ar_frivilliga_periodbundna_och_utanfor_ai(rb_intag):
    suffix = ('_antal_utland_transaktion', '_antal_utland_agare', '_antal_riskbransch', '_antal_kontant')
    nya = [f for f in rb_intag.falt.values() if f.id.startswith('P-TJ.') and f.id.endswith(suffix)]
    assert len(nya) == 4 * len(rb_intag.tjanster)
    for f in nya:
        assert f.typ == 'heltal' and f.periodkrav and not f.kritisk
        assert f.intag and not f.intag.obligatorisk
        assert f.intag.grund == 'metodval'
        assert f.intag.avsnitt == ('D-ARB.5',)
        assert set(f.intag.kallor) == {'SRC-14FS-2024-11', 'SRC-TS-2026-14', 'SRC-LST-SK-3647-2026'}
    assert not set(f.id for f in nya) & set(rb_intag.tillatelselistor['risk_per_tjanst'].falt)


def test_aktiv_fraga_med_dynamiskt_antal_och_okand_annan_tjanst(rb_intag, fordelningsprofil):
    p = andra(fordelningsprofil, 'P-TJ.red07_erbjuds', status='saknas', varde=None)
    q = next(q for q in fragor(rb_intag, p) if q.falt.id == FALT)
    assert 'byråns 6 kunder' in q.falt.fraga
    assert rb_intag.tjanster[TJ].namn in q.falt.fraga
    assert not q.falt.intag.obligatorisk


@pytest.mark.parametrize('fall', ['en_tjanst', 'noll', 'okand_faktor', 'inaktuell_faktor', 'egen_okand', 'egen_nej', 'fel_period'])
def test_fraga_och_sparande_kraver_aktuell_bekraftad_aktivering(rb_intag, fordelningsprofil, fall):
    p = fordelningsprofil
    if fall == 'en_tjanst':
        for t in rb_intag.tjanster.values():
            if t.id != TJ:
                p = andra(p, t.erbjuds_falt, varde=False)
    elif fall == 'noll': p = andra(p, FAKTOR, varde=0)
    elif fall == 'okand_faktor': p = andra(p, FAKTOR, status='saknas')
    elif fall == 'inaktuell_faktor': p = andra(p, FAKTOR, inaktuell=True)
    elif fall == 'egen_okand': p = andra(p, 'P-TJ.red04_erbjuds', status='saknas')
    elif fall == 'egen_nej': p = andra(p, 'P-TJ.red04_erbjuds', varde=False)
    else: p = andra(p, FAKTOR, period=Period(fran=PERIOD.fran, till=PERIOD.till.replace(day=29)))
    assert FALT not in {q.falt.id for q in fragor(rb_intag, p)}
    with pytest.raises(RiskanalysFel):
        spara(rb_intag, p)


def test_saknat_svar_ger_varken_varav_saknad_sparr_eller_preliminar_motor(rb_intag, klar):
    from riskanalys.bedomning.motor import bedom
    from riskanalys.regelverk.urval import valj
    p = andra(klar, FAKTOR, varde=6)
    p = p.model_copy(update={'uppgifter': {k: u for k, u in p.uppgifter.items() if not k.startswith('P-TJ.') or not k.endswith(('_antal_utland_transaktion', '_antal_utland_agare', '_antal_riskbransch', '_antal_kontant'))}})
    from riskanalys.profil.omfattning import harled_andelar
    p = harled_andelar(p, rb_intag, frozenset({FAKTOR}))
    assert tackning(rb_intag, p).komplett
    assert fordelning(rb_intag, p, 'T-RED-01') == {}
    b = bedom(rb_intag, valj(rb_intag, p.byra.regelpaket, p.byra.datum, p.byra.lan), p)
    assert b.status == 'slutlig'


@pytest.mark.parametrize('antal', [0, 2, 6])
def test_sparat_bekraftat_antal_returneras_per_tjanst(rb_intag, fordelningsprofil, antal):
    p = spara(rb_intag, fordelningsprofil, antal)
    assert fordelning(rb_intag, p) == {FAKTOR: antal}
    assert fordelning(rb_intag, p, 'T-RED-02') == {}


@pytest.mark.parametrize(('antal', 'tjanstbas'), [(7, 10), (5, 4), (-1, 10)])
def test_motsagelse_avvisas_vid_sparande_och_handredigering(rb_intag, fordelningsprofil, antal, tjanstbas):
    p = andra(fordelningsprofil, 'P-TJ.red04_antal_kunder', varde=tjanstbas)
    with pytest.raises(RiskanalysFel): spara(rb_intag, p, antal)
    p = andra(p, FALT, varde=antal, status='bekräftad', kalla='Syntetisk', bekraftad_av='roll:Ansvarig', datum=DAG, period=PERIOD)
    assert any(FALT in h for h in kvalitetsbrister(rb_intag, p))
    if antal >= 0: assert any('fler kunder' in h and 'rätta antalet' in h for h in kvalitetsbrister(rb_intag, p))
    assert fordelning(rb_intag, p) == {}


@pytest.mark.parametrize('fall', ['period', 'utan_period', 'bool', 'float', 'inaktuell', 'okand', 'utan_kalla', 'utan_roll', 'utan_datum', 'andrad_faktor', 'andrad_bas', 'andrat_erbjudande', 'andrat_svar'])
def test_gammalt_eller_handandrat_svar_blir_inte_giltigt_varav(rb_intag, fordelningsprofil, fall):
    p = spara(rb_intag, fordelningsprofil)
    if fall == 'andrad_faktor': p = andra(p, FAKTOR, varde=7)
    elif fall == 'andrad_bas': p = andra(p, 'P-TJ.red04_antal_kunder', varde=11)
    elif fall == 'andrat_erbjudande': p = andra(p, 'P-TJ.red04_erbjuds', varde=False)
    else:
        kw = {'period': {'period': Period(fran=PERIOD.fran, till=PERIOD.till.replace(day=29))},
            'utan_period': {'period': None}, 'bool': {'varde': True}, 'float': {'varde': 2.0},
            'inaktuell': {'inaktuell': True}, 'okand': {'status': 'föreslagen'},
            'utan_kalla': {'kalla': ''}, 'utan_roll': {'bekraftad_av': ''}, 'utan_datum': {'datum': None},
            'andrat_svar': {'varde': 3}}[fall]
        p = andra(p, FALT, **kw)
    assert fordelning(rb_intag, p) == {}


@pytest.mark.parametrize('id', [FAKTOR, 'P-KUND.antal_aktiva', 'P-TJ.red04_antal_kunder', 'P-TJ.red04_erbjuds'])
def test_basandring_i_intaget_markerar_gammal_fordelning_inaktuell(rb_intag, fordelningsprofil, id):
    p = spara(rb_intag, fordelningsprofil)
    f = rb_intag.falt[id]
    u = p.uppgifter[id]
    text = 'nej' if f.typ == 'bool' else str(u.varde + 1)
    p = besvara(rb_intag, p, IntagSvar(falt=id, text=text, kalla='Ny syntetisk bas', roll='Ansvarig', datum=DAG, period=u.period))
    assert p.uppgifter[FALT].inaktuell
    assert fordelning(rb_intag, p) == {}


def test_overlappande_tjanster_summeras_inte(rb_intag, fordelningsprofil):
    p = spara(rb_intag, fordelningsprofil, 6)
    p = besvara(rb_intag, p, IntagSvar(falt='P-TJ.red01_antal_utland_transaktion', text='6', kalla='Syntetisk', roll='Ansvarig', datum=DAG, period=PERIOD))
    assert fordelning(rb_intag, p) == {FAKTOR: 6}
    assert fordelning(rb_intag, p, 'T-RED-01') == {FAKTOR: 6}
    assert not kvalitetsbrister(rb_intag, p)


def test_frivillig_fraga_nas_i_oversikt_och_direkt_lank(rb_intag, fordelningsprofil, tmp_path, monkeypatch):
    from riskanalys.intag.vyer import fragesida, oversikt
    from riskanalys.intag.tjanst import Intagstjanst
    from riskanalys.profil.lagring import spara_profil
    spara_profil(tmp_path, fordelningsprofil)
    monkeypatch.setattr('riskanalys.intag.tjanst.byramapp', lambda _: tmp_path)
    t = Intagstjanst('syntetisk', rb_intag)
    s = SimpleNamespace(tjanst=t, prefix='/prov/', csrf='syntetisk', utkast=None, kompletteringar=())
    html = oversikt(s)
    assert FALT in html and 'byråns 6 kunder' in html
    assert 'frivilligt' in html
    sida = fragesida(s, FALT)
    assert 'byråns 6 kunder' in sida and 'valfritt' in sida.lower()


def test_gamla_uppgifters_serialisering_far_ingen_ny_nollmetadata():
    assert 'underlagsbindning' not in Uppgift().model_dump()


def test_irrelevant_tredje_tjansts_erbjudande_bevarar_giltigt_svar(rb_intag, fordelningsprofil):
    p = spara(rb_intag, fordelningsprofil)
    p = besvara(rb_intag, p, IntagSvar(falt='P-TJ.skatt01_erbjuds', text='nej', kalla='Syntetisk', roll='Ansvarig', datum=DAG))
    assert not p.uppgifter[FALT].inaktuell
    assert fordelning(rb_intag, p) == {FAKTOR: 2}


def test_sista_andra_tjansten_inaktiverar_utan_ateranvandning(rb_intag, fordelningsprofil):
    p = fordelningsprofil
    for t in rb_intag.tjanster.values():
        if t.id not in (TJ, 'T-RED-01'):
            p = andra(p, t.erbjuds_falt, varde=False)
    p = spara(rb_intag, p)
    for text in ('nej', 'ja'):
        p = besvara(rb_intag, p, IntagSvar(falt='P-TJ.red01_erbjuds', text=text, kalla='Syntetisk', roll='Ansvarig', datum=DAG))
        assert p.uppgifter[FALT].inaktuell
        assert fordelning(rb_intag, p) == {}


@pytest.mark.parametrize('basfel', ['okant', 'inaktuell', 'utan_period', 'annan_period', 'utan_kalla', 'for_stor'])
def test_ogiltig_tjanstbas_kan_inte_bekrafta_fordelning(rb_intag, fordelningsprofil, basfel):
    kw = {'okant': {'status': 'föreslagen'}, 'inaktuell': {'inaktuell': True},
        'utan_period': {'period': None}, 'annan_period': {'period': Period(fran=PERIOD.fran, till=PERIOD.till.replace(day=29))},
        'utan_kalla': {'kalla': ''}, 'for_stor': {'varde': 101}}[basfel]
    p = andra(fordelningsprofil, 'P-TJ.red04_antal_kunder', **kw)
    with pytest.raises(RiskanalysFel):
        spara(rb_intag, p)
    assert fordelning(rb_intag, p) == {}


def test_historiska_profilbytes_och_revision_bevaras():
    import hashlib
    from riskanalys.profil.lagring import profilrevision
    from riskanalys.profil.modeller import Profil
    historisk = ('{"byra":{"id":"syntetisk","regelpaket":"RP-RED-VG","datum":"2026-10-10","lan":"Västra Götaland"},'
        '"uppgifter":{"P-A":{"varde":2,"status":"bekräftad","kalla":"Syntetisk källa","datum":"2026-10-10",'
        '"bekraftad_av":"roll:Ansvarig","motivering":null,"period":null,"harledd":false,"inaktuell":false}}}')
    profil = Profil.model_validate_json(historisk)
    assert profil.model_dump_json() == historisk
    assert profilrevision(profil) == hashlib.sha256(historisk.encode()).hexdigest()


def test_bindningen_kraver_sha256_och_foljer_med_lokal_lagring(rb_intag, fordelningsprofil, tmp_path):
    from pydantic import ValidationError
    from riskanalys.profil.lagring import las_profil, spara_profil
    with pytest.raises(ValidationError):
        Uppgift(underlagsbindning='privat fritext')
    p = spara(rb_intag, fordelningsprofil)
    spara_profil(tmp_path, p)
    omlast = las_profil(tmp_path)
    assert omlast == p
    assert fordelning(rb_intag, omlast) == {FAKTOR: 2}


@pytest.mark.parametrize('fall', ['obunden_nolla', 'inaktuell', 'overstor', 'handandrad', 'giltig'])
def test_bara_giltig_fordelning_ateranvands_i_lokalt_utkast_och_belagg(rb_intag, fordelningsprofil, fall):
    from riskanalys.analys.modeller import Analysbindning
    from riskanalys.analys.utkast import forifyll_analys
    from riskanalys.bedomning.motor import bedom
    from riskanalys.dokument.intagsunderlag import med_intagsunderlag
    from riskanalys.dokument.modeller import Avsnitt, Dokument
    from riskanalys.regelverk.urval import valj
    p = fordelningsprofil
    if fall == 'obunden_nolla':
        p = andra(p, FALT, varde=0, status='bekräftad', kalla='Syntetisk', datum=DAG, bekraftad_av='roll:Ansvarig', period=PERIOD)
    else:
        p = spara(rb_intag, p)
        if fall == 'inaktuell': p = andra(p, FALT, inaktuell=True)
        elif fall == 'overstor': p = andra(p, FALT, varde=7)
        elif fall == 'handandrad': p = andra(p, FALT, varde=3)
    b = bedom(rb_intag, valj(rb_intag, p.byra.regelpaket, p.byra.datum, p.byra.lan), p)
    bindning = Analysbindning(byra=p.byra.id, profilrevision='syntetisk', bedomningsmanifest='syntetisk',
        utkastmanifest='syntetisk', regelbas=rb_intag.kontrollsumma, kallunderlag='syntetisk',
        historik='syntetisk', bedomningsdatum=p.byra.datum, modell='syntetisk')
    a = forifyll_analys(rb_intag, p, b, bindning)
    assert any(FALT in belagg.profilfalt for belagg in a.belagg) == (fall == 'giltig')
    t = next(t for t in a.tjanster if t.tjanst == TJ)
    assert ('profil:' + FALT in t.exponeringsbelagg) == (fall == 'giltig')
    assert (rb_intag.falt[FALT].fraga in t.exponering) == (fall == 'giltig')
    tomt = Dokument(id='D-ARB', titel='Syntetiskt', avsnitt=(Avsnitt(id='D-ARB.5', rubrik='Underlag', kalla='lokal', stycken=()),))
    d = med_intagsunderlag(tomt, rb_intag, p, b)
    assert any(FALT in s.referenser for a in d.avsnitt for s in a.stycken) == (fall == 'giltig')


@pytest.mark.parametrize('fall', ['obundet', 'handandrat', 'basandrat', 'giltigt', 'saknas'])
def test_oversiktens_status_skiljer_ogiltig_ny_fordelning_fran_bekraftat_svar(
        rb_intag, fordelningsprofil, tmp_path, monkeypatch, fall):
    from riskanalys.intag.modeller import Intagsfraga
    from riskanalys.intag.tjanst import Intagstjanst
    from riskanalys.intag.vyer import oversikt
    from riskanalys.profil.lagring import spara_profil
    p = fordelningsprofil
    if fall in ('handandrat', 'basandrat', 'giltigt'):
        p = spara(rb_intag, p)
    if fall == 'handandrat': p = andra(p, FALT, varde=3)
    elif fall == 'basandrat': p = andra(p, FAKTOR, varde=7)
    elif fall == 'saknas':
        p = p.model_copy(update={'uppgifter': {k: u for k, u in p.uppgifter.items() if k != FALT}})
    spara_profil(tmp_path, p)
    monkeypatch.setattr('riskanalys.intag.tjanst.byramapp', lambda _: tmp_path)
    t = Intagstjanst('syntetisk', rb_intag)
    s = SimpleNamespace(tjanst=t, prefix='/prov/', csrf='syntetisk', utkast=None, kompletteringar=())
    q = next(q for q in fragor(rb_intag, p) if q.falt.id == FALT)
    assert q.besvarad == (fall == 'giltigt')
    # Äldre fält behåller den befintliga visningen även när frågeflaggan skiljer sig.
    gammalt = Intagsfraga(rb_intag.falt['P-ORG.namn'], False)
    html = oversikt(s, qs=(q, gammalt))
    rad = next(rad for rad in html.split('<tr>') if 'falt=' + FALT in rad)
    gammal_rad = next(rad for rad in html.split('<tr>') if 'falt=P-ORG.namn' in rad)
    assert '<small>bekräftad;' in gammal_rad
    if fall == 'giltigt':
        assert '<small>bekräftad (frivilligt inför utkast)' in rad
    elif fall == 'saknas':
        assert '<small>saknas (frivilligt inför utkast)' in rad
        assert 'Behöver bekräftas på nytt' not in rad
    else:
        assert '<small>Behöver bekräftas på nytt (frivilligt inför utkast)' in rad
        assert '<small>bekräftad' not in rad
