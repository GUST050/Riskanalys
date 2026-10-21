# Granskning av planen för kravstöd och tjänsteexponering

Granskare: Claude Code, 21 oktober 2026.

Granskat material:
- [Planen](/Users/danieltrogen/Documents/ChatGPT/Riskbedömning/docs/superpowers/plans/2026-10-21-kravstod-och-tjansteexponering-plan.md) och [designen](/Users/danieltrogen/Documents/ChatGPT/Riskbedömning/docs/superpowers/specs/2026-10-21-kravstod-och-tjansteexponering-design.md).
- Koden på `feat/steg-1-3`, lokalt `288fa66`.

## Slutsats

**Godkänn med ändringar.** Riktningen är rätt och avgränsningen bra:
- inget obligatoriskt kundregister
- ingen V9
- ingen ny riskvikt utan beslut
- planresultat skilt från aktuell bedömning
- inga nya uppgifter till AI.

Alla fil- och fältreferenser i planen finns i koden. Fyra saker behöver ändras före genomförandet. Den första blockerar.

## 1. Fel kodbas (blockerande)

Planen utgår från `feat/steg-1-3` på `688629f`, som är grenens läge på GitHub. Lokalt har grenen tio commits till som inte är pushade:

| Commit | Innehåll | Berör |
|---|---|---|
| `5c8e96f`, `4827095`, `4f69288` | Provkörda metodalternativ för D6 och D9, med rättningar | Uppgift 2 |
| `74c0b12`, `23932aa` | Beslutsformulär med åtta jämförelsepar och precisering inför steg 4 | Uppgift 2 |
| `2014557`, `b50ca76` | Mätverktyg för rapportens längd och upprepning | Uppgift 5, 7 |
| `8fd6116`, `cda6f80` | Gemensamt faktaunderlag (D-ARB.5), källnot, deterministisk källnot | Uppgift 5 |
| `288fa66` | Motortabeller flyttade till B1; nivårad och avgörande skäl kvar i läsrapporten | Uppgift 5 |

Uppgift 5 ändrar just `nivamotivering_v8.py`, `tjanstavsnitt_v8.py` och `operationskarta_v8.py`, som dessa commits redan har ändrat. Uppgift 2 föreslår ett beslutsprotokoll, men beslutsformuläret med åtta par, svarsmall och förväntad nivå per mått finns redan.

**Åtgärd:**
- Pusha grenen och lås basen till `288fa66`.
- Uppgift 0 ska verifiera alla 13 commits, inte bara tre.
- Uppgift 2 ska återanvända `docs/superpowers/reviews/2026-10-21-beslutsformular-jamforelsepar.md` och lägga planfallet och gruppfallet till som par i det, i stället för att skapa ett nytt protokoll.
- Uppgift 5 ska utgå från `dokument/gemensamt_v8.py` och den nya placeringen av beräkningsspåren i B1.

## 2. Uppgift 3 är underskattad och bör delas

**Hela kedjan förutsätter `bedomningar/`.** `BEDOMNINGAR` används på 23 ställen i 8 filer, bland annat i skrivning, lokal analys, granskning och fastställelse. Uppgift 7 kräver kedjan "plan → planeringsbedömning → lokal analys → rapport". Det betyder att hela V8-kedjan måste kunna köras på en bedömning i `forandringsbedomningar/`. Det är ett stort ingrepp som planen inte redovisar.

**Det föreskrifterna kräver är mindre än så.** 2 kap. 3 § kräver att den allmänna riskbedömningen *utvärderas* innan en ny eller väsentligt ändrad tjänst, en ny marknad eller en annan relevant förändring införs. Samma lydelse finns i 12FS 2024:8 (Skåne) och 01FS 2024:20 (Stockholm). Mitt förslag är att dela uppgiften:

- **3a, planpost och bunden utvärdering (litet, uppfyller kravet).** `Tjansteplan` registreras. En historikhändelse av typen utvärdering får `plan_id` och `plansumma`. En grind kräver en genomförd, bunden utvärdering innan erbjudandet ändras till ja för en tjänst med registrerad plan. `registrera_utvardering` hindrar redan framtida datum.
- **3b, planeringsbedömning med motorn (större, kan vänta).** Planens motorutfall redovisas som ett eget avsnitt, *Planerade förändringar*, i den ordinarie rapporten eller i ett kort separat dokument, inte genom hela V8-kedjan med skrivning, analys och granskning.

**Planen behöver säga vad planeringsbedömningen faktiskt visar.** Motorn läser inte tjänstespecifika uppgifter (mandat, fördelning, insyn) förrän D3 är beslutat. Planeringsbedömningen blir därför katalogens grundnivå plus byråns befintliga faktorer, alltså samma resultat som om tjänsten redan erbjöds. Planens egna uppgifter syns i underlaget men påverkar inte nivån. Det behöver stå uttryckligen, så att resultatet inte uppfattas som mer anpassat än det är.

**Ange vilka fält en plan får ersätta.** En ny marknad ändrar typiskt byråns geografi (`P-GEO.*`), inte tjänstens egna fält. Planen bör ange om `Tjansteplan.uppgifter` får innehålla byråfält och hur de skiljs från verkliga uppgifter i planeringsvyn.

## 3. Uppgift 5 riskerar att förlänga läsrapporten igen

Förklaringen "uppgift → sårbarhet → hot → nivå" behövs (krav 24). Om den skrivs per faktor och per tjänst återkommer dock den upprepning som just tagits bort. Läsrapporten gick från 14 573 till 12 354 ord i provfallet med betalningsmandat.

**Åtgärd:**
- Faktorns mekanism (varför den gör utnyttjandet möjligt, och vilken källa som stöder det) skrivs en gång i det gemensamma faktaunderlaget, som faktordefinition.
- Tjänsten anger bara den lokala betydelsen och utfallet för sina scenarier.
- Acceptansvillkoret ska innehålla en mätning med `docs/research/verktyg/rapportmatning.py` före och efter: ord i läsrapport och bilaga, samt ordagrann upprepning mellan tjänster. Ingen hård gräns, men en ökning ska redovisas och motiveras.

## 4. Mindre saker

- **Python-version.** Testkommandona använder `.venv/bin/pytest`. Med Python 3.14 fallerar `test_8_djupt_scb_svar_ger_atgarderbart_fel` av versionsskäl. Ange en stödd miljö (3.12) för de körningar som ska räknas som godkända.
- **Uppgift 4.** `population` och `bas_population` måste enligt planen alltid vara lika och är då dubbletter. Behåll ett fält, eller ange vad en skillnad skulle betyda. Notera också att en ny eller ändrad grupp ändrar profilrevisionen. Det kräver ny bedömning och förnyad analysbindning, vilket stämmer med granskningsfokus 4, men bör stå i uppgiften.
- **Uppgift 7.** "documents-skillen och dess bundled runtime" är ett verktyg i Codex miljö. Skriv i stället "projektets renderingskedja (LibreOffice/Poppler) eller motsvarande".
- **Uppgift 1 bör kunna ändra uppgift 3–5.** Planen säger att inga luckor antas i förväg, men 3–5 är redan specificerade. Låt kravmatrisen få avgränsa eller skjuta upp dem om den visar att en lucka är mindre än antaget.

## Föreslagen ordning

0 (bas 288fa66) → 1 (kravmatris) → 3a (plan och bunden utvärdering) → 4 (kombinationsgrupper) → 5 (faktorförklaring i gemensamt underlag) → 3b (planeringsbedömning) → 6 (beslutade metodändringar) → 7 (hela kedjan).

3a går före 4 och 5 eftersom den stänger en lucka mot en uttrycklig föreskrift med en liten ändring.

## Det planen gör bra

- Granskningsfokus 1–5 träffar de verkliga riskerna: planerad tjänst med noll kunder, okänt överlapp, blandade populationer, privata uppgifter och AI, samt gamla godkännanden.
- Uppgift 6 är korrekt villkorad. Inga nya vikter, ingen ny TF-regel och ingen ny sammanvägning införs utan beslut och facit, och D5 krävs innan ett lokalt "ej relevant" får ta bort ett motorscenario.
- Uppgift 1 bygger på regelbasens befintliga kravkarta i stället för en parallell katalog och skiljer tekniskt stöd från byråns faktiska arbete (krav 31–32).
- Kombinationsgrupperna skiljer noll från okänt och summerar inte överlappande grupper.
