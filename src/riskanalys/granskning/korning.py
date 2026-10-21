"""Granskningskörning: bygger dokumentet, granskar det och sparar resultatet med manifest."""

from contextlib import nullcontext
from datetime import date
from pathlib import Path

from pydantic import TypeAdapter

from riskanalys.bedomning.korning import BEDOMNINGAR, kontrollera_aktuell, las_bedomning, las_bedomningsprofil
from riskanalys.dokument.delskrivning import Tjanstresultat
from riskanalys.dokument.arb import bygg_arb
from riskanalys.dokument.modeller import AvsnittsUtkast, Dokument, Oklarhet
from riskanalys.dokument.skrivning import UTKAST, las_skrivresultat
from riskanalys.drift.historik import historikens_kontrollsumma, las_historik
from riskanalys.fel import RiskanalysFel
from riskanalys.granskning.kontroller import granska
from riskanalys.granskning.modeller import Fynd
from riskanalys.lagring.yamlfil import las_modell
from riskanalys.lagring.korningar import avslutade_korningar, ny_korningsmapp, senaste_korning
from riskanalys.lagring.kontrollsumma import for_fil
from riskanalys.lagring.manifest import MANIFESTNAMN, las_manifest, manifestets_metadata, skriv_manifest, verifiera_manifest
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.urval import valj

GRANSKNING = "granskning"
DOKUMENTFIL = "dokument.json"
FYNDFIL = "fynd.json"
# Uppgifter i granskningens manifest som senare steg läser.
GRANSKNINGENS_NYCKLAR = ("bedomning", "utkast", "historik", "datum")
_FYNDLISTA = TypeAdapter(tuple[Fynd, ...])


def godkanda_utkast(byramapp: Path, bedomningsmapp: Path, *, utkastmapp: Path | None = None) -> tuple[dict[str, AvsnittsUtkast], Path | None]:
    """Godkända AI-utkast från den senaste skrivningen som hör till just den här bedömningen."""
    rot = byramapp / UTKAST
    if rot.is_dir():
        from riskanalys.lagring.manifest import MANIFESTNAMN
        for m in rot.iterdir():
            if m.is_dir() and not (m / MANIFESTNAMN).is_file():
                raise RiskanalysFel(f"Manifest saknas i {m}. Återställ körningen; relevansen kan inte avgöras.")
    horande = [
        mapp
        for mapp in avslutade_korningar(byramapp, UTKAST)
        if las_manifest(mapp).metadata.get("bedomning") == bedomningsmapp.name
    ]
    if utkastmapp is not None:
        if utkastmapp not in horande:
            raise RiskanalysFel("Det valda AI-utkastet hör inte till bedömningen. Skapa ett nytt utkast.")
        mapp = utkastmapp
    elif horande:
        mapp = horande[-1]
    else:
        return {}, None
    fel = verifiera_manifest(mapp)
    if fel:raise RiskanalysFel(f"Utkastet {mapp} är ändrat. Återställ eller kör skriv igen: {'; '.join(fel)}")
    utkast = {}
    for post in las_skrivresultat(mapp):
        if isinstance(post,Tjanstresultat):
            utkast[post.avsnitt] = post
        elif post.godkant_utkast is not None:
            utkast[post.underlag.avsnitt] = post.godkant_utkast
    return utkast, mapp


def oppna_fragor(utkast: dict[str, AvsnittsUtkast]) -> tuple[tuple[str, Oklarhet], ...]:
    """AI-utkastens öppna frågor (oklarheter) per avsnitt, i avsnittens ordning."""
    fragor=[]
    for id,post in utkast.items():
        if isinstance(post,Tjanstresultat):
            fragor.extend((id,Oklarhet(fraga=o.fraga,saknad_uppgift=o.uppgift_id))
                for d in post.delar if d.godkant_svar for o in d.godkant_svar.oklarheter)
        else:
            fragor.extend((id,o) for o in post.oklarheter)
    return tuple(fragor)


def kor_granskning(byramapp: Path, regelbas: Regelbas, granskningsdatum: date, *, bedomningsmapp: Path | None = None, utkastmapp: Path | None = None) -> Path:
    from riskanalys.analys.lagring import analyslas
    # Som fastställelsen: bara omfattningsmetoden läser det lokala analysregistret.
    with analyslas(byramapp) if regelbas.metod.omfattning else nullcontext():
        return _kor_granskning_last(byramapp,regelbas,granskningsdatum,bedomningsmapp=bedomningsmapp,utkastmapp=utkastmapp)


def _kor_granskning_last(byramapp: Path, regelbas: Regelbas, granskningsdatum: date, *, bedomningsmapp: Path | None = None, utkastmapp: Path | None = None) -> Path:
    bedomningsmapp = bedomningsmapp or senaste_korning(byramapp, BEDOMNINGAR, f"bedom {byramapp.name}")
    kontrollera_aktuell(byramapp, bedomningsmapp, regelbas)
    bedomning = las_bedomning(bedomningsmapp)
    profil = las_bedomningsprofil(bedomningsmapp)
    urval = valj(regelbas, bedomning.regelpaket, bedomning.datum, bedomning.lan)
    utkast, utkastmapp = godkanda_utkast(byramapp, bedomningsmapp, utkastmapp=utkastmapp)
    historik = las_historik(byramapp)
    snapshot = None
    rapport = None
    if regelbas.metod.omfattning:
        from riskanalys.analys.lagring import las_analyssnapshot_last, Analyssnapshot
        from riskanalys.granskning.analysunderlag import fryst_modellrapport
        from riskanalys.dokument.arb_v6 import bygg_arb_v6
        snapshot = (las_analyssnapshot_last(byramapp,regelbas,granskningsdatum,bedomningsmapp=bedomningsmapp,utkastmapp=utkastmapp)
                    if utkastmapp else Analyssnapshot(None,'',('Skrivresultat och lokal analys saknas.',),()))
        rapport = fryst_modellrapport(snapshot)
        dokument = bygg_arb(regelbas,profil,bedomning,utkast,historik,analys=snapshot.paket,modellrapport=rapport)
    else:
        dokument = bygg_arb(regelbas, profil, bedomning, utkast, historik)
    fynd = granska(regelbas, urval, profil, bedomning, dokument, historik, granskningsdatum, oppna_fragor(utkast), skrivresultat=utkast, analys=snapshot.paket if snapshot else None, modellrapport=rapport, analysbrister_filer=snapshot.brister if snapshot else ())
    mapp = ny_korningsmapp(byramapp, GRANSKNING)
    (mapp / DOKUMENTFIL).write_text(dokument.model_dump_json(indent=2), encoding="utf-8")
    (mapp / FYNDFIL).write_text(_FYNDLISTA.dump_json(fynd, indent=2).decode("utf-8"), encoding="utf-8")
    metadata = {
        "typ": "granskning",
        "dokumentformat": dokument.formatversion,
        "bedomning": bedomningsmapp.name,
        "utkast": utkastmapp.name if utkastmapp else "",
        # Analysbindning version 2 binder inte utkastet; granskningen binder därför det använda utkastet själv.
        "utkastmanifest": for_fil(utkastmapp / MANIFESTNAMN) if utkastmapp else "",
        "historik": historikens_kontrollsumma(byramapp),
        "blockerande": str(sum(1 for post in fynd if post.allvar == "blockerande")),
        "datum": granskningsdatum.isoformat(),
    }
    if snapshot is not None:
        from riskanalys.granskning.analysunderlag import spara_fryst_analys
        spara_fryst_analys(mapp,snapshot)
        (mapp / "historik.json").write_text(historik.model_dump_json(indent=2), encoding="utf-8")
        metadata['analysbindning'] = snapshot.registersumma
    if dokument.formatversion == 'D-ARB-tjanst-v8':
        from riskanalys.dokument.presentation_v8 import bygg_presentation
        from riskanalys.dokument.rapportpaket_v8 import PRESENTATIONSFIL
        presentation = bygg_presentation(dokument, analys=snapshot.paket if snapshot else None, fynd=fynd, bedomning=bedomning, profil=profil)
        (mapp/PRESENTATIONSFIL).write_text(presentation.model_dump_json(indent=2), encoding='utf-8')
    skriv_manifest(mapp, metadata)
    return mapp


def las_granskning(mapp: Path) -> tuple[Dokument, tuple[Fynd, ...]]:
    dokument = las_modell(mapp / DOKUMENTFIL, Dokument, json=True)
    fynd = las_modell(mapp / FYNDFIL, _FYNDLISTA, json=True)
    return dokument, fynd


def granskningens_metadata(granskningsmapp: Path) -> dict[str, str]:
    """Granskningens metadata. Saknas en uppgift som export, sakgranskning eller fastställelse behöver ges ett fel
    med instruktion om återställning i stället för en krasch."""
    return manifestets_metadata(granskningsmapp, *GRANSKNINGENS_NYCKLAR)


def granskningens_bedomningsmapp(byramapp: Path, granskningsmapp: Path) -> Path:
    """Mappen med den bedömning som granskningen bygger på."""
    return byramapp / BEDOMNINGAR / granskningens_metadata(granskningsmapp)["bedomning"]


def granskningens_profil(byramapp: Path, granskningsmapp: Path) -> Profil:
    """Profilkopian i den bedömning som granskningen bygger på. Den gäller för sakgranskning, export och fastställelse."""
    return las_bedomningsprofil(granskningens_bedomningsmapp(byramapp, granskningsmapp))


def andrade_kallor(byramapp: Path, granskningsmapp: Path) -> list[str]:
    """Filer som ändrats efter körningen i granskningen, i bedömningen den bygger på och i AI-utkasten den använde."""
    granskning = [f"Granskningen är ändrad efter körningen. {rad}" for rad in verifiera_manifest(granskningsmapp)]
    if granskning:
        return granskning
    metadata = granskningens_metadata(granskningsmapp)
    bedomning = [
        f"Bedömningen är ändrad efter körningen. {rad}"
        for rad in verifiera_manifest(byramapp / BEDOMNINGAR / metadata["bedomning"])
    ]
    utkast = [
        f"AI-utkasten är ändrade efter skrivningen. {rad}"
        for rad in (verifiera_manifest(byramapp / UTKAST / metadata["utkast"]) if metadata["utkast"] else [])
    ]
    # Äldre granskningar saknar nyckeln; deras analysbindning version 1 binder utkastet.
    bundet = las_manifest(granskningsmapp).metadata.get("utkastmanifest")
    if bundet and not utkast and for_fil(byramapp / UTKAST / metadata["utkast"] / MANIFESTNAMN) != bundet:
        utkast.append("AI-utkastens manifest har ändrats efter granskningen.")
    return [*bedomning, *utkast]


def kontrollera_kallor(byramapp: Path, granskningsmapp: Path) -> None:
    """Stoppar med ett svenskt meddelande om granskningen eller något den bygger på har ändrats."""
    hinder = andrade_kallor(byramapp, granskningsmapp)
    if hinder:
        raise RiskanalysFel(" ".join(hinder) + " Kör om kedjan från 'riskanalys bedom'.")
