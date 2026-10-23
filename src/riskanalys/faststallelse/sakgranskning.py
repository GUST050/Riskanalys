"""Sakgranskning per avsnitt (spec 10).

En sakgranskning gäller exakt den text som granskaren såg: avsnittet med namnen insatta, så som exporten
skriver ut det. Ändras texten eller ett namn som sätts in i den slutar sakgranskningen att gälla.
"""

from datetime import date
from pathlib import Path
import json

from pydantic import TypeAdapter

from riskanalys.dokument.modeller import Avsnitt, Dokument
from riskanalys.dokument.rendering import renderat_avsnitt
from riskanalys.faststallelse.modeller import Sakgranskning
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.yamlfil import spara_yaml, las_modell
from riskanalys.profil.modeller import Profil
from riskanalys.lagring.kontrollsumma import for_text

SAKGRANSKNINGSFIL = Path("sakgranskning") / "sakgranskningar.yaml"
_LISTA = TypeAdapter(tuple[Sakgranskning, ...])


class SakgranskningsFel(RiskanalysFel):
    """En sakgranskning kan inte registreras."""


def granskad_summa(avsnitt: Avsnitt, profil: Profil) -> str:
    """Kontrollsumman för det granskaren ser och exporten innehåller."""
    return renderat_avsnitt(avsnitt, profil).kontrollsumma()


def _har_struktur(dokument: Dokument) -> bool:
    return dokument.formatversion in ("D-ARB-tjanst-v5", "D-ARB-tjanst-v5.1", "D-ARB-tjanst-v6", "D-ARB-tjanst-v7", "D-ARB-tjanst-v8", "D-ARB-resultat-v9", "D-ARB-resultat-v10") or any(a.underrubriker for a in dokument.avsnitt)


def struktur_summa(dokument: Dokument, *, presentation=None) -> str:
    """Titel, format och faktisk avsnittsordning i det granskade dokumentet."""
    if dokument.formatversion == 'D-ARB-resultat-v10':
        from riskanalys.dokument.rapportvyer_v10 import vystruktur_v10
        return for_text(json.dumps({'dokument':dokument.model_dump(mode='json'),
            'vyer':vystruktur_v10(dokument),'presentation':presentation.model_dump(mode='json') if presentation else None},
            ensure_ascii=False,sort_keys=True,separators=(',',':')))
    if dokument.formatversion == 'D-ARB-resultat-v9':
        from riskanalys.dokument.rapportvyer_v9 import vystruktur_v9
        return for_text(json.dumps({'dokument':dokument.model_dump(mode='json'),
            'vyer':vystruktur_v9(dokument),'presentation':presentation.model_dump(mode='json') if presentation else None},
            ensure_ascii=False,sort_keys=True,separators=(',',':')))
    if dokument.formatversion == "D-ARB-tjanst-v8":
        from riskanalys.dokument.rapportvyer import vystruktur
        return for_text(json.dumps({'titel': dokument.titel, 'format': dokument.formatversion,
            'presentation': presentation.model_dump(mode='json') if presentation else None, 'vyer': vystruktur(dokument), 'avsnitt': [(a.id,a.rubrik,a.visningsnummer,a.leveransdel,
                [(u.fore_stycke,u.rubrik) for u in a.underrubriker],
                [(t.id,t.fore_stycke,t.rubrik,t.kolumner) for t in a.tabeller]) for a in dokument.avsnitt]},
            ensure_ascii=False,separators=(',', ':')))
    if dokument.formatversion in ("D-ARB-tjanst-v5", "D-ARB-tjanst-v5.1", "D-ARB-tjanst-v6", "D-ARB-tjanst-v7", "D-ARB-tjanst-v8", "D-ARB-resultat-v9", "D-ARB-resultat-v10"):
        return for_text(json.dumps({"titel": dokument.titel, "format": dokument.formatversion,
            "avsnitt": [(a.id, a.rubrik, a.visningsnummer,
                         [(u.fore_stycke, u.rubrik) for u in a.underrubriker],
                         [(t.id, t.fore_stycke, t.rubrik, t.kolumner) for t in a.tabeller])
                        for a in dokument.avsnitt]}, ensure_ascii=False, separators=(',', ':')))
    return for_text(json.dumps({'titel': dokument.titel, 'avsnitt': [
        (a.id, a.rubrik, [(u.fore_stycke, u.rubrik) for u in a.underrubriker])
        for a in dokument.avsnitt]}, ensure_ascii=False, separators=(',', ':')))


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
    *, analysbindning: str | None = None, presentation=None,
) -> tuple[Sakgranskning, ...]:
    """Registrera enskilda avsnitt; Resultatrapporten kräver samlad granskning."""
    avsnitt = dokument.avsnitt_med_id().get(avsnitt_id)
    if avsnitt and _ar_resultatavsnitt(avsnitt):
        raise SakgranskningsFel(
            'Resultatrapporten ska granskas samlat. Använd --resultatrapport och --visad-struktursumma.'
        )
    return _registrera_sakgranskning(
        sakgranskningar, dokument, profil, avsnitt_id, godkand, roll, namn, datum, kommentar,
        analysbindning=analysbindning, presentation=presentation,
    )


def _ar_resultatavsnitt(avsnitt: Avsnitt) -> bool:
    return avsnitt.formatversion in ('D-ARB-resultat-v9','D-ARB-resultat-v10') and avsnitt.leveransdel == 'resultatrapport'


def _registrera_sakgranskning(
    sakgranskningar: tuple[Sakgranskning, ...],
    dokument: Dokument,
    profil: Profil,
    avsnitt_id: str,
    godkand: bool,
    roll: str,
    namn: str | None,
    datum: date,
    kommentar: str | None = None,
    *, analysbindning: str | None = None, presentation=None, granskningssatt=None,
) -> tuple[Sakgranskning, ...]:
    """Returnerar sakgranskningarna med en ny post för avsnittet så som det ser ut med profilens namn."""
    if dokument.formatversion in ("D-ARB-tjanst-v8","D-ARB-resultat-v9", "D-ARB-resultat-v10") and presentation is None:
        raise SakgranskningsFel("Rapporten kräver fullständig presentation före sakgranskning.")
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
        analysbindning=analysbindning,
        granskningssatt=granskningssatt,
        kontrollsumma=granskad_summa(avsnitt, profil),
        dokumentstruktur=struktur_summa(dokument, presentation=presentation) if _har_struktur(dokument) else None,
        godkand=godkand,
        roll=roll,
        namn=namn.strip(),
        datum=datum,
        kommentar=kommentar.strip() if kommentar else None,
    )
    return (*sakgranskningar, post)


def galler_sakgranskning(
    sakgranskningar: tuple[Sakgranskning, ...], avsnitt: Avsnitt, profil: Profil, dokument: Dokument | None = None,
    *, analysbindning: str | None = None, presentation=None,
) -> Sakgranskning | None:
    """Den senaste sakgranskningen av avsnittet i exakt den lydelse som exporten skulle få."""
    if dokument and dokument.formatversion in ("D-ARB-tjanst-v8","D-ARB-resultat-v9", "D-ARB-resultat-v10") and presentation is None:
        return None
    summa = granskad_summa(avsnitt, profil)
    ny_struktur = bool(dokument and _har_struktur(dokument))
    poster = sakgranskningar
    if dokument and dokument.formatversion in ("D-ARB-tjanst-v6", "D-ARB-tjanst-v7", "D-ARB-tjanst-v8", "D-ARB-resultat-v9", "D-ARB-resultat-v10"):
        senaste = next((post for post in reversed(poster) if post.avsnitt == avsnitt.id), None)
        poster = (senaste,) if senaste is not None else ()
    giltiga = [post for post in poster if post.avsnitt == avsnitt.id and post.kontrollsumma == summa
               and (not _ar_resultatavsnitt(avsnitt) or post.granskningssatt == 'samlad_resultatrapport')
               and post.analysbindning == analysbindning
               and (post.dokumentstruktur == struktur_summa(dokument, presentation=presentation) if post.dokumentstruktur and dokument
                    else not post.dokumentstruktur and not ny_struktur)]
    return giltiga[-1] if giltiga else None


def sakgranskningsstatus(sakgranskningar: tuple[Sakgranskning, ...], avsnitt: Avsnitt, profil: Profil, dokument: Dokument | None = None, *, analysbindning: str | None = None, presentation=None) -> str:
    galler = galler_sakgranskning(sakgranskningar, avsnitt, profil, dokument, analysbindning=analysbindning, presentation=presentation)
    if galler is not None:
        utfall = "godkänt" if galler.godkand else f"underkänt ({galler.kommentar})"
        return f"{utfall} {galler.datum.isoformat()} av {galler.namn}, roll {galler.roll}"
    if any(post.avsnitt == avsnitt.id for post in sakgranskningar):
        senaste = next(post for post in reversed(sakgranskningar) if post.avsnitt == avsnitt.id)
        if _ar_resultatavsnitt(avsnitt) and senaste.granskningssatt is None:
            return 'samlad granskning kan inte styrkas; granska igen med --resultatrapport och --visad-struktursumma'
        return "ändrat efter sakgranskningen, granska igen"
    return "ej sakgranskat"
