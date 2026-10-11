"""Byrån bekräftar hela tjänsteförteckningen, aldrig härledd från SNI."""
from datetime import date
from html import escape as e
from riskanalys.intag.vyer import dold, falt, foreslagen_roll, sida
from riskanalys.intag.tjanst import profilrevision


def lista(s,p,data=None):
    d=data or {};html='<section class="proposal"><h2>Välj byråns tjänster på en sida</h2><p>Markera alla tjänster ni faktiskt erbjuder. Uppgifterna behöver komma från din genomgång av verksamheten; SCB:s SNI-kod besvarar inte detta.</p>'
    html+=f'<form method="post" action="{s.prefix}tjanster">'+dold('csrf',s.csrf)+dold('revision',d.get('revision',profilrevision(p)))
    html+='<div class="tjanster">'
    for t in s.tjanst.rb.tjanster.values():
        id=t.erbjuds_falt;u=p.uppgifter.get(id)
        checked=d.get('tjanst_'+id)=='ja' if data is not None else bool(p.ar_bekraftad(id) and u.varde is True)
        html+=f'<label class="check"><input type="checkbox" name="tjanst_{e(id)}" value="ja" {"checked" if checked else ""}><span>{e(t.namn)}<br><small class="hint">{e(t.beskrivning)}</small></span></label>'
    html+='</div><p>Denna genomgång ersätter tjänstesvaren. Ändrade erbjudanden kan kräva att tidigare följdsvar kontrolleras igen.</p>'
    html+='<label class="check"><input type="checkbox" name="hela_listan" value="ja" required> Jag har kontrollerat hela listan och bekräftar att omarkerade tjänster inte erbjuds.</label>'
    from riskanalys.intag.underlagsvy import underlagsval
    f=s.tjanst.rb.falt[next(iter(s.tjanst.rb.tjanster.values())).erbjuds_falt]
    html+=underlagsval(s,p,f,data,formid='tjanst')
    html+='<div class="fields"><div>'+falt('roll','Din funktion',d.get('roll',foreslagen_roll(p,getattr(s,'rollforslag',''))),required=True,html_id='tjanst-roll')+'</div><div>'+falt('datum','Bekräftelsedatum',d.get('datum',date.today()),'date',True,html_id='tjanst-datum')+'</div></div>'
    return html+'<button>Godkänn tjänstelistan och fortsätt</button></form><p>Om du inte kan bekräfta hela listan: besvara tjänsterna en i taget och markera de osäkra svaren som ”Vet inte”.</p></section>'


def tjanstesida(s,data=None,fel=''):
    p=s.tjanst.profil()
    html='<h1>Vilka tjänster erbjuder byrån?</h1>'+lista(s,p,data)
    html+='<details><summary>Besvara tjänsterna en i taget</summary><ul>'
    for t in s.tjanst.rb.tjanster.values():
        html+=f'<li><a href="{s.prefix}?falt={e(t.erbjuds_falt)}">{e(t.namn)}</a></li>'
    return sida(s,html+'</ul></details>',fel)
