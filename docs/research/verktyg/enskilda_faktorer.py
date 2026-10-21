"""Vad gör varje enskild riskfaktor i en byrå utan andra faktorer? Nuvarande metod och TF-alternativ.

Endast syntetiska profiler (tester/fixturer/faktorer.py). Inga regelbasfiler ändras; TF-alternativet
sätts bara i minnet för denna körning.
"""
import sys
from pathlib import Path

# Körs från repots rot: .venv/bin/python docs/research/verktyg/enskilda_faktorer.py
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from riskanalys.regelverk.laddning import ladda_regelbas
from riskanalys.regelverk.urval import valj
from riskanalys.bedomning import motor, scenarier
from tester.fixturer.faktorer import faktorprofil, faktorvarden

rb = ladda_regelbas()
TJANSTER = ('T-RED-01', 'T-RED-02', 'T-RED-03', 'T-RED-04', 'T-SKATT-01', 'T-BOLAG-01')


def nivaer(profil, tf_konsekvens):
    scenarier.TF_KONSEKVENS = tf_konsekvens
    b = motor.bedom(rb, valj(rb, profil.byra.regelpaket, profil.byra.datum, profil.byra.lan), profil)
    return {t.tjanst: (t.inneboende.risk, t.kvarstaende, t.terrorfinansiering.risk)
            for t in b.tjanster if t.tjanst in TJANSTER}


def kort(niva):
    return {'låg': 'L', 'måttlig': 'M', 'hög': 'H', 'mycket hög': 'MH'}[niva]


rader = [('ingen faktor', ())] + [(f'{s} {rb.sarbarheter[s].namn}', (s,)) for s in faktorvarden(rb)]
print('Kolumner per tjänst: PT före / PT efter kontroll / TF nu / TF om konsekvens betydande')
print('Tjänster:', ', '.join(TJANSTER))
for namn, faktorer in rader:
    profil = faktorprofil(rb, faktorer, alla_tjanster=True, med_bankdata=True)
    nu, alt = nivaer(profil, 'allvarlig'), nivaer(profil, 'betydande')
    celler = ['/'.join((kort(nu[t][0]), kort(nu[t][1]), kort(nu[t][2]), kort(alt[t][2]))) for t in TJANSTER]
    print(f'{namn[:60]:60} | ' + ' | '.join(f'{c:13}' for c in celler))
scenarier.TF_KONSEKVENS = 'allvarlig'
