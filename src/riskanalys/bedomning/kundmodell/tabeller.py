"""Typade villkor och datum avgränsar kundrader."""

from datetime import date

from riskanalys.regelverk.modeller import Kundmall, Kundrad
from riskanalys.regelverk.villkor import Faltdef, Faltvarde, Sanning, Utfall, tolka_villkor, utvardera


def radutfall(mall: Kundmall, rad: Kundrad, varden: dict[str, Faltvarde], datum: date) -> Utfall:
    """Pröva raden bara när datum och minst en rättslig lydelse är tillämpliga."""
    if (rad.ikraft and datum < rad.ikraft) or (rad.upphor and datum >= rad.upphor):
        return Utfall(Sanning.FALSKT, frozenset())
    if rad.grund == 'ska_krav':
        for id in rad.lydelser:
            if id not in mall.lydelser:
                return Utfall(Sanning.OKANT, frozenset({f'Rättslig lydelse {id} saknas'}))
        giltiga = [
            mall.lydelser[id] for id in rad.lydelser if mall.lydelser[id].ikraft <= datum
            and (mall.lydelser[id].upphor is None or datum < mall.lydelser[id].upphor)
        ]
        if not giltiga:
            return Utfall(Sanning.OKANT, frozenset({f'{rad.id}: giltig lydelse saknas'}))
    definitioner = {k: Faltdef(k, falt.typ, falt.val) for k, falt in mall.falt.items()}
    return utvardera(tolka_villkor(rad.villkor, definitioner), varden)
