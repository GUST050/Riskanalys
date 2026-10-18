"""Kontrollerar scenariometodens katalogkopplingar (spec 2026-10-18, Datamodell och Preciseringar)."""

from collections import Counter
from itertools import product

from riskanalys.regelverk.modeller import Kontroll, Regelbas, Riktning

NIVAER = ("låg", "medel", "hög")
MINSTA_HOT_FOR_SMAL_RIKTNING = 3


def scenariofel(rb: Regelbas) -> list[str]:
    """Hänvisningar prövas alltid; fullständighet krävs bara när metod.scenario finns."""
    fel = [*_sarbarhetshot(rb), *_riktningar(rb)]
    if rb.metod.scenario is None:
        return [*fel, *_negativa_effekter(rb)]
    return [*fel, *_hotnivaer(rb), *_sarbarheter_utan_hot(rb), *_sannolikhetsmatris(rb)]


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
