"""Samlad bekräftelse av visat underlag; inga fakta eller beslut härleds."""
from typing import Literal
from riskanalys.analys import modeller as m
from riskanalys.analys.gemensam import postsumma, tillampning_aktuell
from riskanalys.fel import RiskanalysFel


class GemensamCell(m.Fryst):
    tjanst: str
    slag: Literal['sarbarhet', 'verksamhet']
    post: str
    postsumma: str


def visade_celler(paket, tjanster: tuple[str, ...]) -> tuple[GemensamCell, ...]:
    if paket.schemaversion != 2:
        raise RiskanalysFel('Starta analysen i schema 2 före gemensam bekräftelse.')
    analyser = {a.tjanst: a for a in paket.tjanster}
    if not tjanster or len(set(tjanster)) != len(tjanster) or set(tjanster) - set(analyser):
        raise RiskanalysFel('Välj unika befintliga tjänster ur analysöversikten.')
    celler = []
    for id in tjanster:
        a = analyser[id]
        for slag, poster, appar in (
            ('sarbarhet', paket.gemensamma_sarbarhetsprovningar, a.sarbarhetstillampningar),
            ('verksamhet', paket.gemensamma_verksamhetsposter, a.verksamhetstillampningar),
        ):
            for post in poster:
                app = next((x for x in appar if x.post == post.id), None)
                if app is None or app.stallningstagande == 'galler':
                    celler.append(GemensamCell(tjanst=id, slag=slag, post=post.id, postsumma=postsumma(post)))
    return tuple(celler)


def bygg_gemensam_bekraftelse(paket, tjanster, celler, forfattare):
    namn = forfattare.strip()
    if not namn or len(namn) > 200:
        raise RiskanalysFel('Ange vem som bekräftar det visade underlaget.')
    forvantat = visade_celler(paket, tjanster)
    if (len(celler) != len(set(celler)) or set(celler) != set(forvantat)):
        raise RiskanalysFel('De visade cellerna har ändrats eller är ofullständiga. Läs om översikten före bekräftelse.')
    ts = []
    for a in paket.tjanster:
        if a.tjanst not in tjanster:
            ts.append(a)
            continue
        andringar = {'forfattare': namn}
        for slag, falt, modell in (
            ('sarbarhet', 'sarbarhetstillampningar', m.Sarbarhetstillampning),
            ('verksamhet', 'verksamhetstillampningar', m.GemensamTillampning),
        ):
            appar = {x.post: x for x in getattr(a, falt)}
            for cell in forvantat:
                if (cell.tjanst, cell.slag) != (a.tjanst, slag):
                    continue
                app = appar.get(cell.post) or modell(post=cell.post, stallningstagande='galler', postsumma=cell.postsumma)
                appar[cell.post] = app.model_copy(update={'postsumma': cell.postsumma, 'bekraftad': True})
            andringar[falt] = tuple(appar.values())
        ts.append(a.model_copy(update=andringar))
    return paket.model_copy(update={'tjanster': tuple(ts)})


def visade_scenarioval(rb, paket, tjanst):
    """Befintliga undantag och synliga standardförslag, utan att bekräfta dem."""
    from riskanalys.analys.provning import scenariosumma
    a = next(x for x in paket.tjanster if x.tjanst == tjanst)
    kopplingar = list(a.scenariokopplingar)
    sedda = {x.scenario for x in kopplingar}
    for s in paket.gemensamma_scenarier:
        if s.id not in sedda and set(s.hot) <= set(rb.tjanster[tjanst].hot):
            kopplingar.append(m.Scenariokoppling(scenario=s.id, tillampning='samma', scenariosumma=scenariosumma(s)))
    return tuple(kopplingar)


def bygg_tjanstbekraftelse(rb, profil, bedomning, paket, tjanst, forfattare):
    from riskanalys.analys.provning import analysbrister, blocksumma, scenariosumma
    if paket.schemaversion != 2:
        raise RiskanalysFel('Starta analysen i schema 2 före tjänstegenomgång.')
    a = next((x for x in paket.tjanster if x.tjanst == tjanst), None)
    t = next((x for x in bedomning.tjanster if x.tjanst == tjanst and x.erbjuds is True), None)
    if a is None or t is None or not forfattare.strip():
        raise RiskanalysFel('Välj en erbjuden tjänst och ange författare.')
    for poster, appar in ((paket.gemensamma_sarbarhetsprovningar, a.sarbarhetstillampningar),
                          (paket.gemensamma_verksamhetsposter, a.verksamhetstillampningar)):
        for post in poster:
            app = next((x for x in appar if x.post == post.id), None)
            if app is None or not tillampning_aktuell(post, app):
                raise RiskanalysFel('Bekräfta det gemensamma underlaget först; pröva tjänstens avvikelser separat.')
    gem = {s.id: s for s in paket.gemensamma_scenarier}
    for prov in a.tackningsprovningar:
        kop = next((k for k in a.scenariokopplingar if k.scenario == prov.lokalt_scenario), None)
        if kop and (not kop.bekraftad or kop.scenariosumma != scenariosumma(gem.get(kop.scenario))):
            raise RiskanalysFel('Bekräfta scenariovalet före täckningsprövningen. Visa och pröva täckningen på nytt; tjänstegenomgången förnyar den inte.')
    kopplingar = []
    for kop in visade_scenarioval(rb, paket, tjanst):
        s = gem.get(kop.scenario)
        if s is None or s.relevans == 'okant':
            raise RiskanalysFel('Komplettera scenariots relevans och innehåll före tjänstegenomgång.')
        kopplingar.append(kop.model_copy(update={'bekraftad': True, 'scenariosumma': scenariosumma(s)}))
    a = a.model_copy(update={'scenariokopplingar': tuple(kopplingar), 'forfattare': forfattare.strip()})
    def byt(q, ny):
        return q.model_copy(update={'tjanster': tuple(ny if x.tjanst == tjanst else x for x in q.tjanster)})
    kandidat = byt(paket, a)
    a = a.model_copy(update={'block': tuple(b.model_copy(update={
        'bekraftad_summa': blocksumma(kandidat, tjanst, b.nummer)}) for b in a.block)})
    kandidat = byt(kandidat, a)
    # En ren prövningsvy: hela gemensamma registret, beläggen och bindningen kvar.
    projektion = kandidat.model_copy(update={'tjanster': (a,)})
    fel = analysbrister(rb, profil, bedomning.model_copy(update={'tjanster': (t,)}), projektion)
    if fel:
        raise RiskanalysFel('Komplettera tjänsteunderlaget före bekräftelse: ' + ' '.join(fel))
    return kandidat


def tjanstefakta(rb, profil, tjanst):
    """Läs redan bekräftade tjänsteuppgifter, även fritext, utan ny lagring."""
    from riskanalys.profil.hantering import visa_varde_klartext
    prefix = rb.tjanster[tjanst].erbjuds_falt.removesuffix('_erbjuds') + '_'
    return tuple((id, rb.falt[id].etikett or rb.falt[id].fraga,
        visa_varde_klartext(rb.falt[id], u.varde), u.kalla, u.datum, u.period, u.bekraftad_av)
        for id, u in profil.uppgifter.items()
        if id.startswith(prefix) and id in rb.falt and profil.ar_bekraftad(id))
