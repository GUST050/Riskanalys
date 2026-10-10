from riskanalys.bedomning.korning import BEDOMNINGAR
from riskanalys.cli import main
from riskanalys.dokument.skrivning import UTKAST, Forsok
from riskanalys.lagring.korningar import avslutade_korningar
from riskanalys.lagring.manifest import las_manifest


def _skriv(fil):
    return main(["skriv", "testbyra", "--leverantor", "test", "--testsvar", str(fil)])


def test_skriv_fore_bedom_sager_vilket_steg_som_saknas(byra_med_profil, testsvarsfil, capsys):
    assert _skriv(testsvarsfil) == 1
    assert "Kör 'riskanalys bedom testbyra' först" in capsys.readouterr().err


def test_skriv_med_testleverantor(byra_med_profil, testsvarsfil, capsys):
    main(["bedom", "testbyra"])
    assert _skriv(testsvarsfil) == 0
    assert "D-ARB.6.1 Löpande bokföring: godkänt efter 1 försök." in capsys.readouterr().out
    (mapp,) = avslutade_korningar(byra_med_profil, UTKAST)
    manifest = las_manifest(mapp)
    assert manifest.metadata["bedomning"] == avslutade_korningar(byra_med_profil, BEDOMNINGAR)[-1].name
    assert {"D-ARB.6.1.json", "D-ARB.6.1/underlag.json", "D-ARB.6.1/forsok-1.json"} <= set(manifest.filer)


def test_underkant_utkast_ger_felkod_2(byra_med_profil, tmp_path, giltigt_utkast, capsys):
    felaktigt = giltigt_utkast.model_copy(update={"avsnitt": "D-ARB.6.2"}).model_dump_json()
    fil = tmp_path / "fel.json"
    fil.write_text("[" + ",".join([felaktigt] * 3) + "]", encoding="utf-8")
    main(["bedom", "testbyra"])
    assert _skriv(fil) == 2
    assert "underkänt efter 3 försök" in capsys.readouterr().out


def test_avbruten_skrivning_behaller_forsoken_men_raknas_inte(byra_med_profil, tmp_path, giltigt_utkast, capsys):
    felaktigt = giltigt_utkast.model_copy(update={"avsnitt": "D-ARB.6.2"}).model_dump_json()
    fil = tmp_path / "ett_svar.json"
    fil.write_text("[" + felaktigt + "]", encoding="utf-8")
    main(["bedom", "testbyra"])
    assert _skriv(fil) == 1
    assert "Försöken som hann göras är sparade" in capsys.readouterr().err
    assert avslutade_korningar(byra_med_profil, UTKAST) == []
    (sparat,) = (byra_med_profil / UTKAST).glob("*/D-ARB.6.1/forsok-1.json")
    forsok = Forsok.model_validate_json(sparat.read_text(encoding="utf-8"))
    assert (forsok.anrop.svar_id, forsok.anrop.svarsmodell) == ("test-1", "testleverantor")
    assert forsok.fel


def test_skriv_efter_andrad_profil_vagras(byra_med_profil, testsvarsfil, capsys):
    main(["bedom", "testbyra"])
    main(["bekrafta", "testbyra", "P-ORG.antal_anstallda", "9", "--kalla", "Lönelistan"])
    assert _skriv(testsvarsfil) == 1
    assert "Profilen har ändrats sedan bedömningen" in capsys.readouterr().err


def test_claude_utan_api_nyckel_ger_tydligt_fel(byra_med_profil, monkeypatch, capsys):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    main(["bedom", "testbyra"])
    assert main(["skriv", "testbyra"]) == 1
    assert "ANTHROPIC_API_KEY" in capsys.readouterr().err


def test_testleverantor_utan_fil_ger_tydligt_fel(byra_med_profil, capsys):
    main(["bedom", "testbyra"])
    assert main(["skriv", "testbyra", "--leverantor", "test"]) == 1
    assert "--testsvar" in capsys.readouterr().err
