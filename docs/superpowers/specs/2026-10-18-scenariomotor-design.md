# Scenariomotor: hot och sårbarheter som blir risker

**Status:** tekniskt implementerad och verifierad 2026-10-18 enligt [genomförandeplanen](../plans/2026-10-18-scenariomotor.md): 2 685 passerade, ett bortvalt livetest. Bygger vidare på [huvudspecens](2026-10-08-riskanalys-design.md) revision 36. Samtliga nivåer, kopplingar och matrisval är fortfarande ogranskade metodval; M1–M4 och verklig sakkunnigprövning återstår. Inga sakkunnigstatusar ändras.

## Varför

Användaren vill att riskmotorn bedömer risk på det sätt som Länsstyrelsen beskriver: risken är sannolikheten att ett eller flera hot utnyttjar en eller flera sårbarheter, med konsekvensen att tjänsten utnyttjas.

Dagens motor gör inte det:
- Nivån räknas som tjänstens grundnivå plus summan av alla sårbarheter som gäller. Hoten listas men påverkar inte nivån.
- Ingen sårbarhet är kopplad till något hot.
- Ingen faktor kan sänka risken.
- En kontroll med belagd funktion sänker hela tjänsten ett steg, oavsett vilka hot den täcker.

Därför kan dokumentet inte motivera nivån med den kedja som tillsynen efterfrågar. Forvis Mazars (Skåne 3647-2026), Hanko och Stella sanktionerades för att nivåer saknade en analys av hur hot och sårbarheter samverkar.

## Källor och vad de kräver

| Källa | Krav som styr designen |
|---|---|
| 01FS 2024:20, 12FS 2024:8 och 14FS 2024:11, 2 kap. 2 § | Identifiera och *analysera* hot, med hänsyn till egen rapportering och myndigheternas tillvägagångssätt. Identifiera och analysera sårbarheter. *Värdera riskerna som är förenade med de bedömda hoten och sårbarheterna*. Motivera nivåerna. |
| Länsstyrelsen, *Gör en allmän riskbedömning* | Hot = sätt tjänsten kan användas. Sårbarhet = svaghet som kan utnyttjas. Risk = sannolikheten att hot utnyttjar sårbarheter. Faktorer kan *öka eller minska* risken. En sårbarhet ensam eller i kombination kan göra ett hot verkligt. Exempelmatris: tjänstens egen risk × sannolikheten för riskfaktorer. Åtgärder får tas med om deras faktiska effektivitet bedöms före sammanvägningen. |
| Tillsynsrapport 2026:14, s. 6–10 | Olika tjänster utsätts för olika hot, som påverkas av olika sårbarheter. En motiverad nivå ska bygga på alla relevanta sårbarheter *tillsammans med hot*, för tjänsten och för de enskilda riskfaktorerna. NRA:s sektorsrisk ska beaktas. |
| EU:s överstatliga riskbedömning, metod v1.1 | Analysenheten är scenariot (tillvägagångssätt × sektor). Hotnivå och sårbarhetsnivå bedöms var för sig och kombineras i en matris, viktad 40/60 mot sårbarhet. |
| NRA 2024/2025, avsnitt 3.1 och 8 | Hotnivå och sårbarhetsnivå ger ett riskvärde; därefter vägs konsekvens in. Enligt FATF är risk en funktion av hot, sårbarhet och konsekvens. |
| AMLA, utkast till riktlinjer art. 10.4 AMLR (§ 15–16, 23, 25, 29–30) | Viktade riskfaktorer med dokumenterade skäl. Ingen enskild faktor får oproportionerligt styra utfallet. Kontroller ska kopplas till de risker de minskar. Kvarstående risk bestäms per inneboende risk, och hög inneboende risk kan inte elimineras helt. Utkast, inte gällande rätt. |

## Mål

1. Varje erbjuden tjänst bedöms per **scenario**, ett för varje hot i tjänstens hotlista.
2. Varje scenario har en **hotnivå**, en **sårbarhetsnivå** byggd bara på de sårbarheter som möjliggör just det hotet, en **sannolikhet**, en **konsekvens** och en **inneboende risk**.
3. En kontroll sänker bara de scenarier vars hot den täcker enligt källbunden räckvidd, och bara när utformning, genomförande och effekt är belagda.
4. Tjänstens nivå är det högsta scenariots nivå, separat för penningtvätt (PT) och TF. Dokumentet anger vilket scenario som avgör nivån och varför.
5. Allt är deterministiskt och spårbart till regelbasen. Varje nytt tal och varje ny koppling märks `metodval` med källa och `grund`.

## Icke-mål

- AI bedömer ingen nivå. AI ser inga nivåer, scenarioresultat eller privata uppgifter (oförändrat).
- Ingen sammanvägd risknivå för hela byrån (oförändrat).
- Sanktionsrisken behåller sin separata metod.
- Konsekvensen för TF är fortsatt alltid allvarlig. PT-konsekvensen är fortsatt tjänstens grundvärde.
- Inga nya riskfaktorer som sänker risken läggs in i katalogen i detta bygge; schemat ska bara kunna bära dem.
- Ingen ändring av AI-underlaget eller skrivformat v7.
- Sakkunnigstatus höjs aldrig.

## Får inte hända

- En nivå som inte kan förklaras från regelbasen och byråns bekräftade uppgifter.
- En byrå sänker sin risk genom att markera hot som irrelevanta eller genom att avstå från att svara.
- Avsaknad av egna rapporter sänker hotnivån. NRA tolkar få rapporter som låg riskmedvetenhet.
- En kontroll sänker ett scenario den inte täcker.
- Äldre bedömningar, fastställda paket eller exporter slutar gå att läsa eller verifiera.

## Modellen

### Begrepp

- **Scenario** = (tjänst, hot, dimension). Tjänstens hotlista i `tjanster.yaml` avgör vilka scenarier som finns; hotets `dimensioner` anger PT, TF eller båda. Utan uttryckliga dimensioner gäller bara TF för `H-TF-*`, PT och TF för övriga hot med `galler_tf: true`, annars bara PT.
- **Möjliggörande sårbarhet**: ny katalogkoppling `Sarbarhet.hot: tuple[str, ...]`, de hot som sårbarheten kan göra verkliga. Varje koppling motiveras i `metodmotivering` och har källa.

### Steg 1: hotnivå H (låg, medel, hög)

- **Grund:** nytt fält `Hot.niva` (låg, medel eller hög), `metodval`, med källhänvisning till NRA, Finanspolisen eller tillsynsrapporten som visar hur vanligt och lönsamt tillvägagångssättet är för sektorn.
- **Höjning:** +1 steg (som högst hög) om byrån har uppgett att tillvägagångssättet iakttagits i den egna verksamheten för tjänsten. Underlaget kan vara misstankerapporter, misstankebaserade avböjanden eller egna observationer.
  - Nytt lokalt flervalsfält per tjänst: `P-TJ.{slug}_iakttagna_hot`, med tjänstens hot-ID:n som val.
  - Fältet är frivilligt och ingår aldrig i AI:s tillåtelselista.
- **Ingen sänkning** när inget har iakttagits.

### Steg 2: sårbarhetsnivå V (låg, medel, hög)

`V = steg(tjänstens grund_sannolikhet, Σ effekt av tillämpade sårbarheter som möjliggör hotet)`, med golvet låg och taket hög.
- `grund_sannolikhet` blir därmed **tjänstens egen sårbarhet**, i Länsstyrelsens matris kallad produktens eller tjänstens egen risk.
- Effekten tillåts vara negativ i schemat (−2 till +2, aldrig 0). Katalogen har dock bara positiva effekter i detta bygge.
- Kombinationsregler (`ersatter`) fungerar som idag, men bara inom samma scenario.

### Steg 3: sannolikhet P

Ny metodmatris `BT-SANN-02` (H × V), inspirerad av EU-metodens 40/60. Den tregradiga matrisen nedan är projektets eget diskreta metodval, inte en direkt återgivning eller validering av SNRA:s modell för kvarstående risk:

| H \ V | låg | medel | hög |
|---|---|---|---|
| låg | låg | låg | medel |
| medel | låg | medel | hög |
| hög | medel | hög | hög |

### Steg 4: inneboende risk per scenario

Befintlig riskmatris (P × konsekvens). Konsekvensen är tjänstens `grund_konsekvens` för PT och allvarlig för TF.

### Steg 5: kontroller per scenario

Användaren bad om en lösning som är enkel för byrån men ändå korrekt, och lät Claude välja efter research. Källorna kräver tre saker:
- **Kontrollen kopplas till de risker den minskar.** Det säger AMLA § 25; ICAEW:s och ACCA:s mallar för mindre byråer anger åtgärder per risk.
- **Effekten är belagd.** Länsstyrelsen kräver en utvärdering av om åtgärden i realiteten medverkat; AMLA § 26–28 kräver belägg som kontroller, granskningar och tillsynsfynd.
- **Sänkningen kan inte bli hel.** Hög inneboende risk kan inte elimineras (AMLA § 29).

Valt upplägg:

1. **Katalogen anger kontrollens mål.** Nytt fält `Kontroll.riktar_sig_mot: tuple[Riktning, ...]`, där varje post anger tjänst och de hot kontrollen är utformad att upptäcka eller förhindra. Varje post har källa och motivering, och märks `metodval` och `ej_granskad`.
   - Fältet är skilt från `rackvidd`. Räckvidden beskriver vad en kontroll kan *observera* och är aldrig positiv täckning (spec rad 1065). Målet beskriver vad kontrollen är *utformad mot*.
   - Byggaren smalnar av målen till de hot som källan faktiskt stöder. En kontroll som riktar sig mot allt i tjänsten godtas inte.
2. **Byrån svarar per kontroll, inte per scenario.** De befintliga fasta valen om utformning, genomförande och effekt, med belägg, räcker. Inga nya obligatoriska frågor tillkommer.
3. **Ny regel `BT-KVAR-03`.** Ett scenario sänks ett steg, som lägst låg, när minst en av tjänstens kontroller uppfyller båda villkoren:
   - den riktar sig mot scenariots hot enligt katalogen,
   - den har belagd utformning och genomförande samt effekt bedömd som verksam för samma period.
   
   Annars gäller `BT-KVAR-01`: kvarstående risk är lika med inneboende risk. Sänkningen är högst ett steg.
4. **Byrån kan bara stoppa en sänkning, aldrig skapa en.** Motorn läser inte den lokala analysen, eftersom analysen byggs på och binds till bedömningen; det skulle ge ett kretslopp.
   - I stället prövar den befintliga spärren för faktisk reduktion (block 12 i `analys/provning.py`) varje scenario som motorn har sänkt.
   - Om byråns kontrollprövning för scenariots hot anger täckningen `saknas`, uppstår ett blockerande fynd som hindrar fastställelse. Byrån åtgärdar det genom att rätta kontrolluppgifterna i profilen och bedöma om, eller genom att dokumentera en metodkonflikt.
   - Varje sänkt motorscenario behöver också positiv lokal prövning av samma hot och minst en kontroll bland dess `tackande_kontroller`. Saknad matchning eller ett positivt svar om en annan kontroll är inte stöd för sänkningen. Ordinarie beläggs- och räckviddskrav gäller fortfarande. Osänkta scenariers kontrollbrister hanteras i kontroll-/gapprövningen utan krav på att också de ska få reduktion.
   - Utan lokal analys gäller katalogen ensam, och de befintliga spärrarna för saknad analys gäller som idag. (Claudes beslut 2026-10-18.)

Kostnad om fel: om katalogens mål blir för breda sänks scenarier som kontrollen inte täcker. Det motverkas av krav på källa per hot, av byråns möjlighet att stänga sänkningen och av sakkunnig prövning.

### Steg 6: tjänstens nivå

- PT inneboende = max över PT-scenarier. PT kvarstående = max över PT-scenariernas kvarstående risk.
- TF = max över TF-scenarier. TF har ingen kontrollsänkning, som idag.
- **Avgörande scenarier** är de som ligger på maxnivån. Alla redovisas; programmet väljer inte bland dem.

### Okända uppgifter

Ett okänt villkor ger preliminärt utfall enligt sårbarhetens `vid_okant`, som idag. Ett okänt iakttagelsefält ger ingen höjning, men tjänsten markeras inte preliminär för det.

## Datamodell

- `Hot`:
  - nytt `niva: Sannolikhet`, obligatoriskt i metod 2,
  - nytt `nivamotivering: str`.
- `Sarbarhet`:
  - nytt `hot: tuple[str, ...]`; utan scenariometod kan det vara tomt. Med scenariometod blockerar valideringen tom eller lokalt overksam hot-/dimensionskoppling,
  - `Effekt.sannolikhet` tillåts −2…2 utom 0.
- `Kontroll`: nytt `riktar_sig_mot: tuple[Riktning, ...]`, där `Riktning` består av `tjanst`, `hot`, `kallor`, `grund` och `motivering`.
- `Tjanstbedomning`: nytt valfritt fält `scenarier: tuple[Scenariobedomning, ...] = ()`. Befintliga fält (`inneboende`, `terrorfinansiering`, `kvarstaende`, `tillampade_sarbarheter`, `regelspar`) behålls och fylls med tjänstens maxvärden, så att äldre konsumenter fungerar.
- `Scenariobedomning`:
  - `hot`, `dimension` (pt eller tf), `hotniva`, `iakttaget: bool`,
  - `sarbarheter` (tillämpade och möjliggörande), `sarbarhetsniva`,
  - `sannolikhet`, `konsekvens`, `risk`,
  - `tackande_kontroller`, `kvarstaende`,
  - `regelspar`.
- `metod.yaml`: nya regelobjekt `BT-HOT-01` (hotnivå och höjning), `BT-SARB-01` (sårbarhetsnivå), `BT-SANN-02` (matris), `BT-KVAR-03` (scenariosänkning) och `BT-TJ-01` (maxaggregering). Alla `metodval` och `ej_granskad`.
- Regelbasen höjs till **2.0.0**. Äldre bedömningar, med regelbas 1.x och utan `scenarier`, läses och visas som förut.

## Katalogarbete

Detta är sakarbete med källor, inte kod:
- **Hotnivå för de 21 hoten,** med källhänvisning. Standardvärdet är medel. Hög sätts bara där NRA, Finanspolisen eller tillsynsrapporten uttryckligen beskriver tillvägagångssättet som vanligt eller växande för sektorn. Låg sätts där källan beskriver det som ovanligt.
- **Kontrollernas mål:** för var och en av de 13 kontrollerna, de hot den är utformad mot per tjänst, med källa.
- **Koppling från var och en av de 28 sårbarheterna till de hot de möjliggör,** med en kort motivering. Tillsynsrapportens exempel ska kunna reproduceras:
  - riskbransch + falska fakturor,
  - personal utan kompetens + falska fakturor,
  - utlandstransaktioner + personal utan utbildning + oupptäckta utlandsflöden.

## Dokumentet

- Varje tjänsteavsnitt får en kompakt **scenariotabell**, en rad per scenario. Kolumner: hot, hotnivå (med "iakttaget" när det gäller), möjliggörande sårbarheter som gäller, sannolikhet, risk, täckande kontroll och kvarstående. Den ersätter kategoriöversikten i v7.
- **Nivåmotiveringen** utgår från avgörande scenarier. Exempel: "Avgörande: Osanna och falska fakturor. Hotnivå hög (NRA). Sårbarhetsnivå hög: tjänstens egen nivå medel, höjd av riskbransch och saknad bankdata. Sannolikhet hög, konsekvens betydande, risk hög. Ingen kontroll med belagd effekt täcker scenariot." Byråns egen bedömning står kvar separat.
- **B1** får hela scenarioberäkningen med regelspår.
- **Längden** får inte öka. Tabellen ersätter kategoriöversikten och delar av utfallslistorna. Det ska mätas.

## Verifiering

- Prov skrivs före kod:
  - för varje steg,
  - för matrisens nio celler,
  - för att kontroller bara sänker täckta scenarier,
  - för max och avgörande scenarier,
  - för att avsaknad av iakttagelse aldrig sänker hotnivån,
  - för äldre bedömningar.
- **Typfallen** räknas om. Varje ändrat utfall förklaras i en jämförelsetabell mot dagens motor. Lindvikenprovet och de två påhittade v7-byråerna ingår.
- **Fullsvit och regelbasvalidering** körs. AI-begäran ska vara byteidentisk före och efter för v7, eftersom motorn inte når AI.
- **Ett AI-anrop** behövs inte för detta bygge.

## Preciseringar efter byggargranskning (Claudes beslut, att pröva vid läsning)

1. **TF i scenarier.**
   - `Hot` får `dimensioner`: H-TF-01–03 är bara TF, H-03 är både PT och TF, övriga hot är bara PT (härlett från `galler_tf` och hotets art).
   - Ett TF-scenarios sårbarhetsnivå utgår från `grund_tf_sannolikhet`, som BT-TF-01 gör idag.
   - `Sarbarhet.galler` filtrerar fortfarande: en sårbarhet räknas i ett TF-scenario bara om den gäller TF eller båda.
   - Ett hot har en `niva` för båda dimensionerna, och en iakttagelse höjer båda.
2. **En hotnivå per hot, inte per sektor.** Skillnader mellan sektorerna fångas av tjänstens egen grundnivå och den befintliga NRA-referensen per tjänst. Kostnad om fel: ett hot som är vanligt i en sektor men ovanligt i en annan får samma nivå; det kan läggas till senare som en överstyrning per sektor.
3. **Hoten H-TJ-01–11** ("Utnyttjande av tjänsten") är scenarier, men kopplas bara till tjänstespecifika sårbarheter (område `tj`) och verksamhetsspecifika sårbarheter (område `verk`). De samlar alltså inte alla sårbarheter, så att dagens summering inte återkommer genom dem.
4. **Katalogarbetet görs i bygget.** Byggaren tar fram hotnivåer och kopplingar med källor, märkta `metodval` och `ej_granskad`. Regelbasvalideringen **underkänner** metod 2 om en sårbarhet saknar koppling till något hot, så att risken aldrig sänks tyst. Typfallsjämförelsen ska förklara varje nivå som sjunker jämfört med dagens motor.
5. **Lokala scenarier.** Den lokala analysens scenarier (`Scenarioanalys` med `hot`) kopplas till motorns scenarier via hot-ID och förblir byråns kvalitativa prövning. Spärren för faktisk reduktion i `analys/provning.py` (block 12) prövas per motorscenario med sänkning i stället för per tjänst. Dokumentets scenariotabell ersätter kategoriöversikten; den lokala scenariotabellen står kvar.

## Granskningspreciseringar vid Codex övertagande 2026-10-18

- En sårbarhet som tjänsten listar får inte sakna en verksam koppling till tjänstens egna hot och dimensioner. Enbart ett existerande hot-ID någon annanstans i katalogen räcker inte; om en faktor avgränsas från en tjänst måste det vara uttryckligt och motiverat.
- Ersättningsregler tillämpas inom scenariot efter hot- och dimensionsfilter. Den tidigare globala tjänstelistan får inte styra vilka sårbarheter ett scenario förlorar.
- Modellidentiteten omfattar den nya beräkningsmodulen och dess beroenden. Äldre modellrapporters frysta filförteckningar behålls för historisk verifiering.
- Alla avgörande scenarier redovisas. Identiska beräkningsförklaringar får grupperas i huvudtexten med samtliga hot namngivna; B1 bevarar varje scenarios fullständiga beräkning och regelspår. Huvudtextens längd mäts mot samma syntetiska föreprov.
- Nya regelkällor serialiseras bara när de finns. Äldre regelbaser och sparade bedömningar utan scenariofält behåller sina innehållssummor.

## Lämnat åt byggaren

Modulindelning, namn på hjälpfunktioner, tabellens exakta läsbara layout, och hur scenariofälten serialiseras så att äldre summor består.


## Förtydligat längdbeslut 2026-10-18

Användaren har tagit bort hårda redaktionella ordgränser, inklusive det tidigare normalprovets absoluta tak. Ordmått och rådgivande längdvarning finns kvar. Fullständiga lokala svar, samtliga scenarioberäkningar och spårbarhet får inte kapas för ett ordtal. Läsbarhet och faktiska upprepningar bedöms redaktionellt; en längre huvudtext är inte i sig ett programfel eller en exportspärr. AI-delarnas separata skrivkontrakt är oförändrat.
