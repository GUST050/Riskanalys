"""Förändringsutvärdering är en lokal sakprövning, inte ett motorbeslut."""
from datetime import date
import pytest
from riskanalys.profil.modeller import Byra, Profil, Uppgift, Tjansteplan
from riskanalys.profil.planering import plansumma, planbrister, forandringshinder
from riskanalys.drift.historik import Handelse, Historik, Erbjudanderattelse
from riskanalys.profil.lagring import profilrevision
from riskanalys.regelverk.laddning import ladda_regelbas

DAG = date(2026, 10, 10)

@pytest.fixture(scope='module')
def rb():
    return ladda_regelbas()

def upp(v):
    return Uppgift(varde=v, status='bekräftad', kalla='Syntetisk källa', datum=DAG, bekraftad_av='roll:FfR')

def profil(v=False):
    return Profil(byra=Byra(id='syntetisk', regelpaket='RP-RED-VG', lan='Västra Götaland', datum=DAG),
                  uppgifter={'P-TJ.red01_erbjuds': upp(v)})

def plan(p):
    return p.model_copy(update={'tjansteplaner': (Tjansteplan(id='ny', tjanst='T-RED-01', typ='ny_tjanst',
        beskrivning='Planerade arbetsmoment och insyn, leverans och geografi', uppgifter={}),)})

def ja(p):
    return p.model_copy(update={'uppgifter': {**p.uppgifter, 'P-TJ.red01_erbjuds': upp(True)}})

def utvardering(rb, p):
    return Handelse(datum=DAG, typ='utvärdering', beskrivning='Prövade hot och rutiner; behåller bedömningen med angivna skäl.',
                    plan_id='ny', plansumma=plansumma(rb, p, 'ny'))

def test_nej_till_ja_kraver_plan_och_bunden_utvardering(rb):
    p = profil()
    assert forandringshinder(rb, p, ja(p), Historik(), DAG)
    p = plan(p)
    assert forandringshinder(rb, p, ja(p), Historik(), DAG)
    h = Historik(handelser=(utvardering(rb, p),))
    assert not forandringshinder(rb, p, ja(p), h, DAG)
    assert plansumma(rb, p, 'ny') == plansumma(rb, ja(p), 'ny')
    andra = p.model_copy(update={'tjansteplaner': (p.tjansteplaner[0].model_copy(update={'beskrivning':'Ändrad marknad'}),)})
    assert forandringshinder(rb, andra, ja(andra), h, DAG)

def test_okant_ar_kartlaggning_men_inaktuellt_nej_ar_inte_det(rb):
    p = profil().model_copy(update={'uppgifter': {}})
    assert not forandringshinder(rb, p, ja(p), Historik(), DAG)
    p = profil().model_copy(update={'uppgifter': {'P-TJ.red01_erbjuds': upp(False).model_copy(update={'inaktuell':True})}})
    assert forandringshinder(rb, p, ja(p), Historik(), DAG)

def test_planutvardering_flyttar_inte_arsfrist(rb):
    full = Handelse(datum=date(2026,1,1), typ='utvärdering', beskrivning='Hela bedömningen')
    h = Historik(handelser=(full, utvardering(rb, plan(profil()))))
    assert h.senaste_utvardering() == full.datum
    assert h.nasta_genomgang() == date(2027,1,1)

def test_rattelse_maste_stamma_och_far_inte_kringga_registrerad_plan(rb):
    p = profil(); n = ja(p)
    r = Erbjudanderattelse(tjanst='T-RED-01', fore=p.uppgifter['P-TJ.red01_erbjuds'], efter=n.uppgifter['P-TJ.red01_erbjuds'],
        motivering='Fel vid första kartläggningen', kalla='Avtal från tidigare år', ansvarig='roll:FfR', datum=DAG, profilrevision=profilrevision(p))
    assert not forandringshinder(rb, p, n, Historik(), DAG, rattelse=r)
    assert forandringshinder(rb, plan(p), ja(plan(p)), Historik(), DAG, rattelse=r)
    assert forandringshinder(rb, p, n, Historik(), DAG, rattelse=r.model_copy(update={'profilrevision':'fel'}))

def test_tomma_nya_falt_utelamnas_och_gammal_historik_bevaras():
    assert set(profil().model_dump()) == {'byra','uppgifter'}
    assert set(Handelse(datum=DAG, typ='utvärdering', beskrivning='Hela').model_dump()) == {'datum','typ','beskrivning','version'}

@pytest.mark.parametrize('id,varde', [('P-ROLL.ffr_namn','Hemligt'),('P-TJ.red02_erbjuds',True),('P-KUND.andel_riskbransch',.2),('P-KONTROLL.C-07.genomforande','fungerar'),('P-TJ.red01_erbjuds','ja')])
def test_planfalt_begransas_och_typkontrolleras(rb,id,varde):
    p = plan(profil()); t = p.tjansteplaner[0].model_copy(update={'uppgifter':{id:upp(varde)}})
    assert planbrister(rb, p.model_copy(update={'tjansteplaner':(t,)}))


def test_aldre_alias_nej_ar_inte_forsta_kartlaggning(rb):
    from riskanalys.intag.svar import besvara
    from riskanalys.intag.modeller import IntagSvar
    p=profil().model_copy(update={'uppgifter':{'P-TJ.T-RED-01.erbjuds':upp(False)}})
    n=besvara(rb,p,IntagSvar(falt='P-TJ.red01_erbjuds',text='ja',kalla='Syntetisk källa',datum=DAG))
    assert forandringshinder(rb,p,n,Historik(),DAG)


def test_forvantad_inaktualisering_vid_inforande_bevarar_planbindningen(rb):
    from riskanalys.intag.svar import besvara
    from riskanalys.intag.modeller import IntagSvar
    p=plan(profil())
    p=p.model_copy(update={'uppgifter':{**p.uppgifter,'P-TJ.red01_arbetssatt':upp('Äldre dokumenterade arbetsmoment')}})
    h=Historik(handelser=(utvardering(rb,p),))
    n=besvara(rb,p,IntagSvar(falt='P-TJ.red01_erbjuds',text='ja',kalla='Syntetisk källa',datum=DAG))
    assert n.uppgifter['P-TJ.red01_arbetssatt'].inaktuell
    assert not forandringshinder(rb,p,n,h,DAG)
