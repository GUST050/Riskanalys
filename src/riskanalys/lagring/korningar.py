"""Tidsstämplade körningsmappar. Varje körning sparas i en egen mapp och skrivs aldrig över."""

from datetime import datetime, timezone
from pathlib import Path

from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.manifest import MANIFESTNAMN,las_manifest,ManifestFel

TIDSFORMAT = "%Y%m%dT%H%M%S%f"
_MAX_FORSOK = 100


def ny_korningsmapp(byramapp: Path, undermapp: str) -> Path:
    rot = byramapp / undermapp
    rot.mkdir(parents=True, exist_ok=True)
    stampel = datetime.now(timezone.utc).strftime(TIDSFORMAT) + "Z"
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
    mappar = [m for m in rot.iterdir() if m.is_dir() and (m / MANIFESTNAMN).is_file()]
    def nyckel(m):
        stampel = las_manifest(m).skapad
        if stampel.tzinfo is None:stampel=stampel.replace(tzinfo=timezone.utc)
        return stampel.astimezone(timezone.utc), m.name
    return sorted(mappar,key=nyckel)


def senaste_korning(byramapp: Path, undermapp: str, kommando: str) -> Path:
    rot = byramapp / undermapp
    if rot.is_dir():
        for m in rot.iterdir():
            if m.is_dir() and not (m / MANIFESTNAMN).is_file():
                raise ManifestFel(f"Manifest saknas i {m}; körningens relevans kan inte avgöras. Återställ eller flytta den avbrutna mappen och kör igen.")
    korningar = avslutade_korningar(byramapp, undermapp)
    if not korningar:
        raise RiskanalysFel(f"Det finns ingen körning i {undermapp}. Kör 'riskanalys {kommando}' först.")
    return korningar[-1]
