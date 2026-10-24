"""Redaktionell presentation av frysta fakta; inga riskbeslut eller AI-anrop."""
from copy import deepcopy
import hashlib
import json
import re

VERSION='D-ARB-v10-redaktionell-2'
ORD={'bekraftad':'bekräftad','ej_granskad':'ej sakkunniggranskad',
     'kan_tala_for_lagre':'kan tala för lägre risk','underlag_saknas':'underlag saknas',
     'bada':'PT och TF','BADA':'PT och TF','pt':'PT','tf':'TF','okand':'okänd',
     'ej_bedomd':'ej bedömd','ej_belagt':'ej belagt','ej_relevant':'inte relevant',
     'galler':'gäller','galler_inte':'gäller inte','galler_annorlunda':'gäller annorlunda',
     'verkstaller':'verkställer betalningar','saknas':'saknas','full':'full insyn',
     'delvis':'delvis','digital':'digitalt','kund':'kunden','byran':'byrån',
     'ingen':'inget mandat','forbereder':'förbereder betalningar','egen':'egen',
     'erbjuder':'erbjuder','manuell':'manuellt','digitala':'digitala',
     'sverige':'Sverige','ovriga_ees':'övriga EES','utanfor_ees':'utanför EES'}
KODORD=tuple(x for x in ORD if '_' in x or x in ('bekraftad','BADA','bada','pt','tf','okand'))
RAW=re.compile(r'P-[A-Z]+\.|\bSRC-[A-Z0-9-]+\b|\bT-RED-\d+\b|\bD-ARB\.|;\s*K\d+\b|\bbyra:|\b(?:'+
    '|'.join(map(re.escape,KODORD))+r')\b|\bPROVPERSON-[A-Z0-9-]+|\b\d{5,}\.\d+\b')

def sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()

def los_pointer(x,p):
    for s in p.strip('/').split('/'):
        x=x[int(s)] if isinstance(x,list) else x[s.replace('~1','/').replace('~0','~')]
    return x

def satt_pointer(x,p,v):
    delar=p.strip('/').split('/');parent=los_pointer(x,'/'+ '/'.join(delar[:-1]))
    s=delar[-1];parent[int(s) if isinstance(parent,list) else s]=v

def synlig_text(x):
    if isinstance(x,list):return '\n'.join(synlig_text(v) for v in x)
    return '\n'.join([x.get('titel',''),*(a['rubrik']+'\n'+'\n'.join(
        [*(s['text'] for s in a['stycken']),*(t['rubrik']+'\n'+' | '.join(t['kolumner'])+'\n'+
        '\n'.join(' | '.join(c['text'] for c in r['celler']) for r in t['rader']) for t in a['tabeller'])])
        for a in x['avsnitt'])])

def ravarden(text):
    return [{'varde':m.group(),'position':m.start()} for m in RAW.finditer(text)]

def analysoriginal(x):
    """Alla fria analysfält enligt schemat; enumvärden och referens-ID är programdata."""
    from typing import get_args
    from riskanalys.analys import modeller
    referenser={'id','tjanst','kontroll','scenario','post','lokal_scenario','lokalt_scenario',
        'scenariosumma','summa','postsumma','visad_summa','underlagssumma','svarssumma',
        'profilrevision','bedomningsmanifest','utkastmanifest','regelbas','kallunderlag',
        'historik','modell','byra','dokument','kontrollsumma'}
    fria={n for cls in vars(modeller).values() if isinstance(cls,type) and issubclass(cls,modeller.Fryst)
        for n,f in cls.model_fields.items() if n not in referenser
        and (f.annotation is str or str in get_args(f.annotation))}
    def samla(v):
        if isinstance(v,dict):
            for n,a in v.items():
                if n in fria and isinstance(a,str) and a:yield a
                yield from samla(a)
        elif isinstance(v,(list,tuple)):
            for a in v:yield from samla(a)
    return set(samla(x))

class Lasformat:
    def __init__(self,k,*,regelbas=None,profil=None):
        from riskanalys.regelverk.modeller import Regelbas
        from riskanalys.profil.modeller import Profil
        self.k=k;self.falt=k['regelbas']['falt'];self.upp=k['profil']['uppgifter']
        self.regelbas=regelbas or Regelbas.model_validate(k['regelbas'])
        self.profil=profil or Profil.model_validate(k['profil'])
        self.namn={id:p['namn'] for n in ('hot','sarbarheter','lagre_risk','kontroller','tjanster')
                   for id,p in k['regelbas'][n].items()}

    def ord(self,v):
        return ORD.get(str(v),str(v))

    def etikett(self,id):
        f=self.falt.get(id);return (f.get('etikett') or f['fraga']) if f else 'Uppgift saknas i fältkatalogen'

    def varde(self,id):
        from riskanalys.dokument.faktorstatus_v10 import rapportbelagd
        u=self.upp.get(id,{})
        if u.get('status')=='ej_tillämplig':return 'Inte tillämplig'
        if id not in self.falt or not rapportbelagd(self.regelbas,self.profil,id):return 'Okänt'
        if id=='P-ROLL.ffr_namn':return 'Funktionen för regelefterlevnad'
        v=u.get('varde');f=self.falt[id]
        if f['typ']=='text':return str(v)  # Bokstavligt original, aldrig ord-/regexersättning.
        if id.endswith('_bankinsyn'):
            return {'ingen':'ingen insyn','full':'full insyn','delvis':'delvis insyn'}.get(v,self.ord(v))
        if id.endswith('_betalningsmandat') and v=='inget':return 'inget mandat'
        if type(v) is bool:return 'ja' if v else 'nej'
        if isinstance(v,(list,tuple)):return ', '.join(self.ord(x) for x in v) or 'Inga angivna'
        if isinstance(v,(int,float)):
            if f['typ']=='andel':return self.tal(v*100)+' %'
            if 'omsattning' in id:return self.tal(v/1e6)+' mnkr' if abs(v)>=1e6 else self.tal(v)+' kr'
            return self.tal(v)
        return self.ord(v) if v is not None else 'Okänt'

    @staticmethod
    def tal(v):
        return f'{v:,.2f}'.rstrip('0').rstrip('.').replace(',','\u00a0').replace('.',',')

    def period(self,id):
        p=self.upp.get(id,{}).get('period')
        return p['fran']+'–'+p['till'] if p else 'period saknas'

    def fakta(self,id,*,period=True):
        return self.etikett(id)+': '+self.varde(id)+(f' ({self.period(id)})' if period else '')

    def kallregister(self,id):
        """Källkodfältets register får svenska titlar; originalet bevaras i B1."""
        text=self.varde(id)
        for kod,kalla in self.k['regelbas']['kallor'].items():
            text=re.sub(r'(?<![\w-])'+re.escape(kod)+r'(?![\w-])',lambda m:kalla['titel'],text)
        return self.etikett(id)+': '+text

    def program(self,text,*,kontext=None):
        text=re.sub(r'P-[A-Z]+\.[\w.-]+',lambda m:self.etikett(m.group()) if m.group() in self.falt else m.group(),text)
        kodord=[x for x in ORD if '_' in x or x in ('bekraftad','bada','BADA','pt','tf','okand','galler','verkstaller','byran','forbereder')]
        text=re.sub(r'\b(?:'+ '|'.join(map(re.escape,sorted(kodord,key=len,reverse=True)))+r')\b',lambda m:self.ord(m.group()),text)
        text=re.sub(r'\bR4-(\d+)\b',r'scenario \1',text)
        text=re.sub(r'\bR5-(\d+)\b',r'lokalt scenario \1',text)
        text=text.replace('D-ARB.','avsnitt ')
        for id,name in sorted(self.namn.items(),key=lambda x:-len(x[0])):
            if id.startswith('T-'):
                text=re.sub(r'(?<![\w-])'+re.escape(id)+r'(?![\w-])(?:\s+'+re.escape(name)+r')?',lambda m:name,text)
            elif id.startswith(('H-','S-','C-')):
                text=re.sub(r'(?<![\w-])'+re.escape(id)+r'(?![\w-])',
                    lambda m: id if name in (kontext if kontext is not None else text) else name,text)
        return text

def stycke(text,refs=()):
    from riskanalys.dokument.resultatrapport_v9 import stycke as s
    return s(text,refs,lokal=True).model_dump(mode='json')

def tabell(id,rubrik,kolumner,rader):
    from riskanalys.dokument.resultatrapport_v9 import tabell as t
    return t(id,rubrik,kolumner,[[ (str(c),()) for c in r] for r in rader]).model_dump(mode='json')

def avsnitt(id,rubrik,del_):
    from riskanalys.dokument.rapportdelar_v10 import avsnitt as a
    x=a('F',rubrik).model_dump(mode='json');x.update(id=id,leveransdel=del_,visningsnummer=id.removeprefix('D-ARB.'))
    return x

def verifiera_flyttar(fore,efter):
    fel=[]
    for t in efter['transformationer']:
        if t['typ']!='flytt':continue
        try:
            a=los_pointer(fore,t['kalla']);b=los_pointer(efter,t['mal'])
            if a!=b or sha(a)!=t['summa']:fel.append(t['kalla'])
        except (KeyError,IndexError,TypeError):fel.append(t['kalla'])
    return fel

def bygg(k,p,*,regelbas=None,profil=None):
    k=dict(k)
    k['analys']=k.get('analys') or {'tjanster':[], 'gemensamma_sarbarhetsprovningar':[]}
    f=Lasformat(k,regelbas=regelbas,profil=profil);r={'version':VERSION,'renderade':deepcopy(p['renderade']),
        'transformationer':[],'scenariogrupper':[],'scenariomedlemskap':[],'kallsumma':sha(k)}
    huvud=r['renderade'][0]['avsnitt'];original=p['renderade'][0]['avsnitt']
    byid={a['id']:a for a in huvud};orig={a['id']:(i,a) for i,a in enumerate(original)}

    def flytta(a,del_,rubrik,*,stycken=None,tabeller=None):
        """Kopiera hela originalposter; logga text, tabellrubrik, kolumner och varje cell."""
        ai,old=orig[a['id']];di=1 if del_=='analysbilaga' else 2
        dest=avsnitt('D-ARB.E'+str(len(r['renderade'][di]['avsnitt'])+1),rubrik,del_)
        dest['stycken']=deepcopy(old['stycken'] if stycken is None else [old['stycken'][n] for n in stycken])
        dest['tabeller']=deepcopy(old['tabeller'] if tabeller is None else [old['tabeller'][n] for n in tabeller])
        aj=len(r['renderade'][di]['avsnitt']);r['renderade'][di]['avsnitt'].append(dest)
        sp=range(len(old['stycken'])) if stycken is None else stycken
        tp=range(len(old['tabeller'])) if tabeller is None else tabeller
        pairs=[(f'stycken/{si}/text',f'stycken/{j}/text') for j,si in enumerate(sp)]
        for j,ti in enumerate(tp):
            pairs.append((f'tabeller/{ti}/rubrik',f'tabeller/{j}/rubrik'))
            for ci in range(len(old['tabeller'][ti]['kolumner'])):pairs.append((f'tabeller/{ti}/kolumner/{ci}',f'tabeller/{j}/kolumner/{ci}'))
            for ri,row in enumerate(old['tabeller'][ti]['rader']):
                for ci in range(len(row['celler'])):pairs.append((f'tabeller/{ti}/rader/{ri}/celler/{ci}/text',f'tabeller/{j}/rader/{ri}/celler/{ci}/text'))
        for src,dst in pairs:
            path=f'/renderade/0/avsnitt/{ai}/{src}'
            r['transformationer'].append({'typ':'flytt','kalla':path,'mal':f'/renderade/{di}/avsnitt/{aj}/{dst}',
                'summa':sha(los_pointer(p,path)),'orsak':rubrik})
        return dest['id']

    # Hela hottabellen och dess källnyckel blir ett explicit hotregister.
    a=byid['D-ARB.R2'];mal=flytta(a,'underlagsbilaga','Hotregister med beskrivningar och källor')
    ids=[row['celler'][0]['text'].split()[0] for row in a['tabeller'][0]['rader']]
    a['stycken']=[deepcopy(a['stycken'][0]),stycke('Hoten är '+ '; '.join(f.namn[h] for h in ids)+
        f'. Hotbilden bygger på myndigheternas källor. Fullständigt hotregister: bilaga B1, {mal}. Tjänsternas analys: bilaga A.')];a['tabeller']=[]
    # Metodens tabeller stannar; fulla metodförklaringar följer med till A.
    a=byid['D-ARB.R4.1'];mal=flytta(a,'analysbilaga','Fullständiga metodförklaringar',tabeller=[])
    a['stycken']=[stycke(f'Metoden och samtliga tabellval är provisoriska och ej sakkunniggranskade. Fullständiga förklaringar: bilaga A, {mal}.')]
    for t in a['tabeller']:t['fore_stycke']=1
    # Faktakällornas register innehåller formler; de hör hemma i B1.
    a=byid['D-ARB.R1.1'];mal=flytta(a,'underlagsbilaga','Källor och observationsperioder',stycken=[0],tabeller=[])
    a['stycken']=[stycke(f'Andelar är beräknade ur bekräftade antal. Perioder och fullständiga källor: bilaga B1, {mal}.'),
        *(stycke(f.varde(id)) for id in ('P-BESK.verksamhet','P-BESK.kundtyper'))]
    rows=[]
    for row in a['tabeller'][0]['rader']:
        ref=next((x for x in row['celler'][0]['referenser'] if x.startswith('kalla:profil#/uppgifter/')),None)
        if not ref:continue
        id=ref.split('/uppgifter/')[1].replace('~1','/').replace('~0','~')
        rows.append([f.etikett(id),f.varde(id),f.period(id) if f.falt[id]['typ'] not in ('text','val','bool') else ''])
    a['tabeller']=[tabell('red-verksamhet','Verksamhetsuppgifter',('Uppgift','Värde','Observationsperiod'),rows)]
    # Kort tjänstetabell, med samtliga ursprungliga långa celler i A.
    a=byid['D-ARB.R1.2'];mal=flytta(a,'analysbilaga','Tjänsternas fullständiga arbetssätt och underlag')
    rows=[]
    for tid,t in k['regelbas']['tjanster'].items():
        if f.varde(t['erbjuds_falt'])!='ja':continue
        slug=t['erbjuds_falt'].removesuffix('_erbjuds')
        rows.append([t['namn'],t['beskrivning'],f.varde(slug+'_antal_kunder'),f.varde(slug+'_betalningsmandat'),f.varde(slug+'_bankinsyn')])
    a['tabeller']=[tabell('red-tjanster','Erbjudna tjänster',('Tjänst','Innehåll','Kunder','Mandat','Insyn'),rows)]
    a['stycken']=[stycke(f'Fulla arbetsmoment, attest, leveranssätt och lokala uppdragsprövningar: bilaga A, {mal}.'),
        stycke('Tabellernas tjänsteförkortningar: '+ '; '.join('T'+str(i+1)+' '+k['regelbas']['tjanster'][tid]['namn']
        for i,tid in enumerate(k['regelbas']['regelpaket'][k['profil']['byra']['regelpaket']]['tjanster']) if f.varde(k['regelbas']['tjanster'][tid]['erbjuds_falt'])=='ja')+'.')]
    for status,rubrik in (('nej','Erbjuds inte'),('Okänt','Okänd omfattning')):
        namn=[t['namn'] for t in k['regelbas']['tjanster'].values() if f.varde(t['erbjuds_falt'])==status]
        a['stycken'].append(stycke(rubrik+': '+('; '.join(namn) or 'inga')+'.'))
    # Gemensam erfarenhet stannar ordagrant; tjänsteposterna flyttas.
    a=byid['D-ARB.R2.1'];mal=flytta(a,'analysbilaga','Fullständiga erfarenhetsprövningar')
    a['stycken']=[stycke(f.fakta(id)) for id in ('P-VERK.antal_rapporter','P-VERK.antal_avbojanden')]
    a['stycken']+=[stycke(f.varde('P-BESK.erfarenheter')),stycke(f'Noll rapporter eller avböjanden bevisar inte frånvaro av hot. Tjänstevisa erfarenhetsprövningar: bilaga A, {mal}.')]
    # Läsbara fakta och skilda kända/okända statusar i kapitel 3.
    from riskanalys.regelverk.villkor import falt_i, tolka_villkor, Faltdef
    faltdef={id:Faltdef(id,x["typ"],tuple(x.get("val",()))) for id,x in f.falt.items()}
    for a in huvud:
        if a['id'].startswith('D-ARB.R3.'):
            periodfalt=set()
            for s in a['stycken']:
                m=re.match(r'(byra:[\w]+); ',s['text'])
                if m:
                    g=next(g for g in k['analys']['gemensamma_sarbarhetsprovningar'] if g['id']==m.group(1))
                    namn={'kund':'kunder','kanal':'kanaler','geo':'geografi','verk':'verksamhet','tj':'tjänster'}[g['omrade']]
                    s['text']=f"Gemensam bedömning för {namn} ({f.ord(g['status'])}, {g['relevans']} för {f.ord(g['dimension'])}): "+g['beskrivning']+' '+g['motivering']
            for t in a['tabeller']:
                if t['id'].startswith('v10-faktorer-') or t['id']=='v10-lagre-risk':
                    for row in t['rader']:
                        id=row['celler'][0]['text'].split()[0];post=k['regelbas']['sarbarheter'].get(id) or k['regelbas']['lagre_risk'][id]
                        fields=post.get('profilfalt') or sorted(falt_i(tolka_villkor(post['villkor'],faltdef)))
                        periodfalt.update(fields)
                        row['celler'][2]['text']='; '.join(f.fakta(x,period=False) for x in fields)
            if periodfalt:
                periodtext='; '.join(sorted({f.period(id) for id in periodfalt}))
                a['stycken'].append(stycke('Observationsperioder: '+periodtext+'. Period och källa per uppgift: bilaga B1.'))
    a=byid['D-ARB.R3.7'];mal=flytta(a,'underlagsbilaga','Förteckning över TF-relevanta indikatorer')
    a['stycken']=[stycke(f'TF-relevanta indikatorer ingår i faktatabellerna 3.1–3.5. Full förteckning och begränsningar: bilaga B1, {mal}. Fulla TF-motiveringar och scenarier finns i 4.2–4.3.')]
    # Enbart katalogmekanismer utan lokal variant får samlas i matrisen.
    extra=[];nya=('H-MOD-05','H-MOD-06','H-MOD-07','H-TF-03')
    for h in nya:
        entries=[]
        for ai,a in enumerate(huvud):
            if not a['id'].startswith('D-ARB.R4.3.'):continue
            tid=next(x for x in a['stycken'][0]['referenser'] if x.startswith('T-'))
            lok=next((x for x in k['analys']['tjanster'] if x['tjanst']==tid),None)
            if lok and any(h in s['hot'] for s in lok['scenarier']):continue
            for si,s in enumerate(a['stycken']):
                if not s['text'].startswith('Eget scenario ') or not re.search(r'\b'+h+r'\b',s['text']):continue
                ref=next(x for x in s['referenser'] if x.startswith('kalla:bedomning#/tjanster/'))
                sc=los_pointer(k['bedomning'],ref.split('#')[1]);entries.append((a,si,tid,sc))
        if len(entries)<2:continue
        # Undvik att gruppera bara en del om någon tjänst har en lokal variant.
        if any(any(h in s['hot'] for s in t['scenarier']) for t in k['analys']['tjanster']):continue
        key=lambda s:(json.dumps(s,sort_keys=True),)
        tmax={t['tjanst']:t['kvarstaende'] for t in k['bedomning']['tjanster']}
        if len({key(e[3])+(e[3]['kvarstaende'] is not None and e[3]['kvarstaende']==tmax[e[2]],) for e in entries})!=1:continue
        sc=entries[0][3];avgor_efter=sc['kvarstaende'] is not None and sc['kvarstaende']==tmax[entries[0][2]]
        val=f"{sc['risk']}{'*' if sc['avgorande'] else ''} → {sc['kvarstaende'] or 'ej beräknad'}"+('†' if avgor_efter else '')+f". Sannolikhet {sc['sannolikhet']}, konsekvens {sc['konsekvens']}."
        erbjudna=[t for t in k['bedomning']['tjanster'] if t['erbjuds']]
        extra.append([h+' '+f.namn[h]+' ('+sc['dimension'].upper()+')',*[val if any(e[2]==t['tjanst'] for e in entries) else 'Omfattas inte' for t in erbjudna]])
        r['scenariogrupper'].append({'hot':h,'dimension':sc['dimension'],'tjanster':[e[2] for e in entries],'niva_vag':sc})
        for a,si,tid,sc in entries:
            flytta(a,'analysbilaga','Ursprunglig lokal scenariorad för '+h,stycken=[si],tabeller=[])
            r['scenariomedlemskap'].append({'tjanst':tid,'hot':h,'dimension':sc['dimension'],'motorutfall':sc})
            a['stycken'][si]['text']=''  # tas bort först när samtliga originalpositioner registrerats
    for a in huvud:a['stycken']=[s for s in a['stycken'] if s['text']]
    if extra:
        byid['D-ARB.R4.2']['tabeller'].append(tabell('red-katalogscenarier','Katalogscenarier utan lokal variant',
            ('Hot och dimension',*[k['regelbas']['tjanster'][t['tjanst']]['namn'] for t in k['bedomning']['tjanster'] if t['erbjuds']]),extra))
    # Full kontrolltabell till A, bara verksamma/ej godtagna sänkningar i huvudrapporten.
    a=byid['D-ARB.R4.4'];mal=flytta(a,'analysbilaga','Fullständig kontrolltabell')
    grupper={}
    for ti,t in enumerate(k['bedomning']['tjanster']):
        if not t['erbjuds']:continue
        for sc in t['scenarier']:
            if not sc['tackande_kontroller']:continue
            key=(t['tjanst'],sc['dimension'],sc['risk'],sc['kvarstaende'],tuple(sc['tackande_kontroller']))
            grupper.setdefault(key,[]).append(sc['hot'])
    rows=[]
    for (tid,dim,fore,efter,kontroller),hot in grupper.items():
        ti=next(i for i,t in enumerate(t for t in k['bedomning']['tjanster'] if t['erbjuds']) if t['tjanst']==tid)+1
        rows.append([f.namn[tid],'; '.join(f.namn[h] for h in hot),
            '; '.join(f.namn[c] for c in kontroller),dim.upper()+': '+fore+' → '+str(efter),
            f'Lokal prövning och eventuellt ej godtagen sänkning: 4.3.{ti}.'])
    a['tabeller']=[tabell('red-kontrollavdrag','Motoravdrag som kräver lokal prövning',
        ('Tjänst','Hot','Kontroll','Motor före → efter','Lokal godtagbarhet'),rows)]
    a['stycken']=[stycke(f'Katalogmål är inte belägg för lokal effekt. Oprövade eller ej godtagna sänkningar förklaras i 4.3. Full kontrolltabell: bilaga A, {mal}.')]
    for t in k['bedomning']['tjanster']:
        if not t['erbjuds']:continue
        hs=[s['hot'] for s in t['scenarier'] if s['dimension']=='pt' and s.get('kvarstaende')==t['kvarstaende'] and not s['tackande_kontroller']]
        if hs:a['stycken'].append(stycke(k['regelbas']['tjanster'][t['tjanst']]['namn']+': '+', '.join(h+' '+f.namn[h] for h in hs)+' håller nivån '+t['kvarstaende']+' utan täckande kontroll.'))
    # Fältbaserade fria original ersätter de gamla programskapade metadatahängen.
    a=byid['D-ARB.R5.2'];a['stycken']=[stycke(f.varde('P-BESK.rutiner'))]
    a=byid['D-ARB.R5.3'];mal=flytta(a,'underlagsbilaga','Omvärldsbevakningens ursprungliga källregister',stycken=[0],tabeller=[])
    a['stycken']=[stycke(f.kallregister('P-BEVAKNING.kallor')+f'. Ursprungligt källregister: bilaga B1, {mal}.')]+[stycke(f.fakta(id,period=False)) for id in ('P-BEVAKNING.datum','P-BEVAKNING.ansvarig','P-BEVAKNING.relevans','P-BESK.uppdatering')]+[deepcopy(a['stycken'][-1])]
    # Övriga programvärden översätts utan att originaltexternas innehåll rörs.
    originaltexter={u['varde'] for id,u in f.upp.items() if id in f.falt and f.falt[id]['typ']=='text' and isinstance(u.get('varde'),str)}
    originaltexter.update(analysoriginal(k['analys']))
    def formattext(text):
        spans=[]
        for v in originaltexter:
            if v and v in text:
                spans.extend((m.start(),m.end()) for m in re.finditer(r'(?<![\w-])'+re.escape(v)+r'(?![\w-])',text))
        # Överlappande originalspann förenas, så att inget original formateras.
        merged=[]
        for start,end in sorted(spans):
            if merged and start<=merged[-1][1]:merged[-1]=(merged[-1][0],max(end,merged[-1][1]))
            else:merged.append((start,end))
        chunks=[];pos=0
        for start,end in merged:chunks.extend([f.program(text[pos:start],kontext=text),text[start:end]]);pos=end
        chunks.append(f.program(text[pos:],kontext=text));return ''.join(chunks)
    for a in huvud:
        a['rubrik']=formattext(a['rubrik'])
        for s in a['stycken']:s['text']=formattext(s['text'])
        for t in a['tabeller']:
            t['rubrik']=formattext(t['rubrik'])
            t['kolumner']=[formattext(x) for x in t['kolumner']]
            for row in t['rader']:
                for c in row['celler']:c['text']=formattext(c['text'])
    # Nya avsnitt kan ha färre stycken; ingen tabell får hamna utanför modellen.
    for d in r['renderade']:
        for a in d['avsnitt']:
            for t in a['tabeller']:t['fore_stycke']=min(t['fore_stycke'],len(a['stycken']))
    r['ravarden']=ravarden(synlig_text(r['renderade'][0]));r['flyttfel']=verifiera_flyttar(p,r)
    return r
