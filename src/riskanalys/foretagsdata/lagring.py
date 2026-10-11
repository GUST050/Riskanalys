"""Privata registerbilder och atomisk aktuell pekare utanför Git."""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import re
import tempfile
from pydantic import ValidationError
from riskanalys.fel import RiskanalysFel
from riskanalys.foretagsdata.modeller import Registerbild
from riskanalys.profil.lagring import PROFILFIL


@contextmanager
def registerlas(byramapp: Path):
    mapp = byramapp / 'register'
    try:
        byramapp.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        byramapp.mkdir(exist_ok=True, mode=0o700)
        mapp.mkdir(exist_ok=True, mode=0o700)
        fd = os.open(mapp / '.skrivlas',os.O_CREAT | os.O_RDWR,0o600)
        with os.fdopen(fd,'w') as fil:
            fcntl.flock(fil,fcntl.LOCK_EX)
            yield mapp
    except OSError:
        raise RiskanalysFel('Registerunderlaget kunde inte sparas/läsas. Kontrollera skrivbehörighet och ledigt utrymme.') from None


def _atomiskt(path: Path, raw: bytes):
    fd,temp = tempfile.mkstemp(dir=path.parent,suffix='.tmp')
    try:
        with os.fdopen(fd,'wb') as fil:
            fil.write(raw);fil.flush();os.fsync(fil.fileno())
        os.replace(temp,path)
        fd = os.open(path.parent,os.O_RDONLY)
        try:os.fsync(fd)
        finally:os.close(fd)
    finally:
        if os.path.exists(temp):os.unlink(temp)


def las_bild(byramapp: Path) -> Registerbild | None:
    mapp = byramapp / 'register'
    try:
        pekare = mapp / 'aktuell.json'
        if not pekare.exists():
            return None
        summa = json.loads(pekare.read_text())['summa']
        if not isinstance(summa,str) or not re.fullmatch(r'[a-f0-9]{64}',summa):
            raise ValueError('summa')
        path = mapp / f'{summa}.json'
        if path.stat().st_size>131072:
            raise ValueError('storlek')
        bild = Registerbild.model_validate_json(path.read_bytes())
        if bild.summa != summa:
            raise ValueError('summa')
        return bild
    except (OSError, ValueError, KeyError, TypeError, ValidationError):
        raise RiskanalysFel('Registerunderlagets kontrollsumma eller format stämmer inte. Återställ registermappen från säkerhetskopian innan nya uppgifter används.') from None


def spara_bild(byramapp: Path, bild: Registerbild):
    with registerlas(byramapp) as mapp:
        from riskanalys.profil.lagring import las_profil
        if (byramapp / PROFILFIL).is_file() and bild.hamtningsdag > las_profil(byramapp).byra.datum:
            raise RiskanalysFel('Registerbilden är hämtad efter bedömningsdatumet och kan inte styrka en historisk bedömning. Den tidigare bilden behålls. Starta ett nytt intag för en ny bedömning.')
        fore = las_bild(byramapp)
        if fore and (byramapp / PROFILFIL).is_file() and fore.orgnr != bild.orgnr:
            raise RiskanalysFel('Underlaget gäller en annan juridisk person än byråns sparade registerbild. Starta ett separat byråintag för ett annat organisationsnummer.')
        path = mapp / f'{bild.summa}.json'
        if path.exists():
            if path.read_bytes()!=bild.model_dump_json().encode():
                raise RiskanalysFel('En tidigare registerbild har ändrats. Återställ den från säkerhetskopian.')
        else:
            _atomiskt(path,bild.model_dump_json().encode())
        _atomiskt(mapp/'aktuell.json',json.dumps({'summa':bild.summa}).encode())
