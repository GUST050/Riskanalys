from types import SimpleNamespace

import anthropic
import httpx2
import pytest

from riskanalys.dokument.claude import (
    FALLBACK_BETA,
    MAX_TOKENS,
    PROMPT_KONTROLLSUMMA,
    SCHEMA,
    STANDARDEFFORT,
    STANDARDMODELL,
    ClaudeLeverantor,
)
from riskanalys.dokument.leverantor import LeverantorFel
from riskanalys.dokument.modeller import AvsnittsUtkast

API_URL = "https://api.anthropic.com/v1/messages"


class FalskKlient:
    """Ersätter anthropic.Anthropic i tester. Sparar anropen och returnerar ett förberett svar."""

    def __init__(self, svar=None, undantag=None):
        self.anrop = []
        self._svar = svar
        self._undantag = undantag
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._skapa))

    def _skapa(self, **kwargs):
        self.anrop.append(kwargs)
        if self._undantag is not None:
            raise self._undantag
        return self._svar


def _svar(text, stop_reason="end_turn", modell=STANDARDMODELL, iterationer=None):
    return SimpleNamespace(
        id="msg_test_1",
        model=modell,
        stop_reason=stop_reason,
        content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=text)],
        usage=SimpleNamespace(input_tokens=1200, output_tokens=800, iterations=iterationer),
    )


def test_anropet_foljer_installningarna(giltigt_utkast, real_underlag):
    klient = FalskKlient(_svar(giltigt_utkast.model_dump_json()))
    svar = ClaudeLeverantor(klient=klient).skriv(real_underlag, [])
    assert AvsnittsUtkast.model_validate_json(svar.text) == giltigt_utkast
    (anrop,) = klient.anrop
    assert anrop["model"] == STANDARDMODELL == "claude-opus-5-5"
    assert anrop["max_tokens"] == MAX_TOKENS
    assert anrop["output_config"] == {
        "effort": STANDARDEFFORT,
        "format": {"type": "json_schema", "schema": AvsnittsUtkast.model_json_schema()},
    }
    assert anrop["betas"] == [FALLBACK_BETA]
    assert anrop["fallbacks"] == "default"
    meddelande = anrop["messages"][0]["content"]
    assert real_underlag.model_dump_json(indent=2) in meddelande
    assert "Testa Testsson" not in meddelande


def test_anropsdata_sparas(giltigt_utkast, real_underlag):
    anrop = ClaudeLeverantor(klient=FalskKlient(_svar(giltigt_utkast.model_dump_json()))).skriv(real_underlag, []).anrop
    assert (anrop.leverantor, anrop.begard_modell, anrop.svarsmodell, anrop.effort) == (
        "claude",
        "claude-opus-5-5",
        "claude-opus-5-5",
        "high",
    )
    assert (anrop.svar_id, anrop.stop_reason, anrop.reservmodell_svarade) == ("msg_test_1", "end_turn", False)
    assert anrop.prompt_kontrollsumma == PROMPT_KONTROLLSUMMA
    assert [(post.typ, post.indata_token, post.utdata_token) for post in anrop.anvandning] == [("message", 1200, 800)]


def test_faktisk_svarsmodell_sparas_vid_fallback(giltigt_utkast, real_underlag):
    iterationer = [
        SimpleNamespace(type="message", input_tokens=1200, output_tokens=0),
        SimpleNamespace(type="fallback_message", model="claude-opus-4-8", input_tokens=1200, output_tokens=900),
    ]
    svar = _svar(giltigt_utkast.model_dump_json(), modell="claude-opus-4-8", iterationer=iterationer)
    anrop = ClaudeLeverantor(klient=FalskKlient(svar)).skriv(real_underlag, []).anrop
    assert (anrop.begard_modell, anrop.svarsmodell, anrop.reservmodell_svarade) == (
        "claude-opus-5-5",
        "claude-opus-4-8",
        True,
    )
    assert [(post.typ, post.modell, post.utdata_token) for post in anrop.anvandning] == [
        ("message", None, 0),
        ("fallback_message", "claude-opus-4-8", 900),
    ]


def test_promptens_kontrollsumma_bygger_pa_systemprompt_och_schema():
    assert PROMPT_KONTROLLSUMMA.startswith("sha256:")
    assert SCHEMA == AvsnittsUtkast.model_json_schema()


def test_aterkopplingen_skickas_med(giltigt_utkast, real_underlag):
    klient = FalskKlient(_svar(giltigt_utkast.model_dump_json()))
    ClaudeLeverantor(klient=klient).skriv(real_underlag, ["Stycke 2 innehåller talet 45."])
    assert "- Stycke 2 innehåller talet 45." in klient.anrop[0]["messages"][0]["content"]


@pytest.mark.parametrize(("stop_reason", "meddelande"), [("refusal", "avböjde"), ("max_tokens", "för långt")])
def test_avbrutna_svar_returneras_med_avbrott_och_anropsdata(real_underlag, stop_reason, meddelande):
    svar = ClaudeLeverantor(klient=FalskKlient(_svar("", stop_reason))).skriv(real_underlag, [])
    assert meddelande in svar.avbrott
    assert (svar.anrop.stop_reason, svar.anrop.svar_id) == (stop_reason, "msg_test_1")


def test_api_fel_blir_leverantorsfel(real_underlag):
    begaran = httpx2.Request("POST", API_URL)
    fel = anthropic.RateLimitError("För många anrop.", response=httpx2.Response(429, request=begaran), body=None)
    with pytest.raises(LeverantorFel, match="429"):
        ClaudeLeverantor(klient=FalskKlient(undantag=fel)).skriv(real_underlag, [])


def test_natverksfel_blir_leverantorsfel(real_underlag):
    fel = anthropic.APIConnectionError(request=httpx2.Request("POST", API_URL))
    with pytest.raises(LeverantorFel, match="nätverket"):
        ClaudeLeverantor(klient=FalskKlient(undantag=fel)).skriv(real_underlag, [])
