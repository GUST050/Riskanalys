"""Gemensam innehållsdefinition för automatiskt förifylld exponering."""
from riskanalys.profil.hantering import visa_varde_klartext


def exponeringsposter(rb, profil, tjanst, giltiga):
    erbjuds = rb.tjanster[tjanst].erbjuds_falt
    return tuple((f, rb.falt[f], u) for f, u in profil.uppgifter.items()
        if f.startswith(erbjuds.removesuffix('_erbjuds') + '_') and f in giltiga and rb.falt[f].typ != 'text')


def forifylld_exponering(rb, profil, tjanst, giltiga):
    """Historisk förifyllning, inklusive exakt ordning, frågor och beläggs-ID:n."""
    kat = rb.tjanster[tjanst]
    erbjuds = kat.erbjuds_falt
    text = f'{kat.namn}: erbjudandet är ' + ('bekräftat.' if profil.ar_bekraftad(erbjuds) else 'okänt; komplettera intaget.')
    refs = ('profil:' + erbjuds,) if erbjuds in giltiga else ()
    for f, falt, u in exponeringsposter(rb, profil, tjanst, giltiga):
        period = f' Period {u.period.fran.isoformat()}–{u.period.till.isoformat()}.' if u.period else ''
        text += f' {falt.etikett or falt.fraga}: {visa_varde_klartext(falt, u.varde)}.{period} Bekräftat {u.datum.isoformat()}.'
        refs += ('profil:' + f,)
    return text, refs
