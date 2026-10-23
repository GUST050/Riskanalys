"""Alla indikatorer och lagexempel, med fulla lokala områdesmotiveringar."""
from riskanalys.dokument.rapportdelar_v10 import (
    avsnitt, tabell, rad, stycke, kallkod, faltref, fakta, tjanstalias,
)
from riskanalys.dokument.faktorstatus_v10 import faktorstatus, lagre_status, villkor_for, rapportbelagd
from riskanalys.regelverk.villkor import falt_i

OMRADEN = (('kund', 'Kunder'), ('kanal', 'Kanaler'), ('geo', 'Geografi'),
           ('verk', 'Verksamhet'), ('tj', 'Tjänstespecifika faktorer'))


def kopplingar(rb, profil, s):
    tjanster = [t for t in rb.tjanster.values() if s.id in t.sarbarheter
                and t.id in rb.regelpaket[profil.byra.regelpaket].tjanster
                and not (rapportbelagd(rb, profil, t.erbjuds_falt)
                         and profil.uppgifter[t.erbjuds_falt].varde is False)]
    hot = tuple(dict.fromkeys(h for t in tjanster for h in t.hot if h in s.hot))
    return ', '.join(tjanstalias(rb, profil, t.id) for t in tjanster) or 'Inga tillämpliga tjänster', ', '.join(hot) or 'Inga'


def bygg_kapitel3(rb, profil, analys):
    delar = []
    for n, (omrade, namn) in enumerate(OMRADEN, 1):
        rows = []
        for id, s in rb.sarbarheter.items():
            if s.omrade != omrade:
                continue
            falt = sorted(falt_i(villkor_for(rb, s)))
            refs = (kallkod('regelbas', '/sarbarheter/' + id), *(faltref(profil, f) for f in falt))
            tj, hot = kopplingar(rb, profil, s)
            faktatext = '\n'.join(f.split('.', 1)[-1].replace('_', ' ') + ': ' + fakta(rb, profil, f) for f in falt)
            rows.append(rad((id + ' ' + s.namn, faktorstatus(rb, profil, s), faktatext, tj + '\n' + hot), refs))
        stycken = []
        if n == 1:
            stycken.append(stycke('Finns = belagt villkor; Under tröskeln = belagd positiv förekomst under tröskeln; '
                'Nej = bekräftad frånvaro; Okänt = otillräckligt underlag; Inte tillämplig = ingen erbjuden tjänst berörs. '
                'Konservativt motorpåslag är inte bekräftad förekomst. Områdena har ingen separat beräknad risknivå.',
                (kallkod('regelbas', '/sarbarheter'), kallkod('profil'))))
        if analys:
            for i, g in enumerate(analys.gemensamma_sarbarhetsprovningar):
                if g.omrade == omrade:
                    stycken.append(stycke(f'{g.id}; {g.status}; {g.relevans}; {g.dimension.upper()}: '
                        + g.beskrivning + ' ' + g.motivering,
                        (kallkod('analys', f'/gemensamma_sarbarhetsprovningar/{i}'),), lokal=True))
        if not stycken or n == 1 and len(stycken) == 1:
            stycken.append(stycke('Separat lokal områdesmotivering saknas. Tjänsternas fullständiga prövningar finns i 4.3 och bilaga A.',
                                  (kallkod('analys'),)))
        delar.append(avsnitt('3.' + str(n), namn, stycken,
            (tabell('faktorer-' + omrade, 'Riskindikatorer', ('Indikator', 'Status', 'Fakta, period och källa', 'Tjänster / förstärker hot'), rows),)))
    komb = rb.sarbarheter.get('S-KOMB-01')
    sam = [stycke('S-KOMB-01: ' + (faktorstatus(rb, profil, komb) if komb else 'Okänt')
        + '. Detta är modellens kombination på byrånivå. Separata antal styrker inte att samma kunder har flera faktorer. '
        'Kundöverlapp är okänt om det inte finns en belagd kombinationsgrupp.',
        (kallkod('regelbas', '/sarbarheter'), kallkod('profil')))]
    from riskanalys.profil.kombinationer import kombinationsbrister
    brister = kombinationsbrister(rb, profil)
    for i, g in enumerate(profil.kombinationsgrupper):
        k = (kallkod('profil', f'/kombinationsgrupper/{i}'),)
        fel = [x for x in brister if x.startswith((g.id + ':',g.id + '.antal ',g.id + '.bas '))]
        if fel or g.antal.status != 'bekräftad' or g.bas.status != 'bekräftad':
            sam.append(stycke(g.id + ': Okänt; gruppen har inte fullständigt belagt underlag. ' + ' '.join(fel), k))
        else:
            sam.append(stycke(f'{g.id}, {g.tjanst}, {g.population}: {g.antal.varde} av {g.bas.varde}. '
                f'{g.avgransning}. {g.beskrivning}. Faktorer: {", ".join(g.sarbarheter)}. '
                f'Period {g.antal.period.fran}–{g.antal.period.till}; källa {g.antal.kalla}.', k, lokal=True))
    delar.append(avsnitt('3.6', 'Samverkan', sam))
    tf = [s.id for s in rb.sarbarheter.values() if s.galler in ('bada', 'terrorfinansiering')]
    delar.append(avsnitt('3.7', 'Sårbarheter för terrorfinansiering', (stycke(
        'Katalogens TF-relevanta indikatorer: ' + ', '.join(tf) + '. Faktastatus och tjänste-/hotkopplingar framgår av 3.1–3.5. '
        'Katalogkoppling är inte bevis för en kundhändelse. Full TF-motivering och faktiska scenarier finns i 4.2–4.3.',
        (kallkod('regelbas', '/sarbarheter'), kallkod('bedomning'), kallkod('analys'))),)))
    lower = []
    landtexter = tuple(dict.fromkeys(l.motivering for s in rb.lagre_risk.values() for l in s.landbedomningar))
    for id, s in rb.lagre_risk.items():
        refs = (kallkod('regelbas', '/lagre_risk/' + id), *(faltref(profil, f) for f in s.profilfalt))
        grupper = {}
        for l in s.landbedomningar:
            grupper.setdefault((l.bedomning, l.motivering), []).append(l.grupp)
        land = ' '.join(', '.join(gs) + ': ' + status + '.' for (status, text), gs in grupper.items())
        lower.append(rad((id + ' ' + s.namn, lagre_status(rb, profil, s),
            '\n'.join(f.split('.', 1)[-1].replace('_', ' ') + ': ' + fakta(rb, profil, f) for f in s.profilfalt),
            'Ej prövat',
            ('Påverkar nivån.' if s.nivaeffekt else 'Endast redovisning; ingen nivåeffekt.')
            + ' Relevans, överlapp och dubbelräkning med kontroller måste prövas. ' + land), refs))
    law = []
    for i, (id, s) in enumerate(rb.lagre_risk.items(), 1):
        law.append(rad((f'2:4 p. {i}', s.namn, lagre_status(rb, profil, s), id),
                       (kallkod('regelbas', '/lagre_risk/' + id), kallkod('profil'))))
    ids = ('S-ARB-03', 'S-KUND-02', 'S-ARB-19', 'S-ARB-20', 'S-ARB-13',
           'S-ARB-12', 'S-ARB-21', 'S-ARB-22', 'S-ARB-08', 'S-ARB-23')
    for i, id in enumerate(ids, 1):
        s = rb.sarbarheter[id]
        status = faktorstatus(rb, profil, s)
        text = id
        if i in (5, 6):
            text += '; bredare anknytning: ' + status + '. Kundernas hemvist i lagens exempel är inte därmed utredd.'
            status = 'Okänt'
        law.append(rad((f'2:5 p. {i}', s.namn, status, text),
                       (kallkod('regelbas', '/sarbarheter/' + id), kallkod('profil'))))
    delar.append(avsnitt('3.8', 'Lägre risk och lagens exempel', (stycke(
        'Gemensamt underlag för landbedömningarna: ' + ' '.join(landtexter),
        (kallkod('regelbas', '/lagre_risk'),)),), (
        tabell('lagre-risk', 'Indikatorer på potentiellt lägre risk',
               ('Indikator', 'Status', 'Fakta', 'Kan tala för lägre risk i', 'Prövning'), lower),
        tabell('lagexempel', 'PTL 2 kap. 4–5 §§, punkt för punkt', ('Lagrum', 'Exempel', 'Status', 'Underlag och begränsning'), law))))
    return tuple(delar)
