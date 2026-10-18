"""Frivillig tjänstefördelning stannar lokalt och ändrar inga motorvillkor."""
import hashlib
import json

from riskanalys.profil.modeller import Profil, Uppgift
from riskanalys.profil.omfattning import kompatibilitetsvy
from riskanalys.regelverk.modeller import Regelbas, Tjanst

FAKTORER = {
    'antal_utland_transaktion': ('P-GEO.antal_utland_transaktion', 'utlandstransaktioner'),
    'antal_utland_agare': ('P-GEO.antal_utland_agare', 'utländska ägare'),
    'antal_riskbransch': ('P-KUND.antal_riskbransch', 'verksamhet i riskbransch'),
    'antal_kontant': ('P-KUND.antal_kontant', 'kontanthantering'),
}
KUNDBAS = 'P-KUND.antal_aktiva'
SUFFIX = tuple('_' + suffix for suffix in FAKTORER)


def faltkoppling(rb: Regelbas, id: str) -> tuple[Tjanst, str, str] | None:
    """Endast de fyra registrerade nya fälten per tjänst har detta kontrakt."""
    if id not in rb.falt or not id.startswith('P-TJ.') or not id.endswith(SUFFIX):
        return None
    for t in rb.tjanster.values():
        prefix = t.erbjuds_falt.removesuffix('_erbjuds')
        for suffix, (byrafalt, faktor) in FAKTORER.items():
            if id == f'{prefix}_{suffix}':
                return t, byrafalt, faktor
    return None


def _bekraftad(p, id):
    u = p.uppgifter.get(id, Uppgift())
    return (p.ar_bekraftad(id) and bool(u.kalla and u.kalla.strip())
        and bool(u.bekraftad_av and u.bekraftad_av.strip())
        and u.datum is not None and u.datum <= p.byra.datum)


def _antal(p, id):
    u = p.uppgifter.get(id, Uppgift())
    return (_bekraftad(p, id) and type(u.varde) is int and u.varde >= 0
        and u.period is not None and u.period.till <= p.byra.datum)


def _erbjuds(p, t):
    return _bekraftad(p, t.erbjuds_falt) and p.uppgifter[t.erbjuds_falt].varde is True


def _flera(rb, p, t):
    # Ett okänt tredje erbjudande hindrar inte två bekräftat erbjudna tjänster.
    return any(annan.id != t.id and _erbjuds(p, annan) for annan in rb.tjanster.values())


def aktiverad(rb: Regelbas, profil: Profil, id: str) -> bool:
    koppling = faltkoppling(rb, id)
    if koppling is None:
        return False
    t, byrafalt, _ = koppling
    p = kompatibilitetsvy(profil, rb)
    if not (_erbjuds(p, t) and _flera(rb, p, t) and _antal(p, byrafalt) and _antal(p, KUNDBAS)):
        return False
    u, bas = p.uppgifter[byrafalt], p.uppgifter[KUNDBAS]
    return 0 < u.varde <= bas.varde and u.period == bas.period


def fragetext(rb: Regelbas, profil: Profil, id: str) -> str:
    t, byrafalt, faktor = faltkoppling(rb, id)
    n = profil.uppgifter[byrafalt].varde
    return f'{t.namn}: Hur många av byråns {n} kunder med {faktor} använder tjänsten?'


def svarsbrist(rb: Regelbas, profil: Profil, id: str) -> str | None:
    """Kontrollera ett lämnat svar; frånvaro, gammalt eller inaktivt svar spärrar inte."""
    if not aktiverad(rb, profil, id) or not profil.ar_bekraftad(id):
        return None
    t, byrafalt, faktor = faltkoppling(rb, id)
    u = profil.uppgifter[id]
    kundfalt = t.erbjuds_falt.removesuffix('_erbjuds') + '_antal_kunder'
    bas = profil.uppgifter.get(kundfalt, Uppgift())
    if type(u.varde) is not int or u.varde < 0:
        return f'{id}: {t.namn}: ange ett heltal som är minst noll.'
    if (not _antal(profil, kundfalt) or bas.period != profil.uppgifter[byrafalt].period
            or bas.varde > profil.uppgifter[KUNDBAS].varde):
        return f'{id}: {t.namn}: bekräfta tjänstens kundantal för samma statistikperiod som byråns antal och högst byråns kundantal.'
    if u.varde > min(profil.uppgifter[byrafalt].varde, bas.varde):
        return f'{id}: {t.namn}: fler kunder med {faktor} än byrån har totalt eller än tjänsten har; rätta antalet.'
    if u.period != bas.period:
        return f'{id}: {t.namn}: fördelningen ska avse samma statistikperiod som byråns och tjänstens antal.'
    return None


def underlagsbindning(rb: Regelbas, profil: Profil, id: str) -> str:
    """Bind svaret till relevanta baser/belägg och aktivering, utan ovidkommande tredje tjänst."""
    p = kompatibilitetsvy(profil, rb)
    t, byrafalt, _ = faltkoppling(rb, id)
    ids = (id, byrafalt, KUNDBAS, t.erbjuds_falt,
        t.erbjuds_falt.removesuffix('_erbjuds') + '_antal_kunder')
    data = {ref: p.uppgifter.get(ref, Uppgift()).model_dump(mode='json', exclude={'underlagsbindning'}) for ref in ids}
    data['flera_tjanster'] = _flera(rb, p, t)
    return 'sha256:' + hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def omprova(rb: Regelbas, profil: Profil) -> Profil:
    """Bevara äldre belägg men markera bundna svar som gamla efter relevanta ändringar."""
    upp = dict(profil.uppgifter)
    for id, u in profil.uppgifter.items():
        if (u.underlagsbindning and not u.inaktuell and faltkoppling(rb, id)
                and u.underlagsbindning != underlagsbindning(rb, profil, id)):
            upp[id] = u.model_copy(update={'inaktuell': True})
    return profil.model_copy(update={'uppgifter': upp})


def tjanstefordelning(rb: Regelbas, profil: Profil, tjanst: str) -> dict[str, int]:
    """Bekräftat byråfält-ID → giltigt antal i tjänsten, för V6 och V7.

    Överlappande tjänster summeras aldrig. Handändrat eller obundet svar ger inget
    varav; bindningen är spårbarhet och skydd mot gamla underlag, ingen attest.
    """
    p = kompatibilitetsvy(profil, rb)
    svar = {}
    t = rb.tjanster.get(tjanst)
    if t is None:
        return svar
    prefix = t.erbjuds_falt.removesuffix('_erbjuds')
    for suffix in FAKTORER:
        id = f'{prefix}_{suffix}'
        u = p.uppgifter.get(id, Uppgift())
        koppling = faltkoppling(rb, id)
        if (koppling and koppling[0].id == tjanst and aktiverad(rb, p, id)
                and _antal(p, id) and svarsbrist(rb, p, id) is None
                and u.underlagsbindning == underlagsbindning(rb, p, id)):
            svar[koppling[1]] = u.varde
    return svar


def kan_ateranvandas(rb: Regelbas, profil: Profil, id: str) -> bool:
    """Nya fördelningar kräver samma giltighetsprov i lokal text och belägg; äldre fält lämnas oförändrade."""
    koppling = faltkoppling(rb, id)
    return koppling is None or koppling[1] in tjanstefordelning(rb, profil, koppling[0].id)
