# M2 – regelbas v1 och juridisk granskning: implementeringsplan

> **För genomförande:** använd Superpowers `executing-plans` och genomför uppgifterna i ordning. Stegen följs med kryssrutor. Användaren bad 2026-10-10 Codex bygga M2. Tekniskt genomförande dokumenteras sist; verklig sakkunniggranskning i uppgift 18 återstår.

**Mål:** bygga en spårbar regelbas för en lokalt användande redovisningsbyrå, med full kravkarta, separata juridiska beslutsgrenar och underlag som en oberoende sakkunnig kan granska.

**Arkitektur:** bygg vidare på M1:s deterministiska motor, typade villkor, manifest och fastställelsegrindar. Lydelsens källa styr datum och län; juridisk verksamhetskategori hålls skild från tjänstens riskkategori. Kundmodellen innehåller mallar och syntetiska kontrakt, utan kundärenden.

**Teknik:** Python 3.13 i befintlig `.venv`, pydantic, PyYAML, pytest, python-docx. Befintlig Claude-adapter behålls; M2 verifieras med `Testleverantor`. Inga nya beroenden behövs enligt denna plan.

**Spec:** [designspecifikationen, revision 10](../specs/2026-10-08-riskanalys-design.md), särskilt 5–10, 16–18 och 20. [Research 10](../../research/10-kallkontroll-och-gapinventering-m2.md) ger källkontroll och gapinventering. [Research 09](../../research/09-tillsynsbeslut-2026.md) och det syntetiska tillsynsmaterialet är sakkunnigunderlag.

**Status 2026-10-10:** plan skriven och självgranskad. Uppgifterna nedan är inte genomförda. Researchverktygets kommandoradsfel är däremot rättat under planeringsarbetet; dess verifiering redovisas sist. Planen är inte en juridisk attest eller ett godkännande för verklig användning.

## Gemensamma begränsningar

- Första målgruppen är **en byrå lokalt**. Ingen flerbyråtjänst, serverdrift eller kunddatabas byggs i M2.
- AI fattar inga beslut. Risknivåer, poäng och regler kommer från regelbasen och riskmotorn. AI skriver bara text i ett låst schema.
- Inga personuppgifter till AI. Endast tillåtelselistan används; personer ersätts med rollplatshållare. Källa, bekräftare och fritextmotivering i profilen skickas inte till AI.
- Byrådata ligger i `$RISKANALYS_DATA` utanför repot. Originalfoton och OCR ligger i det privata källarkivet och används aldrig som instruktioner eller AI-indata.
- Varje regel har källa och grund. Skalor, gränser och poäng är `metodval`. Juridiska sammanfattningar märks `ej_granskad` tills en verklig sakkunnig har granskat dem.
- Inga fria uttryck eller `eval`. Sanning är sant, falskt eller okänt. Okända kritiska uppgifter ger preliminärt resultat och hindrar fastställelse.
- Behåll M1:s tre skalor: sannolikhet låg/medel/hög, konsekvens begränsad/betydande/allvarlig, risk låg/måttlig/hög/mycket hög. Kundrisk använder låg/normal/hög och får inte blandas ihop med tjänsterisk.
- En obelagd kontroll sänker inte risk. Ingen juridisk stoppregel får ersättas med poäng. Förbud, åtgärder och rapportering får inte försvinna när C ger låg risk.
- En liten högrisktjänst ska synas separat. Sammanvägning och 20 %-gränsen valideras i M3, inte genom en grön M2-svit.
- Riktiga API-anrop ingår inte i automatiska tester. Ingen installation eller uppgradering av paket behövs nu.
- Ingen verklig fastställelse innan M2:s sakkunniggranskning samt M3–M4:s validering och acceptansprov. Tester signerar en syntetisk kopia.
- Commit och push görs bara efter uttrycklig begäran. Spara små, granskningsbara diffar per uppgift; planens kontrollsteg innebär inte Git-authorization.

## Granskningsfokus

| Felklass | Testägare |
|---|---|
| Samtidiga lydelser i tre län, datumbyte eller ofullständig paragrafkarta ger fel hänvisning | Uppgift 1–4 och 13 |
| Skatterådgivarroll används som generellt undantag, låg risk undertrycker obligatoriska åtgärder eller sanktionsträff hanteras utan identitetsutredning | Uppgift 3, 10–12 |
| Noll nämnare, blandade perioder, ej erbjuden tjänst eller rekonstruerbar liten kundgrupp | Uppgift 5–8 |
| Godkännande överlever ändrad källa, metod, fält, kundgren eller paragraftext | Uppgift 2, 4, 14 |
| Trasig historik/manifest, byte till vintertid, eller AMLR-utkast i operativt urval | Uppgift 13, 15–16 |

## Avgränsning och godkännandekriterier

**Tekniskt M2-underlag är klart när:**

1. Dagens tre länspaket validerar och väljer exakt en relevant alternativ lydelse för varje krav, datum och tillsynsområde. Felaktig eller okänd rättslig omfattning kan inte fastställas.
2. Hela PTL:s inventarium och varje vald länsföreskrift har en redovisad hantering. Registrering enligt 7 kap. 3 § och ledningsförändringar enligt 7 kap. 6 § ingår. Ingen borttagen paragraf döljs genom att också tas bort ur inventariet.
3. De erbjudna tjänsterna i research 10 har egna hot, sårbarheter, kontroller och grundnivåförslag. Bolagsbildning och skatterådgivning identifieras utifrån faktiskt utfört arbete. Varje rättslig avgränsning kan granskas.
4. Omfattning per tjänst, kundtyp, kanal och geografi har bekräftad källa, period och beräkningsbas. Saknad omfattning, blandade perioder och noll nämnare får inget säkert resultat.
5. Kundmodellens A–D har typade rader, egen undantagsprövning, regelspår och minst ett kontrakt per rad samt negativa prov per beroende. Ingen riktig kundprofil lagras.
6. Sanktionsrisk är en egen dimension med källor och tydlig metodstatus. Den innebär inte automatisk screening eller påstådd fullständig sanktionskontroll.
7. Ändrat underlag ogiltigförklarar granskningar. Alla juridiska hinder och nya grindar prövas via kommandoraden, även mot äldre bedömningar.
8. Sakkunnigpaket kan exporteras, återställas och verifieras. Facitutkastets 17 fynd får fortsatt inte kallas upptäckta av produkten.
9. AMLR har en separat utkastkarta och paketstruktur. Operativt urval av utkast avvisas även efter 2027-07-10.
10. Hela sviten är grön utan API-nyckel; regelbasvalideringen är grön; regressionsproven kan visas ha fångat de fel de är avsedda för.

**M2-etappen enligt spec är klar först när** en oberoende sakkunnig även har godkänt krav, paragrafkartor, tillämplighet, metod och varje juridisk kundgren för angivna versioner. En fil med fältet `verifierad` är ingen självständig identitetskontroll eller extern digital signatur. Operatören ansvarar för att granskningsfilen motsvarar en verklig granskning. M3–M4 återstår även efter juridiskt godkännande.

## Beslut om struktur

| Del | Beslut och skäl |
|---|---|
| `Krav.kalla` | Behåll som huvudkälla för M1-kompatibilitet; alla använda källor härleds ur `lydelser`. Den valda lydelsen styr den visade hänvisningen. |
| Alternativa och kumulativa grunder | `lydelser` är alternativa versioner av samma krav. Två oberoende bindande grunder får två länkade krav. Skilda betydelser mellan län får separata krav. |
| Länspaket | `RP-RED-VG`, `RP-RED-SKANE`, `RP-RED-STHLM`. Säte/folkbokföring och utländsk filial prövas enligt PTF 16 §. Kundernas geografi styr sårbarheter, inte tillsynsmyndighet. |
| Fullständighet | Behåll `paragrafkarta` i paketet. Refererade källor inventeras separat; kartans giltighetsintervall, lydelser och paketets län ingår i granskningen. Vid framtida ändrad karta används ny paketversion. |
| Kundmodell | Ny underkatalog `bedomning/kundmodell/` inom befintlig domän, med egna `K-`-fält utanför byråprofilens `P-`-register. Den levererar en granskningsbar mall; kundärenden hör till M9. |
| Omfattning | Utöka `Uppgift` med period och `Falt` med beräkningsbas. Skalärvärden och belägg från M1 behålls. Omfattningsandelar beräknas ur bekräftade antal; inget parallellt statistiklager. |
| Expertunderlag | Exportera kompletta läsbara data och summor; importera en granskningsfil bunden till exporten. Metod och kundtabeller signeras tillsammans med paketet. |
| AMLR | Separat mapp `regelbas/utkast/amlr/` som inte läses av dagens operativa laddare. Explicit inspektion och utkastvalidering, separat framtida frigivning. |

## Filkarta

Sökvägar med `src/`, `regelbas/`, `docs/` eller `tester/` är relativa till `/Users/gt/Documents/Riskanalys/Riskanalys`. Förkortade Python-modulsökvägar, exempelvis `regelverk/modeller.py` och `profil/hantering.py`, är relativa till `src/riskanalys/`. Samma förkortning används i uppgifternas fillistor.

- `regelverk/modeller.py`, `laddning.py`, `validering.py`, `urval.py`: utöka befintliga modeller och urval; referensintegritet och signaturbindning.
- Nya `src/riskanalys/regelverk/inventering.py`, `tillsyn.py`, `sakkunnig.py`: källinventarium, tillsynsområde, export/import av sakkunnigunderlag.
- `regelbas/kallor.yaml`, `lydelser.yaml`, `lydelsetexter/`, `krav/`, `regelpaket/`: dagens kompletta regeldata, med stabila M1-ID:n.
- Nya `regelbas/inventering/`, `referensdata/sektorsrisk.yaml`, `beslutstabeller/tillamplighet.yaml`, `kundfalt.yaml`, `beslutstabeller/kundmodell/`: oberoende inventarium, referensnivåer och typade juridiska tabeller.
- `profil/modeller.py`, `hantering.py`, nya `profil/omfattning.py`: belägg, perioder, antal och härledda andelar.
- Nya `bedomning/sektorsrisk.py`, `bedomning/sanktioner.py`, `bedomning/kundmodell/{modeller,tabeller,utvardering}.py`: separat metod och juridiska grenar.
- `dokument/underlag.py`, `validering.py`, `arb.py`, `leverantor.py`: utökade avsnittsunderlag, förbud mot känsliga uppgifter och korrekt testtext.
- `granskning/kontroller.py`, nya `granskning/sektorsrisk.py`: dokumentets täckning och B-13.
- `faststallelse/grindar.py`, `faststall.py`: paketets expertstatus, giltighet och bekräftad profil.
- `lagring/manifest.py`, `korningar.py`, `yamlfil.py`: versionsproveniens, UTC och åtgärdbara fel.
- `kommandon/profil_kommando.py`, `regelbas_kommando.py`, ny `sakkunnig_kommando.py`, `cli.py`: befintlig CLI utökas; inget nytt gränssnitt.
- `tester/regelkontrakt/`, `enhet/`, `typfall/`: syntetiska kontrakt; ingen nätberoende testdata.

## Arbetsordning

Uppgift 1 → 2 → 3 → 4 etablerar juridiska data. Uppgift 5 → 6 → 7 → 8 etablerar profilen och dokumentgranskningen. Uppgift 9–12 använder dessa kontrakt för riskdimensioner och kundmall. Uppgift 13–16 säkrar fastställelse, sakkunnigunderlag, provenance och AMLR. Uppgift 17 samlar verifieringen. Uppgift 18 är en verklig sakkunniggranskning.

Varje uppgift genomförs med test först, observerad förväntad failure, minimal ändring och grönt fokuserat prov. Exempelkoden är testkontrakt för framtida implementation; den är inte kopierad programkod och har inte körts nu. Nya fixtures ska bygga syntetiska data i `tmp_path` genom befintlig `tester/conftest.py`, aldrig skriva i repots regelbas.

### Uppgift 1: Källinventarium och datumlydelser

**Filer:** skapa `src/riskanalys/regelverk/inventering.py`, `regelbas/inventering/ptl.yaml`, `ptf.yaml`, `14fs.yaml`, `12fs.yaml`, `01fs.yaml`; ändra `src/riskanalys/regelverk/{modeller,laddning,validering}.py`, `regelbas/kallor.yaml`, `lydelser.yaml`, `lydelsetexter/`; test `tester/regelkontrakt/test_inventering.py`.

**Gränssnitt:** `inventera_sfs(text: str, kalla_id: str) -> tuple[InventeradLydelse, ...]`. Den frysta posten definieras i `regelverk/modeller.py` och har `kalla: str`, `lagrum: str`, `text: str`, `ikraft: date | None`, `upphor: date | None`, `inford_genom: str | None`. `kontrollera_inventarium(regelbas: Regelbas, inventarium: tuple[InventeradLydelse, ...]) -> list[str]`. Lägg `Regelbas.inventarium: tuple[InventeradLydelse,...] = ()`; laddaren läser `inventering/*.yaml` och valideringen anropar kontrollen. PDF-uttagen används som kandidater; en källkontrollerad text är facit.

- [x] Skriv `test_inventarium_fangar_borttagen_paragraf`: ta bort en rad från både paketkarta och `Kalla.paragrafer`; det separat sparade inventariet ska fortfarande rapportera den. Skriv gränstest för två versioner av PTL 1 kap. 2 §: 2026-11-19 väljer den äldre, 2026-11-20 den nya.
- [x] Kör `env -u ANTHROPIC_API_KEY .venv/bin/pytest tester/regelkontrakt/test_inventering.py -q`; observera failure för saknad inventeringskontroll.
- [x] Registrera version, hämtning, exakt URL, källfilens SHA-256 och uttagets normaliserade textsumma som olika uppgifter. PTL-uttaget har 142 lydelser men **141 unika lagrum**; blanda inte ihop dessa i kartan. Spara alla lagrum i inventariet, även upphävda paragrafer; deras hantering framgår av paragrafkartan. Förordningen har 29 och varje länsföreskrift 31 i kontrollerat uttag.
- [x] Utöka `Kalla` med `galler_fran: date | None`, `galler_till: date | None` och `inventarium_kontrollsumma: str | None`, samtliga utan automatiskt gissade datum. För v1:s rättskällor krävs källsumma och inventariesumma. Kontrollera inventariefilens innehåll och ta med dess summa samt källgiltigheten i `KALLANS_GILTIGHET` och sakkunnigunderlaget. V0 kan fortfarande laddas; ingen saknad metadata gör en gammal källa granskat aktuell.
- [x] Kontrollera allmänna råd och övergångsbestämmelser separat eftersom uttagsverktyget exkluderar dem. Bestäm varje paragrafversions verkliga ikraftdatum via ändringsförfattningen; använd aldrig lagens ursprungliga ikraftdatum för alla ändrade paragrafer. Rader vars datum inte kan styrkas kvarstår som ogranskade och hindrar frigivning.
- [x] Kör kontrakten grönt och kontrollera källfilernas SHA mot det lokala manifestet. Importen ska inte hämta nätdata under tester eller kopiera privat OCR till repot.

### Uppgift 2: Lydelseurval i tre tillsynsområden

**Filer:** ändra `src/riskanalys/regelverk/{modeller,urval,validering}.py`, `regelbas/regelpaket/`; test `tester/regelkontrakt/test_urval.py`, `test_validering_regelbas.py`.

**Gränssnitt:** behåll `valj(regelbas: Regelbas, paket_id: str, datum: date, lan: str) -> Urval` och `ValtKrav(krav: Krav, lydelse: Lydelse)`. Lägg till `lydelse_galler_i_lan(regelbas: Regelbas, lydelse: Lydelse, lan: str) -> bool`. `Krav.kalla` är huvudkälla, inte urvalsfilter.

- [x] Skriv parametriserat `test_alternativ_lydelse_valjs_per_lan` för VG/Skåne/Stockholm samt ett verkligt överlapp inom samma län som ska ge `UrvalsFel`. Testa att nationell PTL fortfarande gäller i alla tre.
- [x] Observera att M1:s urval ger fel vid samtidiga länslydelser. Implementera filter på både datum och lydelsens källgeografi; tillåt inte att ett saknat bindande krav tyst filtreras bort inom paketets utlovade giltighet.
- [x] Ändra valideringen: huvudkällan måste finnas bland kravets lydelsekällor; radens källa/lagrum får matcha vilken relevant alternativ lydelse som helst. Varje alternativ ska ge samma avsedda krav; skilda innehåll separeras.
- [x] Utöka `kravets_innehallssumma` till samtliga lydelsekällor och rättsliga giltighetsuppgifter. Negativt test: ändrad Skåne-geografi/textsumma ska ogiltigförklara ett tidigare godkännande även när huvudkällan är VG.
- [x] Kör de två testfilerna grönt. Uppdatera väntande ändringar så att bara ändringar relevanta för vald geografi visas.

### Uppgift 3: Tillsyn, faktisk tjänst och rättslig kategori

**Filer:** skapa `src/riskanalys/regelverk/tillsyn.py`, `regelbas/beslutstabeller/tillamplighet.yaml`; ändra `regelbas/falt.yaml`, `src/riskanalys/kommandon/profil_kommando.py`, `profil/hantering.py`; test `tester/regelkontrakt/test_tillamplighet.py`.

**Gränssnitt:** `tillsynsomrade(lan: str, utlandsk_filial: bool) -> str`; `rattlig_omfattning(regelbas: Regelbas, profil: Profil) -> Omfattningsbeslut`. Fryst `Omfattningsbeslut` innehåller `paket_id: str | None`, `punkter: tuple[int, ...]`, `status: Bedomningsstatus`, `regelspar: tuple[str, ...]`, `hinder: tuple[str, ...]`.

- [x] Testa alla 21 län mot PTF 16 §, Stockholm för utländsk filial och avvisning av okänt län. Testa också byrå enligt 19 med bolagsbildning: tjänstens riskkategori kvarstår men punkt 23 läggs inte till automatiskt. Ren bolagsbildare utanför 18–22 prövas mot 23. Oklara svar ger preliminärt beslut.
- [x] Kör testerna och observera failure. Registrera `P-ORG.sateslan`, `P-ORG.utlandsk_filial` och frågor om faktisk yrkesverksamhet; dokumentera vilka frågor som ligger till grund för 18–23. Punkt 18, 21 eller 22 hanteras med sakkunnig fastställd avgränsning/tillsyn; generera inte en säker slutsats från en otydlig titel.
- [x] Lägg konkreta intagsfrågor för bolagsstart, skatteupplägg, betalningsbehörighet, klientmedel, adress, styrelseuppdrag, trust och nominella aktieägare. Svara på faktiskt utfört arbete. Tjänst utanför paketets granskade omfattning ger ett hinder med förklaring.
- [x] Behåll `--lan` och `--regelpaket` för M1-kompatibilitet men kontrollera att de stämmer med bekräftad profil före bedömning och fastställelse. Manuellt paketval får inte kringgå prövningen.
- [x] Kör kontrakten grönt och knyt beslutstabellernas rader till motsvarande paragrafkarta och expertunderlag.

### Uppgift 4: Fullt kravregister och paragrafkartor

**Filer:** skapa `regelbas/krav/{tillamplighet,kundkannedom,rapportering,bevarande,organisation,registrering}.yaml`, `regelbas/regelpaket/redovisning-skane.yaml`, `redovisning-stockholm.yaml`; ändra VG-paket och befintliga ARB-krav; test `tester/regelkontrakt/test_regelbas_v1.py`.

**Gränssnitt:** befintliga `Krav`, `Kartrad`, `Paragrafkarta`, `Regelpaket`; `validera(regelbas: Regelbas) -> list[str]`. Lägg `hantering: str | None` på kartans rader för definitioner/bemyndiganden/ren myndighetsreglering; en sådan rad måste förklara hanteringen och granskas, inte låtsas vara sektorsundantag. Ny fryst `Kravmal(typ: Literal['dokument','drift','kundmall'], id: str, etapp: str)`, och `Krav.mal: tuple[Kravmal,...] = ()`. M1:s `uppfylls_i` behålls; funktionen för dokumenturval använder dess ARB-mål som kompatibilitetsfall när `mal` saknas. V1 kräver explicita `mal` och att de är förenliga med eventuella `uppfylls_i`.

- [x] Skriv kontrakt: alla 141 unika PTL-lagrum och alla 31 föreskriftsparagrafer per paket finns i inventeringskontrollen; rader får krav, motiverad sektorexkludering eller annan redovisad hantering. Krav för 7 kap. 3 och 6 §§ måste finnas.
- [x] Observera failure mot v0. Lägg krav utifrån research 02 och primärkällorna; separera lag, föreskrift, allmänt råd och tillsynspraxis. Varje krav får belägg, villkor, dokument-/driftmål och `ej_granskad`. Stabilt M1-ID behålls för de sex befintliga kraven.
- [x] Utöka målangivelserna från endast dokumentavsnitt till typade mål: `dokument`, `drift` eller `kundmall`. Registrering får driftmål i M4, inte ett påhittat ARB-avsnitt. Varje mål har etapp och ID; strukturell validering kräver att målet är definierat även om leveransen hör till M4/M6.
- [x] Datera kartorna och dokumentera varför exempelvis 4 a/7 a kap. inte ger en skyldighet för vald sektor. För datum innan granskad giltighet: avvisa, använd inte dagens karta retroaktivt. Signatursumman omfattar hela paketets krav och alla beroenden.
- [x] Kör `test_regelbas_v1.py` och regelbasvalideringen grönt utan att sätta sakkunnigstatus till verifierad.

### Uppgift 5: Profil med period, antal och beräkningsbas

**Filer:** ändra `src/riskanalys/profil/{modeller,hantering}.py`, skapa `profil/omfattning.py`; ändra `regelbas/falt.yaml`, `kommandon/profil_kommando.py`; test `tester/enhet/test_omfattning.py`, `test_profil_kommando.py`.

**Gränssnitt:** `Period(fran: date, till: date)` är fryst och kräver `fran <= till`. `Uppgift.period: Period | None = None`. `Falt.periodkrav: bool = False`, `basfalt: str | None = None`, `antalfalt: str | None = None`, `kritisk_om: dict | None = None`. `omfattningsbrister(profil: Profil, regelbas: Regelbas) -> list[str]`; `harled_andelar(profil: Profil, regelbas: Regelbas) -> Profil`.

- [x] Testa saknad period, bakvänd period, bekräftade antal från olika perioder, saknad bas och noll nämnare. Föreslagen uppgift får inte användas som känd nämnare. Exempel: 3 av 100 ger exakt `0.03`, medan noll kunder ger okänd andel, inte 0 %.
- [x] Kör failing tests. Omfattningsandelar härleds bara när antal och bas är bekräftade och perioderna matchar. Dessa andelsfält kan inte bekräftas direkt via handredigering eller CLI; kontrollen jämför med härledningen och anger vilka antal som ska bekräftas. Andel av omsättning använder motsvarande belopp och enhet med samma period, utan krav på heltalskundantal.
- [x] Lägg fält för aktiva kunder och omsättningsbas; för varje tjänst `P-TJ.<slug>_erbjuds`, `_antal_kunder`, `_omsattning`, `_andel_kunder`, `_andel_omsattning` där slug är red01…red07, skatt01, bolag01…bolag03. Behåll gamla erbjudandefält som explicit kompatibilitetsmappning till samma tjänst; konflikter ger fel, inga dubbla sanningar.
- [x] Lägg motsvarande antal/baser för juridisk kundtyp, bransch, nya kunder, kanal, ägar- och transaktionsgeografi och egna rapporter/avböjanden. Dokumentera nämnare och enhet i varje fältdefinition. Kategorier som kan överlappa får inte krävas summera till 100 %. Samma kund får förekomma i flera tjänster; omsättning fördelas utan dubbelräkning.
- [x] Utöka `bekrafta(..., period: Period | None = None) -> Profil` och CLI med `--period-fran`/`--period-till`. Gamla profiler kan läsas; nya okända kritiska uppgifter stoppar fastställelse tills de kompletterats. Inga uppgifter flyttas eller bekräftas automatiskt.
- [x] Skriv och rätta `test_andelen_ett_kraver_tydligt_format`: ensam `"1"` avvisas med hjälp; `"1 %"` betyder 0.01 och `"1,0"` betyder 1.0 för manuella M1-andelar. Härledda andelar påverkas inte av texttolkningen.
- [x] Kör testfilerna grönt; kontrollera att samma brister prövas i `bedom` och fastställelsegrinden.

### Uppgift 6: Tjänster, hot, sårbarheter och kontroller

**Filer:** ändra `regelbas/kataloger/{tjanster,hot,sarbarheter,kontroller}.yaml`, `regelbas/beslutstabeller/metod.yaml`, `src/riskanalys/regelverk/modeller.py`; test `tester/regelkontrakt/test_kataloger_v1.py`, `test_motor.py`.

**Gränssnitt:** befintliga `Tjanst`, `Hot`, `Sarbarhet`, `Kontroll`; utöka metodposter med `grund`, motivering och granskning. `bedom(regelbas, urval, profil) -> Bedomning` behålls.

- [x] Testa de elva tjänst-ID:n i research 10 var för sig: erbjuds/erbjuds ej/okänt. Ej erbjuden tjänst ska finnas kvar utan riskavsnitt och utan krav på tjänstens omsättning/kontrollbelägg. Okänt erbjudande är preliminärt.
- [x] Observera failure. Koppla verifierbara hot till respektive tjänst utifrån NRA 7.19, 7.20, 7.25 och vägledningen; varje källa har avsnitt/sida. Katalogens grundnivåer är **förslag till metodval** och rättslig grund kommer från uppgift 3, inte från sektorsnamnet.
- [x] Lägg sårbarheter för kund, kanal, geografi, verksamhet och tjänst med giltiga `P-`-fält. Lägg kombinationsvillkor som synliggör samverkande faktorer; ange egna regel-ID:n och undvik dubbelräkning av samma förhållande.
- [x] Kontroller kräver både utformning och genomförandebelägg. Testa att rutindokument utan belägg inte sänker risken. FfR:s ej-tillämplighet kräver motivering enligt organisationens regler; ARB får då korrekt ansvarstext. `P-ORG.namn` ska visas bland uppgifter som måste kompletteras när rendering behöver det.
- [x] Kör kontrakten grönt. Skicka grundnivåer och de nya kombinationsreglerna till sakkunnig; presentera inte kalibrering som redan validerad.

### Uppgift 7: Sektorsrisk och kontroll B-13

**Filer:** skapa `regelbas/referensdata/sektorsrisk.yaml`, `src/riskanalys/bedomning/sektorsrisk.py`, `granskning/sektorsrisk.py`; ändra loader/modeller, `granskning/kontroller.py`, `dokument/arb.py`; test `tester/regelkontrakt/test_sektorsrisk.py`.

**Gränssnitt:** `Sektorsreferens(id: str, sektor: str, niva: str, skala: tuple[str, ...], kalla: str, sida: int)`. `sektorsavvikelser(regelbas: Regelbas, bedomning: Bedomning, profil: Profil) -> tuple[Sektorsavvikelse, ...]`; fryst avvikelse har tjänst, referens, jämförd dimension, metod-ID och motiveringens status.

- [x] Skriv test som ger B-13 när en erbjuden tjänsts inneboende risk avviker från sin jämförbara sektorsreferens utan motivering. Fungerande kontroller får inte i sig ändra sektorns referens eller förklara en låg inneboende risk.
- [x] Observera failure. Spara NRA:s originalskala låg/medel/betydande/hög och hög för de tre aktuella sektorerna. Spara källa/sida och referensversion. En explicit mappning till motorns skala är ett separat granskat metodval; tills jämförbarheten är fastställd krävs mänsklig motivering, ingen påhittad automatisk ekvivalens.
- [x] Låt motiveringen finnas lokalt med källa/bekräftare; AI får bara tillåtna strukturerade förhållanden. Automatisk B-13 kontrollerar saknad motivering, inte den juridiska kvaliteten hos fritext. Ett högt nivåord ensamt undanröjer inte ett tillsynsfynd.
- [x] Kör testerna grönt med signerad syntetisk metodkopia och ogranskad verklig regelbas. Uppdatera B-13:s `automatiserad` först när denna kontroll har ett fungerande test.

### Uppgift 8: Dokumentomfattning och AI-underlag

**Filer:** ändra `src/riskanalys/dokument/{underlag,modeller,validering,arb,leverantor}.py`, `granskning/kontroller.py`, `regelbas/tillatelselistor.yaml`; test `tester/enhet/test_underlag.py`, `test_validering_utkast.py`, `tester/regelkontrakt/test_granskning.py`.

**Gränssnitt:** `krav_for_dokument(regelbas: Regelbas, urval: Urval, profil: Profil, dokument_id: str) -> tuple[ValtKrav, ...]`. Befintlig `bygg_underlag(...) -> Avsnittsunderlag` och `validera_utkast(...) -> list[str]` behålls.

- [x] Skriv täckningsprov: ARB-krav saknar avsnitt → fynd; rent rutinkrav/driftmål → inget felaktigt ARB-fynd. Alla krav finns fortfarande i expertpaketets fullständighetsgranskning.
- [x] Skriv negativa AI-prov: oklarhetens `saknad_uppgift` är ett påhittat fält, ett känt men ej tillåtet fält eller ett känsligt fält → valideringsfel. En giltig öppen fråga ska fortfarande blockera fastställelse och synas i sakgranskningen.
- [x] Kör failing tests. Filtrera täckningen via typade mål från uppgift 4. Dela dokumentkategorierna ARB/rutiner/kundmall/drift utan att skapa rutindokument i denna uppgift.
- [x] Skriv smågruppstest: antal 3 med bas 100 får inte ge vare sig `3`, `3 %` eller någon kombination som avslöjar antalet i serialiserat AI-underlag. Under fem visas `färre än 5`; andelar och härledda tal undertrycks tillsammans. Testa även 0, 4 och 5 samt överlappande grupper. Metodgränsen är inget generellt anonymitetsbevis; sådana grupper hålls utanför AI om kombinationen kan identifiera en person.
- [x] Lägg strukturerad period/bas till tillåtna uppgifter där den kan skickas säkert. Skicka inga källnamn, personnamn eller originalhandlingar till AI. Uppdatera `Testleverantor` för de utökade dimensionerna; AI-text kan inte lägga till egna nivåer.
- [x] Kör alla tre testfilerna grönt. Dubbletten av öppen fråga i åtgärdslistan kan tas bort endast med bevarad synlighet i sakgranskningen; den är ingen fastställelsespärr i sig.

### Uppgift 9: Separat sanktionsrisk per tjänst

**Filer:** skapa `src/riskanalys/bedomning/sanktioner.py`, `regelbas/beslutstabeller/sanktionsrisk.yaml`; ändra `bedomning/{modeller,motor}.py`, `dokument/{underlag,validering,arb}.py`, regelkataloger; test `tester/regelkontrakt/test_sanktionsrisk.py`.

**Gränssnitt:** `bedom_sanktionsrisk(regelbas: Regelbas, tjanst: Tjanst, profil: Profil) -> Sanktionsbedomning`. Fryst post: `status`, `inneboende: Riskdel | None`, `kvarstaende: Risk | None`, `regelspar`, `okanda_uppgifter`. Lägg `sanktionsrisk` till `Tjanstbedomning`; äldre sparade bedömningar kan läsas men har inte automatiskt den nya dimensionen.

- [x] Testa att hög TF-risk inte kopieras till sanktionsrisk, att okänd geografi ger preliminär sanktionsbedömning och att obelagd kontroll inte sänker den. Testa att AI inte kan skriva sanktionsnivå som skiljer sig från motorn.
- [x] Observera failure. Använd en separat tabell och explicita riskfaktorer med källor/metodstatus. Detta är en förberedd riskdimension enligt spec 7.1 och AMLR artikel 10; beskriv inte AMLR:s framtida krav som gällande PTL-krav i dag.
- [x] Lägg dimensionens regler och uppgifter till metodgranskningen; gamla bedömningar måste köras om innan ett nytt v1-paket kan fastställas. Ingen listintegration eller kundscreening byggs.
- [x] Kör kontrakten grönt och visa dimensionerna sida vid sida i sakkunnigunderlag och sakgranskning.

### Uppgift 10: Kundmallens tabeller, fält och spår C

**Filer:** skapa `src/riskanalys/bedomning/kundmodell/{__init__,modeller,tabeller,utvardering}.py`, `regelbas/kundfalt.yaml`, `regelbas/beslutstabeller/kundmodell/c-risk.yaml`; ändra loader/modeller; test `tester/regelkontrakt/test_kundmodell_c.py`.

**Gränssnitt:** fryst `Kundrad(id: str, spar: Literal['A','B','C','D'], villkor: dict, utfall: dict, grund: Grund, lydelser: tuple[str,...], forklaring: str)`. `Kundmall` innehåller `falt: dict[str,Falt]`, `rader: tuple[Kundrad,...]`. `utvardera_kundmall(mall: Kundmall, varden: dict[str,Faltvarde], datum: date) -> Kundutfall`. Resultat har A–D, status, okända fält och regelspår. Alla utfall valideras per spår, inga fria strängkommandon.

- [x] Skriv kontrakt att okänt `K-`-fält ger preliminär C och aldrig blir låg/normal genom standardvärde. Varje tabellrad måste ha ett positivt fall, ett negativt fall och prövning av okända ingångar. `K-`-fält får inte hamna i `skapa_profil` eller AI-tillåtelselistan.
- [x] Observera failure. Återanvänd villkorsutvärderaren med separat fältdefinition; definiera kundfaktorer från PTL 2 kap. 3–5 §§. Poäng och gränser registreras som ett granskningsbart metodförslag, med prov vid varje tröskel.
- [x] Håll C:s metodkonfiguration skild från den juridiska tabellutvärderaren. Ingen matchande C-rad, flera motsägande C-rader eller en ogranskad metod ger preliminärt utfall med förklaring, aldrig normal/låg som fallback. Kontrakten använder uttryckliga syntetiska C-rader och prövar hög/låg/normal var för sig. Produktionsvärden för kundpoäng och gränser ska granskas i uppgift 18 och valideras i M3; planen uppfinner ingen riskklassningsformel utan sådant underlag.
- [x] Definiera A-utfall `tillatet/stopp/undantag/preliminart`, C `låg/normal/hög/preliminär`; B är en mängd åtgärds-ID:n och D innehåller `rapportera/undantag/ingen_skalig_misstanke/preliminart`. Beslutstabeller kan inte ändra eller skicka ett kundärende; utvärderaren används här enbart i syntetiska tester och sakkunnigunderlag.
- [x] Kör kontrakten grönt. Dokumentera mallens begränsningar; M9 behöver egen kunddataspec och arbetsflöden.

### Uppgift 11: Spår A och B, med egna undantag

**Filer:** skapa `regelbas/beslutstabeller/kundmodell/a-stopp.yaml`, `b-atgarder.yaml`; ändra kundmallens utvärderare; test `tester/regelkontrakt/test_kundmodell_ab.py`.

**Gränssnitt:** `utvardera_kundmall` från uppgift 10; inga nya fristående poängmotorer. `K-`-fält definieras i det separata registret med frågor, tillämplighet och källa.

- [x] Testa A för otillräcklig kundkännedom, rättsligt avgränsat undantag enligt 3 kap. 1 §, etableringsmisstanke enligt 2 § och transaktion enligt 3 §. En skatterådgivarroll utan rättsligt uppdrag ger inte undantag. Undantag från kundkännedomsstopp tar inte bort etableringsmisstanke.
- [x] Testa B för 3 kap. 16–17 §§: skärpt övervakning plus samtliga fyra informations-/godkännandepunkter; EES-filialundantag gäller först när alla tre villkor är bekräftade. Testa PEP i kund och verklig huvudman, familjemedlem/medarbetare, beslut att ingå/avbryta och 18-månadersgränsen med kalendermånader, inte 18×30 dygn.
- [x] Observera failure. Ange C→B och C→A som uttryckliga beroenden; C låg får inte radera en PEP- eller högrisktredjelandsåtgärd. B→C som hög risk markeras metodval och har eget regel-ID, aldrig lagkrav.
- [x] Skriv kontrakt att okänd undantagsförutsättning inte gör förbjuden åtgärd till tillåten. Utfallet ska ange vilken uppgift som måste kontrolleras.
- [x] Kör kontrakten grönt; bind varje rad och beroende till respektive lagrum och sakkunnigkontrollsumma.

### Uppgift 12: Spår D och avgränsad sanktionsgren

**Filer:** skapa `regelbas/beslutstabeller/kundmodell/d-rapportering.yaml`, `a-sanktioner.yaml`; ändra `regelbas/kallor.yaml`, `lydelser.yaml`, `kundfalt.yaml`; test `tester/regelkontrakt/test_kundmodell_d.py`, `test_kundmodell_sanktioner.py`.

**Gränssnitt:** samma `Kundmall` och `utvardera_kundmall`. För sanktionsgrenen krävs separata fält för möjlig träff, utredd identitet, tillämpligt förbud, rättsligt undantag/tillstånd och exakt källreferens.

- [x] Skriv D-test för skälig misstanke med och utan utförd transaktion; båda rapporteringsprövas. Testa undantagna respektive icke undantagna uppgifter enligt 4 kap. 8 § inom samma skatterådgivaruppdrag. Låg C, stopp A och utförande med A-undantag ändrar inte D:s självständiga prövning.
- [x] Kör failing tests. Lägg 4 kap. 2–3, 8 och 9 §§ med egna villkor/undantag. A och D delar faktauppgifter om uppdraget men har inga automatiskt kopierade undantagsutfall. D okänt ger preliminärt och tydlig hänvisning till mänsklig bedömning, inte `rapportera=false`.
- [x] För sanktionsgrenen: verifiera tillämpliga EU-förordningar och exakta artiklar från EUR-Lex innan en bindande regel skrivs. Skilj frysning/tillgängliggörandeförbud från andra sanktioner och beakta ägande/kontroll samt eventuella tillstånd. Samlingslistan är hjälp till identifiering, inte ensam rättslig grund.
- [x] Skriv prov: möjlig namnträff utan fastställd identitet är `preliminart`, inte bekräftat förbud. Utredningskrav får ge metodiskt tillfälligt stopp, uttryckligen märkt som metod. Bekräftat tillämpligt förbud ger rättsligt stopp även vid låg C. Saknad primärkälla hindrar expertfrigivning.
- [x] Kör båda kontraktfilerna grönt. Exakta sanktionstillämpningar och undantag kräver sakkunnig; planen förutsätter ingen generell frikännande regel för en träff.

### Uppgift 13: Giltighet mellan bedömning och fastställelse

**Filer:** ändra `src/riskanalys/regelverk/urval.py`, `faststallelse/{grindar,faststall}.py`, `kommandon/bedom_kommando.py`; test `tester/regelkontrakt/test_grindar.py`, `tester/enhet/test_faststall_kommando.py`.

**Gränssnitt:** `andringar_mellan(regelbas: Regelbas, urval: Urval, beslutsdatum: date) -> tuple[VantandeAndring,...]`. Behåll `hinder_for_faststallelse(underlag, beslutsdatum) -> list[str]`.

- [x] Testa bedömning 2026-11-19 och beslut 2026-11-20: relevant ändrad lydelse stoppar med krav/avsnitt och instruktion att köra om kedjan. Före gränsen finns inget sådant hinder. En förändring utan betydelse för vald byrå ska kunna bedömas uttryckligen, men inget generellt tyst ignorerande tillåts.
- [x] Observera failure. Jämför låst urval med urval vid beslutets datum samt datumvillkor i tabeller, källor och karta. Samma ordalydelse med ny version visas ändå som ändrat rättsligt underlag; omprövning loggas och går genom granskningen.
- [x] Lägg grind för metod- och kundmallssignatur från uppgift 14, full profilkontroll och paketets omfattning från 3/5. En äldre bedömning får inte kringgå nya obligatoriska dimensioner genom saknade JSON-fält.
- [x] Kör testerna grönt; behåll M1:s kronologiregler och annualitetsgrind. Framtida kalenderdatum i allmän drift rättas i M4 enligt restlistan.

### Uppgift 14: Sakkunnigpaket, granskningsfil och facit

**Filer:** skapa `src/riskanalys/regelverk/sakkunnig.py`, `kommandon/sakkunnig_kommando.py`; ändra `regelverk/modeller.py`, `faststallelse/grindar.py`, `cli.py`; test `tester/enhet/test_sakkunnigpaket.py`, `tester/regelkontrakt/test_sakkunnigbindning.py`.

**Gränssnitt:** `exportera_sakkunnigunderlag(rot: Path, paket_id: str, datum: date, utmapp: Path) -> Path`; `las_granskningsfil(fil: Path, regelbas: Regelbas, paket_id: str) -> Granskningsbeslut`; `tillampa_granskning(regelbasrot: Path, beslut: Granskningsbeslut) -> None`. Exporten skriver `underlag.json`, `granskning.md`, `granskningsmall.yaml` och manifest, med redan sparade paragraftexter; ingen AI används.

Utöka `Regelpaket` med `granskning: Sakkunnig` som har standardstatus `ej_granskad`, så äldre paket aldrig antas vara godkända. Lägg till `Regelbas.paketets_innehallssumma(paket_id: str) -> str`: kanonisk summa över paketet och alla refererade krav, kartor, källor/lydelsetexter, fält, inventarier, kataloger, metoder och kundtabeller, utan granskningsmetadata. Export, import och fastställelsegrind använder samma funktion; paketattesten krävs tillsammans med befintliga objektkontroller.

- [x] Testa att export innehåller samtliga krav, karta, källproveniens, län/datum, metod och kundgrenar med undantag/beroenden. Ändra efter export var för sig: källa, paragraftext, fältdefinition, katalogens grundnivå, metod, kundrad och paketets län; import av den gamla granskningsfilen ska avvisas.
- [x] Observera failure. Granskningsfilen har granskare/kompetens, oberoende, datum, exportens summa, paket/version, beslut per objekt och kommentarer. Tom granskare, saknade objekt, påhittade ID:n, gammal summa eller ofullständig karta avvisas. `ändras` lämnar paketet ogranskat; ingen delvis import gör paketet frigivet.
- [x] Koppla CLI `regelbas granskningsunderlag --paket ... --datum ... --ut ...` och `regelbas importera-granskning <fil> --regelbas ...`. Import sker atomiskt efter att hela filen validerats. Signaturernas innehåll inkluderar alla beroenden, men inte signaturfälten själva, så att import inte ogiltigförklarar sitt eget underlag.
- [x] Bifoga syntetiska tillsynsfall och sidhänvisningar som separat bilaga. Facitets juridiska beslut sparas per fall/fynd/variant och exakt facitversion; råhandlingar följer inte med. De två besluten ger negativt underlag, inte ett universellt positivt facit. Laga kraft/domstolsavgöranden anges som osäkerheter tills kontrollerade.
- [x] Kör kontrakten grönt med syntetiska granskare i kopior. Importens metadata kan inte bevisa att en människa är sakkunnig; attestprocessen och verifierbar identitet dokumenteras i uppgift 18.

### Uppgift 15: Proveniens, UTC och felvägar

**Filer:** ändra `src/riskanalys/lagring/{manifest,korningar,yamlfil}.py`, `profil/lagring.py`, `drift/historik.py`, `faststallelse/sakgranskning.py`, `regelverk/{laddning,villkor}.py`, `granskning/korning.py`, `kommandon/skriv_kommando.py`; test `tester/enhet/test_manifest.py`, `test_korningar.py`, `test_laddning.py`, `test_historik.py`, `test_sakgranskning.py`.

**Gränssnitt:** `Programproveniens(commit: str | None, arbetskopia: Literal['ren','andrad','okand'], innehallssumma: str)` i manifestet. Behåll befintliga läs-/skrivsignaturer. UTC-stämpeln i `ny_korningsmapp` slutar med `Z`; senaste körning sorteras på manifestets tidszonmedvetna `skapad`, inte mappnamnet.

- [x] Skriv prov med två lokala klockslag vid höstens tidsomställning: den senare UTC-körningen väljs, även om lokalt namn är lägre. Både gamla M1-namn och nya UTC-namn kan läsas. Vid lika tid används stabilt mappnamn som sekundär nyckel.
- [x] Skriv negativa prov för saknat/skadat manifest, trasig YAML, fel UTF-8 i historik/sakgranskning/testsvar/lydelsetext och icke-text `falt`/`op`. Fel ska vara `RiskanalysFel` på svenska med berörd fil och återställnings-/rättningsinstruktion, utan stackspår i CLI.
- [x] Observera failures. Urval av senaste körning får aldrig falla tillbaka till en äldre körning när den senaste relevanta har skadat manifest. Ett gammalt utkast som inte ingår i valt bedömningsunderlag ska inte stoppa den nya granskningen; välj beroenden först och verifiera sedan alla som faktiskt används. Vid skadat manifest med okänd relevans: avvisa, gissa inte.
- [x] Spara checksumma av programinnehåll och explicit ren/ändrad/okänd arbetskopia; Git-commit ensam räcker inte. Inkludera relevanta icke ignorerade programfiler men inga hemligheter i export. Utan `.git` sparas `okand` samt paketversion/innehållssumma. Äldre manifest läses som proveniens okänd, aldrig som ren.
- [x] Kör testfilerna grönt och verifiera ett M1-paket utan omskrivning av dess gamla manifest. Fsync/atomiska profilskrivningar och installationspaketering genomförs i M4, inte som en dold del av denna uppgift.

### Uppgift 16: Parallellt AMLR-utkast

**Filer:** skapa `regelbas/utkast/amlr/{kallor.yaml,kravkarta.yaml,paket.yaml,README.md}`; ändra `src/riskanalys/regelverk/laddning.py`, `kommandon/regelbas_kommando.py`, `docs/research/04-eu-regelverk.md`; test `tester/regelkontrakt/test_amlr_utkast.py`.

**Gränssnitt:** `ladda_amlr_utkast(rot: Path) -> AmlrUtkast`; typad `AmlrUtkast(status: Literal['utkast'], tillampas_fran: date, artiklar: tuple[Artikelrad,...])`. CLI `regelbas validera-utkast --utkast <rot>` visar strukturell täckning, inte operativ giltighet.

- [x] Skriv test att `valj` inte kan välja utkastpaketet på 2027-07-09, 2027-07-10 eller 2029-07-10. Utkast ska inte heller ändra dagens regelbassumma eller följa med dagens expertattest utan uttrycklig länkning.
- [x] Observera failure för saknad utkastvalidering. Ändra operativa `regelbasfiler` så att `utkast/` är uttryckligen exkluderat från dagens laddning/summor. Manifest för själva utkastet omfattar däremot alla dess filer.
- [x] Kartlägg samtliga artiklar och bilagor i AMLR som relevant/ej relevant/återstående, med motivering och motsvarande PTL/KRV. Prioritera artikel 10 och bilagorna I–III med delkrav för riskdimensioner, eget ansvar och uppdatering. Spara hänvisningar till artiklar om kundkännedom/rapportering/bevarande; anta ingen identisk tolkning av svenska undantag.
- [x] Håll antagen EU-förordning, kommande tillämpning, riktlinjeutkast och svenskt lagförslag som skilda statusar. Regeringens remiss och AMLA:s publiceringsläge kontrolleras igen vid genomförandet. 2027-07-10 är inget automatiskt frigivningsdatum. Framtida frigivning kräver separat expertbeslut och svensk komplettering.
- [x] Kör kontrakten grönt och dokumentera kvarstående delar i paketets README. Detta avslutar M2:s start av parallellspåret, inte hela AMLR-leveransen.

### Uppgift 17: Hela kedjan och överlämning till M3

**Filer:** skapa `tester/typfall/test_m2_kedja.py`; ändra relevanta fixtures i `tester/conftest.py`, `docs/STATUS.md`, denna plans genomförandelogg.

**Gränssnitt:** befintlig CLI; endast syntetisk kopia av komplett regelbas och byråprofil i temporär datamapp. Granskningspaketets import från uppgift 14 används för syntetiska expertbeslut.

- [x] Skriv subprocess-prov: ny → bekräftelser med perioder → bedom → skriv med testleverantör → granska → exportera utkast → sakgranska → faststall → verifiera. Kör för alla tre län med minst bokföring, skatt och en liten bolagstjänst; använd sökväg med mellanslag/åäö.
- [x] Skriv negativa CLI-prov för öppen AI-fråga, bekräftad uppgift utan källa, fel paket, gammal expertattest, ny giltighetsgräns och ogranskad metod/kundgren. Inget fastställt paket får skapas. Kontrollera även rättsligt undantag som inte gäller en vanlig skatterådgivningsuppgift.
- [x] Observera failure innan implementationen når denna uppgift. När delarna är färdiga körs hela sviten: `env -u ANTHROPIC_API_KEY .venv/bin/pytest -q` och `.venv/bin/riskanalys regelbas validera`. Redovisa faktiskt antal, bortvalda tester och alla fel.
- [x] Säkerhetskopiera syntetiskt paket, återställ i tom datamapp och verifiera byte-identitet/manifest. Inga betalda AI-prov behövs för detta.
- [ ] Kör strukturell kontroll av tillsynsmaterialet och dokumentera att dess 17 fynd inte ännu är produktutvärderade. Lämna sakkunnigbekräftat facit och tabell över manuella/automatiserade B-kontroller till M3; detektionsprov, kontrollvarianter och falska fynd blir M3:s grind före M5.
- [x] Uppdatera STATUS med tekniskt färdigt respektive juridiskt granskat, inga löften om att bäst resultat bevisats. M3 jämför mot manuellt arbete och mäter sakfel, granskningstid och kostnad.

### Uppgift 18: Verklig sakkunniggranskning och beslut

**Filer/underlag:** export från uppgift 14 utanför repot, `docs/STATUS.md`, versionerade signaturer efter verkligt godkännande, facitets versionsanknutna granskningsbeslut.

**Gränssnitt:** `Granskningsbeslut` från uppgift 14. Detta steg är en mänsklig handling och ersätts inte med ett pytest-prov.

- [ ] Användaren utser en oberoende sakkunnig med kompetens om PTL/länsstyrelsetillsyn samt en tänkt användare inför M3–M4. Dokumentera vem som är sakkunnig, granskningens omfattning och om tillsynsbeslutens rättsliga status verifierats.
- [ ] Granskaren kontrollerar full inventering, tillämplighet per tjänst/yrkesroll, samtliga A–D-grenar och undantag, sanktioner, datum, metod, källspår och referensskala. Tabell 1 i tre PDF:er och NRA:s grafik granskas visuellt. Domstolsavgöranden får läggas till efter att original har lästs.
- [ ] Granskaren bekräftar/reviderar de 17 facitfynden och fem varianterna mot bevarade original; dokumenterar manuella punkter. Ingen rå OCR förs in i AI-underlag eller offentligt Git.
- [ ] Revidera underlaget enligt kommentarer, kör berörda kontrakt och exportera på nytt. Tidigare summa gäller inte för ändrade objekt. Importera endast en verkligt godkänd granskningsfil.
- [ ] Kör grinden på nytt och redovisa vilka paket/versioner/datum som godkänts. Markera M2 klar först om allt tillämpligt är granskat; lämna annars tekniskt arbete klart och sakkunniggranskningen som kvarstående.

## Restpunkter från M0–M1

| Punkt | Placering och skäl |
|---|---|
| a Sakgranskning före granskning | M4: samlad kontroll av faktiska tidsstämplar. Befintlig beslutsdatumgrind behålls. |
| b Framtida datum och efterdaterad utvärdering | M4: datumpolicy i drift och användningsprov. M2:s rättsliga giltighet i uppgift 13 är en separat kontroll. |
| c Tom utvärderingsbeskrivning | M4: minsta drift. |
| d FfR ej tillämplig och osynligt namnkrav | Uppgift 6 och 8. |
| e Andelen `1`, engelska argparse-fel | Andel i uppgift 5; samlad svensk CLI/formulärhjälp i M4. |
| f Omarkerad ändrad arbetskopia | Uppgift 15. |
| g Fsync och direkt överskrivning | M4: driftsäkerhet före riktig byrå. |
| h Skadade körningsmanifest/irrelevanta gamla utkast | Uppgift 15. |
| i Lydelse mellan bedömning och beslut | Uppgift 13. |
| j Lokal körningsordning vid vintertid | Uppgift 15. |
| k Installation förutsätter repo | M4: paketering och återställningsprov på tom installation. |
| l Stackspår vid trasiga filer/villkor | Uppgift 15. |
| m Oklarheter med påhittat fält | Flyttas från M3 till uppgift 8 eftersom M2 utökar fältregistret. |

## Vad som kräver ett verkligt beslut

- **Sakkunnig:** rättslig verksamhetskategori, motsvarande länskrav, sektormotiveringar, rapporteringsundantag, sanktionsartiklar och rättsverkningar. Dessa blir inte godkända genom denna plan.
- **Sakkunnig och metodansvarig:** tjänsternas grundnivåer, NRA-skalmappning, kundpoäng, gränser, vikter, kontrollernas sänkning och kombinationsfaktorer. M3 behöver dessutom faktisk validering mot manuellt arbete.
- **Användaren:** vem som granskar och vilken syntetisk referensprofil som representerar den första byråns arbetssätt. Detta blockerar expertattesten, inte teknisk implementation med syntetiska uppgifter.
- **Efter publicerad rätt:** AMLR-paketets framtida frigivning och svensk komplettering. Remiss och utkast får inte användas som bindande rätt.

## Arbetsestimat

Planeringsantagande, inte en leveransgaranti: uppgift 1–4 cirka 3–5 arbetsdagar, 5–9 cirka 4–6, 10–14 cirka 4–7, 15–17 cirka 2–4. Summa tekniskt arbete och egen verifiering **13–22 arbetsdagar** för en byggare, med delvis AI-stöd. Sakkunniggranskning uppskattas till ytterligare 2–5 arbetsdagars aktiv granskning samt väntetid och omarbete. Om sanktionstillämpning eller källåtkomst kräver ytterligare utredning ökar tiden. M3–M4 och hela AMLR-spåret ingår inte i estimatet.

## Självgranskning och verifiering av planeringsarbetet

- Specens M2-delar har uppgifter: källor/giltighet 1–4/13, krav/paragrafkarta 4, profiler/tjänster 5–6, sektorsrisk 7, AI/täckning 8, sanktionsdimension 9, kundmall 10–12, expertgranskning 14/18, provenance/fel 15, AMLR 16, kedja/återställning 17.
- Planens kontrakt använder befintliga M1-signaturer där de behålls. Nya modeller/gränssnitt anges i den uppgift som producerar dem. Exempel på juridiska grenar är granskningsunderlag, inte färdiga juridiska beslut.
- Fynden från Codex granskning är hanterade: 4 kap. 8 §, PTL 7 kap., SFS-verktygets dispatch och avgränsningen av punkt 23. Ytterligare risker har fått egna kontrakt: tredje stycket i 3 kap. 17 §, smågruppsandelar, AMLR-utkast efter datumgränsen och ändrat expertunderlag.
- Tekniskt verifierat under planeringen: nio researchverktygstester, åtta observerat röda före rättningen; SFS/FS-prov mot lokalt hämtade källor; källmanifestets tio SHA-256; tre bevarade M1-paragrafsummor. Det visar verktygsfunktionen, inte att alla extraherade juridiska texter är felfria.
- Tabell 1 i de tre länsföreskrifterna jämfördes visuellt på originalens PDF-sidor 5–6. Samma kontroll- och dokumentationskrav observerades i alla fem rader; radbrytningar, sidbrytningar och rubriklayout skiljer sig. Sakkunnigs tolkning och attest i uppgift 18 återstår.
- Färsk fullsvit under planeringsarbetet: **504 passerade, 1 livtest bortvalt** (2026-10-10, utan API-nyckel). M2:s framtida testkontrakt ovan har inte genomförts eller provkörts.

## Nästa handling

Granska denna plan innan programimplementationen påbörjas. Börja sedan med uppgift 1 enligt `executing-plans`, i befintlig arbetsgren eller en uttryckligt vald ny gren. Sakkunnigstatus förblir `ej_granskad` tills uppgift 18 faktiskt är genomförd.


## Genomförande 2026-10-10

**Tekniskt M2-underlag:** implementerat i arbetskopian på `codex/m0-m1`; slutlig fullsvit är grön (800 passerade, 1 livetest bortvalt). Ingen commit eller push har gjorts i denna omgång. **M2 som juridiskt godkänd etapp är inte klar.** Produktionsbasens paket, kartor, krav, metodval och kundgrenar förblir `ej_granskad`. Uppgift 18 måste utföras av en verklig sakkunnig.

### Levererat

| Uppgifter | Resultat |
|---|---|
| 1–4 | Regelbas `1.0.0`: 107 krav, 11 tjänster, 264 inventerade svenska datumlydelser (PTL 142/141 lagrum, PTF 29 och 31 per föreskrift). Tre paket med 201 hanterade paragrafer vardera; daterat urval per lydelsens källgeografi. Dokument, drift och kundmall har typade mål. Hanterad betyder redovisad hantering, inte juridiskt godkänd tolkning. |
| 3/5–6 | Tillsyn efter säte/filial och faktisk yrkesverksamhet, öppna avgränsningshinder för verksamhet som stödet inte omfattar. Periodbundna antal/intäkter med härledda andelar, belägg och kontroller mot dubbelräkning. Tjänster med separata erbjudanden, riskfaktorer och kontroller. Gamla erbjudandefält läses som alias utan omskrivning av profilen. |
| 7–9 | NRA:s originalskala bevarad; skalmappning är ett ogranskat metodval. B-13 hittar avsaknad av lokal belagd motivering, medan kvaliteten kräver sakgranskning. Separat sanktionsdimension och kontroll, visad i motor, AI-underlag och sakgranskning. AI får strukturerade tillåtna uppgifter; små kundgruppers antal, intäkter och intäktsandelar skyddas. |
| 10–12 | 21 kundrader i A–D med egna undantag, datum, lydelser och C→A/B-beroenden. Alla rader har positiva, negativa och okända kontraktsprov. PEP prövas med kalendermånader och kvarstående risk. Avgränsad EU269 artikel 2-gren kräver mänsklig bekräftelse av tillämplighet; möjlig träff/ofullständig utredning ger preliminärt resultat. Ingen kunddatabas, automatisk screening eller rapportering. Ingen generell C-produktionsformel har frigivits. |
| 13–15 | Grinden prövar profil, omfattning, metod/kundattester och verkligt beslutsdatum, även vid bortfallna krav och kundraders giltighetsgränser. Sakkunnigexport/import är innehållsbunden och import publiceras genom ett atomiskt namnbyte av en attestfil. Flera paket bevaras; en inaktuell annan paketattest upphäver inte aktuella gemensamma attester. Manifest innehåller programkodsumma och ren/ändrad/okänd arbetskopia; UTC-ordning och svenska återställningsfel. |
| 16 | AMLR-utkast med 90 artiklar och sex bilagor samt eget verifierat manifest. Artikel 10 och bilagorna I–III prioriterade; 92 poster återstår. Utkastet påverkar inte operativ checksumma och följer inte med ett fastställt dagens paket. Framtida datum frigör det inte. |
| 17 | Kommandokedjan och byteidentisk återställning prövade i alla tre län med signerade syntetiska kopior, tre erbjudna tjänster och sökväg med mellanslag/åäö. Negativa kommandoprov för fråga, belägg, fel paket, utebliven expertattest, ogranskad C, ändrat datum och äldre bedömning. Riktig kundinformation har inte använts och inga API-anrop har gjorts. |
| 18 | Tre ogranskade exporter finns i `../underlag/sakkunnig-m2-2026-10-10/{vg,skane,stockholm}/`, samtliga med verifierade manifest. Verklig sakkunnig och juridiskt godkännande återstår. |

### Verifiering och slutgranskning

Baslinje: 504 passerade och ett livetest bortvalt. Fristående slutgranskare hittade fyra konkreta brister: läsning av handändrad attestmetadata, ofullständig sanktionsutredning, datumgrindens tabeller/bortfall och olika aliasbesked i motor/dokument. Alla rättades med regressioner som fallerade före rättningen. Återkontrollen bekräftade rättelserna och hittade en flerpaketsregression; båda läsordningarna är nu regressionstestade. Intäkternas smågruppsskydd, B-13:s rättsliga grund och AMLR:s separata manifest har också regressionsprov.

Första fullsviten efter integration: 2 fel, 794 passerade, ett livetest bortvalt (208,43 s). Felen gällde testsvarsfilens feltyp och den utökade rollistan i ett gammalt test. Båda rättades; 53 berörda enhetstester passerade. **Färsk fullsvit efter samtliga rättelser: 800 passerade, 1 livetest bortvalt (223,47 s)**, utan API-nyckel. Elva CLI-testfall passerar: tre positiva kedjor med återställning, sju negativa fastställelser och ett negativt beläggsprov vid bedömning. Ingen fastställelse skapas i negativa prov.

`regelbas validera`: giltig v1, 107 krav, 11 tjänster, 201/201 hanterade paragrafer per paket, alla kartor `ej_granskad`. `regelbas validera-utkast`: 96 inventerade artiklar/bilagor, 92 återstående. Tillsynsmaterialets struktur och arkiv kontrollerade: två fall, 17 fynd, fem varianter, 14 dokument, 79 original och 173 korrekta kontrollsummor. **Detta är materialkontroll, inte produktutvärdering av de 17 fynden.**

### Beslut under genomförandet och kostnader

1. Befintlig arbetskopia på `codex/m0-m1` behölls så tidigare plan- och researchändringar följde med. Kostnad: arbetet är inte isolerat i en ny checkout.
2. Svenska uppgiftsrubriker följs med manuellt extraherade briefar och logg; inga automatiska commits eller radering av arbetsloggen. Kostnad: manuell bokföring måste stämmas av mot 18 uppgifter.
3. M1-kontrakten använder en fryst regelbas från exakt bascommit `77c147f`; nya M2-tester använder dagens verkliga v1. Kostnad: två fixtures kräver underhåll; M1-grönt betyder inte att v1 är granskad.
4. Expertimport använder en atomisk attestfil med flera paket, i stället för att skriva många rättsliga YAML-filer var för sig. Kostnad: läsaren måste applicera och validera attestregistret; identitet/kompetens verifieras utanför programmet.
5. En ny körningsmapp utan manifest stoppar i stället för att tyst falla tillbaka till ett äldre resultat. Kostnad: avbruten körning kan behöva återställas eller flyttas undan innan nästa steg.
6. AMLR:s inventarium omfattar sex bilagor enligt källan. Kostnad: större kvarstående kravkarta än om enbart riskbilagorna I–III inventerats.
7. CLI-kedjan förladdar övrig syntetisk profil som testfixture och gör två verkliga periodbekräftelser genom CLI. Kundundantagens kontrakt prövas i den separata mallutvärderaren, eftersom fas 1 inte har en kund-CLI. Kostnad: detta är inte ett användningsprov av manuell inmatning av samtliga profilfält.
8. EU269 artikel 2 sparas som tydligt märkt återgivet engelskt EUT-utdrag, inte som ett påstått nedladdat PDF-original. Kostnad: sakkunnig måste läsa autentiskt original, bekräfta lydelse/datum och avgränsa ägande, kontroll och undantag innan godkännande.

### Överlämning till M3 och verklig granskning

Den öppna checklistan i uppgift 17 gäller det **sakkunnigbekräftade facitet**. Strukturkontrollen är utförd; juridiskt godkännande av facit återstår i uppgift 18. Inga av de 17 tillsynsfynden påstås upptäckta av produkten.

| B-kontroller | Teknisk funktion nu | Vad M3 måste mäta eller en människa pröva |
|---|---|---|
| B-04 | Eget avsnitt för varje erbjuden tjänst | Individuell analysens sakliga kvalitet |
| B-12 | Motivering med hot- och sårbarhetsreferenser | Om sambandet och risknivån är rimliga |
| B-13 | Saknad belagd sektorsmotivering vid avvikelse/ogranskad jämförbarhet | Mappningens riktighet, motiveringens innehåll, falska fynd |
| B-16 | Saknat datum för utvärdering | Verklig uppdatering och driftbevis |
| B-01–03, B-05–11, B-14–15, B-17–29 | Katalog och underlag; ingen bevisad automatisk detektion | Manuell sakgranskning nu, vald automatisering och detektionsprov i M3 |

Sakkunnig ska granska originalinventarium/ikraftdatum, tre FS-tabeller, NRA-grafik, yrkesroller, samtliga undantag och metoder samt facitets 17 fynd/fem varianter. Källåtkomst och tillsynsbeslutens laga kraft/domstolsstatus är öppna juridiska kontrollpunkter. Kund-C måste kompletteras och prövas som metod; ett syntetiskt konstant normalutfall används enbart i CLI-testerna.

**Mindre uppskjutna granskningsfynd:** inga nya sådana från den tekniska slutgranskningen. Planerade M4-restpunkter a–c, argparse-språkdelen av e, g och k ligger kvar i tabellen ovan. Verklig expertattest och metodvalidering är obligatoriska återstående etapper, inte uppskjutna småfel.

### Rättelser efter Claudes granskning 2026-10-10

Granskningen reproducerade versionsbortfall, tyst förlust av äldre andelsbelägg och okänt paket vid import. Codex reproducerade också facitkopplingen, spår A:s riskhanteringsundantag, ordningsberoendet vid motstridiga sakkunnigbeslut och små komplement. Regressionerna fallerade före respektive rättelse; loggar finns i den lokala arbetsloggen. Kompletterande prov kontrollerar explicit ombekräftelse, faktisk CLI-import av facit, bevarade juridiska attester efter facitrevision och upplösning av en lokal granskningskonflikt.

| Fynd | Rättelse / avgränsning |
|---|---|
| M2-skydd upphör vid 2.0.0 | `Regelbas.utokade_krav` gäller alla innehållsversioner med huvudversion minst 1. Versionen kräver numeriskt format X.Y.Z. Ingen ny framtida datastruktur godtas genom detta: modell- och referensvalideringen gäller fortfarande. 2.0.0 och 10.0.0 prövas. |
| Äldre andel raderas av annan bekräftelse | Värde, källa, datum och bekräftare bevaras med `inaktuell: true`. Uppgiften är okänd i motorn och AI-underlaget och stoppar grinden. Antal/bas måste uttryckligen bekräftas för att ersätta en äldre manuell andel. |
| Facitbundna regelpaketsattester | Facitet får en separat beslutsmodell, version och innehållssumma. Dess 22 objekt ingår inte längre bland regelpaketets 194 granskningsobjekt eller i operativ checksumma. En facitrevision kräver ny facitgranskning; den upphäver inte juridiska paketattester. M3 måste läsa och verifiera facitbeslutet mot exakt facit före användning. Ingen facitattest finns nu. |
| Dubbla facitfiler | `docs/research/typfall/tillsyn-2026.json` är kanonisk. `regelbas/referensdata/facit.json` är en relativ symbolisk länk. Exporter och frysta paket innehåller egna manifestbundna ögonblicksbilder. |
| Spår A:s 3:1-undantag | Kandidatraderna KA-1-UNDANTAG, KA-RISK-STOPP och KA-C-HOG prövar undantaget för hela första stycket, även riskhantering. Självständiga etablerings-/transaktionsstopp och sanktionsstopp består. Källa: [PTL 3 kap. 1–3 §§](https://rkrattsbaser.gov.se/sfst?bet=2017:630), kontrollerad 2026-10-10. Regeländringen är fortsatt `ej_granskad`; sakkunnig prövar den före frigivning. |
| Okänt paket ger stacktrace | Import och export stoppar med `RiskanalysFel`, paket-ID och svensk anvisning. Export skapar ingen mapp vid ogiltigt paket. |
| Svårläst kärnkod | Sakkunnigimport, M2-validering, kundutvärdering, PEP, kundrader och andelshärledning har tydligare kontrollflöden, typer och funktionsbeskrivningar. Oanvända importer rensade; kundmodellens avsiktliga återexport deklarerad. Ingen linter har installerats och ingen pyflakes-körning påstås. |
| Granskarens identitet i offentligt Git | `/regelbas/granskning.yaml` och `/regelbas/facitgranskning.yaml` undantas av `.gitignore`. Beslut och identitet bevaras lokalt i arbetsmaterial, frysta paket och säkerhetskopior. M4 behöver omfatta åtkomst och gallring av dessa personuppgifter. |
| Motstridiga beslut om gemensamma objekt | Ett aktuellt `ändras` gäller framför `verifierad` oavsett paketordning. Berörda paket stoppas tills besluten samordnats, ersatts och lästs in på nytt. Fyra konfliktriktningar/läsordningar samt faktisk lokal återinläsning prövas. |
| Små komplement kan räknas ut | Ett komplement på 1–4 kunder undertrycker gruppens antal, andel och kopplade tjänstbelopp i AI-underlaget. Bas och antal måste avse samma period. 97 av 100 prövas för kundtyp och tjänst. Detta är begränsat gruppskydd; korsvisa slutsatser från flera kategorier eller risknivåer behöver fortsatt prövas i M4. |
| Rapportering i D och andra okända uppgifter | Två kompletterande prov visar att bekräftad rapportering består när andra utredningsfält är okända. Okänt uppgiftsskydd ger fortfarande preliminärt utfall. Ingen ny rättslig prioriteringsregel införs; sakkunnig granskar framtida radkonflikter. |

**Ändrat beslut för uppgift 14/18:** Paketgranskning och facitgranskning är två separata lokala attester. Exporten innehåller nu också `facitgranskningsmall.yaml`; `regelbas importera-facitgranskning <fil> --regelbas <rot>` importerar enbart facitbeslutet. Alla facitobjekt kräver beslut och kommentar, identitet, kompetens, oberoende och datum. En `ändras`-post kan registreras men är inget godkännande för M3. Juridisk paketgranskning har sin egen import och frigivningsgrind. Kostnad: M3 måste kontrollera den fristående facitattesten, och beslut med identitetsuppgifter måste förvaltas lokalt.

Tidigare exporter i `../underlag/sakkunnig-m2-2026-10-10/` bevaras som historiska och ska inte användas för den rättade regelbasen. Nya exporter tas fram i `../underlag/sakkunnig-m2-2026-10-10-r2/`. Allt är fortsatt lokalt och ogranskat av verklig sakkunnig. Ingen commit/push eller betald AI-körning görs i denna rättelseomgång.

**Slutlig verifiering efter samtliga kodrättelser:** `env -u ANTHROPIC_API_KEY .venv/bin/pytest -q` → **832 passerade, 1 livetest bortvalt, 278,71 s**. Exitkod 0. Operativ regelbas giltig, AMLR 96 poster/92 återstående, tillsynsarkivets 173 kontrollsummor stämmer. Kompileringskontroll och `git diff --check` passerar. Tre r2-exporters manifest stämmer och alla 194 + 22 beslutsfält per export är fortfarande obesvarade. Ingen faktisk sakkunnigattest eller produktutvärdering av facitet har tillkommit.

### Kontroll inför begärd commit/push 2026-10-10

En ny läsande kodgranskare fann en P2 i konfliktgrinden: ett gemensamt krav kunde ha ett aktuellt ändringskrav i Skåne men ett lokalt godkännande i VG, och om kravet var inaktivt för byråns profil uteblev spärren i VG. `attesthinder` omfattar nu samtliga krav i paketets granskning, oavsett profilens `galler_om`. Fyra regressioner med `KRV-PTL-2-9` och `P-ORG.koncernmoder=False` fallerade före rättningen och prövar båda avvisande paket och båda läsordningar, inklusive fastställelsens `_m2`-grind.

Git:s indexkontroll hittade layoutblanksteg i fyra frysta källuttag och en överflödig slutrad i en syntetisk fixture. Källuttagens bytes behålls för deras SHA-256-spårning. `.gitattributes` avgränsar whitespacekontrollen och newlinekonverteringen enbart för `regelbas/kalltexter/*.txt`; kod och redigerade dokument omfattas av den vanliga kontrollen. Fixturens extra slutrad togs bort med identisk AST. Den första testkörningen inför commit avbröts när P2 hittades; en ny fullsvit körs efter rättningen.

Sakkunnigunderlagets lokala README har fått en granskningsmatris och återlämningschecklista. Råunderlag och lokala beslut med personuppgifter följer inte med till offentligt Git.

**Färsk verifiering inför commit/push efter den sista konfliktgrindsrättelsen:** `env -u ANTHROPIC_API_KEY .venv/bin/pytest -q` → **836 passerade, 1 livetest bortvalt, 261,79 s**, exitkod 0. Elva riktade konfliktprov passerar. Den fristående läsande återgranskningen fann inga kvarvarande P1/P2 i de granskade kärnflödena. Git:s indexkontroll passerar. Alla tre r2-underlag motsvarar dagens regelbas och deras innehållssummor och manifest stämmer. Detta är en teknisk baslinje; inga verkliga sakkunnigbeslut har tillkommit.
