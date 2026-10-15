from types import SimpleNamespace
from riskanalys.dokument.delvalidering import LANGD
from tester.fixturer.m2 import godkant_delsvar

def test_syntetiska_svar_haller_langdkontrakt_for_alla_tjanster(regelbas_v1):
    for tj in regelbas_v1.tjanster.values():
        t=SimpleNamespace(tjanst=tj.id,hot=tj.hot)
        for del_id,(minimum,maximum) in LANGD.items():
            svar=godkant_delsvar(del_id,t)
            n=sum(len(s.text.split()) for s in svar.stycken)
            assert minimum<=n<=maximum,(tj.id,del_id,n)
