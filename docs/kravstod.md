# Resultatrapport, analysbilaga och underlag

Nya rapportbyggen använder nu resultatrapporten (V9). Byrån lämnar samma gemensamma svar och tjänstevisa prövningar som tidigare. Rapportbytet tillför inga sakfrågor eller AI-anrop.

- **Resultatrapport:** sammanfattning, riskutfall, gemensamma scenarier, tjänsternas skillnader, hela PT-/TF-motiveringarna och åtgärder.
- **Analysbilaga A:** hela den utförliga analysen, med hänvisningar från resultatrapporten.
- **Underlagsbilaga B1:** originaluppgifter, beräkningar, belägg och fullständiga maskinfynd.

Alla tre delarna hör till samma paket och fastställs tillsammans med ett gemensamt manifest. En utkastsexport kan innehålla öppna brister; den är inte en fastställd riskbedömning. Långa motiveringar återges hela även när rapporten därför överskrider sidmålet.

## Skapa eller uppdatera rapporten

I det lokala intaget visas tre nedladdningar: **Resultatrapport**, **Analysbilaga** och **Underlagsbilaga**. Samma aktualitets- och integritetskontroll gäller för alla tre. Ett äldre V8-utkast uppdateras i sitt sparade format. Välj den särskilda handlingen att skapa resultatrapporten när ett formatbyte önskas; originalet bevaras och AI-texterna används på nytt utan AI-anrop.

CLI kan välja format uttryckligen:

```sh
riskanalys granska BYRA --rapportformat v9
riskanalys exportera BYRA
riskanalys sakgranska BYRA --resultatrapport
```

Det sista kommandot visar hela resultatrapporten och dess aktuella struktursumma. Efter faktisk läsning kan exakt alla R-avsnitt godkännas samlat:

```sh
riskanalys sakgranska BYRA --resultatrapport --godkann --visad-struktursumma VISAD_SUMMA --namn 'Sakgranskare' --roll FfR
```

Det godkänner inte A eller B1. Bilagornas ordinarie sakgranskning, analysgodkännanden och övriga fastställelsekrav kvarstår. Fel eller inaktuell summa sparar inga R-attester. Vid formatbyte krävs förnyad sakgranskning av alla tre delarna, även när analysen är oförändrad; gamla V8-attester förs inte över. Nya rapportbyggen använder V9 som standard, medan `--rapportformat v8` fortfarande kan skapa V8 uttryckligen. Historiska fastställda paket verifieras från sparade bytes utan omrendering.

Huvudrapporten är kortare; hela paketet är något längre eftersom analysen finns kvar i A. [Slutprov, mätning och samtliga provfiler för Claude](superpowers/reviews/2026-10-23-resultatrapport-r4-r7.md).

## Planer och kombinationsgrupper


Programmet har lokalt underlag för förändringar och samtidig exponering. Riskmotorns metod är oförändrad. Planantaganden och grupper skickas inte till AI och tolkas inte automatiskt till poäng.

## Planera och utvärdera en förändring

Öppna **Planer och kombinationsgrupper** i det lokala intaget. Välj tjänst, registrera plan-ID och förändringstyp. Beskriv kundtyper, arbetsmoment och befogenheter, underlag och insyn, leverans och geografiska anknytningar. Frivilliga svar per fråga är planantaganden och ersätter inte aktuella profiluppgifter. En registrerad plans ID och tjänst behålls; använd en ny plan för en annan tjänst.

Öppna den sparade planen. Dokumentera en faktiskt genomförd utvärdering av den allmänna riskbedömningen: vilket underlag som prövats, berörda hot och sårbarheter, påverkan på risk och rutiner samt vad som uppdateras eller motiverat behålls. Datum får inte ligga i framtiden eller före de faktiska beläggen. Ett planerat framtida antal kan däremot avse en framtida period; det är inte faktisk historik.

Därefter kan ett tidigare bekräftat nej ändras till ja. När erbjudandet sparas med giltig utvärdering avslutas en plan av typen Ny tjänst atomiskt med profilsparningen. Genomförandedatum, ansvarig, den då gällande utvärderingen och planens oförändrade innehåll bevaras som historik. Ändringar av redan erbjudna tjänster avslutas med en särskild registrering av faktiskt genomförande i webb eller CLI. Avsett datum eller dagens erbjudandeflagga avslutar ingen plan automatiskt. Saknas en aktuell utvärdering stoppar programmet införandet. En genomförd plan kontrolleras inte på nytt mot senare byråfakta, bedömningsdatum eller regelbas. Den får inte redigeras eller återanvändas vid återinförande: registrera en ny plan. Den ordinarie årliga utvärderingen och uppdatering vid förändrade förhållanden gäller fortsatt.

Ett okänt erbjudande kan bekräftas vid första kartläggningen; kända tidigare nej, även i äldre profilformat, får inte kringgå spärren genom ett mellanliggande okänt svar.

Vid ett verkligt införande väljer byrån uttryckligen vilken aktiv plan av typen Ny tjänst som genomförs. Även en enda kandidat behöver väljas; flera planer markeras aldrig automatiskt som genomförda. Ej valda planer förblir aktiva och omfattas fortsatt av prövningen inför fastställelse. Ett okänt svar med en redan registrerad införandeavsikt är inte en väg runt planvalet.

En övergiven plan kan återkallas med datum, ansvarig funktion och motivering. Innehållet och tidigare utvärderingar bevaras som oföränderlig historik. Återkallad plan spärrar inte ett nytt giltigt införande, men kan inte själv genomföras, återkallas igen, redigeras eller användas som aktuell planutvärdering. En genomförd plan kan inte återkallas. Ny avsikt kräver nytt plan-ID.

Det samlade tjänsteurvalet begär planval vid just införanderaderna och behåller hela urvalet, underlaget och funktionen när något saknas. Alla erbjudanden och valda genomföranden sparas i ett enda steg; ett felaktigt val lämnar hela profilen oförändrad. Ändras profilen under arbetet visas de aktuella erbjudandena och kandidaterna för ny jämförelse och bekräftelse.

En ännu inte genomförd plan kräver omprövning om planen, källan eller en relevant sakuppgift ändras. För att uppdatera beläggen för oförändrade planvärden fyller du i nytt underlag, funktion och datum samt eventuell period. Lämna dessa beläggsfält tomma när endast planbeskrivningen ändras och de tidigare antagandena med sina belägg ska behållas.

För ett felregistrerat nej finns en särskild rättelse med motivering, källa, ansvarig funktion och datum. Den får inte användas för att kringgå en verklig registrerad förändringsplan. Före- och efteruppgifter samt ursprunglig profilrevision journalförs. Journalen registrerar begärd rättelse före profilskrivning; vid skrivfel visar den sparade profilen om eftervärdet genomfördes.

Planutvärderingar flyttar inte årsfristen för hela den allmänna riskbedömningen. Historikändringen gör befintlig analys inaktuell: förnya bindningen, jämför underlagen och sakpröva igen. Profiländringar kräver dessutom en ny aktuell bedömning enligt ordinarie flöde. Historiska beslut bevaras, men återanvänds inte som godkännanden av nya fakta.

## Beskriv en kombinationsgrupp

Ange en tjänst, ett beständigt grupp-ID, avgränsning och beskrivning, tjänstens relevanta sårbarhets-ID:n samt antal och bas. Välj en population, **kunder** eller **uppdrag**, som gäller båda antalen. Antal och bas ska avse samma period, källa och bekräftelse. Tomt antal betyder okänt; 0 är ett faktiskt antal. Bas 0 betyder inte låg risk.

Beskriv hur samförekomsten har belagts. Exempel: samma åtta uppdrag har två egenskaper. Separata marginaltal om åtta i vardera kategorin styrker inte att det är samma uppdrag. Överlappande grupper summeras inte till unika totaler. Programmet kan kontrollera den deklarerade populationen och metadata, men kan inte avgöra den verkliga enheten från ett bart heltal.

Gruppen visas i rätt tjänsts sårbarhetsunderlag. Byrån behöver pröva vad den betyder lokalt och vid behov uppdatera analys och rutiner. En registrerad grupp är inte ett automatiskt beslut om dess betydelse för risknivån. Numerisk anslutning väntar på preciserade sakkunnigbeslut i det befintliga beslutsformuläret.

## CLI och dokumentation

Webb och CLI använder samma spar- och förändringskontroller. CLI kan läsa typat lokalt underlag från YAML:

```sh
riskanalys plan BYRA --fil plan.yaml
riskanalys utvardera BYRA --plan PLAN_ID --beskrivning 'Genomförd utvärdering med underlag, hot, sårbarheter, påverkan och beslut med skäl'
riskanalys genomfor-plan BYRA PLAN_ID --datum ÅÅÅÅ-MM-DD --ansvarig 'Ansvarig för genomförandet'
riskanalys aterkalla-plan BYRA PLAN_ID --datum ÅÅÅÅ-MM-DD --ansvarig 'Ansvarig funktion' --motivering 'Avsikten ska inte genomföras'
riskanalys bekrafta BYRA P-TJ.red01_erbjuds ja --kalla 'Prövat uppdragsavtal' --plan PLAN_ID
riskanalys kombinationsgrupp BYRA --fil grupp.yaml
riskanalys bekrafta BYRA P-TJ.red01_erbjuds ja --kalla 'Tidigare uppdragsavtal' --rattelse --motivering 'Fel vid den första registreringen'
```

En minimal planfil har följande form. Innehållet är ett påhittat exempel; verkliga underlag ska ligga i byråns privata datamapp utanför Git.

```yaml
id: nytt_bokslut
tjanst: T-RED-02
typ: ny_tjanst
beskrivning: 'Planerade bokslutsuppdrag för ägarledda bolag med bankunderlag via kunden och digital leverans inom Sverige.'
uppgifter: {}
```

Den fullständiga analysens gemensamma mekanismer för aktiverade faktorer står i D-ARB.5 i A, lokal tillämpning och grupper vid tjänsten i A, fullständiga motorberäkningar samt planunderlag och förändringsutvärderingar i B1. I V9 utgör resultatrapport, A och B1 tillsammans dokumentationen; V8:s äldre läsrapport och B1 bevaras i äldre paket. Exporten ersätter inte verksamhetens information, utbildning eller sakliga utvärdering.

## Uppgradering av befintlig installation

Profilmodellernas ändring ger ny källbunden modellidentitet. Befintliga analysgodkännanden och modellriskunderlag kan därför inte återanvändas utan förnyelse efter uppgraderingen, även om risknivåerna blir lika. Följ ordinarie flöde med aktuell bedömning, jämförelse av underlag, uttrycklig analysförnyelse, sakprövning och nytt godkännande. Historiska fastställda paket bevaras.

Planposter från den första implementationen saknar genomföranderegistrering. Programmet antar inte att de är genomförda utifrån ja eller avsett datum. Genomförandet behöver registreras uttryckligen efter kontroll av underlag; den nuvarande utvärderingsbindningen måste då vara giltig. Genomförda planposter från det nya flödet förblir sedan historik.

## Gemensam byråanalys och tjänstevis riskprövning

Nya analyser i webb och kommandorad använder schema 2. Välj först tjänster ur standardkatalogen; välj bort dem som inte erbjuds och lämna osäkra svar som okända. Urvalet är ett förslag tills det bekräftas med källa, ansvarig och datum. Ett tidigare bekräftat nej som blir ja följer planflödet ovan. En tjänst utanför katalogen ska anges under övriga förhållanden; den får inte utelämnas för att programmet saknar motorstöd.

Arbeta sedan i tre vyer:

1. **Gemensam byråanalys.** Beskriv och belägg kundförhållanden, leveranskanaler, geografi, egen verksamhet, leverantörer, egna erfarenheter och sanktionsanknytning. Förklara hur faktorerna kan göra ett hot möjligt. Markera bekräftat sakförhållande, antagande eller kunskapslucka korrekt.
2. **Tjänstens tillämpning.** Pröva betydelsen för tjänstens kunder, arbetsmoment/befogenheter, underlag/insyn, leverans och geografi. Markera vilka oförändrade poster som gäller och bekräfta dem samlat. Avvikelser behöver egen motivering och belägg; samlad bekräftelse skriver inte över dem. Antaganden följer med som osäkra även när tillämpningen bekräftas. Arbetsmoment, lokala scenarier, kontrollräckvidd och riskens sammanvägning prövas fortfarande i tjänstens analys.
3. **Slutsats och granskning.** Pröva PT och TF var för sig, inneboende och kvarstående risk, konsekvenser enligt programmets befintliga metodval samt rutiner och kvarstående begränsningar. Ett sparat eller bekräftat svar är inte ett analysgodkännande. Analysgodkännandet är i sin tur separat från dokumentets sakgranskning och fastställelse.

Riskmotorn behåller de beslutade reglerna. En belagd lägre bedömning än motorns visas som avvikelse; motorns högre nivå och åtgärdsgrund gäller. Kända falska villkor, under tröskeln och ersatta faktorer skiljs från en uttryckligen påstådd saknad hot-/dimensionskoppling. En allmän PT/TF-angivelse skapar ingen sådan koppling. Okända uppgifter får aldrig visas som ”under tröskeln”. ”Gäller annorlunda” börjar med oklar riktning och måste klargöras och sakgranskas; möjlig underskattning spärrar.

En egen sårbarhet utan katalogfaktor behöver uttrycklig täckningsprövning för varje påstått hot och dimension. Pröva inneboende risk för varje egen risk och dessutom kvarstående risk när motorn sänker det berörda scenariot genom kontroll. Välj befintligt lokalt scenario, samma hot/dimension/riskled och en motiverad jämförelsenivå. Varje nödvändigt riskled har en separat länk och prövning. Beskriv hur mekanismen faktiskt täcks och ange belägg. En hög allmän tjänstenivå eller en PT-nivå täcker inte i sig ett annat hot eller TF. Bredvid jämförelsenivån visas en kontrafaktisk referens: befintligt motorscenario med ytterligare +1-faktor och samma kontrollantaganden. Referensen är inget facit och ändrar inte utfallet. En nivå under referensen behöver uttrycklig referensmotivering och sakgranskning. Ändrat underlag gör den tidigare prövningen inaktuell.

Gemensamma mekanismer och byråposter står i D-ARB.5 i analysbilagan. Varje tjänst visar sin tillämpning, avvikelser och osäkerhet. Originalfält, fulla beräkningar och D9-underlag bevaras i B1. Resultatrapporten sammanfattar med hänvisningar; alla tre delarna utgör tillsammans bedömningen. Inga privata analysuppgifter, tillämpningar eller täckningsprövningar skickas till AI. Metodbesluten D3/D9 och införandet av nya riskvikter ingår inte.

### Uttrycklig överföring av en äldre analys

Schema 1 går fortsatt att läsa historiskt. Ingen läsning, vanlig import eller förnyelse byter schema. Förnya vid behov först en inaktuell bindning enligt uppgraderingsanvisningen. Välj sedan **Jämför uttrycklig överföring till gemensam analys**. Jämför original, belägg, perioder och gemensamma förslag och bekräfta jämförelsen separat.

Överföringen bevarar ursprungliga lokalsvar och deras attributioner. Bara innehåll med samma evidenssemantik kan föreslås gemensamt; skilda perioder, belägg, relevans, scenarier eller motsägande svar slås inte ihop. Förslagen är obekräftade antaganden utan överfört gemensamt författarskap. Alla block/scenarioval måste förnyas, nya tillämpningar prövas och modellens lokala användning ombedömas. Inga gamla ja-beslut förs över. Exakta originalbytes arkiveras innan den nya revisionen publiceras atomiskt. En annan fliks ändring avvisar överföringen.

```sh
riskanalys analys BYRA --forslag --schema 2
riskanalys analys BYRA --overfor-schema 2 --jamfort --revision AKTUELL_REGISTERSUMMA
```

CLI visar aktuell registersumma vid analysstatus. Typade filer för `--bekrafta-tillampningar`, `--tillampningsfil`, `--visa-tackningsprovning` och `--tackningsprovning` använder samma validering som webbformuläret. De sparande handlingarna kräver revision, och bekräftelser kräver uttrycklig författare. Börja med att visa prövningen; ange dess aktuella innehållssumma när den bekräftas.

### Omfattning utanför katalogen

För en tjänst som programmet ännu inte kan analysera kan **ofullständigt omfattningsunderlag** exporteras från översikten eller med `riskanalys exportera BYRA --omfattningsunderlag`. Det återger kända verksamhetsuppgifter och den uttryckligt beskrivna luckan, utan risknivåer. Filen har separat ID/manifesttyp och får inte fastställas som allmän riskbedömning. Detta är en känd produktbegränsning. Nästa utvecklingssteg är spårbar, sakgranskad manuell tjänsteanalys, märkt ”Manuell bedömning – ej motorberäknad”; den är inte införd här.

## Engångssvar och samlad tjänstegenomgång 2026-10-22

Besvara gemensamma sårbarhets- och verksamhetsfrågor en gång i **Gemensam byråanalys**. Kontrollera sedan den visade tjänstelistan och välj **Bekräfta gemensamt underlag för valda tjänster**. Det återanvänder oförändrade svar i alla valda erbjudna tjänster. Lokala undantag och otillräckligt underlag bevaras; en bekräftelse gör aldrig ett antagande till ett sakförhållande.

Öppna varje tjänsts **samlade underlag**. Där visas redan bekräftade profiluppgifter, inklusive tjänstebeskrivning och period, som läst underlag. Gemensamma frågor ska inte besvaras igen. Komplettera tjänstens egna resonemang och undantag och välj **Bekräfta visat tjänsteunderlag**. Programmet kontrollerar samma fullständighet och riskspärrar som tidigare och registrerar interna block-/scenariobekräftelser; analysgodkännande och dokumentets sakgranskning är fortfarande separata.

Ordningen är gemensam bekräftelse → eventuella egna täckningsprövningar → tjänstegenomgång. Om en egen täckningsprövning bygger på ett gemensamt scenario väljs det bärande scenariot uttryckligen före prövningen. Alla nödvändiga hot, PT/TF och riskled måste täckas; en för låg jämförelsenivå behöver uttrycklig motivering. Senare ändrad prövning gör tjänstegenomgången inaktuell. En ändrad gemensam post kräver ny gemensam jämförelse/bekräftelse och nya beroende genomgångar; paketets analysbeslut förnyas enligt befintlig bindning.

För ett komplett fyrtjänstfall är det en gemensam och fyra tjänstebekräftelser **efter svarsinmatning**, inte fem totala klick. Öppna kontroll-, underlags- och metodbrister behöver fortfarande lösas. Rapportläsprovens avsiktliga luckor är därför kvar och löses inte genom att byta rapportformat. Resultatrapportens kortare läsvy tar inte bort underlaget i bilagorna.

CLI har samma handlingar: `analys BYRA --bekrafta-byraunderlag FIL --revision SUMMA --forfattare NAMN` med filens exakta `tjanster` och typade `celler` (tjänst, slag, post, postsumma), samt `--bekrafta-tjansteunderlag TJANST_ID`. De skapar inga analysbeslut. Mätverktygen har `--analyslage schema1|direkt2|overforing2`; de gamla standardlägena och rapportmätningens `--analys-schema` är bevarade. Motstridiga lägesflaggor avvisas.

Prefixet `gemensam:` är en intern referens i läsvyn, inte ett ID som användaren ska skriva som en lokal sårbarhet. För metodval D3/D9 och egna tjänster utanför katalogen gäller fortfarande tidigare begränsningar. [Mätning, verifiering och underlag för Claude](superpowers/reviews/2026-10-22-engangssvar-slutprov.md).
