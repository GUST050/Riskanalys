"""Hela HTTP-flödet med syntetiska myndighetssvar och verklig lagring."""
from datetime import date, datetime, time, timezone
import pytest
from riskanalys.foretagsdata.lagring import las_bild
from riskanalys.intag.modeller import IntagSvar
from riskanalys.intag.tjanst import profilrevision
from riskanalys.profil.modeller import Period
from riskanalys.profil.lagring import PROFILFIL
from tester.fixturer.m2 import DAG
from tester.intag.test_registerwebb import webb
from tester.intag.test_samlat_register import formular
from tester.intag.test_webb import anrop, starta
from tester.foretagsdata.test_scb import ORG
from tester.foretagsdata.test_register_bolagsverket import bv, Leverantor


def hamta_bv(s,form='AB',raw=None):
    d=bv(form);d['hamtad']=datetime.combine(DAG,time(10),timezone.utc).isoformat()
    s.bolagsverksleverantor=Leverantor(d,raw)
    return anrop(s,'registerhamta',dict(csrf=s.csrf,orgnr=ORG,bolagsverket='ja'))


def test_hamtning_och_samlad_start_med_filial_utkast_och_bokslut(webb):
    s,t=webb
    status,html,_=hamta_bv(s)
    assert status==200 and 'val_P-ORG.utlandsk_filial' in html
    assert 'name="verksamhetstext"' in html and '1234567' in html and '2024-12-31' in html
    assert 'Medelantal' in html and 'inklusive ägare' in html
    assert not t.finns()
    b=las_bild(t.mapp)
    d=formular(s,t,bokslutsperiod='ja',verksamhetstext='Vi erbjuder redovisning med digitala underlag.')
    d.update({'val_'+id:'ja' for id in b.forslag()})
    assert anrop(s,'skapa',d)[0]==200
    p=t.profil()
    assert p.uppgifter['P-ORG.utlandsk_filial'].varde is False
    assert p.uppgifter['P-BESK.verksamhet'].varde=='Vi erbjuder redovisning med digitala underlag.'
    assert p.uppgifter['P-VERK.omsattning'].varde==1234567
    assert p.uppgifter['P-VERK.omsattning'].period==Period(fran=date(2024,1,1),till=date(2024,12,31))
    assert 'Bolagsverket' in p.uppgifter['P-ORG.utlandsk_filial'].kalla
    assert 'SCB' in p.uppgifter['P-ORG.namn'].kalla
    assert not p.ar_bekraftad('P-ORG.personantal')
    assert anrop(s,'register')[0]==200


def test_bokslut_kraver_periodbekraftelse_utan_halv_sparning(webb):
    s,t=webb;starta(s);hamta_bv(s)
    before=(t.mapp/PROFILFIL).read_bytes()
    d=formular(s,t,**{'val_P-ORG.namn':'ja','val_P-VERK.omsattning':'ja'})
    status,html,_=anrop(s,'registersamlat',d)
    assert status==400 and 'period' in html.lower()
    assert (t.mapp/PROFILFIL).read_bytes()==before
    d['bokslutsperiod']='ja'
    assert anrop(s,'registersamlat',d)[0]==200
    assert 'SHA256' in t.profil().uppgifter['P-VERK.omsattning'].kalla


def test_annan_bekraftad_kundperiod_stoppar_omsattning_aven_vid_forfalskat_post(webb):
    s,t=webb;starta(s);hamta_bv(s)
    t.spara(IntagSvar(falt='P-KUND.antal_aktiva',text='20',kalla='Kundlista',roll='Test',datum=DAG,
        period=Period(fran=date(2023,1,1),till=date(2023,12,31))),profilrevision(t.profil()))
    html=anrop(s,'register')[1]
    assert 'name="val_P-VERK.omsattning"' not in html
    assert 'period' in html.lower()
    before=(t.mapp/PROFILFIL).read_bytes()
    d=formular(s,t,bokslutsperiod='ja',**{'val_P-VERK.omsattning':'ja'})
    assert anrop(s,'registersamlat',d)[0]==400
    assert (t.mapp/PROFILFIL).read_bytes()==before


def test_omarkerad_filial_kraver_eget_underlag_och_frammande_form_gissas_inte(webb):
    s,t=webb;hamta_bv(s,form='HB')
    assert 'val_P-ORG.utlandsk_filial' not in anrop(s,'register')[1]
    d=formular(s,t,filial='nej',**{'val_P-ORG.sateslan':'ja'})
    assert anrop(s,'skapa',d)[0]==400 and not t.finns()
    d['filialkalla']='Eget kontrollerat underlag'
    assert anrop(s,'skapa',d)[0]==200


def test_bokslutsfel_synligt_men_grundforslag_anvandbara(webb):
    s,t=webb
    status,html,_=hamta_bv(s,raw=b'ej zip')
    assert status==200 and 'säkert omsättningsförslag' in html
    assert 'name="val_P-VERK.omsattning"' not in html
    assert 'name="val_P-ORG.utlandsk_filial"' in html


def test_bolagsverkskalla_ateranvands_inte_for_andra_verksamhetsfakta(webb):
    from riskanalys.intag.underlag import tidigare_underlag
    s,t=webb;starta(s);hamta_bv(s)
    d=formular(s,t,verksamhetstext='Syntetisk byrå',**{'val_P-BESK.verksamhet':'ja'})
    assert anrop(s,'registersamlat',d)[0]==200
    assert not tidigare_underlag(t.rb,t.profil(),t.rb.falt['P-BESK.kundtyper'])


def test_personalstod_visas_i_den_faktiska_personantalfragan(webb):
    s,t=webb;starta(s);hamta_bv(s)
    html=anrop(s,'?falt=P-ORG.antal_anstallda')[1]
    assert 'Medelantal anställda i årsredovisningen: 7' in html
    assert 'inte dagens antal personer inklusive ägare' in html
    assert not t.profil().ar_bekraftad('P-ORG.antal_anstallda')


def test_start_forevaljer_bolagsverket_nar_nycklar_ar_konfigurerade(webb,monkeypatch):
    import re
    s,t=webb
    monkeypatch.setenv('BOLAGSVERKET_CLIENT_ID','syntetiskt-id')
    monkeypatch.setenv('BOLAGSVERKET_CLIENT_SECRET','syntetisk-hemlighet')
    html=anrop(s)[1]
    assert 'checked' in re.search(r'<input[^>]*name="bolagsverket"[^>]*>',html).group()
    assert 'syntetisk-hemlighet' not in html


def test_bokslutsperiod_foreslas_for_kunder_och_senare_avvikelse_avvisas(webb):
    from riskanalys.intag.underlag import periodforslag
    s,t=webb;starta(s);hamta_bv(s)
    d=formular(s,t,bokslutsperiod='ja',**{'val_P-VERK.omsattning':'ja'})
    assert anrop(s,'registersamlat',d)[0]==200
    p=t.profil()
    assert periodforslag(t.rb,p,t.rb.falt['P-KUND.antal_aktiva'])==Period(fran=date(2024,1,1),till=date(2024,12,31))
    before=(t.mapp/PROFILFIL).read_bytes()
    d=dict(csrf=s.csrf,revision=profilrevision(p),falt='P-KUND.antal_aktiva',text='20',kalla='Kundlista',roll='Test',datum=str(DAG),status='bekräftad',period_fran='2023-01-01',period_till='2023-12-31')
    assert anrop(s,'svar',d)[0]==400
    assert (t.mapp/PROFILFIL).read_bytes()==before
    d.update(period_fran='2024-01-01',period_till='2024-12-31')
    assert anrop(s,'svar',d)[0]==200
