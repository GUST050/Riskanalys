import os
import pytest
from tester.fixturer.m2 import DAG
from riskanalys.fel import RiskanalysFel
from riskanalys.profil.lagring import spara_profil, las_profil, PROFILFIL
from riskanalys.intag.tjanst import Intagstjanst, profilrevision
from riskanalys.intag.modeller import IntagSvar


def test_aterupptagning_konflikt_och_historik(tmp_path, monkeypatch, rb_intag):
    monkeypatch.setenv('RISKANALYS_DATA',str(tmp_path))
    t=Intagstjanst('syntetisk',rb_intag)
    t.skapa('Skåne',False,DAG,'Syntetiskt underlag','Uppgiftslamnare')
    p=t.profil();assert p.byra.regelpaket == 'RP-RED-SKANE'
    rev=profilrevision(p)
    t.spara(IntagSvar(falt='P-ORG.namn',text='Syntetisk byrå',kalla='Test',datum=DAG),rev)
    with pytest.raises(RiskanalysFel,match='annan flik|ändrats'):
        t.spara(IntagSvar(falt='P-ORG.namn',text='Överskrivning',kalla='Test',datum=DAG),rev)
    assert Intagstjanst('syntetisk',rb_intag).profil().uppgifter['P-ORG.namn'].varde == 'Syntetisk byrå'
    assert list((t.mapp/'profil/historik').glob('*.yaml'))
    assert os.stat(t.mapp/PROFILFIL).st_mode & 0o777 == 0o600


def test_avbruten_atomic_skrivning_bevarar_original(tmp_path, monkeypatch, tom):
    spara_profil(tmp_path,tom);gammal=(tmp_path/PROFILFIL).read_bytes()
    def avbrott(*args):raise OSError('Syntetiskt diskfel')
    monkeypatch.setattr('riskanalys.profil.lagring.os.replace',avbrott)
    with pytest.raises(RiskanalysFel):spara_profil(tmp_path,tom)
    assert (tmp_path/PROFILFIL).read_bytes() == gammal
    assert not list((tmp_path/'profil').glob('*.tmp'))


def test_filial_auto_valjer_stockholm(tmp_path, monkeypatch, rb_intag):
    monkeypatch.setenv('RISKANALYS_DATA',str(tmp_path))
    t=Intagstjanst('syntetisk',rb_intag)
    t.skapa('Skåne',True,DAG,'Test','Uppgiftslamnare')
    assert t.profil().byra.regelpaket == 'RP-RED-STHLM'


def test_cli_och_intag_delar_en_lasbar_historikoperation(tmp_path,monkeypatch,rb_intag):
    from concurrent.futures import ThreadPoolExecutor
    from argparse import Namespace
    from riskanalys.kommandon.drift_kommando import kor_utvardera
    from riskanalys.intag.utvardering import registrera_utvardering
    from riskanalys.drift.historik import las_historik
    monkeypatch.setenv('RISKANALYS_DATA',str(tmp_path))
    t=Intagstjanst('syntetisk',rb_intag);t.skapa('Skåne',False,DAG,'Test','Test')
    revision=profilrevision(t.profil())
    def registrera(i):
        if i % 2:
            kor_utvardera(Namespace(byra='syntetisk',datum=DAG,beskrivning=f'CLI-{i}'))
        else:
            registrera_utvardering(t,DAG,f'Webb-{i}',revision)
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(registrera,range(24)))
    h=las_historik(t.mapp)
    assert len(h.handelser)==24
    assert {x.beskrivning for x in h.handelser}=={f'{"CLI" if i%2 else "Webb"}-{i}' for i in range(24)}
    assert os.stat(t.mapp/'drift/historik.yaml').st_mode & 0o777 == 0o600
