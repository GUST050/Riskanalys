"""Aktiveringsfrågor går före följdfrågor; alias och andelar frågas aldrig två gånger."""
from riskanalys.intag.modeller import Intagsfraga
from riskanalys.profil.modeller import Profil
from riskanalys.profil.omfattning import aktivt, kompatibilitetsvy
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.villkor import falt_i, tolka_villkor


def fragor(rb: Regelbas, profil: Profil) -> tuple[Intagsfraga, ...]:
    p = kompatibilitetsvy(profil, rb)
    resultat = []
    for f in rb.falt.values():
        if not f.intag or f.alias_for or f.basfalt or not aktivt(f, p, rb):
            continue
        # En okänd aktivering ska först besvaras, inte fylla skärmen med möjliga följdfrågor.
        if f.kritisk_om:
            beroenden = falt_i(tolka_villkor(f.kritisk_om, rb.faltdefinitioner()))
            if any(not p.ar_bekraftad(k) for k in beroenden):
                continue
        resultat.append(Intagsfraga(f, p.ar_bekraftad(f.id)))
    ordnade = sorted(resultat, key=lambda q: (q.falt.intag.ordning, q.falt.id))
    register = {q.falt.id: q for q in ordnade}
    klara = set()
    svar = []
    def lagg_till(q):
        if q.falt.id in klara:return
        klara.add(q.falt.id)
        for id in q.falt.intag.beroenden:
            if id in register:lagg_till(register[id])
        svar.append(q)
    for q in ordnade:lagg_till(q)
    return tuple(svar)
