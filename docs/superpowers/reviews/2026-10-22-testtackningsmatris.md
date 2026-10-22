# Påståendetäckning vid kortare verifiering

Bas `f66a70f`. Detta dokument beskriver testernas ansvar, inte fullsvitens ännu ej avslutade leveransutfall. Vanlig pytest och fullprofilen omfattar samtliga rader; snabb-/analysprofiler är explicita urval.

| Tidigare kontroll | Ny/bevarad kontroll | Vad som faktiskt prövas |
|---|---|---|
| Sju `test_m2_negativ_cli_skapar_inget_paket` | `test_m2_grindar.py`: fem `test_negativ_cli_stoppar_just_andrat_underlag` + två `test_fel_fore_bedomning_skrivning_bygger_ratt_startlage` | Samma sju orsaker; konkret orsak måste saknas före och finnas efter injicering. CLI exit 1, relevant feltext, inget paket. |
| Saknat profilbelägg | `belagg` | Aktuell profils `P-ORG.namn` saknar belägg enligt domängrinden. Riktig CLI-huvudfunktion stoppar ändrad profilbindning; separat riktig subprocess gör samma sak. |
| Saknad sakkunniggranskning | `expert` | `attesthinder` för KUNDMETOD-C är tom före och icke tom efter borttagen granskning. CLI stoppar ändrad regelbas/modellbindning innan publicering. |
| Metod underkänd | `metod` | KUNDMETOD-C:s beslut ändras i testets egen regelbaskopia; konkret attestfel plus CLI:s regelbasbindningsspärr. |
| Framtida beslut | `datum` | En giltig bas har noll hinder på sin dag; framtida datum ger ordinarie grindhinder och CLI-fel. |
| Läsbar äldre bedömning utan omfattning | `aldre` | `_m2` prövas med samma tidigare giltiga underlag men läst äldre bedömning: uttryckligt omfattningsfel. CLI stoppar den nya bedömningsmanifestbindningen. V8-presentationen förfalskas inte för att nå senare grind. |
| Öppen AI-fråga | `fraga` | Den gamla kedjebyggaren används fortfarande från före skrivning, med CLI i process. Frågan injiceras i testsvar, CLI-feltexten måste nämna fråga. Inga gissade frågor läggs i ett redan godkänt dokument. |
| Fel regelpaket | `felpaket` | Kedjan börjar före bedömning. Fel län ska ge preliminär bedömning; senare CLI-avslag ska uttryckligen nämna regelpaket. |
| Positiv verklig CLI-kedja för VG/Skåne/Stockholm | Tre gamla `test_m2_hela_cli_kedjan_och_aterstallning`, markerade `fullkedja` | Samtliga kommandotyper passerar riktig subprocess. Alla avsnitt passerar fortsatt CLI-parsern; efter första avsnittet används huvudfunktionen i samma process. Status, V8, båda DOCX, manifest, noll fynd, verifiering och återställda bytes behålls. |
| Handredigerat profilbelägg stoppas vid bedömning | Gammalt `test_handredigerad_bekraftelse_utan_kalla_stoppas_vid_bedom` | Oförändrad riktig subprocess, specifikt fältnamn/källa och inga bedömnings-/fastställelsepaket. |
| Tre fulla HTTP-formulärresor | En gammal full VG-resa + tre `test_paketval_webb` | VG fyller fortsatt hela formuläret inklusive samlade grupper och skapar riktig Word. Kort HTTP-start kontrollerar varje län/filial/paket; faktiska aktiva frågor, unika ID, perioder och härledda antal provas för alla tre. |
| Webbens CSRF/origin/host, indatafel, gammal revision, dubbel skrivning och ogiltig Word-länk | Samtliga befintliga prov i `test_webb.py` samt `test_skyddad_begaran.py` | Behållna, inte ersatta med mockad HTTP. |
| Rapporter och export | Befintliga `test_rapportflode_v8.py`, `test_rapportpaket_v8.py`, `test_analysgrind.py` | Inga rapport-/fynd-/proveniensassertioner borttagna. Riktig DOCX, båda delar, avbrott, fryst evidens, lås och finalisering kvar. |
| Modulfixturer för analys och schema 2 | `klona_kedja` + fyra nya isoleringsprov | Befintlig återanvändning behålls; varje byrå och regelbas kopieras separat. Symlänkar avvisas, inga hårdlänkar och ingen beständig cache mellan körningar. Ingen ny tidsvinst tillskrivs redan befintliga fixturer. |
| Testkörningens bevis | `test_testverktyg.py` och profilerna | Tomt urval/fel/Pythonversion/källändring får inte ge verifierat grönt; collection ska matcha varje JUnit-post. Fullprofilen väljer inte bort fullkedjor. |

## Reproduktion av de negativa provens känslighet

En separat lokal pytest-plugin används enbart för att ta bort respektive injicerad felorsak. De fem delade basfallen ska då falla på att den specifika orsaken inte nått grinden. För frågefallet tas frågan bort före skrivning; felpaketsfallet återställs före bedömning. Dessa avsiktligt röda körningar sparas separat från den gröna leveranskörningen. Pluginen ligger utanför produkt/testprofiler och följer inte med i ordinarie svit.

Äldre negativa prov krävde i huvudsak exitkod 1. Den nya domänkontrollen gör att exempelvis ett attestprov inte kan räknas som lyckat enbart därför att ett annat allmänt bindningsfel inträffade. Båda kontrollnivåerna redovisas uttryckligen ovan.
