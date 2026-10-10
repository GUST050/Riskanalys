import riskanalys
from riskanalys.fel import RiskanalysFel


def test_paketet_har_versionsnummer():
    assert riskanalys.__version__ == "0.1.0"


def test_riskanalysfel_ar_ett_vanligt_undantag():
    fel = RiskanalysFel("Något gick fel.")
    assert isinstance(fel, Exception)
    assert str(fel) == "Något gick fel."
