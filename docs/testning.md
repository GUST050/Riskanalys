# Testning med Python 3.12

Använd `.venv312/bin/python`, inte en miljö med Python 3.14. Alla automatiska prov använder syntetiska uppgifter och testleverantör; det ordinarie liveprovet är bortvalt.

```sh
.venv312/bin/python scripts/testa.py snabb --ut /private/tmp/riskanalys-snabb-NYTT_ID
.venv312/bin/python scripts/testa.py analys --ut /private/tmp/riskanalys-analys-NYTT_ID
.venv312/bin/python scripts/testa.py full --ut /private/tmp/riskanalys-full-NYTT_ID
```

Välj en ny utdatamapp varje gång. Verktyget sparar insamlade prov, rålogg, JUnit, källsnapshot och resultat med tid, urval och commit. Tomma, trasiga eller ändrade urval ger inte verifierat grönt. Resultatets `commit` är HEAD vid körningen; vid ocommittade arbetsändringar är det `snapshot.json` som binder den faktiskt provade koden. Kontrollera snapshotet igen efter leveranscommit.

Snabbprofilen är en tydligt avgränsad kontroll av schema, referenser, riktning och integritets-/riskgrindar. Analysprofilen lägger till berörda webb-, CLI-, import- och lagringsprov. Profilernas exakta innehåll finns i `tester/testprofiler.json`. Båda utesluter `fullkedja`; det är ingen ersättning för leveransens fullsvit.

Fullprofilen och `.venv312/bin/python -m pytest -q` kör alla ordinarie icke-liveprov, även `fullkedja`. Inga långsamma prov väljs bort från standardkörningen. Fullprofilen jämför collection med JUnit och kräver oförändrat källsnapshot. Snapshotet omfattar alla filer under `src`, `tester`, `regelbas`, `scripts` och `docs/research/verktyg`, även JSON-fixturer, fixture-YAML och textkällor, samt AGENTS/projektkonfiguration/profillista. Genererad bytekod (`__pycache__`, `.pyc`, `.pyo`) undantas uttryckligen.

Skriv först ett riktat reproducerande prov och kör RED/GREEN. Kör berört urval och snabbprofil före arbetscommits. Kör fullsvit före leverans, PR eller merge. Kodrättning efter en fullsvit kräver en ny verifiering; enbart textuppdatering eller nytt commit-ID gör inte den oförändrade koden oprövad. Policyändringen i AGENTS regel 6 är godkänd i användarens genomförandeuppdrag efter plangranskningen.

Den uppmätta basen är 35 min 52,78 s. Väntat första förbättringssteg är cirka 22–25 minuter, vilket måste mätas. Snabb ≤60 s och analys ≤180 s är mål. Tio minuter för hela sviten kräver ett separat optimeringssteg och utlovas inte här.

```sh
.venv312/bin/python scripts/testtid.py SOKVAG_TILL_JUNIT.xml
```

Tidsrapporten läser en redan körd svit; den startar inga tester. Summerad provtid är skild från väggtid. Tidigare resultat och påståendetäckning sparas i `docs/superpowers/reviews/`.

Första omlagda fullsviten gav 3 214 godkända prov på 27 min 40 s; uppskattningen 22–25 minuter nåddes inte. Båda snabbkörningarna tog cirka 25 s och båda analyskörningarna cirka 111 s. [Mätning och verifieringsverktygets parameterreparation](superpowers/reviews/2026-10-22-testtid-slutprov.md) skiljer den första gröna pytest-körningen från den nu genomförda gemensamma slutgrinden för T och F.

Slutversionen på källbas `2644122` har **115 prov/36,155 s** i snabbprofilen, **230/169,342 s** i analysprofilen och **3 308/1 795,884 s** i fullprofilen (väggtid inklusive collection). Ett liveprov bortvalt, noll failures/errors/skipped, exakt collection/JUnit och 783 oförändrade program-/test-/regelresurser. Den sista sviten innehåller även förenklingens nya prov. Fullsviten är fortsatt längre än 22–25-minutersuppskattningen; snabb-/analysmålen nås. [Samlad leveranskontroll](superpowers/reviews/2026-10-22-engangssvar-slutprov.md).

Efter rättningen av scenarioavvikelse och D9-sammanfattning, källcommit `5c40412`: **snabb 119/34,784 s**, **analys 234/168,856 s**, **full 3 315/1 786,302 s inklusive collection**. Ett liveprov bortvalt, noll failures/errors/skipped, exakt collection/JUnit och 783 aktuella resurser oförändrade. AGENTS regel 6 är oförändrad. [Senaste rättning och bevis](superpowers/reviews/2026-10-22-svar-claude-scenario-d9.md).


## Resultatrapport V9, slutkontroll 2026-10-23

Slutlig snabbprofil: **140 godkända / 44,751 s**. Slutlig fullprofil: **3436 godkända / 2159,897 s**, inklusive collection, Python 3.12.15. Ett liveprov bortvalt i fullprofilen; noll failures/errors/skipped, exakt collection/JUnit och samma 816 oförändrade resurser i snabb/full. Körningarnas HEAD är `13a377e` med ocommittade R7-ändringar; det provade innehållet binds av snapshotet `518813e783dfba1f927800bd6b3d68578eb557362b1e6f4c8b09b2c64e1ef79d` och verifieras på nytt efter leveranscommit.

Analysprofilen innehåller 293 prov, inklusive V9-granskning/export, visad CLI-sakgranskning och tre HTTP-nedladdningar. Den gav **293/376,465 s** före de två sista testhjälparrättningarna och kördes inte separat på nytt; hela urvalet ingår i den slutliga fullprofilen. Analysprofilen överskrider det tidigare målet 180 s. Ingen bortsortering av dyra ordinarie prov eller ytterligare testoptimering ingår.

Avvikelsen **376,465 s mot målet 180 s** accepteras i uppdragets del 1 (2026-10-23). Målet ligger kvar för ett separat förbättringsarbete; detta är inget påstående om att analysprofilens tidsmål är uppnått.

Historiska V6/V7/V8-fixturer väljer sina sparade format uttryckligen. En kvarvarande V8-hårdkodning i M2-CLI-kedjan rättades med fem reproducerande fall. Ett intermittent BrokenPipe i det äldre HTTP-testet reproducerades och rättades i testklientens framing; HTTP 404/413/400-kontrollerna är kvar, utan återförsök eller högre timeout. Hela webbfilen gav 14 gröna prov och 500 faktiska upprepade trestegsförlopp passerade. Fullsviten omfattar även dessa ändringar. [Slutprov och alla råbevis](superpowers/reviews/2026-10-23-resultatrapport-r4-r7.md).
