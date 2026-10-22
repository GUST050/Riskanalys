from datetime import date
import pytest
from riskanalys.fel import RiskanalysFel
from riskanalys.intag.modeller import IntagSvar
from riskanalys.intag.tjanst import Intagstjanst
from riskanalys.intag.utvardering import registrera_utvardering
from riskanalys.profil.lagring import spara_profil, profilrevision
from riskanalys.profil.modeller import Tjansteplan, Planval
from riskanalys.drift.historik import las_historik, historikens_kontrollsumma
from tester.fixturer.m2 import DAG

@pytest.fixture
def tjanst(datamapp, rb_intag, tom):
    t = Intagstjanst(tom.byra.id, rb_intag)
    spara_profil(t.mapp, tom)
    return t

def svar(text, status='bekräftad'):
    return IntagSvar(falt='P-TJ.red01_erbjuds', text=text, status=status, kalla='Syntetiskt tjänsteutbud', datum=DAG, motivering='Kontrolleras mot avtal' if status=='okänt' else '')

def test_hela_batchen_kan_inte_dolja_nej(tjanst):
    p = tjanst.spara(svar('nej'), profilrevision(tjanst.profil()))
    with pytest.raises(RiskanalysFel, match='plan'):
        tjanst.spara_flera((svar('', 'okänt'), svar('ja')), profilrevision(p))
    assert tjanst.profil() == p

def test_plan_till_utvardering_till_inforande_utan_motor(tjanst):
    p = tjanst.spara(svar('nej'), profilrevision(tjanst.profil()))
    plan = Tjansteplan(id='ny', tjanst='T-RED-01', typ='ny_tjanst', beskrivning='Planerat uppdrag med insyn och distansleverans.')
    p = tjanst.spara_plan(plan, profilrevision(p))
    fore = historikens_kontrollsumma(tjanst.mapp)
    registrera_utvardering(tjanst, DAG, 'Underlag: avtalsutkast. Hot: falska fakturor. Sårbarhet: distans. Rutiner: verifiera original. Beslut: behåll bedömningen med dessa skäl.', profilrevision(p), plan_id='ny')
    assert fore != historikens_kontrollsumma(tjanst.mapp)
    assert las_historik(tjanst.mapp).senaste_utvardering() is None
    p = tjanst.spara(svar('ja'), profilrevision(p), planval=(Planval(tjanst='T-RED-01',plan_id='ny'),))
    assert p.uppgifter['P-TJ.red01_erbjuds'].varde is True
    assert not (tjanst.mapp/'bedomningar').exists()

def test_stale_planformular_och_framtida_utvardering_vagras(tjanst):
    p = tjanst.profil()
    plan = Tjansteplan(id='ny', tjanst='T-RED-01', typ='ny_tjanst', beskrivning='Planerade arbetsmoment.')
    with pytest.raises(RiskanalysFel, match='ändrats'):
        tjanst.spara_plan(plan, 'fel')
    p = tjanst.spara_plan(plan, profilrevision(p))
    with pytest.raises(RiskanalysFel, match='datum'):
        registrera_utvardering(tjanst, date(2099,1,1), 'Inte genomförd', profilrevision(p), plan_id='ny')


def test_utvardering_far_inte_predatera_gruppens_belagg(tjanst):
    from tester.enhet.test_kombinationsgrupper import profil as grupprofil
    from riskanalys.profil.modeller import Tjansteplan
    p=tjanst.profil()
    plan=Tjansteplan(id='ny',tjanst='T-RED-01',typ='ny_tjanst',beskrivning='Plan med gruppunderlag')
    p=tjanst.spara_plan(plan,profilrevision(p))
    g=grupprofil(tjanst.rb).kombinationsgrupper[0]
    p=tjanst.spara_kombinationsgrupp(g,profilrevision(p))
    with pytest.raises(RiskanalysFel,match='underlag'):
        registrera_utvardering(tjanst,date(2026,9,1),'Prövning daterad före underlaget.',profilrevision(p),plan_id='ny')


def test_planantagandets_framtida_period_ar_inte_faktisk_grupphistorik(tjanst):
    from riskanalys.profil.modeller import Uppgift, Period
    u=Uppgift(varde=0,status='föreslagen',datum=DAG,period=Period(fran=date(2027,1,1),till=date(2027,3,31)))
    plan=Tjansteplan(id='framtid',tjanst='T-RED-01',typ='ny_tjanst',beskrivning='Plan för framtida uppdrag',uppgifter={'P-TJ.red01_antal_kunder':u})
    p=tjanst.spara_plan(plan,profilrevision(tjanst.profil()))
    registrera_utvardering(tjanst,DAG,'Prövar planantaganden om kommande uppdrag.',profilrevision(p),plan_id=plan.id)


def test_planens_tjanstidentitet_far_inte_byta_och_oppna_rattelse(tjanst):
    p=tjanst.spara(svar('nej'),profilrevision(tjanst.profil()))
    plan=Tjansteplan(id='ny',tjanst='T-RED-01',typ='ny_tjanst',beskrivning='Registrerad förändring')
    p=tjanst.spara_plan(plan,profilrevision(p))
    with pytest.raises(RiskanalysFel,match='tjänst'):
        tjanst.spara_plan(plan.model_copy(update={'tjanst':'T-RED-02'}),profilrevision(p))


def test_planens_oforandrade_varde_kan_fa_nya_belagg(tjanst):
    from riskanalys.intag.planeringsvy import spara_plan
    from riskanalys.profil.modeller import Uppgift
    from riskanalys.profil.planering import plansumma
    f='P-TJ.red01_arbetssatt'
    u=Uppgift(varde='Antaget arbetssätt',status='föreslagen',kalla='Gammal källa',datum=date(2026,9,1),bekraftad_av='FfR')
    plan=Tjansteplan(id='ny',tjanst='T-RED-01',typ='ny_tjanst',beskrivning='Planerade uppdrag',uppgifter={f:u})
    p=tjanst.spara_plan(plan,profilrevision(tjanst.profil()))
    fore=plansumma(tjanst.rb,p,'ny')
    data=dict(revision=profilrevision(p),id='ny',tjanst=plan.tjanst,typ=plan.typ,beskrivning=plan.beskrivning,kalla='Ny källa',datum=str(DAG),roll='Metodansvarig',**{'antagande_'+f:u.varde})
    p=spara_plan(tjanst,data)
    ny=p.tjansteplaner[0].uppgifter[f]
    assert (ny.kalla,ny.datum,ny.bekraftad_av)==('Ny källa',DAG,'Metodansvarig')
    assert plansumma(tjanst.rb,p,'ny') != fore

def test_webb_planering_samma_sparr_csrf_och_escape(tjanst):
    import threading
    from riskanalys.intag.webb import skapa_server
    from tester.intag.test_webb import anrop
    s = skapa_server(tjanst)
    trad = threading.Thread(target=s.serve_forever,daemon=True); trad.start()
    try:
        assert anrop(s,'planering')[0] == 200
        data=dict(csrf=s.csrf,revision=profilrevision(tjanst.profil()),id='ny',tjanst='T-RED-01',typ='ny_tjanst',beskrivning='<script>Planantagande</script>')
        assert anrop(s,'plan', {**data,'csrf':'fel'})[0] == 403
        assert anrop(s,'plan',data)[0] == 200
        status,html,_=anrop(s,'planering')
        assert status==200 and '&lt;script&gt;' in html and '<script>Planantagande' not in html
        assert anrop(s,'plan',data)[0] == 409
        assert anrop(s,'plan',{**data,'revision':profilrevision(tjanst.profil()),'tjanst':'okand'})[0] == 400
        status,html,_=anrop(s,'planutvardera',dict(csrf=s.csrf,revision=profilrevision(tjanst.profil()),plan_id='ny',datum='fel',
            underlag='Bevara inmatat underlag',hot_sarbarheter='Bevara hot',risk_rutiner='Bevara rutiner',beslut='Bevara beslut'))
        assert status==400
        assert 'Bevara inmatat underlag' in html and 'Bevara beslut' in html
        assert 'name="plan_id" value="ny"' in html
    finally:
        s.shutdown();s.server_close();trad.join(timeout=2)


def test_andringsplan_kan_registreras_genomford_i_webb_och_cli(tjanst):
    import threading
    from riskanalys.intag.webb import skapa_server
    from riskanalys.cli import main
    from tester.intag.test_webb import anrop
    p=tjanst.spara(svar('ja'),profilrevision(tjanst.profil()))
    for id in ('webbandring','cliandring'):
        plan=Tjansteplan(id=id,tjanst='T-RED-01',typ='ny_marknad',beskrivning='Nytt geografiskt område, dokumenterat i plan.')
        p=tjanst.spara_plan(plan,profilrevision(p))
        registrera_utvardering(tjanst,DAG,'Prövat hot, insyn och rutiner med dokumenterade skäl.',profilrevision(p),plan_id=id)
    s=skapa_server(tjanst);trad=threading.Thread(target=s.serve_forever,daemon=True);trad.start()
    try:
        data=dict(csrf=s.csrf,revision=profilrevision(p),plan_id='webbandring',datum=str(DAG),ansvarig='Ansvarig funktion',genomford='ja')
        assert anrop(s,'plangenomforande',{**data,'csrf':'fel'})[0]==403
        assert anrop(s,'plangenomforande',data)[0]==200
        assert anrop(s,'plangenomforande',data)[0]==409
        status,html,_=anrop(s,'planering?plan=webbandring')
        assert status==200 and 'Genomförd' in html and 'Ansvarig funktion' in html
        assert 'name="beskrivning"' not in html
        assert main(['genomfor-plan',tjanst.mapp.name,'cliandring','--datum',str(DAG),'--ansvarig','Ansvarig funktion'])==0
        assert all(p.genomforande for p in tjanst.profil().tjansteplaner)
    finally:
        s.shutdown();s.server_close();trad.join(timeout=2)
