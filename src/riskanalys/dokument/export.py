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
    from riskanalys.dokument.delskrivning import Tjanstresultat
    from riskanalys.granskning.korning import oppna_fragor
    utkast={}
    for post in las_skrivresultat(byramapp / UTKAST / utkastnamn):
        if isinstance(post,Tjanstresultat):
            utkast[post.avsnitt]=post
        elif post.godkant_utkast:
            utkast[post.underlag.avsnitt]=post.godkant_utkast
    return oppna_fragor(utkast)


def kor_export_utkast(byramapp: Path, datum: date, *, granskningsmapp: Path | None = None, regelbas=None) -> Path:
    """Exporterar den senaste granskningens dokument som ett märkt utkast med åtgärdslista.

    Granskningen, bedömningen (profilkopian) och AI-utkasten (oklarheterna) kontrolleras mot sina manifest
    innan något läses, så att ändrade filer aldrig hamnar i exporten.
    """
    granskningsmapp = granskningsmapp or senaste_korning(byramapp, GRANSKNING, f"granska {byramapp.name}")
    kontrollera_kallor(byramapp, granskningsmapp)
    metadata = granskningens_metadata(granskningsmapp)
    profil = granskningens_profil(byramapp, granskningsmapp)
    dokument, fynd = las_granskning(granskningsmapp)
    if dokument.formatversion in ('D-ARB-tjanst-v8','D-ARB-resultat-v9'):
        from riskanalys.analys.lagring import analyslas
        with analyslas(byramapp):
            exportor=exportera_v9_last if dokument.formatversion=='D-ARB-resultat-v9' else exportera_v8_last
            return exportor(byramapp, datum, granskningsmapp, regelbas=regelbas)
    bilaga = atgardslista(fynd, utkastens_oklarheter(byramapp, metadata["utkast"]), formatversion=dokument.formatversion)
    mapp = ny_korningsmapp(byramapp, EXPORT)
    rendera_docx(dokument, profil, utkaststatus(datum), mapp / UTKASTFIL, bilaga)
    from riskanalys.dokument.matning import dokumentord
    skriv_manifest(mapp, {**{f"ord_{k}": str(v) for k,v in dokumentord(dokument, profil).items()}, "typ": "export_utkast", "granskning": granskningsmapp.name,
                         "dokumentformat": dokument.formatversion, "datum": datum.isoformat()})
    return mapp


def exportera_v8_last(byramapp: Path, datum: date, granskningsmapp: Path, *, regelbas=None) -> Path:
    return _exportera_bundet_last(byramapp,datum,granskningsmapp,regelbas=regelbas,v9=False)


def exportera_v9_last(byramapp: Path, datum: date, granskningsmapp: Path, *, regelbas=None) -> Path:
    return _exportera_bundet_last(byramapp,datum,granskningsmapp,regelbas=regelbas,v9=True)


def _exportera_bundet_last(byramapp: Path, datum: date, granskningsmapp: Path, *, regelbas=None,v9=False) -> Path:
    """Anroparen håller profil→analys→drift; båda dokument publiceras med ett namnbyte."""
    import shutil
    from datetime import datetime, timezone
    from tempfile import TemporaryDirectory
    from riskanalys.analys.lagring import las_analys
    from riskanalys.bedomning.korning import BEDOMNINGAR, las_bedomning
    from riskanalys.dokument.rapportpaket_v8 import Leverans, LEVERANSFIL, las_presentation
    from riskanalys.dokument.rapportvyer import bygg_rapportvyer
    from riskanalys.dokument.rendering import rendera_rapportvyer
    from riskanalys.granskning.analysunderlag import las_fryst_analys, registerhinder
    from riskanalys.lagring.kontrollsumma import for_fil
    from riskanalys.lagring.manifest import MANIFESTNAMN, verifiera_manifest
    from riskanalys.fel import RiskanalysFel
    kontrollera_kallor(byramapp, granskningsmapp)
    metadata = granskningens_metadata(granskningsmapp)
    bedomningsmapp = byramapp / BEDOMNINGAR / metadata['bedomning']
    bedomning = las_bedomning(bedomningsmapp)
    dokument, fynd = las_granskning(granskningsmapp)
    snapshot = las_fryst_analys(granskningsmapp)
    if snapshot.paket is not None or las_analys(byramapp) is not None:
        hinder = registerhinder(byramapp, snapshot)
        if hinder:
            raise RiskanalysFel(' '.join(hinder))
    profil = granskningens_profil(byramapp, granskningsmapp)
    if v9:
        from riskanalys.dokument.rapportpaket_v9 import las_presentation_v9 as las_presentation
        from riskanalys.dokument.leverans_v9 import LeveransV9 as Leverans
    presentation = las_presentation(granskningsmapp, bedomning, profil, regelbas=regelbas)
    leverans = Leverans(datum=datum, bedomning=bedomningsmapp.name, granskning=granskningsmapp.name)
    kallor: dict[str, Path] = {'granskning': granskningsmapp, 'bedomning': bedomningsmapp}
    summor = {namn: for_fil(kalla / MANIFESTNAMN) for namn, kalla in kallor.items()}
    # Arbetsmappen ligger utanför körningskatalogen; avbrutna exporter blir aldrig senaste körning.
    with TemporaryDirectory(prefix='.export-v8-', dir=byramapp) as tmp:
        arbetsmapp = Path(tmp) / 'paket'
        arbetsmapp.mkdir()
        for namn, kalla in kallor.items():
            shutil.copytree(kalla, arbetsmapp / namn)
        if v9:
            from riskanalys.dokument.rapportvyer_v9 import bygg_rapportvyer_v9
            from riskanalys.dokument.rendering_v9 import rendera_rapportvyer_v9
            rendera_rapportvyer_v9(bygg_rapportvyer_v9(dokument),profil,arbetsmapp,presentation=presentation,leverans=leverans)
        else:
            rendera_rapportvyer(
                bygg_rapportvyer(dokument), profil, leverans.statusrad, arbetsmapp,
                analys=snapshot.paket, fynd=fynd, bedomning=bedomning,
                presentation=presentation, leverans=leverans,
            )
        (arbetsmapp / LEVERANSFIL).write_text(leverans.model_dump_json(indent=2), encoding='utf-8')
        kontrollera_kallor(byramapp, granskningsmapp)
        if snapshot.paket is not None or las_analys(byramapp) is not None:
            hinder = registerhinder(byramapp, snapshot)
            if hinder:
                raise RiskanalysFel(' '.join(hinder))
        for namn, kalla in kallor.items():
            if (for_fil(kalla / MANIFESTNAMN) != summor[namn]
                    or for_fil(arbetsmapp / namn / MANIFESTNAMN) != summor[namn]
                    or verifiera_manifest(arbetsmapp / namn)):
                raise RiskanalysFel('Exportens frysta källa ändrades under rendering. Granska och exportera igen.')
        skriv_manifest(arbetsmapp, {
            'typ': 'export_utkast', 'granskning': granskningsmapp.name,
            'dokumentformat': dokument.formatversion, 'datum': datum.isoformat(),
            'analysbindning': snapshot.registersumma,
        })
        fel = verifiera_manifest(arbetsmapp)
        if fel:
            raise RiskanalysFel(' '.join(fel))
        rot = byramapp / EXPORT
        rot.mkdir(exist_ok=True)
        slutlig = rot / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f') + 'Z')
        arbetsmapp.rename(slutlig)
        return slutlig
