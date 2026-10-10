import json
from collections import Counter
from datetime import date
from pathlib import Path

import pytest

from riskanalys.regelverk.laddning import lydelsetextens_kontrollsumma
from riskanalys.regelverk.urval import UrvalsFel, valj
from riskanalys.regelverk.validering import validera

REPO_REGELBAS = Path(__file__).resolve().parents[2] / "regelbas"
TILLSYNSFALL = REPO_REGELBAS.parent / "docs" / "research" / "typfall" / "tillsyn-2026.json"
VG = "Västra Götaland"
KRAV = [f"KRV-LSF-{nummer:03d}" for nummer in range(1, 7)]


def test_repots_regelbas_ar_giltig(regelbas):
    assert validera(regelbas) == []
    assert regelbas.version == "0.1.0"


def test_inget_krav_ar_markt_som_sakkunniggranskat(regelbas):
    assert {krav.sakkunnig.status for krav in regelbas.krav.values()} == {"ej_granskad"}
    assert {paket.paragrafkarta.sakkunnig.status for paket in regelbas.regelpaket.values()} == {"ej_granskad"}


def test_paragrafindelningen_for_foreskrifterna(regelbas):
    paragrafer = regelbas.kallor["SRC-14FS-2024-11"].paragrafer
    per_kapitel = Counter(lagrum.split(" kap.")[0] for lagrum in paragrafer)
    assert per_kapitel == {"1": 2, "2": 12, "3": 7, "4": 1, "5": 2, "6": 4, "7": 3}


def test_paragrafkartan_tacker_2_kap_och_visar_vad_som_saknas(regelbas):
    karta = regelbas.regelpaket["RP-RED-VG"].paragrafkarta
    assert [rad.lagrum for rad in karta.rader] == [f"2 kap. {nummer} §" for nummer in range(1, 13)]
    assert [rad.lagrum for rad in karta.rader if rad.hanterad] == ["2 kap. 1 §", "2 kap. 2 §", "2 kap. 3 §"]
    assert len(karta.ohanterade()) == 9
    assert karta.galler(date(2026, 11, 1))


def test_varje_lydelse_har_text_med_kontrollsumma(regelbas):
    for lydelse_id, lydelse in regelbas.lydelser.items():
        text = (REPO_REGELBAS / "lydelsetexter" / f"{lydelse_id}.txt").read_text(encoding="utf-8")
        assert lydelsetextens_kontrollsumma(text) == lydelse.text_kontrollsumma


def test_lydelsen_av_2_kap_3_kraver_arlig_utvardering_med_datum(regelbas):
    text = (REPO_REGELBAS / "lydelsetexter" / "LYD-LSF-2-3-2024-07-01.txt").read_text(encoding="utf-8")
    assert "minst en gång per år" in text
    assert "Datum för utvärdering och eventuell uppdatering ska framgå" in " ".join(text.split())


def test_varje_krav_har_tillamplighet_och_belagg(regelbas):
    assert {krav.id: krav.galler_om for krav in regelbas.krav.values()} == {krav_id: {"alla": []} for krav_id in KRAV}
    assert all(krav.belagg for krav in regelbas.krav.values())
    assert regelbas.krav["KRV-LSF-006"].belagg == ("dokument", "datum")


def test_bristmonsterkatalogen_ar_komplett(regelbas):
    assert sorted(regelbas.bristmonster) == [f"B-{nummer:02d}" for nummer in range(1, 30)]
    assert regelbas.bristmonster["B-01"].allvar == "blockerande"


def test_automatiserade_bristmonster(regelbas):
    automatiserade = {post.id for post in regelbas.bristmonster.values() if post.automatiserad}
    assert automatiserade == {"B-04", "B-12", "B-16"}


def test_tillsynsfallens_bristmonster_finns_i_katalogen(regelbas):
    """Varje bristmönster som tillsynsfallen hänvisar till ska finnas i regelbasen (research 09)."""
    fall = json.loads(TILLSYNSFALL.read_text(encoding="utf-8"))
    refererade = {
        monster for post in fall["fall"] for fynd in post["forvantade_fynd"] for monster in fynd["bristmonster"]
    }
    assert len(refererade) == 18
    assert refererade <= set(regelbas.bristmonster)


def test_riskmatrisen(regelbas):
    matris = {(rad.sannolikhet, rad.konsekvens): rad.risk for rad in regelbas.metod.riskmatris}
    assert matris[("medel", "betydande")] == "måttlig"
    assert matris[("hög", "betydande")] == "hög"
    assert matris[("låg", "allvarlig")] == "måttlig"
    assert matris[("hög", "allvarlig")] == "mycket hög"


def test_tillatelselistan_innehaller_inga_personuppgifter(regelbas):
    lista = regelbas.tillatelselistor["risk_per_tjanst"]
    assert not any(regelbas.falt[falt_id].personuppgift for falt_id in lista.falt)
    assert "P-ROLL.ffr_namn" not in lista.falt


def test_urval_for_vastra_gotaland(regelbas):
    urval = valj(regelbas, "RP-RED-VG", date(2026, 11, 1), VG)
    assert [valt.krav.id for valt in urval.krav] == KRAV
    assert urval.tjanster == ("T-RED-01",)


def test_foreskrifterna_galler_inte_dagen_fore_ikrafttradandet(regelbas):
    assert valj(regelbas, "RP-RED-VG", date(2024, 6, 30), VG).krav == ()


def test_foreskrifterna_galler_samma_dag_som_ikrafttradandet(regelbas):
    assert [valt.krav.id for valt in valj(regelbas, "RP-RED-VG", date(2024, 7, 1), VG).krav] == KRAV


def test_paketet_galler_inte_stockholm(regelbas):
    with pytest.raises(UrvalsFel, match="gäller inte Stockholm"):
        valj(regelbas, "RP-RED-VG", date(2026, 11, 1), "Stockholm")
