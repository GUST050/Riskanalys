"""Delat syntetiskt underlag till rena V9-prov; inga riktiga AI-anrop."""
from types import SimpleNamespace
import pytest
from docs.research.verktyg.analyslagen import bygg
from riskanalys.dokument.arb_v8 import bygg_arb_v8
from riskanalys.drift.historik import Historik
from tester.enhet.test_arb_v8 import skriv


@pytest.fixture(scope='module')
def resultatfall(regelbas_v1, tmp_path_factory):
    f = bygg(regelbas_v1, tmp_path_factory.mktemp('resultatrapport'), 'fyra_tjanster', 'direkt2')
    resultat = skriv(f)
    historik = Historik()
    d = bygg_arb_v8(f.regelbas, f.profil, f.bedomning, resultat, historik, analys=f.analys)
    return SimpleNamespace(**vars(f), resultat=resultat, historik=historik, dokument=d)


def underlag(f, **kwargs):
    from riskanalys.dokument.resultatunderlag_v9 import bygg_resultatunderlag
    return bygg_resultatunderlag(f.regelbas, f.profil, f.bedomning, f.resultat, f.historik,
                                analys=kwargs.get('analys', f.analys), analysdokument=f.dokument)
