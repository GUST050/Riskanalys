"""Kontrafaktisk referens, samma scenarioregler med antagandet ytterligare +1.

Ändrar aldrig motorutfall eller kontrollantaganden. +1 är ingen beslutad vikt
för den egna sårbarheten; giltig täckning kräver en separat sakprövning.
"""
from riskanalys.bedomning.motor import steg, SANNOLIKHETER, _riskdel
from riskanalys.bedomning.scenarier import _sannolikhetsrad, _kvarstaende


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
    rad=_sannolikhetsrad(rb,s.hotniva,steg(s.sarbarhetsniva,1,SANNOLIKHETER))
    risk,_=_riskdel(rb,rad.sannolikhet,s.konsekvens,0)
    return risk.risk if riskled=='inneboende' else _kvarstaende(rb,risk.risk,s.tackande_kontroller)[0]
