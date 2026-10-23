"""Bekräftad faktastatus hålls skild från motorns försiktighetspåslag."""
from riskanalys.bedomning.erfarenheter import belagd_uppgift
from riskanalys.regelverk.villkor import Jamforelse, Sanning, falt_i, tolka_villkor, utvardera


def rapportbelagd(rb, profil, id):
    if not belagd_uppgift(rb, profil, id):
        return False
    u = profil.uppgifter[id]
    if u.datum > profil.byra.datum or u.period and u.period.till > profil.byra.datum:
        return False
    f = rb.falt[id]
    from riskanalys.profil.katalogstatistik import ANTAL, HEMVIST, statistikbrister
    if id in ANTAL:
        fel = statistikbrister(profil)
        if any(x.startswith(id + ':') or id in HEMVIST and x.startswith('Hemvistfördelningen') for x in fel):
            return False
    if f.periodkrav and id.startswith(('P-KUND.', 'P-GEO.', 'P-KANAL.', 'P-RISK.')):
        bas = profil.uppgifter.get(f.basfalt or 'P-KUND.antal_aktiva')
        if not bas or not bas.period or u.period != bas.period:
            return False
    if f.typ == 'andel' and f.antalfalt and f.basfalt:
        if not all(rapportbelagd(rb, profil, x) for x in (f.antalfalt, f.basfalt)):
            return False
        antal, bas = (profil.uppgifter[x] for x in (f.antalfalt, f.basfalt))
        from math import isclose
        if (type(antal.varde) not in (int, float) or type(bas.varde) not in (int, float)
                or bas.varde <= 0 or antal.period != bas.period or u.period != bas.period
                or not isclose(u.varde, antal.varde / bas.varde, abs_tol=1e-9)):
            return False
    return True


def villkor_for(rb, post):
    return tolka_villkor(post.villkor, rb.faltdefinitioner())


def faktorstatus(rb, profil, sarbarhet):
    tjanster = [t for id, t in rb.tjanster.items()
                if id in rb.regelpaket[profil.byra.regelpaket].tjanster and sarbarhet.id in t.sarbarheter]
    if tjanster and all(rapportbelagd(rb, profil, t.erbjuds_falt)
                       and profil.uppgifter[t.erbjuds_falt].varde is False for t in tjanster):
        return 'Inte tillämplig'
    villkor = villkor_for(rb, sarbarhet)
    falt = falt_i(villkor)
    if any(not rapportbelagd(rb, profil, id) for id in falt):
        return 'Okänt'
    utfall = utvardera(villkor, profil.faltvarden())
    if utfall.sanning is Sanning.SANT:
        return 'Finns'
    if utfall.sanning is Sanning.OKANT:
        return 'Okänt'
    varden = [profil.uppgifter[id].varde for id in falt]
    if varden and all(v is False or type(v) in (int, float) and v == 0 for v in varden):
        return 'Nej'
    if isinstance(villkor, Jamforelse) and villkor.op in ('>', '>='):
        v = profil.uppgifter[villkor.falt].varde
        if type(v) in (int, float) and v > 0:
            return 'Under tröskeln'
    # Ett känt falskt sammansatt villkor är inte belägg för frånvaro.
    return 'Okänt'


def lagre_status(rb, profil, post):
    if any(not rapportbelagd(rb, profil, id) for id in post.profilfalt):
        return 'Okänt'
    if not post.landbedomningar:
        return 'Finns' if any(profil.uppgifter[id].varde > 0 for id in post.profilfalt) else 'Nej'
    grupper = {id.rsplit('hemvist_', 1)[-1]: profil.uppgifter[id].varde for id in post.profilfalt}
    aktuella = [l for l in post.landbedomningar if grupper.get(l.grupp, 0) > 0]
    if any(l.bedomning == 'kan_tala_for_lagre' for l in aktuella):
        return 'Finns'
    return 'Okänt' if aktuella else 'Nej'
