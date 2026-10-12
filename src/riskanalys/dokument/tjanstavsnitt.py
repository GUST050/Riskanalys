"""Sex sammanhängande analysdelar per tjänst; AI skriver endast riskmotiveringen."""
from riskanalys.dokument.modeller import Avsnitt, Textstycke, Underrubrik
from riskanalys.dokument.nivatext import nivastycken, sektorsstycken
from riskanalys.dokument.analysunderlag import _belagg, erfarenhetsstycke, sarbarhetsstycke
from collections.abc import Iterable
from riskanalys.bedomning.modeller import Tjanstbedomning
from riskanalys.dokument.modeller import AvsnittsUtkast
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas

def stycke(text: str, refs: Iterable[str], typ: str='analys') -> Textstycke:
    return Textstycke(typ=typ, text=text, referenser=list(refs))

def kontrollstycken(rb: Regelbas, p: Profil, t: Tjanstbedomning) -> tuple[Textstycke, ...]:
    kontroller = list(t.kontroller)
    if t.sanktionsrisk and t.sanktionsrisk.kontroll:
        kontroller.append(t.sanktionsrisk.kontroll)
    resultat = []
    for k in kontroller:
        post = rb.kontroller[k.id]
        text = f"{post.namn}: {post.beskrivning} Utformning: {k.utformning or 'okänd'}; genomförande: {k.genomforande or 'okänt'}; bedömd effekt: {k.effekt or 'okänd'}. "
        text += f"Riskreducerande enligt metodvillkoren: {('ja' if k.fungerar_och_ar_belagd else 'nej')}. "
        refs = [t.tjanst, k.id, post.utformning_falt, post.genomforande_falt]
        for id in (post.effekt_falt, post.utfall_falt):
            if id:
                refs.append(id)
                text += _belagg(rb, p, id) + ' '
        text += 'Noll upptäckta avvikelser bevisar inte effektivitet. Bedömningen kräver sakgranskning av verkan och vilka hot kontrollen täcker.'
        resultat.append(stycke(text, refs))
    return tuple(resultat) or (stycke('Ingen relevant kontroll är dokumenterad. [VERIFIERA]', [t.tjanst]),)

def slutsatsstycken(rb: Regelbas, t: Tjanstbedomning) -> tuple[Textstycke, ...]:
    tj = rb.tjanster[t.tjanst]
    faktorer = ', '.join((rb.sarbarheter[id].namn for id in t.tillampade_sarbarheter)) or 'inga katalogvillkor är uppfyllda i det bekräftade underlaget'
    hot = '; '.join((rb.hot[id].namn for id in t.hot))
    hog = t.inneboende.risk in {'hög', 'mycket hög'} or t.terrorfinansiering.risk in {'hög', 'mycket hög'}
    text = f'{tj.namn}: penningtvättsrisk {t.inneboende.risk}, terrorfinansieringsrisk {t.terrorfinansiering.risk}; kvarstående penningtvättsrisk {t.kvarstaende}. Identifierade faktorer: {faktorer}. '
    text += 'Fördjupad uppföljning behövs även om tjänsten utgör en liten del av omsättningen. ' if hog else 'Behåll individuell prövning och uppföljning av tjänstens risker. '
    text += 'Rutiner: konkretisera kontrollmoment, eskalering och rapporteringsprövning i detta uppdrag. Kundkännedom: verifiera verklig huvudman, syfte, medlens ursprung och relevanta geografiska anknytningar utifrån kundens egen riskprofil; obligatoriska särskilda åtgärder prövas separat i kundmodellen. '
    text += f'Övervakning: följ upp avvikelser mot förväntat beteende och underlag med särskilt fokus på {hot}. Utbildning: använd dessa tillvägagångssätt och tjänstens identifierade sårbarheter som övningsfall, även terrorfinansiering med legala medel. '
    svaga = [rb.kontroller[k.id].namn for k in t.kontroller if not k.fungerar_och_ar_belagd]
    if svaga:
        text += 'Åtgärdsbehov: pröva och belägg effekten hos ' + ', '.join(svaga) + '. '
    if t.status == 'preliminär':
        text += 'Analysen är preliminär; komplettera okända uppgifter före beslut. [VERIFIERA] '
    text += 'Byrån beslutar ansvariga, tidsfrister, faktisk kundkännedom och uppföljningstakt. Texten är ett analysunderlag och intygar inte genomförda åtgärder.'
    return (stycke(text, [t.tjanst, *t.hot, *t.tillampade_sarbarheter, *[k.id for k in t.kontroller]]),)

def scenarier(rb: Regelbas, t: Tjanstbedomning) -> tuple[Textstycke, ...]:
    if not rb.metod.omfattning:
        return ()
    valda = [id for id in t.tillampade_sarbarheter if rb.sarbarheter[id].galler == 'bada'][:2]
    if not valda:
        valda = list(rb.tjanster[t.tjanst].sarbarheter[:1])
    return tuple((stycke(f'Möjligt scenario att pröva i {rb.tjanster[t.tjanst].namn}: {rb.hot[h].beskrivning} Samverkan med {rb.sarbarheter[s].namn} ska prövas mot tjänstens faktiska underlag. Scenariot är hypotetiskt.', [t.tjanst, h, s], typ='scenario') for h, s in zip(t.hot[:len(valda)], valda)))

def bygg_tjanstavsnitt(rb: Regelbas, p: Profil, t: Tjanstbedomning, utkast: AvsnittsUtkast, avsnitt_id: str, *, utokad: bool=False) -> Avsnitt:
    tj = rb.tjanster[t.tjanst]
    slug = tj.erbjuds_falt.removesuffix('_erbjuds')
    refs = [t.tjanst, tj.erbjuds_falt]
    text = f'{tj.namn}: {tj.beskrivning} '
    for suffix, label in [('_antal_kunder', 'Antal kunder i tjänsten'), ('_andel_kunder', 'Andel av byråns aktiva kunder'), ('_andel_omsattning', 'Andel av byråns omsättning'), ('_arbetssatt', 'Byråns beskrivning av uppdrag och arbetssätt')]:
        id = slug + suffix
        if id in rb.falt:
            refs.append(id)
            text += label + ': ' + _belagg(rb, p, id) + ' '
    delar = [('Beskrivning och omfattning', (stycke(text, refs, typ='beskrivning'),)), ('Hot och egna erfarenheter', tuple((stycke(f'{rb.hot[id].namn}: {rb.hot[id].beskrivning}', [t.tjanst, id, *rb.hot[id].kallor]) for id in t.hot)) + (erfarenhetsstycke(rb, p, t),)), ('Sårbarheter och motivering', tuple((sarbarhetsstycke(rb, p, t.tjanst, id) for id in tj.sarbarheter)) + (scenarier(rb, t) if utokad else ())), ('Kontroller och effekt', kontrollstycken(rb, p, t)), ('Risknivåer och motivering', (*nivastycken(t), *utkast.stycken)), ('Slutsatser', slutsatsstycken(rb, t))]
    stycken = []
    rubriker = []
    for rubrik, texter in delar:
        rubriker.append(Underrubrik(fore_stycke=len(stycken), rubrik=rubrik))
        stycken.extend(texter)
    return Avsnitt(id=avsnitt_id, rubrik=f'Analys av {tj.namn.lower()}', kalla='ai', stycken=tuple(stycken), underrubriker=tuple(rubriker))


def _ai_stycken(svar, numeriska: dict[str, str], perioder: dict[str, str]) -> tuple[Textstycke, ...]:
    from riskanalys.dokument.platshallare import ersatt_tal
    return tuple(stycke(ersatt_tal(s.text, numeriska, perioder), s.referenser, typ=s.typ) for s in svar.stycken)


def bygg_tjanstavsnitt_v3(rb: Regelbas, p: Profil, t: Tjanstbedomning, resultat, avsnitt_id: str) -> Avsnitt:
    """Låsta stycken byggs om ur profil och bedömning; AI-stycken kommer från maskinellt validerade delar (spec 8.4.6)."""
    from riskanalys.dokument.delskrivning import ANSVARSMENING
    from riskanalys.dokument.nivatext import nivastycken, sektorsstycken
    from riskanalys.dokument.delskrivning import kontrollera_resultat
    kontrollera_resultat(rb, p, t, resultat, avsnitt_id)
    tj = rb.tjanster[t.tjanst]
    fb = resultat.faktablad  # grinden har jämfört denna frysta kopia med aktuellt underlag

    def ai(del_id: str, mall: tuple[Textstycke, ...]) -> tuple[Textstycke, ...]:
        svar = resultat.del_(del_id).godkant_svar
        return _ai_stycken(svar, fb.numeriska(), fb.perioder()) if svar else mall

    gammal = bygg_tjanstavsnitt(rb, p, t, AvsnittsUtkast(avsnitt=avsnitt_id, stycken=[], oklarheter=[]), avsnitt_id)
    beskrivning = gammal.stycken[:gammal.underrubriker[1].fore_stycke]
    hotmall = tuple(stycke(f'{rb.hot[id].namn}: {rb.hot[id].beskrivning}', [t.tjanst, id, *rb.hot[id].kallor]) for id in t.hot)
    geo = tuple(sarbarhetsstycke(rb, p, t.tjanst, id) for id in tj.sarbarheter if rb.sarbarheter[id].omrade == "geo")
    sarmall = tuple(sarbarhetsstycke(rb, p, t.tjanst, id) for id in tj.sarbarheter if rb.sarbarheter[id].omrade != "geo")
    mallmotivering = (stycke("Motiveringen kunde inte skrivas maskinellt och behöver kompletteras i sakgranskningen. [VERIFIERA]",
                             [t.tjanst], typ="motivering"),)
    delar = [
        ("Beskrivning och omfattning", tuple(beskrivning)),
        ("Hot och egna erfarenheter", (*ai("hot", hotmall), erfarenhetsstycke(rb, p, t))),
        ("Sårbarheter och motivering", (*geo, *ai("sarbarheter", sarmall))),
        ("Kontroller och effekt", (*kontrollstycken(rb, p, t), *ai("kontroller", ()))),
        ("Risknivåer och motivering", (*nivastycken(t), *sektorsstycken(rb,t), *ai("risknivaer", mallmotivering))),
        ("Slutsatser", (*ai("slutsatser", slutsatsstycken(rb, t)), stycke(ANSVARSMENING, [t.tjanst], typ="beskrivning"))),
    ]
    stycken, rubriker = [], []
    for rubrik, texter in delar:
        rubriker.append(Underrubrik(fore_stycke=len(stycken), rubrik=rubrik))
        stycken.extend(texter)
    return Avsnitt(id=avsnitt_id, rubrik=f'Analys av {tj.namn.lower()}', kalla='ai', stycken=tuple(stycken), underrubriker=tuple(rubriker), formatversion="D-ARB-tjanst-v3")
