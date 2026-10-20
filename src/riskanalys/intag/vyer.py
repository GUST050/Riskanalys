"""HTML utan externa resurser. Allt dynamiskt innehåll escapes."""
from datetime import date
from html import escape as e
from urllib.parse import urlencode
from riskanalys.fel import RiskanalysFel
from riskanalys.intag.fragor import fragor
from riskanalys.intag.fordelning import faltkoppling
from riskanalys.profil.hantering import visa_varde_klartext
from riskanalys.regelverk.granser import metodgranser, metodgransindex
from riskanalys.profil.modeller import Uppgift
from riskanalys.profil.omfattning import kompatibilitetsvy
from riskanalys.regelverk.tillsyn import LAN_PER_OMRADE
from riskanalys.intag.tjanst import profilrevision

CSS='''body{margin:0;background:#f4f6f5;color:#172d29;font:17px/1.55 system-ui,sans-serif}main{max-width:850px;margin:32px auto;padding:28px;background:white;border-radius:12px}h1{font-size:1.9rem;line-height:1.25}h2{font-size:1.2rem}label{display:block;font-weight:650;margin-top:18px}input,select,textarea{box-sizing:border-box;width:100%;padding:12px;border:1px solid #60766f;border-radius:5px;font:inherit}textarea{min-height:125px}button,.button{display:inline-block;background:#14634f;color:white;border:0;border-radius:5px;padding:12px 20px;font:inherit;cursor:pointer;margin:20px 0}a{color:#075d8d}nav{display:flex;gap:24px;margin-bottom:24px}.hint{color:#405951}.error{padding:16px;border:3px solid #ad2b21;background:#fff4f3}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:12px 8px;border-bottom:1px solid #cdd6d2;vertical-align:top;overflow-wrap:anywhere}details{margin:20px 0}small{font-size:.88rem}.tag{font-weight:bold}progress{width:100%;height:16px}*:focus-visible{outline:3px solid #f8ba45;outline-offset:3px}'''

CSS += '.tjanster{display:grid;grid-template-columns:1fr 1fr;gap:18px}.tjanster .check{margin:0}nav{flex-wrap:wrap;gap:12px 24px}main{max-width:920px;box-shadow:0 6px 30px #173d2a08}input[type=checkbox]{width:auto;flex:none;margin:6px 0;accent-color:#14634f}.check{display:flex;align-items:flex-start;gap:12px;font-weight:500}.proposal{padding:16px 20px;margin:14px 0;border:1px solid #cbded6;border-radius:10px;background:#f5faf7}.proposal label{margin-top:0}.proposal p{margin:8px 0}.identity{padding:14px 20px;background:#e9f2ed;border-radius:10px}.identity h2{font-size:1.35rem;margin:0}.identity p{margin:6px 0}.eyebrow{color:#405951;font-size:.9rem}.metadata{border-top:1px solid #dbe3df;padding-top:12px}.fields{display:grid;grid-template-columns:2fr 1fr;gap:20px}.fields label{margin-top:0}summary{cursor:pointer;color:#075d8d;padding:6px 0}button:hover{background:#104c3d}@media(max-width:650px){.tjanster{grid-template-columns:1fr}main{margin:12px;padding:20px}h1{font-size:1.65rem}nav{font-size:.9rem}.fields{grid-template-columns:1fr;gap:12px}th,td{padding:8px 4px}}'

def foreslagen_roll(profil,sessionsroll=''):
    if sessionsroll:return sessionsroll
    if profil is None:return ''
    for u in reversed(tuple(profil.uppgifter.values())):
        if u.status=='bekräftad' and not u.inaktuell and (u.bekraftad_av or '').startswith('roll:'):
            return u.bekraftad_av.removeprefix('roll:')
    return ''


def sida(s, innehall, fel=''):
    tjanstelank=f'<a href="{s.prefix}tjanster">Byråns tjänster</a>' if s.tjanst.finns() else ''
    if s.tjanst.finns():tjanstelank+=f'<a href="{s.prefix}analys">Lokal verksamhetsanalys</a>'
    if s.tjanst.finns():tjanstelank+=f'<a href="{s.prefix}samlat">Samlade frågor</a>'
    varning=f'<div class="error" role="alert"><h2>Kontrollera svaret</h2>{e(str(fel))}</div>' if fel else ''
    return f'<!doctype html><html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Riskanalys – intag</title><style>{CSS}</style></head><body><main><nav><a href="{s.prefix}">Fortsätt intaget</a><a href="{s.prefix}?oversikt=1">Svar och kompletteringar</a><a href="{s.prefix}register">Företagsuppgifter</a>{tjanstelank}</nav>{varning}{innehall}<hr><small>Uppgifter sparas på den här datorn. Namn och fritext skickas inte till AI. Stäng terminalen med Ctrl+C när du är klar.</small></main></body></html>'


def dold(n,v):return f'<input type="hidden" name="{e(n)}" value="{e(str(v),quote=True)}">'


def falt(n,label,v='',typ='text',required=False,html_id=None):
    id=html_id or n
    maxlangd={'roll':200,'kalla':2000,'filialkalla':2000,'motivering':2000,'nyckel':4096}.get(n)
    langd=f'maxlength="{maxlangd}"' if maxlangd else ''
    return f'<label for="{e(id)}">{e(label)}</label><input id="{e(id)}" name="{e(n)}" type="{typ}" value="{e(str(v),quote=True)}" {"required" if required else ""} {langd}>'


def val(n,label,alternativ,v=''):
    options='<option value="">Välj…</option>'+''.join(f'<option value="{e(str(k),quote=True)}" {"selected" if str(k)==str(v) else ""}>{e(str(text))}</option>' for k,text in alternativ)
    return f'<label for="{e(n)}">{e(label)}</label><select id="{e(n)}" name="{e(n)}">{options}</select>'


def leverans():
    return '<section class="identity"><h2>Allmän riskbedömning</h2><p>Du tar fram byråns allmänna riskbedömning som Word-utkast: verksamhet, risker per tjänst, kontroller och åtgärder.</p><details><summary>Vad kommer att skapas?</summary><p>Word-utkastet behöver sakgranskas och fastställas separat. Rutindokument och individuella kundbedömningar är separata leveranser och skapas inte i detta intag.</p></details></section>'


def grund(s,data=None,fel=''):
    d=data or {}
    counties=sorted(l for ls in LAN_PER_OMRADE.values() for l in ls)
    html='<h1>Börja med byråns grunduppgifter</h1>'+leverans()+'<p>Programmet frågar sedan efter tjänster, kunder, arbetssätt, riskförhållanden och kontrollbelägg. Du kan avbryta och återuppta när som helst.</p>'
    from riskanalys.intag.registervy import hamtform
    html+=hamtform(s,data)+'<details><summary>Börja med egna grunduppgifter</summary>'
    html+=f'<form method="post" action="{s.prefix}skapa" autocomplete="off">'+dold('csrf',s.csrf)+dold('revision','')
    html+=val('lan','Byråns sätes- eller folkbokföringslän',[(l,l) for l in counties],d.get('lan',''))
    html+=val('filial','Är detta en filial till ett utländskt företag?',[('ja','Ja'),('nej','Nej')],d.get('filial',''))
    html+=falt('datum','Bedömningsdatum',d.get('datum',date.today()),'date',True)
    html+=falt('kalla','Vad grundar du uppgifterna på? Exempel: registreringsbevis',d.get('kalla',''),required=True)
    html+=falt('roll','Din funktion eller roll',d.get('roll',''),required=True)
    return sida(s,html+'<button>Börja intaget</button></form></details>',fel)


def fragesida(s,id=None,data=None,fel=''):
    p=s.tjanst.profil();qs=fragor(s.tjanst.rb,p)
    q=next((q for q in qs if q.falt.id==id),None) if id else next((q for q in qs if q.falt.intag.obligatorisk and not q.besvarad and p.uppgifter.get(q.falt.id,Uppgift()).status!='föreslagen'),None)
    if not q:return oversikt(s,fel,p,qs)
    from riskanalys.intag.samlade import grupp_for, hamta_grupp
    from riskanalys.intag.samladvy import samladsida, grupplank
    grupp = grupp_for(s.tjanst.rb, q.falt)
    if id is None and grupp and len(hamta_grupp(s.tjanst.rb, p, grupp).falt) > 1:
        return samladsida(s, grupp)
    f=q.falt;u=kompatibilitetsvy(p,s.tjanst.rb).uppgifter.get(f.id,Uppgift());d=data if data is not None else {}
    gransindex=metodgransindex(s.tjanst.rb)
    value=d.get('text',visa_varde_klartext(f,u.varde,metodgranser(s.tjanst.rb,f.id,gransindex)) if u.varde is not None else '')
    t=s.tjanst.oversikt(p)
    nu=sum(q.falt.intag.obligatorisk and not q.besvarad and p.uppgifter.get(q.falt.id,Uppgift()).status!='föreslagen' for q in qs)
    html=f'<p class="eyebrow">3. Komplettera verksamheten</p><p class="hint">{t.besvarade} uppgifter bekräftade · {nu} frågor att besvara nu. Följdfrågor anpassas efter dina tjänster; okända svar finns i översikten.</p><progress value="{t.besvarade}" max="{max(t.antal,1)}"></progress><h1>{e(f.fraga)}</h1><p class="hint">{e(f.varfor)}</p>'
    if grupp:
        html += f'<p><a href="{e(grupplank(s.prefix, grupp), quote=True)}">Besvara närliggande frågor tillsammans</a></p>'
    if not f.intag.obligatorisk:
        html += '<p class="hint">Svaret är valfritt inför utkastet. Du kan lämna frågan obesvarad och fortsätta via översikten.</p>'
    if f.intag:
        kallsidor='; '.join(f'<a href="{e(s.tjanst.rb.kallor[k].url,quote=True)}" rel="noreferrer" target="_blank">{e(s.tjanst.rb.kallor[k].titel)}</a>' for k in f.intag.kallor if k in s.tjanst.rb.kallor)
        html+=f'<details><summary>Frågans källor och användning</summary><p>Svaret används i riskbedömningens avsnitt {e(", ".join(id.removeprefix("D-ARB.") for id in f.intag.avsnitt))}. Källstöd: {kallsidor}.</p><p>Frågekopplingen visar vilket underlag som behövs; den är inget intyg om att kraven är uppfyllda.</p></details>'
    if u.status=='föreslagen' and u.varde is not None:
        html+=f'<p class="hint">Tidigare värde och belägg visas nedan för spårbarhet. Tidigare beläggsdatum: {e(str(u.datum or "saknas"))}. Uppgiften är okänd tills den bekräftas igen.</p>'
    if u.inaktuell:html+='<p class="error">Grunduppgifter har ändrats. Kontrollera det tidigare svaret och dess källa igen.</p>'
    from riskanalys.foretagsdata.lagring import las_bild
    from riskanalys.intag.registervy import inlineforslag
    try:
        b=las_bild(s.tjanst.mapp)
        if b:html+=inlineforslag(s,b,p,f.id)
    except RiskanalysFel:
        html+=f'<p>Registerunderlaget behöver kontrolleras på <a href="{s.prefix}register">företagssidan</a>. Du kan ange ett eget svar här.</p>'
    erbjudandefalt={t.erbjuds_falt for t in s.tjanst.rb.tjanster.values()}
    if f.id in erbjudandefalt:
        from riskanalys.intag.tjanstvy import lista
        html+=lista(s,p)+'<details><summary>Besvara tjänsterna en i taget</summary>'
    html+=f'<form method="post" action="{s.prefix}svar" autocomplete="off">'+dold('csrf',s.csrf)+dold('revision',d.get('revision',profilrevision(p)))+dold('falt',f.id)
    if f.typ=='flerval':
        from riskanalys.intag.flervalsvy import flervalsrutor, formularval, sparade_val
        html+=flervalsrutor(s.tjanst.rb,f,formularval(d) if data is not None else sparade_val(u.varde))
    elif f.typ in ('bool','val'):
        choices=[('ja','Ja'),('nej','Nej')] if f.typ=='bool' else [(v,v.replace('_',' ')) for v in f.val]
        html+=val('text','Ditt svar',choices,value)
    elif f.id=='P-ORG.namn':
        html+=falt('text','Byråns namn',value)
    elif f.typ=='text':
        html+=f'<label for="text">Ditt svar</label><textarea id="text" name="text" maxlength="12000">{e(value)}</textarea>'
    else:html+=falt('text','Ditt svar'+(' ('+f.enhet+')' if f.enhet else ''),value,'date' if f.typ=='datum' else 'text')
    html+=val('status','Kan uppgiften bekräftas?',[('bekräftad','Jag bekräftar uppgiften'),('okänt','Vet inte – kompletterar senare')],d.get('status','bekräftad'))
    from riskanalys.intag.underlag import periodforslag
    from riskanalys.intag.underlagsvy import underlagsval
    period=u.period if u.period else periodforslag(s.tjanst.rb,p,f)
    html+=underlagsval(s,p,f,data,u,period)
    roll=d.get('roll',(u.bekraftad_av or '').removeprefix('roll:') or foreslagen_roll(p,getattr(s,'rollforslag','')))
    html+='<details class="metadata"'+(' open' if data is not None or not roll else '')+'><summary>Bekräftas av '+e(roll or 'ange din funktion')+' · datum och funktion</summary><div class="fields"><div>'
    html+=falt('roll','Vem eller vilken funktion bekräftar?',roll)+'</div><div>'
    html+=falt('datum','Bekräftelsedatum',d.get('datum',date.today()),'date',True)+'</div></div></details>'
    if f.periodkrav:
        html+='<p>Statistik ska avse samma period som kundbasen respektive byråns omsättning. Andelar beräknas automatiskt.</p>'
        html+=falt('period_fran','Periodens start',d.get('period_fran',period.fran if period else ''),'date')+falt('period_till','Periodens slut',d.get('period_till',period.till if period else ''),'date')
    html+='<details'+(' open' if d.get('status')=='okänt' else '')+'><summary>Vet inte? Beskriv vad som behöver kontrolleras</summary>'+falt('motivering','Vad behöver kontrolleras?',d.get('motivering',u.motivering or ''))+'</details>'
    html+='<button>Spara och fortsätt</button></form>'
    if f.id in erbjudandefalt:html+='</details>'
    return sida(s,html,fel)


def oversikt(s,fel='',profil=None,qs=None):
    p=profil if profil is not None else s.tjanst.profil();t=s.tjanst.oversikt(p);qs=qs if qs is not None else fragor(s.tjanst.rb,p)
    vy=kompatibilitetsvy(p,s.tjanst.rb)
    title='Underlag klart för utkast' if t.komplett else 'Sparade svar och kompletteringar'
    html=f'<h1>{title}</h1>'+leverans()+f'<p>{t.besvarade} av {t.antal} aktuella frågor besvarade. Svaren är sparade och kan ändras nedan.</p>'
    if t.saknade:
        html+='<p>Fortsätt intervjun för att komplettera underlaget. Programmet kontrollerar sedan svaren tillsammans inför skrivningen.</p>'
    if t.hinder:
        html+=f'<details {"open" if not t.saknade else ""}><summary>Kontroller som behöver hanteras</summary><ul>'+''.join(f'<li>{e(h)}</li>' for h in t.hinder)+'</ul></details>'
    html+='<h2>Dina svar</h2><table><thead><tr><th>Fråga</th><th>Svar och status</th><th></th></tr></thead><tbody>'
    gransindex=metodgransindex(s.tjanst.rb)
    for q in qs:
        u=vy.uppgifter.get(q.falt.id,Uppgift())
        value=visa_varde_klartext(q.falt,u.varde,metodgranser(s.tjanst.rb,q.falt.id,gransindex)) if u.varde is not None else 'Saknas'
        status='Behöver kontrolleras igen' if u.inaktuell else u.status
        if faltkoppling(s.tjanst.rb, q.falt.id) and u.status == 'bekräftad' and not q.besvarad:
            status = 'Behöver bekräftas på nytt'
        if not q.falt.intag.obligatorisk:status += ' (frivilligt inför utkast)'
        html+=f'<tr><td>{e(q.falt.fraga)}</td><td>{e(value)}<br><small>{e(status)}; {e(u.kalla or u.motivering or "")}</small></td><td><a href="{s.prefix}?{urlencode({"falt":q.falt.id})}">Ändra<span class="hint"> svar</span></a></td></tr>'
    html+='</tbody></table>'
    if t.komplett:
        html+='<h2>Skapa allmän riskbedömning som Word-utkast</h2><p>AI skriver riskavsnitten från tillåtna strukturerade uppgifter. Ett API-anrop till Claude kan kosta pengar. Beskrivningar sätts in lokalt. Resultatet är ett Word-utkast med granskningsbilaga vid öppna fynd.</p>'
        html+=f'<form method="post" action="{s.prefix}skriv">'+dold('csrf',s.csrf)+dold('revision',profilrevision(p))+dold('skrivtoken',s.skrivtoken(profilrevision(p)))+'<button>Skapa Word-utkast med Claude</button></form>'
    if s.utkast:
        html+=f'<p><a class="button" href="{s.prefix}word">Hämta Word-rapport</a></p>'
        if (s.utkast.parent/'underlagsbilaga-UTKAST.docx').is_file():
            html+=f'<p><a class="button" href="{s.prefix}underlag">Hämta underlagsbilaga</a></p><p>Läs båda delarna tillsammans för fullständig dokumentation.</p>'
        html+='<p>Efter ändringar i lokal analys eller utvärdering kan du granska och uppdatera Word från befintlig AI-text. Ändrade verksamhetsfakta kräver en ny skrivning.</p>'
        html+=f'<form method="post" action="{s.prefix}uppdaterautkast">'+dold('csrf',s.csrf)+dold('revision',profilrevision(p))+'<button>Uppdatera Word-utkast utan nya AI-anrop</button></form>'
    from riskanalys.drift.historik import las_historik
    historik=las_historik(s.tjanst.mapp)
    html+='<h2>Utvärdering och uppföljning</h2>'
    if historik.senaste_utvardering():
        html+=f'<p>Senast registrerad utvärdering: {historik.senaste_utvardering()}. Nästa genomgång senast {historik.nasta_genomgang()}.</p>'
    else:
        html+='<p>Datum för faktisk utvärdering saknas. Ett första utkast kan skapas; utvärdering måste genomföras och registreras före fastställelse.</p>'
    html+='<details><summary>Registrera genomförd utvärdering</summary><p>Använd detta bara för en utvärdering som faktiskt genomförts. Att fylla i intaget eller skapa text räknas inte automatiskt som en utvärdering.</p>'
    html+=f'<form method="post" action="{s.prefix}utvardera">'+dold('csrf',s.csrf)+dold('revision',profilrevision(p))
    html+=falt('datum','Datum för genomförd utvärdering','','date',True)+falt('beskrivning','Vad omfattade utvärderingen och vad ledde den till?',required=True)
    html+='<button>Registrera genomförd utvärdering</button></form></details>'
    html+='<h2>Utkastets fortsatta hantering</h2><p>Underlagets fullständighet är ingen juridisk attest. Öppna frågor och dokumentets innehåll ska sakgranskas innan fastställelse. Programmet skapar inga sakkunniggodkännanden.</p>'
    if s.kompletteringar:
        html+='<ul>'
        for avsnitt,o in s.kompletteringar:
            from riskanalys.intag.komplettering import fragefalt
            ids=fragefalt(s.tjanst.rb,o.saknad_uppgift)
            link='; '.join(f'<a href="{s.prefix}?{urlencode({"falt":id})}">{e(s.tjanst.rb.falt[id].fraga)}</a>' for id in ids) if ids else 'Frågan behöver hanteras i sakgranskningen.'
            html+=f'<li>{e(o.fraga)} ({e(avsnitt)}). {link} Kör skrivkedjan igen efter rättning.</li>'
        html+='</ul>'
    return sida(s,html,fel)
