"""Användarmeddelandet i fast ordning: faktablad först, uppgiften sist (spec 8.4.2)."""

from riskanalys.dokument.faktablad import Faktablad, faktablad_json
from riskanalys.dokument.promptar.delar import modultext
from riskanalys.dokument.skrivversion import V5


def _block(tagg: str, innehall: str, *, attribut: str = "") -> dict:
    return {"type": "text", "text": f"<{tagg}{attribut}>\n{innehall}\n</{tagg}>"}


def bygg_innehall(fb: Faktablad, del_id: str, lasta: tuple[str, ...], maskinellt_validerat: tuple[str, ...],
                  aterkoppling: tuple[str, ...], *, formatversion: str = V5) -> list[dict]:
    block = [{**_block("faktablad", faktablad_json(fb)), "cache_control": {"type": "ephemeral"}}]
    if lasta:
        block.append(_block("lasta_meningar", "\n".join(lasta)))
    if maskinellt_validerat:
        block.append(_block("maskinellt_validerat", "\n\n".join(maskinellt_validerat)))
    block.append(_block("uppgift", modultext(del_id, formatversion=formatversion), attribut=f' del="{del_id}"'))
    if aterkoppling:
        rader = "\n".join(f"- {rad}" for rad in aterkoppling)
        block.append(_block("aterkoppling", f"Förra försöket underkändes. Rätta detta:\n{rader}"))
    return block
