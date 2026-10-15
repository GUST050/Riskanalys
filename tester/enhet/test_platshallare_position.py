from riskanalys.dokument.platshallare import platshallarfel, faltid_fel


def test_nummer_raknar_alla_platshallare_utan_att_citera():
    fel = platshallarfel(1, 'Text {roll:FfR} och {Anna Svensson} samt {tal:OKAND} och {tal:KAND}.', [], {'KAND': '20 %'})
    for nr in (2, 3, 4):
        assert any(f'platshållare nummer {nr}' in f for f in fel)
    assert all('Anna' not in f and 'KAND' not in f for f in fel)


def test_unika_faltid_numreras_i_textordning_utan_citat():
    fel = faltid_fel(2, 'P-NAMN.Anna och P-NAMN.Bertil och P-NAMN.Anna {tal:P-KUND.antal}.')
    assert len(fel) == 2
    assert all(f'fält-ID nummer {nr}' in f for nr, f in enumerate(fel, 1))
    assert all('Anna' not in f and 'Bertil' not in f for f in fel)
