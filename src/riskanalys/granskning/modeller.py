"""Fynd från granskningen (spec 9 och 10)."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from riskanalys.regelverk.modeller import Allvar, Grund


class Fynd(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    typ: Literal["tackning", "sparbarhet", "bristmonster", "provtillsyn", "sakgranskning"]
    regel: str | None = None
    allvar: Allvar
    grund: Grund
    avsnitt: str | None = None
    beskrivning: str
    atgard: str
    status: Literal["öppen", "åtgärdad", "accepterad_metodavvikelse", "sakkunnigbedömd"] = "öppen"
    motivering: str | None = None
    hanterad_av: str | None = None
