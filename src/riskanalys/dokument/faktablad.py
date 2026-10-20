"""Faktabladet: det enda AI får veta om en tjänst (spec 8.4.2). Byggs ur det tillåtelselistade underlaget."""

import json
from typing import Literal
from pydantic import Field, model_serializer
from riskanalys.dokument.skrivversion import V6, V7, V8

from riskanalys.dokument.modeller import Last, UnderlagHot, UnderlagKontroll, UnderlagKontrollrackvidd, UnderlagSarbarhet
from riskanalys.dokument.klartext import faltnamn
from riskanalys.regelverk.granser import metodgransindex
from riskanalys.dokument.underlag import (
    AVSNITTSTYP, LOKALT_UTFALL, SKYDDAD_VISNING, bygg_underlag, kontrollstatus_for_ai, provas_lokalt,
    faltets_tjanst, tillatna_falt)
from riskanalys.profil.modeller import Profil, Uppgift
from riskanalys.profil.omfattning import HARLEDNING
from riskanalys.regelverk.modeller import Falt, Regelbas, Sektorsreferens

Kalltyp = Literal["register", "intern_statistik", "egen_kannedom", "dokument", "harledning"]
_NUMERISKA = ("heltal", "tal", "andel")
_INTERVALLVISNINGAR = ("mindre än ", "mer än ", "strax under ", "strax över ", "minst ")


class Faktapost(Last):
    id: str
    etikett: str
    visningsvarde: str
    period: str | None
    kalltyp: Kalltyp | None
    status: Literal["bekräftad", "okänd", "skyddad"]
    tal: float | None = None
    intervall: bool = False
    omfang: Literal['byra', 'tjanst'] | None = None
    tjanst_id: str | None = None

    @model_serializer(mode='wrap')
    def serialisera(self, handler):
        data = handler(self)
        if self.omfang is None:
            data.pop('omfang', None)
            data.pop('tjanst_id', None)
        return data


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
                          *(s.id for s in self.sarbarheter), *(k.id for k in self.kontroller), *self.regelspar,
                          *(id for k in self.kontroller if k.rackviddsstatus is not None
                            for id in (*k.kallor, *(h.kalla for h in k.kallhanvisningar),
                                       *(r.id for r in k.rackvidd),
                                       *(h.kalla for r in k.rackvidd for h in r.kallhanvisningar)))})

    def uppgift_id(self) -> frozenset[str]:
        return frozenset(p.id for p in self.poster)

    def numeriska(self) -> dict[str, str]:
        """Värden som AI får hänvisa till med {tal:ID}, även intervall som 'mindre än 1 %'; skyddade och okända värden saknas."""
        return {p.id: p.visningsvarde for p in self.poster if p.tal is not None or p.intervall}

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
    skyddad = u.varde == SKYDDAD_VISNING
    # Ett intervall som 'mindre än 1 %' lagras som intervall och aldrig som ett exakt tal (spec 8.4.9 punkt 7).
    intervall = not skyddad and u.bekraftad and falt.typ in _NUMERISKA and u.varde.startswith(_INTERVALLVISNINGAR)
    tal = None
    if not skyddad and not intervall and u.bekraftad and falt.typ in _NUMERISKA:
        # Använd bara värdet som redan passerat underlagets maskning och kompatibilitetsvy.
        try:
            tal = float(u.varde.replace("%", "").replace(" ", "").replace("\u00a0", "").replace("\u202f", "").replace(",", "."))
        except ValueError:
            tal = None
    visning = (u.varde if falt.typ == "andel" else visa_tal(tal)) if tal is not None else u.varde
    return Faktapost(
        id=u.id, etikett=faltnamn(regelbas, u.id), visningsvarde=visning,
        period=f"{u.period[0]}–{u.period[1]}" if u.period else None,
        kalltyp=kalltyp(uppgift, falt),
        status="skyddad" if skyddad else "bekräftad" if u.bekraftad and u.varde != "okänt" else "okänd",
        tal=tal, intervall=intervall,
    )


def _post_med_omfang(regelbas: Regelbas, profil: Profil, u, formatversion: str) -> Faktapost:
    post = _post(regelbas, profil, u)
    if formatversion not in (V7, V8):
        return post
    tjanst_id = faltets_tjanst(regelbas, u.id)
    return post.model_copy(update={'omfang': 'tjanst' if tjanst_id else 'byra', 'tjanst_id': tjanst_id})


def bygg_faktablad(regelbas: Regelbas, profil: Profil, tjanstbedomning, avsnitt_id: str, *, gransindex: dict[str, tuple[float, ...]] | None = None, formatversion: str = V6) -> Faktablad:
    if gransindex is None:
        gransindex = metodgransindex(regelbas)
    underlag = bygg_underlag(regelbas, profil, tjanstbedomning, avsnitt_id, gransindex=gransindex, formatversion=formatversion)
    ref=regelbas.sektorsreferenser.get(regelbas.tjanster[tjanstbedomning.tjanst].sektorreferens)
    tillatna = tillatna_falt(regelbas, formatversion)
    sanktion = tjanstbedomning.sanktionsrisk
    bedomda = {k.id: k for k in (*tjanstbedomning.kontroller, *((sanktion.kontroll,) if sanktion and sanktion.kontroll else ()))}
    return Faktablad(
        # Motorns nivåer och regelspår skickas aldrig till AI (spec 8.4.10).
        nivaer={}, sektorsreferens=ref,
        avsnitt=avsnitt_id, tjanst_id=underlag.tjanst_id, tjanst_namn=underlag.tjanst_namn,
        poster=tuple(_post_med_omfang(regelbas, profil, u, formatversion) for u in underlag.uppgifter),
        sarbarhetsomraden={s.id:regelbas.sarbarheter[s.id].omrade for s in underlag.sarbarheter},
        tf_hot=tuple(h.id for h in underlag.hot if regelbas.hot[h.id].galler_tf),
        hot=underlag.hot, regelspar=(),
        # Status byggs av kategorifälten; om kontrollen räknas som riskreducerande avgörs lokalt (spec 8.4.10 punkt 4).
        kontroller=tuple(_kontroll_for_ai(regelbas, k, bedomda[k.id], underlag.tjanst_id, formatversion)
                         for k in underlag.kontroller),
        # Utfallet visas bara när AI ser exakt de uppgifter villkoret läser (spec 8.4.10).
        sarbarheter=tuple(
            s.model_copy(update={"galler": "prövas lokalt", "motivering": LOKALT_UTFALL})
            if provas_lokalt(regelbas, profil, s.id, tillatna, gransindex=gransindex) else s
            for s in underlag.sarbarheter),
    )


def faktablad_json(fb: Faktablad) -> str:
    """Sorterade nycklar och fast ordning, så att cachen kan träffa (spec 8.4.2)."""
    return json.dumps(fb.model_dump(mode="json"), sort_keys=True, ensure_ascii=False, indent=1)


def _kontroll_for_ai(regelbas, kontroll, bedomning, tjanst_id: str, formatversion: str) -> UnderlagKontroll:
    """Publik källpolicy för V7: endast katalogens källbundna saktext och uttryckliga tjänstkoppling.

    Inga profilfält, lokala kontrollutfall, sakkunnigattester eller härledd scenariotäckning kopieras.
    Saknat källstöd lämnar beskrivningen tom; AI ska då inte fylla luckan.
    """
    publik = {"status": kontrollstatus_for_ai(bedomning)}
    k = regelbas.kontroller[kontroll.id]
    if formatversion in (V7, V8):
        publik["rackviddsstatus"] = "okand"
    if formatversion in (V7, V8) and k.kallor and all(id in regelbas.kallor for id in k.kallor):
        publik.update(beskrivning=k.beskrivning, kallor=k.kallor,
            kallhanvisningar=tuple(h for h in k.kallhanvisningar if h.kalla in regelbas.kallor),
            rackvidd=tuple(UnderlagKontrollrackvidd.model_validate(r.model_dump(exclude={'sakkunnig'}))
                for r in k.rackvidd if r.tjanst == tjanst_id
                and all(h.kalla in regelbas.kallor for h in r.kallhanvisningar)))
    if publik.get("rackvidd"):
        publik["rackviddsstatus"] = "kallbundet_underlag"
    return kontroll.model_copy(update=publik)
