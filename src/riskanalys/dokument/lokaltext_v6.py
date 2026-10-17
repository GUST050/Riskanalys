"""Lokala resonemang ersätter v5:s tre borttagna AI-delar."""
from riskanalys.dokument.analystabeller import status, bygg_scenariotabell, bygg_kontrollprovning, bygg_rutinatgarder
from riskanalys.dokument.tjanstavsnitt_v6 import lokaltext

OMRADEN = {'kund': 'Kunder', 'kanal': 'Distributionskanaler', 'geo': 'Geografi', 'verk': 'Egen verksamhet', 'tjanst': 'Tjänstespecifika förhållanden'}


def bygg_lokaltext(a, paket, rb, index):
    poster = []
    def lagg(rubrik, text, refs=(), *, krav=True):
        if text or krav:
            poster.append(lokaltext(rubrik+': '+(text or 'Saknas; komplettera. [VERIFIERA]'), (*refs, 'D-ARB.B1')))
    lagg('Uppdrag och exponering', a.exponering, index.refs('belagg', a.exponeringsbelagg))
    lagg('Arbetsmomentens indelning', a.delningsmotivering)
    for d in a.delanalyser:
        lagg('Delanalys '+(d.rubrik or 'utan rubrik'), d.arbetsmoment_och_befogenheter, (*index.refs('delanalys', (a.tjanst+':'+d.id,)), *index.refs('belagg', d.belagg)))
    insyn = a.betalningsinsyn
    lagg('Betalningsinsyn ('+status(insyn.status)+')', ' '.join(x for x in (
        insyn.motivering, 'Synliga flöden: '+insyn.synliga_floden if insyn.synliga_floden else '',
        'Insynsluckor: '+insyn.insynsluckor if insyn.insynsluckor else '',
        'Avsändare/mottagare: '+insyn.avsandare_och_mottagare if insyn.avsandare_och_mottagare else '',
        'Tillförlitlighet: '+insyn.underlagens_tillforlitlighet if insyn.underlagens_tillforlitlighet else '') if x), index.refs('belagg', insyn.belagg))
    u = a.uppdragsprovning
    lagg('Uppdragshanterbarhet ('+status(u.status)+')',
        f'{u.kompetens_och_insyn} {u.motivering} Handlingsalternativ: {status(u.handlingsalternativ)} ({status(u.beslutsstatus)}).'
        + (f' Ansvar: {u.ansvar}; beslutsdatum {u.datum}.' if u.ansvar or u.datum else ''), index.refs('belagg', u.belagg))
    lagg('Leverantörsprövning', a.leverantorsmotivering, krav=bool(a.leverantorer))
    for v in a.leverantorer:
        lagg('Leverantörens arbete och byråns ansvar', f'{v.omfattning} Leverantörens kontroller: {v.leverantorens_kontroller} '
            f'Egen verifiering: {v.egen_verifiering} Brister/motstridigheter: {v.brister_och_motstridigheter} Ansvar: {v.ansvar}.', index.refs('belagg', v.belagg))
    for s in a.sarbarhetsprovningar:
        lagg(OMRADEN[s.omrade]+' – '+status(s.relevans), s.motivering,
            (*s.sarbarheter, *index.refs('scenario', s.scenarier), *index.refs('belagg', s.belagg)))
    lagg('Faktorernas samverkan', a.samverkan)
    lagg('Egna rapporterings- och bevakningslärdomar', a.erfarenhetsprovning, index.refs('belagg', a.erfarenhetsbelagg))
    lagg('Motivering av PT-utfallet', a.pt_motivering)
    lagg('Separat TF-prövning', a.tf_motivering)
    lagg('Reduktionsprövning ('+status(a.reduktionsprovning)+')', a.reduktionsmotivering, krav=a.reduktionsprovning!='ej_reduktion')
    lagg('Jämförelse med sektorsbilden', a.sektorsjamforelse)
    lagg('Sanktioner', a.sanktioner, krav=False)
    lagg('Slutsats', a.slutsats)
    for g in a.gap:
        lagg('Lucka eller brist ('+status(g.typ)+', '+status(g.status)+')', f'{g.beskrivning} {g.motivering}'
            + (f' Ansvar: {g.ansvar}; tidsfrist {g.tidsfrist}.' if g.ansvar or g.tidsfrist else ''), index.refs('belagg', g.belagg))
    tabeller = tuple(t for t in (bygg_scenariotabell(a, paket, rb, index), bygg_kontrollprovning(a, rb, index), bygg_rutinatgarder(a, index)) if t)
    return tuple(poster), tabeller
