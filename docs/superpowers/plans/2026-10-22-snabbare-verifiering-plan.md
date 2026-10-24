# Kortare testkörningar – genomförandeplan T

**Gällande testpolicy, ändrad på användarens begäran 2026-10-24:** Fullsviten körs endast på uttrycklig begäran. Tidigare formuleringar i denna plan om obligatorisk fullsvit eller ny körning inför merge/leverans är ersatta av AGENTS regel 6. Sparade resultat och genomförda steg nedan är historiska bevis. Inga tester körs i denna policyändring.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Genomför själv i befintlig isolerad arbetskopia; ingen granskare per deluppgift. Användarens Claude-granskning gäller leveranserna.

**Goal:** Förkorta utvecklingsvarvet och fullsviten utan att förlora kontroller för risk, integritet, atomisk lagring eller fastställelse.

**Architecture:** Behåll vanlig pytest som komplett kontroll. Inför explicita körprofiler, återanvänd säkra syntetiska startlägen och fördela påståenden mellan rena prov, gränsprov och ett begränsat antal hela kedjor. Börja med de två filer som står för 39,82 procent av tiden.

**Tech Stack:** Python 3.12.15, befintlig pytest, standardbibliotekets XML/JSON/subprocess; inga nya beroenden eller xdist i denna omgång.

**Spec:** `docs/superpowers/specs/2026-10-22-engangssvar-och-testtid-design.md`, avsnitt 1–3 och 5. Status: godkänd för genomförande med bifogad gransknings ändringar. Kodbas `f66a70f`.

## Global Constraints

- Alla automatiska prov använder syntetiska uppgifter och Testleverantor. Inga riktiga API-anrop.
- Fullprofilen och vanlig pytest kör alla ordinarie icke-liveprov. Inget nytt långsamt urval göms undan som standard.
- Delad fixtur är läskälla; varje muterande prov använder en egen kopia.
- Inget produktionscache, ingen höjd HTTP-tidsgräns och inga ändrade risk-/attestregler för att förbättra tiden.
- Byt AGENTS regel 6 endast enligt det uttryckliga policyförslaget i T1 och efter att denna plan godkänts.
- Måltider: snabb ≤60 s, analys ≤180 s, full uppskattningsvis 22–25 min på baslinjedatorn. Redovisa avvikelser; siffrorna är inte uppmätta resultat.

## Review Focus

1. Delade underlag kan förorenas av ett muterande prov: T2 provar ändrat belägg och efterföljande ren klon.
2. En snabbprofil kan ge falskt grönt vid tomt eller trasigt urval: T1 avvisar saknade node-ID och vidareförmedlar pytest exit 5.
3. In-process CLI kan missa uppstarts-/miljöfel: T3 behåller tre riktiga positiva subprocesskedjor och separat negativ subprocess.
4. En återanvänd manifestkedja kan peka på originalets privata filer: T2 avvisar utpekning utanför den nya klonen och bygger om icke flyttbara steg.
5. Färre E2E-prov kan tappa länsspecifika frågor eller slutspärrar: T3 kräver gammalt påstående → nytt prov/lager i täckningsmatrisen.

## Task 1: T1 Mätning, profiler och körpolicy

**Files:** Create `scripts/testtid.py`, `scripts/testa.py`, `tester/testprofiler.json`, `tester/enhet/test_testverktyg.py`, `docs/testning.md`. Modify `AGENTS.md`, `pyproject.toml` endast för dokumenterad markör `fullkedja`.

**Interfaces:** `testtid.sammanstall(fil: Path) -> dict` ger `antal: int`, `provtid_s: float`, `per_fil: dict`, `per_prov: list` och `kalla_sha256: str`. Väggtid lämnas separat när sådan finns, aldrig som summerad provtid. `testa.main(argv: list[str] | None=None) -> int` tar `snabb|analys|full`, `--ut PATH`; kör projektets Python/pytest och returnerar samma exitkod. JSON-profilen innehåller explicita befintliga node-ID/filer. Snabb/analys använder dessutom `not live and not fullkedja`; `full` har ingen begränsande testlista och inget urval utöver `not live`. Godtyckliga extra pytest-urvalsflaggor accepteras inte av wrappern.

- [ ] Skriv `test_tidsrapport_summerar_utan_att_blanda_vaggtid`, `test_fullprofil_kor_hela_pytest`, `test_tomt_eller_okant_urval_ar_inte_gront`, `test_fel_och_bortval_redovisas`. Använd ett litet syntetiskt JUnit och en injicerad subprocessfunktion; inga nya hela kedjor för verktygsprov.

```python
def test_tidsrapport_summerar_utan_att_blanda_vaggtid(tmp_path):
    fil = tmp_path / 'junit.xml'
    fil.write_text('<testsuites><testsuite time="9.0"><testcase classname="a" name="x" time="0.5"/><testcase classname="b" name="y" time="1.25"/></testsuite></testsuites>')
    r = sammanstall(fil)
    assert r['antal'] == 2
    assert r['provtid_s'] == 1.75
```

- [ ] Kör RED: `.venv312/bin/python -m pytest tester/enhet/test_testverktyg.py -q`. Förväntat: verktyg saknas. Implementera gränssnitten, kör samma prov till GREEN.
- [ ] Definiera snabbprofilen med små kärnprov för schema/bytes, riktning, +1, PT/TF, obligatoriska riskled och importskydd. Utgå från `test_analysschema_v2.py`, `test_riktning_v2.py`, `test_referensniva.py`, `test_gemensam_analys_v2.py`, `test_hotkopplingar_v2.py` och `test_gemensam_provning_v2.py`; lägg korta direkta säkerhetsprov i T3 för de grindar som i dag bara täcks dyrt. Analysprofilen lägger till analysens webb/CLI/lagring och nya F-prov. Kontrollera samtliga profiler mot faktisk pytest-collection, inte filnamnsgissningar.
- [ ] Skriv körpolicyn i `docs/testning.md`. Ersätt AGENTS regel 6 med: ”Skriv reproducerande test först. Använd Python 3.12 via `.venv312/bin/python`. Kör berörda tester och snabbprofil före arbetscommits. Kör hela ordinarie icke-live-sviten före leverans/PR/merge; denna kontroll ska även omfatta ändrad testinfrastruktur. En tidigare grön fullsvit gäller bara för ett oförändrat källsnapshot; redovisa exakt urval och utfall. Ingen push eller merge före grön fullsvit på den exakta levererade kodbasen.” Övriga AGENTS-regler bevaras. T1–T3 är arbetscommits, T4 är testomläggningens leveransgrind.
- [ ] Kör tidsrapporten på sparad `final-full.xml`; förväntat 3 198 prov, summerad tid 2 150,758 s och 39,82 procent i de två första filerna. Kontrollera mot den redan sparade baslinjen `docs/superpowers/reviews/2026-10-22-testtid-baslinje.json`, med fullsvitens väggtid separat. Ingen ny fullsvit behövs för att återskapa detta redan sparade resultat.
- [ ] Commit efter verktygsprov och collectionkontroll: `test: inför explicita profiler och tidsrapport`. T4 är den obligatoriska kompletta kontrollen av den samlade testomläggningen.

## Task 2: T2 Återanvänd dyra startlägen, isolera varje mutation

**Files:** Create `tester/fixturer/kedjecache.py`, `tester/enhet/test_kedjecache.py`. Modify `tester/fixturer/analys_hela_kedjan.py`, `tester/enhet/test_analysgrind.py`, `tester/typfall/test_gemensam_analys_hela_kedjan.py` endast där mätningen visar upprepad uppbyggnad. Återanvänd befintliga modulfixturer där de redan räcker.

**Interfaces:** `klona_kedja(bas: BundenKedja, rot: Path) -> BundenKedja` använder den befintliga typen i `tester.fixturer.analys_hela_kedjan`. En modul-/sessionsfixtur bygger högst en bas per faktiskt skild regelbas/schemaversion/testvariant; ny klon används i varje muterande test. Ingen beständig cache över olika körningar/commits.

- [ ] Skriv `test_mutation_i_klon_andrar_inte_bas_eller_nasta_klon`, `test_klon_laser_endast_sina_egna_privata_belagg`, `test_korrupt_kopia_far_inte_atervanda_aldre_godkannande`, `test_baser_med_olika_schema_eller_regelbas_delar_inte_lage`. Använd små underlag för RED/GREEN.
- [ ] Kör `.venv312/bin/python -m pytest tester/enhet/test_kedjecache.py -q`; implementera bara kloning och fixturförberedelse efter rätt RED. Återbind typade sökvägar enligt befintliga kopieringsfixturer. Gör aldrig generell textersättning i frysta manifest; bygg om det steg som inte kan flyttas korrekt.
- [ ] Mät berörda gamla filer före/efter i samma processmodell med `--durations=20` och JUnit. Behåll varje tidigare assertion. Påstå inte att gamla sessionfixturer är nya besparingar.
- [ ] Kör berörda filer, nya isoleringsprov och snabbprofil. Grönt innebär oförändrade negativa grindar och byteoförändrad bas efter hela urvalet. Commit: `test: återanvänd isolerade syntetiska kedjestarter`.

## Task 3: T3 Ta bort upprepade transporter, behåll verkliga gränsprov

**Files:** Modify `tester/m2/test_m2_kedja.py`, `tester/intag/test_webb.py`, `tester/intag/test_rapportflode_v8.py` bara efter uppmätt behov. Create `tester/m2/test_m2_grindar.py`, `tester/intag/test_paketval_webb.py`, `docs/superpowers/reviews/2026-10-22-testtackningsmatris.md`.

**Interfaces:** Negativa CLI-prov får kalla befintliga `riskanalys.cli.main(argv) -> int` med isolerad miljö och capsys. De använder klon från T2 vid rätt steg före den handling som ska prövas. Riktiga subprocessprov använder fortsatt `subprocess.run` och kontrollerar stdout/stderr, exitkod och skapade/ej skapade filer.

- [ ] Lista alla påståenden i de sju negativa M2-kedjorna (`fraga`, `belagg`, `expert`, `metod`, `felpaket`, `datum`, `aldre`) samt de tre fulla webbvarianterna. För varje rad ange behållet/nytt prov och vilket transport-/domänansvar det verifierar. Ett unikt påstående utan motsvarighet får inte tas bort.
- [ ] Skriv snabba negativa prov mot rätt giltigt basläge, applicera exakt en felorsak och kontrollera specifik feltext, exit 1 och att inget fastställt paket finns. Bevisa först att provet blir rött om just dess fel tas bort. För `fraga`/`felpaket` bygg startläget före skrivning/bedömning så att felet verkligen når rätt grind; lägg inte ett annat fel ovanpå en redan godkänd kedja.
- [ ] Behåll tre riktiga positiva CLI-kedjor inklusive återställning, en per regelpaket. Behåll minst ett verkligt negativt CLI-subprocessprov för fastställelsespärren, miljö-/sökvägsprov med åäö och alla atomiska-/privatfilsskydd. In-process huvudfunktionen ersätter upprepad transport, inte själva grinden.
- [ ] Mät särskilt loopen med ett subprocessanrop för varje `sakgranska`-avsnitt. Prova alla avsnitt/utdata billigt genom `cli.main`, men behåll minst ett riktigt subprocessanrop för `sakgranska` i varje positiv paketkedja. Övriga avsnittsattester kan vara förberett giltigt underlag; varje publik kommandotyp ska fortfarande passeras i riktig subprocess. Rapportera kedjan som blandad förberedelse/gränskontroll där det gäller, inte som oförändrad manuell CLI-resa.
- [ ] Behåll en full HTTP-formulärresa till DOCX. Ersätt endast de två överlappande fullresorna med korta riktiga HTTP-prov för val av län/filial/paket och rena formulärprov för respektive variants aktiva frågor, perioder och härledda antal. Behåll CSRF/origin/host, stale revision, dubbel skrivning och ogiltig nedladdning som riktiga HTTP-prov.
- [ ] Återanvänd läsklara rapportfall för rena innehållspåståenden. Behåll verklig DOCX-rendering för båda delar, aktuella exportformat, avbrott under andra filen och fryst evidens; mocka inte den gräns ett prov säger sig kontrollera.
- [ ] Märk de kvarvarande fulla CLI-/webb-/export-/fastställelsekedjorna `@pytest.mark.fullkedja` och ange deras ersättande korta grindprov i täckningsmatrisen. Märk inte ett ensamt viktigt säkerhetsprov som fullkedja enbart för att gömma en lång tid. Fullprofilen och vanlig pytest ska inkludera markören.
- [ ] Kör nya korta prov, berörda bevarade gränsprov och snabbprofil. Täckningsmatrisen ska sakna borttappade påståenden. Commit: `test: skilj grindprov från upprepade fulla kedjor`.

## Task 4: T4 En samlad slutmätning och leverans av teststrategin

**Files:** Update `docs/testning.md`, `tester/testprofiler.json`, `docs/superpowers/reviews/2026-10-22-testtid-slutprov.md`, `docs/STATUS.md`.

**Interfaces:** Använd verktygen från T1 och täckningsmatrisen från T3. Resultat ska ha kommando, Python-version, profil, SHA/snapshot, tid, urval, faktiskt antal, fel/bortval och koppling till JUnit. Färre prov räknas aldrig ensamt som förbättrad effektivitet.

- [ ] Kör snabb- och analysprofil två gånger vardera och redovisa båda tiderna. En körning visar inte stabilitet eller cacheoberoende. Inget nätverk och inga riktiga nycklar.
- [ ] Frys kod/test/regelbas/verktyg, kör **en** komplett sekventiell `.venv312/bin/python -m pytest -q --durations=30 --junitxml=...`. Verifiera noll fel, full collection täckt av JUnit och oförändrat snapshot. Kör regelbasvalidering och diffkontroll.
- [ ] Jämför tidsandelar, uppbyggnader och subprocessantal före/efter. Redovisa om målen 60/180 s och uppskattningen 22–25 min inte nås och vilka återstående filer som dominerar. Prioritera cirka 50 procent lägre tid i de två ursprungliga huvudfilerna; mät faktisk total utan att lova måluppfyllelse.
- [ ] Om ett kodfel rättas efter slutkörningen: riktad reproduktion och ny fullsvit på ändrat snapshot. Ingen upprepning av redan grön oförändrad fullsvit bara för att uppdatera text eller lägga commit-SHA i slutmeddelandet.
- [ ] Commit: `test: verifiera snabbare svit med bevarade leveransgrindar`. Lämna lokal gren, tidsbevis och täckningsmatris till användarens Claude-granskning före plan F. Ingen push/merge ingår.

## Självkontroll och avgränsning

Alla fem Review Focus-rader har namngivna kontroller i T1–T3. T4 verifierar både täckning och faktisk tid. Fullsvitens enda liveprov förblir bortvalt. Ändringar i AGENTS regel 6 är ett uttryckligt beslut i denna plan; om det inte godkänns gäller den gamla regeln och arbetscommits får samlas till en leverans efter fullsvit. Produktens riskmodell och arbetssätt ändras först i plan F.

## Fortsättning efter research 2026-10-24: femminutersvarv

**Samordning:** [planen för robust programstruktur A0–A1](2026-10-24-robust-programstruktur.md) använder F8 → F6 → F7 → F10 som utvecklingsgrund. Denna plan äger fortsatt testtidsuppgifterna; ingen parallell implementation skapas. F9 är fortsatt villkorad av mätning. För aktiv körpolicy gäller nu AGENTS-tabellen och F5 nedan; äldre policy-/commitformuleringar i T1–T4 ska inte användas för att kringgå aktuell policy eller användarens krav på uttrycklig commitbegäran.

**Läge:** nytt förslag efter användarens researchuppdrag, ännu inte genomfört eller aktiverat. T1–T4 ovan beskriver det tidigare arbetet. [Research, belägg, alternativ och exakt policyförslag](../reviews/2026-10-24-teststrategi-femminuter.md) utgår från dagens `main` (`8ca798d`) och det senaste sparade fullresultatet 3 594 prov/66 min 13 s. Inget nytt fullsvitsresultat påstås.

**Vald rekommendation:** högst 300 s för normal ändringsstyrd återkoppling, med påverkade regressioner/konsumenter och en liten baskontroll. Fullsvit vid färdigt större funktionspaket, definierade delade risk-/schema-/integritets-/attest-/testurvalsändringar, okänd påverkan och riktig release; övrig samlad körning kan ske mer sällan i bakgrunden. Ingen generell timslång fullsvit varje gång en chatt lämnar ett arbetsresultat. Övergången behöver en samlad validering av testinfrastrukturen.

**Berörda kontrakt:** risk och PT/TF, analys-/attestbindning, revisionsskydd/atomisk lagring, historiska bytes, faktisk CLI/HTTP/DOCX-gräns samt verifieringsverktygets fullständiga insamling/JUnit/snapshot. Produktens regler ändras inte genom urvalet.

- [x] F5 (2026-10-24, förenklad efter granskning av Claude och Codex): regel 6 hänvisar nu till en tabell i AGENTS *Verifiera och lämna över* med fyra nivåer: dokumentation, avgränsad ändring, delad kritisk logik och paket/större funktionspaket. `docs/testning.md` och `docs/omraden/Tester.md` är samordnade. Ursprunglig uppgift: fastställ policytexten i researchens avsnitt 5; samordna AGENTS regel 6, `docs/testning.md` och relevanta områdesguider. Avgränsa arbetsredovisning från release och definiera när fullsvit måste blockera integration.
- [x] F6 (införd och lokalt verifierad 2026-10-24; se genomförandeutfallet nedan): inför i stället områdesprofiler i `tester/testprofiler.json` och ett läge i `scripts/testa.py` som kör dem. Varje områdesprofil innehåller områdets egna prov och berörda konsument-/gränsprov, till exempel riskmotor, analys och export vid profiländring. Utför F8 (profilering) före F6. Den automatiska diffväljaren nedan skjuts upp tills områdesprofilerna visat sig otillräckliga. Ursprunglig uppgift: utöka befintlig `scripts/testa.py` med explicit ändringsurval, områdes-/databeroenden och redovisad urvalsorsak. Hantera relevant bas, staged/unstaged, nya filer, deletions, namnbyten och ändrade testhjälpare. Okänd påverkan ska bredda kontrollen, inte ge tomt grönt. Testmon/importgraf får bara vara kompletterande signaler.
- [x] F7 (lokalt verifierad 2026-10-24; två repetitioner per ändringsklass): uppdatera de snabba kontrakten för aktuell V10-standard och mät samma representativa ändringsklasser två gånger. Kräv att relevanta avsiktliga fel fångas och att normalvarvet inklusive collection är högst 300 s. Budgetstopp är ofullständigt, aldrig godkänt.
- [x] F8 (2026-10-24: båda flödena profilerade; YAML-/historikläsning och aktiveringsprövning rättade; fullsvit 3 609/39 min 30 s grön på kandidaten, se `docs/testning.md`): profilera webbens kompletta formulärresa och gemensam analys till fastställelse. Mät setup/call/teardown, kompletta rapportbyggen, renderingar och processer. Bevara varje unikt gammalt påstående i en uppdaterad täckningsmatris när överlappande förberedelser flyttas till små prov.
- [ ] F9: utvärdera separat 2/4 workers och `loadfile`/`worksteal`, om mätningen motiverar det. Bevisa isolering, samma parametriserade testmängd utan luckor/dubbletter, oförändrat snapshot och upprepad väggtidsvinst. Ingen global `-n auto` införs på antagande.
- [x] F10 (lokal samlad kontroll verifierad 2026-10-24): gör en komplett samlad kontroll av den nya infrastrukturen. Redovisa separat kort återkoppling, bred kontroll och fullsvit. Behåll vanlig pytest/fullprofil som fullständigt ordinarie urval. Ingen automatisering, schemaläggning, commit eller push ingår utan ett sådant uppdrag.

Femminutersmålet för normalvarvet och en snabbare fullsvit är två separata acceptanser. Den längsta historiska enskilda testtiden överstiger fem minuter; enbart parallell schemaläggning kan inte uppfylla ett oförändrat fullsvitsmål. Aktiva regler är oförändrade tills förslaget införs.


## Genomförande av F6/F7/F10, 2026-10-24

Genomfört tillsammans med [robusthetsplanens A0–A8](2026-10-24-robust-programstruktur.md#8-genomförandelogg-och-verifierad-kandidat-2026-10-24) på `codex/robust-programstruktur`, bas `416579e`. F6 har sju explicita områdesprofiler, var och en med hela snabbprofilens baskontroll, egna konsumenter och sparad urvalsorsak. Automatisk diffväljare är fortsatt uppskjuten. F7 skyddar nu aktuell V10, kontrollraders sammansatta identitet, referensunikhet och samtidig analysändring. Sex avsiktliga direkta/transitiva importfel samt fyra mutationsfall för V10-presentation fångas. Alla 400 tidigare assert-uttryck i tolv ändrade befintliga testfiler är bevarade, inga unika gamla påståenden har flyttats bort.

| Representativ ändringsklass | Prov | Första varvet | Andra varvet | Utfall |
|---|---:|---:|---:|---|
| Leverantör/utkast | 197 | 79,97 s | 79,51 s | verifierade, inom 300 s |
| Analysblock/lagring/HTTP | 291 | 97,19 s | 96,79 s | verifierade, inom 300 s |
| Rapport/V10/export | 233 | 213,45 s | 214,02 s | verifierade, inom 300 s |

Alla sex har matchande collection/JUnit inklusive multiplicitet, oförändrat snapshot och noll fel/skips. Det tidigare breda `analys` är kvar; 303 prov tog 414,37 respektive 454,77 s på originalet under varierande belastning. Ingen generell prestandavinst härleds ur jämförelsen. En separat parad kontroll med samma 36 oförändrade formulärfall och samma miljö är sparad, men två korta par räcker inte för generella prestandapåståenden. F9-parallellisering ingår inte: den sekventiella processen behålls.

F10:s första fullprofil underkändes med ett failure och åtta setupfel. Indirekta gamla fixturanrop och bevarande av oförändrade äldre referenser är rättade; 85 riktade prov är gröna. Ny fullprofil på fryst rättad kandidat är nu verifierad i `/private/tmp/riskanalys-robust-full-20261024-2`, liksom de sex nya områdesvarven som kördes parallellt med den. Vanlig pytest och fullprofil samlar nu 3 659 ordinarie fall, med ett liveprov bortvalt. Tabellen ovan gäller de första områdesvarven före rättningen; slutliga utfall redovisas nedan. Inga commits eller pushar ingår.


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
