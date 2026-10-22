from datetime import date
import pytest
from riskanalys.profil.modeller import Byra, Profil, Uppgift, Period, Kombinationsgrupp
from riskanalys.profil.kombinationer import kombinationsbrister, grupper_for_tjanst
from riskanalys.regelverk.laddning import ladda_regelbas

@pytest.fixture(scope='module')
def rb():
    return ladda_regelbas()

def upp(v):
    return Uppgift(varde=v,status='bekräftad',kalla='Syntetisk sammanställning',datum=date(2026,10,1),bekraftad_av='roll:FfR',
                  period=Period(fran=date(2026,1,1),till=date(2026,9,30)))

def profil(rb, antal=8, bas=100):
    g=Kombinationsgrupp(id='samtidigt', tjanst='T-RED-01', population='uppdrag', avgransning='Löpande uppdrag under perioden',
        beskrivning='Båda egenskaperna i samma uppdrag, verifierat mot avtal.', sarbarheter=tuple(rb.tjanster['T-RED-01'].sarbarheter[:2]), antal=upp(antal), bas=upp(bas))
    return Profil(byra=Byra(id='syntetisk',lan='Västra Götaland',regelpaket='RP-RED-VG',datum=date(2026,10,10)),uppgifter={},kombinationsgrupper=(g,))

def test_samtidig_grupp_ar_tjanstespecifik_utan_poang(rb):
    p=profil(rb)
    assert not kombinationsbrister(rb,p)
    assert grupper_for_tjanst(rb,p,'T-RED-01') == p.kombinationsgrupper
    assert not grupper_for_tjanst(rb,p,'T-RED-02')

@pytest.mark.parametrize('antal,bas', [(True,100),(-1,100),(101,100),(1,0),(8.0,100)])
def test_ogiltiga_antal_far_inte_bli_andel(rb,antal,bas):
    assert kombinationsbrister(rb,profil(rb,antal,bas))

@pytest.mark.parametrize('andring', [{'inaktuell':True},{'kalla':'Annan källa'},{'period':None},{'bekraftad_av':'Annan funktion'}])
def test_oforenligt_eller_inaktuellt_underlag_vagras(rb,andring):
    p=profil(rb); g=p.kombinationsgrupper[0]
    p=p.model_copy(update={'kombinationsgrupper':(g.model_copy(update={'antal':g.antal.model_copy(update=andring)}),)})
    assert kombinationsbrister(rb,p)

def test_okant_och_noll_ar_skilda_och_grupper_summeras_inte(rb):
    p=profil(rb,0,0)
    assert not kombinationsbrister(rb,p)
    g=p.kombinationsgrupper[0].model_copy(update={'antal':Uppgift()})
    assert not kombinationsbrister(rb,p.model_copy(update={'kombinationsgrupper':(g,)}))
    assert g.antal.varde is None
