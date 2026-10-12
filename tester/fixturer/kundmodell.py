from datetime import date
from riskanalys.regelverk.modeller import Kundrad, Sakkunnig
from riskanalys.regelverk.villkor import Faltvarde, Kunskap

def syntetisk_mall(rb,**v):
    m=rb.kundmall
    # Explicit syntetisk C-metod; ingen signering av produktionsbasen.
    c=Kundrad(id="KC-SYNTETISK",spar="C",villkor={"alla":[]},utfall={"risk":"normal"},grund="metodval",lydelser=(),forklaring="Syntetisk testmetod.")
    m=m.model_copy(update={"rader":(*(r for r in m.rader if r.spar!="C"),c)})
    m=m.model_copy(update={"c_granskning":Sakkunnig(status="verifierad",av="Testsakkunnig",datum=date(2026,10,10),kontrollsumma=m.c_innehallssumma())})
    vard={id:Faltvarde(Kunskap.KAND,False) for id,f in m.falt.items() if f.typ=="bool"}
    vard.update({"K-KK.tillracklig":Faltvarde(Kunskap.KAND,True),"K-A.risk_hanterbar":Faltvarde(Kunskap.KAND,True)})
    vard.update({k:Faltvarde(Kunskap.KAND,x) for k,x in v.items() if x is not None})
    for k,x in v.items():
        if x is None:vard.pop(k,None)
    return m,vard
