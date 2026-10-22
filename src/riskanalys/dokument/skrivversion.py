"""Skrivresultatets version är skild från dokumentets presentationsversion."""
from riskanalys.fel import RiskanalysFel

V5 = 'D-ARB-tjanst-v5'
V6 = 'D-ARB-tjanst-v6'
V7 = 'D-ARB-tjanst-v7'
V8 = 'D-ARB-tjanst-v8'
AKTUELL_SKRIVVERSION = V8
DELAR_V5 = ('hot', 'sarbarheter', 'kontroller', 'risknivaer', 'slutsatser')
DELAR_V6 = ('hot', 'sarbarheter')
DELAR_V7 = ('analys',)
DELAR_V8 = ('analys',)


def delar_for_version(formatversion: str) -> tuple[str, ...]:
    if formatversion == V5:
        return DELAR_V5
    if formatversion == V6:
        return DELAR_V6
    if formatversion == V7:
        return DELAR_V7
    if formatversion == V8:
        return DELAR_V8
    raise RiskanalysFel('Skrivformatet stöds inte för återanvändning. Skriv om utkastet.')
