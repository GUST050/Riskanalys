"""Kort resultatrapport ur sparade sakuppgifter; varken fri sammanfattning eller AI."""
from riskanalys.dokument.modeller import Avsnitt,Textstycke,Dokumenttabell,Tabellrad,Tabellcell
from riskanalys.dokument.rapportversion import V9
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.dokument.resultatmodell_v9 import pointerdel
from riskanalys.dokument.resultattexter_v9 import etikett,celltext,slutsats,gemensamma_motiveringar,sankningsforklaringar


def kolumngrupper(tjanster):
    return tuple(tuple(tjanster[n:n+4]) for n in range(0,len(tjanster),4))


def kallkod(artefakt,pointer=''):
    return f'kalla:{artefakt}#{pointer}'


def stycke(text, refs=(), *, lokal=False):
    return Textstycke(typ='motivering',text=text,referenser=list(refs),
        proveniens='lokal' if lokal else 'regelbas',literala_spann=((0,len(text)),) if lokal and text else ())


def avsnitt(id,rubrik,stycken=(),tabeller=()):
    return Avsnitt(id=id,rubrik=rubrik,kalla='regelbas',stycken=tuple(stycken),tabeller=tuple(tabeller),
                   formatversion=V9,leveransdel='resultatrapport',visningsnummer=id.removeprefix('D-ARB.'))


def tabell(id,rubrik,kolumner,rader,fore=0):
    return Dokumenttabell(id=id,rubrik=rubrik,kolumner=tuple(kolumner),fore_stycke=fore,
        rader=tuple(Tabellrad(celler=tuple(Tabellcell(text=t,referenser=tuple(refs),proveniens='lokal')
                                         for t,refs in r)) for r in rader))


def postref(p):
    return tuple(kallkod(r.artefakt,r.pointer) for r in p.kallor)


def bygg_resultatavsnitt(rb,profil,bedomning,resultat,historik,*,analys,underlag):
    from riskanalys.dokument.resultatunderlag_v9 import mekanism
    valda=list(tjanster_med_avsnitt(bedomning))
    lokala={a.tjanst:(n,a) for n,a in enumerate(analys.tjanster)} if analys else {}
    from riskanalys.analys.provning import ej_godtagna_sankningar, _saktext
    sankningar={t.tjanst:ej_godtagna_sankningar(rb,profil,analys,lokala[t.tjanst][1],t)
                for _,t in valda if t.tjanst in lokala}
    gemmot=gemensamma_motiveringar(analys)
    namn=lambda id:rb.tjanster[id].namn
    namnuppgift=profil.uppgifter.get('P-ORG.namn')
    org=str(namnuppgift.varde) if namnuppgift else '[VERIFIERA]'
    r1=avsnitt('D-ARB.R1','Sammanfattning',(
        stycke(f'{org}. Bedömning per {bedomning.datum}. Status: {bedomning.status}. '
               'Leveransstatus framgår av statusraden. Riskbedömningen omfattar '
               'resultatrapport, bilaga A Analys och bilaga B1 Underlag.',
               (kallkod('profil','/uppgifter/P-ORG.namn'),kallkod('bedomning')),lokal=True),
        stycke(slutsats(bedomning,analys),(kallkod('bedomning'),kallkod('analys'))),
        stycke('Tjänster: '+', '.join(namn(t.tjanst) for _,t in valda)+'. Ansvar och omfattning: bilaga A, D-ARB.1–3.',
               (kallkod('bedomning','/tjanster'),kallkod('regelbas','/tjanster'))),))
    rader=[]
    for _,t in valda:
        bi=bedomning.tjanster.index(t);refs=(t.tjanst,kallkod('bedomning',f'/tjanster/{bi}'))
        rader.append([(v,refs) for v in (namn(t.tjanst),t.inneboende.risk if t.inneboende else 'okänt',
                      t.kvarstaende or 'ej beräknad',t.terrorfinansiering.risk if t.terrorfinansiering else 'okänt',t.status)])
    r2=avsnitt('D-ARB.R2','Risk per tjänst',(
        stycke('PT är penningtvätt, TF är finansiering av terrorism. Skälen framgår av R4 och tjänstens R5. '
               'Ingen samlad risknivå för byrån beräknas. Fullständiga utfall: bilaga A, D-ARB.8 och tjänsteanalysen.',
               (kallkod('bedomning'),)),),
        (tabell('v9-risk','Motorns nivåer',('Tjänst','PT före','PT kvarstående','TF','Status'),rader),))
    prop=bedomning.proportionalitet
    omf=profil.uppgifter.get('P-OMFATTNING.motivering')
    r3=avsnitt('D-ARB.R3','Omfattning och metod',(
        stycke('Omfattning enligt metod: '+(prop.niva if prop else 'okänd [VERIFIERA]')+'. '
               'Motorn beräknar nivåer från tjänster, hot och riskfaktorer. Skalor, fasta konsekvensvärden och '
               'trösklar är metodval. Lokal analys prövar relevans, sårbarheter, insyn och kontrollernas faktiska effekt. '
               'Motorns kontrollavdrag är inte ensamt belägg för en lokal sänkning. '
               'Metod- och sakkunnigstatus samt begränsningar finns i bilaga A, D-ARB.2 och bilaga B1.',
               (kallkod('bedomning','/proportionalitet'),kallkod('regelbas','/metod'))),
        stycke('Byråns omfattningsmotivering: '+(str(omf.varde) if omf else '[VERIFIERA]'),
               (kallkod('profil','/uppgifter/P-OMFATTNING.motivering'),) if omf else (kallkod('profil'),),lokal=True),
        stycke('Antaganden, kunskapsluckor och metodkonflikter ska bedömas före fastställelse. '
               'Egna tjänster utan modellstöd får inte utelämnas; ofullständig omfattning kan inte fastställas. '
               'Dokumentpresentationen ersätter inte sakgranskning eller fastställelse.',(kallkod('bedomning'),)),))
    gem=[]
    for p in underlag.poster:
        if p.tjanst is not None or p.hantering!='sammanfattas':continue
        refs=postref(p)
        if analys and p.id.startswith('gemensam:'):
            g=next(g for g in analys.gemensamma_sarbarhetsprovningar if 'gemensam:'+g.id==p.id)
            if 'egen_sarbarhet' in p.skal or 'osakerhet' in p.skal:
                gem.append(stycke(f'{etikett(g.status)}, {g.dimension.upper()}, hot {", ".join(g.hot) or "saknas"}: '
                                   f'{g.beskrivning} {g.motivering}',refs,lokal=True))
        elif analys and p.id.startswith('verksamhet:'):
            g=next(g for g in analys.gemensamma_verksamhetsposter if 'verksamhet:'+g.id==p.id)
            if g.slag=='erfarenhet' or g.status!='bekraftad':
                gem.append(stycke(f'{g.slag}, {etikett(g.status)}: {g.text}',refs,lokal=True))
    for (falt,text),medlemmar in gemmot.items():
        gem.append(stycke('Gemensam '+falt[:2].upper()+'-motivering för '+', '.join(namn(id) for _,id in medlemmar)+': '+text,
            tuple(kallkod('analys',f'/tjanster/{i}/{falt}') for i,_ in medlemmar),lokal=True))
    # Faktorernas identitet och mekanism en gång, inte upprepat i varje tjänst.
    faktorer=tuple(dict.fromkeys(id for row in underlag.matris for c in row.celler if c.scenario for id in c.scenario.sarbarheter))
    gem.append(stycke('Gemensamma riskfaktorer i de valda scenarierna: '+
        '; '.join(rb.sarbarheter[id].namn for id in faktorer)+'. '
        'Tjänstens faktiska fördelning, perioder och belägg: bilaga A, D-ARB.5–6; full faktor-/kontrollkoppling i B1.',
        (kallkod('bedomning','/tjanster'),*(kallkod('regelbas','/sarbarheter/'+pointerdel(id)) for id in faktorer))))
    tabeller=[]
    ids=tuple(t.tjanst for _,t in valda)
    delade=[row for row in underlag.matris if sum(c.scenario is not None for c in row.celler)>1]
    for gi,grupp in enumerate(kolumngrupper(ids)):
        rows=[]
        for row in delade:
            mh=tuple(kallkod(r.artefakt,r.pointer) for r in row.mekanismkallor)
            title=f'{row.id} {row.hot} {row.dimension.upper()}\n{rb.hot[row.hot].namn}'
            cells=[(title,(row.hot,*mh))]
            for id in grupp:
                c=next(c for c in row.celler if c.tjanst==id)
                s=c.scenario
                orsaker=tuple(b.orsak for b in sankningar.get(id,()) if b.scenario==s)
                txt=celltext(c,orsaker)
                if c.status=='saknas' and any(r.hot==row.hot and r.dimension==row.dimension and
                    any(x.tjanst==id and x.scenario for x in r.celler) for r in underlag.matris):
                    avsid=next(avsid for avsid,t in valda if t.tjanst==id)
                    txt='Egen mekanism, se R5.'+avsid.removeprefix('D-ARB.6.')
                cells.append((txt,(id,*(kallkod(r.artefakt,r.pointer) for r in c.kallor),
                    kallkod('analys'),kallkod('profil'),kallkod('regelbas'))))
            rows.append(cells)
        if rows:tabeller.append(tabell('v9-matris-'+str(gi),'Gemensamma scenarier före och efter kontroll',
                                      ('Hot och dimension',*(id+' '+namn(id) for id in grupp)),rows,fore=len(gem)))
    gem.append(stycke('* avgör tjänstens nivå före kontroll; † avgör motorns kvarstående nivå. '
        'En markerad oprövad eller ej godtagen sänkning är inte en belagd kontrollverkan. '
        'Den inneboende scenarionivån gäller tills den lokala prövningen godtar sänkningen; analysgodkännande spärras. '
        'TF:s kvarstående nivå beräknas inte. '
        'Tjänsternas skilda utfall och kontrollbegränsningar framgår av cellerna och R5.',
        (kallkod('analys'),kallkod('bedomning'))))
    for row in delade:
        used=set();parts=[];refs=[]
        for c in row.celler:
            if c.scenario:
                s=c.scenario;used.add((s.sannolikhet,s.konsekvens))
        for r in row.mekanismkallor:
            from riskanalys.dokument.resultatmodell_v9 import los_pointer
            value=los_pointer(analys.model_dump(mode='json'),r.pointer)
            v=value.get('handelseforlopp','')
            if v and v not in parts:parts.append(v)
            refs.append(kallkod(r.artefakt,r.pointer))
        values='; '.join(f'Sannolikhet {s}, konsekvens {k}' for s,k in sorted(used))
        gem.append(stycke(f'{row.id}: '+(' '.join(parts) or '[VERIFIERA] Lokal scenariomekanism saknas.')+' '+values+'.',
                          (*refs,kallkod('bedomning','/tjanster')),lokal=True))
    r4=avsnitt('D-ARB.R4','Gemensamma förhållanden och scenarier',gem,tabeller)
    lok=[]
    for avsid,t in valda:
        bi=bedomning.tjanster.index(t);ai,a=lokala.get(t.tjanst,(None,None));prefix=f'/tjanster/{ai}'
        s=[stycke(namn(t.tjanst)+'. '+rb.tjanster[t.tjanst].beskrivning,
                  (t.tjanst,kallkod('regelbas','/tjanster/'+pointerdel(t.tjanst))))]
        rows=[r for r in underlag.matris if any(c.tjanst==t.tjanst and c.medlemmar for c in r.celler)]
        flera=any(sum(s.avgorande and s.dimension==dim for s in t.scenarier)>1 for dim in ('pt','tf'))
        antaltext=('Flera scenarier ger var för sig tjänstens risknivå; ' if flera else
                   'Tjänstens avgörande scenarier redovisas nedan; ')
        deladeid=', '.join(r.id for r in rows if r in delade)
        kedjor='Gemensamma kedjor: '+deladeid+'. ' if deladeid else 'Scenarierna nedan har tjänstens egen mekanism. '
        s.append(stycke(kedjor
            +antaltext+'samtliga avgörande före-/efterled ingår. '
            'Detta speglar metodens utfall; prioriteringen av hot kräver fortsatt lokal prövning. '
            f'Full exponering och arbetsmoment: Bilaga A, {avsid}.',
            (t.tjanst,kallkod('bedomning',f'/tjanster/{bi}'))))
        for row in rows:
            c=next(c for c in row.celler if c.tjanst==t.tjanst);v=c.scenario
            if row not in delade:
                s.append(stycke(f'Eget scenario {row.id}, {row.hot} {row.dimension.upper()}: {rb.hot[row.hot].namn}. '
                    f'Sannolikhet {v.sannolikhet}, konsekvens {v.konsekvens}; '+celltext(c,tuple(
                        b.orsak for b in sankningar.get(t.tjanst,()) if b.scenario==v))+'.',
                    (t.tjanst,*(kallkod(r.artefakt,r.pointer) for r in (*c.kallor,*row.mekanismkallor)))))
                from riskanalys.dokument.resultatmodell_v9 import los_pointer
                for mr in row.mekanismkallor:
                    value=los_pointer(analys.model_dump(mode='json'),mr.pointer)
                    if value.get('handelseforlopp'):
                        s.append(stycke(value['handelseforlopp'],(kallkod(mr.artefakt,mr.pointer),),lokal=True))
        controlgrupper={}
        for row in rows:
            c=next(c for c in row.celler if c.tjanst==t.tjanst);v=c.scenario
            if v.dimension=='pt' and v.tackande_kontroller:
                controlgrupper.setdefault((v.tackande_kontroller,v.kvarstaende),[]).append(row.id)
        controls=[', '.join(ids)+': '+', '.join(rb.kontroller[id].namn+' ('+id+')' for id in ks)+
                  '; motorns kvarstående nivå '+(niva or 'ej beräknad') for (ks,niva),ids in controlgrupper.items()]
        avslut=('Ej godtagna sänkningar förklaras nedan; se även bilaga A, D-ARB.7 och tjänstens kontrollprövning.'
                if sankningar.get(t.tjanst) else
                'Belagd lokal effekt och eventuella invändningar ska prövas separat; se bilaga A, D-ARB.7 och tjänstens kontrollprövning.')
        s.append(stycke('Kontrollpåverkan: '+('; '.join(controls) or 'ingen bärande reduktion i de avgörande scenarierna')+'. '+avslut,
            (t.tjanst,kallkod('bedomning',f'/tjanster/{bi}'),kallkod('analys',prefix) if a else kallkod('analys'),
             kallkod('regelbas','/kontroller'))))
        if a:
            for txt in sankningsforklaringar(rb,sankningar[t.tjanst]):
                s.append(stycke(txt,(t.tjanst,kallkod('analys',prefix),kallkod('analys','/belagg'),
                    kallkod('profil'),kallkod('regelbas'),kallkod('bedomning',f'/tjanster/{bi}'))))
            for p in underlag.poster:
                if p.tjanst==t.tjanst and p.hantering=='sammanfattas' and any(x in p.skal for x in ('egen_sarbarhet','avvikelse','osakerhet')):
                    if p.kallor[0].artefakt!='analys':continue  # motoravvikelsen förklaras vid kontrollprövningen ovan
                    from riskanalys.dokument.resultatmodell_v9 import los_pointer
                    value=los_pointer(analys.model_dump(mode='json'),p.kallor[0].pointer)
                    txt=value.get('motivering') or value.get('referensmotivering')
                    if txt:s.append(stycke('Lokal prövning: '+txt,postref(p),lokal=True))
            for falt,label in (('pt_motivering','PT'),('tf_motivering','TF')):
                v=getattr(a,falt)
                if (falt,v) in gemmot:
                    s.append(stycke(label+': se den gemensamma fullständiga motiveringen i R4.',
                        (kallkod('analys',prefix+'/'+falt),)))
                    continue
                markor='' if _saktext(v) else '[KOMPLETTERA: Lokal motivering är inte färdig.] '
                s.append(stycke(label+': '+markor+(v or 'Motivering saknas.'),
                                (kallkod('analys',prefix+'/'+falt),),lokal=True))
            s.append(stycke('Åtgärder för '+namn(t.tjanst)+': se R6 för namn, identitet, status och uppföljning.'
                if a.rutinatgarder else 'Inga åtgärder registrerade.',(kallkod('analys',prefix+'/rutinatgarder'),)))
        else:s.append(stycke('[VERIFIERA] Lokal analys och PT-/TF-motiveringar saknas.',(kallkod('analys'),)))
        lok.append(avsnitt('D-ARB.R5.'+avsid.removeprefix('D-ARB.6.'),namn(t.tjanst),s))
    s6=[]
    for p in underlag.poster:
        if p.hantering!='sammanfattas' or not any(x in p.skal for x in ('atgard','oppet_gap')):continue
        from riskanalys.dokument.resultatmodell_v9 import los_pointer
        v=los_pointer(analys.model_dump(mode='json'),p.kallor[0].pointer)
        if 'atgard' in p.skal:
            txt=(f'{namn(p.tjanst)}: {v["atgard"]} ({v["id"]}). Status {etikett(v["status"])}; ansvar {v.get("ansvar") or "saknas"}; '
                 f'uppföljning {v.get("uppfoljning") or "ej beslutad"}; prioritet {etikett(v.get("prioritet","ej beslutad"))}.')
        else:
            beskrivning=v['beskrivning'];motivering=v['motivering']
            # Endast exakt textåteranvändning, ingen härledd koppling mellan lucka och åtgärd.
            samma=next(((i,a,j,r) for i,a in enumerate(analys.tjanster) for j,r in enumerate(a.rutinatgarder)
                        if a.tjanst==p.tjanst and beskrivning and beskrivning in r.atgard),None)
            refs=list(postref(p))
            if samma:
                i,a,j,r=samma
                beskrivning=f'Beskrivningen återges ordagrant i raden {r.id}.'
                refs.append(kallkod('analys',f'/tjanster/{i}/rutinatgarder/{j}'))
                if motivering==v['beskrivning']:motivering='Samma text utgör luckans motivering.'
            txt=(f'{namn(p.tjanst)} ({v["id"]}), {etikett(v["typ"])}, {etikett(v["status"])}: '
                 +' '.join(dict.fromkeys((beskrivning,motivering)))+
                 f' Ansvar {v.get("ansvar") or "saknas"}; tidsfrist {v.get("tidsfrist") or "ej beslutad"}.')
            s6.append(stycke(txt,refs,lokal=True))
            continue
        s6.append(stycke(txt,postref(p),lokal=True))
    for b in underlag.brister:s6.append(stycke('[VERIFIERA] '+b.beskrivning,tuple(kallkod(r.artefakt,r.pointer) for r in b.kallor)))
    s6.append(stycke('Registreringsordning är ingen beslutad prioritering. Fulla åtgärdsposter, belägg och maskinfynd: '
        'bilaga B1. Metoduppföljning D9 C redovisas där utan att en under-tröskel-upplysning görs till metodkonflikt.',
        (kallkod('analys'),)))
    r6=avsnitt('D-ARB.R6','Åtgärder och luckor',s6)
    utv=historik.senaste_utvardering()
    r7=avsnitt('D-ARB.R7','Utvärdering och omvärld',(
        stycke('Senaste samlade utvärdering: '+(str(utv) if utv else 'saknas [VERIFIERA]')+'. '
               'Riskbedömningen ska utvärderas minst årligen och före relevanta förändringar. '
               f'Registrerade förändringsplaner: {len(profil.tjansteplaner)}. Avgränsade planutvärderingar flyttar inte årsfristen. '
               'Datum, ansvar, nästa genomgång och dokumenterad omvärldsbevakning: bilaga A, D-ARB.10–11; planunderlag i B1.',
               (kallkod('historik'),kallkod('profil','/tjansteplaner') if profil.tjansteplaner else kallkod('profil'))),))
    return (r1,r2,r3,r4,*lok,r6,r7)
