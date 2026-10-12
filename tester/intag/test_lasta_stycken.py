from riskanalys.bedomning.motor import bedom
from riskanalys.dokument.analysunderlag import sarbarhetsstycke
from riskanalys.dokument.intagsunderlag import bygg_underlagsbilaga
from riskanalys.dokument.klartext import faltnamn
from riskanalys.dokument.platshallare import faltid_fel
from riskanalys.dokument.uppfoljning import omfattningsstycke
from riskanalys.profil.omfattning import harled_andelar
from riskanalys.regelverk.urval import valj
from tester.fixturer.m2 import DAG


def _id_for(rb, falt_id):
    return next(s.id for s in rb.sarbarheter.values() if s.villkor.get("falt") == falt_id)


def _med_riskbransch(rb, klar, antal):
    """Testprofilen har 100 aktiva kunder; andelen härleds ur antalet, som i intaget."""
    u = klar.uppgifter["P-KUND.antal_riskbransch"].model_copy(update={"varde": antal})
    profil = klar.model_copy(update={"uppgifter": {**klar.uppgifter, "P-KUND.antal_riskbransch": u}})
    return harled_andelar(profil, rb, frozenset({"P-KUND.antal_riskbransch"}))


def test_sarbarhetsstycke_ar_klartext_med_referenser(rb_intag, klar):
    id = _id_for(rb_intag, "P-GEO.andel_utland_transaktion")
    s = sarbarhetsstycke(rb_intag, klar, "T-RED-01", id)
    assert not faltid_fel(1, s.text) and "SEKTOR-" not in s.text and ">" not in s.text
    assert "Sårbarheten gäller om andel kunder med transaktioner utanför Sverige är större än 0 %." in s.text
    assert "P-GEO.andel_utland_transaktion" in s.referenser
    assert "Faktorn förekommer" not in s.text


def test_harledd_andel_har_klartext_som_kalla(rb_intag, klar):
    id = _id_for(rb_intag, "P-GEO.andel_utland_transaktion")
    s = sarbarhetsstycke(rb_intag, klar, "T-RED-01", id)
    assert "källa: härledd ur bekräftade uppgifter" in s.text and "Härledning" not in s.text


def test_harledd_andel_i_lopande_text_for_s_kund_01(rb_intag, klar):
    s = sarbarhetsstycke(rb_intag, _med_riskbransch(rb_intag, klar, 15), "T-RED-01", "S-KUND-01")
    assert "härledd ur bekräftade uppgifter" in s.text and "Härledning" not in s.text


def test_faktor_under_gransen_i_lasta_stycket(rb_intag, klar):
    id = _id_for(rb_intag, "P-KUND.andel_riskbransch")
    s = sarbarhetsstycke(rb_intag, _med_riskbransch(rb_intag, klar, 15), "T-RED-01", id)
    assert "Villkoret är inte uppfyllt." in s.text
    assert "Faktorn förekommer: andel kunder i riskbranscher är 15 %, men det ligger under metodens gräns på 20 %" in s.text


def test_saknat_geografiunderlag_ger_fortfarande_verifiera(rb_intag, klar):
    utan = klar.model_copy(update={"uppgifter": {k: v for k, v in klar.uppgifter.items() if k != "P-BESK.geografi"}})
    geo = next(id for id in rb_intag.tjanster["T-RED-01"].sarbarheter if rb_intag.sarbarheter[id].omrade == "geo")
    assert "[VERIFIERA]" in sarbarhetsstycke(rb_intag, utan, "T-RED-01", geo).text


def test_bilagan_visar_kortnamn_och_falt_id(rb_intag, klar):
    # Andelsfälten härleds och har inget intag; antalsfältet och kortnamnen finns i bilagan.
    bilaga = bygg_underlagsbilaga(rb_intag, klar)
    rad = next(s.text for s in bilaga.stycken if s.referenser == ["P-ORG.antal_anstallda"])
    assert rad.startswith("Antal personer som arbetar på byrån (P-ORG.antal_anstallda): ")
    assert " = " not in rad and "Källa: " not in rad


def test_bilagan_har_rad_for_harledd_andel_med_oforandrad_kalla(rb_intag, klar):
    bilaga = bygg_underlagsbilaga(rb_intag, _med_riskbransch(rb_intag, klar, 15))
    rad = next(s.text for s in bilaga.stycken if s.referenser == ["P-KUND.andel_riskbransch"])
    assert rad.startswith("Andel kunder i riskbranscher (P-KUND.andel_riskbransch): ")
    assert "Härledning: P-KUND.antal_riskbransch/P-KUND.antal_aktiva" in rad


def test_bilagans_rader_har_kortnamn_och_falt_id_i_borjan(rb_intag, klar):
    bilaga = bygg_underlagsbilaga(rb_intag, klar)
    falt_rader = [s for s in bilaga.stycken if s.referenser[0] in rb_intag.falt]
    assert falt_rader
    for stycke in falt_rader:
        id = stycke.referenser[0]
        assert stycke.text.startswith(f"{faltnamn(rb_intag, id)} ({id}): "), stycke.text


def test_bilagans_personuppgiftsrad_har_kortnamn_och_falt_id(rb_intag, klar):
    bilaga = bygg_underlagsbilaga(rb_intag, klar)
    personrader = [s for s in bilaga.stycken if s.referenser[0] in rb_intag.falt
                   and rb_intag.falt[s.referenser[0]].personuppgift]
    assert personrader
    for s in personrader:
        id = s.referenser[0]
        assert s.text == (f"{faltnamn(rb_intag, id)} ({id}): personuppgift hanteras lokalt i ansvarsfördelningen; "
                          "källa och datum finns i profilen.")


def test_bilagans_harledda_rader_foljer_regelbasens_faltordning(rb_intag, klar):
    bilaga = bygg_underlagsbilaga(rb_intag, klar)
    ordning = list(rb_intag.falt)
    ids = [s.referenser[0] for s in bilaga.stycken if s.referenser[0] in rb_intag.falt]
    assert ids == sorted(ids, key=ordning.index)


def test_omfattningsstycket_namnger_saknade_uppgifter_utan_falt_id(rb_intag, klar):
    saknas = {"P-ORG.antal_anstallda", "P-VERK.omsattning"}
    profil = klar.model_copy(update={"uppgifter": {k: (u.model_copy(update={"status": "saknas"}) if k in saknas else u)
                                                   for k, u in klar.uppgifter.items()}})
    b = bedom(rb_intag, valj(rb_intag, profil.byra.regelpaket, DAG, profil.byra.lan), profil)
    assert set(b.proportionalitet.okanda_uppgifter) >= saknas
    s = omfattningsstycke(rb_intag, profil, b)
    assert faltid_fel(1, s.text) == [] and "[VERIFIERA]" in s.text
    assert "Uppgifter saknas: " in s.text and faltnamn(rb_intag, "P-ORG.antal_anstallda") in s.text
    assert saknas <= set(s.referenser)
