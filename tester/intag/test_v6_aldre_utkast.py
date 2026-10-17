"""V6-byggaren avvisar utkast från en äldre skrivare tidigt, med ett fel som användaren kan åtgärda."""
import pytest

from riskanalys.bedomning.korning import BEDOMNINGAR, kor_bedomning, las_bedomning
from riskanalys.bedomning.motor import bedom
from riskanalys.dokument.arb import bygg_arb
from riskanalys.dokument.delskrivning import skriv_tjanst
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.modeller import AvsnittsUtkast, Textstycke
from riskanalys.dokument.skrivning import UTKAST, Forsok, Skrivresultat
from riskanalys.dokument.skrivversion import DELAR_V5, DELAR_V6, V5
from riskanalys.dokument.underlag import bygg_underlag, tjanster_med_avsnitt
from riskanalys.drift.historik import Historik
from riskanalys.fel import RiskanalysFel
from riskanalys.granskning.korning import GRANSKNING, kor_granskning
from riskanalys.lagring.korningar import avslutade_korningar, ny_korningsmapp
from riskanalys.lagring.manifest import skriv_manifest
from riskanalys.profil.lagring import spara_profil
from riskanalys.regelverk.urval import valj
from tester.fixturer.m2 import DAG, godkant_delsvar

ALDRE_FORMAT = "äldre format"
NY_SKRIVNING = "Kör 'riskanalys skriv' igen"
NY_GRANSKNING = "riskanalys granska"


def _aldre_utkast(rb, profil, t, avsnitt_id):
    """Ett godkänt utkast i den äldre skrivarens schema, utan tjänstidentitet."""
    stycke = Textstycke(typ="analys", text="Syntetisk text från den äldre skrivaren.", referenser=[t.tjanst])
    return AvsnittsUtkast(avsnitt=avsnitt_id, stycken=[stycke], oklarheter=[])


def _v5_resultat(rb, profil, t, avsnitt_id):
    lev = Testleverantor([godkant_delsvar(d, t) for d in DELAR_V5])
    return skriv_tjanst(lev, rb, profil, t, avsnitt_id, effort="medium", personnamn=(), spara=lambda *a: None, formatversion=V5)


def _v6_resultat(rb, profil, t, avsnitt_id):
    lev = Testleverantor([godkant_delsvar(d, t) for d in DELAR_V6])
    return skriv_tjanst(lev, rb, profil, t, avsnitt_id, effort="medium", personnamn=(), spara=lambda *a: None)


def _ar_atgardbart(fel: RiskanalysFel, avsnitt_id: str) -> bool:
    text = str(fel)
    return all(del_ in text for del_ in (avsnitt_id, ALDRE_FORMAT, NY_SKRIVNING, NY_GRANSKNING))


@pytest.mark.parametrize("aldre", [_aldre_utkast, _v5_resultat], ids=["avsnittsutkast", "v5-tjanstresultat"])
def test_v6_avvisar_aldre_utkast_tidigt_med_atgard(rb_intag, klar, aldre):
    b = bedom(rb_intag, valj(rb_intag, klar.byra.regelpaket, klar.byra.datum, klar.byra.lan), klar)
    *forsta, (sista_id, sista) = tjanster_med_avsnitt(b)
    # Bara den sista tjänsten har ett äldre utkast: varje post prövas, inte bara den första.
    utkast = {**{id: _v6_resultat(rb_intag, klar, t, id) for id, t in forsta}, sista_id: aldre(rb_intag, klar, sista, sista_id)}
    with pytest.raises(RiskanalysFel) as fel:
        bygg_arb(rb_intag, klar, b, utkast, Historik())
    assert _ar_atgardbart(fel.value, sista_id)


def _skriv_aldre_utkastkorning(byramapp, rb, profil, bedomning, bedomningsmapp):
    """En avslutad skrivning från den äldre skrivaren: Skrivresultat med godkända AvsnittsUtkast."""
    mapp = ny_korningsmapp(byramapp, UTKAST)
    for avsnitt_id, t in tjanster_med_avsnitt(bedomning):
        underlag = bygg_underlag(rb, profil, t, avsnitt_id)
        utkast = _aldre_utkast(rb, profil, t, avsnitt_id)
        leverans = Testleverantor([utkast]).skriv(underlag, [])
        forsok = Forsok(nummer=1, anrop=leverans.anrop, text=leverans.text, svar=utkast, fel=())
        post = Skrivresultat(underlag=underlag, leverantor="test", modell="testleverantor", forsok=(forsok,))
        (mapp / f"{avsnitt_id}.json").write_text(post.model_dump_json(indent=2), encoding="utf-8")
    skriv_manifest(mapp, {"typ": "utkast", "leverantor": "test", "modell": "testleverantor", "bedomning": bedomningsmapp.name})
    return mapp


@pytest.fixture
def byra_med_aldre_utkast(tmp_path, monkeypatch, rb_intag, klar):
    monkeypatch.setenv("RISKANALYS_DATA", str(tmp_path))
    byra = tmp_path / "syntetisk"
    spara_profil(byra, klar)
    bedomningsmapp = kor_bedomning(byra, rb_intag)
    _skriv_aldre_utkastkorning(byra, rb_intag, klar, las_bedomning(bedomningsmapp), bedomningsmapp)
    assert [m.name for m in avslutade_korningar(byra, BEDOMNINGAR)] == [bedomningsmapp.name]
    return byra


def test_granskning_med_aldre_utkast_ger_samma_atgardbara_fel(byra_med_aldre_utkast, rb_intag):
    with pytest.raises(RiskanalysFel) as fel:
        kor_granskning(byra_med_aldre_utkast, rb_intag, DAG)
    assert _ar_atgardbart(fel.value, "D-ARB.6")
    assert not avslutade_korningar(byra_med_aldre_utkast, GRANSKNING)


def test_granska_kommandot_visar_felet_utan_stackspar(byra_med_aldre_utkast, capsys):
    from riskanalys.cli import main
    assert main(["granska", "syntetisk", "--datum", DAG.isoformat()]) == 1
    fel = capsys.readouterr().err
    assert fel.startswith("Fel: ") and ALDRE_FORMAT in fel and NY_SKRIVNING in fel
    assert "Traceback" not in fel
