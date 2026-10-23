"""C:s lästa källställen ger relevans, ingen uppfunnen tjänstefrekvens."""
def test_varje_hot_har_citat_locator_och_uttrycklig_underlagsbrist(regelbas_v1):
    r=regelbas_v1
    assert len(r.hot)==26
    for h in r.hot.values():
        assert h.niva=='medel' and h.sakkunnig.status=='ej_granskad'
        assert 'Källcitat: ”' in h.nivamotivering and '” (' in h.nivamotivering
        assert 'Underlag för annan nivå saknas' in h.nivamotivering
        assert h.kallhanvisningar[0].sida is not None
        assert h.kallhanvisningar[0].kalla in h.kallor
        assert str(h.kallhanvisningar[0].sida) in h.nivamotivering


def test_sanktionshotets_kallcitat_andrar_inte_rattslig_pt_avgransning(regelbas_v1):
    h=regelbas_v1.hot['H-MOD-06']
    assert h.dimensioner==('pt',)
    assert 'brottsvinst' in h.beskrivning.lower() and 'sanktionsbrott' in h.nivamotivering
