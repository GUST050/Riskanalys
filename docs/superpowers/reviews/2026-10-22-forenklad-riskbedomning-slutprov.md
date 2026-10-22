# Gemensam analys – slutprov och granskningsunderlag för Claude

Status: Plan A och B1–B7 är implementerade och tekniskt slutverifierade. Slutlig fullsvit: **3 198 godkända, ett livetest bortvalt, exit 0**. Ingen push, merge eller verklig sakkunnigattest ingår. Användarens Claude-granskning återstår.

## Granskningsintervall

Arbetskopia: `/Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys`, gren `codex/kravstod-tjansteexponering`. Användarens andra klon/gren har inte ändrats.

| Del | Kodbas / checkpoint | Bevis |
|---|---|---|
| Plan A, planernas livslopp | `b3cf49080fc20e70665d2917042a3a3a6122bf9e` | 3 063 godkända, ett livetest bortvalt, exit 0 |
| B1–B3, katalog/schema/validering | `0be7327decd1fbb494c52c8769046e2c492fb52d` | 3 107 godkända, ett livetest bortvalt, exit 0 |
| B4–B5, arbetsvyer/rapport | `cca0ede` | 3 149 godkända, ett livetest bortvalt, exit 0; två senare reproducerade kanter dokumenterade |
| B6–B7, överföring/slutprov | `cca0ede..HEAD` (slutcommit anges i leveransmeddelandet) | 3 198 godkända, ett livetest bortvalt, exit 0; 2 152,78 s |

Claude kan granska hela produktändringen med `git diff 8379172..HEAD`, eller delarna `8379172..b3cf490`, `d0b75d2..0be7327`, `0be7327..cca0ede` och `cca0ede..HEAD`. Inga av dessa nya produktcommits har pushats eller slagits ihop inom uppdraget. Rawloggar, snapshots och UI/DOCX-stickprov finns i den lokala, Git-ignorerade mappen `.superpowers/sdd/2026-10-22-forenklad-riskbedomning-plan/`; Plan A har sin egen syskonmapp. Dokumentationen här anger utfall och avgränsningar även utan dessa lokala filer.

Design revision 2 och genomförandeplanerna är styrande. B5-checkpointen är en utvecklingsversion. Slutintervallet ska omfatta rättningarna av oklara egna avvikelser och lokala verksamhetssvar; inga kända sådana fel ska lämnas öppna i slutleveransen.

## Vad byrån gör

1. Väljer vilka av standardtjänsterna som erbjuds. Osäkra svar sparas som okända. Valet behöver källa, datum och ansvarig; nytt införande följer planval och bunden utvärdering.
2. Beskriver och belägger gemensamma sårbarheter och verksamhetsförhållanden en gång. Ett antagande är fortsatt ett antagande.
3. Prövar hur varje post berör respektive tjänsts kunder, arbetsmoment/befogenheter, underlag/insyn, leverans och geografi. Oförändrade markerade tillämpningar kan bekräftas samlat. Avvikelser behöver egna skäl och belägg.
4. Kopplar hot och sårbarheter, analyserar samverkan, kontrollernas verkliga räckvidd, PT/TF och kvarstående begränsningar per tjänst. Motorns risknivåer och åtgärdsgrund behålls. Programmet härleder avvikelsernas riktning där underlaget medger det.
5. Prövar täckning för egna relevanta sårbarheter utan katalogfaktor. Det krävs rätt hot/dimension/riskled, beskrivning av mekanismen, relevant lokalt scenario, jämförelsenivå och belägg. Inneboende prövning krävs alltid och kvarstående dessutom vid faktisk kontrollsänkning i samma motorscenario. En hög allmän tjänstenivå är inte täckning.
6. Godkänner hela analysunderlaget, granskar dokumentets båda delar och fastställer enligt befintliga kvalitetsgrindar. De fyra bekräftelse-/beslutstyperna är fortsatt separata. Ändrat paket gör alla tjänstebeslut inaktuella.

## Metod- och AI-gräns

Inga faktiska riskvikter, trösklar, grundnivåer, kontrollavdrag eller konsekvensskalor ändras. Konsekvens bedöms enligt befintlig metod; dess skala/fasta värden är fortsatt metodval. D3/D9 avgörs inte av denna strukturändring.

Den extra +1-beräkningen är en kontrafaktisk referens med befintliga scenarioregler och samma kontrollantaganden, inte en ny tillämpad faktor eller ett facit. En lägre mänsklig jämförelsenivå behöver uttrycklig motivering och sakgranskning. Programmets faktiska risk-/åtgärdsutfall ändras inte.

Privata gemensamma poster, avvikelser, riktningar, täckningsprövningar, belägg och författare skickas inte till AI. Hela begäranden jämförs i normalfall, omförsök och reservsvar. Katalogens nya tjänstebeskrivningar är källbundna **ogranskade förslag**. Regelbasbindningen ändrades av metadata i B1; det är inte en sakkunnigattest eller metodändring.

## Överföring och historik

Läsning/förnyelse/import av äldre analys konverterar den inte automatiskt. Den särskilda överföringen kräver jämförelse och aktuell registersumma. Exakta originalbytes arkiveras före atomisk publicering; avbrott bevarar originalet. Semantiskt skilda texter, perioder, belägg, relevanser och scenarier slås inte ihop.

Lokala originalsvar och deras författare bevaras som källunderlag. Gemensamma förslag saknar överfört författarskap och är obekräftade antaganden. Inga analysgodkännanden förs över; block/scenarioval/tillämpningar och modellens lokala användningsprövning måste förnyas. Privata dokument kontrolleras genom befintlig säker filläsning. En gammal flik, ändrat belägg eller upprepad överföring avvisas.

## Rapportmätning – samma frysta fakta och skrivsvar

Mätkontraktet anger format, schema, profil-, motor-, skrivsvars- och regelbashash. Jämförelsen avser **ogranskade överföringsförslag med alla gamla lokalsvar bevarade**, inte färdigstädade analyser. Inget borttaget original eller flytt till B1 räknas som en minskning.

| Fryst fall | Schema | Läsrapport | B1 | Totalt |
|---|---:|---:|---:|---:|
| Fyra tjänster | 1 | 13 342 | 34 440 | 47 782 |
| Fyra tjänster | 2 | 13 990 | 35 636 | 49 626 |
| Med betalningsmandat | 1 | 13 019 | 34 609 | 47 628 |
| Med betalningsmandat | 2 | 13 667 | 35 805 | 49 472 |

I första tjänsteavsnittet ökar ordagrant identisk text som finns i alla fyra tjänster från 1 090 till 1 233 ord i fyrtjänstfallet och från 1 001 till 1 144 ord med betalningsmandat. Likartad struktur utöver ordagrann upprepning är 310 ord i båda scheman/fallen. Även upprepningen ökar i detta ogranskade överföringsläge.

Båda fallen ökar med **648 ord i läsrapporten, 1 196 i B1 och 1 844 totalt**. Ingen total förkortning påstås. Mätverktyget redovisar också ordagrann upprepning och likartad struktur; råloggar ska läsas tillsammans med tabellen. De installerade verktygen är omkörda för båda fallen och båda scheman. Profil-, motor-, regelbas- och stabil skrivsvarshash är identiska inom varje jämförelse. Endast den typade anropstidsstämpeln undantas ur skrivsvarshashen; ett test säkerställer att ändrad svarstext fortfarande ändrar underlaget.

Verkliga lyckade publika bekräftelseoperationer, samma syntetiska fakta: schema 1 kräver **32 scenarioval + 64 block = 96**. Schema 2 kräver dessutom **fyra samlade tillämpningshandlingar = 100**. Antalet ökar med fyra. Redigering, överföring, analysbeslut och sakgranskningar räknas inte i dessa tal; ingen klick- eller tidsvinst uppskattas. Ett separat fall med belagd lägre avvikelse och egen sårbarhet använder 106 bekräftelseoperationer, följt av fyra nya analysbeslut. Dess större omfattning ska inte blandas ihop med samma-fakta-jämförelsen.

## Dokument och UI

Native DOCX skapas av produktens V8-byggare; inga alternativa rekonstruerade dokument används som bevis. B5:s riktade dokumentkontroll omfattade gemensamt underlag, lokal avvikelse, omfattningsunderlag och B1. Tre DOCX renderades korrekt; utvalda sidor kontrollerades efter rättning av etiketter och periodmetadata. Hela dokumentens visuella kvalitet är inte manuellt godkänd.

CUA/IAB provade de tre arbetsvyerna med enbart syntetiska data. En belagd lägre avvikelse sparades och visade motorns högre nivå som styrande. En ny egen H-03/PT-sårbarhet skapades via formuläret, bekräftades uttryckligen och visade spärrande metodkonflikt utan täckningsprövning. Samlat tjänsteurval med två införanden behöll svaren medan planval begärdes per rad; bara planerna `ett` och `tva` genomfördes, medan `alternativ` förblev aktiv. Lokala testservrar stoppades och browserfliken stängdes efter kontrollen.

B7:s fyra faktiska V8-DOCX renderades med dokument-skillens LibreOffice/PDF/PNG-kedja, samtliga exit 0. Båda läsrapporterna har 40 renderade sidor, B1 har 104 respektive 108. Visuellt öppnade stickprov: fyrtjänstfallets läsrapport sida 5 (gemensamt underlag), mandatfallets läsrapport sida 34 (lokala originalsvar och varning), fyrtjänstfallets B1 sida 79 (originalfält/proveniens). Ingen klippning eller överlappning observerades i dessa stickprov. Den smala tjänstekolumnen radbryter ”Gemensamt”, men är läsbar.

Efter slutgranskningens rättningar exporterades även det faktiskt fastställda syntetiska positiva fallet och renderades korrekt till 58 sidor. Sidorna 17–18 öppnades visuellt: separata inneboende/kvarstående täckningsprövningar, respektive +1-referens, kontrollbegränsningar och ordinarie motorutfall är läsbara utan observerad klippning/överlappning. Det är en syntetisk testfastställelse, inte en verklig attest.

En avslutande skrivskyddad UI-kontroll öppnade den sparade kvarstående prövningen via dess egen länk. Formuläret visade ”Kvarstående risk”, referensen måttlig, den särskilda kontrollmotiveringen och valt kontrollbelägg. Skärmbild: `ui-riskled-kvarstaende.png`. Även denna testserver stoppades (exit 0) och fliken stängdes. Ingen fullsidig visuell eller native Word-kontroll påstås.

[UI-stickprov: kvarstående täckningsprövning](../../../.superpowers/sdd/2026-10-22-forenklad-riskbedomning-plan/ui-riskled-kvarstaende.png).

## Avgränsningar

Manuell tjänsteanalys utanför katalogen är fortfarande en produktuppgift. Ett separat **ofullständigt omfattningsunderlag** visar luckan och kända fakta utan påhittad nivå. Det har eget dokument-ID, manifesttyp, filnamn och fastställelsespärr och får inte användas som en färdig allmän riskbedömning. Spärren beskrivs som produktbegränsning; inget lagkrav på riskmotor påstås.

Ingen verklig sakkunnigstatus har ändrats, ingen kundriskbedömning eller kundregisterfunktion tillkommit och inga produktionsbedömningar fastställts. Tekniskt godkända syntetiska testkopior ersätter inte byråns sakprövning eller Claudes av användaren önskade granskning.

## Oberoende granskning och verifieringslogg

En fristående teknisk helgranskare granskade hela grenen inklusive då ocommittad B6–B7. Inga Critical, fem Important och en Minor. Författaren gjorde en samlad rättningsomgång, med reproducerande RED följt av GREEN:

| Fynd | Rättning och kontroll |
|---|---|
| Riskled kunde ersätta varandra | Inneboende prövning krävs alltid; kvarstående krävs dessutom vid faktisk kontrollsänkning i samma scenario. Bortfall av vardera stoppar hela godkännande-/fastställelsekedjan. |
| Oförenlig egen hot/dimension försvann | Innehålls- och katalogkontroll avvisar en omöjlig kombination; allmän PT/TF-angivelse skapar fortsatt inga extra kataloganspråk. |
| Förnyelse efter överföring använde saknade standard-ID | Nya tjänster hämtar obekräftade tillämpningar från paketets verkliga gemensamma poster och innehållssummor. |
| Enskilt nej/okänt krävde plan i HTML | Planval begärs för bekräftat ja; ett nytt ja får kompletteringssteget. Nej/okänt går att spara. Kärnans införandespärr består. |
| Samma ID i olika typade register kraschade | Typen avgör vilken kontroll som ska utföras, med prov för tillåtna namnrymder. |

Fixpassens slutliga riktade prov gav **45 godkända på 140,43 s**, inklusive positiv fastställelse och negativa riskled. Modell-/importskydd gav **13 godkända, 50 bortvalda** på 1,57 s. Förnyelsens första reproduktionsfixtur hade ogiltiga dubblett-ID; den rättades och därefter reproducerades rätt fel mot den committade B5-funktionen i en separat process. Initiala ofullständiga körningar är inte slutbevis.

**Uppskjuten Minor:** byte bort från ”gäller annorlunda” kan ge ett felaktigt formulärfel när gamla riktningsfält följer med. Felvyn tar bort dem och ett nytt försök fungerar. Det ger ingen väg runt risk-/godkännandekontrollerna. Fyndet är inte rättat i denna leverans.

Granskaren avstod från framtida manuell tjänsteanalys, sakkunnig metodkalibrering och fullständig visuell kvalitetsbedömning. Avgränsningarna redovisas ovan; inga sådana godkännanden sluts av kodgranskningen. Ingen omgranskning dispatchades: rättningarna verifierades med reproduktionsprov och därefter färsk fullsvit. Användarens egen Claude-granskning återstår.

Slutkörningen kördes sekventiellt med Python **3.12.15**, efter alla fem Important-rättningar:

```sh
.venv312/bin/python -m pytest -q --tb=short --junitxml=.superpowers/sdd/2026-10-22-forenklad-riskbedomning-plan/final-full.xml
.venv312/bin/riskanalys regelbas validera
git diff --check
```

**Fullsvit:** 3 198 godkända, ett livetest bortvalt, exit 0, **2 152,78 s**. Wrappern tog 2153.22 s. JUnit innehåller exakt 3 198 provposter och noll failure/error/skipped. De **463 frysta kod-, test-, regelbas- och verktygsfilerna** är byteoförändrade under körningen och vid slutkontrollen. Ingen verklig AI-leverantör anropades.

**Regelbas:** exit 0, version 2.0.0, 107 krav, 11 tjänster; 201/201 paragrafer hanterade i vart och ett av tre paket, sakkunnigstatus `ej_granskad`. Kontrollsumma `sha256:b4dc7018b05b340e746d31efd0a49ee837fa1312c126a24f5571445a27132a58`. Diffkontrollen gav exit 0 före färdigställandet av denna dokumentation och upprepas före commit.

Lokala fullbevis ligger i planens `.superpowers`-mapp: `final-full.log`, `final-full.xml`, `final-full-resultat.json`, `final-full-snapshot.json`, `final-evidens.json` och `final-regelbas.log`. SHA-256 för rålogg: `a0692090f3203b4cf0e5f28dc27afa583048b6e3974c828aa8594a08b4d7c42f`; JUnit: `647b187b923bd005931ec2d8c9aea4f03b1d90ee54677c940356af5bc5f637cd`; källsnapshot: `b568b4816f89c6c030d5e2fd6dbb480651536e8cb7a84929c37e76db8dab3b50`. Äldre avbrutna/fallande körningar är separat historik och ersätter inte detta slutprov.

## Avvägningar under genomförandet

Samtliga 19 dokumenterade avvägningar, i tidsordning. Det sista ledet anger kostnaden om avvägningen behöver omprövas.

1. Genomför A och B utan en ny mellanliggande godkännandegrind; användaren har godkänt ordningen och vill granska med Claude. Alla commits hålls lokala och osammanslagna. Kostnad: granskningen kan kräva ändringar i redan färdiga lokala commits.
2. +1-referensen kräver kända indata för det berörda scenariot, inte för oberoende preliminära fält. Fastställelsespärrarna består. Kostnad: scenariots beroendelista kan behöva kompletteras.
3. Schema-2-projektionen tillåter globalt katalogförda faktorer i gemensamma rader; original får inte använda det reserverade prefixet `gemensam:`. Saknade uttryckliga hotkopplingar prövas separat. Kostnad: ytterligare referensvalidering kan behövas.
4. Det historiskt frysta motorprovet normaliserar endast den avsiktligt ändrade regelbaskontrollsumman vid jämförelsen. Aktuell bindning krävs separat; faktiska motor-/profil-/AI-fält förblir frysta. Kostnad: nytt bindningsformat kräver kompletterat prov.
5. Fullsviter körs sekventiellt, eftersom fyra parallella körningar överskred datorns befintliga HTTP-tidsgränser. Inga tidsgränser höjs. Kostnad: längre verifieringstid.
6. Gemensamma operationer, formulärtolkning och vyer delas i små filer med oförändrade publika gränssnitt och registerkontroll. Kostnad: hjälpmoduler kan behöva flyttas.
7. Historiska webbtesthjälpare väljer uttryckligen schema 1. Nya publika webb-/CLI-analyser väljer 2, medan kärnmodell/fabrik behåller standard 1 för kompatibilitet. Kostnad: enskilda äldre anropare kan behöva anpassas.
8. Omfattningsexporten får valfri förväntad revision för webbens kontroll inom låset utan att bryta CLI:s tvåargumentsgränssnitt. Kostnad: gränssnittet för revisionskontrollen kan behöva justeras.
9. En uttrycklig hotanknytning hör till hela den gemensamma posten, inte varje faktor–hot-kombination. Stöd från någon angiven faktor räcker för den gemensamma kopplingen; en särskild faktorfordran behöver egen post. Egna lokala TF-anspråk får inte försvinna, och ”berör inte” med ett samtidigt riskanspråk är oklart. Kostnad: inmatningens detaljnivå kan behöva förtydligas, utan motorändring.
10. B5:s profilrenderingskontrakt och tre redan reproducerade kopplingsfel rättades före checkpointen. Kostnad: fler regressionsprov före leverans.
11. Alla ”gäller annorlunda” måste ha klarlagd riktning även utan katalogfaktorrader. Giltig täckning för en egen sårbarhet får inte dölja oklar riktning. Kostnad: byrån kan behöva lämna mer förklaring.
12. Lokalt avvikande verksamhetssvar ska förbli verksamma och synliga; gemensam bekräftelse får inte ersätta dem. Kostnad: det kan behöva förtydligas vilket lokalsvar som ska uppdateras.
13. B5 behölls som uttrycklig utvecklingscheckpoint före två senare reproducerade B7-förstärkningar. Båda infördes och verifierades före slutleveransen. Kostnad: checkpointen får inte användas fristående i drift.
14. Rapportmåtten använder konservativ överföring med alla originalfält bevarade, i stället för att låta en ny schema-2-fabrik utelämna äldre rader. Kostnad: större uppmätt längd vid överföring.
15. Den stabila skrivsvarshashen undantar enbart den typade anropstidsstämpeln; svarstext och övriga underlag består. Kostnad: ett framtida flyktigt fält kräver uttrycklig provad utökning.
16. En fristående helgranskning gjordes före den slutliga fullsvitens källfrysning. Fynd rättades i en samlad omgång, utan ny omgranskare. Kostnad: en ytterligare kodändring hade krävt nya berörda prov och ny fullsvit.
17. Framtida manuell tjänsteanalys förblir uppskjuten enligt designen; det ofullständiga omfattningsunderlaget behåller fastställelsespärren. Kostnad: tjänster utanför katalogen kräver fortsatt det framtida manuella spåret.
18. Sakkunnig kalibrering av vikter, trösklar och +1-metodens sakliga innehåll avgörs inte av implementeraren. Befintlig metod behålls. Kostnad: verkliga metodbeslut och ny verifiering återstår.
19. Visuell kontroll gäller utvalda sidor i faktiskt exporterade och renderade DOCX, inte alla sidor eller ett mänskligt sakgodkännande. Kostnad: layoutfel på andra sidor kan finnas kvar.
