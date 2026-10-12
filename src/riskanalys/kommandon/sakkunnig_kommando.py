"""CLI för sakkunnigunderlag och separat import av regelpaket/facit."""

import argparse
from datetime import date
from pathlib import Path
from typing import Any

from riskanalys.fel import RiskanalysFel
from riskanalys.kommandon import regelbasargument
from riskanalys.lagring.yamlfil import las_yaml
from riskanalys.regelverk.facit import las_facitgranskning, tillampa_facitgranskning
from riskanalys.regelverk.laddning import ladda_regelbas
from riskanalys.regelverk.sakkunnig import exportera_sakkunnigunderlag, las_granskningsfil, tillampa_granskning


def lagg_till(under: Any) -> None:
    """Registrera separata export- och importkommandon."""
    parser = under.add_parser('granskningsunderlag', help='Exportera komplett underlag för sakkunnig utan AI.')
    regelbasargument(parser)
    parser.add_argument('--paket', required=True)
    parser.add_argument('--datum', type=date.fromisoformat, required=True)
    parser.add_argument('--ut', type=Path, required=True)
    parser.set_defaults(kor=kor_export)
    for namn, hjalp, kor in (
        ('importera-granskning', 'Importera ett granskat versionsbundet regelpaketsbeslut.', kor_import),
        ('importera-facitgranskning', 'Importera separat granskning av tillsynsfacitet.', kor_facitimport),
    ):
        parser = under.add_parser(namn, help=hjalp)
        regelbasargument(parser)
        parser.add_argument('fil', type=Path)
        parser.set_defaults(kor=kor)


def kor_export(args: argparse.Namespace) -> int:
    """Exportera till en ny lokal mapp."""
    print(exportera_sakkunnigunderlag(args.regelbas, args.paket, args.datum, args.ut))
    return 0


def kor_import(args: argparse.Namespace) -> int:
    """Importera regelpaketsbeslut med ett åtgärdbart fel vid saknat paket."""
    data = las_yaml(args.fil)
    if not isinstance(data, dict) or not isinstance(data.get('paket'), str):
        raise RiskanalysFel('Granskningsfilen saknar paket. Rätta mot mallen.')
    beslut = las_granskningsfil(args.fil, ladda_regelbas(args.regelbas), data['paket'])
    tillampa_granskning(args.regelbas, beslut)
    print('Granskningsbeslutet är importerat. Kör om bedömning och granskning.')
    return 0


def kor_facitimport(args: argparse.Namespace) -> int:
    """Importera facitbeslut utan att frigöra ett regelpaket."""
    beslut = las_facitgranskning(args.fil, ladda_regelbas(args.regelbas).facit)
    tillampa_facitgranskning(args.regelbas, beslut)
    print('Facitgranskningsbeslutet är importerat. Pröva beslut och version före facitutvärderingen.')
    return 0
