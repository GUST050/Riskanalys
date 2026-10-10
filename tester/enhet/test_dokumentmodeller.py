import pytest
from pydantic import ValidationError

from riskanalys.dokument.modeller import (
    Avsnitt,
    Avsnittsunderlag,
    AvsnittsUtkast,
    Dokument,
    Textstycke,
    UnderlagHot,
    UnderlagKontroll,
    UnderlagSarbarhet,
    UnderlagUppgift,
)


def _objekt(schema):
    yield schema
    yield from schema.get("$defs", {}).values()


def test_ai_schemat_ar_last():
    for objekt in _objekt(AvsnittsUtkast.model_json_schema()):
        assert objekt["additionalProperties"] is False
        assert set(objekt["required"]) == set(objekt["properties"])


def test_ai_svar_med_okant_falt_vagras():
    with pytest.raises(ValidationError):
        AvsnittsUtkast.model_validate({"avsnitt": "D-ARB.6.1", "stycken": [], "oklarheter": [], "extra": 1})


def test_ai_svar_med_okand_stycketyp_vagras():
    with pytest.raises(ValidationError):
        Textstycke.model_validate({"typ": "slutsats", "text": "x", "referenser": []})


def test_tillatna_id_i_underlaget():
    underlag = Avsnittsunderlag(
        avsnitt="D-ARB.6.1",
        rubrik="Löpande bokföring",
        instruktion="Skriv.",
        tjanst_id="T-1",
        tjanst_namn="Tjänst",
        tjanst_beskrivning="Beskrivning.",
        nivaer={"inneboende_risk": "hög"},
        hot=(UnderlagHot(id="H-1", namn="Hot", beskrivning="B."),),
        sarbarheter=(UnderlagSarbarhet(id="S-1", namn="Sårbarhet", galler="ja"),),
        kontroller=(UnderlagKontroll(id="C-1", namn="Kontroll", status="finns, ej belagd"),),
        uppgifter=(UnderlagUppgift(id="P-A", fraga="Andel?", varde="30 %", bekraftad=True),),
        regelspar=("BT-MATRIS-08",),
        undvik=(),
    )
    assert underlag.tillatna_id() == {"T-1", "H-1", "S-1", "C-1", "P-A", "BT-MATRIS-08"}


def test_avsnittets_kontrollsumma_andras_med_texten():
    avsnitt = Avsnitt(id="D-ARB.1", rubrik="Syfte", kalla="regelbas", stycken=())
    andrat = avsnitt.model_copy(
        update={"stycken": (Textstycke(typ="beskrivning", text="Ny text.", referenser=[]),)}
    )
    assert avsnitt.kontrollsumma().startswith("sha256:")
    assert avsnitt.kontrollsumma() != andrat.kontrollsumma()


def test_dokument_sparas_och_lases_oforandrat():
    stycke = Textstycke(typ="analys", text="Text.", referenser=["H-1"])
    dokument = Dokument(
        id="D-ARB",
        titel="Allmän riskbedömning",
        avsnitt=(Avsnitt(id="D-ARB.1", rubrik="Syfte", kalla="regelbas", stycken=(stycke,)),),
    )
    assert Dokument.model_validate_json(dokument.model_dump_json()) == dokument
    assert set(dokument.avsnitt_med_id()) == {"D-ARB.1"}
