"""Datamodeller för regelbasen (spec avsnitt 6)."""

import json
from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from riskanalys.lagring.kontrollsumma import for_text
from riskanalys.regelverk.villkor import Faltdef

Grund = Literal["ska_krav", "allmänt_råd", "tillsynspraxis", "eu_utkast", "metodval"]
Sannolikhet = Literal["låg", "medel", "hög"]
Konsekvens = Literal["begränsad", "betydande", "allvarlig"]
Risk = Literal["låg", "måttlig", "hög", "mycket hög"]
Allvar = Literal["blockerande", "hög", "medel", "låg"]
Belagg = Literal["dokument", "datum", "logg", "beslut", "register"]
KONTROLLSUMMA = r"^sha256:[0-9a-f]{64}$"
KALLANS_GILTIGHET = frozenset({"id", "typ", "utgivare", "geografi", "beslutad", "konsoliderad_tom", "kontrollsumma"})


class Strikt(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Falt(Strikt):
    id: str
    typ: Literal["bool", "heltal", "tal", "andel", "text", "val", "datum"]
    fraga: str
    varfor: str
    personuppgift: bool = False
    kritisk: bool = False
    smagrupp: bool = False
    val: tuple[str, ...] = ()


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


class Krav(Strikt):
    id: str
    kalla: str
    lagrum: str
    lydelser: tuple[str, ...] = Field(min_length=1)
    grund: Grund
    text: str
    galler_om: dict[str, Any]
    belagg: tuple[Belagg, ...] = Field(min_length=1)
    uppfylls_i: tuple[str, ...] = Field(min_length=1)
    ikraft: date | None = None
    upphor: date | None = None
    sakkunnig: Sakkunnig = Sakkunnig()


class Hot(Strikt):
    id: str
    namn: str
    beskrivning: str
    kallor: tuple[str, ...] = Field(min_length=1)
    galler_tf: bool = False


class Effekt(Strikt):
    sannolikhet: int = Field(ge=1, le=2)


class Sarbarhet(Strikt):
    id: str
    namn: str
    omrade: Literal["kund", "kanal", "geo", "verk", "tj"]
    grund: Grund
    villkor: dict[str, Any]
    vid_okant: Literal["preliminart_galler", "preliminart_galler_ej"] = "preliminart_galler"
    effekt: Effekt
    galler: Literal["penningtvatt", "terrorfinansiering", "bada"] = "penningtvatt"
    kallor: tuple[str, ...] = Field(min_length=1)


class Kontroll(Strikt):
    id: str
    namn: str
    beskrivning: str
    utformning_falt: str
    genomforande_falt: str
    kallor: tuple[str, ...] = ()


class Tjanst(Strikt):
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
    id: str
    sannolikhet: Sannolikhet
    konsekvens: Konsekvens
    risk: Risk
    grund: Grund
    forklaring: str


class Regel(Strikt):
    id: str
    grund: Grund
    forklaring: str


class Metod(Strikt):
    riskmatris: tuple[MatrisRad, ...]
    sannolikhet: Regel
    konsekvens: Regel
    terrorfinansiering: Regel
    kvarstaende_ej_belagd: Regel
    kvarstaende_sankning: Regel

    def regler(self) -> tuple[Regel, ...]:
        return (
            self.sannolikhet,
            self.konsekvens,
            self.terrorfinansiering,
            self.kvarstaende_ej_belagd,
            self.kvarstaende_sankning,
        )


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

    @property
    def hanterad(self) -> bool:
        return bool(self.krav) or bool(self.ej_tillamplig)


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
    id: str
    namn: str
    sektor: str
    lan: tuple[str, ...] = Field(min_length=1)
    kallor: tuple[str, ...]
    krav: tuple[str, ...] = Field(min_length=1)
    tjanster: tuple[str, ...] = Field(min_length=1)
    paragrafkarta: Paragrafkarta


class Regelbas(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: str
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
        )
        alla = {nyckel for samling in samlingar for nyckel in samling}
        alla |= {rad.id for rad in self.metod.riskmatris}
        alla |= {regel.id for regel in self.metod.regler()}
        return alla

    def kravets_innehallssumma(self, krav_id: str) -> str:
        """Det en sakkunnig godkänner för ett krav: kravet, dess lydelser med giltighet och textsumma,
        källans giltighetsuppgifter och definitionerna av de fält som villkoret galler_om använder."""
        krav = self.krav[krav_id]
        kalla = self.kallor.get(krav.kalla)
        underlag = {
            "krav": krav.model_dump(mode="json", exclude={"sakkunnig"}),
            "lydelser": [self.lydelser[i].model_dump(mode="json") for i in krav.lydelser if i in self.lydelser],
            "kalla": kalla.model_dump(mode="json", include=KALLANS_GILTIGHET) if kalla else None,
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
