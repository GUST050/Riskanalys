# Regelbas C, rapportdisposition, D och E Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Genomför inline; en samlad färsk slutgranskare före slutlig verifiering.

**Goal:** Slutför C, del 3, D och E enligt uppdrag revision 3 och användarens senaste klartecken.

**Architecture:** Befintlig typad motor och historiska rapportformat bevaras. Hotnivåer motiveras mot lästa källor. Ny rapportversion för disposition 0–5 byggs offline före produktintegration. D1–D9 och lägre-risk-beslut registreras som versionsbundna, sakkunniggranskningsbara metodval med explicit genomförandebindning. Slutligen exporteras alla tre sakkunnigpaket.

**Tech Stack:** Python 3.12, YAML, Pydantic, Word/PDF, pytest och Testleverantor.

**Spec:** `/Users/danieltrogen/riskanalys-steg1-3/docs/superpowers/reviews/2026-10-23-uppdrag-codex-r4-r7-och-regelbas.md` revision 3, dess exempelrapport och förslag revision 2. B-bas: `902da79`/regelbas 2.1.0.

## Global Constraints

- Användaren 2026-10-23: fortsätt alla återstående steg; samla tester till slutet där möjligt. Inga fullsviter mellan arbetsstegen. Lokala arbetscommits/version per delsteg och metodbeslut.
- Bara nödvändiga bygg-/syntax-/katalogkontroller under arbetet. Regressionsprov skrivs med ändringarna; samlade riktade prov, snabb och full körs inför slutleverans. Slutlig snapshot ska vara oförändrad och collection/JUnit matcha.
- Alla nya och ändrade regelobjekt är ej_granskad. Ingen riktig expertattest och ingen lättnad av sakkunnigspärren.
- Ingen push eller merge. Inga riktiga byrådata eller API-anrop. AI-tillåtelselistan och AI-skrivformat V8 ändras inte.
- Del 3:s dataluckor ska få två konkreta alternativ och användarens val före rapportbygge; offline-PDF före produktintegration; efter D ny PDF-kontroll före E. Fortsätt oberoende arbete medan nödvändiga val inväntas.
- Exemplet styr form, inte kundriskmodell, åtgärdskrav eller antagna kundöverlapp. Fri text bevaras hel. Okänt skiljs från nej. Metodtext hämtas ur aktuell bunden regelversion.

## Review Focus

1. Historiska signerade V8/V9-paket och befintliga V9-utkast ska behålla format, summering och giltig verifiering utan omräkning.
2. Okända, inaktuella, motstridiga eller delvis kända uppgifter får aldrig bli nej, noll, under tröskel eller positivt lägre-risk-underlag.
3. Varje metodbeslut ska binda allt genomförande inklusive modellfiler; gammal objektattest får inte överleva ändrat genomförande.
4. Metodval som sänker ska redovisas per scenario/riskled och samlat mot ursprunglig 2.0.0-baslinje; inga sänkningar genom ogrundad kontrolltäckning.
5. Resultatrapport 0–5 ska ha alla katalogindikatorer, 15 lagexempel, hela fria motiveringar och samma sakutfall som A/B1, med fungerande källpekare och samlad sakgranskning.

### Task 1: C – nivåunderlag för alla 26 hot

**Files:** `regelbas/kataloger/hot.yaml`, `regelbas/version.yaml`, `docs/superpowers/reviews/2026-10-23-regelbas-steg-c.md`, källcitat/bindningar i samma granskningsunderlag; `tester/regelkontrakt/test_hotnivaer_c.py`.
**Interfaces:** Hot.niva/nivamotivering/kallhanvisningar/sakkunnig; kommande D och rapport använder bunden regelbas. Inga nya höjningar/sänkningar utan tillräckligt stöd.

- [x] Läs samtliga använda källsidor och dokumentera direkt citat, locator, faktisk evidens och vad källan inte avgör.
- [x] Varje hot får källbunden nivåmotivering eller uttrycklig underlagsbrist med medel kvar. Exakta frekvenser får inte härledas ur sektorns nivå eller rapporteringsantal.
- [x] Spara samma syntetiska referensprofiler och effekt mot B samt ursprunglig bas. Katalogladdning/validering som nödvändig kontroll; regressioner körs samlat senare.
- [x] Arbetscommit och regelversion 2.2.0; uppdatera beroenden och status.

### Task 2: Datatäckning och användarval för del 3

**Files:** `docs/superpowers/reviews/2026-10-23-rapport-datatackning.md`, separat konkret rapportplan under `docs/superpowers/plans/` efter mappning av befintlig V9-kedja.
**Interfaces:** Profil.uppgifter, Bedomning, Analyspaket, regelkataloger, historik, rutinåtgärder; ingen ny datakälla får antas.

- [x] Mappa varje rad i dispositionen till fält/objekt/pointer eller dokumenterad okänd uppgift.
- [x] För nivå per område, kundriskklasser, rutinavsnitt och samverkan: två alternativ, rekommendation, frågeantal och konsekvens. Be användaren välja; fortsätt C/annan oberoende kartläggning under väntan.
- [x] Lås den nya rapportversionens format-/historikgräns i rapportplanen; inga V9-omskrivningar. Se `2026-10-23-rapport-v10.md`; fyra användarval inväntas före kod.

### Task 3: Del 3 – offline och därefter produktkedja

**Files/interfaces:** Specificeras i rapportplanen före kod. Ny rapportversion ska producera konstruktioner och tre filer ur exakt samma analyskällor som V9; A/B1 behåller disposition.

- [x] Bygg offline enligt godkända dataalternativ. Alla fem statusar, egna lägre-risk-tabeller, lagens 15 punkter och kapitel 0–5. Inga nya AI-anrop.
- [x] Rendera båda verkliga referenspaketen till PDF; kontrollera alla huvudrapportsidor och ingen kapad text. Mät faktisk sidmängd. Lämna konkreta PDF:er vid användarkontrollpunkten.
- [x] Efter klartecken: integrera export, formatbyte, frysta källor, samlad sakgranskning och fastställelse. Historiska V9-vägar bevaras. Arbetscommit, rapportversion och granskningsunderlag.

### Task 4: D – ett provisoriskt val per beslut

**Files/interfaces:** `regelbas/beslutstabeller/metod.yaml`, relevanta katalog-/fältfiler, typade modeller/laddning/sakkunnigbindning, motorns berörda moduler, rapportens metodförklaringar. Exakta beslut delas upp i dokumenterade arbetssteg före implementation.

- [ ] Läs D1–D9-tabellen och tidigare jämförelseunderlag. För varje val: källa, alternativ, genomförandeobjekt/modellfiler och kostnad vid avslag.
- [ ] Bygg D1, D2, D3, D4, D5, D6, D7, D8 och D9 samt lägre-risk-beslut var för sig, med egen regelversion/commit och före-/efterfacit. Oförändrat beteende kan väljas när källstöd för förändring saknas, men ska ha explicit motivering och granskningsobjekt.
- [ ] Redovisa per steg och totalt mot 2.0.0 för enmansbyrå, betalningsmandat, riskbranscher, få faktorer och båda referensfallen. Lista alla sänkningar och kunskapsluckor.
- [ ] Nya PDF:er efter D visar aktuell metod, inte statisk TF-text. Lämna vid slutkontrollpunkten före E.

### Task 5: E och samlad slutverifiering

**Files:** `docs/sakkunniggranskning.md`, `docs/superpowers/reviews/2026-10-23-regelbas-slutprov.md`, sakkunnigpaket för tre regioner; avsedda regressioner i `tester/`.
**Interfaces:** befintligt CLI granskningsunderlag/importera-granskning; metodbeslut och indikatorer måste ingå i verkliga objektattester.

- [ ] Efter PDF-slutkontroll: exportera RP-RED-VG, RP-RED-SKANE, RP-RED-STHLM. Guide med metodbeslut först, sedan hot/katalog och sist oförändrade krav. Förklara beslut, import och återföring vid avslag.
- [ ] En färsk samlad oberoende slutreview av C–E inklusive rapportens risker och versionsgränser. Rätta betydelsefulla fynd med reproducerande prov.
- [ ] Kör samtliga samlade riktade prov, snabbprofil och fullsvit på exakt slutligt snapshot; rätta fel och kör om nödvändigt. Inga gröna påståenden från delurval.
- [ ] Slutligt granskningsunderlag, käll-/versions-/beslutsberoenden, lokala commits och ren gren. Ingen push/merge.
