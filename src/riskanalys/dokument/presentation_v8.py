"""Deterministiska V8-presentationslistor ur fulla frysta källposter.

Kanoniska avsnitt ändras inte. H7.6 binder analys, full fyndkälla och denna
presentationsversion tillsammans med dokumentets vystruktur.
"""
import json
from collections import defaultdict, deque

from riskanalys.dokument.atgardsgrupper import gruppera_rutinatgarder
from riskanalys.granskning.fyndgrupper import gruppera_fynd

PRESENTATIONSVERSION = 'D-ARB-v8-listor-3'


def atgardsindex(word, analys):
    word.add_heading('Konkreta åtgärder från registrerad analys', level=2)
    word.add_paragraph('Källa: registrerade rutinåtgärder. Rubriker samordnas vid exakt text och rutinversion. '
                       'Medlemsstatus, ansvar och uppföljning står var för sig i tabellen nedan. '
                       'Registreringsordningen är ingen beslutad prioritering.')
    for grupp in gruppera_rutinatgarder(analys):
        post=grupp.medlemmar[0][1]
        word.add_paragraph(post.atgard or 'Åtgärdstext saknas', style='Heading 3')
        word.add_paragraph('Medlemmar: ' + '; '.join(f'{t}, åtgärd {p.id}' for t,p in grupp.medlemmar))


def _varde(value):
    if value is None or value == '' or value == ():
        return 'Saknas'
    if isinstance(value, (tuple,list)):
        return ', '.join(str(x) for x in value)
    return str(value)


def fulla_atgarder(word, analys):
    word.add_heading('Fullständiga registrerade rutinåtgärder',level=1)
    word.add_paragraph('Källa: frysta tjänstevisa Rutinatgard-poster. Inget fält hämtas från fynd eller analysgap.')
    etiketter={'id':'Åtgärds-ID','scenarier':'Scenarier','atgard':'Åtgärdstext','rutin_id':'Rutin-ID',
               'rutin_version':'Rutinversion','rutinbelagg':'Rutinbelägg','status':'Åtgärdsstatus','ansvar':'Ansvar',
               'utlosare_eller_frekvens':'Utlösare eller frekvens','uppfoljning':'Uppföljning','belagg':'Belägg',
               'klart_nar':'Klart när','prioritet':'Prioritet'}
    for t in analys.tjanster:
        for post in t.rutinatgarder:
            word.add_heading(f'{t.tjanst}, åtgärd {post.id}',level=2)
            for key,value in post.model_dump().items():
                word.add_paragraph(f'{etiketter[key]}: {_varde(value)}')


def fyndlista(word, fynd, *, full=False):
    word.add_heading('Fullständig fyndkälla' if full else 'Exakta fyndgrupper',level=1)
    word.add_paragraph('Källa: dokumentets fullständiga granskningsfynd. Visningsgruppering ändrar inga fynd, '
                       'beslut eller fastställelsespärrar. Fyndstatus är skild från åtgärdsstatus.')
    grupper = gruppera_fynd(fynd)
    if full:
        word.add_paragraph('Varje grupp delar exakt samma sakfält. Medlems-ID:n och källpositioner bevarar '
                           'ordning och alla upprepningar. Fältvärden anges som JSON-värden: null betyder '
                           'saknat och "" betyder tom text. Varje full medlem är eget ID plus gruppens sakfält.')
        positioner = defaultdict(deque)
        for n,post in enumerate(fynd,1):
            positioner[id(post)].append(n)
        for n,grupp in enumerate(grupper,1):
            word.add_heading(f'Fyndgrupp {n}',level=2)
            word.add_paragraph('Medlems-ID:n: ' + json.dumps([p.id for p in grupp.medlemmar],ensure_ascii=False))
            word.add_paragraph('Källpositioner: ' + json.dumps([positioner[id(p)].popleft() for p in grupp.medlemmar]))
            for key,value in grupp.medlemmar[0].model_dump(mode='json',exclude={'id'}).items():
                word.add_paragraph(f'{key}: {json.dumps(value,ensure_ascii=False)}')
    else:
        for n,grupp in enumerate(grupper,1):
            post=grupp.medlemmar[0]
            word.add_paragraph(f"{', '.join(p.id for p in grupp.medlemmar)}: allvar {post.allvar}; status {post.status}; "
                               f'regel {_varde(post.regel)}; avsnitt {_varde(post.avsnitt)}. '
                               f'Se underlagsbilagans fullständiga fyndkälla, fyndgrupp {n}, samma ID.')


from typing import Literal
from collections.abc import Callable
from riskanalys.analys.modeller import Analyspaket
from riskanalys.bedomning.modeller import Bedomning
from riskanalys.dokument.modeller import Dokument
from riskanalys.dokument.leverans_v8 import Leveransmall
from riskanalys.granskning.modeller import Fynd
from riskanalys.profil.modeller import Profil
from pydantic import BaseModel, ConfigDict
from riskanalys.lagring.kontrollsumma import for_text


class Presentationsrad(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')
    text: str
    stil: str | None = None


class Presentationsdel(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')
    leveransdel: Literal['lasrapport', 'underlagsbilaga']
    placering: Literal['D-ARB.9:fore_innehall', 'slut:rutinatgarder', 'slut:fynd']
    rader: tuple[Presentationsrad, ...]


class Medlemskalla(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')
    positioner: tuple[int, ...]
    idn: tuple[str, ...]


class Presentationsvy(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')
    titel: str
    format: str
    avsnitt: tuple[str, ...]


class Presentation(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')
    version: str
    # None tillåter historisk verifiering av redan frysta paket, aldrig ny rendering.
    leveransmall: Leveransmall | None = None
    renderingspolicy: str
    literala: tuple[str, ...]
    renderade: tuple[str, ...]
    avsnitt_id: tuple[str, ...]
    vyversion: str
    vyer: tuple[Presentationsvy, ...]
    dokument: str
    analys: str
    fynd: str
    bedomning: str
    erbjudna: tuple[str, ...]
    fyndgrupper: tuple[Medlemskalla, ...]
    # JSON-pointers till varje full medlem i analysens ursprungliga ordning.
    atgardsgrupper: tuple[tuple[str, ...], ...]
    delar: tuple[Presentationsdel, ...]


def kallsumma(value):
    return for_text(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')))


class _Rader:
    """Samma textbyggare matar både Word och den attesterade strukturen."""
    def __init__(self):
        self.rader = []

    def add_heading(self, text, level):
        self.add_paragraph(text, style=f'Heading {level}')

    def add_paragraph(self, text, style=None):
        self.rader.append(Presentationsrad(text=text, stil=style))


def presentationsrader(funktion, *args, **kwargs):
    mal = _Rader()
    funktion(mal, *args, **kwargs)
    return tuple(mal.rader)


def skriv_presentationsrader(word, rader):
    for rad in rader:
        word.add_paragraph(rad.text, style=rad.stil)


def bygg_presentation(
    dokument: Dokument, *, analys: Analyspaket | None, fynd: tuple[Fynd, ...],
    bedomning: Bedomning, profil: Profil,
) -> Presentation:
    from riskanalys.dokument import leverans_v8
    from riskanalys.dokument.underlag import tjanster_med_avsnitt
    from riskanalys.dokument.rendering import bokstavliga_positioner, renderat_avsnitt
    from riskanalys.dokument.rapportvyer import vystruktur

    erbjudna = tuple(t.tjanst for _, t in tjanster_med_avsnitt(bedomning))
    lasanalys = None
    if analys is not None:
        lasanalys = analys.model_copy(update={
            'tjanster': tuple(t for t in analys.tjanster if t.tjanst in erbjudna),
        })
    delar: list[Presentationsdel] = []

    def lagg(leveransdel, placering, funktion: Callable, *args, **kwargs) -> None:
        delar.append(Presentationsdel(
            leveransdel=leveransdel, placering=placering,
            rader=presentationsrader(funktion, *args, **kwargs),
        ))

    if lasanalys is not None and 'D-ARB.9' in dokument.avsnitt_med_id():
        lagg('lasrapport', 'D-ARB.9:fore_innehall', atgardsindex, lasanalys)
    if fynd:
        lagg('lasrapport', 'slut:fynd', fyndlista, fynd)
    if analys is not None:
        lagg('underlagsbilaga', 'slut:rutinatgarder', fulla_atgarder, analys)
    if fynd:
        lagg('underlagsbilaga', 'slut:fynd', fyndlista, fynd, full=True)

    positioner: dict[int, deque[int]] = defaultdict(deque)
    for nummer, post in enumerate(fynd):
        positioner[id(post)].append(nummer)
    grupper = tuple(
        Medlemskalla(
            positioner=tuple(positioner[id(post)].popleft() for post in grupp.medlemmar),
            idn=tuple(post.id for post in grupp.medlemmar),
        )
        for grupp in gruppera_fynd(fynd)
    )
    atgardspointer: dict[tuple[str, int], deque[str]] = defaultdict(deque)
    if analys is not None:
        for ti, tjanst in enumerate(analys.tjanster):
            if tjanst.tjanst in erbjudna:
                for ri, post in enumerate(tjanst.rutinatgarder):
                    atgardspointer[(tjanst.tjanst, id(post))].append(f'/tjanster/{ti}/rutinatgarder/{ri}')
    atgarder = tuple(
        tuple(atgardspointer[(tjanst, id(post))].popleft() for tjanst, post in grupp.medlemmar)
        for grupp in gruppera_rutinatgarder(lasanalys)
    ) if lasanalys is not None else ()
    vyer = vystruktur(dokument)
    return Presentation(
        version=PRESENTATIONSVERSION,
        leveransmall=leverans_v8.LEVERANSMALL,
        renderingspolicy='V8-lokala-original-2',
        literala=tuple(p for a in dokument.avsnitt for p in bokstavliga_positioner(a)),
        renderade=tuple(renderat_avsnitt(a, profil).kontrollsumma() for a in dokument.avsnitt),
        avsnitt_id=tuple(a.id for a in dokument.avsnitt),
        vyversion=vyer['version'],
        vyer=tuple(Presentationsvy(**vy) for vy in vyer['delar']),
        dokument=kallsumma(dokument.model_dump(mode='json')),
        analys=kallsumma(analys.model_dump(mode='json') if analys else None),
        fynd=kallsumma([post.model_dump(mode='json') for post in fynd]),
        bedomning=kallsumma(bedomning.model_dump(mode='json')),
        erbjudna=erbjudna,
        fyndgrupper=grupper,
        atgardsgrupper=atgarder,
        delar=tuple(delar),
    )
