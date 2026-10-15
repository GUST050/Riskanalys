# 10 Källkontroll och gapinventering inför M2

Underlag för [implementeringsplanen för M2](../superpowers/plans/2026-10-10-m2-regelbas-v1-och-juridisk-granskning.md). Kontrollen gjordes 2026-10-10 mot officiella primärkällor. Hämtade versioner ligger utanför repot i `../underlag/kallkontroll-2026-10-10/` från repots rot, med `manifest.json` som anger URL, hämtdatum, storlek och SHA-256 för varje fil. Inga originalhandlingar från tillsynsärendena, ingen OCR och inga personuppgifter har använts.

**Detta är en teknisk källkontroll, inte en juridisk granskning.** Den visar vilka lydelser som gällde och vad som kan kontrolleras maskinellt. Tolkningen av kraven görs av en oberoende sakkunnig i M2.

## 1 Primärkällor som kontrollerats

| Källa | Version och datum | Giltighet | Hämtad från |
|---|---|---|---|
| Lag (2017:630) om åtgärder mot penningtvätt och finansiering av terrorism (PTL) | Konsoliderad t.o.m. SFS 2026:1075 | Ikraft 2017-08-01. 1 kap. 2 § har två lydelser, se 2.1. | [rkrattsbaser.gov.se](https://rkrattsbaser.gov.se/sfst?bet=2017:630) |
| Förordning (2009:92) om åtgärder mot penningtvätt och finansiering av terrorism (PTF) | Konsoliderad t.o.m. SFS 2025:888 | 16 § i lydelse enligt SFS 2021:1253 | [rkrattsbaser.gov.se](https://rkrattsbaser.gov.se/sfst?bet=2009:92) |
| 14FS 2024:11, Länsstyrelsen i Västra Götalands län | Beslutad 2024-05-20, utkom 2024-05-22 | Ikraft 2024-07-01. Upphäver 14FS 2017:178, som fortfarande gäller överträdelser före 2024-07-01. | [lansstyrelsen.se (PDF)](https://www.lansstyrelsen.se/download/18.74c322ef18f9ee08a2929/1716358223326/2024-11%20Penningtv%C3%A4tt%20Dalarnas%20l%C3%A4n%20G%C3%A4vleborgs%20l%C3%A4n%20Hallands%20l%C3%A4n%20V%C3%A4rmlands%20l%C3%A4n%20V%C3%A4stra%20G%C3%B6talands%20l%C3%A4n%20%C3%96rebro%20l%C3%A4n.pdf) |
| 12FS 2024:8, Länsstyrelsen i Skåne län | Beslutad 2024-05-23, utkom 2024-05-28 | Ikraft 2024-07-01. Upphäver 12FS 2017:22 på samma sätt. | [lansstyrelsen.se (PDF)](https://www.lansstyrelsen.se/download/18.74c322ef18f9ee08a291e0d9/1716879026716/fs2024-8%20L%C3%A4nsstyrelsen%20i%20Sk%C3%A5ne%20l%C3%A4ns%20f%C3%B6reskrifter%20och%20allm%C3%A4nna%20r%C3%A5d%20om%20%C3%A5tg%C3%A4rder%20mot%20penningtv%C3%A4tt%20och%20finansiering%20av%20terrorism.pdf) |
| 01FS 2024:20, Länsstyrelsen i Stockholms län | Beslutad 2024-05-27, utkom 2024-06-05 | Ikraft 2024-07-01. Upphäver 01FS 2021:36 på samma sätt. | [lansstyrelsen.se (PDF)](https://www.lansstyrelsen.se/download/18.707df2a018f9ec7c62149421/1717509242057/01FS%202024-20.pdf) |
| Förordning (EU) 2024/1624 (AMLR) | EUT L 2024/1624, 19.6.2024 | Tillämpas från 2027-07-10; artikel 3.3 n och o från 2029-07-10 (artikel 90) | [EUR-Lex, svensk text](https://eur-lex.europa.eu/legal-content/SV/TXT/HTML/?uri=CELEX:32024R1624) |
| Promemorian *EU:s penningtvättspaket* (Fi2026/01654) | Publicerad 2026-07-06, remiss till 2026-10-30 | Lagförslag, inte gällande rätt. Föreslår ny penningtvättslag huvudsakligen från 2027-07-10. | [regeringen.se (PDF)](https://www.regeringen.se/contentassets/996dfddd5f304e8abb8d604ad4383b49/promemorian-eus-penningtvattspaket.pdf) |
| Amla: utkast till riktlinjer om verksamhetsomfattande riskbedömning (artikel 10.4 AMLR) | Konsultation 2026-04-16–2026-07-15 | Stängd. Slutliga riktlinjer hittades inte på den kontrollerade konsultationssidan 2026-10-10. Kontrollera publiceringsläget igen före implementation. | [amla.europa.eu](https://www.amla.europa.eu/policy/public-consultations/consultation-draft-guidelines-business-wide-risk-assessment_en) |

Sekundära källor med preciserad version:

| Källa | Version | Hämtad från |
|---|---|---|
| Nationell riskbedömning av penningtvätt och finansiering av terrorism i Sverige 2024/2025 | 160 sidor, PDF skapad 2026-06-04 | [polisen.se (PDF)](https://polisen.se/0c34c8d8c94e1a371d8cca457b84fb0a/siteassets/dokument/om-polisen/penningtvatt/nationell-riskbedomning-av-penningtvatt-och-finansiering-av-terrorism-i-sverige-2024_2025.pdf) |
| Länsstyrelserna i Skåne, Stockholm och Västra Götaland: *Erfarenheter från länsstyrelsernas penningtvättstillsyn – fokus den allmänna riskbedömningen* | Rapport 2026:14, dnr 10458–2026 | [lansstyrelsen.se (PDF)](https://www.lansstyrelsen.se/download/18.51b8c30c19d05558bd82e18e/1774259142687/Erfarenheter%20fr%C3%A5n%20l%C3%A4nsstyrelsernas%20penningtv%C3%A4ttstillsyn.pdf) |
| Samordningsfunktionen: *Information till redovisningskonsulter och skatterådgivare* | Version mars 2025, dnr A687.781/2024 | [polisen.se (PDF)](https://polisen.se/0be344afbcdff1a86db5cde12c2188c5/siteassets/dokument/om-polisen/penningtvatt/vagledning-till-redovisningskonsulter-och-skatteradgivare.pdf) |

## 2 Resultat

### 2.1 PTL 1 kap. 2 § från 2026-11-20

Lydelsen enligt SFS 2025:603 upphör 2026-11-20 och ersätts av lydelsen enligt SFS 2026:1023. En jämförelse punkt för punkt visar att **bara punkt 11 ändras** (verksamhet med bostadskrediter "och vissa andra konsumentkrediter"). Punkterna 19 (bokföringstjänster och revisionstjänster), 20 (skatterådgivare) och 23 (tjänster enligt 4 § andra stycket, bland annat bolagsbildning) är oförändrade. Ändringen påverkar därför inte vilka byråer som omfattas. Spec 20, fråga 6, är besvarad. Regelbasen ska ändå ha båda lydelserna, eftersom kravet på tester före och efter varje datumgräns gäller (spec 6.4).

Ingen annan paragraf i PTL har en kommande eller upphörande lydelse i den konsoliderade texten.

### 2.2 Tillsynen fördelas efter säte och folkbokföring

Enligt PTF 16 § utövar länsstyrelserna i Stockholms, Västra Götalands och Skåne län tillsyn över verksamhet enligt PTL 1 kap. 2 § första stycket 16, 17, 19, 20 och 22–24:

| Länsstyrelse | Juridiska personer med säte i, och fysiska personer folkbokförda i | Föreskrifter |
|---|---|---|
| Stockholm | Stockholms, Södermanlands, Gotlands, Västmanlands, Uppsala, Jämtlands, Västernorrlands, Västerbottens och Norrbottens län, samt filialer till utländska verksamhetsutövare | 01FS 2024:20 |
| Västra Götaland | Västra Götalands, Hallands, Värmlands, Örebro, Dalarnas och Gävleborgs län | 14FS 2024:11 |
| Skåne | Skåne, Blekinge, Kronobergs, Jönköpings, Kalmar och Östergötlands län | 12FS 2024:8 |

Regelpaketet `RP-RED-VG` har redan rätt sex län. Det som avgör vilket regelpaket som gäller är säte eller folkbokföring, inte var kunderna finns. Profilen saknar i dag den uppgiften.

### 2.3 De tre föreskrifterna har samma innehåll

Texterna jämfördes ord för ord efter att avstavningar tagits bort. Föreskrifterna har samma indelning (7 kapitel och 31 paragrafer, samma som `paragrafer` för `SRC-14FS-2024-11` i regelbasen) och samma lydelse i varje paragraf och allmänt råd. Skillnaderna är:

- länens namn och den upphävda föreskriften (14FS 2017:178, 12FS 2017:22, 01FS 2021:36) i ikraftträdandebestämmelserna,
- underskrifterna,
- ett stavfel i 01FS 2024:20 ("veksamhetsutövaren" i allmänna rådet till 3 kap. 4 §),
- ordningen på orden i tabell 1 i 3 kap. 4 §, som beror på att tabellens kolumner läses ut olika. Samma ord förekommer i alla tre. **Codex jämförde samtliga fem rader och tre kolumner visuellt på PDF-sidorna 5–6 i alla tre originalen 2026-10-10 och såg samma kontroll- och dokumentationskrav.** Radbrytningar, sidbrytningar och rubriklayout skiljer sig. Juridisk tolkning och attest återstår för sakkunnig.

Följden för regelbasen: ett krav kan bygga på samma paragraf i alla tre föreskrifterna, med en lydelse per föreskrift. Vilken lydelse som gäller avgörs av länet. Det minskar sakkunnigs arbete till en granskning per krav i stället för tre.

### 2.4 Rättelser i regelbas, spec och research

| Var | Nu | Rätt | Källa |
|---|---|---|---|
| Spec 6.2, exempel på källa | `beslutad: 2024-05-22` för 14FS 2024:11 | Beslutad 2024-05-20, utkom 2024-05-22, `galler_fran` 2024-07-01 | 14FS 2024:11 |
| `regelbas/kallor.yaml`, `SRC-PTL` | Saknar `konsoliderad_tom` och kontrollsumma | `konsoliderad_tom: "SFS 2026:1075"`, kontrollsumma för hämtad version | rkrattsbaser 2026-10-10 |
| `regelbas/kallor.yaml`, `SRC-14FS-2024-11` | URL till en översiktssida, ingen kontrollsumma | URL till PDF:en och dess SHA-256 | lansstyrelsen.se |
| `regelbas/kallor.yaml`, `SRC-TS-2026-14`, `SRC-VAGL-2025-03`, `SRC-NRA-2024-25` | Generella URL:er, inga kontrollsummor | URL:er och kontrollsummor enligt avsnitt 1 | se avsnitt 1 |
| Research 04 | "verksamhetsövergripande riskbedömning" | Den svenska texten i AMLR artikel 10 säger *verksamhetsomfattande riskbedömning* | AMLR (SV) |
| Research 04 | Amla:s slutliga riktlinjer "väntas Q4 2026" | Artikel 10.4 krävde riktlinjer senast 2026-07-10. Konsultationen stängde 2026-07-15 och resultatet är inte publicerat per 2026-10-10. | AMLR, amla.europa.eu |
| Samordningsfunktionens vägledning (mars 2025) | Anger Stockholms föreskrifter som 01FS 2024:53 | 01FS 2024:20. Stockholms författningssamling 2024 slutar på 2024:42. | lansstyrelsen.se |

Det sista visar varför regelbasen bara ska hänvisa till primärkällor: en officiell vägledning kan ha fel beteckning.

### 2.5 Sektorsrisk i den nationella riskbedömningen

Tabellen på s. 16 anger sammantagen sektorsrisk för sektorer under länsstyrelsernas tillsyn. Hot- och sårbarhetsnivå visas bara grafiskt.

| Sektor | Sektorsrisk | Avsnitt |
|---|---|---|
| Bokförings- och revisionstjänster | Hög | 7.19, s. 122 |
| Skatterådgivare | Hög | 7.20, s. 126 |
| Bolagsbildare och företagsmäklare | Hög | 7.25, s. 144 |
| Kontorshotell och postboxföretag | Betydande | 7.26 |

Avsnitt 7.19 beskriver bland annat osanna fakturor, brottsvinster som bokförs som försäljning, felbetalningar som ska betalas tillbaka till annat konto, möjliggörare och PML-aktörer samt **klientmedelskonton** som döljer vem som står bakom transaktionerna. Den nationella riskbedömningen använder en annan skala (låg, medel, betydande, hög) än riskmotorn (låg, måttlig, hög, mycket hög). Hur skalorna förhåller sig till varandra är ett metodval som en sakkunnig behöver godkänna.

### 2.6 Rättspraxis

Kammarrättsavgörandena som besluten hänvisar till (KRNG 6806-23, KRNS 8234-21, KRNS 2311-21 och 2334-21, KRNG 7174-23) har inte hittats publicerade. De behöver beställas från domstolarna som allmänna handlingar innan de förs in i källregistret.

## 3 Vad regelbas v0 täcker och vad som saknas för M2

| Område | v0.1.0 | Behövs i M2 | Källa och krav | Berörda filer | Verifiering |
|---|---|---|---|---|---|
| Källor | 8 källor, de flesta utan exakt URL och kontrollsumma | Primärkällorna i avsnitt 1 med URL, hämtdatum, beslutsdatum, konsolidering och kontrollsumma; PTF och de två andra föreskrifterna | Spec 5.1 block 1, 6.2 | `regelbas/kallor.yaml` | Regelkontrakt: varje lag, förordning och föreskrift har officiell URL och kontrollsumma |
| Lydelser | 3 (14FS 2 kap. 1–3 §§) | Varje paragraf som ger ett krav, i PTL och i alla tre föreskrifterna, samt båda lydelserna av PTL 1 kap. 2 § | Spec 6.4 | `regelbas/lydelser.yaml`, `regelbas/lydelsetexter/` | Texten kontrolleras mot kontrollsumman; tester före och efter 2026-11-20 |
| Krav | 6, bara allmän riskbedömning | Alla tillämpliga krav för byråer under länsstyrelsernas tillsyn. Inventera hela PTL, inklusive registrering enligt 7 kap. 3 § och ledningsförändringar enligt 7 kap. 6 §, samt föreskrifterna 1–7 kap. | Research 02, spec 18; PTL 7 kap. 3 och 6 §§ | `regelbas/krav/*.yaml` | `regelbas validera`; sakkunnig per krav; ingen paragraf utelämnas utan redovisad hantering |
| Krav i flera län | Ett krav har en källa; geografin följer kravets källa | Ett krav kan ha lydelser i 01FS, 12FS och 14FS; geografin följer lydelsens källa | 2.3 ovan | `regelverk/modeller.py`, `regelverk/urval.py`, `regelverk/validering.py` | Urvalstester per län |
| Regelpaket | `RP-RED-VG` | Ett paket per tillsynsområde: `RP-RED-VG`, `RP-RED-SKANE`, `RP-RED-STHLM` | PTF 16 § | `regelbas/regelpaket/` | Urvalstester; inget län ligger i två paket |
| Paragrafkarta | 14FS 2 kap., 3 av 12 hanterade | Hela PTL:s paragrafindelning (även 4 a och 7 a kap.) och föreskriften 1–7 kap.; varje rad får krav eller motivering till annan hantering/ej tillämplighet. Övergångsbestämmelser kontrolleras separat. | Spec 16.1 | `regelbas/regelpaket/` | Valideringen kräver full karta; fastställelsen kräver hanterade rader |
| Täckning i granskningen | Varje krav i paketet ska ha ett avsnitt i dokumentet | Bara krav som dokumentet ska uppfylla, så att rutinkrav inte ger blockerande fynd i en allmän riskbedömning | Spec 9, 10 | `granskning/kontroller.py` | Regressionstest |
| Tjänstekatalog | `T-RED-01` | Bokslut, deklarationer, lön, betalningsuppdrag, klientmedel, rådgivning, skatterådgivning och bolagsbildning (se 4) | PTL 1 kap. 2 § p. 19, 20, 23; 1 kap. 4 §; NRA 7.19–7.25; beslut 6572-2026 | `regelbas/kataloger/tjanster.yaml`, `falt.yaml` | Regelkontrakt per tjänst |
| Hot, sårbarheter, kontroller | 3, 4 och 1 | Hot ur NRA 7.19, 7.20, 7.25 och vägledningen; sårbarheter för kund, kanal, geografi och verksamhet; kontroller med utformning och genomförande | Spec 7.1 | `regelbas/kataloger/` | Varje tjänst har hot; varje post har källa och grund |
| Sektorsrisk | Saknas | Referensdata med NRA:s sektorsrisk och en automatisk B-13-kontroll | Spec 7.4, rapport 2026:14 | `regelbas/referensdata/`, `granskning/kontroller.py` | Test av B-13 |
| Profilens omfattning | Andelar utan period och nämnare | Omfattning per tjänst, kundtyp, kanal och geografi med period, nämnare, källa och status; säte; egen rapportering | Research 09; B-24, B-08–B-10, B-14 | `profil/`, `regelbas/falt.yaml` | Tester för period och nämnare |
| Kundmodellen | Saknas | Fyra spår som beslutstabeller med uttryckliga beroenden; inga kunduppgifter | Spec 7.6 | ny modul `kundmodell/`, `regelbas/beslutstabeller/kundmodell/` | Ett test per rad och per beroende |
| Sakkunnigunderlag | `regelbas summor` | Ett granskningspaket per regelpaket och datum: krav med lydelsetext, karta, kundmodell, metodval, kontrollsummor | Spec 16.1, 7.8 | nytt kommando | Test av paketets innehåll |
| AMLR | Bara research 04 | Källor och kravkarta AMLR–PTL samt ett separat utkastpaket i det parallella spåret. Paketet kan inte användas operativt innan det är färdigt och sakkunniggranskat. | Spec 18 (parallellt spår) | `regelbas/kallor.yaml`, separat utkastmapp enligt M2-planen | Utkast väljs aldrig operativt, inte heller för datum efter 2027-07-10; dagens paket påverkas inte |

## 4 Tjänstekatalogen

Tre frågor hålls isär.

1. **Juridiskt krav: omfattas verksamhetsutövaren av PTL?** Bokföringstjänster och revisionstjänster enligt punkt 19 samt skatterådgivning enligt punkt 20 prövas efter vad som faktiskt utförs. Punkt 23 hänvisar till tjänsterna i 1 kap. 4 § andra stycket men gäller bara verksamhetsutövare som inte är sådana personer som avses i punkterna 18–22. En byrå som omfattas av punkt 19 eller 20 ska därför inte automatiskt tilldelas punkt 23 när den erbjuder bolagsbildning. Tjänstens riskkategori och verksamhetsutövarens rättsliga tillämplighet registreras separat. Länsstyrelsens tillsyn prövas mot PTF 16 §; särskilda undantag prövas per krav, inte genom påståendet att alla skyldigheter är identiska. [PTL 1 kap. 2 och 4 §§](https://rkrattsbaser.gov.se/sfst?bet=2017:630).
2. **Tillsynspraxis: när räknas en tjänst som skatterådgivning eller bolagsbildning?** I beslut 6572-2026 bedömde Länsstyrelsen att en byrå som hjälpte till med bolagsstart och skatteupplägg också var bolagsbildare och skatterådgivare. Programmet ska därför fråga konkret efter vad byrån gör, inte vad byrån kallar det.
3. **Metodval: vilken grundnivå har tjänsten?** Grundnivåerna och kalibreringen mot sektorsrisken är metodval. Den nationella riskbedömningen ger sektorn hög risk, men det ger inte automatiskt varje tjänst hos varje byrå samma nivå (research 09).

Föreslagen katalog för M2:

| ID | Tjänst | PTL | NRA-sektor | Kommentar |
|---|---|---|---|---|
| T-RED-01 | Löpande bokföring | 1:2 p. 19 | Bokförings- och revisionstjänster | Finns |
| T-RED-02 | Bokslut och årsredovisning | 1:2 p. 19 | Bokförings- och revisionstjänster | NRA 7.19: övertygande årsredovisning |
| T-RED-03 | Deklarationer och deklarationsombud | 1:2 p. 19 | Bokförings- och revisionstjänster | NRA 7.19 räknar deklarationer som bokföringstjänst |
| T-RED-04 | Lönehantering | 1:2 p. 19 | Bokförings- och revisionstjänster | Svart arbetskraft och osanna löner |
| T-RED-05 | Betalningar och attest i kundens namn | 1:2 p. 19 | Bokförings- och revisionstjänster | Byrån utför transaktioner |
| T-RED-06 | Klientmedelskonto | 1:2 p. 19 | Bokförings- och revisionstjänster | NRA 7.19: döljer vem som står bakom |
| T-RED-07 | Ekonomisk rådgivning och ekonomichefstjänster | 1:2 p. 19 | Bokförings- och revisionstjänster | |
| T-SKATT-01 | Skatterådgivning utöver deklarationer | 1:2 p. 20 | Skatterådgivare | B-26; undantaget i PTL 3 kap. 1 § andra stycket gäller skatterådgivare |
| T-BOLAG-01 | Bolagsbildning, lagerbolag och förmedling av bolag | 1:4 andra st. 1; p. 23 bara när undantaget för p. 18–22 inte gäller | Bolagsbildare och företagsmäklare | B-26; rättslig tillämplighet prövas separat |
| T-BOLAG-02 | Registrerad adress eller postadress | 1:4 andra st. 3; samma avgränsning av p. 23 | Kontorshotell och postboxföretag | Rättslig tillämplighet prövas separat |
| T-BOLAG-03 | Styrelseledamot eller bolagsrättsligt ansvarig åt kund | 1:4 andra st. 2; samma avgränsning av p. 23 | Bolagsbildare och företagsmäklare | Firmateckning klassificeras efter uppdragets faktiska innehåll |

Katalogen är ett förslag för målgruppen, inte en uttömmande avskrift av 1 kap. 4 §. Trustförvaltning och nominella aktieägartjänster (andra stycket 4–5) kräver en uttrycklig fråga vid intaget. Om de förekommer och inte täcks av granskat paket blir resultatet preliminärt och paketets otillräckliga omfattning anges; tjänsten får inte döljas som "ekonomisk rådgivning".

## 5 Profilens omfattning

Tillsynsfallen TS-01 och TS-02 saknade uppgifter om omfattning (B-24), geografi (B-08–B-10) och egen rapportering (B-14, B-15). Profilen behöver därför:

- **Säte eller folkbokföringslän** (`P-ORG.sateslan`), som avgör tillsynsområde och regelpaket.
- **Omfattning per tjänst:** om tjänsten erbjuds, antal kunder, andel av omsättningen och andel kunder i riskbransch.
- **Kundtyper:** andel nya kunder och andel kunder som antagits utan fysiskt möte.
- **Kanaler:** andel digitalt underlag och andel kunder med bankdata (finns), andel kunder som hänvisats av annan rådgivare. Hänvisning får aldrig sänka risken (B-27, PTL 3 kap. 21–24 §§).
- **Geografi:** andel kunder med ägare eller transaktioner utanför EES, kunder etablerade i högrisktredjeland och kunder i utsatta områden. Geografi är mer än utlandet (beslut 6572-2026).
- **Egen rapportering och erfarenhet:** antal rapporter till Finanspolisen och antal avböjda kunder under perioden (14FS 2 kap. 2 §).

Varje andel och antal får en **period** (från och till) och en **nämnare** (vad andelen räknas på, till exempel antal aktiva kunder vid periodens slut). Nämnaren står i fältregistret; perioden anges när uppgiften bekräftas. Smågrupper under fem visas som "färre än 5" i AI-underlag (spec 17).

## 6 Kundmodellens fyra spår

Spåren och beroendena följer spec 7.6. Lagrummen är kontrollerade mot PTL i lydelse t.o.m. SFS 2026:1075.

| Spår | Rader | Lagrum |
|---|---|---|
| A Förbud och stopp | Otillräcklig kundkännedom: stopp, med avgränsat undantag enligt 3 kap. 1 § andra stycket. Misstanke vid etablering och misstänkt transaktion prövas var för sig; transaktionsundantaget gäller bara enligt 3 § andra stycket. Möjlig sanktionsträff kräver identitetsutredning; rättsverkan av bekräftad träff kräver exakt tillämplig sanktionsbestämmelse. | PTL 3 kap. 1–3 §§; särskild källkontroll av EU:s sanktionsbestämmelser i M2-planen |
| B Obligatoriska särskilda åtgärder | Högrisktredjeland: skärpt övervakning och de fyra punkterna i 17 § andra stycket. Undantaget för vissa EES-filialer/dotterföretag prövas mot samtliga tre villkor i tredje stycket. PEP, familjemedlem eller känd medarbetare: ursprung, skärpt uppföljning och godkännande, inklusive inför beslut att avbryta affärsförbindelse. Upphört uppdrag: 18 månader, därefter vid hög risk. | PTL 3 kap. 16–17, 19–20 §§ |
| C Riskklassning | Faktorer och poäng är metodval enligt PTL 2 kap. 3–5 §§. Preliminär när uppgifter saknas. | PTL 2 kap. 3–5 §§ |
| D Rapportering | Rapportering prövas enligt 3 §, även vid utebliven transaktion, med separat undantagsprövning för information som omfattas av 8 §. Skatterådgivarrollen ensam ger inget generellt undantag. Meddelandeförbudet och dess undantag prövas enligt 9 §. | PTL 4 kap. 2–3, 8–9 §§ |

Beroenden: C styr kundkännedomens omfattning och A:s tillräcklighetsprövning (3 kap. 1, 14–16 §§). B:s åtgärder får inte försvinna på grund av låg riskklass. Att B också ger hög riskklass är ett metodval. D använder egna rättsliga villkor enligt 4 kap. 2–3 och 8–9 §§; ett stopp i A ersätter inte rapporteringsprövningen. A och D delar uppgifter om yrkesroll och rättsligt uppdrag, men A:s undantag får aldrig automatiskt kopieras till D: 4 kap. 8 § prövas för de berörda uppgifterna. [Primärkälla för undantagsprövningarna](https://rkrattsbaser.gov.se/sfst?bet=2017:630).

Kundmodellen är en mall i fas 1. Den byggs som beslutstabeller med syntetiska testfall, och inga kunduppgifter lagras.

## 7 AMLR-spåret

Rättsläget 2026-10-10:

- AMLR tillämpas från 2027-07-10. Artikel 10 kräver en verksamhetsomfattande riskbedömning som också omfattar risken för att riktade ekonomiska sanktioner kringgås eller inte genomförs. Bedömningen ska utarbetas av den regelefterlevnadsansvariga och godkännas av ledningsorganet.
- Amla skulle enligt artikel 10.4 ha utfärdat riktlinjer senast 2026-07-10. Konsultationen stängde 2026-07-15; slutliga riktlinjer hittades inte på den kontrollerade konsultationssidan 2026-10-10. Kontrollera publiceringsläget igen före implementation.
- Fi2026/01654 föreslår en ny penningtvättslag som ersätter PTL, huvudsakligen från 2027-07-10. Länsstyrelserna i Skåne, Stockholms och Västra Götalands län föreslås fortsätta utöva tillsyn över verksamheter utan annan ordinarie tillsyn och få fler tillsynsobjekt. Remissen pågår till 2026-10-30; någon proposition finns inte.

Allt som bygger på Amla-utkastet eller promemorian märks `eu_utkast` respektive som lagförslag. Ett datum efter 2027-07-10 gör aldrig ett utkast till gällande rätt. Det separata AMLR-utkastpaketet kan inte väljas operativt förrän källor, svensk komplettering, krav och metod har granskats och paketet har frigivits uttryckligen. AMLR är antagen rätt med framtida tillämpning; dess status hålls skild från riktlinjeutkast och svenska lagförslag.

## 8 Kvarstående punkter från M0–M1

| Punkt | Bedömning | Etapp |
|---|---|---|
| a Sakgranskning kan dateras före granskningen | Gäller datumens trovärdighet i drift. Hanteras med b. | M4 |
| b Framtida datum godtas | Kräver en gemensam regel för "i dag" och tillåtna datum i alla kommandon. | M4 |
| c Tom motivering vid utvärdering | Del av minsta drift (spec 13.1). | M4 |
| d FfR ej tillämplig ger alltid [VERIFIERA]; P-ORG.namn stoppar utan att nämnas | Profilen byggs om i M2, och fältens kritiskhet och avsnitt 1 ändras då. | M2 |
| e Engelska felmeddelanden från kommandoraden; andelen "1" blir 100 % | M2 lägger till många andelsfält, så tolkningen av "1" rättas i M2. Formuläret i M4 ersätter kommandoraden för användare. | Andel M2, språk M4 |
| f Manifestet saknar markering för ej committade ändringar | Sakkunnigs underlag och paket ska kunna knytas till exakt regelbas- och programversion. | M2 |
| g Ingen fsync före publicering | Driftsäkerhet. | M4 |
| h Skadat körningsmanifest utan återställningsinstruktion; gammalt skadat utkastmanifest stoppar granska | Samma felväg som M2 bygger ut. | M2 |
| i Ingen varning när en lydelse träder i kraft mellan bedömning och beslut | Blir verkligt 2026-11-20. | M2 |
| j Körningsmappar namnges efter lokal tid | Vintertid börjar 2026-10-25, under M2. | M2 |
| k Spärren mot repot förutsätter redigerbar installation | Installation hör till M4. | M4 |
| l Andra stackspår vid trasiga filer | M2 lägger till många nya YAML-filer. | M2 |
| m AI:ns oklarheter valideras inte mot fältregistret | M2 lägger till många fält; frågorna ska peka på fält som finns. | M2 |

## 9 Osäkerheter

- Tabell 1 i 3 kap. 4 § jämfördes maskinellt och visuellt på PDF-sidorna 5–6 i alla tre originalen. Inga skillnader i kontroll- eller dokumentationskraven observerades; sakkunnigs juridiska tolkning återstår.
- Hot- och sårbarhetsnivåerna i den nationella riskbedömningen finns bara som grafik.
- Kammarrättsavgörandena är inte lästa i original.
- Om länsstyrelserna ändrar föreskrifterna efter remissen av Fi2026/01654 måste kontrollen göras om. Kontrollen bör upprepas före varje fastställelse hos en riktig byrå.
- Att besluten 6045-2026 och 6572-2026 har vunnit laga kraft är inte kontrollerat (research 09).

## 10 Status för M2-planen (kompletterad 2026-10-10)

Implementeringsplanen för M2 är genomförd tekniskt 2026-10-10, med slutlig verifiering i [STATUS](../STATUS.md). Sakkunniggranskning återstår. Verktyget [verktyg/lydelsetexter.py](verktyg/lydelsetexter.py) har rättats så att även kommandot `sfs` ger kontrollsummor, med separata nycklar för datumlydelser. Nio syntetiska kommandoradstester finns i `tester/enhet/test_lydelsetexter.py`; åtta fallerade före rättningen. Verktyget delar upp källorna i paragrafer och återskapar M1:s tre kontrollsummor för 14FS 2024:11 2 kap. 1–3 §§. Lokala `paragrafer.json` innehåller PTL 142, PTF 29 och 31 paragrafer per föreskrift. Efter normalisering av blanktecken är föreskriftsparagraferna lika utom tabellen i 3 kap. 4 §. Uttaget är tekniskt underlag; det ersätter inte kontroll mot källan, allmänna råd eller övergångsbestämmelser.

Utkast till beslut som planen ska bygga på, att pröva vid granskningen:

1. Ett krav kan ha alternativa lydelser från flera län; urvalet följer lydelsens källa och geografi. `Krav.kalla` behålls som huvudkälla för kompatibilitet med M1, men styr inte länsurvalet. Samtliga refererade källor binds till sakkunnigs kontrollsumma.
2. Ett regelpaket per tillsynsområde (`RP-RED-VG`, `RP-RED-SKANE`, `RP-RED-STHLM`), valt efter `P-ORG.sateslan`.
3. Granskningens täckning gäller bara krav som dokumentet ska uppfylla.
4. Skatterådgivning och bolagsbildning får hög grundnivå; avvikelse från NRA:s sektorsrisk kräver motivering (automatisk B-13). Skalmappningen NRA–motor beslutas av sakkunnig.
5. Fältregistret får nämnare och krav på period; uppgifter får period.
6. Kundmodellen byggs som egen modul med kundfält (`K-`) och beslutstabeller, utan kunduppgifter.
7. Sakkunnigunderlag och signering via kommandon som bara accepterar en verklig granskningsfil; tester signerar kopior.
8. AMLR i M2: källor, kravkarta och separat utkastpaket enligt spec 18. Utkastet är inte tillgängligt för operativt urval.
9. Kvarstående punkter enligt avsnitt 8.


## 11 Implementerad källbindning och granskningsbegränsningar

Regelbas v1 binder svenska paragraftexter till ett separat inventarium och källornas datum/geografi. De 264 svenska inventarieposterna och ytterligare EU269-lydelsen följer sakkunnigexporten. Dateringar är kandidatunderlag för expertgranskningen, inte godkännanden. Kartornas första kontrollerade datum är 2026-10-10; historisk användning före detta datum är inte frigiven.

EU269 artikel 2 är avgränsat rättsligt underlag. Det sparade `kalltexter/eu269-art2-eut-utdrag.txt` är ett märkt engelskt utdrag återgivet från den autentiska [EUT-ändringsakten 2025/2037](https://eur-lex.europa.eu/eli/reg/2025/2037/oj/eng), artikel 1.2. Läs originalet och kontrollera ikraftträdandet samt den [konsoliderade texten](https://eur-lex.europa.eu/eli/reg/2014/269/2026-09-28/eng) före attest. Källsumman avser utdraget och får inte kallas en summa av hela original-PDF:en. Andra sanktionsprogram, listuppdateringar och fullständiga individuella undantag/äganderegler är inte automatiskt modellerade. Underlagets rättsliga tillämpning bekräftas av människa.

Stockholms källregister och senare beslut anger 01FS 2024:20; en vägledningshänvisning till 2024:53 ska hanteras som en uttrycklig osäkerhet vid sakkunniggranskningen. Inventarieuttagets PTF 12 § innehåller en avvikande inline-siffra i det hämtade originalet; detta är bevarat kandidatunderlag och ska jämföras av sakkunnig.

AMLA:s konsultationssida och Regeringens remiss kontrollerades igen vid genomförandet 2026-10-10. Separat AMLR-utkast har 90 artiklar och sex bilagor; artikel 10 och riskbilagorna I–III prioriteras, övriga poster redovisas som återstående. Ingen svensk lagförslagstext eller riktlinjeutkast används som dagens bindande regel.


## 12 Förtydligande: byråns riskbedömning och projektets granskningskrav

Kompletterat 2026-10-10 efter användarens förtydligande. Målet är att programmet tar fram verksamhetsanpassade allmänna riskbedömningar för olika byråer, med en första lokal pilot. Codex utför källresearch, analys, rättelser och skrivarbete. Byrån lämnar och bekräftar verksamhetsuppgifterna. Pilotens identitet och faktaunderlag förvaras utanför Git.

### Vad är lagkrav och vad är projektets kvalitetsskydd?

[PTL 2 kap. 1–2 §§](https://www.riksdagen.se/sv/dokument-och-lagar/dokument/svensk-forfattningssamling/lag-2017630-om-atgarder-mot-penningtvatt-och_sfs-2017-630/) lägger ansvaret för riskbedömningen på verksamhetsutövaren. Dokumentet ska utgå från verksamhetens tjänster, kunder, kanaler, geografi, rapportering och relevanta myndighetsuppgifter samt hållas uppdaterat. Min tolkning av dessa bestämmelser är att de inte kräver att varje allmän riskbedömning certifieras av en extern jurist.

Detta ska inte blandas ihop med PTL 6 kap. 1–2 §§: modeller behöver kvalitetssäkras och en oberoende granskningsfunktion kan krävas med hänsyn till verksamhetens storlek och art. Funktionen måste därför bedömas för den faktiska byrån. Codex är inte en mänsklig funktionsinnehavare.

Projektets krav på oberoende sakkunnigattest för hela regelpaketet är ett internt kvalitetsskydd i specen. Det ska beskrivas som ett sådant, utan att tillskrivas lagen. Källkontroll med AI är inte en mänsklig attest och ger inte någon garanti om myndighetens framtida bedömning. Inga atteststatusar ändras genom detta förtydligande.

### Innehåll som dokumentet ska bära

Kontrollerat mot [14FS 2024:11, 2 kap. 1–3 §§](https://www.lansstyrelsen.se/download/18.74c322ef18f9ee08a2929/1716358223326/2024-11%20Penningtv%C3%A4tt%20Dalarnas%20l%C3%A4n%20G%C3%A4vleborgs%20l%C3%A4n%20Hallands%20l%C3%A4n%20V%C3%A4rmlands%20l%C3%A4n%20V%C3%A4stra%20G%C3%B6talands%20l%C3%A4n%20%C3%96rebro%20l%C3%A4n.pdf): tjänster; relevanta hot; sårbarheter för kunder, kanaler, geografi och övriga verksamhetsförhållanden; motiverade risknivåer; utvärdering minst årligen och inför relevanta förändringar; dokumenterade utvärderings- och uppdateringsdatum. Pilotens tillsynsområde måste fastställas innan en länsföreskrift väljs.

[Länsstyrelsens vägledning](https://www.lansstyrelsen.se/halland/samhalle/betalning-ekonomi-och-pengar/forhindra-penningtvatt-och-finansiering-av-terrorism/gor-en-allman-riskbedomning.html) betonar att riskfaktorerna ska analyseras tillsammans för varje tjänst. En riskreducerande kontroll får inte ge en lägre risk enbart därför att den finns beskriven; om sådana kontroller tas med ska deras effektivitet bedömas och dokumenteras. Vägledningen är stöd för tolkningen, inte en egen lagregel.

### Praktisk arbetsgång

1. Kontrollera krav och metod mot källorna och de kända tillsynsbristerna; dokumentera återstående tolkningsfrågor.
2. Samla pilotbyråns egna uppgifter med källa, datum och faktisk omfattning. Referensärenden är granskningsfall och får inte användas som pilotens fakta.
3. Ta fram riskbedömningen och kravmatrisen. Saknade uppgifter lämnas uttryckligen öppna.
4. Låt byrån bekräfta sakuppgifterna och hantera dokumentets beslut enligt sin ansvarsfördelning. Programmet behöver fortsatt prövas i M3/M4; denna första källgenomgång är inte en färdig produktvalidering.


## 13 Research för fullständigt intag (2026-10-10)

[GOV.UK:s question pages](https://design-system.service.gov.uk/patterns/question-pages/) rekommenderar tydligt syfte, en fråga per sida, återanvändning av svar och möjlighet att ange okänt när det är ett giltigt svar. [Check answers](https://design-system.service.gov.uk/patterns/check-answers/) ger översikt och möjlighet att rätta före nästa steg. [Error summary](https://design-system.service.gov.uk/components/error-summary/) ligger till grund för synliga fel med direkt koppling till frågan. Detta är stöd för formgivningen; den konkreta användbarheten för byråer ska prövas med användare.

Tre alternativ jämfördes: en enda lång blankett ger överblick men många irrelevanta frågor; en fri AI-intervju kan anpassa språk men ger svagare verifierbarhet; en regelstyrd intervju ger versionsbundna frågor och kontrollerbara beroenden. Det tredje väljs, med en svaröversikt för att behålla överblicken. Befintliga 142 fält räcker inte som bevis för underlagets fullständighet: beskrivande underlag behöver också kopplas till dokumentkraven.

[Länsstyrelsens vägledning](https://www.lansstyrelsen.se/halland/samhalle/betalning-ekonomi-och-pengar/forhindra-penningtvatt-och-finansiering-av-terrorism/gor-en-allman-riskbedomning.html) styr vilka verksamhetsförhållanden som behöver analyseras tillsammans och att kontrollernas effekt måste bedömas om de tas med som riskreducerande åtgärder. Följdfrågor om kundgrupper, kanaler och geografi knyts därför till varje erbjuden tjänst. Noll/nej får inte fyllas i för okända uppgifter.

[OWASP:s CSRF-vägledning](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html) används för token och Origin-kontroll. [Python http.server](https://docs.python.org/3.13/library/http.server.html) är inte en publik produktionsserver. Användningen begränsas till en lokal session på 127.0.0.1 med slumpad åtkomstväg, Host-kontroll, HTML-escaping, storleksgräns, CSP och avstängd requestlogg. AI-skrivningen använder den befintliga tillåtelselistan och utesluter namn och fritext. Vid uttrycklig SCB-hämtning skickas dessutom det angivna juridiska organisationsnumret till SCB:s fasta HTTPS-adress; personliga nycklar används endast för autentisering.

Beskrivande fritext kopieras lokalt till dokumentet och skickas inte till AI. Därför får formuläret inte påstå att AI har analyserat de fria beskrivningarna. Registrerade riskfaktorer styr motorn; andra relevanta riskförhållanden måste visas för särskild hantering och kan hindra fastställelse. Intaget och Word-utkastet ersätter inte M3:s modellutvärdering eller byråns sakgranskning.


**Verifierade implementationserfarenheter:** ett verkligt webbläsarprov visade att `Referrer-Policy: no-referrer` gjorde Origin till `null` även vid formulär-POST, vilket fick det avsiktliga Origin-skyddet att avvisa legitima svar. [MDN:s Referrer-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Referrer-Policy) beskriver detta beteende. `same-origin` används därför: den egna formulärsessionen behåller Origin medan hänvisningar till andra sajter inte får åtkomstvägen. Fristående källänkar använder dessutom `rel=noreferrer`. En lyckad POST omdirigeras med 303 så att omladdning inte skickar svaret igen.

**Fakta före analys:** intervjun kräver beskrivningar av faktiskt arbete, kundtyper, kanaler, geografi och erfarenheter. Den kräver inte att uppgiftslämnaren skriver en sakkunnig riskmotivering innan programmet bedömt verksamheten. En befintlig sektorsmotivering är frivillig inför första utkastet. B-13 accepterar bara aktuell bekräftad motivering och kvarstår före fastställelse när motivering behövs. Vägledningen används som stöd för dokumentinnehållet; detta gränssnittsval är ett metodval, inte ett nytt lagkrav.

## 14 Förifyllning från företagskällor (2026-10-10)

På användarens fråga kontrollerades externa företagskällor. SCB AFR-koppling och lokal SCB-JSON-import har därefter implementerats i intaget enligt avsnittet nedan. Personlig API-åtkomst saknas ännu; ett autentiserat uppslag är inte verifierat.

| Källa | Verifierat innehåll/åtkomst | Föreslagen användning |
|---|---|---|
| [SCB:s allmänna företagsregister](https://www.scb.se/vara-tjanster/bestall-data-och-statistik/foretagsregistret/avgiftsfria-uppgifter-i-foretagsregistret/) | Avgiftsfritt REST-API, personlig API-nyckel via registrering och accepterade villkor. SNI, arbetsställen/adresser och anställdas storleksklass; bara aktuella uppgifter, ingen historik. | Grunddata som förslag. Storleksklass får inte ersätta exakt antal personer inklusive ägare i P-ORG.antal_anstallda. Arbetsställe/postadress får inte förväxlas med säteskommun eller faktisk tjänstegeografi. |
| [Bolagsverkets företagsinformation](https://bolagsverket.se/apierochoppnadata/hamtaforetagsinformation/apiforatthamtaforetagsinformation.3988.html) | Företagsnamn, identitet, organisationsform/status, säteskommun, verksamhetsbeskrivning och valbara informationsmängder. Företagsinformationstjänsten kräver avtal/nycklar; separata värdefulla datamängder är avgiftsfria. | Primärkälla för juridisk grundidentitet/säte; välj exakt produkt först. Styrelseuppdrag får inte förväxlas med faktiskt utsedd AML-funktion. |
| [Allabolags API](https://www.allabolag.se/info/api/) | Grunduppgifter, bokslutshistorik, befattningar, koncernrelationer och händelser. Pris och integrationstillgång är inte bekräftade i denna kontroll. | Möjligt kompletterande företags-/bokslutsunderlag via avtalad integration. Ingen generell webbskrapning är verifierad eller byggd. |
| Byråns egna exporter/dokument | Kundregister, tjänstevolymer och rutin-/kontrollunderlag behöver komma från den faktiska byrån. En koppling till exempelvis ekonomisystem är ett separat ännu ej byggt integrationssteg. | Aggregerad kund-/tjänstestatistik med nämnare och samma period; lokalt rutinunderlag och faktiska kontrollbelägg. |

Rekommenderat flöde: organisationsnummer → verifierad företagsidentitet → förslag med källa, hämtningstid och uppgifts-/bokslutsperiod → lokal bekräftelse eller rättelse → frågor om kvarstående verksamhetsfakta. Import får inte skriva över bekräftade svar, fylla okända uppgifter med nej/noll eller bekräfta fakta automatiskt. Motstridiga källor visas. Registrerad verksamhet/SNI anger inte vilka tjänster som verkligen erbjuds eller hur de utförs. Årsredovisningens äldre omsättning/personantal är inte automatiskt aktuella intagsvärden. Personer och råa dokument hålls fortsatt utanför AI-underlaget.

Börja med avgiftsfria myndighetsdata där rätt innehåll och åtkomst finns. Allabolag kan tillkomma om dess åtkomst, villkor och nytta motiverar det. Riskanalysens faktiska kunder, befogenheter, kontrollgenomförande, rapportering och erfarenheter behöver fortfarande verifieras från byrån. SCB-flödet är implementerat; inget externt konto, avtal eller API-nyckel har skapats.

### 14.1 Verifierat tekniskt kontrakt och valt flöde

[SCB:s officiella OpenAPI](https://apiafr.scb.se/swagger/v1/swagger.json) hämtades 2026-10-10. Kontraktet anger v1, `GET /v1/juridiskaenheter/{peOrgNr}/full`, JSON-objektet `jeFullData` och `X-API-Key`. En [projektion med originalets kontrollsumma](scb-afr-v1-kontrakt.json) bevarar använda fältnamn och schema. [Variabelbeskrivningen 2026-10-09](https://www.scb.se/contentassets/8a8eb5c3d45f461ea93482f8e8d4de4f/variabelbeskrivning-afr_261009.pdf), s. 15, anger tio siffror för juridisk persons orgNr och prefixet 16 för tolvställigt peOrgNr. S. 5 anger verksamma arbetsställen, s. 15 omsättningsklass och år, s. 21–22 anställdas klasser och säteslän. Klass 0 för anställda är saknad uppgift, klass 1 är noll anställda: dessa får inte blandas ihop. Uppdateringsfrekvens skiljer mellan variabler; API-hämtning ger inte deras senaste ändringsdatum.

Tre integrationsvägar bedömdes: webbskrapning med osäkra format/villkor; ett kommersiellt företags-API med ännu okänd åtkomst/kostnad; myndighets-API med publicerat kontrakt och personligt konto. Användaren valde avgiftsfria myndighetsdata. SCB blir första connector eftersom både innehåll och tekniskt kontrakt gick att verifiera. [Bolagsverkets HVD](https://bolagsverket.se/apierochoppnadata/hamtaforetagsinformation/vardefulladatamangder/apiforvardefulladatamangder.5513.html) är avgiftsfritt men kräver registrering/OAuth-behörighet. Bolagsverkets direktdokumentation blockerades av CAPTCHA i denna kontroll; något gissat API-schema används inte. Digitala årsredovisningar är möjliga framtida underlag, inte en färdig bokslutsimport.

| Hämta/föreslå nu | Hämta som bakgrund nu | Fråga/verifiera från byrån | Senare separat integration |
|---|---|---|---|
| Juridisk identitet, namn, säteslän, registrerat arbetsställeantal | SNI-koder, juridisk form, SCB-företagsstatus, anställdas klass, omsättningsklass och år | Faktiska tjänster och kundvolymer per tjänst/period; kundtyper/ägarkomplexitet; möteskanaler; verklig tjänstegeografi; befogenheter/klientmedel; exakta personer inklusive ägare; faktisk omsättning; rutiner, kontrollbelägg, rapportering, erfarenheter och genomförd utvärdering | Bolagsverket HVD/digitala årsredovisningar; aggregerade ekonomisystemexporter; lokala dokument med uttryckliga belägg |

Bara namn/län/ställen överförs efter individuell bekräftelse, med exakt bildsumma i källan. Förslagen hålls separat från profilen; ingen status bekräftas genom hämtning. Avvikelser visas med befintligt svar. Ny hämtning och filimport bevarar profilsvaren. En bekräftad ändring går genom ordinarie typning, CAS och beroendeinvalidering. Registerdatum bedöms i Europe/Stockholm och aktuell bild får inte användas som historiskt bevis. Lokalt importerat JSON märks ej verifierat ursprung. Telefonnummer/e-post, c/o-adress, rårespons och nycklar sparas inte. SNI fyller inte automatiskt i några erbjudna tjänster eller risksvar.

Teknisk verifiering omfattar syntetisk nättransport, verklig lokal HTTP-omdirigering som inte följs, filbehörigheter, negativa identiteter och felvägar, datum runt midnatt, konflikter, gamla flikar och skadade bilder. Autentiserat SCB-uppslag är en återstående integrationskontroll när användaren har en nyckel. Inga personnummer behandlas av första registerconnectorn; enskilda firmor kan fortsätta med manuellt intag.

### 14.2 Utvidgad research: mindre manuell inmatning (2026-10-10)

Ny kontroll av primärkällorna visar fler möjliga underlag än de tre profileringsförslag som första SCB-connectorn använder. Här skiljs verifierad datatillgång från ännu ej byggda importer. Bolagsverkets direktsidor ger CAPTCHA; deras indexerade officiella sidtexter och FAQ används för innehåll/åtkomst, inte som verifiering av ett körbart API-kontrakt. Inga verkliga företags- eller kunduppslag har genomförts.

| Underlag | Vad går att få? | Koppling till intaget / begränsning | Byggläge och prioritet |
|---|---|---|---|
| [SCB AFR](https://www.scb.se/vara-tjanster/bestall-data-och-statistik/foretagsregistret/avgiftsfria-uppgifter-i-foretagsregistret/) | Företagsidentitet, namn, säte, arbetsställen, SNI, juridisk form/status, storleksklasser. [OpenAPI](https://apiafr.scb.se/swagger/v1/swagger.json) har också `fSkattStat`, `momsStat`, `arbGivStat`, `expImp`, `regDat`, `startDat` och `slutDat`. | Namn/län/ställen kan föreslås. Skatteregistrering är bakgrund om byrån, inte belägg för kundkännedom eller utförd kontroll. Export/importmarkering är inte byråns faktiska tjänstegeografi. Datum är olika registerhändelser, inte verksamhetsuppgifternas senaste verifiering. | Tre intagsfält byggda. Utvidgad bakgrund kan läggas till efter versionerad snapshot-migrering och prov; ingen ytterligare registrering behövs utöver SCB-nyckeln. |
| [Bolagsverket HVD](https://bolagsverket.se/apierochoppnadata/hamtaforetagsinformation/vardefulladatamangder/apiforvardefulladatamangder.5513.html) och [nedladdningsbara filer](https://bolagsverket.se/apierochoppnadata/hamtaforetagsinformation/nedladdningsbarafiler.2517.html) | Avgiftsfria grunddata och digitalt inkomna årsredovisningar; API kräver åtkomst, veckofiler kräver inget avtal enligt den officiella sidan. | Registrerad verksamhet kan ge ett förslag till P-BESK.verksamhet. Bokslutsvärden kan ge P-VERK.omsattning med exakt räkenskapsperiod och eventuell not; alltid den valda juridiska personen, inte koncernens totalsiffra. Medelantal anställda är inte aktuellt personantal inklusive ägare. | Nästa externa connector efter verifierat tekniskt kontrakt/åtkomst. Stora veckofiler är inte förstahandsval för en lokal byrå; lokal iXBRL-fil är ett möjligt första steg. |
| [Bolagsverkets FAQ](https://bolagsverket.se/apierochoppnadata/driftochsupport/fragorochsvaromapierna.4611.html) | Gratis årsredovisningar omfattar digitalt inlämnade iXBRL-filer från 2020; inskannade PDF-årsredovisningar ingår inte i denna gratismängd. | Saknad digital handling betyder inte att årsredovisning eller omsättning saknas. Senaste tillgängliga bokslut måste fortfarande stämma med vald statistikperiod. | Import behöver explicit stöd för period, valuta/enhet, bolag/koncern, originalsumma och saknade värden; inget gissat exakt belopp från en SCB-klass. |
| [Skatteverkets Hämta företagsinformation](https://www.skatteverket.se/hamtaforetagsinformation) | F-skatt, moms, arbetsgivarregistrering och beslutade arbetsgivaravgifter senaste tre månaderna via e-tjänst. | [Utvecklingssidan](https://www.skatteverket.se/omoss/digitalasamarbeten/utvecklingsomraden/foretagsuppgifter.4.339cd9fe17d1714c0773a24.html) säger att tjänsten ännu saknar planerat öppet API. Beskattningsengagemang är ett separat behörighets-/ombudsflöde; [tjänstebeskrivningen](https://www7.skatteverket.se/portal-wapi/open/apier-och-oppna-data/utvecklarportalen/v1/getFile/tjanstebeskrivning-beskattningsengagemang-v1-doc-v12) kräver behörighet. | Ingen skrapning eller automatisk e-postbeställning. SCB:s registreringsstatus är enklare komplettering inom vald gratisväg. |
| [Verklig huvudman](https://bolagsverket.se/apierochoppnadata/hamtaforetagsinformation/hamtainformationomverklighuvudman.6009.html) | Behörighetsstyrd tillgång efter regler ändrade 1 juli 2026; kategori och ändamål behöver fastställas. | Ingen öppen gratis masskälla för alla kunders ägare. Kundnivå med personuppgifter och kundkännedomsprövning är ett separat flöde; allmän bedömning använder aggregerad relevant statistik. | Inte första connector för minskade intagsklick. Ingen åtkomst eller ny kundscreening är byggd här. |
| Byråns egen webbplats / tjänstebeskrivningar | Offentligt beskrivna tjänster, kontor, kontaktkanaler och allmän verksamhet. | Kan föreslå P-BESK.verksamhet och tjänsteurval. Marknadsföring belägger inte kundantal, verkliga befogenheter, fungerande AML-kontroller eller vilka tjänster som faktiskt utförs. Kundlogotyper är ingen fullständig kundbas. | Senare lokal, källbunden import från uttryckligt vald URL/fil med bekräftelse av relevans och aktualitet. Inte byggd eller bedömd som myndighetsdata. |
| Byråns kund-/uppdragsregister, fakturering och befintliga dokument | Aktiva kunder, tjänster per uppdrag, periodens intäkter, interna bransch-/landklassningar och beskrivna rutiner. [Fortnox API](https://api.fortnox.se/apidocs) har kunder och fakturor, med [behörigheter](https://www.fortnox.se/developer/guides-and-good-to-know/scopes) och [sidindelning](https://www.fortnox.se/developer/guides-and-good-to-know/parameters). | Aktivt uppdrag är inte samma som aktiv kundpost eller förekomst av faktura. Tjänst måste mappas till uppdrags-/artikelkatalog. Kreditfakturor, avbrutna fakturor, moms, periodisering och vald juridisk person hanteras före beräkning. AML-rapporter och avböjanden kommer från separata lokala loggar. | Störst sannolik nytta: lokal CSV/XLSX-import av redan aggregerade tal först; ekonomisystem-API senare med verifierad åtkomst/kostnad. Ingen Fortnox-integration byggd i Riskanalys ännu. |
| [EU:s högrisktredjeländer](https://finance.ec.europa.eu/financial-crime/anti-money-laundering-and-countering-financing-terrorism-international-level_en), [FATF](https://www.fatf-gafi.org/en/publications/High-risk-and-other-monitored-jurisdictions.html), [EU-sanktioner](https://finance.ec.europa.eu/eu-and-world/sanctions-restrictive-measures/overview-sanctions-and-related-resources_en), [Polisens riskbedömning](https://polisen.se/om-polisen/polisens-arbete/finanspolisen/) | Offentlig referensdata och hot-/sektorskunskap. | Minskar användarens researcharbete. Berättar inte vilka länder eller kunder byrån faktiskt har. EU-lista, FATF-lista och sanktioner har olika rättslig betydelse och hålls åtskilda; riskmotor/referenceversion får inte bytas tyst av en hämtning. | Befintlig versionerad regelbas är grunden. Kontrollerad uppdateringsimport med källsumma, giltighetsdatum och granskning är ett senare separat steg. |

**Hur mycket kan fyllas i?** Den aktuella katalogen har 178 kanoniska intagsfrågor, varav 167 obligatoriska när de är tillämpliga. Antalet frågor som en viss byrå faktiskt får styrs av dess tjänster och grundsvar. Nuvarande SCB-koppling föreslår **3 fält**: namn, säteslän och verksamhetsställen. Den hämtar dessutom bakgrundsvärden som inte är nya intagssvar. Det är ingen täckningsprocent för en verklig byrå. Bolagsverkets årsredovisning kan tillföra exakt historisk omsättning och registrerad verksamhetsbeskrivning, men den täcker inte de flesta verksamhets- och kontrollfrågorna.

Katalogen har **36 numeriska frågor** som på sikt kan ta emot källbundna beräkningar/importer, exempelvis aktiva kunder, antal/omsättning per tjänst och kund-/kanal-/geografikategorier. Detta är ett potentialmått i koden, inte ett löfte om att samma källa täcker alla eller att alla frågor är aktiva. Kundkategorier kräver underlag om verkliga förhållanden; SNI/registrerad adress får inte ensam bli kundrisk eller tjänstegeografi. En enkel import av byråns aggregerade exporter kan spara mer arbete än att lägga till fler offentliga företagsfält. Personer, kundnamn och råa kundrader behöver inte lämna byråns dator för detta.

Fördelning verifierad mot regelbasens kanoniska intagsfält:

| Frågor | Antal | Praktiskt underlag |
|---|---:|---|
| Kunder och omsättning per tjänst | 22 | Uppdragsregister och tjänstemappad intäktsstatistik, två tal per tjänst. Samma kund kan använda flera tjänster; tjänsteantal summeras inte till unika kunder. |
| Kundbas och kundkategorier | 5 | Aktiva/nya/juridiska kunder samt riskbransch och kontanthantering. De senare kräver faktisk kundkännedomsinformation, inte enbart registerklassning. |
| Leveranskanaler | 2 | Uppdragssystemets uppgift om digitalt underlag och tillgång till bankdata. En kunds bankkonto i bokföringen bevisar inte att byrån har bankåtkomst. |
| Geografiska anknytningar | 2 | Kundkännedom och transaktionsunderlag för utländskt ägande respektive utländska transaktioner. Registrerat säte räcker inte. |
| Byråns storlek och verksamhetsställen | 2 | Aktuell intern person-/kontorsförteckning; SCB kan föreslå verksamhetsställen. Anställdaklass bevisar inte aktuellt antal personer inklusive ägare. |
| Total omsättning, rapporter och avböjanden | 3 | Bokföring/årsredovisning för samma period samt separat intern AML-logg för rapporter/avböjanden. Frånvaro av offentlig uppgift betyder inte noll. |

Nästa importer bör börja med de 22 tjänstetalen och totalt aktivt kundantal/omsättning om byrån har sådana sammanställningar. Kategori- och AML-loggtal läggs till bara när exporten faktiskt innehåller rätt underlag och definition. Det ger en konkret prioritering utan att lova 36 automatiska svar från ett vanligt kundregister.

**Beslut inför nästa bygge (2026-10-11):** gör först ett manuellt pilotintag för pilotbyrån. Inventera de exporter som faktiskt finns, med kolumner, period och definition av kund-/tjänste-/intäktstal. Pilotuppgifter och originalexporter förvaras utanför Git. Bygg sedan CSV/XLSX-import för det verifierade formatet, i stället för en generell import först. Pilotintaget och denna import är ännu inte genomförda.

**Rekommenderad arbetsgång när formatet har verifierats i piloten:** välj byrå → hämta tillgängliga offentliga grundförslag → importera befintligt aggregerat verksamhetsunderlag med period → granska en tydlig lista över förslag, avvikelser och källor → bekräfta relevanta fakta → fråga endast efter luckor. En gemensam bekräftelsevy kan minska klick, men måste visa exakt vilka fakta och perioder som godtas och använda samma CAS-/beroenderegler. Den är inte byggd i denna rättningsomgång. Ny/ändrad källa får aldrig bli ett faktiskt genomförandebelägg eller en automatisk bekräftelse.

[Länsstyrelsens vägledning](https://www.lansstyrelsen.se/halland/samhalle/betalning-ekonomi-och-pengar/forhindra-penningtvatt-och-finansiering-av-terrorism/gor-en-allman-riskbedomning.html) kräver analys av verksamhetens faktiska tjänster, kunder, distributionssätt och geografi samt effektiviteten hos åberopade riskreducerande kontroller. Import kan förbereda dessa frågor; programmet behöver fortsatt sakligt underlag för slutsatserna.

**Återkontroll av SCB-klasser:** PDF 2026-10-09 hämtades och lästes åter. Omsättningsklass 0 är **under 1 tkr**, inte saknad/0 kr. Anställdaklass 0 är saknad uppgift; klass 1 är 0 anställda, klass 2 är 1–4. Befintliga tabeller stämmer och behålls. Juridisk form 96 betyder *utländska juridiska personer*, inte uttryckligen filial; filialsvaret fylls därför inte automatiskt. Regressionerna i `tester/intag/test_granskningsfynd.py` låser klassgränserna.

**Filialuppgift i nästa connector:** [Bolagsverkets HVD-beskrivning](https://bolagsverket.se/apierochoppnadata/hamtaforetagsinformation/vardefulladatamangder/apiforvardefulladatamangder.5513.html) skiljer organisationsform FL (filial) från SCB:s juridiska former. Deras [bulkfilbeskrivning](https://bolagsverket.se/apierochoppnadata/hamtaforetagsinformation/nedladdningsbarafiler.2517.html) anger FL-ORGFO. Detta kan ge ett uttryckligt källbundet filialförslag i en framtida BV-adapter, efter identitets- och datumkontroll. Det ersätter inte filialkällan med SCB i den nu byggda vägen. Koden och frånvaro av filialuppgift måste tolkas enligt respektive verifierat kontrakt; okänd/saknad form blir inte automatiskt ”nej”.

### 14.3 Ny källkontroll och förenklat godkännande 2026-10-11

Användaren har provat ett SCB-uppslag och efterfrågat ett enklare flöde. Den tekniska verifieringen nedan använder syntetiska uppgifter; användarens verkliga nyckel och pilotbyråns underlag har inte lästs eller använts av agenten.

**Källkontroll:** SCB:s [aktuella OpenAPI](https://apiafr.scb.se/swagger/v1/swagger.json) hämtades utan autentisering. Hela dokumentets SHA256 är `e277224de8d504c94010ed026d2e28d84e23c92aba75e9010ef871efeaa8a5da`, vilket skiljer från den sparade kontrollen 2026-10-10. De använda projektionerna `jeFullData`, `naringsgrenData` och `securitySchemes` är däremot exakt lika den sparade kontraktsfilen vid dict-jämförelse. Ingen drift i dessa kontrakt konstaterad. [SCB:s åtkomst-/tekniksida](https://www.scb.se/vara-tjanster/bestall-data-och-statistik/foretagsregistret/avgiftsfria-uppgifter-i-foretagsregistret/) bekräftar aktuella data utan historik, personlig nyckel, högst fem anrop/sekund och olika uppdateringsfrekvens per variabel.

| Uppgift | Säker överföring och precision | Beslut/implementation |
|---|---|---|
| SCB namn, säteslän, positivt registrerat arbetsställeantal | Kontroll av rätt juridisk person och att antal ställen motsvarar verklig verksamhet. | Samlat uttryckligt godkännande; endast valda fält överförs. Namn och ställen kan följa med redan vid starten. |
| F-skatt, moms, arbetsgivarregistrering | `fSkattStat`, `momsStat`, `arbGivStat` ur samma SCB-anrop. Registreringsstatus hos Skatteverket enligt SCB; veckovis uppdatering. Kod som saknas blir ”Saknas”, okänd kod blir kontrollfråga. | Byggt som registerbakgrund i snapshot v2, ingen ny fråga eller kontrollattest. Gamla v1-summor och källhänvisningar bevaras. |
| Kommun/adress, juridisk form, SNI, verksamstatus | Registerbakgrund. Adress/kontaktuppgifter kan innehålla personuppgifter och behövs inte för nuvarande kanoniska intagsfält. | Befintlig form/SNI/status visas; kontaktdata projiceras inte in i snapshot. SNI besvarar inte tjänstelistan. |
| Anställda/omsättning | Klasser; omsättningsklass i tkr med `omsAr`. Anställdas klass motsvarar inte dagens personer inklusive ägare. | Visas i expanderbar bakgrund; exakta tal och relevant period behöver eget underlag. |
| Bolagsverket HVD organisationsform/registrerad verksamhet | Separat gratis åtkomst med OAuth2 `client_id`/`client_secret`; organisationsform FL kan identifiera filial. SCB:s juridiska form 96 bevisar inte filial. | Nästa möjliga adapter, ännu inte byggd. Kräver verifierat maskinellt kontrakt och behörighet. |
| Bolagsverket digital årsredovisning | iXBRL från 2020; inte alla inskannade PDF. Exakt historisk omsättning först efter kontroll av orgnr, taxonomi, period, valuta/enhet och bolag/koncern. Medelantal anställda ersätter inte aktuellt personantal. | Utred separat import/adapter efter kontraktskontroll. Ingen gissad omsättning ur SCB-klassen. |
| Skatteverket företagsinformation | Manuell e-tjänst för skatte-/arbetsgivarstatus samt beslutade arbetsgivaravgifter. Inget planerat öppet API för tjänsten enligt utvecklingssidan. Beskattningsengagemang har separat partner-, OAuth- och behörighetsflöde. | Ingen genväg genom automatiserad skrapning eller gissad API-åtkomst. SCB-status används som avgränsad bakgrund. |
| Faktiskt tjänsteutbud | Byråns egna uppdragslistor/avtal och verksamhetsgenomgång. | Elva erbjudandefrågor kan bekräftas tillsammans med gemensamt underlag. Omarkerade tjänster blir ”nej” bara efter uttrycklig bekräftelse av hela listan. Osäkra tjänster kan fortfarande besvaras enskilt som ”Vet inte”. |
| Kund-/uppdrags-/intäktsstatistik, kanaler/geografi, kontrollernas genomförande | Offentligt organisationsnummer ger inte dessa verksamhetsfakta. | Manuellt pilotintag för pilotbyrån och inventering av faktiska exporter återstår. Därefter formatanpassad CSV/XLSX-import, ingen generell import före piloten. |

Statuskoderna kontrollerades mot [SCB:s variabelbeskrivning 2026-10-09](https://www.scb.se/contentassets/8a8eb5c3d45f461ea93482f8e8d4de4f/variabelbeskrivning-afr_261009.pdf), s. 5, 10 och 14: F-skatt 0/1/9; moms även 3 (via representant); arbetsgivare även 2/3/4 (privatarbetsgivare/representant/ambassad eller konsulat). Ingen av dessa betyder att byråns AML-kontroller har utförts. SCB:s registerdatum är inte datum för användarens bekräftelse.

Bolagsverkets [HVD-sida](https://bolagsverket.se/apierochoppnadata/hamtaforetagsinformation/vardefulladatamangder/apiforvardefulladatamangder.5513.html), [nedladdningsbara filer](https://bolagsverket.se/apierochoppnadata/hamtaforetagsinformation/nedladdningsbarafiler.2517.html) och [API-frågor](https://bolagsverket.se/apierochoppnadata/driftochsupport/fragorochsvaromapierna.4611.html) gav CAPTCHA vid direktläsning. Innehåll och åtkomst har återkontrollerats i indexerade officiella sidtexter; ett körbart HVD-kontrakt har inte verifierats. Veckofiler över hela populationen är opraktiska för detta lokala intag och omfattar personidentiteter. Skatteverkets [företagsinformation](https://www.skatteverket.se/hamtaforetagsinformation) och [utvecklingsområde](https://www.skatteverket.se/omoss/digitalasamarbeten/utvecklingsomraden/foretagsuppgifter.4.339cd9fe17d1714c0773a24.html) återkontrollerades. Beskattningsengagemangs tillgängliga tjänstebeskrivning är version 1.2 daterad 2024-05-23; nytt integrationskontrakt behövs innan bygge.

**Robusthet och användning:** hämtning ändrar inga profilsvar. Bekräftelser gör inga nya nätanrop. Valda svar valideras först i minnet och sparas sedan med ett CAS-sparande; sista svarsfel lämnar profilen oförändrad. Avvikande sparade registervärden kräver uttryckligt ersättningsval. Gammal profilrevision/bild, fel byrå, ogiltigt urval och historiska/framtida datum avvisas. Timeout/503 behåller tidigare bild och profil. SCB-nyckel kan anges i lösenordsfält för den lokala sessionen, aldrig återges i HTML/fel eller lagras i profiler/snapshots; miljövariabel fungerar fortsatt. Bekräftande roll är ett redigerbart förslag, senaste framgångsrikt sparade roll i sessionen återanvänds. Källa återanvänds inte som om den belägger nya manuella uppgifter.

**Prestanda:** samma profilläsning används till frågor, täckning och rendering; kompatibilitetsvyn beräknas en gång för översiktstabellen. Ingen cache av belägg mellan förfrågningar. Progressen visar bekräftade uppgifter och frågor som faktiskt kan besvaras nu, medan fullständighets-/dokumentgrinden fortsatt prövar allt obligatoriskt underlag.

Mätning 2026-10-11: 100 HTTP-mätningar per fall efter tre uppvärmningar, riktig YAML-lagring och samma syntetiska profiler/regelbas. Resultat och reproducerbart skript finns i [prestandaunderlaget](intag-prestanda-2026-10-11.json).

| Syntetiskt fall | Median före → efter | Minskad svarstid | p95 före → efter |
|---|---|---|---|
| Tom profil, frågerutt | 148,4 → 104,0 ms | 30,0 % | 167,9 → 109,7 ms |
| Tom profil, översikt | 148,2 → 102,6 ms | 30,7 % | 167,9 → 105,4 ms |
| Delvis profil, frågerutt | 43,4 → 39,9 ms | 8,0 % | 45,3 → 40,5 ms |
| Delvis profil, översikt | 44,1 → 40,0 ms | 9,2 % | 44,8 → 40,5 ms |
| Komplett profil, frågerutt | 245,8 → 129,9 ms | 47,2 % | 264,7 → 132,6 ms |
| Komplett profil, översikt | 179,7 → 130,6 ms | 27,3 % | 198,3 → 148,0 ms |

”Tom” saknar bekräftade grunduppgifter, ”delvis” har 20 fixturuppgifter och ”komplett” är en komplett syntetisk profil. Rutter utan nästa fråga faller tillbaka till översikten. Mätningen är sekventiell med en lokal användare, inte ett lastprov. Annan testaktivitet förekom under delar av mätningen; resultatet ska ses som en lokal jämförelse, inte garanterad latency eller SCB-nätverkshastighet. Registergodkännande för alla tre förslag minskar från tre separata godkännanden till ett; hela tjänsteutbudet från elva separata svar till ett samlat sparande. Verklig användartid i piloten är inte mätt.

### 14.4 Fler källor, underlagsval och tydlig leverans 2026-10-11

Användaren vill fylla i verkliga luckor och godkänna tillgängliga uppgifter med färre upprepningar. Denna fortsättning bygger avgränsade underlagsval och ytterligare ett villkorat SCB-förslag. Den bygger ingen ny extern anslutning och använder inga personliga nycklar eller verkliga uppgifter från pilotbyrån.

| Källa | Nytta utöver dagens SCB-förslag | Åtkomst och nästa steg |
|---|---|---|
| [Bolagsverket HVD](https://bolagsverket.se/apierochoppnadata/hamtaforetagsinformation/vardefulladatamangder/apiforvardefulladatamangder.5513.html) | Registrerad verksamhet och organisationsform, bland annat filial; tillgängliga digitala årsredovisningar kan ge exakt historisk omsättning. | Högst prioriterad nästa företagsadapter. Avgiftsfri men separat registrering/OAuth2 med `client_id`/`client_secret`; SCB-nyckeln ger inte åtkomst. iXBRL från 2020 omfattar inte alla inskannade PDF. Kontrollera det maskinella kontraktet och orgnr, period, bolag/koncern, valuta/enhet och taxonomi före överföring. Inte byggd. |
| [Skatteverkets företagsuppgifter](https://www.skatteverket.se/omoss/digitalasamarbeten/utvecklingsomraden/foretagsuppgifter.4.339cd9fe17d1714c0773a24.html) | Skatte-/arbetsgivarstatus och beslutade arbetsgivaravgifter. F-skatt/moms/arbetsgivarregistrering visas redan via SCB i programmet. | Utvecklingssidan säger att ett öppet API för e-tjänsten Hämta företagsinformation inte planeras. Beskattningsengagemang har separat autentisering/behörighet. Ingen byggd adapter eller automatiserad e-post/skrapning. |
| [Polisen/Samordningsfunktionens rapporter](https://polisen.se/om-polisen/samordning-mot-penningtvatt-och-finansiering-av-terrorism/rapporter/) och Länsstyrelsernas vägledningar | Hot, sårbarheter och riskresonemang för allmän riskbedömning; inga svar på pilotbyråns faktiska kundantal eller kontrollgenomförande. | Befintlig regelbas har redan versionerade myndighetskällor. **Ny gapnotering:** nationell riskbedömning 2026 om juridiska personer och konstruktioner, september 2026, behöver inventeras mot befintligt källurval. Den har inte integrerats eller ändrat risknivåerna i denna fortsättning. |
| [EU:s högrisktredjelandslista](https://finance.ec.europa.eu/financial-crime/anti-money-laundering-and-countering-financing-terrorism-international-level_en) och [FATF:s listor](https://www.fatf-gafi.org/en/countries/black-and-grey-lists.html) | Underlag för geografisk risk och separata åtgärdsprövningar. | Listorna har olika betydelse. Ingen liveintegration finns i M2. Frys rätt version/giltighet, bevara källan och granska beslutsgrenarna innan en framtida integration påverkar motorn. Sanktionslistor är ett separat spår; en landlista är ingen personsanktionskontroll. |
| pilotbyråns egna kund-, uppdrags-, ekonomisystems- och AML-underlag | Aktiv kundbas, antal/intäkter per faktisk tjänst, kanaler, anknytningar och genomförda kontroller. Här finns den största potentialen att minska återstående manuell inmatning. | Gör först det beslutade manuella pilotintaget och inventera faktiska exporter/definitioner. Bygg därefter lokal CSV/XLSX-import för just det verifierade formatet. Pilot och ny import återstår. |

SCB:s [variabelbeskrivning](https://www.scb.se/vara-tjanster/bestall-data-och-statistik/foretagsregistret/variabelbeskrivning/?menu=open), avsnitt Ägarkategori, anger kod **41** för privat svenskkontrollerade företag utan koncerntillhörighet; 42 betyder med koncerntillhörighet och 50 utlandskontrollerade. `jeFullData.agKat` finns i det kontrollerade [OpenAPI-kontraktet](https://apiafr.scb.se/swagger/v1/swagger.json) med samma kontrollsumma som §14.3. Ny snapshotversion 3 bevarar koden. Endast 41 ger ett **villkorat förslag** `P-ORG.koncernmoder = false`: logiskt kan ett företag utan koncerntillhörighet inte vara yttersta moderföretag i en koncern. Detta är en avgränsad inferens från registerkategorin, inte en ny uppgift om kontrollgenomförande eller ett bevis på dagens struktur. Vyn visar begränsningen; användaren behöver kontrollera och bekräfta. 42/50/okänd/saknad kod ger inget sådant förslag. Varken filial eller koncernens moderidentitet härleds. V1/v2 behåller exakt tidigare kanoniskt format och summa.

**Måste en extern källa anges för allt?** En användbar spårbarhet behöver visa vad svaret grundar sig på, men varje enkel verksamhetsfakta behöver inte en separat uppladdad fil eller offentlig webblänk. Det byggda intaget erbjuder nu ”Egen kännedom om verksamheten” för en begränsad lista av enkla fakta och beskrivningar. Valet sparas tillsammans med roll/datum när användaren bekräftar. Numeriska uppgifter, statistikperioder, sektorsmotiveringar och kontroller har inte detta snabbval. Egna tidigare bekräftade och aktuella hänvisningar kan återanvändas där de passar: ekonomistatistik, kundstatistik och erfarenhetsstatistik hålls isär; kontrollunderlag delas bara inom samma kontroll och fas. SCB-bildens hänvisning återanvänds inte som generell källa till manuella svar. Gammal flik, fel kategori/period, inaktuell uppgift eller okänd valtoken avvisas vid sparandet. Detta beskriver programmets produktval och beläggpolicy, inte ett påstående om ett lagkrav på separat extern källa till varje formulärfält.

**Faktisk leverans nu:** lokal intervju → deterministisk bedömning → uttryckligt AI-skrivsteg → maskinell granskning → `allman-riskbedomning-UTKAST.docx`. Dokumentet innehåller verksamhetsbeskrivning, risker per tjänst, kontroller och åtgärder; åtgärds-/granskningsbilaga ingår vid öppna fynd. Namn och beskrivande fritext sätts in lokalt. Separata rutindokument, individuella kundriskbedömningar och ett fastställt dokument skapas inte av intagets skrivknapp. Grund-/översiktssidan visar nu detta innan användaren fyller i eller skriver. Juridiska/metodiska sakkunniggrindar och senare sakgranskning/fastställelse är oförändrade.

**Verifiering av fortsättningen:** RED före produktionsändring för underlagsval, kategori-/periodgränser, okänt/stale-form och tydlig leverans; separat RED för det villkorade koncernförslaget. Efter rättning **83 fokuserade prov passerade (35,50 s)** och hela berörda intag-/företagsdatapaketet gav **172 passerade (186,90 s)**. Fristående teknisk granskning fann inga konkreta fynd i den avgränsade ändringen. Syntetiskt webbläsarprov verifierade SCB-kod 41 med uttrycklig bekräftelse, egen kännedom, kundunderlag/period som återanvänds och sparas i nästa kundfråga samt att samma underlag inte föreslås för omsättning. Bildbevis ligger utanför Git i `/Users/gt/.codex/visualizations/2026/10/11/01a12a55-3718-74f2-bc3b-588e958dab72/intag-underlagsval.png`. Slutlig fullsvit redovisas i STATUS och registerplanen. Denna fortsättning har inte en ny prestandamätning; tidsvinsten i §14.3 gäller den tidigare renderingsändringen.


### 14.5 Bolagsverket HVD: verifierat kontrakt och första läsväg 2026-10-14

Användaren har nu tillgång till HVD och har uttryckligen godkänt en första version med lokalt kommando för företagsuppgifter och dokumentlista. Det ersätter tidigare uppgiften att åtkomst och körbart kontrakt saknas; intagsintegration och årsredovisningstolkning är fortfarande senare arbete.

Primärkällan är [Bolagsverkets HVD v1 i utvecklarportalen](https://portal.api.bolagsverket.se/devportal/apis/ff8f9a91-1fdd-4705-8836-c1906581162f/overview). Offentlig OpenAPI och anslutningsanvisning version 1.01 (2025-02-10) har hämtats direkt från portalens dokument-API. Exakta adresser, hämtningstid, kontrollsummor och OpenAPI finns i [kontraktsfilen](bolagsverket-hvd-v1-kontrakt.json). Webbplatsens CAPTCHA har inte kringgåtts; utvecklarportalens publika dokumentation var tillgänglig.

- OAuth2 client credentials mot `https://portal.api.bolagsverket.se/oauth2/token`, formulär med grant_type, client_id, client_secret och scope. Läsning använder `vardefulla-datamangder:read`; driftkontroll använder separat ping-scope. Giltigheten kommer från expires_in.
- API-bas: `https://gw.api.bolagsverket.se/vardefulla-datamangder/v1`. POST organisationer och dokumentlista med identitetsbeteckning. GET dokument/{dokumentId} finns i kontraktet men byggs inte i första versionen.
- Använda uppgifter: namn med namntyp, organisationsform, juridisk form, verksamhetsbeskrivning, verksamstatus, registreringsdatum, avregistrering/orsak, pågående förfaranden, SNI och postadress. Dataproducent (Bolagsverket/SCB) följer med per uppgiftsgrupp. Saknad grupp och gruppfel redovisas separat, aldrig som bekräftat nej.
- Dokumentlistan ger dokument-id, filformat, rapporteringsperiodens slut och registreringstidpunkt. Datum behålls som levererade: OpenAPI har strängtyper men flera officiella exempel använder millisekundstal. Ingen gissad kalenderomräkning, ekonomisk tolkning eller påstående om fullständig inlämningshistorik görs.
- Hämtade uppgifter är lokal registerbakgrund, inte bekräftade profilsvar eller nya AML-kontrollbelägg. Ingen riskregel eller sakkunnigstatus ändras. Verkliga svar och nycklar får inte bli testfixturer eller läggas i Git.

Manuell kontroll med användarens uppgifter: autentisering lyckades, expires_in var 3600 sekunder, driftkontroll gav HTTP 200 och OK. Token sparades inte eller skrevs ut. Det styrker åtkomst till token/ping, inte att ett visst företag eller dokument kan hämtas. Företagsuppslag redovisas separat efter att användaren angett organisationsnummer. Automatiska prov använder enbart syntetisk transport och syntetiska svar.


#### Vad HVD kan tillföra i Riskanalys

Kontrollerat även mot portalens officiella Code lists 2026-10-14 (adress och kontrollsumma i kontraktsfilen). Det här är en kartläggning, inte automatiska profilförslag eller nya riskregler.

| Uppgift | Finns i kontraktet | Användning och begränsning |
|---|---|---|
| Namn och registrerad verksamhetsbeskrivning | Ja, flera namntyper kan förekomma | Grundtext för manuell granskning. Registrerad verksamhet bevisar inte dagens faktiska tjänsteutbud. |
| Organisationsform | Ja, bland annat AB, HB, KB, FL, BFL, EK, BRF | FL/BFL är uttryckliga filialformer, till skillnad från SCB:s generella kod för utländsk juridisk person. Kan senare ge ett källbundet förslag, inte automatiskt bekräftat svar. |
| Ideella föreningar/stiftelser | Koder I/S avser sådana som bedriver näringsverksamhet | API:t ska inte beskrivas som heltäckande för alla ideella föreningar och stiftelser. |
| Registreringsdatum, verksamstatus, avregistreringsdatum/orsak | Ja | Registerbakgrund. Datum i ett aktuellt svar är inte fullständig historik och ger inte ensamt kundens verkliga verksamhetsålder. |
| Pågående förfaranden | Kodlistan omfattar konkurs, likvidation, företagsrekonstruktion, fusion/delning, gränsöverskridande ombildning m.m. | Underlag för kontrollfrågor. Ett tomt/felaktigt svar är inte ett intyg på frånvaro. Inga AML-risknivåer härleds här. |
| SNI och postadress | Ja | Registrerad bransch/adress, inte faktiskt tjänsteutbud eller geografiska kundrisker. Postadress bevisar inte säteslän. |
| Registreringsland, reklamsparr och namnskyddslopnummer | Ja | Finns i API men ingår inte i den första lokala projektionen eftersom de inte behövs i det godkända kommandots registerbakgrund. |
| Årsredovisningar | Lista med filformat, periodslut, registreringstidpunkt och dokument-id; separat ZIP-hämtning | Nästa steg kan undersöka faktiskt filformat och läsa bokslutsuppgifter. Dokumentlistan i sig ger inte omsättning, resultat, eget kapital eller medelantal anställda. |
| Styrelse, firmatecknare, verkliga huvudmän, ägarandelar | Inga separata fält/operationer i HVD v1-kontraktet | Får inte utlovas med denna behörighet. Att andra API:er syns i portalen betyder inte att användaren har åtkomst. Eventuella namn i årsredovisningar är inte ett aktuellt styrelse-/ägarregister. |
| PEP, sanktionsträffar, kundmix, antal rapporter, kontrollutfall | Saknas i HVD v1-kontraktet | Kan inte fyllas i från detta API. Kräver andra underlag och vid behov separat behörig tjänst. |

För intaget prioriteras senare registrerad verksamhetsbeskrivning och tydlig organisationsform, med källvisning och uttrycklig bekräftelse. Bokslutsimport kräver ytterligare kontroll av identitet, period, valuta/enhet, taxonomi och bolag kontra koncern. Ingen sådan överföring är byggd i den första läsvägen.
