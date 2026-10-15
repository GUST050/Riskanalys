"""Word-export (spec 10 och 11). Personnamn sätts in först här och skickas aldrig till AI."""

import re
from collections.abc import Iterable
from datetime import date
from pathlib import Path

import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

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
    return any(VERIFIERA_PREFIX in text for text in synliga_texter(renderat_avsnitt(avsnitt, profil)))


def avsnittsnummer(avsnitt_id: str) -> str:
    """D-ARB.6.1 blir 6.1."""
    return avsnitt_id.split(".", 1)[1]


def renderat_avsnitt(avsnitt: Avsnitt, profil: Profil) -> Avsnitt:
    """Avsnittet som granskaren ser och exporten innehåller: platshållarna utbytta mot namn eller [VERIFIERA: roll]."""
    stycken = tuple(
        stycke.model_copy(update={"text": ersatt_platshallare(stycke.text, profil)}) for stycke in avsnitt.stycken
    )
    return avsnitt.model_copy(update={
        "stycken": stycken,
        "visningsnummer": ersatt_platshallare(avsnitt.visningsnummer, profil) if avsnitt.visningsnummer is not None else None,
        "rubrik": ersatt_platshallare(avsnitt.rubrik, profil),
        "underrubriker": tuple(u.model_copy(update={"rubrik": ersatt_platshallare(u.rubrik, profil)}) for u in avsnitt.underrubriker),
        "tabeller": tuple(t.model_copy(update={
            "rubrik": ersatt_platshallare(t.rubrik, profil),
            "kolumner": tuple(ersatt_platshallare(k, profil) for k in t.kolumner),
            "rader": tuple(r.model_copy(update={"celler": tuple(c.model_copy(update={
                "text": ersatt_platshallare(c.text, profil)}) for c in r.celler)}) for r in t.rader),
        }) for t in avsnitt.tabeller),
    })


def synliga_texter(avsnitt: Avsnitt) -> tuple[str, ...]:
    """Synliga rubriker och innehåll i läsordning; anropa efter lokal namninsättning."""
    texter = [f"{avsnitt.visningsnummer or avsnittsnummer(avsnitt.id)} {avsnitt.rubrik}"]
    for index in range(len(avsnitt.stycken) + 1):
        texter.extend(u.rubrik for u in avsnitt.underrubriker if u.fore_stycke == index)
        for tabell in avsnitt.tabeller:
            if tabell.fore_stycke == index:
                texter.extend((tabell.rubrik, *tabell.kolumner))
                texter.extend(c.text for r in tabell.rader for c in r.celler)
        if index < len(avsnitt.stycken):
            texter.append(avsnitt.stycken[index].text)
    return tuple(texter)


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
    v5 = dokument.formatversion == "D-ARB-tjanst-v5"
    avsnitten = tuple(renderat_avsnitt(post, profil) for post in dokument.avsnitt)
    if v5:
        from riskanalys.dokument.wordstil import formatera_dokument
        formatera_dokument(word)
        _innehallsforteckning(word, avsnitten)
        for sektion in word.sections:
            _falt(sektion.footer.paragraphs[0], "PAGE", "Sidnummer uppdateras i Word")
    for nummer, avsnitt in enumerate(avsnitten):
        rubrik = word.add_heading(f"{avsnitt.visningsnummer or avsnittsnummer(avsnitt.id)} {avsnitt.rubrik}", level=1)
        if v5:
            _bokmarke(rubrik, nummer)
            if avsnitt.id == "D-ARB.B1":
                rubrik.paragraph_format.page_break_before = True
        underrubriker = {u.fore_stycke: u.rubrik for u in avsnitt.underrubriker}
        for index in range(len(avsnitt.stycken) + 1):
            if index in underrubriker:
                word.add_heading(underrubriker[index], level=2)
            if v5:
                for tabell in avsnitt.tabeller:
                    if tabell.fore_stycke == index:
                        _tabell(word, tabell)
            if index < len(avsnitt.stycken):
                word.add_paragraph(avsnitt.stycken[index].text)
    if bilaga:
        word.add_heading(BILAGERUBRIK, level=1)
        for rad in bilaga:
            word.add_paragraph(rad, style="List Bullet")
    sokvag.parent.mkdir(parents=True, exist_ok=True)
    word.save(str(sokvag))
    return sokvag


def _falt(stycke, instruktion: str, reservtext: str) -> None:
    """Word beräknar fältet; reservtexten påstår inga beräknade sidnummer."""
    for typ in ("begin", "separate", "end"):
        if typ == "separate":
            kod = OxmlElement("w:instrText")
            kod.set(qn("xml:space"), "preserve")
            kod.text = f" {instruktion} "
            stycke.add_run()._r.append(kod)
        element = OxmlElement("w:fldChar")
        element.set(qn("w:fldCharType"), typ)
        if typ == "begin":
            element.set(qn("w:dirty"), "true")
        stycke.add_run()._r.append(element)
        if typ == "separate":
            stycke.add_run(reservtext)


def _bokmarke(stycke, nummer: int) -> None:
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(nummer))
    start.set(qn("w:name"), f"arb_avsnitt_{nummer}")
    slut = OxmlElement("w:bookmarkEnd")
    slut.set(qn("w:id"), str(nummer))
    stycke._p.insert(0, start)
    stycke._p.append(slut)


def _innehallsforteckning(word, avsnitt: tuple[Avsnitt, ...]) -> None:
    word.add_heading("Innehåll", level=2)
    _falt(word.add_paragraph(), r'TOC \o "1-1" \h \z \u', "Uppdatera innehållsförteckningen i Word för sidnummer.")
    uppdatera = OxmlElement("w:updateFields")
    uppdatera.set(qn("w:val"), "true")
    word.settings.element.append(uppdatera)
    for nummer, post in enumerate(avsnitt):
        stycke = word.add_paragraph()
        from docx.shared import Pt
        stycke.paragraph_format.space_after = Pt(0)
        lank = OxmlElement("w:hyperlink")
        lank.set(qn("w:anchor"), f"arb_avsnitt_{nummer}")
        run = OxmlElement("w:r")
        text = OxmlElement("w:t")
        text.text = f"{post.visningsnummer or avsnittsnummer(post.id)} {post.rubrik}"
        run.append(text)
        lank.append(run)
        stycke._p.append(lank)


def _tabell(word, tabell) -> None:
    word.add_heading(tabell.rubrik, level=3)
    tab = word.add_table(rows=1, cols=len(tabell.kolumner))
    tab.style = "Table Grid"
    for cell, rubrik in zip(tab.rows[0].cells, tabell.kolumner):
        cell.text = rubrik
        for run in cell.paragraphs[0].runs:
            run.bold = True
    header = OxmlElement("w:tblHeader")
    tab.rows[0]._tr.get_or_add_trPr().append(header)
    for rad in tabell.rader:
        for cell, innehall in zip(tab.add_row().cells, rad.celler):
            cell.text = innehall.text
    from riskanalys.dokument.wordstil import formatera_tabell
    formatera_tabell(word, tab, tabell.id)
