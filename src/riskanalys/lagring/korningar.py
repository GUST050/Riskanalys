"""Tidsstämplade körningsmappar. Varje körning sparas i en egen mapp och skrivs aldrig över."""

from datetime import datetime
from pathlib import Path

from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.manifest import MANIFESTNAMN

TIDSFORMAT = "%Y%m%dT%H%M%S%f"
_MAX_FORSOK = 100


def ny_korningsmapp(byramapp: Path, undermapp: str) -> Path:
    rot = byramapp / undermapp
    rot.mkdir(parents=True, exist_ok=True)
    stampel = datetime.now().strftime(TIDSFORMAT)
    for nummer in range(_MAX_FORSOK):
        mapp = rot / (stampel if nummer == 0 else f"{stampel}-{nummer:02d}")
        try:
            mapp.mkdir()
        except FileExistsError:
            continue
        return mapp
    raise RiskanalysFel(f"Kunde inte skapa en ny körningsmapp i {rot}.")


def avslutade_korningar(byramapp: Path, undermapp: str) -> list[Path]:
    """Körningar med manifest, äldst först. En körning utan manifest avbröts och räknas inte."""
    rot = byramapp / undermapp
    if not rot.is_dir():
        return []
    return sorted(mapp for mapp in rot.iterdir() if (mapp / MANIFESTNAMN).is_file())


def senaste_korning(byramapp: Path, undermapp: str, kommando: str) -> Path:
    korningar = avslutade_korningar(byramapp, undermapp)
    if not korningar:
        raise RiskanalysFel(f"Det finns ingen körning i {undermapp}. Kör 'riskanalys {kommando}' först.")
    return korningar[-1]
