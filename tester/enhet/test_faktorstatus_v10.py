"""Faktastatus i rapporten är inte motorns konservativa tillämpning."""
import pytest
from riskanalys.dokument.faktorstatus_v10 import faktorstatus, lagre_status
from tester.fixturer.faktorer import faktorprofil
from tester.fixturer.arb_kedja import andrat


@pytest.mark.parametrize(('varde', 'status'), [(0, 'Nej'), (1, 'Finns')])
def test_belagd_distansidentitet(regelbas_v1, varde, status):
    rb = regelbas_v1
    p = andrat(faktorprofil(rb, ()), 'P-KUND.antal_osaker_distansidentitet', varde=varde)
    assert faktorstatus(rb, p, rb.sarbarheter['S-ARB-08']) == status


@pytest.mark.parametrize('andring', [{'status': 'saknas'}, {'inaktuell': True}, {'kalla': ''}])
def test_okant_blir_aldrig_nej(regelbas_v1, andring):
    rb = regelbas_v1
    p = andrat(faktorprofil(rb, ()), 'P-KUND.antal_osaker_distansidentitet', varde=0, **andring)
    assert faktorstatus(rb, p, rb.sarbarheter['S-ARB-08']) == 'Okänt'


def test_positiv_under_troskel(regelbas_v1):
    rb = regelbas_v1
    p = faktorprofil(rb, ())
    from riskanalys.profil.omfattning import harled_andelar
    p = andrat(p, 'P-KUND.antal_riskbransch', varde=1)
    p = harled_andelar(p, rb, frozenset({'P-KUND.antal_riskbransch'}))
    assert faktorstatus(rb, p, rb.sarbarheter['S-KUND-01']) == 'Under tröskeln'


def test_falskt_sammansatt_villkor_ar_inte_franvaro(regelbas_v1):
    rb = regelbas_v1
    p = faktorprofil(rb, (), med_bankdata=True)
    from riskanalys.profil.omfattning import harled_andelar
    p = andrat(p, 'P-KANAL.antal_digitalt_underlag', varde=p.uppgifter['P-KUND.antal_aktiva'].varde)
    p = harled_andelar(p, rb, frozenset({'P-KANAL.antal_digitalt_underlag'}))
    assert faktorstatus(rb, p, rb.sarbarheter['S-KANAL-01']) == 'Okänt'


def test_ej_erbjuda_ar_inte_tillamplig(regelbas_v1):
    rb = regelbas_v1
    p = faktorprofil(rb, ())
    for t in rb.tjanster.values():
        if 'S-TJ-01' in t.sarbarheter:
            p = andrat(p, t.erbjuds_falt, varde=False)
    assert faktorstatus(rb, p, rb.sarbarheter['S-TJ-01']) == 'Inte tillämplig'


def test_kand_hemvist_styrker_inte_effektivt_aml(regelbas_v1):
    rb = regelbas_v1
    p = faktorprofil(rb, ())
    for suffix, antal in [('sverige', p.uppgifter['P-KUND.antal_aktiva'].varde), ('ovriga_ees', 0), ('utanfor_ees', 0)]:
        p = andrat(p, 'P-GEO.antal_hemvist_' + suffix, varde=antal)
    assert lagre_status(rb, p, rb.lagre_risk['L-PTL-04-02']) == 'Finns'
    assert lagre_status(rb, p, rb.lagre_risk['L-PTL-04-03']) == 'Okänt'


def test_fel_period_eller_framtida_bekraftelse_ar_okant(regelbas_v1):
    from datetime import timedelta
    rb = regelbas_v1
    p = andrat(faktorprofil(rb, ()), 'P-KUND.antal_osaker_distansidentitet', varde=0)
    id = 'P-KUND.antal_osaker_distansidentitet'
    period = p.uppgifter[id].period.model_copy(update={'till': p.uppgifter[id].period.till - timedelta(days=1)})
    assert faktorstatus(rb, andrat(p, id, period=period), rb.sarbarheter['S-ARB-08']) == 'Okänt'
    assert faktorstatus(rb, andrat(p, id, datum=p.byra.datum + timedelta(days=1)), rb.sarbarheter['S-ARB-08']) == 'Okänt'


def test_motstridig_andel_och_hemvist_ar_okant(regelbas_v1):
    rb = regelbas_v1
    p = faktorprofil(rb, ('S-KUND-01',), med_bankdata=True)
    p = andrat(p, 'P-KUND.andel_riskbransch', varde=0)
    assert faktorstatus(rb, p, rb.sarbarheter['S-KUND-01']) == 'Okänt'
    for suffix in ('sverige', 'ovriga_ees', 'utanfor_ees'):
        p = andrat(p, 'P-GEO.antal_hemvist_' + suffix, varde=0)
    assert lagre_status(rb, p, rb.lagre_risk['L-PTL-04-02']) == 'Okänt'
