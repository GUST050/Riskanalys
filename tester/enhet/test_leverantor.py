import pytest

from riskanalys.dokument.leverantor import LeverantorFel, Testleverantor, ladda_testleverantor
from riskanalys.dokument.modeller import Avsnittsunderlag, AvsnittsUtkast


def _underlag():
    return Avsnittsunderlag(
        avsnitt="D-ARB.6.1",
        rubrik="Tjänst",
        instruktion="Skriv.",
        tjanst_id="T-1",
        tjanst_namn="Tjänst",
        tjanst_beskrivning="Beskrivning.",
        nivaer={},
        hot=(),
        sarbarheter=(),
        kontroller=(),
        uppgifter=(),
        regelspar=(),
        undvik=(),
    )


def _utkast(text):
    return AvsnittsUtkast.model_validate(
        {"avsnitt": "D-ARB.6.1", "stycken": [{"typ": "analys", "text": text, "referenser": []}], "oklarheter": []}
    )


def _text(leveranssvar):
    return AvsnittsUtkast.model_validate_json(leveranssvar.text).stycken[0].text


def test_testleverantorn_svarar_i_tur_och_ordning_och_sparar_anropen():
    leverantor = Testleverantor([_utkast("ett"), _utkast("två")])
    forsta = leverantor.skriv(_underlag(), [])
    assert _text(forsta) == "ett"
    assert _text(leverantor.skriv(_underlag(), ["Rätta talet."])) == "två"
    assert [aterkoppling for _, aterkoppling in leverantor.anrop] == [[], ["Rätta talet."]]


def test_testleverantorn_fyller_i_anropsdata():
    svar = Testleverantor([_utkast("ett")]).skriv(_underlag(), [])
    assert (svar.anrop.leverantor, svar.anrop.begard_modell, svar.anrop.svarsmodell) == (
        "test",
        "testleverantor",
        "testleverantor",
    )
    assert (svar.anrop.svar_id, svar.anrop.reservmodell_svarade, svar.avbrott) == ("test-1", False, None)


def test_testleverantorn_kan_ge_ett_svar_som_inte_foljer_schemat():
    assert Testleverantor(['{"avsnitt": "D-ARB.6.1"}']).skriv(_underlag(), []).text == '{"avsnitt": "D-ARB.6.1"}'


def test_testleverantorn_utan_fler_svar_ger_fel():
    leverantor = Testleverantor([_utkast("ett")])
    leverantor.skriv(_underlag(), [])
    with pytest.raises(LeverantorFel, match="1 förberedda svar"):
        leverantor.skriv(_underlag(), [])


def test_testsvar_lases_fran_fil(tmp_path):
    fil = tmp_path / "svar.json"
    fil.write_text("[" + _utkast("ett").model_dump_json() + "]", encoding="utf-8")
    leverantor = ladda_testleverantor(fil)
    assert _text(leverantor.skriv(_underlag(), [])) == "ett"


def test_saknad_testsvarsfil_ger_fel(tmp_path):
    with pytest.raises(LeverantorFel, match="saknas"):
        ladda_testleverantor(tmp_path / "saknas.json")


def test_ogiltig_testsvarsfil_ger_fel(tmp_path):
    fil = tmp_path / "svar.json"
    fil.write_text('[{"avsnitt": "D-ARB.6.1"}]', encoding="utf-8")
    with pytest.raises(LeverantorFel, match="ogiltig"):
        ladda_testleverantor(fil)
