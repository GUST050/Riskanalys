"""Lokala scenariotabeller och förklaringar ur sparade motorutfall."""
from riskanalys.bedomning.modeller import Scenariobedomning, Tjanstbedomning
from riskanalys.dokument.modeller import Dokumenttabell, Tabellcell, Tabellrad
from riskanalys.regelverk.modeller import Regelbas

KORTNAMN = {'Transaktioner med utlandsanknytning': 'Utlandstransaktioner',
            'Extern leverantör för kundkännedom eller AML': 'Extern KYC/AML-leverantör',
            'Kontroll av löpande bokföring': 'Bokföringskontroll',
            'Kontroll av bokslut och årsredovisning': 'Bokslutskontroll',
            'Kontroll av deklarationer och deklarationsombud': 'Deklarationskontroll',
            'Kontroll av lönehantering': 'Lönekontroll',
            'Bankavstämning mot underlag': 'Bankavstämning'}

KOLUMNER = ('Hot', 'Hotnivå', 'Möjliggörande sårbarheter', 'Sannolikhet', 'Risk', 'Täckande kontroll', 'Kvarstående')


def scenarioreferenser(t: Tjanstbedomning, s: Scenariobedomning) -> tuple[str, ...]:
    return tuple(dict.fromkeys((t.tjanst, s.hot, *s.sarbarheter, *s.tackande_kontroller, *s.regelspar)))


def hotnamn(rb: Regelbas, s: Scenariobedomning) -> str:
    return rb.hot[s.hot].namn if s.hot in rb.hot else s.hot


def kontrollnamn(rb: Regelbas, s: Scenariobedomning, *, kort=False) -> str:
    if kort:
        return ", ".join(KORTNAMN.get(rb.kontroller[id].namn, rb.kontroller[id].namn)
                         if id in rb.kontroller else id for id in s.tackande_kontroller)
    return ', '.join(rb.kontroller[id].namn if id in rb.kontroller else id for id in s.tackande_kontroller)


def scenarioforklaring(rb: Regelbas, t: Tjanstbedomning, s: Scenariobedomning, *, vikter=False) -> str:
    """Scenariots egen bas och faktorer; tjänstens globala faktorlista används aldrig."""
    katalog = rb.tjanster.get(t.tjanst)
    if katalog is None:
        return 'Begränsning: tjänstens basnivå saknas i regelbasen.'
    bas = katalog.grund_sannolikhet if s.dimension == 'pt' else katalog.grund_tf_sannolikhet
    faktorer = [rb.sarbarheter[id] for id in s.sarbarheter if id in rb.sarbarheter]
    positiva = [v for v in faktorer if v.effekt.sannolikhet > 0]
    negativa = [v for v in faktorer if v.effekt.sannolikhet < 0]
    def lista(valda):
        return ', '.join(v.namn + (f' ({v.effekt.sannolikhet:+d})' if vikter else '') for v in valda)
    faktor = (', höjd av ' + lista(positiva) if positiva else '')
    faktor += ', sänkt av ' + lista(negativa) if negativa else ''
    return (f'Hotnivå {s.hotniva}{" (iakttaget)" if s.iakttaget else ""}; '
            f'sårbarhetsnivå {s.sarbarhetsniva}: tjänstens egen nivå {bas}{faktor}. '
            f'Sannolikhet {s.sannolikhet}, konsekvens {s.konsekvens}, risk {s.risk}.')


def kontrollmening(rb: Regelbas, s: Scenariobedomning) -> str:
    if s.dimension == 'tf':
        return 'TF sänks inte av kontroller enligt metoden.'
    kvar = s.kvarstaende or 'saknas'
    if s.tackande_kontroller:
        return f'{kontrollnamn(rb, s)} täcker scenariot och har belagd effekt; kvarstående {kvar}.'
    return f'Ingen kontroll med belagd effekt täcker scenariot; kvarstående {kvar}.'


def bygg_scenariotabell(rb: Regelbas, t: Tjanstbedomning) -> Dokumenttabell | None:
    """En rad per sparat PT-/TF-scenario. Katalogmål är inte positiv lokal prövning."""
    if not t.scenarier:
        return None
    rader = []
    for s in t.scenarier:
        refs = scenarioreferenser(t, s)
        etikett = hotnamn(rb, s) + (' (TF)' if s.dimension == 'tf' else '')
        if s.avgorande:
            etikett += ' – avgör nivån'
        varden = (etikett, s.hotniva + (' (iakttaget)' if s.iakttaget else ''),
                  ', '.join(KORTNAMN.get(rb.sarbarheter[id].namn, rb.sarbarheter[id].namn) if id in rb.sarbarheter else id for id in s.sarbarheter) or 'Inga',
                  s.sannolikhet, s.risk, kontrollnamn(rb, s, kort=True) or 'Ingen',
                  s.kvarstaende or ('–' if s.dimension == 'tf' else 'Saknas'))
        rader.append(Tabellrad(celler=tuple(Tabellcell(text=v, referenser=refs, proveniens='regelbas') for v in varden)))
    return Dokumenttabell(id=t.tjanst + '-motorscenarier', rubrik='Motorns scenarier', kolumner=KOLUMNER,
                         rader=tuple(rader), fore_stycke=0)


def sammanfor_scenarioforklaringar(avsnitt, rb: Regelbas, *, startnummer: int):
    """En identisk beräkning återges en gång; namn, dimension och kontrollmening står kvar tjänstevis."""
    import re
    from riskanalys.dokument.modeller import Textstycke
    monster = re.compile(r'^(Avgörande scenario \((PT|TF)\): .+?\. )(Hotnivå .+?\. Sannolikhet .+?\. )(.*)$')
    grupper = {}
    for a in avsnitt:
        for n, s in enumerate(a.stycken):
            m = monster.fullmatch(s.text) if s.proveniens == 'regelbas' else None
            if m:
                faktorer = tuple(sorted((id, rb.sarbarheter[id].effekt.sannolikhet)
                                       for id in s.referenser if id in rb.sarbarheter))
                grupper.setdefault((m[2], m[3], faktorer), []).append((a, n, s, m))
    ersattningar = {}
    gemensamma = []
    for (dimension, forklaring, _), grupp in grupper.items():
        if len({a.id for a, _, _, _ in grupp}) < 2:
            continue
        nummer = startnummer + len(gemensamma)
        namn = []
        hot = []
        refs = []
        for a, n, s, m in grupp:
            tjanst = next((rb.tjanster[id].namn for id in s.referenser if id in rb.tjanster), a.rubrik)
            namn.append(tjanst)
            hot.append(m[1].split(': ', 1)[1].removesuffix('. '))
            refs.extend((*s.referenser, a.id))
            ersattningar[a.id, n] = s.model_copy(update={
                'text': m[1].replace('Avgörande scenario (', 'Avgörande (') + f'Se resonemang {nummer}. ' + (m[4] if dimension == 'PT' else ''),
                'referenser': list(dict.fromkeys((*s.referenser, 'D-ARB.5')))})
        gemensamma.append(Textstycke(typ='motivering',
            text=f'{nummer}. Gemensam scenarioberäkning ({dimension}): ' + '; '.join(dict.fromkeys(hot))
                 + '. Tjänster: ' + ', '.join(dict.fromkeys(namn)) + '. ' + forklaring.rstrip()
                 + (' TF sänks inte av kontroller enligt metoden.' if dimension == 'TF' else ''),
            referenser=list(dict.fromkeys(refs)), proveniens='regelbas'))
    nya = tuple(a.model_copy(update={'stycken': tuple(ersattningar.get((a.id, n), s) for n, s in enumerate(a.stycken))})
                for a in avsnitt)
    return nya, tuple(gemensamma)
