import json
import pytest
from riskanalys.fel import RiskanalysFel
from riskanalys.foretagsdata.scb import tolka_scb
from riskanalys.foretagsdata.lagring import spara_bild, las_bild
from riskanalys.intag.register import bekrafta_register
from riskanalys.intag.tjanst import Intagstjanst, profilrevision
from riskanalys.intag.modeller import IntagSvar
from tester.foretagsdata.test_scb import ORG, post
from tester.fixturer.m2 import DAG

@pytest.fixture
def t(tmp_path,monkeypatch,rb_intag):
    monkeypatch.setenv('RISKANALYS_DATA',str(tmp_path))
    return Intagstjanst('syntetisk',rb_intag)


def test_snapshot_privata_filer_ingen_profilmutation_och_aterupptagning(t):
    b=tolka_scb(post(),ORG,'scb_api');spara_bild(t.mapp,b)
    assert not t.finns() and las_bild(t.mapp)==b
    for p in (t.mapp/'register').glob('*.json'):assert p.stat().st_mode&0o777==0o600
    t.skapa('Skåne',False,DAG,'Test','Test');fore=t.profil()
    spara_bild(t.mapp,b)
    assert t.profil()==fore


def test_bekraftelse_kraver_exakt_bild_profilrevision_och_ordinarie_falt(t):
    t.skapa('Skåne',False,DAG,'Test','Test');b=tolka_scb(post(),ORG,'scb_api');spara_bild(t.mapp,b)
    rev=profilrevision(t.profil())
    for summa,falt,r in [('a'*64,'P-ORG.namn',rev),(b.summa,'P-ORG.namn','gammal'),(b.summa,'P-ORG.antal_anstallda',rev)]:
        with pytest.raises(RiskanalysFel):bekrafta_register(t,summa,falt,'Test',DAG,r)
    p=bekrafta_register(t,b.summa,'P-ORG.namn','Test',DAG,rev)
    assert p.ar_bekraftad('P-ORG.namn') and b.summa in p.uppgifter['P-ORG.namn'].kalla
    assert not p.ar_bekraftad('P-ORG.antal_anstallda')
    with pytest.raises(RiskanalysFel):bekrafta_register(t,b.summa,'P-ORG.namn','Test',DAG,rev)


def test_andrat_lan_anvander_befintlig_invalidering(t):
    t.skapa('Skåne',False,DAG,'Test','Test')
    t.spara(IntagSvar(falt='P-ORG.namn',text='Eget svar',kalla='Test',roll='Test',datum=DAG),profilrevision(t.profil()))
    t.spara(IntagSvar(falt='P-ORG.antal_anstallda',text='3',kalla='Test',roll='Test',datum=DAG),profilrevision(t.profil()))
    b=tolka_scb(post(),ORG,'scb_api');spara_bild(t.mapp,b)
    p=bekrafta_register(t,b.summa,'P-ORG.sateslan','Test',DAG,profilrevision(t.profil()))
    assert p.byra.regelpaket=='RP-RED-VG'
    assert p.ar_bekraftad('P-ORG.namn')
    assert not p.ar_bekraftad('P-ORG.antal_anstallda')


def test_gammal_snapshot_avvisas_och_tidigare_svar_bevaras(t):
    t.skapa('Skåne',False,DAG,'Test','Test');b=tolka_scb(post(),ORG,'scb_api');spara_bild(t.mapp,b)
    c=tolka_scb(post(),ORG,'scb_api');spara_bild(t.mapp,c)
    fore=t.profil()
    with pytest.raises(RiskanalysFel,match='Registerunderlaget har ändrats'):bekrafta_register(t,b.summa,'P-ORG.namn','Test',DAG,profilrevision(fore))
    assert t.profil()==fore
    assert (t.mapp/'register'/f'{b.summa}.json').is_file()


def test_byte_av_byrans_orgnr_stoppar_efter_start(t):
    b=tolka_scb(post(),ORG,'scb_api');spara_bild(t.mapp,b)
    t.skapa('Skåne',False,DAG,'Test','Test')
    d=post();d.update(orgNr='5599991246',peOrgNr='165599991246')
    c=tolka_scb(d,'5599991246','scb_api')
    with pytest.raises(RiskanalysFel,match='annan juridisk'):spara_bild(t.mapp,c)
    assert las_bild(t.mapp)==b


def test_skadad_snapshot_stoppar(t):
    b=tolka_scb(post(),ORG,'scb_api');spara_bild(t.mapp,b)
    p=t.mapp/'register'/f'{b.summa}.json'
    d=json.loads(p.read_text());d['namn']='Ändrat';p.write_text(json.dumps(d))
    with pytest.raises(RiskanalysFel,match='kontrollsumm'):las_bild(t.mapp)


def test_ej_frivillig_bekraftelse_och_framtida_datum(t):
    t.skapa('Skåne',False,DAG,'Test','Test');b=tolka_scb(post(),ORG,'scb_api');spara_bild(t.mapp,b)
    from datetime import timedelta
    for roll,dag in [('',DAG),('Test',DAG+timedelta(days=1))]:
        with pytest.raises(RiskanalysFel):bekrafta_register(t,b.summa,'P-ORG.namn',roll,dag,profilrevision(t.profil()))


def test_aktuell_registerbild_kan_inte_styrka_historisk_bedomning(t):
    from datetime import timedelta
    t.skapa('Skåne',False,DAG,'Test','Test')
    from riskanalys.profil.lagring import spara_profil
    p=t.profil();spara_profil(t.mapp,p.model_copy(update={'byra':p.byra.model_copy(update={'datum':DAG-timedelta(days=1)})}))
    b=tolka_scb(post(),ORG,'scb_api')
    with pytest.raises(RiskanalysFel,match='historisk'):spara_bild(t.mapp,b)
    assert las_bild(t.mapp) is None


def test_aven_byramappen_ar_privat_fore_profil(t):
    spara_bild(t.mapp,tolka_scb(post(),ORG,'scb_api'))
    assert t.mapp.stat().st_mode&0o777==0o700
    assert t.mapp.parent.stat().st_mode&0o077==0


def test_hamtningens_svenska_dag_vid_midnatt(t):
    from datetime import datetime,timezone,timedelta
    from riskanalys.profil.lagring import spara_profil
    t.skapa('Skåne',False,DAG,'Test','Test');p=t.profil()
    spara_profil(t.mapp,p.model_copy(update={'byra':p.byra.model_copy(update={'datum':DAG-timedelta(days=1)})}))
    b=tolka_scb(post(),ORG,'scb_api').model_copy(update={'hamtad':datetime(2026,10,9,22,30,tzinfo=timezone.utc)})
    with pytest.raises(RiskanalysFel,match='historisk'):spara_bild(t.mapp,b)
    assert las_bild(t.mapp) is None
