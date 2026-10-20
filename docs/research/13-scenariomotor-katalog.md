# Scenariokatalog 2.0.0: källstöd och konsekvenser

Datum: 2026-10-18. Alla nivåer, länkar, kontrollmål, steg och matrisceller är **ogranskade metodval**. Teknisk validering är inte sakkunnigprövning eller godkännande för faktisk användning.

## Källavgränsning

Källorna stödjer vilka tillvägagångssätt och svagheter som behöver analyseras. De anger inte katalogens exakta hotnivåer, vikter eller kontrollavdrag. Kopplingarna nedan är därför uttryckliga metodtolkningar. Identitet, bransch, land, föreningsform eller en PEP-anknytning innebär inte att kunden begått brott.

Primärkällor öppnade eller hämtade den 18 oktober 2026:

- [SRC-LST-GOR-ARB: Gör en allmän riskbedömning](https://www.lansstyrelsen.se/skane/samhalle/betalning-ekonomi-och-pengar/forhindra-penningtvatt-och-finansiering-av-terrorism/gor-en-allman-riskbedomning.html).
- [SRC-TS-2026-14: Erfarenheter från länsstyrelsernas penningtvättstillsyn – fokus den allmänna riskbedömningen, rapport 2026:14](https://www.lansstyrelsen.se/download/18.51b8c30c19d05558bd82e18e/1774259142687/Erfarenheter%20fr%C3%A5n%20l%C3%A4nsstyrelsernas%20penningtv%C3%A4ttstillsyn.pdf).
- [SRC-VAGL-2025-03: Information till redovisningskonsulter och skatterådgivare om penningtvätt och finansiering av terrorism (mars 2025)](https://polisen.se/0be344afbcdff1a86db5cde12c2188c5/siteassets/dokument/om-polisen/penningtvatt/vagledning-till-redovisningskonsulter-och-skatteradgivare.pdf).
- [SRC-NRA-2024-25: Nationell riskbedömning av penningtvätt och finansiering av terrorism i Sverige 2024/2025](https://polisen.se/0c34c8d8c94e1a371d8cca457b84fb0a/siteassets/dokument/om-polisen/penningtvatt/nationell-riskbedomning-av-penningtvatt-och-finansiering-av-terrorism-i-sverige-2024_2025.pdf).
- [SRC-FIPO-FORETAG-2026: Storskalig penningtvätt i företagsmiljö](https://polisen.se/8fe83310adc2c5c237323d50c6012100/siteassets/dokument/finanspolisen/fipo-informerar/2026_fipo-informerar_storskalig-penningtvatt-i-foretagsmiljo.pdf).
- [SRC-FIPO-TF-2025: Finanspolisen informerar: Terrorfinansiering 2025](https://polisen.se/f4dc3a983cd5a7738db26e055dfebdca/siteassets/dokument/finanspolisen/fipo-informerar/fipo-informerar_terrorfinansiering_2025.pdf).
- [SRC-FIPO-SWISH-2025: Swish och direktbetalningar 2025](https://polisen.se/8aec5215d427ca11ae6c11371e99e42e/siteassets/dokument/finanspolisen/fipo-informerar/2025_fipo-informerar_swish_direktbetalningar.pdf).
- [SRC-EU-SNRA-METOD: Supranational risk assessment methodology, version 1.1, 4 November 2015](https://fatfplatform.org/assets/04112015-Methodology-SNRA-Clean-v1.1.pdf).

Länsstyrelsens webbvägledning, avsnitten om hot, sårbarheter, nivåer och effekt, styr analyskedjan. Rapport 2026:14 s. 6–10 stödjer tjänstevis analys; s. 7 beskriver utlandsflöden tillsammans med utbildningsbrist. Vägledningen för redovisningskonsulter, fysisk PDF-sida 16–17 och 23, stödjer prövning av betalningar och underlag. NRA 7.19 s. 122–125, 7.20 s. 126–128, 7.25 s. 144–146, 7.26 s. 147–148 och 7.27 s. 149 anger sektorernas relevanta förfaranden. Exakt placering anges på katalogposterna eller i kontrollmålets motivering.

I fixrunda 1 (18 oktober 2026) hämtades NRA, vägledningen för redovisningskonsulter och Finanspolisens TF-lägesbild på nytt från de registrerade URL:erna. Alla tre stämmer med SHA-256 i källregistret. Sidhänvisningarna i kontrollmålen och i S-ARB-05 är lästa i dessa filer; tryckt sidnummer i NRA sammanfaller med PDF-sidan.

EU-dokumentet är kommissionens metodversion 1.1, godkänd 4 november 2015, läst i en arkivkopia hos FATF Platform. Den anger större vikt för sårbarhet, 60 mot 40 för hot, på fysisk PDF-sida 15 och 39. Denna inspirationskälla gör inte programmets trenivåmatris, +1 eller maxaggregering till bindande regler. Den valda niocellsmatrisen är projektets egna metodval.

Finanspolisens tre hämtade PDF:er stämmer med befintliga SHA-256 i källregistret. Den nya EU-kopian har SHA-256 `d3b4520ac4e33ffa4b5d594a3bc1d7f1bc0a25ca9ae40f75c1e4d8a56903fc09`. Källornas tidigare hämtdatum har inte skrivits om.

## Hotnivåer

Medel används för samtliga 21 hot. Hög sektorsrisk och möjliga framtida ökningar i NRA är inte en observerad frekvens för varje enskilt modus. Finanspolisens TF-lägesbild beskriver insamling som vanlig i rapporteringen över sektorer; det ger ingen kvantifierad frekvens för var och en av våra tjänster. Det finns inte heller tillräckligt stöd här för låg. Medel är ett öppet standardval, inte en uppskattad statistisk sannolikhet. `nivamotivering` skiljer detta från källans hotbeskrivning. En bekräftad egen iakttagelse höjer ett steg; inget eller okänt svar sänker aldrig.

`nivamotivering` på varje hot anför samma källställe som hotets första `kallhanvisningar`-post och som tabellen nedan, till exempel SRC-NRA-2024-25 (7.19, s. 123) för H-01–H-03. Tidigare anförde motiveringen för H-01–H-03 SRC-VAGL-2025-03 medan tabellen anförde NRA; det är rättat.

**Att observera för sakkunnig:** när alla hot har nivån medel är medelraden i BT-SANN-02 en identitet: sannolikheten blir lika med sårbarhetsnivån (P = V). Hotnivån skiljer därför inte scenarierna åt förrän byrån registrerar en egen iakttagelse (hotnivå hög) eller en sakkunnig sätter en annan nivå. Hela skillnaden mellan scenarierna kommer i dag från vilka sårbarheter som möjliggör respektive hot.

| Hot | Nivå | Källa och läst avsnitt |
|---|---|---|
| H-01 – Osanna och falska fakturor | medel | SRC-NRA-2024-25 7.19, s. 123 |
| H-02 – Brottsvinster redovisas som intäkter | medel | SRC-NRA-2024-25 7.19, s. 123 |
| H-03 – Oförklarade in- och utflöden | medel | SRC-NRA-2024-25 7.19, s. 123 |
| H-TJ-01 – Utnyttjande av löpande bokföring | medel | SRC-NRA-2024-25 7.19, s. 123 |
| H-TJ-02 – Utnyttjande av bokslut och årsredovisning | medel | SRC-NRA-2024-25 7.19, s. 123 |
| H-TJ-03 – Utnyttjande av deklarationer och deklarationsombud | medel | SRC-NRA-2024-25 7.19, s. 123 |
| H-TJ-04 – Utnyttjande av lönehantering | medel | SRC-NRA-2024-25 7.19, s. 123 |
| H-TJ-05 – Utnyttjande av betalningar och attest i kundens namn | medel | SRC-NRA-2024-25 7.19, s. 123 |
| H-TJ-06 – Utnyttjande av klientmedelskonto | medel | SRC-NRA-2024-25 7.19, s. 123 |
| H-TJ-07 – Utnyttjande av ekonomisk rådgivning och ekonomichefstjänster | medel | SRC-NRA-2024-25 7.19, s. 123 |
| H-TJ-08 – Utnyttjande av skatterådgivning utöver deklarationer | medel | SRC-NRA-2024-25 7.20, s. 126 |
| H-TJ-09 – Utnyttjande av bolagsbildning, lagerbolag och bolagsförmedling | medel | SRC-NRA-2024-25 7.25, s. 144 |
| H-TJ-10 – Utnyttjande av registrerad adress eller postadress | medel | SRC-NRA-2024-25 7.26, s. 147 |
| H-TJ-11 – Utnyttjande av styrelseuppdrag eller bolagsrättsligt ansvar | medel | SRC-NRA-2024-25 7.25, s. 144 |
| H-MOD-01 – Felbetalning med återföring till annat konto | medel | SRC-VAGL-2025-03 Tillvägagångssätt; fysisk PDF-sida, s. 16 |
| H-MOD-02 – Moms- och karusellupplägg med osanna underlag | medel | SRC-VAGL-2025-03 Tillvägagångssätt; fysisk PDF-sida, s. 23 |
| H-MOD-03 – Bolag som förbrukningsvara och dolda företrädare | medel | SRC-FIPO-FORETAG-2026 Tillvägagångssätt; fysisk PDF-sida, s. 1 |
| H-MOD-04 – Snabba direktbetalningar och skiktning | medel | SRC-FIPO-SWISH-2025 Tillvägagångssätt; fysisk PDF-sida, s. 1 |
| H-TF-01 – Insamling och vidareförmedling för terrorism | medel | SRC-FIPO-TF-2025 Tillvägagångssätt; fysisk PDF-sida, s. 2 |
| H-TF-02 – Terrorfinansiering via hawala, krypto eller transitländer | medel | SRC-FIPO-TF-2025 Tillvägagångssätt; fysisk PDF-sida, s. 1; SRC-FIPO-TF-2025 Hawala, kryptovalutor och dolda syften; fysisk PDF-sida, s. 2 |
| H-TF-03 – Föreningar eller bolag döljer ändamålet med finansiering | medel | SRC-FIPO-TF-2025 Tillvägagångssätt; fysisk PDF-sida, s. 4 |

## Möjliggörande sårbarheter

H-TJ-01–11 förekommer endast på sårbarheter med område `tj` eller `verk`. Ett hot som inte finns i en tjänst påverkar inte den tjänsten. Validering och motorns direkta körväg stoppar en använd sårbarhet som saknar någon verksam hot-/dimensionskoppling i tjänsten. S-ARB-05 (ideell organisationsform) har `galler: bada` och höjde därför PT i 1.6.0. I utkastet som granskades (eca5562) kopplades faktorn bara till TF-hoten, vilket sänkte PT för ideella kunder och TF när faktorn kombinerades med en H-03-faktor (se Systematisk sökning). Controllerns beslut: S-ARB-05 behåller TF-kopplingarna och kopplas också till H-03, eftersom källan inte uttryckligen utesluter PT. SRC-FIPO-TF-2025 s. 2 beskriver mönstret som många överföringar från okända avsändare som förs vidare, alltså flöden vars ursprung och mottagare behöver förklaras; s. 4 anger att TF ofta går via samma kanaler som penningtvätt. PT-kopplingen är ändå ett konservativt, ogranskat metodval i avvaktan på sakkunnig: källan är en TF-lägesbild och stöder inte uttryckligen en PT-höjning. Att ta bort PT-höjningen vore en sänkning som kräver sakkunnigbeslut.

H-03 avser oförklarade flöden. KYC-, ägar- och leveranssvagheter kopplas till H-03 när de försvårar att förstå ursprung, ändamål eller mottagare, även i rådgivnings- och bolagsuppdrag. Det är inte samma sak som att tjänsten faktiskt har tillgång till en kunds bankkonton; kontrollmål och räckvidd prövas separat. Inga tjänsters hotlistor eller sårbarhetslistor har ändrats.

| Sårbarhet | Möjliggör hot | Källor | Metodtolkning |
|---|---|---|---|
| S-KUND-01 | H-01, H-02, H-03, H-MOD-02 | SRC-NRA-2024-25, SRC-TS-2026-14, SRC-LST-GOR-ARB | Riskbranscher kan ge osanna underlag, blandade intäkter och svårförklarade flöden. H-01 följer Länsstyrelsens fakturaexempel; H-03 avser flöden även i rådgivnings- och bolagsuppdrag. |
| S-KUND-02 | H-02, H-03, H-TF-01 | SRC-PTL, SRC-VAGL-2025-03, SRC-NRA-2024-25, SRC-LST-GOR-ARB | Kontanter försvårar spårning av intäkters ursprung och insamlade medels vidareförmedling. |
| S-KANAL-01 | H-01, H-02, H-03, H-MOD-01, H-MOD-02, H-MOD-04 | SRC-TS-2026-14, SRC-NRA-2024-25, SRC-LST-GOR-ARB | Utan bankdata kan underlag inte följas till faktisk betalning, motpart eller vidareföring; fakturor och skenbara återbetalningar kan förbli oupptäckta. |
| S-VERK-01 | H-01, H-03, H-TJ-01, H-TJ-02, H-TJ-03, H-TJ-04, H-TJ-05, H-TJ-06, H-TJ-07, H-TJ-08, H-TJ-09, H-TJ-10, H-TJ-11 | SRC-TS-2026-14, SRC-NRA-2024-25, SRC-LST-GOR-ARB | Självständigt arbete utan tillräcklig erfarenhet kan missa osanna underlag och avvikande flöden. De generiska tjänstehoten kopplas endast till denna verksamhetsspecifika granskningssvaghet. |
| S-GEO-01 | H-03, H-TF-01, H-TF-02 | SRC-NRA-2024-25, SRC-LST-GOR-ARB, SRC-TS-2026-14 | Utlandsled försvårar prövningen av flödens syfte, ursprung och slutmottagare; kopplingen H-03 följer tillsynsrapportens utlands- och utbildningsexempel. |
| S-KOMB-01 | H-01, H-02, H-03, H-MOD-02 | SRC-NRA-2024-25, SRC-LST-GOR-ARB | Riskbranschens underlag är svårare att pröva när bankflöden saknas. Ersättning av de enskilda faktorerna sker endast i scenarier där denna kombination själv verkar. |
| S-TJ-01 | H-TJ-05, H-03, H-MOD-01, H-MOD-04 | SRC-NRA-2024-25, SRC-LST-GOR-ARB | Betalningsmandat kan verkställa ogrundade överföringar, återföring till annat konto och snabb vidareföring. |
| S-TJ-02 | H-TJ-06, H-03, H-MOD-01 | SRC-NRA-2024-25, SRC-LST-GOR-ARB | Medel på byråns konto kan skymma kunden bakom transaktionen och möjliggöra återföring till annan mottagare. |
| S-TJ-03 | H-TJ-09, H-MOD-03 | SRC-NRA-2024-25, SRC-LST-GOR-ARB | Bolagsbildning och förmedling kan ge dolda företrädare tillgång till juridisk person, konto och historik. |
| S-TJ-04 | H-TJ-11, H-MOD-03 | SRC-NRA-2024-25, SRC-LST-GOR-ARB | Företrädarmandat kan legitimera bolag där någon annan utövar den verkliga kontrollen. |
| S-ARB-01 | H-01, H-02, H-03, H-MOD-03, H-TF-03 | SRC-TS-2026-14, SRC-LST-GOR-ARB | Minskad vaksamhet i nära relationer kan göra att underlag, flöden och bakomliggande kontroll inte ifrågasätts. |
| S-ARB-02 | H-03 | SRC-VAGL-2025-03, SRC-LST-GOR-ARB | PEP-anknytning kräver fördjupad prövning av tillgångars ursprung och syfte; otillräcklig sådan prövning kan dölja avvikande flöden. Anknytningen är inget bevis om brott. |
| S-ARB-03 | H-03, H-MOD-03, H-TF-03 | SRC-VAGL-2025-03, SRC-LST-GOR-ARB | Otydliga ägarled kan dölja både den faktiska kontrollen över bolaget och flödens mottagare eller ändamål. |
| S-ARB-04 | H-03, H-MOD-03, H-TF-02, H-TF-03 | SRC-VAGL-2025-03, SRC-LST-GOR-ARB | Svårverifierade utländska ägarled kan skymma verklig kontroll och internationella flödens slutmottagare. |
| S-ARB-05 | H-03, H-TF-01, H-TF-03 | SRC-FIPO-TF-2025, SRC-LST-GOR-ARB | Insamling och vidareförmedling via ideella organisationer kan dölja terrorismändamål (s. 2). H-03 följer av källans beskrivning av många inkommande överföringar som förs vidare; PT-delen är ett konservativt ogranskat metodval (se ovan). |
| S-ARB-06 | H-03, H-MOD-03 | SRC-VAGL-2025-03, SRC-LST-GOR-ARB | Kortlivade bolag försvårar uppföljning av återkommande flöden och kan dölja samma aktör bakom flera juridiska personer. |
| S-ARB-07 | H-03, H-MOD-03 | SRC-FIPO-FORETAG-2026, SRC-LST-GOR-ARB | Byten av företrädare kan skymma förändrad faktisk kontroll och nya användningar av befintliga konton och flöden. |
| S-ARB-08 | H-03, H-MOD-03, H-TF-03 | SRC-VAGL-2025-03, SRC-LST-GOR-ARB | Svag verifiering vid distanskontakt kan skymma faktisk kund, företrädare och ändamålet med flöden eller finansiering. |
| S-ARB-09 | H-03, H-MOD-03, H-TF-02, H-TF-03 | SRC-TS-2026-14, SRC-LST-GOR-ARB | Mellanhänder kan skymma kunden bakom flödet, den verkliga kontrollen och finansieringens slutmottagare. |
| S-ARB-10 | H-03, H-MOD-03, H-TF-03 | SRC-TS-2026-14, SRC-LST-GOR-ARB | Otillräcklig egen kontroll av extern kundkännedom kan lämna faktisk kontroll, transaktionssyfte och finansieringsändamål oprövade. |
| S-ARB-11 | H-03, H-TF-02, H-TF-03 | SRC-TS-2026-14, SRC-LST-GOR-ARB | Svaga skydd i högrisktredjeland kan försvåra uppföljning av flöden och bakomliggande mottagare; landanknytning är inte i sig ett brott. |
| S-ARB-12 | H-03, H-MOD-03 | SRC-TS-2026-14, SRC-LST-GOR-ARB | Korruptionsanknytning kan dölja tillgångars ursprung och faktisk kontroll bakom bolag och flöden. |
| S-ARB-13 | H-03, H-TF-02 | SRC-TS-2026-14, SRC-LST-GOR-ARB | Svagt AML-regelverk kan försvåra spårning och verifiering av internationella flöden och mellanhänder. |
| S-ARB-14 | H-03, H-TF-01 | SRC-TS-2026-14, SRC-LST-GOR-ARB | Geografiskt utsatt verksamhet kan ge svårare prövning av flödens ursprung och insamlingars ändamål; områdestillhörighet är ingen brottspresumtion. |
| S-ARB-15 | H-01, H-03, H-TF-01, H-TF-02, H-TF-03, H-TJ-01, H-TJ-02, H-TJ-03, H-TJ-04, H-TJ-05, H-TJ-06, H-TJ-07, H-TJ-08, H-TJ-09, H-TJ-10, H-TJ-11 | SRC-TS-2026-14, SRC-LST-GOR-ARB | Utbildningsbrister kan göra falska fakturor och oförklarade utlandsflöden oupptäckta, enligt Länsstyrelsens exempel. Verksamhetens kompetens behövs även för att känna igen varje tjänsts egna missbruk och TF-modus. |
| S-ARB-16 | H-01, H-03, H-MOD-03, H-TF-03, H-TJ-01, H-TJ-02, H-TJ-03, H-TJ-04, H-TJ-05, H-TJ-06, H-TJ-07, H-TJ-08, H-TJ-09, H-TJ-10, H-TJ-11 | SRC-TS-2026-14, SRC-LST-GOR-ARB | När utförare och kontrollant är samma person saknas oberoende ifrågasättande av underlag, flöden, ägarbild och tjänstens eget missbruk. |
| S-ARB-17 | H-01, H-02, H-03, H-MOD-03, H-TJ-01, H-TJ-02, H-TJ-03, H-TJ-04, H-TJ-05, H-TJ-06, H-TJ-07, H-TJ-08, H-TJ-09, H-TJ-10, H-TJ-11 | SRC-TS-2026-14, SRC-LST-GOR-ARB | Kundberoende kan försvåra kritiska frågor om underlag, medelsursprung, ägande och tjänstens egna arbetsmoment. |
| S-ARB-18 | H-01, H-03, H-MOD-03, H-TF-03, H-TJ-01, H-TJ-02, H-TJ-03, H-TJ-04, H-TJ-05, H-TJ-06, H-TJ-07, H-TJ-08, H-TJ-09, H-TJ-10, H-TJ-11 | SRC-TS-2026-14, SRC-LST-GOR-ARB | Utkontraktering kan ge insynsgap i underlagsgranskning, flödesuppföljning, kundkännedom och de egna tjänstemomenten; ansvar och vaksamhet kvarstår. |

## Kontrollmål

Målet beskriver vad kontrollen är avsedd att upptäcka eller motverka. Det är skilt från den historiska räckviddens möjliga observation och dess status `okand`. Ingen räckvidd har breddats eller fått högre sakkunnigstatus. Före en reduktion krävs samma belägg för utformning, genomförande och verksam effekt som tidigare, och dessutom ett mål för det aktuella hotet i samma tjänst. Ett lågt eller okänt lokalt täckningsutfall måste hanteras i den separata analysprövningen.

I fixrunda 1 prövades varje kontroll mot sin anförda källa. Alla C-TJ-kontroller har samma beskrivning: verifiera underlag, syfte, ägarbild och avvikande flöden i uppdraget. Tjänstens eget H-TJ-hot och H-03 är mål där källan beskriver tjänstens missbruk eller flöden och kontrollens arbetsmoment riktar sig mot det. Där ett av dem inte är mål står hotet och skälet uttryckligen i riktningens `motivering`; ett kontraktsprov kräver det. Övriga hot i tjänsten är inte prövade som mål och ger ingen sänkning. TF-hoten är aldrig mål, eftersom metoden inte sänker TF med kontroller. Ingen riktning omfattar samtliga hot i en tjänst (valideringen underkänner det).

| Kontroll | Tjänst | Hotmål | Källa och avgränsning |
|---|---|---|---|
| C-07 | T-RED-01 | H-03, H-MOD-01 (oförändrat) | NRA 7.19 s. 123 nämner transaktioner utan underlag och felbetalning till annat konto; vägledningen fysisk PDF-sida 16–17. **H-TJ-01 är inte mål:** avstämningen visar att betalning och underlag stämmer, men räckvidden anger att en matchande faktura inte styrker att affären är verklig. Samma skäl för H-01, H-02 och H-MOD-02. H-MOD-04 är inte prövat. |
| C-TJ-01 | T-RED-01 | H-TJ-01, H-01, H-03 (H-TJ-01 ny) | NRA 7.19 s. 122–123: konsulten kan användas för att få falska underlag och fakturor att framstå som riktiga, och transaktioner utan underlag upptäcks inte vid otillräcklig kundkännedom. Vägledningen s. 16 och 23: sådana omständigheter utreds genom frågor och begärda underlag. |
| C-TJ-02 | T-RED-02 | H-TJ-02, H-01, H-03 (H-TJ-02 ny) | NRA 7.19 s. 123: bokslut och övertygande årsredovisning på felaktiga grunder; transaktioner utan underlag. Vägledningen s. 23: räkenskaper som inte stödjer årsredovisningen. |
| C-TJ-03 | T-RED-03 | H-TJ-03, H-01, H-03, H-MOD-02 (H-TJ-03 och H-03 nya) | NRA 7.19 s. 122 räknar deklarationer och deklarationsombud till sektorn; s. 122–123 falska underlag och transaktioner utan underlag. Vägledningen s. 23: osanna fakturor och karusellbedrägeri. H-03 gäller bara flöden som syns i deklarationsunderlaget; kontrollen har inte generell insyn i alla betalningsled. |
| C-TJ-04 | T-RED-04 | H-TJ-04, H-02, H-03 (H-TJ-04 ny) | NRA 7.19 s. 123: brottsvinster som bokförs som försäljning och tas ut som lön och utdelning; osanna fakturor som avlönar svart arbetskraft. Vägledningen s. 17: samma uttag som lön och utdelning. |
| C-TJ-05 | T-RED-05 | H-TJ-05, H-03, H-MOD-01 (H-TJ-05 ny) | NRA 7.19 s. 123: felbetalning till annat konto och verksamhetsfrämmande utlandsbetalningar. Vägledningen s. 16–17: felbetalningar och utlandsbetalningar ska granskas närmare. |
| C-TJ-06 | T-RED-06 | H-TJ-06, H-03 (H-TJ-06 ny) | NRA 7.19 s. 123: med klientmedelskonton behöver varken företaget eller företrädaren stå som kontoinnehavare. Prövning av kund, syfte och ägarbild riktas mot att dölja vem som står bakom medlen. |
| C-TJ-07 | T-RED-07 | H-TJ-07, H-03 (H-TJ-07 ny) | NRA 7.19 s. 123: konsulten kan skapa dokument och underlag som ger ett trovärdigt intryck och dölja penningtvättstransaktioner. |
| C-TJ-08 | T-SKATT-01 | H-TJ-08, H-03, H-MOD-03 (H-TJ-08 och H-03 nya) | NRA 7.20 s. 126–127: komplexa strukturer, brevlådeföretag och slussbolag försvårar spårningen av pengarnas ursprung; osanna underlag ger transaktioner en skenbar förklaring; kundkännedom och kontroll av kundens ekonomiska situation behövs mot anonymitet bakom komplexa ägarstrukturer. Det är samma passage som definierar H-TJ-08. Målet omfattar alla tre PT-hot i tjänsten (se Strukturell spänning). TF-hoten är inte mål; s. 128 anger inga kända TF-modus för sektorn. |
| C-TJ-09 | T-BOLAG-01 | H-TJ-09, H-03, H-MOD-03 (H-TJ-09 och H-03 nya) | NRA 7.25 s. 144–145: historikbolag som brottsverktyg; flera mindre belopp från olika konton vid överföringen av köpeskillingen gör pengarnas ursprung svårt att upptäcka; kundkännedom med uppgifter om kundens ekonomiska situation och pengarnas ursprung krävs. Samma passage definierar H-TJ-09. Alla tre PT-hot i tjänsten är mål. s. 146: inga kända TF-modus. |
| C-TJ-10 | T-BOLAG-02 | H-TJ-10, H-MOD-03 (H-TJ-10 ny) | NRA 7.26 s. 147: hotaktörer använder adresser för att verka anonymt, kan anlita en målvakt, och anonymiteten beror på kundkännedomen. **H-03 är inte mål:** källan beskriver inte att kundens flöden passerar adresstjänsten, och frågan om pengarnas ursprung på s. 148 gäller kundkännedomen, inte granskning av flöden som tjänsten inte hanterar. |
| C-TJ-11 | T-BOLAG-03 | H-TJ-11, H-MOD-03 (H-TJ-11 ny) | Vägledningen s. 17: målvakter som uppträder som ledningspersoner utan att vara bolagets verkliga företrädare; NRA 7.25 s. 144: bolag som brottsverktyg. **H-03 är inte mål:** ingen registrerad källa beskriver kontroll av flöden genom företrädaruppdraget, och NRA 7.27 s. 149 har inte hot- eller sårbarhetsbedömt styrelserepresentation. Om uppdraget ger insyn i bolagets flöden är en öppen fråga för sakkunnig. |
| C-SANK | Separat sanktionsmetod | Inga PT-/TF-mål | Avsiktligt undantag: utredning av sanktionsanknytning får inte bli en generell PT-reduktion. Omprövad i fixrunda 1 med samma slutsats; kontrollen ingår inte i någon tjänsts kontrollista. |

**Beslut om C-SANK:** planens formulering ”alla 13 kontroller får minst ett mål” frångås för den separata sanktionskontrollen. De övriga 12 får mål. C-SANK:s tillämpning, risknivåer och sanktionsmetod är oförändrade. Att skapa PT-mål för att uppfylla ett antal skulle motsäga designens separata sanktionsmetod.

## Strukturell spänning: maxaggregering och smala mål

Tjänstens kvarstående PT-risk är det högsta scenariots kvarstående risk. En kontroll sänker bara scenarier vars hot den riktar sig mot, och valideringen förbjuder en riktning mot samtliga hot i en tjänst med minst tre hot. Tillsammans ger det tre konsekvenser som sakkunnig bör pröva:

- **Tjänster med få PT-hot kan sällan sänkas.** I T-BOLAG-02 och T-BOLAG-03 är H-03 det enda PT-hotet utan mål. H-03 möjliggörs av nästan alla sårbarheter och blir därför oftast det högsta scenariot. Kvarstående risk sjunker då inte, även om kontrollen fungerar.
- **Förbudet biter inte där TF-hot finns.** T-SKATT-01 och T-BOLAG-01 har tre PT-hot och två TF-hot. C-TJ-08 och C-TJ-09 riktar sig mot alla tre PT-hot, vilket valideringen godtar eftersom TF-hoten inte omfattas. Källorna stöder varje mål var för sig, men i praktiken sänker en enda verksam kontroll då hela tjänstens PT-nivå, som den gamla regeln BT-KVAR-02. Det är ett ogranskat metodval.
- **Redovisningstjänsterna har många hot utan mål.** H-02, H-MOD-01, H-MOD-02 och H-MOD-04 saknar mål i flera tjänster. Även när alla scenarier har samma nivå ligger då ett otäckt scenario kvar på inneboende nivå, och tjänstens kvarstående risk blir lika med den inneboende.

Kostnad om fel: antingen är målen för smala (kvarstående risk överskattas och byrån får ingen kredit för fungerande kontroller), eller för breda i T-SKATT-01/T-BOLAG-01 (en kontroll sänker scenarier den inte prövats mot). Uppgift 5 kräver positiv lokal prövning av samma hot och kontroll före varje sänkning, vilket begränsar den andra risken.

## Typfallsjämförelse före och efter

Före är faktiskt körd regelbas 1.6.0 (fryst kopia av HEAD f46b801). Efter är regelbas 2.0.0 efter fixrunda 1. Profil A = `syntetisk_profil` i `tester/fixturer/arb_kedja.py` (T-RED-01, T-SKATT-01, T-BOLAG-01; kontrollerna har belagd utformning, genomförande och verksam effekt); B = A med tio kunder med utlandstransaktion; C = fyrtjänstfixturen `_profil` i `tester/fixturer/analys_hela_kedjan.py`; D = A med ideell organisationsform (`P-RISK.ideell`); E = D med PEP (`P-RISK.pep`). Tabellen innehåller inga riktiga byråuppgifter. Raderna A–E är pinnade i `test_kallbundna_kontrollmal_styr_typfallens_kvarstaende_risk`.

Kolumnen *Kvarstående avgörs av* visar de PT-scenarier som ligger på tjänstens kvarstående nivå; *otäckt* betyder att ingen av tjänstens kontroller riktar sig mot hotet, *täckt* att scenariot har sänkts ett steg.

| Profil | Tjänst | Dim. | Inneboende före → efter | Kvarstående före → efter | Avgörande scenario (inneboende) | Kvarstående avgörs av | Förklaring |
|---|---|---|---|---|---|---|---|
| A | T-RED-01 | PT | måttlig → måttlig | **låg → måttlig** | alla sju PT-hot | H-02, H-MOD-02, H-MOD-04 (otäckta, måttlig) | Ingen faktor gäller, så alla sju PT-scenarier ligger på måttlig. C-TJ-01 och C-07 sänker H-TJ-01, H-01, H-03 och H-MOD-01 till låg. H-02, H-MOD-02 och H-MOD-04 är inte mål för någon av tjänstens kontroller och ligger kvar på måttlig. Förr sänkte en verksam kontroll hela tjänsten ett steg. |
| A | T-RED-01 | TF | måttlig → måttlig | — | H-03, H-TF-01, H-TF-02 | — | Oförändrad. |
| A | T-SKATT-01 | PT | hög → hög | måttlig → måttlig | H-TJ-08, H-03, H-MOD-03 | samma tre (täckta av C-TJ-08) | Oförändrad. Grundnivån hög ger hög i alla tre scenarier; C-TJ-08 riktar sig mot alla tre. |
| A | T-SKATT-01 | TF | måttlig → måttlig | — | H-03, H-TF-03, H-TF-01 | — | Oförändrad. |
| A | T-BOLAG-01 | PT | hög → hög | måttlig → måttlig | H-TJ-09, H-03, H-MOD-03 | samma tre (täckta av C-TJ-09) | Oförändrad. S-TJ-03 höjer H-TJ-09 och H-MOD-03, men grundnivån når redan taket. |
| A | T-BOLAG-01 | TF | måttlig → måttlig | — | H-03, H-TF-03, H-TF-01 | — | Oförändrad. |
| B | T-RED-01 | PT | hög → hög | måttlig → måttlig | H-03 | H-03 (täckt, hög → måttlig); H-02, H-MOD-02, H-MOD-04 (otäckta, måttlig) | Oförändrad. S-GEO-01 höjer bara H-03, som är mål för C-TJ-01 och C-07. |
| B | T-RED-01 | TF | hög → hög | — | H-03, H-TF-01, H-TF-02 | — | Oförändrad. |
| B | T-SKATT-01 | PT | hög → hög | måttlig → måttlig | H-TJ-08, H-03, H-MOD-03 | samma tre (täckta) | Oförändrad. |
| B | T-SKATT-01 | TF | hög → hög | — | H-03, H-TF-01 | — | Oförändrad. |
| B | T-BOLAG-01 | PT | hög → hög | måttlig → måttlig | H-TJ-09, H-03, H-MOD-03 | samma tre (täckta) | Oförändrad. |
| B | T-BOLAG-01 | TF | hög → hög | — | H-03, H-TF-01 | — | Oförändrad. |
| C | T-RED-01 | PT | hög → hög | måttlig → måttlig | H-03 | H-03 (täckt); H-02, H-MOD-02, H-MOD-04 (otäckta, måttlig) | Oförändrad. S-GEO-01 och S-ARB-10 möjliggör båda H-03. |
| C | T-RED-01 | TF | mycket hög → mycket hög | — | H-03 | — | Oförändrad. |
| C | T-RED-02 | PT | hög → hög | måttlig → måttlig | H-03 | H-03 (täckt av C-TJ-02); H-02, H-MOD-01, H-MOD-02, H-MOD-04 (otäckta, måttlig) | Oförändrad. |
| C | T-RED-02 | TF | mycket hög → mycket hög | — | H-03 | — | Oförändrad. |
| C | T-RED-03 | PT | hög → hög | måttlig → måttlig | H-03 | H-03 (täckt av C-TJ-03); H-02, H-MOD-01, H-MOD-04 (otäckta, måttlig) | Oförändrad mot 1.6.0. I utkastet eca5562 var kvarstående hög, eftersom C-TJ-03 inte riktade sig mot H-03; H-03 är nu mål enligt NRA 7.19 s. 122–123. |
| C | T-RED-03 | TF | mycket hög → mycket hög | — | H-03 | — | Oförändrad. |
| C | T-RED-04 | PT | hög → hög | måttlig → måttlig | H-03 | H-03 (täckt av C-TJ-04); H-01, H-MOD-01, H-MOD-02, H-MOD-04 (otäckta, måttlig) | Oförändrad. |
| C | T-RED-04 | TF | mycket hög → mycket hög | — | H-03 | — | Oförändrad. |
| D | T-RED-01 | PT | hög → hög | måttlig → måttlig | H-03 | H-03 (täckt); H-02, H-MOD-02, H-MOD-04 (otäckta, måttlig) | Oförändrad mot 1.6.0. I eca5562 sjönk inneboende till måttlig, eftersom S-ARB-05 bara var kopplad till TF. Nu möjliggör S-ARB-05 H-03. |
| D | T-RED-01 | TF | hög → hög | — | H-03, H-TF-01 | — | Oförändrad. |
| D | T-SKATT-01 | PT | hög → hög | måttlig → måttlig | H-TJ-08, H-03, H-MOD-03 | samma tre (täckta) | Oförändrad. |
| D | T-SKATT-01 | TF | hög → hög | — | H-03, H-TF-03, H-TF-01 | — | Oförändrad. |
| D | T-BOLAG-01 | PT | hög → hög | måttlig → måttlig | H-TJ-09, H-03, H-MOD-03 | samma tre (täckta) | Oförändrad. |
| D | T-BOLAG-01 | TF | hög → hög | — | H-03, H-TF-03, H-TF-01 | — | Oförändrad. |
| E | T-RED-01 | PT | hög → hög | måttlig → måttlig | H-03 | H-03 (täckt); H-02, H-MOD-02, H-MOD-04 (otäckta, måttlig) | Oförändrad. |
| E | T-RED-01 | TF | mycket hög → mycket hög | — | H-03 | — | Oförändrad mot 1.6.0. I eca5562 blev TF hög, eftersom S-ARB-02 (bara H-03) och S-ARB-05 (bara TF-hot) inte möttes i samma scenario. Nu ligger båda i H-03:s TF-scenario. |
| E | T-SKATT-01 | PT | hög → hög | måttlig → måttlig | H-TJ-08, H-03, H-MOD-03 | samma tre (täckta) | Oförändrad. |
| E | T-SKATT-01 | TF | mycket hög → mycket hög | — | H-03 | — | Oförändrad mot 1.6.0; i eca5562 hög, av samma skäl som E/T-RED-01. |
| E | T-BOLAG-01 | PT | hög → hög | måttlig → måttlig | H-TJ-09, H-03, H-MOD-03 | samma tre (täckta) | Oförändrad. |
| E | T-BOLAG-01 | TF | mycket hög → mycket hög | — | H-03 | — | Oförändrad mot 1.6.0; i eca5562 hög, av samma skäl som E/T-RED-01. |

Av 32 rader ändras en nivå: A/T-RED-01 kvarstående PT ökar från låg till måttlig. Ingen inneboende PT- eller TF-nivå ändras och ingen nivå sjunker. Jämfört med det granskade utkastet eca5562 har fem av de sex höjningarna (A och B för T-SKATT-01 och T-BOLAG-01, samt C/T-RED-03) och fyra sänkningar (D/T-RED-01 PT, E/TF i tre tjänster) försvunnit genom ändringarna ovan; den sjätte höjningen, A/T-RED-01, står kvar. De frysta v0-typfallen har oförändrade pinnade bedömningssummor.

För profilerna A, B och C är hela v7-`Delanrop` (systemprompt, innehåll, svarsschema, effort, max_tokens och promptsumma) lika med de sparade förevärdena i arbetsjournalens `task-4-baseline.json`; för D och E är begäran med 1.6.0 och 2.0.0 lika. Hot-, tjänste-, sårbarhets- och kontrollbeskrivningar, räckvidder och AI-tillåtelselista är bevarade. Nytt lokalt flervalsfält skickas aldrig till AI. Inget riktigt AI-anrop har gjorts.

## Systematisk sökning efter sänkningar

Varje byråövergripande riskfaktor (24 sårbarheter; de fyra tjänstespecifika följer av att tjänsten erbjuds) prövades ensam och parvis, 301 kombinationer, med och utan bankdata i grundprofilen (utan bankdata ersätter S-KOMB-01 riskbranschfaktorn). Andelar sattes via sina antalsfält, så att motorn ser samma härledda värden som intaget. Varje kombination kördes dels med profil A:s tre tjänster, dels med alla elva tjänster erbjudna. Före = fryst 1.6.0.

| Katalog | Tjänster | Ändrade nivåer | Sänkningar | Höjningar |
|---|---|---|---|---|
| Granskat utkast eca5562 | 3 | 1 652 | 56 | 1 596 |
| Granskat utkast eca5562 | 11 | 6 018 | 270 | 5 748 |
| 2.0.0 efter fixrunda 1 | 3 | 260 | **0** | 260 |
| 2.0.0 efter fixrunda 1 | 11 | 3 942 | **0** | 3 942 |

**Sänkningarna i utkastet** krävde alla S-ARB-05: (a) ideell ensam sänkte inneboende PT från hög till måttlig i varje tjänst med grundnivå medel (T-RED-01–04, T-RED-07, T-BOLAG-02), eftersom faktorn inte möjliggjorde något PT-hot; (b) ideell tillsammans med en av S-ARB-01–04, S-ARB-06–13 eller S-ARB-16–18 sänkte TF från mycket hög till hög, eftersom partnern inte möjliggjorde något av de TF-hot som S-ARB-05 möjliggör i just den tjänsten (H-TF-01 i alla tjänster, H-TF-03 bara i T-SKATT-01 och T-BOLAG-01–03), så att de två faktorerna aldrig möttes i samma TF-scenario. Med H-03-kopplingen finns båda faktorerna i H-03:s PT- och TF-scenario, och alla sänkningar (56 respektive 270) har försvunnit. Det systematiska provet `test_inga_oredovisade_sankningar_for_enskilda_eller_parvisa_faktorer` (elva tjänster, med och utan bankdata) underkänner varje sänkning som inte är uppräknad och förklarad här. Listan över redovisade sänkningar är tom.

**Höjningarna** gäller bara kvarstående PT-risk; ingen inneboende nivå ändras i någon kombination. Orsaken är i varje tjänst ett PT-scenario som ingen kontroll riktar sig mot:

| Tjänst | Höjningar (av 602 körningar) | Otäckta PT-scenarier som håller kvar nivån |
|---|---|---|
| T-RED-01 | låg → måttlig 2, måttlig → hög 258 | H-02, H-MOD-02, H-MOD-04 |
| T-RED-02 | låg → måttlig 2, måttlig → hög 258 | H-02, H-MOD-01, H-MOD-02, H-MOD-04 |
| T-RED-03 | låg → måttlig 2, måttlig → hög 258 | H-02, H-MOD-01, H-MOD-04 |
| T-RED-04 | låg → måttlig 2, måttlig → hög 360 | H-01, H-MOD-01, H-MOD-02, H-MOD-04 |
| T-RED-05 | måttlig → hög 602 | H-MOD-04: S-TJ-01 (betalningsmandat) höjer alltid H-MOD-04 till hög och C-TJ-05 riktar sig inte mot det |
| T-RED-06 | måttlig → hög 602 | H-MOD-01: S-TJ-02 (klientmedel) höjer alltid H-MOD-01 till hög och C-TJ-06 riktar sig inte mot det |
| T-RED-07 | låg → måttlig 2, måttlig → hög 390 | H-01, H-02, H-MOD-01, H-MOD-02, H-MOD-04 |
| T-SKATT-01 | 0 | inga; C-TJ-08 riktar sig mot alla PT-hot |
| T-BOLAG-01 | 0 | inga; C-TJ-09 riktar sig mot alla PT-hot |
| T-BOLAG-02 | låg → måttlig 2, måttlig → hög 600 | H-03 (ingen källa för flödeskontroll i adresstjänsten) |
| T-BOLAG-03 | måttlig → hög 602 | H-03 (grundnivå hög; ingen källa för flödeskontroll i företrädaruppdraget) |

Höjningarna följer direkt av den strukturella spänningen ovan och av att kontrollmålen inte längre gäller hela tjänsten. De är metodval som sakkunnig ska pröva, inte fel.

## Konservativ framtida negativ effekt

Katalogen innehåller bara positiva effekter. För framtida negativa faktorer kräver valideringen `vid_okant: preliminart_galler_ej`. Motorn väljer dessutom aldrig en negativ effekt från ett okänt villkor, även om någon kör en felaktig regelbas direkt utan validering. Ett bekräftat sant villkor kan fortfarande ge den tillåtna negativa effekten. Uteblivet svar får därmed inte sänka nivån.

## Verifieringsgräns

Slutverifiering 2026-10-18: **2 685 passerade, ett bortvalt livetest, inga fel**. Alla valda prov kördes exakt en gång i fyra separata pytestprocesser och 657 käll-/regel-/testfiler var oförändrade före/efter. Regelbas 2.0.0 validerar; kompilering och diffkontroll passerar. Scenariospår i B1, frivilliga observationsfält, lokal kontrollmatchning och hela syntetiska attest-/export-/återställningskedjan är integrerade. Tidigare övergångsfel och deras röda körningar är bevarade i arbetsjournalen; de är inte dagens slutresultat.

Den samlade oberoende kodgranskningen fann inga Critical/Important. Ett mindre framtida fynd återstår: olika faktor-ID/vikter med samma visningsnamn kan grupperas i huvudtexten; nuvarande katalog saknar sådana namn, och B1 bevarar hela beräkningen. Det måste åtgärdas innan en sådan katalog används.

Normalprovets AI-begäransfil är byteidentisk mot 1.6.0 (4/4 accepterade Testleverantor-svar), och 210/210 längre lokala svar är bevarade. Ordmått: 4 997 huvudtext och 16 859 B1. Användaren har tagit bort hårda redaktionella ordgränser; mätning och rådgivande varning finns kvar utan trunkering eller exportspärr. Word-exportens manifest och renderad layout är kontrollerade med LibreOffice/Poppler, inte Microsoft Word eller verklig medarbetarläsning. Positiva godkännanden har bara provats med uttryckligen syntetiska kopieattester.

Inga sakkunnigstatusar har höjts, inga riktiga AI-/registeranrop har gjorts och inga ändringar har committats eller pushats. De två öppna metodfrågorna ovan, M1–M4 och verklig sakkunnigprövning kvarstår.


## Offlineprov av två påhittade v7-byråer vid slutverifieringen

Före = sparad 1.6.0-baslinje, efter = 2.0.0 med samma profiler. Enbart katalog-ID:n och nivåer redovisas. Profilernas kontrollsummor är identiska och inga filer i originalbyråerna har skrivits om. Tabellen är teknisk motorverifiering, ingen sakgranskning. Alla nio tjänster har oförändrade nivåer; inga ändringar behöver förklaras. Hög inneboende PT-risk och mycket hög TF-risk följer de avgörande scenarierna nedan; okänd eller obelagd kontrollverkan ger ingen sänkning.

| Prov | Tjänst | PT före → efter | TF före → efter | Kvarstående PT före → efter | Avgörande scenarier i 2.0.0 |
|---|---|---|---|---|---|
| Fiktiv A | T-RED-01 | hög → hög | mycket hög → mycket hög | hög → hög | H-03:pt, H-01:pt, H-02:pt, H-MOD-02:pt, H-03:tf, H-TF-02:tf |
| Fiktiv A | T-RED-02 | hög → hög | mycket hög → mycket hög | hög → hög | H-03:pt, H-01:pt, H-02:pt, H-MOD-02:pt, H-03:tf, H-TF-02:tf |
| Fiktiv A | T-RED-03 | hög → hög | mycket hög → mycket hög | hög → hög | H-03:pt, H-01:pt, H-02:pt, H-MOD-02:pt, H-03:tf, H-TF-02:tf |
| Fiktiv A | T-RED-04 | hög → hög | mycket hög → mycket hög | hög → hög | H-03:pt, H-01:pt, H-02:pt, H-MOD-02:pt, H-03:tf, H-TF-02:tf |
| Fiktiv B | T-RED-01 | hög → hög | mycket hög → mycket hög | hög → hög | H-03:pt, H-01:pt, H-02:pt, H-MOD-02:pt, H-03:tf, H-TF-02:tf |
| Fiktiv B | T-RED-02 | hög → hög | mycket hög → mycket hög | hög → hög | H-03:pt, H-01:pt, H-02:pt, H-MOD-02:pt, H-03:tf, H-TF-02:tf |
| Fiktiv B | T-RED-03 | hög → hög | mycket hög → mycket hög | hög → hög | H-03:pt, H-01:pt, H-02:pt, H-MOD-02:pt, H-03:tf, H-TF-02:tf |
| Fiktiv B | T-RED-04 | hög → hög | mycket hög → mycket hög | hög → hög | H-03:pt, H-01:pt, H-02:pt, H-MOD-02:pt, H-03:tf, H-TF-02:tf |
| Fiktiv B | T-RED-05 | hög → hög | mycket hög → mycket hög | hög → hög | H-TJ-05:pt, H-03:pt, H-01:pt, H-02:pt, H-MOD-01:pt, H-MOD-02:pt, H-MOD-04:pt, H-03:tf, H-TF-02:tf |

V7-begärans hela innehåll jämfördes också per tjänst mot de sparade förehasherna: nio av nio identiska för dessa två prov. Lokala iakttagelser och scenarioutfall har inte tillförts AI-underlaget. Endast offlineberäkning gjordes, utan nya AI-anrop.


## H7.7 källbunden metodprövning 2026-10-19

H7.7:s metodunderlag 2026-10-19 omfattar tio syntetiska H7.1-kontraster med samma regelbaskontrollsumma som B-offline. Alla 40 tjänsteutfall blev hög inneboende PT, mycket hög TF och hög kvarstående PT. Mandat, bankinsyn, känd/okänd tjänstefördelning, period, tjänstestorlek och härledbar kundöverlapp skilde inte motorns scenariospår i dessa fall. När belagd effekt togs bort ändrades däremot nio PT-scenarier i bokföring, bokslut och deklaration; otäckta höga scenarier höll ändå kvar tjänsternas maxnivå. Sammanfattningsnivån ensam visar därför inte alla kontrollskillnader. Mandatkontrastens oavsiktliga textkonflikt har rättats och efterprovats separat: profil, scenario, kontrolltillämpning, sektor och insyn följer nu verkställighetsmandat/full bankinsyn, utan ändrad kontrollverkan eller motorbedömning. Ursprungliga föreprov och B-offline är bevarade. En generell blockmotivering om avgränsning även utan mandat är kvar som redaktionell rest; H7.1:s oberoende tekniska fixturgranskning är godkänd efter rättningen; detta är inte en sakkunnigprövning av metoden.

Kontrollen använder oförändrad regelbas 2.0.0. Samma fyra primär-PDF:er som källregistret hämtades och SHA-256-verifierades. Privata fulla scenariospår, källmanifest och mandatvariantens före-/efterfixprov är bevarade i H7:s körjournal. Originalfallen och B-offline har inte skrivits om. M1 avser här kontrollräckvidd, M2 TF, M3 exponering/omfattning och M4 summering/tak/dubbelräkning.

### Primärkällor och deras gränser

- **K1** [Länsstyrelsens vägledning](https://www.lansstyrelsen.se/skane/samhalle/betalning-ekonomi-och-pengar/forhindra-penningtvatt-och-finansiering-av-terrorism/gor-en-allman-riskbedomning.html), avsnitt Produkter och tjänster, Hot, Riskreducerande åtgärder. Stöder verksamhetsanknytning, tjänstevis relevans och faktisk effektprövning. Den fastställer inte programmets numeriska steg eller maxregel.
- **K2** [Tillsynsrapport 2026:14](https://www.lansstyrelsen.se/download/18.51b8c30c19d05558bd82e18e/1774259142687/Erfarenheter%20fr%C3%A5n%20l%C3%A4nsstyrelsernas%20penningtv%C3%A4ttstillsyn.pdf), s. 7–8. Betonar individuell tjänsteanalys och sambandet mellan faktiskt utförda utlandstransaktioner och utbildningsbrist. Kundkategori och leveranssätt behöver förklaras i förhållande till tjänsten.
- **K3** [Vägledning mars 2025](https://polisen.se/0be344afbcdff1a86db5cde12c2188c5/siteassets/dokument/om-polisen/penningtvatt/vagledning-till-redovisningskonsulter-och-skatteradgivare.pdf), s. 16–17, 23. Beskriver osanna fakturor, brottsvinster redovisade som försäljning och uttagna som lön/utdelning; faktura- och transportunderlag som varningssignaler för karusellbedrägeri. Det är inte en uttrycklig koppling mellan ren löneberedning och momsdeklaration.
- **K4** [NRA 2024/2025](https://polisen.se/0c34c8d8c94e1a371d8cca457b84fb0a/siteassets/dokument/om-polisen/penningtvatt/nationell-riskbedomning-av-penningtvatt-och-finansiering-av-terrorism-i-sverige-2024_2025.pdf), 7.19 s. 122–123. Beskriver sektorns faktura-/underlagsmissbruk, intäkter som tas ut som lön, och fakturaupplägg för svart arbetskraft. Kombination av redovisning och betalning nämns. Sektorbeskrivningen fastställer inte lika exponering eller insyn i varje uppdragsform.
- **K5** [Finanspolisens TF-lägesbild mars 2025](https://polisen.se/f4dc3a983cd5a7738db26e055dfebdca/siteassets/dokument/finanspolisen/fipo-informerar/fipo-informerar_terrorfinansiering_2025.pdf), s. 1–2, 4. Beskriver rapporterade insamlings-/vidareförmedlingsmönster, anonymiserande kanaler och möjliggörare. Materialet är rapporteringsbaserat, inte en skattning av TF-frekvens i löneuppdrag. Gemensamma kanaler för PT/TF innebär inte att alla PT-faktorer har samma TF-effekt.

### Öppna sakkunnigbeslut

Samtliga ställningstaganden nedan: **ÖPPET – ingen sakkunnigprövning utförd**. Alternativen är beslutsförslag, inte beslut. Även beslut att behålla metoden behöver skriftliga skäl.

| ID / metodfråga | Källstöd och gräns | Observerat oförändrat utfall | Sakkunnigens konkreta ställningstagande | Eventuell separat versionsändring | Regression/facit efter beslut |
|---|---|---|---|---|---|
| D1 Lön–moms H-MOD-02 | K3 beskriver karusellens fakturaunderlag; K1/K2 kräver tjänsteanknytning. Direkt stöd för ren löneberedning saknas i lästa avsnitt. | T-RED-04 har H-MOD-02 oavsett löneuppdragets mandat; C-TJ-04 täcker det inte. | Ange vilket arbetsmoment gör löneuppdraget till möjliggörare: moms-/fakturagranskning, löneuttag ur upplägg, eller endast indirekt kundexponering? Pröva behåll/villkora/avgränsa. | Endast efter beslut: kataloglänk och eventuellt strukturerat mandatvillkor; inget bortfall nu. | Ren lön utan momsmandat mot samma kund med kombinerat moms-/betalningsmandat; sakkunnig motiverar relevans och nivå separat. |
| D2 Lön–faktura H-01 samt intäkter H-02 | K4 beskriver fakturor för svart arbetskraft och intäkter→lön. Det stöder riskkedjor, inte att lönekonsulten alltid ser leverantörsfakturan. | Båda hot finns i T-RED-04; C-TJ-04 har H-02 men inte H-01 som mål. | Skilj underlag som behandlas i löneuppdraget från fakturor utanför uppdraget. Bestäm direkt, indirekt/villkorad eller otillräckligt belagd länk. | Eventuell mer precis katalogmotivering/uppdelning; aldrig omklassning enbart för lägre nivå. | Falskt löneunderlag, faktura utanför mandat, känd korskoppling mellan faktura och lön. Bevara hela nuvarande spåret som föredata. |
| D3 Portföljfaktor kontra tjänst | K1/K2 kräver koppling mellan kundtyp, arbetsmoment och sårbarhet. | `_valda_sarbarheter` läser globala villkor bland tjänstens katalogfaktorer. Lokala uppdragsbeskrivningar ger inte automatisk numerisk avgränsning. | Bestäm när gemensam utbildning/KYC faktiskt gäller alla tjänster och när geografi/bransch/ägande kräver belagd tjänstefördelning. Okänd fördelning får inte beskrivas som känd samtidig exponering. | Eventuell tjänstespecifik datamodell med explicit okändstatus; inte påslag ur fritext. | Samma portfölj men dokumenterat olika tjänsteexponering; känd respektive okänd fördelning. |
| D4 Kundöverlapp / M3 | Antal per tjänst anger inte vilka kunder som sammanfaller. Detta är matematisk evidensgräns, inte myndighetsriskregel. | AB6: 60 kunder, fyra tjänster med 24 vardera; 96 tjänstekopplingar. | Bekräfta vad som är känt. Minst 12 flertjänstkunder om alla 60 är populationen, eftersom 36 extra kopplingar kan bäras av 12 kunder med fyra tjänster. Identitet och riskkombination är okända. | Ingen automatisk kombinationsfaktor. Eventuell ny explicit överlappsuppgift beslutas separat. | Två tillåtna kundfördelningar med samma marginaltal men olika risköverlapp; ingen påhittad viss kombination. |
| D5 Maxaggregering | K1 stöder motiverad riskbedömning; max per scenario är projektets BT-TJ-01. | Max av PT/TF var för sig; ett otäckt högt PT-scenario håller kvar hög nivå trots effekt på andra. I den separata äldre syntetiska fixturen `m2_bas`: bokföring kvar måttlig; skatte-/bolagsbas hög→måttlig. Den har annan profil än H7.1 och är ingen före-/efterjämförelse av en metodändring. | Avgör om maxregeln bäst representerar tjänstens risk eller kräver kompletterande exponering/motivering. Kontrollera om otäckt scenario är relevant innan smala mål ändras. | Vid annan aggregation: ny regelversion, bevarade föreutfall, nytt expertfacit. Ingen medelvärdesberäkning nu. | Ett högt mot många låga; liten men väsentlig exponering; kontroll endast på ett av två maxscenarier. |
| D6 TF-matris / M2 | K5 ger modus och rapporteringsbegränsning; den bestämmer inte konsekvensen eller de nio cellerna. | Allvarlig TF-konsekvens alltid; låg/medel/hög sannolikhet ger måttlig/hög/mycket hög. TF reduceras inte av kontrollregeln. | Definiera konsekvensens skyddsintresse och enhet. Avgör fast allvarlig och separata faktorers relevans samt hur kontrollernas TF-effekt ska beskrivas. Ingen regel att TF måste understiga PT. | Ändrad TF-konsekvens/matris/reduktion först i separat metodbeslut. | Nio matrisfall, särskilda TF-modus, PT-faktor utan visad TF-kedja, belagd/okänd TF-kontroll. |
| D7 H-03 och ideell faktor | K5 beskriver flöden och gemensamma kanaler men inte ett generellt PT-påslag av organisationsformen. | S-ARB-05 möjliggör H-03 både PT/TF. Ideell+PEP ger mycket hög TF via H-03. | Pröva om två indikatorer avser samma scenario/kunder och varför PT/TF höjs; historiskt bevarad nivå är inte sakfacit. | Eventuell dimensions-/villkorsändring kräver redovisad sänkning/höjning och källgrund. | Ideell ensam, PEP ensam, kombination med känt/okänt överlapp. |
| D8 Kontrollmål / M1 | K1 kräver effektbedömning; det anger inte ett stegs avdrag för valfri verksam kontroll. | BT-KVAR-03 kräver samma hot/tjänst + belägg. C-TJ-08/09 täcker samtliga tre PT-hot; TF-exklusion gör att katalogens totalförbud inte stoppar detta. | Pröva varje mål mot faktisk observation, mandat, stickprovstäckning, period och begränsningar. Avgör om hela PT-täckningen och ett steg är motiverade. Katalogmål är inte belägg för lokal effekt. | Eventuellt riktningar/reduktionsprincip, efter beslut; ingen utvidgning för att kringgå max. | Rätt hot/fel tjänst; rätt mål/okänd effekt; smalt stickprov; ett otäckt maxhot; 08/09 hela PT-sidan. |
| D9 Summering/tak / M4 | K2 beskriver möjlig samverkan, inte oberoende, +1 eller mättnad efter visst antal. | Alla 21 hot medel; medelraden gör P=V. Medel PT-bas når hög med +1; låg TF-bas når hög med +2. | Pröva korrelerade faktorer och om taket döljer skillnader som behöver annan beskrivning. Fler faktorer behöver inte ge högre nivå, men orsaker ska synas. | Eventuell viktning/ersättning/skala behöver nya regelbindningar. | Samma orsak med två indikatorer mot två oberoende orsaker; ersatter efter hot-/dimensionsfilter; mättnadskontrast. |

### Beslutsprotokoll och separat ändringsarbete

För varje D-ID behövs: namngiven sakkunnig, kompetens/roll, datum, lästa källversioner, bedömd giltighet per uppdragsform, behåll/ändra och skäl, osäkerhet, konsekvens för PT/TF, godkänt kontrastfacit samt separat beslutsansvarig. Alla fält är tills vidare obesvarade. Byrån bekräftar fakta; sakkunnig bedömer metod. Ingen textformulering eller lokal riskacceptans ersätter metodbeslutet.

Efter uttryckligt ändringsbeslut: egen implementeringsuppgift med versionsändring, nya modellbindningar, frysta före-/efterfacit, regressionsprov och ny fullsvit; ny sakgranskning före operativ användning. Om beslutet är behåll ska även begränsningarna framgå intill risköversikten. Dokumentförbättringar kan fortsätta medan dessa metodfrågor är öppna.
