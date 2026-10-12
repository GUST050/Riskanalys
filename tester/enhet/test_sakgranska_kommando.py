from datetime import date

from riskanalys.cli import main
from riskanalys.faststallelse.sakgranskning import las_sakgranskningar
from riskanalys.granskning.korning import kor_granskning

GODKANN = ["--godkann", "--namn", "Testa Testsson", "--datum", "2026-11-03"]


def test_sakgranska_fore_granskning_sager_vilket_steg_som_saknas(skriven_byra, capsys):
    assert main(["sakgranska", "testbyra"]) == 1
    assert "Kör 'riskanalys granska testbyra' först" in capsys.readouterr().err


def test_listan_visar_status_per_avsnitt(skriven_byra, regelbas, capsys):
    kor_granskning(skriven_byra, regelbas, date(2026, 11, 2))
    assert main(["sakgranska", "testbyra"]) == 0
    rader = capsys.readouterr().out.splitlines()
    assert "D-ARB.6.1 Risk i löpande bokföring: ej sakgranskat" in rader
    assert sum(1 for rad in rader if rad.startswith("D-ARB.")) == 6


def test_visa_avsnitt_med_namn_insatt(skriven_byra, regelbas, capsys):
    kor_granskning(skriven_byra, regelbas, date(2026, 11, 2))
    assert main(["sakgranska", "testbyra", "--avsnitt", "D-ARB.1"]) == 0
    utskrift = capsys.readouterr().out
    assert "Funktionen för regelefterlevnad utövas av Testa Testsson." in utskrift
    assert "{roll:FfR}" not in utskrift


def test_godkann_avsnitt(skriven_byra, regelbas, capsys):
    kor_granskning(skriven_byra, regelbas, date(2026, 11, 2))
    assert main(["sakgranska", "testbyra", "--avsnitt", "D-ARB.6.1", *GODKANN]) == 0
    (post,) = las_sakgranskningar(skriven_byra)
    assert (post.avsnitt, post.godkand, post.roll) == ("D-ARB.6.1", True, "FfR")
    main(["sakgranska", "testbyra"])
    assert "D-ARB.6.1 Risk i löpande bokföring: godkänt 2026-11-03 av Testa Testsson, roll FfR" in capsys.readouterr().out


def test_underkann_utan_kommentar_vagras(skriven_byra, regelbas, capsys):
    kor_granskning(skriven_byra, regelbas, date(2026, 11, 2))
    assert main(["sakgranska", "testbyra", "--avsnitt", "D-ARB.6.1", "--underkann", "--namn", "Testa Testsson"]) == 1
    assert "--kommentar" in capsys.readouterr().err
    assert las_sakgranskningar(skriven_byra) == ()


def test_godkann_utan_avsnitt_vagras(skriven_byra, regelbas, capsys):
    kor_granskning(skriven_byra, regelbas, date(2026, 11, 2))
    assert main(["sakgranska", "testbyra", *GODKANN]) == 1
    assert "--avsnitt" in capsys.readouterr().err


def test_andrad_granskning_kan_inte_sakgranskas(skriven_byra, regelbas, capsys):
    mapp = kor_granskning(skriven_byra, regelbas, date(2026, 11, 2))
    fil = mapp / "dokument.json"
    fil.write_text(fil.read_text(encoding="utf-8").replace("Testbyrån AB", "Annan byrå AB"), encoding="utf-8")
    assert main(["sakgranska", "testbyra", "--avsnitt", "D-ARB.1", *GODKANN]) == 1
    assert "Granskningen är ändrad efter körningen. Fil ändrad: dokument.json" in capsys.readouterr().err
    assert las_sakgranskningar(skriven_byra) == ()


def test_riskavsnitt_visar_riskmotorns_nivaer_for_jamforelse(skriven_byra, regelbas, capsys):
    """Slutgranskningen 2026-10-10, Important #1: sakgranskaren ska kunna jämföra texten med motorns nivåer."""
    kor_granskning(skriven_byra, regelbas, date(2026, 11, 2))
    assert main(["sakgranska", "testbyra", "--avsnitt", "D-ARB.6.1"]) == 0
    utskrift = capsys.readouterr().out
    assert (
        "Riskmotorns nivåer: inneboende risk hög (sannolikhet hög, konsekvens betydande), "
        "risk för terrorfinansiering måttlig (sannolikhet låg, konsekvens allvarlig), kvarstående risk hög."
    ) in utskrift
    assert main(["sakgranska", "testbyra", "--avsnitt", "D-ARB.1"]) == 0
    assert "Riskmotorns nivåer" not in capsys.readouterr().out


def test_riskavsnitt_visar_ai_utkastets_oppna_fragor(skriven_byra_med_oppen_fraga, regelbas, capsys):
    """Codex 2026-10-10, P1: sakgranskaren ska se AI:ns öppna frågor."""
    kor_granskning(skriven_byra_med_oppen_fraga, regelbas, date(2026, 11, 2))
    assert main(["sakgranska", "testbyra", "--avsnitt", "D-ARB.6.1"]) == 0
    assert (
        "Öppen fråga från AI-utkastet: Har byrån bankkoppling för alla kunder? Uppgift som saknas: P-KANAL.bankdata_andel."
    ) in capsys.readouterr().out


def test_sakgranskaren_ser_underrubriken_som_godkannandet_binder(skriven_byra, regelbas, capsys, monkeypatch):
    from riskanalys.dokument.modeller import Underrubrik
    from riskanalys.granskning.korning import las_granskning
    from riskanalys.kommandon import sakgranska_kommando
    mapp=kor_granskning(skriven_byra,regelbas,date(2026,11,2))
    d,f=las_granskning(mapp)
    a=d.avsnitt_med_id()['D-ARB.6.1']
    a=a.model_copy(update={'underrubriker':(Underrubrik(fore_stycke=0,rubrik='Risknivåer och motivering'),)})
    d=d.model_copy(update={'avsnitt':tuple(a if s.id==a.id else s for s in d.avsnitt)})
    monkeypatch.setattr(sakgranska_kommando,'las_granskning',lambda _: (d,f))
    assert main(['sakgranska','testbyra','--avsnitt',a.id])==0
    assert 'Risknivåer och motivering' in capsys.readouterr().out
