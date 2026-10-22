"""Tre arbetsvyer för gemensam analys, tillämpning och separat sakgranskning."""
from html import escape as e
from urllib.parse import urlencode
from riskanalys.analys import modeller as m
from riskanalys.analys.gemensam import postsumma,tillampning_aktuell,tackningssumma
from riskanalys.analys.riktning import harled_riktningar
from riskanalys.analys.provning_v2 import egna_ansprak,kravda_riskled
from riskanalys.analys.referens import referensniva
from riskanalys.intag.vyer import dold,falt,val
from riskanalys.intag.analysvy import _kontroll
from riskanalys.intag.gemensamformular import katalogval
from riskanalys.intag.analysformular import hamta_tjanst

REFERENS='Referens: samma scenario med ytterligare +1 – inte ett facit'
NAMN={'kund':'Kunder','kanal':'Distributionskanaler','geo':'Geografi','verk':'Egen verksamhet',
      'leverantorer':'Leverantörer och eget ansvar','erfarenhet':'Egna lärdomar','sanktionsanknytning':'Sanktionsanknytning'}


def _unika_dom(fragment,prefix):
    import re
    return re.sub(r'(id|for)="([^"]+)"',lambda m:m[1]+'="'+prefix+'-'+m[2]+'"',fragment)


def _form(prefix,action,csrf,revision,extra=()):
    return '<form method="post" action="'+e(prefix+action,quote=True)+'">'+''.join(dold(k,v) for k,v in (('csrf',csrf),('revision',revision),*extra))


def _falt(modell,objekt,*,utan=(),data=None,kataloger=None):
    from riskanalys.intag.analysformular import grundtyp
    return ''.join(_kontroll(k,grundtyp(f.annotation),getattr(objekt,k),data or {},kataloger) for k,f in modell.model_fields.items() if k not in utan)


def byraanalys(paket,prefix,csrf,revision,query=None,data=None,rb=None,bedomning=None):
    q=query or {};d=data or {};html='<h1>1. Gemensam byråanalys</h1><p>Beskriv och belägg förhållandena en gång. Tjänsterna prövar sedan betydelsen. Antaganden är fortfarande antaganden efter tillämpning.</p>'
    valt=q.get('post',[''])[0];slag=q.get('slag',['sarbarhet'])[0]
    for typ,poster in (('sarbarhet',paket.gemensamma_sarbarhetsprovningar),('verksamhet',paket.gemensamma_verksamhetsposter)):
        for p in poster:
            href=prefix+'analys?'+urlencode({'byraanalys':'ja','post':p.id,'slag':typ})
            html+='<article><h2>'+e(NAMN.get(getattr(p,'omrade',getattr(p,'slag','')),p.id))+'</h2><p>'+e(getattr(p,'beskrivning',getattr(p,'text','')))+' · '+e(p.status)+'</p><a href="'+e(href,quote=True)+'">Redigera gemensamt underlag</a></article>'
    href=prefix+'analys?'+urlencode({'byraanalys':'ja','post':'ny','slag':'sarbarhet'})
    html+='<p><a href="'+e(href,quote=True)+'">Lägg till egen sårbarhet eller motiverad frånvaro</a></p>'
    if not valt:
        from riskanalys.intag.analysvy import _lasbar
        for post in (*paket.gemensamma_sarbarhetsprovningar,*paket.gemensamma_verksamhetsposter):
            html+='<details><summary>Hela underlaget: '+e(post.id)+'</summary><p>'+e(_lasbar(post))+'</p></details>'
        if bedomning is not None:
            from riskanalys.intag.engangsvy import helhet
            html+=helhet(paket,bedomning,prefix,csrf,revision)
        return html
    modell=m.GemensamSarbarhetsprovning if slag=='sarbarhet' else m.GemensamVerksamhetspost
    poster=paket.gemensamma_sarbarhetsprovningar if slag=='sarbarhet' else paket.gemensamma_verksamhetsposter
    p=next((p for p in poster if p.id==valt),None)
    if p is None:
        if modell is m.GemensamVerksamhetspost:return html+'<p>Välj en befintlig verksamhetspost.</p>'
        p=m.GemensamSarbarhetsprovning(id=d.get('id','egen:ny'),omrade='kund')
    html+=_form(prefix,'analysgemensampost',csrf,d.get('revision',revision),(('typ',slag),))
    html+=_falt(modell,p,utan=('leverantorer','forfattare'),data=d,kataloger=katalogval(rb,paket) if rb else None)
    if slag=='verksamhet' and p.slag=='leverantorer':
        for i,l in enumerate((*p.leverantorer,m.Leverantorsprovning(id=''))):
            html+='<fieldset><legend>Leverantör '+str(i+1)+'</legend>'
            from riskanalys.intag.analysformular import grundtyp
            html+=''.join(_kontroll(f'leverantorer.{i}.'+k,grundtyp(f.annotation),getattr(l,k),d) for k,f in m.Leverantorsprovning.model_fields.items())+'</fieldset>'
    html+=falt('forfattare','Ditt namn eller lokala person-ID',d.get('forfattare',p.forfattare or ''),required=True)
    return html+'<button>Spara gemensamt analysunderlag</button></form><p>Sparandet skapar inget analysgodkännande. Ändringar gör tidigare tillämpningar inaktuella.</p>'


def tillampningar(rb,profil,bedomning,paket,tjanst,prefix,csrf,revision,data=None):
    d=data or {};a=hamta_tjanst(paket,tjanst)
    t=next(t for t in bedomning.tjanster if t.tjanst==tjanst)
    html='<h1>2. Tjänstens tillämpning</h1><p>Välj ställningstagande och visa det före sparning om avvikelsefälten behöver ändras. Pröva gemensamma förhållanden mot tjänstens arbetsmoment och hot. Motorns risknivå och åtgärdsgrund ändras inte av en lägre lokal bedömning.</p>'
    batch=_form(prefix,'analysbekraftatillampningar',csrf,revision,(('tjanst',tjanst),))
    i=0
    for slag,poster,appar in (('sarbarhet',paket.gemensamma_sarbarhetsprovningar,a.sarbarhetstillampningar),('verksamhet',paket.gemensamma_verksamhetsposter,a.verksamhetstillampningar)):
        for p in poster:
            app=next((x for x in appar if x.post==p.id),None)
            text=getattr(p,'beskrivning',getattr(p,'text',''))
            html+='<section><h2>'+e(p.id)+'</h2><p>'+e(p.status)+': '+e(text)+'</p><p>'+e(getattr(p,'motivering',''))+'</p><p>Belägg: '+e(', '.join(p.belagg))+'</p>'
            oforandrad=app is None or app.stallningstagande=='galler'
            if oforandrad:
                batch+='<label class="check"><input type="checkbox" name="val.'+str(i)+'" value="'+e(slag+'/'+p.id,quote=True)+'"> Gäller oförändrat: '+e(p.id)+'</label>'+dold('summa.'+str(i),postsumma(p))
            i+=1
            eget=d if d.get('post')==p.id else {}
            start=len(html)
            html+=_form(prefix,'analystillampning',csrf,eget.get('revision',revision),(('tjanst',tjanst),('slag',slag),('post',p.id),('postsumma',postsumma(p))))
            eget=d if d.get('post')==p.id else {}
            stallning=eget.get('stallningstagande',app.stallningstagande if app else 'otillrackligt')
            html+=val('stallningstagande','Hur berör förhållandet tjänsten?',[(v,txt) for v,txt in (
                ('galler','Gäller oförändrat'),('galler_annorlunda','Gäller annorlunda'),('beror_inte','Berör inte tjänsten'),('otillrackligt','Otillräckligt underlag'))],stallning)
            if stallning!='galler':
                html+='<details'+(' open' if stallning!='galler' else '')+'><summary>Lokal avvikelse: motivering och belägg</summary>'
                html+=_kontroll('motivering',str,app.motivering if app else '',eget)+_kontroll('belagg',tuple[str,...],app.belagg if app else (),eget,katalogval(rb,paket))+'</details>'
            if slag=='sarbarhet':
                html+=falt('hotkopplingar','Uttrycklig ytterligare hotkoppling (hot-ID/pt, hot-ID/tf). Lämna tomt utan särskilt påstående.',eget.get('hotkopplingar',', '.join(x.hot+'/'+x.dimension for x in app.hotkopplingar) if app else ''))
                if stallning=='galler_annorlunda':
                    valj=app.riktningsval if app and app.riktningsval else m.Riktningsval()
                    html+=val('riktningsval.riktning','Byråns prövade riktning (oklar spärrar)',[(x,x.replace('_',' ')) for x in ('oklar','lagre','mojlig_underskattning')],eget.get('riktningsval.riktning',valj.riktning))
                    html+=_kontroll('riktningsval.motivering',str,valj.motivering,eget)+_kontroll('riktningsval.belagg',tuple[str,...],valj.belagg,eget,katalogval(rb,paket))
            html+=falt('forfattare','Ditt namn eller lokala person-ID',eget.get('forfattare',a.forfattare or ''),required=True)+'<button name="operation" value="visa" formnovalidate>Visa valt ställningstagande</button><button name="operation" value="spara">Spara och bekräfta visad tillämpning</button></form></section>'
            html=html[:start]+_unika_dom(html[start:],'app'+str(i))
    html+='<h2>Bekräfta markerade oförändrade tillämpningar samlat</h2>'+_unika_dom(batch,'samlad')+falt('forfattare','Ditt namn eller lokala person-ID',a.forfattare or '',required=True)+'<button>Bekräfta enbart markerade gäller-poster</button></form><p>Avvikelser skrivs aldrig över. Osäker sakstatus ändras inte.</p>'
    html+='<h2>Härledd riktning per hot och dimension</h2><ul>'
    for r in harled_riktningar(rb,profil,paket,t):html+='<li>'+e(f'{r.post} · {r.sarbarhet or "egen sårbarhet"} · {r.hot} · {r.dimension}: {r.riktning}. {r.motivering}')+'</li>'
    html+='</ul><h2>Täckning av egna sårbarheter</h2><ul>'
    for ursprung,post,hot,dim in egna_ansprak(rb,paket,t):
        for riskled in kravda_riskled(t,hot,dim):
            href=prefix+'analys?'+urlencode({'tjanst':tjanst,'tackning':'ja','ursprung':ursprung,'post':post,'hot':hot,'dimension':dim,'riskled':riskled})
            html+='<li><a href="'+e(href,quote=True)+'">Pröva täckning: '+e(post+' · '+hot+' · '+dim+' · '+riskled.replace('kvarstaende','kvarstående'))+'</a></li>'
    return html+'</ul>'


def tackningsformular(rb,paket,t,prefix,csrf,revision,query=None,data=None,provning=None):
    from riskanalys.analys.provning import effektiva_scenarier
    q=query or {};d=data or {};a=hamta_tjanst(paket,t.tjanst)
    p=provning
    if p is None:
        nyckel=(q.get('ursprung',['gemensam'])[0],q.get('post',[''])[0],q.get('hot',[''])[0],q.get('dimension',['pt'])[0],q.get('riskled',['inneboende'])[0])
        p=next((p for p in a.tackningsprovningar if (p.ursprung,p.post,p.hot,p.dimension,p.riskled)==nyckel),None) or m.Tackningsprovning(ursprung=nyckel[0],post=nyckel[1],hot=nyckel[2],dimension=nyckel[3],riskled=nyckel[4])
    scenarier,_=effektiva_scenarier(paket,a)
    html='<h1>Täckningsprövning av egen sårbarhet</h1><p>Hot och dimension: '+e(p.hot+' · '+p.dimension)+'</p>'
    referens=referensniva(rb,None,t,p.hot,p.dimension,p.riskled)
    html+='<p>'+e(REFERENS)+': '+e(referens or 'Otillräckligt underlag för referens')+'. Samma kontrollantaganden vid kvarstående risk; deras giltighet måste fortfarande sakprövas.</p>'
    html+=_form(prefix,'analystackning',csrf,d.get('revision',revision),(('tjanst',t.tjanst),('ursprung',p.ursprung),('post',p.post),('hot',p.hot),('dimension',p.dimension)))
    html+=_falt(m.Tackningsprovning,p,utan=('ursprung','post','hot','dimension','visad_summa','forfattare','lokalt_scenario','jamforelseniva'),kataloger=katalogval(rb,paket),data=d)
    html+=val('lokalt_scenario','Scenario som täcker mekanismen',[(s.id,s.rubrik) for s in scenarier.values()],p.lokalt_scenario or '')
    html+=val('jamforelseniva','Byråns jämförelsenivå',[(v,v) for v in ('låg','måttlig','hög','mycket hög')],p.jamforelseniva or '')
    html+=falt('forfattare','Den som prövar täckningen',p.forfattare or a.forfattare or '',required=True)
    if provning is not None:html+=dold('visad_summa',tackningssumma(rb,paket,t,p))
    else:html+=dold('visad_summa',p.visad_summa or '')
    return html+'<button name="operation" value="visa">Visa prövningen och aktuell referens</button><button name="operation" value="spara">Spara och bekräfta den visade prövningen</button></form><p>Ett val under referensen kräver uttrycklig referensmotivering och sakgranskning. Detta är ingen fri tjänstenivå.</p>'
