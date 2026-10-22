# Kort resultatrapport med fastställda bilagor – designunderlag

**Status:** granskningsförslag, revision 1. Inte godkänd för implementation. Användaren har beställt både designunderlag och genomförandeplan för Claude-granskning före implementation.
**Datum:** 2026-10-22.
**Verifierad kodbas:** `4a878b9bb35a2489e902fd341a6391cc4ce4f7fa`, gren `codex/kravstod-tjansteexponering`.
**Genomförandeplan:** [resultatrapport-plan](../plans/2026-10-22-resultatrapport-plan.md).
**Utgångspunkt:** Claudes förslag `2026-10-22-forslag-resultatrapport.md`, läst i den andra, oförändrade klonen `/Users/danieltrogen/riskanalys-steg1-3/docs/superpowers/reviews/`. Detta underlag ersätter förslaget för den här ändringen; den andra klonen ändras inte.

## 1. Avsikt och avgränsning

Byrån ska kunna förstå sin riskbedömning och besluta om åtgärder utan att läsa tiotusentals ord. En kort resultatrapport visar slutsatserna. Analysen och underlaget finns i fastställda bilagor i samma verifierbara paket.

Byrån svarar fortsatt på gemensamma sårbarhetsfrågor en gång. Resultatrapporten kräver inga nya sakuppgifter, sammanfattningsfält eller AI-anrop. Den skapas ur samma profil, bedömning, analys och skrivresultat som bilagorna. Mänsklig granskning av sammanfattningen är däremot en uttrycklig handling.

Detta är en arkitekturändring av dokumentpresentationen. Riskmetod, D3/D9, kataloginnehåll, sakkunnigstatus, analysens schema 1/2 och AI:s skrivformat ändras inte. Egna tjänster utan modellstöd blir inte fastställbara genom denna ändring. Ett ofullständigt utkast ska fortfarande vara tydligt ofullständigt.

### Alternativ och rekommendation

| Alternativ | Följd | Bedömning |
|---|---|---|
| Fortsatt förkortning av V8:s läsrapport | Mindre upprepning, men analysen konkurrerar fortfarande med resultatet om utrymmet. | Otillräckligt som huvudsaklig lösning. |
| Ny resultatrapport och två bilagor, samma underlag | Kort beslutsunderlag och fortsatt full spårbarhet. Kräver nytt presentations- och attestkontrakt. | Rekommenderas och specificeras här. |
| Ny AI-sammanfattning | Ytterligare bedömning av formuleringar, anrop och risk för avvikande slutsatser. | Ingår inte. |

## 2. Utgångsläge och kravens betydelse

De två rättningarna i Claudes förslag är redan genomförda: inaktuell scenarioavvikelse kräver ny prövning, och D9 redovisas samlat per tjänst. [Senaste slutprovet](../reviews/2026-10-22-svar-claude-scenario-d9.md) anger:

| Syntetiskt fall, direkt schema 2 | V8 läsrapport | V8 B1 | Sidor läsrapport |
|---|---:|---:|---:|
| `fyra_tjanster` | 14 126 ord | 36 005 ord | 38 |
| `med_betalningsmandat` | 13 803 ord | 36 150 ord | 38 |

Detta är mätbas, inte ett nytt testresultat. Basen i det ursprungliga förslaget, `fc1a329` och 43 sidor, ska inte användas som aktuell före-mätning.

PTL 2 kap. 1–2 §§ ställer krav på riskbedömningens innehåll, omfattning, dokumentation och aktualitet. 14FS 2024:11, 2 kap. 2–3 §§ kräver bland annat identifiering och analys av relevanta hot och sårbarheter, motiverade risknivåer och dokumenterad utvärdering. Dessa bestämmelser föreskriver inget sidantal. Att fördela dokumentationen på resultatrapport och bilagor är här ett produktval, inte ett uttryckligt lagkrav eller en juridisk attest.

Primärkällor, kontrollerade i denna granskning:

- [Penningtvättslagen, 2 kap. 1–2 §§](https://data.riksdagen.se/dokument/sfs-2017-630.html).
- [14FS 2024:11, 2 kap. 2–3 §§](https://www.lansstyrelsen.se/download/18.74c322ef18f9ee08a2929/1716358223326/2024-11%20Penningtv%C3%A4tt%20Dalarnas%20l%C3%A4n%20G%C3%A4vleborgs%20l%C3%A4n%20Hallands%20l%C3%A4n%20V%C3%A4rmlands%20l%C3%A4n%20V%C3%A4stra%20G%C3%B6talands%20l%C3%A4n%20%C3%96rebro%20l%C3%A4n.pdf).

Alla tillämpliga krav måste täckas i paketet. Huvudrapporten ska sammanfatta de relevanta kravelementen byråspecifikt, men behöver inte innehålla ett separat stycke för varje teknisk `uppfylls_i`-referens. Täckningskartan ska skilja rättsligt krav från programmets presentationskrav. Regelbasens kravtext och hänvisningar ändras inte enbart för att byta rapportlayout.

## 3. Beslut som föreslås för granskning

1. Detaljerad analys får ligga i bilaga A, som fastställs tillsammans med resultatrapporten och B1. Det ersätter det tidigare förbudet mot att uppnå rapportförkortning genom omplacering **för detta nya format**. V8:s historiska regler ändras inte.
2. Resultatrapportens mål är 5–8 sidor för de två fyrtjänstfallen. Högst åtta sidor är acceptans för dessa fall, inte ett absolut sidtak för alla byråer. Inget innehåll får kapas för att uppfylla målet.
3. Resultatrapporten sakgranskas samlat som faktiskt presenterat innehåll och binds till hela paketet. Bilagornas ordinarie sakgranskning kvarstår. Källornas godkännanden är inte automatiskt ett godkännande av sammanfattningen.
4. Nytt dokumentformat är `D-ARB-resultat-v9`. AI:s skrivformat är fortsatt `D-ARB-tjanst-v8`. Historiska V8-paket verifieras oförändrade.

## 4. Leveransen: tre filer, ett fastställt paket

| Del | Ansvar | Filnamn, utkast |
|---|---|---|
| Resultatrapport | Förstå risk, skäl, begränsningar och beslutade/föreslagna åtgärder. | `allman-riskbedomning-UTKAST.docx` |
| Bilaga A – analys | Full gemensam och tjänstevis analys, inklusive de sex tjänstefrågorna. | `analysbilaga-UTKAST.docx` |
| Bilaga B1 – underlag | Fulla fakta, original, belägg, källor, beräkningar, planer, fynd och åtgärdsposter. | `underlagsbilaga-UTKAST.docx` |

Vid fastställelse ersätts `UTKAST` av `v{paketversion}` i alla tre namn. Alla delar visar samma bedömnings-/paketidentitet, status och vilka andra delar som ingår. Manifestet binder tre filer och deras frysta källor. En borttagen del gör paketet ofullständigt även om de övriga filerna är oskadade.

PDF används för sidmätning och visuell kontroll i denna leverans. Automatisk PDF-export till byrån är inte ett nytt produktkrav.

### Resultatrapportens disposition och ordmål

| ID | Innehåll | Riktvärde för fyra tjänster | Analyskälla |
|---|---|---:|---|
| R1 | Byrå, omfattade tjänster, datum, status och ansvar. Utkast påstår aldrig att fastställelse skett. | 100 ord | D-ARB.1, .3, .8, .10 |
| R2 | Risktabell: PT före kontroll, PT kvarstående, TF och bedömningsstatus per tjänst. Hänvisning till tjänstens förklaring i R5; inga dubblerade långa skäl. | 180 ord | D-ARB.8 och bedömningen |
| R3 | Omfattning, metod, skalornas metodstatus, begränsningar och avgränsningar. | 220 ord | D-ARB.1–.2 |
| R4 | Gemensamma förhållanden med betydelse för tjänsternas risker, inklusive egen rapportering och erfarenhet. | 300 ord | D-ARB.4–.5 |
| R5, ett underavsnitt per tjänst | Tjänsten, hot/sårbarhet, sannolikhet/konsekvens, motiverad risk, faktisk kontrollpåverkan och lokala undantag. | 4 × 300 ord | D-ARB.6.x och .7 |
| R6 | Samtliga åtgärder och relevanta luckor, kompakt grupperade med bevarad medlemsstatus, ansvar, uppföljning och prioritet. | 300 ord | D-ARB.9, analysen och fynden |
| R7 | Utvärdering, nästa genomgång, förändringsplaner och omvärldsbevakning. | 150 ord | D-ARB.10–.11 |
| | **Summa riktvärde** | **2 450 ord** | |

Ord är planeringsstöd; faktisk sidmätning är acceptansen. En tjänst får normalt omkring en halv till en sida. Ingen fast halvsida garanteras. Använd A4 och läsbar typografi: brödtext minst 11 punkter, tabelltext minst 9,5 punkter; inte mindre marginaler än V8. Inget separat omslag eller fullständigt innehållsregister som äter upp huvudrapportens sidbudget. Stabil innehållsförteckning och fulla källregister får finnas i bilagorna.

R5 använder stabila ID `D-ARB.R5.<tjänstens suffix>` kopplade till ursprungligt `D-ARB.6.<suffix>`. R1–R4 och R6–R7 har ID `D-ARB.R1` osv. Ingen tom R5-förälder skapas. R2 redovisar inte någon sammanvägd risknivå för hela byrån. TF får inte tilldelas ett nytt kvarstående riskvärde som motorn saknar.

## 5. Urval och sammanfattning utan nya bedömningar

### 5.1 Obligatorisk förklaringskedja per tjänst

Varje erbjuden tjänst ska ha en begriplig kedja:

**Tjänstens användning → relevant hot → möjliggörande sårbarhet och riskfaktorer → sannolikhet och konsekvens → inneboende risk → belagd kontrollpåverkan → kvarstående risk där den beräknas → åtgärd eller begränsning.**

Värden och metodbegränsningar återges från sparat underlag. Faktum, antagande, kunskapslucka och metodkonflikt behåller sina skilda statusar. En tillämpning av ett antagande gör det inte till ett faktum. Frånvaro av belagd kontrollreduktion uttrycks utan att antyda att ingen kontroll utförs.

### 5.2 Urvalsregler

- Ta med alla scenarier som avgör nivån före eller efter kontroll, separat för PT och TF. Gruppning tillåts bara vid identisk nivåväg, mekanism, kontrollpåverkan och status; alla hot-ID och källkopplingar bevaras.
- Ta dessutom med egna identifierade sårbarheter och täckningsprövningar, lokala avvikelser, antaganden och luckor som berör en erbjuden tjänst. De får inte försvinna för att motorn inte aktiverar dem eller för att ett annat hot har högre nivå.
- En gemensam post är obligatorisk i R4 när den är relevant/okänd för minst en erbjuden tjänst och antingen ingår i en bärande kedja, är en egen sårbarhet eller har antagande/lucka/avvikande tillämpning. Bekräftade ej relevanta poster ligger i A/B1. Egen rapportering och erfarenhet redovisas alltid med faktisk status, även vid noll rapporter.
- Under-tröskel-/ej-uppfyllt-/ersatt-faktor-upplysningar behöver normalt bara en samlad hänvisning till A/B1 och D9. Påverkar de en uttrycklig lokal avvikelse eller osäkerhet tas den också upp i R5/R6. Okänt villkor får aldrig presenteras som känt under tröskeln.
- Alla registrerade åtgärder ska vara åtkomliga från R6 med bevarade medlems-ID och faktisk status. Exakt lika åtgärder får dela text; beslut, ansvar, tidsfrister och prioritet hålls per medlem. Registreringsordning är ingen beslutad prioritering. Saknade uppgifter visas som saknade, inte som fattade beslut.
- Öppna kunskapsluckor, motstridigt underlag och metodkonflikter redovisas i R6. Befintlig skillnad mellan spärrande konflikt och icke spärrande upplysning består. Historiska åtgärdade poster får ligga i bilagan med en tydlig hänvisning.

Urvalsreglerna är presentationsregler. De skapar inga nya riskvikter eller riktningar och löser inga metodkonflikter.

### 5.3 Textframställning och brister

Programmallar får sätta samman befintliga strukturerade sakuppgifter och namnge katalogens hot/faktorer. Lokal motivering hämtas ur befintliga `pt_motivering`, `tf_motivering`, relevanta sårbarhets-/tillämpningsmotiveringar, exponering och kontrollprövning. Källfält som används som citat återges helt med attribution; inga första-meningen-utdrag, ellipser eller automatisk omskrivning av fri text. Exakt identisk text får återges en gång med samtliga referenser, utan sammanslagning av olika statusar eller belägg.

Om ett obligatoriskt led inte kan byggas visas en konkret komplettering och ett blockerande presentationsfynd. Ett utkast kan fortfarande exporteras med luckan. Befintliga analyser kan alltså behöva kompletteras i sina ursprungliga fält; inget nytt obligatoriskt sammanfattningsformulär införs. En lång men giltig motivering ska däremot aldrig avvisas av ett generellt ordtak.

Nivåer och statusar ska vara exakt lika mellan huvudrapport, A och bedömning. Åtgärdsmedlemmarnas sakfält ska vara lika mellan R6 och fullposterna i B1. Korta programmeningar behöver inte vara ordagrant lika den långa analysens text; de måste ha kontrollerade källvärden och spårbar konstruktion. Ett test som bara letar efter samma riskord bevisar inte detta.

## 6. Arkitektur och fryst spårbarhet

V8:s `rapportvyer.py` gör två disjunkta projektioner av ett kanoniskt dokument. Det kontraktet bevaras. V9 lägger till **nya sammanfattningsavsnitt**, med egna ID och explicita kopplingar till analyskällorna. Analysens avsnitt kopieras inte in som nya sammanfattningar.

```text
Oförändrade profil-, motor-, analys- och V8-skrivresultat
                         │
                         ▼
             Kanonisk fullständig V8-analys
                         │
              typat urval + källreferenser
                         ▼
      V9-dokument + sammanfattnings-/täckningskarta
         │                 │                  │
   Resultatrapport     Bilaga A          Bilaga B1
         └─────────────────┴──────────────────┘
              fryst presentation och manifest
                         │
              sakgranskning → fastställelse
```

Föreslagna avgränsade komponenter:

| Ny modul | Ansvar |
|---|---|
| `dokument/rapportversion.py` | `V9 = 'D-ARB-resultat-v9'` och aktuell rapportstandard, skild från skrivstandarden. |
| `dokument/resultatmodell_v9.py` | Strikta, frysta källreferenser, urvalsbeslut, presentationsbrister och byggresultat. |
| `dokument/resultatunderlag_v9.py` | Härled obligatoriska kedjor, skäl, åtgärdsmedlemmar och osäkerheter ur befintliga objekt. |
| `dokument/resultatrapport_v9.py` | Bygg R1–R7 utan AI eller nya sakbeslut. |
| `dokument/arb_v9.py` | Sammanställ huvudrapporten och bilagorna till ett kanoniskt V9-dokument. |
| `dokument/rapportvyer_v9.py` | Tre disjunkta avsnittsvyer av V9-dokumentet; sammanfattningens överlapp med analysen finns i spårkartan, inte i delade avsnitts-ID. |
| `dokument/{presentation,leverans,rapportpaket,rendering}_v9.py` | Frysta listor, tre filnamn, verifiering och rendering utan att ändra V8:s policy. |
| `granskning/dokument_v9.py` | Återbyggnad, spår-/täckningskontroll och versionsriktig delegering av befintliga analysgrindar. |

Återanvänd små rena hjälpfunktioner där deras kontrakt passar. Kopiera inte hela V8-motorn eller AI-kedjan. Gemensamma modeller och dispatch behöver utökas versionsmedvetet; `AKTUELL_SKRIVVERSION` förblir V8. V9 får endast byggas från kompatibla V8-skrivresultat eller tydligt ofullständigt underlag. Äldre skrivformat märks inte om.

Fullständigt V8-analysdokument sparas som fryst presentationskälla `analysdokument-v8.json` i V9-granskningen. I V9-dokumentet behålls analysens ID, text, tabeller, originalspann och attribution. Endast format-, del- och visningsmetadata ändras för A/B1. En explicit transformationskarta listar dessa metadataändringar och bevisar att inga sakfält har förändrats. Gamla tvådelsformuleringar behålls i den frysta källan men ersätts i V9:s leveransmetadata av en versionsstyrd tredelsförklaring; varje sådan programtextändring listas separat, aldrig som ett undantag för fri saktext. B2:s korta källregister ligger sist i A; fulla källversioner förblir i B1.

Varje påstående/cell i R-delarna ska ha källartefakt, JSON-pointer, källsumma, tjänst/hot/dimension/riskled när tillämpligt och ett versionsbundet konstruktionsslag. JSON-pointers ska lösas mot frysta original, inte den effektiva läsvyn. En sammansatt mening har alla sina delkällor. Kartan anger också varför en kandidat visas eller bara hänvisas till. Ingen ändringskänslig sidnummerreferens används som enda länk.

Mänskligt läsbara hänvisningar anges per sammanhållen kedja eller tabellrad, med stabila avsnitts-/post-ID i A/B1. Samma hänvisning behöver inte skrivas efter varje mening. Mellanfilsreferenser ska vara begripliga även när en fil öppnas ensam; brutna interna Word-bokmärken är inte godtagbara ersättningar.

Kravkartan blir: **befintligt krav-ID → kanoniskt analysavsnitt → R-sammanfattning → A/B1-belägg**. Faktisk tillämplighet följer befintligt urval. Presentationskartan kan ligga i kod/fryst metadata utan att ändra `regelbas/krav/*.yaml` eller modellidentiteten för en layoutändring. Oförändrad modellbindning måste verifieras, inte antas.

## 7. Granskning, fastställelse och aktualitet

- Kör befintliga analys-, underlags-, kontrollreduktions-, sakkunnig- och fastställelsegrindar. V9 får inte behandlas som gammalt enklare dokumentformat genom en saknad versionsgren.
- Återbygg och pröva full V8-analys med V8-skrivresultaten; pröva därefter V9:s transformation, sammanfattning och tre delar. V9:s dokumentformat får aldrig jämföras direkt med skrivresultatets V8-format och underkänna en korrekt kombination.
- Granskning får inte bero på sin egen fyndsumma: bygg analys och sammanfattning från källorna först, beräkna analys-/presentationsfynd därefter och frys slutligen presentationen med den färdiga fyndlistan. R6:s analysgap byggs från analysen; maskinfynd visas i en separat fryst fyndlista.
- Resultatrapporten har en samlad explicit granskningshandling för exakt alla R-avsnitt som visats. Handlingen skriver vanliga avsnittsvisa granskningsposter atomiskt, med hela paketets struktur-/presentationssumma. Den godkänner inte A/B1, analysbeslut eller sakkunnigstatus.
- A/B1 behöver giltig sakgranskning i V9-paketets faktiska struktur. Gamla V8-attester förs inte över. Det första formatbytet kan därför kräva förnyad sakgranskning även av oförändrad analys; detta visas före bytet. Selektiv atteståteranvändning ingår inte.
- Alla beslut som i dag binds till hela analyspaketet fortsätter att göra det. Ingen selektiv förnyelse införs. Ändrad text, källa, urval, placering, konstruktion eller presentation gör dokumentets sakgranskning inaktuell enligt paketbindningen.
- Utkast får visa öppna fynd. Fastställelsen följer befintliga spärrar och V9:s presentationsspärrar, aldrig enbart att tre filer finns.
- Profil→analys→drift-lås, samtidighetskontroller och atomisk publicering återanvänds. Misslyckad rendering av en del publicerar inget nytt paket. Nedladdning av alla tre delar har samma aktualitetskontroll.
- Historisk verifiering kräver frysta källor och manifest, inte aktuell regelbas, nya mallar eller omrendering. Version väljs från fryst dokumentkälla och validerat manifest, inte bara filnamn.

## 8. Acceptans och verifieringskrav

| ID | Kontrollerbar acceptans |
|---|---|
| K01 | Inga nya sårbarhetssvar, sammanfattningsfält eller AI-anrop för V9; samma tillåtna AI-underlag, svar och motorutfall. |
| K02 | Tre obligatoriska dokumentdelar i ett atomiskt, fristående och verifierbart paket. |
| K03 | Alla erbjudna tjänster har separata PT-/TF-slutsatser och full förklaringskedja; okända värden märks. |
| K04 | Alla avgörande scenarioled, egna sårbarheter, relevanta undantag och osäkerheter omfattas; ingen topp-N-/tröskelfiltrering döljer dem. |
| K05 | Riskvärden, riskled, kontrollpåverkan och åtgärdsmedlemmarnas sakfält överensstämmer med källorna. |
| K06 | All V8-saktext och alla original/belägg/attributioner bevaras i A/B1; metadata- och programtextändringar är uttömmande listade. |
| K07 | Källpointers kan lösas; varje tillämpligt kravelement har analysplats, byråspecifik R-sammanfattning och belägg. |
| K08 | Samlad R-granskning är explicit och atomisk; ändrat underlag/presentation invalidierar; inga V8-attester ärvs. |
| K09 | Befintliga sakgrindar består, inklusive otäckt TF, obelagd kontrollreduktion och ofullständig omfattning. |
| K10 | Historiska V8-paket verifieras utan förändrade bytes, summor eller ny rendering. |
| K11 | Båda fyrtjänstfallen är högst åtta faktiska resultatsidor med angiven typografi. Alla huvudrapportens sidor kontrolleras visuellt. |
| K12 | Fler tjänster/långa giltiga texter får överskrida målet med rådgivande varning; inga tysta utelämnanden, fontminskningar eller fria ordtak. |
| K13 | Ord, sidor och upprepning redovisas separat för R, A, B1 och totalen mot aktuell V8-bas; flyttad text kallas inte borttagen. |
| K14 | Python 3.12, riktad RED/GREEN och snabbprofil under arbetet; en färsk full icke-live-svit på slutligt källsnapshot enligt AGENTS regel 6. |

Om åttasidorsmålet inte nås med bevarat obligatoriskt innehåll ska det redovisas som ej uppnådd acceptans. Ändra då disposition/gruppering inom reglerna eller lämna målkonflikten för granskning; dölj inte innehåll och kalla inte leveransen färdig. Referensfallet kan vara tekniskt exporterat men är inte en verkligt fastställd byråbedömning.

## 9. Införande och granskningsfrågor

Bygg först en offlineversion av urvalet och resultatrapporten för de två syntetiska fallen. Mät och kontrollera läsbarheten innan export-/attestkedjan byggs ut. V8 förblir standard tills V9 har komplett gransknings-, export-, nedladdnings- och fastställelsestöd. Ofullständiga mellancommits används inte hos verkliga byråer.

När V9 blir standard gäller det nya granskningar. Befintliga utkast/fastställda paket fortsätter att identifieras och hanteras i sitt sparade format. En uttrycklig uppdatering kan skapa ett separat V9-utkast från kompatibla frysta V8-skrivresultat utan nya AI-anrop. Originalet skrivs aldrig över.

Claude ombeds särskilt granska:

1. Kan R5 byggas kort och verksamhetsanpassat av befintliga strukturerade uppgifter och hela lokala motiveringar utan nya inmatningsfält?
2. Är urvalsreglerna tillräckliga för att inte dölja TF, egna sårbarheter eller kontrollbegränsningar?
3. Är avgränsningen mellan V8-skrivformat och V9-rapportformat konsekvent genom alla dispatch-, gransknings- och verifieringsvägar?
4. Är transformationsundantagen tillräckligt smala och paket-/sakgranskningsbindningen fullständig?
5. Är åttasidorsmålet rimligt för provfallen utan att beslutsinnehåll eller läsbarhet offras?

## 10. Självkontroll

Underlaget skiljer krav från produkt-/metodval, använder aktuell före-bas, anger föreslagna beslut och bevarar engångssvaren. Ordtabellen summerar till 2 450. Både kritiska urval och långtextfallen har provkrav i planen. Ingen implementation, rättslig sakkunnigattest, automatisk meddelandesändning, push eller merge ingår i denna dokumentbeställning.
