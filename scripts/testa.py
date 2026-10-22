"""Explicita pytestprofiler med collection, JUnit och oförändrat källsnapshot."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROT=Path(__file__).resolve().parents[1]
PROFILERFIL=ROT/'tester/testprofiler.json'


def snapshot():
    # Även fixture-/källresurser är indata. Endast genererad bytekod undantas.
    rotmappar=('src','tester','regelbas','scripts','docs/research/verktyg')
    filer={p for rot in rotmappar for p in (ROT/rot).rglob('*')
        if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.pyo')}
    filer.update(p for p in (ROT/'AGENTS.md',ROT/'pyproject.toml',PROFILERFIL) if p.is_file())
    return {str(p.relative_to(ROT)):sha256(p.read_bytes()).hexdigest() for p in sorted(filer)}


def kanoniskt_nodeid(node):
    fil, _, test = node.partition('::')
    namn, klammer, parameter = test.partition('[')
    return fil.removesuffix('.py').replace('/', '.') + '.' + namn.replace('::', '.') + klammer + parameter


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('profil',choices=('snabb','analys','full'));p.add_argument('--ut',required=True,type=Path)
    a=p.parse_args(argv)
    if sys.version_info[:2]!=(3,12):p.error('Kör med projektets Python 3.12: .venv312/bin/python scripts/testa.py …')
    ut=a.ut.resolve()
    if ut.exists():p.error('Välj en ny utdatamapp; tidigare provbevis skrivs inte över.')
    profiler=json.loads(PROFILERFIL.read_text())
    urval=[] if a.profil=='full' else profiler[a.profil]
    if a.profil!='full' and (not urval or any(not isinstance(x,str) or not x.startswith('tester/') or '..' in Path(x.split('::')[0]).parts or not (ROT/x.split('::')[0]).is_file() for x in urval)):
        p.error('Testprofilen saknar giltiga befintliga prov. Rätta tester/testprofiler.json.')
    mark='not live' if a.profil=='full' else 'not live and not fullkedja'
    cmd=[sys.executable,'-m','pytest',*urval,'-m',mark]
    ut.mkdir(parents=True);start=time.monotonic();fore=snapshot()
    (ut/'snapshot.json').write_text(json.dumps(fore,sort_keys=True))
    samling=subprocess.run([*cmd,'--collect-only','-q'],cwd=ROT,text=True,capture_output=True)
    (ut/'collection.log').write_text(samling.stdout)
    nodes=[s.strip() for s in samling.stdout.splitlines() if s.strip().startswith('tester/') and '::' in s]
    if samling.returncode or not nodes:
        resultat={'profil':a.profil,'verifierad':False,'exitkod':samling.returncode or 5,'antal':0,'orsak':'Urvalet kunde inte samlas in.'}
    else:
        kommando=[*cmd,'-q','--tb=short','--durations=30',f'--junitxml={ut}/junit.xml']
        with (ut/'pytest.log').open('w') as log:
            korning=subprocess.run(kommando,cwd=ROT,stdout=log,stderr=subprocess.STDOUT,text=True)
        xml=ut/'junit.xml';fall=ET.parse(xml).getroot().findall('.//testcase') if xml.is_file() else []
        faktiska={x.get('classname','')+'.'+x.get('name','') for x in fall}
        lika=len(nodes)==len(fall) and {kanoniskt_nodeid(n) for n in nodes}==faktiska
        oforandrat=fore==snapshot()
        git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROT,text=True,capture_output=True)
        resultat=dict(profil=a.profil,kommando=kommando,python=platform.python_version(),commit=git.stdout.strip() if git.returncode==0 else None,
            antal=len(fall),insamlade=len(nodes),collection_matchar=lika,oforandrat=oforandrat,
            fel=sum(x.find('failure') is not None or x.find('error') is not None for x in fall),skippade=sum(x.find('skipped') is not None for x in fall),
            exitkod=korning.returncode,verifierad=korning.returncode==0 and lika and oforandrat)
    resultat['sekunder']=time.monotonic()-start
    (ut/'resultat.json').write_text(json.dumps(resultat,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(resultat,ensure_ascii=False))
    return resultat['exitkod'] or (0 if resultat['verifierad'] else 1)


if __name__=='__main__':raise SystemExit(main())
