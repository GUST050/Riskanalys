"""Uttryckligt schema-2-förslag. Gamla svar bevaras; inga attester överförs."""
from collections import defaultdict
from riskanalys.analys import modeller as m
from riskanalys.analys.gemensam import forifyll_gemensamt,postsumma
from riskanalys.analys.provning import summa,effektiva_scenarier
from riskanalys.fel import RiskanalysFel
from riskanalys.regelverk.modeller import hot_dimensioner


def foresla_overforing(rb,paket):
    if paket.schemaversion!=1:raise RiskanalysFel('Analysen är redan i schema 2. Jämför det sparade underlaget.')
    belagg={b.id:b for b in paket.belagg};grupper=defaultdict(list)
    for a in paket.tjanster:
        scenarier,_=effektiva_scenarier(paket,a)
        for s in a.sarbarhetsprovningar:
            if s.omrade=='tjanst':continue
            # Faktiska belägg och alla scenariodata ingår, inte bara lika text.
            semantik={'post':s.model_dump(mode='json',exclude={'id','scenarier'}),
                'belagg':[belagg[id].model_dump(mode='json') if id in belagg else {'saknas':id} for id in s.belagg],
                'scenarier':[scenarier[id].model_dump(mode='json',exclude={'id'}) if id in scenarier else {'saknas':id} for id in s.scenarier]}
            grupper[summa(semantik)].append((a,s,scenarier))
    nytt=forifyll_gemensamt(rb,paket);gem=[];galler={}
    for grupp in grupper.values():
        if len({a.tjanst for a,_,_ in grupp})<2:continue
        a,s,scenarier=grupp[0]
        hot=tuple(sorted({h for id in s.scenarier if id in scenarier for h in scenarier[id].hot}))
        dimensioner={d for h in hot if h in rb.hot for d in hot_dimensioner(rb.hot[h])}
        dimension=next(iter(dimensioner)) if len(dimensioner)==1 else 'bada'
        post=m.GemensamSarbarhetsprovning(id='overfort:'+str(len(gem)+1),omrade=s.omrade,sarbarheter=s.sarbarheter,
            beskrivning=s.motivering,profilfalt=tuple(sorted({f for id in s.belagg if id in belagg for f in belagg[id].profilfalt})),
            hot=hot,dimension=dimension,relevans=s.relevans,
            motivering='Överfört förslag. Jämför ursprungliga svar, relevans, perioder och belägg före bekräftelse.',
            belagg=s.belagg,status='antagande',forfattare=None)
        gem.append(post);galler[post.id]={a.tjanst for a,_,_ in grupp}
    omraden={g.omrade for g in gem}
    gem.extend(g for g in nytt.gemensamma_sarbarhetsprovningar if g.omrade not in omraden)
    verksamhet=[]
    for p in nytt.gemensamma_verksamhetsposter:
        namn={'leverantorer':'leverantorsmotivering','erfarenhet':'erfarenhetsprovning','sanktionsanknytning':'sanktioner'}[p.slag]
        grupper_v=defaultdict(list)
        for a in paket.tjanster:
            text=getattr(a,namn)
            refs=a.erfarenhetsbelagg if p.slag=='erfarenhet' else tuple(dict.fromkeys(b for l in a.leverantorer for b in l.belagg)) if p.slag=='leverantorer' else ()
            leverantorer=a.leverantorer if p.slag=='leverantorer' else ()
            semantik={'text':text,'belagg':[belagg[id].model_dump(mode='json') if id in belagg else {'saknas':id} for id in refs],
                'referenser':refs,'leverantorer':[l.model_dump(mode='json') for l in leverantorer]}
            if text:grupper_v[summa(semantik)].append((a,refs,leverantorer))
        grupp=max(grupper_v.values(),key=len,default=[])
        if len(grupp)==len(paket.tjanster) and grupp:
            a,refs,leverantorer=grupp[0]
            p=p.model_copy(update={'text':getattr(a,namn),'belagg':refs,'leverantorer':leverantorer})
        verksamhet.append(p)
    ts=[]
    for a in paket.tjanster:
        appar=tuple(m.Sarbarhetstillampning(post=p.id,postsumma=postsumma(p),
            stallningstagande='galler' if a.tjanst in galler.get(p.id,{a.tjanst}) else 'otillrackligt') for p in gem)
        ts.append(a.model_copy(update={'sarbarhetstillampningar':appar,
            'verksamhetstillampningar':tuple(m.GemensamTillampning(post=p.id,postsumma=postsumma(p),stallningstagande='galler') for p in verksamhet),
            'tackningsprovningar':(),
            'block':tuple(b.model_copy(update={'bekraftad_summa':None}) for b in a.block),
            'scenariokopplingar':tuple(k.model_copy(update={'bekraftad':False}) for k in a.scenariokopplingar)}))
    return nytt.model_copy(update={'gemensamma_sarbarhetsprovningar':tuple(gem),'gemensamma_verksamhetsposter':tuple(verksamhet),
        'tjanster':tuple(ts),'beslut':(),
        'modellrisk':paket.modellrisk.model_copy(update={'godkand':False}) if paket.modellrisk else None})
