# Rättning efter granskning av R2 på f653eea

**Avgränsning:** fortsatt R2, före användarens PDF-klartecken. R3–R7, produktens export och fastställelse har inte påbörjats. V8 är fortsatt standard. Den andra klonen är orörd. Inga riktiga AI-anrop eller nya riskregler.

Detta ersätter förhandsvisningarna i [den första R2-redovisningen](2026-10-23-resultatrapport-r2.md). De gamla PDF-filerna finns kvar som historiskt granskningsunderlag och är inte versionerna som ska godkännas.

## Tre huvudfynd

### 1 Sänkningar utan lokal prövning

Rapporten använder nu samma `ej_godtagna_sankningar` som analysgrinden. R4:s celler visar **Sänkning ej prövad lokalt** för orsaken `oprovat`, och **Sänkning ej godtagen lokalt** för andra brister. R5 anger hot, nivåväg och orsaker; samma orsak och nivåväg kan delas med alla hot-ID kvar. Kontrollernas namn och ID visas. Motorvärdena ändras inte. Texten förklarar att den inneboende scenarionivån gäller tills sänkningen godtas och att analysen inte kan godkännas dessförinnan.

En extra lucka upptäcktes under rättningen: även en sänkning i ett scenario som inte avgör tjänstens sammanfattade nivå kan sakna lokal täckning. Den tas därför med som kontrollavvikelse, exempelvis H-MOD-01. Urvalet av avgörande led är oförändrat; kontrollavvikelser tillkommer utan att märkas som avgörande. Egna scenariers ej godtagna sänkningar redovisas i R5.

Proven jämför varje faktiskt ej godtagen sänkning med R4 eller R5 och prövar även att en godtagbar sänkning inte får en falsk varning. En första testförväntan antog felaktigt att alla tjänster hade brister och att alla sänkningar låg i R4. Den är rättad: löneuppdraget saknar sänkningar, och egna scenarier ligger i R5.

### 2 Oförändrad standardmotivering

Nya PT-/TF-förifyllnader har `[KOMPLETTERA: …]`. Dessutom avvisar `_saktext` de två historiska standardmallarna, med deras olika nivåvärden, även i redan sparade analyser. Förifyllnader behöver alltså inte skapas om för att spärren ska gälla. Identifieringen är avsiktligt begränsad till kända hela standardmallar; programmet bedömer inte kvaliteten i godtycklig fri text.

V9 använder samma färdighetskontroll och registrerar en källbunden presentationsbrist. I ett tillåtet preliminärt utkast syns den ofärdiga texten tillsammans med en kompletteringsmarkering; den presenteras inte som en färdig lokal motivering. R4:s kommande produktintegration ska föra presentationsbristerna till blockerande fynd enligt den redan beslutade planen.

Regressionerna omfattar både PT och TF i den verkliga vägen `Analystjanst.beslut`, med oförändrad analysfil när beslutet nekas, samt den samlade tjänstegenomgången. Innehållsprovet för V9 kontrollerar både bristens originalpointer och den synliga markeringen.

### 3 Betalningsmandatets mekanism

Mandatfixturen har egna lokala varianter av de gemensamma scenarierna för löneuppdraget och uttryckliga `avviker`-kopplingar. De andra tre tjänsterna behåller kundens betalningar. Löneuppdragets egna scenarier ligger i R5, separat från R4:s gemensamma mekanism. Kopplingarna är inte sakgodkända automatiskt.

Fixturen återanvänder inte längre förifyllnadens standardmotiveringar för mandatfallet. Befintliga fullständiga syntetiska motiveringar behålls och mandat-/insynspåståenden anpassas. Den visuella kontrollen fångade också formuleringen om avsaknad av mandat i PT-motiveringen och en återställd gammal aktiveringsmotivering. Båda ingår i regressionen. Detta är rättning av syntetiskt provunderlag, inte automatisk omskrivning av en byrås text.

## Läsbarhet

- Svenska etiketter ersätter interna enumvärden, exempelvis bekräftad, föreslagen och öppen.
- Kontrollnamn visas med ID. Åtgärdstext med ID och status visas i R6; R5 hänvisar dit.
- Exakt identiska hela färdiga PT-/TF-motiveringar återges en gång i R4 med samtliga originalpointers; R5 hänvisar dit. Inga utdrag görs.
- R6 hänvisar till en ordagrant redan återgiven luckbeskrivning om hela beskrivningen finns i en åtgärdstext. Detta anger textens plats och härleder inte att åtgärden täcker luckan. Beskrivnings- och åtgärdsreferenser bevaras, liksom luckans egen status, motivering, ansvar och tidsfrist.
- R1 har en deterministisk slutsats ur tjänsteutfallen och antalet öppna registrerade analysgap.
- Egna scenarier får R5-ID; gemensamma scenarier får R4-ID. En tjänst utan delade kedjor får en förklaring om egen mekanism, inte en tom uppräkning.
- `*` och `†` markerar avgörande före-/efterled med förklaring efter matrisen. Tabellhuvudet upprepas och korta rader hålls ihop vid sidbrytning.

Två mindre redaktionella önskemål kvarstår: erfarenhetsfältets fyra liknande men inte identiska deltexter kortas inte maskinellt, eftersom de är ett sammanhållet fritt källfält och designen förbjuder utdrag. R6 är fortfarande en lista, inte den föreslagna tabellen; separata luckor och åtgärder får inte kopplas ihop enbart genom antaganden. Dessa påverkar inte rättningen av huvudfynden.

## Aktuella filer och verifiering

- [Fyra tjänster, 7 sidor](../../../.superpowers/evidens/2026-10-23-resultatrapport-r2-rattad/fyra_tjanster/rendering/resultatrapport.pdf).
- [Betalningsmandat, 8 sidor](../../../.superpowers/evidens/2026-10-23-resultatrapport-r2-rattad/med_betalningsmandat/rendering/resultatrapport.pdf).

Filerna ligger i Codex-klonens `.superpowers/evidens/2026-10-23-resultatrapport-r2-rattad/`, tillsammans med `bygge.json`, `kallor.json`, `matning.json`, DOCX och sidbilder. `kontroll.json` binder de visade PDF-filerna och källorna. De är ignorerade av Git och följer inte med en push. A/B1 finns i det fullständiga byggunderlaget men är ännu inte separat produkt-exporterade Word-/PDF-filer.

| Fall | Resultat ord | A ord | B1 ord | Totalt | V8 med samma källor och ordkontrakt | PDF sidor |
|---|---:|---:|---:|---:|---:|---:|
| Fyra tjänster | 2 718 | 13 728 | 35 794 | 52 240 | 49 503 | 7 |
| Betalningsmandat | 3 172 | 14 674 | 36 806 | 54 652 | 51 461 | 8 |

Ordkontraktet är titel, samtliga stycken och dataceller i dokumentmodellen, samma som i föregående R2-redovisning. Saknade kontrollförklaringar och verkliga mandatavvikelser gör resultatrapporten längre än de förra förhandsvisningarna. A/B1 i mandatfallet växer också eftersom fixturen nu har fullständiga motiveringar och egna scenarier. Detta kallas inte en total förkortning.

**Färsk verifiering, Python 3.12.15:**

- **94 riktade prov godkända, 104,16 s**, exit 0: samtliga V9-underlags-, rapport-, vy- och offlineprov, tjänstegenomgång, två verkliga analysattestprov, versionsprov och V8-rendering. Kommando och utfall finns i `.superpowers/sdd/2026-10-22-resultatrapport-plan/r2-granskning-slutgiltigt.log`.
- **Snabbprofil 140 godkända, 52,858 s**, exit 0. Collection och JUnit matchar, inga fel eller överhoppningar, **798 resurser oförändrade**. Kvitto `/private/tmp/riskanalys-r2-granskning-snabb-giltigt-20261023/resultat.json`. Snapshotet kontrollerades igen efter PDF-bygget och var oförändrat.
- Första reproduktionen på gammal kod: elva nya fyndprov fallerade. Radbrytningsprovet och de två extra mandat-/tomlistproven sågs också röda före respektive rättning. En separat process med enbart den gamla `_saktext`-funktionen återställd i minnet gav **två förväntade fel och ett godkänt markörprov** i tjänstegenomgången. Produktfilerna ändrades inte för detta kontrollprov. De rättade varianterna ingår i den gröna slutkörningen.
- Samtliga källpointers är lösta och kontrollsummor kontrollerade. R-rapporten återbyggs identiskt ur frysta källor och urval i båda fallen. **44 avgörande medlemsled** är kvar; matrisen har **53 medlemsled** när de nio ej godtagna sänkningarna också räknas med. Konstruktionsspår: **127/141**.
- Samtliga **15 slutliga sidor** är visuellt kontrollerade. Identiska sidbilder verifierades med bytejämförelse efter den sista textjusteringen, och ändrade sidor öppnades på nytt. Inga observerade klipp eller överlapp; matrisrader delas inte över sidor. A4, brödtext 11 punkter och tabeller 9,5 punkter. Renderare LibreOfficeDev 26.8.0.0.alpha0, build `2c87e51eeaa2b413ff4ae097b2705eea1995d8e5`.
- Regelbas och samtliga `MODELLFILER` är oförändrade. Ingen ny fullsvit eller leverans för verklig byråanvändning hävdas.

| PDF | SHA-256 |
|---|---|
| Fyra tjänster | `74c98f3f959d13d9dec6cf5cf66a5047e6177b7b2a17fe07b359bf6c1aeb820f` |
| Betalningsmandat | `e0e7c9f81c1d42564e800d7d1f6f752b782bf25c56ae4df543d7f906c7d30a0f` |

PDF-klartecken krävs fortfarande enligt K15 i [designen](../specs/2026-10-22-resultatrapport-design.md) och R2 i [planen](../plans/2026-10-22-resultatrapport-plan.md). Ingen fullsvit, push eller merge ingår i denna förhandsgranskning. Färsk fullsvit på slutligt källsnapshot kvarstår före produktleverans.
