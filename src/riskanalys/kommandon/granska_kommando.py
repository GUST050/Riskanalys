"""riskanalys granska"""

import argparse
from datetime import date
from typing import Any

from riskanalys.granskning.korning import kor_granskning, las_granskning
from riskanalys.kommandon import datumargument, ladda_giltig_regelbas, regelbasargument
from riskanalys.lagring.datamapp import befintlig_byramapp


def lagg_till(underparsers: Any) -> None:
    parser = underparsers.add_parser("granska", help="Bygg dokumentet och granska det maskinellt.")
    parser.add_argument("byra")
    parser.add_argument("--datum", type=datumargument, default=None, help="Granskningsdatum. Standard är i dag.")
    parser.add_argument("--rapportformat",choices=("v8","v9","v10"),default=None,help="Uttryckligt rapportformat utan nya AI-anrop.")
    regelbasargument(parser)
    parser.set_defaults(kor=kor_granska)


def kor_granska(args: argparse.Namespace) -> int:
    byramapp = befintlig_byramapp(args.byra)
    regelbas = ladda_giltig_regelbas(args.regelbas)
    mapp = kor_granskning(byramapp, regelbas, args.datum or date.today(),rapportformat=getattr(args,"rapportformat",None))
    dokument, fynd = las_granskning(mapp)
    print(f"Dokumentet har {len(dokument.avsnitt)} avsnitt. Fynd: {len(fynd)}.")
    for post in fynd:
        print(f"{post.id} [{post.allvar}] {post.beskrivning} Åtgärd: {post.atgard}")
    print(f"Sparad i {mapp}.")
    if any(post.allvar == "blockerande" for post in fynd):
        print("Det finns blockerande fynd. Åtgärda dem innan dokumentet kan fastställas.")
        return 2
    print(f"Nästa steg: 'riskanalys exportera {args.byra} --utkast' och 'riskanalys sakgranska {args.byra}'.")
    return 0
