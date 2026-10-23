# Svar på granskningen av R4–R7 – del 1

Datum: 2026-10-23. Bas: `570bf9a` på `codex/kravstod-tjansteexponering`, separat lokal klon. Uppdrag: del 1 i användarens revision 3. **Status: del 1 tekniskt slutverifierad. 3 448 ordinarie prov godkända, ett liveprov bortvalt, noll fel/överhoppade prov.** Ingen push eller merge.

## R-granskningen

- Den publika domänfunktionen `registrera_sakgranskning` avvisar enskilda beslut för V9:s resultatavsnitt, både godkännande och underkännande. Felet hänvisar till `--resultatrapport` och `--visad-struktursumma`. CLI sparar ingenting vid avslag; provet jämför sparfilens bytes före/efter.
- Den samlade vägen kontrollerar som förut hela den visade strukturen/presentationen och analysbindningen. Varje R-post får dessutom `granskningssatt: samlad_resultatrapport`. A och B1 godkänns aldrig av denna handling och kan fortsatt granskas enskilt.
- Äldre R-poster utan styrkt granskningssätt gäller inte inför ny fastställelse, även med rätt text-, struktur- och analyssummor. Vyn och fastställelsens fel visar hur förnyad samlad granskning görs. Den senaste underkända samlade granskningen har fortsatt företräde.
- Ett saknat nytt fält utelämnas vid serialisering. Ett verkligt V9-paket skapades och fastställdes med koden före rättningen; efter rättningen verifieras det fortfarande och samtliga **366 filer är byteidentiska**. Ingen historisk granskning eller export skrivs om. Även de fyra tidigare V8/V9-exporterna för referensfallen verifieras utan byteändring (13/20 filer per fall).

## Mindre punkter

1. Antalet blockerande maskinfynd följs av **”Blockerande fynd hindrar fastställelse.”** Hela fyndkällan finns kvar i B1.
2. Körnings-ID i inledningen visas som datum/tid i **Europe/Stockholm**, exempelvis `2026-10-23 kl. 10:51:37 (Europe/Stockholm)`. De fullständiga identiteterna ligger kvar i leveransdata och manifest. Äldre frysta leveransmallar behåller sitt ursprungliga visningssätt.
3. Källförteckningen i A15 har mindre styckeavstånd, med samma textstorlek och allt innehåll kvar. Hänvisningar hålls ihop med föregående stycke. Fyrtjänstfallets ensamma hänvisningssida försvinner.
4. `docs/testning.md` anger uttryckligen den accepterade avvikelsen **376,465 s mot analysprofilens mål 180 s**. Målet ligger kvar; ingen testoptimering eller bortsortering av prov ingår.

Leveransmallen är `D-ARB-v9-leveransmall-2`, renderingspolicyn `V9-lokala-original-3`. Äldre utkast behöver ny granskning för att återbyggas med den aktuella presentationen; redan exporterade och fastställda paket verifieras utifrån sina frysta källor. Detta är ingen ny rapportdisposition enligt del 3.

## Prov och bevis

| Kontroll | Utfall |
|---|---|
| Baslinje, befintlig sakgranskning och samlad R-granskning | 15 godkända / 20,35 s |
| RED för domänspärr, granskningssätt och äldre R-poster | 5 förväntade fel, 8 godkända / 24,39 s |
| RED för fyndförklaring och läsbar körningstid | 2 förväntade fel, 1 godkänd / 0,16 s |
| Berörda enhets-/CLI-/V8-/V9-/fastställelseprov efter rättning | 111 godkända / 230,93 s |
| Renderingsprov efter sista layoutändringen | 20 godkända / 11,59 s |
| Snabbprofil på slutligt kodsnapshot | 140 godkända / 48.760 s inklusive collection; verifierad efter sista teständringen |
| Första fullprofilen i sandbox | 3 239 godkända, 6 failures + 203 setupfel, ett liveprov bortvalt / 1 673,869 s; inte verifierad |
| Loopback-prov med tillåtna lokala portar | 2 godkända / 22,57 s |
| Gemensamt positivt fastställelseprov med samlad R-granskning | 1 godkänd / 98,23 s |
| Ny fullprofil på slutligt kodsnapshot | **3 448 godkända / 2207.161 s inklusive collection**, Python 3.12.15, exit 0, ett liveprov bortvalt |

Den första kombinerade GREEN-körningen gav 26 godkända och ett fel: fastställelsen spärrade redan äldre R-poster korrekt men saknade den konkreta CLI-anvisningen i feltexten. Anvisningen lades till; hela det berörda urvalet ovan passerar. Råloggen bevaras som mellanresultat och räknas inte som slutgrind.

Den första fullsviten kördes med för snäva sandboxrättigheter: 203 setupfel och fem failures är `PermissionError` när de syntetiska webbproven öppnar en lokal port på `127.0.0.1`. En minimal socketprobe reproducerar felet i sandboxen och lyckas med godkänd eskalering. Två representativa webbprov passerar i rätt körmiljö. Den sjätte failuren är `test_sakgranskad_gemensam_analys_kan_faststallas`, vars äldre provkod godkände R enskilt. Provet använder nu den publika samlade vägen med visad struktursumma och därefter separat A/B1-granskning. Alla dess befintliga risk-/fastställelseassertioner behålls. Efter teständringen kördes den nya kompletta gröna fullsviten ovan; första körningen är bevarad under `tester/full-sandbox/`.

Regelbasvalideringen passerar: version 2.0.0, 107 krav, 11 tjänster och samtliga tre paragrafkartor fortsatt `ej_granskad`. Riskmodellens **25 kodfiler** och hela regelbasen är byteidentiska med basen. Inga nya AI-anrop, sakfrågor eller sakkunnigbeslut ingår. Proven använder bara syntetiska uppgifter och Testleverantor; den positiva fastställelsen använder som förut en signerad regelbaskopia.

Bevisrot: [.superpowers/evidens/2026-10-23-r4-r7-rattning](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-r4-r7-rattning>). Där finns RED/GREEN-råloggar, modellkontroll, ett äldre V9-paket med filhashar, aktuella frysta presentationsdata och PDF/layoutbevis. Testprofilerna sparar collection, JUnit och exakt källsnapshot. Slutbevis: `tester/full-slut/` och `tester/snabb-efter-kedjeprov/`. Fullsvitens collection och JUnit matchar exakt; noll fel och överhoppade prov. Samtliga **816 resurser** i kod-/test-/regel-/verktygssnapshotet är oförändrade. Snapshotfilens SHA-256: `fce36a3c075eae11194dbfeb98782fce26e9aa6c3fc400eaf4359ce4b8e52711`. Testresultatets HEAD är `570bf9a` med arbetsändringar; snapshotet binder den faktiskt provade koden och kontrolleras även efter leveranscommit.

## PDF-kontroll

Läsproven återanvänder exakt samma frysta profiler, bedömningar, analyser och skrivresultat som R4–R7:s två referensfall, inklusive samtliga **430/438 maskinfynd**. Presentationens saktexter och urval jämförs strukturellt med de tidigare frysta vyerna. Endast den begärda fyndförklaringen, leveransraden och sidflödet ändras. Läsproven är syntetiska **utkast**, inga nya fastställda produktpaket.

| Fall | Resultatrapport | Bilaga A | Bilaga B1 |
|---|---:|---:|---:|
| Fyra tjänster | 7 sidor | **36 sidor** (tidigare 37) | 183 sidor |
| Betalningsmandat | 8 sidor | 39 sidor | 190 sidor |

Samtliga **15 huvudrapportssidor**, första och sista två sidorna i respektive A samt första sidan i respektive B1 är visuellt kontrollerade i slutliga PDF-raster. Ingen synlig överlappning eller klippning i det granskade urvalet. Övriga bilagesidor är inte på nytt visuellt genomlästa; all deras dokumentmodelltext är oförändrad. Renderare: befintlig buntad LibreOfficeDev, samma som R4–R7. Den skriver Fontconfig-cachevarningar i sandboxen men slutför alla sex PDF-konverteringar med exit 0; slutliga raster har kontrollerats.

| Fall | Resultatrapport | Bilaga A | Bilaga B1 |
|---|---|---|---|
| Fyra tjänster | [PDF](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-r4-r7-rattning/lasprov/fyra_tjanster/allman-riskbedomning-UTKAST.pdf>) | [PDF](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-r4-r7-rattning/lasprov/fyra_tjanster/analysbilaga-UTKAST.pdf>) | [PDF](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-r4-r7-rattning/lasprov/fyra_tjanster/underlagsbilaga-UTKAST.pdf>) |
| Betalningsmandat | [PDF](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-r4-r7-rattning/lasprov/med_betalningsmandat/allman-riskbedomning-UTKAST.pdf>) | [PDF](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-r4-r7-rattning/lasprov/med_betalningsmandat/analysbilaga-UTKAST.pdf>) | [PDF](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-r4-r7-rattning/lasprov/med_betalningsmandat/underlagsbilaga-UTKAST.pdf>) |

## Granskning och nästa kontrollpunkt

Författaren har gjort en separat genomgång av hela diffen mot del 1: direkt domänväg, äldre poster, senaste underkännande, historisk serialisering och paketverifiering samt oförändrade saktexter. Ingen oberoende kodgranskare har använts; användarens granskning med Claude återstår.

Del 2 steg A, katalog-/metodändringar och del 3 är inte påbörjade. Uppdraget kräver granskning av denna del före nästa steg. Grenen lämnas lokalt; ingen push eller merge.
