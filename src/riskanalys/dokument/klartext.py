"""Svensk klartext för låsta stycken: fältnamn, uppgifter och villkor utan fält-ID (spec 8.4.9)."""

from riskanalys.regelverk.granser import metodgransindex

import re
from dataclasses import dataclass

from riskanalys.bedomning.erfarenheter import belagd_uppgift
from riskanalys.dokument.platshallare import _FALTID
from riskanalys.profil.hantering import visa_varde, visa_varde_klartext, visa_grans
from riskanalys.profil.modeller import Profil
from riskanalys.profil.omfattning import HARLEDNING
from riskanalys.regelverk.granser import metodgranser
from riskanalys.regelverk.modeller import Regelbas, Regelpaket

VERIFIERA = "[VERIFIERA]"

_TJANSTFALT = {
    "_erbjuds": "{namn} erbjuds",
    "_antal_kunder": "Antal kunder i {liten}",
    "_andel_kunder": "Andel av byråns kunder i {liten}",
    "_omsattning": "Omsättning från {liten}",
    "_andel_omsattning": "Andel av omsättningen från {liten}",
    "_arbetssatt": "Uppdrag och arbetssätt i {liten}",
    "_geografi": "Geografi i {liten}",
    "_ovriga_risker": "Övriga riskförhållanden i {liten}",
}
_KONTROLLFALT = {
    "effekt": "Dokumenterad verkan av",
    "utfall": "Prov och utfall för",
}
_KONTROLLSUMMA = re.compile(r"sha256:\S*[^\s.,;:!?)\]}”»’'\"]")  # skiljetecken efter summan står kvar
_JAMFORELSE = {">=": "är minst", ">": "är större än", "<": "är mindre än", "<=": "är högst", "==": "är", "!=": "inte är"}


@dataclass(frozen=True)
class UnderGrans:
    """En jämförelse mot en gräns som inte är uppfylld fast faktorn förekommer."""

    falt_id: str
    grans: float


def gemen(text: str) -> str:
    """Liten begynnelsebokstav mitt i en mening, men inte i förkortningar som PEP och EU."""
    if len(text) > 1 and text[1].isupper():
        return text
    return text[:1].lower() + text[1:]


def _monsternamn(regelbas: Regelbas, falt_id: str) -> str | None:
    for tjanst in regelbas.tjanster.values():
        slug = tjanst.erbjuds_falt.removesuffix("_erbjuds")
        mall = _TJANSTFALT.get(falt_id[len(slug):]) if falt_id.startswith(slug + "_") else None
        if mall:
            return mall.format(namn=tjanst.namn, liten=gemen(tjanst.namn))
    delar = falt_id.split(".")
    if len(delar) == 3 and delar[0] == "P-KONTROLL" and delar[1] in regelbas.kontroller and delar[2] in _KONTROLLFALT:
        return f"{_KONTROLLFALT[delar[2]]} {_kontrollbeteckning(regelbas.kontroller[delar[1]].namn)}"
    return None


def _kontrollbeteckning(namn: str) -> str:
    """'kontroll av bokföring' när namnet redan börjar med Kontroll, annars 'kontrollen bankavstämning'."""
    liten = gemen(namn)
    return liten if liten.startswith("kontroll") else f"kontrollen {liten}"


def har_eget_namn(regelbas: Regelbas, falt_id: str) -> bool:
    return bool(regelbas.falt[falt_id].etikett or _monsternamn(regelbas, falt_id))


def faltnamn(regelbas: Regelbas, falt_id: str) -> str:
    """Kortnamnet, annars ett namn efter tjänst eller kontroll, annars frågan utan frågetecken."""
    falt = regelbas.falt[falt_id]
    return falt.etikett or _monsternamn(regelbas, falt_id) or falt.fraga.removesuffix(" (beräknad andel)").rstrip("?")


def _kalltext(kalla: str) -> str:
    """Härledda andelar har fält-ID som källa ('Härledning: A/B'); i löptext står en neutral klartext."""
    return "härledd ur bekräftade uppgifter" if kalla.startswith(HARLEDNING) else kalla


def uppgiftstext(regelbas: Regelbas, profil: Profil, falt_id: str, *, namn: str | None = None,
                 med_id: bool = False, gransindex: dict[str, tuple[float, ...]] | None = None) -> str:
    """'Kortnamn: värde (period …; källa: …; bekräftad …).' Fält-ID och källan som den är lagrad visas bara i bilagan (med_id)."""
    if gransindex is None:
        gransindex = metodgransindex(regelbas)
    rubrik = namn or faltnamn(regelbas, falt_id)
    if med_id:
        rubrik = f"{rubrik} ({falt_id})"
    if not belagd_uppgift(regelbas, profil, falt_id):
        return f"{rubrik}: aktuellt bekräftat underlag saknas. {VERIFIERA}"
    u = profil.uppgifter[falt_id]
    delar = [f"period {u.period.fran}–{u.period.till}"] if u.period else []
    delar += [f"källa: {u.kalla if med_id else _kalltext(u.kalla)}", f"bekräftad {u.datum}"]
    varde = str(visa_varde_klartext(regelbas.falt[falt_id], u.varde, metodgranser(regelbas, falt_id, gransindex))).rstrip(".")
    return f"{rubrik}: {varde} ({'; '.join(delar)})."


def _jamforelsetext(data: dict, regelbas: Regelbas) -> str:
    falt = regelbas.falt[data["falt"]]
    namn = gemen(faltnamn(regelbas, falt.id))
    op = data["op"]
    if op == "finns":
        return f"{namn} är angiven"
    if op == "saknas":
        return f"{namn} saknas"
    if falt.typ == "bool" and op in ("==", "!="):
        ja = (data["varde"] in (True, "ja")) == (op == "==")
        return f"uppgiften ”{faltnamn(regelbas, falt.id)}” är {'ja' if ja else 'nej'}"
    if op == "i":
        return f"{namn} är något av {', '.join(str(visa_varde(falt, v)) for v in data['varde'])}"
    return f"{namn} {_JAMFORELSE[op]} {visa_grans(falt, data['varde'])}"


def villkorstext(data: dict, regelbas: Regelbas) -> str:
    """Villkoret i ord, till exempel 'andel kunder i riskbranscher är minst 20 %'."""
    if "falt" in data:
        return _jamforelsetext(data, regelbas)
    if "inte" in data:
        return f"det inte gäller att {villkorstext(data['inte'], regelbas)}"
    nyckel, bindeord = ("alla", " och ") if "alla" in data else ("nagon", " eller ")
    return bindeord.join(villkorstext(d, regelbas) if "falt" in d else f"({villkorstext(d, regelbas)})"
                         for d in data[nyckel])


def under_grans(profil: Profil, data: dict) -> tuple[UnderGrans, ...]:
    """Jämförelser 'minst' eller 'större än' där ett bekräftat värde över noll inte når gränsen."""
    if "falt" in data:
        u = profil.uppgifter.get(data["falt"])
        if (data["op"] not in (">=", ">") or u is None or u.status != "bekräftad" or u.inaktuell
                or type(u.varde) not in (int, float)):
            return ()
        uppfyllt = u.varde >= data["varde"] if data["op"] == ">=" else u.varde > data["varde"]
        return (UnderGrans(data["falt"], data["varde"]),) if 0 < u.varde and not uppfyllt else ()
    if "inte" in data:
        return ()
    return tuple(dict.fromkeys(g for d in data.get("alla", data.get("nagon", [])) for g in under_grans(profil, d)))


def gransmening_text(namn: str, visning: str, grans: str) -> str:
    """Den enda mallen för gränsmeningen. Visningen kommer färdig från visa_varde_klartext."""
    return (f"Faktorn förekommer: {namn} är {visning}, men det ligger under metodens gräns på {grans} "
            "för automatiskt riskpåslag.")


def gransmening(regelbas: Regelbas, profil: Profil, g: UnderGrans, *, gransindex: dict[str, tuple[float, ...]] | None = None) -> str:
    if gransindex is None:
        gransindex = metodgransindex(regelbas)
    falt = regelbas.falt[g.falt_id]
    return gransmening_text(gemen(faltnamn(regelbas, g.falt_id)),
                            visa_varde_klartext(falt, profil.uppgifter[g.falt_id].varde, metodgranser(regelbas, g.falt_id, gransindex)),
                            visa_grans(falt, g.grans))


def _idnamn(regelbas: Regelbas, id_: str) -> str | None:
    """Namnet på ett ID som regelbasen känner igen (fält, tillämplighetsprövning, tjänst, sårbarhet, hot, kontroll)."""
    if id_ in regelbas.falt:
        return faltnamn(regelbas, id_)
    if id_ in regelbas.tillamplighet:
        return f"punkt {regelbas.tillamplighet[id_].punkt}"
    katalog = next((k for k in (regelbas.tjanster, regelbas.sarbarheter, regelbas.hot, regelbas.kontroller)
                    if id_ in k), None)
    return katalog[id_].namn if katalog else None


def kanda_id(regelbas: Regelbas, text: str) -> tuple[str, ...]:
    """De ID i en text som id_till_namn byter mot namn, unika och i den ordning de förekommer."""
    return tuple(dict.fromkeys(id_ for id_ in _FALTID.findall(text) if _idnamn(regelbas, id_)))


def id_till_namn(regelbas: Regelbas, text: str) -> str:
    """Byter kända ID i en text mot namn. Okända ID står kvar.

    Ett namn mitt i en mening skrivs med liten begynnelsebokstav; först i texten och efter '. ' behålls stor.
    """
    def namn(traff: re.Match[str]) -> str:
        id_ = traff.group(0)
        klartext = _idnamn(regelbas, id_)
        if klartext is None:
            return id_
        if traff.start() == 0 or text.endswith(". ", 0, traff.start()):
            return klartext[:1].upper() + klartext[1:]
        return gemen(klartext)

    return _FALTID.sub(namn, text)


def paketnamn(paket: Regelpaket) -> str:
    """Regelpaketets namn utan avslutande kod."""
    return paket.namn.removesuffix(f": {paket.id}")


def _paketnamn_med_lan(paket: Regelpaket) -> str:
    """Alla regelpaket i en regelbas kan heta lika; länen skiljer dem åt."""
    return f"{paketnamn(paket)} ({', '.join(paket.lan)})" if paket.lan else paketnamn(paket)


def _katalogkoder(regelbas: Regelbas) -> re.Pattern[str] | None:
    """De regelpaket- och käll-ID som regelbasen registrerar, som hela ord (längst först)."""
    koder = sorted({*regelbas.regelpaket, *regelbas.kallor}, key=lambda kod: (-len(kod), kod))
    if not koder:
        return None
    return re.compile(r"(?<![\w-])(?:" + "|".join(map(re.escape, koder)) + r")(?![\w-])")


def kod_till_namn(regelbas: Regelbas, text: str) -> str:
    """Ersätt registrerade regelpaket- och käll-ID med namn och titlar och kontrollsummor med en hänvisning
    till bilagan; okända koder lämnas (spec 8.4.9 punkt 8)."""
    def namn(traff: re.Match[str]) -> str:
        kod = traff.group(0)
        if kod in regelbas.regelpaket:
            return _paketnamn_med_lan(regelbas.regelpaket[kod])
        return regelbas.kallor[kod].titel

    text = _KONTROLLSUMMA.sub("(kontrollsumma i bilaga B1)", text)
    koder = _katalogkoder(regelbas)
    return koder.sub(namn, text) if koder else text


def punkttext(punkter: tuple[int, ...]) -> str:
    """Rättsliga punkter i ord: 'punkt 19', 'punkterna 19 och 20', 'punkterna 19, 20 och 21'."""
    if not punkter:
        return "ingen punkt är bekräftad"
    if len(punkter) == 1:
        return f"punkt {punkter[0]}"
    return f"punkterna {', '.join(map(str, punkter[:-1]))} och {punkter[-1]}"
