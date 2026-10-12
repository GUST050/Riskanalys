"""SHA-256-kontrollsummor för filer och text."""

import hashlib
from pathlib import Path

_BLOCKSTORLEK = 65536


def for_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def for_text(text: str) -> str:
    return for_bytes(text.encode("utf-8"))


def for_fil(sokvag: Path) -> str:
    summa = hashlib.sha256()
    with sokvag.open("rb") as fil:
        for block in iter(lambda: fil.read(_BLOCKSTORLEK), b""):
            summa.update(block)
    return "sha256:" + summa.hexdigest()
