"""Uttryckligt syntetiska bekräftelser; aldrig sakkunnig- eller driftbevis."""
from riskanalys.analys import modeller as m, provning as p


def bekraftat_utkast(paket,rb):
    """Pröva syntetiskt avgränsade uppdrag, med gemensamma samma-val efter visning."""
    belagg=tuple(b.id for b in paket.belagg)
    gem=tuple(s.model_copy(update={'relevans':'ej_relevant','motivering':'Syntetiskt belagt avgränsat mandat.',
        'belagg':belagg[:1]}) for s in paket.gemensamma_scenarier)
    paket=paket.model_copy(update={'gemensamma_scenarier':gem})
    tjanster=[]
    for t in paket.tjanster:
        lok=tuple(s.model_copy(update={'relevans':'ej_relevant','motivering':'Syntetiskt prövat avgränsat mandat.',
            'belagg':belagg[:1]}) for s in t.scenarier)
        # Test fixture matches the synthetic catalog's shared scenarios to each service's catalog hot union.
        # Caller passes all shared scenarios only for a common synthetic catalog with those same eight threats.
        kop=tuple(m.Scenariokoppling(scenario=s.id,tillampning='samma',scenariosumma=p.scenariosumma(s),bekraftad=True) for s in gem if set(s.hot)<=set(rb.tjanster[t.tjanst].hot))
        scenarios=tuple(s.id for s in (*lok,*gem))
        sar=tuple(s.model_copy(update={'relevans':'ej_relevant','motivering':'Prövat även vid falskt katalogvillkor.',
            'belagg':belagg[:1]}) for s in t.sarbarhetsprovningar)
        block=tuple(x.model_copy(update={'aktivering':'aktiv' if x.nummer in p.ALLTID or x.nummer==15 else 'ej_tillamplig',
            'motivering':'Syntetiskt explicit avgränsad relevans.'}) for x in t.block)
        t=t.model_copy(update=dict(forfattare='Syntetisk Ada',block=block,scenarier=lok,scenariokopplingar=kop,
            sarbarhetsprovningar=sar,exponeringsbelagg=t.exponeringsbelagg or belagg[:1],
            delningsmotivering='Arbetsmomenten har samma insyn och mandat i provet.',
            betalningsinsyn=m.Betalningsinsyn(status='ej_tillamplig',motivering='Inga betalningsunderlag omfattas av det syntetiska mandatet.'),
            uppdragsprovning=m.Uppdragsprovning(status='hanterbart',kompetens_och_insyn='Belagd syntetisk kompetens.',
                motivering='Avgränsat uppdrag utan oklara befogenheter.',belagg=belagg[:1]),
            samverkan='Kundmix och mandat har prövats tillsammans; inga nya numeriska utfall.',
            erfarenhetsprovning='Noll rapporter bevisar inte frånvaro av hot; tjänstekopplingen har prövats.',
            erfarenhetsbelagg=belagg[:1],pt_motivering='PT bedöms mot separat belagt mandat.',
            tf_motivering='TF prövas separat även med lagligt ursprung.',
            sektorsjamforelse='Sektorsbildens jämförbarhet är prövad med redovisade begränsningar.',
            sanktioner='Ingen belagd sanktionsanknytning i provets avgränsade kundmix.',
            slutsats='Bevara mandatets avgränsning och följ upp nya arbetsmoment. Kundkännedom, övervakning och utbildning anpassas efter tjänstens scenarier.',
            rutinatgarder=(m.Rutinatgard(id=t.tjanst+':rutin',scenarier=scenarios[:1],atgard='Dokumentera oförändrad uppdragsavgränsning.',
                utlosare_eller_frekvens='Vid ändrat uppdrag.'),)))
        tjanster.append(t)
    paket=paket.model_copy(update={'tjanster':tuple(tjanster)})
    return paket.model_copy(update={'tjanster':tuple(t.model_copy(update={'block':tuple(
        b.model_copy(update={'bekraftad_summa':p.blocksumma(paket,t.tjanst,b.nummer)}) if b.aktivering=='aktiv' else b
        for b in t.block)}) for t in paket.tjanster)})
