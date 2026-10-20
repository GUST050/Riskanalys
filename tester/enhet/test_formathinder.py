from datetime import date
from pathlib import Path

import pytest

from riskanalys.dokument.skrivversion import AKTUELL_DOKUMENTVERSION as FORMATVERSION, V5, V6, V7, V8
from riskanalys.dokument.modeller import Avsnitt, Dokument, Textstycke
from riskanalys.faststallelse import faststall as faststallmodul
from riskanalys.faststallelse.modeller import Beslut
from riskanalys.faststallelse.faststall import FASTSTALLDA, FaststallelseFel, faststall, formathinder, kedjehinder
from riskanalys.granskning.korning import GRANSKNING
from riskanalys.lagring.korningar import senaste_korning
from riskanalys.regelverk.laddning import ladda_regelbas


def _avsnitt(id, version):
    return Avsnitt(id=id, rubrik="Analys", kalla="ai",
                   leveransdel="lasrapport" if version == V8 else None,
                   stycken=(Textstycke(typ="beskrivning", text="Text.", referenser=["T-RED-01"]),), formatversion=version)


def _dok(*avsnitt):
    return Dokument(id="D", titel="T", avsnitt=avsnitt)


def test_blandat_format_stoppar():
    d = _dok(_avsnitt('D-ARB.6.1', FORMATVERSION))
    # Angrip formatsparren även efter manipulation förbi dokumentmodellens versionsvalidering.
    d = d.model_copy(update={'avsnitt': (*d.avsnitt, _avsnitt('D-ARB.6.2', 'D-ARB-tjanst-v3'))})
    hinder = formathinder(ladda_regelbas(), d)
    assert len(hinder) == 1 and "D-ARB.6.2" in hinder[0] and "Skriv om utkastet" in hinder[0]
    assert hinder[0].startswith("Tjänsteavsnittet D-ARB.6.2 har formatet D-ARB-tjanst-v3, men aktuellt format är ")


def test_saknad_formatmarkering_i_tjansteavsnitt_stoppar():
    (hinder,) = formathinder(ladda_regelbas(), _dok(_avsnitt("D-ARB.6.1", None)))
    assert hinder.startswith(f"Tjänsteavsnittet D-ARB.6.1 saknar formatmarkering, men aktuellt format är {FORMATVERSION}.")
    assert "har formatet" not in hinder and "utan formatmarkering" not in hinder


def test_aktuellt_format_i_alla_tjansteavsnitt_godtas():
    assert formathinder(ladda_regelbas(), _dok(_avsnitt("D-ARB.6.1", FORMATVERSION), _avsnitt("D-ARB.2", FORMATVERSION))) == []


@pytest.mark.parametrize('version', [V5, V6, V7])
def test_historiskt_format_stoppar_ny_faststallelse(version):
    (hinder,) = formathinder(ladda_regelbas(), _dok(_avsnitt('D-ARB.6.1', version)))
    assert f'har formatet {version}, men aktuellt format är {FORMATVERSION}.' in hinder
    assert 'Skriv om utkastet och granska på nytt.' in hinder


def test_aldre_regelbas_utan_omfattningsmetod_berors_inte():
    v0 = ladda_regelbas(Path(__file__).resolve().parents[1] / "fixturer" / "regelbas_v0")
    assert formathinder(v0, _dok(_avsnitt("D-ARB.6.1", None))) == []


def test_kedjehinder_anropar_formatsparren(kedja, signerad_regelbas_rot, signerad_regelbas, monkeypatch):
    granskningsmapp = senaste_korning(kedja, GRANSKNING, f"granska {kedja.name}")
    assert kedjehinder(kedja, signerad_regelbas_rot, signerad_regelbas, granskningsmapp) == []
    monkeypatch.setattr(faststallmodul, "formathinder", lambda regelbas, dokument: ["SPÄRR"])
    assert "SPÄRR" in kedjehinder(kedja, signerad_regelbas_rot, signerad_regelbas, granskningsmapp)


def test_faststall_stoppas_av_formatsparren_och_skapar_inget_paket(kedja, signerad_regelbas_rot, signerad_regelbas):
    # Kedjan är skriven på den äldre vägen (inget format i tjänsteavsnittet). Regelbasen får omfattningsmetod
    # från repots aktuella regelbas, så att formatspärren gäller.
    omfattning = ladda_regelbas().metod.omfattning
    assert omfattning and not signerad_regelbas.metod.omfattning
    regelbas = signerad_regelbas.model_copy(update={"metod": signerad_regelbas.metod.model_copy(update={"omfattning": omfattning})})
    beslut = Beslut(organ="styrelsen", datum=date(2026, 11, 15), namn="Testa Testsson", roll="FfR")
    with pytest.raises(FaststallelseFel) as fel:
        faststall(kedja, signerad_regelbas_rot, regelbas, beslut)
    assert any(h.startswith("Tjänsteavsnittet D-ARB.6.1 saknar formatmarkering") and "Skriv om utkastet" in h
               for h in fel.value.hinder), fel.value.hinder
    assert not (kedja / FASTSTALLDA / "v1").exists()
    assert not (kedja / FASTSTALLDA).exists() or list((kedja / FASTSTALLDA).iterdir()) == []
