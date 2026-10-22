from datetime import date
import pytest
from riskanalys.profil.lagring import spara_profil, profilrevision, las_profil
from riskanalys.profil.forandringar import spara_andring, registrera_genomforande
from riskanalys.drift.historik import Historik, spara_historik, las_historik
from riskanalys.profil.planering import forandringshinder
from riskanalys.profil.modeller import Tjansteplan, Planval
from riskanalys.fel import RiskanalysFel
from tester.enhet.test_tjansteplanering import profil,plan,ja,utvardering,DAG,rb


def lagra(rb,mapp,p):
    spara_profil(mapp,p)
    spara_historik(mapp,Historik(handelser=(utvardering(rb,p),)))


def inford(rb,mapp):
    p=plan(profil());lagra(rb,mapp,p)
    return spara_andring(mapp,rb,ja(p),profilrevision(p),planval=(Planval(tjanst='T-RED-01',plan_id='ny'),))


def test_avslut_ar_registrerat_och_fryser_planen(rb,tmp_path):
    p=inford(rb,tmp_path)
    g=p.tjansteplaner[0].genomforande
    assert g.datum==DAG and g.ansvarig=='roll:FfR' and g.utvarderad==DAG
    assert 'Prövade hot' in g.utvardering
    assert las_profil(tmp_path)==p
    ny=p.model_copy(update={'tjansteplaner':(p.tjansteplaner[0].model_copy(update={'beskrivning':'Omskriven historik'}),)})
    with pytest.raises(RiskanalysFel,match='historik'):
        spara_andring(tmp_path,rb,ny,profilrevision(p),lokalt_underlag=True)


def test_aterinforande_kraver_ny_plan_och_ny_utvardering(rb,tmp_path):
    p=inford(rb,tmp_path)
    nej=p.model_copy(update={'uppgifter':profil().uppgifter})
    spara_andring(tmp_path,rb,nej,profilrevision(p))
    with pytest.raises(RiskanalysFel,match='plan'):
        spara_andring(tmp_path,rb,ja(nej),profilrevision(nej))


def test_andringsplan_avslutas_uttryckligen_inte_via_datum(rb,tmp_path):
    p=plan(ja(profil()));p=p.model_copy(update={'tjansteplaner':(p.tjansteplaner[0].model_copy(update={'typ':'ny_marknad','avsett_inforande':DAG}),)})
    lagra(rb,tmp_path,p)
    assert p.tjansteplaner[0].genomforande is None
    fore=las_historik(tmp_path)
    p=registrera_genomforande(tmp_path,rb,'ny',DAG,'Ansvarig funktion',profilrevision(p))
    assert p.tjansteplaner[0].genomforande is not None
    assert las_historik(tmp_path)==fore
    nytt=p.model_copy(update={'byra':p.byra.model_copy(update={'datum':date(2027,10,10)})})
    assert not forandringshinder(rb,nytt,nytt,fore,date(2027,10,10))


def test_ej_utvarderad_eller_inaktuell_plan_kan_inte_markeras_genomford(rb,tmp_path):
    p=plan(ja(profil()));spara_profil(tmp_path,p)
    with pytest.raises(RiskanalysFel,match='utvärdering'):
        registrera_genomforande(tmp_path,rb,'ny',DAG,'Ansvarig',profilrevision(p))
    spara_historik(tmp_path,Historik(handelser=(utvardering(rb,p),)))
    with pytest.raises(RiskanalysFel,match='datum'):
        registrera_genomforande(tmp_path,rb,'ny',date(2026,9,1),'Ansvarig',profilrevision(p))


def test_avbruten_profilskrivning_ger_inte_falskt_genomforande(rb,tmp_path,monkeypatch):
    import riskanalys.profil.forandringar as f
    p=plan(profil());lagra(rb,tmp_path,p)
    def avbrott(*args,**kwargs):raise RiskanalysFel('Syntetiskt skrivfel')
    monkeypatch.setattr(f,'spara_profil',avbrott)
    with pytest.raises(RiskanalysFel,match='skrivfel'):
        spara_andring(tmp_path,rb,ja(p),profilrevision(p),planval=(Planval(tjanst='T-RED-01',plan_id='ny'),))
    assert las_profil(tmp_path)==p


def test_gammal_plan_utan_genomforande_bevarar_serialisering(rb):
    p=plan(profil())
    assert 'genomforande' not in p.tjansteplaner[0].model_dump()


def test_genomford_plan_far_inte_importeras_eller_ateroppnas(rb,tmp_path):
    p=inford(rb,tmp_path/'inford')
    for post in (p.tjansteplaner[0].model_copy(update={'genomforande':None}),):
        with pytest.raises(RiskanalysFel,match='historik'):
            spara_andring(tmp_path/'inford',rb,p.model_copy(update={'tjansteplaner':(post,)}),profilrevision(p),lokalt_underlag=True)
    tom=plan(profil());spara_profil(tmp_path/'ny',tom)
    with pytest.raises(RiskanalysFel,match='särskilda flödet'):
        spara_andring(tmp_path/'ny',rb,tom.model_copy(update={'tjansteplaner':p.tjansteplaner}),profilrevision(tom),lokalt_underlag=True)


def test_gammal_planbevisning_lases_historiskt_och_arsfristen_galler(rb,tmp_path):
    from types import SimpleNamespace
    from riskanalys.faststallelse.grindar import _drift
    from riskanalys.drift.historik import Handelse
    p=plan(profil())
    p=p.model_copy(update={'tjansteplaner':(p.tjansteplaner[0].model_copy(update={'uppgifter':{'P-TJ.red01_arbetssatt':p.uppgifter['P-TJ.red01_erbjuds'].model_copy(update={'varde':'Äldre arbetssätt'})}}),)})
    lagra(rb,tmp_path,p)
    p=spara_andring(tmp_path,rb,ja(p),profilrevision(p),planval=(Planval(tjanst='T-RED-01',plan_id='ny'),))
    ny_rb=rb.model_copy(update={'falt':{k:v for k,v in rb.falt.items() if k!='P-TJ.red01_arbetssatt'}})
    h=las_historik(tmp_path).med(Handelse(datum=DAG,typ='utvärdering',beskrivning='Hela riskbedömningen'))
    hinder=_drift(SimpleNamespace(regelbas=ny_rb,profil=p,historik=h),date(2027,10,20))
    assert len(hinder)==1 and 'Nästa genomgång' in hinder[0]
    andrad=p.model_copy(update={'tjansteplaner':(p.tjansteplaner[0].model_copy(update={'beskrivning':'Historik ändrad utanför programmet'}),)})
    assert forandringshinder(rb,andrad,andrad,h,DAG)
