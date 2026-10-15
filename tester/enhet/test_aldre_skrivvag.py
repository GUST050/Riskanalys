"""Den äldre skrivvägen utan faktablad skyddar inte AI-begäran och är stängd för riktiga AI-anrop (spec 8.4.10)."""

import pytest

from riskanalys.bedomning.korning import kor_bedomning
from riskanalys.dokument.leverantor import LeverantorFel, Testleverantor
from riskanalys.dokument.skrivning import UTKAST, kor_skrivning, skriv_avsnitt
from riskanalys.lagring.korningar import avslutade_korningar


class RiktigLeverantor:
    """Står för en riktig AI-leverantör. Registrerar anrop i stället för att göra dem."""

    namn = "claude"
    modell = "prov"

    def __init__(self):
        self.anrop = []

    def skriv(self, underlag, aterkoppling):
        self.anrop.append((underlag, list(aterkoppling)))
        raise AssertionError("En riktig leverantör får inte anropas i den äldre skrivvägen.")

    def skriv_del(self, anrop):
        self.anrop.append(anrop)
        raise AssertionError("En riktig leverantör får inte anropas i den äldre skrivvägen.")


def test_regelbasen_saknar_omfattningsmetod(regelbas):
    assert not regelbas.metod.omfattning


def test_riktig_leverantor_vagras_innan_nagot_anrop(byra_med_profil, regelbas):
    kor_bedomning(byra_med_profil, regelbas)
    leverantor = RiktigLeverantor()
    with pytest.raises(LeverantorFel, match="äldre skrivvägen"):
        kor_skrivning(byra_med_profil, regelbas, leverantor)
    assert leverantor.anrop == []


def test_vagrad_skrivning_lamnar_ingen_utkastmapp(byra_med_profil, regelbas):
    kor_bedomning(byra_med_profil, regelbas)
    with pytest.raises(LeverantorFel):
        kor_skrivning(byra_med_profil, regelbas, RiktigLeverantor())
    assert avslutade_korningar(byra_med_profil, UTKAST) == []
    assert not (byra_med_profil / UTKAST).exists() or list((byra_med_profil / UTKAST).iterdir()) == []


def test_testleverantor_fungerar_fortfarande(byra_med_profil, regelbas, giltigt_utkast):
    kor_bedomning(byra_med_profil, regelbas)
    leverantor = Testleverantor([giltigt_utkast])
    mapp = kor_skrivning(byra_med_profil, regelbas, leverantor)
    assert mapp.parent.name == UTKAST
    assert len(leverantor.anrop) == 1


def test_skriv_avsnitt_vagrar_riktig_leverantor_innan_nagot_anrop(real_underlag):
    leverantor = RiktigLeverantor()
    sparade = []
    with pytest.raises(LeverantorFel, match="äldre skrivvägen"):
        skriv_avsnitt(leverantor, real_underlag, ("Testa Testsson",), sparade.append)
    assert leverantor.anrop == [] and sparade == []


def test_skriv_avsnitt_fungerar_med_testleverantor(real_underlag, giltigt_utkast):
    leverantor = Testleverantor([giltigt_utkast])
    resultat = skriv_avsnitt(leverantor, real_underlag, ("Testa Testsson",))
    assert resultat.godkant_utkast is not None and len(leverantor.anrop) == 1
