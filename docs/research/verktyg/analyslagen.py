"""Gemensamma, uttryckliga lägen för syntetiska jämförelser."""
from types import SimpleNamespace
from tester.fixturer.rapportlasprov import bygg_rapportlasprov
from tester.fixturer.gemensam_analys import bygg_direkt_gemensamt_fall

LAGEN=('schema1','direkt2','overforing2')


def valj_lage(parser,lage,schema=None,standard='schema1'):
    alias={1:'schema1',2:'overforing2'}.get(schema)
    if lage and alias and lage!=alias:parser.error('--analyslage och --analys-schema anger olika arbetssätt.')
    return lage or alias or standard


def bygg(rb,rot,namn,lage):
    arbetsbord={}
    if lage=='direkt2':
        f=bygg_direkt_gemensamt_fall(rb,rot,namn)
        import json
        arbetsbord=json.loads((rot/'engangssvar-handlingar.json').read_text());analys=f.paket
    else:
        f=bygg_rapportlasprov(rb,rot,namn);analys=f.analys
        if lage=='overforing2':
            from riskanalys.analys.overforing import foresla_overforing
            analys=foresla_overforing(rb,analys)
    return SimpleNamespace(regelbas=rb,profil=f.profil,bedomning=f.bedomning,analys=analys,arbetsbord=arbetsbord)


def ord_och_upprepning(dokument,profil):
    from riskanalys.dokument.rendering import renderat_avsnitt,synliga_texter
    from collections import Counter,defaultdict
    delar=defaultdict(int);b1=0;texter=[]
    for a in dokument.avsnitt:
        r=tuple(synliga_texter(renderat_avsnitt(a,profil)))
        n=sum(len(x.split()) for x in r);delar[a.leveransdel]+=n
        if a.id=='D-ARB.B1':b1+=n
        texter.extend(x for x in r if len(x.split())>=12)
    if dokument.avsnitt:delar[dokument.avsnitt[0].leveransdel]+=len(dokument.titel.split())
    antal=Counter(texter)
    return {'per_del':dict(delar),'b1':b1,'totalt':sum(delar.values()),
        'upprepade_ordagrant_extra_ord':sum((n-1)*len(s.split()) for s,n in antal.items() if n>1)}
