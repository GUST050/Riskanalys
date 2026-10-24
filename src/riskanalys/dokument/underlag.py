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
from riskanalys.dokument.skrivversion import V6, V7, V8
from riskanalys.intag.verksamhetsval import VERKSAMHETSVAL, erbjuds_aktuellt, verksamhetsval
from riskanalys.profil.hantering import visa_varde, visa_varde_klartext, visa_grans, visa_andel_begransad
from riskanalys.profil.modeller import Profil, Uppgift
from riskanalys.regelverk.granser import metodgranser, metodgransindex
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.villkor import Sanning, tolka_villkor, utvardera

AVSNITTSTYP = "risk_per_tjanst"
SMA_GRUPPER_GRANS = 5
SKYDDAD_VISNING = "skyddat värde, prövas lokalt"  # samma text för liten grupp och liten restgrupp (spec 8.4.10 punkt 8)
LOKALT_UTFALL = "Utfallet redovisas inte i faktabladet; sårbarheten prövas lokalt."
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
    "Skriv en tjänstespecifik analys och motivering av hot och sårbarheter ur underlaget. "
    "Programmet skriver alla nivåmeningar: ange aldrig nivåer för risk, sannolikhet eller konsekvens, "
    "inte heller för delfaktorer. Beskriv med antal, andel, period och egenskap. "
    "Varje stycke ska ha referenser till underlaget. Okända uppgifter kräver [VERIFIERA] och en oklarhet. "
    "Beakta byråns egna rapporter och misstankebaserade avböjanden som hotunderlag. "
    "Antalen är byråövergripande, inte tjänstespecifika riskpoäng; noll rapporter bevisar inte frånvaro av hot."
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


def provas_lokalt(regelbas: Regelbas, profil: Profil, sarbarhet_id: str, tillatna: tuple[str, ...], *, gransindex: dict | None = None) -> bool:
    """Sant när villkoret läser en uppgift som AI inte får se exakt: utanför tillåtelselistan, eller ett
    smågruppsfält som visas maskerat eller okänt. Avgörs ur den synliga vyn (spec 8.4.10)."""
    from riskanalys.regelverk.villkor import falt_i
    villkor = tolka_villkor(regelbas.sarbarheter[sarbarhet_id].villkor, regelbas.faltdefinitioner())
    for falt_id in falt_i(villkor):
        if falt_id not in tillatna:
            return True
        if regelbas.falt[falt_id].smagrupp:
            visning = _uppgift(regelbas, profil, falt_id, gransindex=gransindex).varde
            if visning in (SKYDDAD_VISNING, "okänt"):
                return True
    return False


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


def kontrollstatus_for_ai(kontroll: Kontrollbedomning) -> str:
    """Kontrollens status för AI, byggd enbart av tillåtna kategorifält. Huruvida riskreduktionen är belagd
    bygger också på utfallsfältet och avgörs därför lokalt (spec 8.4.10 punkt 4)."""
    return (f"utformning {kontroll.utformning or 'okänd'}, genomförande {kontroll.genomforande or 'okänt'}, "
            f"bedömd effekt {kontroll.effekt or 'okänd'}; om kontrollen räknas som riskreducerande avgör programmet lokalt")


def _begransad_precision(regelbas: Regelbas, falt_id: str) -> bool:
    """En andel vars antal eller bas inte är tillåtna visas med begränsad precision (spec 8.4.9 punkt 11)."""
    falt = regelbas.falt[falt_id]
    tillatna = regelbas.tillatelselistor[AVSNITTSTYP].falt
    return bool(regelbas.utokade_krav and falt.typ == "andel" and
                any(ref and ref not in tillatna for ref in (falt.antalfalt, falt.basfalt)))


def visa_for_ai(regelbas: Regelbas, falt_id: str, uppgift: Uppgift, antal: int | None = None, *, gransindex: dict | None = None) -> str:
    falt = regelbas.falt[falt_id]
    if uppgift.status == "ej_tillämplig":
        return "ej tillämplig"
    if uppgift.status != "bekräftad" or uppgift.inaktuell:
        return "okänt"
    if falt.smagrupp and ((falt.typ == "heltal" and uppgift.varde < SMA_GRUPPER_GRANS) or (antal is not None and antal < SMA_GRUPPER_GRANS)):
        return SKYDDAD_VISNING
    if _begransad_precision(regelbas, falt_id):
        return visa_andel_begransad(falt, uppgift.varde, metodgranser(regelbas, falt_id, gransindex))
    return visa_varde_klartext(falt, uppgift.varde, metodgranser(regelbas, falt_id, gransindex))


def bygg_underlag(
    regelbas: Regelbas, profil: Profil, tjanstbedomning: Tjanstbedomning, avsnitt_id: str
, *, gransindex: dict[str, tuple[float, ...]] | None = None, formatversion: str = V6) -> Avsnittsunderlag:
    if gransindex is None:
        gransindex = metodgransindex(regelbas)
    from riskanalys.profil.omfattning import kompatibilitetsvy, aktivitetsprov
    profil = kompatibilitetsvy(profil, regelbas)
    aktiv = aktivitetsprov(profil, regelbas)
    lista = regelbas.tillatelselistor[AVSNITTSTYP]
    _kontrollera_lista(regelbas, lista.falt)
    tjanst = regelbas.tjanster[tjanstbedomning.tjanst]
    tillatna = tillatna_falt(regelbas, formatversion)
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
                motivering=_sarbarhetsmotivering(regelbas, profil, sarbarhet_id, tillatna, gransindex=gransindex),
            )
            for sarbarhet_id in tjanst.sarbarheter
        ),
        kontroller=tuple(
            UnderlagKontroll(id=kontroll.id, namn=regelbas.kontroller[kontroll.id].namn, status=kontrollstatus(kontroll))
            for kontroll in (*tjanstbedomning.kontroller,
                *((tjanstbedomning.sanktionsrisk.kontroll,) if tjanstbedomning.sanktionsrisk and tjanstbedomning.sanktionsrisk.kontroll else ()))
        ),
        uppgifter=tuple(_verksamhetsuppgift(regelbas, profil, falt_id, gransindex=gransindex)
            for falt_id in tillatna if aktiv(regelbas.falt[falt_id])
            and (formatversion not in (V7, V8) or _galler_tjansten(regelbas, profil, falt_id, tjanst.id))),
        regelspar=tjanstbedomning.regelspar + (tjanstbedomning.sanktionsrisk.regelspar if tjanstbedomning.sanktionsrisk else ()),
        undvik=tuple(UnderlagBrist(id=brist_id, namn=regelbas.bristmonster[brist_id].namn) for brist_id in lista.undvik),
    )


def tillatna_falt(regelbas: Regelbas, formatversion: str = V6) -> tuple[str, ...]:
    """Äldre skrivformat behåller sin vy när nya verksamhetsval tillåts för V7."""
    return tuple(id for id in regelbas.tillatelselistor[AVSNITTSTYP].falt
                 if formatversion in (V7, V8) or verksamhetsval(regelbas, id) is None)


def faltets_tjanst(regelbas: Regelbas, falt_id: str) -> str | None:
    for tjanst in regelbas.tjanster.values():
        prefix = tjanst.erbjuds_falt.removesuffix('_erbjuds')
        if falt_id.startswith(prefix + '_'):
            return tjanst.id
        if any(falt_id.startswith(f'P-KONTROLL.{id}.') for id in tjanst.kontroller if id.startswith('C-TJ-')):
            return tjanst.id
    return None


def _galler_tjansten(regelbas: Regelbas, profil: Profil, falt_id: str, tjanst_id: str) -> bool:
    omfang = faltets_tjanst(regelbas, falt_id)
    val = verksamhetsval(regelbas, falt_id)
    return (omfang is None or omfang == tjanst_id) and (val is None or erbjuds_aktuellt(profil, val[0]))


def _verksamhetsuppgift(regelbas: Regelbas, profil: Profil, falt_id: str, *, gransindex: dict | None):
    u = _uppgift(regelbas, profil, falt_id, gransindex=gransindex)
    val = verksamhetsval(regelbas, falt_id)
    if val:
        uppgift = profil.uppgifter.get(falt_id, Uppgift())
        visning = VERKSAMHETSVAL[val[1]].get(uppgift.varde, 'okänt') if u.bekraftad else 'okänt'
        return u.model_copy(update={'varde': visning, 'bekraftad': u.bekraftad and visning != 'okänt'})
    return u


def _sarbarhetsmotivering(regelbas: Regelbas, profil: Profil, id: str, tillatna: tuple[str, ...], *, gransindex: dict | None = None) -> str:
    from riskanalys.dokument.klartext import faltnamn, gemen, gransmening_text, under_grans
    from riskanalys.profil.omfattning import kompatibilitetsvy
    from riskanalys.regelverk.villkor import falt_i
    s = regelbas.sarbarheter[id]
    status = sarbarhet_status(regelbas, profil, id)
    falt = sorted(falt_i(tolka_villkor(s.villkor, regelbas.faltdefinitioner())))
    rader = []
    for ref in falt:
        if ref not in tillatna:
            rader.append(f"{faltnamn(regelbas, ref)}: underlaget finns i byråns lokala belägg; motiveringen behöver granskas lokalt.")
            continue
        u = _uppgift(regelbas, profil, ref, gransindex=gransindex)
        period = f" Period: {'–'.join(u.period)}." if u.period else ""
        rader.append(f"{faltnamn(regelbas, ref)} ({ref}): {u.varde}.{period}")
    for g in under_grans(kompatibilitetsvy(profil, regelbas), s.villkor):
        if g.falt_id not in tillatna:
            continue
        visning = _uppgift(regelbas, profil, g.falt_id, gransindex=gransindex).varde
        # Bara den skyddade vyn styr: ett maskat värde ger ingen mening alls, så att 0 och 3 kunder ser likadana ut.
        if visning in (SKYDDAD_VISNING, "okänt"):
            continue
        grans = visa_grans(regelbas.falt[g.falt_id], g.grans)
        rader.append(gransmening_text(gemen(faltnamn(regelbas, g.falt_id)), visning, grans))
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


def _uppgift(regelbas: Regelbas, profil: Profil, falt_id: str, *, gransindex: dict | None = None) -> UnderlagUppgift:
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
    varde = "okänt" if saknad_bas else visa_for_ai(regelbas, falt_id, uppgift, antal, gransindex=gransindex)
    if komplement and uppgift.status == "bekräftad" and not uppgift.inaktuell:
        varde = SKYDDAD_VISNING
    return UnderlagUppgift(
        id=falt_id, fraga=falt.fraga, varde=varde,
        period=(uppgift.period.fran.isoformat(), uppgift.period.till.isoformat()) if uppgift.period else None,
        bas=str(basuppgift.varde) if visa_bas else None,
        bekraftad=uppgift.status == "bekräftad" and not uppgift.inaktuell,
    )
