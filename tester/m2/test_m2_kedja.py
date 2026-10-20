import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
import pytest
import yaml
from tester.fixturer.m2 import komplett_profil,bygg_delsvar,DAG
from tester.fixturer.v6_analys import utan_reduktionsansprak, godkann_syntetisk_analys
from riskanalys.profil.lagring import las_profil,spara_profil
from riskanalys.bedomning.korning import las_bedomning
from riskanalys.lagring.korningar import senaste_korning
from riskanalys.lagring.manifest import verifiera_manifest
from riskanalys.granskning.korning import las_granskning
from riskanalys.regelverk.laddning import ladda_regelbas,STANDARD_REGELBAS


def kor(env,*args,expected=0):
    p=subprocess.run([str(Path(sys.executable).parent/'riskanalys'),*args],env=env,text=True,capture_output=True)
    assert p.returncode==expected,p.stdout+'\n'+p.stderr
    assert 'Traceback' not in p.stderr
    return p


def expertkopia(tmp_path,paket):
    r=tmp_path/'regelbas';shutil.copytree(STANDARD_REGELBAS,r)
    # C är ett särskilt syntetiskt testfacit för kedjan, inte produktionens metod.
    p=r/'beslutstabeller/kundmodell/c-risk.yaml'
    p.write_text(yaml.safe_dump([dict(id='KC-SYNTETISK',spar='C',villkor={'alla':[]},utfall={'risk':'normal'},grund='metodval',lydelser=[],forklaring='Syntetisk konstant endast för tekniskt kedjeprov.')],allow_unicode=True))
    env={k:os.environ[k] for k in ('PATH','HOME','LANG') if k in os.environ}
    out=tmp_path/'sakkunnig'
    kor(env,'regelbas','granskningsunderlag','--regelbas',str(r),'--paket',paket,'--datum',str(DAG),'--ut',str(out))
    p=out/'granskningsmall.yaml';d=yaml.safe_load(p.read_text());d.update(granskare='Syntetisk testgranskare',kompetens='Syntetisk PTL/FS/metodgranskning',oberoende=True)
    for v in d['objekt'].values():v.update(beslut='verifierad',kommentar='Syntetiskt godkännande för tekniskt prov.')
    p.write_text(yaml.safe_dump(d,allow_unicode=True));kor(env,'regelbas','importera-granskning',str(p),'--regelbas',str(r))
    return r,env


def kedja(tmp_path,paket,lan,negativ=None):
    r,env=expertkopia(tmp_path,paket);data=tmp_path/'data med åäö';env['RISKANALYS_DATA']=str(data)
    arg=['--regelbas',str(r)];kor(env,'ny','testbyra','--regelpaket',paket,'--lan',lan,'--datum',str(DAG),*arg)
    byra=data/'testbyra'
    if negativ=='expert':(r/'granskning.yaml').unlink()
    if negativ=='metod':
        fil=r/'granskning.yaml';d=yaml.safe_load(fil.read_text());d['beslut'][paket]['objekt']['KUNDMETOD-C']['beslut']='ändras';fil.write_text(yaml.safe_dump(d,allow_unicode=True))
    rb=ladda_regelbas(r);p=utan_reduktionsansprak(rb,komplett_profil(rb,las_profil(byra)))
    if negativ=='felpaket':
        from riskanalys.profil.modeller import Uppgift
        p=p.model_copy(update={'uppgifter':{**p.uppgifter,'P-ORG.sateslan':p.uppgifter['P-ORG.sateslan'].model_copy(update={'varde':'Stockholm'})}})
    from tester.fixturer.skrivsvar_v7 import med_verksamhetsval
    p=med_verksamhetsval(rb,p)
    spara_profil(byra,p)
    # Riktig subprocess genom bekräftelser med period och härledning.
    for id,v in [('P-KUND.antal_aktiva','100'),('P-TJ.bolag01_antal_kunder','3')]:
        kor(env,'bekrafta','testbyra',id,v,'--kalla','Syntetisk CLI-testkälla','--datum',str(DAG),'--period-fran','2026-01-01','--period-till','2026-09-30',*arg)
    kor(env,'bedom','testbyra',*arg)
    mapp=senaste_korning(byra,'bedomningar','bedom')
    b=las_bedomning(mapp);assert b.status==('preliminär' if negativ=='felpaket' else 'slutlig')
    if negativ=='aldre':
        # Läsbar äldre modell med giltigt manifest, inte vanlig filkorruption.
        from riskanalys.lagring.manifest import las_manifest,skriv_manifest
        d=json.loads((mapp/'bedomning.json').read_text());d.pop('omfattning')
        (mapp/'bedomning.json').write_text(json.dumps(d,ensure_ascii=False))
        skriv_manifest(mapp,las_manifest(mapp).metadata)
    svar=[s.model_dump(mode='json') for s in bygg_delsvar(rb,las_profil(byra),b,tjanstspecifik=True)]
    if negativ=='fraga':svar[0]['oklarheter']=[{'fraga':'Syntetisk öppen fråga','uppgift_id':'P-KUND.antal_aktiva'}]
    fil=tmp_path/'testsvar.json';fil.write_text(json.dumps(svar,ensure_ascii=False))
    kor(env,'skriv','testbyra','--leverantor','test','--testsvar',str(fil),*arg)
    kor(env,'utvardera','testbyra','--beskrivning','Syntetisk teknisk prövning','--datum',str(DAG))
    godkann_syntetisk_analys(byra,rb,mapp,senaste_korning(byra,'utkast','skriv'),tmp_path/'lokala-underlag',DAG)
    kor(env,'granska','testbyra','--datum',str(DAG),*arg)
    kor(env,'exportera','testbyra','--utkast','--datum',str(DAG),*arg)
    d,f=las_granskning(senaste_korning(byra,'granskning','granska'))
    assert d.formatversion == 'D-ARB-tjanst-v8'
    if not negativ:
        exp=senaste_korning(byra,'export','exportera testbyra')
        wordfiler=tuple(exp.glob('*.docx'))
        assert len(wordfiler)==2, wordfiler
        assert verifiera_manifest(exp)==[]
    if not negativ:assert not f,f
    for a in d.avsnitt:kor(env,'sakgranska','testbyra','--avsnitt',a.id,'--godkann','--namn','Syntetisk testperson','--datum',str(DAG),*arg)
    if negativ=='belagg':
        p=las_profil(byra);u=p.uppgifter['P-ORG.namn'].model_copy(update={'kalla':None});spara_profil(byra,p.model_copy(update={'uppgifter':{**p.uppgifter,'P-ORG.namn':u}}))
    result=kor(env,'faststall','testbyra','--organ','styrelsen','--namn','Syntetisk testperson','--datum','2026-11-20' if negativ=='datum' else str(DAG),*arg,expected=1 if negativ else 0)
    if negativ:
        assert not (byra/'faststallda/v1').exists()
        return result
    kor(env,'verifiera','testbyra','1')
    ut=byra/'faststallda/v1';backup=tmp_path/'backup';shutil.copytree(ut,backup)
    restored=tmp_path/'aterstalld åäö/testbyra/faststallda/v1';shutil.copytree(backup,restored)
    assert verifiera_manifest(restored)==[]
    assert {p.relative_to(ut):p.read_bytes() for p in ut.rglob('*') if p.is_file()}=={p.relative_to(restored):p.read_bytes() for p in restored.rglob('*') if p.is_file()}
    env['RISKANALYS_DATA']=str(tmp_path/'aterstalld åäö');kor(env,'verifiera','testbyra','1')
    assert not (ut/'regelbas/utkast').exists()

@pytest.mark.parametrize('paket,lan',[('RP-RED-VG','Västra Götaland'),('RP-RED-SKANE','Skåne'),('RP-RED-STHLM','Stockholm')])
def test_m2_hela_cli_kedjan_och_aterstallning(tmp_path,paket,lan):kedja(tmp_path,paket,lan)

@pytest.mark.parametrize('fel',['fraga','belagg','expert','metod','felpaket','datum','aldre'])
def test_m2_negativ_cli_skapar_inget_paket(tmp_path,fel):kedja(tmp_path,'RP-RED-VG','Västra Götaland',fel)


def test_handredigerad_bekraftelse_utan_kalla_stoppas_vid_bedom(tmp_path):
    env={k:os.environ[k] for k in ('PATH','HOME','LANG') if k in os.environ}
    env['RISKANALYS_DATA']=str(tmp_path/'data åäö')
    kor(env,'ny','testbyra','--regelpaket','RP-RED-VG','--lan','Västra Götaland','--datum',str(DAG))
    byra=Path(env['RISKANALYS_DATA'])/'testbyra'
    rb=ladda_regelbas(STANDARD_REGELBAS);p=komplett_profil(rb,las_profil(byra))
    u=p.uppgifter['P-ORG.namn'].model_copy(update={'kalla':None})
    spara_profil(byra,p.model_copy(update={'uppgifter':{**p.uppgifter,'P-ORG.namn':u}}))
    result=kor(env,'bedom','testbyra',expected=1)
    assert 'P-ORG.namn' in result.stderr and 'källa' in result.stderr
    assert not list((byra/'bedomningar').glob('*/manifest.json'))
    assert not (byra/'faststallda/v1').exists()
