"""Enbart syntetiska M2-uppgifter, aldrig juridiskt facit eller riktiga byrådata."""
from datetime import date
from riskanalys.profil.modeller import Uppgift,Period
from riskanalys.profil.omfattning import harled_andelar
from riskanalys.dokument.modeller import AvsnittsUtkast,Textstycke
from riskanalys.dokument.underlag import bygg_underlag,tjanster_med_avsnitt
from riskanalys.dokument.validering import validera_utkast

DAG=date(2026,10,10)
PERIOD=Period(fran=date(2026,1,1),till=date(2026,9,30))

def komplett_profil(rb,p):
    upp={}
    for k,f in rb.falt.items():
        if f.alias_for or f.basfalt or k.endswith(('_attest', '_betalningsmandat', '_bankinsyn')):
            # Frivilliga nya verksamhetsval lämnas obesvarade om ett prov inte väljer dem uttryckligen.
            upp[k]=Uppgift();continue
        v={'bool':False,'heltal':0,'tal':0.,'text':'Syntetiskt testnamn','datum':DAG,'andel':0.}.get(f.typ)
        if f.typ=='val':v=p.byra.lan if k=='P-ORG.sateslan' else f.val[0]
        if k=='P-ORG.sateslan':v=p.byra.lan
        if k=='P-BEVAKNING.kallor':v='SRC-TS-2026-14, SRC-VAGL-2025-03'
        if k in {'P-VERK.bokforing','P-VERK.skatteradgivning','P-VERK.bolagstjanster','P-TJ.red01_erbjuds','P-TJ.skatt01_erbjuds','P-TJ.bolag01_erbjuds'}:v=True
        if k in {'P-ORG.antal_anstallda','P-ORG.verksamhetsstallen'}:v=1
        if k=='P-KUND.antal_aktiva':v=100
        if k=='P-VERK.omsattning':v=10000.
        if k.endswith('_sektorsmotivering'):v='Syntetisk belagd lokal motivering för denna tjänsts omfattning och kontroller.'
        if k.startswith('P-TJ.') and k.endswith('_antal_kunder'):v=3 if 'bolag01_' in k else 10
        if k.startswith('P-TJ.') and k.endswith('_omsattning'):v=3000.
        upp[k]=Uppgift(varde=v,status='bekräftad',kalla='Syntetisk testkälla',datum=DAG,bekraftad_av='Syntetisk testperson',period=PERIOD if f.periodkrav else None)
    return harled_andelar(p.model_copy(update={'uppgifter':upp}),rb)


def bygg_testsvar(rb,p,b):
    svar=[]
    for id,t in tjanster_med_avsnitt(b):
        u=bygg_underlag(rb,p,t,id)
        text="Tjänstens ekonomiska flöden kan utnyttjas för att föra in osanna underlag och ge brottsvinster ett legalt utseende."
        refs=[u.hot[0].id,u.sarbarheter[0].id]
        a=AvsnittsUtkast(avsnitt=id,stycken=[Textstycke(typ='analys',text=text,referenser=list(u.regelspar)),Textstycke(typ='motivering',text="Tjänstens ekonomiska flöden kan utnyttjas. Sårbarheter i kundunderlagen kräver spårbara kontroller och uppföljning.",referenser=refs)],oklarheter=[])
        assert not validera_utkast(a,u,()),validera_utkast(a,u,())
        svar.append(a.model_dump(mode='json'))
    return svar


from riskanalys.dokument.modeller import AISvar, AIStycke
from riskanalys.bedomning.korning import kor_bedomning, las_bedomning
from riskanalys.profil.lagring import spara_profil

FYLLNAD = " Byrån konterar kundernas underlag och stämmer av dem mot bankens uppgifter varje månad." * 10


def tjanst_for_prov(mapp, rb, profil):
    spara_profil(mapp, profil)
    b = las_bedomning(kor_bedomning(mapp, rb))
    return tjanster_med_avsnitt(b)[0]


def historiskt_delsvar(del_id, t):
    rb=_regelbas_for_delsvar()
    fyll={
        'T-RED-01':' Bokföraren konterar fakturor och granskar verifikationernas affärshändelser innan periodens bokslut stäms av.',
        'T-SKATT-01':' Skatterådgivaren prövar deklarationsunderlag och skatteupplägg genom att kontrollera transaktionernas skattemässiga syften och konsekvenser.',
        'T-BOLAG-01':' Bolagskonsulten utreder bolagsbildning och ägarbyten genom prövning av aktietecknare, kapitaltillskott samt företrädarnas mandat.',
    }.get(t.tjanst,' '+rb.tjanster[t.tjanst].namn+' analyseras genom prövning av uppdragets särskilda underlag och kundens verksamhet.')*10
    hot=list(t.hot)
    tj=rb.tjanster[t.tjanst]
    sar=list(tj.sarbarheter[:1])
    refs={"hot":[t.tjanst,*hot],"kontroller":[t.tjanst],"risknivaer":[t.tjanst,hot[0],*sar],"slutsatser":[t.tjanst,hot[0]]}
    if del_id=="sarbarheter":
        omraden={}
        for id in tj.sarbarheter:
            omraden.setdefault(rb.sarbarheter[id].omrade,id)
        return AISvar(stycken=[AIStycke(typ="analys",referenser=[t.tjanst,id],text="Underlaget för faktorn ska prövas för denna tjänst."+fyll[:600]) for id in omraden.values()],oklarheter=[])
    extra=" Kundkännedom, övervakning och utbildning anpassas efter hoten." if del_id=="slutsatser" else ""
    return AISvar(stycken=[AIStycke(typ="motivering" if del_id=="risknivaer" else "analys",referenser=refs[del_id],text="Tjänstens flöden kan utnyttjas."+fyll+extra)],oklarheter=[])

from functools import lru_cache

@lru_cache(maxsize=1)
def _regelbas_for_delsvar():
    from riskanalys.regelverk.laddning import ladda_regelbas
    return ladda_regelbas()


def bygg_delsvar(rb, profil, bedomning, *, formatversion="D-ARB-tjanst-v7", tjanstspecifik=False):
    from riskanalys.dokument.skrivversion import delar_for_version
    if formatversion == "D-ARB-tjanst-v7":
        from tester.fixturer.skrivsvar_v7 import godkant_svar_v7, tjanstspecifikt_svar_v7
        bygg = tjanstspecifikt_svar_v7 if tjanstspecifik else godkant_svar_v7
        return [bygg(rb, profil, t, id) for id, t in tjanster_med_avsnitt(bedomning)]
    return [godkant_delsvar(d,t) for _,t in tjanster_med_avsnitt(bedomning) for d in delar_for_version(formatversion)]


def godkant_delsvar(del_id, t):
    """Separata korta H6-svar; äldre jämförelsetext finns i historiskt_delsvar."""
    rb = _regelbas_for_delsvar()
    tj = rb.tjanster[t.tjanst]
    inledning = {
        'T-RED-01': 'Bokföraren granskar fakturor och stämmer av verifikationer mot affärshändelser.',
        'T-RED-02': 'Bokslutskonsulten utreder balansposternas existens genom värderingsunderlag, lagerintyg och dokumentation av ägarlån.',
        'T-RED-03': 'Deklarationshandläggaren jämför avdragsyrkanden, skattemässiga justeringar och dokumenterade transaktioners verkliga innebörd inför deklaration.',
        'T-RED-04': 'Lönekonsulten kontrollerar anställningsavtal, tidrapporter, ersättningsmönster samt mottagarkonton genom attestbehörigheter och oberoende bekräftelser.',
        'T-SKATT-01': 'Skatterådgivaren prövar deklarationsunderlag och transaktionernas skattemässiga syften.',
        'T-BOLAG-01': 'Bolagskonsulten utreder ägarbyten och kapitaltillskott samt företrädarnas mandat.',
    }.get(t.tjanst, tj.namn + ' kräver granskning av uppdragets särskilda underlag och kundens verksamhet.')
    tjansttext = {
        'T-RED-01': (
            ' Fakturor behöver jämföras med leveranser och bokförda betalningar. Oriktiga verifikationer kan ge '
            'brottsvinster sken av vanliga rörelseintäkter. Bokföringsarbetet kräver uppmärksamhet på avvikande '
            'motparter och oförklarade differenser. Avstämning av reskontra behöver knytas till ursprungliga '
            'handlingar. Bokföraren behöver dokumentera vilka affärshändelser som inte kunnat styrkas. '
            'När kvitton saknas behöver kunden förklara utbetalningens ändamål. Kontoutdrag ensamt visar '
            'inte att den bokförda kostnaden avser verklig verksamhet. Periodavslut och rättelser behöver '
            'därför kunna följas tillbaka till verifikationerna och de frågor som ställdes vid granskningen.'),
        'T-RED-02': (
            ' Bokslutsuppdraget samlar periodens resultat och tillgångar i årsredovisningen. Fiktiva kundfordringar '
            'eller osäkra lageruppgifter kan skapa en missvisande bild av ekonomin. Konsulten behöver begära '
            'underlag för värderingar och undersöka ägarlån som saknar tydlig dokumentation. Att posterna '
            'balanserar styrker inte deras existens. Företagsledningen ansvarar för lämnade uppgifter men '
            'byrån behöver följa upp motsägelser före leverans. Avstämningar av balanskonton och dokumenterad '
            'andragranskning ger information om vilka områden som kontrollerats. Det behöver framgå när '
            'kundens förklaring fortfarande saknar oberoende stöd. Sådana begränsningar påverkar hur uppdraget '
            'kan följas upp inför nästa bokslut.'),
        'T-RED-03': (
            ' Deklarationer bygger på redovisade resultat och lämnade uppgifter om avdrag. Osanna kostnader '
            'kan föras vidare utan att en formell skattemässig avstämning avslöjar affärens verkliga innehåll. '
            'Deklarationskonsulten behöver pröva större justeringars stöd och skilja privata utgifter från '
            'verksamhetens kostnader. Kundens dokumentation behöver visa vad transaktionerna avser. Felaktiga '
            'yrkanden ska utredas före inlämning och återkommande avvikelser följas upp. Skatteuppgifternas '
            'överensstämmelse med bokslutet ersätter inte kontroll av det bakomliggande materialet. Osäkerheter '
            'om faktiska leveranser kan kräva kompletteringar även när räkneoperationerna är korrekta. '
            'Handläggaren behöver dokumentera vilka antaganden som fortfarande återstår.'),
        'T-RED-04': (
            ' Löneuppdraget bygger på anställningsavtal och kundattesterade tidrapporter. Påhittade anställningar '
            'eller ändrade mottagarkonton kan ge obehöriga betalningar ett till synes legitimt ändamål. '
            'Lönekonsulten behöver kontrollera beställarens behörighet och uppmärksamma sena ändringar. '
            'Att arbetsgivaren attesterat timmarna bevisar inte att arbetet har utförts. Kontobyten behöver '
            'bekräftas genom en tidigare känd kontaktväg. Underlag för ovanliga ersättningar bör sparas '
            'så att efterföljande granskning kan följa hanteringen. Avvikande mönster mellan anställda och '
            'återkommande rättelser behöver diskuteras med kunden. Dokumentationen ska skilja kundens '
            'uppgifter från vad byrån själv faktiskt kunnat kontrollera.'),
        'T-SKATT-01': (
            ' Deklarationsarbetet kan beröras av upplägg där oriktiga avdrag döljer pengars ursprung. '
            'Rådgivaren behöver förstå beskattningsunderlagets koppling till verkliga transaktioner. '
            'Skatteberäkningar ska kunna följas till relevanta avtal och kundens beskrivning av affärssyftet. '
            'Oklara avdragsyrkanden behöver utredas innan de används i rådgivningen. Gränsöverskridande '
            'arrangemang kan kräva kompletterande handlingar för att förstå mottagare och betalningsändamål. '
            'Konsulten behöver skilja skatteplaneringens formella dokumentation från bevis om den ekonomiska '
            'innebörden. Utredningen behöver ange vilka antaganden som återstår och hur klientens '
            'förklaringar har jämförts med tillgängliga uppgifter.'),
        'T-BOLAG-01': (
            ' Bolagsbildning kan användas för att skapa juridiska strukturer som döljer verklig kontroll. '
            'Aktieteckning behöver därför förstås utifrån kapitalets ursprung och ägarnas avsikter. '
            'Konsulten behöver granska fullmakter och kontrollera vem som faktiskt företräder uppdragsgivaren. '
            'Ägarförändringar kan kräva nya handlingar om kontrollkedjan. Ett registrerat bolag visar '
            'inte att verksamhetens syfte är klarlagt. Osäkerheter om företrädare och finansiering '
            'behöver dokumenteras före fortsatt handläggning. Bildningshandlingar och överlåtelseavtal '
            'behöver vara förenliga med kundens förklaringar. Saknas förståelse för konstruktionen '
            'behöver konsulten begära kompletteringar och överväga uppdragets fortsatta hantering.'),
    }.get(t.tjanst, (' Uppdragets särskilda underlag behöver granskas mot kundens verksamhet och dokumenteras.' * 8))
    hot = list(t.hot)
    if del_id == 'sarbarheter':
        omraden = {}
        for id in tj.sarbarheter:
            omraden.setdefault(rb.sarbarheter[id].omrade, id)
        text = (inledning + ' Faktorn prövas lokalt mot dokumenterade uppdrag. Exponering och kompletteringsbehov i verksamhetens dokumenterade underlag '
                'behöver granskas. Ingen belagd kombination finns.')
        return AISvar(stycken=[AIStycke(typ='analys', referenser=[t.tjanst,id], text=text)
                               for id in omraden.values()], oklarheter=[])
    refs = {'hot':[t.tjanst,*hot], 'kontroller':[t.tjanst],
            'risknivaer':[t.tjanst,hot[0],tj.sarbarheter[0]], 'slutsatser':[t.tjanst,hot[0]]}
    extra = ' Kundkännedom, övervakning och utbildning behöver anpassas efter identifierade hot.' if del_id == 'slutsatser' else ''
    return AISvar(stycken=[AIStycke(typ='motivering' if del_id=='risknivaer' else 'analys',
        referenser=refs[del_id],text=inledning+tjansttext+extra)],oklarheter=[])
