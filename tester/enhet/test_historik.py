from datetime import date

import pytest

from riskanalys.cli import main
from riskanalys.drift.historik import (
    Handelse,
    Historik,
    historikens_kontrollsumma,
    lagg_till_manader,
    las_historik,
    spara_historik,
)
from riskanalys.lagring.datamapp import skapa_byramapp


@pytest.mark.parametrize(
    ("datum", "manader", "vantat"),
    [
        (date(2026, 11, 1), 12, date(2027, 11, 1)),
        (date(2024, 2, 29), 12, date(2025, 2, 28)),
        (date(2026, 1, 31), 1, date(2026, 2, 28)),
        (date(2026, 12, 15), 1, date(2027, 1, 15)),
    ],
)
def test_lagg_till_manader(datum, manader, vantat):
    assert lagg_till_manader(datum, manader) == vantat


def test_tom_historik_har_ingen_nasta_genomgang():
    assert Historik().nasta_genomgang() is None


def test_nasta_genomgang_ar_tolv_manader_efter_den_senaste_utvarderingen():
    historik = Historik().med(Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Första."))
    historik = historik.med(Handelse(datum=date(2027, 3, 1), typ="utvärdering", beskrivning="Andra."))
    assert historik.senaste_utvardering() == date(2027, 3, 1)
    assert historik.nasta_genomgang() == date(2028, 3, 1)


def test_senare_faststallelse_eller_uppdatering_flyttar_inte_fristen():
    historik = Historik().med(Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Första."))
    historik = historik.med(Handelse(datum=date(2026, 11, 20), typ="fastställelse", beskrivning="v1", version=1))
    historik = historik.med(Handelse(datum=date(2027, 2, 1), typ="uppdatering", beskrivning="Ny rutin."))
    assert historik.senaste_utvardering() == date(2026, 11, 1)
    assert historik.nasta_genomgang() == date(2027, 11, 1)


def test_historik_utan_utvardering_har_ingen_nasta_genomgang():
    historik = Historik().med(Handelse(datum=date(2026, 11, 20), typ="fastställelse", beskrivning="v1", version=1))
    assert historik.senaste_utvardering() is None
    assert historik.nasta_genomgang() is None


def test_senaste_utvardering_raknas_efter_datum_inte_ordning():
    historik = Historik().med(Handelse(datum=date(2027, 3, 1), typ="utvärdering", beskrivning="Andra."))
    historik = historik.med(Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Inlagd i efterhand."))
    assert historik.senaste_utvardering() == date(2027, 3, 1)


def test_med_lamnar_den_gamla_historiken_orord():
    historik = Historik()
    historik.med(Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Första."))
    assert historik.handelser == ()


def test_historiken_sparas_och_lases(datamapp):
    mapp = skapa_byramapp("testbyra")
    assert las_historik(mapp) == Historik()
    historik = Historik().med(Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Första."))
    spara_historik(mapp, historik)
    assert las_historik(mapp) == historik


def test_historikens_kontrollsumma_andras_med_historiken(datamapp):
    mapp = skapa_byramapp("testbyra")
    assert historikens_kontrollsumma(mapp) == ""
    spara_historik(mapp, Historik().med(Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Första.")))
    forsta = historikens_kontrollsumma(mapp)
    spara_historik(mapp, las_historik(mapp).med(Handelse(datum=date(2027, 11, 1), typ="utvärdering", beskrivning="Andra.")))
    assert forsta.startswith("sha256:")
    assert historikens_kontrollsumma(mapp) != forsta


def test_utvardera_kommandot(datamapp, capsys):
    skapa_byramapp("testbyra")
    argv = ["utvardera", "testbyra", "--beskrivning", "Första riskbedömningen.", "--datum", "2026-11-01"]
    assert main(argv) == 0
    assert "Nästa genomgång senast 2027-11-01." in capsys.readouterr().out
