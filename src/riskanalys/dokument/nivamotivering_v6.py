"""Risknivå och motivering sist i varje v6-tjänst: programmets beräkning i ord och byråns egen bedömning.

Beräkningen återger bara sparade motorutfall och regelbasens data; ingen profil utvärderas och ingen nivå räknas om.
Byråns bedömning återges ordagrant ur den lokala analysen och hålls skild från beräkningen.
"""
from riskanalys.analys.modeller import Tjansteanalys
from riskanalys.bedomning.modeller import Riskdel, Tjanstbedomning
from riskanalys.bedomning.motor import SANNOLIKHETER
from riskanalys.dokument.modeller import Textstycke
from riskanalys.dokument.skrivversion import V6, V7
from riskanalys.dokument.nivatext import PT_OMRADEN, TF_OMRADEN, _sparbegransning, tillampade_faktorer
from riskanalys.regelverk.modeller import Regelbas

B1 = 'D-ARB.B1'
TAK = 'hög'
SAKNAS = 'Saknas; förklara vilka förhållanden i tjänsten som motiverar nivån. [VERIFIERA]'
REDUKTION_SAKNAS = 'Saknas; komplettera. [VERIFIERA]'
KATALOG_SAKNAS = 'Begränsning: tjänstens basnivå saknas i regelbasen.'
REDUKTIONSFRASER = {'ej_reduktion': 'ingen reduktion redovisas', 'motiverad': 'motiverad',
                    'metodkonflikt': 'öppen metodkonflikt', 'okand': 'inte gjord'}


def _upprakning(namn: list[str]) -> str:
    """'A', 'A och B', 'A, B och C'."""
    return namn[0] if len(namn) == 1 else f"{', '.join(namn[:-1])} och {namn[-1]}"


def _faktordel(t: Tjanstbedomning, rb: Regelbas, grund: str, omraden: frozenset[str], *, samma_som_pt=False) -> str:
    """'Grundnivå X; höjs av …{; taket …}' eller 'Grundnivå X; inga tillämpade faktorer höjer den'."""
    faktorer = tillampade_faktorer(t, rb, omraden)
    if not faktorer:
        return f'Grundnivå {grund}; inga tillämpade faktorer höjer den'
    hojning = ', '.join(f'{s.namn} (+{s.effekt.sannolikhet})' for s in faktorer)
    nar_taket = SANNOLIKHETER.index(grund) + sum(s.effekt.sannolikhet for s in faktorer) > SANNOLIKHETER.index(TAK)
    tak = f'; taket {TAK} nås, så fler faktorer ändrar inte nivån' if nar_taket else ''
    faktorfras = 'samma faktorer och vikter som PT' if samma_som_pt else hojning
    return f'Grundnivå {grund}; höjs av {faktorfras}{tak}'


def _delriskmening(rubrik: str, delrisk: Riskdel | None, forklaring: str) -> str:
    if delrisk is None:
        return f'{rubrik}: ej bedömd i det sparade resultatet.'
    return f'{rubrik}: {delrisk.risk}. {forklaring}'


def _ptmening(t: Tjanstbedomning, rb: Regelbas, begransning: str) -> str:
    if begransning or t.inneboende is None:
        return _delriskmening('Penningtvättsrisk före kontroller', t.inneboende, begransning)
    grund = rb.tjanster[t.tjanst].grund_sannolikhet
    forklaring = f'{_faktordel(t, rb, grund, PT_OMRADEN)}; konsekvens {t.inneboende.konsekvens}.'
    return _delriskmening('Penningtvättsrisk före kontroller', t.inneboende, forklaring)


def _tfmening(t: Tjanstbedomning, rb: Regelbas, begransning: str, *, formatversion=V6) -> str:
    if begransning or t.terrorfinansiering is None:
        return _delriskmening('TF-risk', t.terrorfinansiering, begransning)
    grund = rb.tjanster[t.tjanst].grund_tf_sannolikhet
    samma = formatversion == V7 and bool(tillampade_faktorer(t, rb, TF_OMRADEN)) and (
        tuple((s.id, s.effekt.sannolikhet) for s in tillampade_faktorer(t, rb, TF_OMRADEN)) ==
        tuple((s.id, s.effekt.sannolikhet) for s in tillampade_faktorer(t, rb, PT_OMRADEN)))
    forklaring = (f'{_faktordel(t, rb, grund, TF_OMRADEN, samma_som_pt=samma)}; '
                  f'konsekvensen är alltid {t.terrorfinansiering.konsekvens} enligt metoden.')
    return _delriskmening('TF-risk', t.terrorfinansiering, forklaring)


def _belagda_kontroller(t: Tjanstbedomning, rb: Regelbas) -> list[str]:
    return [rb.kontroller[k.id].namn if k.id in rb.kontroller else k.id for k in t.kontroller if k.fungerar_och_ar_belagd]


def _kvarmening(t: Tjanstbedomning, rb: Regelbas, begransning: str, reduktionsprovning: str) -> str:
    if t.kvarstaende is None:
        return 'Efter kontroller: saknas i det sparade resultatet.'
    if begransning:
        return f'Efter kontroller: {t.kvarstaende}. {begransning}'
    if rb.metod.kvarstaende_sankning.id not in t.regelspar:
        return f'Efter kontroller: {t.kvarstaende}; ingen kontroll har belagd funktion, så nivån sänks inte.'
    kontroller = _upprakning(_belagda_kontroller(t, rb) or ['en kontroll'])
    ar_golv = t.inneboende is not None and t.inneboende.risk == t.kvarstaende
    golv = f', men {t.kvarstaende} är redan skalans lägsta nivå' if ar_golv else ''
    fras = REDUKTIONSFRASER.get(reduktionsprovning, reduktionsprovning)
    return (f'Efter kontroller: {t.kvarstaende}. Sänkningen bygger på belagd utformning och genomförande för '
            f'{kontroller}{golv}. Det är ett ogranskat metodval som inte kräver belagd scenariotäckning. '
            f'Lokal reduktionsprövning: {fras}.')


def _sanktionsmening(t: Tjanstbedomning) -> tuple[str, ...]:
    s = t.sanktionsrisk
    if s is None or s.inneboende is None:
        return ()
    efter = f' och {s.kvarstaende} efter' if s.kvarstaende else ''
    return (f'Sanktionsrisk: {s.inneboende.risk} före{efter} kontroll, enligt den separata sanktionsmetoden.',)


def _dimensioner(t: Tjanstbedomning, rb: Regelbas, reduktionsprovning: str, *, formatversion=V6) -> tuple[str, str, str]:
    """PT före kontroll, PT efter kontroll och TF; sanktionen hålls separat eftersom den har eget regelspår."""
    begransning = _sparbegransning(t, rb) or ('' if t.tjanst in rb.tjanster else KATALOG_SAKNAS)
    return (_ptmening(t, rb, begransning), _kvarmening(t, rb, begransning, reduktionsprovning),
            _tfmening(t, rb, begransning, formatversion=formatversion))


def berakningsmotivering(t: Tjanstbedomning, rb: Regelbas, *, reduktionsprovning: str = 'okand') -> tuple[str, ...]:
    """En mening per dimension: PT före kontroll, PT kvarstående, TF och sanktion när den finns."""
    return (*_dimensioner(t, rb, reduktionsprovning), *_sanktionsmening(t))


def _byrans_pt(a: Tjansteanalys | None) -> str:
    text = f'Byråns bedömning av penningtvättsrisken: {(a.pt_motivering.strip() if a else "") or SAKNAS}'
    if a is None:
        return text
    if a.reduktionsmotivering.strip():
        return f'{text} Reduktionsprövning: {a.reduktionsmotivering.strip()}'
    if a.reduktionsprovning != 'ej_reduktion':
        return f'{text} Reduktionsprövning: {REDUKTION_SAKNAS}'
    return text


def _byrans_tf(a: Tjansteanalys | None) -> str:
    return f'Byråns bedömning av TF-risken: {(a.tf_motivering.strip() if a else "") or SAKNAS}'


def _motivering(text: str, refs, proveniens: str) -> Textstycke:
    return Textstycke(typ='motivering', text=text, referenser=list(dict.fromkeys(refs)), proveniens=proveniens)


def nivamotivering_stycken(rb: Regelbas, t: Tjanstbedomning, a: Tjansteanalys | None, *, formatversion=V6) -> tuple[Textstycke, ...]:
    """Programmets beräkning följd av byråns PT- och TF-bedömning; alla stycken har typen motivering."""
    refs = (t.tjanst, *t.regelspar, *t.tillampade_sarbarheter, B1)
    reduktion = a.reduktionsprovning if a is not None else 'okand'
    sanktionsspar = t.sanktionsrisk.regelspar if t.sanktionsrisk else ()
    berakning = (*(_motivering(text, refs, 'regelbas') for text in _dimensioner(t, rb, reduktion, formatversion=formatversion)),
                 *(_motivering(text, (*refs, *sanktionsspar), 'regelbas') for text in _sanktionsmening(t)))
    # Byråns egen text får ingen källhänvisning till regelbasen; länken leder till tjänstens beräkning i B1.
    byran = tuple(_motivering(text, (B1,), 'lokal') for text in (_byrans_pt(a), _byrans_tf(a)))
    return (*berakning, *byran)
