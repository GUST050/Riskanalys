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
    " Beakta byråns egna rapporter och misstankebaserade avböjanden som hotunderlag när de finns. "
    "Antalen är byråövergripande, inte tjänstespecifika riskpoäng; noll rapporter bevisar inte frånvaro av hot. "
    "Motivera sårbarheternas tillämplighet med det skyddade underlaget."
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
    from riskanalys.profil.omfattning import kompatibilitetsvy
    profil = kompatibilitetsvy(profil, regelbas)
    villkor = tolka_villkor(regelbas.sarbarheter[sarbarhet_id].villkor, regelbas.faltdefinitioner())
    return _STATUS[utvardera(villkor, profil.faltvarden()).sanning]


def kontrollstatus(kontroll: Kontrollbedomning) -> str:
    if kontroll.effekt_belagd is not None:
        text = f"utformning {kontroll.utformning or 'okänd'}, genomförande {kontroll.genomforande or 'okänt'}, effekt {kontroll.effekt or 'okänd'}"
        return text + ("; belagd riskreducerande verkan enligt metodvillkor" if kontroll.fungerar_och_ar_belagd
                       else "; ingen riskreduktion är belagd")
    if kontroll.utformning is None:
        return "okänt om kontrollen finns i rutinerna"
    if kontroll.utformning == "saknas":
        return "saknas i rutinerna"
    if kontroll.genomforande is None:
        return "finns i rutinerna, okänt om den är belagd"
    if kontroll.genomforande == "belagt":
        return "finns i rutinerna och är belagd"
    return "finns i rutinerna men är inte belagd"


def visa_for_ai(regelbas: Regelbas, falt_id: str, uppgift: Uppgift, antal: int | None = None) -> str:
    falt = regelbas.falt[falt_id]
    if uppgift.status == "ej_tillämplig":
        return "ej tillämplig"
    if uppgift.status != "bekräftad" or uppgift.inaktuell:
        return "okänt"
    if falt.smagrupp and ((falt.typ == "heltal" and uppgift.varde < SMA_GRUPPER_GRANS) or (antal is not None and antal < SMA_GRUPPER_GRANS)):
        return f"färre än {SMA_GRUPPER_GRANS}"
    return visa_varde(falt, uppgift.varde)


def bygg_underlag(
    regelbas: Regelbas, profil: Profil, tjanstbedomning: Tjanstbedomning, avsnitt_id: str
) -> Avsnittsunderlag:
    from riskanalys.profil.omfattning import kompatibilitetsvy, aktivt
    profil = kompatibilitetsvy(profil, regelbas)
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
                motivering=_sarbarhetsmotivering(regelbas, profil, sarbarhet_id, lista.falt),
            )
            for sarbarhet_id in tjanst.sarbarheter
        ),
        kontroller=tuple(
            UnderlagKontroll(id=kontroll.id, namn=regelbas.kontroller[kontroll.id].namn, status=kontrollstatus(kontroll))
            for kontroll in (*tjanstbedomning.kontroller,
                *((tjanstbedomning.sanktionsrisk.kontroll,) if tjanstbedomning.sanktionsrisk and tjanstbedomning.sanktionsrisk.kontroll else ()))
        ),
        uppgifter=tuple(_uppgift(regelbas, profil, falt_id) for falt_id in lista.falt if aktivt(regelbas.falt[falt_id], profil, regelbas)),
        regelspar=tjanstbedomning.regelspar + (tjanstbedomning.sanktionsrisk.regelspar if tjanstbedomning.sanktionsrisk else ()),
        undvik=tuple(UnderlagBrist(id=brist_id, namn=regelbas.bristmonster[brist_id].namn) for brist_id in lista.undvik),
    )


def _sarbarhetsmotivering(regelbas: Regelbas, profil: Profil, id: str, tillatna: tuple[str, ...]) -> str:
    from riskanalys.regelverk.villkor import falt_i
    s = regelbas.sarbarheter[id]
    status = sarbarhet_status(regelbas, profil, id)
    falt = sorted(falt_i(tolka_villkor(s.villkor, regelbas.faltdefinitioner())))
    rader = []
    for ref in falt:
        if ref not in tillatna:
            rader.append(f"{ref}: underlag lämnas inte till AI; motiveringen behöver granskas lokalt.")
            continue
        u = _uppgift(regelbas, profil, ref)
        period = f" Period: {'–'.join(u.period)}." if u.period else ""
        rader.append(f"{ref}: {u.varde}.{period}")
    return f"Det registrerade villkorets utfall är {status}. " + " ".join(rader)


def _kontrollera_lista(regelbas: Regelbas, falt: tuple[str, ...]) -> None:
    for falt_id in falt:
        if falt_id not in regelbas.falt:
            raise UnderlagsFel(f"Fältet {falt_id} i tillåtelselistan finns inte i regelbasen.")
        if regelbas.falt[falt_id].personuppgift or regelbas.falt[falt_id].typ == "text":
            raise UnderlagsFel(f"Fältet {falt_id} är en personuppgift och får inte skickas till AI. Rätta tillåtelselistan.")


def _nivaer(tjanst: Tjanstbedomning) -> dict[str, str]:
    if tjanst.inneboende is None or tjanst.terrorfinansiering is None or tjanst.kvarstaende is None:
        raise UnderlagsFel(f"Tjänsten {tjanst.tjanst} saknar risknivåer och kan inte få ett riskavsnitt.")
    nivaer = {
        "inneboende_sannolikhet": tjanst.inneboende.sannolikhet,
        "inneboende_konsekvens": tjanst.inneboende.konsekvens,
        "inneboende_risk": tjanst.inneboende.risk,
        "terrorfinansiering_sannolikhet": tjanst.terrorfinansiering.sannolikhet,
        "terrorfinansiering_konsekvens": tjanst.terrorfinansiering.konsekvens,
        "terrorfinansiering_risk": tjanst.terrorfinansiering.risk,
        "kvarstaende_risk": tjanst.kvarstaende,
    }
    if tjanst.sanktionsrisk and tjanst.sanktionsrisk.inneboende:
        sank = tjanst.sanktionsrisk
        nivaer.update(sanktioner_sannolikhet=sank.inneboende.sannolikhet,
            sanktioner_konsekvens=sank.inneboende.konsekvens, sanktioner_risk=sank.inneboende.risk,
            kvarstaende_sanktioner_risk=sank.kvarstaende)
    return nivaer


def _bekraftat_antal(profil: Profil, falt_id: str | None) -> int | None:
    """Inaktuella antal får varken röja belopp eller användas i gruppskyddet."""
    uppgift = profil.uppgifter.get(falt_id)
    if (uppgift and uppgift.status == "bekräftad" and not uppgift.inaktuell
            and type(uppgift.varde) is int and uppgift.varde >= 0):
        return uppgift.varde
    return None


def _litet_komplement(regelbas: Regelbas, profil: Profil, antal_id: str | None) -> bool:
    """Skydda även en liten restgrupp när antal och kundbas avser samma period."""
    if not regelbas.utokade_krav or antal_id is None:
        return False
    antal = _bekraftat_antal(profil, antal_id)
    if antal is None:
        return False
    for andel in regelbas.falt.values():
        if andel.antalfalt != antal_id or not andel.basfalt:
            continue
        bas = _bekraftat_antal(profil, andel.basfalt)
        antaluppgift = profil.uppgifter[antal_id]
        basuppgift = profil.uppgifter.get(andel.basfalt)
        if (bas is not None and basuppgift and antaluppgift.period is not None
                and antaluppgift.period == basuppgift.period and 0 < bas - antal < SMA_GRUPPER_GRANS):
            return True
    return False


def _uppgift(regelbas: Regelbas, profil: Profil, falt_id: str) -> UnderlagUppgift:
    """Visa tillåtna uppgifter utan exakta små grupper eller små komplement."""
    uppgift = profil.uppgifter.get(falt_id, Uppgift())
    falt = regelbas.falt[falt_id]
    antal_id = falt.smagruppsantal or falt.antalfalt
    if falt.smagrupp and falt.typ == "heltal":
        antal_id = falt.id
    antal = _bekraftat_antal(profil, antal_id)
    undertryckt = falt.smagrupp and antal is not None and antal < SMA_GRUPPER_GRANS
    saknad_bas = regelbas.utokade_krav and falt.smagrupp and bool(antal_id) and antal is None
    komplement = falt.smagrupp and _litet_komplement(regelbas, profil, antal_id)
    basuppgift = profil.uppgifter.get(falt.basfalt)
    visa_bas = (basuppgift and basuppgift.status == "bekräftad" and not basuppgift.inaktuell
                and not undertryckt and not saknad_bas and not komplement)
    varde = "okänt" if saknad_bas else visa_for_ai(regelbas, falt_id, uppgift, antal)
    if komplement and uppgift.status == "bekräftad" and not uppgift.inaktuell:
        varde = "undertryckt (litet komplement)"
    return UnderlagUppgift(
        id=falt_id, fraga=falt.fraga, varde=varde,
        period=(uppgift.period.fran.isoformat(), uppgift.period.till.isoformat()) if uppgift.period else None,
        bas=str(basuppgift.varde) if visa_bas else None,
        bekraftad=uppgift.status == "bekräftad" and not uppgift.inaktuell,
    )
