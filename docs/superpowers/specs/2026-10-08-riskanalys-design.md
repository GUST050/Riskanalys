# Riskanalys – designspecifikation

**Status:** Förslag 2026-10-08. Ej godkänd för implementation.
**Underlag:** [researchsammanställningen](../../research/README.md).
**Nästa steg:** Granskning av denna spec. Därefter implementeringsplan.

---

## 1 Syfte

Programmet tar fram och förvaltar den dokumentation som en verksamhetsutövare behöver enligt penningtvättsregelverket: allmän riskbedömning, rutiner och riktlinjer, kundriskmodell med mera. Dokumentationen ska vara anpassad till den egna verksamheten, och varje påstående ska gå att spåra till en källa.

Målet är att varje tillämpligt krav i lag, föreskrift och tillsynspraxis

- är adresserat i dokumenten,
- är motiverat med verksamhetens egna uppgifter,
- är spårbart till sin källa,
- och går att visa som infört och kontrollerat över tid.

Programmet ger underlag. Verksamhetsutövaren fastställer dokumenten och bär ansvaret. Inget resultat utlovar att tillsynen godkänner dokumentationen.

## 2 Målgrupp och avgränsning

| Fas | Användare | Omfattning |
|---|---|---|
| 1 | Redovisnings- och konsultbyråer under Länsstyrelsens tillsyn, för deras egen efterlevnad | Verksamhetsnivå: allmän riskbedömning, rutiner, kundriskmodell (mall), kravmatris, drift |
| 2 | Samma | Kundnivå: kundkännedom och riskprofil per kund, misstankelogg, femårsregister |
| 3 | Övriga verksamhetsutövare under Länsstyrelsens tillsyn | Nya sektorspaket (skatterådgivare, bolagsbildare, varu- och konsthandlare, pantbanker m.fl.) |
| 4 | Alla | Regelpaket för EU:s AMLR (gäller från 2027-07-10) och ny svensk penningtvättslag |

Programmet byggs först som en kärna med kommandoradsgränssnitt. Webbgränssnitt eller tjänsteleverans byggs senare och anropar samma kärna.

## 3 Fattade beslut

| Beslut | Val | Datum |
|---|---|---|
| Användare | Konsultbyråer först, sedan andra företag | 2026-10-08 |
| Omfattning | Alternativ C: verksamhetsnivå först, datamodell förberedd för kundnivå | 2026-10-08 |
| Arkitektur | Alternativ 2: regelbas och deterministisk motor, AI som skribent | 2026-10-08 |
| Byggare | Ägaren bygger själv med Claude Code och Codex. Koden ska vara enkel att läsa och väl testad. | 2026-10-08 |
| Gränssnitt | Kärna och CLI först, webb senare | 2026-10-08 |

## 4 Grundprinciper

1. **Verksamhetsanpassning är produkten.** Generisk malltext är det tillsynen oftast underkänner (tillsynsrapport 2026:14). Programmet ska hellre stoppa än leverera generisk text.
2. **Spårbarhet åt två håll.**
   - Varje påstående om risk pekar på en post i regelbasen, som i sin tur pekar på en källa.
   - Varje påstående om verksamheten pekar på en uppgift i byråprofilen eller markeras `[VERIFIERA]`.
3. **AI fattar inga beslut.** Risknivåer, poäng och regler kommer från motorn. AI:n formulerar och analyserar inom ett givet underlag och får inte införa nya fakta.
4. **Förklarbar metod.** Varje regel i motorn har en klartextförklaring och en källa. AMLA:s utkast kräver att verksamhetsutövaren förstår och kan förklara metoden även när tredje part har hjälpt till.
5. **Lagkrav hålls isär från verksamhetens egna val.** Varje regel märks *ska-krav*, *allmänt råd*, *tillsynspraxis* eller *verksamhetens val*.
6. **Risk före åtgärder.** Inneboende risk bedöms utan kontroller. Kontroller får sänka risken bara när deras effekt är belagd.
7. **Datum är krav.** Det gäller utvärdering, uppdatering, fastställelse, identitetskontroll och utbildning.
8. **Proportionalitet.** Dokumentens omfattning styrs av verksamhetens storlek och komplexitet, inte av hur mycket text AI:n kan producera.
9. **Versionerad regelbas.** Regelverk, listor och riskbedömningar ändras. Allt har giltighetsdatum, och en bedömning låser den version den gjordes mot.
10. **Inga personuppgifter i fas 1.** Verksamhetsdokumenten innehåller inte kunduppgifter.

## 5 Arkitektur

Strukturen bygger på samma lagerprincip som NIST:s OSCAL: katalog, urval, genomförande, granskning och åtgärder. Varje lager hänvisar till föregående lager i stället för att kopiera det.

```
 KÄLLOR ─► KRAVREGISTER + KUNSKAPSKATALOGER ─► REGELPAKET
                                                   │
 BYRÅPROFIL ───────────────────────────────────────┤
                                                   ▼
                                              RISKMOTOR ─► TEXTGENERATOR ─► GRANSKARE ─► EXPORT/FASTSTÄLLELSE
                                                   ▲                                          │
                                                   └──────────────── DRIFT ◄──────────────────┘
```

### 5.1 Byggblock

| # | Block | Ansvar | Indata | Utdata | AI |
|---|---|---|---|---|---|
| 1 | Källregister | Förteckning över alla källor med metadata | Dokument, webbsidor | `regelbas/kallor/*.yaml` | Nej |
| 2 | Kravregister | Ett atomärt krav per post med källa och villkor | Källor | `regelbas/krav/*.yaml` | Nej (sakkunnig) |
| 3 | Kunskapskataloger | Tjänster, hot, sårbarheter, kundfaktorer, kontroller, varningssignaler, bristmönster | Källor | `regelbas/kataloger/*.yaml` | Nej (sakkunnig) |
| 4 | Referensdata | Landlistor, sanktionsfiler, nationell riskbedömning, utsatta områden | Myndighetskällor | `regelbas/referensdata/` | Nej |
| 5 | Regelpaket | Urval och parametrar för sektor, län, regelverk och datum | 2–4 | `regelbas/regelpaket/*.yaml` | Nej |
| 6 | Byråprofil | Verksamhetens uppgifter med status och källa | Intag | `byraer/<id>/1-profil/` | Förslag ur dokument |
| 7 | Riskmotor | Inneboende risk, kontroller, kvarstående risk, kundmodell | 5, 6 | `byraer/<id>/2-bedomning/` | Nej |
| 8 | Textgenerator | Avsnittstext med referenser | 7, sektionsunderlag | `byraer/<id>/3-utkast/` | Ja |
| 9 | Granskare | Täckning, bristmönster, provtillsyn | 2, 3, 7, 8 | `byraer/<id>/4-granskning/` | Delvis |
| 10 | Export | Word och PDF, fastställelse, bilagor | 8, 9 | `byraer/<id>/5-export/` | Nej |
| 11 | Drift | Versionslogg, påminnelser, utlösande händelser, belägg | Allt | `byraer/<id>/6-drift/` | Nej |

### 5.2 Gränssnitt mellan blocken

- Varje block läser och skriver validerade datastrukturer (pydantic-modeller). Filformatet är YAML för regelbas och profil och JSON för maskingenererade resultat.
- Ett block får bara läsa det föregående blockets utdata, aldrig dess interna logik.
- Varje körning skriver ett manifest med regelbasversion, profilversion, modellversion och tidpunkt, så att en bedömning går att återskapa.

## 6 Datamodell

### 6.1 ID-konventioner

| Objekt | Format | Exempel |
|---|---|---|
| Källa | `SRC-<kortnamn>` | `SRC-PTL`, `SRC-14FS-2024-11`, `SRC-TS-2026-14`, `SRC-NRA-2024-25` |
| Krav | `KRV-<källa>-<nr>` | `KRV-LSF-012` |
| Tjänst | `T-<sektor>-<nr>` | `T-RED-01` (löpande bokföring) |
| Hot | `H-<nr>` | `H-01` (osanna fakturor) |
| Sårbarhetsfaktor | `S-<område>-<nr>` | `S-KUND-03`, `S-KANAL-01`, `S-GEO-02`, `S-VERK-04`, `S-TJ-01` |
| Kundfaktor | `KF-H-<nr>` / `KF-L-<nr>` | `KF-H-02` (kontantintensiv) |
| Kontroll | `C-<nr>` | `C-07` (bankavstämning mot underlag) |
| Varningssignal | `V-<nr>` | `V-15` |
| Bristmönster | `B-<nr>` | `B-04` (tjänster klumpade) |
| Profiluppgift | `P-<område>.<namn>` | `P-ORG.antal_anstallda` |
| Avsnitt | `D-<dokument>.<avsnitt>` | `D-ARB.6.1` |

ID:n är stabila. En post som utgår markeras `utgången` och raderas inte.

### 6.2 Huvudobjekt

**Källa**
```yaml
id: SRC-14FS-2024-11
titel: Länsstyrelsen i Västra Götalands läns föreskrifter och allmänna råd om åtgärder mot penningtvätt och finansiering av terrorism
typ: föreskrift            # lag | förordning | föreskrift | allmänt_råd | vägledning | tillsynsrapport | riskbedömning | beslut | eu_förordning | eu_riktlinje_utkast
utgivare: Länsstyrelsen i Västra Götalands län
beslutad: 2024-05-22
galler_fran: 2024-07-01
galler_till: null
geografi: [Västra Götaland, Halland, Värmland, Örebro, Dalarna, Gävleborg]
url: https://...
hamtad: 2026-10-01
kontrollsumma: sha256:...
```

**Krav**
```yaml
id: KRV-LSF-003
kalla: SRC-14FS-2024-11
lagrum: "2 kap. 3 §"
typ: ska_krav              # ska_krav | allmänt_råd | tillsynspraxis | verksamhetens_val
text: Den allmänna riskbedömningen ska utvärderas minst en gång per år och datum för utvärdering och uppdatering ska framgå.
galler_om: { sektor: [alla], har_anstallda: null }
belagg: [dokument, datum]  # dokument | datum | logg | beslut | register
uppfylls_i: [D-ARB.10]     # fylls av regelpaketet
verifierad_av: null        # sakkunnig + datum
```

**Tjänst, hot, sårbarhet**
```yaml
- id: T-RED-01
  namn: Löpande bokföring
  hot: [H-01, H-02, H-03, H-05, H-11, H-14, H-15]
  kallor: [SRC-VAGL-2025-03, SRC-NRA-2024-25]
- id: H-01
  namn: Osanna och falska fakturor
  beskrivning: ...
  kallor: [SRC-VAGL-2025-03, SRC-EBM-2025]
  galler_tf: false
- id: S-KUND-01
  namn: Kunder i branscher med förhöjd risk
  profilfragor: [P-KUND.andel_riskbransch]
  paverkar: { sannolikhet: +1, nar: "P-KUND.andel_riskbransch >= 0.2" }
  kallor: [SRC-NRA-2024-25, SRC-FIPO-2026]
```

**Profiluppgift**
```yaml
id: P-ORG.antal_anstallda
varde: 12
status: bekräftad          # bekräftad | föreslagen | saknas
kalla: "Årsredovisning 2024/25"
datum: 2026-10-05
bekraftad_av: FfR
```

**Bedömning per tjänst**
```yaml
tjanst: T-RED-01
erbjuds: true
inneboende:
  sannolikhet: hög
  konsekvens: betydande
  niva: hög
  motiveringsunderlag: [H-01, H-02, S-KUND-01, S-KANAL-02, S-VERK-03]
  regelspår: [BT-SANN-04, BT-MATRIS-07]
terrorfinansiering: { sannolikhet: låg, konsekvens: allvarlig, niva: måttlig }
sanktionsrisk: { niva: låg }
kontroller:
  - { id: C-07, utformning: finns, genomforande: ej_belagt }
kvarstaende: { niva: hög, regel: "ej belagd kontroll sänker inte risken" }
```

**Textstycke** (AI-utdata)
```yaml
avsnitt: D-ARB.6.1
stycken:
  - typ: motivering        # beskrivning | analys | motivering | scenario
    text: "..."
    referenser: [H-01, S-KUND-01, P-KUND.andel_riskbransch]
oklarheter:
  - fraga: "Har byrån bankkoppling för alla kunder?"
    saknad_uppgift: P-KANAL.bankdata_andel
```

**Granskningsfynd och åtgärdspunkt**
```yaml
id: F-2026-10-08-014
typ: bristmonster         # tackning | sparbarhet | bristmonster | provtillsyn
regel: B-07
allvar: hög               # blockerande | hög | medel | låg
avsnitt: D-ARB.5.3
beskrivning: Geografiska riskfaktorer kopplas bara till sanktionslistor.
atgard: Beskriv kundernas och motparternas utlandskopplingar och lokala riskfaktorer.
status: öppen
```

## 7 Riskmetod

### 7.1 Steg

Stegen följer både Länsstyrelsens föreskrifter (2 kap. 2 §) och AMLA:s utkast till riktlinjer (fyra minimikrav):

1. **Verksamhetsöversikt.** Organisation, storlek, kunder, tjänster, kanaler, geografi, AML-organisation, utlagd verksamhet och ny teknik.
2. **Identifiera tjänster.** Varje tjänst bedöms för sig. En tjänst som inte erbjuds markeras "erbjuds ej" men finns kvar i bedömningen.
3. **Hot per tjänst.** Hämtas ur hotkatalogen, med källor, och kompletteras med verksamhetens egna erfarenheter (rapporter till Finanspolisen, nekade kunder).
4. **Sårbarheter.** Kunder, kanaler, geografi, verksamhetsspecifika omständigheter och tjänstens egenskaper, matchade mot byråprofilen.
5. **Inneboende risk per tjänst.** Sannolikhet × konsekvens enligt beslutstabeller. Terrorfinansiering och kringgående av riktade finansiella sanktioner bedöms separat.
6. **Kontrollernas kvalitet.** Utformning (finns kontrollen i rutinerna?) och genomförande (finns belägg i driften?).
7. **Kvarstående risk** per tjänst och för verksamheten som helhet.
8. **Prioriterade åtgärder** som förs till rutinerna och åtgärdslistan.

### 7.2 Skalor (standardvärden, verksamhetens val)

| Skala | Nivåer |
|---|---|
| Sannolikhet | låg, medel, hög |
| Konsekvens | begränsad, betydande, allvarlig |
| Risk | låg, måttlig, hög, mycket hög |
| Kontrollkvalitet | fungerar, mindre brister, betydande brister, saknas eller ej belagd |

Riskmatris (standard):

| Sannolikhet \ Konsekvens | Begränsad | Betydande | Allvarlig |
|---|---|---|---|
| Låg | låg | måttlig | måttlig |
| Medel | måttlig | måttlig | hög |
| Hög | måttlig | hög | mycket hög |

### 7.3 Regler för kvarstående risk

- Kvarstående risk är aldrig högre än inneboende risk.
- En kontroll som inte är belagd i driften sänker inte risken.
- En kontroll som fungerar sänker risken högst ett steg per tjänst.
- Inneboende risk som är hög eller mycket hög kan aldrig bli lägre än måttlig (AMLA: hög inneboende risk kan inte helt tas bort med kontroller).
- Terrorfinansiering har alltid konsekvensen allvarlig. Beloppets storlek sänker inte konsekvensen.

### 7.4 Sammanvägning

- Tjänsterna vägs samman med dokumenterade vikter, som standard andel av kunder eller omsättning.
- Den samlade nivån får inte vara lägre än den högsta nivån bland tjänster som väger minst 20 % (standardvärde).
- Ingen enskild faktor får ensam avgöra resultatet (AMLA). Motorn redovisar varje faktors bidrag.
- Avvikelser från sektorns nivå i den nationella riskbedömningen ska motiveras. Granskaren flaggar annars.

### 7.5 Proportionalitetsnivå

| Nivå | Typfall | Effekt |
|---|---|---|
| Enkel | Få anställda, ett kontor, enkla tjänster, inga behörigheter i kundernas namn | Kortare, mer beskrivande dokument. Samma krav täcks. |
| Standard | Typisk redovisningsbyrå | Full analys per tjänst |
| Utökad | Många anställda, flera kontor, behörigheter, utländska kunder, koncern | Fler scenarier, funktioner för intern kontroll, tätare uppföljning |

Nivån beräknas av faktorerna i Länsstyrelsens föreskrifter 6 kap. 3 § (omsättning, anställda, verksamhetsställen, verksamhet, tjänster, komplexitet, riskbedömning) och kan justeras med motivering.

### 7.6 Kundriskmodell (mall för fas 1, motor för fas 2)

1. **Hinder.** Sanktionsträff, otillräcklig kundkännedom, misstanke. Arbetet stoppas tills hindret är undanröjt.
2. **Alltid hög risk.** PEP, högrisktredjeland och verksamhetens egna val (till exempel oförklarlig ägarstruktur).
3. **Riskfaktorer.** Poäng per faktor. Faktorerna härleds ur den allmänna riskbedömningen och lagens exempel på hög risk.
4. **Lågriskfaktorer.** Härleds ur lagens exempel på låg risk och verksamhetens val.
5. **Nivå och justering.** Poänggränser och regler för höjning och sänkning. En uppgift som inte är verifierad ger alltid det försiktiga svaret.

Faktorer, poäng och gränser är verksamhetens val och märks så.

### 7.7 Beslutstabeller

All logik i 7.2–7.6 ligger i `regelbas/beslutstabeller/*.yaml`. Varje rad har ID, villkor, utfall, källa, typ (ska-krav eller verksamhetens val) och en klartextförklaring. Varje rad har minst ett test.

## 8 AI-lagret

### 8.1 Uppgifter för AI

| Uppgift | Tillåtet | Förbjudet |
|---|---|---|
| Skriva avsnitt | Formulera beskrivningar, analyser, motiveringar och scenarier utifrån sektionsunderlaget | Nya fakta, siffror, nivåer eller källor |
| Föreslå profiluppgifter | Extrahera uppgifter ur verksamhetens egna dokument, märkta "föreslagen" | Markera uppgifter som bekräftade |
| Provtillsyn | Bedöma dokumenten mot en rubrik och rapportera fynd | Ändra text |

### 8.2 Flöde per avsnitt

1. Motorn bygger ett **sektionsunderlag**: relevanta krav, hot, sårbarheter, profiluppgifter med status, nivåer med regelspår och de bristmönster avsnittet ska undvika.
2. AI:n svarar i ett **låst schema** (strukturerade svar). Varje stycke bär `referenser`.
3. **Validering:**
   - Alla ID:n finns.
   - Alla siffror finns i underlaget.
   - Nivåer i texten stämmer med motorn.
   - Uppgifter som inte är bekräftade skrivs med `[VERIFIERA]`.
   - Inga förbjudna generiska formuleringar förekommer.
4. Underkänt svar körs om med valideringsfelen som återkoppling. Efter tre försök stoppar avsnittet med ett fynd.

### 8.3 Modell och drift

- Claude via Anthropics officiella Python-SDK. Standardmodell `claude-opus-5-5` med adaptiv tänkning och hög effort för skrivuppgifter.
- Strukturerade svar via SDK:ns `messages.parse` med pydantic-scheman. Claudes inbyggda källhänvisningar går inte att kombinera med strukturerade svar, så programmets egna referens-ID:n används.
- Regelbasens innehåll läggs först i anropet för att utnyttja prompt-cachning. Batch-API används vid omgenerering av många avsnitt.
- Leverantören kapslas in bakom ett gränssnitt. Fas 2 med personuppgifter kräver databehandling inom EU. Anthropics eget API erbjuder i dag bara `us` och `global`, så EU-behandling sker via Google Vertex AI eller Amazon Bedrock i EU-region.
- Modell, version, effort och tokenförbrukning loggas per körning.

## 9 Granskaren

| Nivå | Kontroll | Typ |
|---|---|---|
| 1 Täckning | Varje tillämpligt krav har minst ett avsnitt. Varje erbjuden tjänst har eget avsnitt med hot, sårbarheter och motiverad nivå. | Deterministisk |
| 2 Spårbarhet | Alla referenser finns. Alla verksamhetspåståenden pekar på profiluppgifter. Alla datum finns. | Deterministisk |
| 3 Bristmönster | Katalogen B (från tillsynsrapport 2026:14 och publicerade beslut) | Deterministisk och AI |
| 4 Provtillsyn | AI bedömer dokumenten som en handläggare utifrån föreläggandets punkter och en rubrik | AI |

Fynd med allvar *blockerande* stoppar exporten. Övriga fynd hamnar i åtgärdslistan.

Exempel på bristmönster (fullständig lista i researchsammanställningen):

- B-01 Den allmänna riskbedömningen saknas eller förväxlas med kundbedömning eller rutiner.
- B-02 Mallen är inte anpassad. Låg andel referenser till profilen och hög andel generiska formuleringar.
- B-04 Tjänster beskrivs tillsammans utan individuell analys.
- B-07 Geografi kopplas bara till sanktionslistor.
- B-10 Risknivå utan motivering.
- B-11 Alla nivåer låga utan hänsyn till den nationella riskbedömningen.
- B-12 Datum för utvärdering och uppdatering saknas.

## 10 Utdata i fas 1

| Dokument | Innehåll | Mottagare |
|---|---|---|
| Allmän riskbedömning | Översikt, tjänster, hot, sårbarheter, risk per tjänst, sammanvägning, slutsatser, omvärldsbevakning, utvärdering | Ledning, FfR, tillsyn |
| Metodbilaga | Skalor, matris, beslutsregler, vikter, källor och hur de använts | FfR, tillsyn |
| Rutiner och riktlinjer | Kundkännedom, övervakning, rapportering, bevarande, intern kontroll, personal | Alla |
| Arbetsinstruktioner per roll | Korta checklistor för konsult, FfR och ledning | Respektive roll |
| Kundriskmodell och kundformulär | Mall som följer modellen i 7.6 | Konsulter |
| Kravmatris | Krav, var det uppfylls, status beskrivet, infört och kontrollerat | FfR, tillsyn |
| Åtgärdslista | Öppna `[VERIFIERA]`, fynd och beslut som saknas | FfR |
| Index för tillsynspaket | Föreläggandets punkter kopplade till dokument och loggar | FfR |

## 11 Kommandon

```
riskanalys ny <byrå> --sektor redovisning --lan "Västra Götaland"
riskanalys intag <byrå> [--dokument fil...]
riskanalys bedom <byrå>
riskanalys skriv <byrå> [--avsnitt D-ARB.6.1]
riskanalys granska <byrå>
riskanalys exportera <byrå> --format docx,pdf
riskanalys drift <byrå>
riskanalys regelbas validera
```

## 12 Drift och livscykel

- **Fastställelse:** namn, roll och datum loggas. Versionsnumret låses.
- **Årlig utvärdering:** påminnelse senast tolv månader efter förra utvärderingen. En utvärdering utan ändring dokumenteras med motivering.
- **Utlösande händelser:** ny eller ändrad tjänst, ny marknad, ny version av en referenslista, ny nationell riskbedömning, ändrad föreskrift, hot mot personal, nya mönster i egen rapportering. Programmet jämför referensdatans version med den som bedömningen låste och visar vilka avsnitt som påverkas.
- **Belägg:** utbildningslogg, kontrollplan med resultat och stickprov. Belägg från driften blir indata till nästa års bedömning av kontrollernas genomförande.

## 13 Mappstruktur

```
riskanalys/
  AGENTS.md, CLAUDE.md          gemensamma regler för Codex och Claude
  pyproject.toml
  regelbas/
    kallor/  krav/  kataloger/  referensdata/  regelpaket/  beslutstabeller/
  src/riskanalys/
    modeller/  regelbas/  intag/  motor/  text/  granskning/  export/  drift/
    cli.py
  mallar/                       Word-mallar
  tester/
    regelbas/  motor/  text/  granskning/  facit/
  byraer/                       en mapp per byrå, utanför git
  docs/
```

## 14 Kvalitetssäkring

| Test | Vad det visar |
|---|---|
| Regelbasvalidering | Unika ID:n, inga brutna referenser, varje krav har källa, varje tjänst har hot |
| Beslutstabelltester | Ett test per rad plus gränsfall |
| Motortester | Kända profiler ger kända nivåer |
| Schematester för AI | Validering fångar påhittade ID:n, siffror och nivåer |
| Facitjämförelse | En referensbyrås tidigare underkända riskbedömning ska underkännas. Ett genomarbetat referensutkast ska i stort godkännas. |
| Granskar-eval | Bristmönster ur publicerade sanktionsbeslut används som testfall |
| Sakkunniggranskning | Regelbasen granskas av sakkunnig innan första leverans |

## 15 Säkerhet och dataskydd

- Byråmappar lagras utanför git.
- Inga personuppgifter i fas 1. Fas 2 kräver EU-hostad databehandling, kryptering, behörighetsstyrning och gallring enligt penningtvättslagens bevarandetider (fem år, högst tio).
- API-nycklar läses från miljövariabler. Aldrig i kod eller filer i repot.

## 16 Etapper

| Etapp | Innehåll | Klart när |
|---|---|---|
| M0 | Repo, `AGENTS.md`/`CLAUDE.md`, scheman, regelbasvalidering | `riskanalys regelbas validera` körs grönt i test |
| M1 | Regelbas v1 för redovisningsbyråer | Alla krav från lag, föreskrift och tillsynsrapport registrerade med källa |
| M2 | Intag och byråprofil | Referensbyrån har en komplett profil med status per uppgift |
| M3 | Riskmotor | Alla beslutstabeller testade. Referensbyrån får nivåer per tjänst. |
| M4 | Allmän riskbedömning från början till slut | Word-dokument som klarar granskaren utan blockerande fynd |
| M5 | Rutiner, kundmodell, instruktioner, kravmatris, tillsynspaket | Alla dokument i avsnitt 10 genereras |
| M6 | Drift och referensdatauppdatering | Ändrad högrisklista ger korrekt flaggning |
| M7 | Kundnivå med EU-hosting | Separat spec |
| M8 | Fler sektorer | Ett sektorspaket per sektor |
| M9 | AMLR-regelpaket | Klart före 2027-07-10 |

## 17 Risker och öppna frågor

| Risk | Hantering |
|---|---|
| Regelbasen tolkar lagen fel | Sakkunniggranskning, källa per post, tester |
| AI hittar på fakta | Låst schema, validering, inga fria fält för fakta |
| Generisk text slinker igenom | Bristmönster B-02 och provtillsyn |
| Regelverket ändras (AMLR, ny svensk lag) | Versionerade regelpaket med giltighetsdatum |
| Dokumenten blir för långa att följa | Proportionalitetsnivå och arbetsinstruktioner per roll |
| Föråldrad referensdata | Datum och kontrollsumma per lista, påminnelser |

Öppna frågor:

1. Innehållet i Länsstyrelsen Skånes föreskrifter (12FS 2024:8) behöver jämföras med Stockholms och Västra Götalands.
2. AMLA:s slutliga riktlinjer om verksamhetsövergripande riskbedömning väntas under fjärde kvartalet 2026.
3. Status för ny svensk penningtvättslag (SOU 2024:58).
4. Om Bolagsverket erbjuder elektronisk åtkomst till registret över verkliga huvudmän (påverkar fas 2).
5. Vem som gör sakkunniggranskningen av regelbasen.
