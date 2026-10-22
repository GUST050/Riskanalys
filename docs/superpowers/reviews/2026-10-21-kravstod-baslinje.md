# Baslinje för genomförandet

Kodbas: `288fa6650ea400fda04cdcef965f8ac17adc3575`. Granskningscommit: `8915f0d154416bcbd482b2b926a6523e7f9405d8`.
Isolerad lokal klon från ren `feat/steg-1-3`, gren `codex/kravstod-tjansteexponering`. Ursprungliga arbetskopior lämnas orörda. Inga senare kodcommits fanns vid starten. GitHub är origin; ingen push ingår.

Alla 13 förväntade commits finns i anor; återanvänds utan cherry-pick:

```text
25be85a fix: analysbeslut binds till sakunderlaget, inte till AI-utkastet
d47dadd feat: delvis täckning bär inget kontrollavdrag; åtgärder får slutkriterium och prioritet
688629f docs: beslutsunderlag för metodbesluten D3, D5, D6, D8 och D9
5c8e96f docs: provkör metodalternativ för D6 och D9 i beslutsunderlaget
4827095 docs: rätta beslutsunderlagets prov 3 efter granskning
4f69288 docs: precisera iakttagelsen om exponering i beslutsunderlaget
74c0b12 docs: beslutsformulär med jämförelsepar för metodbesluten
23932aa docs: komplettera beslutsformuläret med bankinsyn, D5 och precisering före steg 4
2014557 docs: mätverktyg för V8-rapportens längd och upprepningar
8fd6116 feat: gemensamt faktaunderlag och källnot i V8-rapporten
b50ca76 docs: rapportmätning skiljer ordagrann upprepning från likartad struktur
cda6f80 fix: källnoten väljer första förekomsten vid lika vanliga källor
288fa66 feat: fullständiga beräkningsspår i B1, nivå och skäl i läsrapporten
```

Vald interpreter: checkoutens `.venv312/bin/python`, Python 3.12.15. Egen editable-installation av just denna checkout, pydantic 2.14.1, pytest 9.1.1, python-docx 1.2.0. Ingen annan checkouts miljö har återanvänts.

Baslinje på oförändrad produktkod: 170 godkända tester på 232,74 s. Körningen omfattade test_analyslagring, test_reduktionssparr_scenario, test_atgardsgrupper, test_analys_hela_kedjan, test_rendering_v8, test_arb_v8 och test_rapportflode_v8. Logg i den ignorerade genomförandejournalen `.superpowers/sdd/2026-10-21-kravstod-och-tjansteexponering-plan/baseline-tests.log`.

`riskanalys regelbas validera`: exit 0; 107 krav, 11 tjänster, samtliga tre läns kartor 201/201 hanterade. Sakkunnigstatus fortsatt ej_granskad. Kontrollsumma `sha256:7e0f77726a35b5e9fd47b8d324b43236cbeab5ded78c107ccfe54570cc97285f`.

Återanvänt: sakbindning version 2 oberoende av AI-utkast, blockering av kontrollavdrag vid delvis täckning, åtgärdernas slutkriterium/prioritet, åtta befintliga jämförelsepar, rapportmätningsverktyget, D-ARB.5:s gemensamma underlag, deterministisk källnot och fullständiga beräkningstabeller i B1. Baslinjeproven ovan verifierar dessa delar tillsammans; inga gamla testresultat räknas som nya.

Rapport före ändring (samma frysta testleverantör): `fyra_tjanster` 12 665 ord läsrapport + 34 440 B1 = 47 105 totalt. Detaljer för båda fallen finns i genomförandejournalens rapport-fore-*.log. Slutprovet redovisar före/efter separat för delarna.
