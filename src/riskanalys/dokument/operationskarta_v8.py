"""Källfält från samma typade byggoperationer som V8 använder, utan textsökning."""
from riskanalys.dokument.analystabeller import scenariokopplingsgrupper
from riskanalys.dokument.tjanstavsnitt_v8 import bygg_tjanstavsnitt_v8, kontrollobservationer
from riskanalys.dokument.nivamotivering_v8 import berakningsgrupper, avgor_efter, faktorregisterposter
from riskanalys.regelverk.granser import metodgransindex


def operationskarta(rb, profil, bedomning, resultat, analys):
    karta={}
    def lagg(position, *pointers):
        karta[position]=tuple(('analys',p) for p in dict.fromkeys(pointers))
    from riskanalys.dokument.underlag import tjanster_med_avsnitt
    for avsnitt,t in tjanster_med_avsnitt(bedomning):
        ti=next((n for n,a in enumerate(analys.tjanster if analys else ()) if a.tjanst==t.tjanst),None)
        a=analys.tjanster[ti] if ti is not None else None
        bas=f'/tjanster/{ti}'
        op={}
        section=bygg_tjanstavsnitt_v8(rb,profil,t,resultat.get(avsnitt),avsnitt,
            gransindex=metodgransindex(rb),analys=analys,_operationer=op)
        for position,fields in op.items():
            if position=='beslutsstycke':
                continue
            if fields[0][0]=='ai':
                r=resultat[avsnitt]; f=len(r.del_('analys').forsok)-1
                karta[avsnitt+'/'+position]=(('resultat',f'/{avsnitt}/delar/0/forsok/{f}/svar/stycken/{fields[0][1]}'),)
            else:
                lagg(avsnitt+'/'+position,*(bas+'/'+p for _,p in fields))
        bi=next(i for i,x in enumerate(bedomning.tjanster) if x.tjanst==t.tjanst)
        for n,post in enumerate(faktorregisterposter(rb,t)):
            felt='sarbarheter' if post.typ=='sarbarhet' else 'tackande_kontroller'
            katalog='sarbarheter' if post.typ=='sarbarhet' else 'kontroller'
            medlemskallor=tuple(('bedomning',f'/tjanster/{bi}/scenarier/{i}/{felt}') for i in post.scenarioindex)
            for m in range(4):
                kallor=medlemskallor
                if m in (1,2) and post.id in (rb.sarbarheter if post.typ=='sarbarhet' else rb.kontroller):
                    kallor+= (('regelbas',f'/{katalog}/{post.id}/'+('id' if m==1 else 'namn')),)
                if m==3:
                    kallor+=tuple(('bedomning',f'/tjanster/{bi}/scenarier/{i}/{f}') for i in post.scenarioindex for f in ('hot','dimension'))
                karta[f'{avsnitt}/tabeller/{t.tjanst}-faktorregister/rader/{n}/celler/{m}']=kallor
        if a is None:
            continue
        # Urvalet läser alltid beslutens tjänst. Hashunderlaget läses bara om ett kandidatbeslut finns.
        pos=avsnitt+f'/stycken/{op["beslutsstycke"]}'
        pointers=[bas+'/forfattare','/beslut']
        kandidat=next((n for n in reversed(range(len(analys.beslut))) if analys.beslut[n].tjanst==a.tjanst),None)
        if kandidat is not None:
            pointers.extend(('/revision','/bindning'))
            pointers.extend('/'+f for f in type(analys).model_fields if f not in ('beslut','revision'))
            pointers.extend(f'/beslut/{kandidat}/{f}' for f in ('tjanst','revision','underlagssumma','svarssumma','godkand','datum','namn'))
        lagg(pos,*pointers)
        for n,grupp in enumerate(kontrollobservationer(a,analys)):
            cols=(('kontroll','scenario','rackvidd'),('tillampning','utfall'),('tackning','kvarstar'),('belagg',))
            for m,fields in enumerate(cols):
                pointers=[f'{bas}/kontroller/{i}/{f}' for i,k in grupp for f in fields]
                # Alla fält deltar i exakt gruppval; redovisa själva operationen separat från textvärdena.
                pointers.extend(f'{bas}/kontroller/{i}' for i,k in grupp)
                if m==3:
                    ids={id for _,k in grupp for id in k.belagg}
                    pointers.extend(f'/belagg/{i}/period' for i,b in enumerate(analys.belagg) if b.id in ids)
                lagg(f'{avsnitt}/tabeller/{a.tjanst}-kontrollprovning/rader/{n}/celler/{m}',*pointers)
        for n,r in enumerate(a.rutinatgarder):
            # Slutkriterium och prioritet visas, serialiseras och spåras bara när de angetts.
            nya=tuple(f for f in ('klart_nar','prioritet') if f in r.model_dump())
            cols=(('scenarier',),('atgard',),('status','rutin_id','rutin_version'),
                  ('ansvar','utlosare_eller_frekvens','uppfoljning',*nya))
            for m,fields in enumerate(cols):
                lagg(f'{avsnitt}/tabeller/{a.tjanst}-rutinatgarder/rader/{n}/celler/{m}',*(f'{bas}/rutinatgarder/{n}/{f}' for f in fields))
        for n,s in enumerate(a.scenarier):
            for m,fields in enumerate((('id','rubrik'),('handelseforlopp',),('relevans','motivering','delanalyser'),('hot','rubrik'),('belagg',))):
                lagg(f'{avsnitt}/tabeller/{a.tjanst}-scenarier/rader/{n}/celler/{m}',*(f'{bas}/scenarier/{n}/{f}' for f in fields))
        for n,(signatur,grupp) in enumerate(scenariokopplingsgrupper(a,analys),len(a.scenarier)):
            kopplingar=[i for i,k in enumerate(a.scenariokopplingar) if any(k is x for x,_ in grupp)]
            gem=[i for i,s in enumerate(analys.gemensamma_scenarier) if any(s is x for _,x in grupp)]
            for m in range(5):
                fields=('scenario',) if m==0 else ('scenario','bekraftad','scenariosumma','tillampning','motivering','lokal_scenario') if m==2 else ('scenario',)
                pointers=[f'{bas}/scenariokopplingar/{i}/{f}' for i in kopplingar for f in fields]
                pointers.extend(f'/gemensamma_scenarier/{i}' for i in gem)
                lagg(f'{avsnitt}/tabeller/{a.tjanst}-scenarier/rader/{n}/celler/{m}',*pointers)
        bi=next(i for i,x in enumerate(bedomning.tjanster) if x.tjanst==t.tjanst)
        start=section.underrubriker[3].fore_stycke
        for n,grupp in enumerate(g for g in berakningsgrupper(t) if g[0].avgorande or avgor_efter(t,g[0])):
            members=[i for i,x in enumerate(t.scenarier) if x in grupp]
            karta[f'{avsnitt}/stycken/{start+n}']=tuple(('bedomning',f'/tjanster/{bi}/scenarier/{i}/{f}')
                for i in members for f in type(t.scenarier[i]).model_fields)+(('bedomning',f'/tjanster/{bi}/kvarstaende'),)
        # De lokala PT/TF-texternas positioner registreras av bygg_tjanstavsnitt_v8 när styckena byggs.
    for n,s in enumerate(analys.gemensamma_scenarier if analys else ()):
        for m,fields in enumerate((('id','rubrik'),('handelseforlopp',),('relevans','motivering','delanalyser'),('hot','rubrik'),('belagg',))):
            lagg(f'D-ARB.4/tabeller/gemensamma-scenarier/rader/{n}/celler/{m}',*(f'/gemensamma_scenarier/{n}/{f}' for f in fields))
    from riskanalys.dokument.arb_v8 import atgardsposter
    for n,(_,_,ti,ri,_) in enumerate(atgardsposter(bedomning,analys)):
        for m,fields in enumerate((('tjanst',),('id',),('status',),('ansvar',),('uppfoljning',),('id',))):
            lagg(f'D-ARB.9/tabeller/v8-atgardsoversikt/rader/{n}/celler/{m}',*(f'/tjanster/{ti}/'+(f if m==0 else f'rutinatgarder/{ri}/{f}') for f in fields))
    return karta
