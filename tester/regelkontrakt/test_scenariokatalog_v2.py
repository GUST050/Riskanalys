"""Katalogens scenarier ska vara källbundna och kunna användas utan tysta bortfall."""
import pytest

from riskanalys.intag.underlag import EGEN_KANNEDOM, vald_kalla
from riskanalys.regelverk.modeller import Regel, hot_dimensioner
from riskanalys.regelverk.validering import validera


def test_verkliga_katalogen_anvander_giltig_scenariometod(regelbas_v1):
    assert regelbas_v1.metod.scenario is not None
    assert validera(regelbas_v1) == []


def test_sarbarheter_kan_verka_i_varje_tjanst_som_anvander_dem(regelbas_v1):
    rb = regelbas_v1
    for t in rb.tjanster.values():
        for id in t.sarbarheter:
            s = rb.sarbarheter[id]
            dimensioner = {'pt', 'tf'} if s.galler == 'bada' else {'pt' if s.galler == 'penningtvatt' else 'tf'}
            assert any(h in t.hot and dimensioner.intersection(hot_dimensioner(rb.hot[h])) for h in s.hot), (t.id, id)
            assert s.metodmotivering
            assert not any(h.startswith('H-TJ-') for h in s.hot) or s.omrade in ('tj', 'verk')


def test_katalogen_reproducerar_tillsynsexemplen(regelbas_v1):
    assert 'H-01' in regelbas_v1.sarbarheter['S-KUND-01'].hot
    assert {'H-01', 'H-03'} <= set(regelbas_v1.sarbarheter['S-ARB-15'].hot)
    assert 'H-03' in regelbas_v1.sarbarheter['S-GEO-01'].hot


def test_bara_aml_kontroller_far_scenariomal(regelbas_v1):
    rb = regelbas_v1
    for k in rb.kontroller.values():
        if k.id == rb.sanktionsmetod.kontroll:
            assert k.riktar_sig_mot == ()
        else:
            assert k.riktar_sig_mot, k.id
            for r in k.riktar_sig_mot:
                assert r.grund == 'metodval'
                assert set(r.kallor) <= set(rb.kallor)
                assert r.motivering


def test_kontrollmal_omfattar_tjanstens_eget_hot_och_h03_eller_motiverar_uteslutningen(regelbas_v1):
    """Tjänstens eget H-TJ-hot och H-03 är mål när källan stöder det; annars namnges hotet i motiveringen."""
    rb = regelbas_v1
    for k in rb.kontroller.values():
        for r in k.riktar_sig_mot:
            for h in rb.tjanster[r.tjanst].hot:
                if (h.startswith('H-TJ-') or h == 'H-03') and h not in r.hot:
                    assert h in r.motivering, (k.id, r.tjanst, h)


def test_iakttagelser_ar_frivilliga_lokala_egen_kannedom(regelbas_v1):
    rb = regelbas_v1
    ai = {f for lista in rb.tillatelselistor.values() for f in lista.falt}
    for t in rb.tjanster.values():
        id = t.erbjuds_falt.removesuffix('_erbjuds') + '_iakttagna_hot'
        assert id in rb.falt
        f = rb.falt[id]
        assert f.typ == 'flerval' and f.val == t.hot
        assert not f.kritisk and not f.intag.obligatorisk
        assert f.intag.grund == 'metodval'
        assert id not in ai
        assert vald_kalla(rb, None, f, {'underlag': 'egen_kannedom'}) == EGEN_KANNEDOM


def test_scenariometodens_tal_har_kallor_och_ogranskad_status(regelbas_v1):
    scenario = regelbas_v1.metod.scenario
    assert scenario is not None
    for regel in scenario.regler():
        assert regel.kallor and set(regel.kallor) <= set(regelbas_v1.kallor)
        assert regel.grund == 'metodval'
        assert regel.sakkunnig.status == 'ej_granskad'


def test_kallor_pa_regel_utelamnas_tomma_for_historiska_summor():
    data = {'id': 'BT-X', 'grund': 'metodval', 'forklaring': 'Syntetiskt.'}
    assert 'kallor' not in Regel(**data).model_dump(mode='json')
    assert Regel(**data, kallor=('SRC-1',)).model_dump(mode='json')['kallor'] == ['SRC-1']


# Steg B: nya PT-modus H-MOD-06/07 saknar prövad kontrollsänkning. Grundnivåer och kontrollmål är oförändrade.
# Varje rad motsvarar en rad i jämförelsetabellen i docs/research/13-scenariomotor-katalog.md (profil A–E).
@pytest.mark.parametrize('fall,vantat', [
    ('m2_bas', [('T-RED-01','måttlig','måttlig','måttlig'), ('T-SKATT-01','hög','måttlig','hög'), ('T-BOLAG-01','hög','måttlig','hög')]),
    ('m2_utland', [('T-RED-01','hög','hög','måttlig'), ('T-SKATT-01','hög','hög','hög'), ('T-BOLAG-01','hög','hög','hög')]),
    ('ab6_fyra', [('T-RED-01','hög','mycket hög','måttlig'), ('T-RED-02','hög','mycket hög','måttlig'), ('T-RED-03','hög','mycket hög','måttlig'), ('T-RED-04','hög','mycket hög','måttlig')]),
    ('m2_ideell', [('T-RED-01','hög','hög','måttlig'), ('T-SKATT-01','hög','hög','hög'), ('T-BOLAG-01','hög','hög','hög')]),
    ('m2_ideell_pep', [('T-RED-01','hög','mycket hög','måttlig'), ('T-SKATT-01','hög','mycket hög','hög'), ('T-BOLAG-01','hög','mycket hög','hög')]),
])
def test_kallbundna_kontrollmal_styr_typfallens_kvarstaende_risk(regelbas_v1, fall, vantat):
    from riskanalys.bedomning.motor import bedom
    from riskanalys.regelverk.urval import valj
    from tester.fixturer.arb_kedja import syntetisk_profil, andrat
    from tester.fixturer.analys_hela_kedjan import _profil

    rb = regelbas_v1
    p = _profil(rb) if fall == 'ab6_fyra' else syntetisk_profil(rb)
    if fall == 'm2_utland':
        p = andrat(p, 'P-GEO.antal_utland_transaktion', varde=10)
    if fall.startswith('m2_ideell'):
        p = andrat(p, 'P-RISK.ideell', varde=True)
    if fall == 'm2_ideell_pep':
        p = andrat(p, 'P-RISK.pep', varde=True)
    b = bedom(rb, valj(rb, p.byra.regelpaket, p.byra.datum, p.byra.lan), p)
    assert [(t.tjanst,t.inneboende.risk,t.terrorfinansiering.risk,t.kvarstaende)
            for t in b.tjanster if t.erbjuds] == vantat


# Sänkningar mot den summerande metoden som docs/research/13-scenariomotor-katalog.md uttryckligen förklarar,
# som (faktorer, tjänst, dimension). Tom: katalogen 2.0.0 sänker ingen nivå för enskilda eller parvisa faktorer.
REDOVISADE_SANKNINGAR = frozenset()
RISKORDNING = ('låg', 'måttlig', 'hög', 'mycket hög')


def _summerande_metod(rb):
    """Samma katalog med den äldre summerande metoden (metod.scenario saknas), som 1.6.0 räknade."""
    return rb.model_copy(update={'metod': rb.metod.model_copy(update={'scenario': None})})


def _nivaer(rb, profil):
    from riskanalys.bedomning.motor import bedom
    from riskanalys.regelverk.urval import valj
    b = bedom(rb, valj(rb, profil.byra.regelpaket, profil.byra.datum, profil.byra.lan), profil)
    return {t.tjanst: {'pt': t.inneboende.risk, 'tf': t.terrorfinansiering.risk, 'kvar': t.kvarstaende}
            for t in b.tjanster if t.erbjuds}


def test_inga_oredovisade_sankningar_for_enskilda_eller_parvisa_faktorer(regelbas_v1):
    """Varje enskild och parvis riskfaktor, alla tjänster erbjudna, med och utan bankdata: ingen nivå sjunker tyst."""
    from itertools import combinations, product
    from tester.fixturer.faktorer import faktorprofil, faktorvarden

    rb, gammal = regelbas_v1, _summerande_metod(regelbas_v1)
    faktorer = tuple(faktorvarden(rb))
    sankningar = set()
    kombinationer = [(), *((f,) for f in faktorer), *combinations(faktorer, 2)]
    for komb, med_bankdata in product(kombinationer, (False, True)):
        profil = faktorprofil(rb, komb, alla_tjanster=True, med_bankdata=med_bankdata)
        fore, efter = _nivaer(gammal, profil), _nivaer(rb, profil)
        sankningar |= {(komb, tjanst, dim) for tjanst in efter for dim in ('pt', 'tf', 'kvar')
                       if RISKORDNING.index(efter[tjanst][dim]) < RISKORDNING.index(fore[tjanst][dim])}
    assert sankningar <= REDOVISADE_SANKNINGAR, sorted(sankningar - REDOVISADE_SANKNINGAR)[:10]
