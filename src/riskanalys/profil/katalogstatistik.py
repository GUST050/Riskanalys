"""Population och period för steg B:s räknade kundegenskaper."""
from riskanalys.profil.modeller import Profil

HOGRE = ('nominella_agare', 'personlig_formogenhet', 'sanktionshemvist', 'terrorhemvist',
         'okand_betalare', 'osaker_distansidentitet')
HEMVIST = tuple('P-GEO.antal_hemvist_' + s for s in ('sverige', 'ovriga_ees', 'utanfor_ees'))
ANTAL = (*('P-KUND.antal_' + s for s in HOGRE), 'P-KUND.antal_offentlig',
         'P-KUND.antal_reglerad_marknad', *HEMVIST)


def statistikbrister(profil: Profil) -> list[str]:
    """Överlapp tillåts mellan indikatorer, men hemvistgrupperna är en partition."""
    bas = profil.uppgifter.get('P-KUND.antal_aktiva')
    if not profil.ar_bekraftad('P-KUND.antal_aktiva') or type(bas.varde) is not int:
        return []
    fel = []
    for id in ANTAL:
        if not profil.ar_bekraftad(id):
            continue
        u = profil.uppgifter[id]
        if type(u.varde) is not int or not 0 <= u.varde <= bas.varde:
            fel.append(f'{id}: kundantal ska vara ett heltal mellan noll och P-KUND.antal_aktiva.')
        if not u.period or not bas.period or u.period != bas.period:
            fel.append(f'{id}: kundantal ska ha samma period som P-KUND.antal_aktiva.')
    if all(profil.ar_bekraftad(id) and type(profil.uppgifter[id].varde) is int
           and profil.uppgifter[id].period == bas.period for id in HEMVIST):
        if sum(profil.uppgifter[id].varde for id in HEMVIST) != bas.varde:
            fel.append('Hemvistfördelningen ska tillsammans motsvara P-KUND.antal_aktiva för samma period.')
    return fel
