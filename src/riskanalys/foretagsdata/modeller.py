"""Minimal, oföränderlig registerbild. Rårespons och nycklar lagras inte."""
from datetime import date, datetime
import hashlib
from zoneinfo import ZoneInfo
from typing import Literal
from riskanalys.foretagsdata.bokslut import Bokslut
from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator


class Bolagsverksbild(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)
    orgnr: str = Field(pattern=r'^[0-9]{10}$')
    hamtad: datetime
    namn: str | None = Field(default=None, max_length=500)
    organisationsform: str | None = Field(default=None, max_length=20)
    verksamhet: str | None = Field(default=None, max_length=12000)
    bakgrund: tuple[tuple[str, str], ...] = ()
    bokslut: Bokslut | None = None
    bokslutsnotis: str = ''


class Registerbild(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)
    schema_version: Literal[1, 2, 3, 4] = 1
    orgnr: str = Field(pattern=r'^[0-9]{10}$')
    namn: str = Field(min_length=1, max_length=500)
    lan: str | None = None
    arbetsstallen: int | None = Field(default=None, ge=0, strict=True)
    anstalldaklass: str | None = None
    omsattningsklass: str | None = None
    omsattningsar: int | None = Field(default=None, ge=1900, le=2100, strict=True)
    juridisk_form: str | None = None
    foretagsstatus: str | None = None
    sni: tuple[str, ...] = ()
    ursprung: Literal['scb_api', 'lokal_json']
    hamtad: datetime
    uppgiftsdatum: date | None = None
    kalla: Literal['https://apiafr.scb.se/scalar/'] = 'https://apiafr.scb.se/scalar/'

    fskatt_status: str | None = Field(default=None, pattern=r'^[0-9]$')
    moms_status: str | None = Field(default=None, pattern=r'^[0-9]$')
    arbetsgivar_status: str | None = Field(default=None, pattern=r'^[0-9]$')
    agarkontroll: str | None = Field(default=None, pattern=r'^[0-9]{2}$')

    bolagsverket: Bolagsverksbild | None = None

    @model_validator(mode='after')
    def versionsgrans(self):
        if self.schema_version==1 and any(v is not None for v in (self.fskatt_status,self.moms_status,self.arbetsgivar_status)):
            raise ValueError('Nya statusfält kräver registerschema 2.')
        if self.schema_version<3 and self.agarkontroll is not None:
            raise ValueError('Ägarkontroll kräver registerschema 3.')
        if self.bolagsverket and (self.schema_version != 4 or self.bolagsverket.orgnr != self.orgnr):
            raise ValueError('Bolagsverksunderlag kräver schema 4 och samma identitet.')
        return self

    @model_serializer(mode='wrap')
    def serialisera(self, handler):
        data=handler(self)
        if self.schema_version==1:
            for key in ('fskatt_status','moms_status','arbetsgivar_status'):
                data.pop(key,None)
        if self.schema_version<3:
            data.pop('agarkontroll',None)
        if self.schema_version < 4:
            data.pop('bolagsverket', None)
        return data

    @property
    def hamtningsdag(self) -> date:
        tider = [self.hamtad] + ([self.bolagsverket.hamtad] if self.bolagsverket else [])
        return max(t.astimezone(ZoneInfo('Europe/Stockholm')).date() for t in tider)

    def forslag(self) -> dict[str, str | int | bool]:
        resultat = {'P-ORG.namn': self.namn}
        if self.lan is not None:
            resultat['P-ORG.sateslan'] = self.lan
        if self.arbetsstallen is not None and self.arbetsstallen > 0:
            resultat['P-ORG.verksamhetsstallen'] = self.arbetsstallen
        # SCB:s företagsklassning utan koncern kan bara föreslå nej.
        # Medlemskap i koncern (42) styrker inte att företaget är yttersta moder.
        if self.agarkontroll == '41':
            resultat['P-ORG.koncernmoder'] = False
        if self.bolagsverket:
            bv = self.bolagsverket
            if bv.organisationsform in ('AB', 'FL'):
                resultat['P-ORG.utlandsk_filial'] = bv.organisationsform == 'FL'
            if bv.verksamhet:
                resultat['P-BESK.verksamhet'] = bv.verksamhet
            if bv.bokslut:
                resultat['P-VERK.omsattning'] = float(bv.bokslut.omsattning)
        return resultat

    @property
    def summa(self) -> str:
        return hashlib.sha256(self.model_dump_json().encode()).hexdigest()

    def hanvisning(self) -> str:
        ursprung = 'SCB AFR API' if self.ursprung == 'scb_api' else 'Lokalt importerat SCB-format (ursprung ej verifierat)'
        return f'{ursprung}; orgnr {self.orgnr}; hämtad/importerad {self.hamtad.isoformat()}; bild {self.summa}; {self.kalla}'

    def faltkalla(self, falt: str) -> str:
        if falt not in ('P-ORG.utlandsk_filial', 'P-BESK.verksamhet', 'P-VERK.omsattning') or not self.bolagsverket:
            return self.hanvisning()
        bv = self.bolagsverket
        text = f'Bolagsverket HVD; orgnr {self.orgnr}; hämtad {bv.hamtad.isoformat()}; bild {self.summa}'
        if falt == 'P-VERK.omsattning' and bv.bokslut:
            b = bv.bokslut
            text += f'; dokument {b.dokument_id}; SHA256 {b.sha256}; fil {b.fil}; kontext {b.kontext}; {b.taxonomi}; SEK'
        return text
