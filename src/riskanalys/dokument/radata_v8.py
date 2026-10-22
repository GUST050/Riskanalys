"""Ordagnanna fria analysfält och läsbar placeringskarta i kompletterande B1."""
from collections import defaultdict
from dataclasses import dataclass

from riskanalys.dokument.analystabeller import lokalcell
from riskanalys.dokument.tabeller import rad, tabell
from riskanalys.dokument.tjanstavsnitt_v6 import lokaltext
from riskanalys.dokument.modeller import Underrubrik

# Endast faktiska fria textfält, inte modellens samtliga primitiver eller privata dokumentbytes.
FRIA_FALT = frozenset(('rubrik', 'arbetsmoment_och_befogenheter', 'synliga_floden', 'insynsluckor',
    'avsandare_och_mottagare', 'underlagens_tillforlitlighet', 'motivering', 'kompetens_och_insyn', 'ansvar',
    'omfattning', 'leverantorens_kontroller', 'egen_verifiering', 'brister_och_motstridigheter',
    'handelseforlopp', 'tillampning', 'utfall', 'kvarstar', 'atgard', 'utlosare_eller_frekvens', 'beskrivning',
    'text','referensmotivering','forfattare', 'exponering', 'delningsmotivering', 'leverantorsmotivering', 'samverkan',
    'erfarenhetsprovning', 'pt_motivering', 'tf_motivering', 'reduktionsmotivering', 'sektorsjamforelse',
    'sanktioner', 'slutsats', 'kommentar', 'namn', 'roll', 'rutin_id', 'rutin_version'))


@dataclass(frozen=True)
class Fritext:
    sokvag: str
    text: str
    tjanst: str | None
    belagg: tuple[str, ...]


def fria_analysfalt(paket):
    if paket is None:
        return ()
    def ga(v, stig='', tjanst=None, belagg=()):
        if isinstance(v, dict):
            tj = v.get('tjanst', tjanst)
            # Rotens belagg är objektregistret, inte detta textfälts referens-ID:n.
            refs = tuple(v.get('belagg', v.get('exponeringsbelagg', belagg))) if stig else ()
            for k, x in v.items():
                if not stig and k not in ('gemensamma_scenarier', 'gemensamma_sarbarhetsprovningar','gemensamma_verksamhetsposter','tjanster', 'beslut'):
                    continue  # Modellfelakter och privata dokumentvägar publiceras inte.
                p = stig+'/'+k
                if k in FRIA_FALT and isinstance(x, str) and x:
                    yield Fritext(p, x, tj, refs)
                elif isinstance(x, (dict, list)):
                    yield from ga(x, p, tj, refs)
        elif isinstance(v, list):
            for n,x in enumerate(v):
                yield from ga(x, stig+'/'+str(n), tjanst, belagg)
    return tuple(ga(paket.model_dump(mode='json')))


def textplaceringar(a):
    for n,s in enumerate(a.stycken):
        yield f'{a.id}/stycken/{n}', s.text
    for tab in a.tabeller:
        for n,r in enumerate(tab.rader):
            for m,c in enumerate(r.celler):
                yield f'{a.id}/tabeller/{tab.id}/rader/{n}/celler/{m}', c.text


def komplettera_radata(bilaga, paket, index):
    """Återanvänd fulltext där den finns; varje fältsökväg får en faktisk läsbar placering."""
    falt = fria_analysfalt(paket)
    befintliga = tuple(textplaceringar(bilaga))
    grupper = defaultdict(list)
    for f in falt:
        grupper[f.text].append(f)
    stycken = list(bilaga.stycken)
    kartan = []
    start = len(stycken)
    stycken.append(lokaltext('Råa lokala svar: ordagranna kompletteringar och fältsökvägar. '
        'Läsrapport och kompletterande underlagsbilaga utgör tillsammans hela riskbedömningens dokumentation.'))
    for text, grupp in grupper.items():
        placering = next((p for p,t in befintliga if text in t), None)
        refs = tuple(dict.fromkeys(ref for f in grupp for ref in (
            *((f.tjanst,) if f.tjanst else ()), *index.refs('belagg', f.belagg))))
        if placering is None:
            placering = f'{bilaga.id}/stycken/{len(stycken)}'
            stycken.append(lokaltext(text, refs))
        for f in grupp:
            kartan.append(rad(lokalcell(f.sokvag, refs), lokalcell(f.tjanst or 'Gemensamt', refs),
                lokalcell(placering, refs), lokalcell(index.lista('belagg', f.belagg), refs)))
    karta = tabell('v8-fria-falt', 'Innehållskarta: lokala originalfält till fulltext',
        ('Fältsökväg i fryst analys', 'Tjänst', 'Fulltextplacering i B1', 'Belägg'), kartan, len(stycken))
    return bilaga.model_copy(update={'stycken': tuple(stycken), 'tabeller': (*bilaga.tabeller,karta),
        'underrubriker': (*bilaga.underrubriker, Underrubrik(fore_stycke=start, rubrik='Fullständiga lokala svar och placeringskarta'))})
