import pytest

from riskanalys.dokument.validering import VERIFIERA, nivapastaenden, validera_utkast

PERSONER = ("Testa Testsson",)


def _andra(utkast, index, **andringar):
    stycken = list(utkast.stycken)
    stycken[index] = stycken[index].model_copy(update=andringar)
    return utkast.model_copy(update={"stycken": stycken})


def _ersatt(utkast, index, gammal, ny):
    text = utkast.stycken[index].text
    assert gammal in text
    return _andra(utkast, index, text=text.replace(gammal, ny))


def test_giltigt_utkast_godkanns(giltigt_utkast, real_underlag):
    assert validera_utkast(giltigt_utkast, real_underlag, PERSONER) == []


def test_fel_avsnitt(giltigt_utkast, real_underlag):
    fel = validera_utkast(giltigt_utkast.model_copy(update={"avsnitt": "D-ARB.6.2"}), real_underlag, PERSONER)
    assert "Utkastet gäller avsnitt D-ARB.6.2, men underlaget gäller D-ARB.6.1." in fel


def test_tomt_utkast(giltigt_utkast, real_underlag):
    fel = validera_utkast(giltigt_utkast.model_copy(update={"stycken": []}), real_underlag, PERSONER)
    assert "Utkastet har inga stycken." in fel
    assert "Utkastet saknar ett stycke av typen motivering." in fel


def test_okand_referens(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 0, referenser=["T-RED-01", "H-99"])
    assert "Stycke 1 hänvisar till H-99, som inte finns i underlaget." in validera_utkast(utkast, real_underlag, PERSONER)


def test_stycke_utan_referenser(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 0, referenser=[])
    assert "Stycke 1 saknar referenser." in validera_utkast(utkast, real_underlag, PERSONER)


def test_pahittat_tal(giltigt_utkast, real_underlag):
    utkast = _ersatt(giltigt_utkast, 1, "30 %", "45 %")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert "Stycke 2 innehåller talet 45, som inte finns i underlaget." in fel


@pytest.mark.parametrize(
    ("text", "vantat"),
    [
        ("Risken är hög.", [("inneboende_risk", "hög")]),
        ("Risknivån bedöms som mycket hög.", [("inneboende_risk", "mycket hög")]),
        ("Den inneboende risken i tjänsten är måttlig.", [("inneboende_risk", "måttlig")]),
        ("Risken för penningtvätt blir låg.", [("inneboende_risk", "låg")]),
        ("Den kvarstående risken är hög.", [("kvarstaende_risk", "hög")]),
        ("Risken bedöms därför som låg.", [("inneboende_risk", "låg")]),
        ("Risken för finansiering av terrorism bedöms som måttlig.", [("terrorfinansiering_risk", "måttlig")]),
        ("Terrorfinansieringsrisken är låg.", [("terrorfinansiering_risk", "låg")]),
        ("Sannolikheten bedöms vara hög.", [("inneboende_sannolikhet", "hög")]),
        ("Sannolikheten för terrorfinansiering är låg.", [("terrorfinansiering_sannolikhet", "låg")]),
        ("Konsekvensen är betydande.", [("inneboende_konsekvens", "betydande")]),
        ("Konsekvensen för finansiering av terrorism är allvarlig.", [("terrorfinansiering_konsekvens", "allvarlig")]),
        (
            "Den kvarstående risken för terrorfinansiering är låg.",
            [("kvarstaende_terrorfinansiering_risk", "låg")],
        ),
        (
            "Konsekvensen är betydande. Risken är hög, och den kvarstående risken är måttlig.",
            [("inneboende_konsekvens", "betydande"), ("inneboende_risk", "hög"), ("kvarstaende_risk", "måttlig")],
        ),
        ("En hög andel av kunderna betalar kontant.", []),
    ],
)
def test_nivapastaenden_binds_till_risktyp(text, vantat):
    assert nivapastaenden(text) == vantat


def test_inneboende_riskniva_som_inte_kommer_fran_motorn(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 1, text=giltigt_utkast.stycken[1].text + " Risken är låg.")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert any(f.startswith("Stycke 2 anger en nivå för den inneboende risken.") for f in fel)


def test_tva_giltiga_nivaer_som_bytt_plats_upptacks(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 2, text=giltigt_utkast.stycken[2].text + " Risken för finansiering av terrorism bedöms som hög. Den kvarstående risken är måttlig.")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert any(f.startswith("Stycke 3 anger en nivå för risken för terrorfinansiering.") for f in fel)


def test_kvarstaende_niva_som_bara_galler_terrorfinansiering_upptacks(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 2, text=giltigt_utkast.stycken[2].text + " Den kvarstående risken är måttlig.")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert any(f.startswith("Stycke 3 anger en nivå för den kvarstående risken.") for f in fel)


def test_fel_sannolikhet_och_konsekvens_upptacks(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 1, text=giltigt_utkast.stycken[1].text + " Sannolikheten bedöms som medel. Konsekvensen är allvarlig.")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert any(f.startswith("Stycke 2 anger en nivå för sannolikheten.") for f in fel)


def test_niva_for_risktyp_som_motorn_inte_bedomer(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 2, text=giltigt_utkast.stycken[2].text + " Den kvarstående risken för terrorfinansiering är låg.")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert any(f.startswith("Stycke 3 anger en nivå för den kvarstående risken för terrorfinansiering.") for f in fel)


def test_obekraftad_uppgift_kraver_verifiera(giltigt_utkast, underlag_fabrik, regelbas, profil_fabrik, real_varden):
    underlag = underlag_fabrik(profil_fabrik(regelbas, real_varden, okanda=("P-KUND.andel_riskbransch",)))
    meddelande = f"Stycke 2 bygger på obekräftade uppgifter (P-KUND.andel_riskbransch) men saknar {VERIFIERA}."
    assert meddelande in validera_utkast(giltigt_utkast, underlag, PERSONER)
    markerat = _andra(giltigt_utkast, 1, text=giltigt_utkast.stycken[1].text + f" {VERIFIERA}")
    assert meddelande not in validera_utkast(markerat, underlag, PERSONER)


def test_forbjuden_formulering(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 0, text=giltigt_utkast.stycken[0].text + " Det finns inga risker i övrigt.")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert 'Stycke 1 innehåller den förbjudna formuleringen "det finns inga risker".' in fel


def test_personnamn_stoppas_utan_att_namnet_upprepas(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 0, text=giltigt_utkast.stycken[0].text + " Testa Testsson ansvarar.")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert "Stycke 1 innehåller ett personnamn. Skriv {roll:FfR} i stället." in fel
    assert not any("Testa Testsson" in rad for rad in fel)


def test_motivering_utan_hot(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 1, referenser=["S-KUND-01", "BT-MATRIS-08"])
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert (
        "Motiveringen i stycke 2 måste hänvisa till minst ett hot (H-) och en sårbarhet (S-) eller uppgift (P-)." in fel
    )


# Slutgranskningen 2026-10-10, Important #1: varje risknivå ska anges, och nivåer före subjektet ska kännas igen.


def test_ai_utkast_behover_inte_ange_kodens_risknivaer(giltigt_utkast, real_underlag):
    assert validera_utkast(giltigt_utkast, real_underlag, PERSONER) == []


@pytest.mark.parametrize(
    "text, vantat",
    [
        ("Tjänsten har därför låg kvarstående risk.", [("kvarstaende_risk", "låg")]),
        ("Kvarstående risk: låg.", [("kvarstaende_risk", "låg")]),
        ("Efter kontrollerna kvarstår en låg risk.", [("kvarstaende_risk", "låg")]),
        ("Byrån bedömer den kvarstående risken som låg.", [("kvarstaende_risk", "låg")]),
        ("Tjänsten har en hög risk för terrorfinansiering.", [("terrorfinansiering_risk", "hög")]),
        ("Det är en låg terrorfinansieringsrisk.", [("terrorfinansiering_risk", "låg")]),
        ("Den låga inneboende risken beror på kunderna.", [("inneboende_risk", "låg")]),
        ("Uppgifterna som låg till grund för risken kom från kunderna.", []),
    ],
)
def test_nivapastaenden_med_nivan_fore_subjektet(text, vantat):
    assert nivapastaenden(text) == vantat


def test_lag_kvarstaende_risk_fore_subjektet_motsager_motorn(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 3, text=giltigt_utkast.stycken[3].text + " Tjänsten har därför låg kvarstående risk.")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert any(f.startswith("Stycke 4 anger en nivå för den kvarstående risken.") for f in fel)


# Slutgranskningen 2026-10-10, Important #2: okända rollplatshållare och egna varianter av [VERIFIERA].


def test_okand_rollplatshallare_underkanns(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 3, text=giltigt_utkast.stycken[3].text + " Ärendet eskaleras till {roll:VD}.")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert fel == ["Stycke 4 använder platshållaren {roll:VD}, som inte finns. Tillåtna roller: {roll:FfR}, {roll:Ansvarsfunktion}."]


def test_kand_rollplatshallare_godkanns(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 3, text=giltigt_utkast.stycken[3].text + " Frågan går till {roll:FfR}.")
    assert validera_utkast(utkast, real_underlag, PERSONER) == []


def test_egen_variant_av_verifiera_underkanns(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 3, text=giltigt_utkast.stycken[3].text + " Ansvarig: [VERIFIERA: VD].")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert fel == [f"Stycke 4 innehåller en egen variant av {VERIFIERA}. Skriv exakt {VERIFIERA}."]

@pytest.mark.parametrize("falt",["P-Pahittad","P-ORG.namn","P-ROLL.ffr_namn"])
def test_oklarhet_far_bara_peka_pa_tillatna_aggregat(giltigt_utkast,real_underlag,falt):
    from riskanalys.dokument.modeller import Oklarhet
    u=giltigt_utkast.model_copy(update={"oklarheter":[Oklarhet(fraga="Syntetisk fråga",saknad_uppgift=falt)]})
    assert any("oklarhet" in f.lower() for f in validera_utkast(u,real_underlag,()))


from riskanalys.dokument.modeller import UnderlagUppgift


def _med_omsattning(utkast, underlag, skrivet):
    uppgift = UnderlagUppgift(id="P-VERK.omsattning", fraga="Omsättning", varde="2300000.0", bekraftad=True)
    nytt_underlag = underlag.model_copy(update={"uppgifter": (*underlag.uppgifter, uppgift)})
    stycke = utkast.stycken[0]
    nytt_utkast = _andra(utkast, 0, text=stycke.text + f" Omsättningen var {skrivet} kr.",
                         referenser=[*stycke.referenser, "P-VERK.omsattning"])
    return nytt_utkast, nytt_underlag


@pytest.mark.parametrize("skrivet", ["2 300 000", "2 300 000", "2 300 000", "2300000"])
def test_svenska_tusentalsavgransare_godtas(giltigt_utkast, real_underlag, skrivet):
    utkast, underlag = _med_omsattning(giltigt_utkast, real_underlag, skrivet)
    assert not [fel for fel in validera_utkast(utkast, underlag, PERSONER) if "talet" in fel]


def test_fel_belopp_med_tusentalsavgransare_underkanns(giltigt_utkast, real_underlag):
    utkast, underlag = _med_omsattning(giltigt_utkast, real_underlag, "2 400 000")
    fel = validera_utkast(utkast, underlag, PERSONER)
    assert "Stycke 1 innehåller talet 2400000, som inte finns i underlaget." in fel


def test_ai_text_far_inte_ange_nivaer_inte_heller_for_delfaktorer(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 0, text=giltigt_utkast.stycken[0].text + " Risken för osanna fakturor är hög.")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert any(f.startswith("Stycke 1 anger en nivå för den inneboende risken.") for f in fel)


def test_fixturen_saknar_nivapastaenden(giltigt_utkast):
    assert not [p for s in giltigt_utkast.stycken for p in nivapastaenden(s.text)]


@pytest.mark.parametrize('text',['Hög risk för penningtvätt finns bland kunderna.','Riskerna är höga.','Konsekvenserna är allvarliga.'])
def test_aven_aldre_schema_forbjuder_generiska_ai_nivaer(giltigt_utkast,real_underlag,text):
    from riskanalys.dokument.modeller import Textstycke
    a=giltigt_utkast.model_copy(update={'stycken':[*giltigt_utkast.stycken,Textstycke(typ='analys',text=text,referenser=['H-01'])]})
    assert any('anger en nivå' in f for f in validera_utkast(a,real_underlag,()))
