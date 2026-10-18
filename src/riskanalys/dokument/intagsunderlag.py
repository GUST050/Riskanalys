"""Infoga lokala fakta; fri text ingår aldrig i AI-underlag eller automatiska riskbeslut."""

from datetime import date
from riskanalys.intag.fordelning import kan_ateranvandas
from riskanalys.intag.verksamhetsval import erbjuds_aktuellt, verksamhetsval

from riskanalys.regelverk.granser import metodgransindex
from riskanalys.dokument.delvalidering import SANKTION_OMFORMULERAD
from riskanalys.dokument.modeller import Dokument, Textstycke, Avsnitt
from riskanalys.profil.hantering import visa_varde
from riskanalys.profil.omfattning import aktivt

SANKTIONSFALT = 'P-GEO.sanktionsanknytning'
SANKTIONSNOTIS = (f'Frågan omformulerades {SANKTION_OMFORMULERAD}. '
                  'Tidigare svar läses som att ingen anknytning har identifierats.')


def _aldre_nej_svar(u) -> bool:
    """Bara ett nej som kan ha getts på den gamla frågan; datum saknas eller är senast omformuleringsdagen."""
    return (u is not None and u.varde is False
            and (u.datum is None or u.datum <= date.fromisoformat(SANKTION_OMFORMULERAD)))


def _med_omformuleringsnotis(text: str, profil, falt_id: str) -> str:
    """Ett äldre nej på sanktionsfrågan läses med den snävare betydelsen; notisen visar det i B1."""
    if falt_id != SANKTIONSFALT or not _aldre_nej_svar(profil.uppgifter.get(falt_id)):
        return text
    return f'{text} {SANKTIONSNOTIS}'


def med_intagsunderlag(dokument: Dokument, rb, profil, bedomning) -> Dokument:
    tillagg = {}
    for f in rb.falt.values():
        if not f.intag or f.personuppgift or not aktivt(f,profil,rb) or not profil.ar_bekraftad(f.id):
            continue
        # Organisationsgrunddata återges redan i syftet; erbjudandena i tjänstelistan.
        if f.id.startswith(('P-ORG.','P-ROLL.')) or f.id.endswith('_erbjuds') or f.alias_for or f.basfalt:
            continue
        if not kan_ateranvandas(rb, profil, f.id):
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


def bygg_underlagsbilaga(rb, profil, *, gransindex: dict[str, tuple[float, ...]] | None = None):
    """Alla lokala intagsbelägg granskas i samma dokument; inga råsvar till AI."""
    if gransindex is None:
        gransindex = metodgransindex(rb)
    from riskanalys.bedomning.erfarenheter import belagd_uppgift
    from riskanalys.dokument.klartext import VERIFIERA, faltnamn, gemen, uppgiftstext
    stycken=[]
    for f in rb.falt.values():
        harledd=bool(f.antalfalt and f.basfalt)
        if not (f.intag or harledd) or f.alias_for or not aktivt(f,profil,rb):
            continue
        val = verksamhetsval(rb, f.id)
        if val and (not erbjuds_aktuellt(profil, val[0]) or not profil.ar_bekraftad(f.id)):
            continue
        if not kan_ateranvandas(rb, profil, f.id):
            # Valfri frånvaro eller gammalt underlag är ingen ny kompletteringsspärr.
            continue
        # Personnamn återges via lokala rollplatshållare i huvudtexten.
        if f.personuppgift:
            text=f'{faltnamn(rb,f.id)} ({f.id}): personuppgift hanteras lokalt i ansvarsfördelningen; källa och datum finns i profilen.'
        elif harledd and not belagd_uppgift(rb,profil,f.id):
            # Stoppet är avsett: markeringen finns kvar tills antal och bas är bekräftade för samma period.
            text=(f'{faltnamn(rb,f.id)} ({f.id}): kan inte härledas; bekräfta {gemen(faltnamn(rb,f.antalfalt))} '
                  f'och {gemen(faltnamn(rb,f.basfalt))} för samma period. {VERIFIERA}')
        else:
            text=_med_omformuleringsnotis(uppgiftstext(rb,profil,f.id,med_id=True, gransindex=gransindex),profil,f.id)
        stycken.append(Textstycke(typ='beskrivning',text=text,referenser=[f.id]))
    for k in rb.kallor.values():
        text=f'{k.id}: {k.titel}. Utgivare: {k.utgivare}; hämtad: {k.hamtad}; källa: {k.url}; kontrollsumma: {k.kontrollsumma or "ingen registrerad originalsumma"}. Registrering är inte byråns genomförda omvärldsbevakning.'
        stycken.append(Textstycke(typ='beskrivning',text=text,referenser=[k.id]))
    return Avsnitt(id='D-ARB.B1',rubrik='Bilaga: Underlag och källversioner',kalla='regelbas',stycken=tuple(stycken))
