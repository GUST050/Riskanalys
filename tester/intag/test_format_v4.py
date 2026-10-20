import pytest

from riskanalys.dokument.delskrivning import FORMATVERSION, kontrollera_resultat, skriv_tjanst
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.modeller import Avsnitt, Dokument, Textstycke
from riskanalys.dokument.promptar import DELAR
from riskanalys.fel import RiskanalysFel

from tester.fixturer.m2 import godkant_delsvar, tjanst_for_prov


def _avsnitt(version):
    return Avsnitt(id="D-ARB.6.1", rubrik="Analys", kalla="ai",
                   stycken=(Textstycke(typ="beskrivning", text="Text.", referenser=["T-RED-01"]),),
                   formatversion=version)


def test_aktuellt_skrivformat_ar_v8():
    assert FORMATVERSION == "D-ARB-tjanst-v8"


def test_dokument_i_v3_kan_fortfarande_lasas():
    gammalt = Dokument(id="D", titel="T", avsnitt=(_avsnitt("D-ARB-tjanst-v3"),))
    assert Dokument.model_validate_json(gammalt.model_dump_json()).formatversion == "D-ARB-tjanst-v3"
    assert Dokument(id="D", titel="T", avsnitt=(_avsnitt("D-ARB-tjanst-v4"),)).formatversion == "D-ARB-tjanst-v4"


def test_ny_formatversion_ger_ny_kontrollsumma():
    assert _avsnitt("D-ARB-tjanst-v3").kontrollsumma() != _avsnitt("D-ARB-tjanst-v4").kontrollsumma()


def test_utkast_i_v3_maste_skrivas_om(tmp_path, rb_intag, klar):
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    lev = Testleverantor([godkant_delsvar(d, t) for d in DELAR])
    res = skriv_tjanst(lev, rb_intag, klar, t, avsnitt_id, effort="medium", personnamn=(), spara=lambda d, f: None, formatversion="D-ARB-tjanst-v5")
    gammal = type(res).model_validate_json(res.model_copy(update={"formatversion": "D-ARB-tjanst-v3"}).model_dump_json())
    with pytest.raises(RiskanalysFel, match="Skriv om"):
        kontrollera_resultat(rb_intag, klar, t, gammal, avsnitt_id, formatversion="D-ARB-tjanst-v5")
