"""Samma leverantörsval och fel för samtliga ingångar, utan nätverk."""
import pytest
from riskanalys.fel import RiskanalysFel


def test_testleverantor_kraver_svarsfil():
    from riskanalys.konfiguration import Skrivkonfiguration, skapa_textleverantor
    with pytest.raises(RiskanalysFel, match='--testsvar'):
        skapa_textleverantor(Skrivkonfiguration(leverantor='test'))


def test_sparade_svar_lases_utan_api_nyckel(testsvarsfil, monkeypatch):
    from riskanalys.konfiguration import Skrivkonfiguration, skapa_textleverantor
    from riskanalys.dokument.leverantor import Testleverantor
    monkeypatch.delenv('ANTHROPIC_API_KEY', raising=False)
    assert isinstance(skapa_textleverantor(Skrivkonfiguration(leverantor='test', testsvar=testsvarsfil)), Testleverantor)


def test_claude_kraver_nyckel(monkeypatch):
    from riskanalys.konfiguration import Skrivkonfiguration, skapa_textleverantor
    monkeypatch.delenv('ANTHROPIC_API_KEY', raising=False)
    with pytest.raises(RiskanalysFel, match='ANTHROPIC_API_KEY'):
        skapa_textleverantor(Skrivkonfiguration())


def test_modell_och_effort_fors_vidare_utan_anrop(monkeypatch):
    from riskanalys import konfiguration as k
    monkeypatch.setenv('ANTHROPIC_API_KEY', 'syntetisk-ingen-natverkstrafik')
    class Leverantor:
        def __init__(self, *, modell, effort):
            self.modell, self.effort = modell, effort
    monkeypatch.setattr(k, 'ClaudeLeverantor', Leverantor)
    r = k.skapa_textleverantor(k.Skrivkonfiguration(modell='lokal-modell', effort='low'))
    assert (r.modell, r.effort) == ('lokal-modell', 'low')


def test_okand_leverantor_avvisas():
    from riskanalys.konfiguration import Skrivkonfiguration, skapa_textleverantor
    with pytest.raises(RiskanalysFel, match='leverantör'):
        skapa_textleverantor(Skrivkonfiguration(leverantor='okand'))
