"""Byråprofilen (spec 6.2). Varje uppgift har status, källa och datum."""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from riskanalys.regelverk.villkor import Faltvarde, Kunskap

Status = Literal["saknas", "föreslagen", "bekräftad", "ej_tillämplig"]


class Fryst(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Uppgift(Fryst):
    varde: Any = None
    status: Status = "saknas"
    kalla: str | None = None
    datum: date | None = None
    bekraftad_av: str | None = None
    motivering: str | None = None


class Byra(Fryst):
    id: str
    regelpaket: str
    datum: date
    lan: str


class Profil(Fryst):
    byra: Byra
    uppgifter: dict[str, Uppgift]

    def faltvarden(self) -> dict[str, Faltvarde]:
        """Uppgifterna som fältvärden för villkorsutvärderaren. Bara bekräftade värden är kända."""
        return {falt_id: _faltvarde(uppgift) for falt_id, uppgift in self.uppgifter.items()}

    def ar_bekraftad(self, falt_id: str) -> bool:
        uppgift = self.uppgifter.get(falt_id)
        return uppgift is not None and uppgift.status == "bekräftad"


def _faltvarde(uppgift: Uppgift) -> Faltvarde:
    if uppgift.status == "bekräftad":
        return Faltvarde(Kunskap.KAND, uppgift.varde)
    if uppgift.status == "ej_tillämplig":
        return Faltvarde(Kunskap.EJ_TILLAMPLIG)
    return Faltvarde(Kunskap.OKAND)
