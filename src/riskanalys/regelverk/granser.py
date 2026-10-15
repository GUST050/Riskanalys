"""Metodgränser för visning, med ett index som kan återanvändas under en rendering."""

from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.villkor import Inte, Jamforelse, ORDNINGSOPERATORER, tolka_villkor


def _jamforelser(villkor):
    if isinstance(villkor, Jamforelse):
        yield villkor
    elif isinstance(villkor, Inte):
        yield from _jamforelser(villkor.inre)
    else:
        for del_ in villkor.delar:
            yield from _jamforelser(del_)


def metodgransindex(regelbas: Regelbas) -> dict[str, tuple[float, ...]]:
    """Bygg en lokal ögonblicksbild; inget muterbart regelbasobjekt cachas globalt."""
    samlade: dict[str, set[float]] = {}
    definitioner = regelbas.faltdefinitioner()
    for s in regelbas.sarbarheter.values():
        for j in _jamforelser(tolka_villkor(s.villkor, definitioner)):
            if j.op in ORDNINGSOPERATORER and type(j.varde) in (int, float) and 0 < j.varde < 1:
                samlade.setdefault(j.falt, set()).add(float(j.varde))
    return {falt: tuple(sorted(granser)) for falt, granser in samlade.items()}


def metodgranser(regelbas: Regelbas, falt_id: str, index: dict | None = None) -> tuple[float, ...]:
    return (metodgransindex(regelbas) if index is None else index).get(falt_id, ())
