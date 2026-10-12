"""Frysta mallar och utfall. Inga kundärenden eller sändningskommandon."""
from typing import Literal
from riskanalys.regelverk.modeller import Kundmall, Kundrad, Strikt

__all__ = ["Kundmall", "Kundrad", "Kundutfall"]

class Kundutfall(Strikt):
    A: Literal["tillatet", "stopp", "undantag", "preliminart"]
    B: tuple[str, ...]
    C: Literal["låg", "normal", "hög", "preliminär"]
    D: Literal["rapportera", "undantag", "ingen_skalig_misstanke", "preliminart"]
    status: Literal["preliminär", "slutlig"]
    okanda_uppgifter: tuple[str, ...]
    regelspar: tuple[str, ...]
    forklaringar: tuple[str, ...]
