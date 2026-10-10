"""Modeller för AI-schemat, AI-underlaget och dokumenten (spec 8 och 11)."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from riskanalys.lagring.kontrollsumma import for_text


class Last(BaseModel):
    """Basklass: okända fält vägras och objekten ändras inte efter att de skapats."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class Textstycke(Last):
    typ: Literal["beskrivning", "analys", "motivering", "scenario"]
    text: str
    referenser: list[str]


class Oklarhet(Last):
    fraga: str
    saknad_uppgift: str


class AvsnittsUtkast(Last):
    """Det låsta schema som AI svarar i."""

    avsnitt: str
    stycken: list[Textstycke]
    oklarheter: list[Oklarhet]


class UnderlagHot(Last):
    id: str
    namn: str
    beskrivning: str


class UnderlagSarbarhet(Last):
    id: str
    namn: str
    galler: Literal["ja", "nej", "okänt"]


class UnderlagKontroll(Last):
    id: str
    namn: str
    status: str


class UnderlagUppgift(Last):
    id: str
    fraga: str
    varde: str
    bekraftad: bool


class UnderlagBrist(Last):
    id: str
    namn: str


class Avsnittsunderlag(Last):
    """Allt AI får veta om ett avsnitt. Byggs bara ur tillåtelselistan."""

    avsnitt: str
    rubrik: str
    instruktion: str
    tjanst_id: str
    tjanst_namn: str
    tjanst_beskrivning: str
    nivaer: dict[str, str]
    hot: tuple[UnderlagHot, ...]
    sarbarheter: tuple[UnderlagSarbarhet, ...]
    kontroller: tuple[UnderlagKontroll, ...]
    uppgifter: tuple[UnderlagUppgift, ...]
    regelspar: tuple[str, ...]
    undvik: tuple[UnderlagBrist, ...]

    def tillatna_id(self) -> frozenset[str]:
        """De ID:n som texten får hänvisa till."""
        return frozenset(
            {
                self.tjanst_id,
                *(post.id for post in self.hot),
                *(post.id for post in self.sarbarheter),
                *(post.id for post in self.kontroller),
                *(post.id for post in self.uppgifter),
                *self.regelspar,
            }
        )


class Avsnitt(Last):
    id: str
    rubrik: str
    kalla: Literal["regelbas", "ai"]
    stycken: tuple[Textstycke, ...]

    def kontrollsumma(self) -> str:
        return for_text(self.model_dump_json())


class Dokument(Last):
    id: str
    titel: str
    avsnitt: tuple[Avsnitt, ...]

    def avsnitt_med_id(self) -> dict[str, Avsnitt]:
        return {avsnitt.id: avsnitt for avsnitt in self.avsnitt}
