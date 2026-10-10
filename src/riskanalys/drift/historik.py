"""Versionshistorik och nästa genomgång (spec 13.1)."""

import calendar
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

from riskanalys.lagring.kontrollsumma import for_fil
from riskanalys.lagring.yamlfil import las_yaml, spara_yaml

HISTORIKFIL = Path("drift") / "historik.yaml"
GENOMGANG_MANADER = 12
UTVARDERING = "utvärdering"


class Handelse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    datum: date
    typ: Literal["utvärdering", "uppdatering", "fastställelse"]
    beskrivning: str
    version: int | None = None


class Historik(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    handelser: tuple[Handelse, ...] = ()

    def med(self, handelse: Handelse) -> "Historik":
        return Historik(handelser=(*self.handelser, handelse))

    def senaste_utvardering(self) -> date | None:
        """Datum för den senaste utvärderingen. Fastställelser och uppdateringar räknas inte."""
        return max((handelse.datum for handelse in self.handelser if handelse.typ == UTVARDERING), default=None)

    def nasta_genomgang(self) -> date | None:
        senaste = self.senaste_utvardering()
        return None if senaste is None else lagg_till_manader(senaste, GENOMGANG_MANADER)


def lagg_till_manader(datum: date, manader: int) -> date:
    """Lägger till månader. Finns inte dagen i målmånaden blir det månadens sista dag."""
    index = datum.month - 1 + manader
    ar, manad = datum.year + index // 12, index % 12 + 1
    return date(ar, manad, min(datum.day, calendar.monthrange(ar, manad)[1]))


def las_historik(byramapp: Path) -> Historik:
    sokvag = byramapp / HISTORIKFIL
    if not sokvag.is_file():
        return Historik()
    return Historik.model_validate(las_yaml(sokvag))


def spara_historik(byramapp: Path, historik: Historik) -> None:
    spara_yaml(byramapp / HISTORIKFIL, historik.model_dump(mode="json"))


def historikens_kontrollsumma(byramapp: Path) -> str:
    sokvag = byramapp / HISTORIKFIL
    return for_fil(sokvag) if sokvag.is_file() else ""
