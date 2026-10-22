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

def bygg_gemensamt_fall(rb: Regelbas, rot: Path, fall: str='fyra_tjanster', *, bevara_original: bool=False) -> GemensamtFall:
    f=bygg_rapportlasprov(rb,rot,fall)
    if bevara_original:
        from riskanalys.analys.overforing import foresla_overforing
        paket=foresla_overforing(rb,f.analys)
    else:paket=forifyll_gemensamt(rb,f.analys)
    return GemensamtFall(rb,f.profil,f.bedomning,paket,f.profil.byra.datum)
