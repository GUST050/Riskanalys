"""Aktiveringsfrågor går före följdfrågor; alias och andelar frågas aldrig två gånger."""
from riskanalys.intag.modeller import Intagsfraga
from riskanalys.intag.verksamhetsval import erbjuds_aktuellt, verksamhetsval
from riskanalys.intag.fordelning import aktiverad, faltkoppling, fragetext, tjanstefordelning
from riskanalys.profil.modeller import Profil
from riskanalys.profil.omfattning import aktivitetsprov, kompatibilitetsvy
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.villkor import falt_i, tolka_villkor


def fragor(rb: Regelbas, profil: Profil) -> tuple[Intagsfraga, ...]:
    p = kompatibilitetsvy(profil, rb)
    aktiv = aktivitetsprov(p, rb)
    resultat = []
    for f in rb.falt.values():
        koppling = faltkoppling(rb, f.id)
        if koppling:
            if aktiverad(rb, p, f.id):
                dynamisk = f.model_copy(update={'fraga': fragetext(rb, p, f.id)})
                resultat.append(Intagsfraga(dynamisk, koppling[1] in tjanstefordelning(rb, p, koppling[0].id)))
            continue
        if not f.intag or f.alias_for or f.basfalt or not aktiv(f):
            continue
        val = verksamhetsval(rb, f.id)
        if val and not erbjuds_aktuellt(p, val[0]):
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
