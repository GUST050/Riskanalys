"""Bekräfta ett svar och ompröva tidigare belägg vid faktiska ändringar."""
from datetime import date
from riskanalys.fel import RiskanalysFel
from riskanalys.intag.modeller import IntagSvar
from riskanalys.intag.verksamhetsval import erbjuds_aktuellt, verksamhetsval
from riskanalys.intag.fordelning import aktiverad, faltkoppling, omprova, svarsbrist, underlagsbindning
from riskanalys.profil.hantering import bekrafta
from riskanalys.profil.modeller import Profil, Uppgift
from riskanalys.profil.omfattning import aktivt, harled_andelar
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.tillsyn import tillsynsomrade


def besvara(rb: Regelbas, profil: Profil, svar: IntagSvar) -> Profil:
    from riskanalys.profil.text import kontrollera_text
    kontrollera_text(svar.text, svar.kalla, svar.roll, svar.motivering)
    f = rb.falt.get(svar.falt)
    if not f or not f.intag or f.alias_for or f.basfalt:
        raise RiskanalysFel('Välj en registrerad intagsfråga; andelar beräknas från antal och bas.')
    val = verksamhetsval(rb, f.id)
    if val and not erbjuds_aktuellt(profil, val[0]):
        raise RiskanalysFel('Frågan är inte tillämplig enligt grundsvaren. Bekräfta först att tjänsten erbjuds.')
    if (faltkoppling(rb, f.id) and not aktiverad(rb, profil, f.id)) or not aktivt(f, profil, rb):
        raise RiskanalysFel('Frågan är inte tillämplig enligt grundsvaren. Ändra dem först.')
    if svar.datum > date.today():
        raise RiskanalysFel('Bekräftelsedatum får inte ligga i framtiden.')
    if svar.status == 'ej_tillämplig':
        raise RiskanalysFel('En aktiv fråga kan inte väljas bort. Svara nej/0 om det stämmer, eller välj Vet inte. Följdfrågor döljs av grundsvaren.')
    if svar.status == 'okänt':
        if not svar.motivering.strip():
            raise RiskanalysFel('Beskriv hur eller när den okända uppgiften ska kontrolleras.')
        tidigare = profil.uppgifter.get(f.id, Uppgift())
        p = profil.model_copy(update={'uppgifter': {**profil.uppgifter, f.id: tidigare.model_copy(
            update={'status': 'föreslagen', 'motivering': svar.motivering.strip(), 'datum': tidigare.datum or svar.datum})}})
    else:
        if not svar.roll.strip():
            raise RiskanalysFel('Ange vem eller vilken funktion som bekräftar uppgiften.')
        oms = profil.uppgifter.get('P-VERK.omsattning')
        if (f.id.startswith(('P-KUND.', 'P-TJ.')) and svar.period and oms
                and profil.ar_bekraftad('P-VERK.omsattning')
                and oms.kalla.startswith('Bolagsverket HVD;') and svar.period != oms.period):
            raise RiskanalysFel('Statistikperioden skiljer sig från den godkända årsredovisningen. Använd samma period eller uppdatera omsättningen med underlag för den nya perioden först.')
        p = bekrafta(profil, rb, f.id, svar.text, svar.kalla, svar.roll, svar.datum, svar.period)
    if faltkoppling(rb, f.id) and svar.status == 'bekräftad':
        hinder = svarsbrist(rb, p, f.id)
        if hinder:
            raise RiskanalysFel(hinder)
        u = p.uppgifter[f.id].model_copy(update={'underlagsbindning': underlagsbindning(rb, p, f.id)})
        p = p.model_copy(update={'uppgifter': {**p.uppgifter, f.id: u}})
    tidigare = profil.uppgifter.get(f.id, Uppgift())
    nytt = p.uppgifter[f.id]
    ny_byra = p.byra
    if f.id in ('P-ORG.sateslan','P-ORG.utlandsk_filial') and all(p.ar_bekraftad(k) for k in ('P-ORG.sateslan','P-ORG.utlandsk_filial')):
        lan=p.uppgifter['P-ORG.sateslan'].varde
        filial=p.uppgifter['P-ORG.utlandsk_filial'].varde
        ny_byra=p.byra.model_copy(update={'lan':'Stockholm' if filial else lan,'regelpaket':tillsynsomrade(lan,filial)})
    andring = (tidigare.varde, tidigare.period, tidigare.status) != (nytt.varde, nytt.period, nytt.status) or ny_byra != p.byra
    if andring:
        andrade = {f.id}
        while True:
            beroende = {k for k,d in rb.falt.items() if d.intag and set(d.intag.beroenden) & andrade} - andrade
            if not beroende:break
            andrade |= beroende
        if f.id in ('P-ORG.sateslan','P-ORG.utlandsk_filial'):
            andrade |= {k for k in p.uppgifter if k not in ('P-ORG.sateslan','P-ORG.utlandsk_filial','P-ORG.namn')}
        uppgifter = dict(p.uppgifter)
        for k in andrade - {f.id}:
            u = uppgifter.get(k,Uppgift())
            if u.status in ('bekräftad','föreslagen','ej_tillämplig'):
                uppgifter[k] = u.model_copy(update={'inaktuell': True})
        p = p.model_copy(update={'uppgifter':uppgifter})
    p=p.model_copy(update={'byra':ny_byra})
    # Äldre alias behålls som historiska belägg, men får inte konkurrera med det rättade grundsvaret.
    uppgifter = dict(p.uppgifter)
    for alias in rb.falt.values():
        if alias.alias_for == f.id and uppgifter.get(alias.id, Uppgift()).status == 'bekräftad':
            uppgifter[alias.id] = uppgifter[alias.id].model_copy(update={'status':'föreslagen','inaktuell':True})
    p = p.model_copy(update={'uppgifter':uppgifter})
    p = omprova(rb, p)
    from riskanalys.intag.kvalitet import kvalitetsbrister
    hinder = [h for h in kvalitetsbrister(rb,p) if h.startswith(f.id + ":")]
    if hinder:raise RiskanalysFel(" ".join(hinder))
    return harled_andelar(p, rb, andrade_falt=frozenset({f.id}))
