from datetime import date

import pytest

from riskanalys.dokument.modeller import Avsnitt, Dokument, Textstycke
from riskanalys.faststallelse.sakgranskning import (
    SakgranskningsFel,
    galler_sakgranskning,
    granskad_summa,
    las_sakgranskningar,
    registrera_sakgranskning,
    sakgranskningsstatus,
    spara_sakgranskningar,
)
from riskanalys.lagring.datamapp import skapa_byramapp

DAG = date(2026, 11, 3)


@pytest.fixture
def profil(regelbas, profil_fabrik, real_varden):
    return profil_fabrik(regelbas, real_varden)


def _dokument(text="Byrån erbjuder löpande bokföring."):
    stycke = Textstycke(typ="beskrivning", text=text, referenser=["T-RED-01"])
    avsnitt = Avsnitt(id="D-ARB.3", rubrik="Byråns tjänster", kalla="regelbas", stycken=(stycke,))
    return Dokument(id="D-ARB", titel="Allmän riskbedömning", avsnitt=(avsnitt,))


def test_godkannande_registreras_med_den_granskade_textens_kontrollsumma(profil):
    dokument = _dokument()
    (post,) = registrera_sakgranskning((), dokument, profil, "D-ARB.3", True, "FfR", "Testa Testsson", DAG)
    assert post.kontrollsumma == granskad_summa(dokument.avsnitt[0], profil)
    assert galler_sakgranskning((post,), dokument.avsnitt[0], profil) == post
    assert sakgranskningsstatus((post,), dokument.avsnitt[0], profil) == "godkänt 2026-11-03 av Testa Testsson, roll FfR"


def test_godkannandet_galler_texten_med_insatt_namn(regelbas, profil_fabrik, real_varden, profil):
    dokument = _dokument("Funktionen för regelefterlevnad utövas av {roll:FfR}.")
    (post,) = registrera_sakgranskning((), dokument, profil, "D-ARB.3", True, "FfR", "Testa Testsson", DAG)
    assert post.kontrollsumma != dokument.avsnitt[0].kontrollsumma()
    ny_ansvarig = profil_fabrik(regelbas, {**real_varden, "P-ROLL.ffr_namn": "Ny Person"})
    assert galler_sakgranskning((post,), dokument.avsnitt[0], ny_ansvarig) is None
    assert sakgranskningsstatus((post,), dokument.avsnitt[0], ny_ansvarig) == "ändrat efter sakgranskningen, granska igen"


def test_sakgranskningen_galler_inte_andrad_text(profil):
    poster = registrera_sakgranskning((), _dokument(), profil, "D-ARB.3", True, "FfR", "Testa Testsson", DAG)
    andrat = _dokument("Byrån erbjuder löpande bokföring och lönehantering.").avsnitt[0]
    assert galler_sakgranskning(poster, andrat, profil) is None
    assert sakgranskningsstatus(poster, andrat, profil) == "ändrat efter sakgranskningen, granska igen"


def test_senaste_sakgranskningen_av_samma_lydelse_galler(profil):
    dokument = _dokument()
    poster = registrera_sakgranskning((), dokument, profil, "D-ARB.3", False, "FfR", "Testa Testsson", DAG, "Fel tjänst.")
    poster = registrera_sakgranskning(poster, dokument, profil, "D-ARB.3", True, "FfR", "Testa Testsson", DAG)
    assert galler_sakgranskning(poster, dokument.avsnitt[0], profil).godkand is True


def test_underkannande_kraver_kommentar(profil):
    with pytest.raises(SakgranskningsFel, match="--kommentar"):
        registrera_sakgranskning((), _dokument(), profil, "D-ARB.3", False, "FfR", "Testa Testsson", DAG)


def test_sakgranskning_kraver_namn(profil):
    with pytest.raises(SakgranskningsFel, match="--namn"):
        registrera_sakgranskning((), _dokument(), profil, "D-ARB.3", True, "FfR", None, DAG)


def test_okant_avsnitt_vagras(profil):
    with pytest.raises(SakgranskningsFel, match="D-ARB.9 finns inte"):
        registrera_sakgranskning((), _dokument(), profil, "D-ARB.9", True, "FfR", "Testa Testsson", DAG)


def test_ej_sakgranskat_avsnitt(profil):
    assert sakgranskningsstatus((), _dokument().avsnitt[0], profil) == "ej sakgranskat"


def test_sakgranskningar_sparas_och_lases(datamapp, profil):
    mapp = skapa_byramapp("testbyra")
    assert las_sakgranskningar(mapp) == ()
    poster = registrera_sakgranskning((), _dokument(), profil, "D-ARB.3", True, "FfR", "Testa Testsson", DAG)
    spara_sakgranskningar(mapp, poster)
    assert las_sakgranskningar(mapp) == poster


def test_v2_godkannande_galler_inte_ny_formatversion(profil):
    from riskanalys.dokument.modeller import Underrubrik
    a=_dokument().avsnitt[0].model_copy(update={"underrubriker":(Underrubrik(fore_stycke=0,rubrik="Analys"),)})
    doc=_dokument().model_copy(update={"avsnitt":(a,)})
    poster=registrera_sakgranskning((),doc,profil,a.id,True,"FfR","Testa Testsson",DAG)
    nytt=a.model_copy(update={"formatversion":"D-ARB-tjanst-v3"})
    assert galler_sakgranskning(poster,nytt,profil) is None
