"""En läsklar syntetisk V8-bas; varje prov arbetar i egen kopia."""
import pytest
from tester.fixturer.analys_hela_kedjan import syntetisk_expertkopia,bygg_bunden_kedja,DAG
from tester.fixturer.kedjecache import klona_kedja


@pytest.fixture(scope='session')
def resultatkedja_bas(tmp_path_factory):
    from riskanalys.dokument import rapportversion
    rot=tmp_path_factory.mktemp('resultat-v9-bas').resolve()
    regelrot,rb=syntetisk_expertkopia(rot/'expert')
    # Basen skyddar uttryckligen gamla V8-utkast även efter standardbytet.
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(rapportversion,'AKTUELL_DOKUMENTVERSION',rapportversion.V8)
        return bygg_bunden_kedja(rb,rot/'kedja',regelrot=regelrot,godkann=True)


@pytest.fixture
def resultatkedja(resultatkedja_bas,tmp_path):
    return klona_kedja(resultatkedja_bas,tmp_path)
