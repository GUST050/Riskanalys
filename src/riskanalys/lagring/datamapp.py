"""Datamappen där byråernas uppgifter lagras. Den får aldrig ligga i repot (spec 5.2)."""

import os
import re
from pathlib import Path

from riskanalys.fel import RiskanalysFel

MILJOVARIABEL = "RISKANALYS_DATA"
STANDARDMAPP = Path("~/RiskanalysData")
REPO_ROT = Path(__file__).resolve().parents[3]
_BYRA_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")


class DatamappFel(RiskanalysFel):
    """Datamappen eller byrå-ID:t är ogiltigt."""


def datamapp() -> Path:
    """Returnerar datamappen. Vägrar om den ligger i repot."""
    mapp = Path(os.environ.get(MILJOVARIABEL, STANDARDMAPP)).expanduser().resolve()
    if _ligger_i_repot(mapp):
        raise DatamappFel(
            f"Datamappen {mapp} ligger i repot. Byrådata får aldrig lagras i repot. "
            f"Sätt {MILJOVARIABEL} till en mapp utanför {REPO_ROT}."
        )
    return mapp


def _ligger_i_repot(mapp: Path) -> bool:
    """Också när sökvägen skrivs med annat skiftläge på ett filsystem som inte skiljer på stora och små bokstäver,
    som macOS standardfilsystem. Jämförelsen görs mot den närmaste mapp i sökvägen som finns."""
    if mapp.is_relative_to(REPO_ROT):
        return True
    befintlig = next((del_ for del_ in (mapp, *mapp.parents) if del_.exists()), None)
    return befintlig is not None and any(os.path.samefile(del_, REPO_ROT) for del_ in (befintlig, *befintlig.parents))


def byramapp(byra_id: str) -> Path:
    """Returnerar mappen för en byrå utan att skapa den."""
    if not _BYRA_ID.match(byra_id):
        raise DatamappFel(
            f"Ogiltigt byrå-ID {byra_id!r}. Använd a–z, 0–9 och bindestreck, "
            "börja med bokstav eller siffra och använd högst 63 tecken."
        )
    return datamapp() / byra_id


def skapa_byramapp(byra_id: str) -> Path:
    """Skapar byråns mapp med behörighet bara för användaren."""
    mapp = byramapp(byra_id)
    if mapp.exists():
        raise DatamappFel(f"Byrån {byra_id} finns redan i {mapp}.")
    mapp.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    mapp.mkdir(mode=0o700)
    return mapp


def befintlig_byramapp(byra_id: str) -> Path:
    """Returnerar mappen för en byrå som måste finnas."""
    mapp = byramapp(byra_id)
    if not mapp.is_dir():
        raise DatamappFel(f"Byrån {byra_id} finns inte i {datamapp()}. Skapa den med 'riskanalys ny'.")
    return mapp
