---
typ: omrade
omrade: Projekt
kontext_granskad: 2026-10-24
tags: [riskanalys, omrade, ai-kontext]
---

# Projektets dokumentation

Gemensamma arbetsregler, aktuell specifikation, planer och status. Obsidian-sidorna hjälper läsningen men är ingen parallell beslutsjournal.

[[docs/START.md|Arbetsgång och kontextnivåer]] · [[docs/omraden/Programflode.md|Programflödet]] · [[docs/kodkarta/omraden/Projekt.md|Alla filkort i området]]

## Minsta kodkontext

Läs uppgiftens ingång och relevanta typer först; tabellen är en läsordning, inte krav att läsa allt. Filkorten leder till originalen. Kontrollera kontrakten mot aktuell kod.

| Fil | Varför |
|---|---|
| [[docs/kodkarta/filer/AGENTS.md.md\|AGENTS.md]] | Gemensam ingång och prioriterad kontextläsning. |
| [[docs/kodkarta/filer/CLAUDE.md.md\|CLAUDE.md]] | Tunn Claude-ingång till samma regler. |
| [[docs/kodkarta/filer/docs/START.md.md\|docs/START.md]] | Uppgiftsrouting, kontextnivåer och arbetsöverlämning. |
| [[docs/kodkarta/filer/docs/research/verktyg/bygg_obsidiankarta.py.md\|docs/research/verktyg/bygg_obsidiankarta.py]] | Bygger metadata från det aktuella Git-urvalet. |

## Kontrakt att bevara

- Indata: aktuell kod, beslut och faktiskt uppmätt verifiering. Utdata: korta områdesguider och spårbara uppdateringar i befintlig plan/status.
- AGENTS anger arbetssätt; spec/plan anger avsett beteende; koden visar implementationen; prov visar endast det som faktiskt körts. Redovisa motsägelser.
- Håll CLAUDE tunt och områdeskontexten selektiv. Läs inte hela statusjournalen eller programkartan vid varje uppgift.
- Ändra handskrivna guider vid ansvar/kontraktsändring och bygg om filkorten. En ny fil kan grupperas automatiskt, men ett nytt produktområde behöver även en mänskligt begriplig guide/routning.

## Nya ingångar efter merge till main

| Fil | Ansvar |
|---|---|
| [[docs/kodkarta/filer/docs/kravstod.md.md\|docs/kravstod.md]] | Läsordning för kravstöd och verksamhetsanpassning. |
| [[docs/kodkarta/filer/docs/sakkunniggranskning.md.md\|docs/sakkunniggranskning.md]] | Guide till expertunderlag och verklig granskning. |
| [[docs/kodkarta/filer/docs/testning.md.md\|docs/testning.md]] | Python 3.12, testprofiler och verifieringsvillkor. |

## Berörda områdesgränser

[Plan för robust programstruktur](../superpowers/plans/2026-10-24-robust-programstruktur.md) samordnar nästa steg: aktuell verifieringsbaslinje, reproducerbar miljö, tydliga modulkontrakt och återställning. Den genomförs på arbetsgrenen; faktisk kod och verifiering redovisas i planens §8 och områdesguiderna.

Planens §3.1–3.5 anger konkret vilka programfiler som behålls, fem föreslagna sammanslagningar (S4 utgick efter granskning) och tre nya filer. Det tekniska genomförandet har 247 programfiler, från 249 genom fem sammanslagningar och tre nya filer. S1–S3 och S5 är en fristående etapp; varje borttagen fil kräver ändrad fillista i `metodbeslut.yaml`. Filkort och områdesguider följer de införda gränserna.

- [[docs/omraden/Tester.md|Tester]] när testkommandon eller evidenskrav dokumenteras.
- [[docs/omraden/CLI.md|CLI]] när lokala verktyg/startinstruktioner ändras.

Kontrollera direkta importer och bakåtlänkar för den ändrade filen, och sök även funktions-/fältnamn i koden. Statiska importer visar varken alla runtimekopplingar eller faktisk testtäckning.

## Verifiering

```bash
python3.12 docs/research/verktyg/bygg_obsidiankarta.py --check
git diff --check
```

## Styrande avsnitt

[[docs/superpowers/specs/2026-10-08-riskanalys-design.md#5 Arkitektur|Spec §5 Arkitektur]] · [[docs/superpowers/specs/2026-10-08-riskanalys-design.md#20 Öppna frågor|Spec §20 Öppna frågor]]. Läs också relevant aktuell post i [[docs/STATUS.md|statusjournalen]] och uppgiftens befintliga plan enligt [[docs/START.md|arbetsgången]].
