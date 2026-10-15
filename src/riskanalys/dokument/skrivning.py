"""Skrivning av AI-avsnitt med validering och omförsök (spec 8.4). Varje försök sparas direkt."""

from collections.abc import Callable
from functools import partial
import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, ValidationError

from riskanalys.bedomning.korning import BEDOMNINGAR, kontrollera_aktuell, las_bedomning, las_bedomningsprofil
from riskanalys.dokument.delskrivning import Tjanstresultat, Delforsok, skriv_tjanst, FORMATVERSION, EFFORTSTEG
from riskanalys.dokument.leverantor import Anropsdata, Leveranssvar, LeverantorFel, Testleverantor, Textleverantor
from riskanalys.dokument.modeller import Avsnittsunderlag, AvsnittsUtkast
from riskanalys.dokument.aischema import tolka_ai_svar
from riskanalys.dokument.underlag import bygg_underlag, tjanster_med_avsnitt
from riskanalys.dokument.validering import validera_utkast
from riskanalys.lagring.yamlfil import las_modell
from riskanalys.lagring.korningar import ny_korningsmapp, senaste_korning
from riskanalys.lagring.manifest import MANIFESTNAMN, skriv_manifest
from riskanalys.profil.hantering import personnamn
from riskanalys.regelverk.modeller import Regelbas

MAX_FORSOK = 3
UTKAST = "utkast"
UNDERLAGSFIL = "underlag.json"
ALDRE_SKRIVVAG_STANGD = ("Den äldre skrivvägen skyddar inte AI-begäran och är stängd för riktiga AI-anrop. "
                         "Använd en regelbas med omfattningsmetod (spec 8.4.10 punkt 5).")


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


def kontrollera_aldre_skrivvag(leverantor: Textleverantor) -> None:
    """Den äldre skrivvägen skickar nivåer och regelspår till AI. Bara testleverantören får gå den (spec 8.4.10 punkt 5)."""
    if leverantor.namn != Testleverantor.namn:
        raise LeverantorFel(ALDRE_SKRIVVAG_STANGD)


def skriv_avsnitt(
    leverantor: Textleverantor,
    underlag: Avsnittsunderlag,
    personnamn: tuple[str, ...],
    spara: Callable[[Forsok], None] = _spara_inte,
    max_forsok: int = MAX_FORSOK,
) -> Skrivresultat:
    """Skriver ett avsnitt med omförsök. Varje försök lämnas till spara innan nästa anrop görs.
    Den äldre skrivvägen är stängd för riktiga AI-anrop och vägrar innan något anrop görs."""
    kontrollera_aldre_skrivvag(leverantor)
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
        svar = tolka_ai_svar(leverans.text, underlag.avsnitt, underlag.tillatna_id())
    except ValidationError as fel:
        return None, (
            f"Svaret följde inte schemat för AI-utkast ({fel.error_count()} fel). Svara bara med JSON enligt schemat.",
        )
    return svar, tuple(validera_utkast(svar, underlag, personnamn))


def kor_skrivning(byramapp: Path, regelbas: Regelbas, leverantor: Textleverantor, *, effort: str | None = None) -> Path:
    """Skriver ett riskavsnitt per bedömd tjänst utifrån den senaste bedömningen.

    Med omfattningsmetod skrivs varje tjänst i analysdelar med skyddad AI-begäran (skriv_tjanst). Utan
    omfattningsmetod används den äldre skrivvägen. Den skyddar inte begäran och vägras därför för riktiga
    AI-leverantörer innan något anrop görs; bara testleverantören får gå den (spec 8.4.10 punkt 5)."""
    effort = effort if effort is not None else getattr(leverantor, "effort", "high") or "high"
    if effort not in EFFORTSTEG:
        raise LeverantorFel("Ogiltig effort. Välj low, medium, high, xhigh eller max.")
    if not regelbas.metod.omfattning:
        kontrollera_aldre_skrivvag(leverantor)
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
            if regelbas.metod.omfattning:
                resultat = skriv_tjanst(leverantor, regelbas, profil, tjanst, avsnitt_id,
                    effort=effort, personnamn=namn,
                    spara=partial(_spara_delforsok, avsnittsmapp))
            else:
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
    if regelbas.metod.omfattning:
        metadata.update(dokumentformat=FORMATVERSION, format=FORMATVERSION, design="B", effort=effort)
    skriv_manifest(mapp, metadata)
    return mapp


def _spara_forsok(avsnittsmapp: Path, forsok: Forsok) -> None:
    (avsnittsmapp / f"forsok-{forsok.nummer}.json").write_text(forsok.model_dump_json(indent=2), encoding="utf-8")


def _spara_delforsok(avsnittsmapp: Path, del_id: str, forsok: Delforsok) -> None:
    (avsnittsmapp / f"{del_id}-forsok-{forsok.nummer}.json").write_text(forsok.model_dump_json(indent=2), encoding="utf-8")


def las_skrivresultat(mapp: Path) -> list[Skrivresultat | Tjanstresultat]:
    resultat = []
    for sokvag in sorted(mapp.glob("*.json")):
        if sokvag.name == MANIFESTNAMN:
            continue
        from riskanalys.fel import RiskanalysFel
        try:
            data = json.loads(sokvag.read_text(encoding="utf-8"))
            modell = Tjanstresultat if "formatversion" in data else Skrivresultat
            resultat.append(modell.model_validate(data))
        except (ValueError, OSError) as fel:
            raise RiskanalysFel(f"Skrivresultatet {sokvag} är ogiltigt. Skriv om utkastet.") from fel
    return resultat
