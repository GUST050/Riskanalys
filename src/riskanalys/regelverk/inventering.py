"""Oberoende paragrafinventarium; extraktion är underlag för källgranskning."""

import re
from collections import Counter
from datetime import date

from riskanalys.fel import RiskanalysFel
from riskanalys.regelverk.modeller import InventeradLydelse, Regelbas, _summa

KAPITEL = re.compile(r"^(\d+(?: [a-z])? kap\.)\s+[A-ZÅÄÖ]")
PARAGRAF = re.compile(r"^(\d+(?: [a-z])?) §(?:\s+/(Upphör att gälla|Träder i kraft) ([UI]):(\d{4}-\d{2}-\d{2})/)?(?:\s+(?=[A-Za-zÅÄÖåäö\"–])|$)")
ANDRINGSNOT = re.compile(r"\s*(?:Lag|Förordning) \((\d{4}:\d+)\)\.\s*$")


def inventera_sfs(text: str, kalla_id: str) -> tuple[InventeradLydelse, ...]:
    """Läser SFST:s fulltext, utan rubriker, ändringsnoter och övergångsbestämmelser.

    Endast uttryckliga I/U-datum sätts. Paragrafnummer behöver inte vara obrutna.
    Ändrings-SFS betyder inte att dess verkliga ikraftdatum har kontrollerats.
    """
    rader = [rad.strip() for rad in text.splitlines() if rad.strip()]
    kapitel = None if any(KAPITEL.match(rad) for rad in rader) else ""
    poster: list[InventeradLydelse] = []
    aktuell: dict | None = None
    delar: list[str] = []
    senast: tuple[int, str] | None = None

    def avsluta() -> None:
        if aktuell is None:
            return
        innehall = " ".join(" ".join(delar).split())
        not_ = ANDRINGSNOT.search(innehall)
        genom = f"SFS {not_.group(1)}" if not_ else None
        if not_:
            innehall = innehall[:not_.start()].rstrip()
        poster.append(InventeradLydelse(**aktuell, text=innehall, inford_genom=genom))

    for index, rad in enumerate(rader):
        if rad.startswith("Övergångsbestämmelser"):
            break
        kap = KAPITEL.match(rad)
        par = PARAGRAF.match(rad)
        if kap:
            avsluta()
            kapitel, aktuell, delar, senast = kap.group(1), None, [], None
        elif par and kapitel is not None and (
            senast is None or _nummer(par.group(1)) > senast or
            (par.group(3) and _nummer(par.group(1)) == senast)
        ):
            avsluta()
            grans = date.fromisoformat(par.group(4)) if par.group(4) else None
            aktuell = {
                "kalla": kalla_id, "lagrum": f"{kapitel} {par.group(1)} §".strip(),
                "ikraft": grans if par.group(3) == "I" else None,
                "upphor": grans if par.group(3) == "U" else None,
            }
            delar = [rad[par.end():]]
            senast = _nummer(par.group(1))
        elif aktuell is not None:
            # SFST rubriker står på egna rader strax före nästa paragraf/kapitel.
            kommande = rader[index+1:index+4]
            rubrik = bool(delar) and delar[-1].endswith(".") and rad[:1].isupper() and not rad.endswith((".", ",", ";", ":")) and len(rad) < 95 and any(
                PARAGRAF.match(nasta) or KAPITEL.match(nasta) for nasta in kommande
            ) and all(
                not nasta.endswith((".", ",", ";", ":"))
                for nasta in kommande[:next((i for i, r in enumerate(kommande) if PARAGRAF.match(r) or KAPITEL.match(r)), len(kommande))]
            )
            if not rubrik:
                delar.append(rad)
    avsluta()
    if not poster:
        raise RiskanalysFel(f"Inga paragrafer hittades för {kalla_id}. Kontrollera källformat och fulltext.")
    return tuple(poster)


def _nummer(nummer: str) -> tuple[int, str]:
    siffra, _, bokstav = nummer.partition(" ")
    return int(siffra), bokstav


def inventariesumma(poster: tuple[InventeradLydelse, ...]) -> str:
    ordnade = sorted(poster, key=lambda rad: (rad.kalla, rad.lagrum, str(rad.ikraft), str(rad.upphor)))
    return _summa({"poster": [rad.model_dump(mode="json") for rad in ordnade]})


def kontrollera_inventarium(regelbas: Regelbas, inventarium: tuple[InventeradLydelse, ...]) -> list[str]:
    fel = []
    nycklar = Counter((rad.kalla, rad.lagrum, rad.ikraft, rad.upphor) for rad in inventarium)
    fel += [f"Inventariet har {kalla} {lagrum} i samma datumversion flera gånger." for (kalla, lagrum, _, _), antal in nycklar.items() if antal > 1]
    for kalla_id in sorted({rad.kalla for rad in inventarium}):
        kalla = regelbas.kallor.get(kalla_id)
        if kalla is None:
            fel.append(f"Inventariet hänvisar till okänd källa {kalla_id}.")
            continue
        poster = tuple(rad for rad in inventarium if rad.kalla == kalla_id)
        lagrum = {rad.lagrum for rad in poster}
        for saknat in sorted(lagrum - set(kalla.paragrafer)):
            fel.append(f"Källinventariet för {kalla_id}: {saknat} saknas i källans paragrafindelning.")
        for extra in sorted(set(kalla.paragrafer) - lagrum):
            fel.append(f"Källinventariet för {kalla_id}: {extra} saknas i inventariet.")
        if kalla.inventarium_kontrollsumma and kalla.inventarium_kontrollsumma != inventariesumma(poster):
            fel.append(f"{kalla_id}: inventariets kontrollsumma stämmer inte. Kontrollera original och inventariefil.")
    if regelbas.utokade_krav:
        from riskanalys.regelverk.laddning import lydelsetextens_kontrollsumma
        for i in inventarium:
            match = [l for l in regelbas.lydelser.values() if (l.kalla,l.lagrum,l.ikraft,l.upphor)==(i.kalla,i.lagrum,i.ikraft,i.upphor)]
            if len(match)!=1 or match[0].text_kontrollsumma != lydelsetextens_kontrollsumma(i.text):
                fel.append(f"{i.kalla} {i.lagrum}: inventeringens datum/text stämmer inte med exakt en lydelse.")
        for kalla in regelbas.kallor.values():
            if kalla.typ in ("lag", "förordning", "föreskrift") and (
                not kalla.kontrollsumma or not kalla.inventarium_kontrollsumma or
                not any(rad.kalla == kalla.id for rad in inventarium)
            ):
                fel.append(f"{kalla.id}: v1 kräver källsumma och separat inventarium med kontrollsumma.")
    return fel
