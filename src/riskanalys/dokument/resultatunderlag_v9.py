"""Deterministiskt urval med bevarade originalreferenser, inte nya riskbeslut."""
from collections import defaultdict
from riskanalys.dokument.resultatmodell_v9 import (
    Urvalspost, Presentationsbrist, ResultatunderlagV9, ScenarioradV9, ScenariocellV9,
    kallartefakter, referens, pointerdel, summa,
)


def mekanism(analys, a, hot):
    """Returnerar originalposter och pointers; en avvikelse ersätter sin gemensamma post."""
    if a is None or analys is None:
        return ()
    ti = next(i for i,t in enumerate(analys.tjanster) if t.tjanst == a.tjanst)
    gem = {s.id:(s,f'/gemensamma_scenarier/{i}') for i,s in enumerate(analys.gemensamma_scenarier)}
    lok = {s.id:(s,f'/tjanster/{ti}/scenarier/{i}') for i,s in enumerate(a.scenarier)}
    poster = []
    ersatta = set()
    for app in a.scenariokopplingar:
        if app.tillampning == 'avviker':
            ersatta.add(app.scenario)
            if app.lokal_scenario in lok:
                poster.append(lok[app.lokal_scenario])
        elif app.scenario in gem:
            poster.append(gem[app.scenario])
    poster.extend(v for id,v in lok.items() if id not in ersatta)
    unika = {ptr:(s,ptr) for s,ptr in poster if hot in s.hot}
    return tuple(unika.values())


def bygg_resultatunderlag(rb, profil, bedomning, resultat, historik, *, analys, analysdokument):
    k = kallartefakter(rb,profil,bedomning,resultat,historik,analys,analysdokument)
    ref = lambda a,p='': referens(k,a,p)
    poster, brister = [], []
    analyser = {a.tjanst:(i,a) for i,a in enumerate(analys.tjanster)} if analys else {}
    grupper = defaultdict(dict)
    def lagg(id, skal, refs, *, tjanst=None, hot=(), dimension=None, riskled=None, hantering='sammanfattas'):
        p = Urvalspost(id=id,tjanst=tjanst,hot=hot,dimension=dimension,riskled=riskled,
                      hantering=hantering,skal=tuple(skal),kallor=tuple(refs))
        poster.append(p)
        return p.id
    erbjudna = [(i,t) for i,t in enumerate(bedomning.tjanster) if t.erbjuds]
    for bi,t in erbjudna:
        ai,a = analyser.get(t.tjanst,(None,None))
        from riskanalys.analys.provning import ej_godtagna_sankningar
        sankningar=ej_godtagna_sankningar(rb,profil,analys,a,t) if a else ()
        for si,s in enumerate(t.scenarier):
            refs = (ref('bedomning',f'/tjanster/{bi}/scenarier/{si}'),)
            ursprung = mekanism(analys,a,s.hot)
            mrefs = tuple(ref('analys',ptr) for _,ptr in ursprung)
            # Olika lokal mekanism/relevans/motivering får inte dela förklaringsrad.
            identitet = tuple((x.handelseforlopp,x.relevans,x.motivering) for x,_ in ursprung)
            key = (s.dimension,s.hot,identitet or ('saknad',t.tjanst))
            ids = []
            if s.avgorande:
                ids.append(lagg(f'{t.tjanst}:{s.hot}:{s.dimension}:fore',('avgor_fore',),(*refs,*mrefs),
                                tjanst=t.tjanst,hot=(s.hot,),dimension=s.dimension,riskled='inneboende'))
            if s.dimension == 'pt' and s.kvarstaende is not None and s.kvarstaende == t.kvarstaende:
                ids.append(lagg(f'{t.tjanst}:{s.hot}:{s.dimension}:efter',('avgor_efter',),(*refs,*mrefs),
                                tjanst=t.tjanst,hot=(s.hot,),dimension=s.dimension,riskled='kvarstaende'))
            if any(b.scenario==s for b in sankningar):
                ids.append(lagg(f'{t.tjanst}:{s.hot}:{s.dimension}:ej_godtagen',('avvikelse',),
                    (*refs,ref('analys',f'/tjanster/{ai}'),ref('analys','/belagg'),ref('profil'),ref('regelbas')),
                    tjanst=t.tjanst,hot=(s.hot,),dimension=s.dimension,riskled='kvarstaende'))
            grupper[key][t.tjanst] = (s,tuple(ids),refs,mrefs)
        if a is None:
            brister.append(Presentationsbrist(kod='saknad_analys',avsnitt='D-ARB.R5',
                beskrivning=f'{t.tjanst}: lokal analys saknas.',kallor=(ref('bedomning',f'/tjanster/{bi}'),)))
            continue
        for falt in ('pt_motivering','tf_motivering'):
            from riskanalys.analys.provning import _saktext
            if not _saktext(getattr(a,falt)):
                brister.append(Presentationsbrist(kod='saknad_'+falt,avsnitt='D-ARB.R5',
                    beskrivning=f'{t.tjanst}: komplettera {falt}.',kallor=(ref('analys',f'/tjanster/{ai}/{falt}'),)))
        for n,p in enumerate(a.sarbarhetsprovningar):
            sk = ('ej_relevant',) if p.relevans=='ej_relevant' else ('egen_sarbarhet',) if not p.sarbarheter else ('avvikelse',)
            if p.relevans=='okant':sk += ('osakerhet',)
            lagg(f'{t.tjanst}:lokal:{p.id}',sk,(ref('analys',f'/tjanster/{ai}/sarbarhetsprovningar/{n}'),),
                 tjanst=t.tjanst,hantering='hanvisas' if sk==('ej_relevant',) else 'sammanfattas')
        for falt,skal in (('rutinatgarder','atgard'),('tackningsprovningar','egen_sarbarhet'),('gap','oppet_gap')):
            for n,p in enumerate(getattr(a,falt)):
                lagg(f'{t.tjanst}:{falt}:{n}',(skal,),(ref('analys',f'/tjanster/{ai}/{falt}/{n}'),),tjanst=t.tjanst,
                     hantering='hanvisas' if falt=='gap' and p.status=='atgardat' else 'sammanfattas')
        for n,p in enumerate(a.sarbarhetstillampningar):
            if p.stallningstagande != 'galler':
                lagg(f'{t.tjanst}:app:{n}',('osakerhet',) if p.stallningstagande=='otillrackligt' else ('avvikelse',),
                     (ref('analys',f'/tjanster/{ai}/sarbarhetstillampningar/{n}'),),tjanst=t.tjanst)
        from riskanalys.analys.riktning import harled_riktningar
        d9 = [r for r in harled_riktningar(rb,profil,analys,t) if r.riktning in
              ('under_troskel','villkor_ej_uppfyllt','ersatt_av_faktor')]
        if d9:
            lagg(t.tjanst+':d9',('metoduppfoljning',),(ref('analys',f'/tjanster/{ai}'),ref('profil'),ref('regelbas')),
                 tjanst=t.tjanst,hantering='hanvisas')
    if analys:
        for n,p in enumerate(analys.gemensamma_sarbarhetsprovningar):
            sk = ('ej_relevant',) if p.status=='bekraftad' and p.relevans=='ej_relevant' else (
                ('egen_sarbarhet',) if not p.sarbarheter else ('avvikelse',))
            if p.status!='bekraftad' or p.relevans=='okant':sk += ('osakerhet',)
            lagg('gemensam:'+p.id,sk,(ref('analys',f'/gemensamma_sarbarhetsprovningar/{n}'),),
                 hot=p.hot,hantering='hanvisas' if sk==('ej_relevant',) else 'sammanfattas')
        for n,p in enumerate(analys.gemensamma_verksamhetsposter):
            lagg('verksamhet:'+p.id,('erfarenhet',) if p.slag=='erfarenhet' else ('avvikelse',),
                 (ref('analys',f'/gemensamma_verksamhetsposter/{n}'),))
    if not any('erfarenhet' in p.skal for p in poster):
        lagg('egen-erfarenhet',('erfarenhet',),(ref('bedomning'),))
    matris = [];nummer={'R4':0,'R5':0}
    for (dim,hot,identitet),cells in sorted(grupper.items(), key=lambda x:(x[0][0]!='pt',list(grupper).index(x[0]))):
        if not any(c[1] for c in cells.values()):continue
        mrefs = tuple(dict.fromkeys(r for c in cells.values() for r in c[3]))
        c = tuple(ScenariocellV9(tjanst=t.tjanst,scenario=cells[t.tjanst][0] if t.tjanst in cells else None,
                  status='beraknad' if t.tjanst in cells else 'saknas',
                  medlemmar=cells[t.tjanst][1] if t.tjanst in cells else (),
                  kallor=cells[t.tjanst][2] if t.tjanst in cells else (ref('bedomning',f'/tjanster/{bi}/scenarier'),))
                  for bi,t in erbjudna)
        del_='R4' if len(cells)>1 else 'R5';nummer[del_]+=1
        matris.append(ScenarioradV9(id=f'{del_}-{nummer[del_]}',hot=hot,dimension=dim,mekanismkallor=mrefs,celler=c))
    return ResultatunderlagV9(poster=tuple(poster),brister=tuple(brister),matris=tuple(matris),
                             kallsummor=tuple((a,summa(v)) for a,v in k.items()))
