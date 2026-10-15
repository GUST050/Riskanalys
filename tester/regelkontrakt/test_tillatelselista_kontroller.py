from riskanalys.dokument.underlag import AVSNITTSTYP
from riskanalys.regelverk.laddning import ladda_regelbas


def test_kontrollernas_kategorifalt_ar_tillatna_men_inte_utfallstexten():
    rb = ladda_regelbas()
    tillatna = set(rb.tillatelselistor[AVSNITTSTYP].falt)
    for k in rb.kontroller.values():
        for falt_id in (k.utformning_falt, k.genomforande_falt, k.effekt_falt):
            assert falt_id in tillatna and rb.falt[falt_id].typ == "val", falt_id
        if k.utfall_falt:
            assert k.utfall_falt not in tillatna
