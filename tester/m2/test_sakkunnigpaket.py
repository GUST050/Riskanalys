from datetime import date
from pathlib import Path
import shutil
import yaml
import pytest
from riskanalys.fel import RiskanalysFel
from riskanalys.regelverk.laddning import STANDARD_REGELBAS,ladda_regelbas
from riskanalys.regelverk.sakkunnig import exportera_sakkunnigunderlag,las_granskningsfil,tillampa_granskning

@pytest.fixture
def kopia(tmp_path):
 r=tmp_path/'regelbas';shutil.copytree(STANDARD_REGELBAS,r);return r

def beslut(rot,out):
 exportera_sakkunnigunderlag(rot,'RP-RED-VG',date(2026,10,10),out)
 fil=out/'granskningsmall.yaml';d=yaml.safe_load(fil.read_text());d.update(granskare='Syntetisk testgranskare',kompetens='Syntetisk PTL/FS-metodkompetens',oberoende=True)
 for x in d['objekt'].values():x.update(beslut='verifierad',kommentar='Syntetiskt prov, aldrig verklig frigivning')
 fil.write_text(yaml.safe_dump(d,allow_unicode=True));return fil

def test_import_ar_syntetisk_transaktion_och_hash_stabil(kopia,tmp_path):
 fil=beslut(kopia,tmp_path/'ut');rb=ladda_regelbas(kopia);summa=rb.paketets_innehallssumma('RP-RED-VG')
 b=las_granskningsfil(fil,rb,'RP-RED-VG');tillampa_granskning(kopia,b)
 nytt=ladda_regelbas(kopia)
 assert nytt.paketets_innehallssumma('RP-RED-VG')==summa
 assert nytt.regelpaket['RP-RED-VG'].granskning.galler(summa)
 assert not ladda_regelbas().regelpaket['RP-RED-VG'].granskning.galler(summa)
 assert (tmp_path/'ut/manifest.json').exists()

@pytest.mark.parametrize('rel',['falt.yaml','kallor.yaml','kataloger/tjanster.yaml','beslutstabeller/metod.yaml','beslutstabeller/kundmodell/a-stopp.yaml','regelpaket/redovisning-vg.yaml','lydelsetexter/LYD-PTL-4-3-2017-08-01.txt'])
def test_andrat_underlag_avvisas(kopia,tmp_path,rel):
 fil=beslut(kopia,tmp_path/'ut');p=kopia/rel
 if p.suffix=='.txt':
  p.write_text(p.read_text()+' Ändrad text')
  with pytest.raises(RiskanalysFel):ladda_regelbas(kopia)
 else:
  d=yaml.safe_load(p.read_text());obj=d[0] if isinstance(d,list) else (d['sannolikhet'] if rel=='beslutstabeller/metod.yaml' else d)
  key=next(k for k,v in obj.items() if isinstance(v,str) and k not in {'id','grund','typ'})
  obj[key]+=' ändrad';p.write_text(yaml.safe_dump(d,allow_unicode=True))
  with pytest.raises(RiskanalysFel):las_granskningsfil(fil,ladda_regelbas(kopia),'RP-RED-VG')
 assert not (kopia/'granskning.yaml').exists()

@pytest.mark.parametrize('fel',['namn','kompetens','oberoende','saknad','extra'])
def test_ofullstandig_granskning_avvisas(kopia,tmp_path,fel):
 fil=beslut(kopia,tmp_path/'ut');d=yaml.safe_load(fil.read_text())
 if fel=='namn':d['granskare']=' '
 elif fel=='kompetens':d['kompetens']=' '
 elif fel=='oberoende':d['oberoende']=False
 elif fel=='saknad':d['objekt'].pop(next(iter(d['objekt'])))
 else:d['objekt']['PÅHITTAD']={'beslut':'verifierad','kommentar':'x'}
 fil.write_text(yaml.safe_dump(d,allow_unicode=True))
 with pytest.raises(RiskanalysFel):las_granskningsfil(fil,ladda_regelbas(kopia),'RP-RED-VG')

def test_andras_frigor_inget_paket(kopia,tmp_path):
 fil=beslut(kopia,tmp_path/'ut');d=yaml.safe_load(fil.read_text());next(iter(d['objekt'].values()))['beslut']='ändras';fil.write_text(yaml.safe_dump(d,allow_unicode=True))
 tillampa_granskning(kopia,las_granskningsfil(fil,ladda_regelbas(kopia),'RP-RED-VG'))
 assert ladda_regelbas(kopia).regelpaket['RP-RED-VG'].granskning.status=='ändras'

@pytest.mark.parametrize('key,value',[('kompetens',''),('oberoende',False),('granskningsdatum','2026-10-01'),('granskare',' ')])
def test_handredigerad_importerad_attest_far_inte_kringga_importen(kopia,tmp_path,key,value):
 fil=beslut(kopia,tmp_path/'ut');b=las_granskningsfil(fil,ladda_regelbas(kopia),'RP-RED-VG');tillampa_granskning(kopia,b)
 p=kopia/'granskning.yaml';d=yaml.safe_load(p.read_text());data=d['beslut']['RP-RED-VG'] if 'beslut' in d else d;data[key]=value;p.write_text(yaml.safe_dump(d,allow_unicode=True))
 with pytest.raises(RiskanalysFel):ladda_regelbas(kopia)

def test_granskning_av_ytterligare_paket_bevarar_tidigare_attest(kopia,tmp_path):
 fil=beslut(kopia,tmp_path/'ut');b=las_granskningsfil(fil,ladda_regelbas(kopia),'RP-RED-VG');tillampa_granskning(kopia,b)
 exportera_sakkunnigunderlag(kopia,'RP-RED-SKANE',date(2026,10,10),tmp_path/'ut2')
 p=tmp_path/'ut2/granskningsmall.yaml';d=yaml.safe_load(p.read_text());d.update(granskare='Syntetisk andra granskare',kompetens='Syntetisk testkompetens',oberoende=True)
 for x in d['objekt'].values():x.update(beslut='verifierad',kommentar='Syntetiskt prov')
 p.write_text(yaml.safe_dump(d,allow_unicode=True));tillampa_granskning(kopia,las_granskningsfil(p,ladda_regelbas(kopia),'RP-RED-SKANE'))
 rb=ladda_regelbas(kopia)
 for id in ['RP-RED-VG','RP-RED-SKANE']:assert rb.regelpaket[id].granskning.galler(rb.paketets_innehallssumma(id))


@pytest.mark.parametrize('ordning',[('RP-RED-VG','RP-RED-SKANE'),('RP-RED-SKANE','RP-RED-VG')])
def test_inaktuell_annans_paketattest_far_inte_forstora_giltig_attest(regelbas_v1,ordning):
 from riskanalys.regelverk.sakkunnig import Granskningsbeslut,Objektbeslut,granskningsobjekt,applicera_attester
 from riskanalys.regelverk.validering_m2 import attesthinder
 rb=regelbas_v1
 beslut={id:Granskningsbeslut(paket=id,version=rb.version,datum=date(2026,10,10),granskningsdatum=date(2026,10,10),kontrollsumma=rb.paketets_innehallssumma(id),granskare='Test',kompetens='Syntetisk sakkunnig',oberoende=True,objekt={k:Objektbeslut(beslut='verifierad',kommentar='Syntetiskt godkännande') for k in granskningsobjekt(rb,id)}) for id in ordning}
 sk=rb.regelpaket['RP-RED-SKANE'].model_copy(update={'namn':'Ändrat paketnamn'})
 rb=rb.model_copy(update={'regelpaket':{**rb.regelpaket,sk.id:sk}})
 for id in ordning:rb=applicera_attester(rb,beslut[id])
 assert rb.regelpaket['RP-RED-VG'].granskning.galler(rb.paketets_innehallssumma('RP-RED-VG'))
 assert not attesthinder(rb,'RP-RED-VG')
 assert not rb.regelpaket[sk.id].granskning.galler(rb.paketets_innehallssumma(sk.id))
 assert rb.regelpaket[sk.id].granskning.status=='ändras'


@pytest.mark.parametrize('avvisar', ['RP-RED-SKANE', 'RP-RED-VG'])
@pytest.mark.parametrize('ordning', [('RP-RED-VG', 'RP-RED-SKANE'), ('RP-RED-SKANE', 'RP-RED-VG')])
def test_motstridiga_aktuella_beslut_stoppar_bada_paketen(regelbas_v1, avvisar, ordning):
    from riskanalys.regelverk.sakkunnig import Granskningsbeslut, Objektbeslut, granskningsobjekt, applicera_attester
    from riskanalys.regelverk.validering_m2 import attesthinder
    rb = regelbas_v1
    gemensamt = next(iter(rb.hot))
    beslut = {
        id: Granskningsbeslut(
            paket=id, version=rb.version, datum=date(2026, 10, 10), granskningsdatum=date(2026, 10, 10),
            kontrollsumma=rb.paketets_innehallssumma(id), granskare='Syntetisk granskare',
            kompetens='Syntetisk sakkunnig', oberoende=True,
            objekt={k: Objektbeslut(beslut='ändras' if id == avvisar and k == gemensamt else 'verifierad',
                                   kommentar='Syntetiskt prov') for k in granskningsobjekt(rb, id)},
        ) for id in ordning
    }
    for id in ordning:
        rb = applicera_attester(rb, beslut[id])
    for id in ordning:
        assert any(gemensamt in hinder for hinder in attesthinder(rb, id))
    assert rb.hot[gemensamt].sakkunnig.status == 'ändras'


def test_lokal_konflikt_loses_genom_ersatta_beslut_och_farsk_inlasning(kopia, regelbas_v1):
    from riskanalys.regelverk.sakkunnig import Granskningsbeslut, Objektbeslut, granskningsobjekt
    from riskanalys.regelverk.validering_m2 import attesthinder
    rb = regelbas_v1
    gemensamt = next(iter(rb.hot))
    beslut = {
        id: Granskningsbeslut(
            paket=id, version=rb.version, datum=date(2026, 10, 10), granskningsdatum=date(2026, 10, 10),
            kontrollsumma=rb.paketets_innehallssumma(id), granskare='Syntetisk granskare',
            kompetens='Syntetisk testkompetens', oberoende=True,
            objekt={k: Objektbeslut(beslut='ändras' if id == 'RP-RED-SKANE' and k == gemensamt else 'verifierad',
                                   kommentar='Syntetiskt prov') for k in granskningsobjekt(rb, id)},
        ) for id in ('RP-RED-SKANE', 'RP-RED-VG')
    }
    fil = kopia/'granskning.yaml'
    fil.write_text(yaml.safe_dump({'beslut':{id:b.model_dump(mode='python') for id,b in beslut.items()}},allow_unicode=True))
    rb = ladda_regelbas(kopia)
    assert all(any(gemensamt in h for h in attesthinder(rb, id)) for id in beslut)
    b = beslut['RP-RED-SKANE']
    b = b.model_copy(update={'objekt':{**b.objekt,gemensamt:Objektbeslut(beslut='verifierad',kommentar='Syntetisk samordning')}})
    tillampa_granskning(kopia, b)
    rb = ladda_regelbas(kopia)
    assert all(not attesthinder(rb, id) for id in beslut)


@pytest.mark.parametrize('avvisar', ['RP-RED-SKANE', 'RP-RED-VG'])
@pytest.mark.parametrize('ordning', [('RP-RED-VG', 'RP-RED-SKANE'), ('RP-RED-SKANE', 'RP-RED-VG')])
def test_konflikt_om_inaktivt_gemensamt_krav_stoppar_bada_paketen(regelbas_v1, avvisar, ordning):
    from types import SimpleNamespace
    from riskanalys.bedomning.motor import bedom
    from riskanalys.faststallelse.grindar import _m2
    from riskanalys.profil.hantering import skapa_profil
    from riskanalys.profil.modeller import Byra
    from riskanalys.regelverk.sakkunnig import Granskningsbeslut, Objektbeslut, granskningsobjekt, applicera_attester
    from riskanalys.regelverk.urval import valj, kravet_galler
    from riskanalys.regelverk.validering_m2 import attesthinder
    from tester.fixturer.m2 import komplett_profil

    rb = regelbas_v1
    dag = date(2026, 10, 10)
    krav = 'KRV-PTL-2-9'
    beslut = {
        id: Granskningsbeslut(
            paket=id, version=rb.version, datum=dag, granskningsdatum=dag,
            kontrollsumma=rb.paketets_innehallssumma(id), granskare='Syntetisk granskare',
            kompetens='Syntetisk testkompetens', oberoende=True,
            objekt={k: Objektbeslut(beslut='ändras' if id == avvisar and k == krav else 'verifierad',
                                   kommentar='Syntetiskt prov') for k in granskningsobjekt(rb, id)},
        ) for id in ordning
    }
    for id in ordning:
        rb = applicera_attester(rb, beslut[id])
    for id, lan in [('RP-RED-VG', 'Västra Götaland'), ('RP-RED-SKANE', 'Skåne')]:
        p = komplett_profil(rb, skapa_profil(rb, Byra(id='syntetisk', regelpaket=id, datum=dag, lan=lan)))
        assert p.uppgifter['P-ORG.koncernmoder'].varde is False
        assert not kravet_galler(rb, rb.krav[krav], p.faltvarden())
        assert any(krav in h for h in attesthinder(rb, id))
        urval = valj(rb, id, dag, lan)
        u = SimpleNamespace(regelbas=rb, profil=p, urval=urval, bedomning=bedom(rb, urval, p))
        assert any(krav in h for h in _m2(u, dag))


def test_rackvidd_exporteras_och_importeras_med_egen_attest(kopia, tmp_path):
    from riskanalys.regelverk.sakkunnig import granskningsobjekt
    from riskanalys.regelverk.validering_m2 import attesthinder
    import json

    fil = beslut(kopia, tmp_path / 'rackvidd')
    rb = ladda_regelbas(kopia)
    post = rb.kontroller['C-07'].rackvidd[0]
    mall = yaml.safe_load(fil.read_text())
    assert post.id in mall['objekt'] and post.id in rb.alla_id()
    underlag = json.loads((fil.parent / 'underlag.json').read_text())
    assert underlag['kontroller']['C-07']['rackvidd'][0]['id'] == post.id
    assert 'sakkunnig' not in underlag['kontroller']['C-07']['rackvidd'][0]
    tillampa_granskning(kopia, las_granskningsfil(fil, rb, 'RP-RED-VG'))
    nytt = ladda_regelbas(kopia)
    assert nytt.kontroller['C-07'].rackvidd[0].sakkunnig.galler(granskningsobjekt(nytt, 'RP-RED-VG')[post.id])
    assert not attesthinder(nytt, 'RP-RED-VG')
    assert post.sakkunnig.status == 'ej_granskad'


def test_andrad_rackvidd_i_fil_avvisar_gammal_import(kopia, tmp_path):
    fil = beslut(kopia, tmp_path / 'rackvidd-andring')
    p = kopia / 'kataloger/kontroller.yaml'
    data = yaml.safe_load(p.read_text())
    data[0]['rackvidd'][0]['begransningar'] += ' Ny begränsning i syntetiskt prov.'
    p.write_text(yaml.safe_dump(data, allow_unicode=True))
    with pytest.raises(RiskanalysFel, match='innehållssumma|bundet objekt'):
        las_granskningsfil(fil, ladda_regelbas(kopia), 'RP-RED-VG')
