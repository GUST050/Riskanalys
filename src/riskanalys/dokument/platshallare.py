"""Platshållare i AI-text (spec 8.4.5). Koden ersätter talen; AI skriver aldrig fält-ID i löptext."""

import re

from riskanalys.dokument.rendering import ROLLER
from riskanalys.fel import RiskanalysFel

_TAL = re.compile(r"\{(tal|period):([^{}\s]+)\}")
_ROLL = re.compile(r"\{roll:(\w+)\}")
_KLAMMER = re.compile(r"\{[^{}]*\}")
_OPPEN = re.compile(r"\{(?:tal|period):[^}]*$|\{(?:tal|period):[^}]*\s")
_FALTID = re.compile(r"\b(?:P|S|H|C|T|BT|D|K)-[A-Z0-9][A-Za-z0-9]*(?:[._-][A-Za-z0-9]+)*\b")


def platshallarfel(nummer: int, text: str, referenser: list[str], numeriska: dict[str, str],
                  perioder: dict[str, str] | None = None) -> list[str]:
    fel = []
    if _OPPEN.search(text) or any(c in _KLAMMER.sub("", text) for c in "{}"):
        fel.append(f"Stycke {nummer} har en felskriven platshållare. Skriv {{tal:ID}} med ett ID från faktabladet.")
    for traff in _KLAMMER.finditer(text):
        hel = traff.group(0)
        tal = _TAL.fullmatch(hel)
        roll = _ROLL.fullmatch(hel)
        if roll and roll.group(1) in ROLLER:
            continue
        if not tal:
            fel.append(f"Stycke {nummer} innehåller en otillåten platshållare {hel}. Tillåtna är {{tal:ID}}, {{period:ID}} och {{roll:FfR}}.")
            continue
        id = tal.group(2)
        varden = numeriska if tal.group(1) == "tal" else (perioder or {})
        if id not in varden:
            fel.append(f"Stycke {nummer}: {hel} är okänt eller skyddat. Använd bara {tal.group(1)}-ID som finns i faktabladet.")
        elif id not in referenser:
            fel.append(f"Stycke {nummer}: {id} i {hel} saknas bland styckets referenser.")
    return fel


def faltid_fel(nummer: int, text: str) -> list[str]:
    utan = _KLAMMER.sub(" ", text)
    return [f"Stycke {nummer} innehåller ID:t {id} i löptexten. Lägg ID:n i referenser och skriv klartext."
            for id in dict.fromkeys(_FALTID.findall(utan))]


def ersatt_tal(text: str, numeriska: dict[str, str], perioder: dict[str, str] | None = None) -> str:
    perioder = perioder or {}
    if platshallarfel(1,text,list(numeriska.keys() | perioder.keys()),numeriska,perioder):
        raise RiskanalysFel("Otillåten eller olöst platshållare. Skriv om delen före sammanställning.")
    def ersatt(traff: re.Match[str]) -> str:
        varden = numeriska if traff.group(1) == "tal" else perioder
        if traff.group(2) not in varden:
            raise RiskanalysFel(f"Platshållaren {traff.group(0)} kan inte ersättas. Skriv om delen innan dokumentet sammanställs.")
        return varden[traff.group(2)]
    return _TAL.sub(ersatt, text)
