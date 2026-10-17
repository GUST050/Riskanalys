"""Projektets frysta rapportpaket; export skapar aldrig sakkunnigattest."""
import json
import shutil
import stat
import tempfile
from datetime import date
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, ValidationError

from riskanalys.drift.modellidentitet import Modellfilmanifest, modellfilmanifest, modellmiljo
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.kontrollsumma import for_bytes, for_fil, for_text
from riskanalys.lagring.manifest import las_manifest, skriv_manifest, verifiera_manifest
from riskanalys.regelverk.modeller import KONTROLLSUMMA, Regelbas, Sakkunnig, Strikt

Text = Annotated[str, Field(min_length=1, pattern=r'\S')]


class Modellvalidering(Strikt):
    schema_version: Literal[1] = 1
    modellbindning: str = Field(pattern=KONTROLLSUMMA)
    modellfiler_kontrollsumma: str = Field(pattern=KONTROLLSUMMA)
    rapportfil: Literal['modellvalidering.pdf'] = 'modellvalidering.pdf'
    rapport_kontrollsumma: str = Field(pattern=KONTROLLSUMMA)
    rapportversion: Text
    datum: date
    tillampningsomrade: Text
    fall_och_facit: Text
    faktiska_utfall: Text
    avvikelser: Text
    begransningar: Text
    verkliga_driftobservationer: Text
    m1_beslut: Literal['ej_provat', 'godkant', 'andring_kravs']
    sakkunnig: Sakkunnig = Field(default_factory=Sakkunnig)


def valideringens_innehallssumma(rapport: Modellvalidering) -> str:
    return for_text(json.dumps(rapport.model_dump(mode='json', exclude={'sakkunnig'}),
                              sort_keys=True, separators=(',', ':'), ensure_ascii=False))


def kontrollera_rapportkoppling(rapport: Modellvalidering, inventariebytes: bytes, pdfbytes: bytes) -> Modellfilmanifest:
    inventarium = Modellfilmanifest.model_validate_json(inventariebytes)
    if (for_bytes(inventariebytes) != rapport.modellfiler_kontrollsumma
            or for_bytes(pdfbytes) != rapport.rapport_kontrollsumma
            or inventarium.modellbindning != rapport.modellbindning):
        raise RiskanalysFel('Projektets modell-, fil- och rapportkoppling stämmer inte. Importera rätt fryst rapportpaket.')
    return inventarium


def exportera_modellvalidering(malmapp: Path, rb: Regelbas, rapport: Modellvalidering, pdf: Path) -> Path:
    if malmapp.exists():
        raise RiskanalysFel('Målmappen finns redan. Välj en ny mapp för rapportpaketet.')
    arbetsmapp = None
    reserverad = False
    try:
        # Revalidera även objekt som skapats med model_copy/model_construct.
        rapport = Modellvalidering.model_validate(rapport.model_dump(mode='json'))
        inventarium = modellfilmanifest(rb)
        inventariebytes = inventarium.model_dump_json(indent=2).encode('utf-8')
        pdfbytes = pdf.read_bytes()
        if not pdfbytes.startswith(b'%PDF-'):
            raise RiskanalysFel('Rapportfilen är inte en PDF. Välj projektets befintliga PDF-rapport.')
        kontrollera_rapportkoppling(rapport, inventariebytes, pdfbytes)
        malmapp.parent.mkdir(parents=True, exist_ok=True)
        arbetsmapp = Path(tempfile.mkdtemp(prefix='.modellrapport-', dir=malmapp.parent))
        (arbetsmapp / 'modellvalidering.json').write_text(rapport.model_dump_json(indent=2), encoding='utf-8')
        (arbetsmapp / 'modellfiler.json').write_bytes(inventariebytes)
        (arbetsmapp / 'modellvalidering.pdf').write_bytes(pdfbytes)
        skriv_manifest(arbetsmapp, {'typ': 'modellvalidering', 'modellbindning': rapport.modellbindning,
                                  'rapport_kontrollsumma': rapport.rapport_kontrollsumma,
                                  'miljo': modellmiljo().model_dump_json()})
        # Ingen ersättning av en tidigare leverans, inte heller vid tom befintlig mapp.
        malmapp.mkdir()
        reserverad = True
        arbetsmapp.rename(malmapp)
        reserverad = False
        return malmapp
    except (OSError, ValueError) as fel:
        raise RiskanalysFel('Rapportpaketet kunde inte skapas. Kontrollera rapporten och välj en ny målmapp.') from fel
    finally:
        if reserverad:
            malmapp.rmdir()
        if arbetsmapp is not None and arbetsmapp.exists():
            shutil.rmtree(arbetsmapp)


def las_modellvalidering(mapp: Path) -> Modellvalidering:
    try:
        namn = {'manifest.json', 'modellvalidering.json', 'modellfiler.json', 'modellvalidering.pdf'}
        if (mapp.is_symlink() or {p.name for p in mapp.iterdir()} != namn
                or any(not stat.S_ISREG((mapp / n).lstat().st_mode) for n in namn)):
            raise RiskanalysFel('Rapportpaketet får bara innehålla de fyra vanliga leveransfilerna, utan länkar.')
        if verifiera_manifest(mapp):
            raise RiskanalysFel('Rapportpaketet har ändrats. Importera projektets oförändrade leverans.')
        rapport = Modellvalidering.model_validate_json((mapp / 'modellvalidering.json').read_bytes())
        kontrollera_rapportkoppling(rapport, (mapp / 'modellfiler.json').read_bytes(),
                                   (mapp / 'modellvalidering.pdf').read_bytes())
        metadata = las_manifest(mapp).metadata
        if (metadata.get('typ') != 'modellvalidering'
                or metadata.get('modellbindning') != rapport.modellbindning
                or metadata.get('rapport_kontrollsumma') != rapport.rapport_kontrollsumma):
            raise RiskanalysFel('Rapportpaketets manifest stämmer inte med rapporten.')
        return rapport
    except (OSError, ValueError, ValidationError) as fel:
        raise RiskanalysFel('Rapportpaketet är skadat. Importera projektets oförändrade leverans.') from fel
