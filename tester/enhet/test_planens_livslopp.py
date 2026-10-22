"""Regressionstest för planens livslopp efter införande (granskning av a7f9377).

Placera filen i tester/enhet/ på codex/kravstod-tjansteexponering. Testerna beskriver beteende,
inte implementation: en plan som införts med en giltig, bunden utvärdering ska därefter vara
genomförd historik och får inte spärra fastställelsen när bedömningsdatum eller byråns fakta
ändras. Planer som ännu inte är genomförda ska fortsatt spärra.

`forandringshinder(rb, profil, profil, historik, datum)` är samma anrop som
`faststallelse/grindar.py:_drift` gör före fastställelse.
"""
from datetime import date

import pytest

from riskanalys.drift.historik import Historik
from riskanalys.profil.modeller import Tjansteplan, Planval
from riskanalys.profil.planering import forandringshinder, plansumma
from riskanalys.regelverk.laddning import ladda_regelbas
from tester.enhet.test_tjansteplanering import DAG, ja, plan, profil, upp, utvardering

NASTA_AR = date(2027, 10, 10)


@pytest.fixture(scope='module')
def rb():
    return ladda_regelbas()


def _inford(rb, tmp_path):
    """Registrera själva genomförandet genom riktig atomisk profilsparning.

    Granskarens ursprungliga hjälpare anropade bara den rena spärrfunktionen.
    Det är ingen genomföranderegistrering; slutstatus får inte härledas ur ja.
    """
    from riskanalys.profil.lagring import spara_profil, profilrevision
    from riskanalys.profil.forandringar import spara_andring
    from riskanalys.drift.historik import spara_historik
    p = plan(profil())
    historik = Historik(handelser=(utvardering(rb, p),))
    assert forandringshinder(rb, p, ja(p), historik, DAG) == (), 'Förutsättning: införandet godtas.'
    spara_profil(tmp_path,p)
    spara_historik(tmp_path,historik)
    inford=spara_andring(tmp_path,rb,ja(p),profilrevision(p),planval=(Planval(tjanst='T-RED-01',plan_id='ny'),))
    return inford, historik


def test_inford_plan_spärrar_inte_fastställelse_samma_år(rb,tmp_path):
    inford, historik = _inford(rb,tmp_path)
    assert forandringshinder(rb, inford, inford, historik, date(2026, 10, 20)) == ()


def test_inford_plan_spärrar_inte_fastställelse_nästa_år(rb,tmp_path):
    """Ny årlig bedömning: bara bedömningsdatumet har ändrats."""
    inford, historik = _inford(rb,tmp_path)
    nasta = inford.model_copy(update={'byra': inford.byra.model_copy(update={'datum': NASTA_AR})})
    assert forandringshinder(rb, nasta, nasta, historik, date(2027, 10, 20)) == ()


def test_inford_plan_spärrar_inte_efter_ändrade_byråfakta(rb,tmp_path):
    """Vanlig uppdatering av byråns uppgifter efter införandet."""
    inford, historik = _inford(rb,tmp_path)
    andrad = inford.model_copy(update={'uppgifter': {**inford.uppgifter, 'P-KUND.antal_aktiva': upp(130)}})
    assert forandringshinder(rb, andrad, andrad, historik, date(2026, 12, 1)) == ()


def test_inford_plan_spärrar_inte_efter_ny_regelbasversion(rb,tmp_path):
    """En ny regelbas ändrar plansumman men gör inte ett genomfört införande ogenomfört."""
    inford, historik = _inford(rb,tmp_path)
    ny_rb = rb.model_copy(update={'kontrollsumma': 'sha256:' + '0' * 64})
    assert plansumma(ny_rb, inford, 'ny') != plansumma(rb, inford, 'ny'), 'Förutsättning: summan beror på regelbasen.'
    assert forandringshinder(ny_rb, inford, inford, historik, date(2026, 12, 1)) == ()


def test_ej_genomford_andringsplan_for_erbjuden_tjanst_spärrar_fortfarande(rb):
    """Skyddet får inte försvinna: en ändringsplan utan bunden utvärdering spärrar fastställelse."""
    erbjuden = ja(profil())
    andring = erbjuden.model_copy(update={'tjansteplaner': (Tjansteplan(id='andring', tjanst='T-RED-01',
        typ='vasentligt_andrad_tjanst', beskrivning='Byrån börjar verkställa betalningar i uppdraget.', uppgifter={}),)})
    assert forandringshinder(rb, andring, andring, Historik(), date(2026, 12, 1))


def test_andrad_plan_fore_inforande_kraver_fortfarande_ny_utvardering(rb):
    """Skyddet får inte försvinna: ändras planen före införandet gäller inte den gamla utvärderingen."""
    p = plan(profil())
    historik = Historik(handelser=(utvardering(rb, p),))
    andrad = p.model_copy(update={'tjansteplaner': (p.tjansteplaner[0].model_copy(update={'beskrivning': 'Ny marknad'}),)})
    assert forandringshinder(rb, andrad, ja(andrad), historik, DAG)


def test_forklaring_av_motstridig_provning_ar_ratt_stavad():
    from riskanalys.dokument.nivamotivering_v8 import _ORSAKER
    assert 'byråns prövningar av C-07' in _ORSAKER['motstridig']('C-07')
