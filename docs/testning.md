# Testning med Python 3.12

Använd `.venv312/bin/python`, inte en miljö med Python 3.14. Alla automatiska prov använder syntetiska uppgifter och testleverantör; det ordinarie liveprovet är bortvalt.

Låst miljö: `uv 0.13.5`, `.python-version` anger `3.12.15`, `requires-python` är avsiktligt `>=3.12,<3.13`. Kör `uv lock --check` och `UV_PROJECT_ENVIRONMENT=.venv312 uv sync --locked --extra dev`. En ren separat installation har provats lokalt; workflowfilen är förberedd för Ubuntu 24.04 men fjärrkörning kräver publicering och har inte påståtts utförd. En pull request kör lås-, import-, regelbas-, kart- och snabbkontroll; fullsviten körs bara på uttrycklig begäran och är avstängd som standard i den manuella körningen (`workflow_dispatch`, välj `fullsvit: true`). Alla actions är låsta till exakt commit-SHA.

```sh
.venv312/bin/python scripts/testa.py snabb --ut /private/tmp/riskanalys-snabb-NYTT_ID
.venv312/bin/python scripts/testa.py analys --ut /private/tmp/riskanalys-analys-NYTT_ID
.venv312/bin/python scripts/testa.py full --ut /private/tmp/riskanalys-full-NYTT_ID
```

Välj en ny utdatamapp varje gång. Verktyget sparar insamlade prov, rålogg, JUnit, källsnapshot och resultat med tid, urval och commit. Tomma, trasiga eller ändrade urval ger inte verifierat grönt. Resultatets `commit` är HEAD vid körningen; vid ocommittade arbetsändringar är det `snapshot.json` som binder den faktiskt provade koden. Kontrollera snapshotet igen efter leveranscommit.

Snabbprofilen omfattar schema, referenser, riktning, V10-presentation, historisk serialisering, importkontrakt och integritets-/riskgrindar. För avgränsad ändring väljs en explicit områdesprofil. `analys` är fortfarande det breda tidigare urvalet och kan överstiga 300 sekunder; det ska inte beskrivas som ett verifierat femminutersvarv.

| Profil | Ändringsklass och konsumenter |
|---|---|
| `profil` | Profil och införandeval, aktiveringsprövning samt webbens tjänsteval. |
| `leverantor` | Gemensam fabrik, CLI, sparade svar och utkastets uppdatering utan nya AI-anrop. |
| `analys-block` | Formulär, typade blockkommandon, CLI, revisions-/processlås och två riktiga HTTP-bekräftelsegränser. |
| `rapport` | Kanoniskt V10-innehåll, samlad granskning, presentation, rendering och tre exportdelar. |
| `lagring` | Manifest, privata sökvägar, analyslagring och atomisk YAML med fel före/efter namnbyte. |
| `regelverk` | Metodbeslut, grindar och sektorsrisk med berörda baskontrakt. |
| `foretagsdata` | Årsredovisning, Bolagsverksbilder och verklig intagsgräns. |

Alla områdesprofiler inkluderar baskontrollen. Exakt urval finns i `tester/testprofiler.json`, inga testpåståenden tas bort från fullsviten. Vid okänd eller delad påverkan väljs bredare riktat urval enligt AGENTS; fullsviten kräver uttrycklig begäran och det finns ingen automatisk diffväljare. Kör exempelvis:

```bash
.venv312/bin/python scripts/testa.py analys-block --ut /private/tmp/riskanalys-analysblock-NYTT_ID --budget 300
```

`--budget` räknar verktygets monotona tidsintervall inklusive insamling. Vid datorvila kan tiden mellan datorns klockslag bli längre; håll datorn vaken för att mäta ett normalt utvecklingsvarv och blanda inte dessa klockor. Överskridande ger `verifierad=false` och exit 1 även om de körda fallen passerade; verktyget dödar inte ett prov mitt i en skrivning. Resultatet redovisar urval, urvalsorsak, miljö/paket och `inom_budget`. Redovisa det körda urvalets omfattning; fullsviten är frivillig och startas bara på uttrycklig begäran.

Fullprofilen och `.venv312/bin/python -m pytest -q` kör alla ordinarie icke-liveprov, även `fullkedja`. Inga långsamma prov väljs bort från standardkörningen. Fullprofilen jämför collection med JUnit och kräver oförändrat källsnapshot. Snapshotet omfattar alla filer under `src`, `tester`, `regelbas`, `scripts` och `docs/research/verktyg`, även JSON-fixturer, fixture-YAML och textkällor, samt AGENTS, pyproject, uv-låsfil, Pythonpinne, CI-konfiguration och profillista. Collection/JUnit jämförs inklusive varje parametriserat falls multiplicitet. Genererad bytekod (`__pycache__`, `.pyc`, `.pyo`) undantas uttryckligen.

Skriv först ett riktat reproducerande prov och kör RED/GREEN vid beteendeändring. Välj berört urval och snabbprofil enligt AGENTS. Fullsviten startas endast på användarens uttryckliga begäran och är inget obligatoriskt villkor för merge, push eller leverans. Ändringar efter en tidigare fullsvit redovisas tillsammans med de riktade kontroller som faktiskt körts; ett ändrat snapshot kräver inte automatiskt en ny fullsvit. En uttrycklig instruktion att inte köra tester gäller även riktade prov och snabbprofil.

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


## Robusthetsplanens tekniska genomförande, 2026-10-24

Arbetsgren `codex/robust-programstruktur`, bas `416579e`. [Planens §8](superpowers/plans/2026-10-24-robust-programstruktur.md#8-genomförandelogg-och-verifierad-kandidat-2026-10-24) samlar det aktuella kandidatresultatet. Nya gränser är gemensam leverantörsfabrik, gemensamt utkastflöde och typade analysändringar med ny kontroll under lås. Fem sammanslagningar och tre nya programfiler ger 247 programfiler.

Riktade bevis: 42/42 på slutliga regressioner med verklig återställning av V10 och hela arbetsmappen, CLI-bekräftelse av kontrollrader samt aktuella webb-/utkastgränser. Sex förbjudna direkta/transitiva importinjektioner underkänns; ordinarie tre kontrakt passerar. V10-presentationens fyra mutationsprov faller med `DID NOT RAISE` när dess integritetskontroll avsiktligt stängs av i en separat process. Ingen sådan mutation finns i kandidaten.

Alla 400 tidigare assert-uttryck i de tolv ändrade befintliga testfilerna finns kvar, inklusive multiplicitet i AST-jämförelse. Detta visar bevarade påståenden, inte ensamt likvärdig funktion; de körda konsumentproven och fullsviten behövs också. Fullprofilen behåller samtliga ordinarie icke-livefall.

Den frysta tekniska kandidatens miljö, insamling, JUnit och snapshot sparas i verifieringsmapparna. Native Word-kontrollen är ofullständig efter UI-timeouter; det redovisas separat från automatisk DOCX-/manifestkontroll. Verklig sakkunnigprövning och användaracceptans är inte utförda genom dessa tekniska prov.


**Slutlig teknisk kontroll på rättad kandidat:** **3 659 godkända, ett liveprov bortvalt, noll fel/skips; 2527,79 s (42 min 08 s) rapporterad monoton mättid inklusive insamling**. Exakt collection/JUnit inklusive multiplicitet och 872 av 872 snapshotresurser oförändrade. Alla 400 tidigare assert-uttryck i tolv ändrade befintliga testfiler är bevarade. Den första underkända fullkontrollen sparas separat och används aldrig som godkänt bevis.

**Nya områdesrepetitioner på samma slutliga snapshot:**

| Profil | Prov per varv | Första | Andra | Utfall |
|---|---:|---:|---:|---|
| Leverantör/utkast | 200 | 84,06 s | 86,17 s | verifierade, inom 300 s |
| Analysblock/lagring/HTTP | 294 | 106,66 s | 106,71 s | verifierade, inom 300 s |
| Rapport/V10/export | 236 | 242,30 s | 252,73 s | verifierade, inom 300 s |

Områdesvarven kördes ett i taget samtidigt som fullsviten, i separata processer och syntetiska datamappar. Tiderna inkluderar denna bakgrundsbelastning; ingen kausal hastighetsvinst påstås. Alla sex har exakt collection/JUnit, oförändrat snapshot och noll fel/skips.

Råbevis: `/private/tmp/riskanalys-robust-full-20261024-2` och `/private/tmp/riskanalys-robust-{leverantor,analysblock,rapport}-slut-{1,2}`. Beständiga bevis, miljöuppgifter, tidigare underkända körningar och komplett ocommittad patch: `/Users/gt/.local/share/riskanalys/provkorningar/robust-programstruktur-20261024`. Den tekniska A0–A8-kandidaten och F6/F7/F10 är lokalt verifierade. A8:s verkliga användar-/sakkunnig-/native Word-acceptans samt driftägarmål kvarstår; fjärr-CI är endast förberedd. Ingen commit, merge eller push har gjorts.

Fullsvitens egna återställningsmätningar inklusive verifiering: låst V10 1,02 s, arbetsmapp 1,08 s. Små syntetiska lokala fall; inga produktions-RTO eller garanterade driftmål.
