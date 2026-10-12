"""Promptarnas delar och deras kontrollsummor."""

from riskanalys.dokument.aischema import SCHEMAVERSION
from riskanalys.dokument.promptar.delar import DELAR, modultext
from riskanalys.dokument.promptar.meddelande import bygg_innehall
from riskanalys.dokument.promptar.system import systemprompt
from riskanalys.lagring.kontrollsumma import for_text


def delmodul(del_id: str) -> str:
    return modultext(del_id)


def promptsumma(modell: str, del_id: str) -> str:
    """Kontrollsumma över systemprompt, delmodul och schemaversion (spec 8.4.7)."""
    return for_text("\n".join((systemprompt(modell), modultext(del_id), SCHEMAVERSION)))


__all__ = ["DELAR", "bygg_innehall", "delmodul", "promptsumma", "systemprompt"]
