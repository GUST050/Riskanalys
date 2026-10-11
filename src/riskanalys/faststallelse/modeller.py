"""Sakgranskning och beslut om fastställelse (spec 10)."""

from datetime import date

from pydantic import BaseModel, ConfigDict


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


class Beslut(Fryst):
    """Beslutet att fastställa: vilket organ, när och vem som undertecknar."""

    organ: str
    datum: date
    namn: str
    roll: str
