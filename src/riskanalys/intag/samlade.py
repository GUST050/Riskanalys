"""Gruppera jämförbara intagsfrågor; spara genom ordinarie svarshantering."""
from dataclasses import dataclass

from riskanalys.fel import RiskanalysFel
from riskanalys.intag.fragor import fragor
from riskanalys.intag.modeller import IntagSvar
from riskanalys.intag.tjanst import profilrevision
from riskanalys.intag.underlag import egen_kannedom_tillaten, kategori, vald_kalla
from riskanalys.regelverk.modeller import Falt


RUBRIKER = {
    'hemvist': 'Kundernas fördelning på hemvist – Sverige, övriga EES och utanför EES',
    'verksamhet': 'Byråns verksamhet och organisation',
    'beskrivningar': 'Beskriv byråns arbetssätt',
    'kunder': 'Kundstatistik, kanaler och geografi',
    'riskforhallanden': 'Förhållanden i verksamheten och kundbasen',
    'ekonomi': 'Omsättning och intäkter per tjänst',
    'erfarenheter': 'Rapportering och avböjanden',
    'tjanstkunder': 'Antal kunder per tjänst',
}


@dataclass(frozen=True)
class Fragegrupp:
    id: str
    rubrik: str
    falt: tuple[Falt, ...]


def grupp_for(rb, f):
    """Avgränsa uttryckligt: inga kontrollfaser, härledda fält eller tjänsteval."""
    if f.typ not in ('text', 'bool', 'heltal', 'tal'):
        return None
    if f.id.startswith('P-GEO.antal_hemvist_'):
        return 'hemvist'
    if egen_kannedom_tillaten(f):
        if f.id.startswith(('P-ORG.', 'P-ROLL.', 'P-VERK.')):
            return 'verksamhet'
        if f.id.startswith('P-BESK.'):
            return 'beskrivningar'
        for t in rb.tjanster.values():
            if f.id.startswith(t.erbjuds_falt.removesuffix('erbjuds')) and f.id != t.erbjuds_falt:
                return 'tjanst-' + t.id
    if f.periodkrav and kategori(f) == 'kundstatistik':
        if f.id.startswith(('P-KUND.', 'P-KANAL.', 'P-GEO.')) and f.typ == 'heltal':
            return 'kunder'
        if f.id.startswith('P-RISK.') and f.typ == 'bool':
            return 'riskforhallanden'
        if f.id.startswith('P-TJ.') and f.id.endswith('_antal_kunder'):
            return 'tjanstkunder'
    if kategori(f) == 'ekonomistatistik':
        return 'ekonomi'
    if kategori(f) == 'erfarenhetsstatistik':
        return 'erfarenheter'
    return None


def grupper(rb, profil):
    """Behåll intagets aktivering och beroendeordning även inom gruppen."""
    urval = {}
    for q in fragor(rb, profil):
        id = grupp_for(rb, q.falt)
        if id:
            urval.setdefault(id, []).append(q.falt)
    rubriker = {**RUBRIKER, **{'tjanst-' + t.id: t.namn + ' – arbetssätt' for t in rb.tjanster.values()}}
    return tuple(Fragegrupp(id, rubriker[id], tuple(falt)) for id, falt in urval.items())


def hamta_grupp(rb, profil, id):
    grupp = next((g for g in grupper(rb, profil) if g.id == id), None)
    if grupp is None:
        raise RiskanalysFel('Välj en aktuell grupp på sidan Samlade frågor. Bekräfta först eventuella grundsvar.')
    return grupp


def spara_grupp(tjanst, data):
    from riskanalys.intag.webb import formulardatum
    from riskanalys.profil.modeller import Period

    p = tjanst.profil()
    if data.get('revision') != profilrevision(p):
        raise RiskanalysFel('Profilen har ändrats i en annan flik. Läs om sidan; inga svar sparades.')
    grupp = hamta_grupp(tjanst.rb, p, data.get('grupp', ''))
    gemensamma = {'csrf', 'revision', 'grupp', 'bekrafta', 'underlag', 'kalla', 'roll', 'datum', 'period_fran', 'period_till'}
    tillatna = gemensamma | {prefix + f.id for f in grupp.falt for prefix in ('text_', 'status_', 'motivering_')}
    if set(data) - tillatna:
        raise RiskanalysFel('Formuläret innehåller frågor som inte hör till den aktuella gruppen. Läs om sidan.')
    if data.get('bekrafta', '') not in ('', 'ja'):
        raise RiskanalysFel('Bekräfta uttryckligen de ifyllda svar som ska sparas.')
    urval = []
    for f in grupp.falt:
        status = data.get('status_' + f.id, '')
        if status not in ('', 'behall', 'okänt'):
            raise RiskanalysFel('Välj spara, lämna oförändrat eller Vet inte för varje fråga.')
        text = data.get('text_' + f.id, '')
        if status != 'behall' and (status == 'okänt' or text.strip()):
            urval.append((f, text, 'okänt' if status == 'okänt' else 'bekräftad'))
    if not urval:
        raise RiskanalysFel('Fyll i minst ett svar eller markera en fråga som Vet inte. Tomma fält lämnas oförändrade.')
    bekraftade = [f for f, _, status in urval if status == 'bekräftad']
    if bekraftade and data.get('bekrafta') != 'ja':
        raise RiskanalysFel('Kontrollera svaren och markera att du bekräftar de ifyllda uppgifterna med det gemensamma underlaget.')
    period = None
    if bekraftade and any(f.periodkrav for f in bekraftade):
        period = Period(fran=formulardatum(data, 'period_fran'), till=formulardatum(data, 'period_till'))
    datum = formulardatum(data, 'datum')
    svar = tuple(IntagSvar(
        falt=f.id, text=text, status=status, datum=datum, roll=data.get('roll', ''),
        kalla=vald_kalla(tjanst.rb, p, f, data, period) if status == 'bekräftad' else '',
        period=period if status == 'bekräftad' else None,
        motivering=data.get('motivering_' + f.id, ''),
    ) for f, text, status in urval)
    return tjanst.spara_flera(svar, data['revision'])
