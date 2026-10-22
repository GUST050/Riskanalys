"""Samlat godkännande genom riktig HTTP/lagring, med syntetisk SCB-transport."""
import re
import pytest
from riskanalys.fel import RiskanalysFel
from riskanalys.foretagsdata.lagring import las_bild
from riskanalys.intag.modeller import IntagSvar
from riskanalys.intag.tjanst import profilrevision
from riskanalys.profil.lagring import PROFILFIL
from tester.fixturer.m2 import DAG
from tester.intag.test_registerwebb import webb, hamta
from tester.intag.test_webb import anrop, starta

IDS=('P-ORG.sateslan','P-ORG.namn','P-ORG.verksamhetsstallen')

def test_scb_utan_koncern_ar_synligt_nejforslag_och_kraver_godkannande(webb):
    from riskanalys.foretagsdata.lagring import spara_bild
    from riskanalys.foretagsdata.scb import tolka_scb
    from tester.foretagsdata.test_scb import post, ORG
    s,t=webb
    b=tolka_scb(post(agKat='41'),ORG,'scb_api');spara_bild(t.mapp,b)
    html=anrop(s,'register')[1]
    assert 'val_P-ORG.koncernmoder' in html and 'Privat svenskt utan koncern' in html
    assert '<strong>Nej</strong>' in html and not t.finns()
    d=formular(s,t,filial='nej',filialkalla='Syntetiskt registreringsbevis',**{'val_P-ORG.sateslan':'ja'})
    assert anrop(s,'skapa',d)[0]==200
    assert not t.profil().ar_bekraftad('P-ORG.koncernmoder')
    d=formular(s,t,**{'val_P-ORG.koncernmoder':'ja'})
    assert anrop(s,'registersamlat',d)[0]==200
    u=t.profil().uppgifter['P-ORG.koncernmoder']
    assert u.varde is False and u.kalla==b.hanvisning()

def formular(s,t,**extra):
    return dict(csrf=s.csrf,bildsumma=las_bild(t.mapp).summa,ratt_byra='ja',
                roll='Uppgiftslamnare',datum=str(DAG),revision=profilrevision(t.profil()) if t.finns() else '',**extra)

def test_vald_registerstart_hoppar_over_namn_och_stallen(webb):
    s,t=webb;hamta(s)
    d=formular(s,t,filial='nej',filialkalla='Syntetiskt registreringsbevis')
    d.update({'val_'+id:'ja' for id in IDS})
    status,html,_=anrop(s,'skapa',d)
    assert status==200
    p=t.profil()
    assert all(p.ar_bekraftad(id) and not p.uppgifter[id].inaktuell for id in IDS)
    assert p.uppgifter['P-ORG.namn'].varde=='Syntetisk byrå AB'
    assert p.uppgifter['P-ORG.verksamhetsstallen'].varde==2
    assert '<h1>Vad heter byrån?' not in html
    assert las_bild(t.mapp).summa in p.uppgifter['P-ORG.namn'].kalla
    assert 'value="Uppgiftslamnare"' in html
    assert not p.ar_bekraftad('P-ORG.personantal')


def test_omarkerat_namn_bevaras_vid_start(webb):
    s,t=webb;hamta(s)
    assert anrop(s,'skapa',formular(s,t,filial='nej',filialkalla='Test',**{'val_P-ORG.sateslan':'ja'}))[0]==200
    assert not t.profil().ar_bekraftad('P-ORG.namn')


def test_samlat_kraver_aktivt_ersattningsval_och_en_skrivning(webb,monkeypatch):
    s,t=webb;starta(s);hamta(s)
    p=t.profil();before=(t.mapp/PROFILFIL).read_bytes()
    d=formular(s,t);d.update({'val_'+id:'ja' for id in IDS})
    status,html,_=anrop(s,'registersamlat',d)
    assert status==400 and 'ersätt' in html.lower()
    assert (t.mapp/PROFILFIL).read_bytes()==before
    import riskanalys.profil.forandringar as service
    real=service.spara_profil;calls=[]
    def save(*a,**kw):calls.append(1);return real(*a,**kw)
    monkeypatch.setattr(service,'spara_profil',save)
    d['ersatt_P-ORG.sateslan']='ja'
    assert anrop(s,'registersamlat',d)[0]==200
    p=t.profil()
    assert calls==[1] and p.byra.lan=='Västra Götaland'
    assert all(p.ar_bekraftad(id) and not p.uppgifter[id].inaktuell for id in IDS)
    assert anrop(s,'registersamlat',d)[0]==409


def test_fel_i_sista_batchsvaret_sparar_ingenting(webb,monkeypatch):
    s,t=webb;starta(s);hamta(s)
    before=(t.mapp/PROFILFIL).read_bytes()
    import riskanalys.intag.tjanst as service
    real=service.besvara
    def answer(rb,p,svar):
        if svar.falt=='P-ORG.verksamhetsstallen':raise RiskanalysFel('Syntetiskt valideringsfel')
        return real(rb,p,svar)
    monkeypatch.setattr(service,'besvara',answer)
    d=formular(s,t,ersatt_P='unused');d.pop('ersatt_P')
    d.update({'val_'+id:'ja' for id in IDS});d['ersatt_P-ORG.sateslan']='ja'
    assert anrop(s,'registersamlat',d)[0]==400
    assert (t.mapp/PROFILFIL).read_bytes()==before


@pytest.mark.parametrize('extra',[{}, {'val_P-ORG.personantal':'ja'}, {'val_P-ORG.namn':'nej'}])
def test_ogiltigt_urval_avvisas_utan_skrivning(webb,extra):
    s,t=webb;starta(s);hamta(s);before=(t.mapp/PROFILFIL).read_bytes()
    assert anrop(s,'registersamlat',formular(s,t,**extra))[0]==400
    assert (t.mapp/PROFILFIL).read_bytes()==before


def test_formular_visar_konflikt_omarkerad_och_forslag_i_ordinarie_fraga(webb):
    s,t=webb;starta(s);hamta(s)
    html=anrop(s,'register')[1]
    assert 'registersamlat' in html
    county=re.search(r'<input[^>]*name="val_P-ORG.sateslan"[^>]*>',html).group()
    assert 'checked' not in county
    assert 'ersatt_P-ORG.sateslan' in html
    page=anrop(s)[1]
    assert 'Syntetisk byrå AB' in page and 'Godkänn registerförslaget' in page
    assert 'value="Uppgiftslamnare"' in page
    assert 'frågor att besvara nu' in page and 'av 167' not in page


def test_nyckel_for_sessionen_utan_atergivning_eller_disk(webb,monkeypatch):
    s,t=webb
    import riskanalys.foretagsdata.scb as scb
    factory=scb.SCBLeverantor;transport=s.foretagsleverantor._transport
    keys=[]
    def provider(nyckel=None):keys.append(nyckel);return factory(nyckel=nyckel,transport=transport)
    monkeypatch.setattr(scb,'SCBLeverantor',provider)
    secret='syntetisk-session-hemlighet'
    status,html,_=anrop(s,'registerhamta',dict(csrf=s.csrf,orgnr='5599991238',nyckel=secret))
    assert status==200 and keys==[secret]
    assert secret not in html
    assert all(secret.encode() not in f.read_bytes() for f in t.mapp.rglob('*') if f.is_file())
    assert 'type="password"' in html
    status,html,_=anrop(s,'registerhamta',dict(csrf=s.csrf,orgnr='fel',nyckel=secret))
    assert status==400 and secret not in html


def test_tjanster_bekraftas_samlat_med_en_kalla_och_ratt_foljdfragor(webb):
    s,t=webb;starta(s)
    ids={x.erbjuds_falt for x in t.rb.tjanster.values()}
    before=(t.mapp/PROFILFIL).read_bytes()
    d=dict(csrf=s.csrf,revision=profilrevision(t.profil()),roll='Uppgiftslamnare',datum=str(DAG),kalla='Syntetisk genomgång av uppdragslistan',**{'tjanst_P-TJ.red01_erbjuds':'ja'})
    assert anrop(s,'tjanster',d)[0]==400
    assert (t.mapp/PROFILFIL).read_bytes()==before
    d['hela_listan']='ja'
    assert anrop(s,'tjanster',d)[0]==200
    p=t.profil()
    assert all(p.ar_bekraftad(id) for id in ids)
    assert p.uppgifter['P-TJ.red01_erbjuds'].varde is True
    assert all(p.uppgifter[id].varde is False for id in ids-{'P-TJ.red01_erbjuds'})
    from riskanalys.intag.fragor import fragor
    qs={q.falt.id for q in fragor(t.rb,p)}
    assert 'P-TJ.red01_arbetssatt' in qs and 'P-TJ.red02_arbetssatt' not in qs
    assert anrop(s,'tjanster',d)[0]==409


def test_tjanstlista_sparar_inte_falska_svar_vid_okand_markor(webb):
    s,t=webb;starta(s);before=(t.mapp/PROFILFIL).read_bytes()
    d=dict(csrf=s.csrf,revision=profilrevision(t.profil()),roll='Test',datum=str(DAG),kalla='Test',hela_listan='ja',**{'tjanst_P-ORG.personantal':'ja'})
    assert anrop(s,'tjanster',d)[0]==400
    assert (t.mapp/PROFILFIL).read_bytes()==before


def test_fraga_har_gemenskapslista_utan_att_tvinga_okanda_tjanster(webb):
    s,t=webb;starta(s)
    html=anrop(s,'?falt=P-TJ.red01_erbjuds')[1]
    assert 'Välj byråns tjänster på en sida' in html
    assert f'{s.prefix}tjanster' in html
    assert 'omarkerade tjänster inte erbjuds' in html
    assert 'besvara tjänsterna en i taget' in html


@pytest.mark.parametrize('feltyp',['revision','bild','ratt_byra','framtid','historisk'])
def test_samlat_avvisar_gamla_eller_obekraftade_underlag(webb,feltyp):
    from datetime import timedelta
    s,t=webb;starta(s);hamta(s)
    d=formular(s,t,**{'val_P-ORG.namn':'ja'})
    before=(t.mapp/PROFILFIL).read_bytes()
    if feltyp=='revision':d['revision']='gammal'
    elif feltyp=='bild':hamta(s)
    elif feltyp=='ratt_byra':d.pop('ratt_byra')
    elif feltyp=='framtid':d['datum']=str(DAG+timedelta(days=1))
    elif feltyp=='historisk':d['datum']=str(DAG-timedelta(days=1))
    assert anrop(s,'registersamlat',d)[0] in (400,409)
    assert (t.mapp/PROFILFIL).read_bytes()==before


def test_valideringsfel_vid_registerstart_skapar_inte_halv_profil(webb,monkeypatch):
    s,t=webb;hamta(s)
    import riskanalys.intag.tjanst as service
    def fail(*a,**k):raise RiskanalysFel('Syntetiskt fel efter grunduppgifter')
    monkeypatch.setattr(service,'besvara',fail)
    d=formular(s,t,filial='nej',filialkalla='Test',**{'val_P-ORG.sateslan':'ja','val_P-ORG.namn':'ja'})
    assert anrop(s,'skapa',d)[0]==400
    assert not t.finns()


def test_allt_tjansteutbud_kan_sparas_utan_att_formularet_avvisas(webb):
    s,t=webb;starta(s)
    d=dict(csrf=s.csrf,revision=profilrevision(t.profil()),hela_listan='ja',kalla='Test',roll='Test',datum=str(DAG))
    d.update({'tjanst_'+x.erbjuds_falt:'ja' for x in t.rb.tjanster.values()})
    assert anrop(s,'tjanster',d)[0]==200
    assert all(t.profil().ar_bekraftad(x.erbjuds_falt) and t.profil().uppgifter[x.erbjuds_falt].varde is True for x in t.rb.tjanster.values())


def test_natfel_behaller_bild_och_profil(webb):
    from urllib.error import HTTPError
    from io import BytesIO
    from riskanalys.foretagsdata.scb import SCBLeverantor
    s,t=webb;starta(s);hamta(s)
    before=(t.mapp/PROFILFIL).read_bytes();summa=las_bild(t.mapp).summa
    def transport(req,timeout):raise HTTPError(req.full_url,503,'hemlig',{},BytesIO(b'hemlig'))
    s.foretagsleverantor=SCBLeverantor(nyckel='hemlig',transport=transport)
    status,html,_=hamta(s)
    assert status==400 and 'hemlig' not in html
    assert las_bild(t.mapp).summa==summa and (t.mapp/PROFILFIL).read_bytes()==before


def test_registerstart_utan_val_kan_inte_bekrafta_sateslan(webb):
    s,t=webb;hamta(s)
    d=formular(s,t,filial='nej',filialkalla='Test')
    assert anrop(s,'skapa',d)[0]==400
    assert not t.finns()


def test_andrad_roll_foreslas_i_nasta_fraga(webb):
    s,t=webb;starta(s)
    d=dict(csrf=s.csrf,revision=profilrevision(t.profil()),falt='P-ORG.namn',text='Syntetisk',kalla='Test',roll='Nyaste roll',datum=str(DAG),status='bekräftad')
    assert anrop(s,'svar',d)[0]==200
    assert 'value="Nyaste roll"' in anrop(s)[1]


def test_samlad_och_enskild_tjanstfrageform_har_egna_faltetiketter(webb):
    s,t=webb;starta(s)
    html=anrop(s,'?falt=P-TJ.red01_erbjuds')[1]
    ids=re.findall(r'\bid="([^"]+)"',html)
    assert len(ids)==len(set(ids)), 'Etiketter får inte peka på det andra formulärets fält.'
