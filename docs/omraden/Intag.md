---
typ: omrade
omrade: Intag
kontext_granskad: 2026-10-24
tags: [riskanalys, omrade, ai-kontext]
---

# Intag och formulär

Från lokala formulär och registerförslag till uttryckligen bekräftade profiluppgifter. HTTP-hantering och vyer ska använda samma tjänst och svarsväg som övrigt intag.

[[docs/START.md|Arbetsgång och kontextnivåer]] · [[docs/omraden/Programflode.md|Programflödet]] · [[docs/kodkarta/omraden/Intag.md|Alla filkort i området]]

## Minsta kodkontext

Läs uppgiftens ingång och relevanta typer först; tabellen är en läsordning, inte krav att läsa allt. Filkorten leder till originalen. Kontrollera kontrakten mot aktuell kod.

| Fil | Varför |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/intag/webb.py.md\|src/riskanalys/intag/webb.py]] | HTTP-rutter, formulärskydd och session. |
| [[docs/kodkarta/filer/src/riskanalys/intag/tjanst.py.md\|src/riskanalys/intag/tjanst.py]] | Intagstjanst: operationer och skydd mot gamla formulär. |
| [[docs/kodkarta/filer/src/riskanalys/intag/svar.py.md\|src/riskanalys/intag/svar.py]] | besvara: validering, bekräftelse och omprövning av belägg. |
| [[docs/kodkarta/filer/src/riskanalys/intag/modeller.py.md\|src/riskanalys/intag/modeller.py]] | Fråge- och svarsmodeller. |

## Kontrakt att bevara

- Indata: regelbas, aktuell profilrevision och uttryckligt användarsvar. Utdata: validerad profiländring med individuell källa, datum och period.
- Behåll CSRF, revisionskontroll, Vet inte och samma svarshantering för enskilda/samlade svar. Ett registerförslag är inte en bekräftelse.
- Vid ändrad lokal analys får en gammal Word-export inte fortsätta laddas ned. Uppdatering av export återanvänder befintlig AI-skrivning.

## Nya ingångar efter merge till main

| Fil | Ansvar |
|---|---|
| [[docs/kodkarta/filer/src/riskanalys/intag/gemensamvy.py.md\|src/riskanalys/intag/gemensamvy.py]] | Arbetsvyer för gemensamt underlag, tjänstetillämpning och separat granskning. |
| [[docs/kodkarta/filer/src/riskanalys/intag/engangsvy.py.md\|src/riskanalys/intag/engangsvy.py]] | Gemensam bekräftelse och en samlad genomgång per tjänst. |
| [[docs/kodkarta/filer/src/riskanalys/intag/planeringsvy.py.md\|src/riskanalys/intag/planeringsvy.py]] | Planer, förändringsutvärderingar och kombinationsgrupper. |
| [[docs/kodkarta/filer/src/riskanalys/intag/dokument.py.md\|src/riskanalys/intag/dokument.py]] | Tre rapportdelar och uttryckligt byte av V10-presentation. |

## Fördjupa bara vid behov

| När uppgiften gäller | Läs vidare |
|---|---|
| Registerförslag eller samlade frågor | [[docs/kodkarta/filer/src/riskanalys/intag/register.py.md\|src/riskanalys/intag/register.py]] · [[docs/kodkarta/filer/src/riskanalys/intag/samlade.py.md\|src/riskanalys/intag/samlade.py]] |
| Word-knappar eller nedladdning | [[docs/kodkarta/filer/src/riskanalys/intag/dokument.py.md\|src/riskanalys/intag/dokument.py]] · [[docs/kodkarta/filer/src/riskanalys/intag/analysvy.py.md\|src/riskanalys/intag/analysvy.py]] |

## Berörda områdesgränser

- [[docs/omraden/Profil.md|Profil]] när svarens typ, period eller bekräftelsestatus ändras.
- [[docs/omraden/Foretagsdata.md|Foretagsdata]] när förslag hämtas eller väljs.
- [[docs/omraden/Lokal-analys.md|Lokal-analys]] när analysformulär eller revisionskontroll ändras.
- [[docs/omraden/Word-och-leverans.md|Word-och-leverans]] när utkast skapas, uppdateras eller laddas ned.

Kontrollera direkta importer och bakåtlänkar för den ändrade filen, och sök även funktions-/fältnamn i koden. Statiska importer visar varken alla runtimekopplingar eller faktisk testtäckning.


### Transport och arbetsflöden

Webbens leverantörsval kommer från `konfiguration.py`. Skapa/uppdatera/kontrollera/läsa utkast finns i `arbetsfloden.py`; `intag/dokument.py` behåller `omfattningsknapp`, `rapportdel` och kompatibla importalias. Analysformuläret ger ett blockavgränsat kommando med revision. Tjänsten läser om aktuellt paket och prövar identitet, referenser och visad summa under låset innan sparning. CSRF/HTTP-fält stannar i adaptern. `fragefalt` finns tillsammans med `fragor` i `intag/fragor.py`.

## Verifiering

Börja med följande provurval när det passar ändringen; det ersätter inte bredare verifiering av ändrade kontrakt.

```bash
env -u ANTHROPIC_API_KEY .venv312/bin/python -m pytest tester/intag/test_webb.py tester/intag/test_samlade_fragor.py -q
```

Vid berörd kedja: [[docs/kodkarta/filer/tester/intag/test_kedja.py.md|tester/intag/test_kedja.py]] · [[docs/kodkarta/filer/tester/intag/test_rapportflode_v8.py.md|tester/intag/test_rapportflode_v8.py]].

Nya kontrakt har särskilda regressioner:

```bash
env -u ANTHROPIC_API_KEY .venv312/bin/python -m pytest tester/intag/test_gemensam_helhetsbekraftelse.py tester/intag/test_resultatrapport_v10.py -q
```

## Styrande avsnitt

[[docs/superpowers/specs/2026-10-08-riskanalys-design.md#14.1 Fullständigt intag och skrivning av hela riskbedömningen|Spec §14.1 Fullständigt intag och skrivning av hela riskbedömningen]] · [[docs/superpowers/specs/2026-10-08-riskanalys-design.md#14.4 Registeruppgifter i lokalt intag|Spec §14.4 Registeruppgifter i lokalt intag]]. Läs också relevant aktuell post i [[docs/STATUS.md|statusjournalen]] och uppgiftens befintliga plan enligt [[docs/START.md|arbetsgången]].
