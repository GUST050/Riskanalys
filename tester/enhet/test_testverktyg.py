"""Körprofilen får aldrig göra ett tomt/felaktigt urval grönt."""
import json
from pathlib import Path
from types import SimpleNamespace
import pytest


def test_tidsrapport_summerar_utan_att_blanda_vaggtid(tmp_path):
    from scripts.testtid import sammanstall
    fil=tmp_path/'junit.xml'
    fil.write_text('<testsuites><testsuite time="9"><testcase classname="a" name="x" time="0.5"/><testcase classname="b" name="y" time="1.25"/></testsuite></testsuites>')
    r=sammanstall(fil)
    assert r['antal']==2 and r['provtid_s']==1.75
    assert r['per_fil']=={'a':0.5,'b':1.25}
    assert r['fel']==0 and r['skippade']==0 and r['kalla_sha256']


def test_fel_och_bortval_redovisas(tmp_path):
    from scripts.testtid import sammanstall
    fil=tmp_path/'junit.xml'
    fil.write_text('<testsuites><testsuite><testcase classname="a" name="x" time="1"><failure/></testcase><testcase classname="a" name="y" time="0"><skipped/></testcase></testsuite></testsuites>')
    r=sammanstall(fil)
    assert r['fel']==1 and r['skippade']==1 and r['godkanda']==0


def fake_korning(monkeypatch,tmp_path,*,exitkod=0,tomt=False,andra=False):
    from scripts import testa
    (tmp_path/'src').mkdir();(tmp_path/'src/a.py').write_text('oforandrat')
    (tmp_path/'tester').mkdir();(tmp_path/'tester/test_litet.py').write_text('def test_exempel(): pass\n')
    profiler=tmp_path/'profiler.json';profiler.write_text(json.dumps({'snabb':['tester/test_litet.py'],'analys':['tester/test_litet.py']}))
    monkeypatch.setattr(testa,'ROT',tmp_path);monkeypatch.setattr(testa,'PROFILERFIL',profiler)
    anrop=[]
    def run(cmd,**kwargs):
        anrop.append(cmd)
        if cmd[:2]==['git','rev-parse']:return SimpleNamespace(returncode=0,stdout='syntetisksha\n')
        if '--collect-only' in cmd:return SimpleNamespace(returncode=5 if tomt else 0,stdout='' if tomt else 'tester/test_litet.py::test_exempel\n\n1 test collected\n')
        xml=Path(next(a.split('=',1)[1] for a in cmd if a.startswith('--junitxml=')))
        xml.write_text('<testsuites><testsuite><testcase classname="tester.test_litet" name="test_exempel" time="0.1"/></testsuite></testsuites>')
        kwargs['stdout'].write('syntetiskt provutfall\n')
        if andra:(tmp_path/'src/a.py').write_text('andrat')
        return SimpleNamespace(returncode=exitkod)
    monkeypatch.setattr(testa.subprocess,'run',run)
    return testa,anrop


def test_fullprofil_kor_hela_pytest(monkeypatch,tmp_path):
    testa,anrop=fake_korning(monkeypatch,tmp_path)
    assert testa.main(['full','--ut',str(tmp_path/'ut')])==0
    cmd=next(c for c in anrop if '--collect-only' not in c and '-m' in c)
    assert 'not live' in cmd and 'not live and not fullkedja' not in cmd
    assert 'tester/test_litet.py' not in cmd
    resultat=json.loads((tmp_path/'ut/resultat.json').read_text())
    assert resultat['verifierad'] and resultat['antal']==1 and resultat['commit']=='syntetisksha'


@pytest.mark.parametrize('exitkod,tomt,forvantat',[(0,True,5),(1,False,1),(5,False,5)])
def test_tomt_eller_okant_urval_ar_inte_gront(monkeypatch,tmp_path,exitkod,tomt,forvantat):
    testa,_=fake_korning(monkeypatch,tmp_path,exitkod=exitkod,tomt=tomt)
    assert testa.main(['snabb','--ut',str(tmp_path/'ut')])==forvantat


def test_andrad_kod_kan_inte_verifieras(monkeypatch,tmp_path):
    testa,_=fake_korning(monkeypatch,tmp_path,andra=True)
    assert testa.main(['snabb','--ut',str(tmp_path/'ut')])==1
    assert not json.loads((tmp_path/'ut/resultat.json').read_text())['verifierad']


def test_okand_profil_avvisas(tmp_path):
    from scripts.testa import main
    with pytest.raises(SystemExit) as e:main(['okand','--ut',str(tmp_path/'ut')])
    assert e.value.code==2


@pytest.mark.parametrize('node,forvantat',[
    ('tester/enhet/test_filer.py::test_vag[a/../../prov.py::inuti]',
     'tester.enhet.test_filer.test_vag[a/../../prov.py::inuti]'),
    ('tester/enhet/test_filer.py::Grupp::test_vag[/tmp/prov.py]',
     'tester.enhet.test_filer.Grupp.test_vag[/tmp/prov.py]'),
])
def test_nodeid_bevarar_hela_parametern(node,forvantat):
    from scripts.testa import kanoniskt_nodeid
    assert kanoniskt_nodeid(node)==forvantat


@pytest.mark.parametrize('resurs', [
    'tester/fixturer/prov.json',
    'tester/fixturer/regelbas_v0/kataloger/tjanster.yaml',
    'regelbas/lydelsetexter/prov.txt',
])
@pytest.mark.parametrize('andring', ['tillagg', 'andring', 'borttagning'])
def test_andrade_test_och_regelresurser_kan_inte_verifieras(monkeypatch,tmp_path,resurs,andring):
    testa,_=fake_korning(monkeypatch,tmp_path)
    fil=tmp_path/resurs;fil.parent.mkdir(parents=True,exist_ok=True)
    if andring!='tillagg':fil.write_text('ursprungligt syntetiskt underlag')
    tidigare=testa.subprocess.run
    def run(cmd,**kwargs):
        resultat=tidigare(cmd,**kwargs)
        if any(x.startswith('--junitxml=') for x in cmd):
            if andring=='borttagning':fil.unlink()
            else:fil.write_text('nytt syntetiskt underlag')
        return resultat
    monkeypatch.setattr(testa.subprocess,'run',run)
    assert testa.main(['snabb','--ut',str(tmp_path/'ut')])==1
    r=json.loads((tmp_path/'ut/resultat.json').read_text())
    assert not r['oforandrat'] and not r['verifierad']


def test_snapshot_ignorerar_genererad_bytekod(monkeypatch,tmp_path):
    from scripts import testa
    monkeypatch.setattr(testa,'ROT',tmp_path)
    monkeypatch.setattr(testa,'PROFILERFIL',tmp_path/'profiler.json')
    for namn in ('src/a.py','tester/f.json','regelbas/f.txt','scripts/v.py','docs/research/verktyg/v.py'):
        p=tmp_path/namn;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('syntetiskt')
    fore=testa.snapshot()
    for namn in ('src/__pycache__/a.cpython-312.pyc','tester/__pycache__/b.pyc','scripts/a.pyc'):
        p=tmp_path/namn;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'genererat')
    assert fore==testa.snapshot()


def test_omradesprofil_kor_explicit_urval_och_redovisar_orsak(monkeypatch, tmp_path):
    testa, anrop = fake_korning(monkeypatch, tmp_path)
    profiler = json.loads(testa.PROFILERFIL.read_text())
    profiler['profil'] = ['tester/test_litet.py']
    testa.PROFILERFIL.write_text(json.dumps(profiler))
    assert testa.main(['profil', '--ut', str(tmp_path/'ut')]) == 0
    assert any('tester/test_litet.py' in cmd for cmd in anrop)
    r = json.loads((tmp_path/'ut/resultat.json').read_text())
    assert r['urval'] == ['tester/test_litet.py']
    assert 'profil' in r['urvalsorsak']
    assert r['miljo']['paket']['pytest']


@pytest.mark.parametrize('resurs', ['uv.lock', '.python-version', '.github/workflows/verifiera.yml'])
def test_andrad_miljodefinition_under_korning_underkanns(monkeypatch, tmp_path, resurs):
    testa, _ = fake_korning(monkeypatch, tmp_path)
    fil = tmp_path/resurs
    fil.parent.mkdir(parents=True, exist_ok=True)
    fil.write_text('ursprunglig')
    orig = testa.subprocess.run
    def run(cmd, **kwargs):
        r = orig(cmd, **kwargs)
        if any(x.startswith('--junitxml=') for x in cmd):
            fil.write_text('andrad')
        return r
    monkeypatch.setattr(testa.subprocess, 'run', run)
    assert testa.main(['snabb', '--ut', str(tmp_path/'ut')]) == 1
    assert not json.loads((tmp_path/'ut/resultat.json').read_text())['oforandrat']


def test_junit_maste_matcha_insamlingens_multiplicitet(monkeypatch, tmp_path):
    testa, _ = fake_korning(monkeypatch, tmp_path)
    orig = testa.subprocess.run
    def run(cmd, **kwargs):
        r = orig(cmd, **kwargs)
        if '--collect-only' in cmd:
            r.stdout = ('tester/test_litet.py::test_a\n' * 2 + 'tester/test_litet.py::test_b\n')
        if any(x.startswith('--junitxml=') for x in cmd):
            xml = Path(next(x.split('=', 1)[1] for x in cmd if x.startswith('--junitxml=')))
            xml.write_text('<testsuites><testsuite>' + ''.join(
                f'<testcase classname="tester.test_litet" name="test_{n}"/>' for n in ('a','b','b')) + '</testsuite></testsuites>')
        return r
    monkeypatch.setattr(testa.subprocess, 'run', run)
    assert testa.main(['snabb', '--ut', str(tmp_path/'ut')]) == 1
    assert not json.loads((tmp_path/'ut/resultat.json').read_text())['collection_matchar']
