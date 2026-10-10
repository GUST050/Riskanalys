"""Kontrollerar att regelbasens poster hänger ihop (spec 6 och 16)."""

import re
from collections import Counter
from collections.abc import Iterable
from itertools import product

from riskanalys.regelverk.modeller import Kartrad, Regelbas, Regelpaket
from riskanalys.regelverk.villkor import VillkorsFel, tolka_villkor

AVSNITT_ID = re.compile(r"^D-[A-Z]+(\.\d+)+$")
KAPITEL = re.compile(r"^(\d+ kap\.)")
KONTROLLVAL = {
    "utformning_falt": ("finns", "saknas"),
    "genomforande_falt": ("belagt", "ej_belagt"),
}
SANNOLIKHETER = ("låg", "medel", "hög")
KONSEKVENSER = ("begränsad", "betydande", "allvarlig")


def validera(regelbas: Regelbas) -> list[str]:
    """Returnerar alla fel i regelbasen. Tom lista betyder att regelbasen är giltig."""
    return [
        *_kallor(regelbas),
        *_lydelser(regelbas),
        *_krav(regelbas),
        *_tjanster(regelbas),
        *_sarbarheter(regelbas),
        *_kontroller(regelbas),
        *_tillatelselistor(regelbas),
        *_regelpaket(regelbas),
        *_sakkunnig(regelbas),
        *_matris(regelbas),
    ]


def _saknas(post_id: str, referenser: Iterable[str], finns: Iterable[str], slag: str = "") -> list[str]:
    tillgangliga = set(finns)
    return [f"{post_id}: hänvisar till {slag}{ref} som inte finns." for ref in referenser if ref not in tillgangliga]


def _kallor(regelbas: Regelbas) -> list[str]:
    samlingar = (
        regelbas.hot,
        regelbas.sarbarheter,
        regelbas.kontroller,
        regelbas.tjanster,
        regelbas.bristmonster,
        regelbas.regelpaket,
    )
    med_lista = [
        fel
        for samling in samlingar
        for post in samling.values()
        for fel in _saknas(post.id, post.kallor, regelbas.kallor, "källan ")
    ]
    med_en = [
        fel
        for post in (*regelbas.lydelser.values(), *regelbas.krav.values())
        for fel in _saknas(post.id, (post.kalla,), regelbas.kallor, "källan ")
    ]
    return med_lista + med_en


def _lydelser(regelbas: Regelbas) -> list[str]:
    return [
        f"{lydelse.id}: upphör {lydelse.upphor} måste vara efter ikraftträdandet {lydelse.ikraft}."
        for lydelse in regelbas.lydelser.values()
        if lydelse.upphor is not None and lydelse.upphor <= lydelse.ikraft
    ]


def _krav(regelbas: Regelbas) -> list[str]:
    definitioner = regelbas.faltdefinitioner()
    fel: list[str] = []
    for krav in regelbas.krav.values():
        try:
            tolka_villkor(krav.galler_om, definitioner)
        except VillkorsFel as undantag:
            fel.append(f"{krav.id}: villkoret galler_om: {undantag}")
        fel += _saknas(krav.id, krav.lydelser, regelbas.lydelser, "lydelsen ")
        fel += [
            f"{krav.id}: lydelsen {lydelse_id} hör till källan {regelbas.lydelser[lydelse_id].kalla}, inte {krav.kalla}."
            for lydelse_id in krav.lydelser
            if lydelse_id in regelbas.lydelser and regelbas.lydelser[lydelse_id].kalla != krav.kalla
        ]
        fel += [
            f"{krav.id}: avsnittet {avsnitt} har fel form. Använd till exempel D-ARB.6.1."
            for avsnitt in krav.uppfylls_i
            if not AVSNITT_ID.match(avsnitt)
        ]
        if krav.ikraft and krav.upphor and krav.upphor <= krav.ikraft:
            fel.append(f"{krav.id}: upphör {krav.upphor} måste vara efter ikraftträdandet {krav.ikraft}.")
    return fel


def _tjanster(regelbas: Regelbas) -> list[str]:
    fel: list[str] = []
    for tjanst in regelbas.tjanster.values():
        falt = regelbas.falt.get(tjanst.erbjuds_falt)
        if falt is None or falt.typ != "bool":
            fel.append(f"{tjanst.id}: fältet {tjanst.erbjuds_falt} för erbjuds måste finnas och vara av typen bool.")
        fel += _saknas(tjanst.id, tjanst.hot, regelbas.hot)
        fel += _saknas(tjanst.id, tjanst.sarbarheter, regelbas.sarbarheter)
        fel += _saknas(tjanst.id, tjanst.kontroller, regelbas.kontroller)
    return fel


def _sarbarheter(regelbas: Regelbas) -> list[str]:
    definitioner = regelbas.faltdefinitioner()
    fel: list[str] = []
    for sarbarhet in regelbas.sarbarheter.values():
        try:
            tolka_villkor(sarbarhet.villkor, definitioner)
        except VillkorsFel as undantag:
            fel.append(f"{sarbarhet.id}: {undantag}")
    return fel


def _kontroller(regelbas: Regelbas) -> list[str]:
    fel: list[str] = []
    for kontroll in regelbas.kontroller.values():
        for attribut, alternativ in KONTROLLVAL.items():
            falt_id = getattr(kontroll, attribut)
            falt = regelbas.falt.get(falt_id)
            if falt is None or falt.typ != "val" or tuple(falt.val) != alternativ:
                fel.append(
                    f"{kontroll.id}: fältet {falt_id} måste vara ett val med alternativen {', '.join(alternativ)}."
                )
    return fel


def _tillatelselistor(regelbas: Regelbas) -> list[str]:
    fel: list[str] = []
    for lista in regelbas.tillatelselistor.values():
        fel += _saknas(lista.id, lista.falt, regelbas.falt)
        fel += [
            f"{lista.id}: fältet {falt_id} är en personuppgift och får inte skickas till AI."
            for falt_id in lista.falt
            if falt_id in regelbas.falt and regelbas.falt[falt_id].personuppgift
        ]
        fel += _saknas(lista.id, lista.undvik, regelbas.bristmonster)
    return fel


def _regelpaket(regelbas: Regelbas) -> list[str]:
    return [
        fel
        for paket in regelbas.regelpaket.values()
        for fel in (
            *_saknas(paket.id, paket.krav, regelbas.krav),
            *_saknas(paket.id, paket.tjanster, regelbas.tjanster),
            *_paragrafkarta(regelbas, paket),
        )
    ]


def _kapitel(lagrum: str) -> str:
    traff = KAPITEL.match(lagrum)
    return traff.group(1) if traff else ""


def _paragrafkarta(regelbas: Regelbas, paket: Regelpaket) -> list[str]:
    """Kartan ska ha exakt en rad för varje paragraf i sin omfattning, och varje krav i paketet ska stå på den."""
    karta = paket.paragrafkarta
    namn = f"Paragrafkartan för {paket.id}"
    fel = []
    if karta.giltig_till is not None and karta.giltig_till <= karta.giltig_fran:
        fel.append(f"{namn}: giltig_till måste vara efter giltig_fran.")
    forvantade: list[tuple[str, str]] = []
    for omfattning in karta.omfattning:
        kalla = regelbas.kallor.get(omfattning.kalla)
        if kalla is None or not kalla.paragrafer:
            fel.append(f"{namn}: källan {omfattning.kalla} saknas eller har ingen paragrafindelning.")
            continue
        forvantade += [(kalla.id, lagrum) for lagrum in kalla.paragrafer if _kapitel(lagrum) in omfattning.kapitel]
    rader = Counter((rad.kalla, rad.lagrum) for rad in karta.rader)
    fel += [f"{namn} saknar {kalla} {lagrum}." for kalla, lagrum in forvantade if (kalla, lagrum) not in rader]
    fel += [f"{namn} har {kalla} {lagrum} mer än en gång." for (kalla, lagrum), antal in rader.items() if antal > 1]
    fel += [
        f"{namn}: {kalla} {lagrum} ingår inte i kartans omfattning eller källans paragrafindelning."
        for kalla, lagrum in rader
        if (kalla, lagrum) not in set(forvantade)
    ]
    fel += [rad_fel for rad in karta.rader for rad_fel in _kartrad(regelbas, paket, namn, rad)]
    pa_kartan = {krav_id for rad in karta.rader for krav_id in rad.krav}
    fel += [f"{namn}: kravet {krav_id} i paketet står inte på kartan." for krav_id in paket.krav if krav_id not in pa_kartan]
    return fel


def _kartrad(regelbas: Regelbas, paket: Regelpaket, namn: str, rad: Kartrad) -> list[str]:
    plats = f"{namn}, {rad.kalla} {rad.lagrum}"
    if rad.krav and rad.ej_tillamplig:
        return [f"{plats}: ange antingen krav eller ej_tillamplig, inte båda."]
    fel = []
    for krav_id in rad.krav:
        krav = regelbas.krav.get(krav_id)
        if krav is None or krav_id not in paket.krav:
            fel.append(f"{plats}: kravet {krav_id} finns inte i regelpaketet.")
        elif (krav.kalla, krav.lagrum) != (rad.kalla, rad.lagrum):
            fel.append(f"{plats}: kravet {krav_id} gäller {krav.kalla} {krav.lagrum}.")
    return fel


def _sakkunnig(regelbas: Regelbas) -> list[str]:
    """Status verifierad ska ha granskare, datum och samma kontrollsumma som innehållet har nu."""
    poster = [(krav.id, krav.sakkunnig, regelbas.kravets_innehallssumma(krav.id)) for krav in regelbas.krav.values()] + [
        (f"Paragrafkartan för {paket.id}", paket.paragrafkarta.sakkunnig, regelbas.kartans_innehallssumma(paket.id))
        for paket in regelbas.regelpaket.values()
    ]
    fel = []
    for namn, sakkunnig, summa in poster:
        if sakkunnig.status != "verifierad":
            continue
        if not sakkunnig.av or sakkunnig.datum is None:
            fel.append(f"{namn}: status verifierad kräver att av och datum är ifyllda.")
        if sakkunnig.kontrollsumma != summa:
            fel.append(
                f"{namn}: innehållet har ändrats efter sakkunniggranskningen. Sätt status till ändras, "
                f"eller låt en sakkunnig granska igen och ange kontrollsumman {summa}."
            )
    return fel


def _matris(regelbas: Regelbas) -> list[str]:
    antal = Counter((rad.sannolikhet, rad.konsekvens) for rad in regelbas.metod.riskmatris)
    return [
        f"Riskmatrisen ska ha exakt en rad för {sannolikhet} sannolikhet och {konsekvens} konsekvens, "
        f"har {antal[(sannolikhet, konsekvens)]}."
        for sannolikhet, konsekvens in product(SANNOLIKHETER, KONSEKVENSER)
        if antal[(sannolikhet, konsekvens)] != 1
    ]
