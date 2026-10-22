# Plan A inför Claude-granskning

Datum: 2026-10-22. Gren: `codex/kravstod-tjansteexponering` i `/Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys`.

**Status:** Plan A är implementerad och tekniskt slutverifierad, klar för användarens granskning med Claude. Detta dokument är implementerarens redovisning, inte Claudes oberoende granskning. Leverans-SHA registreras efter commit.

**Bas:** `837917253c4d0edc99969bd056f19afd9695a85d`; produktkod före ändringen `91a3ece`. [Godkänd plan A](../plans/2026-10-22-planaterkallelse-och-inforandeval-plan.md), [godkänd design revision 2](../specs/2026-10-22-forenklad-riskbedomning-design.md).

## Resultat och gräns

En aktiv plan kan återkallas med datum, ansvarig och motivering. Återkallad och genomförd plan är oföränderlig historik; de kan inte redigeras, återöppnas eller avslutas på nytt genom import eller vanliga profilsvar. Återkallad plans utvärderingar bevaras men räknas inte som aktuell planutvärdering eller ordinarie årsutvärdering. Terminalt planinnehåll kontrolleras mot sin bevarade innehållssumma, utan nya katalogkrav på gammal historik.

Införandet kräver ett uttryckligt giltigt planval per tjänst. Bara valda ny-tjänst-planer markeras genomförda i samma profilsparning som erbjudandena; ej valda planer förblir aktiva och omfattas fortfarande av prövningen inför fastställelse. Giltig första kartläggning utan införandeavsikt behöver inget planval. Äldre alias och ett historiskt nej kan inte kringgå införandespärren.

Webb och CLI använder samma CAS-/låsgräns. Hela tjänsteurvalet och underlaget bevaras när planval behöver kompletteras. En felaktig rad, revisionskonflikt eller avbruten sparning lämnar inga delvis sparade erbjudanden/genomföranden. Ny CLI är `aterkalla-plan`; `bekrafta --plan PLAN_ID` anger införandevalet. B1 återger återkallelsen och historiska utvärderingar.

Plan B är godkänd men inte implementerad här. Dess sista precisering om kontrafaktisk +1-referens är inskriven i planen; inget stöd för den referensen påstås finnas i den här leveransen. Riskmotor, riskvikter, maxregel, kontrollavdrag, regelbas och tillåtelselista är oförändrade. Ändringen av `profil.modeller` ändrar modellidentiteten och kräver ordinarie ombedömning/förnyelse av aktuella godkännanden; historiska paket bevaras. Teknisk verifiering är ingen ny sakkunnigattest.

## Spårbara prov

Alla tekniska prov använder Python **3.12.15**, syntetiska uppgifter och testleverantör. Inga riktiga API-/AI-anrop.

| Moment | Före rättning | Efter rättning |
|---|---|---|
| Oförändrad bas, plan/historik | 41 passerade, 5,60 s | Referens före A. |
| A1 återkallelse | 16 förväntade fel: saknat återkallelsegränssnitt | 57 passerade inklusive äldre plan-/historikskydd, 2,69 s. |
| A2 uttryckligt planval | 12 förväntade fel: valgräns/preflight saknas | 69 passerade inklusive A1 och äldre skydd, 3,21 s. |
| A3 webb/CLI | 4 förväntade fel, 2 skyddsfall passerade | 95 passerade i riktad webb-/CLI-/plan-/historikrunda, 28,55 s. |
| Modellbindning | Ny regression föll på oregistrerat `profil.text`-beroende | Modellbindning/XML/V8: 63 passerade, 29,26 s. |
| Formuläretiketter | Ny regression föll på delade datum-/ansvarig-ID:n | Hela nya webbmodulen och privat AI-begäran inklusive omförsök: 8 passerade, 18,63 s. |

Den första webb-RED-körningen nekades loopbackåtkomst (6 miljöfel); den räknas inte som reproduktion av produktfel. Körningen upprepades med tillstånd innan implementationen.

Fullsvit 1 avbröts efter 95,45 s med 24 testfel, 111 uppsättningsfel och 622 passerade. Orsaken var den nya importen från profilmodellen till textkontrollen, som bröt den avgränsade modellfilförteckningen. Textkontrollen flyttades till livsloppsflödet; modellfilförteckningen breddades inte. Ny regression sågs falla och därefter passera.

Fullsvit 2 avbröts inför etikettfixen efter 395,49 s: 1 677 passerade, ett bortvalt livetest och inga fel före avbrottet. Den räknas inte som slutförd fullsvit. Fullsvit 3 slutfördes med resultatet nedan före leveranscommit.

### Slutlig fullsvit

**Slutresultat: 3 063 passerade, ett bortvalt livetest, exit 0, 1 748,27 sekunder.** JUnit innehåller 3 063 testfall, 0 fel, 0 uppsättningsfel och 0 överhoppningar. Alla 416 registrerade Python-/YAML-/testfiler samt pyproject i filförteckningen var byteidentiska före och efter, och inga filer tillkom i det urvalet. Regelbasvalidering och diffkontroll passerar.

Kommando: `.venv312/bin/python -m pytest -q --junitxml=.superpowers/sdd/2026-10-22-planaterkallelse-och-inforandeval-plan/fullsuite.xml`. Rålogg och fryst filförteckning ligger lokalt i samma ignorerade katalog. Regelbasvalideringen gav giltig regelbas 2.0.0, 107 krav och 11 tjänster; kontrollsumma `sha256:7e0f77726a35b5e9fd47b8d324b43236cbeab5ded78c107ccfe54570cc97285f`.

## Visuell kontroll

En syntetisk byrå provades i inbyggd webbläsare mot loopback: två tjänster valdes, saknade planval bevarade båda valen och underlaget, endast `alternativ` och `tva` blev genomförda. `ett` var fortsatt aktiv, återkallades uttryckligen och visades därefter som läsbar terminal historik utan redigerings-/utvärderingsformulär. Skärmbilder finns lokalt som `planval-webb.png` och `planlivslopp-webb.png` i körkatalogen. Den upptäckta etikettkrocken är rättad och skyddad med ett riktigt HTML-prov.

En syntetisk tvådelad V8-export skapades med programmets befintliga exportör och frysta testsvar. Underlagsbilagan renderades med documents-skillens paketerade renderare/LibreOffice till **99 sidor**. Den ändrade plansidan **64** öppnades visuellt: återkallelse, genomförande och historiska utvärderingar visas utan klippning. Detta är riktad kontroll av ändrat innehåll, inte en ny fullständig layoutgranskning av alla 99 sidor. Export och bilder ligger under körkatalogens `rapportprov/`. Ordinarie V8-prov kontrollerar båda dokumentens kontrakt.

## Arbetsbeslut

- Befintlig separat klon på funktionsgrenen återanvändes enligt sessionens arbetssätt. Användarens andra checkout ändrades inte.
- Uppgiftsextraktorn kräver rubriken `Task N`, medan den godkända planen har A1–A3. Exakta avsnitt kopierades därför till lokala uppgiftsbriefar utan att döpa om eller ändra den godkända planen. Ingen beteendeskillnad.
- Den rena webbvisningen lades i en liten ny `intag/planvalsvy.py`, så att tjänstelista och enskild fråga inte får skilda planvalsregler. Avvikelsen gäller filindelning, inte funktion; fel gräns skulle kräva flytt av hjälparen.
- Riktad basverifiering användes före A1, med den tidigare fullsviten som historisk referens. En färsk fullsvit på slutkoden krävs fortfarande före commit och ersätts inte av de riktade proven.

## Fokus för Claude

Granska särskilt terminal historik vid import, historiskt nej/alias, återkallad plans utvärderingar och årsfristen, endast valt genomförande samt atomiken vid fel i andra införanderaden. Kontrollera även att kandidatvisning aldrig i sig sparar ett erbjudande och att UI:s nya jämförelse efter ändrad revision är uttrycklig. Använd den här klonens kod och testhjälpare; gamla granskningstester på en annan gren ska inte av misstag importera en äldre produktmodell.
