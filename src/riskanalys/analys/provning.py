"""Rena innehållsprövningar; kontrollerar inte levande filer eller modellkod."""
import json
import re
from dataclasses import dataclass
from datetime import date
from typing import Literal
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.kontrollsumma import for_text
from riskanalys.analys.modeller import Analysbeslut, Analyspaket

ALLTID = frozenset({1,2,4,6,7,8,9,13,14,16})
BLOCKFALT = {
    1:('exponering','exponeringsbelagg'), 2:('delningsmotivering','delanalyser'),
    3:('betalningsinsyn',), 4:('uppdragsprovning',),
    5:('leverantorsmotivering','leverantorer'), 6:('scenarier','scenariokopplingar'),
    7:('sarbarhetsprovningar',), 8:('samverkan',),
    9:('erfarenhetsprovning','erfarenhetsbelagg'), 10:('kontroller',),
    11:('kontroller','gap'), 12:('reduktionsprovning','reduktionsmotivering','kontroller','gap'),
    13:('pt_motivering',), 14:('tf_motivering',),
    15:('sektorsjamforelse','sanktioner'), 16:('slutsats','rutinatgarder','gap'),
}
_MARKOR = re.compile(r'\[(?:VERIFIERA|KOMPLETTERA|FYLL I)[^\]]*\]',re.I)
_GAMMAL_MOTIVERING = re.compile(
    r'Motorns (?:PT-utfall: (?:låg|måttlig|hög|mycket hög|okänt); kvarstående '
    r'(?:låg|måttlig|hög|mycket hög|okänd)\. Lokal rimlighetsprövning återstår\.'
    r'|TF-utfall: (?:låg|måttlig|hög|mycket hög|okänt)\. Separat lokal prövning återstår\.)')


def summa(data) -> str:
    if hasattr(data,'model_dump'):
        data=data.model_dump(mode='json')
    return for_text(json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':')))


def scenariosumma(scenario) -> str:
    return summa(scenario)


def underlagssumma(paket: Analyspaket) -> str:
    return summa(paket.bindning)


def svarssumma(paket: Analyspaket) -> str:
    return summa(paket.model_dump(mode='json',exclude={'beslut','revision'}))


def registersumma(paket: Analyspaket) -> str:
    return summa(paket)


def blocksumma(paket: Analyspaket, tjanst: str, nummer: int) -> str:
    t=next(t for t in paket.tjanster if t.tjanst==tjanst)
    gemensamt={}
    if paket.schemaversion==2:
        from riskanalys.analys.gemensam import effektiv_tjanst
        gemensamt={
            'sarbarhetstillampningar':[x.model_dump(mode='json') for x in t.sarbarhetstillampningar],
            'verksamhetstillampningar':[x.model_dump(mode='json') for x in t.verksamhetstillampningar],
            'tackningsprovningar':[x.model_dump(mode='json') for x in t.tackningsprovningar],
            'sarbarheter':[x.model_dump(mode='json') for x in paket.gemensamma_sarbarhetsprovningar
                          if x.id in {a.post for a in t.sarbarhetstillampningar}],
            'verksamhet':[x.model_dump(mode='json') for x in paket.gemensamma_verksamhetsposter
                         if x.id in {a.post for a in t.verksamhetstillampningar}],
        }
        t=effektiv_tjanst(paket,tjanst)
    data=t.model_dump(mode='json')
    block=next((b for b in t.block if b.nummer==nummer),None)
    innehall={f:data[f] for f in BLOCKFALT[nummer]}
    # Dependencies are included, not only the visible prose. Never include confirmations themselves.
    ids={k.scenario for k in t.scenariokopplingar}
    gemensamma=[s.model_dump(mode='json') for s in paket.gemensamma_scenarier if s.id in ids]
    scenarioblock={2,4,6,7,8,9,10,11,12,13,14,16}
    beroenden={}
    if nummer in (8,13,14,16):
        beroenden['sarbarhetsprovningar']=data['sarbarhetsprovningar']
    if nummer in (13,14,16):
        for f in ('samverkan','kontroller','betalningsinsyn','uppdragsprovning'):
            beroenden[f]=data[f]
    if nummer in (4,10,11,12):
        beroenden['betalningsinsyn']=data['betalningsinsyn']
    tillagg={'gemensamt':gemensamt} if paket.schemaversion==2 else {}
    return summa(dict(underlag=paket.bindning.model_dump(mode='json'),tjanst=tjanst,**tillagg,
        nummer=nummer,innehall=innehall,beroenden=beroenden,
        aktivering=block.aktivering if block else None,
        motivering=block.motivering if block else None,
        belagg=[b.model_dump(mode='json') for b in paket.belagg],
        scenarier=([*gemensamma,*[s.model_dump(mode='json') for s in t.scenarier]] if nummer in scenarioblock else [])))


def stoddatum(paket: Analyspaket, tjanst: str) -> tuple[tuple[str,date],...]:
    """Daterade poster som ett godkännande vilar på.

    Frister och uppföljningsdatum (rutinåtgärdens uppföljning, gapets tidsfrist och
    nästa modellgenomgång) är framåtblickande och ingår därför inte.
    """
    t=next((t for t in paket.tjanster if t.tjanst==tjanst),None)
    u=t.uppdragsprovning if t else None
    uppdrag=(('uppdragsbeslutet',u.datum),) if u and u.beslutsstatus=='beslutad' and u.datum else ()
    m=paket.modellrisk
    modell=(('modellutvärderingen',m.utvarderad),('modellriskbeslutet',m.beslutsdatum),
            *((f'modellfelet {f.id}',f.datum) for f in m.fel)) if m else ()
    return (('bedömningen',paket.bindning.bedomningsdatum),
            *((f'belägget {b.id}',b.datum) for b in paket.belagg),*uppdrag,*modell)


def senare_stod(paket: Analyspaket, tjanst: str, godkannande: date) -> tuple[str,...]:
    """Underlag daterat efter godkännandet kan inte ha burit godkännandet."""
    return tuple(f'{tjanst}: {namn} har datum {datum.isoformat()}, efter analysgodkännandet '
        f'{godkannande.isoformat()}. Underlag för ett godkännande får inte vara senare än godkännandet. '
        'Rätta datumet eller godkänn först när underlaget finns.'
        for namn,datum in stoddatum(paket,tjanst) if datum>godkannande)


def registrera_beslut(paket: Analyspaket, beslut: Analysbeslut) -> Analyspaket:
    t=next((t for t in paket.tjanster if t.tjanst==beslut.tjanst),None)
    if t is None or not t.forfattare:
        raise RiskanalysFel('Identifiera författaren till tjänstens svar före beslut.')
    if (beslut.revision!=paket.revision or beslut.underlagssumma!=underlagssumma(paket)
            or beslut.svarssumma!=svarssumma(paket)):
        raise RiskanalysFel('Analysen har ändrats. Läs om svaren före beslut.')
    tidigast=max([paket.bindning.bedomningsdatum,*[b.datum for b in paket.belagg]])
    if beslut.datum<tidigast:
        raise RiskanalysFel('Beslutsdatum får inte föregå bedömningen eller beläggen.')
    # Underkännande får dokumentera felaktiga datum; bara godkännande kräver burande underlag.
    senare=senare_stod(paket,beslut.tjanst,beslut.datum) if beslut.godkand else ()
    if senare:
        raise RiskanalysFel(' '.join(senare))
    nytt=beslut.model_copy(update={'forfattare':t.forfattare,
        'egen_granskning':t.forfattare.strip().casefold()==beslut.namn.strip().casefold()})
    return paket.model_copy(update={'beslut':(*paket.beslut,nytt)})


def gallande_beslut(paket: Analyspaket, tjanst: str) -> Analysbeslut | None:
    senaste=next((b for b in reversed(paket.beslut) if b.tjanst==tjanst),None)
    if senaste and (senaste.revision,senaste.underlagssumma,senaste.svarssumma)==(
            paket.revision,underlagssumma(paket),svarssumma(paket)):
        return senaste
    return None


# Positiv observation kräver räckvidd och genomförandebelägg. Bara tillräcklig täckning bär
# ett helt kontrollavdrag; delvis täckning ensam räcker inte före ett metodbeslut (D8).
POSITIV_TACKNING = ('bedomd_tillracklig','delvis')
TILLRACKLIGT_STOD = ('bedomd_tillracklig',)


def _sankt(fran, till) -> bool:
    from riskanalys.bedomning.motor import RISKNIVAER
    return bool(fran and till) and RISKNIVAER.index(till)<RISKNIVAER.index(fran)


def sankta_scenarier(t) -> tuple:
    """PT-scenarier som motorn har sänkt med en kontroll; TF sänks aldrig."""
    return tuple(s for s in t.scenarier if s.dimension=='pt' and _sankt(s.risk,s.kvarstaende))


def faktisk_reduktion(t) -> bool:
    """Sann när tjänstens nivå eller något enskilt scenario har sänkts.

    Utan scenarier (äldre bedömningar) avgör tjänstens nivå ensam, som tidigare.
    """
    return _sankt(t.inneboende.risk if t.inneboende else None,t.kvarstaende) or bool(sankta_scenarier(t))


def _rackviddshot(rb, tjanst, c) -> frozenset:
    """Hot som kontrollprövningens beskrivna källräckvidd för tjänsten faktiskt avser."""
    kontroll=rb.kontroller.get(c.kontroll)
    rack={r.id:r for r in kontroll.rackvidd} if kontroll else {}
    return frozenset(h for id in c.rackvidd if id in rack and rack[id].tjanst==tjanst
                     and rack[id].beskrivningsstatus=='beskriven' for h in rack[id].hot)


@dataclass(frozen=True)
class Sankningsbrist:
    """Ett skäl till att den lokala prövningen inte godtar motorns sänkning av ett scenario."""
    scenario: object
    orsak: Literal['saknas','oprovat','motstridig','obelagd','delvis','stod']
    kontroller: tuple[str,...]


def sankningsbrister(rb, profil, a, t, scenarier, relevanta, belagg) -> tuple[Sankningsbrist,...]:
    """Spärren per sänkt motorscenario: byrån kan stoppa en sänkning, aldrig skapa en.

    `scenarier` är tjänstens effektiva lokala scenarier (lokala och aktuellt bekräftade
    samma-kopplingar); `relevanta` de av dem som byrån bedömt relevanta; `belagg` paketets
    belägg per ID. En tillräcklig observation bär sänkningen bara om den uppfyller samma
    beläggskrav som granskningen ställer på en positiv kontrollobservation.
    """
    brister=[]
    for s in sankta_scenarier(t):
        def brist(orsak,kontroller=s.tackande_kontroller):
            brister.append(Sankningsbrist(s,orsak,tuple(kontroller)))
        med_hot={id for id,x in scenarier.items() if s.hot in x.hot}
        provade=[c for c in a.kontroller if c.scenario in med_hot and c.kontroll in s.tackande_kontroller]
        if any(c.tackning=='saknas' for c in provade):
            brist('saknas')
        if not med_hot&relevanta:
            brist('oprovat')
            continue
        stodjande=[c for c in provade if c.scenario in relevanta and s.hot in _rackviddshot(rb,a.tjanst,c)]
        angivna={c.kontroll for c in stodjande if c.tackning in TILLRACKLIGT_STOD}
        oklara={c.kontroll for c in stodjande if c.tackning in ('delvis','okand')}
        if angivna&oklara:
            # Ett tillräckligt utfall i ett scenario får inte dölja ett svagare för samma kontroll och hot.
            brist('motstridig',sorted(angivna&oklara))
        belagda=[c for c in stodjande if c.tackning in TILLRACKLIGT_STOD
                 and not positiva_observationsbrister(rb,profil,a,c,scenarier,belagg)]
        if not belagda:
            brist('obelagd' if angivna else 'delvis' if any(c.tackning=='delvis' for c in stodjande) else 'stod')
    return tuple(brister)


def scenarioreduktionsbrister(rb, profil, a, t, scenarier, relevanta, belagg) -> tuple[str,...]:
    texter={
        'saknas':lambda b:f'{b.scenario.hot}: kontrollen täcker enligt byråns prövning inte scenariot; '
            'rätta kontrolluppgifterna eller registrera metodkonflikt.',
        'oprovat':lambda b:f'{b.scenario.hot}: motorn sänker scenariot men hotet saknar relevant lokal scenarioprövning; '
            'pröva hotet i ett relevant scenario eller registrera metodkonflikt.',
        'motstridig':lambda b:f'{b.scenario.hot}: byråns prövningar av bärande kontroll ({", ".join(b.kontroller)}) '
            'är motstridiga; ange en samlad bedömning av täckningen eller registrera metodkonflikt.',
        'obelagd':lambda b:f'{b.scenario.hot}: den tillräckliga täckningen av bärande kontroll ({", ".join(b.kontroller)}) '
            'saknar beskriven räckvidd eller aktuellt genomförandebelägg och bär därför inte sänkningen. '
            'Komplettera beläggen eller registrera metodkonflikt.',
        'delvis':lambda b:f'{b.scenario.hot}: byråns prövning visar bara delvis täckning av bärande kontroll '
            f'({", ".join(b.kontroller)}); delvis täckning räcker inte som stöd för ett helt '
            'kontrollavdrag. Komplettera prövningen eller registrera metodkonflikt.',
        'stod':lambda b:f'{b.scenario.hot}: motorns sänkning saknar positiv lokal prövning av en bärande kontroll '
            f'({", ".join(b.kontroller)}) i ett relevant scenario med hotet; '
            'pröva kontrollen för scenariot eller registrera metodkonflikt.',
    }
    return tuple(texter[b.orsak](b) for b in sankningsbrister(rb,profil,a,t,scenarier,relevanta,belagg))


def effektiva_scenarier(paket, a) -> tuple[dict,frozenset]:
    """Tjänstens lokala scenarier och aktuellt bekräftade samma-kopplingar, samt de relevanta.

    Samma regel som `_tjanstbrister` använder; ogiltiga kopplingar prövas där som fel.
    """
    gem={s.id:s for s in paket.gemensamma_scenarier}
    scenarier={s.id:s for s in a.scenarier}
    for kop in a.scenariokopplingar:
        s=gem.get(kop.scenario)
        if s is not None and kop.tillampning=='samma' and kop.bekraftad and kop.scenariosumma==scenariosumma(s):
            scenarier[s.id]=s
    return scenarier,frozenset(id for id,s in scenarier.items() if s.relevans=='relevant')


def ej_godtagna_sankningar(rb, profil, paket, a, t) -> tuple[Sankningsbrist,...]:
    """Skälen per sänkt motorscenario som den lokala prövningen inte godtar, för rapportens förklaring."""
    scenarier,relevanta=effektiva_scenarier(paket,a)
    return sankningsbrister(rb,profil,a,t,scenarier,relevanta,{b.id:b for b in paket.belagg})


def positiva_observationsbrister(rb, profil, a, c, scenarier, belagg) -> tuple[str,...]:
    """Beläggskraven för en positiv kontrollobservation (tillräcklig eller delvis täckning)."""
    from riskanalys.bedomning.erfarenheter import belagd_uppgift
    fel=[]
    kontroll=rb.kontroller.get(c.kontroll)
    rack={r.id:r for r in kontroll.rackvidd} if kontroll else {}
    s=scenarier.get(c.scenario)
    relevanta_r=[rack[id] for id in c.rackvidd if id in rack and rack[id].tjanst==a.tjanst
                and getattr(rack[id],'beskrivningsstatus',None)=='beskriven'
                and s and bool(set(rack[id].hot)&set(s.hot))]
    if not relevanta_r:
        fel.append(f'{c.scenario}: positiv täckning saknar beskriven relevant källräckvidd.')
    # A catalog source or ordinary profile total cannot prove execution of this control.
    f=kontroll.genomforande_falt if kontroll else None
    u=profil.uppgifter.get(f)
    faktiskt_belagt=bool(f and belagd_uppgift(rb,profil,f) and u and u.varde=='belagt')
    if not faktiskt_belagt:
        fel.append(f'{c.scenario}: positivt genomförande motsäger profilens värde eller saknar aktuellt belagt genomförande; rätta intaget.')
    genomfort=bool(faktiskt_belagt and any(id in belagg and (belagg[id].dokument or
        f in belagg[id].profilfalt) for id in c.belagg))
    if not genomfort:
        fel.append(f'{c.scenario}: aktuellt genomförandebelägg för kontrollen saknas.')
    return tuple(fel)


def _saktext(text):
    return (isinstance(text,str) and bool(text.strip()) and not _MARKOR.search(text)
            and not _GAMMAL_MOTIVERING.fullmatch(' '.join(text.split())))


def analysbrister(rb, profil, bedomning, paket: Analyspaket) -> tuple[str,...]:
    from riskanalys.profil.lagring import profilrevision
    fel=[]
    def krav(villkor,text):
        if not villkor:
            fel.append(text)
    krav(paket.bindning.byra==profil.byra.id==bedomning.byra,'Byråbindningen stämmer inte.')
    krav(paket.bindning.profilrevision==profilrevision(profil),'Profilen har ändrats; förnya analysunderlaget.')
    krav(paket.bindning.regelbas==rb.kontrollsumma==bedomning.regelbas_kontrollsumma,'Regelbasbindningen stämmer inte.')
    krav(paket.bindning.bedomningsdatum==bedomning.datum,'Bedömningsdatum stämmer inte.')
    if paket.schemaversion==2:
        from riskanalys.analys.provning_v2 import gemensamma_analysbrister
        fel.extend(gemensamma_analysbrister(rb,profil,bedomning,paket))
    belagg={b.id:b for b in paket.belagg}
    for b in paket.belagg:
        for f in b.profilfalt:
            krav(f in rb.falt and profil.ar_bekraftad(f),f'{b.id}: profilbelägget {f} är inte aktuellt bekräftat.')
            u=profil.uppgifter.get(f)
            if u:
                krav(bool(u.kalla and u.datum and u.bekraftad_av),f'{b.id}: profiluppgiftens belägg är ofullständiga.')
                krav(b.period==u.period,f'{b.id}: beläggets period skiljer sig från {f}.')
                krav(b.datum==u.datum,f'{b.id}: beläggets datum skiljer sig från {f}.')
    gem={s.id:s for s in paket.gemensamma_scenarier}
    from riskanalys.bedomning.sektorsrisk import sektorsavvikelser
    sektorer={s.tjanst for s in sektorsavvikelser(rb,bedomning,profil)}
    analyser={t.tjanst:t for t in paket.tjanster}
    for t in bedomning.tjanster:
        katalog=rb.tjanster[t.tjanst]
        if t.erbjuds is None:
            fel.append(f'{t.tjanst}: komplettera tjänsteutbudet i intaget.')
        if t.erbjuds is False:
            krav(profil.ar_bekraftad(katalog.erbjuds_falt),f'{t.tjanst}: ej erbjuden tjänst saknar aktuellt profilbelägg.')
            continue
        a=analyser.get(t.tjanst)
        if a is None:
            fel.append(f'{t.tjanst}: tjänsteanalys saknas.')
            continue
        if paket.schemaversion==2:
            from riskanalys.analys.gemensam import effektiv_tjanst
            a=effektiv_tjanst(paket,a.tjanst)
        _tjanstbrister(rb,profil,t,a,paket,gem,belagg,krav,t.tjanst in sektorer)
        g=gallande_beslut(paket,t.tjanst)
        # Även ett tidigare sparat godkännande prövas, så att dokument och fastställelse stoppas.
        if g is not None and g.godkand:
            fel.extend(senare_stod(paket,t.tjanst,g.datum))
    for id in analyser:
        krav(id in {t.tjanst for t in bedomning.tjanster},f'{id}: tjänsten saknas i bedömningen.')
    return tuple(dict.fromkeys(fel))


def _tjanstbrister(rb,profil,t,a,paket,gem,belagg,krav,sektorsavvikelse):
    prefix=f'{a.tjanst}: '
    def k(v,text):krav(v,prefix+text)
    def text(v,namn):k(_saktext(v),f'{namn} saknar ett färdigt svar.')
    def refs(ids,namn,kravs=True):
        k(bool(ids) or not kravs,f'{namn} saknar belägg.')
        for id in ids:k(id in belagg,f'{namn} hänvisar till okänt belägg {id}.')
    katalog=rb.tjanster[a.tjanst]
    k(bool(a.forfattare),'Författare saknas.')
    if t.egen_erfarenhet is not None:
        k(t.egen_erfarenhet.belagd,'Aktuellt underlag för egen erfarenhet saknas.')
    lokala={s.id:s for s in a.scenarier}
    scenarier=dict(lokala)
    for kop in a.scenariokopplingar:
        s=gem.get(kop.scenario)
        k(s is not None,f'Okänt gemensamt scenario {kop.scenario}.')
        if s is None:continue
        k(kop.bekraftad and kop.scenariosumma==scenariosumma(s),f'Scenariokopplingen {s.id} är inte aktuellt bekräftad.')
        if kop.tillampning=='samma':
            k(not kop.lokal_scenario,f'Samma-kopplingen {s.id} får inte dölja en lokal variant.')
            if kop.bekraftad and kop.scenariosumma==scenariosumma(s):scenarier[s.id]=s
        else:
            k(kop.lokal_scenario in lokala and _saktext(kop.motivering),f'Avvikelsen från {s.id} saknar lokal variant/motivering.')
            if kop.lokal_scenario in lokala:
                k(set(s.hot)<=set(lokala[kop.lokal_scenario].hot),f'Lokalt scenario tappar hot från {s.id}.')
    hot=set()
    delids={d.id for d in a.delanalyser}
    anvanda_delar=set()
    for s in scenarier.values():
        hot.update(s.hot)
        k(set(s.hot)<=set(katalog.hot),f'{s.id} har hot utanför tjänsten.')
        k(s.relevans!='okant',f'{s.id}: scenariots relevans är okänd.')
        text(s.motivering,f'{s.id} relevansmotivering')
        text(s.rubrik,f'{s.id} rubrik')
        text(s.handelseforlopp,f'{s.id} händelseförlopp')
        refs(s.belagg,s.id)
        k(set(s.delanalyser)<=delids,f'{s.id} hänvisar till annan eller okänd delanalys.')
        if a.delanalyser and s.relevans=='relevant':
            k(s.id in lokala and bool(s.delanalyser),f'{s.id} kräver lokal koppling till arbetsmoment.')
            anvanda_delar.update(s.delanalyser)
    k(set(katalog.hot)<=hot,'Varje kataloghot kräver uttrycklig scenarioprövning.')
    text(a.delningsmotivering,'Delningsmotivering')
    k(delids<=anvanda_delar,'Varje delanalys behöver ett relevant lokalt scenario.')
    for d in a.delanalyser:
        text(d.rubrik,d.id);text(d.arbetsmoment_och_befogenheter,d.id);refs(d.belagg,d.id)
    relevanta={id for id,s in scenarier.items() if s.relevans=='relevant'}
    block={b.nummer:b for b in a.block}
    k(set(block)==set(range(1,17)),'Alla 16 guideblock ska ha aktivering eller avgränsning.')
    for n,b in block.items():
        if n in ALLTID:k(b.aktivering=='aktiv',f'Block {n} är alltid obligatoriskt.')
        k(b.aktivering!='okand',f'Block {n} har okänd aktivering.')
        text(b.motivering,f'Block {n} aktiveringsskäl')
        if b.aktivering=='aktiv':k(b.bekraftad_summa==blocksumma(paket,a.tjanst,n),f'Block {n} är inte aktuellt bekräftat.')
    def aktiv(n):return n in block and block[n].aktivering=='aktiv'
    extern=[]
    for f in ('P-RISK.extern_kyc','P-RISK.utkontraktering'):
        if f in rb.falt:
            u=profil.uppgifter.get(f)
            extern.append(u.varde if profil.ar_bekraftad(f) else None)
    if extern and any(v is None for v in extern):k(False,'Extern KYC/utkontraktering är okänd; rätta intaget.')
    if extern and all(v is False for v in extern):
        k(not a.leverantorer,'Lokal leverantörsprövning motsäger profilens nej till extern KYC/utkontraktering; rätta intaget.')
    if any(v is True for v in extern):k(aktiv(5),'Leverantörsblocket måste aktiveras vid extern KYC/utkontraktering.')
    if relevanta:
        k(aktiv(10) and aktiv(11),'Relevanta scenarier kräver kontroll- och luckprövning.')
    reduktion=faktisk_reduktion(t)
    if reduktion:k(aktiv(12),'Faktisk motorreduktion kräver reduktionsprövning.')
    if sektorsavvikelse:
        k(aktiv(15),'Relevant sektorsavvikelse kräver aktiverad sektor-/sanktionsprövning.')
    if t.sanktionsrisk and any(profil.ar_bekraftad(f) and profil.uppgifter[f].varde is True
                              for f in ('P-GEO.sanktionsanknytning',)):
        k(aktiv(15),'Sanktionsanknytning kräver sektor-/sanktionsprövning.')
    for namn in ('exponering','samverkan','erfarenhetsprovning','pt_motivering','tf_motivering','slutsats'):
        text(getattr(a,namn),namn)
    refs(a.exponeringsbelagg,'Exponering');refs(a.erfarenhetsbelagg,'Erfarenhetsprövning')
    _insyn_uppdrag(a,aktiv,text,refs,k)
    _sarbarheter(a,rb,katalog,scenarier,relevanta,text,refs,k,gemensamma=paket.schemaversion==2)
    _kontroller_rutiner(a,rb,profil,katalog,scenarier,relevanta,belagg,text,refs,k)
    if aktiv(15):text(a.sektorsjamforelse,'Sektorsjämförelse');text(a.sanktioner,'Sanktionsprövning')
    k(a.reduktionsprovning not in ('okand','metodkonflikt'),'Reduktionsprövningen har okänd effekt eller metodkonflikt.')
    k((a.reduktionsprovning=='ej_reduktion')== (not reduktion),'Reduktionsprövningen stämmer inte med motorns faktiska reduktion.')
    if reduktion:
        k(bool(relevanta),'Faktisk reduktion saknar relevant stöd i lokal scenarioprövning.')
        text(a.reduktionsmotivering,'Reduktionsmotivering')
        if t.scenarier:
            # Bara sänkta motorscenarier behöver reduktionsstöd; övriga brister prövas som kontroll/gap.
            for brist in scenarioreduktionsbrister(rb,profil,a,t,scenarier,relevanta,belagg):k(False,brist)
        else:
            for id in relevanta:
                k(any(c.scenario==id and c.tackning in TILLRACKLIGT_STOD for c in a.kontroller),
                  f'{id}: faktisk reduktion saknar belagd scenariotäckning; registrera metodkonflikt.')
    for g in a.gap:
        text(g.beskrivning,g.id);text(g.motivering,g.id);refs(g.belagg,g.id,kravs=g.status=='atgardat')
        if g.status=='accepterad_kvarstaende_risk':
            k(g.typ=='kontrollbrist' and bool(g.ansvar and g.tidsfrist),f'{g.id}: bara känd kontrollbrist med ansvar/frist får accepteras.')
        elif g.status=='oppet':
            k(False,f'{g.id}: öppet {g.typ} hindrar attest.')


def _insyn_uppdrag(a,aktiv,text,refs,k):
    insyn=a.betalningsinsyn
    if aktiv(3):
        k(insyn.status=='bedomd','Betalningsinsynen behöver bedömas.')
        for n in ('synliga_floden','insynsluckor','avsandare_och_mottagare','underlagens_tillforlitlighet','motivering'):
            text(getattr(insyn,n),'Betalningsinsyn '+n)
        refs(insyn.belagg,'Betalningsinsyn')
    else:
        k(insyn.status=='ej_tillamplig','Betalningsinsyn måste uttryckligen avgränsas när blocket inte är aktivt.')
        text(insyn.motivering,'Avgränsad betalningsinsyn')
    u=a.uppdragsprovning
    k(u.status!='okant','Uppdragets hanterbarhet är okänd.')
    text(u.kompetens_och_insyn,'Kompetens och insyn');text(u.motivering,'Uppdragsprövning');refs(u.belagg,'Uppdragsprövning')
    if u.beslutsstatus=='beslutad':k(bool(u.ansvar and u.datum),'Uppdragsbeslut saknar ansvar/datum.')
    if u.status=='kan_inte_hanteras':k(u.handlingsalternativ in ('begransa','avboj','avsluta') and u.beslutsstatus=='beslutad',
                                  'Ohanterbart uppdrag får inte fortsätta oförändrat.')
    if u.status=='kraver_atgard':
        k(u.handlingsalternativ!='fortsatt' and u.beslutsstatus=='beslutad' and bool(u.ansvar and u.datum and u.belagg),
          'Åtgärdskrävande uppdrag saknar belagd beslutad åtgärd/avgränsning.')
    if aktiv(5):
        text(a.leverantorsmotivering,'Leverantörsmotivering');k(bool(a.leverantorer),'Leverantörsprövning saknas.')
        for l in a.leverantorer:
            for n in ('omfattning','leverantorens_kontroller','egen_verifiering','brister_och_motstridigheter','ansvar'):
                text(getattr(l,n),l.id+' '+n)
            refs(l.belagg,l.id)


def _sarbarheter(a,rb,katalog,scenarier,relevanta,text,refs,k,*,gemensamma=False):
    omraden = ('kund','kanal','geo','verk') + (('tjanst',) if any(rb.sarbarheter[id].omrade == 'tj' for id in katalog.sarbarheter) else ())
    for omrade in omraden:
        k(any(s.omrade==omrade for s in a.sarbarhetsprovningar),f'Sårbarhetsområdet {omrade} saknas.')
    for s in a.sarbarhetsprovningar:
        k(s.relevans!='okant',f'{s.id}: sårbarhetens relevans är okänd.')
        text(s.motivering,s.id);refs(s.belagg,s.id)
        for id in s.sarbarheter:
            k(id in rb.sarbarheter and (id in katalog.sarbarheter or gemensamma and s.id.startswith('gemensam:')),f'{s.id}: okänd sårbarhet {id}.')
            if id in rb.sarbarheter:k(('tjanst' if rb.sarbarheter[id].omrade=='tj' else rb.sarbarheter[id].omrade)==s.omrade,f'{s.id}: sårbarheten hör till annat område.')
        k(set(s.scenarier)<=set(scenarier),f'{s.id}: okänd scenarioreferens.')
        if s.relevans=='relevant':k(bool(set(s.scenarier)&relevanta),f'{s.id}: relevant sårbarhet saknar relevant scenario.')


def _kontroller_rutiner(a,rb,profil,katalog,scenarier,relevanta,belagg,text,refs,k):
    for id in relevanta:k(any(c.scenario==id for c in a.kontroller),f'{id}: kontrollprövning saknas.')
    for c in a.kontroller:
        k(c.scenario in scenarier,f'Okänt scenario {c.scenario} i kontrollprövningen.')
        k(c.kontroll in katalog.kontroller and c.kontroll in rb.kontroller,f'Kontrollen {c.kontroll} hör inte till tjänsten.')
        text(c.tillampning,'Kontrolltillämpning');text(c.utfall,'Kontrollutfall');text(c.kvarstar,'Kvarstående risk')
        k(c.tackning!='okand',f'{c.scenario}: kontrollens effekt är okänd.')
        refs(c.belagg,'Kontrollprövning',kravs=c.tackning!='saknas')
        kontroll=rb.kontroller.get(c.kontroll)
        rack={r.id:r for r in kontroll.rackvidd} if kontroll else {}
        for id in c.rackvidd:k(id in rack,f'Okänd räckvidd {id} för kontrollen.')
        if c.tackning in ('bedomd_tillracklig','delvis'):
            for brist in positiva_observationsbrister(rb,profil,a,c,scenarier,belagg):k(False,brist)
        if c.tackning=='saknas':
            k(any(g.typ=='kontrollbrist' for g in a.gap),f'{c.scenario}: saknad kontroll kräver dokumenterad kontrollbrist.')
    k(bool(a.rutinatgarder),'Slutsatsen kräver konkret rutin/åtgärd eller motiverad oförändrad rutin.')
    for r in a.rutinatgarder:
        k(bool(r.scenarier) and set(r.scenarier)<=set(scenarier),f'{r.id}: konkret giltig scenariokoppling saknas.')
        text(r.atgard,r.id);text(r.utlosare_eller_frekvens,r.id)
        rutin=(r.rutin_id,r.rutin_version,r.rutinbelagg)
        k(all(rutin) or not any(rutin),f'{r.id}: rutin-ID/version/belägg måste anges tillsammans.')
        if all(rutin):
            b=belagg.get(r.rutinbelagg)
            k(bool(b and b.dokument and b.kontrollsumma),f'{r.id}: rutinen kräver privat dokumentkopia.')
        if r.status in ('beslutad','genomford'):
            k(bool(r.ansvar and r.uppfoljning),f'{r.id}: beslut kräver ansvar och uppföljning.')
            # Äldre poster kompletteras inför nytt beslut; status är aldrig belägg för riskreduktion.
            k(_saktext(r.klart_nar),f'{r.id}: beslutad åtgärd kräver ett slutkriterium (klart när).')
            k(r.prioritet!='ej_beslutad',f'{r.id}: beslutad åtgärd kräver en beslutad prioritet.')
        refs(r.belagg,r.id,kravs=r.status=='genomford')
        if r.status=='genomford':k(all(rutin),f'{r.id}: genomförd åtgärd kräver aktuell rutin.')
