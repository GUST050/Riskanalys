"""Datamodeller för regelbasen (spec avsnitt 6)."""

import json
from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_serializer, model_validator

from riskanalys.lagring.kontrollsumma import for_text
from riskanalys.regelverk.villkor import Faltdef

Grund = Literal["ska_krav", "allmänt_råd", "tillsynspraxis", "eu_utkast", "metodval"]
Sannolikhet = Literal["låg", "medel", "hög"]
Konsekvens = Literal["begränsad", "betydande", "allvarlig"]
Risk = Literal["låg", "måttlig", "hög", "mycket hög"]
Allvar = Literal["blockerande", "hög", "medel", "låg"]
Belagg = Literal["dokument", "datum", "logg", "beslut", "register"]
Dimension = Literal["pt", "tf"]
KONTROLLSUMMA = r"^sha256:[0-9a-f]{64}$"
KALLANS_GILTIGHET = frozenset({"id", "typ", "utgivare", "geografi", "beslutad", "konsoliderad_tom", "kontrollsumma", "galler_fran", "galler_till", "inventarium_kontrollsumma"})


class Strikt(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Intagsfalt(Strikt):
    """Frågens syfte och ordning; kopplingen är inget intyg om kravuppfyllelse."""

    grupp: str
    ordning: int = Field(ge=0)
    krav: tuple[str, ...] = ()
    avsnitt: tuple[str, ...] = Field(min_length=1)
    kallor: tuple[str, ...] = Field(min_length=1)
    obligatorisk: bool = True
    beroenden: tuple[str, ...] = ()
    grund: Literal["metodval"] = "metodval"


class Falt(Strikt):
    id: str
    typ: Literal["bool", "heltal", "tal", "andel", "text", "val", "flerval", "datum"]
    fraga: str
    varfor: str
    personuppgift: bool = False
    namnfalt: bool = False  # Namn som prövas lokalt (spec 8.4.10 punkt 7).
    kritisk: bool = False
    smagrupp: bool = False
    smagruppsantal: str | None = None
    periodkrav: bool = False
    basfalt: str | None = None
    antalfalt: str | None = None
    kritisk_om: dict[str, Any] | None = None
    intag: Intagsfalt | None = None
    alias_for: str | None = None
    enhet: str | None = None
    etikett: str | None = None  # Kortnamn i löptext; visningstext som inte ändrar någon regel (spec 8.4.9).
    val: tuple[str, ...] = ()

    @model_serializer(mode="wrap")
    def serialisera(self, handler):
        """Utelämna saknat kortnamn och osatt namnfält, så att historiska innehålls- och attestsummor består."""
        data = handler(self)
        if self.etikett is None:
            data.pop("etikett", None)
        if not self.namnfalt:
            data.pop("namnfalt", None)
        return data

    @model_validator(mode="after")
    def _namnfalt_ar_personuppgift(self):
        if self.namnfalt and not (self.personuppgift and self.typ == "text"):
            raise ValueError(f"{self.id}: ett namnfält måste vara en personuppgift av typen text.")
        return self

    @model_validator(mode="after")
    def _flerval_har_alternativ(self):
        if self.typ == "flerval" and not self.val:
            raise ValueError(f"{self.id}: ett fält av typen flerval måste ange sina alternativ i val.")
        return self

    @model_validator(mode="after")
    def _flerval_blockerar_aldrig(self):
        """Ett flervalsfält är en frivillig lokal iakttagelse: aldrig kritiskt, aldrig ett obligatoriskt intagssvar.

        kritisk_om får finnas; det styr bara när frågan visas, till exempel först när tjänsten erbjuds.
        """
        if self.typ != "flerval":
            return self
        if self.kritisk or (self.intag is not None and self.intag.obligatorisk):
            raise ValueError(
                f"{self.id}: ett fält av typen flerval får inte vara kritiskt eller obligatoriskt. "
                "Ta bort kritisk och sätt intag.obligatorisk till false."
            )
        return self


class Kalla(Strikt):
    id: str
    titel: str
    typ: Literal[
        "lag",
        "förordning",
        "föreskrift",
        "allmänt_råd",
        "vägledning",
        "tillsynsrapport",
        "riskbedömning",
        "beslut",
        "eu_förordning",
        "eu_riktlinje_utkast",
    ]
    utgivare: str
    url: str
    hamtad: date
    geografi: tuple[str, ...] = ()
    beslutad: date | None = None
    konsoliderad_tom: str | None = None
    kontrollsumma: str | None = None
    paragrafer: tuple[str, ...] = ()
    galler_fran: date | None = None
    galler_till: date | None = None
    inventarium_kontrollsumma: str | None = Field(default=None, pattern=KONTROLLSUMMA)


class InventeradLydelse(Strikt):
    """Oberoende inventeringspost; okänt datum får inte gissas från lagens ursprung."""

    kalla: str
    lagrum: str
    text: str = Field(min_length=1)
    ikraft: date | None = None
    upphor: date | None = None
    inford_genom: str | None = None


class Lydelse(Strikt):
    id: str
    kalla: str
    lagrum: str
    ikraft: date
    upphor: date | None = None
    inford_genom: str | None = None
    primarkalla: str
    text_kontrollsumma: str = Field(pattern=KONTROLLSUMMA)


class Sakkunnig(Strikt):
    """Sakkunnig granskning. Status verifierad gäller bara det innehåll som kontrollsumman beskriver."""

    status: Literal["ej_granskad", "verifierad", "ändras"] = "ej_granskad"
    av: str | None = None
    datum: date | None = None
    kontrollsumma: str | None = None

    def galler(self, innehallssumma: str) -> bool:
        return self.status == "verifierad" and self.kontrollsumma == innehallssumma


class Kravmal(Strikt):
    typ: Literal["dokument", "drift", "kundmall"]
    id: str
    etapp: str


class Maldefinition(Kravmal):
    beskrivning: str


class Krav(Strikt):
    id: str
    kalla: str
    lagrum: str
    lydelser: tuple[str, ...] = Field(min_length=1)
    grund: Grund
    text: str
    galler_om: dict[str, Any]
    belagg: tuple[Belagg, ...] = Field(min_length=1)
    uppfylls_i: tuple[str, ...] = ()
    mal: tuple[Kravmal, ...] = ()
    ikraft: date | None = None
    upphor: date | None = None
    sakkunnig: Sakkunnig = Sakkunnig()


class Kallhanvisning(Strikt):
    kalla: str
    avsnitt: str
    sida: int = Field(ge=1)


class Hot(Strikt):
    sakkunnig: Sakkunnig = Sakkunnig()
    grund: Grund = "metodval"
    kallhanvisningar: tuple[Kallhanvisning, ...] = ()
    id: str
    namn: str
    beskrivning: str
    kallor: tuple[str, ...] = Field(min_length=1)
    galler_tf: bool = False
    # Scenariometod (spec 2026-10-18): hotnivå och dimensioner. Tomma värden utelämnas vid serialisering.
    niva: Sannolikhet | None = None
    nivamotivering: str = ""
    dimensioner: tuple[Dimension, ...] = ()

    @field_validator("dimensioner")
    @classmethod
    def _unika_dimensioner(cls, varde: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(varde)) != len(varde):
            raise ValueError("Ange varje dimension, pt eller tf, högst en gång.")
        return varde

    @model_serializer(mode="wrap")
    def serialisera(self, handler):
        """Utelämna osatta scenariofält, så att historiska innehålls- och attestsummor består."""
        data = handler(self)
        if self.niva is None:
            data.pop("niva", None)
        if not self.nivamotivering:
            data.pop("nivamotivering", None)
        if not self.dimensioner:
            data.pop("dimensioner", None)
        return data


TF_HOTPREFIX = "H-TF-"


def hot_dimensioner(hot: Hot) -> tuple[str, ...]:
    """Hotets dimensioner: angivna, annars härledda ur hot-ID och galler_tf."""
    if hot.dimensioner:
        return hot.dimensioner
    if hot.id.startswith(TF_HOTPREFIX):
        return ("tf",)
    return ("pt", "tf") if hot.galler_tf else ("pt",)


class Effekt(Strikt):
    sannolikhet: int = Field(ge=-2, le=2)

    @field_validator("sannolikhet")
    @classmethod
    def _inte_noll(cls, varde: int) -> int:
        if varde == 0:
            raise ValueError("Effekten får inte vara 0. Ange −2, −1, 1 eller 2, eller ta bort sårbarheten.")
        return varde


class Sarbarhet(Strikt):
    beskrivning: str = ""
    metodmotivering: str = ""
    sakkunnig: Sakkunnig = Sakkunnig()
    kallhanvisningar: tuple[Kallhanvisning, ...] = ()
    ersatter: tuple[str, ...] = ()
    id: str
    namn: str
    omrade: Literal["kund", "kanal", "geo", "verk", "tj"]
    grund: Grund
    villkor: dict[str, Any]
    vid_okant: Literal["preliminart_galler", "preliminart_galler_ej"] = "preliminart_galler"
    effekt: Effekt
    galler: Literal["penningtvatt", "terrorfinansiering", "bada"] = "penningtvatt"
    kallor: tuple[str, ...] = Field(min_length=1)
    hot: tuple[str, ...] = ()  # Hot som sårbarheten möjliggör i scenariometoden.

    @model_serializer(mode="wrap")
    def serialisera(self, handler):
        """Tom hotkoppling får inte ändra historiska innehålls- eller attestsummor."""
        data = handler(self)
        if not self.hot:
            data.pop("hot", None)
        return data


class Kontrollrackvidd(Strikt):
    """Källbunden möjlig observation, inte belägg för aktuell kontroll eller effekt."""

    id: str
    tjanst: str
    hot: tuple[str, ...] = Field(min_length=1)
    kan_belagga: str
    begransningar: str
    forutsattningar: str
    grund: Grund
    kallhanvisningar: tuple[Kallhanvisning, ...] = Field(min_length=1)
    sakkunnig: Sakkunnig = Sakkunnig()
    # Kunskapsstatus om beskrivningen, aldrig positiv scenariotäckning eller lokal effekt.
    beskrivningsstatus: Literal["beskriven", "okand"] | None = None

    @model_serializer(mode="wrap")
    def serialisera(self, handler):
        """Bevara äldre räckviddspayloads och deras attestsummor vid oangiven status."""
        data = handler(self)
        if self.beskrivningsstatus is None:
            data.pop("beskrivningsstatus", None)
        return data


    @field_validator("id", "tjanst", "kan_belagga", "begransningar", "forutsattningar")
    @classmethod
    def _saktext(cls, varde: str) -> str:
        import re

        text = varde.strip()
        if not text or re.search(r"\[(?:KOMPLETTERA|VERIFIERA|FYLL I)[^\]]*\]", text, re.IGNORECASE):
            raise ValueError("Ange saklig räckvidd utan tomma svar eller kompletteringsmarkörer.")
        return text

    @field_validator("hot")
    @classmethod
    def _hot_id(cls, varde: tuple[str, ...]) -> tuple[str, ...]:
        ids = tuple(id.strip() for id in varde)
        if any(not id for id in ids) or len(set(ids)) != len(ids):
            raise ValueError("Ange unika, icke-tomma hot-ID:n.")
        return ids


class Riktning(Strikt):
    """Katalogens mål för en kontroll: de hot i en tjänst som kontrollen är utformad mot.

    Skild från räckvidden, som bara beskriver vad kontrollen kan observera.
    """

    tjanst: str
    hot: tuple[str, ...] = Field(min_length=1)
    kallor: tuple[str, ...] = Field(min_length=1)
    grund: Grund
    motivering: str


class Kontroll(Strikt):
    rackvidd: tuple[Kontrollrackvidd, ...] = ()
    riktar_sig_mot: tuple[Riktning, ...] = ()
    effekt_falt: str | None = None
    utfall_falt: str | None = None
    sakkunnig: Sakkunnig = Sakkunnig()
    grund: Grund = "metodval"
    kallhanvisningar: tuple[Kallhanvisning, ...] = ()
    id: str
    namn: str
    beskrivning: str
    utformning_falt: str
    genomforande_falt: str
    kallor: tuple[str, ...] = ()


    @model_serializer(mode="wrap")
    def serialisera(self, handler):
        """Tom räckvidd eller riktning får inte ändra historiska innehålls- eller attestsummor."""
        data = handler(self)
        if not self.rackvidd:
            data.pop("rackvidd", None)
        if not self.riktar_sig_mot:
            data.pop("riktar_sig_mot", None)
        return data


class Tjanst(Strikt):
    sakkunnig: Sakkunnig = Sakkunnig()
    grund: Grund = "metodval"
    kallhanvisningar: tuple[Kallhanvisning, ...] = ()
    kompatibilitetsfalt: tuple[str, ...] = ()
    metodmotivering: str = ""
    sektorreferens: str | None = None
    id: str
    namn: str
    sektor: str
    beskrivning: str
    erbjuds_falt: str
    hot: tuple[str, ...] = Field(min_length=1)
    sarbarheter: tuple[str, ...] = ()
    kontroller: tuple[str, ...] = ()
    grund_sannolikhet: Sannolikhet
    grund_konsekvens: Konsekvens
    grund_tf_sannolikhet: Sannolikhet
    kallor: tuple[str, ...] = Field(min_length=1)


class Bristmonster(Strikt):
    id: str
    namn: str
    upptacks: str
    automatiserad: bool
    allvar: Allvar
    grund: Grund
    kallor: tuple[str, ...] = Field(min_length=1)


class MatrisRad(Strikt):
    sakkunnig: Sakkunnig = Sakkunnig()
    id: str
    sannolikhet: Sannolikhet
    konsekvens: Konsekvens
    risk: Risk
    grund: Grund
    forklaring: str


class Regel(Strikt):
    sakkunnig: Sakkunnig = Sakkunnig()
    id: str
    grund: Grund
    forklaring: str


class Sannolikhetsrad(Regel):
    """En cell i scenariometodens sannolikhetsmatris (hotnivå × sårbarhetsnivå)."""

    hot: Sannolikhet
    sarbarhet: Sannolikhet
    sannolikhet: Sannolikhet


class Scenariometod(Strikt):
    hotniva: Regel
    sarbarhetsniva: Regel
    sannolikhetsmatris: tuple[Sannolikhetsrad, ...]
    kvarstaende: Regel
    aggregering: Regel

    def regler(self) -> tuple[Regel, ...]:
        return (self.hotniva, self.sarbarhetsniva, *self.sannolikhetsmatris, self.kvarstaende, self.aggregering)


class Tillamplighetsrad(Strikt):
    id: str
    punkt: int = Field(ge=18, le=23)
    villkor: dict[str, Any]
    grund: Literal["ska_krav"] = "ska_krav"
    lydelser: tuple[str, ...] = Field(min_length=1)
    forklaring: str


class Omfattningsmetod(Regel):
    kallor: tuple[str, ...] = Field(min_length=1)
    enkel_villkor: dict[str, Any]
    utokad_villkor: dict[str, Any]


class Metod(Strikt):
    omfattning: Omfattningsmetod | None = None
    riskmatris: tuple[MatrisRad, ...]
    sannolikhet: Regel
    konsekvens: Regel
    terrorfinansiering: Regel
    kvarstaende_ej_belagd: Regel
    kvarstaende_sankning: Regel
    scenario: Scenariometod | None = None

    @model_serializer(mode="wrap")
    def serialisera(self, handler):
        """Saknad scenariometod får inte ändra historiska innehållssummor."""
        data = handler(self)
        if self.scenario is None:
            data.pop("scenario", None)
        return data

    def regler(self) -> tuple[Regel, ...]:
        return (
            self.sannolikhet,
            self.konsekvens,
            self.terrorfinansiering,
            self.kvarstaende_ej_belagd,
            self.kvarstaende_sankning,
        ) + ((self.omfattning,) if self.omfattning else ()) + (self.scenario.regler() if self.scenario else ())


class Tillatelselista(Strikt):
    id: str
    falt: tuple[str, ...]
    undvik: tuple[str, ...] = ()


class Kartrad(Strikt):
    """En paragraf på paragrafkartan: de krav den ger upphov till, eller varför den inte gäller sektorn.

    En rad utan krav och utan motivering är en paragraf som regelbasen ännu inte hanterar.
    """

    kalla: str
    lagrum: str
    krav: tuple[str, ...] = ()
    ej_tillamplig: str | None = None
    hantering: str | None = None

    @property
    def hanterad(self) -> bool:
        return bool(self.krav) or bool(self.ej_tillamplig) or bool(self.hantering)


class Kartomfattning(Strikt):
    """Vilka kapitel i en källa som kartan ska täcka, till exempel 2 kap. i 14FS 2024:11."""

    kalla: str
    kapitel: tuple[str, ...] = Field(min_length=1)


class Paragrafkarta(Strikt):
    """Varje paragraf i de relevanta kapitlen för ett datumintervall (spec 16.1)."""

    giltig_fran: date
    giltig_till: date | None = None
    omfattning: tuple[Kartomfattning, ...] = Field(min_length=1)
    rader: tuple[Kartrad, ...] = Field(min_length=1)
    sakkunnig: Sakkunnig = Sakkunnig()

    def galler(self, datum: date) -> bool:
        return self.giltig_fran <= datum and (self.giltig_till is None or datum < self.giltig_till)

    def ohanterade(self) -> tuple[Kartrad, ...]:
        return tuple(rad for rad in self.rader if not rad.hanterad)


class Regelpaket(Strikt):
    granskning: Sakkunnig = Sakkunnig()
    id: str
    namn: str
    sektor: str
    lan: tuple[str, ...] = Field(min_length=1)
    kallor: tuple[str, ...]
    krav: tuple[str, ...] = Field(min_length=1)
    tjanster: tuple[str, ...] = Field(min_length=1)
    paragrafkarta: Paragrafkarta


class Sektorsreferens(Strikt):
    id: str
    sektor: str
    niva: str
    skala: tuple[str, ...]
    kalla: str
    sida: int
    referensversion: str


class Skalmappning(Strikt):
    id: str
    grund: Literal["metodval"] = "metodval"
    mappning: dict[str, Risk]
    forklaring: str
    sakkunnig: Sakkunnig = Sakkunnig()


class Sanktionsrad(Strikt):
    id: str
    villkor: dict[str, Any]
    sannolikhet: Sannolikhet
    grund: Literal["metodval"] = "metodval"
    forklaring: str
    kallor: tuple[str, ...]


class Sanktionsmetod(Strikt):
    id: str
    grund: Literal["metodval"] = "metodval"
    grund_sannolikhet: Sannolikhet
    grund_konsekvens: Konsekvens
    kontroll: str
    rader: tuple[Sanktionsrad, ...]
    forklaring: str
    kallor: tuple[str, ...]
    sakkunnig: Sakkunnig = Sakkunnig()


class Kundrad(Strikt):
    id: str
    spar: Literal["A", "B", "C", "D"]
    villkor: dict[str, Any]
    utfall: dict[str, Any]
    grund: Grund
    lydelser: tuple[str, ...]
    forklaring: str
    ikraft: date | None = None
    upphor: date | None = None
    sakkunnig: Sakkunnig = Sakkunnig()

    @model_validator(mode="after")
    def typat_utfall(self):
        nyckel = {"A": "beslut", "B": "atgarder", "C": "risk", "D": "beslut"}[self.spar]
        if set(self.utfall) != {nyckel}:
            raise ValueError(f"Spår {self.spar} kräver endast {nyckel}.")
        varde = self.utfall[nyckel]
        if self.spar == "B":
            if not isinstance(varde, list) or not varde or any(not isinstance(i, str) or not i.startswith("KB-") for i in varde):
                raise ValueError("B kräver en lista av definierade KB-åtgärds-ID:n.")
        else:
            tillatna = {"A": {"tillatet", "stopp", "undantag", "preliminart"},
                        "C": {"låg", "normal", "hög", "preliminär"},
                        "D": {"rapportera", "undantag", "ingen_skalig_misstanke", "preliminart"}}
            if not isinstance(varde, str) or varde not in tillatna[self.spar]:
                raise ValueError(f"Ogiltigt utfall för {self.spar}.")
        if self.grund == "ska_krav" and not self.lydelser:
            raise ValueError("Bindande kundrad kräver rättslig lydelse.")
        if self.ikraft and self.upphor and self.ikraft >= self.upphor:
            raise ValueError("Kundradens upphörande ska vara efter ikraftträdande.")
        return self


class Kundmall(Strikt):
    falt: dict[str, Falt]
    rader: tuple[Kundrad, ...]
    lydelser: dict[str, Lydelse] = {}
    atgarder: dict[str, str] = {}
    c_granskning: Sakkunnig = Sakkunnig()
    c_metodforslag: str = "Ingen produktionsformel är frigiven; kompletteras och valideras av sakkunnig."

    def c_innehallssumma(self) -> str:
        return _summa({"falt": {k: f.model_dump(mode="json") for k, f in sorted(self.falt.items())},
                       "rader": [r.model_dump(mode="json", exclude={"sakkunnig"}) for r in self.rader if r.spar == "C"],
                       "metodforslag": self.c_metodforslag})


class Regelbas(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: str = Field(pattern=r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
    falt: dict[str, Falt]
    kallor: dict[str, Kalla]
    lydelser: dict[str, Lydelse]
    krav: dict[str, Krav]
    hot: dict[str, Hot]
    sarbarheter: dict[str, Sarbarhet]
    kontroller: dict[str, Kontroll]
    tjanster: dict[str, Tjanst]
    bristmonster: dict[str, Bristmonster]
    metod: Metod
    tillatelselistor: dict[str, Tillatelselista]
    regelpaket: dict[str, Regelpaket]
    kontrollsumma: str
    inventarium: tuple[InventeradLydelse, ...] = ()
    tillamplighet: dict[str, Tillamplighetsrad] = {}
    maldefinitioner: dict[str, Maldefinition] = {}
    sektorsreferenser: dict[str, Sektorsreferens] = {}
    skalmappning: Skalmappning | None = None
    sanktionsmetod: Sanktionsmetod | None = None
    kundmall: Kundmall | None = None
    facit: dict[str, Any] | None = None

    @property
    def utokade_krav(self) -> bool:
        """M2:s skydd gäller alla senare innehållsversioner, även 2.x och 10.x."""
        return int(self.version.split(".")[0]) >= 1

    def paketets_innehallssumma(self, paket_id: str) -> str:
        """Konservativ bindning: gemensam regelbas plus valt paket, utan attestmetadata."""
        if paket_id not in self.regelpaket:
            from riskanalys.fel import RiskanalysFel
            raise RiskanalysFel(f"Okänt regelpaket {paket_id}. Välj ett befintligt paket och exportera en ny granskningsmall.")
        data = self.model_dump(mode="json", exclude={"kontrollsumma", "regelpaket", "facit"})
        data["regelpaket"] = self.regelpaket[paket_id].model_dump(mode="json")
        return _summa(utan_granskningsmetadata(data))

    def faltdefinitioner(self) -> dict[str, Faltdef]:
        return {falt.id: Faltdef(falt.id, falt.typ, falt.val) for falt in self.falt.values()}

    def alla_id(self) -> set[str]:
        """Alla ID:n som text i ett dokument får hänvisa till."""
        samlingar = (
            self.falt,
            self.kallor,
            self.lydelser,
            self.krav,
            self.hot,
            self.sarbarheter,
            self.kontroller,
            self.tjanster,
            self.bristmonster,
            self.tillamplighet,
            self.sektorsreferenser,
        )
        alla = {nyckel for samling in samlingar for nyckel in samling}
        alla |= {r.id for k in self.kontroller.values() for r in k.rackvidd}
        alla |= {rad.id for rad in self.metod.riskmatris}
        alla |= {regel.id for regel in self.metod.regler()}
        if self.skalmappning:
            alla.add(self.skalmappning.id)
        if self.sanktionsmetod:
            alla.add(self.sanktionsmetod.id)
            alla |= {r.id for r in self.sanktionsmetod.rader}
        return alla

    def kravets_innehallssumma(self, krav_id: str) -> str:
        """Det en sakkunnig godkänner för ett krav: kravet, dess lydelser med giltighet och textsumma,
        källans giltighetsuppgifter och definitionerna av de fält som villkoret galler_om använder."""
        krav = self.krav[krav_id]
        kalla_ids = sorted({self.lydelser[i].kalla for i in krav.lydelser if i in self.lydelser})
        underlag = {
            "krav": krav.model_dump(mode="json", exclude={"sakkunnig"}),
            "lydelser": [self.lydelser[i].model_dump(mode="json") for i in krav.lydelser if i in self.lydelser],
            "kallor": [self.kallor[i].model_dump(mode="json", include=KALLANS_GILTIGHET)
                       for i in kalla_ids if i in self.kallor],
            "falt": [
                self.falt[falt_id].model_dump(mode="json")
                for falt_id in sorted(_falt_i_villkorsdata(krav.galler_om))
                if falt_id in self.falt
            ],
        }
        return _summa(underlag)

    def kartans_innehallssumma(self, paket_id: str) -> str:
        """Det en sakkunnig godkänner för en paragrafkarta: kartans rader och giltighet, paketets län och krav,
        källornas paragrafindelning och giltighet samt lydelserna i de källor kartan omfattar."""
        paket = self.regelpaket[paket_id]
        karta = paket.paragrafkarta
        kalla_ids = sorted({omfattning.kalla for omfattning in karta.omfattning})
        underlag = {
            "karta": karta.model_dump(mode="json", exclude={"sakkunnig"}),
            "paket": {"id": paket.id, "lan": list(paket.lan), "krav": list(paket.krav)},
            "kallor": [
                self.kallor[kalla_id].model_dump(mode="json", include=KALLANS_GILTIGHET | {"paragrafer"})
                for kalla_id in kalla_ids
                if kalla_id in self.kallor
            ],
            "lydelser": [
                lydelse.model_dump(mode="json")
                for lydelse in sorted(self.lydelser.values(), key=lambda post: post.id)
                if lydelse.kalla in kalla_ids
            ],
        }
        return _summa(underlag)


def _summa(underlag: dict[str, Any]) -> str:
    return for_text(json.dumps(underlag, sort_keys=True, ensure_ascii=False))


def _falt_i_villkorsdata(data: Any) -> set[str]:
    """Fält som ett villkor i YAML-form nämner, utan att villkoret behöver vara giltigt."""
    if isinstance(data, dict):
        egna = {data["falt"]} if isinstance(data.get("falt"), str) else set()
        return egna.union(*(_falt_i_villkorsdata(varde) for varde in data.values()))
    if isinstance(data, list):
        return set().union(*(_falt_i_villkorsdata(del_) for del_ in data))
    return set()


def utan_granskningsmetadata(data):
    if isinstance(data, dict):
        return {k: utan_granskningsmetadata(v) for k, v in data.items()
                if k not in {"sakkunnig", "granskning", "c_granskning"}}
    if isinstance(data, (list, tuple)):
        return [utan_granskningsmetadata(v) for v in data]
    return data
