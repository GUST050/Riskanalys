"""Syntetisk schema-2-fixtur; gamla rapportläsprov ändras inte."""
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from riskanalys.analys.modeller import Analyspaket
from riskanalys.analys.gemensam import forifyll_gemensamt
from riskanalys.bedomning.modeller import Bedomning
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas
from tester.fixturer.rapportlasprov import bygg_rapportlasprov

@dataclass(frozen=True)
class GemensamtFall:
    rb: Regelbas
    profil: Profil
    bedomning: Bedomning
    paket: Analyspaket
    datum: date

def bygg_gemensamt_fall(rb: Regelbas, rot: Path, fall: str='fyra_tjanster', *, bevara_original: bool=False) -> GemensamtFall:
    f=bygg_rapportlasprov(rb,rot,fall)
    if bevara_original:
        from riskanalys.analys.overforing import foresla_overforing
        paket=foresla_overforing(rb,f.analys)
    else:paket=forifyll_gemensamt(rb,f.analys)
    return GemensamtFall(rb,f.profil,f.bedomning,paket,f.profil.byra.datum)

def bygg_direkt_gemensamt_fall(rb: Regelbas, rot: Path, namn: str='fyra_tjanster') -> GemensamtFall:
    """Riktig schema-2-start och publika sparhandlingar med frysta syntetiska svar.

    Rapportläsprovens avsiktliga sakluckor bevaras. En nekad tjänstegenomgång
    loggas som nekad, aldrig som en lyckad bekräftelse.
    """
    import json
    from riskanalys.analys import modeller as m,lagring as l
    from riskanalys.analys.tjanst import Analystjanst
    from riskanalys.analys.provning import registersumma
    from riskanalys.analys.engangssvar import visade_celler
    from riskanalys.profil.lagring import spara_profil
    from riskanalys.bedomning.korning import kor_bedomning
    from riskanalys.dokument.skrivning import kor_skrivning
    from riskanalys.dokument.leverantor import Testleverantor
    from riskanalys.dokument.underlag import tjanster_med_avsnitt
    from tester.fixturer.skrivsvar_v7 import godkant_svar_v7
    from riskanalys.fel import RiskanalysFel
    f=bygg_rapportlasprov(rb,rot,namn)
    # JSON skiljer inte ISO-datum från text i Uppgifts värdeunion.
    # Återställ datumtypen enligt fältkatalogen; det kanoniska JSON-värdet är samma.
    from dataclasses import replace
    upp=dict(f.profil.uppgifter)
    for id,u in upp.items():
        if id in rb.falt and rb.falt[id].typ=='datum' and isinstance(u.varde,str):
            upp[id]=u.model_copy(update={'varde':date.fromisoformat(u.varde)})
    f=replace(f,profil=f.profil.model_copy(update={'uppgifter':upp}))
    spara_profil(f.byramapp,f.profil)
    kor_bedomning(f.byramapp,rb)
    kor_skrivning(f.byramapp,rb,Testleverantor([godkant_svar_v7(rb,f.profil,t,id)
        for id,t in tjanster_med_avsnitt(f.bedomning)]),effort='medium')
    at=Analystjanst(f.byramapp,rb);at.starta('',schema=2)
    def paket():return l.las_analys(f.byramapp)
    def rev():return registersumma(paket())
    logg=['fryst_profil','bedomning','skrivutkast','schema2_start'];p=paket();bas=f.analys.tjanster[0]
    for g in p.gemensamma_sarbarhetsprovningar:
        svar=next(s for s in bas.sarbarhetsprovningar if s.omrade==g.omrade)
        refs=tuple(dict.fromkeys(b for a in f.analys.tjanster for s in a.sarbarhetsprovningar if s.omrade==g.omrade for b in s.belagg))
        post=g.model_copy(update={'relevans':svar.relevans,'beskrivning':svar.motivering,
            'motivering':'Källbelagt gemensamt förhållande; betydelsen prövas per tjänst.','belagg':refs,'status':'bekraftad'})
        at.spara_gemensam_sarbarhet(post,rev(),'Syntetisk gemensam författare');logg.append('gemensamt_svar')
    for g in p.gemensamma_verksamhetsposter:
        text={'leverantorer':bas.leverantorsmotivering,'erfarenhet':bas.erfarenhetsprovning,'sanktionsanknytning':bas.sanktioner}[g.slag]
        if g.slag=='erfarenhet':
            text='\n'.join(a.tjanst+': '+a.erfarenhetsprovning for a in f.analys.tjanster)
        refs=tuple(dict.fromkeys(b for a in f.analys.tjanster for b in (a.erfarenhetsbelagg if g.slag=='erfarenhet' else a.sarbarhetsprovningar[0].belagg)))
        post=g.model_copy(update={'text':text,'belagg':refs,
            'leverantorer':bas.leverantorer if g.slag=='leverantorer' else (),'status':'bekraftad'})
        at.spara_gemensam_verksamhet(post,rev(),'Syntetisk gemensam författare');logg.append('gemensamt_svar')
    # Frysta lokala svar är inmatningsdata; inga ifyllda schema-1-paket konverteras.
    p=paket();ts=[]
    for a in p.tjanster:
        lokal=next(t for t in f.analys.tjanster if t.tjanst==a.tjanst)
        raw=lokal.model_dump(mode='json')
        raw.update(sarbarhetsprovningar=[s.model_dump(mode='json') for s in lokal.sarbarhetsprovningar if s.omrade=='tjanst'],
            leverantorsmotivering='',leverantorer=[],erfarenhetsprovning='',erfarenhetsbelagg=[],sanktioner=[],
            sarbarhetstillampningar=[x.model_dump(mode='json') for x in a.sarbarhetstillampningar],
            verksamhetstillampningar=[x.model_dump(mode='json') for x in a.verksamhetstillampningar])
        raw['sanktioner']=''
        ts.append(m.Tjansteanalys.model_validate(raw))
    p=p.model_copy(update={'tjanster':tuple(ts),'belagg':f.analys.belagg,
        'gemensamma_scenarier':f.analys.gemensamma_scenarier,'beslut':()})
    fil=rot/'syntetiska-lokalsvar.yaml'
    import yaml
    fil.write_text(yaml.safe_dump(p.model_dump(mode='json'),allow_unicode=True))
    at.importera_svar(fil,'Syntetisk lokal författare',rev());logg.append('lokal_svarimport')
    p=paket();ids=tuple(a.tjanst for a in p.tjanster)
    at.bekrafta_byraunderlag(ids,visade_celler(p,ids),rev(),'Syntetisk prövare');logg.append('gemensam_bekraftelse')
    hinder={}
    for id in ids:
        try:at.bekrafta_tjansteunderlag(id,rev(),'Syntetisk prövare')
        except RiskanalysFel as exc:hinder[id]=str(exc);logg.append('tjanstegenomgang_nekad')
        else:logg.append('tjanstegenomgang')
    from riskanalys.analys.provning_v2 import egna_ansprak,kravda_riskled
    p=paket();krav=sum(len(kravda_riskled(t,h,d)) for t in f.bedomning.tjanster if t.erbjuds
        for _,_,h,d in egna_ansprak(rb,p,t))
    kategorier=('fryst_profil','bedomning','skrivutkast','schema2_start','gemensamt_svar','lokal_svarimport','gemensam_bekraftelse','lokal_avvikelse','scenarioval','blockbekraftelse','tjanstegenomgang','tjanstegenomgang_nekad','tackningsprovning','analysbeslut','sakgranskning')
    data={'handlingar':logg,'rakning':{k:logg.count(k) for k in kategorier},'omfattning':'Fryst syntetisk profil; tidigare intagsarbete mäts inte. Lyckade och nekade handlingar skiljs åt.','hinder':hinder,'tackningsprovningar_kravda':krav,
          'tackningsprovningar_utforda':sum(len(a.tackningsprovningar) for a in p.tjanster),
          'gemensamma_svar':len(p.gemensamma_sarbarhetsprovningar)+len(p.gemensamma_verksamhetsposter),
          'lokala_gemensamma_kopior':sum(sum(s.omrade!='tjanst' for s in a.sarbarhetsprovningar)+bool(a.leverantorsmotivering)+bool(a.erfarenhetsprovning)+bool(a.sanktioner) for a in p.tjanster)}
    (rot/'engangssvar-handlingar.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    return GemensamtFall(rb,f.profil,f.bedomning,p,f.profil.byra.datum)
