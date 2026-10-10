"""riskanalys bedom"""

import argparse
from typing import Any

from riskanalys.bedomning.korning import kor_bedomning, las_bedomning
from riskanalys.bedomning.modeller import Tjanstbedomning
from riskanalys.kommandon import ladda_giltig_regelbas, regelbasargument
from riskanalys.lagring.datamapp import befintlig_byramapp
from riskanalys.regelverk.modeller import Regelbas


def lagg_till(underparsers: Any) -> None:
    parser = underparsers.add_parser("bedom", help="Kör riskmotorn på byråns profil.")
    parser.add_argument("byra")
    regelbasargument(parser)
    parser.set_defaults(kor=kor_bedom)


def beskriv_tjanstbedomning(regelbas: Regelbas, tjanst: Tjanstbedomning) -> str:
    namn = regelbas.tjanster[tjanst.tjanst].namn
    if tjanst.inneboende is None or tjanst.terrorfinansiering is None:
        return f"{tjanst.tjanst} {namn}: erbjuds inte."
    text = (
        f"{tjanst.tjanst} {namn}: inneboende risk {tjanst.inneboende.risk}, "
        f"terrorfinansiering {tjanst.terrorfinansiering.risk}, kvarstående risk {tjanst.kvarstaende}."
    )
    if tjanst.okanda_uppgifter:
        text += f" Preliminär. Okända uppgifter: {', '.join(tjanst.okanda_uppgifter)}."
    return text


def kor_bedom(args: argparse.Namespace) -> int:
    byramapp = befintlig_byramapp(args.byra)
    regelbas = ladda_giltig_regelbas(args.regelbas)
    mapp = kor_bedomning(byramapp, regelbas)
    bedomning = las_bedomning(mapp)
    for tjanst in bedomning.tjanster:
        print(beskriv_tjanstbedomning(regelbas, tjanst))
    if bedomning.status == "preliminär":
        print("Bedömningen är preliminär. Den kan inte fastställas förrän de okända uppgifterna är bekräftade.")
    print(f"Sparad i {mapp}.")
    print(f"Nästa steg: 'riskanalys skriv {args.byra}'.")
    return 0
