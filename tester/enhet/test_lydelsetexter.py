"""Regressioner för researchverktygets verkliga kommandorad, med syntetisk lagtext."""

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest


VERKTYG = Path(__file__).resolve().parents[2] / "docs/research/verktyg/lydelsetexter.py"


def kor(tmp_path, slag, text, *lagrum):
    fil = tmp_path / "syntetisk källa.txt"
    fil.write_text(text, encoding="utf-8")
    return subprocess.run(
        [sys.executable, "-I", str(VERKTYG), slag, str(fil), *lagrum],
        capture_output=True, text=True, check=False,
    )


def summa(text):
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_sfs_kommando_ger_summa_for_befintlig_paragraf(tmp_path):
    svar = kor(tmp_path, "sfs", "1 kap. Inledning\n1 § Syntetisk regel. Lag (2026:1).\n", "1 kap. 1 §")
    assert svar.returncode == 0
    assert svar.stdout.strip() == "1 kap. 1 § " + summa("Syntetisk regel.")


def test_sfs_kommando_skiljer_datumlydelser(tmp_path):
    svar = kor(tmp_path, "sfs", "1 kap. Inledning\n1 § /Upphör att gälla U:2026-11-20/ Äldre regel.\n1 § /Träder i kraft I:2026-11-20/ Ny regel.\n",
               "1 kap. 1 § [U:2026-11-20]", "1 kap. 1 § [I:2026-11-20]")
    assert svar.returncode == 0
    assert svar.stdout.splitlines() == [
        "1 kap. 1 § [U:2026-11-20] " + summa("Äldre regel."),
        "1 kap. 1 § [I:2026-11-20] " + summa("Ny regel."),
    ]


def test_sfs_utan_kapitel_kan_lasas(tmp_path):
    svar = kor(tmp_path, "sfs", "Förordning\n1 § En annan regel. Förordning (2026:2).\n", "1 §")
    assert svar.returncode == 0
    assert svar.stdout.strip() == "1 § " + summa("En annan regel.")


def test_sfs_brodtext_fore_hanvisning_far_inte_forsvinna(tmp_path):
    svar = kor(tmp_path, "sfs", "1 kap. Inledning\n1 § Den som driver\nsin verksamhet som anställd ska följa 6 kap. 1 och\n2 §§ samma lag.\n2 § Nästa regel.\n", "1 kap. 1 §")
    assert svar.returncode == 0
    assert svar.stdout.strip() == "1 kap. 1 § " + summa("Den som driver sin verksamhet som anställd ska följa 6 kap. 1 och 2 §§ samma lag.")


def test_fs_kommando_behaller_summa_utan_allmanna_rad(tmp_path):
    svar = kor(tmp_path, "fs", "1 kap. Inledning\n1 § Bindande regel.\nAllmänna råd\nEtt råd.\n", "1 kap. 1 §")
    assert svar.returncode == 0
    assert svar.stdout.strip() == "1 kap. 1 § " + summa("Bindande regel.")


def test_saknad_paragraf_ger_felkod(tmp_path):
    svar = kor(tmp_path, "fs", "1 kap. Inledning\n1 § Bindande regel.\n", "1 kap. 2 §")
    assert svar.returncode == 1
    assert "1 kap. 2 § SAKNAS" in svar.stdout


def test_okant_kallformat_avvisas(tmp_path):
    svar = kor(tmp_path, "annat", "1 § Text.\n", "1 §")
    assert svar.returncode == 2
    assert "Traceback" not in svar.stderr


def test_sfs_utan_paragrafer_ger_begripligt_fel(tmp_path):
    svar = kor(tmp_path, "sfs", "Ingen författning här.\n", "1 §")
    assert svar.returncode == 1
    assert "Kontrollera" in svar.stderr
    assert "Traceback" not in svar.stderr


@pytest.mark.parametrize("fel", ["saknas", "kodning"])
def test_felaktig_kallfil_ger_begripligt_fel(tmp_path, fel):
    fil = tmp_path / "fel.txt"
    if fel == "kodning":
        fil.write_bytes(b"\xff\xfe")
    svar = subprocess.run([sys.executable, "-I", str(VERKTYG), "sfs", str(fil), "1 §"],
                          capture_output=True, text=True, check=False)
    assert svar.returncode == 1
    assert "Kontrollera" in svar.stderr
    assert "Traceback" not in svar.stderr

def test_fs_avslutande_avskiljare_ar_inte_paragraftext(tmp_path):
    text="7 kap. Uppgifter\n1 § Verksamheten ska lämna uppgifter.\n___________\n1. Dessa föreskrifter träder i kraft den 1 juli 2024."
    svar = kor(tmp_path, "fs", text, "7 kap. 1 §")
    assert svar.stdout.strip() == "7 kap. 1 § " + summa("Verksamheten ska lämna uppgifter.")
