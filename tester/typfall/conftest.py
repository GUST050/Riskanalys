"""M1:s CLI-regressioner använder en explicit fryst v0-bas.

M2-kedjor ligger i tester/m2 och kör mot det verkliga standardpaketet.
"""
import pytest
from pathlib import Path
REPO_REGELBAS = Path(__file__).resolve().parents[1] / "fixturer" / "regelbas_v0"

@pytest.fixture(autouse=True)
def m1_cli_regelbas(monkeypatch):
    monkeypatch.setattr("riskanalys.kommandon.STANDARD_REGELBAS", REPO_REGELBAS)
