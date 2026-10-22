"""Schema 2: gemensamt underlag, aktuell tillämpning och uttrycklig risktäckning."""
from riskanalys.analys.gemensam import tackningssumma, tillampning_aktuell
from riskanalys.analys.provning import effektiva_scenarier, _saktext
from riskanalys.bedomning.motor import RISKNIVAER
from riskanalys.regelverk.modeller import hot_dimensioner


def egna_ansprak(rb,paket,tjanst):
    a=next((a for a in paket.tjanster if a.tjanst==tjanst.tjanst),None)
    if a is None:return ()
    ansprak=[]
    for p in paket.gemensamma_sarbarhetsprovningar:
        app=next((x for x in a.sarbarhetstillampningar if x.post==p.id),None)
        if p.sarbarheter or p.relevans!='relevant' or app is None or app.stallningstagande=='beror_inte':continue
        for hot in p.hot:
            for dim in hot_dimensioner(rb.hot[hot]) if hot in rb.hot else ():
                if p.dimension in ('bada',dim):ansprak.append(('gemensam',p.id,hot,dim))
    scenarier,_=effektiva_scenarier(paket,a)
    for p in a.sarbarhetsprovningar:
        if p.sarbarheter or p.relevans!='relevant':continue
        for id in p.scenarier:
            for hot in scenarier[id].hot if id in scenarier else ():
                for dim in hot_dimensioner(rb.hot[hot]) if hot in rb.hot else ():
                    ansprak.append(('lokal',p.id,hot,dim))
    return tuple(dict.fromkeys(ansprak))


def tackningsbrister(rb,paket,tjanst):
    from riskanalys.analys.referens import referensniva
    a=next((a for a in paket.tjanster if a.tjanst==tjanst.tjanst),None)
    if a is None:return ()
    fel=[];belagg={b.id for b in paket.belagg};scenarier,_=effektiva_scenarier(paket,a)
    ansprak=egna_ansprak(rb,paket,tjanst)
    for nyckel in ansprak:
        prov=[p for p in a.tackningsprovningar if (p.ursprung,p.post,p.hot,p.dimension)==nyckel]
        if not prov:fel.append(f'{tjanst.tjanst}: metodkonflikt {nyckel}: egen sårbarhet saknar uttrycklig täckningsprövning.')
    for p in a.tackningsprovningar:
        prefix=f'{tjanst.tjanst}: täckningsprövning {p.post}/{p.hot}/{p.dimension}/{p.riskled}: '
        def krav(v,text):
            if not v:fel.append(prefix+text)
        krav((p.ursprung,p.post,p.hot,p.dimension) in ansprak,'saknar relevant egen sårbarhet eller har fel hot/dimension.')
        krav(p.stallningstagande=='tacks_av_scenario','öppen metodkonflikt; risken är inte klarlagd som täckt.')
        krav(_saktext(p.motivering),'beskriv hur den egna mekanismen täcks av det lokala händelseförloppet.')
        krav(bool(p.belagg) and set(p.belagg)<=belagg,'aktuella belägg krävs.')
        krav(bool(p.forfattare and p.forfattare.strip()),'identifiera den som gjort täckningsprövningen.')
        lokal=scenarier.get(p.lokalt_scenario)
        krav(lokal is not None and lokal.relevans=='relevant' and p.hot in lokal.hot and _saktext(lokal.handelseforlopp),'giltigt relevant lokalt scenario med samma hot krävs.')
        motor=next((s for s in tjanst.scenarier if (s.hot,s.dimension)==(p.hot,p.dimension)),None)
        niva=(motor.risk if p.riskled=='inneboende' else motor.kvarstaende) if motor else None
        krav(bool(niva and p.jamforelseniva and RISKNIVAER.index(niva)>=RISKNIVAER.index(p.jamforelseniva)),'motorscenariots nivå måste täcka jämförelsenivån i samma riskled och dimension.')
        referens=referensniva(rb,None,tjanst,p.hot,p.dimension,p.riskled)
        if referens and p.jamforelseniva and RISKNIVAER.index(p.jamforelseniva)<RISKNIVAER.index(referens):
            krav(_saktext(p.referensmotivering),'en nivå under referensen +1 kräver uttrycklig motivering och sakgranskning.')
        krav(bool(p.visad_summa and p.visad_summa==tackningssumma(rb,paket,tjanst,p)),'underlaget eller svaret är inaktuellt; läs och bekräfta täckningsprövningen igen.')
    return tuple(fel)


def gemensamma_analysbrister(rb,profil,bedomning,paket):
    from riskanalys.analys.riktning import harled_riktningar
    fel=[];belagg={b.id for b in paket.belagg}
    def krav(v,text):
        if not v:fel.append(text)
    gem={p.id:p for p in paket.gemensamma_sarbarhetsprovningar}
    verk={p.id:p for p in paket.gemensamma_verksamhetsposter}
    for p in (*gem.values(),*verk.values()):
        krav(p.status=='bekraftad',f'{p.id}: {p.status} kvarstår; osäkerheten följer med varje tjänst.')
        krav(bool(p.forfattare and p.forfattare.strip()),f'{p.id}: författare saknas.')
        krav(bool(p.belagg) and set(p.belagg)<=belagg,f'{p.id}: aktuella belägg saknas.')
        if p.id in gem:
            krav(_saktext(p.motivering) and _saktext(p.beskrivning),f'{p.id}: förklara sårbarhetens mekanism eller motiverad frånvaro.')
            krav(p.relevans!='okant',f'{p.id}: relevansen är okänd.')
            krav(set(p.sarbarheter)<=set(rb.sarbarheter) and set(p.hot)<=set(rb.hot),f'{p.id}: välj kända faktorer och hot.')
            krav(set(p.profilfalt)<=set(rb.falt),f'{p.id}: okänt profilfält.')
            for id in p.sarbarheter:
                if id in rb.sarbarheter:krav(rb.sarbarheter[id].omrade==p.omrade,f'{p.id}: faktorn hör till annat område.')
            if p.relevans=='relevant':krav(bool(p.hot),f'{p.id}: ange hot för den relevanta sårbarheten.')
        else:krav(_saktext(p.text),f'{p.id}: gemensamt verksamhetssvar saknas.')
    for a in paket.tjanster:
        t=next((t for t in bedomning.tjanster if t.tjanst==a.tjanst),None)
        for name,poster in (('sarbarhetstillampningar',gem),('verksamhetstillampningar',verk)):
            appar=getattr(a,name)
            krav(set(poster)<={x.post for x in appar},f'{a.tjanst}: varje gemensam post kräver ett tjänsteställningstagande.')
            for app in appar:
                p=poster.get(app.post)
                krav(tillampning_aktuell(p,app),f'{a.tjanst}/{app.post}: gemensam tillämpning saknas eller är inaktuell.')
                krav(app.stallningstagande!='otillrackligt',f'{a.tjanst}/{app.post}: otillräckligt underlag hindrar sakgodkännande.')
                if app.stallningstagande!='galler':
                    krav(_saktext(app.motivering) and bool(app.belagg) and set(app.belagg)<=belagg,f'{a.tjanst}/{app.post}: lokal avvikelse kräver motivering och belägg.')
        for s in a.sarbarhetsprovningar:krav(not s.id.startswith('gemensam:'),f'{a.tjanst}: prefixet gemensam: är reserverat för läsvyn.')
        if t:
            fel.extend(tackningsbrister(rb,paket,t))
            for r in harled_riktningar(rb,profil,paket,t):
                if r.riktning in ('mojlig_underskattning','oklar'):
                    typ='metodkonflikt' if r.riktning=='mojlig_underskattning' else 'kunskapslucka'
                    fel.append(f'{a.tjanst}: {typ} {r.post}/{r.sarbarhet}/{r.hot}/{r.dimension}: {r.motivering}')
    return tuple(dict.fromkeys(fel))
