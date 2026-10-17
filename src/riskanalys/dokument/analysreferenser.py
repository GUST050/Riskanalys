"""Lokala logiska referenser med läsbara etiketter; inga filvägar öppnas."""
from dataclasses import dataclass
from riskanalys.analys.modeller import Analyspaket

PREFIX = 'ANALYS:'


def analysref(typ: str, id: str) -> str:
    return f'{PREFIX}{typ}:{id}'


@dataclass(frozen=True)
class Analysreferenser:
    etiketter: dict[str, str]
    korta: dict[str, str]

    def namn(self, typ, id):
        return self.etiketter.get(analysref(typ, id), f'Okänd lokal referens ({typ}). [VERIFIERA]')

    def lista(self, typ, ids):
        return '; '.join(self.namn(typ, id) for id in ids) or 'Inga angivna'

    def kortlista(self, typ, ids):
        return "; ".join(self.korta.get(analysref(typ, id), self.namn(typ, id)) for id in ids) or "Inga angivna"

    def refs(self, typ, ids):
        return tuple(analysref(typ, id) for id in ids)


def bygg_analysreferenser(paket: Analyspaket | None) -> Analysreferenser:
    etiketter = {}
    korta = {}
    if paket is not None:
        etiketter.update((analysref('belagg', b.id), f'Belägg {n}') for n, b in enumerate(paket.belagg, 1))
        scenarier = (*paket.gemensamma_scenarier, *(s for t in paket.tjanster for s in t.scenarier))
        etiketter.update((analysref('scenario', s.id), f'Scenario {n}: '+(s.rubrik or 'utan rubrik')) for n, s in enumerate(scenarier, 1))
        korta.update((analysref('scenario', s.id), f'Scenario {n}') for n, s in enumerate(scenarier, 1))
        etiketter.update((analysref('delanalys', t.tjanst+':'+d.id), d.rubrik or 'Namnlös delanalys') for t in paket.tjanster for d in t.delanalyser)
    return Analysreferenser(etiketter, korta)
