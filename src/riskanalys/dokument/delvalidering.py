"""Kontroller per analysdel (spec 8.4.4–8.4.5). Avgör bara det som kan avgöras maskinellt."""

import re

from riskanalys.dokument.faktablad import Faktablad
from riskanalys.dokument.modeller import AISvar
from riskanalys.dokument.rendering import ROLLER
from riskanalys.dokument.platshallare import faltid_fel, platshallarfel
from riskanalys.dokument.validering import FORBJUDNA_FORMULERINGAR, VERIFIERA, har_nivasprak

# Ord per del. Metodval som prövas i piloten.
LANGD = {"analys": (160, 320),"hot": (80, 160), "sarbarheter": (100, 220), "kontroller": (60, 120), "risknivaer": (80, 120), "slutsatser": (80, 130)}
# Smala språkprov kompletterar sakgranskning; de bevisar inte semantisk riktighet.
_UTFALLSMOTIVERING = re.compile(
    r"\b(?:därför\s+är\s+risknivån|risknivån\s+(?:är\s+motiverad|avviker\s+från\s+sektorns))\b",
    re.IGNORECASE,
)
_NOLL_RAPPORTER = re.compile(r"\b(?:inga|få|noll)\s+(?:misstanke)?rapporter\b[^.]*\b(?:visar|därför|innebär|tyder)\b", re.IGNORECASE)
_MINSKNING = re.compile(r"\b(?:minskar|begränsar|reducerar|sänker)\b", re.IGNORECASE)
_SAMVERKAN = re.compile(r"\b(?:samverk\w*|kombination\w*|tillsammans|förstärk\w*)\b", re.IGNORECASE)
# Spec 8.4.4 tillåter att analysen konstaterar att ingen belagd kombination finns.
_INGEN_BELAGD = re.compile(
    r"\b(?:ingen\s+belagd\s+kombination|inga\s+belagda\s+kombinationer|ingen\s+kombination\s+är\s+belagd)\b",
    re.IGNORECASE)
_TILLATNA_SIFFROR = re.compile(r"\{[^{}]*\}|\[VERIFIERA\]")
# Sanktionsfrågan gäller sedan detta datum identifierad anknytning; ett nej befriar inte från prövning.
SANKTION_OMFORMULERAD = '2026-10-17'
# Negation och "behöver ... prövas ... sanktion" i samma mening, med negationen före eller efter "behöver".
_SANKTIONSUNDANTAG = re.compile(
    r"(?:\b(?:ingen|inte|inga)\b[^.!?]*\bbehöver\b|\bbehöver\b[^.!?]*\b(?:ingen|inte|inga)\b)"
    r"[^.!?]*\bprövas\b[^.!?]*sanktion|\bsanktion\w*\b[^.!?]*\bbehöver\b[^.!?]*\b(?:inte|ej|aldrig)\b[^.!?]*\bprövas\b",
    re.IGNORECASE)
_PROVAS_LOKALT = re.compile(r"\bprövas\s+lokalt\b", re.IGNORECASE)
_KONTROLLVERB = r"(?:kontrollerar|stämmer\s+av|verifierar|granskar)"
_GENOMFORD_KONTROLL = re.compile(
    r"\b(?:vi|jag|byrån)\s+(?:(?:alltid|regelbundet|redan)\s+)*"
    r"(?:(?:har|hade)\s+(?:(?:alltid|redan)\s+)*(?:kontrollerat|stämt\s+av|verifierat|granskat)|"
    + _KONTROLLVERB + r")\b|\b" + _KONTROLLVERB + r"\s+(?:vi|jag|byrån)\b", re.IGNORECASE)


def _genomford_kontroll(text: str) -> bool:
    """Avgränsade utförandepåståenden; uttryckliga hypotetiska scenarier och råd förblir tillåtna."""
    for mening in re.split(r"[.!?]", text):
        if re.match(r"\s*(?:om\b|vid\s+en\s+tänkt\b)", mening, re.IGNORECASE):
            continue
        for match in _GENOMFORD_KONTROLL.finditer(mening):
            if not re.search(r"\b(?:rekommenderar|föreslår)\b.*\batt\s*$", mening[:match.start()], re.IGNORECASE):
                return True
    return False


_PASSIV_KONTROLL = re.compile(
    r"\b(?:kontroll\w*|avstämning\w*|granskning\w*)\b[^.!?]*\b"
    r"(?:har\s+(?:genomförts|utförts)|är\s+(?:utförd|genomförd))\b", re.IGNORECASE)
_KONTROLLEFFEKT = re.compile(
    r"\b(?:kontroll\w*|avstämning\w*|granskning\w*)\b[^.!?]*\b"
    r"(?:är|var|har\s+varit)\s+(?:(?:alltid|bevisat|dokumenterat)\s+)?(?:effektiv\w*|belagd)\b", re.IGNORECASE)
SANKTIONSFEL = 'Texten påstår att sanktioner inte behöver prövas. Skriv att ingen anknytning har identifierats.'
# Endast V7/analys använder den neutrala rättningsinstruktionen; äldre omförsök behåller sin identitet.
SANKTIONSFEL_V7 = ('Texten påstår att sanktioner inte behöver prövas. Skriv inget undantag från prövning. '
                  'Återge bara faktabladets uppgift om sanktionsanknytning; frånvaro får bara anges vid belagt nej. '
                  'Vid ja eller okänt får du inte förneka anknytning.')
_INGEN_SANKTIONSANKNYTNING = re.compile(
    r'\bingen\s+(?:sanktionsanknytning|anknytning(?:\s+till\s+(?:internationella\s+)?sanktioner)?)'
    r'\s+har\s+identifierats\b', re.IGNORECASE)


def _belagt_sanktionsnej(fb: Faktablad) -> bool:
    return any(p.id == 'P-GEO.sanktionsanknytning' and p.status == 'bekräftad'
               and p.visningsvarde.strip().lower() == 'nej' for p in fb.poster)

# Kommentarer om vad AI har fått se hör inte hemma i riskbedömningen; "AI-verktyg" och "tolkas av AI" godtas.
_AI_KOMMENTAR = re.compile(r"\b(?i:till|för|åt)\s+AI\b(?![-–])")


def _har_namn(text: str, personnamn: tuple[str, ...]) -> bool:
    """Hela namn med Unicode-ordgränser och valfri genitiv; rollplatshållare är inte namn."""
    utan_roller = text
    for roll in ROLLER:
        utan_roller = utan_roller.replace(f"{{roll:{roll}}}", " ")
    return any(re.search(r"(?<!\w)" + re.escape(namn.strip()) + r"s?(?!\w)",
                         utan_roller, re.IGNORECASE)
               for namn in personnamn if namn.strip())


def innehaller_personnamn(svar: AISvar, personnamn: tuple[str, ...]) -> bool:
    """Lokal namnkontroll efter tjänstens alla AI-anrop (spec 8.4.10 punkt 7)."""
    texter = (*(s.text for s in svar.stycken), *(o.fraga for o in svar.oklarheter))
    return any(_har_namn(text, personnamn) for text in texter)


def _stycke(n: int, s, fb: Faktablad, numeriska: dict[str, str], okanda: set[str], personnamn, lasta) -> list[str]:
    liten = s.text.lower()
    fel = [] if s.referenser else [f"Stycke {n} saknar referenser."]
    fel += [f"Stycke {n} hänvisar till {r}, som inte finns i faktabladet." for r in s.referenser if r not in fb.tillatna_id()]
    fel += platshallarfel(n, s.text, s.referenser, numeriska, fb.perioder())
    fel += faltid_fel(n, s.text)
    if _AI_KOMMENTAR.search(s.text):
        fel.append(f"Stycke {n} kommenterar vilket underlag AI har fått. Skriv i stället att underlaget behöver granskas lokalt.")
    if har_nivasprak(s.text):
        fel.append(f"Stycke {n} anger en nivå. Programmet skriver alla nivåmeningar; beskriv faktorer med andel, antal, period och egenskap.")
    if re.search(r"\d", _TILLATNA_SIFFROR.sub("", s.text)):
        fel.append(f"Stycke {n} innehåller siffror. Skriv tal som {{tal:ID}} och perioder som {{period:ID}}.")
    if set(s.referenser) & okanda and VERIFIERA not in s.text:
        fel.append(f"Stycke {n} bygger på obekräftade uppgifter men saknar {VERIFIERA}.")
    fel += [f'Stycke {n} innehåller den förbjudna formuleringen "{f}".' for f in FORBJUDNA_FORMULERINGAR if f in liten]
    if _har_namn(s.text, personnamn):
        fel.append(f"Stycke {n} innehåller ett personnamn. Skriv {{roll:FfR}} i stället.")
    fel += [f"Stycke {n} upprepar en låst mening. Bygg vidare på den i stället." for last in lasta if last and last in s.text]
    return fel


def _gemensamma(svar: AISvar, fb: Faktablad, personnamn, lasta, *, sanktionsfel: str = SANKTIONSFEL) -> list[str]:
    numeriska = fb.numeriska()
    okanda = {p.id for p in fb.poster if p.status == "okänd"}
    fel = [] if svar.stycken else ["Delen har inga stycken."]
    fel += [f"Oklarhet {n}: {o.uppgift_id} finns inte i faktabladet." for n, o in enumerate(svar.oklarheter, 1)
            if o.uppgift_id not in fb.uppgift_id()]
    oklarhetsid={o.uppgift_id for o in svar.oklarheter}
    for n,o in enumerate(svar.oklarheter,1):
        if not o.fraga.strip():
            fel.append(f"Oklarhet {n} saknar fråga.")
        if _har_namn(o.fraga, personnamn):
            fel.append(f"Oklarhet {n} innehåller ett personnamn.")
    for n, s in enumerate(svar.stycken, 1):
        if re.search(r"\[VERIFIERA[^\]]*\]",s.text) and re.search(r"\[VERIFIERA(?!\])",s.text):
            fel.append(f"Stycke {n} har felskriven [VERIFIERA].")
        if _SANKTIONSUNDANTAG.search(s.text):
            fel.append(f"Stycke {n}: {sanktionsfel}")
        for id in (set(s.referenser) & okanda) - oklarhetsid:
            fel.append(f"Oklarhet saknas för obekräftad uppgift {id}.")
        fel += _stycke(n, s, fb, numeriska, okanda, personnamn, lasta)
    return fel


def _per_del(del_id: str, svar: AISvar, fb: Faktablad) -> list[str]:
    refs = [r for s in svar.stycken for r in s.referenser]
    text = " ".join(s.text for s in svar.stycken)
    fel = []
    if del_id in ("hot", "analys"):
        if len({r for r in refs if r.startswith("H-")}) < 2:
            fel.append("Delen ska hänvisa till minst två hot (H-) ur faktabladet.")
        if fb.tf_hot and not set(refs) & set(fb.tf_hot):
            fel.append("Hotanalysen ska hänvisa till ett hot om terrorfinansiering ur faktabladet.")
        if _NOLL_RAPPORTER.search(text):
            fel.append("Få eller inga rapporter får inte användas som belägg för att hotet är litet.")
    if del_id in ("sarbarheter", "analys"):
        kategorier={fb.sarbarhetsomraden[r] for r in refs if r in fb.sarbarhetsomraden}
        fel.extend(f"Sårbarheterna saknar en referens i kategori {k}." for k in sorted({omrade for id, omrade in fb.sarbarhetsomraden.items()
                if del_id != "analys" or next((s.galler for s in fb.sarbarheter if s.id == id), None) != "prövas lokalt"}-kategorier))
        # Faktorer är sårbarheter och faktauppgifter; ingen faktarad belägger att två faktorer avser samma kunder.
        faktorer = {r.id for r in fb.sarbarheter} | fb.uppgift_id()
        fel += [f"Stycke {n} beskriver en kombination utan belagt överlapp. Använd stycketypen scenario."
                for n, s in enumerate(svar.stycken, 1)
                if s.typ == "analys" and _SAMVERKAN.search(_INGEN_BELAGD.sub("", s.text)) and
                    len(set(s.referenser) & faktorer) >= 2]
    if del_id in ("kontroller", "analys"):
        # AI får inte veta om en kontroll har belagd effekt (spec 8.4.10 punkt 4), så inget påstående om minskning
        # kan vara tillåtet; programmet avgör det lokalt.
        fel += [f"Stycke {n} säger att risken minskar. Programmet avgör lokalt om en kontroll räknas som "
                "riskreducerande; använd inte orden minskar, begränsar, reducerar eller sänker i den här delen."
                for n, s in enumerate(svar.stycken, 1) if _pastaende_om_minskning(s.text)]
    if del_id in ("risknivaer", "analys") and not any(
            (del_id == "analys" or s.typ == "motivering") and any(r.startswith("H-") for r in s.referenser)
            and any(r.startswith(("S-", "P-")) for r in s.referenser) for s in svar.stycken):
        fel.append("Minst ett stycke av typen motivering ska hänvisa till ett hot och en sårbarhet eller uppgift.")
    if del_id == "risknivaer" and _UTFALLSMOTIVERING.search(text):
        fel.append("Delen motiverar ett motorutfall. Beskriv endast kvalitativa samband och villkorliga scenarier.")
    if del_id == "slutsatser":
        fel += [f"Slutsatserna ska ta upp {ord_} i tjänsten." for ord_ in ("kundkännedom", "övervakning", "utbildning")
                if ord_ not in text.lower()]
        if not any(r.startswith("H-") for r in refs):
            fel.append("Slutsatserna ska hänvisa till minst ett hot (H-).")
    if del_id == "analys":
        for n, s in enumerate(svar.stycken, 1):
            if _INGEN_SANKTIONSANKNYTNING.search(s.text) and not _belagt_sanktionsnej(fb):
                fel.append(f"Stycke {n} påstår att ingen sanktionsanknytning identifierats utan belagt nej i faktabladet. "
                           "Utelämna frånvaropåståendet och beskriv uppgiften utan att förneka anknytning.")
            if _PROVAS_LOKALT.search(s.text):
                fel.append(f"Stycke {n} innehåller prövas lokalt. Utelämna dessa sårbarheter; programmet skriver utfallet.")
            if _genomford_kontroll(s.text) or _PASSIV_KONTROLL.search(s.text):
                fel.append(f"Stycke {n} påstår genomförd kontroll. Beskriv bara katalogens generella räckvidd.")
            if _KONTROLLEFFEKT.search(s.text):
                fel.append(f"Stycke {n} påstår kontrolleffekt. Lokal effekt ska prövas av programmet och byrån.")
            privata = ({x.id for x in fb.sarbarheter if x.galler == "prövas lokalt"}
                       | {x.id for x in fb.poster if x.status == "skyddad"})
            if set(s.referenser) & privata:
                fel.append(f"Stycke {n} hänvisar till skyddat värde eller sårbarhet som prövas lokalt. Utelämna den; programmet skriver utfallet.")
        if _UTFALLSMOTIVERING.search(text):
            fel.append("Delen motiverar ett motorutfall. Beskriv endast kvalitativa samband och villkorliga scenarier.")
    lagst, hogst = LANGD[del_id]
    antal = len(text.split())
    if not lagst <= antal <= hogst:
        fel.append(f"Delen ska vara {lagst}–{hogst} ord; den är {antal} ord.")
    return fel


def validera_del(del_id: str, svar: AISvar, fb: Faktablad, personnamn: tuple[str, ...], lasta: tuple[str, ...]) -> list[str]:
    sanktionsfel = SANKTIONSFEL_V7 if del_id == "analys" else SANKTIONSFEL
    return [*_gemensamma(svar, fb, personnamn, lasta, sanktionsfel=sanktionsfel), *_per_del(del_id, svar, fb)]


def _pastaende_om_minskning(text: str) -> bool:
    for m in _MINSKNING.finditer(text):
        efter=text[m.end():]
        if not re.match(r"\s+(?:inte|ej|aldrig)\b",efter,re.IGNORECASE):
            return True
    return False
