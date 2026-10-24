"""Frysta källor och exakt flyttregister för V10:s andra presentation."""
from pydantic import BaseModel, ConfigDict
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.analys.modeller import Analyspaket
from riskanalys.bedomning.modeller import Bedomning


class RedaktionV10(BaseModel):
    model_config=ConfigDict(frozen=True,extra='forbid')
    regelbas: Regelbas
    analys: Analyspaket | None
    bedomning: Bedomning
    flyttar: tuple[dict,...]
    scenariogrupper: tuple[dict,...]
    scenariomedlemskap: tuple[dict,...]
