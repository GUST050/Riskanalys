"""Typade lokala svar; ofullständiga utkast är tillåtna men aldrig attester."""
from datetime import date
from pathlib import PurePosixPath
from typing import Literal
import re

from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator
from riskanalys.profil.modeller import Period
from riskanalys.drift.modellrisk import Modellriskunderlag
from riskanalys.regelverk.modeller import Risk


class Fryst(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True, str_strip_whitespace=True)


class Analysbelagg(Fryst):
    id: str
    profilfalt: tuple[str, ...] = ()
    dokument: str | None = None
    kontrollsumma: str | None = None
    datum: date
    period: Period | None = None

    @model_validator(mode='after')
    def koppling(self):
        if bool(self.dokument) != bool(self.kontrollsumma):
            raise ValueError('Dokument och kontrollsumma måste anges tillsammans.')
        if not self.profilfalt and not self.dokument:
            raise ValueError('Ange bekräftade profilfält eller en privat dokumentkopia.')
        if self.dokument:
            p = PurePosixPath(self.dokument)
            if (p.is_absolute() or '..' in p.parts or '\\' in self.dokument or ':' in self.dokument
                    or not self.dokument or any(x in ('','.','..') for x in self.dokument.split('/'))):
                raise ValueError('Belägg måste vara en relativ fil under analys/belagg.')
            if not re.fullmatch(r'sha256:[0-9a-f]{64}', self.kontrollsumma or ''):
                raise ValueError('Ange dokumentets SHA256.')
        return self


class Delanalys(Fryst):
    id: str
    rubrik: str = ''
    arbetsmoment_och_befogenheter: str = ''
    belagg: tuple[str, ...] = ()


class Betalningsinsyn(Fryst):
    status: Literal['bedomd','ej_tillamplig','okand'] = 'okand'
    synliga_floden: str = ''
    insynsluckor: str = ''
    avsandare_och_mottagare: str = ''
    underlagens_tillforlitlighet: str = ''
    motivering: str = ''
    belagg: tuple[str, ...] = ()


class Uppdragsprovning(Fryst):
    status: Literal['hanterbart','kraver_atgard','kan_inte_hanteras','okant'] = 'okant'
    kompetens_och_insyn: str = ''
    motivering: str = ''
    handlingsalternativ: Literal['fortsatt','forstark','begransa','avboj','avsluta'] = 'fortsatt'
    beslutsstatus: Literal['forslag','beslutad'] = 'forslag'
    ansvar: str | None = None
    datum: date | None = None
    belagg: tuple[str, ...] = ()


class Leverantorsprovning(Fryst):
    id: str
    omfattning: str = ''
    leverantorens_kontroller: str = ''
    egen_verifiering: str = ''
    brister_och_motstridigheter: str = ''
    ansvar: str = ''
    belagg: tuple[str, ...] = ()


class Scenarioanalys(Fryst):
    id: str
    hot: tuple[str, ...] = ()
    rubrik: str = ''
    handelseforlopp: str = ''
    relevans: Literal['relevant','ej_relevant','okant'] = 'okant'
    motivering: str = ''
    belagg: tuple[str, ...] = ()
    delanalyser: tuple[str, ...] = ()


class Scenariokoppling(Fryst):
    scenario: str
    tillampning: Literal['samma','avviker']
    lokal_scenario: str | None = None
    motivering: str | None = None
    scenariosumma: str
    bekraftad: bool = False


class Sarbarhetsprovning(Fryst):
    id: str
    omrade: Literal['kund','kanal','geo','verk','tjanst']
    sarbarheter: tuple[str, ...] = ()
    scenarier: tuple[str, ...] = ()
    relevans: Literal['relevant','ej_relevant','okant'] = 'okant'
    motivering: str = ''
    belagg: tuple[str, ...] = ()


class Kontrollprovning(Fryst):
    scenario: str
    kontroll: str
    rackvidd: tuple[str, ...] = ()
    tillampning: str = ''
    utfall: str = ''
    belagg: tuple[str, ...] = ()
    tackning: Literal['bedomd_tillracklig','delvis','saknas','okand'] = 'okand'
    kvarstar: str = ''


class Rutinatgard(Fryst):
    id: str
    scenarier: tuple[str, ...] = ()
    atgard: str = ''
    rutin_id: str | None = None
    rutin_version: str | None = None
    rutinbelagg: str | None = None
    status: Literal['foreslagen','beslutad','genomford'] = 'foreslagen'
    ansvar: str | None = None
    utlosare_eller_frekvens: str = ''
    uppfoljning: date | None = None
    belagg: tuple[str, ...] = ()
    klart_nar: str = ''
    prioritet: Literal['ej_beslutad','hög','medel','låg'] = 'ej_beslutad'

    @model_serializer(mode='wrap')
    def _historiskt_format(self, handler):
        """Ej ifyllda nya fält utelämnas, så att äldre poster behåller sina bytes och kontrollsummor."""
        data = handler(self)
        if self.klart_nar == '':
            data.pop('klart_nar', None)
        if self.prioritet == 'ej_beslutad':
            data.pop('prioritet', None)
        return data


class Analysgap(Fryst):
    id: str
    typ: Literal['kunskapslucka','kontrollbrist','motstridigt_underlag','metodkonflikt']
    beskrivning: str = ''
    status: Literal['oppet','atgardat','accepterad_kvarstaende_risk'] = 'oppet'
    motivering: str = ''
    ansvar: str | None = None
    tidsfrist: date | None = None
    belagg: tuple[str, ...] = ()


class Analysblock(Fryst):
    nummer: int = Field(ge=1,le=16)
    aktivering: Literal['aktiv','ej_tillamplig','okand']
    motivering: str = ''
    bekraftad_summa: str | None = None


class GemensamSarbarhetsprovning(Fryst):
    id: str = Field(min_length=1, max_length=120)
    omrade: Literal['kund','kanal','geo','verk']
    sarbarheter: tuple[str, ...] = ()
    beskrivning: str = ''
    profilfalt: tuple[str, ...] = ()
    hot: tuple[str, ...] = ()
    dimension: Literal['pt','tf','bada'] = 'bada'
    relevans: Literal['relevant','ej_relevant','okant'] = 'okant'
    motivering: str = ''
    belagg: tuple[str, ...] = ()
    status: Literal['bekraftad','antagande','kunskapslucka'] = 'antagande'
    forfattare: str | None = None


class GemensamVerksamhetspost(Fryst):
    id: str = Field(min_length=1, max_length=120)
    slag: Literal['leverantorer','erfarenhet','sanktionsanknytning']
    text: str = ''
    belagg: tuple[str, ...] = ()
    status: Literal['bekraftad','antagande','kunskapslucka'] = 'antagande'
    forfattare: str | None = None
    leverantorer: tuple[Leverantorsprovning, ...] = ()

    @model_validator(mode='after')
    def leverantorslista(self):
        if self.leverantorer and self.slag!='leverantorer':
            raise ValueError('Leverantörslistan hör bara till leverantörsposten.')
        _unika(self.leverantorer)
        return self


class GemensamReferens(Fryst):
    slag: Literal['sarbarhet','verksamhet']
    post: str = Field(min_length=1)
    summa: str = Field(pattern=r'^sha256:[0-9a-f]{64}$')


class GemensamTillampning(Fryst):
    post: str = Field(min_length=1)
    stallningstagande: Literal['galler','galler_annorlunda','beror_inte','otillrackligt']
    motivering: str = ''
    belagg: tuple[str, ...] = ()
    postsumma: str = Field(pattern=r'^sha256:[0-9a-f]{64}$')
    bekraftad: bool = False


class Riktningsval(Fryst):
    riktning: Literal['lagre','mojlig_underskattning','oklar'] = 'oklar'
    motivering: str = ''
    belagg: tuple[str, ...] = ()


class Hotanknytning(Fryst):
    hot: str = Field(min_length=1)
    dimension: Literal['pt','tf']


class Sarbarhetstillampning(GemensamTillampning):
    riktningsval: Riktningsval | None = None
    hotkopplingar: tuple[Hotanknytning, ...] = ()

    @model_validator(mode='after')
    def riktning_och_koppling(self):
        if self.riktningsval is not None and self.stallningstagande!='galler_annorlunda':
            raise ValueError('Manuellt riktningsval hör bara till gäller annorlunda.')
        if len({(h.hot,h.dimension) for h in self.hotkopplingar})!=len(self.hotkopplingar):
            raise ValueError('Ange varje uttrycklig hot-/dimensionskoppling högst en gång.')
        return self


class Tackningsprovning(Fryst):
    ursprung: Literal['gemensam','lokal']
    post: str = Field(min_length=1)
    hot: str = Field(min_length=1)
    dimension: Literal['pt','tf']
    stallningstagande: Literal['tacks_av_scenario','tacks_inte','oklar'] = 'oklar'
    lokalt_scenario: str | None = None
    riskled: Literal['inneboende','kvarstaende'] = 'inneboende'
    jamforelseniva: Risk | None = None
    motivering: str = ''
    belagg: tuple[str, ...] = ()
    forfattare: str | None = None
    visad_summa: str | None = Field(default=None, pattern=r'^sha256:[0-9a-f]{64}$')
    referensmotivering: str = ''


NYA_TJANSTFALT = ('sarbarhetstillampningar','verksamhetstillampningar','tackningsprovningar')


class Tjansteanalys(Fryst):
    tjanst: str
    forfattare: str | None = None
    block: tuple[Analysblock, ...] = ()
    exponering: str = ''
    exponeringsbelagg: tuple[str, ...] = ()
    delningsmotivering: str = ''
    delanalyser: tuple[Delanalys, ...] = ()
    betalningsinsyn: Betalningsinsyn = Betalningsinsyn()
    uppdragsprovning: Uppdragsprovning = Uppdragsprovning()
    leverantorsmotivering: str = ''
    leverantorer: tuple[Leverantorsprovning, ...] = ()
    scenarier: tuple[Scenarioanalys, ...] = ()
    scenariokopplingar: tuple[Scenariokoppling, ...] = ()
    sarbarhetsprovningar: tuple[Sarbarhetsprovning, ...] = ()
    kontroller: tuple[Kontrollprovning, ...] = ()
    samverkan: str = ''
    erfarenhetsprovning: str = ''
    erfarenhetsbelagg: tuple[str, ...] = ()
    pt_motivering: str = ''
    tf_motivering: str = ''
    reduktionsprovning: Literal['ej_reduktion','motiverad','metodkonflikt','okand'] = 'okand'
    reduktionsmotivering: str = ''
    sektorsjamforelse: str = ''
    sanktioner: str = ''
    slutsats: str = ''
    rutinatgarder: tuple[Rutinatgard, ...] = ()
    gap: tuple[Analysgap, ...] = ()
    sarbarhetstillampningar: tuple[Sarbarhetstillampning, ...] = ()
    verksamhetstillampningar: tuple[GemensamTillampning, ...] = ()
    tackningsprovningar: tuple[Tackningsprovning, ...] = ()

    @model_serializer(mode='wrap')
    def historiska_svar(self, handler):
        data=handler(self)
        for falt in NYA_TJANSTFALT:
            if not getattr(self,falt):
                data.pop(falt,None)
        return data

    @model_validator(mode='after')
    def unika(self):
        _unika(self.block, 'nummer')
        for namn in ('scenarier','delanalyser','sarbarhetsprovningar','leverantorer','rutinatgarder','gap'):
            _unika(getattr(self,namn))
        _unika(self.scenariokopplingar,'scenario')
        _unika(self.sarbarhetstillampningar,'post')
        _unika(self.verksamhetstillampningar,'post')
        ids=[(p.ursprung,p.post,p.hot,p.dimension,p.riskled) for p in self.tackningsprovningar]
        if len(ids)!=len(set(ids)):
            raise ValueError('Ange varje täckningsprövning högst en gång.')
        return self


BINDNINGSVERSION = 2


class Analysbindning(Fryst):
    """Version 1 binder även AI-utkastet; version 2 binder bara sakunderlaget.

    Ny AI-text prövas i stället genom sakgranskningen av den renderade texten. Version 1
    serialiseras byteidentiskt med tidigare paket och uppgraderas aldrig automatiskt.
    """
    byra: str
    profilrevision: str
    bedomningsmanifest: str
    utkastmanifest: str | None = None
    regelbas: str
    kallunderlag: str
    historik: str
    bedomningsdatum: date
    modell: str
    bindningsversion: Literal[1, 2] = 1

    @model_validator(mode='after')
    def utkast_efter_version(self):
        if (self.bindningsversion == 1) != (self.utkastmanifest is not None):
            raise ValueError('Bindningsversion 1 kräver AI-utkastets manifest; version 2 får inte ha det.')
        return self

    @model_serializer(mode='wrap')
    def _historiskt_format(self, handler):
        data = handler(self)
        data.pop('bindningsversion' if self.bindningsversion == 1 else 'utkastmanifest', None)
        return data


class Analysbeslut(Fryst):
    tjanst: str
    revision: int = Field(ge=1)
    underlagssumma: str
    svarssumma: str
    godkand: bool
    namn: str
    roll: str
    datum: date
    kommentar: str | None = None
    forfattare: str = ''
    egen_granskning: bool = False

    @model_validator(mode='after')
    def identitet(self):
        if not self.namn or not self.roll or (not self.godkand and not self.kommentar):
            raise ValueError('Ange namn, roll och kommentar vid underkännande.')
        return self


class Analyspaket(Fryst):
    schemaversion: Literal[1,2] = 1
    revision: int = Field(default=1,ge=1)
    bindning: Analysbindning
    belagg: tuple[Analysbelagg, ...] = ()
    gemensamma_scenarier: tuple[Scenarioanalys, ...] = ()
    tjanster: tuple[Tjansteanalys, ...] = ()
    beslut: tuple[Analysbeslut, ...] = ()
    modellrisk: Modellriskunderlag | None = None
    gemensamma_sarbarhetsprovningar: tuple[GemensamSarbarhetsprovning, ...] = ()
    gemensamma_verksamhetsposter: tuple[GemensamVerksamhetspost, ...] = ()

    @model_serializer(mode='wrap')
    def historiskt_kontrakt(self, handler, info):
        data=handler(self)
        if self.schemaversion==1:
            data.pop('gemensamma_sarbarhetsprovningar',None)
            data.pop('gemensamma_verksamhetsposter',None)
        elif ('tjanster' in data and info.include is None
              and not (isinstance(info.exclude, dict) and 'tjanster' in info.exclude)):
            # Fyll bara schemafält vid full serialisering, aldrig utelämnade privata fält.
            for t,rad in zip(self.tjanster,data['tjanster'],strict=True):
                for falt in NYA_TJANSTFALT:
                    rad[falt]=[x.model_dump(mode='json') for x in getattr(t,falt)]
        return data

    @model_validator(mode='after')
    def unika(self):
        if self.schemaversion==1 and (self.gemensamma_sarbarhetsprovningar or self.gemensamma_verksamhetsposter
                or any(getattr(t,f) for t in self.tjanster for f in NYA_TJANSTFALT)):
            raise ValueError('Schema 1 får inte innehålla svar från schema 2. Överför analysen uttryckligen.')
        _unika(self.gemensamma_sarbarhetsprovningar)
        _unika(self.gemensamma_verksamhetsposter)
        _unika(self.gemensamma_verksamhetsposter,'slag')
        _unika(self.belagg)
        _unika(self.gemensamma_scenarier)
        _unika(self.tjanster,'tjanst')
        ids=[s.id for s in self.gemensamma_scenarier]
        ids += [s.id for t in self.tjanster for s in t.scenarier]
        if len(ids)!=len(set(ids)):
            raise ValueError('Scenario-ID måste vara unika i paketet.')
        if any(s.delanalyser for s in self.gemensamma_scenarier):
            raise ValueError('Gemensamma scenarier får inte ha tjänstespecifika delanalyser.')
        return self


def _unika(poster, falt='id'):
    ids=[getattr(p,falt) for p in poster]
    if len(ids)!=len(set(ids)) or any(isinstance(id,str) and not id for id in ids):
        raise ValueError(f'Ange unika, icke-tomma {falt}.')
