"""Starta eller återuppta en byrås lokala intervju."""
import webbrowser
from riskanalys.intag.tjanst import Intagstjanst
from riskanalys.intag.webb import skapa_server
from riskanalys.kommandon import ladda_giltig_regelbas, regelbasargument
from riskanalys.fel import RiskanalysFel


def lagg_till(underparsers):
    p=underparsers.add_parser('intag',help='Intervju från tom profil till hela Word-utkastet.')
    p.add_argument('byra');p.add_argument('--oversikt',action='store_true')
    p.add_argument('--utan-browser',action='store_true');p.add_argument('--port',type=int,default=0)
    regelbasargument(p);p.set_defaults(kor=kor)


def kor(args):
    t=Intagstjanst(args.byra,ladda_giltig_regelbas(args.regelbas))
    if args.oversikt:
        k=t.oversikt();print(f'{k.besvarade}/{k.antal} besvarade. Underlag komplett: {"ja" if k.komplett else "nej"}.')
        for id in k.saknade:print(t.rb.falt[id].fraga if id in t.rb.falt else id)
        for h in k.hinder:print(h)
        return 0 if k.komplett else 2
    try:s=skapa_server(t,args.port)
    except OSError as exc:raise RiskanalysFel('Den lokala porten kunde inte öppnas. Prova --port 0.') from exc
    print(f'Öppna det lokala intaget: {s.url}',flush=True)
    print('Ctrl+C avslutar. Sparade svar finns kvar och återupptas med samma kommando.',flush=True)
    if not args.utan_browser:webbrowser.open(s.url)
    try:s.serve_forever()
    except KeyboardInterrupt:pass
    finally:s.server_close()
    return 0
