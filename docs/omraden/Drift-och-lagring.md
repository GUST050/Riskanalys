---
typ: omrade
omrade: Drift-och-lagring
kontext_granskad: 2026-10-24
tags: [riskanalys, omrade, ai-kontext]
---

# Drift och lagring

Privat datamapp, validerad filläsning, manifest och modellidentitet. Bevara koppling mellan körning, underlag och historik.

[[docs/START.md|Arbetsgång och kontextnivåer]] · [[docs/omraden/Programflode.md|Programflödet]] · [[docs/kodkarta/omraden/Drift-och-lagring.md|Alla filkort i området]]

## Minsta kodkontext

Läs uppgiftens ingång och relevanta typer först; tabellen är en läsordning, inte krav att läsa allt. Filkorten leder till originalen. Kontrollera kontrakten mot aktuell kod.

| Fil | Varför |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/lagring/datamapp.py.md\|src/riskanalys/lagring/datamapp.py]] | Håll byrådata utanför repot. |
| [[docs/kodkarta/filer/src/riskanalys/lagring/manifest.py.md\|src/riskanalys/lagring/manifest.py]] | Manifest, kontrollsummor och programproveniens. |
| [[docs/kodkarta/filer/src/riskanalys/lagring/korningar.py.md\|src/riskanalys/lagring/korningar.py]] | Körningsmappar och val av senaste körning. |
| [[docs/kodkarta/filer/src/riskanalys/drift/modellidentitet.py.md\|src/riskanalys/drift/modellidentitet.py]] | Smal innehållsbunden identitet för riskmodellen. |

## Kontrakt att bevara

- Indata: validerade artefakter och metadata. Utdata: sparade, kontrollerbara körningar och bindningar.
- Kontrollsummor visar integritet men återskapar inga förlorade filer. Behåll privata datamappar, atomisk publicering och tydliga återställningsfel.
- Modellbindning omfattar riskberäkningens identitet; presentationsändringar ska inte vidga den av misstag.
- Profil-/analys-/driftlås är kedjekontrakt. Förändra inte låsordning eller aktuella pekare utan att läsa alla berörda skrivare.

## Nya ingångar efter merge till main

| Fil | Ansvar |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/profil/forandringar.py.md\|src/riskanalys/profil/forandringar.py]] | Förändringslås, profilrevision och historiklås. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/rapportpaket_v10.py.md\|src/riskanalys/dokument/rapportpaket_v10.py]] | Frysta presentationskällor och historisk bytekontroll. |

## Fördjupa bara vid behov

| När uppgiften gäller | Läs vidare |
|---|---|
| YAML/JSON-läsning eller modellriskunderlag | [[docs/kodkarta/filer/src/riskanalys/lagring/yamlfil.py.md\|src/riskanalys/lagring/yamlfil.py]] · [[docs/kodkarta/filer/src/riskanalys/drift/modellrisk.py.md\|src/riskanalys/drift/modellrisk.py]] |
| Atomisk profil-/analyssparning | [[docs/kodkarta/filer/src/riskanalys/profil/lagring.py.md\|src/riskanalys/profil/lagring.py]] · [[docs/kodkarta/filer/src/riskanalys/analys/lagring.py.md\|src/riskanalys/analys/lagring.py]] |

## Berörda områdesgränser

- [[docs/omraden/Profil.md|Profil]] när profilrevision eller snapshot ändras.
- [[docs/omraden/Lokal-analys.md|Lokal-analys]] när CAS/låsning eller belägg ändras.
- [[docs/omraden/Granskning.md|Granskning]] när paketens historik/bindning ändras.
- [[docs/omraden/Word-och-leverans.md|Word-och-leverans]] när manifest eller atomisk leverans ändras.

Kontrollera direkta importer och bakåtlänkar för den ändrade filen, och sök även funktions-/fältnamn i koden. Statiska importer visar varken alla runtimekopplingar eller faktisk testtäckning.

## Verifiering

Börja med följande provurval när det passar ändringen; det ersätter inte bredare verifiering av ändrade kontrakt.

```bash
env -u ANTHROPIC_API_KEY .venv312/bin/python -m pytest tester/enhet/test_manifest.py tester/enhet/test_lagring_grund.py -q
```

Vid berörd kedja: [[docs/kodkarta/filer/tester/enhet/test_bedomningsbindning.py.md|tester/enhet/test_bedomningsbindning.py]] · [[docs/kodkarta/filer/tester/enhet/test_korningar.py.md|tester/enhet/test_korningar.py]].

## Styrande avsnitt

[[docs/superpowers/specs/2026-10-08-riskanalys-design.md#5.2 Datamapp och gränssnitt|Spec §5.2 Datamapp och gränssnitt]] · [[docs/superpowers/specs/2026-10-08-riskanalys-design.md#5.3 Manifest, bevarande och återställning|Spec §5.3 Manifest, bevarande och återställning]] · [[docs/superpowers/specs/2026-10-08-riskanalys-design.md#13 Drift och livscykel|Spec §13 Drift och livscykel]]. Läs också relevant aktuell post i [[docs/STATUS.md|statusjournalen]] och uppgiftens befintliga plan enligt [[docs/START.md|arbetsgången]].
