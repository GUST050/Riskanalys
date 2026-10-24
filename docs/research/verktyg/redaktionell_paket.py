"""Reproducerbara syntetiska produktreferenser och tre expertunderlag, utan AI."""
import argparse
import json
import re
import shutil
import subprocess
from datetime import date
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))

FALL=('fyra_tjanster','med_betalningsmandat')
PAKET=('RP-RED-VG','RP-RED-SKANE','RP-RED-STHLM')
DAG=date(2026,10,24)


def las(p):return json.loads(p.read_text(encoding='utf-8'))
def spara(p,data):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def kontrollera_sakdata(fore,efter):
    """Endast teknisk versions-/filbindning får skilja regelbaserna."""
    efter=json.loads(json.dumps(efter))
    for key in ('version','kontrollsumma'):efter[key]=fore[key]
    for id,b in efter['metodbeslut'].items():
        assert b['sakkunnig']['status']=='ej_granskad'
        b['modellfiler']=fore['metodbeslut'][id]['modellfiler']
    assert efter==fore,'Sakuppgifter skiljer regelbaserna'


def skillnader(fore,efter,pekare=''):
    """Exakta ändrade fält; orörda stora scenarioträd behöver inte upprepas."""
    if fore==efter:return []
    if isinstance(fore,dict) and isinstance(efter,dict) and set(fore)==set(efter):
        return [x for k in sorted(fore) for x in skillnader(fore[k],efter[k],pekare+'/'+k.replace('~','~0').replace('/','~1'))]
    if isinstance(fore,list) and isinstance(efter,list) and all(isinstance(x,dict) and 'hot' in x and 'dimension' in x for x in fore+efter):
        a={x['hot']+':'+x['dimension']:x for x in fore};b={x['hot']+':'+x['dimension']:x for x in efter}
        if len(a)==len(fore) and len(b)==len(efter):
            return [x for k in sorted(a.keys()|b.keys()) for x in skillnader(a.get(k),b.get(k),pekare+'/'+k)]
    if isinstance(fore,list) and isinstance(efter,list) and len(fore)==len(efter):
        return [x for i,(a,b) in enumerate(zip(fore,efter)) for x in skillnader(a,b,pekare+'/'+str(i))]
    return [{'falt':pekare,'fore':fore,'efter':efter}]


def lasbar_jamforelse(data):
    return {n:{**x,'andrade_tjanster':[{'tjanst':t['tjanst'],
        'andrade_falt':skillnader(t['fore'],t['efter'])} for t in x['andrade_tjanster']]} for n,x in data.items()}


def referenser(fran,ut):
    from riskanalys.regelverk.laddning import ladda_regelbas
    from riskanalys.regelverk.urval import valj
    from riskanalys.profil.modeller import Profil
    from riskanalys.bedomning.motor import bedom
    from riskanalys.analys.modeller import Analyspaket
    from riskanalys.drift.historik import Historik
    from riskanalys.dokument.delskrivning import Tjanstresultat
    from riskanalys.dokument.arb_v10 import bygg_resultatpaket_v10
    from riskanalys.dokument.presentation_v10 import bygg_presentation_v10
    from riskanalys.dokument.rapportvyer_v10 import bygg_rapportvyer_v10
    from riskanalys.dokument.rendering_v10 import rendera_rapportvyer_v10
    from riskanalys.dokument.leverans_v10 import LeveransV10
    from riskanalys.dokument.resultatmodell_v9 import kallartefakter
    from riskanalys.granskning.kontroller import granska
    from riskanalys.granskning.dokument_v10 import resultatfynd_v10,kravkarta_v10
    from riskanalys.granskning.modeller import Fynd
    from riskanalys.granskning.korning import oppna_fragor
    from riskanalys.lagring.manifest import skriv_manifest
    from riskanalys.lagring.kontrollsumma import for_fil
    from riskanalys.dokument.redaktionell_v10 import verifiera_flyttar,synlig_text
    rb=ladda_regelbas();ut.mkdir(parents=True,exist_ok=False)
    for namn in FALL:
        rot=ut/namn;rot.mkdir();k=las(fran/namn/'kallor.json')
        kontrollera_sakdata(k['regelbas'],rb.model_dump(mode='json'))
        p=Profil.model_validate(k['profil'])
        p=p.model_copy(update={'uppgifter':{id:u.model_copy(update={'varde':date.fromisoformat(u.varde)})
            if rb.falt[id].typ=='datum' and isinstance(u.varde,str) else u for id,u in p.uppgifter.items()}})
        gammal=k['bedomning'];u=valj(rb,gammal['regelpaket'],date.fromisoformat(gammal['datum']),gammal['lan'])
        b=bedom(rb,u,p);normal=b.model_dump(mode='json')
        for key in ('regelbas_version','regelbas_kontrollsumma'):normal[key]=gammal[key]
        assert normal==gammal,'Motorutfall ändrat'
        analys=Analyspaket.model_validate(k['analys']);h=Historik.model_validate(k['historik'])
        r={id:Tjanstresultat.model_validate(v) for id,v in k['skrivresultat'].items()}
        kontext=las(fran/namn/'granskningskontext.json')
        assert kontext['modellrapport'] is None,'Referensen kräver separat modellrapportprövning'
        bygge=bygg_resultatpaket_v10(rb,p,b,r,h,analys=analys)
        fynd=granska(rb,u,p,b,bygge.analysdokument,h,DAG,oppna_fragor(r),skrivresultat=r,analys=analys,
            modellrapport=None,analysbrister_filer=tuple(kontext['analysbrister_filer']))
        extra=resultatfynd_v10(rb,p,b,r,h,analys=analys,bygge=bygge,dokument=bygge.dokument)
        fynd=(*fynd,*(Fynd(id=f'F-{DAG}-{i:03d}',**x) for i,x in enumerate(extra,len(fynd)+1)))
        pr=bygg_presentation_v10(bygge,analys=analys,fynd=fynd,bedomning=b,profil=p,regelbas=rb,
            presentationsversion='D-ARB-v10-presentation-2')
        rendera_rapportvyer_v10(bygg_rapportvyer_v10(bygge.dokument),p,rot/'word',presentation=pr,
            leverans=LeveransV10(datum=DAG,bedomning='syntetisk-produktreferens',granskning='syntetisk-produktreferens'))
        for fil in ('kallor.json','presentation.json'):
            shutil.copy2(fran/namn/fil,rot/('ursprunglig-'+fil))
        spara(rot/'kallor.json',kallartefakter(rb,p,b,r,h,analys,bygge.analysdokument))
        spara(rot/'bygge.json',bygge.model_dump(mode='json'))
        spara(rot/'presentation.json',pr.model_dump(mode='json'))
        spara(rot/'kravkarta.json',kravkarta_v10(rb,p,b,bygge))
        spara(rot/'granskningskontext.json',kontext)
        spara(rot/'fynd.json',[x.model_dump(mode='json') for x in fynd])
        # Exakt flyttkontroll mot den ursprungliga versionen av dagens produktbygge.
        bas=bygg_presentation_v10(bygge,analys=analys,fynd=fynd,bedomning=b,profil=p)
        red={'renderade':[d.model_dump(mode='json') for d in pr.renderade],
            'transformationer':list(pr.redaktion.flyttar)}
        assert not verifiera_flyttar(bas.model_dump(mode='json'),red)
        main=synlig_text(red['renderade'][0])
        assert all(t.pt_motivering in main and t.tf_motivering in main for t in analys.tjanster)
        spara(rot/'redaktionell-bas.json',bas.model_dump(mode='json'))
        spara(rot/'flyttregister.json',red['transformationer'])
        spara(rot/'bevis.json',{'motorutfall_oforandrat':True,'sakdata_oforandrade':True,
            'flyttar':len(pr.redaktion.flyttar),'scenariomedlemskap':len(pr.redaktion.scenariomedlemskap),
            'ursprungliga_filer':{n:for_fil(fran/namn/n) for n in ('kallor.json','presentation.json')},
            'regelbas_fore':k['regelbas']['kontrollsumma'],'regelbas_efter':rb.kontrollsumma,
            'verkliga_ai_anrop':0})
        (rot/'pdf').mkdir()
        subprocess.run(['soffice','-env:UserInstallation=file:///private/tmp/redaktionell-produkt-'+namn,
            '--headless','--convert-to','pdf','--outdir',str(rot/'pdf'),
            *map(str,sorted((rot/'word').glob('*.docx')))],check=True)
        assert len(list((rot/'pdf').glob('*.pdf')))==3
        skriv_manifest(rot,{'typ':'syntetisk-redaktionell-produktreferens','regelbas':rb.kontrollsumma})
        print(namn,rb.version,len(pr.redaktion.flyttar),'flyttdelar',flush=True)


def paket(fran,refs,ut,prov):
    if prov:
        resultat=las(prov/'resultat.json')
        assert resultat['profil']=='full' and resultat['verifierad'] and resultat['oforandrat'] and resultat['fel']==0,'Slutprovet är inte verifierat grönt'
    from riskanalys.regelverk.laddning import ladda_regelbas,STANDARD_REGELBAS
    from riskanalys.regelverk.sakkunnig import exportera_sakkunnigunderlag,granskningsobjekt
    from riskanalys.regelverk.metodbeslut import filindex
    from riskanalys.regelverk.lasversion import skapa_lasversion
    from riskanalys.lagring.manifest import las_manifest,skriv_manifest,verifiera_manifest
    from riskanalys.lagring.kontrollsumma import for_fil
    from riskanalys.lagring.yamlfil import las_yaml
    repo=Path(__file__).resolve().parents[3];rb=ladda_regelbas();ut.mkdir(parents=True,exist_ok=False)
    from riskanalys.profil.modeller import Profil
    from riskanalys.bedomning.motor import bedom
    from riskanalys.regelverk.urval import valj
    old=fran/PAKET[0];mapping=las(old/'metod/profilkarta.json')
    fasta=las(old/'metod/slut-2.12.2/utfall.json')
    kontraster=las(old/'metod/kontraster3/D-LAGRE-efter.json')
    aktuella={}
    for namn,tidigare in {**fasta,**kontraster}.items():
        fil=old/mapping[namn]['paketfil'] if namn in fasta else old/'metod/kontraster3'/(namn+'-profil.json')
        assert for_fil(fil)==tidigare['profil_summa']
        profil=Profil.model_validate_json(fil.read_text());b=tidigare['utfall']
        ny=bedom(rb,valj(rb,b['regelpaket'],date.fromisoformat(b['datum']),b['lan']),profil).model_dump(mode='json')
        normal=json.loads(json.dumps(ny))
        for key in ('regelbas_version','regelbas_kontrollsumma'):normal[key]=b[key]
        assert normal==b,'Ändrat motorutfall i '+namn
        aktuella[namn]={'profil_summa':tidigare['profil_summa'],'utfall':ny,'sakutfall_oforandrat':True}
    assert len(aktuella)==len(fasta)+len(kontraster)==52
    filer=filindex();dependency={'version':rb.version,'regelbas':rb.kontrollsumma,'samtliga_status':'ej_granskad',
        'beslut':[{'id':id,'valt':b.valt,'attest_innehallssumma':granskningsobjekt(rb,PAKET[0])[id],
            'objekt':b.objekt,'modellfiler':b.modellfiler} for id,b in rb.metodbeslut.items()]}
    for id in PAKET:
        old=fran/id;full=ut/'fullstandigt'/id
        assert not verifiera_manifest(old),'Historiskt expertpaket är ändrat'
        exportera_sakkunnigunderlag(STANDARD_REGELBAS,id,DAG,full)
        for p in old.iterdir():
            if p.name in {'manifest.json','referensrapporter','genomforande','sakkunniggranskning.md','objektgenomgang.md','slutprov.md'} or (full/p.name).exists():continue
            if p.is_dir():shutil.copytree(p,full/p.name)
            else:shutil.copy2(p,full/p.name)
        summor=granskningsobjekt(rb,id)
        text=(old/'objektgenomgang.md').read_text(encoding='utf-8')
        objekt=re.findall(r'^## (.+)$',text,re.M)
        assert set(objekt)==set(summor)
        text=re.sub(r'(^## (.+)\n\nGranskningssumma: `)[^`]+',lambda m:m[1]+summor[m[2]],text,flags=re.M)
        text=text.replace(f'# Objektgenomgång {id}, 2.12.2',f'# Objektgenomgång {id}, {rb.version}')
        (full/'objektgenomgang.md').write_text(text,encoding='utf-8')
        shutil.copy2(repo/'docs/sakkunniggranskning.md',full/'sakkunniggranskning.md')
        method=full/'metod';spara(method/'beslut-och-beroenden.json',dependency)
        summary=(old/'metod/2026-10-23-metodbeslut-samlat.md').read_text(encoding='utf-8')
        summary+='\n\n## Teknisk ombindning 2026-10-24\n\nRegelbas 2.12.3 ändrar endast version och D-beslutens filkontrollsummor. Alla sakuppgifter, val, statusar och motorutfall är oförändrade. Presentationen har ny version. Gamla före-/efterfiler behåller sina historiska versioner. Aktuella bindningar finns i beslut-och-beroenden.json, samtliga historiska skillnader i fore-efter.json och dagens referensbevis under referensrapporter/.\n'
        (method/'sammanstallning.md').write_text(summary,encoding='utf-8')
        spara(method/'slut-2.12.3/utfall.json',aktuella)
        jam={p.relative_to(method).as_posix():{'originalfil_summa':for_fil(p),'profiler':lasbar_jamforelse(las(p))} for p in sorted(method.rglob('*.json'))
            if p.name in ('jamforelse.json','samlat-mot-2.0.0.json') or p.name.endswith(('-jamforelse.json','-samlat-mot-2.0.0.json'))}
        spara(method/'fore-efter.json',{'historiska_jamforelser':jam,
            'aktuell_teknisk_ombindning':{n:las(refs/n/'bevis.json') for n in FALL},
            'aktuell_profilkontroll':{n:{'profil_summa':x['profil_summa'],'sakutfall_oforandrat':True} for n,x in aktuella.items()},
            'lasanvisning':'Varje historisk fil behåller sitt datum och version. andrade_falt visar exakta ändrade värden; scenarier identifieras med hot:dimension. Oförändrade fält upprepas inte. Fulla utfall och originaljämförelser med kontrollsumma finns på angivna sökvägar i fullständiga paketet; ingen redaktionell ändring räknas som sänkt risk.'})
        for fil,summa in filer.items():
            dest=full/'genomforande'/fil;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(repo/fil,dest)
            assert for_fil(dest)==summa
        for n in FALL:
            assert not verifiera_manifest(refs/n)
            dest=full/'referensrapporter'/n;shutil.copytree(refs/n,dest)
            # Gemensamma PDF-filer ligger på stabila sökvägar i full- och läspaket.
            for p in (dest/'pdf').glob('*.pdf'):shutil.copy2(p,dest/p.name)
            (dest/'manifest.json').unlink()
            skriv_manifest(dest,{'typ':'syntetisk-redaktionell-produktreferens','regelbas':rb.kontrollsumma})
        if prov:
            target=full/'slutprov';target.mkdir()
            for n in ('resultat.json','snapshot.json','junit.xml','collection.log','pytest.log'):
                if (prov/n).is_file():shutil.copy2(prov/n,target/n)
        mall=las_yaml(full/'granskningsmall.yaml')
        assert set(mall['objekt'])==set(summor)
        assert all(x['beslut']=='ej_granskad' and not x['kommentar'] for x in mall['objekt'].values())
        meta=las_manifest(full).metadata
        skriv_manifest(full,{**meta,'regelbas_version':rb.version,'regelbas':rb.kontrollsumma})
        assert not verifiera_manifest(full)
        reader=ut/'lasversion'/id;skapa_lasversion(full,reader)
        print(id,len(list(full.rglob('*'))),'poster;',las(reader/'lasversion.json')['storlek_byte'],'byte läsversion',flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='kommando',required=True)
    r=sub.add_parser('referenser');r.add_argument('--fran',type=Path,required=True);r.add_argument('--ut',type=Path,required=True)
    r=sub.add_parser('paket');r.add_argument('--fran',type=Path,required=True);r.add_argument('--referenser',type=Path,required=True);r.add_argument('--ut',type=Path,required=True);r.add_argument('--prov',type=Path)
    a=p.parse_args()
    if a.kommando=='referenser':referenser(a.fran.resolve(),a.ut.resolve())
    else:paket(a.fran.resolve(),a.referenser.resolve(),a.ut.resolve(),a.prov.resolve() if a.prov else None)

if __name__=='__main__':main()
