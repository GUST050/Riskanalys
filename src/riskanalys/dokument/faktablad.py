"""Faktabladet: det enda AI får veta om en tjänst (spec 8.4.2). Byggs ur det tillåtelselistade underlaget."""

import json
from typing import Literal
from pydantic import Field

from riskanalys.dokument.modeller import Last, UnderlagHot, UnderlagKontroll, UnderlagSarbarhet
from riskanalys.dokument.klartext import faltnamn
from riskanalys.dokument.underlag import SKYDDADE_VISNINGAR, bygg_underlag
from riskanalys.profil.modeller import Profil, Uppgift
from riskanalys.profil.omfattning import HARLEDNING
from riskanalys.regelverk.modeller import Falt, Regelbas, Sektorsreferens

Kalltyp = Literal["register", "intern_statistik", "egen_kannedom", "dokument", "harledning"]
_NUMERISKA = ("heltal", "tal", "andel")


class Faktapost(Last):
    id: str
    etikett: str
    visningsvarde: str
    period: str | None
    kalltyp: Kalltyp | None
    status: Literal["bekräftad", "okänd", "skyddad"]
    tal: float | None = None


class Faktablad(Last):
    avsnitt: str
    tjanst_id: str
    tjanst_namn: str
    poster: tuple[Faktapost, ...]
    hot: tuple[UnderlagHot, ...]
    sarbarheter: tuple[UnderlagSarbarhet, ...]
    kontroller: tuple[UnderlagKontroll, ...]
    regelspar: tuple[str, ...]
    sarbarhetsomraden: dict[str,str] = Field(default_factory=dict)
    tf_hot: tuple[str,...] = ()
    nivaer: dict[str,str] = Field(default_factory=dict)
    sektorsreferens: Sektorsreferens | None = None

    def tillatna_id(self) -> frozenset[str]:
        return frozenset({self.tjanst_id, *(p.id for p in self.poster), *(h.id for h in self.hot),
                          *(s.id for s in self.sarbarheter), *(k.id for k in self.kontroller), *self.regelspar})

    def uppgift_id(self) -> frozenset[str]:
        return frozenset(p.id for p in self.poster)

    def numeriska(self) -> dict[str, str]:
        """Värden som AI får hänvisa till med {tal:ID}; skyddade och okända värden saknas."""
        return {p.id: p.visningsvarde for p in self.poster if p.tal is not None}

    def perioder(self) -> dict[str, str]:
        """Perioder från tillåtna faktaposter, aldrig datum som AI hittar på."""
        return {p.id: p.period for p in self.poster if p.period}


def visa_tal(varde: float) -> str:
    heltal = round(varde)
    if abs(varde - heltal) < 1e-9:
        return f"{heltal:,}".replace(",", " ")
    return f"{varde:.1f}".replace(".", ",")


def kalltyp(uppgift: Uppgift, falt: Falt) -> Kalltyp | None:
    """Sluten källtyp som koden härleder. Profilens fria källtext lämnar aldrig datorn."""
    from riskanalys.intag.underlag import EGEN_KANNEDOM
    kalla = uppgift.kalla or ""
    if not kalla:
        return None
    if kalla == EGEN_KANNEDOM:
        return "egen_kannedom"
    if kalla.startswith(HARLEDNING):
        return "harledning"
    if kalla.startswith(("SCB AFR API", "Lokalt importerat SCB")):
        return "register"
    if falt.periodkrav or falt.typ in _NUMERISKA:
        return "intern_statistik"
    return "dokument"


def _post(regelbas: Regelbas, profil: Profil, u) -> Faktapost:
    falt = regelbas.falt[u.id]
    uppgift = profil.uppgifter.get(u.id, Uppgift())
    skyddad = u.varde.startswith(SKYDDADE_VISNINGAR)
    tal = None
    if not skyddad and u.bekraftad and falt.typ in _NUMERISKA:
        # Använd bara värdet som redan passerat underlagets maskning och kompatibilitetsvy.
        try:
            tal = float(u.varde.replace("%", "").replace(" ", "").replace("\u00a0", "").replace("\u202f", "").replace(",", "."))
        except ValueError:
            tal = None
    visning = (visa_tal(tal) + (" %" if falt.typ == "andel" else "")) if tal is not None else u.varde
    return Faktapost(
        id=u.id, etikett=faltnamn(regelbas, u.id), visningsvarde=visning,
        period=f"{u.period[0]}–{u.period[1]}" if u.period else None,
        kalltyp=kalltyp(uppgift, falt),
        status="skyddad" if skyddad else "bekräftad" if u.bekraftad and u.varde != "okänt" else "okänd",
        tal=tal,
    )


def bygg_faktablad(regelbas: Regelbas, profil: Profil, tjanstbedomning, avsnitt_id: str) -> Faktablad:
    underlag = bygg_underlag(regelbas, profil, tjanstbedomning, avsnitt_id)
    ref=regelbas.sektorsreferenser.get(regelbas.tjanster[tjanstbedomning.tjanst].sektorreferens)
    return Faktablad(
        nivaer=underlag.nivaer, sektorsreferens=ref,
        avsnitt=avsnitt_id, tjanst_id=underlag.tjanst_id, tjanst_namn=underlag.tjanst_namn,
        poster=tuple(_post(regelbas, profil, u) for u in underlag.uppgifter),
        sarbarhetsomraden={s.id:regelbas.sarbarheter[s.id].omrade for s in underlag.sarbarheter},
        tf_hot=tuple(h.id for h in underlag.hot if regelbas.hot[h.id].galler_tf),
        hot=underlag.hot, sarbarheter=underlag.sarbarheter, kontroller=underlag.kontroller, regelspar=underlag.regelspar,
    )


def faktablad_json(fb: Faktablad) -> str:
    """Sorterade nycklar och fast ordning, så att cachen kan träffa (spec 8.4.2)."""
    return json.dumps(fb.model_dump(mode="json"), sort_keys=True, ensure_ascii=False, indent=1)
