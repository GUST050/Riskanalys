from datetime import date

import pytest

from riskanalys.bedomning.motor import RISKNIVAER, SANNOLIKHETER, bedom, steg
from riskanalys.regelverk.urval import valj


def _bedom(regelbas, profil):
    urval = valj(regelbas, "RP-RED-VG", date(2026, 11, 1), "Västra Götaland")
    return bedom(regelbas, urval, profil)


def _nivaer(del_):
    return (del_.sannolikhet, del_.konsekvens, del_.risk)


def test_verklighetsnara_fall(regelbas, profil_fabrik, real_varden):
    bedomning = _bedom(regelbas, profil_fabrik(regelbas, real_varden))
    (tjanst,) = bedomning.tjanster
    assert bedomning.status == "slutlig"
    assert tjanst.erbjuds is True
    assert tjanst.tillampade_sarbarheter == ("S-KUND-01", "S-KANAL-01")
    assert _nivaer(tjanst.inneboende) == ("hög", "betydande", "hög")
    assert _nivaer(tjanst.terrorfinansiering) == ("låg", "allvarlig", "måttlig")
    assert tjanst.kvarstaende == "hög"
    assert tjanst.regelspar == ("BT-SANN-01", "BT-KONS-01", "BT-MATRIS-08", "BT-TF-01", "BT-MATRIS-03", "BT-KVAR-01")
    assert tjanst.okanda_uppgifter == ()


def test_belagd_kontroll_sanker_kvarstaende_risk_ett_steg(regelbas, profil_fabrik, real_varden):
    varden = {**real_varden, "P-KONTROLL.C-07.genomforande": "belagt"}
    (tjanst,) = _bedom(regelbas, profil_fabrik(regelbas, varden)).tjanster
    assert tjanst.kontroller[0].fungerar_och_ar_belagd is True
    assert tjanst.kvarstaende == "måttlig"
    assert tjanst.regelspar[-1] == "BT-KVAR-02"


def test_kontroll_som_saknas_i_rutinerna_sanker_inte_risken(regelbas, profil_fabrik, real_varden):
    varden = {**real_varden, "P-KONTROLL.C-07.utformning": "saknas", "P-KONTROLL.C-07.genomforande": "belagt"}
    (tjanst,) = _bedom(regelbas, profil_fabrik(regelbas, varden)).tjanster
    assert tjanst.kvarstaende == "hög"
    assert tjanst.regelspar[-1] == "BT-KVAR-01"


def test_tjanst_som_inte_erbjuds_far_inga_nivaer(regelbas, profil_fabrik, real_varden):
    varden = {**real_varden, "P-TJ.T-RED-01.erbjuds": False}
    bedomning = _bedom(regelbas, profil_fabrik(regelbas, varden))
    (tjanst,) = bedomning.tjanster
    assert tjanst.erbjuds is False
    assert tjanst.inneboende is None
    assert tjanst.kvarstaende is None
    assert bedomning.status == "slutlig"


def test_okand_uppgift_ger_forsiktig_och_preliminar_bedomning(regelbas, profil_fabrik, real_varden):
    profil = profil_fabrik(regelbas, real_varden, okanda=("P-KUND.andel_riskbransch",))
    bedomning = _bedom(regelbas, profil)
    (tjanst,) = bedomning.tjanster
    assert bedomning.status == "preliminär"
    assert tjanst.okanda_uppgifter == ("P-KUND.andel_riskbransch",)
    assert "S-KUND-01" in tjanst.tillampade_sarbarheter


def test_okant_erbjudande_bedoms_preliminart(regelbas, profil_fabrik, real_varden):
    profil = profil_fabrik(regelbas, real_varden, okanda=("P-TJ.T-RED-01.erbjuds",))
    (tjanst,) = _bedom(regelbas, profil).tjanster
    assert tjanst.erbjuds is None
    assert tjanst.inneboende is not None
    assert tjanst.status == "preliminär"


def test_okand_kontrolluppgift_ger_preliminar_bedomning(regelbas, profil_fabrik, real_varden):
    profil = profil_fabrik(regelbas, real_varden, okanda=("P-KONTROLL.C-07.genomforande",))
    (tjanst,) = _bedom(regelbas, profil).tjanster
    assert tjanst.okanda_uppgifter == ("P-KONTROLL.C-07.genomforande",)
    assert tjanst.kontroller[0].fungerar_och_ar_belagd is False
    assert tjanst.kvarstaende == "hög"


def test_alla_sarbarheter_ger_hogsta_sannolikhet_och_hojd_terrorfinansiering(regelbas, profil_fabrik, real_varden):
    varden = {**real_varden, "P-KUND.andel_kontant": 0.2, "P-VERK.juniora_konsulter": True}
    (tjanst,) = _bedom(regelbas, profil_fabrik(regelbas, varden)).tjanster
    assert tjanst.inneboende.sannolikhet == "hög"
    assert _nivaer(tjanst.terrorfinansiering) == ("medel", "allvarlig", "hög")
    assert tjanst.regelspar[4] == "BT-MATRIS-06"


def test_ingen_sarbarhet_ger_grundnivaerna(regelbas, profil_fabrik, real_varden):
    varden = {**real_varden, "P-KUND.andel_riskbransch": 0.1, "P-KANAL.andel_digitalt_underlag": 0.2}
    (tjanst,) = _bedom(regelbas, profil_fabrik(regelbas, varden)).tjanster
    assert tjanst.tillampade_sarbarheter == ()
    assert _nivaer(tjanst.inneboende) == ("medel", "betydande", "måttlig")
    assert tjanst.regelspar[2] == "BT-MATRIS-05"


@pytest.mark.parametrize(
    ("niva", "antal", "skala", "vantat"),
    [
        ("medel", 2, SANNOLIKHETER, "hög"),
        ("låg", -1, SANNOLIKHETER, "låg"),
        ("mycket hög", -1, RISKNIVAER, "hög"),
        ("låg", -1, RISKNIVAER, "låg"),
    ],
)
def test_steg_stannar_inom_skalan(niva, antal, skala, vantat):
    assert steg(niva, antal, skala) == vantat


def test_bedomningen_ar_deterministisk_och_bar_regelbasens_version(regelbas, profil_fabrik, real_varden):
    profil = profil_fabrik(regelbas, real_varden)
    forsta, andra = _bedom(regelbas, profil), _bedom(regelbas, profil)
    assert forsta == andra
    assert forsta.regelbas_version == "0.1.0"
    assert forsta.regelbas_kontrollsumma == regelbas.kontrollsumma


def test_regelbas_utan_scenariometod_ger_inga_scenarier(regelbas, profil_fabrik, real_varden):
    assert regelbas.metod.scenario is None
    (tjanst,) = _bedom(regelbas, profil_fabrik(regelbas, real_varden)).tjanster
    assert tjanst.scenarier == ()
    assert "scenarier" not in tjanst.model_dump(mode="json")
