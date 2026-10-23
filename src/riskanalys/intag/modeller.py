from dataclasses import dataclass
from datetime import date
from typing import Literal
from pydantic import Field
from riskanalys.profil.modeller import Period
from riskanalys.regelverk.modeller import Falt, Strikt


class IntagSvar(Strikt):
    falt: str
    text: str = Field(default='', max_length=12000)
    status: Literal['bekräftad', 'okänt', 'ej_tillämplig'] = 'bekräftad'
    kalla: str = Field(default='', max_length=2000)
    datum: date
    roll: str = Field(default='Uppgiftslamnare', max_length=200)
    period: Period | None = None
    motivering: str = Field(default='', max_length=2000)


@dataclass(frozen=True)
class Intagsfraga:
    falt: Falt
    besvarad: bool


@dataclass(frozen=True)
class Tackning:
    antal: int
    besvarade: int
    saknade: tuple[str, ...]
    hinder: tuple[str, ...]
    endast_faststallelse: tuple[str, ...] = ()

    @property
    def komplett(self) -> bool:
        return not self.saknade and not self.hinder

    @property
    def utkastklart(self) -> bool:
        return not self.saknade and not any(h not in self.endast_faststallelse for h in self.hinder)
