"""AI-underlag för ett riskavsnitt. Byggs bara ur tillåtelselistan (spec 8.2 och 17)."""

from typing import Literal

from riskanalys.bedomning.modeller import Bedomning, Kontrollbedomning, Tjanstbedomning
from riskanalys.dokument.modeller import (
    Avsnittsunderlag,
    UnderlagBrist,
    UnderlagHot,
    UnderlagKontroll,
    UnderlagSarbarhet,
    UnderlagUppgift,
)
from riskanalys.fel import RiskanalysFel
from riskanalys.profil.hantering import visa_varde
from riskanalys.profil.modeller import Profil, Uppgift
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.villkor import Sanning, tolka_villkor, utvardera

AVSNITTSTYP = "risk_per_tjanst"
SMA_GRUPPER_GRANS = 5
NIVANYCKLAR = (
    "inneboende_sannolikhet",
    "inneboende_konsekvens",
    "inneboende_risk",
    "terrorfinansiering_sannolikhet",
    "terrorfinansiering_konsekvens",
    "terrorfinansiering_risk",
    "kvarstaende_risk",
)
INSTRUKTION = (
    "Skriv avsnittet om risken i tjänsten. Beskriv hur tjänsten kan utnyttjas, analysera hoten och "
    "sårbarheterna och motivera risknivåerna med uppgifterna i underlaget. Återge nivåerna exakt och "
    "skriv tydligt vilken nivå som avser vad, till exempel \"Den kvarstående risken är hög.\" eller "
    "\"Risken för finansiering av terrorism bedöms som måttlig.\" "
    "Hänvisa till ID:n i underlaget i fältet referenser. Saknas en uppgift, skriv [VERIFIERA] och "
    "lägg till en oklarhet."
)
_STATUS = {Sanning.SANT: "ja", Sanning.FALSKT: "nej", Sanning.OKANT: "okänt"}


class UnderlagsFel(RiskanalysFel):
    """AI-underlaget kan inte byggas utan att bryta mot tillåtelselistan."""


def avsnitt_for_tjanst(nummer: int) -> str:
    return f"D-ARB.6.{nummer}"


def tjanster_med_avsnitt(bedomning: Bedomning) -> list[tuple[str, Tjanstbedomning]]:
    """Tjänster med risknivåer, numrerade i ordning. En tjänst som inte erbjuds får inget riskavsnitt."""
    bedomda = [tjanst for tjanst in bedomning.tjanster if tjanst.inneboende is not None]
    return [(avsnitt_for_tjanst(nummer), tjanst) for nummer, tjanst in enumerate(bedomda, start=1)]


def sarbarhet_status(regelbas: Regelbas, profil: Profil, sarbarhet_id: str) -> Literal["ja", "nej", "okänt"]:
    villkor = tolka_villkor(regelbas.sarbarheter[sarbarhet_id].villkor, regelbas.faltdefinitioner())
    return _STATUS[utvardera(villkor, profil.faltvarden()).sanning]


def kontrollstatus(kontroll: Kontrollbedomning) -> str:
    if kontroll.utformning is None:
        return "okänt om kontrollen finns i rutinerna"
    if kontroll.utformning == "saknas":
        return "saknas i rutinerna"
    if kontroll.genomforande is None:
        return "finns i rutinerna, okänt om den är belagd"
    if kontroll.genomforande == "belagt":
        return "finns i rutinerna och är belagd"
    return "finns i rutinerna men är inte belagd"


def visa_for_ai(regelbas: Regelbas, falt_id: str, uppgift: Uppgift) -> str:
    falt = regelbas.falt[falt_id]
    if uppgift.status == "ej_tillämplig":
        return "ej tillämplig"
    if uppgift.status != "bekräftad":
        return "okänt"
    if falt.smagrupp and falt.typ == "heltal" and uppgift.varde < SMA_GRUPPER_GRANS:
        return f"färre än {SMA_GRUPPER_GRANS}"
    return visa_varde(falt, uppgift.varde)


def bygg_underlag(
    regelbas: Regelbas, profil: Profil, tjanstbedomning: Tjanstbedomning, avsnitt_id: str
) -> Avsnittsunderlag:
    lista = regelbas.tillatelselistor[AVSNITTSTYP]
    _kontrollera_lista(regelbas, lista.falt)
    tjanst = regelbas.tjanster[tjanstbedomning.tjanst]
    return Avsnittsunderlag(
        avsnitt=avsnitt_id,
        rubrik=tjanst.namn,
        instruktion=INSTRUKTION,
        tjanst_id=tjanst.id,
        tjanst_namn=tjanst.namn,
        tjanst_beskrivning=tjanst.beskrivning,
        nivaer=_nivaer(tjanstbedomning),
        hot=tuple(
            UnderlagHot(id=hot.id, namn=hot.namn, beskrivning=hot.beskrivning)
            for hot in (regelbas.hot[hot_id] for hot_id in tjanstbedomning.hot)
        ),
        sarbarheter=tuple(
            UnderlagSarbarhet(
                id=sarbarhet_id,
                namn=regelbas.sarbarheter[sarbarhet_id].namn,
                galler=sarbarhet_status(regelbas, profil, sarbarhet_id),
            )
            for sarbarhet_id in tjanst.sarbarheter
        ),
        kontroller=tuple(
            UnderlagKontroll(id=kontroll.id, namn=regelbas.kontroller[kontroll.id].namn, status=kontrollstatus(kontroll))
            for kontroll in tjanstbedomning.kontroller
        ),
        uppgifter=tuple(_uppgift(regelbas, profil, falt_id) for falt_id in lista.falt),
        regelspar=tjanstbedomning.regelspar,
        undvik=tuple(UnderlagBrist(id=brist_id, namn=regelbas.bristmonster[brist_id].namn) for brist_id in lista.undvik),
    )


def _kontrollera_lista(regelbas: Regelbas, falt: tuple[str, ...]) -> None:
    for falt_id in falt:
        if falt_id not in regelbas.falt:
            raise UnderlagsFel(f"Fältet {falt_id} i tillåtelselistan finns inte i regelbasen.")
        if regelbas.falt[falt_id].personuppgift:
            raise UnderlagsFel(f"Fältet {falt_id} är en personuppgift och får inte skickas till AI. Rätta tillåtelselistan.")


def _nivaer(tjanst: Tjanstbedomning) -> dict[str, str]:
    if tjanst.inneboende is None or tjanst.terrorfinansiering is None or tjanst.kvarstaende is None:
        raise UnderlagsFel(f"Tjänsten {tjanst.tjanst} saknar risknivåer och kan inte få ett riskavsnitt.")
    return {
        "inneboende_sannolikhet": tjanst.inneboende.sannolikhet,
        "inneboende_konsekvens": tjanst.inneboende.konsekvens,
        "inneboende_risk": tjanst.inneboende.risk,
        "terrorfinansiering_sannolikhet": tjanst.terrorfinansiering.sannolikhet,
        "terrorfinansiering_konsekvens": tjanst.terrorfinansiering.konsekvens,
        "terrorfinansiering_risk": tjanst.terrorfinansiering.risk,
        "kvarstaende_risk": tjanst.kvarstaende,
    }


def _uppgift(regelbas: Regelbas, profil: Profil, falt_id: str) -> UnderlagUppgift:
    uppgift = profil.uppgifter.get(falt_id, Uppgift())
    return UnderlagUppgift(
        id=falt_id,
        fraga=regelbas.falt[falt_id].fraga,
        varde=visa_for_ai(regelbas, falt_id, uppgift),
        bekraftad=uppgift.status == "bekräftad",
    )
