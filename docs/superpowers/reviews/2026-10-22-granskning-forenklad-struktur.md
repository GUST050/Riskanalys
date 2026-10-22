# Granskning av förslaget till förenklad struktur för allmän riskbedömning

Granskare: Claude Code, 22 oktober 2026.

Kontrollerat mot:
- PTL 2 kap. 1–2 §§ och 14FS 2024:11, 2 kap. 1–3 §§, i projektets källtexter (`regelbas/kalltexter/`).
- Länsstyrelsen Västra Götalands vägledning *Gör en allmän riskbedömning*, i användarens lokala kopia (MHTML).
- Analysmodellen, valideringen, rapporten och tjänstekatalogen på `feat/steg-1-3`, samt planerna och kombinationsgrupperna på `codex/kravstod-tjansteexponering` (`91a3ece`).

## Slutsats

**Förslaget är rätt och bör genomföras, med fyra justeringar.**

Kärnan har starkt stöd i vägledningen: byråns sårbarheter analyseras gemensamt och tillämpas sedan per tjänst. Vägledningen kräver att man ska "sammanväga och analysera hur samtliga riskfaktorer från den allmänna riskbedömningen påverkar den specifika produkten eller tjänsten". Det är just det förslaget gör, och det kan byggas med ett mönster som redan finns i programmet (gemensamma scenarier med koppling per tjänst).

Justeringarna:

1. **Konsekvens.** Vägledningen beskriver risken som "sannolikheten för att ett eller flera hot utnyttjar en eller flera sårbarheter med konsekvensen att produkten eller tjänsten utnyttjas", och frågar också "hur stora konsekvenserna skulle bli". Den föreskriver däremot ingen konsekvensskala. Programmets skala och fasta konsekvensvärden är metodval och bör märkas så. De bör inte kompletteras med ett nytt obligatoriskt fritextfält utan koppling till nivån. *(Rättad 22 oktober efter Codex påpekande: den tidigare formuleringen att konsekvens inte är en egen fråga i vägledningen var för stark.)*
2. **"Berör inte tjänsten"** får inte sänka motorns nivå före ett metodbeslut (D3). Fram till dess ska ställningstagandet synas som en avvikelse mot motorn, på samma sätt som en ej godtagen sänkning.
3. **Ställningstagandet per tjänst måste gå att göra samlat.** Annars blir det runt 100 svar för en byrå med fyra tjänster. Förslag: bekräfta "gäller enligt gemensam analys" för alla på en gång, och hantera bara avvikelser och osäkerheter en och en.
4. **Egna tjänster utanför katalogen** kräver ett metodbeslut om hot och grundnivåer. Det bör inte ingå i första leveransen, men luckan ska stå i kravmatrisen.

## Vad som är bindande, vägledning, metodval och teknik

| Del av förslaget | Grund | Kommentar |
|---|---|---|
| Identifiera tjänster | **Föreskrift** 14FS 2 kap. 2 § | Finns: erbjudandefält per katalogtjänst. |
| Analysera hot, med hänsyn till egen rapportering och myndighetsinformation | **Föreskrift** 14FS 2 kap. 2 §; **lag** PTL 2 kap. 1 § | Finns: hotkatalog med källor, egen erfarenhet (B-15). |
| Analysera sårbarheter: kunder, distributionskanaler, geografi, andra verksamhetsspecifika omständigheter | **Föreskrift** 14FS 2 kap. 2 § | Finns per tjänst i fem områden. Förslaget flyttar analysen till en gemensam nivå. |
| Värdera riskerna och motivera nivåerna | **Föreskrift** 14FS 2 kap. 2 § | Finns: motorns nivåer och lokal PT/TF-motivering. |
| Risknivå *per tjänst*, och sammanvägning av samtliga faktorer per tjänst | **Lag** PTL 2 kap. 1 § ("hur de produkter och tjänster … kan utnyttjas") och **vägledning** | Stödjer förslagets avsnitt 6. |
| Kombinationseffekter (lågrisktjänst med högriskleverans) | **Vägledning** | Finns delvis: kombinationsfaktorer i katalogen och deklarerade grupper. |
| Sannolikhet och konsekvensernas storlek | **Vägledning** | Vägledningen frågar efter båda. |
| Konsekvensskala, fasta konsekvensvärden och niocellsmatris | **Metodval** | Vägledningens matris är ett exempel; ingen skala föreskrivs. |
| Fyra ställningstaganden per gemensam sårbarhet och tjänst | **Metodval / teknik** | Bra arbetsstöd; inget krav på just den formen. |
| Standardiserad tjänstekatalog med bortval | **Teknik** | Arbetsbesparande, men får inte göra katalogtexten till byråns fakta. |
| Utvärdering före nya eller ändrade tjänster | **Föreskrift** 14FS 2 kap. 3 § (samma lydelse i 12FS 2024:8 och 01FS 2024:20) | Finns på `codex/kravstod-tjansteexponering` (planer, spärr och avslut). |
| Ingen sammanvägd riskpoäng för hela byrån | **Metodval** | Förenligt med källorna; inget krav på en byrånivå. |

## Svar på granskningsfrågorna

### 1. Stödjer strukturen sambandet hot → sårbarheter → sannolikhet och konsekvens → risk per tjänst?

Ja. Två preciseringar:

- **Konsekvensens storlek** efterfrågas av vägledningen, men ingen skala föreskrivs. Programmets skala ska redovisas som metodval, och dess fasta värde per tjänst (i dag oftast *betydande*, och alltid *allvarlig* för TF) ska motiveras. Inför inte ett fritt konsekvensfält som inte påverkar något. Det skulle bli ett formulärsvar som ser ut som analys.
- **Både PT och TF** täcks redan av motorns dimensioner och av de lokala motiveringarna (block 13–14). Den gemensamma analysen behöver ange för varje sårbarhet om den gäller PT, TF eller båda. Katalogens `galler` finns som förslag.

### 2. Vad kan bedömas gemensamt och vad behövs per tjänst?

| Gemensamt (en gång) | Per tjänst |
|---|---|
| Kundtyper och branscher | Tjänstens arbetsmoment, attest, betalningsmandat och bankinsyn (fälten finns: `P-TJ.*`) |
| Geografi och utlandsanknytning | Vilka kundgrupper som använder tjänsten (frivilliga fördelningar finns) |
| Distributionskanaler och leveranssätt | Ställningstagande till varje gemensam sårbarhet, med avvikelser motiverade |
| Organisation, kompetens, rollfördelning | Tjänstespecifika sårbarheter (till exempel betalningsmandat, klientmedel) |
| Externa leverantörer och utkontraktering (block 5) | Relevanta hot (scenariokopplingar finns) |
| Egen rapportering och erfarenhet (block 9) | Samverkan mellan faktorerna i just denna tjänst (block 8) |
| Sanktionsanknytning på byrånivå | Kontroller, effekt och kvarstående risk (block 10–12) |
| Myndighetsinformation (hotkatalogen) | Motiverad nivå och åtgärder (block 13, 14, 16) |

### 3. Kan urval och återanvändning förenklas utan att osäkerheter döljs?

Ja, med tre villkor:

- **Tjänsteurvalet** startar som *okänt* för alla tjänster, inte som ja. Bortvalsflödet är bra, men varje rad ska aktivt bli *erbjuds*, *erbjuds ej* eller *osäker*, och kunna bekräftas i ett steg. Gränssnittet ska förklara samspelet med införandespärren: den första bekräftelsen är kartläggning, men ett senare nej → ja kräver plan och utvärdering.
- **Ställningstaganden** kan bekräftas samlat per tjänst ("alla övriga gäller enligt gemensam analys"). *Otillräckligt underlag* och *berör inte* kräver dock individuell motivering och kan aldrig sättas samlat. En gemensam sårbarhet med status *antagande* eller *kunskapslucka* ska synas i varje tjänst som bekräftar den. Osäkerheten får inte försvinna genom samlad bekräftelse.
- **Katalogtexter** som arbetsmoment, befogenheter och frågor visas som förslag med egen märkning. Den bekräftade tjänstebeskrivningen sparas som byråns uppgift med källa och datum, på samma sätt som profiluppgifter.

### 4. Vilka analysblock kan återanvändas, flyttas eller ersättas?

| Block | Innehåll i dag | Förslag |
|---|---|---|
| 1 | Exponering | Per tjänst (oförändrat) |
| 2 | Delanalyser | Per tjänst (oförändrat) |
| 3 | Betalningsinsyn | Per tjänst (oförändrat) |
| 4 | Uppdragsprövning | Per tjänst (oförändrat) |
| 5 | Leverantörer | **Gemensamt**, med tillämpning per tjänst |
| 6 | Scenarier och kopplingar | Oförändrat; gemensamma scenarier finns redan |
| 7 | Sårbarhetsprövningar (fem områden per tjänst) | **Ersätts** av gemensam sårbarhetsanalys plus tillämpning per tjänst; tjänstespecifika sårbarheter kvar per tjänst |
| 8 | Samverkan | Per tjänst (oförändrat), med hänvisning till gemensam analys |
| 9 | Egen erfarenhet | **Gemensamt** (rapporten har redan gemensamt stycke), med kort tillämpning per tjänst |
| 10–12 | Kontroller, luckor, reduktion | Per tjänst (oförändrat); spärrarna från steg 2 behålls |
| 13–14 | PT- och TF-motivering | Per tjänst (oförändrat) |
| 15 | Sektor och sanktioner | Sanktionsanknytning gemensamt; sektorsjämförelse per tjänst |
| 16 | Slutsats och åtgärder | Per tjänst (oförändrat) |

Att bara dölja fält räcker inte, som förslaget själv säger. Valideringen i `analys/provning.py:_sarbarheter` kräver i dag alla fem områden i varje tjänst och måste ändras till att kontrollera den gemensamma analysen plus tillämpningen.

### 5. Vilka ändringar behövs?

**Datamodell (`analys/modeller.py`)**, enligt samma mönster som `gemensamma_scenarier` och `Scenariokoppling`:
- `Analyspaket.gemensamma_sarbarhetsprovningar`: id, område, katalogsårbarheter (eller egen), beskrivning, hotkopplingar, dimension (PT/TF/båda), belägg, och status (*bekräftad*, *antagande*, *kunskapslucka*).
- `Tjansteanalys.sarbarhetstillampningar`: gemensam post-ID, ställningstagande (`galler`, `galler_annorlunda`, `beror_inte`, `otillrackligt`), motivering, belägg, den gemensamma postens kontrollsumma och bekräftelse.
- Befintliga `sarbarhetsprovningar` per tjänst behålls för tjänstespecifika sårbarheter.
- Nya fält utelämnas vid serialisering när de är tomma, så att äldre paket blir byteidentiska. Det mönstret används redan för `Rutinatgard` och `Analysbindning`. Analysmodulerna ingår inte i modellidentiteten. Modellbindningen beräknas dock också av regelbasens kontrollsumma (`drift/modellidentitet.py:modellfilmanifest`), så utökad katalogdata, till exempel arbetsmoment och frågor per tjänst, ändrar bindningen. Leveransen som helhet ska därför inte utlovas ge oförändrad modellbindning. *(Rättad 22 oktober.)*

**Validering (`analys/provning.py`):**
- Varje gemensam post som avser tjänstens katalogsårbarheter ska ha ett ställningstagande i tjänsten.
- Områdena täcks på den sammanslagna nivån.
- `galler_annorlunda`, `beror_inte` och `otillrackligt` kräver motivering. `beror_inte` kräver dessutom belägg.
- Ändrad gemensam post gör tillämpningen inaktuell genom kontrollsumman (som `Scenariokoppling.scenariosumma`).

**Rapport:**
- D-ARB.5 slår ihop katalogens mekanism och byråns gemensamma analys till *en* post per faktor, i stället för två listor.
- Tjänsten visar bara avvikelser, osäkerheter och tjänstespecifika sårbarheter, plus en mening om att övriga gäller enligt den gemensamma analysen.
- B1 behåller fullständiga ursprungliga svar.

**Godkännanden:** `gallande_beslut` (`analys/provning.py`) binder varje tjänsts beslut till hela paketets revision, underlagssumma och svarssumma. En ändring var som helst, även i den gemensamma analysen, gör därför alla tjänsters beslut inaktuella. Blocksumman per post styr bara blockens bekräftelse, inte besluten. Selektiv förnyelse av bara berörda tjänster kräver en särskild ändring; första leveransen kan behålla dagens bredare omprövning. *(Rättad 22 oktober: den tidigare formuleringen att bara berörda tjänster påverkas var fel.)*

### 6. Vilka metodbeslut krävs innan tjänsteanalysen får påverka motorn?

- **D3:** Om, och med vilket typat belägg, `beror_inte` eller `galler_annorlunda` får ta bort eller ändra en faktors påverkan i en tjänst. Förslag: bara med ett strukturerat belägg (till exempel en bekräftad fördelning på 0 i tjänsten eller ett bekräftat mandat), aldrig med enbart fritext.
- **D5 och D9:** Hur kombinationer och små exponerade grupper vägs.
- **Ett nytt beslut om avvikande bedömning:** vad som gäller när byråns motiverade bedömning avviker från motorns nivå. Förslag: ingen fri nivå. Avvikelsen registreras som metodkonflikt som spärrar fastställelse tills metodansvarig har prövat den. Det följer principen "byrån kan stoppa en sänkning, aldrig skapa en" och projektets regel att AI och fritext inte sätter nivåer.

Fram till dess är motorn oförändrad. Ett `beror_inte` för en faktor som motorn tillämpar visas i tjänsteavsnittet som avvikelse ("motorn tillämpar X; byrån bedömer att den inte berör tjänsten eftersom …; nivån är oförändrad tills metodbeslut finns").

### 7. Hur överförs befintliga analyser?

- Gamla paket läses oförändrade. Nya fält är tomma och utelämnas.
- Ett hjälpflöde kan *föreslå* gemensamma poster där tjänsternas sårbarhetsprövningar har ordagrant samma text. Förslagen är obekräftade och utan författare.
- Blocksummorna ändras när strukturen ändras, så bekräftelser och analysbeslut nollställs. Inget godkännande förs över, vilket stämmer med förslaget.
- Fastställda paket berörs inte (de verifieras mot sina manifest).

## Vad som kan återanvändas direkt

- `gemensamma_scenarier` + `Scenariokoppling` med `scenariosumma`: mönstret för gemensam post och tillämpning per tjänst.
- `dokument/gemensamt_v8.py` (D-ARB.5) och dess granskningskontroller (B-09, B-10, B-15) för gemensamt underlag med prövning per tjänst.
- Profilens tjänstefält för attest, mandat, insyn och arbetssätt, samt frivilliga fördelningar per tjänst.
- Kombinationsgrupper och planer med avslut (`codex/kravstod-tjansteexponering`).
- Spärrarna för ej godtagna sänkningar som mall för hur avvikelser mot motorn visas.

## Risker att hantera

- **Samlad bekräftelse kan dölja osäkerhet.** Den måste därför vara spärrad för *otillräckligt underlag*, och statusen *antagande* ska synas i varje tjänst.
- **Katalogförslag kan läsas som byråns fakta.** De ska märkas och kräva bekräftelse.
- **"Berör inte" kan uppfattas som en sänkning.** Rapporten måste visa att nivån är oförändrad tills metodbeslut finns.
- **Egna tjänster utanför katalogen** kan inte motorberäknas utan beslut om hot och grundnivåer. Det är en lucka mot kravet att identifiera *alla* tjänster och bör stå öppet i kravmatrisen.
