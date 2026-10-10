"""riskanalys ny, bekrafta och profil"""

import argparse
from datetime import date
from typing import Any

from riskanalys.kommandon import datumargument, ladda_giltig_regelbas, regelbasargument
from riskanalys.lagring.datamapp import befintlig_byramapp, skapa_byramapp
from riskanalys.profil.hantering import (
    ProfilFel,
    bekrafta,
    beskriv_uppgift,
    kritiska_falt,
    markera_ej_tillamplig,
    saknade_kritiska,
    skapa_profil,
)
from riskanalys.profil.lagring import las_profil, spara_profil
from riskanalys.profil.modeller import Byra, Period, Uppgift
from riskanalys.regelverk.urval import beskriv_vantande, valj, vantande_andringar


def lagg_till(underparsers: Any) -> None:
    ny = underparsers.add_parser("ny", help="Skapa en ny byrå med tom profil.")
    ny.add_argument("byra", help="Byrå-ID, till exempel testbyra.")
    ny.add_argument("--regelpaket", required=True, help="Till exempel RP-RED-VG.")
    ny.add_argument("--lan", required=True, help='Länet där byrån har sitt säte, till exempel "Västra Götaland".')
    ny.add_argument("--datum", required=True, type=datumargument, help="Datum som regelverket väljs för.")
    regelbasargument(ny)
    ny.set_defaults(kor=kor_ny)

    bekraftelse = underparsers.add_parser("bekrafta", help="Bekräfta en uppgift i profilen.")
    bekraftelse.add_argument("byra")
    bekraftelse.add_argument("falt", help="Fältets ID, till exempel P-KUND.andel_riskbransch.")
    bekraftelse.add_argument("varde", nargs="?", help="Värdet, till exempel 30 %%, 0,3, ja eller finns.")
    bekraftelse.add_argument("--kalla", help="Varifrån uppgiften kommer.")
    bekraftelse.add_argument("--roll", default="FfR", help="Rollen som bekräftar. Standard är FfR.")
    bekraftelse.add_argument("--ej-tillampligt", action="store_true", help="Markera uppgiften som ej tillämplig.")
    bekraftelse.add_argument("--motivering", help="Krävs med --ej-tillampligt.")
    bekraftelse.add_argument("--datum", type=datumargument, default=None, help="Standard är dagens datum.")
    bekraftelse.add_argument("--period-fran", type=datumargument)
    bekraftelse.add_argument("--period-till", type=datumargument)
    regelbasargument(bekraftelse)
    bekraftelse.set_defaults(kor=kor_bekrafta)

    visning = underparsers.add_parser("profil", help="Visa byråns profil och vilka uppgifter som saknas.")
    visning.add_argument("byra")
    regelbasargument(visning)
    visning.set_defaults(kor=kor_profil)


def kor_ny(args: argparse.Namespace) -> int:
    regelbas = ladda_giltig_regelbas(args.regelbas)
    urval = valj(regelbas, args.regelpaket, args.datum, args.lan)
    mapp = skapa_byramapp(args.byra)
    byra = Byra(id=args.byra, regelpaket=args.regelpaket, datum=args.datum, lan=args.lan)
    spara_profil(mapp, skapa_profil(regelbas, byra))
    print(f"Byrån {args.byra} är skapad i {mapp}.")
    print(f"Regelpaket {urval.regelpaket.id} för {args.lan}: {len(urval.krav)} krav gäller {args.datum.isoformat()}.")
    for andring in vantande_andringar(regelbas, urval):
        print(f"Ändring som väntar: {beskriv_vantande(andring)}")
    print(f"Nästa steg: bekräfta uppgifterna. Se vilka som saknas med 'riskanalys profil {args.byra}'.")
    return 0


def kor_bekrafta(args: argparse.Namespace) -> int:
    mapp = befintlig_byramapp(args.byra)
    regelbas = ladda_giltig_regelbas(args.regelbas)
    profil = las_profil(mapp)
    datum = args.datum or date.today()
    if bool(args.period_fran) != bool(args.period_till):
        raise ProfilFel("Ange både --period-fran och --period-till.")
    if args.period_fran and args.period_fran > args.period_till:
        raise ProfilFel("Periodens från-datum får inte vara efter till-datum.")
    period = Period(fran=args.period_fran, till=args.period_till) if args.period_fran else None
    if args.ej_tillampligt:
        ny_profil = markera_ej_tillamplig(profil, regelbas, args.falt, args.motivering, args.roll, datum)
    elif args.varde is None:
        raise ProfilFel("Ange ett värde, eller --ej-tillampligt med --motivering.")
    else:
        ny_profil = bekrafta(profil, regelbas, args.falt, args.varde, args.kalla, args.roll, datum, period=period)
    spara_profil(mapp, ny_profil)
    print(f"{args.falt}: {beskriv_uppgift(regelbas.falt[args.falt], ny_profil.uppgifter[args.falt])}")
    return 0


def kor_profil(args: argparse.Namespace) -> int:
    mapp = befintlig_byramapp(args.byra)
    regelbas = ladda_giltig_regelbas(args.regelbas)
    profil = las_profil(mapp)
    byra = profil.byra
    urval = valj(regelbas, byra.regelpaket, byra.datum, byra.lan)
    kritiska = kritiska_falt(regelbas, urval, profil)
    print(f"Profil för {byra.id} ({byra.regelpaket}, {byra.lan}, {byra.datum.isoformat()})")
    for falt in regelbas.falt.values():
        markering = "*" if falt.id in kritiska else " "
        print(f"{markering} {falt.id}: {beskriv_uppgift(falt, profil.uppgifter.get(falt.id, Uppgift()))}")
        print(f"    {falt.fraga}")
    print("* = kritisk uppgift. Den måste vara bekräftad eller ej tillämplig innan riskbedömningen kan fastställas.")
    print(f"Kritiska uppgifter som saknas: {len(saknade_kritiska(profil, regelbas, urval))}")
    return 0
