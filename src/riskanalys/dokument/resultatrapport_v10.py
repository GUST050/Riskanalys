"""Ny disposition från fulla original; inga nya AI-svar eller riskberäkningar."""
import re
from riskanalys.dokument.rapportdelar_v10 import avsnitt, stycke, kallkod, uppgift, faltref
from riskanalys.dokument.resultatrapport_v9 import bygg_resultatavsnitt as bygg_v9
from riskanalys.dokument.rapportfakta_v10 import (
    faktaruta, verksamhet, tjanster, hot, erfarenhet, rutiner, uppfoljning, versionslogg,
)
from riskanalys.dokument.kapitel3_v10 import bygg_kapitel3
from riskanalys.dokument.metodavsnitt_v10 import bygg_metod, kontroller


def _programhanvisning(text):
    # Lokala original går aldrig genom denna funktion.
    for gammal, ny in [('R4', '4.2'), ('R5', '4.3'), ('R6', '5.1'), ('R7', '5.3')]:
        text = re.sub(r'(?<![\w-])' + gammal + r'(?![\w-])', ny, text)
    return text


def _flytta(a, nummer, rubrik=None, *, stycken=None):
    ss = []
    for s in a.stycken if stycken is None else stycken:
        if s.proveniens != 'lokal':
            s = s.model_copy(update={'text': _programhanvisning(s.text)})
        ss.append(s)
    tabeller = []
    for t in a.tabeller:
        if a.id == 'D-ARB.R4':
            # Dessa celler skapas av V9-matrisens mall, aldrig ur fri text.
            t = t.model_copy(update={'rader': tuple(r.model_copy(update={'celler': tuple(
                c.model_copy(update={'text': _programhanvisning(c.text)}) for c in r.celler)}) for r in t.rader)})
        if stycken is not None:
            t = t.model_copy(update={'fore_stycke': 0})
        tabeller.append(t)
    return avsnitt(nummer, rubrik or a.rubrik, ss, tabeller)


def bygg_resultatavsnitt_v10(rb, profil, b, resultat, historik, *, analys, underlag):
    old = bygg_v9(rb, profil, b, resultat, historik, analys=analys, underlag=underlag)
    byid = {a.id: a for a in old}
    summary = byid['D-ARB.R1']
    summary = summary.model_copy(update={'stycken': (stycke(
        uppgift(rb, profil, 'P-ORG.namn') + f'. Bedömning per {b.datum}; analysstatus {b.status}. '
        'Leveransstatus framgår av statusraden. Resultatrapport, bilaga A och B1 utgör tillsammans dokumentationen.',
        (faltref(profil, 'P-ORG.namn'), kallkod('bedomning'))), *summary.stycken[1:])})
    risks = byid['D-ARB.R2'].tabeller[0]
    skala = ('låg', 'måttlig', 'hög', 'mycket hög')
    t_by_name = {rb.tjanster[t.tjanst].namn: t for t in b.tjanster if t.erbjuds}
    def nyckel(row):
        t = t_by_name[row.celler[0].text]
        def rank(v):
            return skala.index(v) if v in skala else len(skala)
        return (rank(t.kvarstaende), rank(t.inneboende.risk if t.inneboende else None),
                rank(t.terrorfinansiering.risk if t.terrorfinansiering else None))
    risks = risks.model_copy(update={'id': 'v10-risk', 'rader': tuple(sorted(risks.rader, key=nyckel, reverse=True)),
        'fore_stycke': len(summary.stycken)})
    s0 = _flytta(summary, '0')
    s0 = s0.model_copy(update={'tabeller': (risks,)})
    r4 = byid['D-ARB.R4']
    delade = tuple(row for row in underlag.matris if sum(c.scenario is not None for c in row.celler) > 1)
    gem = []
    for s in r4.stycken:
        refs = s.referenser
        if any(s.text.startswith(row.id + ': ') for row in delade):
            continue  # V10 grupperar samma källmekanism över dimensionerna nedan.
        if any('#/gemensamma_sarbarhetsprovningar/' in x for x in refs):
            continue  # fullständigt i rätt område i kapitel 3
        erfarenhetsref = any('#/gemensamma_verksamhetsposter/' in x for x in refs) and s.text.startswith('erfarenhet,')
        if erfarenhetsref:
            continue  # fullständigt i 2.1
        if s.proveniens != 'lokal' and s.text.startswith('Gemensamma riskfaktorer i de valda scenarierna:'):
            continue  # samtliga faktorer har egna rader i kapitel 3
        if s.proveniens != 'lokal' and s.text.startswith('* avgör tjänstens nivå'):
            s = stycke('* avgör tjänstens nivå före kontroll; † avgör motorns kvarstående nivå. '
                'Markerad oprövad eller ej godtagen sänkning är inte belagd kontrollverkan. '
                'Den inneboende nivån gäller tills prövningen godtar sänkningen; analysgodkännande spärras. '
                'Metoden för dimensioner och kvarstående risk följer den bundna regelversionen i 4.1. '
                'Tjänsternas utfall och begränsningar framgår av cellerna och 4.3.', s.referenser)
        gem.append(s)
    from riskanalys.dokument.scenariokedjor_v10 import gemensamma_kedjor
    gem.extend(gemensamma_kedjor(underlag, analys))
    matris = _flytta(r4, '4.2', 'Scenarier och gemensamma motiveringar', stycken=gem)
    # Tabellpositioner måste följa de bevarade styckena, inte deras gamla index.
    matris = matris.model_copy(update={'tabeller': tuple(t.model_copy(update={'fore_stycke': 0}) for t in matris.tabeller)})
    lok = tuple(_flytta(a, '4.3.' + a.id.removeprefix('D-ARB.R5.'))
                for a in old if a.id.startswith('D-ARB.R5.'))
    return (faktaruta(rb, profil, b, historik), s0,
        avsnitt('1', 'Verksamheten, produkter och tjänster'), verksamhet(rb, profil), tjanster(rb, profil, b),
        _flytta(byid['D-ARB.R3'], '1.3', 'Omfattning'), hot(rb, profil, b, analys), erfarenhet(rb, profil, analys),
        avsnitt('3', 'Sårbarheter och riskfaktorer'), *bygg_kapitel3(rb, profil, analys),
        avsnitt('4', 'Risknivåer och motivering'), bygg_metod(rb), matris, *lok, kontroller(rb, b),
        avsnitt('4.5', 'Tjänsterisk och kundrisk', (stycke('Nivåerna avser tjänster och scenarier. '
            'De klassificerar inte enskilda kunder. Programmet har inget kundriskunderlag som ger kundriskpoäng '
            'eller antal kunder per riskklass i denna rapport. Kundernas egna förhållanden måste prövas separat.',
            (kallkod('bedomning'), kallkod('profil'))),)),
        avsnitt('5', 'Åtgärder och uppföljning'), _flytta(byid['D-ARB.R6'], '5.1', 'Luckor och åtgärder'), rutiner(rb, profil, analys),
        uppfoljning(rb, profil, historik), versionslogg(b, historik))
