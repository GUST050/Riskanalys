"""Registrera bara en uttryckligen bekräftad, faktiskt genomförd utvärdering."""
from datetime import date
from riskanalys.drift.historik import Handelse, registrera_handelse
from riskanalys.fel import RiskanalysFel
from riskanalys.profil.lagring import profilrevision


def registrera_utvardering(tjanst, datum: date, beskrivning: str, revision: str):
    if datum > date.today() or not beskrivning.strip() or len(beskrivning)>12000:
        raise RiskanalysFel('Ange datum senast idag och vad den genomförda utvärderingen omfattade. Registrera inte en planerad utvärdering som genomförd.')
    p=tjanst.profil()
    if profilrevision(p)!=revision:
        raise RiskanalysFel('Profilen har ändrats i en annan flik. Läs om sidan före registrering.')
    return registrera_handelse(tjanst.mapp, Handelse(datum=datum, typ='utvärdering', beskrivning=beskrivning.strip()))
