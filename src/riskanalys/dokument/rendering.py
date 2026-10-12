"""Word-export (spec 10 och 11). Personnamn sätts in först här och skickas aldrig till AI."""

import re
from collections.abc import Iterable
from datetime import date
from pathlib import Path

import docx

from riskanalys.dokument.modeller import Avsnitt, Dokument, Oklarhet
from riskanalys.granskning.modeller import Fynd
from riskanalys.profil.modeller import Profil

ROLLER = {"FfR": "P-ROLL.ffr_namn", "Ansvarsfunktion": "P-ROLL.ansvarsfunktion"}
UTKASTMARKERING = "UTKAST – ej fastställt av byrån"
BILAGERUBRIK = "Bilaga: Åtgärdslista"
_PLATSHALLARE = re.compile(r"\{roll:(\w+)\}")
VERIFIERA_PREFIX = "[VERIFIERA"


def roller_i(text: str) -> tuple[str, ...]:
    """Rollerna i textens platshållare, i den ordning de står."""
    return tuple(_PLATSHALLARE.findall(text))


def ersatt_platshallare(text: str, profil: Profil) -> str:
    """Byter {roll:X} mot det bekräftade namnet, eller mot [VERIFIERA: X] om namnet saknas."""

    def ersatt(traff: re.Match[str]) -> str:
        roll = traff.group(1)
        falt_id = ROLLER.get(roll)
        if falt_id is None or not profil.ar_bekraftad(falt_id):
            return f"[VERIFIERA: {roll}]"
        return str(profil.uppgifter[falt_id].varde)

    return _PLATSHALLARE.sub(ersatt, text)


def har_verifiera(avsnitt: Avsnitt, profil: Profil) -> bool:
    """Om avsnittet så som det skrivs ut har en [VERIFIERA]-markering av något slag, till exempel [VERIFIERA: FfR]."""
    return any(VERIFIERA_PREFIX in stycke.text for stycke in renderat_avsnitt(avsnitt, profil).stycken)


def avsnittsnummer(avsnitt_id: str) -> str:
    """D-ARB.6.1 blir 6.1."""
    return avsnitt_id.split(".", 1)[1]


def renderat_avsnitt(avsnitt: Avsnitt, profil: Profil) -> Avsnitt:
    """Avsnittet som granskaren ser och exporten innehåller: platshållarna utbytta mot namn eller [VERIFIERA: roll]."""
    stycken = tuple(
        stycke.model_copy(update={"text": ersatt_platshallare(stycke.text, profil)}) for stycke in avsnitt.stycken
    )
    return avsnitt.model_copy(update={"stycken": stycken})


def utkaststatus(datum: date) -> str:
    return f"{UTKASTMARKERING}. Skapat {datum.isoformat()}."


def faststalld_status(organ: str, datum: date, version: int) -> str:
    """Statusraden för en fastställd version. Den påstår aldrig att regelverket är uppfyllt (spec 10)."""
    return f"Fastställt av {organ} {datum.isoformat()}. Version {version}."


def atgardslista(fynd: Iterable[Fynd], oklarheter: Iterable[tuple[str, Oklarhet]]) -> tuple[str, ...]:
    """Öppna fynd och AI:ns oklarheter, en rad var (spec 11)."""
    fyndrader = [
        f"{post.id} ({post.allvar}): {post.beskrivning} Åtgärd: {post.atgard}" for post in fynd if post.status == "öppen"
    ]
    oklarhetsrader = [
        f"{avsnitt}: {oklarhet.fraga} Uppgift som saknas: {oklarhet.saknad_uppgift}." for avsnitt, oklarhet in oklarheter
    ]
    return (*fyndrader, *oklarhetsrader)


def rendera_docx(
    dokument: Dokument, profil: Profil, statusrad: str, sokvag: Path, bilaga: tuple[str, ...] = ()
) -> Path:
    """Skriver dokumentet som Word-fil med statusraden i sidhuvudet, så att den syns på varje sida."""
    word = docx.Document()
    for sektion in word.sections:
        sektion.header.paragraphs[0].text = statusrad
    word.add_heading(dokument.titel, level=0)
    word.add_paragraph().add_run(statusrad).bold = True
    for avsnitt in (renderat_avsnitt(post, profil) for post in dokument.avsnitt):
        word.add_heading(f"{avsnittsnummer(avsnitt.id)} {avsnitt.rubrik}", level=1)
        underrubriker = {u.fore_stycke: u.rubrik for u in avsnitt.underrubriker}
        for index, stycke in enumerate(avsnitt.stycken):
            if index in underrubriker:
                word.add_heading(underrubriker[index], level=2)
            word.add_paragraph(stycke.text)
    if bilaga:
        word.add_heading(BILAGERUBRIK, level=1)
        for rad in bilaga:
            word.add_paragraph(rad, style="List Bullet")
    sokvag.parent.mkdir(parents=True, exist_ok=True)
    word.save(str(sokvag))
    return sokvag
