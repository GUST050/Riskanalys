---
typ: omrade
omrade: Riskmotor
kontext_granskad: 2026-10-24
tags: [riskanalys, omrade, ai-kontext]
---

# Deterministisk riskmotor

Beräkna deterministiska riskutfall per tjänst, hot och dimension från bekräftad profil och vald regelbas. Text och presentation ska återge dessa utfall.

[[docs/START.md|Arbetsgång och kontextnivåer]] · [[docs/omraden/Programflode.md|Programflödet]] · [[docs/kodkarta/omraden/Riskmotor.md|Alla filkort i området]]

## Minsta kodkontext

Läs uppgiftens ingång och relevanta typer först; tabellen är en läsordning, inte krav att läsa allt. Filkorten leder till originalen. Kontrollera kontrakten mot aktuell kod.

| Fil | Varför |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/bedomning/motor.py.md\|src/riskanalys/bedomning/motor.py]] | bedom och bedom_tjanst samordnar beräkningen. |
| [[docs/kodkarta/filer/src/riskanalys/bedomning/scenarier.py.md\|src/riskanalys/bedomning/scenarier.py]] | Sannolikhet, konsekvens och kontrollpåverkan per scenario. |
| [[docs/kodkarta/filer/src/riskanalys/bedomning/modeller.py.md\|src/riskanalys/bedomning/modeller.py]] | Bedomning, Tjanstbedomning och Scenariobedomning. |
| [[docs/kodkarta/filer/src/riskanalys/bedomning/korning.py.md\|src/riskanalys/bedomning/korning.py]] | Fryst profil, modellbindning, manifest och aktualitet. |

## Kontrakt att bevara

- Indata: Regelbas, Urval och Profil. Utdata: motorägda nivåer, scenarioresultat och regelspår; samma indata ska ge samma resultat.
- Kontrollpåverkan filtreras till samma hot/tjänst/dimension. Behåll den historiska vägen när scenariometod saknas.
- Tjänstens maxnivå och alla avgörande scenarier bevaras. Lokal prövning av faktisk reduktion kräver mer än en generell kontrolltext.
- Ändrad eller saknad modellbindning stoppar ny fortsättning. Presentation ska inte räknas som ändrad riskmodell.

## Nya ingångar efter merge till main

| Fil | Ansvar |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/analys/riktning.py.md\|src/riskanalys/analys/riktning.py]] | Skilj försiktighetspåslag från belagd riskriktning. |
| [[docs/kodkarta/filer/src/riskanalys/analys/referens.py.md\|src/riskanalys/analys/referens.py]] | Kontrafaktisk referens under samma scenarioregler. |
| [[docs/kodkarta/filer/src/riskanalys/regelverk/metodbeslut.py.md\|src/riskanalys/regelverk/metodbeslut.py]] | Metodbeslutens kod- och sakbindning. |

## Fördjupa bara vid behov

| När uppgiften gäller | Läs vidare |
|---|---|
| Kundmodellens separata spår | [[docs/kodkarta/filer/src/riskanalys/bedomning/kundmodell/modeller.py.md\|src/riskanalys/bedomning/kundmodell/modeller.py]] · [[docs/kodkarta/filer/src/riskanalys/bedomning/kundmodell/tabeller.py.md\|src/riskanalys/bedomning/kundmodell/tabeller.py]] |
| Belägg för faktisk kontrollreduktion | [[docs/kodkarta/filer/src/riskanalys/analys/provning.py.md\|src/riskanalys/analys/provning.py]] · [[docs/kodkarta/filer/src/riskanalys/drift/modellidentitet.py.md\|src/riskanalys/drift/modellidentitet.py]] |

## Berörda områdesgränser

- [[docs/omraden/Profil.md|Profil]] när beräkningsunderlag eller profilsnapshot ändras.
- [[docs/omraden/Regelverk.md|Regelverk]] när hot, villkor, skalor eller kataloger ändras.
- [[docs/omraden/Lokal-analys.md|Lokal-analys]] när reduktion behöver lokal prövning.
- [[docs/omraden/Rapport.md|Rapport]] när utfall, orsaker eller tabeller får nytt schema.

Kontrollera direkta importer och bakåtlänkar för den ändrade filen, och sök även funktions-/fältnamn i koden. Statiska importer visar varken alla runtimekopplingar eller faktisk testtäckning.

## Verifiering

Börja med följande provurval när det passar ändringen; det ersätter inte bredare verifiering av ändrade kontrakt.

```bash
env -u ANTHROPIC_API_KEY .venv312/bin/python -m pytest tester/regelkontrakt/test_scenariomotor.py tester/regelkontrakt/test_motor.py -q
```

Vid berörd kedja: [[docs/kodkarta/filer/tester/enhet/test_reduktionssparr_scenario.py.md|tester/enhet/test_reduktionssparr_scenario.py]] · [[docs/kodkarta/filer/tester/enhet/test_bedomningsbindning.py.md|tester/enhet/test_bedomningsbindning.py]].

Nya kontrakt har särskilda regressioner:

```bash
env -u ANTHROPIC_API_KEY .venv312/bin/python -m pytest tester/enhet/test_riktning_v2.py tester/enhet/test_referensniva.py -q
```

## Styrande avsnitt

[[docs/superpowers/specs/2026-10-08-riskanalys-design.md#7 Riskmetod|Spec §7 Riskmetod]] · [[docs/superpowers/specs/2026-10-08-riskanalys-design.md#5.3 Manifest, bevarande och återställning|Spec §5.3 Manifest, bevarande och återställning]]. Läs också relevant aktuell post i [[docs/STATUS.md|statusjournalen]] och uppgiftens befintliga plan enligt [[docs/START.md|arbetsgången]].
