"""Byrån bekräftar hela tjänsteförteckningen, aldrig härledd från SNI."""
from datetime import date
from html import escape as e
from riskanalys.intag.vyer import dold, falt, foreslagen_roll, sida
from riskanalys.intag.tjanst import profilrevision


def lista(s,p,data=None):
    d=data or {};html='<section class="proposal"><h2>Välj byråns tjänster på en sida</h2><p>Välj bort tjänster som inte ingår och markera osäkra rader. Förslagen sparar inga uppgifter förrän du bekräftar urvalet. SCB:s SNI-kod besvarar inte detta.</p>'
    from riskanalys.intag.planvalsvy import behov_for_erbjudanden, planvalsfalt
    from riskanalys.profil.omfattning import kompatibilitetsvy
    vy=kompatibilitetsvy(p,s.tjanst.rb)
    val={t.erbjuds_falt:(d.get('tjanst_'+t.erbjuds_falt,'bevara') if d.get('urvalsformat')=='2' else
         'ja' if d.get('tjanst_'+t.erbjuds_falt)=='ja' else 'nej') if data is not None else
         'bevara' if t.erbjuds_falt in vy.uppgifter and vy.uppgifter[t.erbjuds_falt].status!='saknas' else 'ja'
         for t in s.tjanst.rb.tjanster.values()}
    behov={b.tjanst:b for b in behov_for_erbjudanden(s,p,
        {id:v=='ja' for id,v in val.items() if v in ('ja','nej')})}
    jamfor=data is not None and d.get('revision')!=profilrevision(p)
    if jamfor:
        html+='<p class="error">Profilen har ändrats. Ditt urval och underlag är bevarade. Jämför med de nu sparade erbjudandena och planerna nedan innan du bekräftar igen.</p>'
    html+=f'<form method="post" action="{s.prefix}tjanster">'+dold('csrf',s.csrf)+dold('revision',profilrevision(p))+dold('urvalsformat','2')
    html+='<div class="tjanster">'
    for t in s.tjanst.rb.tjanster.values():
        id=t.erbjuds_falt;u=p.uppgifter.get(id)
        html+=f'<label for="tjanst-{e(t.id)}">{e(t.namn)}</label><p>{e(t.beskrivning)}</p>'
        html+=f'<select id="tjanst-{e(t.id)}" name="tjanst_{e(id)}" required>'
        for v,namn in (('bevara','Behåll sparad uppgift'),('ja','Erbjuds – bekräftas vid sparning'),('nej','Erbjuds inte'),('okant','Osäker – sparas som okänt')):
            html+=f'<option value="{v}" {"selected" if val[id]==v else ""}>{namn}</option>'
        html+='</select>'
        html+='<details><summary>Ogranskat förslag till tjänstens innehåll</summary><p>Kontrollera mot uppdragsavtalet. Förslagen är inte belägg för vad byrån gör.</p>'
        for rubrik,poster in (('Arbetsmoment',t.arbetsmoment),('Befogenheter att pröva',t.befogenheter),('Kompletteringsfrågor',t.kompletteringsfragor)):
            if poster:
                html+=f'<h3>{rubrik}</h3><ul>'+''.join(f'<li>{e(x)}</li>' for x in poster)+'</ul>'
        html+='</details>'
        if jamfor:
            sparat='ja' if vy.ar_bekraftad(id) and vy.uppgifter[id].varde is True else 'nej' if vy.ar_bekraftad(id) and vy.uppgifter[id].varde is False else 'okänt'
            html+=f'<p>Nu sparat: {sparat}. Ditt bevarade val: {e(val[id])}.</p>'
        if t.id in behov:
            html+=planvalsfalt(s,behov[t.id],'plan_'+t.id,d.get('plan_'+t.id,''))
    html+='</div><p>Behåll sparad uppgift ändrar inga tidigare värden eller belägg. Ja och nej ersätter svaret med angivet underlag; osäker blir aldrig ett bekräftat ja. Ändrade erbjudanden kan kräva att följdsvar kontrolleras igen.</p>'
    html+='<label class="check"><input type="checkbox" name="hela_listan" value="ja" '+('checked ' if d.get('hela_listan')=='ja' and not jamfor else '')+'required> Jag har kontrollerat hela listan och bekräftar mina val per rad.</label>'
    from riskanalys.intag.underlagsvy import underlagsval
    f=s.tjanst.rb.falt[next(iter(s.tjanst.rb.tjanster.values())).erbjuds_falt]
    html+=underlagsval(s,p,f,data,formid='tjanst')
    html+='<div class="fields"><div>'+falt('roll','Din funktion',d.get('roll',foreslagen_roll(p,getattr(s,'rollforslag',''))),required=True,html_id='tjanst-roll')+'</div><div>'+falt('datum','Bekräftelsedatum',d.get('datum',date.today()),'date',True,html_id='tjanst-datum')+'</div></div>'
    knapp='Jag har jämfört ändringarna – bekräfta tjänstelistan' if jamfor else 'Godkänn tjänstelistan och fortsätt'
    return html+f'<button>{knapp}</button></form><p>Om du inte kan bekräfta hela listan: besvara tjänsterna en i taget och markera de osäkra svaren som ”Vet inte”.</p></section>'


def tjanstesida(s,data=None,fel=''):
    p=s.tjanst.profil()
    html='<h1>Vilka tjänster erbjuder byrån?</h1>'+lista(s,p,data)
    html+='<details><summary>Besvara tjänsterna en i taget</summary><ul>'
    for t in s.tjanst.rb.tjanster.values():
        html+=f'<li><a href="{s.prefix}?falt={e(t.erbjuds_falt)}">{e(t.namn)}</a></li>'
    return sida(s,html+'</ul></details>',fel)
