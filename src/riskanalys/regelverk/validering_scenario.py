"""Kontrollerar scenariometodens katalogkopplingar (spec 2026-10-18, Datamodell och Preciseringar)."""

from collections import Counter
from itertools import product

from riskanalys.regelverk.modeller import Kontroll, Regelbas, Riktning, Sarbarhet, Tjanst, hot_dimensioner

NIVAER = ("låg", "medel", "hög")
MINSTA_HOT_FOR_SMAL_RIKTNING = 3


def scenariofel(rb: Regelbas) -> list[str]:
    """Hänvisningar prövas alltid; fullständighet krävs bara när metod.scenario finns."""
    fel = [*_sarbarhetshot(rb), *_riktningar(rb)]
    if rb.metod.scenario is None:
        return [*fel, *_negativa_effekter(rb)]
    return [*fel, *_hotnivaer(rb), *_sarbarheter_utan_hot(rb), *_sannolikhetsmatris(rb),
            *tjanstkopplingsfel(rb), *_scenarioregler(rb)]


def verksam_hotkoppling(rb: Regelbas, tjanst: Tjanst, sarbarhet: Sarbarhet) -> bool:
    """Minst ett av tjänstens scenarier kan ta emot sårbarhetens effekt."""
    dimensioner = {"pt", "tf"} if sarbarhet.galler == "bada" else {
        "pt" if sarbarhet.galler == "penningtvatt" else "tf"}
    return any(h in rb.hot and h in tjanst.hot and dimensioner.intersection(hot_dimensioner(rb.hot[h]))
               for h in sarbarhet.hot)


def tjanstkopplingsfel(rb: Regelbas, tjanst: Tjanst | None = None) -> list[str]:
    """Samma tjänstgräns används vid validering och före en direkt scenarioberäkning."""
    fel = []
    for t in (tjanst,) if tjanst else rb.tjanster.values():
        for dimension in ("pt", "tf"):
            if not any(h in rb.hot and dimension in hot_dimensioner(rb.hot[h]) for h in t.hot):
                fel.append(f"{t.id}: tjänsten saknar {dimension.upper()}-scenario. Ange ett relevant hot "
                           "med denna dimension i kataloger/tjanster.yaml och validera regelbasen.")
        for id in t.sarbarheter:
            s = rb.sarbarheter.get(id)
            if s and s.hot and not verksam_hotkoppling(rb, t, s):
                fel.append(f"{t.id}, {s.id}: sårbarheten saknar verksam hot-/dimensionskoppling i tjänsten. "
                           "Motivera en relevant koppling eller avgränsa tjänstens sårbarheter uttryckligen.")
    return fel


def _scenarioregler(rb: Regelbas) -> list[str]:
    fel = []
    for regel in rb.metod.scenario.regler():
        if regel.grund != "metodval":
            fel.append(f"{regel.id}: numerisk riskpåverkan är metodval, inte rättsligt ska-krav.")
        if not regel.kallor:
            fel.append(f"{regel.id}: ange källor för scenariometodens regel i kallor.")
    for s in rb.sarbarheter.values():
        if s.effekt.sannolikhet < 0 and s.vid_okant != "preliminart_galler_ej":
            fel.append(f"{s.id}: en negativ effekt kräver vid_okant: preliminart_galler_ej. "
                       "Ett okänt svar får aldrig sänka risken.")
        if s.omrade not in ("tj", "verk"):
            fel += [f"{s.id}: {h} får bara kopplas till sårbarheter i område tj eller verk."
                    for h in s.hot if h.startswith("H-TJ-")]
    fel += [f"{h.id}: hotnivån är ett ogranskat metodval, inte ett rättsligt ska-krav."
            for h in rb.hot.values() if h.niva is not None and h.grund != "metodval"]
    fel += [f"{k.id}, riktning mot {r.tjanst}: kontrollmålet är ett metodval, inte ett rättsligt ska-krav."
            for k in rb.kontroller.values() for r in k.riktar_sig_mot if r.grund != "metodval"]
    return fel


def _saknas(plats: str, referenser, finns, slag: str) -> list[str]:
    return [f"{plats}: hänvisar till {slag}{ref} som inte finns." for ref in referenser if ref not in finns]


def _sarbarhetshot(rb: Regelbas) -> list[str]:
    return [fel for s in rb.sarbarheter.values() for fel in _saknas(s.id, s.hot, rb.hot, "hotet ")]


def _riktningar(rb: Regelbas) -> list[str]:
    fel: list[str] = []
    for kontroll in rb.kontroller.values():
        for riktning in kontroll.riktar_sig_mot:
            fel += _riktning(rb, kontroll, riktning)
        fel += _for_breda_riktningar(rb, kontroll)
    return fel


def _riktning(rb: Regelbas, kontroll: Kontroll, riktning: Riktning) -> list[str]:
    plats = f"{kontroll.id}, riktning mot {riktning.tjanst}"
    fel = _saknas(plats, riktning.hot, rb.hot, "hotet ") + _saknas(plats, riktning.kallor, rb.kallor, "källan ")
    tjanst = rb.tjanster.get(riktning.tjanst)
    if tjanst is None:
        return [f"{plats}: tjänsten finns inte. Ange en tjänst ur kataloger/tjanster.yaml.", *fel]
    if kontroll.id not in tjanst.kontroller:
        fel.append(f"{plats}: tjänsten har inte kontrollen {kontroll.id}. "
                   f"Lägg till kontrollen i tjänsten eller ta bort riktningen.")
    fel += _saknas(plats, [h for h in riktning.hot if h in rb.hot], tjanst.hot, "hotet i tjänsten ")
    return fel


def _for_breda_riktningar(rb: Regelbas, kontroll: Kontroll) -> list[str]:
    """En kontroll som tillsammans riktar sig mot alla hot i en tjänst med minst tre hot godtas inte."""
    fel = []
    tjanster = dict.fromkeys(r.tjanst for r in kontroll.riktar_sig_mot)
    for tjanst_id in tjanster:
        tjanst = rb.tjanster.get(tjanst_id)
        if tjanst is None or len(tjanst.hot) < MINSTA_HOT_FOR_SMAL_RIKTNING:
            continue
        omfattade = {h for r in kontroll.riktar_sig_mot if r.tjanst == tjanst_id for h in r.hot}
        if set(tjanst.hot) <= omfattade:
            fel.append(f"{kontroll.id}, riktning mot {tjanst_id}: kontrollen riktar sig mot samtliga "
                       f"{len(tjanst.hot)} hot i tjänsten. Smalna av till de hot som källan stöder "
                       f"att kontrollen är utformad mot.")
    return fel


def _negativa_effekter(rb: Regelbas) -> list[str]:
    """Den äldre motorn summerar effekter per tjänst; en negativ effekt skulle sänka nivån tyst."""
    return [
        f"{s.id}: Negativ effekt kräver scenariometoden; ange en positiv effekt (1 eller 2) i "
        f"kataloger/sarbarheter.yaml eller lägg till scenario i beslutstabeller/metod.yaml."
        for s in rb.sarbarheter.values()
        if s.effekt.sannolikhet < 0
    ]


def _hotnivaer(rb: Regelbas) -> list[str]:
    i_tjanster = dict.fromkeys(h for t in rb.tjanster.values() for h in t.hot if h in rb.hot)
    return [
        f"{hot_id}: hotet saknar hotnivå. Ange niva (låg, medel eller hög) med källa och nivamotivering "
        f"i kataloger/hot.yaml."
        for hot_id in i_tjanster
        if rb.hot[hot_id].niva is None
    ]


def _sarbarheter_utan_hot(rb: Regelbas) -> list[str]:
    return [
        f"{s.id}: sårbarheten saknar koppling till hot. Ange de hot den möjliggör i hot, "
        f"annars kan risken sänkas tyst."
        for s in rb.sarbarheter.values()
        if not s.hot
    ]


def _sannolikhetsmatris(rb: Regelbas) -> list[str]:
    antal = Counter((rad.hot, rad.sarbarhet) for rad in rb.metod.scenario.sannolikhetsmatris)
    return [
        f"Sannolikhetsmatrisen ska ha exakt en rad för hotnivå {hot} och sårbarhetsnivå {sarbarhet}, "
        f"har {antal[(hot, sarbarhet)]}. Rätta scenario.sannolikhetsmatris i beslutstabeller/metod.yaml."
        for hot, sarbarhet in product(NIVAER, NIVAER)
        if antal[(hot, sarbarhet)] != 1
    ]
