"""Korta bara ett exakt återidentifierat automatiskt prefix i V6:s visning."""
from riskanalys.analys.exponering import exponeringsposter, forifylld_exponering
from riskanalys.intag.fordelning import kan_ateranvandas
from riskanalys.profil.hantering import visa_varde_klartext

_ETIKETTER = {
    'erbjuds': 'Erbjuds', 'antal_kunder': 'Kunder', 'andel_kunder': 'Kundandel',
    'omsattning': 'Omsättning (SEK)', 'andel_omsattning': 'Omsättningsandel',
}


def kort_exponering(a, paket, rb, profil):
    giltiga = {f for b in paket.belagg for f in b.profilfalt
        if b.id == 'profil:' + f and f in rb.falt and profil.ar_bekraftad(f)
        and profil.uppgifter[f].datum and profil.uppgifter[f].kalla and profil.uppgifter[f].bekraftad_av
        and kan_ateranvandas(rb, profil, f)}
    prefix, refs = forifylld_exponering(rb, profil, a.tjanst, giltiga)
    if not a.exponering.startswith(prefix) or not set(refs) <= set(a.exponeringsbelagg):
        return a.exponering
    grupper = {}
    erbjuds = rb.tjanster[a.tjanst].erbjuds_falt
    faltprefix = erbjuds.removesuffix('_erbjuds') + '_'
    for f, falt, u in exponeringsposter(rb, profil, a.tjanst, giltiga):
        period = f'{u.period.fran}–{u.period.till}' if u.period else None
        etikett = _ETIKETTER.get(f.removeprefix(faltprefix), falt.etikett or falt.fraga)
        grupper.setdefault((period, u.datum), []).append(f'{etikett}: {visa_varde_klartext(falt, u.varde)}')
    status = 'bekräftat' if profil.ar_bekraftad(erbjuds) else 'okänt; komplettera intaget'
    delar = [f'{rb.tjanster[a.tjanst].namn}: erbjudandet är {status}.']
    for (period, datum), varden in grupper.items():
        metadata = (f'Period {period}; ' if period else '') + f'bekräftat {datum}.'
        delar.append('; '.join(varden) + '. ' + metadata)
    # Allt efter det exakta automatiska prefixet tillhör författaren och bevaras byte för byte.
    return ' '.join(delar) + a.exponering[len(prefix):]
