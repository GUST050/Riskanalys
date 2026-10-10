from datetime import date
import pytest
from pydantic import ValidationError
from riskanalys.profil.modeller import Profil, Byra, Uppgift
from riskanalys.regelverk.modeller import Falt
from riskanalys.profil.hantering import ProfilFel, tolka_varde

def p(varden):
    return Profil(byra=Byra(id="test",regelpaket="RP-1",datum=date(2026,10,10),lan="Västra Götaland"),uppgifter=varden)

def u(n,period,status="bekräftad"):
    return Uppgift(varde=n,period=period,status=status,kalla="Syntetisk statistik",datum=date(2026,10,10),bekraftad_av="roll:FfR")

def bas(minimal_regelbas):
    f=lambda id,typ,**kw:Falt(id=id,typ=typ,fraga="Syntetisk fråga",varfor="Test",**kw)
    return minimal_regelbas.model_copy(update={"falt":{
        **minimal_regelbas.falt,
        "ANTAL":f("ANTAL","heltal",periodkrav=True),
        "BAS":f("BAS","heltal",periodkrav=True),
        "ANDEL":f("ANDEL","andel",antalfalt="ANTAL",basfalt="BAS",periodkrav=True)
    }})

def test_bakvand_period_avvisas():
    from riskanalys.profil.modeller import Period
    with pytest.raises(ValidationError):
        Period(fran=date(2026,2,1),till=date(2026,1,1))

@pytest.mark.parametrize("brist",["period","annan_period","bas","noll","foreslagen","for_stor","negativ"])
def test_ogiltig_harledning_blir_ingen_kand_andel(minimal_regelbas,brist):
    from riskanalys.profil.modeller import Period
    from riskanalys.profil.omfattning import harled_andelar, omfattningsbrister
    per=Period(fran=date(2026,1,1),till=date(2026,9,30))
    annan=Period(fran=date(2026,2,1),till=date(2026,9,30))
    v={"ANTAL":u(3,per),"BAS":u(100,per)}
    if brist=="period":v["ANTAL"]=u(3,None)
    elif brist=="annan_period":v["BAS"]=u(100,annan)
    elif brist=="bas":v.pop("BAS")
    elif brist=="noll":v["BAS"]=u(0,per)
    elif brist=="foreslagen":v["BAS"]=u(100,per,"föreslagen")
    elif brist=="for_stor":v["ANTAL"]=u(101,per)
    else:v["ANTAL"]=u(-1,per)
    rb=bas(minimal_regelbas)
    ny=harled_andelar(p(v),rb)
    assert not ny.ar_bekraftad("ANDEL")
    assert omfattningsbrister(ny,rb)

def test_tre_av_hundra_ar_exakt_003_och_tampering_stoppas(minimal_regelbas):
    from riskanalys.profil.modeller import Period
    from riskanalys.profil.omfattning import harled_andelar, omfattningsbrister
    per=Period(fran=date(2026,1,1),till=date(2026,9,30));rb=bas(minimal_regelbas)
    ny=harled_andelar(p({"ANTAL":u(3,per),"BAS":u(100,per)}),rb)
    assert ny.uppgifter["ANDEL"].varde==0.03
    assert omfattningsbrister(ny,rb)==[]
    for ersatt in (u(.03,per),ny.uppgifter["ANDEL"].model_copy(update={"varde":.5})):
        hand=ny.model_copy(update={"uppgifter":{**ny.uppgifter,"ANDEL":ersatt}})
        assert omfattningsbrister(hand,rb)

def test_andelen_ett_kraver_tydligt_format():
    f=Falt(id="P-A",typ="andel",fraga="Andel?",varfor="Test")
    with pytest.raises(ProfilFel,match="1 %"):
        tolka_varde(f,"1")
    assert tolka_varde(f,"1 %")==.01
    assert tolka_varde(f,"1,0")==1.0

def test_handandel_stoppas_i_bedomning_och_i_grind(minimal_regelbas):
    from riskanalys.profil.modeller import Period
    from riskanalys.profil.hantering import kontrollera_profil
    from riskanalys.faststallelse.grindar import _uppgifter
    from types import SimpleNamespace
    from riskanalys.regelverk.urval import valj
    per=Period(fran=date(2026,1,1),till=date(2026,9,30));rb=bas(minimal_regelbas)
    hand=p({"ANTAL":u(3,per),"BAS":u(100,per),"ANDEL":u(.8,per)})
    with pytest.raises(ProfilFel,match="direkt|Direkt"):
        kontrollera_profil(hand,rb)
    # Urval från minimalbas behövs bara för kritiska fält i detta säkerhetsprov.
    urval=valj(minimal_regelbas,"RP-1",date(2026,10,10),"Västra Götaland")
    assert any("direkt" in h for h in _uppgifter(SimpleNamespace(profil=hand,regelbas=rb,urval=urval)))
