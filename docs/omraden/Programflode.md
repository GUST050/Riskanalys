---
typ: flode
tags: [riskanalys, oversikt]
---

# Hela programflödet

[[docs/START.md|Start]] · [[docs/kodkarta/INDEX.md|Alla projektfiler]]

Aktuell läsordning efter uppdateringen till `main` (`8ca798d`, 2026-10-24). Filkorten visar statiska importer; de är inte ett bevis för testtäckning eller körordning.

1. [[docs/omraden/Regelverk.md|Regelverk]] läser kataloger, datumstyrda krav och källbundna metodförslag.
2. [[docs/omraden/Foretagsdata.md|Företagsdata]] lämnar registerförslag till [[docs/omraden/Intag.md|intaget]].
3. [[docs/omraden/Intag.md|Intaget]] bekräftar fakta till [[docs/omraden/Profil.md|byråprofilen]]. Tjänsteplaner, återkallelse och införande har uttryckliga val.
4. [[docs/omraden/Riskmotor.md|Riskmotorn]] räknar deterministiskt från den bekräftade profilen och regelbasen. Bedömning, profilbytes och modellbindning fryses tillsammans.
5. [[docs/omraden/Lokal-analys.md|Lokal analys]] samlar privata underlag i schema 2 med uttrycklig tjänstetillämpning, täckningsprövning och separata analysbeslut. Äldre schema överförs uttryckligen utan attester.
6. [[docs/omraden/AI-skrivning.md|AI-skrivningen]] skriver från tillåtna faktablad enligt skrivformat V8. Privata analyssvar skickas inte till AI.
7. [[docs/omraden/Rapport.md|Rapportbyggaren]] bygger V10 via V9 och full V8-analys, med samma sparade skrivsvar. Resultatrapport och bilagor har bundna källor.
8. [[docs/omraden/Granskning.md|Granskningen]] återbygger dokument, källor och kravkarta samt registrerar maskinella fynd. Mänsklig sakgranskning är ett separat steg.
9. [[docs/omraden/Word-och-leverans.md|Presentation och Word]] binder redaktionella flyttar till källorna och exporterar resultatrapport, analysbilaga A och underlagsbilaga B1 tillsammans. Äldre utkast byter presentation genom ett uttryckligt val med förnyad granskning.
10. [[docs/omraden/Granskning.md|Fastställelsen]] prövar grindar och samlad resultatgranskning. [[docs/omraden/Drift-och-lagring.md|Drift och lagring]] bevarar manifest, historik och frysta paket.

[[docs/omraden/CLI.md|Kommandoraden]] och det lokala webbgränssnittet når samma kärna. [[docs/omraden/Tester.md|Testerna]] använder syntetiska data och explicita profiler. Ett utkast kan vara ofullständigt; fastställelsen har starkare grindar. Regelobjekt och metodförslag är fortsatt `ej_granskad` tills verklig sakkunnigprövning skett.
