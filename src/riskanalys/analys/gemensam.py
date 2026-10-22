"""Rena läsvyer och innehållssummor; inga svar eller bekräftelser skrivs här."""
from riskanalys.analys.modeller import (
    Analyspaket, Tjansteanalys, Sarbarhetsprovning, GemensamSarbarhetsprovning,
    GemensamVerksamhetspost, Sarbarhetstillampning, GemensamTillampning,
)
from riskanalys.analys.provning import summa, effektiva_scenarier


def postsumma(post: GemensamSarbarhetsprovning | GemensamVerksamhetspost) -> str:
    return summa(post)


def tillampning_aktuell(post, app) -> bool:
    return bool(post is not None and app.bekraftad and app.postsumma==postsumma(post))


def effektiv_tjanst(paket: Analyspaket, tjanst: str) -> Tjansteanalys:
    a=next(t for t in paket.tjanster if t.tjanst==tjanst)
    if paket.schemaversion==1:
        return a
    scenarier,_=effektiva_scenarier(paket,a)
    poster={p.id:p for p in paket.gemensamma_sarbarhetsprovningar}
    provningar=list(a.sarbarhetsprovningar)
    for app in a.sarbarhetstillampningar:
        p=poster.get(app.post)
        if not tillampning_aktuell(p,app):
            continue  # B3 prövar den saknade/inaktuella bekräftelsen; inget innehåll ärvs.
        osakert=p.status!='bekraftad' or app.stallningstagande=='otillrackligt'
        relevans='okant' if osakert else 'ej_relevant' if app.stallningstagande=='beror_inte' else p.relevans
        text=' '.join(x for x in (p.status.capitalize()+':',p.beskrivning,p.motivering,app.motivering) if x)
        belagg=tuple(dict.fromkeys((*p.belagg,*app.belagg)))
        ids=tuple(s.id for s in scenarier.values() if set(s.hot)&set(p.hot))
        provningar.append(Sarbarhetsprovning(id='gemensam:'+p.id,omrade=p.omrade,
            sarbarheter=p.sarbarheter,scenarier=ids,relevans=relevans,motivering=text,belagg=belagg))
    andringar={'sarbarhetsprovningar':tuple(provningar)}
    poster={p.id:p for p in paket.gemensamma_verksamhetsposter}
    for app in a.verksamhetstillampningar:
        p=poster.get(app.post)
        if not tillampning_aktuell(p,app):
            continue
        if app.stallningstagande=='galler_annorlunda':
            continue  # Egna strukturerade svar prövas lokalt; avvikelsen redovisas separat.
        text=' '.join(x for x in ((p.status.capitalize()+':') if p.status!='bekraftad' else '',p.text,app.motivering) if x)
        if app.stallningstagande=='beror_inte':
            text='Berör inte tjänsten: '+app.motivering
        belagg=tuple(dict.fromkeys((*p.belagg,*app.belagg)))
        if p.slag=='leverantorer':
            andringar.update(leverantorsmotivering=text,leverantorer=() if app.stallningstagande=='beror_inte' else p.leverantorer)
        elif p.slag=='erfarenhet':
            andringar.update(erfarenhetsprovning=text,erfarenhetsbelagg=belagg)
        else:
            andringar['sanktioner']=text
    return a.model_copy(update=andringar)


def tillampningar_for_poster(paket: Analyspaket, tjanst: Tjansteanalys) -> Tjansteanalys:
    """Nya tjänsters obekräftade förslag följer det faktiska postregistret."""
    return tjanst.model_copy(update={
        'sarbarhetstillampningar':tuple(Sarbarhetstillampning(post=p.id,stallningstagande='galler',postsumma=postsumma(p))
            for p in paket.gemensamma_sarbarhetsprovningar),
        'verksamhetstillampningar':tuple(GemensamTillampning(post=p.id,stallningstagande='galler',postsumma=postsumma(p))
            for p in paket.gemensamma_verksamhetsposter)})


def forifyll_gemensamt(rb, paket: Analyspaket) -> Analyspaket:
    """Förslag och obekräftade tillämpningar; inga faktiska byråförhållanden härleds."""
    sarbarheter=[]
    for omrade in ('kund','kanal','geo','verk'):
        ids=tuple(sorted({id for t in paket.tjanster for id in rb.tjanster[t.tjanst].sarbarheter
                          if rb.sarbarheter[id].omrade==omrade}))
        sarbarheter.append(GemensamSarbarhetsprovning(id='byra:'+omrade,omrade=omrade,sarbarheter=ids,
            beskrivning='Pröva gemensamma förhållanden inom '+omrade+'.',
            hot=tuple(sorted({h for id in ids for h in rb.sarbarheter[id].hot}))))
    verksamhet=tuple(GemensamVerksamhetspost(id='byra:'+slag,slag=slag) for slag in
                    ('leverantorer','erfarenhet','sanktionsanknytning'))
    tjanster=tuple(t.model_copy(update={
        'sarbarhetsprovningar':tuple(s for s in t.sarbarhetsprovningar if s.omrade=='tjanst'),
        'sarbarhetstillampningar':tuple(Sarbarhetstillampning(post=p.id,stallningstagande='galler',postsumma=postsumma(p)) for p in sarbarheter),
        'verksamhetstillampningar':tuple(GemensamTillampning(post=p.id,stallningstagande='galler',postsumma=postsumma(p)) for p in verksamhet),
    }) for t in paket.tjanster)
    return paket.model_copy(update={'schemaversion':2,'gemensamma_sarbarhetsprovningar':tuple(sarbarheter),
        'gemensamma_verksamhetsposter':verksamhet,'tjanster':tjanster})


def tackningssumma(rb,paket,tjanst,provning):
    from riskanalys.analys.referens import referensniva
    a=next((a for a in paket.tjanster if a.tjanst==tjanst.tjanst),None)
    post=next((p for p in (paket.gemensamma_sarbarhetsprovningar if provning.ursprung=='gemensam' else a.sarbarhetsprovningar if a else ()) if p.id==provning.post),None)
    app=next((x for x in a.sarbarhetstillampningar if x.post==provning.post),None) if a and provning.ursprung=='gemensam' else None
    lokala,_=effektiva_scenarier(paket,a) if a else ({},())
    scenario=next((s for s in tjanst.scenarier if (s.hot,s.dimension)==(provning.hot,provning.dimension)),None)
    def data(x):return x.model_dump(mode='json') if x is not None else None
    return summa(dict(bindning=paket.bindning.model_dump(mode='json'),post=data(post),app=data(app),
        lokalt=data(lokala.get(provning.lokalt_scenario)),motor=data(scenario),belagg=[data(b) for b in paket.belagg],
        provning=provning.model_dump(mode='json',exclude={'visad_summa'}),
        referens=referensniva(rb,None,tjanst,provning.hot,provning.dimension,provning.riskled),
        antagande='Ytterligare +1; samma kontrollantaganden, inte ett facit.'))
