"""Engångsunderlag och en genomgång per tjänst; lokal redigering är separat."""
import json
from html import escape as e
from urllib.parse import urlencode
from riskanalys.analys.engangssvar import visade_celler
from riskanalys.analys.gemensam import effektiv_tjanst,tillampning_aktuell
from riskanalys.analys.provning import BLOCKFALT
from riskanalys.intag.vyer import dold,falt


def helhet(paket,bedomning,prefix,csrf,revision):
    ids=tuple(t.tjanst for t in bedomning.tjanster if t.erbjuds is True and any(a.tjanst==t.tjanst for a in paket.tjanster))
    if not ids:return '<p>Bekräfta tjänsteutbudet före gemensam bekräftelse.</p>'
    celler=visade_celler(paket,ids)
    html='<h2>Automatisk återanvändning</h2><p>De gemensamma svaren används i följande tjänster. Kontrollera urvalet och oförändrade tillämpningar nedan. Ändra tjänsteurvalet i intaget. Lokala undantag lämnas kvar och behöver prövas separat.</p><ul>'
    for id in ids:
        a=next(a for a in paket.tjanster if a.tjanst==id)
        html+='<li>'+e(id)+': '+e(', '.join(c.post for c in celler if c.tjanst==id))
        undantag=[x.post+' ('+x.stallningstagande+')' for x in (*a.sarbarhetstillampningar,*a.verksamhetstillampningar) if x.stallningstagande!='galler']
        html+='; undantag: '+e(', '.join(undantag) or 'inga')+'</li>'
    html+='</ul><form method="post" action="'+e(prefix+'analysbekraftabyraunderlag',quote=True)+'">'
    for key,value in (('csrf',csrf),('revision',revision),('tjanster',','.join(ids)),
        ('celler',json.dumps([c.model_dump() for c in celler],ensure_ascii=False))):html+=dold(key,value)
    html+=falt('forfattare','Ditt namn eller lokala person-ID','',required=True)
    return html+'<label><input type="checkbox" name="bekrafta" value="ja" required> Jag har gått igenom de visade oförändrade tillämpningarna</label><button>Bekräfta gemensamt underlag för valda tjänster</button></form><p>Detta skapar inga analysgodkännanden och ändrar inte antaganden till bekräftade fakta.</p>'


def genomgang(rb,profil,bedomning,paket,tjanst,prefix,csrf,revision):
    from riskanalys.intag.analysvy import _lasbar,_etikett
    from riskanalys.analys.engangssvar import bygg_tjanstbekraftelse,visade_scenarioval,tjanstefakta
    from riskanalys.fel import RiskanalysFel
    from riskanalys.analys.provning_v2 import egna_ansprak,kravda_riskled
    from riskanalys.analys.riktning import harled_riktningar
    a=next((a for a in paket.tjanster if a.tjanst==tjanst),None)
    t=next((t for t in bedomning.tjanster if t.tjanst==tjanst),None)
    if a is None or t is None:raise RiskanalysFel('Välj en tjänst ur analysöversikten.')
    html='<h1>Samlad tjänstegenomgång: '+e(rb.tjanster[tjanst].namn)+'</h1><p>Gemensamma fakta återanvänds. Läs tjänstens betydelse, lokala svar och scenarier nedan. Knappen bekräftar underlaget; analysgodkännande och sakgranskning görs separat.</p>'
    html+='<p>Motorns PT: '+e(t.inneboende.risk if t.inneboende else 'okänt')+'; kvarstående: '+e(t.kvarstaende or 'okänt')+'; TF: '+e(t.terrorfinansiering.risk if t.terrorfinansiering else 'okänt')+'.</p>'
    html+='<h2>Redan besvarade tjänstefrågor</h2><p>Bekräftade fakta från tjänstebeskrivningen och intaget används direkt. De ska inte skrivas om i analysen.</p><dl>'
    for id,etikett,varde,kalla,datum,period,ansvarig in tjanstefakta(rb,profil,tjanst):
        html+='<dt>'+e(etikett)+'</dt><dd>'+e(varde)+' · '+e(str(kalla or ''))+' · '+e(str(datum or ''))+' · '+e((period.fran.isoformat()+'–'+period.till.isoformat()) if period else '')+' · '+e(str(ansvarig or ''))+'</dd>'
    html+='</dl><h2>Gemensamma källor</h2><ul>'
    for slag,poster,appar in (('sarbarhet',paket.gemensamma_sarbarhetsprovningar,a.sarbarhetstillampningar),('verksamhet',paket.gemensamma_verksamhetsposter,a.verksamhetstillampningar)):
        for p in poster:
            app=next((x for x in appar if x.post==p.id),None)
            url=prefix+'analys?'+urlencode({'byraanalys':'ja','post':p.id,'slag':slag})
            html+='<li><a href="'+e(url,quote=True)+'">'+e(p.id)+'</a> · '+e(p.status)+' · '+e(app.stallningstagande if app else 'saknar tillämpning')+' · '+('aktuellt' if app and tillampning_aktuell(p,app) else 'bekräfta gemensamt först')+'</li>'
            if app and app.stallningstagande!='galler':
                html+='<li>Lokal motivering: '+e(app.motivering)+' · Belägg: '+e(', '.join(app.belagg))+'</li>'
            if app and getattr(app,'riktningsval',None):html+='<li>'+e(_lasbar(app.riktningsval))+'</li>'
            if app and getattr(app,'hotkopplingar',()):html+='<li>Uttrycklig hotkoppling: '+e(_lasbar(app.hotkopplingar))+'</li>'
    html+='</ul><p><a href="'+e(prefix+'analys?'+urlencode({'tjanst':tjanst,'tillampningar':'ja'}),quote=True)+'">Pröva lokala undantag</a></p>'
    effektiv=effektiv_tjanst(paket,tjanst)
    from riskanalys.analys.guide import guideblock
    rubriker={b.nummer:b.rubrik for b in guideblock(a)}
    for n,namn in BLOCKFALT.items():
        html+='<section><h2>'+str(n)+'. '+e(rubriker[n])+'</h2>'
        delade=set()
        for key in namn:
            # Gemensamma sakfrågor redigeras en gång. Lokala avvikelser visas i tillämpningen.
            if key=='scenariokopplingar':continue
            delad=delad_verksamhetspost(paket,a,key)
            if delad:
                if delad.id not in delade:
                    html+='<p>Återanvänds från gemensamt underlag: '+e(delad.id)+'. Lokala undantag prövas separat.</p>'
                    delade.add(delad.id)
                continue
            value=getattr(effektiv,key)
            if key=='sarbarhetsprovningar':
                value=tuple(x for x in value if not x.id.startswith('gemensam:'))
                if not value:
                    html+='<p>Gemensamma sårbarheter återanvänds från källorna ovan. Inga lokala tillägg är registrerade.</p>'
                    continue
            html+='<p><strong>'+e(_etikett(key))+'</strong>: '+e(_lasbar(value))+'</p>'
        html+='<a href="'+e(prefix+'analys?'+urlencode({'tjanst':tjanst,'block':n}),quote=True)+'">Komplettera lokala uppgifter</a></section>'
    html+='<h2>Visade gemensamma scenarier</h2>'
    for k in visade_scenarioval(rb,paket,tjanst):
        s=next((s for s in paket.gemensamma_scenarier if s.id==k.scenario),None)
        if s:html+='<article><h3>'+e(s.rubrik)+'</h3><p>'+e(s.handelseforlopp)+'</p><p>'+e(s.relevans+': '+s.motivering)+' · Belägg: '+e(', '.join(s.belagg))+'</p><p>Tillämpning: '+e(k.tillampning)+' '+e(k.motivering or '')+'</p></article>'
    html+='<h2>Faktorernas betydelse per hot och dimension</h2><ul>'
    for r in harled_riktningar(rb,profil,paket,t):html+='<li>'+e(r.post+' · '+(r.sarbarhet or 'egen sårbarhet')+' · '+r.hot+' · '+r.dimension+': '+r.riktning+'. '+r.motivering)+'</li>'
    html+='</ul><h2>Separata täckningsprövningar</h2><ul>'
    for ursprung,post,hot,dim in egna_ansprak(rb,paket,t):
        for s in paket.gemensamma_scenarier:
            if hot in s.hot:
                url=prefix+'analys?'+urlencode(dict(tjanst=tjanst,scenario=s.id))
                html+='<li><a href="'+e(url,quote=True)+'">Bekräfta det bärande scenariot före täckningsprövningen: '+e(s.rubrik)+'</a></li>'
        for riskled in kravda_riskled(t,hot,dim):
            url=prefix+'analys?'+urlencode(dict(tjanst=tjanst,tackning='ja',ursprung=ursprung,post=post,hot=hot,dimension=dim,riskled=riskled))
            html+='<li><a href="'+e(url,quote=True)+'">'+e(post+' · '+hot+' · '+dim+' · '+riskled)+'</a></li>'
    html+='</ul>'
    for prov in a.tackningsprovningar:
        html+='<details><summary>Registrerad täckningsprövning: '+e(prov.post+' · '+prov.hot+' · '+prov.dimension+' · '+prov.riskled)+'</summary><p>'+e(_lasbar(prov))+'</p></details>'
    try:bygg_tjanstbekraftelse(rb,profil,bedomning,paket,tjanst,a.forfattare or 'Förhandskontroll')
    except RiskanalysFel as exc:html+='<p class="fel">'+e(str(exc))+'</p>'
    html+='<form method="post" action="'+e(prefix+'analysbekraftatjansteunderlag',quote=True)+'">'
    for key,value in (('csrf',csrf),('revision',revision),('tjanst',tjanst)):html+=dold(key,value)
    html+=falt('forfattare','Ditt namn eller lokala person-ID',a.forfattare or '',required=True)
    return html+'<label><input type="checkbox" name="bekrafta" value="ja" required> Jag har gått igenom hela det visade tjänsteunderlaget och scenariovalen</label><button>Bekräfta visat tjänsteunderlag</button></form>'


def delad_verksamhetspost(paket,a,falt):
    if paket.schemaversion!=2:return None
    slag={'leverantorsmotivering':'leverantorer','leverantorer':'leverantorer',
        'erfarenhetsprovning':'erfarenhet','erfarenhetsbelagg':'erfarenhet','sanktioner':'sanktionsanknytning'}.get(falt)
    for post in paket.gemensamma_verksamhetsposter:
        app=next((x for x in a.verksamhetstillampningar if x.post==post.id),None)
        if post.slag==slag and (app is None or app.stallningstagande!='galler_annorlunda'):return post
    return None
