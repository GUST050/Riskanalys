"""Bedömningsresultat (spec 7). Allt här kommer från motorn, inget från AI."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_serializer

from riskanalys.regelverk.tillsyn import Omfattningsbeslut
from riskanalys.regelverk.modeller import Dimension, Konsekvens, Risk, Sannolikhet

Bedomningsstatus = Literal["preliminär", "slutlig"]


class Fryst(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Riskdel(Fryst):
    sannolikhet: Sannolikhet
    konsekvens: Konsekvens
    risk: Risk


class Kontrollbedomning(Fryst):
    effekt: str | None = None
    effekt_belagd: bool | None = None
    id: str
    utformning: str | None
    genomforande: str | None
    fungerar_och_ar_belagd: bool


class Sanktionsbedomning(Fryst):
    kontroll: Kontrollbedomning | None = None
    status: Bedomningsstatus
    inneboende: Riskdel | None
    kvarstaende: Risk | None
    regelspar: tuple[str, ...]
    okanda_uppgifter: tuple[str, ...]


class EgenErfarenhet(Fryst):
    """Byråövergripande observationer, aldrig en riskpoäng per tjänst."""

    rapporter: Literal["inga", "finns", "saknas"]
    avbojanden: Literal["inga", "finns", "saknas"]
    belagd: bool
    okanda_uppgifter: tuple[str, ...]


class Scenariobedomning(Fryst):
    """Ett scenario (tjänst × hot) i en dimension, beräknat enligt scenariometoden (spec 2026-10-18)."""

    hot: str
    dimension: Dimension
    hotniva: Sannolikhet
    iakttaget: bool
    sarbarheter: tuple[str, ...]
    sarbarhetsniva: Sannolikhet
    sannolikhet: Sannolikhet
    konsekvens: Konsekvens
    risk: Risk
    tackande_kontroller: tuple[str, ...]
    kvarstaende: Risk | None
    avgorande: bool
    regelspar: tuple[str, ...]


class Tjanstbedomning(Fryst):
    egen_erfarenhet: EgenErfarenhet | None = None
    sanktionsrisk: Sanktionsbedomning | None = None
    tjanst: str
    erbjuds: bool | None
    status: Bedomningsstatus
    hot: tuple[str, ...]
    tillampade_sarbarheter: tuple[str, ...]
    inneboende: Riskdel | None
    terrorfinansiering: Riskdel | None
    kontroller: tuple[Kontrollbedomning, ...]
    kvarstaende: Risk | None
    regelspar: tuple[str, ...]
    okanda_uppgifter: tuple[str, ...]
    scenarier: tuple[Scenariobedomning, ...] = ()

    @model_serializer(mode="wrap")
    def serialisera(self, handler):
        """Utan scenariometod utelämnas scenarierna, så att äldre bedömningar och summor består."""
        data = handler(self)
        if not self.scenarier:
            data.pop("scenarier", None)
        return data


class Proportionalitet(Fryst):
    niva: Literal["enkel", "standard", "utökad"]
    status: Bedomningsstatus
    regelspar: tuple[str, ...]
    okanda_uppgifter: tuple[str, ...]


class Bedomning(Fryst):
    proportionalitet: Proportionalitet | None = None
    byra: str
    regelpaket: str
    datum: date
    lan: str
    regelbas_version: str
    regelbas_kontrollsumma: str
    status: Bedomningsstatus
    tjanster: tuple[Tjanstbedomning, ...]
    omfattning: Omfattningsbeslut | None = None
