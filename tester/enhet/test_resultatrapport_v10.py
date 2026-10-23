"""Disposition, fria original och oförändrade historiska format."""
import pytest
from tester.fixturer.resultatrapport import resultatfall
from riskanalys.dokument.arb_v10 import bygg_resultatpaket_v10
from riskanalys.dokument.resultatmodell_v9 import kallartefakter, los_referens


def bygg(f, **andrat):
    return bygg_resultatpaket_v10(f.regelbas, f.profil, f.bedomning, f.resultat, f.historik,
                                analys=andrat.get('analys', f.analys))


def huvud(b):
    return tuple(a for a in b.dokument.avsnitt if a.leveransdel == 'resultatrapport')


def text(avsnitt):
    return '\n'.join([*(s.text for a in avsnitt for s in a.stycken),
                      *(c.text for a in avsnitt for t in a.tabeller for r in t.rader for c in r.celler)])


def test_hela_dispositionen_och_alla_indikatorer(resultatfall):
    b = bygg(resultatfall)
    ids = [a.id for a in huvud(b)]
    assert ids[0:2] == ['D-ARB.RF', 'D-ARB.R0']
    for prefix in ('1.1', '1.2', '1.3', '2', '2.1', '3.1', '3.8', '4.1', '4.2', '4.4', '4.5', '5.1', '5.4'):
        assert 'D-ARB.R' + prefix in ids
    faktorer = [r.celler[0].text.split()[0] for a in huvud(b) for t in a.tabeller
                if t.id.startswith('v10-faktorer-') for r in t.rader]
    assert set(faktorer) == set(resultatfall.regelbas.sarbarheter) and len(faktorer) == 33
    tabeller = {t.id: t for a in huvud(b) for t in a.tabeller}
    assert len(tabeller['v10-lagre-risk'].rader) == 5
    assert len(tabeller['v10-lagexempel'].rader) == 15
    assert 'Kan tala för lägre risk i' in tabeller['v10-lagre-risk'].kolumner
    hemvist = [r for r in tabeller['v10-lagexempel'].rader if r.celler[0].text in ('2:5 p. 5', '2:5 p. 6')]
    assert len(hemvist) == 2 and all(r.celler[2].text == 'Okänt' for r in hemvist)


def test_fulla_lokala_pt_tf_motiveringar_och_kedjor(resultatfall):
    b = bygg(resultatfall)
    txt = text(huvud(b))
    for a in resultatfall.analys.tjanster:
        assert a.pt_motivering in txt and a.tf_motivering in txt
    for s in resultatfall.analys.gemensamma_scenarier:
        if any(s.handelseforlopp in p.text for a in huvud(b) for p in a.stycken):
            assert txt.count(s.handelseforlopp) == 1


def test_alla_konstruktioner_har_giltig_kalla_och_slag(resultatfall):
    f = resultatfall
    b = bygg(f)
    kallor = kallartefakter(f.regelbas, f.profil, f.bedomning, f.resultat, f.historik, f.analys, b.analysdokument)
    assert {k.produktionsslag for k in b.konstruktioner} == {'programmall', 'regelbas', 'lokalt_original'}
    for k in b.konstruktioner:
        assert k.kallor
        for r in k.kallor:
            los_referens(kallor, r)


def test_v9_och_bilagornas_disposition_bevaras(resultatfall):
    from riskanalys.dokument.arb_v9 import bygg_resultatpaket_v9
    f = resultatfall
    fore = bygg_resultatpaket_v9(f.regelbas, f.profil, f.bedomning, f.resultat, f.historik, analys=f.analys)
    sparat = fore.model_dump_json()
    ny = bygg(f)
    old = [a for a in fore.dokument.avsnitt if a.leveransdel != 'resultatrapport']
    new = [a for a in ny.dokument.avsnitt if a.leveransdel != 'resultatrapport']
    assert [a.id for a in new] == [a.id for a in old]
    for a, b in zip(old, new, strict=True):
        assert a.model_dump(exclude={'formatversion'}) == b.model_dump(exclude={'formatversion'})
    assert fore.model_dump_json() == sparat
    assert fore.dokument.formatversion == 'D-ARB-resultat-v9'
    from riskanalys.dokument.rapportversion import AKTUELL_DOKUMENTVERSION, V9
    assert AKTUELL_DOKUMENTVERSION == V9  # offlinefasen får inte byta produktstandard


def test_metodtext_foljer_bunden_regelbas(resultatfall):
    from riskanalys.dokument.metodavsnitt_v10 import bygg_metod
    rb = resultatfall.regelbas
    tf = rb.metod.terrorfinansiering.model_copy(update={'forklaring': 'Syntetiskt ändrad TF-metod.'})
    rb2 = rb.model_copy(update={'metod': rb.metod.model_copy(update={'terrorfinansiering': tf})})
    assert 'Syntetiskt ändrad TF-metod.' in text((bygg_metod(rb2),))
    assert 'TF:s kvarstående nivå beräknas inte.' not in text(huvud(bygg(resultatfall)))


def test_langt_original_med_rollklamrar_bevaras(resultatfall):
    from riskanalys.dokument.rapportvyer_v10 import bygg_rapportvyer_v10
    from riskanalys.dokument.presentation_v10 import bygg_presentation_v10
    f = resultatfall
    lang = 'Ordagrant {roll:FfR} och fullständig motivering. ' * 150
    a = f.analys.tjanster[0].model_copy(update={'pt_motivering': lang})
    analys = f.analys.model_copy(update={'tjanster': (a, *f.analys.tjanster[1:])})
    b = bygg(f, analys=analys)
    p = bygg_presentation_v10(b, analys=analys, fynd=(), bedomning=f.bedomning, profil=f.profil)
    assert lang in text((bygg_rapportvyer_v10(b.dokument).resultatrapport.avsnitt))
    assert lang in text(p.renderade[0].avsnitt)


def test_matrisens_programhanvisning_flyttas_men_fri_text_bevaras():
    from riskanalys.dokument.resultatrapport_v9 import avsnitt, tabell, stycke
    from riskanalys.dokument.resultatrapport_v10 import _flytta
    original = 'Lokal fri text med hänvisningen R5.4.'
    a = avsnitt('D-ARB.R4', 'Matris', (stycke(original, lokal=True),), (
        tabell('v9-matris-1', 'Matris', ('Tjänst',), [[('Egen mekanism, se R5.4', ())]]),))
    ny = _flytta(a, '4.2')
    assert ny.tabeller[0].rader[0].celler[0].text == 'Egen mekanism, se 4.3.4'
    assert ny.stycken[0].text == original
