"""Infoga lokala fakta; fri text ingår aldrig i AI-underlag eller automatiska riskbeslut."""
from riskanalys.dokument.modeller import Dokument, Textstycke, Avsnitt
from riskanalys.profil.hantering import visa_varde
from riskanalys.profil.omfattning import aktivt


def med_intagsunderlag(dokument: Dokument, rb, profil, bedomning) -> Dokument:
    tillagg = {}
    for f in rb.falt.values():
        if not f.intag or f.personuppgift or not aktivt(f,profil,rb) or not profil.ar_bekraftad(f.id):
            continue
        # Organisationsgrunddata återges redan i syftet; erbjudandena i tjänstelistan.
        if f.id.startswith(('P-ORG.','P-ROLL.')) or f.id.endswith('_erbjuds') or f.alias_for or f.basfalt:
            continue
        u=profil.uppgifter[f.id]
        period=f' Period: {u.period.fran}–{u.period.till}.' if u.period else ''
        text=f'{f.fraga} {visa_varde(f,u.varde)}.{period} Källa: {u.kalla}; bekräftat {u.datum}.'
        stycke=Textstycke(typ='beskrivning',text=text,referenser=[f.id])
        for id in f.intag.avsnitt:
            tillagg.setdefault(id,[]).append(stycke)
    avsnitt=[a.model_copy(update={'stycken':(*a.stycken,*tillagg.get(a.id,()))}) for a in dokument.avsnitt]
    if not any(f.intag for f in rb.falt.values()):
        return dokument
    kontroller=[]; sammanfattning=[]; atgarder=[]
    for t in bedomning.tjanster:
        if t.inneboende is None:continue
        namn=rb.tjanster[t.tjanst].namn
        sammanfattning.append(Textstycke(typ='beskrivning',text=f'{namn}: inneboende penningtvättsrisk {t.inneboende.risk}, kvarstående {t.kvarstaende}; terrorfinansiering {t.terrorfinansiering.risk}. Riskerna redovisas per tjänst; ingen sammanvägd byrånivå beräknas.',referenser=[t.tjanst,*t.regelspar]))
        for k in t.kontroller:
            text=f'{namn}: {rb.kontroller[k.id].namn}. Utformning: {k.utformning}; genomförande: {k.genomforande}. Belagd kontrollverkan enligt motorns villkor: {"ja" if k.fungerar_och_ar_belagd else "nej"}.'
            kontroller.append(Textstycke(typ='beskrivning',text=text,referenser=[k.id,t.tjanst]))
            if not k.fungerar_och_ar_belagd:
                atgarder.append(Textstycke(typ='beskrivning',text=f'{namn}: utred och dokumentera kontrollen {rb.kontroller[k.id].namn}; ingen riskreduktion får antas utan belägg. Ansvarig och tidsfrist behöver bestämmas i verksamhetens åtgärdsarbete.',referenser=[k.id,t.tjanst]))
    avsnitt[-1:-1]=[
        Avsnitt(id='D-ARB.7',rubrik='Kontroller och belägg',kalla='regelbas',stycken=tuple(kontroller)),
        Avsnitt(id='D-ARB.8',rubrik='Sammanställning av risker',kalla='regelbas',stycken=tuple(sammanfattning)),
        Avsnitt(id='D-ARB.9',rubrik='Fortsatt åtgärdsarbete',kalla='regelbas',stycken=tuple(atgarder) or (Textstycke(typ='beskrivning',text='Följ upp kontrollernas faktiska verkan och de kompletteringar som framgår av utkastets granskningsbilaga. Dokumentera ansvar, tidsfrister och genomförande.',referenser=[]),))]
    return dokument.model_copy(update={'avsnitt':tuple(avsnitt)})


def bygg_underlagsbilaga(rb, profil):
    """Alla lokala intagsbelägg granskas i samma dokument; inga råsvar till AI."""
    from riskanalys.dokument.klartext import uppgiftstext
    stycken=[]
    for f in rb.falt.values():
        if not f.intag or f.alias_for or not aktivt(f,profil,rb):
            continue
        # Personnamn återges via lokala rollplatshållare i huvudtexten.
        if f.personuppgift:
            text=f'{f.id}: personuppgift hanteras lokalt i ansvarsfördelningen; källa och datum finns i profilen.'
        else:
            text=uppgiftstext(rb,profil,f.id,med_id=True)
        stycken.append(Textstycke(typ='beskrivning',text=text,referenser=[f.id]))
    for k in rb.kallor.values():
        text=f'{k.id}: {k.titel}. Utgivare: {k.utgivare}; hämtad: {k.hamtad}; källa: {k.url}; kontrollsumma: {k.kontrollsumma or "ingen registrerad originalsumma"}. Registrering är inte byråns genomförda omvärldsbevakning.'
        stycken.append(Textstycke(typ='beskrivning',text=text,referenser=[k.id]))
    return Avsnitt(id='D-ARB.B1',rubrik='Bilaga: Underlag och källversioner',kalla='regelbas',stycken=tuple(stycken))
