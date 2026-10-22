"""Villkor för fastställelse (spec 10). Varje hinder är en mening som säger vad som saknas."""

from dataclasses import dataclass
from riskanalys.dokument.presentation_v8 import Presentation
from datetime import date

from riskanalys.analys.modeller import Analyspaket
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
    analys: Analyspaket | None = None
    analysbindning: str | None = None
    presentation: Presentation | None = None


def hinder_for_faststallelse(underlag: Faststallelseunderlag, beslutsdatum: date) -> list[str]:
    """Alla skäl att inte fastställa. Tom lista betyder att villkoren i spec 10 är uppfyllda."""
    return [
        *(['Ofullständigt omfattningsunderlag kan inte fastställas som en allmän riskbedömning.'] if underlag.dokument.id=='OMFATTNING-OFULLSTANDIGT' else []),
        *_uppgifter(underlag),
        *_bedomning(underlag),
        *_omfattning(underlag),
        *_verifiera(underlag),
        *_sakkunnig(underlag),
        *_paragrafkarta(underlag),
        *(rad for post in underlag.fynd for rad in fyndhinder(post)),
        *_analys(underlag),
        *_sakgranskning(underlag),
        *_drift(underlag, beslutsdatum),
        *_kronologi(underlag, beslutsdatum),
        *_m2(underlag, beslutsdatum),
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
    from riskanalys.profil.omfattning import omfattningsbrister
    omfattning = omfattningsbrister(underlag.profil, underlag.regelbas)
    saknade = saknade_kritiska(underlag.profil, underlag.regelbas, underlag.urval)
    hinder = [f"Kritiska uppgifter saknas: {', '.join(saknade)}. Bekräfta dem med 'riskanalys bekrafta'."] if saknade else []
    if any(f.intag for f in underlag.regelbas.falt.values()):
        from riskanalys.intag.tackning import tackning
        t = tackning(underlag.regelbas, underlag.profil)
        hinder.extend(t.hinder)
        if t.saknade:
            hinder.append('Intaget är ofullständigt: ' + ', '.join(t.saknade))
    return [*hinder, *omfattning, *(f"{rad} Bekräfta uppgiften igen med 'riskanalys bekrafta'." for rad in belaggsbrister(underlag.profil))]


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
        galler = galler_sakgranskning(underlag.sakgranskningar, avsnitt, underlag.profil, underlag.dokument, analysbindning=underlag.analysbindning, presentation=underlag.presentation)
        if galler is None:
            hinder.append(f"Avsnitt {avsnitt.id} är inte sakgranskat i nuvarande lydelse.")
        elif not galler.godkand:
            hinder.append(f"Avsnitt {avsnitt.id} underkändes vid sakgranskningen: {galler.kommentar}")
    return hinder


def _drift(underlag: Faststallelseunderlag, beslutsdatum: date) -> list[str]:
    from riskanalys.profil.planering import forandringshinder
    planer = list(forandringshinder(underlag.regelbas, underlag.profil, underlag.profil, underlag.historik, beslutsdatum))
    nasta = underlag.historik.nasta_genomgang()
    if nasta is None:
        return [*planer, "Datum för utvärdering saknas. Registrera utvärderingen med 'riskanalys utvardera'."]
    if nasta < beslutsdatum:
        return [*planer, f"Nästa genomgång skulle ha gjorts senast {nasta.isoformat()}. Utvärdera riskbedömningen igen."]
    return planer


def _kronologi(underlag: Faststallelseunderlag, beslutsdatum: date) -> list[str]:
    """Ett beslut kan inte fattas innan underlaget finns: granskning, sakgranskning, utvärdering och tidigare beslut."""
    sakgranskade = [
        galler.datum
        for avsnitt in underlag.dokument.avsnitt
        if (galler := galler_sakgranskning(underlag.sakgranskningar, avsnitt, underlag.profil, underlag.dokument, analysbindning=underlag.analysbindning, presentation=underlag.presentation)) is not None
    ]
    faststallda = [handelse.datum for handelse in underlag.historik.handelser if handelse.typ == FASTSTALLELSE]
    tidigare = (
        ("granskningen", underlag.granskningsdatum),
        ("den senaste sakgranskningen", max(sakgranskade, default=None)),
        ("den senaste utvärderingen", underlag.historik.senaste_utvardering()),
        ("den senaste fastställelsen", max(faststallda, default=None)),
    )
    from riskanalys.granskning.dokument_v6 import analyskronologihinder
    return [
        *(f"Beslutsdatum {beslutsdatum.isoformat()} är före {namn} {datum.isoformat()}."
          for namn, datum in tidigare
          if datum is not None and beslutsdatum < datum),
        *analyskronologihinder(underlag.bedomning,underlag.analys,beslutsdatum),
    ]


def _omfattning(underlag: Faststallelseunderlag) -> list[str]:
    """Pröva profilen på nytt; äldre sparade bedömningar får inte kringgå M2."""
    if not underlag.regelbas.utokade_krav:
        return []
    from riskanalys.regelverk.tillsyn import rattlig_omfattning
    return list(rattlig_omfattning(underlag.regelbas, underlag.profil).hinder)


def _m2(u: Faststallelseunderlag, datum: date) -> list[str]:
    if not u.regelbas.utokade_krav:
        return []
    from riskanalys.profil.hantering import kontrollera_profil
    from riskanalys.fel import RiskanalysFel
    from riskanalys.regelverk.urval import andringar_mellan, beskriv_vantande
    hinder = []
    try:
        kontrollera_profil(u.profil, u.regelbas)
        hinder += [beskriv_vantande(a) + " Kör om hela kedjan från bedom med beslutets datum."
                   for a in andringar_mellan(u.regelbas, u.urval, datum)]
    except RiskanalysFel as e:
        hinder.append(str(e) + " Rätta profilen eller datumet och kör om kedjan.")
    from riskanalys.regelverk.validering_m2 import attesthinder
    hinder += attesthinder(u.regelbas, u.urval.regelpaket.id)
    paket = u.regelbas.regelpaket[u.urval.regelpaket.id]
    if not paket.granskning.galler(u.regelbas.paketets_innehallssumma(paket.id)) or not paket.granskning.av or not paket.granskning.datum:
        hinder.append("Paketets metod- och kundgrenar är inte verifierade i nuvarande innehåll. Exportera sakkunnigunderlag och importera verkligt granskat beslut.")
    if u.bedomning.omfattning is None:
        hinder.append("Äldre bedömning saknar rättslig omfattning. Kör bedom igen.")
    for t in u.bedomning.tjanster:
        if t.erbjuds is not False and (t.sanktionsrisk is None or t.sanktionsrisk.inneboende is None or t.sanktionsrisk.kvarstaende is None):
            hinder.append(f"{t.tjanst}: sanktionsdimension saknas. Kör bedom igen.")
    return hinder


def _analys(underlag: Faststallelseunderlag) -> list[str]:
    if not underlag.regelbas.metod.omfattning:return []
    from riskanalys.analys.provning import registersumma
    from riskanalys.granskning.dokument_v6 import analyshinder
    hinder=list(analyshinder(underlag.regelbas,underlag.profil,underlag.bedomning,underlag.analys))
    if underlag.analys is None or underlag.analysbindning!=registersumma(underlag.analys):
        hinder.append('Dokumentet saknar korrekt bindning till den frysta analysen.')
    return hinder
