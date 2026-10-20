"""Ren exakt visningsgruppering; inga fyndbeslut ändras."""
from dataclasses import dataclass
from riskanalys.granskning.modeller import Fynd


@dataclass(frozen=True)
class Fyndgrupp:
    medlemmar: tuple[Fynd, ...]

    def __post_init__(self):
        if not self.medlemmar:
            raise ValueError('En fyndgrupp måste ha minst en medlem.')
        if len({p.model_dump_json(exclude={'id'}) for p in self.medlemmar}) != 1:
            raise ValueError('Alla sakfält i en fyndgrupp måste vara identiska.')


def gruppera_fynd(fynd: tuple[Fynd, ...]) -> tuple[Fyndgrupp, ...]:
    grupper = {}
    for post in fynd:
        grupper.setdefault(post.model_dump_json(exclude={'id'}), []).append(post)
    return tuple(Fyndgrupp(tuple(grupp)) for grupp in grupper.values())
