"""Skrivning av AI-avsnitt med validering och omförsök (spec 8.4). Varje försök sparas direkt."""

from collections.abc import Callable
from functools import partial
from pathlib import Path

from pydantic import BaseModel, ConfigDict, ValidationError

from riskanalys.bedomning.korning import BEDOMNINGAR, kontrollera_aktuell, las_bedomning, las_bedomningsprofil
from riskanalys.dokument.leverantor import Anropsdata, Leveranssvar, LeverantorFel, Textleverantor
from riskanalys.dokument.modeller import Avsnittsunderlag, AvsnittsUtkast
from riskanalys.dokument.underlag import bygg_underlag, tjanster_med_avsnitt
from riskanalys.dokument.validering import validera_utkast
from riskanalys.lagring.korningar import ny_korningsmapp, senaste_korning
from riskanalys.lagring.manifest import MANIFESTNAMN, skriv_manifest
from riskanalys.profil.hantering import personnamn
from riskanalys.regelverk.modeller import Regelbas

MAX_FORSOK = 3
UTKAST = "utkast"
UNDERLAGSFIL = "underlag.json"


class Forsok(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    nummer: int
    anrop: Anropsdata
    text: str
    svar: AvsnittsUtkast | None
    fel: tuple[str, ...]


class Skrivresultat(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    underlag: Avsnittsunderlag
    leverantor: str
    modell: str
    forsok: tuple[Forsok, ...]

    @property
    def godkant_utkast(self) -> AvsnittsUtkast | None:
        """Det sista försöket, om det klarade valideringen."""
        if not self.forsok or self.forsok[-1].fel:
            return None
        return self.forsok[-1].svar


def _spara_inte(forsok: Forsok) -> None:
    """Standard för skriv_avsnitt när anroparen inte vill spara försöken."""


def skriv_avsnitt(
    leverantor: Textleverantor,
    underlag: Avsnittsunderlag,
    personnamn: tuple[str, ...],
    spara: Callable[[Forsok], None] = _spara_inte,
    max_forsok: int = MAX_FORSOK,
) -> Skrivresultat:
    """Skriver ett avsnitt med omförsök. Varje försök lämnas till spara innan nästa anrop görs."""
    forsok: tuple[Forsok, ...] = ()
    aterkoppling: list[str] = []
    for nummer in range(1, max_forsok + 1):
        leverans = leverantor.skriv(underlag, aterkoppling)
        svar, fel = _bedom_leverans(leverans, underlag, personnamn)
        post = Forsok(nummer=nummer, anrop=leverans.anrop, text=leverans.text, svar=svar, fel=fel)
        spara(post)
        forsok = (*forsok, post)
        if leverans.avbrott is not None:
            raise LeverantorFel(f"Avsnitt {underlag.avsnitt}: {leverans.avbrott}")
        if not fel:
            break
        aterkoppling = list(fel)
    return Skrivresultat(underlag=underlag, leverantor=leverantor.namn, modell=leverantor.modell, forsok=forsok)


def _bedom_leverans(
    leverans: Leveranssvar, underlag: Avsnittsunderlag, personnamn: tuple[str, ...]
) -> tuple[AvsnittsUtkast | None, tuple[str, ...]]:
    if leverans.avbrott is not None:
        return None, (leverans.avbrott,)
    try:
        svar = AvsnittsUtkast.model_validate_json(leverans.text)
    except ValidationError as fel:
        return None, (
            f"Svaret följde inte schemat för AI-utkast ({fel.error_count()} fel). Svara bara med JSON enligt schemat.",
        )
    return svar, tuple(validera_utkast(svar, underlag, personnamn))


def kor_skrivning(byramapp: Path, regelbas: Regelbas, leverantor: Textleverantor) -> Path:
    """Skriver ett riskavsnitt per bedömd tjänst utifrån den senaste bedömningen."""
    bedomningsmapp = senaste_korning(byramapp, BEDOMNINGAR, f"bedom {byramapp.name}")
    kontrollera_aktuell(byramapp, bedomningsmapp, regelbas)
    bedomning = las_bedomning(bedomningsmapp)
    profil = las_bedomningsprofil(bedomningsmapp)
    namn = personnamn(profil, regelbas)
    mapp = ny_korningsmapp(byramapp, UTKAST)
    try:
        for avsnitt_id, tjanst in tjanster_med_avsnitt(bedomning):
            underlag = bygg_underlag(regelbas, profil, tjanst, avsnitt_id)
            avsnittsmapp = mapp / avsnitt_id
            avsnittsmapp.mkdir()
            (avsnittsmapp / UNDERLAGSFIL).write_text(underlag.model_dump_json(indent=2), encoding="utf-8")
            resultat = skriv_avsnitt(leverantor, underlag, namn, partial(_spara_forsok, avsnittsmapp))
            (mapp / f"{avsnitt_id}.json").write_text(resultat.model_dump_json(indent=2), encoding="utf-8")
    except LeverantorFel as fel:
        raise LeverantorFel(
            f"{fel} Försöken som hann göras är sparade i {mapp}. Körningen räknas inte, eftersom den avbröts."
        ) from fel
    metadata = {
        "typ": "utkast",
        "leverantor": leverantor.namn,
        "modell": leverantor.modell,
        "bedomning": bedomningsmapp.name,
    }
    skriv_manifest(mapp, metadata)
    return mapp


def _spara_forsok(avsnittsmapp: Path, forsok: Forsok) -> None:
    (avsnittsmapp / f"forsok-{forsok.nummer}.json").write_text(forsok.model_dump_json(indent=2), encoding="utf-8")


def las_skrivresultat(mapp: Path) -> list[Skrivresultat]:
    return [
        Skrivresultat.model_validate_json(sokvag.read_text(encoding="utf-8"))
        for sokvag in sorted(mapp.glob("*.json"))
        if sokvag.name != MANIFESTNAMN
    ]
