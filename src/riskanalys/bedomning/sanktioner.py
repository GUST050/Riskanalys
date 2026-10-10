"""Separat föreslagen riskdimension; aldrig kopierad från terrorfinansiering."""

from riskanalys.bedomning.modeller import Riskdel, Sanktionsbedomning
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas, Tjanst
from riskanalys.regelverk.villkor import Sanning, tolka_villkor, utvardera


def bedom_sanktionsrisk(regelbas: Regelbas, tjanst: Tjanst, profil: Profil) -> Sanktionsbedomning:
    """Pröva sanktionsdimensionens egna villkor och belagda kontroll utan ärendebeslut."""
    from riskanalys.bedomning.motor import SANNOLIKHETER, RISKNIVAER, steg, _kontroll

    metod = regelbas.sanktionsmetod
    if metod is None:
        return Sanktionsbedomning(
            status='preliminär', inneboende=None, kvarstaende=None,
            regelspar=(), okanda_uppgifter=('Sanktionsmetod saknas',),
        )
    sannolikhet = metod.grund_sannolikhet
    okanda: set[str] = set()
    spar = [metod.id]
    for rad in metod.rader:
        utfall = utvardera(tolka_villkor(rad.villkor, regelbas.faltdefinitioner()), profil.faltvarden())
        okanda.update(utfall.okanda)
        if utfall.sanning is not Sanning.FALSKT:
            sannolikhet = max((sannolikhet, rad.sannolikhet), key=SANNOLIKHETER.index)
            spar.append(rad.id)
    riskrad = next(
        rad for rad in regelbas.metod.riskmatris
        if rad.sannolikhet == sannolikhet and rad.konsekvens == metod.grund_konsekvens
    )
    kontroll, brister = _kontroll(regelbas.kontroller[metod.kontroll], profil.faltvarden())
    okanda.update(brister)
    spar.extend((riskrad.id, metod.kontroll))
    kvarstaende = steg(riskrad.risk, -1, RISKNIVAER) if kontroll.fungerar_och_ar_belagd else riskrad.risk
    return Sanktionsbedomning(
        kontroll=kontroll, status='preliminär' if okanda else 'slutlig',
        inneboende=Riskdel(sannolikhet=sannolikhet, konsekvens=metod.grund_konsekvens, risk=riskrad.risk),
        kvarstaende=kvarstaende, regelspar=tuple(spar), okanda_uppgifter=tuple(sorted(okanda)),
    )
