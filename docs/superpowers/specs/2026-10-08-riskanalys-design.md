# Riskanalys – designspecifikation

**Status:** Förslag, revision 35 (2026-10-17); verksamhetsanpassad nivåmotivering och sammanhängande tjänstetext godkänd som riktning, genomförs enligt [V7-planen](../plans/2026-10-17-nivamotivering-och-sammanhangande-text.md). Ligger till grund för M0–M1 och [implementeringsplanen för M2](../plans/2026-10-10-m2-regelbas-v1-och-juridisk-granskning.md). Juridiskt godkännande återstår.
**Underlag:** [researchsammanställningen](../../research/README.md).
**Ändringar:** se [ändringsloggen](#22-ändringslogg) sist i dokumentet.
**Nästa steg:** verklig sakkunniggranskning av M2:s tekniska underlag och sedan M3:s metod-/granskningsutvärdering. M0–M1 och M2:s tekniska implementation är införda; M2 är ännu inte juridiskt godkänd. Se [status](../../STATUS.md) och [M2-planens genomförandelogg](../plans/2026-10-10-m2-regelbas-v1-och-juridisk-granskning.md#genomförande-2026-10-10) för kontrakt, verifiering och kvarstående arbete.

---

## 1 Syfte

Programmet tar fram och förvaltar den dokumentation som en verksamhetsutövare behöver enligt penningtvättsregelverket: allmän riskbedömning, rutiner och riktlinjer, kundriskmodell med mera. Dokumentationen ska vara anpassad till den egna verksamheten, och varje påstående ska gå att spåra till en källa.

Målet är att varje tillämpligt krav i lag, föreskrift och tillsynspraxis

- är adresserat i dokumenten,
- är motiverat med verksamhetens egna uppgifter,
- är spårbart till sin källa,
- och går att visa som infört och kontrollerat över tid.

Programmet ger underlag. Resultatet kallas **"fastställt av byrån"**. Det är byråns eget beslut och ingen certifiering av att regelverket följs. Inget resultat utlovar att tillsynen godkänner dokumentationen.

## 2 Målgrupp och avgränsning

| Fas | Användare | Omfattning |
|---|---|---|
| 1 | Redovisnings- och konsultbyråer under Länsstyrelsens tillsyn, för deras egen efterlevnad | Verksamhetsnivå: allmän riskbedömning, rutiner, kundriskmodell (mall), kravmatris, minsta drift. **Inga kundärenden.** |
| 2 | Samma | Kundnivå: kundkännedom och riskprofil per kund, misstankelogg, femårsregister |
| 3 | Övriga verksamhetsutövare under Länsstyrelsens tillsyn | Nya sektorspaket (skatterådgivare, bolagsbildare, varu- och konsthandlare, pantbanker m.fl.) |
| Parallellt | Alla | Regelpaket för EU:s AMLR (tillämpas i huvudsak från 2027-07-10) och de svenska kompletterande reglerna |

Programmet byggs först som en kärna med kommandoradsgränssnitt. Före användning hos en riktig byrå krävs ett enkelt lokalt gränssnitt för intag och sakgranskning (avsnitt 14). Webbgränssnitt eller tjänsteleverans byggs senare och anropar samma kärna.

## 3 Fattade beslut

| Beslut | Val | Datum |
|---|---|---|
| Användare | Konsultbyråer först, sedan andra företag | 2026-10-08 |
| Omfattning | Alternativ C: verksamhetsnivå först, datamodell förberedd för kundnivå | 2026-10-08 |
| Arkitektur | Alternativ 2: regelbas och deterministisk motor, AI som skribent | 2026-10-08 |
| Byggare | Ägaren bygger själv med Claude Code och Codex. Koden ska vara enkel att läsa och väl testad. | 2026-10-08 |
| Gränssnitt | Kärna och CLI först. Enkelt lokalt formulär före första riktiga byrå. Webb senare. | 2026-10-08 |

## 4 Grundprinciper

1. **Verksamhetsanpassning är produkten.** Generisk malltext är det tillsynen oftast underkänner (tillsynsrapport 2026:14). Programmet ska hellre stoppa än leverera generisk text.
2. **Spårbarhet åt två håll.**
   - Varje påstående om risk pekar på en post i regelbasen, som i sin tur pekar på en källa.
   - Varje påstående om verksamheten pekar på en uppgift i byråprofilen eller markeras `[VERIFIERA]`.
3. **AI fattar inga beslut.** Risknivåer, poäng och regler kommer från motorn. AI:n formulerar och analyserar inom ett givet underlag och får inte införa nya fakta.
4. **En människa godkänner sakinnehållet.** Maskinell validering visar att referenserna finns, inte att formuleringarna stämmer. Varje avsnitt sakgranskas av en ansvarig person före fastställelse.
5. **Förklarbar och validerad metod.** Varje regel i motorn har en klartextförklaring och en källa. Motorn är en modell för riskbedömning och riskklassificering i lagens mening och omfattas av kravet på modellriskhantering (PTL 6 kap. 1 § andra stycket, avsnitt 7.8).
6. **Lagkrav hålls isär från metodval.** Varje regel märks med sin grund: *ska-krav*, *allmänt råd*, *tillsynspraxis*, *EU-utkast (ej bindande)* eller *metodval*.
7. **Juridiska beslutsgrenar hålls isär.** Förbud och stopp, obligatoriska åtgärder, riskklassning och rapportering är olika bestämmelser med egna villkor och undantag. De slås inte ihop till en risknivå (avsnitt 7.6).
8. **Okänt är inte samma sak som högt.** En uppgift som saknas ger ett försiktigt *preliminärt* resultat, aldrig en fastställd slutsats.
9. **Risk före åtgärder.** Inneboende risk bedöms utan kontroller. Kontroller får sänka risken bara när deras effekt är belagd.
10. **Datum är krav.** Det gäller utvärdering, uppdatering, nästa genomgång, fastställelse, identitetskontroll och utbildning.
11. **Proportionalitet.** Dokumentens omfattning styrs av verksamhetens storlek och komplexitet, inte av hur mycket text AI:n kan producera.
12. **Underlaget bevaras och kan verifieras.** Ett fastställt paket bevaras med allt underlag och kan verifieras och återställas (avsnitt 5.3).
13. **Minsta möjliga personuppgifter.** Fas 1 behandlar inga kundärenden. Personuppgifter begränsas till de kategorier som anges i avsnitt 17. AI-anrop innehåller bara uppgifter från en granskningsbar tillåtelselista.

## 5 Arkitektur

Strukturen bygger på samma lagerprincip som NIST:s OSCAL: katalog, urval, genomförande, granskning och åtgärder. Varje lager hänvisar till föregående lager i stället för att kopiera det.

```
 KÄLLOR ─► KRAVREGISTER + KATALOGER ─► REGELPAKET
                                           │
 BYRÅPROFIL (bekräftad) ───────────────────┤
                                           ▼
                                      BEDÖMNING ─► DOKUMENT ─► GRANSKNING ─► SAKGRANSKNING ─► FASTSTÄLLELSE
                                           ▲          (AI)      (maskinell)    (människa)    (av byrån, låst)
                                           │                                                        │
                                           └──────────────────────── DRIFT ◄────────────────────────┘
                     LAGRING: datamapp, manifest, kontrollsummor och säkerhetskopia för allt ovan
```

### 5.1 Byggblock

| # | Block | Ansvar | AI |
|---|---|---|---|
| 1 | Källregister | Alla källor med metadata, län och kontrollsumma. Lydelser per paragraf med egna datum för ikraftträdande och upphörande (6.4). | Nej |
| 2 | Kravregister | Ett atomärt krav per post med källa, villkor och sakkunnigstatus. Paragrafkarta per källa (avsnitt 16.1). | Nej (sakkunnig) |
| 3 | Kataloger | Tjänster, hot, sårbarheter, kundfaktorer, kontroller, varningssignaler, bristmönster | Nej (sakkunnig) |
| 4 | Referensdata | Landlistor, sanktionsfiler, nationell riskbedömning, utsatta områden | Nej |
| 5 | Regelpaket | Urval och parametrar för sektor, län, regelverk och datum | Nej |
| 6 | Byråprofil | Verksamhetens uppgifter med status, källa och bekräftelse | Nej i fas 1 |
| 7 | Bedömning | Inneboende risk, kontroller, kvarstående risk, kundmodellens fyra spår, regelspår | Nej |
| 8 | Dokument | Avsnittsunderlag, AI-text, rendering till Word och PDF | Ja (text) |
| 9 | Granskning | Täckning, spårbarhet, bristmönster, senare AI-provtillsyn | Delvis |
| 10 | Fastställelse | Dokumentstatus, sakgranskning, avvikelser, godkännande, låsning | Nej |
| 11 | Lagring | Datamapp, manifest, kontrollsummor, säkerhetskopia och återställning | Nej |
| 12 | Drift | Minsta drift före första riktiga fastställelse (avsnitt 13.1). Full drift senare. | Nej |

### 5.2 Datamapp och gränssnitt

- **Byråns data ligger i en konfigurerad datamapp utanför repot.** Sökvägen anges med miljövariabeln `RISKANALYS_DATA`, som standard `~/RiskanalysData`. Programmet vägrar skriva byrådata innanför repots katalog. `.gitignore` är bara ett extra skydd.
- Varje block läser och skriver validerade datastrukturer (pydantic-modeller). Regelbas och profil lagras som YAML. Maskingenererade resultat lagras som JSON.
- Ett block läser bara föregående blocks utdata, aldrig dess interna logik.

```
$RISKANALYS_DATA/<byrå>/
  profil/          profil.yaml och bekräftelser
  bedomningar/     en mapp per körning
  utkast/          avsnittsunderlag, AI-svar, mänskliga ändringar
  granskning/      fynd, avvikelser och sakgranskningslogg
  faststallda/     låsta paket, ett per version
  manifest/        ett manifest per körning
  drift/           versionshistorik, utvärderingar, ändringskontroller
```

### 5.3 Manifest, bevarande och återställning

Varje körning skriver ett manifest med kontrollsumma (SHA-256) för varje artefakt som påverkat resultatet:

| Del | Exempel |
|---|---|
| Programversion | Git-commit och paketversion |
| Regelpaket | Paketfil och alla krav, kataloger och beslutstabeller det pekar på |
| Källor och referensdata | Varje källa och lista i den version som användes |
| Profil | Ögonblicksbild av den bekräftade profilen |
| Bedömning | Bedömningens JSON med regelspår |
| Avsnittsunderlag | Exakt underlag som skickades till AI, inklusive tillåtelselistan |
| AI-anrop | Modell, inställningar, promptmall och svar |
| Mänskliga ändringar, avvikelser och sakgranskning | Vem, när, motivering och avsnittets kontrollsumma före och efter |
| Mallar och renderade dokument | Word-mall, Word-fil och PDF |

**Vad manifestet visar och inte visar:** kontrollsummorna visar att sparade filer är oförändrade. De återskapar inga förlorade filer. Därför gäller:

- Vid fastställelse **kopieras alla artefakter som manifestet pekar på** in i `faststallda/<version>/`. Paketet är fristående och beror inte på att regelbasen eller mallarna finns kvar i samma version.
- AI-svaren sparas, eftersom de inte kan köras fram igen.
- Datamappen ska ingå i en **säkerhetskopia**. Programmet varnar om ingen säkerhetskopia har registrerats för datamappen.
- `riskanalys verifiera` kontrollerar ett paket mot dess manifest. Ett saknat eller skadat manifest rapporteras som en avvikelse med instruktion om återställning från säkerhetskopian, aldrig som en krasch.
- **Återställningsprov:** ett fastställt paket återställs från säkerhetskopia på en tom installation och verifieras (avsnitt 16).

Ett fastställt paket är oföränderligt. En ändring ger en ny version som ersätter den gamla. Den gamla sparas.

## 6 Datamodell

### 6.1 ID-konventioner

| Objekt | Format | Exempel |
|---|---|---|
| Källa | `SRC-<kortnamn>` | `SRC-PTL`, `SRC-14FS-2024-11`, `SRC-TS-2026-14`, `SRC-NRA-2024-25` |
| Paragraflydelse | `LYD-<källa>-<kap>-<§>-<ikraft>` | `LYD-PTL-1-2-2026-11-20` |
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
| Avvikelse | `A-<datum>-<nr>` | `A-2026-10-08-002` |

**Varje katalog finns på ett enda ställe:** `regelbas/kataloger/<katalog>.yaml`. Katalogen har versionsnummer, och spec, research och kod hänvisar till den i stället för att återge den. ID:n är stabila. En post som utgår markeras `utgången` och raderas inte. Bristmönsterkatalogen v0 finns i [research 03](../../research/03-tillsyn-och-sanktioner.md) och flyttas till regelbasen i etapp M0.

### 6.2 Huvudobjekt

**Källa**
```yaml
id: SRC-14FS-2024-11
titel: Länsstyrelsen i Västra Götalands läns föreskrifter och allmänna råd om åtgärder mot penningtvätt och finansiering av terrorism
typ: föreskrift            # lag | förordning | föreskrift | allmänt_råd | vägledning | tillsynsrapport | riskbedömning | beslut | eu_förordning | eu_riktlinje_utkast
utgivare: Länsstyrelsen i Västra Götalands län
beslutad: 2024-05-20
galler_fran: 2024-07-01
galler_till: null
geografi: [Västra Götaland, Halland, Värmland, Örebro, Dalarna, Gävleborg]
konsoliderad_tom: null     # för lagar: senaste ändrings-SFS, t.ex. "SFS 2026:1075"
url: https://...
hamtad: 2026-10-01
kontrollsumma: sha256:...
```

**Lydelse** (en version av en paragraf)
```yaml
id: LYD-PTL-1-2-2026-11-20
kalla: SRC-PTL
lagrum: "1 kap. 2 §"
ikraft: 2026-11-20
upphor: null
inford_genom: "SFS 2026:1023"
primarkalla: rkrattsbaser    # Regeringskansliets rättsdatabaser
text_kontrollsumma: sha256:...
```

**Krav**
```yaml
id: KRV-LSF-003
kalla: SRC-14FS-2024-11            # huvudkälla; länsurval sker per refererad lydelse
lagrum: "2 kap. 3 §"
lydelser: [LYD-LSF-2-3-2024-07-01]   # kravets giltighet följer lydelserna; en ny lydelse läggs till i listan
ikraft: 2024-07-01
upphor: null
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
  kontrollsumma: null      # kravets innehåll när det verifierades; verifierad gäller bara det innehållet
```

I M2 får ett krav ha alternativa likalydande paragraflydelser från flera län. `kalla` behålls som huvudkälla; vald lydelse avgör den rättsliga hänvisningen och geografin. Skillnader i betydelse kräver separata krav. Krav med flera självständiga rättsliga grunder länkas i kravkartan och behandlas inte som alternativa lydelser. Samtliga källor, lydelser, fält och metodberoenden som godkännandet omfattar ingår i sakkunnigunderlagets kontrollsumma.

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
  vid_okant: preliminart_galler   # ger ett försiktigt preliminärt utfall, se 6.3
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
status: bekräftad          # saknas | föreslagen | bekräftad | ej_tillämplig
motivering: null           # krävs vid ej_tillämplig
kalla: "Årsredovisning 2024/25"
datum: 2026-10-05
bekraftad_av: roll:FfR
```

**Bedömning per tjänst**
```yaml
tjanst: T-RED-01
erbjuds: true
status: slutlig            # preliminär | slutlig
inneboende:
  sannolikhet: hög
  konsekvens: betydande
  niva: hög
  motiveringsunderlag: [H-01, H-02, S-KUND-01, S-KANAL-02, S-VERK-03]
  regelspar: [BT-SANN-04, BT-MATRIS-07]
  okanda_uppgifter: []     # ifyllt ger status preliminär
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
status: öppen             # öppen | åtgärdad | accepterad_metodavvikelse | sakkunnigbedömd
```

**Avvikelse och manuell ändring** (underlag för modellriskhantering)
```yaml
id: A-2026-10-08-002
typ: metodavvikelse        # metodavvikelse | manuell_niva | ej_tillampligt
galler: BT-SAMMAN-03       # regel, faktor eller nivå som avviks från
fran: hög
till: måttlig
motivering: "..."
underlag: [P-KUND.andel_riskbransch]
beslutad_av: roll:FfR
datum: 2026-10-20
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
- Utfallet är *sant*, *falskt* eller *okänt*. *Okänt* uppstår när ett villkor bygger på en uppgift som inte är bekräftad.
- Vid *okänt* används regelns `vid_okant`. Standard är `preliminart_galler`: regeln tillämpas försiktigt, men resultatet märks **preliminärt** och listar de okända uppgifterna. Ett preliminärt resultat kan aldrig fastställas (avsnitt 10).

### 6.4 Datumstyrning

En konsoliderad lag kan samtidigt innehålla gällande och framtida lydelse av samma paragraf. Penningtvättslagens 1 kap. 2 § har till exempel en lydelse som upphör och en som träder i kraft 2026-11-20. Giltighet för en hel källa räcker därför inte.

- **Giltighet sätts per paragraflydelse** (`LYD-...`) med `ikraft` och `upphor`. Krav, beslutstabellrader och katalogposter som bygger på en lydelse ärver dess giltighet, eller har egna snävare datum.
- **Ett regelpaket väljs för ett bestämt datum** (`riskanalys ny ... --datum`). Urvalet tar med varje lydelse där `ikraft ≤ datum` och datumet ligger före `upphor`. Datumet låses i manifestet.
- **Primärkälla för konsoliderade författningar** är Regeringskansliets rättsdatabaser (SFST), som visar både gällande och kommande lydelser. Riksdagens öppna data används som kompletterande kontroll, eftersom den kan ligga efter.
- **Ändringar som väntar:** när en ny lydelse finns men ännu inte trätt i kraft visar programmet vilka krav och avsnitt som påverkas och från vilket datum.
- **Tester på båda sidor om varje datumgräns:** för varje lydelse med ett framtida `ikraft` eller `upphor` finns tester för dagen före och samma dag.
- Paragrafkartan (16.1) gäller ett bestämt datum och län.

## 7 Riskmetod

### 7.1 Steg

Stegen följer Länsstyrelsens föreskrifter (2 kap. 2 §) och är förberedda för AMLA:s utkast till riktlinjer (fyra minimikrav, ej bindande ännu):

1. **Verksamhetsöversikt.** Organisation, storlek, kunder, tjänster, kanaler, geografi, AML-organisation, utlagd verksamhet och ny teknik.
2. **Identifiera tjänster.** Varje tjänst bedöms för sig. En tjänst som inte erbjuds markeras "erbjuds ej" men finns kvar i bedömningen.
3. **Hot per tjänst.** Hämtas ur hotkatalogen, med källor, och kompletteras med verksamhetens egna erfarenheter (rapporter till Finanspolisen, nekade kunder).
4. **Sårbarheter.** Kunder, kanaler, geografi, verksamhetsspecifika omständigheter och tjänstens egenskaper, matchade mot byråprofilen.
5. **Inneboende risk per tjänst.** Sannolikhet × konsekvens enligt beslutstabeller. Terrorfinansiering och kringgående av riktade finansiella sanktioner bedöms separat.
6. **Kontrollernas kvalitet.** Utformning (finns kontrollen i rutinerna?) och genomförande (finns belägg?). Rutiner får inte ensamma motivera låg risk. Tillsynen har kritiserat just det.
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

### 7.4 Tjänstevis redovisning och framtida sammanvägning

Dagens motor redovisar varje tjänsts penningtvättsrisk, terrorfinansieringsrisk och separata sanktionsrisk. Ingen sammanvägd byrånivå beräknas. Varje tjänst får egen motivering och slutsatser, även om andelen kunder eller omsättning är liten. Avvikelse från NRA:s sektorsnivå kräver underlagsmotivering (B-13). NRA:s skala jämställs inte med motorns skala.

En framtida viktad byrånivå kräver en separat sakkunniggranskad metod och prov i M3. Den tidigare 20-procentsgränsen är ett obygget förslag och används inte i dagens dokument eller motor.

### 7.5 Proportionalitetsnivå

PTL 2 kap. 2 § kräver omfattning efter storlek och art. Implementerat metodförslag `BT-OMF-01` använder dokumenterade personer, kontor, omsättning, tjänster, komplexitet, utlandsanknytning och den tjänstevisa risken. Nivåerna är **enkel**, **standard** och **utökad**. Alla nivåer innehåller fullständig analys av varje erbjuden tjänst och samma rättsliga kravtäckning; utökad nivå lägger till hypotetiska scenarier och anger behov av fördjupad kontrolluppföljning. Ingen nivå beslutar automatiskt om särskilda funktioner, kundklass eller faktisk uppföljningstakt.

Trösklarna finns enbart i `regelbas/beslutstabeller/metod.yaml`: enkel högst två personer, ett kontor, högst tre miljoner kronor och bara de enklare redovisningstjänsterna; utökad minst tio personer, två kontor, tio miljoner kronor, särskilda betalnings-/företrädartjänster, komplexitet/utlandsanknytning eller hög/mycket hög tjänsterisk. Annars standard. **Trösklar, nivånamn och riskutlöst utökning är ogranskade metodval, inte föreskrivna gränser.** Saknade aktuella underlag ger preliminär bedömning. Byrån ger egen motivering i `P-OMFATTNING.motivering`; metodregeln ingår i sakkunnigattesten. PTL 2:2, föreskrifternas organisationsfaktorer och rapport 2026:14 ger stöd för vilka förhållanden som behöver prövas, inte dessa siffervärden.

### 7.6 Kundmodellen: fyra separata spår

Kundmodellen är en mall i fas 1 och en motor i fas 2. Den består av fyra spår som utvärderas var för sig. Inget spår får påverka ett annat utom där lagen säger det. **Varje spår och varje beslutsgren granskas av sakkunnig.**

| Spår | Fråga | Rättslig grund (verifieras i M2) | Utfall |
|---|---|---|---|
| **A Förbud och stopp** | Får affärsförbindelsen inledas eller fortsätta, eller åtgärden utföras? | Otillräcklig kundkännedom (PTL 3 kap. 1 §, med avgränsat undantag). Misstanke vid etablering (3 kap. 2 §). Misstänkt transaktion (3 kap. 3 §, med lagens transaktionsundantag). Sanktioner prövas efter identitetsutredning och mot exakt tillämplig bestämmelse. | Tillåtet, stopp, lagstadgat undantag eller preliminärt när underlag saknas. Varje utfall har egen dokumentation. |
| **B Obligatoriska särskilda åtgärder** | Vilka åtgärder kräver lagen oavsett riskklass? | Högrisktredjeland (3 kap. 17 §): skärpta åtgärder och godkännande av behörig beslutsfattare, med lagens undantag. PEP och närstående (3 kap. 19–20 §§): medlens ursprung, skärpt uppföljning, godkännande, samt 18 månader efter avslutat uppdrag. | Lista över åtgärder som ska genomföras och dokumenteras |
| **C Riskklassning** | Vilken riskprofil har kunden? | PTL 2 kap. 3–5 §§. Faktorer, poäng och gränser är metodval. Att PEP eller högrisktredjeland också ger hög riskklass är ett metodval, inte ett lagkrav. | Låg, normal eller hög, med motivering. Preliminär om uppgifter saknas. |
| **D Rapportering** | Ska misstanke rapporteras till Finanspolisen? | PTL 4 kap. 2–3 §§ (bedömning och rapportering), 8 § (undantag för vissa anförtrodda uppgifter) och 9 § (meddelandeförbud med undantag) | Rapportskyldighet prövad på egna villkor, oberoende av riskklass |

Spåren utvärderas var för sig men har **uttryckliga beroenden**. Andra beroenden än dessa finns inte.

| Från | Till | Beroende | Grund |
|---|---|---|---|
| C Riskklassning | Kundkännedomens omfattning | Kontroller, bedömningar och utredningar görs i den omfattning som kundens riskprofil kräver | PTL 3 kap. 14 § |
| C Riskklassning (hög) | B Obligatoriska åtgärder | Hög risk utlöser skärpta åtgärder: särskilt omfattande kontroller, bedömningar och utredningar samt ytterligare åtgärder | PTL 3 kap. 16 § |
| C Riskklassning (låg) | Kundkännedomens omfattning | Låg risk *tillåter* förenklade åtgärder, men kräver dem inte | PTL 3 kap. 15 § |
| C Riskklassning | A Förbud och stopp | Om kundkännedomen är *tillräcklig* bedöms mot den risk som ska hanteras. Högre risk kräver mer underlag innan förbindelsen får inledas eller fortsätta. | PTL 3 kap. 1 § |
| B → C | Riskklassning | Att PEP eller högrisktredjeland *också* ger hög riskklass är ett metodval (se tabellen ovan) | Metodval |
| Gemensamma rättsliga uppgifter | A och D, var för sig | Yrkesroll, uppdragets rättsliga syfte och uppgifternas sammanhang prövas separat mot respektive undantag. A:s undantag kopieras inte till D. Rapportering prövas även om A stoppar affären; låg riskklass befriar inte från rapporteringsprövning. | PTL 3 kap. 1 § andra stycket samt 4 kap. 2–3 och 8 §§ |

Beroendena finns i beslutstabellerna som egna rader med egna tester. Kundformuläret visar varje beroende för användaren.

Den rättsliga verksamhetskategorin hålls skild från tjänstens riskkategori. PTL 1 kap. 2 § första stycket 23 gäller bara verksamhetsutövare som inte är sådana personer som avses i 18–22. Bolagsbildning hos en byrå som omfattas av 19 eller 20 utlöser därför ingen automatisk omklassning till 23. Paketet avgränsas till länsstyrelsetillsyn enligt PTF 16 §; annan tillsyn eller en tjänst utanför paketets granskade omfattning ger ett tydligt hinder. Dessa frågor och rapporteringsundantaget har kontrollerats tekniskt mot [PTL](https://rkrattsbaser.gov.se/sfst?bet=2017:630); sakkunnig ska godkänna varje beslutsgren.

### 7.7 Beslutstabeller

All logik i 7.2–7.6 ligger i `regelbas/beslutstabeller/*.yaml`. Varje rad har ID, villkor (enligt 6.3), utfall, källa, grund och en klartextförklaring. Varje rad har minst ett test.

### 7.8 Modellriskhantering

Riskmotorn och kundmodellen är modeller för riskbedömning och riskklassificering. Penningtvättslagen 6 kap. 1 § andra stycket kräver rutiner för att utvärdera och kvalitetssäkra sådana modeller, anpassade efter verksamhetens storlek, art och risk. Programmet stödjer detta med:

| Del | Innehåll | När |
|---|---|---|
| Dokumenterad metod | Metodbilagan: regler, grund, skalor, vikter, gränser och kända begränsningar | Varje fastställelse |
| Sakkunnig validering | Sakkunnig granskar beslutstabellerna och varje juridisk beslutsgren i 7.6 per version av regelpaketet | Före första riktiga användning och vid ändring |
| Testfall | Regelkontrakt och typfall, inklusive saknade uppgifter och en liten högrisktjänst | Varje ändring |
| Motiverade manuella ändringar | Varje avvikelse från motorns resultat loggas som avvikelse (6.2) med motivering och beslutsfattare | Löpande |
| Återkommande kontroll | Årlig genomgång: avvikelsernas antal och mönster, fynd från granskning och tillsyn, och om utfallen är rimliga mot verksamheten | Årligen och vid ny version |
| Valideringsrapport | Sammanfattning av ovanstående per version av regelpaketet | Per version |

Byrån behöver också en egen rutin för modellriskhantering. Den ingår i rutinerna och riktlinjerna (avsnitt 11).

**Konkretisering i A + B, revision 33:** AB7 inför ett privat `Modellriskunderlag`. Modellidentiteten binder motor, beräkningsberoenden och regelbasens innehåll; Python-/biblioteksversioner sparas som miljöinformation och bryter inte i sig modellbindningen. Projektet levererar valideringsrapport för varje release med modellhash, fall/facit, utfall och begränsningar; ren miljö-/presentationsrelease kan återanvända tidigare modellvalidering med redovisade kompatibilitetsprov. Byrån granskar rapportens relevans, godkänner användningen och ansvarar för egen rutin/feluppföljning, utan att själv behöva skriva projektets valideringsrapport. M1 avgörs av sakkunnig i samma granskning som verifierar metoden. Ett väsentligt verkligt fel eller en ändrad modell kräver omprövning; gröna tester ger ingen attest. Den årliga basnivån och rollen modellansvarig är projektets operationalisering. Programstödet är implementerat; verklig sakkunnigprövning och projektets tekniska rapportartefakt återstår i pågående slutprov.

## 8 AI-lagret

### 8.1 Uppgifter för AI

| Uppgift | Tillåtet | Förbjudet |
|---|---|---|
| Skriva avsnitt | Formulera beskrivningar, analyser, motiveringar och scenarier utifrån avsnittsunderlaget | Nya fakta, siffror, nivåer eller källor |
| Provtillsyn (etapp M7) | Bedöma dokumenten mot en rubrik och rapportera fynd | Ändra text |
| Föreslå profiluppgifter ur byråns dokument | Skjuts upp. Kräver maskning av personuppgifter först (avsnitt 17). | – |

### 8.2 Flöde per avsnitt

1. Bedömningen bygger ett **avsnittsunderlag** enbart ur avsnittstypens **tillåtelselista**. Listan anger vilka profilfält och regelbasposter som får ingå. Den är versionerad och granskningsbar, och den sparas i manifestet. Personer ersätts med rollplatshållare, till exempel `{roll:FfR}`, och namn sätts in först vid rendering.
2. AI:n svarar i ett **låst schema** (strukturerade svar). Varje stycke bär `referenser`.
3. **Maskinell validering:**
   - Alla ID:n finns.
   - Alla siffror finns i underlaget.
   - Nivåer i texten stämmer med bedömningen.
   - Uppgifter som inte är bekräftade skrivs med `[VERIFIERA]`.
   - Inga förbjudna generiska formuleringar och inga personnamn förekommer.
4. Ett underkänt svar körs om med valideringsfelen som återkoppling, högst två omförsök per del (8.4.5). Därefter används programmets mall för delen och ett granskningsfynd skapas, så att dokumentet aldrig stannar tyst och aldrig ser färdigt ut.
5. Godkänt svar sparas med kontrollsumma och går vidare till granskning och sakgranskning (avsnitt 10). Maskinell validering visar inte att en formulering stöds av källan. Det avgör sakgranskningen.

### 8.3 Modell, kostnad och utvärdering

- Claude via Anthropics officiella Python-SDK, bakom ett eget leverantörsgränssnitt.
- **Startinställning:** `claude-opus-5-5`, adaptiv tänkning, effort `high`. Modell och effort är inställningar, inte låsta val. Inför M3 jämförs `claude-sonnet-5-5` på effort `high` och `claude-opus-5-5` på effort `medium` (modellens egen standard); standarden fastställs efter utvärderingen i 8.4.8.
- **AI-utvärdering (etapp M3)** med riktiga skrivuppgifter innan inställningen fastställs. Mått: sakfel, ogrundade påståenden, andel avsnitt som klarar maskinell validering, sakgranskarens tidsåtgång och kostnad per godkänt avsnitt. Valet av modell och effort görs av projektägaren utifrån mätningen.
- **Automatiska tester använder en kontrollerad testleverantör** som ger förutbestämda svar. Prov mot det riktiga API:t är frivilliga, körs separat och kostar pengar.
- Strukturerade svar via SDK:ns `messages.parse` med pydantic-scheman. Claudes inbyggda källhänvisningar går inte att kombinera med strukturerade svar, så programmets egna referens-ID:n används.
- Prompt-cachning: den fasta systemprompten och faktabladet ligger först och är byte för byte identiska mellan anropen i samma tjänst (8.4.2). Cachningen sparar lite, eftersom utdata står för merparten av kostnaden; huvudskälet till en gemensam prompt är att reglerna finns på ett ställe.
- **Batch-API används inte som standard.** Det lagrar begäran och svar hos leverantören i upp till 29 dagar. Det får slås på för underlag som är fritt från personuppgifter, och batcherna raderas då efter att resultatet hämtats.
- Om personuppgifter någon gång måste skickas till AI (fas 2) krävs databehandling inom EU. Anthropics eget API erbjuder i dag bara `us` och `global`, så EU-behandling sker då via Google Vertex AI eller Amazon Bedrock i EU-region.
- Modell, inställningar, promptmall, svar och tokenförbrukning sparas per anrop och tas med i manifestet.

### 8.4 Skrivning av hela dokumentet från faktablad

**Versionsavgränsning, revision 33:** femdelarsflödet nedan beskriver befintliga skrivresultat till och med v5, även för steg 1:s v5.1-dokument. A+B:s steg 2 inför v6-skrivresultat med endast hot och sårbarheter; kontroll-, nivå- och slutsatsanalys kommer då från lokalt granskat underlag. Delinstruktioner, anropskedja och granskningsgrind väljs efter skrivversion, aldrig efter om privat analys finns. Schema per AI-svar och skyddsregler i 8.4.10 består. Detaljer finns i A+B-kontraktet sist i specen. V6-skrivning och lokal dokumentkoppling är implementerade; slutverifiering pågår.

Avsnittet bygger på [researchrapporten om promptdesign](../../research/12-promptdesign-ai-skrivning.md) (2026-10-11) och på en provkörning med syntetisk byrå: Sonnet 5.5 klarade tre av fem tjänsteavsnitt på andra försöket och två underkändes efter tre försök. Fyra av fem underkännandeorsaker gällde sådant som koden kan avgöra (talformat, nivåmeningar, obligatoriska meningar, avsnitts-ID och formatet för oklarheter). **Att de försvinner när koden tar över är en hypotes som piloten ska pröva, inte ett uppmätt resultat.** Principen är att AI ska ansvara för så lite som möjligt och att varje AI-skriven del måste vara bättre än programmets mall. Design, modell och effort i detta avsnitt är preliminära tills sakkunnigutvärderingen i 8.4.8 är genomförd; implementationen före dess är experimentell.

#### 8.4.1 Arbetsfördelning

- **Koden äger fakta och beslut:** alla tal (AI skriver dem som platshållare enligt 8.4.5), risknivåmeningar, obligatoriska meningar, jämförelsen med NRA:s sektorsnivå, datum, källförteckningar, kontrollernas status och belägg samt delen *Beskrivning och omfattning*.
- **Låsta stycken:** kodens stycken i varje del är låsta och skrivs byte för byte likadant varje gång underlaget är detsamma. Hit hör meningen om egen rapportering och erfarenhet (B-15), geografins underlagsstycke (B-09, B-10), nivåmeningarna och beskrivningen. AI-texten skrivs runt dem och får inte återge eller ändra dem.
- **AI skriver den analyserande texten mellan dem:** hur tjänsten kan utnyttjas hos just den här byrån, varför en uppgift spelar roll och hur faktorerna samverkar.
- **AI anger aldrig någon nivå** för risk, sannolikhet eller konsekvens, inte heller för delfaktorer. En sådan mening är en riskbedömning som regelmotorn inte har gjort (regel 1). Delfaktorer beskrivs med andel, antal, period och egenskap.
- Lokala fritexter, namn och kompletteringar går aldrig till AI. Koden sätter in dem som *Byråns komplettering* (14.5).

#### 8.4.2 Promptens delar

Varje anrop består av en fast systemprompt, ett användarmeddelande och ett schema.

- **Systemprompten är densamma i alla anrop.** Den skrivs som löptext där varje regel har sitt skäl, utan versaler eller tryckord, med roll, arbetsfördelning, regler och 3–5 korta syntetiska exempel märkta som illustrativa. Den är minst 512 token så att den kan cachas och innehåller inga datum eller villkorade avsnitt. För Sonnet 5.5 läggs raden *Think the problem through before you answer.* sist, eftersom modellen annars ofta hoppar över tänkandet med strukturerade svar.
- **Användarmeddelandet har en fast ordning:** `<faktablad>` först (JSON med sorterade nycklar; varje post har id, etikett, visningsvärde, period, källtyp och status), därefter cachebrytpunkt, `<lasta_meningar>`, `<maskinellt_validerat>` (bara för motivering och slutsatser), `<uppgift del="…">` och vid omförsök `<aterkoppling>`.
- **Faktabladets integritetsgräns:** faktabladet byggs bara ur tillåtelselistan, som i dag. `källtyp` är ett värde från en sluten lista som koden härleder (till exempel register, intern statistik, egen kännedom, dokument, härledning), aldrig profilens fria källtext. Rå källtext, dokumentnamn, sökvägar och bekräftarens identitet stannar lokalt. Små grupper och små restgrupper visas som ”skyddat värde, prövas lokalt”; saknad bas visas som okänd. Härledda andelar vars antal eller bas inte är tillåtna visas med begränsad precision (8.4.9 punkt 11). Skyddade värden får ingen talplatshållare.
- **Schemat garanterar formen:** `stycken` med `typ`, `referenser` och `text` i den ordningen, där `referenser` är en `enum` över tjänstens ID; `oklarheter` med `uppgift_id` (`enum`) och `fraga`. Alla fält är obligatoriska. Fältet för avsnitts-ID tas bort, eftersom koden redan känner till det. Schemat har inget fält för resonemang; resonemanget sker i modellens tänkande.
- Ingen instruktion om att modellen ska granska sig själv. Valideraren är kontrollen.

#### 8.4.3 Anropsflöde

Preliminär standard är **ett anrop per analysdel** (design B):

1. Koden bygger faktabladet ur tillåtelselistan och skriver *Beskrivning och omfattning* samt alla låsta stycken.
2. *Hot och egna erfarenheter* skrivs först. *Sårbarheter och motivering* och *Kontroller och effekt* skrivs därefter parallellt ur samma faktablad.
3. Varje del valideras för sig och körs om för sig.
4. *Risknivåer och motivering* skrivs med de maskinellt validerade delarna som underlag, och *Slutsatser* med den maskinellt validerade motiveringen. Kedjan för bara vidare AI:s egen maskinellt validerade text, enligt det avgränsade beslutet i 8.4.10 punkt 9. Maskinellt validerad betyder att delen klarat kontrollerna i 8.4.5, inte att den är sakgranskad.

Byråövergripande avsnitt: D-ARB.2 (motiveringen av omfattningen), D-ARB.4, D-ARB.5 och D-ARB.7 skrivs i egna anrop; D-ARB.9 skrivs sist med tjänsternas godkända slutsatser som underlag. D-ARB.1, D-ARB.3, D-ARB.8, D-ARB.10, omvärldsbevakningen och bilagan skrivs av koden i klartext, utan fält-ID.

Delinstruktionerna är separata moduler. Design A, där ett anrop skriver alla AI-delar i en tjänst, är en inställning med samma moduler och behålls som jämförelse i utvärderingen. Programmets nuvarande mallar (C0) är måttstocken.

#### 8.4.4 Delinstruktioner

Varje delmodul anger mål, de krav som styr, fällor med skäl och 2–3 delspecifika exempel. Den fullständiga tabellen med källor finns i researchrapporten; sammanfattning:

| Del | Skrivs av | Mål för AI-texten | Styrande krav | Fällor som förklaras | Maskinell kontroll |
|---|---|---|---|---|---|
| Beskrivning och omfattning | Kod | Ingen AI-uppgift | 14FS 2:2 p. 1; vägledningen | – | Antal eller andel kunder, andel av omsättningen och period finns |
| Hot och egna erfarenheter | AI; koden skriver meningen om egen rapportering | Minst två konkreta sätt som tjänsten kan utnyttjas hos byrån, kopplade till tjänstens kunder och regelbasens hot; terrorfinansiering när sådana hot finns | PTL 2:1; 14FS 2:2 p. 2; NRA | Allmänna hot för alla tjänster; att få rapporter skulle visa lågt hot | Minst två hot-ID; förbjudna mönster om noll rapporter |
| Sårbarheter och motivering | AI | Kunder, kanaler, geografi och verksamhetsspecifika förhållanden: gäller, gäller inte eller okänt, varför och hur stor andel. Samverkan mellan faktorer beskrivs som belagd bara när underlaget visar att de avser samma kunder; annars som ett villkorligt scenario, eller som "ingen belagd kombination" | 14FS 2:2 p. 3; vägledningen; AMLR bilaga I (framtida) | "Gäller inte" utan motivering; "bara svenska kunder"; långa kundrelationer som trygghet; påhittade samband mellan separata indikatorer | Minst ett sårbarhets-ID per kategori; geografi omfattar mer än sanktionslistor; ett kombinationsstycke av typen `analys` kräver en referens till en uppgift om överlapp, annars ska det ha typen `scenario` |
| Kontroller och effekt | Koden skriver status och belägg; AI kopplingen till risken | Vilken risk kontrollen riktar sig mot och vad belägget visar; saknas belagd effekt ska det stå att nivån inte sänks | Vägledningen; metodstöd: AMLA:s riktlinjeutkast och FATF | En beskriven kontroll sänker inte risken; andras kundkännedom sänker inte risken | Inga påståenden om att en kontroll minskar, begränsar, reducerar eller sänker risken; programmet avgör det lokalt (8.4.10) |

Status för styrande krav: PTL och Länsstyrelsernas föreskrifter är gällande rätt; Länsstyrelsens vägledning, NRA och tillsynsbesluten är vägledning och tillsynspraxis. AMLR (EU 2024/1624) är framtida regelverk som för redovisningsbyråernas skyldigheter tillämpas från den 10 juli 2027 ([art. 90](https://eur-lex.europa.eu/eli/reg/2024/1624/oj/eng)). AMLA:s riktlinjeutkast och FATF:s vägledning är metodstöd och inte bindande. Två giltiga referenser i ett stycke visar inte att ett samband finns.
| Risknivåer och motivering | Koden skriver nivåmeningar och NRA-jämförelse; AI motiveringen | Riskbilden som en kedja av hot, sårbarhet, omfattning och konsekvens, utan att AI ser motorns nivåer; förklara skillnader mot NRA:s sektorsnivå | 14FS 2:2 p. 4; vägledningen | Samma nivå för alla tjänster; text som tonar ned nivån | Minst ett hot-ID och ett sårbarhets-ID; inga nivåord i AI-texten |
| Slutsatser | AI; koden skriver ansvarsmeningen | Vad riskbilden betyder för kundkännedom, övervakning och utbildning i just denna tjänst | PTL 2:2–3, 2:8, 2:14; 14FS 2:10 | En slutsats som bara upprepar nivån; allmänna löften | Kundkännedom, övervakning och utbildning nämns; minst ett hot-ID |

#### 8.4.5 Validering och omförsök

**Platshållare.** AI:s råsvar får innehålla två slags platshållare: `{tal:ID}` och `{roll:FfR}`. En `{tal:ID}` är tillåten bara om ID finns i faktabladet, har ett numeriskt värde som inte är skyddat av smågruppsskyddet och finns bland styckets referenser. Okända, otillåtna eller felskrivna platshållare stoppar delen före godkännande. Alla andra fält-ID, villkorsuttryck och interna nycklar är förbjudna i texten. Nästa anrop i kedjan får den maskinellt validerade texten med platshållarna kvar (8.4.10 punkt 9). Koden ersätter platshållarna först vid rendering, och en platshållare som inte kan ersättas stoppar renderingen. Siffror som inte är platshållare kontrolleras som i dag mot faktabladet, efter att mellanslag, hårt mellanslag (U+00A0), smalt hårt mellanslag (U+202F) och decimalkomma normaliserats.

**Det valideraren kan avgöra maskinellt:**
- schemats form, `enum`-värden och att varje referens finns i faktabladet
- platshållarna enligt ovan och siffror utanför platshållare
- att AI-texten saknar nivåord, fält-ID och förbjudna fraser, och inte återger låsta stycken
- de ID och ord som varje del kräver enligt 8.4.4, till exempel minst två hot-ID eller att kundkännedom, övervakning och utbildning nämns
- stycketypen för kombinationer (`analys` kräver en referens till överlapp, annars `scenario`)
- lägsta och högsta längd per del och hur lika samma del är mellan byråns tjänster
- att stoppskälet inte är `max_tokens` eller ett avböjande.

**Det som kräver sakgranskning:** om resonemanget faktiskt stöds av de refererade uppgifterna, om en referens stöder just det påstående den sitter vid, om ett beskrivet samband är rimligt och om texten är tillräckligt tjänstespecifik. Maskinell validering är en förutsättning för sakgranskning, inte en ersättning.

**Omförsök.** Högst två omförsök per del, bara för den underkända delen, med den citerade felmeningen och de tillåtna värdena. Det andra omförsöket görs på högre effort. Därefter används mallen för delen, delen märks som mall i manifestet och ett granskningsfynd skapas. Anrop med högre `max_tokens` än SDK:ns gräns för vanliga anrop strömmas.

#### 8.4.6 Granskningsgrinden för AI-skrivna delar

Dagens grind (`granskning/analys.py`) bygger om hela tjänsteavsnittet med kod och jämför kontrollsumman; bara riskmotiveringen får komma från AI. Den ersätts i samma ändring som AI börjar skriva fler delar, enligt följande kontrakt:

1. **Dokumentformatets version** anger för varje del vilka stycken som är låsta och vilka som är AI-skrivna. Versionen ingår i exportens och granskningens metadata.
2. **Låsta stycken** byggs om från aktuell profil, bedömning och regelbas och ska finnas byte för byte på sin plats. B-09, B-10 och B-15 fortsätter att kontrollera sina låsta stycken som i dag.
3. **AI-stycken** jämförs med det maskinellt validerade utkastet för delen i skrivningens manifest, via kontrollsumma per del. En del som märkts som mall jämförs med mallen.
4. **Avvikelser** i låsta stycken, AI-stycken, ordning, underrubriker eller formatversion ger ett blockerande fynd, som i dag.
5. **Ogiltigförklaring:** ändrad formatversion eller ändrad AI-text upphäver tidigare sakgodkännanden av avsnittet. Ett godkännande gäller exakt den text som exporterades.

Prov ska visa att ändrad AI-text, flyttade låsta stycken och gamla sakgodkännanden fångas lika strängt som med dagens grind.

#### 8.4.7 Spårbarhet

För varje anrop sparas en kontrollsumma över systemprompt, delmodul och schemaversion, vald design, begärd och svarande modell, effort, tokenförbrukning inklusive cachefält, stoppskäl och kategori vid avböjande, försöksnummer och valideringsfel per felklass. Ett livetest kontrollerar att cachen träffar vid andra anropet i samma tjänst.

#### 8.4.8 Utvärdering före val (M3)

1. **Pilot:** 2–3 syntetiska profiler med C0, design A och design B. Kostnaden per byrå räknas fram ur förbrukningen.
2. **Fall:** 24–30 syntetiska profiler, bland annat en liten högrisktjänst bland stora lågrisktjänster, noll rapporter, okända uppgifter och många tjänster, plus 6–8 par där en uppgift ändrats. Delning i utvecklings- och testprofiler låses. En sakkunnig skriver checklistor per fall och del.
3. **Bedömning i tre lager:** deterministiska kontroller; en AI-domare av annan modell än skribenten med en ja/nej-fråga per kriterium, som används som krav först när den når minst 0,9 träffsäkerhet för både godkända och underkända fall; blind sakkunnig granskning med tidtagning.
4. **Krav för godkännande** är metodval som projektägaren beslutar, till exempel noll sakfel och nivåfel i den sakkunniges granskning och kortare sakgranskningstid än med C0.
5. **Val:** bland inställningarna som klarar kraven väljs den med lägst kostnad per godkänt avsnitt och kortast sakgranskningstid. Skillnader inom den statistiska osäkerheten räknas som oavgjorda, och då vinner den enklare inställningen.

Batch-API får användas för syntetiska profiler, som saknar personuppgifter, och batcherna raderas efter att resultatet hämtats. Uppskattad API-kostnad för hela utvärderingen är några hundra dollar; den sakkunniges tid är den verkliga gränsen.

#### 8.4.9 Klartext i låsta stycken (format `D-ARB-tjanst-v4`)

Låsta stycken skrivs för läsaren, inte för programmet:

1. Löptexten innehåller inga fält-ID, villkorsuttryck eller katalogkoder. En uppgift skrivs med fältets kortnamn, värde, period, källa och datum. Kortnamnet (`etikett`) är visningstext i regelbasen och ändrar ingen regel. Tjänste- och kontrollfält får namn efter tjänstens och kontrollens namn.
2. Villkor skrivs i ord, till exempel ”Sårbarheten gäller om andel kunder i riskbranscher är minst 20 %”.
3. När en jämförelse med en gräns inte är uppfylld men det bekräftade värdet är större än noll, skriver programmet att faktorn förekommer men ligger under metodens gräns för automatiskt riskpåslag. Motorns utfall och gränsen ändras inte. I faktabladet gäller tillåtelselistan och smågruppsskyddet. När värdet är skyddat eller inte får nå AI skriver faktabladet ingen gränsmening, så att texten blir densamma oavsett det skyddade värdet.
4. Sektorsreferensen anges med källans titel, nivå, skala och sida.
5. Spårbarheten finns kvar. Varje stycke behåller sina referenser, och bilagan `D-ARB.B1` anger kortnamn och fält-ID för varje uppgift.
6. Övergången till v4 ändrar texten i låsta stycken och upphäver därför tidigare sakgodkännanden enligt 8.4.6 punkt 5. Utkast i v3 skrivs om. Fastställda paket byggs aldrig om och förblir oförändrade.
7. En andel som är större än noll men skulle visas som 0 % skrivs ”mindre än 1 %”, och en andel under 100 % som skulle visas som 100 % skrivs ”mer än 99 %”. Det gäller på samma sätt i låsta stycken, faktablad och platshållare. Ett sådant intervall lagras inte som ett exakt tal.
8. Katalogkoder och kontrollsummor (regelpaket, källor) står bara i referenser och i bilagan `D-ARB.B1`. Löptexten använder titlar och namn.
9. Ny fastställelse kräver att varje tjänsteavsnitt i granskningens dokument har aktuellt format. Äldre fastställda paket kan fortfarande läsas.
10. En andel som avrundad till hela procent skulle visas som en av metodens gränser (strikt mellan 0 och 100 %) fast den inte är lika med gränsen, visas med så många decimaler som behövs för att hamna på rätt sida, högst två (metodval). Mot gränsen 20 % visas 195 av 1 000 som 19,5 % och 204 av 1 000 som 20,4 %. Räcker inte två decimaler skrivs ”strax under 20 %” eller ”strax över 20 %”, och det lagras som ett intervall. Det gäller i låsta stycken, gränsmeningar och intagsvyer samt för värden som får visas i faktabladet. Själva metodgränsen behåller sina decimaler. Punkt 7 gäller vid 0 och 100 %. Motorns gränser och utfall ändras inte. För AI gäller punkt 11 när en härledd andels antal eller bas inte är tillåtna.
11. En härledd andel vars antalfält eller basfält inte står på tillåtelselistan visas för AI med begränsad precision (metodval). Den visas i hela procent, och inom en halv procentenhet från en metodgräns bara med sidan om gränsen: ”strax under 20 %” eller ”minst 20 %”, lagrat som intervall. Smågruppsskyddet går före, och punkt 7 gäller vid 0 och 100 %. Lokala texter behåller decimalerna enligt punkt 10. Visningen får inte avslöja mer än hela procent och sidan om gränsen, som gränsmeningen och utfallet redan visar. Ett prov räknar ut vilka antal som går att härleda ur andel och bas: små grupper och små restgrupper får aldrig gå att härleda, medan exakta antal från fem och uppåt kan gå att härleda även vid större kundbaser. Användaren godkände denna avgränsning 2026-10-14. Hela kundbasen kan vara exakt härledbar även vid stora baser och redovisas separat. Resultaten avser provade baser och profiler, inte en generell gräns vid 200 eller 400 kunder. Hela AI-begäran, inklusive andra antal, gränsmeningar, sårbarhetsutfall och omförsök, prövas också för smågruppsskyddet. Resultaten redovisas i STATUS. Antalsfälten läggs inte på tillåtelselistan utan ett särskilt beslut.

#### 8.4.10 Skyddad AI-begäran

1. Hela den utgående begäran till AI – systemprompt, varje dels innehåll, återkoppling vid omförsök och svarsschema – ska bara bero på det AI får se. Två profiler som bara skiljer sig i uppgifter utanför tillåtelselistan eller i smågruppsskyddade värden (värden som AI ser maskerade eller som okända) ska ge identisk begäran.
2. AI får därför aldrig motorns risknivåer, regelspår eller de kodskrivna nivåmeningarna. Nivåmeningarna skrivs som tidigare lokalt i dokumentet. AI motiverar riskbilden utifrån hot, sårbarheter, kontroller och faktauppgifter utan att ange nivåer.
3. En sårbarhet vars villkor läser en uppgift utanför tillåtelselistan eller ett smågruppsskyddat värde får utfallet ”prövas lokalt” i faktabladet. Beslutet fattas ur det AI får se, inte ur råvärdet. Motorns lokala bedömning ändras inte. Sårbarhetskatalogen beskriver fortfarande möjliga hot och faktorer, medan programmet skriver den lokala tillämpningen.
4. Kontrollernas kategorifält (utformning, genomförande och bedömd effekt) ingår i tillåtelselistan efter beslut 2026-10-13. Kontrollernas utfallstext ingår inte. Kontrollstatusen till AI byggs enbart av kategorierna. Om en kontroll räknas som riskreducerande avgörs lokalt, eftersom den bedömningen också bygger på utfallsfältet, och AI skriver aldrig att en kontroll minskar risken.
5. Den äldre skrivvägen utan faktablad får inte användas med riktiga AI-anrop. Historiska utkast och paket kan fortfarande läsas.
6. Prov visar identisk begäran för 0, 1, 3 och 4 kunder, för ett maskerat litet komplement, för en liten grupp mot en liten restgrupp (3 och 97 av 100), för saknad bas, för ett smågruppsfält och en ja/nej-uppgift utanför tillåtelselistan, för kontrollernas utfallstext, för olika bekräftade personnamn med samma svar (även i genitiv) och vid omförsök. Identitetsproven körs med profilens verkliga personnamn.
7. Bekräftade personnamn prövas bara lokalt. Varken återkopplingen vid omförsök eller antalet anrop får bero på om AI:s svar innehåller ett namn. När alla delar i en tjänst är skrivna prövar programmet varje godkänt delsvar mot de bekräftade namnen (hela namn med ordgränser och valfritt genitiv-s, utan skillnad på stora och små bokstäver). En del som innehåller ett namn ersätts av mallen och får ett blockerande granskningsfynd som säger att delen innehöll ett bekräftat personnamn. Endast fält med egenskapen `namnfalt` i regelbasen ingår (i dag P-ROLL.ffr_namn); ansvarsfunktionens rolltext är inte ett personnamn. Egenskapen serialiseras bara när den är satt, så att historiska kontrollsummor består. Rollplatshållare undantas från namnmatchningen. Kontrollen före dokumentbygget finns kvar. Återkoppling om felaktiga platshållare och fält-ID anger deras ordningsnummer i stycket men citerar inte AI:s text.
8. Ett smågruppsskyddat värde visas för AI med samma text, ”skyddat värde, prövas lokalt”, oavsett om det är gruppen eller resten som är liten. AI kan därför inte se på vilken sida en liten grupp ligger. Lokala texter visar som tidigare de verkliga värdena.
9. Uttryckligen godkänt av användaren 2026-10-14 om kedjan: tidigare AI-genererad, maskinellt validerad text får återanvändas som underlag för risknivåer och slutsatser (8.4.3 punkt 4). Kedjan innehåller bara AI:s egen text; inga namn eller andra uppgifter hämtas från profilen. Den lokala namnkontrollen körs först när tjänstens alla anrop är gjorda, och dess resultat påverkar aldrig nästa anrop. Ett namn som AI själv har skrivit kan därför skickas tillbaka till AI, utan att programmet bekräftar att namnet finns i profilen. Prov visar att kedjans innehåll och antalet anrop är identiska för profiler med olika namn.

## 9 Granskning (maskinell)

| Nivå | Kontroll | Typ |
|---|---|---|
| 1 Täckning | Varje tillämpligt krav har minst ett avsnitt. Varje erbjuden tjänst har eget avsnitt med hot, sårbarheter och motiverad nivå. | Deterministisk |
| 2 Spårbarhet | Alla referenser finns. Alla verksamhetspåståenden pekar på profiluppgifter. Alla obligatoriska datum finns. | Deterministisk |
| 3 Bristmönster | Bristmönsterkatalogen (`regelbas/kataloger/bristmonster.yaml`) | Deterministisk, senare kompletterad med AI |
| 4 Provtillsyn (M7) | AI bedömer dokumenten som en handläggare utifrån föreläggandets punkter och en rubrik | AI |

Exempel ur bristmönsterkatalogen v0 (ID:n enligt [research 03](../../research/03-tillsyn-och-sanktioner.md)):

- B-01 Den allmänna riskbedömningen saknas eller förväxlas med kundbedömning eller rutiner.
- B-02 Mallen är inte anpassad till verksamheten.
- B-03 Otillräcklig identifiering och analys av hot och sårbarheter.
- B-04 Tjänster beskrivs tillsammans utan individuell analys.
- B-09 Geografi kopplas bara till sanktionslistor.
- B-12 Sammantagen risk utan analys av hur nivån nåtts.
- B-13 Alla nivåer låga utan hänsyn till sektorsrisken i den nationella riskbedömningen.
- B-16 Datum för utvärdering och uppdatering saknas.

Vad fynden betyder för dokumentets status framgår av avsnitt 10.

## 10 Dokumentstatus och grindar

```
utkast ─► granskat ─► sakgranskat ─► fastställt av byrån (låst) ─► ersatt
```

| Övergång | Villkor |
|---|---|
| **Export som utkast** | Alltid tillåten. Varje sida märks "UTKAST – ej fastställt av byrån", och åtgärdslistan med öppna punkter bifogas. |
| utkast → **granskat** | Maskinell granskning är körd och har inga *blockerande* fynd. |
| granskat → **sakgranskat** | En ansvarig person har gått igenom varje avsnitt mot fakta och källa och godkänt sakpåståenden och motiveringar. Vem, när och avsnittets kontrollsumma loggas. Text som ändras av en människa valideras maskinellt igen. |
| sakgranskat → **fastställt av byrån** | Alla villkor nedan är uppfyllda och ett behörigt organ (styrelse eller ledning) har fattat beslut. Namn, roll och datum registreras. |

Villkor för fastställelse:

1. Alla **kritiska** profiluppgifter (sådana som används av en beslutstabell eller ett ska-krav) har status *bekräftad* eller *ej tillämplig* med motivering.
2. Ingen bedömning har status *preliminär*, och texten innehåller inga `[VERIFIERA]`.
3. Alla krav i regelpaketet som är tillämpliga på byrån **för paketets datum** har sakkunnigstatus *verifierad*, och regelpaketets paragrafkarta för samma datum och län är sakkunniggranskad (avsnitt 6.4 och 16.1).
4. Fynd hanteras efter vad de gäller:

   | Fynd gäller | Får fastställas om |
   |---|---|
   | **Metodval** (skala, gräns, poäng, vikt, formulering) | Fyndet är åtgärdat, eller funktionen för regelefterlevnad har accepterat avvikelsen med motivering (registreras som avvikelse) |
   | **Allmänt råd, tillsynspraxis eller EU-utkast** (ej bindande) | Fyndet är åtgärdat, eller funktionen för regelefterlevnad har valt en annan metod och motiverat hur det **bindande** krav som rådet hör till ändå uppfylls. Avvikelsen registreras med hänvisning till det bindande kravet. |
   | **Ska-krav i lag eller föreskrift** som saknas eller är fel tillämpat | Fyndet är åtgärdat, eller en sakkunnig har bedömt det särskilt och dokumenterat varför kravet är uppfyllt eller inte tillämpligt. Byrån kan inte själv acceptera bort ett lagkrav. |
   | **Blockerande** fynd av alla slag | Aldrig. Fyndet måste åtgärdas. |

5. Sakgranskning är gjord för varje avsnitt och gäller den aktuella kontrollsumman.
6. Versionshistorik, datum för utvärdering och datum för nästa genomgång är ifyllda (avsnitt 13.1).

Vid fastställelse låses paketet och bevaras enligt avsnitt 5.3. Programmet skriver "Fastställt av [organ] [datum]". Det skriver aldrig att regelverket är uppfyllt eller att dokumentationen är godkänd.

## 11 Utdata i fas 1

| Dokument | Innehåll | Mottagare |
|---|---|---|
| Allmän riskbedömning | Översikt, tjänster, hot, sårbarheter, risk per tjänst, sammanvägning, slutsatser, omvärldsbevakning, utvärdering | Ledning, FfR, tillsyn |
| Metodbilaga | Skalor, matris, beslutsregler med grund, vikter, gränser, källor och hur de använts, kända begränsningar | FfR, tillsyn |
| Valideringsrapport för modellen | Enligt 7.8 | FfR, ledning |
| Rutiner och riktlinjer | Kundkännedom, övervakning, rapportering, bevarande, intern kontroll med modellriskhantering, personal | Alla |
| Arbetsinstruktioner per roll | Korta checklistor för konsult, FfR och ledning | Respektive roll |
| Kundriskmodell och kundformulär | Mall med de fyra spåren i 7.6 | Konsulter |
| Kravmatris | Krav, var det uppfylls, status beskrivet, infört och kontrollerat | FfR, tillsyn |
| Åtgärdslista | Öppna `[VERIFIERA]`, fynd, avvikelser och beslut som saknas | FfR |
| Index för tillsynspaket | Föreläggandets punkter kopplade till dokument och loggar | FfR |

## 12 Kommandon

```
riskanalys regelbas validera
riskanalys ny <byrå> --sektor redovisning --lan "Västra Götaland" --datum 2026-11-01
riskanalys intag <byrå>
riskanalys bekrafta <byrå>                    # bekräfta profiluppgifter
riskanalys bedom <byrå>
riskanalys skriv <byrå> [--avsnitt D-ARB.6.1]
riskanalys granska <byrå>
riskanalys sakgranska <byrå>                  # mänsklig granskning per avsnitt
riskanalys avvikelse <byrå>                   # registrera motiverad avvikelse
riskanalys exportera <byrå> --utkast
riskanalys faststall <byrå> --beslut "styrelsen 2026-11-15"
riskanalys verifiera <byrå> <version>         # kontrollera paket mot manifest
riskanalys andring <byrå>                     # ändringskontroll, se 13.1
```

## 13 Drift och livscykel

### 13.1 Minsta drift (före första riktiga fastställelse)

- **Versionshistorik** med datum och typ av händelse för varje utvärdering och uppdatering, även när inget ändras.
- **Datum för utvärdering och för nästa genomgång**, senast tolv månader efter den senaste utvärderingen. En utvärdering utan ändring dokumenteras med motivering.
- **Ändringskontroll** (`riskanalys andring`): innan byrån erbjuder en ny eller väsentligt ändrad tjänst, vänder sig till en ny marknad eller gör andra relevanta förändringar ställer programmet frågorna i föreskrifternas 2 kap. 3 § och visar vilka avsnitt som behöver utvärderas.

### 13.2 Full drift (senare etapp)

- Påminnelser.
- Utlösande händelser från referensdata: ny landlista, ny nationell riskbedömning, ändrad föreskrift. Programmet jämför referensdatans kontrollsummor med dem som det fastställda paketet låste och visar vilka avsnitt som påverkas.
- Belägg: utbildningslogg, kontrollplan med resultat och stickprov. Belägg från driften blir indata till nästa års bedömning av kontrollernas genomförande.

## 14 Användarflöde

Före användning hos en riktig byrå ska flödet nedan kunna genomföras av den person som faktiskt sakgranskar. Det får vara ett enkelt lokalt formulär. M1 kan byggas som kommandorad för att bevisa kedjan.

1. Välj tillämpligt regelpaket och datum.
2. Beskriv varje erbjuden tjänst.
3. Bekräfta byråns uppgifter.
4. Pröva hot och sårbarheter per tjänst.
5. Motivera risknivåer och kontrollernas faktiska effekt.
6. Granska varje utkast mot fakta och källa.
7. Besluta och fastställ.
8. Följ upp förändringar.

I varje steg ska användaren

- se **varför frågan ställs**: vilket krav, vilken regel och vilken källa den hör till,
- kunna markera **"ej tillämpligt" med motivering**,
- kunna **rätta ett felaktigt förslag** (rättelsen loggas och valideras),
- se vad som är *preliminärt* och varför.


### 14.1 Fullständigt intag och skrivning av hela riskbedömningen

Programmet ansvarar för att fråga efter allt relevant underlag som behövs för den valda leveransen. Användaren ska kunna börja med en tom profil, utan en tidigare riskbedömning, YAML-redigering eller kännedom om fält-ID:n. Första leveransen är hela den allmänna riskbedömningen. Rutiner, kundmall och övriga dokument har separata leveranser; en färdig riskbedömning får inte beskrivas som bevis för att alla byråns skyldigheter är genomförda.

Intaget ska vara en sparbar intervju med grundfrågor och villkorade följdfrågor. Varje fråga hör till ett versionerat fält och redovisar syfte, koppling till krav/metod och vilket avsnitt svaret används i. Befintliga fältfrågor är utgångspunkt, men antalet besvarade fält är inte ett bevis för ett fullständigt underlag.

| Område | Underlag som intervjun ska täcka när det är relevant |
|---|---|
| Byrån och omfattningen | Verksamhetsutövare, säteslän/filial, faktiska yrkesroller, bedömningsdatum, storlek, verksamhetsställen och ansvarsfördelning |
| Tjänster och befogenheter | Alla erbjudna tjänster, hur de utförs, omfattning, betalningsbehörighet, klientmedel, bolagstjänster och andra befogenheter |
| Kunder | Aggregerade kundtyper, branscher, ägarstrukturer och relevanta riskegenskaper; antal, nämnare, statistikperiod och källa |
| Leverans och kontakt | Kundintag, distansarbete, identitetskontroll, ombud/tredje parter, system, underlag och insyn i transaktioner |
| Geografi | Relevanta länder och anknytningar, omfattning och omständigheter som påverkar respektive tjänst |
| Hot och erfarenheter | Verksamhetens relevanta scenarier för penningtvätt och terrorfinansiering, avvikelser och lärdomar av egen rapportering utan kundidentifierande uppgifter |
| Sårbarheter och kontroller | Tjänsternas och organisationens svagheter, faktiska arbetssätt, kontrollernas utformning, genomförande och belägg för deras effekt |
| Uppföljning | Befintliga rutiner, kända brister, ansvar, utvärdering/uppdatering och planerade relevanta förändringar |

Om en tjänst erbjuds ska programmet fråga hur den används och av vilka kundgrupper, kanaler och geografiska anknytningar. Gemensamma totalsiffror räcker inte automatiskt som underlag för varje tjänst. Härledda andelar beräknas från antal och nämnare med samma period; användaren behöver inte svara på samma uppgift flera gånger. Överlappande kategorier förklaras och får inte behandlas som en fördelning som måste summera till 100 procent.

Intervjun ska tillåta att användaren sparar och fortsätter senare, svarar att en uppgift är okänd, samt anger noll, nej eller ej tillämpligt där det är ett sakligt svar. Saknas får inte omvandlas till nej, noll eller låg risk. Villkorade frågor visas när tillämpligheten är känd; vid okänd tillämplighet ställs först frågan som avgör den. Ett svar om ej tillämpligt behöver en motivering och får inte användas för att acceptera bort ett tillämpligt krav.

Programmet ska kontrollera typ, period, källa, belägg, aktualitet och motsägelser. När ett grundsvar ändras ska berörda följdsvar, bedömningar och godkännanden omprövas; tidigare uppgifter bevaras för spårbarhet och blir inte automatiskt bekräftade för den nya situationen.

**Rättelser efter Claude-granskningen 2026-10-10:** Webb och CLI använder samma intagshantering för kanoniska intagsfält och atomiskt revisionsskydd vid sparande. Äldre alias kan läsas men ändras genom sin kanoniska fråga. Aktiva frågor kan inte väljas bort med CLI. XML-ogiltiga tecken avvisas vid svar/bekräftelse och handredigerade profiler kontrolleras före AI-anrop. Datum-, validerings- och exportfel har skilda meddelanden. Skrivformuläret har en engångstoken bunden till profilrevisionen; token förbrukas före skrivning även vid fel. Ett nytt uttryckligt försök kräver ett nytt formulär. Detta skyddar dubbelpostning inom en lokal session, inte flera samtidigt startade program mot samma byrå.

”Vet inte” gör uppgiften obekräftad men behåller tidigare värde, källa, beläggsdatum, bekräftare och period. Tidigare belägg visas som historiska, inte som bekräftelse av ett aktuellt faktum. Ny okänd uppgift får registreringsdatum; rollen behövs först för en bekräftelse. Kompletteringsmotiveringen sparas och profilhistoriken bevarar tidigare revisioner.

Säteslän och filialstatus får rättas i samma bedömningsprofil via svarshanteringen. Profilens effektiva län och regelpaket uppdateras tillsammans vid ett uttryckligt sätesläns-/filialsvar när båda grundsvaren är kända. Ett orelaterat svar får inte tyst rätta en handredigerad län/paket-konflikt. Berörda verksamhetsuppgifter blir inaktuella och gamla bedömningar/utkast kan inte användas som aktuella. Även återbekräftelse av samma grundvärde utlöser denna omprövning om profilens effektiva län eller regelpaket ändras. Handredigerade motsägelser mellan län och paket stoppas fortsatt. Bedömningsdatum ändras inte av denna rättelse. Detta är en korrigeringspolicy för intaget; en ny bedömning med nytt datum behöver separat profil.

### 14.2 När underlaget räcker

En versionerad täckningskarta ska koppla varje tillämpligt dokumentkrav, metodberoende och verksamhetspåstående till frågor, uppgifter eller beräknat underlag. Tillämpliga krav utan koppling ska redovisas som en lucka. Även nödvändiga beskrivande uppgifter ska ingå; enbart fält som riskmotorn använder räcker inte.

Programmet ska visa vad som saknas, varför det behövs och vilken fråga eller åtgärd som löser luckan. Kontrollen av fullständighet görs mot kravkartan och underlagets kvalitet, inte bara mot om formuläret är ifyllt. Om ett relevant förhållande ligger utanför stödet ska det visas och hanteras före fastställelse.

När underlaget räcker bygger motorn bedömningen och programmet skriver och sammanställer hela riskbedömningen med källhänvisningar, motiveringar och uppföljning. Användaren ska inte behöva skriva analysens avsnitt. Sakuppgifter bekräftas och texten sakgranskas i samma användarflöde. Om skrivningen skapar en ny oklarhet ska den återföras till en konkret kompletteringsfråga; ett svar behöver ompröva berörda bedömningar och textavsnitt. Öppna oklarheter och saknade kritiska uppgifter hindrar fastställelse enligt avsnitt 10.

### 14.3 Prov som krävs för intaget

Före första riktiga byrå ska syntetiska användningsprov visa att:

- en tom profil kan fyllas genom intervjun och ge hela riskbedömningen utan manuell text- eller profilredigering,
- olika tjänster, tillsynsområden och verksamhetsstorlekar ger rätt följdfrågor och dokumentunderlag,
- en liten tjänst med hög risk inte försvinner bakom byråns totalsiffror,
- saknade, motstridiga, inaktuella eller otillräckligt belagda svar ger riktade kompletteringar och hindrar fastställelse,
- ändrade grundsvar omprövar berörda följdsvar och godkännanden utan att radera tidigare belägg,
- varje tillämpligt krav har ett kontrollerat underlag och varje verksamhetspåstående är spårbart,
- personuppgifter stannar i lokal lagring och tillåtelselistan gäller även kompletteringssvaren.

Den första tekniska delen av intaget är implementerad 2026-10-10 enligt [intagsplanen](../plans/2026-10-10-intag-och-hel-riskbedomning.md): lokal sparbar intervju, kontroll av beroenden och hela Word-utkastet. Obligatoriska sakuppgifter behövs före skrivning; redan dokumenterad sektorsmotivering är frivillig inför utkastet men B-13 och sakgranskning gäller före fastställelse. Faktisk utvärdering registreras uttryckligen. Aktiva frågor kan inte avfärdas som ej tillämpliga; nej/noll/okänt och villkorat dolda frågor används. Fråge- och täckningskontrakten ska dessutom prövas mot sakkunnigbekräftade tillsynsfall i M3; M4 omfattar pilot, det sammanhållna sakgranskningsflödet, installation och driftprov före M5. Dokumentimport är ett senare stöd och får inte vara ett villkor för att skapa den första riskbedömningen.

### 14.4 Registeruppgifter i lokalt intag

SCB:s avgiftsfria AFR används efter registrering av personlig nyckel. Nyckeln hålls lokalt i `RISKANALYS_SCB_API_KEY` och visas aldrig i formulär, ögonblicksbilder eller fel. Organisationsnummer identifierar juridiska personer; enskilda näringsidkare kan fortsatt besvara intaget manuellt.

Hämtningar blir separata, privata ögonblicksbilder med ursprung, identitet, hämtningstid och kontrollsumma. Hämtningstid är inte uppgiftens giltighetsdatum. API:t ger aktuell registerbild och kan inte styrka historiska förhållanden. Lokal SCB-JSON-import är tillåten men märks som ej verifierat ursprung. Förslag bekräftar inga profiluppgifter automatiskt och skriver aldrig över tidigare svar.

Namn och säteslän kan föreslås; registrerat arbetsställeantal kräver kontroll mot faktiska arbetsställen. Anställdas storleksklass ersätter inte personer inklusive ägare. Omsättningsklass/år ersätter inte aktuell exakt omsättning och period. SNI/juridisk form/registerstatus används som bakgrund; tjänster, kundgrupper, befogenheter, kanaler, geografi, kontroller och erfarenheter frågas fortfarande. Bekräftelse använder ordinarie profilvalidering och invaliderar berörda följdsvar. Vid motstridiga källuppgifter visas både registerförslag och profilsvar. En hämtning blir inte en ny bedömning eller utvärdering.

Filialsvaret vid registerstart kräver eget underlag eller ett uttryckligen valt Bolagsverksförslag enligt schema 4; SCB-bildens allmänna källhänvisning kan inte belägga det. En ny hämtning/import efter profilens bedömningsdag avvisas före nätanrop och visas inte som möjligt val. Lagringen har samma datumgrind och behåller tidigare användbar bild. Bekräftelse kontrollerar fortfarande bildens datum. Bedömningsdatum uppdateras aldrig automatiskt för att få en hämtning att passa.

Samlad registerstart och senare bekräftelse kräver ett uttryckligt fälturval, även i råa formuläranrop. Saknat säteslänsurval vid registerstart får inte bekräfta länet. Alla valda svar valideras genom ordinarie svarshantering i minnet före ett enda atomiskt CAS-sparande. Avvikande tidigare svar kräver separat ersättningsval. Grundändringar behandlas före följdsvar. Bekräftelse gör inga nätanrop och markerade förslag blir inte sakkunnigattester.

SCB-registerschema 2 lägger till F-skatt/moms/arbetsgivarstatus som bakgrund. Schema 3 lägger till `agKat`: endast kod 41 (privat svenskkontrollerat utan koncerntillhörighet) ger ett villkorat ”nej”-förslag för yttersta moderföretag. Koden, begränsningen och kravet på aktuell egen kontroll visas före bekräftelse. Andra/saknade koder ger inget sådant förslag och filial härleds inte. Schema 1 och 2 serialiseras med samma fält och summa som tidigare. Nyckel kan anges i lokalt lösenordsfält för serverns session, utan lagring eller återgivning; miljövariabel stöds fortfarande. Tidigare roll föreslås, och senaste framgångsrikt sparade roll återanvänds inom sessionen. Tjänsteutbudet kan bekräftas på en sida med gemensam källa, roll och datum; nej för omarkerade tjänster kräver uttrycklig bekräftelse av hela listan. Enskilda okända svar finns kvar. Progressen räknar frågor som kan besvaras nu; fullständighetsgrinden är oförändrad. Fråge-/översiktssidan använder en färsk profil per förfrågan och ingen kvarhängande cache av belägg.

Enkla verksamhetsfakta och beskrivningar har det uttryckliga underlagsvalet ”Egen kännedom om verksamheten” enligt en begränsad tillåtelselista. Det gäller inte numeriska uppgifter, periodstatistik, sektorsmotiveringar eller kontrollutformning/genomförande/belägg. Tidigare aktuella bekräftade manuella underlag kan föreslås inom samma kategori; ekonomistatistik, kundstatistik och erfarenhetsstatistik hålls åtskilda, liksom varje kontroll och dess fas. Registerbildens källhänvisning blir inget generellt manuellt underlag. Statistikperiod föreslås från aktuell bekräftad kundbas respektive omsättning. Ett återanvänt underlag måste finnas i den färska profilen, passa kategorin och ha exakt samma period som det nya svaret. Okända/inaktuella svar är inga förslag. Formuläret visar valet; sparande kräver användarens bekräftelse och ordinarie validering/CAS.

Grund-/översiktssidan och skrivknappen anger faktisk leverans: byråns allmänna riskbedömning som Word-utkast, med verksamhet, risker per tjänst, kontroller och åtgärder samt granskningsbilaga vid öppna fynd. Separata rutindokument och individuella kundriskbedömningar ingår inte i detta intags skrivflöde. Sakgranskning, utvärdering och fastställelse är senare uttryckliga steg.

Bolagsverkets avgiftsfria HVD används i en första, separat läsväg efter verifierat tekniskt kontrakt och åtkomst (användargodkänd 2026-10-14). `riskanalys bolagsverket ORGNR` läser `BOLAGSVERKET_CLIENT_ID` och `BOLAGSVERKET_CLIENT_SECRET` ur samma privata nyckelfil som SCB/Claude, hämtar en token som bara finns i minnet och visar aktuell företagsinformation samt metadata för tillgängliga digitala årsredovisningar. Token förnyas före utgång och högst en gång vid nekad dataåtkomst; permanenta fel blir tydliga felmeddelanden. Endast juridiska organisationsnummer tillåts. Identitet, svarsstorlek och använda fälttyper kontrolleras; delfel får inte presenteras som frånvaro av ett riskförhållande. Okända svarsfält och råa feltexter visas inte. Kommandot sparar inga filer eller profilsvar och gör inga AI-anrop. Intagsbekräftelse, dokumentnedladdning och iXBRL-tolkning ingår inte i denna första version. Allabolag kräver separat åtkomst-/villkorsprövning. Råa registerdata och identiteter går inte till AI.

**Godkänd fortsättning 2026-10-14, registerschema 4:** Samma webbformulär kan hämta SCB och Bolagsverket. SCB förblir källa till namn/län/arbetsställen/koncernförslag. Bolagsverkets organisationsform AB/FL ger ett filialförslag; andra koder ger inget. Registrerad beskrivning är ett lokalt redigerbart utkast för P-BESK.verksamhet. Användarens komplettering märks i källan. Bolagsverkskällan kan inte återanvändas för andra frågor. Avvikande myndighetsnamn visas för kontroll.

Senaste entydiga digitala årsredovisningspaket kan ge nettoomsättning och medelantal anställda. Originalet sparas privat med SHA256. Läsaren stöder verifierad gen-base-taxonomi 2021-10-31, odimensionerad bolagskontext, SEK och avgränsade numeriska transformationer. ZIP/XML är storleksbegränsade, ingen extraktion till godtycklig sökväg eller extern XML-resurs sker. Identitet, period, valuta, skala, precision och dubbletter prövas; exakt belopp krävs. Unsupported format, skadad komprimering och osäker metadata ger bokslutsnotis utan beloppsförslag, medan hämtade grundfakta kan användas. Medelantal visas som bakgrund vid frågan om faktiskt personantal inklusive ägare.

Omsättning överförs bara med uttryckligt periodgodkännande. Befintlig aktuell kund-/tjänstestatistik med annan period blockerar förslaget; senare statistik svaras för samma godkända bokslutsperiod eller efter att omsättningsunderlaget bytts. Bokslutsperioden föreslås i kundfrågorna om kundbasperiod saknas. Saknat fälturval, fel byrå, gamla snapshots/revisioner, datumkonflikter och saknade ersättningsval stoppar sparandet. Enskilda gamla registerendpoints tillåter inte att de nya fälten kringgår det samlade flödet. Validering sker före en enda profilsparning. Schema 1–3 serialiseras oförändrat. Inga nya riskregler, AI-tillåtelser eller kundimporter ingår.

### 14.5 Kryssfrågor i stället för fritext

En syntetisk helkörning med regelbas 1.2.0 och fem tjänster gav 150 frågor på 137 sidor, varav 53 fritexter. Fritexten kan inte gå till AI (regel 2) och klistras därför in ordagrant i Word. Användaren ska i stället lämna fakta genom kryss, och AI skriver texten utifrån dem (8.4).

| Grupp | Frågor | Form |
|---|---|---|
| Gemensamma arbetssätt | Kanaler och identifiering, rutiner och omprövning | Kryssrutor för byrån. Varje tjänst bekräftar uttryckligen *Samma som byrån* eller anger sina avvikelser. Bekräftelsen sparas per tjänst med källtyp, period och funktion. |
| Kundpopulation | Kundtyper och ägarstrukturer, geografi, riskindikatorer | Byråns kryss visar vad som förekommer i hela kundbasen men styrker inget om en enskild tjänst; att byrån har PEP-kunder visar inte att de använder lönehantering. Varje tjänst bekräftar sin egen omfattning med källtyp och period. Omarkerat är okänt tills ett nej har bekräftats. Antal och andelar ärvs aldrig mellan olika kundbaser. Geografi har snabbvalet *Endast Sverige*, som ett svar att bekräfta och inte som ett förifyllt sant värde; analysen ska ändå pröva andra geografiska förhållanden. |
| Kryss per tjänst | Arbetssätt och befogenheter, avvikelser i tjänsten | Tjänstespecifika alternativ, till exempel betalbehörighet eller ombud hos Skatteverket. Avvikelser har snabbvalet *Inga kända avvikelser i någon tjänst*. |
| Riskindikatorer på en sida | Regelbasens riskindikatorer | En sida med kryss för byrån i stället för en sida per indikator. Tjänstens omfattning bekräftas enligt raden Kundpopulation. |
| Fortsatt text | Namn på byrån och funktionen för regelefterlevnad, belägg för kontroller, frivillig sektorsmotivering, övriga riskförhållanden | Belägg får stöd i form av kryss för typ (checklista, logg, stickprov), datum och var underlaget finns. Dokumentnamnet skrivs. |

- **Komplettering:** varje kryssfråga har en frivillig ruta *Komplettering (skickas inte till AI)*. Koden sätter in den som *Byråns komplettering* efter AI-texten. Eftersom AI inte ser kompletteringen kontrollerar sakgranskningen att de inte motsäger varandra.
- **Regelbasen:** kryssalternativen är regelbasposter med källa och grund; gränser och urval märks `metodval`. Tillåtelselistan utökas med källa för de kryssfakta som AI får se. *Vet inte* är alltid möjligt, och ett ändrat kryss omprövar beroenden på samma sätt som andra grundsvar.
- **Beskrivning och omfattning** per tjänst skrivs av koden ur kryssen och talen (8.4.1).
- **Mål:** för en byrå med fem tjänster ska högst cirka tio textrutor behöva fyllas i, och antalet sidor ska vara betydligt lägre än i regelbas 1.2.0. Målet mäts med samma syntetiska helkörning som användes för siffrorna ovan.

## 15 Mappstruktur

```
riskanalys/                     (repot)
  AGENTS.md, CLAUDE.md          gemensamma regler för Codex och Claude
  pyproject.toml
  regelbas/                     granskade och versionerade data
    kallor/  krav/  kataloger/  referensdata/  regelpaket/  beslutstabeller/
  src/riskanalys/
    regelverk/       källor, krav, kataloger, regelpaket, giltighet, villkorsformat, paragrafkarta, validering
    profil/          intag, belägg, bekräftelse
    bedomning/       beslutstabeller, risknivåer, regelspår, kundmodellens spår
    dokument/        avsnittsunderlag, tillåtelselistor, AI-klient, testleverantör, rendering
    granskning/      täckning, spårbarhet, bristmönster, fynd
    faststallelse/   status, sakgranskning, avvikelser, godkännande, låsning
    lagring/         datamapp, manifest, kontrollsummor, verifiering
    drift/           versionshistorik, utvärderingsdatum, ändringskontroll
    cli.py
  mallar/                       Word-mallar
  tester/
    enhet/  regelkontrakt/  typfall/
  docs/
```

Byrådata ligger i `$RISKANALYS_DATA`, aldrig i repot (avsnitt 5.2).

## 16 Kvalitetssäkring

| Test eller kontroll | Vad det visar |
|---|---|
| Regelbasvalidering | Unika ID:n, inga brutna referenser, giltiga villkor, varje krav har källa, varje tjänst har hot |
| Paragrafkarta (sakkunnig) | Att inget krav saknas (16.1) |
| Regelkontrakt | Ett test per beslutstabellrad plus gränsfall och okända uppgifter |
| Datumgränser | Rätt lydelser väljs dagen före och samma dag som varje ikraftträdande och upphörande (6.4) |
| Spårberoenden | Varje uttryckligt beroende mellan kundmodellens spår (7.6) har eget test |
| Typfall | Hela kedjan med syntetiska profiler ger förväntade nivåer, fynd och status |
| AI-validering | Valideringen fångar påhittade ID:n, siffror, nivåer och personnamn (med testleverantör) |
| AI-utvärdering | Sakfel, ogrundade påståenden, granskningstid och kostnad per godkänt avsnitt (live, frivilligt, M3) |
| Verifiering och återställningsprov | Ett fastställt paket verifieras mot sitt manifest och återställs från säkerhetskopia på en tom installation |
| Tillsynsfall före verklig användning (M3–M5) | Syntetiska negativa fall härledda från besluten 6045-2026 och 6572-2026 ska ge förklarade fynd inom prövad omfattning. Se 16.3. |
| Utvidgad facitjämförelse (M7) | Tidigare underkända dokument ska underkännas inom respektive omfattning. Ett genomarbetat referensutkast ska i stort godkännas. Återanvänder fallen i 16.3. |
| **Acceptansprov före verklig användning** | Se 16.2 |

**Syntetiska uppgifter används tills regelbasen är sakkunniggranskad.** Ingen riktig byrå får ett fastställt paket innan dess.

### 16.1 Paragrafkarta

Tester hittar fel i regler som finns, men inte ett krav som aldrig lades in. Därför har varje regelpaket en **paragrafkarta**: varje paragraf i de relevanta kapitlen av lag och föreskrift, för angivet datum och län, med antingen de krav-ID:n den ger upphov till eller "ej tillämplig för sektorn" med motivering. Kartan granskas och signeras av sakkunnig per version av regelpaketet. Programmet kontrollerar att kartan är fullständig mot källans paragrafindelning.

M2 inventerar hela PTL (även 4 a och 7 a kap.) och hela den valda länsföreskriften. Även registrering hos Bolagsverket enligt PTL 7 kap. 3 § och anmälan av ledningsförändringar enligt 7 kap. 6 § ingår. Definitioner, tillsynsregler och bemyndiganden får en redovisad hantering eller sektormotivering; de får inte bara utelämnas. Övergångsbestämmelser ingår i en separat kontroll av giltighet. Registreringskravens regeldata förbereds i M2; användarflödet och faktisk drift prövas i M4 före M5. En granskning av enbart allmän riskbedömning kontrollerar dokumentets krav, medan den juridiska fullständighetskontrollen fortfarande omfattar hela paketet.

### 16.2 Acceptansprov

Före första användning hos en riktig byrå går en **oberoende sakkunnig** och en **tänkt användare** igenom flera byråprofiler, däribland:

- ett fall med saknade uppgifter,
- en liten tjänst med hög risk,
- brister av den typ som syns i publicerade tillsynsbeslut.

Resultatet jämförs med manuellt arbete:

- Vilka fakta saknas?
- Vilka slutsatser går inte att förklara?
- Vilka påståenden saknar stöd?
- Hur lång tid tar sakgranskningen?

Först därefter går det att säga om upplägget ger bättre resultat än dagens arbetssätt.

### 16.3 Granskningsfall från verklig tillsyn

[Research 09](../../research/09-tillsynsbeslut-2026.md#bevarat-underlag-och-återanvändbara-granskningsfall) beskriver bevarade original, OCR och sidkarta utanför repot. [tillsyn-2026.json](../../research/typfall/tillsyn-2026.json) innehåller två nyskrivna syntetiska negativa fall, 17 förväntade fynd och fem kontrollvarianter. Det är ett **facitutkast, inte juridiskt validerat**, och ingen produktutvärdering är ännu genomförd med fallen.

- M2: en oberoende sakkunnig bekräftar eller reviderar facitversionen mot beslut och relevanta krav. Besluten används som tillsynspraxis, inte som universella risknivåer eller en formel för sanktionsavgifter. Facitets 22 fynd/varianter granskas separat från regelpaketens rättsliga objekt, med egen version och innehållssumma. `docs/research/typfall/tillsyn-2026.json` är kanonisk; regelbasens referensfil länkar dit. En facitrevision upphäver endast facitattesten. Granskarens identitet och kompetens sparas i lokala attestfiler utanför offentligt Git. M3 måste verifiera facitbeslutet mot exakt facitversion före utvärdering.
- M3: granskaren och det mänskliga sakgranskningsflödet ska hitta och förklara alla obligatoriska fynd inom allmän riskbedömning. Saknade fakta får inte fyllas i av AI. Längre språk, högre risknivåer och ett äldre uppgivet utvärderingsdatum får inte ensamma undanröja bristerna. Åtgärdade fynd ska inte fortsätta rapporteras. Missade och ogrundade fynd redovisas i valideringsrapporten och hanteras före M5.
- M4–M5: pröva att intaget samlar in omfattning per tjänst, kundtyp, kanal och relevant geografi, med period, nämnare, källa och uppgiftsstatus. Fynd inom rutiner prövas när befintliga rutiner ses över; de får inte poängsättas som om de ingick i en granskning av enbart allmän riskbedömning.
- M7: utvidgad provtillsyn av hela dokumentpaketet. Den ersätter inte prövningen av allmän riskbedömning före första riktiga byrå.

Ett bristmönster i katalogen räknas inte som upptäckt förrän en granskningskontroll och ett test visar att programmet hittar det. `automatiserad: false` betyder manuell kontroll. Spårningen per bristmönster, med vad M0–M1 täcker och vilken etapp som ansvarar för resten, står i implementeringsplanen för M0–M1 och förs vidare i planerna för senare etapper.

Om AI används som granskare ska alla tre körningar per oförändrat fall och konfiguration klara de obligatoriska kriterierna. Modell, effort, promptsumma, svar, kostnad och mänsklig bedömning sparas. Separata senare fall hålls utanför promptjusteringen. Ett matchande B-ID eller ett generellt påstående om brister räcker inte som godkänt resultat. Råhandlingar och OCR skickas inte till AI; de syntetiska testindata används. Källhänvisningar kontrolleras lokalt mot originalfotona.

## 17 Personuppgifter och säkerhet

Fas 1 behandlar inga kundärenden. Viss behandling av personuppgifter är ändå nödvändig, eftersom föreskrifterna kräver att det framgår vem som har funktionerna (LSF 6 kap. 3–4 §§) och att utbildning dokumenteras med deltagarnas namn (LSF 2 kap. 11 §). Även företagsanknutna kontaktuppgifter och uppgifter om enskilda näringsidkare kan vara personuppgifter. Uppgifter är anonyma först när ingen person kan identifieras, varken direkt eller indirekt (IMY).

| Kategori | Exempel | Tillåtet i fas 1 | I AI-underlag |
|---|---|---|---|
| Funktionsinnehavare och beslutsfattare | Namn och roll för FfR, VD, styrelse | Ja | Nej. Ersätts med rollplatshållare. |
| Anställda i utbildnings- och lämplighetslogg | Namn, datum, utbildningsinnehåll | Ja | Nej |
| Byråns kontaktuppgifter | Företagsanknuten e-post och telefon | Ja | Nej |
| Byrå som är enskild näringsidkare | Organisationsnummer som är personnummer | Ja | Nej. Ersätts med platshållare. |
| Aggregerad kundstatistik | Antal och andelar per kategori | Ja | Bara fält på tillåtelselistan. Små grupper (under 5 kunder, metodval) skickas som "färre än 5" och bedöms särskilt, eftersom en liten grupp kan peka ut en person. |
| Kunder, verkliga huvudmän, enskilda kundärenden | – | **Nej** | Nej |
| Importerade byrådokument | Riktlinjer, årsredovisning | Bara efter maskning av personuppgifter | Nej i fas 1 |

Övrigt:

- Varje AI-anrop byggs enbart ur avsnittstypens tillåtelselista (8.2). Listan är versionerad och granskningsbar.
- Profiluppgifter har fältet `personuppgift`. Sådana uppgifter finns aldrig på en tillåtelselista.
- Valideringen av AI-svar söker efter personnamn som finns i profilen.
- Batch-API används inte som standard (8.3).
- Byrådata lagras i datamappen utanför repot, med filbehörighet bara för användaren.
- Gallring följer penningtvättslagens bevarandetider där de gäller (fem år, högst tio). Verksamhetsutövaren ansvarar för rättslig grund och information till de registrerade.
- API-nycklar läses från miljövariabler, aldrig från kod eller filer i repot.
- Fas 2 med kundärenden kräver en egen spec med kryptering, behörighetsstyrning och EU-hostad databehandling.

## 18 Etapper

| Etapp | Innehåll | Klart när |
|---|---|---|
| **M0 Grund** | Repo, `AGENTS.md`/`CLAUDE.md`, datamapp, lagring och manifest, villkorsformat och utvärderare, scheman, regelbasvalidering, testleverantör för AI, bristmönsterkatalogen v0 flyttad till regelbasen | `riskanalys regelbas validera` är grön, och villkorsutvärderaren har fullständiga regelkontrakt |
| **M1 Tunn kedja** | Hela flödet för en tjänst med syntetiska data: ett litet kravpaket (allmän riskbedömning, LSF 2 kap. 1–3 §§) → bekräftad syntetisk testprofil → bedömning av löpande bokföring → spårbart AI-utkast (testleverantör) → maskinell granskning → sakgranskning → fastställd testexport med låst paket, versionshistorik och datum för nästa genomgång | Kedjan körs i ett typfallstest, och `riskanalys verifiera` godkänner paketet |
| **M2 Regelbas v1 och juridisk granskning** | Alla krav, kataloger och beslutstabeller för redovisningsbyråer. Paragrafkarta. Kundmodellens fyra spår. Sakkunniggranskning per beslutsgren. | Alla tillämpliga krav och paragrafkartan har status *verifierad* |
| **M3 Modellvalidering och AI-utvärdering** | Metodbilaga, valideringsrapport, avvikelselogg, typfall (bland annat saknade uppgifter och liten högrisktjänst), prövning av 20 %-gränsen, AI-utvärdering med riktiga skrivuppgifter och sakkunnigbekräftade tillsynsfall inom allmän riskbedömning (16.3) | Valideringsrapport klar, tillsynsfall och kontrollvarianter ger förväntade fynd och kvarstående avvikelser är hanterade. Beslut om modell och effort fattat utifrån mätning. |
| **M4 Användningsprov och minsta drift** | Enkelt lokalt formulär för intag och sakgranskning, ändringskontroll, versionshistorik, återställningsprov, acceptansprov (16.2) | Acceptansprovet är genomfört och dokumenterat |
| **M5 Första riktiga byrå: endast allmän riskbedömning** | Del-leverans. Full allmän riskbedömning för en riktig byrå, fastställd av byrån och märkt "endast allmän riskbedömning". Byråns **befintliga rutiner och riktlinjer ses över mot den nya bedömningen**. Avvikelser förs till åtgärdslistan med ansvarig och datum, eftersom rutinerna ska bygga på riskbedömningen och vara verksamhetsanpassade. | Riskbedömningen är fastställd av byrån och verifierad, och genomgången av befintliga rutiner är dokumenterad |
| M6 Övriga dokument | Rutiner (med modellriskhantering), kundmodell, instruktioner, kravmatris, tillsynspaket. Ersätter de befintliga rutiner som granskades i M5. | Alla dokument i avsnitt 11 genereras |
| M7 Provtillsyn och facit | AI-provtillsyn och facitjämförelse | Facitfallen ger förväntat utfall |
| M8 Full drift | Påminnelser, utlösande händelser från referensdata, belägg | Ändrad högrisklista ger korrekt flaggning |
| M9 Kundnivå | Egen spec | – |
| M10 Fler sektorer | Ett sektorspaket per sektor | – |

**Parallellt spår: AMLR.** Startar samtidigt med M2. AMLR:s artiklar och bilagor kartläggs mot kravregistret, och ett eget regelpaket med tillämpningsdatum 2027-07-10 byggs och testas vid sidan av dagens paket. M2 levererar kravkarta och ett separat utkastpaket. Ett utkast kan inte väljas operativt, även om användaren anger ett senare datum. Spåret följer promemorian *EU:s penningtvättspaket* (Fi2026/01654) och AMLA:s slutliga riktlinjer; lagförslag och riktlinjeutkast blir inte bindande genom att datumet passerar. Hela spåret är klart när AMLR-paketet och de svenska kompletteringarna är sakkunniggranskade före 2027-07-10.

M1 bevisar att arkitekturen håller innan arbetet läggs på hela regelbasen. M2–M4 ser till att metoden är juridiskt granskad, validerad och användbar innan en riktig byrå fastställer något.

## 19 Risker

| Risk | Hantering |
|---|---|
| Regelbasen tolkar lagen fel | Sakkunniggranskning per beslutsgren, källa per post, regelkontrakt |
| Ett krav saknas helt i regelbasen | Paragrafkarta granskad av sakkunnig |
| Juridiska beslutsgrenar blandas ihop | Kundmodellens fyra spår med uttryckliga och testade beroenden |
| Fel lydelse används för ett datum | Giltighet per paragraflydelse, Regeringskansliets rättsdatabaser som primärkälla, tester på båda sidor om datumgränser |
| Riskbedömningen fastställs innan rutinerna anpassats | M5 märks "endast allmän riskbedömning" och kräver dokumenterad genomgång av befintliga rutiner |
| AI hittar på fakta | Låst schema, tillåtelselista, maskinell validering |
| AI-text stämmer formellt men inte i sak | Sakgranskning per avsnitt före fastställelse |
| Saknade uppgifter ser ut som säkra slutsatser | Preliminär status som blockerar fastställelse |
| En liten högrisktjänst döljs i sammanvägningen | Egen redovisning och egna slutsatser för varje tjänst med hög risk |
| Generisk text slinker igenom | Bristmönster B-02 och provtillsyn |
| Personuppgifter sprids | Kategorier, tillåtelselistor, rollplatshållare, ingen batch som standard, datamapp utanför repot |
| Underlag går förlorat | Fristående låsta paket, säkerhetskopia, återställningsprov |
| Resultatet uppfattas som certifiering | "Fastställt av byrån", aldrig "uppfyller regelverket" |
| Regelverket ändras (AMLR, ny svensk lag) | Parallellt AMLR-spår, versionerade regelpaket med giltighetsdatum |
| Dokumenten blir för långa att följa | Proportionalitetsnivå och arbetsinstruktioner per roll |
| Föråldrad referensdata | Datum och kontrollsumma per lista, påminnelser |

## 20 Öppna frågor

1. Skånes föreskrifter har jämförts maskinellt med Stockholms och Västra Götalands (research 10). Tabell 1 i 3 kap. 4 § har även jämförts visuellt på PDF-sidorna 5–6 utan observerade skillnader i kontroll- eller dokumentationskraven. Sakkunnigs juridiska bedömning återstår.
2. AMLA:s konsultation om verksamhetsomfattande riskbedömning är stängd. På den kontrollerade konsultationssidan finns ännu inget slutligt resultat (2026-10-10, research 10). Publiceringsläget kontrolleras på nytt före användning. Till dess märks allt som bygger på utkastet som *EU-utkast* eller *metodval*.
3. De svenska kompletterande reglerna: promemorian *EU:s penningtvättspaket* (Fi2026/01654), publicerad 2026-07-06, är på remiss med svar senast 2026-10-30. Någon proposition har ännu inte setts.
6. Ändringen av PTL 1 kap. 2 § 2026-11-20 har jämförts: punkterna 19, 20 och 23 är oförändrade (research 10). Båda lydelserna och testerna runt datumgränsen ska införas i M2; sakkunnig verifierar tillämpligheten.
4. Om Bolagsverket erbjuder elektronisk åtkomst till registret över verkliga huvudmän (påverkar fas 2).
5. Vem som gör sakkunniggranskningen av regelbasen och acceptansprovet.
7. Grundnivåerna i tjänstekatalogen ska kalibreras mot sektorsrisken. Den nationella riskbedömningen 2024/2025 kallar risken för bokförings- och revisionstjänster hög ([research 09](../../research/09-tillsynsbeslut-2026.md)). Regelbas v1 ska också ha bolagsbildning och skatterådgivning i tjänstekatalogen och omfattning per tjänst i profilen.

## 21 Definitioner

| Begrepp | Betydelse här |
|---|---|
| Fastställt av byrån | Byråns behöriga organ har beslutat om dokumentet. Ingen certifiering. |
| Preliminär | Resultatet bygger på minst en uppgift som inte är bekräftad |
| Metodval | En regel som byrån eller programmet valt, inte ett lagkrav |
| Metodavvikelse | Ett motiverat beslut att avvika från ett metodval i ett enskilt fall |
| Sakgranskning | En människas granskning av att text stämmer med fakta och källa |
| Paragrafkarta | Förteckning över varje relevant paragraf och hur den hanterats i regelbasen |
| Lydelse | En version av en paragraf med eget datum för ikraftträdande och upphörande |

## 22 Ändringslogg

| Revision | Datum | Ändring |
|---|---|---|
| 1 | 2026-10-08 | Första förslaget |
| 2 | 2026-10-08 | Efter första granskningen (Codex): bristmönstrens ID:n samordnade, kategorier för personuppgifter, dokumentstatus och grindar, typat villkorsformat, manifest med kontrollsummor, mänsklig sakgranskning, datamapp utanför repot, modulerna `faststallelse/` och `lagring/`, M1 som tunn kedja |
| 3 | 2026-10-08 | Efter andra granskningen (Codex): (1) kundmodellen delad i fyra spår (förbud och stopp, obligatoriska åtgärder, riskklassning, rapportering) med sakkunniggranskning per beslutsgren; (2) modellriskhantering enligt PTL 6 kap. 1 § andra stycket; (3) minsta drift flyttad före första riktiga fastställelse; (4) okänd uppgift ger preliminärt resultat, och små högrisktjänster döljs inte i sammanvägningen; (5) paragrafkarta för fullständighet och promemorian Fi2026/01654; (6) AI-modell och effort som inställningar som avgörs genom utvärdering, och testleverantör i automatiska tester; (7) tillåtelselistor för AI-underlag, små grupper och ingen batch som standard; (8) löftet om återskapande ersatt med bevarande, säkerhetskopia och återställningsprov. Dessutom: grind som skiljer metodavvikelser från lagkrav, "fastställt av byrån", användarflöde, acceptansprov, ny etappordning och AMLR som parallellt spår. |
| 4 | 2026-10-08 | Efter tredje granskningen (Codex): (1) kundmodellens spår har uttryckliga beroenden enligt PTL 3 kap. 1, 14–16 §§, och rapportering prövas fristående; (2) datumstyrning per paragraflydelse med Regeringskansliets rättsdatabaser som primärkälla och tester på båda sidor om datumgränser (exempel: 1 kap. 2 § ny lydelse 2026-11-20); (3) M5 märkt "endast allmän riskbedömning" med genomgång av befintliga rutiner; (4) egen rad i fastställelsegrinden för allmänna råd, tillsynspraxis och EU-utkast; (5) datum för Fi2026/01654 rättat till 2026-07-06 och remissen beskriven som pågående. |
| 5 | 2026-10-08 | Efter fjärde granskningen (Codex, av implementeringsplanen): kravet har `lydelser` (lista) i stället för `lydelse`, så att ett krav kan följa sin paragraf genom flera lydelser (6.4). Övriga fynd gällde planen och är rättade där: nästa genomgång räknas bara från utvärderingar, lydelser har `text_kontrollsumma` med sparad paragraftext, krav har `galler_om` och `belagg`, varje AI-försök sparas löpande med faktisk svarsmodell, och nivåer i AI-text binds till sin risktyp. |
| 6 | 2026-10-09 | Efter femte granskningen (Codex, av implementeringsplanen): sakkunnigstatus *verifierad* binds till en kontrollsumma av det granskade innehållet, för både krav och paragrafkarta (6.2 och 16.1). Övriga fynd gällde planen och är rättade där: paragrafkartan har en rad per paragraf och kontrolleras mot källans paragrafindelning, beslutsdatum får inte ligga före granskning, sakgranskning, utvärdering eller tidigare fastställelse, ett fastställt paket publiceras med ett enda namnbyte, och export, sakgranskning och fastställelse kontrollerar manifesten för allt de läser. Öppen fråga 7 om kalibrering mot sektorsrisken, efter två fullständiga tillsynsbeslut (research 09). |
| 7 | 2026-10-09 | På användarens begäran: tillsynsmaterialet bevarat lokalt utanför repot med OCR och kontrollsummor. Två syntetiska granskningsfall med 17 förväntade fynd och fem kontrollvarianter kopplade till originalens sidor. Avsnitt 16.3 kräver prövning av allmän riskbedömning i M3 före M5; utvidgad facitjämförelse kvarstår i M7. Facit väntar på sakkunniggranskning. |
| 8 | 2026-10-09 | Efter Codex negativa prov av planens kodblock: sakkunnigstatus binds också till refererade lydelser, källans giltighetsuppgifter och fälten i `galler_om` (6.2 och 16.1); sakgranskningen gäller avsnittet med insatta namn, exakt som det exporteras (10); tidigare fastställda paket verifieras mot manifest innan de används (5.3). 16.3 anger att ett bristmönster räknas som upptäckt först med granskningskontroll och test. |
| 9 | 2026-10-09 | Efter Codex granskning av rättningarna: ett saknat eller skadat manifest rapporteras som en avvikelse med instruktion om återställning, aldrig som en krasch (5.3). |
| 10 | 2026-10-10 | Efter granskning av M2-underlaget: rapporteringsundantaget i PTL 4 kap. 8 § och separata undantagsprövningar i kundmodellen; rättslig avgränsning av punkt 23; full PTL-inventering inklusive 7 kap.; korrekt beslutsdatum för 14FS; alternativ lydelse per län med bevarad huvudkälla; AMLR som separat utkastpaket utan operativt urval. M2-plan tillagd. Alla juridiska slutsatser väntar på sakkunniggranskning. |
| 11 | 2026-10-10 | På användarens förtydligande: komplett intag från tom profil, villkorade följdfrågor, täckningskarta för krav och beskrivande underlag, kontroll av motsägelser/aktualitet samt skrivning av hela riskbedömningen. Frågekontrakt prövas i M3; sammanhållet lokalt flöde i M4 före första riktiga byrå. Befintlig riskbedömning behövs inte för att börja. |
| 12 | 2026-10-10 | Lokalt intag och hela Word-utkastet implementerat före resterande M4. Fråge-/kravkopplingar i regelbas 1.1.0, lokala beskrivningar, faktabaserat intag utan krav på att användaren skriver analysen, explicit utvärdering och bevarade granskningsgrindar. M3/M4:s verksamhetsprov återstår. |
| 13 | 2026-10-10 | SCB AFR-registerhämtning och lokal JSON-import som källbundna förslag i intaget (§14.4). Särskild bekräftelse, identitetskontroll, privata snapshots och bevarad faktisk verksamhetsintervju. Ingen ny AI-tillåtelse eller juridisk attest. |
| 14 | 2026-10-10 | Efter Claude-granskning: XML-kontroll före AI, engångsskrivning, gemensam CLI/webb med CAS, egen filialkälla, bevarande av registerbild vid senare hämtning, historiska belägg vid okänt, skilda felvägar och explicit korrigeringspolicy för län/regelpaket. Utvidgad datakällsresearch finns i research 10, avsnitt 14.2. |
| 15 | 2026-10-11 | Samlat källbundet registergodkännande och tjänsteutbud, obligatoriskt fälturval och atomiska batchar, redigerbara rollförslag, sessionsnyckel, SCB-status som versionshanterad bakgrund och request-lokal rendering. Ny källkontroll i research 10 §14.3. Exportpilot för pilotbyrån krävs fortfarande före ny CSV/XLSX-import. |
| 16 | 2026-10-11 | Avgränsat val av egen kännedom och aktuella tidigare underlag med kategori-/periodkontroll, föreslagen statistikperiod, tydlig faktisk Word-leverans och SCB-schema 3 med villkorat koncernförslag för kod 41. Fler källor och ännu ej integrerade riskrapporter inventeras i research 10 §14.4; inga nya externa anslutningar eller juridiska attester. |
| 17 | 2026-10-11 | Efter Claudes provkörning med riktig AI och researchrapporten om promptdesign: AI skriver den analyserande texten i alla analysdelar från ett faktablad, medan koden äger tal, nivåer, obligatoriska meningar, låsta stycken, datum och format (8.4). Gemensam systemprompt med regler och skäl, preliminärt ett anrop per analysdel med ett anrop per tjänst som jämförelse, schema med `enum`-referenser, platshållare med stoppregler, högst två omförsök följt av mall och fynd, gräns mellan maskinell validering och sakgranskning, faktablad med sluten källtyp och oförändrat smågruppsskydd, ersättningskontrakt för granskningsgrinden och utvärdering i tre lager före val av modell och design. Kryssfrågor med frivillig lokal komplettering ersätter merparten av fritexten i intaget, utan att tjänstefakta ärvs från byrån (14.5). AMLR märkt som framtida regelverk. Ingen juridisk attest och ingen ändring av riskmetoden. |
| 18 | 2026-10-12 | Efter pilot på tre tjänster: låsta stycken i klartext med kortnamn i regelbasen, villkor i ord, faktorer under metodens gräns beskrivs som förekommande, sektorsreferens med källans titel och spårbarhet via referenser och bilaga B1. Format `D-ARB-tjanst-v4` med ny sakgranskning; fastställda paket oförändrade (8.4.9). Inga ändrade regler, gränser eller nivåer. |
| 19 | 2026-10-13 | Efter granskning med syntetiska data: AI-begäran beror bara på det AI får se – inga nivåer, regelspår eller nivåmeningar till AI, utfallet ”prövas lokalt” för sårbarheter som bygger på uppgifter utanför tillåtelselistan eller smågruppsskyddade värden, kontrollernas kategorifält i tillåtelselistan och den äldre skrivvägen stängd för riktiga AI-anrop (8.4.10). Andelar nära 0 och 100 % visas konsekvent, katalogkoder och kontrollsummor flyttas till referenser och bilaga B1, och fastställelse kräver aktuellt format i varje tjänsteavsnitt (8.4.9). Inga ändrade regler, gränser eller nivåer. |
| 20 | 2026-10-14 | Efter granskning: personnamn prövas bara lokalt efter tjänstens alla AI-anrop, och en del med namn ersätts av mallen (8.4.10 punkt 7). Smågruppsskyddade värden visas för AI med en gemensam text (8.4.10 punkt 8). Andelar nära metodens gränser visas med tillräcklig precision (8.4.9 punkt 10). Inga ändrade regler, gränser eller nivåer. |
| 21 | 2026-10-14 | Efter granskning: hela namn och genitiv i uttryckliga namnfält, inga kedjade fria AI-svar, lokala namnstopp redovisas separat från godkända förstaförsök. Härledda AI-andelar maskeras om antal eller bas saknar tillåtelse; lokal precision och decimalgränser bevaras även i intaget. |
| 22 | 2026-10-14 | Efter beslut: kedjan mellan analysdelarna återställs med ett avgränsat beslut (8.4.10 punkt 9). Tillåtna kundandelar visas åter för AI, med begränsad precision när antal eller bas inte är tillåtna, och ett prov redovisar vilka antal som går att härleda (8.4.9 punkt 11). Namnfält anges med egenskapen `namnfalt` i regelbasen. Inga ändrade regler, gränser eller nivåer. |
| 23 | 2026-10-14 | Användargodkänd första Bolagsverket HVD-läsväg (14.4): lokal nyckelfil, token i minnet och kommandot bolagsverket för registerbild och årsredovisningslista. Verifierat myndighetskontrakt. Ingen automatisk profilöverföring, AI-användning eller ändring av riskmetod. |
| 24 | 2026-10-14 | Användargodkänd samlad SCB/Bolagsverket-hämtning och intagsbekräftelse, schema 4, privat ZIP/iXBRL-läsning, redigerbart verksamhetsutkast och omsättning med periodgrind i båda svarsriktningarna. Begränsat taxonomistöd, inga nya riskregler eller AI-data. |
| 25 | 2026-10-14 | Planerad H6: typade lokala tabeller, läsbara utfalls-/källförklaringar och tvåfilsrapport under samma sakgranskning. Separat beslutsspår för riskmetod; ingen implementation eller ändrad riskregel. |
| 26 | 2026-10-14 | H6-plan reviderad efter granskning: en Word-fil, AI-budget 400–750 ord per tjänst, kvalitativ syntes i befintlig riskdel och lokal beräkningstabell. Kontrollpunkt för befintliga ändringar. Ej implementerat. |
| 27 | 2026-10-14 | H6-v5 implementerat: typade tabeller, lokala beräkningsförklaringar, källregister, kortare skrivkontrakt och enfilsrapport. Mätt längd överskrider målet; synlig varning utan trunkering. Oförändrad riskmetod. |
| 28 | 2026-10-15 | Oberoende H6-granskning: kontrolltabellen visar nekad metodverkan/saknade belägg; risköversikten markerar preliminär status och okänt erbjudande utan ändrade motorutfall. Användaren valde A + B för en senare revision: källbunden kontrollräckvidd och lokal verksamhetsgranskning. Ingen sådan ny modell eller motorändring är implementerad. |
| 29 | 2026-10-15 | Planerat A + B-kontrakt preciserat: beskrivande kontrollräckvidd, privat analysmodell, frågor per tjänst, underlags-/svarsbindning och separata lokala analys- och dokumentgodkännanden. Nästa dokumentformat v6 skiljs från skrivresultatets v5. Ändringsmatris och sex genomförandeuppgifter tillagda i befintlig D-ARB-plan. Endast dokumentation; ingen implementation, ny sakkunnigattest eller push. |
| 30 | 2026-10-15 | Användaren beställde källgranskningens fem kompletteringar i A + B-planen: tjänstevis sårbarhetsprövning, faktorernas samverkan, konkret rutinlänk, egna lärdomar och separata datum samt blockerande prövning av om redovisad reduktion har stöd. Modeller/frågor/acceptansprov preciserade; ingen ändrad motor, AI-gräns eller implementation. |
| 31 | 2026-10-15 | A + B omskriven med sex ytterligare kompletteringar: tjänstedetalj/delanalyser, betalningsinsyn, uppdragshanterbarhet, leverantörsprövning, plattforms-/PSP-prov och löpande modellriskhantering. Modeller, frågor, bindningar och prov synkroniserade; AB7 preciserar §7.8 före slutlig attest. Tidigare fem krav bevaras. Inga nya numeriska riskregler, automatiska kundbeslut eller kodändringar. |
| 32 | 2026-10-15 | Avgränsning efter Claudes granskning: förifyllda utkast/delade scenarier och räknad arbetsbörda, endast två AI-delar i v6 med omräknad ordbudget, två separata leveranssteg, synlig egen granskning, M1 vid metodverifieringen samt motor-/regelbasbunden identitet med miljöuppgifter separat och projektlevererad valideringsrapport. Endast plan/spec/STATUS, ingen implementation eller commit. |
| 33 | 2026-10-15 | A+B:s programstöd byggt med subagenter: beskrivande regelbas 1.5.0, privat revisionsskyddad analys, typad CLI/webbguide, v6 med två AI-delar och lokal motivering samt frysta modell-/analysunderlag och separata attester. Uppgiftsgranskning och slutverifiering pågår; ingen verklig expertattest, numerisk motorändring, commit eller push. |
| 34 | 2026-10-17 | A+B slutfört tekniskt efter Claudes och Codex granskningar. V6 har åter de låsta styckena om egen rapportering och geografi (8.4.6) med B-09, B-10 och B-15, omfattningens motivering efter storlek och art samt D-ARB.9 om följder för rutiner, kundkännedom, övervakning och utbildning, byggt ur den godkända lokala analysen. AI-delarna i v6 prövas lokalt mot exakt de låsta v6-styckena efter alla anrop, så att begäran och omförsök inte påverkas (8.4.10 punkt 1 och 7); en del som återger ett låst stycke blir mall med blockerande fynd. Stöd för ett analysgodkännande får inte vara daterat efter godkännandet; uppföljningsfrister får ligga i framtiden och ett underkännande får dokumentera felet. B1:s delrubriker ingår i dokumentmodellen och sakgranskningen. Längdkontrakt enligt användarens beslut: realistiskt läsprov 3 500–5 000 huvudord med 4 700 som riktbudget, AI-maxprov med synlig längdvarning och bevarad analys, ingen trunkering. Ingen ändring av motor, regelvillkor, tillåtelselista eller sakkunnigstatus. |
| 35 | 2026-10-17 | Användaren godkände riktningen i research 11 §10.8: nivåmotivering i huvudtexten före mer AI-text, lokala utfall för skyddade faktorer, rättad sanktionsbetydelse, mindre upprepad programtext, tjänstefördelning av byråövergripande faktorer, fasta verksamhetsval och ett sammanhängande AI-stycke per tjänst i skrivformat v7. Motorns beräkning oförändrad; M1-förslaget läggs i sakkunnigens beslutsunderlag. |

### D-ARB-format efter källkontroll 2026-10-11

Godkänd H5-plan: `docs/superpowers/plans/2026-10-11-d-arb-tjanststruktur.md`. Kontroller/effekt (`D-ARB.7`) står före tjänsteanalysen. Varje `D-ARB.6.n` innehåller beskrivning/omfattning, hot/egen erfarenhet, sårbarheter med underlagsmotivering, kontroller/effekt, motiverade nivåer och slutsatser. `D-ARB.11` anger byråns utförda bevakning; `D-ARB.B1` samlar frågesvar, belägg, perioder, nämnare och källversioner. Bilagan ingår i sakgranskning. Underrubriker, dokumenttitel och disposition binds till sakgodkännandet; historiskt format utan underrubriker kan fortfarande läsas.

Kontrollernas genomförande är skilt från verkan: aktuell bekräftad effekt och belagt utfall med samma period behövs för metodens riskreduktion. Utfallstext stannar lokalt. Noll avvikelser bevisar inte effekt; ett steg om minst en kontroll är verksam förblir ogranskad metod. B-09/B-10/B-15 kontrollerar maskinellt underlag och att deterministisk analys finns i tjänsteavsnittet, men bedömer inte om fri text juridiskt eller sakligt är tillräcklig. Nya indikatorer viktas konservativt per tjänst och kräver sakkunniggranskning samt M3-kalibrering.


### H6 – dokumentpresentation och separat metodprövning

Fortsättningen H6 finns i [den befintliga D-ARB-planen](../plans/2026-10-11-d-arb-tjanststruktur.md#h6--kortare-rapport-med-tabeller-och-separat-metodspår-2026-10-14). Presentationsdelen är implementerad i v5; redaktionellt längdmål och sakkunnig metodprövning återstår. Huvudrapporten ska innehålla typade tjänste-, kontroll-, risk- och åtgärdstabeller, läsbara källhänvisningar, innehållsförteckning och lokala förklaringar av sparade motorutfall. Gemensamma kontrollbeskrivningar återges en gång. Visningsnummer hålls åtskilda från stabila ID:n. Underlagsbilagan renderas efter sidbrytning i samma Word-fil och behålls i samma sakgranskning och verifierbara exportpaket. Ändrad cell, hänvisning, ordning eller bilaga ogiltigförklarar tidigare sakgodkännande; äldre format och paket behåller sina summor. Formatet är D-ARB-tjanst-v5. Historiska format förblir läsbara med sina gamla kontrollsummor.

Risknivåer, regler, tillåtelselista och AI-schema är oförändrade i denna leverans. Sakkunnigstatus får inte höjas. M1–M4 i planens separata beslutsspår avser kontrolltäckning, TF-metod, exponeringens omfattning och faktorernas summering/dubbelräkning; de är öppna metodfrågor, inte beslutade regeländringar. En kortare huvudrapport är ett redaktionellt mål utan minskad kravtäckning.

H6-revidering: AI-delarnas införda max är 160/220/120/120/130 ord, totalt 750 per tjänst. Fem anrop och schema behålls, men `risknivaer` begränsas till kvalitativ syntes under Scenarier och osäkerheter. Den lokala tabellen ensam förklarar beräkningen. Promptidentitet och längdvalidering är uppdaterade; äldre skrivförsök kan läsas men kräver omskrivning för ny v5-sammansättning. Huvudrapportens budget för fyra tjänster är 3 000 AI-ord plus 2 000 ord lokalt innehåll, prövad även vid maxlängd.

H6 mätutfall 2026-10-14: fyrtjänstprovet ger 6 096 ord huvudtext, 5 078 ord B1 och tio tabeller; 1 750 ord kommer från manuellt förberedda skrivsvar. Maxprovet med 3 000 AI-ord ger 7 346 ord huvudtext. Budgeten 2 000 lokala ord är därmed **inte uppnådd** (4 346 i exemplet), och v5 visar en redaktionell längdvarning över 5 000 ord utan trunkering eller ny fastställelsespärr. `dokumentord` räknar modellens synliga rubriker, numrering, celler och text efter substitution; upprepad navigering, sidhuvuden och den exporterade fyndlistan räknas inte dubbelt. Exportmanifestet sparar huvudtext/bilaga/totalt. Regelbas, motor, tillåtelselista och sakkunnigstatus är oförändrade.

H6-slutgranskning 2026-10-15: tabeller ska skilja kategorin uppgiven effekt från motorns beläggsprövning. Kontrolltabellen visar därför om riskreducerande verkan godtas enligt dagens metodvillkor, samt vilka aktuella kontrollbelägg som saknas. Detta styrker inte scenariotäckning. Risköversikten markerar preliminär bedömning och okänt tjänsteerbjudande i raden; sparade nivåer byts inte ut. Dessa presentationsrättningar omfattas av befintlig v5-sakgranskning och gör tidigare sakgodkännanden av ändrade avsnitt ogiltiga. Historiska exporter skrivs inte om.

### A + B – kontrakt och genomförande efter H6

**Programstödet är byggt; samlad slutverifiering och artefaktprov pågår.** Detaljerade modeller, frågor, ogiltigförklarande och acceptansprov finns i [D-ARB-planens A + B-avsnitt](../plans/2026-10-11-d-arb-tjanststruktur.md#a--b--konkret-kontrakt-inför-nästa-revision-2026-10-15). Detta preciserar användarens val av källbeskrivningar tillsammans med lokal verksamhetsgranskning; den aktuella omfattningsvägen använder v6 medan historiska v5/v5.1-kontrakt bevaras.

1. **Beskrivande kontrollräckvidd:** `Kontroll.rackvidd` ska ange tjänst, hot, möjlig observation, begränsningar, förutsättningar, grund, precisa källhänvisningar och sakkunnigstatus. Uppgiften bevisar inte att byrån genomför kontrollen. Den får inte användas av motorn som en ny reduktionsregel. Nya operativa poster kräver regelbasversion och relevanta attestbindningar; tomma tillägg ska utelämnas ur äldre serialisering.
2. **Lokal analys:** ett separat privat `Analyspaket` ska innehålla belägg och tjänstevisa svar om exponering, konkreta scenarier, kontrolltillämpning/utfall, kvarstående begränsningar, separata PT-/TF-resonemang, sektorsjämförelse, sanktioner och uppföljningsbeslut. Profilen förblir kanonisk faktakälla. Lokala svar får ingen kanal till AI och ingen möjlighet att ersätta motorns risknivåer.
3. **Två godkännanden:** först godkänner en identifierad person varje tjänsteanalys mot exakt underlag, svar och registerrevision. Författare och godkännare sparas; om samma person gör båda loggas och visas det i översikten, utan automatisk ny spärr. Därefter sakgranskas det faktiskt renderade dokumentet mot den frysta analyskopian. Dokumentet ska inte hashbinda ett godkännande som i sin tur kräver samma dokuments slutliga hash. Senaste lokala beslut gäller; underkännande får inte passeras med en äldre matchande attest.
4. **Ogiltigförklarande:** ändrad profil, period/status/belägg, bedömning, skrivresultat, regel-/källunderlag eller lokal analys kräver ny bindning och lokal granskning. Ändrad dokumenttext, ordning eller tabell kräver ny dokumentsakgranskning. Källgiltighet avser kontrollerade sparade versioner; ingen automatisk upptäckt av webbändringar utlovas. Äldre fastställda paket verifieras fortsatt mot sina frysta versioner.
5. **Grindar:** saknade obligatoriska/aktiverade svar, okänt relevant underlag, felaktiga referenser och olösta sak-/metodmotsägelser ska hindra lokalt godkännande och fastställelse. En känd kontrollbrist kan dokumenteras med motiverat beslut om kvarstående risk och uppföljning; det upphäver inga blockerande fynd eller sakkunnigkrav. Maskinell kontroll bevisar strukturell fullständighet, inte riktigheten i fri text.
6. **Två leveranssteg och format:** steg 1 levererar AB1 och AB4a:s nya läsordning i `D-ARB-tjanst-v5.1`, med oförändrat v5-skrivresultat/fem AI-delar och befintliga grindar, utan beroende till privat analys eller AB7. Egen granskning/fullsvit föregår separat beställd commit. Steg 2 inför v6:s lokala analys och ett särskilt v6-skrivresultat med endast `hot` och `sarbarheter` (80–160 respektive 100–220 ord). De tre AI-delarna kontroll, nivå och slutsats utgår och ersätts av lokalt innehåll. Två grundanrop görs alltid i v6, även utan analys, med oförändrad dataskyddsgräns i 8.4.10. Historiska skriv-/dokumentformat behåller sina kontrakt; efter v6 får v5/v5.1 inte kringgå de nya grindarna. Nya v6-utkast utan komplett analys visar kompletteringspunkter. Risköversikt med faktisk metodstatus kommer först efter syfte/avgränsning, scenario-/kontrolltabeller läggs per tjänst och full beräkning/källmetadata i B1. En Word-fil behålls; ord-/sidutfall ska mätas utan trunkering.
7. **Inarbetade källkompletteringar:** varje tjänst ska uttryckligen pröva kund-, kanal-, geografiska och egna verksamhetssårbarheter med relevans/belägg samt beskriva deras samverkan. Lokala frågor ska behandla lärdomar från rapportering, avböjanden och aktuell myndighetsinformation. Slutsatser ska länka konkret risk/åtgärd till rutin-ID/version eller en synlig rutinlucka, med ansvar, utlösare/frekvens, uppföljning och skild föreslagen/beslutad/genomförd status. Visa senaste utvärdering och eventuell separat uppdatering; en uppdatering flyttar inte årsfristen utan ny utvärdering. Reduktionsprövningen ska avse faktiskt motorutfall: olöst motsägelse mot kontrollräckvidd/effekt blockerar lokal attest och fastställelse, utan att modellen beräknar en annan nivå. Planens modeller och AB2–AB6 anger acceptansproven.
8. **Sex ytterligare kompletteringar:** tjänsternas arbetsmoment ska prövas för delanalys med motiverad detaljnivå. Faktisk betalningsinsyn och leverantörernas kontroller/egen verifiering ska dokumenteras. Uppdragshanterbarheten ska kunna leda till förstärkning, begränsning, avböjande eller avslut som mänskligt beslutsunderlag; hög risk är inte automatiskt avslag och rapportgodkännande utför inga kundåtgärder. Ett syntetiskt plattforms-/PSP-fall prövar bakomliggande parter och ändamål utan generellt riskpåslag. AB7 konkretiserar §7.8:s modellriskunderlag och levererar modellbindningen före AB2; steg 2 genomförs AB7 → AB2 → AB3 → AB4b → AB5 → AB6 efter steg 1 (AB1 → AB4a). Delanalyser skapar inga egna nivåer utan motorstöd. Metodkonflikt och bristande aktuellt modellunderlag hindrar slutlig attest/fastställelse.

9. **Förifyllnad och återanvändning:** redigerbara ogranskade utkast byggs ur bekräftad profil, motorutfall och källunderlag, med befintliga beläggsreferenser. Effekt, tillämpning och mänskliga beslut hittas inte på. Gemensamma scenarioanalyser får delas med uttrycklig samma/avviker-bekräftelse per tjänst; avvikelse motiveras lokalt och ändring upphäver beroende bekräftelser. De 16 frågorna är guidesteg: 10 alltid obligatoriska block och 6 villkorade fördjupningar. Ej aktiverad stödfråga blockerar inte. Det specificerade fyrtjänstfallet har 40 alltid obligatoriska + 24 aktiverade blockbedömningar och 12 unika scenarier för 36 tjänst–hot-kopplingar; antal block är inte antal nya fritextsvar eller klick. Gränssnitt/prov ska mäta återanvändning och faktisk kompletteringsbörda.
10. **Omräknad ordbudget:** fyrtjänstfallets AI-max är 1 520 ord. Riktbudget för huvudtext är 4 700 ord: 400 översikt, 700 gemensamt/delade scenarier, fyra tjänster med 380 AI + 420 lokala ord vardera, 400 åtgärder/uppföljning. Målet 3 500–5 000 prövas med verklig lokal analys och AI-max; inga nödvändiga resonemang trunkeras. Samma person som författare/godkännare visas utan att rollen framställs som oberoende.

Genomförandets lagringskontrakt: `Analysblock` binder aktivering och bekräftat blockinnehåll; `Scenariokoppling` binder uttryckligt val till aktuell gemensam scenariosumma. Författaren bevaras i varje beslut. Underlags-, svars- och hela registersumman hålls åtskilda; dokumentattesten binder hela registret inklusive beslut. Profil → analys → drift hålls låsta genom prövning och publicering. Oförändrade redan bekräftade block får återanvändas; importerade bekräftelseflaggor betros inte. Rapportersättning får inte tyst radera kända modellfel.

Regelbasens `beskrivningsstatus` skiljer beskriven möjlig observation från okänd räckvidd; frånvaro är okänd och utelämnas i historisk serialisering. Källstatus bevisar inte lokal effekt. V6:s valfria stycke-/cellproveniens (`ai`, `regelbas`, `lokal`) utelämnas när den saknas så äldre summor består. En ren byggare tar faktisk typad modellrapport ur verifierade frysta descriptorbytes; byråns användningsbeslut ersätter aldrig rapportens sakkunnig/M1. Python-/biblioteksversioner är separat miljöinformation.

De fem tidigare och sex ytterligare kompletteringarna preciserar dokumentets analys och spårbarhet. De ersätter inte kundriskprofiler, kundkännedom, rapporteringsrutiner, bevarande, intern kontroll eller utbildningsbevis. Föreslagen disposition, ordbudget, tabellform och dubbel attest är projektets design-/kvalitetsval, inte självständiga lagkrav. E-bokens äldre landlistor, paragrafnumrering och riskexempel används inte som aktuella beslutsregler. FATF och de nya provfallen är metodstöd; plattformsanvändning och högriskklassning bevisar inte i sig brott eller automatisk avslagsskyldighet. Befintliga katalogposter återanvänds; nya faktorvikter, reduktionsregler och numeriska delnivåer kräver separat metodprövning.

M1–M4 om kontrollernas verkan, TF, exponeringströsklar och faktorernas mättnad är fortsatt öppna. M1 ska avgöras av sakkunnig vid samma granskning som verifierar metoden; numerisk rättning vid behov hanteras som separat metodändring med facit/typfall. Användaren behöver utse sakkunnig och beslutsansvarig; ingen har tilldelats uppdraget genom denna spec. Teknisk implementation och syntetisk provning kan genomföras utan att juridisk, metodisk eller pilotmässig beredskap påstås vara klar.

Genomförandet av A+B följer samma D-ARB-plan och redovisas i STATUS: källbunden kontrollräckvidd och lokal granskning av faktisk exponering och effekt. Motorns numeriska metod är oförändrad. M1–M4 och verklig sakkunnigprövning är fortsatt öppna; tekniska prov gör dem inte godkända.

### Revision 35 – nivåmotivering, lokala utfall och sammanhängande tjänstetext

Grund: [research 11 §10–10.8](../../research/11-kallkontroll-allman-riskbedomning.md#108-kontroll-av-claudes-granskning-och-reviderad-prioritering-2026-10-17), Lindvikenprovet 2026-10-17 och tillsynsbesluten Forvis Mazars (Skåne 3647-2026), Hanko (38008-2025), Stella (47923-2025), Jas och Y-ekonomi. Besluten är sakstöd, inte domstolspraxis. Disposition, längd och tabellform är projektets redaktionella val, inte lagkrav.

1. **Nivån motiveras där den står.** Varje tjänsteavsnitt får delen *Risknivå och motivering* direkt efter den lokala analysen: programmets beräkning i ord (grundnivå, samtliga tillämpade faktorer med effekt, om taket hög nåddes, konsekvens, kontrollsänkning och regel) och, separat, byråns PT- och TF-bedömning. Programmet väljer inga "viktigaste" faktorer som motorn inte prioriterar. Dessa stycken samordnas aldrig till gemensamma resonemang. Saknad byråbedömning ger [VERIFIERA]. B1 behåller full beräkningstabell.
2. **Motorn och M1.** Motorns beräkning (BT-KVAR-01/02) är oförändrad tills sakkunnig prövat metoden. Huvudrapporten visar inte två konkurrerande nivåer. Intill varje kvarstående nivå anges tydligt att sänkningen bygger på ett ogranskat metodval som inte kräver belagd scenariotäckning, och den lokala reduktionsprövningens status. Förslaget "ingen reduktion utan belagd relevant räckvidd och effekt" står endast i B1:s beslutsunderlag för sakkunnig, med källa i Länsstyrelsens vägledning.
3. **Lokala utfall.** För sårbarheter som AI ser som "prövas lokalt" eller skyddade skriver programmet lokalt ett utfallsstycke per område i tjänstens sårbarhetsdel: gäller, villkoret inte uppfyllt, förekommer under metodens gräns, okänt eller inaktuellt underlag, med värde, omfång och period. Ett ej uppfyllt villkor beskrivs aldrig som frånvaro av risk. Inget av detta når AI; AI-begäran och omförsök är identiska oavsett privata värden.
4. **Sanktionsbetydelse.** `P-GEO.sanktionsanknytning` frågar om *identifierad* anknytning. Nej betyder att ingen anknytning har identifierats, aldrig att sanktionsprövning kan avstås. Tidigare nej-svar läses med denna snävare betydelse, eftersom den inte tillför något undantag; B1 visar att frågan omformulerats. Valideringen underkänner AI-text som påstår att sanktioner inte behöver prövas.
5. **Mindre upprepning.** Tjänstens geografibeskrivning skrivs inte ut när den är identisk med byråns och har samma källa och period; båda referenserna bevaras. Metodfrågorna samlas i en mening med faktisk status. En tjänst-ID-referens ger ingen källhänvisning i sig; identisk källhänvisning i följd inom samma avsnitt visas en gång; länken till B1 visas högst en gång per avsnitt; tabellceller samordnas först vid minst 40 ord.
6. **Tjänstefördelning.** När en byråövergripande faktor (utlandstransaktioner, utländska ägare, riskbransch, kontanthantering) har minst en kund och byrån erbjuder minst två tjänster frågar intaget hur många av dessa kunder som finns i varje tjänst. Svaren är lokala, kontrolleras mot byråns och tjänstens antal och används i utfallsstyckena. De läggs inte till i tillåtelselistan.
7. **Fasta verksamhetsval.** Per erbjuden tjänst tre fasta val som får sändas till AI: vem som attesterar underlag (kund, byrå, båda, okänt), betalningsmandat (inget, förbereder, verkställer, okänt) och bankinsyn (full, delvis, ingen, okänt). Inga fria svar, personer eller antal.
8. **Skrivformat v7.** En AI-del `analys` per tjänst (160–320 ord) skriver i sammanhang: uppdraget och verksamhetsvalen, hur tjänsten kan utnyttjas, vilka omständigheter som påverkar det och vad katalogens kontroller normalt inte visar. AI anger inga nivåer, påstår inte att kontroller genomförts eller varit effektiva och skriver inte om sårbarheter som prövas lokalt. Låsta stycken, utfallsstycken och nivåmotivering fogas in lokalt efter AI-texten. Kategorierna i PTL 2 kap. 1 § följs i en kompakt översikt per tjänst, inte genom uppräkning i löptexten. V5- och v6-resultat och äldre exporter förblir verifierbara.
9. **Verifiering.** Fullsvit, automatiskt prov av hela AI-anropskedjan under privata variationer, mätning av huvudord/sidor och ett kontrasterande prov med riktig AI på två påhittade byråer (beräkning kontra betalningsmandat, god kontra begränsad insyn). Inga sakkunnig- eller byråattester simuleras.
