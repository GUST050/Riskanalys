"""Lokala planer, förändringsutvärderingar, rättelser och kombinationsgrupper."""
from datetime import date
from html import escape as e
from riskanalys.fel import RiskanalysFel
from riskanalys.intag.vyer import sida, dold, falt
from riskanalys.profil.lagring import profilrevision
from riskanalys.profil.hantering import tolka_varde, visa_varde
from riskanalys.profil.modeller import Tjansteplan, Kombinationsgrupp, Uppgift, Period
from riskanalys.profil.planering import tillatna_planfalt


def _text(namn, rubrik, varde=''):
    return f'<label>{e(rubrik)}<textarea name="{e(namn)}" rows="4" required>{e(str(varde))}</textarea></label>'


def _val(namn, alternativ, valt):
    return f'<select name="{e(namn)}">'+''.join(f'<option value="{e(k)}" {"selected" if k==valt else ""}>{e(v)}</option>' for k,v in alternativ)+'</select>'


def _form(s, p, action):
    return f'<form method="post" action="{s.prefix}{action}">'+dold('csrf',s.csrf)+dold('revision',profilrevision(p))


def planeringssida(s, query=None, data=None, fel=''):
    from riskanalys.drift.historik import las_historik
    from riskanalys.profil.planering import aktuell_planutvardering
    p=s.tjanst.profil(); rb=s.tjanst.rb; q=query or {}; d=data or {}
    plan_id=d.get('plan_id') or q.get('plan',[''])[0]
    plan=next((t for t in p.tjansteplaner if t.id==plan_id),None)
    tjanst=d.get('tjanst',plan.tjanst if plan else q.get('tjanst',[next(iter(rb.tjanster))])[0])
    if tjanst not in rb.tjanster:
        if data is None:
            raise RiskanalysFel('Välj en registrerad tjänst.')
        tjanst=plan.tjanst if plan else next(iter(rb.tjanster))
    html='<h1>Planer och kombinationsgrupper</h1><p>Underlaget stannar lokalt. Planantaganden och grupper ändrar inte motorns risknivåer. Ändringar kräver aktuell bedömning och förnyad sakprövning före fastställelse.</p>'
    html+='<h2>Registrerade planer</h2><ul>'
    h=las_historik(s.tjanst.mapp)
    for t in p.tjansteplaner:
        status='Aktuell bunden utvärdering finns' if aktuell_planutvardering(rb,p,t,h,date.today()) else 'Behöver utvärderas'
        html+=f'<li><a href="{s.prefix}planering?plan={e(t.id)}">{e(t.id)}</a>: {e(t.beskrivning)}. {status}.</li>'
    html+='</ul><h2>Planerad förändring</h2><p>Beskriv kundtyper, arbetsmoment och befogenheter, underlag och insyn, leverans och geografiska anknytningar. Planen ersätter inga aktuella uppgifter.</p>'
    html+='<p>Välj tjänst för en ny plan: '+ ' · '.join(f'<a href="{s.prefix}planering?tjanst={e(t.id)}">{e(t.namn)}</a>' for t in rb.tjanster.values())+'</p>'
    html+=_form(s,p,'plan')+dold('tjanst',tjanst)+f'<p>{e(rb.tjanster[tjanst].namn)}</p>'
    html+=falt('id','Plan-ID',d.get('id',plan.id if plan else ''),required=True)
    typer=(('ny_tjanst','Ny tjänst'),('vasentligt_andrad_tjanst','Väsentligt ändrad tjänst'),('ny_marknad','Ny marknad'),('annan_forandring','Annan relevant förändring'))
    html+=_val('typ',typer,d.get('typ',plan.typ if plan else 'ny_tjanst'))
    html+=_text('beskrivning','Beskriv förändringen',d.get('beskrivning',plan.beskrivning if plan else ''))
    html+=falt('avsett_inforande','Avsett införande (är inte genomförandedatum)',d.get('avsett_inforande',plan.avsett_inforande or '' if plan else ''),'date')
    html+='<details><summary>Planantaganden per fråga (frivilligt)</summary><p>Tomt innebär okänt. Dessa svar ersätter inte aktuell profil och påverkar inte nivån.</p>'
    for id in tillatna_planfalt(rb,tjanst):
        u=plan.uppgifter.get(id) if plan else None
        v=visa_varde(rb.falt[id],u.varde) if u and u.varde is not None else ''
        html+=falt('antagande_'+id,rb.falt[id].fraga,d.get('antagande_'+id,v))
    html+='</details>'+falt('kalla','Underlag för nya/ändrade planantaganden',d.get('kalla',''))
    html+=falt('roll','Ansvarig funktion för planantaganden',d.get('roll',''))
    html+='<p>Nytt underlag, ansvarig funktion, datum eller period bekräftar de ifyllda antagandena på nytt även när värdena är oförändrade. Lämna beläggsfälten tomma för att behålla tidigare belägg vid en beskrivningsändring.</p>'
    html+=falt('datum','Antagandenas datum',d.get('datum','' if plan else date.today()),'date')
    html+=falt('period_fran','Antagandenas period från (för antalsfält)',d.get('period_fran',''),'date')
    html+=falt('period_till','Antagandenas period till',d.get('period_till',''),'date')
    html+='<button>Spara plan</button></form>'
    if plan:
        html+='<h2>Dokumentera genomförd förändringsutvärdering</h2><p>Utvärdera den allmänna riskbedömningen med hänsyn till planen. Årsfristen ändras inte. Registreringen gör befintlig analys inaktuell; förnya och sakpröva igen.</p>'
        html+=_form(s,p,'planutvardera')+dold('plan_id',plan.id)
        for id,rubrik in (('underlag','Vilket underlag har prövats?'),('hot_sarbarheter','Vilka hot och sårbarheter berörs?'),('risk_rutiner','Hur påverkas riskbedömningen och rutinerna?'),('beslut','Vad uppdateras eller behålls, och varför?')):
            html+=_text(id,rubrik,d.get(id,''))
        html+=falt('datum','Datum för genomförd utvärdering',d.get('datum',date.today()),'date',True)
        html+='<button>Registrera genomförd utvärdering för planen</button></form>'
    html+='<h2>Deklarerade kombinationsgrupper</h2><p>Ange belagd samtidig exponering, inte ett antagande från separata marginaltal. Överlappande grupper får inte summeras till unika kunder eller uppdrag. Samma populationsmått gäller antal och bas.</p>'
    for g in p.kombinationsgrupper:
        html+=f'<p>{e(g.id)} – {e(g.tjanst)}: {e(g.beskrivning)}. {e(g.population)}; {e(g.avgransning)}.</p>'
    html+=_form(s,p,'kombinationsgrupp')+dold('tjanst',tjanst)
    html+=falt('id','Grupp-ID (samma ID ersätter gruppen)',d.get('id',''),required=True)
    html+=_val('population',(('kunder','Kunder'),('uppdrag','Uppdrag')),d.get('population','uppdrag'))
    for id,rubrik in (('avgransning','Vilka uppdrag eller kunder ingår i populationen?'),('beskrivning','Vad visar det gemensamma underlaget?'),('sarbarheter','Sårbarhets-ID:n som samverkar, separerade med komma')):
        html+=_text(id,rubrik,d.get(id,''))
    html+='<p>Tjänstens möjliga sårbarheter: '+e(', '.join(rb.tjanster[tjanst].sarbarheter))+'</p>'
    for id,rubrik in (('antal','Antal i gruppen (tomt = okänt)'),('bas','Bas i samma population (tomt = okänt)'),('kalla','Gemensam källa'),('roll','Bekräftad av/funktion')):
        html+=falt(id,rubrik,d.get(id,''),required=id in ('kalla','roll'))
    for id,rubrik in (('datum','Bekräftelsedatum'),('period_fran','Period från'),('period_till','Period till')):
        html+=falt(id,rubrik,d.get(id,date.today() if id=='datum' else ''),'date',True)
    html+='<button>Spara kombinationsgrupp</button></form>'
    html+='<h2>Rätta felregistrerat nej</h2><p>Använd bara när tjänsten redan erbjöds och nej var felregistrerat. Ett verkligt nytt införande kräver plan och utvärdering.</p>'
    html+=_form(s,p,'erbjudanderattelse')+_val('tjanst',tuple((t.id,t.namn) for t in rb.tjanster.values()),tjanst)
    html+=_text('motivering','Varför var det tidigare nejet fel?',d.get('motivering',''))
    for id,rubrik in (('kalla','Underlag som styrker det tidigare erbjudandet'),('roll','Ansvarig funktion')):
        html+=falt(id,rubrik,d.get(id,''),required=True)
    html+=falt('datum','Rättelsedatum',date.today(),'date',True)+'<button>Dokumentera rättelse från nej till ja</button></form>'
    return sida(s,html,fel)


def _period(data):
    if bool(data.get('period_fran')) != bool(data.get('period_till')):
        raise RiskanalysFel('Ange både periodens start och slut.')
    return Period(fran=data['period_fran'],till=data['period_till']) if data.get('period_fran') else None


def spara_plan(tjanst,data):
    rb=tjanst.rb; id=data.get('tjanst',''); upp={}
    gammal=next((p for p in tjanst.profil().tjansteplaner if p.id==data.get('id')),None)
    tillatna=tillatna_planfalt(rb,id)
    if set(data)-{'csrf','revision','id','tjanst','typ','beskrivning','avsett_inforande','kalla','datum','roll','period_fran','period_till'}-{'antagande_'+f for f in tillatna}:
        raise RiskanalysFel('Planformuläret innehåller otillåtna uppgifter.')
    for f in tillatna:
        text=data.get('antagande_'+f,'').strip()
        if text:
            nytt_underlag=any(data.get(k,'').strip() for k in ('kalla','roll','datum','period_fran','period_till'))
            if gammal and f in gammal.uppgifter and tolka_varde(rb.falt[f],text)==gammal.uppgifter[f].varde and not nytt_underlag:
                upp[f]=gammal.uppgifter[f]
                continue
            if not data.get('kalla','').strip() or not data.get('roll','').strip():
                raise RiskanalysFel('Planantaganden kräver underlag och ansvarig funktion.')
            period=_period(data)
            if rb.falt[f].periodkrav and period is None:
                raise RiskanalysFel('Planens antalsfält kräver en period.')
            upp[f]=Uppgift(varde=tolka_varde(rb.falt[f],text),status='föreslagen',kalla=data['kalla'],datum=date.fromisoformat(data['datum']),bekraftad_av=data['roll'],period=period)
    plan=Tjansteplan(id=data.get('id',''),tjanst=id,typ=data.get('typ',''),beskrivning=data.get('beskrivning',''),
                    avsett_inforande=data.get('avsett_inforande') or None,uppgifter=upp)
    return tjanst.spara_plan(plan,data.get('revision',''))


def spara_kombinationsgrupp(tjanst,data):
    if set(data)-{'csrf','revision','id','tjanst','population','avgransning','beskrivning','sarbarheter','antal','bas','kalla','datum','roll','period_fran','period_till'}:
        raise RiskanalysFel('Gruppformuläret innehåller okända fält.')
    def antal(id):
        return Uppgift(varde=int(data[id]),status='bekräftad',kalla=data.get('kalla',''),datum=date.fromisoformat(data['datum']),
            bekraftad_av=data.get('roll',''),period=_period(data)) if data.get(id,'').strip() else Uppgift()
    g=Kombinationsgrupp(id=data.get('id',''),tjanst=data.get('tjanst',''),population=data.get('population',''),avgransning=data.get('avgransning',''),
        beskrivning=data.get('beskrivning',''),sarbarheter=tuple(x.strip() for x in data.get('sarbarheter','').split(',') if x.strip()),antal=antal('antal'),bas=antal('bas'))
    return tjanst.spara_kombinationsgrupp(g,data.get('revision',''))
