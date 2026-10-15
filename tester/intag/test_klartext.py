from datetime import date

import pytest

from riskanalys.dokument.klartext import (faltnamn, gemen, gransmening, gransmening_text, id_till_namn, kanda_id,
                                          kod_till_namn, paketnamn, punkttext, under_grans, uppgiftstext,
                                          villkorstext)
from riskanalys.profil.hantering import visa_varde_klartext
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


def test_gransmeningens_mall_ar_gemensam():
    assert gransmening_text("andel kunder i riskbranscher", "15 %", "20 %") == (
        "Faktorn förekommer: andel kunder i riskbranscher är 15 %, men det ligger under metodens gräns "
        "på 20 % för automatiskt riskpåslag.")


def test_gransmeningens_mall_skriver_visningen_som_den_ar():
    # Intervallet "mindre än 1 %" kommer färdigt från visa_varde_klartext; mallen gör ingen egen omskrivning.
    text = gransmening_text("andel kunder i riskbranscher", "mindre än 1 %", "20 %")
    assert "är mindre än 1 %, men det ligger under" in text
    assert "är 0 %, men" in gransmening_text("andel kunder i riskbranscher", "0 %", "20 %")


def test_gransmeningen_for_en_andel_som_avrundas_till_noll(rb_intag):
    p = _profil({"P-KUND.andel_riskbransch": _u(0.004)})
    (g,) = under_grans(p, GRANS)
    assert gransmening(rb_intag, p, g).startswith("Faktorn förekommer: andel kunder i riskbranscher är mindre än 1 %,")


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


def test_id_till_namn_byter_kanda_id_mot_namn(rb_intag):
    text = id_till_namn(rb_intag, "Bekräfta P-KUND.andel_riskbransch; T-RED-01: erbjuds.")
    assert text == (f"Bekräfta {gemen(faltnamn(rb_intag, 'P-KUND.andel_riskbransch'))}; "
                    f"{gemen(rb_intag.tjanster['T-RED-01'].namn)}: erbjuds.")


def test_id_till_namn_skriver_namn_mitt_i_meningen_med_liten_bokstav(rb_intag):
    text = id_till_namn(rb_intag, "Bekräfta P-ORG.sateslan; rättslig omfattning kan inte avgöras.")
    assert text == ("Bekräfta län där byrån har sitt säte eller ägaren är folkbokförd; "
                    "rättslig omfattning kan inte avgöras.")


def test_id_till_namn_behaller_stor_bokstav_forst_och_efter_punkt(rb_intag):
    forst = id_till_namn(rb_intag, "P-ORG.sateslan saknas. BT-TILL-19: saknar lydelse. T-RED-01: erbjuds.")
    assert forst == ("Län där byrån har sitt säte eller ägaren är folkbokförd saknas. "
                     f"Punkt {rb_intag.tillamplighet['BT-TILL-19'].punkt}: saknar lydelse. "
                     f"{rb_intag.tjanster['T-RED-01'].namn}: erbjuds.")


def test_id_till_namn_behaller_forkortningar_mitt_i_meningen(rb_intag):
    pep = next(s.id for s in rb_intag.sarbarheter.values() if s.namn.startswith("PEP"))
    assert id_till_namn(rb_intag, f"Granska {pep}.") == f"Granska {rb_intag.sarbarheter[pep].namn}."


def test_kanda_id_ger_unika_kanda_id_i_ordning(rb_intag):
    text = ("Bekräfta P-ORG.sateslan; T-RED-01: x. Okänt P-FINNS.inte och T-OKAND-99, "
            "P-ORG.sateslan igen, BT-TILL-19 och paketet RP-RED-VG.")
    assert kanda_id(rb_intag, text) == ("P-ORG.sateslan", "T-RED-01", "BT-TILL-19")
    assert kanda_id(rb_intag, "Inga ID här.") == ()


def test_id_till_namn_byter_sarbarhet_hot_och_kontroll(rb_intag):
    sarbarhet, hot, kontroll = (next(iter(k)) for k in (rb_intag.sarbarheter, rb_intag.hot, rb_intag.kontroller))
    text = id_till_namn(rb_intag, f"{sarbarhet} och {hot} samt {kontroll}.")
    assert text == (f"{rb_intag.sarbarheter[sarbarhet].namn} och {gemen(rb_intag.hot[hot].namn)} "
                    f"samt {gemen(rb_intag.kontroller[kontroll].namn)}.")


def test_id_till_namn_byter_tillamplighetsrad_mot_punkt(rb_intag):
    rad = rb_intag.tillamplighet["BT-TILL-19"]
    assert id_till_namn(rb_intag, "prövningen BT-TILL-19.") == f"prövningen punkt {rad.punkt}."


def test_id_till_namn_lamnar_okanda_id_och_regelpaket_oforandrade(rb_intag):
    text = "Okänt P-FINNS.inte, T-OKAND-99 och paketet RP-RED-VG."
    assert id_till_namn(rb_intag, text) == text


def test_punkttext_skriver_punkterna_i_ord():
    assert punkttext(()) == "ingen punkt är bekräftad"
    assert punkttext((19,)) == "punkt 19"
    assert punkttext((19, 20)) == "punkterna 19 och 20"
    assert punkttext((19, 20, 21)) == "punkterna 19, 20 och 21"


@pytest.mark.parametrize("varde,text", [
    (0.0, "0 %"), (0.0049, "mindre än 1 %"), (0.005, "mindre än 1 %"), (0.0051, "1 %"),
    (0.9949, "99 %"), (0.995, "mer än 99 %"), (0.9951, "mer än 99 %"), (1.0, "100 %"), (0.15, "15 %"),
])
def test_visa_varde_klartext_for_andelar(rb_intag, varde, text):
    assert visa_varde_klartext(rb_intag.falt["P-KUND.andel_riskbransch"], varde) == text


def test_paketnamn_utan_kod(rb_intag):
    assert paketnamn(rb_intag.regelpaket["RP-RED-VG"]) == "Bokföring, skatterådgivning och bolagstjänster"


def test_kod_till_namn(rb_intag):
    titel = rb_intag.kallor["SRC-PTL"].titel
    assert kod_till_namn(rb_intag, "Lästa: SRC-PTL och SRC-OKAND.") == f"Lästa: {titel} och SRC-OKAND."


def test_kod_till_namn_byter_regelpaket_mot_paketnamn_med_lan(rb_intag):
    # Alla tre regelpaketen heter lika; länen skiljer dem åt.
    paket = rb_intag.regelpaket["RP-RED-VG"]
    namn = f"{paketnamn(paket)} ({', '.join(paket.lan)})"
    assert "Västra Götaland" in namn
    assert kod_till_namn(rb_intag, "Regelpaketet RP-RED-VG, men inte RP-OKANT.") == f"Regelpaketet {namn}, men inte RP-OKANT."


def test_kod_till_namn_ger_olika_text_for_olika_regelpaket(rb_intag):
    text = kod_till_namn(rb_intag, "RP-RED-VG och RP-RED-STHLM")
    assert "RP-" not in text and "Västra Götaland" in text and "Stockholm" in text


def test_kod_till_namn_byter_registrerad_kalla_utan_src_prefix(rb_intag):
    assert "EU-269-2014" in rb_intag.kallor
    assert kod_till_namn(rb_intag, "Källa EU-269-2014.") == f"Källa {rb_intag.kallor['EU-269-2014'].titel}."


def test_kod_till_namn_byter_bara_hela_koder(rb_intag):
    text = "SRC-PTL-X, XSRC-PTL, SRC-PTLX, EU-269-2014-X"
    assert kod_till_namn(rb_intag, text) == text


def test_kod_till_namn_byter_kontrollsumma_mot_hanvisning_till_bilagan(rb_intag):
    summa = rb_intag.kallor["SRC-PTL"].kontrollsumma
    assert summa.startswith("sha256:")
    assert kod_till_namn(rb_intag, f"Version {summa} lästes.") == "Version (kontrollsumma i bilaga B1) lästes."


@pytest.mark.parametrize("skrivet", ["sha256:xyz", "sha256:0123abcdöö", "sha256:ÖÄÅ-123", "sha256:0123abcd_!?x", "sha256:"])
def test_kod_till_namn_byter_ogiltig_text_efter_sha256_mot_hanvisning_till_bilagan(rb_intag, skrivet):
    # Byrån kan skriva vad som helst efter "sha256:"; ingenting av det får stå kvar i löptexten.
    text = kod_till_namn(rb_intag, f"Version {skrivet} lästes.")
    if skrivet == "sha256:":
        assert text == "Version sha256: lästes."  # utan något efter kolonet finns ingen kontrollsumma att dölja
    else:
        assert text == "Version (kontrollsumma i bilaga B1) lästes."


@pytest.mark.parametrize(("skrivet", "vantat"), [
    ("Version sha256:0123abcd.", "Version (kontrollsumma i bilaga B1)."),
    ("Version (sha256:0123abcd), lästes.", "Version ((kontrollsumma i bilaga B1)), lästes."),
    ("Är det sha256:xyz?", "Är det (kontrollsumma i bilaga B1)?"),
    ("Värdet ”sha256:abc”.", "Värdet ”(kontrollsumma i bilaga B1)”."),
    ("Värdet 'sha256:abc'.", "Värdet '(kontrollsumma i bilaga B1)'."),
])
def test_kod_till_namn_behaller_skiljetecken_efter_kontrollsumman(rb_intag, skrivet, vantat):
    assert kod_till_namn(rb_intag, skrivet) == vantat
