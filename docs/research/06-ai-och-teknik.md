# 06 AI och teknik

Fakta om Claude-API:t gäller per oktober 2026 och kommer från Anthropics dokumentation för utvecklare.

## Claude-API

| Fråga | Svar | Följd för designen |
|---|---|---|
| Vilken modell? | Standard är `claude-opus-5-5`. Billigare alternativ är `claude-sonnet-5-5` och `claude-haiku-5-5`. | Opus för skrivande och provtillsyn. Billigare modell kan prövas för extraktion av profiluppgifter, men först efter mätning. |
| Tänkande | Adaptiv tänkning. Djupet styrs med `effort` (low–max). Standard för Opus 5.5 är `medium`. | `high` för skrivuppgifter, sätts uttryckligen |
| Strukturerade svar | `output_config.format` eller SDK:ns `messages.parse` med schema. Svaret valideras mot schemat. | Alla AI-svar i låsta pydantic-scheman |
| Inbyggda källhänvisningar | Finns för dokument som skickas med, men **går inte att kombinera med strukturerade svar** | Egna referens-ID:n i schemat i stället. De pekar på regelbasen, vilket är bättre för spårbarheten. |
| Långa svar | Strömning rekommenderas vid stora `max_tokens` | Strömning i textgeneratorn |
| Kostnad | Prompt-cachning av stabila prefix. Batch-API till halva priset för asynkron körning, men batchen lagrar begäran och svar hos leverantören i upp till 29 dagar (kan raderas efteråt). | Regelbasens innehåll först i anropet. Batch används inte som standard och bara för underlag utan personuppgifter, med radering efter hämtning. |
| Val av modell och effort | Leverantören rekommenderar uppgiftsspecifika utvärderingar | `claude-opus-5-5` med effort `high` är startinställning. En utvärdering med riktiga skrivuppgifter (sakfel, ogrundade påståenden, granskningstid, kostnad per godkänt avsnitt) avgör inställningen. |
| Automatiska tester | Anrop mot riktiga API:t kostar pengar och ger olika svar | En kontrollerad testleverantör ger förutbestämda svar i alla automatiska tester. Livetester är frivilliga och körs separat. |
| Avböjanden | `stop_reason: "refusal"` ska alltid kontrolleras. Fallback kan slås på serverside. | Felhantering i AI-klienten |
| Databehandlingens geografi | Anthropics egna API: `inference_geo` med `us` eller `global`. EU-region finns via Google Vertex AI (`eu`) och Amazon Bedrock (EU-regioner). | I fas 1 skickas inga personuppgifter till AI (rollplatshållare i stället för namn), så Anthropics API kan användas. Om personuppgifter någon gång måste skickas krävs EU-behandling via Vertex eller Bedrock. Leverantören kapslas in bakom ett gränssnitt. |

## Varför AI bara skriver

- Ett tidigare AI-genererat paket visar att AI kan skriva metodiskt bra text. Men det krävde många versioner för att bli konsekvent, och påståenden om källor och datum gick inte att lita på utan kontroll.
- Med strukturerade svar och egna referens-ID:n kan varje stycke valideras maskinellt:
  - Alla ID:n finns.
  - Alla siffror finns i underlaget.
  - Nivåer stämmer med motorn.
  - Obekräftade uppgifter är markerade.
- AI-provtillsynen är ett komplement till de deterministiska kontrollerna, inte en ersättning.

## Python-verktyg

| Behov | Verktyg | Kommentar |
|---|---|---|
| Scheman och validering | pydantic v2 | Samma scheman används för regelbas, profil, motor och AI-svar |
| Regelbas och profil | YAML (PyYAML eller ruamel.yaml) | Läsbart för sakkunniga |
| Kommandorad | Typer eller Click | Enkelt att utöka |
| Tester | pytest | Ett test per beslutstabellrad, plus facitjämförelser |
| Word-export | docxtpl (Jinja-taggar i Word-mallar) eller python-docx | docxtpl släppte senast version 0.20.2 i november 2025 och har en underhållare. Taggar måste ligga i samma "run" i Word. python-docx är reserv. |
| PDF | Konvertering från Word (till exempel LibreOffice i kommandoradsläge) | Skjuts till etapp M4. M1 exporterar Word med python-docx. |
| Text ur källdokument | pdftotext, standardbiblioteket för mhtml, docx och xlsx | Se [verktyg/extrahera_text.py](verktyg/extrahera_text.py) |
| AI | Anthropics officiella Python-SDK (`anthropic`) | Ingen egen HTTP-klient |

## Arbetssätt med Claude Code och Codex

- `AGENTS.md` (läses av Codex) och `CLAUDE.md` (läses av Claude Code) ska ha samma regler: mappstruktur, namngivning, att tester körs före varje commit och att regelbasen inte ändras utan källa.
- Små filer med tydliga gränser gör det lättare för båda verktygen att ändra rätt sak.
- Tester är skyddsnätet när koden skrivs med AI-hjälp av någon utan lång programmeringsvana.
