"""Kort katalogstatus i huvudtext; komplett källbunden beskrivning finns i B1."""
from riskanalys.dokument.arb_v5 import stycke


def rackviddsoversikt(rb, bedomning):
    poster = [stycke('Källbeskrivning är inte faktiskt genomförande eller scenariotäckning. Fulla observationer, begränsningar, förutsättningar och sakkunnigstatus finns i bilaga B1.', ['D-ARB.B1'])]
    kontrolltjanster = {}
    for t in bedomning.tjanster:
        if t.erbjuds is False:
            continue
        for k in (*t.kontroller, *((t.sanktionsrisk.kontroll,) if t.sanktionsrisk and t.sanktionsrisk.kontroll else ())):
            kontrolltjanster.setdefault(k.id, []).append(t.tjanst)
    okanda = []
    for id, tjanster in kontrolltjanster.items():
        k = rb.kontroller[id]
        beskrivna = [t for t in tjanster if any(r.tjanst == t and r.beskrivningsstatus == 'beskriven' for r in k.rackvidd)]
        okand = [t for t in tjanster if t not in beskrivna]
        if beskrivna:
            poster.append(stycke(k.namn+': källbunden möjlig observation finns för '+', '.join(rb.tjanster[t].namn for t in beskrivna)
                + '. Den bevisar inte kontrollens lokala effekt. Ett matchande synligt betalningsflöde styrker varken underliggande affär eller samtliga betalningsled.', [id, *beskrivna, 'D-ARB.B1']))
        if okand:
            okanda.append(k.namn+' ('+', '.join(rb.tjanster[t].namn for t in okand)+')')
    if okanda:
        poster.append(stycke('Källbunden scenariotäckning är okänd för: '+'; '.join(okanda)
            + '. Saknat källstöd får inte bli positiv täckning eller ett godkännande av motorns reduktion. Pröva faktiskt genomförande och kvarstående begränsning per tjänst.', [*kontrolltjanster, 'D-ARB.B1']))
    return tuple(poster)
