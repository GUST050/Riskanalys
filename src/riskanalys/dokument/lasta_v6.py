"""Låsta stycken i v6: egen rapportering (B-15) och geografins underlag (B-09, B-10).

Styckena skrivs byte för byte likadant varje gång underlaget är detsamma (spec 8.4.1, 8.4.6 punkt 2).
De hålls korta i huvudtexten; fält-ID och fullständiga belägg står i bilaga B1 (spec 8.4.9 punkt 8).
Inget av dem skickas till AI; AI ser bara de skyddade instruktionerna i delskrivningen.
"""
from riskanalys.bedomning.erfarenheter import AVBOJANDEN, ERFARENHETSFALT, RAPPORTER, belagd_uppgift
from riskanalys.bedomning.modeller import Tjanstbedomning
from riskanalys.dokument.klartext import (VERIFIERA, faltnamn, gemen, gransmening, under_grans, uppgiftstext,
                                          villkorstext)
from riskanalys.dokument.modeller import Textstycke
from riskanalys.dokument.tabeller import kort_varde
from riskanalys.profil.modeller import Profil
from riskanalys.profil.omfattning import kompatibilitetsvy
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.villkor import Sanning, falt_i, tolka_villkor, utvardera

Gransindex = dict[str, tuple[float, ...]]
UTFALL = {Sanning.SANT: 'uppfyllt', Sanning.FALSKT: 'inte uppfyllt', Sanning.OKANT: 'okänt'}
_GEMENSAMT_NAMN = 'geografibeskrivning'
GEOGRAFIBESKRIVNINGAR = (('P-BESK.geografi', 'Byråns geografibeskrivning'), ('{slug}_geografi', 'Tjänstens geografi'))


def last_stycke(text: str, refs) -> Textstycke:
    return Textstycke(typ='analys', text=text, referenser=list(dict.fromkeys(refs)), proveniens='regelbas')


def _antal(rb: Regelbas, profil: Profil, id: str, status: str, index: Gransindex) -> str:
    return 'okänt' if status == 'saknas' else kort_varde(rb, profil, id, period=True, gransindex=index)


def _erfarenhetsslutsats(e) -> str:
    if not e.belagd:
        return f'Underlaget är ofullständigt och erfarenheten kan inte bedömas. {VERIFIERA}'
    if e.rapporter == 'inga':
        return 'Noll rapporter visar inte frånvaro av hot.'
    return 'Rapporterna är ingen riskpoäng; deras tillvägagångssätt prövas mot tjänstens hot.'


def erfarenhetsstycke_v6(rb: Regelbas, profil: Profil, t: Tjanstbedomning, *,
                         gransindex: Gransindex) -> tuple[Textstycke, ...]:
    """Meningen om egen rapportering och erfarenhet i tjänstens hotdel."""
    e = t.egen_erfarenhet
    if e is None or not all(id in rb.falt for id in ERFARENHETSFALT):
        return ()
    text = (f'Egen rapportering för hela byrån: misstankerapporter {_antal(rb, profil, RAPPORTER, e.rapporter, gransindex)}, '
            f'misstankebaserade avböjanden {_antal(rb, profil, AVBOJANDEN, e.avbojanden, gransindex)}. '
            + _erfarenhetsslutsats(e))
    if e.avbojanden == 'finns':
        text += ' Misstankebaserade avböjanden är egna observationer, inte lämnade rapporter.'
    return (last_stycke(text, (t.tjanst, *ERFARENHETSFALT)),)


def _visning(rb: Regelbas, profil: Profil, id: str, index: Gransindex) -> str:
    if not belagd_uppgift(rb, profil, id):
        return f'aktuellt underlag saknas {VERIFIERA}'
    return kort_varde(rb, profil, id, period=True, gransindex=index)


def _varden(rb: Regelbas, profil: Profil, falt: tuple[str, ...], index: Gransindex) -> str:
    if len(falt) == 1:
        return _visning(rb, profil, falt[0], index)
    return '; '.join(f'{gemen(faltnamn(rb, id))} {_visning(rb, profil, id, index)}' for id in falt)


def _utfall(rb: Regelbas, profil: Profil, id: str) -> Sanning:
    return utvardera(tolka_villkor(rb.sarbarheter[id].villkor, rb.faltdefinitioner()), profil.faltvarden()).sanning


def _motivering(rb: Regelbas, profil: Profil, id: str, index: Gransindex) -> tuple[str, tuple[str, ...]]:
    """Villkor i ord, utfall, värde och period för den första geografiska sårbarheten."""
    s = rb.sarbarheter[id]
    falt = tuple(sorted(falt_i(tolka_villkor(s.villkor, rb.faltdefinitioner()))))
    utfall = _utfall(rb, profil, id)
    text = (f'{s.namn}: Sårbarheten gäller om {villkorstext(s.villkor, rb)}. '
            f'Villkoret är {UTFALL[utfall]}: {_varden(rb, profil, falt, index)}.')
    text += ''.join(' ' + gransmening(rb, profil, g, gransindex=index) for g in under_grans(profil, s.villkor))
    if utfall is Sanning.OKANT:
        text += f' Komplettera underlaget innan sårbarheten kan bedömas. {VERIFIERA}'
    return text, falt


def _ovriga(rb: Regelbas, profil: Profil, ids: tuple[str, ...]) -> str:
    """Övriga geografiska villkor med utfall; deras värden står i B1."""
    if not ids:
        return ''
    grupper: dict[Sanning, list[str]] = {}
    for id in ids:
        grupper.setdefault(_utfall(rb, profil, id), []).append(rb.sarbarheter[id].namn)
    delar = []
    if Sanning.FALSKT in grupper:
        antal = len(grupper[Sanning.FALSKT])
        delar.append(f'{antal} inte uppfyllt' if antal == 1 else f'{antal} inte uppfyllda')
    if Sanning.SANT in grupper:
        delar.append('uppfyllt: ' + ', '.join(grupper[Sanning.SANT]))
    if Sanning.OKANT in grupper:
        delar.append('okänt: ' + ', '.join(grupper[Sanning.OKANT]) + ' ' + VERIFIERA)
    return ' Övriga geografiska villkor: ' + '; '.join(delar) + '.'


def geografistycke_v6(rb: Regelbas, profil: Profil, tjanst: str, *,
                      gransindex: Gransindex) -> tuple[Textstycke, ...]:
    """Geografins underlagsstycke i tjänstens sårbarhetsdel, med villkor, värde, period och källa."""
    ids = tuple(id for id in rb.tjanster[tjanst].sarbarheter if rb.sarbarheter[id].omrade == 'geo')
    if not ids:
        return ()
    vy = kompatibilitetsvy(profil, rb)
    text, falt = _motivering(rb, vy, ids[0], gransindex)
    text += _ovriga(rb, vy, ids[1:]) + ' Villkoren utesluter inte andra geografiska risker, även inom Sverige.'
    refs = [tjanst, *ids, *falt]
    slug = rb.tjanster[tjanst].erbjuds_falt.removesuffix('_erbjuds')
    skrivet: list[str] = []
    for mall, namn in GEOGRAFIBESKRIVNINGAR:
        ref = mall.format(slug=slug)
        if ref not in rb.falt:
            continue
        refs.append(ref)
        if _upprepar_beskrivning(rb, vy, ref, skrivet, gransindex):
            continue
        skrivet.append(uppgiftstext(rb, vy, ref, namn=_GEMENSAMT_NAMN, gransindex=gransindex))
        text += ' ' + uppgiftstext(rb, vy, ref, namn=namn, gransindex=gransindex)
    return (last_stycke(text, refs),)


def _upprepar_beskrivning(rb: Regelbas, profil: Profil, ref: str, skrivet: list[str], index: Gransindex) -> bool:
    """Sant när en belagd beskrivning har samma visade värde, källa och period som en redan skriven.

    Referensen behålls av anroparen, så granskningsreglerna B-09 och B-10 ser bindningen ändå."""
    return (belagd_uppgift(rb, profil, ref)
            and uppgiftstext(rb, profil, ref, namn=_GEMENSAMT_NAMN, gransindex=index) in skrivet)


def lasta_stycken_v6(rb: Regelbas, profil: Profil, t: Tjanstbedomning, del_id: str, *,
                     gransindex: Gransindex) -> tuple[Textstycke, ...]:
    """Programmets låsta stycken i AI-delen hot eller sårbarheter."""
    if del_id == 'hot':
        return erfarenhetsstycke_v6(rb, profil, t, gransindex=gransindex)
    return geografistycke_v6(rb, profil, t.tjanst, gransindex=gransindex)
