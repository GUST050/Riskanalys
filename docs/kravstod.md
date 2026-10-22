# Planer och kombinationsgrupper

Programmet har lokalt underlag för förändringar och samtidig exponering. Riskmotorns metod är oförändrad. Planantaganden och grupper skickas inte till AI och tolkas inte automatiskt till poäng.

## Planera och utvärdera en förändring

Öppna **Planer och kombinationsgrupper** i det lokala intaget. Välj tjänst, registrera plan-ID och förändringstyp. Beskriv kundtyper, arbetsmoment och befogenheter, underlag och insyn, leverans och geografiska anknytningar. Frivilliga svar per fråga är planantaganden och ersätter inte aktuella profiluppgifter. En registrerad plans ID och tjänst behålls; använd en ny plan för en annan tjänst.

Öppna den sparade planen. Dokumentera en faktiskt genomförd utvärdering av den allmänna riskbedömningen: vilket underlag som prövats, berörda hot och sårbarheter, påverkan på risk och rutiner samt vad som uppdateras eller motiverat behålls. Datum får inte ligga i framtiden eller före de faktiska beläggen. Ett planerat framtida antal kan däremot avse en framtida period; det är inte faktisk historik.

Därefter kan ett tidigare bekräftat nej ändras till ja. När erbjudandet sparas med giltig utvärdering avslutas en plan av typen Ny tjänst atomiskt med profilsparningen. Genomförandedatum, ansvarig, den då gällande utvärderingen och planens oförändrade innehåll bevaras som historik. Ändringar av redan erbjudna tjänster avslutas med en särskild registrering av faktiskt genomförande i webb eller CLI. Avsett datum eller dagens erbjudandeflagga avslutar ingen plan automatiskt. Saknas en aktuell utvärdering stoppar programmet införandet. En genomförd plan kontrolleras inte på nytt mot senare byråfakta, bedömningsdatum eller regelbas. Den får inte redigeras eller återanvändas vid återinförande: registrera en ny plan. Den ordinarie årliga utvärderingen och uppdatering vid förändrade förhållanden gäller fortsatt.

Ett okänt erbjudande kan bekräftas vid första kartläggningen; kända tidigare nej, även i äldre profilformat, får inte kringgå spärren genom ett mellanliggande okänt svar.

En ännu inte genomförd plan kräver omprövning om planen, källan eller en relevant sakuppgift ändras. För att uppdatera beläggen för oförändrade planvärden fyller du i nytt underlag, funktion och datum samt eventuell period. Lämna dessa beläggsfält tomma när endast planbeskrivningen ändras och de tidigare antagandena med sina belägg ska behållas.

För ett felregistrerat nej finns en särskild rättelse med motivering, källa, ansvarig funktion och datum. Den får inte användas för att kringgå en verklig registrerad förändringsplan. Före- och efteruppgifter samt ursprunglig profilrevision journalförs. Journalen registrerar begärd rättelse före profilskrivning; vid skrivfel visar den sparade profilen om eftervärdet genomfördes.

Planutvärderingar flyttar inte årsfristen för hela den allmänna riskbedömningen. Historikändringen gör befintlig analys inaktuell: förnya bindningen, jämför underlagen och sakpröva igen. Profiländringar kräver dessutom en ny aktuell bedömning enligt ordinarie flöde. Historiska beslut bevaras, men återanvänds inte som godkännanden av nya fakta.

## Beskriv en kombinationsgrupp

Ange en tjänst, ett beständigt grupp-ID, avgränsning och beskrivning, tjänstens relevanta sårbarhets-ID:n samt antal och bas. Välj en population, **kunder** eller **uppdrag**, som gäller båda antalen. Antal och bas ska avse samma period, källa och bekräftelse. Tomt antal betyder okänt; 0 är ett faktiskt antal. Bas 0 betyder inte låg risk.

Beskriv hur samförekomsten har belagts. Exempel: samma åtta uppdrag har två egenskaper. Separata marginaltal om åtta i vardera kategorin styrker inte att det är samma uppdrag. Överlappande grupper summeras inte till unika totaler. Programmet kan kontrollera den deklarerade populationen och metadata, men kan inte avgöra den verkliga enheten från ett bart heltal.

Gruppen visas i rätt tjänsts sårbarhetsunderlag. Byrån behöver pröva vad den betyder lokalt och vid behov uppdatera analys och rutiner. En registrerad grupp är inte ett automatiskt beslut om dess betydelse för risknivån. Numerisk anslutning väntar på preciserade sakkunnigbeslut i det befintliga beslutsformuläret.

## CLI och dokumentation

Webb och CLI använder samma spar- och förändringskontroller. CLI kan läsa typat lokalt underlag från YAML:

```sh
riskanalys plan BYRA --fil plan.yaml
riskanalys utvardera BYRA --plan PLAN_ID --beskrivning 'Genomförd utvärdering med underlag, hot, sårbarheter, påverkan och beslut med skäl'
riskanalys genomfor-plan BYRA PLAN_ID --datum ÅÅÅÅ-MM-DD --ansvarig 'Ansvarig för genomförandet'
riskanalys kombinationsgrupp BYRA --fil grupp.yaml
riskanalys bekrafta BYRA P-TJ.red01_erbjuds ja --kalla 'Tidigare uppdragsavtal' --rattelse --motivering 'Fel vid den första registreringen'
```

En minimal planfil har följande form. Innehållet är ett påhittat exempel; verkliga underlag ska ligga i byråns privata datamapp utanför Git.

```yaml
id: nytt_bokslut
tjanst: T-RED-02
typ: ny_tjanst
beskrivning: 'Planerade bokslutsuppdrag för ägarledda bolag med bankunderlag via kunden och digital leverans inom Sverige.'
uppgifter: {}
```

V8 behålls. Gemensamma mekanismer för aktiverade faktorer står i D-ARB.5, lokal tillämpning och grupper vid tjänsten, fullständiga motorberäkningar samt planunderlag och förändringsutvärderingar i B1. Läsrapport och B1 utgör tillsammans dokumentationen. Exporten ersätter inte verksamhetens information, utbildning eller sakliga utvärdering.

## Uppgradering av befintlig installation

Profilmodellernas ändring ger ny källbunden modellidentitet. Befintliga analysgodkännanden och modellriskunderlag kan därför inte återanvändas utan förnyelse efter uppgraderingen, även om risknivåerna blir lika. Följ ordinarie flöde med aktuell bedömning, jämförelse av underlag, uttrycklig analysförnyelse, sakprövning och nytt godkännande. Historiska fastställda paket bevaras.

Planposter från den första implementationen saknar genomföranderegistrering. Programmet antar inte att de är genomförda utifrån ja eller avsett datum. Genomförandet behöver registreras uttryckligen efter kontroll av underlag; den nuvarande utvärderingsbindningen måste då vara giltig. Genomförda planposter från det nya flödet förblir sedan historik.
