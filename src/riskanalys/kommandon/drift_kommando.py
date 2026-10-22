"""riskanalys utvardera"""

import argparse
from datetime import date
from typing import Any

from riskanalys.drift.historik import Handelse, registrera_handelse
from riskanalys.kommandon import datumargument
from riskanalys.lagring.datamapp import befintlig_byramapp


def lagg_till(underparsers: Any) -> None:
    parser = underparsers.add_parser("utvardera", help="Registrera en utvärdering av riskbedömningen.")
    parser.add_argument("byra")
    parser.add_argument("--beskrivning", required=True, help="Vad utvärderingen omfattade och vad den ledde till.")
    parser.add_argument("--datum", type=datumargument, default=None, help="Standard är dagens datum.")
    parser.add_argument('--plan', help='Bind en avgränsad förändringsutvärdering till detta plan-ID; årsfristen flyttas inte.')
    from riskanalys.kommandon import regelbasargument
    regelbasargument(parser)
    parser.set_defaults(kor=kor_utvardera)


def kor_utvardera(args: argparse.Namespace) -> int:
    mapp = befintlig_byramapp(args.byra)
    datum = args.datum or date.today()
    if getattr(args,'plan',None):
        from riskanalys.kommandon import ladda_giltig_regelbas
        from riskanalys.intag.tjanst import Intagstjanst
        from riskanalys.intag.utvardering import registrera_utvardering
        from riskanalys.profil.lagring import profilrevision
        t = Intagstjanst(args.byra,ladda_giltig_regelbas(args.regelbas))
        registrera_utvardering(t,datum,args.beskrivning,profilrevision(t.profil()),plan_id=args.plan)
        print('Förändringsutvärderingen är registrerad. Förnya analysen och sakpröva igen. Årsfristen är oförändrad.')
        return 0
    historik = registrera_handelse(mapp, Handelse(datum=datum, typ="utvärdering", beskrivning=args.beskrivning))
    print(f"Utvärdering registrerad {datum.isoformat()}. Nästa genomgång senast {historik.nasta_genomgang()}.")
    return 0
