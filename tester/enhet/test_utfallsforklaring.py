"""Sparade motorutfall förklaras utan ny bedömning."""
from riskanalys.bedomning.modeller import Tjanstbedomning, Riskdel, Kontrollbedomning
from riskanalys.dokument import nivatext


def resultat(**andringar):
    data = dict(tjanst='T-1', erbjuds=True, status='slutlig', hot=('H-1',),
                tillampade_sarbarheter=('S-1',),
                inneboende=Riskdel(sannolikhet='hög', konsekvens='betydande', risk='hög'),
                terrorfinansiering=Riskdel(sannolikhet='låg', konsekvens='allvarlig', risk='måttlig'),
                kontroller=(Kontrollbedomning(id='C-1', utformning='finns', genomforande='belagt', fungerar_och_ar_belagd=True),),
                kvarstaende='måttlig', regelspar=('BT-SANN-01', 'BT-KONS-01', 'BT-MATRIS-08', 'BT-TF-01', 'BT-MATRIS-03', 'BT-KVAR-02'),
                okanda_uppgifter=())
    return Tjanstbedomning(**(data | andringar))


def test_sparad_hojning_tak_konsekvens_och_faktisk_reduktion(minimal_regelbas):
    assert hasattr(nivatext, 'utfallsforklaring'), 'Lokal utfallsförklaring saknas'
    t = resultat()
    tabell = nivatext.utfallsforklaring(t, minimal_regelbas)
    assert len(tabell.rader) == 3
    pt = ' '.join(c.text for c in tabell.rader[0].celler)
    for text in ('medel', 'Testsårbarhet', '+1', 'tak hög', 'betydande', 'hög → måttlig', '1 steg', 'inte'):
        assert text in pt
    tf = ' '.join(c.text for c in tabell.rader[1].celler)
    assert 'allvarlig' in tf and 'låg' in tf and 'måttlig' in tf
    assert 'C-1' in tabell.rader[0].celler[1].referenser
    assert resultat() == t


def test_okant_eller_saknat_spar_ger_begransning_och_bevarar_utfall(minimal_regelbas):
    assert hasattr(nivatext, 'utfallsforklaring')
    for spar in ((), ('BT-OKAND',)):
        tabell = nivatext.utfallsforklaring(resultat(regelspar=spar), minimal_regelbas)
        text = ' '.join(c.text for r in tabell.rader for c in r.celler)
        assert 'Begränsning:' in text and 'hög → måttlig' in text
        refs = {ref for r in tabell.rader for c in r.celler for ref in c.referenser}
        assert set(spar) <= refs


def test_sanktioner_behover_eget_fullstandigt_spar(minimal_regelbas):
    from riskanalys.bedomning.modeller import Sanktionsbedomning
    from riskanalys.regelverk.modeller import Sanktionsmetod
    metod = Sanktionsmetod(id='BT-SANK', grund_sannolikhet='låg', grund_konsekvens='allvarlig', kontroll='C-1',
                          rader=(), forklaring='Syntetisk metod', kallor=('SRC-1',))
    rb = minimal_regelbas.model_copy(update={'sanktionsmetod': metod})
    sank = Sanktionsbedomning(status='slutlig', inneboende=Riskdel(sannolikhet='låg', konsekvens='allvarlig', risk='måttlig'),
                              kvarstaende='låg', regelspar=('BT-SANK',), okanda_uppgifter=())
    tabell = nivatext.utfallsforklaring(resultat(sanktionsrisk=sank), rb)
    assert 'Begränsning:' in tabell.rader[2].celler[1].text
    assert 'måttlig → låg' in tabell.rader[2].celler[2].text
    sank = sank.model_copy(update={'regelspar': ('BT-SANK', 'BT-MATRIS-03', 'C-1'), 'kontroll': resultat().kontroller[0]})
    tabell = nivatext.utfallsforklaring(resultat(sanktionsrisk=sank), rb)
    assert 'Begränsning:' not in tabell.rader[2].celler[1].text
    assert '1 steg' in tabell.rader[2].celler[2].text
