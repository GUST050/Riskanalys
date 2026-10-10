"""Läs och spara byråprofilen i byråns datamapp."""

from pathlib import Path

from pydantic import ValidationError

from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.yamlfil import las_yaml, spara_yaml
from riskanalys.profil.modeller import Profil

PROFILFIL = Path("profil") / "profil.yaml"


def spara_profil(byramapp: Path, profil: Profil) -> Path:
    sokvag = byramapp / PROFILFIL
    spara_yaml(sokvag, profil.model_dump(mode="python"))
    return sokvag


def las_profil(byramapp: Path) -> Profil:
    sokvag = byramapp / PROFILFIL
    if not sokvag.is_file():
        raise RiskanalysFel(f"Profilen saknas i {byramapp}. Skapa byrån med 'riskanalys ny'.")
    try:
        return Profil.model_validate(las_yaml(sokvag))
    except ValidationError as fel:
        platser = ", ".join(".".join(str(del_) for del_ in post["loc"]) for post in fel.errors()[:3])
        raise RiskanalysFel(
            f"Profilen i {sokvag} kan inte läsas. Kontrollera {platser}. "
            "Rätta filen eller återställ den från säkerhetskopian."
        ) from fel
