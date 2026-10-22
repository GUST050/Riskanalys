"""Verkliga spar-/förnyelse- och HTML-vägar från slutgranskningen."""
import re
import pytest
from riskanalys.analys import lagring as l,provning as p,modeller as m
from riskanalys.analys.tjanst import Analystjanst
from riskanalys.profil.lagring import profilrevision
from riskanalys.profil.modeller import Tjansteplan
from tester.intag.test_analys import analysmiljo,start
from tester.intag.test_webb import anrop
from tester.intag.test_tjansteplanering import tjanst,svar
from tester.intag.test_tjansteurval_planval import server
from tester.fixturer.m2 import DAG


def test_fornyelse_nya_tjanster_anvander_paketets_overforda_postregister(analysmiljo):
    from tester.enhet.test_analys_overforing_v2 import tva_lika
    from riskanalys.analys.gemensam import postsumma
    s,t=analysmiljo;start(s);at=Analystjanst(t.mapp,t.rb);a=l.las_analys(t.mapp)
    l.spara_analys(t.mapp,tva_lika(a),forvantad_summa=p.registersumma(a));a=l.las_analys(t.mapp)
    at.overfor(p.registersumma(a),True);fore=l.las_analys(t.mapp)
    assert any(g.id.startswith('overfort:') for g in fore.gemensamma_sarbarhetsprovningar)
    assert 'byra:kund' not in {g.id for g in fore.gemensamma_sarbarhetsprovningar}
    at.fornya(p.registersumma(fore));efter=l.las_analys(t.mapp)
    assert efter.gemensamma_sarbarhetsprovningar==fore.gemensamma_sarbarhetsprovningar
    nya=[a for a in efter.tjanster if a.tjanst not in {x.tjanst for x in fore.tjanster}];assert nya
    for a in nya:
        for appar,poster in ((a.sarbarhetstillampningar,efter.gemensamma_sarbarhetsprovningar),(a.verksamhetstillampningar,efter.gemensamma_verksamhetsposter)):
            assert {x.post for x in appar}=={x.id for x in poster}
            assert all(not x.bekraftad and x.postsumma==postsumma(next(g for g in poster if g.id==x.post)) for x in appar)


def test_webb_nekar_oforenlig_hotdimension_utan_att_spara(analysmiljo):
    s,t=analysmiljo;at=Analystjanst(t.mapp,t.rb);at.starta('',schema=2);a=l.las_analys(t.mapp)
    d=dict(csrf=s.csrf,revision=p.registersumma(a),typ='sarbarhet',id='egen:fel-dimension',omrade='kund',hot='H-TF-01',dimension='pt',
        relevans='relevant',status='bekraftad',forfattare='Syntetisk',belagg=a.belagg[0].id,
        beskrivning='Syntetiskt identifierad egen sårbarhet',motivering='Denna felaktiga dimensionsangivelse måste rättas')
    assert anrop(s,'analysgemensampost',d)[0]==400
    assert l.las_analys(t.mapp)==a


def med_plan(t):
    from riskanalys.intag.utvardering import registrera_utvardering
    profil=t.spara(svar('nej'),profilrevision(t.profil()))
    profil=t.spara_plan(Tjansteplan(id='ny',tjanst='T-RED-01',typ='ny_tjanst',beskrivning='Syntetiskt planerat införande'),profilrevision(profil))
    registrera_utvardering(t,DAG,'Syntetiskt prövat underlag, hot, sårbarheter och rutiner före införandet.',profilrevision(profil),plan_id='ny')
    return profil


@pytest.mark.parametrize('text,status',[('nej','bekräftad'),('ja','okänt')])
def test_enskilt_nej_eller_okant_kraver_inte_planval(tjanst,server,text,status):
    from riskanalys.intag.vyer import fragesida
    s=server;profil=med_plan(tjanst)
    html=fragesida(s,'P-TJ.red01_erbjuds',{'text':text,'status':status})
    select=re.search(r'<select name="plan_id"[^>]*>',html)
    assert select is None or 'required' not in select.group()
    data=dict(csrf=s.csrf,revision=profilrevision(profil),falt='P-TJ.red01_erbjuds',text=text,status=status,
        kalla='Syntetiskt tjänsteutbud',roll='Metodansvarig',datum=str(DAG),motivering='Kontrolleras mot avtal',plan_id='ny')
    assert anrop(s,'svar',data)[0]==200
    ny=tjanst.profil();assert ny.uppgifter['P-TJ.red01_erbjuds'].varde is (False if status=='bekräftad' else None)
    assert ny.tjansteplaner[0].genomforande is None


def test_enskilt_ja_begar_plan_som_komplettering_och_sparar_bara_vald_plan(tjanst,server):
    s=server;profil=med_plan(tjanst)
    data=dict(csrf=s.csrf,revision=profilrevision(profil),falt='P-TJ.red01_erbjuds',text='ja',status='bekräftad',kalla='Syntetiskt tjänsteutbud',roll='Metodansvarig',datum=str(DAG))
    kod,html,_=anrop(s,'svar',data)
    assert kod==400 and re.search(r'<select name="plan_id"[^>]*required',html)
    assert tjanst.profil()==profil
    assert anrop(s,'svar',{**data,'plan_id':'ny'})[0]==200
    assert tjanst.profil().tjansteplaner[0].genomforande is not None


def test_tackningsvy_nekar_ogiltig_riskled_som_lasbart_fel(analysmiljo):
    s,t=analysmiljo;Analystjanst(t.mapp,t.rb).starta('',schema=2);a=l.las_analys(t.mapp)
    assert anrop(s,'analys?tjanst='+a.tjanster[0].tjanst+'&tackning=ja&riskled=fel')[0]==400
