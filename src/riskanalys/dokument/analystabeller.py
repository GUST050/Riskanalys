"""Scenarier, kontroller och rutiner ur lokal prövning, utan numerisk riskberäkning."""
from collections.abc import Iterable

from riskanalys.analys.provning import scenariosumma
from riskanalys.dokument.analysreferenser import analysref
from riskanalys.dokument.modeller import Tabellcell
from riskanalys.dokument.tabeller import rad, tabell

INTERVALL_MINST = 3  # Så många på varandra följande nummer skrivs som intervall; två skrivs ut.
SCENARIOPREFIX = 'Scenario '

STATUS = {'relevant': 'relevant', 'ej_relevant': 'ej relevant', 'okant': 'okänd', 'okand': 'okänd',
    'bedomd_tillracklig': 'bedömd tillräcklig', 'delvis': 'delvis', 'saknas': 'saknas',
    'foreslagen': 'föreslagen', 'beslutad': 'beslutad', 'genomford': 'genomförd',
    'hanterbart': 'hanterbart', 'kraver_atgard': 'kräver åtgärd', 'kan_inte_hanteras': 'kan inte hanteras',
    'fortsatt': 'fortsatt uppdrag', 'forstark': 'förstärk', 'begransa': 'begränsa', 'avboj': 'avböj', 'avsluta': 'avsluta',
    'forslag': 'förslag', 'bedomd': 'bedömd', 'ej_tillamplig': 'ej tillämplig',
    'ej_reduktion': 'ingen reduktion', 'motiverad': 'motiverad', 'metodkonflikt': 'metodkonflikt',
    'oppet': 'öppet', 'atgardat': 'åtgärdat', 'accepterad_kvarstaende_risk': 'accepterad kvarstående risk',
    'kunskapslucka': 'kunskapslucka', 'kontrollbrist': 'kontrollbrist', 'motstridigt_underlag': 'motstridigt underlag'}


def status(kod):
    return STATUS.get(kod, kod)


def lokalcell(text, refs=()):
    return Tabellcell(text=text, referenser=tuple(dict.fromkeys(refs)), proveniens='lokal')


def _sammanhangande(nummer: Iterable[int]) -> tuple[tuple[int, int], ...]:
    """Stigande följder av på varandra följande nummer som (första, sista)."""
    foljder = ()
    for n in sorted(set(nummer)):
        if foljder and n == foljder[-1][1] + 1:
            foljder = (*foljder[:-1], (foljder[-1][0], n))
        else:
            foljder = (*foljder, (n, n))
    return foljder


def nummerintervall(nummer: Iterable[int]) -> str:
    """Entydig stigande nummerlista: '1–3, 5, 7, 8'. Varje nummer i indata ingår i exakt ett led."""
    def led(forsta, sista):
        if sista - forsta + 1 >= INTERVALL_MINST:
            return f'{forsta}–{sista}'
        return ', '.join(str(n) for n in range(forsta, sista + 1))
    return ', '.join(led(forsta, sista) for forsta, sista in _sammanhangande(nummer))


def _scenarionummer(index, id) -> int | None:
    kort = index.korta.get(analysref('scenario', id), '')
    siffror = kort.removeprefix(SCENARIOPREFIX)
    return int(siffror) if kort.startswith(SCENARIOPREFIX) and siffror.isdigit() else None


def scenarioetikett(index, ids) -> str:
    """Kort synlig scenariohänvisning; cellens referenser bär varje fullständigt scenario-ID."""
    tal = tuple((id, _scenarionummer(index, id)) for id in dict.fromkeys(ids))
    nummer = tuple(n for _, n in tal if n is not None)
    okanda = tuple(index.namn('scenario', id) for id, n in tal if n is None)
    if not nummer:
        kanda = ()
    elif len(nummer) == 1:
        kanda = (SCENARIOPREFIX + str(nummer[0]),)
    else:
        kanda = ('Scenarier ' + nummerintervall(nummer),)
    return '; '.join((*kanda, *okanda)) or 'Inga angivna'


def _namn(rb, ids, katalog):
    return ', '.join(getattr(rb, katalog)[id].namn if id in getattr(rb, katalog) else 'Okänd katalogreferens. [VERIFIERA]' for id in ids)


def scenariorad(s, rb, index, *, rubrik=None, tjanst=None):
    refs = (*s.hot, *index.refs('scenario', (s.id,)), *index.refs('belagg', s.belagg), 'D-ARB.B1')
    delar = index.lista('delanalys', tuple(tjanst+':'+id for id in s.delanalyser)) if s.delanalyser else 'Hela tjänsten'
    return rad(lokalcell(rubrik or index.namn('scenario', s.id), refs),
        lokalcell(s.handelseforlopp or 'Händelseförlopp saknas. [VERIFIERA]', refs),
        lokalcell(f'{status(s.relevans)}. {s.motivering or "Motivering saknas. [VERIFIERA]"} Arbetsmoment: {delar}.', refs),
        lokalcell(('Samma hot som scenariots rubrik' if _namn(rb, s.hot, 'hot') == s.rubrik else _namn(rb, s.hot, 'hot')) or 'Lokalt tillägg utan ny motorfaktor', s.hot),
        lokalcell(index.lista('belagg', s.belagg), refs))


def scenariokopplingsgrupper(a, paket):
    """Gemensam typad gruppoperation för visning och V8-ursprung."""
    gem = {s.id: s for s in paket.gemensamma_scenarier}
    grupper = {}
    for k in a.scenariokopplingar:
        s = gem.get(k.scenario)
        giltig = bool(s and k.bekraftad and k.scenariosumma == scenariosumma(s))
        signatur = (k.tillampning, k.motivering, k.lokal_scenario, giltig,
                    s.relevans if s else None, s.belagg if s else ())
        grupper.setdefault(signatur, []).append((k, s))
    return tuple(grupper.items())


def bygg_scenariotabell(a, paket, rb, index):
    rader = [scenariorad(s, rb, index, tjanst=a.tjanst) for s in a.scenarier]
    for signatur, grupp in scenariokopplingsgrupper(a, paket):
        koppling, s = grupp[0]
        giltig = signatur[3]
        text = ('Bekräftad' if giltig else 'Obekräftad eller inaktuell. [VERIFIERA]') + ' tjänstekoppling: ' + koppling.tillampning + '.'
        if koppling.motivering:
            text += ' ' + koppling.motivering
        lokal = (koppling.lokal_scenario,) if koppling.lokal_scenario else ()
        if lokal:
            # Variantens fulla rubrik står på dess egen rad i samma tabell; här räcker numret.
            text += ' Lokal variant: ' + scenarioetikett(index, lokal) + '.'
        ids = tuple(k.scenario for k, _ in grupp)
        refs = (*index.refs('scenario', ids), 'D-ARB.4')
        hot = tuple(dict.fromkeys(h for _, scenario in grupp if scenario for h in scenario.hot))
        rader.append(rad(lokalcell(scenarioetikett(index, ids), refs),
            lokalcell('Händelseförlopp: se Gemensamma scenarier.', ('D-ARB.4',)),
            lokalcell(text, (*refs, *index.refs('scenario', lokal))),
            lokalcell('Hot enligt gemensamma scenarier' if s else 'Okänt hot. [VERIFIERA]', hot),
            lokalcell(index.lista('belagg', s.belagg) if s else 'Saknas. [VERIFIERA]', refs)))
    if not rader:
        rader.append(rad(*(lokalcell(x) for x in ('Scenarioanalys saknas. [VERIFIERA]', 'Komplettera händelseförlopp.', 'Relevans är okänd.', 'Pröva varje kataloghot.', 'Belägg saknas.'))))
    return tabell(a.tjanst+'-scenarier', 'Scenarioprövning per tjänst', ('Scenario', 'Händelseförlopp', 'Lokal betydelse', 'Hot', 'Belägg'), rader)


def bygg_kontrollprovning(a, rb, index):
    rader = []
    grupper = {}
    for k in a.kontroller:
        grupper.setdefault(k.model_dump_json(exclude={'scenario'}), []).append(k)
    for grupp in grupper.values():
        k = grupp[0]
        scenarier = tuple(x.scenario for x in grupp)
        refs = (k.kontroll, *k.rackvidd, *index.refs('scenario', scenarier), *index.refs('belagg', k.belagg), 'D-ARB.B1')
        rader.append(rad(lokalcell(scenarioetikett(index, scenarier), refs),
            lokalcell(_namn(rb, (k.kontroll,), 'kontroller'), refs),
            lokalcell(f'Tillämpning: {k.tillampning} Utfall: {k.utfall}', refs),
            lokalcell(f'Täckning: {status(k.tackning)}. Kvarstår: {k.kvarstar}', refs),
            lokalcell(index.lista('belagg', k.belagg), refs)))
    return tabell(a.tjanst+'-kontrollprovning', 'Faktisk kontroll och kvarstående begränsning',
        ('Scenario', 'Kontroll', 'Lokal tillämpning och utfall', 'Täckning och begränsning', 'Belägg'), rader) if rader else None


def _prioritet_och_slut(r):
    """Visas bara när de angetts, så att äldre tabeller behåller sin text."""
    delar = ([f'Prioritet: {r.prioritet}.'] if r.prioritet != 'ej_beslutad' else []) + (
        [f'Klart när: {r.klart_nar}'.rstrip('.') + '.'] if r.klart_nar else [])
    return ''.join(' ' + d for d in delar)


def bygg_rutinatgarder(a, index):
    rader = []
    for r in a.rutinatgarder:
        refs = (*index.refs('scenario', r.scenarier), *index.refs('belagg', (*r.belagg, *((r.rutinbelagg,) if r.rutinbelagg else ()))), 'D-ARB.B1')
        rutin = f'{r.rutin_id}, version {r.rutin_version}' if r.rutin_id and r.rutin_version else 'Rutin saknas'
        rader.append(rad(lokalcell(scenarioetikett(index, r.scenarier), refs), lokalcell(r.atgard, refs),
            lokalcell(f'{status(r.status)}. {rutin}.', refs),
            lokalcell(f'Ansvar: {r.ansvar or "inte beslutat"}. Utlösare/frekvens: {r.utlosare_eller_frekvens}. Uppföljning: {r.uppfoljning or "inte beslutad"}.'
                      + _prioritet_och_slut(r), refs)))
    return tabell(a.tjanst+'-rutinatgarder', 'Risk, rutin och åtgärd', ('Scenario', 'Konkret åtgärd', 'Status och rutin', 'Ansvar och uppföljning'), rader) if rader else None
