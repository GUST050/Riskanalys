"""Spara fulla motorutfall och redovisa varje sänkt eller borttaget scenarioled.

Python 3.12, ingen AI. Kör snapshot före mutation, sedan efter och jämförelse.
Profilerna är frysta syntetiska byråer från B:s evidenskatalog.
"""
from pathlib import Path
import json
from riskanalys.bedomning.motor import bedom
from riskanalys.regelverk.urval import valj
from riskanalys.profil.modeller import Profil
from riskanalys.lagring.kontrollsumma import for_fil

BAS=Path('.superpowers/evidens/2026-10-23-regelbas-steg-b')
NAMN=('referens_standard','referens_fyra','enmansbyra','betalningsmandat','riskbranscher','fa_faktorer')
RISK=('låg','måttlig','hög','mycket hög')
SANN=('låg','medel','hög')
KONS=('begränsad','betydande','allvarlig')


def profiler():
    for namn in NAMN:
        for suffix in ('-profil.json','_kompletterad-jamforelseprofil.json'):
            fil=BAS/(namn+suffix)
            yield namn+('_ursprunglig' if suffix=='-profil.json' else ''),fil,Profil.model_validate_json(fil.read_text())


def snapshot(rb,ut):
    ut.mkdir(parents=True,exist_ok=False)
    (ut/'regelbas.json').write_text(rb.model_dump_json(indent=2))
    from riskanalys.drift.modellidentitet import modellfilmanifest
    (ut/'modellfilmanifest.json').write_text(modellfilmanifest(rb).model_dump_json(indent=2))
    resultat={}
    for namn,fil,profil in profiler():
        b=bedom(rb,valj(rb,profil.byra.regelpaket,profil.byra.datum,profil.byra.lan),profil)
        resultat[namn]={'profilfil':str(fil),'profil_summa':for_fil(fil),
            'utfall':b.model_dump(mode='json')}
    (ut/'utfall.json').write_text(json.dumps(resultat,ensure_ascii=False,indent=2))
    return resultat


def jamfor(fore,efter):
    resultat={}
    for namn,a in efter.items():
        b=fore[namn];assert a['profil_summa']==b['profil_summa']
        ft={t['tjanst']:t for t in b['utfall']['tjanster']};et={t['tjanst']:t for t in a['utfall']['tjanster']}
        andringar=[];sankta=[];borttagna=[]
        for tid,t in et.items():
            old=ft.get(tid)
            if not old or t['erbjuds'] is not True:continue
            if old!=t:andringar.append({'tjanst':tid,'fore':old,'efter':t})
            fs={(s['hot'],s['dimension']):s for s in old['scenarier']}
            es={(s['hot'],s['dimension']):s for s in t['scenarier']}
            for key,s in fs.items():
                if key not in es:borttagna.append({'tjanst':tid,'fore':s})
            for key,s in es.items():
                if key not in fs:continue
                for led,skala in [('hotniva',SANN),('sarbarhetsniva',SANN),('sannolikhet',SANN),('konsekvens',KONS),('risk',RISK),('kvarstaende',RISK)]:
                    x,y=fs[key].get(led),s.get(led)
                    if x in skala and y in skala and skala.index(y)<skala.index(x):
                        sankta.append({'tjanst':tid,'hot':key[0],'dimension':key[1],'led':led,'fore':x,'efter':y})
        resultat[namn]={'profil_summa':a['profil_summa'],'andrade_tjanster':andringar,
            'sankta_led':sankta,'borttagna_scenarier':borttagna}
    return resultat
