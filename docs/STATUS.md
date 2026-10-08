# Status och framsteg

Senast uppdaterad 2026-10-08.

## Läge

**Fas:** design. Ingen programkod är skriven ännu.

| Steg | Status |
|---|---|
| Genomgång av källmaterial | Klar |
| Gemensam förståelse av mål och målgrupp | Klar |
| Val av omfattning (alternativ C) | Klar |
| Val av arkitektur (alternativ 2) | Klar |
| Fördjupad research (EU-regelverk, metod, teknik) | Klar |
| Strukturförslag och spec, revision 1 | Klar, granskad av Codex 2026-10-08. Sex brister påtalades och godtogs. |
| Spec, revision 2 | Klar, granskad av Codex 2026-10-08. Arkitekturens riktning godkänd, åtta ändringar påtalades och godtogs. |
| Spec, revision 3 | Klar, granskad av Codex 2026-10-08. Fem kvarvarande fynd (två höga, två medel, ett lågt) godtogs. |
| Spec, revision 4 | **Skriven, väntar på granskning** |
| Implementeringsplan | Ej påbörjad |
| Etapp M0 (grund) och M1 (tunn kedja) | Ej påbörjade |

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

## Nästa steg

1. Granska [specen, revision 4](superpowers/specs/2026-10-08-riskanalys-design.md) och godkänn eller begär ändringar.
2. Ta fram implementeringsplan för etapp M0 (grund) och M1 (tunn kedja).
3. Bestäm vem som gör sakkunniggranskningen av regelbasen och acceptansprovet.
4. Hämta och jämför Länsstyrelsen Skånes föreskrifter (12FS 2024:8).

## Öppna frågor

Se avsnitt 17 i specen.
