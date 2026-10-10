"""Claude som textleverantör via den officiella SDK:n (spec 8.3)."""

import json
from datetime import datetime, timezone
from typing import Any

import anthropic

from riskanalys.dokument.leverantor import Anropsdata, Leveranssvar, LeverantorFel, Tokenanvandning
from riskanalys.dokument.modeller import Avsnittsunderlag, AvsnittsUtkast
from riskanalys.lagring.kontrollsumma import for_text

STANDARDMODELL = "claude-opus-5-5"
STANDARDEFFORT = "high"
MAX_TOKENS = 16000
FALLBACK_BETA = "server-side-fallback-2026-07-01"
RESERVMODELLENS_POST = "fallback_message"
SYSTEMPROMPT = """Du skriver ett avsnitt i en redovisningsbyrås allmänna riskbedömning enligt penningtvättsregelverket.

Regler:
- Använd bara uppgifterna i underlaget. Hitta inte på tal, hot, sårbarheter, kontroller eller källor.
- Risknivåerna kommer från en regelmotor. Återge dem exakt och ändra dem aldrig.
- Skriv varje nivå så att det framgår vad den avser, i någon av formerna "Sannolikheten bedöms som hög.", "Konsekvensen är betydande.", "Risken är hög.", "Risken för finansiering av terrorism bedöms som måttlig." och "Den kvarstående risken är hög."
- Varje stycke ska ha referenser till ID:n i underlaget.
- Minst ett stycke ska vara en motivering som hänvisar till hot och till sårbarheter eller uppgifter och anger den inneboende risknivån, till exempel "Risken är hög."
- Om ett stycke bygger på en uppgift som inte är bekräftad, skriv [VERIFIERA] i stycket och lägg till en oklarhet.
- Skriv aldrig namn på personer. Skriv {roll:FfR} när funktionen för regelefterlevnad avses.
- Undvik bristmönstren i underlaget. Skriv konkret om just den här byrån, inte generellt.
- Skriv sakligt och på svenska."""
SCHEMA = AvsnittsUtkast.model_json_schema()
PROMPT_KONTROLLSUMMA = for_text(SYSTEMPROMPT + "\n" + json.dumps(SCHEMA, sort_keys=True, ensure_ascii=False))
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
        try:
            svar = self._klient.beta.messages.create(
                model=self.modell,
                max_tokens=MAX_TOKENS,
                system=SYSTEMPROMPT,
                messages=[{"role": "user", "content": bygg_meddelande(underlag, aterkoppling)}],
                output_config={"effort": self.effort, "format": {"type": "json_schema", "schema": SCHEMA}},
                betas=[FALLBACK_BETA],
                fallbacks="default",
            )
        except anthropic.APIStatusError as fel:
            raise LeverantorFel(f"Claude-API:t svarade med fel {fel.status_code}: {fel.message}") from fel
        except anthropic.APIConnectionError as fel:
            raise LeverantorFel("Kunde inte nå Claude-API:t. Kontrollera nätverket och försök igen.") from fel
        return self._leveranssvar(svar)

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
        )
        for post in poster
    )
