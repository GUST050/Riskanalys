"""Läs och spara byråprofilen i byråns datamapp."""

from pathlib import Path
import fcntl
import hashlib
import os
import tempfile

import yaml

from pydantic import ValidationError

from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.yamlfil import las_yaml_text
from riskanalys.profil.modeller import Profil

PROFILFIL = Path("profil") / "profil.yaml"


def profilrevision(profil: Profil) -> str:
    return hashlib.sha256(profil.model_dump_json().encode()).hexdigest()


def spara_profil(byramapp: Path, profil: Profil, revision: str | None = None) -> Path:
    """Privat, atomisk skrivning; CAS skyddar intagets öppna flikar och historik bevarar tidigare bytes."""
    sokvag = byramapp / PROFILFIL
    temp = None
    try:
        sokvag.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd = os.open(sokvag.parent / '.skrivlas', os.O_CREAT | os.O_RDWR, 0o600)
        with os.fdopen(fd, 'w') as las:
            fcntl.flock(las, fcntl.LOCK_EX)
            if revision is not None:
                faktisk = profilrevision(las_profil(byramapp)) if sokvag.exists() else ''
                if faktisk != revision:
                    raise RiskanalysFel('Profilen har ändrats i en annan flik eller ett annat program. Läs om sidan före nästa svar.')
            if sokvag.exists():
                tidigare = sokvag.read_bytes()
                historik = sokvag.parent / 'historik'
                historik.mkdir(exist_ok=True, mode=0o700)
                h = historik / (hashlib.sha256(tidigare).hexdigest() + '.yaml')
                if not h.exists():
                    with os.fdopen(os.open(h, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'wb') as fil:
                        fil.write(tidigare)
                        fil.flush()
                        os.fsync(fil.fileno())
            fd, temp = tempfile.mkstemp(suffix='.tmp', dir=sokvag.parent)
            with os.fdopen(fd, 'w', encoding='utf-8') as fil:
                yaml.safe_dump(profil.model_dump(mode='python'), fil, allow_unicode=True, sort_keys=False)
                fil.flush()
                os.fsync(fil.fileno())
            os.replace(temp, sokvag)
            temp = None
            fd = os.open(sokvag.parent, os.O_RDONLY)
            try:os.fsync(fd)
            finally:os.close(fd)
        return sokvag
    except OSError as exc:
        raise RiskanalysFel('Profilen kunde inte sparas. Kontrollera ledigt utrymme och skrivbehörighet; tidigare profil finns kvar om namnbytet inte utfördes.') from exc
    finally:
        if temp and os.path.exists(temp):os.unlink(temp)


def las_profil(byramapp: Path) -> Profil:
    return las_profilsnapshot(byramapp)[0]


def las_profilsnapshot(byramapp: Path) -> tuple[Profil, bytes]:
    """Validera och återge exakt samma bytes; profilspararen publicerar med atomiskt namnbyte."""
    sokvag = byramapp / PROFILFIL
    if not sokvag.is_file():
        raise RiskanalysFel(f"Profilen saknas i {byramapp}. Skapa byrån med 'riskanalys ny'.")
    try:
        innehall = sokvag.read_bytes()
        data = las_yaml_text(innehall.decode('utf-8'))
    except (OSError, UnicodeDecodeError) as fel:
        raise RiskanalysFel(f"Filen {sokvag} kan inte läsas som UTF-8. Rätta filen eller återställ från säkerhetskopian.") from fel
    except yaml.YAMLError as fel:
        raise RiskanalysFel(f"Filen {sokvag} är inte giltig YAML: {fel}") from fel
    try:
        return Profil.model_validate(data), innehall
    except ValidationError as fel:
        platser = ", ".join(".".join(str(del_) for del_ in post["loc"]) for post in fel.errors()[:3])
        raise RiskanalysFel(
            f"Profilen i {sokvag} kan inte läsas. Kontrollera {platser}. "
            "Rätta filen eller återställ den från säkerhetskopian."
        ) from fel
