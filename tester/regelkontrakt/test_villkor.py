from datetime import date

import pytest

from riskanalys.regelverk.villkor import (
    Alla,
    Faltdef,
    Faltvarde,
    Inte,
    Jamforelse,
    Kunskap,
    Nagon,
    Sanning,
    VillkorsFel,
    falt_i,
    kontrollera_varde,
    tolka_villkor,
    utvardera,
)

FALT = {
    "P-B": Faltdef("P-B", "bool"),
    "P-H": Faltdef("P-H", "heltal"),
    "P-T": Faltdef("P-T", "tal"),
    "P-A": Faltdef("P-A", "andel"),
    "P-X": Faltdef("P-X", "text"),
    "P-V": Faltdef("P-V", "val", ("finns", "saknas")),
    "P-D": Faltdef("P-D", "datum"),
}
S, F, O = Sanning.SANT, Sanning.FALSKT, Sanning.OKANT


def kand(varde):
    return Faltvarde(Kunskap.KAND, varde)


def test_tolkar_jamforelse():
    assert tolka_villkor({"falt": "P-A", "op": ">=", "varde": 0.2}, FALT) == Jamforelse("P-A", ">=", 0.2)


def test_tolkar_kombinatorer():
    data = {
        "alla": [
            {"falt": "P-B", "op": "==", "varde": True},
            {"nagon": [{"inte": {"falt": "P-X", "op": "finns"}}]},
        ]
    }
    vantat = Alla((Jamforelse("P-B", "==", True), Nagon((Inte(Jamforelse("P-X", "finns")),))))
    assert tolka_villkor(data, FALT) == vantat


@pytest.mark.parametrize(
    ("data", "meddelande"),
    [
        ({"falt": "P-OKANT", "op": "==", "varde": 1}, "Okänt fält"),
        ({"falt": "P-H", "op": "~=", "varde": 1}, "Okänd operator"),
        ({"falt": "P-H", "op": "finns", "varde": 1}, "tar inget värde"),
        ({"falt": "P-H", "op": "=="}, "kräver ett värde"),
        ({"falt": "P-B", "op": "<", "varde": True}, "kan inte användas"),
        ({"falt": "P-X", "op": ">", "varde": "a"}, "kan inte användas"),
        ({"falt": "P-H", "op": "i", "varde": []}, "kräver en lista"),
        ({"falt": "P-H", "op": "i", "varde": 3}, "kräver en lista"),
        ({"falt": "P-A", "op": "==", "varde": 1.5}, "passar inte typen andel"),
        ({"falt": "P-H", "op": "==", "varde": True}, "passar inte typen heltal"),
        ({"falt": "P-V", "op": "==", "varde": "kanske"}, "passar inte typen val"),
        ({"falt": "P-D", "op": "<", "varde": "2026-01-01"}, "passar inte typen datum"),
        ({"alla": {"falt": "P-B", "op": "finns"}}, "måste innehålla en lista"),
        ({"falt": "P-B", "op": "finns", "extra": 1}, "Okänd villkorsform"),
        ({}, "måste vara en mappning"),
        ("P-B == true", "måste vara en mappning"),
    ],
)
def test_felaktiga_villkor_vagras(data, meddelande):
    with pytest.raises(VillkorsFel, match=meddelande):
        tolka_villkor(data, FALT)


@pytest.mark.parametrize(
    ("op", "varde", "falt_varde", "vantat"),
    [
        ("==", 3, 3, S), ("==", 3, 4, F),
        ("!=", 3, 4, S), ("!=", 3, 3, F),
        ("<", 3, 2, S), ("<", 3, 3, F),
        ("<=", 3, 3, S), ("<=", 3, 4, F),
        (">", 3, 4, S), (">", 3, 3, F),
        (">=", 3, 3, S), (">=", 3, 2, F),
    ],
)
def test_jamforande_operatorer_pa_heltal(op, varde, falt_varde, vantat):
    villkor = tolka_villkor({"falt": "P-H", "op": op, "varde": varde}, FALT)
    assert utvardera(villkor, {"P-H": kand(falt_varde)}).sanning is vantat


def test_andel_gransfall():
    villkor = tolka_villkor({"falt": "P-A", "op": ">=", "varde": 0.2}, FALT)
    assert utvardera(villkor, {"P-A": kand(0.2)}).sanning is S
    assert utvardera(villkor, {"P-A": kand(0.19)}).sanning is F


def test_datum_jamfors_pa_bada_sidor_om_gransen():
    villkor = tolka_villkor({"falt": "P-D", "op": "<", "varde": date(2026, 11, 20)}, FALT)
    assert utvardera(villkor, {"P-D": kand(date(2026, 11, 19))}).sanning is S
    assert utvardera(villkor, {"P-D": kand(date(2026, 11, 20))}).sanning is F


def test_operatorn_i():
    villkor = tolka_villkor({"falt": "P-V", "op": "i", "varde": ["finns"]}, FALT)
    assert utvardera(villkor, {"P-V": kand("finns")}).sanning is S
    assert utvardera(villkor, {"P-V": kand("saknas")}).sanning is F


def test_finns_och_saknas():
    finns = tolka_villkor({"falt": "P-X", "op": "finns"}, FALT)
    saknas = tolka_villkor({"falt": "P-X", "op": "saknas"}, FALT)
    assert utvardera(finns, {"P-X": kand("text")}).sanning is S
    assert utvardera(saknas, {"P-X": kand(None)}).sanning is S
    assert utvardera(finns, {"P-X": kand(None)}).sanning is F


def test_okant_falt_ger_okant_och_listas():
    villkor = tolka_villkor({"falt": "P-A", "op": ">=", "varde": 0.2}, FALT)
    utfall = utvardera(villkor, {})
    assert utfall.sanning is O
    assert utfall.okanda == frozenset({"P-A"})


def test_ej_tillampligt_falt():
    jamforelse = tolka_villkor({"falt": "P-A", "op": ">=", "varde": 0.2}, FALT)
    saknas = tolka_villkor({"falt": "P-A", "op": "saknas"}, FALT)
    varden = {"P-A": Faltvarde(Kunskap.EJ_TILLAMPLIG)}
    assert utvardera(jamforelse, varden).sanning is F
    assert utvardera(saknas, varden).sanning is S


def test_kant_tomt_varde_ger_falskt_vid_jamforelse():
    villkor = tolka_villkor({"falt": "P-H", "op": ">", "varde": 1}, FALT)
    assert utvardera(villkor, {"P-H": kand(None)}).sanning is F


def _konstant(sanning):
    """Ett villkor som ger angivet sanningsvärde med VARDEN nedan."""
    return {
        S: Jamforelse("P-B", "==", True),
        F: Jamforelse("P-B", "==", False),
        O: Jamforelse("P-OKAND", "==", True),
    }[sanning]


VARDEN = {"P-B": kand(True)}


@pytest.mark.parametrize(
    ("a", "b", "vantat"),
    [(S, S, S), (S, F, F), (S, O, O), (F, S, F), (F, F, F), (F, O, F), (O, S, O), (O, F, F), (O, O, O)],
)
def test_alla_sanningstabell(a, b, vantat):
    assert utvardera(Alla((_konstant(a), _konstant(b))), VARDEN).sanning is vantat


@pytest.mark.parametrize(
    ("a", "b", "vantat"),
    [(S, S, S), (S, F, S), (S, O, S), (F, S, S), (F, F, F), (F, O, O), (O, S, S), (O, F, O), (O, O, O)],
)
def test_nagon_sanningstabell(a, b, vantat):
    assert utvardera(Nagon((_konstant(a), _konstant(b))), VARDEN).sanning is vantat


@pytest.mark.parametrize(("inre", "vantat"), [(S, F), (F, S), (O, O)])
def test_inte_sanningstabell(inre, vantat):
    assert utvardera(Inte(_konstant(inre)), VARDEN).sanning is vantat


def test_tomma_kombinatorer():
    assert utvardera(Alla(()), {}).sanning is S
    assert utvardera(Nagon(()), {}).sanning is F


def test_okanda_samlas_fran_alla_delar():
    villkor = Nagon((_konstant(O), Jamforelse("P-ANNAN", "finns")))
    assert utvardera(villkor, VARDEN).okanda == frozenset({"P-OKAND", "P-ANNAN"})


def test_falt_i_listar_alla_falt_i_tradet():
    villkor = Alla((Jamforelse("P-A", ">=", 0.2), Nagon((Inte(Jamforelse("P-B", "finns")),))))
    assert falt_i(villkor) == frozenset({"P-A", "P-B"})


@pytest.mark.parametrize(
    ("definition", "varde"),
    [
        (Faltdef("x", "bool"), True),
        (Faltdef("x", "heltal"), 3),
        (Faltdef("x", "tal"), 2.5),
        (Faltdef("x", "andel"), 0),
        (Faltdef("x", "andel"), 1),
        (Faltdef("x", "text"), "a"),
        (Faltdef("x", "val", ("a",)), "a"),
        (Faltdef("x", "datum"), date(2026, 1, 1)),
    ],
)
def test_giltiga_varden_godtas(definition, varde):
    kontrollera_varde(definition, varde)


def test_okand_typ_vagras():
    with pytest.raises(VillkorsFel, match="Okänd typ"):
        kontrollera_varde(Faltdef("x", "lista"), [])
