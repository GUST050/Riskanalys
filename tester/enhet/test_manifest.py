import pytest

from riskanalys.lagring.manifest import MANIFESTNAMN, ManifestFel, las_manifest, skriv_manifest, verifiera_manifest


def _paket(mapp):
    (mapp / "a.txt").write_text("a", encoding="utf-8")
    (mapp / "under").mkdir()
    (mapp / "under" / "b.txt").write_text("b", encoding="utf-8")
    (mapp / "under" / MANIFESTNAMN).write_text("{}", encoding="utf-8")


def test_manifest_tar_med_alla_filer_utom_sitt_eget(tmp_path):
    _paket(tmp_path)
    manifest = skriv_manifest(tmp_path, {"typ": "test"})
    assert set(manifest.filer) == {"a.txt", "under/b.txt", f"under/{MANIFESTNAMN}"}
    assert las_manifest(tmp_path).metadata == {"typ": "test"}


def test_oforandrat_paket_verifieras(tmp_path):
    _paket(tmp_path)
    skriv_manifest(tmp_path, {})
    assert verifiera_manifest(tmp_path) == []


def test_andrad_fil_upptacks(tmp_path):
    _paket(tmp_path)
    skriv_manifest(tmp_path, {})
    (tmp_path / "a.txt").write_text("ändrad", encoding="utf-8")
    assert verifiera_manifest(tmp_path) == ["Fil ändrad: a.txt"]


def test_borttagen_fil_upptacks(tmp_path):
    _paket(tmp_path)
    skriv_manifest(tmp_path, {})
    (tmp_path / "under" / "b.txt").unlink()
    assert verifiera_manifest(tmp_path) == ["Fil saknas: under/b.txt"]


def test_tillagd_fil_upptacks(tmp_path):
    _paket(tmp_path)
    skriv_manifest(tmp_path, {})
    (tmp_path / "ny.txt").write_text("x", encoding="utf-8")
    assert verifiera_manifest(tmp_path) == ["Fil finns inte i manifestet: ny.txt"]


def test_saknat_manifest_rapporteras(tmp_path):
    assert verifiera_manifest(tmp_path) == [f"Manifest saknas i {tmp_path}."]


def test_manifest_innehaller_programversion_och_commit(tmp_path):
    manifest = skriv_manifest(tmp_path, {})
    assert manifest.programversion == "0.1.0"
    assert manifest.git_commit


@pytest.mark.parametrize("innehall", ["{inte json", "{}", '{"skapad": "igår"}'])
def test_skadat_manifest_rapporteras_utan_krasch(tmp_path, innehall):
    _paket(tmp_path)
    skriv_manifest(tmp_path, {})
    (tmp_path / MANIFESTNAMN).write_text(innehall, encoding="utf-8")
    assert verifiera_manifest(tmp_path) == [f"Manifestet i {tmp_path} är skadat och kan inte läsas."]
    with pytest.raises(ManifestFel, match="Återställ mappen från säkerhetskopian"):
        las_manifest(tmp_path)


def test_manifest_med_fel_kodning_rapporteras_utan_krasch(tmp_path):
    skriv_manifest(tmp_path, {})
    (tmp_path / MANIFESTNAMN).write_bytes(b"\xff\xfe\x00")
    assert verifiera_manifest(tmp_path) == [f"Manifestet i {tmp_path} är skadat och kan inte läsas."]


@pytest.mark.parametrize("namn", [".DS_Store", "._beslut.yaml", "Icon\r", ".localized", "Thumbs.db", "desktop.ini"])
def test_systemfiler_fran_finder_och_utforskaren_paverkar_inte_manifestet(tmp_path, namn):
    """Slutgranskningen 2026-10-10, Important #3: att öppna ett paket i Finder får inte göra det ogiltigt."""
    (tmp_path / "under").mkdir()
    (tmp_path / "under" / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "under" / namn).write_bytes(b"finns redan")
    manifest = skriv_manifest(tmp_path, {"typ": "test"})
    assert list(manifest.filer) == ["under/a.txt"]
    (tmp_path / namn).write_bytes(b"skapad efter manifestet")
    assert verifiera_manifest(tmp_path) == []
