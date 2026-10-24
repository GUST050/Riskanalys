---
typ: start
tags: [riskanalys, oversikt]
---

# Riskanalys — börja här

Gemensam ingång för Obsidian, Codex och Claude Code. [[AGENTS.md|Arbetsreglerna]] gäller en gång; [[CLAUDE.md|Claude-ingången]] hänvisar till dem. Programmet ligger i `src/riskanalys/`. Läs relevant kontext stegvis.

## Aktuell struktur och arbetsgren, 2026-10-24

Valvet följer den aktuella lokala arbetskopian. Robusthetsändringarna finns i `2d25550` och CI-ändringen i `a21bf49` på `codex/robust-programstruktur`. De är inte mergade till `main`, som ligger på `416579e`. Det aktuella dokumentformatet är **V10**, med resultatrapport, analysbilaga A och underlagsbilaga B1 i samma paket. AI-skrivformatet är fortsatt **V8**. Äldre V8- och V9-byggare är också beroenden för V10; versionsnumret i ett filnamn avgör inte om filen fortfarande används.

Den nya strukturen omfattar gemensam analys i schema 2, uttrycklig tillämpning per tjänst, engångsbekräftelse, tjänsteplaner och provisoriska metodbeslut. V10:s redaktionella presentation har ett fryst flyttregister och kräver uttryckligt byte för äldre utkast. Börja med [[docs/omraden/Programflode.md|programflödet]] eller välj området nedan.

Aktuella styrdokument: [[docs/superpowers/specs/2026-10-22-forenklad-riskbedomning-design.md|Gemensam analys]] · [[docs/superpowers/specs/2026-10-22-resultatrapport-design.md|Tre rapportdelar]] · [[docs/superpowers/plans/2026-10-23-rapport-v10.md|V10-planen]] · [[docs/superpowers/plans/2026-10-24-redaktionell-runda.md|Redaktionell V10]] · [[docs/testning.md|Testprofiler och Python 3.12]] · [[docs/sakkunniggranskning.md|Sakkunniggranskning]].

## Välj primärt område

För fortsatt struktur- och robusthetsarbete: [samordnad plan A0–A8](superpowers/plans/2026-10-24-robust-programstruktur.md). Den tekniska implementationen är klar. Planens §8 redovisar gemensamma tjänster, typade analyskommandon, låst miljö och sparad verifiering. §9 redovisar utförd avgränsad Word-kontroll och konkreta återstående användar-, sakkunnig- och driftbeslut. Fullsviten startas bara på uttrycklig begäran; inga tester körs i denna fortsättning.

| Uppgiften gäller | Läs denna kontext |
|---|---|
| Formulär, frågor, svar, CSRF, registerbekräftelse | [[docs/omraden/Intag.md\|Intag och formulär]] |
| Profilfält, tjänsteplaner, förändringar och profilsparning | [[docs/omraden/Profil.md\|Byråprofil]] |
| SCB, Bolagsverket, bokslut, iXBRL, registerbilder | [[docs/omraden/Foretagsdata.md\|Företagsdata]] |
| YAML-kataloger, villkor, källor, datum-/länsurval | [[docs/omraden/Regelverk.md\|Regelverk och regeldata]] |
| Risknivåer, scenarier, kontroller, bedömningskörning | [[docs/omraden/Riskmotor.md\|Deterministisk riskmotor]] |
| Gemensam analys i schema 2, tjänstetillämpning och täckningsprövning | [[docs/omraden/Lokal-analys.md\|Lokal verksamhetsanalys]] |
| Faktablad, promptar, AI-schema, omförsök, textleverantör | [[docs/omraden/AI-skrivning.md\|AI-skrivning]] |
| V10-resultatrapport, analysbilaga, källor och motorförklaring | [[docs/omraden/Rapport.md\|Rapportens innehåll]] |
| Word, layout, presentation, rapportvyer, export/nedladdning | [[docs/omraden/Word-och-leverans.md\|Word och leverans]] |
| Fynd, källkontroll, sakgranskning, fastställelse | [[docs/omraden/Granskning.md\|Granskning och fastställelse]] |
| Manifest, filintegritet, datamapp, modellidentitet, historik | [[docs/omraden/Drift-och-lagring.md\|Drift och lagring]] |
| Start, CLI-argument, kommandon, användarfel | [[docs/omraden/CLI.md\|Kommandorad och start]] |
| Fixturer, provurval, frysta underlag, kedjeverifiering | [[docs/omraden/Tester.md\|Tester]] |
| Arbetsregler, dokumentation, kartgenerator | [[docs/omraden/Projekt.md\|Projektets dokumentation]] |

Om flera områden berörs: börja där beteendet ändras och följ konsumenterna i guiden. Dokumentkedjan är uppdelad i AI-skrivning → Rapport → Word/leverans, med Granskning över kedjan. [[docs/omraden/Programflode.md|Programflödet]] visar helheten när den behövs.

## Läs kontext i tre steg

1. **Orientera:** kontrollera arbetskopia och diff. Välj en guide; läs dess ansvar, kontrakt och uppgiftens startfil/typer.
2. **Följ påverkan:** läs berörda konsumenter och regressioner. Använd filkort, `rg` och relevanta spec-/planavsnitt. Vid gemensamt schema eller tvärgående fel behövs flera områden.
3. **Utöka vid belägg:** öppna fler filer, äldre format eller historiska beslut när uppgiften kräver det. Ett litet starturval är en prioritering, aldrig ett tak för en fullständig utredning.

Områdesguiderna är handskriven navigering. Datumet `kontext_granskad` anger senaste genomgång, inte att framtida kodändringar automatiskt har granskats. Filkortens hash/radantal/importer kan kontrolleras maskinellt. Läs originalet när beteendet är avgörande.

## Hitta aktuell status och avsett beteende

- [[docs/superpowers/specs/2026-10-08-riskanalys-design.md|Specifikationen]] och uppgiftens befintliga plan beskriver avsett beteende. Varje guide länkar relevanta spec-rubriker.
- Sök rubriker i [[docs/STATUS.md|statusjournalen]]; läs den senaste relevanta posten och följ dess planlänk. Poster om Obsidian är inte produktens verifieringsstatus.
- [[docs/PROGRAMKARTA.md|Den fullständiga programkartan]] är ett daterat uppslagsverk. Läs en relevant del vid behov.
- [[docs/kodkarta/INDEX.md|Aktuellt filregister]] är återbyggbar metadata; ladda inte alla filkort som kontext.

```bash
rg -n '^## ' docs/STATUS.md
rg -n 'schema 2|V10|metodbeslut|bindning' docs/STATUS.md docs/superpowers/plans
rg -n '^#{1,3} ' docs/superpowers/specs/2026-10-08-riskanalys-design.md
```

Välj sökord efter uppgiften och läs det relevanta avsnittet, inte hela journalen. En äldre anteckning eller lyckad körning är inget nytt provresultat. Om spec, guide och implementation skiljer sig: redovisa skillnaden och hantera den i den befintliga uppgiften.

## Läs struktur med eller utan Obsidian

Filerna i den egna arbetskopian är alltid tillgängliga för utvecklingsagenten. Obsidian CLI ger dessutom länkar och bakåtlänkar när appen är igång:

```bash
obsidian vault=Riskanalys vault info=path
obsidian vault=Riskanalys read path=docs/omraden/Riskmotor.md
obsidian vault=Riskanalys links path=docs/omraden/Riskmotor.md
obsidian vault=Riskanalys backlinks path=docs/kodkarta/filer/src/riskanalys/bedomning/motor.py.md format=json
```

Jämför valvets sökväg med `git rev-parse --show-toplevel`. Använd den egna kopians filer om vägarna skiljer sig; skriv inte genom CLI till en annan worktree. Om filkorten saknas eller är inaktuella: bygg om dem lokalt. Statiska importer missar vissa runtimekopplingar; bakåtlänkar och testimporter bevisar inte testtäckning.

Grafens första vy visar startsidan och områdes-/flödessidorna med filtret `(path:docs/omraden OR path:docs/START.md) -path:docs/kodkarta`. Töm filtret för alla anteckningar. Grafens visuella filter begränsar inte agentens filåtkomst.

## Håll kontexten aktuell

- **Ny/ändrad fil eller import:** bygg om kartan och kontrollera aktualitet.
- **Ändrat ansvar, schema, ingång eller provurval:** uppdatera relevant områdesguide och vid behov befintlig spec/plan/status. Generatorn kan inte ompröva ansvarstext åt dig.
- **Nytt område:** lägg till guide, rad i tabellen och områdesgruppering i generatorn. Håll gemensamma instruktioner i AGENTS; håll CLAUDE tunt.
- **Överlämning:** skriv kort i uppgiftens befintliga plan/status när det behövs: mål, arbetskopia/branch och kodläge, ändrade filer, berörda kontrakt, exakta verifieringsutfall, öppna frågor och nästa steg. Länka bevis; kopiera inte chattloggar.
- **Samtidigt arbete:** avgränsade filer, egna arbetskopior och syntetiska datamappar. Samordna delade modeller och kontrakt. En areas avgränsning är inte bevis på att dess ändring saknar följder i andra områden.

```bash
python3.12 docs/research/verktyg/bygg_obsidiankarta.py
python3.12 docs/research/verktyg/bygg_obsidiankarta.py --check
```

`docs/kodkarta/` och `.obsidian/` är lokala och ignorerade. Kartan använder Git-urvalet, inklusive nya ej ignorerade filer; privata byrådata och nycklar ska aldrig läggas där. Ändra originalen och de handskrivna guiderna, inte genererade filkort. Dokumentationen delas genom projektfilerna; chatthistorik delas inte automatiskt och vanlig ChatGPT-webb har ingen separat molnanslutning till detta valv.
