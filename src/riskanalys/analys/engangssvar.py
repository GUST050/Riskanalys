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


