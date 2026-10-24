---
typ: omrade
omrade: Regelverk
kontext_granskad: 2026-10-24
tags: [riskanalys, omrade, ai-kontext]
---

# Regelverk och regeldata

Källbunden regelbas: YAML-kataloger, typade modeller, validering och datum-/länsstyrt urval. AI-formuleringar och lokala bekräftelser hör till andra områden.

[[docs/START.md|Arbetsgång och kontextnivåer]] · [[docs/omraden/Programflode.md|Programflödet]] · [[docs/kodkarta/omraden/Regelverk.md|Alla filkort i området]]

## Minsta kodkontext

Läs uppgiftens ingång och relevanta typer först; tabellen är en läsordning, inte krav att läsa allt. Filkorten leder till originalen. Kontrollera kontrakten mot aktuell kod.

| Fil | Varför |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/regelverk/laddning.py.md\|src/riskanalys/regelverk/laddning.py]] | Laddning och kontrollsumma av regelbasen. |
| [[docs/kodkarta/filer/src/riskanalys/regelverk/modeller.py.md\|src/riskanalys/regelverk/modeller.py]] | Regelbasens typade schema. |
| [[docs/kodkarta/filer/src/riskanalys/regelverk/urval.py.md\|src/riskanalys/regelverk/urval.py]] | Krav och lydelser för valt datum, län och regelpaket. |
| [[docs/kodkarta/filer/src/riskanalys/regelverk/villkor.py.md\|src/riskanalys/regelverk/villkor.py]] | Utvärdering av typade villkor. |

## Kontrakt att bevara

- Indata: regelbasfiler och urvalsparametrar. Utdata: validerad Regelbas och Urval med källor och kontrollsummor.
- Varje regeländring behöver källa/grund; metodval hålls synliga. Ingen eval eller implicit dagens-datumlogik.
- Sakkunnigstatus får inte ändras till verifierad utan verklig granskning. Frågetäckning är inte uppfyllda krav; nya fält kräver sammanhängande katalogreferenser.

## Nya ingångar efter merge till main

| Fil | Ansvar |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/regelverk/metodbeslut.py.md\|src/riskanalys/regelverk/metodbeslut.py]] | Bind metodförslag till sakobjekt och faktiskt kodgenomförande. |
| [[docs/kodkarta/filer/regelbas/beslutstabeller/metodbeslut.yaml.md\|regelbas/beslutstabeller/metodbeslut.yaml]] | D1–D9 och D-LAGRE med källor, begränsningar och granskningsstatus. |
| [[docs/kodkarta/filer/regelbas/kataloger/lagre_risk.yaml.md\|regelbas/kataloger/lagre_risk.yaml]] | Källbundna lägre-risk-indikatorer. |
| [[docs/kodkarta/filer/src/riskanalys/regelverk/lasversion.py.md\|src/riskanalys/regelverk/lasversion.py]] | Litet läspaket med byteidentiska filer ur verifierat expertunderlag. |

## Fördjupa bara vid behov

| När uppgiften gäller | Läs vidare |
|---|---|
| Intagsfält eller tillåtna AI-uppgifter | [[docs/kodkarta/filer/src/riskanalys/regelverk/intagskontrakt.py.md\|src/riskanalys/regelverk/intagskontrakt.py]] · [[docs/kodkarta/filer/src/riskanalys/dokument/underlag.py.md\|src/riskanalys/dokument/underlag.py]] |
| Scenariokatalog eller sakkunnigpaket | [[docs/kodkarta/filer/src/riskanalys/regelverk/validering_scenario.py.md\|src/riskanalys/regelverk/validering_scenario.py]] · [[docs/kodkarta/filer/src/riskanalys/regelverk/sakkunnig.py.md\|src/riskanalys/regelverk/sakkunnig.py]] |

## Berörda områdesgränser

- [[docs/omraden/Riskmotor.md|Riskmotor]] när kataloger, skalor, hot eller kontroller ändras.
- [[docs/omraden/Intag.md|Intag]] när fält, frågor eller tillämplighet ändras.
- [[docs/omraden/AI-skrivning.md|AI-skrivning]] när tillåtelselista eller underlag ändras.
- [[docs/omraden/Granskning.md|Granskning]] när krav, källor eller sakkunnigprövning påverkas.

Kontrollera direkta importer och bakåtlänkar för den ändrade filen, och sök även funktions-/fältnamn i koden. Statiska importer visar varken alla runtimekopplingar eller faktisk testtäckning.

## Verifiering

Börja med följande provurval när det passar ändringen; det ersätter inte bredare verifiering av ändrade kontrakt.

```bash
env -u ANTHROPIC_API_KEY .venv312/bin/python -m pytest tester/regelkontrakt/test_urval.py tester/regelkontrakt/test_validering_regelbas.py -q
```

Vid berörd kedja: [[docs/kodkarta/filer/tester/regelkontrakt/test_scenariokatalog_v2.py.md|tester/regelkontrakt/test_scenariokatalog_v2.py]] · [[docs/kodkarta/filer/tester/m2/test_sakkunnigpaket.py.md|tester/m2/test_sakkunnigpaket.py]]. Vid katalog-/schemaändring: utöka till hela `tester/regelkontrakt/`.

Nya kontrakt har särskilda regressioner:

```bash
env -u ANTHROPIC_API_KEY .venv312/bin/python -m pytest tester/regelkontrakt/test_metodbeslut_d.py tester/regelkontrakt/test_katalogkomplettering_b.py tester/regelkontrakt/test_hotnivaer_c.py -q
```

## Styrande avsnitt

Aktuella tillägg: [[docs/superpowers/plans/2026-10-23-regelbas-steg-b.md|2026-10-23-regelbas-steg-b]] · [[docs/superpowers/plans/2026-10-23-regelbas-c-rapport-d-e.md|2026-10-23-regelbas-c-rapport-d-e]] · [[docs/superpowers/plans/2026-10-23-metodbeslut-d.md|2026-10-23-metodbeslut-d]].

[[docs/superpowers/specs/2026-10-08-riskanalys-design.md#6.3 Villkorsformat|Spec §6.3 Villkorsformat]] · [[docs/superpowers/specs/2026-10-08-riskanalys-design.md#6.4 Datumstyrning|Spec §6.4 Datumstyrning]] · [[docs/superpowers/specs/2026-10-08-riskanalys-design.md#16.1 Paragrafkarta|Spec §16.1 Paragrafkarta]]. Läs också relevant aktuell post i [[docs/STATUS.md|statusjournalen]] och uppgiftens befintliga plan enligt [[docs/START.md|arbetsgången]].
