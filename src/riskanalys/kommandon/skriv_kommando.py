"""riskanalys skriv"""

import argparse
import os
from pathlib import Path
from typing import Any

from riskanalys.dokument.claude import STANDARDEFFORT, STANDARDMODELL, ClaudeLeverantor
from riskanalys.dokument.leverantor import LeverantorFel, Textleverantor, ladda_testleverantor
from riskanalys.dokument.skrivning import kor_skrivning, las_skrivresultat
from riskanalys.kommandon import ladda_giltig_regelbas, regelbasargument
from riskanalys.lagring.datamapp import befintlig_byramapp


def lagg_till(underparsers: Any) -> None:
    parser = underparsers.add_parser("skriv", help="Låt AI skriva riskavsnitten utifrån den senaste bedömningen.")
    parser.add_argument("byra")
    parser.add_argument("--leverantor", choices=["claude", "test"], default="claude")
    parser.add_argument("--testsvar", type=Path, help="JSON-fil med förberedda svar. Krävs med --leverantor test.")
    parser.add_argument("--modell", default=STANDARDMODELL, help=f"Standard är {STANDARDMODELL}.")
    parser.add_argument("--effort", default=STANDARDEFFORT, help=f"Standard är {STANDARDEFFORT}.")
    regelbasargument(parser)
    parser.set_defaults(kor=kor_skriv)


def valj_leverantor(args: argparse.Namespace) -> Textleverantor:
    if args.leverantor == "test":
        if args.testsvar is None:
            raise LeverantorFel("Ange en fil med förberedda svar med --testsvar.")
        return ladda_testleverantor(args.testsvar)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise LeverantorFel(
            "Sätt miljövariabeln ANTHROPIC_API_KEY för att använda Claude, eller använd --leverantor test."
        )
    return ClaudeLeverantor(modell=args.modell, effort=args.effort)


def kor_skriv(args: argparse.Namespace) -> int:
    byramapp = befintlig_byramapp(args.byra)
    regelbas = ladda_giltig_regelbas(args.regelbas)
    mapp = kor_skrivning(byramapp, regelbas, valj_leverantor(args))
    resultat = las_skrivresultat(mapp)
    for post in resultat:
        status = "godkänt" if post.godkant_utkast else "underkänt"
        print(f"{post.underlag.avsnitt} {post.underlag.rubrik}: {status} efter {len(post.forsok)} försök.")
        if post.godkant_utkast is None:
            for rad in post.forsok[-1].fel:
                print(f"  - {rad}")
    print(f"Sparad i {mapp}.")
    if all(post.godkant_utkast for post in resultat):
        print(f"Nästa steg: registrera utvärderingen med 'riskanalys utvardera {args.byra}' om det inte är gjort.")
        print(f"Granska sedan med 'riskanalys granska {args.byra}'.")
        return 0
    print("Minst ett avsnitt underkändes. Kör 'riskanalys skriv' igen eller rätta underlaget.")
    return 2
