"""Anropsflöde per tjänst: ett anrop per analysdel från skyddat faktablad, med omförsök och mallreserv (spec 8.4.3, 8.4.5)."""

from riskanalys.regelverk.granser import metodgransindex

from collections.abc import Callable
from typing import Literal
from datetime import datetime, timezone

from pydantic import ValidationError, model_validator

from riskanalys.dokument.aischema import ai_schema, tolka_delsvar
from riskanalys.dokument.analysunderlag import erfarenhetsstycke, sarbarhetsstycke
from riskanalys.dokument.delvalidering import innehaller_personnamn, validera_del
from riskanalys.dokument.faktablad import Faktablad, bygg_faktablad
from riskanalys.dokument.lasta_v6 import lasta_stycken_v6
from riskanalys.dokument.leverantor import Anropsdata, Delanrop, LeverantorFel, Leveranssvar
from riskanalys.dokument.modeller import AISvar, Last
from riskanalys.dokument.nivatext import nivastycken, sektorsstycken
from riskanalys.dokument.platshallare import ersatt_tal
from riskanalys.dokument.promptar import DELAR, bygg_innehall, promptsumma, systemprompt
from riskanalys.dokument.tjanstavsnitt import kontrollstycken
from riskanalys.lagring.kontrollsumma import for_text

from riskanalys.dokument.skrivversion import AKTUELL_SKRIVVERSION, V5, V6, V7, delar_for_version

FORMATVERSION = AKTUELL_SKRIVVERSION
MAX_OMFORSOK = 2
MAX_TOKENS = 64000
EFFORTSTEG = {"low": "medium", "medium": "high", "high": "xhigh", "xhigh": "max", "max": "max"}
ANSVARSMENING = ("Byrån beslutar ansvariga, tidsfrister, faktisk kundkännedom och uppföljningstakt. "
                 "Texten är ett analysunderlag och intygar inte genomförda åtgärder.")


class Delforsok(Last):
    nummer: int
    effort: str
    anrop: Anropsdata
    text: str
    svar: AISvar | None
    fel: tuple[str, ...]


class Delresultat(Last):
    del_id: str
    forsok: tuple[Delforsok, ...]
    mall: bool
    lokal_sparr: Literal["personnamn"] | None = None

    @property
    def godkant_svar(self) -> AISvar | None:
        if self.mall or not self.forsok or self.forsok[-1].fel:
            return None
        return self.forsok[-1].svar

    def kontrollsumma(self) -> str:
        svar = self.godkant_svar
        return for_text(svar.model_dump_json() if svar else "mall")


class Tjanstresultat(Last):
    avsnitt: str
    tjanst: str
    design: Literal["A", "B"]
    formatversion: Literal["D-ARB-tjanst-v3", "D-ARB-tjanst-v4", "D-ARB-tjanst-v5", "D-ARB-tjanst-v6", "D-ARB-tjanst-v7"] = FORMATVERSION
    faktablad: Faktablad
    delar: tuple[Delresultat, ...]

    @model_validator(mode="after")
    def giltiga_delar(self):
        if self.formatversion in (V5, V6, V7) and tuple(d.del_id for d in self.delar) != delar_for_version(self.formatversion):
            raise ValueError("Skrivresultatets delar följer inte formatets ordning.")
        return self

    def del_(self, del_id: str) -> Delresultat:
        return next(d for d in self.delar if d.del_id == del_id)


def lasta_texter(regelbas, profil, t, del_id: str, *, gransindex: dict[str, tuple[float, ...]] | None = None,
                 formatversion: str = V5) -> tuple[str, ...]:
    """Kodens låsta stycken i delen. De används endast lokalt för validering (spec 8.4.1).

    I v6 är det exakt de stycken som v6-bygget infogar i delen; historiska format behåller sina stycken."""
    if gransindex is None:
        gransindex = metodgransindex(regelbas)
    if formatversion == V7:
        return tuple(s.text for del_ in ("hot", "sarbarheter")
                     for s in lasta_stycken_v6(regelbas, profil, t, del_, gransindex=gransindex))
    if formatversion == V6:
        return tuple(s.text for s in lasta_stycken_v6(regelbas, profil, t, del_id, gransindex=gransindex))
    if del_id == "hot":
        return (erfarenhetsstycke(regelbas, profil, t, gransindex=gransindex).text,)
    if del_id == "sarbarheter":
        tj = regelbas.tjanster[t.tjanst]
        return tuple(sarbarhetsstycke(regelbas, profil, t.tjanst, id, gransindex=gransindex).text
                     for id in tj.sarbarheter if regelbas.sarbarheter[id].omrade == "geo")
    if del_id == "kontroller":
        return tuple(s.text for s in kontrollstycken(regelbas, profil, t, gransindex=gransindex))
    if del_id == "risknivaer":
        return tuple(s.text for s in (*nivastycken(t),*sektorsstycken(regelbas,t)))
    return (ANSVARSMENING,)



def skyddade_lasta_texter(fb: Faktablad, t, del_id: str) -> tuple[str, ...]:
    """AI ser säkra instruktioner, aldrig lokala belägg, namn eller omaskerade antal."""
    if del_id == "analys":
        return ("Programmet återger lokalt egen rapportering, geografins belägg, sårbarhetsutfall och tjänstefördelning. "
                "Bygg bara på faktabladets synliga uppgifter; noll rapporter bevisar inte frånvaro av hot.",)
    if del_id == "hot":
        return ("Programmet återger byråns egen rapportering och erfarenhet. Antalen gäller hela byrån; noll rapporter bevisar inte frånvaro av hot.",)
    if del_id == "sarbarheter":
        return ("Programmet återger geografins lokala underlag. Fritexten finns i byråns lokala belägg; hänvisa bara till faktabladets strukturerade uppgifter.",)
    if del_id == "kontroller":
        return tuple(f"Programmet återger {k.namn}: {k.status}." for k in fb.kontroller)
    if del_id == "risknivaer":
        return ("Programmet skriver nivåmeningarna och sektorsreferensen lokalt. Du ser inte motorns nivåer och anger inga nivåer.",)
    return (ANSVARSMENING,)

def _tolka(text: str, fb: Faktablad) -> tuple[AISvar | None, tuple[str, ...]]:
    try:
        return tolka_delsvar(text,fb.tillatna_id(),fb.uppgift_id()), ()
    except ValidationError as fel:
        return None, (f"Svaret följde inte schemat ({fel.error_count()} fel). Svara bara med JSON enligt schemat.",)


def skriv_del(leverantor, fb: Faktablad, t, del_id: str, validerat: tuple[str, ...], *,
              effort: str, spara: Callable[[str, Delforsok], None], formatversion: str = FORMATVERSION) -> Delresultat:
    # Valideringen får bara jämföra mot det AI faktiskt har sett. De riktiga låsta texterna och personnamnen
    # prövas bara lokalt (spec 8.4.10 punkt 1, 2 och 7).
    lasta = skyddade_lasta_texter(fb, t, del_id)
    schema = ai_schema(fb.tillatna_id(), fb.uppgift_id(), formatversion=formatversion)
    forsok: tuple[Delforsok, ...] = ()
    aterkoppling: tuple[str, ...] = ()
    for nummer in range(1, MAX_OMFORSOK + 2):
        klippt = any(f.anrop.stop_reason == "max_tokens" for f in forsok)
        niva = effort if nummer <= MAX_OMFORSOK or klippt else EFFORTSTEG[effort]
        anrop = Delanrop(del_id=del_id, system=systemprompt(leverantor.modell, formatversion=formatversion),
                         innehall=bygg_innehall(fb, del_id, lasta, validerat, aterkoppling, formatversion=formatversion), schema=schema,
                         effort=niva, max_tokens=MAX_TOKENS, promptsumma=promptsumma(leverantor.modell, del_id, formatversion=formatversion))
        try:
            leverans = leverantor.skriv_del(anrop)
        except LeverantorFel as fel:
            if not fel.tillfalligt:
                raise
            # Felet och försöket sparas utan att serverns fria feltext förs vidare till nästa AI-anrop.
            leverans = Leveranssvar(anrop=Anropsdata(
                leverantor=leverantor.namn, begard_modell=leverantor.modell,
                svarsmodell="inget_svar", effort=niva, prompt_kontrollsumma=anrop.promptsumma,
                svar_id=None, stop_reason="leverantorsfel", reservmodell_svarade=False,
                anvandning=(), tidpunkt=datetime.now(timezone.utc), del_id=del_id),
                text="", avbrott="Leverantören kunde inte leverera något svar; försök igen eller använd mall.")
        svar, fel = (None, (leverans.avbrott,)) if leverans.avbrott else _tolka(leverans.text,fb)
        if svar is not None:
            fel = tuple(validera_del(del_id, svar, fb, (), lasta))
        post = Delforsok(nummer=nummer, effort=niva, anrop=leverans.anrop, text=leverans.text, svar=svar, fel=fel)
        spara(del_id, post)
        forsok = (*forsok, post)
        if not fel:
            return Delresultat(del_id=del_id, forsok=forsok, mall=False)
        aterkoppling = fel
    return Delresultat(del_id=del_id, forsok=forsok, mall=True)


def _utan_personnamn(d: Delresultat, personnamn: tuple[str, ...]) -> Delresultat:
    """Namnen prövas först när tjänstens alla AI-anrop är gjorda, så att varken återkoppling eller antal anrop
    beror på dem (spec 8.4.10 punkt 7). En del med namn ersätts av mallen."""
    svar = d.godkant_svar
    if svar is None or not innehaller_personnamn(svar, personnamn):
        return d
    return d.model_copy(update={"mall": True, "lokal_sparr": "personnamn"})


def aterger_last(svar: AISvar, fb: Faktablad, lasta: tuple[str, ...]) -> bool:
    """Ett AI-stycke innehåller ett låst stycke, som råtext eller sedan platshållarna ersatts som i dokumentet."""
    texter = tuple(text for s in svar.stycken for text in (s.text, ersatt_tal(s.text, fb.numeriska(), fb.perioder())))
    return any(last and last in text for last in lasta for text in texter)


def _utan_lasta_v6(d: Delresultat, fb: Faktablad, lasta: tuple[str, ...]) -> Delresultat:
    """V6:s låsta stycken bygger på uppgifter som AI inte ser, till exempel källa, bekräftare och smågruppsskyddade
    antal. De prövas därför som namnen, först efter tjänstens alla AI-anrop, så att varken återkoppling eller antal
    anrop beror på dem (spec 8.4.10 punkt 1). En del som återger ett låst stycke ersätts av mallen (spec 8.4.1)."""
    svar = d.godkant_svar
    if svar is None or not aterger_last(svar, fb, lasta):
        return d
    return d.model_copy(update={"mall": True})


def skriv_tjanst(leverantor, regelbas, profil, t, avsnitt_id: str, *, design: Literal["A", "B"] = "B", effort: str,
                 personnamn: tuple[str, ...], spara: Callable[[str, Delforsok], None],
                 formatversion: str = FORMATVERSION) -> Tjanstresultat:
    if design != "B":
        raise LeverantorFel("Design A är inte byggd ännu; använd design B.")
    fb = bygg_faktablad(regelbas, profil, t, avsnitt_id, formatversion=formatversion)
    delar: dict[str, Delresultat] = {}

    def validerad(*ids: str) -> tuple[str, ...]:
        return tuple(s.text for id in ids if (svar := delar[id].godkant_svar) for s in svar.stycken)

    # Godkänd AI-text får följa kedjan; lokal namnkontroll påverkar aldrig nästa anrop (spec 8.4.10.9).
    for del_id in delar_for_version(formatversion):
        underlag = (validerad("hot", "sarbarheter", "kontroller") if del_id == "risknivaer"
                    else validerad("risknivaer") if del_id == "slutsatser" else ())
        delar[del_id] = skriv_del(leverantor, fb, t, del_id, underlag, effort=effort, spara=spara, formatversion=formatversion)
    provade = tuple(_utan_personnamn(d, personnamn) for d in delar.values())
    if formatversion in (V6, V7):
        index = metodgransindex(regelbas)
        provade = tuple(_utan_lasta_v6(d, fb, lasta_texter(regelbas, profil, t, d.del_id, gransindex=index, formatversion=formatversion))
                        for d in provade)
    return Tjanstresultat(avsnitt=avsnitt_id, tjanst=t.tjanst, design=design, formatversion=formatversion, faktablad=fb,
                         delar=provade)


def kontrollera_resultat(rb, p, t, resultat: Tjanstresultat, avsnitt_id: str, *, gransindex: dict[str, tuple[float, ...]] | None = None, formatversion: str = FORMATVERSION) -> None:
    """Kontrollera fryst indata och varje godkänt råsvar på nytt före dokumentbygget."""
    if gransindex is None:
        gransindex = metodgransindex(rb)
    from riskanalys.fel import RiskanalysFel
    from riskanalys.profil.hantering import personnamn
    if (resultat.avsnitt != avsnitt_id or resultat.tjanst != t.tjanst or resultat.design != "B"
            or tuple(d.del_id for d in resultat.delar) != delar_for_version(formatversion)
            or resultat.formatversion != formatversion):
        raise RiskanalysFel("Tjänstresultatets identitet eller analysdelar är ogiltiga. Skriv om utkastet.")
    if resultat.faktablad != bygg_faktablad(rb, p, t, avsnitt_id, gransindex=gransindex, formatversion=formatversion):
        raise RiskanalysFel("Skrivningens faktablad avviker från aktuellt underlag. Skriv och sakgranska på nytt.")
    for d in resultat.delar:
        if d.mall:
            continue
        if not d.godkant_svar:
            raise RiskanalysFel("En analysdel saknar validerat svar. Skriv om delen.")
        anrop = d.forsok[-1].anrop
        if anrop.prompt_kontrollsumma != promptsumma(anrop.begard_modell, d.del_id, formatversion=formatversion):
            raise RiskanalysFel("Analysdelens prompt är inte aktuell. Skriv om delen och sakgranska på nytt.")
        svar, fel = _tolka(d.forsok[-1].text,resultat.faktablad)
        if svar != d.godkant_svar or fel:
            raise RiskanalysFel("Analysdelens råsvar avviker från det sparade svaret. Skriv om delen.")
        lasta = lasta_texter(rb, p, t, d.del_id, gransindex=gransindex, formatversion=formatversion)
        fel = validera_del(d.del_id, svar, resultat.faktablad, personnamn(p, rb), lasta)
        if fel:
            raise RiskanalysFel("Analysdelen klarar inte valideringen. Skriv om delen: " + "; ".join(fel))
        if formatversion in (V6, V7) and aterger_last(svar, resultat.faktablad, lasta):
            raise RiskanalysFel("Analysdelen återger programmets låsta stycke. Skriv om delen och sakgranska på nytt.")
