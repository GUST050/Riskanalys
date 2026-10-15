from datetime import date

import pytest

from riskanalys.bedomning.motor import bedom
from riskanalys.dokument.underlag import NIVANYCKLAR, SKYDDAD_VISNING, UnderlagsFel, bygg_underlag, tjanster_med_avsnitt
from riskanalys.regelverk.modeller import Tillatelselista
from riskanalys.regelverk.urval import valj


def _bedomning(regelbas, profil):
    return bedom(regelbas, valj(regelbas, "RP-RED-VG", date(2026, 11, 1), "Västra Götaland"), profil)


def test_underlaget_for_lopande_bokforing(real_underlag):
    assert real_underlag.avsnitt == "D-ARB.6.1"
    assert real_underlag.tjanst_id == "T-RED-01"
    assert real_underlag.nivaer == {
        "inneboende_sannolikhet": "hög",
        "inneboende_konsekvens": "betydande",
        "inneboende_risk": "hög",
        "terrorfinansiering_sannolikhet": "låg",
        "terrorfinansiering_konsekvens": "allvarlig",
        "terrorfinansiering_risk": "måttlig",
        "kvarstaende_risk": "hög",
    }
    assert tuple(real_underlag.nivaer) == NIVANYCKLAR
    assert {uppgift.id: uppgift.varde for uppgift in real_underlag.uppgifter} == {
        "P-ORG.antal_anstallda": "8",
        "P-KUND.andel_riskbransch": "30 %",
        "P-KUND.andel_kontant": "5 %",
        "P-KANAL.andel_digitalt_underlag": "80 %",
        "P-KANAL.bankdata_andel": "40 %",
        "P-VERK.juniora_konsulter": "nej",
    }
    assert {post.id: post.galler for post in real_underlag.sarbarheter} == {
        "S-KUND-01": "ja",
        "S-KUND-02": "nej",
        "S-KANAL-01": "ja",
        "S-VERK-01": "nej",
    }
    assert [post.status for post in real_underlag.kontroller] == ["finns i rutinerna men är inte belagd"]
    assert [post.id for post in real_underlag.undvik] == ["B-02", "B-03", "B-04", "B-12", "B-13", "B-24", "B-25"]
    assert "BT-MATRIS-08" in real_underlag.tillatna_id()


def test_underlaget_innehaller_inga_personuppgifter_eller_byranamn(real_underlag):
    text = real_underlag.model_dump_json()
    assert "Testa Testsson" not in text
    assert "Testbyrån AB" not in text


def test_sma_grupper_visas_inte_exakt(underlag_fabrik, regelbas, profil_fabrik, real_varden):
    underlag = underlag_fabrik(profil_fabrik(regelbas, {**real_varden, "P-ORG.antal_anstallda": 3}))
    anstallda = next(uppgift for uppgift in underlag.uppgifter if uppgift.id == "P-ORG.antal_anstallda")
    assert anstallda.varde == SKYDDAD_VISNING


def test_okand_uppgift_skickas_som_okand(underlag_fabrik, regelbas, profil_fabrik, real_varden):
    underlag = underlag_fabrik(profil_fabrik(regelbas, real_varden, okanda=("P-KUND.andel_riskbransch",)))
    uppgift = next(uppgift for uppgift in underlag.uppgifter if uppgift.id == "P-KUND.andel_riskbransch")
    assert (uppgift.varde, uppgift.bekraftad) == ("okänt", False)
    assert next(post for post in underlag.sarbarheter if post.id == "S-KUND-01").galler == "okänt"


def test_personuppgift_i_tillatelselistan_stoppas(regelbas, profil_fabrik, real_varden):
    lista = regelbas.tillatelselistor["risk_per_tjanst"]
    felaktig = Tillatelselista(id=lista.id, falt=(*lista.falt, "P-ROLL.ffr_namn"), undvik=lista.undvik)
    andrad = regelbas.model_copy(update={"tillatelselistor": {lista.id: felaktig}})
    profil = profil_fabrik(andrad, real_varden)
    ((avsnitt_id, tjanst),) = tjanster_med_avsnitt(_bedomning(andrad, profil))
    with pytest.raises(UnderlagsFel, match="P-ROLL.ffr_namn är en personuppgift"):
        bygg_underlag(andrad, profil, tjanst, avsnitt_id)


def test_tjanst_som_inte_erbjuds_far_inget_riskavsnitt(regelbas, profil_fabrik, real_varden):
    profil = profil_fabrik(regelbas, {**real_varden, "P-TJ.T-RED-01.erbjuds": False})
    assert tjanster_med_avsnitt(_bedomning(regelbas, profil)) == []

@pytest.mark.parametrize("antal",[0,3,4,5])
def test_smagruppsandel_och_antal_undertrycks_tillsammans(regelbas,profil_fabrik,real_varden,antal):
    from riskanalys.regelverk.modeller import Falt
    from riskanalys.regelverk.urval import valj
    from riskanalys.bedomning.motor import bedom
    from riskanalys.dokument.underlag import bygg_underlag
    f=regelbas.falt["P-KUND.andel_riskbransch"].model_copy(update={"smagrupp":True,"antalfalt":"P-KUND.antal_riskbransch","basfalt":"P-KUND.bas"})
    count=Falt(id="P-KUND.antal_riskbransch",typ="heltal",fraga="Antal?",varfor="Test",smagrupp=True)
    rb=regelbas.model_copy(update={"falt":{**regelbas.falt,f.id:f,count.id:count}})
    p=profil_fabrik(rb,{**real_varden,f.id:antal/100,count.id:antal})
    t=bedom(rb,valj(rb,p.byra.regelpaket,p.byra.datum,p.byra.lan),p).tjanster[0]
    a=bygg_underlag(rb,p,t,"D-ARB.6.1")
    value=next(u.varde for u in a.uppgifter if u.id==f.id)
    assert value==(SKYDDAD_VISNING if antal<5 else "5 %")
