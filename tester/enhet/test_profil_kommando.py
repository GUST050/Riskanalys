import pytest

from riskanalys.cli import main
from riskanalys.lagring.datamapp import byramapp
from riskanalys.profil.lagring import las_profil

NY = ["ny", "testbyra", "--regelpaket", "RP-RED-VG", "--lan", "Västra Götaland", "--datum", "2026-11-01"]


def test_ny_skapar_byra_med_tom_profil(datamapp, capsys):
    assert main(NY) == 0
    assert las_profil(byramapp("testbyra")).byra.regelpaket == "RP-RED-VG"
    assert "Nästa steg" in capsys.readouterr().out


def test_ny_med_okant_regelpaket_skapar_ingen_mapp(datamapp, capsys):
    assert main([*NY[:3], "RP-SAKNAS", *NY[4:]]) == 1
    assert "RP-SAKNAS finns inte" in capsys.readouterr().err
    assert not byramapp("testbyra").exists()


def test_ny_tva_ganger_vagras(datamapp, capsys):
    main(NY)
    assert main(NY) == 1
    assert "finns redan" in capsys.readouterr().err


def test_ogiltigt_datum_ger_svenskt_meddelande(datamapp, capsys):
    with pytest.raises(SystemExit):
        main([*NY[:-1], "1 november"])
    assert "ÅÅÅÅ-MM-DD" in capsys.readouterr().err


def test_bekrafta_med_procent(datamapp):
    main(NY)
    assert main(["bekrafta", "testbyra", "P-KUND.andel_riskbransch", "30 %", "--kalla", "Kundregistret"]) == 0
    assert las_profil(byramapp("testbyra")).uppgifter["P-KUND.andel_riskbransch"].varde == 0.3


def test_bekrafta_andel_utan_procenttecken_vagras(datamapp, capsys):
    main(NY)
    assert main(["bekrafta", "testbyra", "P-KUND.andel_riskbransch", "30", "--kalla", "Kundregistret"]) == 1
    assert "0–1 eller i procent" in capsys.readouterr().err


def test_bekrafta_utan_kalla_vagras(datamapp, capsys):
    main(NY)
    assert main(["bekrafta", "testbyra", "P-ORG.antal_anstallda", "8"]) == 1
    assert "--kalla" in capsys.readouterr().err


def test_bekrafta_ej_tillampligt(datamapp):
    main(NY)
    argv = ["bekrafta", "testbyra", "P-VERK.juniora_konsulter", "--ej-tillampligt", "--motivering", "Inga konsulter."]
    assert main(argv) == 0
    assert las_profil(byramapp("testbyra")).uppgifter["P-VERK.juniora_konsulter"].status == "ej_tillämplig"


def test_alla_varden_i_testfallet_kan_bekraftas(datamapp, real_varden, real_varden_text):
    main(NY)
    for falt_id, text in real_varden_text:
        assert main(["bekrafta", "testbyra", falt_id, text, "--kalla", "Syntetiskt testfall"]) == 0
    uppgifter = las_profil(byramapp("testbyra")).uppgifter
    assert {falt_id: uppgifter[falt_id].varde for falt_id in real_varden} == real_varden


def test_profil_visar_saknade_kritiska_uppgifter(datamapp, capsys):
    main(NY)
    capsys.readouterr()
    assert main(["profil", "testbyra"]) == 0
    assert "Kritiska uppgifter som saknas: 11" in capsys.readouterr().out


def test_kommando_for_okand_byra(datamapp, capsys):
    assert main(["profil", "saknas"]) == 1
    assert "finns inte" in capsys.readouterr().err
