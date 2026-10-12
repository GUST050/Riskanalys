from datetime import date, timedelta

import pytest

from riskanalys.regelverk.laddning import ladda_regelbas
from riskanalys.regelverk.urval import UrvalsFel, beskriv_vantande, kravet_galler, valj, vantande_andringar
from riskanalys.regelverk.villkor import Faltvarde, Kunskap

GRANS = date(2026, 11, 20)
VG = "Västra Götaland"


def _ny_lydelse(minimal_filer, **andringar):
    """En kopia av LYD-1 med ändrade fält. Texten är densamma, så LYD-1:s textfil kan återanvändas."""
    return {**minimal_filer["lydelser.yaml"][0], **andringar}


@pytest.fixture
def tva_lydelser(tmp_path, skriv_minimal_regelbas, minimal_filer):
    """KRV-1 med en lydelse som upphör och en som träder i kraft vid GRANS."""
    lydelser = [_ny_lydelse(minimal_filer, upphor=GRANS), _ny_lydelse(minimal_filer, id="LYD-2", ikraft=GRANS)]
    krav = [{**minimal_filer["krav/test.yaml"][0], "lydelser": ["LYD-1", "LYD-2"]}]
    paket = {**minimal_filer["regelpaket/test.yaml"], "lan": [VG, "Stockholm"]}
    rot = skriv_minimal_regelbas(
        tmp_path / "rb",
        {
            "lydelser.yaml": lydelser,
            "lydelsetexter/LYD-2.txt": minimal_filer["lydelsetexter/LYD-1.txt"],
            "krav/test.yaml": krav,
            "regelpaket/test.yaml": paket,
        },
    )
    return ladda_regelbas(rot)


def test_dagen_fore_gransen_galler_den_gamla_lydelsen(tva_lydelser):
    urval = valj(tva_lydelser, "RP-1", GRANS - timedelta(days=1), VG)
    assert [(valt.krav.id, valt.lydelse.id) for valt in urval.krav] == [("KRV-1", "LYD-1")]


def test_samma_dag_som_gransen_galler_den_nya_lydelsen(tva_lydelser):
    urval = valj(tva_lydelser, "RP-1", GRANS, VG)
    assert [(valt.krav.id, valt.lydelse.id) for valt in urval.krav] == [("KRV-1", "LYD-2")]


def test_fore_forsta_lydelsen_finns_inget_krav(tva_lydelser):
    assert valj(tva_lydelser, "RP-1", date(2024, 6, 30), VG).krav == ()


def test_overlappande_lydelser_ger_fel(tmp_path, skriv_minimal_regelbas, minimal_filer):
    lydelser = [*minimal_filer["lydelser.yaml"], _ny_lydelse(minimal_filer, id="LYD-2", ikraft=GRANS)]
    krav = [{**minimal_filer["krav/test.yaml"][0], "lydelser": ["LYD-1", "LYD-2"]}]
    ersattningar = {
        "lydelser.yaml": lydelser,
        "lydelsetexter/LYD-2.txt": minimal_filer["lydelsetexter/LYD-1.txt"],
        "krav/test.yaml": krav,
    }
    regelbas = ladda_regelbas(skriv_minimal_regelbas(tmp_path / "rb", ersattningar))
    with pytest.raises(UrvalsFel, match="flera giltiga lydelser"):
        valj(regelbas, "RP-1", GRANS, VG)


def test_kravets_egna_datum_begransar_urvalet(tmp_path, skriv_minimal_regelbas, minimal_filer):
    krav = [{**minimal_filer["krav/test.yaml"][0], "upphor": date(2025, 1, 1)}]
    regelbas = ladda_regelbas(skriv_minimal_regelbas(tmp_path / "rb", {"krav/test.yaml": krav}))
    assert len(valj(regelbas, "RP-1", date(2024, 12, 31), VG).krav) == 1
    assert valj(regelbas, "RP-1", date(2025, 1, 1), VG).krav == ()


def test_kalla_med_geografi_galler_bara_i_sina_lan(tva_lydelser):
    assert valj(tva_lydelser, "RP-1", GRANS, "Stockholm").krav == ()


def test_okant_regelpaket_ger_fel_med_tillgangliga_paket(minimal_regelbas):
    with pytest.raises(UrvalsFel, match="RP-SAKNAS finns inte. Tillgängliga: RP-1"):
        valj(minimal_regelbas, "RP-SAKNAS", GRANS, VG)


def test_lan_utanfor_paketet_ger_fel(minimal_regelbas):
    with pytest.raises(UrvalsFel, match="gäller inte Skåne"):
        valj(minimal_regelbas, "RP-1", GRANS, "Skåne")


def test_urvalet_tar_med_paketets_tjanster(minimal_regelbas):
    assert valj(minimal_regelbas, "RP-1", GRANS, VG).tjanster == ("T-1",)


def test_vantande_andring_visas_fore_gransen(tva_lydelser):
    urval = valj(tva_lydelser, "RP-1", GRANS - timedelta(days=1), VG)
    andringar = vantande_andringar(tva_lydelser, urval)
    assert [(a.krav_id, a.avsnitt, a.lydelse.id) for a in andringar] == [("KRV-1", ("D-ARB.1",), "LYD-2")]


def test_inga_vantande_andringar_samma_dag_som_gransen(tva_lydelser):
    urval = valj(tva_lydelser, "RP-1", GRANS, VG)
    assert vantande_andringar(tva_lydelser, urval) == ()


def test_beskrivning_av_vantande_andring(tva_lydelser):
    urval = valj(tva_lydelser, "RP-1", GRANS - timedelta(days=1), VG)
    (andring,) = vantande_andringar(tva_lydelser, urval)
    assert beskriv_vantande(andring) == "KRV-1 (avsnitt D-ARB.1) får ny lydelse av 2 kap. 1 § från 2026-11-20."


def _med_tillamplighet(tmp_path, skriv_minimal_regelbas, minimal_filer, galler_om):
    krav = [{**minimal_filer["krav/test.yaml"][0], "galler_om": galler_om}]
    return ladda_regelbas(skriv_minimal_regelbas(tmp_path / "rb", {"krav/test.yaml": krav}))


def test_krav_utan_villkor_galler_alltid(minimal_regelbas):
    assert kravet_galler(minimal_regelbas, minimal_regelbas.krav["KRV-1"], {})


@pytest.mark.parametrize(
    ("varden", "vantat"),
    [
        ({"P-A": Faltvarde(Kunskap.KAND, 0.3)}, True),
        ({"P-A": Faltvarde(Kunskap.KAND, 0.1)}, False),
        ({}, True),
    ],
)
def test_tillamplighet_foljer_villkoret_och_okant_raknas_som_att_kravet_galler(
    tmp_path, skriv_minimal_regelbas, minimal_filer, varden, vantat
):
    regelbas = _med_tillamplighet(
        tmp_path, skriv_minimal_regelbas, minimal_filer, {"falt": "P-A", "op": ">=", "varde": 0.2}
    )
    assert kravet_galler(regelbas, regelbas.krav["KRV-1"], varden) is vantat
