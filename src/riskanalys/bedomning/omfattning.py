"""Dokumentomfattning efter storlek och art; inget undantag från lagkrav."""
from riskanalys.bedomning.modeller import Proportionalitet
from riskanalys.bedomning.erfarenheter import belagd_uppgift
from riskanalys.regelverk.villkor import falt_i, tolka_villkor, utvardera, Sanning

def bedom_omfattning(rb, profil, tjanster):
    metod = rb.metod.omfattning
    if not metod:
        return None
    enk = tolka_villkor(metod.enkel_villkor, rb.faltdefinitioner())
    uto = tolka_villkor(metod.utokad_villkor, rb.faltdefinitioner())
    e = utvardera(enk, profil.faltvarden())
    u = utvardera(uto, profil.faltvarden())
    refs = falt_i(enk) | falt_i(uto)
    saknas = {id for id in refs if not belagd_uppgift(rb, profil, id)} | set(e.okanda) | set(u.okanda)
    hogrisk = any((t.inneboende and (t.inneboende.risk in {'hög', 'mycket hög'} or t.terrorfinansiering.risk in {'hög', 'mycket hög'}) for t in tjanster))
    niva = 'utökad' if u.sanning is not Sanning.FALSKT or hogrisk else 'enkel' if e.sanning is Sanning.SANT else 'standard'
    return Proportionalitet(niva=niva, status='preliminär' if saknas else 'slutlig', regelspar=(metod.id,), okanda_uppgifter=tuple(sorted(saknas)))
