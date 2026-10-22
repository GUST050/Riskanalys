# Kort resultatrapport med fastställda bilagor – designunderlag

**Status:** granskningsförslag, revision 2 efter Claudes granskning. Inte godkänd för implementation. Användaren har beställt uppdatering av båda dokumenten före implementation.
**Datum:** upprättat 2026-10-22, reviderat 2026-10-23.
**Verifierad kodbas:** `4a878b9bb35a2489e902fd341a6391cc4ce4f7fa`, gren `codex/kravstod-tjansteexponering`.
**Föregående dokumentrevision:** `6e34cfd`; produktkoden är oförändrad sedan angiven kodbas.
**Genomförandebeslut 2026-10-23:** användaren har godkänt start av R0–R2 med två ytterligare standardbytesprov. Kontrollpunkten efter R2 kvarstår före R3–R7.
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

**Kontroll av Claudes huvudfynd 2026-10-23:** en separat körning av befintliga `analyslagen.bygg(..., 'direkt2')` på syntetiska data bekräftar sju PT- och tre TF-scenarier per tjänst, fem avgörande PT-scenarier före kontroll och tre avgörande TF-scenarier med nivån mycket hög. Nio av tio `(hot, dimension)`-par finns i alla fyra tjänster. Det är åtta unika hot-ID, eftersom ett hot förekommer i båda dimensionerna; jämförelsen gäller scenarier, inte bara hotnamn.

I `fyra_tjanster` är de hela PT-/TF-motiveringarna 109–114 ord per tjänst och exponeringen 153–179 ord. Exempelvis har `H-01/PT` kvarstående nivåer hög, måttlig, måttlig, hög för `T-RED-01`–`04`. Detta stöder matris med separata tjänsteceller och lokala kontrollförklaringar. Gemensamt hot-ID bevisar däremot inte identisk mekanism; delningsvillkoren i 5.1.1 ska alltid prövas. Ordantalet är uppmätt i just detta fall, inte ett antagande om betalningsmandatfallet eller riktiga byråtexter. Kontrollen körde inga AI-anrop, ingen full testsvit och ingen V9-implementation.

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
| R4 | Gemensamma förhållanden, egen rapportering/erfarenhet och gemensamma scenariokedjor en gång. Scenariomatris med hot och dimension som rader och tjänster som kolumner; nivå före/efter kontroll per cell. | 550 ord | D-ARB.4–.5, .6.x–.7 och bedömningen |
| R5, ett underavsnitt per tjänst | Kort om användningen, egna scenarier/sårbarheter, avvikande kontrollpåverkan, lokala undantag och åtgärdsreferenser. Hela PT- och TF-motiveringen; explicita hänvisningar till tjänstens celler och kedjor i R4. | 4 × 250 ord | D-ARB.6.x och .7 |
| R6 | Samtliga åtgärder och relevanta luckor, kompakt grupperade med bevarad medlemsstatus, ansvar, uppföljning och prioritet. | 300 ord | D-ARB.9, analysen och fynden |
| R7 | Utvärdering, nästa genomgång, förändringsplaner och omvärldsbevakning. | 150 ord | D-ARB.10–.11 |
| | **Summa riktvärde** | **2 500 ord** | |

Ord är planeringsstöd; faktisk sidmätning är acceptansen. En tjänst får normalt omkring en halv till en sida. Ingen fast halvsida garanteras. Använd A4 och läsbar typografi: brödtext minst 11 punkter, tabelltext minst 9,5 punkter; inte mindre marginaler än V8. Inget separat omslag eller fullständigt innehållsregister som äter upp huvudrapportens sidbudget. Stabil innehållsförteckning och fulla källregister får finnas i bilagorna.

R5 använder stabila ID `D-ARB.R5.<tjänstens suffix>` kopplade till ursprungligt `D-ARB.6.<suffix>`. R1–R4 och R6–R7 har ID `D-ARB.R1` osv. Ingen tom R5-förälder skapas. R2 redovisar inte någon sammanvägd risknivå för hela byrån. TF får inte tilldelas ett nytt kvarstående riskvärde som motorn saknar.

## 5. Urval och sammanfattning utan nya bedömningar

### 5.1 Obligatorisk förklaringskedja per tjänst

Varje erbjuden tjänst ska ha en begriplig kedja i **R4 och R5 tillsammans**; den gemensamma kedjan behöver inte upprepas i varje R5-avsnitt:

**Tjänstens användning → relevant hot → möjliggörande sårbarhet och riskfaktorer → sannolikhet och konsekvens → inneboende risk → belagd kontrollpåverkan → kvarstående risk där den beräknas → åtgärd eller begränsning.**

Värden och metodbegränsningar återges från sparat underlag. Faktum, antagande, kunskapslucka och metodkonflikt behåller sina skilda statusar. En tillämpning av ett antagande gör det inte till ett faktum. Frånvaro av belagd kontrollreduktion uttrycks utan att antyda att ingen kontroll utförs.

### 5.1.1 Gemensamma kedjor en gång i R4

Matrisens rader identifierar hot och dimension samt den gemensamma mekanismen. Kolumnerna identifierar varje erbjuden tjänst, även om flera får samma värden. Varje beräknad cell visar risk före och kvarstående risk där den finns, samt vilka led som är avgörande. TF utan beräknad kvarstående risk märks **ej beräknad**, aldrig med ett kopierat PT-värde. Saknat scenario, ej relevant och okänt underlag skiljs åt; ett tomt streck får inte dölja skillnaden.

På stående A4 visas högst fyra tjänstekolumner i samma matris. Fler tjänster delas i flera tabeller med upprepade radrubriker och samma stabila scenario-ID; varje tjänstecell visas exakt en gång. Förklaringar och källmedlemskap delas fortsatt utan informationsförlust. Textstorleken minskas inte för att få plats och sidmålet är fortsatt rådgivande för stora fall.

Gemensam kedjetext beskriver hot, möjliggörande sårbarhet och sannolikhet/konsekvens en gång. Identiska nivåvägar, kontrollpåverkan och statusar får dela förklaring mellan tjänster. Medlemskap, faktorer, värden, belägg och källpointers bevaras per tjänst, hot, dimension och riskled. Samma hotnamn eller slutnivå räcker inte som grund för att slå ihop olika mekanismer eller kontrollbegränsningar.

Olika före-/efternivåer för samma gemensamma hot kan visas i **separata tjänsteceller på samma rad**; värdena slås inte ihop. Skillnadens faktiska kontrollpåverkan och, när de skiljer, sannolikhet/konsekvens förklaras i berörda R5-avsnitt med hänvisning tillbaka till raden. Om mekanismen skiljer ska den särredovisas som egen variant eller lokalt scenario, inte döljas av en gemensam rubrik.

R5 återger bara tjänstens egen del av kedjan och hela dess PT-/TF-motiveringar, med referenser till samtliga tillämpliga R4-rader. Därmed går hela kedjan att följa för varje tjänst, även om den delas i presentationen. Tjänstens användning beskrivs kort med befintliga strukturerade tjänstefakta och katalogens beskrivning. Det långa fria fältet `exponering` återges i bilaga A och hänvisas till från R5, inte som ett obligatoriskt citat i huvudrapporten. Lokala sårbarheter och avgörande begränsningar får inte försvinna med denna hänvisning.

När flera scenarier var för sig ger tjänstens nivå ska rapporten säga det uttryckligen, exempelvis: **Flera scenarier ger var för sig nivån hög; samtliga avgörande scenarier framgår av R4 och tjänstens egna scenarier nedan.** Textens nivå hämtas från utfallet. Att flera scenarier når toppnivån beskrivs som metodens utfall och en fråga för metod-/sakkunnigprövning, inte som stöd för att rapporten väljer ett enda verkligt huvudhot eller ändrar metoden.

### 5.2 Urvalsregler

- Ta med alla scenarier som avgör nivån före eller efter kontroll, separat för PT och TF. Urvalet är oförändrat. Gruppning av identiska förklaringar tillåts inom och mellan tjänster enligt 5.1.1; alla tjänste-/hot-ID och källkopplingar bevaras. Matrisplacering får inte likställas med att olika nivåvägar eller kontrollförhållanden blivit identiska.
- Ta dessutom med egna identifierade sårbarheter och täckningsprövningar, lokala avvikelser, antaganden och luckor som berör en erbjuden tjänst. De får inte försvinna för att motorn inte aktiverar dem eller för att ett annat hot har högre nivå.
- En gemensam post är obligatorisk i R4 när den är relevant/okänd för minst en erbjuden tjänst och antingen ingår i en bärande kedja, är en egen sårbarhet eller har antagande/lucka/avvikande tillämpning. Bekräftade ej relevanta poster ligger i A/B1. Egen rapportering och erfarenhet redovisas alltid med faktisk status, även vid noll rapporter.
- Under-tröskel-/ej-uppfyllt-/ersatt-faktor-upplysningar behöver normalt bara en samlad hänvisning till A/B1 och D9. Påverkar de en uttrycklig lokal avvikelse eller osäkerhet tas den också upp i R5/R6. Okänt villkor får aldrig presenteras som känt under tröskeln.
- Alla registrerade åtgärder ska vara åtkomliga från R6 med bevarade medlems-ID och faktisk status. Exakt lika åtgärder får dela text; beslut, ansvar, tidsfrister och prioritet hålls per medlem. Registreringsordning är ingen beslutad prioritering. Saknade uppgifter visas som saknade, inte som fattade beslut.
- Öppna kunskapsluckor, motstridigt underlag och metodkonflikter redovisas i R6. Befintlig skillnad mellan spärrande konflikt och icke spärrande upplysning består. Historiska åtgärdade poster får ligga i bilagan med en tydlig hänvisning.

Urvalsreglerna är presentationsregler. De skapar inga nya riskvikter eller riktningar och löser inga metodkonflikter.

### 5.3 Textframställning och brister

Programmallar får sätta samman befintliga strukturerade sakuppgifter och namnge katalogens hot/faktorer. Hela `pt_motivering` och `tf_motivering` återges per tjänst i R5. Relevanta egna sårbarhets-/tillämpningsmotiveringar och avvikande kontrollprövningar återges där de behövs; delbara kedjor placeras i R4. Fältet `exponering` refereras till bilaga A enligt 5.1.1. Källfält som används som citat återges helt med attribution; inga första-meningen-utdrag, ellipser eller automatisk omskrivning av fri text. Exakt identisk text får återges en gång med samtliga referenser, utan sammanslagning av olika statusar eller belägg.

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

**En enda aktuell dokumentversion:** flytta den befintliga `AKTUELL_DOKUMENTVERSION` från `skrivversion.py` till `rapportversion.py`, behåll namnet och uppdatera samtliga produkt-/testimporter. Inför inte en parallell `AKTUELL_RAPPORTVERSION` eller ett kopierat alias. Dokumentstandarden är V8 under R1–R6 och byts till V9 först i R7. `skrivversion.py` behåller `AKTUELL_SKRIVVERSION = V8` och de historiska skrivversions-ID:na. Äldre V6/V7-byggare väljer sina uttryckliga/faktiska historiska skrivformat; de ska inte få V9 som fallback genom den flyttade konstanten. Granskning och fastställelse prövar det sparade dokumentets stödda format och faktiska struktur, medan standardkonstanten bara väljer format för nya byggen. Historisk verifiering läser fortsatt fryst format. Samtliga importer och relevanta standardvalsprov ska ändras i samma arbetssteg.

Fullständigt V8-analysdokument sparas som fryst presentationskälla `analysdokument-v8.json` i V9-granskningen. I V9-dokumentet behålls analysens ID, text, tabeller, originalspann och attribution. Endast format-, del- och visningsmetadata ändras för A/B1. En explicit transformationskarta listar dessa metadataändringar och bevisar att inga sakfält har förändrats. Gamla tvådelsformuleringar behålls i den frysta källan men ersätts i V9:s leveransmetadata av en versionsstyrd tredelsförklaring; varje sådan programtextändring listas separat, aldrig som ett undantag för fri saktext. B2:s korta källregister ligger sist i A; fulla källversioner förblir i B1.

Varje påstående/cell i R-delarna ska ha källartefakt, JSON-pointer, källsumma, tjänst/hot/dimension/riskled när tillämpligt och ett versionsbundet konstruktionsslag. JSON-pointers ska lösas mot frysta original, inte den effektiva läsvyn. En sammansatt mening har alla sina delkällor. Kartan anger också varför en kandidat visas eller bara hänvisas till. Ingen ändringskänslig sidnummerreferens används som enda länk.

Mänskligt läsbara hänvisningar anges per sammanhållen kedja eller tabellrad, med stabila avsnitts-/post-ID i A/B1. Samma hänvisning behöver inte skrivas efter varje mening. Mellanfilsreferenser ska vara begripliga även när en fil öppnas ensam; brutna interna Word-bokmärken är inte godtagbara ersättningar.

Kravkartan blir: **befintligt krav-ID → kanoniskt analysavsnitt → R-sammanfattning → A/B1-belägg**. Faktisk tillämplighet följer befintligt urval. Presentationskartan kan ligga i kod/fryst metadata utan att ändra `regelbas/krav/*.yaml` eller modellidentiteten för en layoutändring. Oförändrad modellbindning måste verifieras, inte antas.

## 7. Granskning, fastställelse och aktualitet

- Kör befintliga analys-, underlags-, kontrollreduktions-, sakkunnig- och fastställelsegrindar. V9 får inte behandlas som gammalt enklare dokumentformat genom en saknad versionsgren.
- Återbygg och pröva full V8-analys med V8-skrivresultaten; pröva därefter V9:s transformation, sammanfattning och tre delar. V9:s dokumentformat får aldrig jämföras direkt med skrivresultatets V8-format och underkänna en korrekt kombination.
- Granskning får inte bero på sin egen fyndsumma: bygg analys och sammanfattning från källorna först, beräkna analys-/presentationsfynd därefter och frys slutligen presentationen med den färdiga fyndlistan. R6:s analysgap byggs från analysen; maskinfynd visas i en separat fryst fyndlista.
- Resultatrapporten har en samlad explicit granskningshandling för exakt alla R-avsnitt som visats. Handlingen skriver vanliga avsnittsvisa granskningsposter atomiskt, med hela paketets struktur-/presentationssumma. Den godkänner inte A/B1, analysbeslut eller sakkunnigstatus.
- A/B1 behöver giltig sakgranskning i V9-paketets faktiska struktur. Gamla V8-attester förs inte över. Det första formatbytet kräver därför förnyad sakgranskning även av oförändrad analys; detta är en arbetskostnad för befintliga utkast och visas före bytet. Selektiv atteståteranvändning ingår inte.
- Alla beslut som i dag binds till hela analyspaketet fortsätter att göra det. Ingen selektiv förnyelse införs. Ändrad text, källa, urval, placering, konstruktion eller presentation gör dokumentets sakgranskning inaktuell enligt paketbindningen.
- Utkast får visa öppna fynd. Fastställelsen följer befintliga spärrar och V9:s presentationsspärrar, aldrig enbart att tre filer finns.
- Profil→analys→drift-lås, samtidighetskontroller och atomisk publicering återanvänds. Misslyckad rendering av en del publicerar inget nytt paket. Nedladdning av alla tre delar har samma aktualitetskontroll.
- Historisk verifiering kräver frysta källor och manifest, inte aktuell regelbas, nya mallar eller omrendering. Version väljs från fryst dokumentkälla och validerat manifest, inte bara filnamn.

## 8. Acceptans och verifieringskrav

| ID | Kontrollerbar acceptans |
|---|---|
| K01 | Inga nya sårbarhetssvar, sammanfattningsfält eller AI-anrop för V9; samma tillåtna AI-underlag, svar och motorutfall. |
| K02 | Tre obligatoriska dokumentdelar i ett atomiskt, fristående och verifierbart paket. |
| K03 | Alla erbjudna tjänster har separata PT-/TF-slutsatser och full förklaringskedja genom R4 + R5; okända värden märks. |
| K04 | Alla avgörande scenarioled, egna sårbarheter, relevanta undantag och osäkerheter omfattas; ingen topp-N-/tröskelfiltrering döljer dem. Delning mellan tjänster bevarar samtliga medlemmar och deras olika värden, statusar och belägg. |
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
| K15 | Efter R2 lämnas båda offline-byggda resultatrapporterna som PDF till användaren för läsning och granskning med Claude. R3–R7 börjar först efter uttryckligt klartecken till de visade versionerna. |

Om åttasidorsmålet inte nås med bevarat obligatoriskt innehåll ska det redovisas som ej uppnådd acceptans. Ändra då disposition/gruppering inom reglerna eller lämna målkonflikten för granskning; dölj inte innehåll och kalla inte leveransen färdig. Referensfallet kan vara tekniskt exporterat men är inte en verkligt fastställd byråbedömning.

## 9. Införande och granskningsfrågor

Bygg först en offlineversion av urvalet och resultatrapporten för de två syntetiska fallen. **Stanna alltid efter R2**, även om test- och sidmål redan nås. Skapa två fullständiga PDF-förhandsvisningar, med samma innehåll, ordning och typografiska begränsningar som designen, via ett avgränsat offlineverktyg utan produktens export-/attestintegration. Märk dem som förhandsvisningar, inte fastställda paket. Lämna båda till användaren för läsning och Claude-granskning, tillsammans med sidantal, spår-/täckningskontroll och kända brister. Förhandsvisningarnas kontrollsummor och användarens uttryckliga klartecken ska dokumenteras före R3. Om PDF inte kan framställas är kontrollpunkten inte passerad; senare rendering i R3/R7 ersätter inte den. Granskningen avser läsbarhet och urval, inte en juridisk sakattest.

Detta är ett avsiktligt stopp före den dyra delen: planen omfattar omkring 15 nya produktmoduler och berör granskning, export, manifest, fastställelse och webb. Offlineverktyget är granskningsstöd, inte ännu en produktmodul eller ett alternativt fastställelseflöde. Slutlig produktlayout kontrolleras åter i R3/R7. V8 förblir standard tills V9 har komplett stöd. Ofullständiga mellancommits används inte hos verkliga byråer.

När V9 blir standard gäller det nya granskningar. Befintliga utkast/fastställda paket fortsätter att identifieras och hanteras i sitt sparade format. En uttrycklig uppdatering kan skapa ett separat V9-utkast från kompatibla frysta V8-skrivresultat utan nya AI-anrop. Originalet skrivs aldrig över.

Claude ombeds särskilt granska:

1. Återger R4:s matris de gemensamma kedjorna en gång med rätt medlemskap, och visar R5 tjänstens egen analys utan upprepning eller informationsförlust?
2. Syns TF, egna sårbarheter och skillnader i kontrollpåverkan även när slutnivåerna är lika?
3. Är flytten av den enda dokumentversionskonstanten och avgränsningen mot V8-skrivformat konsekvent genom samtliga importer och formatgrenar?
4. Är transformationsundantagen tillräckligt smala och paket-/sakgranskningsbindningen fullständig?
5. Är åttasidorsmålet rimligt för provfallen utan att beslutsinnehåll eller läsbarhet offras?

## 10. Självkontroll

Underlaget skiljer krav från produkt-/metodval, använder aktuell före-bas, anger föreslagna beslut och bevarar engångssvaren. Ordtabellen summerar till 2 500. Både kritiska urval, delning mellan tjänster och långtextfallen har provkrav i planen. R2:s PDF-granskning är obligatorisk och kan inte ersättas av automatiska testresultat. Ingen implementation, rättslig sakkunnigattest, automatisk meddelandesändning, push eller merge ingår i denna dokumentbeställning.

### Ändringar i revision 2

- Gemensamma scenarier presenteras en gång i R4:s matris; R5 innehåller lokala skillnader och hela PT-/TF-motiveringarna. Lång exponering hänvisas till A.
- Delning mellan tjänster är uttryckligen tillåten utan att olika kontrollutfall, statusar eller belägg slås ihop. Rapporten förklarar när flera scenarier var för sig ger slutnivån.
- Befintlig dokumentversionskonstant flyttas och blir enda standardvalet; det tidigare förslaget med två överlappande konstanter utgår.
- Två PDF-förhandsvisningar och användarens klartecken efter R2 är ett obligatoriskt villkor före R3–R7. Förnyad sakgranskning av befintliga utkast anges som en faktisk arbetskostnad.
