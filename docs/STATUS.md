# Status och framsteg

Senast uppdaterad 2026-10-12.

## Klartext i låsta stycken (format v4), 2026-10-12

De låsta styckena i tjänsteavsnitten skrivs nu i klartext. Motorns utfall och gränserna är oförändrade; det som ändras är hur utfallet beskrivs.

- Kortnamn används i stället för fält-ID.
- Villkor skrivs i ord, till exempel ”Sårbarheten gäller om andel kunder i riskbranscher är minst 20 %”.
- Ja/nej-uppgifter skrivs som ”uppgiften ”<kortnamn>” är ja”.
- När en faktor förekommer men ligger under metodens gräns anger en gränsmening det: ”Faktorn förekommer: andel kunder i riskbranscher är 15 %, men det ligger under metodens gräns på 20 % för automatiskt riskpåslag.”
- Sektorsreferensen anges med källans titel, nivå, skala och sida, både i tjänsteavsnitten och i metodavsnittet D-ARB.2 (gemensam mening).
- D-ARB.2 skriver tjänstens namn, punkterna i ord och hindertexter med namn i stället för ID. Uppföljningsavsnittet namnger saknade uppgifter med kortnamn. Tjänstebeskrivningen dubblerar inte längre etiketterna.

Spårbarhet: varje stycke behåller sina referenser, och D-ARB.2:s tjänstestycken har nu även sektorsreferensens ID och källa. Bilagan D-ARB.B1 visar kortnamn och fält-ID för varje uppgift och listar nu även härledda andelar med källan ”Härledning: antal/bas”. I löptexten står ”härledd ur bekräftade uppgifter”.

Faktabladet till AI använder kortnamnen och skriver gränsmeningen bara när det visade värdet inte är skyddat; 0 och 3 kunder ger samma text. Sårbarhetsmodulen ber AI skriva att faktorn förekommer men ligger under gränsen.

Regelbasen är 1.3.0 med 48 kortnamn (43 fält i låsta stycken och 5 härledda andelar). Inga regler, gränser, källor eller sakkunnigstatus är ändrade; status är fortsatt `ej_granskad`. Ett saknat kortnamn serialiseras inte, så historiska attestsummor är oförändrade (prov mot frysta summor).

Formatet är `D-ARB-tjanst-v4`. Utkast i v3 måste skrivas om och sakgranskas på nytt. Regelbashöjningen gör också tidigare bedömningar inaktuella, så en v3-granskning kan inte fastställas. Fastställda paket byggs aldrig om och är oförändrade.

Verifiering: slutlig fullsvit är grön, **1 309 tester passerar och två livetester är bortvalda** (653,23 s), med båda API-nycklarna borttagna ur körmiljön. Regelbasvalideringen (regelbas 1.3.0, 107 krav, 11 tjänster) och `git diff --check` är gröna. Diffen mot utgångsläget är tom för `regelbas/kataloger/sarbarheter.yaml`, `regelbas/kundfalt.yaml`, `tester/enhet/test_faststall.py`, `tester/enhet/test_manifest.py`, `tester/typfall/` och `tester/fixturer/regelbas_v0/`.

Kvar:

- Nästa pilot ska kontrollera att AI inte skriver att en sårbarhet under gränsen ”inte gäller”.
- Ett beslut återstår om sårbarhetens utfall (ja/nej) för villkor ”> 0” på smågruppsandelar. Det skiljer 0 från 1–4 kunder i faktabladet och fanns före denna ändring.
- Återanvändning av v3-utkast byggs inte (beslut 2026-10-12).

## Pilot efter kalibreringen, 2026-10-12

Claude Sonnet 5.5 skrev tre tjänster åt den syntetiska byrån: löpande bokföring (T-RED-01), deklarationer (T-RED-03) och betalningar och attest i kundens namn (T-RED-05). Varje tjänst skrevs med effort `medium` och `high` på samma bedömning. Kostnadstaket var 10 USD; körningen kostade 2,42 USD.

| Tre tjänster, fem delar var | `medium` | `high` |
|---|---|---|
| Godkända förstaförsök | 12 av 15 | 13 av 15 |
| Reservmall | 0 | 0 |
| Kostnad | 0,81 USD | 1,61 USD |
| Tid per tjänst | 2–3 min | 5–6,5 min |

Före kalibreringen underkändes alla tio förstaförsök i en tjänst, och delen sårbarheter blev reservmall med båda effortnivåerna. De fem underkända förstaförsöken i den nya piloten godkändes efter omförsök: tre var för långa, ett använde få rapporter som belägg för litet hot och ett saknade referensen till ett tal. Texterna är konkreta och byråspecifika i båda nivåerna; möjliga överlapp skrivs som scenario. `high` ger något mer detaljerade kontroll- och övervakningsavsnitt. `medium` är ett preliminärt val för fortsatt provning, inte ett slutligt modellval. Piloten täcker ännu inte bolagstjänster eller skatterådgivning utöver deklarationer.

Piloten visade tre fynd:

- I fem av sex körningar skrev AI interna kommentarer i dokumentet, till exempel ”underlaget lämnas inte till AI”. Formuleringen kom från faktabladets och de låsta instruktionernas egna texter. De är nu neutrala (”underlaget finns i byråns lokala belägg”), systemprompten ber AI skriva att underlaget behöver granskas lokalt, och valideringen underkänner kommentarer om vad AI har fått. Beskrivningar av teknik, som ”AI-verktyg” eller ”fakturor som tolkas av AI”, godtas.
- Sårbarheten kunder i riskbranscher redovisas som att den inte gäller, fast 15 % av kunderna finns i riskbranscher. Metodens gräns för automatiskt riskpåslag är 20 %. Texten ska säga att faktorn förekommer men ligger under gränsen; tröskeln ändras inte. Det ingår i planen för klartext.
- De låsta styckena visar fält-ID, villkorsuttryck och sektorskoder. En plan för klartext tas fram och granskas innan formatet `D-ARB-tjanst-v4` byggs.

## Kalibrering efter piloten (planens del C), 2026-10-12

Piloten med Claude på den syntetiska byrån (en tjänst, Sonnet 5.5, effort `medium` och `high`) visade två systematiska fel. Prompten angav inga ordgränser, så alla första försök blev för långa. Kombinationsregeln underkände varje sårbarhetsstycke som nämnde två tillämpliga sårbarheter, så delen sårbarheter föll tillbaka till reservmallen.

- Varje delmodul anger nu delens ordintervall ur `LANGD`. Prompt och validering har samma källa, och promptens kontrollsumma följer gränserna.
- Kombinationsregeln ersätter regeln i avsnittet om granskningsrättelser nedan. Ett analysstycke underkänns när det påstår ett samband (samverkar, tillsammans, kombination, förstärker) och refererar minst två faktorer, alltså sårbarheter eller faktauppgifter. Att två faktorer gäller utan påstått samband godtas. Formuleringen ”ingen belagd kombination” godtas i analys enligt spec 8.4.4, liksom ”inga belagda kombinationer” och ”ingen kombination är belagd”. Systemprompten och sårbarhetsmodulen föreslår den formuleringen, ber om ett stycke per kategori och förbjuder sambandsord i analysstycken.
- Omsättningskontrollen räknade härledda andelar (0–1) som kronor i summan av tjänsternas intäkter. När hela omsättningen fördelades på tjänsterna underkändes därför underlaget. Andelsfälten räknas inte längre.

Verifiering: varje ändring har ett regressionstest som fallerade före rättningen, bland annat tre tjänster på 3 000 kr mot en omsättning på 9 000 kr och ett påstått samband mellan en sårbarhet och en faktauppgift. Fullsvit: **1 240 passerar, två livetester bortvalda** (695,91 s), utan API-nycklar i körmiljön. Regelbasvalidering och `git diff --check` är gröna; kontrollsumma och sakkunnigstatus är oförändrade. Inga riktiga API-anrop har gjorts under denna rättningsomgång. Del C:s tre ändringar är committade lokalt (e10d2d4, c4fa39f, a6d4ce9), och rättelserna efter granskningen är committade i en egen commit efter dem. Grenen är pushad till draft-PR #1.

Den nya piloten efter kalibreringen redovisas i avsnittet ovan.

## Rättelser efter avbruten pilot, 2026-10-12

Användaren rapporterade att piloten på en syntetisk byrå med Sonnet 5.5 och effort `high` stoppades efter åtta anrop, varav fyra klipptes vid 16 000 utdatatoken. Delanropens gräns är nu 64 000 token och anropen använder den befintliga strömningen. Ett tidigare `max_tokens`-avbrott i samma del hindrar höjning av effort i sista omförsöket, även om ett senare försök underkänns av ett annat skäl. Avbrottsmeddelandet anger anropets faktiska tokengräns.

Endast faktapoststatus `okänd` kräver `[VERIFIERA]` och oklarhet. Bekräftade maskerade värden med status `skyddad` får refereras utan dessa krav; deras exakta tal är fortfarande otillåtna som talplatshållare. `riskanalys skriv --effort` valideras och styr hela v3-körningen även med testleverantören. Valet sparas i manifestet och faktisk effort sparas per försök. Piloten kan därför jämföra `medium` med `high` på samma bedömning. Längdgränserna i `LANGD` är oförändrade.

Verifiering: tio regressioner fallerade för token/skydd och tre för körningens effort före rättningarna. Riktad svit: 87 passerar. Slutlig fullsvit: **1 226 passerar, två livetester bortvalda** (655,29 s), med båda API-nycklarna borttagna ur körmiljön. Regelbasvalidering och `git diff --check` är gröna. Ingen ny pilot eller riktiga API-anrop har körts av Codex. Inga commits eller pushar har gjorts.

## Rättelser efter granskning av AI-skrivningen, 2026-10-12

Claudes fem fynd är kontrollerade mot implementationen och rättade med fallerande regressionstester före respektive ändring. Permanenta leverantörsfel stoppar skrivningen direkt: 400, 401 och 403 ger ett meddelande med orsak och åtgärd. Endast 429, 5xx och nätverksfel får bli misslyckade försök. Slut på förberedda testsvar ger åter ett fel. Serverns fria feltext skickas inte tillbaka till AI.

AI kan ange `{period:ID}` med samma faktareferens eller skriva ”under statistikperioden”. Perioden sätts in från faktabladet före sakgranskning; fria datum, saknad period och trasiga platshållare underkänns. Kombinationskontrollen kräver scenario när minst två refererade sårbarheter gäller eller är okända, eller när analysen använder samverkansord. Sårbarhetsmodulen anger alla fem kategorierna `kund`, `kanal`, `geo`, `tj` och `verk`. Faktabladet sparas i tjänstresultatet; den separata dubbleringen `faktablad.json` är borttagen.

Verifiering: slutlig fullsvit är grön, **1 213 tester passerar och två livetester är bortvalda** (653,71 s), med båda API-nycklarna borttagna ur körmiljön. Regelbasvalidering och `git diff --check` är gröna. Regelbasens kontrollsumma och sakkunnigstatus är oförändrade. Inga riktiga API-anrop, commits eller pushar har gjorts. Den tidigare verifieringen nedan gäller implementationen före dessa rättelser.

## AI-skrivning från faktablad, 2026-10-11

[Planen](superpowers/plans/2026-10-11-ai-skrivning-fran-faktablad.md#genomförande-2026-10-11) är implementerad i del A och B. Programmet skriver tal, risknivåmeningar, sektorsreferens och låsta stycken. Fem AI-delar per tjänst körs i följd med separat schema, validering och högst två omförsök. Alla försök sparas direkt. Vid fortsatt fel används en reservmall som ger ett blockerande granskningsfynd. Dokumentformatet är `D-ARB-tjanst-v3`; grinden omtolkar råsvaren, omvaliderar dem och jämför fryst faktablad och dokument. Ändrad text eller format kräver ny sakgranskning.

AI får skyddade faktablad och säkra sammanfattningar av låsta stycken. Lokala källtexter, personnamn, fritext och omaskerade smågruppstal skickas aldrig med de låsta styckena. Regelbas `1.2.0` och dess sakkunnigstatus är oförändrade.

Mätningen i uppgift 4 är byggd: sammanställning per körning redovisar förstaförsök, samtliga anrop, felklasser och in-/ut-/cachetoken; kostnadsfunktionen tar uttryckliga priser. Ingen betald pilot är genomförd, så hypotesen att fyra av fem underkännanden försvinner är **inte uppmätt**. Design B, befintlig standardmodell och effort är preliminära tills utvärderingen i spec 8.4.8 är genomförd. Design A, byråövergripande AI-avsnitt och kryssfrågorna i 14.5 återstår enligt planens avgränsning.

Verifiering: slutlig fullsvit med syntetiska data är grön, **1 183 tester passerar och två livetester är bortvalda** (656,80 s), utan API-nycklar. Regelbasvalideringen är grön och kontrollsumman oförändrad. Den oberoende kodgranskningens fynd har fått regressionstester, rättats och återkontrollerats utan kvarstående anmärkningar. Inga riktiga API-anrop har gjorts. Inget är committat eller pushat i detta genomförande.

## Läge

**Fas:** M2:s tekniska implementation, lokalt fullständigt intag och SCB-registerförslag är införda. Regelbasen är `1.2.0`. Juridisk sakkunniggranskning, M3:s modellprov och M4:s verksamhetsprov återstår.

**Aktuellt:** [M2-planens genomförandelogg](superpowers/plans/2026-10-10-m2-regelbas-v1-och-juridisk-granskning.md#genomförande-2026-10-10) beskriver implementation, verifiering och överlämning. Aktuell regelbas `1.2.0` har 107 krav, 11 tjänster, 283 fält, 24 källor, 21 hot, 28 sårbarheter, 13 kontroller och tre länspaket. [Intagsplanen](superpowers/plans/2026-10-10-intag-och-hel-riskbedomning.md) och [registerplanen](superpowers/plans/2026-10-10-registerhamtning.md) beskriver de efterföljande användarflödena. **Ingen verklig sakkunnigattest har tillkommit; M2-etappen är ännu inte juridiskt klar.** M2-koden och rättelserna versioneras som teknisk baslinje på `codex/m0-m1`; verkligt juridiskt godkännande återstår.

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
| Källkontroll inför M2 | [Research 10](research/10-kallkontroll-och-gapinventering-m2.md) kompletterad av Codex 2026-10-10: rapporteringsundantag, registrering enligt PTL 7 kap., avgränsning av punkt 23, tre länspaket och separat AMLR-utkast. Tio källfilers storlek och SHA-256 stämmer; paragrafuttag omfattar PTL 142 lydelser/141 lagrum, PTF 29 och 31 per föreskrift. Visuell jämförelse av tabell 1 på sidorna 5–6 visade samma kontroll- och dokumentationskrav. Juridisk granskning återstår. |
| [Implementeringsplan M2](superpowers/plans/2026-10-10-m2-regelbas-v1-och-juridisk-granskning.md) | Skriven och självgranskad av Codex på användarens begäran 2026-10-10. 18 uppgifter med filer, gränssnitt, kontrakt, grindar, tidsestimat och överlämning till M3. Alla tretton restpunkter har placering. Teknisk implementation och verklig sakkunniggranskning redovisas separat. **Teknisk implementation och kontrakt är införda; se genomförandeloggen och färsk verifiering nedan.** |
| Rättat researchverktyg | `lydelsetexter.py` hanterar nu SFS i kommandoraden, datumversioner och felkoder. Åtta regressioner fallerade före rättningen; samtliga nio verktygstester passerar. Färsk fullsvit 2026-10-10: **504 passerar, ett livtest bortvalt**, utan API-nyckel (14,81 s). Uttag via CLI prövat för alla paragrafer i de fem lokala rättskällorna; tre M1-paragrafsummor bevaras. Ingen ändring i `src/` eller den operativa regelbasen i denna planeringsomgång. |

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

## M2 – färsk verifiering 2026-10-10

**Färsk fullsvit efter Claudes granskning och sista konfliktgrindsrättelsen: 836 passerade, 1 livetest bortvalt, 261,79 s**, körd med `env -u ANTHROPIC_API_KEY .venv/bin/pytest -q`. Före denna rättelseomgång passerade 800 tester. Nya prov omfattar versionsskydd, andelsbelägg, oberoende facitimport, rättsliga undantag, granskningskonflikter och små komplement. Hela kedjan och byteidentisk återställning passerar för alla tre län. Åtta negativa CLI-prov (sju fastställelsefall samt handredigerad bekräftelse vid bedömning) stoppar utan paket, inklusive äldre bedömning och rättslig datumgräns.

- Regelbasvalidering: giltig `1.0.0`, 107 krav, 11 tjänster, 201/201 hanterade paragrafer i VG, Skåne och Stockholm. Samtliga kartor är `ej_granskad`.
- AMLR-utkast: 90 artiklar och sex bilagor, 92 återstående poster, eget verifierat manifest. Utkastet kan aldrig väljas operativt via ett framtida datum.
- Tillsynsmaterial: två fall, 17 förväntade fynd och fem varianter; 173 arkivkontrollsummor stämmer. **Facitet är ännu inte sakkunniggranskat och de 17 fynden inte produktutvärderade.**
- Fristående teknisk slutgranskning och rättelser dokumenteras i M2-planen. Syntetiska granskare signerar endast testkopior. Inga betalda AI-anrop eller installationer har gjorts.

### Claudes M2-granskning och rättelser

Codex reproducerade och rättade versionsbortfallet (2.0.0/10.0.0), den tysta förlusten av äldre andelsbelägg, facitkopplingen och okänt paket vid import/export. Kandidatraderna i spår A har rättats efter källkontroll men är fortsatt ogranskade. Facitets 22 objekt har en separat version/summa och en kanonisk fil; regelpaketen har 194 rättsliga/metodobjekt var. Lokala attestfiler med granskarens identitet undantas från Git. Motstridiga aktuella beslut stoppar båda berörda paketen oavsett läsordning. Små komplement skyddas också i AI-underlaget. Kärnmodulerna har gjorts mer läsbara. Detaljer och begränsningar finns i [planens rättelselog](superpowers/plans/2026-10-10-m2-regelbas-v1-och-juridisk-granskning.md#rättelser-efter-claudes-granskning-2026-10-10).

Tidigare expertunderlag bevaras som historiska och ska inte användas för den rättade regelbasen. Ingen faktisk sakkunniggranskning har gjorts. Användaren har begärt commit/push av den tekniska M2-baslinjen. Slutlig testkörning efter alla kodändringar: **836 passerade, 1 livetest bortvalt, 261,79 s**, exitkod 0. Regelbasvalidering, AMLR-manifest, tillsynsarkiv, kompileringskontroll och `git diff --check` passerar. Ingen linter har installerats eller körts i rättelseomgången.

### Kontroll inför commit/push

En sista teknisk granskning hittade att konfliktgrinden missade gemensamma krav som var inaktiva för den aktuella byråprofilen. Rättat: paketets alla granskade krav ingår nu i konfliktkontrollen. Fyra regressioner fallerade före rättningen, och motsvarande grind prövas för båda paket och läsordningar. Källuttagens originalbytes bevaras; Git:s whitespacekontroll avgränsas för dessa frysta utdrag. Färsk fullsvit efter denna rättelse: **836 passerade, 1 livetest bortvalt, 261,79 s**, exitkod 0. Elva riktade konfliktprov passerar också. Den fristående tekniska återgranskningen fann inga kvarvarande P1/P2 i granskade kärnflöden. De tre exporterade underlagen motsvarar dagens regelbas, med giltiga innehållssummor och manifest. Verklig sakkunniggranskning och M3/M4 återstår.


### Förtydligat uppdrag: verksamhetsanpassad riskbedömning

Användaren har förtydligat att Codex ska göra källresearch, analys och skrivarbete för ett program som kan anpassa riskbedömningen till olika byråer, med en första lokal pilot. Byrån behöver bekräfta sina faktiska verksamhetsuppgifter. Identitet och pilotunderlag ligger utanför Git. Kravet på oberoende sakkunnigattest i specen är ett internt kvalitetsskydd, inte ett generellt lagkrav på extern certifiering av varje allmän riskbedömning. PTL:s krav på intern kontroll och eventuella särskilda funktioner behöver bedömas separat. [Första källgenomgången och arbetsgången](research/10-kallkontroll-och-gapinventering-m2.md#12-förtydligande-byråns-riskbedömning-och-projektets-granskningskrav) är dokumenterad. AI-källkontroll registreras inte som mänsklig attest. Pilotens uppgifter saknas ännu i det identifierade projektunderlaget. De ska kunna lämnas genom programmets intag; en tidigare verksamhetsbeskrivning eller riskbedömning är ett frivilligt underlag.


### Fullständigt intag som produktkrav

Användaren har förtydligat att programmet ska samla in allt relevant underlag och skriva hela den allmänna riskbedömningen. [Spec revision 12, avsnitt 14.1–14.3](superpowers/specs/2026-10-08-riskanalys-design.md#141-fullständigt-intag-och-skrivning-av-hela-riskbedömningen) beskriver intervjun, följdfrågor, kravtäckning, kompletteringar och användningsprov. En tidigare riskbedömning är inte ett startkrav. Den tekniska implementationsluckan är nu åtgärdad enligt [intagsplanen](superpowers/plans/2026-10-10-intag-och-hel-riskbedomning.md). Regelbas 1.1.0 har 219 fält inklusive nya lokala beskrivnings- och beläggsfält; kanoniska frågor har versionerade krav-/avsnitts-/källkopplingar och beroenden. `riskanalys intag <byrå>` startar eller återupptar den lokala intervjun, kontrollerar kompletteringar och skapar hela Word-utkastet. Kontrakt och syntetiska formulärprov ingår; M3:s sakkunnigbekräftade typfall samt M4:s verkliga pilot, sakgranskningsgränssnitt och driftprov återstår.

## Nästa steg

Codex fortsätter käll- och metodgenomgången samt intaget för pilotbyrån. Följande är kvarstående produktgrindar enligt befintlig spec, inte en förteckning över lagkrav på externa konsulter:

1. Utse en oberoende sakkunnig och låt denne granska de tre paketens exporter samt krav, datum, tillsyn/yrkesroller, FS-tabeller, NRA-skala, metodval och kundgrenar. Tre rättade, ogranskade exporter finns i `../underlag/sakkunnig-intag-2026-10-10-r3/{vg,skane,stockholm}/`, med verifierade manifest och gemensam README. Inga riktiga godkännanden finns.
2. Bekräfta eller revidera de 17 tillsynsfynden/fem varianterna mot lokala original, inklusive beslutens rättsliga status. Importera endast verkligt granskade beslut. Facit har en separat import och attest; en facitrevision kräver ny facitgranskning och upphäver inte paketens juridiska attester.
3. Bygg M3: metod- och granskningsutvärdering med sakkunnigbekräftat facit. Pröva automatiska/manuella B-kontroller, falska fynd, sakfel, granskningstid och AI-kostnad mot manuellt arbete. Kund-C behöver en granskad metod och får ingen normalrisk som standard.
4. Genomför M4:s användningsprov, säker drift, installation och återställning före första riktiga byrå. M2:s gröna teknik är ingen leverans av en färdig användarprodukt.

## Öppna frågor

Se avsnitt 20 i specen samt M2-planens avsnitt om verkliga beslut.


### Genomförande: fullständigt intag 2026-10-10

- Regelstyrd intervju från tom profil, per tjänst och tillsynsområde. Okänt kan sparas, andelar härleds och verksamhetsbeskrivningar/kontrollbelägg sätts in lokalt. Användaren lämnar fakta; programmet skriver utkastet.
- Privata atomiska profilskrivningar, tidigare profilkopior, revisionskonflikter och omprövade beroenden. CLI och webb delar låst atomisk tilläggsoperation för utvärderingshistorik.
- Word byggs med bedömning, godkända AI-utkast, maskinell granskning och manifest. Nedladdningen kontrollerar aktuell profil, regelbas, historik och källfiler. Omexport efter faktisk utvärdering återanvänder den tidigare exportens bedömningskälla och AI-text.
- Lokal HTTP-server på 127.0.0.1 med slumpad åtkomstväg, Host/Origin/CSRF, HTML-escaping, CSP, begränsad kropp, no-store och inga requestloggar. Riktig webbläsare använd för spara→nästa fråga→omladdning→översikt med syntetiska uppgifter; inget verkligt AI-anrop.
- Fristående teknisk granskning har lett till regressioner för kontroll-/geografiberoenden, gamla alias, AI-frågor om härledda andelar, handredigerad datakvalitet, samtidig historik, historikändring efter Word-export, inaktuell sektorsmotivering och förlust av riskavsnitt vid omexport. Då identifierade fynd rättade. Senare Claude-granskning hittade ytterligare brister i intag/CLI/skrivning; se rättningsloggen nedan.
- Alla tidigare fastställelsegrindar finns kvar. Inga sakkunnigattester har skapats. Tekniskt intag är ingen juridisk certifiering eller avslutad M3/M4.
- Start: `.venv/bin/riskanalys intag pilotbyra`. Nyckel behövs först vid uttrycklig Claude-skrivning. Faktaunderlag för pilotbyrån är ännu inte inmatat i detta byggarbete.


**Färsk slutverifiering av intaget (2026-10-10):** `env -u ANTHROPIC_API_KEY .venv/bin/pytest -q` gav **881 passerar, ett livetest bortvalt**, 468,32 s. Detta inkluderar 45 nya intagsprov och hela befintliga sviten. Tre syntetiska tom-profil→formulär→Word-prov passerar för VG, Skåne och utländsk filial/Stockholm. Det verkliga webbläsarprovet omfattar sparande, nästa fråga, omladdning och översikt, inte ett riktigt Claude-anrop. Regelbas 1.1.0 validerar med 107 krav, 11 tjänster och 201/201 hanterade paragrafer per länspaket; sakkunnigstatus är fortfarande `ej_granskad`. `compileall` och `git diff --check` passerar. De tre r3-granskningsunderlagens manifest är verifierade. Koden och dokumentändringarna är inte committade eller pushade i detta uppdrag.

**Registerförifyllning i intaget:** organisationsnummer och myndighetsdata enligt [källkontroll och valt flöde](research/10-kallkontroll-och-gapinventering-m2.md#14-förifyllning-från-företagskällor-2026-10-10). SCB AFR-hämtning och lokal SCB-JSON-import är implementerade enligt [registerplanen](superpowers/plans/2026-10-10-registerhamtning.md). Personlig SCB-nyckel saknas ännu; autentiserat uppslag är inte verifierat. Externa värden ska vara källbundna förslag, och byråns egna tjänster/kundstatistik/kontrollbelägg behöver fortfarande bekräftas.

### Registerhämtning i intaget 2026-10-10

SCB AFR v1 är första avgiftsfria connectorn. Användaren har ingen API-åtkomst ännu. Lokal `RISKANALYS_SCB_API_KEY` används efter användarens egen registrering; JSON-fil kan importeras som alternativ, märkt ej verifierat ursprung. Bara juridiska organisationsnummer används i denna connector. Enskilda firmor kan fortsätta manuellt.

Grund-/registersidan visar namn, säteslän, arbetsställeantal, SNI, juridisk form/status och anställdas/omsättningens klasser med år. Bara namn/län/ställen kan överföras med uttrycklig rätt-byrå-bekräftelse. Hämtning ändrar inga profilsvar, avvikelser visas och ändringar använder ordinarie profilvalidering och beroenden. Privat lagring bevarar minimala snapshots med källhänvisning och summa utanför Git. AI:s tillåtelselista och sakkunnigstatus är oförändrade.

Källor, valt flöde och hämtas/frågas-matris finns i [research 10 §14](research/10-kallkontroll-och-gapinventering-m2.md#14-förifyllning-från-företagskällor-2026-10-10). Bolagsverket HVD prioriteras som senare adapter; inget gissat API eller Allabolag-skrapning är byggt. SCB:s autentiserade liveflöde återstår att prova när en personlig nyckel finns. Ingen nyckel, inget konto och ingen betald AI-användning ingår i verifieringen. Kodändringarna är inte committade eller pushade i detta uppdrag.

**Färsk slutverifiering för registerhämtningen:** hela sviten gav **938 passerade, 1 livetest bortvalt, 454,56 s**, exitkod 0, utan AI-/SCB-nycklar. 57 nya registerprov ingår. Fristående återgranskning verifierade då provade rättelser; senare Claude-granskning fann ytterligare brister som redovisas i rättningsloggen nedan. Verkligt webbläsarprov använde syntetisk transport: hämtning, grundstart, bekräftelse av namn/arbetsställen, sparande efter omladdning och fortsatt fråga om verkligt personantal. Regelbasvalidering, compileall och whitespacekontroll passerar. Autentiserat SCB-uppslag och M3/M4:s verksamhetsprov är separata återstående kontroller.

### Claude-granskning och minskad manuell inmatning 2026-10-10

[Fynd 1–10 och kompletterande beslut](superpowers/plans/2026-10-10-intag-och-hel-riskbedomning.md#claude-granskning-och-rättelser-2026-10-10) är prövade/rättade med regressioner. Spec revision14 beskriver gemensam CLI/webb, bevarade okända belägg, länpolicy, skrivtoken och registerdatumgrind. De tidigare slutomdömena ska läsas som daterade avgränsade tekniska kontroller. Denna rättningsomgång har nu färsk helsvit och fristående återgranskning enligt resultatet nedan.

[Utvidgad research](research/10-kallkontroll-och-gapinventering-m2.md#142-utvidgad-research-mindre-manuell-inmatning-2026-10-10) skiljer byggd SCB-förifyllning (tre kanoniska intagsfält) från fler offentliga grund-/bokslutsuppgifter och byråns egna exporter. Lokal aggregerad import prioriteras för att reducera manuella verksamhetssvar; Bolagsverket HVD är nästa externa datakälla. Inga nya konton, API-åtkomster, betalda anrop, sakkunnigattester, commit eller push har gjorts.

Första fullsviten i rättningsomgången gav 956 passerade/1 fel/1 livetest bortvalt (449,97 s). M2:s negativa paketprov fångade en oavsiktlig län/paket-samordning efter orelaterat CLI-svar. Den rättades med ytterligare RED-regression och föranledde en ny fullsvit enligt slutresultatet nedan. Provets säkerhetsförväntan behålls.

Återgranskningen hittade även explicit återbekräftelse med oförändrat grundvärde men ändrat effektivt län/paket. Det är rättat efter RED-prov; sådan metadataändring omprövar nu beläggen. De 21 nya regressionerna och M2:s negativa paketprov gav 22 passerade (30,74 s). Fristående återgranskning fann inga konkreta P1/P2 i den sista avgränsade länrättningen. **Slutlig fullsvit: 959 passerade, 1 livetest bortvalt, 465,53 s**, exitkod 0, utan AI-/SCB-nycklar. Regelbasvalidering, compileall och diff --check passerar. Syntetiskt webbläsarprov visar egen filialkälla och sparande av okänt svar utan roll. Verklig API-åtkomst, sakkunnigstatus `ej_granskad` och M3/M4:s produktgrindar kvarstår; nya CSV/XLSX-/BV-importer är föreslagna, inte byggda. Ingen commit/push.

### Datumoberoende registerprov och CLI-längdfel 2026-10-11

De tio datumberoende registerfelen reproducerades och rättades i testuppsättningen. Intagets testklocka använder nu samma syntetiska dag som bedömningsfixturen; successiva hämtningar behåller olika tidsstämplar. De två proven som blandade `DAG` med verkligt dagens datum är samordnade. Produktionsgrindarna för framtida/historiskt underlag och svensk hämtningsdag är oförändrade.

CLI:s `IntagSvar`-validering blir nu ett `ProfilFel` med svensk längdanvisning, i stället för en Pydantic-stackspårning. Fyra nya negativa regressioner blev först röda för svar, roll, källa och motivering; två gränsprov visar fortsatt sparande vid 12 000/200 tecken. Avvisning ändrar inte profil eller profilhistorik. Båda ursprungliga kommandona återprovades också som riktiga CLI-processer. [Detaljer och RED/GREEN-loggar](superpowers/plans/2026-10-10-intag-och-hel-riskbedomning.md#datumoberoende-prov-och-cli-längdfel-2026-10-11).

**Färsk helsvit:** `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest` gav **965 passerade, 1 livetest bortvalt, 458,81 s (7:38)**, exitkod 0. Logg: `/tmp/riskanalys-2026-10-11-full-pytest.log`. Alla 89 intagsprov passerade separat; 62 berörda register-/fråge-/fyndprov passerade även med simulerad omgivningsdag 2025-01-01 respektive 2030-01-01. Regelbasvalidering, compileall och diff --check passerar. Ingen kodändring efter helsvitens start, bara dokumentationsnoter. Ingen commit/push.

**Beslut inför nästa bygge:** gör först ett manuellt pilotintag för pilotbyrån och inventera vilka exporter som faktiskt finns. Bygg därefter CSV/XLSX-import för det verifierade formatet, inte en generell import först. Pilotunderlag ligger utanför Git. Pilotintaget och den nya importen är ännu inte genomförda.

### Förenklat och mätt intagsflöde 2026-10-11

Namn, säteslän och registrerade arbetsställen kan nu godkännas tillsammans och följa med redan vid registerstart. Motsvarande ordinarie fråga visar sparat SCB-förslag med godkännandeknapp. Hämtning ändrar inga profilsvar; avvikande tidigare värden kräver uttryckligt ersättningsval. Valideringen sker först i minnet och hela urvalet sparas med en CAS-sparning. Ett tomt registerurval får inte bekräfta säteslänet.

Elva tjänsteutbudsfrågor kan besvaras i en samlad lista med gemensamt eget underlag/roll/datum och uttrycklig bekräftelse att omarkerade tjänster inte erbjuds. Enskilda osäkra svar med ”Vet inte” finns kvar. Intervjusidan visar frågor som kan besvaras nu, i stället för alla ännu osäkra följdfrågor. Roll föreslås redigerbart och senast framgångsrikt sparad roll återanvänds i sessionen. Metadata och registerbakgrund kan expanderas vid behov.

F-skatt, moms och arbetsgivarregistrering läses ur samma SCB-svar som registerbakgrund i snapshot v2. Tidigare v1-bilder behåller format/summa och kan fortfarande användas. Nyckel kan anges i ett lokalt lösenordsfält och användas i sessionen utan disk-/HTML-lagring; miljövariabel stöds också. Användaren har visat ett eget lyckat SCB-uppslag. Agentens implementation/verifiering använder syntetisk transport och data, inga personliga nycklar eller verkliga svar från pilotbyrån. [Ny research och källmatris](research/10-kallkontroll-och-gapinventering-m2.md#143-ny-källkontroll-och-förenklat-godkännande-2026-10-11) skiljer dagens överförbara fält från Bolagsverkets möjliga filial/verksamhet/bokslut, separat åtkomst och byråns egna statistik-/kontrolluppgifter. Manuellt pilotintag och exportinventering återstår före formatanpassad CSV/XLSX-import; ingen generell import eller ny Bolagsverket-adapter har byggts.

**Verifiering:** 25 nya regressioner totalt, inklusive samlade svar, fel utan delvis sparning, gamla flikar/bilder, datum, skattestatus utan faktainferens, v1-summor, sessionsnyckel utan återgivning och unika formuläretiketter. Fristående granskningens markörfria start och rollförslag reproducerades RED→GREEN. Verkligt webbläsarprov använde syntetisk transport: registerstart → nästa riktiga lucka → samlad tjänstelista → sparande/omladdning → bevarad registerjämförelse och expanderbar skattestatus. Lokal HTTP-benchmark med sex fall ×100 mätningar gav median **8–47 % kortare svarstid**, med fulla mätdata och begränsningar i [prestandaunderlaget](research/intag-prestanda-2026-10-11.json). Detta mäter lokal rendering, inte extern SCB-hastighet eller verklig användartid.

**Slutlig helsvit:** `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest` gav **990 passerade, 1 livetest bortvalt, 441,32 s (7:21)**, exitkod 0, utan varningar. Logg: `/tmp/riskanalys-smidigt-final-full-pytest.log`. Regelbasvalidering, compileall och diff --check passerar; sakkunnigstatus är fortsatt `ej_granskad`. Kod och testuppsättning ändrades inte efter slutkörningens start; endast dokumentationsnoter. Ingen commit/push. Den befintliga verkliga pilotservern har inte startats om eller ändrats; samma intagskommando behöver köras igen för att visa ny kod och bevarade svar.

### Underlagsval och tydlig leverans 2026-10-11

Enkla verksamhetsfakta/beskrivningar har nu ett synligt val ”Egen kännedom om verksamheten”. Det sparas med användarens bekräftelse, funktion och datum, utan krav på en ny fritextkälla för varje sådant svar. Statistik, numeriska frågor, sektorsmotiveringar och kontroller har inget sådant snabbval. Tidigare aktuella bekräftade manuella underlag kan väljas igen inom samma kategori och exakt period; kund-/ekonomi-/erfarenhetsstatistik och varje kontroll/fas hålls åtskilda. Okänt/inaktuellt underlag och registerbildens generella källa erbjuds inte som manuellt underlag. Period föreslås från bekräftad kundbas respektive omsättning. Gammal revision eller ändrat underlagsval lämnar profilen oförändrad vid avvisning.

SCB-schema 3 bevarar ägarkategori. Kod 41 (privat svenskkontrollerat utan koncerntillhörighet) ger ett villkorat ”nej”-förslag för yttersta moderföretag, med synlig begränsning och uttryckligt godkännande. Övriga/saknade koder ger inget koncernförslag; filial härleds inte. V1/v2 behåller exakt tidigare format/kontrollsumma. Grund-/översiktssidan och skrivrubriken visar nu faktisk leverans: allmän riskbedömning som Word-utkast med verksamhet, risker per tjänst, kontroller och åtgärder, samt granskningsbilaga vid öppna fynd. Separata rutindokument och individuella kundriskbedömningar ingår inte i detta intags skrivflöde.

[Fler källor inventerade](research/10-kallkontroll-och-gapinventering-m2.md#144-fler-källor-underlagsval-och-tydlig-leverans-2026-10-11): Bolagsverket HVD prioriteras för registrerad verksamhet/organisationsform/digitala årsredovisningar, men separat API-åtkomst och maskinellt kontrakt återstår. Skatteverkets befintliga statusbakgrund via SCB räcker för de nu byggda fälten. Polisen/Länsstyrelserna och EU/FATF kan tillföra riskunderlag; ny NRA 2026 om juridiska personer är identifierad men inte integrerad eller använd för att ändra frysta riskregler. Manuellt pilotintag och inventering av verkliga exporter återstår före ny formatanpassad CSV/XLSX-import.

**Verifiering:** 18 nya regressioner, med RED före produktionsändring; 83 fokuserade prov passerade (35,50 s) och alla berörda intags-/företagsdataprov gav 172 passerade (186,90 s). Fristående granskning fann inga konkreta fynd i den avgränsade ändringen. Syntetiskt webbläsarprov visar godkänt koncernförslag, sparad egen kännedom, sparat kundunderlag/period återanvänt i nästa kundfråga och att omsättning inte får samma underlag föreslaget. Bildbevis finns utanför Git i `/Users/gt/.codex/visualizations/2026/10/11/01a12a55-3718-74f2-bc3b-588e958dab72/intag-underlagsval.png`. Provfliken och provservern är avslutade; den verkliga pilotservern har inte startats om. Inga personliga nycklar, autentiserade API-/AI-anrop eller verkliga uppgifter från pilotbyrån användes.

**Slutlig helsvit:** `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest` gav **1008 passerade, 1 livetest bortvalt, 466,39 s (7:46)**, exitkod 0, utan varningar. Logg: `/tmp/riskanalys-underlagsval-final-full-pytest.log`. Regelbasvalidering, compileall och diff --check passerar; sakkunnigstatus fortsatt `ej_granskad`. Kod/testuppsättning ändrades inte efter fullsvitens start, bara dokumentationsnoter. Ingen commit/push. Användaren behöver stoppa sin befintliga intagsserver med Ctrl+C och köra samma kommando/ID igen för att läsa ny kod och bevara svar. Pilotens befintliga data-ID byts inte automatiskt.


### Källkontroll och verksamhetsanpassad D-ARB 2026-10-11

Användarens beställning i [research 11](research/11-kallkontroll-allman-riskbedomning.md) kontrollerad självständigt mot kod, regelbas, PTL/föreskrifter, rapport 2026:14, vägledningen mars 2025, sparade Länsstyrelsewebbsidor/nyhetsbrev och tillsynsbesluten. H5-planen [tjänststruktur](superpowers/plans/2026-10-11-d-arb-tjanststruktur.md) godkändes av användaren före bygge. Tidigare ändringar i checkout bevaras; inget har committats eller pushats i detta uppdrag.

- H1/H2: egna rapporter och misstankebaserade avböjanden ingår som belagd erfarenhet, utan riskpoäng från antal. B-15 maskinkontrollerar erfarenhet i varje tjänsts hotanalys. Varje sårbarhet motiveras med villkor, faktiskt underlag, period och källa. Ofullständigt geografiskt underlag eller borttagen motivering ger blockerande B-09/B-10.
- H3/H4: 18 nya sårbarhetsindikatorer med intagsfält, 7 konkreta hot/tillvägagångssätt inklusive tre terrorfinansieringsmodus. H-01/H-02 kopplas till tjänster; research 11:s påstående om total avsaknad av TF korrigeras: H-03 var redan markerad TF, men konkreta modus saknades. Kundantal/andelar för forskningsluckorna byggda; positiva belagda andelar för fysiskt möte, utländska ägare, högrisktredjeland och utsatt område kan inte döljas av en nej-indikator.
- H5/M1–M3: kontrollernas dokumenterade effekt före riskavsnitten. Sex analysdelar per tjänst; råa intagsfrågor/svar och källversioner i sakgranskad bilaga. Lokala fritexter stannar utanför AI. Omfattning följer storlek/art i BT-OMF-01; trösklar är ogranskade metodval. Slutsatser omfattar rutiner, kundkännedom, övervakning och utbildning. Ingen sammanvägd byrånivå; spec §7.4 och §7.5 uppdaterade.
- M4/L: dokumenterad omvärldsbevakning med lästa registrerade källversioner, ansvar och relevans; hämtning är inte genomförd byråbevakning. Uppdateringsgrunder, spridning, goAML och tidigare tillsyn ingår. Tolv nya original hämtade och SHA-256-kontrollerade, se [manifest](research/kallmanifest-2026-10-11.json). SMOB är en forskningsrapport från ett forskningscentrum, inte en föreskrift/myndighetsnorm.
- Fastställelse: ändrad text, underrubriker, namn, dokumenttitel, avsnittsordning eller bilaga kräver nytt sakgodkännande. Formatet `D-ARB-tjanst-v2` registreras i nya gransknings-, export- och fastställelsemanifest; historiska paket ändras inte. Maskingranskning regenererar deterministisk tjänstanalys och stoppar ändrat innehåll/sexdelad struktur. `ej_bedömd` effekt är okänd. Kontrollernas period och de nya faktorernas period ska stämma med kundunderlagets analysperiod; historiska belägg med annan period ger ingen aktuell reduktion.

**Verifiering:** H1/H2 skrevs RED före kod; den då fokuserade regressionskörningen gav 103 passerande prov. Senare H3/H4/H5/M1–M4 och slutgranskningsrättelser skrivna RED→GREEN. Fristående slutgranskare fann inga Critical och reproducerade luckor i ej bedömd effekt, ändrad deterministisk text och historiska kontroll-/faktorperioder; samtliga rättade med regressioner. Precis TF-källhänvisning och synliga CLI-underrubriker rättade. Slutlig helsvit: **1090 passerar, 1 livetest bortvalt, 642.79 s**, utan ANTHROPIC_API_KEY och RISKANALYS_SCB_API_KEY. Regelbasvalidering, compileall och git diff --check passerar. Första sviten under pågående bygge gav 1059 passerar/5 fel; en senare körning avbröts när en äldre integrationsförväntan behövde anpassas till kravet på effektunderlag. Felen omfattade tidigare laddad fixture/version samt saknad effekt i äldre sanktionsprov. Integrationsförväntan rättad och proven passerar; inga kontrollkrav eller spärrar försvagade. Den separata nya M2-CLI-kedjan gav 11 passerar, med syntetisk signering endast i testkopia, fastställelse och återställningsprov för tre länspaket.

**Kvarstår:** FATF:s TF-original gav HTTP 403 och är därför varken checksumregistrerat eller använt som ny katalogkälla. Original till domarna 12554-25, 842-26 och 1129-26 saknas; ingen ny rättspraxis byggs ur referat. Verklig sakkunniggranskning, tjänstevis kalibrering av de byråövergripande indikatorerna, kontrollernas tillräckliga täckning och M3/M4-prov återstår. Alla nya poster är `ej_granskad`; tekniskt gröna tester är inte juridiskt godkännande.

**För granskning:** ett enbart syntetiskt Word-utkast och provresultat ligger utanför repot i `../underlag/kallkontroll-2026-10-11/`. Nya ogranskade granskningsunderlag för regelbas 1.2.0 är framställda för alla tre länspaket i `../underlag/granskningsunderlag-1.2.0-2026-10-11/`; deras manifest verifierar. Ingen mall är signerad. Inga riktiga byrådata eller riktiga API-anrop användes i testerna.
