"""Bedömningskörning: sparar bedömningen med en kopia av profilen och ett manifest (spec 5.3)."""

from pathlib import Path

from riskanalys.bedomning.modeller import Bedomning
from riskanalys.bedomning.motor import bedom
from riskanalys.drift.modellidentitet import modellbindning
from riskanalys.lagring.kontrollsumma import for_fil
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.korningar import ny_korningsmapp
from riskanalys.lagring.manifest import manifestets_metadata, skriv_manifest, verifiera_manifest
from riskanalys.lagring.yamlfil import las_modell
from riskanalys.profil.hantering import kontrollera_profil
from riskanalys.profil.lagring import PROFILFIL, las_profilsnapshot
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.urval import valj

BEDOMNINGAR = "bedomningar"
BEDOMNINGSFIL = "bedomning.json"
PROFILKOPIA = "profil.yaml"


def kor_bedomning(byramapp: Path, regelbas: Regelbas) -> Path:
    profil, profilbytes = las_profilsnapshot(byramapp)
    kontrollera_profil(profil, regelbas)
    modell = modellbindning(regelbas)
    byra = profil.byra
    bedomning = bedom(regelbas, valj(regelbas, byra.regelpaket, byra.datum, byra.lan), profil)
    mapp = ny_korningsmapp(byramapp, BEDOMNINGAR)
    (mapp / PROFILKOPIA).write_bytes(profilbytes)
    (mapp / BEDOMNINGSFIL).write_text(bedomning.model_dump_json(indent=2), encoding="utf-8")
    skriv_manifest(
        mapp,
        {
            "typ": "bedomning",
            "regelpaket": bedomning.regelpaket,
            "datum": bedomning.datum.isoformat(),
            "lan": bedomning.lan,
            "regelbas_version": bedomning.regelbas_version,
            "regelbas_kontrollsumma": bedomning.regelbas_kontrollsumma,
            "modellbindning": modell,
            "status": bedomning.status,
        },
    )
    return mapp


def las_bedomning(mapp: Path) -> Bedomning:
    return las_modell(mapp / BEDOMNINGSFIL, Bedomning, json=True)


def las_bedomningsprofil(mapp: Path) -> Profil:
    return las_modell(mapp / PROFILKOPIA, Profil)


def profilen_har_andrats(byramapp: Path, bedomningsmapp: Path) -> bool:
    return for_fil(byramapp / PROFILFIL) != for_fil(bedomningsmapp / PROFILKOPIA)


def regelbasen_har_andrats(bedomningsmapp: Path, regelbas: Regelbas) -> bool:
    return manifestets_metadata(bedomningsmapp, "regelbas_kontrollsumma")["regelbas_kontrollsumma"] != regelbas.kontrollsumma


def aktualitetshinder(byramapp: Path, bedomningsmapp: Path, regelbas: Regelbas) -> list[str]:
    """Skäl att inte bygga vidare: ändrade filer, profil, regelbas eller beräkningsmodell."""
    andrade = [f"Bedömningen är ändrad efter körningen. {rad}" for rad in verifiera_manifest(bedomningsmapp)]
    regelbas_hinder = (
        ["Regelbasen har ändrats sedan bedömningen. Kör 'riskanalys bedom' igen."]
        if regelbasen_har_andrats(bedomningsmapp, regelbas)
        else []
    )
    profil_hinder = (
        ["Profilen har ändrats sedan bedömningen. Kör 'riskanalys bedom' igen."]
        if profilen_har_andrats(byramapp, bedomningsmapp)
        else []
    )
    metadata = manifestets_metadata(bedomningsmapp, "regelbas_kontrollsumma")
    modell_hinder = (
        ["Modellbindningen saknas eller riskmodellen har ändrats sedan bedömningen. Kör 'riskanalys bedom' igen."]
        if metadata.get("modellbindning") != modellbindning(regelbas)
        else []
    )
    return andrade + regelbas_hinder + profil_hinder + modell_hinder


def kontrollera_aktuell(byramapp: Path, bedomningsmapp: Path, regelbas: Regelbas) -> None:
    hinder = aktualitetshinder(byramapp, bedomningsmapp, regelbas)
    if hinder:
        raise RiskanalysFel(" ".join(hinder))
