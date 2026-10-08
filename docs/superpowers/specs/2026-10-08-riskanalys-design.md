# Riskanalys – designspecifikation

**Status:** Förslag, revision 2 (2026-10-08). Ej godkänd för implementation.
**Underlag:** [researchsammanställningen](../../research/README.md).
**Ändringar:** se [ändringsloggen](#20-ändringslogg) sist i dokumentet.
**Nästa steg:** granskning av revision 2. Därefter implementeringsplan för M0 och M1.

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
| 1 | Redovisnings- och konsultbyråer under Länsstyrelsens tillsyn, för deras egen efterlevnad | Verksamhetsnivå: allmän riskbedömning, rutiner, kundriskmodell (mall), kravmatris. **Inga kundärenden.** |
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
4. **En människa godkänner sakinnehållet.** Maskinell validering visar att referenserna finns, inte att formuleringarna stämmer. Varje avsnitt sakgranskas av en ansvarig person före fastställelse.
5. **Förklarbar metod.** Varje regel i motorn har en klartextförklaring och en källa. AMLA:s utkast kräver att verksamhetsutövaren förstår och kan förklara metoden även när tredje part har hjälpt till.
6. **Lagkrav hålls isär från metodval.** Varje regel märks med sin grund: *ska-krav*, *allmänt råd*, *tillsynspraxis*, *EU-utkast (ej bindande)* eller *metodval*.
7. **Risk före åtgärder.** Inneboende risk bedöms utan kontroller. Kontroller får sänka risken bara när deras effekt är belagd.
8. **Datum är krav.** Det gäller utvärdering, uppdatering, fastställelse, identitetskontroll och utbildning.
9. **Proportionalitet.** Dokumentens omfattning styrs av verksamhetens storlek och komplexitet, inte av hur mycket text AI:n kan producera.
10. **Allt underlag låses.** En fastställd version kan återskapas exakt ur manifest och kontrollsummor (avsnitt 5.3).
11. **Minsta möjliga personuppgifter.** Fas 1 behandlar inga kundärenden. Personuppgifter begränsas till de kategorier som anges i avsnitt 16, och AI-anrop innehåller inga personuppgifter.

## 5 Arkitektur

Strukturen bygger på samma lagerprincip som NIST:s OSCAL: katalog, urval, genomförande, granskning och åtgärder. Varje lager hänvisar till föregående lager i stället för att kopiera det.

```
 KÄLLOR ─► KRAVREGISTER + KATALOGER ─► REGELPAKET
                                           │
 BYRÅPROFIL (bekräftad) ───────────────────┤
                                           ▼
                                      BEDÖMNING ─► DOKUMENT ─► GRANSKNING ─► SAKGRANSKNING ─► FASTSTÄLLELSE
                                           ▲          (AI)      (maskinell)    (människa)       (låst paket)
                                           │                                                        │
                                           └──────────────────────── DRIFT ◄────────────────────────┘
                                 LAGRING: datamapp, manifest och kontrollsummor för allt ovan
```

### 5.1 Byggblock

| # | Block | Ansvar | AI |
|---|---|---|---|
| 1 | Källregister | Alla källor med metadata och kontrollsumma | Nej |
| 2 | Kravregister | Ett atomärt krav per post med källa, villkor och sakkunnigstatus | Nej (sakkunnig) |
| 3 | Kataloger | Tjänster, hot, sårbarheter, kundfaktorer, kontroller, varningssignaler, bristmönster | Nej (sakkunnig) |
| 4 | Referensdata | Landlistor, sanktionsfiler, nationell riskbedömning, utsatta områden | Nej |
| 5 | Regelpaket | Urval och parametrar för sektor, län, regelverk och datum | Nej |
| 6 | Byråprofil | Verksamhetens uppgifter med status, källa och bekräftelse | Nej i fas 1 |
| 7 | Bedömning | Inneboende risk, kontroller, kvarstående risk, kundmodell, regelspår | Nej |
| 8 | Dokument | Avsnittsunderlag, AI-text, rendering till Word och PDF | Ja (text) |
| 9 | Granskning | Täckning, spårbarhet, bristmönster, senare AI-provtillsyn | Delvis |
| 10 | Fastställelse | Dokumentstatus, sakgranskning, godkännande, låsning | Nej |
| 11 | Lagring | Datamapp, manifest, kontrollsummor, oföränderliga versioner | Nej |
| 12 | Drift (etapp M6) | Versionslogg, påminnelser, utlösande händelser, belägg | Nej |

### 5.2 Datamapp och gränssnitt

- **Byråns data ligger i en konfigurerad datamapp utanför repot.** Sökvägen anges med miljövariabeln `RISKANALYS_DATA`, som standard `~/RiskanalysData`. Programmet vägrar skriva byrådata innanför repots katalog. `.gitignore` är bara ett extra skydd.
- Varje block läser och skriver validerade datastrukturer (pydantic-modeller). Regelbas och profil lagras som YAML. Maskingenererade resultat lagras som JSON.
- Ett block läser bara föregående blocks utdata, aldrig dess interna logik.

```
$RISKANALYS_DATA/<byrå>/
  profil/          profil.yaml och bekräftelser
  bedomningar/     en mapp per körning
  utkast/          avsnittsunderlag, AI-svar, mänskliga ändringar
  granskning/      fynd och sakgranskningslogg
  faststallda/     låsta paket, ett per version
  manifest/        ett manifest per körning
```

### 5.3 Manifest och låsning

Varje körning skriver ett manifest. Det innehåller kontrollsumma (SHA-256) för varje artefakt som påverkat resultatet:

| Del | Exempel |
|---|---|
| Programversion | Git-commit och paketversion |
| Regelpaket | Paketfil och alla krav, kataloger och beslutstabeller det pekar på |
| Källor och referensdata | Varje källa och lista i den version som användes |
| Profil | Ögonblicksbild av den bekräftade profilen |
| Bedömning | Bedömningens JSON med regelspår |
| Avsnittsunderlag | Exakt underlag som skickades till AI |
| AI-anrop | Modell, inställningar, promptmall och svar (svaren sparas, eftersom de inte kan återskapas genom ny körning) |
| Mänskliga ändringar och sakgranskning | Vem, när och avsnittets kontrollsumma före och efter |
| Mallar och renderade dokument | Word-mall, Word-fil och PDF |

Ett fastställt paket är oföränderligt. En ändring ger en ny version som ersätter den gamla. Den gamla sparas.

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
| Beslutstabellrad | `BT-<tabell>-<nr>` | `BT-MATRIS-07` |
| Profiluppgift | `P-<område>.<namn>` | `P-ORG.antal_anstallda` |
| Avsnitt | `D-<dokument>.<avsnitt>` | `D-ARB.6.1` |
| Fynd | `F-<datum>-<nr>` | `F-2026-10-08-014` |

**Varje katalog finns på ett enda ställe:** `regelbas/kataloger/<katalog>.yaml`. Katalogen har versionsnummer, och spec, research och kod hänvisar till den i stället för att återge den. ID:n är stabila. En post som utgår markeras `utgången` och raderas inte. Bristmönsterkatalogen v0 finns i [research 03](../../research/03-tillsyn-och-sanktioner.md) och flyttas till regelbasen i etapp M0.

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
grund: ska_krav            # ska_krav | allmänt_råd | tillsynspraxis | eu_utkast | metodval
text: Den allmänna riskbedömningen ska utvärderas minst en gång per år och datum för utvärdering och uppdatering ska framgå.
galler_om:                 # villkor enligt 6.3
  alla: []
belagg: [dokument, datum]  # dokument | datum | logg | beslut | register
uppfylls_i: [D-ARB.10]
sakkunnig:
  status: ej_granskad      # ej_granskad | verifierad | ändras
  av: null
  datum: null
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
  grund: metodval
  villkor:
    alla:
      - { falt: P-KUND.andel_riskbransch, op: ">=", varde: 0.2 }
  vid_okant: galler        # en obekräftad uppgift ger det försiktiga utfallet
  effekt: { sannolikhet: "+1" }
  kallor: [SRC-NRA-2024-25, SRC-FIPO-2026]
```

**Profiluppgift**
```yaml
id: P-ORG.antal_anstallda
typ: heltal
varde: 12
personuppgift: false
kritisk: true              # används av en beslutstabell eller ett ska-krav
status: bekräftad          # saknas | föreslagen | bekräftad
kalla: "Årsredovisning 2024/25"
datum: 2026-10-05
bekraftad_av: roll:FfR
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
  regelspar: [BT-SANN-04, BT-MATRIS-07]
terrorfinansiering: { sannolikhet: låg, konsekvens: allvarlig, niva: måttlig }
sanktionsrisk: { niva: låg }
kontroller:
  - { id: C-07, utformning: finns, genomforande: ej_belagt }
kvarstaende: { niva: hög, regelspar: [BT-KVAR-02] }
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

**Granskningsfynd**
```yaml
id: F-2026-10-08-014
typ: bristmonster         # tackning | sparbarhet | bristmonster | provtillsyn | sakgranskning
regel: B-09               # Geografi kopplas bara till sanktionslistor
allvar: hög               # blockerande | hög | medel | låg
avsnitt: D-ARB.5.3
beskrivning: Geografiska riskfaktorer kopplas bara till sanktionslistor.
atgard: Beskriv kundernas och motparternas utlandskopplingar och lokala riskfaktorer.
status: öppen             # öppen | åtgärdad | accepterad (med motivering)
```

### 6.3 Villkorsformat

Villkor i regelbasen skrivs i ett litet typat format, inte som fria uttryck. YAML får inte bli ett programmeringsspråk.

```yaml
villkor:
  alla:                                   # alla | nagon | inte
    - { falt: P-KUND.andel_riskbransch, op: ">=", varde: 0.2 }
    - nagon:
        - { falt: P-KANAL.distanskunder, op: "==", varde: true }
        - { falt: P-GEO.lander_utanfor_ees, op: "finns" }
```

| Del | Tillåtet |
|---|---|
| Kombinatorer | `alla`, `nagon`, `inte` |
| Operatorer | `==`, `!=`, `<`, `<=`, `>`, `>=`, `i` (värdet finns i lista), `finns`, `saknas` |
| Fält | Endast profiluppgifter (`P-...`) och bedömningsresultat som finns i ett registrerat fältregister med typ |
| Typer | `bool`, `heltal`, `tal`, `andel` (0–1), `text`, `val` (fast lista), `datum` |

- Utvärderaren är en liten Python-funktion. Den använder aldrig `eval` och inga funktionsanrop.
- Okända fält, fel typ och okända operatorer ger fel redan när regelbasen läses in.
- Bygger ett villkor på en uppgift som inte är bekräftad blir utfallet *okänt*. Regelns fält `vid_okant` avgör vad som gäller. Standard är det försiktiga utfallet, det vill säga det som ger högre risk.

## 7 Riskmetod

### 7.1 Steg

Stegen följer Länsstyrelsens föreskrifter (2 kap. 2 §) och är förberedda för AMLA:s utkast till riktlinjer (fyra minimikrav, ej bindande ännu):

1. **Verksamhetsöversikt.** Organisation, storlek, kunder, tjänster, kanaler, geografi, AML-organisation, utlagd verksamhet och ny teknik.
2. **Identifiera tjänster.** Varje tjänst bedöms för sig. En tjänst som inte erbjuds markeras "erbjuds ej" men finns kvar i bedömningen.
3. **Hot per tjänst.** Hämtas ur hotkatalogen, med källor, och kompletteras med verksamhetens egna erfarenheter (rapporter till Finanspolisen, nekade kunder).
4. **Sårbarheter.** Kunder, kanaler, geografi, verksamhetsspecifika omständigheter och tjänstens egenskaper, matchade mot byråprofilen.
5. **Inneboende risk per tjänst.** Sannolikhet × konsekvens enligt beslutstabeller. Terrorfinansiering och kringgående av riktade finansiella sanktioner bedöms separat.
6. **Kontrollernas kvalitet.** Utformning (finns kontrollen i rutinerna?) och genomförande (finns belägg?).
7. **Kvarstående risk** per tjänst och för verksamheten som helhet.
8. **Prioriterade åtgärder** som förs till rutinerna och åtgärdslistan.

### 7.2 Skalor

Alla skalor är **metodval** (standardvärden som verksamheten kan ändra med motivering).

| Skala | Nivåer |
|---|---|
| Sannolikhet | låg, medel, hög |
| Konsekvens | begränsad, betydande, allvarlig |
| Risk | låg, måttlig, hög, mycket hög |
| Kontrollkvalitet | fungerar, mindre brister, betydande brister, saknas eller ej belagd |

Riskmatris (metodval):

| Sannolikhet \ Konsekvens | Begränsad | Betydande | Allvarlig |
|---|---|---|---|
| Låg | låg | måttlig | måttlig |
| Medel | måttlig | måttlig | hög |
| Hög | måttlig | hög | mycket hög |

### 7.3 Regler för kvarstående risk

| Regel | Grund |
|---|---|
| Kvarstående risk är aldrig högre än inneboende risk | Metodval, följer AMLA:s utkast |
| En kontroll som inte är belagd sänker inte risken | Metodval, följer Länsstyrelsens vägledning om att riskreducerande åtgärders effekt ska utvärderas |
| En fungerande kontroll sänker risken högst ett steg per tjänst | Metodval |
| Inneboende hög eller mycket hög risk blir aldrig lägre än måttlig | Metodval. AMLA:s utkast anger att hög inneboende risk inte helt kan tas bort med kontroller, men anger ingen nivå. |
| Terrorfinansiering har alltid konsekvensen allvarlig | Metodval, följer myndigheternas vägledning om att små belopp kan finansiera terrorism |

### 7.4 Sammanvägning

| Regel | Grund |
|---|---|
| Tjänsterna vägs samman med dokumenterade vikter, som standard andel av kunder eller omsättning | Metodval |
| Den samlade nivån är lägst den högsta nivån bland tjänster som väger minst 20 % | Metodval (gränsen kan ändras med motivering) |
| Motorn redovisar varje faktors bidrag så att ingen enskild faktor ensam avgör | Metodval, följer AMLA:s utkast |
| Avvikelse från sektorns nivå i den nationella riskbedömningen ska motiveras | Tillsynspraxis (rapport 2026:14) |

### 7.5 Proportionalitetsnivå

| Nivå | Typfall | Effekt |
|---|---|---|
| Enkel | Få anställda, ett kontor, enkla tjänster, inga behörigheter i kundernas namn | Kortare, mer beskrivande dokument. Samma krav täcks. |
| Standard | Typisk redovisningsbyrå | Full analys per tjänst |
| Utökad | Många anställda, flera kontor, behörigheter, utländska kunder, koncern | Fler scenarier, funktioner för intern kontroll, tätare uppföljning |

Nivån beräknas av faktorerna i Länsstyrelsens föreskrifter 6 kap. 3 § (omsättning, anställda, verksamhetsställen, verksamhet, tjänster, komplexitet, riskbedömning). Gränsvärdena är metodval och kan justeras med motivering.

### 7.6 Kundriskmodell (mall för fas 1, motor för fas 2)

1. **Hinder.** Sanktionsträff, otillräcklig kundkännedom, misstanke. Arbetet stoppas tills hindret är undanröjt. *Ska-krav.*
2. **Alltid hög risk.** PEP och högrisktredjeland (*ska-krav om skärpta åtgärder*) samt verksamhetens egna val, till exempel oförklarlig ägarstruktur (*metodval*).
3. **Riskfaktorer.** Poäng per faktor, härledda ur den allmänna riskbedömningen och lagens exempel på hög risk. *Poängen är metodval.*
4. **Lågriskfaktorer.** Härledda ur lagens exempel på låg risk och verksamhetens val. *Metodval.*
5. **Nivå och justering.** Poänggränser och regler för höjning och sänkning. En uppgift som inte är verifierad ger alltid det försiktiga svaret. *Metodval.*

### 7.7 Beslutstabeller

All logik i 7.2–7.6 ligger i `regelbas/beslutstabeller/*.yaml`. Varje rad har ID, villkor (enligt 6.3), utfall, källa, grund och en klartextförklaring. Varje rad har minst ett test.

## 8 AI-lagret

### 8.1 Uppgifter för AI

| Uppgift | Tillåtet | Förbjudet |
|---|---|---|
| Skriva avsnitt | Formulera beskrivningar, analyser, motiveringar och scenarier utifrån avsnittsunderlaget | Nya fakta, siffror, nivåer eller källor |
| Provtillsyn (etapp M5) | Bedöma dokumenten mot en rubrik och rapportera fynd | Ändra text |
| Föreslå profiluppgifter ur byråns dokument | Skjuts upp. Kräver maskning av personuppgifter först (avsnitt 16). | – |

### 8.2 Flöde per avsnitt

1. Bedömningen bygger ett **avsnittsunderlag**: relevanta krav, hot, sårbarheter, profiluppgifter med status, nivåer med regelspår och de bristmönster avsnittet ska undvika. Personer ersätts med rollplatshållare, till exempel `{roll:FfR}`, och namn sätts in först vid rendering.
2. AI:n svarar i ett **låst schema** (strukturerade svar). Varje stycke bär `referenser`.
3. **Maskinell validering:**
   - Alla ID:n finns.
   - Alla siffror finns i underlaget.
   - Nivåer i texten stämmer med bedömningen.
   - Uppgifter som inte är bekräftade skrivs med `[VERIFIERA]`.
   - Inga förbjudna generiska formuleringar och inga personnamn förekommer.
4. Ett underkänt svar körs om med valideringsfelen som återkoppling. Efter tre försök stoppar avsnittet med ett fynd.
5. Godkänt svar sparas med kontrollsumma och går vidare till granskning och sakgranskning (avsnitt 10).

### 8.3 Modell och drift

- Claude via Anthropics officiella Python-SDK. Standardmodell `claude-opus-5-5` med adaptiv tänkning och hög effort för skrivuppgifter.
- Strukturerade svar via SDK:ns `messages.parse` med pydantic-scheman. Claudes inbyggda källhänvisningar går inte att kombinera med strukturerade svar, så programmets egna referens-ID:n används.
- Regelbasens innehåll läggs först i anropet för att utnyttja prompt-cachning. Batch-API används vid omgenerering av många avsnitt.
- Leverantören kapslas in bakom ett gränssnitt. Om personuppgifter någon gång måste skickas till AI (fas 2) krävs databehandling inom EU. Anthropics eget API erbjuder i dag bara `us` och `global`, så EU-behandling sker då via Google Vertex AI eller Amazon Bedrock i EU-region.
- Modell, inställningar, promptmall, svar och tokenförbrukning sparas per anrop och tas med i manifestet.

## 9 Granskning (maskinell)

| Nivå | Kontroll | Typ |
|---|---|---|
| 1 Täckning | Varje tillämpligt krav har minst ett avsnitt. Varje erbjuden tjänst har eget avsnitt med hot, sårbarheter och motiverad nivå. | Deterministisk |
| 2 Spårbarhet | Alla referenser finns. Alla verksamhetspåståenden pekar på profiluppgifter. Alla obligatoriska datum finns. | Deterministisk |
| 3 Bristmönster | Bristmönsterkatalogen (`regelbas/kataloger/bristmonster.yaml`) | Deterministisk, senare kompletterad med AI |
| 4 Provtillsyn (M5) | AI bedömer dokumenten som en handläggare utifrån föreläggandets punkter och en rubrik | AI |

Exempel ur bristmönsterkatalogen v0 (ID:n enligt [research 03](../../research/03-tillsyn-och-sanktioner.md)):

- B-01 Den allmänna riskbedömningen saknas eller förväxlas med kundbedömning eller rutiner.
- B-02 Mallen är inte anpassad till verksamheten.
- B-04 Tjänster beskrivs tillsammans utan individuell analys.
- B-09 Geografi kopplas bara till sanktionslistor.
- B-12 Sammantagen risk utan analys av hur nivån nåtts.
- B-13 Alla nivåer låga utan hänsyn till sektorsrisken i den nationella riskbedömningen.
- B-16 Datum för utvärdering och uppdatering saknas.

Vad fynden betyder för dokumentets status framgår av avsnitt 10.

## 10 Dokumentstatus och grindar

```
utkast ─► granskat ─► sakgranskat ─► fastställt (låst) ─► ersatt
```

| Övergång | Villkor |
|---|---|
| **Export som utkast** | Alltid tillåten. Varje sida märks "UTKAST – ej fastställt", och åtgärdslistan med öppna punkter bifogas. |
| utkast → **granskat** | Maskinell granskning är körd och har inga *blockerande* fynd. |
| granskat → **sakgranskat** | En ansvarig person har gått igenom varje avsnitt och godkänt sakpåståenden och motiveringar. Vem, när och avsnittets kontrollsumma loggas. Text som ändras av en människa valideras maskinellt igen. |
| sakgranskat → **fastställt** | Alla villkor nedan är uppfyllda och ett behörigt organ (styrelse eller ledning) har fattat beslut. Namn, roll och datum registreras. |

Villkor för fastställelse:

1. Alla **kritiska** profiluppgifter (sådana som används av en beslutstabell eller ett ska-krav) har status *bekräftad*.
2. Texten innehåller inga `[VERIFIERA]`.
3. Alla krav i regelpaketet som är tillämpliga på byrån har sakkunnigstatus *verifierad*.
4. Inga fynd är öppna med allvar *blockerande* eller *hög*. Ett fynd med allvar *hög* får accepteras om funktionen för regelefterlevnad skriver en motivering.
5. Sakgranskning är gjord för varje avsnitt och gäller den aktuella kontrollsumman.

Vid fastställelse låses paketet: manifestet (avsnitt 5.3) skrivs, alla artefakter kopieras till `faststallda/<version>/`, och paketet kan därefter bara ersättas av en ny version.

## 11 Utdata i fas 1

| Dokument | Innehåll | Mottagare |
|---|---|---|
| Allmän riskbedömning | Översikt, tjänster, hot, sårbarheter, risk per tjänst, sammanvägning, slutsatser, omvärldsbevakning, utvärdering | Ledning, FfR, tillsyn |
| Metodbilaga | Skalor, matris, beslutsregler med grund (lagkrav eller metodval), vikter, källor och hur de använts | FfR, tillsyn |
| Rutiner och riktlinjer | Kundkännedom, övervakning, rapportering, bevarande, intern kontroll, personal | Alla |
| Arbetsinstruktioner per roll | Korta checklistor för konsult, FfR och ledning | Respektive roll |
| Kundriskmodell och kundformulär | Mall som följer modellen i 7.6 | Konsulter |
| Kravmatris | Krav, var det uppfylls, status beskrivet, infört och kontrollerat | FfR, tillsyn |
| Åtgärdslista | Öppna `[VERIFIERA]`, fynd och beslut som saknas | FfR |
| Index för tillsynspaket | Föreläggandets punkter kopplade till dokument och loggar | FfR |

## 12 Kommandon

```
riskanalys regelbas validera
riskanalys ny <byrå> --sektor redovisning --lan "Västra Götaland"
riskanalys intag <byrå>
riskanalys bekrafta <byrå>                    # bekräfta profiluppgifter
riskanalys bedom <byrå>
riskanalys skriv <byrå> [--avsnitt D-ARB.6.1]
riskanalys granska <byrå>
riskanalys sakgranska <byrå>                  # mänsklig granskning per avsnitt
riskanalys exportera <byrå> --utkast
riskanalys faststall <byrå> --beslut "styrelsen 2026-11-15"
```

## 13 Drift och livscykel (etapp M6)

- **Årlig utvärdering:** påminnelse senast tolv månader efter förra utvärderingen. En utvärdering utan ändring dokumenteras med motivering.
- **Utlösande händelser:** ny eller ändrad tjänst, ny marknad, ny version av en referenslista, ny nationell riskbedömning, ändrad föreskrift, hot mot personal, nya mönster i egen rapportering. Programmet jämför referensdatans kontrollsummor med dem som det fastställda paketet låste och visar vilka avsnitt som påverkas.
- **Belägg:** utbildningslogg, kontrollplan med resultat och stickprov. Belägg från driften blir indata till nästa års bedömning av kontrollernas genomförande.

## 14 Mappstruktur

```
riskanalys/                     (repot)
  AGENTS.md, CLAUDE.md          gemensamma regler för Codex och Claude
  pyproject.toml
  regelbas/                     granskade och versionerade data
    kallor/  krav/  kataloger/  referensdata/  regelpaket/  beslutstabeller/
  src/riskanalys/
    regelverk/       källor, krav, kataloger, regelpaket, giltighet, villkorsformat, validering
    profil/          intag, belägg, bekräftelse
    bedomning/       beslutstabeller, risknivåer, regelspår, kundmodell
    dokument/        avsnittsunderlag, AI-klient, AI-text, rendering
    granskning/      täckning, spårbarhet, bristmönster, fynd
    faststallelse/   status, sakgranskning, godkännande, låsning
    lagring/         datamapp, manifest, kontrollsummor
    drift/           (etapp M6)
    cli.py
  mallar/                       Word-mallar
  tester/
    enhet/  regelkontrakt/  typfall/
  docs/
```

Byrådata ligger i `$RISKANALYS_DATA`, aldrig i repot (avsnitt 5.2).

## 15 Kvalitetssäkring

| Test | Vad det visar |
|---|---|
| Regelbasvalidering | Unika ID:n, inga brutna referenser, giltiga villkor, varje krav har källa, varje tjänst har hot |
| Regelkontrakt | Ett test per beslutstabellrad plus gränsfall och okända uppgifter |
| Typfall | Hela kedjan med syntetiska profiler ger förväntade nivåer, fynd och status |
| AI-validering | Valideringen fångar påhittade ID:n, siffror, nivåer och personnamn |
| Återskapande | Ett fastställt paket kan verifieras mot sitt manifest |
| Facitjämförelse (M5) | En referensbyrås tidigare underkända riskbedömning ska underkännas. Ett genomarbetat referensutkast ska i stort godkännas. |
| Sakkunniggranskning | Regelbasen granskas av sakkunnig innan första riktiga fastställelse |

**Syntetiska uppgifter används tills regelbasen är sakkunniggranskad.** Ingen riktig byrå får ett fastställt paket innan dess.

## 16 Personuppgifter och säkerhet

Fas 1 behandlar inga kundärenden. Viss behandling av personuppgifter är ändå nödvändig, eftersom föreskrifterna kräver att det framgår vem som har funktionerna (LSF 6 kap. 3–4 §§) och att utbildning dokumenteras med deltagarnas namn (LSF 2 kap. 11 §). Även företagsanknutna kontaktuppgifter och uppgifter om enskilda näringsidkare kan vara personuppgifter (se IMY).

| Kategori | Exempel | Tillåtet i fas 1 | Skickas till AI |
|---|---|---|---|
| Funktionsinnehavare och beslutsfattare | Namn och roll för FfR, VD, styrelse | Ja | Nej. Ersätts med rollplatshållare. |
| Anställda i utbildnings- och lämplighetslogg | Namn, datum, utbildningsinnehåll | Ja | Nej |
| Byråns kontaktuppgifter | Företagsanknuten e-post och telefon | Ja | Nej |
| Byrå som är enskild näringsidkare | Organisationsnummer som är personnummer | Ja | Nej. Ersätts med platshållare. |
| Aggregerad kundstatistik | Antal och andelar per kategori | Ja | Ja (inte personuppgifter) |
| Kunder, verkliga huvudmän, enskilda kundärenden | – | **Nej** | Nej |
| Importerade byrådokument | Riktlinjer, årsredovisning | Bara efter maskning av personuppgifter | Nej i fas 1 |

Övrigt:

- Profiluppgifter har fältet `personuppgift`. Sådana uppgifter tas aldrig med i ett avsnittsunderlag.
- Valideringen av AI-svar söker efter personnamn som finns i profilen.
- Byrådata lagras i datamappen utanför repot, med filbehörighet bara för användaren.
- Gallring följer penningtvättslagens bevarandetider där de gäller (fem år, högst tio). Verksamhetsutövaren ansvarar för rättslig grund och information till de registrerade.
- API-nycklar läses från miljövariabler, aldrig från kod eller filer i repot.
- Fas 2 med kundärenden kräver en egen spec med kryptering, behörighetsstyrning och EU-hostad databehandling.

## 17 Etapper

| Etapp | Innehåll | Klart när |
|---|---|---|
| **M0 Grund** | Repo, `AGENTS.md`/`CLAUDE.md`, datamapp, lagring och manifest, villkorsformat och utvärderare, scheman, regelbasvalidering, bristmönsterkatalogen v0 flyttad till regelbasen | `riskanalys regelbas validera` är grön, och villkorsutvärderaren har fullständiga regelkontrakt |
| **M1 Tunn kedja** | Hela flödet för en tjänst med syntetiska data: ett litet kravpaket (allmän riskbedömning, LSF 2 kap. 1–3 §§) → en bekräftad syntetisk testprofil → bedömning av löpande bokföring → spårbart AI-utkast för det avsnittet → maskinell granskning → sakgranskning → fastställd testexport med låst manifest | Kedjan körs i ett typfallstest, och manifestet verifierar det fastställda paketet |
| M2 Regelbas v1 | Alla krav, kataloger och beslutstabeller för redovisningsbyråer. Sakkunniggranskning. | Alla tillämpliga krav har status *verifierad* |
| M3 Allmän riskbedömning | Alla tjänster, sammanvägning, metodbilaga, intag för en riktig byrå | En riktig byrå kan fastställa sin riskbedömning |
| M4 Övriga dokument | Rutiner, kundmodell, instruktioner, kravmatris, tillsynspaket | Alla dokument i avsnitt 11 genereras |
| M5 Provtillsyn och facit | AI-provtillsyn och facitjämförelse | Facitfallen ger förväntat utfall |
| M6 Drift | Påminnelser, utlösande händelser, belägg | Ändrad högrisklista ger korrekt flaggning |
| M7 Kundnivå | Egen spec | – |
| M8 Fler sektorer | Ett sektorspaket per sektor | – |
| M9 AMLR | Regelpaket för AMLR och ny svensk lag | Klart före 2027-07-10 |

M1 bevisar att arkitekturen håller innan arbetet läggs på hela regelbasen, provtillsynen och driften.

## 18 Risker

| Risk | Hantering |
|---|---|
| Regelbasen tolkar lagen fel | Sakkunniggranskning, källa per post, regelkontrakt |
| AI hittar på fakta | Låst schema, maskinell validering, inga fria fält för fakta |
| AI-text stämmer formellt men inte i sak | Sakgranskning per avsnitt före fastställelse |
| Generisk text slinker igenom | Bristmönster B-02 och provtillsyn |
| Personuppgifter sprids | Kategorier i avsnitt 16, rollplatshållare, datamapp utanför repot |
| En äldre bedömning går inte att återskapa | Manifest med kontrollsummor, sparade AI-svar, låsta paket |
| Regelverket ändras (AMLR, ny svensk lag) | Versionerade regelpaket med giltighetsdatum |
| Dokumenten blir för långa att följa | Proportionalitetsnivå och arbetsinstruktioner per roll |
| Föråldrad referensdata | Datum och kontrollsumma per lista, påminnelser |

## 19 Öppna frågor

1. Innehållet i Länsstyrelsen Skånes föreskrifter (12FS 2024:8) behöver jämföras med Stockholms och Västra Götalands.
2. AMLA:s slutliga riktlinjer om verksamhetsövergripande riskbedömning väntas under fjärde kvartalet 2026. Till dess märks allt som bygger på utkastet som *EU-utkast* eller *metodval*.
3. Status för ny svensk penningtvättslag (SOU 2024:58).
4. Om Bolagsverket erbjuder elektronisk åtkomst till registret över verkliga huvudmän (påverkar fas 2).
5. Vem som gör sakkunniggranskningen av regelbasen.

## 20 Ändringslogg

| Revision | Datum | Ändring |
|---|---|---|
| 1 | 2026-10-08 | Första förslaget |
| 2 | 2026-10-08 | Efter granskning (Codex): (1) bristmönstrens ID:n samordnade med research 03 och en enda versionerad katalog som facit; (2) "inga personuppgifter" ersatt med kategorier för personuppgifter och rollplatshållare i AI-anrop; (3) dokumentstatus och grindar för utkast, granskat, sakgranskat och fastställt; (4) typat villkorsformat utan fria uttryck, och alla skalor, gränser och poäng märkta som metodval; (5) manifest med kontrollsummor för allt underlag och sparade AI-svar; (6) obligatorisk mänsklig sakgranskning per avsnitt. Dessutom: datamapp utanför repot, ny modulstruktur med `faststallelse/` och `lagring/`, och första byggetappen ändrad till en tunn kedja genom hela flödet med syntetiska data. |
