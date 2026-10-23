# D – genomförande av provisoriska metodbeslut

Delplan till `2026-10-23-regelbas-c-rapport-d-e.md`, Task 4. Utgångspunkt: produktintegration `8abd6d9`, regelbas 2.2.0. Användaren har godkänt V10-förslaget och fortsatt arbete. Alla val nedan är AI-framtagna förslag med `ej_granskad`, inte sakkunnigbeslut. Tester skrivs nu och körs vid slutet enligt användarens instruktion.

## Gemensamt kontrakt

Typat `Metodbeslut` innehåller ID, titel, valt alternativ, minst två alternativ, skäl, osäkerhet, källor med läst locator/kort citat, exakta objektinnehållssummor, genomförandefilernas summor och konkret återföring. Tomt beslutsregister utelämnas vid serialisering för historiska summor. Referenser till andra beslut tillåts inte (ingen cirkel). Registret laddas från egen YAML. Varje beslut ingår i granskningsmall/import/attest och fastställelsespärr. Aktuella objekt/filer kontrolleras; gammal attest kan inte överleva ändrat genomförande. Befintlig separat modellvalidering kvarstår.

För varje steg sparas regelbas före/efter, samma sex frysta profilbytes, fullständiga tjänste-/scenarioberäkningar och diff både mot föregående och 2.0.0. Borttagna scenarier redovisas särskilt jämte numeriska sänkningar. Riktade syntetiska kontraster kompletterar sexfallen. Inga källor sägs kalibrera numeriska värden som de inte anger.

## Steg och avsett val

| ID | Egen version | Genomförande och alternativ | Skäl/kontrast |
|---|---|---|---|
| D1 | 2.3.0 | Avgränsa bort H-MOD-02 från ren T-RED-04; alternativ behåll indirekt momsanknytning i varje löneuppdrag. | Moms-/fakturagranskning hör till annan erbjuden tjänst. Indirekt kundexponering kvar genom H-02; risk vid falska löneuppgifter genom H-TJ-04. Ren lön jämförs med erbjuden bokföring/betalning. Bortfall redovisas som potentiell sänkning även utan ändrat max. |
| D2 | 2.4.0 | Avgränsa H-01 från ren T-RED-04, behåll H-02. Alternativ behåll båda generellt. | Källan beskriver faktura–svart lön och brottsvinst–lön, men ingen generell insyn i leverantörsfakturan. Lönens eget falska underlag finns i H-TJ-04. H-02:s löneuttag är relevant även utan bankmandat; kontrolltäckning utvidgas inte. |
| D3 | 2.5.0 | Behåll konservativ portföljmodell, med uttrycklig begränsning att kundernas faktiska fördelning inte beräknas. Alternativ bygg numerisk tjänsteavgränsning. | Befintliga fyra frivilliga antal täcker inte alla kund-/geografifaktorer och deras lämpliga trösklar är inte kalibrerade. Lokal känd nolla är beskrivet sakunderlag men innebär ännu inte automatisk motoravgränsning. Organisationsfaktorer är byrågemensamma. Ingen ny antagen kundfördelning. |
| D4 | 2.6.0 | Endast uttryckliga kombinationsgrupper är kundöverlapp; alternativ härled överlapp ur tjänstemarginaler. | Samma marginaler kan ge olika kundöverlapp. Befintlig global kombinationsfaktor märks modellkombination. Ingen automatisk identifiering av riskkunder. |
| D5 | 2.7.0 | Behåll max per dimension med synlig scenariobredd och otäckta maxled; alternativ medel-/exponeringsviktning. | En väsentlig exponeringskedja ska inte döljas av många låga scenarier. Källan anger inget max eller viktning; eget metodval. |
| D6 | 2.8.0 | Behåll allvarlig TF-konsekvens och separat sannolikhet, ingen TF-kontrollreduktion; alternativ tjänste-/beloppsberoende konsekvens och avdrag. | Skyddsintresset är möjlig skada på människor/samhälle vid terrorändamål, enheten ett relevant missbruksscenario. Belopp är inte skadekalibrering. Allvarlig och cellerna är provisoriska metodval. |
| D7 | 2.9.0 | S-ARB-05 endast TF; alternativ behåll generellt PT-påslag. | Organisationsformen ensam belägger inte PT-kedja. H-03 kvar i båda dimensioner men faktorn höjer bara TF. Separata verkliga PT-faktorer kvarstår. Ideell/PEP ensam och båda med känd/okänd samförekomst. |
| D8 | 2.10.0 | Behåll högst ett PT-steg per täckt hot/tjänst och belagd effekt; alternativ nivå-/gradberoende reduktion. | Katalogmål är inte effektbelägg. Lokal prövning av period, räckvidd, stickprov och begränsningar kvarstår. Inga nya MOD-mål för att kringgå max. |
| D9 | 2.11.0 | Behåll +1 och tak hög med scenarioavgränsad ersättning; alternativ områdespoäng eller kalibrerade vikter. | Heuristisk konservativ indikatoransamling, inte sannolikhetsestimat eller påstått oberoende. Områden bevisar inte oberoende. Mättnad och kvarvarande orsaker ska synas. |
| D-LAGRE | 2.12.0 | Fortsatt enbart redovisning, ingen nivåeffekt; alternativ avdrag efter dokumenterad relevans-/överlappsprövning. | Land-/kundfördelning och gemensamma kontrollmekanismer räcker inte för ett kalibrerat tjänsteavdrag. Positiv lågindikator neutraliserar inte högre faktor. |

Varje rad får egna källbelägg och granskningsobjekt i regelbasen och granskningsunderlaget. Vid senare ändring av delad fil/objekt binds tidigare beslut om, fortsatt `ej_granskad`; detta dokumenteras som följdberoende. Ny metodtext redovisas ur aktuell regelbas i V10. Efter D byggs två nya PDF:er och lämnas till användarens slutkontroll före E.
