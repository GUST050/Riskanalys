"""Fastställelse: kontroll av kedjan och grindarna, låst paket och verifiering (spec 5.3 och 10).

Publiceringen är ett enda namnbyte. Allt, också versionshistoriken med det nya beslutet, skrivs i en
arbetsmapp som byter namn till v{n} när den är klar. Efter namnbytet skrivs ingenting mer, så en
fastställelse är antingen helt gjord eller inte gjord alls. Därför läses fastställelserna ur de låsta
paketen och inte ur byråns historikfil.
"""

import re
import shutil
from datetime import date
from pathlib import Path

from riskanalys.bedomning.korning import BEDOMNINGAR, aktualitetshinder, las_bedomning, las_bedomningsprofil
from riskanalys.dokument.skrivversion import AKTUELL_DOKUMENTVERSION as FORMATVERSION
from riskanalys.dokument.modeller import Avsnitt, Dokument
from riskanalys.dokument.rendering import faststalld_status, rendera_docx
from riskanalys.dokument.skrivning import UTKAST
from riskanalys.drift.historik import Handelse, Historik, historikens_kontrollsumma, las_historik, spara_historik
from riskanalys.faststallelse.grindar import FASTSTALLELSE, Faststallelseunderlag, hinder_for_faststallelse
from riskanalys.faststallelse.modeller import Beslut
from riskanalys.faststallelse.sakgranskning import las_sakgranskningar, spara_sakgranskningar
from riskanalys.fel import RiskanalysFel
from riskanalys.granskning.korning import GRANSKNING, andrade_kallor, granskningens_metadata, las_granskning
from riskanalys.lagring.korningar import senaste_korning
from riskanalys.lagring.manifest import MANIFESTNAMN, las_manifest, skriv_manifest, verifiera_manifest
from riskanalys.lagring.kontrollsumma import for_fil
from riskanalys.lagring.yamlfil import las_yaml, spara_yaml
from riskanalys.regelverk.laddning import regelbasens_kontrollsumma
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.urval import valj

FASTSTALLDA = "faststallda"
BESLUTSFIL = "beslut.yaml"
_VERSION = re.compile(r"^v(\d+)$")
_IGNORERA = shutil.ignore_patterns("__pycache__", ".DS_Store", "utkast", ".granskning-*")


class FaststallelseFel(RiskanalysFel):
    """Villkoren för fastställelse är inte uppfyllda. hinder räknar upp vad som saknas."""

    def __init__(self, hinder: list[str]) -> None:
        super().__init__("Kan inte fastställa:\n" + "\n".join(f"- {rad}" for rad in hinder))
        self.hinder = hinder


def paketfil(version: int) -> str:
    return f"allman-riskbedomning-v{version}.docx"


def faststallda_versioner(byramapp: Path) -> tuple[tuple[int, Path], ...]:
    """Publicerade versioner i nummerordning. En arbetsmapp som aldrig bytte namn räknas inte."""
    rot = byramapp / FASTSTALLDA
    if not rot.is_dir():
        return ()
    versioner = [
        (int(traff.group(1)), mapp) for mapp in rot.iterdir() if mapp.is_dir() and (traff := _VERSION.match(mapp.name))
    ]
    return tuple(sorted(versioner))


def nasta_version(byramapp: Path) -> int:
    return max((version for version, _ in faststallda_versioner(byramapp)), default=0) + 1


def skadade_versioner(byramapp: Path) -> list[str]:
    """Tidigare versioner som inte stämmer med sitt manifest. Inget får läsas ur dem förrän de återställts."""
    return [
        f"Version {version} stämmer inte med sitt manifest: {rad} Återställ paketet från säkerhetskopian."
        for version, mapp in faststallda_versioner(byramapp)
        for rad in verifiera_manifest(mapp)
    ]


def versionshistorik(byramapp: Path) -> Historik:
    """Byråns registrerade utvärderingar och uppdateringar samt varje fastställd version, ur de låsta paketen.

    Paketen kontrolleras mot sina manifest först. Ett ändrat eller ofullständigt paket stoppar med ett fel.
    """
    skadade = skadade_versioner(byramapp)
    if skadade:
        raise RiskanalysFel(" ".join(skadade))
    historik = las_historik(byramapp)
    for version, mapp in faststallda_versioner(byramapp):
        historik = historik.med(_faststallelse(Beslut.model_validate(las_yaml(mapp / BESLUTSFIL)), version))
    return historik


def kedjehinder(byramapp: Path, regelbas_rot: Path, regelbas: Regelbas, granskningsmapp: Path) -> list[str]:
    """Skäl att inte lita på att tidigare versioner, granskningen, bedömningen, utkasten och regelbasen hör ihop."""
    skadade = skadade_versioner(byramapp)
    if skadade:
        return skadade
    andrade = andrade_kallor(byramapp, granskningsmapp)
    if andrade:
        return andrade
    metadata = granskningens_metadata(granskningsmapp)
    senaste = senaste_korning(byramapp, BEDOMNINGAR, f"bedom {byramapp.name}")
    if metadata["bedomning"] != senaste.name:
        return ["Granskningen hör inte till den senaste bedömningen. Kör 'riskanalys granska' igen."]
    redan = [
        f"Granskningen {granskningsmapp.name} är redan fastställd som version {version}. "
        "Gör en ny granskning för en ny version."
        for version, mapp in faststallda_versioner(byramapp)
        if las_manifest(mapp).metadata.get("granskning") == granskningsmapp.name
    ]
    historik = (
        ["Versionshistoriken har ändrats sedan granskningen. Kör 'riskanalys granska' igen."]
        if historikens_kontrollsumma(byramapp) != metadata["historik"]
        else []
    )
    regelbas_hinder = (
        [f"Regelbasen i {regelbas_rot} stämmer inte med den inlästa regelbasen."]
        if regelbasens_kontrollsumma(regelbas_rot) != regelbas.kontrollsumma
        else []
    )
    return [
        *aktualitetshinder(byramapp, senaste, regelbas),
        *redan,
        *historik,
        *regelbas_hinder,
        *formathinder(regelbas, las_granskning(granskningsmapp)[0]),
    ]


def _formatbeskrivning(avsnitt: Avsnitt) -> str:
    return f"har formatet {avsnitt.formatversion}" if avsnitt.formatversion else "saknar formatmarkering"


def formathinder(regelbas: Regelbas, dokument: Dokument) -> list[str]:
    """Varje tjänsteavsnitt ska ha aktuellt format före ny fastställelse; äldre paket läses som förut (spec 8.4.9 punkt 9)."""
    if not regelbas.metod.omfattning:
        return []
    return [
        f"Tjänsteavsnittet {a.id} {_formatbeskrivning(a)}, men aktuellt format är "
        f"{FORMATVERSION}. Skriv om utkastet och granska på nytt."
        for a in dokument.avsnitt
        if a.id.startswith("D-ARB.6.") and a.formatversion != FORMATVERSION
    ]


def faststall(byramapp: Path, regelbas_rot: Path, regelbas: Regelbas, beslut: Beslut) -> Path:
    from riskanalys.analys.lagring import analyslas
    from contextlib import nullcontext
    with analyslas(byramapp) if regelbas.metod.omfattning else nullcontext():
        return _faststall_last(byramapp,regelbas_rot,regelbas,beslut)


def _faststall_last(byramapp: Path, regelbas_rot: Path, regelbas: Regelbas, beslut: Beslut) -> Path:
    """Fastställer den senaste granskningen och publicerar den som en ny, låst version."""
    granskningsmapp = senaste_korning(byramapp, GRANSKNING, f"granska {byramapp.name}")
    hinder = kedjehinder(byramapp, regelbas_rot, regelbas, granskningsmapp)
    if hinder:
        raise FaststallelseFel(hinder)
    metadata = granskningens_metadata(granskningsmapp)
    kallor = {'bedomning': byramapp / BEDOMNINGAR / metadata['bedomning'], 'granskning': granskningsmapp}
    if metadata['utkast']:
        kallor['utkast'] = byramapp / UTKAST / metadata['utkast']
    kallsummor = {namn: for_fil(kalla/MANIFESTNAMN) for namn,kalla in kallor.items()}
    if regelbas.metod.omfattning:
        from riskanalys.granskning.analysunderlag import aktuell_analys_hinder
        hinder = aktuell_analys_hinder(byramapp,regelbas,granskningsmapp,beslut.datum)
        if hinder:raise FaststallelseFel(list(hinder))
    underlag = _underlag(byramapp, regelbas, granskningsmapp)
    hinder = hinder_for_faststallelse(underlag, beslut.datum)
    if hinder:
        raise FaststallelseFel(hinder)
    version = nasta_version(byramapp)
    pagaende = _tom_arbetsmapp(byramapp, version)
    _bygg_paket(pagaende, byramapp, regelbas_rot, granskningsmapp, underlag, beslut, version)
    for namn,kalla in kallor.items():
        if for_fil(pagaende/namn/MANIFESTNAMN)!=kallsummor[namn]:
            raise FaststallelseFel([f'Kopian av {namn} motsvarar inte det granskade källmanifestet.'])
    # Kontrollera även efter rendering: paketmanifestet får inte legitimera en
    # kopia som ändrats efter den första kontrollen.
    for namn in ('bedomning','granskning',*(['utkast'] if granskningens_metadata(granskningsmapp)['utkast'] else [])):
        fel = verifiera_manifest(pagaende/namn)
        if fel:raise FaststallelseFel([f'Kopian av {namn} har ändrats: {rad}' for rad in fel])
    if regelbasens_kontrollsumma(pagaende/'regelbas')!=regelbas.kontrollsumma:
        raise FaststallelseFel(['Den kopierade regelbasen har ändrats.'])
    if underlag.analys is not None:
        from riskanalys.granskning.analysunderlag import las_fryst_analys
        kopia = las_fryst_analys(pagaende)
        if kopia.paket != underlag.analys:
            raise FaststallelseFel(['Den kopierade analysen avviker från det granskade underlaget.'])
    skriv_manifest(pagaende, _metadata(underlag, beslut, version, granskningsmapp))
    # Kontrollera källor och faktisk kopia sist, under samma profil→analys→drift-lås.
    hinder = kedjehinder(byramapp,regelbas_rot,regelbas,granskningsmapp)
    if regelbas.metod.omfattning:
        hinder.extend(aktuell_analys_hinder(byramapp,regelbas,granskningsmapp,beslut.datum))
    for namn,kalla in kallor.items():
        if for_fil(kalla/MANIFESTNAMN)!=kallsummor[namn]:
            hinder.append(f'Källmanifestet för {namn} har ändrats under paketeringen.')
    if hinder:raise FaststallelseFel(hinder)
    fel = verifiera_manifest(pagaende)
    if fel:raise FaststallelseFel([f'Paketet har ändrats före publicering: {rad}' for rad in fel])
    return _publicera(pagaende, byramapp / FASTSTALLDA / f"v{version}")


def verifiera_version(byramapp: Path, version: int) -> list[str]:
    """Jämför ett fastställt paket med dess manifest. Tom lista betyder att paketet är oförändrat."""
    mapp = byramapp / FASTSTALLDA / f"v{version}"
    if not mapp.is_dir():
        raise RiskanalysFel(f"Version {version} finns inte i {byramapp / FASTSTALLDA}.")
    return verifiera_manifest(mapp)


def _faststallelse(beslut: Beslut, version: int) -> Handelse:
    return Handelse(
        datum=beslut.datum,
        typ=FASTSTALLELSE,
        beskrivning=f"Version {version} fastställd av {beslut.organ}.",
        version=version,
    )


def _underlag(byramapp: Path, regelbas: Regelbas, granskningsmapp: Path) -> Faststallelseunderlag:
    metadata = granskningens_metadata(granskningsmapp)
    bedomningsmapp = byramapp / BEDOMNINGAR / metadata["bedomning"]
    bedomning = las_bedomning(bedomningsmapp)
    dokument, fynd = las_granskning(granskningsmapp)
    snapshot = None
    if regelbas.metod.omfattning:
        from riskanalys.granskning.analysunderlag import las_fryst_analys
        snapshot = las_fryst_analys(granskningsmapp)
    return Faststallelseunderlag(
        analys=snapshot.paket if snapshot else None,
        analysbindning=snapshot.registersumma if snapshot else None,
        regelbas=regelbas,
        urval=valj(regelbas, bedomning.regelpaket, bedomning.datum, bedomning.lan),
        profil=las_bedomningsprofil(bedomningsmapp),
        bedomning=bedomning,
        dokument=dokument,
        fynd=fynd,
        sakgranskningar=las_sakgranskningar(byramapp),
        historik=versionshistorik(byramapp),
        granskningsdatum=date.fromisoformat(metadata["datum"]),
    )


def _tom_arbetsmapp(byramapp: Path, version: int) -> Path:
    """En tom mapp att bygga paketet i. Rester av ett avbrutet försök är kopior och tas bort."""
    pagaende = byramapp / FASTSTALLDA / f".v{version}-pagaende"
    if pagaende.exists():
        shutil.rmtree(pagaende)
    pagaende.mkdir(parents=True)
    return pagaende


def _bygg_paket(
    pagaende: Path,
    byramapp: Path,
    regelbas_rot: Path,
    granskningsmapp: Path,
    underlag: Faststallelseunderlag,
    beslut: Beslut,
    version: int,
) -> None:
    """Kopierar underlaget till arbetsmappen och skriver beslut, versionshistorik och Word-fil där."""
    metadata = granskningens_metadata(granskningsmapp)
    shutil.copytree(byramapp / BEDOMNINGAR / metadata["bedomning"], pagaende / "bedomning")
    shutil.copytree(granskningsmapp, pagaende / "granskning")
    if metadata["utkast"]:
        shutil.copytree(byramapp / UTKAST / metadata["utkast"], pagaende / "utkast")
    shutil.copytree(regelbas_rot, pagaende / "regelbas", ignore=_IGNORERA)
    # Varje kopierad källa måste fortfarande stämma med sitt sparade manifest.
    for namn in ('bedomning','granskning',*(['utkast'] if metadata['utkast'] else [])):
        fel=verifiera_manifest(pagaende/namn)
        if fel:raise FaststallelseFel([f'Kopian av {namn} har ändrats: {rad}' for rad in fel])
    if regelbasens_kontrollsumma(pagaende/'regelbas')!=underlag.regelbas.kontrollsumma:
        raise FaststallelseFel(['Den kopierade regelbasen har ändrats. Granska igen.'])
    if underlag.analys is not None:
        from riskanalys.granskning.analysunderlag import las_fryst_analys,spara_fryst_analys
        snapshot=las_fryst_analys(pagaende/'granskning')
        if snapshot.registersumma!=underlag.analysbindning:
            raise FaststallelseFel(['Den kopierade analysen avviker från det granskade underlaget.'])
        spara_fryst_analys(pagaende,snapshot)
    spara_sakgranskningar(pagaende, underlag.sakgranskningar)
    spara_historik(pagaende, underlag.historik.med(_faststallelse(beslut, version)))
    spara_yaml(pagaende / BESLUTSFIL, beslut.model_dump(mode="python"))
    statusrad = faststalld_status(beslut.organ, beslut.datum, version)
    rendera_docx(underlag.dokument, underlag.profil, statusrad, pagaende / paketfil(version))


def _metadata(underlag: Faststallelseunderlag, beslut: Beslut, version: int, granskningsmapp: Path) -> dict[str, str]:
    return {
        **({"analysbindning": underlag.analysbindning} if underlag.analysbindning is not None else {}),
        "typ": "faststallt_paket",
        "dokumentformat": underlag.dokument.formatversion,
        "version": str(version),
        "organ": beslut.organ,
        "beslutsdatum": beslut.datum.isoformat(),
        "regelpaket": underlag.bedomning.regelpaket,
        "datum": underlag.bedomning.datum.isoformat(),
        "lan": underlag.bedomning.lan,
        "regelbas_version": underlag.regelbas.version,
        "regelbas_kontrollsumma": underlag.regelbas.kontrollsumma,
        "granskning": granskningsmapp.name,
    }


def _publicera(pagaende: Path, slutlig: Path) -> Path:
    """Det enda steget som gör versionen synlig. Ett namnbyte inom samma mapp sker helt eller inte alls."""
    pagaende.rename(slutlig)
    return slutlig
