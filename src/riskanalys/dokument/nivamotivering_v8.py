"""V8 visar varje nivåväg och alla avgörande före/efter lokalt, utan omräkning."""
from dataclasses import dataclass
from typing import Literal

from riskanalys.dokument.modeller import Textstycke, Tabellcell, Tabellrad, Dokumenttabell
from riskanalys.dokument.nivamotivering_v6 import nivamotivering_stycken
from riskanalys.dokument.scenariotabell import hotnamn, scenarioforklaring, kontrollmening, scenarioreferenser, kontrollnamn


def avgor_efter(t, s):
    return s.dimension == 'pt' and s.kvarstaende is not None and s.kvarstaende == t.kvarstaende


def berakningsgrupper(t):
    """Endast hotets identitet får skilja; alla sparade beräkningsfält ingår."""
    grupper = {}
    for s in t.scenarier:
        grupper.setdefault(s.model_dump_json(exclude={'hot'}), []).append(s)
    return tuple(tuple(g) for g in grupper.values())


def faktorgrupper(t):
    """Faktorlistor får delas bara inom samma fullständiga beräkningsstruktur."""
    return berakningsgrupper(t)


def gruppreferenser(t, grupp):
    return tuple(dict.fromkeys(ref for s in grupp for ref in scenarioreferenser(t, s)))


def nivaskal(rb, t, analys):
    if not t.scenarier:
        return nivamotivering_stycken(rb, t, analys)
    poster = []
    for grupp in berakningsgrupper(t):
        s = grupp[0]
        if not s.avgorande and not avgor_efter(t, s):
            continue
        nar = 'före och efter kontroll' if s.avgorande and avgor_efter(t, s) else 'före kontroll' if s.avgorande else 'efter kontroll'
        poster.append(Textstycke(typ='motivering', text=f'Avgörande {nar} ({s.dimension.upper()}): '
            + '; '.join(f'{hotnamn(rb, medlem)} [{medlem.hot}]' for medlem in grupp)
            + f'. {scenarioforklaring(rb, t, s, vikter=True)} {kontrollmening(rb, s)}',
            referenser=list(gruppreferenser(t, grupp)), proveniens='regelbas'))
    poster.append(Textstycke(typ='motivering', text='Metodstatus: nivåer och reduktion är versionsbundna motorutfall. '
        'De ersätter inte lokal relevans-/täckningsprövning eller sakkunnigprövning av metodval.',
        referenser=list(t.regelspar), proveniens='regelbas'))
    # Endast de lokala motiveringarna och separat sanktion återanvänds, inga gamla scenariohänvisningar.
    poster.extend(s for s in nivamotivering_stycken(rb, t, analys)
                  if s.proveniens == 'lokal' or s.text.startswith('Sanktionsrisk:'))
    return tuple(poster)


def scenariotabell(rb, t):
    """Nivåvägen i sju kolumner; faktor-/kontroll-ID:n står i den intilliggande tabellen."""
    if not t.scenarier:
        return None
    rader = []
    for s in t.scenarier:
        refs = scenarioreferenser(t, s)
        fore = s.risk + (' – avgör före' if s.avgorande else '')
        efter = (s.kvarstaende or 'Ej beräknad') + (' – avgör efter' if avgor_efter(t, s) else '')
        varden = (f'{hotnamn(rb,s)} [{s.hot}], {s.dimension.upper()}',
            s.hotniva + (' (iakttaget)' if s.iakttaget else ''), s.sarbarhetsniva,
            s.sannolikhet, s.konsekvens, fore, efter)
        rader.append(Tabellrad(celler=tuple(Tabellcell(text=v, referenser=refs, proveniens='regelbas') for v in varden)))
    return Dokumenttabell(id=t.tjanst+'-motorscenarier', rubrik='Samtliga motorutfall: före och efter kontroll',
        kolumner=('Hot och dimension', 'Hotnivå', 'Sårbarhetsnivå', 'Sannolikhet',
                  'Konsekvens', 'Risk före', 'Kvarstående'), rader=tuple(rader), fore_stycke=0)


def faktortabell(rb, t):
    """Fulla faktorer och bärande kontroller per exakt scenario, ingen namnlikhetsgruppering."""
    if not t.scenarier:
        return None
    rader = []
    for grupp in faktorgrupper(t):
        s = grupp[0]
        refs = gruppreferenser(t, grupp)
        faktorer = ', '.join(s.sarbarheter) or 'Inga'
        kontroller = ', '.join(s.tackande_kontroller) or 'Ingen bärande kontroll'
        rader.append(Tabellrad(celler=tuple(Tabellcell(text=v, referenser=refs, proveniens='regelbas')
            for v in ('; '.join(f'{medlem.hot}, {medlem.dimension.upper()}' for medlem in grupp), faktorer, kontroller))))
    return Dokumenttabell(id=t.tjanst+'-motorfaktorer', rubrik='Scenariernas faktorer och bärande kontroller',
        kolumner=('Scenario', 'Sårbarheter', 'Bärande kontroller'), rader=tuple(rader), fore_stycke=0)


@dataclass(frozen=True)
class Faktorregisterpost:
    typ: Literal['sarbarhet', 'kontroll']
    id: str
    namn: str
    scenarioindex: tuple[int, ...]
    referenser: tuple[str, ...]


def faktorregisterposter(rb, t) -> tuple[Faktorregisterpost, ...]:
    """Exakt ID-register i första förekomstordning, med alla scenarioidentiteter."""
    urval = {}
    for i,s in enumerate(t.scenarier):
        for typ,ids in (('sarbarhet',s.sarbarheter),('kontroll',s.tackande_kontroller)):
            for id in ids:
                urval.setdefault((typ,id), []).append(i)
    poster=[]
    for (typ,id),medlemmar in urval.items():
        katalog=rb.sarbarheter if typ=='sarbarhet' else rb.kontroller
        namn=katalog[id].namn if id in katalog else 'Namn saknas i regelbasen'
        refs=tuple(dict.fromkeys(ref for i in medlemmar for ref in scenarioreferenser(t,t.scenarier[i])))
        poster.append(Faktorregisterpost(typ,id,namn,tuple(medlemmar),refs))
    return tuple(poster)


def faktorregister(rb,t):
    poster=faktorregisterposter(rb,t)
    if not poster:
        return None
    rader=[]
    for post in poster:
        varden=('Sårbarhet' if post.typ=='sarbarhet' else 'Bärande kontroll', post.id, post.namn,
            '; '.join(f'{t.scenarier[i].hot}, {t.scenarier[i].dimension.upper()}' for i in post.scenarioindex))
        rader.append(Tabellrad(celler=tuple(Tabellcell(text=v,referenser=post.referenser,proveniens='regelbas') for v in varden)))
    return Dokumenttabell(id=t.tjanst+'-faktorregister',rubrik='Tjänstens faktor och kontrollregister',
        kolumner=('Typ','ID','Fullständigt namn','Scenarier'),rader=tuple(rader),fore_stycke=0)


_ORSAKER = {
    'saknas': lambda k: 'byråns prövning anger att den bärande kontrollen inte täcker scenariot',
    'oprovat': lambda k: 'hotet saknar en relevant lokal scenarioprövning',
    'motstridig': lambda k: f'byråns prövningar av {k} är motstridiga',
    'obelagd': lambda k: f'den tillräckliga täckningen av {k} saknar beskriven räckvidd eller aktuellt genomförandebelägg',
    'delvis': lambda k: f'byråns prövning visar bara delvis täckning av {k}, vilket inte räcker för ett helt kontrollavdrag',
    'stod': lambda k: f'det saknas en positiv lokal prövning av den bärande kontrollen {k} i ett relevant scenario',
}


def ej_godtagna_sankningar(rb, profil, paket, a, t):
    """Läsbar förklaring per motorsänkning som den lokala prövningen inte godtar.

    Det frysta motorresultatet skrivs inte om; texten anger att sänkningen inte gäller.
    """
    from riskanalys.analys.provning import ej_godtagna_sankningar as skal
    from riskanalys.bedomning.motor import RISKNIVAER
    if not t.scenarier:
        return ()
    per_scenario = {}
    for b in skal(rb, profil, paket, a, t):
        per_scenario.setdefault(id(b.scenario), (b.scenario, []))[1].append(_ORSAKER[b.orsak](', '.join(b.kontroller)))
    poster = []
    for s, orsaker in per_scenario.values():
        poster.append(Textstycke(typ='motivering', text=(
            f'Motorns sänkning av {hotnamn(rb, s)} [{s.hot}] från {s.risk} till {s.kvarstaende} är inte godtagen '
            f'av den lokala prövningen: {"; ".join(dict.fromkeys(orsaker))}. Till dess prövningen kompletterats '
            f'eller metodkonflikten avgjorts gäller scenariots inneboende nivå {s.risk}, och analysen kan inte '
            'godkännas. [VERIFIERA]'), referenser=[t.tjanst, *scenarioreferenser(t, s), 'D-ARB.B1'], proveniens='lokal'))
    hogsta = max((s.risk for s, _ in per_scenario.values()), key=RISKNIVAER.index, default=None)
    if hogsta and t.kvarstaende and RISKNIVAER.index(t.kvarstaende) < RISKNIVAER.index(hogsta):
        poster.append(Textstycke(typ='motivering', text=(
            f'Tjänstens redovisade kvarstående PT-nivå {t.kvarstaende} bygger på sänkningar som inte är godtagna. '
            f'Utan dem är nivån minst {hogsta}. [VERIFIERA]'), referenser=[t.tjanst, 'D-ARB.B1'], proveniens='lokal'))
    return tuple(poster)
