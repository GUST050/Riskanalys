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
    from riskanalys.dokument.rapportversion import AKTUELL_DOKUMENTVERSION, V10
    assert AKTUELL_DOKUMENTVERSION == V10  # användaren har godkänt PDF-förslaget


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


@pytest.mark.parametrize('tomt',[False,True])
def test_publik_byggare_anvander_v10_som_ny_standard(resultatfall,tomt):
    from riskanalys.dokument.arb import bygg_arb
    f=resultatfall
    d=bygg_arb(f.regelbas,f.profil,f.bedomning,{} if tomt else f.resultat,f.historik,analys=f.analys)
    assert d.formatversion=='D-ARB-resultat-v10'
    assert 'D-ARB.R3.8' in d.avsnitt_med_id()


def test_kombinationsgrupp_utan_kalla_ar_okant(resultatfall):
    from riskanalys.profil.modeller import Kombinationsgrupp
    from riskanalys.dokument.kapitel3_v10 import bygg_kapitel3
    f=resultatfall;u=f.profil.uppgifter['P-KUND.antal_aktiva'].model_copy(update={'kalla':None})
    g=Kombinationsgrupp(id='G1',tjanst='T-RED-04',population='kunder',avgransning='Syntetiskt urval',
        beskrivning='Båda faktorerna finns hos samma kund.',sarbarheter=('S-ARB-05','S-KUND-02'),
        antal=u.model_copy(update={'varde':1}),bas=u)
    profil=f.profil.model_copy(update={'kombinationsgrupper':(g,)})
    a=next(a for a in bygg_kapitel3(f.regelbas,profil,f.analys) if a.id=='D-ARB.R3.6')
    txt=text((a,))
    assert 'G1: Okänt' in txt and '1 av ' not in txt


def test_alla_fria_profiltexter_i_huvudrapport_ar_bokstavliga(resultatfall):
    from riskanalys.dokument.presentation_v10 import bygg_presentation_v10
    f=resultatfall;upp=dict(f.profil.uppgifter)
    for id in ('P-BESK.erfarenheter','P-ORG.namn'):
        upp[id]=upp[id].model_copy(update={'varde':'Original '+id+' med {roll:FfR} ordagrant.'})
    profil=f.profil.model_copy(update={'uppgifter':upp})
    b=bygg_resultatpaket_v10(f.regelbas,profil,f.bedomning,f.resultat,f.historik,analys=f.analys)
    p=bygg_presentation_v10(b,analys=f.analys,fynd=(),bedomning=f.bedomning,profil=profil)
    a=p.renderade[0].avsnitt_med_id()
    assert upp['P-ORG.namn'].varde in a['D-ARB.R0'].stycken[0].text
    assert upp['P-BESK.erfarenheter'].varde in text((a['D-ARB.R2.1'],))


def test_obesvarat_tjansteutbud_bevarar_preliminara_motorutfall(regelbas_v1):
    from datetime import date
    from riskanalys.profil.hantering import skapa_profil
    from riskanalys.profil.modeller import Byra
    from riskanalys.bedomning.motor import bedom
    from riskanalys.regelverk.urval import valj
    from riskanalys.drift.historik import Historik
    from riskanalys.dokument.arb import bygg_arb
    p=skapa_profil(regelbas_v1,Byra(id='syntetisk',regelpaket='RP-RED-VG',
        lan='Västra Götaland',datum=date(2026,10,23)))
    b=bedom(regelbas_v1,valj(regelbas_v1,p.byra.regelpaket,p.byra.datum,p.byra.lan),p)
    d=bygg_arb(regelbas_v1,p,b,{},Historik())
    rows=d.avsnitt_med_id()['D-ARB.R0'].tabeller[0].rader
    assert len(rows)==len(regelbas_v1.tjanster)
    bynamn={regelbas_v1.tjanster[t.tjanst].namn:t for t in b.tjanster}
    assert all(t.erbjuds is None for t in b.tjanster)
    for r in rows:
        t=bynamn[r.celler[0].text]
        assert r.celler[1].text==(t.inneboende.risk if t.inneboende else 'okänt')
        assert r.celler[-1].text==t.status=='preliminär'
