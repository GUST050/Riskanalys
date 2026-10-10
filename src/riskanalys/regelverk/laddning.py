"""Läser in regelbasen från YAML-filer och lydelsetexter (spec 5.1)."""

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ValidationError

from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.kontrollsumma import for_fil, for_text
from riskanalys.regelverk.modeller import (
    Bristmonster,
    Falt,
    Hot,
    Kalla,
    Kontroll,
    Krav,
    Lydelse,
    Metod,
    Regelbas,
    Regelpaket,
    Sarbarhet,
    Tillatelselista,
    Tjanst,
)

STANDARD_REGELBAS = Path(__file__).resolve().parents[3] / "regelbas"
LYDELSETEXTER = "lydelsetexter"
REGELBASFILER = frozenset({".yaml", ".txt"})

LISTFILER: dict[str, tuple[str, type[BaseModel]]] = {
    "falt": ("falt.yaml", Falt),
    "kallor": ("kallor.yaml", Kalla),
    "lydelser": ("lydelser.yaml", Lydelse),
    "hot": ("kataloger/hot.yaml", Hot),
    "sarbarheter": ("kataloger/sarbarheter.yaml", Sarbarhet),
    "kontroller": ("kataloger/kontroller.yaml", Kontroll),
    "tjanster": ("kataloger/tjanster.yaml", Tjanst),
    "bristmonster": ("kataloger/bristmonster.yaml", Bristmonster),
    "tillatelselistor": ("tillatelselistor.yaml", Tillatelselista),
}


class RegelbasFel(RiskanalysFel):
    """Regelbasen kan inte läsas in eller innehåller fel."""

    def __init__(self, fel: list[str]) -> None:
        super().__init__("Regelbasen har fel:\n" + "\n".join(f"- {rad}" for rad in fel))
        self.fel = fel


def regelbasfiler(rot: Path) -> list[Path]:
    """Alla filer i regelbasen (YAML och lydelsetexter), sorterade."""
    return sorted(sokvag for sokvag in rot.rglob("*") if sokvag.is_file() and sokvag.suffix in REGELBASFILER)


def regelbasens_kontrollsumma(rot: Path) -> str:
    """En kontrollsumma för hela regelbasen, byggd av varje fils kontrollsumma."""
    rader = [f"{sokvag.relative_to(rot).as_posix()} {for_fil(sokvag)}" for sokvag in regelbasfiler(rot)]
    return for_text("\n".join(rader))


def lydelsetextens_kontrollsumma(text: str) -> str:
    """Kontrollsumma för en paragraftext där alla blanktecken slagits ihop till ett mellanslag."""
    return for_text(" ".join(text.split()))


def ladda_regelbas(rot: Path = STANDARD_REGELBAS) -> Regelbas:
    if not rot.is_dir():
        raise RegelbasFel([f"Regelbasmappen {rot} finns inte."])
    fel: list[str] = []
    data: dict[str, Any] = {}
    for namn, (relativ, modell) in LISTFILER.items():
        data[namn] = _poster(rot, [rot / relativ], modell, fel)
    data["krav"] = _poster(rot, sorted((rot / "krav").glob("*.yaml")), Krav, fel)
    data["regelpaket"] = _poster(rot, sorted((rot / "regelpaket").glob("*.yaml")), Regelpaket, fel, en_per_fil=True)
    version = _las_yaml(rot / "version.yaml", fel)
    metod = _las_yaml(rot / "beslutstabeller" / "metod.yaml", fel)
    fel += _lydelsetexter(rot, data["lydelser"].values())
    if fel:
        raise RegelbasFel(fel)
    try:
        return Regelbas(
            version=str(version["regelbas_version"]),
            metod=Metod.model_validate(metod),
            kontrollsumma=regelbasens_kontrollsumma(rot),
            **data,
        )
    except (ValidationError, KeyError, TypeError) as undantag:
        raise RegelbasFel([f"version.yaml eller beslutstabeller/metod.yaml: {undantag}"]) from undantag


def _lydelsetexter(rot: Path, lydelser: Iterable[Lydelse]) -> list[str]:
    """Kontrollerar att varje lydelse har sin text och att texten stämmer med kontrollsumman."""
    fel = []
    for lydelse in lydelser:
        relativ = f"{LYDELSETEXTER}/{lydelse.id}.txt"
        sokvag = rot / relativ
        if not sokvag.is_file():
            fel.append(f"{relativ}: texten till lydelsen {lydelse.id} saknas.")
        elif lydelsetextens_kontrollsumma(sokvag.read_text(encoding="utf-8")) != lydelse.text_kontrollsumma:
            fel.append(f"{relativ}: texten stämmer inte med text_kontrollsumma för {lydelse.id}.")
    return fel


def _las_yaml(sokvag: Path, fel: list[str]) -> Any:
    try:
        return yaml.safe_load(sokvag.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fel.append(f"Filen saknas: {sokvag}")
    except yaml.YAMLError as undantag:
        fel.append(f"Ogiltig YAML i {sokvag}: {undantag}")
    return None


def _poster(
    rot: Path,
    filer: list[Path],
    modell: type[BaseModel],
    fel: list[str],
    en_per_fil: bool = False,
) -> dict[str, Any]:
    resultat: dict[str, Any] = {}
    for fil in filer:
        relativ = fil.relative_to(rot).as_posix()
        innehall = _las_yaml(fil, fel)
        if innehall is None:
            continue
        poster = [innehall] if en_per_fil else innehall
        if not isinstance(poster, list):
            fel.append(f"{relativ}: ska innehålla en lista.")
            continue
        for nummer, post in enumerate(poster, start=1):
            try:
                objekt = modell.model_validate(post)
            except ValidationError as undantag:
                fel.append(f"{relativ}, post {nummer}: {_kort(undantag)}")
                continue
            if objekt.id in resultat:
                fel.append(f"{relativ}: ID:t {objekt.id} finns redan.")
                continue
            resultat[objekt.id] = objekt
    return resultat


def _kort(undantag: ValidationError) -> str:
    return "; ".join(
        f"{'.'.join(str(del_) for del_ in fel['loc']) or 'posten'}: {fel['msg']}" for fel in undantag.errors()
    )
