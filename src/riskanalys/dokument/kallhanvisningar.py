"""Versionsbundna källhänvisningar i den modell som sakgranskas."""

import re
from typing import TypeVar

from riskanalys.dokument.m1_forslag import ar_m1_forslag
from riskanalys.dokument.modeller import Avsnitt, Dokument, Dokumenttabell, Tabellcell, Textstycke
from riskanalys.regelverk.modeller import Regelbas

_GEMENSAM = ' Gemensamma hänvisningar inom avsnittet.'
_HISTORISKT_SUFFIX = re.compile(r'(?: Källor: (?:\[\d+(?:, s\. [\d, ]+)?\](?:, )?)+\.)?(?: Profilbelägg: bilaga B1\.)?$')
_REGISTER = 'Källregister ['
_KORTA_HANVISNINGAR = ('D-ARB-tjanst-v6', 'D-ARB-tjanst-v7')
_Textpost = TypeVar('_Textpost', Textstycke, Tabellcell)


def utan_kallhanvisning(text: str, *, genererad_etikett: str = '') -> str:
    """Rensa källsuffix; etikett bara när anroparen vet att den genererats."""
    utan = _HISTORISKT_SUFFIX.sub('', text)
    if utan != text and genererad_etikett and utan.endswith(genererad_etikett):
        return utan[:-len(genererad_etikett)]
    return utan


def _poster(rb: Regelbas, *, rackvidd: bool = False) -> dict:
    poster = {}
    for namn in ('kallor', 'lydelser', 'krav', 'hot', 'sarbarheter', 'kontroller', 'tjanster',
                 'bristmonster', 'tillamplighet', 'sektorsreferenser'):
        poster.update(getattr(rb, namn))
    poster.update({r.id: r for r in (*rb.metod.regler(), *rb.metod.riskmatris)})
    if rb.sanktionsmetod:
        poster[rb.sanktionsmetod.id] = rb.sanktionsmetod
        poster.update({r.id: r for r in rb.sanktionsmetod.rader})
    if rackvidd:
        poster.update({r.id: r for k in rb.kontroller.values() for r in getattr(k, 'rackvidd', ())})
    return poster


def _kallor(refs, rb: Regelbas, poster: dict, *, formatversion: str = 'D-ARB-tjanst-v5') -> dict[str, set[int]]:
    """Följ källfält, aldrig andra katalogposter som bara finns i inventariet."""
    resultat: dict[str, set[int]] = {}
    besokta = set()

    def lagg_till(id):
        if id in besokta:
            return
        besokta.add(id)
        if formatversion in _KORTA_HANVISNINGAR and id in rb.tjanster:
            return  # Tjänsteinventariet belägger inte återgiven hot-, scenario- eller sektorstext.
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
    ny = dokument.formatversion in ('D-ARB-tjanst-v5.1', 'D-ARB-tjanst-v6', 'D-ARB-tjanst-v7')
    poster = _poster(regelbas, rackvidd=ny)
    kallor = set()
    for avsnitt in dokument.avsnitt:
        if avsnitt.id == 'D-ARB.B1':
            # B1:s inventarium är inte användning av källan. Flyttade beräkningar är det.
            texter = [cell for tabell in avsnitt.tabeller for rad in tabell.rader for cell in rad.celler] if ny else []
            # M1-förslaget använder sin källa, till skillnad från inventariets källversionsrader.
            if dokument.formatversion in ('D-ARB-tjanst-v6', 'D-ARB-tjanst-v7'):
                texter.extend(s for s in avsnitt.stycken if ar_m1_forslag(s.text))
        else:
            texter = [*avsnitt.stycken, *(cell for tabell in avsnitt.tabeller for rad in tabell.rader for cell in rad.celler)]
        for text in texter:
            kallor.update(_kallor(text.referenser, regelbas, poster, formatversion=dokument.formatversion))
    return {id: str(nr) for nr, id in enumerate(sorted(kallor), 1)}


def med_kallhanvisningar(dokument: Dokument, regelbas: Regelbas) -> Dokument:
    """Returnera ny modell med numrerade hänvisningar och register i bilaga B1.

    Referens-ID:n bevaras för granskningsspåret. Sidor visas bara när en
    uttrycklig hänvisning anger sidan; ett katalog-ID är inte ett sidbelägg.
    """
    if dokument.formatversion not in ('D-ARB-tjanst-v5', 'D-ARB-tjanst-v5.1', 'D-ARB-tjanst-v6', 'D-ARB-tjanst-v7'):
        return dokument
    register = bygg_kallregister(dokument, regelbas)
    ny = dokument.formatversion in ('D-ARB-tjanst-v5.1', 'D-ARB-tjanst-v6', 'D-ARB-tjanst-v7')
    v6 = dokument.formatversion in ('D-ARB-tjanst-v6', 'D-ARB-tjanst-v7')
    poster = _poster(regelbas, rackvidd=ny)
    def med_hanvisning(text: _Textpost, visade: set[tuple[str, int | None]] | None = None) -> _Textpost:
        kallor = _kallor(text.referenser, regelbas, poster, formatversion=dokument.formatversion)
        profilbelagg = any(ref.startswith('P-') for ref in text.referenser)
        forsta = visade is not None and not visade
        if visade is not None:
            nya = {}
            for id, sidor in kallor.items():
                nya_sidor = {sida for sida in sidor if (id, sida) not in visade}
                if (id, None) not in visade or nya_sidor:
                    nya[id] = nya_sidor
                visade.add((id, None))
                visade.update((id, sida) for sida in sidor)
            kallor = nya
            profilbelagg = profilbelagg and ('profil', None) not in visade
            if profilbelagg:
                visade.add(('profil', None))
        delar = []
        for id in sorted(kallor):
            if id not in register:
                continue
            sida = ', s. ' + ', '.join(map(str, sorted(kallor[id]))) if kallor[id] else ''
            delar.append(f'[{register[id]}{sida}]')
        suffix = ' Källor: ' + ', '.join(delar) + '.' if delar else ''
        if profilbelagg:
            suffix += ' Profilbelägg: bilaga B1.'
        etikett = (' Hänvisningar.' if dokument.formatversion == 'D-ARB-tjanst-v7' else _GEMENSAM) if forsta and suffix else ''
        return text.model_copy(update={'text': utan_kallhanvisning(text.text, genererad_etikett=etikett) + etikett + suffix})

    def med_tabellhanvisningar(tabell: Dokumenttabell, visade: set[tuple[str, int | None]] | None = None) -> Dokumenttabell:
        if dokument.formatversion not in ('D-ARB-tjanst-v6', 'D-ARB-tjanst-v7'):
            return tabell.model_copy(update={'rader': tuple(rad.model_copy(update={
                'celler': tuple(med_hanvisning(c) for c in rad.celler)}) for rad in tabell.rader)})
        rader = []
        for rad in tabell.rader:
            refs = tuple(dict.fromkeys(ref for cell in rad.celler for ref in cell.referenser))
            celler = rad.celler
            if celler:
                forsta = med_hanvisning(celler[0].model_copy(update={'referenser': refs}), visade)
                celler = (forsta.model_copy(update={'referenser': celler[0].referenser}),
                    *(c.model_copy(update={'text': utan_kallhanvisning(c.text)}) for c in celler[1:]))
            rader.append(rad.model_copy(update={'celler': celler}))
        return tabell.model_copy(update={'rader': tuple(rader)})

    avsnitt = []
    for a in dokument.avsnitt:
        if a.id == 'D-ARB.B1':
            reservkatalog = range(0)
            if dokument.formatversion == 'D-ARB-tjanst-v7':
                from riskanalys.dokument.tjanstavsnitt_v7 import RESERVKATALOG_RUBRIK
                for n, rubrik in enumerate(a.underrubriker):
                    if rubrik.rubrik == RESERVKATALOG_RUBRIK:
                        slut = a.underrubriker[n+1].fore_stycke if n+1 < len(a.underrubriker) else len(a.stycken)
                        reservkatalog = range(rubrik.fore_stycke, slut)
                        break
            # Behåll positionerna även när det gamla registret ersätts och tabeller lagts efter det.
            behall = [i for i, s in enumerate(a.stycken) if not s.text.startswith(_REGISTER)]
            tabeller = tuple(t.model_copy(update={
                'fore_stycke': sum(i < t.fore_stycke for i in behall),
                'rader': med_tabellhanvisningar(t).rader}) for t in a.tabeller) if ny else a.tabeller
            stycken = tuple(med_hanvisning(a.stycken[i]) if i in reservkatalog or (v6 and ar_m1_forslag(a.stycken[i].text))
                else a.stycken[i] for i in behall)
            avsnitt.append(a.model_copy(update={'stycken': stycken, 'tabeller': tabeller}))
            continue
        visade = set() if dokument.formatversion in _KORTA_HANVISNINGAR else None
        stycken = []
        tabeller = list(a.tabeller)
        # Hänvisningar följer faktisk läsordning, även när en tabell står mellan styckena.
        for index in range(len(a.stycken) + 1):
            for n, tabell in enumerate(a.tabeller):
                if tabell.fore_stycke == index:
                    tabeller[n] = med_tabellhanvisningar(tabell, visade)
            if index < len(a.stycken):
                stycken.append(med_hanvisning(a.stycken[index], visade))
        avsnitt.append(a.model_copy(update={'stycken': tuple(stycken), 'tabeller': tuple(tabeller)}))
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
