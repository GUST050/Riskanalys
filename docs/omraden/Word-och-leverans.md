---
typ: omrade
omrade: Word-och-leverans
kontext_granskad: 2026-10-24
tags: [riskanalys, omrade, ai-kontext]
---

# Word och leverans

Leverera V10 som tre bundna Word-filer: resultatrapport, analysbilaga A och underlagsbilaga B1. Den redaktionella presentationen har ett exakt flyttregister och bevarar sakunderlag och historisk verifiering.

[[docs/START.md|Arbetsgång och kontextnivåer]] · [[docs/omraden/Programflode.md|Programflödet]] · [[docs/kodkarta/omraden/Word-och-leverans.md|Alla filkort i området]]

## Minsta kodkontext

Läs uppgiftens ingång och relevanta typer först; tabellen är en läsordning, inte krav att läsa allt. Filkorten leder till originalen. Kontrollera kontrakten mot aktuell kod.

| Fil | Varför |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/dokument/rapportvyer_v10.py.md\|src/riskanalys/dokument/rapportvyer_v10.py]] | Tre obligatoriska, disjunkta leveransdelar. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/redaktionspresentation_v10.py.md\|src/riskanalys/dokument/redaktionspresentation_v10.py]] | Aktuell presentationsversion och frysta käll-/flyttbindningar. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/rendering_v10.py.md\|src/riskanalys/dokument/rendering_v10.py]] | Word från verifierad presentation, utan AI- eller motoranrop. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/rapportpaket_v10.py.md\|src/riskanalys/dokument/rapportpaket_v10.py]] | Aktuell återbyggnad och historisk bytekontroll av paketet. |

## Kontrakt att bevara

- Indata: granskat kanoniskt dokument, fryst Presentation och leveransmetadata. Utdata: tre bundna DOCX-filer, underlag och manifest för V10.
- Behåll Leveransmall, bokstavliga spann, ordnade källor, historiska bytekontrakt och atomisk publicering.
- Aktuell export/nedladdning jämför dagens analys och läser bytes under lås. Exportuppdatering får inte starta ny AI-skrivning; historisk verifiering är inte ny aktuell attest.
- V10 levereras som resultatrapport, analysbilaga A och B1; alla tre är obligatoriska. Äldre V8-paket behåller sitt tvådelade format.
- Aktuell presentation är `D-ARB-v10-presentation-2`. Äldre utkast byter inte presentation tyst; ett uttryckligt byte kräver förnyad samlad sakgranskning.

## Fördjupa bara vid behov

| Fil | När den behövs |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/dokument/presentationsval_v10.py.md\|src/riskanalys/dokument/presentationsval_v10.py]] | Uttryckligt presentationsbyte för äldre V10-utkast. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/redaktionell_v10.py.md\|src/riskanalys/dokument/redaktionell_v10.py]] | Redaktionell omformning med bevarade original och källor. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/resultatmodell_v10.py.md\|src/riskanalys/dokument/resultatmodell_v10.py]] | Exakt flyttregister och scenariogrupper. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/leverans_v10.py.md\|src/riskanalys/dokument/leverans_v10.py]] | Fasta mallar och begränsade leveransvärden. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/export.py.md\|src/riskanalys/dokument/export.py]] | Atomisk export och kontroll mot aktuell analys. |

## Berörda områdesgränser

- [[docs/omraden/Rapport.md|Rapport]] när innehåll eller kanonisk struktur ändras.
- [[docs/omraden/Granskning.md|Granskning]] när presentation, attest eller källor ändras.
- [[docs/omraden/Drift-och-lagring.md|Drift-och-lagring]] när manifest/låsning/publicering ändras.

Kontrollera direkta importer och bakåtlänkar för den ändrade filen, och sök även funktions-/fältnamn i koden. Statiska importer visar varken alla runtimekopplingar eller faktisk testtäckning.


### Gemensamt flöde och stil

`arbetsfloden.py` samordnar aktuella utkast och exportuppdatering från sparat AI-svar. Inaktuell bedömning stoppar uppdatering; ändrad lokal analys kan granskas och exporteras på nytt utan AI. Låsens omfattning och historiska paket bevaras. `dokument/wordstil.py` äger även `anpassa_tabeller`, som fortsatt bara anropas för avsedd V10-presentation. `RedaktionV10` finns i `resultatmodell_v10.py`. Renderingsspärren `_SLUTRENDERING` och semantisk paketverifiering är oförändrade.

## Utförd Word-kontroll och återstående acceptans

En avgränsad Word-kontroll av aktuell presentationsversion är utförd på ett separat syntetiskt utkast: 16/30/87 sidor för huvudrapport/A/B1. Första och sista sidan i varje del granskades; filerna öppnades utan reparationsvarning och behöll sina bytes. Fullständig visuell slutkontroll och mänsklig användaracceptans återstår. [Robusthetsplanens §9](../superpowers/plans/2026-10-24-robust-programstruktur.md#9-avslut-och-konkret-återstående-acceptans-2026-10-24) anger underlag, begränsningar och nästa moment.

## Verifiering

Börja med följande provurval när det passar ändringen; det ersätter inte bredare verifiering av ändrade kontrakt.

```bash
env -u ANTHROPIC_API_KEY .venv312/bin/python -m pytest tester/enhet/test_rapportpaket_v10.py tester/enhet/test_presentation_v10.py tester/enhet/test_redaktionell_produkt.py -q
```

Vid berörd kedja: [[docs/kodkarta/filer/tester/enhet/test_rapportvyer.py.md|tester/enhet/test_rapportvyer.py]] · [[docs/kodkarta/filer/tester/intag/test_rapportflode_v8.py.md|tester/intag/test_rapportflode_v8.py]].

## Styrande avsnitt

Aktuella tillägg: [[docs/superpowers/plans/2026-10-24-redaktionell-runda.md|2026-10-24-redaktionell-runda]] · [[docs/superpowers/specs/2026-10-22-resultatrapport-design.md|2026-10-22-resultatrapport-design]].

[[docs/superpowers/specs/2026-10-08-riskanalys-design.md#11.1 V8: två leveransdelar|Spec §11.1 V8: två leveransdelar]] · [[docs/superpowers/specs/2026-10-08-riskanalys-design.md#10.1 V8: gemensam granskning och historik|Spec §10.1 V8: gemensam granskning och historik]]. Läs också relevant aktuell post i [[docs/STATUS.md|statusjournalen]] och uppgiftens befintliga plan enligt [[docs/START.md|arbetsgången]].
