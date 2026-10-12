"""Claude som textleverantör via den officiella SDK:n (spec 8.3)."""

import json
from datetime import datetime, timezone
from typing import Any

import anthropic

from riskanalys.dokument.leverantor import Anropsdata, Delanrop, Leveranssvar, LeverantorFel, Tokenanvandning
from riskanalys.dokument.modeller import Avsnittsunderlag
from riskanalys.dokument.aischema import SCHEMAVERSION, ai_schema
from riskanalys.lagring.kontrollsumma import for_text

STANDARDMODELL = "claude-opus-5-5"
STANDARDEFFORT = "high"
MAX_TOKENS = 16000
STROMNINGSGRANS = 16000
FALLBACK_BETA = "server-side-fallback-2026-07-01"
RESERVMODELLENS_POST = "fallback_message"
SYSTEMPROMPT = """Du skriver analys och motivering i en redovisningsbyrås allmänna riskbedömning.
Använd bara underlaget. Programmet äger tal, risknivåer och låsta meningar. Ange aldrig någon nivå
för risk, sannolikhet eller konsekvens, inte heller för delfaktorer; beskriv dem med fakta.
Varje stycke bär referenser till underlaget. En motivering knyter hot till sårbarhet eller uppgift.
Okända uppgifter markeras [VERIFIERA] och får en oklarhet. Personer skrivs som {roll:FfR}.
Skriv konkret och sakligt på svenska utan nya fakta, kontroller eller källor."""
PROMPT_KONTROLLSUMMA = for_text(SYSTEMPROMPT + "\n" + SCHEMAVERSION)
_AVBROTT = {
    "refusal": "Claude avböjde att skriva avsnittet.",
    "max_tokens": f"Svaret blev för långt och avbröts vid {MAX_TOKENS} token.",
}


class ClaudeLeverantor:
    namn = "claude"

    def __init__(self, modell: str = STANDARDMODELL, effort: str = STANDARDEFFORT, klient: Any = None) -> None:
        self.modell = modell
        self.effort = effort
        self._klient = klient if klient is not None else anthropic.Anthropic()

    def skriv(self, underlag: Avsnittsunderlag, aterkoppling: list[str]) -> Leveranssvar:
        schema = ai_schema(underlag.tillatna_id(), frozenset(u.id for u in underlag.uppgifter))
        try:
            svar = self._klient.beta.messages.create(
                model=self.modell,
                max_tokens=MAX_TOKENS,
                system=SYSTEMPROMPT,
                messages=[{"role": "user", "content": bygg_meddelande(underlag, aterkoppling)}],
                output_config={"effort": self.effort, "format": {"type": "json_schema", "schema": schema}},
                betas=[FALLBACK_BETA],
                fallbacks="default",
            )
        except anthropic.APIStatusError as fel:
            raise _statusfel(fel.status_code) from fel
        except anthropic.APIConnectionError as fel:
            raise LeverantorFel("Kunde inte nå Claude-API:t. Kontrollera nätverket och försök igen.", tillfalligt=True) from fel
        return self._leveranssvar(svar)

    def skriv_del(self, anrop: Delanrop) -> Leveranssvar:
        parametrar = dict(
            model=self.modell, max_tokens=anrop.max_tokens, system=anrop.system,
            messages=[{"role": "user", "content": anrop.innehall}],
            output_config={"effort": anrop.effort, "format": {"type": "json_schema", "schema": anrop.schema}},
            betas=[FALLBACK_BETA], fallbacks="default",
        )
        try:
            if anrop.max_tokens > STROMNINGSGRANS:
                with self._klient.beta.messages.stream(**parametrar) as strom:
                    svar = strom.get_final_message()
            else:
                svar = self._klient.beta.messages.create(**parametrar)
        except anthropic.APIStatusError as fel:
            raise _statusfel(fel.status_code) from fel
        except anthropic.APIConnectionError as fel:
            raise LeverantorFel("Kunde inte nå Claude-API:t. Kontrollera nätverket och försök igen.", tillfalligt=True) from fel
        leverans = self._leveranssvar(svar)
        anropsdata = leverans.anrop.model_copy(update={"del_id": anrop.del_id, "prompt_kontrollsumma": anrop.promptsumma,
                                                       "effort": anrop.effort})
        avbrott = (f"Svaret blev för långt och avbröts vid {anrop.max_tokens} token."
                   if svar.stop_reason == "max_tokens" else leverans.avbrott)
        return leverans.model_copy(update={"anrop": anropsdata, "avbrott": avbrott})

    def _leveranssvar(self, svar: Any) -> Leveranssvar:
        anvandning = _anvandning(svar.usage)
        text = next((block.text for block in svar.content if block.type == "text"), "")
        avbrott = _AVBROTT.get(svar.stop_reason) or (None if text else "Claude-svaret saknade text.")
        reservmodell = svar.stop_reason != "refusal" and any(post.typ == RESERVMODELLENS_POST for post in anvandning)
        anrop = Anropsdata(
            leverantor=self.namn,
            begard_modell=self.modell,
            svarsmodell=svar.model,
            effort=self.effort,
            prompt_kontrollsumma=PROMPT_KONTROLLSUMMA,
            svar_id=svar.id,
            stop_reason=svar.stop_reason,
            reservmodell_svarade=reservmodell,
            anvandning=anvandning,
            tidpunkt=datetime.now(timezone.utc),
        )
        return Leveranssvar(anrop=anrop, text=text, avbrott=avbrott)


def _statusfel(status: int) -> LeverantorFel:
    instruktion = {
        400: "Ogiltig begäran. Kontrollera modell och anropsinställningar innan du kör igen.",
        401: "API-nyckeln nekades. Kontrollera nyckeln innan du kör igen.",
        403: "Behörighet saknas. Kontrollera kontots åtkomst till modellen innan du kör igen.",
    }.get(status, "Kontrollera API-inställningarna innan du kör igen.")
    tillfalligt = status == 429 or 500 <= status < 600
    if tillfalligt:
        instruktion = "Tillfälligt fel hos leverantören. Försök igen senare."
    return LeverantorFel(f"Claude-API:t svarade med fel {status}. {instruktion}", tillfalligt=tillfalligt)


def bygg_meddelande(underlag: Avsnittsunderlag, aterkoppling: list[str]) -> str:
    delar = ["Underlag för avsnittet, som JSON:", underlag.model_dump_json(indent=2)]
    if aterkoppling:
        rader = "\n".join(f"- {rad}" for rad in aterkoppling)
        delar.append(f"Det förra utkastet underkändes av den maskinella granskningen. Rätta detta:\n{rader}")
    return "\n\n".join(delar)


def _anvandning(usage: Any) -> tuple[Tokenanvandning, ...]:
    """En post per försök hos API:t. Utan iterationer finns bara svarets egen användning."""
    poster = getattr(usage, "iterations", None) or [usage]
    return tuple(
        Tokenanvandning(
            typ=getattr(post, "type", "message"),
            modell=getattr(post, "model", None),
            indata_token=post.input_tokens,
            utdata_token=post.output_tokens,
            cache_lasning_token=getattr(post, "cache_read_input_tokens", 0) or 0,
            cache_skrivning_token=getattr(post, "cache_creation_input_tokens", 0) or 0,
        )
        for post in poster
    )
