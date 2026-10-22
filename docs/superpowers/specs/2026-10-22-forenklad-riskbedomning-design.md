# Förenklad analys av byråns tjänster och sårbarheter

Designunderlag för implementation, revision 2, den 22 oktober 2026. Innehåller det reviderade chattförslaget, granskningen korrigerad i `9fedb6f` och användarens efterföljande granskning av revision 1. Revision 2 skiljer dokumenterad försiktigare motorbedömning från möjlig underskattning, anger manuell tjänsteanalys som fortsatt produktutveckling och förenar samlat tjänsteurval med planval per rad. Övriga godkända designdelar behålls. Produktändringarna är ännu inte implementerade.

## 1 Mål och avgränsning

Byrån väljer sina tjänster ur en standardkatalog, bekräftar tjänsternas faktiska innehåll och gör en gemensam sårbarhetsanalys. För varje tjänst prövar byrån sedan hur dessa förhållanden samverkar med relevanta hot och motiverar riskbedömningen för penningtvätt och finansiering av terrorism.

Gemensamt underlag beskrivs en gång och återanvänds med uttrycklig tillämpning per tjänst. Katalogtext ska vara synligt förslag tills byrån har bekräftat den. Osäkerheter följer med vid återanvändning. Ingen sammanvägd byrånivå införs och inget individuellt kund- eller uppdragsregister krävs.

Första leveransen ändrar analysstruktur, intag, rapport och planernas livslopp. Riskmotor, vikter, maxregel och kontrollavdrag behåller sin metod. D3, D5 och D9 samt andra verkliga metodbeslut ersätts inte av denna design. Egna tjänster utanför katalogen kan i denna leverans redovisas som en lucka men får ingen konstruerad motornivå. Att de tills vidare hindrar ett komplett fastställt paket är en känd produktbegränsning; fortsatt stöd genom manuell tjänsteanalys beskrivs i avsnitt 7.

## 2 Kontrollerad bas och källgräns

Produktbasen är `91a3ece` på `codex/kravstod-tjansteexponering`. Den har elva katalogtjänster, sexton lokala analysblock, gemensamma scenarier, deklarerade kombinationsgrupper och planer med genomföranderegistrering. Granskningen från `feat/steg-1-3` är bevarad som [granskningsunderlag](../reviews/2026-10-22-granskning-forenklad-struktur.md), korrigerad i `9fedb6f`. Senare chattkompletteringar är inarbetade här.

Rättsliga källor är PTL 2 kap. 1–2 §§ och tillämpliga länsföreskrifter, däribland 14FS 2024:11, 2 kap. 1–3 §§. [Länsstyrelsens vägledning](https://www.lansstyrelsen.se/vastra-gotaland/samhalle/betalning-ekonomi-och-pengar/forhindra-penningtvatt-och-finansiering-av-terrorism/gor-en-allman-riskbedomning.html) preciserar tjänstevisa risknivåer och sammanvägning av riskfaktorer. Vägledningen frågar även efter konsekvensernas storlek; programmets skala, fasta konsekvensvärden och riskmatris är metodval. Inget nytt obligatoriskt konsekvensfält införs utan en bestämd funktion i metoden.

Lag, föreskrift, vägledning, metodval och teknik ska märkas var för sig i den befintliga kravmatrisen. Designen är ett sätt att stödja analysen, ingen sakkunnigverifiering av regelbasen.

## 3 Tjänsteurval och beskrivning

Alla erbjudandeuppgifter startar som okända. Formuläret visar standardlistan och låter byrån välja bort tjänster och markera osäkra rader. En tydlig bekräftelse av hela urvalet kan sätta kvarvarande tjänster till erbjuds och bortvalda till erbjuds ej. Osäker sparas alltid som okänt, aldrig som ja. Inget förslag blir en bekräftad sakuppgift före denna handling.

Samlad bekräftelse kräver källa, datum och ansvarig funktion. Ett gemensamt underlag räcker när det faktiskt gäller hela urvalet; metadata sparas på varje uppgift med befintlig evidensmodell. Befintliga svar ersätts bara genom uttryckligt ändringsval, med revisionsskydd och atomisk sparning. Historiska nej och äldre alias får inte bli första kartläggning genom ett mellanliggande okänt svar.

Vid samlad bekräftelse identifierar formuläret de rader som innebär ett känt nej till ja och begär planval vid just dessa rader. Det ska behålla urvalet och gemensamma belägg medan användaren väljer plan, inte börja med att avvisa hela formuläret med ett generellt fel. En aktiv kandidat får föreslås men måste bekräftas; flera kräver uttryckligt val. Saknas giltig plan erbjuds vägen att registrera och utvärdera en plan samt återvända till urvalet. Efter ändrad profilrevision måste de bevarade valen jämföras med aktuella svar före sparning. Den särskilda rättelsevägen för felregistrerade nej behålls.

Själva erbjudandeändringarna och valda genomförandena sparas först när alla berörda rader är giltiga, i en atomisk transaktion. Webb och CLI skickar ett typat planval per tjänst till samma kärna. En direkt begäran med saknat/felaktigt val ska fortfarande avvisas utan delvis sparning. Övriga tjänsters bekräftelser får inte sparas tyst medan införanderaderna fallerar.

Katalogen kompletteras med källbundna förslag till arbetsmoment, möjliga befogenheter och relevanta kompletteringsfrågor. Befintliga tjänste-ID:n behålls. Innehållet är nytt katalogarbete; dagens korta beskrivningar räcker inte som färdigt tjänsteunderlag. Använd befintliga `P-TJ.*`-fält för byråns faktiska arbetssätt, attest, mandat och insyn där de räcker. En standardbeskrivning är aldrig belägg för att byrån utför ett visst moment.

Första kartläggningen skiljs från ett nytt införande. Ett senare känt nej till ja följer planreglerna i avsnitt 9.

## 4 Gemensam analys och tillämpning per tjänst

### Gemensamma poster

Utöka `Analyspaket` med `gemensamma_sarbarhetsprovningar`, enligt mönstret för gemensamma scenarier. En post har stabilt ID, område, beskrivning av svagheten, bakomliggande riskfaktorer/profilreferenser, katalogsårbarheter, hotkopplingar, dimension PT/TF/båda, motivering, belägg och status bekräftad/antagande/kunskapslucka. Utkast får vara ofullständiga; godkännande kräver fullständig sakprövning.

De gemensamma områdena är kunder, kanaler, geografi och egen verksamhet. Tjänstens egenskaper prövas vid tjänsten. Alla områden ska vara uttryckligt behandlade i det sammanställda underlaget; inga funna sårbarheter i ett område dokumenteras med skäl och belägg i stället för att området utelämnas. Förifyllning från katalog/profil är ogranskat förslag och begränsas inte till redan aktiverade motorfaktorer.

Leverantörer, egen erfarenhet och sanktionsanknytning beskrivs i en typad gemensam verksamhetsdel i `Analyspaket`. Befintliga strukturer för leverantörsprövning och belägg återanvänds; dessa uppgifter ska inte pressas in i en sårbarhetsbeskrivning eller lagras som enbart rapporttext. Tjänsten får uttryckliga innehållsbundna tillämpningar av respektive del, enligt samma bekräftelsemönster som sårbarheterna. Dess faktiska omfattning, betydelse och avvikelser prövas fortfarande vid tjänsten. Gemensamma poster använder samma beläggsregister; källor och bekräftade sakuppgifter dupliceras inte.

### Tjänstens tillämpningar

Utöka `Tjansteanalys` med `sarbarhetstillampningar`. Varje tillämpning innehåller gemensamt post-ID, ställningstagande, motivering, belägg, refererad posts innehållssumma och uttrycklig bekräftelse. Ställningstaganden är `galler`, `galler_annorlunda`, `beror_inte` och `otillrackligt`.

Varje gemensam post ska få ett ställningstagande i varje erbjuden tjänst. Detta förhindrar att egenidentifierade förhållanden försvinner för att katalogen saknar en koppling. Avvikelser, berör inte och otillräckligt kräver individuell motivering; berör inte kräver även belägg. Tjänstespecifika sårbarheter behålls i tjänstens befintliga `sarbarhetsprovningar`.

Användaren kan markera flera synliga poster som gäller enligt gemensam analys och bekräfta dem i en atomisk sparning. Samlad bekräftelse får bara sätta `galler`; den får inte skriva över befintliga avvikelser eller osäkerhetsval. Ändrad post/revision mellan visning och sparning kräver omläsning.

Bekräftelsen gäller tillämpningen, inte sanningshalten i ett antagande. Den gemensamma postens status följer med till varje tjänst och visas i formulär och rapport. Otillräckligt underlag får inte döljas av en samlingsmening. Kvarstående osäkerhet måste hanteras enligt befintliga regler före godkännande.

## 5 Samverkan och motorutfall

Tjänstens samverkan, PT-/TF-motivering och slutsats bygger på gemensamma poster, tillämpningar och lokala förutsättningar. Byråns alla kundgrupper, leveranssätt och geografiska anknytningar antas inte automatiskt förekomma i varje tjänst. Befintliga fördelningar och kombinationsgrupper används där de behövs för slutsatsen; nya obligatoriska kundregister eller standardkrav på alla antal införs inte.

`beror_inte` eller `galler_annorlunda` ändrar inte motorutfallet före ett metodbeslut. Avvikelsen dokumenteras med tjänst, faktor, berörda hot/scenarier, PT/TF, riktning, motivering och belägg. Användaren ska kunna ange vad som faktiskt gäller utan att behöva bekräfta en felaktig tillämpning för att få fastställa.

| Riktning | Hantering före metodbeslut |
|---|---|
| Byråns prövning innebär lägre risk; motorn är försiktigare | Synlig avvikelse med motivering, belägg och sakgranskning. Motorns högre nivå används fortsatt. Avvikelsen i sig spärrar inte godkännande eller fastställelse. |
| Byrån identifierar högre eller ytterligare risk som motorunderlaget inte täcker | Befintlig öppen `Analysgap` av typen `metodkonflikt` spärrar godkännande och därmed fastställelse. |
| Riktningen är oklar, underlaget är otillräckligt eller olika delar pekar åt olika håll | Registrera relevant öppen kunskapslucka/metodkonflikt och klarlägg före godkännande. |

Riktningen prövas för berörda hot/scenarier och dimensioner, inte enbart genom att jämföra tjänstens sammanfattande nivå. En hög motorbedömd PT-risk får exempelvis inte dölja ett TF-hot som modellen inte täcker. En egen sårbarhet utan katalogkoppling ska alltid få ett uttryckligt ställningstagande till om risken täcks; en allmänt hög motornivå är inte ensam belägg för täckning.

Den icke blockerande avvikelsen lagras som en innehållsbunden upplysning i den typade tjänstetillämpningen, inte som en öppen eller accepterad `Analysgap`. Att kalla en faktisk underskattning försiktigare motorutfall får inte undanta den från prövning. Ändrad gemensam post, tillämpning eller motorbedömning kräver ny kontroll av riktning och nya giltiga godkännanden enligt avsnitt 8.

Rapporten anger vilken faktor byrån anser inte berör tjänsten, skälen/beläggen och att motorns nivå används tills metoden har ändrats. Motorns använda nivå ligger också till grund för riskstyrda åtgärder; den lägre bedömningen i fritext får inte leda till en tyst sänkning av vare sig nivå eller åtgärder.

Befintliga spärrar mot obelagda kontrollavdrag, okänd effekt och andra brister behålls. En upplysning om försiktigare motorutfall får inte åsidosätta dem. En verklig blockerande konflikt får inte försvinna genom statusbyte till åtgärdad; den bakomliggande bristen måste vara rättad eller ett dokumenterat metodbeslut genomfört i reglerna och ny bedömning gjord. Metodkonflikt får inte godtas som accepterad kvarstående kontrollrisk. Ingen parallell spärrmekanism införs.

## 6 Fördelning av befintliga analysblock

| Block | Hantering |
|---|---|
| 1–4 Exponering, arbetsmoment, betalningsinsyn, uppdragsprövning | Kvar per tjänst. |
| 5 Leverantörer | Gemensamt grundunderlag och analys; tillämpning/avvikelser per tjänst. |
| 6 Scenarier | Befintliga gemensamma scenarier och tjänstekopplingar återanvänds. |
| 7 Sårbarheter | Gemensamma poster plus tillämpningar och tjänstespecifika poster. |
| 8 Samverkan | Kvar per tjänst med hänvisningar. |
| 9 Egen erfarenhet | Gemensam analys; betydelse/avvikelser per tjänst. |
| 10–12 Kontroller, luckor, reduktion | Kvar per tjänst med befintliga effekt- och reduktionskrav. |
| 13–14 PT och TF | Kvar per tjänst. |
| 15 Sektor och sanktioner | Gemensam sanktionsanknytning; tjänstens tillämpning och sektorsjämförelse kvar. |
| 16 Slutsats och åtgärder | Kvar per tjänst. |

Formulär, validering och blocksummor ändras tillsammans. `_sarbarheter` ska pröva den gemensamma analysen tillsammans med tillämpningen och lokala poster, inte kräva att gemensam text skrivs igen. Att dölja obligatoriska gamla fält uppfyller inte designen.

## 7 Tjänster utanför katalogen

Första leveransen erbjuder ingen fri motorberäknad tjänst. Byrån ska ändå kunna ange att katalogen inte täcker allt och beskriva vad som saknas. Återanvänd `P-BESK.ovriga_forhallanden` och `P-BESK.ovrigt` som underlag och förtydliga att tjänster utanför katalogen omfattas. Saknat eller osäkert besked får inte presenteras som bekräftat komplett urval.

Luckan ska synas i intagets omfattningsöversikt, kravmatrisen och rapportens omfattningsavsnitt. Ett uttryckligt ofullständigt granskningsutkast kan redovisa katalogluckan och kända tjänsters underlag; den saknade tjänsten får ingen påhittad nivå. I första leveransen följer omfattningshindret med till granskning och fastställelse. Befintlig spärr mot komplett dokumentgenerering får inte kringgås generellt för andra okända riskförhållanden. Genomförandeplanen ska ange den avgränsade vägen för detta granskningsutkast och prova hindret genom hela kedjan.

Spärren är en produktbegränsning i den första leveransen, inte ett lagkrav på motorberäkning eller ett permanent förbud mot att fastställa bedömningar av egna tjänster. [PTL 2 kap. 1–2 §§](https://data.riksdagen.se/dokument/sfs-2017-630.html) kräver bedömning och dokumentation; bestämmelsen om modellriskhantering i 6 kap. 1 § gäller när modeller används. Programmets val av motor ska inte framställas som en föreskriven enda arbetsmetod.

Den fortsatta lösningen är ett uttryckligt, versionsbundet spår för manuell tjänsteanalys. Det ska omfatta tjänstens bekräftade innehåll, relevanta kataloghot och identifierade sårbarheter, gemensamma faktorers betydelse, PT/TF, motiverad risknivå, underlag, författare och daterad sakgranskning. Kontroller och deras effekt behöver prövas om de används för att motivera kvarstående risk. Hot som katalogen inte kan beskriva får inte döljas; där behövs kompletterat analysstöd.

En sådan nivå märks ”Manuell bedömning – ej motorberäknad” i rapport, underlag och beslut. Den är byråns uttryckliga, granskade bedömning och ska inte lagras eller presenteras som motorutfall. AI sätter ingen nivå. Manuell analys följer en dokumenterad metod och samma krav på fullständighet, spårbarhet, aktualitet och godkännande; den är ingen generell väg för att skriva över katalogtjänsters motorresultat. Det spåret ska, när det är implementerat och verifierat, göra det möjligt att fastställa ett komplett paket även med tjänster utanför motorkatalogen. Det byggs inte i första leveransen och registreras som en kvarstående produktuppgift i kravmatrisen.

## 8 Rapport och godkännanden

D-ARB.5 redovisar katalogens mekanism och byråns gemensamma analys tillsammans, med separerad proveniens. De ska inte bilda två upprepade faktorlistor. Tjänstens text visar avvikelser, osäkerheter, lokala sårbarheter och samlad riskmotivering. En kort hänvisning anger vilka övriga poster som uttryckligen gäller oförändrat. B1 behåller fullständiga ursprungliga svar, referenser och motorberäkningar.

Rapporten ska skilja motorutfall från byråns tillämpning och synligt visa såväl icke blockerande avvikelser med försiktigare motorutfall som blockerande metodkonflikter. PT och TF behandlas; befintlig sanktionsprövning hålls separat. V8:s läsrapport och B1 behålls som leveransstruktur; ingen ny rapportversion införs enbart för omdisponeringen. Ändrade producent- och analyskontrakt ska vara versionsbundna så att äldre paket inte omtolkas.

En ändrad gemensam post gör dess tillämpningar inaktuella genom innehållssumman. Analysbeslut behåller i första leveransen dagens bindning till hela paketets revision, underlagssumma och svarssumma: alla tjänsters beslut blir inaktuella när paketets svar ändras. Selektiv förnyelse ingår inte. Tillämpningsbekräftelse, blockbekräftelse, analysbeslut och sakgranskning är skilda kontroller och får inte likställas.

## 9 Återkallade planer och uttryckligt införandeval

På produktbasen kan en övergiven plan spärra ett senare införande. Om flera nya-tjänst-planer utvärderas markerar erbjudandeövergången alla som genomförda. Detta är reproducerat med syntetiska uppgifter och ska rättas separat före strukturändringen.

Planens logiska tillstånd är aktiv, genomförd eller återkallad. Befintligt `genomforande` behålls och kompletteras med en valfri typad `aterkallelse`. Tomt nytt fält utelämnas i äldre serialisering. Återkallelsen innehåller datum, ansvarig, motivering, profilrevision före registreringen och innehållssumma för bevarat planinnehåll. Genomförande och återkallelse får aldrig finnas samtidigt.

| Från | Till | Villkor |
|---|---|---|
| Aktiv | Genomförd | Uttryckligt planval och giltig bunden utvärdering; övriga införandekrav gäller. |
| Aktiv | Återkallad | Faktiskt återkallande med datum senast idag, ansvarig och motivering. |
| Återkallad | Genomförd eller återkallad igen | Förbjudet. |
| Genomförd | Återkallad | Förbjudet. |

Återkallade och genomförda poster är oföränderlig historik. De får inte tas bort, återöppnas eller ändras/importeras genom vanlig plansparning. En ny avsikt kräver ett nytt plan-ID. Befintliga utvärderingar bevaras i historiken, men utvärderingar av återkallade planer kan inte bära ett införande eller räknas som aktuell planutvärdering. Ingen ny utvärdering/genomföranderegistrering får göras mot en återkallad plan. Årsfristen för hela bedömningen förblir separat.

Vid ett nytt införande som kräver plan enligt avsnitt 3 ska byrån uttryckligen välja den aktiva plan som genomförs för tjänsten. Den första kartläggningen av befintliga tjänster får inte bli ett planpliktigt införande enbart för att ett okänt svar bekräftas. Exakt en aktiv kandidat får föreslås, men måste bekräftas. Vid flera kandidater krävs val; inget implicit första-ID och ingen automatisk genomförandemarkering av alla planer. Fel tjänst, fel plantyp för införandet, inaktiv plan, saknad/inaktuell utvärdering och saknat val ger åtgärdbara fel.

Vid samlat tjänsteurval följer varje införanderads planval med till samma atomiska sparning enligt avsnitt 3. Ändringar av andra rader, okända svar, gemensam källa och planval ska bevaras genom formulärets kompletteringssteg. Planval efter ändrad profilrevision får inte baseras på den gamla sidans kandidater utan omläsning och jämförelse.

Ej valda planer blir inte genomförda. De förblir aktiva och omfattas av befintliga prövningskrav; planer som inte längre avses ska återkallas uttryckligen. Denna rättning upphäver inte övriga aktiva förändringsplaners krav vid fastställelse. För redan erbjuden tjänst behålls det uttryckliga genomförandeflödet med valt plan-ID.

Webb och CLI använder samma kärna. Återkallelse och genomförande sparas atomiskt med profilen, under befintlig låsordning och CAS. Avbruten sparning lämnar ingen falsk avslutshändelse. Datum, innehållssummor och gamla historikposter bevaras; terminal historik kontrolleras inte mot senare byråfakta. Planval och återkallelse är privata och tillförs inte AI-underlaget.

## 10 Överföring och bindningar

Äldre fastställda paket behålls oförändrade och verifieras med sina ursprungliga manifest. Äldre analysregister med schemaversion 1 läses med sitt befintliga kontrakt; tomma nya fält ändrar inte deras serialisering. Ny analys enligt denna struktur använder schemaversion 2, så att den sammanställda områdesprövningen skiljs från den äldre. Överföring från 1 till 2 är en uttrycklig handling. Ingen tyst överföring av äldre godkännanden eller ommärkning av historiska format.

Ett uttryckligt hjälpflöde får föreslå gemensamma poster från identiska äldre texter. Identisk text räcker inte för att slå ihop olika belägg, perioder, dimensioner eller motsägande relevansbedömningar. Förslag är obekräftade och överför inget författarskap/godkännande. Ursprungliga uppgifter bevaras tills användaren har granskat förslaget. Vid övergång krävs aktuell bindning och nya bekräftelser, analysbeslut och sakgranskningar.

Ändrad katalogdata ändrar regelbasens kontrollsumma; ändrad `profil.modeller` ingår i modellidentiteten. Leveransen får därför inte utlova oförändrad modellbindning trots att `analys.*` ligger utanför modellfilförteckningen. Uppgraderingsinformationen ska ange vad som behöver förnyas för nya beslut. Historiska attester märks aldrig om.

## 11 Acceptanskriterier för genomförandeplanen

1. Tjänsteurvalet sparar osäker som okänt och bär källa, datum och ansvarig på varje uppgift även vid samlad bekräftelse. Första kartläggning och nytt införande skiljs åt; historiskt nej kan inte kringgås. Planval begärs vid just införanderaderna och hela urvalet/beläggen bevaras. Fel val, avbrott och revisionskonflikt lämnar inga delvis sparade erbjudanden eller genomföranden.
2. En gemensam beskrivning kan användas av flera tjänster utan duplicerad text, men varje post får uttrycklig tillämpning och alla områden täcks på den sammansatta nivån.
3. Samlad tillämpning kan bara sätta gäller; avvikelser bevaras och antaganden/kunskapsluckor syns i varje berörd tjänst. Stale revision/postsumma kan inte bekräftas.
4. Berör inte ändrar ingen risknivå före metodbeslut. En belagd avvikelse där motorn är försiktigare kan sakgranskas och fastställas med motorns nivå och synlig avvikelse, utan att byrån behöver ange gäller. Möjlig underskattning eller oklar riktning ger befintlig öppen lucka/metodkonflikt. Prova även blandade PT/TF-förhållanden, nya sårbarheter utan katalogkoppling, obelagda kontrollavdrag och försök att kringgå en kvarstående brist genom statusbyte.
5. Tjänst utanför katalogen syns som omfattningslucka i översikt, rapport och kravmatris. Första leveransens fastställelsespärr märks som känd produktbegränsning och fortsatt manuell analys som uppskjuten produktuppgift. Ingen befintlig funktion får framställas som stöd för en ännu inte implementerad manuell nivå.
6. Rapporten redovisar gemensam analys en gång, lokala avvikelser och faktisk riskmotivering. Mät läsrapport, B1 och total samt upprepning före/efter för samma frysta provfall. Förbättring av totalmåttet får inte skapas genom enbart flytt till B1.
7. Äldre bytes, tolkning och fastställda paket bevaras. Förslag vid överföring är obekräftade; inga beslut följer med. Ändrad gemensam analys gör nuvarande paketbeslut inaktuella enligt befintligt kontrakt.
8. Utöka planregressionen med att en återkallad plan inte spärrar ett nytt giltigt införande och att bara vald plan blir genomförd. Prova även alla förbjudna övergångar, bevarad historik/årsfrist, flera kandidater utan val, stale revision och skrivavbrott genom gemensam kärna samt webb/CLI.
9. Hela AI-begäran inklusive omförsök är oförändrad av privat gemensam analys, tillämpningar, återkallelse och planval. Risknivåer får inte skapas ur fritext.
10. Godkänd teknisk verifiering använder Python 3.12, syntetiska uppgifter och testleverantör. Regelbasvalidering, relevant fullsvit, historiska kontrakt och riktad visuell exportkontroll ingår före produktleverans. Sakkunnigstatus ändras inte av testerna.

## 12 Föreslagen genomförandeordning

Rätta först planernas återkallande och införandeval med reproducerande regressioner. Följ därefter tjänsteurval/katalogförslag, gemensam analys och tjänstetillämpning, samlad bekräftelse, validering och befintliga metodkonflikter, rapport/omfattningslucka samt uttrycklig överföring och slutprov. Skapa inte en parallell motor eller ett nytt godkännandesystem. Metodbesluten hanteras separat och ska vara synligt öppna i kravmatrisen.
