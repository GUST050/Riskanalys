"""Läsbar jämförelse och separat, uttrycklig överföringshandling."""
from html import escape
import yaml
from riskanalys.analys.overforing import foresla_overforing
from riskanalys.intag.vyer import dold


def jamforelse(s,paket,revision,data=None):
    nytt=foresla_overforing(s.tjanst.rb,paket)
    html='<h1>Jämför schema 1 med schema 2</h1><p>Originalets lokala svar och attributioner bevaras. Bara semantiskt lika uppgifter kan föreslås gemensamt. Förslagen är antaganden; inga godkännanden förs över. Läs och belägg dem innan tjänsternas tillämpningar bekräftas.</p>'
    html+='<p>Block, scenarioval och modellens lokala användningsprövning måste bekräftas på nytt. Alla tjänstebeslut är bundna till hela analyspaketet. Sparandet arkiverar exakta originalbytes och ersätter därefter paketet atomiskt.</p>'
    for rubrik,p in (('Sparat original – schema 1',paket),('Ogranskat överföringsförslag – schema 2',nytt)):
        html+='<details><summary>'+rubrik+'</summary><pre>'+escape(yaml.safe_dump(p.model_dump(mode='json'),allow_unicode=True,sort_keys=False))+'</pre></details>'
    html+='<form method="post" action="'+escape(s.prefix+'analysoverfor',quote=True)+'">'+dold('csrf',s.csrf)+dold('revision',(data or {}).get('revision',revision))
    return html+'<label class="check"><input type="checkbox" name="jamfort" value="ja" required> Jag har jämfört original, belägg, perioder och förslag</label><button>Överför till ogranskad gemensam analys</button></form><p>Vanlig läsning, import eller förnyelse byter aldrig schema.</p>'
