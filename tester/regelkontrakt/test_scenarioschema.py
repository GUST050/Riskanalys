"""Schema och validering för scenariometoden (tjänst × hot). Alla uppgifter är syntetiska."""

import copy
from pathlib import Path

import pytest
from pydantic import ValidationError

from riskanalys.regelverk.laddning import ladda_regelbas
from riskanalys.regelverk.modeller import (
    Effekt,
    Falt,
    Hot,
    Kontroll,
    Metod,
    Riktning,
    Sarbarhet,
    Scenariometod,
    hot_dimensioner,
)
from riskanalys.regelverk.validering import validera

V0 = Path(__file__).resolve().parents[1] / "fixturer" / "regelbas_v0"
# Summor för den frysta M1-regelbasen före scenarioschemat (se även test_etiketter.py).
V0_KONTROLLSUMMA = "sha256:39c841b2cf60ff2083615bf76c20ee2fe59dcc8d1d5442e84b402dbbd2523bf3"
V0_PAKET = "sha256:55d2dc582f5e7fa6cb31a9c7976e335a766d7ce153607efb613a8e2e40a784ef"

NIVAER = ("låg", "medel", "hög")
SANN_02 = {
    ("låg", "låg"): "låg", ("låg", "medel"): "låg", ("låg", "hög"): "medel",
    ("medel", "låg"): "låg", ("medel", "medel"): "medel", ("medel", "hög"): "hög",
    ("hög", "låg"): "medel", ("hög", "medel"): "hög", ("hög", "hög"): "hög",
}


def _regel(regel_id: str) -> dict:
    return {"id": regel_id, "grund": "metodval", "forklaring": "Testregel."}


def _sannolikhetsmatris() -> list[dict]:
    return [
        {
            "id": f"BT-SANN-02-{nummer:02d}",
            "hot": hot,
            "sarbarhet": sarbarhet,
            "sannolikhet": SANN_02[(hot, sarbarhet)],
            "grund": "metodval",
            "forklaring": f"Hotnivå {hot} och sårbarhetsnivå {sarbarhet}.",
        }
        for nummer, (hot, sarbarhet) in enumerate(SANN_02, start=1)
    ]


def _scenario() -> dict:
    return {
        "hotniva": _regel("BT-HOT-01"),
        "sarbarhetsniva": _regel("BT-SARB-01"),
        "sannolikhetsmatris": _sannolikhetsmatris(),
        "kvarstaende": _regel("BT-KVAR-03"),
        "aggregering": _regel("BT-TJ-01"),
    }


def _riktning(hot: list[str], tjanst: str = "T-1") -> dict:
    return {"tjanst": tjanst, "hot": hot, "kallor": ["SRC-1"], "grund": "metodval", "motivering": "Testmotivering."}


@pytest.fixture
def scenariofiler(minimal_filer):
    """Den minimala regelbasen med scenariometod, tre hot i T-1 och fullständiga kopplingar."""
    filer = copy.deepcopy(minimal_filer)
    filer["kataloger/hot.yaml"] = [
        {"id": f"H-{nummer}", "namn": f"Testhot {nummer}", "beskrivning": "Test.", "kallor": ["SRC-1"],
         "niva": "medel", "nivamotivering": "Testmotivering."}
        for nummer in (1, 2, 3)
    ]
    filer["kataloger/sarbarheter.yaml"][0]["hot"] = ["H-1"]
    filer["kataloger/kontroller.yaml"][0]["riktar_sig_mot"] = [_riktning(["H-1"])]
    filer["kataloger/tjanster.yaml"][0]["hot"] = ["H-1", "H-2", "H-3"]
    filer["beslutstabeller/metod.yaml"]["scenario"] = _scenario()
    return filer


def _fel(tmp_path, skriv_minimal_regelbas, filer) -> list[str]:
    return validera(ladda_regelbas(skriv_minimal_regelbas(tmp_path / "rb", filer)))


# --- Schema ---------------------------------------------------------------


def test_hot_dimensioner_harleds_fran_galler_tf_och_id():
    assert hot_dimensioner(Hot(id="H-01", namn="x", beskrivning="x", kallor=("SRC-1",))) == ("pt",)
    assert hot_dimensioner(Hot(id="H-03", namn="x", beskrivning="x", kallor=("SRC-1",), galler_tf=True)) == ("pt", "tf")
    assert hot_dimensioner(Hot(id="H-TF-01", namn="x", beskrivning="x", kallor=("SRC-1",), galler_tf=True)) == ("tf",)


def test_hot_dimensioner_anges_uttryckligen():
    hot = Hot(id="H-01", namn="x", beskrivning="x", kallor=("SRC-1",), dimensioner=("tf",))
    assert hot_dimensioner(hot) == ("tf",)


def test_hot_dimensioner_far_inte_upprepas():
    with pytest.raises(ValidationError):
        Hot(id="H-01", namn="x", beskrivning="x", kallor=("SRC-1",), dimensioner=("pt", "pt"))


def test_repots_hot_far_harledda_dimensioner():
    hot = ladda_regelbas().hot
    assert hot_dimensioner(hot["H-01"]) == ("pt",)
    assert hot_dimensioner(hot["H-03"]) == ("pt", "tf")
    assert hot_dimensioner(hot["H-TF-01"]) == ("tf",)


def test_effekt_tillater_negativa_varden_men_inte_noll():
    assert Effekt(sannolikhet=-1).sannolikhet == -1
    assert Effekt(sannolikhet=-2).sannolikhet == -2
    assert Effekt(sannolikhet=2).sannolikhet == 2
    for ogiltig in (0, 3, -3):
        with pytest.raises(ValidationError):
            Effekt(sannolikhet=ogiltig)


def test_flerval_kraver_alternativ():
    falt = Falt(id="P-X", typ="flerval", fraga="Vilka?", varfor="Test.", val=("H-1", "H-2"))
    assert falt.typ == "flerval" and falt.val == ("H-1", "H-2")
    with pytest.raises(ValidationError, match="flerval"):
        Falt(id="P-X", typ="flerval", fraga="Vilka?", varfor="Test.")


def test_riktning_kraver_hot_och_kallor():
    with pytest.raises(ValidationError):
        Riktning(tjanst="T-1", hot=(), kallor=("SRC-1",), grund="metodval", motivering="x")
    with pytest.raises(ValidationError):
        Riktning(tjanst="T-1", hot=("H-1",), kallor=(), grund="metodval", motivering="x")


def test_metodens_regler_omfattar_scenariometoden(scenariofiler, tmp_path, skriv_minimal_regelbas):
    rb = ladda_regelbas(skriv_minimal_regelbas(tmp_path / "rb", scenariofiler))
    assert isinstance(rb.metod.scenario, Scenariometod)
    ids = [regel.id for regel in rb.metod.regler()]
    assert {"BT-HOT-01", "BT-SARB-01", "BT-KVAR-03", "BT-TJ-01"} <= set(ids)
    assert [i for i in ids if i.startswith("BT-SANN-02-")] == [f"BT-SANN-02-{n:02d}" for n in range(1, 10)]
    assert {"BT-HOT-01", "BT-SANN-02-05"} <= rb.alla_id()


def test_nya_falt_utelamnas_nar_de_ar_tomma():
    hot = Hot(id="H-01", namn="x", beskrivning="x", kallor=("SRC-1",))
    assert not {"niva", "nivamotivering", "dimensioner"} & set(hot.model_dump(mode="json"))
    sarbarhet = Sarbarhet(id="S-1", namn="x", omrade="kund", grund="metodval", villkor={"alla": []},
                          effekt=Effekt(sannolikhet=1), kallor=("SRC-1",))
    assert "hot" not in sarbarhet.model_dump(mode="json")
    kontroll = Kontroll(id="C-1", namn="x", beskrivning="x", utformning_falt="a", genomforande_falt="b")
    assert "riktar_sig_mot" not in kontroll.model_dump(mode="json")


def test_satta_falt_serialiseras(scenariofiler, tmp_path, skriv_minimal_regelbas):
    rb = ladda_regelbas(skriv_minimal_regelbas(tmp_path / "rb", scenariofiler))
    assert rb.hot["H-1"].model_dump(mode="json")["niva"] == "medel"
    assert rb.sarbarheter["S-1"].model_dump(mode="json")["hot"] == ["H-1"]
    assert rb.kontroller["C-1"].model_dump(mode="json")["riktar_sig_mot"][0]["hot"] == ["H-1"]
    assert "scenario" in rb.metod.model_dump(mode="json")


def test_metod_utan_scenario_serialiseras_som_forut(minimal_regelbas):
    assert minimal_regelbas.metod.scenario is None
    assert "scenario" not in minimal_regelbas.metod.model_dump(mode="json")


def test_regelbas_v0_ar_oforandrad_utan_scenariometod():
    rb = ladda_regelbas(V0)
    assert rb.metod.scenario is None
    assert validera(rb) == []
    assert rb.kontrollsumma == V0_KONTROLLSUMMA
    assert rb.paketets_innehallssumma("RP-RED-VG") == V0_PAKET


def test_repots_regelbas_validerar_utan_scenariometod_och_utan_nya_nycklar():
    rb = ladda_regelbas()
    assert rb.metod.scenario is None
    assert validera(rb) == []
    data = rb.model_dump(mode="json")
    assert "scenario" not in data["metod"]
    assert all(not {"niva", "nivamotivering", "dimensioner"} & set(h) for h in data["hot"].values())
    assert all("hot" not in s for s in data["sarbarheter"].values())
    assert all("riktar_sig_mot" not in k for k in data["kontroller"].values())


# --- Validering med scenariometod ------------------------------------------


def test_fullstandig_scenariometod_ar_giltig(scenariofiler, tmp_path, skriv_minimal_regelbas):
    assert _fel(tmp_path, skriv_minimal_regelbas, scenariofiler) == []


def test_hot_i_tjanst_utan_niva_underkanns(scenariofiler, tmp_path, skriv_minimal_regelbas):
    del scenariofiler["kataloger/hot.yaml"][1]["niva"]
    fel = _fel(tmp_path, skriv_minimal_regelbas, scenariofiler)
    assert any(rad.startswith("H-2: hotet saknar hotnivå") for rad in fel), fel


def test_hot_utanfor_tjanster_far_sakna_niva(scenariofiler, tmp_path, skriv_minimal_regelbas):
    scenariofiler["kataloger/hot.yaml"].append(
        {"id": "H-9", "namn": "Oanvänt", "beskrivning": "Test.", "kallor": ["SRC-1"]})
    assert _fel(tmp_path, skriv_minimal_regelbas, scenariofiler) == []


def test_sarbarhet_utan_hot_underkanns(scenariofiler, tmp_path, skriv_minimal_regelbas):
    del scenariofiler["kataloger/sarbarheter.yaml"][0]["hot"]
    fel = _fel(tmp_path, skriv_minimal_regelbas, scenariofiler)
    assert any(rad.startswith("S-1: sårbarheten saknar koppling till hot") for rad in fel), fel


def test_sarbarhet_med_okant_hot_underkanns(scenariofiler, tmp_path, skriv_minimal_regelbas):
    scenariofiler["kataloger/sarbarheter.yaml"][0]["hot"] = ["H-1", "H-SAKNAS"]
    fel = _fel(tmp_path, skriv_minimal_regelbas, scenariofiler)
    assert "S-1: hänvisar till hotet H-SAKNAS som inte finns." in fel


def test_riktning_med_okant_hot_underkanns(scenariofiler, tmp_path, skriv_minimal_regelbas):
    scenariofiler["kataloger/kontroller.yaml"][0]["riktar_sig_mot"] = [_riktning(["H-SAKNAS"])]
    fel = _fel(tmp_path, skriv_minimal_regelbas, scenariofiler)
    assert "C-1, riktning mot T-1: hänvisar till hotet H-SAKNAS som inte finns." in fel


def test_riktning_mot_tjanst_utan_kontrollen_underkanns(scenariofiler, tmp_path, skriv_minimal_regelbas):
    scenariofiler["kataloger/tjanster.yaml"][0]["kontroller"] = []
    fel = _fel(tmp_path, skriv_minimal_regelbas, scenariofiler)
    assert any(rad.startswith("C-1, riktning mot T-1: tjänsten har inte kontrollen C-1") for rad in fel), fel


def test_riktning_mot_hot_som_tjansten_saknar_underkanns(scenariofiler, tmp_path, skriv_minimal_regelbas):
    scenariofiler["kataloger/hot.yaml"].append(
        {"id": "H-9", "namn": "Annat", "beskrivning": "Test.", "kallor": ["SRC-1"], "niva": "låg"})
    scenariofiler["kataloger/kontroller.yaml"][0]["riktar_sig_mot"] = [_riktning(["H-9"])]
    fel = _fel(tmp_path, skriv_minimal_regelbas, scenariofiler)
    assert "C-1, riktning mot T-1: hänvisar till hotet i tjänsten H-9 som inte finns." in fel


def test_riktning_mot_okand_tjanst_underkanns(scenariofiler, tmp_path, skriv_minimal_regelbas):
    scenariofiler["kataloger/kontroller.yaml"][0]["riktar_sig_mot"] = [_riktning(["H-1"], tjanst="T-SAKNAS")]
    fel = _fel(tmp_path, skriv_minimal_regelbas, scenariofiler)
    assert any(rad.startswith("C-1, riktning mot T-SAKNAS: tjänsten finns inte") for rad in fel), fel


def test_riktning_med_okand_kalla_underkanns(scenariofiler, tmp_path, skriv_minimal_regelbas):
    riktning = _riktning(["H-1"])
    riktning["kallor"] = ["SRC-SAKNAS"]
    scenariofiler["kataloger/kontroller.yaml"][0]["riktar_sig_mot"] = [riktning]
    fel = _fel(tmp_path, skriv_minimal_regelbas, scenariofiler)
    assert "C-1, riktning mot T-1: hänvisar till källan SRC-SAKNAS som inte finns." in fel


def test_riktning_mot_samtliga_hot_underkanns(scenariofiler, tmp_path, skriv_minimal_regelbas):
    scenariofiler["kataloger/kontroller.yaml"][0]["riktar_sig_mot"] = [_riktning(["H-1", "H-2", "H-3"])]
    fel = _fel(tmp_path, skriv_minimal_regelbas, scenariofiler)
    assert any(rad.startswith("C-1, riktning mot T-1: kontrollen riktar sig mot samtliga") for rad in fel), fel


def test_flera_riktningar_som_tillsammans_tacker_samtliga_hot_underkanns(scenariofiler, tmp_path, skriv_minimal_regelbas):
    scenariofiler["kataloger/kontroller.yaml"][0]["riktar_sig_mot"] = [_riktning(["H-1", "H-2"]), _riktning(["H-3"])]
    fel = _fel(tmp_path, skriv_minimal_regelbas, scenariofiler)
    assert any(rad.startswith("C-1, riktning mot T-1: kontrollen riktar sig mot samtliga") for rad in fel), fel


def test_riktning_mot_alla_hot_tillats_nar_tjansten_har_farre_an_tre(scenariofiler, tmp_path, skriv_minimal_regelbas):
    scenariofiler["kataloger/tjanster.yaml"][0]["hot"] = ["H-1", "H-2"]
    scenariofiler["kataloger/kontroller.yaml"][0]["riktar_sig_mot"] = [_riktning(["H-1", "H-2"])]
    assert _fel(tmp_path, skriv_minimal_regelbas, scenariofiler) == []


def test_matris_som_saknar_cell_underkanns(scenariofiler, tmp_path, skriv_minimal_regelbas):
    scenariofiler["beslutstabeller/metod.yaml"]["scenario"]["sannolikhetsmatris"].pop()
    fel = _fel(tmp_path, skriv_minimal_regelbas, scenariofiler)
    assert ("Sannolikhetsmatrisen ska ha exakt en rad för hotnivå hög och sårbarhetsnivå hög, har 0. "
            "Rätta scenario.sannolikhetsmatris i beslutstabeller/metod.yaml.") in fel


def test_matris_med_dubblerad_cell_underkanns(scenariofiler, tmp_path, skriv_minimal_regelbas):
    matris = scenariofiler["beslutstabeller/metod.yaml"]["scenario"]["sannolikhetsmatris"]
    matris[8] = {**matris[0], "id": "BT-SANN-02-09"}
    fel = _fel(tmp_path, skriv_minimal_regelbas, scenariofiler)
    assert any(rad.startswith("Sannolikhetsmatrisen ska ha exakt en rad för hotnivå låg och sårbarhetsnivå låg, har 2")
               for rad in fel), fel
    assert any("hotnivå hög och sårbarhetsnivå hög, har 0" in rad for rad in fel), fel


def test_utan_scenariometod_kravs_varken_niva_eller_hotkoppling(minimal_filer, tmp_path, skriv_minimal_regelbas):
    """Äldre regelbaser utan metod.scenario ska validera som förut."""
    assert "hot" not in minimal_filer["kataloger/sarbarheter.yaml"][0]
    assert "niva" not in minimal_filer["kataloger/hot.yaml"][0]
    assert _fel(tmp_path, skriv_minimal_regelbas, minimal_filer) == []


def test_scenariometod_kan_byggas_direkt():
    metod = Metod.model_validate({
        "riskmatris": [], "sannolikhet": _regel("BT-SANN-01"), "konsekvens": _regel("BT-KONS-01"),
        "terrorfinansiering": _regel("BT-TF-01"), "kvarstaende_ej_belagd": _regel("BT-KVAR-01"),
        "kvarstaende_sankning": _regel("BT-KVAR-02"), "scenario": _scenario(),
    })
    assert metod.scenario.hotniva.id == "BT-HOT-01"
    assert len(metod.scenario.sannolikhetsmatris) == 9
    assert {(r.hot, r.sarbarhet): r.sannolikhet for r in metod.scenario.sannolikhetsmatris} == SANN_02


def test_attest_omfattar_scenariometodens_regler(scenariofiler, tmp_path, skriv_minimal_regelbas):
    """Scenarioreglerna är granskningsobjekt; ett godkännande ska också nå dem."""
    from datetime import date

    from riskanalys.regelverk.sakkunnig import Granskningsbeslut, Objektbeslut, applicera_attester, granskningsobjekt
    from riskanalys.regelverk.validering_m2 import attesthinder

    rb = ladda_regelbas(skriv_minimal_regelbas(tmp_path / "rb", scenariofiler))
    objekt = granskningsobjekt(rb, "RP-1")
    scenarioregler = [regel.id for regel in rb.metod.scenario.regler()]
    assert set(scenarioregler) <= set(objekt)
    beslut = Granskningsbeslut(
        paket="RP-1", version=rb.version, datum=date(2026, 10, 18), granskningsdatum=date(2026, 10, 18),
        kontrollsumma=rb.paketets_innehallssumma("RP-1"), granskare="Syntetisk granskare",
        kompetens="Syntetisk sakkunnig", oberoende=True,
        objekt={k: Objektbeslut(beslut="verifierad", kommentar="Syntetiskt prov") for k in objekt},
    )
    attesterad = applicera_attester(rb, beslut)
    assert all(regel.sakkunnig.status == "verifierad" for regel in attesterad.metod.scenario.regler())
    assert not [h for h in attesthinder(attesterad, "RP-1") if h.split(":")[0] in scenarioregler]


def test_negativ_effekt_utan_scenariometod_underkanns(minimal_filer, tmp_path, skriv_minimal_regelbas):
    """Den äldre motorn får aldrig sänkas tyst av en negativ effekt."""
    minimal_filer["kataloger/sarbarheter.yaml"][0]["effekt"] = {"sannolikhet": -1}
    fel = _fel(tmp_path, skriv_minimal_regelbas, minimal_filer)
    assert any(rad.startswith("S-1: Negativ effekt kräver scenariometoden;") for rad in fel), fel


def test_negativ_effekt_med_scenariometod_godtas(scenariofiler, tmp_path, skriv_minimal_regelbas):
    scenariofiler["kataloger/sarbarheter.yaml"][0]["effekt"] = {"sannolikhet": -1}
    assert _fel(tmp_path, skriv_minimal_regelbas, scenariofiler) == []
