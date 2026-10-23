# Resultatrapport R0–R2 för PDF-granskning

**Ersatt efter Claude-granskningen:** se [rättningen och de nya förhandsvisningarna](2026-10-23-svar-claude-resultatrapport-r2.md). Nedanstående mätvärden och PDF-filer beskriver den tidigare versionen på `f653eea`.

**Status 2026-10-23:** offlineimplementationen för R0–R2 är utförd. Användarens uttryckliga PDF-klartecken återstår. R3–R7 har inte påbörjats. Rapportstandarden och AI-skrivformatet är fortfarande V8. Ingen push eller merge.

Planeringsbas: `f1351b8`, produktbas `4a878b9`. R1 är arbetscommit `061a0c9`. R2:s arbetscommit framgår av Git-historiken efter denna rapport. [Design](../specs/2026-10-22-resultatrapport-design.md) och [plan](../plans/2026-10-22-resultatrapport-plan.md) gäller med användarens två standardbytesprov och regeln om högst fyra tjänstekolumner.

## Läs dessa två förhandsvisningar

- [Fyra tjänster, sex sidor](../../../.superpowers/evidens/2026-10-23-resultatrapport-r2/fyra_tjanster/rendering/resultatrapport.pdf).
- [Med betalningsmandat, sex sidor](../../../.superpowers/evidens/2026-10-23-resultatrapport-r2/med_betalningsmandat/rendering/resultatrapport.pdf).

Filerna är lokala syntetiska granskningsunderlag, inte fastställda byråpaket. `.superpowers` är ignorerad av Git. Det krävs ingen ny frågeomgång eller riktiga AI-anrop för att skapa resultatrapporten. Befintliga provsvar kommer från Testleverantor.

Gemensamma avgörande scenarier visas en gång i R4, med skilda tjänsteceller och rätt före-/eftervärden. R5 behåller hela PT-/TF-motiveringarna och tjänstens egna händelseförlopp. Exponeringstexten ligger kvar i analysbilagan. Samma hot eller nivå räcker inte för att slå ihop olika mekanismer. Egna TF-sårbarheter, antaganden, lokala skillnader och okända/ej relevanta celler har särskilda prov.

## Faktisk mätning

Samma ordkontrakt för V8 och V9 nedan: dokumentets titel, samtliga stycken och dataceller. Rubriker, tabellkolumnnamn och leveransdekor mäts inte som saktext. PDF-sidantalet är däremot från verklig rendering av hela Word-filen, inklusive rubriker och tabellhuvuden.

| Fall | V9 resultat | V9 analys A | V9 underlag B1 | V9 totalt | V8 totalt, samma underlag/ordkontrakt | PDF resultat |
|---|---:|---:|---:|---:|---:|---:|
| Fyra tjänster | 2 480 | 13 728 | 35 794 | 52 002 | 49 503 | 6 sidor |
| Med betalningsmandat | 2 128 | 13 405 | 35 939 | 51 472 | 49 325 | 6 sidor |

Huvudrapporten är kortare att läsa. Hela dokumentationen blir längre eftersom resultatrapporten tillkommer; ingen total förkortning hävdas. All kanonisk V8-saktext, originalreferenser och skyddsspann bevaras i V9:s A/B1. Enbart explicit listad format-/del-/numrering och exakt känd programförklaring om två/tre delar får ändras.

R0:s befintliga `rapportmatning.py` gav 13 712/13 389 läsord och 35 782/35 927 B1-ord innan titel/dekor och andra presentationsinslag. Tidigare redovisade 14 126/13 803 och 36 005/36 150 är historiska mätvärden med ett annat kontrakt. Enkel whitespace-räkning av de tidigare DOCX-filerna ger i sin tur 14 900/14 585 och 36 346/36 499. Dessa mått blandas inte i jämförelsen ovan. R0-loggar och kontrollsummor för de äldre exporterna är bevarade i planens arbetskatalog.

## Verifiering och gränser

- R1: 17 nya prov först röda, sedan 17 gröna. Berörda V8-/skrivformats-/formatgrinds-/riktningsprov: 195 godkända på 64,50 s. Snabbprofil: 136 godkända på 46,194 s, exakt collection/JUnit och oförändrat snapshot.
- Slutligt riktat R2-urval inklusive R1, nya rapport-/vy-/offlineprov och äldre dokument-/V8-/skrivformatsprov: **238 godkända på 83,88 s**.
- R2:s snabbprofil: **137 godkända på 49,167 s**, exakt collection/JUnit, exit 0, inga fel eller överhoppningar och oförändrat snapshot om **796 resurser**. Endast ett nytt rent kolumndelningsprov läggs till snabbprofilen; de tyngre rapportproven körs riktat.
- Extra RED/GREEN-fynd rättade inom R2: egen TF-post saknade synlig dimension/hot, eget scenario saknade händelseförlopp, okända/ej relevanta celler fick fel etikett, flera-scenarier-texten var ovillkorlig och tredelsundantaget var för brett för AI-text. Ett geometritest justerades till 0,1 mm tolerans för Word-formatets hela twips.
- Alla **112 konstruktionsposter per fall** har kontrollerade källpointers. Matrisen bevarar exakt **44 avgörande medlemsled per fall**. Den faktiskt presenterade R-rapporten kan återbyggas identiskt från frysta källor och urval.
- Fullt nytt V8-återbygge från enbart rå JSON-profil gav extra skyddsspann för datum som bytt Python-typ från datum till sträng; saktexten skiljde inte. V9 bevarar därför den fulla frysta V8-källan och dess ursprungliga spann. R2:s reproduktionsbevis gäller R-rapporten från denna frysta källa, inte ett påstående om byteidentisk nyproduktion av V8 från typförlorande JSON. Befintligt versionsriktigt profil-/källkontrakt ska följas i R4–R5.
- Regelbas och riskmodellfiler är oförändrade. Inga nya poäng, trösklar, sakkunnigstatusar, analysbeslut eller sakattester skapas.
- **Ingen färsk fullsvit körd för R2.** Detta är den avtalade förhandsgranskningen före produktintegration. Full slutgrind kvarstår till R7; nuvarande kod är inte levererad för verklig byråanvändning.

Råloggar: `.superpowers/sdd/2026-10-22-resultatrapport-plan/`. Snabbkvitton: `/private/tmp/riskanalys-resultat-r1-snabb-20261023/` respektive `/private/tmp/riskanalys-resultat-r2-snabb-20261023/`.

## PDF-kontroll och frysta versioner

Renderare: **LibreOfficeDev 26.8.0.0.alpha0**, build `2c87e51eeaa2b413ff4ae097b2705eea1995d8e5`, via den tillgängliga dokumentrenderaren. A4, brödtext 11 punkter, tabeller 9,5 punkter. Alla tolv sidor har visats och kontrollerats visuellt: inga observerade klipp, överlapp eller oläsliga tabellceller. Vanliga löptextbrytningar över sidor finns kvar. Detta är teknisk layoutkontroll av förhandsvisningarna, inte användarens läsbarhetsgodkännande eller en juridisk sakgranskning.

| Fall | PDF SHA-256 |
|---|---|
| Fyra tjänster | `690d1eb20b3e55bca7f0734990a1be866831ef1a349119d3b7afbff29ed67e3a` |
| Betalningsmandat | `5808de8c4af27edb36851f4332ade410cd75e11901f41ac23e17fe5d8b2b97e1` |

`bygge.json`, `kallor.json`, `matning.json`, DOCX, PDF, sidbilder och `kontroll.json` ligger under `.superpowers/evidens/2026-10-23-resultatrapport-r2/`. Datum-/typbegränsningen och ordkontrakten ovan får inte tappas bort vid fortsatt granskning.

## Tilläggen inför standardbytet

Provet `test_tomt_utkast_med_v9_standard_byggs_som_v9_och_aldrig_v6` är redan implementerat och grönt i R2. Det sätter V9 som standard, lämnar utkasten tomma och låter V6-byggaren fallera om den anropas.

Planen innehåller också de namngivna verkliga fastställelseproven för ett befintligt V8-utkast respektive ett V9-paket byggt av V8-skrivresultat efter standardbytet. De genomförs i R5/R7, när paketstödet finns, och får inte ersättas av bara ett enhetsprov av formatgrinden. Blandade presentationsformat accepteras inte. **R3–R7 återstår**, liksom komplett V9-export, attest-/manifest-/webbstöd, standardbyte och fullsvit.

## Nästa kontrollpunkt

Användaren och Claude ska läsa båda PDF-filerna. Dokumentera uttryckligt klartecken till dessa PDF-/underlagssummor innan R3 startar. Ett godkänt testresultat eller det tidigare plangodkännandet ersätter inte detta klartecken. Filerna är avsiktligt preliminära och visar kvarstående sakluckor från de syntetiska fallen.
