"""Byråprofilen (spec 6.2). Varje uppgift har status, källa och datum."""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_serializer, model_validator

from riskanalys.regelverk.villkor import Faltvarde, Kunskap

Status = Literal["saknas", "föreslagen", "bekräftad", "ej_tillämplig"]


class Fryst(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Period(Fryst):
    fran: date
    till: date

    @model_validator(mode="after")
    def ordning(self):
        if self.fran > self.till:
            raise ValueError("Periodens från-datum får inte vara efter till-datum.")
        return self


class Uppgift(Fryst):
    varde: Any = None
    status: Status = "saknas"
    kalla: str | None = None
    datum: date | None = None
    bekraftad_av: str | None = None
    motivering: str | None = None
    period: Period | None = None
    harledd: bool = False
    inaktuell: bool = False
    underlagsbindning: str | None = Field(default=None, pattern=r"^sha256:[0-9a-f]{64}$")

    @field_validator("varde", mode="after")
    @classmethod
    def _flerval_som_tuple(cls, varde: Any) -> Any:
        """Ett flerval lagras som YAML-lista men hanteras som oföränderlig tuple."""
        return tuple(varde) if isinstance(varde, list) else varde

    @model_serializer(mode="wrap")
    def serialisera(self, handler):
        """Historiska uppgifter behåller sina payloads och profilsummor. Ett flerval skrivs som lista."""
        data = handler(self)
        if self.underlagsbindning is None:
            data.pop("underlagsbindning", None)
        if isinstance(self.varde, tuple) and "varde" in data:
            data["varde"] = list(data["varde"])
        return data


class Byra(Fryst):
    id: str
    regelpaket: str
    datum: date
    lan: str


class Tjansteplan(Fryst):
    id: str = Field(min_length=1, max_length=80, pattern=r'^[a-zA-Z0-9_-]+$')
    tjanst: str
    typ: Literal['ny_tjanst', 'vasentligt_andrad_tjanst', 'ny_marknad', 'annan_forandring']
    beskrivning: str = Field(min_length=1, max_length=12000)
    avsett_inforande: date | None = None
    uppgifter: dict[str, Uppgift] = Field(default_factory=dict)


class Kombinationsgrupp(Fryst):
    id: str = Field(min_length=1, max_length=80, pattern=r'^[a-zA-Z0-9_-]+$')
    tjanst: str
    population: Literal['kunder', 'uppdrag']
    avgransning: str = Field(min_length=1, max_length=2000)
    beskrivning: str = Field(min_length=1, max_length=12000)
    sarbarheter: tuple[str, ...] = Field(min_length=1)
    antal: Uppgift
    bas: Uppgift


class Profil(Fryst):
    byra: Byra
    uppgifter: dict[str, Uppgift]
    tjansteplaner: tuple[Tjansteplan, ...] = ()
    kombinationsgrupper: tuple[Kombinationsgrupp, ...] = ()

    @model_serializer(mode='wrap')
    def serialisera(self, handler):
        data = handler(self)
        for falt in ('tjansteplaner', 'kombinationsgrupper'):
            if not getattr(self, falt):
                data.pop(falt, None)
        return data

    def faltvarden(self) -> dict[str, Faltvarde]:
        """Uppgifterna som fältvärden för villkorsutvärderaren. Bara bekräftade värden är kända."""
        return {falt_id: _faltvarde(uppgift) for falt_id, uppgift in self.uppgifter.items()}

    def ar_bekraftad(self, falt_id: str) -> bool:
        uppgift = self.uppgifter.get(falt_id)
        return uppgift is not None and uppgift.status == "bekräftad" and not uppgift.inaktuell


def _faltvarde(uppgift: Uppgift) -> Faltvarde:
    if uppgift.inaktuell:
        return Faltvarde(Kunskap.OKAND)
    if uppgift.status == "bekräftad":
        return Faltvarde(Kunskap.KAND, uppgift.varde)
    if uppgift.status == "ej_tillämplig":
        return Faltvarde(Kunskap.EJ_TILLAMPLIG)
    return Faltvarde(Kunskap.OKAND)
