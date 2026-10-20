"""Syntetisk aktuell M2-analys med verkliga privata kopior och separata attester.

Endast testdata: inget här signerar repots regelbas eller verkliga byråuppgifter.
"""
from datetime import date, timedelta

from riskanalys.analys import lagring as l, modeller as m, provning as p
from riskanalys.analys.utkast import forifyll_analys
from riskanalys.bedomning.korning import las_bedomning
from riskanalys.drift import modellrisk as mr
from riskanalys.lagring.kontrollsumma import for_bytes,for_fil
from riskanalys.profil.lagring import las_profil
from riskanalys.regelverk.modeller import Sakkunnig


def utan_reduktionsansprak(rb,profil):
    """Testbyrån uppger uttryckligt saknad utformning/ej belagt genomförande."""
    upp=dict(profil.uppgifter)
    for c in rb.kontroller.values():
        for falt,varde in ((c.utformning_falt,'saknas'),(c.genomforande_falt,'ej_belagt')):
            if falt in upp:upp[falt]=upp[falt].model_copy(update={'varde':varde})
    return profil.model_copy(update={'uppgifter':upp})


def _modellunderlag(byra,rb,rot,datum):
    rot.mkdir(parents=True,exist_ok=True)
    pdf=rot/'rapport.pdf';pdf.write_bytes(b'%PDF-1.4\nSynthetic technical validation only.\n%%EOF')
    inventarium=mr.modellfilmanifest(rb)
    rapport=mr.Modellvalidering(modellbindning=inventarium.modellbindning,
        modellfiler_kontrollsumma=for_bytes(inventarium.model_dump_json(indent=2).encode()),
        rapport_kontrollsumma=for_fil(pdf),rapportversion='syntetisk-m2-v6',datum=datum,
        tillampningsomrade='Endast syntetiska aktuella M2-kedjor.',fall_och_facit='Syntetiska normal- och negativfall.',
        faktiska_utfall='Tekniskt kedjeprov; ingen juridisk eller verklig driftvalidering.',
        avvikelser='Redovisas i respektive negativt testfall.',begransningar='Inga verkliga kundärenden eller driftobservationer.',
        verkliga_driftobservationer='Inga; endast syntetiskt prov.',m1_beslut='godkant')
    rapport=rapport.model_copy(update={'sakkunnig':Sakkunnig(status='verifierad',av='Syntetisk metodgranskare',datum=datum,
        kontrollsumma=mr.valideringens_innehallssumma(rapport))})
    leverans=mr.exportera_modellvalidering(rot/'leverans',rb,rapport,pdf)
    kopior=l.importera_modellrapport(byra,leverans)
    fil=rot/'modellrutin.txt';fil.write_text('Syntetisk månatlig granskning av felutfall; årsvis omprövning och stopp vid väsentligt fel.')
    namn,hash=l.importera_belagg(byra,fil)
    return mr.Modellriskunderlag(modellansvarig='Syntetisk modellansvarig',modellbindning=rapport.modellbindning,
        rutin=mr.Modellbelagg(fil=namn,kontrollsumma=hash),projektrapport=kopior.projektrapport,
        valideringsrapport=kopior.valideringsrapport,modellfiler=kopior.modellfiler,
        utvarderad=datum,nasta_genomgang=datum+timedelta(days=365),
        feluppfoljning='Syntetisk månatlig felkontroll och årlig omprövning.',fel=(),godkand=True,
        beslutad_av='Syntetisk lokal modellansvarig',beslutsdatum=datum)


def godkann_syntetisk_analys(byra,rb,bedomningsmapp,utkastmapp,rot,datum):
    """Förnya riktig bindning, pröva utvecklade svar och append via gemensam transaktion."""
    from tester.fixturer.analys_hela_kedjan import _tjanst,_bekrafta
    profil=las_profil(byra);b=las_bedomning(bedomningsmapp)
    assert all(not p.faktisk_reduktion(t) for t in b.tjanster if t.erbjuds)
    bindning=l.bygg_bindning(byra,rb,bedomningsmapp,utkastmapp)
    a=forifyll_analys(rb,profil,b,bindning)
    texter={
        'mandat':'Syntetiska uppdragsbrev: mandat, personalens kompetens och ekonomiska underlag för varje faktiskt erbjuden tjänst är dokumenterade. Byrån bedömer handlingar men verkställer inte kundens betalningar.',
        'kontroll':'Syntetisk kartläggning: ingen generisk kontroll har belagt genomförande eller styrkt effekt. Källräckvidden kan inte ersättas av allmän bankavstämning; inga riskreduktioner görs.',
        'bevakning':'Syntetisk bevakningslogg: ofullständiga affärsunderlag har utretts mot avtal och uppdragsbrev. Noll rapporter är inget bevis på frånvaro av hot; varje tjänst prövas.',
        'rutin':'Syntetisk rutin R-AB6 version 1: uppdragsansvarig begär kompletterande ursprungshandlingar när ändamål eller parter är oklara och följer upp innan leverans.',
        'leverantor':'Ingen extern KYC eller utkontraktering ingår enligt de bekräftade syntetiska profiluppgifterna; byrån gör egen prövning.',
    }
    belagg=[]
    rot.mkdir(parents=True,exist_ok=True)
    for id,text in texter.items():
        fil=rot/(id+'.txt');fil.write_text(text)
        namn,hash=l.importera_belagg(byra,fil)
        belagg.append(m.Analysbelagg(id='ab6:'+id,dokument=namn,kontrollsumma=hash,datum=datum))
    gem=tuple(s.model_copy(update={'relevans':'relevant','motivering':
        'Detta hot prövas i kundens ekonomiska underlagskedja och tjänstens mandat; underlagen kan legitimera annat ändamål.',
        'belagg':('ab6:mandat',)}) for s in a.gemensamma_scenarier)
    a=a.model_copy(update={'gemensamma_scenarier':gem,'belagg':(*a.belagg,*belagg),
        'modellrisk':_modellunderlag(byra,rb,rot/'modell',datum)})
    tjanster=[]
    motorresultat={x.tjanst:x for x in b.tjanster}
    for t in a.tjanster:
        # Each service gets only the common threats present in its own catalog.
        egna_gem=tuple(s for s in gem if set(s.hot)<=set(rb.tjanster[t.tjanst].hot))
        t=_tjanst(rb,t,egna_gem,motorresultat[t.tjanst],variation=False)
        t=t.model_copy(update={'leverantorer':(),
            'leverantorsmotivering':'Ingen extern KYC eller utkontraktering enligt den bekräftade profilen.',
            'reduktionsprovning':'ej_reduktion','reduktionsmotivering':'Motorns faktiska utfall har ingen kontrollreduktion.',
            'gap':tuple(g.model_copy(update={'tidsfrist':datum+timedelta(days=30)}) for g in t.gap if g.typ!='metodkonflikt'),
            'block':tuple(x.model_copy(update={'aktivering':'ej_tillamplig' if x.nummer in (5,12) else 'aktiv',
                'motivering':'Ingen extern leverantör används.' if x.nummer==5 else
                    'Ingen faktisk motorreduktion görs.' if x.nummer==12 else x.motivering}) for x in t.block)})
        tjanster.append(t)
    a=_bekrafta(a.model_copy(update={'tjanster':tuple(tjanster)}))
    assert p.analysbrister(rb,profil,b,a)==()
    cas=l.spara_analys(byra,a,forvantad_summa='')
    for t in a.tjanster:
        a=l.las_analys(byra)
        beslut=m.Analysbeslut(tjanst=t.tjanst,revision=a.revision,underlagssumma=p.underlagssumma(a),
            svarssumma=p.svarssumma(a),godkand=True,namn='Syntetisk lokal analysgranskare',roll='FfR',datum=datum)
        cas=l.registrera_analysbeslut(byra,rb,beslut,forvantad_summa=cas,bedomningsmapp=bedomningsmapp,utkastmapp=utkastmapp)
    return cas
