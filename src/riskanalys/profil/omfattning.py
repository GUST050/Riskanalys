"""Spårbara andelar härleds ur bekräftade antal/belopp med samma period."""

import math

from riskanalys.profil.modeller import Profil, Uppgift
from riskanalys.regelverk.modeller import Falt, Regelbas
from riskanalys.regelverk.villkor import Sanning, tolka_villkor, utvardera


def aktivt(falt: Falt, profil: Profil, regelbas: Regelbas) -> bool:
    """Okänd aktivering kräver uppgifter; bara uttryckligen falskt är inaktivt."""
    if falt.kritisk_om is None:
        return True
    utfall = utvardera(tolka_villkor(falt.kritisk_om, regelbas.faltdefinitioner()), profil.faltvarden())
    return utfall.sanning is not Sanning.FALSKT


def _par(falt: Falt, profil: Profil) -> tuple[Uppgift, Uppgift] | None:
    """Godta bara belagda tal med samma period och en positiv gemensam bas."""
    antal = profil.uppgifter.get(falt.antalfalt)
    bas = profil.uppgifter.get(falt.basfalt)
    if not antal or not bas or any(u.status != 'bekräftad' or u.inaktuell for u in (antal, bas)):
        return None
    if not antal.period or antal.period != bas.period:
        return None
    if any(type(u.varde) not in (int, float) or not math.isfinite(u.varde) for u in (antal, bas)):
        return None
    if antal.varde < 0 or bas.varde <= 0 or antal.varde > bas.varde:
        return None
    if any(not u.kalla or not u.kalla.strip() or not u.bekraftad_av or u.datum is None for u in (antal, bas)):
        return None
    return antal, bas


def harled_andelar(profil: Profil, regelbas: Regelbas, andrade_falt: frozenset[str] = frozenset()) -> Profil:
    """Härled från giltiga baser; bevara äldre belägg och markera inaktuella värden."""
    vy = kompatibilitetsvy(profil, regelbas)
    uppgifter = dict(profil.uppgifter)
    for falt in regelbas.falt.values():
        if not falt.antalfalt or not falt.basfalt:
            continue
        par = _par(falt, vy) if aktivt(falt, vy, regelbas) else None
        tidigare = uppgifter.get(falt.id, Uppgift())
        manuell = tidigare.status == 'bekräftad' and not tidigare.harledd
        bas_bekraftad = bool(andrade_falt & {falt.antalfalt, falt.basfalt})
        if par is None or (manuell and not bas_bekraftad):
            if tidigare.status in {'bekräftad', 'föreslagen'}:
                uppgifter[falt.id] = tidigare.model_copy(update={'inaktuell': True})
        else:
            antal, bas = par
            uppgifter[falt.id] = Uppgift(
                varde=antal.varde / bas.varde, status='bekräftad',
                kalla=f'Härledning: {falt.antalfalt}/{falt.basfalt}', datum=max(antal.datum, bas.datum),
                bekraftad_av='system:harledning', period=antal.period, harledd=True,
            )
    return profil.model_copy(update={'uppgifter': uppgifter})


def omfattningsbrister(profil: Profil, regelbas: Regelbas) -> list[str]:
    """Upptäck motstridiga alias, handändrade andelar och oförenlig statistik."""
    fel: list[str] = []
    vy = kompatibilitetsvy(profil, regelbas)
    for falt in regelbas.falt.values():
        uppgift = profil.uppgifter.get(falt.id, Uppgift())
        if falt.alias_for:
            kanonisk = profil.uppgifter.get(falt.alias_for, Uppgift())
            if uppgift.status == kanonisk.status == 'bekräftad' and uppgift.varde != kanonisk.varde:
                fel.append(f'{falt.id} och {falt.alias_for} är motstridiga. Bekräfta samma erbjudande.')
        if not aktivt(falt, vy, regelbas):
            continue
        if falt.periodkrav and uppgift.status == 'bekräftad' and not uppgift.period:
            fel.append(f'{falt.id}: bekräfta statistiken med --period-fran och --period-till.')
        if falt.antalfalt and falt.basfalt:
            par = _par(falt, profil)
            if par is None:
                fel.append(
                    f'{falt.id}: bekräfta {falt.antalfalt} och {falt.basfalt} med samma period, '
                    'icke-negativt antal/belopp och positiv bas. Andelen är okänd.'
                )
            elif uppgift.status == 'bekräftad' and (
                uppgift.inaktuell or not uppgift.harledd or uppgift.varde != par[0].varde / par[1].varde
                or uppgift.period != par[0].period
            ):
                fel.append(
                    f'{falt.id}: direkt bekräftad eller ändrad andel är inte tillåten. '
                    'Bekräfta antal och bas och kör härledningen.'
                )
        elif (falt.periodkrav and uppgift.status == 'bekräftad'
              and type(uppgift.varde) in (int, float) and uppgift.varde < 0):
            fel.append(f'{falt.id}: antal och belopp får inte vara negativa.')
    # Tjänstkundantal överlappar; tjänstintäkter ska däremot klassas utan dubbelräkning.
    bas = profil.uppgifter.get('P-VERK.omsattning', Uppgift())
    intakter = [
        profil.uppgifter.get(falt.id, Uppgift()) for falt in regelbas.falt.values()
        if falt.id.startswith('P-TJ.') and falt.id.endswith('_omsattning') and falt.typ != 'andel'
        and aktivt(falt, profil, regelbas)
    ]
    kanda = [u for u in intakter if u.status == 'bekräftad' and type(u.varde) in (int, float)]
    if bas.status == 'bekräftad' and type(bas.varde) in (int, float):
        if any(u.period != bas.period for u in kanda):
            fel.append('Tjänsternas intäkter ska avse samma period som P-VERK.omsattning.')
        elif sum(u.varde for u in kanda) > bas.varde:
            fel.append('Tjänsternas intäkter överstiger byråns omsättning. Rätta klassningen utan dubbelräkning.')
    return fel


def kompatibilitetsvy(profil: Profil, regelbas: Regelbas) -> Profil:
    """Gamla erbjudandefält läses som alias; den sparade profilen ändras aldrig."""
    uppgifter = dict(profil.uppgifter)
    for falt in regelbas.falt.values():
        if not falt.alias_for:
            continue
        alias = uppgifter.get(falt.id, Uppgift())
        kanonisk = uppgifter.get(falt.alias_for, Uppgift())
        if kanonisk.status == 'saknas' and alias.status == 'bekräftad':
            uppgifter[falt.alias_for] = alias
    return profil.model_copy(update={'uppgifter': uppgifter})
