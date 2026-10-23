"""Sakgranskning och beslut om fastställelse (spec 10)."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_serializer


class Fryst(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Sakgranskning(Fryst):
    """En persons granskning av ett avsnitt i en bestämd lydelse, identifierad med kontrollsumman."""

    avsnitt: str
    kontrollsumma: str
    godkand: bool
    roll: str
    namn: str
    datum: date
    kommentar: str | None = None
    dokumentstruktur: str | None = None
    analysbindning: str | None = None
    granskningssatt: Literal['samlad_resultatrapport'] | None = None

    @model_serializer(mode="wrap")
    def _historiskt_format(self, handler):
        data = handler(self)
        if self.analysbindning is None:
            data.pop("analysbindning", None)
        if self.granskningssatt is None:
            data.pop("granskningssatt", None)
        return data


class Beslut(Fryst):
    """Beslutet att fastställa: vilket organ, när och vem som undertecknar."""

    organ: str
    datum: date
    namn: str
    roll: str
