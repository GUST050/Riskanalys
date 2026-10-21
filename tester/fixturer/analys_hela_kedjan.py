"""AB6:s syntetiska byrådata; inga riktiga kunder, attester eller API-anrop.

Basfallet har tolv scenarier. Utlandsvarianten har tjugo eftersom varje
relevant delat scenario får en egen lokal tillämpning för bokföringen.
"""
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path

from riskanalys.analys import modeller as m, provning as p
from riskanalys.analys.lagring import importera_belagg
from riskanalys.analys.utkast import forifyll_analys
from riskanalys.bedomning.motor import bedom
from riskanalys.dokument.delskrivning import skriv_tjanst
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.profil.hantering import skapa_profil
from riskanalys.profil.lagring import profilrevision
from riskanalys.profil.modeller import Byra
from riskanalys.profil.omfattning import harled_andelar
from riskanalys.regelverk.urval import valj
from tester.fixturer.m2 import komplett_profil, godkant_delsvar, PERIOD

DAG = date(2026,10,15)
TJANSTER = ('T-RED-01','T-RED-02','T-RED-03','T-RED-04')


@dataclass(frozen=True)
class SyntetisktFall:
    regelbas: object
    profil: object
    bedomning: object
    analys: m.Analyspaket
    byramapp: Path


def _profil(rb):
    byra = Byra(id='ab6-syntetisk-sju',regelpaket='RP-RED-VG',lan='Västra Götaland',datum=DAG)
    profil = komplett_profil(rb,skapa_profil(rb,byra))
    upp = dict(profil.uppgifter)
    for id,t in rb.tjanster.items():
        upp[t.erbjuds_falt] = upp[t.erbjuds_falt].model_copy(update={'varde':id in TJANSTER})
        prefix=t.erbjuds_falt.removesuffix('_erbjuds')
        for suffix,varde in (('_antal_kunder',24 if id in TJANSTER else 0),('_omsattning',750000. if id in TJANSTER else 0.)):
            if prefix+suffix in upp:
                upp[prefix+suffix]=upp[prefix+suffix].model_copy(update={'varde':varde})
    for id,varde in {'P-ORG.antal_anstallda':7,'P-ORG.verksamhetsstallen':1,
                     'P-KUND.antal_aktiva':60,'P-VERK.omsattning':3000000.,
                     'P-RISK.extern_kyc':True,'P-RISK.utkontraktering':False,
                     'P-GEO.sanktionsanknytning':True,
                     'P-VERK.skatteradgivning':False,'P-VERK.bolagstjanster':False,
                     'P-KANAL.antal_digitalt_underlag':48,'P-KANAL.antal_bankdata':36,
                     'P-KUND.antal_juridisk':60,'P-GEO.antal_utland_transaktion':6,
                     'P-VERK.antal_avbojanden':1}.items():
        upp[id]=upp[id].model_copy(update={'varde':varde})
    return harled_andelar(profil.model_copy(update={'uppgifter':upp}),rb)


def _belagg(byramapp,rot):
    texter={
        'mandat':'Syntetiskt uppdragsbrev: fyra redovisningstjänster för företag med verifierat mandat. Kunden beslutar betalningar; byrån registrerar och granskar underlagen.',
        'kontroll':'Syntetiskt stickprovsprotokoll: fakturor jämfördes med avtal, leveranser och avräkningar. Bokslutsposter, deklarationsjusteringar och löneändringar följdes till ursprungshandlingar. Bankavstämning ensam styrker inte affärens verklighet.',
        'bevakning':'Syntetisk lärdom: en avböjd kompletteringsbegäran visade att ofullständiga avräkningar kan dölja motparter. Noll rapporter i övrigt är inget frånvarobevis. Bevakning kontrollerad mot daterat underlag.',
        'rutin':'Syntetisk rutin R-AB6 version 1: ansvarig konsult utreder differenser vid varje månadsavslut och rapporterar olösta underlagsluckor till uppdragsansvarig före leverans.',
        'leverantor':'Syntetisk extern KYC-kontroll med dokumenterad identitet och ägarkedja. Byrån jämför resultatet med egna uppdragsuppgifter och behåller ansvaret för sin bedömning.',
    }
    belagg=[]
    for id,text in texter.items():
        fil=rot/f'{id}.txt';fil.write_text(text,encoding='utf-8')
        namn,summa=importera_belagg(byramapp,fil)
        belagg.append(m.Analysbelagg(id='ab6:'+id,dokument=namn,kontrollsumma=summa,datum=DAG,period=PERIOD))
    return tuple(belagg)


def _bekrafta(paket):
    return paket.model_copy(update={'tjanster':tuple(t.model_copy(update={'block':tuple(
        b.model_copy(update={'bekraftad_summa':p.blocksumma(paket,t.tjanst,b.nummer)})
        for b in t.block)}) for t in paket.tjanster)})


def skapa_fall(rb,rot: Path,*,variation=False) -> SyntetisktFall:
    """Skapa reella privata beläggsfiler och utvecklade ogranskade lokalsvar.

    Bindningens körnings-ID:n är syntetiska tills konsumentkedjan ersätter dem
    med riktiga manifest. Ingen granskning/fastställelse utförs här.
    """
    rot.mkdir(parents=True,exist_ok=True)
    profil=_profil(rb)
    b=bedom(rb,valj(rb,profil.byra.regelpaket,DAG,profil.byra.lan),profil)
    byramapp=rot/'byra'
    belagg=_belagg(byramapp,rot)
    bindning=m.Analysbindning(byra=profil.byra.id,profilrevision=profilrevision(profil),
        bedomningsmanifest='syntetisk-bedomning',utkastmanifest='syntetiskt-utkast',
        regelbas=rb.kontrollsumma,kallunderlag='syntetiska-kallreferenser',historik='syntetisk-historik',
        bedomningsdatum=DAG,modell='syntetisk-bindning-ersatts-vid-konsumentintegration')
    paket=forifyll_analys(rb,profil,b,bindning)
    gem=tuple(s.model_copy(update={'relevans':'relevant',
        'motivering':'Hotet prövas mot kundernas faktiska uppdrag och dokumenterade mandat; underlag kan användas för att dölja andra ändamål.',
        'belagg':('ab6:mandat',)}) for s in paket.gemensamma_scenarier)
    paket=paket.model_copy(update={'belagg':(*paket.belagg,*belagg),'gemensamma_scenarier':gem})
    motorresultat={t.tjanst:t for t in b.tjanster}
    tjanster=tuple(_tjanst(rb,t,gem,motorresultat[t.tjanst],variation=variation) for t in paket.tjanster)
    paket=_bekrafta(paket.model_copy(update={'tjanster':tjanster}))
    return SyntetisktFall(rb,profil,b,paket,byramapp)


def _tjanst(rb,t,gem,motorresultat,*,variation):
    id=t.tjanst
    reduktion=p.faktisk_reduktion(motorresultat)
    lok=tuple(s.model_copy(update={'relevans':'relevant',
        'motivering':'Tjänstens egna arbetsmoment kan ge felaktiga underlag ett legitimt utseende. Kontrollen prövas mot ursprungshandlingar och kvarstående begränsningar.',
        'belagg':('ab6:mandat',)}) for s in t.scenarier)
    kop=tuple(m.Scenariokoppling(scenario=s.id,tillampning='samma',scenariosumma=p.scenariosumma(s),bekraftad=True) for s in gem)
    delar=()
    if variation and id=='T-RED-01':
        delar=(m.Delanalys(id=id+':utland',rubrik='Utlandsflöden via PSP',
            arbetsmoment_och_befogenheter='Bokför avräkningar och jämför mottagna betalningar med försäljning. Mandatet omfattar inte kundens parallella bank eller beslut om betalning.',belagg=('ab6:mandat',)),)
        varianter=tuple(s.model_copy(update={'id':id+':lokal:'+s.id,'delanalyser':(delar[0].id,),
            'motivering':'Utlandsflödets betalningsled och dolda bakomliggande parter ger särskild insynsbegränsning i bokföringsmandatet.'}) for s in gem)
        lok=tuple(s.model_copy(update={'delanalyser':(delar[0].id,)}) for s in lok)+varianter
        kop=tuple(k.model_copy(update={'tillampning':'avviker','lokal_scenario':s.id,
            'motivering':'Utlandsflödet har ett separat arbetsmoment med avgränsad insyn.'}) for k,s in zip(kop,varianter))
    scenarier=(*lok,*(s for s in gem if not delar))
    kontroll=rb.kontroller[rb.tjanster[id].kontroller[0]]
    prov=[]
    for s in scenarier:
        rack=tuple(r.id for r in kontroll.rackvidd if r.tjanst==id and r.beskrivningsstatus=='beskriven' and set(s.hot)&set(r.hot))
        prov.append(m.Kontrollprovning(scenario=s.id,kontroll=kontroll.id,rackvidd=rack,
            tillampning='Ansvarig konsult jämför aktuellt stickprov med mandat, ursprungshandlingar och avvikelser före leverans.',
            utfall='Stickprovet är dokumenterat men bevisar inte att alla kundens transaktioner eller avsikter är kända.',
            belagg=('ab6:kontroll',),tackning='delvis' if rack else 'saknas',
            kvarstar='Betalningens existens styrker inte underlagets verkliga innebörd; externa betalningsled och kundens uppgifter kan fortfarande vara ofullständiga.'))
    saknad_tackning=any(c.tackning=='saknas' for c in prov)
    konflikt=reduktion and saknad_tackning
    gap=(m.Analysgap(id=id+':kontrollbrist',typ='kontrollbrist',status='accepterad_kvarstaende_risk',
        beskrivning='Katalogens räckvidd är okänd för tjänstens kontroll; dokumenterat stickprov ersätter inte källbunden räckvidd.',
        motivering='Känd begränsning redovisas med ansvar och frist. Detta godkänner inte motorns reduktion.',ansvar='Syntetisk metodansvarig',tidsfrist=date(2026,11,15)),) if saknad_tackning else ()
    if konflikt:
        gap+= (m.Analysgap(id=id+':metodkonflikt',typ='metodkonflikt',status='oppet',
            beskrivning='Motorn reducerar risk men stöd för kontrollens scenariotäckning saknas.',
            motivering='Utred källräckvidd och M1 före attest; motorns numeriska utfall bevaras.'),)
    if variation and id=='T-RED-02':
        gap+=(m.Analysgap(id=id+':leverantorskonflikt',typ='motstridigt_underlag',status='oppet',
            beskrivning='Leverantörens positiva ägarkedja motsägs av aktuellt kompletteringsunderlag.',
            motivering='Egen verifiering kan ännu inte lösa motsägelsen; fortsatt slutlig attest är blockerad.'),)
    forklaring={1:'Uppdrag, kunder och period framgår av uppdragsbrevet.',2:'Arbetsmomentens jämförbarhet är prövad.',
        3:'Avräkningar och kontoutdrag ingår i tjänstens underlag.',4:'Personalens kompetens och mandat behöver prövas.',
        5:'Bekräftad extern KYC används med eget ansvar.',6:'Varje kataloghot har en explicit relevant tillämpning.',
        7:'Kund, kanal, geografi och egen verksamhet prövas separat.',8:'Faktorer samverkar i underlagskedjan.',
        9:'Egen erfarenhet och aktuell bevakning finns dokumenterad.',10:'Relevanta scenarier kräver kontrollprövning.',
        11:'Relevant scenario lämnar dokumenterade begränsningar.',12:'Motorn redovisar faktisk reduktion.' if reduktion else 'Motorn redovisar ingen faktisk reduktion.',
        13:'PT-utfallet behöver lokal rimlighetsprövning.',14:'TF prövas självständigt även vid lagligt ursprung.',
        15:'Sanktionsanknytning finns bekräftad i intaget.',16:'Riskbeslut behöver rutin och uppföljning.'}
    block=tuple(x.model_copy(update={'aktivering':'aktiv','motivering':forklaring[x.nummer]}) for x in t.block)
    sartext={'kund':'Kundens uppgifter om affärsändamål jämförs med avtal; företrädarens egen uppgift är inte oberoende bevis.',
        'kanal':'Digitalt inlämnade handlingar kan sakna ursprungskontroll och därför dölja ändringar eller utelämnade flöden.',
        'geo':'Gränsöverskridande betalningar kan lämna oklarhet om bakomliggande parter; geografi ensam avgör inte utfallet.',
        'verk':'Sju medarbetare delar granskningsarbete; dokumenterad ersättare och ansvar behövs vid frånvaro och tidspress.'}
    sidor=tuple(s.model_copy(update={'relevans':'relevant','motivering':sartext.get(s.omrade, 'Tjänstens särskilda arbetsmoment och mandat behöver prövas mot uppdragets underlag och scenarier.'),
        'scenarier':(scenarier[0].id,),'belagg':('ab6:mandat',)}) for s in t.sarbarhetsprovningar)
    u=m.Uppdragsprovning(status='hanterbart',kompetens_och_insyn='Syntetiskt dokumenterad tjänstekompetens, ersättare och mandat för granskning av mottagna underlag.',
        motivering='Uppdragets dokumenterade avgränsning motsvarar tillgänglig kapacitet; nya betalningsled kräver förnyad prövning.',belagg=('ab6:mandat',))
    if variation and id in ('T-RED-03','T-RED-04'):
        u=u.model_copy(update={'handlingsalternativ':'begransa' if id=='T-RED-03' else 'forstark',
            'beslutsstatus':'beslutad' if id=='T-RED-03' else 'forslag',
            'ansvar':'Syntetisk uppdragsansvarig','datum':DAG,
            'motivering':'Det dokumenterade mandatet begränsar vilka underlag vi levererar; förstärkt specialiststöd föreslås före utökat uppdrag.'})
    return t.model_copy(update=dict(forfattare='Syntetisk Ada',block=block,scenarier=lok,scenariokopplingar=kop,
        exponering=t.exponering+' Syntetiskt mandat för löpande underlag och periodleveranser. PSP-avräkningar prövas som en del av affärsflödet, utan automatisk högriskklassning.',
        delningsmotivering='Arbetsmomenten har samma dokumenterade mandat och insyn i basfallet.' if not delar else 'Utlandsflödets separata avräkningskedja kräver egen tillämpning av varje relevant scenario.',
        delanalyser=delar,betalningsinsyn=m.Betalningsinsyn(status='bedomd',
            synliga_floden='Kundens mottagna kontoutdrag och avräkningsrapporter jämförs med tjänstens underlag.',
            insynsluckor='Ett parallellt bankengagemang och bakomliggande PSP-parter är inte fullständigt synliga.' if variation else 'Insynen omfattar mottagna uppdragshandlingar, inte alla kundens betalningsled.',
            avsandare_och_mottagare='Namngivna betalningsmotparter framgår av avtal i provet; bakomliggande parter måste utredas när avräkning bara visar förmedlaren.',
            underlagens_tillforlitlighet='Avräkningens summa jämförs med redovisning och ursprunglig handling; överensstämmelse ersätter inte förståelse av ändamålet.',
            motivering='Uppdraget innebär faktisk men begränsad insyn. Avstämning ensam styrker varken samtliga konton eller affärshändelsens riktighet.',belagg=('ab6:kontroll',)),
        uppdragsprovning=u,leverantorsmotivering='Extern KYC är ett underlag; byrån prövar resultat, täckning och begränsningar för varje uppdrag.',
        leverantorer=(m.Leverantorsprovning(id=id+':extern',omfattning='Identifiering och kontroll av dokumenterad ägarkedja.',
            leverantorens_kontroller='Daterad syntetisk registerkontroll med angivet urval och dokumenterade begränsningar.',
            egen_verifiering='Ansvarig konsult jämför identifierade företrädare och mandat med eget uppdragsunderlag.',
            brister_och_motstridigheter='Motstridig ägarkedja är fortfarande olöst.' if variation and id=='T-RED-02' else 'Ingen oförklarad motsägelse i det syntetiska urvalet; resultatet omfattar inte transaktionsändamål.',
            ansvar='Syntetisk ansvarig konsult behåller det lokala ansvaret.',belagg=('ab6:leverantor',)),),
        sarbarhetsprovningar=sidor,kontroller=tuple(prov),gap=gap,
        samverkan='Digital dokumentöverföring och begränsad motpartsinsyn kan tillsammans dölja osanna underlag. Tidspress vid periodslut förstärker risken för att motsägelser inte följs upp; dokumenterat ansvar begränsar men undanröjer inte osäkerheten.',
        erfarenhetsprovning='En syntetisk avböjd komplettering visade att avräkningsrapporter behöver följas till ursprungshandlingar. Lärdomen tillämpas i tjänstens underlagskontroll. Noll rapporter i övrigt utesluter inte PT eller TF.',
        erfarenhetsbelagg=('ab6:bevakning',),
        pt_motivering='Motorns PT-utfall prövas mot hur felaktiga underlag kan legitimera inkomster eller kostnader. Uppdragets begränsade insyn och kontrollens belagda räckvidd måste hållas isär; utred metodkonflikten före attest.',
        tf_motivering='TF prövas separat: även lagliga inkomster kan föras vidare till otillåtna ändamål. Mottagarkedja och ändamål kan vara ofullständiga trots korrekt bokföring; sanktionskontroll ersätter inte denna prövning.',
        reduktionsprovning='ej_reduktion' if not reduktion else 'metodkonflikt' if konflikt else 'motiverad',
        reduktionsmotivering=('Motorns faktiska reduktion bevaras. Källräckvidd och genomförande prövas scenario för scenario; okänd räckvidd ger en öppen metodkonflikt och inget tyst alternativt risksteg.' if reduktion else 'Motorn sänker inte tjänstens kvarstående nivå. Kontrollens begränsningar redovisas utan reduktionsanspråk.'),
        sektorsjamforelse='Tjänstens kundmix och mandat jämförs med sektorsbilden utan att byråns avgränsning automatiskt ändrar motorns nivå.',
        sanktioner='Bekräftad anknytning kräver lokal kontroll av aktuell träff och motpart; ingen kundåtgärd utförs av programmet.',
        slutsats='Behåll dokumenterad avgränsning och följ upp motsägelser före leverans. Olöst metod- eller underlagskonflikt hindrar slutlig attest; förslag är inte genomförande. Kundkännedom, övervakning och utbildning anpassas efter tjänstens scenarier.',
        rutinatgarder=(m.Rutinatgard(id=id+':rutin',scenarier=(scenarier[0].id,),rutin_id='R-AB6',rutin_version='1',rutinbelagg='ab6:rutin',
            atgard='Jämför avräkning med ursprungligt underlag och eskalera oförklarad differens till uppdragsansvarig.',
            status='foreslagen',ansvar='Syntetisk uppdragsansvarig',utlosare_eller_frekvens='Varje månadsavslut och vid ändrat betalningsled.',uppfoljning=date(2026,11,15)),)))


def _maxsvar(del_id,t):
    svar=godkant_delsvar(del_id,t)
    target={'hot':160,'sarbarheter':220}[del_id]
    current=sum(len(s.text.split()) for s in svar.stycken)
    if current>target:
        raise ValueError('Bastexten överskrider avsedd AI-budget.')
    extra=('Osäkerheter om ursprungshandlingar behöver dokumenteras så att senare granskning kan följa vilka uppgifter som saknades. '
        'En registrerad betalning berättar inte ensam vem som faktiskt styrde affären eller varför ersättningen lämnades. '
        'Kundens förklaring behöver kunna jämföras med dokumenterat mandat och tillgängliga externa uppgifter före fortsatt behandling. '
        'När sådant stöd saknas kvarstår behov av komplettering och ett uttryckligt lokalt ställningstagande till underlagens tillförlitlighet. '
        'Bristande dokumentation kan avse både mottagare och avsändare samt det ekonomiska sammanhanget bakom den synliga transaktionen. '
        'Särskild uppmärksamhet behövs när flera handlingar har samma ursprung och därför inte utgör oberoende bekräftelser. '
        'Periodavgränsning behöver framgå för att en tidigare dokumenterad kontroll inte ska förväxlas med aktuellt stöd. '
        'Dokumentationen behöver också skilja en föreslagen förbättring från en åtgärd som faktiskt har genomförts och följts upp. '
        'En leverantörs positiva etikett ersätter inte byråns förståelse av den tjänst som utförs för kundens räkning. '
        'Om betalningskedjan går genom en förmedlare behöver tillgängliga handlingar förklara kopplingen till den bakomliggande affären.')
    kvar=target-current
    meningar=[]
    for mening in extra.split('. '):
        mening=mening.rstrip('.')+'.'
        if len(mening.split())<=kvar:
            meningar.append(mening);kvar-=len(mening.split())
    avslut={1:'Uppföljning.',2:'Dokumentation behövs.',3:'Mandatet behöver dokumenteras.',
        4:'Underlag behöver prövas lokalt.',5:'Kvarstående osäkerheter behöver dokumenteras lokalt.',
        6:'Dokumenterade begränsningar behöver följas upp inför leverans.',
        7:'Underlagens tillförlitlighet behöver alltid prövas mot uppdragets mandat.',
        8:'Kvarstående osäkerheter behöver beskrivas och följas upp före leverans.'}
    for mening in reversed(tuple(avslut.values())):
        if len(mening.split())<=kvar:
            meningar.append(mening);kvar-=len(mening.split())
    if kvar:raise ValueError('Maxtexten behöver mer utvecklad saktext.')
    tail=' '.join(meningar)
    stycken=list(svar.stycken)
    stycken[-1]=stycken[-1].model_copy(update={'text':stycken[-1].text+' '+tail})
    return svar.model_copy(update={'stycken':stycken})


def skriv_fall(fall,*,skript='normal',maxord=False):
    """Kör den riktiga v6-skrivaren; analysen är uttryckligen inget argument."""
    svar=[]
    for _,t in tjanster_med_avsnitt(fall.bedomning):
        svar.extend((_maxsvar if maxord else godkant_delsvar)(d,t) for d in ('hot','sarbarheter'))
    if skript=='omforsok':svar.insert(0,'inte JSON')
    elif skript=='reserv':svar[:0]=['inte JSON']*3;svar.pop(3)
    elif skript!='normal':raise ValueError('Okänt syntetiskt svarsskript.')
    leverantor=Testleverantor(svar)
    resultat={id:skriv_tjanst(leverantor,fall.regelbas,fall.profil,t,id,effort='medium',
        personnamn=(),spara=lambda *args:None, formatversion="D-ARB-tjanst-v6") for id,t in tjanster_med_avsnitt(fall.bedomning)}
    return resultat,[a.model_dump(mode='json',by_alias=True) for a in leverantor.delanrop]


def privata_variationer(fall):
    """Ändra privata registrerade svar utan att ändra tillåtna AI-fakta."""
    a=fall.analys;t=a.tjanster[0]
    uppdateringar=(
        {'forfattare':'Syntetisk PRIVAT-NAMN-X','exponering':'PRIVAT-FRITEXT-X om kunders konfidentiella arbetsmoment.'},
        {'pt_motivering':'PRIVAT-PT-X','tf_motivering':'PRIVAT-TF-X','samverkan':'PRIVAT-SAMVERKAN-X','erfarenhetsprovning':'PRIVAT-LARDOM-X'},
        {'betalningsinsyn':t.betalningsinsyn.model_copy(update={'insynsluckor':'PRIVAT-BANK-X'}),
         'uppdragsprovning':t.uppdragsprovning.model_copy(update={'status':'kan_inte_hanteras','motivering':'PRIVAT-KAPACITET-X'})},
        {'leverantorer':tuple(l.model_copy(update={'brister_och_motstridigheter':'PRIVAT-LEVERANTOR-X'}) for l in t.leverantorer),
         'delanalyser':(m.Delanalys(id='privat-del',rubrik='PRIVAT-UTLAND-X'),)},
        {'sarbarhetsprovningar':tuple(s.model_copy(update={'motivering':'PRIVAT-SARBARHET-X'}) for s in t.sarbarhetsprovningar)},
    )
    for update in uppdateringar:
        yield replace(fall,analys=a.model_copy(update={'tjanster':(t.model_copy(update=update),*a.tjanster[1:])}))
    belagg=tuple(x.model_copy(update={'kontrollsumma':'sha256:'+'f'*64}) if x.dokument else x for x in a.belagg)
    yield replace(fall,analys=a.model_copy(update={'belagg':belagg}))
    beslut=m.Analysbeslut(tjanst=t.tjanst,revision=a.revision,underlagssumma=p.underlagssumma(a),
        svarssumma=p.svarssumma(a),godkand=False,namn='Syntetisk PRIVAT-GRANSKARE-X',roll='ansvarig',datum=DAG,
        kommentar='PRIVAT-NEJ-X',forfattare=t.forfattare,egen_granskning=False)
    yield replace(fall,analys=a.model_copy(update={'beslut':(beslut,)}))
    from riskanalys.drift.modellrisk import Modellbelagg, Modellriskunderlag, Modellfel
    ref=Modellbelagg(fil='privat-modellunderlag.txt',kontrollsumma='sha256:'+'e'*64)
    underlag=Modellriskunderlag(modellansvarig='Syntetisk PRIVAT-MODELLANSVARIG-X',
        modellbindning='sha256:'+'d'*64,rutin=ref,valideringsrapport=ref,projektrapport=ref,modellfiler=ref,
        utvarderad=DAG,nasta_genomgang=date(2027,10,15),feluppfoljning='PRIVAT-MODELLUPPFOLJNING-X',
        fel=(Modellfel(id='privat-fel',datum=DAG,beskrivning='PRIVAT-MODELLFEL-X',allvar='vasentligt',
            status='oppet',atgard_och_omprovning='Utred före användning',belagg=(ref,)),),
        godkand=False,beslutad_av='Syntetisk ansvarig',beslutsdatum=DAG)
    yield replace(fall,analys=a.model_copy(update={'modellrisk':underlag}))


def placera_privat_analys(fall):
    """Placera negativa syntetiska snapshots; detta är ingen attest/importväg.

    Testet behöver även kunna placera ett inaktuellt nej eller manipulerade
    beläggsbytes och bevisa att skrivaren aldrig försöker läsa dem.
    """
    import yaml
    from riskanalys.analys.lagring import ANALYSFIL
    fil=fall.byramapp/ANALYSFIL
    fil.parent.mkdir(parents=True,exist_ok=True)
    fil.write_text(yaml.safe_dump(fall.analys.model_dump(mode='json'),allow_unicode=True),encoding='utf-8')
    for b in fall.analys.belagg:
        if b.dokument and b.kontrollsumma=='sha256:'+'f'*64:
            (fall.byramapp/'analys/belagg'/b.dokument).write_text('Syntetiska PRIVAT-BELAGGSBYTES-X',encoding='utf-8')



@dataclass(frozen=True)
class BundenKedja:
    fall: SyntetisktFall
    bedomningsmapp: Path
    utkastmapp: Path
    granskningsmapp: Path
    regelrot: Path


def syntetisk_expertkopia(rot):
    """Endast tempkopia: syntetisk kundmetod, räckvidd och expertbeslut.

    Avsiktligt inget facit om den riktiga metodens scenariotäckning/M1.
    """
    import yaml
    from tester.m2.test_m2_kedja import expertkopia,kor
    from riskanalys.regelverk.laddning import ladda_regelbas
    regelrot,env=expertkopia(rot,'RP-RED-VG')
    fil=regelrot/'kataloger/kontroller.yaml';data=yaml.safe_load(fil.read_text())
    for c in data:
        for r in c.get('rackvidd',[]):
            if r['tjanst'] in TJANSTER:
                r['beskrivningsstatus']='beskriven'
                r['kan_belagga']='Syntetiskt antaget scenarioomfång enbart för positivt tekniskt kedjeprov; inget verkligt käll- eller M1-facit.'
                r['begransningar']='Syntetisk testförutsättning. Får aldrig överföras till riktig regelbas eller byrå.'
    fil.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False))
    out=rot/'syntetisk-omgranskning'
    kor(env,'regelbas','granskningsunderlag','--regelbas',str(regelrot),'--paket','RP-RED-VG','--datum',str(DAG),'--ut',str(out))
    mall=out/'granskningsmall.yaml';d=yaml.safe_load(mall.read_text())
    d.update(granskare='Syntetisk AB6-testgranskare',kompetens='Endast tekniskt syntetiskt kedjeprov',oberoende=True)
    for v in d['objekt'].values():v.update(beslut='verifierad',kommentar='Syntetiskt antagande i isolerad tempkopia, ingen verklig metodattest.')
    mall.write_text(yaml.safe_dump(d,allow_unicode=True))
    kor(env,'regelbas','importera-granskning',str(mall),'--regelbas',str(regelrot))
    return regelrot,ladda_regelbas(regelrot)


def _positiv_bankavstamning(rb, paket):
    """Den positiva syntetiska kopian prövar C-07 för felbetalning i bokföringen.

    C-TJ-01 bär inte H-MOD-01:s sänkning. Den vanliga ogranskade fixturen
    behåller sina luckor; detta tillägg används bara efter explicit syntetisk signering.
    Delvis täckning bär inte ett helt kontrollavdrag, så den signerade kopian anger
    uttryckligen tillräcklig täckning där fixturen annars har delvis.
    """
    scenarier = {s.id: s for s in paket.gemensamma_scenarier}
    analyser = []
    for t in paket.tjanster:
        t = t.model_copy(update={'kontroller': tuple(
            c.model_copy(update={'tackning': 'bedomd_tillracklig'}) if c.tackning == 'delvis' else c
            for c in t.kontroller)})
        if t.tjanst == 'T-RED-01':
            lokala = {**scenarier, **{s.id: s for s in t.scenarier}}
            rack = tuple(r.id for r in rb.kontroller['C-07'].rackvidd
                         if r.tjanst == t.tjanst and r.beskrivningsstatus == 'beskriven' and 'H-MOD-01' in r.hot)
            assert rack, 'Den positiva kopian kräver beskriven bankavstämning för H-MOD-01.'
            tillagg = tuple(c.model_copy(update={'kontroll': 'C-07', 'rackvidd': rack, 'tackning': 'bedomd_tillracklig',
                'tillampning': 'Syntetiskt dokumenterad bankavstämning: konsulten utreder felbetalning och återföring till annat konto.'})
                for c in t.kontroller if c.scenario in lokala and 'H-MOD-01' in lokala[c.scenario].hot)
            t = t.model_copy(update={'kontroller': (*t.kontroller, *tillagg)})
        analyser.append(t)
    return paket.model_copy(update={'tjanster': tuple(analyser)})


def bygg_bunden_kedja(rb,rot,*,regelrot,godkann=False,variation=False,formatversion=None):
    """Verkliga manifest och bindningar; godkann=True ENDAST syntetisk kopia."""
    from riskanalys.analys import lagring as l
    from riskanalys.profil.lagring import spara_profil
    from riskanalys.bedomning.korning import kor_bedomning,las_bedomning
    from riskanalys.dokument.skrivning import kor_skrivning
    from riskanalys.drift.historik import registrera_handelse,Handelse
    from riskanalys.granskning.korning import kor_granskning
    f=skapa_fall(rb,rot,variation=variation)
    from tester.fixturer.skrivsvar_v7 import med_verksamhetsval
    f=replace(f,profil=med_verksamhetsval(rb,f.profil))
    from riskanalys.dokument.skrivversion import AKTUELL_SKRIVVERSION, V8
    if (formatversion or AKTUELL_SKRIVVERSION)==V8:
        from riskanalys.intag.fordelning import faltkoppling,underlagsbindning
        upp=dict(f.profil.uppgifter)
        if godkann:
            # Explicit syntetiska, aktiva faktorbaser för det positiva V8-provet.
            for id in ('P-GEO.antal_utland_agare','P-KUND.antal_riskbransch','P-KUND.antal_kontant'):
                upp[id]=upp[id].model_copy(update={'varde':6})
            f=replace(f,profil=harled_andelar(f.profil.model_copy(update={'uppgifter':upp}),rb))
            upp=dict(f.profil.uppgifter)
        for id,u in upp.items():
            if faltkoppling(rb,id) and f.profil.ar_bekraftad(id):
                upp[id]=u.model_copy(update={'underlagsbindning':underlagsbindning(rb,f.profil,id)})
        f=replace(f,profil=f.profil.model_copy(update={'uppgifter':upp}))
    spara_profil(f.byramapp,f.profil)
    bm=kor_bedomning(f.byramapp,rb);b=las_bedomning(bm)
    from tester.fixturer.skrivsvar_v7 import tjanstspecifikt_svar_v7
    svar=[tjanstspecifikt_svar_v7(rb,f.profil,t,id) for id,t in tjanster_med_avsnitt(b)]
    um=kor_skrivning(f.byramapp,rb,Testleverantor(svar),effort='medium', **({'formatversion':formatversion} if formatversion else {}))
    registrera_handelse(f.byramapp,Handelse(datum=date(2026,10,1),typ='utvärdering',beskrivning='Syntetisk årlig utvärdering av tjänster och mandat.'))
    registrera_handelse(f.byramapp,Handelse(datum=date(2026,10,8),typ='uppdatering',beskrivning='Syntetisk separat komplettering om betalningsled; flyttar inte årsfristen.'))
    a=f.analys
    if godkann:
        if not (regelrot/'granskning.yaml').is_file():raise ValueError('Positiv kedja kräver uttryckligt signerad syntetisk tempkopia.')
        a=_positiv_bankavstamning(rb,a)
        from tester.fixturer.v6_analys import _modellunderlag
        a=a.model_copy(update={'modellrisk':_modellunderlag(f.byramapp,rb,rot/'syntetisk-modellrapport',DAG)})
    a=_bekrafta(a.model_copy(update={'bindning':l.bygg_bindning(f.byramapp,rb,bm,um)}))
    cas=l.spara_analys(f.byramapp,a,forvantad_summa='')
    if godkann:
        assert not p.analysbrister(rb,f.profil,b,l.las_analys(f.byramapp)),p.analysbrister(rb,f.profil,b,l.las_analys(f.byramapp))
        for i,t in enumerate(a.tjanster):
            a=l.las_analys(f.byramapp)
            beslut=m.Analysbeslut(tjanst=t.tjanst,revision=a.revision,underlagssumma=p.underlagssumma(a),
                svarssumma=p.svarssumma(a),godkand=True,namn=t.forfattare if i%2==0 else 'Syntetisk Bo',roll='FfR',datum=DAG)
            cas=l.registrera_analysbeslut(f.byramapp,rb,beslut,forvantad_summa=cas,bedomningsmapp=bm,utkastmapp=um)
    a=l.las_analys(f.byramapp)
    gm=kor_granskning(f.byramapp,rb,DAG)
    if godkann:
        from riskanalys.granskning.korning import las_granskning
        from riskanalys.faststallelse.sakgranskning import registrera_sakgranskning,spara_sakgranskningar
        d,fynd=las_granskning(gm)
        assert not fynd,fynd
        poster=()
        from riskanalys.dokument.rapportpaket_v8 import las_presentation
        presentation=las_presentation(gm,b,f.profil,regelbas=rb) if d.formatversion=='D-ARB-tjanst-v8' else None
        for avsnitt in d.avsnitt:
            poster=registrera_sakgranskning(poster,d,f.profil,avsnitt.id,True,'FfR','Syntetisk dokumentgranskare',DAG,analysbindning=cas,presentation=presentation)
        spara_sakgranskningar(f.byramapp,poster)
    return BundenKedja(replace(f,bedomning=b,analys=a),bm,um,gm,regelrot)


def negativt_underlag(a,typ):
    """En saklig negativ mutation, bevarade motorfakta och faktisk modellfilbas."""
    from riskanalys.drift.modellrisk import Modellfel
    if typ=='saknad_modell':return a.model_copy(update={'modellrisk':None})
    if typ=='inaktuell_modell':return a.model_copy(update={'modellrisk':a.modellrisk.model_copy(update={'nasta_genomgang':DAG})})
    if typ=='modellfel':
        fel=Modellfel(id='syntetiskt-vasentligt',datum=DAG,beskrivning='Syntetiskt öppet väsentligt modellfel',
            allvar='vasentligt',status='oppet',atgard_och_omprovning='Utred före fortsatt användning.',belagg=(a.modellrisk.rutin,))
        return a.model_copy(update={'modellrisk':a.modellrisk.model_copy(update={'fel':(fel,)})})
    t=a.tjanster[0]
    if typ=='kapacitet':t=t.model_copy(update={'uppdragsprovning':t.uppdragsprovning.model_copy(update={'status':'kan_inte_hanteras','handlingsalternativ':'fortsatt'})})
    elif typ=='leverantor':
        t=t.model_copy(update={'leverantorer':tuple(l.model_copy(update={'brister_och_motstridigheter':'Syntetisk olöst ägarmotsägelse.'}) for l in t.leverantorer),
            'gap':(*t.gap,m.Analysgap(id='leverantorskonflikt',typ='motstridigt_underlag',beskrivning='KYC-resultat motsäger aktuellt eget underlag.',motivering='Olöst efter egen verifiering.'))})
    elif typ=='reduktion':
        t=t.model_copy(update={'kontroller':tuple(c.model_copy(update={'tackning':'saknas','rackvidd':(),
            'tillampning':'Enbart bankavstämning av synligt konto.', 'kvarstar':'Falsk faktura och bakomliggande affär styrks inte av bankavstämning.'}) for c in t.kontroller),
            'reduktionsprovning':'metodkonflikt','gap':(*t.gap,m.Analysgap(id='bankmetodkonflikt',typ='metodkonflikt',
                beskrivning='Enbart avstämning stöder inte faktisk reduktion för falska underlag.',motivering='Motorns nivå bevaras, attest stoppas.'))})
    else:raise ValueError('Okänt negativt syntetiskt fall.')
    return a.model_copy(update={'tjanster':(t,*a.tjanster[1:])})


def psp_jamforelse(fall):
    t=fall.analys.tjanster[0]
    normal=t.model_copy(update={'betalningsinsyn':t.betalningsinsyn.model_copy(update={
        'synliga_floden':'Syntetisk PSP-avräkning följs till avtal och förstått normalt abonnemangsflöde.',
        'insynsluckor':'Urvalet styrker förstådd mottagarkedja; ytterligare flöden kan ligga utanför mandatet.'})})
    osaker=t.model_copy(update={'betalningsinsyn':t.betalningsinsyn.model_copy(update={
        'insynsluckor':'Bakomliggande gåvogivare och ändamål i PSP-ledet är ofullständiga.'}),
        'scenarier':tuple(s.model_copy(update={'motivering':s.motivering+' Omfattning och ändamål är osäkra; plattformsnamnet bevisar inte brott och omfattningen kan inte skattas från detta prov.'}) for s in t.scenarier)})
    return tuple(replace(fall,analys=fall.analys.model_copy(update={'tjanster':(v,*fall.analys.tjanster[1:])})) for v in (normal,osaker))


DEMO_TEXTER={
    'T-RED-01':(
        'Bokföringsuppdraget kan utnyttjas för att ge påhittade affärshändelser ett trovärdigt underlag. En faktura kan motsvara en verklig bankbetalning utan att den angivna varan har levererats eller tjänsten utförts. Intäkter som bokförs från en betalningsförmedlares avräkning kan dölja vem som ursprungligen betalade och vilket ändamål betalningen hade. Återbetalningar, rättelser och ägarnas privata utlägg behöver därför förstås i sitt affärsmässiga sammanhang. TF kan beröra även pengar med lagligt ursprung när en mottagare eller ett senare betalningsled har annat ändamål än det redovisade. Bokföraren behöver skilja den registrerade transaktionen från vad underlagen faktiskt visar om motpart och ekonomisk innebörd.',
        'Kundens egen beskrivning av affären är en möjlig informationskälla men kan sakna oberoende stöd. I den digitala inlämningskanalen kan ursprungshandlingar ersättas av sammanställningar som inte visar alla betalningsled. Geografiska uppgifter behöver sättas i relation till den faktiska affären och motparten; ett landsnamn säger inte ensamt vad transaktionen avser. Byråns arbetsfördelning och tid för frågor påverkar möjligheten att följa upp återkommande differenser före periodavslut. Om bokföraren bara ser en avräkning kan både mottagarkedjan och kopplingen till kundens försäljning vara ofullständiga. Dokumentationen behöver ange vilka handlingar som saknas och vad som kunnat jämföras med avtal, leveranser och redovisning. Ett avstämt konto ersätter inte denna förståelse.'),
    'T-RED-02':(
        'Bokslutsarbetet kan ge osäkra eller uppdiktade tillgångar en auktoritativ presentation. Kundfordringar kan sakna verkliga leveranser, lager kan vara felvärderat och ägarlån kan dölja andra betalningsändamål. Att balansräkningen stämmer aritmetiskt visar inte att posterna finns eller har den innebörd som företagsledningen uppger. Periodiseringar och bokslutsverifikationer kan också flytta ekonomiska händelser mellan perioder så att deras ursprung blir svårare att följa. TF kan beröras när tillgångar eller lagliga medel används för vidare finansiering genom en oklar mottagarkedja. Konsultens analys behöver därför följa större eller ovanliga poster till ursprungligt underlag och beskriva osäkerheter som finns kvar inför årsredovisningen.',
        'Kundberoendet är tydligt när värderingar och uppgifter om lager eller fordringar kommer från företagsledningen. Elektroniska sammanställningar kan sakna spårbarhet till de handlingar som låg bakom beloppen. För tillgångar eller fordringar med anknytning till andra länder kan tillgången till bekräftelser och förståelsen av affärsförhållandet vara otillräcklig. Byråns egen verksamhet behöver ha dokumenterat ansvar för svåra värderingsfrågor och för frågor som kvarstår när leveransfristen närmar sig. En tidigare granskad ingående balans bevisar inte att årets förändringar är riktiga. Det behöver framgå vilka uppgifter som har kontrollerats mot oberoende material och vilka som fortfarande bygger på kundens förklaring. Motsägelser behöver utredas före ett lokalt ställningstagande till fortsatt hantering.'),
    'T-RED-03':(
        'Deklarationsuppdraget kan föra vidare oriktiga kostnader eller affärsbeskrivningar till ett formellt korrekt skatteunderlag. Ett avdragsyrkande kan bygga på en faktura som inte avser den redovisade verksamheten. Skattemässiga justeringar kan också presenteras utan begripligt samband med avtal, leveranser eller betalningar. Att uppgifterna överensstämmer med bokslutet visar endast att samma uppgifter används, inte att det bakomliggande förloppet är styrkt. Vid gränsöverskridande affärer kan syfte och mottagare vara svåra att klarlägga. TF kan förekomma genom överföring av lagligt intjänade medel till andra ändamål. Deklarationskonsulten behöver därför förstå ekonomisk innebörd och redovisa när underlaget fortfarande kräver frågor till kunden.',
        'Kundens val av uppgifter och förklaringar påverkar vilka avdrag och transaktioner konsulten kan pröva. En digital deklarationsbilaga kan innehålla korrekta beräkningar trots att stöd för själva affären saknas. Geografisk anknytning behöver bedömas utifrån avtalsparter, betalningsled och tillgängliga handlingar, med tydlig skillnad mellan känt och okänt. I byråns arbete kan återkommande deklarationsfrister göra det svårt att hinna utreda avvikande poster om ansvaret för kompletteringar är oklart. En avgränsad deklarationstjänst ger inte automatiskt insyn i samtliga kundkonton eller bakomliggande verksamhetsförhållanden. Mandatet behöver därför beskriva vilket underlag som granskas och när ytterligare kompetens eller komplettering behövs. Dokumenterad osäkerhet ska kunna följas till den berörda justeringen även efter inlämningen.'),
    'T-RED-04':(
        'Lönehanteringen kan utnyttjas för betalningar till påhittade anställda eller för ersättningar som inte motsvarar utfört arbete. Ändringar av mottagarkonton och sena instruktioner kan ge en annan part tillgång till pengar som ser ut att vara vanlig lön. Kundattesterade tidrapporter visar vem som lämnat uppgiften men styrker inte ensamma att arbetet har utförts. Ovanliga förmåner, utlägg och rättelser behöver förstås mot anställningsvillkor och faktiska arbetsförhållanden. TF kan beröra lagliga löneutbetalningar som senare används för finansiering genom andra mottagare. Lönekonsulten behöver därför kunna följa beställarens behörighet, underlagets ursprung och ändringarnas innebörd utan att framställa en godkänd lönekörning som bevis för hela betalningskedjan.',
        'Kundens arbetsledare kan vara den enda källan till uppgifter om arbetstid och ersättningar. Digital överföring av löneunderlag skapar ett behov av att förstå vem som gjort ändringar och vilken attest som faktiskt finns. För anställda eller betalningar med utlandsanknytning kan kunskap om mottagare och ekonomiskt sammanhang vara begränsad. Byråns egen bemanning behöver möjliggöra frågor även under tidspress inför lönekörning, med en känd ersättare när ansvarig konsult saknas. Ett konto som tidigare har använts behöver inte vara rätt mottagarkonto efter en ändring. Dokumentationen behöver skilja kundens instruktion från det som byrån själv har kunnat bekräfta. Återkommande avvikelser och brister i mandat behöver därför kunna följas upp mellan löneperioder.'),
}


def demosvar(del_id,t,rb):
    """Handskrivna förberedda exempel, inte ett faktiskt AI-svar eller läsprov."""
    from riskanalys.dokument.modeller import AISvar,AIStycke
    text=DEMO_TEXTER[t.tjanst][0 if del_id=='hot' else 1]
    refs=[t.tjanst,*(t.hot if del_id=='hot' else rb.tjanster[t.tjanst].sarbarheter)]
    return AISvar(stycken=[AIStycke(typ='analys',text=text,referenser=refs)],oklarheter=[])
