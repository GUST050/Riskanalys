"""Villkor för fastställelse (spec 10). Varje hinder är en mening som säger vad som saknas."""

from dataclasses import dataclass
from datetime import date

from riskanalys.bedomning.modeller import Bedomning
from riskanalys.dokument.modeller import Dokument
from riskanalys.dokument.rendering import har_verifiera
from riskanalys.dokument.validering import VERIFIERA
from riskanalys.drift.historik import Historik
from riskanalys.faststallelse.modeller import Sakgranskning
from riskanalys.faststallelse.sakgranskning import galler_sakgranskning
from riskanalys.granskning.modeller import Fynd
from riskanalys.profil.hantering import belaggsbrister, saknade_kritiska
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.urval import Urval, kravet_galler

ICKE_BINDANDE = frozenset({"allmänt_råd", "tillsynspraxis", "eu_utkast"})
FASTSTALLELSE = "fastställelse"


@dataclass(frozen=True)
class Faststallelseunderlag:
    """Allt som grinden prövar. Läses från den senaste granskningen och den bedömning den hör till.

    historik är versionshistoriken inklusive tidigare fastställelser. granskningsdatum är granskningens datum.
    """

    regelbas: Regelbas
    urval: Urval
    profil: Profil
    bedomning: Bedomning
    dokument: Dokument
    fynd: tuple[Fynd, ...]
    sakgranskningar: tuple[Sakgranskning, ...]
    historik: Historik
    granskningsdatum: date


def hinder_for_faststallelse(underlag: Faststallelseunderlag, beslutsdatum: date) -> list[str]:
    """Alla skäl att inte fastställa. Tom lista betyder att villkoren i spec 10 är uppfyllda."""
    return [
        *_uppgifter(underlag),
        *_bedomning(underlag),
        *_verifiera(underlag),
        *_sakkunnig(underlag),
        *_paragrafkarta(underlag),
        *(rad for post in underlag.fynd for rad in fyndhinder(post)),
        *_sakgranskning(underlag),
        *_drift(underlag, beslutsdatum),
        *_kronologi(underlag, beslutsdatum),
    ]


def fyndhinder(post: Fynd) -> list[str]:
    """Hinder från ett fynd, efter fyndets allvar, status och grund (spec 10, villkor 4)."""
    if post.allvar == "blockerande":
        return [f"{post.id}: blockerande fynd måste åtgärdas. {post.beskrivning}"]
    if post.status == "åtgärdad":
        return []
    if post.status == "öppen":
        return [f"{post.id}: fyndet är öppet. {post.beskrivning}"]
    motivering = (post.motivering or "").strip()
    if post.status == "sakkunnigbedömd":
        return [] if motivering else [f"{post.id}: den sakkunniga bedömningen saknar motivering."]
    if post.grund == "ska_krav":
        return [f"{post.id}: ett lagkrav kan inte accepteras som metodavvikelse. Det kräver en sakkunnig bedömning."]
    if not motivering:
        return [f"{post.id}: avvikelsen saknar motivering."]
    if post.grund in ICKE_BINDANDE and "KRV-" not in motivering:
        return [f"{post.id}: avvikelse från {post.grund} ska hänvisa till det bindande krav (KRV-) som ändå uppfylls."]
    return []


def _uppgifter(underlag: Faststallelseunderlag) -> list[str]:
    """Villkor 1: kritiska uppgifter är bekräftade eller ej tillämpliga, och varje status har sina belägg."""
    saknade = saknade_kritiska(underlag.profil, underlag.regelbas, underlag.urval)
    hinder = [f"Kritiska uppgifter saknas: {', '.join(saknade)}. Bekräfta dem med 'riskanalys bekrafta'."] if saknade else []
    return [*hinder, *(f"{rad} Bekräfta uppgiften igen med 'riskanalys bekrafta'." for rad in belaggsbrister(underlag.profil))]


def _bedomning(underlag: Faststallelseunderlag) -> list[str]:
    if underlag.bedomning.status != "preliminär":
        return []
    return ["Bedömningen är preliminär. Bekräfta de okända uppgifterna och kör 'riskanalys bedom' igen."]


def _verifiera(underlag: Faststallelseunderlag) -> list[str]:
    """Prövar texten så som den skrivs ut, så att också [VERIFIERA: roll] från en platshållare utan namn stoppar."""
    return [
        f"Avsnitt {avsnitt.id} innehåller {VERIFIERA}."
        for avsnitt in underlag.dokument.avsnitt
        if har_verifiera(avsnitt, underlag.profil)
    ]


def _sakkunnig(underlag: Faststallelseunderlag) -> list[str]:
    """Varje krav som gäller byrån ska vara verifierat i just den lydelse det har nu."""
    varden = underlag.profil.faltvarden()
    return [
        f"Kravet {valt.krav.id} ({valt.krav.lagrum}) är inte verifierat av sakkunnig i sin nuvarande lydelse "
        f"(status {valt.krav.sakkunnig.status})."
        for valt in underlag.urval.krav
        if kravet_galler(underlag.regelbas, valt.krav, varden)
        and not valt.krav.sakkunnig.galler(underlag.regelbas.kravets_innehallssumma(valt.krav.id))
    ]


def _paragrafkarta(underlag: Faststallelseunderlag) -> list[str]:
    """Kartan ska vara verifierad i sin nuvarande lydelse, hantera varje paragraf och gälla bedömningens datum."""
    paket = underlag.urval.regelpaket
    karta = paket.paragrafkarta
    namn = f"Paragrafkartan för regelpaketet {paket.id}"
    hinder = []
    if not karta.sakkunnig.galler(underlag.regelbas.kartans_innehallssumma(paket.id)):
        hinder.append(
            f"{namn} är inte verifierad av sakkunnig i sin nuvarande lydelse (status {karta.sakkunnig.status})."
        )
    ohanterade = karta.ohanterade()
    if ohanterade:
        lista = ", ".join(f"{rad.kalla} {rad.lagrum}" for rad in ohanterade)
        hinder.append(f"{namn} har paragrafer som regelbasen ännu inte hanterar: {lista}.")
    if not karta.galler(underlag.bedomning.datum):
        hinder.append(f"{namn} gäller inte bedömningens datum {underlag.bedomning.datum.isoformat()}.")
    return hinder


def _sakgranskning(underlag: Faststallelseunderlag) -> list[str]:
    hinder = []
    for avsnitt in underlag.dokument.avsnitt:
        galler = galler_sakgranskning(underlag.sakgranskningar, avsnitt, underlag.profil)
        if galler is None:
            hinder.append(f"Avsnitt {avsnitt.id} är inte sakgranskat i nuvarande lydelse.")
        elif not galler.godkand:
            hinder.append(f"Avsnitt {avsnitt.id} underkändes vid sakgranskningen: {galler.kommentar}")
    return hinder


def _drift(underlag: Faststallelseunderlag, beslutsdatum: date) -> list[str]:
    nasta = underlag.historik.nasta_genomgang()
    if nasta is None:
        return ["Datum för utvärdering saknas. Registrera utvärderingen med 'riskanalys utvardera'."]
    if nasta < beslutsdatum:
        return [f"Nästa genomgång skulle ha gjorts senast {nasta.isoformat()}. Utvärdera riskbedömningen igen."]
    return []


def _kronologi(underlag: Faststallelseunderlag, beslutsdatum: date) -> list[str]:
    """Ett beslut kan inte fattas innan underlaget finns: granskning, sakgranskning, utvärdering och tidigare beslut."""
    sakgranskade = [
        galler.datum
        for avsnitt in underlag.dokument.avsnitt
        if (galler := galler_sakgranskning(underlag.sakgranskningar, avsnitt, underlag.profil)) is not None
    ]
    faststallda = [handelse.datum for handelse in underlag.historik.handelser if handelse.typ == FASTSTALLELSE]
    tidigare = (
        ("granskningen", underlag.granskningsdatum),
        ("den senaste sakgranskningen", max(sakgranskade, default=None)),
        ("den senaste utvärderingen", underlag.historik.senaste_utvardering()),
        ("den senaste fastställelsen", max(faststallda, default=None)),
    )
    return [
        f"Beslutsdatum {beslutsdatum.isoformat()} är före {namn} {datum.isoformat()}."
        for namn, datum in tidigare
        if datum is not None and beslutsdatum < datum
    ]
