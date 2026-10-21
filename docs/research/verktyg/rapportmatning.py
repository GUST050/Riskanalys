"""Mät V8-rapporten för H7.1:s fyrtjänstfall: ord per avsnitt och leveransdel, och upprepade stycken.

Syntetiska uppgifter och Testleverantor; inga AI-anrop. Körs från repots rot:
.venv/bin/python docs/research/verktyg/rapportmatning.py
"""
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from riskanalys.dokument.arb_v8 import bygg_arb_v8
from riskanalys.dokument.rendering import renderat_avsnitt
from riskanalys.drift.historik import Historik
from riskanalys.regelverk.laddning import ladda_regelbas
from tester.enhet.test_arb_v8 import skriv
from tester.fixturer.rapportlasprov import bygg_rapportlasprov


def ord(text):
    return len(text.split())


def normalisera(text):
    """Tjänstenamn och ID:n byts mot platshållare så att mallupprepning mellan tjänster syns."""
    text = re.sub(r'\b(T|H|S|C|KR|BT)-[A-Z0-9-]+\b', '#', text)
    return re.sub(r'\d+', '0', text)


def main():
    rb = ladda_regelbas()
    with tempfile.TemporaryDirectory() as rot:
        f = bygg_rapportlasprov(rb, Path(rot).resolve(), 'fyra_tjanster')
        d = bygg_arb_v8(rb, f.profil, f.bedomning, skriv(f), Historik(), analys=f.analys)
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
