"""Webbens rapportval och omfattningsknapp; gemensamt flöde i arbetsfloden."""
from pathlib import Path
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.manifest import verifiera_manifest
from riskanalys.dokument.export import UTKASTFIL
# Kompatibla publika importvägar; nya konsumenter använder arbetsfloden direkt.
from riskanalys.arbetsfloden import skapa_utkast, kontrollera_utkast, las_utkast, uppdatera_export

def omfattningsknapp(s,profil):
    from html import escape
    from riskanalys.intag.vyer import dold
    from riskanalys.profil.lagring import profilrevision
    html='<details><summary>Tjänst utanför katalogen eller annat som saknar modellstöd</summary><p>Beskriv det i frågan om ytterligare riskförhållanden. Du kan ta fram ett separat ofullständigt omfattningsunderlag med bekräftade fakta och beskrivningen. Det innehåller inga risknivåer och kan inte fastställas som en komplett bedömning.</p>'
    html+='<form method="post" action="'+escape(s.prefix,quote=True)+'omfattningsunderlag">'+dold('csrf',s.csrf)+dold('revision',profilrevision(profil))+'<button>Skapa ofullständigt omfattningsunderlag utan AI</button></form>'
    if getattr(s,'omfattningsfil',None):html+='<p><a href="'+escape(s.prefix,quote=True)+'omfattningsword">Hämta OFULLSTÄNDIGT omfattningsunderlag</a></p>'
    return html+'</details>'


def rapportdel(utkast:Path,del_:str) -> Path:
    """Fasta routenamn väljer en del ur det verifierade exportpaketet."""
    from riskanalys.lagring.manifest import las_manifest
    from riskanalys.dokument.rapportpaket_v9 import ar_v9_paket
    from riskanalys.dokument.leverans_v9 import LeveransV9,DELAR
    if del_ not in ('word','underlag','analysbilaga'):
        raise RiskanalysFel('Okänd rapportdel. Läs om översikten.')
    m=utkast.parent
    if verifiera_manifest(m):raise RiskanalysFel('Exportpaketet är ändrat eller ofullständigt. Uppdatera utkastet.')
    from riskanalys.dokument.rapportpaket_v10 import ar_v10_paket
    if ar_v10_paket(m,las_manifest(m)):
        from riskanalys.dokument.leverans_v10 import LeveransV10
        l=LeveransV10.model_validate_json((m/'leverans.json').read_text())
        if l.version is not None:raise RiskanalysFel('Nedladdningen kräver ett märkt utkast.')
        return m/l.filnamn[{'word':0,'analysbilaga':1,'underlag':2}[del_]]
    if ar_v9_paket(m,las_manifest(m)):
        l=LeveransV9.model_validate_json((m/'leverans.json').read_text())
        if l.version is not None:raise RiskanalysFel('Nedladdningen kräver ett märkt utkast.')
        val={'word':0,'analysbilaga':1,'underlag':2}
        return m/l.filnamn[val[del_]]
    if del_=='analysbilaga':raise RiskanalysFel('Detta äldre utkast saknar separat analysbilaga. Uppdatera uttryckligen till resultatrapport.')
    return m/('underlagsbilaga-UTKAST.docx' if del_=='underlag' else UTKASTFIL)
