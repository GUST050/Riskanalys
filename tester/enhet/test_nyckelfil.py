"""Lokala API-nycklar i en fil utanför repot. Alla nycklar är syntetiska."""

import os
from pathlib import Path

import pytest

from riskanalys.cli import main
from riskanalys.fel import RiskanalysFel
from riskanalys.nyckelfil import STANDARDFIL, ladda_nycklar, nyckelfil

NYCKEL = "syntetisk-nyckel-123"


def test_provsviten_laser_aldrig_den_riktiga_nyckelfilen():
    assert nyckelfil() != STANDARDFIL.expanduser()
    assert not nyckelfil().exists()


def skriv(fil: Path, text: str, rattigheter: int = 0o600) -> Path:
    fil.write_text(text, encoding="utf-8")
    fil.chmod(rattigheter)
    return fil


def test_saknad_fil_laddar_inget(tmp_path):
    miljo: dict[str, str] = {}
    assert ladda_nycklar(tmp_path / "saknas.env", miljo) == ()
    assert miljo == {}


def test_laddar_tillatna_nycklar_och_ignorerar_ovriga(tmp_path):
    fil = skriv(tmp_path / ".env", (
        "# kommentar\n\n"
        f'export ANTHROPIC_API_KEY="{NYCKEL}"\n'
        "RISKANALYS_SCB_API_KEY='scb-123'\n"
        "ANNAN_HEMLIGHET=ska-inte-laddas\n"
    ))
    miljo: dict[str, str] = {}
    assert ladda_nycklar(fil, miljo) == ("ANTHROPIC_API_KEY", "RISKANALYS_SCB_API_KEY")
    assert miljo == {"ANTHROPIC_API_KEY": NYCKEL, "RISKANALYS_SCB_API_KEY": "scb-123"}


def test_variabel_som_redan_finns_i_terminalen_vinner(tmp_path):
    fil = skriv(tmp_path / ".env", f"ANTHROPIC_API_KEY={NYCKEL}\n")
    miljo = {"ANTHROPIC_API_KEY": "fran-terminalen"}
    assert ladda_nycklar(fil, miljo) == ()
    assert miljo == {"ANTHROPIC_API_KEY": "fran-terminalen"}


def test_fil_som_andra_kan_lasa_stoppas_med_chmod_anvisning(tmp_path):
    fil = skriv(tmp_path / ".env", f"ANTHROPIC_API_KEY={NYCKEL}\n", 0o644)
    miljo: dict[str, str] = {}
    with pytest.raises(RiskanalysFel, match="chmod 600") as fel:
        ladda_nycklar(fil, miljo)
    assert NYCKEL not in str(fel.value)
    assert miljo == {}


def test_felaktig_rad_anger_radnummer_men_inte_innehall(tmp_path):
    fil = skriv(tmp_path / ".env", f"ANTHROPIC_API_KEY={NYCKEL}\n{NYCKEL}\n")
    with pytest.raises(RiskanalysFel, match="Rad 2") as fel:
        ladda_nycklar(fil, {})
    assert NYCKEL not in str(fel.value)


def test_cli_laddar_nyckelfilen_fore_kommandot(tmp_path, monkeypatch):
    fil = skriv(tmp_path / ".env", f"ANTHROPIC_API_KEY={NYCKEL}\n")
    monkeypatch.setenv("RISKANALYS_NYCKELFIL", str(fil))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    monkeypatch.setenv("RISKANALYS_DATA", str(tmp_path / "data"))
    main(["profil", "finnsinte"])
    assert os.environ["ANTHROPIC_API_KEY"] == NYCKEL


def test_cli_visar_fel_for_oskyddad_nyckelfil_utan_att_visa_nyckeln(tmp_path, monkeypatch, capsys):
    fil = skriv(tmp_path / ".env", f"ANTHROPIC_API_KEY={NYCKEL}\n", 0o644)
    monkeypatch.setenv("RISKANALYS_NYCKELFIL", str(fil))
    assert main(["regelbas", "validera"]) == 1
    fel = capsys.readouterr().err
    assert "chmod 600" in fel
    assert NYCKEL not in fel
