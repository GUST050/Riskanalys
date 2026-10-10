"""Rättslig yrkeskategori, faktisk tjänst och tillsyn provas separat."""

from datetime import date

import pytest

from riskanalys.profil.modeller import Byra, Profil, Uppgift
from riskanalys.regelverk.laddning import ladda_regelbas, STANDARD_REGELBAS

LAN = [
    ("Dalarna", "RP-RED-VG"), ("Gävleborg", "RP-RED-VG"), ("Halland", "RP-RED-VG"),
    ("Värmland", "RP-RED-VG"), ("Västra Götaland", "RP-RED-VG"), ("Örebro", "RP-RED-VG"),
    ("Skåne", "RP-RED-SKANE"), ("Blekinge", "RP-RED-SKANE"), ("Kronoberg", "RP-RED-SKANE"),
    ("Jönköping", "RP-RED-SKANE"), ("Kalmar", "RP-RED-SKANE"), ("Östergötland", "RP-RED-SKANE"),
    ("Stockholm", "RP-RED-STHLM"), ("Södermanland", "RP-RED-STHLM"), ("Gotland", "RP-RED-STHLM"),
    ("Västmanland", "RP-RED-STHLM"), ("Uppsala", "RP-RED-STHLM"), ("Jämtland", "RP-RED-STHLM"),
    ("Västernorrland", "RP-RED-STHLM"), ("Västerbotten", "RP-RED-STHLM"), ("Norrbotten", "RP-RED-STHLM"),
]


@pytest.mark.parametrize("lan,paket", LAN)
def test_alla_lan_foljer_ptf_16(lan, paket):
    from riskanalys.regelverk.tillsyn import tillsynsomrade

    assert tillsynsomrade(lan, False) == paket
    assert tillsynsomrade(lan, True) == "RP-RED-STHLM"


def test_okant_lan_avvisas_aven_for_filial():
    from riskanalys.fel import RiskanalysFel
    from riskanalys.regelverk.tillsyn import tillsynsomrade

    with pytest.raises(RiskanalysFel, match="län"):
        tillsynsomrade("Påhittat", True)


def profil(**andringar):
    varden = {
        "P-ORG.sateslan": "Västra Götaland", "P-ORG.utlandsk_filial": False,
        "P-VERK.auktoriserad_revision": False, "P-VERK.bokforing": True,
        "P-VERK.skatteradgivning": False, "P-VERK.advokat": False,
        "P-VERK.oberoende_jurist": False, "P-VERK.bolagstjanster": True,
        "P-VERK.trust": False, "P-VERK.nominell_aktieagare": False,
    }
    varden.update(andringar)
    uppgifter = {k: Uppgift(varde=v, status="bekräftad", kalla="Syntetiskt uppdrag", datum=date(2026, 10, 10), bekraftad_av="roll:FfR")
                for k, v in varden.items() if v is not None}
    return Profil(byra=Byra(id="syntetisk", regelpaket="RP-RED-VG", lan="Västra Götaland", datum=date(2026, 10, 10)), uppgifter=uppgifter)


def test_bokforingsbyra_med_bolagsbildning_blir_inte_punkt_23():
    from riskanalys.regelverk.tillsyn import rattlig_omfattning

    beslut = rattlig_omfattning(ladda_regelbas(STANDARD_REGELBAS), profil())
    assert beslut.punkter == (19,)
    assert beslut.status == "slutlig"
    assert beslut.hinder == ()
    assert "BT-TILL-19" in beslut.regelspar


def test_ren_bolagsbildare_provas_mot_23():
    from riskanalys.regelverk.tillsyn import rattlig_omfattning

    beslut = rattlig_omfattning(ladda_regelbas(STANDARD_REGELBAS), profil(**{"P-VERK.bokforing": False}))
    assert beslut.punkter == (23,)


@pytest.mark.parametrize("andringar", [
    {"P-VERK.auktoriserad_revision": True}, {"P-VERK.advokat": True},
    {"P-VERK.oberoende_jurist": True}, {"P-VERK.trust": True}, {"P-VERK.nominell_aktieagare": True},
    {"P-VERK.auktoriserad_revision": None}, {"P-ORG.sateslan": None},
    {"P-ORG.sateslan": "Skåne"}, {"P-ORG.utlandsk_filial": True},
])
def test_ogranskad_omfattning_eller_fel_manuellt_paket_ger_hinder(andringar):
    from riskanalys.regelverk.tillsyn import rattlig_omfattning

    beslut = rattlig_omfattning(ladda_regelbas(STANDARD_REGELBAS), profil(**andringar))
    assert beslut.status == "preliminär"
    assert beslut.hinder


def test_foreslaget_sateslan_far_inte_styra_paket():
    from riskanalys.regelverk.tillsyn import rattlig_omfattning

    p = profil()
    p = p.model_copy(update={"uppgifter": {**p.uppgifter, "P-ORG.sateslan": Uppgift(varde="Västra Götaland", status="föreslagen")}})
    beslut = rattlig_omfattning(ladda_regelbas(STANDARD_REGELBAS), p)
    assert beslut.paket_id is None
    assert beslut.status == "preliminär"


def test_motorn_sparar_omfattningshinder_aven_med_kanda_riskuppgifter(regelbas_v1):
    from riskanalys.bedomning.motor import bedom
    from riskanalys.regelverk.urval import valj
    rb = regelbas_v1.model_copy(update={"version": "1.0.0"})
    p = profil(**{"P-ORG.sateslan": "Skåne"})
    resultat = bedom(rb, valj(rb, "RP-RED-VG", p.byra.datum, p.byra.lan), p)
    assert resultat.status == "preliminär"
    assert any("tillsynsområdet" in h for h in resultat.omfattning.hinder)


def test_gammal_bedomning_far_inte_kringga_omfattningsgrinden(regelbas_v1):
    from types import SimpleNamespace
    from riskanalys.faststallelse.grindar import _omfattning
    u = SimpleNamespace(regelbas=regelbas_v1.model_copy(update={"version": "1.0.0"}), profil=profil(**{"P-VERK.trust": True}))
    assert any("P-VERK.trust" in h for h in _omfattning(u))
