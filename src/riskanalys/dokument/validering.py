"""Maskinell validering av AI-utkast (spec 8.4). Ett utkast som inte klarar valideringen används aldrig."""

import re

from riskanalys.dokument.modeller import Avsnittsunderlag, AvsnittsUtkast, Textstycke
from riskanalys.dokument.rendering import ROLLER, VERIFIERA_PREFIX, roller_i

VERIFIERA = "[VERIFIERA]"
FORBJUDNA_FORMULERINGAR = (
    "enligt gällande lagstiftning",
    "i enlighet med branschpraxis",
    "som alla redovisningsbyråer",
    "det finns inga risker",
    "risken är generellt låg",
)
BENAMNINGAR = {
    "sanktioner_risk": "sanktionsrisken",
    "kvarstaende_sanktioner_risk": "den kvarstående sanktionsrisken",
    "sanktioner_sannolikhet": "sannolikheten för sanktioner",
    "sanktioner_konsekvens": "konsekvensen för sanktioner",
    "inneboende_sannolikhet": "sannolikheten",
    "inneboende_konsekvens": "konsekvensen",
    "inneboende_risk": "den inneboende risken",
    "terrorfinansiering_sannolikhet": "sannolikheten för terrorfinansiering",
    "terrorfinansiering_konsekvens": "konsekvensen för terrorfinansiering",
    "terrorfinansiering_risk": "risken för terrorfinansiering",
    "kvarstaende_risk": "den kvarstående risken",
    "kvarstaende_terrorfinansiering_risk": "den kvarstående risken för terrorfinansiering",
}
_TAL = re.compile(r"\d{1,3}(?:[ \u00a0\u202f]\d{3})+(?:,\d+)?|\d+(?:[.,]\d+)?")
_TUSENTAL = str.maketrans("", "", " \u00a0\u202f")
_VERB = r"\s+(?:är|blir|bedöms(?:\s+\w+)?\s+(?:som|vara))\s+"
_AMNE = r"(?:\s+för\s+(?P<amne>finansiering\s+av\s+terrorism|terrorfinansiering|penningtvätt|internationella\s+sanktioner|sanktioner))?"
_FYLLNAD = r"(?:\s+\w+){0,3}?"
_TF = r"(?P<tf>terrorfinansierings)?(?P<sf>sanktions)?"
_PASTAENDEN = (
    (
        "risk",
        re.compile(
            r"\b(?P<led>kvarstående\s+|inneboende\s+)?" + _TF + r"risk(?:en|nivån)?" + _AMNE + _FYLLNAD + _VERB
            + r"(?P<niva>mycket\s+hög|låg|måttlig|hög)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "sannolikhet",
        re.compile(
            r"\b" + _TF + r"sannolikhet(?:en)?" + _AMNE + _FYLLNAD + _VERB + r"(?P<niva>medelhög|medel|låg|hög)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "konsekvens",
        re.compile(
            r"\b" + _TF + r"konsekvens(?:en)?" + _AMNE + _FYLLNAD + _VERB + r"(?P<niva>begränsad|betydande|allvarlig)\b",
            re.IGNORECASE,
        ),
    ),
)
# Risknivåer som står före subjektet eller efter kolon: "låg kvarstående risk", "Kvarstående risk: låg",
# "kvarstår en låg risk", "bedömer den kvarstående risken som låg". Bara former där risktypen är entydig.
_NIVA_FORE = r"(?P<niva>mycket\s+höga?|låga?|måttliga?|höga?)"
_RISKAMNE = r"(?P<led>kvarstående\s+|inneboende\s+)?" + _TF + r"risk(?:en|nivån)?" + _AMNE
_PASTAENDEN_FORE = (
    ("risk", r"\b" + _NIVA_FORE + r"\s+(?P<led>kvarstående|inneboende)\s+" + _TF + r"risk(?:en)?" + _AMNE + r"\b"),
    (
        "risk",
        r"\b" + _NIVA_FORE
        + r"\s+(?:(?P<tf>terrorfinansierings)risk|risk\s+för\s+(?P<amne>finansiering\s+av\s+terrorism|terrorfinansiering))\b",
    ),
    ("risk", r"\b" + _RISKAMNE + r"\s*:\s*" + _NIVA_FORE + r"\b"),
    ("risk", r"\bbedömer\s+(?:\w+\s+){0,2}?" + _RISKAMNE + r"\s+(?:som|till)\s+" + _NIVA_FORE + r"\b"),
    ("kvarstår", r"\bkvarstår\s+(?:det\s+)?(?:en\s+)?" + _NIVA_FORE + r"\s+risk\b"),
)
_PASTAENDEN = (*_PASTAENDEN, *((storhet, re.compile(monster, re.IGNORECASE)) for storhet, monster in _PASTAENDEN_FORE))
# Risknivåer som varje riskavsnitt ska ange, med exempel på formulering (spec 7.1 steg 5 och 7).
_BOJDA_NIVAER = {"låga": "låg", "höga": "hög", "måttliga": "måttlig"}


def validera_utkast(utkast: AvsnittsUtkast, underlag: Avsnittsunderlag, personnamn: tuple[str, ...]) -> list[str]:
    """Returnerar alla fel i utkastet. Meddelandena skickas tillbaka till AI och innehåller aldrig personnamn."""
    tillatna_tal = _tal_i(underlag.model_dump_json())
    stycken = [
        fel
        for nummer, stycke in enumerate(utkast.stycken, start=1)
        for fel in _stycke(nummer, stycke, underlag, tillatna_tal, personnamn)
    ]
    return [*_helhet(utkast, underlag), *stycken, *_motiveringar(utkast)]


def motivering_har_hot_och_sarbarhet(stycke: Textstycke) -> bool:
    har_hot = any(ref.startswith("H-") for ref in stycke.referenser)
    har_grund = any(ref.startswith(("S-", "P-")) for ref in stycke.referenser)
    return har_hot and har_grund


def nivapastaenden(text: str) -> list[tuple[str, str]]:
    """Nivåpåståenden i texten som (nivånyckel, nivå), i den ordning de står."""
    traffar = [
        (traff.start(), _nyckel(storhet, traff), _niva(traff["niva"]))
        for storhet, monster in _PASTAENDEN
        for traff in monster.finditer(text)
    ]
    return [(nyckel, niva) for _, nyckel, niva in sorted(traffar)]


def _niva(text: str) -> str:
    """Nivån i grundform med små bokstäver: "Mycket höga" blir "mycket hög"."""
    ord_ = text.lower().split()
    return " ".join([*ord_[:-1], _BOJDA_NIVAER.get(ord_[-1], ord_[-1])])


def _nyckel(storhet: str, traff: re.Match[str]) -> str:
    if storhet == "kvarstår":
        return "kvarstaende_risk"
    grupper = traff.groupdict()
    ar_sank = bool(grupper.get("sf")) or "sanktion" in (grupper.get("amne") or "").lower()
    if ar_sank:
        if storhet == "risk" and (grupper.get("led") or "").strip().lower() == "kvarstående":
            return "kvarstaende_sanktioner_risk"
        return f"sanktioner_{storhet}"
    ar_tf = bool(grupper.get("tf")) or "terror" in (grupper.get("amne") or "").lower()
    if storhet != "risk":
        return f"{'terrorfinansiering' if ar_tf else 'inneboende'}_{storhet}"
    if (grupper.get("led") or "").strip().lower() == "kvarstående":
        return "kvarstaende_terrorfinansiering_risk" if ar_tf else "kvarstaende_risk"
    return "terrorfinansiering_risk" if ar_tf else "inneboende_risk"


def _helhet(utkast: AvsnittsUtkast, underlag: Avsnittsunderlag) -> list[str]:
    tillatna_falt = {u.id for u in underlag.uppgifter}
    fel = [
        f"Oklarhet {nummer}: saknad_uppgift måste vara ett tillåtet, icke-känsligt fält i underlaget."
        for nummer, fraga in enumerate(utkast.oklarheter, start=1)
        if fraga.saknad_uppgift not in tillatna_falt
    ]
    if utkast.avsnitt != underlag.avsnitt:
        fel.append(f"Utkastet gäller avsnitt {utkast.avsnitt}, men underlaget gäller {underlag.avsnitt}.")
    if not utkast.stycken:
        fel.append("Utkastet har inga stycken.")
    return fel


def _nivafel(nummer: int, text: str) -> list[str]:
    """AI anger aldrig nivåer, inte heller för delfaktorer; programmet skriver nivåmeningarna (regel 1)."""
    fel = [
        f"Stycke {nummer} anger en nivå för {BENAMNINGAR[nyckel]}. Programmet skriver alla nivåmeningar; "
        "beskriv delfaktorer med andel, antal, period och egenskap i stället."
        for nyckel in dict.fromkeys(nyckel for nyckel, _ in nivapastaenden(text))
    ]

    if not fel and har_nivasprak(text):
        fel.append(f"Stycke {nummer} anger en nivå. Programmet skriver alla nivåmeningar; beskriv faktorerna med belagda fakta.")
    return fel


def _stycke(
    nummer: int,
    stycke: Textstycke,
    underlag: Avsnittsunderlag,
    tillatna_tal: set[str],
    personnamn: tuple[str, ...],
) -> list[str]:
    tillatna_id = underlag.tillatna_id()
    obekraftade = {uppgift.id for uppgift in underlag.uppgifter if not uppgift.bekraftad}
    liten = stycke.text.lower()
    fel = [] if stycke.referenser else [f"Stycke {nummer} saknar referenser."]
    fel += [
        f"Stycke {nummer} hänvisar till {ref}, som inte finns i underlaget."
        for ref in stycke.referenser
        if ref not in tillatna_id
    ]
    fel += [
        f"Stycke {nummer} innehåller talet {tal}, som inte finns i underlaget."
        for tal in sorted(_tal_i(stycke.text) - tillatna_tal)
    ]
    fel += _nivafel(nummer, stycke.text)
    beroenden = sorted(set(stycke.referenser) & obekraftade)
    if beroenden and VERIFIERA not in stycke.text:
        fel.append(f"Stycke {nummer} bygger på obekräftade uppgifter ({', '.join(beroenden)}) men saknar {VERIFIERA}.")
    fel += [
        f'Stycke {nummer} innehåller den förbjudna formuleringen "{formulering}".'
        for formulering in FORBJUDNA_FORMULERINGAR
        if formulering in liten
    ]
    if any(namn.lower() in liten for namn in personnamn):
        fel.append(f"Stycke {nummer} innehåller ett personnamn. Skriv {{roll:FfR}} i stället.")
    tillatna_roller = ", ".join(f"{{roll:{roll}}}" for roll in ROLLER)
    fel += [
        f"Stycke {nummer} använder platshållaren {{roll:{roll}}}, som inte finns. Tillåtna roller: {tillatna_roller}."
        for roll in dict.fromkeys(roller_i(stycke.text))
        if roll not in ROLLER
    ]
    if VERIFIERA_PREFIX in stycke.text.replace(VERIFIERA, ""):
        fel.append(f"Stycke {nummer} innehåller en egen variant av {VERIFIERA}. Skriv exakt {VERIFIERA}.")
    return fel


def _motiveringar(utkast: AvsnittsUtkast) -> list[str]:
    motiveringar = [(nummer, stycke) for nummer, stycke in enumerate(utkast.stycken, start=1) if stycke.typ == "motivering"]
    if not motiveringar:
        return ["Utkastet saknar ett stycke av typen motivering."]
    return [
        f"Motiveringen i stycke {nummer} måste hänvisa till minst ett hot (H-) och en sårbarhet (S-) eller uppgift (P-)."
        for nummer, stycke in motiveringar
        if not motivering_har_hot_och_sarbarhet(stycke)
    ]




def _tal_i(text: str) -> set[str]:
    return {_normalisera(tal) for tal in _TAL.findall(text)}


def _normalisera(tal: str) -> str:
    med_punkt = tal.translate(_TUSENTAL).replace(",", ".")
    return med_punkt.rstrip("0").rstrip(".") if "." in med_punkt else med_punkt


_AI_NIVA = re.compile(
    r"\b(?:mycket\s+)?(?:låg[at]?|hög[at]?|måttlig[at]?)\s+(?:risk(?:en|er|erna|nivå|nivån)?|sannolikhet(?:en|er|erna)?)\b"
    r"|\b(?:begränsad[e]?|betydande|allvarlig[at]?)\s+konsekvens(?:en|er|erna)?\b"
    r"|\b(?:risker(?:na)?|sannolikheter(?:na)?)\s+(?:är|bedöms\s+som|:)\s+(?:mycket\s+)?(?:låga|måttliga|höga)\b"
    r"|\bkonsekvenser(?:na)?\s+(?:är|bedöms\s+som)\s+(?:begränsade|betydande|allvarliga)\b",
    re.IGNORECASE,
)


def har_nivasprak(text: str) -> bool:
    """Även generiska nivåpåståenden är förbjudna i AI-texten."""
    return bool(nivapastaenden(text) or _AI_NIVA.search(text))
