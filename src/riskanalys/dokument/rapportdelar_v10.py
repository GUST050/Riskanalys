"""Små byggblock för källbundna avsnitt; inga riskbeslut."""
from riskanalys.dokument.modeller import Avsnitt, Dokumenttabell, Tabellrad, Tabellcell
from riskanalys.dokument.rapportversion import V10
from riskanalys.dokument.resultatrapport_v9 import stycke, kallkod
from riskanalys.dokument.resultatmodell_v9 import pointerdel
from riskanalys.dokument.faktorstatus_v10 import rapportbelagd


def avsnitt(nummer, rubrik, stycken=(), tabeller=()):
    return Avsnitt(id='D-ARB.R' + nummer, rubrik=rubrik, kalla='regelbas',
                   stycken=tuple(stycken), tabeller=tuple(tabeller), formatversion=V10,
                   leveransdel='resultatrapport', visningsnummer='' if nummer == 'F' else nummer)


def tabell(id, rubrik, kolumner, rader, fore=0):
    return Dokumenttabell(id='v10-' + id, rubrik=rubrik, kolumner=tuple(kolumner), fore_stycke=fore,
        rader=tuple(Tabellrad(celler=tuple(Tabellcell(text=str(text), referenser=tuple(refs),
                    proveniens='lokal' if any(x.startswith(('kalla:profil#', 'kalla:analys#')) for x in refs) else None)
                                           for text, refs in rad)) for rad in rader))


def rad(varden, refs):
    return [(v, refs) for v in varden]


def faltref(profil, id):
    return kallkod('profil', '/uppgifter/' + pointerdel(id)) if id in profil.uppgifter else kallkod('profil')


def uppgift(rb, profil, id):
    u = profil.uppgifter.get(id)
    if not u or not rapportbelagd(rb, profil, id):
        return 'Okänt'
    v = u.varde
    if type(v) is bool:
        return 'Ja' if v else 'Nej'
    if isinstance(v, (tuple, list)):
        return ', '.join(str(x) for x in v) or 'Inga angivna'
    if rb.falt[id].typ == 'andel':
        return f'{v:.1%}'.replace('.', ',')
    return str(v)


def period_kalla(profil, id):
    u = profil.uppgifter.get(id)
    if not u:
        return 'Okänd period', 'Källa saknas'
    perioder = tuple(dict.fromkeys((v.period.fran, v.period.till) for v in profil.uppgifter.values() if v.period))
    kallor = tuple(dict.fromkeys(v.kalla for v in profil.uppgifter.values() if v.kalla))
    period = 'P' + str(perioder.index((u.period.fran, u.period.till)) + 1) if u.period else 'Ej angiven'
    kalla = 'K' + str(kallor.index(u.kalla) + 1) if u.kalla else 'Saknas'
    return period, kalla


def fakta(rb, profil, id):
    return uppgift(rb, profil, id) + '; ' + '; '.join(period_kalla(profil, id))


def register(profil):
    perioder = tuple(dict.fromkeys((v.period.fran, v.period.till) for v in profil.uppgifter.values() if v.period))
    kallor = tuple(dict.fromkeys(v.kalla for v in profil.uppgifter.values() if v.kalla))
    return '; '.join(f'P{i}: {a}–{b}' for i, (a, b) in enumerate(perioder, 1)) + '.\n' + '; '.join(
        f'K{i}: {k}' for i, k in enumerate(kallor, 1))


def tjanstalias(rb, profil, id):
    return 'T' + str(rb.regelpaket[profil.byra.regelpaket].tjanster.index(id) + 1)
