from datetime import date

from riskanalys.bedomning.motor import bedom
from riskanalys.dokument.arb import bygg_arb
from riskanalys.drift.historik import Handelse, Historik
from riskanalys.regelverk.urval import valj

HISTORIK = Historik().med(Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Första."))


def _arb(regelbas, profil, utkast, historik=HISTORIK):
    bedomning = bedom(regelbas, valj(regelbas, "RP-RED-VG", date(2026, 11, 1), "Västra Götaland"), profil)
    return bygg_arb(regelbas, profil, bedomning, utkast, historik)


def _texter(dokument, avsnitt_id):
    return [stycke.text for stycke in dokument.avsnitt_med_id()[avsnitt_id].stycken]


def test_avsnitten_kommer_i_ordning(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    dokument = _arb(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast})
    assert [avsnitt.id for avsnitt in dokument.avsnitt] == [
        "D-ARB.1",
        "D-ARB.3",
        "D-ARB.4",
        "D-ARB.5",
        "D-ARB.6.1",
        "D-ARB.10",
    ]
    riskavsnitt = dokument.avsnitt_med_id()["D-ARB.6.1"]
    assert riskavsnitt.kalla == "ai"
    assert list(riskavsnitt.stycken[-len(giltigt_utkast.stycken):]) == giltigt_utkast.stycken
    assert riskavsnitt.stycken[0].typ == "beskrivning"
    assert "Den inneboende risken är" in riskavsnitt.stycken[0].text


def test_personer_skrivs_som_roll(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    text = _arb(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast}).model_dump_json()
    assert "{roll:FfR}" in text
    assert "Testa Testsson" not in text
    assert "Testbyrån AB" in text


def test_alla_referenser_finns_i_regelbasen(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    dokument = _arb(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast})
    referenser = {ref for avsnitt in dokument.avsnitt for stycke in avsnitt.stycken for ref in stycke.referenser}
    assert referenser <= regelbas.alla_id()


def test_utan_godkant_utkast_saknas_riskavsnittet(regelbas, profil_fabrik, real_varden):
    dokument = _arb(regelbas, profil_fabrik(regelbas, real_varden), {})
    assert "D-ARB.6.1" not in dokument.avsnitt_med_id()


def test_utan_historik_markeras_datumet(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    dokument = _arb(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast}, Historik())
    assert _texter(dokument, "D-ARB.10") == ["Datum för utvärdering saknas. [VERIFIERA]"]


def test_utvarderingsdatum_och_nasta_genomgang(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    dokument = _arb(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast})
    (text,) = _texter(dokument, "D-ARB.10")
    assert text.startswith("Riskbedömningen utvärderades senast 2026-11-01. Nästa utvärdering görs senast 2027-11-01")


def test_faststallelse_andrar_inte_utvarderingsdatumet(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    historik = HISTORIK.med(Handelse(datum=date(2026, 11, 20), typ="fastställelse", beskrivning="v1", version=1))
    dokument = _arb(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast}, historik)
    (text,) = _texter(dokument, "D-ARB.10")
    assert "utvärderades senast 2026-11-01" in text
    assert "senast 2027-11-01" in text


def test_okanda_uppgifter_markeras(regelbas, profil_fabrik, real_varden):
    profil = profil_fabrik(regelbas, real_varden, okanda=("P-ORG.antal_anstallda", "P-KUND.andel_riskbransch"))
    dokument = _arb(regelbas, profil, {})
    assert "[VERIFIERA]" in _texter(dokument, "D-ARB.1")[0]
    assert "Kunder i branscher med förhöjd risk (Löpande bokföring): Okänt, eftersom uppgifter saknas. [VERIFIERA]" in (
        _texter(dokument, "D-ARB.5")
    )


def test_sarbarheterna_beskrivs_enligt_profilen(regelbas, profil_fabrik, real_varden):
    texter = _texter(_arb(regelbas, profil_fabrik(regelbas, real_varden), {}), "D-ARB.5")
    assert "Kunder i branscher med förhöjd risk (Löpande bokföring): Gäller enligt byråns uppgifter." in texter
    assert "Juniora konsulter arbetar självständigt (Löpande bokföring): Gäller inte enligt byråns uppgifter." in texter
