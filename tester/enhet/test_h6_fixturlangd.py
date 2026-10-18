from types import SimpleNamespace

import pytest

from riskanalys.bedomning.motor import bedom_tjanst
from riskanalys.dokument.delvalidering import LANGD
from riskanalys.dokument.skrivversion import V5, V6, delar_for_version
from tester.fixturer.m2 import godkant_delsvar
from tester.fixturer.skrivsvar_v7 import godkant_svar_v7, med_verksamhetsval, tjanstspecifikt_svar_v7
from tester.enhet.test_verksamhetsval_v7 import bas


@pytest.mark.parametrize('version', [V5, V6])
def test_syntetiska_svar_haller_langdkontrakt_for_alla_tjanster(regelbas_v1, version):
    for tj in regelbas_v1.tjanster.values():
        t=SimpleNamespace(tjanst=tj.id,hot=tj.hot)
        for del_id in delar_for_version(version):
            minimum,maximum=LANGD[del_id]
            svar=godkant_delsvar(del_id,t)
            n=sum(len(s.text.split()) for s in svar.stycken)
            assert minimum<=n<=maximum,(version,tj.id,del_id,n)


@pytest.mark.parametrize('byggsvar', [godkant_svar_v7, tjanstspecifikt_svar_v7])
def test_v7_syntetiska_svar_haller_langdkontrakt_for_alla_tjanster(bas, byggsvar):
    rb, p = bas
    p = med_verksamhetsval(rb, p)
    p = p.model_copy(update={'uppgifter': {**p.uppgifter, **{
        tj.erbjuds_falt: p.uppgifter[tj.erbjuds_falt].model_copy(update={'varde': True})
        for tj in rb.tjanster.values()}}})
    minimum, maximum = LANGD['analys']
    for tj in rb.tjanster.values():
        t = bedom_tjanst(rb, tj, p)
        svar = byggsvar(rb, p, t, 'D-ARB.6.1')
        n = sum(len(s.text.split()) for s in svar.stycken)
        assert minimum <= n <= maximum, (tj.id, byggsvar.__name__, n)
