from riskanalys.cli import main


def test_regelbas_validera_godkanner_repots_regelbas(capsys):
    assert main(["regelbas", "validera"]) == 0
    utskrift = capsys.readouterr().out
    assert "Regelbasen är giltig." in utskrift
    assert "Version: 0.1.0" in utskrift
    assert "Krav: 6" in utskrift
    assert "Paragrafkarta RP-RED-VG: 3 av 12 paragrafer hanterade, sakkunnigstatus ej_granskad." in utskrift


def test_regelbas_summor_visar_det_som_ska_signeras(capsys):
    assert main(["regelbas", "summor"]) == 0
    rader = capsys.readouterr().out.splitlines()
    assert len(rader) == 7
    assert rader[0].startswith("KRV-LSF-001 sha256:")
    assert rader[-1].startswith("RP-RED-VG paragrafkarta sha256:")


def test_regelbas_validera_visar_fel_utan_stackspar(tmp_path, skriv_minimal_regelbas, minimal_filer, capsys):
    hot = minimal_filer["kataloger/hot.yaml"]
    hot[0]["kallor"] = ["SRC-SAKNAS"]
    rot = skriv_minimal_regelbas(tmp_path / "rb", {"kataloger/hot.yaml": hot})
    assert main(["regelbas", "validera", "--regelbas", str(rot)]) == 1
    fel = capsys.readouterr().err
    assert fel.startswith("Fel: Regelbasen har fel:")
    assert "H-1: hänvisar till källan SRC-SAKNAS som inte finns." in fel
    assert "Traceback" not in fel


def test_saknad_regelbasmapp_ger_felkod(tmp_path, capsys):
    assert main(["regelbas", "validera", "--regelbas", str(tmp_path / "saknas")]) == 1
    assert "finns inte" in capsys.readouterr().err
