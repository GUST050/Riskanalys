# Del 3 – V10-förslag för PDF-läsning

V10 är byggt offline enligt användarens uttryckliga **”1 på alla”** den 23 oktober 2026. Områdena får full motivering utan nytt nivåord, kundriskklassraden utelämnas, rutiner hänvisar till faktiskt dokument/ID och version, och samverkan begränsas till befintligt belagt underlag. **Noll nya intagsfrågor.**

Detta är kontrollpunkt 2, inte en färdig produktleverans. Export, samlad sakgranskning, fastställelse och standardformat är inte ändrade till V10. V9 är fortfarande produktstandard. C:s regelbas 2.2.0 är oförändrad; D:s metodbeslut är ännu inte genomförda. Inga verkliga AI-anrop, ingen push och ingen merge har gjorts.

## PDF-filer att läsa

| Referensfall | Resultatrapport | Bilaga A | Bilaga B1 | Ofiltrerade maskinfynd |
|---|---|---|---|---|
| Fyra tjänster | [19 sidor](../../../.superpowers/evidens/2026-10-23-rapport-v10-prov10/fyra_tjanster/pdf/allman-riskbedomning-UTKAST.pdf) | [37 sidor](../../../.superpowers/evidens/2026-10-23-rapport-v10-prov10/fyra_tjanster/pdf/analysbilaga-UTKAST.pdf) | [195 sidor](../../../.superpowers/evidens/2026-10-23-rapport-v10-prov10/fyra_tjanster/pdf/underlagsbilaga-UTKAST.pdf) | 430 |
| Med betalningsmandat | [20 sidor](../../../.superpowers/evidens/2026-10-23-rapport-v10-prov10/med_betalningsmandat/pdf/allman-riskbedomning-UTKAST.pdf) | [41 sidor](../../../.superpowers/evidens/2026-10-23-rapport-v10-prov10/med_betalningsmandat/pdf/analysbilaga-UTKAST.pdf) | [203 sidor](../../../.superpowers/evidens/2026-10-23-rapport-v10-prov10/med_betalningsmandat/pdf/underlagsbilaga-UTKAST.pdf) | 440 |

**Riktmärket tio sidor är inte uppnått.** Det första layoutprovet gav 27 sidor i fyrtjänstfallet. Gemensamt period-/källregister, anpassade kolumnbredder, kompakta matristabeller och gemensam händelsekedja över PT/TF har minskat längden. Brödtexten är fortfarande 11 punkter och tabelltexten minst 9,5. Alla valda fria motiveringar och nya tabellrader är kvar. Uppdragets acceptans anger att innehållet har företräde och att inget ska kapas för sidmålet; avvikelsen lämnas därför synlig för användarens läsning.

Word-filer, frysta källor, byggunderlag, konstruktioner, granskningskontext, fulla fyndlistor, innehållskontroller, sidbilder och PDF-kontroller finns i samma fallmappar under `.superpowers/evidens/2026-10-23-rapport-v10-prov10/`.

## Disposition och sakgränser

- Faktaruta och kapitel 0–5 med verksamhets-/tjänstefakta, hot, alla områden, metodmatriser, scenario-/tjänstemotivering, kontroller, åtgärder, rutiner och historik.
- Samtliga **33 högre-risk-indikatorer**, **fem lägre-risk-indikatorer** och **15 lagexempel** finns som egna rader. Okända, inaktuella, periodfelaktiga och motstridiga data blir inte nej. Ett konservativt motorpåslag presenteras inte som belagd förekomst.
- PTL 2:5 p. 5–6 har okänd status för det snävare hemvistexemplet när bara programmets bredare anknytningsfråga finns. Den bredare faktorns egen status visas separat i hänvisningen. Hemvist utreds inte genom antagande.
- Lägre risk har egen tabell med ”Kan tala för lägre risk i” och ”Prövning”. Saknat centralt landunderlag syns, och aktuell katalog anger ingen nivåeffekt.
- S-KOMB-01 beskrivs som modellkombination på byrånivå. Marginaltal görs inte till påståenden om samma kunder. Belagda kombinationsgrupper kan återges; felaktigt gruppunderlag märks okänt.
- Hela utvalda PT-/TF-motiveringar bevaras. Samma källmekanism som används för båda dimensionerna återges en gång med separata sannolikheter och konsekvenser. Scenario-ID:n R4-/R5- behålls som identiteter; kapitelhänvisningar går till den nya dispositionen, till exempel 4.3.4.
- Skalor, båda matriserna och metodförklaringarna läses från den bundna regelbasen. Ingen fast rapportsats bestämmer att framtida kvarstående TF måste saknas. Nuvarande saknade motorvärde visas som saknat beräknat värde i respektive cell.
- Inga kundriskpoäng eller nya åtgärdskrav per nivå har införts. Saknade organisations-/registreringsuppgifter och särskilt dokumentansvar visas som okända.

## Källor och konstruktion

V10 återanvänder hela V8-analysen och generiska frysta käll-/urvalstyper. Bilaga A/B1 har samma avsnitts-ID, ordning och saktext som ett V9-bygge från **exakt samma källor**, med endast den nya formatstämpeln. Detta är kontrollerat objekt för objekt; gamla V9-byggare och V9-laddare har inte skrivits om.

Varje huvudstycke och datacell har källreferens med pointer och kontrollsumma samt konstruktionsslag: programmall, lokalt original eller regelbas. De två fallen har 695 respektive 713 konstruktioner. Alla deras källpekare är upplösta och kontrollerade. Frysta presentationer binder även konstruktionsinnehåll, vyer, fynd, åtgärder och renderingspolicy.

Referensverktyget läser befintligt sparat skrivutkast, bedömningsprofil, analysens snapshot, historik och eventuell verifierbar modellrapport från de syntetiska fallen. Full filgranskningskontext, inklusive 206 respektive 211 analysfilbrister, följer med till den ofiltrerade granskningen. Den tidigare förenklade förhandsvisningskontexten används inte i filerna ovan.

## Utförd kontroll och kvarstående verifiering

Utfört under bygget:

- Import-/syntaxkontroll av V10-moduler och skrivna regressionsprov samt `git diff --check`.
- Återbyggnad mot samma källor: **0 presentationsfynd i båda fallen**.
- Alla tre Word-delars stycken och dataceller motsvarar den frysta presentationskällan; hela PT-/TF-motiveringar bevaras. H-03:s gemensamma mekanism återges en gång i huvudrapporten.
- A/B1 jämförda mot V9 från samma källor: identisk disposition och saktext efter att enbart formatversion uteslutits.
- Båda huvudrapporterna renderade till sidbilder och granskade på kontaktark; särskild detaljkontroll av lagexempel och scenariomatris/hänvisningar. Inga ord utanför PDF-sidornas gränser upptäcktes. Alla sex PDF:ers faktiska sidantal är mätta.
- A/B1 är renderade och innehållskontrollerade; bilagornas samtliga PDF-sidor är **inte** fullständigt visuellt granskade i detta arbetssteg.

Regressionsprov är skrivna för faktastatus, ofullständiga/motstridiga data, hemvist, disposition, fria original/rollklamrar, källpekare, metodversion, V9-bevarande, programhänvisningar och manipulerad fryst presentation. **Pytest, snabbprofil och fullsvit har inte körts i detta steg**, enligt användarens instruktion att samla testerna till slutet. Ingen grön slutverifiering eller fullständigt verifierad historisk V8/V9-produktkedja påstås.

## Beroenden och nästa kontrollpunkt

Tillkommande V10-filer ligger i dokumentlagret, `granskning/dokument_v10.py` och offlineverktyget. Befintliga `dokument/modeller.py` och `rapportversion.py` accepterar den nya typen; gemensam literalhantering känner igen V10. Befintliga format behåller sina tidigare serialiseringsgrenar. Inga motorfiler, regelobjekt, AI-tillåtelselistor eller intagsfält har ändrats i rapportsteget.

Vid ändrat dataval behöver berörd tabellbyggare, konstruktioner, presentationer, PDF:er och deras samlade sakgranskning byggas om. Ett framtida metodbeslut i D kräver nya rapporter från dess regelversion och den föreskrivna slutkontrollen före E.

Nästa steg kräver användarens uttryckliga PDF-klartecken enligt uppdragets kontrollpunkt 2–3. Efter läsningen kan produktkedjan anpassas, sedan genomförs D, nya referens-PDF:er lämnas och sist E med samlad slutverifiering. Ingen push eller merge.
