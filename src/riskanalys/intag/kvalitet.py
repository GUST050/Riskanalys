"""Samma sakliga begränsningar gäller formulär, CLI och handredigerade profiler."""
from datetime import date
from riskanalys.profil.omfattning import aktivt


def kvalitetsbrister(rb, profil) -> tuple[str, ...]:
    hinder=[]
    if profil.byra.datum > date.today():
        hinder.append('Bedömningsdatum får inte ligga i framtiden.')
    for f in rb.falt.values():
        u=profil.uppgifter.get(f.id)
        if not u or u.status!='bekräftad' or u.inaktuell or not aktivt(f,profil,rb):continue
        if u.datum and u.datum > date.today():
            hinder.append(f'{f.id}: bekräftelsedatum får inte ligga i framtiden.')
        if u.period and u.period.till > profil.byra.datum:
            hinder.append(f'{f.id}: statistikperioden slutar efter bedömningsdatumet.')
        if f.typ in ('heltal','tal') and type(u.varde) in (int,float) and u.varde < 0:
            hinder.append(f'{f.id}: antal och belopp får inte vara negativa.')
        if f.id in ('P-ORG.antal_anstallda','P-ORG.verksamhetsstallen') and type(u.varde) is int and u.varde < 1:
            hinder.append(f'{f.id}: ange minst en person respektive ett verksamhetsställe.')
    return tuple(hinder)
