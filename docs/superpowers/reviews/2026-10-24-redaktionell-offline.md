# Redaktionell offlineförhandsvisning – kontrollpunkt 1

Status: redo för användarens PDF-granskning. **Riktmärket tio sidor är inte nått. Produktkedjan och sakkunnigpaketet är inte anpassade ännu.** Ingen push eller merge.

Bas: `d8a91a1bd91be0a47c3d8d0b767e5139ee404e71`, regelbas 2.12.2. Uppdrag: `/Users/danieltrogen/riskanalys-steg1-3/docs/superpowers/reviews/2026-10-24-uppdrag-codex-redaktionell-runda.md`.

## Filer att läsa

Granskningsmapp: `/Users/danieltrogen/Documents/ChatGPT/Riskbedömning/underlag/redaktionell-offline-2026-10-24/`.

| Referensfall | Resultatrapport | Bilaga A | Bilaga B1 | Tidigare R/A/B1 |
|---|---:|---:|---:|---|
| Fyra tjänster | 19 | 42 | 199 | 20/38/195 |
| Med betalningsmandat | 19 | 45 | 204 | 21/40/200 |

Varje fall innehåller `allman-riskbedomning-UTKAST.pdf`, `analysbilaga-UTKAST.pdf` och `underlagsbilaga-UTKAST.pdf`, samt `flyttregister.md`, `transformationer.json` och `pdfkontroll.json`. `SHA256.json` binder kopiorna. Alla sex PDF-kopior är byteidentiska med de visuellt granskade filerna i evidensmappen.

- [Fyra tjänster: varje flytt med originaltext, källa, mål och summa](/Users/danieltrogen/Documents/ChatGPT/Riskbedömning/underlag/redaktionell-offline-2026-10-24/fyra_tjanster/flyttregister.md).
- [Betalningsmandat: varje flytt med originaltext, källa, mål och summa](/Users/danieltrogen/Documents/ChatGPT/Riskbedömning/underlag/redaktionell-offline-2026-10-24/med_betalningsmandat/flyttregister.md).

Detta är en separat förhandsvisning, inte ett nytt sakkunnigpaket och inte ett exporterat eller fastställt produktpaket. Historiska filer har inte skrivits om.

## Vad som har ändrats

Formatteraren använder fältkatalogens svenska etikett eller fråga och en fast ordlista för programvärden. Belopp och andelar formateras på svenska. Rollnamn visas i huvudrapporten. Bankinsyn och betalningsmandat har skilda ordlistor så att exempelvis ingen bankinsyn inte blir inget mandat. Fritext skrivs inte om.

Källkodfältet för omvärldsbevakning visas med katalogens faktiska källtitlar. Dess ursprungliga registerpost ligger ordagrant i B1. Okända källkoder stoppas av råvärdeskontrollen; inga titlar gissas. Kontrollen omfattar även tabellrubriker och kolumnrubriker, tjänstekoder, dokumentkoder och källkoder.

| Från huvudrapporten | Fullständigt original finns i |
|---|---|
| Hottabellen och källnyckeln i 2 | B1 E2, Hotregister |
| Period- och källregistret i 1.1 | B1 E3 |
| Fulla tjänstetabellen och arbetsmomenten i 1.2 | A E17 |
| Tjänstevisa erfarenhetsprövningar i 2.1 | A E18 |
| Långa metodförklaringar i 4.1 | A E16 |
| De fyra kataloghotens tidigare tjänstevisa scenariorader | A E19–E34; ny gemensam matris i 4.2 |
| Hela kontrolltabellen i 4.4 | A E35 |
| Upprepad TF-indikatorförteckning i 3.7 | B1 E4; indikatorernas status och fakta står kvar i 3.1–3.5 |
| Omvärldsbevakningens ursprungliga källkodspost i 5.3 | B1 E5 |

De två sista flyttarna gör det möjligt att undvika upprepade långa hot-/indikatornamn respektive källkoder i läsartexten. Varje flytt ingår i samma kontroll som de uttryckligen uppräknade flyttarna i uppdraget.

Per fall har **231 stycken, tabellrubriker, kolumnrubriker och celler** exakt verifierade mål. Tabeller räknas alltså per textdel, inte som en enda flytt. Samtliga måltexter finns även i de renderade Word-filerna. Originalregistret bevarar tekniska uppgifter i bilagorna, som uppdragets råvärdesförbud undantar.

Kataloggrupperingen omfattar fyra hot och 16 medlemskap per fall. Den kräver samma dimension, hotnivå, sårbarhetsnivå, sannolikhet, konsekvens, risk före/efter kontroll, täckande kontroller samt avgörande status före/efter. Hot med en lokal variant grupperas inte. Betalningsmandatets egna lönebetalningsscenarier står därför kvar.

Kontrolltabellen i huvudrapporten innehåller motoravdrag även när scenariot ligger under tjänstens maxnivå, med hänvisning till den lokala prövningen i 4.3. Förklaringarna till ej godtagna sänkningar står kvar där. Motoravdrag framställs inte som lokalt godkända sänkningar.

## Varför rapporterna fortfarande är långa

De beställda flyttarna och grupperingen är genomförda. Huvudtexten innehåller cirka 6 948 respektive 7 456 ord enligt dokumentmodellen, inklusive tabelltext men exklusive den separata fyndsammanfattningen. Kapitel 3 står för cirka 2 447 ord; kapitel 4 för cirka 2 754 respektive 3 284 ord. Tillsammans är det ungefär tre fjärdedelar av innehållet.

Det som återstår är framför allt faktatabellerna och lagens exempel i kapitel 3, de gemensamma händelsekedjorna, tjänsternas ordagranna lokala PT-/TF-motiveringar och sänkningsförklaringarna. Läsbara fältetiketter och fulla hotnamn tar mer plats än de tidigare koderna. Betalningsmandatet har dessutom egna lokala kedjor som inte får slås ihop med de andra tjänsternas mekanism.

Förhandsvisningen behåller 11 punkters brödtext och minst 9,5 punkters tabelltext i huvudrapporten. Tomma tabellrubriker visas inte och fyndsammanfattningen hålls samman. Inget innehåll kapas för att nå sidmålet. Ytterligare förkortning mot tio sidor skulle kräva ett nytt redaktionellt upplägg för framför allt kapitel 3 och de långa lokala motiveringarna. Denna förhandsvisning ska inte beskrivas som att tiosidorsmålet är uppnått.

## Verifiering och begränsningar

- 16 riktade prov godkända: `/private/tmp/redaktionell-slutprov.log`. Regressionerna har först observerats felande och därefter godkända. De täcker bland annat fritext, svenska värden, koder i rubriker, källtitlar, skilda perioder, scenariogruppering och kontrollavdrag under max.
- Snabbprofil: 140 godkända, 0 fel, 0 överhoppade, verifierat oförändrat snapshot, 57,80 sekunder. Resultat och exakt urval: `/private/tmp/redaktionell-snabb-7/resultat.json`.
- Den faktiska PDF-texten har inga träffar på råvärdesmönstren. Ingen huvudtext ligger utanför sidans gränser enligt ordkoordinatkontroll. 231 flyttar per fall har exakt text/summa på rätt mål. 52 respektive 59 längre originaltexter ur profil/analys som förekom i den gamla huvudrapporten finns kvar ordagrant i paketet. Samtliga fulla PT-/TF-motiveringar står kvar i huvudrapporten.
- Alla 38 huvudsidor är visuellt lästa. Visuellt lästa bilagestickprov: fyra tjänster A 37–42 och B1 113, 114, 116, 117; betalningsmandat A 39, 40, 42–44 och B1 118, 119, 121. Kontroller och sidbilder finns i evidensmappen.
- Källfilerna är byteidentiska med de frysta referenserna. Motorutfallet och den inbäddade regelbasen är oförändrade. `git diff d8a91a1 -- src regelbas pyproject.toml` är tom.
- Regelbasvalideringen gav giltig 2.12.2 utan fel. Ordinarie regelbassumma är fortsatt `sha256:21cf1f9fc25a110f31ce5addc47c133b1ed5689b2ac64b117409e5ce63dcb4c0`. JSON-digesterna i PDF-kontrollfilerna använder separat serialisering och ersätter inte denna regelbassumma.
- Inga verkliga AI-anrop eller verkliga byråuppgifter har använts.
- **Ny fullsvit och samlad slutreview återstår efter produktanpassningen.** Den gamla fullsviten för `d8a91a1` gäller den oförändrade produkten, inte de nytillkomna offlineverktygen/testerna. Detta är en förhandsvisning vid uppdragets första kontrollpunkt, inte slutleverans, PR eller push.

Evidens: `.superpowers/evidens/2026-10-24-redaktionell-offline/kontrollpunkt-1/`. Återskapande:

```bash
env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv312/bin/python \
  docs/research/verktyg/redaktionell_offline.py \
  --fran .superpowers/evidens/2026-10-23-rapport-v10-2.12.2 \
  --ut /private/tmp/redaktionell-nytt-prov
```

Konvertera de sex Word-filerna med LibreOffice till PDF. Sidantalet måste mätas igen vid en annan Word-/PDF-renderare; sidbrytningar kan skilja sig.

## Produktkedjans särskilda beroende

`src/riskanalys/regelverk/metodbeslut.py` binder konservativt samtliga appens Python-filer till D-besluten. En ändring i rapportkoden gör därför filbindningarna inaktuella även om metod och motorutfall är oförändrade. Att skriva om dessa bindningar skulle ändra regelbasens kontrollsumma.

Offlineverktygen ligger utanför appkoden och utlöser inte den konflikten. Innan produktanpassning måste kopplingen redovisas som ett separat tekniskt ändringsförslag. Ingen bindning försvagas, ingen regelbassumma skrivs om och ingen sakkunnigstatus höjs inom denna kontrollpunkt.

Efter användarens PDF-besked återstår produktens versionsbyte/export/samlad sakgranskning/fastställelse, historisk verifiering, läsversion per regelpaket, samlad slutreview och färsk fullsvit. Fullständigt sakkunnigpaket och läsversion paketeras bara på slutet enligt användarens beslut.
