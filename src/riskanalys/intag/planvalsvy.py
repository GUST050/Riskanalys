"""Visat planval utan profilsparning eller implicit val av första kandidaten."""
from html import escape as e

from riskanalys.profil.forandringar import inforandebehov_for_andring
from riskanalys.profil.lagring import profilrevision
from riskanalys.profil.modeller import Uppgift
from riskanalys.profil.hantering import tolka_varde
from riskanalys.fel import RiskanalysFel


def bekraftat_ja(falt,text,status):
    if status!='bekräftad':return False
    try:return tolka_varde(falt,str(text)) is True
    except RiskanalysFel:return False


def behov_for_erbjudanden(s, profil, erbjudanden):
    uppgifter = dict(profil.uppgifter)
    for falt, erbjuds in erbjudanden.items():
        uppgifter[falt] = uppgifter.get(falt, Uppgift()).model_copy(
            update={'varde': erbjuds, 'status': 'bekräftad', 'inaktuell': False})
    efter = profil.model_copy(update={'uppgifter': uppgifter})
    return inforandebehov_for_andring(s.tjanst.mapp, s.tjanst.rb, efter, profilrevision(profil))


def planvalsfalt(s, behov, namn, valt=''):
    t = s.tjanst.rb.tjanster[behov.tjanst]
    html = f'<fieldset><legend>Plan för införandet av {e(t.namn)}</legend>'
    if len(behov.kandidater) == 1:
        html += f'<p>Föreslagen kandidat: {e(behov.kandidater[0])}. Välj planen uttryckligen för att bekräfta den.</p>'
    if behov.kandidater:
        html += f'<label>Vilken utvärderad plan genomförs?<select name="{e(namn)}" required><option value="">Välj plan</option>'
        html += ''.join(f'<option value="{e(id)}" {"selected" if id == valt else ""}>{e(id)}</option>' for id in behov.kandidater)
        html += '</select></label><p>Endast den valda planen markeras som genomförd.</p>'
    else:
        html += '<p>Registrera och utvärdera en ny-tjänst-plan före införandet.</p>'
    html += f'<p><a href="{s.prefix}planering?tjanst={e(t.id)}" target="_blank" rel="noopener">Öppna planering i en ny flik</a>. Behåll detta urval; efter ändrad profil behöver du jämföra och bekräfta det igen.</p>'
    return html + '</fieldset>'
