"""Låsta erfarenhets- och geografistycken i v6 med endast syntetiska uppgifter och Testleverantor."""
import re

import pytest

from riskanalys.dokument.arb_v6 import bygg_arb_v6
from riskanalys.dokument.lasta_v6 import erfarenhetsstycke_v6, geografistycke_v6
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.regelverk.granser import metodgransindex
from tester.fixturer.m2 import PERIOD
from tester.fixturer.arb_kedja import HISTORIK, andrat, bedom_kedja, granska_kedja, med_avsnitt, syntetisk_profil, v6_kedja

RAPPORTER = "P-VERK.antal_rapporter"
AVBOJANDEN = "P-VERK.antal_avbojanden"
INTERNA_ID = re.compile(r"\b(?:P|S|T|H|K)-[A-ZÅÄÖ]+[.\-]")


@pytest.fixture
def profil(regelbas_v1):
    return syntetisk_profil(regelbas_v1)


def forsta_tjanst(rb, p):
    _, b = bedom_kedja(rb, p)
    return tjanster_med_avsnitt(b)[0][1]


def test_lamnade_rapporter_ar_ingen_riskpoang_och_avbojanden_ar_inte_rapporter(regelbas_v1, profil):
    p = andrat(andrat(profil, RAPPORTER, varde=3), AVBOJANDEN, varde=2)
    (s,) = erfarenhetsstycke_v6(regelbas_v1, p, forsta_tjanst(regelbas_v1, p), gransindex=metodgransindex(regelbas_v1))
    assert "misstankerapporter 3" in s.text and "avböjanden 2" in s.text
    assert "ingen riskpoäng" in s.text and "Noll rapporter" not in s.text
    assert "inte lämnade rapporter" in s.text and "[VERIFIERA]" not in s.text


def test_okant_geografiskt_villkor_namnges_och_markeras(regelbas_v1, profil):
    p = andrat(profil, "P-RISK.korruption", status="saknas")
    t = forsta_tjanst(regelbas_v1, p)
    (s,) = geografistycke_v6(regelbas_v1, p, t.tjanst, gransindex=metodgransindex(regelbas_v1))
    assert "okänt: " + regelbas_v1.sarbarheter["S-ARB-12"].namn + " [VERIFIERA]" in s.text
    assert "S-ARB-12" in s.referenser and "Noll" not in s.text


def test_lasta_stycken_ar_klartext_utan_interna_id(regelbas_v1, profil):
    t = forsta_tjanst(regelbas_v1, profil)
    index = metodgransindex(regelbas_v1)
    for s in (*erfarenhetsstycke_v6(regelbas_v1, profil, t, gransindex=index),
              *geografistycke_v6(regelbas_v1, profil, t.tjanst, gransindex=index)):
        assert not INTERNA_ID.search(s.text), s.text
        assert s.proveniens == "regelbas"


def test_andrat_erfarenhetsstycke_ger_b15(regelbas_v1, profil):
    k = v6_kedja(regelbas_v1, profil)
    id, _ = tjanster_med_avsnitt(k.bedomning)[0]
    a = k.dokument.avsnitt_med_id()[id]
    stycken = tuple(s.model_copy(update={"text": s.text.replace("Noll rapporter visar inte frånvaro av hot.", "Inga hot.")})
                    if RAPPORTER in s.referenser else s for s in a.stycken)
    fynd = [f for f in granska_kedja(regelbas_v1, k, profil, med_avsnitt(k.dokument, a.model_copy(update={"stycken": stycken})))
            if f.regel == "B-15"]
    assert [(f.avsnitt, f.allvar) for f in fynd] == [(id, "blockerande")]


def test_mall_for_sarbarheter_har_geografin_en_gang_i_det_lasta_stycket(regelbas_v1, profil):
    k = v6_kedja(regelbas_v1, profil)
    id, _ = tjanster_med_avsnitt(k.bedomning)[0]
    r = k.resultat[id]
    mall = r.del_("sarbarheter").model_copy(update={"mall": True})
    resultat = {**k.resultat, id: r.model_copy(update={"delar": (r.del_("hot"), mall)})}
    d = bygg_arb_v6(regelbas_v1, profil, k.bedomning, resultat, HISTORIK, analys=None)
    geo = [s for s in d.avsnitt_med_id()[id].stycken if "S-GEO-01" in s.referenser and "Sårbarheten gäller om" in s.text]
    assert len(geo) == 1 and geo[0].proveniens == "regelbas"
    assert bygg_arb_v6(regelbas_v1, profil, k.bedomning, resultat, HISTORIK, analys=None) == d


GEO_BYRA = "P-BESK.geografi"
GEO_RED = "P-TJ.red01_geografi"
GEO_TEXT = "Kundernas verksamheter finns i Västra Götaland och Halland."


@pytest.fixture
def profil_med_lika_geografi(profil):
    return andrat(andrat(profil, GEO_BYRA, varde=GEO_TEXT), GEO_RED, varde=GEO_TEXT)


@pytest.fixture
def profil_med_olika_geografi(profil):
    return andrat(andrat(profil, GEO_BYRA, varde=GEO_TEXT), GEO_RED, varde="Tjänstens kunder finns i Skåne.")


def geo(rb, p, tjanst="T-RED-01"):
    (s,) = geografistycke_v6(rb, p, tjanst, gransindex=metodgransindex(rb))
    return s


def test_identisk_tjanstegeografi_skrivs_en_gang(regelbas_v1, profil_med_lika_geografi):
    s = geo(regelbas_v1, profil_med_lika_geografi)
    assert s.text.count("Kundernas verksamheter finns") == 1
    assert "Byråns geografibeskrivning" in s.text and "Tjänstens geografi" not in s.text
    assert {GEO_BYRA, GEO_RED} <= set(s.referenser)


def test_olika_tjanstegeografi_skrivs_ut(regelbas_v1, profil_med_olika_geografi):
    s = geo(regelbas_v1, profil_med_olika_geografi)
    assert "Tjänstens geografi" in s.text and "Skåne" in s.text
    assert {GEO_BYRA, GEO_RED} <= set(s.referenser)


@pytest.mark.parametrize("falt, uppdatering", [
    ("kalla", {"kalla": "Annan syntetisk källa"}),
    ("period", {"period": PERIOD}),
])
def test_samma_text_med_annan_kalla_eller_period_skrivs_ut(regelbas_v1, profil_med_lika_geografi, falt, uppdatering):
    p = andrat(profil_med_lika_geografi, GEO_RED, **uppdatering)
    assert "Tjänstens geografi" in geo(regelbas_v1, p).text


def test_tjanstegeografi_utan_underlag_skrivs_ut_som_saknad(regelbas_v1, profil_med_lika_geografi):
    p = andrat(profil_med_lika_geografi, GEO_RED, status="saknas")
    assert "Tjänstens geografi: aktuellt bekräftat underlag saknas" in geo(regelbas_v1, p).text
