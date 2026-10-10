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
