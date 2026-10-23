"""Offlinekontroll av V10 mot ny återbyggnad och dess fulla V8-källa."""
from riskanalys.dokument.arb_v10 import bygg_resultatpaket_v10
from riskanalys.dokument.resultatmodell_v9 import kallartefakter, los_referens

KRAVKARTA = {
    'D-ARB.1': ('D-ARB.RF', 'D-ARB.R0', 'D-ARB.R1.3'), 'D-ARB.2': ('D-ARB.R1.3', 'D-ARB.R4.1'),
    'D-ARB.3': ('D-ARB.R1.1', 'D-ARB.R1.2', 'D-ARB.R1.3'),
    'D-ARB.4': ('D-ARB.R2', 'D-ARB.R4.2'), 'D-ARB.5': ('D-ARB.R3',),
    'D-ARB.6': ('D-ARB.R4.3',), 'D-ARB.7': ('D-ARB.R4.4', 'D-ARB.R5.2'),
    'D-ARB.8': ('D-ARB.R0', 'D-ARB.R4.3'), 'D-ARB.9': ('D-ARB.R5.1',),
    'D-ARB.10': ('D-ARB.R5.3', 'D-ARB.R5.4'), 'D-ARB.11': ('D-ARB.R5.3',),
}


def kravkarta_v10(rb, profil, bedomning, bygge):
    from riskanalys.dokument.omfattning import krav_for_dokument, dokumentmal
    from riskanalys.regelverk.urval import valj
    u = valj(rb, bedomning.regelpaket, bedomning.datum, bedomning.lan)
    rows = []
    for valt in krav_for_dokument(rb, u, profil, 'D-ARB'):
        for mal in dokumentmal(valt.krav, 'D-ARB'):
            rows.append({'krav': valt.krav.id, 'mal': mal,
                'analys': [a.id for a in bygge.analysdokument.avsnitt if a.id == mal or a.id.startswith(mal + '.')],
                'sammanfattning': [a.id for a in bygge.dokument.avsnitt if any(
                    a.id == r or a.id.startswith(r + '.') for r in KRAVKARTA.get(mal, ()))],
                'underlag': ['D-ARB.B1']})
    return rows


def resultatfynd_v10(rb, profil, bedomning, resultat, historik, *, analys, bygge, dokument,
                     modellrapport=None, **kwargs):
    fynd = []
    def lagg(id, text):
        fynd.append(dict(typ='tackning', allvar='blockerande', grund='metodval', avsnitt=id,
            beskrivning=text, atgard='Komplettera källan och granska hela resultatrapporten med bilagor på nytt.'))
    nytt = bygg_resultatpaket_v10(rb, profil, bedomning, resultat, historik, analys=analys, modellrapport=modellrapport)
    if nytt != bygge or dokument != nytt.dokument:
        lagg('D-ARB', 'V10:s text, konstruktioner, källor, tabeller eller ordning avviker från återbyggnaden.')
    for b in bygge.underlag.brister:
        lagg('D-ARB.R4.3', b.beskrivning)
    kallor = kallartefakter(rb, profil, bedomning, resultat, historik, analys, bygge.analysdokument)
    for k in bygge.konstruktioner:
        if not k.kallor:
            lagg('D-ARB', 'Konstruktionen saknar källbindning: ' + k.placering)
        for ref in k.kallor:
            try:
                los_referens(kallor, ref)
            except ValueError as e:
                lagg('D-ARB', str(e))
    for r in kravkarta_v10(rb, profil, bedomning, bygge):
        if not r['analys'] or not r['sammanfattning']:
            lagg('D-ARB', 'Kravkartan saknar analys eller huvudavsnitt för ' + r['krav'])
    return fynd
