"""H6: presentation får inte byta riskutfall eller dölja underlagsbrister."""
import pytest
from riskanalys.dokument.arb import bygg_arb
from riskanalys.dokument.arb_v5 import bygg_arb_v5
from riskanalys.dokument.delskrivning import skriv_tjanst
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.promptar import DELAR
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.bedomning.motor import bedom
from riskanalys.drift.historik import Historik, Handelse
from riskanalys.profil.hantering import skapa_profil
from riskanalys.profil.modeller import Byra
from riskanalys.regelverk.urval import valj
from tester.fixturer.m2 import DAG, komplett_profil, godkant_delsvar

@pytest.fixture
def h6(regelbas_v1):
    rb=regelbas_v1
    p=komplett_profil(rb,skapa_profil(rb,Byra(id='h6',regelpaket='RP-RED-VG',lan='Västra Götaland',datum=DAG)))
    u=valj(rb,p.byra.regelpaket,DAG,p.byra.lan); b=bedom(rb,u,p)
    resultat={a:skriv_tjanst(Testleverantor([godkant_delsvar(d,t) for d in DELAR]),rb,p,t,a,
                  design='B',effort='high',personnamn=(),spara=lambda *args:None, formatversion="D-ARB-tjanst-v5") for a,t in tjanster_med_avsnitt(b)}
    hist=Historik().med(Handelse(datum=DAG,typ='utvärdering',beskrivning='Syntetiskt H6-prov'))
    return rb,p,u,b,resultat,hist,bygg_arb_v5(rb,p,b,resultat,hist)

def test_h6_risk_tabell_bevarar_alla_motorutfall(h6):
    rb,p,u,b,r,h,d=h6
    assert d.formatversion=='D-ARB-tjanst-v5'
    tab=d.avsnitt_med_id()['D-ARB.8'].tabeller[0]
    for t,row in zip([t for t in b.tjanster if t.inneboende],tab.rader,strict=True):
        assert row.celler[0].text.startswith(rb.tjanster[t.tjanst].namn)
        for index,value in [(1,t.inneboende.risk),(2,t.kvarstaende),(3,t.terrorfinansiering.risk)]:
            assert row.celler[index].text.split(' Källor:')[0]==value

def test_h6_kontroll_beskrivs_en_gang_och_bilaga_finns(h6):
    *_,d=h6
    assert 'D-ARB.B1' in d.avsnitt_med_id()
    controls=d.avsnitt_med_id()['D-ARB.7'].tabeller[0]
    names=[r.celler[0].text for r in controls.rader]
    assert len(names)==len(set(names))
    assert all(a.visningsnummer for a in d.avsnitt)
    assert d.avsnitt_med_id()['D-ARB.9'].tabeller

def test_h6_nybyggt_dokument_ger_inga_falska_analysfynd(h6):
    from riskanalys.granskning.kontroller import granska
    rb,p,u,b,r,h,d=h6
    fynd=granska(rb,u,p,b,d,h,DAG,skrivresultat=r)
    assert not [f for f in fynd if f.allvar=='blockerande'],fynd

@pytest.mark.parametrize('id',['D-ARB.7','D-ARB.8','D-ARB.6.1'])
def test_h6_andrad_tabell_blockeras_trots_samma_profil(h6,id):
    from riskanalys.granskning.kontroller import granska
    rb,p,u,b,r,h,d=h6
    a=d.avsnitt_med_id()[id]; tab=a.tabeller[0]; row=tab.rader[0]
    cell=row.celler[0].model_copy(update={'text':'Felaktigt påstående'})
    row=row.model_copy(update={'celler':(cell,*row.celler[1:])})
    tab=tab.model_copy(update={'rader':(row,*tab.rader[1:])})
    a=a.model_copy(update={'tabeller':(tab,*a.tabeller[1:])})
    changed=d.model_copy(update={'avsnitt':tuple(a if x.id==id else x for x in d.avsnitt)})
    fynd=granska(rb,u,p,b,changed,h,DAG,skrivresultat=r)
    assert any(f.allvar=='blockerande' and f.avsnitt==id for f in fynd)

def test_h6_cli_visar_tabellceller_och_kallreferenser(h6):
    from riskanalys.kommandon.sakgranska_kommando import beskriv_avsnitt
    d=h6[-1]; a=d.avsnitt_med_id()['D-ARB.8']
    text=beskriv_avsnitt(a)
    for tab in a.tabeller:
        assert tab.rubrik in text
        for r in tab.rader:
            assert all(c.text in text for c in r.celler)
    assert 'Hänvisningar:' in text

def test_h6_sektorsreferensen_redovisas_pa_egen_skala(h6):
    d=h6[-1]
    assert any('Källans skala är separat' in s.text for s in d.avsnitt_med_id()['D-ARB.2'].stycken)


def test_h6_identiska_geografivillkor_samlas_en_gang(h6):
    d=h6[-1]
    tabeller=[t for a in d.avsnitt for t in a.tabeller if 'geografi' in t.id]
    signaturer=[(t.kolumner,t.rader) for t in tabeller]
    assert len(signaturer)==len(set(signaturer))


def test_h6_preliminar_bedomning_bevarar_komplettering_i_atgardsdelen(h6):
    rb,p,u,b,r,h,d=h6
    ny=bygg_arb_v5(rb,p,b.model_copy(update={'status':'preliminär'}),r,h)
    assert any('[VERIFIERA]' in s.text for s in ny.avsnitt_med_id()['D-ARB.9'].stycken)


def test_h6_oversikt_bevarar_liten_tjanst_och_okant_utfall(h6):
    from riskanalys.dokument.tabeller import bygg_riskoversikt,bygg_tjansteoversikt
    rb,p,u,b,*_=h6
    aktiva=[t for t in b.tjanster if t.inneboende]
    liten=next(t for t in b.tjanster if t.tjanst=='T-RED-04').model_copy(update={
        'erbjuds':True,'inneboende':aktiva[0].inneboende,'kvarstaende':'hög',
        'terrorfinansiering':aktiva[0].terrorfinansiering})
    b=b.model_copy(update={'tjanster':(*aktiva,liten)})
    tab=bygg_riskoversikt(b,rb)
    assert len(tab.rader)==4 and tab.rader[-1].celler[2].text=='hög'
    # Omfattning är rader per tjänst, utan en summerad kundrad.
    omfattning=bygg_tjansteoversikt(rb,p,b)
    assert len(omfattning.rader)==4
    okand=liten.model_copy(update={'erbjuds':None,'inneboende':None,'kvarstaende':None,'terrorfinansiering':None})
    tab=bygg_riskoversikt(b.model_copy(update={'tjanster':(okand,)}),rb)
    assert tab.rader[0].celler[1].text=='Ej bedömt'
    assert bygg_riskoversikt(b.model_copy(update={'tjanster':()}),rb).rader==()


def test_h6_gemensam_kontroll_bevarar_skild_effekt_per_tjanst(h6):
    from riskanalys.dokument.tabeller import bygg_kontrolloversikt
    rb,p,u,b,*_=h6
    t1,t2=[t for t in b.tjanster if t.inneboende][:2]
    k=t1.kontroller[0].model_copy(update={'effekt':'verksam','fungerar_och_ar_belagd':True})
    svag=k.model_copy(update={'effekt':'begränsad','fungerar_och_ar_belagd':False})
    b=b.model_copy(update={'tjanster':(t1.model_copy(update={'kontroller':(k,)}),t2.model_copy(update={'kontroller':(svag,)}))})
    tab=bygg_kontrolloversikt(b,rb,p)
    row=next(r for r in tab.rader if r.celler[0].referenser==(k.id,))
    status=row.celler[2].text
    assert 'effekt: verksam' in status and 'effekt: begränsad' in status
    assert rb.tjanster[t1.tjanst].namn in status and rb.tjanster[t2.tjanst].namn in status
    assert sum(r.celler[0].referenser==(k.id,) for r in tab.rader)==1


def test_h6_noll_rapporter_och_saknat_erfarenhetsbelagg_halls_isar(h6):
    from riskanalys.dokument.arb_v5 import egen_erfarenhet_kort
    from riskanalys.regelverk.granser import metodgransindex
    rb,p,u,b,*_=h6
    t=next(t for t in b.tjanster if t.inneboende)
    e=t.egen_erfarenhet.model_copy(update={'rapporter':'inga'})
    text=egen_erfarenhet_kort(rb,p,t.model_copy(update={'egen_erfarenhet':e}),metodgransindex(rb)).text
    assert 'Noll rapporter visar inte frånvaro av hot' in text
    text=egen_erfarenhet_kort(rb,p,t.model_copy(update={'egen_erfarenhet':None}),metodgransindex(rb)).text
    assert '[VERIFIERA]' in text


@pytest.mark.parametrize('suffix', ['utformning', 'genomforande', 'effekt', 'utfall'])
def test_h6_kontrolltabell_visar_nekad_verkan_nar_kallbelagg_saknas(h6, suffix):
    from riskanalys.dokument.tabeller import bygg_kontrolloversikt
    rb, p, u, b, *_ = h6
    falt = f'P-KONTROLL.C-TJ-01.{suffix}'
    p = p.model_copy(update={'uppgifter': p.uppgifter | {
        falt: p.uppgifter[falt].model_copy(update={'kalla': ''})}})
    b = bedom(rb, u, p)
    kontroll = next(k for t in b.tjanster for k in t.kontroller if k.id == 'C-TJ-01')
    assert kontroll.effekt == 'verksam'
    assert kontroll.effekt_belagd is False
    assert kontroll.fungerar_och_ar_belagd is False
    row = next(r for r in bygg_kontrolloversikt(b, rb, p).rader
               if r.celler[0].referenser == ('C-TJ-01',))
    assert 'Riskreducerande enligt metodvillkoren: nej' in row.celler[2].text
    assert '[VERIFIERA]' in row.celler[3].text
    assert falt in row.celler[3].referenser


def test_h6_kontrolltabell_visar_motorvillkor_utan_att_avgora_scenariotackning(h6):
    from riskanalys.dokument.tabeller import bygg_kontrolloversikt
    rb, p, _, b, *_ = h6
    row = next(r for r in bygg_kontrolloversikt(b, rb, p).rader
               if r.celler[0].referenser == ('C-TJ-01',))
    assert 'Riskreducerande enligt metodvillkoren: ja' in row.celler[2].text
    assert '[VERIFIERA]' not in row.celler[3].text


@pytest.mark.parametrize('andring,markering', [
    ({'status': 'saknas', 'varde': None}, 'okänt om tjänsten erbjuds'),
    ({'inaktuell': True}, 'okänt om tjänsten erbjuds'),
])
def test_h6_riskoversikt_markerar_okant_erbjudande_med_bevarade_nivaer(h6, andring, markering):
    from riskanalys.dokument.tabeller import bygg_riskoversikt
    from riskanalys.profil.modeller import Uppgift
    rb, p, u, b, *_ = h6
    falt = 'P-TJ.red01_erbjuds'
    # Validera även den ändrade uppgiften: inga påhittade statusvärden i provet.
    uppgift = Uppgift.model_validate(p.uppgifter[falt].model_dump() | andring)
    p = p.model_copy(update={'uppgifter': p.uppgifter | {falt: uppgift}})
    ny_bedomning = bedom(rb, u, p)
    t = next(t for t in ny_bedomning.tjanster if t.tjanst == 'T-RED-01')
    assert t.erbjuds is None and t.status == 'preliminär'
    fore = next(r for r in bygg_riskoversikt(b, rb).rader if r.celler[0].referenser == ('T-RED-01',))
    efter = next(r for r in bygg_riskoversikt(ny_bedomning, rb).rader if r.celler[0].referenser == ('T-RED-01',))
    assert markering in efter.celler[0].text
    assert 'preliminär' in efter.celler[0].text.lower()
    assert '[VERIFIERA]' in efter.celler[0].text
    assert efter.celler[1:] == fore.celler[1:]


def test_h6_riskoversikt_markerar_preliminara_nivaer_for_kand_tjanst(h6):
    from riskanalys.dokument.tabeller import bygg_riskoversikt
    rb, p, u, b, *_ = h6
    falt = 'P-KONTROLL.C-TJ-01.effekt'
    p = p.model_copy(update={'uppgifter': p.uppgifter | {
        falt: p.uppgifter[falt].model_copy(update={'kalla': ''})}})
    b = bedom(rb, u, p)
    t = next(t for t in b.tjanster if t.tjanst == 'T-RED-01')
    assert t.erbjuds is True and t.status == 'preliminär'
    row = next(r for r in bygg_riskoversikt(b, rb).rader if r.celler[0].referenser == ('T-RED-01',))
    assert 'preliminär' in row.celler[0].text.lower()
    assert '[VERIFIERA]' in row.celler[0].text
    assert row.celler[1].text == t.inneboende.risk
