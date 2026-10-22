"""Härledda upplysningar och brister per hot och dimension, ingen alternativ motor."""
from dataclasses import dataclass
from typing import Literal
from riskanalys.bedomning.motor import _valda_sarbarheter, _OKAND
from riskanalys.bedomning.erfarenheter import belagd_uppgift
from riskanalys.profil.omfattning import kompatibilitetsvy
from riskanalys.regelverk.modeller import hot_dimensioner
from riskanalys.regelverk.villkor import tolka_villkor, utvardera, falt_i, Sanning, Jamforelse
from riskanalys.analys.gemensam import tillampning_aktuell

@dataclass(frozen=True)
class Avvikelserad:
    post: str
    sarbarhet: str | None
    hot: str | None
    dimension: Literal['pt','tf']
    riktning: Literal['i_linje','lagre','under_troskel','villkor_ej_uppfyllt','ersatt_av_faktor','tackt_av_scenario','mojlig_underskattning','oklar']
    kalla: Literal['harledd','manuell']
    motivering: str
    regelspar: tuple[str,...]=()
    profilfalt: tuple[str,...]=()
    ersatt_av: str | None=None


def motorvarden(rb,profil):
    profil=kompatibilitetsvy(profil,rb)
    varden=profil.faltvarden()
    for id in rb.falt:
        if id.startswith('P-RISK.') and not belagd_uppgift(rb,profil,id):
            varden[id]=_OKAND
    return varden


def harled_riktningar(rb,profil,paket,tjanst):
    if paket.schemaversion!=2:
        return ()
    a=next((a for a in paket.tjanster if a.tjanst==tjanst.tjanst),None)
    if a is None:return ()
    varden=motorvarden(rb,profil);kat=rb.tjanster[tjanst.tjanst]
    valda,_=_valda_sarbarheter(rb,kat,varden)
    resultat=[]
    poster={p.id:p for p in paket.gemensamma_sarbarhetsprovningar}
    for app in a.sarbarhetstillampningar:
        p=poster.get(app.post)
        if not tillampning_aktuell(p,app) or p.relevans!='relevant':continue
        for id in p.sarbarheter:
            s=rb.sarbarheter.get(id)
            if s is None:continue  # referensbrist prövas separat
            villkor=tolka_villkor(s.villkor,rb.faltdefinitioner())
            utfall=utvardera(villkor,varden)
            for scenario in tjanst.scenarier:
                h,dim=scenario.hot,scenario.dimension
                if h not in p.hot or (p.dimension!='bada' and p.dimension!=dim):continue
                kopplad=id in kat.sarbarheter and h in s.hot and s.galler in ({'penningtvatt','bada'} if dim=='pt' else {'terrorfinansiering','bada'})
                explicit=any((x.hot,x.dimension)==(h,dim) for x in app.hotkopplingar)
                if not kopplad and not explicit:continue
                riktning='i_linje';text='Faktorn och tillämpningen följer scenariot.';kalla='harledd';ersatt=None
                if p.status!='bekraftad' or app.stallningstagande=='otillrackligt' or utfall.sanning is Sanning.OKANT:
                    riktning='oklar';text='Underlaget är okänt eller ett obekräftat antagande; det är inte under tröskeln.'
                elif explicit and not kopplad:
                    riktning='mojlig_underskattning';text='Uttryckligt påstådd hot-/dimensionskoppling saknas i katalogen.'
                elif app.stallningstagande=='galler_annorlunda':
                    val=app.riktningsval
                    riktning=val.riktning if val and val.motivering.strip() and val.belagg else 'oklar'
                    text=val.motivering if val else 'Klargör riktningen och sakgranska avvikelsen.';kalla='manuell'
                elif app.stallningstagande=='beror_inte':
                    if id in scenario.sarbarheter:
                        riktning='lagre' if s.effekt.sannolikhet>0 else 'oklar'
                        text='Motorns högre nivå och åtgärdsgrund gäller tills metodbeslut.'
                elif utfall.sanning is Sanning.FALSKT:
                    troskel=isinstance(villkor,Jamforelse) and villkor.op in ('>=','>') and isinstance(villkor.varde,(int,float)) and not isinstance(villkor.varde,bool)
                    riktning='under_troskel' if troskel else 'villkor_ej_uppfyllt'
                    text='Motorn har prövat ett känt villkor som falskt; upplysning för metoduppföljning D9 C.'
                elif id not in scenario.sarbarheter:
                    ersatt=next((x.id for x in valda if x.id in scenario.sarbarheter and id in x.ersatter),None)
                    riktning='ersatt_av_faktor' if ersatt else 'oklar'
                    text='Faktorn ersätts inom samma scenario.' if ersatt else 'Frånvaro i faktorlistan styrker inte ett falskt villkor.'
                resultat.append(Avvikelserad(p.id,id,h,dim,riktning,kalla,text,scenario.regelspar,tuple(sorted(falt_i(villkor))),ersatt))
        for x in app.hotkopplingar:
            if not any(s.hot==x.hot and s.dimension==x.dimension for s in tjanst.scenarier):
                resultat.append(Avvikelserad(p.id,None,x.hot,x.dimension,'mojlig_underskattning','harledd','Uttrycklig hotkoppling saknar motorscenario.'))
    from riskanalys.analys.provning_v2 import egna_ansprak, tackningsbrister
    brister=tackningsbrister(rb,paket,tjanst)
    for ursprung,id,hot,dim in egna_ansprak(rb,paket,tjanst):
        prefix=f'{tjanst.tjanst}: täckningsprövning {id}/{hot}/{dim}/'
        prov=any((p.ursprung,p.post,p.hot,p.dimension)==(ursprung,id,hot,dim) for p in a.tackningsprovningar)
        tackt=prov and not any(x.startswith(prefix) for x in brister)
        resultat.append(Avvikelserad(id,None,hot,dim,'tackt_av_scenario' if tackt else 'mojlig_underskattning','harledd',
            'Egen sårbarhet täcks genom uttrycklig scenarioprövning.' if tackt else 'Egen sårbarhet saknar giltig uttrycklig täckning.'))
    return tuple(resultat)
