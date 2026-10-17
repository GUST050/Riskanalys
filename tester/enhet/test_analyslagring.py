"""CAS, privata kopior och låsta beslut provas med syntetiska filer."""
import importlib.util
from datetime import date
from pathlib import Path

import pytest


def test_analyslagring_finns_for_cas_och_filsakerhet():
    assert importlib.util.find_spec('riskanalys.analys.lagring') is not None


@pytest.fixture
def lagring():
    if importlib.util.find_spec('riskanalys.analys.lagring') is None:
        pytest.skip('RED: lagring saknas')
    from riskanalys.analys import lagring
    return lagring


@pytest.fixture
def paket():
    from riskanalys.analys.modeller import Analysbindning, Analyspaket
    return Analyspaket(bindning=Analysbindning(byra='syntetisk',profilrevision='p',
        bedomningsmanifest='b',utkastmanifest='u',regelbas='r',kallunderlag='k',historik='',
        bedomningsdatum=date(2026,10,1),modell='m'))


def test_stale_cas_bevarar_tidigare_fil(lagring,paket,tmp_path):
    from riskanalys.fel import RiskanalysFel
    assert lagring.las_analys(tmp_path) is None
    summa=lagring.spara_analys(tmp_path,paket,forvantad_summa='')
    fil=tmp_path/'analys/analys.yaml'
    fore=fil.read_bytes()
    nytt=paket.model_copy(update={'revision':0,'bindning':paket.bindning.model_copy(update={'utkastmanifest':'nytt'})})
    with pytest.raises(RiskanalysFel):lagring.spara_analys(tmp_path,nytt,forvantad_summa='fel')
    assert fil.read_bytes()==fore
    ny=lagring.spara_analys(tmp_path,nytt,forvantad_summa=summa)
    assert ny!=summa
    assert lagring.las_analys(tmp_path).revision==2
    assert len(list((tmp_path/'analys/historik').glob('*.yaml')))==1
    assert fil.stat().st_mode&0o777==0o600


def test_avbruten_sparning_lamnar_lasbart_register(lagring,paket,tmp_path,monkeypatch):
    from riskanalys.fel import RiskanalysFel
    summa=lagring.spara_analys(tmp_path,paket,forvantad_summa='')
    def avbrott(*args,**kwargs):raise OSError('syntetiskt avbrott före replace')
    monkeypatch.setattr(lagring.os,'replace',avbrott)
    nytt=paket.model_copy(update={'bindning':paket.bindning.model_copy(update={'utkastmanifest':'nytt'})})
    with pytest.raises(RiskanalysFel):lagring.spara_analys(tmp_path,nytt,forvantad_summa=summa)
    assert lagring.las_analys(tmp_path)==paket
    assert not list((tmp_path/'analys').glob('*.tmp'))


def test_belaggsfil_utanfor_privata_roten_avvisas(lagring,tmp_path):
    from riskanalys.fel import RiskanalysFel
    kallfil=tmp_path/'valt.txt';kallfil.write_text('uttryckligen valt syntetiskt underlag')
    byra=tmp_path/'byra'
    rel,summa=lagring.importera_belagg(byra,kallfil)
    assert '/' not in rel
    assert lagring.las_belaggsfil(byra,rel,summa)==kallfil.read_bytes()
    lank=tmp_path/'lank';lank.symlink_to(kallfil)
    with pytest.raises(RiskanalysFel):lagring.importera_belagg(byra,lank)
    for fil in ('../valt.txt',str(kallfil),'belagg/../../valt.txt'):
        with pytest.raises(RiskanalysFel):lagring.las_belaggsfil(byra,fil,summa)
    (byra/'analys/belagg'/rel).write_text('ändrade bytes med samma filnamn')
    with pytest.raises(RiskanalysFel):lagring.las_belaggsfil(byra,rel,summa)


def test_symlankad_belaggsrot_avvisas(lagring,tmp_path):
    from riskanalys.fel import RiskanalysFel
    fil=tmp_path/'valt';fil.write_text('syntetisk')
    byra=tmp_path/'byra';(byra/'analys').mkdir(parents=True)
    (byra/'analys/belagg').symlink_to(tmp_path,target_is_directory=True)
    with pytest.raises(RiskanalysFel):lagring.importera_belagg(byra,fil)


def _symlankad_kalla(tmp_path):
    """Syntetisk källfil i en mapp som också nås via symlänk, som /tmp → /private/tmp på macOS."""
    riktig=tmp_path/'riktig';riktig.mkdir()
    fil=riktig/'rutin.pdf';fil.write_bytes(b'%PDF-1.4 syntetisk rutin')
    lank=tmp_path/'lank';lank.symlink_to(riktig,target_is_directory=True)
    return riktig,lank,fil


def test_vald_kalla_genom_symlankad_foraldermapp_importeras(lagring,tmp_path):
    from riskanalys.lagring.kontrollsumma import for_bytes
    _,lank,fil=_symlankad_kalla(tmp_path)
    byra=tmp_path/'byra'
    rel,hash=lagring.importera_belagg(byra,lank/'rutin.pdf')
    assert hash==for_bytes(fil.read_bytes())
    assert (byra/'analys/belagg'/rel).read_bytes()==fil.read_bytes()
    assert lagring.las_belaggsfil(byra,rel,hash)==fil.read_bytes()


def test_vald_kalla_som_sjalv_ar_symlank_avvisas(lagring,tmp_path):
    from riskanalys.fel import RiskanalysFel
    riktig,lank,fil=_symlankad_kalla(tmp_path)
    (riktig/'genvag.pdf').symlink_to(fil)
    byra=tmp_path/'byra'
    for vald in (riktig/'genvag.pdf',lank/'genvag.pdf'):
        with pytest.raises(RiskanalysFel):lagring.importera_belagg(byra,vald)
    assert not byra.exists()


def test_relativ_kalla_fran_symlankad_arbetsmapp(lagring,tmp_path,monkeypatch):
    _,lank,fil=_symlankad_kalla(tmp_path)
    byra=tmp_path/'byra'
    monkeypatch.chdir(lank)
    for vald in (Path('rutin.pdf'),Path('../lank/rutin.pdf')):
        rel,hash=lagring.importera_belagg(byra,vald)
        assert lagring.las_belaggsfil(byra,rel,hash)==fil.read_bytes()


def test_las_belaggsfil_genom_symlankad_byraforalder_avvisas(lagring,tmp_path):
    from riskanalys.fel import RiskanalysFel
    riktig=tmp_path/'riktig';riktig.mkdir()
    kalla=tmp_path/'kalla.txt';kalla.write_bytes(b'syntetiskt privat underlag')
    rel,hash=lagring.importera_belagg(riktig/'byra',kalla)
    lank=tmp_path/'lank';lank.symlink_to(riktig,target_is_directory=True)
    with pytest.raises(RiskanalysFel):lagring.las_belaggsfil(lank/'byra',rel,hash)


def test_importerat_belagg_kan_lasas_direkt_av_ab7(lagring,tmp_path):
    from riskanalys.drift.modellrisk import Modellbelagg, _belaggsbytes
    fil=tmp_path/'vald.pdf';fil.write_bytes(b'syntetisk rapport')
    rel,hash=lagring.importera_belagg(tmp_path/'byra',fil)
    assert _belaggsbytes(tmp_path/'byra',Modellbelagg(fil=rel,kontrollsumma=hash))==fil.read_bytes()


def test_to_samtidiga_svar_skriver_inte_over_varandra(lagring,paket,tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from riskanalys.fel import RiskanalysFel
    cas=lagring.spara_analys(tmp_path,paket,forvantad_summa='')
    start=Barrier(2)
    def skriv(n):
        nytt=paket.model_copy(update={'bindning':paket.bindning.model_copy(update={'utkastmanifest':str(n)})})
        start.wait()
        try:lagring.spara_analys(tmp_path,nytt,forvantad_summa=cas);return 'sparat'
        except RiskanalysFel:return 'inaktuellt'
    with ThreadPoolExecutor(max_workers=2) as pool:
        resultat=list(pool.map(skriv,(1,2)))
    assert sorted(resultat)==['inaktuellt','sparat']
    assert lagring.las_analys(tmp_path).revision==2


def test_import_far_inte_skriva_beslut_eller_valja_revision(lagring,paket,tmp_path):
    from riskanalys.analys.modeller import Analysbeslut
    from riskanalys.fel import RiskanalysFel
    from riskanalys.analys.provning import svarssumma,underlagssumma
    cas=lagring.spara_analys(tmp_path,paket.model_copy(update={'revision':100}),forvantad_summa='')
    gammalt=lagring.las_analys(tmp_path)
    assert gammalt.revision==1
    d=Analysbeslut(tjanst='t',revision=1,underlagssumma=underlagssumma(gammalt),svarssumma=svarssumma(gammalt),
        godkand=True,namn='Ada',roll='ansvarig',datum=date(2026,10,15))
    with pytest.raises(RiskanalysFel):lagring.spara_analys(tmp_path,gammalt.model_copy(update={'beslut':(d,)}),forvantad_summa=cas)
    assert lagring.las_analys(tmp_path)==gammalt


def test_gemensamt_las_haller_profilen_genom_publicering(lagring,paket,tmp_path,minimal_regelbas,profil_fabrik):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from riskanalys.profil.lagring import spara_profil
    profil=profil_fabrik(minimal_regelbas,{})
    spara_profil(tmp_path,profil)
    start=Event();klart=Event()
    def skriv():
        start.set();spara_profil(tmp_path,profil);klart.set()
    with ThreadPoolExecutor(max_workers=1) as pool:
        with lagring.analyslas(tmp_path):
            jobb=pool.submit(skriv)
            assert start.wait(1)
            assert not klart.wait(.05)
            lagring.spara_analys_last(tmp_path,paket,forvantad_summa='')
        jobb.result(timeout=2)
    assert klart.is_set()


def test_otillatna_registrerade_filer_avvisas(lagring,paket,tmp_path):
    from riskanalys.fel import RiskanalysFel
    lagring.spara_analys(tmp_path,paket,forvantad_summa='')
    fil=tmp_path/'analys/analys.yaml';fil.unlink()
    osakert=tmp_path/'utanf.yaml';osakert.write_text('syntetisk')
    fil.symlink_to(osakert)
    with pytest.raises(RiskanalysFel):lagring.las_analys(tmp_path)


def test_snapshot_fryser_exakta_belaggsbytes_utan_levande_omlasning(lagring,paket,tmp_path,regelbas):
    from riskanalys.analys.modeller import Analysbelagg
    assert hasattr(lagring,'las_analyssnapshot_last'),'Gemensam fryst snapshot saknas'
    fil=tmp_path/'valt';fil.write_bytes(b'original kontrollkopia')
    byra=tmp_path/'byra';rel,hash=lagring.importera_belagg(byra,fil)
    b=Analysbelagg(id='b',dokument=rel,kontrollsumma=hash,datum=date(2026,10,1))
    paket=paket.model_copy(update={'belagg':(b,)})
    lagring.spara_analys(byra,paket,forvantad_summa='')
    # Snapshot's byte copying is independent of semantic model validation; this fixture intentionally has no live runs.
    with lagring.analyslas(byra):
        snap=lagring.las_analyssnapshot_last(byra,regelbas,date(2026,10,15),bedomningsmapp=tmp_path/'saknas',utkastmapp=tmp_path/'saknas')
    assert snap.paket==paket
    assert dict(snap.filer)[rel]==b'original kontrollkopia'
    (byra/'analys/belagg'/rel).write_bytes('senare ändring'.encode())
    assert dict(snap.filer)[rel]==b'original kontrollkopia'
    assert snap.brister  # Missing live basis never becomes implicitly approved.


def test_modellrapportimport_anvander_samma_belaggsrot(lagring,regelbas,tmp_path):
    assert hasattr(lagring,'importera_modellrapport'),'Registrerad trippelimport saknas'
    from riskanalys.drift import modellrisk as mr
    from tester.enhet.test_modellrisk import projekt
    rapport,projektmapp=projekt(mr,regelbas,tmp_path)
    byra=tmp_path/'byra'
    kopia=lagring.importera_modellrapport(byra,projektmapp)
    assert lagring.las_belaggsfil(byra,kopia.projektrapport.fil,kopia.projektrapport.kontrollsumma)==(projektmapp/'modellvalidering.json').read_bytes()
    assert mr._belaggsbytes(byra,kopia.valideringsrapport)==(projektmapp/'modellvalidering.pdf').read_bytes()
    assert mr._belaggsbytes(byra,kopia.modellfiler)==(projektmapp/'modellfiler.json').read_bytes()


def test_modellrapport_genom_symlankad_foraldermapp_importeras(lagring,regelbas,tmp_path):
    from riskanalys.drift import modellrisk as mr
    from tester.enhet.test_modellrisk import projekt
    riktig=tmp_path/'riktig';riktig.mkdir()
    _,projektmapp=projekt(mr,regelbas,riktig)
    lank=tmp_path/'lank';lank.symlink_to(riktig,target_is_directory=True)
    byra=tmp_path/'byra'
    kopia=lagring.importera_modellrapport(byra,lank/projektmapp.name)
    for b,namn in ((kopia.projektrapport,'modellvalidering.json'),(kopia.valideringsrapport,'modellvalidering.pdf'),
                   (kopia.modellfiler,'modellfiler.json')):
        assert lagring.las_belaggsfil(byra,b.fil,b.kontrollsumma)==(projektmapp/namn).read_bytes()


def test_modellrapportfil_som_byts_mot_symlank_efter_paketkontroll_avvisas(lagring,regelbas,tmp_path,monkeypatch):
    from riskanalys.drift import modellrisk as mr
    from riskanalys.fel import RiskanalysFel
    from tester.enhet.test_modellrisk import projekt
    _,projektmapp=projekt(mr,regelbas,tmp_path)
    fil=projektmapp/'modellfiler.json'
    kopia=tmp_path/'kopia.json';kopia.write_bytes(fil.read_bytes())
    original=mr.las_modellvalidering
    def kontrollera_och_byt(mapp):
        rapport=original(mapp)
        fil.unlink();fil.symlink_to(kopia)
        return rapport
    monkeypatch.setattr(mr,'las_modellvalidering',kontrollera_och_byt)
    byra=tmp_path/'byra'
    with pytest.raises(RiskanalysFel):lagring.importera_modellrapport(byra,projektmapp)
    assert not byra.exists()


@pytest.fixture
def verklig_skrivkedja(lagring,regelbas_v1,tmp_path):
    from riskanalys.profil.hantering import skapa_profil
    from riskanalys.profil.modeller import Byra
    from riskanalys.profil.lagring import spara_profil
    from riskanalys.bedomning.korning import kor_bedomning,las_bedomning
    from riskanalys.dokument.skrivning import kor_skrivning
    from riskanalys.dokument.leverantor import Testleverantor
    from riskanalys.dokument.underlag import tjanster_med_avsnitt
    from riskanalys.dokument.skrivversion import delar_for_version
    from tester.fixturer.m2 import komplett_profil,godkant_delsvar
    rb=regelbas_v1;byra=tmp_path/'skrivkedja'
    profil=komplett_profil(rb,skapa_profil(rb,Byra(id='skrivkedja',regelpaket='RP-RED-VG',datum=date(2026,10,15),lan='Västra Götaland')))
    upp=dict(profil.uppgifter)
    for c in rb.kontroller.values():
        upp[c.genomforande_falt]=upp[c.genomforande_falt].model_copy(update={'varde':'ej_belagt'})
    profil=profil.model_copy(update={'uppgifter':upp})
    spara_profil(byra,profil)
    bm=kor_bedomning(byra,rb);b=las_bedomning(bm)
    svar=[godkant_delsvar(d,t) for _,t in tjanster_med_avsnitt(b) for d in delar_for_version('D-ARB-tjanst-v6')]
    um=kor_skrivning(byra,rb,Testleverantor(svar))
    return byra,rb,profil,b,bm,um


def test_bygg_bindning_verifierar_verkliga_v6_skrivresultat(lagring,verklig_skrivkedja):
    byra,rb,profil,b,bm,um=verklig_skrivkedja
    bindning=lagring.bygg_bindning(byra,rb,bm,um)
    assert bindning.byra==profil.byra.id
    assert bindning.bedomningsdatum==b.datum
    assert bindning.bedomningsmanifest!=bindning.utkastmanifest
    assert bindning.modell.startswith('sha256:')


def test_bindning_avvisar_skrivresultat_som_etiketterats_om(lagring,verklig_skrivkedja):
    from riskanalys.fel import RiskanalysFel
    from riskanalys.lagring.manifest import skriv_manifest,las_manifest
    import json
    byra,rb,_,_,bm,um=verklig_skrivkedja
    fil=next(p for p in um.glob('*.json') if p.name!='manifest.json')
    data=json.loads(fil.read_text());data['tjanst']='T-RED-01' if data['tjanst']!='T-RED-01' else 'T-BOLAG-01'
    fil.write_text(json.dumps(data))
    skriv_manifest(um,las_manifest(um).metadata)
    with pytest.raises(RiskanalysFel):lagring.bygg_bindning(byra,rb,bm,um)


def test_bindning_avvisar_extra_dubblerat_tjanstresultat(lagring,verklig_skrivkedja):
    from riskanalys.fel import RiskanalysFel
    from riskanalys.lagring.manifest import skriv_manifest,las_manifest
    byra,rb,_,_,bm,um=verklig_skrivkedja
    fil=next(p for p in um.glob('*.json') if p.name!='manifest.json')
    (um/'extra.json').write_bytes(fil.read_bytes())
    skriv_manifest(um,las_manifest(um).metadata)
    with pytest.raises(RiskanalysFel):lagring.bygg_bindning(byra,rb,bm,um)


def test_las_godkannandetransaktion_och_senare_underkannande(lagring,verklig_skrivkedja,tmp_path):
    from riskanalys.analys.utkast import forifyll_analys
    from riskanalys.analys.modeller import Analysbeslut
    from riskanalys.analys.provning import underlagssumma,svarssumma,gallande_beslut,analysbrister
    from tester.fixturer.lokal_analys import bekraftat_utkast
    from tester.enhet.test_modellrisk import projekt,DAG
    from riskanalys.drift import modellrisk as mr
    byra,rb,profil,b,bm,um=verklig_skrivkedja
    bindning=lagring.bygg_bindning(byra,rb,bm,um)
    paket=bekraftat_utkast(forifyll_analys(rb,profil,b,bindning),rb)
    rapport,mapp=projekt(mr,rb,tmp_path)
    kopia=lagring.importera_modellrapport(byra,mapp)
    rutin=tmp_path/'rutin.txt';rutin.write_text('Syntetisk löpande uppföljning av verkliga fel.')
    fil,hash=lagring.importera_belagg(byra,rutin)
    underlag=mr.Modellriskunderlag(modellansvarig='Syntetisk ansvarig',modellbindning=bindning.modell,
        rutin=mr.Modellbelagg(fil=fil,kontrollsumma=hash),projektrapport=kopia.projektrapport,
        valideringsrapport=kopia.valideringsrapport,modellfiler=kopia.modellfiler,
        utvarderad=DAG,nasta_genomgang=date(2027,10,15),feluppfoljning='Kontrollera verkliga fel varje månad; inga driftobservationer än.',
        fel=(),godkand=True,beslutad_av='Syntetisk Ada',beslutsdatum=DAG)
    paket=paket.model_copy(update={'modellrisk':underlag})
    assert not analysbrister(rb,profil,b,paket),analysbrister(rb,profil,b,paket)
    cas=lagring.spara_analys(byra,paket,forvantad_summa='')
    def beslut(godkand):
        return Analysbeslut(tjanst=paket.tjanster[0].tjanst,revision=paket.revision,
            underlagssumma=underlagssumma(paket),svarssumma=svarssumma(paket),godkand=godkand,
            namn='Syntetisk Ada',roll='ansvarig',datum=DAG,kommentar=None if godkand else 'Ny lokal invändning.')
    cas=lagring.registrera_analysbeslut(byra,rb,beslut(True),forvantad_summa=cas,bedomningsmapp=bm,utkastmapp=um)
    sparat=lagring.las_analys(byra)
    assert gallande_beslut(sparat,paket.tjanster[0].tjanst).godkand
    assert sparat.revision==1 and sparat.beslut[-1].egen_granskning
    with lagring.analyslas(byra):
        ny=lagring.registrera_analysbeslut_last(byra,rb,beslut(False),forvantad_summa=cas,bedomningsmapp=bm,utkastmapp=um)
    assert ny!=cas
    assert not gallande_beslut(lagring.las_analys(byra),paket.tjanster[0].tjanst).godkand


def test_aven_underkannande_kraver_aktuellt_underlag(lagring,verklig_skrivkedja):
    from riskanalys.analys.utkast import forifyll_analys
    from riskanalys.analys.modeller import Analysbeslut
    from riskanalys.analys.provning import underlagssumma,svarssumma
    from riskanalys.profil.lagring import spara_profil
    from riskanalys.fel import RiskanalysFel
    byra,rb,profil,b,bm,um=verklig_skrivkedja
    paket=forifyll_analys(rb,profil,b,lagring.bygg_bindning(byra,rb,bm,um))
    t=paket.tjanster[0].model_copy(update={'forfattare':'Ada'})
    paket=paket.model_copy(update={'tjanster':(t,*paket.tjanster[1:])})
    cas=lagring.spara_analys(byra,paket,forvantad_summa='')
    upp=dict(profil.uppgifter);id=next(iter(upp));upp[id]=upp[id].model_copy(update={'kalla':'Ändrat källunderlag'})
    spara_profil(byra,profil.model_copy(update={'uppgifter':upp}))
    beslut=Analysbeslut(tjanst=t.tjanst,revision=paket.revision,underlagssumma=underlagssumma(paket),svarssumma=svarssumma(paket),
        godkand=False,namn='Ada',roll='ansvarig',datum=date(2026,10,15),kommentar='Invändning från inaktuell flik.')
    with pytest.raises(RiskanalysFel):lagring.registrera_analysbeslut(byra,rb,beslut,forvantad_summa=cas,bedomningsmapp=bm,utkastmapp=um)
    assert lagring.las_analys(byra).beslut==()


def test_leverantor_far_inte_tyst_motsaga_bekraftad_profil(lagring,verklig_skrivkedja):
    from riskanalys.analys.utkast import forifyll_analys
    from riskanalys.analys.modeller import Leverantorsprovning
    from riskanalys.analys.provning import analysbrister
    byra,rb,profil,b,bm,um=verklig_skrivkedja
    paket=forifyll_analys(rb,profil,b,lagring.bygg_bindning(byra,rb,bm,um))
    a=paket.tjanster[0].model_copy(update={'leverantorer':(Leverantorsprovning(id='lokal-kyc'),)})
    assert any('motsäger profilens' in f for f in analysbrister(rb,profil,b,paket.model_copy(update={'tjanster':(a,*paket.tjanster[1:])})))


@pytest.mark.parametrize('operation',['import','spara','las'])
def test_symlank_i_byraforalder_avvisas_fore_skapande(lagring,paket,tmp_path,operation):
    from riskanalys.fel import RiskanalysFel
    real=tmp_path/'riktig';real.mkdir()
    lank=tmp_path/'lank';lank.symlink_to(real,target_is_directory=True)
    byra=lank/'inte-skapad'/'byra'
    source=tmp_path/'source';source.write_bytes(b'privat syntetiskt underlag')
    with pytest.raises(RiskanalysFel):
        if operation=='import':lagring.importera_belagg(byra,source)
        elif operation=='spara':lagring.spara_analys(byra,paket,forvantad_summa='')
        else:
            with lagring.analyslas(byra):pass
    assert list(real.iterdir())==[]


def test_privata_destinationer_har_0700_och_0600(lagring,paket,tmp_path):
    source=tmp_path/'source';source.write_bytes(b'syntetisk privat kopia')
    byra=tmp_path/'nyrot'/'byra'
    rel,_=lagring.importera_belagg(byra,source)
    cas=lagring.spara_analys(byra,paket,forvantad_summa='')
    nytt=paket.model_copy(update={'bindning':paket.bindning.model_copy(update={'utkastmanifest':'revision2'})})
    lagring.spara_analys(byra,nytt,forvantad_summa=cas)
    for mapp in (tmp_path/'nyrot',byra,byra/'profil',byra/'analys',byra/'drift',byra/'analys/belagg',byra/'analys/historik'):
        assert mapp.stat().st_mode&0o777==0o700
    for fil in byra.rglob('*'):
        if fil.is_file():assert fil.stat().st_mode&0o777==0o600


def test_atomiskt_namnbyte_anvander_samma_kontrollerade_kataloghandtag(lagring,paket,tmp_path,monkeypatch):
    byra=tmp_path/'byra';annan=tmp_path/'annan';annan.mkdir()
    original=lagring.os.replace
    flyttad=byra/'ursprunglig-analys'
    def byt(src,dst,**kwargs):
        assert kwargs['src_dir_fd']==kwargs['dst_dir_fd']
        assert isinstance(src,str) and '/' not in src
        assert dst=='analys.yaml'
        (byra/'analys').rename(flyttad)
        (byra/'analys').symlink_to(annan,target_is_directory=True)
        return original(src,dst,**kwargs)
    monkeypatch.setattr(lagring.os,'replace',byt)
    lagring.spara_analys(byra,paket,forvantad_summa='')
    assert (flyttad/'analys.yaml').is_file()
    assert list(annan.iterdir())==[]
