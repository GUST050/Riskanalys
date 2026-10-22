"""Enbart explicit syntetiskt ifyllda svar för slutprov; används aldrig av produkten."""
from riskanalys.analys import modeller as m
from riskanalys.analys.gemensam import postsumma


def ifylld_analys(rb,profil,bedomning,original,*,avvikelse=False,egen=False):
    from riskanalys.analys.overforing import foresla_overforing
    p=foresla_overforing(rb,original)
    belagg=tuple(b.id for b in p.belagg if b.dokument) or (p.belagg[0].id,)
    gem=[]
    for g in p.gemensamma_sarbarhetsprovningar:
        g=g.model_copy(update={'status':'bekraftad','forfattare':'Syntetisk gemensam författare','relevans':'relevant',
            'beskrivning':g.beskrivning if g.id.startswith('overfort:') else 'Syntetiskt prövat gemensamt underlag inom '+g.omrade+'. Uppgifterna gäller byråns bas; deras betydelse prövas per tjänst.',
            'motivering':'Gemensamt belagt underlag i det frysta syntetiska fallet. Katalogens mekanismer och lokala avgränsningar prövas tillsammans; ingen risknivå skrivs över.',
            'belagg':g.belagg or belagg})
        gem.append(g)
    verk=[];a=original.tjanster[0]
    for g in p.gemensamma_verksamhetsposter:
        text={'leverantorer':a.leverantorsmotivering,'erfarenhet':a.erfarenhetsprovning,'sanktionsanknytning':a.sanktioner}[g.slag]
        refs=a.erfarenhetsbelagg if g.slag=='erfarenhet' else belagg
        verk.append(g.model_copy(update={'status':'bekraftad','forfattare':'Syntetisk gemensam författare','text':text,
            'belagg':refs,'leverantorer':a.leverantorer if g.slag=='leverantorer' else ()}))
    if egen:
        gem.append(m.GemensamSarbarhetsprovning(id='egen:slutprov',omrade='kund',hot=('H-03',),dimension='pt',
            beskrivning='Syntetisk egen sårbarhet: samma underlagsförfalskning kan ske via ett alternativt dokumentformat i det redan beskrivna flödet.',
            motivering='Det alternativa dokumentformatet kräver uttrycklig prövning; högsta tjänstenivån används inte ensam som belägg.',
            relevans='relevant',belagg=belagg,status='bekraftad',forfattare='Syntetisk egen analys'))
    ts=[]
    for i,a in enumerate(p.tjanster):
        appar=[]
        for g in gem:
            beror_inte=(avvikelse and i==0 and g.omrade=='kund' and g.id!='egen:slutprov') or (g.id=='egen:slutprov' and i!=0)
            appar.append(m.Sarbarhetstillampning(post=g.id,postsumma=postsumma(g),stallningstagande='beror_inte' if beror_inte else 'galler',
                motivering='Syntetiskt belagd lokal avgränsning. Motorns högre nivå och åtgärdsgrund används fortsatt.' if beror_inte else '',
                belagg=belagg if beror_inte else ()))
        ts.append(a.model_copy(update={'sarbarhetstillampningar':tuple(appar),'verksamhetstillampningar':tuple(
            m.GemensamTillampning(post=g.id,postsumma=postsumma(g),stallningstagande='galler') for g in verk)}))
    return p.model_copy(update={'gemensamma_sarbarhetsprovningar':tuple(gem),'gemensamma_verksamhetsposter':tuple(verk),'tjanster':tuple(ts),
        # Detta är uttryckligen testets nya syntetiska användningsprövning av samma regelbas.
        'modellrisk':original.modellrisk.model_copy(update={'godkand':True}) if original.modellrisk else None})


def bekrafta_innehall(at,*,egen=False,samlat=False):
    """Logga verkliga lyckade API-handlingar, inga skattade klick eller tidsvinster."""
    from riskanalys.analys.lagring import las_analys
    from riskanalys.analys.provning import registersumma,scenariosumma,blocksumma
    from riskanalys.analys.gemensam import tackningssumma
    from riskanalys.bedomning.korning import las_bedomning
    logg=[]
    def paket():return las_analys(at.mapp)
    def kor(namn,fn,*args):
        fn(*args);logg.append(namn)
    p=paket()
    if p.schemaversion==2:
        for a in p.tjanster:
            p=paket();a=next(x for x in p.tjanster if x.tjanst==a.tjanst);refs=[]
            for slag,poster,appar in (('sarbarhet',p.gemensamma_sarbarhetsprovningar,a.sarbarhetstillampningar),('verksamhet',p.gemensamma_verksamhetsposter,a.verksamhetstillampningar)):
                for g in poster:
                    app=next(x for x in appar if x.post==g.id)
                    ref=m.GemensamReferens(slag=slag,post=g.id,summa=postsumma(g))
                    if app.stallningstagande=='galler':refs.append(ref)
                    else:
                        kor('lokal_avvikelse',at.spara_tillampning,a.tjanst,ref,app,registersumma(paket()),'Syntetisk prövare')
            if refs and not samlat:kor('samlad_tillampning',at.bekrafta_tillampningar,a.tjanst,tuple(refs),registersumma(paket()),'Syntetisk prövare')
    if samlat:
        from riskanalys.analys.engangssvar import visade_celler
        p=paket();ids=tuple(a.tjanst for a in p.tjanster)
        kor('gemensam_bekraftelse',at.bekrafta_byraunderlag,ids,visade_celler(p,ids),registersumma(p),'Syntetisk prövare')
    for a in paket().tjanster:
        for kop in a.scenariokopplingar:
            if samlat and (not egen or a.tjanst!=paket().tjanster[0].tjanst or kop.scenario!='gem:H-03'):continue
            p=paket();s=next(s for s in p.gemensamma_scenarier if s.id==kop.scenario)
            data={'tillampning':kop.tillampning,'lokal_scenario':kop.lokal_scenario or '',
                  'motivering':kop.motivering or 'Syntetiskt uttryckligt tjänsteval','visad_summa':scenariosumma(s),'forfattare':'Syntetisk prövare'}
            kor('scenarioval',at.spara_scenarioval,a.tjanst,s.id,data,registersumma(p))
    if egen:
        p=paket();a=p.tjanster[0];scenarier={s.id:s for s in (*p.gemensamma_scenarier,*a.scenarier)}
        s=next(s for s in scenarier.values() if 'H-03' in s.hot and s.relevans=='relevant')
        t=next(t for t in at.status().bedomning.tjanster if t.tjanst==a.tjanst)
        prov=m.Tackningsprovning(ursprung='gemensam',post='egen:slutprov',hot='H-03',dimension='pt',riskled='inneboende',
            stallningstagande='tacks_av_scenario',lokalt_scenario=s.id,jamforelseniva='låg',
            motivering='Den egna förfalskningsvägen ingår i det lokala H-03-scenariots beskrivna betalningsflöden; underlaget styrker samma mekanism.',
            referensmotivering='Syntetisk belagd gemensam orsak som redan ingår genom katalogfaktorn. Den lägre jämförelsenivån prövas uttryckligen och sakgranskas; ingen ny risknivå skapas.',
            belagg=(p.belagg[0].id,),forfattare='Syntetisk täckningsprövare')
        from riskanalys.analys.provning_v2 import kravda_riskled
        for riskled in kravda_riskled(t,prov.hot,prov.dimension):
            p=paket();n=prov.model_copy(update={'riskled':riskled})
            if riskled=='kvarstaende':
                n=n.model_copy(update={'motivering':prov.motivering+' Kontrollens dokumenterade stickprov omfattar samma underlagsformat och betalningsled; kvarstående risk prövas särskilt.',
                    'belagg':('ab6:kontroll',)})
            n=n.model_copy(update={'visad_summa':tackningssumma(at.rb,p,t,n)})
            kor('tackningsprovning',at.spara_tackningsprovning,a.tjanst,n,registersumma(p),'Syntetisk täckningsprövare')
    for a in paket().tjanster:
        if samlat:
            kor('tjanstegenomgang',at.bekrafta_tjansteunderlag,a.tjanst,registersumma(paket()),'Syntetisk prövare')
            continue
        for b in a.block:
            if b.aktivering!='aktiv':continue
            p=paket();data={'operation':'bekrafta','forfattare':'Syntetisk prövare','visad_summa':blocksumma(p,a.tjanst,b.nummer)}
            kor('blockbekraftelse',at.spara_block,a.tjanst,b.nummer,data,registersumma(p))
    return logg
