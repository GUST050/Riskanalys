"""B-09, B-10 och B-15 i v6: belägg och programmets låsta stycken i varje tjänstavsnitt (spec 8.4.6 punkt 2).

Det låsta stycket jämförs med samma stycke i det återbyggda dokumentet, byte för byte och med
källhänvisningar. Hela avsnittets kontrollsumma prövas separat i dokument_v6.
"""
from riskanalys.dokument.analysunderlag import sarbarhetsstycke
from riskanalys.dokument.klartext import VERIFIERA
from riskanalys.dokument.lasta_v6 import erfarenhetsstycke_v6, geografistycke_v6
from riskanalys.dokument.underlag import tjanster_med_avsnitt

ATGARD_B15 = ('Bekräfta rapporter och misstankebaserade avböjanden med källa och period, kör bedömningen igen '
              'och återskapa dokumentet. Sakgranska på nytt.')
ATGARD_B09 = ('Bekräfta faktiska länder och områden, även svenska anknytningar, och tjänstens geografiska underlag. '
              'Kör bedömningen igen och återskapa dokumentet.')
ATGARD_B10 = ('Återskapa tjänstavsnittet så att geografins villkor, bekräftade värden, perioder och källor står kvar '
              'oförändrade. Sakgranska slutsatsen.')


def _fynd(rb, regel, avsnitt, beskrivning, atgard):
    post = rb.bristmonster.get(regel)
    return dict(typ='bristmonster', regel=regel, allvar='blockerande', grund=post.grund if post else 'metodval',
                avsnitt=avsnitt, beskrivning=beskrivning, atgard=atgard)


def _renderat(avsnitt, last):
    """Det låsta stycket som det står i det återbyggda avsnittet, med programmets källhänvisningar."""
    if avsnitt is None:
        return None
    return next((s for s in avsnitt.stycken if s.referenser == last.referenser and s.text.startswith(last.text)), None)


def _oforandrade(aktuellt, forvantat, lasta):
    """Varje låst stycke finns kvar i avsnittet med samma text och minst samma referenser."""
    for last in lasta:
        mal = _renderat(forvantat, last)
        if mal is None or aktuellt is None or not any(
                s.text == mal.text and set(mal.referenser) <= set(s.referenser) for s in aktuellt.stycken):
            return False
    return True


def _b15(rb, p, t, id, aktuellt, forvantat, index):
    e = t.egen_erfarenhet
    if e is None or not e.belagd:
        return [_fynd(rb, 'B-15', id, 'Aktuellt belägg för egna erfarenheter saknas.', ATGARD_B15)]
    if not _oforandrade(aktuellt, forvantat, erfarenhetsstycke_v6(rb, p, t, gransindex=index)):
        return [_fynd(rb, 'B-15', id, 'Programmets stycke om egen rapportering och erfarenhet saknas eller är ändrat i hotdelen.',
                      ATGARD_B15)]
    return []


def _b09(rb, p, t, id, index):
    sarbarheter = rb.tjanster[t.tjanst].sarbarheter
    if any(rb.sarbarheter[s].omrade == 'geo' and VERIFIERA in sarbarhetsstycke(rb, p, t.tjanst, s, gransindex=index).text
           for s in sarbarheter):
        return [_fynd(rb, 'B-09', id, 'Geografins aktuella underlag är ofullständigt.', ATGARD_B09)]
    return []


def _b10(rb, p, t, id, aktuellt, forvantat, index):
    if _oforandrade(aktuellt, forvantat, geografistycke_v6(rb, p, t.tjanst, gransindex=index)):
        return []
    return [_fynd(rb, 'B-10', id, 'Den geografiska sårbarheten saknar programmets spårbara underlagsmotivering, '
                  'eller motiveringen är ändrad.', ATGARD_B10)]


def lasta_fynd_v6(rb, p, b, d, forvantat, *, gransindex):
    """Fynd per erbjuden tjänst; d är granskningens dokument och forvantat en ny v6-byggnad av samma underlag."""
    aktuella, forvantade = d.avsnitt_med_id(), forvantat.avsnitt_med_id()
    fynd = []
    for id, t in tjanster_med_avsnitt(b):
        aktuellt, mal = aktuella.get(id), forvantade.get(id)
        fynd.extend((*_b15(rb, p, t, id, aktuellt, mal, gransindex), *_b09(rb, p, t, id, gransindex),
                     *_b10(rb, p, t, id, aktuellt, mal, gransindex)))
    return fynd
