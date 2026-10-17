"""riskanalys analys: lokala frågor, utkast och uttrycklig tjänsteattest."""
from datetime import date
from pathlib import Path

from pydantic import ValidationError
import yaml

from riskanalys.analys.guide import guideblock
from riskanalys.analys.tjanst import Analystjanst
from riskanalys.fel import RiskanalysFel
from riskanalys.kommandon import datumargument, ladda_giltig_regelbas, regelbasargument
from riskanalys.lagring.datamapp import befintlig_byramapp


def lagg_till(underparsers):
    parser = underparsers.add_parser('analys', help='Guidad lokal analys, status och separat mänskligt beslut.')
    parser.add_argument('byra')
    operation = parser.add_mutually_exclusive_group()
    operation.add_argument('--forifyll', action='store_true', help='Starta ett ogranskat förifyllt analysutkast.')
    operation.add_argument('--fornya', action='store_true', help='Bind bevarade svar till aktuellt underlag efter egen jämförelse.')
    operation.add_argument('--forslag', action='store_true', help='Visa ny förifyllnad som YAML utan att skriva över sparade svar.')
    operation.add_argument('--import', dest='importfil', type=Path, help='Strukturerad svarimport som ogranskat utkast.')
    operation.add_argument('--belagg', type=Path, help='Kopiera ett uttryckligen valt privat dokument.')
    operation.add_argument('--modellrapport', type=Path, help='Importera projektets rapportpaket en gång för hela analysen.')
    operation.add_argument('--modellrisk', type=Path, help='Läs lokala modellriskfält från YAML; skapar inget projektfacit.')
    operation.add_argument('--godkann', action='store_true')
    operation.add_argument('--underkann', action='store_true')
    operation.add_argument('--bekrafta-block', type=int, choices=range(1,17), metavar='1–16', help='Bekräfta ett tidigare visat blocks aktuella svar.')
    operation.add_argument('--scenarioval', help='Bekräfta ett tidigare visat gemensamt scenario för en tjänst.')
    parser.add_argument('--revision', default=None, help='Registersumma från aktuell status; tom sträng för första utkastet.')
    parser.add_argument('--tjanst')
    parser.add_argument('--namn', default='')
    parser.add_argument('--roll', default='')
    parser.add_argument('--forfattare', default='')
    parser.add_argument('--kommentar', default='')
    parser.add_argument('--belagg-id', default='')
    parser.add_argument('--visad-summa', default='')
    parser.add_argument('--tillampning', choices=('samma','avviker'))
    parser.add_argument('--lokal-scenario', default='')
    parser.add_argument('--motivering', default='')
    parser.add_argument('--datum', type=datumargument)
    regelbasargument(parser)
    parser.set_defaults(kor=kor)


def kor(args):
    muterar = any((args.forifyll, args.fornya, args.importfil, args.belagg, args.modellrapport, args.modellrisk, args.godkann, args.underkann, args.bekrafta_block, args.scenarioval))
    if muterar and args.revision is None:
        raise RiskanalysFel('Ange --revision med registersumman från aktuell analysstatus.')
    if (args.godkann or args.underkann) and (not args.tjanst or not args.namn.strip() or not args.roll.strip() or args.datum is None):
        raise RiskanalysFel('Beslut kräver --tjanst, --namn, --roll och --datum efter genomgång av svaren.')
    if (args.bekrafta_block or args.scenarioval) and (not args.tjanst or not args.forfattare.strip() or not args.visad_summa):
        raise RiskanalysFel('Bekräftelse kräver --tjanst, --forfattare och --visad-summa från den visade analysen.')
    t = Analystjanst(befintlig_byramapp(args.byra), ladda_giltig_regelbas(args.regelbas))
    dag = args.datum or date.today()
    try:
        if args.forslag:
            print(yaml.safe_dump(t.forslag().model_dump(mode='json'), allow_unicode=True, sort_keys=False))
            return 0
        if args.forifyll:
            t.starta(args.revision)
        elif args.fornya:
            t.fornya(args.revision)
        elif args.importfil:
            t.importera_svar(args.importfil, args.forfattare, args.revision)
        elif args.belagg:
            if not args.belagg_id or args.datum is None:
                raise RiskanalysFel('Beläggsimport kräver --belagg-id och --datum.')
            t.importera_belagg(args.belagg, args.belagg_id, dag, args.revision)
        elif args.modellrapport:
            t.importera_rapport(args.modellrapport, dag, args.revision)
        elif args.modellrisk:
            from riskanalys.lagring.yamlfil import las_yaml
            raw = las_yaml(args.modellrisk)
            if not isinstance(raw, dict):
                raise RiskanalysFel('Modellriskfilen ska innehålla de lokala användningsfälten.')
            t.spara_modellrisk({k: str(v) for k, v in raw.items()}, args.revision)
        elif args.godkann or args.underkann:
            t.beslut(args.tjanst, args.godkann, args.namn, args.roll, dag, args.kommentar, args.revision)
        elif args.bekrafta_block:
            t.spara_block(args.tjanst, args.bekrafta_block, {'operation':'bekrafta', 'forfattare':args.forfattare, 'visad_summa':args.visad_summa}, args.revision)
        elif args.scenarioval:
            t.spara_scenarioval(args.tjanst, args.scenarioval, {'forfattare':args.forfattare, 'visad_summa':args.visad_summa, 'tillampning':args.tillampning or '', 'lokal_scenario':args.lokal_scenario, 'motivering':args.motivering}, args.revision)
        status = t.status(dag)
    except (ValidationError, ValueError) as exc:
        raise RiskanalysFel('Kontrollera analysens statusvärden, referenser, identitet och datum.') from exc
    print('Lokal verksamhetsanalys – registersumma: ' + status.revision)
    if status.paket:
        from riskanalys.analys.provning import BLOCKFALT, blocksumma, scenariosumma
        for tj in status.paket.tjanster:
            if args.tjanst and tj.tjanst != args.tjanst:
                continue
            print(tj.tjanst + ':')
            for block in guideblock(tj):
                print(f'  {block.nummer}. {block.rubrik} – {block.aktivering}; {block.motivering}')
                print('  Visad summa: ' + blocksumma(status.paket, tj.tjanst, block.nummer))
                if args.tjanst:
                    raw = tj.model_dump(mode='json')
                    print(yaml.safe_dump({k:raw[k] for k in BLOCKFALT[block.nummer]}, allow_unicode=True, sort_keys=False))
        for scenario in status.paket.gemensamma_scenarier:
            print('Gemensamt scenario: ' + scenario.id + ' · ' + scenario.rubrik)
            print(scenario.handelseforlopp + '\n' + scenario.relevans + ': ' + scenario.motivering)
            print('Belägg: ' + ', '.join(scenario.belagg) + '\nVisad summa: ' + scenariosumma(scenario))
    for brist in status.brister:
        print(brist)
    print(f"Guidad redigering: riskanalys intag {args.byra}, välj Lokal verksamhetsanalys. Profilfakta rättas i intaget. Analysgodkännande är separat från dokumentets sakgranskning.")
    return 0 if muterar or not status.brister else 2
