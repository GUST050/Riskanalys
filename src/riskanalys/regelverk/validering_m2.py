"""M2-dependenser får inte falla ur kartor, datatyper eller metodattester."""

from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.villkor import Faltdef, VillkorsFel, tolka_villkor


def m2fel(rb: Regelbas) -> list[str]:
    """Validera M2:s referenser och datatyper för alla innehållsversioner från 1.0."""
    if not rb.utokade_krav:
        return []
    from riskanalys.regelverk.intagskontrakt import intagskontraktsfel
    fel: list[str] = intagskontraktsfel(rb)

    def villkor(id: str, data: dict, definitioner: dict[str, Faltdef]) -> None:
        try:
            tolka_villkor(data, definitioner)
        except VillkorsFel as exc:
            fel.append(f'{id}: {exc}')

    def cykel(id: str, stig: set[str]) -> bool:
        if id in stig:
            return True
        return any(
            cykel(ref, stig | {id}) for ref in rb.sarbarheter[id].ersatter if ref in rb.sarbarheter
        )

    for falt in rb.falt.values():
        for ref in (falt.basfalt, falt.antalfalt, falt.alias_for, falt.smagruppsantal):
            if ref and ref not in rb.falt:
                fel.append(f'{falt.id}: okänd fältreferens {ref}.')
        if bool(falt.basfalt) != bool(falt.antalfalt):
            fel.append(f'{falt.id}: både antal och bas krävs.')
        if falt.alias_for and falt.alias_for in rb.falt:
            kanonisk = rb.falt[falt.alias_for]
            if falt.typ != kanonisk.typ or kanonisk.alias_for:
                fel.append(f'{falt.id}: alias måste ha samma typ och peka på ett kanoniskt fält.')
        if falt.kritisk_om:
            villkor(falt.id, falt.kritisk_om, rb.faltdefinitioner())
    for post in rb.sarbarheter.values():
        for ref in post.ersatter:
            if ref not in rb.sarbarheter or ref == post.id:
                fel.append(f'{post.id}: ogiltig ersätterreferens {ref}.')
        if cykel(post.id, set()):
            fel.append(f'{post.id}: cirkel i ersätterkedjan.')
    if rb.metod.omfattning:
        post = rb.metod.omfattning
        villkor(post.id, post.enkel_villkor, rb.faltdefinitioner())
        villkor(post.id, post.utokad_villkor, rb.faltdefinitioner())
        if any(id not in rb.kallor for id in post.kallor):
            fel.append(f'{post.id}: okänd källa.')
    for post in rb.kontroller.values():
        if bool(post.effekt_falt) != bool(post.utfall_falt):
            fel.append(f'{post.id}: både effekt och utfall krävs.')
        for ref in (post.effekt_falt, post.utfall_falt):
            if ref and ref not in rb.falt:
                fel.append(f'{post.id}: okänt effektfält {ref}.')
    for samling in (rb.hot, rb.sarbarheter, rb.kontroller, rb.tjanster):
        for post in samling.values():
            if getattr(post, 'effekt', None) or hasattr(post, 'grund_sannolikhet'):
                if post.grund != 'metodval':
                    fel.append(f'{post.id}: numerisk riskpåverkan är metodval, inte rättsligt ska-krav.')
            for ref in post.kallhanvisningar:
                if ref.kalla not in rb.kallor or ref.kalla not in post.kallor:
                    fel.append(f'{post.id}: okänd/obunden källhänvisning {ref.kalla}.')
            if getattr(post, 'sektorreferens', None) and post.sektorreferens not in rb.sektorsreferenser:
                fel.append(f'{post.id}: okänd sektorsreferens.')
    for ref in rb.sektorsreferenser.values():
        if ref.kalla not in rb.kallor or ref.sida < 1 or ref.niva not in ref.skala:
            fel.append(f'{ref.id}: felaktig källa, sida eller referensskala.')
    if rb.sanktionsmetod:
        if rb.sanktionsmetod.kontroll not in rb.kontroller:
            fel.append('Sanktionsmetodens kontroll saknas.')
        for rad in rb.sanktionsmetod.rader:
            villkor(rad.id, rad.villkor, rb.faltdefinitioner())
            if any(k not in rb.kallor for k in rad.kallor):
                fel.append(f'{rad.id}: okänd källa.')
    else:
        fel.append('V1 saknar separat sanktionsmetod.')
    if rb.kundmall:
        mall = rb.kundmall
        definitioner = {k: Faltdef(k, falt.typ, falt.val) for k, falt in mall.falt.items()}
        if set(mall.falt) & set(rb.falt) or any(not k.startswith('K-') for k in mall.falt):
            fel.append('Kundfält ska ligga i ett separat K-register.')
        for rad in mall.rader:
            villkor(rad.id, rad.villkor, definitioner)
            if any(id not in rb.lydelser for id in rad.lydelser):
                fel.append(f'{rad.id}: okänd rättslig lydelse.')
            if rad.spar == 'B' and any(id not in mall.atgarder for id in rad.utfall['atgarder']):
                fel.append(f'{rad.id}: odefinierad B-åtgärd.')
    else:
        fel.append('V1 saknar kundmallens A–D-grenar.')
    return fel


def attesthinder(rb: Regelbas, paket_id: str) -> list[str]:
    """Kräv aktuella godkännanden av gemensamma objekt även när paketet godkänts."""
    from riskanalys.regelverk.sakkunnig import granskningsobjekt

    summor = granskningsobjekt(rb, paket_id)
    objekt = [post for samling in (rb.hot, rb.sarbarheter, rb.kontroller, rb.tjanster) for post in samling.values()]
    # Paketets granskning omfattar även krav som inte gäller just denna profil.
    # Ett ändringskrav på gemensamt innehåll får inte döljas av galler_om.
    objekt += [rb.krav[id] for id in rb.regelpaket[paket_id].krav]
    objekt += [*rb.metod.riskmatris, *rb.metod.regler()]
    objekt += [post for post in (rb.skalmappning, rb.sanktionsmetod) if post]
    if rb.kundmall:
        objekt += list(rb.kundmall.rader)
    hinder: list[str] = []
    for post in objekt:
        sakkunnig = post.sakkunnig
        if not sakkunnig.galler(summor[post.id]) or not sakkunnig.av or not sakkunnig.av.strip() or not sakkunnig.datum:
            hinder.append(f'{post.id}: granskningsobjekt saknar aktuell sakkunnigattest.')
    if rb.kundmall and not rb.kundmall.c_granskning.galler(rb.kundmall.c_innehallssumma()):
        hinder.append('KUNDMETOD-C: aktuell metodattest saknas.')
    return hinder
