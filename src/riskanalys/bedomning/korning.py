"""Bedömningskörning: sparar bedömningen med en kopia av profilen och ett manifest (spec 5.3)."""

import shutil
from pathlib import Path

from riskanalys.bedomning.modeller import Bedomning
from riskanalys.bedomning.motor import bedom
from riskanalys.lagring.kontrollsumma import for_fil
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.korningar import ny_korningsmapp
from riskanalys.lagring.manifest import manifestets_metadata, skriv_manifest, verifiera_manifest
from riskanalys.lagring.yamlfil import las_yaml
from riskanalys.profil.hantering import kontrollera_profil
from riskanalys.profil.lagring import PROFILFIL, las_profil
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.urval import valj

BEDOMNINGAR = "bedomningar"
BEDOMNINGSFIL = "bedomning.json"
PROFILKOPIA = "profil.yaml"


def kor_bedomning(byramapp: Path, regelbas: Regelbas) -> Path:
    profil = las_profil(byramapp)
    kontrollera_profil(profil, regelbas)
    byra = profil.byra
    bedomning = bedom(regelbas, valj(regelbas, byra.regelpaket, byra.datum, byra.lan), profil)
    mapp = ny_korningsmapp(byramapp, BEDOMNINGAR)
    shutil.copyfile(byramapp / PROFILFIL, mapp / PROFILKOPIA)
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
            "status": bedomning.status,
        },
    )
    return mapp


def las_bedomning(mapp: Path) -> Bedomning:
    return Bedomning.model_validate_json((mapp / BEDOMNINGSFIL).read_text(encoding="utf-8"))


def las_bedomningsprofil(mapp: Path) -> Profil:
    return Profil.model_validate(las_yaml(mapp / PROFILKOPIA))


def profilen_har_andrats(byramapp: Path, bedomningsmapp: Path) -> bool:
    return for_fil(byramapp / PROFILFIL) != for_fil(bedomningsmapp / PROFILKOPIA)


def regelbasen_har_andrats(bedomningsmapp: Path, regelbas: Regelbas) -> bool:
    return manifestets_metadata(bedomningsmapp, "regelbas_kontrollsumma")["regelbas_kontrollsumma"] != regelbas.kontrollsumma


def aktualitetshinder(byramapp: Path, bedomningsmapp: Path, regelbas: Regelbas) -> list[str]:
    """Skäl att inte bygga vidare på bedömningen: ändrade filer, ändrad regelbas eller ändrad profil."""
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
    return andrade + regelbas_hinder + profil_hinder


def kontrollera_aktuell(byramapp: Path, bedomningsmapp: Path, regelbas: Regelbas) -> None:
    hinder = aktualitetshinder(byramapp, bedomningsmapp, regelbas)
    if hinder:
        raise RiskanalysFel(" ".join(hinder))
