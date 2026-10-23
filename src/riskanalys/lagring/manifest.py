"""Manifest med kontrollsummor för alla filer i en mapp (spec 5.3).

Kontrollsummorna visar att sparade filer är oförändrade. De återskapar inga förlorade filer.
"""

import subprocess
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ConfigDict, ValidationError, Field
from typing import Literal
from riskanalys.lagring.kontrollsumma import for_text

from riskanalys import __version__
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.kontrollsumma import for_fil

MANIFESTNAMN = "manifest.json"
# Filer som operativsystemet skapar när en mapp öppnas i Finder eller Utforskaren. De är inget underlag
# och ingår varken när manifestet skrivs eller när det verifieras. "._x" är macOS dolda resursfiler.
SYSTEMFILER = frozenset({".DS_Store", "Icon\r", ".localized", "Thumbs.db", "desktop.ini"})


class ManifestFel(RiskanalysFel):
    """Manifestet finns men kan inte läsas: trasig JSON, fel kodning eller saknade fält."""


class Programproveniens(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    commit: str | None = None
    arbetskopia: Literal["ren", "andrad", "okand"] = "okand"
    innehallssumma: str = "okänd (äldre manifest)"


def programproveniens(rot: Path | None = None) -> Programproveniens:
    rot = rot or Path(__file__).resolve().parents[3]
    filer = sorted((rot / "src").rglob("*.py"))
    filer += [rot / n for n in ("pyproject.toml", "uv.lock", "requirements.txt") if (rot / n).is_file()]
    summa = for_text("\n".join(f"{p.relative_to(rot).as_posix()} {for_fil(p)}" for p in filer))
    commit = None
    status = "okand"
    if (rot / ".git").exists():
        try:
            commit = subprocess.run(["git", "rev-parse", "HEAD"],cwd=rot,capture_output=True,text=True,check=True).stdout.strip()
            andringar = subprocess.run(["git", "status", "--porcelain"],cwd=rot,capture_output=True,text=True,check=True).stdout
            status = "andrad" if andringar else "ren"
        except (OSError, subprocess.CalledProcessError):
            pass
    return Programproveniens(commit=commit,arbetskopia=status,innehallssumma=summa)


class Manifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skapad: datetime
    programversion: str
    programproveniens: Programproveniens = Field(default_factory=Programproveniens)
    git_commit: str
    metadata: dict[str, str]
    filer: dict[str, str]


def _git_commit() -> str:
    try:
        resultat = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent,
        )
    except (OSError, subprocess.CalledProcessError):
        return "okänd"
    return resultat.stdout.strip()


def _filer(mapp: Path) -> dict[str, str]:
    eget_manifest = mapp / MANIFESTNAMN
    return {
        sokvag.relative_to(mapp).as_posix(): for_fil(sokvag)
        for sokvag in sorted(mapp.rglob("*"))
        if sokvag.is_file() and sokvag != eget_manifest and not _systemfil(sokvag.name)
    }


def _systemfil(namn: str) -> bool:
    return namn in SYSTEMFILER or namn.startswith("._")


def skriv_manifest(mapp: Path, metadata: dict[str, str]) -> Manifest:
    """Skriver manifest.json med kontrollsumma för varje fil i mappen och dess undermappar."""
    manifest = Manifest(
        skapad=datetime.now(timezone.utc),
        programversion=__version__,
        git_commit=_git_commit(),
        programproveniens=programproveniens(),
        metadata=metadata,
        filer=_filer(mapp),
    )
    (mapp / MANIFESTNAMN).write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    return manifest


def skadat_manifest(mapp: Path) -> str:
    return f"Manifestet i {mapp} är skadat och kan inte läsas."


def las_manifest(mapp: Path) -> Manifest:
    """Läser manifestet. Ett manifest som inte går att läsa ger ManifestFel med instruktion om återställning."""
    try:
        return Manifest.model_validate_json((mapp / MANIFESTNAMN).read_text(encoding="utf-8"))
    except (ValidationError, UnicodeDecodeError, OSError) as fel:
        raise ManifestFel(
            f"{skadat_manifest(mapp)} Återställ mappen från säkerhetskopian och försök igen."
        ) from fel


def manifestets_metadata(mapp: Path, *nycklar: str) -> dict[str, str]:
    """Manifestets metadata. Saknas en uppgift som kedjan behöver ges ManifestFel med instruktion om återställning."""
    metadata = las_manifest(mapp).metadata
    saknade = [nyckel for nyckel in nycklar if nyckel not in metadata]
    if saknade:
        raise ManifestFel(
            f"{skadat_manifest(mapp)} Uppgifter saknas: {', '.join(saknade)}. "
            "Återställ mappen från säkerhetskopian och försök igen."
        )
    return metadata


def verifiera_manifest(mapp: Path) -> list[str]:
    """Jämför filerna med manifestet. Tom lista betyder att allt stämmer.

    Ett saknat eller skadat manifest rapporteras som en avvikelse, aldrig som en krasch.
    """
    if not (mapp / MANIFESTNAMN).is_file():
        return [f"Manifest saknas i {mapp}."]
    try:
        manifest = las_manifest(mapp)
    except ManifestFel:
        return [skadat_manifest(mapp)]
    nuvarande = _filer(mapp)
    fel = []
    for namn, summa in manifest.filer.items():
        if namn not in nuvarande:
            fel.append(f"Fil saknas: {namn}")
        elif nuvarande[namn] != summa:
            fel.append(f"Fil ändrad: {namn}")
    for namn in sorted(nuvarande.keys() - manifest.filer.keys()):
        fel.append(f"Fil finns inte i manifestet: {namn}")
    from riskanalys.dokument.rapportpaket_v8 import verifiera_rapportpaket
    from riskanalys.dokument.rapportpaket_v9 import ar_v9_paket,verifiera_rapportpaket_v9
    from riskanalys.dokument.rapportpaket_v10 import ar_v10_paket,verifiera_rapportpaket_v10
    if ar_v10_paket(mapp,manifest):verifiera_rapportpaket=verifiera_rapportpaket_v10
    elif ar_v9_paket(mapp,manifest):verifiera_rapportpaket=verifiera_rapportpaket_v9
    return [*fel, *verifiera_rapportpaket(mapp, manifest)]
