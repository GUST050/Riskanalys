"""Framtida EU-utkast är aldrig en operativ regelbas."""
from datetime import date
from pathlib import Path
from typing import Literal
from pydantic import ValidationError
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.yamlfil import las_yaml
from riskanalys.lagring.manifest import verifiera_manifest
from riskanalys.regelverk.modeller import Strikt

class Artikelrad(Strikt):
    id: str
    status: Literal['relevant','ej_relevant','aterstaende']
    motivering: str
    motsvarigheter: tuple[str,...]
    text: str
    delkrav: tuple[str,...]

class AmlrUtkast(Strikt):
    id: str
    status: Literal['utkast']
    tillampas_fran: date
    artiklar: tuple[Artikelrad,...]


def ladda_amlr_utkast(rot:Path)->AmlrUtkast:
    avvikelser = verifiera_manifest(rot)
    if avvikelser:
        raise RiskanalysFel('AMLR-utkastets manifest stämmer inte. Återställ det bevarade utkastet eller dokumentera och manifestera en ny utkastversion. ' + '; '.join(avvikelser))
    try:
        u=AmlrUtkast(**las_yaml(rot/'paket.yaml'),artiklar=las_yaml(rot/'kravkarta.yaml'))
    except (ValidationError,TypeError) as e:
        raise RiskanalysFel(f'AMLR-utkastet {rot} har fel. Rätta mot kravkartan.') from e
    ids=[a.id for a in u.artiklar]
    forvantat={f'Artikel {i}' for i in range(1,91)}|{f'Bilaga {i}' for i in ('I','II','III','IV','V','VI')}
    if len(ids)!=len(set(ids)) or set(ids)!=forvantat or any(not a.motivering.strip() for a in u.artiklar):
        raise RiskanalysFel('AMLR-utkastet saknar full inventering eller motivering. Rätta alla 90 artiklar och sex bilagor.')
    return u
