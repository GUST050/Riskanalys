"""Skrivfritt införandeval; samma regler gäller för webb, CLI och profilsparning."""
from dataclasses import dataclass

from riskanalys.fel import RiskanalysFel
from riskanalys.profil.modeller import Planval, Profil, Tjansteplan
from riskanalys.profil.omfattning import kompatibilitetsvy
from riskanalys.profil.planlivslopp import aktiv_plan
from riskanalys.regelverk.modeller import Regelbas


@dataclass(frozen=True)
class Inforandebehov:
    tjanst: str
    kandidater: tuple[str, ...]


def erbjudandeovergangar(rb: Regelbas, fore: Profil, efter: Profil) -> frozenset[str]:
    fore, efter = kompatibilitetsvy(fore, rb), kompatibilitetsvy(efter, rb)
    return frozenset(t.id for t in rb.tjanster.values()
        if efter.ar_bekraftad(t.erbjuds_falt) and efter.uppgifter[t.erbjuds_falt].varde is True
        and not (fore.ar_bekraftad(t.erbjuds_falt) and fore.uppgifter[t.erbjuds_falt].varde is True))


def inforandebehov(rb: Regelbas, fore: Profil, efter: Profil) -> tuple[Inforandebehov, ...]:
    forevy = kompatibilitetsvy(fore, rb)
    overgar = erbjudandeovergangar(rb, fore, efter)
    behov = []
    for t in rb.tjanster.values():
        if t.id not in overgar:
            continue
        a = forevy.uppgifter.get(t.erbjuds_falt)
        kandidater = tuple(p.id for p in efter.tjansteplaner
            if p.tjanst == t.id and p.typ == 'ny_tjanst' and aktiv_plan(p))
        if kandidater or a and a.status == 'bekräftad' and a.varde is False:
            behov.append(Inforandebehov(t.id, kandidater))
    return tuple(behov)


def validera_planval(rb: Regelbas, fore: Profil, efter: Profil,
                    val: tuple[Planval, ...]) -> dict[str, Tjansteplan]:
    behov = {b.tjanst: b for b in inforandebehov(rb, fore, efter)}
    if len({v.tjanst for v in val}) != len(val):
        raise RiskanalysFel('Ange exakt ett planval per införandetjänst, utan dubbletter.')
    if set(v.tjanst for v in val) != set(behov):
        raise RiskanalysFel('Välj en aktiv plan per införandetjänst. Registrera och utvärdera en plan om kandidat saknas; välj inte plan för oförändrade erbjudanden.')
    planer = {p.id: p for p in efter.tjansteplaner}
    valda = {}
    for v in val:
        if v.plan_id not in behov[v.tjanst].kandidater:
            raise RiskanalysFel(f'{v.tjanst}: välj en aktiv ny-tjänst-plan som hör till tjänsten.')
        valda[v.tjanst] = planer[v.plan_id]
    return valda
