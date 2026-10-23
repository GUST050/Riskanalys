# Resultatrapport R4–R7 – genomförande och underlag till Claude

**Datum:** 2026-10-23. **Gren:** `codex/kravstod-tjansteexponering`, separat lokal klon. **Bas:** `06405994125c87df5fa44d09844457f0cf1a6f7c` (godkänd R3). Ingen push, merge eller sändning till Claude ingår. Den andra klonen `feat/steg-1-3` har inte ändrats.

**Leveransgrind:** R4–R7 är tekniskt slutverifierade: **3436 ordinarie prov godkända**, ett liveprov bortvalt, noll fel/överhoppade prov. Hela kod-/test-/regel-/verktygssnapshotet är oförändrat. Ny rapportstandard är V9; AI:s skrivformat är fortsatt V8. Riskmetod, regelbas och modellidentitetens 25 filer är byteidentiska med basen.

## Vad som genomförts

| Steg | Resultat | Arbetscommit |
|---|---|---|
| R4 | Granska originalanalys och exakt V9-presentation; fryst krav-/källkarta; rätta tvådelsformuleringen i B1. | `f96c61e3c620bd397c2584ced09dbc01e67132d4` |
| R5 | Samlad sakgranskning av exakt R; tre delar i atomisk export/fastställelse/manifest; historisk byteverifiering; skyddad slutstatus. | `0c66301e6123b71fbc889159ba58cc383d99a936` |
| R6 | Tre kontrollerade nedladdningar; formatbyte utan AI; äldre V8-uppdatering behåller format; varning om förnyad sakgranskning. | `13a377eba9dcff54ef0f31655bc73d719151edfb` |
| R7 | Faktiska produktkedjor, V8/V9-jämförelse, alla analyslägen, PDF/layoutkontroll, V9-standard och slutgrind. | Slutcommit som innehåller detta dokument; exakt SHA i lokal Git-historik och bevisrotens leveranskontroll. |

Byrån svarar på gemensamma frågor en gång, som före rapportändringen. Resultatrapporten sammanställs ur samma data och fullständiga analys. Den lägger inte till sakfrågor, sammanfattningsfält, riskvikter eller AI-anrop. Analysgodkännande, dokumentets sakgranskning och beslut om fastställelse är fortfarande separata handlingar.

Den samlade resultatgranskningen binder lästa R-avsnitt till visad struktursumma, alla tre delarnas presentation, urval, källor, fynd och hela analysregistret. Den registrerar exakt R-avsnitten och godkänner aldrig A/B1. Formatbyte kräver ny sakgranskning även om analysen är lika; inga V8-attester förs över. Befintlig V8-export uppdateras i sitt sparade format om inget uttryckligt byte begärs.

## Svar på R3-granskningen

- B1:s exakta programtext ”Läsrapport och kompletterande underlagsbilaga utgör …” ingår nu i den uttömmande tredelstransformationen, med pointer och originaltext. Fryst V8-källa och byråns/AI:s originaltexter bevaras. Regressionen söker kända tvådelsformuleringar i synlig programtext i samtliga V9-delar; originaltexter omfattas inte.
- Sakgranska-kommandot använder tredelsförklaringen för V9 och den gamla texten för V8. CLI-provet kontrollerar den faktiska utskriften.
- Källförteckningen i A visas som **A15**. Utkastets inledning säger att paketet blir verifierbart när det fastställs med alla tre delar och ett gemensamt manifest.
- Ett vanligt renderingsanrop kan inte skapa V9-status ”Fastställt” med version/beslutsorgan. Endast den prövade fastställelsekedjan får passera slutrenderingen. Negativt renderingsprov och positivt faktiskt fastställelseprov finns.
- Hela A och B1 har renderats till PDF och sidlayouten har kontrollerats genom bilagorna; exakt omfattning redovisas nedan.

## Två tekniska fynd under genomförandet

**Fyndindexets omfattning.** Med den verkliga granskningslistan hade provfallen 430 respektive 438 maskinfynd, inte den tomma listan i R3-förhandsvisningen. Ett indexstycke per fyndgrupp skulle ensamt göra huvudrapporten lång. V9 visar nu antal per allvar/status och en uttrycklig hänvisning till hela den grupperade listan i B1. Varje fynd-ID, ursprunglig text, status och hänvisning finns kvar där och i den frysta presentationen. Lokala analysluckor/åtgärder står fortsatt i R6. Ingen brist accepteras och inga fastställelsespärrar tas bort. Ändringen är uttryckligen dokumenterad i designen och versionsbunden som `V9-lokala-original-2`; den skyddas med ett prov med 432 maskinfynd.

**Processberoende ordning.** En verklig nyprocesskontroll av mandatfallet upptäckte att kompletteringspunkter kom från en mängd i varierande ordning. Samma underlag kunde därför avvisas vid återbyggnad. `analysbilaga.py` sorterar nu punkterna deterministiskt, med reproducerande ordningsprov. Inga punkter tas bort, inga riskmodellfiler ändras och historiska paket omrenderas inte. Båda slutliga V9-presentationerna har återbyggts och jämförts i en ny process och båda exportmanifesten verifieras utan fel.

## Mätning med samma underlag

Följande är det befintliga mätkontraktets ordantal i dokumentets sakdelar, **inte** antal ord i hela Word-filen. V8 och V9 har för varje fall exakt samma bedömning, skrivutkast, utkastmanifest, historik och analysbindning. Båda är verkligt granskade och exporterade produktpaket med ofiltrerade fynd. Tidigare R0-siffror från andra versioner av mandatfixturen är inte jämförelsebas.

| Fall/format | Huvudrapport | A | B1 | Totalt | Upprepade extra ord |
|---|---:|---:|---:|---:|---:|
| Fyra tjänster V8 | 14 126 | – | 36 005 | 50 131 | 10 524 |
| Fyra tjänster V9 | 2 703 | 14 121 | 36 018 | 52 842 | 10 673 |
| Betalningsmandat V8 | 15 100 | – | 37 099 | 52 199 | 11 197 |
| Betalningsmandat V9 | 3 355 | 15 095 | 37 112 | 55 562 | 11 742 |

Huvudrapporten minskar 11 423 respektive 11 745 ord. Hela paketet ökar **2 711 respektive 3 363 ord**. Ingen total förkortning eller minskad fullständig granskningstid påstås. Hela motiveringar återges; exponeringstexten står i A med hänvisning från R. Flera självständigt nivåavgörande scenarier och oprövade sänkningar är uttryckliga i rapporten.

De kompletta Word-filernas synliga dokumentkropp innehåller också leveransrader, presentationslistor och hela fyndlistan:

| Fall | R, faktiska Word-ord | A, faktiska Word-ord | B1, faktiska Word-ord | Faktiska PDF-sidor R/A/B1 |
|---|---:|---:|---:|---|
| Fyra tjänster | 2 761 | 14 192 | 46 308 | **7 / 37 / 183** |
| Betalningsmandat | 3 413 | 15 166 | 47 563 | **8 / 39 / 190** |

Word-ord räknas ur alla `w:p` i `word/document.xml`, inklusive tabellceller, men utan sidhuvud/sidfot. Skillnaden mot mätkontraktet är särskilt stor i B1 eftersom hela granskningslistan tillkommer. Faktiska sidor kommer från de sex exporterade Word-filernas PDF-renderingar; inga uppskattade sidor har summerats.

Separat kompatibilitetsmätning kördes i **schema1**, **direkt2** och **overforing2** för båda fallen och båda formaten (12 körningar). Profil-, motor-, skrivsvars- och regelbassummor samt analysläge/schema/arbetsbordsutfall matchar V8/V9 i alla sex jämförelseparen. Primär före-/eftermätning ovan gäller direkt2. Schemaöverföring och attribution ändras inte av rapportvalet.

Provfallen har avsiktliga underlags-/kontrollbrister: 415 blockerande + 15 höga fynd respektive 423 blockerande + 15 höga. De är **utkast**, inte färdiga riskbedömningar som kan fastställas. Det separata positiva kedjeprovet använder en fullständig syntetisk, lokalt signerad regelbaskopia; repots sakkunnigstatus är oförändrad.

## Acceptans K01–K15

| Krav | Bevis |
|---|---|
| K01, samma svar/inga nya AI-anrop | `kompatibilitet/kontroll.json`, `test_uppdatera_v8_till_v9_anropar_inte_ai_och_bevarar_original`, verkligt CLI-prov. |
| K02, tre delar/atomisk publicering | `test_tre_exportfiler_och_verifiering`, `test_fel_vid_tredje_filen_publicerar_ingenting`, hela fastställelsekedjan. |
| K03, PT/TF och full kedja | `test_r4_och_r5_tillsammans_tacker_varje_tjansts_hela_kedja`, `test_hela_pt_tf_motiveringen_stannar_i_r5_men_exponering_hanvisas_till_a`. |
| K04, avgörande/egna/osäkerheter | Urvalsproven i `test_resultatunderlag_v9.py`, syntetisk egen TF-sårbarhet och antagande/okänt; negativa borttappningsprov i `test_dokument_v9.py`. |
| K05, samma nivåer/åtgärder | Exakta cell-/åtgärdsprov och `test_niva_eller_atgardsstatus_som_avviker_ger_fynd`; V8/V9-samma källor i verklig export. |
| K06, hela original/attribution | `test_v8_sakfalt_bevaras_med_uttommande_metadataundantag`, `test_tredelsundantag_bevarar_byrans_egna_original`, Word-text/presentation-matchning. |
| K07, spår och krav | Fryst `kravkarta-v9.json` per tillämpligt krav-ID, typed pointers, `test_kravkartans_gallande_element_har_r_sammanfattning_och_analysplats`, felpointerprov. |
| K08, visad R-granskning | `test_samlad_r_granskning_omfattar_exakt_alla_r_avsnitt`, ändrad analys/struktur och CLI:s felaktiga summa sparar inga beslut. |
| K09, oförändrade sakgrindar | `test_obelagd_reduktion_och_otackt_tf_sparrar_som_forut`, separata R/A/B1-attester i positivt/negativt kedjeprov. |
| K10, sparade format/historik | `test_befintligt_v8_och_v9_med_v8_skrivresultat_kan_faststallas_efter_standardbyte` i båda parametrarna; historisk verifiering förbjuder ny rendering/aktuell regelbas; äldre webbuppdatering bevarar V8. |
| K11, högst åtta sidor i referensfallen | Faktiska produkt-PDF:er **7 respektive 8 sidor**, 430/438 maskinfynd kvar i paketet; typsnitt/marginalprov. |
| K12, långa fall utan trunkering | Hela långmotiveringen bevaras; rådgivande omfattningsvarning; fler än fyra tjänster delas i matriser utan tappade celler. |
| K13, ärlig mätning | Två tabeller ovan, faktiska filer, `filkontroll.json`, `matning.json` och alla 12 kompatibilitetsmätningarna. |
| K14, färsk verifiering | **3436 godkända**, ett liveprov bortvalt; exakt collection/JUnit, noll fel/skip och 816 oförändrade resurser, Python 3.12.15. |
| K15, ovillkorlig PDF-kontrollpunkt | Användarens uttryckliga ”gå vidare med r3” efter godkänd granskning av `35b5be0`, därefter ”forstätt med r4-r7” efter godkänd R3 `0640599`. |

R2:s godkända PDF-summor var `74c98f3f959d13d9dec6cf5cf66a5047e6177b7b2a17fe07b359bf6c1aeb820f` och `e0e7c9f81c1d42564e800d7d1f6f752b782bf25c56ae4df543d7f906c7d30a0f`. De avser kontrollpunkten, inte de nya slutprovs-PDF:erna nedan.

## Visuell kontroll och avgränsning

Renderare: **LibreOfficeDev 26.8.0.0.alpha0**, bygg-ID `2c87e51eeaa2b413ff4ae097b2705eea1995d8e5`, via lokalt DOCX-renderingsverktyg. A4, Arial 11 punkter i brödtext, minst 9,5 i V9-tabeller och V8:s marginaler 18 mm i sidled/19 mm vertikalt. Programmet inför inget nytt produktberoende på LibreOffice eller Codex; Word kan också visa/exportera leveransfilerna.

Huvudrapporternas samtliga **15 sidor** har lästs och visuellt inspekterats individuellt. Bilagornas samtliga **76 A-sidor och 373 B1-sidor** har inspekterats för sidlayout genom kontaktark med sex sidor per bild. Den kontrollen bedömer sidflöde, tabeller och synlig överlappning/avklippning; den är inte en individuell fullstor sakläsning av varje bilagesida.

Efter ordningsrättningen jämfördes texten på **alla 464 slutliga PDF-sidor** med den visuellt granskade renderingen, med endast körnings-ID:n/kontrollsummor normaliserade. Inga R-/A-sidor ändrades; B1 ändrades på 8 respektive 12 sidor. Alla dessa 20 sidor omkontrollerades i större kontaktark. Slutliga PDF:er, alla sid-PNG:er och `sidjamforelse.json` är sparade. De 77 granskade kontaktarken finns i `layout-fore-ordningsfix/`; de fyra större omkontrollarken ligger i slutprovets B1-mappar. `typografikontroll.json` kontrollerar samtliga sex slutliga Word-filers stilar/tabellstorlekar/marginaler. Ingen synlig överlappning/avklippning noterades. A:s sista sida i fyrtjänstfallet innehåller bara en avslutande hänvisningsrad; det är en kvarstående mindre layoutpunkt.

Webbflödet är kontrollerat med den verkliga HTTP-serverhanteraren på loopback, inklusive alla tre hämtningar, CSRF/origin, inaktuell länk och byte av format utan AI. Ingen separat visuell webbläsargranskning påstås.

## Filer för läsning och granskning

Alla filer är syntetiska utkast. PDF:erna är granskningskopior från Word-exporterna; produktpaketets manifest binder de faktiska Word-filerna och de frysta källorna. PDF-kopiorna ligger utanför exportroten så att manifestet förblir verifierbart.

### Fyra tjänster

| Del | Word | PDF | PDF-sidor |
|---|---|---|---:|
| Resultatrapport | [Word](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r4-r7/filer/fyra_tjanster/allman-riskbedomning-UTKAST.docx>) | [PDF](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r4-r7/filer/fyra_tjanster/allman-riskbedomning-UTKAST.pdf>) | 7 |
| Analysbilaga A | [Word](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r4-r7/filer/fyra_tjanster/analysbilaga-UTKAST.docx>) | [PDF](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r4-r7/filer/fyra_tjanster/analysbilaga-UTKAST.pdf>) | 37 |
| Underlagsbilaga B1 | [Word](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r4-r7/filer/fyra_tjanster/underlagsbilaga-UTKAST.docx>) | [PDF](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r4-r7/filer/fyra_tjanster/underlagsbilaga-UTKAST.pdf>) | 183 |
### Med betalningsmandat

| Del | Word | PDF | PDF-sidor |
|---|---|---|---:|
| Resultatrapport | [Word](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r4-r7/filer/med_betalningsmandat/allman-riskbedomning-UTKAST.docx>) | [PDF](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r4-r7/filer/med_betalningsmandat/allman-riskbedomning-UTKAST.pdf>) | 8 |
| Analysbilaga A | [Word](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r4-r7/filer/med_betalningsmandat/analysbilaga-UTKAST.docx>) | [PDF](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r4-r7/filer/med_betalningsmandat/analysbilaga-UTKAST.pdf>) | 39 |
| Underlagsbilaga B1 | [Word](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r4-r7/filer/med_betalningsmandat/underlagsbilaga-UTKAST.docx>) | [PDF](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r4-r7/filer/med_betalningsmandat/underlagsbilaga-UTKAST.pdf>) | 190 |

### Kontrollsummor SHA-256

| Fall/fil | SHA-256 |
|---|---|
| `filer/fyra_tjanster/allman-riskbedomning-UTKAST.docx` | `f03e4f05520f7188594145e85cfca9b8f50f01462e8c8e6a0a4206290e8e24d1` |
| `filer/fyra_tjanster/allman-riskbedomning-UTKAST.pdf` | `643843bf5f60cee5366b016b7bad78fc18b812a81c0ff5f7a17c2770a31f0330` |
| `filer/fyra_tjanster/analysbilaga-UTKAST.docx` | `195fd39258c47eb0a87d8ca8ebfa9c15c174318792ad2e2d0e7d612f1f9625a6` |
| `filer/fyra_tjanster/analysbilaga-UTKAST.pdf` | `7b63b29894c357da358a5a0a56571d84b86b04b890b6dc6cfb98cc4114172c36` |
| `filer/fyra_tjanster/underlagsbilaga-UTKAST.docx` | `c2f011cf8932e2ddbce5111e79093abed33d1d761e1a3b8634b143358f7526b4` |
| `filer/fyra_tjanster/underlagsbilaga-UTKAST.pdf` | `87a5ed22d7363b8badd7bcf435f4ecf783b84564c37f1a782c2888bca5150865` |
| `filer/med_betalningsmandat/allman-riskbedomning-UTKAST.docx` | `9aa60ada6fb82744b201eb3404816e2d5e777d068ee72500396242f19279a2f2` |
| `filer/med_betalningsmandat/allman-riskbedomning-UTKAST.pdf` | `d6cd4c2dffa12e773074f663155a273e79195560cacc422aa94662c0f9ef77c9` |
| `filer/med_betalningsmandat/analysbilaga-UTKAST.docx` | `0b5e542e9eddce3d95e29005b2ee1da294899d7d92cab8aa42b11ccdb46a2020` |
| `filer/med_betalningsmandat/analysbilaga-UTKAST.pdf` | `47dfd535f901011b1b729d325a5d02dd9d580109d328334286a864feb0aba7a8` |
| `filer/med_betalningsmandat/underlagsbilaga-UTKAST.docx` | `f4c8e0233810955669123a873901a87e77d98b99e39f9c467d9dffdb0a54dfce` |
| `filer/med_betalningsmandat/underlagsbilaga-UTKAST.pdf` | `aedc6740aa3e3f8dffc6f544baa08c57d3f1c800adeac85674808f7eb7d1a99d` |

## Råbevis och reproduktion

Bevisrot: [/Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r4-r7](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r4-r7>), lokalt ignorerad i Git. `produktprov/` innehåller frysta profiler, bedömningar, analyser, skrivresultat, granskningar, faktiska V8/V9-exporter och renderingar. `kompatibilitet/` innehåller alla 12 format-/analyslägeskörningar. `filkontroll.json` binder de 12 läsfilerna, och `aterbyggnad-och-modellkontroll.json` visar aktuell nyprocesskontroll och oförändrade modellfiler/regelbas. Slutliga testbevis finns under `tester/slutlig-snabb/` och `tester/slutlig-full/`, med resultat, rålogg, collection, JUnit och snapshot. De första profilerna har ett gemensamt 816-filssnapshot, SHA-256 `25f078fe63689f9f118c3c026132e08cefc923b8a159ea948cd4850686279def`. Första fullprofilen gav 3 431 godkända och fem historiska M2-formatassertioner, samtliga i samma hjälpare. Hjälparens kvarvarande hårdkodning missades i det riktade standardbytesurvalet och fångades av fullsviten. De fem fallen passerar efter ett uttryckligt V8-val (189,58 s); ingen assertion eller domängrind tas bort. Den följande körningens reproducerade HTTP-klientrace och avbrott redovisas nedan. Samtliga körningar bevaras; endast den sista kompletta gröna fullprofilen räknas som leveransgrind. Körningarnas HEAD är R6-commit `13a377e`; de då ocommittade R7-källändringarna binds av snapshotet, inte av en felaktig hänvisning till R6 som färdig kodbas.

```sh
.venv312/bin/python docs/research/verktyg/resultatrapport_slutprov.py --ut /private/tmp/riskanalys-v9-produktprov-NYTT_ID
.venv312/bin/python docs/research/verktyg/rapportmatning.py --help
.venv312/bin/python scripts/testa.py snabb --ut /private/tmp/riskanalys-snabb-NYTT_ID
.venv312/bin/python scripts/testa.py analys --ut /private/tmp/riskanalys-analys-NYTT_ID
.venv312/bin/python scripts/testa.py full --ut /private/tmp/riskanalys-full-NYTT_ID
```

Mätverktygets hjälpflagga är `--help`; använd format `v8` eller `v9` och analysläge enligt den visade hjälpen. Befintliga mätkommandon har fortsatt V8 som standard för jämförbar historik, oberoende av produktens V9-standard.

## Verifiering och kvarstående granskning

**Slutlig snabbprofil: 140 godkända / 44,751 s. Slutlig fullprofil: 3436 godkända / 2159,897 s**, inklusive collection, Python 3.12.15. Ett liveprov bortvalt i fullprofilen; noll failures/errors/skipped, exakt collection/JUnit och samma 816-filssnapshot i snabb/full. Ingen ordinarie testgrupp är bortvald. Snapshotfilens SHA-256 är `518813e783dfba1f927800bd6b3d68578eb557362b1e6f4c8b09b2c64e1ef79d`. Källsnapshotet kontrolleras igen efter leveranscommit och binds då till dess exakta SHA i `leveranskontroll.json`.

Analysprofilen gav tidigare **293 godkända / 376,465 s** på det första snapshotet, före de två sista testhjälparrättningarna. Den kördes inte separat på nytt; samtliga analysprov ingår i den kompletta slutliga fullprofilen. Analysprofilens 180-sekundersmål överskrids. Ingen ytterligare testoptimering eller tidsvinst för fullsviten påstås.

Regelbasvalidering och `git diff --check` passerar. Regelbasens kontrollsumma är `sha256:b4dc7018b05b340e746d31efd0a49ee837fa1312c126a24f5571445a27132a58`; sakkunnigstatus är fortsatt `ej_granskad`. Båda faktiska V9-exporternas manifest och aktuella nyprocessåterbyggnad är verifierade utan fel. De tolv Word-/PDF-kopiornas hashvärden matchar tabellen.

De riktade RED/GREEN-körningarna och rättningshistoriken bevaras i arbetsloggen. Under R7 behövde historiska V6/V7/V8-fixturer uttryckligen välja sitt historiska rapportformat när produktstandarden byttes; deras historiska kontrakt prövas fortsatt. Det generella intagsprovet skiljer AI:s skrivformat från rapportformatet och kontrollerar hela trepartsleveransen för originaltexter. Den slutliga fullsviten omfattar också alla dessa teständringar.

Ingen separat agentgranskning har startats, enligt uppdragets arbetssätt. Egen genomgång omfattar slutformat/grindar, frysta källor, atomisk publicering, hela original och bakåtkompatibilitet; användarens externa Claude-granskning återstår. Kända avgränsningar: inga nya metodbeslut D3/D9, ingen manuell motorlös tjänsteanalys och ingen förkortning av bilagornas fullständiga text. Att resultatrapporten är kort innebär inte att hela paketet sakgranskas automatiskt.


### Föreslaget granskningsfokus för Claude

1. Kan någon R-text, matrisruta, kravpointer eller fryst presentation ändras och ändå återanvända sakgranskningen? Kontrollera aktuella återbyggnader och att historisk verifiering använder den sparade källan.
2. Stoppar saknad tredje fil, fel vid rendering och ändrat register hela publiceringen? Kontrollera särskilt att samlad R-granskning aldrig godkänner A/B1.
3. Bevaras V8-utkast och V8-skrivresultat efter standardbytet, inklusive tomt nytt utkast och båda positiva fastställelseparametrarna?
4. Är den korta hänvisningen till B1:s fulla maskinfyndlista tydlig nog? Fyndens ID/status/text är kvar, men resultatrapporten har inte längre ett stycke per fyndgrupp.
5. Läs huvudrapporterna och stickprova A/B1. Provfallen är medvetet ofullständiga; en PDF-förhandsvisning är inte bevis för en godkänd verklig riskbedömning. Den stora bilagevolymen och analysprofilens tid är kvarstående praktiska kostnader.


### Avgränsad stabilisering av ett äldre HTTP-prov

Den andra fullkörningen avbröts efter ett underkänt webbprov: 2 618 godkända och ett fel av 3 436 insamlade. Den räknas inte som godkänd fullgrind. Det exakta felet reproducerades separat i cykel 41: urllib hann skicka en chunk-slutmarkör efter att servern redan avvisat den otillåtna överföringen. Resultatet blev BrokenPipe före läsningen av det korrekta HTTP-avslaget. Den berörda produktfunktionen var oförändrad.

Provet skickar nu de otillåtna överföringsheadersen och läser HTTP 400 direkt, utan kropp/trailer. Det kontrollerar den specifika feltexten och att ingen profil skapas. Okänd väg HTTP 404 och den verkliga för stora kroppen HTTP 413 är kvar. **500 hela trestegsförlopp passerade**, utan återförsök, högre timeout eller undantag som räknas som godkänt. Råloggar ligger under `tester/webb-reproduktion/`. Ny färsk fullprofil krävs också efter denna teständring och redovisas som den enda slutgrinden ovan.
