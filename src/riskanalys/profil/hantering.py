"""Skapa och ändra byråprofilen (spec 6.2 och 14)."""

import math
import re
from collections.abc import Callable
from datetime import date
from typing import Any

from riskanalys.fel import RiskanalysFel
from riskanalys.profil.modeller import Byra, Period, Profil, Uppgift
from riskanalys.regelverk.modeller import Falt, Regelbas
from riskanalys.regelverk.urval import Urval
from riskanalys.regelverk.villkor import Faltdef, VillkorsFel, falt_i, kontrollera_varde, tolka_villkor

SANT = frozenset({"ja", "sant", "true", "1"})
FALSKT = frozenset({"nej", "falskt", "false", "0"})
ANDEL_HJALP = "Andelen anges som 0–1 eller i procent, till exempel 0,3 eller 30 %."
_PROCENT = re.compile(r"^(\d+(?:[.,]\d+)?)\s*%$")
_HJALP = {
    "andel": ANDEL_HJALP,
    "bool": "Skriv ja eller nej.",
    "heltal": "Skriv ett tal.",
    "tal": "Skriv ett tal.",
    "datum": "Skriv datumet som ÅÅÅÅ-MM-DD.",
}


class ProfilFel(RiskanalysFel):
    """En uppgift i profilen kan inte sparas."""


def skapa_profil(regelbas: Regelbas, byra: Byra) -> Profil:
    """En ny profil där alla uppgifter saknas."""
    return Profil(byra=byra, uppgifter={falt_id: Uppgift() for falt_id in regelbas.falt})


def tolka_varde(falt: Falt, text: str) -> Any:
    """Tolkar ett värde som användaren skrivit, med svenska format."""
    try:
        varde = _TOLKARE[falt.typ](text.strip())
    except ValueError as undantag:
        raise ProfilFel(f"Värdet {text!r} passar inte fältet {falt.id}.{_hjalp(falt)}") from undantag
    try:
        kontrollera_varde(Faltdef(falt.id, falt.typ, falt.val), varde)
    except VillkorsFel as undantag:
        raise ProfilFel(f"{undantag}{_hjalp(falt)}") from undantag
    return varde


def visa_varde(falt: Falt, varde: Any) -> str:
    """Ett värde som text på svenska."""
    if falt.typ == "bool":
        return "ja" if varde else "nej"
    if falt.typ == "andel":
        return f"{round(varde * 100)} %"
    if isinstance(varde, date):
        return varde.isoformat()
    return str(varde)


def beskriv_uppgift(falt: Falt, uppgift: Uppgift) -> str:
    if uppgift.inaktuell:
        return f"{visa_varde(falt, uppgift.varde)} (inaktuell; tidigare källa: {uppgift.kalla}). Bekräfta antal och bas igen."
    if uppgift.status == "bekräftad":
        return f"{visa_varde(falt, uppgift.varde)} (bekräftad {uppgift.datum}, källa: {uppgift.kalla})"
    if uppgift.status == "ej_tillämplig":
        return f"ej tillämplig ({uppgift.motivering})"
    return uppgift.status


def bekrafta(
    profil: Profil,
    regelbas: Regelbas,
    falt_id: str,
    text: str,
    kalla: str | None,
    roll: str,
    datum: date,
    period: Period | None = None,
) -> Profil:
    """Returnerar en ny profil där uppgiften är bekräftad."""
    falt = _falt(regelbas, falt_id)
    if falt.antalfalt or falt.basfalt:
        raise ProfilFel(f"{falt_id} härleds. Bekräfta {falt.antalfalt} och {falt.basfalt}, inte andelen direkt.")
    if falt.periodkrav and period is None:
        raise ProfilFel(f"{falt_id} kräver --period-fran och --period-till.")
    if not kalla or not kalla.strip():
        raise ProfilFel("Ange varifrån uppgiften kommer med --kalla, till exempel --kalla \"Kundregistret 2026-09-30\".")
    uppgift = Uppgift(
        varde=tolka_varde(falt, text),
        status="bekräftad",
        kalla=kalla.strip(),
        datum=datum,
        bekraftad_av=f"roll:{roll}",
        period=period,
    )
    from riskanalys.profil.omfattning import harled_andelar
    return harled_andelar(_med(profil, falt.id, uppgift), regelbas, andrade_falt=frozenset({falt.id}))


def markera_ej_tillamplig(
    profil: Profil,
    regelbas: Regelbas,
    falt_id: str,
    motivering: str | None,
    roll: str,
    datum: date,
) -> Profil:
    """Returnerar en ny profil där uppgiften är markerad som ej tillämplig."""
    falt = _falt(regelbas, falt_id)
    if not motivering or not motivering.strip():
        raise ProfilFel("Ange varför uppgiften inte är tillämplig med --motivering.")
    uppgift = Uppgift(status="ej_tillämplig", motivering=motivering.strip(), datum=datum, bekraftad_av=f"roll:{roll}")
    return _med(profil, falt.id, uppgift)


def kritiska_falt(regelbas: Regelbas, urval: Urval, profil: Profil | None = None) -> frozenset[str]:
    """Uppgifter som riskbedömningen bygger på och som måste vara kända före fastställelse."""
    definitioner = regelbas.faltdefinitioner()
    tjanster = [regelbas.tjanster[tjanst_id] for tjanst_id in urval.tjanster]
    from riskanalys.profil.omfattning import aktivt
    uttryckliga = {falt.id for falt in regelbas.falt.values() if falt.kritisk and (profil is None or aktivt(falt, profil, regelbas))}
    tillamplighet = {
        falt_id for valt in urval.krav for falt_id in falt_i(tolka_villkor(valt.krav.galler_om, definitioner))
    }
    erbjuds = {tjanst.erbjuds_falt for tjanst in tjanster}
    if profil is not None:
        tjanster = [t for t in tjanster if not (profil.ar_bekraftad(t.erbjuds_falt) and profil.uppgifter[t.erbjuds_falt].varde is False)]
    kontroller = {
        falt_id
        for tjanst in tjanster
        for kontroll_id in tjanst.kontroller
        for falt_id in (
            regelbas.kontroller[kontroll_id].utformning_falt,
            regelbas.kontroller[kontroll_id].genomforande_falt,
        )
    }
    villkor = {
        falt_id
        for tjanst in tjanster
        for sarbarhet_id in tjanst.sarbarheter
        for falt_id in falt_i(tolka_villkor(regelbas.sarbarheter[sarbarhet_id].villkor, definitioner))
    }
    return frozenset(uttryckliga | tillamplighet | erbjuds | kontroller | villkor)


def kontrollera_profil(profil: Profil, regelbas: Regelbas) -> None:
    """Prövar varje bekräftat värde mot fältregistret innan det används.

    Ett handredigerat värde eller ett värde av en typ som regelbasen inte längre har får aldrig ändra bedömningen
    i tysthet. Värden i fält med personuppgifter skrivs inte ut.
    """
    definitioner = regelbas.faltdefinitioner()
    from riskanalys.profil.omfattning import omfattningsbrister
    fel = [*belaggsbrister(profil), *omfattningsbrister(profil, regelbas)]
    for falt_id, uppgift in profil.uppgifter.items():
        if uppgift.status != "bekräftad" or falt_id not in definitioner:
            continue
        try:
            kontrollera_varde(definitioner[falt_id], uppgift.varde)
        except VillkorsFel:
            varde = "ett värde" if regelbas.falt[falt_id].personuppgift else f"värdet {uppgift.varde!r}"
            fel.append(f"{falt_id} har {varde}, som inte passar typen {definitioner[falt_id].typ}.")
    if fel:
        raise ProfilFel(
            "Profilen har uppgifter som inte kan användas:\n"
            + "\n".join(f"- {rad}" for rad in fel)
            + "\nBekräfta uppgifterna igen med 'riskanalys bekrafta <byrå> <fält> <värde> --kalla <källa>', "
            "eller markera dem med --ej-tillampligt och --motivering."
        )


# Belägg som en status kräver (spec 6.2 och 10, villkor 1): fält i Uppgift och hur det benämns i meddelanden.
_BELAGG = {
    "bekräftad": (("kalla", "källa"), ("datum", "datum"), ("bekraftad_av", "uppgift om vem som bekräftat")),
    "ej_tillämplig": (("motivering", "motivering"), ("datum", "datum"), ("bekraftad_av", "uppgift om vem som bekräftat")),
}
_STATUSTEXT = {"bekräftad": "är bekräftad", "ej_tillämplig": "är markerad som ej tillämplig"}


def belaggsbrister(profil: Profil) -> tuple[str, ...]:
    """Uppgifter vars status saknar sina belägg, till exempel en bekräftelse utan källa i en handredigerad profil.

    En bekräftad uppgift kräver källa, datum och vem som bekräftat. En uppgift som inte är tillämplig kräver
    motivering, datum och vem som bekräftat.
    """
    brister = []
    for falt_id, uppgift in sorted(profil.uppgifter.items()):
        krav = _BELAGG.get(uppgift.status)
        if krav is None:
            continue
        saknade = [benamning for falt, benamning in krav if not _har_varde(getattr(uppgift, falt))]
        if saknade:
            brister.append(f"{falt_id} {_STATUSTEXT[uppgift.status]} utan {_uppraknad(saknade)}.")
    return tuple(brister)


def _har_varde(varde: Any) -> bool:
    return varde is not None and (not isinstance(varde, str) or bool(varde.strip()))


def _uppraknad(delar: list[str]) -> str:
    return delar[0] if len(delar) == 1 else f"{', '.join(delar[:-1])} och {delar[-1]}"


def saknade_kritiska(profil: Profil, regelbas: Regelbas, urval: Urval) -> tuple[str, ...]:
    """Kritiska uppgifter som varken är bekräftade eller ej tillämpliga."""
    from riskanalys.profil.omfattning import kompatibilitetsvy
    profil = kompatibilitetsvy(profil, regelbas)
    klara = {"bekräftad", "ej_tillämplig"}
    return tuple(
        sorted(
            falt_id
            for falt_id in kritiska_falt(regelbas, urval, profil)
            if profil.uppgifter.get(falt_id, Uppgift()).status not in klara or profil.uppgifter.get(falt_id, Uppgift()).inaktuell
        )
    )


def personnamn(profil: Profil, regelbas: Regelbas) -> tuple[str, ...]:
    """Bekräftade personuppgifter i textform. De får aldrig förekomma i AI-text."""
    return tuple(
        str(uppgift.varde)
        for falt_id, uppgift in profil.uppgifter.items()
        if falt_id in regelbas.falt
        and regelbas.falt[falt_id].personuppgift
        and uppgift.status == "bekräftad"
        and uppgift.varde
    )


def _falt(regelbas: Regelbas, falt_id: str) -> Falt:
    if falt_id not in regelbas.falt:
        raise ProfilFel(f"Fältet {falt_id} finns inte i regelbasen. Se alla fält med 'riskanalys profil'.")
    return regelbas.falt[falt_id]


def _med(profil: Profil, falt_id: str, uppgift: Uppgift) -> Profil:
    return profil.model_copy(update={"uppgifter": {**profil.uppgifter, falt_id: uppgift}})


def _hjalp(falt: Falt) -> str:
    if falt.typ == "val":
        return f" Välj ett av: {', '.join(falt.val)}."
    return f" {_HJALP[falt.typ]}" if falt.typ in _HJALP else ""


def _tal(text: str) -> float:
    varde = float(text.replace(" ", "").replace(",", "."))
    if not math.isfinite(varde):
        raise ValueError("inget ändligt tal")
    return varde


def _andel(text: str) -> float:
    if text == "1":
        raise ProfilFel("Ensam 1 är tvetydig. Skriv 1 % för en procent eller 1,0 för hundra procent.")
    procent = _PROCENT.match(text)
    if procent:
        return _tal(procent.group(1)) / 100
    varde = _tal(text)
    if varde > 1:
        raise ValueError("andel över 1 utan procenttecken")
    return varde


def _bool(text: str) -> bool:
    if text.lower() in SANT:
        return True
    if text.lower() in FALSKT:
        return False
    raise ValueError("inte ja eller nej")


def _heltal(text: str) -> int:
    return int(text.replace(" ", ""))


def _text(text: str) -> str:
    if not text:
        raise ValueError("tom text")
    return text


_TOLKARE: dict[str, Callable[[str], Any]] = {
    "bool": _bool,
    "heltal": _heltal,
    "tal": _tal,
    "andel": _andel,
    "text": _text,
    "val": _text,
    "datum": date.fromisoformat,
}
