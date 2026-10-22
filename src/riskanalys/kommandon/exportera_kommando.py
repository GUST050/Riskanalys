"""riskanalys exportera"""

import argparse
from datetime import date
from typing import Any

from riskanalys.dokument.export import UTKASTFIL, kor_export_utkast
from riskanalys.fel import RiskanalysFel
from riskanalys.kommandon import datumargument, regelbasargument, ladda_giltig_regelbas
from riskanalys.lagring.datamapp import befintlig_byramapp
from riskanalys.regelverk.laddning import STANDARD_REGELBAS


def lagg_till(underparsers: Any) -> None:
    parser = underparsers.add_parser("exportera", help="Skapa ett Word-dokument av den senaste granskningen.")
    parser.add_argument("byra")
    operation=parser.add_mutually_exclusive_group()
    operation.add_argument("--omfattningsunderlag",action="store_true",help="Separat ofullständigt omfattningsunderlag, inga risknivåer eller AI-anrop.")
    operation.add_argument("--utkast", action="store_true", help="Exportera som utkast med åtgärdslista.")
    parser.add_argument("--datum", type=datumargument, default=None, help="Datum i statusraden. Standard är i dag.")
    regelbasargument(parser)
    parser.set_defaults(kor=kor_exportera)


def kor_exportera(args: argparse.Namespace) -> int:
    if getattr(args,'omfattningsunderlag',False):
        from riskanalys.dokument.omfattningsutkast import exportera_omfattningsutkast
        fil=exportera_omfattningsutkast(befintlig_byramapp(args.byra),ladda_giltig_regelbas(args.regelbas))
        print('OFULLSTÄNDIGT omfattningsunderlag, får inte fastställas: '+str(fil))
        return 0
    if not args.utkast:
        raise RiskanalysFel("En fastställd version skapas med 'riskanalys faststall'. Använd --utkast för ett utkast.")
    regelbas = ladda_giltig_regelbas(args.regelbas) if args.regelbas != STANDARD_REGELBAS else None
    mapp = kor_export_utkast(befintlig_byramapp(args.byra), args.datum or date.today(), regelbas=regelbas)
    print(f"Utkastet är sparat i {mapp / UTKASTFIL}.")
    if (mapp/'underlagsbilaga-UTKAST.docx').is_file():
        print(f"Kompletterande underlagsbilaga: {mapp / 'underlagsbilaga-UTKAST.docx'}. Läs båda delarna tillsammans.")
    print("Varje sida är märkt UTKAST. Öppna fynd och oklarheter står i åtgärdslistan sist i dokumentet.")
    print(f"Nästa steg: sakgranska avsnitten med 'riskanalys sakgranska {args.byra}'.")
    return 0
