"""Scenarioberäkning i riskmotorn (spec 2026-10-18, Modellen steg 1–6). Alla uppgifter är syntetiska."""

import copy
import hashlib
from datetime import date

import pytest

from riskanalys.bedomning.modeller import Bedomning, Tjanstbedomning
from riskanalys.bedomning.motor import bedom, bedom_tjanst
from riskanalys.bedomning.scenarier import IAKTTAGET_SUFFIX
from riskanalys.fel import RiskanalysFel
from riskanalys.profil.modeller import Byra, Period, Profil, Uppgift
from riskanalys.regelverk.laddning import ladda_regelbas
from riskanalys.regelverk.urval import valj
from riskanalys.regelverk.validering import validera
from tester.conftest import REAL_VARDEN, REPO_REGELBAS

NIVAER = ("låg", "medel", "hög")
SANN_02 = {
    ("låg", "låg"): "låg", ("låg", "medel"): "låg", ("låg", "hög"): "medel",
    ("medel", "låg"): "låg", ("medel", "medel"): "medel", ("medel", "hög"): "hög",
    ("hög", "låg"): "medel", ("hög", "medel"): "hög", ("hög", "hög"): "hög",
}
SANN_ID = {cell: f"BT-SANN-02-{nummer:02d}" for nummer, cell in enumerate(SANN_02, start=1)}
DAG = date(2026, 10, 1)
PERIOD = Period(fran=date(2026, 1, 1), till=date(2026, 9, 30))
IAKTTAGELSE = f"P-TJ.t1{IAKTTAGET_SUFFIX}"
EFFEKTVAL = ["verksam", "begränsad", "verkningslös", "ej_bedömd"]

# Pinnade summor av model_dump_json() beräknade med motorn före scenariometoden (commit 52ed984).
FORE_SCENARIO = {
    "v0_real": "3ca60e09b235f5163ccc1e25b9c76851316f0397fc027cca5d7014c3319c1570",
    "v0_belagd": "4a8296117eba5c34cfe569e76daa0a13a29cee6515828d7a0064780b3ebdbaaf",
    "v0_alla": "8bcde51967140f4ae5d92e2d8c11de4955efc40f7e97c4f90bc524993247318c",
    "v0_inga": "7f58c7a64e86da1e000179d01241eb9a6b191c74343bbab44bfe3832a3022f79",
    "v0_ej": "1cc6fb59536fd7b7bb28241762c23b0d7512dc118db3ead8e0006358afa5b05d",
    "v0_okand": "f42199fcb2ffa336675510f10bf7934e9f8ceba59e2b8d66d23db6199ca4ba08",
    "repo_komplett": "6733b7c9d8bdf07fa1dba02aae7af99bfa43546cc950cd601dc45d5182f89326",
}
V0_FALL = {
    "v0_real": {},
    "v0_belagd": {"P-KONTROLL.C-07.genomforande": "belagt"},
    "v0_alla": {"P-KUND.andel_kontant": 0.2, "P-VERK.juniora_konsulter": True},
    "v0_inga": {"P-KUND.andel_riskbransch": 0.1, "P-KANAL.andel_digitalt_underlag": 0.2},
    "v0_ej": {"P-TJ.T-RED-01.erbjuds": False},
}


def _regel(regel_id: str) -> dict:
    return {"id": regel_id, "grund": "metodval", "forklaring": "Testregel."}


def _scenariometod() -> dict:
    matris = [
        {"id": SANN_ID[(hot, sarbarhet)], "hot": hot, "sarbarhet": sarbarhet, "sannolikhet": sannolikhet,
         "grund": "metodval", "forklaring": f"Hotnivå {hot} och sårbarhetsnivå {sarbarhet}."}
        for (hot, sarbarhet), sannolikhet in SANN_02.items()
    ]
    return {"hotniva": _regel("BT-HOT-01"), "sarbarhetsniva": _regel("BT-SARB-01"), "sannolikhetsmatris": matris,
            "kvarstaende": _regel("BT-KVAR-03"), "aggregering": _regel("BT-TJ-01")}


def _hot(hot_id: str, niva: str | None, galler_tf: bool = False) -> dict:
    post = {"id": hot_id, "namn": f"Testhot {hot_id}", "beskrivning": "Test.", "kallor": ["SRC-1"],
            "galler_tf": galler_tf, "nivamotivering": "Testmotivering."}
    return {**post, "niva": niva} if niva else post


def _falt(falt_id: str, typ: str, **extra) -> dict:
    return {"id": falt_id, "typ": typ, "fraga": "Testfråga?", "varfor": "Test.", **extra}


def _kontrollfalt(prefix: str) -> list[dict]:
    return [
        _falt(f"{prefix}.utf", "val", val=["finns", "saknas"]),
        _falt(f"{prefix}.gen", "val", val=["belagt", "ej_belagt"]),
        _falt(f"{prefix}.eff", "val", val=EFFEKTVAL, periodkrav=True),
        _falt(f"{prefix}.utfall", "text", periodkrav=True),
    ]


def _kontroll(kontroll_id: str, prefix: str, riktade_hot: list[str]) -> dict:
    post = {"id": kontroll_id, "namn": f"Testkontroll {kontroll_id}", "beskrivning": "Test.",
            "utformning_falt": f"{prefix}.utf", "genomforande_falt": f"{prefix}.gen",
            "effekt_falt": f"{prefix}.eff", "utfall_falt": f"{prefix}.utfall"}
    if riktade_hot:
        post["riktar_sig_mot"] = [{"tjanst": "T-1", "hot": riktade_hot, "kallor": ["SRC-1"], "grund": "metodval",
                                   "motivering": "Testmotivering."}]
    return post


@pytest.fixture
def filer(minimal_filer):
    """Syntetisk regelbas med scenariometod: fyra hot, två sårbarheter och två kontroller i T-1."""
    filer = copy.deepcopy(minimal_filer)
    filer["falt.yaml"] = [
        _falt("P-TJ.t1_erbjuds", "bool"),
        _falt(IAKTTAGELSE, "flerval", val=["H-1", "H-2", "H-3", "H-TF-1"]),
        _falt("P-A", "andel"),
        _falt("P-B", "andel"),
        *_kontrollfalt("P-C1"),
        *_kontrollfalt("P-C2"),
    ]
    filer["kataloger/hot.yaml"] = [_hot("H-1", "medel"), _hot("H-2", "låg"), _hot("H-3", "hög", galler_tf=True),
                                   _hot("H-TF-1", "medel", galler_tf=True)]
    sarbarhet = filer["kataloger/sarbarheter.yaml"][0]
    filer["kataloger/sarbarheter.yaml"] = [
        {**sarbarhet, "id": "S-1", "villkor": {"falt": "P-A", "op": ">=", "varde": 0.2}, "hot": ["H-1"],
         "galler": "penningtvatt"},
        {**sarbarhet, "id": "S-2", "villkor": {"falt": "P-B", "op": ">=", "varde": 0.2}, "hot": ["H-2", "H-3"],
         "galler": "bada"},
    ]
    filer["kataloger/kontroller.yaml"] = [_kontroll("C-1", "P-C1", ["H-1"]), _kontroll("C-2", "P-C2", [])]
    tjanst = filer["kataloger/tjanster.yaml"][0]
    filer["kataloger/tjanster.yaml"] = [{**tjanst, "erbjuds_falt": "P-TJ.t1_erbjuds",
                                         "hot": ["H-1", "H-2", "H-3", "H-TF-1"], "sarbarheter": ["S-1", "S-2"],
                                         "kontroller": ["C-1", "C-2"]}]
    filer["tillatelselistor.yaml"] = [{"id": "risk_per_tjanst", "falt": ["P-A", "P-B"], "undvik": ["B-1"]}]
    filer["beslutstabeller/metod.yaml"] = {**filer["beslutstabeller/metod.yaml"], "scenario": _scenariometod()}
    return filer


@pytest.fixture
def ladda(tmp_path, skriv_minimal_regelbas):
    raknare = iter(range(1000))

    def _ladda(filer):
        return ladda_regelbas(skriv_minimal_regelbas(tmp_path / f"rb{next(raknare)}", filer))

    return _ladda


def _kontrollvarden(prefix: str, utf="finns", gen="belagt", eff="verksam") -> dict:
    return {f"{prefix}.utf": utf, f"{prefix}.gen": gen, f"{prefix}.eff": eff,
            f"{prefix}.utfall": "Syntetiskt prov av kontrollens utfall."}


BAS = {"P-TJ.t1_erbjuds": True, "P-A": 0.0, "P-B": 0.0,
       **_kontrollvarden("P-C1", gen="ej_belagt"), **_kontrollvarden("P-C2", gen="ej_belagt")}


def _profil(rb, varden: dict, okanda: tuple[str, ...] = ()) -> Profil:
    byra = Byra(id="testbyra", regelpaket="RP-1", datum=date(2026, 11, 1), lan="Västra Götaland")

    def uppgift(falt_id):
        if falt_id not in varden or falt_id in okanda:
            return Uppgift()
        return Uppgift(varde=varden[falt_id], status="bekräftad", kalla="Syntetiskt testfall", datum=DAG,
                       bekraftad_av="roll:FfR", period=PERIOD if rb.falt[falt_id].periodkrav else None)

    return Profil(byra=byra, uppgifter={falt_id: uppgift(falt_id) for falt_id in rb.falt})


def _bedom(rb, extra: dict | None = None, okanda: tuple[str, ...] = ()) -> Tjanstbedomning:
    return bedom_tjanst(rb, rb.tjanster["T-1"], _profil(rb, {**BAS, **(extra or {})}, okanda))


def _scenario(t: Tjanstbedomning, hot: str, dimension: str = "pt"):
    (scenario,) = [s for s in t.scenarier if s.hot == hot and s.dimension == dimension]
    return scenario


def _satt_hot(filer, hot_id: str, **andringar) -> None:
    filer["kataloger/hot.yaml"] = [{**h, **andringar} if h["id"] == hot_id else h for h in filer["kataloger/hot.yaml"]]


# --- Grundfallet ------------------------------------------------------------


def test_syntetiska_regelbasen_ar_giltig(filer, ladda):
    assert validera(ladda(filer)) == []


def test_scenarier_i_katalogordning_pt_forst_och_tf_for_tf_hot(filer, ladda):
    t = _bedom(ladda(filer))
    assert [(s.hot, s.dimension) for s in t.scenarier] == [
        ("H-1", "pt"), ("H-2", "pt"), ("H-3", "pt"), ("H-3", "tf"), ("H-TF-1", "tf")]


def test_grundfallet_ger_niva_per_scenario_och_maxvarden_for_tjansten(filer, ladda):
    t = _bedom(ladda(filer))
    nivaer = {(s.hot, s.dimension): (s.hotniva, s.sarbarhetsniva, s.sannolikhet, s.konsekvens, s.risk, s.kvarstaende)
              for s in t.scenarier}
    assert nivaer == {
        ("H-1", "pt"): ("medel", "medel", "medel", "betydande", "måttlig", "måttlig"),
        ("H-2", "pt"): ("låg", "medel", "låg", "betydande", "måttlig", "måttlig"),
        ("H-3", "pt"): ("hög", "medel", "hög", "betydande", "hög", "hög"),
        ("H-3", "tf"): ("hög", "låg", "medel", "allvarlig", "hög", None),
        ("H-TF-1", "tf"): ("medel", "låg", "låg", "allvarlig", "måttlig", None),
    }
    assert (t.inneboende.sannolikhet, t.inneboende.konsekvens, t.inneboende.risk) == ("hög", "betydande", "hög")
    assert (t.terrorfinansiering.sannolikhet, t.terrorfinansiering.risk) == ("medel", "hög")
    assert t.kvarstaende == "hög"
    assert t.status == "slutlig" and t.okanda_uppgifter == ()
    assert t.hot == ("H-1", "H-2", "H-3", "H-TF-1")


@pytest.mark.parametrize(("hotniva", "sarbarhetsniva"), list(SANN_02))
def test_sannolikhetsmatrisens_nio_celler(filer, ladda, hotniva, sarbarhetsniva):
    _satt_hot(filer, "H-1", niva=hotniva)
    filer["kataloger/tjanster.yaml"][0]["grund_sannolikhet"] = sarbarhetsniva
    t = _bedom(ladda(filer))
    scenario = _scenario(t, "H-1")
    assert (scenario.hotniva, scenario.sarbarhetsniva) == (hotniva, sarbarhetsniva)
    assert scenario.sannolikhet == SANN_02[(hotniva, sarbarhetsniva)]
    assert SANN_ID[(hotniva, sarbarhetsniva)] in scenario.regelspar
    assert SANN_ID[(hotniva, sarbarhetsniva)] in t.regelspar


# --- Sårbarheter ------------------------------------------------------------


def test_sarbarhet_hojer_bara_de_hot_den_mojliggor(filer, ladda):
    t = _bedom(ladda(filer), {"P-A": 0.5})
    assert t.tillampade_sarbarheter == ("S-1",)
    assert (_scenario(t, "H-1").sarbarhetsniva, _scenario(t, "H-1").sarbarheter) == ("hög", ("S-1",))
    assert (_scenario(t, "H-2").sarbarhetsniva, _scenario(t, "H-2").sarbarheter) == ("medel", ())
    assert _scenario(t, "H-3").sarbarhetsniva == "medel"


def test_sarbarhet_som_bara_galler_penningtvatt_paverkar_inte_tf_scenariot(filer, ladda):
    filer["kataloger/sarbarheter.yaml"][0]["hot"] = ["H-3"]
    t = _bedom(ladda(filer), {"P-A": 0.5})
    assert _scenario(t, "H-3", "pt").sarbarheter == ("S-1",)
    assert _scenario(t, "H-3", "pt").sarbarhetsniva == "hög"
    assert _scenario(t, "H-3", "tf").sarbarheter == ()
    assert _scenario(t, "H-3", "tf").sarbarhetsniva == "låg"


def test_sarbarhet_som_galler_bada_hojer_bade_pt_och_tf(filer, ladda):
    t = _bedom(ladda(filer), {"P-B": 0.5})
    assert _scenario(t, "H-3", "pt").sarbarhetsniva == "hög"
    assert _scenario(t, "H-3", "tf").sarbarhetsniva == "medel"
    assert _scenario(t, "H-3", "tf").sarbarheter == ("S-2",)
    assert _scenario(t, "H-TF-1", "tf").sarbarheter == ()


def test_negativ_effekt_sanker_sarbarhetsnivan_med_golv_lag(filer, ladda):
    filer["kataloger/sarbarheter.yaml"][1]["effekt"] = {"sannolikhet": -2}
    rb = ladda(filer)
    assert validera(rb) == []
    t = _bedom(rb, {"P-B": 0.5})
    assert _scenario(t, "H-2").sarbarhetsniva == "låg"
    assert _scenario(t, "H-3", "tf").sarbarhetsniva == "låg"


def test_ersatt_sarbarhet_raknas_inte(filer, ladda):
    filer["kataloger/sarbarheter.yaml"][1]["hot"] = ["H-1"]
    filer["kataloger/sarbarheter.yaml"][1]["ersatter"] = ["S-1"]
    t = _bedom(ladda(filer), {"P-A": 0.5, "P-B": 0.5})
    assert t.tillampade_sarbarheter == ("S-2",)
    assert _scenario(t, "H-1").sarbarheter == ("S-2",)
    assert _scenario(t, "H-1").sarbarhetsniva == "hög"


def test_ersattning_galler_bara_inom_samma_scenario(filer, ladda):
    """A (hot H-1) ersätter B (hot H-1 och H-2): i H-1 räknas bara A, i H-2 räknas B som vanligt."""
    filer["kataloger/sarbarheter.yaml"][0]["hot"] = ["H-1", "H-2"]
    filer["kataloger/sarbarheter.yaml"][1].update(hot=["H-1"], ersatter=["S-1"], galler="penningtvatt")
    t = _bedom(ladda(filer), {"P-A": 0.5, "P-B": 0.5})
    assert _scenario(t, "H-1").sarbarheter == ("S-2",)
    assert _scenario(t, "H-1").sarbarhetsniva == "hög"
    assert _scenario(t, "H-2").sarbarheter == ("S-1",)
    assert _scenario(t, "H-2").sarbarhetsniva == "hög"


def test_ersattning_kraver_att_ersattaren_omfattar_dimensionen(filer, ladda):
    filer["kataloger/sarbarheter.yaml"][0].update(hot=["H-3"], galler="bada")
    filer["kataloger/sarbarheter.yaml"][1].update(hot=["H-3"], ersatter=["S-1"], galler="penningtvatt")
    t = _bedom(ladda(filer), {"P-A": 0.5, "P-B": 0.5})
    assert _scenario(t, "H-3", "pt").sarbarheter == ("S-2",)
    assert _scenario(t, "H-3", "tf").sarbarheter == ("S-1",)
    assert _scenario(t, "H-3", "tf").sarbarhetsniva == "medel"


def test_okant_villkor_galler_preliminart_enligt_vid_okant(filer, ladda):
    filer["kataloger/sarbarheter.yaml"][0]["vid_okant"] = "preliminart_galler"
    t = _bedom(ladda(filer), okanda=("P-A",))
    assert _scenario(t, "H-1").sarbarheter == ("S-1",)
    assert t.status == "preliminär" and "P-A" in t.okanda_uppgifter


# --- Hotnivå och iakttagelse ------------------------------------------------


def test_iakttaget_hot_hojer_hotnivan_ett_steg(filer, ladda):
    t = _bedom(ladda(filer), {IAKTTAGELSE: ("H-1", "H-2")})
    assert (_scenario(t, "H-1").hotniva, _scenario(t, "H-1").iakttaget) == ("hög", True)
    assert (_scenario(t, "H-2").hotniva, _scenario(t, "H-2").iakttaget) == ("medel", True)
    assert (_scenario(t, "H-3").hotniva, _scenario(t, "H-3").iakttaget) == ("hög", False)
    assert t.status == "slutlig"


def test_iakttaget_hot_stannar_vid_hog_och_hojer_bada_dimensionerna(filer, ladda):
    t = _bedom(ladda(filer), {IAKTTAGELSE: ["H-3"]})
    assert _scenario(t, "H-3", "pt").hotniva == "hög" and _scenario(t, "H-3", "pt").iakttaget
    assert _scenario(t, "H-3", "tf").hotniva == "hög" and _scenario(t, "H-3", "tf").iakttaget
    _satt_hot(filer, "H-3", niva="medel")
    t = _bedom(ladda(filer), {IAKTTAGELSE: ["H-3"]})
    assert (_scenario(t, "H-3", "pt").hotniva, _scenario(t, "H-3", "tf").hotniva) == ("hög", "hög")


def test_obesvarad_iakttagelse_hojer_inte_och_gor_inte_preliminar(filer, ladda):
    utan = _bedom(ladda(filer))
    obesvarad = _bedom(ladda(filer), {IAKTTAGELSE: ("H-1",)}, okanda=(IAKTTAGELSE,))
    assert _scenario(obesvarad, "H-1").hotniva == "medel" and not _scenario(obesvarad, "H-1").iakttaget
    assert obesvarad.status == "slutlig"
    assert IAKTTAGELSE not in obesvarad.okanda_uppgifter
    assert obesvarad == utan


def test_ingen_iakttagelse_sanker_aldrig_hotnivan(filer, ladda):
    t = _bedom(ladda(filer), {IAKTTAGELSE: ()})
    assert [s.hotniva for s in t.scenarier] == ["medel", "låg", "hög", "hög", "medel"]


def test_iakttagelsefalt_som_saknas_i_regelbasen_ger_ingen_hojning(filer, ladda):
    filer["falt.yaml"] = [f for f in filer["falt.yaml"] if f["id"] != IAKTTAGELSE]
    t = _bedom(ladda(filer))
    assert _scenario(t, "H-1").hotniva == "medel"
    assert t.status == "slutlig"


@pytest.mark.parametrize("varde", ["H-1", ("H-OKANT",), 3, None])
def test_ogiltigt_iakttagelsevarde_ger_ingen_hojning_och_inget_fel(filer, ladda, varde):
    t = _bedom(ladda(filer), {IAKTTAGELSE: varde})
    assert _scenario(t, "H-1").hotniva == "medel" and not _scenario(t, "H-1").iakttaget
    assert t.status == "slutlig"


def test_iakttagelse_som_motorn_markt_okand_hojer_inte(filer, ladda):
    from riskanalys.bedomning.scenarier import iakttagelsefalt, iakttagna_hot
    from riskanalys.regelverk.villkor import Faltvarde, Kunskap

    tjanst = ladda(filer).tjanster["T-1"]
    assert iakttagelsefalt(tjanst) == IAKTTAGELSE
    varden = {IAKTTAGELSE: Faltvarde(Kunskap.KAND, ("H-1", "H-OKANT"))}
    assert iakttagna_hot(tjanst, varden, frozenset()) == {"H-1"}
    assert iakttagna_hot(tjanst, varden, frozenset({IAKTTAGELSE})) == frozenset()
    assert iakttagna_hot(tjanst, {IAKTTAGELSE: Faltvarde(Kunskap.EJ_TILLAMPLIG)}, frozenset()) == frozenset()


def test_hot_utan_niva_i_scenariometoden_ger_begripligt_fel(filer, ladda):
    _satt_hot(filer, "H-2", niva=None)
    filer["kataloger/hot.yaml"] = [{k: v for k, v in h.items() if v is not None} for h in filer["kataloger/hot.yaml"]]
    with pytest.raises(RiskanalysFel, match="H-2: hotet saknar hotnivå"):
        _bedom(ladda(filer))


def test_tillampad_sarbarhet_utan_hotkoppling_ger_begripligt_fel(filer, ladda):
    del filer["kataloger/sarbarheter.yaml"][0]["hot"]
    rb = ladda(filer)
    _bedom(rb)  # S-1 tillämpas inte och sänker därför inget
    with pytest.raises(RiskanalysFel, match="S-1: sårbarheten saknar koppling till hot"):
        _bedom(rb, {"P-A": 0.5})


# --- Kontroller -------------------------------------------------------------


def test_riktad_kontroll_med_belagd_effekt_sanker_bara_sitt_hot(filer, ladda):
    t = _bedom(ladda(filer), _kontrollvarden("P-C1"))
    h1 = _scenario(t, "H-1")
    assert (h1.risk, h1.kvarstaende, h1.tackande_kontroller) == ("måttlig", "låg", ("C-1",))
    assert "BT-KVAR-03" in h1.regelspar
    h3 = _scenario(t, "H-3")
    assert (h3.risk, h3.kvarstaende, h3.tackande_kontroller) == ("hög", "hög", ())
    assert "BT-KVAR-01" in h3.regelspar
    assert t.kvarstaende == "hög"
    assert {"BT-KVAR-03", "BT-KVAR-01"} <= set(t.regelspar)


def test_kontroll_med_belagd_effekt_utan_riktning_sanker_inte(filer, ladda):
    t = _bedom(ladda(filer), _kontrollvarden("P-C2"))
    assert next(k for k in t.kontroller if k.id == "C-2").effekt_belagd is True
    assert all(s.kvarstaende == s.risk and s.tackande_kontroller == () for s in t.scenarier if s.dimension == "pt")
    assert "BT-KVAR-03" not in t.regelspar


def test_riktad_kontroll_med_obedomd_effekt_sanker_inte(filer, ladda):
    t = _bedom(ladda(filer), _kontrollvarden("P-C1", eff="ej_bedömd"))
    c1 = next(k for k in t.kontroller if k.id == "C-1")
    assert c1.fungerar_och_ar_belagd is False and c1.effekt_belagd is False
    assert _scenario(t, "H-1").kvarstaende == "måttlig"
    assert _scenario(t, "H-1").tackande_kontroller == ()


def test_riktad_kontroll_utan_effektuppgift_sanker_inte(filer, ladda):
    """Utan effektfält blir kontrollen fungerande enligt metod 1, men scenariosänkning kräver belagd effekt."""
    kontroll = filer["kataloger/kontroller.yaml"][0]
    del kontroll["effekt_falt"], kontroll["utfall_falt"]
    t = _bedom(ladda(filer), _kontrollvarden("P-C1"))
    c1 = next(k for k in t.kontroller if k.id == "C-1")
    assert c1.fungerar_och_ar_belagd is True and c1.effekt_belagd is None
    assert _scenario(t, "H-1").kvarstaende == "måttlig"
    assert _scenario(t, "H-1").tackande_kontroller == ()


def test_riktad_kontroll_utan_belagt_genomforande_sanker_inte(filer, ladda):
    t = _bedom(ladda(filer), _kontrollvarden("P-C1", gen="ej_belagt"))
    assert _scenario(t, "H-1").kvarstaende == "måttlig"


def test_sankning_ar_hogst_ett_steg_aven_med_tva_kontroller(filer, ladda):
    filer["kataloger/kontroller.yaml"][1] = _kontroll("C-2", "P-C2", ["H-1"])
    _satt_hot(filer, "H-1", niva="hög")
    t = _bedom(ladda(filer), {**_kontrollvarden("P-C1"), **_kontrollvarden("P-C2")})
    h1 = _scenario(t, "H-1")
    assert (h1.risk, h1.kvarstaende, h1.tackande_kontroller) == ("hög", "måttlig", ("C-1", "C-2"))


def test_sankning_har_golvet_lag(filer, ladda):
    _satt_hot(filer, "H-1", niva="låg")
    filer["kataloger/tjanster.yaml"][0].update(grund_sannolikhet="låg", grund_konsekvens="begränsad")
    t = _bedom(ladda(filer), _kontrollvarden("P-C1"))
    h1 = _scenario(t, "H-1")
    assert (h1.risk, h1.kvarstaende, h1.tackande_kontroller) == ("låg", "låg", ("C-1",))


def test_tf_scenarier_far_ingen_kvarstaende_risk(filer, ladda):
    filer["kataloger/kontroller.yaml"][0] = _kontroll("C-1", "P-C1", ["H-3"])
    t = _bedom(ladda(filer), _kontrollvarden("P-C1"))
    assert _scenario(t, "H-3", "pt").kvarstaende == "måttlig"
    assert _scenario(t, "H-3", "tf").kvarstaende is None
    assert _scenario(t, "H-3", "tf").tackande_kontroller == ()
    assert t.kvarstaende == "måttlig"


# --- Aggregering ------------------------------------------------------------


def test_avgorande_ar_alla_scenarier_pa_dimensionens_maxrisk(filer, ladda):
    t = _bedom(ladda(filer))
    assert [(s.hot, s.dimension) for s in t.scenarier if s.avgorande] == [("H-3", "pt"), ("H-3", "tf")]


def test_lika_maxscenarier_markeras_alla_och_hogst_sannolikhet_valjs(filer, ladda):
    _satt_hot(filer, "H-3", niva="låg")
    filer["kataloger/tjanster.yaml"][0]["hot"] = ["H-2", "H-1", "H-3", "H-TF-1"]
    t = _bedom(ladda(filer))
    pt = [s for s in t.scenarier if s.dimension == "pt"]
    assert [(s.hot, s.sannolikhet, s.risk) for s in pt] == [
        ("H-2", "låg", "måttlig"), ("H-1", "medel", "måttlig"), ("H-3", "låg", "måttlig")]
    assert all(s.avgorande for s in pt)
    assert (t.inneboende.sannolikhet, t.inneboende.risk) == ("medel", "måttlig")
    tf = [s for s in t.scenarier if s.dimension == "tf"]
    assert [(s.hot, s.risk, s.avgorande) for s in tf] == [("H-3", "måttlig", True), ("H-TF-1", "måttlig", True)]


def test_lika_risk_och_sannolikhet_valjer_forsta_i_katalogordning(filer, ladda):
    from riskanalys.bedomning.scenarier import sammanfatta_scenarier

    _satt_hot(filer, "H-1", niva="hög")
    t = _bedom(ladda(filer))
    assert [s.hot for s in t.scenarier if s.dimension == "pt" and s.avgorande] == ["H-1", "H-3"]
    andrad = (t.scenarier[0].model_copy(update={"konsekvens": "allvarlig"}), *t.scenarier[1:])
    pt, _, _ = sammanfatta_scenarier(andrad)
    assert pt.konsekvens == "allvarlig"


def test_sammanfattning_utan_scenarier_ger_inga_nivaer():
    from riskanalys.bedomning.scenarier import sammanfatta_scenarier

    assert sammanfatta_scenarier(()) == (None, None, None)


def test_regelspar_ar_scenariometodens_regler_och_anvanda_matrisrader(filer, ladda):
    rb = ladda(filer)
    t = _bedom(rb)
    assert t.regelspar[:2] == ("BT-HOT-01", "BT-SARB-01")
    assert t.regelspar[-1] == "BT-TJ-01"
    anvanda = {SANN_ID[(s.hotniva, s.sarbarhetsniva)] for s in t.scenarier}
    assert anvanda <= set(t.regelspar)
    assert not {r.id for r in rb.metod.scenario.sannolikhetsmatris} - anvanda & set(t.regelspar)
    assert "BT-SANN-01" not in t.regelspar
    assert len(t.regelspar) == len(set(t.regelspar))
    assert set(t.regelspar) <= rb.alla_id()
    for s in t.scenarier:
        assert set(s.regelspar) <= set(t.regelspar)


def test_tjanst_som_inte_erbjuds_far_inga_scenarier(filer, ladda):
    t = _bedom(ladda(filer), {"P-TJ.t1_erbjuds": False})
    assert t.erbjuds is False and t.scenarier == () and t.inneboende is None
    assert "scenarier" not in t.model_dump(mode="json")


def test_scenarier_serialiseras_och_lases_tillbaka(filer, ladda):
    t = _bedom(ladda(filer), _kontrollvarden("P-C1"))
    data = t.model_dump_json()
    assert '"scenarier"' in data
    assert Tjanstbedomning.model_validate_json(data) == t
    assert Tjanstbedomning.model_validate_json(data).model_dump_json() == data


# --- Äldre regelbaser och sparade bedömningar -------------------------------


def _summa(bedomning: Bedomning) -> str:
    return hashlib.sha256(bedomning.model_dump_json().encode()).hexdigest()


def _v0_bedomning(profil_fabrik, extra: dict, okanda=()) -> Bedomning:
    rb = ladda_regelbas(REPO_REGELBAS)
    urval = valj(rb, "RP-RED-VG", date(2026, 11, 1), "Västra Götaland")
    return bedom(rb, urval, profil_fabrik(rb, {**REAL_VARDEN, **extra}, okanda=okanda))


@pytest.mark.parametrize("fall", list(V0_FALL))
def test_regelbas_v0_ger_byteidentisk_bedomning(profil_fabrik, fall):
    bedomning = _v0_bedomning(profil_fabrik, V0_FALL[fall])
    assert _summa(bedomning) == FORE_SCENARIO[fall]
    assert all(t.scenarier == () for t in bedomning.tjanster)
    assert '"scenarier"' not in bedomning.model_dump_json()


def test_regelbas_v0_med_okand_uppgift_ger_byteidentisk_bedomning(profil_fabrik):
    bedomning = _v0_bedomning(profil_fabrik, {}, okanda=("P-KUND.andel_riskbransch",))
    assert _summa(bedomning) == FORE_SCENARIO["v0_okand"]


def test_repots_regelbas_utan_scenariometod_ger_byteidentisk_bedomning():
    from riskanalys.profil.hantering import skapa_profil
    from tester.fixturer.m2 import komplett_profil

    rb = ladda_regelbas()
    assert rb.metod.scenario is None
    byra = Byra(id="syntetisk", regelpaket="RP-RED-VG", datum=date(2026, 10, 10), lan="Västra Götaland")
    profil = komplett_profil(rb, skapa_profil(rb, byra))
    bedomning = bedom(rb, valj(rb, byra.regelpaket, byra.datum, byra.lan), profil)
    assert _summa(bedomning) == FORE_SCENARIO["repo_komplett"]


def test_sparad_aldre_bedomning_utan_scenarier_lases_och_serialiseras_byteidentiskt(profil_fabrik):
    sparad = _v0_bedomning(profil_fabrik, V0_FALL["v0_belagd"]).model_dump_json()
    assert '"scenarier"' not in sparad
    last = Bedomning.model_validate_json(sparad)
    assert all(t.scenarier == () for t in last.tjanster)
    assert last.model_dump_json() == sparad
    assert hashlib.sha256(sparad.encode()).hexdigest() == FORE_SCENARIO["v0_belagd"]
