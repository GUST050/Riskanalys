# Granskning av implementationen av kravstöd och tjänsteexponering

Granskare: Claude Code, 22 oktober 2026.

Granskat material:
- `codex/kravstod-tjansteexponering`, HEAD `a7f9377`, i Codex lokala klon.
- Koden i `bd8577f` jämförd med `8915f0d`.
- Slutprovet `docs/superpowers/reviews/2026-10-21-kravstod-slutprov.md`.

Regressionstest: [`kravstod-granskning-2026-10-22/test_planens_livslopp.py`](kravstod-granskning-2026-10-22/test_planens_livslopp.py).

## Slutsats

**Rätta det allvarliga felet före integration.** Planerna, spärren mot nytt införande, rättelsevägen och kombinationsgrupperna är i övrigt omsorgsfullt gjorda. Integritetsgränsen mot AI är provad på riktigt, och slutprovet redovisar gränser och längdökning öppet.

## Testkörning

| Körning | Utfall |
|---|---|
| Hela sviten, Codex klon, `.venv312`, Python 3.12.15 | 3 009 godkända, 1 fel, 1 livetest bortvalt, 1 663 s |
| Det felande testet `tester/intag/test_webb.py::test_okanda_vagar_och_stor_kropp` | 5/5 godkända på `a7f9377` och 5/5 på `288fa66` vid omkörning |

Felet ("Broken pipe" vid en mycket stor förfrågan) beror på tidsordningen mellan server och klient och är inte orsakat av ändringen. Det är skillnaden mot Codex 3 010 godkända.

## Allvarligt: en införd plan spärrar fastställelsen för all framtid

`faststallelse/grindar.py:_drift` anropar `forandringshinder(rb, profil, profil, historik, beslutsdatum)`. Det kräver en aktuell bunden utvärdering för *varje* plan som hör till en erbjuden tjänst. Samtidigt gäller:

- Planer får inte raderas (`profil/forandringar.py:spara_andring`).
- `plansumma` binder byrån inklusive bedömningsdatum, regelbasens kontrollsumma och alla aktuella uppgifter i `P-GEO`, `P-KUND`, `P-KANAL` och `P-RISK`.

En korrekt genomförd plan blir därför inaktuell vid nästa årliga bedömning, vid varje ändring av byråfakta och vid varje ny regelbasversion. Därefter spärrar den fastställelsen tills planen utvärderas igen, och så vidare utan slut. Meddelandet säger dessutom "före förändringen", fast förändringen redan är genomförd.

**Verifierat med Codex egna testhjälpare:**

| Läge | `forandringshinder` |
|---|---|
| Införande med bunden utvärdering | `()` (korrekt) |
| Fastställelse samma år | `()` (korrekt) |
| Fastställelse nästa år, bara nytt bedömningsdatum | **spärr** |
| Fastställelse efter ändrat kundantal | **spärr** |
| Fastställelse efter ny regelbasversion | **spärr** |

**Förslag till rättning:** ge planen ett livslopp. När erbjudandet ändras med en giltig bunden utvärdering, eller när en ändringsplan genomförs, blir planen *genomförd* och utvärderingen *historisk*. En genomförd plan kontrolleras inte mot aktuella fakta. Den ingår i stället i den ordinarie årliga utvärderingen. Bara planer som inte är genomförda ska spärra.

Genomförandet kan registreras uttryckligen, till exempel som en historikhändelse eller ett statusfält i planen. Det bör inte härledas ur datum, eftersom ett återkallat och sedan återinfört erbjudande annars blir tvetydigt.

**Regressionstestet** innehåller sju fall. Fyra fallerar på `a7f9377`: nästa år, ändrade byråfakta, ny regelbas, och felstavningen nedan. Tre skyddar befintligt beteende och går igenom i dag: samma år, en ännu inte genomförd ändringsplan som fortfarande ska spärra, och en plan som ändras före införandet och då kräver ny utvärdering. Kör testet så här:

```
cp docs/superpowers/reviews/kravstod-granskning-2026-10-22/test_planens_livslopp.py tester/enhet/
.venv312/bin/pytest -q tester/enhet/test_planens_livslopp.py
```

## Mindre allvarligt

### Läsrapporten blev längre

Läsrapporten blev 687 ord längre (+5,6 %) i båda provfallen. Ordagrann upprepning mellan tjänsterna är i stort sett oförändrad (973 → 968).

- **Standardtext.** 184 av de 371 nya orden i D-ARB.5 är samma mening på 23 ord, upprepad för var och en av åtta faktorer ("Aktivering i motorunderlaget är inte i sig bekräftad exponering. Tjänstens lokala prövning …"). Skriv den en gång före listan.
- **Mekanismen förklarar inte kopplingen till hotet.** `gemensamma_faktormekanismer` väljer `s.beskrivning` före `s.metodmotivering`. Beskrivningen är en kort mening, till exempel "Utkontraktering kan begränsa överblick och ansvarsfördelning; byråns ansvar kvarstår", som inte säger hur faktorn gör hotet möjligt. Det var syftet med uppgift 5 (uppgift → sårbarhet → hot → påverkan). Använd `metodmotivering` när den finns, och visa vilka hot faktorn möjliggör med namn.
- **Den lokala texten är en kodlista.** `lokala_faktorskal` ger till exempel "S-ARB-18: relevant (H-TJ-01/PT, H-03/PT, H-01/PT, H-03/TF); S-KUND-01: relevant (…)". Det upprepar beräkningsspåret i B1 och är ingen förklaring för en läsare. Använd faktorns och hotens namn och den lokala motiveringen, eller hänvisa bara till sårbarhetsprövningen om den redan säger det.

### Felstavning i rapporttexten

`dokument/nivamotivering_v8.py`, `_ORSAKER['motstridig']`: "byråns **provningar**" i stället för "prövningar". Det ser ut som en oavsiktlig ändring som tog bort å. Inget befintligt test fångar det; regressionstestet ovan gör det.

### Uppgraderingen ogiltigförklarar befintliga analysgodkännanden

`profil.modeller` ingår i `drift/modellidentitet.py:MODELLMODULER`. Den nya profilmodellen ger därför ny modellbindning, och alla befintliga analyser och modellriskunderlag måste förnyas efter uppgraderingen. Det följer projektets regler och nämns i slutprovet, men bör också stå i `docs/STATUS.md` som en uppgraderingsanteckning för användaren.

### Mindre iakttagelser utan krav på ändring

- `profil/forandringar.py:_tidigare_nej` läser alla historiska profilfiler vid varje sparning av ett erbjudande. Det är korrekt men växer med historiken.
- `Erbjudanderattelse.ansvarig` sätts till rollen (`--roll`, standard `FfR`) i CLI, inte en namngiven person. Överväg ett eget fält för ansvarig.

## Det som är bra

- **Spärren mot nytt införande** täcker nej → okänt → ja och äldre aliasfält, och rättelsevägen är bunden till profilrevision och värden före och efter.
- **Planutvärderingar flyttar inte den årliga fristen** (`Historik.senaste_utvardering`).
- **Kombinationsgrupperna** skiljer 0 från okänt, kräver samma period, källa och bekräftelse för antal och bas, och summerar inte grupper som överlappar. Inget kundregister behövs.
- **AI-begäran** jämförs i sin helhet, inklusive omförsök, och ändras inte av privata plan- och gruppuppgifter.
- **De två ändrade befintliga testerna** pekar bara om en monkeypatch till den nya modulen `profil.forandringar`. Beteendet är oförändrat.
- **Slutprovet** redovisar längdökningen, uppskjuten 3b, metodbeslut som återstår och den lokala miljölösningen med `.pth` utan att överdriva.
