# Kort resultatrapport – genomförandeplan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Ingen implementation före användarens granskning med Claude och godkännande av den reviderade designen och planen. Använd inga subagenter utan separat instruktion.

**Goal:** Skapa en kort, automatiskt sammanställd resultatrapport med fullständig analys och underlag i två bilagor, utan nya sakfrågor eller AI-anrop.

**Architecture:** Behåll V8-skrivresultaten och den fullständiga analysen som källa. Redovisa gemensamma scenariokedjor en gång i R4:s tjänstematris och tjänstens egna förhållanden i R5. Bygg ett nytt V9-dokument med tre leveransvyer och en fryst spår-/täckningskarta. Stanna efter R2 för obligatorisk läsning av två PDF-förhandsvisningar före kedjeintegration.

**Tech Stack:** Python 3.12 via `.venv312/bin/python`, befintlig Pydantic, pytest och python-docx. Inga nya produktberoenden, externa AI-anrop eller ändringar av riskmetoden.

**Spec:** [2026-10-22-resultatrapport-design.md](../specs/2026-10-22-resultatrapport-design.md), revision 2, uppdaterad 2026-10-23 efter Claudes granskning. Även planen är revision 2. R0–R2 är implementerade och PDF-kontrollpunkten är passerad genom användarens uttryckliga klartecken på `35b5be0`. R3 är implementerad för granskning. R4–R7 återstår.

**R2-rättning efter `f653eea`:** användarens tre PDF-fynd rättas före förnyat klartecken. Oprövade/ej godtagna sänkningar ska synas i cellen och förklaras i R5, även om scenariot inte avgör tjänstens nivå. Gamla och nya standardmotiveringar ska spärras i analysgrinden och ge presentationsbrist. Mandatfixturen ska ha egen mekanism, avvikelsekoppling och konsekventa hela motiveringar. R3–R7:s kontrollpunkt består. [Genomförande och verifiering](../reviews/2026-10-23-svar-claude-resultatrapport-r2.md).

**Base:** `4a878b9bb35a2489e902fd341a6391cc4ce4f7fa`, `codex/kravstod-tjansteexponering`. Läs AGENTS.md, designspecens avsnitt 4/5/8/10–11, aktuell STATUS och detta designunderlag. Verifiera basen igen vid genomförandet; senare ändringar får inte skrivas över eller behandlas som om basen vore oförändrad.
**Dokumentbas:** revision 1 ligger i `6e34cfd`; produktkoden har inte ändrats av dokumentrevisionerna.
**Genomförandebeslut 2026-10-23:** R0–R2 får börja med tilläggen nedan; R2:s obligatoriska PDF-granskning kvarstår. R3–R7 är inte godkända genom att denna start godkänts.

## Global Constraints

- Byrån svarar fortsatt på gemensamma sårbarhetsfrågor en gång. Resultatrapporten kräver inga nya sakuppgifter, sammanfattningsfält eller AI-anrop.
- Nytt dokumentformat är `D-ARB-resultat-v9`. AI:s skrivformat är fortsatt `D-ARB-tjanst-v8`. Historiska V8-paket verifieras oförändrade.
- Riskmetod, D3/D9, kataloginnehåll, sakkunnigstatus, analysens schema 1/2 och AI:s skrivformat ändras inte.
- Alla tillämpliga krav måste täckas i paketet. Regelbasens kravtext och hänvisningar ändras inte enbart för att byta rapportlayout.
- Källfält som används som citat återges helt med attribution; inga första-meningen-utdrag, ellipser eller automatisk omskrivning av fri text.
- Resultatrapportens mål är 5–8 sidor för de två fyrtjänstfallen. Högst åtta sidor är acceptans för dessa fall, inte ett absolut sidtak för alla byråer.
- Använd A4 och läsbar typografi: brödtext minst 11 punkter, tabelltext minst 9,5 punkter; inte mindre marginaler än V8.
- Bilagornas ordinarie sakgranskning kvarstår. Gamla V8-attester förs inte över. Ingen selektiv förnyelse införs.
- Efter R2 lämnas båda offline-byggda resultatrapporterna som PDF till användaren för läsning och granskning med Claude. R3–R7 börjar först efter uttryckligt klartecken till de visade versionerna.
- Enda standardkonstanten är `rapportversion.AKTUELL_DOKUMENTVERSION`, flyttad från `skrivversion.py`. Ingen parallell rapportversionskonstant eller kopierat alias införs.
- Python 3.12, riktad RED/GREEN och snabbprofil under arbetet; en färsk full icke-live-svit på slutligt källsnapshot enligt AGENTS regel 6.
- Alla prov använder syntetiska data och Testleverantor. Inga byrådata i repot. Ingen push/merge eller sändning till Claude ingår.

## Review Focus

1. En gemensam matrisrad döljer ett TF-hot, en egen sårbarhet eller olika kontrollutfall: R1–R2 provar separat medlemskap per tjänst/hot/dimension/riskled, identisk kärntext och skilda cellvärden.
2. En lång fri motivering gör sidmålet svårt: R2/R7 provar hela originaltexten och rådgivande överskridande, aldrig avklippning.
3. En gammal konstantimport eller skrivformatet väljer fel rapportgren: R1 provar samtliga importer och historiska fallback, R4/R7 provar uttryckliga format och V9-standard med V8-skrivresultat.
4. En källa ändras efter visning eller under tredje filens export: R5–R6 provar föråldrad granskning/nedladdning och atomiskt avslag utan delpaket.
5. Ett gammalt fastställt V8-paket öppnas efter standardbytet: R5/R7 provar fryst byteverifiering utan ny rendering eller krav på aktuell regelbas.

## Filkarta och avgränsning

Nya produktfiler:

| Filer | Ansvar | Uppgift |
|---|---|---|
| `dokument/rapportversion.py`, `resultatmodell_v9.py`, `resultatunderlag_v9.py` | Rapportversion, källreferenser och deterministiskt urval. | R1 |
| `dokument/resultatrapport_v9.py`, `arb_v9.py`, `rapportvyer_v9.py` | R-delar, full dokumentbyggnad och tre vyer. | R2 |
| `dokument/presentation_v9.py`, `leverans_v9.py`, `rendering_v9.py` | Fryst presentation, tre filnamn och Word-rendering. | R3 |
| `granskning/dokument_v9.py` | Innehålls-, krav- och spårkontroll med befintliga analysgrindar. | R4 |
| `dokument/rapportpaket_v9.py`, `faststallelse/resultatgranskning.py` | Aktuell/historisk verifiering och samlad R-granskning. | R5 |

Till R2 kommer granskningsverktyget `docs/research/verktyg/resultatrapport_offline.py`. Det skapar ofastställda förhandsvisningar och används inte av produktens export-/fastställelseflöde. Att producera PDF-förhandsvisningen ska inte kräva att R3–R7 först implementeras.

Alla sökvägar ovan är relativt `src/riskanalys/`. Ändra endast berörda delar i befintliga filer, enligt uppgifterna nedan. V8:s tvåvys-/renderings-/attestkontrakt behålls. En liten versionsdispatch kan delas; ingen generell omskrivning av äldre dokumentversioner ingår.

Under R0 inventeras alla formatgrenar med `rg`; det är ett skydd mot missade anrop, inte tillstånd att bredda uppdraget. Produkt-/testfiler som tillkommer utöver denna karta ska motiveras i körloggen. Blanda inte in ytterligare testoptimering.

## R0: Lås källor och jämförelsekontrakt

**Files:** Read `AGENTS.md`, `docs/{STATUS,testning,kravstod}.md`, specifikationen och befintliga V8-enhets-/intagsprov. Create `docs/superpowers/reviews/2026-10-23-resultatrapport-r2.md` som första granskningslogg; slutprovslogg tillkommer vid R7. Syntetisk råevidens placeras i `.superpowers/evidens/2026-10-23-resultatrapport-r2/` och planens SDD-arbetskatalog; inga genererade byrådata committas.

**Interfaces:** Före-/efterkontraktet använder `frysta_skrivsvar` från `docs/research/verktyg/matkontrakt.py` och `bygg`/`valj_lage` från `analyslagen.py`. Jämförelser sker per samma syntetiska fall och läge, inte mellan orelaterade modell-/profilversioner.

- [x] Kontrollera `git status --short`, `git rev-parse HEAD` och `.venv312/bin/python --version`; spara utfall. Läs den tidigare gröna verifieringens snapshot men påstå inte att den testar V9.
- [x] Inventera `rg -n 'D-ARB-tjanst-v8|AKTUELL_DOKUMENTVERSION|rapportvyer|rapportpaket_v8|lasrapport|underlagsbilaga' src/riskanalys`. Notera varje gren som berör byggnad, modellvalidering, granskning, rendering, sakgranskning, export, fastställelse, manifest och HTTP-nedladdning. Markera ägare R1–R7.
- [x] Utöka konstantinventeringen till `src` och `tester`. Flytten i R1 omfattar dagens `dokument/{arb,arb_v6,skrivversion}.py`, `faststallelse/faststall.py`, `tester/intag/test_kedja.py` och `tester/enhet/{test_formathinder,test_skrivformat_v7,test_skrivformat_v8,test_rapportpaket_v8}.py`. Samla nytillkomna träffar innan ändringen, inte först efter standardbytet.
- [x] Kör aktuell `rapportmatning.py` för `fyra_tjanster` och `med_betalningsmandat` med `--analyslage direkt2`. Kontrollera 14 126/13 803 ord i läsrapporten och 36 005/36 150 i B1 eller förklara varje avvikelse innan fortsatt jämförelse.
- [x] Frys profil-, motor-, analys-, historik-, regelbas- och skrivsvarssummor samt faktiska V8-exporter. Bevara tidigare evidens; använd nya mappar. Samla en historisk V8-paketfixtur som redan verifieras, inte ett V9-paket med ändrad etikett.
- [x] Skriv bas och inventering i körloggen. Ingen fullsvit behövs för denna rena basmätning på oförändrad kod. Dokumentationscommit får hållas ihop med nästa arbetscommit.

## R1: Typat urval och källreferenser

**Files:** Create `src/riskanalys/dokument/{rapportversion,resultatmodell_v9,resultatunderlag_v9}.py`, `tester/enhet/{test_resultatunderlag_v9,test_rapportversion}.py`. Modify konstantimporterna i R0:s namngivna produkt-/testfiler. Reuse `bedomning/modeller.py`, `analys/gemensam.py` och befintliga härledda riktnings-/täckningsfunktioner utan ändrade riskregler.

**Interfaces, nya och beslutade i denna plan:**

- `rapportversion.V9 = 'D-ARB-resultat-v9'`; flytta den enda `AKTUELL_DOKUMENTVERSION` till denna modul, med värdet V8 under R1–R6 och V9 först i R7. Ta bort den gamla definitionen från `skrivversion.py`, uppdatera samtliga importer/monkeypatcher i samma commit och inför inget återexporterat alias. `AKTUELL_SKRIVVERSION = V8` och historiska skrivversions-ID lämnas oförändrade. Inga versionsberoenden från `rapportversion.py` tillbaka till dokumentbyggare.
- Alla nya modeller är frysta Pydantic-modeller med `extra='forbid'`.
- `Kallreferens(artefakt: Literal['profil','bedomning','analys','skrivresultat','historik','regelbas','analysdokument'], pointer: str, summa: str)`. `summa` avser det lösta värdet; artefakternas fulla summor binds separat i byggresultatet. Pointer följer RFC 6901; tom pointer är artefaktens rot.
- `Urvalspost(id: str, tjanst: str|None, hot: tuple[str,...], dimension: Literal['pt','tf']|None, riskled: Literal['inneboende','kvarstaende']|None, hantering: Literal['sammanfattas','hanvisas'], skal: tuple[str,...], kallor: tuple[Kallreferens,...])`. `skal` valideras till `avgor_fore`, `avgor_efter`, `egen_sarbarhet`, `avvikelse`, `osakerhet`, `erfarenhet`, `atgard`, `oppet_gap`, `ej_relevant` eller `metoduppfoljning`; ingen poäng eller prioritering härleds från listordning. Även bilagehänvisade kandidater sparas med skäl så att ett utelämnande kan granskas.
- `Presentationsbrist(kod: str, avsnitt: str, beskrivning: str, kallor: tuple[Kallreferens,...])` representerar saknat obligatoriskt innehåll; alla sådana brister blockerar fastställelse men inte märkt utkastsexport.
- `ResultatunderlagV9(poster: tuple[Urvalspost,...], brister: tuple[Presentationsbrist,...])`.
- Utöka underlaget med `matris: tuple[ScenarioradV9,...]`. `ScenariocellV9(tjanst: str, scenario: Scenariobedomning|None, status: Literal['beraknad','ej_relevant','saknas','okant'], medlemmar: tuple[str,...], kallor: tuple[Kallreferens,...])` bevarar källans fulla scenarioobjekt och valda urvalspost-ID per tjänst. `ScenarioradV9(id: str, hot: str, dimension: Literal['pt','tf'], mekanismkallor: tuple[Kallreferens,...], celler: tuple[ScenariocellV9,...])` tillåter olika nivåer i olika celler men inte att de slås ihop. Falskt `ej_relevant` får inte härledas ur att motorn saknar ett scenario.
- `bygg_resultatunderlag(rb, profil, bedomning, resultat, historik, *, analys, analysdokument: Dokument) -> ResultatunderlagV9` är ren och använder originalpaketet för pointers, effektiva läsvyer bara för härledning.

- [x] Skriv `test_alla_avgorande_fore_och_efter_bevaras_per_dimension`, `test_lagre_tf_hot_forsvinner_inte_bakom_pt`, `test_egen_sarbarhet_utan_motoraktivering_tas_med` och `test_antagande_och_okant_villkor_forblir_osakert`. Assert exakt tjänst/hot/dimension/riskled och urvalsskäl, inte bara antal poster.
- [x] Skriv `test_bekraftad_ej_relevant_post_far_bilagereferens`, `test_d9_under_troskel_ar_inte_modellkonflikt`, `test_noll_egen_rapportering_aterges` och `test_kallpointer_pekar_pa_original_inte_lasvy`. Saknad/utbytt källa ska ge explicit fel eller presentationsbrist, aldrig en generisk motivering.
- [x] Skriv `test_gemensam_kedja_har_alla_tjanstemedlemmar`, `test_samma_hot_med_olika_kontrolleffekt_bevarar_varje_cells_hela_scenario`, `test_lika_niva_med_olika_mekanism_far_inte_samma_forklaring` och `test_matris_skiljer_saknat_ej_relevant_okant_och_tf_utan_efterniva`. Jämför exakt medlemsmängd `(tjänst, hot, dimension, riskled)` före och efter presentationsgruppering, inklusive belägg/status; inte bara antal rader.
- [x] Skriv `test_en_enda_aktuell_dokumentversion`, `test_flyttad_konstant_bevarar_v8_standard_fore_inforande` och `test_v6_v7_byggare_far_inte_v9_som_skrivformatsfallback`. Testa alla produktimporter och justera gamla standardvalsassertioner så att skrivstandard och dokumentstandard prövas separat. Historiska V8-fixturer väljer explicit V8 i stället för att förutsätta att det alltid är standard.
- [x] Kör RED: `.venv312/bin/python -m pytest tester/enhet/test_resultatunderlag_v9.py -q`. Dokumentera att felet gäller den saknade funktionen/beteendet.
- [x] Implementera urvalsreglerna i designens 5.2 och matrisreglerna i 5.1.1. Bevara källornas tjänsteordning som kolumnordning; rader ordnas PT före TF, sedan första förekomsten i källornas ordning. Egna varianter får egna rad-/scenario-ID. Hela valda medlemsmängden bevaras; inga topp-N-val eller nya numeriska gränser. Delad kärntext kräver samma mekanism och, för den delade nivåförklaringen, identisk nivåväg, kontrollpåverkan och status.
- [x] Flytta konstanten enligt kontraktet ovan. I `kontrollera_v6_utkast` bevaras det gamla avvisningsbeteendet för tomma/blandade resultat: välj explicit format eller en entydig historisk skrivversion, inte den nya rapportstandarden. `faststall.py` får rätt konstantimport i detta steg; versionsprövningen av faktiska V9-dokument färdigställs i R5 när dokumentmodellen och paketkedjan finns.
- [x] Kör samma fil GREEN och berörda riktnings-/täckningsprov. Lägg den lilla rena filen i snabbprofilen och kör `scripts/testa.py snabb` med ny `--ut`-mapp. Commit: `feat: härled källbundet underlag till resultatrapport`.

## R2: Bygg huvudrapport och bilagor; obligatorisk PDF-kontrollpunkt

**Files:** Create `src/riskanalys/dokument/{resultatrapport_v9,arb_v9,rapportvyer_v9}.py`, `docs/research/verktyg/resultatrapport_offline.py`, `tester/enhet/{test_resultatrapport_v9,test_rapportvyer_v9,test_resultatrapport_offline}.py`. Modify `src/riskanalys/dokument/modeller.py` endast för versionsmedvetna V9-avsnitt, leveransdelar och serialisering. V8:s validerings- och byteutfall förblir oförändrade.

**Interfaces:**

- V9-delar är exakt `resultatrapport`, `analysbilaga`, `underlagsbilaga`; V8 tillåter fortsatt endast sina två delar. V9-dokument har enhetligt V9-format och unika avsnitts-ID; blandade format avvisas.
- `bygg_resultatavsnitt(rb, profil, bedomning, resultat, historik, *, analys, underlag: ResultatunderlagV9) -> tuple[Avsnitt,...]` bygger R1–R7 enligt designens disposition och ID-kontrakt.
- `TransformationV9(pointer: str, fore: str, efter: str, orsak: Literal['format','leveransdel','visningsnummer','tredelsforklaring'])` och `ResultatbyggeV9(dokument: Dokument, analysdokument: Dokument, underlag: ResultatunderlagV9, transformationer: tuple[TransformationV9,...])` definieras i `resultatmodell_v9.py`. Inga extra transformationsfält eller fria transformationsorsaker.
- `bygg_resultatpaket_v9(rb, profil, bedomning, resultat, historik, *, analys, gransindex=None, modellrapport=None) -> ResultatbyggeV9` bygger full V8-källa via befintlig byggare och därefter nya R-avsnitt och metadataomlagda A/B1-avsnitt.
- `RapportvyerV9(resultatrapport: Dokument, analysbilaga: Dokument, underlagsbilaga: Dokument)` och `bygg_rapportvyer_v9(dokument: Dokument) -> RapportvyerV9` definieras i `rapportvyer_v9.py`; `vystruktur_v9(dokument: Dokument) -> dict` har versionsnamnet `D-ARB-v9-tre-delar-1` och explicit avsnittsordning för alla tre delar.
- Offlineverktyget körs som `.venv312/bin/python docs/research/verktyg/resultatrapport_offline.py --ut /private/tmp/riskanalys-resultatrapport-offline-NYTT_ID`. Det bygger båda referensfallen i `direkt2`, sparar fryst byggunderlag/kontrollsummor, `resultatrapport.docx` och `matning.json` per fall samt förbereder PDF-konvertering med Word/LibreOffice. R-ordning, allt R-innehåll, hänvisningar och typografi enligt designen måste finnas med; ingen manuell efterredigering av rapporttext. PDF och renderarversion läggs till innan kontrollpunkten får passeras. Verktyget skapar inga giltiga exportmanifest, attester eller fastställda paket.

- [x] Skriv `test_r4_matris_visar_gemensam_kedja_en_gang_for_fyra_tjanster`, `test_r4_och_r5_tillsammans_tacker_varje_tjansts_hela_kedja`, `test_r5_visar_egna_scenarier_och_avvikande_kontrollutfall`, `test_hela_pt_tf_motiveringen_stannar_i_r5_men_exponering_hanvisas_till_a` och `test_flera_scenarier_som_var_for_sig_avgor_nivan_forklaras`. Kontrollera faktiska före-/eftervärden, sannolikhet/konsekvens, medlems-ID, radreferenser och exakt en återgivning av gemensam förklaring. En låg kvarstående nivå i en tjänst får inte kopieras till andra.
- [x] Skriv `test_r2_har_exakta_pt_och_tf_varden_utan_pahittad_tf_reduktion`, `test_atgardsmedlemmar_bevarar_status_och_ej_beslutad_prioritet` och `test_lang_motivering_aterges_hel_utan_nytt_sammanfattningsfalt`. Assert hela lokala PT-/TF-originalmotiveringen, rätt led och kontrollstatus; exponeringstexten ska finnas hel i A med giltig hänvisning från R5.
- [x] Skriv `test_fler_an_fyra_tjanster_delar_matrisen_utan_att_tappa_celler`: högst fyra tjänstekolumner, återkommande scenario-ID och exakt varje tjänstemedlem en gång, utan minskad textstorlek.
- [x] Skriv `test_v9_tre_vyer_utgor_hela_dokumentet`, `test_v8_sakfalt_bevaras_med_uttommande_metadataundantag`, `test_referenser_och_literala_spann_bevaras` och `test_gamla_format_och_blandade_vyer_avvisas`. Koppla varje R-stycke/tabellcell till minst en giltig källa eller en fast, versionsbunden programmall.
- [x] Kör RED på de två produktprovsfilerna. Implementera rena byggare. R4 visar matrisen och delade kedjor, R5 hänvisar till sina celler och visar lokala tillägg samt hela PT-/TF-motiveringarna. R2 länkar till R4/R5 i stället för att dubblera skälen. Återanvänd inte fri text under ny proveniens. Saknat led ger `[VERIFIERA]` och en specifik presentationsbrist.
- [x] Transformationslistan får bara byta exakt kända V8-programformuleringar om två delar till V9:s tre delar. Matcha källpointer och förväntad originaltext. Förändrad lokal text, belägg eller annan programtext ska falla i jämförelsen. Bevara B2 sist i A och all B1-saktext.
- [x] Skriv och kör RED/GREEN för `test_offline_bygger_bada_fallen_utan_export_faststallelse_eller_ai`, `test_offline_aterger_samtliga_r_stycken_och_matrisvarden` och `test_offline_sparar_kallsummor_och_markerar_forhandsvisning`. Återanvänd rena Word-primitivelement och V8:s läsbara stil som tillgängliga byggdelar utan att anropa produktens V9-renderings-/exportkedja. Matcha alla synliga saktexter/celler mot R-dokumentet.
- [x] Kör GREEN och befintliga `test_dokumentmodeller.py`, `test_rapportvyer.py`, `test_arb_v8.py`. Kör offlineverktyget, konvertera båda faktiska huvudrapporterna till PDF med Word/LibreOffice och registrera renderare/version och sidantal. Kontrollera varje sida och matrisens läsbarhet. Om PDF saknas eller målet inte nås: redovisa bristen; flytta inte kontrollpunkten till R3/R7 och kapa ingen text.
- [x] Kör snabbprofil och commit: `feat: bygg resultatrapport med fullständiga analysbilagor`. Standardleveransen är fortfarande V8.
- [x] **Stanna alltid här före R3.** Lämna båda PDF-filerna, sid-/ordmätning, spårtäckning, aktuellt commit och PDF-/underlagssummor till användaren för läsning och Claude-granskning. Dokumentera uttryckligt klartecken till dessa versioner i körloggen. Gröna tester, uteblivet svar eller enbart godkänd plan passerar inte kontrollpunkten. Detta är en förhandsgranskning av en isolerad mellanversion, inte produktleverans; full slutgrind kvarstår i R7.

## R3: Fryst presentation, hänvisningar och Word-rendering

**Förutsättning:** R2:s två PDF-förhandsvisningar har fått användarens uttryckliga klartecken. R3–R7 får inte starta tidigare. Kontrollpunkten är passerad 2026-10-23; användarens aktuella uppdrag omfattar R3.

**Files:** Create `src/riskanalys/dokument/{presentation_v9,leverans_v9,rendering_v9}.py`, `tester/enhet/test_rendering_v9.py`. Modify `dokument/{rendering,wordstil}.py` bara där befintliga rena primitivelement behöver stödja V9; behåll V8-grenarnas policy. Extend `test_rendering_v8.py` om en delad hjälpfunktion ändras.

**Interfaces:**

- `LeveransV9` i `leverans_v9.py` har strikt format `D-ARB-v9-leverans-1`, `datum: date`, `bedomning: str`, `granskning: str`, `version: int|None`, `organ: str|None`; beslut kräver version och organ tillsammans. `filnamn -> tuple[str,str,str]` följer designens tre namn.
- `PresentationV9` i `presentation_v9.py` binder fulla källsummor, V9-dokument, urval/transformationer, exakt renderade listor, vystruktur och den fasta tredelsmallen. Ingen V8-presentation märks om.
- `bygg_presentation_v9(bygge: ResultatbyggeV9, *, analys, fynd, bedomning, profil) -> PresentationV9` byggs först när den slutliga fyndlistan finns.
- `rendera_rapportvyer_v9(vyer: RapportvyerV9, profil, mapp: Path, *, presentation: PresentationV9, leverans: LeveransV9) -> tuple[Path,Path,Path]` återger enbart den granskade presentationen och fasta leveransvärden.

- [x] Skriv `test_tre_filer_visar_samma_identitet_och_samtliga_andra_delar`, `test_word_saktext_matchar_presentationskallan`, `test_hanvisning_till_annan_fil_ar_lasbar_utan_bokmarke` och `test_status_utkast_blir_inte_faststalld_i_r1`. Parse faktisk DOCX/XML; kontrollera originalspann och ingen rollplatshållarsubstitution inne i literal fri text.
- [x] Skriv `test_a4_och_minsta_textstorlek`, `test_hela_atgards_och_fyndkallan_finns_i_b1` och `test_andrad_presentationsmall_kraver_ny_granskning`. Tabeller ska kunna gå över sidor med återkommande rubrik, inte klippas eller krympas.
- [x] Kör RED, implementera V9-renderingen och versionsstyrda hänvisningar. Frys fulla åtgärds-/fyndposter i B1. Låt huvudrapportens maskinfyndlista vara separat från analysgap så att ingen återbyggnadscykel uppstår.
- [x] Kör GREEN, berörda V8-renderingsprov och snabbprofil. Rendera de två huvudrapporterna med tillgänglig Word/LibreOffice-miljö och kontrollera alla sidor. Registrera verktyg/version och faktiska sidantal; DOCX har inte tillförlitligt sidantal utan rendering. Jämför saktext, urval och matrisvärden med R2:s godkända förhandsvisningar. Redaktionella innehållsändringar lämnas för förnyad läsning; R2:s klartecken är inte en attest av ännu osedd produktlayout.
- [x] Justera endast layout/disposition/gruppering inom designens innehållsregler. Commit: `feat: rendera tre bundna rapportdelar i V9`.

## R4: Återbyggnad, kravkarta och oförändrade sakgrindar

**Komplettering från R3-granskningen:** byt också den exakt kända programmeningen i B1:s ”Råa lokala svar” genom tredelstransformationen. Sök i synlig programtext efter gamla tvådelsformuleringar; lokala original och AI-text får aldrig skrivas om. Källbilagan får visningsnummer A15.

**Files:** Create `src/riskanalys/granskning/dokument_v9.py`, `tester/enhet/test_granskning_v9.py`. Modify `dokument/arb.py`, `granskning/{korning,kontroller}.py`, `kommandon/granska_kommando.py`. Reuse `granskning/{dokument_v8,lasta_v8}.py` på den fullständiga V8-källan, inte på en ommärkt V9-delvy.

**Interfaces:**

- Utöka `kor_granskning` och `_kor_granskning_last` med keyword-only `rapportformat: Literal['v8','v9']|None = None`. `None` följer den enda `rapportversion.AKTUELL_DOKUMENTVERSION`; historiska läsvägar följer sparat format. `bygg_arb(..., formatversion=V9)` returnerar `bygg_resultatpaket_v9(...).dokument`; V9-granskningen använder byggresultatet även för spårkällorna. V8-skrivresultat får inte få företräde framför ett uttryckligt V9-val eller den nya rapportstandarden.
- CLI `riskanalys granska BYRA --rapportformat v8|v9` gör ett uttryckligt presentationsval utan omskrivning/ny bedömning. Saknas kompatibla V8-skrivresultat visas begripligt fel; det är inte tillstånd att anropa AI automatiskt.
- `resultatfynd_v9(rb, profil, bedomning, resultat, historik, *, analys, bygge: ResultatbyggeV9, dokument: Dokument, modellrapport=None, analysbrister_filer=(), granskningsdatum=None) -> list[dict]` ger fynd i befintligt fyndformat.
- Spara `analysdokument-v8.json`, `resultatunderlag-v9.json` och `transformationer-v9.json` i granskningen tillsammans med befintligt `dokument.json`, fryst analys/historik och `presentation.json`. Alla ingår i manifestet. Täckningskartan för R→A/B1 följer underlagets frysta referenser och befintliga krav-ID.

- [x] Skriv `test_v9_granskas_med_v8_skrivresultat`, `test_v7_skrivresultat_far_inte_markas_om`, `test_utelamnat_tf_eller_egen_sarbarhet_ger_fynd`, `test_niva_eller_atgardsstatus_som_avviker_ger_fynd`, `test_matris_med_borttappad_tjanstemedlem_ger_fynd` och `test_trasig_eller_fel_typad_pointer_ger_fynd`. Kontrollera konkret regel/avsnitt och blockerande allvar; gruppens rubrik får inte ersätta medlemskontroll.
- [x] Skriv `test_kravkartans_gallande_element_har_r_sammanfattning_och_analysplats`, `test_b09_b10_b15_provas_i_analysen_och_sammanfattas`, `test_obelagd_reduktion_och_otackt_tf_sparrar_som_forut` och `test_fyndlistan_skapar_inte_rekursiv_rapport`. Ett närvarande avsnitts-ID är inte tillräckligt kravbevis.
- [x] Kör RED. Bygg V8-källa och V9 en gång per granskning, kör befintliga sakgrindar på källan och nya presentationskontroller på V9. Frys presentation sist. V9-grenen får inte falla igenom till äldre `_b12`-/analyskontroller med andra kontrakt.
- [x] Kontrollera modellen för kravtäckning och spårbarhet i `kontroller.py`: behåll D-ARB.1–.11 i A, validera nya R-ID separat och undvik dubbla motstridiga fynd för samma källbrist. Regelbasfiler ändras inte.
- [x] Kör GREEN och berörda gransknings-/CLI-/modellbindningsprov, inklusive att riskmodellidentiteten är oförändrad för samma riskkod/regler. Om identiteten ändras av en layoutimport ska orsaken granskas; ingen tyst omdefinition eller förfalskad gammal summa.
- [x] Lägg riktade V9-granskningsprov i analysprofilen, kör snabb- och analysprofil. Commit: `feat: granska resultatrapport mot full analys och kravkarta`.

## R5: Export, samlad sakgranskning och fastställelse

**Komplettering från R3-granskningen:** CLI:s tvådelsformulering i `sakgranska_kommando.py` ersätts versionsriktigt för V9. Utkastets inledning får inte påstå att ett fastställt verifierbart manifest redan finns. Den publika renderaren ska avvisa slutstatus från vanliga anrop även när version/organ anges; endast den prövade fastställelsekedjan får ge slutrendering, med ett reproducerande prov.

**Files:** Create `src/riskanalys/dokument/rapportpaket_v9.py`, `src/riskanalys/faststallelse/resultatgranskning.py`, `tester/enhet/{test_rapportpaket_v9,test_resultatgranskning_v9}.py`, `tester/typfall/test_resultatrapport_hela_kedjan.py`. Modify `dokument/export.py`, `faststallelse/{sakgranskning,grindar,faststall}.py`, `lagring/manifest.py`, `kommandon/sakgranska_kommando.py`. Läs även `faststallelse/modeller.py`; använd dess befintliga avsnittsposter utan att ändra äldre serialisering.

**Interfaces:**

- `las_presentation_v9(granskningsmapp: Path, bedomning, profil, *, aktuell: bool = True, regelbas=None) -> PresentationV9` kontrollerar alla frysta källor och aktuell policy vid ny export. Historisk läsning kräver inga aktuella mallar.
- `verifiera_rapportpaket_v9(mapp: Path, manifest) -> list[str]` kräver tre namngivna filer samt frysta V9-källor. Dispatch från manifestverifieringen använder fryst dokumentformat; trasig/saknad dokumentkälla med V9-leveransmetadata får inte falla tillbaka till ingen kontroll.
- `exportera_v9_last(byramapp: Path, datum: date, granskningsmapp: Path, *, regelbas=None) -> Path` implementeras i `dokument/export.py`. Samma låsordning och källa→rendering→omkontroll→atomisk publicering som V8, nu för tre filer.
- `registrera_resultatgranskning(sakgranskningar: tuple[Sakgranskning,...], dokument: Dokument, profil: Profil, *, presentation: PresentationV9, visad_struktursumma: str, analysbindning: str, godkand: bool, roll: str, namn: str, datum: date, kommentar: str|None = None) -> tuple[Sakgranskning,...]` registrerar exakt alla R-avsnitt som en atomisk kandidat. Falsk/inaktuell summa ger ingen ny post.
- CLI `sakgranska BYRA --resultatrapport` är ett alternativ till befintligt `--avsnitt`, med samma person-/roll-/godkännandekrav och explicit `--visad-struktursumma`. Visa summa, alla R-avsnitt och faktisk presentation innan granskningshandlingen; inget dolt godkännande av A/B1.

- [x] Skriv `test_andrad_analys_efter_visning_sparar_inga_r_attester`, `test_samlad_r_granskning_omfattar_exakt_alla_r_avsnitt`, `test_r_granskning_godkanner_inte_a_b1` och `test_v8_attester_galler_inte_for_v9_struktur`. Samma paketbindning ska göra poster inaktuella när text, källa, urval eller presentation ändras.
- [x] Skriv `test_fel_vid_tredje_filen_publicerar_ingenting`, `test_saknad_analysbilaga_ger_ofullstandigt_paket`, `test_felaktig_yttre_versionshint_kringgar_inte_verifiering` och `test_andrad_fryst_kalla_ger_avslag`. Misslyckad ny export får inte göra ett tidigare giltigt paket oanvändbart.
- [x] Skriv historiskt prov `test_v8_verifieras_utan_aktuell_regelbas_eller_omrendering` med spärrade renderingsanrop, jämför ursprungliga bytes/attestsummor och `test_v9_aterskapas_fran_frysta_kallor_pa_tom_datamapp`. Fastställbara prov använder signerad syntetisk regelbaskopia, aldrig ändrad sakkunnigstatus i repot.
- [x] Skriv `test_formathinder_provar_sparat_format_och_inte_ny_standard`: giltig V8 prövas som V8 även med V9 som nybyggnadsstandard, giltig V9 som V9, blandade/ommärkta avsnitt avvisas och äldre format behåller tidigare policy. Ändra `formathinder` till denna versionsriktiga prövning och kontrollera den frysta dokumentkällan; ett godtyckligt yttre versionsfält får inte välja en lättare grind.
- [x] Lägg de fullständiga typfallen `test_befintligt_v8_utkast_kan_faststallas_efter_v9_standardbyte` och `test_v9_paket_med_v8_skrivresultat_kan_faststallas_efter_standardbyte` i `test_resultatrapport_hela_kedjan.py`. Pröva faktisk fastställelse och verifiering, inte bara tom fellista från `formathinder`. V9-avsnittens presentationsformat är V9; deras frysta skrivresultat är V8. Blandade presentationsformat tillåts inte.
- [x] Kör RED och implementera V9:s paketstöd och sakgranskningsbindning. Alla A/B1-avsnitt har fortfarande ordinarie krav på aktuell sakgranskning. Export av märkt utkast får ske med öppna fynd; fastställelse får det inte när de ordinarie/V9-grindarna spärrar.
- [x] Märk det nya typfallsprovet `fullkedja`. Låt det köra granska→export→granskningsavslag/godkännande→fastställ→verifiera på samma syntetiska kedja, inte skapa en dyr ny kedja för varje negativt exempel. Bevara tidigare tester; nya rena manipulationer görs på isolerade kopior.
- [x] Kör GREEN, berörda export-/manifest-/fastställelseprov, snabbprofil och analysprofil. Commit: `feat: fastställ resultatrapport och bilagor som ett paket`.

## R6: Användarflöde och uppdatering utan nya AI-anrop

**Files:** Modify `src/riskanalys/intag/{dokument,vyer,webb}.py`, `tester/intag/test_rapportflode_v8.py`. Create `tester/intag/test_resultatrapport_v9.py`. Extend CLI-proven där R4/R5:s nya flaggor används; inga nya riskfrågor eller val per faktor.

**Interfaces:** Behåll befintliga `word` och `underlag` för R respektive B1. Lägg en explicit route `analysbilaga` för A. Hämta filnamn från V9:s leveransmodell och validerat exportmanifest, inte godtyckligt filnamn från URL. Alla tre använder `las_utkast` och samma skyddade aktualitets-/integritetskontroll.

`uppdatera_export` får keyword-only `rapportformat: Literal['v8','v9']|None = None`; `None` bevarar tidigare exportformat vid en vanlig uppdatering. Ett uttryckligt formatbyte till V9 bygger separat granskning/export med oförändrade V8-skrivresultat. Standard för helt nya utkast ändras först i R7.

- [x] Skriv `test_tre_tydligt_namngivna_nedladdningar`, `test_analysbilaga_far_samma_aktualitetskontroll_som_resultatrapport`, `test_uppdatera_v8_till_v9_anropar_inte_ai_och_bevarar_original` och `test_v8_uppdatering_byter_inte_format_tyst`.
- [x] Skriv `test_formatbyte_visar_behov_av_fornyad_sakgranskning`, `test_ogiltig_revision_eller_fel_route_ger_ingen_export` och `test_inga_nya_sammanfattnings_eller_sarbarhetsfragor`. Testa faktisk serverhanterare med befintligt CSRF/origin-skydd och isolerade syntetiska data.
- [x] Kör RED. Visa tre knappar med resultatrapportens roll och att alla tre delarna hör ihop. Formatversionens teknik behöver inte visas som ett nytt val i byråns normala frågeflöde. För äldre utkast finns en uttrycklig handling att skapa den nya resultatrapporten utan nya AI-anrop, med information om förnyad sakgranskning.
- [x] Kör GREEN och befintliga skyddad-begäran-/nedladdningsprov samt snabb-/analysprofil. Öppna ett syntetiskt utkast och kontrollera de tre hämtade filerna och en inaktuell länk. Commit: `feat: visa resultatrapport och bilagor i byråflödet`.

## R7: Mät, slutverifiera och byt standard först när kedjan är komplett

**Files:** Modify `docs/research/verktyg/rapportmatning.py`, `src/riskanalys/dokument/rapportversion.py`, `tester/testprofiler.json`, `docs/{STATUS,kravstod,testning}.md`, påbörjad slutprovslogg. Create `tester/enhet/test_rapportmatning_v9.py`. Extend R5:s hela-kedjan-prov för standardval och bakåtkompatibilitet. Båda design-/plandokumenten uppdateras med faktiskt utfall utan att historiska mål skrivs om.

**Interfaces:** Lägg `--rapportformat v8|v9` till rapportmätningen, med standard `v8` för kompatibla tidigare mätkommandon. Behåll alla befintliga `--analyslage` och `--analys-schema`-kontrakt. Redovisa format, analysläge, oförändrade källsummor, ord/upprepning per R/A/B1 samt total. Sidor kommer från faktiska exportfiler och identifierad renderare; summera inte ett uppskattat sidantal.

- [ ] Skriv `test_matning_valjer_format_utan_att_byta_analyslage`, `test_matning_redovisar_tre_delar_och_total`, `test_langtext_och_fler_tjanster_far_varning_utan_trunkering` och `test_nya_granskningar_valjer_v9_men_historiska_paket_bevaras`. Kör RED före ändrad standard.
- [ ] Skriv `test_tomt_utkast_med_v9_standard_byggs_som_v9_och_aldrig_v6` med `bygg_arb(..., utkast={})`, V9 som standard och en V6-byggare som omedelbart fallerar om den anropas. Kontrollera V9-format och synligt ofullständigt underlag. Kör även R5:s båda verkliga fastställelseprov med V9 som standard. Dessa tre prov är obligatoriska före standardbytet.
- [ ] Implementera mätstödet. Kör de två fallen med samma profil-, motor-, skrivsvars-, regelbas- och historikunderlag i V8/V9, primärt `direkt2`. Kör schema 1 och `overforing2` som kompatibilitetsprov med bevarade original/attributioner, inte som alternativ före-bas.
- [ ] Exportera samtliga sex faktiska Word-filer (två fall × tre delar). Rendera hela resultatrapporten i båda fallen, kontrollera varje sida och spara PDF/PNG med renderarversion. Word eller LibreOffice fungerar; ett Codex-specifikt verktyg får inte vara enda accepterade metod. Rendera även A/B1 till PDF och granska sidlayouten genom hela bilagorna enligt användarens komplettering. Registrera exakt vilken visuell kontroll som har gjorts; text-/XML-kontroll ensam räcker inte.
- [ ] Verifiera K01–K13 och K15 med en tabell som länkar varje krav till test/logg/export och användarens dokumenterade klartecken efter R2. Högst åtta resultatsidor per referensfall måste nås utan informationsförlust eller för liten text. Om inte: lämna det som öppen acceptans och aktivera inte V9 som standard i denna leverans.
- [ ] När K01–K13 och K15 är uppfyllda, sätt `rapportversion.AKTUELL_DOKUMENTVERSION = V9`. Kontrollera att `AKTUELL_SKRIVVERSION` är oförändrad V8 och att `bygg_arb` inte väljer V8 bara för att skrivresultaten är V8. Kör `rg` över `src`/`tester` för att verifiera att den gamla konstantdefinitionen, dess importer/monkeypatcher och det tidigare parallella konstantförslaget är borta. Kör GREEN, snabb-/analysprofil och det berörda hela-kedjan-provet; fixa orsaker före slutgrinden.
- [ ] Frys kod/test/regler/profiler/verktyg. Kör `.venv312/bin/python scripts/testa.py full --ut /private/tmp/riskanalys-resultatrapport-full-NYTT_ID`, `.venv312/bin/riskanalys regelbas validera` och `git diff --check`. Kontrollera collection↔JUnit, exitkod, faktisk tid och oförändrat snapshot. Kod-/test-/verktygsrättning kräver ny färsk fullsvit; enbart slutdokumentation/commit-ID kräver inte omkörning.
- [ ] Redovisa före/efter för huvudrapport, A, B1 och total, urvalets täckning, faktisk arbetsbörda/sakgranskning, exakt testurval, kvarstående begränsningar och alla versions-/hashbindningar. Flyttad analys är inte borttagen text, och en längre total är inte en total förkortning.
- [ ] Commit: `feat: leverera verifierad resultatrapport som rapportstandard`. Kontrollera efter commit att källsnapshotet fortfarande matchar fullsviten. Lämna dokument och leveransbevis för användarens Claude-granskning; ingen push/merge på eget initiativ.

## Täckning och självkontroll

| Designkrav | Genomförande och bevis |
|---|---|
| K01, engångssvar/AI-gräns | R1–R2 oförändrade källor, R6 ingen ny frågeomgång/anrop, R7 hashjämförelse. |
| K02, tre delar/atomiskt paket | R3 rendering, R5 export/manifest/fastställelse, R6 alla nedladdningar. |
| K03–K05, riskkedja/urval/sakvärden | R1 typat urval och matris med exakt medlemskap, R2 delade kedjor/lokala skillnader, R4 negativa manipulationer, R7 falljämförelse. |
| K06–K07, bevarande/spår/krav | R2 transformationsprov, R3 hänvisningar, R4 kravkarta och återbyggnad. |
| K08–K10, granskning/grindar/historik | R4 gamla sakgrindar, R5 attest-/paketprov, R6 aktualitet, R7 historisk standardseparation. |
| K11–K13, längd/läsbarhet/mätning | R2 tidig genomförbarhet, R3 faktisk rendering, R7 fullsidig huvudrapportkontroll och ärlig total. |
| K14, verifiering | Varje arbetscommit riktad GREEN + snabbprofil; analys vid kedjeändringar; R7 en full slutgrind enligt AGENTS. |
| K15, obligatorisk PDF-granskning | R2 offlineverktyg, två fullständiga PDF-filer och uttryckligt användarklartecken före R3–R7; återkontroll av produktlayout i R3/R7. |

Varje Review Focus-rad har ett uttryckligt negativt/positivt prov i ägaruppgiften. Nya gränssnitt är förslag i denna plan och ska granskas som sådana; de påstås inte redan finnas i koden. Uppgifterna använder samma namn och versioner genom hela kedjan. PDF-kontrollpunkten efter R2 är ovillkorlig och standardbytet ligger efter komplett produktkedja. Konstantflytten omfattar alla importer, historiska fallback och standardvalsprov i samma steg. Förnyad sakgranskning vid formatbyte är en uttrycklig arbetskostnad, inte en automatisk överföring av tidigare attester. Genomförandemetoden föreslås vara implementation i denna chatt med användarens Claude-granskning; inget arbete startar av att planen skrivits.

### Ändringar i revision 2

R1–R2 har fått typer och negativa prov för delning mellan tjänster, varierande kontrollutfall och komplett matristäckning. R5:s långexponering hänvisas till A medan hela PT-/TF-motiveringen stannar i huvudrapporten. Den gamla dokumentversionskonstanten flyttas i stället för att dubbleras. R2 omfattar ett separat offlineverktyg och ett ovillkorligt användarstopp med två PDF-förhandsvisningar före R3–R7. Omfattningen är fortsatt omkring 15 nya produktmoduler plus granskningsverktyget; ingen implementation ingår i denna dokumentrevision.

## Status efter R3 2026-10-23

R2-kontrollpunkten är passerad genom användarens uttryckliga ”gå vidare med r3” efter Claude-granskningen av `35b5be0`. Godkända PDF-summor: `74c98f3f959d13d9dec6cf5cf66a5047e6177b7b2a17fe07b359bf6c1aeb820f` och `e0e7c9f81c1d42564e800d7d1f6f752b782bf25c56ae4df543d7f906c7d30a0f`.

R3 är implementerad: strikt fryst presentation, leveransmall, tre Word-filer, verkliga filhänvisningar och fulla åtgärds-/fyndkällor. Användarens fyra R3-förfiningar är gjorda. En lokal icke nivåavgörande scenariovariant omfattas också av urvalet så att hänvisningen ”Egen mekanism” alltid har sitt innehåll i R5. Ingen risknivå eller vikt ändras.

Båda huvudrapporterna har renderats till PDF med LibreOfficeDev och alla **7 respektive 8 sidor** är visuellt kontrollerade. **78 riktade prov**, inklusive V8-renderingen, samt **140 prov i snabbprofilen** passerar med oförändrat källsnapshot. Ingen färsk fullsvit; R3 är ett arbetssteg för granskning, ingen produktleverans. R4–R7 återstår och V8 är fortsatt standard. [Granskningsunderlag, filer och kontrollsummor](../reviews/2026-10-23-resultatrapport-r3.md).
