---
typ: omrade
omrade: Granskning
kontext_granskad: 2026-10-24
tags: [riskanalys, omrade, ai-kontext]
---

# Granskning och fastställelse

Pröva dokument och underlag, hantera separat mänsklig sakgranskning och verkställa fastställelse först när kedjans grindar håller.

[[docs/START.md|Arbetsgång och kontextnivåer]] · [[docs/omraden/Programflode.md|Programflödet]] · [[docs/kodkarta/omraden/Granskning.md|Alla filkort i området]]

## Minsta kodkontext

Läs uppgiftens ingång och relevanta typer först; tabellen är en läsordning, inte krav att läsa allt. Filkorten leder till originalen. Kontrollera kontrakten mot aktuell kod.

| Fil | Varför |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/granskning/korning.py.md\|src/riskanalys/granskning/korning.py]] | Bygg/granska/spara dokument, fynd och manifest. |
| [[docs/kodkarta/filer/src/riskanalys/granskning/dokument_v10.py.md\|src/riskanalys/granskning/dokument_v10.py]] | Återbygg V10 och kravkarta från exakt fryst underlag. |
| [[docs/kodkarta/filer/src/riskanalys/faststallelse/grindar.py.md\|src/riskanalys/faststallelse/grindar.py]] | Uttryckliga hinder för fastställelse. |
| [[docs/kodkarta/filer/src/riskanalys/faststallelse/faststall.py.md\|src/riskanalys/faststallelse/faststall.py]] | Kontrollera kedjan och publicera/verifiera låst paket. |

## Kontrakt att bevara

- Indata: bedömning, skrivresultat, fryst analys och aktuella underlag/beslut. Utdata: fynd och granskningsartefakter; fastställelse är ett senare uttryckligt beslut.
- Skilj maskinellt fynd, analysgodkännande, mänsklig sakgranskning, sakkunnigattest och byråns fastställelse.
- Sakgranskning gäller exakt text med insatta namn. Ändrade källor, modell eller analys ska prövas där aktuell fortsättning kräver det.
- Historiska paket ska verifieras mot sina sparade bytes utan ny rendering. Lätta inte på en grind för att få ett syntetiskt prov att passera.

## Nya ingångar efter merge till main

| Fil | Ansvar |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/granskning/dokument_v10.py.md\|src/riskanalys/granskning/dokument_v10.py]] | Återbygg V10, kontrollera källor och kravkarta mot full analys. |
| [[docs/kodkarta/filer/src/riskanalys/faststallelse/resultatgranskning.py.md\|src/riskanalys/faststallelse/resultatgranskning.py]] | Uttrycklig samlad sakgranskning av exakt visade R-avsnitt. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/rapportpaket_v10.py.md\|src/riskanalys/dokument/rapportpaket_v10.py]] | Tre obligatoriska delar och historisk paketverifiering. |

## Fördjupa bara vid behov

| När uppgiften gäller | Läs vidare |
|---|---|
| Mänsklig textgranskning | [[docs/kodkarta/filer/src/riskanalys/faststallelse/sakgranskning.py.md\|src/riskanalys/faststallelse/sakgranskning.py]] · [[docs/kodkarta/filer/src/riskanalys/faststallelse/modeller.py.md\|src/riskanalys/faststallelse/modeller.py]] |
| Aktuell kontra fryst analys eller grupperade fynd | [[docs/kodkarta/filer/src/riskanalys/granskning/analysunderlag.py.md\|src/riskanalys/granskning/analysunderlag.py]] · [[docs/kodkarta/filer/src/riskanalys/granskning/fyndgrupper.py.md\|src/riskanalys/granskning/fyndgrupper.py]] |

## Berörda områdesgränser

- [[docs/omraden/Lokal-analys.md|Lokal-analys]] när register, belägg eller analysbeslut ändras.
- [[docs/omraden/Rapport.md|Rapport]] när innehåll återbyggs eller nya källfält införs.
- [[docs/omraden/Word-och-leverans.md|Word-och-leverans]] när presentation eller V10:s tre rapportdelar ändras.
- [[docs/omraden/Regelverk.md|Regelverk]] när sakkunnigpaket eller kravurval ändras.

Kontrollera direkta importer och bakåtlänkar för den ändrade filen, och sök även funktions-/fältnamn i koden. Statiska importer visar varken alla runtimekopplingar eller faktisk testtäckning.

## Verifiering

Börja med följande provurval när det passar ändringen; det ersätter inte bredare verifiering av ändrade kontrakt.

```bash
env -u ANTHROPIC_API_KEY .venv312/bin/python -m pytest tester/enhet/test_faststall.py tester/enhet/test_granskning_korning.py -q
```

Vid berörd kedja: [[docs/kodkarta/filer/tester/enhet/test_sakgranskning.py.md|tester/enhet/test_sakgranskning.py]] · [[docs/kodkarta/filer/tester/m2/test_m2_kedja.py.md|tester/m2/test_m2_kedja.py]].

Nya kontrakt har särskilda regressioner:

```bash
env -u ANTHROPIC_API_KEY .venv312/bin/python -m pytest tester/enhet/test_resultatgranskning_v10.py tester/enhet/test_redaktionell_produkt.py -q
```

## Styrande avsnitt

Aktuella tillägg: [[docs/superpowers/specs/2026-10-22-resultatrapport-design.md|2026-10-22-resultatrapport-design]] · [[docs/sakkunniggranskning.md|sakkunniggranskning]].

[[docs/superpowers/specs/2026-10-08-riskanalys-design.md#9 Granskning (maskinell)|Spec §9 Granskning (maskinell)]] · [[docs/superpowers/specs/2026-10-08-riskanalys-design.md#10.1 V8: gemensam granskning och historik|Spec §10.1 V8: gemensam granskning och historik]]. Läs också relevant aktuell post i [[docs/STATUS.md|statusjournalen]] och uppgiftens befintliga plan enligt [[docs/START.md|arbetsgången]].
