"""riskanalys regelbas validera"""

import argparse
from typing import Any

from riskanalys.kommandon import ladda_giltig_regelbas, regelbasargument
from riskanalys.regelverk.laddning import ladda_regelbas


def lagg_till(underparsers: Any) -> None:
    parser = underparsers.add_parser("regelbas", help="Arbeta med regelbasen.")
    under = parser.add_subparsers(dest="regelbaskommando", required=True, metavar="underkommando")
    validera = under.add_parser("validera", help="Läs in regelbasen och kontrollera att den hänger ihop.")
    regelbasargument(validera)
    validera.set_defaults(kor=kor_validera)
    summor = under.add_parser("summor", help="Visa kontrollsummorna som en sakkunnig signerar.")
    regelbasargument(summor)
    summor.set_defaults(kor=kor_summor)


def kor_validera(args: argparse.Namespace) -> int:
    regelbas = ladda_giltig_regelbas(args.regelbas)
    print("Regelbasen är giltig.")
    print(f"Version: {regelbas.version}")
    print(f"Krav: {len(regelbas.krav)}")
    print(f"Tjänster: {len(regelbas.tjanster)}")
    for paket in regelbas.regelpaket.values():
        karta = paket.paragrafkarta
        hanterade = len(karta.rader) - len(karta.ohanterade())
        print(
            f"Paragrafkarta {paket.id}: {hanterade} av {len(karta.rader)} paragrafer hanterade, "
            f"sakkunnigstatus {karta.sakkunnig.status}."
        )
    print(f"Kontrollsumma: {regelbas.kontrollsumma}")
    return 0


def kor_summor(args: argparse.Namespace) -> int:
    """En sakkunnig som verifierat ett krav eller en karta skriver in summan i sakkunnig.kontrollsumma.

    Regelbasen läses utan validering, eftersom summorna behövs just när en tidigare verifiering slutat gälla.
    """
    regelbas = ladda_regelbas(args.regelbas)
    for krav in regelbas.krav.values():
        print(f"{krav.id} {regelbas.kravets_innehallssumma(krav.id)}")
    for paket in regelbas.regelpaket.values():
        print(f"{paket.id} paragrafkarta {regelbas.kartans_innehallssumma(paket.id)}")
    return 0
