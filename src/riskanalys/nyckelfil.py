"""Lokala API-nycklar i en fil utanför repot. Nyckelvärden visas aldrig i fel."""

import os
import stat
from collections.abc import MutableMapping
from pathlib import Path

from riskanalys.fel import RiskanalysFel

MILJOVARIABEL = "RISKANALYS_NYCKELFIL"
STANDARDFIL = Path("~/.config/riskanalys/.env")
TILLATNA = ("ANTHROPIC_API_KEY", "RISKANALYS_SCB_API_KEY", "BOLAGSVERKET_CLIENT_ID", "BOLAGSVERKET_CLIENT_SECRET")


def nyckelfil() -> Path:
    return Path(os.environ.get(MILJOVARIABEL) or STANDARDFIL).expanduser()


def _las_rader(fil: Path) -> list[str]:
    try:
        skyddad = not fil.stat().st_mode & (stat.S_IRWXG | stat.S_IRWXO)
        rader = fil.read_text(encoding="utf-8").splitlines() if skyddad else []
    except (OSError, UnicodeDecodeError):
        raise RiskanalysFel(f"Nyckelfilen {fil} kan inte läsas. Kontrollera att den är en vanlig textfil i UTF-8.") from None
    if not skyddad:
        raise RiskanalysFel(f"Nyckelfilen {fil} kan läsas av andra användare. Skydda den med: chmod 600 {fil}")
    return rader


def _utan_citattecken(varde: str) -> str:
    if len(varde) >= 2 and varde[0] == varde[-1] and varde[0] in "\"'":
        return varde[1:-1]
    return varde


def _tolka(rader: list[str]) -> dict[str, str]:
    varden = {}
    for nummer, rad in enumerate(rader, start=1):
        rad = rad.strip()
        if not rad or rad.startswith("#"):
            continue
        namn, lika, varde = rad.removeprefix("export ").partition("=")
        if not lika or not namn.strip():
            raise RiskanalysFel(f"Rad {nummer} i nyckelfilen ska ha formen NAMN=värde.")
        varden[namn.strip()] = _utan_citattecken(varde.strip())
    return varden


def ladda_nycklar(fil: Path | None = None, miljo: MutableMapping[str, str] = os.environ) -> tuple[str, ...]:
    """Sätter tillåtna nycklar som saknas i miljön och returnerar deras namn. En satt variabel vinner."""
    fil = fil if fil is not None else nyckelfil()
    if not fil.exists():
        return ()
    varden = _tolka(_las_rader(fil))
    laddade = tuple(namn for namn in TILLATNA if varden.get(namn) and not miljo.get(namn))
    for namn in laddade:
        miljo[namn] = varden[namn]
    return laddade
