"""riskanalys skriv"""

import argparse
from pathlib import Path
from typing import Any

from riskanalys.dokument.delskrivning import Tjanstresultat, EFFORTSTEG
from riskanalys.konfiguration import Skrivkonfiguration, skapa_textleverantor, STANDARDEFFORT, STANDARDMODELL
from riskanalys.dokument.leverantor import Textleverantor
from riskanalys.dokument.skrivning import kor_skrivning, las_skrivresultat
from riskanalys.kommandon import ladda_giltig_regelbas, regelbasargument
from riskanalys.lagring.datamapp import befintlig_byramapp


def lagg_till(underparsers: Any) -> None:
    parser = underparsers.add_parser("skriv", help="Låt AI skriva riskavsnitten utifrån den senaste bedömningen.")
    parser.add_argument("byra")
    parser.add_argument("--leverantor", choices=["claude", "test"], default="claude")
    parser.add_argument("--testsvar", type=Path, help="JSON-fil med förberedda svar. Krävs med --leverantor test.")
    parser.add_argument("--modell", default=STANDARDMODELL, help=f"Standard är {STANDARDMODELL}.")
    parser.add_argument("--effort", choices=tuple(EFFORTSTEG), default=STANDARDEFFORT, help=f"Standard är {STANDARDEFFORT}.")
    regelbasargument(parser)
    parser.set_defaults(kor=kor_skriv)


def valj_leverantor(args: argparse.Namespace) -> Textleverantor:
    return skapa_textleverantor(Skrivkonfiguration(
        leverantor=args.leverantor, testsvar=getattr(args, 'testsvar', None),
        modell=args.modell, effort=args.effort))


def kor_skriv(args: argparse.Namespace) -> int:
    byramapp = befintlig_byramapp(args.byra)
    regelbas = ladda_giltig_regelbas(args.regelbas)
    mapp = kor_skrivning(byramapp, regelbas, valj_leverantor(args), effort=args.effort)
    resultat = las_skrivresultat(mapp)
    for post in resultat:
        if isinstance(post,Tjanstresultat):
            for d in post.delar:
                status = "godkänt" if d.godkant_svar else "mall, blockerar fastställelse"
                print(f"{post.avsnitt}/{d.del_id}: {status} efter {len(d.forsok)} försök.")
            from riskanalys.granskning.analys import mallfynd
            for fynd in mallfynd(post):
                print(f"  - {fynd['beskrivning']} {fynd['atgard']}")
            continue
        status = "godkänt" if post.godkant_utkast else "underkänt"
        print(f"{post.underlag.avsnitt} {post.underlag.rubrik}: {status} efter {len(post.forsok)} försök.")
        if post.godkant_utkast is None:
            for rad in post.forsok[-1].fel:
                print(f"  - {rad}")
    from riskanalys.dokument.matning import sammanfatta
    s = sammanfatta(resultat)
    print(f"Avsnitt/delar: {s.avsnitt}, godkända direkt: {s.godkanda_forsta_forsoket}, anrop: {s.anrop}, "
          f"token in/ut: {s.indata_token}/{s.utdata_token}, cache läs/skriv: {s.cache_lasning_token}/{s.cache_skrivning_token}.")
    print(f"Sparad i {mapp}.")
    if all(all(d.godkant_svar for d in post.delar) if isinstance(post,Tjanstresultat) else post.godkant_utkast for post in resultat):
        print(f"Nästa steg: registrera utvärderingen med 'riskanalys utvardera {args.byra}' om det inte är gjort.")
        print(f"Granska sedan med 'riskanalys granska {args.byra}'.")
        return 0
    print("Minst ett avsnitt underkändes. Kör 'riskanalys skriv' igen eller rätta underlaget.")
    return 2
