"""Export av ett utkast till Word utifrån den senaste granskningen (spec 10)."""

from datetime import date
from pathlib import Path

from riskanalys.dokument.modeller import Oklarhet
from riskanalys.dokument.rendering import atgardslista, rendera_docx, utkaststatus
from riskanalys.dokument.skrivning import UTKAST, las_skrivresultat
from riskanalys.granskning.korning import (
    GRANSKNING,
    granskningens_metadata,
    granskningens_profil,
    kontrollera_kallor,
    las_granskning,
)
from riskanalys.lagring.korningar import ny_korningsmapp, senaste_korning
from riskanalys.lagring.manifest import skriv_manifest

EXPORT = "export"
UTKASTFIL = "allman-riskbedomning-UTKAST.docx"


def utkastens_oklarheter(byramapp: Path, utkastnamn: str) -> tuple[tuple[str, Oklarhet], ...]:
    """Oklarheterna i de godkända AI-utkast som granskningen använde."""
    if not utkastnamn:
        return ()
    return tuple(
        (post.underlag.avsnitt, oklarhet)
        for post in las_skrivresultat(byramapp / UTKAST / utkastnamn)
        if post.godkant_utkast is not None
        for oklarhet in post.godkant_utkast.oklarheter
    )


def kor_export_utkast(byramapp: Path, datum: date) -> Path:
    """Exporterar den senaste granskningens dokument som ett märkt utkast med åtgärdslista.

    Granskningen, bedömningen (profilkopian) och AI-utkasten (oklarheterna) kontrolleras mot sina manifest
    innan något läses, så att ändrade filer aldrig hamnar i exporten.
    """
    granskningsmapp = senaste_korning(byramapp, GRANSKNING, f"granska {byramapp.name}")
    kontrollera_kallor(byramapp, granskningsmapp)
    metadata = granskningens_metadata(granskningsmapp)
    profil = granskningens_profil(byramapp, granskningsmapp)
    dokument, fynd = las_granskning(granskningsmapp)
    bilaga = atgardslista(fynd, utkastens_oklarheter(byramapp, metadata["utkast"]))
    mapp = ny_korningsmapp(byramapp, EXPORT)
    rendera_docx(dokument, profil, utkaststatus(datum), mapp / UTKASTFIL, bilaga)
    skriv_manifest(mapp, {"typ": "export_utkast", "granskning": granskningsmapp.name, "datum": datum.isoformat()})
    return mapp
