# Regelbasens steg B

**Steg B är ett granskningsunderlag och en lokal arbetscommit. Fullsviten är ännu inte grön; ingen slutleverans, push eller merge. Användaren har därefter gett klartecken att fortsätta C, del 3, D och E.**

Baslinje: godkända steg A, `48991af`, efter godkänd del 1 `654066f`. Användaren har beslutat snävare tjänsteomfattning och fyra preciseringar i uppdragets avsnitt Beslut efter granskningen av steg A. Arbetet sker lokalt på `codex/regelbas-inventering`. Ingen push eller merge.

## Genomförande

Regelbasförslaget är **2.1.0**. Det innehåller 13 tjänster, 26 hot, 33 sårbarheter, 15 kontroller och fem separata indikatorer på potentiellt lägre risk. Nya och ändrade katalogobjekt har `ej_granskad`. Kravtexternas 107 poster och fastställelsens sakkunnigspärr är kvar. Indikatorerna på lägre risk ger inga avdrag.

| Ändring | Objekt och genomförande |
|---|---|
| Två nya tjänster | `T-RED-08` ansökningar om ROT, RUT och offentliga utbetalningar; `T-RED-09` granskningsuppdrag utanför auktoriserad/godkänd revision. Ingår i alla tre regionala paket, med ordinarie uppdrags-, exponerings- och kontrollfrågor. |
| Tjänstehot och kontroller | `H-TJ-12`/`13`, `C-TJ-12`/`13` och motsvarande räckviddsobjekt. Katalogens räckvidd är okänd och styrker inte lokal kontrollverkan. Kontrollmål ger inga nya generella sänkningar. |
| Tre konkreta modus | `H-MOD-05` oriktiga underlag för offentliga utbetalningar, `H-MOD-06` tvätt av brottsvinster från sanktionsbrott och `H-MOD-07` brottsursprung som döljs via krypto i företagsflöden. Alla har PT-dimension; TF-kanaler prövas fortsatt separat. |
| Fem nya kundindikatorer | `S-ARB-19` nominella ägare/innehavarandelar, `20` konstruktion för fysisk persons tillgångar, `21` sanktionshemvist, `22` terrorhemvist, `23` okänd eller okopplad betalare. Varje indikator använder ett kundantal med period. Förekomst över noll och ett steg är uttryckligen ogranskade metodval inför D3/D9. |
| Distans | `S-ARB-08` använder ett sjätte kundantal: distans utan tillförlitlig identitetssäkring. Ett äldre ja om uteblivet fysiskt möte är inte ett belägg för detta. |
| Lägre risk | `L-PTL-04-01`–`05` i en separat typad katalog. Källhänvisningar, central bedömning och granskningsstatus binds till innehållssumman och ingår i expertimport/-export. `nivaeffekt: false` är låst i schemat. |
| Hemvist | Tre heltalsfält i en gemensam fråga om Sverige, övriga EES och utanför EES, med gemensam period/underlag. Kundantal kontrolleras mot aktiva kunder; de tre bekräftade hemvistgrupperna ska tillsammans utgöra populationen. Delvis okänd fördelning summeras inte till ett påhittat utfall. |
| Avgränsning | Trust och nominell aktieägare byggs inte som tjänster. Ja ger ett synligt omfattningshinder: tjänsten ligger utanför programmets analysstöd och fastställelse är spärrad. Utkast får skapas. Även fastställelsen prövar omfattningen på nytt. |
| Företrädaruppdrag | `T-BOLAG-03` avgränsas mot vanligt eget styrelseuppdrag. Ett särskilt bekräftelsefält krävs för tredje mans uppdrag i relevant utlandsverksamhet. Äldre breda ja-svar räcker inte. NRA 7.27 saknar bedömd sektorsnivå; bolagsbildningens höga sektorsrisk från 7.25 används därför inte som jämförelsegrund. |
| Övriga preciseringar | Läsbara `S-TJ-01`–`04`, fakturautställande i löpande bokföring, skatteuppdragens arbetsmoment, offentliga löneunderlag, koncernflöden och plattforms-/PSP-led. Källhänvisningar följer de ändrade beskrivningarna. |

Hotnivån medel är fortsatt ogranskat standardvärde. Steg C:s nivåprövning och steg D:s kalibrering genomförs inte här. Nya katalogkopplingar är möjliga tjänstekedjor. Varje tillägg till en tjänst har nu en egen metodförklaring och hotposternas källlocator. H-MOD-05 kopplas till bokföring, bokslut, deklaration, lön, betalningar, klientmedelskonto, ansökningar och granskning. Ekonomisk rådgivning/ekonomichefstjänster har ingen direkt koppling till detta modus. Betalningstjänstens och klientmedelskontots mekanismer avser faktiskt mandat och vidareföring/sammanblandning av medel. Nya tjänstehot och modus ingår också i de befintliga kompetens-/organisationsfaktorernas uttryckliga hotlistor, med samma tidigare vikt och tröskel. Inga faktiska kundhändelser antas. AI-tillåtelselistan är oförändrad; de nya profil- och kontrollfälten lämnas utanför AI-underlaget.

## Frågeantal mot baslinjen

| Frågetyp | Nya intagsfält |
|---|---:|
| Sex kundantal för högre risk inklusive distans | 6 |
| Offentlig kund och reglerad/motsvarande värdepappersmarknad | 2 |
| Hemvistfördelning, tre antal i en gemensam formulärfråga | 3 |
| Två tjänster enligt befintligt mönster, 17 fält vardera | 34 |
| Två tjänstekontroller, fem fält vardera | 10 |
| Särskild bekräftelse av snävare företrädaruppdrag | 1 |
| **Summa** | **56** |

**324 → 380 intagsfält**, och totalt **371 → 431 profilfält** inklusive härledda fält. Samlade formulär och villkorad visning innebär att fältantalet inte är antalet sidor eller frågor varje byrå måste besvara. Hemvistfördelningen är en gemensam fråga med tre svarsrader. Den särskilda företrädarbekräftelsen är ett tillägg mot steg A:s räkneexempel 55; den behövs för att gamla breda styrelsesvar inte ska få en ny innebörd utan omprövning.

## Centrala landsbedömningar

Ingen byrå ombeds bedöma regelverk eller korruption per kund. Regelbasens lägre-risk-objekt innehåller en central bedömning per hemvistgrupp, med källa, grund `metodval` och status `ej_granskad` för hela objektet.

- PTL 2:4 p. 2 kan tala för lägre risk vid styrkt hemvist i Sverige eller övriga EES. Det påverkar ingen nivå i B.
- Gruppantal styrker inte motsvarande och effektivt tillämpade AML/TF-system enligt p. 3, eller låg korruption och annan relevant brottslighet enligt p. 4. De centrala bedömningarna är därför `underlag_saknas` där det lästa underlaget inte räcker. En totalsiffra utanför EES kan inte avgöra vilka länder kunderna har hemvist i.
- Ingen automatisk landlista eller positiv landsbedömning har hittats på. Ett senare positivt beslut behöver centralt källstöd och ny sakkunnigprövning; byrån ska fortfarande inte bedöma varje kunds land.

## Källversioner

Källorna och lästa avsnitt redovisas i [steg A:s käll- och täckningsmatriser](2026-10-23-katalogluckor.md). Nya/ändrade poster har motsvarande precisa hänvisningar. Lagtext får kapitel/paragraf som locator utan ett påhittat PDF-sidnummer; äldre hänvisningar med sidnummer behåller sin serialisering.

`SRC-EUROPOL-TESAT-2025` och dess äldre kontrollsumma behålls:

`sha256:0a18061235353efda54b433510f4ff20a19fca4b8933b00578f4d6f3045ef3f6`.

Den nu hämtade filen har ett nytt versions-ID, `SRC-EUROPOL-TESAT-2025-20261023`, hämtdatum 2026-10-23 och kontrollsumma:

`sha256:97a34c80ae0f8fcb6bd5527c620fb21358820a4c7b541839cc4bd1bee7d666aa`.

Versionen registrerades före katalogkompletteringen. Äldre hänvisningar skrivs inte om till den nya filen. Sakkunnigunderlagets instruktion noterar dessutom att marsvägledningens fotnot anger 01FS 2024:53 medan läst primärföreskrift och Stockholms myndighetssida anger 01FS 2024:20.

## Före och efter på samma syntetiska underlag

Den frysta basregelbasen 2.0.0, sex profilfiler och deras föreutfall sparades före ändringarna. Efterutfallen använder exakt samma profilbytes. Utfallet redovisas i två led: först äldre profiler där de nya uppgifterna saknas, sedan separata syntetiskt kompletterade jämförelsepar där båda regelbaserna får samma nya uppgifter. De nya nollorna/nej-svaren är testdata, inte en migrering av en verklig byrå.

Notation i tabellen: **PT / TF / kvarstående PT**. M = måttlig, H = hög, MH = mycket hög. Fullständiga tjänste- och scenarioutfall finns i lokalt evidensarkiv `.superpowers/evidens/2026-10-23-regelbas-steg-b/jamforelse.json` med profilernas SHA-256 och separata före-/efterfiler.

| Fall och tjänster | Före 2.0.0 | Efter med äldre obesvarad profil | Efter med kompletterat syntetiskt underlag |
|---|---|---|---|
| Standard, enmansbyrå och få faktorer: bokföring | M/M/M | H/MH/H, preliminärt | M/M/M |
| Samma fall: skatt och bolagsbildning | H/M/M | H/MH/H, preliminärt | H/M/H |
| Fyrtjänstfallet: bokföring, bokslut, deklaration, lön | H/MH/M | H/MH/H, preliminärt | H/MH/M |
| Riskbranscher: bokföring | H/H/H | H/MH/H, preliminärt | H/H/H |
| Riskbranscher: skatt och bolagsbildning | H/H/M | H/MH/H, preliminärt | H/H/H |
| Betalningsmandat: betalning och klientmedel | H/M/H | H/MH/H, preliminärt | H/M/H |

Saknade nya uppgifter gäller preliminärt enligt den befintliga försiktiga metoden. De får inte fyllas med noll. Efter komplettering förklaras höjd kvarstående nivå för skatt/bolagsbildning av att nya modus saknar prövad kontrolltäckning; de befintliga höga grundnivåerna och kontrollmålen är inte ändrade. Enbart etiketten slutlig på en tjänst betyder inte att hela paketet får fastställas: omfattning, intag och sakkunniggrindar prövas också.

De två nya tjänsterna saknar motsvarighet i baslinjen. Med uttryckligen bekräftad syntetisk standardprofil får vardera T-RED-08 och T-RED-09 15 scenarier och M/M/M. När endast juniora konsulter respektive utbildningsbrist aktiveras påverkas också deras egna tjänstehot; detta provas separat. Dessa är provutfall, inte färdigprövade tjänstenivåer.

Fyrtjänstfallets lokala analys omfattar nu 16 unika scenarier och 48 gemensamma val, jämfört med 12 och 32. Antalet analysblock är fortsatt 64. Summan av tjänsternas kataloghot är 52 i stället för 36. Utlandsvarianten får 28 unika scenarier i stället för 20. Dessa är katalog-/analysmått, inte antal rapporterade brott.

Distansändringen kan ta bort ett påslag som tidigare byggde enbart på uteblivet fysiskt möte. Det är en rättelse till PTL 2:5 p. 9:s kriterium om tillförlitlig identitetssäkring, inte ett automatiskt kontrollavdrag. Saknat nytt antal är okänt och sänker inte. Den riktade regressionen provar både bekräftad förekomst och att äldre kanalsvar inte ersätter det nya kriteriet. Det särskilda fallet `distans_saker_identitet` använder exakt samma syntetiska profil i båda motorerna: äldre distanssvar ja, nytt bekräftat antal med osäker identitet 0 och övriga nya indikatorantal 0. Utfallet blir:

| Tjänst | Före | Efter | Sänkta befintliga scenarioled |
|---|---|---|---:|
| Bokföring | H/H/M | M/M/M | 3 |
| Skatt | H/H/M | H/M/H | 2 |
| Bolagsbildning | H/H/M | H/M/H | 2 |

De sju sänkta scenarioleden avser H-03 PT före och efter kontroll samt TF i bokföring, och H-03 TF samt H-TF-03 TF i skatt respektive bolagsbildning. TF har ingen kvarstående nivå. PT:s kvarstående nivå i skatt och bolagsbildning höjs samtidigt genom de nya otäckta modusposterna. Ingen sänkning finns i de övriga tolv jämförelseparen, varken per befintligt scenarioled eller slutnivå.

Den starkare motiveringen för distanssänkningen är den lästa [PTL 2 kap. 5 § 9](https://www.riksdagen.se/sv/dokument-och-lagar/dokument/svensk-forfattningssamling/lag-2017630-om-atgarder-mot-penningtvatt-och_sfs-2017-630/): ”utan användning av metoder som på ett tillförlitligt sätt kan säkerställa kundens identitet”. Att avstå fysiskt möte räcker inte för just detta lagexempel. Ett positivt nytt antal behåller påslaget; ett okänt antal ger försiktig preliminär bedömning. Rättelsen inför inga lägre-risk-avdrag.

## Beroenden och granskningsobjekt

| Ändring | Beroenden och följd vid avslag |
|---|---|
| Sex kundantal och `S-ARB-08`/`19`–`23` | Profilfält, intag, typade villkor, tjänste-/hotkopplingar och period-/populationsvalidering. Kodvalideringen omfattas av modellfilbindningen. Ändring kräver ny regelversion och nya före-/efterutfall samt omprövning av berörda profil-/analysunderlag. D3/D9 bygger vidare på detta. |
| `L-PTL-04-01`–`05` | Ny typad samling, laddning, validering, expertobjekt och attestimport/-export samt profilfält. Tom samling utelämnas vid historisk serialisering. Del 3 bygger tabellen och D beslutar eventuell verkan; avslag på verkan behöver inte innebära borttagna data. |
| `T-RED-08`/`09`, `H-TJ-12`/`13`, `C-TJ-12`/`13` | Alla tre regionala paket, nya fält, hotobservation, räckviddsobjekt och kontrollfrågor. C behöver pröva hotnivåer; del 3 och D behöver dessa tjänster. Avslag kräver borttagen tjänstegren och nya typfallsutfall. |
| `H-MOD-05`–`07` och ändrade kopplingar | Källversioner, tjänstekatalog och motorfacit. Kontrollmål utvidgas inte automatiskt. Avslag kräver omprövade kopplingar, kvarstående nivåer och scenariounderlag. |
| Trust/nominee-stopp och företrädaravgränsning | Gemensam rättslig omfattning, utkast och ny prövning inför fastställelse. Modellfilbindningen ändras. Äldre paket läses med sina frysta underlag. |
| Källversioner och laglocator | Källregister, serialisering och källhänvisningar. Historiska kontrollsummor bevaras; ändrade källbeslut kräver förnyad granskning av beroende katalogposter. |

Den exakta [objekt- och beroendeförteckningen](2026-10-23-regelbas-steg-b-objekt.json) listar varje nytt/ändrat/borttaget objekt, de 60 nya fälten, berörda modellfiler och återprovning per beslut. Den anger även regelbasens före-/eftersummor. Ingen katalogpost har tagits bort.

De nya indikatorerna exporteras som egna granskningsobjekt. Ändrade tjänster, hot, sårbarheter och räckvidder binds enligt befintliga innehållssummor; paketattesten binder gemensam regelbas. Sakkunnigstatus har inte ändrats till verifierad i repot. Tekniska positiva fastställelseprov använder endast uttryckligt signerade syntetiska tempkopior. Där utökas den antagna räckvidden för testets aktuella katalog, inte i den verkliga regelbasen.

## Oberoende slutgranskning

En separat granskare läste hela arbetsdiffen mot `48991af`, inklusive nya filer, och gjorde begränsade reproduktioner utan externa API-anrop. Fyra betydelsefulla fynd reproducerades först som sex röda kontraktsprov:

1. Trust/nominee stoppade även intagets utkast. Utkastbehörighet skiljer nu de två uttryckliga fastställelsestoppen från övriga intagshinder. Intagets knapp och faktiska dokumentkedja använder samma kontroll; fastställelsens nyprövning är kvar. Granskningsfynd visar omfattningshinder även när andra uppgifter samtidigt är okända.
2. Företrädaruppdraget använde bolagsbildningens sektorsrisk. Bindningen är borttagen och både hotets och sårbarhetens källförklaringar avser nu 7.27/s.149. Inga nya risknivåer hämtas ur avsnittet.
3. Nya tjänstehot saknades i organisationsfaktorernas hotlistor. Kopplingar och källmotiveringar har kompletterats, även för de nya modusposterna. Prov växlar enbart juniora konsulter respektive utbildning och kontrollerar faktisk scenarioeffekt för båda tjänsterna.
4. Nya tjänstekopplingar saknade tjänstevis förklaring. Varje kvarvarande koppling har nu konkret arbetsmoment, möjlig mekanism och källa; den direkta kopplingen från ekonomisk rådgivning till offentliga utbetalningar har avgränsats bort.

De sex reproduktionsproven är gröna. Den nya B-kontraktsfilens **37 prov passerar**, inklusive ett prov genom riktig bedömning, skrivning, granskning och tre Word-filer med Testleverantor. Det kontrollerar att omfattningsstoppet syns i rapportpaketet och kvarstår inför fastställelse. Blankteckensfyndet från granskningen är rättat för ren diffkontroll. Inga mindre fynd har skjutits upp.

## Tekniska avvägningar

- Hemvist sparas som tre typade heltalsfält i en gemensam fråga. Det återanvänder period-/beläggskontrollen. Om formen behöver ändras senare krävs en annan widget, inga kundvisa landsbedömningar.
- p. 3–4 får centralt `underlag_saknas` när totalsiffror och lästa källor inte räcker för ett positivt landbeslut. Ett positivt beslut kräver nytt centralt källstöd och granskning; ingen obelagd sänkning uppstår.
- B lämnas som granskningsbart arbetssteg med riktade tester och snabbprofil. Slutlig fullsvit flyttas till slutleveransen enligt AGENTS. Om arbetet ändå används som produktleverans saknas ännu den fullständiga verifieringen.
- Ett extra bekräftelsefält införs för företrädaruppdraget: 56 nya intagsfält i stället för inventeringens 55. Kostnaden är ytterligare ett villkorat svar; alternativet skulle ge gamla breda svar en obestyrkt ny innebörd.

## Verifiering och kvarvarande arbete

B är ett arbetssteg för granskning. AGENTS regel 6 kräver berörda tester och snabbprofil inför arbetscommits samt fullsvit före leverans/PR/merge. Den tidigare planen lade fullsviten som en extra grind före B. Efter frågan om C har denna onödigt stränga ordning rättats: B kan granskas innan den slutliga fullsviten, och användaren har därefter gett uttryckligt klartecken att fortsätta de återstående stegen. Ingen grön slutleverans påstås.

- Senaste riktade urvalet, `arbetscommit-riktat2.log`: **72 godkända/10,66 s**. Det omfattar samtliga 37 B-prov, promptar och scenariotabeller.
- Riktat V8/V9-urval: **105 godkända/71,60 s**. Det positiva syntetiska fastställelseprovet med 48 scenarioval: **1 godkänt/141,60 s**. D9-facit: **2 godkända/20,70 s**.
- Snabbprofil på slutligt arbetssnapshot, `snabb6`: **140 godkända, noll fel/överhoppade, 51.480 s**, Python 3.12.15. Collection och JUnit matchar, alla 820 snapshotresurser är oförändrade.
- Katalogvalidering och diffkontroll passerar. AI-tillåtelselistan är oförändrad. Samtliga katalogers sakkunnigstatus är `ej_granskad`.
- **Fullsviten är inte grön.** Senaste hela urvalsförsöket `full7` stannade efter **1 504 godkända och 1 fel**, ett liveprov bortvalt, 697,16 s. Felet var ännu ett historiskt AI-begärandeprov som använde den utökade katalogen. Både detta V7-prov och det tidigare V5/V6-provet använder nu en separat fryst 2.0.0-katalog från godkända `48991af`. Samtliga befintliga gyllene request-/retry-summor passerar oförändrade i det riktade sluturvalet.

Den historiska testresursens innehållssumma är `sha256:b4dc7018b05b340e746d31efd0a49ee837fa1312c126a24f5571445a27132a58`. Ingen äldre JSON-resurs eller gyllene begärandekontrollsumma har skrivits om. Positiva aktuella testprofiler kompletteras uttryckligen för de nya fälten; det är inte en migrering av riktiga byrådata.

Röda och avbrutna körningar bevaras i det lokala evidensarkivet `.superpowers/evidens/2026-10-23-regelbas-steg-b/`. Tidiga fel omfattade gamla katalog-/räkningsfacit och historiska prov med levande katalog. Ett mellanliggande insamlingsfel i en testindragning är också rättat. Dessa urval räknas inte som gröna fullsviter. Snabb3 och snabb5 hade noll testfel men ändrat snapshot och används inte som slutbevis.

Den slutliga kodbasen måste få en färsk, grön ordinarie icke-live-fullsvit med exakt collection/JUnit och oförändrat snapshot före slutleverans/PR/merge. Efter B:s granskning följer C, sedan del 3 med dess beslut/PDF-kontrollpunkter, D, förnyad PDF-granskning och sist E. Inga steg C/D/E eller rapportdisposition har påbörjats här.
