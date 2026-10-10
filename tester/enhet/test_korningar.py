import pytest

from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.korningar import avslutade_korningar, ny_korningsmapp, senaste_korning
from riskanalys.lagring.manifest import skriv_manifest


def test_utan_korning_namns_kommandot_som_ska_koras_forst(tmp_path):
    with pytest.raises(RiskanalysFel, match="Kör 'riskanalys bedom testbyra' först"):
        senaste_korning(tmp_path, "bedomningar", "bedom testbyra")


def test_korningsmappar_skrivs_aldrig_over(tmp_path):
    mappar = [ny_korningsmapp(tmp_path, "x") for _ in range(3)]
    assert len(set(mappar)) == 3
    for mapp in mappar:
        skriv_manifest(mapp, {})
    assert avslutade_korningar(tmp_path, "x") == mappar


def test_avbruten_korning_utan_manifest_raknas_inte(tmp_path):
    forsta = ny_korningsmapp(tmp_path, "x")
    skriv_manifest(forsta, {})
    ny_korningsmapp(tmp_path, "x")
    assert senaste_korning(tmp_path, "x", "k") == forsta
