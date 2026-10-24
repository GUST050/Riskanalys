"""Läs och skriv YAML med svenska tecken."""

from pathlib import Path
import os
import tempfile
from pydantic import ValidationError
from typing import Any

import yaml

from riskanalys.fel import RiskanalysFel

# libyaml ger samma säkra tolkning som ren Python men flera gånger snabbare. Skrivningen
# behåller ren Python så att sparade bytes och deras hashar inte ändras.
YAMLLASARE = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def las_yaml_text(text: str | bytes) -> Any:
    return yaml.load(text, Loader=YAMLLASARE)


def spara_yaml(sokvag: Path, data: Any) -> None:
    """Publicera fullständiga YAML-bytes; skilj skrivfel från synkfel efter namnbyte."""
    temp = None
    publicerad = False
    try:
        sokvag.parent.mkdir(parents=True, exist_ok=True)
        fd, temp = tempfile.mkstemp(prefix='.' + sokvag.name + '-', suffix='.tmp', dir=sokvag.parent)
        with os.fdopen(fd, 'w', encoding='utf-8') as fil:
            yaml.safe_dump(data, fil, allow_unicode=True, sort_keys=False)
            fil.flush()
            os.fsync(fil.fileno())
        os.replace(temp, sokvag)
        publicerad = True
        temp = None
        fd = os.open(sokvag.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    except OSError as exc:
        if publicerad:
            raise RiskanalysFel('Filen har sparats, men katalogens disksynk misslyckades. Läs om den sparade filen innan du försöker igen.') from exc
        raise RiskanalysFel('Filen kunde inte sparas. Tidigare fil är oförändrad. Kontrollera ledigt utrymme och skrivbehörighet.') from exc
    finally:
        if temp is not None and os.path.exists(temp):
            os.unlink(temp)


def las_yaml(sokvag: Path) -> Any:
    try:
        return las_yaml_text(las_text(sokvag))
    except FileNotFoundError as undantag:
        raise RiskanalysFel(f"Filen {sokvag} saknas.") from undantag
    except yaml.YAMLError as undantag:
        raise RiskanalysFel(f"Filen {sokvag} är inte giltig YAML: {undantag}") from undantag


def las_text(sokvag: Path) -> str:
    try:
        return sokvag.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise RiskanalysFel(f"Filen {sokvag} kan inte läsas som UTF-8. Rätta filen eller återställ från säkerhetskopian.") from e


def las_modell(sokvag: Path, modell, *, json: bool = False):
    try:
        data = las_text(sokvag) if json else las_yaml(sokvag)
        return modell.validate_json(data) if json and hasattr(modell, "validate_json") else (
            modell.model_validate_json(data) if json else (
                modell.validate_python(data) if hasattr(modell, "validate_python") else modell.model_validate(data)))
    except (ValidationError, ValueError, TypeError) as e:
        raise RiskanalysFel(f"Filen {sokvag} har felaktigt innehåll. Rätta filen eller återställ från säkerhetskopian.") from e
