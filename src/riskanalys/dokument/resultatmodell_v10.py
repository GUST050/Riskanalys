"""Källbunden V10-konstruktion; generiska frysta källtyper återanvänds."""
from typing import Literal
from riskanalys.dokument.modeller import Dokument
from riskanalys.dokument.resultatmodell_v9 import (
    Fryst, Kallreferens, ResultatunderlagV9, TransformationV9,
)


class KonstruktionV10(Fryst):
    placering: str
    mall: str = 'D-ARB-v10-konstruktion-1'
    produktionsslag: Literal['programmall', 'lokalt_original', 'regelbas']
    kallor: tuple[Kallreferens, ...]


class ResultatbyggeV10(Fryst):
    dokument: Dokument
    analysdokument: Dokument
    underlag: ResultatunderlagV9
    transformationer: tuple[TransformationV9, ...]
    konstruktioner: tuple[KonstruktionV10, ...]
