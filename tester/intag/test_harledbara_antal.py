from collections import defaultdict
from riskanalys.dokument.underlag import SKYDDAD_VISNING, _uppgift
from riskanalys.profil.hantering import visa_varde
from riskanalys.profil.omfattning import kompatibilitetsvy
from riskanalys.regelverk.granser import metodgranser, metodgransindex
from tester.intag.test_faktablad import _kundbas

ANDEL = 'P-KUND.andel_riskbransch'
BASER = (20, 50, 100, 150, 199, 200, 250, 399, 401, 1000)


def grupper(visningar):
    resultat = defaultdict(set)
    for antal, visning in visningar.items():
        resultat[visning].add(antal)
    return resultat


def _visningar(rb_intag, klar):
    index = metodgransindex(rb_intag)
    return {bas: {a: _uppgift(rb_intag, kompatibilitetsvy(_kundbas(rb_intag, klar, bas, a), rb_intag),
                            ANDEL, gransindex=index).varde for a in range(bas + 1)} for bas in BASER}


def test_visning_skyddar_grupper_begransar_precision_och_redovisar_harledning(rb_intag, klar):
    visningar = _visningar(rb_intag, klar)
    for bas, varden in visningar.items():
        for a in (*range(5), *range(bas - 4, bas)):
            assert varden[a] == SKYDDAD_VISNING
        assert varden[bas] == '100 %'
        if bas >= 50:
            assert varden[round(.9 * bas)] != SKYDDAD_VISNING

    falt, granser = rb_intag.falt[ANDEL], metodgranser(rb_intag, ANDEL)
    for bas, varden in visningar.items():
        synliga = {a: v for a, v in varden.items() if v != SKYDDAD_VISNING}
        nya = grupper(synliga)
        for grupp in grupper({a: (visa_varde(falt, a / bas), tuple(a / bas >= g for g in granser), a == bas) for a in synliga}).values():
            assert grupp <= nya[synliga[next(iter(grupp))]], (bas, grupp)

    exakta = {(bas, next(iter(g))) for bas, vs in visningar.items() for g in grupper(vs).values() if len(g) == 1}
    hela = {(b, a) for b, a in exakta if a == b}
    andra = exakta - hela
    assert hela == {(b, b) for b in BASER}
    assert andra and all(a >= 5 and b - a >= 5 for b, a in andra)
    # Resultat för valda baser, ingen generell 200/400-gräns.
    print('Exakta antal utom hela basen:', {b: sorted(a for bas, a in andra if bas == b) for b in BASER})


def test_hela_begaran_skyddar_sma_grupper_och_restgrupper(rb_intag, klar):
    from tester.intag.test_skyddad_begaran import begaran, _svar_med_nivakandidater
    for bas in (20, 100, 1000):
        profiler = [_kundbas(rb_intag, klar, bas, a) for a in (0, 1, 3, 4, bas - 4, bas - 3, bas - 1)]
        for svar in (None, _svar_med_nivakandidater):
            forsta = begaran(rb_intag, profiler[0], svar)
            assert all(begaran(rb_intag, p, svar) == forsta for p in profiler[1:])
