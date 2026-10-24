"""Läsning av YAML: samma säkra tolkning, men med libyaml när den finns."""
from datetime import date

import pytest
import yaml

from riskanalys.lagring import yamlfil

TEXT = """\
byra:
  id: syntetisk
  datum: 2026-10-10
uppgifter:
  P-ORG.namn: {varde: 'Åsa & Örjan AB', status: bekräftad, period: null}
  P-TJ.red01_erbjuds: {varde: true, antal: 3, andel: 0.25}
lista: [a, 'b: c', "\\u00e5"]
"""


def test_samma_resultat_som_ren_safe_load():
    assert yamlfil.las_yaml_text(TEXT) == yaml.safe_load(TEXT)
    assert yamlfil.las_yaml_text(TEXT)['byra']['datum'] == date(2026, 10, 10)


def test_anvander_libyaml_nar_den_finns():
    if not yaml.__with_libyaml__:
        pytest.skip('PyYAML saknar libyaml i denna miljö.')
    assert yamlfil.YAMLLASARE is yaml.CSafeLoader


@pytest.mark.parametrize('text', ['a: [1, 2', '!!python/object/apply:os.system [echo]'])
def test_ogiltig_eller_osaker_yaml_avvisas(text):
    with pytest.raises(yaml.YAMLError):
        yamlfil.las_yaml_text(text)
