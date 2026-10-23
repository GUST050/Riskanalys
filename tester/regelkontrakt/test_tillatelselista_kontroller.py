from riskanalys.dokument.underlag import AVSNITTSTYP
from riskanalys.regelverk.laddning import ladda_regelbas


def test_kontrollernas_kategorifalt_ar_tillatna_men_inte_utfallstexten():
    rb = ladda_regelbas()
    tillatna = set(rb.tillatelselistor[AVSNITTSTYP].falt)
    for k in rb.kontroller.values():
        for falt_id in (k.utformning_falt, k.genomforande_falt, k.effekt_falt):
            assert rb.falt[falt_id].typ == "val", falt_id
            if k.id in ("C-TJ-12", "C-TJ-13"):
                assert falt_id not in tillatna  # Steg B utökar inte AI-tillåtelselistan.
            else:
                assert falt_id in tillatna, falt_id
        if k.utfall_falt:
            assert k.utfall_falt not in tillatna
