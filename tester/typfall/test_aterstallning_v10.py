"""Fristående V10 och hela arbetsmappen återställs i nya syntetiska datamappar."""
from hashlib import sha256
from pathlib import Path
import shutil
import time
import pytest
from tester.fixturer.resultatkedja import resultatkedja_bas,DAG
from tester.fixturer.kedjecache import klona_kedja


def _innehall(rot):
    return {str(p.relative_to(rot)):sha256(p.read_bytes()).hexdigest() for p in rot.rglob('*') if p.is_file()}


@pytest.fixture(scope='module')
def aterstallningsbas(resultatkedja_bas,tmp_path_factory):
    from riskanalys.granskning.korning import kor_granskning,las_granskning
    from riskanalys.dokument.rapportpaket_v10 import las_presentation_v10
    from riskanalys.faststallelse.resultatgranskning import registrera_resultatgranskning
    from riskanalys.faststallelse.sakgranskning import registrera_sakgranskning,spara_sakgranskningar,struktur_summa
    from riskanalys.faststallelse.faststall import faststall
    from riskanalys.faststallelse.modeller import Beslut
    from riskanalys.analys.provning import registersumma
    k=klona_kedja(resultatkedja_bas,tmp_path_factory.mktemp('aterstallningsbas'))
    f=k.fall
    gm=kor_granskning(f.byramapp,f.regelbas,DAG,rapportformat='v10')
    d,fynd=las_granskning(gm)
    assert not fynd
    p=las_presentation_v10(gm,f.bedomning,f.profil,regelbas=f.regelbas)
    poster=registrera_resultatgranskning((),d,f.profil,presentation=p,
        visad_struktursumma=struktur_summa(d,presentation=p),analysbindning=registersumma(f.analys),
        godkand=True,roll='FfR',namn='Syntetisk återställningsprövare',datum=DAG)
    for a in d.avsnitt:
        if a.leveransdel!='resultatrapport':
            poster=registrera_sakgranskning(poster,d,f.profil,a.id,True,'FfR','Syntetisk',DAG,
                analysbindning=registersumma(f.analys),presentation=p)
    spara_sakgranskningar(f.byramapp,poster)
    final=faststall(f.byramapp,k.regelrot,f.regelbas,Beslut(organ='Syntetisk',namn='Syntetisk',roll='FfR',datum=DAG))
    assert len(list(final.glob('*.docx')))==3
    return k,final


def test_last_v10_aterstalls_utan_ursprungsmapp_eller_nytt_ai(aterstallningsbas,tmp_path,monkeypatch,record_testsuite_property):
    from riskanalys.faststallelse.faststall import verifiera_version
    from riskanalys.dokument import skrivning,rendering_v10
    from riskanalys.regelverk import laddning
    _,final=aterstallningsbas
    kalla=tmp_path/'ursprung/v1';shutil.copytree(final,kalla)
    backup=tmp_path/'backup/v1';shutil.copytree(kalla,backup)
    kalla.parent.rename(tmp_path/'ursprung-otillgangligt')
    ny=tmp_path/'ny-datamapp/byra'
    start=time.monotonic();shutil.copytree(backup,ny/'faststallda/v1')
    def forbjudet(*a,**kw):pytest.fail('Återställning läste aktuell modell eller körde AI/rendering')
    monkeypatch.setattr(skrivning,'kor_skrivning',forbjudet)
    monkeypatch.setattr(rendering_v10,'rendera_rapportvyer_v10',forbjudet)
    monkeypatch.setattr(laddning,'ladda_regelbas',forbjudet)
    assert verifiera_version(ny,1)==[]
    assert _innehall(backup)==_innehall(ny/'faststallda/v1')
    record_testsuite_property('aterstallning_s',time.monotonic()-start)


@pytest.mark.parametrize('skada',['saknas','andrad'])
def test_aterstalld_kopia_avvisar_skadad_rapportdel(aterstallningsbas,tmp_path,skada):
    from riskanalys.faststallelse.faststall import verifiera_version
    _,final=aterstallningsbas
    ny=tmp_path/'ny';rest=ny/'faststallda/v1';shutil.copytree(final,rest)
    fil=next(rest.glob('*analysbilaga*.docx'))
    if skada=='saknas':fil.unlink()
    else:fil.write_bytes(b'syntetiskt skadad rapport')
    fel=verifiera_version(ny,1)
    assert fel and any(fil.name in f for f in fel)
    from riskanalys.faststallelse.faststall import skadade_versioner
    assert any('säkerhetskop' in f.lower() for f in skadade_versioner(ny))


def test_hela_arbetsmappen_aterstalls_med_historia_och_attester(aterstallningsbas,tmp_path,record_testsuite_property):
    from riskanalys.analys.lagring import analyslas,las_analys
    from riskanalys.profil.lagring import las_profil
    from riskanalys.faststallelse.sakgranskning import las_sakgranskningar
    from riskanalys.faststallelse.faststall import verifiera_version
    k,_=aterstallningsbas
    source=tmp_path/'ursprung';shutil.copytree(k.fall.byramapp,source)
    from riskanalys.profil.lagring import spara_profil
    spara_profil(source,las_profil(source))  # Sparar tidigare profilbytes i historiken.
    backup=tmp_path/'backup'
    # Profil-, analys- och driftlåsen hålls; övriga skrivare är stoppade under kopieringen.
    with analyslas(source):shutil.copytree(source,backup)
    fore=_innehall(backup)
    profil,analys,attester=las_profil(source),las_analys(source),las_sakgranskningar(source)
    source.rename(tmp_path/'ursprung-otillgangligt')
    ny=tmp_path/'aterstalld';start=time.monotonic();shutil.copytree(backup,ny)
    assert fore==_innehall(ny)
    assert las_profil(ny)==profil and las_analys(ny)==analys and las_sakgranskningar(ny)==attester
    assert list((ny/'profil/historik').glob('*.yaml'))
    assert verifiera_version(ny,1)==[]
    record_testsuite_property('arbetsmapp_aterstallning_s',time.monotonic()-start)
