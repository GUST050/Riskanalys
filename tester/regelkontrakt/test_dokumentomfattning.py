from datetime import date
from riskanalys.regelverk.modeller import Kravmal
from riskanalys.regelverk.urval import valj
from riskanalys.dokument.modeller import Dokument
from riskanalys.granskning.kontroller import _tackning

def test_rent_rutinkrav_far_inte_blockera_arb(minimal_regelbas,profil_fabrik):
    rb=minimal_regelbas;k=rb.krav["KRV-1"].model_copy(update={"mal":(Kravmal(typ="dokument",id="D-RR.1",etapp="M6"),),"uppfylls_i":("D-RR.1",)})
    rb=rb.model_copy(update={"krav":{k.id:k}})
    p=profil_fabrik(rb,{});u=valj(rb,"RP-1",date(2026,10,10),"Västra Götaland")
    assert _tackning(rb,u,p,Dokument(id="D-ARB",titel="Test",avsnitt=()))==[]
    assert len(_tackning(rb,u,p,Dokument(id="D-RR",titel="Test",avsnitt=())))==1

def test_driftmal_ger_inget_arb_fynd(minimal_regelbas,profil_fabrik):
    k=minimal_regelbas.krav["KRV-1"].model_copy(update={"mal":(Kravmal(typ="drift",id="DRIFT-REGISTRERING",etapp="M4"),),"uppfylls_i":()})
    rb=minimal_regelbas.model_copy(update={"krav":{k.id:k}})
    p=profil_fabrik(rb,{});u=valj(rb,"RP-1",date(2026,10,10),"Västra Götaland")
    assert _tackning(rb,u,p,Dokument(id="D-ARB",titel="Test",avsnitt=()))==[]
