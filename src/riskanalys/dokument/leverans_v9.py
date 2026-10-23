"""Tre filer med granskade fasta mallar och begränsade leveransvärden."""
from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

DELAR=('resultatrapport','analysbilaga','underlagsbilaga')


class LeveransmallV9(BaseModel):
    model_config=ConfigDict(frozen=True,extra='forbid')
    version: str='D-ARB-v9-leveransmall-1'
    filnamn: tuple[str,str,str]=('allman-riskbedomning-{suffix}.docx','analysbilaga-{suffix}.docx','underlagsbilaga-{suffix}.docx')
    utkaststatus: str='UTKAST – ej fastställt av byrån. Skapat {datum}.'
    slutstatus: str='Fastställt av {organ} {datum}. Version {version}.'
    inledning: str=('Gemensam paketversion: {paketversion}. Bedömningsversion: {bedomning}. '
        'Granskningsversion: {granskning}. Läs tillsammans med {andra}. '
        'Alla tre delarna och deras gemensamma manifest utgör det verifierbara paketet.')
    utkastpaket: str='Utkastet blir verifierbart när det fastställs med alla tre delar och ett gemensamt manifest.'
    hanvisning: str='Se {fil}, avsnitt {avsnitt}.'

    def filnamn_for(self,l):
        suffix='UTKAST' if l.version is None else f'v{l.version}'
        return tuple(f.format(suffix=suffix) for f in self.filnamn)

    def status_for(self,l):
        return (self.utkaststatus if l.version is None else self.slutstatus).format(
            datum=l.datum.isoformat(),organ=l.organ,version=l.version)

    def inledning_for(self,l,del_):
        andra=[f for n,f in zip(DELAR,self.filnamn_for(l),strict=True) if n!=del_]
        mall=self.inledning if l.version is not None else self.inledning.replace(
            'Alla tre delarna och deras gemensamma manifest utgör det verifierbara paketet.',self.utkastpaket)
        return mall.format(paketversion='utkast' if l.version is None else f'v{l.version}',
            bedomning=l.bedomning,granskning=l.granskning,andra=' och '.join(andra))


LEVERANSMALL_V9=LeveransmallV9()


class LeveransV9(BaseModel):
    model_config=ConfigDict(frozen=True,extra='forbid')
    format: Literal['D-ARB-v9-leverans-1']='D-ARB-v9-leverans-1'
    datum: date
    bedomning: str=Field(min_length=1)
    granskning: str=Field(min_length=1)
    version: int|None=Field(default=None,ge=1)
    organ: str|None=None

    @model_validator(mode='after')
    def beslut(self):
        if (self.version is None)!=(self.organ is None) or self.organ is not None and not self.organ.strip():
            raise ValueError('Fastställd leverans kräver både version och beslutsorgan.')
        return self

    @property
    def filnamn(self):
        return LEVERANSMALL_V9.filnamn_for(self)

    @property
    def statusrad(self):
        return LEVERANSMALL_V9.status_for(self)
