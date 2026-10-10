"""Bedömningsresultat (spec 7). Allt här kommer från motorn, inget från AI."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict

from riskanalys.regelverk.tillsyn import Omfattningsbeslut
from riskanalys.regelverk.modeller import Konsekvens, Risk, Sannolikhet

Bedomningsstatus = Literal["preliminär", "slutlig"]


class Fryst(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Riskdel(Fryst):
    sannolikhet: Sannolikhet
    konsekvens: Konsekvens
    risk: Risk


class Kontrollbedomning(Fryst):
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


class Tjanstbedomning(Fryst):
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


class Bedomning(Fryst):
    byra: str
    regelpaket: str
    datum: date
    lan: str
    regelbas_version: str
    regelbas_kontrollsumma: str
    status: Bedomningsstatus
    tjanster: tuple[Tjanstbedomning, ...]
    omfattning: Omfattningsbeslut | None = None
