"""Läs och skriv YAML med svenska tecken."""

from pathlib import Path
from pydantic import ValidationError
from typing import Any

import yaml

from riskanalys.fel import RiskanalysFel


def spara_yaml(sokvag: Path, data: Any) -> None:
    sokvag.parent.mkdir(parents=True, exist_ok=True)
    sokvag.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def las_yaml(sokvag: Path) -> Any:
    try:
        return yaml.safe_load(las_text(sokvag))
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
