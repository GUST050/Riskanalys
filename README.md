# Riskanalys

Ett program som tar fram och förvaltar den dokumentation som verksamhetsutövare behöver enligt penningtvättsregelverket: allmän riskbedömning, rutiner och riktlinjer, kundriskmodell, kravmatris och löpande uppföljning. Dokumentationen anpassas till den egna verksamheten, och varje påstående går att spåra till en källa.

Första målgrupp är redovisnings- och konsultbyråer under Länsstyrelsens tillsyn.

> **Status:** M0–M2:s teknik samt det lokala intaget till ett helt Word-utkast är byggda och prövade med syntetiska uppgifter. Regelbas 1.1.0 är ännu inte sakkunniggranskad; modellutvärdering och användningsprov med en riktig byrå återstår. Se [docs/STATUS.md](docs/STATUS.md).

## Dokumentation

| Dokument | Innehåll |
|---|---|
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

Kräver Python 3.12 eller senare på macOS/Linux (lagringen använder fillås med `fcntl`). Byråns uppgifter sparas i `$RISKANALYS_DATA` (standard `~/RiskanalysData`), aldrig i repot.

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest
.venv/bin/riskanalys regelbas validera
```

### Börja med intaget

`pilotbyra` används som exempel-ID. Har du redan startat intaget med ett annat ID, fortsätt med det för att behålla dina sparade svar.

```bash
.venv/bin/riskanalys intag pilotbyra
```

Webbläsaren öppnas med ett formulär på den egna datorn. Börja med län, filial och bedömningsdatum. Programmet frågar därefter efter fakta om organisation, tjänster, kunder, kanaler, geografi, erfarenheter, rutiner och kontrollbelägg. Följdfrågor visas för de tjänster som erbjuds. Källa, bekräftare och statistikperiod sparas med svaret; andelar beräknas automatiskt.

- **Spara och återuppta:** svaren sparas direkt. Avsluta med Ctrl+C och kör samma kommando igen. Välj *Vet inte* för sådant som ska kompletteras. Ett tidigare svar med källa och period bevaras som historiskt underlag; det används först när det bekräftats igen.
- **Rätta:** översikten visar sparade svar. Ändrade grunduppgifter gör berörda följdsvar inaktuella; en äldre flik kan inte skriva över nya svar.
- **Underlag:** för enkla verksamhetsfakta kan du välja *Egen kännedom om verksamheten*. Relevanta tidigare underlag kan väljas igen; statistikperiod föreslås från aktuell kundbas respektive omsättning. Statistik och kontrollgenomförande behöver fortsatt ett konkret underlag. Kontrollera alltid att det valda underlaget gäller det nya svaret.
- **Skriv:** när underlaget räcker blir *Skapa allmän riskbedömning som Word-utkast* tillgängligt. Knappen kör bedömning, skrivning, granskning och Word-export. Utkastet omfattar verksamhet, risker per tjänst, kontroller och åtgärder; en granskningsbilaga följer med vid öppna fynd. Separata rutindokument och individuella kundriskbedömningar skapas inte av detta intag. AI-nyckeln `ANTHROPIC_API_KEY` behövs endast för detta steg. Anrop kan kosta pengar.
- **Datagräns:** namn och beskrivande fritext sätts in lokalt och skickas inte till AI. AI skriver utifrån tillåtna strukturerade uppgifter och kataloger; den analyserar inte fritexten. Andra riskförhållanden utanför modellen måste hanteras innan ett helt utkast kan skapas.
- **Uppföljning:** en faktisk utvärdering registreras uttryckligen med datum och beskrivning. Det räknas inte automatiskt som genomfört när formuläret fylls i. Befintligt utkast kan då omexporteras utan ett nytt AI-anrop.

Intaget stöder nu regelbasens elva redovisnings-, skatte- och bolagstjänster. Det väljer tillsynspaket för VG, Skåne eller Stockholm utifrån län och filial. Annan yrkesroll eller verksamhet utanför regelstödet ger ett hinder. Stöd för varje tänkbar byrå eller juridisk verksamhet är inte verifierat.

Översikt utan webbläsare:

```bash
.venv/bin/riskanalys intag pilotbyra --oversikt
.venv/bin/riskanalys intag pilotbyra --utan-browser
```

### Efter utkastet

Programmet skriver dokumentet. Byrån bekräftar fakta, sakgranskar texten och beslutar om fastställelse. Öppna AI-frågor, saknade belägg och ogrundade avvikelser från sektorns risk hindrar fastställelse. Befintlig lokal sakkunnigmotivering kan läggas in frivilligt inför utkastet; detta undantar inte den senare sakgranskningen.

Sakgranskning och fastställelse har ännu CLI-flödet:

```bash
.venv/bin/riskanalys sakgranska pilotbyra --avsnitt D-ARB.6.1
.venv/bin/riskanalys faststall --help
```

`faststall` vägrar så länge regelpaketet inte är sakkunniggranskat enligt projektets kvalitetsskydd. Programmet är ännu inte verifierat för skarp användning; M3:s modell-/tillsynsutvärdering och M4:s pilot, installations- och driftprov återstår. Dokumentimport är ett senare stöd, inte ett krav för att börja.

## Ansvar

Programmet ger underlag. Verksamhetsutövaren fastställer dokumentationen och ansvarar för att regelverket följs.

### Avgiftsfri registerhämtning i intaget

Välj **Företagsuppgifter** i intaget. Ange organisationsnummer och välj **Hämta från SCB**. Kontrollera namn/nummer, jämför registerförslagen med egna svar och bekräfta de uppgifter som ska användas. Hämtningen ändrar inga svar automatiskt. Namn, säteslän och registrerade arbetsställen kan godkännas tillsammans och följa med redan vid starten. Avvikande sparade svar kräver ett särskilt ersättningsval. Du kan också fortsätta manuellt. Filialsvaret behöver ett eget underlag, exempelvis registreringsbevis; SCB-bilden används inte som källa till den frågan.

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

Utvidgad [datakällsresearch](docs/research/10-kallkontroll-och-gapinventering-m2.md#142-utvidgad-research-mindre-manuell-inmatning-2026-10-10) visar vilka uppgifter som kan hämtas, importeras och behöver bekräftas. Lokal import av aggregerad kund-/uppdragsstatistik är nästa föreslagna förenkling. Bolagsverket HVD är nästa möjlig avgiftsfri adapter; den är ännu inte implementerad. Allabolag eller ekonomisystem kräver ett separat verifierat åtkomst- och integrationssteg. Den nya SCB-kopplingen är testad med syntetisk transport; autentiserat uppslag kräver en personlig nyckel och är inte verifierat här.

**Färre upprepningar i intaget:** **Byråns tjänster** samlar elva erbjudandefrågor med gemensam källa, roll och datum. Markera faktiskt erbjudna tjänster och bekräfta hela listan innan omarkerade blir ”nej”; använd enskilda frågor med ”Vet inte” när underlaget är osäkert. Vanliga frågor föreslår tidigare roll, och godkända registerförslag hoppar över motsvarande frågor. Registerbakgrund med bransch/storleksklasser samt F-skatt/moms/arbetsgivarstatus är expanderbar. De sistnämnda visas efter en ny SCB-hämtning; äldre bilder bevaras. [Ny källkontroll och avgränsning](docs/research/10-kallkontroll-och-gapinventering-m2.md#143-ny-källkontroll-och-förenklat-godkännande-2026-10-11).

[Fler källor och återanvändning av underlag](docs/research/10-kallkontroll-och-gapinventering-m2.md#144-fler-källor-underlagsval-och-tydlig-leverans-2026-10-11): Bolagsverket kan tillföra registrerad verksamhet, organisationsform och tillgängliga digitala årsredovisningar efter separat API-åtkomst. Polisen/Länsstyrelserna samt EU/FATF ger riskunderlag som behöver versionshanteras och granskas. Dessa är inte nya byggda anslutningar. pilotbyråns egna exporter inventeras i det manuella pilotintaget före en formatanpassad CSV/XLSX-import.
