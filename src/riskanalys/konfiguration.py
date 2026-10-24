"""Sammansättning av textleverantör för CLI och webb."""
from dataclasses import dataclass
import os
from pathlib import Path
from typing import Literal

from riskanalys.dokument.claude import STANDARDEFFORT, STANDARDMODELL, ClaudeLeverantor
from riskanalys.dokument.leverantor import LeverantorFel, Textleverantor, ladda_testleverantor


@dataclass(frozen=True)
class Skrivkonfiguration:
    leverantor: Literal['claude', 'test'] = 'claude'
    testsvar: Path | None = None
    modell: str = STANDARDMODELL
    effort: str = STANDARDEFFORT


def skapa_textleverantor(val: Skrivkonfiguration) -> Textleverantor:
    if val.leverantor == 'test':
        if val.testsvar is None:
            raise LeverantorFel('Ange en fil med förberedda svar med --testsvar.')
        return ladda_testleverantor(val.testsvar)
    if val.leverantor != 'claude':
        raise LeverantorFel('Välj en känd textleverantör: claude eller test.')
    if not os.environ.get('ANTHROPIC_API_KEY'):
        raise LeverantorFel('Sätt miljövariabeln ANTHROPIC_API_KEY för att använda Claude, eller använd --leverantor test.')
    return ClaudeLeverantor(modell=val.modell, effort=val.effort)
