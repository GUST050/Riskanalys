"""riskanalys utvardera"""

import argparse
from datetime import date
from typing import Any

from riskanalys.drift.historik import Handelse, las_historik, spara_historik
from riskanalys.kommandon import datumargument
from riskanalys.lagring.datamapp import befintlig_byramapp


def lagg_till(underparsers: Any) -> None:
    parser = underparsers.add_parser("utvardera", help="Registrera en utvärdering av riskbedömningen.")
    parser.add_argument("byra")
    parser.add_argument("--beskrivning", required=True, help="Vad utvärderingen omfattade och vad den ledde till.")
    parser.add_argument("--datum", type=datumargument, default=None, help="Standard är dagens datum.")
    parser.set_defaults(kor=kor_utvardera)


def kor_utvardera(args: argparse.Namespace) -> int:
    mapp = befintlig_byramapp(args.byra)
    datum = args.datum or date.today()
    historik = las_historik(mapp).med(Handelse(datum=datum, typ="utvärdering", beskrivning=args.beskrivning))
    spara_historik(mapp, historik)
    print(f"Utvärdering registrerad {datum.isoformat()}. Nästa genomgång senast {historik.nasta_genomgang()}.")
    return 0
