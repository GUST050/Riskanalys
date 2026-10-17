"""Steg 1:s läsordning, sammansatt ur oförändrade v5-skrivresultat."""

from riskanalys.dokument.arb_v5 import bygg_arb_v5, stycke
from riskanalys.dokument.kallhanvisningar import med_kallhanvisningar
from riskanalys.dokument.matning import med_langdvarning
from riskanalys.dokument.modeller import Dokument
from riskanalys.regelverk.modeller import _summa, utan_granskningsmetadata

FORMATVERSION = 'D-ARB-tjanst-v5.1'
METODFRAGOR = (
    'Kontrollernas räckvidd', 'TF som egen dimension',
    'Enstaka exponering kontra omfattning', 'Summering, tak och dubbelräkning',
)


def _sakkunnigstatus(post):
    summa = _summa(utan_granskningsmetadata(post.model_dump(mode='json')))
    status = post.sakkunnig.status
    return 'verifierad men inaktuell' if status == 'verifierad' and not post.sakkunnig.galler(summa) else status


def _rackviddsstycken(rb, bedomning):
    """Visa katalogens möjliga observationer en gång, utan genomförandepåstående."""
    kontroller = {}
    for t in bedomning.tjanster:
        if not t.inneboende:
            continue
        for k in (*t.kontroller, *((t.sanktionsrisk.kontroll,)
                                  if t.sanktionsrisk and t.sanktionsrisk.kontroll else ())):
            kontroller.setdefault(k.id, set()).add(t.tjanst)
    poster = [stycke(
        'Källbunden kontrollräckvidd beskriver möjliga observationer och begränsningar. '
        'Den styrker inte byråns genomförande, faktisk scenariotäckning eller en riskreduktion.')]
    for id, tjanster in kontroller.items():
        kontroll = rb.kontroller[id]
        rackvidd = [r for r in getattr(kontroll, 'rackvidd', ()) if r.tjanst in tjanster]
        for tjanst in sorted(tjanster - {r.tjanst for r in rackvidd}):
            poster.append(stycke(
                f'{kontroll.namn} – {rb.tjanster[tjanst].namn}: källbunden scenariotäckning är okänd. '
                'Komplettera källunderlaget och pröva den lokala tillämpningen.', [id, tjanst]))
        for r in rackvidd:
            kallor = '; '.join(f'{rb.kallor[h.kalla].titel}, {h.avsnitt}, s. {h.sida}' for h in r.kallhanvisningar)
            poster.append(stycke(
                f'{kontroll.namn} – {rb.tjanster[r.tjanst].namn}. '
                f'Hot: {", ".join(rb.hot[id].namn for id in r.hot)}. Kan belägga: {r.kan_belagga} '
                f'Begränsningar: {r.begransningar} Förutsättningar: {r.forutsattningar} '
                f'Grund: {r.grund}. Sakkunnigstatus: {_sakkunnigstatus(r)}. '
                f'Precisa källhänvisningar: {kallor}.',
                [id, r.id, r.tjanst, *r.hot, *(h.kalla for h in r.kallhanvisningar)]))
    return tuple(poster)


def bygg_arb_v5_1(rb, profil, bedomning, resultat, historik, *, gransindex=None) -> Dokument:
    """Flytta presentationen; beräkna aldrig om sparade motorutfall."""
    gammalt = bygg_arb_v5(rb, profil, bedomning, resultat, historik, gransindex=gransindex)
    avsnitt = gammalt.avsnitt_med_id()
    bilaga = avsnitt['D-ARB.B1']
    bilagetexter = list(bilaga.stycken)
    bilagetabeller = list(bilaga.tabeller)
    metodposter = (*rb.metod.regler(), *rb.metod.riskmatris)
    verifierade = sum(_sakkunnigstatus(r) == 'verifierad' for r in metodposter)
    metodstatus = (f'Metodstatus: {verifierade} av {len(metodposter)} regelobjekt har giltig '
                   'sakkunnigverifiering. Regelvis atteststatus finns i bilaga B1. '
                   'Objektattester avgör inte i sig de öppna metodfrågorna.')
    bilagetexter.append(stycke('Regelvis sakkunnigstatus: ' + '; '.join(
        f'{r.id}: {_sakkunnigstatus(r)}' for r in metodposter) + '.', [r.id for r in metodposter]))
    poster = []
    for a in gammalt.avsnitt:
        if a.id in ('D-ARB.8', 'D-ARB.B1'):
            continue
        berakningar = tuple(t for t in a.tabeller if t.id.endswith('-utfall'))
        if berakningar:
            pos = len(bilagetexter)
            bilagetexter.append(stycke(
                f'Beräkningsunderlag för {a.rubrik.lower()}. Åter till tjänsteanalysen: {a.rubrik}.', [a.id]))
            bilagetabeller.extend(t.model_copy(update={'fore_stycke': pos}) for t in berakningar)
            a = a.model_copy(update={
                'tabeller': tuple(t for t in a.tabeller if not t.id.endswith('-utfall')),
                'stycken': (*a.stycken, stycke(
                    'Fullständig beräkning och regelspår finns i bilaga B1.', ['D-ARB.B1'])),
            })
        if a.id == 'D-ARB.7':
            a = a.model_copy(update={'stycken': (*a.stycken, *_rackviddsstycken(rb, bedomning))})
        if a.id == 'D-ARB.1':
            a = a.model_copy(update={'stycken': tuple(
                stycke(metodstatus + ' Nivåerna är motorns utfall. Öppna metodfrågor och '
                       'kontrollbrister behöver hanteras före fastställelse.', [r.id for r in metodposter])
                if s.text.startswith('Metodstatus:') else s for s in a.stycken)})
        poster.append(a)
    oversikt = avsnitt['D-ARB.8'].model_copy(update={'stycken': (stycke(
        'Nivåerna är oförändrade motorutfall. Fullständig beräkning och regelspår finns i bilaga '
        'B1. Metodstatus och begränsningar framgår av syftet och metodavsnittet. '
        'Ingen sammanvägd byrånivå beräknas. Sanktionsrisk är inte ett besked om listträff eller förbud.',
        ['D-ARB.B1']), stycke(metodstatus, [r.id for r in metodposter]), *(
            stycke(f'{fraga}: öppen, inte dokumenterat avgjord.') for fraga in METODFRAGOR))})
    poster.insert(1, oversikt)
    poster.append(bilaga.model_copy(update={'stycken': tuple(bilagetexter), 'tabeller': tuple(bilagetabeller)}))
    dokument = gammalt.model_copy(update={'avsnitt': tuple(
        a.model_copy(update={'formatversion': FORMATVERSION,
                             'visningsnummer': 'B1' if a.id == 'D-ARB.B1' else str(n)})
        for n, a in enumerate(poster, 1))})
    return med_langdvarning(med_kallhanvisningar(dokument, rb), profil)
