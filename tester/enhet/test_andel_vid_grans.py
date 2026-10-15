import pytest

from riskanalys.profil.hantering import visa_varde_klartext
from riskanalys.regelverk.laddning import ladda_regelbas


@pytest.fixture(scope="module")
def rb():
    return ladda_regelbas()


@pytest.fixture(scope="module")
def andel(rb):
    return rb.falt["P-KUND.andel_riskbransch"]


@pytest.mark.parametrize(("varde", "vantat"), [
    (0.195, "19,5 %"), (0.204, "20,4 %"), (0.2004, "20,04 %"), (0.0995, "9,95 %"),
    (0.19996, "strax under 20 %"), (0.200001, "strax över 20 %"), (0.2, "20 %"), (0.33, "33 %"),
])
def test_andel_nara_grans_visas_pa_ratt_sida(andel, varde, vantat):
    assert visa_varde_klartext(andel, varde, (0.1, 0.2)) == vantat


def test_utan_granser_ar_visningen_oforandrad(andel):
    assert visa_varde_klartext(andel, 0.195) == "20 %"


def test_intervall_vid_noll_och_hundra_gar_fore_gransen(andel):
    assert visa_varde_klartext(andel, 0.003, (0.2,)) == "mindre än 1 %"
    assert visa_varde_klartext(andel, 0.997, (0.2,)) == "mer än 99 %"


def test_metodgranser_ar_unika_sorterade_och_strikt_mellan_noll_och_ett(rb):
    from riskanalys.regelverk.granser import metodgranser
    assert metodgranser(rb, "P-KUND.andel_riskbransch") == (0.2,)
    # Bara jämförelsen '> 0' finns för det här fältet; den hanteras av intervallregeln (8.4.9 punkt 7).
    assert metodgranser(rb, "P-GEO.andel_utland_transaktion") == ()


def test_metodgranser_hittar_nastlade_jamforelser_och_utesluter_andra_falt(rb):
    from riskanalys.regelverk.granser import metodgranser

    falt_id = "P-KUND.andel_riskbransch"
    villkor = {"alla": [
        {"falt": falt_id, "op": ">=", "varde": 0.2},
        {"nagon": [
            {"falt": falt_id, "op": "<", "varde": 0.1},
            {"inte": {"falt": falt_id, "op": "<=", "varde": 0.4}},
            {"falt": falt_id, "op": ">", "varde": 0.2},
        ]},
        {"falt": "P-GEO.andel_utland_transaktion", "op": ">", "varde": 0.3},
        *({"falt": falt_id, "op": ">", "varde": v} for v in (0, 1)),
        {"falt": falt_id, "op": "==", "varde": 0.5},
    ]}
    sarb = rb.sarbarheter["S-KUND-01"].model_copy(update={"villkor": villkor})
    kopia = rb.model_copy(update={"sarbarheter": {sarb.id: sarb}})
    assert metodgranser(kopia, falt_id) == (0.1, 0.2, 0.4)

@pytest.mark.parametrize('varde,granser,vantat', [
    (.205, (.205,), '20,5 %'),
    (.204999, (.205,), 'strax under 20,5 %'),
    (.205001, (.205,), 'strax över 20,5 %'),
    (.20496, (.2, .205), 'strax under 20,5 %'),
])
def test_brakgrans_och_flera_granser(andel, varde, granser, vantat):
    assert visa_varde_klartext(andel, varde, granser) == vantat


def test_brakgrans_i_villkorstext(rb):
    from riskanalys.dokument.klartext import villkorstext
    assert villkorstext({'falt': 'P-KUND.andel_riskbransch', 'op': '>=', 'varde': .205}, rb).endswith('20,5 %')


@pytest.mark.parametrize('varde,vantat', [(.195,'strax under 20 %'),(.1999,'strax under 20 %'),(.2,'minst 20 %'),(.204,'minst 20 %'),(.205,'minst 20 %'),(.2051,'21 %'),(.1949,'19 %'),(.33,'33 %'),(.003,'mindre än 1 %'),(.997,'mer än 99 %')])
def test_begransad_precision_for_ai(andel,varde,vantat):
    from riskanalys.profil.hantering import visa_andel_begransad
    assert visa_andel_begransad(andel,varde,(.2,)) == vantat
