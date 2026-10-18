"""B1:s delrubriker i v6 ingår i dokumentmodellen.

Rubrikerna skrivs av byggaren i byggarens ordning, sakgranskas och binds av avsnittets
kontrollsumma och av v6-återbygget. De räknas till bilagan, inte till huvudtexten.
Historiska v5- och v5.1-dokument får inga rubriker och behåller sina summor.
"""
import re

import docx
import pytest

from riskanalys.dokument import arb_v6
from riskanalys.dokument.arb_v6 import bygg_arb_v6
from riskanalys.dokument.modeller import Dokument, Textstycke
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.faststallelse.sakgranskning import galler_sakgranskning, registrera_sakgranskning
from riskanalys.lagring.kontrollsumma import for_text
from tester.enhet.test_arb_v5_1 import underlag  # noqa: F401  (fixtur)
from tester.enhet.test_arb_v6 import v6underlag  # noqa: F401  (fixtur)
from tester.enhet.test_lokalt_dokument_v6 import lokal  # noqa: F401  (fixtur)
from tester.fixturer.m2 import DAG

B1 = 'D-ARB.B1'
MED_ANALYS = ('Profiluppgifter', 'Källversioner', 'Omfattningsregel', 'Gemensamma resonemang per tjänst',
              'Källbunden kontrollräckvidd', 'Lokal analys och belägg', 'Scenarioreferenser',
              'Delanalyser och analysblock', 'Kompletteringspunkter', 'Beräkningsunderlag',
              'Regelvis sakkunnigstatus', 'Källregister')
UTAN_ANALYS = ('Profiluppgifter', 'Källversioner', 'Omfattningsregel', 'Gemensamma resonemang per tjänst',
               'Källbunden kontrollräckvidd',
               'Lokal analys och belägg', 'Beräkningsunderlag', 'Regelvis sakkunnigstatus', 'Källregister')


def _analysblock(s, rb):
    return s.text.startswith('Delanalysreferens: ') or re.search(r', analysblock \d+: ', s.text) is not None


# Oberoende orakel: vad som hör till varje del, utläst ur stycket och inte ur byggarens indelning.
TILLHOR = {
    'Profiluppgifter': lambda s, rb: len(s.referenser) == 1 and s.referenser[0].startswith('P-'),
    'Källversioner': lambda s, rb: len(s.referenser) == 1 and s.referenser[0] in rb.kallor
        and s.text.startswith(s.referenser[0] + ': '),
    'Omfattningsregel': lambda s, rb: s.text.startswith('Omfattningsregel '),
    'Gemensamma resonemang per tjänst': lambda s, rb: 'D-ARB.5' in s.referenser,
    'Källbunden kontrollräckvidd': lambda s, rb: s.text.startswith('Källbunden kontrollräckvidd ') or ' – ' in s.text,
    'Lokal analys och belägg': lambda s, rb: s.text.startswith(('Lokal analysrevision ', 'Fryst analysstatus:', 'Belägg ')),
    'Scenarioreferenser': lambda s, rb: s.text.startswith('Scenarioreferens: '),
    'Analysblock': _analysblock,
    'Delanalyser och analysblock': _analysblock,
    'Kompletteringspunkter': lambda s, rb: s.text.startswith('Kompletteringspunkt: '),
    'Beräkningsunderlag': lambda s, rb: s.text.startswith('Beräkningsunderlag för '),
    'Regelvis sakkunnigstatus': lambda s, rb: s.text.startswith(('Regelvis sakkunnigstatus: ', 'Förslag till sakkunnig, M1')),
    'Källregister': lambda s, rb: s.text.startswith('Källregister ['),
}


def _b1(d):
    return d.avsnitt_med_id()[B1]


def _med_b1(d, ny):
    return d.model_copy(update={'avsnitt': tuple(ny if a.id == B1 else a for a in d.avsnitt)})


def _delar(b1):
    """{rubrik: (start, slut)} enligt modellens underrubriker."""
    starter = [u.fore_stycke for u in b1.underrubriker]
    return {u.rubrik: (start, slut) for u, start, slut in zip(b1.underrubriker, starter, (*starter[1:], len(b1.stycken)))}


def _andrade(b1):
    """Ändrad, flyttad och borttagen rubrik; texten och tabellerna är oförändrade."""
    rubriker = b1.underrubriker
    flyttad = rubriker[1].model_copy(update={'fore_stycke': rubriker[1].fore_stycke + 1})
    return {
        'ändrad': b1.model_copy(update={'underrubriker': (rubriker[0].model_copy(update={'rubrik': 'Ändrad rubrik'}), *rubriker[1:])}),
        'flyttad': b1.model_copy(update={'underrubriker': (rubriker[0], flyttad, *rubriker[2:])}),
        'borttagen': b1.model_copy(update={'underrubriker': rubriker[:-1]}),
    }


@pytest.fixture
def dokument(v6underlag, lokal):
    return bygg_arb_v6(*v6underlag, analys=lokal)


@pytest.mark.parametrize('med_analys', [True, False])
def test_byggaren_skriver_b1_delarna_som_underrubriker_pa_ratt_stycken(v6underlag, lokal, med_analys):
    rb, _, b, _, _ = v6underlag
    d = bygg_arb_v6(*v6underlag, analys=lokal if med_analys else None)
    b1 = _b1(d)
    assert tuple(u.rubrik for u in b1.underrubriker) == (MED_ANALYS if med_analys else UTAN_ANALYS)
    assert set(MED_ANALYS) | {'Analysblock'} == set(arb_v6.B1_DELRUBRIKER)
    # Rubrikerna täcker hela bilagan och varje stycke står under sin egen dels rubrik.
    assert b1.underrubriker[0].fore_stycke == 0
    for rubrik, (start, slut) in _delar(b1).items():
        assert start < slut
        felplacerade = [s.text[:60] for s in b1.stycken[start:slut] if not TILLHOR[rubrik](s, rb)]
        assert not felplacerade, (rubrik, felplacerade)
    # Varje tjänsts utfallstabell hör till beräkningsdelen och står vid tjänstens eget stycke.
    start, slut = _delar(b1)['Beräkningsunderlag']
    avsnitt_for = {t.tjanst: id for id, t in tjanster_med_avsnitt(b)}
    utfall = [t for t in b1.tabeller if t.id.endswith('-utfall')]
    assert len(utfall) == len(avsnitt_for) == len(b1.tabeller)
    for tabell in utfall:
        assert start <= tabell.fore_stycke < slut
        assert b1.stycken[tabell.fore_stycke].referenser == [avsnitt_for[tabell.id.removesuffix('-utfall')]]
    if not med_analys:
        # Maskinskrivna lokala utfall kan delas även utan ett författat analysobjekt.
        delar = _delar(b1)
        start, slut = delar['Gemensamma resonemang per tjänst']
        assert delar['Omfattningsregel'][1] == start
        assert slut == delar['Källbunden kontrollräckvidd'][0]
        gemensamma = d.avsnitt_med_id()['D-ARB.5'].stycken
        kartlagda = set()
        for s in b1.stycken[start:slut]:
            tjansteavsnitt = set(s.referenser) & set(avsnitt_for.values())
            assert len(tjansteavsnitt) == 1
            id, = tjansteavsnitt
            kartlagda.add(id)
            assert s.text.startswith(d.avsnitt_med_id()[id].rubrik + '. ')
            nummer = re.search(r'gemensamt resonemang (\d+)\.$', s.text)
            assert nummer is not None
            traffar = [g for g in gemensamma if g.text.startswith(f'Gemensamt resonemang {nummer[1]}. ')]
            assert len(traffar) == 1
            assert set(s.referenser) & set(rb.sarbarheter)
            assert set(s.referenser) - {id, 'D-ARB.5'} <= set(traffar[0].referenser)
            assert any('D-ARB.5' in stycke.referenser and id in stycke.referenser
                       for stycke in d.avsnitt_med_id()[id].stycken)
        assert kartlagda == set(avsnitt_for.values())
    # Positionerna håller modellens validering även efter lagring.
    assert Dokument.model_validate_json(d.model_dump_json()) == d


@pytest.mark.parametrize('med_analys', [True, False])
def test_m1_forslaget_star_under_b1s_sakkunnigdel_efter_statusstycket(v6underlag, lokal, med_analys):
    b1 = _b1(bygg_arb_v6(*v6underlag, analys=lokal if med_analys else None))
    start, slut = _delar(b1)['Regelvis sakkunnigstatus']
    delen = [s.text for s in b1.stycken[start:slut]]
    assert delen[0].startswith('Regelvis sakkunnigstatus: ')
    assert [t.startswith('Förslag till sakkunnig, M1 (inte beslutat):') for t in delen] == [False, True]


def test_m1_forslaget_visas_aldrig_utanfor_b1_med_lokal_analys(v6underlag, lokal):
    d = bygg_arb_v6(*v6underlag, analys=lokal)
    for a in d.avsnitt:
        if a.id != B1:
            texter = [*(s.text for s in a.stycken), *(c.text for t in a.tabeller for r in t.rader for c in r.celler)]
            assert not [t for t in texter if 'Förslag till sakkunnig, M1' in t or 'ingen reduktion utan belagd' in t], a.id


@pytest.mark.parametrize('med_analys', [False, True])
@pytest.mark.parametrize('med_m1_kalla', [False, True])
def test_m1_byggs_och_granskas_utan_okand_kalla(v6underlag, lokal, med_analys, med_m1_kalla):
    """Minimal modellvariant av äldre källkatalog, inte hela den frysta regelbasen 1.5.0."""
    from riskanalys.granskning.kontroller import granska
    from riskanalys.regelverk.urval import valj
    rb, p, b, resultat, h = v6underlag
    kallor = dict(rb.kallor)
    if not med_m1_kalla:
        del kallor['SRC-LST-GOR-ARB']
    variant = rb.model_copy(update={'kallor': kallor})
    fore = variant.model_dump_json()
    analys = lokal if med_analys else None
    d = bygg_arb_v6(variant, p, b, resultat, h, analys=analys)
    fynd = granska(variant, valj(variant, p.byra.regelpaket, DAG, p.byra.lan), p, b, d, h, DAG,
                   skrivresultat=resultat, analys=analys)
    assert not [f for f in fynd if f.typ == 'sparbarhet' and 'SRC-LST-GOR-ARB' in f.beskrivning]
    b1 = _b1(d)
    start, slut = _delar(b1)['Regelvis sakkunnigstatus']
    delen = b1.stycken[start:slut]
    assert delen[0].text.startswith('Regelvis sakkunnigstatus: ')
    forslag = [s for s in delen if s.text.startswith('Förslag till sakkunnig, M1')]
    assert len(forslag) == int(med_m1_kalla)
    if med_m1_kalla:
        assert forslag[0].referenser == ['SRC-LST-GOR-ARB', 'BT-KVAR-01', 'BT-KVAR-02', B1]
        assert 'Källor: [' in forslag[0].text
    else:
        assert all('SRC-LST-GOR-ARB' not in s.referenser for s in b1.stycken)
    assert variant.model_dump_json() == fore
    assert 'SRC-LST-GOR-ARB' in rb.kallor


def test_analysblock_utan_delanalyser_far_ingen_delanalysrubrik(v6underlag, lokal):
    tjanster = tuple(t.model_copy(update={'delanalyser': (), 'scenarier': tuple(
        s.model_copy(update={'delanalyser': ()}) for s in t.scenarier)}) for t in lokal.tjanster)
    utan = lokal.model_copy(update={'tjanster': tjanster})
    assert any(t.block for t in utan.tjanster)
    rubriker = [u.rubrik for u in _b1(bygg_arb_v6(*v6underlag, analys=utan)).underrubriker]
    assert 'Analysblock' in rubriker and 'Delanalyser och analysblock' not in rubriker


def test_b1_rubrikerna_ingar_i_kontrollsumman(dokument):
    b1 = _b1(dokument)
    assert b1.underrubriker
    assert b1.kontrollsumma() != for_text(b1.model_dump_json(exclude={'underrubriker'}))
    assert b1.kontrollsumma() not in {a.kontrollsumma() for a in _andrade(b1).values()}


def test_andrad_flyttad_eller_borttagen_b1_rubrik_upphaver_sakgodkannandet(dokument, v6underlag):
    from riskanalys.dokument.rendering import renderat_avsnitt
    from riskanalys.kommandon.sakgranska_kommando import beskriv_avsnitt
    p = v6underlag[1]
    b1 = _b1(dokument)
    assert b1.underrubriker
    # Sakgranskaren ser rubrikerna i den visning som godkänns.
    visning = beskriv_avsnitt(renderat_avsnitt(b1, p)).split('\n\n')
    assert [rad for rad in visning if rad in arb_v6.B1_DELRUBRIKER] == [u.rubrik for u in b1.underrubriker]
    poster = registrera_sakgranskning((), dokument, p, B1, True, 'FfR', 'Syntetisk granskare', DAG)
    assert galler_sakgranskning(poster, b1, p, dokument) is not None
    for namn, ny in _andrade(b1).items():
        assert galler_sakgranskning(poster, ny, p, _med_b1(dokument, ny)) is None, namn
        assert galler_sakgranskning(poster, ny, p) is None, namn


def test_v6_aterbygget_upptacker_andrad_flyttad_eller_borttagen_b1_rubrik(dokument, v6underlag, lokal):
    from riskanalys.granskning.dokument_v6 import analysfynd_v6
    rb, p, b, resultat, h = v6underlag

    def b1fynd(d):
        return [f for f in analysfynd_v6(rb, b, p, d, h, resultat, analys=lokal)
                if f['avsnitt'] == B1 and 'avviker från den frysta analysen' in f['beskrivning']]

    b1 = _b1(dokument)
    assert b1.underrubriker
    assert b1fynd(dokument) == []
    for namn, ny in _andrade(b1).items():
        fynd = b1fynd(_med_b1(dokument, ny))
        assert fynd and all(f['allvar'] == 'blockerande' for f in fynd), namn


def test_b1_rubrikerna_raknas_till_bilagan_och_inte_till_huvudtexten(dokument, v6underlag):
    from riskanalys.dokument.matning import dokumentord
    p = v6underlag[1]
    b1 = _b1(dokument)
    utan = _med_b1(dokument, b1.model_copy(update={'underrubriker': ()}))
    med, ej = dokumentord(dokument, p), dokumentord(utan, p)
    rubrikord = sum(len(u.rubrik.split()) for u in b1.underrubriker)
    assert rubrikord > 0
    assert med['huvudtext'] == ej['huvudtext']
    assert med['bilaga'] - ej['bilaga'] == rubrikord


def test_andrad_analysbilaga_stoppar_bygget_i_stallet_for_att_flytta_rubriker(v6underlag, lokal, monkeypatch):
    original = arb_v6.analysbilaga
    extra = Textstycke(typ='beskrivning', text='Oväntad post.', referenser=[], proveniens='lokal')
    monkeypatch.setattr(arb_v6, 'analysbilaga', lambda *a: (*original(*a), extra))
    with pytest.raises(ValueError, match='delindelningen'):
        bygg_arb_v6(*v6underlag, analys=lokal)


def test_andrat_kallunderlag_stoppar_bygget_i_stallet_for_att_flytta_rubriker(v6underlag, monkeypatch):
    from riskanalys.dokument import intagsunderlag
    original = intagsunderlag.bygg_underlagsbilaga
    monkeypatch.setattr(intagsunderlag, 'bygg_underlagsbilaga',
                        lambda *a, **k: (lambda b: b.model_copy(update={'stycken': b.stycken[:-1]}))(original(*a, **k)))
    with pytest.raises(ValueError, match='delindelningen'):
        bygg_arb_v6(*v6underlag, analys=None)


@pytest.mark.parametrize('format', ['D-ARB-tjanst-v5', 'D-ARB-tjanst-v5.1'])
def test_historiskt_paket_och_sparad_b1_summa_verifieras_oforandrat(underlag, tmp_path, format):
    from riskanalys.dokument.arb_v5 import bygg_arb_v5
    from riskanalys.dokument.arb_v5_1 import bygg_arb_v5_1
    from riskanalys.dokument.rendering import rendera_docx
    from riskanalys.faststallelse.faststall import FASTSTALLDA, verifiera_version
    from riskanalys.lagring.manifest import skriv_manifest
    rb, p, _, b, r, h = underlag
    d = (bygg_arb_v5 if format == 'D-ARB-tjanst-v5' else bygg_arb_v5_1)(rb, p, b, r, h)
    assert d.formatversion == format
    b1 = _b1(d)
    # Historisk B1 har inga rubriker i modellen och summan räknas som förut, utan underrubrikerna.
    assert b1.underrubriker == ()
    assert b1.kontrollsumma() == for_text(b1.model_dump_json(exclude={'underrubriker'}))
    poster = registrera_sakgranskning((), d, p, B1, True, 'FfR', 'Syntetisk granskare', DAG)
    paket = tmp_path / FASTSTALLDA / 'v1'
    paket.mkdir(parents=True)
    (paket / 'dokument.json').write_text(d.model_dump_json(), encoding='utf-8')
    skriv_manifest(paket, {'dokumentformat': format})
    assert verifiera_version(tmp_path, 1) == []
    sparat = Dokument.model_validate_json((paket / 'dokument.json').read_text(encoding='utf-8'))
    assert sparat == d
    assert galler_sakgranskning(poster, _b1(sparat), p, sparat) is not None
    # Word-exporten lägger inte till några B1-rubriker i historiska format.
    word = docx.Document(str(rendera_docx(sparat, p, 'UTKAST', tmp_path / 'historisk.docx')))
    assert not [x.text for x in word.paragraphs if x.text in arb_v6.B1_DELRUBRIKER]
