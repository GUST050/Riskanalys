# Samlad slutverifiering av C–E och resultatrapport V10

Slutunderlag 2026-10-23. Regelbas **2.12.2**, kodcommit `508f8c6`, fullkörningens commitstämpel `f25eb21`. **3 557 godkända, 0 fel, 0 överhoppade; ett livetest bortvalt.** Insamling/JUnit matchar, exitkod 0 och alla 851 snapshotresurser är oförändrade. Användaren har uttryckligen godkänt båda referens-PDF:erna efter D och gett klartecken till E. E och den samlade slutreviewen är färdiga.

## Omfattning och gränser

C omfattar källbundna nivåmotiveringar för samtliga 26 hot. V10 inför disposition 0–5 och separata A/B1 med samma analysunderlag. D innehåller tio provisoriska beslut med versionsbundna sakobjekt och samtliga 244 appfiler. Alla nya och ändrade regelobjekt är fortfarande `ej_granskad`; inga verkliga sakkunnigattester har skapats.

Historiska V8/V9-vägar och frysta källor ingår i regressionerna. Ett faktiskt tidigare fastställt V9-paket verifierades dessutom med tom fellista på den aktuella koden. Tester använder syntetiska uppgifter och testleverantör. Inga verkliga AI-anrop, ingen push och ingen merge.

## Genomförda körningar

| Kontroll | Utfall | Tid | Underlag |
|---|---:|---:|---|
| Riktat urval för reviewrättningar, V10 och metodkontraster | 26 godkända, 0 fel | 26,93 s | `/private/tmp/riskanalys-cde-review-green.log` |
| CLI, fastställelse V8/V9/V10, historisk verifiering, scenarier, reduktionsspärr och rapportkontrakt | 96 godkända, 0 fel | 185,50 s | `/private/tmp/riskanalys-cde-kedja-5.log` |
| Snabbprofil genom `scripts/testa.py` | 140 godkända, 0 fel, 0 överhoppade | 60,522 s | `/private/tmp/riskanalys-cde-snabb-2/resultat.json` |
| Första ordinarie fullprofil, inga livetester | 3 522 godkända, 34 fel, 0 överhoppade; ett livetest bortvalt | 2 868,393 s | `/private/tmp/riskanalys-cde-full-1/resultat.json` |
| Riktat efter fullsvitsrättningar, V10/metod/regelkatalog | 68 godkända, 0 fel | 42,55 s | `/private/tmp/riskanalys-fullfix-slut.log` |
| Historiska gyllene V7-bytes, preliminärt V10-utbud och uppdaterad trepartsrapport utan AI-anrop | 3 godkända, 0 fel | 23,57 s | `/private/tmp/riskanalys-fullfix-3.log` |
| Fullständigt syntetiskt webbintag till Word | 1 godkänt, 0 fel | 215,28 s | `/private/tmp/riskanalys-fullfix-webb.log` |
| Ny snabbprofil efter rättningarna | 140 godkända, 0 fel, 0 överhoppade | 67,213 s | `/private/tmp/riskanalys-cde-snabb-3/resultat.json` |
| Ny ordinarie fullprofil, commitstämpel f25eb21, inga livetester | 3 557 godkända, 0 fel, 0 överhoppade; ett livetest bortvalt | 3 129,232 s (pytest 3 127,15 s) | `/private/tmp/riskanalys-cde-full-2/resultat.json` |

Snabbprofilernas collection och JUnit matchar och deras snapshot förblev oförändrade. Snabb2:s commitstämpel är `dd52d85`: rättningarna fanns i arbetskopian och sparades därefter som `40d5aad`. Snabb3 kördes på de slutliga rättningarna, därefter sparade som `508f8c6`. Full2 kördes efter den kodcommiten. Under körningen sparades endast dokumentation som `f25eb21`, som är slutprotokollets commitstämpel. Snapshotet omfattar kod, tester, regelbas, profiler och verktyg och förblev exakt oförändrat. Även en ny jämförelse mot leveransens aktuella filer gav 851/851 identiska resurser. Full2:s `resultat.json` har `verifierad: true`, `collection_matchar: true` och `oforandrat: true`.

Kommandot för fullprofilen:

```bash
env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv312/bin/python scripts/testa.py full --ut /private/tmp/riskanalys-cde-full-2
```

## Fynd och rättningar

Den samlade kodreviewen gav fyra betydelsefulla fynd, samtliga rättade med reproducerande RED→GREEN-prov: transitive genomförandefiler i metodbeslutsbindningen, källösa kombinationsgrupper, exakt återgivning av fri profiltext och kumulativ effektjämförelse mot ursprunglig regelbas 2.0.0. Den publika rapportbyggarens V10-dispatch kontrollerades också RED→GREEN. E-delen av samma slutreview är klar utan kvarstående fynd.

Tidigare riktade körningar upptäckte äldre positiva testkopior med ändrad kontrollräckvidd utan ombindning, borttagna hotkopplingar i syntetiska lönefixturer samt hårdkodade versions-/rapportförväntningar. Testkopior och förväntningar anpassades till de nya kontrakten. Produktens katalog-, kontroll- och sakkunnigspärrar behölls. En körning hindrades av sandboxens lokala portspärr; den berörda kedjan kördes därefter med tillåtna lokala testportar.

Fullsvitens två produktfel reproducerades före rättning: V10:s risksortering saknade obesvarade tjänster i uppslagningen, och lönefrågans iakttagna hot hade kvar de två borttagna hoten. Båda är rättade med RED→GREEN. Ny regelversion och D-bindningar är 2.12.2. Äldre förväntningar på V9-standard, antal tjänstkopplingar och ideellindikatorns PT-effekt följer nu de godkända ändringarna. Testprofiler med ändrad kundbas får en konsekvent hemvistfördelning; produktvalideringen är kvar. Det historiska V7-provet använder sin frysta 2.0.0-regelbas och samtliga ursprungliga gyllene kontrollsummor är oförändrade. HTTP-provets tidigare femsekundersgräns var för kort för den faktiska synkrona rapportuppdateringen; med 30 sekunder passerar samma handling och dess innehållskontroller. Ingen kontroll hoppas över.

## Referensrapporter efter D

Användaren godkände underlagen i `.superpowers/evidens/2026-10-23-rapport-v10-slutkontroll/`. Nybundna slutunderlag 2.12.2 finns i `.superpowers/evidens/2026-10-23-rapport-v10-2.12.2/`:

| Syntetiskt fall | Huvudrapport | Bilaga A | Bilaga B1 | Maskinfynd | Presentationsfynd |
|---|---:|---:|---:|---:|---:|
| Fyra tjänster | 20 sidor | 38 sidor | 195 sidor | 430 | 0 |
| Betalningsmandat | 21 sidor | 40 sidor | 200 sidor | 432 | 0 |

Hela fria motiveringar, 33 högre-risk-/sårbarhetsrader, fem lägre-risk-rader och 15 lagexempel är bevarade. Gemensamma hotkedjor återges en gång. Word-innehåll, källpekare och manifest kontrollerades. Texten på samtliga huvudsidor är identisk med de godkända PDF:erna förutom versionsangivelsen på sida 1 och 20/21; dessa fyra sidor är visuellt omkontrollerade. Huvudrapporterna är visuellt genomgångna; alla bilagesidor har inte granskats visuellt. Riktmärket tio sidor är inte uppnått; innehåll har inte kapats. Tolv fasta profilvarianters scenarioled och tjänsteutfall är identiska mot D-slut. PDF-godkännandet före E är uppfyllt.

## Slutleverans och kvarvarande expertprövning

Full2 är grön och det oförändrade snapshotet verifierat. E:s guide och tre expertpaket innehåller 276 obesvarade objekt, 244 bundna appfiler, 40 kontrastprofiler, tolv fasta profilfiler, lästa primärkällor och sex referens-PDF:er per paket. E-delen av samma slutreview är klar utan kvarstående fynd. Leveransarkiv: `../underlag/sakkunnigpaket-2.12.2-2026-10-23.zip` relativt repot, med separat SHA-256-fil och de fullständiga testprotokollen under `verifiering/`. [Alla genomförandebeslut och deras kostnader](2026-10-23-genomforandebeslut.md) är redovisade. Grenen behålls lokalt utan push eller merge. Verklig sakkunniggranskning och metodkalibrering ingår inte i Codex uppdrag.
