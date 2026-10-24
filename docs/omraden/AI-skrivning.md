---
typ: omrade
omrade: AI-skrivning
kontext_granskad: 2026-10-24
tags: [riskanalys, omrade, ai-kontext]
---

# AI-skrivning

Bygg tillåtet faktablad, anropa textleverantör och validera/spara svar. AI får formulera text inom schema och källunderlag.

[[docs/START.md|Arbetsgång och kontextnivåer]] · [[docs/omraden/Programflode.md|Programflödet]] · [[docs/kodkarta/omraden/AI-skrivning.md|Alla filkort i området]]

## Minsta kodkontext

Läs uppgiftens ingång och relevanta typer först; tabellen är en läsordning, inte krav att läsa allt. Filkorten leder till originalen. Kontrollera kontrakten mot aktuell kod.

| Fil | Varför |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/dokument/skrivning.py.md\|src/riskanalys/dokument/skrivning.py]] | Körning, formatval, aktualitetskontroll och sparade försök. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/underlag.py.md\|src/riskanalys/dokument/underlag.py]] | Tillåtelselistat underlag ur profil och motorutfall. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/faktablad.py.md\|src/riskanalys/dokument/faktablad.py]] | Det avgränsade faktablad som textkedjan använder. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/delskrivning.py.md\|src/riskanalys/dokument/delskrivning.py]] | Skrivning per tjänst/del, omförsök och mallreserv. |

## Kontrakt att bevara

- Indata: tillåtna uppgifter och vald skrivversion. Utdata: validerade, versionsbundna skrivresultat med sparad anrops-/svarshistorik.
- Behåll tillåtelselistan och rollplatshållare. Ingen privat analysfritext eller personnamn får slinka in genom promptändring.
- AI bestämmer inte risknivåer och får inte hitta på fakta. Mallreserv och valideringsfel ska vara synliga.
- Automatiska prov använder Testleverantor; starta inte verkliga API-anrop för att prova en prompt. Äldre oskyddad skrivväg förblir stängd för verklig leverantör.

## Nya ingångar efter merge till main

| Fil | Ansvar |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/dokument/skrivversion.py.md\|src/riskanalys/dokument/skrivversion.py]] | AI-skrivformat V8; separat från dokumentformatet. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/rapportversion.py.md\|src/riskanalys/dokument/rapportversion.py]] | V10-dokument från samma sparade skrivresultat. |

## Fördjupa bara vid behov

| När uppgiften gäller | Läs vidare |
|---|---|
| Prompt eller svarsschema | [[docs/kodkarta/filer/src/riskanalys/dokument/promptar/delar.py.md\|src/riskanalys/dokument/promptar/delar.py]] · [[docs/kodkarta/filer/src/riskanalys/dokument/aischema.py.md\|src/riskanalys/dokument/aischema.py]] |
| Svarsprövning eller leverantörstransport | [[docs/kodkarta/filer/src/riskanalys/dokument/delvalidering.py.md\|src/riskanalys/dokument/delvalidering.py]] · [[docs/kodkarta/filer/src/riskanalys/dokument/claude.py.md\|src/riskanalys/dokument/claude.py]] |

## Berörda områdesgränser

- [[docs/omraden/Regelverk.md|Regelverk]] när tillåtna fält eller referenser ändras.
- [[docs/omraden/Rapport.md|Rapport]] när skrivresultatets schema/format ändras.
- [[docs/omraden/Granskning.md|Granskning]] när valideringsregler eller låst text ändras.

Kontrollera direkta importer och bakåtlänkar för den ändrade filen, och sök även funktions-/fältnamn i koden. Statiska importer visar varken alla runtimekopplingar eller faktisk testtäckning.

## Verifiering

Börja med följande provurval när det passar ändringen; det ersätter inte bredare verifiering av ändrade kontrakt.

```bash
env -u ANTHROPIC_API_KEY .venv312/bin/python -m pytest tester/intag/test_skyddad_begaran.py tester/enhet/test_delvalidering.py -q
```

Vid berörd kedja: [[docs/kodkarta/filer/tester/enhet/test_skrivformat_v8.py.md|tester/enhet/test_skrivformat_v8.py]] · [[docs/kodkarta/filer/tester/enhet/test_aldre_skrivvag.py.md|tester/enhet/test_aldre_skrivvag.py]].

## Styrande avsnitt

[[docs/superpowers/specs/2026-10-08-riskanalys-design.md#8.4 Skrivning av hela dokumentet från faktablad|Spec §8.4 Skrivning av hela dokumentet från faktablad]] · [[docs/superpowers/specs/2026-10-08-riskanalys-design.md#8.5 V8: reproducerbara produktionsvägar|Spec §8.5 V8: reproducerbara produktionsvägar]]. Läs också relevant aktuell post i [[docs/STATUS.md|statusjournalen]] och uppgiftens befintliga plan enligt [[docs/START.md|arbetsgången]].
