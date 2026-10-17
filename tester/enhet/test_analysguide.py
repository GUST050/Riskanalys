"""Guiden får inte gömma obligatoriska bedömningar eller kalla utkast attesterade."""
from datetime import date

import pytest

from riskanalys.analys.modeller import Analysbindning, Analysblock, Analyspaket, Scenarioanalys, Tjansteanalys


def paket():
    return Analyspaket(bindning=Analysbindning(byra='syntetisk', profilrevision='p', bedomningsmanifest='b', utkastmanifest='u', regelbas='r', kallunderlag='k', historik='h', bedomningsdatum=date(2026, 1, 1), modell='m'), gemensamma_scenarier=(Scenarioanalys(id='gem', rubrik='Delat'),), tjanster=tuple(Tjansteanalys(tjanst=f'T-{n}', block=tuple(Analysblock(nummer=i, aktivering='aktiv', motivering='Syntetiskt prov') for i in range(1, 17)), scenarier=(Scenarioanalys(id=f'lokal-{n}'),)) for n in range(4)))


def test_arbetsborda_skiljer_block_scenarier_och_oskrivna_utkast():
    from riskanalys.analys.guide import arbetsborda
    b = arbetsborda(paket())
    assert b.alltid == 40
    assert b.villkorade == 24
    assert b.unika_scenarier == 5
    assert b.bekraftade_block == 0
    assert b.gemensamma_val == 0
    assert b.nyskrivna_kompletteringar is None


def test_villkorad_okand_franvaro_ar_inte_avgransad():
    from riskanalys.analys.guide import guideblock
    rader = guideblock(Tjansteanalys(tjanst='T'))
    assert len(rader) == 16
    assert rader[2].aktivering == 'okand'
    assert rader[0].obligatorisk
    assert not rader[2].obligatorisk


def test_checklista_fyrtjanstfall_redovisar_64_block_och_12_scenarier():
    from riskanalys.analys.guide import arbetsborda
    from riskanalys.analys.modeller import Scenariokoppling
    from riskanalys.analys.provning import scenariosumma
    p = paket()
    gem = tuple(Scenarioanalys(id=f'gem-{i}', hot=(f'H-{i}',)) for i in range(8))
    tjanster = tuple(t.model_copy(update={'scenariokopplingar': tuple(Scenariokoppling(scenario=s.id, tillampning='samma', scenariosumma=scenariosumma(s), bekraftad=True) for s in gem)}) for t in p.tjanster)
    p = p.model_copy(update={'gemensamma_scenarier': gem, 'tjanster': tjanster})
    b = arbetsborda(p)
    assert b.alltid + b.villkorade == 64
    assert b.unika_scenarier == 12
    assert b.gemensamma_val == 32
    assert b.nyskrivna_kompletteringar is None


def test_ateranvant_belagg_raknas_som_referenser_inte_nya_uppladdningar():
    from riskanalys.analys.guide import arbetsborda
    p = paket()
    t = p.tjanster[0].model_copy(update={'exponeringsbelagg': ('B-1',), 'erfarenhetsbelagg': ('B-1',)})
    b = arbetsborda(p.model_copy(update={'tjanster': (t,)}))
    assert b.belaggsreferenser == 2
    assert b.ateranvanda_belaggsreferenser == 1
