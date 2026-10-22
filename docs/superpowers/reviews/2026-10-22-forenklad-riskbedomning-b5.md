# B4–B5: gemensam analys, lokala tillämpningar och V8-rapport

Granskningsbas: `0be7327decd1fbb494c52c8769046e2c492fb52d`. Nästa leveranscommit innehåller B4–B5; B6–B7 följer separat. Ändringen hålls lokal på `codex/kravstod-tjansteexponering` för Claudes granskning. Ingen push eller merge.

## Konkret beteende

Nya analyser i webb/CLI använder schema 2. Gemensamt byråunderlag skrivs och beläggs en gång; varje tjänst bekräftar bara uttryckligen markerade oförändrade tillämpningar eller anger belagd avvikelse. Samlad bekräftelse skriver inte över avvikelser. Ett tillämpat antagande förblir ett antagande. Äldre schema 1 är fortsatt läsbart; överföringsoperationen kommer i B6.

Tre arbetsvyer använder samma typade, låsta och revisionskontrollerade operationer som kommandoraden. Täckningsprövningen visar befintligt motorscenario med en extra +1-faktor som referens. Den påverkar aldrig faktiskt motorutfall. En lägre jämförelsenivå kräver en särskild motivering och senare sakgranskning.

V8 redovisar gemensam mekanism en gång i D-ARB.5, lokal tillämpning och avvikelser per tjänst samt originalfält och beräkningsspår i B1. Proveniens pekar på faktiskt lagrade poster. Rapportproducentens bindning och ombyggnadskontroll omfattar schema 2. Analysbeslut är fortfarande bundna till hela paketet; inga selektiva godkännanden har införts.

Ett separat **ofullständigt omfattningsunderlag** kan exporteras för tjänster utanför katalogen. Det har separat dokument-ID, manifesttyp, filnamn och fastställelsespärr. Det innehåller inga manuella risknivåer och kan inte ersätta en färdig allmän riskbedömning. Manuell tjänsteanalys är fortsatt en känd produktbegränsning, inte ett påstått lagkrav på motor.

## Verifiering

Python 3.12.15, enbart syntetiska fakta och Testleverantor. Riktade B4-prov: 132 godkända; CLI 17 godkända. B5:s breda rapport-/exportprov: 132 godkända. Separata verkliga CLI-/webbexporter och fastställelsespärr provade. Sista extra regressionsurvalet: 41 godkända.

Första fullsviten: 3 143 godkända, ett fel, ett livetest bortvalt. Felet var att omfattningsknappen läste profil på nytt trots ett redan tillhandahållet profilargument. Det är rättat med regressionstest; första försöket räknas inte som godkänd leveransverifiering.

Färsk godkänd fullsvit: **3 149 godkända, ett livetest bortvalt, exit 0**, 2 023,52 s (wrapper 2 023,93 s). JUnit visar 0 fel, 0 errors, 0 skipped. Källkodens snapshot var oförändrat under hela körningen. Regelbasvalidering och `git diff --check` passerar. Rålogg, JUnit och källsnapshot finns i den ignorerade planarbetsmappen som bevaras för Claude.

Ett positivt syntetiskt schema-2-förprov, inklusive egen sårbarhet och lägre avvikelse, genomförde 105 faktiska bekräftelseoperationer och fyra analysbeslut. `analysbrister == ()` och kanonisk dokumentgranskning utan fynd. Full fastställelse och jämförande arbetsbördemätning ingår i B7; förprovet ersätter inte dem.

## Dokumentkontroll

Tre verkliga DOCX-exporter skapades av produkten och renderades med dokumentverktygets LibreOffice-flöde: läsrapport 44 sidor, B1 101 sidor, omfattningsunderlag 10 sidor. Första visuella passet hittade engelskliknande interna statuskoder och saknad periodmetadata; regressionstest och korrigering följdes av omrendering. Gemensamt underlag, lokal avvikelse, omfattning och B1 kontrollerades på utvalda sidor (läsrapport 7/11, B1 66/75, omfattning 1). Ingen klippning eller överlappning observerades där. Detta är riktad visuell kontroll, inte ett påstående att varje sida är manuellt godkänd.

Rapportlängd och faktisk arbetsbörda ska redovisas för båda frysta fallen i B7. En omflyttning till B1 räknas inte som en minskning. Slutgranskningen ska särskilt kontrollera att kända falska villkor inte blir metodkonflikter, att allmän PT/TF-angivelse inte skapar en koppling som inte påståtts, samt att egna risker aldrig täcks av en hög generell tjänstenivå ensam.

## Återstående före slutleverans

B6: uttrycklig jämförelse/överföring av äldre analyser med exakta originalbytes i historiken och utan överförda godkännanden. B7: kedja till fastställelse, privata schema-2-data mot exakta AI-begäranden, längd/bekräftelser, UI och slutlig helgranskning. Grenen är ännu under utveckling och ska inte tas i skarp drift mellan delcommits.

### Kända regressionsfall för nästa steg, redan reproducerade

Under den frysta fullsviten förbereddes B7-prov i separata, ej insamlade testfiler. De reproducerade två ytterligare kanter: en oklar/högre `galler_annorlunda` utan katalogfaktor tappade sin riktningsprövning, och en gemensam verksamhetsavvikelse ersatte det uttryckligen annorlunda lokalsvaret. Isolerade rättningsutkast passerar respektive RED→GREEN (2 respektive 3 prov); de är inte del av denna checkpoint och förs in i B7 före slutleverans. Denna mellancommit är därför en granskningsbar utvecklingscheckpoint, inte en driftklar release. Ingen slutlig färdigförklaring av B5:s alla avvikelsefall görs förrän dessa rättningar och slutlig fullsvit är klara.
