# Kravstöd och tjänsteexponering i Riskanalys

Revision 3, den 21 oktober 2026. Bygger på granskningen i `8915f0d` mot kodbas `288fa66` och den uppföljande granskningen i chatten. Python-miljö, erbjudandeövergångar/rättelser, historikbindning och gemensamt faktorurval är förtydligade. Designunderlag för den beställda implementeringsplanen. Inga riskregler, källstatusar eller produktfiler ändras genom dokumentet.

## Syfte och avgränsning

Programmet ska stödja kedjan **hot och sårbarheter, analyserade med riskfaktorer, till en motiverad risk per tjänst**. Befintlig scenariomotor, lokal analys i 16 block, fem interna sårbarhetsområden, källregister, rapport V8, egen erfarenhet och utvärderingshistorik återanvänds. Sexdelningen är en karta över kravens placering, inte sex nya programmoduler.

Första leveransen ska ge en verifierad kravkarta och belagda förbättringar i befintliga flöden. Kravkartan får minska, avgränsa eller skjuta upp föreslagna uppgifter när befintliga funktioner räcker. Registrering av enskilda kunduppdrag är inte ett krav. Befintliga sammanställningar får användas; deklarerade kombinationsgrupper kompletterar dem där behovet beläggs. Ett framtida frivilligt uppdragsregister ingår inte.

## Kontrollerad kodbas

- Repo: `GUST050/Riskanalys`, gren `feat/steg-1-3`.
- Låst kodbas: `288fa6650ea400fda04cdcef965f8ac17adc3575`.
- Granskning och kontrollerad fjärr-HEAD: `8915f0d154416bcbd482b2b926a6523e7f9405d8`. Detta är ett dokumentationscommit ovanpå kodbasen.
- Kodbasen innehåller 13 commits efter den äldre basen `fc82b6754537cd3de0eee74dcb2a32b82c1a39a9`: de tre tidigare rättningarna plus tio senare commits med metodalternativ, åtta jämförelsepar, rapportmätning, gemensamt faktaunderlag, deterministisk källnot och beräkningsspår i B1. Historik och centrala ändringar har lästs, men inga produkttester eller rapportmätningar har körts i denna planrevision.
- Aktuell lokal arbetskopia i en annan chatt har inte använts eller ändrats. Genomförandet kontrollerar arbetsstatus mot den låsta kodbasen.

Alla 13 commits ska verifieras och återanvändas. Den nya planen ersätter återstående planering för kravkarta, tjänsteexponering och metodprövning; den äldre planen behålls som historik. Huvudordningen är 0 → 1 → 3a → 4 → 5 → valfri 3b → 6 → 7. Uppgift 2 kompletterar befintliga metodunderlag efter 1 och före berörda beslut i 6; den blockerar inte 3a.

## Krav och källgräns

De 36 punkterna kommer från användarens `Kravsammanställning allmän riskbedömning.docx`, daterad 19 oktober 2026. Numren är sammanställningens nummer, inte paragrafnummer.

| Del i kravkartan | Punkter |
|---|---|
| Bedömningens ram och omfattning | 5–6 |
| Verksamhetsunderlag, tjänster, källor och egen erfarenhet | 4, 8–9, 13, 15–16 |
| Tjänstevis analys av PT/TF, hot, sårbarheter och samverkan | 3, 10–12, 14, 17–22, 25–26 |
| Motiverade risknivåer och villkorad effektprövning | 1, 23–24, 34–36 |
| Skriftlig dokumentation, rutiner, information och tillsyn | 2, 7, 31–33 |
| Utvärdering och uppdatering | 27–30 |

Primärt underlag är Länsstyrelsens tillhandahållna MHTML och motsvarande [webbvägledning](https://www.lansstyrelsen.se/vastra-gotaland/samhalle/betalning-ekonomi-och-pengar/forhindra-penningtvatt-och-finansiering-av-terrorism/gor-en-allman-riskbedomning.html), [penningtvättslagen](https://www.riksdagen.se/sv/dokument-och-lagar/dokument/svensk-forfattningssamling/lag-2017630-om-atgarder-mot-penningtvatt-och_sfs-2017-630/) och 14FS 2024:11, särskilt 2 kap. 1–3 §§. Dessa lästes vid föregående kravavstämning i samma chatt. Exakt aktuell föreskrift för respektive län ska hämtas ur projektets daterade regelpaket och verifieras vid genomförandet; författningsnummer från den inklistrade diskussionen är inte självständigt verifierade för alla län.

Lag, föreskrift, vägledning och projektets metodval ska vara skilda i kravkartan. En viss matris, numerisk vikt, maxregel eller ett stegs avdrag är inte ett krav från webbvägledningen. Planerade funktioner och deklarerade grupper är projektets sätt att stödja analysen.

## Data och analys

### Tjänster och förändringar

Befintligt ja/nej-fält för att en tjänst erbjuds behålls för aktuell verksamhet. En separat lokal `Tjansteplan` beskriver en ny tjänst eller förändring och dess avsedda förutsättningar. Detta är en planpost i den befintliga profilen, inte ett nytt riskresultat eller en kundriskmodell.

Planen innehåller ID, tjänst-ID, förändringstyp, beskrivning, eventuellt avsett införandedatum och strukturerade planeringsuppgifter med samma evidensmodell som `Uppgift`. Förändringstyper är `ny_tjanst`, `vasentligt_andrad_tjanst`, `ny_marknad` och `annan_forandring`. Framtida införandedatum är tillåtet; ett genomfört utvärderingsdatum får inte vara framtida.

**3a är minimileveransen:** planpost och sakligt dokumenterad utvärdering av den allmänna riskbedömningen med hänsyn till förändringen. Utvärderingen behandlar berörda hot, sårbarheter och riskfaktorer, konsekvenser för riskbild/rutiner samt beslut om uppdatering eller motiverat behållande. Ingen ny motorbedömning krävs för registrering av den genomförda utvärderingen. Detta är ett programstöd; en ifylld post bevisar inte ensam att verksamhetens sakliga skyldighet är fullgjord.

**3b är en frivillig senare etapp:** samma motor kan ge en orientering för en plan, redovisad i ett kort separat planunderlag. Ingen generell flytt av V8-kedjans mappreferenser och ingen ny kedja för AI-skrivning, lokal analys och fastställelse ingår. Före D3 bygger orienteringen på katalogens grundnivåer och byråns befintliga faktorer som om tjänsten erbjöds; planens egna uppgifter redovisas som antaganden och påverkar inte nivån. Begränsningen måste stå intill resultatet. Originalprofil och aktuell bedömning förblir oförändrade. Befintlig kontrollverkan får inte tillskrivas en ännu inte införd tjänst.

Planpostens tillåtna fält omfattar måltjänstens egna fält och utvalda relevanta byråfält, även geografi inför ny marknad. ID och datatyp valideras mot regelbasen. Roll-/personfält, andra tjänsters erbjudanden, härledda andelar och kontrollutfall/effekt får inte ersättas av planantaganden. Att ett planvärde får dokumenteras betyder inte att motorn redan använder det; en numerisk anslutning kräver exakta fält och regler i D3 eller annat berört metodbeslut.

Utvärdering inför förändring binds till berörd plan, relevanta sakuppgifter och regelbasens identitet. Bindningen omfattar inte den förväntade ändringen av erbjudandeflaggan eller historikhändelsen själv. En gammal eller orelaterad årlig utvärdering är inte bevis för att just förändringen prövats, och en begränsad planutvärdering får inte automatiskt skjuta upp hela årsgenomgången. Utvärdering innebär inte att tjänsten börjar erbjudas. CLI och webb använder samma kontroll inför ändring av registrerat erbjudande. Första kartläggning av redan befintliga tjänster skiljs från ett nytt införande; historiska paket kräver ingen retroaktiv planpost. Stödet kan inte hindra arbete som utförs utanför programmet.

Programmets uttryckliga övergångsregel är att bekräftat giltigt nej → ja kräver plan och bunden utvärdering. Okänt → ja behandlas som kartläggning, utom när en registrerad plan eller ett uttryckligt införande redan anger att det är en förändring. Jämför ursprunglig sparad profil med slutligt transaktionsresultat; ett mellanliggande okänt får inte dölja ett nej. En belagt felaktig nej-registrering får rättas via särskilt rättelseläge med källa, motivering, ansvarig, datum och bevarade före-/efteruppgifter. Rättelsen registreras i historiken och ersätter inte andra krav på förnyad analys. Väsentliga ändringar och nya marknader prövas även om erbjudandet redan är ja.

Den befintliga analysbindningen omfattar hela historikfilens kontrollsumma. En ny planutvärdering eller rättelse gör därför aktuellt analyspaket och dess analysbeslut inaktuella. Den konservativa regeln behålls: beslutens historik sparas men bindning och sakprövning förnyas före ny fastställelse. Användaren får en tydlig förklaring av följden. Enbart historikändring ger inte automatiskt ny numerisk risk; ändrad profil kräver däremot ny aktuell bedömning enligt befintlig aktualitetskontroll. Planens egen bindning, som undantar införandeflaggan, ska inte förväxlas med detta bredare aktualitetskrav för hela analysen.

### Deklarerade kombinationsgrupper

En grupp avser en tjänst, en angiven population (`kunder` eller `uppdrag`) och en avgränsning. Den innehåller beskrivning av samförekommande egenskaper, analysreferenser till befintliga sårbarheter, antal och bas med källor/bekräftelse/period enligt `Uppgift`. Ett enda `population` gäller både täljare och nämnare. Manuell registrering bekräftar enheten för båda talen; separat enhetstaggade importuppgifter med enhetskonflikt får inte godtas. Programmet kan inte bevisa en källas verkliga enhet ur ett tal eller fri text.

Referenserna till sårbarhetskatalogen är analyskopplingar. De betyder inte i sig att en katalogposts portföljtröskel är uppfylld av gruppens medlemmar. Ingen riskregel får tolka gruppens fritext. D3/D4/D9 måste ange hur deklarerade sakförhållanden kan användas numeriskt och vilka ytterligare typade uppgifter det kräver.

Bekräftat antal 0 skiljs från okänt antal. Antal och bas måste avse samma population, enhet, avgränsning och period. Antal ska vara heltal inom 0–bas; bas 0 betyder inte automatiskt låg risk. Kundantal får inte användas som nämnare till ett antal uppdrag. Uppskattningar märks uttryckligen och ger inte belagt reduktionsstöd.

Två marginaltal bevisar inte ett visst överlapp. Grupper summeras inte till en unik total i första leveransen eftersom de kan överlappa. En liten betydelsefull grupp ska återges även om den inte ändrar tjänstens högsta etikett. Saknade, inaktuella och motstridiga uppgifter redovisas öppet.

Ny eller ändrad grupp ändrar profilrevisionen och kräver ny aktuell bedömning och förnyad berörd analysbindning. Det gäller även när risketiketterna inte ändras. Historiska profiler utan grupper behåller sina tidigare payloads och kontrollsummor.

### Samma samband i motor och rapport

Rapporten ska tillsammans med B1 visa vilken uppgift eller grupp som är relevant, vilken sårbarhet den beskriver, hur hotet kan utnyttja den, berörd metodregel, numeriskt utfall och osäkerhet. Gemensam mekanism och källa skrivs en gång per entydig faktor och definitionsversion i befintligt D-ARB.5 via `dokument/gemensamt_v8.py`. Varje tjänst återger endast lokal tillämpning, avvikelse och avgörande skäl. Fulla beräkningstabeller, faktorregister och kontrollspår förblir i B1 enligt `288fa66`. Befintliga `metodmotivering`, `kallhanvisningar`, lokala prövningar och deterministiska källnoter återanvänds.

Det gemensamma avsnittet begränsas till unionen av faktorer som används i minst en bekräftat erbjuden tjänsts motorscenarier. För äldre resultat utan scenarier används tillämpade sårbarheter i erbjudna tjänster. Katalogposter som inte aktiverats fyller inte D-ARB.5; avgränsningar och ej tillämpliga faktorer bevaras i sårbarhetsprövningen/B1. En gemensam definition betyder inte att faktorn gäller alla tjänster. Preliminär aktivering beskrivs som sådan i den lokala tillämpningen.

Fem interna områden (`kund`, `kanal`, `geo`, `verk`, `tjanst`) ska fortsatt prövas. Det är programmets indelning; webbvägledningens fyra uttryckliga riskfaktorområden blir inte fem rättsliga krav genom denna indelning.

Att inget automatiskt påslag aktiveras får inte beskrivas som att exponeringen saknas. En kodskriven förklaring ska skilja observation, sårbarhetsmekanism, metodantagande och utfall. Samma ID:n ska kunna följas i intag, analys, motorspår och rapport utan en ny fristående bedömningsmodell.

Mät före och efter med befintligt `docs/research/verktyg/rapportmatning.py`, samma H7.1-profiler och frysta AI-svar. Redovisa ord i läsrapport/B1 och ordagrann upprepning separat från likartad struktur. Ökningar förklaras; inget hårt ordtak införs. Tidigare uppmätta ordantal är historik, inte denna revisions testresultat.

## Metodbeslut före ändrad beräkning

D3, D5, D6, D8 och D9 återanvänds. D4 styr evidensgränsen för överlapp; D1/D2/D7 tas med när relevans eller dimensionskoppling påverkas. Använd det befintliga `docs/superpowers/reviews/2026-10-21-beslutsformular-jamforelsepar.md` med åtta jämförelsepar, svarsmall och precisering per riskmått. Plan- och gruppfallet läggs till som par 9 och 10 i samma formulär. Befintliga alternativ och prov är inte beslut; skapa inget konkurrerande protokoll.

Varje beslut ska ange ansvarig, verklig granskare, datum, källversioner, behåll/ändra och skäl, exakta fält/populationer/perioder, berörda regler och förväntat facit per kontrast. Ingen ny riskvikt, tröskel, maxregel, TF-konsekvens eller kontrollreduktion beslutas av denna plan.

Gruppregistrering och tydligare redovisning kan införas utan ny riskberäkning. Anslutning till motorns nivåer väntar på ett tillräckligt preciserat beslut. Ett oförändrat resultat är tillåtet när sakskälen förklaras. Målet är inte lägre eller mer varierade etiketter.

## Två genomgående prov

1. **Planerad tjänst:** tjänsten erbjuds inte, en planpost finns och förändringen sakprövas genom en bunden utvärdering före införande (3a). Ändrade planuppgifter kräver omprövning. En frivillig senare motororientering (3b) redovisas separat med sin begränsning före D3 och ersätter inte aktuell bedömning.
2. **Liten exponerad grupp:** tjänsten har 100 uppdrag, varav 8 med båda de angivna egenskaperna. Jämför med samma marginaltal men belagt åtskilda egenskaper och med okänt överlapp. Prova ett och två avgörande maxscenarier samt kontroll av endast ett av dem.

Talen är syntetiska provdata, inte risktrösklar. Nuvarande metod körs och sparas före ändring. Mänskligt prövade målutfall tillkommer genom metodbesluten; de uppfinns inte av testförfattaren.

## Villkor som består

- AI skriver text men fattar inga riskbeslut.
- Inga personuppgifter, privata råsvar eller kontrollutfall till AI; återkoppling vid omförsök följer samma gräns.
- Byrådata ligger utanför Git; tester använder syntetiska uppgifter.
- Ändringar av metod, modell och bindningsalgoritm identifieras uttryckligen. Gamla godkännanden får inte tyst få ny innebörd.
- Låsordning, revisionsskydd, kontrollsummor och atomisk export bevaras.
- Sakkunnigstatus ändras bara efter verklig granskning. Teknisk verifiering är en separat status.
- Ingen hård ordgräns, automatisk radering av historik eller generell omskrivning av tidigare format.
- Nya planposter och kombinationsgrupper stannar lokalt. Tomma nya modellfält utelämnas vid historisk serialisering. Ingen ny AI-uppdelning, tillåtelselista eller rapport V9 ingår.
- Godkända verifieringskörningar använder en kontrollerad Python 3.12-miljö i genomförandets checkout, vald via `RISKANALYS_VENV`. Återanvänd en giltig `.venv312` eller skapa en separat sådan med `python3.12`; ingen `.venv` antas redan ha rätt interpreter och en använd Python 3.14-miljö byggs inte om. Renderingskontrollen använder projektets kedja med LibreOffice/Poppler eller motsvarande; den kräver inte en viss agentmiljös verktyg.

## Leveransgräns

Kravkartan får status per punkt och exakt bevis för funktion, test och rapport. Slutprovet skiljer tekniska kontroller från verksamhetens faktabekräftelse och verklig metodgranskning. Krav om information, utbildning och faktisk användning kan stödjas av programmet men inte anses fullgjorda enbart genom ett grönt test.
