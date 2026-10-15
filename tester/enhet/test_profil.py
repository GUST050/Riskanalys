from datetime import date

import pytest

from riskanalys.lagring.datamapp import skapa_byramapp
from riskanalys.profil.hantering import (
    ProfilFel,
    bekrafta,
    kritiska_falt,
    markera_ej_tillamplig,
    personnamn,
    saknade_kritiska,
    skapa_profil,
    tolka_varde,
    visa_varde,
)
from riskanalys.profil.lagring import las_profil, spara_profil
from riskanalys.profil.modeller import Byra
from riskanalys.regelverk.urval import valj
from riskanalys.regelverk.villkor import Kunskap

BYRA = Byra(id="testbyra", regelpaket="RP-RED-VG", datum=date(2026, 11, 1), lan="Västra Götaland")
DAG = date(2026, 10, 1)
KRITISKA = {
    "P-ORG.antal_anstallda",
    "P-ORG.verksamhetsstallen",
    "P-ROLL.ffr_namn",
    "P-TJ.T-RED-01.erbjuds",
    "P-KUND.andel_riskbransch",
    "P-KUND.andel_kontant",
    "P-KANAL.andel_digitalt_underlag",
    "P-KANAL.bankdata_andel",
    "P-VERK.juniora_konsulter",
    "P-KONTROLL.C-07.utformning",
    "P-KONTROLL.C-07.genomforande",
}


def test_ny_profil_saknar_alla_uppgifter(regelbas):
    profil = skapa_profil(regelbas, BYRA)
    assert set(profil.uppgifter) == set(regelbas.falt)
    assert {uppgift.status for uppgift in profil.uppgifter.values()} == {"saknas"}


@pytest.mark.parametrize(
    ("falt_id", "text", "vantat"),
    [
        ("P-VERK.juniora_konsulter", "Ja", True),
        ("P-VERK.juniora_konsulter", "nej", False),
        ("P-KUND.andel_riskbransch", "30 %", 0.3),
        ("P-KUND.andel_riskbransch", "30%", 0.3),
        ("P-KUND.andel_riskbransch", "0,3", 0.3),
        ("P-KUND.andel_riskbransch", "1,0", 1.0),
        ("P-ORG.antal_anstallda", "8", 8),
        ("P-KONTROLL.C-07.utformning", "finns", "finns"),
        ("P-ORG.namn", " Testbyrån AB ", "Testbyrån AB"),
    ],
)
def test_varden_med_svenska_format_tolkas(regelbas, falt_id, text, vantat):
    assert tolka_varde(regelbas.falt[falt_id], text) == vantat


def test_andel_over_ett_utan_procenttecken_vagras(regelbas):
    with pytest.raises(ProfilFel, match="0–1 eller i procent"):
        tolka_varde(regelbas.falt["P-KUND.andel_riskbransch"], "30")


@pytest.mark.parametrize(
    ("falt_id", "text", "meddelande"),
    [
        ("P-KUND.andel_riskbransch", "130 %", "0–1 eller i procent"),
        ("P-VERK.juniora_konsulter", "kanske", "ja eller nej"),
        ("P-KONTROLL.C-07.utformning", "delvis", "Välj ett av: finns, saknas"),
        ("P-ORG.antal_anstallda", "åtta", "Skriv ett tal"),
        ("P-ORG.namn", "  ", "passar inte"),
    ],
)
def test_ogiltiga_varden_vagras_med_hjalptext(regelbas, falt_id, text, meddelande):
    with pytest.raises(ProfilFel, match=meddelande):
        tolka_varde(regelbas.falt[falt_id], text)


@pytest.mark.parametrize(
    ("falt_id", "varde", "vantat"),
    [
        ("P-KUND.andel_kontant", 0.05, "5 %"),
        ("P-VERK.juniora_konsulter", False, "nej"),
        ("P-ORG.antal_anstallda", 8, "8"),
    ],
)
def test_varden_visas_pa_svenska(regelbas, falt_id, varde, vantat):
    assert visa_varde(regelbas.falt[falt_id], varde) == vantat


def test_bekrafta_ger_ny_profil_och_lamnar_den_gamla_orord(regelbas):
    profil = skapa_profil(regelbas, BYRA)
    ny = bekrafta(profil, regelbas, "P-KUND.andel_riskbransch", "30 %", "Kundregistret", "FfR", DAG)
    assert ny.uppgifter["P-KUND.andel_riskbransch"].varde == 0.3
    assert ny.uppgifter["P-KUND.andel_riskbransch"].bekraftad_av == "roll:FfR"
    assert profil.uppgifter["P-KUND.andel_riskbransch"].status == "saknas"


def test_bekrafta_kraver_kalla(regelbas):
    with pytest.raises(ProfilFel, match="--kalla"):
        bekrafta(skapa_profil(regelbas, BYRA), regelbas, "P-ORG.antal_anstallda", "8", None, "FfR", DAG)


def test_bekrafta_okant_falt_vagras(regelbas):
    with pytest.raises(ProfilFel, match="P-SAKNAS finns inte"):
        bekrafta(skapa_profil(regelbas, BYRA), regelbas, "P-SAKNAS", "1", "Källa", "FfR", DAG)


def test_ej_tillampligt_kraver_motivering(regelbas):
    with pytest.raises(ProfilFel, match="--motivering"):
        markera_ej_tillamplig(skapa_profil(regelbas, BYRA), regelbas, "P-VERK.juniora_konsulter", None, "FfR", DAG)


def test_faltvarden_foljer_status(regelbas):
    profil = bekrafta(skapa_profil(regelbas, BYRA), regelbas, "P-ORG.antal_anstallda", "8", "Lönelistan", "FfR", DAG)
    profil = markera_ej_tillamplig(
        profil, regelbas, "P-VERK.juniora_konsulter", "Byrån har inga anställda konsulter.", "FfR", DAG
    )
    varden = profil.faltvarden()
    assert varden["P-ORG.antal_anstallda"].kunskap is Kunskap.KAND
    assert varden["P-VERK.juniora_konsulter"].kunskap is Kunskap.EJ_TILLAMPLIG
    assert varden["P-KUND.andel_kontant"].kunskap is Kunskap.OKAND


def _urval(regelbas):
    return valj(regelbas, BYRA.regelpaket, BYRA.datum, BYRA.lan)


def test_kritiska_falt_for_lopande_bokforing(regelbas):
    assert kritiska_falt(regelbas, _urval(regelbas)) == KRITISKA


def test_falt_som_avgor_om_ett_krav_galler_ar_kritiska(regelbas):
    krav = regelbas.krav["KRV-LSF-001"]
    villkor = {"falt": "P-ORG.namn", "op": "finns"}
    andrad = regelbas.model_copy(
        update={"krav": {**regelbas.krav, krav.id: krav.model_copy(update={"galler_om": villkor})}}
    )
    assert kritiska_falt(andrad, _urval(andrad)) == KRITISKA | {"P-ORG.namn"}


def test_saknade_kritiska_uppgifter(regelbas, profil_fabrik, real_varden):
    assert len(saknade_kritiska(skapa_profil(regelbas, BYRA), regelbas, _urval(regelbas))) == 11
    assert saknade_kritiska(profil_fabrik(regelbas, real_varden), regelbas, _urval(regelbas)) == ()


def test_personnamn_hamtas_ur_bekraftade_namnfalt(regelbas_v1, profil_fabrik, real_varden):
    # Den aktuella regelbasen deklarerar namnfalt; den historiska v0-basen ändras inte.
    assert personnamn(profil_fabrik(regelbas_v1, real_varden), regelbas_v1) == ("Testa Testsson",)
    okand = profil_fabrik(regelbas_v1, real_varden, okanda=("P-ROLL.ffr_namn",))
    assert personnamn(okand, regelbas_v1) == ()


def test_profilen_sparas_och_lases_oforandrad(datamapp, regelbas, profil_fabrik, real_varden):
    mapp = skapa_byramapp("testbyra")
    profil = profil_fabrik(regelbas, real_varden)
    spara_profil(mapp, profil)
    assert las_profil(mapp) == profil
