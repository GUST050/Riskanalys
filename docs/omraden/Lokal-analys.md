---
typ: omrade
omrade: Lokal-analys
kontext_granskad: 2026-10-24
tags: [riskanalys, omrade, ai-kontext]
---

# Lokal verksamhetsanalys

Gemensamma verksamhetsposter och sårbarhetsprövningar i schema 2 tillämpas uttryckligt per tjänst. Byråns privata resonemang, kontrollbelägg, täckningsprövningar och analysbeslut hålls samman med revisioner och källsummor.

[[docs/START.md|Arbetsgång och kontextnivåer]] · [[docs/omraden/Programflode.md|Programflödet]] · [[docs/kodkarta/omraden/Lokal-analys.md|Alla filkort i området]]

## Minsta kodkontext

Läs uppgiftens ingång och relevanta typer först; tabellen är en läsordning, inte krav att läsa allt. Filkorten leder till originalen. Kontrollera kontrakten mot aktuell kod.

| Fil | Varför |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/analys/tjanst.py.md\|src/riskanalys/analys/tjanst.py]] | Gemensam tjänst för webb och CLI. |
| [[docs/kodkarta/filer/src/riskanalys/analys/modeller.py.md\|src/riskanalys/analys/modeller.py]] | Schema 1/2, gemensamma poster, tillämpningar och täckningsprövningar. |
| [[docs/kodkarta/filer/src/riskanalys/analys/gemensamma_operationer.py.md\|src/riskanalys/analys/gemensamma_operationer.py]] | Typade skrivoperationer genom samma analyslås och CAS. |
| [[docs/kodkarta/filer/src/riskanalys/analys/provning_v2.py.md\|src/riskanalys/analys/provning_v2.py]] | Aktuellt underlag, tjänstetillämpning och uttrycklig risktäckning. |

## Kontrakt att bevara

- Indata: aktuella profil-/bedömningsbindningar, lokala svar och belägg. Utdata: privat analysregister, snapshot och separat beslut.
- Ofullständiga utkast får sparas. Utkast, analysgodkännande, mänsklig sakgranskning och fastställelse är olika tillstånd.
- Behåll revisionsjämförelse (CAS), profil→analys→drift-låsordning och kontroll mot dagens register. Ändrat underlag gör gamla beslut/exporter inaktuella.
- Privat analysfritext ska inte föras in i AI-underlaget. Kontrollreduktion prövas för samma scenario med lokala belägg för utformning, införande och effekt.
- Gemensamt svar innebär inte automatisk tillämpning eller godkännande för alla tjänster. Samlad bekräftelse får inte skriva över en dokumenterad avvikelse.
- Överföring av äldre analys är en uttrycklig handling och överför inga gamla attester. Analysbeslut binds till sakunderlaget, separat från AI-utkastet.

## Fördjupa bara vid behov

| Fil | När den behövs |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/analys/engangssvar.py.md\|src/riskanalys/analys/engangssvar.py]] | Samlad bekräftelse av exakt visade celler; inga automatiska beslut. |
| [[docs/kodkarta/filer/src/riskanalys/analys/overforing.py.md\|src/riskanalys/analys/overforing.py]] | Uttrycklig överföring från schema 1; gamla svar bevaras, attester överförs inte. |
| [[docs/kodkarta/filer/src/riskanalys/analys/gemensam.py.md\|src/riskanalys/analys/gemensam.py]] | Rena läsvyer och innehållssummor. |
| [[docs/kodkarta/filer/src/riskanalys/analys/riktning.py.md\|src/riskanalys/analys/riktning.py]] | Upplysningar per hot/dimension utan en alternativ motor. |
| [[docs/kodkarta/filer/src/riskanalys/analys/lagring.py.md\|src/riskanalys/analys/lagring.py]] | Atomiska snapshots, belägg och revisionskontroll. |

## Berörda områdesgränser

- [[docs/omraden/Riskmotor.md|Riskmotor]] när scenarier eller faktisk reduktion påverkas.
- [[docs/omraden/Intag.md|Intag]] när analysformulär och revision påverkas.
- [[docs/omraden/Granskning.md|Granskning]] när analysbeslut eller aktuellt register prövas.
- [[docs/omraden/Word-och-leverans.md|Word-och-leverans]] när ny analys gör tidigare export inaktuell.

Kontrollera direkta importer och bakåtlänkar för den ändrade filen, och sök även funktions-/fältnamn i koden. Statiska importer visar varken alla runtimekopplingar eller faktisk testtäckning.

## Verifiering

Börja med följande provurval när det passar ändringen; det ersätter inte bredare verifiering av ändrade kontrakt.

```bash
env -u ANTHROPIC_API_KEY .venv312/bin/python -m pytest tester/enhet/test_gemensamma_operationer.py tester/enhet/test_gemensam_provning_v2.py tester/enhet/test_engangssvar.py -q
```

Vid berörd kedja: [[docs/kodkarta/filer/tester/enhet/test_analysgrind.py.md|tester/enhet/test_analysgrind.py]] · [[docs/kodkarta/filer/tester/typfall/test_analys_hela_kedjan.py.md|tester/typfall/test_analys_hela_kedjan.py]].

## Styrande avsnitt

Aktuella tillägg: [[docs/superpowers/specs/2026-10-22-forenklad-riskbedomning-design.md|2026-10-22-forenklad-riskbedomning-design]] · [[docs/superpowers/specs/2026-10-22-engangssvar-och-testtid-design.md|2026-10-22-engangssvar-och-testtid-design]].

[[docs/superpowers/specs/2026-10-08-riskanalys-design.md#6.2 Huvudobjekt|Spec §6.2 Huvudobjekt]] · [[docs/superpowers/specs/2026-10-08-riskanalys-design.md#10 Dokumentstatus och grindar|Spec §10 Dokumentstatus och grindar]] · [[docs/superpowers/specs/2026-10-08-riskanalys-design.md#5.3 Manifest, bevarande och återställning|Spec §5.3 Manifest, bevarande och återställning]]. Läs också relevant aktuell post i [[docs/STATUS.md|statusjournalen]] och uppgiftens befintliga plan enligt [[docs/START.md|arbetsgången]].
