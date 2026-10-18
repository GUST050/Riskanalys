"""Smal, innehållsbunden identitet för den granskade riskberäkningen."""
import ast
import json
import platform
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path, PurePosixPath
from typing import Literal

from pydantic import Field, model_validator

from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.kontrollsumma import for_fil, for_text
from riskanalys.regelverk.modeller import KONTROLLSUMMA, Regelbas, Strikt

MODELLROT = Path(__file__).resolve().parents[1]
# Avsiktlig förteckning: också fristående kundmodell och sektorsreferens ingår.
MODELLMODULER = (
    'bedomning.erfarenheter', 'bedomning.kundmodell.modeller',
    'bedomning.kundmodell.pep', 'bedomning.kundmodell.tabeller',
    'bedomning.kundmodell.utvardering', 'bedomning.modeller', 'bedomning.motor',
    'bedomning.omfattning', 'bedomning.sanktioner', 'bedomning.scenarier', 'bedomning.sektorsrisk',
    'fel', 'lagring.kontrollsumma', 'profil.modeller', 'profil.omfattning',
    'regelverk.modeller', 'regelverk.tillsyn', 'regelverk.urval', 'regelverk.villkor',
)
MODELLPAKET = ('bedomning', 'bedomning.kundmodell', 'lagring', 'profil', 'regelverk')
MODELLFILER = tuple(sorted(
    [f"src/riskanalys/{m.replace('.', '/')}.py" for m in MODELLMODULER]
    + [f"src/riskanalys/{m.replace('.', '/')}/__init__.py" for m in MODELLPAKET]
))


class Modellfil(Strikt):
    fil: str
    kontrollsumma: str = Field(pattern=KONTROLLSUMMA)


class Modellfilmanifest(Strikt):
    schema_version: Literal[1] = 1
    modellbindning: str = Field(pattern=KONTROLLSUMMA)
    regelbas_kontrollsumma: str = Field(pattern=KONTROLLSUMMA)
    filer: tuple[Modellfil, ...]

    @model_validator(mode='after')
    def kontrollera_inventarium(self):
        namn = tuple(rad.fil for rad in self.filer)
        if not namn or namn != tuple(sorted(set(namn))):
            raise ValueError('Modellfilförteckningen måste vara unik och sorterad.')
        for fil in namn:
            sokvag = PurePosixPath(fil)
            if (not fil.startswith('src/riskanalys/') or not fil.endswith('.py')
                    or '\\' in fil or sokvag.as_posix() != fil
                    or any(del_ in {'', '.', '..'} for del_ in fil.split('/'))):
                raise ValueError('Modellfilförteckningen har en otillåten sökväg.')
        if self.modellbindning != _bindning(self.regelbas_kontrollsumma, self.filer):
            raise ValueError('Modellbindningen stämmer inte med filförteckningen.')
        return self


class Modellmiljo(Strikt):
    python: str
    pydantic: str
    pyyaml: str
    python_docx: str
    anthropic: str


def modellmiljo() -> Modellmiljo:
    def installerad(namn: str) -> str:
        try:
            return version(namn)
        except PackageNotFoundError:
            return 'ej installerat'
    return Modellmiljo(python=platform.python_version(), pydantic=installerad('pydantic'),
                       pyyaml=installerad('PyYAML'), python_docx=installerad('python-docx'),
                       anthropic=installerad('anthropic'))


def _bindning(regelsumma: str, filer: tuple[Modellfil, ...]) -> str:
    return for_text(json.dumps({'schema_version': 1, 'regelbas': regelsumma,
                               'filer': [f.model_dump() for f in filer]},
                              sort_keys=True, separators=(',', ':'), ensure_ascii=False))


def _rotmetadata() -> None:
    trad = ast.parse((MODELLROT / '__init__.py').read_text(encoding='utf-8'))
    for nod in trad.body:
        if isinstance(nod, ast.Expr) and isinstance(nod.value, ast.Constant) and isinstance(nod.value.value, str):
            continue
        if (isinstance(nod, ast.Assign) and len(nod.targets) == 1
                and isinstance(nod.targets[0], ast.Name) and nod.targets[0].id == '__version__'
                and isinstance(nod.value, ast.Constant) and isinstance(nod.value.value, str)):
            continue
        raise RiskanalysFel('Rotpaketet innehåller annat än versionsmetadata. Granska modellfilförteckningen.')


def _kontrollera_importer(fil: str) -> None:
    trad = ast.parse((MODELLROT / Path(fil).relative_to('src/riskanalys')).read_text(encoding='utf-8'))
    relativ = Path(fil).relative_to('src').with_suffix('').parts
    modul = '.'.join(relativ[:-1] if relativ[-1] == '__init__' else relativ)
    paket = modul if relativ[-1] == '__init__' else modul.rsplit('.', 1)[0]
    tillatna = {'riskanalys.' + m for m in (*MODELLMODULER, *MODELLPAKET)}
    for nod in ast.walk(trad):
        # Även enkla alias (hamta = __import__ / builtins.__import__) är förbjudna.
        if ((isinstance(nod, ast.Name) and isinstance(nod.ctx, ast.Load)
             and nod.id in {'__import__', 'eval', 'exec'})
                or (isinstance(nod, ast.Attribute) and nod.attr in {'__import__', 'eval', 'exec'})):
            raise RiskanalysFel('Dynamisk kod/import i modellfil. Granska modellfilförteckningen.')
        namn = []
        if isinstance(nod, ast.Import):
            # En naken punktimport binder rotpaketet och öppnar dess uteslutna metadata.
            if any(a.name.startswith('riskanalys.') and a.asname is None for a in nod.names):
                raise RiskanalysFel('Importen exponerar rotpaketets metadata. Använd en explicit modellimport.')
            namn = [alias.name for alias in nod.names]
        elif isinstance(nod, ast.ImportFrom):
            bas = nod.module or ''
            if bas == 'builtins' and any(a.name in {'__import__', 'eval', 'exec'} for a in nod.names):
                raise RiskanalysFel('Alias till dynamisk kod/import i modellfil. Granska modellfilförteckningen.')
            if nod.level:
                delar = paket.split('.')
                bas = '.'.join(delar[:len(delar) - nod.level + 1] + ([bas] if bas else []))
            namn = [bas]
            if bas in {'riskanalys', *('riskanalys.' + p for p in MODELLPAKET)}:
                # Paketimport kan dölja både metadata och tidigare oregistrerade hjälpfiler.
                namn = [bas + '.' + alias.name for alias in nod.names]
        elif isinstance(nod, ast.Call):
            if ((isinstance(nod.func, ast.Name) and nod.func.id in {'__import__', 'eval', 'exec'})
                    or (isinstance(nod.func, ast.Attribute) and nod.func.attr in {'import_module', '__import__'})):
                raise RiskanalysFel('Dynamisk kod/import i modellfil. Granska modellfilförteckningen.')
        for beroende in namn:
            if beroende == 'importlib' or beroende.startswith('importlib.'):
                raise RiskanalysFel('Dynamisk import i modellfil. Granska modellfilförteckningen.')
            if beroende == 'riskanalys' or (beroende.startswith('riskanalys.') and beroende not in tillatna):
                raise RiskanalysFel(f'Oregistrerat modellberoende {beroende}. Granska modellfilförteckningen.')


def modellfilmanifest(rb: Regelbas) -> Modellfilmanifest:
    try:
        _rotmetadata()
        for fil in MODELLFILER:
            _kontrollera_importer(fil)
        filer = tuple(Modellfil(fil=fil, kontrollsumma=for_fil(MODELLROT / Path(fil).relative_to('src/riskanalys'))) for fil in MODELLFILER)
        return Modellfilmanifest(modellbindning=_bindning(rb.kontrollsumma, filer),
                                 regelbas_kontrollsumma=rb.kontrollsumma, filer=filer)
    except (OSError, SyntaxError, ValueError) as fel:
        raise RiskanalysFel('Modellfiler saknas eller är ogiltiga. Återställ och granska modellfilförteckningen.') from fel


def modellbindning(rb: Regelbas) -> str:
    return modellfilmanifest(rb).modellbindning
