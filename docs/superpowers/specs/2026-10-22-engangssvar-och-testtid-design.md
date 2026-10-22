# Engångssvar och kortare testkörningar – granskningsförslag

Status: genomförande godkänt av användaren efter bifogad plangranskning. Reviderad enligt granskningen; implementation påbörjas nu. Bas: `f66a70f62d3baf26d2e47d5d5e97ba0bdce1c3a4`. Ersätter tidigare förenklingsmål där de strider mot användarens precisering: byrån svarar på gemensamma sårbarhetsfrågor en gång och underlaget återanvänds automatiskt.

## 1. Två leveranser, i denna ordning

1. Förkorta verifieringen och besluta en tydlig körpolicy. Behåll säkerhetskraven och fullständig leveranskontroll.
2. Genomför förenklingen av användarens arbete. Mät ett direkt skapat schema-2-fall, inte bara överföringsförslag.

Planerna är separata eftersom testförbättringen ska kunna levereras även om produktförändringen behöver revideras. Ingen ny fullsvit ska köras enbart för att granska dessa planer.

## 2. Faktisk testbas

Den sparade fullsviten gav 3 198 godkända, ett livetest bortvalt, 2 152,78 s på Python 3.12.15. JUnit summerar provtider till 2 150,758 s; skillnaden mot väggtid är normal körningsöverbyggnad. Källa: `.superpowers/sdd/2026-10-22-forenklad-riskbedomning-plan/final-full.{log,xml}`. JUnit SHA-256: `647b187b923bd005931ec2d8c9aea4f03b1d90ee54677c940356af5bc5f637cd`.

| Fil | Prov | Summerad tid |
|---|---:|---:|
| `tester/m2/test_m2_kedja.py` | 11 | 452,74 s |
| `tester/intag/test_webb.py` | 16 | 403,64 s |
| `tester/intag/test_rapportflode_v8.py` | 19 | 137,28 s |
| `tester/intag/test_analys.py` | 33 | 129,94 s |
| `tester/enhet/test_analysgrind.py` | 67 | 129,56 s |
| `tester/typfall/test_gemensam_analys_hela_kedjan.py` | 8 | 124,94 s |

De två första filerna står för 39,82 procent av summerad provtid. [Sparad baslinje](../reviews/2026-10-22-testtid-baslinje.json) innehåller de 20 största filerna och proveniens. Koden visar upprepade fullständiga CLI-kedjor, ett subprocessanrop per dokumentavsnittsgranskning och tre genomgångar av hela webbformuläret. Detta är belagda upprepningar; hur mycket respektive förberedelse kan sparas ska mätas. Serveravstängning och generell parallellisering är inte visade huvudorsaker. Tidigare fyrvägsparallell körning gav HTTP-tidsgränser och ska inte vara förstahandsåtgärd.

## 3. Teststrategi

- `snabb`: deterministiska innehålls-, bindnings- och säkerhetsprov med små syntetiska underlag.
- `analys`: berörda innehållsprov plus webb/CLI/import/lagring för analysflödet.
- `full`: samtliga ordinarie icke-liveprov, inklusive riktiga subprocesser, HTTP, DOCX och fastställelse. Vanlig `pytest -q` ska fortfarande köra hela ordinarie sviten.
- Riktade RED/GREEN-prov under arbetet. Ingen fullsvit efter varje rättad rad eller dokumentändring.
- Fullsvit efter testomläggningen, före produktleveransen och efter en eventuell slutlig kodrättning. En grön körning får återanvändas när dess kod-, test-, regelbas- och verktygssnapshot är oförändrat.
- Befintlig AGENTS regel 6 kräver fullsvit före varje commit. Plan T innehåller ett uttryckligt förslag att ändra den: riktad grön verifiering före arbetscommits, full grön verifiering före leverans/PR/merge och efter ändrad testinfrastruktur. Regeln ändras först när planen godkänts; den får inte kringgås tyst.

Mål på samma dator: snabbprofil högst 60 s, analysprofil högst 3 min, fullsvit preliminärt 22–25 min efter denna omgång. Snabb-/analystider är mål, fullsvitstiden är granskarens uppskattning, inte uppmätta löften. Tio minuter kräver ett separat steg. Redovisa faktisk tid och kvarstående gap. Gör en prioriterad optimeringsomgång; starta inte en obegränsad ombyggnad för att nå minutmålet.

Varje ersatt dyrt prov ska ha en spårbar motsvarighet för sina påståenden. Behåll riktiga gränsprov för CLI, HTTP, privat filläsning, atomisk publicering, dokumentrendering och fastställelse. Färre testfunktioner eller grönt snabburval bevisar inte full täckning. Delad fixtur får bara vara läskälla; varje muterande prov använder en egen kopia. Tidsberoende och korruption får inte läcka mellan prov. Inget produktionscache införs för att få testerna snabbare.

## 4. Produktens avsedda flöde

1. Välj tjänster och beskriv deras arbetsmoment, mandat och insyn.
2. Besvara och belägg gemensamma frågor en gång. Spara fakta, antagande och kunskapslucka med rätt status.
3. Visa en gemensam översikt över automatisk återanvändning i de valda tjänsterna. En samlad handling bekräftar visat gemensamt underlag och standardtillämpning. Inga kryss krävs per kombination av tjänst och post. Befintliga avvikelser/osäkerhetsval skrivs aldrig över.
4. Visa varje tjänsts analys med ärvda fakta, hot, lokala förutsättningar, samverkan och risk. Endast avvikelser och tjänstespecifika frågor behöver egna svar. Automatiskt återanvända fakta betyder inte att alla faktorer har samma betydelse eller ändrar alla risknivåer.
5. En handling per tjänst bekräftar den visade, kompletta tjänstegenomgången. Aktuella scenarioval och de 16 interna blocksummorna registreras tillsammans. Detta ersätter separata block-/scenarioklick, inte innehållsprövningen.
6. Analysgodkännande, särskilda täckningsprövningar, dokumentets sakgranskning och fastställelse behåller egna krav. Dessa får inte automatiskt skapas av de två samlade handlingarna.

Interna tillämpningar och blocksummor får materialiseras per tjänst för spårbarhet. Byrån ska inte återskriva faktaunderlaget eller behöva öppna varje post per tjänst. Nya tjänster ärver visat gemensamt underlag som utgångspunkt; tjänstens nya genomgång krävs fortfarande men dess standardtillämpningar ska först bekräftas i den gemensamma handlingen, utan att svaren skrivs om.

## 5. Lagring och säkerhet

- Behåll schema 1 och historiska serialiserings-/attestkontrakt. Behåll schema 2:s befintliga post-, tillämpnings-, scenario- och blocktyper; inget schema 3 behövs för samlade handlingar.
- Gemensamma fakta lagras en gång i nya analyser. Äldre originalsvar och attributioner får inte raderas vid överföring för att ge snyggare mätning.
- Samlade handlingar kontrollerar visad revision, postreferenser, målservice-ID, författare och giltiga underlag inom samma analyslås. Ett fel lämnar hela handlingen osparad.
- Bekräfta endast det som visats. Oklar aktivering, saknat svar, obelagd sänkning eller otillräcklig täckning stoppar tjänstegenomgången. Antaganden blir inte fakta.
- Import får inte skapa samlade bekräftelser, blocksummor, analysbeslut eller visad täckning. Inga allmänna flaggor för att hoppa över fastställelsens innehållskontroll införs.
- Ändrat underlag gör berörda bekräftelser inaktuella och alla analysbeslut inaktuella enligt befintlig paketbindning. En samlad förnyad genomgång ska vara möjlig utan att skriva om oförändrade svar.
- Inga riskvikter, trösklar, konsekvensskalor, kontrollavdrag, D3/D9-beslut eller verkliga sakkunnigstatusar ändras. Inga privata analysuppgifter skickas till AI. Alla automatiska prov använder syntetiska uppgifter och Testleverantor.

## 6. Mätbar acceptans

Ett nytt fyrtjänstfall utan avvikelser ska ha ett enda lagrat gemensamt svar per fråga, automatisk användning i fyra läsvyer och inga separata bekräftelser för samma fråga i varje tjänst. Efter svarsinmatning ska den kontrollerade bekräftelsejämförelsen omfatta en gemensam handling och fyra tjänstegenomgångar, i stället för 32 scenarioval + 64 block. Detta är fem bekräftelsehandlingar, inte fem totala klick: redigeringar, svar, analysbeslut, täckningsprövningar och sakgranskningar räknas separat och redovisas också.

Två nya analyser byggs direkt i schema 2: `fyra_tjanster` och `med_betalningsmandat`, med samma fakta, motor och frysta skrivsvar som jämförelsefallen. D-ARB.5 återger gemensam beskrivning en gång; tjänsten hänvisar och förklarar lokal betydelse/avvikelse. Mät läsrapport, B1, total, ordagrann upprepning och verkliga användarhandlingar. Bevara tidigare överföringsmätning som en separat uppgraderingskostnad. Rapportförkortning får inte skapas genom att utelämna sakligt underlag eller flytta det till B1.

Ett avvikelsefall ska dessutom visa att en lokal avvikelse inte ändrar övriga tjänster, att oklarhet fortfarande spärrar och att egen PT/TF-risk med obligatoriska riskled behöver särskild täckning. Gröna teknikprov ersätter inte byråns sakliga bedömning.

## 7. Alternativ och vald inriktning

- Enbart parallella tester: snabb att föreslå men tidigare instabil och tar inte bort upprepad uppbyggnad. Avvaktas.
- Enbart färre knappar för block 5/7/9: liten rättning men lämnar dubblettfrågor och större delen av bekräftelsearbetet. Otillräckligt som slutmål.
- Rekommenderat: återanvänd testlägen med spårad täckning; därefter gemensamt faktaunderlag och undantagsstyrd tjänstegenomgång med befintliga interna kontroller.

Planer: [T – snabbare verifiering](../plans/2026-10-22-snabbare-verifiering-plan.md), därefter [F – engångssvar och automatisk återanvändning](../plans/2026-10-22-engangssvar-plan.md). Användaren vill granska införandet med Claude; underlagen lämnas för den granskningen innan genomförande.

## Revidering efter granskning

Ordningen är gemensam bekräftelse → särskilda täckningsprövningar → tjänstegenomgång. Tjänstegenomgången ändrar inga tillämpningar. Kandidaten med interna block-/scenariostämplar prövas med den ordinarie grinden inklusive samtliga gemensamma brister; ingen flagga införs som undantar bekräftelsekrav. Gemensam begäran innehåller exakt visade celler `(tjanst, slag, post, postsumma)`; avvikande mängd avvisas atomiskt. Båda mätfallen ska ange faktiskt antal nödvändiga och utförda täckningsprövningar. Ny testpolicy anger `.venv312/bin/python` och tillåter ingen push/merge före grön fullsvit på leveransens exakta kod-/test-/regelbas-/verktygssnapshot.
