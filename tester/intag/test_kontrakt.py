from riskanalys.regelverk.laddning import ladda_regelbas


def test_kanoniska_falt_har_spårbar_intagskoppling():
    rb = ladda_regelbas()
    for f in rb.falt.values():
        if not f.alias_for and not f.basfalt:
            assert getattr(f, 'intag', None) is not None, f.id
            assert f.intag.kallor and f.intag.avsnitt


def test_varje_tjanst_har_lokalt_verksamhetsunderlag():
    rb = ladda_regelbas()
    for t in rb.tjanster.values():
        prefix = t.erbjuds_falt.removesuffix('_erbjuds')
        for del_ in ('arbetssatt', 'kundtyper', 'kanaler', 'geografi', 'ovriga_risker'):
            assert prefix + '_' + del_ in rb.falt


def test_kontrakt_avvisar_okand_referens_och_cykel():
    from riskanalys.regelverk.intagskontrakt import intagskontraktsfel
    rb=ladda_regelbas();f=rb.falt['P-ORG.namn']
    for update in ({'kallor':('SRC-SAKNAS',)}, {'beroenden':('P-ORG.namn',)}):
        f2=f.model_copy(update={'intag':f.intag.model_copy(update=update)})
        r=rb.model_copy(update={'falt':{**rb.falt,f.id:f2}})
        assert intagskontraktsfel(r)


def test_saknad_kravkoppling_och_all_borttagen_metadata_avvisas():
    from riskanalys.regelverk.intagskontrakt import intagskontraktsfel
    rb=ladda_regelbas()
    r=rb.model_copy(update={'falt':{k:f.model_copy(update={'intag':None}) for k,f in rb.falt.items()}})
    assert intagskontraktsfel(r)
    fields={k:f.model_copy(update={'intag':f.intag.model_copy(update={'krav':()})}) if f.intag else f for k,f in rb.falt.items()}
    assert any('frågekoppling' in h for h in intagskontraktsfel(rb.model_copy(update={'falt':fields})))
