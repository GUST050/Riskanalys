"""riskanalys ny, bekrafta och profil"""

import argparse
from datetime import date
from typing import Any
from pydantic import ValidationError

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
from riskanalys.profil.lagring import las_profil, spara_profil, profilrevision
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
    bekraftelse.add_argument('--rattelse', action='store_true', help='Rätta ett felregistrerat nej med källa och --motivering. Gäller inte ett nytt införande.')
    bekraftelse.add_argument('--plan', help='Uttryckligt val av den aktiva ny-tjänst-plan som genomförs vid införandet.')
    bekraftelse.add_argument("--datum", type=datumargument, default=None, help="Standard är dagens datum.")
    bekraftelse.add_argument("--period-fran", type=datumargument)
    bekraftelse.add_argument("--period-till", type=datumargument)
    regelbasargument(bekraftelse)
    bekraftelse.set_defaults(kor=kor_bekrafta)

    visning = underparsers.add_parser("profil", help="Visa byråns profil och vilka uppgifter som saknas.")
    visning.add_argument("byra")
    regelbasargument(visning)
    visning.set_defaults(kor=kor_profil)
    for namn, modell in (('plan', 'Tjansteplan'), ('kombinationsgrupp', 'Kombinationsgrupp')):
        parser = underparsers.add_parser(namn, help='Registrera eller ersätt lokalt underlag från en YAML-fil.')
        parser.add_argument('byra')
        parser.add_argument('--fil', required=True)
        regelbasargument(parser)
        parser.set_defaults(kor=kor_lokalt_underlag, underlagsmodell=modell)


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
    revision = profilrevision(profil)
    datum = args.datum or date.today()
    if bool(args.period_fran) != bool(args.period_till):
        raise ProfilFel("Ange både --period-fran och --period-till.")
    if args.period_fran and args.period_fran > args.period_till:
        raise ProfilFel("Periodens från-datum får inte vara efter till-datum.")
    period = Period(fran=args.period_fran, till=args.period_till) if args.period_fran else None
    falt = regelbas.falt.get(args.falt)
    if falt and falt.alias_for and regelbas.falt[falt.alias_for].intag:
        raise ProfilFel(f'Besvara det aktuella intagsfältet {falt.alias_for}; äldre alias kan inte ändras via bekrafta.')
    if falt and falt.intag and not falt.basfalt:
        from riskanalys.intag.modeller import IntagSvar
        from riskanalys.intag.svar import besvara
        if args.varde is None and not args.ej_tillampligt:
            raise ProfilFel('Ange ett värde och --kalla.')
        try:
            svar = IntagSvar(falt=args.falt, text=args.varde or '',
                kalla=args.kalla or '', roll=args.roll, datum=datum, period=period,
                status='ej_tillämplig' if args.ej_tillampligt else 'bekräftad', motivering=args.motivering or '')
        except ValidationError as exc:
            namn = {'text': 'värdet', 'roll': '--roll', 'kalla': '--kalla', 'motivering': '--motivering'}
            fel = []
            for e in exc.errors(include_input=False):
                falt = namn.get(e['loc'][0], str(e['loc'][0]))
                grans = e.get('ctx', {}).get('max_length')
                fel.append(f'{falt}: använd högst {grans} tecken' if grans else f'{falt}: kontrollera värdet')
            raise ProfilFel('Kontrollera intagssvaret. ' + '; '.join(fel) + '.') from None
        ny_profil = besvara(regelbas, profil, svar)
    elif args.ej_tillampligt:
        ny_profil = markera_ej_tillamplig(profil, regelbas, args.falt, args.motivering, args.roll, datum)
    elif args.varde is None:
        raise ProfilFel("Ange ett värde, eller --ej-tillampligt med --motivering.")
    else:
        ny_profil = bekrafta(profil, regelbas, args.falt, args.varde, args.kalla, args.roll, datum, period=period)
    from riskanalys.profil.forandringar import spara_andring
    rattelse = None
    if getattr(args,'rattelse',False):
        from riskanalys.drift.historik import Erbjudanderattelse
        t = next((t for t in regelbas.tjanster.values() if t.erbjuds_falt == args.falt), None)
        if t is None or not args.motivering or ny_profil.uppgifter[args.falt].varde is not True:
            raise ProfilFel('Rättelse kräver ett tjänsteerbjudande till ja, --kalla och --motivering.')
        from riskanalys.profil.omfattning import kompatibilitetsvy
        rattelse = Erbjudanderattelse(tjanst=t.id,fore=kompatibilitetsvy(profil,regelbas).uppgifter[args.falt],efter=ny_profil.uppgifter[args.falt],
            motivering=args.motivering,kalla=args.kalla or '',ansvarig=args.roll,datum=datum,profilrevision=revision)
    val=()
    if getattr(args,'plan',None):
        from riskanalys.profil.modeller import Planval
        t=next((t for t in regelbas.tjanster.values() if t.erbjuds_falt==args.falt),None)
        if t is None:
            raise ProfilFel('--plan får bara användas med ett tjänsteerbjudande.')
        val=(Planval(tjanst=t.id,plan_id=args.plan),)
    spara_andring(mapp,regelbas,ny_profil,revision,rattelse=rattelse,planval=val)
    print(f"{args.falt}: {beskriv_uppgift(regelbas.falt[args.falt], ny_profil.uppgifter[args.falt])}")
    return 0


def kor_lokalt_underlag(args):
    from pathlib import Path
    import yaml
    from riskanalys.intag.tjanst import Intagstjanst
    from riskanalys.profil.modeller import Tjansteplan, Kombinationsgrupp
    t = Intagstjanst(args.byra,ladda_giltig_regelbas(args.regelbas))
    revision = profilrevision(t.profil())
    modell = Tjansteplan if args.underlagsmodell == 'Tjansteplan' else Kombinationsgrupp
    try:
        post = modell.model_validate(yaml.safe_load(Path(args.fil).read_text(encoding='utf-8')))
    except (OSError, ValueError, yaml.YAMLError):
        raise ProfilFel('Underlaget kan inte läsas. Kontrollera YAML-filens fält, typer och belägg.') from None
    if modell is Tjansteplan:
        t.spara_plan(post,revision)
    else:
        t.spara_kombinationsgrupp(post,revision)
    print('Lokalt underlag sparat. Beräkna aktuell bedömning och förnya och sakpröva analysen före fastställelse.')
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
