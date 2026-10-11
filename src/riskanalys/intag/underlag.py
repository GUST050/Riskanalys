"""Synliga underlagsval, avgränsade till samma slags fakta och statistikperiod."""
from dataclasses import dataclass
import hashlib
import json
from riskanalys.fel import RiskanalysFel
from riskanalys.profil.modeller import Period

EGEN_KANNEDOM = 'Egen kännedom om verksamheten'
ENKLA_FALT = frozenset({
    'P-ORG.namn', 'P-ORG.koncernmoder', 'P-ORG.sarskilda_funktioner',
    'P-ROLL.ffr_namn', 'P-ROLL.ansvarsfunktion',
    'P-BESK.verksamhet', 'P-BESK.kundtyper', 'P-BESK.kanaler',
    'P-BESK.geografi', 'P-BESK.ovriga_forhallanden', 'P-BESK.ovrigt',
})


def egen_kannedom_tillaten(falt):
    if falt.periodkrav or falt.typ in ('heltal', 'tal', 'andel', 'datum'):
        return False
    return (falt.id in ENKLA_FALT
            or (falt.id.startswith('P-VERK.') and falt.typ == 'bool')
            or (falt.id.startswith('P-TJ.') and falt.id.endswith(
                ('_erbjuds', '_arbetssatt', '_kundtyper', '_kanaler', '_geografi', '_ovriga_risker'))))


def kategori(falt):
    if egen_kannedom_tillaten(falt):
        return 'verksamhet'
    if falt.periodkrav:
        if falt.id in ('P-VERK.antal_rapporter', 'P-VERK.antal_avbojanden'):
            return 'erfarenhetsstatistik'
        if falt.id.endswith('.omsattning') or falt.id.endswith('_omsattning'):
            return 'ekonomistatistik'
        return 'kundstatistik'
    if falt.id.startswith('P-KONTROLL.'):
        delar = falt.id.rsplit('.', 1)
        fas = 'genomforande' if delar[1] == 'belagg' else delar[1]
        return delar[0] + '.' + fas
    return falt.id


@dataclass(frozen=True)
class Underlag:
    token: str
    kalla: str
    period: Period | None


def tidigare_underlag(rb, profil, falt):
    resultat = {}
    for id, u in reversed(tuple(profil.uppgifter.items())):
        f = rb.falt.get(id)
        if (not f or not f.intag or f.alias_for or not profil.ar_bekraftad(id)
                or kategori(f) != kategori(falt) or not u.kalla):
            continue
        if u.kalla.startswith(('SCB AFR API;', 'Lokalt importerat SCB-format')):
            continue
        if u.kalla == EGEN_KANNEDOM and not egen_kannedom_tillaten(falt):
            continue
        data = [kategori(falt), u.kalla, u.period.model_dump(mode='json') if u.period else None]
        token = 'tidigare:' + hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        resultat.setdefault(token, Underlag(token, u.kalla, u.period))
    return tuple(resultat.values())[:8]


def periodforslag(rb, profil, falt):
    if not falt.periodkrav:
        return None
    bas = 'P-VERK.omsattning' if kategori(falt) == 'ekonomistatistik' else 'P-KUND.antal_aktiva'
    u = profil.uppgifter.get(bas)
    return u.period if u and profil.ar_bekraftad(bas) else None


def vald_kalla(rb, profil, falt, data, period=None):
    val = data.get('underlag', 'eget')
    if val == 'eget':
        return data.get('kalla', '')
    if val == 'egen_kannedom':
        if not egen_kannedom_tillaten(falt):
            raise RiskanalysFel('Den här frågan behöver ett konkret underlag. Egen kännedom kan inte väljas som underlag här.')
        return EGEN_KANNEDOM
    for u in tidigare_underlag(rb, profil, falt):
        if u.token == val:
            if u.period != period:
                raise RiskanalysFel('Det valda underlaget gäller en annan period. Kontrollera perioden eller ange ett annat underlag.')
            return u.kalla
    raise RiskanalysFel('Välj ett visat underlag eller ange ett eget. Underlaget kan ha ändrats; läs om sidan.')
