# Testning med Python 3.12

Använd `.venv312/bin/python`, inte en miljö med Python 3.14. Alla automatiska prov använder syntetiska uppgifter och testleverantör; det ordinarie liveprovet är bortvalt.

```sh
.venv312/bin/python scripts/testa.py snabb --ut /private/tmp/riskanalys-snabb-NYTT_ID
.venv312/bin/python scripts/testa.py analys --ut /private/tmp/riskanalys-analys-NYTT_ID
.venv312/bin/python scripts/testa.py full --ut /private/tmp/riskanalys-full-NYTT_ID
```

Välj en ny utdatamapp varje gång. Verktyget sparar insamlade prov, rålogg, JUnit, källsnapshot och resultat med tid, urval och commit. Tomma, trasiga eller ändrade urval ger inte verifierat grönt. Resultatets `commit` är HEAD vid körningen; vid ocommittade arbetsändringar är det `snapshot.json` som binder den faktiskt provade koden. Kontrollera snapshotet igen efter leveranscommit.

Snabbprofilen är en tydligt avgränsad kontroll av schema, referenser, riktning och integritets-/riskgrindar. Analysprofilen lägger till berörda webb-, CLI-, import- och lagringsprov. Profilernas exakta innehåll finns i `tester/testprofiler.json`. Båda utesluter `fullkedja`; de ersätter inte fullsviten vid de kontrollpunkter som AGENTS regel 6 anger.

Fullprofilen och `.venv312/bin/python -m pytest -q` kör alla ordinarie icke-liveprov, även `fullkedja`. Inga långsamma prov väljs bort från standardkörningen. Fullprofilen jämför collection med JUnit och kräver oförändrat källsnapshot. Snapshotet omfattar alla filer under `src`, `tester`, `regelbas`, `scripts` och `docs/research/verktyg`, även JSON-fixturer, fixture-YAML och textkällor, samt AGENTS/projektkonfiguration/profillista. Genererad bytekod (`__pycache__`, `.pyc`, `.pyo`) undantas uttryckligen.

Skriv först ett riktat reproducerande prov och kör RED/GREEN. Kör berört urval och snabbprofil före arbetscommits. Fullsviten körs enligt tabellen i AGENTS *Verifiera och lämna över*: före merge/push till `main` av delad kritisk logik eller okänd påverkan, samt på exakt kandidat för paket till byrå/sakkunnig och färdiga större funktionspaket. Kodrättning efter en fullsvit kräver en ny verifiering; enbart textuppdatering eller nytt commit-ID gör inte den oförändrade koden oprövad.

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

## Research om femminutersvarv, 2026-10-24

[Aktuellt beslutsunderlag](superpowers/reviews/2026-10-24-teststrategi-femminuter.md) jämför ändringsstyrda tester, mer sällsynta fullsviter, profilering och parallellisering. Rekommendationen är normal återkoppling inom 300 sekunder och separat fullkontroll vid definierade risk-/releasepunkter. Context7 och officiell dokumentation har använts; sparade tider skiljs från nya statiska observationer och föreslagna mål.

[Fortsättningen ligger i befintlig testtidsplan](superpowers/plans/2026-10-22-snabbare-verifiering-plan.md#fortsättning-efter-research-2026-10-24-femminutersvarv). Steg F5 är infört 2026-10-24: AGENTS regel 6 hänvisar till en tabell efter ändringens påverkan, och en avgränsad ändring kräver inte längre fullsvit före varje leverans. Profilerna är fortfarande `snabb/analys/full`; områdesprofiler (F6) och femminutersmålet är ännu inte mätta.

## Profilering och första flaskhals, 2026-10-24

Python 3.12.15 i ny `.venv312` på denna dator. Formulärprovet `test_tom_profil_genom_hela_formularet_till_word` mättes fas för fas: formuläranropen dominerade, och provet nådde aldrig bedömningen inom profileringens tidsgräns. Serverprofilen visade att 93 % av servertiden gick till YAML-tolkning: 1 764 `safe_load` à cirka 0,27 s. Huvudorsaken var att `profil/forandringar.py::_tidigare_nej` tolkade hela profilhistoriken en gång per tjänst och sidvisning; historiken växer med varje sparat svar.

Rättning: historiken tolkas en gång per kontroll, och läsning går via `lagring/yamlfil.py::las_yaml_text` med libyaml (`CSafeLoader`) när den finns. Skrivningen är oförändrad, så sparade bytes och hashar påverkas inte. Ingen cache. Modellfilernas kontrollsummor i `metodbeslut.yaml` är ombundna för de sex ändrade filerna; ingen sakkunnigstatus är ändrad. Regressionsprov: `tester/enhet/test_yamllasning.py` och `test_historiken_tolkas_en_gang_per_kontroll_med_flera_nya_tjanster`.

| Mätning, samma dator | Före | Efter |
|---|---:|---:|
| Formulärprovet | 255,0 s (körd parallellt med annan mätning) | 59,9 s |
| Hela `tester/intag/test_webb.py` | ej mätt här (430 s historiskt) | 100,4 s |
| Snabbprofil | 140/71,7 s | 140/43,4 s |
| Analysprofil | ej mätt här | 303/453,7 s |

### Andra flaskhalsen: aktiveringsprövning

`profil/omfattning.py::aktivt` byggde om alla fältdefinitioner och fältvärden vid varje villkorsstyrt fält (166 020 anrop och 88 miljoner `_faltvarde` i en provfil). Nya `aktivitetsprov(profil, regelbas)` bygger dem en gång per operation och profilvy; `aktivt` är oförändrad utåt. Sju heta anropsställen använder den: `fragor`, `tackning`, `kvalitetsbrister`, `omfattningsbrister`, `harled_andelar`, `bygg_underlag` och `kritiska_falt`. Varje ställe använder samma vy som tidigare; `omfattningsbrister` har en prövning för kompatibilitetsvyn och en för originalprofilen.

Beteendet kontrollerades med en tillfällig differensjämförelse utanför repot: gammal och ny kod gav identiska utdata för 84 kombinationer (två regelpaket, sju profilvarianter med tom, komplett, alla tjänster, inaktuella värden, luckor, alias ja och alias nej, samt sex operationer). Två avsiktliga felval av vy (i `fragor` och `omfattningsbrister`) gav avvikelser, så jämförelsen är känslig för fel vy. Regressionsprov: `tester/enhet/test_aktivitetsprov.py`. Sex modellfiler till är ombundna i `metodbeslut.yaml`. `dokument/underlag.py::sarbarhet_status` bygger fortfarande om värden en gång per sårbarhet och ligger utanför denna avgränsning.

Samma underlag, ingen samtidig körning: `test_gemensam_analys_hela_kedjan.py` + `test_webb.py` **301,9 s → 243,0 s** (29 prov); formulärprovet 62,2 s → 36,5 s.

### Kandidatkörning efter båda rättningarna

HEAD `8ca798d` med ocommittade ändringar; snapshot `2be25f0cbd7c716d8568c447d438f9474296a294b6fbbe4b7975b30d021b4b3b`, 866 oförändrade resurser i samtliga tre körningar. Noll failures/errors/skipped och exakt collection/JUnit.

| Profil | Prov | Väggtid |
|---|---:|---:|
| Snabb | 140 | 39,4 s |
| Analys | 303 | 392,0 s |
| Full | 3 609 (ett liveprov bortvalt) | 2 370,4 s, 39 min 30 s |

Senaste sparade fullsvit var 3 594 prov på 66 min 13 s (`43abc07`), möjligen på en annan dator; jämförelsen är därför ungefärlig. Analysprofilen överskrider fortfarande femminutersmålet; nästa steg är områdesprofiler (F6). Dyraste filgrupper nu: gemensam analys 188 s, rapportflöde V8 140 s, intag/analys 135 s, analysgrind 114 s.
