"""Isolerade fel med riktig CLI-huvudfunktion och en kontrollerad positiv bas."""
import json
from pathlib import Path
import subprocess
import sys
import pytest
import yaml
from tester.fixturer.analys_hela_kedjan import bygg_bunden_kedja,syntetisk_expertkopia,DAG
from tester.fixturer.kedjecache import klona_kedja
from tester.fixturer.cli_process import kor_direkt
from riskanalys.profil.lagring import las_profil,spara_profil


@pytest.fixture(scope='module')
def bas(tmp_path_factory):
    rot=tmp_path_factory.mktemp('m2-grindbas').resolve();rr,rb=syntetisk_expertkopia(rot/'expert')
    return bygg_bunden_kedja(rb,rot/'fall',regelrot=rr,godkann=True)


def faststall_args(k,dag=DAG):
    return ('faststall',k.fall.byramapp.name,'--organ','styrelsen','--namn','Syntetisk',
            '--datum',str(dag),'--regelbas',str(k.regelrot))


def miljo(k):
    return {'RISKANALYS_DATA':str(k.fall.byramapp.parent)}


def injicera(k,fel):
    from datetime import date
    if fel=='belagg':
        p=las_profil(k.fall.byramapp);u=p.uppgifter['P-ORG.namn'].model_copy(update={'kalla':None})
        spara_profil(k.fall.byramapp,p.model_copy(update={'uppgifter':{**p.uppgifter,'P-ORG.namn':u}}))
    elif fel=='expert':(k.regelrot/'granskning.yaml').unlink()
    elif fel=='metod':
        f=k.regelrot/'granskning.yaml';d=yaml.safe_load(f.read_text());d['beslut']['RP-RED-VG']['objekt']['KUNDMETOD-C']['beslut']='ändras';f.write_text(yaml.safe_dump(d,allow_unicode=True))
    elif fel=='aldre':
        from riskanalys.lagring.manifest import las_manifest,skriv_manifest
        f=k.bedomningsmapp/'bedomning.json';d=json.loads(f.read_text());d.pop('omfattning');f.write_text(json.dumps(d,ensure_ascii=False))
        skriv_manifest(k.bedomningsmapp,las_manifest(k.bedomningsmapp).metadata)
    return date(2026,11,20) if fel=='datum' else DAG


def orsaksbrister(k,fel,dag=DAG,*,ursprung=None):
    if fel=='belagg':
        from riskanalys.profil.hantering import belaggsbrister
        return tuple(s for s in belaggsbrister(las_profil(k.fall.byramapp)) if 'P-ORG.namn' in s)
    if fel in ('expert','metod'):
        from riskanalys.regelverk.laddning import ladda_regelbas
        from riskanalys.regelverk.validering_m2 import attesthinder
        return tuple(s for s in attesthinder(ladda_regelbas(k.regelrot),'RP-RED-VG') if 'KUNDMETOD-C' in s)
    from riskanalys.faststallelse.faststall import _underlag
    from riskanalys.faststallelse.grindar import _m2,hinder_for_faststallelse
    if fel=='aldre' and ursprung is not None:
        from dataclasses import replace
        from riskanalys.bedomning.korning import las_bedomning
        return tuple(s for s in _m2(replace(ursprung,bedomning=las_bedomning(k.bedomningsmapp)),dag) if 'Äldre bedömning' in s)
    u=_underlag(k.fall.byramapp,k.fall.regelbas,k.granskningsmapp)
    if fel=='aldre':return tuple(s for s in _m2(u,dag) if 'Äldre bedömning' in s)
    return tuple(hinder_for_faststallelse(u,dag))


@pytest.mark.fullkedja
def test_positiv_bas_kan_faststallas_via_cli_i_process(bas,tmp_path):
    k=klona_kedja(bas,tmp_path)
    r=kor_direkt(miljo(k),*faststall_args(k))
    assert 'fastställd' in r.stdout and (k.fall.byramapp/'faststallda/v1').is_dir()


@pytest.mark.parametrize('fel,ord',[('belagg','profil'),('expert','regelbasen har ändrats'),('metod','regelbasen har ändrats'),('datum','datum'),('aldre','analysens underlag har ändrats')])
def test_negativ_cli_stoppar_just_andrat_underlag(bas,tmp_path,fel,ord):
    k=klona_kedja(bas,tmp_path)
    assert not orsaksbrister(k,fel), 'Den negativa orsaken fanns redan före injiceringen.'
    from riskanalys.faststallelse.faststall import _underlag
    ursprung=_underlag(k.fall.byramapp,k.fall.regelbas,k.granskningsmapp) if fel=='aldre' else None
    dag=injicera(k,fel)
    assert orsaksbrister(k,fel,dag,ursprung=ursprung), 'Provets specifika felorsak nådde inte domängrinden.'
    args=faststall_args(k,dag)
    r=kor_direkt(miljo(k),*args,expected=1)
    assert ord in r.stderr.lower(),r.stderr
    assert not (k.fall.byramapp/'faststallda/v1').exists()


@pytest.mark.fullkedja
@pytest.mark.parametrize('fel,ord',[('fraga','fråga'),('felpaket','regelpaket')])
def test_fel_fore_bedomning_skrivning_bygger_ratt_startlage(tmp_path,monkeypatch,fel,ord):
    from tester.m2 import test_m2_kedja as gammal
    monkeypatch.setattr(gammal,'kor',kor_direkt)
    r=gammal.kedja(tmp_path,'RP-RED-VG','Västra Götaland',fel)
    assert ord in r.stderr.lower(),r.stderr


@pytest.mark.fullkedja
def test_negativ_faststallelse_fungerar_i_riktig_subprocess(bas,tmp_path,monkeypatch):
    k=klona_kedja(bas,tmp_path);injicera(k,'belagg')
    monkeypatch.setenv('RISKANALYS_DATA',str(k.fall.byramapp.parent))
    r=subprocess.run([str(Path(sys.executable).parent/'riskanalys'),*faststall_args(k)],capture_output=True,text=True)
    assert r.returncode==1 and 'profil' in r.stderr.lower() and 'Traceback' not in r.stderr
    assert not (k.fall.byramapp/'faststallda/v1').exists()
