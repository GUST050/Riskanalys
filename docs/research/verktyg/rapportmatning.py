"""Mät V8-rapporten för H7.1:s fyrtjänstfall: ord per avsnitt och leveransdel, och upprepade stycken.

Syntetiska uppgifter och Testleverantor; inga AI-anrop. Körs från repots rot:
.venv/bin/python docs/research/verktyg/rapportmatning.py [H7.1-fall, standard fyra_tjanster]
"""
import argparse
import json
from dataclasses import replace
from hashlib import sha256
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from docs.research.verktyg.matkontrakt import frysta_skrivsvar
from riskanalys.dokument.arb_v8 import bygg_arb_v8
from riskanalys.dokument.rendering import renderat_avsnitt
from riskanalys.drift.historik import Historik
from riskanalys.regelverk.laddning import ladda_regelbas
from tester.enhet.test_arb_v8 import skriv
from tester.fixturer.rapportlasprov import bygg_rapportlasprov


def ord(text):
    return len(text.split())


TJANSTNAMN = ()


def normalisera(text):
    """Tjänstenamn, ID:n och tal byts mot platshållare. Mäter likartad struktur, inte samma sakuppgift."""
    for namn in TJANSTNAMN:
        text = text.replace(namn, '#').replace(namn.lower(), '#')
    text = re.sub(r'\b(T|H|S|C|KR|BT)-[A-Z0-9-]+\b', '#', text)
    return re.sub(r'\d+', '0', text)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fall",nargs="?",default="fyra_tjanster")
    parser.add_argument("--analys-schema",type=int,choices=(1,2),default=1)
    args=parser.parse_args(argv)
    global TJANSTNAMN
    rb = ladda_regelbas()
    TJANSTNAMN = tuple(t.namn for t in rb.tjanster.values())
    with tempfile.TemporaryDirectory() as rot:
        fall = args.fall
        print('Provfall:', fall)
        f = bygg_rapportlasprov(rb, Path(rot).resolve(), fall)
        original=f.analys
        if args.analys_schema==2:
            from riskanalys.analys.overforing import foresla_overforing
            f=replace(f,analys=foresla_overforing(rb,original))
        svar=skriv(f)
        def hashv(v):return 'sha256:'+sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        print('Mätkontrakt:',json.dumps({'format':'D-ARB-tjanst-v8','analys_schema':args.analys_schema,
            'tillstand':'ogranskat uttryckligt överföringsförslag, samtliga lokala originalsvar bevarade',
            'profil':hashv(f.profil.model_dump(mode='json')),'motor':hashv(f.bedomning.model_dump(mode='json')),
            'skrivsvar':hashv(frysta_skrivsvar(svar)),'regelbas':rb.kontrollsumma},ensure_ascii=False,sort_keys=True))
        d = bygg_arb_v8(rb, f.profil, f.bedomning, svar, Historik(), analys=f.analys)
    delar = defaultdict(int)
    rader = []
    texter = []
    for a in d.avsnitt:
        r = renderat_avsnitt(a, f.profil)
        stycken = sum(ord(s.text) for s in r.stycken)
        tabell = sum(ord(c.text) for t in a.tabeller for rad in t.rader for c in rad.celler)
        delar[a.leveransdel] += stycken + tabell
        rader.append((a.leveransdel, a.id, a.rubrik[:55], stycken, tabell))
        texter.extend((a.leveransdel, a.id, s.text) for s in a.stycken)
        texter.extend((a.leveransdel, a.id, c.text) for t in a.tabeller for rad in t.rader for c in rad.celler)
    print('Ord per leveransdel:', dict(delar), 'totalt', sum(delar.values()))
    print('\nAvsnitt (del, id, rubrik, ord i stycken, ord i tabeller):')
    for rad in sorted(rader, key=lambda x: -(x[3] + x[4]))[:25]:
        print(f'  {rad[0]:12} {rad[1]:14} {rad[2]:55} {rad[3]:6} {rad[4]:6}')
    tjanster = sorted({a for _, a, _ in texter if a.startswith('D-ARB.6.')})
    ordagrant = set.intersection(*({t for _, a, t in texter if a == x} for x in tjanster)) if tjanster else set()
    struktur = set.intersection(*({normalisera(t) for _, a, t in texter if a == x} for x in tjanster)) if tjanster else set()
    forsta = [t for _, a, t in texter if tjanster and a == tjanster[0]]
    totalt = sum(ord(t) for t in forsta)
    print(f'\nFörsta tjänsteavsnittet {tjanster[0] if tjanster else "-"}: {totalt} ord. Text som finns i alla {len(tjanster)} tjänster:')
    print(f'  ordagrant identisk:            {sum(ord(t) for t in forsta if t in ordagrant):5} ord')
    print(f'  likartad struktur (namn, ID och tal utbytta, ej ordagrann): '
          f'{sum(ord(t) for t in forsta if t not in ordagrant and normalisera(t) in struktur):5} ord')
    print('\nUpprepade texter (minst 12 ord), sorterade efter totala ord:')
    grupper = defaultdict(list)
    for del_, avsnitt, text in texter:
        if ord(text) >= 12:
            grupper[normalisera(text)].append((del_, avsnitt, text))
    upprepade = [(len(g) * ord(g[0][2]), len(g), g) for g in grupper.values() if len(g) > 1]
    for totalt, antal, g in sorted(upprepade, key=lambda x: -x[0])[:20]:
        platser = Counter(f'{d}:{a}' for d, a, _ in g)
        print(f'  {antal:3} gånger, {totalt:5} ord: {g[0][2][:110]}')
        print(f'      i {dict(platser)}')


if __name__ == '__main__':
    main()
