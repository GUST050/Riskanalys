# Arbetsregler för Riskanalys

Gäller för alla som skriver kod i repot, både människor, Codex och Claude Code.

## Läs först

- Bekräfta aktuell arbetskopia med `pwd`, `git rev-parse --show-toplevel` och `git status --short`. Bevara andras ändringar.
- Läs `docs/START.md` och välj **ett primärt område** i `docs/omraden/`. Vid en avgränsad fortsättning kan du gå direkt till den redan valda guiden.
- Läs guidens relevanta startfiler, typer och prov; följ sedan de konsumenter som uppgiften berör. Börja normalt med en guide och 2–4 kodfiler. Utöka när kontrakt, fel eller tvärgående uppgift kräver det.
- Sök rubriker i `docs/STATUS.md` och `docs/superpowers/plans/`; läs den senaste relevanta statusposten och uppgiftens befintliga plan. Guiden pekar på relevanta avsnitt i `docs/superpowers/specs/2026-10-08-riskanalys-design.md`.
- Läs **inte hela** `docs/PROGRAMKARTA.md`, `docs/STATUS.md`, filregistret eller alla områdesguider rutinmässigt. De är uppslagsverk. Begränsa sökresultat till relevanta filer och läs vidare när det behövs.
- Ange kort mål, primärt område, berörda kontrakt och planerad verifiering innan större ändring. Avsedd funktion följer användarens uppgift och aktuell spec/plan; kod och prov visar faktisk implementation. Redovisa motsägelser i stället för att dölja dem.

## Gemensam projektnavigering i Obsidian

- `CLAUDE.md` hänvisar hit. Gemensamma regler finns en gång; områdeskontext finns i respektive guide. Skapa inte dubbla regeluppsättningar för modellerna.
- Dokumentationen är vanliga lokala filer och fungerar även när Obsidian är stängt. Valvet `Riskanalys` är knutet till en bestämd arbetskopia; jämför `obsidian vault=Riskanalys vault info=path` med din Git-rot före CLI-läsning/skrivning. I annan worktree: använd dess egna filer och karta.
- Läs filkort bara för berörda filer. Kontrollera originalkod och sök konsumenter även med `rg`; importer och bakåtlänkar är läshjälp, inte fullständig beroendeanalys eller testtäckning.
- Efter ändrat ansvar, kontrakt, ingång eller provurval: uppdatera berörd områdesguide och befintlig spec/plan/status där det behövs. Nytt område kräver guide, routing i `docs/START.md` och gruppering i kartgeneratorn.
- Efter fil-/import-/dokumentändringar: bygg kartan med `python3.12 docs/research/verktyg/bygg_obsidiankarta.py` och kör samma kommando med `--check`. Redigera aldrig `docs/kodkarta/` för hand. Generatorn kontrollerar metadata, inte sanningshalten i handskrivna ansvarsbeskrivningar.
- Vid parallellt arbete: egna arbetskopior och syntetiska datamappar, avgränsade filer och samordning av delade modeller/kontrakt. Lämna mål, arbetskopia, ändrade filer, verifiering och nästa steg i uppgiftens befintliga plan/status när en överlämning behövs. Chattar delar inte automatiskt historik.

## Verifiera och lämna över

- Välj först områdets relevanta prov och berörda konsument-/gränsprov. Bevara äldre format och frysta fixturer.

| Ändring | Kontroll före arbetscommit och överlämning | Fullsvit |
|---|---|---|
| Dokumentation och navigering (inga `.py`, regelbas, fixturer, profiler eller testverktyg) | Kartbygge med `--check` och länkar | Nej |
| Avgränsad ändring inom ett område | Reproducerande prov, områdets prov, berörda konsument-/gränsprov och snabbprofil; mål högst 5 min | Nej, ingår i nästa samlade kontrollpunkt |
| Delad kritisk logik: riskmotor, regelbas, datamodeller, integritet/tillåtelselistor, attest/fastställelse, lagring, testverktyg/profiler eller okänd påverkan | Som ovan, med bredare konsumenturval | Ja, före merge eller push till `main` |
| Paket till byrå eller sakkunnig och färdigt större funktionspaket | Som ovan | Ja, på exakt kandidat |

- Fullsviten körs vid samlade kontrollpunkter, gärna i bakgrunden medan oberoende arbete fortsätter. Ett avslutat chattvarv eller en arbetsredovisning är ingen kontrollpunkt. Redovisa riktat urval och fullsvit var för sig, och säg uttryckligen när en fullsvit återstår.
- Rapportera vad som ändrats, exakta körda kontroller och kvarstående begränsningar. Testinsamling, historiskt gröna resultat och dagens passerade prov ska hållas isär.
- Commit/push bara på användarens begäran. Återställ inte andras filer och starta inte nya externa AI-/API-körningar genom ett dokumentations- eller testarbete.

## Kommandon

```bash
python3.12 -m venv .venv312
.venv312/bin/pip install -e ".[dev]"
.venv312/bin/python scripts/testa.py snabb --ut /private/tmp/riskanalys-snabb-NYTT_ID
.venv312/bin/python -m pytest -q       # hela ordinarie sviten, inga livetester
.venv312/bin/riskanalys regelbas validera
```

## Regler som inte får brytas

1. **AI fattar inga beslut.** Risknivåer, poäng och regler kommer från regelbasen och riskmotorn. AI skriver bara text i ett låst schema.
2. **Inga personuppgifter till AI.** AI-underlag byggs bara ur tillåtelselistan i `regelbas/tillatelselistor.yaml`. Personer skrivs som `{roll:FfR}`.
3. **Byrådata aldrig i repot.** Den ligger i `$RISKANALYS_DATA`. Lägg aldrig in riktiga byråuppgifter i tester, bara syntetiska.
4. **Regelbasen ändras bara med källa.** Varje krav, katalogpost och regel har `kallor` eller `kalla` och en `grund`. Skalor, gränser och poäng märks `metodval`.
5. **Inga fria uttryck i regelbasen.** Villkor skrivs i det typade formatet (spec 6.3). Ingen `eval`.
6. **Verifiera efter ändringens påverkan.** Använd Python 3.12 via `.venv312/bin/python`. Skriv reproducerande test först vid beteendeändring. Välj kontroll enligt tabellen i *Verifiera och lämna över*. Saknade, avbrutna eller tidsstoppade prov rapporteras aldrig som godkända. Ett fullsvitsresultat gäller bara det oförändrade snapshot det kördes på; ändrad dokumentation eller nytt commit-ID kräver ingen omkörning.
7. **Inga anrop mot riktiga API:t i automatiska tester.** Använd `Testleverantor`. Livetester markeras `@pytest.mark.live`.
8. **Ändra aldrig sakkunnigstatus i repots regelbas** till `verifierad` utan en verklig sakkunnig granskning. Tester signerar en kopia.

## Stil

- Användartexter och dokumentation på svenska. Identifierare i koden på svenska utan å, ä och ö.
- Små filer med en uppgift var. En funktion gör en sak.
- Fel som användaren kan åtgärda ärver från `riskanalys.fel.RiskanalysFel` och har ett meddelande som säger vad som ska göras.
- Funktioner returnerar nya objekt i stället för att ändra befintliga.
- Commit: `<typ>: <beskrivning>` med typerna feat, fix, refactor, docs, test, chore.
