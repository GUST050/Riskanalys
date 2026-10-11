import pytest
from datetime import date, datetime, time, timedelta, timezone
from importlib import import_module
from itertools import count
from riskanalys.regelverk.laddning import ladda_regelbas
from riskanalys.profil.hantering import skapa_profil
from riskanalys.profil.modeller import Byra
from tester.fixturer.m2 import DAG, komplett_profil


@pytest.fixture(autouse=True)
def intagsklocka(monkeypatch):
    """Bedömning och hämtning använder samma syntetiska dag, oavsett körningsdag."""
    class Testdatum(date):
        @classmethod
        def today(cls):
            return DAG

        @classmethod
        def fromisoformat(cls, text):
            # Vanliga date-objekt behövs vid YAML-lagring av formulärsvar.
            return date.fromisoformat(text)

    steg = count()
    start = datetime.combine(DAG, time(10), tzinfo=timezone.utc)

    class Testtid(datetime):
        @classmethod
        def now(cls, tz=None):
            # Två hämtningar ska fortsatt ge olika snapshots/kontrollsummor.
            tid = start + timedelta(microseconds=next(steg))
            return tid.astimezone(tz) if tz else tid.astimezone().replace(tzinfo=None)

    for namn in ('kvalitet', 'svar', 'tjanst', 'utvardering', 'webb', 'vyer', 'registervy', 'tjanstvy', 'dokument'):
        monkeypatch.setattr(import_module('riskanalys.intag.' + namn), 'date', Testdatum)
    for namn in ('profil_kommando', 'drift_kommando'):
        monkeypatch.setattr(import_module('riskanalys.kommandon.' + namn), 'date', Testdatum)
    monkeypatch.setattr(import_module('riskanalys.foretagsdata.scb'), 'datetime', Testtid)


@pytest.fixture(scope='session')
def rb_intag():
    return ladda_regelbas()

@pytest.fixture
def tom(rb_intag):
    return skapa_profil(rb_intag, Byra(id='syntetisk', lan='Västra Götaland', regelpaket='RP-RED-VG', datum=DAG))

@pytest.fixture
def klar(rb_intag, tom):
    return komplett_profil(rb_intag, tom)
