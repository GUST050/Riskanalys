from riskanalys.bedomning.motor import bedom
from riskanalys.dokument.analysunderlag import sarbarhetsstycke
from riskanalys.dokument.arb import _metod, bygg_arb
from riskanalys.dokument.delskrivning import skriv_tjanst
from riskanalys.dokument.intagsunderlag import bygg_underlagsbilaga
from riskanalys.dokument.klartext import faltnamn
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.nivatext import sektorsmening, sektorsstycken
from riskanalys.dokument.platshallare import faltid_fel
from riskanalys.dokument.promptar import DELAR
from riskanalys.dokument.tjanstavsnitt import bygg_tjanstavsnitt_v3
from riskanalys.dokument.uppfoljning import omfattningsstycke
from riskanalys.drift.historik import Historik
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


def _metodavsnitt(rb, profil):
    b = bedom(rb, valj(rb, profil.byra.regelpaket, DAG, profil.byra.lan), profil)
    return b, bygg_arb(rb, profil, b, {}, Historik()).avsnitt_med_id()["D-ARB.2"]


def test_metodavsnittet_har_tjanstens_namn_och_sektorsmening_utan_koder(rb_intag, klar):
    b, avsnitt = _metodavsnitt(rb_intag, klar)
    texter = [s.text for s in avsnitt.stycken]
    assert [x for n, x in enumerate(texter, 1) if faltid_fel(n, x)] == []
    assert not [x for x in texter if "SEKTOR-" in x or "SRC-" in x or "version " in x]
    for t in (t for t in b.tjanster if t.inneboende is not None):
        stycke = next(s for s in avsnitt.stycken if s.referenser == [t.tjanst])
        ref = rb_intag.sektorsreferenser[rb_intag.tjanster[t.tjanst].sektorreferens]
        assert stycke.text.startswith(f"{rb_intag.tjanster[t.tjanst].namn}: penningtvätt {t.inneboende.risk}")
        assert not stycke.text.startswith(t.tjanst)
        assert sektorsmening(rb_intag, ref) in stycke.text


def test_sektorsmeningen_delas_av_sektorsstycket_och_metodavsnittet(tmp_path, rb_intag, klar):
    _, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    ref = rb_intag.sektorsreferenser[rb_intag.tjanster[t.tjanst].sektorreferens]
    mening = sektorsmening(rb_intag, ref)
    assert mening.endswith("Källans skala är separat från byråns motor och likställs inte med tjänstens risknivå.")
    assert f"sida {ref.sida}." in mening and "SEKTOR-" not in mening and "SRC-" not in mening
    (s,) = sektorsstycken(rb_intag, t)
    assert s.text == f"{mening} Motiveringen ska pröva tjänstens egna förhållanden mot denna sektorsreferens."


def test_frysta_m1_kedjan_behaller_metodavsnittets_gamla_text(rb_intag, klar):
    gammal = rb_intag.model_copy(update={"version": "0.9.0"})
    assert not gammal.utokade_krav
    b = bedom(gammal, valj(gammal, klar.byra.regelpaket, DAG, klar.byra.lan), klar)
    t = next(t for t in b.tjanster if t.inneboende is not None)
    ref = gammal.sektorsreferenser[gammal.tjanster[t.tjanst].sektorreferens]
    stycke = next(s for s in _metod(gammal, b).stycken if s.referenser == [t.tjanst])
    assert stycke.text.startswith(f"{t.tjanst}: penningtvätt {t.inneboende.risk}, kvarstående {t.kvarstaende}; ")
    assert stycke.text.endswith(
        f"Sektorsreferens {ref.id}: {ref.niva} på källans skala {ref.skala}, {ref.kalla}, sida {ref.sida}, "
        f"version {ref.referensversion}. Källans skala är separat från byråns motor.")
