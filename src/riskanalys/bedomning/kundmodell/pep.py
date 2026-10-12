"""PEP-period räknas i kalendermånader; härledda indata kan inte förfalskas."""

import calendar
from datetime import date

from riskanalys.regelverk.villkor import Faltvarde, Kunskap


def manader_efter(datum: date, antal: int) -> date:
    """Flytta ett datum hela kalendermånader, begränsat till månadens sista dag."""
    total = datum.year * 12 + datum.month - 1 + antal
    ar, manad = divmod(total, 12)
    return date(ar, manad + 1, min(datum.day, calendar.monthrange(ar, manad + 1)[1]))


def pep_varde(varden: dict[str, Faltvarde], datum: date) -> Faltvarde:
    """Härled om PEP-åtgärder krävs utan att tolka okända uppgifter som falska."""
    def kand(id: str) -> object:
        uppgift = varden.get(id)
        return uppgift.varde if uppgift and uppgift.kunskap is Kunskap.KAND else None

    pep = [kand(id) for id in ('K-PEP.kund', 'K-PEP.vh', 'K-PEP.familj_rca')]
    if all(post is False for post in pep):
        return Faltvarde(Kunskap.KAND, False)
    if not any(post is True for post in pep):
        return Faltvarde(Kunskap.OKAND)
    upphort = kand('K-PEP.funktion_upphort')
    if upphort is False:
        return Faltvarde(Kunskap.KAND, True)
    slut = kand('K-PEP.slutdatum')
    if upphort is not True or type(slut) is not date or slut > datum:
        return Faltvarde(Kunskap.OKAND)
    if datum < manader_efter(slut, 18):
        return Faltvarde(Kunskap.KAND, True)
    hog = kand('K-PEP.hog_risk_efter18')
    return Faltvarde(Kunskap.KAND, hog) if type(hog) is bool else Faltvarde(Kunskap.OKAND)
