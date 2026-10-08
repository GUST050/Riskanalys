# Riskanalys – designspecifikation

**Status:** Förslag, revision 3 (2026-10-08). Ej godkänd för implementation.
**Underlag:** [researchsammanställningen](../../research/README.md).
**Ändringar:** se [ändringsloggen](#22-ändringslogg) sist i dokumentet.
**Nästa steg:** granskning av revision 3. Därefter implementeringsplan för M0 och M1.

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
| 1 | Källregister | Alla källor med metadata, giltighet per datum och län, kontrollsumma | Nej |
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
- `riskanalys verifiera` kontrollerar ett paket mot dess manifest.
- **Återställningsprov:** ett fastställt paket återställs från säkerhetskopia på en tom installation och verifieras (avsnitt 16).

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
| Avvikelse | `A-<datum>-<nr>` | `A-2026-10-08-002` |

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
konsoliderad_tom: null     # för lagar: senaste ändrings-SFS, t.ex. "SFS 2026:1075"
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

### 7.4 Sammanvägning

| Regel | Grund |
|---|---|
| Varje tjänsts egen risk redovisas alltid, oavsett tjänstens vikt | Metodval |
| Tjänsterna vägs samman med dokumenterade vikter, som standard andel av kunder eller omsättning | Metodval |
| Den samlade nivån är lägst den högsta nivån bland tjänster som väger minst 20 % | Metodval. Gränsen prövas mot typfall i M3 och kan ändras med motivering. |
| En tjänst med hög eller mycket hög risk ska alltid få egna slutsatser och åtgärder, även om den väger under gränsen | Metodval. Hindrar att en liten högrisktjänst döljs i sammanvägningen. |
| Motorn redovisar varje faktors bidrag så att ingen enskild faktor ensam avgör | Metodval, följer AMLA:s utkast |
| Avvikelse från sektorns nivå i den nationella riskbedömningen ska motiveras | Tillsynspraxis (rapport 2026:14) |

### 7.5 Proportionalitetsnivå

| Nivå | Typfall | Effekt |
|---|---|---|
| Enkel | Få anställda, ett kontor, enkla tjänster, inga behörigheter i kundernas namn | Kortare, mer beskrivande dokument. Samma krav täcks. |
| Standard | Typisk redovisningsbyrå | Full analys per tjänst |
| Utökad | Många anställda, flera kontor, behörigheter, utländska kunder, koncern | Fler scenarier, funktioner för intern kontroll, tätare uppföljning |

Nivån beräknas av faktorerna i Länsstyrelsens föreskrifter 6 kap. 3 § (omsättning, anställda, verksamhetsställen, verksamhet, tjänster, komplexitet, riskbedömning). Gränsvärdena är metodval och kan justeras med motivering.

### 7.6 Kundmodellen: fyra separata spår

Kundmodellen är en mall i fas 1 och en motor i fas 2. Den består av fyra spår som utvärderas var för sig. Inget spår får påverka ett annat utom där lagen säger det. **Varje spår och varje beslutsgren granskas av sakkunnig.**

| Spår | Fråga | Rättslig grund (verifieras i M2) | Utfall |
|---|---|---|---|
| **A Förbud och stopp** | Får affärsförbindelsen inledas eller fortsätta, eller åtgärden utföras? | Otillräcklig kundkännedom (PTL 3 kap. 1 §, med undantag vid rättsligt förfarande). Misstanke vid etablering (3 kap. 2 §). Misstänkt transaktion (3 kap. 3 §, med undantag när det inte går att avstå). Träff på sanktionslista (EU:s sanktionsförordningar). | Tillåtet, stopp, eller stopp med lagens undantag. Varje utfall har egen dokumentation. |
| **B Obligatoriska särskilda åtgärder** | Vilka åtgärder kräver lagen oavsett riskklass? | Högrisktredjeland (3 kap. 17 §): skärpta åtgärder och godkännande av behörig beslutsfattare, med lagens undantag. PEP och närstående (3 kap. 19–20 §§): medlens ursprung, skärpt uppföljning, godkännande, samt 18 månader efter avslutat uppdrag. | Lista över åtgärder som ska genomföras och dokumenteras |
| **C Riskklassning** | Vilken riskprofil har kunden? | PTL 2 kap. 3–5 §§. Faktorer, poäng och gränser är metodval. Att PEP eller högrisktredjeland också ger hög riskklass är ett metodval, inte ett lagkrav. | Låg, normal eller hög, med motivering. Preliminär om uppgifter saknas. |
| **D Rapportering** | Ska misstanke rapporteras till Finanspolisen? | PTL 4 kap. 3 § (rapportering) och 4 kap. 9 § (meddelandeförbud) | Rapportskyldighet, oberoende av riskklass |

Riskklassen (spår C) styr omfattningen av förenklade eller skärpta åtgärder. Den ändrar aldrig utfallet i spår A, B eller D.

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
4. Ett underkänt svar körs om med valideringsfelen som återkoppling. Efter tre försök stoppar avsnittet med ett fynd.
5. Godkänt svar sparas med kontrollsumma och går vidare till granskning och sakgranskning (avsnitt 10). Maskinell validering visar inte att en formulering stöds av källan. Det avgör sakgranskningen.

### 8.3 Modell, kostnad och utvärdering

- Claude via Anthropics officiella Python-SDK, bakom ett eget leverantörsgränssnitt.
- **Startinställning:** `claude-opus-5-5`, adaptiv tänkning, effort `high`. Modell och effort är inställningar, inte låsta val.
- **AI-utvärdering (etapp M3)** med riktiga skrivuppgifter innan inställningen fastställs. Mått: sakfel, ogrundade påståenden, andel avsnitt som klarar maskinell validering, sakgranskarens tidsåtgång och kostnad per godkänt avsnitt. Valet av modell och effort görs av projektägaren utifrån mätningen.
- **Automatiska tester använder en kontrollerad testleverantör** som ger förutbestämda svar. Prov mot det riktiga API:t är frivilliga, körs separat och kostar pengar.
- Strukturerade svar via SDK:ns `messages.parse` med pydantic-scheman. Claudes inbyggda källhänvisningar går inte att kombinera med strukturerade svar, så programmets egna referens-ID:n används.
- Regelbasens innehåll läggs först i anropet för att utnyttja prompt-cachning.
- **Batch-API används inte som standard.** Det lagrar begäran och svar hos leverantören i upp till 29 dagar. Det får slås på för underlag som är fritt från personuppgifter, och batcherna raderas då efter att resultatet hämtats.
- Om personuppgifter någon gång måste skickas till AI (fas 2) krävs databehandling inom EU. Anthropics eget API erbjuder i dag bara `us` och `global`, så EU-behandling sker då via Google Vertex AI eller Amazon Bedrock i EU-region.
- Modell, inställningar, promptmall, svar och tokenförbrukning sparas per anrop och tas med i manifestet.

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
3. Alla krav i regelpaketet som är tillämpliga på byrån har sakkunnigstatus *verifierad*, och regelpaketets paragrafkarta är sakkunniggranskad (avsnitt 16.1).
4. Fynd hanteras efter vad de gäller:

   | Fynd gäller | Får fastställas om |
   |---|---|
   | **Metodval** (skala, gräns, poäng, vikt, formulering) | Fyndet är åtgärdat, eller funktionen för regelefterlevnad har accepterat avvikelsen med motivering (registreras som avvikelse) |
   | **Ett ska-krav eller allmänt råd som saknas eller är fel tillämpat** | Fyndet är åtgärdat, eller en sakkunnig har bedömt det särskilt och dokumenterat varför kravet är uppfyllt eller inte tillämpligt. Byrån kan inte själv acceptera bort ett lagkrav. |
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
| Typfall | Hela kedjan med syntetiska profiler ger förväntade nivåer, fynd och status |
| AI-validering | Valideringen fångar påhittade ID:n, siffror, nivåer och personnamn (med testleverantör) |
| AI-utvärdering | Sakfel, ogrundade påståenden, granskningstid och kostnad per godkänt avsnitt (live, frivilligt, M3) |
| Verifiering och återställningsprov | Ett fastställt paket verifieras mot sitt manifest och återställs från säkerhetskopia på en tom installation |
| Facitjämförelse (M7) | En referensbyrås tidigare underkända riskbedömning ska underkännas. Ett genomarbetat referensutkast ska i stort godkännas. |
| **Acceptansprov före verklig användning** | Se 16.2 |

**Syntetiska uppgifter används tills regelbasen är sakkunniggranskad.** Ingen riktig byrå får ett fastställt paket innan dess.

### 16.1 Paragrafkarta

Tester hittar fel i regler som finns, men inte ett krav som aldrig lades in. Därför har varje regelpaket en **paragrafkarta**: varje paragraf i de relevanta kapitlen av lag och föreskrift, för angivet datum och län, med antingen de krav-ID:n den ger upphov till eller "ej tillämplig för sektorn" med motivering. Kartan granskas och signeras av sakkunnig per version av regelpaketet. Programmet kontrollerar att kartan är fullständig mot källans paragrafindelning.

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
| **M3 Modellvalidering och AI-utvärdering** | Metodbilaga, valideringsrapport, avvikelselogg, typfall (bland annat saknade uppgifter och liten högrisktjänst), prövning av 20 %-gränsen, AI-utvärdering med riktiga skrivuppgifter | Valideringsrapport klar. Beslut om modell och effort fattat utifrån mätning. |
| **M4 Användningsprov och minsta drift** | Enkelt lokalt formulär för intag och sakgranskning, ändringskontroll, versionshistorik, återställningsprov, acceptansprov (16.2) | Acceptansprovet är genomfört och dokumenterat |
| **M5 Första riktiga byrå** | Full allmän riskbedömning för en riktig byrå, fastställd av byrån | Paketet är fastställt av byrån och verifierat |
| M6 Övriga dokument | Rutiner (med modellriskhantering), kundmodell, instruktioner, kravmatris, tillsynspaket | Alla dokument i avsnitt 11 genereras |
| M7 Provtillsyn och facit | AI-provtillsyn och facitjämförelse | Facitfallen ger förväntat utfall |
| M8 Full drift | Påminnelser, utlösande händelser från referensdata, belägg | Ändrad högrisklista ger korrekt flaggning |
| M9 Kundnivå | Egen spec | – |
| M10 Fler sektorer | Ett sektorspaket per sektor | – |

**Parallellt spår: AMLR.** Startar samtidigt med M2. AMLR:s artiklar och bilagor kartläggs mot kravregistret, och ett eget regelpaket med giltighet från 2027-07-10 byggs och testas vid sidan av dagens paket. Spåret följer promemorian *EU:s penningtvättspaket* (Fi2026/01654) och AMLA:s slutliga riktlinjer. Klart när AMLR-paketet är sakkunniggranskat före 2027-07-10.

M1 bevisar att arkitekturen håller innan arbetet läggs på hela regelbasen. M2–M4 ser till att metoden är juridiskt granskad, validerad och användbar innan en riktig byrå fastställer något.

## 19 Risker

| Risk | Hantering |
|---|---|
| Regelbasen tolkar lagen fel | Sakkunniggranskning per beslutsgren, källa per post, regelkontrakt |
| Ett krav saknas helt i regelbasen | Paragrafkarta granskad av sakkunnig |
| Juridiska beslutsgrenar blandas ihop | Kundmodellens fyra separata spår |
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

1. Innehållet i Länsstyrelsen Skånes föreskrifter (12FS 2024:8) behöver jämföras med Stockholms och Västra Götalands.
2. AMLA:s slutliga riktlinjer om verksamhetsövergripande riskbedömning väntas under fjärde kvartalet 2026. Till dess märks allt som bygger på utkastet som *EU-utkast* eller *metodval*.
3. De svenska kompletterande reglerna: promemorian *EU:s penningtvättspaket* (Fi2026/01654) var på remiss med svar senast 2026-10-30. Någon proposition har ännu inte setts.
4. Om Bolagsverket erbjuder elektronisk åtkomst till registret över verkliga huvudmän (påverkar fas 2).
5. Vem som gör sakkunniggranskningen av regelbasen och acceptansprovet.

## 21 Definitioner

| Begrepp | Betydelse här |
|---|---|
| Fastställt av byrån | Byråns behöriga organ har beslutat om dokumentet. Ingen certifiering. |
| Preliminär | Resultatet bygger på minst en uppgift som inte är bekräftad |
| Metodval | En regel som byrån eller programmet valt, inte ett lagkrav |
| Metodavvikelse | Ett motiverat beslut att avvika från ett metodval i ett enskilt fall |
| Sakgranskning | En människas granskning av att text stämmer med fakta och källa |
| Paragrafkarta | Förteckning över varje relevant paragraf och hur den hanterats i regelbasen |

## 22 Ändringslogg

| Revision | Datum | Ändring |
|---|---|---|
| 1 | 2026-10-08 | Första förslaget |
| 2 | 2026-10-08 | Efter första granskningen (Codex): bristmönstrens ID:n samordnade, kategorier för personuppgifter, dokumentstatus och grindar, typat villkorsformat, manifest med kontrollsummor, mänsklig sakgranskning, datamapp utanför repot, modulerna `faststallelse/` och `lagring/`, M1 som tunn kedja |
| 3 | 2026-10-08 | Efter andra granskningen (Codex): (1) kundmodellen delad i fyra spår (förbud och stopp, obligatoriska åtgärder, riskklassning, rapportering) med sakkunniggranskning per beslutsgren; (2) modellriskhantering enligt PTL 6 kap. 1 § andra stycket; (3) minsta drift flyttad före första riktiga fastställelse; (4) okänd uppgift ger preliminärt resultat, och små högrisktjänster döljs inte i sammanvägningen; (5) paragrafkarta för fullständighet och promemorian Fi2026/01654; (6) AI-modell och effort som inställningar som avgörs genom utvärdering, och testleverantör i automatiska tester; (7) tillåtelselistor för AI-underlag, små grupper och ingen batch som standard; (8) löftet om återskapande ersatt med bevarande, säkerhetskopia och återställningsprov. Dessutom: grind som skiljer metodavvikelser från lagkrav, "fastställt av byrån", användarflöde, acceptansprov, ny etappordning och AMLR som parallellt spår. |
