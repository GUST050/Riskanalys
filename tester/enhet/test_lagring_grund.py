import stat

import pytest

from riskanalys.lagring import datamapp as dm
from riskanalys.lagring.kontrollsumma import for_bytes, for_fil, for_text


def test_kontrollsumma_for_text_ar_stabil_och_markt():
    assert for_text("abc") == for_text("abc")
    assert for_text("abc").startswith("sha256:")
    assert for_text("abc") != for_text("abd")


def test_kontrollsumma_for_fil_motsvarar_innehallet(tmp_path):
    fil = tmp_path / "a.txt"
    fil.write_bytes(b"innehall")
    assert for_fil(fil) == for_bytes(b"innehall")


def test_datamapp_las_fran_miljovariabel(tmp_path, monkeypatch):
    monkeypatch.setenv(dm.MILJOVARIABEL, str(tmp_path / "data"))
    assert dm.datamapp() == (tmp_path / "data").resolve()


def test_datamapp_med_mellanslag_och_svenska_tecken_fungerar(tmp_path, monkeypatch):
    monkeypatch.setenv(dm.MILJOVARIABEL, str(tmp_path / "Mapp med å ä ö"))
    mapp = dm.skapa_byramapp("testbyra")
    assert mapp.is_dir()
    assert mapp.parent.name == "Mapp med å ä ö"


def test_datamapp_i_repot_vagras(monkeypatch):
    monkeypatch.setenv(dm.MILJOVARIABEL, str(dm.REPO_ROT / "data"))
    with pytest.raises(dm.DatamappFel, match="ligger i repot"):
        dm.datamapp()


@pytest.mark.parametrize("ogiltigt", ["", "../annan", "Byrå", "a b", "-borjar-med-streck", "x" * 64])
def test_ogiltigt_byra_id_vagras(tmp_path, monkeypatch, ogiltigt):
    monkeypatch.setenv(dm.MILJOVARIABEL, str(tmp_path))
    with pytest.raises(dm.DatamappFel, match="Ogiltigt byrå-ID"):
        dm.byramapp(ogiltigt)


def test_skapa_byramapp_ger_behorighet_bara_for_anvandaren(tmp_path, monkeypatch):
    monkeypatch.setenv(dm.MILJOVARIABEL, str(tmp_path / "data"))
    mapp = dm.skapa_byramapp("testbyra")
    assert stat.S_IMODE(mapp.stat().st_mode) == 0o700


def test_skapa_byramapp_tva_ganger_vagras(tmp_path, monkeypatch):
    monkeypatch.setenv(dm.MILJOVARIABEL, str(tmp_path))
    dm.skapa_byramapp("testbyra")
    with pytest.raises(dm.DatamappFel, match="finns redan"):
        dm.skapa_byramapp("testbyra")


def test_befintlig_byramapp_kraver_att_byran_finns(tmp_path, monkeypatch):
    monkeypatch.setenv(dm.MILJOVARIABEL, str(tmp_path))
    with pytest.raises(dm.DatamappFel, match="finns inte"):
        dm.befintlig_byramapp("saknas")


def test_datamapp_i_repot_med_annat_skiftlage_vagras(monkeypatch):
    """Slutgranskningen 2026-10-10, Important #6: på macOS är /users/... samma mapp som /Users/..."""
    import os
    from pathlib import Path

    annat_skiftlage = Path(str(dm.REPO_ROT).swapcase())
    if not annat_skiftlage.exists() or not os.path.samefile(annat_skiftlage, dm.REPO_ROT):
        pytest.skip("Filsystemet skiljer på stora och små bokstäver.")
    monkeypatch.setenv(dm.MILJOVARIABEL, str(annat_skiftlage / "data"))
    with pytest.raises(dm.DatamappFel, match="ligger i repot"):
        dm.datamapp()


def test_datamapp_via_symbolisk_lank_in_i_repot_vagras(monkeypatch, tmp_path):
    lank = tmp_path / "lank"
    lank.symlink_to(dm.REPO_ROT, target_is_directory=True)
    monkeypatch.setenv(dm.MILJOVARIABEL, str(lank / "data"))
    with pytest.raises(dm.DatamappFel, match="ligger i repot"):
        dm.datamapp()
