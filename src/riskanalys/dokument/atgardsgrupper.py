"""Rubrikgrupper av registrerade rutinåtgärder med fulla tjänstemedlemmar."""
from dataclasses import dataclass
from riskanalys.analys.modeller import Analyspaket, Rutinatgard


def _nyckel(post):
    return post.atgard, post.rutin_id, post.rutin_version


@dataclass(frozen=True)
class Atgardsgrupp:
    medlemmar: tuple[tuple[str, Rutinatgard], ...]

    def __post_init__(self):
        if not self.medlemmar:
            raise ValueError('En åtgärdsgrupp måste ha minst en medlem.')
        if len(self.medlemmar)>1 and (not self.medlemmar[0][1].atgard.strip() or
                len({_nyckel(p) for _,p in self.medlemmar}) != 1):
            raise ValueError('Endast identisk icke-tom åtgärdstext och rutinbindning får grupperas.')


def gruppera_rutinatgarder(analys: Analyspaket) -> tuple[Atgardsgrupp, ...]:
    grupper = {}
    for tjanst in analys.tjanster:
        for post in tjanst.rutinatgarder:
            nyckel = _nyckel(post) if post.atgard.strip() else object()
            grupper.setdefault(nyckel, []).append((tjanst.tjanst, post))
    return tuple(Atgardsgrupp(tuple(grupp)) for grupp in grupper.values())
