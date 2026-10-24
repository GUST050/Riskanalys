---
typ: omrade
omrade: Profil
kontext_granskad: 2026-10-24
tags: [riskanalys, omrade, ai-kontext]
---

# Byråprofil

Typade, bekräftade verksamhetsuppgifter. Området äger profilens struktur, värdetolkning och atomiska sparning; hämtning av registerförslag hör till Företagsdata.

[[docs/START.md|Arbetsgång och kontextnivåer]] · [[docs/omraden/Programflode.md|Programflödet]] · [[docs/kodkarta/omraden/Profil.md|Alla filkort i området]]

## Minsta kodkontext

Läs uppgiftens ingång och relevanta typer först; tabellen är en läsordning, inte krav att läsa allt. Filkorten leder till originalen. Kontrollera kontrakten mot aktuell kod.

| Fil | Varför |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/profil/modeller.py.md\|src/riskanalys/profil/modeller.py]] | Profil, Byra, Uppgift och Period. |
| [[docs/kodkarta/filer/src/riskanalys/profil/hantering.py.md\|src/riskanalys/profil/hantering.py]] | Bekräftelse, värdetolkning och kritiska fält. |
| [[docs/kodkarta/filer/src/riskanalys/profil/lagring.py.md\|src/riskanalys/profil/lagring.py]] | Profilrevision och exakt profilsnapshot. |

## Kontrakt att bevara

- Indata: typat värde med status, källa, datum och eventuell period. Utdata: validerad Profil och sparade profilbytes.
- Saknad/okänd uppgift är inte ett bekräftat nollvärde. Behåll skillnaden mellan uppgiftens värde, status och underlag.
- En bedömning måste beräknas från samma profilbytes som dess profilkopia. Samtidig sparning får göra bedömningen inaktuell men inte blanda underlagen.

## Nya ingångar efter merge till main

| Fil | Ansvar |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/profil/forandringar.py.md\|src/riskanalys/profil/forandringar.py]] | Gemensam transaktion för webb/CLI med profil-CAS och historiklås. |
| [[docs/kodkarta/filer/src/riskanalys/profil/planering.py.md\|src/riskanalys/profil/planering.py]] | Tjänsteplaner och utvärdering av förändringar. |
| [[docs/kodkarta/filer/src/riskanalys/profil/planlivslopp.py.md\|src/riskanalys/profil/planlivslopp.py]] | Införda och återkallade planer sparas atomiskt. |
| [[docs/kodkarta/filer/src/riskanalys/profil/planval.py.md\|src/riskanalys/profil/planval.py]] | Uttryckligt, skrivfritt införandeval; ingen implicit första kandidat. |

## Fördjupa bara vid behov

| När uppgiften gäller | Läs vidare |
|---|---|
| Omfattning eller visning av lokala svar | [[docs/kodkarta/filer/src/riskanalys/profil/omfattning.py.md\|src/riskanalys/profil/omfattning.py]] · [[docs/kodkarta/filer/src/riskanalys/profil/text.py.md\|src/riskanalys/profil/text.py]] |
| Profiländringens följder för bedömningen | [[docs/kodkarta/filer/src/riskanalys/bedomning/korning.py.md\|src/riskanalys/bedomning/korning.py]] · [[docs/kodkarta/filer/src/riskanalys/intag/svar.py.md\|src/riskanalys/intag/svar.py]] |

## Berörda områdesgränser

- [[docs/omraden/Intag.md|Intag]] när svar, formulär eller ogiltigförklaring påverkas.
- [[docs/omraden/Riskmotor.md|Riskmotor]] när beräkningsfält eller snapshots ändras.
- [[docs/omraden/Drift-och-lagring.md|Drift-och-lagring]] när sparning, låsning eller kontrollsummor ändras.

Kontrollera direkta importer och bakåtlänkar för den ändrade filen, och sök även funktions-/fältnamn i koden. Statiska importer visar varken alla runtimekopplingar eller faktisk testtäckning.

## Verifiering

Börja med följande provurval när det passar ändringen; det ersätter inte bredare verifiering av ändrade kontrakt.

```bash
env -u ANTHROPIC_API_KEY .venv312/bin/python -m pytest tester/enhet/test_profil.py tester/enhet/test_bedomning_korning.py -q
```

Vid berörd kedja: [[docs/kodkarta/filer/tester/enhet/test_bedomningsbindning.py.md|tester/enhet/test_bedomningsbindning.py]] · [[docs/kodkarta/filer/tester/intag/test_lagring.py.md|tester/intag/test_lagring.py]].

Nya kontrakt har särskilda regressioner:

```bash
env -u ANTHROPIC_API_KEY .venv312/bin/python -m pytest tester/enhet/test_planens_livslopp.py tester/enhet/test_inforandeval.py -q
```

## Styrande avsnitt

Aktuella tillägg: [[docs/superpowers/plans/2026-10-22-planaterkallelse-och-inforandeval-plan.md|2026-10-22-planaterkallelse-och-inforandeval-plan]].

[[docs/superpowers/specs/2026-10-08-riskanalys-design.md#6.2 Huvudobjekt|Spec §6.2 Huvudobjekt]] · [[docs/superpowers/specs/2026-10-08-riskanalys-design.md#5.3 Manifest, bevarande och återställning|Spec §5.3 Manifest, bevarande och återställning]]. Läs också relevant aktuell post i [[docs/STATUS.md|statusjournalen]] och uppgiftens befintliga plan enligt [[docs/START.md|arbetsgången]].
