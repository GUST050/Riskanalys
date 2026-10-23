"""Fasta presentationsetiketter och förklaringar; ändrar inga motorutfall."""
from collections import Counter

ETIKETTER = {
    'bekraftad':'bekräftad', 'foreslagen':'föreslagen', 'genomford':'genomförd',
    'oppet':'öppen', 'atgardat':'åtgärdad', 'okant':'okänt', 'okand':'okänd',
    'ej_beslutad':'ej beslutad', 'motstridigt_underlag':'motstridigt underlag',
    'accepterad_kvarstaende_risk':'accepterad kvarstående risk',
}


def etikett(varde):
    return ETIKETTER.get(varde,varde)


def celltext(c,orsaker):
    s=c.scenario
    if s is None:
        return {'saknas':'Saknas i denna variant','ej_relevant':'Ej relevant enligt lokal prövning',
                'okant':'Okänt underlag'}[c.status]
    markering='*' if any('fore' in m for m in c.medlemmar) else ''
    efter='†' if any('efter' in m for m in c.medlemmar) else ''
    text=f'{s.risk}{markering} → {s.kvarstaende or "ej beräknad"}{efter}'
    if orsaker:
        text+='\nSänkning ej prövad lokalt' if 'oprovat' in orsaker else '\nSänkning ej godtagen lokalt'
    return text


def slutsats(bedomning,analys):
    valda=[t for t in bedomning.tjanster if t.erbjuds]
    utfall=Counter((t.inneboende.risk if t.inneboende else 'okänd',
                    t.terrorfinansiering.risk if t.terrorfinansiering else 'okänd') for t in valda)
    delar=[f'{n} tjänster har {pt} PT-risk och {tf} TF-risk' for (pt,tf),n in utfall.items()]
    # Redovisa motorns tjänsteutfall, aldrig ett påstående om lokalt belagd effekt.
    if valda and all(t.inneboende and t.kvarstaende==t.inneboende.risk for t in valda):
        delar.append('Motorns kontrollavdrag sänker inte någon tjänsts samlade kvarstående PT-nivå')
    luckor=sum(g.status=='oppet' for a in analys.tjanster for g in a.gap) if analys else 0
    delar.append(f'{luckor} öppna luckor är registrerade i den lokala analysen')
    return '. '.join(delar)+'.'


def gemensamma_motiveringar(analys):
    """Gruppera bara hela identiska och färdiga svar; bevara samtliga originalpointers."""
    from riskanalys.analys.provning import _saktext
    grupper={}
    if analys:
        for i,a in enumerate(analys.tjanster):
            for falt in ('pt_motivering','tf_motivering'):
                text=getattr(a,falt)
                if _saktext(text):grupper.setdefault((falt,text),[]).append((i,a.tjanst))
    return {key:tuple(val) for key,val in grupper.items() if len(val)>1}


def sankningsforklaringar(rb,brister):
    """Samma brist och nivåväg en gång, med alla hot kvar; inga egna riskregler."""
    from riskanalys.dokument.nivamotivering_v8 import _ORSAKER
    per_hot={}
    for b in brister:
        namn=', '.join(rb.kontroller[id].namn+' ('+id+')' for id in b.kontroller)
        per_hot.setdefault((b.scenario.hot,b.scenario.risk,b.scenario.kvarstaende),[]).append(_ORSAKER[b.orsak](namn))
    grupper={}
    for (hot,fore,efter),orsaker in per_hot.items():
        key=(fore,efter,tuple(dict.fromkeys(orsaker)))
        grupper.setdefault(key,[]).append(hot)
    return tuple('Sänkningen '+fore+' → '+efter+' för '+', '.join(hot)+
        ' är inte godtagen av den lokala prövningen: '+'; '.join(orsaker)+'. '
        'Tills prövningen kompletterats eller metodkonflikten avgjorts gäller scenariots inneboende nivå '+fore+
        '; analysen kan inte godkännas. [VERIFIERA]' for (fore,efter,orsaker),hot in grupper.items())
