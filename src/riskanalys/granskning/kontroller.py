"""Maskinell granskning av dokumentet: täckning, spårbarhet och bristmönster (spec 9)."""

from datetime import date
from typing import Any

from riskanalys.bedomning.modeller import Bedomning
from riskanalys.dokument.omfattning import dokumentmal, krav_for_dokument
from riskanalys.dokument.modeller import Dokument, Oklarhet
from riskanalys.dokument.rendering import har_verifiera
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.dokument.validering import VERIFIERA, motivering_har_hot_och_sarbarhet
from riskanalys.drift.historik import Historik
from riskanalys.fel import RiskanalysFel
from riskanalys.granskning.modeller import Fynd
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.urval import Urval

from riskanalys.granskning.sektorsrisk import sektorsfynd
from riskanalys.granskning.analys import analysfynd

RISKAVSNITT = "D-ARB.6."


def granska(
    regelbas: Regelbas,
    urval: Urval,
    profil: Profil,
    bedomning: Bedomning,
    dokument: Dokument,
    historik: Historik,
    granskningsdatum: date,
    oklarheter: tuple[tuple[str, Oklarhet], ...] = (),
    *, skrivresultat=None, analys=None, modellrapport=None, analysbrister_filer=(),
) -> tuple[Fynd, ...]:
    """Fynd för dokumentet. oklarheter är AI-utkastens öppna frågor per avsnitt; var och en blir ett fynd."""
    utkast = [
        *_tackning(regelbas, urval, profil, dokument),
        *_preliminar(bedomning),
        *_verifiera(dokument, profil),
        *_oppna_fragor(oklarheter),
        *_sparbarhet(regelbas, dokument, analys),
        *_b04(regelbas, bedomning, dokument),
        # V6:s lokala PT/TF-, scenario- och sårbarhetsprövningar valideras och
        # återbyggs nedan; den äldre AI-motiveringens stycketyp finns inte där.
        *(_b12(regelbas, dokument) if dokument.formatversion != "D-ARB-tjanst-v6" else []),
        *_b16(regelbas, historik),
        *sektorsfynd(regelbas, bedomning, profil),
        *_analys(regelbas, bedomning, profil, dokument, historik, skrivresultat, analys, modellrapport, analysbrister_filer, granskningsdatum=granskningsdatum),
    ]
    return tuple(
        Fynd(id=f"F-{granskningsdatum.isoformat()}-{nummer:03d}", **falt)
        for nummer, falt in enumerate(utkast, start=1)
    )


def _analys(rb, b, p, d, historik, resultat, analys=None, modellrapport=None, analysbrister_filer=(), *, granskningsdatum=None):
    if d.formatversion == "D-ARB-tjanst-v6":
        from riskanalys.granskning.dokument_v6 import analysfynd_v6
        return analysfynd_v6(rb,b,p,d,historik,resultat,analys=analys,modellrapport=modellrapport,analysbrister_filer=analysbrister_filer,granskningsdatum=granskningsdatum)
    if d.formatversion in ("D-ARB-tjanst-v5", "D-ARB-tjanst-v5.1"):
        from riskanalys.granskning.dokument_v5 import analysfynd_v5
        return analysfynd_v5(rb, b, p, d, historik, resultat)
    return analysfynd(rb, b, p, d, resultat)


def _tackning(regelbas: Regelbas, urval: Urval, profil: Profil, dokument: Dokument) -> list[dict[str, Any]]:
    finns = [avsnitt.id for avsnitt in dokument.avsnitt]
    varden = profil.faltvarden()
    return [
        {
            "typ": "tackning",
            "regel": valt.krav.id,
            "allvar": "blockerande",
            "grund": valt.krav.grund,
            "avsnitt": avsnitt,
            "beskrivning": f"Kravet {valt.krav.id} ({valt.krav.lagrum}) ska uppfyllas i avsnitt {avsnitt}, "
            "men avsnittet saknas.",
            "atgard": "Skapa avsnittet. Är det ett riskavsnitt, kör 'riskanalys skriv' och sedan 'riskanalys granska'.",
        }
        for valt in krav_for_dokument(regelbas, urval, profil, dokument.id)
        for avsnitt in dokumentmal(valt.krav, dokument.id)
        if not any(befintligt == avsnitt or befintligt.startswith(avsnitt + ".") for befintligt in finns)
    ]


def _preliminar(bedomning: Bedomning) -> list[dict[str, Any]]:
    if bedomning.status != "preliminär":
        return []
    okanda = sorted({falt_id for tjanst in bedomning.tjanster for falt_id in tjanst.okanda_uppgifter})
    return [
        {
            "typ": "tackning",
            "allvar": "hög",
            "grund": "ska_krav",
            "beskrivning": f"Bedömningen är preliminär. Okända uppgifter: {', '.join(okanda)}.",
            "atgard": "Bekräfta uppgifterna med 'riskanalys bekrafta' och kör 'riskanalys bedom' igen.",
        }
    ]


def _verifiera(dokument: Dokument, profil: Profil) -> list[dict[str, Any]]:
    """[VERIFIERA] i texten så som den skrivs ut, också [VERIFIERA: roll] från en platshållare utan namn."""
    return [
        {
            "typ": "sparbarhet",
            "allvar": "hög",
            "grund": "ska_krav",
            "avsnitt": avsnitt.id,
            "beskrivning": f"Avsnitt {avsnitt.id} innehåller {VERIFIERA}.",
            "atgard": "Bekräfta de uppgifter som saknas och kör om bedömning, skrivning och granskning.",
        }
        for avsnitt in dokument.avsnitt
        if har_verifiera(avsnitt, profil)
    ]


def _oppna_fragor(oklarheter: tuple[tuple[str, Oklarhet], ...]) -> list[dict[str, Any]]:
    """En öppen fråga från AI betyder att en uppgift saknas. Den hanteras som [VERIFIERA] (spec 10, villkor 2)."""
    return [
        {
            "typ": "sparbarhet",
            "allvar": "hög",
            "grund": "ska_krav",
            "avsnitt": avsnitt_id,
            "beskrivning": (
                f"Avsnitt {avsnitt_id} har en öppen fråga från AI-utkastet: {oklarhet.fraga} "
                f"Uppgift som saknas: {oklarhet.saknad_uppgift}."
            ),
            "atgard": "Bekräfta uppgiften med 'riskanalys bekrafta' och kör om bedömning, skrivning och granskning.",
        }
        for avsnitt_id, oklarhet in oklarheter
    ]


def _sparbarhet(regelbas: Regelbas, dokument: Dokument, analys=None) -> list[dict[str, Any]]:
    kanda = regelbas.alla_id()
    if dokument.formatversion in ("D-ARB-tjanst-v5.1", "D-ARB-tjanst-v6"):
        kanda = kanda | set(dokument.avsnitt_med_id())
    if dokument.formatversion == "D-ARB-tjanst-v6":
        from riskanalys.dokument.analysreferenser import bygg_analysreferenser
        kanda = kanda | set(bygg_analysreferenser(analys).etiketter)
    return [
        {
            "typ": "sparbarhet",
            "allvar": "blockerande",
            "grund": "metodval",
            "avsnitt": avsnitt.id,
            "beskrivning": f"Avsnitt {avsnitt.id} hänvisar till {ref}, som inte finns i regelbasen.",
            "atgard": "Ta bort hänvisningen eller rätta regelbasen.",
        }
        for avsnitt in dokument.avsnitt
        for ref in sorted(({ref for stycke in avsnitt.stycken for ref in stycke.referenser}
                           | {ref for tab in avsnitt.tabeller for rad in tab.rader for cell in rad.celler for ref in cell.referenser}) - kanda)
    ]


def _bristmonster(regelbas: Regelbas, monster_id: str, avsnitt: str, beskrivning: str, atgard: str) -> dict[str, Any]:
    post = regelbas.bristmonster.get(monster_id)
    if post is None:
        raise RiskanalysFel(f"Bristmönstret {monster_id} saknas i regelbasen.")
    return {
        "typ": "bristmonster",
        "regel": monster_id,
        "allvar": post.allvar,
        "grund": post.grund,
        "avsnitt": avsnitt,
        "beskrivning": beskrivning,
        "atgard": atgard,
    }


def _b04(regelbas: Regelbas, bedomning: Bedomning, dokument: Dokument) -> list[dict[str, Any]]:
    finns = {avsnitt.id for avsnitt in dokument.avsnitt}
    return [
        _bristmonster(
            regelbas,
            "B-04",
            avsnitt_id,
            f"{regelbas.tjanster[tjanst.tjanst].namn} saknar eget riskavsnitt ({avsnitt_id}).",
            "Kör 'riskanalys skriv' så att varje tjänst får ett eget avsnitt.",
        )
        for avsnitt_id, tjanst in tjanster_med_avsnitt(bedomning)
        if avsnitt_id not in finns
    ]


def _b12(regelbas: Regelbas, dokument: Dokument) -> list[dict[str, Any]]:
    return [
        _bristmonster(
            regelbas,
            "B-12",
            avsnitt.id,
            f"Avsnitt {avsnitt.id} saknar en motivering som hänvisar till hot och sårbarheter.",
            "Skriv om avsnittet med 'riskanalys skriv'.",
        )
        for avsnitt in dokument.avsnitt
        if avsnitt.id.startswith(RISKAVSNITT)
        and not any(
            stycke.typ == "motivering" and motivering_har_hot_och_sarbarhet(stycke) for stycke in avsnitt.stycken
        )
    ]


def _b16(regelbas: Regelbas, historik: Historik) -> list[dict[str, Any]]:
    if historik.nasta_genomgang() is not None:
        return []
    return [
        _bristmonster(
            regelbas,
            "B-16",
            "D-ARB.10",
            "Datum för utvärdering och uppdatering saknas.",
            "Registrera utvärderingen med 'riskanalys utvardera'.",
        )
    ]
