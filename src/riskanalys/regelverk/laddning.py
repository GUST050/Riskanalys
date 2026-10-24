"""Läser in regelbasen från YAML-filer och lydelsetexter (spec 5.1)."""

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import json
import yaml
from pydantic import BaseModel, ValidationError

from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.yamlfil import las_text, las_yaml_text
from riskanalys.lagring.kontrollsumma import for_fil, for_text
from riskanalys.regelverk.modeller import (
    Bristmonster,
    Falt,
    Hot,
    IndikatorLagreRisk,
    Metodbeslut,
    InventeradLydelse,
    Kalla,
    Kontroll,
    Kundmall,
    Kundrad,
    Krav,
    Lydelse,
    Metod,
    Maldefinition,
    Regelbas,
    Regelpaket,
    Sarbarhet,
    Sektorsreferens,
    Skalmappning,
    Sanktionsmetod,
    Tillatelselista,
    Tillamplighetsrad,
    Tjanst,
)

STANDARD_REGELBAS = Path(__file__).resolve().parents[3] / "regelbas"
LYDELSETEXTER = "lydelsetexter"
REGELBASFILER = frozenset({".yaml", ".txt", ".json"})

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
    """Operativa filer; forskningsfacit och dess attest har en separat bindning."""
    separat = {"referensdata/facit.json", "facitgranskning.yaml"}
    return sorted(
        sokvag for sokvag in rot.rglob("*")
        if sokvag.is_file()
        and "utkast" not in sokvag.relative_to(rot).parts
        and sokvag.relative_to(rot).as_posix() not in separat
        and sokvag.suffix in REGELBASFILER
    )


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
    lagre = rot / 'kataloger/lagre_risk.yaml'
    data['lagre_risk'] = _poster(rot, [lagre], IndikatorLagreRisk, fel) if lagre.exists() else {}
    beslut = rot / 'beslutstabeller/metodbeslut.yaml'
    data['metodbeslut'] = _poster(rot, [beslut], Metodbeslut, fel) if beslut.exists() else {}
    data["regelpaket"] = _poster(rot, sorted((rot / "regelpaket").glob("*.yaml")), Regelpaket, fel, en_per_fil=True)
    inventarium = []
    for fil in sorted((rot / "inventering").glob("*.yaml")):
        poster = _las_yaml(fil, fel)
        if not isinstance(poster, list):
            fel.append(f"{fil}: inventariet ska vara en lista.")
            continue
        for nummer, post in enumerate(poster, start=1):
            try:
                inventarium.append(InventeradLydelse.model_validate(post))
            except ValidationError as exc:
                fel.append(f"{fil}, post {nummer}: {_kort(exc)}")
    data["inventarium"] = tuple(inventarium)
    tillamplighet = rot / "beslutstabeller/tillamplighet.yaml"
    data["tillamplighet"] = _poster(rot, [tillamplighet], Tillamplighetsrad, fel) if tillamplighet.exists() else {}
    malfil = rot / "mal.yaml"
    data["maldefinitioner"] = _poster(rot, [malfil], Maldefinition, fel) if malfil.exists() else {}
    sektorfil = rot / "referensdata/sektorsrisk.yaml"
    data["sektorsreferenser"] = _poster(rot, [sektorfil], Sektorsreferens, fel) if sektorfil.exists() else {}
    skalfil = rot / "beslutstabeller/skalmappning.yaml"
    if skalfil.exists():
        try:
            data["skalmappning"] = Skalmappning.model_validate(_las_yaml(skalfil, fel))
        except ValidationError as exc:
            fel.append(f"{skalfil}: {_kort(exc)}")
    sankfil = rot / "beslutstabeller/sanktionsrisk.yaml"
    if sankfil.exists():
        try:
            data["sanktionsmetod"] = Sanktionsmetod.model_validate(_las_yaml(sankfil, fel))
        except ValidationError as exc:
            fel.append(f"{sankfil}: {_kort(exc)}")
    kundfil = rot / "kundfalt.yaml"
    if kundfil.exists():
        kundfalt = _poster(rot, [kundfil], Falt, fel)
        kundrader = _poster(rot, sorted((rot / "beslutstabeller/kundmodell").glob("*-*.yaml")), Kundrad, fel)
        configfil = rot / "beslutstabeller/kundmodell.yaml"
        config = _las_yaml(configfil, fel) if configfil.exists() else {}
        try:
            data["kundmall"] = Kundmall(falt=kundfalt, rader=tuple(kundrader.values()), lydelser=data["lydelser"], **(config or {}))
        except ValidationError as exc:
            fel.append(f"kundmodell: {_kort(exc)}")
    version = _las_yaml(rot / "version.yaml", fel)
    metod = _las_yaml(rot / "beslutstabeller" / "metod.yaml", fel)
    fel += _lydelsetexter(rot, data["lydelser"].values())
    if fel:
        raise RegelbasFel(fel)
    try:
        regelbas = Regelbas(
            version=str(version["regelbas_version"]),
            metod=Metod.model_validate(metod),
            kontrollsumma=regelbasens_kontrollsumma(rot),
            **data,
        )
        facitfil = rot / "referensdata/facit.json"
        if facitfil.exists():
            regelbas = regelbas.model_copy(update={"facit": json.loads(facitfil.read_text(encoding="utf-8"))})
        granskningsfil = rot / "granskning.yaml"
        if granskningsfil.exists():
            from riskanalys.regelverk.sakkunnig import applicera_attester, Granskningsbeslut
            data = _las_yaml(granskningsfil, fel)
            if not isinstance(data, dict):
                raise RegelbasFel([f"{granskningsfil}: återställ attestfilen från granskningen."])
            if "beslut" in data:
                if set(data) != {"beslut"} or not isinstance(data["beslut"], dict):
                    raise RegelbasFel([f"{granskningsfil}: fel attestregister. Återställ filen."])
                for paket_id, post in sorted(data["beslut"].items()):
                    beslut = Granskningsbeslut.model_validate(post)
                    if beslut.paket != paket_id:
                        raise RegelbasFel([f"{granskningsfil}: paket-ID skiljer sig från beslutet. Rätta filen."])
                    regelbas = applicera_attester(regelbas, beslut)
            else:
                regelbas = applicera_attester(regelbas, Granskningsbeslut.model_validate(data))
        return regelbas
    except (ValidationError, KeyError, TypeError, ValueError, UnicodeDecodeError, OSError) as undantag:
        raise RegelbasFel([f"version.yaml eller beslutstabeller/metod.yaml: {undantag}"]) from undantag


def _lydelsetexter(rot: Path, lydelser: Iterable[Lydelse]) -> list[str]:
    """Kontrollerar att varje lydelse har sin text och att texten stämmer med kontrollsumman."""
    fel = []
    for lydelse in lydelser:
        relativ = f"{LYDELSETEXTER}/{lydelse.id}.txt"
        sokvag = rot / relativ
        if not sokvag.is_file():
            fel.append(f"{relativ}: texten till lydelsen {lydelse.id} saknas.")
        elif lydelsetextens_kontrollsumma(las_text(sokvag)) != lydelse.text_kontrollsumma:
            fel.append(f"{relativ}: texten stämmer inte med text_kontrollsumma för {lydelse.id}.")
    return fel


def _las_yaml(sokvag: Path, fel: list[str]) -> Any:
    try:
        return las_yaml_text(sokvag.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fel.append(f"Filen saknas: {sokvag}")
    except RiskanalysFel as undantag:
        fel.append(str(undantag))
    except (yaml.YAMLError, UnicodeDecodeError, OSError) as undantag:
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
