"""Strikt adapter för schema 2. Endast typade modeller och visade referenser."""
from typing import get_origin,get_args
from riskanalys.analys import modeller as m
from riskanalys.fel import RiskanalysFel
from riskanalys.intag.analysformular import grundtyp,faltlista,normalisera_urval

META={'csrf','revision','forfattare'}


def ids(text):
    v=tuple(s.strip() for s in text.split(',') if s.strip())
    if len(set(v))!=len(v):raise RiskanalysFel('Ange varje referens endast en gång.')
    return v


def modellfalt(modell,data,prefix='',utan=()):
    raw={};tillatna=set()
    for key,f in modell.model_fields.items():
        if key in utan:continue
        n=prefix+key;tillatna.add(n)
        if n in data:
            raw[key]=ids(data[n]) if get_origin(grundtyp(f.annotation)) is tuple else data[n] or None if type(None) in get_args(f.annotation) else data[n]
    return raw,tillatna


def katalogval(rb,paket):
    return {
        'sarbarheter':[(id,s.namn) for id,s in rb.sarbarheter.items()],
        'hot':[(id,h.namn) for id,h in rb.hot.items()],
        'belagg':[(b.id,'Belägg '+str(i+1)+' ('+b.id+')') for i,b in enumerate(paket.belagg)],
    }


def las_post(data,paket,rb=None):
    slag=data.get('typ')
    modell=m.GemensamSarbarhetsprovning if slag=='sarbarhet' else m.GemensamVerksamhetspost if slag=='verksamhet' else None
    if modell is None:raise RiskanalysFel('Välj gemensam sårbarhet eller verksamhetspost.')
    if rb is not None:data=normalisera_urval(data,faltlista(modell),katalogval(rb,paket))
    raw,tillatna=modellfalt(modell,data,utan=('leverantorer',))
    if modell is m.GemensamVerksamhetspost:
        poster=paket.gemensamma_verksamhetsposter
        gammal=next((p for p in poster if p.id==raw.get('id')),None)
        n=len(gammal.leverantorer) if gammal else 0
        leverantorer=[]
        for i in range(n+1):
            prefix=f'leverantorer.{i}.'
            row,keys=modellfalt(m.Leverantorsprovning,data,prefix);tillatna.update(keys)
            if any(v for v in row.values()):leverantorer.append(m.Leverantorsprovning.model_validate(row))
        raw['leverantorer']=tuple(leverantorer)
    if set(data)-(META|{'typ'}|tillatna):raise RiskanalysFel('Formuläret innehåller okända fält.')
    return modell.model_validate(raw)


def las_tillampning(data,rb=None,paket=None):
    if rb is not None:data=normalisera_urval(data,faltlista(m.Sarbarhetstillampning),katalogval(rb,paket))
    ref=m.GemensamReferens(slag=data.get('slag',''),post=data.get('post',''),summa=data.get('postsumma',''))
    modell=m.Sarbarhetstillampning if ref.slag=='sarbarhet' else m.GemensamTillampning
    tillatna=META|{'tjanst','slag','post','postsumma','stallningstagande','motivering','belagg','operation'}
    raw={'post':ref.post,'postsumma':ref.summa,'stallningstagande':data.get('stallningstagande',''),
         'motivering':data.get('motivering',''),'belagg':ids(data.get('belagg',''))}
    if ref.slag=='sarbarhet':
        tillatna|={'hotkopplingar','riktningsval.riktning','riktningsval.motivering','riktningsval.belagg'}
        kopplingar=[]
        for x in ids(data.get('hotkopplingar','')):
            hot,sep,dim=x.partition('/')
            if not sep:raise RiskanalysFel('Ange uttrycklig hotkoppling som hot-ID/pt eller hot-ID/tf.')
            kopplingar.append(m.Hotanknytning(hot=hot,dimension=dim))
        raw['hotkopplingar']=tuple(kopplingar)
        val={key.removeprefix('riktningsval.'):v for key,v in data.items() if key.startswith('riktningsval.')}
        if val:
            val['belagg']=ids(val.get('belagg',''));raw['riktningsval']=m.Riktningsval.model_validate(val)
        elif raw['stallningstagande']=='galler_annorlunda':raw['riktningsval']=m.Riktningsval()
    if set(data)-tillatna:raise RiskanalysFel('Programhärledd riktning får inte skickas in. Kontrollera formulärets fält.')
    return ref,modell.model_validate(raw)


def las_samlad(data,paket):
    from riskanalys.analys.gemensam import postsumma
    valbara=[m.GemensamReferens(slag=slag,post=p.id,summa=postsumma(p)) for slag,poster in
              (('sarbarhet',paket.gemensamma_sarbarhetsprovningar),('verksamhet',paket.gemensamma_verksamhetsposter)) for p in poster]
    tillatna=META|{'tjanst'};valda=[]
    for i,p in enumerate(valbara):
        key=f'val.{i}';hashkey=f'summa.{i}';tillatna|={key,hashkey}
        if key not in data:continue
        if data[key]!=p.slag+'/'+p.post:raise RiskanalysFel('Välj en post ur det visade urvalet.')
        valda.append(p.model_copy(update={'summa':data.get(hashkey,'')}))
    if set(data)-tillatna:raise RiskanalysFel('Urvalet innehåller okända fält.')
    return tuple(valda)


def las_tackning(data,rb=None,paket=None):
    if rb is not None:data=normalisera_urval(data,faltlista(m.Tackningsprovning),katalogval(rb,paket))
    raw,tillatna=modellfalt(m.Tackningsprovning,data)
    if set(data)-(tillatna|META|{'tjanst','operation'}):raise RiskanalysFel('Prövningen innehåller okända fält.')
    if data.get('operation') not in ('visa','spara'):raise RiskanalysFel('Visa eller spara den aktuella prövningen uttryckligen.')
    return m.Tackningsprovning.model_validate(raw)
