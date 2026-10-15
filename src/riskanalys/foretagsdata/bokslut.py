"""Tillåtna bokslutsfakta, med period och spårbarhet till privat original."""
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from riskanalys.profil.modeller import Period


class Bokslut(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)
    period: Period
    omsattning: Decimal = Field(ge=0, le=10**15, allow_inf_nan=False)
    medelantal: Decimal | None = Field(default=None, ge=0, le=10**7, allow_inf_nan=False)
    dokument_id: str = Field(min_length=1, max_length=500)
    sha256: str = Field(pattern=r'^[a-f0-9]{64}$')
    fil: str = Field(max_length=500)
    kontext: str = Field(max_length=500)
    taxonomi: str
