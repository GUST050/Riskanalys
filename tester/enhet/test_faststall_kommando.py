import json

import pytest

from riskanalys.cli import main
from riskanalys.faststallelse.faststall import FASTSTALLDA
from riskanalys.lagring.korningar import avslutade_korningar
from riskanalys.lagring.manifest import MANIFESTNAMN

BESLUT = ["--organ", "styrelsen", "--datum", "2026-11-15", "--namn", "Testa Testsson"]


def test_faststall_och_verifiera(kedja, signerad_regelbas_rot, capsys):
    assert main(["faststall", "testbyra", *BESLUT, "--regelbas", str(signerad_regelbas_rot)]) == 0
    utskrift = capsys.readouterr().out
    assert "v1 är fastställd av styrelsen 2026-11-15" in utskrift
    assert "riskanalys verifiera testbyra 1" in utskrift
    assert "Nästa genomgång senast 2027-11-01." in utskrift
    assert main(["verifiera", "testbyra", "1"]) == 0
    assert "Version 1 stämmer med manifestet." in capsys.readouterr().out


def test_verifiera_rapporterar_andrad_fil_med_felkod_2(kedja, signerad_regelbas_rot, capsys):
    main(["faststall", "testbyra", *BESLUT, "--regelbas", str(signerad_regelbas_rot)])
    (kedja / FASTSTALLDA / "v1" / "beslut.yaml").write_text("organ: någon annan\n", encoding="utf-8")
    capsys.readouterr()
    assert main(["verifiera", "testbyra", "1"]) == 2
    utskrift = capsys.readouterr().out
    assert "- Fil ändrad: beslut.yaml" in utskrift
    assert "Återställ versionen från säkerhetskopian" in utskrift


def test_hinder_visas_som_lista_utan_stackspar(osignerad_kedja, capsys):
    assert main(["faststall", "testbyra", *BESLUT]) == 1
    fel = capsys.readouterr().err
    assert fel.startswith("Fel: Kan inte fastställa:")
    assert (
        "- Kravet KRV-LSF-001 (2 kap. 1 §) är inte verifierat av sakkunnig i sin nuvarande lydelse (status ej_granskad)."
        in fel
    )
    assert "Traceback" not in fel


def test_faststall_kraver_beslutsuppgifter(kedja, capsys):
    with pytest.raises(SystemExit):
        main(["faststall", "testbyra", "--organ", "styrelsen"])
    assert "--datum" in capsys.readouterr().err


@pytest.mark.parametrize(
    "korning, nyckel",
    [("granskning", "bedomning"), ("granskning", "utkast"), ("granskning", "historik"), ("granskning", "datum"),
     ("bedomningar", "regelbas_kontrollsumma")],
)
def test_manifest_som_saknar_en_uppgift_ger_fel_med_aterstallning(kedja, signerad_regelbas_rot, capsys, korning, nyckel):
    """Slutgranskningen 2026-10-10, Important #4 (Review Focus 13): aldrig en krasch på en saknad uppgift."""
    fil = avslutade_korningar(kedja, korning)[-1] / MANIFESTNAMN
    data = json.loads(fil.read_text(encoding="utf-8"))
    del data["metadata"][nyckel]
    fil.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    capsys.readouterr()
    assert main(["faststall", "testbyra", *BESLUT, "--regelbas", str(signerad_regelbas_rot)]) == 1
    fel = capsys.readouterr().err
    assert f"Uppgifter saknas: {nyckel}." in fel
    assert "Återställ mappen från säkerhetskopian" in fel
    assert not (kedja / FASTSTALLDA).exists()
