# Fullständigt intag och hel riskbedömning – implementeringsplan

> **För agentic workers:** Använd executing-plans för genomförande i samma session. Användaren har begärt research, val av arbetssätt och implementation. Ingen commit/push ingår i detta uppdrag.

**Goal:** En användare ska kunna starta med en tom byråprofil, besvara relevanta följdfrågor, spara och återuppta samt skapa ett spårbart Word-utkast av hela riskbedömningen.

**Architecture:** En gemensam regelstyrd frågekärna läser versionerade fält med krav-/avsnittskoppling och tillämplighet. Ett lokalt HTML-formulär och CLI-översikt använder samma svarshantering. Profilen är den kanoniska datakällan; befintlig bedömning, AI-skrivning, granskning och export återanvänds. Fritext sätts in lokalt och skickas aldrig till AI.

**Tech Stack:** Befintlig Python/Pydantic/PyYAML/python-docx, standardbibliotekets lokala HTTP-server; inga nya beroenden.

**Spec:** `docs/superpowers/specs/2026-10-08-riskanalys-design.md`, särskilt 14.1–14.3.

## Global Constraints

- AI fattar inga riskbeslut; namn och fritext skickas inte till AI.
- Byrådata lagras utanför Git. Inga kundärenden i fas 1.
- Regelbasändringar har källor och grund; inga fria uttryck eller eval.
- Ingen mänsklig sakkunnigattest skapas av programmet eller av byggagenten.
- Utkast kan skapas men fastställelse behåller samtliga befintliga grindar.
- TDD och syntetiska underlag. Inga betalda API-anrop i verifieringen.
- Befintliga, okommittade dokumentändringar bevaras.

## Review Focus

1. Okänd tjänst/tillämplighet får inte gömma nödvändiga frågor eller ge falsk fullständighet.
2. Byte av tjänst, period eller geografiskt grundsvar måste ompröva beroenden och gamla godkännanden.
3. Ett rättat svar i en annan flik får inte skrivas över; avbruten skrivning får inte skada profilen.
4. Fullständighet omfattar beskrivande underlag, tomma/icke tillämpliga svar och motstridig statistik.
5. Lokala HTTP-anrop måste skydda byrådata mot andra webbsidor, HTML-injektion och godtyckliga filsökvägar.

## Task 1: Versionerad frågetäckning och beskrivande underlag

**Files:** `regelbas/falt.yaml`, `regelbas/version.yaml`, `regelverk/modeller.py`, `regelverk/validering_m2.py`, `tester/intag/test_kontrakt.py`.
**Interfaces:** `Falt.intag: Intagsfalt | None`, med `grupp`, `ordning`, `krav`, `avsnitt`, `kallor`, `beroenden`; `intagskontraktsfel(rb) -> list[str]`.
- [x] Skriv och kör röda kontrakt för saknad kravtäckning, okända referenser, cykliska beroenden samt beskrivande frågor per tjänst.
- [x] Lägg frågekoppling på kanoniska profilfält och nya lokala beskrivningsfält för byrå, kundgrupper, kanaler, geografi, erfarenheter, arbetssätt per tjänst samt kontrollbelägg.
- [x] Kör kontrakt och regelbasvalidering; äldre regelbaser ska fortfarande kunna läsas.

## Task 2: Adaptiv frågekärna och verifierad fullständighet

**Files:** nya `src/riskanalys/intag/{modeller,fragor,tackning,svar}.py`, `tester/intag/test_fragor.py`.
**Interfaces:** `fragor(rb, profil) -> tuple[Intagsfraga,...]`, `tackning(rb, profil) -> Tackning`, `besvara(rb, profil, svar: IntagSvar) -> Profil`.
- [x] Röda prov: alias/andelar frågas inte dubbelt; okända aktiveringar frågas först; inaktiva tjänster döljer följdfrågor; saknad fritext/period/källa samt falsk ej-tillämplighet hindrar färdigstatus.
- [x] Implementera ordning/tillämplighet och hänvisningar. Kontrollera kvalitet och omfattning med befintliga profilfunktioner, samt kravtäckning och rättslig omfattning.
- [x] Bevara tidigare belägg och markera beroenden inaktuella vid faktiska grundändringar. Okänt får sparas utan att bekräftas.
- [x] Gröna prov för tomma, små, flera tjänster och ändrade profiler.

## Task 3: Återupptagning, historik och atomisk profilskrivning

**Files:** `profil/lagring.py`, ny `intag/tjanst.py`, `tester/intag/test_lagring.py`.
**Interfaces:** `Intagstjanst(byra_id, rb)`, `skapa(...)`, `spara(svar, revision)`, `oversikt()`; `profilrevision(profil) -> str`.
- [x] Röda prov för gammal revision, avbrutet namnbyte, bevarad historik och byte av rätt tillsynsområde.
- [x] Skapa profil från bekräftat län/filial/datum; lås aldrig ett gissat län. Spara privat, atomiskt med fsync, tidigare kopia och konfliktskydd.
- [x] Verifiera återupptagning och gamla profilformat.

## Task 4: Lokalt formulär och CLI

**Files:** nya `intag/{webb,vyer}.py`, `kommandon/intag_kommando.py`, `cli.py`, `tester/intag/test_webb.py`.
**Interfaces:** `skapa_server(tjanst, port=0) -> Intagsserver`, `riskanalys intag <byra> [--oversikt] [--port N] [--utan-browser]`.
- [x] Röda HTTP-prov för start, spara/följdfråga, ändra, fel utan svarsförlust, CSRF, Origin/Host, HTML-escaping, okända vägar, för stor kropp och gammal revision.
- [x] Bygg HTML utan externa resurser: en fråga per sida, källa/period med svaret, okänt, sakliga nej/noll och villkorad tillämplighet, svaröversikt, återupptagning och tydlig lucklista.
- [x] Bind bara 127.0.0.1, använd slumpad åtkomstväg och CSRF-token, privata svar/no-store/CSP, begränsade requestkroppar och inga byrådata i HTTP-loggar.
- [x] Verifiera CLI och verklig webbläsare med syntetiska data.

## Task 5: Hela dokumentet och kompletteringar

**Files:** ny `intag/dokument.py`, `dokument/arb.py`, `dokument/intagsunderlag.py`, `faststallelse/grindar.py`, `tester/intag/test_kedja.py`.
**Interfaces:** `skapa_utkast(byramapp, rb, leverantor) -> Path`.
- [x] Röda prov för intag → bedömning → skrivning → granskning → Word, lokalt insatta beskrivningar och frånvaro av fritext/persondata i AI-underlaget.
- [x] Koppla skrivknappen till befintlig kedja med fullständighetskontroll före anrop. Underkända AI-svar/oklarheter ska visas och återkopplas till registrerade frågor; omappad oklarhet blir ett synligt hinder.
- [x] Lägg intagets täckningshinder även i fastställelsegrinden så att CLI/handredigering inte kringgår kravet.
- [x] Verifiera ändring efter export, inga automatiska godkännanden och tydlig UTKAST-status.

## Task 6: Research, verifiering och slutgranskning

**Files:** befintlig research 10, STATUS, spec 14, README.
- [x] Dokumentera källor och designval i befintliga researchfiler.
- [x] Kör riktade prov, hela projektets pytest utan API-nyckel, regelbasvalidering, Git-kontroll och verkligt syntetiskt användningsprov.
- [x] Fristående teknisk slutgranskning enligt executing-plans; rätta viktiga fynd med röda/gröna regressioner.
- [x] Redovisa resultat, startkommando och vad som återstår i M3/M4. Intaget innebär inte juridisk certifiering.


## Genomförande och avvikelser 2026-10-10

Alla sex uppgifters implementation är införd. Slutverifiering dokumenteras i STATUS och körloggen.

- Ingen commit/push; befintliga dokumentändringar är bevarade.
- Aktiva frågor kan inte markeras ej tillämpliga i formuläret. Inaktiva följdfrågor döljs; nej/noll är sakliga svar, okänt kan sparas men ger inte färdigstatus.
- Tidigare sektorsmotivering är frivillig inför ett första utkast. B-13 använder bara aktuell bekräftelse, och kvarvarande sakgranskningsgrindar tillämpas före fastställelse.
- Faktisk utvärdering får en egen uttrycklig registrering. Befintligt Word-utkast uppdateras genom granskning/export med bundna källor, utan extra AI-anrop.
- Historik har gemensamt läs-/tilläggslås för CLI och webb. Word-nedladdning och skrivning kontrollerar historikens aktualitet utöver profil, regelbas och manifest.
- Standardbibliotekets webbserver är endast lokal på macOS/Linux. Publik tjänst, Windows-installation, dokumentimport och hela grafiska sakgranskningen ingår inte i denna leverans.
- Oberoende teknisk granskning utförd; fynd reproducerade och rättade med regressioner. Regelbasen förblir ej sakkunniggranskad; användbarhet och modellkvalitet med riktiga byråer är återstående M3/M4-gates.

**Slutresultat:** 881 tester passerar, ett livetest bortvalt (468,32 s), utan API-nyckel. Regelbasvalidering, compileall, diff --check och tre nya granskningsmanifest passerar. Fristående teknisk slutgranskning har inga kvarvarande konkreta P1/P2.

## Claude-granskning och rättelser 2026-10-10

Användaren begärde prövning/rättning av Claude-fynden samt mer research om förifyllning. Koden är fortfarande okommittad. Tidigare tekniska granskningsomdömen var begränsade till då provade vägar; de innebär inte att senare fynd saknades.

| Fynd | Utfall | Rättning / evidens |
|---|---|---|
| 1 XML-ogiltig fritext | Rättat | Delad XML-kontroll vid intag/CLI och preflight av handredigerad profil före AI. Regressioner för NUL, vertikal tab, surrogat och U+FFFE samt HTTP-feltext. |
| 2 dubbel skrivning | Rättat | Engångstoken per formulär och revision, förbrukad även om skrivningen fallerar. Regression efter fel och tre hela Word-flöden som återpostar samma formulär utan nya AI-anrop. |
| 3 CLI kringgår intag/CAS | Rättat | Kanoniska intagsfält går via besvara, alla CLI-sparningar använder CAS. Äldre intagsalias hänvisas till sin kanoniska fråga. Regression för följdsvar och samtidig webbsparning. |
| 4 filialens källa | Rättat | Registerstart kräver separat egen filialkälla. Säteslän behåller exakt SCB-bildreferens. Negativt startprov och kontroll av båda källorna. |
| 5 senare hämtning | Rättat | Dölj och avvisa fetch/import efter låst bedömningsdatum före nätanrop; samma grind i lagringen behåller tidigare bild. Ny bedömning använder separat profil. |
| 6 Vet inte tappar belägg | Rättat | Tidigare värde, källa, datum, bekräftare och period behålls medan status är obekräftad. Formuläret märker tidigare belägg. Regression även för statistikperiod. |
| 7 okänt utan roll | Rättat | Tom roll kan sparas för okänt; bekräftelse kräver fortfarande funktion. HTTP-prov ger lyckat sparande. |
| 8 djupt SCB-JSON | Rättat | RecursionError fångas som redigerat JSON-fel. Ursprunglig parserväg återskapades i isolerad kod och visade felet. Regression använder 30 000 nivåer under storleksgränsen. |
| 9 dubbla kvalitetskontroller | Förenklat | Sakliga antal-/periodkontroller finns i kvalitetsbrister; besvara anropar dem efter svarshantering. Befintliga negativa kvalitetsprov kvar. |
| 10 POST-monolit | Förenklat | Sju namngivna hanterare, gemensam felrendering och separat datumtolkning. Exportfel ger inte datumfel. HTTP-/säkerhetsprov kvar. |
| Länpolicy | Beslutat | Grundsvar får rättas med gemensam län/paketuppdatering och invalidering; handredigerad konflikt stoppas. Spec rev14 och tillsynshjälp samordnade. |
| SCB-tabeller | Ej ändrade, verifierade | Officiell PDF anger OMS0 <1 tkr och ANST0 saknad, ANST1 noll. Befintliga tabeller korrekta; nya gränsprov. |
| Tidigare slutomdöme | Förtydligat | Omdömen gäller daterad och avgränsad granskning. Denna logg dokumenterar de senare funna bristerna. |

RED: första nya regressionerna gav 14 fel före rättning. Ett test använde det felstavade fältet `genomfor` från granskningsbeskrivningen; rätt kanoniskt fält är `genomforande`. Djuptestets nivå ökades eftersom pytest-processens rekursionsgräns tillät första provet. Första bredare delsviten gav 3 fel/124 passerade: fältnamnsfelet och två äldre prov som väntade avvisning först vid bekräftelse. Dessa anpassades till den nu tidigare datumgrinden; sakgrinden och bevarande provas fortsatt. Senaste riktade verifiering: 36 passerade (19 nya regressioner + registerlagring/webb), 17,37 s. Efterföljande helsvit och fristående granskning redovisas nedan.

Utvidgad källmatris och prioritering finns i [research 10, avsnitt 14.2](../../research/10-kallkontroll-och-gapinventering-m2.md#142-utvidgad-research-mindre-manuell-inmatning-2026-10-10). Ingen ny extern connector, dokumentimport eller gemensam bekräftelsevy ingår i rättningen. Användarens beslut 2026-10-11: gör först ett manuellt pilotintag för pilotbyrån och inventera faktiska exporter. Bygg därefter CSV/XLSX-import för det formatet; börja inte med en generell import.

Kompletterande RED-återprov: den tidigare generiska ValueError→datumfel-mappningen kördes i en isolerad pytest-plugin mot exportfelstestet och gav förväntat rött resultat (1 fel, 1,43 s). Produktionsfilerna ändrades inte. Testet ingår grönt i den ordinarie nya regressionen. Fristående teknisk review gav 19 passerade, 9,23 s, och inga konkreta P1/P2 i rättningarna; juridisk M2-riktighet, liveåtkomst och produktionsberedskap bedömdes inte och kvarstår som separata grindar.

Nytt verkligt webbläsarprov av filialkälla och okänt svar efter fynd 1–10-rättningarna: separat lokal server med syntetisk SCB-transport, start med eget filialunderlag, sparande av okänd fråga med tom roll och återläsning i svaröversikten. Bildbevis: `/Users/gt/Documents/Riskanalys/underlag/claude-rattningar-syntetiskt-prov-2026-10-10.png`. Testflik och tillfällig server stängdes efter provet; tidigare användarflikar/demoprocesser ändrades inte. Ingen extern SCB- eller AI-tjänst användes.

**Första helsvit efter rättningarna:** 956 passerade, 1 fel, 1 livetest bortvalt, 449,97 s. Det äldre M2-provet `test_m2_negativ_cli_skapar_inget_paket[felpaket]` avslöjade att intagets län/paket-samordning också kördes efter ett orelaterat CLI-svar. Då kunde en handredigerad länkonflikt tyst försvinna utan grundrättning eller full omprövning. Ny regression `test_ovrigt_svar_laker_inte_handredigerad_lanskonflikt` gav RED (1 fel, 1,21 s). Rättelse: bara ett uttryckligt sätesläns-/filialsvar får samordna profilens län/paket. Orelaterade svar bevarar konflikten och den rättsliga bedömningen förblir preliminär. Den befintliga negativa M2-grinden behålls; dess förväntan försvagas inte. Ny fokuserad och full verifiering redovisas nedan.

Återgranskningen hittade dessutom återbekräftelse med oförändrat fältvärde men motstridigt län/paket i Byra. Ny regression `test_aterbekraftat_lan_omprovar_belagg_vid_paketbyte` gav RED (1 fel, 1,20 s). Rättat: den kommande explicita län/paketuppdateringen räknas som ändring och utlöser samma invalidering. Riktad svit med samtliga 21 nya regressioner och det befintliga negativa M2-paketprovet: **22 passerade, 30,74 s**. Fristående read-only återgranskning provade fem fall (explicit byte, återbekräftelse vid konflikt, orelaterat svar, oförändrat län utan konflikt och filialbyte) utan kvarvarande konkreta P1/P2 i denna avgränsade ändring. Slutlig helsvit efter dessa rättelser redovisas nedan.

**Slutlig helsvit på rättad kod:** `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest -q` gav **959 passerade, 1 livetest bortvalt, 465,53 s (7:45)**, exitkod 0. Logg: `/tmp/riskanalys-claude-rattningar-slut-pytest.log`. Regelbasvalidering, `compileall -q src tester` och `git diff --check` passerar. Regelbas 1.1.0 har fortsatt sakkunnigstatus `ej_granskad`. Inga kod-/regelbasändringar efter helsvitens start; endast dokumentationsnoter. Autentiserade SCB-/AI-anrop, verkliga byrådata och M3/M4 ingår inte i denna verifiering. Ingen installation, commit eller push.

## Datumoberoende prov och CLI-längdfel 2026-10-11

Registerproven blandade det fasta bedömningsdatumet `DAG=2026-10-10` med verklig hämtningstid och dagens datum. De tio rapporterade registerfelen reproducerades i de tre berörda testfilerna. Körningen hade dessutom ett tillfälligt lagringsfel i `test_7_vet_inte_utan_roll_gar_att_spara` vid mycket lågt ledigt diskutrymme; separat återprov passerade. RED-logg: `/tmp/riskanalys-2026-10-11-register-red.log`.

En lokal autouse-fixtur i `tester/intag/conftest.py` låser intagets datumkontroller, formulärdatum, CLI-standarddatum och SCB-hämtningar till samma syntetiska dag. Hämtningstider ökas med mikrosekunder så att två bilder fortfarande får olika kontrollsummor. Historik-, framtids-, midnatts- och konfliktgrindarna i produktionen är oförändrade. Sökning i hela `tester/` hittade två explicita blandningar av `DAG` och `date.today()`; framtidsproven använder nu `DAG + 1 dag`. Övriga intagsvägar med intern körningsklocka omfattas av fixturen. M2:s separata CLI-processer använder explicita bedömnings-/bekräftelsedatum.

Fyra nya CLI-längdprov gav först **4 fel och 2 passerade gränsprov**, 2,11 s, med obehandlad `ValidationError` för svar, roll, källa och motivering. Konstruktion av `IntagSvar` omvandlar nu valideringsfelet till `ProfilFel` med svensk anvisning om argument och maximal längd. Inmatad text återges inte i felet. Proven kontrollerar oförändrade profilbytes och ingen skapad profilhistorik vid avvisning, samt lyckat sparande exakt vid 12 000 respektive 200 tecken. RED-logg: `/tmp/riskanalys-2026-10-11-cli-red.log`.

Riktad GREEN: **89 intagsprov passerade**, 172,03 s. Återprov av 62 register-/fråge-/fyndprov med simulerad omgivningsdag **2025-01-01** respektive **2030-01-01** gav **62 passerade per körning**, 19,50/19,58 s. Hjälpkörningarna hade varsin pytest-varning om redan importerad `anyio`, från startskriptets importordning. Loggar: `/tmp/riskanalys-2026-10-11-intag-green.log`, `/tmp/riskanalys-2026-10-11-clock-2025.log`, `/tmp/riskanalys-2026-10-11-clock-2030.log`. De två ursprungliga CLI-kommandona återprovades också som separata processer mot en tillfällig syntetisk profil: exit 1, kort svenskt fel, inget stackspår och oförändrad profil. Regelbasvalidering, compileall och diff --check passerar.

**Slutlig helsvit 2026-10-11:** `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest` gav **965 passerade, 1 livetest bortvalt, 458,81 s (7:38)**, exitkod 0, utan varningar. Logg: `/tmp/riskanalys-2026-10-11-full-pytest.log`. Kod och testuppsättning ändrades inte efter helsvitens start; endast dokumentationsnoter. Ingen commit/push. Nästa bygge börjar med manuellt pilotintag och exportinventering innan formatanpassad CSV/XLSX-import byggs.

## Förenklad registergranskning och tjänstelista 2026-10-11

På användarens begäran har befintligt SCB-/intagsflöde förenklats innan fler importer byggs. [Registerplanens genomförandelogg](2026-10-10-registerhamtning.md#genomförandelogg-för-förenklingen) redovisar samlad bekräftelse, atomiska svar, tydliga ersättningsval, rollförslag, lokal sessionsnyckel, mindre missvisande progress och negativa återprov. Alla elva tjänsteutbudsfrågor kan nu bekräftas tillsammans med gemensamt eget underlag; osäkra erbjudanden kan fortfarande markeras ”Vet inte” enskilt. [Ny research](../../research/10-kallkontroll-och-gapinventering-m2.md#143-ny-källkontroll-och-förenklat-godkännande-2026-10-11) skiljer byggd SCB-statusbakgrund från framtida Bolagsverket-åtkomst och pilotbyråns egna exporter. Det tidigare beslutet om manuellt pilotintag/exportinventering före formatanpassad CSV/XLSX-import gäller fortfarande. Ingen verklig pilotdata har hanterats av agenten i ändringen.

**Slutverifiering av förenklingen:** 990 passerade, 1 livetest bortvalt, 441,32 s (7:21), exitkod 0, utan varningar. Logg `/tmp/riskanalys-smidigt-final-full-pytest.log`. 25 nya regressioner ingår. Regelbasvalidering, compileall och diff --check passerar. Syntetiskt webbläsarprov och fristående granskning är redovisade i registerplanen. Endast dokumentation ändrades efter helsvitens start. Ingen commit/push, ingen ny CSV/XLSX-/BV-import och ingen ändring av verklig pilotprofil/server.
