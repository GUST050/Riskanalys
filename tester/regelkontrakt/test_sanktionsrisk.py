from datetime import date
import pytest
from riskanalys.profil.modeller import Profil, Byra, Uppgift
from riskanalys.bedomning.motor import bedom_tjanst
from riskanalys.dokument.modeller import Textstycke

def profil(**v):
 return Profil(byra=Byra(id="test",regelpaket="RP-RED-VG",datum=date(2026,10,10),lan="Västra Götaland"),uppgifter={id:Uppgift(varde=value,status="bekräftad",kalla="Test",datum=date(2026,10,10),bekraftad_av="Test") for id,value in v.items()})

def test_tf_far_inte_kopieras_och_obelagd_kontroll_sanker_inte(regelbas_v1):
 from riskanalys.bedomning.sanktioner import bedom_sanktionsrisk
 t=regelbas_v1.tjanster["T-RED-01"].model_copy(update={"grund_tf_sannolikhet":"hög"})
 p=profil(**{"P-GEO.sanktionsanknytning":False,"P-KONTROLL.C-SANK.utformning":"finns","P-KONTROLL.C-SANK.genomforande":"ej_belagt"})
 a=bedom_sanktionsrisk(regelbas_v1,t,p)
 assert a.status=="slutlig" and a.inneboende.sannolikhet=="låg"
 assert a.kvarstaende==a.inneboende.risk
 assert bedom_tjanst(regelbas_v1,t,p).sanktionsrisk==a

def test_okand_geografi_ar_preliminar(regelbas_v1):
 from riskanalys.bedomning.sanktioner import bedom_sanktionsrisk
 a=bedom_sanktionsrisk(regelbas_v1,regelbas_v1.tjanster["T-RED-01"],profil())
 assert a.status=="preliminär" and "P-GEO.sanktionsanknytning" in a.okanda_uppgifter

@pytest.mark.parametrize("text",["Sanktionsrisken är låg.","Den kvarstående sanktionsrisken är låg.","Risken för internationella sanktioner är låg."])
def test_ai_far_inte_andra_sanktionsniva(giltigt_utkast,real_underlag,text):
 from riskanalys.dokument.validering import validera_utkast
 underlag=real_underlag.model_copy(update={"nivaer":{**real_underlag.nivaer,"sanktioner_risk":"hög","kvarstaende_sanktioner_risk":"hög"}})
 u=giltigt_utkast.model_copy(update={"stycken":[*giltigt_utkast.stycken,Textstycke(typ="analys",text=text,referenser=["H-01"])]})
 assert any("sanktion" in f.lower() and "riskmotorn" in f for f in validera_utkast(u,underlag,()))
