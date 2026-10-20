from datetime import date

from riskanalys.bedomning.motor import bedom
from riskanalys.dokument.arb import bygg_arb
from riskanalys.drift.historik import Handelse, Historik
from riskanalys.granskning.kontroller import granska
from riskanalys.regelverk.urval import valj

DAG = date(2026, 11, 2)
HISTORIK = Historik().med(Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Första."))


def _granska(regelbas, profil, utkast, historik=HISTORIK):
    urval = valj(regelbas, "RP-RED-VG", date(2026, 11, 1), "Västra Götaland")
    bedomning = bedom(regelbas, urval, profil)
    dokument = bygg_arb(regelbas, profil, bedomning, utkast, historik)
    return granska(regelbas, urval, profil, bedomning, dokument, historik, DAG)


def test_fullstandigt_dokument_ger_inga_fynd(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    assert _granska(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast}) == ()


def test_saknat_riskavsnitt_ger_tackningsfynd_och_b04(regelbas, profil_fabrik, real_varden):
    fynd = {post.regel: post for post in _granska(regelbas, profil_fabrik(regelbas, real_varden), {})}
    assert set(fynd) == {"KRV-LSF-005", "B-04"}
    assert (fynd["KRV-LSF-005"].allvar, fynd["KRV-LSF-005"].grund) == ("blockerande", "ska_krav")
    assert (fynd["B-04"].allvar, fynd["B-04"].typ) == ("hög", "bristmonster")


def test_krav_som_inte_galler_byran_kravs_inte(regelbas, profil_fabrik, real_varden):
    krav = regelbas.krav["KRV-LSF-005"]
    villkor = {"falt": "P-VERK.juniora_konsulter", "op": "==", "varde": True}
    andrad = regelbas.model_copy(
        update={"krav": {**regelbas.krav, krav.id: krav.model_copy(update={"galler_om": villkor})}}
    )
    fynd = _granska(andrad, profil_fabrik(andrad, real_varden), {})
    assert {post.regel for post in fynd} == {"B-04"}


def test_krav_med_okand_tillamplighet_kravs(regelbas, profil_fabrik, real_varden):
    krav = regelbas.krav["KRV-LSF-005"]
    villkor = {"falt": "P-VERK.juniora_konsulter", "op": "==", "varde": True}
    andrad = regelbas.model_copy(
        update={"krav": {**regelbas.krav, krav.id: krav.model_copy(update={"galler_om": villkor})}}
    )
    profil = profil_fabrik(andrad, real_varden, okanda=("P-VERK.juniora_konsulter",))
    assert "KRV-LSF-005" in {post.regel for post in _granska(andrad, profil, {})}


def test_saknad_utvardering_ger_b16(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    fynd = _granska(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast}, Historik())
    assert {post.regel for post in fynd} == {None, "B-16"}
    assert any(post.beskrivning == "Avsnitt D-ARB.10 innehåller [VERIFIERA]." for post in fynd)


def test_okand_referens_ar_blockerande(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    stycken = list(giltigt_utkast.stycken)
    stycken[0] = stycken[0].model_copy(update={"referenser": ["T-RED-01", "H-99"]})
    utkast = giltigt_utkast.model_copy(update={"stycken": stycken})
    (fynd,) = _granska(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": utkast})
    assert (fynd.typ, fynd.allvar) == ("sparbarhet", "blockerande")
    assert fynd.beskrivning == "Avsnitt D-ARB.6.1 hänvisar till H-99, som inte finns i regelbasen."


def test_preliminar_bedomning_ger_fynd(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    profil = profil_fabrik(regelbas, real_varden, okanda=("P-KUND.andel_kontant",))
    fynd = _granska(regelbas, profil, {"D-ARB.6.1": giltigt_utkast})
    assert [post.beskrivning for post in fynd] == [
        "Bedömningen är preliminär. Okända uppgifter: P-KUND.andel_kontant.",
        "Avsnitt D-ARB.5 innehåller [VERIFIERA].",
    ]


def test_preliminar_omfattning_visar_sina_okanda_falt(regelbas, profil_fabrik, real_varden):
    from riskanalys.bedomning.modeller import Proportionalitet
    from riskanalys.granskning.kontroller import _preliminar
    profil = profil_fabrik(regelbas, real_varden)
    urval = valj(regelbas, "RP-RED-VG", DAG, "Västra Götaland")
    b = bedom(regelbas, urval, profil)
    assert all(not t.okanda_uppgifter for t in b.tjanster)
    b = b.model_copy(update={"status": "preliminär", "proportionalitet": Proportionalitet(
        niva="utökad", status="preliminär", regelspar=("BT-OMF-01",),
        okanda_uppgifter=("P-ORG.omsattning",))})
    (fynd,) = _preliminar(b)
    assert fynd["beskrivning"] == "Bedömningen är preliminär. Okända uppgifter: P-ORG.omsattning."


def test_preliminar_utan_okanda_falt_har_begriplig_atgard(regelbas, profil_fabrik, real_varden):
    from riskanalys.granskning.kontroller import _preliminar
    from riskanalys.regelverk.tillsyn import Omfattningsbeslut
    profil = profil_fabrik(regelbas, real_varden)
    urval = valj(regelbas, "RP-RED-VG", DAG, "Västra Götaland")
    hinder = "Tillsynsområdet behöver utredas för filialen."
    omfattning = Omfattningsbeslut(paket_id=None, punkter=(), status="preliminär",
                                  regelspar=(), hinder=(hinder,))
    b = bedom(regelbas, urval, profil).model_copy(update={"status": "preliminär", "omfattning": omfattning})
    (fynd,) = _preliminar(b)
    assert "Okända uppgifter: ." not in fynd["beskrivning"]
    assert hinder in fynd["beskrivning"]
    assert "omfattning" in fynd["atgard"].lower()


def test_motivering_utan_hot_ger_b12(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    stycken = [stycke.model_copy(update={"typ": "analys"}) for stycke in giltigt_utkast.stycken]
    utkast = giltigt_utkast.model_copy(update={"stycken": stycken})
    fynd = _granska(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": utkast})
    assert [post.regel for post in fynd] == ["B-12"]


def test_fynd_far_lopnummer_med_datum(regelbas, profil_fabrik, real_varden):
    fynd = _granska(regelbas, profil_fabrik(regelbas, real_varden), {})
    assert [post.id for post in fynd] == ["F-2026-11-02-001", "F-2026-11-02-002"]


def test_okand_rollplatshallare_ger_fynd(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    """Slutgranskningen 2026-10-10, Important #2: granskningen läser texten så som den skrivs ut."""
    stycken = list(giltigt_utkast.stycken)
    stycken[3] = stycken[3].model_copy(update={"text": stycken[3].text + " Ärendet eskaleras till {roll:VD}."})
    utkast = giltigt_utkast.model_copy(update={"stycken": stycken})
    fynd = _granska(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": utkast})
    assert any(post.beskrivning == "Avsnitt D-ARB.6.1 innehåller [VERIFIERA]." for post in fynd)
