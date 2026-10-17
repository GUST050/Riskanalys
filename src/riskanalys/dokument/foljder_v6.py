"""D-ARB.9 i v6: följder för rutiner, kundkännedom, övervakning och utbildning.

Avsnittet sammanställer bara byråns lokalt registrerade slutsats och rutinåtgärder per tjänst.
Programmet beslutar inga åtgärder och fyller inte i det som saknas; luckor blir [VERIFIERA] så att
fastställelsegrinden stoppar. Inget här ingår i AI-underlaget.
"""
from riskanalys.analys.modeller import Analyspaket, Rutinatgard, Tjansteanalys
from riskanalys.analys.provning import gallande_beslut
from riskanalys.bedomning.modeller import Bedomning
from riskanalys.dokument.analysreferenser import Analysreferenser
from riskanalys.dokument.analystabeller import status
from riskanalys.dokument.modeller import Avsnitt
from riskanalys.dokument.skrivversion import V6
from riskanalys.dokument.tjanstavsnitt_v6 import lokaltext
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.regelverk.modeller import Regelbas

AVSNITT_ID = 'D-ARB.9'
RUBRIK = 'Följder för rutiner, kundkännedom, övervakning och utbildning'
# Samma ordprov som v5:s AI-slutsatser (delvalidering.py), på ordstammar så att böjda former räknas.
OMRADEN = (('kundkännedom', 'kundkännedom'), ('övervakning', 'övervak'), ('utbildning', 'utbild'))
STATUSORDNING = ('foreslagen', 'beslutad', 'genomford')
INLEDNING = ('Byråns lokala slutsats och rutinåtgärder; programmet beslutar inga åtgärder. '
             'Scenario, ansvar, utlösare och uppföljning: tjänstens åtgärdstabell.')
SAKNAD_ANALYS = ('Lokal analys saknas. Följder för rutiner, kundkännedom, övervakning och utbildning kan inte '
                 'redovisas; komplettera varje erbjuden tjänst. [VERIFIERA]')
SAKNAD_TJANSTEANALYS = 'Tjänsteanalys saknas; komplettera slutsats och rutinåtgärder. [VERIFIERA]'
EJ_GODKAND = 'Godkännande saknas. [VERIFIERA] '
INGEN_RUTINATGARD = 'Rutiner: ingen rutinåtgärd; komplettera. [VERIFIERA]'
EJ_UPPTAGET = 'saknas i slutsats och rutinåtgärder; komplettera. [VERIFIERA]'


def _uppraknad(poster: list[str]) -> str:
    """'a', 'a och b', 'a, b och c'."""
    return poster[0] if len(poster) == 1 else ', '.join(poster[:-1]) + ' och ' + poster[-1]


def _rutin(r: Rutinatgard) -> str:
    return f'rutin {r.rutin_id} version {r.rutin_version}' if r.rutin_id and r.rutin_version else 'rutin saknas'


def rutinrad(atgarder: tuple[Rutinatgard, ...]) -> str:
    """Föreslagen, beslutad och genomförd redovisas var för sig, med rutin eller synligt saknad rutin."""
    if not atgarder:
        return INGEN_RUTINATGARD
    par = dict.fromkeys((s, _rutin(r)) for s in STATUSORDNING for r in atgarder if r.status == s)
    return 'Rutiner: ' + '; '.join(f'{status(s)} åtgärd, {rutin}' for s, rutin in par) + '.'


def omradesbeskrivning(a: Tjansteanalys, stam: str) -> str:
    kallor = ['slutsatsen'] if stam in a.slutsats.lower() else []
    kallor += [f'{status(s)} åtgärd' for s in STATUSORDNING
               if any(r.status == s and stam in r.atgard.lower() for r in a.rutinatgarder)]
    return f'tas upp i {_uppraknad(kallor)}.' if kallor else EJ_UPPTAGET


def omradesrader(a: Tjansteanalys) -> str:
    """Områden med samma utfall skrivs i en mening, i fast ordning."""
    beskrivningar = [(namn, omradesbeskrivning(a, stam)) for namn, stam in OMRADEN]
    utfall = tuple(dict.fromkeys(text for _, text in beskrivningar))
    return ' '.join(_uppraknad([n for n, t in beskrivningar if t == text]).capitalize() + ': ' + text for text in utfall)


def tjanstrad(a: Tjansteanalys | None, paket: Analyspaket) -> str:
    if a is None:
        return SAKNAD_TJANSTEANALYS
    beslut = gallande_beslut(paket, a.tjanst)
    godkannande = '' if beslut is not None and beslut.godkand else EJ_GODKAND
    return godkannande + rutinrad(a.rutinatgarder) + ' ' + omradesrader(a)


def _refs(avsnitt_id: str, a: Tjansteanalys | None, index: Analysreferenser) -> tuple[str, ...]:
    scenarier = tuple(dict.fromkeys(s for r in (a.rutinatgarder if a else ()) for s in r.scenarier))
    return (avsnitt_id, *index.refs('scenario', scenarier))


def _tjanststycken(rb: Regelbas, bedomning: Bedomning, paket: Analyspaket, index: Analysreferenser):
    """En mening per tjänst; tjänster med exakt samma följder delar mening men behåller sina hänvisningar."""
    analyser = {a.tjanst: a for a in paket.tjanster}
    rader = [(tjanstrad(analyser.get(t.tjanst), paket), rb.tjanster[t.tjanst].namn, _refs(id, analyser.get(t.tjanst), index))
             for id, t in tjanster_med_avsnitt(bedomning)]
    texter = tuple(dict.fromkeys(text for text, _, _ in rader))
    return tuple(lokaltext('; '.join(namn for t, namn, _ in rader if t == text) + ': ' + text,
                           tuple(ref for t, _, refs in rader if t == text for ref in refs)) for text in texter)


def bygg_foljder_v6(rb: Regelbas, bedomning: Bedomning, paket: Analyspaket | None, index: Analysreferenser) -> Avsnitt:
    tjanster = _tjanststycken(rb, bedomning, paket, index) if paket is not None else (lokaltext(SAKNAD_ANALYS),)
    return Avsnitt(id=AVSNITT_ID, rubrik=RUBRIK, kalla='lokal', stycken=(lokaltext(INLEDNING), *tjanster), formatversion=V6)
