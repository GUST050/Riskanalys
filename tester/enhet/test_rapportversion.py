from pathlib import Path


def test_en_enda_aktuell_dokumentversion():
    from riskanalys.dokument import rapportversion, skrivversion
    assert not hasattr(skrivversion,'AKTUELL_DOKUMENTVERSION')
    assert not hasattr(rapportversion,'AKTUELL_RAPPORTVERSION')
    assert skrivversion.AKTUELL_SKRIVVERSION == skrivversion.V8


def test_enkel_konstant_valjer_v10_for_nya_rapporter():
    from riskanalys.dokument.rapportversion import AKTUELL_DOKUMENTVERSION
    assert AKTUELL_DOKUMENTVERSION == 'D-ARB-resultat-v10'


def test_v6_v7_byggare_far_inte_v9_som_skrivformatsfallback(monkeypatch):
    from riskanalys.dokument import rapportversion
    from riskanalys.dokument.arb_v6 import kontrollera_v6_utkast
    from riskanalys.fel import RiskanalysFel
    import pytest
    monkeypatch.setattr(rapportversion,'AKTUELL_DOKUMENTVERSION',rapportversion.V9)
    with pytest.raises(RiskanalysFel) as e:
        kontrollera_v6_utkast({})
    assert rapportversion.V9 not in str(e.value)
