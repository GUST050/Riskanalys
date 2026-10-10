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
    lydelse: Lydelse | None
    beskrivning: str | None = None


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
    if regelbas.utokade_krav and not paket.paragrafkarta.galler(datum):
        raise UrvalsFel(f"{paket_id}: paragrafkartan gäller inte {datum}. Välj ett datum inom paketets kontrollerade giltighet.")
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
        for lydelse_id in krav.lydelser
        if regelbas.lydelser[lydelse_id].ikraft > urval.datum
        and lydelse_galler_i_lan(regelbas, regelbas.lydelser[lydelse_id], urval.lan)
    ]
    return tuple(sorted(andringar, key=lambda andring: (andring.lydelse.ikraft, andring.krav_id)))


def beskriv_vantande(andring: VantandeAndring) -> str:
    if andring.beskrivning:
        return andring.beskrivning
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
    if not _krav_galler(krav, datum):
        return None
    giltiga = [regelbas.lydelser[i] for i in krav.lydelser
               if lydelse_galler(regelbas.lydelser[i], datum)
               and lydelse_galler_i_lan(regelbas, regelbas.lydelser[i], lan)
               and _kalla_galler(regelbas, regelbas.lydelser[i], datum)]
    if len(giltiga) > 1:
        raise UrvalsFel(
            f"{krav.id} har flera giltiga lydelser {datum.isoformat()}: "
            f"{', '.join(lydelse.id for lydelse in giltiga)}. Rätta datumen i regelbas/lydelser.yaml."
        )
    if not giltiga and regelbas.utokade_krav and krav.grund == "ska_krav":
        raise UrvalsFel(f"{krav.id} saknar giltig lydelse för {lan} {datum}. Kontrollera källans datum och geografi.")
    return ValtKrav(krav, giltiga[0]) if giltiga else None


def _krav_galler(krav: Krav, datum: date) -> bool:
    efter_start = krav.ikraft is None or krav.ikraft <= datum
    fore_slut = krav.upphor is None or datum < krav.upphor
    return efter_start and fore_slut


def lydelse_galler_i_lan(regelbas: Regelbas, lydelse: Lydelse, lan: str) -> bool:
    geografi = regelbas.kallor[lydelse.kalla].geografi
    return not geografi or lan in geografi


def _kalla_galler(regelbas: Regelbas, lydelse: Lydelse, datum: date) -> bool:
    kalla = regelbas.kallor[lydelse.kalla]
    return (kalla.galler_fran is None or kalla.galler_fran <= datum) and (
        kalla.galler_till is None or datum < kalla.galler_till
    )


def andringar_mellan(regelbas: Regelbas, urval: Urval, beslutsdatum: date) -> tuple[VantandeAndring, ...]:
    """Jämför versioner, inte bara ordalydelse, vid det verkliga beslutets datum."""
    nytt = valj(regelbas, urval.regelpaket.id, beslutsdatum, urval.lan)
    gamla = {v.krav.id: v for v in urval.krav}
    nya = {v.krav.id: v for v in nytt.krav}
    andringar = []
    for id in sorted(gamla.keys() | nya.keys()):
        gammalt, nytt_krav = gamla.get(id), nya.get(id)
        if gammalt == nytt_krav:
            continue
        valt = nytt_krav or gammalt
        text = None if nytt_krav else f"{id} upphör att ingå vid beslutets datum {beslutsdatum}."
        andringar.append(VantandeAndring(id, valt.krav.uppfylls_i, valt.lydelse, text))
    # Kundraderna har egen giltighet och egna lydelser. De följer inte ARB-urvalet.
    if regelbas.kundmall:
        for rad in regelbas.kundmall.rader:
            def giltighet(datum):
                aktiv = (rad.ikraft is None or rad.ikraft <= datum) and (rad.upphor is None or datum < rad.upphor)
                lydelser = tuple(sorted(id for id in rad.lydelser
                    if lydelse_galler(regelbas.kundmall.lydelser[id], datum)
                    and _kalla_galler(regelbas, regelbas.kundmall.lydelser[id], datum)))
                return aktiv, lydelser
            if giltighet(urval.datum) != giltighet(beslutsdatum):
                andringar.append(VantandeAndring(rad.id, (), None,
                    f"Kundrad {rad.id} har ändrad datumgiltighet mellan {urval.datum} och {beslutsdatum}."))
    # Även referenskällor utanför ARB-kraven påverkar metodens giltighet.
    for id, kalla in regelbas.kallor.items():
        def galler(datum):
            return (kalla.galler_fran is None or kalla.galler_fran <= datum) and (kalla.galler_till is None or datum < kalla.galler_till)
        if galler(urval.datum) != galler(beslutsdatum):
            andringar.append(VantandeAndring(id, (), None,
                f"Källa {id} har ändrad datumgiltighet mellan {urval.datum} och {beslutsdatum}."))
    return tuple(andringar)
