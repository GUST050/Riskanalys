# Researchverktyg

Researchverktyg från 2026-10-08–10. De är inte en del av programmets körkedja. `lydelsetexter.py` har automatiska regressionstester; äldre uttagsskript har inte samma verifiering.

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

## lydelsetexter.py

Läser lokalt hämtad SFS-text eller föreskriftstext från `pdftotext -layout`. Visar SHA-256 för efterfrågade paragrafer med samma blankteckennormalisering som regelbasen. SFS-ändringsnoter tas bort ur paragraftexten. Två datumlydelser hålls isär med suffixen `[U:ÅÅÅÅ-MM-DD]` och `[I:ÅÅÅÅ-MM-DD]`.

Kör från repots rot; verktyget gör inga nätanrop och ändrar inga filer:

```bash
python3 -I docs/research/verktyg/lydelsetexter.py fs ../underlag/kallkontroll-2026-10-10/14fs-2024-11-vastra-gotaland.txt '2 kap. 1 §'
python3 -I docs/research/verktyg/lydelsetexter.py sfs ../underlag/kallkontroll-2026-10-10/ptl-2017-630-rkrattsbaser.txt '3 kap. 17 §'
python3 -I docs/research/verktyg/lydelsetexter.py sfs ../underlag/kallkontroll-2026-10-10/ptl-2017-630-rkrattsbaser.txt '1 kap. 2 § [U:2026-11-20]' '1 kap. 2 § [I:2026-11-20]'
env -u ANTHROPIC_API_KEY .venv/bin/pytest tester/enhet/test_lydelsetexter.py -q
```

Felkod 0 betyder att alla begärda paragrafer hittades, 1 betyder saknad paragraf eller oläsbar/otolkbar källa, 2 betyder felaktiga argument. Nio kommandoradstester använder syntetiska källtexter; åtta fallerade före rättningen 2026-10-10. Verkliga lokala källfiler krävs inte för testsuiten.

Uttaget är en kandidattext. Allmänna råd, rubriker och övergångsbestämmelser ingår inte i paragraftexten. Tabeller, avstavningar och textens fullständighet måste kontrolleras mot originalet innan en juridisk lydelse godkänns. En matchande checksumma visar oförändrad text, inte att texten är juridiskt korrekt.
