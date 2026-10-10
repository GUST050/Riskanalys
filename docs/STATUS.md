# Status och framsteg

Senast uppdaterad 2026-10-10.

## Läge

**Fas:** M1 klar. Nästa etapp är M2 (regelbas v1 och juridisk granskning).

| Steg | Status |
|---|---|
| Genomgång av källmaterial | Klar |
| Gemensam förståelse av mål och målgrupp | Klar |
| Val av omfattning (alternativ C) | Klar |
| Val av arkitektur (alternativ 2) | Klar |
| Fördjupad research (EU-regelverk, metod, teknik) | Klar |
| Genomgång av två fullständiga tillsynsbeslut från 2026 | Klar 2026-10-09. [Research 09](research/09-tillsynsbeslut-2026.md): vad Länsstyrelsen underkänner, bristmönster B-23–B-29. |
| Bevarat tillsynsmaterial och granskningsfall | Importerat 2026-10-09: 79 originalfoton, OCR och 14 handlingar i lokalt arkiv utanför repot. [Två syntetiska fall](research/typfall/tillsyn-2026.json), 17 förväntade fynd och fem kontrollvarianter. **Facitutkast, ej sakkunniggranskat; produktutvärdering ej körd.** |
| Strukturförslag och spec, revision 1 | Klar, granskad av Codex 2026-10-08. Sex brister påtalades och godtogs. |
| Spec, revision 2 | Klar, granskad av Codex 2026-10-08. Arkitekturens riktning godkänd, åtta ändringar påtalades och godtogs. |
| Spec, revision 3 | Klar, granskad av Codex 2026-10-08. Fem kvarvarande fynd (två höga, två medel, ett lågt) godtogs. |
| Spec, revision 4 | Klar. Ligger till grund för implementeringsplanen. |
| Spec, revision 5 | Klar. Krav har `lydelser` (lista), efter Codex granskning av planen. |
| Spec, revision 6 | Klar. Sakkunnigstatus binds till en kontrollsumma, efter Codex andra granskning av planen. |
| Spec, revision 7 | Tillsynsmaterialet kopplat till intag och regelbas i M2, granskningsprov i M3 före första riktiga byrå, rutinernas genomgång i M5 och utvidgad provtillsyn i M7. |
| Spec, revision 8–9 | Sakkunnigs godkännande binds till refererade lydelser, sakgranskning till texten med insatta namn, tidigare paket verifieras före användning, och ett saknat eller skadat manifest ger ett fel med instruktion om återställning. |
| [Implementeringsplan M0–M1](superpowers/plans/2026-10-08-m0-m1-grund-och-tunn-kedja.md) | Skriven, 22 tasks. Granskad av Codex fyra gånger 2026-10-08–09; alla fynd åtgärdade. Spårning från tillsynsbrist till etapp finns i planen. Planens kod byggd i en tom mapp med [provkörningsverktyget](superpowers/plans/verktyg/README.md) 2026-10-09: 452 passerar. Godkänd av Codex för implementation med syntetiska data. Genomförd 2026-10-10; avvikelser och rättelser står sist i planen. |
| Senaste kodblocksgranskningen | Codex bekräftade 2026-10-09 att 446 tester passerar, att de fyra regressionstesterna för sakkunnigstatus, sakgodkännande och tidigare paket fallerar före rättningen och passerar efter, och att arkivets 173 kontrollsummor stämmer. Två kvarstående punkter: ett skadat manifest gav en krasch i `verifiera` och `faststall`, och Task 22 tog bort facitpunkten ur nästa steg. **Båda rättade i planen 2026-10-09.** Sju nya eller skärpta tester fallerar mot planens tidigare kod och passerar efter. Hela den återskapade sviten: 452 passerar, ett livetest bortvalt. Codex godkände därefter planen för implementation och reproducerade 452 passerande tester och ett bortvalt livetest. |
| Etapp M0 (grund) och M1 (tunn kedja) | Klara 2026-10-10. Typfallet och återställningsprovet passerar. Koden är införd i repot enligt planens 22 tasks, testerna skrivna före koden. Hela sviten: 495 passerar, ett livetest bortvalt, utan `ANTHROPIC_API_KEY` och med testleverantören. Hela kommandokedjan körd för hand med syntetiska uppgifter i en datamapp med mellanslag och å, ä, ö: med en signerad testkopia av regelbasen fastställs och verifieras paketet; med repots regelbas stoppas fastställelsen eftersom kraven och paragrafkartan inte är sakkunniggranskade. Paketet återställt från säkerhetskopia i en tom datamapp och verifierat. M0–M1 är granskat av Codex och versionshanteras på `codex/m0-m1`. |
| Slutgranskning av M0–M1 | Gjord 2026-10-10 av en fristående granskare (Claude Opus). Inga kritiska fynd. Sex viktiga fynd rättade med tester som fallerade före rättningen: risknivåer som saknades eller stod i en annan form i AI-texten, okända rollplatshållare som blev `[VERIFIERA: …]` i ett fastställt dokument, systemfiler från Finder som gjorde paketet ogiltigt, saknade uppgifter i manifest som gav en krasch, profilvärden som inte prövades mot fältregistret och en sökväg med annat skiftläge som kringgick spärren mot byrådata i repot. Tretton mindre punkter förs till M2–M4 (förteckning sist i planen). Codex granskade därefter implementationen samma dag och fann två brister till, båda rättade med tester som fallerade före rättningen: AI:ns öppna frågor kunde följa med till fastställelse utan att hanteras, och en handredigerad profil kunde ha status bekräftad eller ej tillämplig utan källa, datum, bekräftare eller motivering. Regressionstesterna i Task 22 fångar de fel de skrivits för, prövat genom att felen återinförts i en kopia. **Tillsynsfallens 17 fynd är inte prövade av M1:s tester.** |

## Beslut

| Datum | Beslut | Motivering |
|---|---|---|
| 2026-10-08 | Målgrupp: konsultbyråer för egen efterlevnad, sedan andra företag | Största sektorn under Länsstyrelsens tillsyn och flest sanktioner. Referensfall finns. |
| 2026-10-08 | Omfattning C: verksamhetsnivå först, datamodell förberedd för kundnivå | De flesta sanktioner gäller verksamhetsnivån. Kundnivån kräver personuppgifter och integrationer. |
| 2026-10-08 | Arkitektur 2: regelbas och deterministisk motor, AI som skribent | Reproducerbart, spårbart och testbart. Löser problemen i det tidigare AI-utkastet. |
| 2026-10-08 | Python, YAML, pydantic, pytest, Claude via officiell SDK | Läsbart för en byggare med AI-hjälp. Bra stöd för Word och AI. |
| 2026-10-08 | Kärna och CLI först, webbgränssnitt senare | Kärnan är det svåra. Gränssnittet kan läggas ovanpå. |
| 2026-10-08 | Byggs med Claude Code och Codex | Kräver gemensamma regler i `AGENTS.md` och `CLAUDE.md` och många tester |
| 2026-10-08 | En versionerad katalog per ID-typ är facit | Spec och research hade olika ID:n för samma bristmönster |
| 2026-10-08 | Personuppgifter i fas 1 begränsas till definierade kategorier. Inga personuppgifter till AI. | Föreskrifterna kräver namn på funktionsinnehavare och utbildningsdeltagare. |
| 2026-10-08 | Statusflöde utkast → granskat → sakgranskat → fastställt, med grindar | Ett utkast med öppna punkter får inte kunna se fastställt ut |
| 2026-10-08 | Typat villkorsformat i regelbasen, inga fria uttryck | Reglerna ska gå att granska och testa |
| 2026-10-08 | Manifest med kontrollsummor, sparade AI-svar och låsta paket | En äldre bedömning ska kunna återskapas exakt |
| 2026-10-08 | Mänsklig sakgranskning per avsnitt | Giltiga referenser bevisar inte att texten stämmer i sak |
| 2026-10-08 | Byrådata i datamapp utanför repot (`RISKANALYS_DATA`) | `.gitignore` är bara ett extra skydd |
| 2026-10-08 | Första byggetapp blir en tunn kedja genom hela flödet med syntetiska data | Bevisar arkitekturen innan hela regelbasen byggs |
| 2026-10-08 | Kundmodellen delas i fyra spår: förbud och stopp, obligatoriska åtgärder, riskklassning, rapportering | Olika bestämmelser med egna villkor och undantag |
| 2026-10-08 | Modellriskhantering ingår | PTL 6 kap. 1 § andra stycket gäller även en enkel regelmotor |
| 2026-10-08 | Okänd uppgift ger preliminärt resultat som inte kan fastställas | Okänt är inte samma sak som hög risk |
| 2026-10-08 | Paragrafkarta granskad av sakkunnig | Tester hittar inte krav som aldrig lagts in |
| 2026-10-08 | Modell och effort avgörs av utvärdering. Testleverantör i automatiska tester. | Kvalitet och kostnad ska mätas, inte antas |
| 2026-10-08 | Tillåtelselista per AI-anrop. Ingen batch som standard. | Små grupper kan vara personuppgifter. Batch lagrar data i 29 dagar. |
| 2026-10-08 | Bevarande, säkerhetskopia och återställningsprov | Kontrollsummor återskapar inga förlorade filer |
| 2026-10-08 | Resultatet heter "fastställt av byrån" | Får inte uppfattas som certifiering |
| 2026-10-08 | Juridisk granskning, modellvalidering, användningsprov och minsta drift före första riktiga byrå. AMLR som parallellt spår. | AMLR tillämpas från 2027-07-10 |
| 2026-10-08 | Kundmodellens spår har uttryckliga beroenden | Riskklass styr kundkännedomens omfattning och skärpta åtgärder (PTL 3 kap. 14–16 §§) |
| 2026-10-08 | Giltighet per paragraflydelse. Regeringskansliets rättsdatabaser som primärkälla. | PTL 1 kap. 2 § får ny lydelse 2026-11-20. Riksdagens version kan ligga efter. |
| 2026-10-08 | M5 är bara allmän riskbedömning, med genomgång av befintliga rutiner | Rutinerna ska bygga på riskbedömningen |
| 2026-10-08 | Allmänna råd får avvikas med motivering om det bindande kravet ändå uppfylls | Allmänna råd är inte bindande på samma sätt som lag och föreskrift |
| 2026-10-08 | Nästa genomgång räknas bara från utvärderingar, inte från fastställelser | Ett beslut att fastställa är ingen utvärdering (14FS 2024:11 2 kap. 3 §) |
| 2026-10-08 | Paragraftexten sparas i regelbasen med kontrollsumma. Krav har tillämplighet (`galler_om`) och belägg (`belagg`). | Lydelse, tillämplighet och belägg ska gå att kontrollera utan att regelbasens format byggs om |
| 2026-10-08 | Varje AI-försök sparas direkt med begärd och faktisk modell, effort, promptens kontrollsumma, svars-ID och tokenanvändning | Ett betalt svar får inte gå förlorat vid avbrott, och fallback kan byta modell |
| 2026-10-09 | Paragrafkartan har en rad per paragraf och kontrolleras mot källans paragrafindelning. Ohanterade paragrafer stoppar fastställelsen. | Spec 16.1: tester hittar inte ett krav som aldrig lades in |
| 2026-10-09 | Sakkunnigstatus *verifierad* gäller bara med kontrollsumma av det granskade innehållet | En status får inte överleva att kravet eller kartan ändras |
| 2026-10-09 | Ett fastställt paket publiceras med ett enda namnbyte. Fastställelser läses ur paketen. | En fastställelse ska vara helt gjord eller inte gjord alls |
| 2026-10-09 | Bristmönster B-23–B-29 läggs till. Regelbas v1 (M2) ska ha omfattning per tjänst, bolagsbildning och skatterådgivning i tjänstekatalogen och kalibrering mot sektorsrisken. | Två fullständiga sanktionsbeslut visar brister som katalogen saknade |
| 2026-10-09 | Original och OCR bevaras i `../underlag/tillsyn-2026-10-09/` från repots rot. Syntetiska fall med sidhänvisningar versionshanteras i repot. | Källkontroll kan göras lokalt och granskningsförmågan kan prövas utan råa byråhandlingar i tester eller AI-anrop |
| 2026-10-09 | Tillsynsfall inom allmän riskbedömning prövas i M3 efter sakkunniggranskning av facitet. | Före M5 ska det finnas evidens för att granskaren och sakgranskningsflödet hittar kända brister; en grön teknisk kedja räcker inte |
| 2026-10-09 | Sakkunnigs godkännande omfattar refererade lydelser och källans giltighet. Sakgranskning gäller texten med insatta namn. Tidigare paket verifieras innan de används. Ett skadat manifest ger ett fel med instruktion om återställning. | Tre negativa prov visade att godkännanden och historik annars kunde överleva ändringar som de inte omfattade |
| 2026-10-10 | Word-export med python-docx i M1. PDF skjuts till M4. | Word räcker för sakgranskning och fastställelse i M1. PDF-konvertering prövas tillsammans med användningsprovet. |
| 2026-10-10 | `faststall` tar `--organ`, `--datum`, `--namn` och `--roll` i stället för en sammanslagen `--beslut` | Spec 10 kräver namn, roll och datum. Separata argument behöver inte tolkas. |
| 2026-10-10 | Varje riskavsnitt ska ange inneboende risk, risk för terrorfinansiering och kvarstående risk med motorns nivåer, och `sakgranska` visar motorns nivåer bredvid texten | Slutgranskningen visade att AI-text kunde utelämna eller motsäga en nivå utan att valideringen märkte det. Ovanliga formuleringar fångas fortfarande bara av sakgranskningen. |
| 2026-10-10 | En öppen fråga från AI blir ett granskningsfynd som måste hanteras före fastställelse, och sakgranskaren ser frågan. En uppgifts status gäller bara med sina belägg: bekräftad kräver källa, datum och bekräftare, ej tillämplig kräver motivering, datum och bekräftare. | Codex visade att båda annars kunde fastställas som verifierbara paket (spec 10, villkor 1 och 2). |

## Nästa steg

1. Ta fram och granska implementeringsplanen för M2 (regelbas v1 och juridisk granskning).
2. Förbered sakkunniggranskningen av kraven och paragrafkartan i M2.
3. Bestäm vem som gör sakkunniggranskningen av regelbasen och acceptansprovet.
4. Låt sakkunnig bekräfta eller revidera [tillsynsfallens facitutkast](research/typfall/tillsyn-2026.json) mot de lokalt bevarade originalen. Använd fallen för M2 och pröva granskningen i M3 enligt spec 16.3.
5. Hämta och jämför Länsstyrelsen Skånes föreskrifter (12FS 2024:8).
6. Ta med de tretton mindre punkterna från slutgranskningen av M0–M1 i planen för M2 (förteckning sist i [implementeringsplanen](superpowers/plans/2026-10-08-m0-m1-grund-och-tunn-kedja.md)).

## Öppna frågor

Se avsnitt 17 i specen.
