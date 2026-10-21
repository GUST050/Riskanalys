"""V8:s gemensamma faktaunderlag och tjänstens egen prövning av det (B-09, B-10, B-15).

Byråövergripande underlag skrivs en gång i avsnittet Gemensamt faktaunderlag. Varje tjänst har
ett eget, kortare stycke med tjänstens geografi och en hänvisning, så att tjänstens prövning
fortfarande syns och kontrolleras i tjänsteavsnittet. V6- och V7-kontrakten är oförändrade.
"""
from riskanalys.dokument.lasta_v6 import (GEOGRAFIBESKRIVNINGAR, _GEMENSAMT_NAMN, _motivering, _ovriga,
                                          erfarenhetsstycke_v6, last_stycke)
from riskanalys.dokument.klartext import uppgiftstext
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.profil.omfattning import kompatibilitetsvy

GEMENSAMT_ID = 'D-ARB.5'
GEMENSAMT_RUBRIK = 'Gemensamt faktaunderlag'
BYRAGEOGRAFI = 'P-BESK.geografi'


def _geo_ids(rb, tjanst):
    return tuple(id for id in rb.tjanster[tjanst].sarbarheter if rb.sarbarheter[id].omrade == 'geo')


def _med_originalspann(stycke, rb, vy, ref, insatt, offset):
    from riskanalys.dokument.profiloriginal_v8 import spann_for_profiltext
    spann = tuple((a + offset, b + offset) for a, b in spann_for_profiltext(rb, vy, ref, insatt))
    return stycke.model_copy(update={'literala_spann': (*stycke.literala_spann, *spann)}) if spann else stycke


def gemensamt_erfarenhetsstycke(rb, profil, bedomning, *, gransindex):
    """Byråns egna rapportering och erfarenhet, en gång för alla tjänster."""
    for _, t in tjanster_med_avsnitt(bedomning):
        stycken = erfarenhetsstycke_v6(rb, profil, t, gransindex=gransindex)
        if stycken:
            s = stycken[0]
            return (s.model_copy(update={'referenser': [r for r in s.referenser if r != t.tjanst]}),)
    return ()


def gemensamma_geografistycken(rb, profil, bedomning, *, gransindex):
    """Ett stycke per unik uppsättning geografiska villkor: villkor, utfall och byråns geografibeskrivning."""
    vy = kompatibilitetsvy(profil, rb)
    sett, stycken = set(), []
    for _, t in tjanster_med_avsnitt(bedomning):
        ids = _geo_ids(rb, t.tjanst)
        if not ids or ids in sett:
            continue
        sett.add(ids)
        text, falt = _motivering(rb, vy, ids[0], gransindex)
        text += _ovriga(rb, vy, ids[1:]) + ' Villkoren utesluter inte andra geografiska risker, även inom Sverige.'
        refs = [*ids, *falt]
        stycke = last_stycke(text, refs)
        if BYRAGEOGRAFI in rb.falt:
            insatt = uppgiftstext(rb, vy, BYRAGEOGRAFI, namn='Byråns geografibeskrivning', gransindex=gransindex,
                                  bevara_textoriginal=True)
            stycke = _med_originalspann(stycke.model_copy(update={'text': text + ' ' + insatt,
                'referenser': [*refs, BYRAGEOGRAFI]}), rb, vy, BYRAGEOGRAFI, insatt, len(text) + 1)
        stycken.append(stycke)
    return tuple(stycken)


def tjanstens_erfarenhetsstycke(rb, profil, t, *, gransindex):
    """Tjänstens hänvisning till byråns egen rapportering; finns bara när det gemensamma stycket finns."""
    if not erfarenhetsstycke_v6(rb, profil, t, gransindex=gransindex):
        return ()
    return (last_stycke(f'Egen rapportering och erfarenhet gäller hela byrån och redovisas i avsnittet '
                        f'{GEMENSAMT_RUBRIK}. Hur erfarenheterna berör just denna tjänsts hot prövas i '
                        'tjänstens lokala svar.', (t.tjanst, GEMENSAMT_ID)),)


def tjanstens_geografistycke(rb, profil, tjanst, *, gransindex):
    """Tjänstens geografi och hänvisning till byråns geografiska villkor i det gemensamma avsnittet."""
    ids = _geo_ids(rb, tjanst)
    if not ids:
        return ()
    vy = kompatibilitetsvy(profil, rb)
    text = (f'Geografi i tjänsten: villkor, utfall och byråns geografibeskrivning redovisas i avsnittet '
            f'{GEMENSAMT_RUBRIK}.')
    refs = [tjanst, *ids, GEMENSAMT_ID]
    slug = rb.tjanster[tjanst].erbjuds_falt.removesuffix('_erbjuds')
    ref = GEOGRAFIBESKRIVNINGAR[1][0].format(slug=slug)
    stycke = last_stycke(text, refs)
    if ref not in rb.falt:
        return (stycke,)
    refs.append(ref)
    byra = (uppgiftstext(rb, vy, BYRAGEOGRAFI, namn=_GEMENSAMT_NAMN, gransindex=gransindex)
            if BYRAGEOGRAFI in rb.falt else None)
    egen = uppgiftstext(rb, vy, ref, namn=_GEMENSAMT_NAMN, gransindex=gransindex)
    if byra is not None and egen == byra:
        return (last_stycke(text + ' Tjänstens geografi är densamma som byråns beskrivning.', refs),)
    insatt = uppgiftstext(rb, vy, ref, namn=GEOGRAFIBESKRIVNINGAR[1][1], gransindex=gransindex,
                          bevara_textoriginal=True)
    stycke = last_stycke(text + ' ' + insatt, refs)
    return (_med_originalspann(stycke, rb, vy, ref, insatt, len(text) + 1),)
