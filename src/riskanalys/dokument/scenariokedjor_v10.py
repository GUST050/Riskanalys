"""Samma originalmekanism en gång även när den används för både PT och TF."""
from riskanalys.dokument.resultatmodell_v9 import los_pointer
from riskanalys.dokument.rapportdelar_v10 import stycke, kallkod


def gemensamma_kedjor(underlag, analys):
    grupper = {}
    for row in underlag.matris:
        if sum(c.scenario is not None for c in row.celler) <= 1:
            continue
        identitet = tuple((r.artefakt, r.pointer) for r in row.mekanismkallor)
        if not identitet:
            identitet = (('saknad', row.id),)
        grupper.setdefault(identitet, []).append(row)
    data = analys.model_dump(mode='json') if analys else {}
    poster = []
    for rows in grupper.values():
        original = []
        refs = []
        for r in rows[0].mekanismkallor:
            v = los_pointer(data, r.pointer)
            if v.get('handelseforlopp') and v['handelseforlopp'] not in original:
                original.append(v['handelseforlopp'])
            refs.append(kallkod(r.artefakt, r.pointer))
        utfall = []
        for row in rows:
            sk = tuple(dict.fromkeys((c.scenario.sannolikhet, c.scenario.konsekvens)
                       for c in row.celler if c.scenario))
            utfall.append(row.id + ' ' + row.dimension.upper() + ': ' + '; '.join(
                'sannolikhet ' + s + ', konsekvens ' + k for s, k in sk))
        poster.append(stycke('Gemensam kedja ' + ', '.join(r.id for r in rows) + ': '
            + (' '.join(original) or '[VERIFIERA] Lokal scenariomekanism saknas.') + '\n' + '. '.join(utfall) + '.',
            (*refs, kallkod('bedomning', '/tjanster')), lokal=True))
    return tuple(poster)
