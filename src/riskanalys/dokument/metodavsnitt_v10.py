"""Metodtabeller läses ur den regelversion som källpaketet binder."""
from riskanalys.dokument.rapportdelar_v10 import avsnitt, tabell, rad, stycke, kallkod


def bygg_metod(rb):
    m = rb.metod
    refs = (kallkod('regelbas', '/metod'),)
    sannolikheter = tuple(dict.fromkeys(r.sannolikhet for r in m.riskmatris))
    konsekvenser = tuple(dict.fromkeys(r.konsekvens for r in m.riskmatris))
    risk = [rad((p, *(next(r.risk for r in m.riskmatris if r.sannolikhet == p and r.konsekvens == k)
                     for k in konsekvenser)), refs) for p in sannolikheter]
    s = []
    regler = [m.konsekvens, m.terrorfinansiering]
    if m.scenario:
        regler += [m.scenario.hotniva, m.scenario.sarbarhetsniva,
                   m.scenario.kvarstaende, m.scenario.aggregering]
    else:
        regler += [m.sannolikhet, m.kvarstaende_ej_belagd, m.kvarstaende_sankning]
    for r in regler:
        s.append(stycke(r.id + ': ' + r.forklaring + ' Grund: ' + r.grund + '.', refs))
    tabeller = [tabell('riskmatris', 'Riskmatris: sannolikhet och konsekvens',
                       ('Sannolikhet / konsekvens', *konsekvenser), risk)]
    if m.scenario:
        hs = tuple(dict.fromkeys(r.hot for r in m.scenario.sannolikhetsmatris))
        vs = tuple(dict.fromkeys(r.sarbarhet for r in m.scenario.sannolikhetsmatris))
        tabeller.append(tabell('sannolikhet', 'Hotnivå och sårbarhetsnivå ger sannolikhet',
            ('Hot / sårbarhet', *vs),
            [rad((h, *(next(r.sannolikhet for r in m.scenario.sannolikhetsmatris
                           if r.hot == h and r.sarbarhet == v) for v in vs)), refs) for h in hs]))
    s.append(stycke('Skalorden ovan kommer från de bundna matrisraderna. Förklaringar och tabellceller är metodval; '
        'de utgör inga nya åtgärdskrav per nivå. Kontrollernas lokala effekt och giltigheten av en sänkning prövas separat. '
        'Aktuell sakkunnigstatus: ' + ', '.join(r.id + ' ' + r.sakkunnig.status for r in regler if hasattr(r, 'sakkunnig')) + '.', refs))
    return avsnitt('4.1', 'Metod, skalor och matriser', s, tabeller)


def kontroller(rb, b):
    rows = []
    for ti, t in enumerate(b.tjanster):
        if not t.erbjuds:
            continue
        for si, s in enumerate(t.scenarier):
            refs = (kallkod('bedomning', f'/tjanster/{ti}/scenarier/{si}'), kallkod('regelbas', '/kontroller'))
            if s.dimension == 'pt' and s.kvarstaende == t.kvarstaende:
                rows.append(rad((t.tjanst, s.hot, ', '.join(s.tackande_kontroller) or 'Inga', s.kvarstaende), refs))
    # Matrisen i 4.2 innehåller varje nivå. Här hålls kontrollförklaringen kort och källbunden.
    s = [stycke('Kontrollmål i katalogen är inte belägg för genomförande, täckning eller verksam effekt. '
        'Katalogens räckvidd, lokal effektprövning och oprövade eller ej godtagna sänkningar ska läsas tillsammans '
        'med 4.2–4.3 och bilaga A, D-ARB.7. Saknat kvarstående värde är inte låg risk.',
        (kallkod('regelbas', '/kontroller'), kallkod('bedomning'), kallkod('analys')))]
    if rb.metod.scenario:
        s.append(stycke(rb.metod.scenario.kvarstaende.forklaring, (kallkod('regelbas', '/metod/scenario/kvarstaende'),)))
    return avsnitt('4.4', 'Kontroller och kvarstående risk', s, (
        tabell('kvarstaende-max', 'PT-scenarier som håller kvar tjänstens nivå',
               ('Tjänst', 'Hot', 'Täckande kontroller i motor', 'Kvarstående'), rows),))
