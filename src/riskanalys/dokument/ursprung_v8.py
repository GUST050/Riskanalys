"""Reproducerbar innehållskarta: placeringsidentitet, mall och faktiska ingångar.

Kartan är härledd ur samma frysta ingångar som byggaren. En giltig pointer är
teknisk spårning, inte en automatisk sakattest för den formulerade slutsatsen.
"""
from hashlib import sha256

from riskanalys.dokument.operationskarta_v8 import operationskarta
from riskanalys.dokument.skrivversion import V8
from riskanalys.dokument.underlag import tjanster_med_avsnitt


def _esc(v):
    return str(v).replace('~','~0').replace('/','~1')


def los_pointer(data, pointer):
    for del_ in pointer.split('/')[1:]:
        key=del_.replace('~1','/').replace('~0','~')
        data=data[int(key)] if isinstance(data,list) else data[key]
    return data


def _objektindex(data, stig=''):
    if isinstance(data,dict):
        if isinstance(data.get('id'),str):
            yield data['id'],stig
        for k,v in data.items():
            yield from _objektindex(v,stig+'/'+_esc(k))
    elif isinstance(data,list):
        for n,v in enumerate(data):
            yield from _objektindex(v,stig+'/'+str(n))


def bygg_ursprungskarta(dokument,rb,profil,bedomning,resultat,historik,analys):
    """Alla stycken/celler och statiska rubriker har identitet, även utan faktakälla."""
    if dokument.formatversion!=V8:
        raise ValueError('Ursprungskartan kräver V8.')
    rbindex=dict(_objektindex(rb.model_dump(mode='json')))
    tjindex={t.tjanst:n for n,t in enumerate(bedomning.tjanster)}
    avsnitt_tj={id:t.tjanst for id,t in tjanster_med_avsnitt(bedomning)}
    analysindex={}
    if analys:
        analysindex.update(('ANALYS:belagg:'+b.id,'/belagg/'+str(n)) for n,b in enumerate(analys.belagg))
        analysindex.update(('ANALYS:scenario:'+s.id,'/gemensamma_scenarier/'+str(n)) for n,s in enumerate(analys.gemensamma_scenarier))
        for n,t in enumerate(analys.tjanster):
            analysindex.update(('ANALYS:scenario:'+s.id,f'/tjanster/{n}/scenarier/{m}') for m,s in enumerate(t.scenarier))
            analysindex.update(('ANALYS:delanalys:'+t.tjanst+':'+s.id,f'/tjanster/{n}/delanalyser/{m}') for m,s in enumerate(t.delanalyser))
    operationer=operationskarta(rb,profil,bedomning,resultat,analys)
    from riskanalys.dokument.radata_v8 import fria_analysfalt
    lokala_original={falt.text for falt in fria_analysfalt(analys)}
    # B1:s råfältstabell är själv en explicit exakt-återanvändningsoperation.
    # Endast där får flera identiska originalsvar bindas till samma fulltextplacering.
    b1=dokument.avsnitt_med_id().get('D-ARB.B1')
    if b1 and analys:
        from riskanalys.dokument.arb_v6 import ANALYSBLOCK, DELANALYSER_OCH_ANALYSBLOCK
        blockdel=next((u for u in b1.underrubriker if u.rubrik in (ANALYSBLOCK,DELANALYSER_OCH_ANALYSBLOCK)),None)
        if blockdel:
            n=blockdel.fore_stycke
            # Samma typade ordning som analysbilaga/_analysdelar, inklusive tomma delanalyser.
            for ti,t in enumerate(analys.tjanster):
                for di,d in enumerate(t.delanalyser):
                    operationer[f'D-ARB.B1/stycken/{n}']=(('analys',f'/tjanster/{ti}/delanalyser/{di}/id'),
                        ('analys',f'/tjanster/{ti}/delanalyser/{di}/rubrik'))
                    n+=1
                for bi,b in enumerate(t.block):
                    operationer[f'D-ARB.B1/stycken/{n}']=tuple(('analys',f'/tjanster/{ti}/block/{bi}/{f}')
                        for f in ('nummer','aktivering','motivering','bekraftad_summa'))+(('regelbas',f'/tjanster/{_esc(t.tjanst)}/namn'),)
                    n+=1
    if b1:
        for tab in b1.tabeller:
            if tab.id=='v8-fria-falt':
                for n,r in enumerate(tab.rader):
                    pointer=r.celler[0].text
                    target=r.celler[2].text
                    operationer[target]=(*operationer.get(target,()),('analys',pointer))
                    for m in range(len(r.celler)):
                        operationer[f'D-ARB.B1/tabeller/{tab.id}/rader/{n}/celler/{m}']=(('analys',pointer),)
    karta=[]
    def lagg(placering,text,*,avsnitt=None,post=None,ingangar=(),statisk=False,motor=False,tjanst=None):
        refs=tuple(getattr(post,'referenser',()))
        tjanst_id=tjanst or (avsnitt_tj.get(avsnitt.id) if avsnitt else None)
        kallor=[*ingangar,*operationer.get(placering,())]
        if not statisk:
            for ref in refs:
                for prefix,falt in (('LOKAL-GRUPP:','kombinationsgrupper'),('LOKAL-PLAN:','tjansteplaner')):
                    if ref.startswith(prefix):
                        kallor.extend(('profil',f'/{falt}/{n}') for n,p in enumerate(getattr(profil,falt)) if p.id==ref.removeprefix(prefix))
                if ref in profil.uppgifter:
                    kallor.append(('profil','/uppgifter/'+_esc(ref)))
                if ref in rbindex:
                    kallor.append(('regelbas',rbindex[ref]))
                if ref in analysindex:
                    kallor.append(('analys',analysindex[ref]))
        lokalt_original=(post is not None and getattr(post,'proveniens',None)=='lokal'
            and placering in operationer and text in lokala_original)
        slag='mänsklig analys/beslut' if lokalt_original else 'motor' if motor else 'programmall'
        if post is not None and getattr(post,'proveniens',None)=='ai':
            slag='ai'
            # AI-styckets index kommer från samma byggoperation, inte textsökning.
        if not statisk and motor and tjanst_id in tjindex:
            kallor.append(('bedomning',f'/tjanster/{tjindex[tjanst_id]}'))
        if not statisk and avsnitt:
            if avsnitt.id=='D-ARB.10':
                kallor.append(('historik',''))
            if avsnitt.id=='D-ARB.8':
                kallor.append(('bedomning','/status'))
                if analys:
                    kallor.extend((('analys','/beslut'),('analys','/bindning')))
            if avsnitt.id=='D-ARB.B1' and post and text.startswith('Lokal analysrevision') and analys:
                kallor.append(('analys',''))
            if avsnitt.id=='D-ARB.B1' and 'KRV-LSF-006' in refs:
                kallor.append(('historik',''))
        karta.append({'placering':placering,'leveransdel':avsnitt.leveransdel if avsnitt else 'gemensam',
            'produktionsslag':slag,'mallversion':V8,'textsumma':sha256(text.encode()).hexdigest(),
            'ingangar':[{'kalla':k,'pointer':p} for k,p in dict.fromkeys(kallor)],
            'referenser':list(refs),'transformation':'statisk versionsbunden text' if statisk else
                'validerad AI-text med lokala platshållarvärden' if slag=='ai' else
                'återgivning av sparade motorfält' if motor else 'versionsbunden mall och ordagranna lokala värden'})
    lagg('titel',dokument.titel,ingangar=(('profil','/uppgifter/P-ORG.namn/varde'),) if 'P-ORG.namn' in profil.uppgifter else ())
    for a in dokument.avsnitt:
        rubrik_ing=(('regelbas','/tjanster/'+_esc(avsnitt_tj[a.id])+'/namn'),) if a.id in avsnitt_tj else ()
        lagg(a.id+'/rubrik',a.rubrik,avsnitt=a,ingangar=rubrik_ing,statisk=not rubrik_ing)
        for n,u in enumerate(a.underrubriker):
            lagg(a.id+f'/underrubriker/{n}',u.rubrik,avsnitt=a,statisk=True)
        for n,s in enumerate(a.stycken):
            placering=a.id+f'/stycken/{n}'
            motor=(getattr(s,'proveniens',None)=='regelbas' and any(k=='bedomning' and '/scenarier/' in p
                for k,p in operationer.get(placering,())))
            lagg(placering,s.text,avsnitt=a,post=s,motor=motor)
        for tab in a.tabeller:
            bas=a.id+'/tabeller/'+tab.id
            lagg(bas+'/rubrik',tab.rubrik,avsnitt=a,statisk=True)
            for n,k in enumerate(tab.kolumner):
                lagg(bas+f'/kolumner/{n}',k,avsnitt=a,statisk=True)
            for n,r in enumerate(tab.rader):
                for m,c in enumerate(r.celler):
                    ing=()
                    motor=tab.id.endswith(('-motorscenarier','-motorfaktorer','-faktorregister','-utfall'))
                    # Motortabellerna står i B1; tjänsten anges av tabellens ID.
                    tabelltjanst=next((tab.id.removesuffix(x) for x in ('-motorscenarier','-motorfaktorer',
                        '-faktorregister','-utfall') if tab.id.endswith(x)),None)
                    if tab.id.endswith(('-motorscenarier','-motorfaktorer')):
                        ti=tjindex[tabelltjanst]
                        falt=(('hot','hotniva','sarbarhetsniva','sannolikhet','konsekvens','risk','kvarstaende')
                              if tab.id.endswith('-motorscenarier') else ('hot','sarbarheter','tackande_kontroller'))[m]
                        index = (n,)
                        if tab.id.endswith('-motorfaktorer'):
                            from riskanalys.dokument.nivamotivering_v8 import faktorgrupper
                            t = bedomning.tjanster[ti]
                            grupp = faktorgrupper(t)[n]
                            index = tuple(i for i, scenario in enumerate(t.scenarier) if scenario in grupp)
                        ing=tuple(('bedomning',f'/tjanster/{ti}/scenarier/{i}/{falt}') for i in index)
                    lagg(bas+f'/rader/{n}/celler/{m}',c.text,avsnitt=a,post=c,ingangar=ing,motor=motor,tjanst=tabelltjanst)
    return tuple(karta)
