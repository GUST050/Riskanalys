"""AB5 binder dokumentet och publiceringen till exakt fryst lokal evidens."""
from datetime import date
import json

import pytest

from riskanalys.dokument.modeller import Avsnitt, Dokument, Textstycke
from riskanalys.faststallelse.modeller import Sakgranskning
from riskanalys.faststallelse.sakgranskning import registrera_sakgranskning, galler_sakgranskning
from riskanalys.faststallelse.faststall import formathinder

DAG = date(2026, 10, 15)
V6 = 'D-ARB-tjanst-v6'


@pytest.fixture
def profil(regelbas, profil_fabrik, real_varden):
    return profil_fabrik(regelbas, real_varden)


def dokument(text='Första texten.'):
    return Dokument(id='D-ARB', titel='Riskbedömning', avsnitt=(Avsnitt(
        id='D-ARB.6.1', rubrik='Tjänst', kalla='regelbas', formatversion=V6,
        stycken=(Textstycke(typ='beskrivning',text=text,referenser=[]),)),))


def test_senaste_dokumentbeslut_aterupplivar_inte_aldre_ja(profil):
    d = dokument()
    beslut = registrera_sakgranskning((),d,profil,'D-ARB.6.1',True,'FfR','Test',DAG)
    annat = dokument('Ny text.')
    beslut = registrera_sakgranskning(beslut,annat,profil,'D-ARB.6.1',False,'FfR','Test',DAG,'Fel')
    assert galler_sakgranskning(beslut,d.avsnitt[0],profil,d) is None


def test_dokumentattest_binder_hela_registret(profil):
    d = dokument()
    beslut = registrera_sakgranskning((),d,profil,'D-ARB.6.1',True,'FfR','Test',DAG,analysbindning='sha256:ett')
    assert galler_sakgranskning(beslut,d.avsnitt[0],profil,d,analysbindning='sha256:ett')
    assert galler_sakgranskning(beslut,d.avsnitt[0],profil,d,analysbindning='sha256:tva') is None
    assert galler_sakgranskning(beslut,d.avsnitt[0],profil,d) is None


def test_historisk_sakgranskning_utelamnar_endast_ny_none():
    s = Sakgranskning(avsnitt='D',kontrollsumma='x',godkand=True,roll='FfR',namn='Test',datum=DAG)
    data = json.loads(s.model_dump_json())
    assert 'analysbindning' not in data
    assert data['dokumentstruktur'] is None and data['kommentar'] is None


@pytest.mark.parametrize('version',['D-ARB-tjanst-v5','D-ARB-tjanst-v5.1'])
def test_v5_och_v5_1_kan_inte_nyfaststallas_efter_v6(regelbas_v1,version):
    d = dokument().model_copy(update={'avsnitt':(dokument().avsnitt[0].model_copy(update={'formatversion':version}),)})
    assert formathinder(regelbas_v1,d)


def test_fryser_analys_och_faktiska_belagg_utan_levande_register(tmp_path):
    from riskanalys.analys.modeller import Analysbindning, Analyspaket, Analysbelagg
    from riskanalys.analys.lagring import Analyssnapshot
    from riskanalys.analys.provning import registersumma
    from riskanalys.lagring.kontrollsumma import for_bytes
    import importlib
    helper = importlib.import_module('riskanalys.granskning.analysunderlag')
    data = b'syntetiskt rutinunderlag'
    a = Analyspaket(bindning=Analysbindning(byra='b',profilrevision='p',bedomningsmanifest='b',utkastmanifest='u',regelbas='r',kallunderlag='k',historik='',bedomningsdatum=DAG,modell='m'),
        belagg=(Analysbelagg(id='rutin',dokument='rutin.bin',kontrollsumma=for_bytes(data),datum=DAG),))
    snapshot = Analyssnapshot(a,registersumma(a),('Utkast.',),(('rutin.bin',data),))
    helper.spara_fryst_analys(tmp_path,snapshot)
    nytt = helper.las_fryst_analys(tmp_path)
    assert nytt == snapshot
    assert (tmp_path/'analys/belagg/rutin.bin').read_bytes() == data
    (tmp_path/'analys/belagg/rutin.bin').write_bytes(b'utbytt')
    from riskanalys.fel import RiskanalysFel
    with pytest.raises(RiskanalysFel): helper.las_fryst_analys(tmp_path)


def test_v6_saknad_analys_blir_blockerande_utan_aldre_aterbyggnad(regelbas_v1,profil):
    from riskanalys.granskning.dokument_v6 import analysfynd_v6
    from riskanalys.bedomning.motor import bedom
    from riskanalys.regelverk.urval import valj
    from riskanalys.drift.historik import Historik
    # An intentionally incomplete v6 document still produces findings, never legacy StopIteration.
    b=bedom(regelbas_v1,valj(regelbas_v1,profil.byra.regelpaket,profil.byra.datum,profil.byra.lan),profil)
    fynd=analysfynd_v6(regelbas_v1,b,profil,dokument(),Historik(),{},analys=None)
    assert fynd and all(f['allvar']=='blockerande' for f in fynd)


def test_v7_granskning_fryser_ofullstandig_analys_som_utkast(regelbas_v1,tmp_path):
    from tester.fixturer.analys_hela_kedjan import skapa_fall, skriv_fall
    from riskanalys.profil.lagring import spara_profil
    from riskanalys.bedomning.korning import kor_bedomning
    from riskanalys.dokument.skrivning import kor_skrivning
    from riskanalys.dokument.leverantor import Testleverantor
    from tester.fixturer.m2 import bygg_delsvar
    from riskanalys.analys.lagring import bygg_bindning,spara_analys
    from riskanalys.granskning.korning import kor_granskning,las_granskning
    from riskanalys.granskning.analysunderlag import las_fryst_analys
    f=skapa_fall(regelbas_v1,tmp_path)
    spara_profil(f.byramapp,f.profil)
    bm=kor_bedomning(f.byramapp,regelbas_v1)
    um=kor_skrivning(f.byramapp,regelbas_v1,Testleverantor(bygg_delsvar(regelbas_v1,f.profil,f.bedomning)),formatversion='D-ARB-tjanst-v7')
    a=f.analys.model_copy(update={'bindning':bygg_bindning(f.byramapp,regelbas_v1,bm,um)})
    spara_analys(f.byramapp,a,forvantad_summa='')
    gm=kor_granskning(f.byramapp,regelbas_v1,DAG)
    frozen=las_fryst_analys(gm)
    assert frozen.paket == a and len(frozen.filer)>=5
    assert any('modellrisk' in x.lower() for x in frozen.brister)
    d,fynd=las_granskning(gm)
    assert d.formatversion=='D-ARB-tjanst-v7' and any(x.allvar=='blockerande' for x in fynd)


def test_fryst_analys_kraver_exakt_levande_register(tmp_path):
    import importlib
    from riskanalys.analys.modeller import Analysbindning, Analyspaket
    from riskanalys.analys.lagring import Analyssnapshot,spara_analys,las_analys
    from riskanalys.analys.provning import registersumma
    h=importlib.import_module('riskanalys.granskning.analysunderlag')
    a=Analyspaket(bindning=Analysbindning(byra='b',profilrevision='p',bedomningsmanifest='b',utkastmanifest='u',regelbas='r',kallunderlag='k',historik='',bedomningsdatum=DAG,modell='m'))
    byra=tmp_path/'byra';gm=tmp_path/'gm'
    spara_analys(byra,a,forvantad_summa='')
    h.spara_fryst_analys(gm,Analyssnapshot(a,registersumma(a),(),()))
    nytt=a.model_copy(update={'bindning':a.bindning.model_copy(update={'kallunderlag':'nytt'})})
    spara_analys(byra,nytt,forvantad_summa=registersumma(a))
    assert h.registerhinder(byra,h.las_fryst_analys(gm))


@pytest.fixture(scope="module")
def historisk_v7_kedja(tmp_path_factory,regelbas_v1):
    tmp_path=tmp_path_factory.mktemp("ab5-kedja")
    """Fryst historisk V7-kedja; inga avstängda grindar eller produktionsattester."""
    import shutil
    from riskanalys.regelverk.laddning import ladda_regelbas
    from tester.m2.test_m2_kedja import expertkopia
    from tester.fixturer.analys_hela_kedjan import skapa_fall, _bekrafta
    from riskanalys.profil.lagring import spara_profil
    from riskanalys.profil.omfattning import harled_andelar
    from riskanalys.bedomning.korning import kor_bedomning,las_bedomning
    from riskanalys.dokument.skrivning import kor_skrivning
    from riskanalys.dokument.leverantor import Testleverantor
    from tester.fixturer.m2 import bygg_delsvar
    from riskanalys.drift.historik import registrera_handelse,Handelse
    from riskanalys.analys import lagring as l, provning as p, modeller as m
    from riskanalys.drift import modellrisk as api
    from tester.enhet.test_modellrisk import projekt
    from riskanalys.granskning.korning import kor_granskning,las_granskning
    from riskanalys.faststallelse.sakgranskning import spara_sakgranskningar
    r,_=expertkopia(tmp_path/'expert','RP-RED-VG')
    rb=ladda_regelbas(r)
    f=skapa_fall(rb,tmp_path/'fall')
    # No riskreduktion is claimed: all four substantive local scenario sets remain.
    upp=dict(f.profil.uppgifter)
    for c in rb.kontroller.values():
        for falt,varde in ((c.utformning_falt,'saknas'),(c.genomforande_falt,'ej_belagt')):
            if falt in upp:upp[falt]=upp[falt].model_copy(update={'varde':varde})
    from tester.fixturer.skrivsvar_v7 import med_verksamhetsval
    profil=med_verksamhetsval(rb,harled_andelar(f.profil.model_copy(update={'uppgifter':upp}),rb))
    spara_profil(f.byramapp,profil)
    bm=kor_bedomning(f.byramapp,rb);b=las_bedomning(bm)
    um=kor_skrivning(f.byramapp,rb,Testleverantor(bygg_delsvar(rb,profil,b,tjanstspecifik=True)),formatversion='D-ARB-tjanst-v7')
    registrera_handelse(f.byramapp,Handelse(datum=DAG,typ='utvärdering',beskrivning='Syntetisk kontroll.'))
    (tmp_path/'rapport').mkdir()
    rapport,projektrot=projekt(api,rb,tmp_path/'rapport')
    imp=l.importera_modellrapport(f.byramapp,projektrot)
    rutinfil=tmp_path/'modellrutin.txt';rutinfil.write_text('Syntetisk månatlig feluppföljning och årlig utvärdering.')
    namn,hash=l.importera_belagg(f.byramapp,rutinfil)
    u=api.Modellriskunderlag(modellansvarig='Syntetisk ansvarig',modellbindning=rapport.modellbindning,
        rutin=api.Modellbelagg(fil=namn,kontrollsumma=hash),projektrapport=imp.projektrapport,
        valideringsrapport=imp.valideringsrapport,modellfiler=imp.modellfiler,
        utvarderad=DAG,nasta_genomgang=date(2027,10,15),feluppfoljning='Syntetisk månatlig granskning av faktiska fel.',
        fel=(),godkand=True,beslutad_av='Syntetisk beslutsfattare',beslutsdatum=DAG)
    a=f.analys.model_copy(update={'bindning':l.bygg_bindning(f.byramapp,rb,bm,um),'modellrisk':u,
        'tjanster':tuple(t.model_copy(update={'reduktionsprovning':'ej_reduktion',
            'reduktionsmotivering':'Ingen reduktion i det faktiska motorutfallet.',
            'gap':tuple(g for g in t.gap if g.typ!='metodkonflikt')}) for t in f.analys.tjanster)})
    a=_bekrafta(a)
    assert p.analysbrister(rb,profil,b,a)==()
    cas=l.spara_analys(f.byramapp,a,forvantad_summa='')
    for t in a.tjanster:
        a=l.las_analys(f.byramapp)
        beslut=m.Analysbeslut(tjanst=t.tjanst,revision=a.revision,underlagssumma=p.underlagssumma(a),svarssumma=p.svarssumma(a),
            godkand=True,namn='Syntetisk granskare',roll='FfR',datum=DAG)
        cas=l.registrera_analysbeslut(f.byramapp,rb,beslut,forvantad_summa=cas,bedomningsmapp=bm,utkastmapp=um)
    gm=kor_granskning(f.byramapp,rb,DAG)
    d,fynd=las_granskning(gm)
    assert not fynd,fynd
    sak=()
    for avsnitt in d.avsnitt:
        sak=registrera_sakgranskning(sak,d,profil,avsnitt.id,True,'FfR','Syntetisk granskare',DAG,analysbindning=cas)
    spara_sakgranskningar(f.byramapp,sak)
    return f.byramapp,r,rb,gm


@pytest.fixture(scope="module")
def _positiv_v8_kedja(tmp_path_factory,regelbas_v1):
    """Aktuell V8-kedja med samma separata syntetiska positiv-fixtur som typfallen.

    Fastställelse- och säkerhetsproven nedan ska nå sina egna assertioner från en
    nollfyndskedja. V7-kontraktsproven använder den separata historiska fixturen.
    """
    from tester.fixturer.analys_hela_kedjan import syntetisk_expertkopia,bygg_bunden_kedja
    from riskanalys.dokument.skrivversion import V8
    rot=tmp_path_factory.mktemp("ab5-positiv-v8")
    regelrot,rb=syntetisk_expertkopia(rot/"expert")
    return bygg_bunden_kedja(rb,rot/"fall",regelrot=regelrot,godkann=True,formatversion=V8)


@pytest.fixture
def aktuell_kedja(_positiv_v8_kedja,tmp_path):
    from tester.fixturer.kedjecache import klona_kedja
    k=klona_kedja(_positiv_v8_kedja,tmp_path)
    return k.fall.byramapp,k.regelrot,k.fall.regelbas,k.granskningsmapp


@pytest.mark.parametrize('falt,varde',[
    ('pt_motivering','Motorns PT-utfall: hög; kvarstående hög. Lokal rimlighetsprövning återstår.'),
    ('tf_motivering','Motorns TF-utfall: mycket hög. Separat lokal prövning återstår.'),
])
def test_standardmotivering_stoppar_verklig_analysattest(aktuell_kedja,falt,varde):
    from riskanalys.analys import lagring as l, provning as p
    from riskanalys.analys.tjanst import Analystjanst
    from riskanalys.profil.lagring import las_profil
    from riskanalys.granskning.korning import granskningens_bedomningsmapp
    from riskanalys.bedomning.korning import las_bedomning
    from riskanalys.fel import RiskanalysFel
    byra,_,rb,gm=aktuell_kedja;q=l.las_analys(byra)
    bm=granskningens_bedomningsmapp(byra,gm)
    assert not p.analysbrister(rb,las_profil(byra),las_bedomning(bm),q)
    a=q.tjanster[0].model_copy(update={falt:varde})
    ny=q.model_copy(update={'tjanster':(a,*q.tjanster[1:])})
    # Förnya visningssummorna: felet ska vara innehållet, inte en gammal bekräftelse.
    ny=ny.model_copy(update={'tjanster':tuple(t.model_copy(update={'block':tuple(
        b.model_copy(update={'bekraftad_summa':p.blocksumma(ny,t.tjanst,b.nummer)})
        for b in t.block)}) for t in ny.tjanster)})
    revision=l.spara_analys(byra,ny,forvantad_summa=p.registersumma(q))
    fore=(byra/l.ANALYSFIL).read_bytes()
    with pytest.raises(RiskanalysFel,match=falt+' saknar ett färdigt svar'):
        Analystjanst(byra,rb).beslut(a.tjanst,True,'Syntetisk granskare','ansvarig',
                                    las_bedomning(bm).datum,'',revision)
    assert (byra/l.ANALYSFIL).read_bytes()==fore


def test_aktiv_obesvarad_frivillig_fordelning_hindrar_inte_v8_faststallelse(tmp_path,monkeypatch):
    """En frivillig lucka är synlig/okänd utan VERIFIERA i en fastställbar V8-kedja."""
    import docx
    import tester.fixturer.analys_hela_kedjan as kedja
    from riskanalys.dokument.skrivversion import V8
    from riskanalys.faststallelse.faststall import faststall,verifiera_version
    from riskanalys.faststallelse.modeller import Beslut
    from riskanalys.granskning.korning import las_granskning
    from riskanalys.intag.fordelning import aktiverad,svarsbrist
    from riskanalys.profil.modeller import Uppgift

    falt='P-TJ.red01_antal_kontant'
    original=kedja._profil
    def utan_fordelningssvar(rb):
        p=original(rb)
        uppgifter=dict(p.uppgifter)
        uppgifter[falt]=Uppgift()
        return p.model_copy(update={'uppgifter':uppgifter})
    monkeypatch.setattr(kedja,'_profil',utan_fordelningssvar)
    regelrot,rb=kedja.syntetisk_expertkopia(tmp_path/'expert')
    k=kedja.bygg_bunden_kedja(rb,tmp_path/'fall',regelrot=regelrot,godkann=True,formatversion=V8)

    p=k.fall.profil
    assert aktiverad(rb,p,falt)
    assert svarsbrist(rb,p,falt) is None
    assert rb.falt[falt].intag.obligatorisk is False
    assert p.uppgifter[falt].varde is None
    d,fynd=las_granskning(k.granskningsmapp)
    assert not fynd,fynd

    from riskanalys.dokument.lokaldata_v8 import uppgiftsrad
    visning=uppgiftsrad(rb,p,falt).celler[1].text
    assert 'Frivillig fördelning har inte lämnats' in visning
    assert '[VERIFIERA]' not in visning

    paket=faststall(k.fall.byramapp,regelrot,rb,
        Beslut(organ='styrelsen',datum=DAG,namn='Syntetisk',roll='FfR'))
    assert (paket/'allman-riskbedomning-v1.docx').is_file()
    assert (paket/'underlagsbilaga-v1.docx').is_file()
    assert verifiera_version(k.fall.byramapp,1)==[]
    word_rows=[]
    for name in ('allman-riskbedomning-v1.docx','underlagsbilaga-v1.docx'):
        w=docx.Document(paket/name)
        word_rows.extend(' | '.join(c.text for c in row.cells)
            for table in w.tables for row in table.rows
            if any('Frivillig fördelning har inte lämnats' in c.text for c in row.cells))
    assert word_rows and all('[VERIFIERA]' not in row for row in word_rows)


def test_v7_paket_verifieras_utan_levande_modellregister(historisk_v7_kedja,monkeypatch):
    import shutil
    from riskanalys.faststallelse.faststall import faststall,verifiera_version
    from riskanalys.faststallelse.modeller import Beslut
    # Bygg ett uttryckligen historiskt V7-paket; dagens grind tillåter inte ny V7-fastställelse.
    monkeypatch.setattr('riskanalys.faststallelse.faststall.formathinder',lambda *args:[])
    byra,r,rb,gm=historisk_v7_kedja
    paket=faststall(byra,r,rb,Beslut(organ='styrelsen',datum=DAG,namn='Syntetisk',roll='FfR'))
    assert (paket/'analys/snapshot.json').is_file()
    assert len(list((paket/'analys/belagg').glob('*'))) >= 9
    shutil.rmtree(byra/'analys')
    monkeypatch.setattr('riskanalys.drift.modellrisk.modellbindning',lambda *_: 'ny framtida modell')
    assert verifiera_version(byra,1)==[]


@pytest.mark.parametrize('yta',['profil','profil_status','profil_datum','profil_period','profil_namn','svar','scenario','gap','sarbarhet','samverkan','erfarenhet','rutinstatus','uppdrag','betalningsinsyn','leverantor','delning','modellansvarig','nytt_nej','historik','rutinbytes','rapportbytes','modell','regelbas','kalltext','samma_niva_nyttmanifest','utkast'])
def test_andringsmatris_kraver_nytt_godkannande(aktuell_kedja,yta,monkeypatch):
    from riskanalys.faststallelse.faststall import faststall,FaststallelseFel
    from riskanalys.faststallelse.modeller import Beslut
    from riskanalys.analys.lagring import las_analys
    from riskanalys.profil.lagring import las_profil,spara_profil
    from riskanalys.drift.historik import registrera_handelse,Handelse
    import yaml
    byra,r,rb,gm=aktuell_kedja
    a=las_analys(byra)
    if yta.startswith('profil'):
        profil=las_profil(byra)
        falt='P-KUND.antal_aktiva' if yta=='profil_period' else 'P-ORG.namn'
        u=profil.uppgifter[falt]
        andring={'kalla':'Ny syntetisk källa'}
        if yta=='profil_status':andring={'status':'föreslagen'}
        elif yta=='profil_datum':andring={'datum':date(2026,10,14)}
        elif yta=='profil_namn':andring={'varde':'Nytt syntetiskt byrånamn'}
        elif yta=='profil_period':andring={'period':u.period.model_copy(update={'till':date(2026,9,29)})}
        spara_profil(byra,profil.model_copy(update={'uppgifter':{**profil.uppgifter,falt:u.model_copy(update=andring)}}))
    elif yta=='historik':registrera_handelse(byra,Handelse(datum=DAG,typ='uppdatering',beskrivning='Ny uppgift.'))
    elif yta in ('rutinbytes','rapportbytes'):
        ref=a.modellrisk.rutin if yta=='rutinbytes' else a.modellrisk.valideringsrapport
        (byra/'analys/belagg'/ref.fil).write_bytes(b'nya bytes samma filnamn')
    elif yta in ('regelbas','kalltext'):
        fil=r/'version.yaml' if yta=='regelbas' else next((r/'lydelsetexter').glob('*.txt'))
        # Shared immutable fixture source is copied before changing it.
        import shutil
        ny=byra.parent/'andrad-regelbas';shutil.copytree(r,ny)
        fil=ny/fil.relative_to(r);fil.write_text(fil.read_text()+'\nÄndrat syntetiskt underlag.\n');r=ny
    elif yta in ('samma_niva_nyttmanifest','utkast'):
        from riskanalys.granskning.korning import granskningens_metadata
        from riskanalys.lagring.manifest import las_manifest,skriv_manifest
        meta=granskningens_metadata(gm)
        rot=byra/('bedomningar' if yta=='samma_niva_nyttmanifest' else 'utkast')/meta['bedomning' if yta=='samma_niva_nyttmanifest' else 'utkast']
        gammal=las_manifest(rot)
        skriv_manifest(rot,{**gammal.metadata,'ny_revision':'oforandrad_visningsniva'})
    elif yta=='modell':monkeypatch.setattr('riskanalys.drift.modellrisk.modellbindning',lambda *_:'ny modell')
    else:
        data=a.model_dump(mode='json')
        t=data['tjanster'][0]
        if yta=='svar':t['slutsats']='Ett ändrat lokalt svar.'
        elif yta=='scenario':data['gemensamma_scenarier'][0]['motivering']='Nytt förlopp.'
        elif yta=='gap':
            if not t['gap']:
                t['gap'].append({'id':'syntetisk','typ':'kunskapslucka','beskrivning':'Syntetisk öppen lucka.',
                    'status':'oppet','motivering':'Ursprunglig motivering.'})
            t['gap'][0]['motivering']='Nytt gapbeslut.'
        elif yta=='sarbarhet':t['sarbarhetsprovningar'][0]['motivering']='Nytt underlag.'
        elif yta=='samverkan':t['samverkan']='Ändrad faktorprövning.'
        elif yta=='erfarenhet':t['erfarenhetsprovning']='Ny erfarenhetsprövning.'
        elif yta=='rutinstatus':t['rutinatgarder'][0]['atgard']='Ny rutinåtgärd.'
        elif yta=='uppdrag':t['uppdragsprovning']['motivering']='Nytt mandat.'
        elif yta=='betalningsinsyn':t['betalningsinsyn']['insynsluckor']='Nytt osynligt betalningsled.'
        elif yta=='leverantor':t['leverantorsmotivering']='Ändrad lokal leverantörsprövning.'
        elif yta=='delning':t['delningsmotivering']='Nya arbetsmoment.'
        elif yta=='modellansvarig':data['modellrisk']['modellansvarig']='Annan syntetisk ansvarig'
        else:data['beslut'].append({**data['beslut'][0],'godkand':False,'kommentar':'Återkallat.'})
        (byra/'analys/analys.yaml').write_text(yaml.safe_dump(data,allow_unicode=True))
    with pytest.raises(FaststallelseFel):faststall(byra,r,rb,Beslut(organ='styrelsen',datum=DAG,namn='Syntetisk',roll='FfR'))
    assert not (byra/'faststallda/v1').exists()


@pytest.mark.parametrize('yta',['profil','analys','historik'])
def test_andring_mellan_granskning_och_publicering_stoppar_paket(aktuell_kedja,yta,monkeypatch):
    from riskanalys.faststallelse import faststall as f
    from riskanalys.faststallelse.modeller import Beslut
    byra,r,rb,gm=aktuell_kedja
    original=f._bygg_paket
    def bygg(*args,**kwargs):
        original(*args,**kwargs)
        # Simulates a noncooperating file edit after the first checks; normal writers
        # are additionally excluded by the shared locks throughout this interval.
        fil=byra/({'profil':'profil/profil.yaml','analys':'analys/analys.yaml','historik':'drift/historik.yaml'}[yta])
        raw=fil.read_text()
        if yta=='analys':raw=raw.replace('revision: 1','revision: 2')
        elif yta=='profil':raw=raw.replace('Syntetisk testkälla','Ny källa',1)
        else:raw+='\n# ändrade faktiska historikbytes\n'
        fil.write_text(raw)
    monkeypatch.setattr(f,'_bygg_paket',bygg)
    with pytest.raises(f.FaststallelseFel):f.faststall(byra,r,rb,Beslut(organ='styrelsen',datum=DAG,namn='Syntetisk',roll='FfR'))
    assert not (byra/'faststallda/v1').exists()


@pytest.mark.parametrize('yta',['mening','cell','referens'])
def test_v7_aterbyggs_fran_fryst_analys(historisk_v7_kedja,yta):
    from riskanalys.granskning.analysunderlag import las_fryst_analys,fryst_modellrapport
    from riskanalys.granskning.dokument_v6 import analysfynd_v6
    from riskanalys.granskning.korning import las_granskning,granskningens_metadata,godkanda_utkast
    from riskanalys.bedomning.korning import las_bedomning,las_bedomningsprofil
    from riskanalys.drift.historik import las_historik
    byra,r,rb,gm=historisk_v7_kedja
    meta=granskningens_metadata(gm);bm=byra/'bedomningar'/meta['bedomning']
    d,_=las_granskning(gm);snap=las_fryst_analys(gm)
    resultat,_=godkanda_utkast(byra,bm)
    av=list(d.avsnitt);i=next(i for i,a in enumerate(av) if a.id.startswith('D-ARB.6.'))
    a=av[i]
    if yta=='cell':
        tabs=list(a.tabeller);tab=tabs[0];rader=list(tab.rader);rad=rader[0];celler=list(rad.celler)
        celler[0]=celler[0].model_copy(update={'text':'Utbytt cell.'});rader[0]=rad.model_copy(update={'celler':tuple(celler)})
        tabs[0]=tab.model_copy(update={'rader':tuple(rader)});a=a.model_copy(update={'tabeller':tuple(tabs)})
    else:
        stycken=list(a.stycken);s=stycken[-1]
        stycken[-1]=s.model_copy(update={'text':'Utbytt lokal mening.'} if yta=='mening' else {'referenser':['ANALYS:belagg:okant']})
        a=a.model_copy(update={'stycken':tuple(stycken)})
    av[i]=a;d=d.model_copy(update={'avsnitt':tuple(av)})
    fynd=analysfynd_v6(rb,las_bedomning(bm),las_bedomningsprofil(bm),d,las_historik(byra),resultat,analys=snap.paket,modellrapport=fryst_modellrapport(snap))
    assert any(x['allvar']=='blockerande' and x['avsnitt']==a.id for x in fynd)


def test_kopierat_underlag_kontrolleras_efter_hela_bygget(aktuell_kedja,monkeypatch):
    from riskanalys.faststallelse import faststall as f
    from riskanalys.faststallelse.modeller import Beslut
    byra,r,rb,gm=aktuell_kedja
    original=f._bygg_paket
    def bygg(pagaende,*args,**kwargs):
        original(pagaende,*args,**kwargs)
        (pagaende/'granskning/analys/belagg'/next((pagaende/'granskning/analys/belagg').iterdir()).name).write_bytes(b'utbytt efter kopiering')
    monkeypatch.setattr(f,'_bygg_paket',bygg)
    with pytest.raises(f.FaststallelseFel):f.faststall(byra,r,rb,Beslut(organ='styrelsen',datum=DAG,namn='Syntetisk',roll='FfR'))
    assert not (byra/'faststallda/v1').exists()


@pytest.mark.parametrize('skrivare',['profil','analys','drift'])
def test_normala_skrivare_vantar_tills_publiceringen_ar_klar(aktuell_kedja,monkeypatch,skrivare):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from riskanalys.faststallelse import faststall as f
    from riskanalys.faststallelse.modeller import Beslut
    from riskanalys.profil.lagring import las_profil,spara_profil
    from riskanalys.analys.lagring import las_analys,spara_analys
    from riskanalys.analys.provning import registersumma
    from riskanalys.drift.historik import registrera_handelse,Handelse
    byra,r,rb,gm=aktuell_kedja
    start,klar=Event(),Event()
    def skriv():
        start.set()
        if skrivare=='profil':spara_profil(byra,las_profil(byra))
        elif skrivare=='analys':
            a=las_analys(byra);spara_analys(byra,a,forvantad_summa=registersumma(a))
        else:registrera_handelse(byra,Handelse(datum=DAG,typ='uppdatering',beskrivning='Efter publicering.'))
        klar.set()
    original=f._publicera
    with ThreadPoolExecutor(max_workers=1) as pool:
        framtid=[]
        def publicera(pagaende,slutlig):
            framtid.append(pool.submit(skriv))
            assert start.wait(2)
            assert not klar.wait(.15), 'Skrivaren passerade publiceringslåset.'
            return original(pagaende,slutlig)
        monkeypatch.setattr(f,'_publicera',publicera)
        paket=f.faststall(byra,r,rb,Beslut(organ='styrelsen',datum=DAG,namn='Syntetisk',roll='FfR'))
        framtid[0].result(timeout=3)
    assert paket.is_dir() and klar.is_set()


def test_kopians_manifest_maste_motsvara_granskad_bindning(aktuell_kedja,monkeypatch):
    from riskanalys.faststallelse import faststall as f
    from riskanalys.faststallelse.modeller import Beslut
    from riskanalys.lagring.manifest import las_manifest,skriv_manifest
    byra,r,rb,gm=aktuell_kedja
    original=f._bygg_paket
    def bygg(pagaende,*args,**kwargs):
        original(pagaende,*args,**kwargs)
        fil=pagaende/'bedomning/bedomning.json'
        fil.write_text(fil.read_text().replace('2026-10-15','2026-10-14'))
        # A newly self-consistent copied manifest cannot replace the frozen source identity.
        skriv_manifest(fil.parent,las_manifest(fil.parent).metadata)
    monkeypatch.setattr(f,'_bygg_paket',bygg)
    with pytest.raises(f.FaststallelseFel):f.faststall(byra,r,rb,Beslut(organ='styrelsen',datum=DAG,namn='Syntetisk',roll='FfR'))
    assert not (byra/'faststallda/v1').exists()


def test_sakgranskning_kraver_aktuell_fryst_bindning_i_cli(aktuell_kedja,monkeypatch,capsys):
    from riskanalys.cli import main
    from riskanalys.faststallelse.sakgranskning import las_sakgranskningar
    from riskanalys.analys.lagring import las_analys,spara_analys
    from riskanalys.analys.provning import registersumma
    byra,r,rb,gm=aktuell_kedja
    monkeypatch.setenv('RISKANALYS_DATA',str(byra.parent))
    args=['sakgranska','byra','--avsnitt','D-ARB.6.1','--godkann','--namn','Syntetisk CLI','--datum',str(DAG),'--regelbas',str(r)]
    assert main(args)==0
    post=las_sakgranskningar(byra)[-1]
    a=las_analys(byra)
    assert post.analysbindning==registersumma(a)
    nytt=a.model_copy(update={'tjanster':(a.tjanster[0].model_copy(update={'slutsats':'Ny slutsats.'}),*a.tjanster[1:])})
    spara_analys(byra,nytt,forvantad_summa=registersumma(a))
    fore=las_sakgranskningar(byra)
    assert main(args)==1
    assert las_sakgranskningar(byra)==fore
    assert 'ändrats' in capsys.readouterr().err


def test_reduktionskonflikt_kan_inte_accepteras_bort(aktuell_kedja):
    from riskanalys.analys.lagring import las_analys
    from riskanalys.analys.modeller import Analysgap
    from riskanalys.granskning.dokument_v6 import analyshinder
    from riskanalys.bedomning.korning import las_bedomning,las_bedomningsprofil
    from riskanalys.granskning.korning import granskningens_bedomningsmapp
    byra,r,rb,gm=aktuell_kedja;a=las_analys(byra)
    t=a.tjanster[0].model_copy(update={'reduktionsprovning':'metodkonflikt','gap':(Analysgap(id='konflikt',typ='kontrollbrist',status='accepterad_kvarstaende_risk',beskrivning='Otillräcklig täckning.',motivering='Accepterad risk.',ansvar='Syntetisk',tidsfrist=date(2026,11,15)),)})
    a=a.model_copy(update={'tjanster':(t,*a.tjanster[1:])})
    bm=granskningens_bedomningsmapp(byra,gm)
    assert any('metodkonflikt' in x.lower() for x in analyshinder(rb,las_bedomningsprofil(bm),las_bedomning(bm),a))


def test_snapshot_bevarar_nastlade_felbelagg(aktuell_kedja,tmp_path):
    from riskanalys.analys.lagring import las_analys,analyslas,las_analyssnapshot_last,importera_belagg
    from riskanalys.analys.provning import registersumma
    from riskanalys.drift.modellrisk import Modellfel,Modellbelagg
    from riskanalys.granskning.analysunderlag import spara_fryst_analys,las_fryst_analys
    from riskanalys.granskning.korning import granskningens_metadata
    import yaml
    byra,r,rb,gm=aktuell_kedja
    fil=tmp_path/'fel.txt';fil.write_text('PRIVAT-SYNTETISK-FELAKT')
    namn,hash=importera_belagg(byra,fil);a=las_analys(byra)
    fel=Modellfel(id='syn-fel',datum=DAG,beskrivning='Privat syntetisk felakt.',allvar='ovrigt',status='atgardat',
        atgard_och_omprovning='Utrett syntetiskt.',belagg=(Modellbelagg(fil=namn,kontrollsumma=hash),))
    a=a.model_copy(update={'modellrisk':a.modellrisk.model_copy(update={'fel':(fel,)})})
    (byra/'analys/analys.yaml').write_text(yaml.safe_dump(a.model_dump(mode='json'),allow_unicode=True))
    meta=granskningens_metadata(gm)
    with analyslas(byra):snap=las_analyssnapshot_last(byra,rb,DAG,bedomningsmapp=byra/'bedomningar'/meta['bedomning'],utkastmapp=byra/'utkast'/meta['utkast'])
    assert (namn,fil.read_bytes()) in snap.filer
    target=tmp_path/'fryst';spara_fryst_analys(target,snap)
    assert dict(las_fryst_analys(target).filer)[namn]==b'PRIVAT-SYNTETISK-FELAKT'


def test_sista_paketmanifestet_kontrolleras_fore_publicering(aktuell_kedja,monkeypatch):
    from riskanalys.faststallelse import faststall as f
    from riskanalys.faststallelse.modeller import Beslut
    byra,r,rb,gm=aktuell_kedja
    original=f.skriv_manifest
    def skriv(mapp,metadata):
        resultat=original(mapp,metadata)
        (mapp/'beslut.yaml').write_text('utbytt efter manifestskrivning')
        return resultat
    monkeypatch.setattr(f,'skriv_manifest',skriv)
    with pytest.raises(f.FaststallelseFel):f.faststall(byra,r,rb,Beslut(organ='styrelsen',datum=DAG,namn='Syntetisk',roll='FfR'))
    assert not (byra/'faststallda/v1').exists()


def test_granskningsmanifest_far_inte_bytas_under_paketeringen(aktuell_kedja,monkeypatch):
    from riskanalys.faststallelse import faststall as f
    from riskanalys.faststallelse.modeller import Beslut
    from riskanalys.lagring.manifest import las_manifest,skriv_manifest
    byra,r,rb,gm=aktuell_kedja
    original=f._bygg_paket
    def bygg(pagaende,*args,**kwargs):
        # Replace live review with a self-consistent manifest after the underlag was read.
        data=json.loads((gm/'dokument.json').read_text())
        data['titel']='Utbytt dokument under paketering'
        (gm/'dokument.json').write_text(json.dumps(data,ensure_ascii=False))
        skriv_manifest(gm,las_manifest(gm).metadata)
        original(pagaende,*args,**kwargs)
    monkeypatch.setattr(f,'_bygg_paket',bygg)
    with pytest.raises(f.FaststallelseFel):f.faststall(byra,r,rb,Beslut(organ='styrelsen',datum=DAG,namn='Syntetisk',roll='FfR'))
    assert not (byra/'faststallda/v1').exists()


def _nytt_lokalt_beslut(aktuell_kedja,datum,*,godkand=True):
    from riskanalys.analys import lagring as l,provning as p,modeller as m
    from riskanalys.granskning.korning import granskningens_metadata
    byra,r,rb,gm=aktuell_kedja;meta=granskningens_metadata(gm);a=l.las_analys(byra)
    beslut=m.Analysbeslut(tjanst=a.tjanster[0].tjanst,revision=a.revision,underlagssumma=p.underlagssumma(a),
        svarssumma=p.svarssumma(a),godkand=godkand,namn='Syntetisk datumgranskare',roll='FfR',datum=datum,
        kommentar=None if godkand else 'Korrigerat till underkännande.')
    return l.registrera_analysbeslut(byra,rb,beslut,forvantad_summa=p.registersumma(a),
        bedomningsmapp=byra/'bedomningar'/meta['bedomning'],utkastmapp=byra/'utkast'/meta['utkast'])


def _sakgodkann_fryst(byra,gm,datum,rb):
    from riskanalys.granskning.korning import las_granskning,granskningens_profil,granskningens_bedomningsmapp
    from riskanalys.bedomning.korning import las_bedomning
    from riskanalys.dokument.rapportpaket_v8 import las_presentation
    from riskanalys.granskning.analysunderlag import las_fryst_analys
    from riskanalys.faststallelse.sakgranskning import spara_sakgranskningar
    d,_=las_granskning(gm);profil=granskningens_profil(byra,gm);cas=las_fryst_analys(gm).registersumma
    bm=granskningens_bedomningsmapp(byra,gm)
    presentation=las_presentation(gm,las_bedomning(bm),profil,regelbas=rb) if d.formatversion=='D-ARB-tjanst-v8' else None
    sak=()
    for av in d.avsnitt:
        sak=registrera_sakgranskning(sak,d,profil,av.id,True,'FfR','Syntetisk dokumentgranskare',datum,analysbindning=cas,presentation=presentation)
    spara_sakgranskningar(byra,sak)


def test_granskning_fore_senaste_lokala_godkannande_blir_blockerande(aktuell_kedja):
    from datetime import timedelta
    from riskanalys.granskning.korning import kor_granskning,las_granskning
    byra,r,rb,_=aktuell_kedja
    _nytt_lokalt_beslut(aktuell_kedja,DAG+timedelta(days=1))
    gm=kor_granskning(byra,rb,DAG)
    _,fynd=las_granskning(gm)
    assert any(x.allvar=='blockerande' and '2026-10-16' in x.beskrivning and 'lokala' in x.beskrivning for x in fynd)


def test_dokumentgodkannande_fore_lokal_attest_avvisas_i_cli(aktuell_kedja,monkeypatch,capsys):
    from datetime import timedelta
    from riskanalys.cli import main
    from riskanalys.granskning.korning import kor_granskning
    from riskanalys.faststallelse.sakgranskning import las_sakgranskningar
    byra,r,rb,_=aktuell_kedja
    _nytt_lokalt_beslut(aktuell_kedja,DAG+timedelta(days=1))
    kor_granskning(byra,rb,DAG+timedelta(days=1))
    monkeypatch.setenv('RISKANALYS_DATA',str(byra.parent));fore=las_sakgranskningar(byra)
    assert main(['sakgranska','byra','--avsnitt','D-ARB.6.1','--godkann','--namn','Syntetisk',
        '--datum',str(DAG),'--regelbas',str(r)])==1
    assert las_sakgranskningar(byra)==fore
    assert '2026-10-16' in capsys.readouterr().err


def test_faststallelse_fore_lokal_attest_skapar_inget_paket(aktuell_kedja):
    from datetime import timedelta
    from riskanalys.granskning.korning import kor_granskning
    from riskanalys.faststallelse.faststall import faststall,FaststallelseFel
    from riskanalys.faststallelse.modeller import Beslut
    byra,r,rb,_=aktuell_kedja
    _nytt_lokalt_beslut(aktuell_kedja,DAG+timedelta(days=1))
    gm=kor_granskning(byra,rb,DAG)
    _sakgodkann_fryst(byra,gm,DAG,rb)
    with pytest.raises(FaststallelseFel,match='2026-10-16'):
        faststall(byra,r,rb,Beslut(organ='styrelsen',datum=DAG,namn='Syntetisk',roll='FfR'))
    assert not (byra/'faststallda/v1').exists()


def test_rena_kronologigrinden_omfattar_lokala_attester(aktuell_kedja):
    from datetime import timedelta
    from riskanalys.granskning.korning import kor_granskning
    from riskanalys.faststallelse.faststall import _underlag
    from riskanalys.faststallelse.grindar import _kronologi
    byra,r,rb,_=aktuell_kedja
    _nytt_lokalt_beslut(aktuell_kedja,DAG+timedelta(days=1))
    gm=kor_granskning(byra,rb,DAG)
    hinder=_kronologi(_underlag(byra,rb,gm),DAG)
    assert any('2026-10-16' in x and 'lokala' in x for x in hinder)


@pytest.mark.parametrize('dagar',[1,2])
def test_lokal_attest_efter_bedomning_tillats_vid_samma_eller_senare_granskning(aktuell_kedja,dagar,monkeypatch):
    from datetime import timedelta
    from riskanalys.granskning.korning import kor_granskning,las_granskning
    from riskanalys.faststallelse.faststall import faststall,verifiera_version
    from riskanalys.faststallelse.modeller import Beslut
    byra,r,rb,_=aktuell_kedja;datum=DAG+timedelta(days=dagar)
    _nytt_lokalt_beslut(aktuell_kedja,DAG+timedelta(days=1))
    gm=kor_granskning(byra,rb,datum)
    assert las_granskning(gm)[1]==()
    _sakgodkann_fryst(byra,gm,datum,rb)
    from riskanalys.cli import main
    monkeypatch.setenv('RISKANALYS_DATA',str(byra.parent))
    assert main(['sakgranska','byra','--avsnitt','D-ARB.6.1','--godkann','--namn','Syntetisk CLI',
        '--datum',str(datum),'--regelbas',str(r)])==0
    assert faststall(byra,r,rb,Beslut(organ='styrelsen',datum=datum,namn='Syntetisk',roll='FfR')).is_dir()
    assert verifiera_version(byra,1)==[]


def test_korrigerat_senaste_datum_ersatter_aldre_framtida_ja(aktuell_kedja):
    from datetime import timedelta
    from riskanalys.granskning.korning import kor_granskning,las_granskning
    from riskanalys.faststallelse.faststall import faststall
    from riskanalys.faststallelse.modeller import Beslut
    byra,r,rb,_=aktuell_kedja
    _nytt_lokalt_beslut(aktuell_kedja,DAG+timedelta(days=1))
    _nytt_lokalt_beslut(aktuell_kedja,DAG)
    gm=kor_granskning(byra,rb,DAG)
    assert las_granskning(gm)[1]==()
    _sakgodkann_fryst(byra,gm,DAG,rb)
    assert faststall(byra,r,rb,Beslut(organ='styrelsen',datum=DAG,namn='Syntetisk',roll='FfR')).is_dir()


def test_senaste_nej_ersatts_inte_av_aldre_ja_for_att_klara_datum(aktuell_kedja):
    from datetime import timedelta
    from riskanalys.granskning.korning import kor_granskning,las_granskning
    byra,r,rb,_=aktuell_kedja
    _nytt_lokalt_beslut(aktuell_kedja,DAG+timedelta(days=1))
    _nytt_lokalt_beslut(aktuell_kedja,DAG,godkand=False)
    gm=kor_granskning(byra,rb,DAG);_,fynd=las_granskning(gm)
    assert any('aktuellt lokalt godkännande saknas' in x.beskrivning for x in fynd)
    assert not any('är före det lokala analysgodkännandet' in x.beskrivning for x in fynd)


# Kronologi genom den gemensamma låsta beslutsvägen (CLI/webb): Analystjanst.beslut.
FRAMTID = date(2099, 1, 1)


def _spara_uppdragsandring(byra, uppdrag=None, rutin=None):
    """Ändra första tjänstens svar via ordinarie lagring och bekräfta blocken på nytt."""
    from riskanalys.analys import lagring as l, provning as p
    from tester.fixturer.analys_hela_kedjan import _bekrafta
    a = l.las_analys(byra)
    t = a.tjanster[0]
    andring = {'uppdragsprovning': t.uppdragsprovning.model_copy(update=uppdrag or {})}
    if rutin:
        andring['rutinatgarder'] = tuple(r.model_copy(update=rutin) for r in t.rutinatgarder)
    ny = _bekrafta(a.model_copy(update={'tjanster': (t.model_copy(update=andring), *a.tjanster[1:])}))
    return t.tjanst, l.spara_analys(byra, ny, forvantad_summa=p.registersumma(a))


def _uppdragsbeslut(status, datum):
    return {'status': status, 'handlingsalternativ': 'begransa', 'beslutsstatus': 'beslutad',
            'ansvar': 'Syntetisk Ada', 'datum': datum}


@pytest.mark.parametrize('status', ['kraver_atgard', 'kan_inte_hanteras'])
def test_framtida_uppdragsbeslut_stoppas_i_last_beslutsvag(aktuell_kedja, status):
    from riskanalys.analys import lagring as l, provning as p
    from riskanalys.analys.tjanst import Analystjanst
    from riskanalys.fel import RiskanalysFel
    byra, r, rb, gm = aktuell_kedja
    tjanst, cas = _spara_uppdragsandring(byra, _uppdragsbeslut(status, FRAMTID))
    with pytest.raises(RiskanalysFel, match='uppdragsbeslutet har datum 2099-01-01'):
        Analystjanst(byra, rb).beslut(tjanst, True, 'Syntetisk datumgranskare', 'FfR', DAG, '', cas)
    efter = l.las_analys(byra)
    assert p.registersumma(efter) == cas
    assert p.gallande_beslut(efter, tjanst) is None


def test_uppdragsbeslut_samma_dag_godtas_i_last_beslutsvag(aktuell_kedja):
    from riskanalys.analys import lagring as l, provning as p
    from riskanalys.analys.tjanst import Analystjanst
    byra, r, rb, gm = aktuell_kedja
    tjanst, cas = _spara_uppdragsandring(byra, _uppdragsbeslut('kraver_atgard', DAG))
    ny = Analystjanst(byra, rb).beslut(tjanst, True, 'Syntetisk datumgranskare', 'FfR', DAG, '', cas)
    efter = l.las_analys(byra)
    assert ny == p.registersumma(efter)
    assert p.gallande_beslut(efter, tjanst).godkand


def test_framtida_uppfoljning_godtas_i_last_beslutsvag(aktuell_kedja):
    from riskanalys.analys import lagring as l, provning as p
    from riskanalys.analys.tjanst import Analystjanst
    byra, r, rb, gm = aktuell_kedja
    tjanst, cas = _spara_uppdragsandring(byra, _uppdragsbeslut('kraver_atgard', DAG),
        rutin={'status': 'beslutad', 'uppfoljning': FRAMTID,
              'klart_nar': 'Rutinen är uppdaterad och kommunicerad.', 'prioritet': 'medel'})
    a = l.las_analys(byra)
    assert any(r.uppfoljning == FRAMTID for r in a.tjanster[0].rutinatgarder)
    Analystjanst(byra, rb).beslut(tjanst, True, 'Syntetisk datumgranskare', 'FfR', DAG, '', cas)
    assert p.gallande_beslut(l.las_analys(byra), tjanst).godkand


def test_framtida_frist_pa_giltigt_hanterat_gap_godtas_i_last_beslutsvag(aktuell_kedja):
    from riskanalys.analys import lagring as l, provning as p, modeller as m
    from riskanalys.analys.tjanst import Analystjanst
    from riskanalys.bedomning.korning import las_bedomning, las_bedomningsprofil
    from tester.fixturer.analys_hela_kedjan import _bekrafta
    from riskanalys.granskning.korning import granskningens_bedomningsmapp

    byra, r, rb, gm = aktuell_kedja
    a = l.las_analys(byra)
    t = a.tjanster[0]
    gap = m.Analysgap(id='syntetisk-framtida-frist', typ='kontrollbrist',
        status='accepterad_kvarstaende_risk',
        beskrivning='Avgränsad kontrollbrist är dokumenterad.',
        motivering='Kvarstående risk har ansvarig och fastställd frist.',
        ansvar='Syntetisk metodansvarig', tidsfrist=FRAMTID)
    ny = _bekrafta(a.model_copy(update={'tjanster': (
        t.model_copy(update={'gap': (gap,)}), *a.tjanster[1:])}))
    cas = l.spara_analys(byra, ny, forvantad_summa=p.registersumma(a))

    beslut = Analystjanst(byra, rb).beslut(t.tjanst, True,
        'Syntetisk datumgranskare', 'FfR', DAG, '', cas)
    efter = l.las_analys(byra)
    assert beslut == p.registersumma(efter)
    assert p.gallande_beslut(efter, t.tjanst).godkand
    bedomningsmapp = granskningens_bedomningsmapp(byra, gm)
    profil = las_bedomningsprofil(bedomningsmapp)
    bedomning = las_bedomning(bedomningsmapp)
    assert p.analysbrister(rb, profil, bedomning, efter) == ()


def test_lagrat_godkannande_med_framtida_uppdragsbeslut_stoppar_dokumentet(aktuell_kedja):
    """Ett register sparat före regeln får inte bli underlag för dokument eller fastställelse."""
    import yaml
    from riskanalys.analys import lagring as l, modeller as m, provning as p
    from riskanalys.faststallelse.faststall import faststall, FaststallelseFel
    from riskanalys.faststallelse.modeller import Beslut
    from riskanalys.granskning.korning import kor_granskning, las_granskning
    from tester.fixturer.analys_hela_kedjan import _bekrafta
    byra, r, rb, gm = aktuell_kedja
    a = l.las_analys(byra)
    t = a.tjanster[0]
    u = t.uppdragsprovning.model_copy(update=_uppdragsbeslut('kraver_atgard', FRAMTID))
    ny = _bekrafta(a.model_copy(update={'revision': a.revision + 1,
        'tjanster': (t.model_copy(update={'uppdragsprovning': u}), *a.tjanster[1:])}))
    beslut = tuple(m.Analysbeslut(tjanst=x.tjanst, revision=ny.revision, underlagssumma=p.underlagssumma(ny),
        svarssumma=p.svarssumma(ny), godkand=True, namn='Syntetisk granskare', roll='FfR', datum=DAG,
        forfattare=x.forfattare) for x in ny.tjanster)
    ny = ny.model_copy(update={'beslut': (*a.beslut, *beslut)})
    (byra / 'analys/analys.yaml').write_text(yaml.safe_dump(ny.model_dump(mode='json'), allow_unicode=True))
    assert p.gallande_beslut(l.las_analys(byra), t.tjanst).godkand
    _, fynd = las_granskning(kor_granskning(byra, rb, DAG))
    assert any('uppdragsbeslutet har datum 2099-01-01' in x.beskrivning and x.allvar == 'blockerande' for x in fynd)
    with pytest.raises(FaststallelseFel, match='uppdragsbeslutet har datum 2099-01-01'):
        faststall(byra, r, rb, Beslut(organ='styrelsen', datum=DAG, namn='Syntetisk', roll='FfR'))
    assert not (byra / 'faststallda/v1').exists()
