"""Läs och skriv YAML med svenska tecken."""

from pathlib import Path
from typing import Any

import yaml

from riskanalys.fel import RiskanalysFel


def spara_yaml(sokvag: Path, data: Any) -> None:
    sokvag.parent.mkdir(parents=True, exist_ok=True)
    sokvag.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def las_yaml(sokvag: Path) -> Any:
    try:
        return yaml.safe_load(sokvag.read_text(encoding="utf-8"))
    except FileNotFoundError as undantag:
        raise RiskanalysFel(f"Filen {sokvag} saknas.") from undantag
    except yaml.YAMLError as undantag:
        raise RiskanalysFel(f"Filen {sokvag} är inte giltig YAML: {undantag}") from undantag
