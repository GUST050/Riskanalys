import pytest

from riskanalys.dokument.platshallare import ersatt_tal, faltid_fel, platshallarfel
from riskanalys.fel import RiskanalysFel

NUM = {"P-TJ.red01_antal_kunder": "110", "P-KUND.antal_aktiva": "120"}


def test_giltig_platshallare_godtas():
    assert platshallarfel(1, "Tjänsten används av {tal:P-TJ.red01_antal_kunder} kunder.",
                          ["P-TJ.red01_antal_kunder"], NUM) == []


@pytest.mark.parametrize("text,refs,del_av_fel", [
    ("{tal:P-OKAND.x} kunder", ["P-OKAND.x"], "okänt eller skyddat"),
    ("{tal:P-KUND.antal_aktiva} kunder", ["T-RED-01"], "saknas bland styckets referenser"),
    ("{tal:P-KUND.antal_aktiva kunder", ["P-KUND.antal_aktiva"], "felskriven"),
    ("{antal} kunder", [], "otillåten platshållare"),
])
def test_otillatna_platshallare_underkanns(text, refs, del_av_fel):
    assert any(del_av_fel in f for f in platshallarfel(1, text, refs, NUM))


def test_skyddat_varde_kan_inte_refereras():
    assert platshallarfel(1, "{tal:P-GEO.antal_hogrisktredjeland}", ["P-GEO.antal_hogrisktredjeland"], NUM)


def test_falt_id_i_lopande_text_underkanns_men_inte_i_platshallare():
    assert faltid_fel(1, "Andelen P-KUND.andel_riskbransch är 15 %.")
    assert faltid_fel(1, "Hotet H-01 gäller.")
    assert faltid_fel(1, "Tjänsten har {tal:P-KUND.antal_aktiva} kunder och {roll:FfR} ansvarar.") == []


def test_ersattning_och_stopp_vid_olost():
    assert ersatt_tal("{tal:P-KUND.antal_aktiva} kunder", NUM) == "120 kunder"
    with pytest.raises(RiskanalysFel):
        ersatt_tal("{tal:P-GEO.saknas} kunder", NUM)

@pytest.mark.parametrize('text',['{roll:Fel}', '{tal:P-KUND.antal_aktiva', '{foo}', 'Något } återstår', '{{tal:P-KUND.antal_aktiva}}'])
def test_felskrivna_platshallare_stoppar_aven_sammanstallningen(text):
    with pytest.raises(RiskanalysFel):
        ersatt_tal(text, NUM)


def test_period_ersatts_med_faktapostens_period():
    assert ersatt_tal('Kunderna under {period:P-KUND.antal_aktiva}.', {},
        {'P-KUND.antal_aktiva': '2025-01-01–2025-12-31'}) == 'Kunderna under 2025-01-01–2025-12-31.'


@pytest.mark.parametrize('text,refs', [
    ('{period:P-SAKNAS.x}', ['P-SAKNAS.x']),
    ('{period:P-KUND.antal_aktiva}', []),
    ('{period:P-KUND.antal_aktiva', ['P-KUND.antal_aktiva']),
])
def test_ogiltig_period_underkanns(text, refs):
    assert platshallarfel(1, text, refs, {}, {'P-KUND.antal_aktiva': '2025-01-01–2025-12-31'})


def test_period_saknas_stoppar_sammanstallningen():
    with pytest.raises(RiskanalysFel):
        ersatt_tal('{period:P-SAKNAS.x}', {}, {})
