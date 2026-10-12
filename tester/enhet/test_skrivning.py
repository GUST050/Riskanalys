import pytest

from riskanalys.dokument.leverantor import LeverantorFel, Testleverantor
from riskanalys.dokument.skrivning import las_skrivresultat, skriv_avsnitt
from riskanalys.lagring.manifest import skriv_manifest

AVBROTT = "Claude avböjde att skriva avsnittet."


def _felaktigt(utkast):
    return utkast.model_copy(update={"avsnitt": "D-ARB.6.2"})


class AvbrytandeLeverantor:
    """Svarar som när modellen avböjer: ett tomt svar med avbrott."""

    namn = "test"
    modell = "testleverantor"

    def skriv(self, underlag, aterkoppling):
        return Testleverantor([""]).skriv(underlag, aterkoppling).model_copy(update={"avbrott": AVBROTT})


def test_godkant_pa_forsta_forsoket(giltigt_utkast, real_underlag):
    resultat = skriv_avsnitt(Testleverantor([giltigt_utkast]), real_underlag, ("Testa Testsson",))
    assert len(resultat.forsok) == 1
    assert resultat.godkant_utkast == giltigt_utkast
    assert (resultat.leverantor, resultat.modell) == ("test", "testleverantor")
    assert (resultat.forsok[0].nummer, resultat.forsok[0].anrop.svar_id) == (1, "test-1")


def test_aterkoppling_skickas_vid_nytt_forsok(giltigt_utkast, real_underlag):
    leverantor = Testleverantor([_felaktigt(giltigt_utkast), giltigt_utkast])
    resultat = skriv_avsnitt(leverantor, real_underlag, ())
    assert len(resultat.forsok) == 2
    assert leverantor.anrop[0][1] == []
    assert leverantor.anrop[1][1] == list(resultat.forsok[0].fel)
    assert resultat.godkant_utkast == giltigt_utkast


def test_underkant_efter_tre_forsok(giltigt_utkast, real_underlag):
    leverantor = Testleverantor([_felaktigt(giltigt_utkast)] * 3)
    resultat = skriv_avsnitt(leverantor, real_underlag, ())
    assert len(resultat.forsok) == 3
    assert resultat.godkant_utkast is None


def test_svar_som_inte_foljer_schemat_ar_ett_underkant_forsok(giltigt_utkast, real_underlag):
    leverantor = Testleverantor(['{"avsnitt": "D-ARB.6.1"}', giltigt_utkast])
    resultat = skriv_avsnitt(leverantor, real_underlag, ())
    forsta = resultat.forsok[0]
    assert (forsta.svar, forsta.text) == (None, '{"avsnitt": "D-ARB.6.1"}')
    assert forsta.fel[0].startswith("Svaret följde inte schemat")
    assert resultat.godkant_utkast == giltigt_utkast


def test_varje_forsok_sparas_innan_nasta_anrop(giltigt_utkast, real_underlag):
    sparade = []
    with pytest.raises(LeverantorFel, match="1 förberedda svar"):
        skriv_avsnitt(Testleverantor([_felaktigt(giltigt_utkast)]), real_underlag, (), spara=sparade.append)
    assert [forsok.nummer for forsok in sparade] == [1]
    assert sparade[0].fel


def test_avbrott_sparas_och_stoppar_skrivningen(real_underlag):
    sparade = []
    with pytest.raises(LeverantorFel, match="avböjde"):
        skriv_avsnitt(AvbrytandeLeverantor(), real_underlag, (), spara=sparade.append)
    assert [(forsok.nummer, forsok.fel) for forsok in sparade] == [(1, (AVBROTT,))]


def test_skrivresultat_sparas_och_lases(tmp_path, giltigt_utkast, real_underlag):
    resultat = skriv_avsnitt(Testleverantor([giltigt_utkast]), real_underlag, ())
    (tmp_path / "D-ARB.6.1.json").write_text(resultat.model_dump_json(), encoding="utf-8")
    skriv_manifest(tmp_path, {})
    assert las_skrivresultat(tmp_path) == [resultat]
