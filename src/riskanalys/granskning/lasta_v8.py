"""V8:s kravtäckning för geografiskt underlag och egen rapportering (B-09, B-10, B-15).

Byråövergripande underlag står en gång i avsnittet Gemensamt faktaunderlag och tjänstens egen
prövning i tjänsteavsnittet. Båda kontrolleras mot ett återbyggt dokument; ett gemensamt stycke
ersätter aldrig tjänstens eget. Äldre v6/v7-kontroller och bytekontrakt ändras inte.
"""
from riskanalys.dokument.gemensamt_v8 import (GEMENSAMT_ID, gemensamma_geografistycken,
                                              gemensamt_erfarenhetsstycke, tjanstens_erfarenhetsstycke,
                                              tjanstens_geografistycke)
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.granskning.lasta_v6 import ATGARD_B10, ATGARD_B15, _b09, _fynd, _oforandrade

KRAVTACKNING_V8 = {'B-09': 'gemensamt+tjanst/lokal-sarbarhet', 'B-10': 'gemensamt+tjanst/lokal-sarbarhet',
                   'B-15': 'gemensamt+tjanst/lokal-sarbarhet'}


def lasta_fynd_v8(rb, p, b, d, forvantat, *, gransindex):
    """Det gemensamma underlaget prövas en gång, tjänstens egen prövning per erbjuden tjänst.

    d är granskningens dokument och forvantat en ny V8-byggnad av samma underlag.
    """
    aktuella, forvantade = d.avsnitt_med_id(), forvantat.avsnitt_med_id()
    gem_aktuellt, gem_forvantat = aktuella.get(GEMENSAMT_ID), forvantade.get(GEMENSAMT_ID)
    tjanster = tuple(tjanster_med_avsnitt(b))
    fynd = []
    if any(t.egen_erfarenhet and t.egen_erfarenhet.belagd for _, t in tjanster) and not _oforandrade(
            gem_aktuellt, gem_forvantat, gemensamt_erfarenhetsstycke(rb, p, b, gransindex=gransindex)):
        fynd.append(_fynd(rb, 'B-15', GEMENSAMT_ID, 'Programmets stycke om byråns egen rapportering och erfarenhet '
                          'saknas eller är ändrat i det gemensamma faktaunderlaget.', ATGARD_B15))
    for stycke in gemensamma_geografistycken(rb, p, b, gransindex=gransindex):
        if not _oforandrade(gem_aktuellt, gem_forvantat, (stycke,)):
            fynd.append(_fynd(rb, 'B-10', GEMENSAMT_ID, 'Byråns geografiska villkor, underlag eller beskrivning saknas '
                              'eller är ändrade i det gemensamma faktaunderlaget.', ATGARD_B10))
    for id, t in tjanster:
        aktuellt, mal = aktuella.get(id), forvantade.get(id)
        e = t.egen_erfarenhet
        if e is None or not e.belagd:
            fynd.append(_fynd(rb, 'B-15', id, 'Aktuellt belägg för egna erfarenheter saknas.', ATGARD_B15))
        elif not _oforandrade(aktuellt, mal, tjanstens_erfarenhetsstycke(rb, p, t, gransindex=gransindex)):
            fynd.append(_fynd(rb, 'B-15', id, 'Tjänstens hänvisning till byråns egen rapportering och erfarenhet saknas '
                              'eller är ändrad i hotdelen.', ATGARD_B15))
        fynd.extend(_b09(rb, p, t, id, gransindex))
        if not _oforandrade(aktuellt, mal, tjanstens_geografistycke(rb, p, t.tjanst, gransindex=gransindex)):
            fynd.append(_fynd(rb, 'B-10', id, 'Tjänstens geografiska prövning saknas eller är ändrad.', ATGARD_B10))
    return fynd
