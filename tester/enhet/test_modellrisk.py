"""AB7:s underlag är syntetiska; grön teknik är aldrig sakkunnigattest."""
import importlib
import importlib.util
import json
import shutil
from datetime import date
from pathlib import Path

import pytest

from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.kontrollsumma import for_bytes, for_fil
from riskanalys.regelverk.modeller import Sakkunnig

DAG = date(2026, 10, 15)

def test_modellriskmodulen_exponerar_grind():
    assert importlib.util.find_spec('riskanalys.drift.modellrisk'), 'AB7 saknar modellriskmodul'

@pytest.fixture
def api():
    if not importlib.util.find_spec('riskanalys.drift.modellrisk'):
        pytest.skip('Beteendekontrakt väntar på AB7-modulen')
    return importlib.import_module('riskanalys.drift.modellrisk')

@pytest.fixture
def kopia(tmp_path, monkeypatch, api):
    identitet = importlib.import_module('riskanalys.drift.modellidentitet')
    rot = tmp_path / 'kod'
    shutil.copytree(Path(__file__).resolve().parents[2] / 'src', rot / 'src')
    monkeypatch.setattr(identitet, 'MODELLROT', rot / 'src/riskanalys')
    return rot


def projekt(api, regelbas, tmp_path, granskat=True):
    pdf = tmp_path / 'rapport.pdf'
    pdf.write_bytes(b'%PDF-1.4\nSyntetisk provrapport, inte expertgranskning.\n%%EOF')
    inventarium = api.modellfilmanifest(regelbas)
    rapport = api.Modellvalidering(
        modellbindning=inventarium.modellbindning,
        modellfiler_kontrollsumma=for_bytes(inventarium.model_dump_json(indent=2).encode()),
        rapport_kontrollsumma=for_fil(pdf), rapportversion='syntetisk-1', datum=DAG,
        tillampningsomrade='Endast syntetiska tester', fall_och_facit='Syntetiska typfall A och B',
        faktiska_utfall='Syntetiskt uppmätta utfall i provet', avvikelser='Inga i dessa syntetiska fall',
        begransningar='Ingen riktig användning prövad', verkliga_driftobservationer='Saknas; inte observerat i drift',
        m1_beslut='godkant' if granskat else 'ej_provat',
    )
    if granskat:
        rapport = rapport.model_copy(update={'sakkunnig': Sakkunnig(status='verifierad', av='Syntetisk sakkunnig', datum=DAG, kontrollsumma=api.valideringens_innehallssumma(rapport))})
    paket = api.exportera_modellvalidering(tmp_path / 'leverans', regelbas, rapport, pdf)
    return rapport, paket


def adoption(api, regelbas, tmp_path, granskat=True):
    rapport, paket = projekt(api, regelbas, tmp_path, granskat)
    byra = tmp_path / 'byra'
    belagg = byra / 'analys' / 'belagg'
    belagg.mkdir(parents=True)
    def kopiera(namn):
        shutil.copyfile(paket / namn, belagg / namn)
        return api.Modellbelagg(fil=namn, kontrollsumma=for_fil(belagg / namn))
    (belagg / 'rutin.txt').write_text('Syntetisk rutin för återkommande uppföljning')
    u = api.Modellriskunderlag(
        modellansvarig='Syntetisk ansvarig', modellbindning=rapport.modellbindning,
        rutin=api.Modellbelagg(fil='rutin.txt', kontrollsumma=for_fil(belagg / 'rutin.txt')),
        valideringsrapport=kopiera('modellvalidering.pdf'), projektrapport=kopiera('modellvalidering.json'),
        modellfiler=kopiera('modellfiler.json'), utvarderad=DAG, nasta_genomgang=date(2027,10,15),
        feluppfoljning='Månatlig kontroll av verkliga fel; inga observationer ännu', fel=(), godkand=True,
        beslutad_av='Syntetisk lokal beslutsfattare', beslutsdatum=DAG,
    )
    return byra, u, rapport


def test_modellrisk_saknat_underlag_ar_hinder(api, regelbas, tmp_path):
    assert api.modellriskhinder(tmp_path, regelbas, None, DAG)


def test_modellrisk_komplett_syntetiskt_beslut(api, regelbas, tmp_path):
    byra, u, _ = adoption(api, regelbas, tmp_path)
    assert api.modellriskhinder(byra, regelbas, u, DAG) == ()

@pytest.mark.parametrize('andring', [
    {'modellansvarig':' '}, {'feluppfoljning':''}, {'beslutad_av':''}, {'godkand':False},
    {'modellbindning':'sha256:'+'0'*64}, {'nasta_genomgang':DAG},
    {'nasta_genomgang':date(2027,10,16)}, {'utvarderad':date(2026,10,16)},
    {'beslutsdatum':date(2026,10,16)}, {'beslutsdatum':date(2026,10,14)},
])
def test_modellrisk_kraver_aktuell_rapport_och_feluppfoljning(api, regelbas, tmp_path, andring):
    byra, u, _ = adoption(api, regelbas, tmp_path)
    assert api.modellriskhinder(byra, regelbas, u.model_copy(update=andring), DAG)


def test_forfallen_och_arsgrans(api, regelbas, tmp_path):
    byra, u, _ = adoption(api, regelbas, tmp_path)
    assert not api.modellriskhinder(byra, regelbas, u, date(2027,10,15))
    assert api.modellriskhinder(byra, regelbas, u, date(2027,10,16))
    # 29 februari ger 28 februari nästa år, inte 365 dagar som generell regel.
    v = u.model_copy(update={'utvarderad':date(2024,2,29), 'beslutsdatum':DAG, 'nasta_genomgang':date(2025,3,1)})
    assert api.modellriskhinder(byra, regelbas, v, DAG)

@pytest.mark.parametrize('status,narrativ,belagt,block', [
    ('oppet','Utreds',False,True), ('atgardat','',False,True),
    ('atgardat','Rättat och omprövat',False,True), ('atgardat','Rättat och omprövat',True,False),
])
def test_vasentliga_fel_kraver_atgard_och_omprovning(api, regelbas, tmp_path, status, narrativ, belagt, block):
    byra,u,_=adoption(api,regelbas,tmp_path)
    fel=api.Modellfel(id='syntetiskt-fel',datum=DAG,beskrivning='Syntetiskt modellfel',allvar='vasentligt',status=status,atgard_och_omprovning=narrativ,belagg=(u.rutin,) if belagt else ())
    assert bool(api.modellriskhinder(byra,regelbas,u.model_copy(update={'fel':(fel,)}),DAG)) is block

@pytest.mark.parametrize('granskat', [False,True])
def test_projektrapport_och_lokalt_anvandningsbeslut_halls_isar(api, regelbas, tmp_path, granskat):
    byra,u,rapport=adoption(api,regelbas,tmp_path,granskat)
    assert bool(api.modellriskhinder(byra,regelbas,u,DAG)) is (not granskat)
    assert api.modellriskhinder(byra,regelbas,u.model_copy(update={'godkand':False}),DAG)
    assert rapport.sakkunnig.status == ('verifierad' if granskat else 'ej_granskad')

@pytest.mark.parametrize('fil', ['modellvalidering.pdf','modellvalidering.json','modellfiler.json','rutin.txt'])
def test_andrad_valideringsrapport_kraver_nytt_lokalt_beslut(api, regelbas, tmp_path, fil):
    byra,u,_=adoption(api,regelbas,tmp_path)
    fore=api.modellbindning(regelbas)
    with (byra/'analys'/'belagg'/fil).open('ab') as f: f.write(b'\nANDRAT')
    assert api.modellriskhinder(byra,regelbas,u,DAG)
    assert api.modellbindning(regelbas)==fore

@pytest.mark.parametrize('namn', ['../utanfor.txt','/tmp/utanfor.txt','a/../../utanfor.txt'])
def test_belagg_far_inte_lamna_registret(api, regelbas, tmp_path, namn):
    byra,u,_=adoption(api,regelbas,tmp_path)
    v=u.model_copy(update={'rutin':api.Modellbelagg(fil=namn,kontrollsumma=u.rutin.kontrollsumma)})
    assert api.modellriskhinder(byra,regelbas,v,DAG)


def test_belagg_symlank_och_saknad_fil(api, regelbas, tmp_path):
    byra,u,_=adoption(api,regelbas,tmp_path)
    rutin=byra/'analys'/'belagg'/'rutin.txt'
    rutin.unlink()
    assert api.modellriskhinder(byra,regelbas,u,DAG)
    annan=tmp_path/'annan'; annan.write_text('Hemlig utanför')
    rutin.symlink_to(annan)
    assert api.modellriskhinder(byra,regelbas,u,DAG)

@pytest.mark.parametrize('fil', ['bedomning/motor.py','profil/omfattning.py','bedomning/kundmodell/pep.py','regelverk/villkor.py','bedomning/__init__.py'])
def test_modellbindning_andras_med_motor_regler_och_hjalpfil(api, regelbas, kopia, fil):
    fore=api.modellbindning(regelbas)
    with (kopia/'src'/'riskanalys'/fil).open('a') as f: f.write('\n# Ändrad modellfil\n')
    assert api.modellbindning(regelbas)!=fore
    assert api.modellbindning(regelbas.model_copy(update={'kontrollsumma':'sha256:'+'1'*64}))!=fore


def test_miljo_och_presentationsbyte_bryter_inte_modellbindning(api, regelbas, kopia, monkeypatch):
    fore=api.modellbindning(regelbas)
    (kopia/'src/riskanalys/__init__.py').write_text('__version__ = "99.0.0"\n')
    for fil in ['ai/klient.py','dokument/byggare.py','ui/test.py']:
        p=kopia/'src/riskanalys'/fil; p.parent.mkdir(exist_ok=True); p.write_text('raise RuntimeError("presentation")')
    identitet=importlib.import_module('riskanalys.drift.modellidentitet')
    monkeypatch.setattr(identitet.platform,'python_version',lambda:'99.0')
    assert api.modellmiljo().python=='99.0'
    assert api.modellbindning(regelbas)==fore

@pytest.mark.parametrize('kod', [
    '\ndef hjalp():\n    from riskanalys.profil.nyhjalp import rakna\n',
    '\nfrom .nyhjalp import rakna\n',
    '\nimport importlib\n', '\nx = __import__("riskanalys.profil.nyhjalp")\n',
    '\nfrom riskanalys import __version__\n', '\nimport riskanalys as modellmetadata\n',
])
def test_nytt_beroende_kan_inte_tyst_utelamnas(api, regelbas, kopia, kod):
    with (kopia/'src/riskanalys/bedomning/motor.py').open('a') as f:f.write(kod)
    with pytest.raises(RiskanalysFel): api.modellbindning(regelbas)


def test_saknad_fil_och_korbart_rotinit_blockeras(api, regelbas, kopia):
    (kopia/'src/riskanalys/__init__.py').write_text('x = 42\n')
    with pytest.raises(RiskanalysFel):api.modellbindning(regelbas)
    (kopia/'src/riskanalys/__init__.py').write_text('__version__="1"\n')
    (kopia/'src/riskanalys/bedomning/erfarenheter.py').unlink()
    with pytest.raises(RiskanalysFel):api.modellbindning(regelbas)


def test_export_bevarar_rapport_utan_autoattest_och_nekar_overskrivning(api, regelbas, tmp_path):
    rapport,paket=projekt(api,regelbas,tmp_path,False)
    assert api.las_modellvalidering(paket)==rapport
    assert rapport.m1_beslut=='ej_provat' and rapport.sakkunnig.status=='ej_granskad'
    assert 'Saknas' in rapport.verkliga_driftobservationer
    fore={p.name:p.read_bytes() for p in paket.iterdir()}
    with pytest.raises(RiskanalysFel):api.exportera_modellvalidering(paket,regelbas,rapport,tmp_path/'rapport.pdf')
    assert {p.name:p.read_bytes() for p in paket.iterdir()}==fore
    with (paket/'modellvalidering.pdf').open('ab') as f:f.write(b'ANDRAT')
    with pytest.raises(RiskanalysFel):api.las_modellvalidering(paket)


def test_attest_binder_m1_begransning_och_pdf(api, regelbas, tmp_path):
    rapport,_=projekt(api,regelbas,tmp_path)
    summa=api.valideringens_innehallssumma(rapport)
    assert rapport.sakkunnig.galler(summa)
    for andring in [{'m1_beslut':'ej_provat'},{'begransningar':'Ändrat'},{'rapport_kontrollsumma':'sha256:'+'2'*64}]:
        assert not rapport.sakkunnig.galler(api.valideringens_innehallssumma(rapport.model_copy(update=andring)))


def test_samma_rapport_kan_ateranvandas_i_annan_katalog_och_miljo(api, regelbas, kopia, tmp_path, monkeypatch):
    rapport,paket=projekt(api,regelbas,tmp_path)
    fore=(paket/'modellvalidering.json').read_bytes()
    annan=kopia.parent/'flyttad'; kopia.rename(annan)
    identitet=importlib.import_module('riskanalys.drift.modellidentitet')
    monkeypatch.setattr(identitet,'MODELLROT',annan / 'src/riskanalys')
    monkeypatch.setattr(identitet.platform,'python_version',lambda:'99.0')
    ny=api.exportera_modellvalidering(tmp_path/'leverans-ny',regelbas,rapport,tmp_path/'rapport.pdf')
    assert (ny/'modellvalidering.json').read_bytes()==fore
    assert api.las_modellvalidering(ny)==rapport
    metadata=json.loads((ny/'manifest.json').read_text())['metadata']
    assert json.loads(metadata['miljo'])['python']=='99.0'

@pytest.mark.parametrize('andring', [
    {'modellbindning':'sha256:'+'0'*64},
    {'modellfiler_kontrollsumma':'sha256:'+'0'*64},
    {'rapport_kontrollsumma':'sha256:'+'0'*64},
])
def test_export_nekar_fel_modell_eller_bytes(api, regelbas, tmp_path, andring):
    rapport,_=projekt(api,regelbas,tmp_path)
    with pytest.raises(RiskanalysFel):
        api.exportera_modellvalidering(tmp_path/'fel-leverans',regelbas,rapport.model_copy(update=andring),tmp_path/'rapport.pdf')
    assert not (tmp_path/'fel-leverans').exists()

@pytest.mark.parametrize('slag',['symlank','extra'])
def test_projektpaket_nekar_lankar_och_oregistrerade_filer(api, regelbas, tmp_path, slag):
    from riskanalys.lagring.manifest import las_manifest, skriv_manifest
    _,paket=projekt(api,regelbas,tmp_path)
    metadata=las_manifest(paket).metadata
    if slag=='symlank':
        (paket/'modellvalidering.pdf').unlink()
        (paket/'modellvalidering.pdf').symlink_to(tmp_path/'rapport.pdf')
    else:
        (paket/'extra.json').write_text('{}')
    skriv_manifest(paket,metadata)
    with pytest.raises(RiskanalysFel):api.las_modellvalidering(paket)


def test_belagg_specialfil_och_symlankad_katalog_nekar(api, regelbas, tmp_path):
    import os
    byra,u,_=adoption(api,regelbas,tmp_path)
    rutin=byra/'analys/belagg/rutin.txt'; rutin.unlink(); os.mkfifo(rutin)
    assert api.modellriskhinder(byra,regelbas,u,DAG)
    rutin.unlink()
    katalog=byra/'analys/belagg'; annan=tmp_path/'annat-belagg'; katalog.rename(annan); katalog.symlink_to(annan,target_is_directory=True)
    assert api.modellriskhinder(byra,regelbas,u,DAG)

@pytest.mark.parametrize('andring',[{'m1_beslut':'andring_kravs'}, {'begransningar':'Efter attest ändrad begränsning'}])
def test_lokal_adoption_kan_inte_ersatta_giltigt_expertbeslut(api, regelbas, tmp_path, andring):
    byra,u,rapport=adoption(api,regelbas,tmp_path)
    fil=byra/'analys/belagg/modellvalidering.json'
    fil.write_text(rapport.model_copy(update=andring).model_dump_json(indent=2))
    uppdaterad=api.Modellbelagg(fil=fil.name,kontrollsumma=for_fil(fil))
    assert api.modellriskhinder(byra,regelbas,u.model_copy(update={'projektrapport':uppdaterad}),DAG)


def test_syntetisk_provning_blir_inte_verkliga_felutfall(api, regelbas, tmp_path):
    byra,u,rapport=adoption(api,regelbas,tmp_path,False)
    fore=u.model_dump_json()
    filer={p.name:p.read_bytes() for p in (byra/'analys/belagg').iterdir()}
    assert api.modellriskhinder(byra,regelbas,u,DAG)
    assert u.model_dump_json()==fore and u.fel==()
    assert rapport.verkliga_driftobservationer=='Saknas; inte observerat i drift'
    assert {p.name:p.read_bytes() for p in (byra/'analys/belagg').iterdir()}==filer


def test_dotted_import_far_inte_gora_rotversion_till_modellindata(api, regelbas, kopia):
    with (kopia/'src/riskanalys/bedomning/motor.py').open('a') as fil:
        fil.write('\nimport riskanalys.bedomning.motor\nx = riskanalys.__version__\n')
    with pytest.raises(RiskanalysFel):api.modellbindning(regelbas)


def test_extremt_framtida_datum_blir_hinder_utan_krasch(api, regelbas, tmp_path):
    byra,u,_=adoption(api,regelbas,tmp_path)
    u=u.model_copy(update={'utvarderad':date(9999,1,1),'nasta_genomgang':date(9999,12,31),'beslutsdatum':date(9999,1,1)})
    assert api.modellriskhinder(byra,regelbas,u,DAG)


def test_installerad_distribution_har_samma_identitet_som_kallkopia(api, regelbas, kopia, tmp_path):
    import subprocess
    import sys
    installerad=tmp_path/'site-packages'
    shutil.copytree(kopia/'src/riskanalys',installerad/'riskanalys')
    kod='''import sys
from types import SimpleNamespace
sys.path.insert(0, sys.argv[1])
from riskanalys.drift.modellrisk import modellbindning
print(modellbindning(SimpleNamespace(kontrollsumma=sys.argv[2])))
'''
    resultat=subprocess.run([sys.executable,'-c',kod,str(installerad),regelbas.kontrollsumma],cwd=tmp_path,capture_output=True,text=True)
    assert resultat.returncode==0, resultat.stderr
    assert resultat.stdout.strip()==api.modellbindning(regelbas)


def test_historisk_rapport_lases_efter_utokat_aktuellt_inventarium(api, regelbas, tmp_path, monkeypatch, kopia):
    byra,u,rapport=adoption(api,regelbas,tmp_path)
    paket=tmp_path/'leverans'
    (kopia/'src/riskanalys/profil/nyhjalp.py').write_text('def rakna(): return 999\n')
    identitet=importlib.import_module('riskanalys.drift.modellidentitet')
    monkeypatch.setattr(identitet,'MODELLFILER',tuple(sorted((*identitet.MODELLFILER,'src/riskanalys/profil/nyhjalp.py'))))
    assert api.las_modellvalidering(paket)==rapport
    assert api.modellbindning(regelbas)!=rapport.modellbindning
    assert api.modellriskhinder(byra,regelbas,u,DAG)

@pytest.mark.parametrize('kod',[
    '\nfrom builtins import __import__ as hamta_modul\n',
    '\nfrom builtins import eval as utvardera_text\n',
    '\nhamta_modul = __import__\n',
    '\nkor_kod = exec\n',
    '\nimport builtins as standard\nhamta_modul = standard.__import__\n',
])
def test_alias_till_dynamisk_laddare_blockeras(api, regelbas, kopia, kod):
    with (kopia/'src/riskanalys/bedomning/motor.py').open('a') as fil:fil.write(kod)
    with pytest.raises(RiskanalysFel):api.modellbindning(regelbas)
