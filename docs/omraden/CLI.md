---
typ: omrade
omrade: CLI
kontext_granskad: 2026-10-24
tags: [riskanalys, omrade, ai-kontext]
---

# Kommandorad och start

Programmets start och tunna kommandon till samma kärna som lokala formulär. Välj det kommando som uppgiften gäller innan andra moduler läses.

[[docs/START.md|Arbetsgång och kontextnivåer]] · [[docs/omraden/Programflode.md|Programflödet]] · [[docs/kodkarta/omraden/CLI.md|Alla filkort i området]]

## Minsta kodkontext

Läs uppgiftens ingång och relevanta typer först; tabellen är en läsordning, inte krav att läsa allt. Filkorten leder till originalen. Kontrollera kontrakten mot aktuell kod.

| Fil | Varför |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/cli.py.md\|src/riskanalys/cli.py]] | Registrering av kommandon och gemensam start. |
| [[docs/kodkarta/filer/src/riskanalys/fel.py.md\|src/riskanalys/fel.py]] | Användaråtgärdbara fel. |
| [[docs/kodkarta/filer/src/riskanalys/kommandon/bedom_kommando.py.md\|src/riskanalys/kommandon/bedom_kommando.py]] | Exempel: adapter till bedömningskedjan. |
| [[docs/kodkarta/filer/src/riskanalys/nyckelfil.py.md\|src/riskanalys/nyckelfil.py]] | Lokal nyckelläsning; läs kod, aldrig hemliga värden. |

## Kontrakt att bevara

- Indata: CLI-argument, konfiguration och valt underlag. Utdata: anrop av kärnoperation och begripligt resultat/fel.
- Beräknings- och grindlogik ska inte kopieras till kommandolagret. Webb och CLI behöver samma betydelse för samma operation.
- Skriv inte nycklar eller riktiga byråuppgifter till logg, dokumentation eller Git. Framgång i CLI får inte likställas med mänsklig attest.

## Nya ingångar efter merge till main

| Fil | Ansvar |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/kommandon/gemensam_analys.py.md\|src/riskanalys/kommandon/gemensam_analys.py]] | Typade schema-2-operationer; inga importerade attester. |
| [[docs/kodkarta/filer/src/riskanalys/kommandon/profil_kommando.py.md\|src/riskanalys/kommandon/profil_kommando.py]] | Planering och uttryckliga förändrings-/införandeval. |
| [[docs/kodkarta/filer/src/riskanalys/kommandon/sakgranska_kommando.py.md\|src/riskanalys/kommandon/sakgranska_kommando.py]] | Samlad granskning och formatbundna presentationsval. |

## Fördjupa bara vid behov

| När uppgiften gäller | Läs vidare |
|---|---|
| Skrivning eller export | [[docs/kodkarta/filer/src/riskanalys/kommandon/skriv_kommando.py.md\|src/riskanalys/kommandon/skriv_kommando.py]] · [[docs/kodkarta/filer/src/riskanalys/kommandon/exportera_kommando.py.md\|src/riskanalys/kommandon/exportera_kommando.py]] |
| Analys eller fastställelse | [[docs/kodkarta/filer/src/riskanalys/kommandon/analys_kommando.py.md\|src/riskanalys/kommandon/analys_kommando.py]] · [[docs/kodkarta/filer/src/riskanalys/kommandon/faststall_kommando.py.md\|src/riskanalys/kommandon/faststall_kommando.py]] |

## Berörda områdesgränser

- [[docs/omraden/Riskmotor.md|Riskmotor]] när bedom-kommandot eller modellbindning påverkas.
- [[docs/omraden/AI-skrivning.md|AI-skrivning]] när skriv-kommandot påverkas.
- [[docs/omraden/Lokal-analys.md|Lokal-analys]] när analys-kommandot påverkas.
- [[docs/omraden/Granskning.md|Granskning]] när granska/faststall/sakgranska påverkas.

Kontrollera direkta importer och bakåtlänkar för den ändrade filen, och sök även funktions-/fältnamn i koden. Statiska importer visar varken alla runtimekopplingar eller faktisk testtäckning.


### Delade ingångar

`skriv_kommando.valj_leverantor` är en tunn kompatibel mappning till `konfiguration.skapa_textleverantor`. Analyskommandot bygger samma typade block-/scenariokommandon som webb och lämnar revision och visad summa för ny kontroll under tjänstens lås. CLI:s separata bedömning, skrivning, granskning och export fortsätter vara separata operationer; ingen lågkommandooperation startar hela utkastkedjan.

## Verifiering

Börja med följande provurval när det passar ändringen; det ersätter inte bredare verifiering av ändrade kontrakt.

```bash
env -u ANTHROPIC_API_KEY .venv312/bin/python -m pytest tester/enhet/test_cli.py tester/enhet/test_nyckelfil.py -q
```

Vid berörd kedja: [[docs/kodkarta/filer/tester/enhet/test_skriv_kommando.py.md|tester/enhet/test_skriv_kommando.py]] · [[docs/kodkarta/filer/tester/enhet/test_exportera_kommando.py.md|tester/enhet/test_exportera_kommando.py]].

## Styrande avsnitt

[[docs/superpowers/specs/2026-10-08-riskanalys-design.md#12 Kommandon|Spec §12 Kommandon]] · [[docs/superpowers/specs/2026-10-08-riskanalys-design.md#14 Användarflöde|Spec §14 Användarflöde]]. Läs också relevant aktuell post i [[docs/STATUS.md|statusjournalen]] och uppgiftens befintliga plan enligt [[docs/START.md|arbetsgången]].
