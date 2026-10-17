"""Gemensam läsmodell för de sexton lokala guidestegen."""
from dataclasses import dataclass

from riskanalys.analys.modeller import Analyspaket, Tjansteanalys
from riskanalys.analys.provning import ALLTID, blocksumma

RUBRIKER = (
    'Uppdrag, kunder, period och mandat', 'Arbetsmoment och delanalyser',
    'Faktisk betalningsinsyn', 'Uppdragets hanterbarhet',
    'Leverantörer och eget ansvar', 'Scenarier och tjänstevisa avvikelser',
    'Sårbarheter: kunder, kanaler, geografi och egen verksamhet',
    'Faktorernas samverkan', 'Egna lärdomar och bevakning',
    'Faktisk kontroll och effekt', 'Kvarstående begränsningar och luckor',
    'Prövning av motorns faktiska reduktion', 'Motivering av PT-utfallet',
    'TF-scenarier och osäkerheter', 'Sektorsbild och sanktioner',
    'Slutsats, rutin och uppföljning',
)


@dataclass(frozen=True)
class Guideblock:
    nummer: int
    rubrik: str
    obligatorisk: bool
    aktivering: str
    motivering: str
    bekraftad_summa: str | None


def guideblock(tjanst: Tjansteanalys) -> tuple[Guideblock, ...]:
    poster = {b.nummer: b for b in tjanst.block}
    return tuple(Guideblock(n, text, n in ALLTID,
        poster[n].aktivering if n in poster else 'aktiv' if n in ALLTID else 'okand',
        poster[n].motivering if n in poster else '',
        poster[n].bekraftad_summa if n in poster else None)
        for n, text in enumerate(RUBRIKER, 1))


@dataclass(frozen=True)
class Arbetsborda:
    alltid: int
    villkorade: int
    unika_scenarier: int
    bekraftade_block: int
    gemensamma_val: int
    belaggsreferenser: int
    ateranvanda_belaggsreferenser: int
    nyskrivna_kompletteringar: int | None = None


def arbetsborda(paket: Analyspaket) -> Arbetsborda:
    """Räkna registerinnehåll; faktisk skrivbörda kräver separat händelsemätning."""
    alla = [(t, b) for t in paket.tjanster for b in guideblock(t)]
    scenarier = {s.id for s in paket.gemensamma_scenarier}
    scenarier.update(s.id for t in paket.tjanster for s in t.scenarier)
    refs: list[str] = []

    def samla(data):
        if isinstance(data, dict):
            for k, v in data.items():
                if k.endswith('belagg') and isinstance(v, (tuple, list)):
                    refs.extend(v)
                else:
                    samla(v)
        elif isinstance(data, (tuple, list)):
            for v in data:
                samla(v)

    for t in paket.tjanster:
        samla(t.model_dump())
    return Arbetsborda(
        alltid=sum(b.obligatorisk for _, b in alla),
        villkorade=sum(not b.obligatorisk and b.aktivering == 'aktiv' for _, b in alla),
        unika_scenarier=len(scenarier),
        bekraftade_block=sum(b.bekraftad_summa == blocksumma(paket, t.tjanst, b.nummer)
                            for t, b in alla if b.bekraftad_summa),
        gemensamma_val=sum(k.bekraftad for t in paket.tjanster for k in t.scenariokopplingar),
        belaggsreferenser=len(refs),
        ateranvanda_belaggsreferenser=len(refs) - len(set(refs)),
    )
