"""Provkör ogranskade metodalternativ för D6 och D9 mot syntetiska profiler. Inga beslut.

Alternativen sätts bara i minnet för körningen; regelbasens filer och motorns kod ändras inte.
Körs från repots rot: .venv/bin/python docs/research/verktyg/metodalternativ.py
"""
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from riskanalys.bedomning import motor, scenarier
from riskanalys.regelverk.laddning import ladda_regelbas
from riskanalys.regelverk.urval import valj
from riskanalys.profil.omfattning import harled_andelar
from tester.fixturer.arb_kedja import andrat
from tester.fixturer.faktorer import faktorprofil, faktorvarden
from tester.fixturer.rapportlasprov import FALL, bygg_rapportlasprov

GRUND = ladda_regelbas()
TJANSTER = ('T-RED-01', 'T-RED-02', 'T-RED-03', 'T-RED-04', 'T-SKATT-01', 'T-BOLAG-01')
ORIGINAL = {'mojliggorande': scenarier._mojliggorande, 'dimensioner': scenarier.hot_dimensioner}


def _utan_tf_lankar(rb):
    """D6 C1, katalogfilter: en faktor räknas i TF bara om katalogen länkar den till ett H-TF-hot.

    Avsaknad av H-TF-länk visar inte att faktorn saknar saklig TF-relevans; H-03 omfattar båda.
    """
    andrade = {id: s.model_copy(update={'galler': 'penningtvatt'}) if s.galler == 'bada'
               and not any(h.startswith('H-TF') for h in s.hot) else s for id, s in rb.sarbarheter.items()}
    return rb.model_copy(update={'sarbarheter': andrade})


def _omradespaslag(sarbarheter, hot, dimension):
    """D9 B, påslag efter antal områden: ett steg per katalogområde utöver det första (kund, kanal,
    geo, verk, tj). Räknar områden, inte belagt oberoende orsaker."""
    valda = ORIGINAL['mojliggorande'](sarbarheter, hot, dimension)
    steg = max(len({s.omrade for s in valda}) - 1, 0)
    return tuple(SimpleNamespace(id=f'{s.id}', effekt=SimpleNamespace(sannolikhet=1 if n < steg else 0))
                 for n, s in enumerate(valda))


ALTERNATIV = {
    'nu': {},
    'D6B konsekvens betydande': {'tf': 'betydande'},
    'D6C1 katalogfilter H-TF-länk': {'tf_lankar': True},
    'D6C2 H-03 bara PT': {'h03_pt': True},
    'D9B påslag efter antal områden': {'tva': True},
    'D9B + D6B': {'tva': True, 'tf': 'betydande'},
}


@contextmanager
def alternativ(namn):
    val = ALTERNATIV[namn]
    rb = _utan_tf_lankar(GRUND) if val.get('tf_lankar') else GRUND
    scenarier.TF_KONSEKVENS = val.get('tf', 'allvarlig')
    if val.get('tva'):
        scenarier._mojliggorande = _omradespaslag
    if val.get('h03_pt'):
        scenarier.hot_dimensioner = lambda h: ('pt',) if h.id == 'H-03' else ORIGINAL['dimensioner'](h)
    try:
        yield rb
    finally:
        scenarier.TF_KONSEKVENS = 'allvarlig'
        scenarier._mojliggorande = ORIGINAL['mojliggorande']
        scenarier.hot_dimensioner = ORIGINAL['dimensioner']


def nivaer(rb, profil):
    b = motor.bedom(rb, valj(rb, profil.byra.regelpaket, profil.byra.datum, profil.byra.lan), profil)
    return {t.tjanst: (t.inneboende.risk, t.kvarstaende, t.terrorfinansiering.risk) for t in b.tjanster
            if t.tjanst in TJANSTER and t.erbjuds}


def kort(niva):
    return {'låg': 'L', 'måttlig': 'M', 'hög': 'H', 'mycket hög': 'MH'}[niva]


def rad(n):
    return '/'.join(kort(x) for x in n)


UTLAND_ANTAL = 'P-GEO.antal_utland_transaktion'

PROFILER = {
    'ingen faktor': (),
    '1 av 100 kunder med utlandstransaktion (S-GEO-01)': ((), {UTLAND_ANTAL: 1}),
    'alla kunder med utlandstransaktion (S-GEO-01, 100 %)': ('S-GEO-01',),
    'kontanter (S-KUND-02)': ('S-KUND-02',),
    'PEP (S-ARB-02)': ('S-ARB-02',),
    'enmansbyrå (S-ARB-16)': ('S-ARB-16',),
    'enmansbyrå + utland 100 %': ('S-ARB-16', 'S-GEO-01'),
    'distans + extern KYC (samma område)': ('S-ARB-08', 'S-ARB-10'),
    'utland 100 % + distans + extern KYC': ('S-GEO-01', 'S-ARB-08', 'S-ARB-10'),
    'ideell + PEP': ('S-ARB-05', 'S-ARB-02'),
    'riskbransch + kontanter + utland 100 % + nära relation': ('S-KUND-01', 'S-KUND-02', 'S-GEO-01', 'S-ARB-01'),
}


def profil_for(rb, spec):
    """Faktorer via fixturens utlösande värden, eller uttryckliga antal för minimal exponering."""
    faktorer, antal = spec if len(spec) == 2 and isinstance(spec[1], dict) else (spec, {})
    profil = faktorprofil(rb, faktorer, alla_tjanster=True, med_bankdata=True)
    for falt, varde in antal.items():
        profil = andrat(profil, falt, varde=varde)
    return harled_andelar(profil, rb, frozenset(antal)) if antal else profil


def main():
    print('Cell per tjänst: PT före / PT efter kontroll / TF.  Tjänster:', ', '.join(TJANSTER))
    for profilnamn, faktorer in PROFILER.items():
        print(f'\n{profilnamn}')
        for namn in ALTERNATIV:
            with alternativ(namn) as rb:
                n = nivaer(rb, profil_for(rb, faktorer))
            print(f'  {namn:34} ' + ' | '.join(f'{rad(n[t]):8}' for t in TJANSTER))
    print('\nEnskilda faktorer: antal av 24 som ensamma ger PT hög i bokföring / TF hög eller mer i bokföring')
    for namn in ALTERNATIV:
        with alternativ(namn) as rb:
            utfall = [nivaer(rb, faktorprofil(rb, (f,), alla_tjanster=True, med_bankdata=True))['T-RED-01']
                      for f in faktorvarden(rb)]
        print(f'  {namn:34} PT hög {sum(u[0] == "hög" for u in utfall):2}   TF hög+ {sum(u[2] in ("hög", "mycket hög") for u in utfall):2}')
    print('\nH7.1-kontraster (fyra redovisningstjänster): olika utfall över de tio fallen')
    for namn in ALTERNATIV:
        with alternativ(namn) as rb:
            utfall = {}
            for fall in FALL:
                with tempfile.TemporaryDirectory() as rot:
                    f = bygg_rapportlasprov(rb, Path(rot).resolve(), fall)
                b = {t.tjanst: (t.inneboende.risk, t.kvarstaende, t.terrorfinansiering.risk)
                     for t in f.bedomning.tjanster if t.erbjuds}
                utfall[fall] = ' | '.join(f'{rad(b[t]):8}' for t in sorted(b))
        print(f'  {namn:34} ' + '; '.join(sorted(set(utfall.values()))))


if __name__ == '__main__':
    main()
