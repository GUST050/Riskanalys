"""Kommandoraden: riskanalys <kommando> (spec 12)."""

import argparse
import sys

from riskanalys.fel import RiskanalysFel
from riskanalys.kommandon import (
    bedom_kommando,
    drift_kommando,
    exportera_kommando,
    faststall_kommando,
    granska_kommando,
    profil_kommando,
    regelbas_kommando,
    sakgranska_kommando,
    skriv_kommando,
)

KOMMANDON = [
    regelbas_kommando,
    profil_kommando,
    drift_kommando,
    bedom_kommando,
    skriv_kommando,
    granska_kommando,
    exportera_kommando,
    sakgranska_kommando,
    faststall_kommando,
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="riskanalys",
        description="Verksamhetsanpassad dokumentation enligt penningtvättsregelverket.",
    )
    underparsers = parser.add_subparsers(dest="kommando", required=True, metavar="kommando")
    for kommando in KOMMANDON:
        kommando.lagg_till(underparsers)
    args = parser.parse_args(argv)
    try:
        return args.kor(args)
    except RiskanalysFel as fel:
        print(f"Fel: {fel}", file=sys.stderr)
        return 1
