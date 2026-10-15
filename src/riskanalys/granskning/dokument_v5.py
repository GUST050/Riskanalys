"""Bind allt H6-innehåll till samma profil, bedömning och validerade skrivsvar."""
from riskanalys.dokument.arb_v5 import bygg_arb_v5
from riskanalys.dokument.analysunderlag import sarbarhetsstycke
from riskanalys.dokument.delskrivning import Tjanstresultat
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.granskning.analys import mallfynd
from riskanalys.fel import RiskanalysFel


def analysfynd_v5(rb,b,p,d,historik,resultat):
    fynd=[]
    def lagg(id,text,regel=None):
        fynd.append(dict(typ='tackning',allvar='blockerande',grund='metodval',avsnitt=id,
                         **({'regel':regel} if regel else {}),beskrivning=text,
                         atgard='Återskapa dokumentet från aktuellt underlag och sakgranska på nytt.'))
    resultat=resultat or {}
    if any(not isinstance(resultat.get(id),Tjanstresultat) for id,t in tjanster_med_avsnitt(b)):
        lagg('D-ARB','Validerade skrivdelar saknas för en erbjuden tjänst.')
        return fynd
    try:
        expected=bygg_arb_v5(rb,p,b,resultat,historik)
    except RiskanalysFel as error:
        lagg('D-ARB',str(error))
        return fynd
    actual=d.avsnitt_med_id()
    if d.titel!=expected.titel or [a.id for a in d.avsnitt]!=[a.id for a in expected.avsnitt]:
        lagg('D-ARB','Dokumentets titel, ordning eller avsnitt avviker från underlaget.')
    for a in expected.avsnitt:
        if a.id not in actual or actual[a.id].kontrollsumma()!=a.kontrollsumma():
            lagg(a.id,'Text, tabeller eller källhänvisningar avviker från det belagda underlaget.')
        for tab in a.tabeller:
            if tab.id.endswith('-utfall') and any('Begränsning:' in c.text for r in tab.rader for c in r.celler):
                lagg(a.id,'Beräkningen saknar ett fullständigt regelspår och kan inte förklaras säkert.')
    for id,t in tjanster_med_avsnitt(b):
        fynd.extend(mallfynd(resultat[id]))
        if t.egen_erfarenhet is None or not t.egen_erfarenhet.belagd:
            lagg(id,'Aktuellt belägg för egna erfarenheter saknas.','B-15')
        for sid in rb.tjanster[t.tjanst].sarbarheter:
            if rb.sarbarheter[sid].omrade=='geo' and '[VERIFIERA]' in sarbarhetsstycke(rb,p,t.tjanst,sid).text:
                lagg(id,'Geografins aktuella underlag är ofullständigt.','B-09')
    from riskanalys.dokument.likhet import likhetsfynd
    fynd.extend({**f,'typ':'bristmonster','regel':'B-04'} for f in likhetsfynd(list(resultat.values())))
    return fynd
