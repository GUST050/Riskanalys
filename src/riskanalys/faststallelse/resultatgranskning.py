"""En explicit handling ger vanliga attestposter för exakt alla visade R-avsnitt."""
from riskanalys.faststallelse.sakgranskning import struktur_summa,registrera_sakgranskning,SakgranskningsFel
from riskanalys.dokument.resultatmodell_v9 import summa
from riskanalys.dokument.rendering_v9 import kontrollera_presentation
from riskanalys.dokument.rapportvyer_v9 import bygg_rapportvyer_v9


def registrera_resultatgranskning(sakgranskningar,dokument,profil,*,presentation,
        visad_struktursumma,analysbindning,godkand,roll,namn,datum,kommentar=None):
    kontrollera_presentation(bygg_rapportvyer_v9(dokument),profil,presentation)
    if (not analysbindning or not visad_struktursumma or
        visad_struktursumma!=struktur_summa(dokument,presentation=presentation) or
        summa(dokument.model_dump(mode='json'))!=presentation.dokument):
        raise SakgranskningsFel('Det visade underlaget har ändrats. Läs hela resultatrapporten och dess struktursumma på nytt.')
    nya=sakgranskningar
    for a in dokument.avsnitt:
        if a.leveransdel=='resultatrapport':
            nya=registrera_sakgranskning(nya,dokument,profil,a.id,godkand,roll,namn,datum,kommentar,
                analysbindning=analysbindning,presentation=presentation)
    return nya
