from dataclasses import replace
from datetime import date

import pytest

from riskanalys.bedomning.motor import bedom
from riskanalys.dokument.arb import bygg_arb
from riskanalys.drift.historik import Handelse, Historik
from riskanalys.faststallelse.grindar import Faststallelseunderlag, fyndhinder, hinder_for_faststallelse
from riskanalys.faststallelse.modeller import Sakgranskning
from riskanalys.faststallelse.sakgranskning import granskad_summa
from riskanalys.granskning.kontroller import granska
from riskanalys.granskning.modeller import Fynd
from riskanalys.regelverk.urval import valj
from riskanalys.regelverk.validering import validera

GRANSKNINGSDAG = date(2026, 11, 2)
SAKGRANSKNINGSDAG = date(2026, 11, 3)
BESLUTSDAG = date(2026, 11, 15)
HISTORIK = Historik().med(Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Första."))


def _underlag(regelbas, profil, utkast, historik=HISTORIK):
    urval = valj(regelbas, "RP-RED-VG", date(2026, 11, 1), "Västra Götaland")
    bedomning = bedom(regelbas, urval, profil)
    dokument = bygg_arb(regelbas, profil, bedomning, utkast, historik)
    fynd = granska(regelbas, urval, profil, bedomning, dokument, historik, GRANSKNINGSDAG)
    sakgranskningar = tuple(
        Sakgranskning(
            avsnitt=avsnitt.id,
            kontrollsumma=granskad_summa(avsnitt, profil),
            godkand=True,
            roll="FfR",
            namn="Testa Testsson",
            datum=SAKGRANSKNINGSDAG,
        )
        for avsnitt in dokument.avsnitt
    )
    return Faststallelseunderlag(
        regelbas=regelbas,
        urval=urval,
        profil=profil,
        bedomning=bedomning,
        dokument=dokument,
        fynd=fynd,
        sakgranskningar=sakgranskningar,
        historik=historik,
        granskningsdatum=GRANSKNINGSDAG,
    )


@pytest.fixture
def komplett(signerad_regelbas, profil_fabrik, real_varden, giltigt_utkast):
    return _underlag(signerad_regelbas, profil_fabrik(signerad_regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast})


def _med_andrat_krav(underlag, krav_id, **andringar):
    regelbas = underlag.regelbas
    krav = regelbas.krav[krav_id].model_copy(update=andringar)
    andrad = regelbas.model_copy(update={"krav": {**regelbas.krav, krav_id: krav}})
    return replace(underlag, regelbas=andrad, urval=valj(andrad, "RP-RED-VG", date(2026, 11, 1), "Västra Götaland"))


def _med_andrad_karta(underlag, **andringar):
    regelbas = underlag.regelbas
    paket = regelbas.regelpaket["RP-RED-VG"]
    andrat = paket.model_copy(update={"paragrafkarta": paket.paragrafkarta.model_copy(update=andringar)})
    andrad = regelbas.model_copy(update={"regelpaket": {paket.id: andrat}})
    return replace(underlag, regelbas=andrad, urval=valj(andrad, "RP-RED-VG", date(2026, 11, 1), "Västra Götaland"))


def test_den_signerade_testkopian_ar_en_giltig_regelbas(signerad_regelbas):
    assert validera(signerad_regelbas) == []


def test_komplett_underlag_har_inga_hinder(komplett):
    assert hinder_for_faststallelse(komplett, BESLUTSDAG) == []


def test_osignerad_regelbas_ger_hinder_for_krav_och_paragrafkarta(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    underlag = _underlag(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast})
    hinder = hinder_for_faststallelse(underlag, BESLUTSDAG)
    assert len([rad for rad in hinder if "är inte verifierat av sakkunnig" in rad]) == 6
    assert (
        "Paragrafkartan för regelpaketet RP-RED-VG är inte verifierad av sakkunnig i sin nuvarande lydelse "
        "(status ej_granskad)." in hinder
    )
    (ohanterade,) = [rad for rad in hinder if "ännu inte hanterar" in rad]
    assert ohanterade.startswith(
        "Paragrafkartan för regelpaketet RP-RED-VG har paragrafer som regelbasen ännu inte hanterar: "
        "SRC-14FS-2024-11 2 kap. 4 §, "
    )


def test_krav_som_inte_galler_byran_behover_inte_vara_verifierat(komplett):
    villkor = {"falt": "P-VERK.juniora_konsulter", "op": "==", "varde": True}
    krav = komplett.regelbas.krav["KRV-LSF-001"]
    underlag = _med_andrat_krav(
        komplett, "KRV-LSF-001", galler_om=villkor, sakkunnig=krav.sakkunnig.model_copy(update={"status": "ej_granskad"})
    )
    assert hinder_for_faststallelse(replace(underlag, fynd=()), BESLUTSDAG) == []


def test_krav_som_andrats_efter_verifieringen_ar_hinder(komplett):
    underlag = _med_andrat_krav(komplett, "KRV-LSF-001", text="Ett ändrat krav.")
    assert hinder_for_faststallelse(underlag, BESLUTSDAG) == [
        "Kravet KRV-LSF-001 (2 kap. 1 §) är inte verifierat av sakkunnig i sin nuvarande lydelse (status verifierad)."
    ]


def test_paragrafkarta_som_andrats_efter_verifieringen_ar_hinder(komplett):
    karta = komplett.regelbas.regelpaket["RP-RED-VG"].paragrafkarta
    rader = (*karta.rader[:-1], karta.rader[-1].model_copy(update={"ej_tillamplig": "En annan motivering."}))
    hinder = hinder_for_faststallelse(_med_andrad_karta(komplett, rader=rader), BESLUTSDAG)
    assert hinder == [
        "Paragrafkartan för regelpaketet RP-RED-VG är inte verifierad av sakkunnig i sin nuvarande lydelse "
        "(status verifierad)."
    ]


def test_paragrafkarta_som_inte_galler_bedomningens_datum_ar_hinder(komplett):
    hinder = hinder_for_faststallelse(_med_andrad_karta(komplett, giltig_fran=date(2027, 1, 1)), BESLUTSDAG)
    assert "Paragrafkartan för regelpaketet RP-RED-VG gäller inte bedömningens datum 2026-11-01." in hinder


def test_saknad_kritisk_uppgift_och_preliminar_bedomning(signerad_regelbas, profil_fabrik, real_varden, giltigt_utkast):
    profil = profil_fabrik(signerad_regelbas, real_varden, okanda=("P-KUND.andel_kontant",))
    hinder = hinder_for_faststallelse(_underlag(signerad_regelbas, profil, {"D-ARB.6.1": giltigt_utkast}), BESLUTSDAG)
    assert "Kritiska uppgifter saknas: P-KUND.andel_kontant. Bekräfta dem med 'riskanalys bekrafta'." in hinder
    assert any(rad.startswith("Bedömningen är preliminär.") for rad in hinder)
    assert "Avsnitt D-ARB.5 innehåller [VERIFIERA]." in hinder


def test_blockerande_fynd_ar_alltid_hinder(signerad_regelbas, profil_fabrik, real_varden):
    underlag = _underlag(signerad_regelbas, profil_fabrik(signerad_regelbas, real_varden), {})
    hinder = hinder_for_faststallelse(underlag, BESLUTSDAG)
    assert any("blockerande fynd" in rad and "KRV-LSF-005" in rad for rad in hinder)
    assert any("Löpande bokföring saknar eget riskavsnitt" in rad for rad in hinder)


def test_avsnitt_som_andrats_efter_sakgranskningen_ar_hinder(komplett):
    (forsta, *ovriga) = komplett.dokument.avsnitt
    stycke = forsta.stycken[0].model_copy(update={"text": forsta.stycken[0].text + " Tillägg."})
    andrat = forsta.model_copy(update={"stycken": (stycke, *forsta.stycken[1:])})
    dokument = komplett.dokument.model_copy(update={"avsnitt": (andrat, *ovriga)})
    assert hinder_for_faststallelse(replace(komplett, dokument=dokument), BESLUTSDAG) == [
        "Avsnitt D-ARB.1 är inte sakgranskat i nuvarande lydelse."
    ]


def test_byte_av_ansvarig_person_efter_sakgranskningen_ar_hinder(komplett, profil_fabrik, real_varden):
    ny_ansvarig = profil_fabrik(komplett.regelbas, {**real_varden, "P-ROLL.ffr_namn": "Ny Person"})
    assert hinder_for_faststallelse(replace(komplett, profil=ny_ansvarig), BESLUTSDAG) == [
        "Avsnitt D-ARB.1 är inte sakgranskat i nuvarande lydelse."
    ]


def test_underkant_avsnitt_ar_hinder(komplett):
    avsnitt = komplett.dokument.avsnitt[0]
    underkant = Sakgranskning(
        avsnitt=avsnitt.id,
        kontrollsumma=granskad_summa(avsnitt, komplett.profil),
        godkand=False,
        roll="FfR",
        namn="Testa Testsson",
        datum=date(2026, 11, 4),
        kommentar="Fel antal anställda.",
    )
    underlag = replace(komplett, sakgranskningar=(*komplett.sakgranskningar, underkant))
    assert hinder_for_faststallelse(underlag, BESLUTSDAG) == [
        "Avsnitt D-ARB.1 underkändes vid sakgranskningen: Fel antal anställda."
    ]


def test_utvardering_saknas_eller_har_passerat(komplett):
    utan = replace(komplett, historik=Historik())
    assert "Datum för utvärdering saknas. Registrera utvärderingen med 'riskanalys utvardera'." in (
        hinder_for_faststallelse(utan, BESLUTSDAG)
    )
    assert hinder_for_faststallelse(komplett, date(2027, 11, 2)) == [
        "Nästa genomgång skulle ha gjorts senast 2027-11-01. Utvärdera riskbedömningen igen."
    ]


def test_beslut_fore_granskningen_och_sakgranskningen_ar_hinder(komplett):
    assert hinder_for_faststallelse(komplett, date(2026, 11, 1)) == [
        "Beslutsdatum 2026-11-01 är före granskningen 2026-11-02.",
        "Beslutsdatum 2026-11-01 är före den senaste sakgranskningen 2026-11-03.",
    ]


def test_beslut_samma_dag_som_sakgranskningen_godtas(komplett):
    assert hinder_for_faststallelse(komplett, SAKGRANSKNINGSDAG) == []


def test_beslut_fore_senaste_utvarderingen_ar_hinder(komplett):
    historik = HISTORIK.med(Handelse(datum=date(2026, 11, 20), typ="utvärdering", beskrivning="Andra."))
    assert hinder_for_faststallelse(replace(komplett, historik=historik), BESLUTSDAG) == [
        "Beslutsdatum 2026-11-15 är före den senaste utvärderingen 2026-11-20."
    ]


def test_beslut_fore_en_tidigare_faststallelse_ar_hinder(komplett):
    faststallelse = Handelse(datum=date(2026, 11, 20), typ="fastställelse", beskrivning="v1", version=1)
    assert hinder_for_faststallelse(replace(komplett, historik=HISTORIK.med(faststallelse)), BESLUTSDAG) == [
        "Beslutsdatum 2026-11-15 är före den senaste fastställelsen 2026-11-20."
    ]


def _fynd(allvar="hög", grund="tillsynspraxis", status="öppen", motivering=None):
    return Fynd(
        id="F-2026-11-02-001",
        typ="bristmonster",
        regel="B-04",
        allvar=allvar,
        grund=grund,
        beskrivning="Beskrivning.",
        atgard="Åtgärd.",
        status=status,
        motivering=motivering,
    )


@pytest.mark.parametrize(
    ("fynd", "hinder"),
    [
        (_fynd(), "fyndet är öppet"),
        (_fynd(allvar="medel"), "fyndet är öppet"),
        (_fynd(status="åtgärdad"), None),
        (_fynd(allvar="blockerande", status="åtgärdad"), "blockerande fynd"),
        (_fynd(grund="ska_krav", status="accepterad_metodavvikelse", motivering="KRV-LSF-005 uppfylls."), "sakkunnig"),
        (_fynd(grund="ska_krav", status="sakkunnigbedömd", motivering="Kravet är uppfyllt genom avsnitt 6."), None),
        (_fynd(grund="ska_krav", status="sakkunnigbedömd"), "saknar motivering"),
        (_fynd(grund="metodval", status="accepterad_metodavvikelse", motivering="Annan skala."), None),
        (_fynd(grund="metodval", status="accepterad_metodavvikelse"), "saknar motivering"),
        (_fynd(status="accepterad_metodavvikelse", motivering="Vi gör på annat sätt."), "KRV-"),
        (_fynd(status="accepterad_metodavvikelse", motivering="KRV-LSF-005 uppfylls i avsnitt 6."), None),
        (_fynd(grund="eu_utkast", status="accepterad_metodavvikelse", motivering="Inte bindande än."), "KRV-"),
    ],
)
def test_fyndhinder_foljer_fyndets_grund(fynd, hinder):
    if hinder is None:
        assert fyndhinder(fynd) == []
    else:
        (rad,) = fyndhinder(fynd)
        assert hinder in rad


def test_okand_rollplatshallare_i_utskriften_ar_hinder(signerad_regelbas, profil_fabrik, real_varden, giltigt_utkast):
    """Slutgranskningen 2026-10-10, Important #2: {roll:VD} blir [VERIFIERA: VD] i utskriften och får inte fastställas."""
    stycken = list(giltigt_utkast.stycken)
    stycken[3] = stycken[3].model_copy(update={"text": stycken[3].text + " Ärendet eskaleras till {roll:VD}."})
    utkast = giltigt_utkast.model_copy(update={"stycken": stycken})
    underlag = _underlag(signerad_regelbas, profil_fabrik(signerad_regelbas, real_varden), {"D-ARB.6.1": utkast})
    assert "Avsnitt D-ARB.6.1 innehåller [VERIFIERA]." in hinder_for_faststallelse(underlag, BESLUTSDAG)


@pytest.mark.parametrize(
    "andringar, vantat",
    [
        ({"kalla": None}, "P-KUND.andel_kontant är bekräftad utan källa."),
        (
            {"status": "ej_tillämplig", "varde": None, "kalla": None, "motivering": None},
            "P-KUND.andel_kontant är markerad som ej tillämplig utan motivering.",
        ),
    ],
)
def test_uppgift_utan_belagg_ar_hinder(signerad_regelbas, profil_fabrik, real_varden, giltigt_utkast, andringar, vantat):
    """Codex 2026-10-10, P2: villkor 1 i spec 10 kräver ej tillämplig med motivering och bekräftelse med belägg."""
    profil = profil_fabrik(signerad_regelbas, real_varden)
    uppgift = profil.uppgifter["P-KUND.andel_kontant"].model_copy(update=andringar)
    profil = profil.model_copy(update={"uppgifter": {**profil.uppgifter, "P-KUND.andel_kontant": uppgift}})
    hinder = hinder_for_faststallelse(_underlag(signerad_regelbas, profil, {"D-ARB.6.1": giltigt_utkast}), BESLUTSDAG)
    assert any(rad.startswith(vantat) for rad in hinder)


def test_ofullstandigt_omfattningsunderlag_kan_aldrig_faststallas(komplett):
    from riskanalys.dokument.omfattningsutkast import bygg_omfattningsutkast
    d=bygg_omfattningsutkast(komplett.regelbas,komplett.profil).dokument
    fel=hinder_for_faststallelse(replace(komplett,dokument=d),BESLUTSDAG)
    assert 'Ofullständigt omfattningsunderlag kan inte fastställas som en allmän riskbedömning.' in fel
