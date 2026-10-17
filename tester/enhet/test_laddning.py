from datetime import date

import pytest

from riskanalys.regelverk.laddning import (
    RegelbasFel,
    ladda_regelbas,
    lydelsetextens_kontrollsumma,
    regelbasens_kontrollsumma,
    regelbasfiler,
)
from riskanalys.regelverk.modeller import Sakkunnig
from riskanalys.regelverk.villkor import Faltdef


def test_minimal_regelbas_laddas(minimal_rot):
    regelbas = ladda_regelbas(minimal_rot)
    assert regelbas.version == "0.0.1"
    assert set(regelbas.krav) == {"KRV-1"}
    assert set(regelbas.regelpaket) == {"RP-1"}
    assert regelbas.metod.sannolikhet.id == "BT-SANN-01"
    assert regelbas.kontrollsumma.startswith("sha256:")
    assert regelbas.krav["KRV-1"].galler_om == {"alla": []}
    assert regelbas.krav["KRV-1"].belagg == ("dokument",)


def test_paragrafkartan_laddas_med_rader_och_giltighet(minimal_regelbas):
    karta = minimal_regelbas.regelpaket["RP-1"].paragrafkarta
    assert [(rad.lagrum, rad.hanterad) for rad in karta.rader] == [("2 kap. 1 §", True), ("2 kap. 2 §", True)]
    assert karta.ohanterade() == ()
    assert karta.galler(date(2024, 7, 1))
    assert not karta.galler(date(2024, 6, 30))


def _med_krav(regelbas, **andringar):
    krav = regelbas.krav["KRV-1"].model_copy(update=andringar)
    return regelbas.model_copy(update={"krav": {**regelbas.krav, "KRV-1": krav}})


def _med_lydelse(regelbas, **andringar):
    lydelse = regelbas.lydelser["LYD-1"].model_copy(update=andringar)
    return regelbas.model_copy(update={"lydelser": {**regelbas.lydelser, "LYD-1": lydelse}})


def _med_kalla(regelbas, **andringar):
    kalla = regelbas.kallor["SRC-1"].model_copy(update=andringar)
    return regelbas.model_copy(update={"kallor": {**regelbas.kallor, "SRC-1": kalla}})


def test_sakkunnigstatus_galler_bara_det_granskade_innehallet(minimal_regelbas):
    summa = minimal_regelbas.kravets_innehallssumma("KRV-1")
    signatur = Sakkunnig(status="verifierad", av="Testsakkunnig", datum=date(2026, 10, 1), kontrollsumma=summa)
    signerad = _med_krav(minimal_regelbas, sakkunnig=signatur)
    assert signerad.kravets_innehallssumma("KRV-1") == summa
    assert signatur.galler(signerad.kravets_innehallssumma("KRV-1"))
    assert not signatur.galler(_med_krav(signerad, text="Ett annat krav.").kravets_innehallssumma("KRV-1"))


@pytest.mark.parametrize(
    ("andra", "andras"),
    [
        (lambda rb: _med_lydelse(rb, text_kontrollsumma="sha256:" + "1" * 64), True),
        (lambda rb: _med_lydelse(rb, upphor=date(2030, 1, 1)), True),
        (lambda rb: _med_kalla(rb, geografi=("Västra Götaland", "Halland")), True),
        (lambda rb: _med_kalla(rb, hamtad=date(2026, 12, 1), url="https://example.se/ny"), False),
    ],
)
def test_kravets_summa_omfattar_refererad_lydelse_och_kallans_giltighet(minimal_regelbas, andra, andras):
    fore = minimal_regelbas.kravets_innehallssumma("KRV-1")
    assert (andra(minimal_regelbas).kravets_innehallssumma("KRV-1") != fore) is andras


def test_kartans_summa_omfattar_lydelser_och_paragrafindelning(minimal_regelbas):
    fore = minimal_regelbas.kartans_innehallssumma("RP-1")
    assert _med_lydelse(minimal_regelbas, text_kontrollsumma="sha256:" + "1" * 64).kartans_innehallssumma("RP-1") != fore
    assert _med_kalla(minimal_regelbas, paragrafer=("2 kap. 1 §", "2 kap. 2 §")).kartans_innehallssumma("RP-1") != fore


def test_lydelsetextens_kontrollsumma_bortser_fran_radbrytningar(minimal_filer):
    text = minimal_filer["lydelsetexter/LYD-1.txt"]
    summa = minimal_filer["lydelser.yaml"][0]["text_kontrollsumma"]
    assert lydelsetextens_kontrollsumma(text) == summa
    assert lydelsetextens_kontrollsumma("  " + text.replace("\n", "\n   ")) == summa
    assert lydelsetextens_kontrollsumma(text.replace("allmän", "särskild")) != summa


def test_saknad_lydelsetext_rapporteras(minimal_rot):
    (minimal_rot / "lydelsetexter" / "LYD-1.txt").unlink()
    with pytest.raises(RegelbasFel, match="lydelsetexter/LYD-1.txt: texten till lydelsen LYD-1 saknas"):
        ladda_regelbas(minimal_rot)


def test_andrad_lydelsetext_rapporteras(minimal_rot):
    (minimal_rot / "lydelsetexter" / "LYD-1.txt").write_text("En annan text.", encoding="utf-8")
    with pytest.raises(RegelbasFel, match="stämmer inte med text_kontrollsumma"):
        ladda_regelbas(minimal_rot)


def test_lydelse_utan_textkontrollsumma_vagras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    lydelser = minimal_filer["lydelser.yaml"]
    del lydelser[0]["text_kontrollsumma"]
    rot = skriv_minimal_regelbas(tmp_path / "rb", {"lydelser.yaml": lydelser})
    with pytest.raises(RegelbasFel, match="lydelser.yaml, post 1: text_kontrollsumma"):
        ladda_regelbas(rot)


def test_krav_utan_tillamplighet_eller_belagg_vagras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    krav = minimal_filer["krav/test.yaml"]
    del krav[0]["galler_om"]
    krav[0]["belagg"] = []
    rot = skriv_minimal_regelbas(tmp_path / "rb", {"krav/test.yaml": krav})
    with pytest.raises(RegelbasFel) as fel:
        ladda_regelbas(rot)
    assert "krav/test.yaml, post 1: galler_om" in str(fel.value)
    assert "belagg" in str(fel.value)


def test_okant_slag_av_belagg_vagras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    krav = minimal_filer["krav/test.yaml"]
    krav[0]["belagg"] = ["mejl"]
    rot = skriv_minimal_regelbas(tmp_path / "rb", {"krav/test.yaml": krav})
    with pytest.raises(RegelbasFel, match="krav/test.yaml, post 1: belagg"):
        ladda_regelbas(rot)


def test_lydelsetexterna_ingar_i_regelbasens_filer(minimal_rot):
    assert minimal_rot / "lydelsetexter" / "LYD-1.txt" in regelbasfiler(minimal_rot)


def test_faltdefinitioner(minimal_regelbas):
    assert minimal_regelbas.faltdefinitioner()["P-C.utf"] == Faltdef("P-C.utf", "val", ("finns", "saknas"))


def test_alla_id_innehaller_poster_och_regler(minimal_regelbas):
    alla = minimal_regelbas.alla_id()
    assert {"P-A", "SRC-1", "LYD-1", "KRV-1", "H-1", "S-1", "C-1", "T-1", "B-1"} <= alla
    assert {"BT-MATRIS-01", "BT-SANN-01", "BT-KVAR-02"} <= alla


def test_saknad_mapp_vagras(tmp_path):
    with pytest.raises(RegelbasFel, match="finns inte"):
        ladda_regelbas(tmp_path / "saknas")


def test_saknad_fil_rapporteras(minimal_rot):
    (minimal_rot / "falt.yaml").unlink()
    with pytest.raises(RegelbasFel, match="Filen saknas"):
        ladda_regelbas(minimal_rot)


def test_ogiltig_yaml_rapporteras(minimal_rot):
    (minimal_rot / "kataloger" / "hot.yaml").write_text("- id: [", encoding="utf-8")
    with pytest.raises(RegelbasFel, match="Ogiltig YAML"):
        ladda_regelbas(minimal_rot)


def test_okand_nyckel_i_post_rapporteras_med_fil_och_post(tmp_path, skriv_minimal_regelbas, minimal_filer):
    hot = minimal_filer["kataloger/hot.yaml"]
    hot[0]["okand"] = "x"
    rot = skriv_minimal_regelbas(tmp_path / "rb", {"kataloger/hot.yaml": hot})
    with pytest.raises(RegelbasFel, match="kataloger/hot.yaml, post 1"):
        ladda_regelbas(rot)


def test_dubblett_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    hot = minimal_filer["kataloger/hot.yaml"]
    rot = skriv_minimal_regelbas(tmp_path / "rb", {"kataloger/hot.yaml": hot + hot})
    with pytest.raises(RegelbasFel, match="H-1 finns redan"):
        ladda_regelbas(rot)


def test_alla_fel_samlas_i_ett_undantag(minimal_rot):
    (minimal_rot / "falt.yaml").unlink()
    (minimal_rot / "kallor.yaml").unlink()
    with pytest.raises(RegelbasFel) as fel:
        ladda_regelbas(minimal_rot)
    assert len(fel.value.fel) == 2


def test_kontrollsumman_andras_nar_en_fil_andras(minimal_rot):
    fore = regelbasens_kontrollsumma(minimal_rot)
    (minimal_rot / "version.yaml").write_text("regelbas_version: '0.0.2'\n", encoding="utf-8")
    assert regelbasens_kontrollsumma(minimal_rot) != fore


def test_laddning_och_dump_bevarar_kontrollrackvidd():
    from riskanalys.regelverk.modeller import Kontroll

    rb = ladda_regelbas()
    kontroll = rb.kontroller['C-07']
    assert kontroll.rackvidd
    assert Kontroll.model_validate(kontroll.model_dump(mode='json')) == kontroll
    assert kontroll.rackvidd[0].id in rb.alla_id()
