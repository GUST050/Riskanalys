"""Kontroller per analysdel (spec 8.4.4–8.4.5). Avgör bara det som kan avgöras maskinellt."""

import re

from riskanalys.dokument.faktablad import Faktablad
from riskanalys.dokument.modeller import AISvar
from riskanalys.dokument.platshallare import faltid_fel, platshallarfel
from riskanalys.dokument.validering import FORBJUDNA_FORMULERINGAR, VERIFIERA, har_nivasprak

# Ord per del. Metodval som prövas i piloten.
LANGD = {"hot": (80, 450), "sarbarheter": (100, 600), "kontroller": (60, 400), "risknivaer": (80, 400), "slutsatser": (80, 400)}
_NOLL_RAPPORTER = re.compile(r"\b(?:inga|få|noll)\s+(?:misstanke)?rapporter\b[^.]*\b(?:visar|därför|innebär|tyder)\b", re.IGNORECASE)
_MINSKNING = re.compile(r"\b(?:minskar|begränsar|reducerar|sänker)\b", re.IGNORECASE)
_SAMVERKAN = re.compile(r"\b(?:samverk\w*|kombination\w*|tillsammans|förstärk\w*)\b", re.IGNORECASE)
_INGEN_BELAGD = re.compile(r"\bingen belagd kombination\b", re.IGNORECASE)
_TILLATNA_SIFFROR = re.compile(r"\{[^{}]*\}|\[VERIFIERA\]")
_BELAGD_EFFEKT = "belagd riskreducerande verkan enligt metodvillkor"  # ändra till den text som kontrollstatus() använder för belagd effekt


def _stycke(n: int, s, fb: Faktablad, numeriska: dict[str, str], okanda: set[str], personnamn, lasta) -> list[str]:
    liten = s.text.lower()
    fel = [] if s.referenser else [f"Stycke {n} saknar referenser."]
    fel += [f"Stycke {n} hänvisar till {r}, som inte finns i faktabladet." for r in s.referenser if r not in fb.tillatna_id()]
    fel += platshallarfel(n, s.text, s.referenser, numeriska, fb.perioder())
    fel += faltid_fel(n, s.text)
    if har_nivasprak(s.text):
        fel.append(f"Stycke {n} anger en nivå. Programmet skriver alla nivåmeningar; beskriv faktorer med andel, antal, period och egenskap.")
    if re.search(r"\d", _TILLATNA_SIFFROR.sub("", s.text)):
        fel.append(f"Stycke {n} innehåller siffror. Skriv tal som {{tal:ID}} och perioder som {{period:ID}}.")
    if set(s.referenser) & okanda and VERIFIERA not in s.text:
        fel.append(f"Stycke {n} bygger på obekräftade uppgifter men saknar {VERIFIERA}.")
    fel += [f'Stycke {n} innehåller den förbjudna formuleringen "{f}".' for f in FORBJUDNA_FORMULERINGAR if f in liten]
    if any(namn.lower() in liten for namn in personnamn):
        fel.append(f"Stycke {n} innehåller ett personnamn. Skriv {{roll:FfR}} i stället.")
    fel += [f"Stycke {n} upprepar en låst mening. Bygg vidare på den i stället." for last in lasta if last and last in s.text]
    return fel


def _gemensamma(svar: AISvar, fb: Faktablad, personnamn, lasta) -> list[str]:
    numeriska = fb.numeriska()
    okanda = {p.id for p in fb.poster if p.status == "okänd"}
    fel = [] if svar.stycken else ["Delen har inga stycken."]
    fel += [f"Oklarhet {n}: {o.uppgift_id} finns inte i faktabladet." for n, o in enumerate(svar.oklarheter, 1)
            if o.uppgift_id not in fb.uppgift_id()]
    oklarhetsid={o.uppgift_id for o in svar.oklarheter}
    for n,o in enumerate(svar.oklarheter,1):
        if not o.fraga.strip():
            fel.append(f"Oklarhet {n} saknar fråga.")
        if any(namn.lower() in o.fraga.lower() for namn in personnamn):
            fel.append(f"Oklarhet {n} innehåller ett personnamn.")
    for n, s in enumerate(svar.stycken, 1):
        if re.search(r"\[VERIFIERA[^\]]*\]",s.text) and re.search(r"\[VERIFIERA(?!\])",s.text):
            fel.append(f"Stycke {n} har felskriven [VERIFIERA].")
        for id in (set(s.referenser) & okanda) - oklarhetsid:
            fel.append(f"Oklarhet saknas för obekräftad uppgift {id}.")
        fel += _stycke(n, s, fb, numeriska, okanda, personnamn, lasta)
    return fel


def _per_del(del_id: str, svar: AISvar, fb: Faktablad) -> list[str]:
    refs = [r for s in svar.stycken for r in s.referenser]
    text = " ".join(s.text for s in svar.stycken)
    fel = []
    if del_id == "hot":
        if len({r for r in refs if r.startswith("H-")}) < 2:
            fel.append("Delen ska hänvisa till minst två hot (H-) ur faktabladet.")
        if fb.tf_hot and not set(refs) & set(fb.tf_hot):
            fel.append("Hotanalysen ska hänvisa till ett hot om terrorfinansiering ur faktabladet.")
        if _NOLL_RAPPORTER.search(text):
            fel.append("Få eller inga rapporter får inte användas som belägg för att hotet är litet.")
    if del_id == "sarbarheter":
        kategorier={fb.sarbarhetsomraden[r] for r in refs if r in fb.sarbarhetsomraden}
        fel.extend(f"Sårbarheterna saknar en referens i kategori {k}." for k in sorted(set(fb.sarbarhetsomraden.values())-kategorier))
        fel += [f"Stycke {n} beskriver en kombination utan belagt överlapp. Använd stycketypen scenario."
                for n, s in enumerate(svar.stycken, 1)
                if s.typ == "analys" and _SAMVERKAN.search(_INGEN_BELAGD.sub("", s.text)) and
                    len({r.id for r in fb.sarbarheter if r.id in s.referenser}) >= 2]
    if del_id == "kontroller":
        belagda = {k.id for k in fb.kontroller if _BELAGD_EFFEKT in k.status}
        fel += [f"Stycke {n} säger att risken minskar utan hänvisning till en kontroll med belagd effekt."
                for n, s in enumerate(svar.stycken, 1) if _pastaende_om_minskning(s.text) and not set(s.referenser) & belagda]
    if del_id == "risknivaer" and not any(
            s.typ == "motivering" and any(r.startswith("H-") for r in s.referenser)
            and any(r.startswith(("S-", "P-")) for r in s.referenser) for s in svar.stycken):
        fel.append("Minst ett stycke av typen motivering ska hänvisa till ett hot och en sårbarhet eller uppgift.")
    if del_id == "slutsatser":
        fel += [f"Slutsatserna ska ta upp {ord_} i tjänsten." for ord_ in ("kundkännedom", "övervakning", "utbildning")
                if ord_ not in text.lower()]
        if not any(r.startswith("H-") for r in refs):
            fel.append("Slutsatserna ska hänvisa till minst ett hot (H-).")
    lagst, hogst = LANGD[del_id]
    antal = len(text.split())
    if not lagst <= antal <= hogst:
        fel.append(f"Delen ska vara {lagst}–{hogst} ord; den är {antal} ord.")
    return fel


def validera_del(del_id: str, svar: AISvar, fb: Faktablad, personnamn: tuple[str, ...], lasta: tuple[str, ...]) -> list[str]:
    return [*_gemensamma(svar, fb, personnamn, lasta), *_per_del(del_id, svar, fb)]


def _pastaende_om_minskning(text: str) -> bool:
    for m in _MINSKNING.finditer(text):
        efter=text[m.end():]
        if not re.match(r"\s+(?:inte|ej|aldrig)\b",efter,re.IGNORECASE):
            return True
    return False
