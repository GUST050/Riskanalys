"""Reduktionsspärren per motorscenario (spec 2026-10-18, steg 5 punkt 4).

Byrån kan bara stoppa en sänkning, aldrig skapa en. Endast syntetiska data:
motorns scenarier fryses här uttryckligen per test, så att spärren prövas
oberoende av katalogens aktuella kontrollmål.
"""
from dataclasses import replace

import pytest

from riskanalys.analys import modeller as m, provning as p
from riskanalys.bedomning.motor import RISKNIVAER

TJ = 'T-RED-01'
BAR = 'C-07'
RACKVIDD = 'KR-C-07-T-RED-01'


def saknas_text(hot):
    return (f'{TJ}: {hot}: kontrollen täcker enligt byråns prövning inte scenariot; '
            'rätta kontrolluppgifterna eller registrera metodkonflikt.')


def stod_text(hot, kontroller):
    return (f'{TJ}: {hot}: motorns sänkning saknar positiv lokal prövning av en bärande kontroll '
            f'({", ".join(kontroller)}) i ett relevant scenario med hotet; pröva kontrollen för scenariot '
            'eller registrera metodkonflikt.')


def delvis_text(hot, kontroller=(BAR,)):
    return (f'{TJ}: {hot}: byråns prövning visar bara delvis täckning av bärande kontroll '
            f'({", ".join(kontroller)}); delvis täckning räcker inte som stöd för ett helt kontrollavdrag. '
            'Komplettera prövningen eller registrera metodkonflikt.')


def konflikt_text(hot, kontroller=(BAR,)):
    return (f'{TJ}: {hot}: byråns prövningar av bärande kontroll ({", ".join(kontroller)}) är motstridiga; '
            'ange en samlad bedömning av täckningen eller registrera metodkonflikt.')


def obelagd_text(hot, kontroller=(BAR,)):
    return (f'{TJ}: {hot}: den tillräckliga täckningen av bärande kontroll ({", ".join(kontroller)}) saknar '
            'beskriven räckvidd eller aktuellt genomförandebelägg och bär därför inte sänkningen. '
            'Komplettera beläggen eller registrera metodkonflikt.')


def oprovat_text(hot):
    return (f'{TJ}: {hot}: motorn sänker scenariot men hotet saknar relevant lokal scenarioprövning; '
            'pröva hotet i ett relevant scenario eller registrera metodkonflikt.')


@pytest.fixture(scope='module')
def fall(tmp_path_factory, regelbas_v1):
    from tester.fixturer.analys_hela_kedjan import skapa_fall
    return skapa_fall(regelbas_v1, tmp_path_factory.mktemp('reduktionssparr'))


def _lagre(risk):
    return RISKNIVAER[max(RISKNIVAER.index(risk) - 1, 0)]


def _motor(fall, sankta, *, utan_scenarier=False):
    """Fryser motorns PT-scenarier: bara hoten i `sankta` sänks, med angivna bärande kontroller."""
    t = next(x for x in fall.bedomning.tjanster if x.tjanst == TJ)
    if utan_scenarier:
        ny = t.model_copy(update={'scenarier': ()})
    else:
        def scenario(s):
            if s.dimension != 'pt':
                return s
            if s.hot in sankta:
                return s.model_copy(update={'kvarstaende': _lagre(s.risk), 'tackande_kontroller': sankta[s.hot]})
            return s.model_copy(update={'kvarstaende': s.risk, 'tackande_kontroller': ()})
        scenarier = tuple(scenario(s) for s in t.scenarier)
        kvar = max((s.kvarstaende for s in scenarier if s.dimension == 'pt'), key=RISKNIVAER.index)
        ny = t.model_copy(update={'scenarier': scenarier, 'kvarstaende': kvar})
    return fall.bedomning.model_copy(update={'tjanster': tuple(ny if x.tjanst == TJ else x for x in fall.bedomning.tjanster)})


def _positiv(scenario, tackning='bedomd_tillracklig', kontroll=BAR):
    return m.Kontrollprovning(scenario=scenario, kontroll=kontroll, rackvidd=(RACKVIDD,),
        tillampning='Ansvarig konsult stämmer av kontoutdrag mot bokfört underlag och utreder differenser.',
        utfall='Stickprovet visar dokumenterade avstämningar; dolda led omfattas inte.',
        belagg=('ab6:kontroll',), tackning=tackning,
        kvarstar='Parallella bankengagemang och dolda mottagare kan fortfarande finnas.')


def _analys(fall, *, kontroller=None, ersatt=None, **andringar):
    """Tjänstens lokala analys utan fixturens öppna metodkonflikt, omräknade bekräftelser."""
    from tester.fixturer.analys_hela_kedjan import _bekrafta
    a = next(x for x in fall.analys.tjanster if x.tjanst == TJ)
    prov = tuple(kontroller) if kontroller is not None else tuple(
        c for c in a.kontroller if c.scenario not in (ersatt or {})) + tuple((ersatt or {}).values())
    a = a.model_copy(update={'reduktionsprovning': 'motiverad',
        'gap': tuple(g for g in a.gap if g.typ != 'metodkonflikt'), 'kontroller': prov, **andringar})
    return _bekrafta(fall.analys.model_copy(update={'tjanster': tuple(a if x.tjanst == TJ else x for x in fall.analys.tjanster)}))


def _brister(fall, bedomning, paket):
    return tuple(x for x in p.analysbrister(fall.regelbas, fall.profil, bedomning, paket) if x.startswith(TJ + ': '))


def _stod(fall):
    """Positiv prövning av den bärande kontrollen för båda de sänkta scenarierna."""
    return {'gem:H-03': _positiv('gem:H-03'), 'gem:H-MOD-01': _positiv('gem:H-MOD-01')}


SANKTA = {'H-03': (BAR,), 'H-MOD-01': (BAR,)}


# --- sankta_scenarier och faktisk_reduktion ---------------------------------------------------

def test_sankta_scenarier_ar_bara_sankta_pt_scenarier(fall):
    t = next(x for x in _motor(fall, SANKTA).tjanster if x.tjanst == TJ)
    sankta = p.sankta_scenarier(t)
    assert {s.hot for s in sankta} == {'H-03', 'H-MOD-01'}
    assert all(s.dimension == 'pt' for s in sankta)
    assert all(RISKNIVAER.index(s.kvarstaende) < RISKNIVAER.index(s.risk) for s in sankta)


def test_delreduktion_ar_faktisk_trots_oforandrat_tjanstemax(fall):
    t = next(x for x in _motor(fall, {'H-MOD-01': (BAR,)}).tjanster if x.tjanst == TJ)
    assert t.kvarstaende == t.inneboende.risk == 'hög'
    assert p.faktisk_reduktion(t)


def test_inga_sankta_scenarier_ar_ingen_reduktion(fall):
    t = next(x for x in _motor(fall, {}).tjanster if x.tjanst == TJ)
    assert p.sankta_scenarier(t) == () and not p.faktisk_reduktion(t)


def test_aldre_bedomning_utan_scenarier_foljer_tjanstenivan(fall):
    t = next(x for x in _motor(fall, {}, utan_scenarier=True).tjanster if x.tjanst == TJ)
    assert t.scenarier == () and p.sankta_scenarier(t) == ()
    assert p.faktisk_reduktion(t) is True
    lika = t.model_copy(update={'kvarstaende': t.inneboende.risk})
    assert p.faktisk_reduktion(lika) is False
    assert p.faktisk_reduktion(t.model_copy(update={'inneboende': None})) is False


# --- spärren i block 12 -----------------------------------------------------------------------

def test_delvis_ensam_racker_inte_for_helt_avdrag(fall):
    stod = {k: _positiv(k, 'delvis') for k in _stod(fall)}
    assert _brister(fall, _motor(fall, SANKTA), _analys(fall, ersatt=stod)) == (
        delvis_text('H-03'), delvis_text('H-MOD-01'))


def test_delvis_ar_fortsatt_giltig_observation_utan_sankning(fall):
    # En delvis observation i ett scenario som motorn inte sänker kräver inget reduktionsstöd.
    stod = {**_stod(fall), 'gem:H-01': _positiv('gem:H-01', 'delvis')}
    fynd = _brister(fall, _motor(fall, SANKTA), _analys(fall, ersatt=stod))
    assert not any('delvis täckning räcker inte' in x for x in fynd)


def test_motstridiga_observationer_av_bararande_kontroll_blockerar(fall):
    stod = _stod(fall)
    a = next(x for x in fall.analys.tjanster if x.tjanst == TJ)
    prov = (tuple(c for c in a.kontroller if c.scenario not in stod) + tuple(stod.values())
            + (_positiv('gem:H-03', 'delvis'),))
    assert _brister(fall, _motor(fall, SANKTA), _analys(fall, kontroller=prov)) == (konflikt_text('H-03'),)


def test_tillrackligt_stod_i_annat_scenario_doljer_inte_konflikt(fall):
    stod = {**_stod(fall), 'gem:H-03': _positiv('gem:H-03', 'okand')}
    a = next(x for x in fall.analys.tjanster if x.tjanst == TJ)
    lokal = m.Scenarioanalys(id=TJ + ':avstamning', hot=('H-03',), rubrik='Syntetiskt avstämningsförlopp',
        handelseforlopp='Oförklarade flöden passerar avstämningen.', relevans='relevant',
        motivering='Prövat mot uppdragets mandat och tillgängliga underlag.', belagg=('ab6:mandat',))
    paket = _analys(fall, ersatt={**stod, lokal.id: _positiv(lokal.id)}, scenarier=(*a.scenarier, lokal))
    assert konflikt_text('H-03') in _brister(fall, _motor(fall, SANKTA), paket)


def test_bedomd_tillracklig_bararande_kontroll_ger_inget_fynd(fall):
    stod = {k: _positiv(k, 'bedomd_tillracklig') for k in _stod(fall)}
    assert _brister(fall, _motor(fall, SANKTA), _analys(fall, ersatt=stod)) == ()


def test_fel_kontroll_trots_positiv_annan_kontroll_blockerar(fall):
    motor = _motor(fall, {'H-03': ('C-TJ-01',), 'H-MOD-01': (BAR,)})
    assert _brister(fall, motor, _analys(fall, ersatt=_stod(fall))) == (stod_text('H-03', ('C-TJ-01',)),)


def test_uttrycklig_saknas_for_bararande_kontroll_blockerar_trots_annan_positiv(fall):
    a = next(x for x in fall.analys.tjanster if x.tjanst == TJ)
    saknas = next(c for c in a.kontroller if c.scenario == 'gem:H-03')
    assert saknas.kontroll == 'C-TJ-01' and saknas.tackning == 'saknas'
    motor = _motor(fall, {'H-03': ('C-TJ-01', BAR), 'H-MOD-01': (BAR,)})
    prov = tuple(c for c in a.kontroller if c.scenario != 'gem:H-MOD-01') + tuple(_stod(fall).values())
    assert _brister(fall, motor, _analys(fall, kontroller=prov)) == (saknas_text('H-03'),)


def test_saknad_tackning_utan_bararande_kontroll_blockerar_inte(fall):
    # C-TJ-01 saknas för gem:H-03 men bär inte sänkningen; C-07 är positivt prövad.
    a = next(x for x in fall.analys.tjanster if x.tjanst == TJ)
    prov = tuple(c for c in a.kontroller if c.scenario != 'gem:H-MOD-01') + tuple(_stod(fall).values())
    assert _brister(fall, _motor(fall, SANKTA), _analys(fall, kontroller=prov)) == ()


@pytest.mark.parametrize('tackning', ['okand', 'saknas'])
def test_okand_eller_saknad_tackning_ar_inget_stod(fall, tackning):
    stod = {**_stod(fall), 'gem:H-03': _positiv('gem:H-03', tackning)}
    fynd = _brister(fall, _motor(fall, SANKTA), _analys(fall, ersatt=stod))
    if tackning == 'okand':
        assert stod_text('H-03', (BAR,)) in fynd
    else:
        assert saknas_text('H-03') in fynd and stod_text('H-03', (BAR,)) in fynd


def test_positiv_tackning_utan_rackvidd_for_hotet_ar_inget_stod(fall):
    # Räckvidden måste avse just det sänkta hotet, inte bara något hot i scenariot.
    rb = fall.regelbas
    c = rb.kontroller[BAR]
    smal = tuple(r.model_copy(update={'hot': tuple(h for h in r.hot if h != 'H-MOD-01')}) if r.id == RACKVIDD else r
                 for r in c.rackvidd)
    kontroller = {**rb.kontroller, BAR: c.model_copy(update={'rackvidd': smal})}
    rb = rb.model_copy(update={'kontroller': kontroller})
    lokal = m.Scenarioanalys(id=TJ + ':kombinerat', hot=('H-TJ-01', 'H-MOD-01'),
        rubrik='Kombinerat syntetiskt förlopp', handelseforlopp='Falska underlag och dolda motparter i samma kedja.',
        relevans='relevant', motivering='Prövat mot uppdragets mandat och tillgängliga underlag.', belagg=('ab6:mandat',))
    a = next(x for x in fall.analys.tjanster if x.tjanst == TJ)
    stod = {**_stod(fall), lokal.id: _positiv(lokal.id)}
    stod.pop('gem:H-MOD-01')
    paket = _analys(fall, ersatt=stod, scenarier=(*a.scenarier, lokal),
        scenariokopplingar=tuple(k for k in a.scenariokopplingar if k.scenario != 'gem:H-MOD-01'))
    fynd = tuple(x for x in p.analysbrister(rb, fall.profil, _motor(fall, SANKTA), paket) if x.startswith(TJ + ': '))
    assert stod_text('H-MOD-01', (BAR,)) in fynd


def test_saknat_provat_hot_blockerar(fall):
    a = next(x for x in fall.analys.tjanster if x.tjanst == TJ)
    paket = _analys(fall, kontroller=tuple(c for c in a.kontroller if c.scenario != 'gem:H-MOD-01')
                    + (_positiv('gem:H-03'),),
                    scenariokopplingar=tuple(k for k in a.scenariokopplingar if k.scenario != 'gem:H-MOD-01'))
    fynd = _brister(fall, _motor(fall, SANKTA), paket)
    assert oprovat_text('H-MOD-01') in fynd
    assert stod_text('H-MOD-01', (BAR,)) not in fynd


def test_lokal_ej_relevant_doljer_inte_sankt_motorhot(fall):
    gem = tuple(s.model_copy(update={'relevans': 'ej_relevant',
        'motivering': 'Syntetiskt: hotet bedöms inte förekomma i uppdragen.'}) if s.id == 'gem:H-MOD-01' else s
        for s in fall.analys.gemensamma_scenarier)
    ny = next(s for s in gem if s.id == 'gem:H-MOD-01')
    a = next(x for x in fall.analys.tjanster if x.tjanst == TJ)
    kop = tuple(k.model_copy(update={'scenariosumma': p.scenariosumma(ny)}) if k.scenario == ny.id else k
                for k in a.scenariokopplingar)
    paket = _analys(replace(fall, analys=fall.analys.model_copy(update={'gemensamma_scenarier': gem})),
                    ersatt=_stod(fall), scenariokopplingar=kop)
    fynd = _brister(fall, _motor(fall, SANKTA), paket)
    assert oprovat_text('H-MOD-01') in fynd


def test_osankt_scenario_med_accepterad_brist_blockerar_inte_men_brist_kravs(fall):
    a = next(x for x in fall.analys.tjanster if x.tjanst == TJ)
    assert any(c.scenario == 'gem:H-01' and c.tackning == 'saknas' for c in a.kontroller)
    motor = _motor(fall, SANKTA)
    assert _brister(fall, motor, _analys(fall, ersatt=_stod(fall))) == ()
    utan_brist = _analys(fall, ersatt=_stod(fall), gap=())
    fynd = _brister(fall, motor, utan_brist)
    assert any('saknad kontroll kräver dokumenterad kontrollbrist' in x for x in fynd)
    assert not any('faktisk reduktion saknar belagd scenariotäckning' in x for x in fynd)


def _avvikande(fall, *, prov_pa_variant=True):
    a = next(x for x in fall.analys.tjanster if x.tjanst == TJ)
    gem = next(s for s in fall.analys.gemensamma_scenarier if s.id == 'gem:H-03')
    variant = gem.model_copy(update={'id': TJ + ':lokal:H-03',
        'motivering': 'Tjänstens egna avräkningar ger en särskild tillämpning av hotet.'})
    kop = tuple(k.model_copy(update={'tillampning': 'avviker', 'lokal_scenario': variant.id,
        'motivering': 'Bokföringsmandatet ger annan insyn än det gemensamma scenariot.'}) if k.scenario == gem.id else k
        for k in a.scenariokopplingar)
    flyttat = tuple(c.model_copy(update={'scenario': variant.id}) if c.scenario == gem.id else c for c in a.kontroller)
    stod = (_positiv(variant.id if prov_pa_variant else gem.id), _positiv('gem:H-MOD-01'))
    prov = tuple(c for c in flyttat if c.scenario != 'gem:H-MOD-01') + stod
    return _analys(fall, kontroller=prov, scenarier=(*a.scenarier, variant), scenariokopplingar=kop)


def test_avvikande_lokal_variant_bar_stodet(fall):
    assert _brister(fall, _motor(fall, SANKTA), _avvikande(fall)) == ()


def test_prov_pa_ersatt_gemensamt_scenario_ar_inget_stod(fall):
    fynd = _brister(fall, _motor(fall, SANKTA), _avvikande(fall, prov_pa_variant=False))
    assert stod_text('H-03', (BAR,)) in fynd


def test_inaktuell_samma_koppling_ar_inget_stod(fall):
    a = next(x for x in fall.analys.tjanster if x.tjanst == TJ)
    kop = tuple(k.model_copy(update={'scenariosumma': 'sha256:' + '0' * 64}) if k.scenario == 'gem:H-03' else k
                for k in a.scenariokopplingar)
    fynd = _brister(fall, _motor(fall, SANKTA), _analys(fall, ersatt=_stod(fall), scenariokopplingar=kop))
    assert oprovat_text('H-03') in fynd


def test_delreduktion_aktiverar_block12_trots_oforandrat_tjanstemax(fall):
    motor = _motor(fall, {'H-MOD-01': (BAR,)})
    a = next(x for x in fall.analys.tjanster if x.tjanst == TJ)
    block = tuple(x.model_copy(update={'aktivering': 'ej_tillamplig'}) if x.nummer == 12 else x for x in a.block)
    utan = _analys(fall, ersatt={'gem:H-MOD-01': _positiv('gem:H-MOD-01')}, block=block,
                   reduktionsprovning='ej_reduktion', reduktionsmotivering='')
    fynd = _brister(fall, motor, utan)
    assert f'{TJ}: Faktisk motorreduktion kräver reduktionsprövning.' in fynd
    assert f'{TJ}: Reduktionsprövningen stämmer inte med motorns faktiska reduktion.' in fynd
    med = _analys(fall, ersatt={'gem:H-MOD-01': _positiv('gem:H-MOD-01')})
    assert _brister(fall, motor, med) == ()


def test_aldre_bedomning_behaller_dagens_sparr(fall):
    motor = _motor(fall, {}, utan_scenarier=True)
    fynd = _brister(fall, motor, _analys(fall, ersatt=_stod(fall)))
    assert f'{TJ}: gem:H-01: faktisk reduktion saknar belagd scenariotäckning; registrera metodkonflikt.' in fynd
    assert not any('motorns sänkning' in x or 'kontrollen täcker enligt byråns prövning' in x or
                   'motorn sänker scenariot' in x for x in fynd)


# --- rapportens förklaring av ej godtagna sänkningar --------------------------------------------

def _avsnittstext(fall, motor, paket):
    from riskanalys.dokument.tjanstavsnitt_v8 import bygg_tjanstavsnitt_v8
    from riskanalys.regelverk.granser import metodgransindex
    t = next(x for x in motor.tjanster if x.tjanst == TJ)
    avsnitt = bygg_tjanstavsnitt_v8(fall.regelbas, fall.profil, t, None, 'D-ARB.4',
                                    gransindex=metodgransindex(fall.regelbas), analys=paket)
    return [s.text for s in avsnitt.stycken]


def test_rapporten_forklarar_ej_godtagen_sankning_per_scenario(fall):
    stod = {**_stod(fall), 'gem:H-03': _positiv('gem:H-03', 'delvis')}
    texter = [x for x in _avsnittstext(fall, _motor(fall, SANKTA), _analys(fall, ersatt=stod)) if 'inte godtagen' in x]
    assert len(texter) == 1
    assert '[H-03]' in texter[0] and 'från hög till måttlig' in texter[0]
    assert 'bara delvis täckning av C-07' in texter[0]
    assert 'inneboende nivå hög' in texter[0] and '[VERIFIERA]' in texter[0]


def test_rapporten_tiger_nar_sankningen_har_tillrackligt_stod(fall):
    texter = _avsnittstext(fall, _motor(fall, SANKTA), _analys(fall, ersatt=_stod(fall)))
    assert not any('inte godtagen' in x for x in texter)


def test_rapporten_anger_nar_tjanstens_niva_bygger_pa_ej_godtagen_sankning(fall):
    t = next(x for x in fall.bedomning.tjanster if x.tjanst == TJ)
    alla = {s.hot: (BAR,) for s in t.scenarier if s.dimension == 'pt'}
    motor = _motor(fall, alla)
    # Bara H-MOD-01 har stöd; det höga H-03-scenariot saknar godtaget stöd och bär tjänstens nivå.
    texter = _avsnittstext(fall, motor, _analys(fall, ersatt={'gem:H-MOD-01': _positiv('gem:H-MOD-01')}))
    assert any('Tjänstens redovisade kvarstående PT-nivå måttlig bygger på' in x and 'minst hög' in x for x in texter)
    # Med stöd för H-03 avgörs nivån bara av måttliga ej godtagna sänkningar: ingen tjänstemening.
    texter = _avsnittstext(fall, motor, _analys(fall, ersatt=_stod(fall)))
    assert not any('Tjänstens redovisade kvarstående' in x for x in texter)


def test_rapportens_skal_motsvarar_spärrens_fynd(fall):
    stod = {**_stod(fall), 'gem:H-03': _positiv('gem:H-03', 'delvis')}
    paket = _analys(fall, ersatt=stod)
    motor = _motor(fall, SANKTA)
    t = next(x for x in motor.tjanster if x.tjanst == TJ)
    a = next(x for x in paket.tjanster if x.tjanst == TJ)
    skal = p.ej_godtagna_sankningar(fall.regelbas, fall.profil, paket, a, t)
    assert [(b.scenario.hot, b.orsak) for b in skal] == [('H-03', 'delvis')]
    assert _brister(fall, motor, paket) == (delvis_text('H-03'),)


def test_tillracklig_tackning_utan_genomforandebelagg_forklaras_i_rapporten(fall):
    stod = {k: c.model_copy(update={'belagg': ()}) for k, c in _stod(fall).items()}
    paket = _analys(fall, ersatt=stod)
    motor = _motor(fall, SANKTA)
    fynd = _brister(fall, motor, paket)
    assert any('aktuellt genomförandebelägg för kontrollen saknas' in x for x in fynd)
    assert obelagd_text('H-03') in fynd and obelagd_text('H-MOD-01') in fynd
    t = next(x for x in motor.tjanster if x.tjanst == TJ)
    a = next(x for x in paket.tjanster if x.tjanst == TJ)
    assert [(b.scenario.hot, b.orsak) for b in p.ej_godtagna_sankningar(fall.regelbas, fall.profil, paket, a, t)] == [
        ('H-03', 'obelagd'), ('H-MOD-01', 'obelagd')]
    texter = [x for x in _avsnittstext(fall, motor, paket) if 'inte godtagen' in x]
    assert len(texter) == 2 and all('saknar beskriven räckvidd eller aktuellt genomförandebelägg' in x for x in texter)
