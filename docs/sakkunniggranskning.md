# Guide för sakkunniggranskning av regelbas 2.12.2

Detta är ett förslag till regelbas för redovisningsverksamhet, med resultatrapport V10. Alla nya och ändrade poster är `ej_granskad`. Teknisk validering eller godkända tester är inte rättsligt godkännande. Granskaren ska kunna ändra eller avslå varje förslag. Fastställelse är spärrad tills regelpaket, genomförande och den enskilda rapportens sakuppgifter har aktuella godkännanden.

Användaren har godkänt båda referens-PDF:erna efter steg D den 23 oktober 2026 och gett klartecken till steg E. Huvudrapporterna omfattar 20 respektive 21 sidor. Riktmärket tio sidor har inte uppnåtts; innehåll har inte kapats.

## Börja med rätt paket och läsordning

Det finns separata underlag för `RP-RED-VG`, `RP-RED-SKANE` och `RP-RED-STHLM`, med rättsligt datum 2026-10-23. Varje paket innehåller:

- `granskningsmall.yaml`: obesvarade beslut per granskningsobjekt. Identitet och kompetens är tomma; oberoende är inte intygat.
- `underlag.json`: hela regelbasens sakuppgifter, källregister och fullständiga rättsliga lydelsetexter. `val` anger paket, datum och innehållssumma.
- `sakkunniggranskning.md`: denna guide. `objektgenomgang.md` innehåller varje faktiskt granskningsobjekts fullständiga sakunderlag, källor, motiveringar och koppling till referensfallen. Läs dessa data; det krävs ingen kodläsning för sakgranskningen.
- `metod/`: beslut, alternativa val, sänkningar, exakta beroenden och före-/efterutfall. `referensrapporter/` innehåller de två godkända syntetiska huvud-PDF:erna och deras kontrollunderlag.
- `genomforande/`: en kopia av de 244 bundna appfilerna med kontrollsummor, för eventuell separat teknisk granskning. Sakgranskningen stöds av förklaringarna och faciten i paketet.
- `facit.json` och `facitgranskningsmall.yaml`: separat granskning av tillsynsfacitet. Det frigör inte regelpaketet.
- `manifest.json`: kontrollsummor för paketets filer. Det bevisar filintegritet enligt programmets befintliga hotmodell, inte granskarens identitet.

Granska först metodbesluten nedan. Granska därefter hotnivåer, ändrade katalogposter och villkor. Granska sist övriga krav, den regionala paragrafkartan och befintliga metodobjekt. Beslut om D ersätter inte beslut om dess enskilda genomförandeobjekt: båda finns i mallen.

## 1. Metodbesluten först

Varje D-beslut innehåller sitt val, minst ett alternativ, skäl, osäkerhet, lästa källbelägg med sida/avsnitt, exakta sakobjekt, genomförandefiler och återföring vid avslag. De fullständiga posterna finns i `underlag.json` under `metodbeslut`, i objektgenomgången och i `metod/beslut-och-beroenden.json`. Den senare visar exakt vilka sakobjekt och filkontrollsummor varje beslut binder. Alla 244 appfiler binds konservativt; även en ändring utanför den berörda beräkningsfunktionen kan därför kräva ny D-prövning.

| Objekt | Föreslaget val och skäl | Effekt och öppen prövning |
|---|---|---|
| D1 | H-MOD-02, momskarusell, avgränsas från ren löneberedning. Lönehot H-TJ-04 och H-02 kvarstår. Källorna ger inte stöd för att varje löneberedning är ett momskarusellscenario. | Fyra scenarier tas bort i de tolv fasta profilvarianterna. Ingen sänkning av kvarvarande riskled eller tjänstnivå i sexfallen. Pröva tjänstegränsen och om annan faktisk tjänst ska analyseras separat. |
| D2 | H-01, fakturahotet, avgränsas från ren löneberedning. Brottsvinst som lön kvarstår. | Ytterligare fyra borttagna scenarier i samma tolv varianter. Ingen sänkning av kvarvarande riskled eller tjänstnivå i sexfallen. Pröva ren löneberedning mot bokföring, fakturering och betalningsmandat. |
| D3 | Konservativ portföljmodell behålls. Byråfaktorer avgränsas inte numeriskt till en tjänst utan en kalibrerad metod. Frivilliga lokala antal visas med begränsning. | Ingen beräkningsändring. Även lokalt nollantal neutraliserar inte automatiskt byråfaktorn. Pröva överföringen från byrå till tjänst, exponering och vilka kompletterande uppgifter en alternativ metod kräver. |
| D4 | Kundsamförekomst visas endast för belagda kombinationsgrupper. Samtidigt aktiva byråfaktorer bevisar inte att samma kunder har dem. | Ingen ny beräkningsvikt. Två konkreta fördelningar med samma 60 kunder och tjänsteantal 24/24/24/24 har 24 respektive 12 flertjänstkunder. Marginaltal identifierar inte exakt överlapp eller kundernas riskklass. |
| D5 | Max per dimension behålls. Scenariobredd och otäckta avgörande scenarier redovisas. | Ingen beräkningsändring. Pröva om max döljer betydelsefull bredd; källorna kalibrerar inte en alternativ summering. |
| D6 | TF-konsekvens behålls som allvarlig, med separat sannolikhet per scenario. TF får inget automatiskt PT-kontrollavdrag. | Ingen beräkningsändring. Pröva skyddsintresse, analysenhet och kalibrering; allvarlig konsekvens betyder inte att varje scenario får samma sannolikhet eller risk. |
| D7 | S-ARB-05, ideell indikator, höjer endast TF. Andra tillämpliga PT-faktorer verkar fortfarande. | Sänker PT i kontraster med ideell indikator ensam; se särskild redovisning nedan. Pröva om det finns självständigt PT-stöd för ett annat val. |
| D8 | Högst ett PT-steg för belagd effekt i samma hot, tjänst och period. Lokal godtagbarhet prövas separat. Ingen utvidgning av okända kontrollmål. | Ingen ny numerisk effekt jämfört med föregående steg. Pröva effektbelägg, period och täckning av samtliga avgörande scenarier. Motorns avdrag är inte en godkänd lokal sänkning. |
| D9 | Indikatorpåslag och tak behålls, med scenarioavgränsad ersättning. | Ingen beräkningsändring. Pröva dubbelräkning och beroenden. Antalet indikatorer bevisar inte att de är oberoende. |
| D-LAGRE | Fem indikatorer på potentiellt lägre risk visas utan automatisk nivåeffekt. | Ingen sänkning. Pröva relevans, överlapp och dubbelräkning innan eventuell verkan införs. Positiv indikator neutraliserar inte andra faktorer. |

De lästa källorna beskriver rättsliga krav och riskmekanismer. De ger inte empirisk kalibrering av programmets exakta trösklar, fasta konsekvensvärden, påslag, maxregel eller kontrollsteg. Dessa är uttryckligen `metodval`. Källcitat, lokalisering, vad belägget stöder och vad som saknas framgår av respektive D-post. Alternativen är förslag för granskning, inte redan prövade likvärdiga modeller.

### Sänkningar ska granskas särskilt

D7 ger i de 40 kontrastprofilerna **64 sänkta led mot föregående steg**: två ekvivalenta ideellprofiler × åtta tjänster × fyra led för H-03/PT (sårbarhet, sannolikhet, inneboende risk och motorns kvarstående risk). Det är inte 64 oberoende scenarier. I vardera profilen sjunker inneboende PT i åtta tjänster; tjänstens kvarstående PT sjunker endast i T-BOLAG-02, eftersom andra avgörande scenarier håller uppe nivån i de övriga. TF är oförändrad. Motorns lägre kvarstående nivå är inte bevisad lokal kontrollverkan.

**Samlat mot ursprunglig 2.0.0** är det 48 sänkta led: samma två profiler × sex jämförbara äldre tjänster × fyra led. T-RED-08 och T-RED-09 saknas i 2.0.0 och får inte beskrivas som sänkta mot en obefintlig nivå. D1–D2 ger totalt 80 borttagna scenarier i de 40 kontrasterna. Fullständiga före-/efterutfall och profilkontrollsummor finns i `metod/kontraster3/`; inga gamla profilbytes har ersatts.

De sex fasta fallen med ursprunglig respektive kompletterad profil ger tolv varianter. Deras D1–D2-jämförelser tar bort sammanlagt åtta scenarier; inget kvarvarande numeriskt riskled och ingen tjänsts slutnivå sänks där. Skillnaden mellan dessa fall och ideellkontrasten är en redovisad begränsning i täckningen, inte ett påstående om ofarlighet.

De tolv fasta profilfilerna finns i `metod/fasta-profiler/`. `metod/profilkarta.json` mappar de historiska sökvägarna i utfallsfilerna till paketets lokala filer och verifierade kontrollsummor. `metod/slut-2.12.2/` visar oförändrade tjänste- och scenarioled mot D-slut efter den tekniska rättningen.

### Läs beräkningarna utan kod

Regelbasens typade villkor använder `==` (lika med), `!=` (inte lika med), `>=` (minst), `>` (över), `<` (under), `<=` (högst), `i` (ett av alternativen), `finns`/`saknas` samt `alla`/`nagon`/`inte` för och/eller/negation. Saknad, inaktuell eller oförenlig uppgift är okänd och får inte tolkas som ett nej eller noll. Villkor, tröskel, dimension och hotkoppling står fullständigt vid varje indikator i objektgenomgången.

Motorn bildar scenarier för tjänstens tillämpliga hot och dimension PT/TF. Hotnivå och tillämplig sårbarhet ger sannolikhet enligt den exporterade scenariometodens beslutstabeller. Sannolikhet och konsekvens slås upp i den fullständiga riskmatrisen. PT och TF hålls isär. Avgörande scenarier ger tjänstens maxnivå; en kontroll kan påverka bara sina uttryckliga mål med aktuellt belägg. Ett kvarvarande otäckt maxscenario hindrar en tjänstesänkning. Exakta skalor, tabellrader, tak och metodförklaringar finns som egna objekt i genomgången, så att granskaren kan räkna varje sparat scenario för hand. Sanktionsprövningen är separat och får inte bakas in i PT/TF.

## 2. Hotnivåer och katalogändringar

Granska samtliga **26 hot**. Varje hot har ett direkt läst citat med sida/avsnitt, nivåmotivering och källhänvisningar. Medel behålls där källorna inte ger tillräckligt stöd för en annan generell nivå per tjänst. Sektorns risknivå eller antal rapporterade händelser är inte en uppmätt frekvens för den enskilda tjänsten. Objektgenomgången återger hela posten; C:s granskningsunderlag följer med i `metod/`.

Steg B tillförde två tjänster, fem hot, fem högre-risk-indikatorer och fem lägre-risk-indikatorer, snävade in distansvillkoret samt förtydligade tjänstenamn. Antalet intagsfält ökade med **56, från 324 till 380**. Granska varje fälts fråga, period, okäntalternativ och koppling till katalogen i det kompletta underlaget.

- **T-RED-08:** ansökningar om ROT, RUT och offentliga utbetalningar. **T-RED-09:** granskningsuppdrag. Trust och nominell aktieägare byggs inte; ett ja på dessa verksamhetsfrågor ger synligt stopp före fastställelse.
- De sex nya frågorna om högre risk avser antal kunder och period; okänt är tillåtet. Antal är inte individuella kundriskbedömningar.
- PTL 2:4 p. 2–4 hanteras genom kundernas hemvistfördelning Sverige/övriga EES/utanför EES och ett centralt källbundet landunderlag. Ingen individuell kundprövning antas. Saknat landunderlag är okänt. Landvalet är `metodval` och `ej_granskad`.
- H-MOD-06:s PT-/TF-grund ska prövas i katalogposten. Enbart sanktionsanknytning räcker inte som PT-/TF-grund.
- Den frivilliga frågan om iakttagna hot för löneberedning följer efter D1–D2 tjänstens aktuella hotlista. Frånvaro av iakttagelser sänker inte en hotnivå.

### Källversioner och avvikelser

Ny Europol-fil är registrerad separat som `SRC-EUROPOL-TESAT-2025-20261023`, hämtad 2026-10-23, SHA-256 `97a34c80ae0f8fcb6bd5527c620fb21358820a4c7b541839cc4bd1bee7d666aa`. Den äldre `SRC-EUROPOL-TESAT-2025`, hämtad 2026-10-11, behåller `0a18061235353efda54b433510f4ff20a19fca4b8933b00578f4d6f3045ef3f6`. Båda versionerna finns i källregistret; den gamla kontrollsumman har inte skrivits över.

Paketets bifogade Europol-PDF och dess TXT/JSON-utdrag bär nyversionens ID. Exakta äldre PDF-bytes är inte tillgängliga i paketet. Den nya filen får inte användas som verifiering av den äldre kontrollsumman; den äldre versionen måste återanskaffas om ett äldre källbelägg ska verifieras mot originalfilen.

Marsvägledningens fotnot anger **01FS 2024:53**, medan läst primärföreskrift och Stockholms myndighetssida anger **01FS 2024:20**. Pröva hänvisningen mot primärkällan. Kontrollera också rättsligt datum, föreskrifternas tabell 1 och relevanta grafiska original manuellt. Källornas hämtdatum betyder inte att någon senare omvärldsbevakning har genomförts.

## 3. Övriga krav och granskningsobjekt

Objektgenomgången täcker exakt samma objektmängd som paketets mall: krav, paragrafkarta, hot, sårbarheter, kontroller, tjänster, lägre-risk-indikatorer, kontrollräckvidder, metodregler, riskmatris, skalmappning, sanktionsmetod och kundmetodens objekt. Sakuppgifter och motiveringar återges fullständigt. Varje objekt visar källa och öppen prövning samt vilka fasta fall det kan påverka. Oförändrade objekt ska också prövas för rätt paket och datum; äldre status är inte automatiskt ett aktuellt godkännande.

Tillsynsfacitet är negativt underlag från avgränsade tillsynsfall och inte ett universellt positivt facit. Dess mall, version och import är separata. Kundspårets objekt är egna förslag; deras förekomst betyder inte att resultatrapporten har en operativ kundriskmodell eller får presentera kundriskpoäng.

## 4. Rapportens disposition och samlade sakgranskning

| Kapitel | Innehåll att kontrollera |
|---|---|
| Faktaruta och 0 | Version, analysdag, status, läsanvisning, sammanfattning och risk per tjänst. Ingen samlad numerisk byrånivå. |
| 1 | Verksamhet, produkter, tjänster och omfattning från verkliga profilfält. |
| 2 | Hot och fulla erfarenhetsuppgifter med källor. |
| 3 | Alla indikatorer per område, lagens exempel, lägre-risk-tabell och endast belagd samverkan. |
| 4 | Aktuell bunden metod, scenariomatris, fulla lokala PT/TF-motiveringar, kontroller och avgränsning mot kundrisk. |
| 5 | Luckor, åtgärder, verkliga rutin-ID/versioner, uppföljning och versionslogg. |
| Bilaga A och B1 | Befintlig disposition; innehållet följer den aktuella analysen och regelbasen. |

Kapitel 3 skiljer på **finns**, **under tröskeln**, **nej**, **okänt** och **inte tillämplig**. Okänt får aldrig visas som nej. Lägre-risk-indikatorer har kolumnerna ”Kan tala för lägre risk i” och ”Prövning”; de beskrivs inte som hotförstärkare. Underlag saknas för numerisk nivå per område, antal kunder per riskklass och konstruerade rutinavsnitt. Rapporten redovisar dessa begränsningar. Samverkan visas endast där befintliga data ger stöd, exempelvis en belagd kombinationsgrupp; flera aktiva byråfaktorer är inte kundsamförekomst.

Fri text återges hel och gemensamma kedjor en gång. Oprövade eller inte godtagna sänkningar är markerade. V10 kräver samlad sakgranskning av hela huvudrapporten; enskilda R-godkännanden räcker inte och äldre poster utan granskningssätt räknas inte. A och B1 kan granskas var för sig. En formatändring kräver förnyad samlad sakgranskning. Redan fastställda V9-paket verifieras från sina frysta källor; de skrivs inte om. Vanlig uppdatering av ett äldre utkast behåller dess sparade format om användaren inte uttryckligen väljer byte.

De båda godkända syntetiska huvudrapporterna finns i paketet. Bilaga A/B1:s innehåll och källbindning har kontrollerats maskinellt, men varje bilagesida har inte granskats visuellt. Rapportgodkännandet här ersätter varken verklig sakkunniggranskning av regelbasen eller senare sakgranskning av en byrås rapport.

## 5. Lämna och importera beslut

Arbeta i en kopia av `granskningsmall.yaml`. Behåll paket, version, datum, kontrollsumma och samtliga objekt-ID:n exakt. Ange verklig granskare, kompetens, oberoende och granskningsdatum (tidigast underlagets datum). För **varje** objekt välj `verifierad` eller `ändras` och skriv en konkret kommentar. `ej_granskad`, tom kommentar eller saknade objekt avvisas vid import.

Vid `ändras`: ange vad som avslås, önskat alternativ, nödvändigt underlag och om ändringen påverkar källtolkning, tjänsteavgränsning, beräkning eller presentation. Ange vid metodavslag både D-ID och berörda genomförandeobjekt. Överför inte ett godkännande till nya bytes genom att själv ändra kontrollsumman i mallen.

Import görs av ansvarig efter genomläsning av den verkligt ifyllda filen:

```bash
.venv312/bin/riskanalys regelbas importera-granskning <ifylld-granskningsmall.yaml> --regelbas <regelbaskopia>
```

Importen validerar aktuell regelbas, paket/version/innehållssumma, rättsligt datum, exakt objektmängd och granskningsmetadata. Alla tre regionpaket måste ha sina egna aktuella beslut. Motstridiga aktuella beslut om gemensamma objekt stoppar berörda paket. Metadata i en YAML-fil bevisar inte kompetens eller identitet; det kontrolleras utanför programmet. Codex fyller inte i verkliga expertbeslut.

## 6. Återföring vid avslag eller ändring

1. Registrera `ändras` med motivering; fastställ inte med ett avslaget eller ogranskat objekt.
2. Använd `metod/beslut-och-beroenden.json` och D-postens `aterforing` för att hitta beroenden. Katalog-/frågeändringar går tillbaka till B, hotnivåer till C och metodändringar till D. Ett beslut kan avslås separat, men dess genomförande kan kräva ombyggnad av flera senare beslut.
3. Ändra i en ny regelversion. Bind om berörda sakobjekt och genomförandefiler. Ingen gammal attest får kopieras till ändrat innehåll. Alla D-beslut binder hela appfilinventariet och måste därför prövas på nytt vid ändrad appkod. Sakobjektsändringar ogiltigförklarar D-beslut som refererar objektet; de exakta referenserna finns i beroendefilen.
4. Räkna om samma frysta profilbytes. Redovisa varje sänkt eller borttaget scenarioled mot föregående steg och kumulativt mot 2.0.0, inklusive kontraster och nya tjänsters avsaknad av baslinje. Prova berörd kedja, snabbprofil och fullsvit på slutligt oförändrat snapshot.
5. En ändrad regelbas-/paketversion eller paketets innehållssumma kräver ny export och aktuellt granskningsbeslut för varje berört regionpaket. Gamla mallar importeras inte mot det nya innehållet. Oförändrade frysta historiska rapportpaket förblir historiska; nya rapporter måste bedömas, granskas och sakgodkännas på nytt.
6. Bygg om båda referensrapporterna när metod, utfall eller presentation påverkas. Läs deras faktiska PDF:er och gör förnyad samlad sakgranskning före export/fastställelse. Uppdatera guiden och expertpaketen efter den nya kontrollen.

## 7. Teknisk status

Slutlig fullsvit gav **3 557 godkända, 0 fel och 0 överhoppade**, med ett livetest bortvalt, matchande insamling/JUnit och 851 oförändrade snapshotresurser. Första körningens 3 522 godkända/34 fel, rättningarna och den gröna slutkörningen redovisas i [slutprovsunderlaget](superpowers/reviews/2026-10-23-regelbas-slutprov.md). Paketets sakstatus är fortfarande `ej_granskad`. Ingen push eller merge ingår.
