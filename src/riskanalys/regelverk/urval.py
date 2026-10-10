"""Datumstyrt urval av krav och paragraflydelser (spec 6.4) och kravens tillämplighet."""

from dataclasses import dataclass
from datetime import date

from riskanalys.fel import RiskanalysFel
from riskanalys.regelverk.modeller import Krav, Lydelse, Regelbas, Regelpaket
from riskanalys.regelverk.villkor import Faltvarde, Sanning, tolka_villkor, utvardera


class UrvalsFel(RiskanalysFel):
    """Regelpaket, län eller datum ger inget entydigt urval."""


@dataclass(frozen=True)
class ValtKrav:
    krav: Krav
    lydelse: Lydelse


@dataclass(frozen=True)
class VantandeAndring:
    krav_id: str
    avsnitt: tuple[str, ...]
    lydelse: Lydelse


@dataclass(frozen=True)
class Urval:
    regelpaket: Regelpaket
    datum: date
    lan: str
    krav: tuple[ValtKrav, ...]
    tjanster: tuple[str, ...]


def lydelse_galler(lydelse: Lydelse, datum: date) -> bool:
    return lydelse.ikraft <= datum and (lydelse.upphor is None or datum < lydelse.upphor)


def valj(regelbas: Regelbas, paket_id: str, datum: date, lan: str) -> Urval:
    """Väljer de krav och lydelser i ett regelpaket som gäller ett visst datum i ett visst län."""
    paket = _paket(regelbas, paket_id, lan)
    valda = (_valt_krav(regelbas, regelbas.krav[krav_id], datum, lan) for krav_id in paket.krav)
    return Urval(
        regelpaket=paket,
        datum=datum,
        lan=lan,
        krav=tuple(valt for valt in valda if valt is not None),
        tjanster=paket.tjanster,
    )


def vantande_andringar(regelbas: Regelbas, urval: Urval) -> tuple[VantandeAndring, ...]:
    """Lydelser i paketets krav som ännu inte trätt i kraft vid urvalets datum."""
    andringar = [
        VantandeAndring(krav.id, krav.uppfylls_i, regelbas.lydelser[lydelse_id])
        for krav in (regelbas.krav[krav_id] for krav_id in urval.regelpaket.krav)
        if _galler_i_lan(regelbas, krav, urval.lan)
        for lydelse_id in krav.lydelser
        if regelbas.lydelser[lydelse_id].ikraft > urval.datum
    ]
    return tuple(sorted(andringar, key=lambda andring: (andring.lydelse.ikraft, andring.krav_id)))


def beskriv_vantande(andring: VantandeAndring) -> str:
    return (
        f"{andring.krav_id} (avsnitt {', '.join(andring.avsnitt)}) får ny lydelse av "
        f"{andring.lydelse.lagrum} från {andring.lydelse.ikraft.isoformat()}."
    )


def kravet_galler(regelbas: Regelbas, krav: Krav, varden: dict[str, Faltvarde]) -> bool:
    """Om kravet gäller byrån enligt galler_om. Ett okänt utfall räknas som att kravet gäller."""
    utfall = utvardera(tolka_villkor(krav.galler_om, regelbas.faltdefinitioner()), varden)
    return utfall.sanning is not Sanning.FALSKT


def _paket(regelbas: Regelbas, paket_id: str, lan: str) -> Regelpaket:
    if paket_id not in regelbas.regelpaket:
        tillgangliga = ", ".join(sorted(regelbas.regelpaket))
        raise UrvalsFel(f"Regelpaketet {paket_id} finns inte. Tillgängliga: {tillgangliga}.")
    paket = regelbas.regelpaket[paket_id]
    if lan not in paket.lan:
        raise UrvalsFel(f"Regelpaketet {paket_id} gäller inte {lan}. Det gäller: {', '.join(paket.lan)}.")
    return paket


def _valt_krav(regelbas: Regelbas, krav: Krav, datum: date, lan: str) -> ValtKrav | None:
    if not _krav_galler(krav, datum) or not _galler_i_lan(regelbas, krav, lan):
        return None
    giltiga = [regelbas.lydelser[i] for i in krav.lydelser if lydelse_galler(regelbas.lydelser[i], datum)]
    if len(giltiga) > 1:
        raise UrvalsFel(
            f"{krav.id} har flera giltiga lydelser {datum.isoformat()}: "
            f"{', '.join(lydelse.id for lydelse in giltiga)}. Rätta datumen i regelbas/lydelser.yaml."
        )
    return ValtKrav(krav, giltiga[0]) if giltiga else None


def _krav_galler(krav: Krav, datum: date) -> bool:
    efter_start = krav.ikraft is None or krav.ikraft <= datum
    fore_slut = krav.upphor is None or datum < krav.upphor
    return efter_start and fore_slut


def _galler_i_lan(regelbas: Regelbas, krav: Krav, lan: str) -> bool:
    geografi = regelbas.kallor[krav.kalla].geografi
    return not geografi or lan in geografi
