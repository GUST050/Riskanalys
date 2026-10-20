"""D-ARB.9 och omfattningsmotiveringen i v6, endast med syntetiska uppgifter.

D-ARB.9 sammanställer byråns lokala slutsats och rutinåtgärder per tjänst. Programmet beslutar
inga åtgärder, och inget i avsnittet skickas till AI.
"""
from riskanalys.analys import modeller as m
from riskanalys.analys.provning import registrera_beslut, svarssumma, underlagssumma
from riskanalys.dokument.arb_v6 import bygg_arb_v6
from riskanalys.dokument.rendering import har_verifiera
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.granskning.dokument_v6 import analysfynd_v6
from tester.enhet.test_arb_v6 import v6underlag  # noqa: F401  pytest-fixtur
from tester.enhet.test_lokalt_dokument_v6 import lokal  # noqa: F401  pytest-fixtur

VERIFIERA = '[VERIFIERA]'
OMRADEN = ('rutiner', 'kundkännedom', 'övervakning', 'utbildning')
ALLA_OMRADEN = 'Kundkännedom, övervakning och utbildning anpassas efter tjänstens scenarier.'


def foljder(d):
    return d.avsnitt_med_id()['D-ARB.9']


def tjanststycke(d, avsnitt_id):
    return next(s for s in foljder(d).stycken if avsnitt_id in s.referenser)


def forsta_avsnitt(underlag):
    return tjanster_med_avsnitt(underlag[2])[0][0]


def med_tjanst(paket, index, **andringar):
    tjanster = list(paket.tjanster)
    tjanster[index] = tjanster[index].model_copy(update=andringar)
    return paket.model_copy(update={'tjanster': tuple(tjanster)})


def med_alla_omraden(paket):
    for i, t in enumerate(paket.tjanster):
        paket = med_tjanst(paket, i, slutsats=t.slutsats + ' ' + ALLA_OMRADEN)
    return paket


def godkand(paket):
    for t in paket.tjanster:
        paket = registrera_beslut(paket, m.Analysbeslut(tjanst=t.tjanst, revision=paket.revision,
            underlagssumma=underlagssumma(paket), svarssumma=svarssumma(paket), godkand=True,
            namn='Syntetisk godkännare', roll='FfR', datum=paket.bindning.bedomningsdatum))
    return paket


def test_saknad_analys_ger_synlig_komplettering_for_alla_omraden(v6underlag):
    d = bygg_arb_v6(*v6underlag, analys=None)
    text = ' '.join(s.text for s in foljder(d).stycken)
    assert VERIFIERA in text
    assert all(o in text.lower() for o in OMRADEN)
    assert har_verifiera(foljder(d), v6underlag[1])


def test_foljder_ligger_efter_tjansterna_med_sammanhangande_visningsnummer(v6underlag, lokal):
    d = bygg_arb_v6(*v6underlag, analys=lokal)
    ids = [a.id for a in d.avsnitt]
    sista_tjanst = max(i for i, id in enumerate(ids) if id.startswith('D-ARB.6.'))
    assert ids[sista_tjanst + 1:sista_tjanst + 3] == ['D-ARB.9', 'D-ARB.10']
    assert [a.visningsnummer for a in d.avsnitt[:-1]] == [str(n) for n in range(1, len(d.avsnitt))]
    assert d.avsnitt[-1].visningsnummer == 'B1'
    assert foljder(d).kalla == 'lokal' and not foljder(d).underrubriker
    assert all(s.proveniens == 'lokal' for s in foljder(d).stycken)


def test_omrade_som_inte_tas_upp_ger_verifiera(v6underlag, lokal):
    paket = godkand(med_tjanst(lokal, 0, slutsats='Kundkännedom och övervakning skärps vid nya betalningsled.'))
    text = tjanststycke(bygg_arb_v6(*v6underlag, analys=paket), forsta_avsnitt(v6underlag)).text
    assert 'Kundkännedom och övervakning: tas upp i slutsatsen.' in text
    assert 'Utbildning: saknas i slutsats och rutinåtgärder; komplettera. [VERIFIERA]' in text


def test_omrade_kan_tas_upp_i_rutinatgard_med_bojd_form(v6underlag, lokal):
    t = lokal.tjanster[0]
    atgard = t.rutinatgarder[0].model_copy(update={'atgard': 'Utbilda personalen i övervakningen av leveransunderlag.'})
    paket = godkand(med_tjanst(lokal, 0, slutsats='Kundkännedomen förstärks.', rutinatgarder=(atgard,)))
    text = tjanststycke(bygg_arb_v6(*v6underlag, analys=paket), forsta_avsnitt(v6underlag)).text
    assert 'Kundkännedom: tas upp i slutsatsen.' in text
    assert 'Övervakning och utbildning: tas upp i beslutad åtgärd.' in text
    assert VERIFIERA not in text


def test_godkand_analys_som_tar_upp_alla_omraden_ger_ingen_markering(v6underlag, lokal):
    d = bygg_arb_v6(*v6underlag, analys=godkand(med_alla_omraden(lokal)))
    assert not har_verifiera(foljder(d), v6underlag[1])
    text = ' '.join(s.text for s in foljder(d).stycken).lower()
    assert all(o in text for o in OMRADEN)


def test_ej_godkand_analys_ger_verifiera_men_visar_utkastet(v6underlag, lokal):
    d = bygg_arb_v6(*v6underlag, analys=med_alla_omraden(lokal))
    text = tjanststycke(d, forsta_avsnitt(v6underlag)).text
    assert 'Godkännande saknas. [VERIFIERA]' in text
    assert 'RUT-FAKTURA version 2' in text


def test_foreslagen_beslutad_och_genomford_halls_isar(v6underlag, lokal):
    t = lokal.tjanster[0]
    beslutad = t.rutinatgarder[0]
    foreslagen = beslutad.model_copy(update={'id': 'forslag', 'status': 'foreslagen', 'rutin_id': None,
        'rutin_version': None, 'rutinbelagg': None, 'ansvar': None, 'uppfoljning': None, 'belagg': ()})
    genomford = beslutad.model_copy(update={'id': 'genomford', 'status': 'genomford', 'rutin_version': '3'})
    paket = godkand(med_alla_omraden(med_tjanst(lokal, 0, rutinatgarder=(genomford, foreslagen, beslutad))))
    text = tjanststycke(bygg_arb_v6(*v6underlag, analys=paket), forsta_avsnitt(v6underlag)).text
    assert ('Rutiner: föreslagen åtgärd, rutin saknas; beslutad åtgärd, rutin RUT-FAKTURA version 2; '
            'genomförd åtgärd, rutin RUT-FAKTURA version 3.') in text
    ensam = godkand(med_alla_omraden(med_tjanst(lokal, 0, rutinatgarder=(foreslagen,))))
    text = tjanststycke(bygg_arb_v6(*v6underlag, analys=ensam), forsta_avsnitt(v6underlag)).text
    assert 'föreslagen åtgärd, rutin saknas' in text
    assert 'genomförd' not in text and 'beslutad' not in text


def test_saknad_rutinatgard_och_saknad_tjansteanalys_ger_verifiera(v6underlag, lokal):
    utan = med_tjanst(med_alla_omraden(lokal), 0, rutinatgarder=())
    text = tjanststycke(bygg_arb_v6(*v6underlag, analys=utan), forsta_avsnitt(v6underlag)).text
    assert 'Rutiner: ingen rutinåtgärd; komplettera. [VERIFIERA]' in text
    saknas = lokal.model_copy(update={'tjanster': lokal.tjanster[1:]})
    text = tjanststycke(bygg_arb_v6(*v6underlag, analys=saknas), forsta_avsnitt(v6underlag)).text
    assert 'Tjänsteanalys saknas' in text and VERIFIERA in text


def test_lika_foljder_samlas_med_alla_tjansters_hanvisningar(v6underlag, lokal):
    d = bygg_arb_v6(*v6underlag, analys=godkand(med_alla_omraden(lokal)))
    ovriga = [id for id, _ in tjanster_med_avsnitt(v6underlag[2])][1:]
    delade = [s for s in foljder(d).stycken if set(ovriga) <= set(s.referenser)]
    assert len(delade) == 1
    for _, t in tjanster_med_avsnitt(v6underlag[2])[1:]:
        assert v6underlag[0].tjanster[t.tjanst].namn in delade[0].text


def test_foljder_ar_deterministiska_och_granskas_mot_aterbyggnad(v6underlag, lokal):
    rb, p, b, resultat, h = v6underlag
    d = bygg_arb_v6(rb, p, b, resultat, h, analys=lokal)
    assert bygg_arb_v6(rb, p, b, resultat, h, analys=lokal) == d
    assert not any(f['avsnitt'] == 'D-ARB.9' for f in analysfynd_v6(rb, b, p, d, h, resultat, analys=lokal))
    a = foljder(d)
    stycken = (*a.stycken[:-1], a.stycken[-1].model_copy(update={'text': 'Alla åtgärder är genomförda.'}))
    andrad = d.model_copy(update={'avsnitt': tuple(a.model_copy(update={'stycken': stycken}) if x.id == a.id else x
                                                   for x in d.avsnitt)})
    assert any(f['avsnitt'] == 'D-ARB.9' and f['allvar'] == 'blockerande'
               for f in analysfynd_v6(rb, b, p, andrad, h, resultat, analys=lokal))


def test_metod_motiverar_omfattning_efter_storlek_och_art(v6underlag):
    rb, p, b, resultat, h = v6underlag
    d = bygg_arb_v6(rb, p, b, resultat, h, analys=None)
    s = next(s for s in d.avsnitt_med_id()['D-ARB.2'].stycken if s.text.startswith('Vald omfattning enligt metod:'))
    assert 'Storlek: ' in s.text and 'Art: ' in s.text and 'Byråns motivering: ' in s.text
    assert {'P-ORG.antal_anstallda', 'P-ORG.verksamhetsstallen', 'P-VERK.omsattning', 'P-OMFATTNING.motivering',
            rb.metod.omfattning.id} <= set(s.referenser)
    for _, t in tjanster_med_avsnitt(b):
        assert rb.tjanster[t.tjanst].namn in s.text
    assert VERIFIERA not in s.text
    b1 = ' '.join(x.text for x in d.avsnitt_med_id()['D-ARB.B1'].stycken)
    assert rb.metod.omfattning.forklaring in b1


def test_okand_storlek_ger_verifiera_i_metodens_omfattning(v6underlag):
    from riskanalys.bedomning.motor import bedom
    from riskanalys.dokument.klartext import faltnamn
    from riskanalys.regelverk.urval import valj
    rb, p, b, resultat, h = v6underlag
    u = p.uppgifter['P-ORG.antal_anstallda'].model_copy(update={'status': 'saknas'})
    p = p.model_copy(update={'uppgifter': {**p.uppgifter, 'P-ORG.antal_anstallda': u}})
    b = bedom(rb, valj(rb, p.byra.regelpaket, b.datum, p.byra.lan), p)
    assert 'P-ORG.antal_anstallda' in b.proportionalitet.okanda_uppgifter
    d = bygg_arb_v6(rb, p, b, {}, h, analys=None, formatversion='D-ARB-tjanst-v6')
    s = next(s for s in d.avsnitt_med_id()['D-ARB.2'].stycken if s.text.startswith('Vald omfattning enligt metod:'))
    assert VERIFIERA in s.text and 'Uppgifter saknas: ' + faltnamn(rb, 'P-ORG.antal_anstallda') in s.text
