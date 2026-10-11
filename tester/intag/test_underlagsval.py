"""Underlag väljs uttryckligt, hålls åtskilda och sparas genom ordinarie HTTP-flöde."""
import re
import pytest
from riskanalys.intag.modeller import IntagSvar
from riskanalys.intag.tjanst import profilrevision
from riskanalys.profil.modeller import Period
from riskanalys.profil.lagring import PROFILFIL
from tester.fixturer.m2 import DAG
from tester.intag.test_webb import webb, anrop, starta


def svar(s,t,id,text,**extra):
    return dict(csrf=s.csrf,revision=profilrevision(t.profil()),falt=id,text=text,
                status='bekräftad',kalla='',roll='Test',datum=str(DAG),**extra)


def lagg(t,id,text,kalla,period=None):
    t.spara(IntagSvar(falt=id,text=text,kalla=kalla,roll='Test',datum=DAG,period=period),profilrevision(t.profil()))


def underlagstoken(html):
    return re.search(r'<option value="(tidigare:[^"]+)"',html)[1]


def test_egen_kannedom_kan_valjas_utan_att_skriva_kalltext(webb):
    s,t=webb;starta(s)
    status,html,_=anrop(s,'svar',svar(s,t,'P-ORG.namn','Syntetisk byrå',underlag='egen_kannedom'))
    assert status==200,html
    u=t.profil().uppgifter['P-ORG.namn']
    assert u.kalla=='Egen kännedom om verksamheten' and u.bekraftad_av=='roll:Test'
    assert u.datum==DAG and u.status=='bekräftad'
    assert 'Egen kännedom om verksamheten' in anrop(s,'?falt=P-VERK.bokforing')[1]


@pytest.mark.parametrize('id,text,extra',[
    ('P-ORG.antal_anstallda','4',{}),
    ('P-KUND.antal_aktiva','10',dict(period_fran='2026-01-01',period_till=str(DAG))),
    ('P-KONTROLL.C-07.utformning','finns',{}),
    ('P-KONTROLL.C-07.genomforande','belagt',{}),
])
def test_egen_kannedom_ar_inte_snabbval_for_statistik_eller_kontroll(webb,id,text,extra):
    s,t=webb;starta(s);before=(t.mapp/PROFILFIL).read_bytes()
    d=svar(s,t,id,text,underlag='egen_kannedom',**extra);d['kalla']='Syntetiskt underlag'
    status,html,_=anrop(s,'svar',d)
    assert status==400 and 'underlag' in html.lower()
    assert (t.mapp/PROFILFIL).read_bytes()==before


def test_kundunderlag_och_period_ateranvands_synligt(webb):
    s,t=webb;starta(s);period=Period(fran=DAG.replace(month=1,day=1),till=DAG)
    lagg(t,'P-KUND.antal_aktiva','10','Syntetiskt kundregister',period)
    html=anrop(s,'?falt=P-KUND.antal_kontant')[1]
    token=underlagstoken(html)
    assert 'value="2026-01-01"' in html and f'value="{DAG}"' in html
    assert 'Syntetiskt kundregister' in html
    d=svar(s,t,'P-KUND.antal_kontant','2',underlag=token,period_fran='2026-01-01',period_till=str(DAG))
    assert anrop(s,'svar',d)[0]==200
    u=t.profil().uppgifter['P-KUND.antal_kontant']
    assert u.kalla=='Syntetiskt kundregister' and u.period==period and u.varde==2
    # Kundregister får inte föreslås som bokföringsunderlag för omsättning.
    assert 'Syntetiskt kundregister' not in anrop(s,'?falt=P-VERK.omsattning')[1]


def test_valt_underlag_maste_matcha_period_och_frageslag(webb):
    s,t=webb;starta(s);period=Period(fran=DAG.replace(month=1,day=1),till=DAG)
    lagg(t,'P-KUND.antal_aktiva','10','Syntetiskt kundregister',period)
    token=underlagstoken(anrop(s,'?falt=P-KUND.antal_kontant')[1])
    before=(t.mapp/PROFILFIL).read_bytes()
    for id,fran in [('P-KUND.antal_kontant','2026-02-01'),('P-VERK.omsattning','2026-01-01')]:
        d=svar(s,t,id,'2',underlag=token,period_fran=fran,period_till=str(DAG));d['kalla']='En text får inte kringgå urvalet'
        assert anrop(s,'svar',d)[0]==400
        assert (t.mapp/PROFILFIL).read_bytes()==before


def test_okant_underlagsval_avvisas_och_gammal_flik_stoppar(webb):
    s,t=webb;starta(s);d=svar(s,t,'P-ORG.namn','Syntetisk',underlag='hittat_pa');d['kalla']='Test'
    before=(t.mapp/PROFILFIL).read_bytes()
    assert anrop(s,'svar',d)[0]==400
    assert (t.mapp/PROFILFIL).read_bytes()==before
    d['underlag']='egen_kannedom'
    assert anrop(s,'svar',d)[0]==200
    assert anrop(s,'svar',d)[0]==409


def test_okant_svar_kraver_inte_en_kalla_och_bekraftas_inte(webb):
    s,t=webb;starta(s)
    d=svar(s,t,'P-ORG.namn','',underlag='eget',motivering='Kontrolleras med ansvarig');d['status']='okänt'
    assert anrop(s,'svar',d)[0]==200
    assert not t.profil().ar_bekraftad('P-ORG.namn')


def test_tjansteutbud_kan_bekraftas_med_egen_kannedom(webb):
    s,t=webb;starta(s)
    d=dict(csrf=s.csrf,revision=profilrevision(t.profil()),hela_listan='ja',underlag='egen_kannedom',kalla='',roll='Test',datum=str(DAG),**{'tjanst_P-TJ.red01_erbjuds':'ja'})
    status,html,_=anrop(s,'tjanster',d)
    assert status==200,html
    assert t.profil().uppgifter['P-TJ.red01_erbjuds'].kalla=='Egen kännedom om verksamheten'
    assert t.profil().uppgifter['P-TJ.red02_erbjuds'].varde is False


def test_intaget_forklarar_wordleveransen_innan_skrivning(webb):
    s,t=webb
    for html in (anrop(s)[1],):
        assert 'Allmän riskbedömning' in html and 'Word-utkast' in html
        assert 'Rutindokument och individuella kundbedömningar' in html
    starta(s)
    html=anrop(s,'?oversikt=1')[1]
    assert 'Allmän riskbedömning' in html and 'Rutindokument och individuella kundbedömningar' in html
