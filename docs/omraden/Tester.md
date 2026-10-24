---
typ: omrade
omrade: Tester
kontext_granskad: 2026-10-24
tags: [riskanalys, omrade, ai-kontext]
---

# Tester och syntetiska underlag

Välj prov efter ändringens kontrakt och berörda konsumenter. Testernas mappar är verifieringsnivåer, inte separata produktområden.

[[docs/START.md|Arbetsgång och kontextnivåer]] · [[docs/omraden/Programflode.md|Programflödet]] · [[docs/kodkarta/omraden/Tester.md|Alla filkort i området]]

## Minsta kodkontext

Läs uppgiftens ingång och relevanta typer först; tabellen är en läsordning, inte krav att läsa allt. Filkorten leder till originalen. Kontrollera kontrakten mot aktuell kod.

| Fil | Varför |
|---|---|
| [[docs/kodkarta/filer/tester/conftest.py.md\|tester/conftest.py]] | Gemensam regelbas, syntetiska underlag och fixturer. |
| [[docs/kodkarta/filer/tester/enhet/conftest.py.md\|tester/enhet/conftest.py]] | Enhetsprovets gemensamma fixturer. |
| [[docs/kodkarta/filer/tester/intag/conftest.py.md\|tester/intag/conftest.py]] | Intagets fixturer och lokala kedja. |
| [[docs/kodkarta/filer/pyproject.toml.md\|pyproject.toml]] | Pytest-konfiguration och bortval av live. |

## Kontrakt att bevara

- Indata: syntetiska profiler, testleverantör och frysta underlag. Utdata: reproducerbar kontroll av ett namngivet beteende.
- Insamlade testfall är inte passerade testfall. Redovisa kommando, exitkod, urval och kvarstående fel separat.
- Behåll fryst v0-bas och äldre formatbytes. Ändra inte en fixture enbart för att dölja en regression.
- Automatiska prov använder inga riktiga leverantörsanrop. Följ tabellen i AGENTS regel 6 för val av kontroll; tekniskt grönt är inte rättslig eller mänsklig attest.

## Nya ingångar efter merge till main

| Fil | Ansvar |
|---|---|
| [[docs/kodkarta/filer/scripts/testa.py.md\|scripts/testa.py]] | Snabb-, analys- och fullprofil med collection/JUnit och oförändrat snapshot. |
| [[docs/kodkarta/filer/tester/testprofiler.json.md\|tester/testprofiler.json]] | De exakta avgränsade provurvalen. |
| [[docs/kodkarta/filer/scripts/testtid.py.md\|scripts/testtid.py]] | Läs befintlig JUnit utan att starta tester. |
| [[docs/kodkarta/filer/tester/fixturer/redaktionell_v10_d8a91a1.json.gz.md\|tester/fixturer/redaktionell_v10_d8a91a1.json.gz]] | Komprimerat, fryst underlag för den redaktionella V10-presentationen. |

## Berörda områdesgränser

- [[docs/omraden/Intag.md|Intag]] när formulär, svar eller webb ändras.
- [[docs/omraden/Riskmotor.md|Riskmotor]] när beräkning eller modellbindning ändras.
- [[docs/omraden/Rapport.md|Rapport]] när innehåll/format ändras.
- [[docs/omraden/Granskning.md|Granskning]] när kedjan eller grindar ändras.

Kontrollera direkta importer och bakåtlänkar för den ändrade filen, och sök även funktions-/fältnamn i koden. Statiska importer visar varken alla runtimekopplingar eller faktisk testtäckning.


### Låst miljö och områdesprofiler

`uv.lock`/`.python-version` och CI-konfigurationen binds in i testverktygets snapshot. `scripts/testa.py` läser explicita profiler ur JSON och redovisar urvalsorsak, paketversioner, tidsbudget och multiplicitet i collection/JUnit. Områdesprofiler och kommandon finns i [testguiden](../testning.md). Nya gränsprov: `test_skrivkonfiguration`, `test_utkastflode`, `test_analysandringar`, `test_modulgranser` samt `typfall/test_aterstallning_v10`. Fullprofilen är fortsatt hela ordinarie icke-live-sviten.

## Verifiering

Använd projektets Python 3.12-miljö enligt [[docs/testning.md|testguiden]]. Kartgeneratorn använder enbart standardbiblioteket och kan köras direkt med `python3.12`.

Välj riktade prov från produktområdets guide och lägg till konsument-/kedjeprov för ändrade kontrakt. Vid kontroll av hela testurvalet kan du samla fallen utan att köra dem:

```bash
env -u ANTHROPIC_API_KEY .venv312/bin/python -m pytest --collect-only -q
```

AGENTS regel 6 kräver berörda prov och snabbprofil före arbetscommit. Full icke-live-svit krävs vid de kontrollpunkter som tabellen i AGENTS anger, alltid på det exakta snapshotet. Ändrat testverktyg eller ändrade profiler räknas som delad kritisk logik. Testinsamling är inte en passerad körning. Kart- och länkkontroll verifierar denna navigering; den ersätter inte produktens fullsvit.

Vid berörd kedja: [[docs/kodkarta/filer/tester/typfall/test_analys_hela_kedjan.py.md|tester/typfall/test_analys_hela_kedjan.py]] · [[docs/kodkarta/filer/tester/m2/test_m2_kedja.py.md|tester/m2/test_m2_kedja.py]].

## Styrande avsnitt

Aktuella tillägg: [[docs/testning.md|testning]].

[[docs/superpowers/specs/2026-10-08-riskanalys-design.md#16 Kvalitetssäkring|Spec §16 Kvalitetssäkring]] · [[docs/superpowers/specs/2026-10-08-riskanalys-design.md#16.2 Acceptansprov|Spec §16.2 Acceptansprov]]. Läs också relevant aktuell post i [[docs/STATUS.md|statusjournalen]] och uppgiftens befintliga plan enligt [[docs/START.md|arbetsgången]].
