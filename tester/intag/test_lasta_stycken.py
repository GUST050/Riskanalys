from datetime import date

from riskanalys.bedomning.motor import bedom
from riskanalys.dokument.analysunderlag import sarbarhetsstycke
from riskanalys.dokument.arb import bygg_arb
from riskanalys.dokument.delskrivning import skriv_tjanst
from riskanalys.dokument.intagsunderlag import bygg_underlagsbilaga
from riskanalys.dokument.klartext import faltnamn, gemen
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.nivatext import sektorsmening, sektorsstycken
from riskanalys.dokument.platshallare import faltid_fel
from riskanalys.dokument.promptar import DELAR
from riskanalys.dokument.tjanstavsnitt import bygg_tjanstavsnitt_v3
from riskanalys.dokument.uppfoljning import omfattningsstycke
from riskanalys.drift.historik import Historik
from riskanalys.profil.modeller import Period
from riskanalys.profil.omfattning import harled_andelar
from riskanalys.regelverk.urval import valj
from tester.fixturer.m2 import DAG, godkant_delsvar, tjanst_for_prov


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


def test_litet_men_positivt_antal_i_riskbranscher_skrivs_som_mindre_an_en_procent(rb_intag, klar):
    # 8 av 2 000 är 0,4 %, som visas som "0 %". Det får inte se ut som att faktorn saknas.
    aktiva = klar.uppgifter["P-KUND.antal_aktiva"].model_copy(update={"varde": 2000})
    profil = klar.model_copy(update={"uppgifter": {**klar.uppgifter, "P-KUND.antal_aktiva": aktiva}})
    profil = harled_andelar(_med_riskbransch(rb_intag, profil, 8), rb_intag, frozenset({"P-KUND.antal_aktiva"}))
    id = _id_for(rb_intag, "P-KUND.andel_riskbransch")
    text = sarbarhetsstycke(rb_intag, profil, "T-RED-01", id).text
    assert "Faktorn förekommer: andel kunder i riskbranscher är mindre än 1 %, men det ligger under" in text
    assert "är 0 %, men" not in text


def test_saknat_geografiunderlag_ger_fortfarande_verifiera(rb_intag, klar):
    utan = klar.model_copy(update={"uppgifter": {k: v for k, v in klar.uppgifter.items() if k != "P-BESK.geografi"}})
    geo = next(id for id in rb_intag.tjanster["T-RED-01"].sarbarheter if rb_intag.sarbarheter[id].omrade == "geo")
    assert "[VERIFIERA]" in sarbarhetsstycke(rb_intag, utan, "T-RED-01", geo).text


def test_bilagan_visar_kortnamn_och_falt_id(rb_intag, klar):
    # Raden för ett intagsfält visar kortnamn och fält-ID, utan råsvarets form. Härledda andelar har egna rader, se nedan.
    bilaga = bygg_underlagsbilaga(rb_intag, klar)
    rad = next(s.text for s in bilaga.stycken if s.referenser == ["P-ORG.antal_anstallda"])
    assert rad.startswith("Antal personer som arbetar på byrån (P-ORG.antal_anstallda): ")
    assert " = " not in rad and "Källa: " not in rad


def test_bilagan_har_rad_for_harledd_andel_med_oforandrad_kalla(rb_intag, klar):
    bilaga = bygg_underlagsbilaga(rb_intag, _med_riskbransch(rb_intag, klar, 15))
    rad = next(s.text for s in bilaga.stycken if s.referenser == ["P-KUND.andel_riskbransch"])
    assert rad.startswith("Andel kunder i riskbranscher (P-KUND.andel_riskbransch): ")
    assert "Härledning: P-KUND.antal_riskbransch/P-KUND.antal_aktiva" in rad


def test_bilagan_forklarar_varfor_en_andel_inte_kan_harledas(rb_intag, klar):
    # Antalet nya kunder avser en annan period än de aktiva kunderna, så andelen går inte att härleda.
    annan = Period(fran=date(2024, 1, 1), till=date(2024, 12, 31))
    antal = klar.uppgifter["P-KUND.antal_nya"].model_copy(update={"period": annan})
    profil = klar.model_copy(update={"uppgifter": {**klar.uppgifter, "P-KUND.antal_nya": antal}})
    profil = harled_andelar(profil, rb_intag, frozenset({"P-KUND.antal_nya"}))
    rad = next(s.text for s in bygg_underlagsbilaga(rb_intag, profil).stycken if s.referenser == ["P-KUND.andel_nya"])
    assert rad == (
        f"{faltnamn(rb_intag, 'P-KUND.andel_nya')} (P-KUND.andel_nya): kan inte härledas; bekräfta "
        f"{gemen(faltnamn(rb_intag, 'P-KUND.antal_nya'))} och {gemen(faltnamn(rb_intag, 'P-KUND.antal_aktiva'))} "
        "för samma period. [VERIFIERA]")


def test_bilagan_behaller_den_vanliga_raden_for_ett_saknat_intagsfalt(rb_intag, klar):
    saknas = klar.uppgifter["P-ORG.antal_anstallda"].model_copy(update={"status": "saknas"})
    profil = klar.model_copy(update={"uppgifter": {**klar.uppgifter, "P-ORG.antal_anstallda": saknas}})
    rad = next(s.text for s in bygg_underlagsbilaga(rb_intag, profil).stycken if s.referenser == ["P-ORG.antal_anstallda"])
    assert rad == (f"{faltnamn(rb_intag, 'P-ORG.antal_anstallda')} (P-ORG.antal_anstallda): "
                   "aktuellt bekräftat underlag saknas. [VERIFIERA]")


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


def test_omfattningsstycket_upprepar_inte_motiveringens_etikett(rb_intag, klar):
    b = bedom(rb_intag, valj(rb_intag, klar.byra.regelpaket, DAG, klar.byra.lan), klar)
    text = omfattningsstycke(rb_intag, klar, b).text
    assert "Byråns motivering: " in text
    assert faltnamn(rb_intag, "P-OMFATTNING.motivering") not in text
    assert "Motivering av vald analysomfattning" not in text
    assert "Byråns motivering: Syntetisk" in text


def test_omfattningsstycket_saknad_motivering_behaller_verifiera(rb_intag, klar):
    profil = _andrat(klar, "P-OMFATTNING.motivering", status="saknas")
    b = bedom(rb_intag, valj(rb_intag, profil.byra.regelpaket, DAG, profil.byra.lan), profil)
    text = omfattningsstycke(rb_intag, profil, b).text
    assert "Byråns motivering: aktuellt bekräftat underlag saknas. [VERIFIERA]" in text


def test_sektorsreferensen_anges_med_kallans_titel(tmp_path, rb_intag, klar):
    _, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    (s,) = sektorsstycken(rb_intag, t)
    ref = rb_intag.sektorsreferenser[rb_intag.tjanster[t.tjanst].sektorreferens]
    assert s.text.startswith(f"{rb_intag.kallor[ref.kalla].titel} anger risknivån {ref.niva} för sektorn {ref.sektor}")
    assert "SEKTOR-" not in s.text and ref.id in s.referenser


def test_inga_falt_id_i_tjanstavsnittets_lasta_stycken(tmp_path, rb_intag, klar):
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    lev = Testleverantor([godkant_delsvar(d, t) for d in DELAR])
    res = skriv_tjanst(lev, rb_intag, klar, t, avsnitt_id, effort="medium", personnamn=(), spara=lambda d, f: None)
    avsnitt = bygg_tjanstavsnitt_v3(rb_intag, klar, t, res, avsnitt_id)
    texter = [s.text for s in avsnitt.stycken]
    assert [x for n, x in enumerate(texter, 1) if faltid_fel(n, x)] == []
    assert not [x for x in texter if "SEKTOR-" in x or " >= " in x or " == " in x]
    assert texter[0].count("Antal kunder i tjänsten") == 1
    assert ": Antal " not in texter[0] and ": Andel " not in texter[0]


def _metodavsnitt(rb, profil):
    b = bedom(rb, valj(rb, profil.byra.regelpaket, DAG, profil.byra.lan), profil)
    return b, bygg_arb(rb, profil, b, {}, Historik()).avsnitt_med_id()["D-ARB.2"]


def _andrat(profil, falt, **uppdatering):
    u = profil.uppgifter[falt].model_copy(update=uppdatering)
    return profil.model_copy(update={"uppgifter": {**profil.uppgifter, falt: u}})


def _tjanststycke(avsnitt, t):
    return next(s for s in avsnitt.stycken if s.referenser[:1] == [t.tjanst])


def test_metodavsnittet_har_tjanstens_namn_och_sektorsmening_utan_koder(rb_intag, klar):
    b, avsnitt = _metodavsnitt(rb_intag, klar)
    texter = [s.text for s in avsnitt.stycken]
    assert [x for n, x in enumerate(texter, 1) if faltid_fel(n, x)] == []
    assert not [x for x in texter if "SEKTOR-" in x or "SRC-" in x or "version " in x]
    erbjudna = [t for t in b.tjanster if t.inneboende is not None]
    assert erbjudna
    for t in erbjudna:
        stycke = _tjanststycke(avsnitt, t)
        ref = rb_intag.sektorsreferenser[rb_intag.tjanster[t.tjanst].sektorreferens]
        assert stycke.text.startswith(f"{rb_intag.tjanster[t.tjanst].namn}: penningtvätt {t.inneboende.risk}")
        assert sektorsmening(rb_intag, ref) in stycke.text
        assert stycke.referenser == [t.tjanst, ref.id, ref.kalla]


def test_metodavsnittets_forsta_stycke_skriver_punkterna_i_ord(rb_intag, klar):
    _, avsnitt = _metodavsnitt(rb_intag, klar)
    forsta = avsnitt.stycken[0].text
    assert "Rättslig omfattning: punkterna 19 och 20; status slutlig." in forsta
    assert "(" not in forsta.split("Rättslig omfattning")[1]


def test_metodavsnittet_skriver_en_enda_punkt_i_ord(rb_intag, klar):
    profil = _andrat(klar, "P-VERK.bokforing", status="saknas")
    b, avsnitt = _metodavsnitt(rb_intag, profil)
    assert b.omfattning.punkter == (20,)
    assert "Rättslig omfattning: punkt 20; status preliminär." in avsnitt.stycken[0].text


def test_metodavsnittets_hinder_saknar_falt_id_nar_sateslan_ar_okant(rb_intag, klar):
    _, avsnitt = _metodavsnitt(rb_intag, _andrat(klar, "P-ORG.sateslan", status="saknas"))
    texter = [s.text for s in avsnitt.stycken]
    assert "Bekräfta " in texter[0] and "P-ORG.sateslan" not in texter[0]
    assert f"Bekräfta {gemen(faltnamn(rb_intag, 'P-ORG.sateslan'))}; " in texter[0]
    assert [x for n, x in enumerate(texter, 1) if faltid_fel(n, x)] == []


def test_metodavsnittets_forsta_stycke_har_de_namngivna_idn_som_referenser(rb_intag, klar):
    _, avsnitt = _metodavsnitt(rb_intag, _andrat(klar, "P-ORG.sateslan", status="saknas"))
    referenser = avsnitt.stycken[0].referenser
    assert "P-ORG.sateslan" in referenser
    assert len(referenser) == len(set(referenser))
    assert set(referenser) <= rb_intag.alla_id()


def test_metodavsnittets_forsta_stycke_saknar_referenser_utan_namngivna_id(rb_intag, klar):
    _, avsnitt = _metodavsnitt(rb_intag, klar)
    assert avsnitt.stycken[0].referenser == []


def test_metodavsnittets_hinder_saknar_id_for_tjanst_roll_och_tillamplighetsrad(rb_intag, klar):
    profil = _andrat(klar, "P-VERK.bokforing", status="saknas")
    b, avsnitt = _metodavsnitt(rb_intag, profil)
    assert any(h.startswith("T-RED-01:") for h in b.omfattning.hinder)
    assert any("BT-TILL-" in h for h in b.omfattning.hinder)
    texter = [s.text for s in avsnitt.stycken]
    assert [x for n, x in enumerate(texter, 1) if faltid_fel(n, x)] == []
    assert f"{rb_intag.tjanster['T-RED-01'].namn}: faktiskt erbjuden tjänst kräver" in texter[0]
    assert {"T-RED-01", "P-VERK.bokforing"} <= set(avsnitt.stycken[0].referenser)
    assert any(r.startswith("BT-TILL-") for r in avsnitt.stycken[0].referenser)


def test_sektorsmeningen_delas_av_sektorsstycket_och_metodavsnittet(tmp_path, rb_intag, klar):
    _, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    ref = rb_intag.sektorsreferenser[rb_intag.tjanster[t.tjanst].sektorreferens]
    mening = sektorsmening(rb_intag, ref)
    assert mening.endswith("Källans skala är separat från byråns motor och likställs inte med tjänstens risknivå.")
    assert f"sida {ref.sida}." in mening and "SEKTOR-" not in mening and "SRC-" not in mening
    (s,) = sektorsstycken(rb_intag, t)
    assert s.text == f"{mening} Motiveringen ska pröva tjänstens egna förhållanden mot denna sektorsreferens."
