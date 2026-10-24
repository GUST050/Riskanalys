"""Importkontrakten ska fånga verkliga direkta och transitiva förbjudna vägar."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import pytest


@pytest.mark.parametrize('kant',['direkt','indirekt'])
@pytest.mark.parametrize('direkt,indirekt,import_,kontrakt',[
    ('intag/webb.py','intag/modeller.py','from riskanalys.kommandon import skriv_kommando','Webb använder tjänster, aldrig kommandopaketet'),
    ('analys/tjanst.py','analys/modeller.py','from riskanalys.intag import analysformular','Analystjänsten är oberoende av formuläradaptern'),
    ('bedomning/motor.py','bedomning/modeller.py','import docx','Riskberäkningen är oberoende av konkret AI och Word'),
])
def test_forbjuden_import_underkanns_i_separat_kopia(tmp_path,kant,direkt,indirekt,import_,kontrakt):
    rot=Path(__file__).resolve().parents[2]
    shutil.copytree(rot/'src/riskanalys',tmp_path/'src/riskanalys',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy2(rot/'pyproject.toml',tmp_path/'pyproject.toml')
    fil=tmp_path/'src/riskanalys'/(direkt if kant=='direkt' else indirekt)
    with fil.open('a') as f:f.write('\n'+import_+'\n')
    env=dict(os.environ,PYTHONPATH=str(tmp_path/'src'))
    r=subprocess.run([str(Path(sys.executable).parent/'lint-imports'),'--no-cache','--no-logo'],cwd=tmp_path,env=env,text=True,capture_output=True)
    assert r.returncode!=0
    assert kontrakt+' BROKEN' in r.stdout,r.stdout+r.stderr


def test_kartinventering_foljer_ostagade_borttagningar(tmp_path,monkeypatch):
    from docs.research.verktyg import bygg_obsidiankarta as karta
    subprocess.run(['git','init','-q',str(tmp_path)],check=True)
    gammal=tmp_path/'borttagen.py';gammal.write_text('"""Syntetisk gammal fil."""\n')
    subprocess.run(['git','-C',str(tmp_path),'add','borttagen.py'],check=True)
    gammal.unlink()
    (tmp_path/'ny.py').write_text('"""Syntetisk mottagare."""\n')
    monkeypatch.setattr(karta,'ROOT',tmp_path)
    assert karta.inventory()==['ny.py']
