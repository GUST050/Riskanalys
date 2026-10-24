# Research: högst fem minuters normal teståterkoppling

Datum: 2026-10-24. Kodbas: lokal `main`, `8ca798d`, med befintliga lokala navigeringsändringar. Uppdrag: utreda kortare testtid, mer sällsynta fullsviter och testurval efter ändringens påverkan.

**Rekommendation:** kombinera ändringsstyrda tester med en liten baskontroll i utvecklingsvarvet. Behåll fullsviten som en separat, mer sällan körd kontroll. Optimera dess tunga kedjor efter profilering. Gör inte fem minuter till ett löfte om hela dagens svit.

Detta är ett konkret besluts- och genomförandeunderlag. AGENTS regel 6, testurvalen och körverktyget är ännu oförändrade. Fortsättningen ligger i [den befintliga testtidsplanen](../plans/2026-10-22-snabbare-verifiering-plan.md#fortsättning-efter-research-2026-10-24-femminutersvarv).

## 1. Vad vi faktiskt vet

| Uppgift | Belägg | Status |
|---|---|---|
| Fullsviten hade 3 594 passerade prov och tog 3 973,446 s, 66 min 13 s. | [Slutprov 24 oktober](2026-10-24-redaktionell-slutprov.md#fullsvit-och-slutlig-paketering), källcommit `43abc07`. | Historisk mätning, inte omkörd i denna research. |
| Snabbprofilen hade 140 passerade prov och tog 60,22 s. | Samma [slutprov](2026-10-24-redaktionell-slutprov.md#färsk-samlad-slutgranskning). | Historisk mätning. |
| Ett formulärprov tog 362,804 s och ett fastställelseprov 246,407 s. | [Sparad JUnit-sammanställning](2026-10-24-redaktionell-slutprov.md#var-testtiden-ligger). | Historiska provtider; rå JUnit har inte kontrollerats här. |
| Snabb/analys består av 17 respektive 33 profilposter. | `tester/testprofiler.json`, läst och räknat nu. | Aktuell statisk observation. Poster är filer eller node-ID, inte antal testfall. |
| Wrappern erbjuder bara `snabb`, `analys`, `full`. Den kör sekventiell pytest. | `scripts/testa.py:31–64`. | Aktuell kodläsning. |
| Fullsvit krävs före varje leverans/PR/merge, också för testinfrastruktur. | `AGENTS.md`, regel 6. | Aktuell instruktion. |
| Ingen `.github/`-katalog finns i arbetskopian. | Lokal filinventering. | Ingen repoägd Actions-konfiguration har hittats; externa kontroller har inte inventerats. |

Den här datorn har Python 3.12.15 men saknar `.venv312` och pytest/projektberoenden i den tolken. Den befintliga `.venv` använder Python 3.13.7. Inga tester har körts med fel Pythonversion och inget nytt beroende har installerats. Researchen använder kodläsning, AST-/JSON-analys, aritmetik och officiella källor. En ny tidsgräns är därför ett mål att verifiera i nästa steg.

## 2. Varför en generell genväg inte räcker

### Fullsvit på fem minuter kräver mer än parallellisering

Från den sparade körningen behövs cirka **13,24 gånger** kortare väggtid. En idealiserad delning av hela tiden på fyra respektive åtta processer ger 16 min 33 s respektive 8 min 17 s. Detta är aritmetiska referenser, inte uppmätta xdist-resultat. Duplicerad fixturuppbyggnad, schemaläggning och resurskonkurrens kan ge sämre utfall.

Det längsta enskilda provet tog dessutom **6 min 3 s**. Med oförändrad provkostnad kan parallell fördelning mellan testfall inte få den körningen under fem minuter. `loadfile` håller hela filer ihop, vilket här dessutom kan lämna en filgrupp på cirka 7 min 10 s på en worker. En optimering inne i dessa prov krävs också.

Åtta filgrupper står för 1 902,312 av JUnits 3 969,764 provsekunder, cirka **47,9 procent**:

| Grupp | Historiska provsekunder |
|---|---:|
| `tester/intag/test_webb.py` | 429,859 |
| `tester/typfall/test_gemensam_analys_hela_kedjan.py` | 364,805 |
| `tester/m2/test_m2_kedja.py` | 258,893 |
| `tester/m2/test_m2_grindar.py` | 202,108 |
| `tester/intag/test_analys.py` | 186,012 |
| `tester/intag/test_rapportflode_v8.py` | 160,678 |
| `tester/enhet/test_analysgrind.py` | 159,583 |
| `tester/typfall/test_analys_hela_kedjan.py` | 140,374 |

Tiderna lokaliserar dyra ansvar. De bevisar inte att exempelvis disk-I/O, hashning, modellvalidering, renderingsarbete eller subprocesser är den dominerande orsaken. Det kräver profilering.

### Markörer och profiler beskriver inte all faktisk kostnad

AST-genomgången hittade sju direkt `fullkedja`-dekorerade testfunktioner i fem filer. Parametrisering och fixturer gör detta till något annat än sju testfall. Exempelvis saknar `test_sakgranskad_gemensam_analys_kan_faststallas` i den gemensamma helkedjefilen markören trots att den använder en dyr kedjefixtur och verifierar ett komplett fastställt paket. Enbart `-m 'not fullkedja'` garanterar därför inget kort urval.

Analysprofilens sista poster pekar fortfarande på flera V9-specifika prov. Snabbprofilen har nyttiga generella skydd men ingen uttrycklig V10-fil bland sina 17 poster. Det är inte bevis för en testlucka i fullsviten; det är ett skäl att uppdatera de snabba kontrakten för aktuell produktstandard.

Sessions-/modulfixturer och isolerade kloner finns redan. Den tidigare [testtidsrapporten](2026-10-22-testtid-slutprov.md#bevarad-kontroll) visar ungefär oförändrad tid, 254,19 mot 254,50 s, för den dåvarande kloningsändringen. Att bara höja fixturscope en gång till är därför inget belagt botemedel.

### Importgrafen är både för bred och ofullständig som testväljare

En statisk AST-prototyp över interna importer, inklusive importer i funktioner och testhjälpare, gav följande antal nåbara testfiler via omvänd transitiv sökning:

| Ändrad modul | Statiskt nåbara testfiler |
|---|---:|
| `dokument/redaktionell_v10.py` | 200 |
| `bedomning/scenarier.py` | 202 |
| `profil/modeller.py` | 208 |
| `regelverk/modeller.py` | 214 |

Detta är konservativ reachability i en importgraf, inte ett mätt nödvändigt testurval. Ett importberoende innebär inte att varje test använder den berörda funktionen. Gemensamma moduler och testhjälpare breddar grafen kraftigt. Samtidigt finns YAML-/TXT-/JSON- och dynamiska beroenden som inte uttrycks som Pythonimporter. Obsidian-kartan är ett bra läsunderlag, men ska inte ensam fatta testbeslut.

## 3. Vad externa verktyg faktiskt erbjuder

| Metod | Nytta här | Begränsning och rekommendation |
|---|---|---|
| Pytest med filer/node-ID/markörer | Kör direkt berörda prov utan nytt beroende. | Bygg första lösningen ovanpå befintlig pytest och dess explicita profiler. [Officiell dokumentation](https://docs.pytest.org/en/stable/how-to/usage.html). |
| `--lf` / `--ff` | Kortare omtag efter ett konstaterat fel. | De beskriver tidigare fel, inte alla följder av en ny ändring. De ersätter inte en påverkananalys. [Pytest](https://docs.pytest.org/en/stable/how-to/cache.html). |
| `pytest-xdist` | Samma testurval kan fördelas över processer. | Jämför 2/4 workers och `loadfile` mot `worksteal`. Sessionsfixturer körs per worker om inget särskilt görs. Välj efter mätning; lova ingen linjär vinst. [Fördelning](https://pytest-xdist.readthedocs.io/en/stable/distribution.html), [fixturer](https://pytest-xdist.readthedocs.io/en/stable/how-to.html#making-session-scoped-fixtures-execute-only-once). |
| `pytest-testmon` | Samlar exekveringsberoenden och väljer berörda Pythonprov. | Kräver en initial körning och spårar enligt projektets dokumentation inte statiska filer. YAML/TXT/JSON och subprocessgränser behöver egen lösning och prov. `-m` och andra urvalsflaggor påverkar dess selektionsläge; wrappern använder alltid `-m`. Utvärdera senare som kompletterande signal. [Projektets dokumentation](https://www.testmon.org/). |
| Färre överlappande helkedjor | Flytta upprepade domänpåståenden till små prov, behåll riktiga HTTP/CLI/DOCX-gränser. | Kräver gammalt påstående → bevarat/nytt prov, inte bara färre tester. Principen stöds av [Googles erfarenhetsartikel](https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html), som inte ger en tidsprognos för detta repo. |

För testmon är den statiska filbegränsningen avgörande: Riskanalys beteende bestäms i stor utsträckning av regeldata. Ett verktyg som bara följer exekverad Pythonkod är otillräckligt som ensam kontroll.

### Kontroll genom Context7

Context7 användes för tre avgränsade kontroller mot `/pytest-dev/pytest`, `/pytest-dev/pytest-xdist` och `/tarpas/pytest-testmon`, efter upplösning av respektive biblioteks-ID. Resultaten bekräftade node-ID-/durationstödet, fördelningsalternativen och att sessionsfixturer kan byggas per worker. De bekräftade också en konkret integrationsdetalj: `-m` får normalt testmon att avstå från egen bortselektion. Dagens wrapper och pytest-konfiguration använder redan `-m`; ett enkelt tillägg av `--testmon` skulle därför inte ge avsett ändringsurval. Ett eventuellt uttryckligt `--testmon-forceselect` kräver fortfarande den egna data-/kontraktskontrollen. Källor: [pytest](https://github.com/pytest-dev/pytest/blob/main/doc/en/how-to/usage.rst), [xdist](https://github.com/pytest-dev/pytest-xdist/blob/master/docs/distribution.rst), [testmons konfiguration](https://github.com/tarpas/pytest-testmon/blob/main/testmon/configure.py).

## 4. Föreslagen vardag: ett ändringsstyrt varv under 300 sekunder

| Situation | Obligatorisk normal kontroll | Fullsvit |
|---|---|---|
| Ren text/navigering i uttryckligt tillåten dokumentationsyta | Länkar, kartans aktualitet och diffkontroll. | Ingen automatisk produktfullsvit. Exekverbara `.py`-verktyg och verifieringspolicy är inte vanlig dokumentation. |
| Lokal rättning eller ny avgränsad funktion | Reproducerande regression, påverkade domän-/konsumentprov och liten baskontroll. | Samlad kontroll senare enligt riskklass och kontrollpunkt. |
| Ändrad UI-/CLI-adapter | Berörda domänprov plus faktiska transport-/valideringsprov för adaptern. | Behåll relevanta kompletta resor i den samlade kontrollen. |
| Delad risk-/schema-/integritets-/attestlogik eller okänd påverkan | Bredare explicit kontraktsurval och baskontroll; markera samlad fullkontroll som obligatorisk. | Före integration av den samlade förändringen. Den får köras i bakgrunden medan oberoende arbete fortsätter. |
| Vanlig avgränsad PR med låg/normal påverkan | Ändringsstyrt urval och baskontroll. | Ingen generell fullsvit per PR i det nya policyförslaget. |
| Faktisk release eller färdigt sakkunnig-/byråpaket | Full ordinarie icke-live-svit på kandidaten. | Obligatorisk, även om en äldre version var grön. |

**Fem minuter avser normal återkoppling inklusive insamling, uppbyggnad och resultatkontroll.** Om ett nödvändigt urval överskrider budgeten ska det rapporteras som utökat/pågående, inte kapas och kallas godkänt. En stoppad körning är ofullständig. Förändringen kan behöva optimeras eller få sin breda kontroll vid en av de mer sällsynta kontrollpunkterna.

Föreslagen frekvens för övrig fullsvit: en samlad körning vid avslutat större funktionspaket eller högst en återkommande bakgrundskörning per aktiv utvecklingsdag när kodbasen ändrats, plus de obligatoriska risk-/releasepunkterna ovan. Samordna överlappande behov till samma kandidat. Ingen körning behövs bara för att en chatt avslutas, ett nytt commit-ID skrivs i en text eller exakt samma redan verifierade snapshot rapporteras igen.

En daglig körning på en äldre commit godkänner inte senare kod. Fullresultat, riktade resultat och öppen fullkontroll ska redovisas separat. Den som tar en release ska kunna se vilken exakt kandidat som fulltestats.

Ingen automation eller CI-konfiguration har skapats genom detta researchuppdrag. Vid införande kan GitHub Actions hålla en relevant körning per kandidat och avbryta ersatta PR-körningar med [concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency). Avbrutna körningar räknas aldrig som passerade och slutkandidaten måste få gå färdigt.

## 5. Konkret förslag till AGENTS regel 6

Följande text är ett **ersättningsförslag**, inte aktiv regel:

> **Verifiera efter ändringens påverkan.** Använd Python 3.12. Skriv reproducerande test först vid beteendeändring. Under utveckling och före arbetscommit körs berörda regressions-, domän- och konsumentprov samt den lilla baskontrollen; normal återkoppling ska rymmas inom 300 sekunder. Dokumentation i uttryckligt tillåten textyta verifieras med relevanta dokumentationskontroller. Full ordinarie icke-live-svit körs samlat före release/extern produktleverans och före integration av ändrad delad risk-, schema-, integritets-, attest- eller testurvalslogik, eller när påverkan är okänd. Vanliga avgränsade PR:er kan godkännas med deklarerat riktat urval och baskontroll. Samlad bakgrundsfullsvit används för övrig utveckling enligt testguiden. Ett chattslut eller en lokal arbetsredovisning är ingen extern produktleverans. Redovisa exakt snapshot, faktiskt urval, resultat och kvarstående fullkontroll. Saknade, avbrutna eller budgetstoppade prov får inte rapporteras som passerade. Fullsvitsresultat återanvänds bara för oförändrat verifierat snapshot; dokumentations- och commit-ID-ändringar kräver ingen onödig omkörning av samma produktunderlag.

Övriga regler, inklusive uttrycklig användarbegäran före commit/push, bevaras. En ny policy måste skrivas konsekvent i AGENTS, testguiden, områdesguiderna och den befintliga testtidsplanen så att agenter inte får motsatta instruktioner.

## 6. Så ska ett ändringsstyrt urval fungera

Utöka den befintliga `scripts/testa.py` i stället för att skapa en konkurrerande testväg. Ett tänkbart nytt läge är `andrat`; det finns inte ännu.

1. Läs diff mot en uttrycklig relevant bas: verifierad kandidat eller integrationsbas, inte godtyckligt `HEAD~1`. Ta med committade ändringar, staged/unstaged, nya ej ignorerade filer, borttagningar och båda sidor av namnbyten.
2. Klassificera påverkan med en versionshanterad områdes-/kontraktskarta. Deklarera även beroenden på regeldata, textkällor, JSON/gzip-fixturer, konfiguration, testhjälpare och verifieringsverktyg.
3. Välj unionen av ändrade tester, regressionsprov, påverkade konsument-/gränsprov och baskontroll. En ändrad gemensam `conftest.py` eller vald fixtur ska kunna bredda urvalet. Okänd/borttagen modul utan säker klassning får inte ge tomt grönt.
4. Använd importgraf eller testmon som kompletterande förslag. En manuellt verifierad kontraktskarta och data-/verktygsregler avgör när bredare kontroll behövs.
5. Spara `urval.json`: diffbas, inputhashar, ändrade filer, valda node-ID, skäl per vald grupp, utelämnade lager, tidsbudget och eventuell obligatorisk fullkontroll.
6. Kontrollera collection mot faktiskt körda node-ID/JUnit med bevarade parametrar och multiplicitet samt oförändrat snapshot. Inget tomt urval, oväntat bortval, duplicerat deljobb eller utebliven grupp får bli verifierat grönt.
7. Inför tidsregression för urvalet och separera status för riktad körning från status för fullsvit. En dokumentationskörning får heta dokumentationskontroll, inte fulltestad produkt.

Börja med få explicita områden från de befintliga guiderna. Bevisa urvalet med representativa avsiktliga fel: exempelvis ändrat scenario, korrupt manifest, stale analys, fel V10-presentation, ändrad YAML och förlorad HTTP-spärr. Väljaren ska ta med provet som fångar respektive fel. Testa också diffbas, nya filer, deletions, namnbyten och ändrad testhjälpare.

## 7. Mätbar fortsättning i rätt ordning

**Steg A: definiera och samordna körpolicyn.** Avgränsa utvecklingsåterkoppling från release. Exakt regeltext ovan och trigger-tabellen är underlag för beslut. Ingen optimering behöver först göra alla 3 594 prov tretton gånger snabbare.

**Steg B: inför explicit ändringsurval och V10-baskontrakt.** Utöka wrappern/profilfilen med spårbara urval och egen verifiering av väljaren. Kör representativa ändringsklasser två gånger med ren process; målet är högst 300 s per normalklass och inga förlorade påståenden. Fastställ baskontrollens innehåll genom faktiskt uppmätt kostnad, inte enbart filnamn eller markörer.

**Steg C: profilera två tunga flöden.** Börja med hela formulärresan och gemensam analys → fastställelse. Använd `--durations=30` för setup/call/teardown och exempelvis nedanstående profileringskommando efter att korrekt miljö är klar:

```sh
.venv312/bin/python -m cProfile -o /private/tmp/riskanalys-webb-NYTT_ID.prof -m pytest tester/intag/test_webb.py::test_tom_profil_genom_hela_formularet_till_word -q
```

Kommandot är föreslaget och har inte körts här. `cProfile` ger anrops-/kostnadsfördelning; den profilerade tiden får inte jämföras som vanlig benchmarktid. [Python 3.12-dokumentationen](https://docs.python.org/3.12/library/profile.html) beskriver både användningen och mätpåverkan.

Mät särskilt antal kompletta rapportbyggen, DOCX-renderingar, regelbasladdningar, hash-/manifestkontroller, serialiseringar och CLI-processer. Flytta rena innehålls-/grindpåståenden till minsta giltiga syntetiska startläge. Behåll faktiska transporter, atomisk export, oförändrade original och historisk paketverifiering där just de kontrakten prövas. En funktion med många förberedelsesteg behöver inte samtidigt vara full E2E-bevis för varje negativ variant.

**Steg D: prova kontrollerad parallellisering.** Jämför sekventiellt, två och fyra processer på samma kod-/test-/regeldatasnapshot och samma testmängd. Prova åtta först om dator/resursmätning motiverar det. Gruppfördelning som återanvänder fixturer jämförs med finare fördelning. Ingen variant blir standard utan matchande node-ID/JUnit, isolerade datamappar/portar, godkänd korrekthet och upprepad tidsmätning. Den befintliga wrappern behöver ett uttryckligt workers-gränssnitt; att bara skriva `-n auto` efter dess kommando fungerar inte.

**Steg E: validera omläggningen samlat en gång.** När policy, väljare och fixturändringar är klara behövs en komplett kontroll av den samlade testinfrastrukturen. Därefter används den nya frekvensen. Vanlig pytest/fullprofil ska fortsatt kunna köra samtliga ordinarie prov; inget viktigt prov raderas för att förbättra ett urvalstal.

## 8. Mål och gräns för slutsatsen

- Normal utvecklingsåterkoppling: högst 300 s inklusive collection. Detta är ett mål, inte uppmätt i denna körning.
- Fullsvit: körs mer sällan och gärna i bakgrunden. Fem minuter för hela sviten är en separat optimeringsambition som inte kan utlovas från befintliga belägg.
- Bevara risk-, integritets-, samtidighets-, historik- och attestkontrakt. Lägre körfrekvens medför senare upptäckt av vissa korsfel; bakgrundssviten och breda riskpunkter fångar denna avvägning.
- Ingen ändrad riskmodell, produktcache, borttagen regression, installerad plugin, aktiv schemaläggning eller försvagad aktiv gate ingår i researchen.
- Färsk verifiering här är statisk och dokumentär. Sparade tider hämtas från versionshanterade rapporter och har inte reproducerats på denna dator. Rå JUnit och fullpaketets tidsanalys på en annan arbetsdator måste hämtas/återskapas i införandet om deras exakta mätförutsättningar ska jämföras.

**Slutsats:** lös först den onödiga väntan genom en tydlig körpolicy och verifierat ändringsurval. Lägg sedan optimeringsarbetet på de få tunga kedjor som mätningen pekar ut. Både återkopplingstiden och fullsvitens kvarvarande kostnad ska redovisas separat.
