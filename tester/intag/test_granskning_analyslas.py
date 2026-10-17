"""Granskningen tar analyslåset bara med omfattningsmetod, på samma sätt som fastställelsen."""
from contextlib import contextmanager
from datetime import date

from riskanalys.bedomning.korning import kor_bedomning, las_bedomning
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.skrivning import kor_skrivning
from riskanalys.granskning.korning import GRANSKNING, kor_granskning
from riskanalys.profil.lagring import spara_profil
from tester.fixturer.m2 import DAG, bygg_delsvar

GRANSKNINGSDAG = date(2026, 11, 2)
LASMAPPAR = ("analys", "drift")


def _alla_sokvagar(byramapp):
    return {str(sokvag.relative_to(byramapp)) for sokvag in byramapp.rglob("*")}


def test_granskning_utan_omfattningsmetod_skapar_inga_analys_eller_driftmappar(byra_med_profil, regelbas, giltigt_utkast):
    assert not regelbas.metod.omfattning
    kor_bedomning(byra_med_profil, regelbas)
    kor_skrivning(byra_med_profil, regelbas, Testleverantor([giltigt_utkast]))
    assert not any((byra_med_profil / namn).exists() for namn in LASMAPPAR)
    fore = _alla_sokvagar(byra_med_profil)
    kor_granskning(byra_med_profil, regelbas, GRANSKNINGSDAG)
    nya = _alla_sokvagar(byra_med_profil) - fore
    assert nya and all(sokvag.split("/")[0] == GRANSKNING for sokvag in nya)
    assert not any((byra_med_profil / namn).exists() for namn in LASMAPPAR)


def test_granskning_med_omfattningsmetod_tar_analyslaset_en_gang(tmp_path, monkeypatch, rb_intag, klar):
    from riskanalys.analys import lagring
    assert rb_intag.metod.omfattning
    spara_profil(tmp_path, klar)
    b = las_bedomning(kor_bedomning(tmp_path, rb_intag))
    kor_skrivning(tmp_path, rb_intag, Testleverantor(bygg_delsvar(rb_intag, klar, b)))
    original = lagring.analyslas
    lasta = []

    @contextmanager
    def raknande_las(byramapp):
        with original(byramapp):
            lasta.append(byramapp)
            yield

    monkeypatch.setattr(lagring, "analyslas", raknande_las)
    kor_granskning(tmp_path, rb_intag, DAG)
    assert lasta == [tmp_path]
