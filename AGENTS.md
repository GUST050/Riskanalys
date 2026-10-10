# Arbetsregler för Riskanalys

Gäller för alla som skriver kod i repot, både människor, Codex och Claude Code.

## Läs först

- Spec: `docs/superpowers/specs/2026-10-08-riskanalys-design.md`
- Aktuell plan: `docs/superpowers/plans/`
- Status och beslut: `docs/STATUS.md`

## Kommandon

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest                      # alla tester utom livetester
.venv/bin/riskanalys regelbas validera
```

## Regler som inte får brytas

1. **AI fattar inga beslut.** Risknivåer, poäng och regler kommer från regelbasen och riskmotorn. AI skriver bara text i ett låst schema.
2. **Inga personuppgifter till AI.** AI-underlag byggs bara ur tillåtelselistan i `regelbas/tillatelselistor.yaml`. Personer skrivs som `{roll:FfR}`.
3. **Byrådata aldrig i repot.** Den ligger i `$RISKANALYS_DATA`. Lägg aldrig in riktiga byråuppgifter i tester, bara syntetiska.
4. **Regelbasen ändras bara med källa.** Varje krav, katalogpost och regel har `kallor` eller `kalla` och en `grund`. Skalor, gränser och poäng märks `metodval`.
5. **Inga fria uttryck i regelbasen.** Villkor skrivs i det typade formatet (spec 6.3). Ingen `eval`.
6. **Tester före commit.** Kör `.venv/bin/pytest` och se att allt är grönt innan du committar. Skriv testet först.
7. **Inga anrop mot riktiga API:t i automatiska tester.** Använd `Testleverantor`. Livetester markeras `@pytest.mark.live`.
8. **Ändra aldrig sakkunnigstatus i repots regelbas** till `verifierad` utan en verklig sakkunnig granskning. Tester signerar en kopia.

## Stil

- Användartexter och dokumentation på svenska. Identifierare i koden på svenska utan å, ä och ö.
- Små filer med en uppgift var. En funktion gör en sak.
- Fel som användaren kan åtgärda ärver från `riskanalys.fel.RiskanalysFel` och har ett meddelande som säger vad som ska göras.
- Funktioner returnerar nya objekt i stället för att ändra befintliga.
- Commit: `<typ>: <beskrivning>` med typerna feat, fix, refactor, docs, test, chore.
