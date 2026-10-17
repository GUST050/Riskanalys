import json

import pytest
from pydantic import ValidationError

from riskanalys.dokument.aischema import INGEN_UPPGIFT, ai_schema, tolka_ai_svar

TILLATNA = frozenset({"T-RED-01", "H-01", "S-KUND-01", "P-KUND.andel_riskbransch"})


def test_schemat_har_enum_och_alla_falt_obligatoriska():
    schema = ai_schema(TILLATNA, frozenset({"P-KUND.andel_riskbransch"}))
    stycke = schema["properties"]["stycken"]["items"]
    assert list(stycke["properties"]) == ["typ", "referenser", "text"]
    assert stycke["required"] == ["typ", "referenser", "text"]
    assert stycke["properties"]["referenser"]["items"]["enum"] == sorted(TILLATNA)
    assert "avsnitt" not in schema["properties"]
    assert schema["additionalProperties"] is False


def test_tom_uppgiftslista_ger_giltigt_enum():
    schema = ai_schema(TILLATNA, frozenset())
    enum = schema["properties"]["oklarheter"]["items"]["properties"]["uppgift_id"]["enum"]
    assert enum == [INGEN_UPPGIFT]


def test_svar_tolkas_med_avsnitt_fran_koden_och_skiftlage_normaliseras():
    text = json.dumps({"stycken": [{"typ": "analys", "referenser": ["h-01", "T-RED-01"], "text": "Text."}],
                       "oklarheter": [{"uppgift_id": "p-kund.andel_riskbransch", "fraga": "Vilken period?"}]})
    utkast = tolka_ai_svar(text, "D-ARB.6.1", TILLATNA)
    assert utkast.avsnitt == "D-ARB.6.1"
    assert utkast.stycken[0].referenser == ["H-01", "T-RED-01"]
    assert utkast.oklarheter[0].saknad_uppgift == "P-KUND.andel_riskbransch"


def test_aldre_svar_med_avsnittsfalt_godtas(giltigt_utkast):
    utkast = tolka_ai_svar(giltigt_utkast.model_dump_json(), "D-ARB.6.1", TILLATNA)
    assert utkast == giltigt_utkast


def test_ogiltigt_svar_kastar_valideringsfel():
    with pytest.raises(ValidationError):
        tolka_ai_svar('{"stycken": "fel"}', "D-ARB.6.1", TILLATNA)


@pytest.mark.parametrize('stycken', [None, 0, False, 'fel form', {'text': 'fel form'}])
@pytest.mark.parametrize('med_avsnitt', [False, True])
def test_felformat_styckesamling_ger_valideringsfel(stycken, med_avsnitt):
    data = {'stycken': stycken, 'oklarheter': []}
    if med_avsnitt:
        data['avsnitt'] = 'D-ARB.6.1'
    with pytest.raises(ValidationError):
        tolka_ai_svar(json.dumps(data), 'D-ARB.6.1', TILLATNA)
