# Katalogluckor inför komplettering av regelbasen

**Steg A, 23 oktober 2026. Förslag för användarens granskning före steg B.**

Inventeringen utgår från den godkända del 1, commit `654066fdd6fb1b0b1bf071cc0fec02a171e5a5b4`, och regelbas **2.0.0**. Arbetet ligger på den nya lokala grenen `codex/regelbas-inventering`. Kod, tester, regelbas, risknivåer, sakkunnigstatus och frysta rapportpaket är oförändrade. Ingen push eller merge.

Katalogerna behöver kompletteras, men flera kandidater täcks redan delvis. De tydligaste luckorna är fem av lagens exempel på högre kundrisk, uppgift om bristande identifiering på distans och fem indikatorer på potentiellt lägre risk. Därutöver behövs mer precisa tjänsteavgränsningar och beskrivningar av vissa tillvägagångssätt. En generell hotrubrik eller en fråga i formuläret räknas inte ensam som fullständig täckning: även beskrivning, underlag och koppling till berörd tjänst måste stämma.

Ingen rekommendation nedan är ett sakkunnigbeslut. Steg A bedömer **innehåll och täckning**. Viktning, automatisk aktivering, trösklar, kombinationer och kontrollsänkningar avgörs i steg B–D enligt uppdragets ordning. **Steg B har inte påbörjats.**

## 1. Underlag och läsanvisning

Uppdraget är revision 3 av `2026-10-23-uppdrag-codex-r4-r7-och-regelbas.md`; regelbasförslaget är revision 2 av `2026-10-23-forslag-regelbas-infor-sakkunniggranskning.md`, båda i den andra klonens `docs/superpowers/reviews/`. Användarens senaste instruktion godkänner del 1 och avgränsar denna leverans till steg A.

Följande källor har lästs i de angivna delarna. **PDF-sida betyder den fysiska sidan från 1**, även när tryckt sidnummer skiljer sig. Lag hänvisas med kapitel och paragraf; webbsidor med rubrik. Käll-ID avser befintligt `regelbas/kallor.yaml`. Länkar och kontrollsummerade PDF-filer är bevarade i det lokala, ignorerade evidensarkivet `.superpowers/evidens/2026-10-23-katalogluckor/kallor/`.

| Källa | Lästa delar och användning |
|---|---|
| `SRC-PTL` | [PTL hos Riksdagen](https://www.riksdagen.se/sv/dokument-och-lagar/dokument/svensk-forfattningssamling/lag-2017630-om-atgarder-mot-penningtvatt-och_sfs-2017-630/), 2 kap. 1–5 §§, jämfört med repots källtext; 1 kap. 2 och 4 §§ för tjänsteavgränsningar. Webbtexten anger ändringar t.o.m. SFS 2026:1075 och visar även framtida lydelse av 1 kap. 2 §. Den framtida lydelsen används inte som dagens grund. |
| `SRC-14FS-2024-11`, `SRC-12FS-2024-8`, `SRC-01FS-2024-20` | Alla tre föreskrifternas 2 kap. 1–12 §§, PDF s. 1–4. Jämförda med respektive lokal källtext och kravposter. |
| `SRC-LST-GOR-ARB` | [Gör en allmän riskbedömning](https://www.lansstyrelsen.se/skane/samhalle/betalning-ekonomi-och-pengar/forhindra-penningtvatt-och-finansiering-av-terrorism/gor-en-allman-riskbedomning.html), hela sakdelen från inledningen till frågorna om utvärdering och spridning. |
| `SRC-VAGL-2025-03` | [Information till redovisningskonsulter och skatterådgivare](https://polisen.se/siteassets/dokument/om-polisen/penningtvatt/vagledning-till-redovisningskonsulter-och-skatteradgivare.pdf), mars 2025, PDF s. 1–28. Tjänster s. 4–6, skyldigheter s. 8–15, modus s. 16–17, varningssignaler s. 18–25, rapportering s. 26–27. |
| `SRC-NRA-2024-25` | Nationell riskbedömning 2024/2025, avsnitt 7.19 s. 122–125, 7.20 s. 126–128, 7.23 s. 138–139, 7.25 s. 144–146, 7.26 s. 147–148 och 7.27 s. 149. Dessa är sektorerna för tjänstekatalogen och identifierade avgränsningsfrågor. Övriga sektorer är inte fullständigt inventerade. |
| `SRC-TS-2026-14` | Erfarenheter från länsstyrelsernas penningtvättstillsyn, s. 8–11: relationer, kanaler, geografi, organisation och motiverad värdering. |
| Lägesbilder | Lästa avsnitt och täckning redovisas källvis i avsnitt 6. Det är inte ett påstående om genomläsning av varje sida i alla rapporter. |

Inventeringen har också kontrollerat den lokala kravsammanställningens 36 punkter och MCon-exemplets avsnitt 1–6. De används som exempel och avstämning, inte som rättslig eller empirisk grund för nya poster. Privata dokument och eventuella byråuppgifter kopieras inte till repot.

### Två källavvikelser att hantera

1. Vägledningens fotnot på PDF s. 2 anger **01FS 2024:53**. Den hämtade föreskriften och [Stockholms aktuella myndighetssida, Föreskrifter och allmänna råd](https://www.lansstyrelsen.se/stockholm/samhalle/betalning-ekonomi-och-pengar/forhindra-penningtvatt-och-finansiering-av-terrorism.html) anger **01FS 2024:20**, med giltighet från 1 juli 2024. Inventeringen följer den lästa primärföreskriften och uppdragets 2024:20. Ingen oidentifierad 2024:53 införs; avvikelsen ska framgå i sakkunnigunderlaget.
2. Den nu nedladdade `SRC-EUROPOL-TESAT-2025` har SHA-256 `97a34c80ae0f8fcb6bd5527c620fb21358820a4c7b541839cc4bd1bee7d666aa`, medan registret anger `0a18061235353efda54b433510f4ff20a19fca4b8933b00578f4d6f3045ef3f6`. PDF s. 31/41 har lästs i **den nu hämtade filen**. Den används bara som kompletterande kontext här; svenska primärkällor bär förslagen. Orsaken till byteavvikelsen är inte fastställd. Steg B behöver bevara och identifiera rätt version innan ändrade katalogposter hänvisar till den. Övriga 20 hämtade PDF-filer matchar registrerad kontrollsumma. Registret är inte ändrat i steg A.

## 2. Vad som faktiskt finns

| Objekt | Baslinje |
|---|---|
| Tjänster | 11: `T-RED-01`–`07`, `T-SKATT-01`, `T-BOLAG-01`–`03` |
| Hot | 21: `H-01`–`03`, `H-TJ-01`–`11`, `H-MOD-01`–`04`, `H-TF-01`–`03`; alla har `niva: medel` |
| Sårbarheter | 28: sex grund-/kombinationsposter, fyra tjänsteposter och `S-ARB-01`–`18` |
| Kontroller | 13; bland annat bankavstämning, en per befintlig tjänst och sanktionskontroll |
| Krav | 107 över kravfilerna; lagen 2:1–5 och samtliga tre regionala 2 kap. finns representerade |
| Profilfält | **371 fält, varav 324 med intagsmetadata**. 371 är alltså inte antalet separata frågor som visas i intaget. Härledda andelar och kompatibilitetsfält ingår i totalen. |

Kontrollerade filer: `regelbas/kataloger/{tjanster,hot,sarbarheter,kontroller}.yaml`, `regelbas/falt.yaml`, `regelbas/krav/`, regionala `regelbas/regelpaket/`, `regelbas/beslutstabeller/sanktionsrisk.yaml` samt källregister och källtexter. Befintliga kravposter är inte detsamma som fungerande katalogindikatorer eller en verifierad efterlevnad hos en byrå.

Viktiga återanvändbara uppgifter:

- `P-VERK.trust` och `P-VERK.nominell_aktieagare` finns redan som frågor om **byråns tjänster**. De beskriver inte kundens egenskaper enligt PTL 2:5 p. 3–4.
- `P-GEO.sanktionsanknytning` finns för kund-, ägar- eller transaktionsanknytning. Den driver den separata, ogranskade sanktionsdimensionen `BT-SANK-01`/`02` och kontrollen `C-SANK`. Den anger inte särskilt kundens hemvist enligt PTL 2:5 p. 7.
- Antal kunder, geografiska antal, riskbransch, kontanthantering och vissa tjänstevisa antal finns. Ägares nationalitet/placering är inte kundens hemvist, och utlandstransaktioner är inte heller ett hemvistmått.
- `P-TJ.<tjänst>_{arbetssatt,kundtyper,kanaler,geografi,ovriga_risker}` finns. Befogenheter anges även i `attest`, `betalningsmandat` och `bankinsyn`. Fritext kan återges och prövas lokalt, men ska inte tolkas av AI till ett nytt beslutsvärde.

## 3. PTL 2 kap. 1–5 §§ och regionala föreskrifter

### Allmänna krav och avgränsning mot kundrisk

| Källa | Motsvarighet och slutsats |
|---|---|
| PTL 2:1 | `KRV-PTL-2-1`, tjänste-/hot-/sårbarhetskatalogerna, tjänstebeskrivningar, egna iakttagelser och `P-BEVAKNING.*`. **Befintlig struktur, innehållsluckor enligt nedan.** Antal egna rapporter ensamt beskriver inte lärdomarna; använd befintliga tjänstevisa avvikelser och bevakningsrelevans, utan kundnamn eller rapportdetaljer. |
| PTL 2:2 | `KRV-PTL-2-2`, organisationsuppgifter och dokument-/utvärderingsavsnitt. **Ingen ny katalogpost.** Omfattning, motiveringar och koppling till åtgärder måste kontrolleras i den kommande rapporten. |
| PTL 2:3 | `KRV-PTL-2-3`, kundmallens mål. **Ett annat bedömningsobjekt än allmän tjänsterisk.** Detta uppdrag bygger ingen individuell kundriskmotor och får inte härleda antal kunder per riskklass ur allmänna riskfaktorer. |
| PTL 2:4–5 | `KRV-PTL-2-4`/`5` finns som kravtext. **Delvis katalogtäckning** enligt de två fullständiga punktmatriserna nedan. Överföring från kundegenskap till allmän tjänsterisk kräver metodmotivering och tjänstevis relevans. |

### Fem indikatorer på potentiellt lägre risk

Källa för varje rad: `SRC-PTL`, 2 kap. 4 § med angiven punkt. **Ny indikator som data, utan nivåeffekt i steg B.** Frånvaro av en riskfaktor, svensk adress eller ett okänt svar får inte ersätta positivt underlag. Ett registrerat värde ska ha period, underlag och datum enligt intagets befintliga beläggshantering.

| Punkt och indikator | Täckning i dag | Föreslaget underlag i formuläret |
|---|---|---|
| 1. Offentlig kund eller rättsligt bestämmande offentligt inflytande | Ingen egen indikator. Fritext om kundtyper är inte typat underlag. | Antal aktiva kunder som uppfyller den fullständiga definitionen; även direkt/indirekt och gemensamt inflytande omfattas. |
| 2. Kundens hemvist inom EES | Saknas. Ägar- och transaktionsandelar mäter annat. | Antal aktiva kunder med styrkt hemvist inom EES. |
| 3. Hemvist i stat med motsvarande **och effektivt tillämpade** AML/TF-bestämmelser | Saknas. `S-ARB-13 = nej` bevisar inte detta. | Antal kunder för vilka båda villkoren dokumenterats, med bedömd stat och daterad källa i underlaget. |
| 4. Hemvist i stat med låg korruption **och annan relevant brottslighet** | Saknas. `S-ARB-12 = nej` räcker inte. | Antal kunder för vilka båda delarna styrkts; ingen automatisk landlista föreslås. |
| 5. Överlåtbara värdepapper på reglerad EES-marknad eller motsvarande utanför EES | Saknas. Generellt börsnoterad är för oprecist. | Antal kunder som uppfyller marknadsvillkoret, med marknad och underlag. Definitionen får inte begränsas till aktier eller utvidgas till alla handelsplattformar. |

Samma kund kan förekomma i flera rader. Antalen får inte summeras till unika lågriskkunder. Samtliga fem indikatorer ska få en egen presentation och prövning, skild från hotförstärkande faktorer. Relevans, överlapp och dubbelräkning med kontroller hör till steg D.

### Tio exempel på potentiellt högre risk

Källa för varje rad: `SRC-PTL`, 2 kap. 5 § med angiven punkt. **Ny post** betyder rekommenderad komplettering i steg B; det betyder inte automatiskt nivån hög.

| Punkt och företeelse | Slag och täckning i dag | Förslag och frågor |
|---|---|---|
| 1. Ovanlig eller alltför komplicerad ägarstruktur i förhållande till verksamheten | Kundindikator: `S-ARB-03`, `P-RISK.komplex_agare`. | **Redan täckt**, precisera frågehjälpen med verksamhetens behov. Ingen ny fråga. Normal koncernstruktur är inte ensam grund. |
| 2. Kontantintensiv verksamhet | Kundindikator: `S-KUND-02`, antal/andel kontantkunder. Villkoret använder 10 procent. | **Täckt med metodbegränsning.** Även förekomst under tröskeln ska framgå. Behåll frågorna; pröva andel, antal och tjänstevis fördelning i D9. |
| 3. Nominella aktieägare eller andelar på innehavaren | Kundindikator: dolda företrädare i `H-MOD-03` och komplexitet i `S-ARB-03` täcker mekanismen delvis. Ingen uttrycklig faktor. Byråfrågan `P-VERK.nominell_aktieagare` avser ett annat sakförhållande. | **Ny post** för kundegenskapen med en gemensam förekomstfråga som uttryckligen omfattar båda alternativen, belagd med underlag. Koppla till dolda ägare, ägarutredning och relevanta transaktionshot. |
| 4. Juridisk person/trust/liknande konstruktion för en viss fysisk persons tillgångar | Kundindikator: komplexitet och utländskt ägande täcker inte ändamålet; `P-VERK.trust` avser byråns förvaltning. | **Ny post och en fråga** om kundens konstruktion och ändamål. Ett vanligt holdingbolag klassas inte automatiskt enbart utifrån namnet. |
| 5. Hemvist där effektiva AML/TF-system saknas | Geografisk kundindikator: `S-ARB-13`, `P-RISK.svagt_aml`. | **Redan täckt i huvudsak**; frågehjälpen ska omfatta ineffektiv tillämpning, inte bara avsaknad av lagtext. Dokumentera hemvist och bedömningskälla i befintligt underlag. |
| 6. Hemvist med betydande korruption och annan relevant brottslighet | Geografisk kundindikator: `S-ARB-12`, `P-RISK.korruption`. Frågan nämner bara korruption. | **Ändrad post och frågehjälp** för hela lagtextens relevanta omständigheter. Ingen ny parallell ja/nej-fråga föreslås. |
| 7. Hemvist i stat under sanktioner, embargo eller liknande | Geografisk kundindikator: separat sanktionsprövning finns, men ingen motsvarande AML-faktor. Bred anknytning är inte samma sak som hemvist. | **Ny post och en precis hemvistfråga**. Återanvänd den befintliga breda anknytningen i sanktionsdimensionen; ställ inte den igen. Förklara skillnaden och undvik dubbelräkning. Inga listträffar eller förbud beslutas av faktorn. |
| 8. Hemvist i stat som finansierar/stöder terrorism eller där terroristorganisationer verkar | Geografisk kundindikator: `S-ARB-11` och `H-TF-02` är närliggande men har andra definitioner. | **Ny post och en fråga** med daterad källbedömning. EU-högrisktredjeland och transitland får inte likställas med detta kriterium. |
| 9. Distans utan tillförlitlig identitetssäkring | Kanalindikator: `S-ARB-08`, `P-RISK.utan_mote` och andel utan möte mäter bara fysisk frånvaro. | **Ändrad post samt en kompletterande fråga** om distansrelationer eller distanstransaktioner där tillförlitlig identitetssäkring saknas. Behåll uppgiften om leveranskanal. Kontrollens existens är inte bevis för säker identifiering i varje relevant fall. D9 måste pröva nivåeffekten. |
| 10. Varor/tjänster betalas av okänd eller någon utan koppling till kunden | Betalningsindikator: `H-03`, `H-MOD-01` och ombudsfrågan täcker delar, men varken felbetalning eller ombud är liktydigt med tredjepartsbetalning. | **Ny post och en fråga** om sådana betalningar i byråns uppdrag eller kundernas relevanta flöden. Underlag ska skilja dessa från kända betalningsförmedlare och förklarliga koncernbetalningar. |

### Föreskrifternas hela 2 kapitel

Jämförelsen avser 2 kap. i **samtliga tre** `SRC-14FS-2024-11`, `SRC-12FS-2024-8` och `SRC-01FS-2024-20`, PDF s. 1–4. De har motsvarande ämnesindelning och paragrafnummer här. Regionala lydelser finns redan bundna till kravposterna; en gemensam tabell betyder inte att bara en föreskrift lästs.

| Paragraf | Befintlig motsvarighet | Katalogslutsats |
|---|---|---|
| 1 | `KRV-LSF-2-01` | Dokumentkrav; ingen ny hot-/faktorpost. |
| 2 | `KRV-LSF-2-02` samt `KRV-LSF-001`–`005` | Tjänster, relevanta hot, egna rapporter, sårbarheter och motiverad värdering. Kompletteringar i avsnitt 3–7. |
| 3 | `KRV-LSF-2-03`, dokumentavsnitt `D-ARB.10`, mål `DRIFT-UTVARDERING` | Årlig utvärdering, ändringsutvärdering i förväg och datum. Ingen ny faktor. Rapportens datatäckning och nästa granskning måste verifieras i del 3. |
| 4 | `KRV-LSF-2-04`, kundmall `KM-C` | Kundprofil hålls isär från allmän tjänsterisk; punktmatriserna ovan visar dataluckorna. |
| 5 | `KRV-LSF-2-05` | Rutiner/KYC, uppgiftslämning, bevarande, intern kontroll är krav- och rutinobjekt; inte fyra nya hot. |
| 6 | `KRV-LSF-2-06` | Personalrutiner och skydd. Organisatorisk prövning finns; ingen automatisk risk av att ha anställda. |
| 7 | `KRV-LSF-2-07` | Verksamhetsanpassade handlingsregler; knyt åtgärder till relevanta scenarier och senare rutinavsnitt. |
| 8 | `KRV-LSF-2-08` | Utvärdering och datum för rutiner; inte ny faktor. |
| 9 | `KRV-LSF-2-09` | Lämplighet och arbetsuppgifter. Kontrollbrister hanteras som belägg/åtgärdsbehov, inte ett schablonhot. |
| 10–11 | `KRV-LSF-2-10`/`11`, `S-ARB-15`, `S-VERK-01` | Utbildning/kompetens och utbildningsdokumentation finns representerade. Två års erfarenhet är ett befintligt metodval, ingen gräns i föreskriften. |
| 12 | `KRV-LSF-2-12` | Skydd och återföring av erfarenheter. Befintlig fritext om verksamhetsbrister/avvikelser kan bära lokala lärdomar; ingen separat generell PT/TF-hotpost för hot mot personal föreslås. |

Detta är en kontroll av regelrepresentation och katalogbehov. Den intygar inte att varje rutin redan är införd eller fungerar hos en verklig byrå.

## 4. Tjänster och avgränsningar

### Vägledningens tjänster och befintliga tjänster

Förkortningar i tabellen: **V** = `SRC-VAGL-2025-03`, **N** = `SRC-NRA-2024-25`. Varje rad anger sida/avsnitt. En hänvisning till en sektorsbeskrivning ger inte i sig stöd för en viss riskpoäng.

| Tjänst eller arbetsmoment | Källa | Täckning och förslag | Formulär |
|---|---|---|---|
| Löpande affärshändelser, reskontra, avstämning | V s. 5; N 7.19 s. 122–123 | **Täckt:** `T-RED-01`/`H-TJ-01`. | Befintliga red01-fält. |
| Årsbokslut och årsredovisning | V s. 5; N 7.19 s. 122–123 | **Täckt:** `T-RED-02`/`H-TJ-02`. | Befintliga red02-fält. |
| Skattedeklarationer och deklarationsombud | V s. 5–6; N 7.19 s. 122 och 7.20 s. 126 | **Täckt:** `T-RED-03`/`H-TJ-03`. | Befintliga red03-fält, även kundtyp dödsbo. |
| Skatteberäkning, redovisning, råd/tolkning och materiellt bistånd | V s. 6; N 7.20 s. 126–128 | **Täckt/preciseras:** red03 för deklarationsarbete, `T-SKATT-01`/`H-TJ-08` för övrigt. Strukturering vid förvärv/fusion/utköp behöver stå i arbetsmomenten. Laglig planering likställs inte med missbruk. | Befintlig uppdragsbeskrivning, kundtyper och geografi. Ingen ny dubbel fråga. |
| Revision som står under länsstyrelsens tillsyn; granskning/due diligence, internrevision, ej lagstadgad rapportgranskning | V s. 4–5; N 7.19 s. 122 | **Ny tjänstepost föreslås.** Dessa granskningsuppdrag är inte bokslutsproduktion eller vanlig CFO-rådgivning. Auktoriserad/godkänd revision och RI-tillsyn ska avgränsas. Preliminärt `T-RED-09`, se beslut nedan. | Ny tjänstegren med villkorade uppdrags-/exponeringsfrågor. Befintlig övergripande fråga om bokföring/revision räcker inte för att avgöra erbjudandet. |
| Företräda kund i rättsligt skatteförfarande/bedöma rättslig situation | V s. 10–11 | **Undertyp och rättslig avgränsning**, inte ett nytt hot eller generell dispens. Använd `T-SKATT-01` och befintlig beskrivning; kraven `KRV-PTL-3-1` och `KRV-PTL-4-8` måste följa rätt uppdrag. | Förtydliga befintlig frågehjälp, ingen ny fråga i förslaget. |
| Lönehantering | N 7.19 s. 123; `SRC-BRA-2025-20` s. 90–91 | **Täckt:** `T-RED-04`/`H-TJ-04`; komplettera exempel på falska löneuppgifter. Mandat/insyn prövas i D1–D2. | Befintliga red04-fält. |
| Betalning och attest åt kund | N 7.19 s. 123 | **Täckt:** `T-RED-05`/`H-TJ-05`. | Befintligt betalningsmandat, attest och bankinsyn. |
| Klientmedelskonto | N 7.19 s. 123 | **Täckt:** `T-RED-06`/`H-TJ-06`. Ett klientmedelskonto är inte ett vanligt betalningsmandat. | Befintliga red06-fält. |
| Ekonomisk rådgivning/CFO | N 7.19 s. 123–124 | **Täckt:** `T-RED-07`/`H-TJ-07`. Precisa befogenheter krävs; all rådgivning innebär inte egen tillgångsförvaltning. | Befintliga red07-fält. |
| Bolagsbildning, lager-/historikbolag och bolagsförmedling | N 7.25 s. 144–146 | **Täckt:** `T-BOLAG-01`, `H-TJ-09`, `H-MOD-03`. Förtydliga snabbavveckling som kan bli vidareförsäljning av historikbolag. | Befintliga bolag01-fält. |
| Registrerad adress, kontors-/postadress och digital posthantering | N 7.26 s. 147–148 | **Täckt:** `T-BOLAG-02`/`H-TJ-10`; precisera digital vidarebefordran som arbetsmoment. | Befintliga bolag02-fält. |
| Styrelse-/företrädarfunktion på tredje mans vägnar | N 7.27 s. 149 | **Ändrad post:** `T-BOLAG-03`, `H-TJ-11`, `S-TJ-04`. Vanlig egen styrelseledamot får inte likställas med denna yrkesmässiga tjänst. N anger utlandsavgränsning och att sektorn inte bedömts. | Precisera befintlig erbjudandefråga och avtals-/geografibeskrivning. Äldre breda ja-svar måste omprövas, inte automatiskt återanvändas. |

### Övriga kandidater

| Kandidat och slag | Källa med locator | Täckning i dag och rekommendation | Frågor som behövs |
|---|---|---|---|
| Fakturering för kunds räkning, arbetsmoment | PTL 2:1; N 7.19 s. 123; V s. 16 | Reskontra i red01 och `H-01` täcker mycket, men fakturautställande är inte uttryckligt. **Ändra red01:s arbetsmoment och koppla H-01 tydligt.** Ingen separat tjänst föreslås när samma redovisningsuppdrag omfattar momentet. Separat försäljning av factoring är något annat. | Befintlig red01-arbetssättsfråga med uttrycklig hjälp om att upprätta/skicka fakturor och behörighet. |
| Ansökningar om ROT/RUT och andra offentliga utbetalningar, tjänst | PTL 2:1; `SRC-MYND-OB-2025` s. 20–21; `SRC-BRA-2025-20` s. 90–91 | Deklarationer, fakturor och lön ger **delvis** täckning. En fristående ansökningstjänst behöver kunna identifieras utan att deklarationstjänst påstås. **Ny tjänst föreslås**, preliminärt `T-RED-08`. ROT/RUT är ett föreslaget arbetsmoment, inte ett påstående att den lästa lägesbilden uttryckligen räknar upp just dessa system. | Ny tjänstegren. Frågehjälp skiljer underlagsframtagning, ansökan/ombud och betalningsmandat. |
| Föreningar, kundtyp respektive förvaltningstjänst | `SRC-FIPO-TF-2025` s. 2/4; PTL 2:1 | Ideella kunder finns i `P-RISK.ideell`/`S-ARB-05`; föreningar kan köpa flera befintliga tjänster. **Redan täckt som kundtyp, förtydliga per tjänst.** Ingen ny tjänst enbart för associationsformen. Ekonomisk förening/BRF är inte automatiskt ideell insamlingsverksamhet. | Befintliga kundtyps- och arbetsmomentssvar. Faktisk förvaltning/mandat ska beskrivas, inte antas av namnet. D7 avgör PT/TF-effekt. |
| Dödsbon, kundtyp | PTL 2:1; V s. 6 om skattearbete för privatpersoner | Deklaration/skatteråd/bokföring kan beskrivas i befintliga tjänster. **Medvetet ingen generell dödsbofaktor eller egen tjänst.** De lästa källorna belägger inte att kundtypen ensam innebär förhöjd risk. | Befintlig kundtyp och uppdrag. Rättslig boutredning/förvaltning utanför tjänsternas beskrivning får inte kallas analyserad genom deklarationsfrågan. |
| Trustförvaltning, byråtjänst | PTL 1:4 andra stycket p. 4; N 7.23 s. 138–139 | `P-VERK.trust` finns men ingen egen tjänst med exponering. **Ny tjänst föreslås**, preliminärt `T-BOLAG-04`, om paketens redan breda bolagstjänsteomfattning ska bestå. Kundens förvaltningskonstruktion i 2:5 p. 4 är en separat faktor. | Återanvänd erbjudande från `P-VERK.trust`; nya villkorade tjänsteuppgifter. Underlaget stödjer anonymitets-/insynsrisk, men inga kända svenska modus eller exakta hotnivåer ska hittas på. |
| Nominell aktieägare/arrangera funktionen, byråtjänst | PTL 1:4 andra stycket p. 5; N 7.27 s. 149 | `P-VERK.nominell_aktieagare` finns men ingen egen tjänst. **Ny uttryckligt avgränsad tjänst föreslås**, preliminärt `T-BOLAG-05`, för relevant utlandsuppdrag. Alternativet är dokumenterad avgränsning med synligt stopp vid ja-svar, inte att behandla det som vanlig bolagsbildning. | Återanvänd befintligt erbjudandesvar; villkorade tjänsteuppgifter och rättslig/geografisk avgränsning. |
| Factoring, bank-/betaltjänst eller egen kryptotillgångstjänst, separat verksamhet | N 7.19 s. 123 och PTL 1:2 | **Medvetet utelämnade som egna tjänster i redovisningspaketen.** En integrerad lösning kan skapa kund-/kanalexponering, men gör inte byråns redovisning till bankverksamhet. Annan reglerad verksamhet kräver rätt paket och separat avgränsning. | Befintliga arbetsmoment, mandat, kanaler och övriga risker används för redovisningsdelen. Ingen fråga får dölja att annan utförd verksamhet saknar analysstöd. |

**Rekommendation inför B:** pröva de fyra nya tjänsteposterna uttryckligen vid granskningen. De är inte fyra automatiskt konstaterade tjänster hos byrån. Om trust/nominell aktieägare avgränsas bort måste ja-svar hanteras öppet som utanför analysstödet; i denna inventering lämnas de därför inte tyst utan motsvarighet. De föreslagna ID-numren är arbetsnamn och finns ännu inte i regelbasen.

## 5. Hot och varningssignaler i marsvägledningen

Följande är en täckningsmatris mot `SRC-VAGL-2025-03`, inte en kopia av varningslistorna. En varningssignal är inte bevis för brott och behöver inte bli ett eget hot. Befintliga fritextsvar om avvikelser används där inget nytt beräkningsvärde behövs.

| PDF-sidor och företeelser | Motsvarighet | Förslag/frågebehov |
|---|---|---|
| 3/14: dölja brottsursprung respektive finansiera terrorism med även legala medel | `H-01`–`03`, `H-TF-01`–`03` | Täckt som skilda syften. Inga nya frågor. |
| 16: felbetalning till annat återbetalningskonto | `H-MOD-01`, `H-TJ-05`, `H-03` | Täckt. |
| 16: osanna/falska fakturor | `H-01`, `H-TJ-01`, `H-MOD-02` | Täckt; fakturautställande förtydligas enligt avsnitt 4. |
| 17: målvakter och bolagsbyten | `H-MOD-03`, `S-ARB-03`/`06`/`07`/`09` | Täckt, behåll skillnaden verklig och formell företrädare. |
| 17: gränsöverskridande skiktning | `H-03`, `H-MOD-04`, `S-GEO-01` | Delvis; förtydliga även långsamma/komplexa kedjor, inte bara snabba flöden. |
| 17: brottsmedel som försäljning, därefter lön/utdelning | `H-02`, `H-TJ-01`/`04` | Täckt; lön och utdelning i beskrivningen. |
| 18–19: identitet/adress/ID-underlag; distans/ombud | `S-ARB-08`/`09`, kanalsvar och kundkännedomsrutiner | Distansändring enligt 2:5 p. 9. Övrigt frågehjälp/lokala avvikelser. |
| 18–19: PEP, högrisktredjeland, kortlivade företag, bulvaner, utländska företrädare | `S-ARB-02`/`04`/`06`/`11`, `H-MOD-03` | Befintliga indikatorer; undvik att enbart utländsk bosättning blir ett brottspåstående. |
| 18–19: domstolsbeslut, varningslistor, utomstående företrädare | KYC/rutinprövning, `H-MOD-03`, tjänstevis `ovriga_risker` | Exempel i hjälpen. Ingen generell faktor för att någon nämns i ett beslut/lista utan relevansprövning. |
| 19–20: onormalt belopp/frekvens/motpart/syfte, snabba flöden, saknade driftkostnader | `H-03`, `H-MOD-04` | Förtydliga befintliga beskrivningar; ingen separat fråga per signal. |
| 19–20: anonymitet, virtuella betalmedel, valuta, strukturering | `H-03`, `H-MOD-04`, TF-delen i `H-TF-02` | PT-krypto behöver konkretiseras, se avsnitt 6. |
| 19–20: investeringar/prisavvikelser, belåning, lån, apport, förtida återköp, tredje parts konto | `H-03`, `H-TJ-02`/`07`; delvis `H-MOD-01` | Ändra exempel/hotkopplingar. Ny betalningsindikator enligt 2:5 p. 10; inga påhittade beloppsgränser. |
| 20: mellanhänder, utlandsstrukturer, skalbanker | `S-ARB-03`/`04`/`09`/`13`, `H-03`, `H-TJ-08` | Täckt som mekanismer; skalbanksexemplet är kundens flöde, ingen erbjuden byråtjänst. |
| 21–22: oförklarade tillskott/lån, kontanter, orimliga resultat, kort bolagsliv, strukturer/byten, interna överföringar | `H-01`–`03`, `H-MOD-03`/`04`, `S-KUND-02`, `S-ARB-03`/`06`/`07` | Förtydliga beskrivningar och tjänsterelevans. |
| 21: misstänkta förmåner, flera/byten av rådgivare, inga väntade anställda | Organisatoriska kontroller, `S-ARB-01`/`17`, tjänstevis avvikelsesvar | Förmåner är inte identiskt med nära relation/kundberoende. Lägg exempel för lokal prövning; ingen automatisk faktor eller beloppsgräns föreslås. |
| 22: offshorearvoden, garantier, högriskkoppling, onödiga utlandsbolag/konton, omotiverad förvaltning och förlustaffärer | `H-03`, `H-TJ-07`/`08`, `S-ARB-03`/`04`/`11`/`13` | Precisera uppdragsexempel. Kundens förvaltningsändamål får egen indikator enligt 2:5 p. 4. |
| 23–24: saknade/motsägande underlag, verksamhetsavvikelser, fiktiv leverans, fakturafel, karusell, skulder, ospecificerade tjänster, felaktiga transaktioner | `H-01`/`03`, `H-MOD-02`, `H-TJ-01`/`02`/`03` | Täckt genom befintliga hot och lokala underlag; karusell kräver konkret leverans-/momssamband. |
| 25: undvikande eller orimliga förklaringar, svag kunskap, kontrollintresse, resor/privatekonomi, privata konton och kontaktbrister | KYC/rutinprövning, tjänstevis avvikelsesvar och `H-03`; ibland `H-MOD-03` | Frågehjälp och mänsklig relevansprövning. Ingen generell faktor för resor, privatekonomi eller kunskapsnivå föreslås. |
| 8–13/26–27: rutiner, utbildning, skydd, bevarande, övervakning/rapportering | Kravkatalog, kontrollobjekt, `P-VERK.goaml`, `P-VERK.spridning` | Skyldigheter och rutiner; inga nya tjänstehot enbart för att skyldigheten finns. |

Samtliga tjänstetyper i vägledningens s. 4–6 och de namngivna modusen på s. 16–17 har därmed en motsvarighet eller ett uttryckligt kompletteringsförslag. Varningslistorna s. 18–25 har dessutom prövats gruppvis ovan. Listan blir inte en automatisk kundscreening.

## 6. Nationell riskbedömning och registrerade lägesbilder

| Källa och läst avsnitt | Täckning i dag | Föreslagen åtgärd |
|---|---|---|
| `SRC-NRA-2024-25`, 7.19 s. 122–125 | Fakturor, felbetalningar, skenintäkter, svart lön, möjliggörande, klientmedel och kombinerade tjänster finns huvudsakligen i `H-01`–`03`, `H-TJ-01`–`07`, `H-MOD-01`–`04`. | Behåll befintliga modus, precisera arbetsmoment och kopplingar; lägg till granskningsuppdrag enligt avsnitt 4. Osanna fakturor/falska underlag nämns även för TF på s. 125. Pröva koppling till TF-hot; inte bara till PT. |
| Samma källa, 7.20 s. 126–128 | `H-TJ-08`/`H-MOD-03` täcker dolda strukturer. `H-TF-02` täcker hawala men har TF-ändamål. | Komplettera PT-beskrivningen för rådgivning som möjliggör underground banking; TF-hotet får inte ensamt anses täcka PT. Avsaknad av kända svenska TF-modus på s. 128 betyder inte nej eller ingen risk. |
| Samma källa, 7.23 s. 138–139; 7.25 s. 144–146; 7.26 s. 147–148; 7.27 s. 149 | Trust/nominee saknar tjänsteposter; övriga bolag/adressposter finns. | Avgränsningar och förslag i avsnitt 4. Okänt modus eller ej bedömd TF får inte fyllas med egna sakpåståenden. |
| `SRC-FIPO-FORETAG-2026`, s. 1–6, särskilt 2–4 | `H-MOD-03` täcker förbrukningsbolag; `H-01`–`03`/`H-TJ-02` täcker även legitimerande underlag och övervärden. | Förtydliga långlivade bolag, koncernlån/tillskott och cirkelfakturering. Enbart kort bolagsliv får inte bli hela hotbeskrivningen. **Nytt PT-modus föreslås** för företagsflöden via krypto som döljer ursprung; se nedan. |
| `SRC-FIPO-SWISH-2025`, s. 1–4 | `H-MOD-04`, `H-02`, `H-TF-01`/`02`. | Befintliga poster täcker skiktning och blandning. Beskriv även andra direktbetalningar och fragmenterad insyn. Rapporteringstal kan inte räknas om till byråns hotfrekvens. |
| `SRC-FIPO-TF-2025`, s. 1–4 | `H-TF-01` insamling, `02` hawala/krypto/transit, `03` föreningar/bolag. | **Redan täckta hot.** Kontrollera kopplingar för alla tjänster där ändamålet kan döljas. Ideell form ensam avgör inte risknivån. D6/D7 kvarstår. |
| `SRC-FIPO-PLATTFORM-2026`, s. 1–3 | `H-02`/`03`, `H-MOD-04`, `H-TF-01`/`02` kan omfatta betalningar via plattformar. | **Ändra exempel och kopplingar** för virtuella gåvor, skins och PSP-led. Ingen egen byråtjänst som heter sociala medier. Koppla till bokföring/betalning/rådgivning när flödet faktiskt berör uppdraget. Begränsat bedömningsunderlag får inte bli en belagd frekvens. |
| `SRC-FIPO-AR-2025`, s. 9–11, särskilt s. 10 | Företags- och slussmodus finns. Separat sanktionsrisk finns, men katalogen beskriver inte hur redovisning/rådgivning kan hjälpa att dölja sanktionsanknutna transaktioner. | **Nytt avgränsat hotförslag** om dolda parter/transaktionskedjor vid kringgående av sanktioner. AR s. 10 belägger ämnets relevans, inte ett detaljerat byråmodus. Den tjänstevisa konkretiseringen ska märkas metodtolkning. Sanktionsförbud och listkontroll hålls kvar separat. |
| `SRC-FIPO-AR-2024`, s. 6–9 | Professionella penningtvättare, företagsmiljö och finansiella sårbarheter är redan representerade. | Kontext; ingen ytterligare post eller nivå härleds ur fokusområden eller aggregerad statistik. |
| `SRC-EBM-2025`, s. 18–21 och 26–27 | `H-01`–`03`, `H-MOD-03`, `S-ARB-03`/`04`/`06`/`07`. | Förtydliga både korta och långsiktiga bolagskedjor, falsk registertillit och möjliggörande i befintliga hot/uppdragsbeskrivningar. Ingen ny faktor för att ett bolag är aktiebolag. |
| `SRC-MYND-OB-2025`, s. 20–22 | Falska fakturor och dolda företrädare täcks; offentliga utbetalningsunderlag framgår inte tillräckligt av tjänster och hot. | **Nytt konkret hot föreslås**: oriktiga redovisnings-, löne- eller ansökningsunderlag möjliggör felaktiga offentliga utbetalningar och vidareföring av vinsten. Inte varje ansökningsfel är PT. |
| `SRC-BRA-2025-20`, s. 90–91 och 130–131 | Lön/fakturor/möjliggörande finns. | Stöd för samma offentliga-utbetalningshot, falska löneuppgifter och relevanta tjänstekopplingar. Ingen dubbel hotpost för samma kedja enbart därför att två myndighetskällor beskriver den. |
| `SRC-POLIS-UTSATTA-2025`, avsnitt 1.1–1.2, s. 5–6 | `S-ARB-14`, geografiska antal/andelar. | Behåll geografisk relevansprövning. Områdestyp, socioekonomi och brottsrisk hos enskild kund får inte likställas. Tröskeln hör till D9. |
| `SRC-NCT-2026`, s. 4–5 | Bakgrund för TF/geografi, inte en frekvensskala för redovisningsuppdrag. | Ingen ny hotnivå eller automatisk landklassning. Terrorhot mot Sverige är inte samma mätstorhet som risken att en tjänst används för TF. |
| `SRC-EUROPOL-TESAT-2025`, nu hämtad PDF s. 31/41, tryckt s. 30/40 | `H-TF-01`/`02` täcker insamling, legala/illegala medel och överföringskanaler. | Inga ytterligare poster. Byteavvikelsen i avsnitt 1 måste hanteras före katalogändring med denna källa. |
| `SRC-SMOB-2026`, PDF s. 72–73, tryckt s. 70–71 | Branscher, bolagsrelationer och professionella funktioner har befintliga motsvarigheter. | Kompletterande forsknings-/samverkansunderlag, **inte en myndighetsföreskrift**. Ingen egen faktor för yrkes- eller branschtillhörighet, och inga poäng från registerassociationer. |

De tre rekommenderade tillkommande modusposterna blir preliminärt `H-MOD-05` offentliga utbetalningar, `H-MOD-06` sanktionskringgående genom dolda parter/underlag och `H-MOD-07` krypto i företagsflöden för att dölja brottsursprung. Numren reserveras inte i denna dokumentationsleverans.

För krypto räcker inte rubriken kryptotillgångar. Kedjan ska beskriva **vilken tjänst som utnyttjas**, exempelvis bokföring/avstämning av företagsmedel som förs via kryptoväxling och återkommer med oklar ursprungsförklaring. Källan beskriver företagskonton/kryptoplånböcker och utlandsled; den bevisar inte ett specifikt kundfall. Påstådda kryptovinster som förklaring till tillskott kan stå som **prövningsexempel/metodtolkning**, inte citeras som observerat modus i källan. `H-TF-02` kvarstår för TF-ändamålet. Ingen ny generell ja/nej-fråga om alla kunders kryptoinnehav föreslås; tjänstens befintliga uppdrags-/avvikelsesvar och hotobservation används.

### Kopplingar som måste prövas även utan nya poster

- `H-01`/`H-MOD-02` och fakturarelaterade TF-scenarier behöver granskas mot redovisnings-, löne-, deklarations- och rådgivningsuppdrag. En fakturakedja är inte relevant för lön bara för att samma byrå bokför; mandat och insyn avgör D1–D3.
- `H-TF-03` är i dag kopplat till skatt/bolag men inte alla redovisningstjänster. Ideell kundindikator, redovisat ändamål och insamling måste kunna prövas i rätt tjänst. Det är ett **förslag till kopplingsgranskning**, inte klartecken att lägga hotet på alla tjänster.
- Ett nytt offentligt-utbetalningshot ska prövas för lön, deklaration, bokföring/bokslut och en eventuell ansökningstjänst. Sanktions-/kryptohot ska prövas för betalning/klientmedel och relevanta redovisnings-/rådgivningsuppdrag. Ingen global koppling utan förklaring.
- Allt som endast täcks genom en allmän rubrik ska få konkreta exempel och rätt källhänvisning i B. Nivåmotiveringen för varje hot görs i C. **Medel behålls tills tillräckligt avgränsat underlag stöder annat.** Sektorns höga hot är inte automatiskt varje modus nivå.

## 7. Befintliga sårbarheter och metodgränser

| Poster | Slutsats och följd |
|---|---|
| `S-KUND-01`, `S-KUND-02` | Riskbransch/kontanthantering finns. 20 respektive 10 procent är metodval; varken frånvaro av aktivering eller under-tröskel är nej. D3/D9. |
| `S-KANAL-01` | Digitalt underlag kombinerat med begränsad bankdata. Detta mäter insyn; det är inte samma uppgift som osäker distansidentifiering. Behåll separat med tydligt syfte. |
| `S-VERK-01`, `S-ARB-15` | Erfarenhet och aktuell utbildning finns. De överlappar men är inte samma sak. Tvåårsgränsen och dubbelräkning prövas i D9. |
| `S-GEO-01`, `S-ARB-04`/`11`/`14` | Utländska transaktioner, ägare utanför EES, högrisktredjeland och utsatt område finns. `> 0` kan vara rimligt som synlig förekomst men är inte en föreskriven höjningströskel. Antal/andel och relevans ska visas separat; D3/D9. |
| `S-KOMB-01` | Riskbransch och svagt bankunderlag finns som kombination av byråandelar. Marginalandelarna visar inte vilka kunder som har båda egenskaperna. Beskriv inte detta som konstaterad kundsamverkan. D4/D9 och del 3:s särskilda databeslut. |
| `S-TJ-01`–`04` | **Byt läsbara namn**, exempelvis Betalnings- och attestmandat, Klientmedel i byråns namn, Bolagsbildning och förmedling samt Företrädaruppdrag för tredje mans räkning. `erbjuds = ja` är inte i sig belägg för en brist. Vikten och sista tjänstens avgränsning behöver prövas. Inga nya frågor för namnbytet. |
| `S-ARB-01`/`16`/`17`/`18` | Nära relation, samlade roller, kundberoende och outsourcing finns. Det är verksamhetsspecifika metodtolkningar; ensamföretagande och outsourcing är inte generella lagbrott. |
| `S-ARB-02`/`03`/`06`/`07`/`09`/`10` | PEP, ägarstruktur, kortlivade/övertagna bolag, ombud och extern KYC finns. Behåll, precisera hjälpen vid behov enligt källmatriserna. |
| `S-ARB-05` | Ideella kunder finns redan. Insamling/vidareförmedling är mekanismen, inte associationsformen ensam. PT-kopplingen via `H-03` och TF-kopplingarna prövas i D7. |
| `S-ARB-08` | Ändringen för tillförlitlig identifiering är ett sakligt förtydligande med konsekvenser för tidigare svar/scenarier. Inga gamla svar får automatiskt bli positiva belägg för det nya kriteriet. |
| `S-ARB-12`/`13` | Förtydliga hela geografiska kriteriet och effektiv tillämpning enligt avsnitt 3. Generell utlandsanknytning ersätter inte bedömningen. |

All befintlig sårbarhetskatalog är därmed avstämd. Föreslagna nya indikatorer ska i B få typade villkor, område, relevanta hot, källa/locator och `ej_granskad`. Varje egen vikt eller tröskel märks `metodval`. Lägre-risk-indikatorer behöver kunna lagras utan att felaktigt bli hotförstärkare.

## 8. Nya frågor och arbetsmängd inför B

**Detta är ett frågeförslag, inte byggda fält.** Gemensamma uppgifter lämnas en gång. Befintliga intagsfunktioner för okänt, underlag, datum och period ska återanvändas. Saknat svar får inte bli nej/noll. Alla föreslagna beräkningsfält behöver en definierad population och tjänstevis relevansprövning.

| Frågegrupp | Antal nya sakfrågor i förslaget | Innehåll |
|---|---:|---|
| Högre risk/distans | 6 | Förekomst hos kunder av (1) nominee/innehavarandelar, (2) konstruktion för fysisk persons tillgångar, (3) hemvist under sanktion/embargo, (4) hemvist med terrorstöd/verksamhet, (5) okänd/okopplad betalare samt (6) distans utan tillförlitlig identifiering. Se fullständiga definitioner i avsnitt 3. |
| Potentiellt lägre risk | 5 | Ett kundantal för var och en av de fem definitionerna. Gemensam bas `P-KUND.antal_aktiva`; överlapp tillåts och visas. Noll kräver underlag, annars okänt. |
| Befintliga tjänster, nya modus, namn och hjälpförtydliganden | 0 | Återanvänd uppdragsbeskrivningar, kundtyper, kanaler, geografi, mandat, lokala avvikelser och tjänstens hotobservation. Att lägga alternativ till en hotlista är ingen ny fristående fråga. |
| Fyra nya tjänster, om granskningen väljer dem | 66 | Samma 17 tjänstevisa intagsfrågor som dagens red01-gren, gånger fyra, minus två erbjudandefrågor som redan finns för trust/nominee: `17 × 4 − 2`. Se specifikation nedan. |
| Fyra motsvarande tjänstekontroller, om de byggs enligt befintligt mönster | 20 | Fem per kontroll: utformning, genomförande, belägg, effekt och utfall. Specifik kontrollverkan får inte antas av att tjänsten erbjuds. |

**Grundförslaget till indikatorer innebär 11 nya frågor.** Med samtliga fyra tjänstegrenar och kontrollgrenar enligt nuvarande formulärmönster blir det **97 nya frågedefinitioner totalt** (`11 + 66 + 20`), villkorade efter erbjudande och relevans. Det är ett högt antal och ska vara synligt före B. De fem frågorna per kontroll kan till exempel hanteras genom befintlig gemensam beläggshantering, men en teknisk sammanslagning får inte ta bort den sakliga prövningen.

De 17 tjänstefrågorna avser erbjudande, kundantal, omsättning, lokal sektorsmotivering, arbetssätt, kundtyper, kanaler, geografi, avvikelser, fyra kundantal (utlandstransaktioner, utländska ägare, riskbransch, kontanter), attest, betalningsmandat, bankinsyn och iakttagna hot. Härledda andelar räknas inte som nya frågor. Basperiod, relevans och kontrollfrågor ska visas villkorat, inte som ett krav att alla 97 besvaras av varje byrå.

**Alternativ för tjänsteomfattningen:**

- Fullt förslag: fyra nya tjänster; 97 frågor enligt mönstret ovan. Det gör uppdrag som redan berörs av paketens tillämpningsfrågor explicit analyserbara.
- Snävare redovisningsomfattning: bara ansökningar och icke auktoriserade granskningsuppdrag som nya tjänster; `11 + 2 × (17 + 5) = 55` frågor. Trust/nominee måste då få en uttrycklig avgränsning vid befintliga ja-svar. Detta är ett alternativ till granskning, inte beslutat eller byggt.

Före implementation behöver granskningen välja tjänsteomfattning. I B ska det slutliga antalet redovisas mot **324 befintliga intagsfält**, tillsammans med varför varje fråga behövs. Ändringar i hjälpen till befintliga frågor räknas och versionsbinds separat. Ingen utökning av AI:s tillåtelselista föreslås.

## 9. Beroenden och gränser för nästa steg

| Förslag | Beroenden och följd om det avslås |
|---|---|
| Fem nya högre-risk-faktorer och distansförtydligande | B: profil-/katalogobjekt och relevanta kopplingar, C: berörda hotmotiveringar, del 3: datatäckning/statusar, D3/D9: relevans och trösklar. Avslag kräver ombyggda kopplingar, frågor och facit samt ny regelversion; gamla distanssvar kan inte återtolkas. |
| Fem lägre-risk-indikatorer | B lagrar/presenterar utan nivåeffekt. Del 3 behöver egen tabell. D beslutar eventuell verkan och dubbelräkning. Ett avslag på verkan kan lämna uppgifterna kvar som data om det är det uttryckliga beslutet. |
| Nya tjänster | B: tjänster, hot, kontroller, fält och berörda regionala paket. C: varje tillkommande hotnivå. Del 3: alla tabeller och datakällor. D1–D5/D8/D9: exponering, scenarier, aggregering och kontrollverkan. Avslag kräver borttagen tjänstegren och omräkning av jämförelsefallen. |
| Tre nya modus samt kopplingsförtydliganden | B: konkreta beskrivningar och tjänsterelevans. C: källbundna nivåer eller uttrycklig underlagsbrist. D: före/efter mot föregående steg och ursprunglig bas. En borttagen post kräver att eventuell faktisk täckning förs till annan post eller redovisas som kvarstående lucka. |
| Läsbara S-TJ-namn | Referenser/ID kan behållas. Nya texter måste granskas som ändrade objekt; namnbytet ska i sig inte ändra beräkningen. |
| Källavvikelserna | B behöver säker källa/version och tydlig sakkunnignotering. Inga historiska källbytes eller fastställda paket skrivs om. |

I B ska både nya och ändrade objekt vara `ej_granskad`. Samtliga genomförandeobjekt ska senare omfattas av sakkunnigbeslutet, inte bara en beskrivning i guiden. B får inte smyga in D:s metodval. Särskilt ska inte nivåer sänkas därför att kunder har EES-hemvist eller en fråga har fått ett snävare namn.

Efter granskning av A gäller fortsatt arbetsordningen **B, C, del 3, D, ny granskning av båda referens-PDF:erna, E**. Del 3 har egna beslut före bygge om nivå per område, kundriskklasser, rutinavsnitt och samverkan. Rapportexemplets poäng och nivååtgärder är inte källor för metoden. Bilaga A och B1 behåller dispositionen men måste återge ändrat regelinnehåll.

## 10. Kontroll och granskningspunkt

Steg A levererar en motsvarighet eller uttrycklig avgränsning för **alla fem punkter i PTL 2:4, alla tio i 2:5, vägledningens tjänster och namngivna hot**. Föreskrifternas 2 kapitel, befintliga 28 sårbarheter och relevanta delar av registrerade lägesbilder är också avstämda. Detta är en innehållsinventering; det är inte juridiskt godkännande eller en ny beräkningsmodell.

Kravsammanställningens punkter 1–16 har motsvarighet i omfattnings-/tjänste-/hot-/källstrukturen, 17–26 i faktor- och värderingsmatriserna, 27–33 i utvärderings-/informations-/tillsynskraven och 34–36 i kontrollernas dokumenterade effektivitetsprövning. De senare metod- och rapportkopplingarna ska kontrolleras i D respektive del 3. MCon-exemplets generella lågrisketiketter för svenska småföretag, lönehantering och digital identifiering förs inte in som metodbasis.

**Verifiering:** enbart dokumentationsändringar; jämförelsen av testverktygets snapshot omfattar samma 816 resurser som del 1:s gröna fullsvit och ska vara identisk före och efter dokumentationen. Den tidigare körningen är **3 448 godkända, ett liveprov bortvalt, noll fel eller överhoppade prov**. Ingen ny fullsvit har körts för denna rena dokumentationsleverans; AGENTS regel 6 tillåter färdigställande av dokumentation när verifierat snapshot är oförändrat. Diffkontroll och kontroll av dokumentets befintliga objekt-ID görs före commit.

**Lämnas nu för granskning:** täckningsbedömningarna, de tre modusförslagen, avgränsningen av styrelse-/nomineetjänster, tjänsteomfattningen med frågeantal och de två källavvikelserna. Inga nya fält eller katalogposter byggs innan granskningen av steg A är klar.
