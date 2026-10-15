"""Lokalt registeruppslag. Inga profilsvar bekräftas eller ändras."""
import argparse
import json

from riskanalys.foretagsdata.bolagsverket import BolagsverketLeverantor


def lagg_till(underparsers):
    parser = underparsers.add_parser('bolagsverket', help='Visa företagsuppgifter och årsredovisningslista från Bolagsverket.')
    parser.add_argument('orgnr', help='Juridisk persons organisationsnummer (inte personnummer).')
    parser.set_defaults(kor=kor)


def kor(args: argparse.Namespace) -> int:
    resultat = BolagsverketLeverantor().hamta(args.orgnr)
    print('Bolagsverket: aktuell registerbild. Inga profilsvar har ändrats eller skickats till AI.')
    print('Hämtningstid är inte uppgifternas giltighetsdatum. Kontrollera uppgifterna före användning.')
    print('Dokumentlistan visar tillgängliga digitala årsredovisningar, inte ett bevis på fullständig inlämningshistorik.')
    print(json.dumps(resultat, ensure_ascii=False, indent=2))
    return 0
