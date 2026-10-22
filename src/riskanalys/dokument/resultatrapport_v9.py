"""Kort resultatrapport ur sparade sakuppgifter; varken fri sammanfattning eller AI."""
from riskanalys.dokument.modeller import Avsnitt,Textstycke,Dokumenttabell,Tabellrad,Tabellcell
from riskanalys.dokument.rapportversion import V9
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.dokument.resultatmodell_v9 import pointerdel


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
    namn=lambda id:rb.tjanster[id].namn
    namnuppgift=profil.uppgifter.get('P-ORG.namn')
    org=str(namnuppgift.varde) if namnuppgift else '[VERIFIERA]'
    r1=avsnitt('D-ARB.R1','Sammanfattning',(
        stycke(f'{org}. Bedömning per {bedomning.datum}. Status: {bedomning.status}. '
               'Förhandsvisning av resultatrapport, ej fastställt av byrån. Riskbedömningen omfattar '
               'resultatrapport, bilaga A Analys och bilaga B1 Underlag.',
               (kallkod('profil','/uppgifter/P-ORG.namn'),kallkod('bedomning')),lokal=True),
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
               'Denna förhandsvisning utgör inget godkännande.',(kallkod('bedomning'),)),))
    gem=[]
    for p in underlag.poster:
        if p.tjanst is not None or p.hantering!='sammanfattas':continue
        refs=postref(p)
        if analys and p.id.startswith('gemensam:'):
            g=next(g for g in analys.gemensamma_sarbarhetsprovningar if 'gemensam:'+g.id==p.id)
            if 'egen_sarbarhet' in p.skal or 'osakerhet' in p.skal:
                gem.append(stycke(f'{g.status}, {g.dimension.upper()}, hot {", ".join(g.hot) or "saknas"}: '
                                   f'{g.beskrivning} {g.motivering}',refs,lokal=True))
        elif analys and p.id.startswith('verksamhet:'):
            g=next(g for g in analys.gemensamma_verksamhetsposter if 'verksamhet:'+g.id==p.id)
            if g.slag=='erfarenhet' or g.status!='bekraftad':
                gem.append(stycke(f'{g.slag}, {g.status}: {g.text}',refs,lokal=True))
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
                txt=(f'{s.risk} → {s.kvarstaende or "ej beräknad"}\n'
                     +('Avgör före. ' if s.avgorande else '')
                     +('Avgör efter.' if any('efter' in x for x in c.medlemmar) else '')) if s else {
                         'saknas':'Saknas i denna variant', 'ej_relevant':'Ej relevant enligt lokal prövning',
                         'okant':'Okänt underlag'}[c.status]
                cells.append((txt,(id,*(kallkod(r.artefakt,r.pointer) for r in c.kallor))))
            rows.append(cells)
        if rows:tabeller.append(tabell('v9-matris-'+str(gi),'Gemensamma scenarier före och efter kontroll',
                                      ('Hot och dimension',*(id+' '+namn(id) for id in grupp)),rows,fore=len(gem)))
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
        gem.append(stycke(f'{row.id}: '+(' '.join(parts) or '[VERIFIERA] Lokal scenariomekanism saknas.')+' '+values+
                          '. Tjänsternas skilda utfall och kontrollbegränsningar framgår av cellerna och R5.',
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
        s.append(stycke('Gemensamma kedjor: '+', '.join(r.id for r in rows if r in delade)+'. '
            +antaltext+'samtliga avgörande före-/efterled ingår. '
            'Detta speglar metodens utfall; prioriteringen av hot kräver fortsatt lokal prövning. '
            f'Full exponering och arbetsmoment: Bilaga A, {avsid}.',
            (t.tjanst,kallkod('bedomning',f'/tjanster/{bi}'))))
        for row in rows:
            c=next(c for c in row.celler if c.tjanst==t.tjanst);v=c.scenario
            if row not in delade:
                s.append(stycke(f'Eget scenario {row.id}, {row.hot} {row.dimension.upper()}: {rb.hot[row.hot].namn}. '
                    f'Sannolikhet {v.sannolikhet}, konsekvens {v.konsekvens}; risk {v.risk}, kvarstående {v.kvarstaende or "ej beräknad"}.',
                    (t.tjanst,*(kallkod(r.artefakt,r.pointer) for r in (*c.kallor,*row.mekanismkallor)))))
                from riskanalys.dokument.resultatmodell_v9 import los_pointer
                for mr in row.mekanismkallor:
                    value=los_pointer(analys.model_dump(mode='json'),mr.pointer)
                    if value.get('handelseforlopp'):
                        s.append(stycke(value['handelseforlopp'],(kallkod(mr.artefakt,mr.pointer),),lokal=True))
        controls=[]
        for row in rows:
            c=next(c for c in row.celler if c.tjanst==t.tjanst);v=c.scenario
            if v.dimension=='pt' and v.tackande_kontroller:
                controls.append(f'{row.id}: '+', '.join(v.tackande_kontroller)+f'; motorns kvarstående nivå {v.kvarstaende}')
        s.append(stycke('Kontrollpåverkan: '+('; '.join(controls) or 'ingen bärande reduktion i de avgörande scenarierna')+'. '
            'Belagd lokal effekt och eventuella invändningar ska prövas separat; se bilaga A, D-ARB.7 och tjänstens kontrollprövning.',
            (t.tjanst,kallkod('bedomning',f'/tjanster/{bi}'),kallkod('analys',prefix) if a else kallkod('analys'))))
        if a:
            for p in underlag.poster:
                if p.tjanst==t.tjanst and p.hantering=='sammanfattas' and any(x in p.skal for x in ('egen_sarbarhet','avvikelse','osakerhet')):
                    from riskanalys.dokument.resultatmodell_v9 import los_pointer
                    value=los_pointer(analys.model_dump(mode='json'),p.kallor[0].pointer)
                    txt=value.get('motivering') or value.get('referensmotivering')
                    if txt:s.append(stycke('Lokal prövning: '+txt,postref(p),lokal=True))
            for falt,label in (('pt_motivering','PT'),('tf_motivering','TF')):
                s.append(stycke(label+': '+(getattr(a,falt) or '[VERIFIERA] Motivering saknas.'),
                                (kallkod('analys',prefix+'/'+falt),),lokal=True))
            s.append(stycke('Åtgärder: '+(', '.join(p.id for p in a.rutinatgarder) or 'inga registrerade')+
                '. Status och uppföljning framgår av R6.',(kallkod('analys',prefix+'/rutinatgarder'),)))
        else:s.append(stycke('[VERIFIERA] Lokal analys och PT-/TF-motiveringar saknas.',(kallkod('analys'),)))
        lok.append(avsnitt('D-ARB.R5.'+avsid.removeprefix('D-ARB.6.'),namn(t.tjanst),s))
    s6=[]
    for p in underlag.poster:
        if p.hantering!='sammanfattas' or not any(x in p.skal for x in ('atgard','oppet_gap')):continue
        from riskanalys.dokument.resultatmodell_v9 import los_pointer
        v=los_pointer(analys.model_dump(mode='json'),p.kallor[0].pointer)
        if 'atgard' in p.skal:
            txt=(f'{p.tjanst} {v["id"]}: {v["atgard"]} Status {v["status"]}; ansvar {v.get("ansvar") or "saknas"}; '
                 f'uppföljning {v.get("uppfoljning") or "ej beslutad"}; prioritet {v.get("prioritet","ej beslutad")}.')
        else:txt=f'{p.tjanst} {v["id"]}, {v["typ"]}, {v["status"]}: {v["beskrivning"]} {v["motivering"]}'
        s6.append(stycke(txt,postref(p),lokal=True))
    for b in underlag.brister:s6.append(stycke('[VERIFIERA] '+b.beskrivning,tuple(kallkod(r.artefakt,r.pointer) for r in b.kallor)))
    s6.append(stycke('Registreringsordning är ingen beslutad prioritering. Fulla åtgärdsposter, belägg och maskinfynd: '
        'bilaga B1. Metoduppföljning D9 C redovisas där utan att en under-tröskel-upplysning görs till metodkonflikt.',
        (kallkod('analys'),)))
    r6=avsnitt('D-ARB.R6','Åtgärder och luckor',s6)
    utv=[h for h in historik.handelser if h.typ=='utvardering' and not h.plan_id]
    r7=avsnitt('D-ARB.R7','Utvärdering och omvärld',(
        stycke('Senaste samlade utvärdering: '+(str(max(h.datum for h in utv)) if utv else 'saknas [VERIFIERA]')+'. '
               'Riskbedömningen ska utvärderas minst årligen och före relevanta förändringar. '
               f'Registrerade förändringsplaner: {len(profil.tjansteplaner)}. Avgränsade planutvärderingar flyttar inte årsfristen. '
               'Datum, ansvar, nästa genomgång och dokumenterad omvärldsbevakning: bilaga A, D-ARB.10–11; planunderlag i B1.',
               (kallkod('historik'),kallkod('profil','/tjansteplaner') if profil.tjansteplaner else kallkod('profil'))),))
    return (r1,r2,r3,r4,*lok,r6,r7)
