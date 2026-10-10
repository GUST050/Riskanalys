"""Dokumenttäckning följer typade mål, med explicit M1-kompatibilitet."""
from riskanalys.regelverk.urval import kravet_galler

def dokumentmal(krav, dokument_id):
    mal=[m.id for m in krav.mal if m.typ=="dokument"] if krav.mal else list(krav.uppfylls_i)
    return tuple(id for id in mal if id.startswith(dokument_id+"."))

def krav_for_dokument(regelbas,urval,profil,dokument_id):
    return tuple(v for v in urval.krav if dokumentmal(v.krav,dokument_id)
                 and kravet_galler(regelbas,v.krav,profil.faltvarden()))
