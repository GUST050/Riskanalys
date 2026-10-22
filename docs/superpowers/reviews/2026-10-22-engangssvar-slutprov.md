# Engångssvar och snabbare verifiering 2026-10-22

Status: funktionerna och de riktade proven är genomförda. Gemensam slutgranskning och komplett fullsvit återstår innan leverans. Lokala arbetscommits; ingen push eller merge. Produktbas `f66a70f`, T1–T3 `132f8e9`–`1b40ddb`, verktygsrättning `03bd8bd`, F1 `c7a2ccb`, F2 `bb3ee8b`.

## Vad byrån gör

Byrån skriver de gemensamma sårbarhets- och verksamhetssvaren en gång. En gemensam handling bekräftar exakt visade oförändrade tillämpningar för valda erbjudna tjänster. Därefter läser byrån varje tjänsts profilfakta, gemensamma referenser, egna resonemang, hot och PT/TF-bedömning och bekräftar tjänsteunderlaget med en handling. Lokala undantag redigeras separat. Antaganden förblir antaganden.

Det kompletta fyrtjänstprovet går genom verkliga bundna publika operationer med **en gemensam + fyra tjänstehandlingar**, utan 32 scenarioklick eller 64 blockbekräftelser. Det är fem bekräftelser **efter svarsinmatning**, inte fem totala klick. Egen risk kräver dessutom en uttrycklig täckningsprövning per hot, dimension och obligatoriskt riskled; det avancerade provet loggar fyra lokala avvikelser, en gemensam bekräftelse, ett bärande scenarioval, två täckningsprövningar och fyra tjänstegenomgångar. Analysbeslut och dokumentets sakgranskning skapas inte av dessa handlingar.

## Kontroller som finns kvar

- Exakt cellmängd (tjänst, typ, post, postsumma), revision, författare och erbjudande kontrolleras inom analyslåset. Fel, dubbletter, gamla summor eller okända mål avvisar hela skrivningen. Kända avvikelser skrivs inte över.
- Tjänstegenomgången ändrar inga tillämpningar eller täckningsprövningar. Den bygger scenarioval och blockstämplar och kör den ordinarie `analysbrister`, inklusive `gemensamma_analysbrister`, på en ren tjänsteprojektion. Alla gemensamma poster, belägg och bindningar finns kvar. Inget globalt fel filtreras med textprefix och projektionen sparas aldrig.
- Verkliga lokala brister, saknade belägg, oklarhet, otillräckligt kontrollavdrag och otäckt egen PT/TF-risk stoppar fortfarande. Senare ändring gör bundna stämplar/beslut inaktuella enligt befintliga summor. Import skapar inga bekräftelser.
- Motorn, poängen, D3/D9, sakkunnigstatus och AI-tillåtelselistan är oförändrade. Full jämförelse av privata AI-begäranden efter gemensam handling passerar även omförsök och reserv.
- Schema 1:s serialisering och historiska original bevaras. Ingen schema 3 eller rapportversion V9 införs. Vanlig pytest kör fortfarande alla icke-liveprov.

## Mätning av det verkliga schema-2-flödet

`direkt2` startar via schema 2 och publika sparhandlingar; ett prov förbjuder överföringsfunktionen och konvertering av en ifylld schema-1-analys. Samma frysta profil, motor och skrivsvar används i alla tre lägen. ISO-datum i den syntetiska JSON-fixturens värdeunion återställs till datumtypen före riktig profilsparning; det kanoniska JSON-värdet och hashvärdet är oförändrade. Alla ursprungliga fria saktexter, belägg och aktuella författaruppgifter finns kvar, inklusive de fyra olika tjänsteerfarenheterna.

I båda frysta rapportfallen besvaras **sju gemensamma poster en gång**, och **noll lokala kopior av gemensamma svar** lagras. Nödvändiga/utförda egna täckningsprövningar är **0/0 i vartdera fallet**. Råloggen innehåller även nollvärden för separata scenario-, block-, besluts- och sakgranskningshandlingar.

De frysta rapportläsproven innehåller avsiktliga luckor i kontroll och uppdragsförmåga. Därför loggas fyra **nekade** tjänstegenomgångar, inga lyckade. De görs inte falskt färdiga för att nå en klicksiffra. Varje rålogg har 17 steg: fryst profil, bedömning, skrivutkast, schema-2-start, sju gemensamma svar, en lokal svarimport, en gemensam bekräftelse och fyra nekade tjänstehandlingar. Tidigare intagsarbete mäts inte. Det separata kompletta provet ovan bevisar de fem lyckade bekräftelserna.

## Faktisk dokumentlängd

Ord räknas med samma kanoniska synliga dokumenttext, inklusive rubriker och tabeller. Läsrapportens korta källbilaga ingår i läsrapporten. B1 är den kompletterande underlagsbilagan; totalt är summan av delarna. Upprepning är extra förekomster av ordagrant identiska texter med minst tolv ord över båda delar, inte en bedömning av att innehållet kan tas bort.

| Fall | Läge | Läsrapport | B1 | Totalt | Extra upprepade ord |
| --- | --- | ---: | ---: | ---: | ---: |
| fyra_tjanster | schema1 | 13 756 | 34 658 | 48 414 | 10 836 |
| fyra_tjanster | direkt2 | 16 446 | 36 005 | 52 451 | 11 778 |
| fyra_tjanster | overforing2 | 14 404 | 35 854 | 50 258 | 11 394 |
| med_betalningsmandat | schema1 | 13 433 | 34 827 | 48 260 | 11 094 |
| med_betalningsmandat | direkt2 | 16 123 | 36 150 | 52 273 | 12 012 |
| med_betalningsmandat | overforing2 | 14 081 | 36 023 | 50 104 | 11 652 |

Direkt2 är **4 037 respektive 4 013 ord längre totalt än schema 1**, inte kortare. Bekräftade tillämpningar synliggör D9-prövningar som ett obekräftat överföringsförslag inte visar. Jämförelsen bevarar sakunderlaget men har olika bekräftelsestatus. Ingen tidsvinst för människans läsning påstås.

Den första native-mätningen hade 60 475/60 297 ord. Ett reproducerande prov fångade upprepade fullständiga D9-villkor per hot/tjänst. Den lokala upplysningen grupperas nu per faktor, med alla hot/dimensioner kvar; fulla fakta och villkor fanns redan i B1. Det tog bort 8 024 ord i vardera fallet; **B1 är ordmässigt oförändrad före/efter just den rättningen**. Ingen information flyttades till B1 för att få en kortare läsrapport. Någon större redaktionell ombyggnad ingår inte.

## Teknisk och visuell verifiering

F1: 17 RED → 17 GREEN; berört urval 71 godkända, 48,53 s. F2: 20 RED; efter rättning av visning av valfri scenariomotivering passerar 30 kärn-/CLI-prov, 9,20 s. Två verkliga bundna publika kedjeprov passerar, 31,50 s. F3: saknade native-gränssnitt och formulärövergång reproducerade, därefter 13 godkända, 37,50 s. D9-upprepning RED2 → GREEN12 med rapportproven, 22,32 s. Native UI-fynd RED2 → GREEN2, 16,83 s. Privata AI-begäranden normal/omförsök/reserv: tre godkända, 2,59 s.

Slutliga arbetsprofiler efter F3: **snabb 102 prov/34,006 s och analys 217 prov/168,677 s**, båda med exakt collection/JUnit och oförändrat aktuellt snapshot. Fullsvit redovisas efter den gemensamma slutgranskningen. T:s separata mätning och skyddade testomläggning finns i [testslutprovet](2026-10-22-testtid-slutprov.md) och [påståendematrisen](2026-10-22-testtackningsmatris.md).

En riktig syntetisk browser-session har bekräftat gemensamt underlag, läst den samlade tjänstevyn och sparat ett lokalt berör-inte-undantag. Kontrollen visar oförändrade gemensamma original, övriga tjänster och motorutfall samt inga analysbeslut. Perioder visas läsbart, faktorn identifieras och gemensamt arv märks inte som ett saknat nytt svar. Testflik och egen loopbackserver är stängda; inga riktiga byrådata eller API-anrop användes.

Båda faktiska Word-delar har exporterats och renderats för båda direkt2-fallen (43+103 respektive 42+106 sidor). En separat syntetisk undantagsrapport renderades också (43 sidor). **Riktad PNG-kontroll av åtta sidor**, inte fullsidig kontroll: fyrtjänst-läsrapport 6/13, fyrtjänst-B1 67/70, mandat-läsrapport 33/37, mandat-B1 70 och undantagsrapport 13. Gemensam prövning, lokal tillämpning, oförändrad högre motor, PT/TF, tabeller och raw-underlag är läsbara utan observerad klippning/överlapp på de kontrollerade sidorna. Före-/efter-metadata och exporter har separata mappar.

## Genomförandeval att granska

1. Egen täckning som använder ett gemensamt scenario kräver först ett uttryckligt bärande scenarioval, eftersom den befintliga täckningssumman binder det effektiva scenariot. Normalfallet behåller fem bekräftelser. Kostnad om beslutet är för strängt: ett överflödigt val för egna risker.
2. De två frysta rapportfallen behåller sina avsiktliga sakluckor. Fem lyckade handlingar bevisas separat med ett komplett fall. Kostnad: rapportjämförelsen är inte ett prov av två färdiga riskbedömningar.
3. Efter felet i körverktygets parameter-normalisering samordnas den rättade T-infrastrukturens fullsvit med F:s slutgrind, i stället för en extra 27-minuterskörning före fortsatt redan beställt F-arbete. Kostnad: integrationsfel kan upptäckas först vid slutgrinden; ingen leverans/push/merge före grönt.

## Kvarstående gränser och granskningsväg

Rapporten är fortfarande lång. Ingen kalibrering av risknivåerna eller ny manuell tjänsteanalys utanför katalogen ingår. En allmän analys ersätter inte kundriskbedömning. Tekniskt grönt ersätter inte byråns sakgranskning eller verklig metod-/sakkunnigprövning.

Granska diffen från `f66a70f` till leveransens lokala HEAD och de tre genomförandevalen ovan. Planspecifikationerna ligger i `docs/superpowers/specs/2026-10-22-engangssvar-och-testtid-design.md` samt plan T/F. Råbevis finns lokalt under `.superpowers/sdd/2026-10-22-engangssvar-plan/` och T:s motsvarande mapp tills överlämningens evidensarkiv har färdigställts. Inga externa meddelanden, pushar eller merger ingår.
