"""V6 återbyggs från exakt fryst lokal analys och validerade skrivresultat."""
from riskanalys.analys.provning import analysbrister, gallande_beslut
from riskanalys.dokument.arb_v6 import bygg_arb_v6
from riskanalys.dokument.delskrivning import Tjanstresultat
from riskanalys.dokument.skrivversion import V6
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.fel import RiskanalysFel
from riskanalys.granskning.lasta_v6 import lasta_fynd_v6
from riskanalys.regelverk.granser import metodgransindex


def analyskronologihinder(bedomning,analys,datum):
    """Bara senaste aktuella ja är underlag för detta stegs datumprövning."""
    if analys is None:return ()
    hinder=[]
    for _,t in tjanster_med_avsnitt(bedomning):
        beslut=gallande_beslut(analys,t.tjanst)
        if beslut is not None and beslut.godkand and beslut.datum > datum:
            hinder.append(f'{t.tjanst}: datum {datum.isoformat()} är före det lokala analysgodkännandet '
                f'{beslut.datum.isoformat()}. Ange samma eller senare datum, eller rätta det senaste analysbeslutet.')
    return tuple(hinder)


def analyshinder(rb,profil,bedomning,analys,*,datum=None):
    if analys is None:return ('Lokal analys saknas. Komplettera och godkänn varje erbjuden tjänst.',)
    hinder=list(analysbrister(rb,profil,bedomning,analys))
    for _,t in tjanster_med_avsnitt(bedomning):
        beslut=gallande_beslut(analys,t.tjanst)
        if beslut is None or not beslut.godkand:
            hinder.append(f'{t.tjanst}: aktuellt lokalt godkännande saknas.')
    if datum is not None:
        hinder.extend(analyskronologihinder(bedomning,analys,datum))
    return tuple(dict.fromkeys(hinder))


def analysfynd_v6(rb,b,p,d,historik,resultat,*,analys=None,modellrapport=None,analysbrister_filer=(),granskningsdatum=None):
    fynd=[]
    def lagg(id,text):
        fynd.append(dict(typ='tackning',allvar='blockerande',grund='metodval',avsnitt=id,
            beskrivning=text,atgard='Komplettera analysen och återskapa dokumentet från aktuellt underlag. Sakgranska på nytt.'))
    for text in (*analyshinder(rb,p,b,analys,datum=granskningsdatum),*analysbrister_filer):lagg('D-ARB',text)
    resultat=resultat or {}
    if any(not isinstance(resultat.get(id),Tjanstresultat) or resultat[id].formatversion!=d.formatversion
           for id,t in tjanster_med_avsnitt(b)):
        lagg('D-ARB','Validerade versionsbundna skrivdelar saknas för en erbjuden tjänst.')
        return fynd
    try:
        expected=bygg_arb_v6(rb,p,b,resultat,historik,analys=analys,modellrapport=modellrapport,formatversion=d.formatversion)
    except RiskanalysFel as exc:
        lagg('D-ARB',str(exc));return fynd
    if d.titel!=expected.titel or d.formatversion!=expected.formatversion or [a.id for a in d.avsnitt]!=[a.id for a in expected.avsnitt]:
        lagg('D-ARB','Dokumentets titel, format eller avsnittsordning avviker från underlaget.')
    actual=d.avsnitt_med_id()
    for a in expected.avsnitt:
        if a.id not in actual or actual[a.id].kontrollsumma()!=a.kontrollsumma():
            lagg(a.id,'Text, tabeller, proveniens eller hänvisningar avviker från den frysta analysen.')
        if any(tab.id.endswith('-utfall') and any('Begränsning:' in c.text for rad in tab.rader for c in rad.celler) for tab in a.tabeller):
            lagg(a.id,'Beräkningen saknar ett fullständigt regelspår.')
    from riskanalys.granskning.analys import mallfynd
    for id,t in tjanster_med_avsnitt(b):
        fynd.extend(mallfynd(resultat[id]))
    fynd.extend(lasta_fynd_v6(rb,p,b,d,expected,gransindex=metodgransindex(rb)))
    from riskanalys.dokument.likhet import likhetsfynd
    fynd.extend({**f,'typ':'bristmonster','regel':'B-04'} for f in likhetsfynd(list(resultat.values())))
    return fynd
