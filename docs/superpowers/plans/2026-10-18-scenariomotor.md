# Scenariomotor – genomförandeplan

> **För agentiska utförare:** OBLIGATORISK DELFÄRDIGHET: använd superpowers:subagent-driven-development för att genomföra planen uppgift för uppgift. Stegen har kryssrutor (`- [ ]`).

**Mål:** Riskmotorn bedömer varje tjänst per scenario (tjänst × hot): hotnivå och de sårbarheter som möjliggör hotet ger sannolikhet och risk, kontroller sänker bara de hot de är utformade mot, och tjänstens nivå är det högsta scenariot.

**Arkitektur:** Regelbasen får en valfri scenariometod. Finns den, används den nya beräkningen; annars den gamla, så att äldre regelbaser, fryst testregelbas och sparade bedömningar är oförändrade. Ny modul `bedomning/scenarier.py` räknar scenarier; `motor.py` väljer metod och fyller tjänstens befintliga fält med maxvärden. Dokumentet visar en scenariotabell och motiverar nivån med de avgörande scenarierna.

**Teknik:** Python 3, Pydantic, YAML-regelbas, pytest.

**Spec:** `docs/superpowers/specs/2026-10-18-scenariomotor-design.md` (godkänd 2026-10-18). Bakgrund: huvudspecen avsnitt 7.

## Aktuellt användarbeslut: inga hårda ordgränser, 2026-10-18

Användaren har förtydligat att gränsen 5 000 ord inte ska finnas som ett hårt krav. Detta ersätter planens tidigare absoluta normalprovsgräns, inklusive jämförelsen mot 4 999 ord. Dokumentet ska inte kapas eller pressas under ett bestämt ordtal. Hela analysen, spårbarhet och läsbarhet styr. Ordmått och rådgivande längdvarning behålls. Redaktionell borttagning av verkliga upprepningar är tillåten, men ingen ytterligare kortning krävs för att få ett längdtest grönt. AI-skrivformatets separata delgränser påverkas inte av detta beslut.

## Globala villkor

- AGENTS.md gäller i sin helhet: AI fattar inga beslut; inga personuppgifter eller privata fritexter till AI; varje krav, katalogpost och regel har `kallor`/`kalla` och `grund`, skalor och gränser `metodval`; inga fria uttryck; inga riktiga API-anrop i tester; sakkunnigstatus ändras aldrig till `verifierad`.
- Identifierare på svenska utan å, ä, ö; användartext på svenska. Funktioner returnerar nya objekt.
- Regelbas utan scenariometod (`metod.scenario is None`) ger **byte-identiska** bedömningar mot dagens motor. Det gäller `tester/fixturer/regelbas_v0` och all historik.
- Ett nytt valfritt fält på en sparad modell utelämnas vid serialisering när det är tomt, så att äldre kontrollsummor består (samma mönster som `proveniens` i v6).
- AI-begäran ändras inte: faktablad, prompt och tillåtelselista rörs inte, utom att nya lokala fält aldrig får hamna i tillåtelselistan.
- Regelbasen blir **2.0.0** i uppgift 4 och bara där.
- Testkommando: `env -u ANTHROPIC_API_KEY .venv/bin/pytest <filer> -q`. Fullsviten (cirka 25 min) körs i uppgift 4 och 7.
- En lokal commit per godkänd uppgift på `codex/m0-m1`, format `<typ>: <beskrivning>`, avslutad med `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Ingen push. `research_notes/` committas inte. Sök efter pilotbyråns verkliga namn och data-id innan commit (de står bara i privata anteckningar, aldrig i repot).

## Granskningsfokus

1. **Tyst sänkning:** en sårbarhet utan hotkoppling, ett hot utan nivå eller ett okänt iakttagelsesvar får aldrig sänka en nivå jämfört med när uppgiften finns. Prov i uppgift 1 (validering) och 2 (motor).
2. **Kontroll utan mål:** en kontroll med belagd effekt men utan mål för scenariots hot sänker inte det scenariot. Prov i uppgift 2.
3. **Äldre regelbas:** `regelbas_v0` och en sparad bedömning utan `scenarier` ger identiskt resultat och identisk dokumenttext. Prov i uppgift 2 och 6.
4. **Lika maxscenarier:** när flera scenarier delar maxnivån redovisas alla, i katalogordning. Prov i uppgift 2 och 6.
5. **Iakttaget hot med okänt svar:** ett obesvarat eller okänt iakttagelsefält ger ingen höjning och gör inte tjänsten preliminär. Prov i uppgift 2.

---

## Övertagande och granskningspreciseringar 2026-10-18

Codex fortsätter från `f46b801` efter Claudes uppgifter 1–3. De färdiga stegen byggs inte om. Fortsättningen sker med subagenter, riktade RED→GREEN-prov, uppgiftsgranskning och en slutlig fullsvit. Ändringarna lämnas utan nya commits eller pushar tills ägaren beställer det; tidigare commitsteg nedan beskriver den ursprungliga planen.

- **Verksamma kopplingar:** en sårbarhet som listas för en tjänst måste kunna påverka ett hot i samma tjänst och en gemensam dimension. En globalt giltig men lokalt oanvänd hotreferens får inte tyst eliminera sårbarheten. Katalogens avgränsningar ska vara sakligt motiverade.
- **Ersättning:** `ersatter` tillämpas efter filtrering på scenariots hot och dimension. Detta är infört i `8fb4ba7` och ersätter formuleringen om återanvändning av globalt ersättningsfiltrerade sårbarheter i uppgift 2.
- **Modellidentitet:** `bedomning.scenarier` ska ingå i filförteckningen och en ändring i modulen ska bryta modellbindningen. Registreringen är införd; historiska rapportpaket ska fortfarande kunna verifieras.
- **Kontrollprövning:** varje sänkt motorscenario behöver positiv lokal prövning av samma hot och minst en av de kontroller som faktiskt bär dess sänkning. En annan kontroll eller ett annat hot räcker inte. Uttrycklig motsägelse för en bärande kontroll blockerar. Osänkta scenarier prövas med ordinarie kontroll-/gapregler, utan krav på att de ska få reduktion.
- **Spårbar metod:** scenarioregler och matrisrader får formella källreferenser; tomma nya fält utelämnas för historisk kompatibilitet. Matris, nivåer och maxaggregering är ogranskade metodval. SNRA:s 40/60 är inspirationskälla och validerar inte automatiskt projektets diskretisering eller kontrollavdrag.
- **Verifiering:** fullsviten körs efter att katalog, lokal spärr och dokument har integrerats, så att kända övergångsfel inte förväxlas med slutresultatet. AI-begärans bytes, äldre bedömningar, nivåjämförelser, Word-export och huvudtextens längd kontrolleras separat.

### Uppgift 1: Schema och validering för scenariometoden

**Filer:**
- Ändra: `src/riskanalys/regelverk/modeller.py` (`Hot`, `Sarbarhet`, `Effekt`, `Kontroll`, `Metod`, `Falt.typ`), `src/riskanalys/regelverk/validering.py`
- Test: `tester/regelkontrakt/test_validering_regelbas.py`, ny `tester/regelkontrakt/test_scenarioschema.py`

**Gränssnitt (produceras):**
- `Hot.niva: Sannolikhet | None = None`, `Hot.nivamotivering: str = ""`, `Hot.dimensioner: tuple[Literal['pt','tf'], ...] = ()` (tomt = härleds: `('pt','tf')` om `galler_tf` och id inte börjar med `H-TF-`, `('tf',)` för `H-TF-*`, annars `('pt',)`); funktion `hot_dimensioner(hot: Hot) -> tuple[str, ...]`.
- `Sarbarhet.hot: tuple[str, ...] = ()`.
- `Effekt.sannolikhet: int` med `ge=-2, le=2` och validator som avvisar 0.
- `Riktning(Strikt)`: `tjanst: str`, `hot: tuple[str, ...]` (minst 1), `kallor: tuple[str, ...]` (minst 1), `grund: Grund`, `motivering: str`. `Kontroll.riktar_sig_mot: tuple[Riktning, ...] = ()`.
- `Scenariometod(Strikt)`: `hotniva: Regel` (BT-HOT-01), `sarbarhetsniva: Regel` (BT-SARB-01), `sannolikhetsmatris: tuple[Sannolikhetsrad, ...]` (BT-SANN-02, nio rader `hot`, `sarbarhet`, `sannolikhet`, `id`, `grund`, `forklaring`), `kvarstaende: Regel` (BT-KVAR-03), `aggregering: Regel` (BT-TJ-01). `Metod.scenario: Scenariometod | None = None`; `Metod.regler()` tar med scenariometodens regler och matrisrader när den finns.
- `Falt.typ` får värdet `"flerval"` (lista av `val`).
- Valideringsfel (svenska, åtgärdsinriktade) när `metod.scenario` finns: hot i någon tjänst saknar `niva`; sårbarhet utan `hot`; okänt hot-ID i `Sarbarhet.hot` eller `Riktning.hot`; `Riktning.tjanst` erbjuder inte kontrollen eller hotet; riktning som omfattar samtliga hot i en tjänst med minst tre hot; matrisen saknar eller dubblerar någon av nio celler.

- [x] **Steg 1: Skriv fallerande prov** för varje valideringsfel ovan, för `hot_dimensioner` (H-01 → pt, H-03 → pt+tf, H-TF-01 → tf), för `Effekt` (−1 godkänns, 0 och 3 avvisas), för `flerval` och för att `regelbas_v0` och nuvarande regelbas laddar och validerar oförändrat utan `metod.scenario`. Använd en minimal syntetisk regelbas byggd i provet (kopiera mönstret i befintliga regelkontraktsprov).
- [x] **Steg 2: Kör och se dem falla.** `env -u ANTHROPIC_API_KEY .venv/bin/pytest tester/regelkontrakt/test_scenarioschema.py tester/regelkontrakt/test_validering_regelbas.py -q`
- [x] **Steg 3: Implementera schema och validering.** Regelbasens kontrollsumma för nuvarande regelbas får inte ändras (nya fält har standardvärden och utelämnas när de saknas).
- [x] **Steg 4: Kör** samma prov samt `tester/regelkontrakt tester/enhet/test_laddning.py`, och `.venv/bin/riskanalys regelbas validera`. Förväntat: PASS, oförändrad kontrollsumma.
- [x] **Steg 5: Commit** `feat: schema och validering för scenariometod`

### Uppgift 2: Scenarioberäkning i motorn

**Filer:**
- Skapa: `src/riskanalys/bedomning/scenarier.py`
- Ändra: `src/riskanalys/bedomning/modeller.py`, `src/riskanalys/bedomning/motor.py`
- Test: ny `tester/regelkontrakt/test_scenariomotor.py`, befintliga `tester/regelkontrakt/test_motor.py`

**Gränssnitt:**
- Konsumerar: uppgift 1:s modeller.
- Producerar i `bedomning/modeller.py`: `Scenariobedomning(Fryst)` med `hot: str`, `dimension: Literal['pt','tf']`, `hotniva: Sannolikhet`, `iakttaget: bool`, `sarbarheter: tuple[str, ...]`, `sarbarhetsniva: Sannolikhet`, `sannolikhet: Sannolikhet`, `konsekvens: Konsekvens`, `risk: Risk`, `tackande_kontroller: tuple[str, ...]`, `kvarstaende: Risk | None`, `avgorande: bool`, `regelspar: tuple[str, ...]`. `Tjanstbedomning.scenarier: tuple[Scenariobedomning, ...] = ()` (utelämnas tom).
- Producerar i `scenarier.py`: `IAKTTAGET_SUFFIX = '_iakttagna_hot'`; `bedom_scenarier(regelbas, tjanst, varden, kontroller: tuple[Kontrollbedomning, ...], okanda: frozenset[str]) -> tuple[Scenariobedomning, ...]`; `sammanfatta_scenarier(scenarier) -> tuple[Riskdel | None, Riskdel | None, Risk | None]` (PT inneboende, TF, PT kvarstående).

**Regler (exakt):**
- Scenarier: tjänstens `hot` i katalogordning; ett PT-scenario per hot med `'pt'` i `hot_dimensioner`, ett TF-scenario per hot med `'tf'`.
- Hotnivå = `hot.niva`, +1 steg (tak hög) om hot-ID finns i profilens kända värde för `P-TJ.{slug}{IAKTTAGET_SUFFIX}`. Okänt eller saknat värde: ingen höjning och inget tillägg i `okanda_uppgifter`.
- Sårbarhetsnivå = `steg(bas, Σ effekt)` på skalan låg–hög, där bas är `grund_sannolikhet` (pt) eller `grund_tf_sannolikhet` (tf) och summan tas över tjänstens tillämpade sårbarheter (befintlig `_tillampade_sarbarheter`, inklusive `ersatter`) som har scenariots hot i `Sarbarhet.hot` och `galler` som omfattar dimensionen.
- Sannolikhet = raden i `sannolikhetsmatris` för (hotnivå, sårbarhetsnivå). Konsekvens = `grund_konsekvens` (pt) eller `allvarlig` (tf). Risk = befintlig riskmatris.
- PT-kvarstående: ett steg lägre (golv låg) om någon kontroll i `kontroller` har `fungerar_och_ar_belagd` och `effekt_belagd is True` och en `Riktning` för tjänsten som omfattar hotet; dessa kontroll-ID:n i `tackande_kontroller`. Annars lika med risk. TF-scenarier har `kvarstaende=None`.
- Tjänstens `inneboende` = PT-scenariot med högst risk (vid lika: högst sannolikhet, därefter katalogordning) som `Riskdel`; `terrorfinansiering` likadant för TF; `kvarstaende` = högsta PT-kvarstående. `avgorande=True` för alla scenarier på respektive dimensions maxrisk.
- `regelspar` för tjänsten: scenariometodens regel-ID:n och använda matrisrader; `tillampade_sarbarheter` oförändrad betydelse (alla tillämpade).
- `motor.bedom_tjanst` använder `bedom_scenarier` när `regelbas.metod.scenario` finns, annars dagens kod oförändrad.

- [x] **Steg 1: Skriv fallerande prov:** alla nio matrisceller via parametrisering; sårbarhet kopplad till annat hot påverkar inte scenariot; `galler='penningtvatt'` påverkar inte TF-scenariot; iakttaget höjer, okänt höjer inte och gör inte preliminär; kontroll med belagd effekt men utan riktning sänker inte; kontroll med riktning och effekt `ej_bedömd` sänker inte; sänkning högst ett steg och golv låg; lika maxscenarier markeras alla avgörande; `regelbas_v0`-bedömning byte-identisk med dagens (jämför `model_dump_json`); sparad äldre bedömning utan `scenarier` läses och serialiseras byte-identiskt.
- [x] **Steg 2: Kör och se dem falla.**
- [x] **Steg 3: Implementera** enligt reglerna ovan.
- [x] **Steg 4: Kör** `tester/regelkontrakt tester/enhet/test_bedomning_korning.py tester/typfall -q`. Förväntat: PASS.
- [x] **Steg 5: Commit** `feat: scenarioberäkning i riskmotorn`

### Uppgift 3: Flervalsfält och iakttagna hot i intaget

**Filer:**
- Ändra: `src/riskanalys/intag/fragor.py`, `src/riskanalys/intag/svar.py`, `src/riskanalys/intag/vyer.py`, `src/riskanalys/intag/kvalitet.py` vid behov, `src/riskanalys/profil/modeller.py` vid behov
- Test: `tester/intag/` (ny `test_flerval.py`)

**Gränssnitt:** `flerval`-svar sparas som en sorterad tuple av giltiga `val`; okänt val ger ett svenskt fel; tomt val är tillåtet och betyder "inga iakttagna". Visning: kryssrutor i webbintaget, kommaseparerade värden i CLI. Fält `P-TJ.{slug}_iakttagna_hot` skapas i uppgift 4; här provas typen med ett syntetiskt fält.

- [x] **Steg 1: Skriv fallerande prov:** spara och läsa flerval; ogiltigt val avvisas; tomt sparas; webbformuläret visar kryssrutor och tar emot flera värden; fältet kan aldrig vara kritiskt eller blockera.
- [x] **Steg 2–4:** kör, implementera, kör `tester/intag -q`.
- [x] **Steg 5: Commit** `feat: flervalsfält i intaget`

### Uppgift 4: Katalog och regelbas 2.0.0 med källor

**Filer:**
- Ändra: `regelbas/kataloger/hot.yaml`, `regelbas/kataloger/sarbarheter.yaml`, `regelbas/kataloger/kontroller.yaml`, `regelbas/beslutstabeller/metod.yaml`, `regelbas/falt.yaml`, `regelbas/kallor.yaml` vid behov, `regelbas/version.yaml`
- Skapa: `docs/research/13-scenariomotor-katalog.md`
- Ändra: befintliga prov som anger nivåer från den riktiga regelbasen

**Innehåll (sakarbete med källa per värde):**
- `Hot.niva` och `nivamotivering` för alla 21 hot. Standard medel; hög endast där NRA 2024/25, Finanspolisen (`SRC-FIPO-*`) eller tillsynsrapport `SRC-TS-2026-14` uttryckligen beskriver tillvägagångssättet som vanligt eller växande för sektorn; låg där källa beskriver det som ovanligt. Lägg till `kallhanvisningar` med sida där det går.
- `Sarbarhet.hot` för alla 28. Hoten `H-TJ-*` kopplas endast till sårbarheter med område `tj` eller `verk`. Tillsynsrapportens exempel ska gå att reproducera: S-KUND-01 → H-01; S-ARB-15 → H-01 och H-03; S-GEO-01 och S-ARB-15 → H-03.
- `Kontroll.riktar_sig_mot` för alla 13, smalt: endast hot som källan stöder att kontrollen är utformad mot.
- `metod.yaml`: `scenario` med BT-HOT-01, BT-SARB-01, BT-SANN-02 (matrisen i specen, exakt), BT-KVAR-03 och BT-TJ-01, alla `metodval`, `ej_granskad`, med förklaring och källor (`SRC-LST-GOR-ARB`, `SRC-TS-2026-14`; lägg till EU:s metod `SRC-EU-SNRA-METOD` med URL https://fatfplatform.org/assets/04112015-Methodology-SNRA-Clean-v1.1.pdf om den saknas).
- `falt.yaml`: `P-TJ.{slug}_iakttagna_hot` per tjänst, typ `flerval`, val = tjänstens hot-ID:n, `kritisk: false`, frivilligt, `grund: metodval`, källor `SRC-14FS-2024-11` och `SRC-LST-GOR-ARB`. Inte i tillåtelselistan.
- `version.yaml`: 2.0.0.
- `docs/research/13-scenariomotor-katalog.md`: tabeller över hotnivåer, sårbarhetskopplingar och kontrollmål med källa och motivering, samt en jämförelsetabell för typfallen och den syntetiska fyrtjänstprofilen: gammal och ny nivå per tjänst och dimension, avgörande scenario, och en förklaring till varje ändrad nivå.

- [x] **Steg 1: Skriv fallerande prov:** regelbasen validerar med `metod.scenario`; varje sårbarhet har minst ett hot; varje kontroll har minst en riktning; tillsynsrapportens exempel finns som kopplingar; fältet finns och saknas i tillåtelselistan.
- [x] **Steg 2: Kör och se dem falla.**
- [x] **Steg 3: Gör katalogarbetet** med källor och skriv research 13.
- [x] **Steg 4: Uppdatera prov** som påstår nivåer för den riktiga regelbasen; varje ändrad förväntan ska motsvara en rad i jämförelsetabellen. Ändra inga prov mot `regelbas_v0`.
- [x] **Steg 5: Kör fullsviten** och `.venv/bin/riskanalys regelbas validera`. Förväntat: alla passerar utom bortvalt livetest.
- [ ] **Steg 6: Commit** `feat: regelbas 2.0.0 med scenariometod och källbundna kopplingar`

### Uppgift 5: Reduktionsspärren per scenario

**Filer:** Ändra `src/riskanalys/analys/provning.py` (`faktisk_reduktion`, block 12). Test: `tester/enhet/test_analysgrind.py`, `tester/intag/test_analys.py`.

**Gränssnitt:** `sankta_scenarier(t) -> tuple[Scenariobedomning, ...]` (PT-scenarier där `kvarstaende` är lägre än `risk`); `faktisk_reduktion(t)` är sann om något scenario sänkts, eller som idag när `scenarier` är tomt.

**Regel:** för varje sänkt scenario blockerar en lokal `Kontrollprovning` med `tackning == 'saknas'` för en lokal scenarioanalys vars `hot` innehåller scenariots hot och vars kontroll finns i `tackande_kontroller`: `'{hot}: kontrollen täcker enligt byråns prövning inte scenariot; rätta kontrolluppgifterna eller registrera metodkonflikt.'` Befintliga krav för reduktionsprövning gäller oförändrat.

- [x] **Steg 1–4:** prov (sänkt scenario + lokal täckning saknas → blockerande; bedömd tillräcklig → inget fynd; äldre bedömning utan scenarier → dagens beteende), kör, implementera, kör.
- [ ] **Steg 5: Commit** `feat: reduktionsspärr per scenario`

### Uppgift 6: Scenariotabell och nivåmotivering i dokumentet

**Filer:**
- Skapa: `src/riskanalys/dokument/scenariotabell.py`
- Ändra: `src/riskanalys/dokument/nivamotivering_v6.py`, `src/riskanalys/dokument/tjanstavsnitt_v7.py`, `src/riskanalys/dokument/nivatext.py` (B1-förklaring), `src/riskanalys/dokument/arb_v6.py` vid behov
- Test: `tester/enhet/test_nivamotivering_v6.py`, `tester/enhet/test_arb_v7.py`, ny `tester/enhet/test_scenariotabell.py`

**Gränssnitt:**
- `bygg_scenariotabell(rb, t: Tjanstbedomning) -> Dokumenttabell | None` med kolumner `Hot`, `Hotnivå`, `Möjliggörande sårbarheter`, `Sannolikhet`, `Risk`, `Täckande kontroll`, `Kvarstående`. En rad per PT-scenario och en per TF-scenario (märkt "TF").
  - Hotnivå visar "(iakttaget)" när det gäller.
  - Sårbarheter visas med kortnamn.
  - Avgörande rader markeras "avgör nivån".
  - Returnerar `None` när `t.scenarier` är tomt.
- `nivamotivering_stycken` använder, när `t.scenarier` finns, mönstret `Avgörande scenario: {hot}. Hotnivå {H}{ (iakttaget)}; sårbarhetsnivå {V}: tjänstens egen nivå {bas}{, höjd av namn, …}. Sannolikhet {P}, konsekvens {K}, risk {R}. {Kontrollmening}`. Kontrollmeningen är antingen `{kontroll} täcker scenariot och har belagd effekt; kvarstående {kvar}.` eller `Ingen kontroll med belagd effekt täcker scenariot; kvarstående {kvar}.` Ett stycke per avgörande scenario och dimension. Byråns bedömning står kvar oförändrad. Utan `scenarier`: dagens text.
- I v7 ersätter scenariotabellen kategoriöversikten. B1 får hela scenarioberäkningen med regelspår per scenario.
- Normalprovets ordmått mäts och redovisas i rapporten. Enligt användarens senaste beslut finns inget hårt ordtak; fullständighet, spårbarhet och läsbarhet styr.

- [x] **Steg 1–4:** prov (tabellens rader, kolumner och markering; motivering med iakttaget hot och med täckande kontroll; lika avgörande scenarier ger flera stycken; äldre bedömning ger dagens text och tabell; ordmått redovisat och all analys bevarad), kör, implementera, kör `tester/enhet tester/intag tester/m2 -q`.
- [ ] **Steg 5: Commit** `feat: scenariotabell och scenariobaserad nivåmotivering`

### Uppgift 7: Slutverifiering och dokumentation

**Filer:** `docs/STATUS.md`, huvudspecen (revision 36 i ändringsloggen och statusraden), denna plan (utfall).

- [x] **Steg 1:** Kör fullsviten och regelbasvalideringen. Förväntat: alla passerar utom bortvalt livetest.
- [x] **Steg 2:** Kör bedömning, skrivning med `Testleverantor`, granskning och export för den syntetiska fyrtjänstprofilen och kontrollera att varje tjänst har scenariotabell och nivåmotivering. Kör offline-bedömning (ingen AI) för de två påhittade v7-byråerna i den privata provmappen och lägg deras gamla och nya nivåer i jämförelsetabellen i research 13, utan privata texter.
- [x] **Steg 3:** Uppdatera STATUS och spec revision 36: scenariomotorn, regelbas 2.0.0, att värdena är ogranskade metodval och att M1–M4 och sakkunnig prövning kvarstår.
- [ ] **Steg 4: Commit** `docs: scenariomotor verifierad och status`


## Återupptaget efter sessionsavbrott, 2026-10-18

Codex återtar T5–T7 med bevarade ändringar och utan commit/push. T4:s omgranskning godkände fixrundan; dess kvarstående dokumentfel är integrationsarbete för T6. T5:s 20 nya scenariospärrprov är gröna i färsk övertagandekontroll; ytterligare 56 gemensamma dokumentfixturfel väntar på T6. T6 byggs och T7:s offlinejämförelse är utförd. Slutlig fullsvit, samlad oberoende granskning och Word-kontroll återstår.

De två öppna metodfrågorna — höga kvarstående nivåer genom maxregeln och kontrollmål som täcker hela PT-sidan i skatterådgivning/bolagsbildning — är kvar för sakkunnigbeslut. Ingen av reglerna ändras för att få tester eller längdmål att gå igenom.


## Slututfall 2026-10-18

Uppgift 4–7 är tekniskt slutförda. Fullsviten: **2 685 passerade, ett bortvalt livetest, noll fel**, körd i fyra färska processer med exakt samma samlade testurval som vanlig fullinsamling. Inga dubletter eller extra bortval; 657 käll-/regel-/testfiler oförändrade under körningen. Total väggtid 673.56 s. Regelbas 2.0.0 validerar; kompilering och diffkontroll passerar.

Scenariotabeller, fullständigt B1-spår, lokal reduktionsspärr och positiva/negativa attest-, paket- och återställningskedjor är verifierade. Normalprov: 4/4 accepterade Testleverantor-svar, hela begäransfilen byteidentisk mot 1.6.0, 210/210 längre lokala svar bevarade. Ordmått 4 997 huvudtext + 16 859 B1; rådgivande varning är kvar, inga hårda ordgränser. Bredare utkastsexport: 5 354 + 16 998 ord, manifest giltigt, 40 scenariorader; verklig ogranskad metod och lokala brister stoppar fortfarande godkännande. Renderkontroll med buntad LibreOffice/Poppler: 68 sidor, fyra läsbara scenariotabeller och 0 ord utanför sidorna av 23 267 kontrollerade. Ingen kontroll i Microsoft Word eller medarbetarläsning gjordes här.

De två fiktiva v7-byråernas nio tjänster har oförändrade nivåer mot sparad 1.6.0; originalprofilerna är orörda. Samlad oberoende granskning fann inga Critical/Important. Ett Minor är parkerat: olika faktor-ID/vikter med samma namn kan grupperas i huvudtexten; dagens katalog har unika namn och B1 bevarar beräkningarna. Åtgärda före en framtida katalog med sådana namn. Maxregelns kvarstående nivåer och C-TJ-08/09:s hela PT-täckning lämnas som sakbeslut, tillsammans med M1–M4 och verklig sakkunnigprövning.

Inga commits eller pushar. De gamla commitrutorna är avsiktligt orörda; de ingår inte i senaste beställningen. Tidigare röda/avbrutna körningar och källmanifest finns i planens bevarade ignorerade arbetsjournal.

## Beställda rättningar efter programgenomgången, 2026-10-19

Användaren beställer rättning av de tre bekräftade felen enligt den bifogade omgranskningen. Befintligt arbete bevaras på `codex/m0-m1`. Inga commits eller pushar. Metodval, regelbas, AI-begäran och sakkunnigstatus ändras inte.

- [x] Reproducera med regressioner: samma profilbytes till beräkning och kopia; ändrad/tillagd/borttagen lokal analys stoppar aktuell Word-nedladdning, men ingen analys då eller nu tillåts; ändrad/saknad modellidentitet kräver ny bedömning, med bevarad historisk läsning och kompatibilitet vid enbart presentation.
- [x] Läs profilen en gång och spara samma bytes. Spara modellbindning vid bedömningen och kontrollera den före fortsatt arbete.
- [x] Bind utkastets nedladdning till aktuellt analysregister och erbjud granskning/export av lokala ändringar från befintlig AI-text utan nya anrop. Behåll utkastets tillåtelse till öppna fynd och fastställelsens starkare grindar.
- [x] Oberoende avgränsad kodgranskning, riktade regressioner, färsk fullsvit, regelbasvalidering, kompilering och diffkontroll. Uppdatera STATUS med uppmätt resultat och kända gränser.

Arbetsjournal och utgångskopia: `.superpowers/fixes/2026-10-19-kedjebindning/`.

**Slututfall:** alla tre felen är rättade. 14 nya regressioner kördes först: 12 väntade fel och två gröna skyddsprov. Därefter 38 riktade och 122 integrationsprov gröna. Oberoende granskning av de sju frysta kod-/testfilerna: Ready, inga Critical/Important/Minor, egen körning 38 passerade. Färsk fullsvit: **2 699 passerade, ett bortvalt livetest, inga fel**, 732,45 s, exakt fullständigt urval i fyra nya processer och 658 oförändrade käll-/regel-/testfiler inklusive pyproject. Regelbasvalidering, kompilering och diffkontroll passerar. Regelbas 2.0.0 och dess kontrollsumma är oförändrade, alla sakkunnigstatusar är fortsatt ej_granskad. Endast sju kod-/testfiler och fyra dokumentationsfiler avviker från denna rundas start; resten av det ärvda arbetet är bevarat. Inga riktiga API-anrop, commits eller pushar.

Äldre bedömningar utan modellbindning får läsas historiskt men måste räknas om för en ny kedja. Äldre nedladdningsvägar utan omfattningsmetod behåller kompatibiliteten utan nya analys-/driftmappar. Kontrollen gäller analysregistrets aktualitet, ingen ny fullständig levande beläggsprövning. Maxregel, C-TJ-08/09, M1–M4 och verklig sakkunnigprövning är oförändrade separata frågor. Detaljer: arbetsjournalens `resultat.md`, `review-result.md`, `final-fullsuite-result.json` och `change-audit.json`.


## Öppna metodbeslut efter H7.7 2026-10-19

H7.7 har kompletterat beslutsunderlaget med tio H7.1-kontraster och oförändrad motor. Alla 40 tjänsteutfall behåller hög PT/mycket hög TF/hög kvarstående PT, medan borttagen belagd effekt ändrar nio PT-scenarier utan att tjänstemax ändras. Mandat, tjänstespecifik exponering/period och kundöverlapp behöver uttrycklig sakkunnigprövning; numerisk likhet är inte bevis för saklig likvärdighet. H7.1:s oberoende tekniska fixturgranskning är godkänd efter mandattextens rättning; sakkunnigprövningen är fortsatt öppen. Mandatkontrastens operativa textkonflikt är rättad och riktat efterprovad med oförändrade kontrollutfall, effektstatus och hela motorbedömningen; en generell blockmotivering kvarstår som redaktionell rest. Se [research 13:s H7.7-matris](../../research/13-scenariomotor-katalog.md#h77-källbunden-metodprövning-2026-10-19) för källgränser och de nio öppna beslutsfrågorna D1–D9. Maxregeln, C-TJ-08/09, tjänst–hot-kopplingarna, TF och M1–M4 förblir öppna. Ett uttryckligt ändringsbeslut följs av separat versionsbunden implementation med frysta före-/efterfacit, nya modellbindningar och fullsvit. Dokumentförbättringar innebär inte metodgodkännande.
