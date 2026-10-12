"""Schemat som AI svarar i. API:t garanterar formen; valideringen kontrollerar innehållet (spec 8.4.2)."""

from pydantic import ValidationError

from riskanalys.dokument.modeller import AISvar, AvsnittsUtkast, Oklarhet, Textstycke

SCHEMAVERSION = "ai-svar-v1"
INGEN_UPPGIFT = "ingen_uppgift"
STYCKETYPER = ("analys", "motivering", "scenario")


def ai_schema(tillatna_id: frozenset[str], uppgift_id: frozenset[str]) -> dict:
    """JSON-schema med enum för referenser och oklarheter. Ett tomt enum är ogiltigt, därav reservvärdet."""
    stycke = {
        "type": "object",
        "additionalProperties": False,
        "required": ["typ", "referenser", "text"],
        "properties": {
            "typ": {"type": "string", "enum": list(STYCKETYPER)},
            "referenser": {"type": "array", "items": {"type": "string", "enum": sorted(tillatna_id)}},
            "text": {"type": "string"},
        },
    }
    oklarhet = {
        "type": "object",
        "additionalProperties": False,
        "required": ["uppgift_id", "fraga"],
        "properties": {
            "uppgift_id": {"type": "string", "enum": sorted(uppgift_id) or [INGEN_UPPGIFT]},
            "fraga": {"type": "string"},
        },
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["stycken", "oklarheter"],
        "properties": {
            "stycken": {"type": "array", "items": stycke},
            "oklarheter": {"type": "array", "items": oklarhet},
        },
    }


def _kanonisk(varde: str, tillatna: frozenset[str]) -> str:
    """API:t garanterar inte skiftläget i enum-värden; jämför utan hänsyn till det."""
    return {id.lower(): id for id in tillatna}.get(varde.lower(), varde)


def tolka_ai_svar(text: str, avsnitt: str, tillatna_id: frozenset[str]) -> AvsnittsUtkast:
    """AI-svaret som AvsnittsUtkast. Äldre svar med avsnittsfält godtas för testsvar och sparade körningar."""
    try:
        svar = AISvar.model_validate_json(text)
    except ValidationError:
        return AvsnittsUtkast.model_validate_json(text)
    return AvsnittsUtkast(
        avsnitt=avsnitt,
        stycken=[
            Textstycke(typ=s.typ, text=s.text, referenser=[_kanonisk(r, tillatna_id) for r in s.referenser])
            for s in svar.stycken
        ],
        oklarheter=[Oklarhet(fraga=o.fraga, saknad_uppgift=_kanonisk(o.uppgift_id, tillatna_id)) for o in svar.oklarheter],
    )


def tolka_delsvar(text: str, tillatna_id: frozenset[str], uppgift_id: frozenset[str]) -> AISvar:
    svar=AISvar.model_validate_json(text)
    return svar.model_copy(update={
        "stycken":[s.model_copy(update={"referenser":[_kanonisk(r,tillatna_id) for r in s.referenser]}) for s in svar.stycken],
        "oklarheter":[o.model_copy(update={"uppgift_id":_kanonisk(o.uppgift_id,uppgift_id)}) for o in svar.oklarheter],
    })
