"""Flera närliggande svar med gemensamt underlag och uttrycklig bekräftelse."""
from html import escape as e
from urllib.parse import urlencode

from riskanalys.fel import RiskanalysFel
from riskanalys.intag.samlade import grupper, hamta_grupp
from riskanalys.intag.tjanst import profilrevision
from riskanalys.intag.underlag import periodforslag
from riskanalys.intag.underlagsvy import underlagsval
from riskanalys.profil.hantering import visa_varde
from riskanalys.profil.modeller import Uppgift


def grupplank(prefix, id):
    return prefix + 'samlat?' + urlencode({'grupp': id})


def registerforslag(s, p, grupp):
    """Behåll nästa registerförslag i ett eget formulär före gruppformuläret."""
    from riskanalys.foretagsdata.lagring import las_bild
    from riskanalys.intag.registervy import inlineforslag

    try:
        bild = las_bild(s.tjanst.mapp)
        if bild:
            for f in grupp.falt:
                if not p.ar_bekraftad(f.id):
                    html = inlineforslag(s, bild, p, f.id)
                    if html:
                        return html
    except RiskanalysFel:
        return f'<p>Registerunderlaget behöver kontrolleras på <a href="{s.prefix}register">företagssidan</a>. Du kan ange egna svar nedan.</p>'
    return ''


def samladsida(s, id=None, data=None, fel=''):
    from riskanalys.intag.vyer import sida, dold, falt, val, foreslagen_roll, date

    p = s.tjanst.profil()
    if id is None:
        html = '<h1>Samlade frågor</h1><p>Besvara flera närliggande frågor med ett gemensamt underlag och en bekräftelse. Varje svar sparas med egen källa, period, datum och funktion.</p><ul>'
        for g in grupper(s.tjanst.rb, p):
            kvar = sum(not p.ar_bekraftad(f.id) for f in g.falt)
            html += f'<li><a href="{e(grupplank(s.prefix, g.id), quote=True)}">{e(g.rubrik)}</a> · {kvar} av {len(g.falt)} frågor kvar</li>'
        return sida(s, html + '</ul>', fel)
    g = hamta_grupp(s.tjanst.rb, p, id)
    d = data or {}
    html = f'<h1>{e(g.rubrik)}</h1><p>Fyll i de uppgifter du har underlag för. Tomma fält och svar märkta ”Lämna oförändrat” sparas inte. Välj ”Vet inte” och beskriv vad som behöver kontrolleras för en osäker uppgift.</p>'
    nu = sum(not p.ar_bekraftad(f.id) and p.uppgifter.get(f.id, Uppgift()).status != 'föreslagen' for f in g.falt)
    html += f'<p class="hint">{sum(p.ar_bekraftad(f.id) for f in g.falt)} av {len(g.falt)} uppgifter bekräftade i gruppen · {nu} frågor att besvara nu.</p>'
    html += registerforslag(s, p, g)
    html += f'<form method="post" action="{s.prefix}samlat" autocomplete="off">'
    html += dold('csrf', s.csrf) + dold('revision', d.get('revision', profilrevision(p))) + dold('grupp', g.id)
    for f in g.falt:
        u = p.uppgifter.get(f.id, Uppgift())
        text = d.get('text_' + f.id, visa_varde(f, u.varde) if u.varde is not None else '')
        status = d.get('status_' + f.id, 'behall' if u.varde is not None or u.status == 'föreslagen' else '')
        html += '<fieldset class="proposal"><legend>' + e(f.fraga) + '</legend><p class="hint">' + e(f.varfor) + '</p>'
        if u.varde is not None or u.status == 'föreslagen':
            etikett = 'Behöver kontrolleras igen' if u.inaktuell else 'Vet inte – komplettering behövs' if u.status == 'föreslagen' else u.status
            periodtext = f' · period {u.period.fran}–{u.period.till}' if u.period else ''
            html += f'<details><summary>Tidigare svar: {e(etikett)}</summary><p class="hint">{e(u.kalla or "Underlag saknas")}{e(periodtext)} · {e(str(u.datum or "Datum saknas"))}. Välj ”Spara ifyllt svar” för att bekräfta det med underlaget nedan.</p></details>'
        namn = 'text_' + f.id
        if f.typ != 'text':
            html += '<div class="fields"><div>'
        if f.typ == 'bool':
            html += val(namn, 'Ditt svar', [('ja', 'Ja'), ('nej', 'Nej')], text)
        elif f.typ == 'text':
            html += f'<label for="{e(namn)}">Ditt svar</label><textarea id="{e(namn)}" name="{e(namn)}" maxlength="12000">{e(text)}</textarea>'
        else:
            html += falt(namn, 'Ditt svar' + (f' ({f.enhet})' if f.enhet else ''), text)
        if f.typ != 'text':
            html += '</div><div>'
        # Tomt värde är ett synligt val även i en vanlig select utan skript.
        alternativ = [('', 'Spara ifyllt svar med gruppen'), ('behall', 'Lämna oförändrat'), ('okänt', 'Vet inte – komplettera senare')]
        html += f'<label for="status_{e(f.id)}">Hantera svaret</label><select id="status_{e(f.id)}" name="status_{e(f.id)}">'
        html += ''.join(f'<option value="{e(k)}" {"selected" if k == status else ""}>{e(v)}</option>' for k, v in alternativ) + '</select>'
        if f.typ != 'text':
            html += '</div></div>'
        html += '<details' + (' open' if status == 'okänt' else '') + '><summary>Vad behöver kontrolleras?</summary>'
        html += falt('motivering_' + f.id, 'Hur eller när ska uppgiften kontrolleras?', d.get('motivering_' + f.id, u.motivering or '')) + '</details>'
        html += f'<p><a href="{s.prefix}?{urlencode({"falt": f.id})}">Besvara bara denna fråga med eget underlag</a></p></fieldset>'
    html += '<h2>Gemensamt underlag för svaren du bekräftar</h2><p>Kontrollera att samma underlag stöder varje ifyllt svar som ska sparas. Använd den enskilda frågan om ett svar behöver en annan källa eller period. Vet inte behåller eventuella tidigare belägg utan att bekräfta dem.</p>'
    period = periodforslag(s.tjanst.rb, p, g.falt[0])
    html += underlagsval(s, p, g.falt[0], data, period=period, formid='grupp')
    if g.falt[0].periodkrav:
        html += '<p>Perioden gäller alla svar som bekräftas här. Andelar beräknas automatiskt från antal och bas.</p>'
        html += falt('period_fran', 'Periodens start', d.get('period_fran', period.fran if period else ''), 'date')
        html += falt('period_till', 'Periodens slut', d.get('period_till', period.till if period else ''), 'date')
    html += falt('roll', 'Din funktion eller roll', d.get('roll', foreslagen_roll(p, s.rollforslag)))
    html += falt('datum', 'Bekräftelsedatum', d.get('datum', date.today()), 'date', True)
    html += '<label class="check"><input type="checkbox" name="bekrafta" value="ja" ' + ('checked' if d.get('bekrafta') == 'ja' else '') + '>Jag har kontrollerat de ifyllda svar som ska sparas och bekräftar dem med det gemensamma underlaget.</label>'
    html += '<p class="hint">Markeringen behövs för bekräftade svar. Du kan spara enbart Vet inte utan källa eller funktion.</p><button>Spara gruppen och fortsätt</button></form>'
    return sida(s, html, fel)
