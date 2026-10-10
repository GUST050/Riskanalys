"""Separat versionsbunden granskning av syntetiska tillsynsfall."""

import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.yamlfil import las_yaml, spara_yaml
from riskanalys.regelverk.modeller import Strikt, _summa
from riskanalys.regelverk.sakkunnig import Objektbeslut


class Facitgranskning(Strikt):
    version: str
    datum: date
    granskningsdatum: date
    kontrollsumma: str
    granskare: str
    kompetens: str
    oberoende: bool
    objekt: dict[str, Objektbeslut]


def facitobjekt(facit: dict[str, Any]) -> dict[str, str]:
    """Samla fynd och kontrollvarianter med deras egna innehållssummor."""
    fynd = [fynd for fall in facit["fall"] for fynd in fall["forvantade_fynd"]]
    poster = [*fynd, *facit.get("kontrollvarianter", [])]
    return {post["id"]: _summa(post) for post in poster}


def exportera_facitmall(facit: dict[str, Any], datum: date, fil: Path) -> None:
    """Exportera obesvarade beslut; ingen status i det kanoniska facitet ändras."""
    mall = Facitgranskning(
        version=facit["version"], datum=datum, granskningsdatum=datum,
        kontrollsumma=_summa(facit), granskare="", kompetens="", oberoende=False,
        objekt={id: Objektbeslut(beslut="ej_granskad") for id in facitobjekt(facit)},
    )
    spara_yaml(fil, mall.model_dump(mode="python"))


def kontrollera_facitbeslut(beslut: Facitgranskning, facit: dict[str, Any] | None) -> None:
    """Avvisa förändrat underlag, ofullständiga beslut och saknad attestmetadata."""
    if not facit or beslut.version != facit["version"] or beslut.kontrollsumma != _summa(facit):
        raise RiskanalysFel("Facitets version eller innehåll har ändrats. Exportera och granska facitet på nytt.")
    if (beslut.granskningsdatum < beslut.datum or not beslut.granskare.strip()
            or not beslut.kompetens.strip() or not beslut.oberoende):
        raise RiskanalysFel("Ange facitgranskare, kompetens, oberoende och granskningsdatum efter underlagets datum.")
    if set(beslut.objekt) != set(facitobjekt(facit)):
        raise RiskanalysFel("Facitgranskningen har saknade eller okända objekt. Exportera en ny facitmall.")
    if any(post.beslut == "ej_granskad" or not post.kommentar.strip() for post in beslut.objekt.values()):
        raise RiskanalysFel("Varje facitobjekt kräver beslut verifierad/ändras och kommentar före import.")


def las_facitgranskning(fil: Path, facit: dict[str, Any] | None) -> Facitgranskning:
    """Läs och kontrollera beslut mot exakt den facitversion som ska användas."""
    try:
        beslut = Facitgranskning.model_validate(las_yaml(fil))
    except ValidationError as exc:
        raise RiskanalysFel(f"Facitgranskningsfilen {fil} har fel. Rätta mot den exporterade mallen.") from exc
    kontrollera_facitbeslut(beslut, facit)
    return beslut


def tillampa_facitgranskning(regelbasrot: Path, beslut: Facitgranskning) -> None:
    """Spara en lokal attest atomiskt utan att ändra regelpaketens godkännanden."""
    from riskanalys.regelverk.laddning import ladda_regelbas

    kontrollera_facitbeslut(beslut, ladda_regelbas(regelbasrot).facit)
    fd, namn = tempfile.mkstemp(prefix=".facitgranskning-", suffix=".tmp", dir=regelbasrot)
    os.close(fd)
    tmp = Path(namn)
    try:
        spara_yaml(tmp, beslut.model_dump(mode="python"))
        kontrollera_facitbeslut(beslut, ladda_regelbas(regelbasrot).facit)
        os.replace(tmp, regelbasrot / "facitgranskning.yaml")
    finally:
        tmp.unlink(missing_ok=True)
