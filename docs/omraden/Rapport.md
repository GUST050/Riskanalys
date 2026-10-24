---
typ: omrade
omrade: Rapport
kontext_granskad: 2026-10-24
tags: [riskanalys, omrade, ai-kontext]
---

# Rapportens innehåll

Bygg V10-resultatrapporten från frysta sakuppgifter, full V8-analys och samma sparade skrivsvar. Huvudrapport, analysbilaga A och underlagsbilaga B1 har spårbara källor; Word-presentation och leverans är egna steg.

[[docs/START.md|Arbetsgång och kontextnivåer]] · [[docs/omraden/Programflode.md|Programflödet]] · [[docs/kodkarta/omraden/Rapport.md|Alla filkort i området]]

## Minsta kodkontext

Läs uppgiftens ingång och relevanta typer först; tabellen är en läsordning, inte krav att läsa allt. Filkorten leder till originalen. Kontrollera kontrakten mot aktuell kod.

| Fil | Varför |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/dokument/rapportversion.py.md\|src/riskanalys/dokument/rapportversion.py]] | V10 är dokumentstandard; AI-skrivformat väljs separat. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/arb_v10.py.md\|src/riskanalys/dokument/arb_v10.py]] | Bygg V10 via V9 och den fulla V8-analysen. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/resultatrapport_v10.py.md\|src/riskanalys/dokument/resultatrapport_v10.py]] | Disposition och källbundna avsnitt utan nya riskbeslut. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/resultatmodell_v10.py.md\|src/riskanalys/dokument/resultatmodell_v10.py]] | Frysta konstruktioner, källreferenser och transformationer. |

## Kontrakt att bevara

- Indata: fryst profil/bedömning, validerad skrivning och lokal analys. Utdata: kanoniskt Dokument med hela underlaget och källspår.
- Återge sparade motorutfall; inför ingen ny riskberäkning i textbyggaren. Lokala original, perioder och öppna markörer får inte tyst försvinna.
- Innehåll får inte kapas för ett ord-/sidtal. Äldre format och deras frysta kontrakt ska bevaras; V5–V9-filer innehåller också byggdelar som V10 återanvänder.
- Dokumentformat och AI-skrivformat är separata kontrakt. V10 är dokumentstandard, medan skrivformatet fortfarande är V8.
- V10:s tre delar ska bevara hela analysen och dess underlag. Presentationsflyttar ändrar inte motorutfall eller privata original.

## Fördjupa bara vid behov

| Fil | När den behövs |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/dokument/arb_v9.py.md\|src/riskanalys/dokument/arb_v9.py]] | Återanvänd analysunderlag och bilagor från V8. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/arb_v8.py.md\|src/riskanalys/dokument/arb_v8.py]] | Fullständig analyskälla; fortfarande del av V10-kedjan. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/faktorstatus_v10.py.md\|src/riskanalys/dokument/faktorstatus_v10.py]] | Skilj bekräftad faktastatus från motorns försiktighetspåslag. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/kapitel3_v10.py.md\|src/riskanalys/dokument/kapitel3_v10.py]] | Indikatorer och lägre-risk-exempel med lokala motiveringar. |
| [[docs/kodkarta/filer/src/riskanalys/dokument/metodavsnitt_v10.py.md\|src/riskanalys/dokument/metodavsnitt_v10.py]] | Metodtabeller från den bundna regelbasversionen. |

## Berörda områdesgränser

- [[docs/omraden/AI-skrivning.md|AI-skrivning]] när skrivsvar eller versionskontrakt ändras.
- [[docs/omraden/Lokal-analys.md|Lokal-analys]] när lokala svar/beslut projiceras.
- [[docs/omraden/Word-och-leverans.md|Word-och-leverans]] när kanonisk struktur eller placeringsidentitet ändras.
- [[docs/omraden/Granskning.md|Granskning]] när källfält, låsta spann eller innehållskontroller ändras.

Kontrollera direkta importer och bakåtlänkar för den ändrade filen, och sök även funktions-/fältnamn i koden. Statiska importer visar varken alla runtimekopplingar eller faktisk testtäckning.

## Verifiering

Börja med följande provurval när det passar ändringen; det ersätter inte bredare verifiering av ändrade kontrakt.

```bash
env -u ANTHROPIC_API_KEY .venv312/bin/python -m pytest tester/enhet/test_resultatrapport_v10.py tester/enhet/test_faktorstatus_v10.py -q
```

Vid berörd kedja: [[docs/kodkarta/filer/tester/intag/test_rapportflode_v8.py.md|tester/intag/test_rapportflode_v8.py]] · [[docs/kodkarta/filer/tester/enhet/test_arb_v7.py.md|tester/enhet/test_arb_v7.py]].

## Styrande avsnitt

Aktuella tillägg: [[docs/superpowers/plans/2026-10-23-rapport-v10.md|2026-10-23-rapport-v10]] · [[docs/superpowers/plans/2026-10-24-redaktionell-runda.md|2026-10-24-redaktionell-runda]] · [[docs/superpowers/specs/2026-10-22-resultatrapport-design.md|2026-10-22-resultatrapport-design]].

[[docs/superpowers/specs/2026-10-08-riskanalys-design.md#7.9 V8: tjänsteanalysens läsordning|Spec §7.9 V8: tjänsteanalysens läsordning]] · [[docs/superpowers/specs/2026-10-08-riskanalys-design.md#8.5 V8: reproducerbara produktionsvägar|Spec §8.5 V8: reproducerbara produktionsvägar]]. Läs också relevant aktuell post i [[docs/STATUS.md|statusjournalen]] och uppgiftens befintliga plan enligt [[docs/START.md|arbetsgången]].
