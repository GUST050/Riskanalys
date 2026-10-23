# E färdigt för granskning – ny fullsvit pågår

Regelbas **2.12.2**, kodcommit `508f8c6`. Användaren har godkänt båda referens-PDF:erna efter D och gett klartecken till E. [Guiden](sakkunniggranskning.md) och [tre sakkunnigpaket](superpowers/reviews/2026-10-23-regelbas-steg-e.md) är färdiga: 276 obesvarade objekt, 526 manifestbundna filer, 244 appfiler, tolv fasta profiler, 40 kontrastprofiler och sex referens-PDF:er per region. Samlad C–E-review klar, inga kvarstående E-fynd. Alla regelobjekt fortsatt `ej_granskad`.

Första fullsviten: **3 522 godkända/34 fel**, collection/JUnit matchar och snapshot oförändrat. Två produktfel och äldre testfixturer/förväntningar rättade; inga produktspärrar lättade. Senaste riktade prov: **68 godkända/42,55 s**, historiska gyllene bytes + V10/export **3 godkända/23,57 s**, komplett webbintag **1 godkänt/215,28 s**. Snabb3: **140 godkända/67,213 s**, collection/JUnit matchar och snapshot oförändrat. **Full2 pågår på exakt 508f8c6; inget grönt slutbesked ännu.** [Slutprovsunderlag](superpowers/reviews/2026-10-23-regelbas-slutprov.md).

Nya huvud-PDF:er 20/21 sidor, A38/40 och B1195/200. Saktext exakt som godkänd utom versionsangivelse; ändrade sidor omkontrollerade visuellt. Tolv fasta profilvarianters scenarioled oförändrade mot D-slut. Ingen push eller merge.

## Föregående arbetsstatus

# D genomfört som förslag – PDF-slutkontroll och testning

V10-produktanpassningen är sparad som `8abd6d9`. D1–D9 och lägre-risk-beslutet har egna arbetscommits/regelversioner, nu **2.12.0**. Alla förslag är `ej_granskad`. [Samlat D-underlag med sänkningar och beroenden](superpowers/reviews/2026-10-23-metodbeslut-samlat.md).

Nya referens-PDF:er efter D: **20/21 sidor**, A **38/40**, B1 **195/200**, maskinfynd **430/432**, 0 presentationsfynd. Innehåll/källor/manifester kontrollerade och huvudrapporterna visuellt genomgångna. Användarens föreskrivna slutkontroll har begärts före steg E. Samlade riktade tester pågår; snabb/full återstår. Ingen push/merge eller grön slutleverans påstås.

## Föregående arbetsstatus

# V10 godkänt för produktintegration

Användaren har godkänt båda referensfallens PDF-förslag (första alternativet: ”Godkänn rapportförslaget”). V10 kopplas nu till granskning, export, samlad sakgranskning och fastställelse. Nya rapporter använder kapitel 0–5. Befintliga V8/V9-utkast behåller sparat format vid vanlig uppdatering; byte till V10 är uttryckligt och kräver förnyad samlad sakgranskning. Historiska V9-vägar är bevarade.

Godkänt offlineunderlag: huvudrapporter **19/20 sidor**, A **37/41**, B1 **195/203**, ofiltrerade maskinfynd **430/440**. Riktmärket tio sidor är inte uppnått; innehållet är bevarat. Regressioner skrivs med ändringarna och körs vid slutet enligt användarens instruktion. Ingen grön fullsvit påstås.

**Fortsatt ordning:** produktintegration, D, nya referens-PDF:er för användarens slutkontroll, sedan E och samlad verifiering. Ingen push eller merge.

## Föregående arbetsstatus

# V10 offlineförslag – inväntar PDF-läsning

Användaren valde första alternativet i alla fyra rapportfrågor. V10 är byggt offline med disposition 0–5, 33 indikatorer, fem lägre-risk-rader och 15 lagexempel. Noll nya frågor eller verkliga AI-anrop. Regelbas 2.2.0 och motorn är oförändrade. **V9 är fortfarande produktstandard.**

[PDF-filer och granskningsunderlag](superpowers/reviews/2026-10-23-rapport-v10-offline.md): huvudrapporter **19/20 sidor**, A **37/41**, B1 **195/203**, ofiltrerade maskinfynd **430/440**. Riktmärket tio sidor är inte uppnått; innehållet är bevarat. Bygg-/käll-/Word-kontroll passerar och huvudrapporternas sidlayout är genomgången. Skrivna regressioner, snabbprofil och fullsvit väntar till samlad slutverifiering enligt användarens instruktion. Ingen grön fullsvit påstås.

**Nästa steg:** användaren läser de två huvudrapporterna enligt uppdragets kontrollpunkt 2. Efter PDF-klartecken: produktintegration, D, nya PDF:er och E. Ingen push eller merge.

## Föregående arbetsstatus

# Steg C genomfört – fortsatt rapport- och metodarbete

B sparat lokalt som `902da79`. C föreslår regelbas **2.2.0**: samtliga 26 hot har lästa källcitat, precisa sidor och en uttrycklig notering om att underlag för annan hotnivå saknas. Medel behålls; samtliga 27 erbjudna tjänsteutfall i sex fasta syntetiska fall är identiska med B. Alla objekt är `ej_granskad`.

[C:s käll- och effektunderlag](superpowers/reviews/2026-10-23-regelbas-steg-c.md). [Datatäckningsinventeringen för hela den nya rapporten](superpowers/reviews/2026-10-23-rapport-datatackning.md) är klar och de fyra föreskrivna användarvalen har ställts. Ingen rapportkod har byggts före dessa val. [V10-planen](superpowers/plans/2026-10-23-rapport-v10.md) anger formatgräns, källbindning, offlinebygge och produktintegration efter PDF-kontroll. [Förberedelsen inför D](superpowers/reviews/2026-10-23-steg-d-forberedelse.md) kartlägger varje metodfrågas genomförande, kontraster och följdberoenden; inga D-beslut är ännu genomförda.

Användaren har gett klartecken att fortsätta C, del 3, D och E och samla testerna till slutet där möjligt. Nödvändiga käll-/bygg-/katalogkontroller görs löpande; regressioner skrivs och körs samlat senare. **Ingen grön fullsvit eller slutleverans påstås. Ingen push eller merge.** PDF-kontrollpunkterna hanteras när konkreta filer finns.

## B – tidigare arbetsredovisning

# Regelbasen steg B – arbetssteg för granskning

Steg A (`48991af`) är godkänt av användaren. Katalogkompletteringen i B är genomförd lokalt som förslag i regelbas **2.1.0**: två nya tjänster, fem nya hot, fem nya högre-risk-indikatorer, snävare distansvillkor och fem separata lägre-risk-indikatorer utan nivåeffekt. **56 nya intagsfält, 324 → 380.** Trust/nominee ger synligt fastställelsestopp men utkast kan skapas. Alla katalogobjekt har `ej_granskad`.

[Granskningsunderlag med källor, frågeantal, beroenden, före-/efterutfall och redovisade sänkningar](superpowers/reviews/2026-10-23-regelbas-steg-b.md). Fyra betydelsefulla granskningsfynd är rättade och reproducerande prov passerar. Senaste riktade urval: **72 godkända/10,66 s**. Katalog- och diffkontroll passerar. Snabbprofil: **140 godkända/51.480 s**, matchande collection/JUnit och 820 oförändrade snapshotresurser.

**Fullsviten är ännu inte grön.** Senaste körningen stannade efter 1 504 godkända och ett fel i ett historiskt AI-begärandeprov. Dess katalogbindning är nu rättad, med oförändrade gyllene request-hashar och grönt riktat prov. B är en arbetscommit och ett granskningsunderlag; färsk grön fullsvit på exakt slutlig kod krävs före slutleverans/PR/merge. Ingen push eller merge.

**Användaren har därefter gett klartecken att fortsätta samtliga återstående steg.** Ordning: C, del 3, D, förnyad PDF-granskning och sist E. Testerna samlas till slutet i den mån arbetet kan fortsätta utan dem. Del 3:s uttryckliga val av datatäckning och PDF-kontrollpunkter hanteras med konkreta underlag. Ingen ny rapportdisposition eller metodkalibrering har byggts i B.

## Godkänt steg A – tidigare redovisning

# Regelbasen steg A – inventering för granskning

Användaren har godkänt del 1 (`654066f`) och uttryckligen gett klartecken till del 2 steg A, enbart dokumentation. [Luckförteckningen](superpowers/reviews/2026-10-23-katalogluckor.md) jämför katalogerna med PTL 2:1–5, de tre regionala föreskrifternas 2 kapitel, marsvägledningen, Länsstyrelsens webbvägledning samt relevanta delar av nationell riskbedömning och registrerade lägesbilder. Alla 15 lagexempel och vägledningens tjänster/modus har motsvarighet, kompletteringsförslag eller uttrycklig avgränsning.

Förslaget redovisar fem nya högre-risk-indikatorer, ett distansförtydligande, fem lägre-risk-indikatorer utan automatisk sänkning, tre konkreta modusförslag och fyra möjliga nya tjänstegrenar. Frågeförslaget innebär 11 nya gemensamma frågor, eller 97 nya frågedefinitioner om alla fyra tjänste- och kontrollgrenarna följer nuvarande mönster; ett snävare alternativ redovisas. Två källavvikelser är öppet noterade: vägledningens hänvisning till Stockholms föreskrift samt ändrade bytes i den nu hämtade Europolrapporten.

**Enbart dokument ändrade.** Samma 816 resurser är byteidentiska med del 1:s gröna fullsvit: 3 448 godkända, ett liveprov bortvalt, noll fel/överhoppade prov. Ingen ny fullsvit behövs för dessa dokumentationsändringar enligt AGENTS regel 6; diff- och referenskontroll är genomförda. Regelbas 2.0.0, kod, tester, risknivåer och sakkunnigstatus är orörda. Ny lokal gren `codex/regelbas-inventering`; ingen push eller merge. **Steg B inväntar användarens granskning av luckförteckningen.**

## Del 1 godkänd av användaren – tidigare teknisk redovisning

# Rättning efter R4–R7 – del 1 tekniskt slutverifierad

Den enskilda V9-vägen avvisar R-beslut. Samlad granskning märks i attestposterna; äldre R-poster utan styrkt granskningssätt gäller inte inför ny fastställelse. Historiska V8/V9-paket verifieras fortsatt oförändrade. Fyndförklaring, läsbara tider och A15:s sidflöde är rättade; fyrtjänstfallets A minskar från 37 till 36 PDF-sidor med samma text. Huvudrapporterna är fortsatt 7/8 sidor.

**Färsk fullsvit: 3 448 godkända, ett liveprov bortvalt, noll fel/överhoppade prov, exit 0**, Python 3.12.15, 2207.161 s inklusive collection. Snabbprofil **140 godkända / 48,760 s**. Exakt collection/JUnit och 816 oförändrade kod-/test-/regel-/verktygsresurser. Regelbas- och diffkontroll passerar. Första fullsvitens 208 nekade loopback-prov och äldre typfallsprov är redovisade; den nya kompletta körningen är grön med lokala testportar tillåtna och samlad R-granskning i typfallsprovet.

[Granskningssvar, ändringar och PDF-läsprov](superpowers/reviews/2026-10-23-svar-r4-r7-granskning.md). Regelbasen och riskmodellens 25 filer är oförändrade. Användaren har därefter godkänt del 1; steg A redovisas överst. Grenen lämnas lokalt. Ingen push eller merge.

## Föregående leverans – historik

# Resultatrapport R4–R7 – tekniskt slutverifierad 2026-10-23

R4–R7 är genomförda på `codex/kravstod-tjansteexponering`. Nya rapportbyggen använder V9: resultatrapport, fullständig analysbilaga A och underlagsbilaga B1 i ett gemensamt paket. Granskning, sakgranskning, atomisk export/fastställelse, historisk verifiering och tre skyddade nedladdningar ingår. Inga nya sakfrågor eller AI-anrop; riskmodellens filer och regelbas är oförändrade.

**Färsk fullsvit: 3436 godkända, ett liveprov bortvalt, noll fel/överhoppade prov, exit 0**, Python 3.12.15, 2159,897 s inklusive collection. Snabb **140/44,751 s**. Exakt collection/JUnit och 816 oförändrade kod-/test-/regel-/verktygsresurser. Regelbas-/diffkontroll passerar. Första fullkörningens historiska M2-formatantagande och den andra körningens reproducerade HTTP-testklientrace rättades före denna nya kompletta slutgrind; alla råbevis är bevarade.

Två faktiska provpaket med ofiltrerade 430/438 maskinfynd har resultatrapporter på **7/8 PDF-sidor**; A **37/39**, B1 **183/190**. Hela bilagornas sidlayout är granskad via kontaktark, med särskild omkontroll av ändrade sidor. Huvudrapporten är kortare; hela paketet blir 2 711/3 363 ord längre enligt samma-fakta-kontraktet. Analysprofilen överskrider 180-sekundersmålet; ingen ny testoptimering ingår.

[Underlag till Claude, acceptansmatris och alla Word-/PDF-filer](superpowers/reviews/2026-10-23-resultatrapport-r4-r7.md). Formatbyte kräver ny sakgranskning av alla tre delarna. Befintlig V8-uppdatering behåller sitt sparade format och historiska fastställda bytes bevaras. Grenen lämnas lokalt för användarens Claude-granskning; ingen push eller merge.

## Föregående kontrollpunkter – historik

# Resultatrapport R3 – tre frysta Word-delar för granskning 2026-10-23

Användaren har gett uttryckligt klartecken till R3 efter Claude-granskning av R2 på `35b5be0`. R3 är implementerad med strikt fryst presentation, leveransmall, tre Word-filer och läsbara hänvisningar mellan filerna. Användarens fyra R3-förfiningar är gjorda. Riskmodellfiler och regelbas är orörda; inga nya frågor eller AI-anrop tillkommer.

**Verifiering:** 78 riktade prov / 89,60 s och snabbprofilens 140 prov / 49,709 s, Python 3.12.15. Collection/JUnit matchar, inga fel eller överhoppade prov och källsnapshotet är oförändrat. Båda syntetiska huvudrapporterna har **7 respektive 8 sidor**, samtliga visuellt kontrollerade. Alla sex Word-filers synliga text, ordning och källpekare är kontrollerade; bilagorna är inte fullsidigt visuellt granskade.

[Underlag till Claude, huvudrapporter och båda Word-bilagorna för varje fall](superpowers/reviews/2026-10-23-resultatrapport-r3.md). Detta är ett arbetssteg, inte en produktleverans: ingen färsk fullsvit, ingen produktgranskning/export/fastställelse för V9 och ingen push eller merge. **R4–R7 återstår; V8 är fortsatt standard.** Provrapporternas maskinfyndlista är syntetiskt tom; sidmålet måste därför provas igen med R4:s verkliga slutliga fyndlista.

## Föregående status – historik

# Scenarioavvikelse och D9-rad – tekniskt slutverifierade 2026-10-22

Claude-granskningens två fynd är rättade. En inaktuell eller obekräftad scenarioavvikelse kan inte stämplas om av den samlade tjänstegenomgången. Vyn visar behovet av separat omprövning; en aktuell avvikelse bevaras och standardvalet samma kan fortsatt bekräftas samlat. D9 redovisas i en rad per tjänst med alla faktor-/källreferenser kvar.

**Färsk fullsvit: 3 315 godkända, ett liveprov bortvalt, exit 0**, Python 3.12.15, 1 784,82 s pytest/1 786,302 s inklusive collection. Alla node-ID matchar JUnit, noll failures/errors/skipped och 783 frysta resurser oförändrade. Snabb **119/34,784 s**, analys **234/168,856 s**. Regelbas-/diffkontroll passerar. Fryst källcommit `5c40412`; efterföljande commit innehåller bara slutdokumentation.

De 64 D9-styckena blir fyra. Läsrapporten minskar **2 320 ord i båda fallen**, men är fortfarande **370 ord längre än schema 1**. B1:s samtliga saktexter och ordantal är oförändrade (endast revisionsradens tre kontrollsummor skiljer). Riskmetod och AI-gräns är oförändrade. [Rättning, reproduktion och fullständiga mätvärden](superpowers/reviews/2026-10-22-svar-claude-scenario-d9.md). Ren lokal gren lämnas för användarens granskning; ingen push eller merge. Andra klonen/grenen `feat/steg-1-3` är orörd.

## Resultatrapport R0–R2 för PDF-granskning 2026-10-23

R0–R2 är implementerade som offlineförhandsvisning. Efter Claude-granskningen på `f653eea` är oprövade/ej godtagna kontrollsänkningar märkta och förklarade, nya och gamla standardmotiveringar spärrade och mandatfixturens egna mekanismer samt hela motiveringar rättade. Nya PDF-filer har **7 respektive 8 sidor**, samtliga visuellt kontrollerade. Riktat sluturval **94 godkända/104,16 s**; snabbprofil **140/52,858 s**, 798 oförändrade resurser. Ingen färsk fullsvit eller produktleverans; V8 är fortsatt standard. **R3–R7 inväntar användarens uttryckliga klartecken till de nya PDF-filerna.** [Rättning, filer, bevis och två mindre redaktionella önskemål som återstår](superpowers/reviews/2026-10-23-svar-claude-resultatrapport-r2.md). Den första R2-redovisningen ligger kvar som historik.

## Föregående leverans och verifiering

# Engångssvar och testomläggning – tekniskt slutverifierade 2026-10-22

Plan T och F är genomförda på `codex/kravstod-tjansteexponering`. Gemensamma sårbarhets-/verksamhetssvar lämnas en gång; en gemensam handling och en tjänstegenomgång per erbjuden tjänst ersätter separata standardtillämpnings-/scenario-/blockklick. Lokala undantag, täckningsprövningar och ordinarie sakgrindar består. Nyinmatning av kontroll/rutin fungerar utan förberedda scenariokopplingar. Privata belägg kontrolleras före de samlade bekräftelserna. Riskmetod och AI-gräns är oförändrade.

**Färsk fullsvit: 3 308 godkända, ett liveprov bortvalt, exit 0**, Python 3.12.15, 1 794,45 s pytest/1 795,884 s inklusive collection. Samtliga node-ID matchar JUnit, noll failures/errors/skipped och 783 frysta program-/test-/regelresurser är oförändrade. Snabbprofil **115/36,155 s**, analys **230/169,342 s**. Regelbasvalidering/diffkontroll passerar. Fryst källbas `2644122`; efterföljande commit färdigställer endast dokumentation. Oberoende helgranskningens fyra Important är rättade med reproducerande RED/GREEN-prov före fullsviten; inga uppskjutna Minor från denna granskning.

[Slutprov och underlag till Claude](superpowers/reviews/2026-10-22-engangssvar-slutprov.md), [helgranskning](superpowers/reviews/2026-10-22-engangssvar-slutgranskning.md), [testtäckningsmatris](superpowers/reviews/2026-10-22-testtackningsmatris.md) och [användning](kravstod.md). Fem bekräftelser i det kompletta fyrtjänstprovet avser efter svarsinmatning. Rapporterna är fortfarande cirka 4 000 ord längre än schema 1; ingen rapport-/lästidsvinst påstås. Riktad, inte fullsidig, visuell kontroll. Råbevis bevaras i lokalt ignorerat evidensarkiv. Grenen lämnas lokalt för användarens granskning med Claude; ingen push eller merge.

## Tidigare testcheckpoint

# Testomläggning under slutverifiering 2026-10-22

Testplan T har explicita snabb-/analysprofiler, isolerade kedjekopior och färre upprepade transporter. Första fulla pytest: **3 214 godkända, ett liveprov bortvalt, 1 660,05 s**. Ett separat fel i körverktygets hantering av parametriserade testnamn är rättat med två RED-regressioner; samtliga tio verktygsprov passerar och samma fulla collection/JUnit matchar exakt med rättningen. **Slutlig leveransgrind för den rättade testinfrastrukturen samordnas med plan F; ingen push eller merge före den.** [Mätning](superpowers/reviews/2026-10-22-testtid-slutprov.md) och [täckningsmatris](superpowers/reviews/2026-10-22-testtackningsmatris.md) redovisar begränsningar och råbevis.

## Föregående produktleverans

# Gemensam analys – tekniskt slutverifierad, 2026-10-22

Plan A och B1–B7 är införda på `codex/kravstod-tjansteexponering`. Färsk fullsvit efter helgranskningens samlade rättningar: **3 198 godkända, ett livetest bortvalt, exit 0**, 2 152,78 s på Python 3.12.15. JUnit har noll fel och de 463 frysta källfilerna är oförändrade. Regelbasvalidering och diffkontroll passerar. [Slutprovet och underlaget till Claude](superpowers/reviews/2026-10-22-forenklad-riskbedomning-slutprov.md) anger arbetsflöde, mellancommits, rapport-/bekräftelsemått, riktade prov och kvarstående begränsningar. Ingen push eller merge. Användarens slutgranskning med Claude återstår.

Infört: uttryckligt planval/återkallelse, standardtjänster, gemensam byråanalys, innehållsbunden tillämpning per tjänst, separat hot-/PT-/TF-/riskledsprövning, kontrafaktisk +1-referens, V8-rapport och uttrycklig överföring med originalarkiv. Motorns riskmetod och AI-gräns är oförändrade; nytt kataloginnehåll är ogranskat.

Samma-fakta-mätningen visar **1 844 fler ord totalt** och **100 i stället för 96 bekräftelseoperationer** i båda provfallen. Ingen längd-/tidsvinst påstås. Egna tjänster utanför katalogen kräver fortsatt det framtida manuella analysstödet. En uppskjuten Minor kan kräva ett nytt formulärförsök när man byter bort från ”gäller annorlunda”; risk-/godkännandespärrar består. Läs [användnings- och uppgraderingsanvisningen](kravstod.md) före överföring; inga gamla analysgodkännanden förs över.

## Tidigare status och verifieringshistorik

Texten nedan är historik och kan beskriva tidigare, ännu inte införda steg. Aktuell leveransstatus står ovan och i slutprovet.

# Status och framsteg

Senast uppdaterad 2026-10-22.

## Design för gemensam analys och tjänstevis tillämpning

Designens revision 2 är godkänd i chatten. Genomförandet är uppdelat: först [återkallelse och uttryckligt införandeval, A1–A3](superpowers/plans/2026-10-22-planaterkallelse-och-inforandeval-plan.md), därefter [gemensam analys och tjänstevis tillämpning, B1–B7](superpowers/plans/2026-10-22-forenklad-riskbedomning-plan.md). Plan A är implementerad och tekniskt slutverifierad: **3 063 passerade, ett bortvalt livetest, exit 0**, 1 748,27 s på Python 3.12.15. Filhasharna i det frysta urvalet (416 filer), regelbasvalidering och diffkontroll passerar. [Slutprov och granskningsunderlag för Claude](superpowers/reviews/2026-10-22-planlivslopp-slutprov.md) redovisar även rättningshistorik och riktad visuell kontroll. Produktleverans `b3cf490` är committad lokalt. Användarens Claude-granskning återstår. Plan B är godkänd men ännu inte implementerad. Den tar med användarens preciseringar: härledd riktning där motor-/katalogkopplingen medger det, oklar som standard för `galler_annorlunda` och en separat kontrafaktisk +1-referens för täckningsprövningen. Referensen ändrar inget verkligt motorutfall; en lägre vald jämförelsenivå kräver uttrycklig motivering och sakgranskning. Mellanleveransen efter B3 får inte användas av verkliga byråer före verifierat rapportstöd i B5.

**Plangranskning 2026-10-22:** Båda planerna är godkända; användarens sista precisering om +1-referensen är införd i plan B. Planrevision 2 skiljer känt falskt villkor/under tröskel från uttryckligen saknad hotkoppling, inför täckningsprövning för egen sårbarhet och rekommenderar leveranscommits efter B3, B5 och B7 med färsk fullsvit vid varje gräns. Ny katalogtext ska vara ogranskad och visuell dokumentkontroll fungerar även utanför Codex. [Granskningssvaret](superpowers/reviews/2026-10-22-svar-plangranskning-forenklad-struktur.md) beskriver ändringarna för användarens fortsatta granskning med Claude.

Ett [skriftligt designunderlag, revision 2](superpowers/specs/2026-10-22-forenklad-riskbedomning-design.md) samlar det reviderade chattförslaget, [granskningen korrigerad i `9fedb6f`](superpowers/reviews/2026-10-22-granskning-forenklad-struktur.md) och efterföljande granskning i chatten. Det beskriver standardkatalog med samlat tjänsteurval, gemensam sårbarhetsanalys, uttryckliga tjänstetillämpningar och rapportering av omfattningsluckor. Belagda avvikelser där motorn är försiktigare ska vara synliga utan att i sig spärra; möjlig underskattning/oklarhet använder befintlig öppen lucka eller metodkonflikt. Spärren för tjänster utanför katalogen beskrivs som en produktbegränsning i första leveransen, med manuell tjänsteanalys som fortsatt utveckling. Samlat tjänsteurval ska begära planval vid införanderaderna och sparas atomiskt. Strukturändringarna i plan B är inte implementerade. Riskmotor och metodbeslut är oförändrade.

**Känd produktlucka på `91a3ece`:** en övergiven plan kan spärra ett nytt införande, och om flera nya-tjänst-planer utvärderas genomförs alla vid erbjudandeövergången. Båda beteendena är reproducerade med syntetiska uppgifter. Designen anger återkallande med bevarad historik och uttryckligt val av den plan som genomförs. Den efterföljande plan-A-rättningen är nu tekniskt verifierad enligt avsnittet ovan. Testutfallet i den äldre rättningshistoriken nedan avser produktbasen och ska inte blandas ihop med den nya leveransens slutprov.

## Rättning efter implementationsgranskning, 2026-10-22

Planer har nu ett uttryckligt livslopp. Ny tjänst avslutas vid giltig erbjudandeövergång i samma atomiska profilsparning. Genomförd ändring av redan erbjuden tjänst registreras uttryckligen i webb eller med `genomfor-plan`. Avslutade planer bevaras med sin då gällande utvärdering och kontrolleras inte mot senare byråfakta, bedömningsdatum eller regelbas. De får inte redigeras eller användas för ett nytt återinförande. Ordinarie årsutvärdering och aktuell analys krävs fortfarande.

**Uppgraderingsanteckning:** `profil.modeller` ingår i modellidentiteten. Uppgraderingen ogiltigförklarar därför befintliga analysgodkännanden och modellriskunderlag som underlag för nya beslut. Gör aktuell bedömning och uttrycklig analysförnyelse, jämför uppgifterna och sakpröva/godkänn igen. Historiska fastställda paket bevaras. Planer från första implementationen utan avslut markeras inte automatiskt som genomförda; de behöver uttrycklig registrering med kontrollerat underlag.

Gemensamma faktormekanismer använder metodmotiveringen när den finns och anger möjliggjorda hot med namn. Standardtexten står en gång; den lokala kodlistan är ersatt av hänvisning till redan redovisad sårbarhetsprövning. Motorn och AI-gränsen är oförändrade. Verifieringsutfall för denna rättning dokumenteras separat i [granskningssvaret](superpowers/reviews/2026-10-22-svar-granskning-kravstod-implementation.md); föregående slutprov nedan är historik för `a7f9377`.

**Ny slutverifiering:** Python 3.12.15, **3 027 godkända prov och 1 bortvalt livetest**, exit 0 på 1 727,86 s. Regelbasvalidering och diffkontroll passerar. Oberoende kodgranskning gav inga kvarstående fynd. Berörda exporterade sidor är visuellt kontrollerade. Rapportmätningen mot `a7f9377` visar tio ord kortare läsrapport i båda provfallen och oförändrad B1; ingen större förkortning påstås.

## Kravstöd och tjänsteexponering, 2026-10-22

Planrevision 3 är genomförd för uppgift 0–5 och slutprov 7 i den avgränsade underlagsleveransen. Registrerade planer har bunden mänsklig förändringsutvärdering före införande, uttrycklig rättelseväg och bevarad årsfrist. Deklarerade kombinationsgrupper ligger lokalt och redovisas vid rätt tjänst; inget individuellt kundregister införs. V8:s gemensamma faktormekanismer och lokala tillämpning kompletterar befintlig analys; fulla beräkningstabeller ligger kvar i B1. Äldre serialisering och AI-gränser är bevarade.

**Verifiering:** Python 3.12.15, 3 010 godkända tester och 1 avmarkerat livetest, exit 0 på 1 909,08 s. Regelbasvalidering och diffkontroll exit 0. Separat granskning gav fem Important och två Minor; samtliga rättade med reproducerande prov före slutlig fullsvit. Riktad visuell kontroll av berörda exporterade sidor genomförd. Läsrapporten ökar 687 ord i båda jämförelsefallen, B1 är oförändrad; ingen total minskning påstås.

**Kvar:** 3b är frivillig och uppskjuten. Uppgift 6 avvaktar verkliga metodbeslut; riskmotor, vikter och regelbas är oförändrade. Profilmodellernas ändring ger ny befintlig källbunden modellidentitet; historiska attester märks inte om. Teknisk verifiering är inte sakkunnigattest, verklig utbildning eller produktionsrelease. Se [slutprovet](superpowers/reviews/2026-10-21-kravstod-slutprov.md), [kravmatrisen med 36 rader](superpowers/reviews/2026-10-21-kravmatris-36.md) och [användning](kravstod.md).

## Plan för bättre riskbedömning och rapport, 2026-10-19

H7:s V8-dokumentkedja är tekniskt implementerad med V8 som aktuell standard. Det kanoniska dokumentet är komplett; läsrapport och underlagsbilaga är två disjunkta, oförändrade projektioner som tillsammans utgör helheten. Den frysta `Presentation` binder Leveransmall, bokstavliga spann, ordnade källor och vyerna. Tvåfilsleveransen publiceras atomiskt. Aktuell V8-kontroll använder dagens producentoperationer och bedömningsbundna period-/regelbasunderlag; historisk V5–V7-verifiering behåller sina gamla bytes och attestkontrakt. Fix 6:s V8-analysundantag gäller endast den exakta, synligt belagda verbträffen för delvis tjänstebunden bankinsyn; övriga riskminskningspåståenden och äldre format behåller spärren.

**Teknisk verifiering:** Sol har godkänt fix 4 inom produktkodscope, fix 5 inom testscope och fix 6 inom sin smala produktkodscope. Fix 6:s fokuserade V8/V7-prov gav 202 passed på 3,22 s. Ordinarie fullsvit 4 är grön som historik före fix 6: 2 924 passed, 1 deselected, 1 907,37 s, exit 0; 2 924 valda prov motsvarade 2 924 JUnitposter, 689 frysta kodfiler och 0 ändrade. Den frysta fullsvit 5 efter fix 6 gav **2 946 passed, 1 deselected**, pytest exit 0 på 1 926,28 s; helper 1 928,56 s, 2 946 valda prov exakt täckta av JUnit, 0 failures/errors/skipped, 689 kodfiler oförändrade och 736 projektfiler utan hashavvikelse. Källor: `RUN/slutlig-fullsvit-5/{pytest.log,pytest.xml,resultat.json,root-verifiering.json,tackning-mot-full4.json}`. Separat regelbasvalidering gav exit 0 för version 2.0.0, 107 krav, 11 tjänster och 201/201 hanterade paragrafer i vart och ett av tre paket; sakkunnigstatus är `ej_granskad`. 351 metodfiler, varav 314 regelbasfiler, var oförändrade. Root har applicerat exakt de tre dokumenten från verifierad bas/resultat-SHA; efterföljande `git diff --check` passerade (exit 0), bevis `RUN/slutdocs-root-applicering.json`. Slutlig Sol-review av den faktiska docs-diffen är genomförd: [Approved inom dokumentations-/evidensscope](../.superpowers/sdd/2026-10-11-d-arb-tjanststruktur/h7-slutdocs-final-sol-review.md).

**Separata offlinebaslinjer och mått:** primär B-offlinejämförelse använder samma verifierade original-YAML-profil, motor, analys och exakt frysta AISvar via V7/V8-anrop; enda typade transportskillnaden är `P-BEVAKNING.datum/varde` (YAML `date` respektive ISO-sträng i JSON:s Any-värde). V7 är 100 sidor/35 272 ord. V8:s läsrapport är 49 sidor/18 326 ord och underlagsbilagan 134 sidor/37 503 ord, tillsammans 183 sidor/55 829 ord. Fix 4:s 130 ordnade fynd matchar `h7-8/B-offline-originalyaml-slut/fynd.json`; måtten kommer från de slutliga DOCX:erna i `B-offline-slut-efter-fix4/` och `offline-slut-sidmatning/matning.json`, där tre DOCX-hashar var oförändrade före/efter. V7 använder Letter och V8 A4. Måttet 20–25 lässidor är inte uppnått. Dessa offlineord och sidor jämförs inte med ett senare AI-svar eller med ett totalmått där bara läsrapporten ingår.

**Faktiskt AI-prov och efterföljande replay:** B-live-provet gjorde 11 leverantörsanrop för fyra logiska analyser; sju externa omförsök, noll SDK-omförsök och ingen reservmodell. Samtliga första försök underkändes; en av fyra analyser passerade efter omförsök och tre slutade som mallar. Modellen var Claude Opus 5.5, high, med xhigh på tre tredje försök. Förbrukningen var 12 982 indata-, 202 688 utdata-, 110 566 cachelästa och 63 721 cacheskrivna token. Kostnaden är ett listprisestimat på 4,4464062 USD från [officiell prissättning](https://platform.claude.com/docs/en/about-claude/pricing), hämtad 2026-10-19 17:03 UTC; prisnivåerna som användes var 4 USD per miljon inputtoken, 20 USD per miljon outputtoken, 5 USD per miljon cache-write-token och 0,20 USD per miljon cache-read-token enligt prislistan; prompt-cache-dokumentationen anger fem minuters standard-TTL ([cachevillkor](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)). Det är inte en faktura. Väggtiden var 1 809,115403 s. Under provet förblev 306 source- och 306 copyfiler, kritiska indata och samtliga 736 projektfiler byteoförändrade. Originalets 1/4-utfall och mallar är bevarade.

En separat strikt offline-replay efter fix 6 återanvände exakt de 11 sparade request-/responseparen och gjorde noll externa anrop. Den fick två av fyra analyser igenom och två mallar (T-RED-03/T-RED-04); originalkörningen skrivs inte om, och redan använda token debiteras inte en gång till. Den efterföljande kontrollen fann 418 råfält, 24 frågor, 249 fullständiga ordnade fynd, 132 exakta fyndgrupper och 242 blockerande fynd; fulltext, multiplicitet, ordning och källhashar bestod. Detta är offline-ombedömning av samma frysta AI-svar, inte en ny stokastisk körning eller ett generellt följsamhetsmått.

Den slutliga replayexporten efter webbuppdateringen mäter 52 sidor/20 519 ord för läsrapporten och 143 sidor/42 647 ord för underlagsbilagan, totalt 195 sidor/63 166 ord. Måttet avser en separat B-live-svarstext inom samma ursprungliga syntetiska byrå; en stokastisk AI-text är inte byteidentisk med B-offline-svaret eller tidigare B-live-svar. Ingen total minskning, lästidsvinst, lägre risk eller minskad mänsklig kompletteringsbörda påstås. Den tidigare generiska skriptsvarstexten i H7.4/H7.5 och den äldre 102-sidiga B-live-mätningen är historik, inte slutlig jämförelsetext.

**UI, Word och rendering:** det avgränsade browserprovet använde en egen testserversession återupptagen från en verklig kontrollerad export; ordinarie CLI återställer inte sessionen. De två nedladdningsrutterna svarade 200 före och efter, uppdateringen svarade 303 och skapade en ny export utan AI-anrop. HTTP-payloadens hash matchade båda filerna före och efter, men webbläsarens faktiska skrivning till disk kunde inte styrkas (`net::ERR_ABORTED`). Den egna serverprocessen stoppades med exit 0; delad server lämnades orörd. Microsoft Word kontrollerade båda slutliga DOCX-filerna på skrivskyddade, byteidentiska kopior utan fältuppdatering eller sparning; stickprovet omfattade första/sista sida, tät löptext och tabellregioner i dokument med 52 respektive 143 Word-sidor. Inga klipp eller korrupt text observerades i de kontrollerade regionerna; detta är inte fullsidig Word-QA. Samtliga 195 Cairo-PNG-sidor har nu öppnats individuellt: läsrapport 52 och underlagsbilaga 143, med exakt union utan luckor/dubbletter och SHA-match för alla bilder; de två DOCX- och två PDF-källorna är oförändrade. Ingen materiell kroppsklippning eller överlappning konstaterades. Kvarstående kosmetiska Minor är radbrytningen av den smala tjänstekolumnen för Gemensamt på bilagesidor 70–72 samt fyndfortsättningar utan upprepat grupp-ID. Cairo-raster saknar ibland upprepade tabellrubriker/sidhuvuden, exempelvis 80/82; äldre `pdftoppm`-bild 80 från exakt samma PDF visar full tabellrubrik och UTKAST. Det är en renderingsbegränsning, inte belägg för fel i dokumentkroppen. Word-stickprovet på sidorna 15/45–46 består. Försök till extra Word-kontroll av sida 80 nådde öppningsdialog men avbröts av CUA-timeout; inget nytt native Word-resultat påstås. Detta är full visuell raster-QA, inte fullsidig native Word-QA eller mänsklig sakgranskning.

Slutlig Sol-review av docs-diffen är genomförd: [Approved inom dokumentations-/evidensscope](../.superpowers/sdd/2026-10-11-d-arb-tjanststruktur/h7-slutdocs-final-sol-review.md). **Öppet:** faktisk browsernedladdning till disk, verklig medarbetarläsning, H7.7:s nio frågor samt M1–M4 och sakkunnig-/byråbeslut. Redaktionell komprimering mot 20–25 lässidor och bättre AI-följsamhet återstår trots tekniskt gröna tester: aktuell export är 52 sidor läsrapport/143 sidor bilaga, livekörningen gav tre mallar och offline-replay två. Dessa resultat räcker inte för att kalla läsbarhetsmålet uppnått. Slutfix 6-reviewns Minor `RB-KATALOGATTRIBUTION` kvarstår: katalogtext kan få en felaktig utförandeetikett, men separat kombinationsfel behåller mallutfallet; detta är ingen verifierad utförandeuppgift och ingen generell attributiondispens. Kodslutreviewns Minor M3 (fortsättningssida utan upprepat grupp-ID) är uppskjuten och har ingen layoutomdesign i denna scope. Teknisk implementering eller testresultat är inte juridiskt godkännande, mänsklig attest eller produktionsrelease.

## Samlade intagsformulär, 2026-10-19

På användarens begäran samlas närliggande aktiva frågor på samma sida med ett gemensamt underlag, eventuell period, datum och funktion. Varje svar behåller egen spårbarhet. Tidigare svar lämnas orörda som standard, tomt blir inte nej/noll och Vet inte kan sparas per rad med historiska belägg kvar. Hela urvalet går genom befintlig svarshantering och en enda atomisk profilsparning med revisionsskydd. Intervjun väljer gruppvisning automatiskt; **Samlade frågor** ger gruppöversikten och enskilda frågor finns kvar för egna källor/perioder. Registerförslagen har fortsatt separat uttrycklig bekräftelse. Kontrollfaser och den lokala analysguiden grupperas inte om.

**Slutverifiering:** **2 730 passerade, ett bortvalt livetest**, inga fel, överhoppade prov eller xfail, 654,60 s. Fyra färska pytestprocesser körde exakt samma fullständiga urval som ordinarie insamling; alla 661 program-/regel-/testfiler inklusive pyproject var byteidentiska före/efter. Delresultat: enhet/företagsdata/typfall 1 419, intag 525, M2 98 och regelkontrakt 688 + ett bortvalt livetest. 31 nya grupprov ingår. Separat granskning och syntetiskt webbläsarprov är genomförda utan kvarvarande konkreta fynd. Den första fullsviten avbröts efter ett reproducerat registervisningsfel; felet rättades med en ny regression före den gröna slutkörningen. Regelbasvalidering, kompilering och diffkontroll passerar. Planen redovisar RED/GREEN, granskning och bevarade körloggar.

Inga commits, pushar, riktiga API-/AI-anrop eller ändringar av verklig byrådata ingår. Beräkningsregler, AI-underlag och sakkunnigstatus är oförändrade. Se [intagsplanens genomförandelogg](superpowers/plans/2026-10-10-intag-och-hel-riskbedomning.md#samlade-formulär-2026-10-19) och spec §14.1.

## Tre kedjefel rättade och verifierade, 2026-10-19

De tre felen från programgenomgången nedan är rättade. Bedömningen räknar från och sparar exakt samma profilbytes även vid samtidig atomisk profilsparning. Nya bedömningar sparar den befintliga, avgränsade modellbindningen; fortsatt arbete stoppas om bindningen saknas eller modellen har ändrats. Äldre frysta bedömningar och paket kan fortfarande läsas och verifieras, men behöver en ny bedömning för att användas i en ny kedja. Enbart presentationsändringar ogiltigförklarar inte modellen.

Aktuell Word-nedladdning jämför den frysta lokala analysen med dagens register under analyslåset och läser dokumentets bytes innan låset släpps. Ändrad, tillagd eller borttagen analys stoppar ett gammalt utkast; ingen analys då eller nu tillåts fortfarande för första utkastet. Knappen **Uppdatera Word-utkast utan nya AI-anrop** granskar och exporterar igen från det befintliga skrivförsöket. Profiländringar kräver fortsatt ny skrivning. CSRF-, revisions- och formulärkontroller samt fastställelsens starkare grindar behålls.

**Slutverifiering:** **2 699 passerade, ett bortvalt livetest, inga fel, överhoppade prov eller xfail**, 732,45 s. Fyra färska pytestprocesser körde exakt samma fullständiga urval som ordinarie insamling; alla 658 program-/regel-/testfiler inklusive pyproject var byteidentiska före/efter. Delresultat: enhet/företagsdata/typfall 1 419, intag 494, M2 98, regelkontrakt 688 + ett bortvalt livetest. Före rättning föll 12 väntade regressioner (två skyddsprov passerade); efter rättning passerade 38 prov i de berörda modulerna och 122 integrationsprov. Oberoende granskning fann inga Critical/Important/Minor och körde själv 38 prov med godkänt resultat. Regelbasvalidering, kompilering och diffkontroll passerar. Regelbasens kontrollsumma, beräkningsregler, AI-begäran och sakkunnigstatus är oförändrade. Inga commits, pushar eller riktiga API-anrop.

Sakkunnigprövning och de tidigare öppna metodfrågorna kvarstår. Kontrollen av aktuellt analysregister är ingen ny fullständig prövning av externa beläggsfiler med oförändrat register.

Plan och arbetsjournal: [scenarioplanens rättningsavsnitt](superpowers/plans/2026-10-18-scenariomotor.md#beställda-rättningar-efter-programgenomgången-2026-10-19), `.superpowers/fixes/2026-10-19-kedjebindning/`.

## Programgenomgång: tre reproducerade fel, 2026-10-18

Efter den avgränsade scenariogranskningen har Codex granskat huvudflödet från intag till fastställelse och provat det lokala gränssnittet med syntetiska data. Tre nya fynd reproducerades vid genomgången och har därefter rättats enligt avsnittet ovan: **P1** samtidig profilsparning kan blanda en gammal beräkning med en ny profilkopia (`bedomning/korning.py`); **P2** webbens Word-nedladdning godtar ett tidigare utkast efter ändrad lokal analys (`intag/dokument.py`, HTTP 200 med gamla bytes verifierat); **P2** en gammal bedömning kan få en ny modellbindning utan omräkning (`analys/lagring.py`, simulerat modellbyte i isolerad kodkopia). Fastställelsens starkare kontroll av aktuellt analysregister finns kvar. Proven visar inte att ett verkligt fastställt paket är felaktigt.

Färsk ordinarie fullsvit: **2 685 passerade, ett bortvalt livetest**, inga testfel; fyra nya pytestprocesser, exakt samma urval som fullinsamling, 682,28 s och **657 oförändrade program-/regel-/testfiler**. Regelbasvalidering, kompilering och diffkontroll passerar. De separata reproduktionsproven visar luckor i den gröna svitens täckning. Programkod, regelbas, riktiga byråuppgifter och sakkunnigstatus är oförändrade under genomgången; inga commits eller pushar.

Detaljerad genomgång av hur programmet fungerar, prioriterade rättningsförslag, användbarhetsfynd och prov ligger i [granskningsrapporten](../.superpowers/review/2026-10-18-programgenomgang/granskning.md) och samma privata arbetskatalog. Genomgångens rättningsförslag var bedömningens profil-/modellbindning och aktuell Word-export efter lokal ändring utan nya AI-anrop; utfallen redovisas ovan. Maxregel, bred PT-kontrolltäckning och sakkunnigprövning är fortfarande separata metodfrågor.

## Scenariomotor 2.0.0: tekniskt slutförd, 2026-10-18

Codex har återtagit [scenarioplanen](superpowers/plans/2026-10-18-scenariomotor.md) efter sessionsavbrotten. Uppgift 1–3 behålls från `52ed984`–`f46b801`; katalogrundan i uppgift 4 är omgranskad. Uppgift 5 prövar varje faktiskt sänkt PT-scenario mot positiv lokal prövning av samma hot och en bärande kontroll, även när tjänstens maxnivå inte sänks. Uppgift 6 visar alla scenarier, avgörande före/efter och scenarioegna faktorer; B1 bevarar varje beräkning och regelspår. Äldre bedömningar utan scenarier behåller sin gamla väg. Regelbasen är 2.0.0 och AI-begäran är oförändrad.

**Slutverifiering:** **2 685 passerade**, ett bortvalt livetest, inga fel, överhoppade prov eller xfail. Hela testurvalet kördes exakt en gång i fyra färska pytestprocesser på 673.56 s; samtliga 657 program-, regel- och testfiler var byteidentiska före/efter. Delresultat: enhet/företagsdata/typfall 1 413, intag 486, M2 98, regelkontrakt 688 + ett bortvalt livetest. Regelbasvalidering, kompilering och diffkontroll passerar. Oberoende kodgranskning fann inga Critical/Important och verifierade själv 188 prov samt 12/12 identiska äldre dokumentserialiseringar.

Integrationsrundan rättade falskt B1-stopp för frivilliga iakttagelsefält och registrerade den nya B1-rubriken. Det positiva syntetiska typfallet kompletterades med bankavstämningen som faktiskt bär H-MOD-01:s sänkning; produktionsspärrarna försvagades inte. Äldre Word-/tabellförväntningar uppdaterades till scenariomodellen. Tidigare röda/avbrutna körningar är bevarade i arbetsjournalen; slutresultatet ovan är efter dessa rättningar och användarens längdbeslut.

**Mätt syntetiskt normalprov:** 4/4 Testleverantor-svar accepterade och hela begäransfilen byteidentisk mot 1.6.0. Huvudtext 4 999 → **4 997 ord**, B1 12 913 → **16 859 ord**. Alla 210 längre lokala svar som förekom i föredokumentet finns kvar. Nya tabeller är renderade och visuellt kontrollerade med buntad LibreOffice/Poppler; 68 sidor totalt, varav 19 huvudtext och 49 bilaga. Sidantalet är ett läsbarhetsmått, ingen automatisk godkännandegräns. Detta är ingen kontroll i Microsoft Word. Det bredare kedjeprovet ger 5 354 huvudord och visar den befintliga längdvarningen utan trunkering. Utkastsexportens manifest verifieras; ogranskad metod och lokala metodkonflikter hindrar fortfarande godkännande.

**Längdbeslut:** användaren har tagit bort hårda ordgränser i dokumentproven, inklusive det tidigare taket 4 999/5 000 ord. Ordmätning och rådgivande varning behålls; innehåll och spårbarhet styr. Ingen ytterligare kortning görs enbart för ett ordtal.

**Kvarstående beslut:** maxaggregering och smala kontrollmål ger höga kvarstående nivåer; C-TJ-08/09 täcker hela PT-sidan trots breddregeln över PT+TF. Dessa metodval lämnas till sakkunnig. Ett mindre framtida kodfynd är också parkerat: olika faktor-ID/vikter med samma visningsnamn kan grupperas i huvudtexten; dagens katalog har inga sådana namn, och B1 bevarar beräkningarna. Se [research 13](research/13-scenariomotor-katalog.md). M1–M4 och verklig sakkunnigprövning kvarstår. Inga nya commits eller pushar ingår.

## Nivåmotivering, lokala utfall och skrivformat v7, 2026-10-18

Planen [nivåmotivering och sammanhängande text](superpowers/plans/2026-10-17-nivamotivering-och-sammanhangande-text.md) (spec revision 35) är byggd med subagenter och separat granskning per uppgift: rättad sanktionsbetydelse, nivåmotivering i varje tjänsteavsnitt, M1-förslaget i B1, lokala utfall för skyddade faktorer, frivillig tjänstefördelning, färre hänvisningar, fasta verksamhetsval och skrivformat/dokument v7 med en AI-del per tjänst. Motorns beräkning och sakkunnigstatus är oförändrade; regelbas 1.6.0 validerar.

**Verifiering:** fullsvit **2 495 passerade, ett bortvalt livetest, 1 408,97 s** (commits `6a9e59e`, `8eb0cdc`). Andra provet med riktig AI på två påhittade byråer: **9 av 9 tjänstetexter godkända, inga reservmallar**, 13 anrop, kanariekontroll godkänd (första provet: 2 av 9).

**Inte uppnått:** huvudtexten blev 8 590 respektive 10 543 ord mot målet 3 500–5 000. Orsaken är främst att samma lokala svar återges i flera fält inom tjänsten och att byråövergripande utfallslistor upprepas i varje tjänst. Restetiketter ("Hänvisningar.") och en motsägelse mellan AI-text och lokal tjänstefördelning behöver rättas. Sidantal, Microsoft Word-läsning och medarbetarläsprov återstår.

**Metodstatus vid V7-leveransen:** den dåvarande motorn värderade inte hoten och kontrollsänkningen var inte kopplad till specifika risker. Scenariomodellen (hot → sårbarheter → kontroller per scenario) har därefter beställts enligt avsnittet ovan. M1–M4 och sakkunnigprövning kvarstår.

## A + B tekniskt slutfört, 2026-10-17

Claude slutförde A + B med subagenter efter att Codex nått sin användningsgräns; Codex granskade två gånger. Rättat: äldre utkast ger tydligt fel i stället för krasch, låsta stycken om egen rapportering och geografi med B-09/B-10/B-15, omfattningens motivering och D-ARB.9 i v6, lokal prövning av AI-text mot v6:s låsta stycken utan ändrad AI-begäran, framtidsdaterat stöd för analysgodkännande, symlänkade mappar vid beläggsimport, v6-layout och B1-delrubriker i dokumentmodellen. 81 regelkontraktsprov körs mot v6.

Användarens beslut 2026-10-17: realistiskt läsprov 3 500–5 000 huvudord (riktbudget 4 700), AI-maxprov med synlig längdvarning och bevarad analys; ett underkännande får dokumentera felaktigt daterat stöd; B1-rubriker i modellen.

**Verifiering:** fullsvit **2 107 passerade, ett bortvalt livetest, 1 147,52 s**, exitkod 0. Regelbas 1.5.0 validerar; `git diff --check` passerar. Demo 4 510 huvudord på 15 LibreOffice-sidor (sidmålet 9–12 nås inte), AI-max 5 239 med längdvarning, B1 cirka 12 700 ord. Ogranskat tekniskt modellrapportpaket verifierat i `~/.local/share/riskanalys/provkorningar/ab-modellrapport-20261017/`.

**Kvarstår:** verklig sakkunnig metodvalidering och M1–M4, namngiven modellansvarig och byråbeslutsansvarig, medarbetarläsprov, kontroll i Microsoft Word, commit. Detaljer i [D-ARB-planen](superpowers/plans/2026-10-11-d-arb-tjanststruktur.md#slutförande-och-verifiering-2026-1016–17) och spec revision 34.

## A + B: implementation med subagenter pågår, 2026-10-15

Användaren beställde genomförande av hela planen med subagenter. Färsk baslinje: **1 632 passerade, ett bortvalt livetest, 729,80 s**; 573 program-/regel-/testfiler var oförändrade under körningen. Arbete sker på `codex/m0-m1`, utan commit eller push. De tre tidigare dokumentationsändringarna är säkerhetskopierade och `research_notes/` lämnas orört.

AB1 har infört beskrivande räckvidd, korsreferenser och egna innehållsbundna sakkunnigobjekt; regelbas 1.4.0 validerar. Riktad verifiering: 83 passerade, samt 32 efter rättad aktuell versionsförväntan. En ny granskare har godkänt AB1. Faktisk scenariotäckning är fortfarande okänd för de generiska kontrollerna; inga nya riskfaktorer eller numeriska regler införs.

AB4a har infört dokumentformat v5.1 med risköversikt först, beräkningar i B1, interna Word-länkar och läsbara käll-/kontrollbeskrivningar. Historiska v5-summor bevaras. Granskningen hittade saknad explicit M1–M4-status och interna ID:n i ny löptext; båda rättades och återgranskades. Efter rättning: **122 riktade tester passerade**, inklusive syntetisk CLI-kedja genom fastställelse/verifiering/återställning. Färsk steg 1-fullsvit: **1 677 passerade, ett bortvalt livetest, 730,04 s**; alla 576 program-/regel-/testfiler var oförändrade under körningen. Regelbasvalidering och diffkontroll passerar. Exakt testat steg är sparat separat före fortsatt arbete. Tretjänstprovet blev längre av beskrivningarna, så längdmålet är inte uppnått genom läsordningen ensam.

Steg 2 har kompletterat räckvidden med typad beskrivningsstatus och regelbas 1.5.0, utan numerisk ändring; 99 riktade tester och separat granskning passerar. AB7:s modellidentitet, rapportpaket och lokala modellriskunderlag är implementerade. Separat granskning hittade tre fel i installationsformat, historisk rapportläsning och importkontroll; dessa rättades med RED→GREEN. Återgranskning godkänner rättningarna, 92 riktade tester passerar. AB2:s modeller, privata CAS-lagring, belägg och låsta beslut är byggda. Granskningens två fel i kontrollvärdesprövning och destinationsvägens symlänksskydd rättades med RED→GREEN; återgranskningen godkänner och 130 riktade tester tillsammans med AB7 passerar. AB3:s typade CLI/webbguide är implementerad och godkänd i separat granskning: 67 färska prov, inklusive kompletta formulär-POST för alla 16 block. AB4b:s fulla v6-dokumentbyggare är också godkänd; maxproven ger 4 892 respektive 5 628 huvudord med 1 520 AI-ord. B1 är fortsatt omfattande och ingen sidlayout är ännu verifierad. AB5:s frysta attest-/paketkedja klarar 135 riktade och elva M2-prov; separat granskning hittade ett kronologifel som rättats med RED→GREEN. 143 riktade prov och separat återgranskning med åtta datumprov godkänner rättningen. AB6:s helkedja och artefaktprov pågår. Projektets tekniska rapport har ännu inte levererats. Dessa preciseringar tillför inga nya sakfrågor eller riskvikter. Sakkunnig metodprövning/M1 och verklig byrågranskning kvarstår.

## A + B: avgränsad efter Claudes granskning, 2026-10-15

[Befintlig plan](superpowers/plans/2026-10-11-d-arb-tjanststruktur.md#avgränsning-efter-claudes-granskning-2026-10-15) och spec revision 32 preciserar sex omfattningsbeslut: redigerbara ogranskade förslag och delade scenarier med samma/avviker per tjänst; endast hot/sårbarheter från AI i v6; två leveranssteg; logg/synlig märkning när författare och godkännare är samma person; M1 avgörs i metodens sakkunniggranskning; modellidentitet av motor/beräkningsberoenden/regelbas med miljöversioner separat och projektlevererad valideringsrapport som byrån bedömer och godkänner.

Steg 1 är AB1 + AB4a (v5.1-läsordning, risköversikt först, beräkningar i B1), granskat och fulltestat före eventuell separat beställd commit. Steg 2 är AB7 → AB2 → AB3 → AB4b → AB5 → AB6. Arbetsbördeprovet specificerar 40 alltid obligatoriska + 24 villkorade blockbedömningar och 12 unika scenarier i fyrtjänstfallet, med förifyllnad/återanvändning; det är inte uppmätt tidsåtgång eller 64 nya fritextsvar. AI-max blir 1 520 ord för fyra tjänster; huvudtextens riktbudget är 4 700 ord och måste provas vid implementationen.

Tidigare fem och sex källkompletteringar behålls. Endast tre befintliga Markdownfiler ändras. Kod, regelbas och sakkunnigstatus är oförändrade; inget är implementerat, committat eller pushat i detta steg. Dokumentkontroll görs; fullsvit körs inte för denna dokumentändring. Senast uppmätta kodtestresultat står i commitverifieringen nedan. `research_notes/` lämnas orört.

## A + B: sex ytterligare kompletteringar inarbetade, 2026-10-15

På användarens beställning har [befintlig D-ARB-plan](superpowers/plans/2026-10-11-d-arb-tjanststruktur.md#inarbetad-fortsättningsgranskning--sex-kompletteringar-2026-10-15) skrivits om med tjänstedetalj/delanalyser, faktisk betalningsinsyn, uppdragshanterbarhet, lokal leverantörsprövning, plattforms-/PSP-prov och löpande modellriskhantering. De fem tidigare kraven är bevarade och tilläggen ingår i modeller, frågor, bindningsmatris, dokumentkrav och acceptansprov. Ny AB7 preciserar spec §7.8; beroendeordningen är AB1 → AB7 → AB2 → AB3 → AB4 → AB5 → AB6. Designspec revision 31 är synkroniserad.

Planen skiljer delanalyser från nya risknivåer, uppdragsbeslut från dokumentattest samt grön programtestning från faktisk modellvalidering/feluppföljning. Befintliga katalogposter om kundrelationer, kundberoende, leverantörer och TF återanvänds. Endast plan/spec/STATUS ändras; ingen implementation, fullsvit, risk-/AI-regeländring, sakkunnigattest, commit eller push. Privat underlag och `research_notes/` lämnas orörda.

## A + B: fem källkompletteringar inarbetade i planen, 2026-10-15

På användarens beställning har den befintliga [D-ARB-planen](superpowers/plans/2026-10-11-d-arb-tjanststruktur.md#inarbetad-källgranskning--fem-bindande-plankrav-2026-10-15) kompletterats inom datamodell, granskningsfrågor, ändringsmatris, dokumentinnehåll och AB2–AB6. Kraven gäller sårbarhetsprövning per tjänst, faktorernas samverkan, konkret rutinlänk, egna rapporterings-/bevakningslärdomar och skilda utvärderings-/uppdateringsdatum samt blockerande lokal prövning av redovisad reduktion mot kontrollräckvidd. Designspec revision 30 är synkroniserad.

Den tidigare hänvisningen till research 11 §10 saknar motsvarande avsnitt i den aktuella arbetskopian; källstödet och det privata datumprovet hänvisas därför direkt i planen. Befintlig research är oförändrad. Endast plan/spec/STATUS ändras i detta steg. Kompletteringarna är ännu inte implementerade; kod, riskregler, AI-gräns, historiska paket och sakkunnigstatus är oförändrade. Ingen fullsvit, commit eller push; `research_notes/` lämnas utanför.

## A + B: datakontrakt och genomförande preciserade, 2026-10-15

Efter den inklistrade granskningen av trecommitskedjan har den befintliga [D-ARB-planen](superpowers/plans/2026-10-11-d-arb-tjanststruktur.md#a--b--konkret-kontrakt-inför-nästa-revision-2026-10-15) kompletterats med A + B:s datamodell, åtta frågor per tjänst, bindnings-/ändringsmatris och sex genomförandeuppgifter med acceptansprov. Designspec revision 29 beskriver samma planerade kontrakt. Separat lokal analysattest föregår sakgranskning av dokumentet, så att bindningen inte blir cirkulär. Kontrollräckvidd ska vara beskrivande och källbunden; motor och AI-gräns förblir oförändrade.

**Inte implementerat:** privat analysregister, formulär/CLI, nya räckviddsposter och dokumentformat v6. Aktuell leverans är fortfarande H6/v5. Sakkunnig/beslutsansvarig för M1–M4 är inte utsedd här. Endast tre befintliga Markdownfiler ändras i denna planrevision; ingen fullsvit körs om för den. Senast uppmätta kodläge är fortsatt 1 632 passerade och ett bortvalt livetest enligt commitverifieringen nedan, inte en ny körning. Ingen commit eller push; den inklistrade granskarens pushfråga räknas inte som beställning. `research_notes/` lämnas utanför.

## Godkänd uppdelning i tre commits, 2026-10-15

Användaren beställde den föreslagna trecommitsuppdelningen. Den byggdes i en separat lokal klon med backup av 621 arbetsfiler, staged/unstaged diffar och det ursprungliga indexet. Appens worktreeverktyg pekade på en annan, tom Git-katalog och användes därför inte för det faktiska repot.

1. **`8e7e83fb`**: skyddad AI-begäran, namn/precision och Bolagsverket med samlat registerintag. Officiellt API-kontrakt följer koden. H6:s kod-/testdiff är borttagen i detta mellanläge.
2. **`a08f6c5a`**: H6, inklusive båda presentationsrättningarna och regressionerna. Programkod, tester och regelbas matchar exakt innehållet före commituppdelningen.
3. **Dokumentation**: återstående research, plan, spec, README och denna status. Inga ytterligare program-/regeländringar ingår.

**Verifiering:** mellanläget gav **1557 passerade, 1 bortvalt livetest, 747.48 s**; H6-läget gav **1632 passerade, 1 bortvalt livetest, 754.91 s**. Båda kördes med kopians egen Python-/CLI-miljö och redan installerade beroenden. Före commits kontrollerades identiska testade filer, diffar och kända lokala namn, organisationsnummer och nycklar; inga träffar. Den avslutande dokumentationscommiten ändrar bara Markdown och behåller den verifierade programkoden.

Den första mellanlägeskörningen gav tio falleringar i `test_m2_hela_cli_kedjan_och_aterstallning` (tre län) och `test_m2_negativ_cli_skapar_inget_paket` (sju varianter), eftersom deras subprocessmiljö tappade `PYTHONPATH` och startade huvudrepots H6-installation. Det var ett blandat testläge. Egen lokal CLI-miljö löste isoleringen; kod och tester ändrades inte. Den körningen används inte som verifiering. Samtliga loggar och nodnamn finns i evidensmappen.

`research_notes/` är bevarad och utanför commitsen. Tidigare staging är säkerhetskopierad; slutindexet motsvarar commitkedjan. Ingen push, inget riktigt API-anrop och inga ändringar i privata byråprofiler eller tidigare exporter. A + B är valt men ännu inte implementerat. Backup och evidens: `~/.local/share/riskanalys/provkorningar/commituppdelning-20261015-155926`.


## H6: oberoende granskning, rättningar och valt fortsättningsspår, 2026-10-15

Två nya subagenter granskade H6:s dokument-/exportkedja respektive skriv-/dataskyddskontrakt, med den privata startkopian som avgränsning. Dokumentgranskningen fann två P2-presentationsfel: kontrolltabellen dolde att motorn nekat kontrollverkan när effektbelägg saknades, och risköversikten markerade inte okänt erbjudande/preliminära nivåer. Båda är rättade i `tabeller.py`. Åtta nya regressioner föll före rättningen; därefter passerade 50 riktade prov. Återgranskningen fann inga kvarstående åtgärdskrävande fynd i rättningen (29 prov samt två syntetiska markering-/källprov).

Skrivgranskningen fann inga konkreta H6-regressioner inom sitt scope (253 riktade prov samt ett separat 60-anropsprov med Testleverantor). Detta ersätter den uteblivna tekniska slutgranskningen från 2026-10-14 inom dessa avgränsningar, inte sakkunnig metodprövning eller ett verkligt språk-/byråprov. Ny fullsvit efter rättningarna: **1 632 passerade, ett bortvalt livetest, 729,24 s**, exitkod 0. Kod, tester och regelbas är oförändrade sedan fullsvitens start enligt hashjämförelsen. Regelbasvalidering, compileall och diffkontroll passerar; samtliga 326 jämförda motor-/regelbasfiler är byteidentiska mot H6-startkopian.

Användaren valde **A + B** för nästa revision: generell källbunden kontrollräckvidd och obligatorisk lokal granskning av byråns faktiska tillämpning. Inriktning och öppna konstruktionsfrågor är tillagda i [befintlig D-ARB-plan](superpowers/plans/2026-10-11-d-arb-tjanststruktur.md#valt-fortsättningsspår-a--b-2026-10-15), spec revision 28. Scenariotäckning, nytt lokalt granskningsintag och ny disposition är ännu inte implementerade. M1–M4 är fortsatt öppna.

Evidens: `~/.local/share/riskanalys/provkorningar/h6-granskning-20261015/`. En separat diff för H6:s kod/tester kan tillämpas på den privata startkopian (`git apply --check` passerar). Föreslagna commitgrupper finns i planen; inga commitobjekt har skapats, Git-indexet är bevarat och ingen push har gjorts. Historiska exporter och deras mätningar är orörda.

## Fördjupad strukturresearch efter H6, 2026-10-14

[Research 11 §9](research/11-kallkontroll-allman-riskbedomning.md#9-fördjupad-strukturresearch-efter-h6--2026-10-14) jämför aktuellt Word-prov med 24 primärkällor, inklusive fyra offentliga tillsynsbeslut och skriv-/tillgänglighetsvägledning. Ingen universellt bästa disposition är belagd. Förslaget är sex huvuddelar med risköversikt först, tydligare scenario-/exponeringsanalys per tjänst och full beräkningslogg i navigerbar B1 i samma Word-fil. En mekanisk utfallsförklaring ersätter inte saklig motivering av nivån.

Ny mätning: fyra beräkningstabeller står för 999 huvudord; återkommande källsuffix för cirka 892 ord, delvis överlappande. Dagens lokala dokumentinnehåll står för 4 346 ord utöver 1 750 förberedda skrivord. Förkortning behöver alltså omfatta mer än AI-text. Två nya nationella 2026-rapporter föreslås för relevansprövning men har inte aktiverats. Det livehämtade NRA-originalets hash stämmer med dagens katalog.

Endast research/status och en hänvisning i befintlig plan ändrade; ingen kod, riskmetod, regelbas, export eller commit. Rekommendationerna är ännu inte implementerade. Fullsviten har inte körts om för dokumentationsarbetet; ny evidens ligger i `~/.local/share/riskanalys/provkorningar/strukturresearch-20261014/`. Verkligt modellprov, medarbetarläsning och sakkunnig metodprövning återstår.

## H6 implementerat och tekniskt verifierat, 2026-10-14

D-ARB-tjanst-v5 har riktiga tjänste-, kontroll-, risk- och åtgärdstabeller, riskmatris, lokala beräkningsförklaringar och numrerade källor. Gemensamma kontrollbeskrivningar och exakt samma geografiska villkor samlas en gång. Cellinnehåll, källreferenser, ordning och visningsnummer ingår i sakgranskningen; CLI visar också tabellerna. En Word-fil innehåller huvudrapport, navigering och B1 efter sidbrytning. Äldre exporter är fortsatt verifierbara. AI får samma tillåtna data och schema, med nya längdgränser 400–750 ord per tjänst och kvalitativ scenariotext i riskdelen. Gamla skrivförsök får inte återanvändas som nygodkända v5-svar.

**Mätt fyrtjänstprov:** huvudtext 13 138 → **6 096 ord**, B1 5 078 ord, **10 tabeller**. Word-kompatibel rendering: **15 sidor huvudtext + 15 sidor bilaga/fynd**. Sidnummer fungerar; innehållsförteckningsfältets sidnummer behöver uppdateras i Word, medan den statiska länköversikten finns direkt. Samtliga fyra gamla höga fynd och alla tjänstebedömningar är exakt bevarade. Huvudtexten når alltså **inte** målet 3 500–5 000 ord / 8–12 sidor. Maxprovet med 3 000 skrivord ger 7 346 huvudord; båda visar längdvarning utan trunkering. Det realistiska läsprovet använder 1 750 ord manuellt förberedda, tjänsteanpassade svar, ingen riktig AI.

Startläget säkrades före kodändring; baslinjen gav 1 557 passerade tester. Subagenter implementerade modell/rendering, skrivkontrakt och käll-/utfallsförklaring. Bolagsverksgranskningen fann inget blockerande inom sin avgränsning (71 prov). Slutgranskningsagenten och skrivagentens sista kontroll stoppades av användningsgränsen; huvudagenten integrerade och självgranskade. Ingen oberoende slutgranskning påstås. Regelbas, motor, tillåtelselista och registerintegration har inga H6-ändringar enligt startfilernas hashjämförelse. En befintlig precisionsfråga vid mycket stora registerbelopp ligger utanför H6.

Slutlig fullsvit: **1 621 passerade, ett bortvalt livetest, 738,86 s**, exitkod 0 (`final-full.log`). Inga funktionella kodändringar efter körningens start; två rena layoutjusteringar och en tom slutrad kontrollerades separat. Tre extra tabellkontrakt tillkom efter insamlingen till fullsviten och passerade i den separata 13-provskörningen. Riktade slutprov: 51 passerade; separat layoutprov 10; tabellkontrakt 13 inklusive tre efterhandsprov för okända/uteblivna tjänster, skilda kontrollutfall och noll rapporter. Efter fullsviten passerade även alla 23 tabell-/renderingsprov på de sista layoutjusteringarna (`final-postsuite.log`). Regelbasvalidering, compileall och diffkontroll passerar. Regelbas 1.3.0 är fortsatt ej_granskad. Inga commits, pushar, riktiga API-anrop eller ändringar i riktiga profiler.

[Genomförande och kvarstående redaktionellt gap](superpowers/plans/2026-10-11-d-arb-tjanststruktur.md#genomförande-2026-10-14), spec revision 27. Artefakter och loggar: `~/.local/share/riskanalys/provkorningar/h6-20261014-203520/`; `provresultat.json` pekar på Word-provet, `jamforelse.json` binder före/efter och `maxresultat.json` visar gränsprovet. Metodfrågorna M1–M4 är fortsatt öppna; presentationen validerar inte riskmetoden.

## Reviderad H6-plan efter granskning, 2026-10-14

H6-planen och spec revision 26 ersätter föregående tvåfilsförslag: en Word-fil med bilaga efter sidbrytning. Nya planerade AI-intervall ger högst 750 ord per tjänst; ett maxlängdsprov och totalbudget ingår. Befintlig riskdel behålls som kort kvalitativ syntes, medan lokal tabell förklarar beräkningen. Före kodändring ska startläget säkras, Bolagsverksintaget granskas och fullsviten köras. Inget är committat eller implementerat genom denna planrevidering. Namngiven sakkunnig och kalenderfrist för metodbesluten är ännu inte utsedda.

## Dokumentplan H6 och metodspår, 2026-10-14

På användarens begäran har [befintlig H5-plan kompletterats med H6](superpowers/plans/2026-10-11-d-arb-tjanststruktur.md#h6--kortare-rapport-med-tabeller-och-separat-metodspår-2026-10-14). Fem genomförandeuppgifter täcker typade tabeller, mindre dubblering, lokala utfallsförklaringar/källor, separat verifierbar bilaga och ett komplett läsprov. Spec revision 25 markerar detta som planerat. Dokumentarbete kan utföras före metodkalibrering; fyra öppna metodbeslut hålls separat. Endast plan/spec/status ändrade i denna leverans, ingen program- eller regeländring.


## Källresearch och granskning av realistiskt utkast, 2026-10-14

[Research 11 §8](research/11-kallkontroll-allman-riskbedomning.md#8-ny-granskning-av-skrivande-riskmotor-och-realistiskt-utkast--2026-10-14) jämför samtliga 24 registrerade källors användning, kompletterande officiella webbkällor, kod och det realistiska utkastet. Mätning: 18 167 ord, noll tabeller; förberedda skrivsvar står för 3 264 ord före sammansättning. Diagnostiska motoranrop visar generell kontrollreduktion och snabb mättnad av TF-nivån. Rapporten föreslår scenario-/kontrolltabeller, mindre dubblering, bättre lokala motiveringar och metodprövning före kalibrering. Endast research/statusdokument ändrade; ingen riskregel eller export ändrad. Fullsviten har inte körts om; riktig AI-skrivkvalitet är fortfarande oprövad. Mätartefakter: `~/.local/share/riskanalys/provkorningar/granskning-20261014/`.

## Realistiskt fiktivt byråunderlag, 2026-10-14

Användaren bad om mer realistiska byråsvar. Ny separat profil i `~/.local/share/riskanalys/provkorningar/realistisk-byra-20261014` beskriver sju personer, 120 kunder och 5,4 mkr januari–september, med bokföring, bokslut, deklarationer och löner. Frågesvar och kontrollbegränsningar är individuellt skrivna och tydligt fiktiva. Täckning och omsättningssummering godkända; ordinarie kedja exporterade Word med 20 förberedda skrivdelar. Fyra höga granskningsfynd bevaras, bland annat ej bedömd sanktionskontrolleffekt och saknad utvärdering. Första försöket stoppade på övriga riskförhållanden; scenariosvaret korrigerades eftersom förhållandena redan täcks av befintliga frågor. Inga regler ändrades. Word och profil kontrollerades för kvarvarande generiska testnamn. Ingen riktig AI-användning, inga riktiga profiländringar och inga program-/teständringar. Läs `BYRANS-SVAR.md` och `LAS-MIG.md` i provmappen. Kostnadstak för livepilot är fortfarande inte angivet.

## Syntetiskt skrivprov från intag till Word, 2026-10-14

På användarens begäran kördes ordinarie dokumentkedja på komplett syntetisk profil med tre tjänster. Testleverantören gav 15 förberedda delsvar; ingen riktig AI eller register-API anropades. Bedömning, skrivning, granskning, Word-export och exportkontroll lyckades. Första exporten gav två höga fynd om saknad utvärdering. Efter en tydligt syntetisk utvärderingshändelse och omexport med samma skrivunderlag blev fyndlistan tom. Inget fastställdes och inga riktiga profiler ändrades. Nio riktade kedjetester passerade på 12,15 s; fullsviten kördes inte om eftersom programkod och tester är oförändrade.

Artefakter utanför Git: `/Users/gt/.local/share/riskanalys/provkorningar/20261014-193452-syntetisk` (LAS-MIG.md, resultat.json och två Word-exporter). Läskontrollen visar kapitel 7 före 6, dubblerade kontrolltexter samt intern M6-formulering i rapporten. Detta är observationer inför skrivfasen, inte rättningar. Fixturtexterna är avsiktligt repetitiva och utvärderar inte modellens skrivkvalitet. Kostnadstak för riktig skrivpilot har efterfrågats; inget liveprov ingår i denna körning.

## Samlat registerintag och bokslut, 2026-10-14

Användaren godkände att bygga registerflödet och därefter fokusera på den allmänna riskanalysen. Intaget kan nu välja SCB tillsammans med Bolagsverket, visa filialförslag (AB/FL), lokalt redigerbart verksamhetsutkast och exakt bokslutsomsättning med period. Grunduppgifter och valda förslag kan godkännas tillsammans redan vid starten. Medelantal anställda är stöd vid personantalfrågan. SCB-källor och äldre snapshotformat bevaras. Inga regelbas-/AI-ändringar ingår.

Läsaren stöder gen-base 2021-10-31 och avgränsade iXBRL-format; okänt eller tvetydigt bokslut ger en synlig notis och manuell komplettering. ZIP-original lagras privat och källan inkluderar dokument-ID, SHA256, fil, kontext och taxonomi. Omsättningsperioden godkänns uttryckligen och måste stämma med kund-/tjänstestatistik, även när statistiken anges senare.

Verifiering: initialt 14 röda parserprov och 11 röda adapterprov, därefter 156 riktade prov gröna. Syntetiskt webbläsarprov gick från hämtning till samlad start och nästa fråga. Det upptäckte fel ID för personalstödet; två nya UI-prov gick RED→GREEN. Oberoende granskning hittade periodkontroll som bara fungerade i ena svarsriktningen och ofångat dekomprimeringsfel; båda reproducerade före rättning. Efter dessa rättningar passerade 24 riktade prov. Regelbasvalidering godkänd med oförändrad summa och fortsatt ej_granskad. Återgranskningen efter rättningarna fann inga kvarvarande konkreta P1/P2 inom avgränsningen; 33 relevanta och 11 befintliga underlagsvalstester passerade. **Slutlig fullsvit på färdig kod:** `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY -u BOLAGSVERKET_CLIENT_ID -u BOLAGSVERKET_CLIENT_SECRET .venv/bin/pytest` gav **1 557 godkända, ett bortvalt livetest, 730,10 s**, exitkod 0. Logg: `/tmp/riskanalys-bv-intag-full.log`. Inga kod-/teständringar efter fullsvitens start; därefter endast dokumentation. Compileall och diffkontroll godkända. Syntetiska provservrar/fliken avslutade.

Manuell läskontroll av tidigare privat sparat verkligt original gav samma period, omsättning och medelantal som föregående manuella extraktion. Inga nya autentiserade API-anrop, ändringar i riktiga profiler, riktiga API-nycklar i tester, installationer, staging, commits eller pushar. Den verkliga pilotservern är inte omstartad. Syntetiskt webbläsarprov efter omladdning verifierade sparade svar, personalstöd och att avvikande verksamhetsutkast inte skriver över den kompletterade texten. Bildbevis utanför Git: `/Users/gt/.codex/visualizations/2026/10/14/01a13b5b-a065-7483-b9f2-537a445188c4/register-personalstod.png`.

## Bolagsverket HVD: första lokala läskommandot, 2026-10-14

Användaren har godkänt en första avgränsad anslutning och användning av sina lokala anslutningsuppgifter. `riskanalys bolagsverket ORGNR` visar aktuell företagsinformation och metadata för tillgängliga digitala årsredovisningar. Den befintliga privata nyckelfilen läser nu även `BOLAGSVERKET_CLIENT_ID` och `BOLAGSVERKET_CLIENT_SECRET`; token hämtas/förnyas i minnet. Nycklar/token skrivs inte ut eller sparas i resultat. Omdirigeringar tillåts inte, dataidentitet och svarsstorlek kontrolleras, delfel visas uttryckligen och 401 medger högst en tokenförnyelse per dataoperation. Övriga HTTP-fel ger ett svenskt fel utan råsvar.

Primärkällor och användning finns i [research 10 §14.5](research/10-kallkontroll-och-gapinventering-m2.md#145-bolagsverket-hvd-verifierat-kontrakt-och-första-läsväg-2026-10-14), med officiellt OpenAPI-kontrakt och SHA256, anslutningsanvisning 1.01 samt kodlistor. Spec revision 23, den befintliga registerplanen och README beskriver avgränsningen. SCB:s format och intag är oförändrade. Inga registeruppgifter blir automatiskt bekräftade profilsvar, riskregler eller AI-underlag. Intagsintegration, dokumentnedladdning och bokslutstolkning återstår.

Manuell livekontroll, separat från testerna: autentisering lyckades (3600 sekunders giltighet); /isalive gav HTTP 200 och OK. Därefter gjordes ett användarauktoriserat företagsuppslag och hämtning av de två senaste tillgängliga årsredovisningspaketen. Identitet, period, enhet och exakt kronprecision kontrollerades; balanssummor och tio jämförelseposter mellan åren stämmer. Original, extraherade uppgifter och sammanställning lagras privat utanför Git. Företagsnamn, nummer och belopp läggs inte i repot. Detta är en manuell kontrakts-/dataundersökning, inte en färdig generell årsredovisningsimport eller intagsintegration. Inga riktiga registerdata används som testfixturer.

Verifiering: 28 nya prov fallerade före implementation; efter implementation och kompletterande felvägsprov passerade 91 företagsdata-/nyckelfilsprov. Färsk helsvit utan Claude-, SCB- eller Bolagsverksnycklar gav **1 521 godkända och ett bortvalt livetest, 722,13 s**, exitkod 0. Logg: `/tmp/riskanalys-bolagsverket-full-pytest.log`. Den riktiga nyckelfilen är bortkopplad i provsviten. Inga produktions- eller testfiler ändrades efter helsvitens start; därefter endast dokumentation. Regelbasvalidering och diffkontroll är gröna. Regelbasens checksumma är oförändrad (`sha256:1e34b174e6882764c400613328df589a29f63c24875690929c0a87338dc7e5ff`). Inga tidigare arbetsändringar eller stageade filer har återställts; ingen staging, commit eller push har gjorts.

## Kedja, begränsad precision och namnfält, 2026-10-14

Spec revision 22 och planen `2026-10-14-kedja-precision-namnfalt.md` är genomförda efter användarens godkännande. Detta avsnitt ersätter revision 21:s beslut nedan om fristående analysdelar och generell maskering av härledda kundandelar.

- Kedjan är återställd: riskmotiveringen får de maskinellt godkända delarna om hot, sårbarheter och kontroller, och slutsatsen får riskmotiveringen. Endast AI:s egen text med olösta platshållare förs vidare. Ett namn som AI själv skrivit kan därför återföras utan att programmet bekräftar om namnet finns i profilen. Namnkontrollen görs efter alla anrop för tjänsten och påverkar aldrig följdanrop eller omförsök. Identitetsproven använder profilens verkliga syntetiska namn.
- De sex tillåtna kundandelarna (riskbransch, kontant, digitalt underlag, bankdata, nya och juridiska kunder) visas åter för AI i hela procent. Inom en halv procentenhet från en metodgräns visas bara sidan, exempelvis ”strax under 20 %” eller ”minst 20 %”, även exakt på gränsen. Lokala texter behåller decimalerna. Smågruppsskyddet går alltid före precisionsvisningen. Inga antalsfält har lagts till på tillåtelselistan.
- Alla 18 S-ARB-sårbarheter prövas fortsatt lokalt eftersom deras villkor läser fält utanför tillåtelselistan. S-KUND-01, S-KUND-02, S-KANAL-01, S-GEO-01 och S-KOMB-01 prövas lokalt när deras smågruppsvärden är maskerade eller okända; kundandelarna är inte längre alltid maskerade. I den använda syntetiska grundprofilen är dessa fem maskerade, alltså totalt 23 av 28 lokalt. S-VERK-01 och S-TJ-01–04 är öppna i samma profil.
- `namnfalt` anger vilka textfält som är personnamn. Endast P-ROLL.ffr_namn har egenskapen; ansvarsfunktionens rolltext har den inte. Namnfält måste vara personuppgifter av typen text. Saknad/falsk egenskap serialiseras inte, så historiska innehålls- och attestsummor består. En namnstoppad del följs nu hela vägen genom skrivning och granskning: programmets mall används i dokumentet och ett blockerande fynd kräver omskrivning med rollplatshållare och ny sakgranskning.
- Återkoppling om felaktiga platshållare och fält-ID anger ordningsnummer utan att citera texten. Numreringen räknar även giltiga rollplatshållare. Gränsindexet byggs en gång per dokument och skickas till delbyggarna; ett räknande prov täcker både tjänsteavsnitt och hela dokumentet. Ingen global cache införs.

**Härledningsprovet.** Alla antal från 0 till basen prövas för baserna i tabellen. Tabellen visar exakt härledbara antal utöver hela basen, utifrån den synliga riskbranschandelen och en känd kundbas. ”Steg” anger varje tal i den aritmetiska följden, inklusive ändpunkterna.

| Kundbas | Exakt härledbara antal, utom hela basen |
|---|---|
| 20 | 5–15 |
| 50 | 5–45 |
| 100 | 5–95 |
| 150 | 5; 6–144 (steg 3); 145 |
| 199 | 39; 40 |
| 200 | 5; 6–38 (steg 4); 39; 42–106 (steg 4); 118–194 (steg 4); 195 |
| 250 | 49 |
| 399 | 5; 394 |
| 401 | inga |
| 1000 | 5; 995 |

Hela kundbasen är exakt härledbar vid samtliga tio provbaser, upp till 1 000. Största provbas med andra exakt härledbara antal är också **1 000** (5 och 995). Det finns alltså ingen styrkt generell 200/400-gräns. Inga provade grupper på 0–4 eller restgrupper på 1–4 visas öppet. Baslinjeprovet bevarar grupperingen för hela procent plus sidan om metodgränsen, med hela kundbasen separat som godkänt undantag. Vid baserna 20, 100 och 1 000 jämförs också hela serialiserade AI-begäran för små grupper och restgrupper, inklusive andra poster, sårbarhetsutfall, schema, kedja och omförsök. Ett geografiprov har 90 av 100 som öppet kontrollvärde. Resultaten gäller prövade profiler och baser, inte alla möjliga kombinationer av uppgifter.

Regelbasen är fortsatt 1.3.0. Den enda regelbasändringen i denna omgång är `namnfalt: true` på P-ROLL.ffr_namn. Kontrollsumman går från `sha256:12180a9773ed9996c680e106b06e3a9e5f8b35203cf3482fb6a2867fb126c3d9` till `sha256:1e34b174e6882764c400613328df589a29f63c24875690929c0a87338dc7e5ff`. Äldre bedömningar måste köras om. Riskgränser, regler, källor och sakkunnigstatus är oförändrade.

Verifiering: den färska fullsviten gav **1 486 godkända och ett bortvalt livetest** (708,62 s), med båda API-nycklarna borttagna. Riktade beteendeprov kördes röda före kodändringarna. Första fullsviten hittade tre äldre testförväntningar (feltexter och namnfält i den historiska regelbasen); testerna anpassades till de beslutade kontrakten och omgranskades utan nya fynd, varefter hela sviten kördes på nytt. Oberoende slutgranskning och dokumentationsgranskning har inga åtgärdskrävande fynd. Regelbasvalidering och diffkontroll är gröna. Skyddade typfall, den gyllene M1-kedjan och befintligt Git-index är bevarade. Inga riktiga API-anrop, staging, commits eller pushar. Piloten väntar på separat godkännande och kostnadstak.

## Historik: rättningar enligt revision 21, 2026-10-14

Den tidigare slutgranskningen missade falska namnträffar och två integritetsproblem. De 1 433 gröna testerna nedan avser det tidigare läget och täckte inte dessa fynd. Rättningsomgången är genomförd enligt spec revision 21 och tillägget i den befintliga planen.

- Namnmatchning använder uttryckliga namnfält, hela namn och genitiv; rolltext och rollplatshållare behandlas inte som personnamn. Bo i bokföring, Eva i evaluering och VD i avdrag ger inte längre namnträff.
- Tidigare fri AI-text skickas aldrig vidare till senare delar. Även felmeddelanden om felaktiga platshållare och fält-ID är generiska, så att namn i AI-text inte citeras tillbaka vid omförsök. Varje del får det skyddade faktabladet, och namnkontrollen sker fortfarande lokalt efter alla delanrop. Därmed behövs inget undantag för återförda namn.
- Härledda andelar maskeras för AI om antal eller bas saknar tillåtelse. Även beroende sårbarhetsutfall och gränsmeningar skyddas. Lokal precision behålls. Detta ger mindre information i AI-texten; lokal analys och sakgranskning har kvar underlaget.
- Lokala namnstopp redovisas i CLI med orsak och konkret åtgärd och räknas inte som godkända förstaförsök. Anrops- och tokenmätning behålls.
- Decimaler i själva metodgränsen och intagets visning rättas. Ingen riskgräns eller riskbedömning ändras. Metodgränserna använder den befintliga typade villkorstolkningen och ett lokalt index som återanvänds inom AI-underlaget och intagsöversikten. Fristående lokala dokumentuppslag bygger fortfarande ett eget index; ingen global cache införs.

Verifiering: nya regressioner har körts röda före rättningarna. Hela sviten gav **1 461 passerade och ett bortvalt livetest** (699,99 s), med API-nycklarna borttagna. Granskning av namn/kedja/rapportering upptäckte återkopplingsläckan som rättades med ett eget kedjeprov och granskades igen. Precision och integritet kontrollerades mot kod och riktade prov. Regelbasvalidering och diffkontroll är gröna; kontrollsumman är oförändrad. Skyddade jämförelsefiler och befintligt index är bevarade. Inga riktiga API-anrop, commits eller pushar.

## Namn, maskering och avrundning, 2026-10-14

Planen för spec revision 20 är implementerad med fallerande regressionstester före kodändringarna. Personnamn kontrolleras lokalt efter tjänstens alla AI-anrop, små grupper och små restgrupper får samma maskeringstext och andelar nära metodgränser visas på rätt sida om gränsen. Separat granskning av uppgifterna och slutgranskning är godkända utan kvarstående fynd. Fullsviten gav **1 433 passerade och ett bortvalt livetest** (683,92 s), med båda API-nycklarna borttagna. Regelbasvalideringen och diffkontrollen är gröna. De skyddade jämförelsefilerna och den frysta M1-kedjan är oförändrade. Hela sviten kördes en gång efter integration och slutgranskning; varje koduppgift hade egna röda och gröna regressionstester. Inga riktiga API-anrop, commits eller pushar har gjorts under denna omgång.

## Skyddad AI-begäran, 2026-10-13

Det som skickas till AI skyddas nu enligt spec 8.4.10. Motorns bedömning, nivåer, regelspår, regler och gränser är oförändrade; det som ändras är vad AI får se.

- AI får aldrig nivåer, regelspår eller nivåmeningar. Faktabladet och de låsta instruktionerna innehåller inga av dem. Återkopplingen vid omförsök valideras mot det AI faktiskt har sett (de skyddade låsta texterna), aldrig mot motorns riktiga nivåmeningar; de riktiga låsta texterna används bara lokalt vid den slutliga kontrollen före dokumentbygget. Ett mutationsprov byter alla nivåfält (inneboende, terrorfinansiering, kvarstående och sanktionsrisken) och alla regelspår mot andra värden och kräver att hela begäran är identisk, även när ett första svar innehåller kandidatmeningar för nivåerna och tjänsten får ett omförsök. Ett andra prov ändrar `P-RISK.pep` (en uppgift utanför tillåtelselistan som ändrar motorns nivå) och kräver samma identitet.
- Sårbarheter vars villkor bygger på uppgifter utanför tillåtelselistan, eller på smågruppsskyddade värden, har utfallet ”prövas lokalt” i stället för ja eller nej. Av de 28 sårbarheterna läser 18 (alla S-ARB, byråövergripande indikatorer som PEP-anknytning och ägarstruktur) fält utanför tillåtelselistan och får alltid ”prövas lokalt”. Fem (S-KUND-01, S-KUND-02, S-KANAL-01, S-GEO-01 och S-KOMB-01) får det när smågruppsvärden är maskerade eller okända, vilket de är i den syntetiska provprofilen (testprofilens kundantal är 0). Fem (S-VERK-01 och S-TJ-01 till S-TJ-04) behåller ja eller nej. I provprofilen prövas alltså 23 av 28 lokalt.
- Kontrollernas kategorifält (utformning, genomförande och effekt, 39 fält för 13 kontroller) är tillåtna efter beslut 2026-10-13 och står i `regelbas/tillatelselistor.yaml` med grund i en kommentar. AI:s kontrollstatus bygger enbart på dem. Belagd riskreduktion avgörs lokalt. Eftersom AI inte får veta om en kontroll har belagd effekt underkänner valideringen i kontrolldelen varje påstående om att risken minskar, oavsett vilken kontroll stycket hänvisar till, och återkopplingen säger att programmet avgör det lokalt. Verben minskar, begränsar, reducerar och sänker fångas i presensform (utan efterföljande inte, ej eller aldrig), och prompten för kontrolldelen nämner samma fyra verb. Andra formuleringar och böjningsformer fångas bara av sakgranskningen. Kontrollernas fria utfallstext skickas inte.
- Prov visar att begäran är identisk för 0, 1, 3 och 4 kunder, för ett maskerat litet komplement (96, 97 och 99 av 100; 100 av 100 visas öppet när härledningens källfält också är tillåtna), vid saknad bas, för ett smågruppsfält och en ja/nej-uppgift utanför tillåtelselistan, för kontrollernas fria utfallstext och vid omförsök, även när ett svar innehåller nivåmeningar.
- Bekräftade personnamn, även genitiv och förekomster i oklarhetsfrågor, prövas bara lokalt efter tjänstens alla AI-anrop. En träff ersätter den berörda delen med programmets mall och ger ett blockerande granskningsfynd. Namnkontrollen före dokumentbygget finns kvar. Omförsök får ingen namnberoende återkoppling; identitetsproven använder profilens verkliga syntetiska namn och kräver samma begäran och samma antal anrop för profiler med olika namn.
- Både en liten grupp och en liten restgrupp visas för AI som ”skyddat värde, prövas lokalt”. Ett identitetsprov kräver samma hela begäran för 3 och 97 av 100. Det ersätter det tidigare beslutet att låta maskeringstypen avslöja vilken sida den lilla gruppen ligger på.
- Andelar nära metodens gränser visas med en eller två decimaler, till exempel 19,5 % och 20,4 % mot gränsen 20 %. När två decimaler inte räcker används ”strax under” eller ”strax över”. Faktabladet och talplatshållarna behåller visningen; intervall lagras utan exakt tal. Smågruppsskyddet går före precisionen.
- Andelar nära 0 och 100 % visas som ”mindre än 1 %” och ”mer än 99 %” i de låsta styckena, faktabladet och platshållarna. De lagras som intervall och aldrig som ett exakt tal.
- Katalogkoder och kontrollsummor står bara i referenser och i bilaga D-ARB.B1. I löptexten visas regelpaket med namn och län i hindertexter, och registrerade källor, till exempel EU-269-2014, med titel.
- Fastställelse kräver aktuellt format i varje tjänsteavsnitt. Ett tjänsteavsnitt utan formatmarkering eller med äldre format stoppar fastställelsen innan paketet byggs (gäller regelbaser med omfattningsmetod). Fastställda paket byggs inte om och kan fortfarande läsas.
- Den äldre skrivvägen är stängd i både `kor_skrivning` (på en regelbas utan omfattningsmetod) och `skriv_avsnitt`: varje leverantör som inte är testleverantören vägras med felet ”äldre skrivvägen” innan något anrop görs. Testleverantören fungerar som förut, och en leverantör med riktigt namn stoppas inte på en regelbas med omfattningsmetod. Det frivilliga livetestet för den äldre vägen (`tester/live/test_claude_live.py`) är ersatt av ett enhetsprov i `tester/enhet/test_aldre_skrivvag.py`; den nya vägen täcks av `tester/live/test_delcache.py`.

Regelbasen är fortsatt 1.3.0. Den enda ändringen under `regelbas/` är de 39 kategorifälten i `regelbas/tillatelselistor.yaml`; inga regler, gränser, källor eller sakkunnigstatus är ändrade. Kontrollsumman har ändrats av tillåtelselistan, från `sha256:7e9a26f1dc06025ba906d355b631f1ca3a9f142ce50ae18df4909397dc905800` till `sha256:12180a9773ed9996c680e106b06e3a9e5f8b35203cf3482fb6a2867fb126c3d9`. Bedömningar och granskningar som gjorts under 1.3.0 före ändringen är därför inaktuella och måste köras om. `tester/typfall/`, `tester/fixturer/`, `tester/enhet/test_m1_gyllene_dokument.py`, `tester/enhet/test_manifest.py` och `tester/enhet/test_faststall.py` är oförändrade mot utgångsläget (den nya fastställelsespärren prövas i `tester/enhet/test_formathinder.py`). Dokumentformatet är fortsatt `D-ARB-tjanst-v4`.

Verifiering efter kompletteringarna 2026-10-14: slutlig fullsvit är grön, **1 433 tester passerar och ett livetest är bortvalt** (683,92 s), med båda API-nycklarna borttagna ur körmiljön; siffran gäller efter slutgranskningen av namn, maskering och avrundning. Regelbasvalideringen (regelbas 1.3.0, 107 krav, 11 tjänster) och `git diff --check` är gröna. Inga riktiga API-anrop har gjorts. Inget är committat: ändringarna väntar på användarens godkännande för commit.

Kvar:

- En pilot på en tjänst med effort `medium`, efter användarens godkännande och med ett uttryckligt kostnadstak inklusive omförsök, för att pröva formuleringen för faktorer under metodens gräns och utfallet ”prövas lokalt”.
- Ett beslut om vilka fler uppgifter AI får se. Tillåtelselistan är medvetet snäv, och många sårbarheter får utfallet ”prövas lokalt” tills fler fält tillåts.

## Klartext i låsta stycken (format v4), 2026-10-12

De låsta styckena i tjänsteavsnitten skrivs nu i klartext. Motorns utfall och gränserna är oförändrade; det som ändras är hur utfallet beskrivs.

- Kortnamn används i stället för fält-ID.
- Villkor skrivs i ord, till exempel ”Sårbarheten gäller om andel kunder i riskbranscher är minst 20 %”.
- Ja/nej-uppgifter skrivs som: uppgiften ”<kortnamn>” är ja.
- När en faktor förekommer men ligger under metodens gräns anger en gränsmening det: ”Faktorn förekommer: andel kunder i riskbranscher är 15 %, men det ligger under metodens gräns på 20 % för automatiskt riskpåslag.”
- Sektorsreferensen anges med källans titel, nivå, skala och sida, både i tjänsteavsnitten och i metodavsnittet D-ARB.2 (gemensam mening).
- D-ARB.2 skriver tjänstens namn, punkterna i ord och hindertexter med namn i stället för ID. Uppföljningsavsnittet namnger saknade uppgifter med kortnamn. Tjänstebeskrivningen dubblerar inte längre etiketterna.

Spårbarhet: varje stycke behåller sina referenser, och D-ARB.2:s tjänstestycken har nu även sektorsreferensens ID och källa. Bilagan D-ARB.B1 visar kortnamn och fält-ID för varje uppgift och listar nu även härledda andelar med källan Härledning: antal/bas. I löptexten står ”härledd ur bekräftade uppgifter”.

Faktabladet till AI använder kortnamnen och skriver gränsmeningen bara när det visade värdet inte är skyddat; 0 och 3 kunder ger samma text. Sårbarhetsmodulen ber AI skriva att faktorn förekommer men ligger under gränsen.

Regelbasen är 1.3.0 med 56 kortnamn (51 fält i låsta stycken och hindertexter, bland dem de åtta omfattningsfälten som D-ARB.2 namnger, och 5 härledda andelar). Inga regler, gränser, källor eller sakkunnigstatus är ändrade; status är fortsatt `ej_granskad`. Ett saknat kortnamn serialiseras inte, så historiska attestsummor är oförändrade (prov mot frysta summor).

Formatet är `D-ARB-tjanst-v4`. Utkast i v3 måste skrivas om och sakgranskas på nytt. Regelbashöjningen gör också tidigare bedömningar inaktuella, så en v3-granskning kan inte fastställas. Fastställda paket byggs aldrig om och är oförändrade.

Verifiering: slutlig fullsvit är grön, **1 327 tester passerar och två livetester är bortvalda** (672,36 s), med båda API-nycklarna borttagna ur körmiljön; siffran gäller efter slutgranskningens rättningar (id_till_namn med rätt versal/gemen, referenser i D-ARB.2, gemensam gränsmening, kortnamn för de åtta omfattningsfälten, gyllene prov för den frysta M1-kedjan). Regelbasvalideringen (regelbas 1.3.0, 107 krav, 11 tjänster) och `git diff --check` är gröna. Diffen mot utgångsläget är tom för `regelbas/kataloger/sarbarheter.yaml`, `regelbas/kundfalt.yaml`, `tester/enhet/test_faststall.py`, `tester/enhet/test_manifest.py`, `tester/typfall/` och `tester/fixturer/regelbas_v0/`.

Kvar:

- Nästa pilot ska kontrollera att AI inte skriver att en sårbarhet under gränsen ”inte gäller”.
- Ett beslut återstår om sårbarhetens utfall (ja/nej) för villkor ”> 0” på smågruppsandelar. Det skiljer 0 från 1–4 kunder i faktabladet och fanns före denna ändring. Löst 2026-10-13 för S-GEO-01: se avsnittet Skyddad AI-begäran.
- Återanvändning av v3-utkast byggs inte (beslut 2026-10-12).
- Kravsummorna är oförändrade, men paketsummorna har ändrats av regelbas 1.3.0. Underlaget för sakkunniggranskning av paketen behöver därför tas fram på nytt för 1.3.0.

## Pilot efter kalibreringen, 2026-10-12

Claude Sonnet 5.5 skrev tre tjänster åt den syntetiska byrån: löpande bokföring (T-RED-01), deklarationer (T-RED-03) och betalningar och attest i kundens namn (T-RED-05). Varje tjänst skrevs med effort `medium` och `high` på samma bedömning. Kostnadstaket var 10 USD; körningen kostade 2,42 USD.

| Tre tjänster, fem delar var | `medium` | `high` |
|---|---|---|
| Godkända förstaförsök | 12 av 15 | 13 av 15 |
| Reservmall | 0 | 0 |
| Kostnad | 0,81 USD | 1,61 USD |
| Tid per tjänst | 2–3 min | 5–6,5 min |

Före kalibreringen underkändes alla tio förstaförsök i en tjänst, och delen sårbarheter blev reservmall med båda effortnivåerna. De fem underkända förstaförsöken i den nya piloten godkändes efter omförsök: tre var för långa, ett använde få rapporter som belägg för litet hot och ett saknade referensen till ett tal. Texterna är konkreta och byråspecifika i båda nivåerna; möjliga överlapp skrivs som scenario. `high` ger något mer detaljerade kontroll- och övervakningsavsnitt. `medium` är ett preliminärt val för fortsatt provning, inte ett slutligt modellval. Piloten täcker ännu inte bolagstjänster eller skatterådgivning utöver deklarationer.

Piloten visade tre fynd:

- I fem av sex körningar skrev AI interna kommentarer i dokumentet, till exempel ”underlaget lämnas inte till AI”. Formuleringen kom från faktabladets och de låsta instruktionernas egna texter. De är nu neutrala (”underlaget finns i byråns lokala belägg”), systemprompten ber AI skriva att underlaget behöver granskas lokalt, och valideringen underkänner kommentarer om vad AI har fått. Beskrivningar av teknik, som ”AI-verktyg” eller ”fakturor som tolkas av AI”, godtas.
- Sårbarheten kunder i riskbranscher redovisas som att den inte gäller, fast 15 % av kunderna finns i riskbranscher. Metodens gräns för automatiskt riskpåslag är 20 %. Texten ska säga att faktorn förekommer men ligger under gränsen; tröskeln ändras inte. Det ingår i planen för klartext.
- De låsta styckena visar fält-ID, villkorsuttryck och sektorskoder. En plan för klartext tas fram och granskas innan formatet `D-ARB-tjanst-v4` byggs.

## Kalibrering efter piloten (planens del C), 2026-10-12

Piloten med Claude på den syntetiska byrån (en tjänst, Sonnet 5.5, effort `medium` och `high`) visade två systematiska fel. Prompten angav inga ordgränser, så alla första försök blev för långa. Kombinationsregeln underkände varje sårbarhetsstycke som nämnde två tillämpliga sårbarheter, så delen sårbarheter föll tillbaka till reservmallen.

- Varje delmodul anger nu delens ordintervall ur `LANGD`. Prompt och validering har samma källa, och promptens kontrollsumma följer gränserna.
- Kombinationsregeln ersätter regeln i avsnittet om granskningsrättelser nedan. Ett analysstycke underkänns när det påstår ett samband (samverkar, tillsammans, kombination, förstärker) och refererar minst två faktorer, alltså sårbarheter eller faktauppgifter. Att två faktorer gäller utan påstått samband godtas. Formuleringen ”ingen belagd kombination” godtas i analys enligt spec 8.4.4, liksom ”inga belagda kombinationer” och ”ingen kombination är belagd”. Systemprompten och sårbarhetsmodulen föreslår den formuleringen, ber om ett stycke per kategori och förbjuder sambandsord i analysstycken.
- Omsättningskontrollen räknade härledda andelar (0–1) som kronor i summan av tjänsternas intäkter. När hela omsättningen fördelades på tjänsterna underkändes därför underlaget. Andelsfälten räknas inte längre.

Verifiering: varje ändring har ett regressionstest som fallerade före rättningen, bland annat tre tjänster på 3 000 kr mot en omsättning på 9 000 kr och ett påstått samband mellan en sårbarhet och en faktauppgift. Fullsvit: **1 240 passerar, två livetester bortvalda** (695,91 s), utan API-nycklar i körmiljön. Regelbasvalidering och `git diff --check` är gröna; kontrollsumma och sakkunnigstatus är oförändrade. Inga riktiga API-anrop har gjorts under denna rättningsomgång. Del C:s tre ändringar är committade lokalt (e10d2d4, c4fa39f, a6d4ce9), och rättelserna efter granskningen är committade i en egen commit efter dem. Grenen är pushad till draft-PR #1.

Den nya piloten efter kalibreringen redovisas i avsnittet ovan.

## Rättelser efter avbruten pilot, 2026-10-12

Användaren rapporterade att piloten på en syntetisk byrå med Sonnet 5.5 och effort `high` stoppades efter åtta anrop, varav fyra klipptes vid 16 000 utdatatoken. Delanropens gräns är nu 64 000 token och anropen använder den befintliga strömningen. Ett tidigare `max_tokens`-avbrott i samma del hindrar höjning av effort i sista omförsöket, även om ett senare försök underkänns av ett annat skäl. Avbrottsmeddelandet anger anropets faktiska tokengräns.

Endast faktapoststatus `okänd` kräver `[VERIFIERA]` och oklarhet. Bekräftade maskerade värden med status `skyddad` får refereras utan dessa krav; deras exakta tal är fortfarande otillåtna som talplatshållare. `riskanalys skriv --effort` valideras och styr hela v3-körningen även med testleverantören. Valet sparas i manifestet och faktisk effort sparas per försök. Piloten kan därför jämföra `medium` med `high` på samma bedömning. Längdgränserna i `LANGD` är oförändrade.

Verifiering: tio regressioner fallerade för token/skydd och tre för körningens effort före rättningarna. Riktad svit: 87 passerar. Slutlig fullsvit: **1 226 passerar, två livetester bortvalda** (655,29 s), med båda API-nycklarna borttagna ur körmiljön. Regelbasvalidering och `git diff --check` är gröna. Ingen ny pilot eller riktiga API-anrop har körts av Codex. Inga commits eller pushar har gjorts.

## Rättelser efter granskning av AI-skrivningen, 2026-10-12

Claudes fem fynd är kontrollerade mot implementationen och rättade med fallerande regressionstester före respektive ändring. Permanenta leverantörsfel stoppar skrivningen direkt: 400, 401 och 403 ger ett meddelande med orsak och åtgärd. Endast 429, 5xx och nätverksfel får bli misslyckade försök. Slut på förberedda testsvar ger åter ett fel. Serverns fria feltext skickas inte tillbaka till AI.

AI kan ange `{period:ID}` med samma faktareferens eller skriva ”under statistikperioden”. Perioden sätts in från faktabladet före sakgranskning; fria datum, saknad period och trasiga platshållare underkänns. Kombinationskontrollen kräver scenario när minst två refererade sårbarheter gäller eller är okända, eller när analysen använder samverkansord. Sårbarhetsmodulen anger alla fem kategorierna `kund`, `kanal`, `geo`, `tj` och `verk`. Faktabladet sparas i tjänstresultatet; den separata dubbleringen `faktablad.json` är borttagen.

Verifiering: slutlig fullsvit är grön, **1 213 tester passerar och två livetester är bortvalda** (653,71 s), med båda API-nycklarna borttagna ur körmiljön. Regelbasvalidering och `git diff --check` är gröna. Regelbasens kontrollsumma och sakkunnigstatus är oförändrade. Inga riktiga API-anrop, commits eller pushar har gjorts. Den tidigare verifieringen nedan gäller implementationen före dessa rättelser.

## AI-skrivning från faktablad, 2026-10-11

[Planen](superpowers/plans/2026-10-11-ai-skrivning-fran-faktablad.md#genomförande-2026-10-11) är implementerad i del A och B. Programmet skriver tal, risknivåmeningar, sektorsreferens och låsta stycken. Fem AI-delar per tjänst körs i följd med separat schema, validering och högst två omförsök. Alla försök sparas direkt. Vid fortsatt fel används en reservmall som ger ett blockerande granskningsfynd. Dokumentformatet är `D-ARB-tjanst-v3`; grinden omtolkar råsvaren, omvaliderar dem och jämför fryst faktablad och dokument. Ändrad text eller format kräver ny sakgranskning.

AI får skyddade faktablad och säkra sammanfattningar av låsta stycken. Lokala källtexter, personnamn, fritext och omaskerade smågruppstal skickas aldrig med de låsta styckena. Regelbas `1.2.0` och dess sakkunnigstatus är oförändrade.

Mätningen i uppgift 4 är byggd: sammanställning per körning redovisar förstaförsök, samtliga anrop, felklasser och in-/ut-/cachetoken; kostnadsfunktionen tar uttryckliga priser. Ingen betald pilot är genomförd, så hypotesen att fyra av fem underkännanden försvinner är **inte uppmätt**. Design B, befintlig standardmodell och effort är preliminära tills utvärderingen i spec 8.4.8 är genomförd. Design A, byråövergripande AI-avsnitt och kryssfrågorna i 14.5 återstår enligt planens avgränsning.

Verifiering: slutlig fullsvit med syntetiska data är grön, **1 183 tester passerar och två livetester är bortvalda** (656,80 s), utan API-nycklar. Regelbasvalideringen är grön och kontrollsumman oförändrad. Den oberoende kodgranskningens fynd har fått regressionstester, rättats och återkontrollerats utan kvarstående anmärkningar. Inga riktiga API-anrop har gjorts. Inget är committat eller pushat i detta genomförande.

## Läge

**Fas:** M2:s tekniska implementation, lokalt fullständigt intag och SCB-registerförslag är införda. Regelbasen är `1.3.0`. Juridisk sakkunniggranskning, M3:s modellprov och M4:s verksamhetsprov återstår.

**Aktuellt:** [M2-planens genomförandelogg](superpowers/plans/2026-10-10-m2-regelbas-v1-och-juridisk-granskning.md#genomförande-2026-10-10) beskriver implementation, verifiering och överlämning. Aktuell regelbas `1.3.0` har 107 krav, 11 tjänster, 283 fält, 24 källor, 21 hot, 28 sårbarheter, 13 kontroller och tre länspaket. [Intagsplanen](superpowers/plans/2026-10-10-intag-och-hel-riskbedomning.md) och [registerplanen](superpowers/plans/2026-10-10-registerhamtning.md) beskriver de efterföljande användarflödena. **Ingen verklig sakkunnigattest har tillkommit; M2-etappen är ännu inte juridiskt klar.** M2-koden och rättelserna versioneras som teknisk baslinje på `codex/m0-m1`; verkligt juridiskt godkännande återstår.

| Steg | Status |
|---|---|
| Genomgång av källmaterial | Klar |
| Gemensam förståelse av mål och målgrupp | Klar |
| Val av omfattning (alternativ C) | Klar |
| Val av arkitektur (alternativ 2) | Klar |
| Fördjupad research (EU-regelverk, metod, teknik) | Klar |
| Genomgång av två fullständiga tillsynsbeslut från 2026 | Klar 2026-10-09. [Research 09](research/09-tillsynsbeslut-2026.md): vad Länsstyrelsen underkänner, bristmönster B-23–B-29. |
| Bevarat tillsynsmaterial och granskningsfall | Importerat 2026-10-09: 79 originalfoton, OCR och 14 handlingar i lokalt arkiv utanför repot. [Två syntetiska fall](research/typfall/tillsyn-2026.json), 17 förväntade fynd och fem kontrollvarianter. **Facitutkast, ej sakkunniggranskat; produktutvärdering ej körd.** |
| Strukturförslag och spec, revision 1 | Klar, granskad av Codex 2026-10-08. Sex brister påtalades och godtogs. |
| Spec, revision 2 | Klar, granskad av Codex 2026-10-08. Arkitekturens riktning godkänd, åtta ändringar påtalades och godtogs. |
| Spec, revision 3 | Klar, granskad av Codex 2026-10-08. Fem kvarvarande fynd (två höga, två medel, ett lågt) godtogs. |
| Spec, revision 4 | Klar. Ligger till grund för implementeringsplanen. |
| Spec, revision 5 | Klar. Krav har `lydelser` (lista), efter Codex granskning av planen. |
| Spec, revision 6 | Klar. Sakkunnigstatus binds till en kontrollsumma, efter Codex andra granskning av planen. |
| Spec, revision 7 | Tillsynsmaterialet kopplat till intag och regelbas i M2, granskningsprov i M3 före första riktiga byrå, rutinernas genomgång i M5 och utvidgad provtillsyn i M7. |
| Spec, revision 8–9 | Sakkunnigs godkännande binds till refererade lydelser, sakgranskning till texten med insatta namn, tidigare paket verifieras före användning, och ett saknat eller skadat manifest ger ett fel med instruktion om återställning. |
| [Implementeringsplan M0–M1](superpowers/plans/2026-10-08-m0-m1-grund-och-tunn-kedja.md) | Skriven, 22 tasks. Granskad av Codex fyra gånger 2026-10-08–09; alla fynd åtgärdade. Spårning från tillsynsbrist till etapp finns i planen. Planens kod byggd i en tom mapp med [provkörningsverktyget](superpowers/plans/verktyg/README.md) 2026-10-09: 452 passerar. Godkänd av Codex för implementation med syntetiska data. Genomförd 2026-10-10; avvikelser och rättelser står sist i planen. |
| Senaste kodblocksgranskningen | Codex bekräftade 2026-10-09 att 446 tester passerar, att de fyra regressionstesterna för sakkunnigstatus, sakgodkännande och tidigare paket fallerar före rättningen och passerar efter, och att arkivets 173 kontrollsummor stämmer. Två kvarstående punkter: ett skadat manifest gav en krasch i `verifiera` och `faststall`, och Task 22 tog bort facitpunkten ur nästa steg. **Båda rättade i planen 2026-10-09.** Sju nya eller skärpta tester fallerar mot planens tidigare kod och passerar efter. Hela den återskapade sviten: 452 passerar, ett livetest bortvalt. Codex godkände därefter planen för implementation och reproducerade 452 passerande tester och ett bortvalt livetest. |
| Etapp M0 (grund) och M1 (tunn kedja) | Klara 2026-10-10. Typfallet och återställningsprovet passerar. Koden är införd i repot enligt planens 22 tasks, testerna skrivna före koden. Hela sviten: 495 passerar, ett livetest bortvalt, utan `ANTHROPIC_API_KEY` och med testleverantören. Hela kommandokedjan körd för hand med syntetiska uppgifter i en datamapp med mellanslag och å, ä, ö: med en signerad testkopia av regelbasen fastställs och verifieras paketet; med repots regelbas stoppas fastställelsen eftersom kraven och paragrafkartan inte är sakkunniggranskade. Paketet återställt från säkerhetskopia i en tom datamapp och verifierat. M0–M1 är granskat av Codex och versionshanteras på `codex/m0-m1`. |
| Slutgranskning av M0–M1 | Gjord 2026-10-10 av en fristående granskare (Claude Opus). Inga kritiska fynd. Sex viktiga fynd rättade med tester som fallerade före rättningen: risknivåer som saknades eller stod i en annan form i AI-texten, okända rollplatshållare som blev `[VERIFIERA: …]` i ett fastställt dokument, systemfiler från Finder som gjorde paketet ogiltigt, saknade uppgifter i manifest som gav en krasch, profilvärden som inte prövades mot fältregistret och en sökväg med annat skiftläge som kringgick spärren mot byrådata i repot. Tretton mindre punkter förs till M2–M4 (förteckning sist i planen). Codex granskade därefter implementationen samma dag och fann två brister till, båda rättade med tester som fallerade före rättningen: AI:ns öppna frågor kunde följa med till fastställelse utan att hanteras, och en handredigerad profil kunde ha status bekräftad eller ej tillämplig utan källa, datum, bekräftare eller motivering. Regressionstesterna i Task 22 fångar de fel de skrivits för, prövat genom att felen återinförts i en kopia. **Tillsynsfallens 17 fynd är inte prövade av M1:s tester.** |
| Källkontroll inför M2 | [Research 10](research/10-kallkontroll-och-gapinventering-m2.md) kompletterad av Codex 2026-10-10: rapporteringsundantag, registrering enligt PTL 7 kap., avgränsning av punkt 23, tre länspaket och separat AMLR-utkast. Tio källfilers storlek och SHA-256 stämmer; paragrafuttag omfattar PTL 142 lydelser/141 lagrum, PTF 29 och 31 per föreskrift. Visuell jämförelse av tabell 1 på sidorna 5–6 visade samma kontroll- och dokumentationskrav. Juridisk granskning återstår. |
| [Implementeringsplan M2](superpowers/plans/2026-10-10-m2-regelbas-v1-och-juridisk-granskning.md) | Skriven och självgranskad av Codex på användarens begäran 2026-10-10. 18 uppgifter med filer, gränssnitt, kontrakt, grindar, tidsestimat och överlämning till M3. Alla tretton restpunkter har placering. Teknisk implementation och verklig sakkunniggranskning redovisas separat. **Teknisk implementation och kontrakt är införda; se genomförandeloggen och färsk verifiering nedan.** |
| Rättat researchverktyg | `lydelsetexter.py` hanterar nu SFS i kommandoraden, datumversioner och felkoder. Åtta regressioner fallerade före rättningen; samtliga nio verktygstester passerar. Färsk fullsvit 2026-10-10: **504 passerar, ett livtest bortvalt**, utan API-nyckel (14,81 s). Uttag via CLI prövat för alla paragrafer i de fem lokala rättskällorna; tre M1-paragrafsummor bevaras. Ingen ändring i `src/` eller den operativa regelbasen i denna planeringsomgång. |

## Beslut

| Datum | Beslut | Motivering |
|---|---|---|
| 2026-10-08 | Målgrupp: konsultbyråer för egen efterlevnad, sedan andra företag | Största sektorn under Länsstyrelsens tillsyn och flest sanktioner. Referensfall finns. |
| 2026-10-08 | Omfattning C: verksamhetsnivå först, datamodell förberedd för kundnivå | De flesta sanktioner gäller verksamhetsnivån. Kundnivån kräver personuppgifter och integrationer. |
| 2026-10-08 | Arkitektur 2: regelbas och deterministisk motor, AI som skribent | Reproducerbart, spårbart och testbart. Löser problemen i det tidigare AI-utkastet. |
| 2026-10-08 | Python, YAML, pydantic, pytest, Claude via officiell SDK | Läsbart för en byggare med AI-hjälp. Bra stöd för Word och AI. |
| 2026-10-08 | Kärna och CLI först, webbgränssnitt senare | Kärnan är det svåra. Gränssnittet kan läggas ovanpå. |
| 2026-10-08 | Byggs med Claude Code och Codex | Kräver gemensamma regler i `AGENTS.md` och `CLAUDE.md` och många tester |
| 2026-10-08 | En versionerad katalog per ID-typ är facit | Spec och research hade olika ID:n för samma bristmönster |
| 2026-10-08 | Personuppgifter i fas 1 begränsas till definierade kategorier. Inga personuppgifter till AI. | Föreskrifterna kräver namn på funktionsinnehavare och utbildningsdeltagare. |
| 2026-10-08 | Statusflöde utkast → granskat → sakgranskat → fastställt, med grindar | Ett utkast med öppna punkter får inte kunna se fastställt ut |
| 2026-10-08 | Typat villkorsformat i regelbasen, inga fria uttryck | Reglerna ska gå att granska och testa |
| 2026-10-08 | Manifest med kontrollsummor, sparade AI-svar och låsta paket | En äldre bedömning ska kunna återskapas exakt |
| 2026-10-08 | Mänsklig sakgranskning per avsnitt | Giltiga referenser bevisar inte att texten stämmer i sak |
| 2026-10-08 | Byrådata i datamapp utanför repot (`RISKANALYS_DATA`) | `.gitignore` är bara ett extra skydd |
| 2026-10-08 | Första byggetapp blir en tunn kedja genom hela flödet med syntetiska data | Bevisar arkitekturen innan hela regelbasen byggs |
| 2026-10-08 | Kundmodellen delas i fyra spår: förbud och stopp, obligatoriska åtgärder, riskklassning, rapportering | Olika bestämmelser med egna villkor och undantag |
| 2026-10-08 | Modellriskhantering ingår | PTL 6 kap. 1 § andra stycket gäller även en enkel regelmotor |
| 2026-10-08 | Okänd uppgift ger preliminärt resultat som inte kan fastställas | Okänt är inte samma sak som hög risk |
| 2026-10-08 | Paragrafkarta granskad av sakkunnig | Tester hittar inte krav som aldrig lagts in |
| 2026-10-08 | Modell och effort avgörs av utvärdering. Testleverantör i automatiska tester. | Kvalitet och kostnad ska mätas, inte antas |
| 2026-10-08 | Tillåtelselista per AI-anrop. Ingen batch som standard. | Små grupper kan vara personuppgifter. Batch lagrar data i 29 dagar. |
| 2026-10-08 | Bevarande, säkerhetskopia och återställningsprov | Kontrollsummor återskapar inga förlorade filer |
| 2026-10-08 | Resultatet heter "fastställt av byrån" | Får inte uppfattas som certifiering |
| 2026-10-08 | Juridisk granskning, modellvalidering, användningsprov och minsta drift före första riktiga byrå. AMLR som parallellt spår. | AMLR tillämpas från 2027-07-10 |
| 2026-10-08 | Kundmodellens spår har uttryckliga beroenden | Riskklass styr kundkännedomens omfattning och skärpta åtgärder (PTL 3 kap. 14–16 §§) |
| 2026-10-08 | Giltighet per paragraflydelse. Regeringskansliets rättsdatabaser som primärkälla. | PTL 1 kap. 2 § får ny lydelse 2026-11-20. Riksdagens version kan ligga efter. |
| 2026-10-08 | M5 är bara allmän riskbedömning, med genomgång av befintliga rutiner | Rutinerna ska bygga på riskbedömningen |
| 2026-10-08 | Allmänna råd får avvikas med motivering om det bindande kravet ändå uppfylls | Allmänna råd är inte bindande på samma sätt som lag och föreskrift |
| 2026-10-08 | Nästa genomgång räknas bara från utvärderingar, inte från fastställelser | Ett beslut att fastställa är ingen utvärdering (14FS 2024:11 2 kap. 3 §) |
| 2026-10-08 | Paragraftexten sparas i regelbasen med kontrollsumma. Krav har tillämplighet (`galler_om`) och belägg (`belagg`). | Lydelse, tillämplighet och belägg ska gå att kontrollera utan att regelbasens format byggs om |
| 2026-10-08 | Varje AI-försök sparas direkt med begärd och faktisk modell, effort, promptens kontrollsumma, svars-ID och tokenanvändning | Ett betalt svar får inte gå förlorat vid avbrott, och fallback kan byta modell |
| 2026-10-09 | Paragrafkartan har en rad per paragraf och kontrolleras mot källans paragrafindelning. Ohanterade paragrafer stoppar fastställelsen. | Spec 16.1: tester hittar inte ett krav som aldrig lades in |
| 2026-10-09 | Sakkunnigstatus *verifierad* gäller bara med kontrollsumma av det granskade innehållet | En status får inte överleva att kravet eller kartan ändras |
| 2026-10-09 | Ett fastställt paket publiceras med ett enda namnbyte. Fastställelser läses ur paketen. | En fastställelse ska vara helt gjord eller inte gjord alls |
| 2026-10-09 | Bristmönster B-23–B-29 läggs till. Regelbas v1 (M2) ska ha omfattning per tjänst, bolagsbildning och skatterådgivning i tjänstekatalogen och kalibrering mot sektorsrisken. | Två fullständiga sanktionsbeslut visar brister som katalogen saknade |
| 2026-10-09 | Original och OCR bevaras i `../underlag/tillsyn-2026-10-09/` från repots rot. Syntetiska fall med sidhänvisningar versionshanteras i repot. | Källkontroll kan göras lokalt och granskningsförmågan kan prövas utan råa byråhandlingar i tester eller AI-anrop |
| 2026-10-09 | Tillsynsfall inom allmän riskbedömning prövas i M3 efter sakkunniggranskning av facitet. | Före M5 ska det finnas evidens för att granskaren och sakgranskningsflödet hittar kända brister; en grön teknisk kedja räcker inte |
| 2026-10-09 | Sakkunnigs godkännande omfattar refererade lydelser och källans giltighet. Sakgranskning gäller texten med insatta namn. Tidigare paket verifieras innan de används. Ett skadat manifest ger ett fel med instruktion om återställning. | Tre negativa prov visade att godkännanden och historik annars kunde överleva ändringar som de inte omfattade |
| 2026-10-10 | Word-export med python-docx i M1. PDF skjuts till M4. | Word räcker för sakgranskning och fastställelse i M1. PDF-konvertering prövas tillsammans med användningsprovet. |
| 2026-10-10 | `faststall` tar `--organ`, `--datum`, `--namn` och `--roll` i stället för en sammanslagen `--beslut` | Spec 10 kräver namn, roll och datum. Separata argument behöver inte tolkas. |
| 2026-10-10 | Varje riskavsnitt ska ange inneboende risk, risk för terrorfinansiering och kvarstående risk med motorns nivåer, och `sakgranska` visar motorns nivåer bredvid texten | Slutgranskningen visade att AI-text kunde utelämna eller motsäga en nivå utan att valideringen märkte det. Ovanliga formuleringar fångas fortfarande bara av sakgranskningen. |
| 2026-10-10 | En öppen fråga från AI blir ett granskningsfynd som måste hanteras före fastställelse, och sakgranskaren ser frågan. En uppgifts status gäller bara med sina belägg: bekräftad kräver källa, datum och bekräftare, ej tillämplig kräver motivering, datum och bekräftare. | Codex visade att båda annars kunde fastställas som verifierbara paket (spec 10, villkor 1 och 2). |

## M2 – färsk verifiering 2026-10-10

**Färsk fullsvit efter Claudes granskning och sista konfliktgrindsrättelsen: 836 passerade, 1 livetest bortvalt, 261,79 s**, körd med `env -u ANTHROPIC_API_KEY .venv/bin/pytest -q`. Före denna rättelseomgång passerade 800 tester. Nya prov omfattar versionsskydd, andelsbelägg, oberoende facitimport, rättsliga undantag, granskningskonflikter och små komplement. Hela kedjan och byteidentisk återställning passerar för alla tre län. Åtta negativa CLI-prov (sju fastställelsefall samt handredigerad bekräftelse vid bedömning) stoppar utan paket, inklusive äldre bedömning och rättslig datumgräns.

- Regelbasvalidering: giltig `1.0.0`, 107 krav, 11 tjänster, 201/201 hanterade paragrafer i VG, Skåne och Stockholm. Samtliga kartor är `ej_granskad`.
- AMLR-utkast: 90 artiklar och sex bilagor, 92 återstående poster, eget verifierat manifest. Utkastet kan aldrig väljas operativt via ett framtida datum.
- Tillsynsmaterial: två fall, 17 förväntade fynd och fem varianter; 173 arkivkontrollsummor stämmer. **Facitet är ännu inte sakkunniggranskat och de 17 fynden inte produktutvärderade.**
- Fristående teknisk slutgranskning och rättelser dokumenteras i M2-planen. Syntetiska granskare signerar endast testkopior. Inga betalda AI-anrop eller installationer har gjorts.

### Claudes M2-granskning och rättelser

Codex reproducerade och rättade versionsbortfallet (2.0.0/10.0.0), den tysta förlusten av äldre andelsbelägg, facitkopplingen och okänt paket vid import/export. Kandidatraderna i spår A har rättats efter källkontroll men är fortsatt ogranskade. Facitets 22 objekt har en separat version/summa och en kanonisk fil; regelpaketen har 194 rättsliga/metodobjekt var. Lokala attestfiler med granskarens identitet undantas från Git. Motstridiga aktuella beslut stoppar båda berörda paketen oavsett läsordning. Små komplement skyddas också i AI-underlaget. Kärnmodulerna har gjorts mer läsbara. Detaljer och begränsningar finns i [planens rättelselog](superpowers/plans/2026-10-10-m2-regelbas-v1-och-juridisk-granskning.md#rättelser-efter-claudes-granskning-2026-10-10).

Tidigare expertunderlag bevaras som historiska och ska inte användas för den rättade regelbasen. Ingen faktisk sakkunniggranskning har gjorts. Användaren har begärt commit/push av den tekniska M2-baslinjen. Slutlig testkörning efter alla kodändringar: **836 passerade, 1 livetest bortvalt, 261,79 s**, exitkod 0. Regelbasvalidering, AMLR-manifest, tillsynsarkiv, kompileringskontroll och `git diff --check` passerar. Ingen linter har installerats eller körts i rättelseomgången.

### Kontroll inför commit/push

En sista teknisk granskning hittade att konfliktgrinden missade gemensamma krav som var inaktiva för den aktuella byråprofilen. Rättat: paketets alla granskade krav ingår nu i konfliktkontrollen. Fyra regressioner fallerade före rättningen, och motsvarande grind prövas för båda paket och läsordningar. Källuttagens originalbytes bevaras; Git:s whitespacekontroll avgränsas för dessa frysta utdrag. Färsk fullsvit efter denna rättelse: **836 passerade, 1 livetest bortvalt, 261,79 s**, exitkod 0. Elva riktade konfliktprov passerar också. Den fristående tekniska återgranskningen fann inga kvarvarande P1/P2 i granskade kärnflöden. De tre exporterade underlagen motsvarar dagens regelbas, med giltiga innehållssummor och manifest. Verklig sakkunniggranskning och M3/M4 återstår.


### Förtydligat uppdrag: verksamhetsanpassad riskbedömning

Användaren har förtydligat att Codex ska göra källresearch, analys och skrivarbete för ett program som kan anpassa riskbedömningen till olika byråer, med en första lokal pilot. Byrån behöver bekräfta sina faktiska verksamhetsuppgifter. Identitet och pilotunderlag ligger utanför Git. Kravet på oberoende sakkunnigattest i specen är ett internt kvalitetsskydd, inte ett generellt lagkrav på extern certifiering av varje allmän riskbedömning. PTL:s krav på intern kontroll och eventuella särskilda funktioner behöver bedömas separat. [Första källgenomgången och arbetsgången](research/10-kallkontroll-och-gapinventering-m2.md#12-förtydligande-byråns-riskbedömning-och-projektets-granskningskrav) är dokumenterad. AI-källkontroll registreras inte som mänsklig attest. Pilotens uppgifter saknas ännu i det identifierade projektunderlaget. De ska kunna lämnas genom programmets intag; en tidigare verksamhetsbeskrivning eller riskbedömning är ett frivilligt underlag.


### Fullständigt intag som produktkrav

Användaren har förtydligat att programmet ska samla in allt relevant underlag och skriva hela den allmänna riskbedömningen. [Spec revision 12, avsnitt 14.1–14.3](superpowers/specs/2026-10-08-riskanalys-design.md#141-fullständigt-intag-och-skrivning-av-hela-riskbedömningen) beskriver intervjun, följdfrågor, kravtäckning, kompletteringar och användningsprov. En tidigare riskbedömning är inte ett startkrav. Den tekniska implementationsluckan är nu åtgärdad enligt [intagsplanen](superpowers/plans/2026-10-10-intag-och-hel-riskbedomning.md). Regelbas 1.1.0 har 219 fält inklusive nya lokala beskrivnings- och beläggsfält; kanoniska frågor har versionerade krav-/avsnitts-/källkopplingar och beroenden. `riskanalys intag <byrå>` startar eller återupptar den lokala intervjun, kontrollerar kompletteringar och skapar hela Word-utkastet. Kontrakt och syntetiska formulärprov ingår; M3:s sakkunnigbekräftade typfall samt M4:s verkliga pilot, sakgranskningsgränssnitt och driftprov återstår.

## Nästa steg

Codex fortsätter käll- och metodgenomgången samt intaget för pilotbyrån. Följande är kvarstående produktgrindar enligt befintlig spec, inte en förteckning över lagkrav på externa konsulter:

1. Utse en oberoende sakkunnig och låt denne granska de tre paketens exporter samt krav, datum, tillsyn/yrkesroller, FS-tabeller, NRA-skala, metodval och kundgrenar. Tre rättade, ogranskade exporter finns i `../underlag/sakkunnig-intag-2026-10-10-r3/{vg,skane,stockholm}/`, med verifierade manifest och gemensam README. Inga riktiga godkännanden finns.
2. Bekräfta eller revidera de 17 tillsynsfynden/fem varianterna mot lokala original, inklusive beslutens rättsliga status. Importera endast verkligt granskade beslut. Facit har en separat import och attest; en facitrevision kräver ny facitgranskning och upphäver inte paketens juridiska attester.
3. Bygg M3: metod- och granskningsutvärdering med sakkunnigbekräftat facit. Pröva automatiska/manuella B-kontroller, falska fynd, sakfel, granskningstid och AI-kostnad mot manuellt arbete. Kund-C behöver en granskad metod och får ingen normalrisk som standard.
4. Genomför M4:s användningsprov, säker drift, installation och återställning före första riktiga byrå. M2:s gröna teknik är ingen leverans av en färdig användarprodukt.

## Öppna frågor

Se avsnitt 20 i specen samt M2-planens avsnitt om verkliga beslut.


### Genomförande: fullständigt intag 2026-10-10

- Regelstyrd intervju från tom profil, per tjänst och tillsynsområde. Okänt kan sparas, andelar härleds och verksamhetsbeskrivningar/kontrollbelägg sätts in lokalt. Användaren lämnar fakta; programmet skriver utkastet.
- Privata atomiska profilskrivningar, tidigare profilkopior, revisionskonflikter och omprövade beroenden. CLI och webb delar låst atomisk tilläggsoperation för utvärderingshistorik.
- Word byggs med bedömning, godkända AI-utkast, maskinell granskning och manifest. Nedladdningen kontrollerar aktuell profil, regelbas, historik och källfiler. Omexport efter faktisk utvärdering återanvänder den tidigare exportens bedömningskälla och AI-text.
- Lokal HTTP-server på 127.0.0.1 med slumpad åtkomstväg, Host/Origin/CSRF, HTML-escaping, CSP, begränsad kropp, no-store och inga requestloggar. Riktig webbläsare använd för spara→nästa fråga→omladdning→översikt med syntetiska uppgifter; inget verkligt AI-anrop.
- Fristående teknisk granskning har lett till regressioner för kontroll-/geografiberoenden, gamla alias, AI-frågor om härledda andelar, handredigerad datakvalitet, samtidig historik, historikändring efter Word-export, inaktuell sektorsmotivering och förlust av riskavsnitt vid omexport. Då identifierade fynd rättade. Senare Claude-granskning hittade ytterligare brister i intag/CLI/skrivning; se rättningsloggen nedan.
- Alla tidigare fastställelsegrindar finns kvar. Inga sakkunnigattester har skapats. Tekniskt intag är ingen juridisk certifiering eller avslutad M3/M4.
- Start: `.venv/bin/riskanalys intag pilotbyra`. Nyckel behövs först vid uttrycklig Claude-skrivning. Faktaunderlag för pilotbyrån är ännu inte inmatat i detta byggarbete.


**Färsk slutverifiering av intaget (2026-10-10):** `env -u ANTHROPIC_API_KEY .venv/bin/pytest -q` gav **881 passerar, ett livetest bortvalt**, 468,32 s. Detta inkluderar 45 nya intagsprov och hela befintliga sviten. Tre syntetiska tom-profil→formulär→Word-prov passerar för VG, Skåne och utländsk filial/Stockholm. Det verkliga webbläsarprovet omfattar sparande, nästa fråga, omladdning och översikt, inte ett riktigt Claude-anrop. Regelbas 1.1.0 validerar med 107 krav, 11 tjänster och 201/201 hanterade paragrafer per länspaket; sakkunnigstatus är fortfarande `ej_granskad`. `compileall` och `git diff --check` passerar. De tre r3-granskningsunderlagens manifest är verifierade. Koden och dokumentändringarna är inte committade eller pushade i detta uppdrag.

**Registerförifyllning i intaget:** organisationsnummer och myndighetsdata enligt [källkontroll och valt flöde](research/10-kallkontroll-och-gapinventering-m2.md#14-förifyllning-från-företagskällor-2026-10-10). SCB AFR-hämtning och lokal SCB-JSON-import är implementerade enligt [registerplanen](superpowers/plans/2026-10-10-registerhamtning.md). Personlig SCB-nyckel saknas ännu; autentiserat uppslag är inte verifierat. Externa värden ska vara källbundna förslag, och byråns egna tjänster/kundstatistik/kontrollbelägg behöver fortfarande bekräftas.

### Registerhämtning i intaget 2026-10-10

SCB AFR v1 är första avgiftsfria connectorn. Användaren har ingen API-åtkomst ännu. Lokal `RISKANALYS_SCB_API_KEY` används efter användarens egen registrering; JSON-fil kan importeras som alternativ, märkt ej verifierat ursprung. Bara juridiska organisationsnummer används i denna connector. Enskilda firmor kan fortsätta manuellt.

Grund-/registersidan visar namn, säteslän, arbetsställeantal, SNI, juridisk form/status och anställdas/omsättningens klasser med år. Bara namn/län/ställen kan överföras med uttrycklig rätt-byrå-bekräftelse. Hämtning ändrar inga profilsvar, avvikelser visas och ändringar använder ordinarie profilvalidering och beroenden. Privat lagring bevarar minimala snapshots med källhänvisning och summa utanför Git. AI:s tillåtelselista och sakkunnigstatus är oförändrade.

Källor, valt flöde och hämtas/frågas-matris finns i [research 10 §14](research/10-kallkontroll-och-gapinventering-m2.md#14-förifyllning-från-företagskällor-2026-10-10). Bolagsverket HVD prioriteras som senare adapter; inget gissat API eller Allabolag-skrapning är byggt. SCB:s autentiserade liveflöde återstår att prova när en personlig nyckel finns. Ingen nyckel, inget konto och ingen betald AI-användning ingår i verifieringen. Kodändringarna är inte committade eller pushade i detta uppdrag.

**Färsk slutverifiering för registerhämtningen:** hela sviten gav **938 passerade, 1 livetest bortvalt, 454,56 s**, exitkod 0, utan AI-/SCB-nycklar. 57 nya registerprov ingår. Fristående återgranskning verifierade då provade rättelser; senare Claude-granskning fann ytterligare brister som redovisas i rättningsloggen nedan. Verkligt webbläsarprov använde syntetisk transport: hämtning, grundstart, bekräftelse av namn/arbetsställen, sparande efter omladdning och fortsatt fråga om verkligt personantal. Regelbasvalidering, compileall och whitespacekontroll passerar. Autentiserat SCB-uppslag och M3/M4:s verksamhetsprov är separata återstående kontroller.

### Claude-granskning och minskad manuell inmatning 2026-10-10

[Fynd 1–10 och kompletterande beslut](superpowers/plans/2026-10-10-intag-och-hel-riskbedomning.md#claude-granskning-och-rättelser-2026-10-10) är prövade/rättade med regressioner. Spec revision14 beskriver gemensam CLI/webb, bevarade okända belägg, länpolicy, skrivtoken och registerdatumgrind. De tidigare slutomdömena ska läsas som daterade avgränsade tekniska kontroller. Denna rättningsomgång har nu färsk helsvit och fristående återgranskning enligt resultatet nedan.

[Utvidgad research](research/10-kallkontroll-och-gapinventering-m2.md#142-utvidgad-research-mindre-manuell-inmatning-2026-10-10) skiljer byggd SCB-förifyllning (tre kanoniska intagsfält) från fler offentliga grund-/bokslutsuppgifter och byråns egna exporter. Lokal aggregerad import prioriteras för att reducera manuella verksamhetssvar; Bolagsverket HVD är nästa externa datakälla. Inga nya konton, API-åtkomster, betalda anrop, sakkunnigattester, commit eller push har gjorts.

Första fullsviten i rättningsomgången gav 956 passerade/1 fel/1 livetest bortvalt (449,97 s). M2:s negativa paketprov fångade en oavsiktlig län/paket-samordning efter orelaterat CLI-svar. Den rättades med ytterligare RED-regression och föranledde en ny fullsvit enligt slutresultatet nedan. Provets säkerhetsförväntan behålls.

Återgranskningen hittade även explicit återbekräftelse med oförändrat grundvärde men ändrat effektivt län/paket. Det är rättat efter RED-prov; sådan metadataändring omprövar nu beläggen. De 21 nya regressionerna och M2:s negativa paketprov gav 22 passerade (30,74 s). Fristående återgranskning fann inga konkreta P1/P2 i den sista avgränsade länrättningen. **Slutlig fullsvit: 959 passerade, 1 livetest bortvalt, 465,53 s**, exitkod 0, utan AI-/SCB-nycklar. Regelbasvalidering, compileall och diff --check passerar. Syntetiskt webbläsarprov visar egen filialkälla och sparande av okänt svar utan roll. Verklig API-åtkomst, sakkunnigstatus `ej_granskad` och M3/M4:s produktgrindar kvarstår; nya CSV/XLSX-/BV-importer är föreslagna, inte byggda. Ingen commit/push.

### Datumoberoende registerprov och CLI-längdfel 2026-10-11

De tio datumberoende registerfelen reproducerades och rättades i testuppsättningen. Intagets testklocka använder nu samma syntetiska dag som bedömningsfixturen; successiva hämtningar behåller olika tidsstämplar. De två proven som blandade `DAG` med verkligt dagens datum är samordnade. Produktionsgrindarna för framtida/historiskt underlag och svensk hämtningsdag är oförändrade.

CLI:s `IntagSvar`-validering blir nu ett `ProfilFel` med svensk längdanvisning, i stället för en Pydantic-stackspårning. Fyra nya negativa regressioner blev först röda för svar, roll, källa och motivering; två gränsprov visar fortsatt sparande vid 12 000/200 tecken. Avvisning ändrar inte profil eller profilhistorik. Båda ursprungliga kommandona återprovades också som riktiga CLI-processer. [Detaljer och RED/GREEN-loggar](superpowers/plans/2026-10-10-intag-och-hel-riskbedomning.md#datumoberoende-prov-och-cli-längdfel-2026-10-11).

**Färsk helsvit:** `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest` gav **965 passerade, 1 livetest bortvalt, 458,81 s (7:38)**, exitkod 0. Logg: `/tmp/riskanalys-2026-10-11-full-pytest.log`. Alla 89 intagsprov passerade separat; 62 berörda register-/fråge-/fyndprov passerade även med simulerad omgivningsdag 2025-01-01 respektive 2030-01-01. Regelbasvalidering, compileall och diff --check passerar. Ingen kodändring efter helsvitens start, bara dokumentationsnoter. Ingen commit/push.

**Beslut inför nästa bygge:** gör först ett manuellt pilotintag för pilotbyrån och inventera vilka exporter som faktiskt finns. Bygg därefter CSV/XLSX-import för det verifierade formatet, inte en generell import först. Pilotunderlag ligger utanför Git. Pilotintaget och den nya importen är ännu inte genomförda.

### Förenklat och mätt intagsflöde 2026-10-11

Namn, säteslän och registrerade arbetsställen kan nu godkännas tillsammans och följa med redan vid registerstart. Motsvarande ordinarie fråga visar sparat SCB-förslag med godkännandeknapp. Hämtning ändrar inga profilsvar; avvikande tidigare värden kräver uttryckligt ersättningsval. Valideringen sker först i minnet och hela urvalet sparas med en CAS-sparning. Ett tomt registerurval får inte bekräfta säteslänet.

Elva tjänsteutbudsfrågor kan besvaras i en samlad lista med gemensamt eget underlag/roll/datum och uttrycklig bekräftelse att omarkerade tjänster inte erbjuds. Enskilda osäkra svar med ”Vet inte” finns kvar. Intervjusidan visar frågor som kan besvaras nu, i stället för alla ännu osäkra följdfrågor. Roll föreslås redigerbart och senast framgångsrikt sparad roll återanvänds i sessionen. Metadata och registerbakgrund kan expanderas vid behov.

F-skatt, moms och arbetsgivarregistrering läses ur samma SCB-svar som registerbakgrund i snapshot v2. Tidigare v1-bilder behåller format/summa och kan fortfarande användas. Nyckel kan anges i ett lokalt lösenordsfält och användas i sessionen utan disk-/HTML-lagring; miljövariabel stöds också. Användaren har visat ett eget lyckat SCB-uppslag. Agentens implementation/verifiering använder syntetisk transport och data, inga personliga nycklar eller verkliga svar från pilotbyrån. [Ny research och källmatris](research/10-kallkontroll-och-gapinventering-m2.md#143-ny-källkontroll-och-förenklat-godkännande-2026-10-11) skiljer dagens överförbara fält från Bolagsverkets möjliga filial/verksamhet/bokslut, separat åtkomst och byråns egna statistik-/kontrolluppgifter. Manuellt pilotintag och exportinventering återstår före formatanpassad CSV/XLSX-import; ingen generell import eller ny Bolagsverket-adapter har byggts.

**Verifiering:** 25 nya regressioner totalt, inklusive samlade svar, fel utan delvis sparning, gamla flikar/bilder, datum, skattestatus utan faktainferens, v1-summor, sessionsnyckel utan återgivning och unika formuläretiketter. Fristående granskningens markörfria start och rollförslag reproducerades RED→GREEN. Verkligt webbläsarprov använde syntetisk transport: registerstart → nästa riktiga lucka → samlad tjänstelista → sparande/omladdning → bevarad registerjämförelse och expanderbar skattestatus. Lokal HTTP-benchmark med sex fall ×100 mätningar gav median **8–47 % kortare svarstid**, med fulla mätdata och begränsningar i [prestandaunderlaget](research/intag-prestanda-2026-10-11.json). Detta mäter lokal rendering, inte extern SCB-hastighet eller verklig användartid.

**Slutlig helsvit:** `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest` gav **990 passerade, 1 livetest bortvalt, 441,32 s (7:21)**, exitkod 0, utan varningar. Logg: `/tmp/riskanalys-smidigt-final-full-pytest.log`. Regelbasvalidering, compileall och diff --check passerar; sakkunnigstatus är fortsatt `ej_granskad`. Kod och testuppsättning ändrades inte efter slutkörningens start; endast dokumentationsnoter. Ingen commit/push. Den befintliga verkliga pilotservern har inte startats om eller ändrats; samma intagskommando behöver köras igen för att visa ny kod och bevarade svar.

### Underlagsval och tydlig leverans 2026-10-11

Enkla verksamhetsfakta/beskrivningar har nu ett synligt val ”Egen kännedom om verksamheten”. Det sparas med användarens bekräftelse, funktion och datum, utan krav på en ny fritextkälla för varje sådant svar. Statistik, numeriska frågor, sektorsmotiveringar och kontroller har inget sådant snabbval. Tidigare aktuella bekräftade manuella underlag kan väljas igen inom samma kategori och exakt period; kund-/ekonomi-/erfarenhetsstatistik och varje kontroll/fas hålls åtskilda. Okänt/inaktuellt underlag och registerbildens generella källa erbjuds inte som manuellt underlag. Period föreslås från bekräftad kundbas respektive omsättning. Gammal revision eller ändrat underlagsval lämnar profilen oförändrad vid avvisning.

SCB-schema 3 bevarar ägarkategori. Kod 41 (privat svenskkontrollerat utan koncerntillhörighet) ger ett villkorat ”nej”-förslag för yttersta moderföretag, med synlig begränsning och uttryckligt godkännande. Övriga/saknade koder ger inget koncernförslag; filial härleds inte. V1/v2 behåller exakt tidigare format/kontrollsumma. Grund-/översiktssidan och skrivrubriken visar nu faktisk leverans: allmän riskbedömning som Word-utkast med verksamhet, risker per tjänst, kontroller och åtgärder, samt granskningsbilaga vid öppna fynd. Separata rutindokument och individuella kundriskbedömningar ingår inte i detta intags skrivflöde.

[Fler källor inventerade](research/10-kallkontroll-och-gapinventering-m2.md#144-fler-källor-underlagsval-och-tydlig-leverans-2026-10-11): Bolagsverket HVD prioriteras för registrerad verksamhet/organisationsform/digitala årsredovisningar, men separat API-åtkomst och maskinellt kontrakt återstår. Skatteverkets befintliga statusbakgrund via SCB räcker för de nu byggda fälten. Polisen/Länsstyrelserna och EU/FATF kan tillföra riskunderlag; ny NRA 2026 om juridiska personer är identifierad men inte integrerad eller använd för att ändra frysta riskregler. Manuellt pilotintag och inventering av verkliga exporter återstår före ny formatanpassad CSV/XLSX-import.

**Verifiering:** 18 nya regressioner, med RED före produktionsändring; 83 fokuserade prov passerade (35,50 s) och alla berörda intags-/företagsdataprov gav 172 passerade (186,90 s). Fristående granskning fann inga konkreta fynd i den avgränsade ändringen. Syntetiskt webbläsarprov visar godkänt koncernförslag, sparad egen kännedom, sparat kundunderlag/period återanvänt i nästa kundfråga och att omsättning inte får samma underlag föreslaget. Bildbevis finns utanför Git i `/Users/gt/.codex/visualizations/2026/10/11/01a12a55-3718-74f2-bc3b-588e958dab72/intag-underlagsval.png`. Provfliken och provservern är avslutade; den verkliga pilotservern har inte startats om. Inga personliga nycklar, autentiserade API-/AI-anrop eller verkliga uppgifter från pilotbyrån användes.

**Slutlig helsvit:** `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest` gav **1008 passerade, 1 livetest bortvalt, 466,39 s (7:46)**, exitkod 0, utan varningar. Logg: `/tmp/riskanalys-underlagsval-final-full-pytest.log`. Regelbasvalidering, compileall och diff --check passerar; sakkunnigstatus fortsatt `ej_granskad`. Kod/testuppsättning ändrades inte efter fullsvitens start, bara dokumentationsnoter. Ingen commit/push. Användaren behöver stoppa sin befintliga intagsserver med Ctrl+C och köra samma kommando/ID igen för att läsa ny kod och bevara svar. Pilotens befintliga data-ID byts inte automatiskt.


### Källkontroll och verksamhetsanpassad D-ARB 2026-10-11

Användarens beställning i [research 11](research/11-kallkontroll-allman-riskbedomning.md) kontrollerad självständigt mot kod, regelbas, PTL/föreskrifter, rapport 2026:14, vägledningen mars 2025, sparade Länsstyrelsewebbsidor/nyhetsbrev och tillsynsbesluten. H5-planen [tjänststruktur](superpowers/plans/2026-10-11-d-arb-tjanststruktur.md) godkändes av användaren före bygge. Tidigare ändringar i checkout bevaras; inget har committats eller pushats i detta uppdrag.

- H1/H2: egna rapporter och misstankebaserade avböjanden ingår som belagd erfarenhet, utan riskpoäng från antal. B-15 maskinkontrollerar erfarenhet i varje tjänsts hotanalys. Varje sårbarhet motiveras med villkor, faktiskt underlag, period och källa. Ofullständigt geografiskt underlag eller borttagen motivering ger blockerande B-09/B-10.
- H3/H4: 18 nya sårbarhetsindikatorer med intagsfält, 7 konkreta hot/tillvägagångssätt inklusive tre terrorfinansieringsmodus. H-01/H-02 kopplas till tjänster; research 11:s påstående om total avsaknad av TF korrigeras: H-03 var redan markerad TF, men konkreta modus saknades. Kundantal/andelar för forskningsluckorna byggda; positiva belagda andelar för fysiskt möte, utländska ägare, högrisktredjeland och utsatt område kan inte döljas av en nej-indikator.
- H5/M1–M3: kontrollernas dokumenterade effekt före riskavsnitten. Sex analysdelar per tjänst; råa intagsfrågor/svar och källversioner i sakgranskad bilaga. Lokala fritexter stannar utanför AI. Omfattning följer storlek/art i BT-OMF-01; trösklar är ogranskade metodval. Slutsatser omfattar rutiner, kundkännedom, övervakning och utbildning. Ingen sammanvägd byrånivå; spec §7.4 och §7.5 uppdaterade.
- M4/L: dokumenterad omvärldsbevakning med lästa registrerade källversioner, ansvar och relevans; hämtning är inte genomförd byråbevakning. Uppdateringsgrunder, spridning, goAML och tidigare tillsyn ingår. Tolv nya original hämtade och SHA-256-kontrollerade, se [manifest](research/kallmanifest-2026-10-11.json). SMOB är en forskningsrapport från ett forskningscentrum, inte en föreskrift/myndighetsnorm.
- Fastställelse: ändrad text, underrubriker, namn, dokumenttitel, avsnittsordning eller bilaga kräver nytt sakgodkännande. Formatet `D-ARB-tjanst-v2` registreras i nya gransknings-, export- och fastställelsemanifest; historiska paket ändras inte. Maskingranskning regenererar deterministisk tjänstanalys och stoppar ändrat innehåll/sexdelad struktur. `ej_bedömd` effekt är okänd. Kontrollernas period och de nya faktorernas period ska stämma med kundunderlagets analysperiod; historiska belägg med annan period ger ingen aktuell reduktion.

**Verifiering:** H1/H2 skrevs RED före kod; den då fokuserade regressionskörningen gav 103 passerande prov. Senare H3/H4/H5/M1–M4 och slutgranskningsrättelser skrivna RED→GREEN. Fristående slutgranskare fann inga Critical och reproducerade luckor i ej bedömd effekt, ändrad deterministisk text och historiska kontroll-/faktorperioder; samtliga rättade med regressioner. Precis TF-källhänvisning och synliga CLI-underrubriker rättade. Slutlig helsvit: **1090 passerar, 1 livetest bortvalt, 642.79 s**, utan ANTHROPIC_API_KEY och RISKANALYS_SCB_API_KEY. Regelbasvalidering, compileall och git diff --check passerar. Första sviten under pågående bygge gav 1059 passerar/5 fel; en senare körning avbröts när en äldre integrationsförväntan behövde anpassas till kravet på effektunderlag. Felen omfattade tidigare laddad fixture/version samt saknad effekt i äldre sanktionsprov. Integrationsförväntan rättad och proven passerar; inga kontrollkrav eller spärrar försvagade. Den separata nya M2-CLI-kedjan gav 11 passerar, med syntetisk signering endast i testkopia, fastställelse och återställningsprov för tre länspaket.

**Kvarstår:** FATF:s TF-original gav HTTP 403 och är därför varken checksumregistrerat eller använt som ny katalogkälla. Original till domarna 12554-25, 842-26 och 1129-26 saknas; ingen ny rättspraxis byggs ur referat. Verklig sakkunniggranskning, tjänstevis kalibrering av de byråövergripande indikatorerna, kontrollernas tillräckliga täckning och M3/M4-prov återstår. Alla nya poster är `ej_granskad`; tekniskt gröna tester är inte juridiskt godkännande.

**För granskning:** ett enbart syntetiskt Word-utkast och provresultat ligger utanför repot i `../underlag/kallkontroll-2026-10-11/`. Nya ogranskade granskningsunderlag för regelbas 1.2.0 är framställda för alla tre länspaket i `../underlag/granskningsunderlag-1.2.0-2026-10-11/`; deras manifest verifierar. Ingen mall är signerad. Inga riktiga byrådata eller riktiga API-anrop användes i testerna.
