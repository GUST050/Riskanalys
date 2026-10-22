"""Kontrafaktisk referens, samma scenarioregler med antagandet ytterligare +1.

Ändrar aldrig motorutfall eller kontrollantaganden. +1 är ingen beslutad vikt
för den egna sårbarheten; giltig täckning kräver en separat sakprövning.
"""


def referensniva(rb, profil, tjanst, hot, dimension, riskled):
    s=next((s for s in tjanst.scenarier if (s.hot,s.dimension)==(hot,dimension)),None)
    if s is None or tjanst.erbjuds is not True or rb.metod.scenario is None:
        return None
    from riskanalys.regelverk.villkor import tolka_villkor, falt_i
    galler={'penningtvatt','bada'} if dimension=='pt' else {'terrorfinansiering','bada'}
    falt=set().union(*(falt_i(tolka_villkor(rb.sarbarheter[id].villkor,rb.faltdefinitioner()))
        for id in rb.tjanster[tjanst.tjanst].sarbarheter
        if hot in rb.sarbarheter[id].hot and rb.sarbarheter[id].galler in galler))
    if falt & set(tjanst.okanda_uppgifter):return None
    if riskled not in ('inneboende','kvarstaende') or dimension not in ('pt','tf'):
        return None
    if riskled=='kvarstaende' and (dimension!='pt' or s.kvarstaende is None):
        return None
    from riskanalys.bedomning.scenarier import _scenario
    from riskanalys.regelverk.modeller import Sarbarhet,Effekt
    kat=rb.tjanster[tjanst.tjanst]
    if any(id not in rb.sarbarheter for id in s.sarbarheter):return None
    extra=Sarbarhet(id='REFERENS:+1',namn='Kontrafaktisk +1, ingen beslutad vikt',omrade='verk',grund='metodval',
        villkor={'falt':kat.erbjuds_falt,'op':'==','varde':True},effekt=Effekt(sannolikhet=1),galler='bada',
        kallor=rb.hot[hot].kallor,hot=(hot,))
    # Lägg +1 före golv och tak, även om en framtida metod innehåller negativa faktorer.
    referens=_scenario(rb,kat,rb.hot[hot],dimension,tuple(rb.sarbarheter[id] for id in s.sarbarheter)+(extra,),
        tjanst.kontroller,frozenset((hot,)) if s.iakttaget else frozenset())
    return referens.risk if riskled=='inneboende' else referens.kvarstaende
