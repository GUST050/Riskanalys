"""PTL 2:1/LSF 2:2: beakta rapportering utan att härleda en riskpoäng ur antal."""
from riskanalys.bedomning.modeller import EgenErfarenhet
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas

RAPPORTER = "P-VERK.antal_rapporter"
AVBOJANDEN = "P-VERK.antal_avbojanden"
ERFARENHETSFALT = (RAPPORTER, AVBOJANDEN)


def belagd_uppgift(regelbas: Regelbas, profil: Profil, falt_id: str) -> bool:
    """Bekräftelsestatus ensam styrker varken källa, aktualitet eller statistikperiod."""
    f = regelbas.falt.get(falt_id)
    u = profil.uppgifter.get(falt_id)
    bas = profil.uppgifter.get("P-KUND.antal_aktiva")
    period_stammer = not (
        f and f.periodkrav and falt_id.startswith(("P-RISK.", "P-KONTROLL."))
        and (not bas or not bas.period or not u or u.period != bas.period)
    )
    return bool(
        f and u and profil.ar_bekraftad(falt_id)
        and u.kalla and u.kalla.strip() and u.bekraftad_av and u.bekraftad_av.strip()
        and u.datum and (not f.periodkrav or u.period)
        and u.varde is not None and (not isinstance(u.varde, str) or u.varde.strip())
        and period_stammer
    )


def bedom_egen_erfarenhet(regelbas: Regelbas, profil: Profil) -> EgenErfarenhet | None:
    if not all(id in regelbas.falt for id in ERFARENHETSFALT):
        return None  # äldre regelbaser utan detta underlag
    status = {}
    for id in ERFARENHETSFALT:
        u = profil.uppgifter.get(id)
        kant = belagd_uppgift(regelbas, profil, id) and u is not None and type(u.varde) is int and u.varde >= 0
        status[id] = ("inga" if u.varde == 0 else "finns") if kant else "saknas"
    okanda = tuple(id for id in ERFARENHETSFALT if status[id] == "saknas")
    return EgenErfarenhet(rapporter=status[RAPPORTER], avbojanden=status[AVBOJANDEN],
                         belagd=not okanda, okanda_uppgifter=okanda)
