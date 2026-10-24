# Riskanalys

Ett program som tar fram och förvaltar den dokumentation som verksamhetsutövare behöver enligt penningtvättsregelverket: allmän riskbedömning, rutiner och riktlinjer, kundriskmodell, kravmatris och löpande uppföljning. Dokumentationen anpassas till den egna verksamheten, och varje påstående går att spåra till en källa.

Första målgrupp är redovisnings- och konsultbyråer under Länsstyrelsens tillsyn.

> **Status:** M0–M2:s teknik samt det lokala intaget till ett helt Word-utkast är byggda och prövade med syntetiska uppgifter. Regelbas 1.1.0 är ännu inte sakkunniggranskad; modellutvärdering och användningsprov med en riktig byrå återstår. Se [docs/STATUS.md](docs/STATUS.md).

## Dokumentation

| Dokument | Innehåll |
|---|---|
| [Start och länkad projektöversikt](docs/START.md) | Ingång för Obsidian, Codex och Claude Code; områden, filkort och kommandon |
| [Programkarta och fullständigt filregister](docs/PROGRAMKARTA.md) | Filansvar, grupper, importkopplingar och flödet från intag till Word och fastställelse; uppdaterad 2026-10-24 |
| [Designspecifikation](docs/superpowers/specs/2026-10-08-riskanalys-design.md) | Föreslagen struktur, datamodell, riskmetod, AI-lager, granskning och etapper |
| [Research](docs/research/README.md) | Källmaterial, kravkarta, tillsyn och sanktioner, EU-regelverk, metod, teknik och referensdata |
| [Tillsynsmaterial och granskningsfall](docs/research/09-tillsynsbeslut-2026.md#bevarat-underlag-och-återanvändbara-granskningsfall) | Bevarade original utanför repot och syntetiska fall med förväntade fynd för bygget och utvärderingen |
| [Status](docs/STATUS.md) | Framsteg, beslut och nästa steg |

## Princip i korthet

```
Källor ─► Kravregister och kataloger ─► Regelpaket
                                            │
Byråprofil ─────────────────────────────────┤
                                            ▼
                                       Riskmotor ─► AI-skribent ─► Granskare ─► Export och fastställelse
                                            ▲                                          │
                                            └──────────────── Drift ◄──────────────────┘
```

- Risknivåer räknas fram av regler, inte av AI.
- AI skriver text inom ett låst schema och måste hänvisa till regelbasen.
- En granskare kontrollerar täckning och spårbarhet och letar efter de brister som tillsynen oftast påtalar.
- En ansvarig person sakgranskar varje avsnitt innan något fastställs. Ett fastställt paket låses med kontrollsummor.

## Kom igång

Kräver **Python 3.12.15** och **uv 0.13.5** på macOS/Linux (fillås med `fcntl`). Python 3.13+, Windows och fjärrkörd CI är inte verifierade genom den lokala kontrollen. Byråns uppgifter sparas i `$RISKANALYS_DATA` (standard `~/RiskanalysData`), aldrig i repot.

```bash
uv python install
uv lock --check
UV_PROJECT_ENVIRONMENT=.venv312 uv sync --locked --extra dev
.venv312/bin/lint-imports
.venv312/bin/python scripts/testa.py snabb --ut /private/tmp/riskanalys-snabb-NYTT_ID --budget 300
.venv312/bin/riskanalys regelbas validera
```

Installera den angivna uv-versionen från det officiella paketet `uv==0.13.5` om verktyget saknas. Prova exakt synk i en ny miljö först; `uv sync` kan ta bort paket som inte tillhör den valda miljödefinitionen. Full verifiering och områdesprofiler beskrivs i [testguiden](docs/testning.md).

### API-nycklar

Programmet läser nycklar från `~/.config/riskanalys/.env` när ett kommando startar. Filen ligger utanför repot så att den inte kan committas eller läsas av verktyg som arbetar i projektmappen. Följande variabler stöds; ange bara de tjänster du använder:

```text
ANTHROPIC_API_KEY=din-anthropic-nyckel
RISKANALYS_SCB_API_KEY=din-scb-nyckel
BOLAGSVERKET_CLIENT_ID=ditt-client-id
BOLAGSVERKET_CLIENT_SECRET=ditt-client-secret
```

Filen får bara vara läsbar för dig (`chmod 600`); annars stoppar programmet och säger hur du rättar det. En variabel som redan är satt i terminalen gäller före filen. `RISKANALYS_NYCKELFIL` pekar ut en annan fil vid behov. Provsviten läser aldrig den riktiga filen. Nyckelvärden visas inte i felmeddelanden.

### Bolagsverket: lokalt företagsuppslag

Efter att du fått tillgång till Värdefulla datamängder och sparat anslutningsuppgifterna ovan:

```bash
.venv/bin/riskanalys bolagsverket ORGANISATIONSNUMMER
```

Ersätt `ORGANISATIONSNUMMER` med en juridisk persons organisationsnummer. Kommandot visar registeruppgifter och lista över tillgängliga årsredovisningar. Token hämtas och förnyas automatiskt i minnet; spara ingen access token i `.env`. Nycklar skickas bara till Bolagsverkets tokenadress. Inga filer eller profilsvar sparas och ingen AI anropas. Den första versionen är ett separat läskommando; knappen i intaget använder fortfarande SCB. Årsredovisningsfiler laddas inte ner och bokslutstal tolkas inte ännu. Se [verifierat kontrakt och uppgiftskarta](docs/research/10-kallkontroll-och-gapinventering-m2.md#145-bolagsverket-hvd-verifierat-kontrakt-och-första-läsväg-2026-10-14).

### Börja med intaget

`pilotbyra` används som exempel-ID. Har du redan startat intaget med ett annat ID, fortsätt med det för att behålla dina sparade svar.

```bash
.venv/bin/riskanalys intag pilotbyra
```

Webbläsaren öppnas med ett formulär på den egna datorn. Börja med län, filial och bedömningsdatum. Programmet frågar därefter efter fakta om organisation, tjänster, kunder, kanaler, geografi, erfarenheter, rutiner och kontrollbelägg. Följdfrågor visas för de tjänster som erbjuds. Källa, bekräftare och statistikperiod sparas med svaret; andelar beräknas automatiskt.

- **Spara och återuppta:** svaren sparas direkt. Avsluta med Ctrl+C och kör samma kommando igen. Välj *Vet inte* för sådant som ska kompletteras. Ett tidigare svar med källa och period bevaras som historiskt underlag; det används först när det bekräftats igen.
- **Rätta:** översikten visar sparade svar. Ändrade grunduppgifter gör berörda följdsvar inaktuella; en äldre flik kan inte skriva över nya svar.
- **Underlag:** för enkla verksamhetsfakta kan du välja *Egen kännedom om verksamheten*. Relevanta tidigare underlag kan väljas igen; statistikperiod föreslås från aktuell kundbas respektive omsättning. Statistik och kontrollgenomförande behöver fortsatt ett konkret underlag. Kontrollera alltid att det valda underlaget gäller det nya svaret.
- **Samlade frågor:** intervjun samlar närliggande frågor på samma sida. Ange gemensamt underlag, eventuell period och funktion en gång och bekräfta de ifyllda svaren tillsammans. Befintliga svar lämnas oförändrade som standard; välj *Spara ifyllt svar med gruppen* för att ändra eller bekräfta dem igen. Tomma fält hoppas över. *Vet inte* kan väljas per fråga med en egen kompletteringsnotering. Använd länken vid frågan om den behöver ett eget underlag. Alla svar i sparningen sparas tillsammans eller inte alls. Gruppöversikten finns under **Samlade frågor**.
- **Skriv:** när underlaget räcker blir *Skapa allmän riskbedömning som Word-utkast* tillgängligt. Knappen kör bedömning, skrivning, granskning och Word-export. Utkastet omfattar verksamhet, risker per tjänst, kontroller och åtgärder; en granskningsbilaga följer med vid öppna fynd. Separata rutindokument och individuella kundriskbedömningar skapas inte av detta intag. AI-nyckeln `ANTHROPIC_API_KEY` behövs endast för detta steg. Anrop kan kosta pengar.
- **AI-skrivning:** fem analysdelar skrivs per tjänst från ett skyddat faktablad. Programmet skriver tal, nivåmeningar och låsta stycken; AI skriver analys och motivering. En underkänd del körs om högst två gånger. Därefter används en mall och ett fynd som blockerar fastställelse, medan Word-utkastet fortfarande kan granskas. Ändrad text, underlag eller dokumentformat kräver ny granskning. CLI-kommandot `skriv` redovisar anrop och token inklusive cache; modell och design är preliminära inför sakkunnig utvärdering.
- **Datagräns:** namn och beskrivande fritext sätts in lokalt och skickas inte till AI. AI skriver utifrån tillåtna strukturerade uppgifter och kataloger; den analyserar inte fritexten. Andra riskförhållanden utanför modellen måste hanteras innan ett helt utkast kan skapas.
- **Uppföljning:** en faktisk utvärdering registreras uttryckligen med datum och beskrivning. Det räknas inte automatiskt som genomfört när formuläret fylls i. Befintligt utkast kan då omexporteras utan ett nytt AI-anrop.

Intaget stöder nu regelbasens elva redovisnings-, skatte- och bolagstjänster. Det väljer tillsynspaket för VG, Skåne eller Stockholm utifrån län och filial. Annan yrkesroll eller verksamhet utanför regelstödet ger ett hinder. Stöd för varje tänkbar byrå eller juridisk verksamhet är inte verifierat.

Översikt utan webbläsare:

```bash
.venv/bin/riskanalys intag pilotbyra --oversikt
.venv/bin/riskanalys intag pilotbyra --utan-browser
```

### Efter utkastet

För att jämföra effort i AI-piloten, kör mot samma oförändrade bedömning av den syntetiska byrån (här med ID `syntetisk`):

```bash
.venv/bin/riskanalys skriv syntetisk --modell claude-sonnet-5-5 --effort medium
.venv/bin/riskanalys skriv syntetisk --modell claude-sonnet-5-5 --effort high
```

Varje körning sparas separat med vald effort i manifestet och faktisk effort, stoppskäl och token per försök. Delanrop använder 64 000 token och strömning. Ett tokenavbrott hindrar höjning av effort i delens sista omförsök. Längdgränserna ändras först när pilotens jämförelse ger underlag för det.

Programmet skriver dokumentet. Byrån bekräftar fakta, sakgranskar texten och beslutar om fastställelse. Öppna AI-frågor, saknade belägg och ogrundade avvikelser från sektorns risk hindrar fastställelse. Befintlig lokal sakkunnigmotivering kan läggas in frivilligt inför utkastet; detta undantar inte den senare sakgranskningen.

Efter ändringar i den lokala verksamhetsanalysen: välj **Uppdatera Word-utkast utan nya AI-anrop** i översikten. Programmet granskar underlaget på nytt och bygger en ny Word-fil från befintlig AI-text. Det gamla utkastet kan inte laddas ner som aktuellt om analysen har ändrats, tillkommit eller tagits bort. Ett första utkast får fortfarande skapas innan lokal analys finns. Ändrade verksamhetsfakta kräver en ny skrivning.

Bedömningen sparar också identiteten för den beräknande modellen. Har motorn ändrats, eller är bedömningen från en äldre version som saknar denna bindning, behöver du köra `riskanalys bedom` och fortsätta kedjan på nytt. En ren presentationsändring kräver ingen ny bedömning. Tidigare frysta paket kan fortfarande läsas och verifieras som historik.

Sakgranskning och fastställelse har ännu CLI-flödet:

```bash
.venv/bin/riskanalys sakgranska pilotbyra --avsnitt D-ARB.6.1
.venv/bin/riskanalys faststall --help
```

`faststall` vägrar så länge regelpaketet inte är sakkunniggranskat enligt projektets kvalitetsskydd. Programmet är ännu inte verifierat för skarp användning; M3:s modell-/tillsynsutvärdering och M4:s pilot, installations- och driftprov återstår. Dokumentimport är ett senare stöd, inte ett krav för att börja.

## Ansvar

Programmet ger underlag. Verksamhetsutövaren fastställer dokumentationen och ansvarar för att regelverket följs.

### Avgiftsfri registerhämtning i intaget

Välj **Företagsuppgifter** i intaget. Ange organisationsnummer och välj **Hämta valda företagsuppgifter**. Välj även Bolagsverket för grunduppgifter och senaste digitala årsredovisning; valet är förmarkerat när båda Bolagsverksnycklarna är konfigurerade. Kontrollera namn/nummer, jämför registerförslagen med egna svar och bekräfta de uppgifter som ska användas. Hämtningen ändrar inga svar automatiskt. Namn, säteslän och registrerade arbetsställen kan godkännas tillsammans och följa med redan vid starten. Avvikande sparade svar kräver ett särskilt ersättningsval. Du kan också fortsätta manuellt. Filial kan föreslås från Bolagsverkets organisationsform AB/FL. Utan ett valt sådant förslag behövs eget filialunderlag; SCB-bilden styrker inte filialsvaret.

SCB:s [AFR-API](https://www.scb.se/vara-tjanster/bestall-data-och-statistik/foretagsregistret/avgiftsfria-uppgifter-i-foretagsregistret/) är avgiftsfritt men kräver personlig nyckel. Registrera dig i [SCB:s portal](https://registreraafr.scb.se/) och godkänn deras villkor själv. Programmet skapar inga konton. Enklast: öppna **Ange eller byt SCB-nyckel** i det lokala hämtningsformuläret och klistra in nyckeln i lösenordsfältet. Den används bara i sessionen och sparas inte på disk. Alternativt i macOS/zsh kan nyckeln anges utan att dess värde skrivs i terminalhistoriken:

```zsh
read -rs 'RISKANALYS_SCB_API_KEY?SCB-nyckel: '
export RISKANALYS_SCB_API_KEY
.venv/bin/riskanalys intag pilotbyra
unset RISKANALYS_SCB_API_KEY
```

Nyckeln ska inte skrivas i chatt, Git eller vanliga svarsfält. Använd bara det avsedda lokala lösenordsfältet eller miljövariabeln. Tills åtkomst finns kan du fortsätta manuellt eller klistra in innehållet från en redan hämtad SCB-JSON-fil (`juridiskaenheter/.../full`). Den importen märks **ursprung ej verifierat**. Första kopplingen stöder juridiska personers organisationsnummer; enskild firma besvarar intaget manuellt utan personnummer i registerformuläret.

| Uppgift | Användning |
|---|---|
| Namn och säteslän | Förslag att kontrollera och bekräfta. Län och filial styr regelpaket. |
| Registrerat arbetsställeantal | Förslag att kontrollera mot faktiska arbetsställen. |
| Ägarkategori 41: privat svenskkontrollerat företag utan koncerntillhörighet | Villkorat förslag ”nej” på yttersta moderföretag. Kräver kontroll och uttrycklig bekräftelse; andra/saknade koder ger inget sådant förslag. |
| SNI, juridisk form och registerstatus | Bakgrund; avgör inte faktiska tjänster eller risknivå. |
| Anställdas klass, omsättningsklass och omsättningsår | Bakgrund; ersätter inte exakta personer inklusive ägare eller aktuell omsättning/period. |
| Kunder, tjänsteomfattning, kanaler, länder, befogenheter och kontrollgenomförande | Frågas fortfarande från byrån och dess underlag. |

Minimala registerbilder sparas privat i `$RISKANALYS_DATA/<byra>/register/`, med källa, tid och kontrollsumma. Hämtningstid är inte senaste ändringsdatum. Tidigare bilder bevaras; ta med mappen i säkerhetskopian. En bekräftelse refererar exakt bild i profilsvarets källa. Vid fel eller konflikt ska uppgiften kontrolleras; en aktuell registerbild får inte styrka en tidigare bedömningsdag. Hämtning/import efter bedömningsdatum avvisas och den tidigare bilden behålls. En ny bedömning med nytt datum behöver ett separat intag. Bekräftade ändringar använder profilens vanliga validering, följdfrågor och skydd mot gamla flikar. Rårespons, nycklar och registeridentitet går inte till AI.

Utvidgad [datakällsresearch](docs/research/10-kallkontroll-och-gapinventering-m2.md#142-utvidgad-research-mindre-manuell-inmatning-2026-10-10) visar vilka uppgifter som kan hämtas, importeras och behöver bekräftas. Lokal import av aggregerad kund-/uppdragsstatistik är nästa föreslagna förenkling. Bolagsverket HVD kan nu komplettera SCB i samma intagsflöde. Allabolag eller ekonomisystem kräver ett separat verifierat åtkomst- och integrationssteg. Den nya SCB-kopplingen är testad med syntetisk transport; autentiserat uppslag kräver en personlig nyckel och är inte verifierat här.

**Färre upprepningar i intaget:** **Byråns tjänster** samlar elva erbjudandefrågor med gemensam källa, roll och datum. Markera faktiskt erbjudna tjänster och bekräfta hela listan innan omarkerade blir ”nej”; använd enskilda frågor med ”Vet inte” när underlaget är osäkert. Vanliga frågor föreslår tidigare roll, och godkända registerförslag hoppar över motsvarande frågor. Registerbakgrund med bransch/storleksklasser samt F-skatt/moms/arbetsgivarstatus är expanderbar. De sistnämnda visas efter en ny SCB-hämtning; äldre bilder bevaras. [Ny källkontroll och avgränsning](docs/research/10-kallkontroll-och-gapinventering-m2.md#143-ny-källkontroll-och-förenklat-godkännande-2026-10-11).

[Fler källor och återanvändning av underlag](docs/research/10-kallkontroll-och-gapinventering-m2.md#144-fler-källor-underlagsval-och-tydlig-leverans-2026-10-11): Bolagsverket kan tillföra registrerad verksamhet, organisationsform och tillgängliga digitala årsredovisningar efter separat API-åtkomst. Polisen/Länsstyrelserna samt EU/FATF ger riskunderlag som behöver versionshanteras och granskas. Bolagsverket har både ett separat läskommando och samlad intagshämtning; övriga nämnda källor är inte nya byggda anslutningar. Pilotbyråns egna exporter inventeras i det manuella pilotintaget före en formatanpassad CSV/XLSX-import.

### Bolagsverket och bokslut i samma godkännande

Med `BOLAGSVERKET_CLIENT_ID` och `BOLAGSVERKET_CLIENT_SECRET` i den privata nyckelfilen kan intaget komplettera SCB med filialförslag, registrerad verksamhetsbeskrivning som redigerbart utkast och exakt nettoomsättning. Markera önskade förslag och godkänn dem tillsammans. Bekräfta uttryckligen bokslutets statistikperiod; den måste stämma med redan bekräftad kund-/tjänstestatistik och föreslås för följande statistikfrågor. Även senare svar kontrolleras mot den godkända bokslutsperioden. Vid periodbyte behöver omsättningen först uppdateras med rätt underlag.

Årsredovisningsläsaren stöder iXBRL med `gen-base/2021-10-31`, odimensionerad bolagskontext och SEK. Den kontrollerar identitet, period, skala/precision och motstridiga dubbletter. Andra taxonomier, koncernkontexter, enbart avrundade belopp eller flera dokument för senaste period ger inget automatiskt beloppsförslag. Grundförslagen kan ändå användas och begränsningen visas. Medelantal anställda visas som stöd; dagens antal inklusive ägare besvaras fortfarande manuellt.

Originalpaketet sparas privat i `$RISKANALYS_DATA/<byra>/register/original/<sha256>.zip`. Registerschema 4 binder Bolagsverksfakta och bokslut till samma juridiska person; äldre SCB-bilders format och kontrollsummor bevaras. Källan följer respektive fält och får inte återanvändas som belägg för andra verksamhetsfakta. Hämtning bekräftar ingenting och gör inga AI-anrop.


### Säkerhetskopiering och återställning

Två separata fall behöver skyddas: låsta versioner i `faststallda/vN` och hela den pågående privata arbetsmappen med profil, analys/belägg, register, skrivsvar, historik och attester. Stoppa alla skrivande CLI-/webboperationer före en arbetsmappskopia. Kopiera inte bara rapportfilerna. De interna låsen för profil → analys → drift skyddar dessa register; de utgör ingen generell backuptransaktion för alla filer.

Kopiera till en separat, åtkomstskyddad lagringsplats utanför originalets disk och verifiera att kopian går att läsa. Återställ till en **ny datamapp**, behåll den skadade ursprungskopian och kör `riskanalys verifiera <byra> <version>` med `RISKANALYS_DATA` riktad mot den återställda mappen. Ett låst V10-paket innehåller sin frysta regelbas och tre rapportdelar; verifieringen ska inte köra AI eller bygga om Word. Ett checksummefel kräver återställning av hela den berörda versionen från en känd giltig kopia.

För pågående arbete ska också profil-/analysrevision, privat beläggsinnehåll, historik och sakgranskningar jämföras med den konsistenta kopian. Äldre underlag som används med ny kod måste prövas mot aktuell modellbindning; historiska låsta paket verifieras mot sina egna frysta underlag. Ingen sakkunnigstatus följer automatiskt med en ny bindning.

Driftägaren behöver fastställa backupfrekvens, maximal tolererad dataförlust, återställningstid, skyddad lagringsplats och retention. Tekniskt prov: `tester/typfall/test_aterstallning_v10.py`. **Känd produktlucka:** registrering av backup och automatisk varning när sådan saknas är ännu inte implementerad; se A6-B i [robusthetsplanen](docs/superpowers/plans/2026-10-24-robust-programstruktur.md). En passerad manifestkontroll ersätter inte detta krav.


Ett preliminärt driftförslag är arbetsmappskopia varje arbetsdag, extra kopia efter fastställelse, högst en arbetsdags förlorat pågående arbete och återställning inom fyra arbetstimmar. Preliminär rotation: 30 dagliga och 12 månadskopior, med separat beslutad bevarandepolicy för låsta paket. Prova återställning månadsvis och efter systembyte. Detta är lokala förslag för driftägarens beslut. [Google SRE:s återställningsprinciper](https://sre.google/sre-book/data-integrity/) stödjer att välja återställningstid och accepterad dataförlust uttryckligt; de anger inte dessa projektspecifika tal.
