# Rättning efter granskning av kravstödet

Rättningen avser granskningen från 22 oktober 2026 av `a7f9377`. Granskningen och originaltestet hämtades direkt från den lokala grenen `feat/steg-1-3`, commit `799fbec`; någon push behövdes inte för åtkomst. Inga filer ändrades i granskarens checkout. Rättningen ligger på `codex/kravstod-tjansteexponering`.

## Planen får ett uttryckligt avslut

En genomförd plan bevaras som historik och kräver inte ny planutvärdering vid nytt bedömningsår, ändrade byråfakta eller ny regelbas. Före genomförandet gäller samma krav på aktuell, bunden utvärdering som tidigare.

Vid giltig övergång till erbjuden tjänst avslutas planer av typen `ny_tjanst` i samma atomiska profilsparning. Andra genomförda ändringar registreras uttryckligen i webb eller med `genomfor-plan`. Programmet drar ingen slutsats om genomförande enbart av dagens erbjudandeflagga eller avsett datum.

Avslutet innehåller faktiskt datum, ansvarig, datum och text för den då gällande utvärderingen, dess plansumma, planens egen innehållssumma och profilrevisionen före sparningen. Avslutade planer får inte ändras, öppnas igen eller importeras som nya avslut via den vanliga underlagssparningen. Vid återinförande krävs en ny aktiv plan. Misslyckad profilsparning lämnar inget falskt avslut. Årsutvärderingen flyttas inte och krävs fortsatt.

Kontrollen av historiska planer gäller deras eget bevarade innehåll. De prövas inte på nytt mot dagens fältregister eller regelbas. Aktuella byråfakta och den aktuella analysen prövas i ordinarie flöde.

## Rapport och uppgradering

Standardtexten om motoraktivering står en gång i det gemensamma faktaunderlaget. Mekanismen använder katalogens `metodmotivering` när den finns, och anger möjliggjorda hot med namn. Tjänstens tidigare kodlista ersätts med hänvisning till den redan redovisade lokala sårbarhetsprövningen och dess belägg. Saknas lokal motivering markeras behovet av verifiering. Fullständiga beräkningsspår finns fortsatt i B1. Stavningen är rättad till ”byråns prövningar”.

Uppgraderingsanteckningen finns i [STATUS](../../STATUS.md) och [användningsbeskrivningen](../../kravstod.md). Profilmodellernas ändring ger ny modellidentitet: befintliga analysgodkännanden och modellriskunderlag behöver förnyas för nya beslut. Historiska fastställda paket bevaras. Äldre planer utan avslutsregistrering markeras inte automatiskt som genomförda; de behöver uttrycklig registrering med kontrollerat underlag och giltig utvärderingsbindning.

De två iakttagelser som inte krävde ändring, historikskanningens prestanda och rättelsens ansvarigfält, ingår inte i denna rättning. Riskmotor, vikter, regelbas och sakkunnigstatus är oförändrade. Planer, grupper och privata avslutsuppgifter hålls utanför AI-underlaget.

## Regressioner och granskning

Originaltestet gav först exakt **4 fel och 3 godkända** på `a7f9377`, av de angivna skälen. Originalfilen är bevarad oförändrad under [granskningen](2026-10-22-granskning-kravstod-implementation.md). Den körbara kopian finns i `tester/enhet/test_planens_livslopp.py`.

Den körbara kopians hjälpfunktion registrerar nu ett faktiskt införande genom `spara_andring`, i stället för att bara anropa den rena spärrkontrollen och returnera en osparad profil. De sju fallens påståenden är behållna. Anpassningen behövs för att prova ett uttryckligen registrerat livslopp utan att härleda avslut från ett ja-värde.

Åtta ytterligare enhetsprov täcker oföränderlig historik, nytt återinförande, uttryckligt avslut av ändringsplan, saknad utvärdering och fel datum, skrivavbrott, äldre serialisering, otillåten import/återöppning samt historiska fält och bevarad årsfrist. Webb/CLI-provet täcker båda vägarna, CSRF och revisionskonflikt. AI-provet jämför hela begäran inklusive omförsök även när privata genomförandeuppgifter finns.

Riktade körningar med Python 3.12.15 gav **108 godkända** för livslopp, planering, historik och V8 samt **80 godkända** för analysbindning, AI-begäran och rapportflöde. Urvalen överlappar och ska inte summeras till unika tester. En oberoende kodgranskning av den faktiska rättningen gav inga Critical, Important eller Minor; granskaren körde också de 15 livsloppsproven. Den granskningen omfattade inte native webbläsarinteraktion, Word-layout, verkliga API-anrop eller saklig/juridisk tillräcklighet hos mänskliga utvärderingar.

**Fullsvit:** `.venv312/bin/python -m pytest -q` gav **3 027 godkända, 1 bortvalt livetest**, exit 0, på 1 727,86 s. Insamlingen omfattade exakt samma 3 027 valda prov. Ingen registrerad käll- eller testfil ändrades under slutkörningen. Regelbasvalidering och `git diff --check` gav också exit 0. Det tidsberoende webbprovet passerade i denna fullständiga körning och ändrades inte.

## Rapportmätning och visuell kontroll

Samma två frysta provfall och svar användes före och efter rättningen med `rapportmatning.py`. Detta är jämförelse mot `a7f9377`, inte mot versionen före hela kravstödsändringen.

| Provfall | Läsrapport före | Läsrapport efter | B1 före/efter | Totalt före | Totalt efter |
|---|---:|---:|---:|---:|---:|
| Fyra tjänster | 13 352 | 13 342 | 34 440 | 47 792 | 47 782 |
| Med betalningsmandat | 13 029 | 13 019 | 34 609 | 47 638 | 47 628 |

Måtten avser ord. Båda läsrapporterna minskar tio ord. Ordagrant gemensam tjänstetext ökar 33 ord i båda fallen när en läsbar hänvisning ersätter kodlistan; liknande struktur minskar 84 ord. Ändringen ger tydligare mekanismer och hotnamn, men är ingen större förkortning. Den tidigare redovisade ökningen för hela kravstödet kvarstår i huvudsak.

En separat syntetisk export med genomförd plan och kombinationsgrupp renderades med den paketerade dokumentrenderaren till 38 lässidor och 99 bilagesidor. Visuellt öppnades läsrapportens sidor 5–7, 10, 18, 25 och 32 samt B1:s sida 64. De berörda mekanismerna, lokala hänvisningarna och genomförandeuppgifterna är läsbara utan konstaterad klippning eller överlappning. Detta är riktad rasterkontroll, inte fullsidig QA eller native Word-kontroll. Exporten är ett layoutprov med syntetiskt underlag, inte en sakgodkänd riskbedömning.

Körloggar, mätningar och renderade QA-filer ligger lokalt i den ignorerade mappen `.superpowers/review-2026-10-22/`. Tidigare slutprov behålls som historik. Frivillig motororientering 3b och verkliga metodbeslut i uppgift 6 är fortsatt avgränsade enligt den godkända planen.
