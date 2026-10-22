"""Byrån bekräftar hela tjänsteförteckningen, aldrig härledd från SNI."""
from datetime import date
from html import escape as e
from riskanalys.intag.vyer import dold, falt, foreslagen_roll, sida
from riskanalys.intag.tjanst import profilrevision


def lista(s,p,data=None):
    d=data or {};html='<section class="proposal"><h2>Välj byråns tjänster på en sida</h2><p>Markera alla tjänster ni faktiskt erbjuder. Uppgifterna behöver komma från din genomgång av verksamheten; SCB:s SNI-kod besvarar inte detta.</p>'
    from riskanalys.intag.planvalsvy import behov_for_erbjudanden, planvalsfalt
    from riskanalys.profil.omfattning import kompatibilitetsvy
    vy=kompatibilitetsvy(p,s.tjanst.rb)
    val={t.erbjuds_falt:(d.get('tjanst_'+t.erbjuds_falt)=='ja' if data is not None else
         bool(vy.ar_bekraftad(t.erbjuds_falt) and vy.uppgifter[t.erbjuds_falt].varde is True))
         for t in s.tjanst.rb.tjanster.values()}
    behov={b.tjanst:b for b in behov_for_erbjudanden(s,p,val)}
    jamfor=data is not None and d.get('revision')!=profilrevision(p)
    if jamfor:
        html+='<p class="error">Profilen har ändrats. Ditt urval och underlag är bevarade. Jämför med de nu sparade erbjudandena och planerna nedan innan du bekräftar igen.</p>'
    html+=f'<form method="post" action="{s.prefix}tjanster">'+dold('csrf',s.csrf)+dold('revision',profilrevision(p))
    html+='<div class="tjanster">'
    for t in s.tjanst.rb.tjanster.values():
        id=t.erbjuds_falt;u=p.uppgifter.get(id)
        checked=val[id]
        html+=f'<label class="check"><input type="checkbox" name="tjanst_{e(id)}" value="ja" {"checked" if checked else ""}><span>{e(t.namn)}<br><small class="hint">{e(t.beskrivning)}</small></span></label>'
        if jamfor:
            sparat='ja' if vy.ar_bekraftad(id) and vy.uppgifter[id].varde is True else 'nej' if vy.ar_bekraftad(id) and vy.uppgifter[id].varde is False else 'okänt'
            html+=f'<p>Nu sparat: {sparat}. Ditt bevarade val: {"ja" if checked else "nej"}.</p>'
        if t.id in behov:
            html+=planvalsfalt(s,behov[t.id],'plan_'+t.id,d.get('plan_'+t.id,''))
    html+='</div><p>Denna genomgång ersätter tjänstesvaren. Ändrade erbjudanden kan kräva att tidigare följdsvar kontrolleras igen.</p>'
    html+='<label class="check"><input type="checkbox" name="hela_listan" value="ja" '+('checked ' if d.get('hela_listan')=='ja' and not jamfor else '')+'required> Jag har kontrollerat hela listan och bekräftar att omarkerade tjänster inte erbjuds.</label>'
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
