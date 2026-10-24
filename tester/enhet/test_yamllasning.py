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


def test_avbrott_fore_namnbyte_bevarar_gammal_yaml(tmp_path, monkeypatch):
    import os
    from riskanalys.fel import RiskanalysFel
    fil = tmp_path/'svar.yaml'
    yamlfil.spara_yaml(fil, {'text':'ursprunglig'})
    fore = fil.read_bytes()
    def avbrott(fd):
        raise OSError('syntetiskt diskfel')
    monkeypatch.setattr(os,'fsync',avbrott)
    with pytest.raises(RiskanalysFel,match='sparas'):
        yamlfil.spara_yaml(fil,{'text':'ändrad'})
    assert fil.read_bytes() == fore
    assert not list(tmp_path.glob('*.tmp'))


def test_fel_efter_namnbyte_redovisar_att_filen_ar_sparad(tmp_path, monkeypatch):
    import os
    from riskanalys.fel import RiskanalysFel
    fil=tmp_path/'svar.yaml'
    yamlfil.spara_yaml(fil,{'text':'ursprunglig'})
    original=os.fsync
    n=0
    def avbrott(fd):
        nonlocal n
        n+=1
        if n==2:raise OSError('syntetiskt fel efter replace')
        return original(fd)
    monkeypatch.setattr(os,'fsync',avbrott)
    with pytest.raises(RiskanalysFel,match='har sparats'):
        yamlfil.spara_yaml(fil,{'text':'ändrad'})
    assert yamlfil.las_yaml(fil)=={'text':'ändrad'}


def test_atomisk_yaml_bevarar_bytes_och_privata_behorigheter(tmp_path):
    data={'text':'Åsa & Örjan','datum':date(2026,10,24)}
    fil=tmp_path/'svar.yaml'
    yamlfil.spara_yaml(fil,data)
    assert fil.read_text()==yaml.safe_dump(data,allow_unicode=True,sort_keys=False)
    assert fil.stat().st_mode & 0o777 == 0o600
