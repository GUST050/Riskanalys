from datetime import date
import pytest
from pydantic import ValidationError
from riskanalys.regelverk.modeller import Falt, Sakkunnig
from riskanalys.regelverk.villkor import Faltvarde, Kunskap

@pytest.mark.parametrize("risk",["låg","normal","hög"])
def test_c_kraver_uttrycklig_och_signerad_metod(risk):
 from riskanalys.bedomning.kundmodell.modeller import Kundmall, Kundrad
 from riskanalys.bedomning.kundmodell.utvardering import utvardera_kundmall
 f=Falt(id="K-TEST",typ="bool",fraga="Test?",varfor="Syntetiskt")
 r=Kundrad(id="KC-TEST",spar="C",villkor={"falt":f.id,"op":"==","varde":True},utfall={"risk":risk},grund="metodval",lydelser=(),forklaring="Syntetisk metod")
 m=Kundmall(falt={f.id:f},rader=(r,))
 known={f.id:Faltvarde(Kunskap.KAND,True)}
 assert utvardera_kundmall(m,known,date(2026,10,10)).C=="preliminär"
 signed=m.model_copy(update={"c_granskning":Sakkunnig(status="verifierad",av="Syntetisk granskare",datum=date(2026,10,10),kontrollsumma=m.c_innehallssumma())})
 assert utvardera_kundmall(signed,known,date(2026,10,10)).C==risk
 assert utvardera_kundmall(signed,{f.id:Faltvarde(Kunskap.KAND,False)},date(2026,10,10)).C=="preliminär"
 assert utvardera_kundmall(signed,{},date(2026,10,10)).C=="preliminär"
 assert "K-TEST" in utvardera_kundmall(signed,{},date(2026,10,10)).okanda_uppgifter
 # Motsägande träffar får aldrig bli en normal fallback.
 andra=r.model_copy(update={"id":"KC-ANDRA","utfall":{"risk":"hög" if risk!="hög" else "låg"}})
 conflict=m.model_copy(update={"rader":(r,andra)})
 conflict=conflict.model_copy(update={"c_granskning":Sakkunnig(status="verifierad",av="Syntetisk granskare",datum=date(2026,10,10),kontrollsumma=conflict.c_innehallssumma())})
 assert utvardera_kundmall(conflict,known,date(2026,10,10)).C=="preliminär"

def test_fritt_kommando_och_ogiltig_risk_vagras():
 from riskanalys.bedomning.kundmodell.modeller import Kundrad
 for data in ({"kommando":"skicka"},{"risk":"ingen risk"}):
  with pytest.raises(ValidationError):
   Kundrad(id="KC",spar="C",villkor={"alla":[]},utfall=data,grund="metodval",lydelser=(),forklaring="Test")

def test_kundfalt_ar_separata_och_produktions_c_ar_ogranskad(regelbas_v1):
 from riskanalys.profil.hantering import skapa_profil
 from riskanalys.profil.modeller import Byra
 from riskanalys.bedomning.kundmodell.utvardering import utvardera_kundmall
 assert regelbas_v1.kundmall
 assert not any(id.startswith("K-") for id in regelbas_v1.falt)
 assert not any(id.startswith("K-") for id in regelbas_v1.tillatelselistor["risk_per_tjanst"].falt)
 assert utvardera_kundmall(regelbas_v1.kundmall,{},date(2026,10,10)).C=="preliminär"
