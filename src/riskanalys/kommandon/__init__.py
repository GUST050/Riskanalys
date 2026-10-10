"""Underkommandon. Varje modul har lagg_till(underparsers) och kör-funktioner som returnerar en felkod."""

from datetime import date
import argparse
from pathlib import Path

from riskanalys.regelverk.laddning import STANDARD_REGELBAS, RegelbasFel, ladda_regelbas
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.validering import validera


def regelbasargument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--regelbas",
        type=Path,
        default=STANDARD_REGELBAS,
        help="Mapp med regelbasen. Standard är repots regelbas.",
    )


def ladda_giltig_regelbas(rot: Path) -> Regelbas:
    """Läser in regelbasen och vägrar om den har fel."""
    regelbas = ladda_regelbas(rot)
    fel = validera(regelbas)
    if fel:
        raise RegelbasFel(fel)
    return regelbas


def datumargument(text: str) -> date:
    """Argparse-typ för datum med svenskt felmeddelande."""
    try:
        return date.fromisoformat(text)
    except ValueError as undantag:
        raise argparse.ArgumentTypeError(
            f"{text!r} är inget datum. Skriv ÅÅÅÅ-MM-DD, till exempel 2026-11-01."
        ) from undantag
