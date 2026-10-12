"""Underlagsväljare utan skript eller automatisk bekräftelse."""
from html import escape as e
from riskanalys.intag.underlag import EGEN_KANNEDOM, egen_kannedom_tillaten, tidigare_underlag


def underlagsval(s, p, f, data=None, uppgift=None, period=None, formid='svar'):
    from riskanalys.intag.vyer import falt
    d = data or {}
    kalla = d.get('kalla', uppgift.kalla if uppgift and uppgift.kalla else '')
    tidigare = tidigare_underlag(s.tjanst.rb, p, f)
    alternativ = [('eget', 'Ange ett underlag eller en hänvisning')]
    if egen_kannedom_tillaten(f):
        alternativ.append(('egen_kannedom', EGEN_KANNEDOM))
    for u in tidigare:
        if u.kalla == EGEN_KANNEDOM:
            continue
        etikett = u.kalla + (f' · {u.period.fran}–{u.period.till}' if u.period else '')
        alternativ.append((u.token, etikett))
    if data is not None:
        valt = d.get('underlag', 'eget')
    elif kalla:
        valt = 'egen_kannedom' if kalla == EGEN_KANNEDOM and egen_kannedom_tillaten(f) else 'eget'
    else:
        samma = next((u for u in tidigare if u.period == period and u.kalla != EGEN_KANNEDOM), None)
        valt = samma.token if samma else 'egen_kannedom' if egen_kannedom_tillaten(f) else 'eget'
    id = formid + '-underlag'
    html = f'<label for="{id}">Vad grundar du svaret på?</label><select id="{id}" name="underlag">'
    html += ''.join(f'<option value="{e(k,quote=True)}" {"selected" if k == valt else ""}>{e(v)}</option>' for k, v in alternativ)
    html += '</select><p class="hint">Kontrollera att det valda underlaget gäller just detta svar. Det sparas med din bekräftelse.</p>'
    html += '<details' + (' open' if valt == 'eget' else '') + '><summary>Ange eller ändra egen hänvisning</summary>'
    html += falt('kalla', 'Underlag eller hänvisning — används när ”Ange ett underlag” är valt', kalla, html_id=formid+'-kalla')
    return html + '</details>'
