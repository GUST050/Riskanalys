"""Sakgranskning per avsnitt (spec 10).

En sakgranskning gäller exakt den text som granskaren såg: avsnittet med namnen insatta, så som exporten
skriver ut det. Ändras texten eller ett namn som sätts in i den slutar sakgranskningen att gälla.
"""

from datetime import date
from pathlib import Path

from pydantic import TypeAdapter

from riskanalys.dokument.modeller import Avsnitt, Dokument
from riskanalys.dokument.rendering import renderat_avsnitt
from riskanalys.faststallelse.modeller import Sakgranskning
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.yamlfil import spara_yaml, las_modell
from riskanalys.profil.modeller import Profil

SAKGRANSKNINGSFIL = Path("sakgranskning") / "sakgranskningar.yaml"
_LISTA = TypeAdapter(tuple[Sakgranskning, ...])


class SakgranskningsFel(RiskanalysFel):
    """En sakgranskning kan inte registreras."""


def granskad_summa(avsnitt: Avsnitt, profil: Profil) -> str:
    """Kontrollsumman för det granskaren ser och exporten innehåller."""
    return renderat_avsnitt(avsnitt, profil).kontrollsumma()


def las_sakgranskningar(byramapp: Path) -> tuple[Sakgranskning, ...]:
    sokvag = byramapp / SAKGRANSKNINGSFIL
    if not sokvag.is_file():
        return ()
    return las_modell(sokvag, _LISTA)


def spara_sakgranskningar(byramapp: Path, sakgranskningar: tuple[Sakgranskning, ...]) -> None:
    spara_yaml(byramapp / SAKGRANSKNINGSFIL, [post.model_dump(mode="python") for post in sakgranskningar])


def registrera_sakgranskning(
    sakgranskningar: tuple[Sakgranskning, ...],
    dokument: Dokument,
    profil: Profil,
    avsnitt_id: str,
    godkand: bool,
    roll: str,
    namn: str | None,
    datum: date,
    kommentar: str | None = None,
) -> tuple[Sakgranskning, ...]:
    """Returnerar sakgranskningarna med en ny post för avsnittet så som det ser ut med profilens namn."""
    avsnitt = dokument.avsnitt_med_id().get(avsnitt_id)
    if avsnitt is None:
        tillgangliga = ", ".join(dokument.avsnitt_med_id())
        raise SakgranskningsFel(f"Avsnittet {avsnitt_id} finns inte i dokumentet. Avsnitt: {tillgangliga}.")
    if not namn or not namn.strip():
        raise SakgranskningsFel("Ange vem som sakgranskar med --namn.")
    if not godkand and not (kommentar and kommentar.strip()):
        raise SakgranskningsFel("Ett underkännande kräver --kommentar som säger vad som är fel.")
    post = Sakgranskning(
        avsnitt=avsnitt.id,
        kontrollsumma=granskad_summa(avsnitt, profil),
        godkand=godkand,
        roll=roll,
        namn=namn.strip(),
        datum=datum,
        kommentar=kommentar.strip() if kommentar else None,
    )
    return (*sakgranskningar, post)


def galler_sakgranskning(
    sakgranskningar: tuple[Sakgranskning, ...], avsnitt: Avsnitt, profil: Profil
) -> Sakgranskning | None:
    """Den senaste sakgranskningen av avsnittet i exakt den lydelse som exporten skulle få."""
    summa = granskad_summa(avsnitt, profil)
    giltiga = [post for post in sakgranskningar if post.avsnitt == avsnitt.id and post.kontrollsumma == summa]
    return giltiga[-1] if giltiga else None


def sakgranskningsstatus(sakgranskningar: tuple[Sakgranskning, ...], avsnitt: Avsnitt, profil: Profil) -> str:
    galler = galler_sakgranskning(sakgranskningar, avsnitt, profil)
    if galler is not None:
        utfall = "godkänt" if galler.godkand else f"underkänt ({galler.kommentar})"
        return f"{utfall} {galler.datum.isoformat()} av {galler.namn}, roll {galler.roll}"
    if any(post.avsnitt == avsnitt.id for post in sakgranskningar):
        return "ändrat efter sakgranskningen, granska igen"
    return "ej sakgranskat"
