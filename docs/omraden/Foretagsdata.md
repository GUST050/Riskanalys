---
typ: omrade
omrade: Foretagsdata
kontext_granskad: 2026-10-24
tags: [riskanalys, omrade, ai-kontext]
---

# Företagsdata

Hämta och tolka avgränsade externa företagsuppgifter till daterade förslag. Området bekräftar varken profiluppgifter eller bedömningar.

[[docs/START.md|Arbetsgång och kontextnivåer]] · [[docs/omraden/Programflode.md|Programflödet]] · [[docs/kodkarta/omraden/Foretagsdata.md|Alla filkort i området]]

## Minsta kodkontext

Läs uppgiftens ingång och relevanta typer först; tabellen är en läsordning, inte krav att läsa allt. Filkorten leder till originalen. Kontrollera kontrakten mot aktuell kod.

| Fil | Varför |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/foretagsdata/samlad.py.md\|src/riskanalys/foretagsdata/samlad.py]] | Sammanför SCB och Bolagsverket. |
| [[docs/kodkarta/filer/src/riskanalys/foretagsdata/modeller.py.md\|src/riskanalys/foretagsdata/modeller.py]] | Oföränderliga registerbilder och källmetadata. |
| [[docs/kodkarta/filer/src/riskanalys/foretagsdata/bolagsverket.py.md\|src/riskanalys/foretagsdata/bolagsverket.py]] | Transport och leverantör; token stannar i minnet. |
| [[docs/kodkarta/filer/src/riskanalys/foretagsdata/arsredovisning.py.md\|src/riskanalys/foretagsdata/arsredovisning.py]] | Konservativ tolkning av avgränsad iXBRL. |

## Kontrakt att bevara

- Indata: identifierat företag och leverantörssvar. Utdata: Registerbild/Bolagsverksbild som användaren kan granska.
- Behåll bolag, kontext, period, enhet, skala och tecken. Okänd semantik ger inget omsättningsförslag.
- Rårespons/nycklar ska inte hamna i kartan eller Git. Registerhämtning får inte tyst bekräfta profilfält. Leverantörsfel ska förbli synliga.

## Fördjupa bara vid behov

| När uppgiften gäller | Läs vidare |
|---|---|
| SCB eller lagring av bilder | [[docs/kodkarta/filer/src/riskanalys/foretagsdata/scb.py.md\|src/riskanalys/foretagsdata/scb.py]] · [[docs/kodkarta/filer/src/riskanalys/foretagsdata/lagring.py.md\|src/riskanalys/foretagsdata/lagring.py]] |
| Förslagets väg till profilsvar | [[docs/kodkarta/filer/src/riskanalys/intag/register.py.md\|src/riskanalys/intag/register.py]] · [[docs/kodkarta/filer/src/riskanalys/intag/bolagsverksvy.py.md\|src/riskanalys/intag/bolagsverksvy.py]] |

## Berörda områdesgränser

- [[docs/omraden/Intag.md|Intag]] när förslag visas, väljs eller bekräftas.
- [[docs/omraden/Profil.md|Profil]] när fältens betydelse eller periodtyp ändras.
- [[docs/omraden/Drift-och-lagring.md|Drift-och-lagring]] när privata registerbilder eller aktuell pekare ändras.

Kontrollera direkta importer och bakåtlänkar för den ändrade filen, och sök även funktions-/fältnamn i koden. Statiska importer visar varken alla runtimekopplingar eller faktisk testtäckning.

## Verifiering

Börja med följande provurval när det passar ändringen; det ersätter inte bredare verifiering av ändrade kontrakt.

```bash
env -u ANTHROPIC_API_KEY .venv312/bin/python -m pytest tester/foretagsdata -q
```

Vid berörd kedja: [[docs/kodkarta/filer/tester/intag/test_register.py.md|tester/intag/test_register.py]] · [[docs/kodkarta/filer/tester/intag/test_bolagsverket_intag.py.md|tester/intag/test_bolagsverket_intag.py]].

## Styrande avsnitt

[[docs/superpowers/specs/2026-10-08-riskanalys-design.md#14.4 Registeruppgifter i lokalt intag|Spec §14.4 Registeruppgifter i lokalt intag]] · [[docs/superpowers/specs/2026-10-08-riskanalys-design.md#17 Personuppgifter och säkerhet|Spec §17 Personuppgifter och säkerhet]]. Läs också relevant aktuell post i [[docs/STATUS.md|statusjournalen]] och uppgiftens befintliga plan enligt [[docs/START.md|arbetsgången]].
