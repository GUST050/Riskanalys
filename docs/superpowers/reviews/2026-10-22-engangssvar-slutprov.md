> Detta slutprov avser leveransen `fc1a329` och källbas `2644122`. Senare rättning av scenarioavvikelse och D9-sammanfattning redovisas separat i [svaret på Claude-granskningen](2026-10-22-svar-claude-scenario-d9.md). Äldre prov-/ordmått nedan är historiska och har inte skrivits över.

# Engångssvar och snabbare verifiering 2026-10-22

Status: **tekniskt slutverifierad och lokalt committad**. Oberoende helgranskningens fyra Important är rättade med RED/GREEN i en samlad pass; färsk fullsvit är grön på den exakta slutliga kod-/test-/resursbasen. Ingen push eller merge. Användarens granskning med Claude återstår. Produktbas `f66a70f`, T1–T3 `132f8e9`–`1b40ddb`, verktygsrättning `03bd8bd`, F1 `c7a2ccb`, F2 `bb3ee8b`, F3 `70492b6`, samlad granskningsrättning och fryst källbas `264412289ba35cfc84fe236d406fe9ab9d2c5343`.

## Vad byrån gör

Byrån skriver de gemensamma sårbarhets- och verksamhetssvaren en gång. En gemensam handling bekräftar exakt visade oförändrade tillämpningar för valda erbjudna tjänster. Därefter läser byrån varje tjänsts profilfakta, gemensamma referenser, egna resonemang, hot och PT/TF-bedömning och bekräftar tjänsteunderlaget med en handling. Lokala undantag redigeras separat. Antaganden förblir antaganden.

Det kompletta fyrtjänstprovet går genom verkliga bundna publika operationer med **en gemensam + fyra tjänstehandlingar**, utan 32 scenarioklick eller 64 blockbekräftelser. Det är fem bekräftelser **efter svarsinmatning**, inte fem totala klick. Egen risk kräver dessutom en uttrycklig täckningsprövning per hot, dimension och obligatoriskt riskled; det avancerade provet loggar fyra lokala avvikelser, en gemensam bekräftelse, ett bärande scenarioval, två täckningsprövningar och fyra tjänstegenomgångar. Analysbeslut och dokumentets sakgranskning skapas inte av dessa handlingar.

## Kontroller som finns kvar

- Exakt cellmängd (tjänst, typ, post, postsumma), revision, författare och erbjudande kontrolleras inom analyslåset. Fel, dubbletter, gamla summor eller okända mål avvisar hela skrivningen. Kända avvikelser skrivs inte över.
- Tjänstegenomgången ändrar inga tillämpningar eller täckningsprövningar. Den bygger scenarioval och blockstämplar och kör den ordinarie `analysbrister`, inklusive `gemensamma_analysbrister`, på en ren tjänsteprojektion. Alla gemensamma poster, belägg och bindningar finns kvar. Inget globalt fel filtreras med textprefix och projektionen sparas aldrig.
- Verkliga lokala brister, saknade belägg, oklarhet, otillräckligt kontrollavdrag och otäckt egen PT/TF-risk stoppar fortfarande. Senare ändring gör bundna stämplar/beslut inaktuella enligt befintliga summor. Import skapar inga bekräftelser.
- Motorn, poängen, D3/D9, sakkunnigstatus och AI-tillåtelselistan är oförändrade. Full jämförelse av privata AI-begäranden efter gemensam handling passerar även omförsök och reserv.
- Schema 1:s serialisering och historiska original bevaras. Ingen schema 3 eller rapportversion V9 införs. Vanlig pytest kör fortfarande alla icke-liveprov.

## Mätning av det verkliga schema-2-flödet

`direkt2` startar via schema 2 och publika sparhandlingar; ett prov förbjuder överföringsfunktionen och konvertering av en ifylld schema-1-analys. Samma frysta profil, motor och skrivsvar används i alla tre lägen. ISO-datum i den syntetiska JSON-fixturens värdeunion återställs till datumtypen före riktig profilsparning; det kanoniska JSON-värdet och hashvärdet är oförändrade. Alla ursprungliga fria saktexter, belägg och aktuella författaruppgifter finns kvar, inklusive de fyra olika tjänsteerfarenheterna.

I båda frysta rapportfallen besvaras **sju gemensamma poster en gång**, och **noll lokala kopior av gemensamma svar** lagras. Nödvändiga/utförda egna täckningsprövningar är **0/0 i vartdera fallet**. Råloggen innehåller även nollvärden för separata scenario-, block-, besluts- och sakgranskningshandlingar.

De frysta rapportläsproven innehåller avsiktliga luckor i kontroll och uppdragsförmåga. Därför loggas fyra **nekade** tjänstegenomgångar, inga lyckade. De görs inte falskt färdiga för att nå en klicksiffra. Varje rålogg har 17 steg: fryst profil, bedömning, skrivutkast, schema-2-start, sju gemensamma svar, en lokal svarimport, en gemensam bekräftelse och fyra nekade tjänstehandlingar. Tidigare intagsarbete mäts inte. Det separata kompletta provet ovan bevisar de fem lyckade bekräftelserna.

## Faktisk dokumentlängd

Ord räknas med samma kanoniska synliga dokumenttext, inklusive rubriker och tabeller. Läsrapportens korta källbilaga ingår i läsrapporten. B1 är den kompletterande underlagsbilagan; totalt är summan av delarna. Upprepning är extra förekomster av ordagrant identiska texter med minst tolv ord över båda delar, inte en bedömning av att innehållet kan tas bort.

| Fall | Läge | Läsrapport | B1 | Totalt | Extra upprepade ord |
| --- | --- | ---: | ---: | ---: | ---: |
| fyra_tjanster | schema1 | 13 756 | 34 658 | 48 414 | 10 836 |
| fyra_tjanster | direkt2 | 16 446 | 36 005 | 52 451 | 11 778 |
| fyra_tjanster | overforing2 | 14 404 | 35 854 | 50 258 | 11 394 |
| med_betalningsmandat | schema1 | 13 433 | 34 827 | 48 260 | 11 094 |
| med_betalningsmandat | direkt2 | 16 123 | 36 150 | 52 273 | 12 012 |
| med_betalningsmandat | overforing2 | 14 081 | 36 023 | 50 104 | 11 652 |

Direkt2 är **4 037 respektive 4 013 ord längre totalt än schema 1**, inte kortare. Bekräftade tillämpningar synliggör D9-prövningar som ett obekräftat överföringsförslag inte visar. Jämförelsen bevarar sakunderlaget men har olika bekräftelsestatus. Ingen tidsvinst för människans läsning påstås.

Den första native-mätningen hade 60 475/60 297 ord. Ett reproducerande prov fångade upprepade fullständiga D9-villkor per hot/tjänst. Den lokala upplysningen grupperas nu per faktor, med alla hot/dimensioner kvar; fulla fakta och villkor fanns redan i B1. Det tog bort 8 024 ord i vardera fallet; **B1 är ordmässigt oförändrad före/efter just den rättningen**. Ingen information flyttades till B1 för att få en kortare läsrapport. Någon större redaktionell ombyggnad ingår inte.

## Teknisk och visuell verifiering

F1: 17 RED → 17 GREEN; berört urval 71 godkända, 48,53 s. F2: 20 RED; efter rättning av visning av valfri scenariomotivering passerar 30 kärn-/CLI-prov, 9,20 s. Två verkliga bundna publika kedjeprov passerar, 31,50 s. F3: saknade native-gränssnitt och formulärövergång reproducerade, därefter 13 godkända, 37,50 s. D9-upprepning RED2 → GREEN12 med rapportproven, 22,32 s. Native UI-fynd RED2 → GREEN2, 16,83 s. Privata AI-begäranden normal/omförsök/reserv: tre godkända, 2,59 s.

Checkpoint efter F3, före helgranskningen: **snabb 102 prov/34,006 s och analys 217 prov/168,677 s**, båda med exakt collection/JUnit och oförändrat dåvarande snapshot. Slutlig fullsvit och profiler efter granskningsrättningen redovisas nedan. T:s separata mätning och skyddade testomläggning finns i [testslutprovet](2026-10-22-testtid-slutprov.md) och [påståendematrisen](2026-10-22-testtackningsmatris.md).

En riktig syntetisk browser-session har bekräftat gemensamt underlag, läst den samlade tjänstevyn och sparat ett lokalt berör-inte-undantag. Kontrollen visar oförändrade gemensamma original, övriga tjänster och motorutfall samt inga analysbeslut. Perioder visas läsbart, faktorn identifieras och gemensamt arv märks inte som ett saknat nytt svar. Testflik och egen loopbackserver är stängda; inga riktiga byrådata eller API-anrop användes.

Båda faktiska Word-delar har exporterats och renderats för båda direkt2-fallen (43+103 respektive 42+106 sidor). En separat syntetisk undantagsrapport renderades också (43 sidor). **Riktad PNG-kontroll av åtta sidor**, inte fullsidig kontroll: fyrtjänst-läsrapport 6/13, fyrtjänst-B1 67/70, mandat-läsrapport 33/37, mandat-B1 70 och undantagsrapport 13. Gemensam prövning, lokal tillämpning, oförändrad högre motor, PT/TF, tabeller och raw-underlag är läsbara utan observerad klippning/överlapp på de kontrollerade sidorna. Före-/efter-metadata och exporter har separata mappar.

## Oberoende slutgranskning och samlad rättning

[Slutgranskningen](2026-10-22-engangssvar-slutgranskning.md) av `f66a70f..70492b6` gav fyra Important och inga Critical/Minor. Samtliga fyra är rättade i en pass: nya kontroll-/rutinutkast kan hänvisa till giltiga visade standardscenarier utan att attestera dem; alla blocks aktivering/motivering visas; privata beläggsbytes kontrolleras atomiskt före båda samlade handlingarna; snapshotet omfattar även samtliga test-/regelresurser och undantar genererad bytekod.

Reproduktionerna visade de tre första oberoende mekanismerna med 12 RED-fall och de privata beläggsfelen med fyra RED-fall efter rättning av testets egen gamla revision. Berört urval: **85 godkända/48,44 s**. Det förstärkta verkligt bundna flödet tar bort alla förberedda scenariokopplingar och sparar kontroller/rutiner via ordinarie formuläroperationer för fyra tjänster före de fem bekräftelserna. Senaste separata publik-/beläggsprov: **sex godkända/46,07 s**. Snabbprofil efter rättning: **115 godkända/36,155 s**, exakt collection/JUnit och oförändrat resursinkluderande snapshot. Analysprofilen gav därefter **230 godkända/169,342 s**; fullsviten redovisas nedan. Ingen ny granskningsomgång beställdes.

## Slutlig leveranskontroll

Python **3.12.15**, fryst kodbas `2644122`. Inga installerade program-, test-, regelbas-, profil- eller verktygsfiler ändrades under eller efter körningen; efterföljande ändringar är slutdokumentation.

| Profil | Godkända | Väggtid inklusive collection |
| --- | ---: | ---: |
| Snabb | 115 | 36,155 s |
| Analys | 230 | 169,342 s |
| Full, alla ordinarie icke-liveprov | 3 308 | 1 795,884 s (29 min 56 s) |

Full pytest rapporterade **3 308 godkända, ett liveprov bortvalt, exit 0 på 1 794,45 s**. JUnit har noll failures/errors/skipped. Samtliga 3 308 valda node-ID matchar JUnit exakt; alla **783 program-/test-/regelresurser** matchar aktuellt snapshot. JUnit SHA-256: `5c83ce9fc50e7ad240f05b78ddf106f8ef87b8687371d45bf411c396ba14f8f1`. Summerad provtid **1 792,733 s** är ett annat mått än väggtid. Oberoende efterkontroll av alla tre profilerna, regelbasvalidering och diffkontroll passerar. Regelbasens kontrollsumma är oförändrad och tre paket har sakkunnigstatus `ej_granskad`.

Snabb/analys når målen 60/180 s. Första rena testomläggningen tog 27 min 40 s; med de ytterligare förenklings-/regressionsproven tar den sista fullsviten 29 min 56 s. Det är cirka **16,6 procent mindre väggtid** än den historiska 35 min 52,78 s-körningen, med fler prov (3 308 mot 3 198). Jämförelsen är inte en kontrollerad prestandamätning på samma testmängd. Uppskattningen 22–25 minuter nåddes inte. Fullsvit under tio minuter ingår inte.

Rå collection, JUnit, loggar, snapshots, arbetsloggar, diffpaket, rapportdata, Word/PDF och PNG-bevis bevaras lokalt i `.superpowers/evidens/2026-10-22-engangssvar/`, mappar `T` och `F`. `F/slutlig-verifiering.json` sammanfattar efterkontrollen; `F/slutverifiera.py` kan kontrollera de flyttade bevisen från reporoten. Historiska absoluta sökvägar i råloggar har inte skrivits om. De två avslutade planernas scratchmappar har flyttats intakta till arkivet; andra planers mappar har lämnats kvar.

## Genomförandeval att granska

1. Egen täckning som använder ett gemensamt scenario kräver först ett uttryckligt bärande scenarioval, eftersom den befintliga täckningssumman binder det effektiva scenariot. Normalfallet behåller fem bekräftelser. Kostnad om beslutet är för strängt: ett överflödigt val för egna risker.
2. De två frysta rapportfallen behåller sina avsiktliga sakluckor. Fem lyckade handlingar bevisas separat med ett komplett fall. Kostnad: rapportjämförelsen är inte ett prov av två färdiga riskbedömningar.
3. Efter felet i körverktygets parameter-normalisering samordnas den rättade T-infrastrukturens fullsvit med F:s slutgrind, i stället för en extra 27-minuterskörning före fortsatt redan beställt F-arbete. Kostnad: integrationsfel kan upptäckas först vid slutgrinden; ingen leverans/push/merge före grönt.

## Genomförandebeslut efter slutgranskningen

Granskaren satte följande frågor åt sidan. Genomföraren har avgjort dem, utan att betrakta specifikationens tystnad som ett godkännande:

1. Slutlig fullsvit körs först med samtliga rättningar och måste verifiera aktuellt komplett snapshot. Kostnad om detta inte upprätthålls: oprövad leverans; ingen leverans före grönt.
2. Full kombinerad återinförandekedja körs inte separat igen. Terminal plan/ny plan och förnyelsens nollställning täcks av separata prov; granskaren följde en faktisk ny tjänst och native sparvägen har förstärkts. Kostnad om fel: en integrationslucka mellan separat prövade steg kan kvarstå.
3. Juridisk/metodisk riktighet avgörs inte tekniskt. Oförändrade metodval och ogranskad sakkunnigstatus kräver verklig sakprövning. Kostnad om fel: tekniskt grönt kan misstolkas som materiellt korrekt.
4. Ingen allmän redaktionell förkortning läggs till. Bara bevisad dubblering rättas, med öppna längdmått. Kostnad: fortsatt lång rapport och läsbörda.
5. Rapportfallens sakluckor behålls enligt tidigare beslut; separata positiva prov bevisar bekräftelserna. Kostnad: de två jämförelseexporterna visar inte färdiga riskbedömningar.
6. Riktad åttasidig Word-kontroll och browserprov används, utan fullsidig kontroll eller uppmätt mänsklig lästid. Kostnad om fel: layoutfel på andra sidor eller utebliven faktisk lästidsvinst kan kvarstå.

Inga konkreta Minor är uppskjutna från denna slutgranskning. Den tidigare formulär-Minor som krävde omförsök vid byte bort från gäller annorlunda är rättad inom F3, med bevarat skydd mot förfalskad härledd riktning.

## Kvarstående gränser och granskningsväg

Rapporten är fortfarande lång. Ingen kalibrering av risknivåerna eller ny manuell tjänsteanalys utanför katalogen ingår. En allmän analys ersätter inte kundriskbedömning. Tekniskt grönt ersätter inte byråns sakgranskning eller verklig metod-/sakkunnigprövning.

Granska diffen från `f66a70f` till leveransens lokala HEAD och samtliga genomförandeval ovan. Planspecifikationerna ligger i `docs/superpowers/specs/2026-10-22-engangssvar-och-testtid-design.md` samt plan T/F. Råbevis finns i det lokala evidensarkivet ovan; arkivets README anger flyttningen från tidigare scratchsökvägar. Inga externa meddelanden, pushar eller merger ingår.
