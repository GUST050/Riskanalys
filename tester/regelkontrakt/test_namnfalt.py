import pytest
from riskanalys.regelverk.laddning import ladda_regelbas
from riskanalys.regelverk.modeller import Falt
from riskanalys.profil.hantering import personnamn, skapa_profil
from riskanalys.profil.modeller import Byra, Uppgift
from datetime import date


def test_ffr_namn_ar_namnfalt_men_inte_rolltext():
    rb = ladda_regelbas()
    assert rb.falt['P-ROLL.ffr_namn'].namnfalt
    assert not rb.falt['P-ROLL.ansvarsfunktion'].namnfalt


def test_osatt_namnfalt_serialiseras_inte():
    bas = dict(id='P-X.namn',typ='text',fraga='Namn?',varfor='Prov',personuppgift=True)
    assert 'namnfalt' not in Falt(**bas).model_dump()
    assert 'namnfalt' not in Falt(**bas,namnfalt=False).model_dump()
    assert Falt(**bas,namnfalt=True).model_dump()['namnfalt'] is True


@pytest.mark.parametrize('typ,personuppgift',[('heltal',True),('text',False)])
def test_namnfalt_maste_vara_personlig_text(typ,personuppgift):
    with pytest.raises(ValueError):
        Falt(id='P-X.namn',typ=typ,fraga='Namn?',varfor='Prov',personuppgift=personuppgift,namnfalt=True)


def test_personnamn_foljer_egenskapen_inte_id():
    rb = ladda_regelbas()
    falt = rb.falt['P-ROLL.ansvarsfunktion'].model_copy(update={'namnfalt':True})
    rb = rb.model_copy(update={'falt':{**rb.falt,falt.id:falt}})
    profil = skapa_profil(rb,Byra(id='syntetisk',lan='Västra Götaland',regelpaket='RP-RED-VG',datum=date(2026,10,14)))
    profil = profil.model_copy(update={'uppgifter':{**profil.uppgifter,falt.id:Uppgift(status='bekräftad',varde='Cecilia Ek')}})
    assert 'Cecilia Ek' in personnamn(profil,rb)
