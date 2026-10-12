"""M1:s CLI-regressioner använder en explicit fryst v0-bas.

M2-kedjor ligger i tester/m2 och kör mot det verkliga standardpaketet.
"""
import pytest
from pathlib import Path
REPO_REGELBAS = Path(__file__).resolve().parents[1] / "fixturer" / "regelbas_v0"

@pytest.fixture(autouse=True)
def m1_cli_regelbas(monkeypatch):
    monkeypatch.setattr("riskanalys.kommandon.STANDARD_REGELBAS", REPO_REGELBAS)


@pytest.fixture
def faktablad_exempel():
    from riskanalys.dokument.faktablad import Faktablad, Faktapost
    from riskanalys.dokument.modeller import UnderlagHot
    return Faktablad(avsnitt="D-ARB.6.1", tjanst_id="T-RED-01", tjanst_namn="Löpande bokföring",
                     poster=(Faktapost(id="P-KUND.antal_aktiva", etikett="Aktiva kunder", visningsvarde="120",
                                       period="2025-01-01–2025-12-31", kalltyp="intern_statistik", status="bekräftad", tal=120.0),),
                     hot=(UnderlagHot(id="H-01", namn="Osanna fakturor", beskrivning="Syntetisk beskrivning."),
                          UnderlagHot(id="H-02", namn="Brottsvinster som intäkter", beskrivning="Syntetisk beskrivning.")),
                     sarbarheter=(), kontroller=(), regelspar=())
