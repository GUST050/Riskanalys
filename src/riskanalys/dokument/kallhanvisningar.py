"""Läsbara källhänvisningar i den modell som sakgranskas, endast v5."""

import re

from riskanalys.dokument.modeller import Avsnitt, Dokument, Textstycke
from riskanalys.regelverk.modeller import Regelbas

_SUFFIX = re.compile(r'(?: Källor: (?:\[\d+(?:, s\. [\d, ]+)?\](?:, )?)+\.)?(?: Profilbelägg: bilaga B1\.)?$')
_REGISTER = 'Källregister ['


def _poster(rb: Regelbas) -> dict:
    poster = {}
    for namn in ('kallor', 'lydelser', 'krav', 'hot', 'sarbarheter', 'kontroller', 'tjanster',
                 'bristmonster', 'tillamplighet', 'sektorsreferenser'):
        poster.update(getattr(rb, namn))
    poster.update({r.id: r for r in (*rb.metod.regler(), *rb.metod.riskmatris)})
    if rb.sanktionsmetod:
        poster[rb.sanktionsmetod.id] = rb.sanktionsmetod
        poster.update({r.id: r for r in rb.sanktionsmetod.rader})
    return poster


def _kallor(refs, rb: Regelbas, poster: dict) -> dict[str, set[int]]:
    """Följ källfält, aldrig andra katalogposter som bara finns i inventariet."""
    resultat: dict[str, set[int]] = {}
    besokta = set()

    def lagg_till(id):
        if id in besokta:
            return
        besokta.add(id)
        if id in rb.kallor:
            resultat.setdefault(id, set())
            return
        post = poster.get(id)
        if post is None:
            return  # Originalreferensen finns kvar i dokumentet för valideringen.
        for kalla in getattr(post, 'kallor', ()):
            lagg_till(kalla)
        for falt in ('kalla', 'primarkalla'):
            kalla = getattr(post, falt, None)
            if kalla:
                lagg_till(kalla)
        for lydelse in getattr(post, 'lydelser', ()):
            lagg_till(lydelse)
        for hanvisning in getattr(post, 'kallhanvisningar', ()):
            if hanvisning.kalla in rb.kallor:
                resultat.setdefault(hanvisning.kalla, set()).add(hanvisning.sida)
        if getattr(post, 'sida', None) and getattr(post, 'kalla', None) in rb.kallor:
            resultat.setdefault(post.kalla, set()).add(post.sida)

    for ref in refs:
        lagg_till(ref)
    return resultat


def bygg_kallregister(dokument: Dokument, regelbas: Regelbas) -> dict[str, str]:
    """Stabila läsnummer för faktiskt refererade källor utanför B1:s inventarium."""
    poster = _poster(regelbas)
    kallor = set()
    for avsnitt in dokument.avsnitt:
        if avsnitt.id == 'D-ARB.B1':
            continue
        texter = [*avsnitt.stycken, *(cell for tabell in avsnitt.tabeller for rad in tabell.rader for cell in rad.celler)]
        for text in texter:
            kallor.update(_kallor(text.referenser, regelbas, poster))
    return {id: str(nr) for nr, id in enumerate(sorted(kallor), 1)}


def med_kallhanvisningar(dokument: Dokument, regelbas: Regelbas) -> Dokument:
    """Returnera ny modell med numrerade hänvisningar och register i bilaga B1.

    Referens-ID:n bevaras för granskningsspåret. Sidor visas bara när en
    uttrycklig hänvisning anger sidan; ett katalog-ID är inte ett sidbelägg.
    """
    if dokument.formatversion != 'D-ARB-tjanst-v5':
        return dokument
    register = bygg_kallregister(dokument, regelbas)
    poster = _poster(regelbas)

    def med_hanvisning(text):
        kallor = _kallor(text.referenser, regelbas, poster)
        delar = []
        for id in sorted(kallor):
            if id not in register:
                continue
            sida = ', s. ' + ', '.join(map(str, sorted(kallor[id]))) if kallor[id] else ''
            delar.append(f'[{register[id]}{sida}]')
        suffix = ' Källor: ' + ', '.join(delar) + '.' if delar else ''
        if any(ref.startswith('P-') for ref in text.referenser):
            suffix += ' Profilbelägg: bilaga B1.'
        return text.model_copy(update={'text': _SUFFIX.sub('', text.text) + suffix})

    avsnitt = []
    for a in dokument.avsnitt:
        if a.id == 'D-ARB.B1':
            avsnitt.append(a.model_copy(update={'stycken': tuple(s for s in a.stycken if not s.text.startswith(_REGISTER))}))
            continue
        tabeller = tuple(tabell.model_copy(update={'rader': tuple(rad.model_copy(update={
            'celler': tuple(med_hanvisning(c) for c in rad.celler)}) for rad in tabell.rader)}) for tabell in a.tabeller)
        avsnitt.append(a.model_copy(update={'stycken': tuple(med_hanvisning(s) for s in a.stycken), 'tabeller': tabeller}))
    registerstycken = tuple(Textstycke(typ='beskrivning', text=(
        f'{_REGISTER}{nr}]: {regelbas.kallor[id].titel}. {regelbas.kallor[id].utgivare}. {regelbas.kallor[id].url}'),
        referenser=[id]) for id, nr in register.items())
    for index, a in enumerate(avsnitt):
        if a.id == 'D-ARB.B1':
            avsnitt[index] = a.model_copy(update={'stycken': a.stycken + registerstycken})
            break
    else:
        if registerstycken:
            avsnitt.append(Avsnitt(id='D-ARB.B1', rubrik='Bilaga: Källregister', kalla='regelbas', stycken=registerstycken))
    return dokument.model_copy(update={'avsnitt': tuple(avsnitt)})
