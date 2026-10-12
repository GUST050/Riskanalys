import os

import pytest

from riskanalys.dokument.claude import ClaudeLeverantor
from riskanalys.dokument.delskrivning import skriv_tjanst
from tester.fixturer.m2 import tjanst_for_prov

pytestmark = pytest.mark.live
from tester.intag.conftest import rb_intag, tom, klar


@pytest.mark.skipif(os.environ.get("RISKANALYS_LIVE") != "1" or not os.environ.get("ANTHROPIC_API_KEY"), reason="kräver riktig nyckel")
def test_andra_delanropet_traffar_cachen(tmp_path, rb_intag, klar):
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    res = skriv_tjanst(ClaudeLeverantor(modell="claude-sonnet-5-5", effort="high"), rb_intag, klar, t, avsnitt_id,
                       design="B", effort="high", personnamn=(), spara=lambda d, f: None)
    andra = res.delar[1].forsok[0].anrop.anvandning
    assert sum(p.cache_lasning_token for p in andra) > 0
