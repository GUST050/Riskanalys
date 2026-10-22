"""Versionshistorik och nästa genomgång (spec 13.1)."""

import calendar
import fcntl
import os
import tempfile
import yaml
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator
from riskanalys.profil.modeller import Uppgift

from riskanalys.lagring.kontrollsumma import for_fil
from riskanalys.lagring.yamlfil import las_modell
from riskanalys.fel import RiskanalysFel

HISTORIKFIL = Path("drift") / "historik.yaml"
GENOMGANG_MANADER = 12
UTVARDERING = "utvärdering"


class Erbjudanderattelse(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)
    tjanst: str
    fore: Uppgift
    efter: Uppgift
    motivering: str = Field(min_length=1, max_length=12000)
    kalla: str = Field(min_length=1, max_length=2000)
    ansvarig: str = Field(min_length=1, max_length=200)
    datum: date
    profilrevision: str

    @model_validator(mode='after')
    def belagg(self):
        from riskanalys.profil.text import kontrollera_text
        for text in (self.motivering, self.kalla, self.ansvarig):
            if not text.strip():
                raise ValueError('Rättelsen kräver motivering, källa och ansvarig.')
            kontrollera_text(text)
        return self


class Handelse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    datum: date
    typ: Literal["utvärdering", "uppdatering", "fastställelse", "rättelse"]
    beskrivning: str
    version: int | None = None
    plan_id: str | None = None
    plansumma: str | None = Field(default=None, pattern=r'^sha256:[0-9a-f]{64}$')
    rattelse: Erbjudanderattelse | None = None

    @model_validator(mode='after')
    def avgransning(self):
        if (self.plan_id is None) != (self.plansumma is None) or self.plan_id is not None and self.typ != 'utvärdering':
            raise ValueError('Planutvärderingen kräver både plan-ID och plansumma.')
        if (self.typ == 'rättelse') != (self.rattelse is not None) or self.rattelse and self.rattelse.datum != self.datum:
            raise ValueError('Rättelsehändelsen kräver en rättelse med samma datum.')
        return self

    @model_serializer(mode='wrap')
    def serialisera(self, handler):
        data = handler(self)
        for falt in ('plan_id', 'plansumma', 'rattelse'):
            if getattr(self, falt) is None:
                data.pop(falt, None)
        return data


class Historik(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    handelser: tuple[Handelse, ...] = ()

    def med(self, handelse: Handelse) -> "Historik":
        return Historik(handelser=(*self.handelser, handelse))

    def senaste_utvardering(self) -> date | None:
        """Datum för den senaste utvärderingen. Fastställelser och uppdateringar räknas inte."""
        return max((h.datum for h in self.handelser if h.typ == UTVARDERING and h.plan_id is None), default=None)

    def senaste_uppdatering(self) -> date | None:
        """Senaste separata uppdatering, utan att flytta utvärderingsfristen."""
        return max((h.datum for h in self.handelser if h.typ == "uppdatering"), default=None)

    def nasta_genomgang(self) -> date | None:
        senaste = self.senaste_utvardering()
        return None if senaste is None else lagg_till_manader(senaste, GENOMGANG_MANADER)


def lagg_till_manader(datum: date, manader: int) -> date:
    """Lägger till månader. Finns inte dagen i målmånaden blir det månadens sista dag."""
    index = datum.month - 1 + manader
    ar, manad = datum.year + index // 12, index % 12 + 1
    return date(ar, manad, min(datum.day, calendar.monthrange(ar, manad)[1]))


def las_historik(byramapp: Path) -> Historik:
    sokvag = byramapp / HISTORIKFIL
    if not sokvag.is_file():
        return Historik()
    return las_modell(sokvag, Historik)


def _spara_atomiskt(fil: Path, historik: Historik) -> None:
    temp = None
    try:
        fd, temp = tempfile.mkstemp(dir=fil.parent, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            yaml.safe_dump(historik.model_dump(mode="json"), out, allow_unicode=True, sort_keys=False)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temp, fil)
        temp = None
        fd = os.open(fil.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        if temp and os.path.exists(temp):
            os.unlink(temp)


def _skriv_historik(byramapp: Path, *, historik: Historik | None = None, handelse: Handelse | None = None) -> Historik:
    """CLI och webb låser samma hela läs–lägg till–skriv-operation."""
    fil = byramapp / HISTORIKFIL
    try:
        fil.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd = os.open(fil.parent / ".skrivlas", os.O_RDWR | os.O_CREAT, 0o600)
        with os.fdopen(fd, "w") as las:
            fcntl.flock(las, fcntl.LOCK_EX)
            resultat = las_historik(byramapp).med(handelse) if handelse is not None else historik
            assert resultat is not None
            _spara_atomiskt(fil, resultat)
            return resultat
    except OSError as exc:
        raise RiskanalysFel("Historiken kunde inte sparas. Kontrollera ledigt utrymme och skrivbehörighet.") from exc


def spara_historik(byramapp: Path, historik: Historik) -> None:
    """Sparar en hel historik, exempelvis en fryst paketkopia. Använd registrera_handelse för tillägg."""
    _skriv_historik(byramapp, historik=historik)


def registrera_handelse(byramapp: Path, handelse: Handelse) -> Historik:
    return _skriv_historik(byramapp, handelse=handelse)


def historikens_kontrollsumma(byramapp: Path) -> str:
    sokvag = byramapp / HISTORIKFIL
    return for_fil(sokvag) if sokvag.is_file() else ""
