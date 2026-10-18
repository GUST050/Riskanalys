"""Promptarnas delar och deras kontrollsummor."""

from riskanalys.dokument.aischema import SCHEMAVERSION, SCHEMAVERSION_V7
from riskanalys.dokument.skrivversion import V5, V7
from riskanalys.dokument.promptar.delar import DELAR, modultext
from riskanalys.dokument.promptar.meddelande import bygg_innehall
from riskanalys.dokument.promptar.system import systemprompt
from riskanalys.lagring.kontrollsumma import for_text


def delmodul(del_id: str, *, formatversion: str = V5) -> str:
    return modultext(del_id, formatversion=formatversion)


def promptsumma(modell: str, del_id: str, *, formatversion: str = V5) -> str:
    """Kontrollsumma över systemprompt, delmodul och schemaversion (spec 8.4.7)."""
    return for_text("\n".join((systemprompt(modell, formatversion=formatversion), modultext(del_id, formatversion=formatversion),
                                 SCHEMAVERSION_V7 if formatversion == V7 else SCHEMAVERSION)))


__all__ = ["DELAR", "bygg_innehall", "delmodul", "promptsumma", "systemprompt"]
