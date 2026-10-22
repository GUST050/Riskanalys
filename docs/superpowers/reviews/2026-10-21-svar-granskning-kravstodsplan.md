# Revision efter granskning av kravstödsplanen

Datum: 21 oktober 2026. Avser revision 2 av [planen](../plans/2026-10-21-kravstod-och-tjansteexponering-plan.md) och [designen](../specs/2026-10-21-kravstod-och-tjansteexponering-design.md).

Granskning läst i `GUST050/Riskanalys`, dokumentationscommit `8915f0d154416bcbd482b2b926a6523e7f9405d8`, fil `docs/superpowers/reviews/2026-10-21-granskning-kravstodsplan.md`. Kodbasen som granskningen avser är `288fa6650ea400fda04cdcef965f8ac17adc3575`.

## Avstämning och ändringar

| Granskningspunkt | Kontrollerat underlag | Ändring i revision 2 |
|---|---|---|
| 1 Kodbas och återanvändning | GitHub-grenen slutar i 8915f0d. Jämförelsen 688629f–288fa66 innehåller tio senare commits. Jämförelsen från fc82b67 innehåller totalt 13 kod-/underlagscommits och den separata granskningen. Beslutsformulärets åtta par är lästa. | Lås kodbasen till 288fa66 och granskningen till 8915f0d. Uppgift 0 verifierar samtliga 13. Uppgift 2 kompletterar samma formulär med par 9–10; inget nytt beslutsprotokoll. |
| 2 Planerade tjänster | `Analystjanst._underlag` bildar sökväg med BEDOMNINGAR. Historiken har redan separata utvärderings- och uppdateringshändelser. | Dela i 3a, planpost och saklig bunden förändringsutvärdering utan motor, och 3b, valfri senare motororientering i ett kort separat dokument. Ingen ny V8-mappväg krävs för 3a. Tillåtna planfält och begränsningen före D3 preciseras. |
| 3 Rapportens upprepning | `gemensamt_v8.py` innehåller D-ARB.5, gemensam erfarenhet och geografi med tjänstehänvisningar. `nivamotivering_v8.berakningstabeller` anger B1. `rapportmatning.py` använder H7.1-fall och skiljer ordagrann text från likartad struktur. | Mekanism/källa skrivs gemensamt; tjänsten behåller lokal tillämpning. Fulla beräkningar stannar i B1. Kräv före/eftermätning för samma två fall och motiverade ökningar utan hårt ordtak. |
| 4 Miljö, gruppmodell och omfattning | Gruppfältens dubbla population var en designföreskrift, inte två olika sakuppgifter. V8 har en befintlig renderingskedja och profilrevision/bindning ska återanvändas. | Ett populationsfält, uttryckligt krav på ny bedömning/analysbindning efter gruppändring, Python 3.12 för godkända körningar och portabel renderingskontroll. Uppgift 1 får begränsa eller skjuta upp 3a–5 och 3b. |

## Ytterligare konsekvenser som preciserats

- En avgränsad planutvärdering får inte räknas som en full årsutvärdering enbart för att båda är historikhändelser av typen utvärdering. Detta följer av att befintlig `senaste_utvardering` väljer senaste händelsen av denna typ. Ett riktat prov läggs i 3a.
- Planbindningen ska exkludera själva historikhändelsen och den förväntade övergången till erbjuden. Annars skulle en korrekt införandeövergång genast göra underlaget inaktuellt.
- En planpost eller ett grönt test bevisar inte att en saklig förändringsutvärdering genomförts. Analys av berörda risker, rutiner, underlag och behov av uppdatering måste dokumenteras av verksamheten.
- I frivillig 3b används befintliga byråfaktorer tills beslutad anslutning finns. Planvärden är synliga antaganden, inte motorindata före D3. Befintlig kontrollverkan tillskrivs inte den nya tjänsten.

## Verifieringsgräns

Denna revision bygger på fjärrhistorik och källäsning. Produktkoden och andra chattars arbetskopior har inte ändrats. Inga produkttester, nya rapportmätningar eller renderingar har körts. Lokala dokument har kontrollerats för länkar, uppgiftsreferenser, överensstämmande omfattning och filreferenser mot trädobjektet för 288fa66. Sakkunnigstatus och metodbeslut är oförändrade.

## Uppföljande förtydliganden i revision 3

- Python-miljön väljs uttryckligen via `RISKANALYS_VENV`. En giltig `.venv312` återanvänds i rätt checkout eller skapas med `python3.12`. Alla test- och mätkommandon är uppdaterade. Granskarens lokala uppgifter om Python 3.14/3.12 är inte en miljökontroll utförd i denna dokumentarbetsyta.
- Erbjudandets före-/efterregel är explicit: bekräftat nej→ja kräver plan och utvärdering; okänt→ja är kartläggning om registrerad plan eller uttryckligt införande inte anger annat. Ett mellanliggande okänt i samma transaktion kringgår inte kontrollen. Felaktigt nej har en särskild, belagd och historikförd rättelseväg.
- Källäsning av `analys/lagring.py:bygg_bindning` och `analysaktualitetshinder` bekräftar att hela historikens kontrollsumma påverkar analysbindningen. Denna regel behålls och dess följd för alla aktuella analysbeslut dokumenteras i 3a och provas i 7. Planbindning och hela analysens bindning är olika kontrakt.
- D-ARB.5 innehåller gemensamma definitioner bara för faktorer som används i minst en erbjuden tjänsts motorscenarier, med historisk reservväg för resultat utan scenarier. Ej tillämpliga faktorer stannar i sårbarhetsprövningen/B1. Preliminär aktivering får inte beskrivas som bekräftad fakta.

Revision 3 ändrar endast lokala dokument. Inga produktändringar eller produkttestkörningar ingår.
