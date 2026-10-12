"""Gränssnitt för textleverantörer och en testleverantör för automatiska tester (spec 8.3)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from pydantic import TypeAdapter, ValidationError, Field

from riskanalys.dokument.modeller import Avsnittsunderlag, AvsnittsUtkast, AISvar, Last
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.yamlfil import las_text

_SVARSLISTA = TypeAdapter(list[AvsnittsUtkast | AISvar])


class LeverantorFel(RiskanalysFel):
    """Textleverantören kunde inte leverera något svar."""

    def __init__(self, meddelande: str, *, tillfalligt: bool = False) -> None:
        super().__init__(meddelande)
        self.tillfalligt = tillfalligt


class Tokenanvandning(Last):
    """Tokenanvändning för ett försök hos leverantören."""

    typ: str
    modell: str | None
    indata_token: int
    utdata_token: int
    cache_lasning_token: int = 0
    cache_skrivning_token: int = 0


class Anropsdata(Last):
    """Vem som svarade, med vilka inställningar, och vad anropet förbrukade."""

    leverantor: str
    begard_modell: str
    svarsmodell: str
    effort: str | None
    prompt_kontrollsumma: str | None
    svar_id: str | None
    stop_reason: str | None
    reservmodell_svarade: bool
    anvandning: tuple[Tokenanvandning, ...]
    tidpunkt: datetime
    del_id: str | None = None


class Leveranssvar(Last):
    """Ett svar från leverantören: råtexten, anropsdatan och eventuellt avbrott."""

    anrop: Anropsdata
    text: str
    avbrott: str | None


class Textleverantor(Protocol):
    namn: str
    modell: str

    def skriv(self, underlag: Avsnittsunderlag, aterkoppling: list[str]) -> Leveranssvar: ...

    def skriv_del(self, anrop: "Delanrop") -> Leveranssvar: ...


class Testleverantor:
    """Returnerar förberedda svar i tur och ordning. Används i alla automatiska tester."""

    __test__ = False  # namnet börjar på Test, men klassen är ingen testklass för pytest
    namn = "test"
    modell = "testleverantor"

    def __init__(self, svar: list[AvsnittsUtkast | AISvar | str]) -> None:
        self._svar = tuple(svar)
        self.anrop: list[tuple[Avsnittsunderlag, list[str]]] = []
        self.delanrop: list[Delanrop] = []

    def skriv(self, underlag: Avsnittsunderlag, aterkoppling: list[str]) -> Leveranssvar:
        self.anrop.append((underlag, list(aterkoppling)))
        nummer = len(self.anrop)
        if nummer > len(self._svar):
            raise LeverantorFel(f"Testleverantören har bara {len(self._svar)} förberedda svar.")
        svar = self._svar[nummer - 1]
        return Leveranssvar(
            anrop=Anropsdata(
                leverantor=self.namn,
                begard_modell=self.modell,
                svarsmodell=self.modell,
                effort=None,
                prompt_kontrollsumma=None,
                svar_id=f"test-{nummer}",
                stop_reason="end_turn",
                reservmodell_svarade=False,
                anvandning=(),
                tidpunkt=datetime.now(timezone.utc),
            ),
            text=svar if isinstance(svar, str) else svar.model_dump_json(),
            avbrott=None,
        )

    def skriv_del(self, anrop: Delanrop) -> Leveranssvar:
        self.delanrop.append(anrop)
        nummer = len(self.anrop) + len(self.delanrop)
        if nummer > len(self._svar):
            raise LeverantorFel(f"Testleverantören har bara {len(self._svar)} förberedda svar.")
        svar = self._svar[nummer - 1]
        return Leveranssvar(
            anrop=Anropsdata(leverantor=self.namn, begard_modell=self.modell, svarsmodell=self.modell, effort=anrop.effort,
                             prompt_kontrollsumma=anrop.promptsumma, svar_id=f"test-{nummer}", stop_reason="end_turn",
                             reservmodell_svarade=False, anvandning=(), tidpunkt=datetime.now(timezone.utc),
                             del_id=anrop.del_id),
            text=svar if isinstance(svar, str) else svar.model_dump_json(),
            avbrott=None,
        )


def ladda_testleverantor(fil: Path) -> Testleverantor:
    """Läser förberedda svar från en JSON-fil med en lista av AI-utkast."""
    try:
        svar = _SVARSLISTA.validate_json(las_text(fil))
    except RiskanalysFel as undantag:
        raise LeverantorFel(str(undantag)) from undantag
    except FileNotFoundError as undantag:
        raise LeverantorFel(f"Filen med testsvar saknas: {fil}") from undantag
    except ValidationError as undantag:
        raise LeverantorFel(f"Filen med testsvar {fil} är ogiltig: {undantag.error_count()} fel.") from undantag
    return Testleverantor(list(svar))


class Delanrop(Last):
    """Ett anrop för en analysdel: fast systemprompt, innehåll i fast ordning och schema (spec 8.4.2)."""

    del_id: str
    system: str
    innehall: list[dict]
    svarsschema: dict = Field(alias="schema")

    @property
    def schema(self) -> dict:
        return self.svarsschema
    effort: str
    max_tokens: int
    promptsumma: str
