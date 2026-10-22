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

