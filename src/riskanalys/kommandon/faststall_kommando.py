"""riskanalys faststall och verifiera"""

import argparse
from typing import Any

from riskanalys.faststallelse.faststall import faststall, verifiera_version, versionshistorik
from riskanalys.faststallelse.modeller import Beslut
from riskanalys.kommandon import datumargument, ladda_giltig_regelbas, regelbasargument
from riskanalys.lagring.datamapp import befintlig_byramapp


def lagg_till(underparsers: Any) -> None:
    fastst = underparsers.add_parser("faststall", help="Fastställ den senaste granskade versionen och lås paketet.")
    fastst.add_argument("byra")
    fastst.add_argument("--organ", required=True, help='Organet som beslutat, till exempel "styrelsen".')
    fastst.add_argument("--datum", required=True, type=datumargument, help="Beslutsdatum, ÅÅÅÅ-MM-DD.")
    fastst.add_argument("--namn", required=True, help="Namn på den som undertecknar beslutet.")
    fastst.add_argument("--roll", default="FfR", help="Rollen hos den som undertecknar. Standard är FfR.")
    regelbasargument(fastst)
    fastst.set_defaults(kor=kor_faststall)

    verifiering = underparsers.add_parser("verifiera", help="Kontrollera ett fastställt paket mot dess manifest.")
    verifiering.add_argument("byra")
    verifiering.add_argument("version", type=int, help="Versionsnummer, till exempel 1.")
    verifiering.set_defaults(kor=kor_verifiera)


def kor_faststall(args: argparse.Namespace) -> int:
    byramapp = befintlig_byramapp(args.byra)
    regelbas = ladda_giltig_regelbas(args.regelbas)
    beslut = Beslut(organ=args.organ, datum=args.datum, namn=args.namn, roll=args.roll)
    mapp = faststall(byramapp, args.regelbas, regelbas, beslut)
    version = mapp.name.removeprefix("v")
    print(f"{mapp.name} är fastställd av {beslut.organ} {beslut.datum.isoformat()} och låst i {mapp}.")
    print(f"Kontrollera paketet när som helst med 'riskanalys verifiera {args.byra} {version}'.")
    print(f"Nästa genomgång senast {versionshistorik(byramapp).nasta_genomgang()}.")
    return 0


def kor_verifiera(args: argparse.Namespace) -> int:
    fel = verifiera_version(befintlig_byramapp(args.byra), args.version)
    if fel:
        print(f"Version {args.version} stämmer inte med manifestet:")
        for rad in fel:
            print(f"- {rad}")
        print("Återställ versionen från säkerhetskopian och kör 'riskanalys verifiera' igen.")
        return 2
    print(f"Version {args.version} stämmer med manifestet.")
    return 0
