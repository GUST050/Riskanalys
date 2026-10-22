"""XML 1.0:s teckenkrav kontrolleras före lagring och kostsam skrivning."""
from riskanalys.fel import RiskanalysFel


def kontrollera_text(*texter):
    for text in texter:
        if isinstance(text, str) and any(not (ord(c) in (9, 10, 13) or 32 <= ord(c) <= 0xD7FF or 0xE000 <= ord(c) <= 0xFFFD or 0x10000 <= ord(c) <= 0x10FFFF) for c in text):
            raise RiskanalysFel('Texten innehåller styrtecken eller andra tecken som inte kan skrivas i Word (XML). Ta bort dem och spara igen.')


def kontrollera_profiltext(profil):
    kontrollera_text(profil.byra.id, profil.byra.lan, profil.byra.regelpaket)
    for id, u in profil.uppgifter.items():
        try:
            kontrollera_text(id, u.varde, u.kalla, u.bekraftad_av, u.motivering)
        except RiskanalysFel as exc:
            raise RiskanalysFel(f'{id}: {exc}') from None
    for plan in profil.tjansteplaner:
        kontrollera_text(plan.beskrivning)
        for id, u in plan.uppgifter.items():
            kontrollera_text(id,u.varde,u.kalla,u.bekraftad_av,u.motivering)
    for g in profil.kombinationsgrupper:
        kontrollera_text(g.avgransning,g.beskrivning)
        for u in (g.antal,g.bas):
            kontrollera_text(u.kalla,u.bekraftad_av,u.motivering)
