"""Parametriserad leveranspresentation: fasta mallar attesteras, värden levereras."""
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from riskanalys.dokument.rapportpaket_v8 import Leverans
    from riskanalys.dokument.presentation_v8 import Presentation

Leveransdel = Literal['lasrapport', 'underlagsbilaga']
Leveransplacering = Literal['sidhuvud:status', 'start:titel', 'start:status_fet', 'start:inledning']


class Leveransmall(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')
    version: str = 'D-ARB-v8-leveransmall-1'
    filnamn: tuple[str, str] = ('allman-riskbedomning-{suffix}.docx', 'underlagsbilaga-{suffix}.docx')
    utkastsuffix: str = 'UTKAST'
    slutsuffix: str = 'v{version}'
    utkaststatus: str = 'UTKAST – ej fastställt av byrån. Skapat {datum}.'
    slutstatus: str = 'Fastställt av {organ} {datum}. Version {version}.'
    utkastversion: str = 'utkast {granskning}'
    slutversion: str = 'v{version}'
    inledning: str = ('Gemensam paketversion: {paketversion}. Bedömningsversion: {bedomning}. '
                     'Läs tillsammans med {andra} för fullständig dokumentation. '
                     'Båda delarna och deras gemensamma manifest utgör det verifierbara paketet.')
    placering: tuple[Leveransplacering, ...] = (
        'sidhuvud:status', 'start:titel', 'start:status_fet', 'start:inledning',
    )

    def filnamn_for(self, leverans: 'Leverans') -> tuple[str, str]:
        suffix = self.utkastsuffix if leverans.version is None else self.slutsuffix.format(version=leverans.version)
        return (self.filnamn[0].format(suffix=suffix), self.filnamn[1].format(suffix=suffix))

    def status_for(self, leverans: 'Leverans') -> str:
        mall = self.utkaststatus if leverans.version is None else self.slutstatus
        return mall.format(datum=leverans.datum.isoformat(), organ=leverans.organ, version=leverans.version)

    def inledning_for(self, leverans: 'Leverans', del_: Leveransdel) -> str:
        versionmall = self.utkastversion if leverans.version is None else self.slutversion
        paketversion = versionmall.format(granskning=leverans.granskning, version=leverans.version)
        andra = self.filnamn_for(leverans)[1 if del_ == 'lasrapport' else 0]
        return self.inledning.format(paketversion=paketversion, bedomning=leverans.bedomning, andra=andra)


# Det är modellens faktiska fält, inte bara versionsnamnet, som binds till granskningen.
LEVERANSMALL = Leveransmall()


def kontrollerad_leveransmall(presentation: 'Presentation | None') -> Leveransmall:
    """Ny rendering kräver dagens fasta policy i den granskade beskrivningen."""
    mall = presentation.leveransmall if presentation is not None else None
    if mall is None or mall != LEVERANSMALL:
        raise ValueError('Den fasta leveranspresentationen har ändrats. Granska båda delarna på nytt.')
    return mall
