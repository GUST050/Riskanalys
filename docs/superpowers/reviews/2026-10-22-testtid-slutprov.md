# Teststrategins slutprov 2026-10-22

Produktbas `f66a70f`; testomläggning `132f8e9` → `1b40ddb`. Python 3.12.15. Endast syntetiska uppgifter och testleverantör.

## Faktiskt utfall

| Kontroll | Prov | Tid |
| --- | ---: | ---: |
| Historisk fullsvit | 3 198 | 2 152,78 s |
| Snabb 1 | 60 | 25,596 s |
| Snabb 2 | 60 | 25.280 s |
| Analys 1 | 152 | 111.334 s |
| Analys 2 | 152 | 111.128 s |
| Första T-fullsvit | 3 214 | 1 661,444 s inklusive collection |
| Slutlig T+F-snabb | 115 | 36,155 s |
| Slutlig T+F-analys | 230 | 169,342 s |
| Slutlig T+F-fullsvit | 3 308 | 1 795,884 s inklusive collection |

Noll fel och skippade prov; ett liveprov bortvalt. Körverktygets första resultat avvisades korrekt som ej verifierat: dess namnnormalisering ändrade snedstreck även inne i parametrar. Två nya regressioner blev röda, och efter rättningen passerade alla tio verktygsprov. Den separata omprövningen av samma collection och JUnit matchar nu samtliga 3 214 fall exakt; de ursprungliga loggarna är oförändrade. Verktygsrättningen och slutgranskningens utökade resursbindning ingår nu i den gemensamma gröna fullsviten med plan F på `2644122`. De första profilerna hade oförändrat dåvarande snapshot; den slutliga kontrollen binder även JSON-fixturer, fixture-YAML och regelbasens text-/övriga resurser (783 filer), med uttryckligt bytekodundantag. Fullsvitens JUnit SHA-256: `ece0972b51d308b69ea22e32492ddca17dfaeb0d42945f3035af12d569a2e714`. Summerad provtid 1658.341 s ska inte blandas ihop med väggtid inklusive collection. Fullsviten kördes sekventiellt; små isolerade F-utkast prövades separat under tiden, vilket kan påverka jämförelsetiden något.

Målen snabb ≤60 s och analys ≤180 s nåddes i båda körningarna. Fullsviten minskade cirka 22.8 procent mot den historiska väggtiden; jämförelsen är inte en kontrollerad prestandamätning på identiska testmängder. Första uppskattningen var 22–25 minuter; faktiskt utfall är 27.69 minuter. Tio minuter har inte utlovats.

De tidigare två största testgrupperna minskade tillsammans från 856,376 s till 371.865 s när ersättningsproven räknas med: M2:s två filer 220,413 s och webbens fullresa 148,854 s plus korta paketval 2.598 s. Det är cirka 56 procent kortare summerad provtid för dessa ansvar; inga borttagna påståenden räknas som tidsvinst.

## Bevarad kontroll

[Påståendematrisen](2026-10-22-testtackningsmatris.md) visar gamla påståenden och ersättande prov. De sju negativa grindarna blev verkligen röda när respektive avsiktligt fel togs bort: sju fallerade, två bortvalda, 57,85 s. Negativa prov kontrollerar både specifik domänorsak, faktisk CLI-spärr och avsaknad av slutpaket. När CLI stoppar tidigare på ändrad bindning redovisas det uttryckligen.

Tre positiva regelpaketkedjor går genom riktiga subprocesser för samtliga kommandotyper. För `sakgranska` körs första avsnittet i en subprocess och resterande avsnitt genom riktiga `cli.main`: en subprocess per paket i stället för en per avsnitt. Antalet beror på rapportens avsnitt; inget statiskt anropsantal eller separat uppmätt hastighetsvinst för transporten påstås. Ett verkligt negativt fastställelseprov och den gamla före-skrivningens beläggsspärresan är kvar. En full HTTP-resa till DOCX samt tre korta paketvalstester ersätter två överlappande resor; övriga HTTP-skydd är kvar.

Befintliga modulfixturer var redan återanvända. T2 stärker isoleringen med separata byrå- och regelbasfiler; de två berörda filernas 254,19 s mot tidigare 254,50 s visar ingen påvisad tidsvinst. Ingen produktcache infördes.

## Tid per fil i den första nya fullsviten

| Fil eller JUnit-klass | Summerad provtid s |
| --- | ---: |
| `tester.intag.test_webb` | 148.85 |
| `tester.intag.test_rapportflode_v8` | 136.71 |
| `tester.intag.test_analys` | 130.33 |
| `tester.enhet.test_analysgrind` | 127.93 |
| `tester.m2.test_m2_kedja` | 127.65 |
| `tester.typfall.test_gemensam_analys_hela_kedjan` | 124.58 |
| `tester.m2.test_m2_grindar` | 92.76 |
| `tester.enhet.test_rapportpaket_v8` | 57.64 |
| `tester.typfall.test_analys_hela_kedjan` | 51.61 |
| `tester.m2.test_sakkunnigpaket` | 49.73 |
| `tester.intag.test_samlade_fragor` | 43.95 |
| `tester.intag.test_samlat_register` | 30.87 |
| `tester.enhet.test_arb_v8` | 28.98 |
| `tester.intag.test_harledbara_antal` | 21.77 |
| `tester.intag.test_tjansteurval_planval` | 21.09 |

Råloggar, collection, JUnit och snapshot finns lokalt i `.superpowers/evidens/2026-10-22-engangssvar/T/`; den gemensamma slutkörningen och efterkontrollen finns i motsvarande `F/`. Arkivets README anger de historiska scratchsökvägarna. De ska bevaras som verifieringsbevis vid överlämningen. Ingen push eller merge ingår.

## Slutlig gemensam leveransgrind

T4 och F3 är klara på fryst källbas `264412289ba35cfc84fe236d406fe9ab9d2c5343`: **3 308 godkända, ett liveprov bortvalt, noll failures/errors/skipped**, full collection exakt täckt av JUnit och alla 783 aktuella resurser oförändrade. Full pytest 1 794,45 s; wrapper med collection 1 795,884 s. JUnit SHA-256 `5c83ce9fc50e7ad240f05b78ddf106f8ef87b8687371d45bf411c396ba14f8f1`; summerad provtid 1 792,733 s. Regelbasvalidering/diffkontroll passerar. Slutgranskningens fyra Important är rättade med riktade RED/GREEN-prov; ingen extra oförändrad fullkörning görs för slutdokumentationen.

Den sista sviten inkluderar fler produktprov än den första T-körningen och tar 29 min 56 s, cirka 16,6 procent mindre väggtid än den historiska basen. Ingen jämförbarhet på exakt samma testmängd påstås; 22–25-minutersuppskattningen nåddes inte. Senaste snabb 36,155 s och analys 169,342 s når målen 60/180 s.

Största kvarstående grupper i slutkörningen: gemensam helkedja 171,479 s (inklusive nya publika inmatnings-/beläggsprov), webb 150,758 s, rapportflöde 136,550 s, analysgrind 128,214 s, analyswebb 128,179 s, M2-kedja 125,357 s och M2-grindar 92,993 s. Resterande detaljer finns i rå tidsrapport. Se [produktens slutprov och samtliga genomförandeval](2026-10-22-engangssvar-slutprov.md).
