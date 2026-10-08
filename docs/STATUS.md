# Status och framsteg

Senast uppdaterad 2026-10-08.

## Läge

**Fas:** design. Ingen programkod är skriven ännu.

| Steg | Status |
|---|---|
| Genomgång av källmaterial | Klar |
| Gemensam förståelse av mål och målgrupp | Klar |
| Val av omfattning (alternativ C) | Klar |
| Val av arkitektur (alternativ 2) | Klar |
| Fördjupad research (EU-regelverk, metod, teknik) | Klar |
| Strukturförslag och spec | **Skriven, väntar på granskning** |
| Implementeringsplan | Ej påbörjad |
| Etapp M0 (repo, scheman, regelbasvalidering) | Ej påbörjad |

## Beslut

| Datum | Beslut | Motivering |
|---|---|---|
| 2026-10-08 | Målgrupp: konsultbyråer för egen efterlevnad, sedan andra företag | Största sektorn under Länsstyrelsens tillsyn och flest sanktioner. Referensfall finns. |
| 2026-10-08 | Omfattning C: verksamhetsnivå först, datamodell förberedd för kundnivå | De flesta sanktioner gäller verksamhetsnivån. Kundnivån kräver personuppgifter och integrationer. |
| 2026-10-08 | Arkitektur 2: regelbas och deterministisk motor, AI som skribent | Reproducerbart, spårbart och testbart. Löser problemen i det tidigare AI-utkastet. |
| 2026-10-08 | Python, YAML, pydantic, pytest, Claude via officiell SDK | Läsbart för en byggare med AI-hjälp. Bra stöd för Word och AI. |
| 2026-10-08 | Kärna och CLI först, webbgränssnitt senare | Kärnan är det svåra. Gränssnittet kan läggas ovanpå. |
| 2026-10-08 | Byggs med Claude Code och Codex | Kräver gemensamma regler i `AGENTS.md` och `CLAUDE.md` och många tester |

## Nästa steg

1. Granska [specen](superpowers/specs/2026-10-08-riskanalys-design.md) och godkänn eller begär ändringar.
2. Ta fram implementeringsplan för etapp M0–M4.
3. Bestäm vem som gör sakkunniggranskningen av regelbasen.
4. Hämta och jämför Länsstyrelsen Skånes föreskrifter (12FS 2024:8).

## Öppna frågor

Se avsnitt 17 i specen.
