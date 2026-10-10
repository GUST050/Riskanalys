# Researchverktyg

Engångsskript från researchen 2026-10-08. De är inte en del av programmet och har inga tester.

## extrahera_text.py

Konverterar källdokument till ren text, en `.txt` per källa.

| Format | Metod |
|---|---|
| PDF | `pdftotext -layout` (Poppler måste vara installerat) |
| MHTML (sparade webbsidor) | Standardbibliotekets `email` och `html.parser` |
| DOCX | Läser `word/document.xml`, stycken och tabeller |
| XLSX | Läser blad, delade strängar och formler |
| Pages | Packar upp `Index.zip` och dekomprimerar IWA (Snappy) samt plockar ut textsträngar |

```bash
python3 -I extrahera_text.py <utmapp> <fil> [<fil> ...]
```

## sanktionsstatistik.py

Läser text från Länsstyrelsens sidor om ingripanden (konverterade med skriptet ovan) och klassificerar varje beslut efter:

- vad som granskats: endast allmän riskbedömning, allmän riskbedömning och rutiner, samtliga delar, eller övrigt
- typ av ingripande
- sanktionsavgiftens belopp

```bash
python3 -I sanktionsstatistik.py <stockholm.txt> <vastra_gotaland.txt>
```

Klassificeringen bygger på textmönster och ska ses som ungefärlig. Se begränsningarna i [03-tillsyn-och-sanktioner.md](../03-tillsyn-och-sanktioner.md).

## verifiera_tillsynsmaterial.py

Kontrollerar det syntetiska granskningsmaterialets struktur: unika ID:n, befintliga B-referenser, dokument- och sidhänvisningar samt kontrollvarianter. Med `--underlag` kontrolleras även SHA-256 och sidkarta i det lokala källarkivet. Standardbiblioteket räcker; inga paket installeras och inga API-anrop görs.

Kör från repots rot:

```bash
python3 -I docs/research/verktyg/verifiera_tillsynsmaterial.py
python3 -I docs/research/verktyg/verifiera_tillsynsmaterial.py --underlag ../underlag/tillsyn-2026-10-09
```

Resultatet är en materialkontroll. Programmets granskningsförmåga och facitets juridiska riktighet ska prövas enligt [research 09](../09-tillsynsbeslut-2026.md#bevarat-underlag-och-återanvändbara-granskningsfall).
