"""riskanalys sakgranska"""

import argparse
from datetime import date
from typing import Any

from riskanalys.bedomning.korning import las_bedomning
from riskanalys.bedomning.modeller import Tjanstbedomning
from riskanalys.dokument.export import utkastens_oklarheter
from riskanalys.dokument.rendering import renderat_avsnitt
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.faststallelse.sakgranskning import (
    SakgranskningsFel,
    las_sakgranskningar,
    registrera_sakgranskning,
    sakgranskningsstatus,
    spara_sakgranskningar,
)
from riskanalys.granskning.korning import (
    GRANSKNING,
    granskningens_bedomningsmapp,
    granskningens_metadata,
    granskningens_profil,
    kontrollera_kallor,
    las_granskning,
)
from riskanalys.kommandon import datumargument
from riskanalys.lagring.datamapp import befintlig_byramapp
from riskanalys.lagring.korningar import senaste_korning


def lagg_till(underparsers: Any) -> None:
    parser = underparsers.add_parser("sakgranska", help="Gå igenom och godkänn avsnitten ett och ett.")
    parser.add_argument("byra")
    parser.add_argument("--avsnitt", help="Avsnittets ID, till exempel D-ARB.6.1. Utan beslut visas texten.")
    beslut = parser.add_mutually_exclusive_group()
    beslut.add_argument("--godkann", action="store_true", help="Godkänn avsnittet i sin nuvarande lydelse.")
    beslut.add_argument("--underkann", action="store_true", help="Underkänn avsnittet. Kräver --kommentar.")
    parser.add_argument("--kommentar", help="Vad som är fel, eller annan kommentar.")
    parser.add_argument("--namn", help="Namn på den som sakgranskar.")
    parser.add_argument("--roll", default="FfR", help="Rollen hos den som sakgranskar. Standard är FfR.")
    parser.add_argument("--datum", type=datumargument, default=None, help="Standard är dagens datum.")
    parser.set_defaults(kor=kor_sakgranska)


def kor_sakgranska(args: argparse.Namespace) -> int:
    byramapp = befintlig_byramapp(args.byra)
    granskningsmapp = senaste_korning(byramapp, GRANSKNING, f"granska {args.byra}")
    kontrollera_kallor(byramapp, granskningsmapp)
    dokument, _ = las_granskning(granskningsmapp)
    profil = granskningens_profil(byramapp, granskningsmapp)
    sakgranskningar = las_sakgranskningar(byramapp)
    if args.godkann or args.underkann:
        if not args.avsnitt:
            raise SakgranskningsFel("Ange vilket avsnitt beslutet gäller med --avsnitt.")
        nya = registrera_sakgranskning(
            sakgranskningar,
            dokument,
            profil,
            args.avsnitt,
            args.godkann,
            args.roll,
            args.namn,
            args.datum or date.today(),
            args.kommentar,
        )
        spara_sakgranskningar(byramapp, nya)
        print(f"{args.avsnitt}: {sakgranskningsstatus(nya, dokument.avsnitt_med_id()[args.avsnitt], profil)}")
        return 0
    if args.avsnitt:
        avsnitt = dokument.avsnitt_med_id().get(args.avsnitt)
        if avsnitt is None:
            raise SakgranskningsFel(f"Avsnittet {args.avsnitt} finns inte i dokumentet.")
        print(f"{avsnitt.id} {avsnitt.rubrik} ({sakgranskningsstatus(sakgranskningar, avsnitt, profil)})")
        tjanst = dict(tjanster_med_avsnitt(las_bedomning(granskningens_bedomningsmapp(byramapp, granskningsmapp))))
        if avsnitt.id in tjanst:
            print(beskriv_motorns_nivaer(tjanst[avsnitt.id]))
        utkastnamn = granskningens_metadata(granskningsmapp)["utkast"]
        for avsnitt_id, oklarhet in utkastens_oklarheter(byramapp, utkastnamn):
            if avsnitt_id == avsnitt.id:
                print(f"Öppen fråga från AI-utkastet: {oklarhet.fraga} Uppgift som saknas: {oklarhet.saknad_uppgift}.")
        for stycke in renderat_avsnitt(avsnitt, profil).stycken:
            print(f"\n[{stycke.typ}] {stycke.text}")
            print(f"Hänvisningar: {', '.join(stycke.referenser) or 'inga'}")
        return 0
    for avsnitt in dokument.avsnitt:
        print(f"{avsnitt.id} {avsnitt.rubrik}: {sakgranskningsstatus(sakgranskningar, avsnitt, profil)}")
    print(f"Visa ett avsnitt med 'riskanalys sakgranska {args.byra} --avsnitt <ID>'.")
    return 0


def beskriv_motorns_nivaer(tjanst: Tjanstbedomning) -> str:
    """Motorns nivåer för ett riskavsnitt, så att sakgranskaren kan jämföra dem med texten."""
    inneboende, tf = tjanst.inneboende, tjanst.terrorfinansiering
    if inneboende is None or tf is None:
        return f"Tjänsten {tjanst.tjanst} har inga risknivåer."
    return (
        f"Riskmotorns nivåer: inneboende risk {inneboende.risk} (sannolikhet {inneboende.sannolikhet}, "
        f"konsekvens {inneboende.konsekvens}), risk för terrorfinansiering {tf.risk} (sannolikhet {tf.sannolikhet}, "
        f"konsekvens {tf.konsekvens}), kvarstående risk {tjanst.kvarstaende}. "
        "Kontrollera att texten anger samma nivåer."
    )
