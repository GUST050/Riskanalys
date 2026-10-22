"""Syntetisk schema-2-fixtur; gamla rapportläsprov ändras inte."""
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from riskanalys.analys.modeller import Analyspaket
from riskanalys.analys.gemensam import forifyll_gemensamt
from riskanalys.bedomning.modeller import Bedomning
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas
from tester.fixturer.rapportlasprov import bygg_rapportlasprov

@dataclass(frozen=True)
class GemensamtFall:
    rb: Regelbas
    profil: Profil
    bedomning: Bedomning
    paket: Analyspaket
    datum: date

def bygg_gemensamt_fall(rb: Regelbas, rot: Path, fall: str='fyra_tjanster') -> GemensamtFall:
    f=bygg_rapportlasprov(rb,rot,fall)
    return GemensamtFall(rb,f.profil,f.bedomning,forifyll_gemensamt(rb,f.analys),f.profil.byra.datum)
