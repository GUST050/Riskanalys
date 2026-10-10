"""Typat villkorsformat för regelbasen (spec 6.3).

Formatet är medvetet litet: kombinatorerna alla, nagon och inte samt jämförelser
mellan ett registrerat fält och ett värde. Inga fria uttryck och ingen eval.
Utvärderingen har tre sanningsvärden: sant, falskt och okänt.
"""

from __future__ import annotations

import operator
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any

from riskanalys.fel import RiskanalysFel

ORDNADE_TYPER = frozenset({"heltal", "tal", "andel", "datum"})
OPERATORER = frozenset({"==", "!=", "<", "<=", ">", ">=", "i", "finns", "saknas"})
ORDNINGSOPERATORER = frozenset({"<", "<=", ">", ">="})
UTAN_VARDE = frozenset({"finns", "saknas"})
_JAMFOR = {
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}


class VillkorsFel(RiskanalysFel):
    """Ett villkor eller ett värde i regelbasen är felaktigt."""


class Sanning(Enum):
    SANT = "sant"
    FALSKT = "falskt"
    OKANT = "okänt"


class Kunskap(Enum):
    KAND = "känd"
    OKAND = "okänd"
    EJ_TILLAMPLIG = "ej_tillämplig"


@dataclass(frozen=True)
class Faltvarde:
    kunskap: Kunskap
    varde: Any = None


@dataclass(frozen=True)
class Faltdef:
    id: str
    typ: str
    val: tuple[str, ...] = ()


@dataclass(frozen=True)
class Jamforelse:
    falt: str
    op: str
    varde: Any = None


@dataclass(frozen=True)
class Alla:
    delar: tuple[Villkor, ...]


@dataclass(frozen=True)
class Nagon:
    delar: tuple[Villkor, ...]


@dataclass(frozen=True)
class Inte:
    inre: Villkor


Villkor = Jamforelse | Alla | Nagon | Inte


@dataclass(frozen=True)
class Utfall:
    sanning: Sanning
    okanda: frozenset[str] = frozenset()


def kontrollera_varde(definition: Faltdef, varde: Any) -> None:
    """Kontrollerar att ett värde passar fältets typ."""
    typ = definition.typ
    ar_tal = isinstance(varde, (int, float)) and not isinstance(varde, bool)
    if typ == "bool":
        ok = isinstance(varde, bool)
    elif typ == "heltal":
        ok = isinstance(varde, int) and not isinstance(varde, bool)
    elif typ == "tal":
        ok = ar_tal
    elif typ == "andel":
        ok = ar_tal and 0 <= varde <= 1
    elif typ == "text":
        ok = isinstance(varde, str)
    elif typ == "val":
        ok = isinstance(varde, str) and varde in definition.val
    elif typ == "datum":
        ok = isinstance(varde, date)
    else:
        raise VillkorsFel(f"Okänd typ {typ!r} för fältet {definition.id}.")
    if not ok:
        raise VillkorsFel(f"Värdet {varde!r} passar inte typen {typ} för fältet {definition.id}.")


def tolka_villkor(data: Any, falt: dict[str, Faltdef]) -> Villkor:
    """Tolkar ett villkor från YAML-data och kontrollerar fält, operatorer och typer."""
    if not isinstance(data, dict) or not data:
        raise VillkorsFel(f"Ett villkor måste vara en mappning, fick {data!r}.")
    nycklar = set(data)
    if nycklar in ({"alla"}, {"nagon"}):
        (nyckel,) = nycklar
        delar = data[nyckel]
        if not isinstance(delar, list):
            raise VillkorsFel(f"'{nyckel}' måste innehålla en lista.")
        tolkade = tuple(tolka_villkor(del_, falt) for del_ in delar)
        return Alla(tolkade) if nyckel == "alla" else Nagon(tolkade)
    if nycklar == {"inte"}:
        return Inte(tolka_villkor(data["inte"], falt))
    if {"falt", "op"} <= nycklar <= {"falt", "op", "varde"}:
        return _tolka_jamforelse(data, falt)
    raise VillkorsFel(f"Okänd villkorsform med nycklarna {sorted(nycklar)}.")


def _tolka_jamforelse(data: dict[str, Any], falt: dict[str, Faltdef]) -> Jamforelse:
    falt_id, op = data["falt"], data["op"]
    if falt_id not in falt:
        raise VillkorsFel(f"Okänt fält {falt_id!r}. Fältet måste finnas i fältregistret.")
    if op not in OPERATORER:
        raise VillkorsFel(f"Okänd operator {op!r} för fältet {falt_id}.")
    definition = falt[falt_id]
    if op in UTAN_VARDE:
        if "varde" in data:
            raise VillkorsFel(f"Operatorn {op} tar inget värde ({falt_id}).")
        return Jamforelse(falt_id, op)
    if "varde" not in data:
        raise VillkorsFel(f"Operatorn {op} kräver ett värde ({falt_id}).")
    if op in ORDNINGSOPERATORER and definition.typ not in ORDNADE_TYPER:
        raise VillkorsFel(f"Operatorn {op} kan inte användas på typen {definition.typ} ({falt_id}).")
    varde = data["varde"]
    if op == "i":
        if not isinstance(varde, list) or not varde:
            raise VillkorsFel(f"Operatorn i kräver en lista med minst ett värde ({falt_id}).")
        for del_ in varde:
            kontrollera_varde(definition, del_)
        return Jamforelse(falt_id, op, tuple(varde))
    kontrollera_varde(definition, varde)
    return Jamforelse(falt_id, op, varde)


def utvardera(villkor: Villkor, varden: dict[str, Faltvarde]) -> Utfall:
    """Utvärderar ett villkor med tre sanningsvärden."""
    if isinstance(villkor, Jamforelse):
        return _utvardera_jamforelse(villkor, varden)
    if isinstance(villkor, Inte):
        inre = utvardera(villkor.inre, varden)
        return Utfall(_inte(inre.sanning), inre.okanda)
    if isinstance(villkor, (Alla, Nagon)):
        utfall = [utvardera(del_, varden) for del_ in villkor.delar]
        sanningar = [u.sanning for u in utfall]
        okanda = frozenset().union(*(u.okanda for u in utfall))
        sanning = _alla(sanningar) if isinstance(villkor, Alla) else _nagon(sanningar)
        return Utfall(sanning, okanda)
    raise VillkorsFel(f"Okänt villkor {villkor!r}.")


def falt_i(villkor: Villkor) -> frozenset[str]:
    """Alla fält som ett villkor bygger på."""
    if isinstance(villkor, Jamforelse):
        return frozenset({villkor.falt})
    if isinstance(villkor, Inte):
        return falt_i(villkor.inre)
    return frozenset().union(*(falt_i(del_) for del_ in villkor.delar))


def _inte(sanning: Sanning) -> Sanning:
    return {Sanning.SANT: Sanning.FALSKT, Sanning.FALSKT: Sanning.SANT}.get(sanning, Sanning.OKANT)


def _alla(sanningar: list[Sanning]) -> Sanning:
    if Sanning.FALSKT in sanningar:
        return Sanning.FALSKT
    if Sanning.OKANT in sanningar:
        return Sanning.OKANT
    return Sanning.SANT


def _nagon(sanningar: list[Sanning]) -> Sanning:
    if Sanning.SANT in sanningar:
        return Sanning.SANT
    if Sanning.OKANT in sanningar:
        return Sanning.OKANT
    return Sanning.FALSKT


def _sanning(uppfyllt: bool) -> Sanning:
    return Sanning.SANT if uppfyllt else Sanning.FALSKT


def _utvardera_jamforelse(jamforelse: Jamforelse, varden: dict[str, Faltvarde]) -> Utfall:
    faltvarde = varden.get(jamforelse.falt, Faltvarde(Kunskap.OKAND))
    if faltvarde.kunskap is Kunskap.OKAND:
        return Utfall(Sanning.OKANT, frozenset({jamforelse.falt}))
    if faltvarde.kunskap is Kunskap.EJ_TILLAMPLIG:
        return Utfall(_sanning(jamforelse.op == "saknas"))
    varde = faltvarde.varde
    if jamforelse.op == "finns":
        return Utfall(_sanning(varde is not None))
    if jamforelse.op == "saknas":
        return Utfall(_sanning(varde is None))
    if varde is None:
        return Utfall(Sanning.FALSKT)
    if jamforelse.op == "i":
        return Utfall(_sanning(varde in jamforelse.varde))
    return Utfall(_sanning(_JAMFOR[jamforelse.op](varde, jamforelse.varde)))
