"""Deklarerade grupper är lokala belägg. De ändrar inga motorvikter eller trösklar."""
from riskanalys.profil.hantering import belaggsbrister
from riskanalys.profil.modeller import Profil


def kombinationsbrister(rb, profil):
    fel, sett = [], set()
    for g in profil.kombinationsgrupper:
        if g.id in sett:
            fel.append(f'{g.id}: grupp-ID måste vara unikt.')
        sett.add(g.id)
        if g.tjanst not in rb.tjanster:
            fel.append(f'{g.id}: välj en registrerad tjänst.')
            continue
        from riskanalys.regelverk.urval import valj
        if g.tjanst not in valj(rb,profil.byra.regelpaket,profil.byra.datum,profil.byra.lan).tjanster:
            fel.append(f'{g.id}: tjänsten ingår inte i byråns regelpaket.')
        if not g.avgransning.strip() or not g.beskrivning.strip():
            fel.append(f'{g.id}: beskriv gruppen och dess avgränsning.')
        if len(set(g.sarbarheter)) != len(g.sarbarheter) or set(g.sarbarheter) - set(rb.tjanster[g.tjanst].sarbarheter):
            fel.append(f'{g.id}: ange unika sårbarhets-ID:n som hör till tjänsten.')
        fel.extend(belaggsbrister(Profil(byra=profil.byra, uppgifter={g.id+'.antal':g.antal, g.id+'.bas':g.bas})))
        for u in (g.antal, g.bas):
            if u.status == 'bekräftad' and (u.inaktuell or type(u.varde) is not int or u.varde < 0 or u.period is None
                    or u.datum is None or u.datum > profil.byra.datum or u.period.till > profil.byra.datum):
                fel.append(f'{g.id}: bekräftade antal kräver aktuellt heltal, period och datum senast bedömningsdagen.')
        if g.antal.status == g.bas.status == 'bekräftad':
            if any(getattr(g.antal, f) != getattr(g.bas, f) for f in ('period','kalla','bekraftad_av','datum')):
                fel.append(f'{g.id}: antal och bas måste avse samma period, källa och bekräftelse.')
            if type(g.antal.varde) is int and type(g.bas.varde) is int and g.antal.varde > g.bas.varde:
                fel.append(f'{g.id}: antal får inte överstiga basen för samma {g.population}.')
    return tuple(fel)


def grupper_for_tjanst(rb, profil, tjanst):
    return tuple(g for g in profil.kombinationsgrupper if g.tjanst == tjanst and tjanst in rb.tjanster)
