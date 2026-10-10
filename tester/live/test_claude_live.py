"""Livetest mot det riktiga Claude-API:t. Kostar pengar. Körs bara med RISKANALYS_LIVE=1."""

import os

import pytest

from riskanalys.dokument.claude import ClaudeLeverantor
from riskanalys.dokument.skrivning import skriv_avsnitt

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(os.environ.get("RISKANALYS_LIVE") != "1", reason="Livetester körs bara med RISKANALYS_LIVE=1."),
]


def test_claude_skriver_ett_godkant_avsnitt(real_underlag):
    resultat = skriv_avsnitt(ClaudeLeverantor(), real_underlag, ("Testa Testsson",))
    assert resultat.godkant_utkast is not None, resultat.forsok[-1].fel
    anrop = resultat.forsok[-1].anrop
    assert anrop.svar_id
    assert anrop.svarsmodell
    assert sum(post.utdata_token for post in anrop.anvandning) > 0
