# Steg E – sakkunnigpaket och granskningsguide

Användaren godkände uttryckligen båda referens-PDF:erna efter D den 23 oktober 2026 och gav klartecken till E. Regelbas **2.12.2**, kodcommit `508f8c6`. [Granskningsguiden](../../sakkunniggranskning.md) börjar med D1–D9 och D-LAGRE, därefter hot/katalog och sist övriga krav. Den beskriver källor, alternativ, sänkningar, beroenden, import, avslag och förnyade godkännanden samt V10:s disposition 0–5 och A/B1.

## Tre verkliga exporter

Underlag finns i `.superpowers/evidens/2026-10-23-sakkunnig-2.12.2/`:

| Paket | Objekt | Manifestbundna filer | Beslut |
|---|---:|---:|---|
| RP-RED-VG | 276 | 527 | Samtliga `ej_granskad` |
| RP-RED-SKANE | 276 | 527 | Samtliga `ej_granskad` |
| RP-RED-STHLM | 276 | 527 | Samtliga `ej_granskad` |

Exporten använder programmets befintliga `granskningsunderlag`-funktion för respektive paket med rättsligt datum 2026-10-23. Exporterna kompletteras med guide och fullständig objektgenomgång, lästa primärkällor, tio metodbeslut och deras genomförandebindningar, fulla före-/efterutfall, 40 kontrastprofiler, tolv fasta profilfiler med lokal sökvägsmappning, 244 bundna appfiler samt sex referens-PDF:er och kontrollunderlag. Alla beslut är obesvarade. Granskare och kompetens är tomma och oberoende är inte intygat. Inget importeras i produktens regelbas av Codex.

Objektgenomgången täcker exakt mallens objektmängd. Varje post återger hela sakunderlaget, källor och motivering samt berörda fasta fall eller sin paketövergripande betydelse. Sakgranskaren behöver inte läsa appkoden för att se vad förslaget innehåller; koden följer med för separat teknisk granskning av genomförandebindningen.

Efter den oberoende paketinventeringen har också sammanställningen `genomforandebeslut.md` bifogats. Slutpaketen har därför 527 manifestbundna filer vardera; sakobjekt, profilfiler och genomförandebindningar är oförändrade.

## Oberoende granskning och rättningar

E granskades som återstående del av samma samlade C–E-review. Två betydelsefulla paketeringsfynd rättades före leverans:

1. Den nya Europol-filen och dess TXT/JSON-utdrag bar först det äldre käll-ID:t. De bär nu `SRC-EUROPOL-TESAT-2025-20261023`, med PDF-kontrollsumma som matchar registret. Äldre kontrollsumma bevaras i regelbasen. Exakta äldre PDF-bytes saknas och anges uttryckligen som otillgängliga; ingen aktuell granskad sakpost hänvisar till äldre ID.
2. De tolv fasta profilernas utfallsfiler pekade på historiska sökvägar utanför paketet. Exakta indata ingår nu i `metod/fasta-profiler/`, med `metod/profilkarta.json` som mappar sökvägar och kontrollsummor. Alla tolv matchar utfallsfilernas profilhashar.

Den kopierade guidens lokala slutprovslänk fungerar. Reviewern verifierade i alla tre paket: noll manifestavvikelser, 276/276 objekt, tolv profilhashar, samtliga 244 filbindningar, sex PDF:er och samtliga bifogade käll-PDF:ers versions-ID/kontrollsummor. Slutomdöme: **inga kvarstående E-fynd; E kan lämnas till sakkunnig**. Inga mindre fynd skjuts upp.

## Referenser och teknisk slutkontroll

Huvudrapporterna är fortsatt 20/21 sidor, A 38/40 och B1 195/200. Hela fria original, 33 sårbarhetsrader, fem lägre-risk-rader och 15 lagexempel är bevarade. 2.12.2 skiljer från de godkända huvud-PDF:erna bara i versionsangivelsen på första och sista sidan; dessa sidor har kontrollerats visuellt. Alla bilagesidor har inte granskats visuellt. Tiorsidorsriktmärket är inte uppnått och inget innehåll har kapats.

[Slutprovsunderlaget](2026-10-23-regelbas-slutprov.md) redovisar första fullsvitens 3 522 godkända/34 fel, rättningarna och slutlig fullsvit: **3 557 godkända, 0 fel**, matchande insamling/JUnit och 851 oförändrade snapshotresurser. Leveransarkivet ligger i `../underlag/sakkunnigpaket-2.12.2-2026-10-23.zip` relativt repot, med tre regionpaket och fullständiga testprotokoll. Alla regelobjekt förblir `ej_granskad`; verklig rättslig prövning, kalibrering, identitets-/kompetenskontroll och expertbeslut återstår. Ingen push eller merge.
