from datetime import date

import pytest

from riskanalys.dokument.klartext import faltnamn, gemen, gransmening, under_grans, uppgiftstext, villkorstext
from riskanalys.profil.modeller import Byra, Period, Profil, Uppgift

PER = Period(fran=date(2025, 1, 1), till=date(2025, 12, 31))


def _u(varde, status="bekräftad"):
    return Uppgift(varde=varde, period=PER, status=status, kalla="Syntetisk statistik",
                   datum=date(2026, 10, 10), bekraftad_av="roll:FfR")


def _profil(uppgifter):
    return Profil(byra=Byra(id="syntetisk", regelpaket="RP-RED-VG", datum=date(2026, 10, 10), lan="Västra Götaland"),
                  uppgifter=uppgifter)


GRANS = {"falt": "P-KUND.andel_riskbransch", "op": ">=", "varde": 0.2}


def test_faltnamn_anvander_etikett_och_monster(rb_intag):
    assert faltnamn(rb_intag, "P-KUND.andel_riskbransch") == "Andel kunder i riskbranscher"
    assert faltnamn(rb_intag, "P-TJ.red01_antal_kunder") == "Antal kunder i löpande bokföring"
    assert faltnamn(rb_intag, "P-KONTROLL.C-07.effekt") == "Dokumenterad verkan av kontrollen bankavstämning mot underlag"


def test_kontrollnamn_som_borjar_med_kontroll_upprepar_inte_ordet(rb_intag):
    assert faltnamn(rb_intag, "P-KONTROLL.C-TJ-01.effekt") == "Dokumenterad verkan av kontroll av löpande bokföring"
    assert faltnamn(rb_intag, "P-KONTROLL.C-TJ-01.utfall") == "Prov och utfall för kontroll av löpande bokföring"
    assert faltnamn(rb_intag, "P-KONTROLL.C-07.utfall") == "Prov och utfall för kontrollen bankavstämning mot underlag"


def test_gemen_behaller_forkortningar():
    assert gemen("Andel kunder i riskbranscher") == "andel kunder i riskbranscher"
    assert gemen("PEP, familjemedlem eller känd medarbetare") == "PEP, familjemedlem eller känd medarbetare"
    assert gemen("EU-högrisktredjeland") == "EU-högrisktredjeland"


@pytest.mark.parametrize("villkor,text", [
    (GRANS, "andel kunder i riskbranscher är minst 20 %"),
    ({"falt": "P-GEO.andel_utland_transaktion", "op": ">", "varde": 0},
     "andel kunder med transaktioner utanför Sverige är större än 0 %"),
    ({"falt": "P-KANAL.bankdata_andel", "op": "<", "varde": 0.5},
     "andel kunder där byrån har tillgång till bankdata är mindre än 50 %"),
    ({"falt": "P-RISK.korruption", "op": "==", "varde": True},
     "uppgiften ”Anknytning till land eller område med korruption” är ja"),
    ({"falt": "P-RISK.korruption", "op": "!=", "varde": True},
     "uppgiften ”Anknytning till land eller område med korruption” är nej"),
    ({"alla": [GRANS, {"falt": "P-KANAL.bankdata_andel", "op": "<", "varde": 0.5}]},
     "andel kunder i riskbranscher är minst 20 % och andel kunder där byrån har tillgång till bankdata är mindre än 50 %"),
])
def test_villkor_skrivs_i_ord(rb_intag, villkor, text):
    assert villkorstext(villkor, rb_intag) == text


def test_faktor_under_gransen_beskrivs_som_forekommande(rb_intag):
    p = _profil({"P-KUND.andel_riskbransch": _u(0.15)})
    (g,) = under_grans(p, GRANS)
    assert gransmening(rb_intag, p, g) == (
        "Faktorn förekommer: andel kunder i riskbranscher är 15 %, men det ligger under metodens gräns "
        "på 20 % för automatiskt riskpåslag.")


@pytest.mark.parametrize("uppgift", [None, _u(0), _u(0.25), _u(0.15, status="föreslagen")])
def test_ingen_gransmening_utan_bekraftad_forekomst_under_gransen(uppgift):
    p = _profil({"P-KUND.andel_riskbransch": uppgift} if uppgift else {})
    assert under_grans(p, GRANS) == ()


def test_uppgiftstext_utan_falt_id_och_med_id_i_bilagan(rb_intag):
    p = _profil({"P-KUND.andel_riskbransch": _u(0.15)})
    assert uppgiftstext(rb_intag, p, "P-KUND.andel_riskbransch") == (
        "Andel kunder i riskbranscher: 15 % (period 2025-01-01–2025-12-31; källa: Syntetisk statistik; "
        "bekräftad 2026-10-10).")
    assert uppgiftstext(rb_intag, p, "P-KUND.andel_riskbransch", med_id=True).startswith(
        "Andel kunder i riskbranscher (P-KUND.andel_riskbransch): 15 %")


def test_saknat_underlag_behaller_verifiera(rb_intag):
    assert uppgiftstext(rb_intag, _profil({}), "P-KUND.andel_riskbransch") == (
        "Andel kunder i riskbranscher: aktuellt bekräftat underlag saknas. [VERIFIERA]")


def test_varje_sarbarhetsvillkor_skrivs_utan_att_forekomma_ihop_med_ja_nej_falt(rb_intag):
    texter = {id_: villkorstext(sarbarhet.villkor, rb_intag) for id_, sarbarhet in rb_intag.sarbarheter.items()}
    assert texter
    assert [id_ for id_, text in texter.items() if "förekommer" in text] == []


def test_tjanstesarbarhet_skrivs_som_ja_nej_uppgift(rb_intag):
    assert villkorstext(rb_intag.sarbarheter["S-TJ-01"].villkor, rb_intag) == (
        "uppgiften ”Betalningar och attest i kundens namn erbjuds” är ja")


def test_samma_falt_tva_ganger_ger_en_gransmening(rb_intag):
    p = _profil({"P-KUND.andel_riskbransch": _u(0.15)})
    assert len(under_grans(p, {"alla": [GRANS, GRANS]})) == 1
    assert under_grans(p, {"nagon": [GRANS, {"alla": [GRANS]}]}) == under_grans(p, GRANS)
