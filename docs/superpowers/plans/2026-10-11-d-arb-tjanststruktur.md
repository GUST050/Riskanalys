# H5 – verksamhetsanpassad tjänststruktur för D-ARB

> **För genomförande:** använd Superpowers `executing-plans`, arbeta inline med tester före kod. **Användaren ska granska planen innan H5 byggs.** Inga commits eller push utan en ny uttrycklig begäran.

**Mål:** ett läsbart Word-utkast där varje erbjuden tjänst har en sammanhängande analys och underlagsredovisningen ligger i en sakgranskad bilaga.

**Arkitektur:** behåll D-ARB och befintliga riskavsnitts-ID:n `D-ARB.6.n`, regelmotor, AI-schema och lokalt sparade skrivförsök. Sammanställ en tjänsts beskrivning, hot/erfarenheter, sårbarheter, kontroller, riskmotivering och slutsatser i samma avsnitt. Numrering och Word-rubriker får inte ersätta stabila ID:n. Allmänna principer, metod, kontrollsammanställning och uppföljning ligger kvar före/efter tjänstanalysen. Byråns fritext återges lokalt som uppgift från byrån; den blir inte automatiskt en verifierad analys.

**Teknik:** befintlig Python 3.12+, Pydantic, PyYAML, python-docx och pytest. Testleverantor, inga betalda AI-anrop eller verkliga byråuppgifter. Inga nya beroenden.

**Spec:** `docs/superpowers/specs/2026-10-08-riskanalys-design.md` §7–11, §14 och §16; `docs/research/11-kallkontroll-allman-riskbedomning.md` §3.5–3.9. H1/H2:s tekniska rättelser ska vara verifierade före omstruktureringen.

## Gemensamma begränsningar

- AI fattar inga beslut. Risknivåer och metodval kommer från regelbasen och riskmotorn.
- Inga personuppgifter eller beskrivande fritext till AI. Tillåtelselistan och smågruppsskyddet gäller även efter flytten till bilaga.
- Alla nya regelbasposter har källhänvisning och grund. Gränser/poäng/effekter är metodval; sakkunnigstatus förblir `ej_granskad`.
- Byrådata ligger utanför repot i `$RISKANALYS_DATA`.
- Fastställelse kräver aktuell juridisk/metodisk attest, belagd profil, hanterade fynd och sakgranskning av det faktiskt renderade dokumentet.
- Gamla exporter, manifest, fastställda paket och granskningar ändras aldrig på plats. Ett gammalt sakgodkännande får inte gälla ett nytt dokumentformat.
- Ingen sammanvägd byrånivå byggs här. Spec §7.4 ska beskriva tjänstevis redovisning som dagens leverans och eventuell framtida sammanvägning som separat metodutvärdering.

## Granskningsfokus

1. En liten högrisktjänst får inte döljas av mer omfattande lågrisktjänster: eget fullständigt avsnitt och egna slutsatser.
2. Noll rapporter och noll utlandstransaktioner får inte återges som frånvaro av hot/geografisk risk.
3. Fritext med ett syntetiskt personnamn får finnas lokalt men inte i AI-underlaget eller återkopplingen.
4. Flyttad källa, ändrad ordning, underrubrik, bilaga eller lokalt infogat namn måste ogiltigförklara tidigare sakgranskning.
5. Utkast med okända fakta, öppna frågor eller saknad effektbedömning får inte bli ett fastställt dokument genom en ny export.

## Föreslagen disposition

1. Syfte, ansvar och avgränsning (`D-ARB.1`).
2. Metod och motiverad omfattning utifrån verksamhetens storlek/art (`D-ARB.2`, M1).
3. Tjänsteöversikt med faktiskt erbjudna tjänster och omfattning (`D-ARB.3`).
4. Gemensamt myndighetsunderlag och egna erfarenheter (`D-ARB.4`), utan att upprepa intervjuns frågor.
5. Gemensamma riskförhållanden och analysens begränsningar (`D-ARB.5`).
6. Kontrollernas utformning, genomförande och dokumenterade effekt (`D-ARB.7`, **före riskavsnitten**, M3).
7. Ett avsnitt per tjänst (`D-ARB.6.n`) med sex underrubriker: **Beskrivning och omfattning; Hot och egna erfarenheter; Sårbarheter och motivering; Kontroller och effekt; Risknivåer och motivering; Slutsatser**.
8. Tjänstevis risksammanställning (`D-ARB.8`).
9. Konkreta följder för rutiner, kundkännedom, övervakning och utbildning (`D-ARB.9`, M2).
10. Utvärdering, uppdateringsgrunder och spridning (`D-ARB.10`).
11. Omvärldsbevakning (`D-ARB.11`, M4): faktiskt lästa källor, datum, ansvarig och dokumenterad relevans; hämtning är inte genomförd bevakning.
12. **Underlagsbilaga** (`D-ARB.B1`): bekräftade fakta, källor, perioder, beräkningsbaser, fråge-ID:n, granskningsfynd och öppna kompletteringar. Bilagan ingår i sakgranskning och kontrollsumma.

Exempel med syntetiska fakta: huvudtexten skriver ”Tjänsten avser löpande bokföring för 10 av 100 kunder under januari–september. Byrån har inte identifierat utlandstransaktioner i kundunderlaget för perioden; detta utesluter inte andra geografiska riskfaktorer.” Bilagan visar de bekräftade antalen, perioden, källhänvisningen och aktuella geografiska bedömningar. Det blir inte ett påstående om att alla tio kunder säkert saknar geografisk risk.

## Uppgift 1 – versionsbundet dokumentformat

**Filer:** `src/riskanalys/dokument/modeller.py`, `rendering.py`, `arb.py`; `tester/enhet/test_rendering.py`, `test_arb.py`, `test_sakgranskning.py`.

**Gränssnitt:** lägg till lokala `Underrubrik(fore_stycke: int, rubrik: str)` och `Avsnitt.underrubriker: tuple[Underrubrik, ...] = ()`. AI:s `AvsnittsUtkast` och `Textstycke` ändras inte. Underrubriker ingår i avsnittets innehållssumma och rendering. Dokumentformatets version registreras i export/granskningsmetadata; äldre format kan fortfarande läsas och verifieras.

- [x] Skriv prov för sex rubriker, felaktig position och ändrad rubrik/ordning som ogiltigförklarar sakgodkännande.
- [x] Kör proven RED; bygg modellen och Word-renderingen.
- [x] Kör proven GREEN samt befintliga rendering-/sakgranskningsprov.

## Uppgift 2 – samla tjänstens analys utan att flytta AI:s beslut

**Filer:** ny `src/riskanalys/dokument/tjanstavsnitt.py`; ändra `arb.py`, `analysunderlag.py`, `intagsunderlag.py`; `tester/regelkontrakt/test_arb_tjanststruktur.py`.

**Gränssnitt:** `bygg_tjanstavsnitt(regelbas: Regelbas, profil: Profil, tjanst: Tjanstbedomning, utkast: AvsnittsUtkast, avsnitt_id: str) -> Avsnitt`. Återanvänd H1/H2:s deterministiska erfarenhets- och sårbarhetsstycken. AI:s godkända riskmotiveringar läggs bara under Risknivåer och motivering. Lokal beskrivning märks som byråns uppgift. Antal/andelar återges endast med aktuellt belägg och samma period.

- [x] Skriv prov för två olika tjänster, en liten högrisktjänst, noll rapporter, obekräftad geografi och lokal syntetisk fritext.
- [x] Kör RED, implementera sammansättningen och kör GREEN.
- [x] Säkerställ att risknivåerna är byteidentiska mot motorns resultat och att varje källa hör till rätt tjänst.

## Uppgift 3 – underlagsbilaga och kravtäckning

**Filer:** `dokument/intagsunderlag.py`, `dokument/omfattning.py`, `granskning/analys.py`, `regelbas/mal.yaml`, berörda krav-/intagsreferenser; `tester/regelkontrakt/test_dokumentomfattning.py`, `test_arb_tjanststruktur.py`.

**Gränssnitt:** `bygg_underlagsbilaga(regelbas: Regelbas, profil: Profil) -> Avsnitt` med ID `D-ARB.B1`. En flytt till bilagan får inte ensam uppfylla ett analyskrav. B-15 ska kräva egen erfarenhetsanalys per erbjuden tjänst; B-09/B-10 kräver underlagsbunden geografisk analys i respektive tjänstavsnitt. Registrera de exakta nya dokumentmålen och versionshöj regelbasen; inga attester återanvänds.

- [x] Skriv negativa prov: råa svar bara i bilagan, saknat tjänstavsnitt, felaktiga referenser och saknad bilaga.
- [x] Kör RED, flytta underlaget från huvudtexten till bilagan och anpassa maskinkontrollerna.
- [x] Kör GREEN och kontrollera att generiska formulärsvar inte räknas som analys.

## Uppgift 4 – effekt, omfattning och slutsatser (M1–M3)

**Filer:** `regelbas/falt.yaml`, källbundna metod-/kontrollposter, `bedomning/modeller.py`, `motor.py`, `dokument/tjanstavsnitt.py`, `arb.py`, `intag/tackning.py`; nya kontrakt i `tester/regelkontrakt/` och `tester/intag/`.

- [x] Källkontrollera vilka effektuppgifter som behövs per kontroll: period, genomförande, observerat utfall, bedömd verkan och begränsningar. ”Inga upptäckta avvikelser” bevisar inte effektivitet.
- [x] Skriv negativa prov för en genomförd men verkningslös kontroll samt saknad effektbedömning. Ingen riskreduktion innan metodvillkoren är uppfyllda; effektnivåer är ogranskade metodval.
- [x] Skriv prov för dokumenterad motivering av omfattningen från storlek och art. Inga godtyckliga lagpåståenden eller minskad kravtäckning för små byråer. Eventuella trösklar ska stå i regelbasen som metodval och prövas i M3.
- [x] Skriv prov för tjänstespecifika slutsatser: relevant kundkännedom, kontroll/övervakningsfokus, utbildningsinnehåll och fortsatt åtgärdsarbete. Byrån beslutar ansvar/tidsfrist; programmet hittar inte på genomförda åtgärder.
- [x] Kör RED/GREEN per beteende, dokumentera metodens kvarstående osäkerhet.

## Uppgift 5 – omvärldsbevakning och uppföljning (M4/L)

**Filer:** verifierade källor med lokalt manifest; `regelbas/falt.yaml`, `mal.yaml`; `dokument/arb.py`, `drift/historik.py`, intagskopplingar och tester.

- [x] Registrera bara myndighetskällor som hämtats, SHA-256-kontrollerats och lästs. Skilj nyhetsbrevets hänvisning från den refererade originalrapporten.
- [x] Skriv prov: hämtning räknas inte som läsning/utvärdering; ändrad källa eller relevansbedömning ogiltigförklarar godkännande.
- [x] Lägg till faktiskt utförd bevakning med källa/datum/relevans, spridning och uppdateringsgrunder (även hot/hämnd mot personal). goAML-förmåga och tidigare tillsyn behöver eget underlag.
- [x] Domarna 12554-25, 842-26 och 1129-26 används först efter att original erhållits. Beslutsöversiktens referat är inte domtext eller fullständig prejudikatkontroll.
- [x] Kör RED/GREEN och uppdatera spec §7.4 utan att bygga sammanvägd byrånivå.

## Uppgift 6 – hela kedjan och överlämning

**Filer:** `tester/intag/test_kedja.py`, `tester/m2/test_m2_kedja.py`, `tester/enhet/test_sakgranskning.py`, `docs/STATUS.md`, designspecifikationens befintliga dokumentavsnitt.

- [x] Pröva skapa utkast → maskinell granskning → sakgranska samtliga avsnitt/bilaga → fastställ med syntetiskt signerad testkopia → verifiera → återställ för tre tillsynspaket.
- [x] Pröva ändrade namn, källor, underrubriker, tjänsteordning och bilaga: tidigare sakgodkännande ska sluta gälla; historiska paket förblir verifierbara.
- [x] Kontrollera verklig DOCX-struktur med python-docx: underrubriker, kontrollavsnitt före riskavsnitt, underlag i bilaga, synlig UTKAST-status och inga dubbla intervjufrågor i huvudtexten.
- [x] Kör `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest`, regelbasvalidering, compileall och diff --check. Redovisa varje resultat; sakkunniggranskning och M3/M4:s verkliga prov kvarstår.
- [x] Uppdatera STATUS och visa det konkreta syntetiska Word-utkastet för användaren. Ingen commit/push utan begäran.

## Självgranskning

Planen täcker H5 och dess direkta beroenden M1–M4/L, utan att säga att H3/H4 är lösta av layout. H3/H4:s källbundna fält/kataloger är en tidigare separat leverans. De fem granskningsriskerna ovan har prov i uppgift 1–6. Ingen juridisk attest, riskpoäng från rapportantal, AI-tolkning av fritext eller historisk paketomskrivning införs. **Planen godkändes av användaren 2026-10-11 före H5-implementation.**

## Genomförandelogg 2026-10-11

H1/H2: 21 prov RED, sedan GREEN; fokuserad regression 103 passerar. H3/H4/H5/M1–M4: 31 nya prov RED, separat proportionalitet 4 RED; 56 passerar efter implementation. Slutlig full svit: 1090 passerar, 1 livetest bortvalt, 642.79 s.

Pre-flight: uppgift 1/2 delar Avsnitt.underrubriker; lokal schemautökning ändrar inte AI-schemat. Uppgift 2/3 delar stabila D-ARB.6.n; B-09/B-10/B-15 flyttas till tjänstavsnitten. Uppgift 4/5:s nya profilfält måste aktiveras i intaget och ingå i bilagan. Uppgift 6 använder samma renderade avsnitt och manifest som sakgranskning.

Ruling: Arbeta i befintligt dirty checkout på codex/m0-m1; tidigare ändringar bevaras med startbackup, inga commits görs eftersom användaren förbjudit dem utan fråga. Kostnad vid fel är sammanblandning med tidigare ändringar; slutgranskningen avgränsas till denna leverans.

Ruling: Samma fulla tjänsteanalys för alla proportionalitetsnivåer, med fler hypotetiska scenarier vid utökad nivå; ingen juridisk kravtäckning minskar. Trösklarna är nya ogranskade metodval i BT-OMF-01, ska prövas i M3. Kostnad om fel: olämplig analyslängd/uppföljningsnivå.

Ruling: H3:s 18 indikatorer används konservativt byråövergripande per erbjuden tjänst, med uttrycklig metodmotivering och separat tjänstevis sakprövning. De anger inte att alla tjänstens kunder omfattas. Kostnad om fel: överskattad tjänsterisk och behov av tjänstevisa indikatorer i kalibreringen.

Källhinder: FATF-PDF:s filhämtning ger HTTP 403 trots läsbar officiell webbrendering; ingen originalsumma eller katalogpost tillskrivs den. Tre domars original har inte återfunnits offentligt och används inte som egen rättspraxis.

Uppgift 1–5: tekniskt implementerade. Prov samlade i `test_arb_erfarenhet_motivering.py` och `test_arb_utvidgning.py` i stället för planens flera nya filnamn; renderings- och sakgranskningsregressioner återanvänds. 91 fokuserade prov passerar efter slutgranskningens fixpass. Uppgift 6: separat M2-CLI-prov 11 passerar, tre länspaket och återställning. Syntetiskt Word: 14 avsnitt, tre tjänster/18 underrubriker, 342 stycken, noll maskinfynd; endast teknisk demonstration. Slutlig helsvit: 1090 passerar, 1 livetest bortvalt, 642.79 s. Validering av 1.2.0, compileall och diff --check gröna.

Final: fixed ej_bedömd effekt — nytt regressionstest RED→GREEN; status preliminär, ingen reduktion och fastställelse stängd.

Final: fixed ändrad deterministisk tjänstanalys/sexdelad struktur — fyra regressioner RED→GREEN; maskingranskning jämför mot regenererat underlag och blockerar avvikelse. AI:s validerade riskmotivering och sakprövning kvarstår som separata steg.

Final: fixed historiska faktor-/kontrollperioder — två regressioner RED→GREEN; aktuellt belägg för nya indikatorer och kontrollverkan binds till kundunderlagets period.

Final: fixed exakt TF-källstöd — regression RED→GREEN; H-TF-02 hänvisar till fysiska PDF-sidor 1 och 2.

Final: Ruling: CLI:s dolda underrubriker omgraderas från Minor till Important eftersom sakgranskaren måste se den struktur godkännandet binder; prov RED→GREEN och rubriker skrivs vid sina styckepositioner. Kostnad om fel: mer utskrift, men ingen ändrad beslutsgång.

Final: Ruling: Kundunderlagets bekräftade period används som analysperiod för de nya faktorerna och kontrollernas effekt/genomförande. En annan period kräver nytt aktuellt underlag; inget godtyckligt ålderstak eller lagpåstående införs. Kostnad om fel: historiskt användbara kontroller måste kompletteras innan aktuell risk kan reduceras.

Final: Ruling: Juridiskt godkännande, metodtrösklar, kalibrering och kontrollernas tillräckliga täckning bedöms inte som tekniskt färdiga; sakkunniggrindar och M3/M4 kvarstår. Kostnad om detta skulle förbises: tekniskt resultat kan misstolkas som rättsligt godkänt.

Final: Ruling: FATF och de tre domarna används först efter verifierbart original. Kostnad: dessa delar av M4/L är ofullständiga; andra verifierade källor stöder den levererade TF-katalogen.

Final: Ruling: Fullsviten bedöms från ny körning efter avslutad kodändring, inte första körningen under bygge eller granskarens samtidiga fokusprov. Kostnad: ytterligare körtid, men samma slutliga kod testas.

Final: Ruling: Befintlig möjlighet att registrera sakgodkännande trots öppna fynd behålls; fastställelsen prövar fynd och preliminär status separat. Kostnad: godkända avsnitt kan finnas i ett ännu ofastställbart utkast; godkännandet är inget beslut om fastställelse.

Fristående slutgranskning utförd 2026-10-11; inga Critical. Alla identifierade Important rättade i en fixpass med RED→GREEN, inga uppskjutna Minor. Tolv nya PDF-summor kontrollerade både av implementerare och granskare; hela lokala tillsynsarkivets 173 filer matchar manifestet. Ingen ny verklig sakkunnigstatus eller commit/push.

Slutlig verifiering efter fixpass och korrigerad äldre integrationsförväntan: `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest` → 1090 passerar, 1 livetest bortvalt, 642.79 s. Regelbas 1.2.0 validerar, compileall och diff --check passerar. Uppgift 1–6 tekniskt klara; originalhinder och juridiska/metodiska granskningsgrindar ovan kvarstår. Inga commits eller push.

## H6 – kortare rapport med tabeller och separat metodspår, 2026-10-14

> **Ursprunglig genomförandeanvisning:** använd Superpowers `executing-plans`, arbeta inline med tester före kod. Genomförande och senare slutgranskning redovisas nedan; användarens senare beställning av subagenter ersatte inline-anvisningen. Ingen commit eller push utan uttrycklig begäran.

**Mål:** en kortare, läsbar och spårbar D-ARB där läsaren kan följa scenario → exponering → kontroll → kvarstående risk, utan ändring av motorns bedömningar.

**Arkitektur:** utöka den lokala dokumentmodellen med typade tabeller och läsbar numrering. Huvudrapport och underlagsbilaga ligger i samma Word-fil, med sidbrytning före bilagan. AI:s schema, tillåtelselista och befogenheter ändras inte. Lokal kod redovisar hur dagens motor räknade; detta är en beräkningsförklaring, inte ett påstående om att metoden är validerad.

**Teknik:** befintlig Python 3.12+, Pydantic, python-docx och pytest; inga nya beroenden. Testleverantor för automatiska prov.

**Spec:** befintlig designspecifikation, tillägget ”Planerad H6”; research 11 §8. Denna fortsättning ersätter H5:s presentationsordning vid implementation, men inte dess stabila ID:n, kravtäckning eller historiska godkännanden.

### Genomförande 2026-10-14

Användaren beställde implementation med subagenter och därefter fortsatt arbete. Det ersätter planens ursprungliga inline-anvisning. Gemensam befintlig `codex/m0-m1`-checkout har bevarats. Före ändring sparades alla tracked och icke ignorerade nya filer, staged/unstaged patchar och filhashar utanför Git. Baslinjen passerade med **1 557 tester, ett bortvalt livetest**. Ingen commit eller push.

Subagenter levererade modell/rendering/sakgranskning, skrivkontrakt och käll-/utfallsförklaringar. Separat Bolagsverksgranskning fann inget blockerande i avgränsningen (71 prov); en befintlig precisionsfråga vid mycket stora registerbelopp noterades utanför H6. Den avslutande oberoende granskningsagenten och skrivagentens sista kontroll stoppades av användningsgränsen. Huvudagenten integrerade, rättade och självgranskade resultatet; leveransen ska inte beskrivas som oberoende slutgranskad.

Implementerat: typade tabeller och visningsnummer, v5-summor som omfattar celler/referenser, gamla formats oförändrade serialisering, tjänste-/kontroll-/risk-/åtgärdstabeller, matris och tjänsternas beräkningar. Exakt identiska geografitabeller samlas gemensamt med tjänstehänvisning; skilda underlag slås inte samman. Kontroller beskrivs en gång och olika tjänstestatus bevaras. Reservtext efter stoppad AI innehåller fortfarande katalogens hot samt blockerande fynd. Den vanliga CLI-sakgranskningen visar samtliga tabellceller och referenser. En Word-fil innehåller B1 efter sidbrytning, navigeringsfält/direktlänkar och sidnummer.

Längdkontraktet är 400–750 ord per tjänst och riskdelen är kvalitativ. Alla tjugo delar i maxprovet passerade på första försöket. Rapportens totallängd mäts efter lokal insättning; överskridande ger synlig redaktionell varning, aldrig tyst kapning. Exportmanifestets ordmått är strängfält enligt befintligt manifestkontrakt.

| Mått, samma realistiska fiktiva profil | Före | H6 läsprov | H6 maxprov |
|---|---:|---:|---:|
| Huvudtext, samma modellmätning | 13 138 | 6 096 | 7 346 |
| B1 | 4 948 | 5 078 | 5 078 |
| Förberedda skrivsvar före lokal sammansättning | 3 264 | 1 750 | 3 000 |
| Riktiga Word-tabeller | 0 | 10 | 10 |
| Öppna höga fynd | 4 | 4 | 4 |

Det tidigare talet 18 167 gällde hela Word-filens text; modellmätningen är jämförbar före/efter och räknar inte navigation, sidhuvud eller exporterad fyndlista dubbelt. Fyrtjänstprovet behåller **exakt samma tjänstebedömningar och samtliga fyra gamla fynd**. Historiskt Word-utkast verifieras fortfarande. Tio tabeller omfattar matris, tjänster, gemensam geografi, kontroller, fyra beräkningstabeller, risköversikt och åtgärder. Kontrollbeskrivningarna identifieras med kontroll-ID; inga textsannolikheter används för sammanslagning.

**Kvarstående redaktionellt gap:** huvudrapporten når inte 3 500–5 000 ord / 8–12 sidor. Lokalt innehåll svarar för 4 346 ord i exemplet. Läsprovet renderas till femton sidor huvudrapport och femton sidor bilaga/fyndlista. Detta är inte ett godkänt längdmål eller ett verkligt AI-kvalitetsprov. Förberedda svar för läsprovet är separata från testfixturer och från ett tydligt syntetiskt maxprov; inga riktiga API-anrop eller verkliga kunduppgifter används.

Evidens finns i `~/.local/share/riskanalys/provkorningar/h6-20261014-203520/`: startläge, provskript, `jamforelse.json`, `provresultat.json`, `maxresultat.json`, tester och Word-kompatibel rendering. Mellankörningar sparas också, inklusive misslyckade försök; de används inte som slutlig evidens. Slutlig fullsvit: **1 621 passed, 1 deselected in 738.86s**, exitkod 0 (`final-full.log`). Tre extra kontraktprov tillkom efter insamlingen till fullsviten och ingår i `edge-contracts.log`: 13 passed. Regelbasvalidering, compileall och diffkontroll passerar. Riktade slutprov: 51 godkända; separat layoutprov: 10 godkända. Efter fullsviten passerade samtliga 23 tabell-/renderingsprov på slutligt innehåll (`final-postsuite.log`). Efter fullsvitens start gjordes endast layoutjustering av titelram/kolumnbredd samt borttagning av en tom slutrad i kod; layoutproven kördes på de justeringarna.

### Avgränsning och beslut

- Bygg dokumentförbättringarna före metodkalibreringen. Riskregler, vikter, trösklar, kontrollreduktion och sakkunnigstatus lämnas oförändrade.
- PT, TF och sanktionsrisk redovisas åtskilda. Ingen sammanvägd byrånivå. En sanktionsrisknivå är inte en sanktionslistkontroll.
- Alla metodosäkerheter synliggörs kort och samlat. Visa inte nya nivåer för ett scenario som motorn endast bedömer per tjänst.
- Råa intervjusvar och fullständig teknisk proveniens flyttas till bilagan. Nödvändiga verksamhetsfakta och analytiska resonemang ska fortfarande finnas i huvudrapporten.
- Bevara underlagets integritet, namn-/smågruppsskydd och lokala personuppgifter. Inga nya API-anrop eller nya AI-data behövs för denna leverans.
- Historiska filer och exporter skrivs inte om. Läsning och verifiering av äldre format ska fungera med tidigare kontrollsummor.
- Sidmål: prova 8–12 sidor huvudrapport och 3 500–5 000 ord inklusive tabeller för fyrtjänstexemplet. Redaktionellt mål, inte lagkrav eller automatisk fastställelsespärr. Ingen tyst trunkering för att nå målet.

### Revidering efter granskning – ordbudget och ansvar

Vid planrevideringen före implementation kunde längdmålet inte garanteras: de dåvarande fem intervallen tillät 2 250 ord per tjänst och 9 000 ord för fyra tjänster. Ett kort fixturprov räcker inte som längdverifiering. Följande redaktionella gränser infördes sedan i H6; mätutfallet och kvarstående längdgap redovisas i genomförandet ovan.

| AI-del (befintligt ID behålls) | Nytt intervall i ord |
|---|---:|
| hot | 80–160 |
| sarbarheter | 100–220 |
| kontroller | 60–120 |
| risknivaer | 80–120 |
| slutsatser | 80–130 |
| Summa per tjänst | 400–750 |

Fyra tjänster får därmed högst 3 000 AI-ord. Huvudrapportens övriga planeringsbudget är 2 000 ord: överblick/verksamhet 400, metod/gemensamma förhållanden 400, lokal tjänstetext inklusive beräkningstabeller 500, gemensamma kontroll-/risköversikter 350 och åtgärder/uppföljning/källhänvisningar 350. Allt synligt innehåll inklusive rubriker och tabellceller räknas; B1 räknas separat. Budgeten är ett provmål för fyra tjänster, inte en universell maxlängd för elva tjänster. Vid överskridande visas en redaktionell varning och faktisk mätning; inga fakta tas bort automatiskt.

Fem anrop och befintliga ID:n/schema behålls. `risknivaer` blir en kort kvalitativ syntes under rubriken **Scenarier och osäkerheter**: endast samband som stöds av underlaget eller uttryckligt villkorliga scenarier, inga påståenden om varför en viss nivå är riktig eller avviker från sektorn. `motivering` kan fortsatt användas som stycketyp för det kvalitativa resonemanget; det betyder inte nivåmotivering. Upprepa inte hotdelens scenariobeskrivningar. Den lokala tabellen ensam beskriver basnivå, faktorer, tak, konsekvens, kontrollreduktion och utfall. Att byta denna textinstruktion kräver uppdaterad promptidentitet och validering, men inte nya AI-data eller ändrat antal anrop.

### Uppgift 0 – avgränsa befintligt arbete före implementation

- [x] Inventera staged, unstaged och nya filer utan att återställa eller flytta någon annans arbete. Spara en återställbar lokal startbild inklusive nya filer utanför Git; inga hemligheter i repot.
- [x] Granska Bolagsverket-/bokslutsintaget och dess överlappande dokumentfiler innan H6-kod skrivs. Redovisa fynd och berörda tester separat från H6.
- [x] Kör den fulla testsuiten på startläget och spara utfallet. Befintliga fel ska identifieras innan H6:s regression bedöms.
- [x] Föreslå logiska commitgrupper efter genomgången. Se slutgranskningen 2026-10-15 nedan. Commit kräver uttrycklig användarbeställning; den inklistrade granskarens fråga är inte ett sådant godkännande. En verifierad lokal startbild kan användas som bas om commit inte beställs.

### Disposition och tabellkontrakt

| Del i huvudrapporten | Form och obligatoriskt innehåll |
|---|---|
| Överblick | Status, period, ansvar, avgränsning, centrala risker och öppna beslut. Ingen ny AI-genererad sammanfattning krävs; okända slutsatser markeras. |
| Verksamhet och tjänster | Tabell: tjänst, kundantal, omsättning med period, uppdrag/befogenheter. Okänd uppgift visas som okänd. Överlappande kundantal summeras inte till unika kunder. |
| Metod | Kort beskrivning av befintlig matris, skalor och begränsningar; tabell från aktuell regelbas. Färg kompletterar textetiketter. |
| Gemensamma förhållanden | Kundgrupper, geografi, kanaler, organisation och erfarenheter beskrivs en gång. Ingen slutsats om frånvaro av risk från noll rapporter. |
| Kontroller | En rad per kontroll-ID: namn, genomförande, effektstatus, period, belägg/begränsning och berörda tjänster. Samma kontroll återges inte i fulltext i varje tjänst. Saknad scenariotäckning anges uttryckligen; den uppfinns inte. |
| Tjänsteanalys | Scenario/exponering/kontrollbegränsning i tabell där befintligt strukturerat stöd finns, följt av sammanhängande motivering och praktisk följd. Befintlig AI-prosa behålls som prosa; ingen heuristisk meningsextraktion eller automatisk scenarioetikett. |
| Risköversikt | Tjänst, PT före/efter kontroll, TF och sanktionsrisk med tydliga rubriker. Saknat utfall är ”Ej bedömt”, aldrig ”Låg”. Länka till tjänstens beräkningsförklaring och analys. |
| Åtgärder och uppföljning | Tabell: brist/föreslagen åtgärd, prioritet om belagd, ansvarig, tidsfrist, uppföljning. Obeslutade fält markeras ”Ej beslutat”. Maskinfynd är inte hela byråns handlingsplan. |
| Källor och bilagehänvisning | Korta, upplösta källnummer vid relevanta påståenden. Sida/avsnitt endast när känt. Fullt register och lokala belägg i bilagan. |

En Word-fil med befintligt filnamn. `D-ARB.B1` ligger efter en sidbrytning och ingår i samma sakgranskning och manifest som huvudtexten. Intern länk leder till bilagan. Huvudtext och bilaga mäts separat. En framtida filuppdelning kräver ett visat användarbehov.

### Granskningsfokus

1. Ändrad cell, källa, visningsordning eller bilaga får inte behålla tidigare sakgodkännande (uppgift 1 och 4).
2. Tom/okänd uppgift, överlappande kunder och en liten högrisktjänst får inte försvinna i summeringen (uppgift 2).
3. Saknat namn i en cell och text med `[VERIFIERA]` måste upptäckas lika säkert som i ett stycke (uppgift 1).
4. En regelreferens eller sektorskälla får inte framställas som stöd för en obestyrkt poäng eller kontrolltäckning (uppgift 3).
5. Långa celler, många tjänster och en läsare utan uppdaterade Word-fält ska fortfarande få en begriplig rapport (uppgift 4 och 5).

### Uppgift 1 – typade tabeller och historisk kompatibilitet

**Ändra:** `src/riskanalys/dokument/modeller.py`, `rendering.py`, `faststallelse/sakgranskning.py`, `faststallelse/grindar.py`.
**Tester:** `tester/enhet/test_dokumentmodeller.py`, `test_rendering.py`, `test_sakgranskning.py`; nya `tester/enhet/test_dokumenttabeller.py`.

**Gränssnitt:** lokala modeller `Tabellcell(text: str, referenser: tuple[str, ...] = ())`, `Tabellrad(celler: tuple[Tabellcell, ...])`, `Dokumenttabell(id: str, rubrik: str, kolumner: tuple[str, ...], rader: tuple[Tabellrad, ...], fore_stycke: int)`. Lägg till `Avsnitt.tabeller: tuple[Dokumenttabell, ...] = ()` och `Avsnitt.visningsnummer: str | None = None`. Ny formatetikett `D-ARB-tjanst-v5`. Position får vara 0–antal stycken, inklusive avsnitt utan prosa; vid samma position renderas tabeller i deklarerad ordning. Kräv unika tabell-ID:n och lika många celler som kolumner.

- [x] Skriv RED-prov för felaktig radbredd/position, tomma kolumnrubriker, dubbla tabell-ID:n och deterministisk ordning.
- [x] Skriv RED-prov för ändrad celltext/referens/ordning/visningsnummer som ändrar granskningssumman; äldre serialisering och summor är identiska före/efter tillägget.
- [x] Implementera modeller och versionsvillkor: nya standardfält utelämnas i äldre formats serialisering. AI:s `Textstycke`/`AISvar` ändras inte.
- [x] Utöka `renderat_avsnitt` och `har_verifiera` till alla synliga rubriker och celler; samma lokala namnsubstitution och hinder som för prosa.
- [x] Kör `.venv/bin/pytest -q tester/enhet/test_dokumenttabeller.py tester/enhet/test_dokumentmodeller.py tester/enhet/test_rendering.py tester/enhet/test_sakgranskning.py`. Samtliga ska passera efter RED/GREEN.

### Uppgift 2 – kortare sammansättning med oförändrade utfall

**Ändra:** `dokument/arb.py`, `tjanstavsnitt.py`, `analysunderlag.py`, `intagsunderlag.py`, `granskning/analys.py` under `src/riskanalys/`.
**Skapa:** `src/riskanalys/dokument/tabeller.py`.
**Tester:** nya `tester/regelkontrakt/test_arb_tabeller.py`; befintliga `test_arb_erfarenhet_motivering.py`, `test_dokumentomfattning.py`.

**Gränssnitt:** `bygg_riskoversikt(bedomning: Bedomning, regelbas: Regelbas) -> Dokumenttabell` och `bygg_kontrolloversikt(bedomning: Bedomning, regelbas: Regelbas, profil: Profil) -> Dokumenttabell` i `tabeller.py`. Använd modellerna från uppgift 1. Kontroller identifieras med ID, aldrig genom likhetsmatchning av text. Visningsnummer följer dokumentordningen; stabila ID:n behålls.

- [x] Komplettera kontraktprov med fyra syntetiska tjänster: varje nivåcell motsvarar exakt sparad `Tjanstbedomning`; en liten högrisktjänst syns; kundantal med överlapp summeras inte.
- [x] Komplettera kontraktprov för en gemensam kontroll: en full beskrivning, korta tjänstehänvisningar; olika effektbelägg får inte slås ihop till ett bättre gemensamt omdöme.
- [x] Komplettera kontraktprov för noll rapporter, okänd exponering, inga erbjudna tjänster och saknad effekt. Bevara öppna fynd och kompletteringar.
- [x] Samla gemensam geografi och metodtext en gång; behåll tjänstens relevanta skillnader och motivering. Flytta råa svar till B1. Inga fraser tas bort enbart för att de liknar varandra.
- [x] Anpassa analytisk kravkontroll till typat innehåll utan att godta enbart rådata i en cell som analys. Flyttade underlag uppfyller inte automatiskt B-09/B-10/B-15.
- [x] Kör `.venv/bin/pytest -q tester/regelkontrakt/test_arb_tabeller.py tester/regelkontrakt/test_arb_erfarenhet_motivering.py tester/regelkontrakt/test_dokumentomfattning.py`. Kontrollera att motor och regelbas saknar ändringar.

### Uppgift 2b – längdkontrakt och tydlig uppgift för AI

**Ändra:** `src/riskanalys/dokument/delvalidering.py`, `promptar/delar.py`, `delskrivning.py`, `matning.py` och `tjanstavsnitt.py`; relevanta fixturer. **Tester:** `tester/enhet/test_delvalidering.py`, `test_promptar.py` samt nya `tester/enhet/test_ordbudget.py`.

- [x] Skriv RED-prov för varje nytt min/max, max+1 och min−1; promptens intervall ska alltid komma från samma `LANGD` som valideringen.
- [x] Skriv kontraktprov för den nya instruktionen: kvalitativ syntes, inga påståenden om motorns utfall eller avvikelse från sektorsnivån. Behåll förbudet mot AI-genererade nivåer. Maskinkontroller kompletteras med läsprov, de bevisar inte semantisk riktighet.
- [x] Implementera intervallen ovan, ändra riskdelens uppgift/rubrik och uppdatera prompt-/valideringsidentitet så gamla skrivförsök inte återanvänds som nygodkända H6-delar. Äldre exporter ska fortsatt kunna verifieras.
- [x] Skriv RED-prov för total synlig ordmängd inklusive tabeller och lokal insättning av platshållare. Redovisa både AI-svarets ordantal och den slutliga huvudrapportens ordantal; expansion kan göra dem olika.
- [x] Kör `.venv/bin/pytest -q tester/enhet/test_delvalidering.py tester/enhet/test_promptar.py tester/enhet/test_ordbudget.py`. Kör även befintliga skrivkedjeprov efter ändrad promptidentitet.

### Uppgift 3 – lokala beräkningsförklaringar och läsbara källor

**Ändra:** `src/riskanalys/dokument/nivatext.py`, `tjanstavsnitt.py`.
**Skapa:** `src/riskanalys/dokument/kallhanvisningar.py`.
**Tester:** nya `tester/enhet/test_utfallsforklaring.py`, `test_kallhanvisningar.py`.

**Gränssnitt:** `utfallsforklaring(t: Tjanstbedomning, regelbas: Regelbas) -> Dokumenttabell` i `nivatext.py`; `bygg_kallregister(dokument: Dokument, regelbas: Regelbas) -> dict[str, str]` i `kallhanvisningar.py`, där nyckeln är käll-ID och värdet är stabilt läsnummer för dokumentets faktiskt refererade källor. Upplös katalog-/regelreferenser via befintliga källfält; håll profilbelägg som separata bilagereferenser. Ordna käll-ID:n deterministiskt.

- [x] Skriv RED-prov som återger basnivå, tillämpade faktorer, tak, konsekvens och faktisk kontrollreduktion från det sparade resultatet och dess låsta regelbas. Ingen ny bedömning görs.
- [x] Skriv RED-prov för saknat/okänt regelspår: synlig begränsning i utkastet och granskningsfynd; ingen gissad förklaring.
- [x] Implementera formuleringar som skiljer ”motorn räknar så här” från ”kontrollen täcker detta hot”. Den senare slutsatsen kräver belägg som dagens motor inte alltid har.
- [x] Skriv RED-prov för korrekta källnummer, okänd sida utan påhittat sidnummer, ändrad hänvisning som ändrar summa och orefererad källa som inte fyller huvudrapporten.
- [x] Implementera hänvisningar i samma lokala modell som sakgranskas, inklusive celler. Fulla källmetadata bevaras i bilagan.
- [x] Kör `.venv/bin/pytest -q tester/enhet/test_utfallsforklaring.py tester/enhet/test_kallhanvisningar.py`. Samtliga ska passera.

### Uppgift 4 – en Word-fil med tydligt avskild bilaga

**Ändra:** `src/riskanalys/dokument/rendering.py`, `export.py`, `faststallelse/faststall.py`, `faststallelse/sakgranskning.py`; berörda manifestkontroller.
**Tester:** `tester/enhet/test_rendering.py`, `test_exportera_kommando.py`, `test_sakgranskning.py`; nya `tester/enhet/test_dokumentpaket.py`.

**Gränssnitt:** behåll `rendera_docx(dokument, profil, statusrad, sokvag, bilaga=()) -> Path`. V5 renderar tabeller och sidbrytning före B1; äldre format behåller sitt beteende. Inget nytt tvåfils-API. B1 förblir en del av hela dokumentets sakgranskning.

- [x] Skriv RED-prov: huvudtext utan rå B1-text, bilaga efter sidbrytning med allt underlag, ändrad/borttagen bilaga underkänns vid verifiering av samma fil.
- [x] Skriv RED-prov: tidigare sakgodkännande gäller inte efter ändrad struktur, cell eller bilaga; historiskt paket verifieras fortfarande.
- [x] Rendera riktiga Word-tabeller med upprepad rubrikrad, textetiketter, sidnummer och löpande rubriknumrering. Ingen manuell radbrytning som imiterar tabell.
- [x] Lägg in Word-innehållsförteckningsfält med uppdateringsflagga och en alltid läsbar rubriköversikt med interna länkar. Påstå inte att python-docx har beräknat sidnumren; fältens sidnummer verifieras i Word-kompatibel rendering.
- [x] Kontrollera att export och fastställelse använder samma fullständiga v5-dokument och befintligt enfilspaket. Behåll alla grindar; inga ändringar i publiceringsprotokollet behövs.
- [x] Kör `.venv/bin/pytest -q tester/enhet/test_dokumentpaket.py tester/enhet/test_rendering.py tester/enhet/test_exportera_kommando.py tester/enhet/test_sakgranskning.py`.

### Uppgift 5 – komplett jämförelse och läsprov

**Ändra:** `tester/intag/test_kedja.py`, `tester/m2/test_m2_kedja.py`, befintlig spec och STATUS. Syntetiska provfiler ligger utanför Git; ingen rå profil kopieras in.

- [x] Skriv kedjeprov för v5: skrivning → granskning → enfilsutkast → syntetisk sakgranskning/attest → fastställelse → verifiering. Öppna riktiga hinder ska fortfarande blockera fastställelse.
- [x] Kör fyrtjänstfallet med samma sparade motorresultat och nya, korta syntetiska skrivsvar enligt H6-kontraktet. Gamla testsvar behålls som historisk jämförelse och trunkeras inte. Kör dessutom ett separat gränsprov där alla delar ligger på sina nya maxlängder. Jämför nivåer exakt; detta utvärderar fortfarande inte riktig AI-kvalitet.
- [x] Mät huvudtext och bilaga separat, antal tabeller, upprepade kontrollbeskrivningar, källtäckning och kvarstående fynd. Kräv minst tjänste-, kontroll-, risk- och åtgärdstabell. Inget gammalt högt fynd får försvinna utan saklig grund.
- [x] Inspektera Word visuellt: breda tabeller, långa texter, rubriker, innehållsförteckning, länkar och sidhuvud. Om tillgänglig rendering inte kan beräkna sidantal, redovisa det som ej verifierat; rapportera ändå struktur- och ordmätning.
- [x] Kör `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest -q`, `.venv/bin/riskanalys regelbas validera` och `git diff --check`. Redovisa utfallet, ingen automatisk commit.
- [x] Visa huvudrapport och bilaga för användaren, med före/efter-mätning. Dokumentera kvarstående metodproblem separat.

### Separat beslutsspår – riskmetod (ingen kalibrering i H6)

| Beslut | Underlag som behöver tas fram | Leverans före ändring av regler |
|---|---|---|
| M1 Kontrollernas räckvidd | Vilka hot/scenarier täcker varje kontroll, vad täcks inte och vilket effektbelägg finns? | Källbunden täckningsmatris, regler för okänd effekt och sakkunnigbedömda kontrastfall. Ett annat godtyckligt antal kontroller ersätter inte dagens `any`-regel. |
| M2 TF som egen dimension | Relevanta TF-scenarier, faktorer och konsekvensdefinition; vilka faktorer överlappar faktiskt PT? | Motiverad separat metod och facit. Inget krav att TF ska ligga under PT och ingen automatisk översättning av nationell sektorsnivå. |
| M3 Enstaka exponering kontra omfattning | Tjänst, befogenhet, kundandel, belopp, faktisk geografi och koncentration; även väsentliga enstaka kunder. | Kontrastfall för en kund/hög exponering respektive många/låg exponering. Varken all utlandskoppling eller en generell procentgräns blir facit utan prövning. |
| M4 Summering, tak och dubbelräkning | Beroende mellan faktorer, gemensam kontra tjänstespecifik exponering, skalans förmåga att skilja fall åt. | Känslighetsprov och sakkunnigbedömda fall med få/många oberoende faktorer respektive flera uttryck för samma faktor. Fler faktorer måste inte alltid ge högre nivå. |

Byrån bekräftar verksamhetsfakta och beslutar sina åtgärder. Metodförslagen dokumenteras med källor och explicita metodval; sakkunnigprövning och användarens godkännande föregår operativ ändring. Saknas sakkunnigfacit förblir förslagen oprövade. Status: **M1–M4 öppna**. Tekniskt underlag och kontrastfall tas fram av implementerande agent; användaren utser en namngiven sakkunnig och beslutsansvarig. Ingen sådan person eller kalenderfrist är ännu utsedd. Beslutskontroll sker före första fastställelse/operativa användning av en reviderad riskmetod; dokumentbyggandet väntar inte på detta. Tills dess ska metodstatus och de oförändrade motorutfallen framgå av rapportens överblick. Åtgärdstabellens ansvar/tidsfrister förblir ”Ej beslutat” där intaget saknar stöd; H6 bygger inget nytt åtgärdsintag. Ingen ny skyldighet eller riskvikt införs genom denna plan.

### Självgranskning och överlämning

Planen täcker struktur, tabeller, källor, lokala förklaringar, bilaga, historik och hela exportkedjan. De fem granskningsriskerna har utpekade tester. AI-schema, riskmetod och registerintegrationer är utanför leveransen. Presentationen ska tydliggöra dagens metodbrister utan att legitimera dem. Återstående produktval är läsbarhetsbedömningen av det färdiga provet; inga obestämda metodval måste lösas för att bygga tabellerna. Genomförandet använde subagenter enligt användarens senare uttryckliga instruktion; huvudagenten ansvarar för integration och verifiering.

### Strukturresearch efter genomförandet, 2026-10-14

Användaren begärde fördjupad onlineresearch av dispositionen. [Research 11 §9](../../research/11-kallkontroll-allman-riskbedomning.md#9-fördjupad-strukturresearch-efter-h6--2026-10-14) redovisar 24 primärkällor, ny dokumentmätning och ett förslag med sex huvuddelar, risköversikt först samt full beräkningslogg i B1. Huvudrapporten behöver saklig analys per tjänst, utöver förklaring av motorns beräkning. Detta är rekommendationer inför en nästa revision, inte ändrade H6-acceptanskrav i efterhand eller en påbörjad implementation. En fil och bevarad sakgranskning/proveniens rekommenderas fortsatt. M1–M4 är öppna; inga nivåer eller regler ändras genom researchen.

### Oberoende teknisk slutgranskning och rättning, 2026-10-15

Två nya subagenter granskade H6 med avgränsat uppdrag utan tidigare konversationshistorik. H6 isolerades mot den privata startkopian, inte genom att kalla hela HEAD-diffen för H6. Vid start matchade alla H6-kod-/testfiler de sparade sluthasharna. Arbetskatalogen hade 66 ändrade spårade filer (+3 215/−560) och 34 nya filer; även befintliga indexändringar bevarades.

Dokumentgranskningen fann två P2-presentationsregressioner:

1. Kontrolltabellen visade kategorin ”verksam” även när effektens källbelägg saknades och motorn nekade kontrollverkan. Rättningen visar motorns befintliga riskreducerande-flagga samt saknade aktuella belägg för utformning, genomförande, effektbedömning och utfall. Det är ingen ny prövning av scenariotäckning.
2. Risköversikten återgav preliminära nivåer utan att markera okänt tjänsteerbjudande/preliminär status. Rättningen markerar detta i tjänstecellen; nivåcellerna behåller motorutfallen.

Åtta nya regressioner föll före kodändring av avsedd orsak (8 failed, 13 deselected, 2,82 s). Prov använder schema-giltiga saknade/inaktuella uppgifter. Efter rättning passerade 50 riktade tester på 6,03 s. Granskarens återgranskning fann inga kvarstående åtgärdskrävande fynd i rättningen; 29 relevanta prov samt två syntetiska prov för källrendering/verifieramarkering passerade.

Skrivgranskningen fann inga konkreta H6-regressioner inom sitt scope: 253 riktade prov passerade på 32,60 s. Ett separat syntetiskt prov med 60 Testleverantör-anrop, inklusive omförsök, gav identiska begäranden vid byte av namn, nivåer och regelspår. Gamla format/promptidentiteter och överlånga manipulerade svar stoppades; namnspärr behöll blockerande fynd. Detta är teknisk granskning, inte sakkunnigattest eller verkligt modellprov.

Slutlig fullsvit efter rättningen: **1 632 passerade, ett bortvalt livetest, 729,24 s**, exitkod 0. Ingen kod, test- eller regelbasfil ändrades eller tillkom efter körningens start enligt hashjämförelsen. Regelbasvalidering, compileall och diffkontroll passerar. Evidens och start-/sluthashar sparas i `~/.local/share/riskanalys/provkorningar/h6-granskning-20261015/`. Historiska Word-exporter lämnas orörda; mätningarna från 2026-10-14 gäller det sparade provet före denna textjustering. Ingen ny rapportdisposition har byggts.

Preliminära commitgrupper i beroendeordning: (1) skyddad AI-begäran/namn och tillåtelselista, (2) lokal precision och namnfältsrättningar, (3) Bolagsverket/bokslut och samlat intag, (4) H6 inklusive slutgranskningens rättningar, (5) strukturresearch. Gemensamma filer behöver delas på innehållsnivå mot startkopior; en vanlig helfilsstaging skulle blanda arbetena. H6:s separata kod-/testdiff ligger i evidensmappen och passerar `git apply --check` mot en kopia av motsvarande startfiler. Detta är ett förslag, inte redan isolerade eller verifierade commitobjekt. Indexet ändras inte i denna granskning; inga commits eller pushar.

### Valt fortsättningsspår A + B, 2026-10-15

Användaren valde uttryckligen **källbundna beskrivningar av kontrollernas räckvidd plus obligatorisk lokal granskning av byråns faktiska tillämpning**. Det är en inriktning för nästa revision efter H6-granskningen; ännu ingen operativ regel-/metodändring.

- **A, generell beskrivning:** knyt kontroll-ID till relevanta scenarier/tjänster, vad kontrollen kan belägga, begränsningar och precisa källor. Påstå inte att byrån faktiskt genomför kontrollen. Beskrivningen är separat från motorns beslut om riskreduktion. Om den läggs i regelbasen krävs källbunden modell, versionshantering och bevarad historisk serialisering; ny metadata får inte smygändra tidigare summor eller sakkunnigstatus.
- **B, lokal analys:** granskaren dokumenterar per tjänst faktisk exponering, vilka scenarier som gäller, kontrollernas tillämpning/effektbelägg, PT-/TF-resonemang och kvarstående gap. Svar och godkännande binds till exakt underlag, dokument och relevanta käll-/metodversioner. Saknade svar eller olösta väsentliga motsägelser ska hindra fastställelse. Ett ifyllt textfält bevisar inte analysens riktighet.
- **Arbetsdelning:** programmet sammanställer godkänt strukturerat underlag och redovisar oförändrade motorutfall; AI behåller dagens dataskyddsgräns. Byrån bekräftar fakta och beslutar åtgärder. Sakkunnig metodprövning avgör när kontrolltäckningen får påverka motorn. M1–M4 stängs inte genom beskrivningstext eller lokal attest ensam.
- **Redaktionell fortsättning:** risköversikten först, beräkning och fulla metadata i B1 samt kortare precisa hänvisningar enligt research §9. Status om ogranskad metod och öppna frågor ska finnas i första översikten. Sidmålet verifieras med nytt dokumentprov; 9–12 sidor är ingen garanti.

Före implementation behöver detta konkretiseras i samma plan/spec med datamodell, lokala granskningsfrågor, versions-/ogiltigförklaranderegler och acceptansprov. Mänsklig medarbetarläsning och namngiven sakkunnig kvarstår; syntetiska tekniska prov kan inte ersätta dem.

### Godkänd trecommitsuppdelning genomförd, 2026-10-15

Användarens uttryckliga beställning ersätter förslaget om fem commits ovan. Genomförandet använder tre commits: `8e7e83fb` samlar allt före H6 inklusive integrationskontraktet, `a08f6c5a` lägger på H6 inklusive granskningens rättningar, och en dokumentationscommit samlar återstående Markdown. Inga nya programbeteenden införs genom uppdelningen. Alla staged/unstaged arbetsfiler samt ursprungligt index säkerhetskopierades först; `research_notes/` ingår i backupen men lämnas utanför Git.

En separat lokal klon användes eftersom appverktyget var kopplat till en annan Git-rot. Fullsviterna verifierade mellanläget (**1557 passerade, 1 bortvalt livetest, 747.48 s**) och H6 (**1632 passerade, 1 bortvalt livetest, 754.91 s**). Båda slutkörningarna använde egna Python-/CLI-miljöer som importerar respektive kopias kod även när testernas subprocesser tar bort `PYTHONPATH`. Den första blandade mellanlägeskörningen föll i tio CLI-kedjevarianter; den sparas som diagnostik och ersätts av den gröna isolerade körningen. Ingen produktions-/testkod ändrades för miljörättningen.

Kända pilotidentifierare och nyckelvärden samt vanliga token-/privatnyckelformat kontrollerades före commits utan träff. Symlänken till det kanoniska tillsynsfacitet och historiska filer bevaras. För H6 verifierades dessutom att återpålagd kod/test/regler matchar den ursprungliga arbetskatalogens innehåll exakt. Den sista commiten ändrar endast Markdown; inga nya testberoenden tillkommer där. Ingen push eller ändring i privata profiler/exporter.

Backup, fulla testloggar, körningshashar och commitmanifest ligger i `~/.local/share/riskanalys/provkorningar/commituppdelning-20261015-155926`. Det tidigare indexet är återställbart därifrån; det ersätts i ordinarie checkout först när commitkedjan är verifierad. A + B och den nya dispositionen kvarstår som nästa separata implementation enligt avsnittet ovan.

## A + B – konkret kontrakt inför nästa revision, 2026-10-15

**Status: genomförande pågår.** Steg 1 (AB1 + AB4a) är implementerat och granskat: färsk fullsvit 1 677 passerade, ett bortvalt livetest, 730,04 s. Steg 2:s programstöd är byggt och uppgiftsgranskas; samlad slutgranskning och fullsvit återstår. Detta avsnitt preciserar användarens val A + B. Det ersätter inte H6:s historik eller M1–M4. Baslinje: `3c6d405` på `codex/m0-m1`; enbart `research_notes/` ligger utanför Git. Den inklistrade granskarens fråga om push är inte en pushbeställning.

**Mål:** en kortare läsordning och en spårbar, lokalt skriven analys för varje erbjuden tjänst, med källbeskrivna kontrollbegränsningar och uttrycklig mänsklig granskning. Nivåerna ska vara samma motorutfall som före revisionen.

**Arkitektur:** beskrivande räckvidd under befintliga kontrollposter; separat privat analysregister; två godkännanden utan cirkelberoende: först analysen mot underlaget, sedan det renderade dokumentet mot den godkända analysen. Dokumentformat `D-ARB-tjanst-v6` avser sammansättningen. Historiska v5-skrivresultat behålls. Steg 1 använder dem oförändrade; steg 2 inför ett separat v6-skrivresultat med endast `hot` och `sarbarheter`. V6 gör alltid dessa två anrop, även utan lokal analys, så att privat analysstatus inte påverkar anropsmönstret. Efter steg 2 byggs nya dokument i v6 även när analys saknas, då som ofullständiga utkast. V5 och steg 1:s v5.1 får därefter inte bli vägar runt den nya grinden.

**Teknik/spec:** befintlig Python, Pydantic, YAML, python-docx och pytest; inga nya beroenden. Designspec §8.4.10, §10 samt avsnittet A + B nedan, och research 11 §9. Inga riktiga AI-/registeranrop behövs för implementationen. Planläggningen ändrade bara dokumentation. Den beställda implementationen beskrivs i genomförandeloggen nedan; commit och remoteändringar ingår inte.

### Avgränsning efter Claudes granskning, 2026-10-15

Denna revision inför sex omfattningsbeslut före implementation. Inga ytterligare sakkrav läggs till. De fem tidigare källkraven och sex kompletteringarna nedan behålls men ska kunna uppfyllas genom förifyllnad, återanvändning och relevansstyrda fördjupningar.

1. **Förifyll och återanvänd:** programmet bygger redigerbara, ogranskade utkast ur bekräftad profil, motorutfall och källkatalog. Det länkar befintliga belägg i stället för att begära dem igen. Lokal tillämpning, effekt och beslut får inte hittas på. En scenarioanalys kan delas av flera tjänster; varje tjänst anger uttryckligen **samma/avviker**. Checklistans obligatoriska och villkorade block samt fyrtjänstfallets antal anges nedan.
2. **Två AI-delar i v6:** endast hot och sårbarheter genereras. Kontroll-, nivå- och slutsatsdelarna skrivs lokalt; de tre överflödiga AI-anropen tas bort. Ingen privat fritext skickas till AI. Historisk v5-verifiering behåller femdelarskontraktet.
3. **Två leveranssteg:** först AB1 + AB4a (risköversikt först och beräkningar i B1), med egen granskning och full grön svit före eventuell commit. Därefter AB7 → AB2 → AB3 → AB4b → AB5 → AB6. Steg 1 får inte bero på det nya analysregistret eller AB7. Commit och push kräver separat faktisk beställning; inklistrad granskartext utför dem inte.
4. **Synlig egen granskning:** spara författaridentitet för den granskade svarsrevisionen och godkännaridentitet. Om samma person skriver och godkänner ska en härledd loggpost och märkningen ”Samma person har skrivit och godkänt den lokala analysen” synas i översikten. Det är transparens, ingen ny automatisk spärr eller påstått oberoende.
5. **M1 i metodgranskningen:** sakkunnig avgör kontrollernas scenariotäckning och reduktionsprincip vid samma granskning som verifierar metoden. Attest utan uttryckligt beslut om M1 räcker inte. Krävs ändrad numerisk regel blir det en separat källbunden metodändring med typfall; A+B inför den inte tyst.
6. **Rätt ansvar för modellvalidering:** modellidentiteten binder motor, dess beräkningsberoenden och regelbas. Runtime/bibliotek dokumenteras som miljöuppgift och bryter inte i sig modellbindningen. Projektet levererar versionsbunden valideringsrapport; byrån granskar relevans/begränsningar, godkänner användningen och följer upp verkliga fel. AB7 preciserar detta.

### Inarbetad källgranskning – fem bindande plankrav, 2026-10-15

Användaren har beställt att följande kompletteringar ska ingå i A + B. De är nu del av genomförandets acceptanskontrakt, inte en separat förslagslista. "Bindande plankrav" avser projektets beslutade leverans; alla föreslagna fält och tabeller är inte föreskrivna i lag. Detaljerna införs i modellerna, frågorna och AB2–AB6 nedan.

| Komplettering | Det som ska levereras | Ansvarig uppgift och verifiering |
|---|---|---|
| 1. Sårbarheter per tjänst | Explicit lokal prövning av kundtyper, distributionskanaler, geografi och egna verksamhetsförhållanden, kopplad till scenarier och belägg. Ett falskt katalogvillkor utesluter inte andra relevanta sårbarheter. | AB2/AB3, `test_sarbarhetsprovning_kraver_fyra_omraden_och_belagg`; AB4, `test_v6_visar_sarbarheternas_betydelse_per_tjanst`. |
| 2. Samverkan och nivåmotivering | Förklara hur faktorer förstärker eller begränsar varandra i tjänstens scenarier och varför PT-/TF-utfallet är rimligt eller ifrågasätts. Ingen ny numerisk sammanvägning införs. | AB2/AB3, `test_samverkan_och_separata_nivamotiveringar_kravs`; AB4 visar resonemanget vid respektive nivå. |
| 3. Risk till konkret rutin | En spårbar åtgärdsrad: scenario/risk, vad som ska göras, rutin-ID/version eller synlig uppgift att rutin saknas, ansvar, utlösare/frekvens, uppföljning och faktisk status. | AB2/AB3, `test_rutinatgard_skiljer_forslag_beslut_och_genomforande`; AB4, `test_v6_lankar_risk_till_rutin_utan_falsk_genomforandestatus`. |
| 4. Lärdomar och båda datumen | Egen rapportering, avböjanden och aktuell myndighetsinformation prövas uttryckligen per tjänst. Visa senaste utvärdering och eventuell separat uppdatering samt nästa genomgång. | AB2, `test_egna_lardomar_kraver_provning`; AB4, datumproven nedan. |
| 5. Verkan bakom redovisad reduktion | Den lokala granskningen måste ta ställning till den faktiskt beräknade reduktionen och dess stöd i scenariotäckning/effekt. Olöst reduktionskonflikt blockerar godkännande; motorutfallet skrivs inte om. | AB2/AB5, `test_bankavstamning_utan_scenariotackning_ger_metodkonflikt`; AB6 bevisar samma nivåer och stoppad fastställelse. |

**Källstöd:** användarens myndighetsvägledning, version mars 2025, s. 8–13 och 16–27 (`SRC-VAGL-2025-03`); [14FS 2024:11](https://www.lansstyrelsen.se/download/18.74c322ef18f9ee08a2929/1716358223326/2024-11%20Penningtv%C3%A4tt%20Dalarnas%20l%C3%A4n%20G%C3%A4vleborgs%20l%C3%A4n%20Hallands%20l%C3%A4n%20V%C3%A4rmlands%20l%C3%A4n%20V%C3%A4stra%20G%C3%B6talands%20l%C3%A4n%20%C3%96rebro%20l%C3%A4n.pdf), 2 kap. 2–3 §§; samt [Länsstyrelsens vägledning](https://www.lansstyrelsen.se/vastra-gotaland/samhalle/betalning-ekonomi-och-pengar/forhindra-penningtvatt-och-finansiering-av-terrorism/gor-en-allman-riskbedomning.html), avsnitten om sårbarheter, nivåmotivering, åtgärdseffekt och uppdatering. E-boken anger utgåva januari 2022; dess s. 24–29 är bakgrundsexempel, medan landlistor, äldre paragrafnumrering och riskmatris inte är aktuella beslutsregler. VG:s Pages-dokument är en webböversikt som skiljer allmän riskbedömning från kundbedömningar och rutiner. Källornas redovisningsordning är inte låst; vår disposition och ordbudget är designval.

Den tidigare hänvisningen till research 11 §10 saknar motsvarande avsnitt i den aktuella arbetskopian. Denna plan hänvisar därför direkt till ovanstående källor och det sparade datumprovet `~/.local/share/riskanalys/provkorningar/kallkontroll-20261015-bilagor/datumprov.json`, inte till ett saknat researchavsnitt. Befintlig research §9 bevaras.

**Avgränsning:** allmän riskbedömning ska vara grund för kundriskbedömning, kundkännedom, övervakning/rapportering, bevarande, intern kontroll och utbildning. De separata rutinerna och genomförandebeläggen behöver finnas och granskas i sina egna arbetsflöden. A + B eller en godkänd dokumenthash är inte bevis på att alla dessa skyldigheter faktiskt fullgjorts.

### Inarbetad fortsättningsgranskning – sex kompletteringar, 2026-10-15

Detta är användarens beställda omskrivning efter den fortsatta källgranskningen. De fem kraven ovan består. Följande sex kompletteringar är också leveranskrav; de ska genomföras i modell, frågor, dokument och prov enligt samma plan. Prioritera 1–3 och 6. Punkt 4 fördjupar befintlig leverantörsprövning; punkt 5 är ett obligatoriskt syntetiskt prov med lokalt relevansval, ingen generell högriskklassning.

| Komplettering | Beslutad utformning | Ägare/prov |
|---|---|---|
| 1. Tjänsternas detaljnivå | Pröva om katalogtjänstens olika arbetsmoment behöver delanalyser. Motivera både uppdelning och utebliven uppdelning. Fakturabokföring och bokföring av gränsöverskridande flöden ska kunna analyseras olika inom samma tjänst. | AB2–AB4; `test_tjanstens_detaljniva_kraver_motivering_och_scenariokoppling`. |
| 2. Faktisk betalningsinsyn | Beskriv vilka flöden/underlag som är synliga, kända insynsluckor, möjligheten att identifiera verklig avsändare/mottagare och underlagens tillförlitlighet. Avgränsa efter uppdraget; påstå inte total insyn för att ett konto stämmer. | AB2–AB4; `test_bankavstamning_ar_inte_fullstandig_betalningsinsyn`. |
| 3. Uppdragets hanterbarhet | Pröva kompetens, insyn och förmåga att hantera riskerna. Åtgärder kan vara förstärkning, begränsning, avböjande eller avslut. Hög risk är inte automatisk vägran; otillräcklig kundkännedom prövas i tillämpligt kundflöde. | AB2/AB3/AB5; `test_hog_risk_ar_inte_automatiskt_avslag` och `test_ohanterbart_uppdrag_kraver_atgard_eller_avgransning`. |
| 4. Leverantörer och ansvar | Dokumentera leverantörens uppgift/kontroller, egen verifiering, kvarstående ansvar och hantering av saknade/motstridiga resultat. Återanvänd befintliga poster om extern KYC och utkontraktering. | AB2/AB3/AB5; `test_extern_kyc_kraver_lokal_ansvars_och_resultatprovning`. |
| 5. Digitala affärsmodeller | Prova plattformsintäkter och betalningsförmedlare med dolda bakomliggande parter/ändamål. Skilj detta från digital leverans av verifikationer och pröva relevansen för just byråns kundmix. | AB6; `test_plattformsintakter_via_psp_provas_utan_automatisk_hogrisk`. |
| 6. Löpande modellriskhantering | Versionsbunden modellidentitet, ansvarig, valideringsrapport, rutin och återkommande kontroll av verkliga felutfall. Åtgärder och omprövning ska dokumenteras; testsiffror och engångsattest räcker inte. | AB7 före AB5/AB6; `test_modellrisk_kraver_aktuell_rapport_och_feluppfoljning`. |

**Verifierat källstöd:** [tillsynsrapport 2026:14, s. 7–8](https://www.lansstyrelsen.se/download/18.51b8c30c19d05558bd82e18e/1774259142687/Erfarenheter%20fr%C3%A5n%20l%C3%A4nsstyrelsernas%20penningtv%C3%A4ttstillsyn.pdf) för detaljnivå/leverantörer; [Finanspolisen, företagsmiljö, februari 2026, s. 2](https://polisen.se/8fe83310adc2c5c237323d50c6012100/siteassets/dokument/finanspolisen/fipo-informerar/2026_fipo-informerar_storskalig-penningtvatt-i-foretagsmiljo.pdf) för parallella bankengagemang/fabricerat underlag; [FATF:s redovisningsvägledning 2019, punkt 21](https://www.fatf-gafi.org/content/dam/fatf-gafi/guidance/RBA-Accounting-Profession.pdf.coredownload.pdf) för kompetens/riskaptit; [Finanspolisen, digitala plattformar, augusti 2026, s. 1–3](https://polisen.se/3c258ab8120fc2de94f6a7f11f2f774c/siteassets/dokument/finanspolisen/fipo-informerar/2026_risk-for-penningtvatt-och-tf_digitala-plattformar.pdf) för plattformar/PSP och osäker omfattning; [PTL](https://www.riksdagen.se/sv/dokument-och-lagar/dokument/svensk-forfattningssamling/lag-2017630-om-atgarder-mot-penningtvatt-och_sfs-2017-630/), 3 kap. 1 § och 6 kap. 1 §, för kundkännedom respektive modellriskrutiner när modeller används. FATF och de föreslagna provfallen är metodstöd, inte egna svenska lagkrav. PDF-originalen från Finanspolisen finns privat i `~/.local/share/riskanalys/provkorningar/tillaggsgranskning-20261015/`.

**Vad som ändras i regelbasen:** kontrollernas källbundna räckviddsbeskrivningar och nödvändiga källmetadata enligt AB1. Nära kundrelationer, kundberoende, extern KYC/utkontraktering samt TF via insamlingar, hawala och krypto finns redan i katalogen och får inte dubbleras. De sex kompletteringarna tillför i huvudsak lokal prövning, dokumentation och prov. Saknade generella kataloghot/faktorer noteras som separata källbundna ändringsbehov; nya riskvikter, faktorregler, delnivåer och reduktionsregler kräver fortsatt särskild metodprövning och ingår inte automatiskt här.

### Gemensamma begränsningar och granskningsfokus

- Kontrollräckvidd beskriver vad en kontroll kan belägga och dess begränsningar. Den ändrar inte `Kontrollbedomning`, faktorer, sannolikhet, konsekvens eller reduktionsregler. Ingen ny manuell risknivå införs i analysmodellen.
- Lokala svar, namn, belägg och attester stannar under `$RISKANALYS_DATA`. De får inte påverka AI-begäran, återkoppling, antal anrop eller cacheidentitet genom den nya analysvägen. Befintlig tillåtelselista och smågruppsskydd gäller.
- Källbunden tolkning är fortfarande tolkning. Varje räckviddspost har `grund`, precisa hänvisningar och egen sakkunnigstatus; ingen teknisk körning sätter `verifierad`.
- Profilen är den kanoniska faktakällan. Analysen får inte ersätta ett profilvärde med ett konkurrerande tal eller bekräfta en registeruppgift. Fel fakta rättas i intaget och bedömningen körs om.
- Historiska dokument, format, paket och summor ska förbli läsbara och verifierbara. Ny fastställelse och verifiering av gammalt paket är skilda vägar.

| Felklass som granskningen särskilt ska söka | Prov som ska fånga den |
|---|---|
| En beskrivning av räckvidd blir numerisk reduktion eller ett löfte om faktisk kontroll | `test_rackvidd_andrar_inte_motorutfall` och `test_kallbeskrivning_ar_inte_genomforandebelagg` |
| Privat analys läcker till AI eller lokalt underkännande styr omförsök | `test_lokal_analys_paverkar_inte_ai_begaran_eller_anrop` |
| Ett gammalt godkännande återanvänds efter ändrat underlag, ny revision eller underkännande | `test_andringsmatris_kraver_nytt_godkannande` och `test_senaste_beslut_galler_utan_aterupplivning` |
| En gemensam analys döljer en tjänst, TF eller en kontrollbegränsning | `test_varje_erbjuden_tjanst_och_risktyp_kraver_svar` |
| Ny text/tabell eller äldre format kringgår gransknings-/paketkedjan | `test_v6_aterbyggs_fran_fryst_analys`, `test_v5_och_v5_1_kan_inte_nyfaststallas_efter_v6` och `test_historiskt_v5_paket_bevarar_summa` |

Fördjupa den fjärde felklassen med delanalyser, osynliga betalningsled, leverantörsberoende och ett plattformsfall. Den femte omfattar även gammal modellvalidering och ett oåtgärdat väsentligt modellfel. Testerna för dessa villkor finns i kompletteringstabellen och AB7; de är delar av samma granskningsfokus.

### Datakontrakt

Alla nya modeller är frysta Pydanticmodeller med `extra="forbid"`. Strängar med sakuppgifter trimmas; obligatoriska/aktiverade svar kan inte godkännas om de är tomma eller innehåller kvarvarande kompletteringsmarkörer. Ej aktiverade fördjupningar kan vara tomma med redovisad avgränsning; varken modellvalidator eller granskning får kräva fritext i dessa fält. Ingen minimilängd används som bevis på innehållskvalitet. ID:n kontrolleras mot katalog/profil; inga fria Python-/villkorsuttryck.

**A, regelbas:** ny `Kontrollrackvidd` i `src/riskanalys/regelverk/modeller.py`, placerad i `Kontroll.rackvidd: tuple[Kontrollrackvidd, ...] = ()`.

| Fält | Typ och innebörd |
|---|---|
| `id`, `tjanst`, `hot` | Stabilt räckvidds-ID, ett befintligt tjänste-ID och en icke-tom tuple av hot-ID:n som hör till tjänsten. Kontroll-ID följer av föräldraposten. |
| `beskrivningsstatus` | Genomförandeprecisering för steg 2: `Literal["beskriven", "okand"] \| None = None`. Frånvaro utelämnas i serialisering och behandlas som okänd. En beskriven möjlig observation är inte bevisad faktisk scenariotäckning. Positiv lokal täckning kräver relevant beskrivet stöd och eget genomförandebelägg. |
| `kan_belagga`, `begransningar`, `forutsattningar` | Icke-tom text om möjlig observation, vad den inte styrker och vilka förutsättningar som behövs. Inga påståenden om den aktuella byråns genomförande. |
| `grund`, `kallhanvisningar`, `sakkunnig` | Befintliga typer `Grund`, icke-tom `tuple[Kallhanvisning, ...]`, `Sakkunnig()`; källorna måste finnas och ingå i kontrollens `kallor`. |

Källunderlaget kontrolleras i de redan sparade primärkällorna i research 11; nya sakpåståenden kräver läsning av den exakta källpassagen. En slutsats om exempelvis falska fakturor får inte tillskrivas en källa som bara nämner avstämning. Egen härledning märks `metodval` och motiveras i texten. Saknas hållbart stöd lämnas räckvidden okänd, med synlig kompletteringspunkt. Ingen antagen full täckning.

Tom `rackvidd` utelämnas vid serialisering så äldre objektsummor består. Fylld räckvidd ingår i kontrollens innehållssumma och paketbindning. Operativa katalogändringar kräver ny regelbasversion (nästa minor efter nuvarande 1.3.0), aktualitetsprövning och nya berörda attester. Oförändrad numerisk metod betyder inte oförändrad regelbassumma.

**B, privat analys:** nytt paket `src/riskanalys/analys/` med följande modeller i `modeller.py`. Tjänste-ID används som nyckel; avsnittsnumret härleds vid dokumentbygget.

| Modell | Fält och validering |
|---|---|
| `Analysbelagg` | `id: str`, `profilfalt: tuple[str, ...]`, `dokument: str \| None`, `kontrollsumma: str \| None`, `datum: date`, `period: Period \| None`. Minst ett aktuellt bekräftat profilfält eller en privat dokumentkopia behövs. Dokument är en relativ sökväg under `analys/belagg/`, med obligatorisk SHA256; inga URL:er eller godtyckliga filvägar läses vid rendering. |
| `Delanalys` | `id: str`, `rubrik: str`, `arbetsmoment_och_befogenheter: str`, `belagg: tuple[str, ...]`. Underindelning av förälderns katalogtjänst, utan egen numerisk risknivå. Delanalysens scenarier ska ha egna motiveringar; olikartade arbetsmoment får inte döljas genom en gemensam standardtext. |
| `Betalningsinsyn` | `status: Literal["bedomd", "ej_tillamplig", "okand"]`, `synliga_floden: str`, `insynsluckor: str`, `avsandare_och_mottagare: str`, `underlagens_tillforlitlighet: str`, `motivering: str`, `belagg: tuple[str, ...]`. Begränsad men känd insyn kan beskrivas som bedömd; det betyder inte tillräcklig insyn. Ej tillämpligt kräver saklig motivering utifrån uppdraget. Kundkonton eller rapportidentifierare ska inte behöva exponeras i huvudtexten. |
| `Uppdragsprovning` | `status: Literal["hanterbart", "kraver_atgard", "kan_inte_hanteras", "okant"]`, `kompetens_och_insyn: str`, `motivering: str`, `handlingsalternativ: Literal["fortsatt", "forstark", "begransa", "avboj", "avsluta"]`, `beslutsstatus: Literal["forslag", "beslutad"]`, `ansvar: str \| None`, `datum: date \| None`, `belagg: tuple[str, ...]`. Beslut kräver identifierad ansvarig/datum. Avser byråns förmåga och gränser för uppdragstyper; kundspecifika rättsliga beslut och åtgärder hanteras i respektive kundakt. |
| `Leverantorsprovning` | `id: str`, `omfattning: str`, `leverantorens_kontroller: str`, `egen_verifiering: str`, `brister_och_motstridigheter: str`, `ansvar: str`, `belagg: tuple[str, ...]`. Beskriv faktiskt utfört/okänt arbete och eskalering vid brist. Ny lokalt beskriven leverantör får inte tyst motsäga profilens uppgift om extern KYC eller utkontraktering. |
| `Scenarioanalys` | `id: str`, `hot: tuple[str, ...]`, `rubrik: str`, `handelseforlopp: str`, `relevans: Literal["relevant", "ej_relevant", "okant"]`, `motivering: str`, `belagg: tuple[str, ...]`. Varje kataloghot prövas uttryckligen; flera lokala scenarier kan belysa samma hot. Extra scenario med tom `hot` är tillåtet men kräver egen motivering och blir ingen ny motorfaktor. |
| `Sarbarhetsprovning` | `id: str`, `omrade: Literal["kund", "kanal", "geo", "verk", "tjanst"]`, `sarbarheter: tuple[str, ...]`, `scenarier: tuple[str, ...]`, `relevans: Literal["relevant", "ej_relevant", "okant"]`, `motivering: str`, `belagg: tuple[str, ...]`. De fyra första områdena måste omfattas av en bekräftad prövning per tjänst, med återanvända profilbelägg; extra tjänstespecifik prövning är tillåten. Katalog-ID:n valideras; tom `sarbarheter` tillåter en lokalt identifierad svaghet utan att skapa en motorfaktor. Relevant prövning måste kopplas till minst ett relevant scenario. |
| `Kontrollprovning` | `scenario: str`, `kontroll: str`, `rackvidd: tuple[str, ...]`, `tillampning: str`, `utfall: str`, `belagg: tuple[str, ...]`, `tackning: Literal["bedomd_tillracklig", "delvis", "saknas", "okand"]`, `kvarstar: str`. Bedömd tillräcklighet avser bara angivet scenario och är ingen garanti eller automatisk riskreduktion. Hänvisningar valideras mot tjänstens lokala scenarier och uttryckligen bekräftade gemensamma scenariokopplingar samt tjänstens kontroller, räckvidd och belägg. |
| `Rutinatgard` | `id: str`, `scenarier: tuple[str, ...]`, `atgard: str`, `rutin_id: str \| None`, `rutin_version: str \| None`, `rutinbelagg: str \| None`, `status: Literal["foreslagen", "beslutad", "genomford"]`, `ansvar: str \| None`, `utlosare_eller_frekvens: str`, `uppfoljning: date \| None`, `belagg: tuple[str, ...]`. Icke-tom scenariokoppling och konkret handlingsbeskrivning krävs. Rutin-ID/version anges tillsammans och pekar via `rutinbelagg` på en `Analysbelagg` med privat dokumentkopia/hash; annars är alla tre tomma och rutinen visas som saknad. Beslut kräver ansvar/uppföljning; påstått genomförande kräver dessutom aktuell rutin och genomförandebelägg. |
| `Analysgap` | `id: str`, `typ: Literal["kunskapslucka", "kontrollbrist", "motstridigt_underlag", "metodkonflikt"]`, `beskrivning: str`, `status: Literal["oppet", "atgardat", "accepterad_kvarstaende_risk"]`, `motivering: str`, `ansvar: str \| None`, `tidsfrist: date \| None`, `belagg: tuple[str, ...]`. Accepterad kvarstående risk är ett lokalt beslut om en känd kontrollbrist, aldrig dispens från blockerande fynd eller sakkunnigkrav. |
| `Tjansteanalys` | `tjanst: str`, `exponering: str`, `exponeringsbelagg: tuple[str, ...]`, `scenarier: tuple[Scenarioanalys, ...]`, `scenariokopplingar: tuple[Scenariokoppling, ...]`, `sarbarhetsprovningar: tuple[Sarbarhetsprovning, ...]`, `kontroller: tuple[Kontrollprovning, ...]`, `samverkan: str`, `erfarenhetsprovning: str`, `erfarenhetsbelagg: tuple[str, ...]`, `pt_motivering: str`, `tf_motivering: str`, `reduktionsprovning: Literal["ej_reduktion", "motiverad", "metodkonflikt", "okand"]`, `reduktionsmotivering: str`, `sektorsjamforelse: str`, `sanktioner: str`, `slutsats: str`, `rutinatgarder: tuple[Rutinatgard, ...]`, `gap: tuple[Analysgap, ...]`. Separat PT och TF; sanktionsresonemang kan inte ersätta något av dem. De nya svaren ingår i svarssumman och blir aldrig manuella risknivåer. |
| `Analysbindning` | `byra: str`, `profilrevision: str`, `bedomningsmanifest: str`, `utkastmanifest: str`, `regelbas: str`, `kallunderlag: str`, `historik: str`, `bedomningsdatum: date`. Summorna avser det faktiska innehållet, inte bara filnamn eller versionsetiketter. `kallunderlag` är en kanonisk summa över använda källversioner/sparade lydelser. |
| `Analysbeslut` | `tjanst: str`, `revision: int`, `underlagssumma: str`, `svarssumma: str`, `godkand: bool`, `namn: str`, `roll: str`, `datum: date`, `kommentar: str \| None`. Namn/roll krävs; underkännande kräver kommentar. Datum får inte föregå den bedömning eller de belägg som beslutet avser. |
| `Analyspaket` | `schemaversion: Literal[1]`, `revision: int`, `bindning: Analysbindning`, `belagg: tuple[Analysbelagg, ...]`, `gemensamma_scenarier: tuple[Scenarioanalys, ...]`, `tjanster: tuple[Tjansteanalys, ...]`, `beslut: tuple[Analysbeslut, ...]`. Unika ID:n och en post per tjänst. Ett beslut gäller bara exakt aktuell revision och summor. |

**Delade scenarier och författarspår:** `Scenariokoppling(scenario: str, tillampning: Literal["samma", "avviker"], lokal_scenario: str | None, motivering: str | None)` pekar på paketets gemensamma scenario. `samma` bekräftas uttryckligen efter visning av tjänstens fakta; `avviker` kräver en lokal variant och motivering. Kataloghot måste täckas för varje tjänst, men samma hot behöver inte beskrivas fyra gånger. Kontrolltillämpning, delanalysreferenser och bevis för effekt valideras fortfarande inom respektive tjänst. Gemensamma scenarier har inga tjänstespecifika delanalys-ID:n; sådana hör till den lokala varianten. Ändrad gemensam analys gör de beroende bekräftelserna inaktuella.

`Tjansteanalys` får `forfattare: str | None` för den aktuella svarsrevisionen; programutkast har ingen mänsklig författare förrän någon sparat/bekräftat dem. `Analysbeslut` får `egen_granskning: bool`, härledd av programmet genom jämförelse med författaren. Attest kräver identifierad författare. Programmet härleder flaggan vid beslut; en importerad flagga betros inte. Identiteter använder samma lokala personidentifiering i CLI/webb, inte skilda rollnamn. Ingen autentiserad signatur eller upptäckt av medvetet falsk identitet utlovas. Beslutshistoriken bevarar båda identiteterna för den granskade revisionen.

**Tillägg till modellerna ovan efter fortsättningsgranskningen:** `Tjansteanalys` får `delningsmotivering: str`, `delanalyser: tuple[Delanalys, ...]`, `betalningsinsyn: Betalningsinsyn`, `uppdragsprovning: Uppdragsprovning`, `leverantorsmotivering: str`, `leverantorer: tuple[Leverantorsprovning, ...]`. Den lokala `Scenarioanalys` får `delanalyser: tuple[str, ...]`; alla referenser ska finnas hos samma tjänst. Om en tjänst har delanalyser måste varje relevant scenario få en lokal koppling/variant till minst en av dem och varje delanalys ha scenarioanalys; delade scenarier används då som redigeringsunderlag för de lokala varianterna. Utan delning krävs motivering, inte en tom standardpost. Sårbarheter/kontroller/rutinåtgärder kopplas via scenario-ID:n och ska därmed kunna följas till rätt arbetsmoment.

`Analysbindning` får `modell: str` från AB7:s aktuella modellidentitet. `Analyspaket` får `modellrisk: Modellriskunderlag | None` från `drift/modellrisk.py`; saknad post tillåter utkast men inte ny slutlig attest/fastställelse. Modellriskunderlaget och alla nya lokala svar omfattas av paket-/svarsbindningen. Införandet ändrar inte äldre dokument-, profil- eller historikpayloads; analysschema 1 har nu implementerats utan historiska produktionsposter att migrera.

`revision` är en ökande lokal registerrevision, inte profilens revisionshash. En innehållsändring ökar revisionen; registrering av ett beslut ändrar inte svarens revision/summa. Beslutshistoriken är tillägg, och det senaste beslutet för tjänsten avgör. Ett underkännande får inte passeras genom att välja en äldre matchande godkänd post. Äldre svar kan användas som redigeringsstöd, aldrig som automatisk aktuell bekräftelse. Vid byte av bindning måste granskaren aktivt uppdatera och godkänna svaren igen.

### Genomförandeprecisering av redan beslutade bekräftelser

Läsförberedelsen fann att modelltabellen behöver lagra den skillnad mellan förifyllt och bekräftat som planen redan kräver. Detta tillför inga nya guidesteg eller riskregler:

- `Analysblock(nummer: int, aktivering: Literal["aktiv", "ej_tillamplig", "okand"], motivering: str, bekraftad_summa: str | None = None)` lagras i `Tjansteanalys.block`. Nummer 1–16 är unika. En aktiv obligatorisk fråga kräver bekräftelse av sitt visade innehåll, en motiverat ej aktiv fördjupning kräver inte ett nytt fritextsvar. En bekräftelsesumma binder relevant blockinnehåll, refererat underlag och aktuell underlagsbindning; den får inte inkludera sig själv, beslut eller registerrevision så att en bekräftelse upphäver sig själv. Oförändrade bekräftade block kan återanvändas medan ändrade svar fortfarande upphäver tjänsteattesten.
- `Scenariokoppling` får `scenariosumma: str` och `bekraftad: bool = False`. Visad summa måste matcha den aktuella gemensamma analysen; programmet får inte automatiskt flytta ett gammalt samma-val till ändrad text. Förifyllnad skapar inget förvalt samma/avviker-val.
- `Analysbeslut.forfattare: str` härleds vid append och bevarar författaren till den granskade revisionen. En importerad egen-granskningsflagga betros inte.
- Gemensam godkännandetransaktion verifierar aktuell profil, analys, modellrisk, faktiska belägg och CAS under lås, återanvänd av CLI/webb. Låsordning vid historikbunden attest/publicering är profil → analys → drift; interna låsta sparhjälpare får inte återta samma flock. De rena prövnings-/beslutsfunktionerna är inte ensamma filaktualitetsgrindar.

AB1:s kompletterande statusfält och uttrycklig katalogklassning görs först i steg 2, efter den sparade 1.4.0-kontrollpunkten. Operativa metadata kräver nästa minor 1.5.0 och förnyad innehållsbunden attest; ingen numerisk metodändring. Okänd källa kan vara korrekt sakkunniggranskad som okänd och blir ändå inte positivt täckningsstöd. Historiska utelämnade fält bevarar sina summor.

### Guidad checklista med förifyllnad och tjänstevisa avvikelser

Samma grundfrågor gäller varje faktiskt erbjuden tjänst, även en liten sådan. För okänt erbjudande krävs först komplettering i intaget; "erbjuds inte" stöds av aktuellt profilbelägg. Programmet förifyller redigerbara utkast från bekräftade fakta, motorutfall och källbundna förklaringar. Källor, datum, period och beläggs-ID följer med. Okända uppgifter står som okända, inte som påhittade slutsatser. Faktisk tillämpning/effekt och mänskliga beslut förblir ogranskade tills en person tagit ställning. Ingen automatisk attest, och ingen analysfritext till AI.

De 16 raderna är **guidesteg**, inte krav på 16 nya fritextsvar per tjänst. Samma belägg kan refereras från flera svar. Förifyllnadens text är läsbar utkasttext med separat status; ingen slutlig text markeras med kompletteringsmarkör enbart för att en valfri fördjupning lämnats tom.

| Nr och guidesteg | Typat svar/återanvändning | Krävs |
|---|---|---|
| 1. Vilket uppdrag, kunder, period och mandat? | `exponering` och belägg; byrågemensamma tal får inte bli tjänstespecifika tal. | Alltid |
| 2. Behöver arbetsmoment delas upp? | `delningsmotivering`, eventuella `delanalyser`; ingen uppfunnen delnivå. | Alltid |
| 3. Vilka betalningsled ser vi? | `betalningsinsyn`; avstämning av ett konto bevisar inte full insyn. | Vid relevant transaktionsinsyn |
| 4. Kan vi hantera uppdragstypen? | `uppdragsprovning`; kompetens/insyn och motiverat handlingsalternativ. Ingen automatisk kundåtgärd. | Alltid |
| 5. Vad gör leverantören och vi själva? | `leverantorsmotivering`/`leverantorer`; faktisk kontroll, eget ansvar och konflikter. | Vid extern KYC/utkontraktering |
| 6. Hur kan uppdraget missbrukas? | Lokalt eller delat `Scenarioanalys`; varje kataloghot prövas för tjänsten. Noll rapporter bevisar inte frånvaro av hot. | Alltid |
| 7. Vilka sårbarheter möjliggör det? | `sarbarhetsprovningar`: kund, kanal, geografi, egen verksamhet med belägg. Ett falskt katalogvillkor avslutar inte områdets prövning. | Alltid |
| 8. Hur samverkar faktorerna? | `samverkan`; motivera förstärkning/begränsning och osäkerhet, inte bara faktorantal. | Alltid |
| 9. Vad har erfarenhet/bevakning lärt oss? | `erfarenhetsprovning` och belägg; motivera tjänstekopplingen även vid oförändrad slutsats. Kundidentifierande rapporter infogas inte. | Alltid |
| 10. Vilken faktisk kontroll och effekt? | `Kontrollprovning` med aktuellt belägg; saknad kontroll registreras som brist. | Vid relevant scenario |
| 11. Vad täcks inte eller förblir okänt? | `kvarstar`/`Analysgap`; känd brist skiljs från okänd effekt. | Vid relevant scenario |
| 12. Stöds motorns faktiska reduktion? | `reduktionsprovning`/motivering; utan reduktion förifylls `ej_reduktion`. Olöst konflikt spärrar attest. | Vid faktisk reduktion |
| 13. Är PT-utfallet rimligt? | `pt_motivering` mot exponering/scenarier, inga alternativa numeriska nivåer. | Alltid |
| 14. Vilka TF-scenarier/osäkerheter finns? | Separat `tf_motivering`, även lagligt ursprung kan vara relevant; PT-text ersätter inte TF-prövningen. | Alltid |
| 15. Avviker vi från sektorsbilden, och hur berörs sanktioner? | `sektorsjamforelse`/`sanktioner`; listkontroll ersätter inte TF-analys. | Vid relevant avvikelse/anknytning |
| 16. Vilken slutsats, rutin och uppföljning följer? | `slutsats`, `rutinatgarder`, gap; återanvänd befintlig rutin/belägg, skilj föreslaget/beslutat/genomfört. Oförändrad rutin motiveras. | Alltid |

**Obligatoriskt/villkorat:** alltid obligatoriska block är raderna **1, 2, 4, 6, 7, 8, 9, 13, 14 och 16** (10). Rad 3 fördjupas vid betalnings-/transaktionsinsyn i uppdraget; 5 vid extern KYC/utkontraktering; 10–11 vid relevanta scenarier; 12 vid faktisk motorreduktion; 15 vid relevant sektorsavvikelse eller sanktionsanknytning. För varje villkorad rad visas skälet till att den aktiverats/avgränsats. Bekräftade fakta kan ge ett motiverat förslag om ej tillämpligt, men okänd uppgift får inte tolkas som nej. Övriga tjänstespecifika följdfrågor är stöd, inte fristående obligatoriska svar. Sakfrågor inom ett block måste täckas; att räkna block är inte att räkna varje fält eller klick.

**Planerat acceptansfall med fyra tjänster (`T-RED-01`–`04`):** 10 × 4 = **40 alltid obligatoriska blockbedömningar**. Fallet använder extern KYC, relevant betalningsinsyn, relevanta scenarier, faktisk reduktion och sektors-/sanktionsfråga i alla fyra tjänster: ytterligare 6 × 4 = **24 villkorade block**, totalt **64 bekräftade blockbedömningar**. Katalogen har för dessa tjänster åtta gemensamma och fyra tjänsteunika hot: **12 unika scenarioanalyser** kan täcka de 36 tjänst–hot-kopplingarna utan fyra kopior av samma analys. De åtta gemensamma scenariernas samma/avviker-val visas samlat men loggas uttryckligen för var och en av tjänstens kopplingar (32 val); fyra unika scenarier ligger lokalt. Fyra tjänsteattester avslutar analysen. En gemensam granskningsåtgärd får bekräfta visade val för markerade tjänster, aldrig osedda förval. Detta är ett specificerat provfall, inte uppmätt tidsåtgång eller ett löfte om 16 klick. AB3/AB6 ska redovisa separat antal block, scenarier, bekräftelseval, belägg som återanvändes och faktiskt nyskrivna kompletteringar. Ingen säger att byrån måste skriva över 100 nya svar.

En obesvarad obligatorisk/aktiverad sakfråga, okänd relevant uppgift, saknat åberopat belägg, motsägelse mot bekräftade fakta eller olöst metodkonflikt hindrar lokalt godkännande. En ej aktiverad följdfråga skapar inget eget hinder. Känd kvarstående risk kan godkännas med motiverade åtgärder; den behöver inte vara eliminerad. Innehållets riktighet kan inte maskinbevisas av att alla fält är ifyllda.

Programmet upptäcker strukturella fel och konflikter mellan typade statusar/referenser; granskaren måste själv ange sakliga motsägelser och metodkonflikter som inte kan utläsas ur strukturen. Fri text kan inte sanningsprövas med dessa kontroller. `bedomd_tillracklig`/`delvis` kräver åberopad källräckvidd och aktuellt genomförandebelägg; ett relevant scenario utan sådan räckvidd ska visa okänd täckning eller en dokumenterad kontrollbrist, aldrig ett konstruerat källstöd.

`samverkan` och `erfarenhetsprovning` är obligatoriska sakgranskningsfrågor, även om utfallet blir att en viss omständighet inte påverkar slutsatsen. `reduktionsprovning="okand"` eller `"metodkonflikt"` blockerar godkännande. Programmet får kontrollera att en åberopad kontroll/effekt har en faktisk länk till det relevanta scenariot; det får inte härleda en ny reduktionsstorlek ur länken. En påvisad konflikt mellan motorns reduktion och dokumenterad kontrollräckvidd måste hanteras som `Analysgap(typ="metodkonflikt")`. Den får inte markeras som accepterad kvarstående risk. Textvalidering kan inte avgöra om bedömningen är fackmässigt riktig; M1–M4 och berörda sakkunniggrindar kvarstår.

`ej_reduktion` måste stämma med det faktiska motorutfallet och avvisas om motorn sänkt nivån. `motiverad` kräver stöd i den lokala kontrollprövningen; statusvalet är inte i sig ett belägg. Prova detta med `test_reduktionsprovning_maste_stamma_med_motorutfall` i AB2, inklusive försök att dölja en faktisk sänkning som "ej reduktion".

Rutinbindningen avser den registrerade privata kopian. En rutin som ändras i ett annat system utan att registreras kan inte upptäckas automatiskt här; granskaren måste säkerställa att rätt aktuella version har lämnats. Ett redan känt bindande rutinkrav får inte accepteras bort genom att åtgärden märks som föreslagen eller beslutad.

Okänd uppdragshanterbarhet eller en dokumenterad oförmåga som ändå kombineras med fortsatt oförändrat uppdrag blockerar lokal slutlig attest. "Kräver åtgärd" behöver beslutad relevant åtgärd/avgränsning och belägg för att förutsättningarna för den bedömda hanterbarheten är uppfyllda. Programmet bedömer struktur och motstridiga statusar; en människa prövar kompetens/insyn och fattar verksamhetsbeslut. En rapport kan korrekt beskriva att byrån inte erbjuder en viss uppdragsvariant. Att blockera godkännande av rapporten är ett annat beslut än att förbjuda eller avsluta en kundrelation.

Följande tjänsteanpassade följdfrågor visas som stöd till grundfrågorna. De är frågor, inte konstaterade risker eller nya katalog-/motorregler. Ett svar kan motivera att omständigheten inte gäller. Inför skarp användning ska frågestödet prövas i samma käll- och sakgranskning som övrig analystext.

| Befintlig tjänst | Följdfrågor för lokal prövning |
|---|---|
| `T-RED-01` Löpande bokföring | Vem tillhandahåller underlaget och hur prövas transaktionens affärsmässiga innebörd? Vad kan en bankavstämning visa om en betalning vars faktura verkar korrekt men vars innehåll är felaktigt? |
| `T-RED-02` Bokslut och årsredovisning | Vilka uppgifter om balansposter, värderingar, ägarlån och närståendetransaktioner verifierar vi själva? Vad bygger endast på kundens uppgifter? |
| `T-RED-03` Deklarationer och deklarationsombud | Vilken information ser vi utöver deklarationsunderlaget och vilka ombudsbehörigheter har vi? Hur hanteras avvikande rättelser och återbetalningsuppgifter? |
| `T-RED-04` Lönehantering | Hur styrks anställnings-/löneunderlag och ändringar av mottagarkonto? Kan vi upptäcka att en rapporterad person inte utför det arbete som uppges? |
| `T-RED-05` Betalningar och attest i kundens namn | Vem får lägga upp mottagare, ändra konto och godkänna betalningen? Är behörighet och oberoende kontroll belagd i just vårt uppdrag? |
| `T-RED-06` Klientmedelskonto | Vem har rätt till medlen, varför passerar de kontot och hur stäms innehav och utbetalningar av? Vilka belägg har vi för avsändare, mottagare och betalningsändamål? |
| `T-RED-07` Ekonomisk rådgivning och ekonomichefstjänster | När övergår vår rådgivning till beslut, attest eller genomförande? Vilken insyn har vi i de transaktioner och motparter som besluten avser? |
| `T-SKATT-01` Skatterådgivning utöver deklarationer | Vilka upplägg och gränsöverskridande flöden medverkar vi till att utforma? Hur prövas syfte, ägarbild och vår faktiska insyn utan att likställa skatteplanering med penningtvätt? |
| `T-BOLAG-01` Bolagsbildning, lagerbolag och bolagsförmedling | Vilka ägare, företrädare, ändamål och finansieringsuppgifter kan vi styrka vid bildning/överlåtelse? Vad ser vi av efterföljande användning? |
| `T-BOLAG-02` Registrerad adress eller postadress | Vilken faktisk kontakt och verksamhetsanknytning kan vi styrka? Hur följs ändrade företrädare, posthantering och vår begränsade insyn upp? |
| `T-BOLAG-03` Styrelseuppdrag eller bolagsrättsligt ansvar | Vilka formella och praktiska befogenheter har vi och vilket underlag når oss inför beslut? Hur hanteras situationer där övriga företrädare kontrollerar informationen? |

### Godkännandekedja och när den slutar gälla

1. Bygg bindningen ur aktuell profil, vald bedömning, validerade skrivresultat, regel-/källunderlag och historik. Förifyll ett ogranskat utkast; registrera sedan bekräftade lokala svar, delade scenariokopplingar, författare och återanvända/nya belägg mot bindningen.
2. Granskaren godkänner varje tjänsteanalys mot `underlagssumma` + `svarssumma` + registerrevision. Logga författare/godkännare och härledd egen granskning; visa den i översikten utan ny spärr. Dokumentet får visa svar även innan godkännande, men markerar dem som ogranskade.
3. Bygg v6 från exakt fryst analyspaket. Spara paketets summa och kopia i granskningskörningen; komplettera manifestets metadata och dokumentets B1. Återbyggnad måste få samma dokument, inklusive status och referenser.
4. Befintlig sakgranskning godkänner det renderade dokumentet, ordningen och analysbindningen. En ny valfri bindningssumma i `Sakgranskning` ska utelämnas när den saknas i historiska poster. Ingen godkännandepost stoppas tillbaka i texten som den själv hashbinder.
5. Fastställelse läser den frysta kopian, jämför med aktuellt privat register/underlag och kräver båda godkännandena plus befintliga juridiska, metodiska och övriga grindar. Paketet bevarar underlag och lokal attest för framtida verifiering utan tillgång till det levande registret.

| Ändring | Följd |
|---|---|
| Profilvärde, status, datum, period, källa, belägg eller namn | Konservativt: hela profilrevisionen ändras; alla lokala tjänstegodkännanden och den beroende dokumentgranskningen kräver omprövning. |
| Bedömning, tjänsteutbud, motor-/regelutfall, regelbasversion eller innehåll | Ny bindning och ny lokal granskning, även om samma visningsnivå blir resultatet. Enbart lika nivåer är ingen återanvändningsgrund. |
| Räckviddstext, källa/sparad lydelse eller sakkunnigstatus | Ny bindning/granskning och berörda regelbasattester prövas igen. Externa webbsidor bevakas inte här; giltighet avser kontrollerade källversioner, inte okända webbändringar. |
| Beläggsfil eller dess metadata, svar, scenario eller gapbeslut | Ny registerrevision; tidigare lokala godkännanden gäller inte. Filens faktiska hash kontrolleras även när dess namn är oförändrat. |
| Sårbarhetsprövning, samverkans-/erfarenhetssvar, reduktionsprövning eller rutinens version/status | Ingår i svarens aktuella bindning. Ändring kräver ny registerrevision och lokal attest; ett genomförandepåstående kan inte ärvas från ett förslag. Refererade privata rutinversioner/hashar kontrolleras vid godkännande och paketering. |
| Delanalys/arbetsmoment, betalningsinsyn, uppdragsbeslut eller leverantörsprövning | Ny registerrevision och lokal attest. Den gamla gemensamma analysen får inte godkänna en ny uppdragsvariant eller en förändrad insynslucka. |
| Motor-/regelbasidentitet, modellriskrutin, valideringsrapport, ansvarig eller feluppföljning | Modellriskunderlaget måste gälla aktuell modell och aktuellt läge. Ändring bryter beroende analys-/dokumentattester; ny rapport eller omprövning registreras vid modelländring eller väsentligt nytt fel. Äldre paket behåller sin frysta evidens. |
| Enbart Python-/biblioteksversion eller kod utanför modellen | Miljöuppgiften uppdateras; modellbindningen och modellrapportens giltighet bryts inte automatiskt. Ändrat dokument-/AI-innehåll kan ändå kräva ny dokument-/analysgranskning enligt övriga rader. Upptäckt beteendefel hanteras i feluppföljningen. |
| Nytt underkännande eller återkallande | Senaste beslutet gäller; nytt uttryckligt godkännande behövs. Återställning till äldre svar återupplivar inte godkännandet. |
| AI-skrivresultat eller versionshistorik | Ny bindning, lokal omprövning och ny dokumentgranskning. Ny körning får inte tyst låna äldre analysattest. |
| Rubrik, ordning, cell, hänvisning eller lokal text i dokumentet | Dokumentgodkännandet faller. Oförändrad underlags-/svarsbindning kan behålla lokal analysattest; dokumentet återbyggs och sakgranskas igen. |
| Nytt dokumentformat | Ny dokumentsakgranskning. Historiska v5-godkännanden gäller endast historiska paket, inte ny fastställelse i v6. |
| Belägg är inte längre aktuellt vid nytt bedömnings-/beslutsdatum | Aktualitetsprövning enligt befintliga regler; inga antagna nya giltighetstider införs här. Underlag och granskning uppdateras vid brist. |

Det befintliga innehållsbaserade profilrevisionsskyddet är inte en manipulationssäker händelselogg. Återställning av hela den privata datamappen eller en profil som ändras och återställs mellan kontroller kan inte upptäckas enbart med dessa summor. Ny analysrevision och nya beslut skyddar normala ändringsflöden; planen lovar inte skydd mot en användare som skriver om hela historiken.

### Dokumentets läsordning och ordbudget

Behåll stabila ID:n och en Word-fil. Efter kort syfte/avgränsning (`D-ARB.1`) kommer risksammanställningen (`D-ARB.8`) före metoddetaljer och tjänsteanalyser. Första översikten ska alltid visa faktisk sakkunnigstatus och vilka M1–M4 som är öppna; i dagens läge står ogranskad metod tydligt där, inte bara i bilagan. Inga påståenden om generell juridisk kvalitet eller "bästa struktur".

Varje tjänst visar exponering, konkreta scenarier, en kompakt tabell **scenario / faktisk kontroll och belägg / begränsning och kvarstående risk**, separata lokala PT-/TF-resonemang och åtgärder. Källbeskrivningen skrivs en gång i det gemensamma kontrollavsnittet; tjänsttabellen hänvisar till den och beskriver den lokala tillämpningen. Beräkningstabeller, fullständiga metadata och källversioner samlas i B1 med tjänstevis återhänvisning. Ingen information får försvinna vid flytten.

Scenariotabellen eller ett kort anslutande stycke ska också visa sårbarheternas betydelse och samverkan. Läsaren ska kunna följa **hot → sårbarhet/kombination → faktisk åtgärd och begränsning → motiverad risknivå → rutin/uppföljning** utan att behöva rekonstruera resonemanget ur B1. Bevara motiveringen av omfattningen efter byråns storlek och art. Risköversikten är en sammanfattning av de underliggande analyserna; ogranskad metod och olöst reduktionskonflikt ska framgå i översikten.

Delanalyser ligger under sin befintliga tjänst med stabila lokala ID:n; deras bedömda skillnader, insynsluckor och hanterbarhet ska framgå i huvudtexten. Skriv inte ut egna delnivåer som saknar motorstöd. Gemensam leverantörsbeskrivning kan återges en gång med hänvisningar, men tjänstens faktiska beroende och begränsning måste framgå lokalt. Sammanfatta modellansvar/version, valideringsstatus och öppna modellbegränsningar i metodavsnittet; full rutin/rapport/felregister ligger i privat granskningsunderlag och bevaras med paketet. Den rena v6-byggaren får ett valfritt typat `modellrapport: Modellvalidering | None` från den verifierade frysta rapportbeskrivningen. Gransknings-/återbyggnadsvägen kontrollerar dess verkliga refererade bytes och lämnar samma rapportobjekt vidare; byråns eget godkännande betyder aldrig att sakkunnig godkänt M1. Saknad rapportbeskrivning visas som ej styrkt, utan filinläsning i byggaren. Känsliga kundfall och misstankerapporter ska inte följa med den bredare Word-rapporten.

Avsnittet Utvärdering och uppdatering ska visa senaste dokumenterade utvärdering, senaste eventuella uppdatering med relevant ändringsbeskrivning och nästa utvärdering. Vid avsaknad av uppdateringshändelse används "Ingen separat uppdatering registrerad", utan att skapa en händelse eller påstå att ingen ändring någonsin skett. Nästa ordinarie genomgång beräknas fortfarande från senaste utvärdering; enbart uppdatering får inte flytta årsfristen. Tidigare v5-avsnitt/paket ändras inte på plats.

I v6 behålls endast AI-delarna `hot` och `sarbarheter` (oförändrade gränser 80–160 respektive 100–220 ord). AI-kontroller, AI-nivåtext och AI-slutsatser utgår; deras lokala innehåll finns kvar. Byråns lokala analys märks tydligt och får inte framstå som AI-validerad. Den nya lokala författaruppgiften behöver en separat `kalla="lokal"` i dokumentmodellen; äldre serialisering ska vara oförändrad. Blandade tjänsteavsnitt får dessutom valfri `proveniens` (`ai`, `regelbas`, `lokal`) på `Textstycke` och `Tabellcell`; frånvarande värde utelämnas så äldre summor bevaras. Hela avsnittets granskade innehåll binder även denna proveniens.

Huvudtextmålet är fortsatt **3 500–5 000 ord** för fyrtjänstfallet. Ny budget: orientering/översikt 400, gemensamt underlag/kontroller/metod och delade scenarier 700, fyra tjänster vardera högst 380 AI-ord + riktvärde 420 lokala ord, åtgärder/uppföljning 400: **4 700 ord**. AI-max blir 4 × (160 + 220) = **1 520 ord**, jämfört med 3 000 i femdelarsflödet. Gemensamma scenarier skrivs en gång; tjänsterna visar tillämpning/avvikelse och relevanta kontroll-/nivåmotiveringar. Återge inte samma scenario som lång AI-text och lång lokal text. Mät verkliga ord även med AI-max och utvecklade lokala svar; riktvärdet 420 är inget tak som får kapa nödvändig analys. Budgetavvikelse redovisas, ingen automatisk trunkering eller sidgaranti.

### Genomförande i sju verifierbara uppgifter

**Arbetsform vid genomförandet:** användaren har beställt subagenter; `subagent-driven-development` används med tester före kod, uppgiftsgranskning och samlad slutgranskning. Filernas leveransstatus framgår av genomförandeloggen och STATUS. Ingen commit eller push ingår utan uttrycklig beställning. Efter varje uppgift körs dess relevanta prov; fullsvit på slutläget. Ett fynd i gränssnittet ska rättas i denna plan, inte döljas med en alternativ väg.

Behåll uppgifts-ID:n och dela AB4 i två oberoende leveransdelar:

- **Steg 1: AB1 → AB4a.** Källbunden räckvidd och ny läsordning på befintligt skriv-/bedömningsunderlag. Nytt dokumentformat `D-ARB-tjanst-v5.1` skiljer dispositionen från historisk v5. Granska, kör fullsviten, lämna sammanhållen diff för separat beställd commit. Ingen beroendeväg till AB2/AB7 eller ny analysgrind.
- **Steg 2: AB7 → AB2 → AB3 → AB4b → AB5 → AB6.** Privat analys med förifyllnad/delning, tvådelad AI-skrivning i v6, egen-granskningslogg och nya grindar. AB7 ligger sist i texten för stabila hänvisningar. Den sparade steg 1-kontrollpunkten beror inte på steg 2. Aktuell leveransstatus anges nedan.

Båda stegen har egen granskning och grön fullsvit före eventuell commit; ingen push ingår.

#### AB1. Källbunden, beskrivande räckvidd

**Modify:** `src/riskanalys/regelverk/modeller.py`, `validering.py`, `sakkunnig.py`; `regelbas/kataloger/kontroller.yaml`, `regelbas/version.yaml`. Loaderns befintliga kontrollkatalog räcker; inget nytt globalt katalogregister behövs.

**Create/Test:** `tester/regelkontrakt/test_kontrollrackvidd.py`; komplettera `tester/m2/test_sakkunnigpaket.py` och `tester/enhet/test_laddning.py` vid berörda attest-/hashfall.

**Consumes/produces:** befintlig `ladda_regelbas(rot: Path) -> Regelbas` producerar kontroller med ovanstående `rackvidd`; `validera(regelbas: Regelbas) -> list[str]` kontrollerar alla korsreferenser. Befintlig `granskningsobjekt(rb: Regelbas, paket_id: str) -> dict[str, str]` ska omfatta de nya räckviddsobjektens attester utan att automatiskt godkänna dem.

Komplettera även `Regelbas.alla_id()` och attesternas export/import/applicering för stabila räckvidds-ID:n. Varje räckvidd har egen innehållssumma; dess föräldrakontroll binds till innehållet utan granskningsmetadata. Ingen attest får förbli giltig genom att bara versionssträngen eller den nya underpostens status ändras. En oförändrad post kan behålla en fortfarande matchande attest enligt befintligt flöde.

- [ ] RED: `test_rackvidd_kraver_precis_kalla_och_giltiga_korsreferenser` avvisar okänd tjänst/hot/källa, dubbla räckvidds-ID och källhänvisning utanför kontrollens källor.
- [ ] RED: `test_tom_rackvidd_bevarar_historiska_objektsummor` jämför gamla payloads mot frysta summor; `test_andrad_rackvidd_kraver_ny_attest` ändrar bara en begränsning.
- [ ] Källäs och inför bara stödjbara beskrivningar. Ange uttryckligen okänd räckvidd där underlag saknas. Behåll `ej_granskad` och versionshöj katalogen.
- [ ] Kontrollera de sex kompletteringarnas primärkällor mot befintligt källregister innan eventuella nya källposter skapas; matcha innehåll/hash och undvik dubbletter. Utöka `test_rackvidd_andrar_inte_motorutfall` med leverantörs- och plattformsfallen. Saknat katalogstöd ska ge ett öppet käll-/metodbehov, inte en odokumenterad riskfaktor eller ett extra sannolikhetssteg.
- [ ] GREEN: `.venv/bin/pytest tester/regelkontrakt/test_kontrollrackvidd.py tester/m2/test_sakkunnigpaket.py tester/enhet/test_laddning.py`; förväntat alla passerar. `test_rackvidd_andrar_inte_motorutfall` jämför risker, regelvillkor och reduktionsbeslut på identiska profilfall före/efter, med endast provenienssummor undantagna.

#### AB2. Privat analys, belägg och revisionsskydd

**Create:** `src/riskanalys/analys/__init__.py`, `modeller.py`, `lagring.py`, `provning.py`, `utkast.py`. **Test:** nya `tester/enhet/test_lokal_analys.py` och `test_analyslagring.py`.

**Consumes/produces:** modellerna ovan. `bygg_bindning(byramapp: Path, rb: Regelbas, bedomningsmapp: Path, utkastmapp: Path) -> Analysbindning`; `las_analys(byramapp: Path) -> Analyspaket | None`; `spara_analys(byramapp: Path, paket: Analyspaket, *, forvantad_summa: str) -> str`; `analysbrister(rb: Regelbas, profil: Profil, bedomning: Bedomning, paket: Analyspaket) -> tuple[str, ...]`; `registrera_beslut(paket: Analyspaket, beslut: Analysbeslut) -> Analyspaket`. `forifyll_analys(rb: Regelbas, profil: Profil, bedomning: Bedomning, bindning: Analysbindning) -> Analyspaket` i `utkast.py` ger ett ogranskat paket med käll-/beläggsreferenser, inga påhittade effektpåståenden eller attester. Befintliga manuella svar skrivs aldrig över; förnyad förifyllnad visas som jämförelseförslag.

`bygg_bindning` använder AB7:s `modellbindning(rb)` för `Analysbindning.modell`. `analysbrister` och `registrera_beslut` förblir rena modellfunktioner. Gränssnittens godkännväg ska först anropa `modellriskhinder(byramapp, rb, paket.modellrisk, beslutsdatum)` för aktuell kod, datum och faktiska beläggsfiler, därefter pröva analysbrister och registrera beslutet under befintligt revisions-/aktualitetsskydd. AB5 upprepar kontrollen före ny fastställelse; en importerad godkänd status får inte kringgå den.

Spara i `analys/analys.yaml` med privat lås, CAS, historik, temporär fil, fsync och atomiskt namnbyte enligt mönstret i `profil/lagring.py`; skapa inte en allmän lagringsram. `forvantad_summa=""` betyder inget befintligt register. Returnerad summa omfattar även beslutshistoriken; den skiljer sig från svarssumman. Jämför aktuell profil/bindning före godkännande och igen före senare användning. Godkännande från inaktuell flik avvisas.

Registerrevisionen ökas och kontrolleras på serversidan under låset; importerade formulär/filer får inte välja ett äldre revisionsnummer. Håll beslutsappend och svarändring åtskilda så att godkännande inte självt gör de nyss granskade svaren inaktuella.

Belägg lagras som privata kopior med innehållsadresserade filnamn i `analys/belagg/`; import tillåter inte symlänksflykt eller filer utanför det uttryckligen valda underlaget. `importera_belagg(byramapp: Path, fil: Path) -> tuple[str, str]` returnerar relativ sökväg och SHA256, utan att bekräfta dess sakinnehåll. Återläsning kontrollerar både sökväg och faktiska bytes. Webb väljer registrerade belägg; ingen godtycklig lokal filrouter byggs.

- [ ] RED: `test_forifyllnad_ar_redigerbart_utkast_utan_attest` och `test_delat_scenario_kraver_samma_eller_avviker_per_tjanst` provar förifyllnad, återanvända belägg, lokal avvikelse, otäckta hot och inaktuell delad analys. `test_samma_forfattare_och_godkannare_loggas` kräver rätt loggidentiteter utan spärr; annan person ska inte felmärkas.
- [ ] RED: `test_varje_erbjuden_tjanst_och_risktyp_kraver_svar`, `test_kallbeskrivning_ar_inte_genomforandebelagg`, `test_okand_effekt_och_metodkonflikt_blockerar` samt `test_kand_kontrollbrist_kan_ha_motiverad_uppfoljning` prövar frågetabellen och gapreglerna.
- [ ] RED: `test_sarbarhetsprovning_kraver_fyra_omraden_och_belagg` provar att utebliven kund-/kanal-/geo-/verksamhetsprövning var för sig hindrar attest; okänd relevans och saknade/okända belägg avvisas. `test_samverkan_och_separata_nivamotiveringar_kravs` provar saknad samverkan, PT respektive TF var för sig. `test_egna_lardomar_kraver_provning` kräver motiverad tjänstekoppling till aktuell egen erfarenhet/bevakning, även vid noll rapporter.
- [ ] RED: `test_rutinatgard_skiljer_forslag_beslut_och_genomforande` avvisar halv rutinreferens, beslut utan ansvar/uppföljning och genomförandepåstående utan aktuell rutin och belägg. Avsaknad av rutin visas som lucka och får inte bli genomfört genom en standardtext. Relevanta riskbeslut utan ändring ska hänvisa till befintlig rutin och ha uttrycklig motivering.
- [ ] RED: `test_bankavstamning_utan_scenariotackning_ger_metodkonflikt` använder ett falskt-faktura-scenario, bara bankavstämning, dokumenterad saknad täckning och motorreduktion. Lokal attest avvisas och metodkonflikt krävs, medan motorns nivå bevaras. Komplettera med utan-reduktion och belagd scenariokoppling så att en känd kvarstående risk inte likställs med automatiskt felaktig reduktion.
- [ ] RED: `test_tjanstens_detaljniva_kraver_motivering_och_scenariokoppling` avvisar omotiverad utebliven delning, delanalys utan scenarier och referens till annan tjänsts delanalys. Ett delat bokföringsfall ska bevara de skilda resonemangen utan att skapa egna motorutfall.
- [ ] RED: `test_bankavstamning_ar_inte_fullstandig_betalningsinsyn` visar att ett avstämt synligt konto kan förenas med kända saknade flöden. Kräv motivering/tillförlitlighetsprövning; markera begränsningen och pröva den i hanterbarheten. Motiverat begränsat uppdrag ska inte automatiskt kräva insyn i samtliga kundkonton.
- [ ] RED: `test_hog_risk_ar_inte_automatiskt_avslag` tillåter motiverat hanterbart uppdrag med belagd kapacitet trots hög risk. `test_ohanterbart_uppdrag_kraver_atgard_eller_avgransning` stoppar oförändrat fortsatt uppdrag vid dokumenterad otillräcklig kapacitet, men bevarar beslut om begränsning/avböjande som mänskligt beslutsunderlag. Ingen kundåtgärd eller kontakt utförs av provet/programmet.
- [ ] RED: `test_extern_kyc_kraver_lokal_ansvars_och_resultatprovning` avvisar tom leverantörsprövning när profilen anger extern KYC/utkontraktering samt oförklarade saknade/motstridiga resultat. Leverantörens positiva etikett ensam är inget genomförande-/effektbelägg för byrån.
- [ ] RED: `test_stale_cas_bevarar_tidigare_fil`, `test_avbruten_sparning_lamnar_lasbart_register`, `test_belaggsfil_utanfor_privata_roten_avvisas` och `test_senaste_beslut_galler_utan_aterupplivning`.
- [ ] GREEN: implementera rena valideringsfunktioner och privat lagring; `.venv/bin/pytest tester/enhet/test_lokal_analys.py tester/enhet/test_analyslagring.py` passerar.

#### AB3. Lokala frågor i CLI och intag

**Create:** `src/riskanalys/kommandon/analys_kommando.py`, `src/riskanalys/intag/analysvy.py`; nya `tester/enhet/test_analys_kommando.py`, `tester/intag/test_analys.py`. **Modify:** `src/riskanalys/cli.py`, `src/riskanalys/intag/webb.py`, `vyer.py`.

**Consumes/produces:** samma AB2-modeller och funktioner för båda gränssnitten. Föreslaget CLI: `riskanalys analys BYRA` visar frågor/status; `--import FIL` läser strukturerade svar till en ny registerrevision; `--belagg FIL` kopierar ett uttryckligen valt dokument; `--godkann/--underkann --tjanst ID --namn NAMN --roll ROLL --datum DATUM` registrerar lokal attest. Muterande operationer kräver `--revision SUMMA`; webb använder dold summa och befintligt CSRF/origin-skydd. Ingen flagga får både importera och godkänna osedda svar.

- [ ] RED: `test_cli_och_webb_har_samma_analysbrister`, `test_godkannande_kraver_identitet_och_aktuellt_underlag`, `test_fakta_rattas_i_intaget_inte_i_analysen`, `test_analystext_renderas_escapad` samt CSRF-/dubbelpostnings-/gammal-revisionsfall.
- [ ] Visa förifyllda, redigerbara guidesteg med tjänstejämförelse och uttrycklig bekräftelse av visade samma/avviker-val. `test_checklista_fyrtjanstfall_redovisar_64_block_och_12_scenarier` provar antalen ovan, villkorad avgränsning och att valfri följdfråga inte blockerar. Samma belägg ska inte behöva laddas upp igen.
- [ ] Visa en tjänst åt gången, källbeskrivning och kvarstående begränsning intill faktisk tillämpning; visa PT/TF separat. Ogranskat är standard, aldrig förkryssat godkännande. HTML undgår injektion och nya fel är korta svenska meddelanden.
- [ ] Grundfrågorna ska visa de fyra sårbarhetsområdena, samverkan, egna lärdomar och reduktionsprövning uttryckligen; de får inte döljas i ett gemensamt fritextfält. Rutinrader visar föreslagen/beslutad/genomförd och saknad rutin utan förvalt godkännande. Utöka `test_cli_och_webb_har_samma_analysbrister` med samtliga fem kompletteringar.
- [ ] Visa också detaljnivå/delanalyser, betalningsinsyn, uppdragshanterbarhet och leverantörsprövning som uttryckliga frågor. Modellriskunderlaget registreras en gång per analyspaket via samma import-/sparväg och privata beläggsimport; ge inget standardgodkännande från gröna tester. Utöka CLI/webb-pariteten till de sex nya kompletteringarna. Prov med `avboj`/`avsluta` ska registrera beslutsunderlag utan utskick, radering, kundspärr eller ändrat tjänsteutbud.
- [ ] GREEN: `.venv/bin/pytest tester/enhet/test_analys_kommando.py tester/intag/test_analys.py`; API-/AI-leverantörer får inte anropas av spara-/granska-/godkännflödet.

#### AB4. Två leveransdelar: läsordning först, lokal analys därefter

**AB4a, steg 1:** skapa `src/riskanalys/dokument/arb_v5_1.py` och `tester/enhet/test_arb_v5_1.py`. `bygg_arb_v5_1(rb, profil, bedomning, resultat, historik) -> Dokument` bygger vidare på befintlig v5, flyttar risköversikten efter syftet och beräkningstabellerna till B1 med återhänvisningar samt visar AB1:s beskrivningar en gång. Inget lokalt analysregister krävs. Utöka formattyper/serialisering, byggdispatch, rendering och gransknings-/fastställelsedispatch för `D-ARB-tjanst-v5.1`; lägg återbyggnad i `granskning/dokument_v5.py` via samma befintliga mönster som v5. Gammal v5 återbyggs oförändrat. AI-skrivresultatet är fortsatt v5/fem delar. Samtliga befintliga grindar kvarstår; ingen ny rätt till fastställelse av ogranskad metod. Testa `test_v5_1_oversikt_forst_berakning_i_b1`, `test_v5_1_aterbyggnad_stoppar_andrad_cell`, `test_v5_1_saknar_beroende_till_lokal_analys` och historiska v5-summor. Kör riktade prov och därefter fullsvit + regelbasvalidering + diffkontroll. Granska resultatet som egen leverans före steg 2/ev. beställd commit.

**AB4b, steg 2 – v6:**

**Create:** `src/riskanalys/dokument/arb_v6.py`, `tester/enhet/test_arb_v6.py`. **Modify:** `dokument/modeller.py`, `arb.py`, `tabeller.py`, `kallhanvisningar.py`, `intagsunderlag.py`, `rendering.py`, `src/riskanalys/granskning/korning.py`, `src/riskanalys/intag/dokument.py`; samtliga relativa modulnamn här under `src/riskanalys/`.

Datumkompletteringen berör även befintliga `src/riskanalys/drift/historik.py` och `tester/enhet/test_historik.py`. Lägg till `Historik.senaste_uppdatering() -> date | None` utan att ändra historikens serialisering. Ny `utvarderingsavsnitt_v6(historik: Historik) -> Avsnitt` i `arb_v6.py` visar både datumtyperna; den historiska v5-byggvägen bevaras.

**Consumes/produces:** `bygg_arb_v6(rb: Regelbas, profil: Profil, bedomning: Bedomning, resultat: dict[str, Tjanstresultat], historik: Historik, *, analys: Analyspaket | None) -> Dokument`. `bygg_arb(..., *, gransindex=None, analys: Analyspaket | None = None)` får ett nytt keywordargument utan ändring av gamla indata. Inför separat dokumentformatkonstant och versionsstyrd skrivdispatch. Utöka `dokument/delskrivning.py`, `skrivning.py`, `aischema.py`, `promptar/delar.py`, `delvalidering.py` och berörda persistens-/granskningsläsare: v6-skrivresultat har format `D-ARB-tjanst-v6` och exakt delordning `("hot", "sarbarheter")`; v5 behåller femdelarskontraktet. JSON-schemat för ett enskilt AI-svar och tillåtelselistan behöver inte ändras. Format väljs av dokument-/skrivversion, aldrig av lokal analysstatus. Tester i befintliga skriv-/prompt-/skyddsprov samt `test_arb_v6.py` ska visa två grundanrop i v6 med/utan analys, korrekt omförsök, oförändrad v5-verifiering och att borttagna delar aldrig anropas eller krävs av v6-grindarna. Delresultatens typ, prompt-/cacheidentitet och manifest måste följa rätt skrivversion; fem gamla delresultat får inte märkas om till ett nytt tvådelarsresultat.

- [ ] RED: `test_v6_har_bara_tva_ai_delar_och_lokal_slutsats`, `test_v6_ordbudget_med_ai_max` och `test_v6_visar_egen_granskning_i_oversikten` provar tvåanropsflöde, 1 520 AI-maxord och synlig egen-granskningsstatus.
- [ ] RED: `test_v6_oversikt_kommer_fore_metod_och_visar_ogranskad_status`, `test_v6_har_scenariotabell_per_tjanst`, `test_lokal_text_har_egen_proveniens` och `test_berakning_och_kallversioner_finns_kvar_i_b1`.
- [ ] RED: `test_v6_visar_sarbarheternas_betydelse_per_tjanst` kräver de lokala motiveringarna och samverkan i huvudtexten. `test_v6_lankar_risk_till_rutin_utan_falsk_genomforandestatus` kräver scenario/rutin/version, konkret åtgärd, ansvar, utlösare/frekvens, uppföljning och rätt status. Fullständiga belägg får ligga i B1, resonemanget får inte försvinna dit.
- [ ] RED: `test_v6_visar_delanalyser_insyn_och_hanterbarhet` kräver att fakturabokföring och utlandsflöden kan ha skilda motiveringar, att kända insynsluckor syns och att åtgärdsförslag inte beskrivs som genomförda. Endast föräldratjänstens verkliga motorutfall visas som nivåer. `test_v6_visar_modellstatus_utan_kansliga_felakter` kräver aktuell modellbindning/rapportstatus och kända begränsningar men inga kundidentifierande felakter i Word.
- [ ] RED: `test_v6_visar_separat_utvarderings_och_uppdateringsdatum` använder utvärdering `2026-10-01` och uppdatering `2026-10-08`: båda ska synas, nästa genomgång ska vara `2027-10-01`. `test_v6_utan_uppdatering_skapar_inte_falskt_datum` kräver den uttryckliga texten om ingen registrerad separat uppdatering. Prova flera uppdateringar samt en uppdatering efter årsfristen utan ny utvärdering; den får inte återställa aktualiteten. Kör proven röda på befintligt beteende innan datumkompletteringen byggs.
- [ ] Utöka format-/författartyper och tabellvalidator till v6 utan ändrad äldre serialisering. Vid saknad/inaktuell analys visas konkret kompletteringsmarkering; utkastet är läsbart och aldrig implicit godkänt. Bevara stabila avsnitts-ID:n, flytta endast läsordning och visningsnummer.
- [ ] Frys analyskopian och dess summa i varje ny granskningskörning, även "saknas" uttryckligen. Längdräkning, källupplösning och rendering ska hantera lokala scenario-/beläggsreferenser; inga osäkrade filvägar eller brutna interna länkar.
- [ ] GREEN: `.venv/bin/pytest tester/enhet/test_arb_v6.py tester/enhet/test_historik.py tester/enhet/test_rendering.py tester/enhet/test_dokumentmodeller.py tester/enhet/test_kallhanvisningar.py`.

#### AB5. Återbyggnad, sakgranskning och fastställelse

**Create:** `src/riskanalys/granskning/dokument_v6.py`, `tester/enhet/test_analysgrind.py`. **Modify:** `src/riskanalys/granskning/kontroller.py`, `korning.py`; `src/riskanalys/faststallelse/modeller.py`, `sakgranskning.py`, `grindar.py`, `faststall.py`; `src/riskanalys/kommandon/sakgranska_kommando.py`; befintliga `tester/enhet/test_sakgranskning.py`, `test_formathinder.py`, `test_faststall.py`, `test_granskning_korning.py`.

**Consumes/produces:** AB2:s analyspaket. Utöka `Faststallelseunderlag` med `analys: Analyspaket | None = None` och analysbindningssumman; nya värden hämtas ur fryst granskningskopia. `analysfynd_v6(...)` följer v5:s återbyggnadsmodell men tar också det frysta paketet. `Sakgranskning.analysbindning: str | None = None` binder dokumentgodkännandet till hela frysta paketet; värdet härleds av programmet, inte av en CLI-sträng.

- [ ] RED: `test_v6_aterbyggs_fran_fryst_analys` ändrar en cell, en lokal mening och en beläggsreferens var för sig; varje ändring ger blockerande fynd.
- [ ] RED: parametrisera `test_andringsmatris_kraver_nytt_godkannande` efter hela ändringstabellen ovan. Testa också ändrad fil med samma filnamn, nytt underkännande och samma nivå efter nytt motorunderlag.
- [ ] RED: `test_v5_och_v5_1_kan_inte_nyfaststallas_efter_v6`, `test_historiskt_v5_paket_bevarar_summa`, `test_saknad_analys_kan_exporteras_som_utkast` och `test_lokal_attest_ersatter_inte_sakkunniggrind`.
- [ ] Kräv aktuell lokal attest för samtliga erbjudna tjänster. Saknad/okänd analys, referensfel och olöst motsägelse blir blockerande; kan inte accepteras bort som metodavvikelse. Känd kvarstående kontrollbrist med beslutad uppföljning redovisas utan automatisk ny nivå. Befintliga sak-/metod-/juridikgrindar kvarstår.
- [ ] RED: `test_reduktionskonflikt_kan_inte_accepteras_bort` blockerar kvarstående konflikt mellan faktiskt motorutfall och kontrollräckvidd även om gapstatus satts till accepterad kvarstående risk. `test_andrade_rutinbelagg_kraver_ny_attest` ändrar en refererad rutin med samma ID/version men nya bytes. Sådan ändring måste falla på innehållsbindningen. Ett lokalt godkännande ersätter aldrig sakkunnigprövningen av M1.
- [ ] Läs AB7:s modellriskunderlag ur samma frysta paket som analysen och jämför det med aktuell modellidentitet vid lokal attest och fastställelse. RED: `test_sakgodkannande_ersatter_inte_modellriskunderlag` och `test_andrad_modell_eller_vasentligt_fel_stoppar_faststallelse` ska stoppa gammal/saknad validering eller öppet väsentligt modellfel även när dokumentets text är oförändrad. Ompröva också vid ändrat uppdrags-/leverantörsläge; rapportgodkännande får inte passera en olöst hanterbarhetskonflikt.
- [ ] RED: `test_v6_paket_verifieras_utan_levande_modellregister` tar bort det levande analysregistret efter fryst fastställelse i en syntetisk testkopia. Verifieringen ska kontrollera paketets sparade manifest/underlag och fortsätta fungera, även med en senare installerad programversion. Den ska inte jämföra historisk modellidentitet med dagens kod eller påstå reproducerbar beräkning utan bevarad runtime. Ny fastställelse kräver däremot aktuellt underlag.
- [ ] `test_andring_mellan_granskning_och_publicering_stoppar_paket` provar uppdatering av analys eller profil efter första kontrollen. Håll samma privata låsordning (profil före analys) genom avslutande aktualitetskontroll och paketpublicering så normala skrivflöden inte kan publicera en redan inaktuell attest. Läs inte om ett annat analysläge mitt i paketeringen; använd den frysta kopian och avvisa vid avvikelse.
- [ ] GREEN: `.venv/bin/pytest tester/enhet/test_analysgrind.py tester/enhet/test_sakgranskning.py tester/enhet/test_formathinder.py tester/enhet/test_faststall.py tester/enhet/test_granskning_korning.py`.

#### AB6. Integrerat dokumentprov, granskning och status

**Create/Test:** `tester/typfall/test_analys_hela_kedjan.py` med helt syntetiska svar och `Testleverantor`. Komplettera befintliga skyddsprov där begäran byggs. **Modify:** denna plan, designspecen och `docs/STATUS.md` med uppmätt resultat efter implementationen.

- [ ] RED: `test_lokal_analys_paverkar_inte_ai_begaran_eller_anrop` varierar namn, fri text, PT/TF-resonemang, belägg och godkännanden medan tillåtna AI-data hålls identiska. Jämför hela begäran inklusive omförsök och anropsantal. Det nya analysregistret får inte läsas av AI-kedjan.
- [ ] Kör fyra realistiska syntetiska tjänster från profil till analys, granskning och Word-utkast. Lägg in en ändring efter godkännande och bevisa att ny fastställelse stoppas. En positiv fastställelsekedja får använda uttryckligt syntetiska testattester, aldrig ge den verkliga regelbasen sakkunnigstatus.
- [ ] Acceptansfallet ska omfatta kund-/kanal-/geo-/verksamhetssårbarheter, minst en kombination av faktorer, egen rapporteringslärdom, konkret rutinlänk och skilda utvärderings-/uppdateringsdatum. Ett andra fall med oförändrade motorutfall men olöst reduktionskonflikt ska fortfarande ge läsbart UTKAST och stoppad lokal attest/fastställelse. Variation av dessa lokala svar ingår också i AI-begärans identitetsprov.
- [ ] RED: `test_plattformsintakter_via_psp_provas_utan_automatisk_hogrisk` använder prenumerations-/gåvo- eller spelrelaterad plattformsintäkt, PSP och ofullständig information om bakomliggande parter/ändamål. Jämför med en kund med belagt förstått normalt flöde. Båda kräver relevansprövning; plattformsnamnet får inte ensamt ändra motorfaktor, utlösa kundavslag eller bli bevis för penningtvätt/TF. Finanspolisens osäkerhet om omfattningen ska bevaras i källtillämpningen.
- [ ] Integrera delanalys för utlandsflöden, parallella bankengagemang, motstridigt leverantörsresultat samt ett begränsat uppdrag och ett förstärkningsförslag. Positiv testkedja kräver uttryckligt syntetiskt modellriskunderlag. Negativa prov ska ge utkast men stoppa slutlig attest vid saknat aktuellt modellunderlag, öppet väsentligt modellfel eller oförändrat ohanterbart uppdrag. AI-identitetsproven omfattar även dessa privata uppgifter.
- [ ] Mät ord per del, tabeller och sida i faktisk Word-rendering om lokal renderer finns. Utan renderer rapporteras bara uppmätta modellord och tabeller, ingen påstådd sid-/layoutverifiering. Kör även AI-maxfall och visa eventuell budgetavvikelse. Resultat och dokument sparas utanför Git.
- [ ] Läs dokumentet för dubbleringar och källprecision. Begär kodgranskning enligt `requesting-code-review` före eventuell senare commit; verifiera konkreta fynd och rätta dem med RED→GREEN. Medarbetarens läsprov och extern sakkunnig är separata mänskliga kontroller.
- [ ] Slutgate: `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY -u BOLAGSVERKET_CLIENT_ID -u BOLAGSVERKET_CLIENT_SECRET .venv/bin/pytest`, `.venv/bin/riskanalys regelbas validera` och `git diff --check`. Rapportera faktisk output, hoppade prov och kvarstående begränsningar; ingen automatisk commit/push.

#### AB7. Versionsbunden modellrisk och återkommande uppföljning

**Körs i steg 2 före AB2–AB6, efter färdiggranskat steg 1.** Detta preciserar befintlig spec §7.8 inom samma plan; ingen parallell modellriskplan eller fullständig generator för M6-rutiner byggs.

**Create:** `src/riskanalys/drift/modellrisk.py`, `modellidentitet.py`, `modellrapport.py` samt `tester/enhet/test_modellrisk.py`. De tre modulerna delar ansvar för lokalt underlag/grind, smal modellidentitet respektive projektets rapportpaket; det publika kontraktet exponeras via `drift/modellrisk.py`. **Modify vid integration:** AB2:s planerade `analys/modeller.py`, `lagring.py`, `provning.py`, AB3:s gränssnitt samt AB5:s grind-/paketfiler. Använd befintliga `lagring/kontrollsumma.py`, `lagring/manifest.py` och `drift/historik.py` för summor, frysta underlag och datumberäkning.

**Typer i `drift/modellrisk.py`:** frysta modeller med `extra="forbid"`:

- `Modellbelagg(fil: str, kontrollsumma: str)`: registrerad privat dokumentkopia under byråns `analys/belagg/`. Ingen fri URL/filrouter; filens faktiska hash kontrolleras. AB2:s import kan leverera kopian utan att AB7 importerar analysmodulen.
- `Modellfel(id: str, datum: date, beskrivning: str, allvar: Literal["vasentligt", "ovrigt"], status: Literal["oppet", "atgardat"], atgard_och_omprovning: str, belagg: tuple[Modellbelagg, ...])`: lokal uppföljning av exempelvis missade scenarier, felaktiga nivåer/reduktioner och datakvalitet. Ett åtgärdat väsentligt fel kräver belägg för rättning och omprövning, inte bara ändrad etikett. Normal rapportersättning och strukturerad analysimport får inte tyst radera tidigare registrerade modellfel; felaktigt registrerade poster avslutas uttryckligen med förklaring och erforderligt belägg.
- `Modellriskunderlag(modellansvarig: str, modellbindning: str, rutin: Modellbelagg, valideringsrapport: Modellbelagg, utvarderad: date, nasta_genomgang: date, feluppfoljning: str, fel: tuple[Modellfel, ...], godkand: bool, beslutad_av: str, beslutsdatum: date)`: ansvar och rapport ska vara verkliga mänskliga uppgifter vid riktig användning. Utkast kan sakna underlaget; inga standardnamn eller autoattester. Projektets rapport beskriver fallurval, utfall, avvikelser och begränsningar; byråns feluppföljning beskriver hur verksamheten hittar/bedömer nya fel och när nästa kontroll sker.

**Consumes/produces:** `modellbindning(rb: Regelbas) -> str` och `modellriskhinder(byramapp: Path, rb: Regelbas, underlag: Modellriskunderlag | None, datum: date) -> tuple[str, ...]`. Identiteten omfattar faktisk riskberäkning, dess lokala beroenden och `rb.kontrollsumma`, inte enbart versionsetikett/Git-HEAD. AB7 definierar en granskad filförteckning för motor och beslutspåverkande hjälpfunktioner, med utgångspunkt i `bedomning/motor.py`, `erfarenheter.py`, `omfattning.py`, `sanktioner.py`, `kundmodell/`, modelltyperna samt använda profilhärledningar och regelverkets urval/villkor/tillsyn. Följ även funktionslokala importer; en beräkningsändring får inte gömmas i en utelämnad hjälpfil. Manifestet och faktisk filtext i stabil relativ ordning binds; saknad modellfil är ett hinder. Dokumentbyggare, UI och AI-klient ingår inte.

Python och installerade versioner av Pydantic, PyYAML, python-docx och anthropic sparas som **miljöuppgift** med release-/körningsmanifestet. Enbart versionsbyte bryter inte modellbindningen. Det betyder inte att runtime aldrig kan påverka beräkningar: projektets kompatibilitetsprov och verkliga feluppföljning fångar avvikande beteende; ett upptäckt väsentligt fel stoppar fortsatt fastställelse. Övriga innehålls-/dokumentbindningar gäller som tidigare.

**Projektets leverans:** versionsbunden valideringsrapport med modellhash, fallurval/facit, faktiska utfall, avvikelser, begränsningar och sakkunnigs uttryckliga M1-beslut. Rapport och modellfilförteckning levereras med releasen (manifestet `modellfiler.json` och rapporten `modellvalidering.pdf` i versionspaketets underlagsdel); byrån importerar en privat fryst kopia med faktisk hash. Vid en ren dokument-/UI-/biblioteksrelease kan rapporten hänvisa till den tidigare modellvalideringen och redovisa kompatibilitetsproven, utan ny full metodvalidering. Byte av modellhash kräver rapport för den nya modellen. Teknisk rapport före sakkunnigs prövning märks ogranskad och ger ingen attest.

**Byråns del:** granska om rapportens tillämpningsområde och begränsningar passar verksamheten, dokumentera godkännande/åtgärd, egen rutin och återkommande uppföljning av verkliga fel. Byrån ska inte behöva konstruera modellens facit/fallurval eller skriva projektets valideringsrapport. `Modellriskunderlag` sparar rapportkopia och detta lokala beslut; releasemanifestets modellhash och rapporthash ska matcha den aktuella modellen respektive de faktiska rapportbytesen. En fritt angiven lokal modellsträng räcker inte som rapportkoppling.

**Levererat rapportkontrakt:** frysta `Modellfil(fil, kontrollsumma)` och `Modellfilmanifest(schema_version=1, modellbindning, regelbas_kontrollsumma, filer)` beskriver den exakta sorterade lokala modellfilslutningen. `Modellvalidering` innehåller `schema_version=1`, modellbindning, `modellfiler_kontrollsumma`, `rapportfil="modellvalidering.pdf"`, `rapport_kontrollsumma`, rapportversion/datum, tillämpningsområde, fall/facit, faktiska utfall, avvikelser, begränsningar, sanningsenlig uppgift om verkliga driftobservationer, `m1_beslut: Literal["ej_provat", "godkant", "andring_kravs"]` och befintlig `Sakkunnig`. Godkännande kräver explicit godkänt M1 och giltig attest mot rapportbeskrivningens innehållssumma, inklusive PDF-hash och begränsningar, inte ett nytt parallellt booleskt expertgodkännande. `Modellriskunderlag` får `projektrapport: Modellbelagg` och `modellfiler: Modellbelagg` utöver PDF-kopian. Byråns beslut binder exakt dessa kopior. Detta lagrar det redan krävda sambandet projekt–modell–rapport, inte en ny expertroll.

Publika tillägg: `modellfilmanifest(rb) -> Modellfilmanifest`, `modellmiljo() -> Modellmiljo`, `valideringens_innehallssumma(rapport) -> str`, `exportera_modellvalidering(malmapp: Path, rb: Regelbas, rapport: Modellvalidering, pdf: Path) -> Path`, `las_modellvalidering(mapp: Path) -> Modellvalidering`. Exporten tar en befintlig PDF och skriver fast JSON, filmanifest, PDF samt befintligt paketmanifest i en ny målmapp. Den genererar inte PDF eller sakkunnigattest. `Modellmiljo` lagrar Python och de fyra nämnda biblioteksuppgifterna separat. Samma modellrapport/attest ska kunna återanvändas oförändrad i en ren presentations-/miljörelease; ändra inte dess rapportversion/datum enbart för att applikationen fått ny version. Teknisk rapport utan verklig sakkunnig är `ej_granskad` och M1 `ej_provat`.

Modellfilernas importer kontrolleras även inuti funktioner; en ny lokal hjälpfunktion får inte hamna utanför identiteten. Icke-rotdelpaketens init-filer ingår. Rotens init-fil tillåts som metadata endast med docstring och enkel literal versionsdeklaration; annat körbart beteende stoppas tills det granskats. Dynamiska importer i modellslutningen är inte en genväg runt inventariet.

Årlig modellgenomgång är projektets basnivå enligt §7.8, anpassad tätare vid behov; påstå inte att just tolvmånadersintervallet eller en viss befattningstitel är ordagrant föreskriven i PTL 6 kap. 1 §. `nasta_genomgang` ska ligga efter `utvarderad` och senast tolv månader därefter. En modelländring eller ett väsentligt nytt fel kräver omprövning före fortsatt slutligt godkännande. Ett nytt bevarat paket ska innehålla aktuellt underlag; historiska paket verifieras fortsatt mot sin frysta version.

Byrån ansvarar för rutinen och den löpande uppföljningen. Saknas verkliga driftobservationer ska det sägas i rapporten; inga verkliga observationer får konstrueras ur syntetiska tester eller noll registrerade fel. Programmet kan kontrollera bindning/fullständighet/öppna fel, inte att en människa faktiskt gjort en fackmässigt tillräcklig utvärdering. Modellriskunderlaget ersätter inte befintliga sakkunnigattester för M1–M4.

- [ ] RED: `test_modellrisk_kraver_aktuell_rapport_och_feluppfoljning` avvisar saknad ansvarig/rutin/rapport, `godkand=False` eller felaktig bindning, passerat uppföljningsdatum och öppet väsentligt modellfel. Väsentligt fel med status åtgärdat men utan omprövningsbelägg får inte passera.
- [ ] RED: `test_modellbindning_andras_med_motor_regler_och_hjalpfil` kräver ny bindning vid beräknings-/regeländring inklusive lokal hjälpfil. `test_miljo_och_presentationsbyte_bryter_inte_modellbindning` varierar Python/bibliotek, UI, Word och AI-klient utan ändrad modell: samma bindning, uppdaterad miljöuppgift. Samma modell i annan katalog ger samma identitet. `test_andrad_valideringsrapport_kraver_nytt_lokalt_beslut` ändrar rapportbytes med samma filnamn: modellhashen består, men byråns godkännande av just rapportkopian blir inaktuellt. Befintliga slutliga paket förblir orörda.
- [ ] RED: `test_projektrapport_och_lokalt_anvandningsbeslut_halls_isar` kräver rapport för rätt modell samt byråns uttryckliga godkännande; lokal notering eller grönt test ersätter inte saknad sakkunnigprövning/M1-beslut.
- [ ] RED: `test_syntetisk_provning_blir_inte_verkliga_felutfall` säkerställer att ingen statistik/attest skapas av programmet ur gröna testresultat eller tomt felregister. Importerad mänsklig rapport och avgränsning ska bevaras oförändrade; provet är inte ett maskinellt sanningsprov av fri text.
- [ ] GREEN: `.venv/bin/pytest tester/enhet/test_modellrisk.py`. Efter integration körs även AB2–AB6:s prov och slutgaten. Godkänt tekniskt prov uppdaterar aldrig sakkunnigstatus eller byråns riktiga modellriskregister.

### Metodansvar och planens egen kontroll

Användaren behöver utse en namngiven sakkunnig, byråns beslutsansvariga och modellansvarig samt tid för M1–M4 och modellvalideringen. M1 tas upp och avgörs av sakkunnig vid samma metodgranskning, med dokumenterat beslut/facit och kvarstående begränsningar. Ingen metodverifiering före detta beslut. En eventuell numerisk rättning beställs och provas separat. Roller kan kombineras där det är lämpligt och tillåtet; skapa inte skenbart oberoende genom olika etiketter för samma granskning. Identitet, kompetens och beslut dokumenteras privat enligt befintligt attestflöde; tills dess står **ej utsedd/ej granskad**. Implementationen kan byggas och provas syntetiskt under tiden. Den får inte presenteras som expertgranskad metod eller färdigt produktionsunderlag.

Planen har kontrollerats mot de befintliga modellerna, v5-återbyggnaden, profilens CAS-lagring, sakgranskningen och fastställelsegrinden. Två identifierade fallgropar är uttryckligen hanterade: skrivresultatets format skiljs från dokumentformatet, och analysattest skapas före dokumentsakgranskning så att hashbindningen inte blir cirkulär. Uppgifterna täcker A, B, samtliga ändringsfall och de fem felklasserna. Inga nya programprov har körts för denna planrevision; kod och regelbas är oförändrade.

Denna revision har dessutom kontrollerats för de sex omfattningsbesluten: förifyllnad/delning och räknat fyrtjänstfall, endast två AI-delar i v6, oberoende steg 1, synlig egen granskning, M1 vid metodverifieringen samt smal modellbindning och projektlevererad rapport. De tidigare källkraven består. Endast plan/spec/STATUS ändras; inga nya programprov, commits eller API-anrop i plansteget.


### A+B genomförandelogg med subagenter, 2026-10-15

Arbetet sker i det befintliga repot på `codex/m0-m1`, med start vid `3c6d405`. Inga nya commits eller push. Tidigare dokumentationsarbete och index är bevarade. Uppgiftsvisa rapporter, RED/GREEN-loggar, granskningar och filhashar ligger privat i `~/.local/share/riskanalys/provkorningar/ab-implementation-20261015-212722/`. Checklistan ovan är det ursprungliga acceptanskontraktet; flera testnamn har vid genomförandet delats upp eller fått mer precisa namn. Nedanstående filkopplingar, inte en påstådd körning av alla ursprungliga namn, redovisar den utförda prövningen.

| Leverans | Genomförande och verifiering |
|---|---|
| AB1 / AB4a | Källbunden kontrollräckvidd och v5.1-läsordning, separat granskade. Steg 1: 1 677 passerade, ett bortvalt livetest, 730,04 s; exakt testade filer sparade separat. Regelbas 1.4.0 i kontrollpunkten. |
| AB1 i steg 2 | Typad `beskrivningsstatus` skiljer beskrivet stöd från okänd räckvidd. Regelbas 1.5.0, 99 riktade prov och separat återgranskning. `tester/regelkontrakt/test_kontrollrackvidd.py`. Inga numeriska ändringar. |
| AB7 | Smal modellidentitet, verifierat rapportpaket och lokal modellriskprövning. Tre funna installations-/historik-/importfel rättade och återgranskade; 92 riktade prov. `tester/enhet/test_modellrisk.py`. Teknisk rapportartefakt inväntar slutresultat; ingen riktig expertattest skapas. |
| AB2 | Typade privata analyser, förifyllnad, delning, blockbekräftelser, belägg, CAS och låsta beslut. Två granskningsfynd rättade och återgranskade; 130 riktade prov tillsammans med AB7. `tester/enhet/test_lokal_analys.py`, `test_analyslagring.py`. |
| AB3 | Typade webbformulär och CLI över samma tillämpningstjänst. Belägg återanvänds utan ny uppladdning; import är ogranskat utkast. Separat granskning: 67 färska prov, inklusive faktisk komplett formulär-POST för alla 16 block. `tester/intag/test_analys.py` samt `tester/enhet/test_analys{guide,formular,_kommando}.py`. |
| AB4b | Aktuell v6 med två AI-delar, lokalt författarskap, scenarier/kontroller/rutiner, faktisk M1-status och fryst återbyggnad. Separat slutgranskning godkänner 37 filer; 99 dokumentprov och 157 skriv-/dataskyddsprov har körts, delvis överlappande. `tester/enhet/test_arb_v6.py`, `test_lokalt_dokument_v6.py` och `tester/intag/test_skrivning_v6.py`. |
| AB5 | Fryst analys/belägg/rapport, separat dokumentattest, låst atomisk publicering och historisk paketverifiering. 135 riktade och elva M2-prov. Granskningen fann att framtida lokal attest kunde följas av tidigare granskning/fastställelse; rättat RED→GREEN, 143 riktade prov passerar. Återgranskning godkänner med åtta färska datumprov och fem matchande filhashar. `tester/enhet/test_analysgrind.py`, `tester/m2/test_m2_kedja.py`. |
| AB6 | Integrerad syntetisk positiv kedja i signerad testkopia samt negativa aktualitets-, modellrisk-, kapacitets-, leverantörs-, PSP- och reduktionsprov. Riktade helkedjeprov och Word-layoutgranskning pågår; fullsvit och samlad slutgranskning kvarstår. `tester/typfall/test_analys_hela_kedjan.py`. |

**Hittills uppmätt längd:** maxprovet ger 4 892 huvudord + 12 580 B1-ord; det delade utlandsfallet ger 5 628 + 12 639. Båda har 1 520 ursprungliga AI-ord i åtta anrop. Basfallet klarar huvudmålet 3 500–5 000 men överskrider riktbudgeten 4 700 med 192; variationen överskrider huvudmålet. Ingen text kapas. Det första separata läsprovet använder 806 manuellt förberedda tjänsteanpassade skrivord, inte ett riktigt AI-anrop. Slutlig mätning och sidor rapporteras efter konsekvent profil- och layoutkontroll. B1 är fortsatt lång; målet om en kort totalrapport är inte uppnått.

**Kvarstående mänskligt arbete:** verklig sakkunnig metodvalidering och M1–M4, namngiven modellansvarig/byråbeslutsansvarig samt ett verkligt medarbetarläsprov. Alla faktiska sakkunnigposter är fortfarande `ej_granskad`. Ett syntetiskt godkänt paket visar programkedjan, inte att den riktiga modellen eller en verklig byrå är godkänd.

### Slutförande och verifiering, 2026-10-16–17

Claude tog över efter att Codex nått sin användningsgräns och slutförde med subagenter; Codex granskade två gånger. Tidigare uppmätta längder ovan gäller läget före dessa ändringar.

| Ändring | Innehåll och verifiering |
|---|---|
| Äldre utkast | V6-byggaren avvisar mall- och v5-utkast med tydligt `RiskanalysFel` i stället för `AttributeError`, även via `granska` och CLI. Död kod i `arb.py` borttagen; granskningen tar analyslåset bara när regelbasen har `omfattning`. |
| Regeltester | 81 regelkontraktsprov körs mot v6 (`tester/fixturer/arb_kedja.py`), plus 12 prov för historisk v5-verifiering. |
| Låsta stycken | `dokument/lasta_v6.py` och `granskning/lasta_v6.py`: egen rapportering och geografi i varje tjänst, B-09, B-10 och B-15 (spec 8.4.6). AI-delarna prövas lokalt mot exakt dessa stycken efter alla anrop; begäran, omförsök och promptsummor är oförändrade. |
| Omfattning och D-ARB.9 | `uppfoljning.py` och `dokument/foljder_v6.py`: motivering efter storlek och art i D-ARB.2; D-ARB.9 ur den godkända lokala analysen med [VERIFIERA] där område, rutinåtgärd eller godkännande saknas. |
| Datum | `analys/provning.py`: stöd daterat efter ett analysgodkännande avvisas och tidigare sparade sådana godkännanden stoppas; uppföljningsfrister får ligga i framtiden. Ett underkännande får dokumentera felet. |
| Belägg | `analys/lagring.py`: symlänkade mappar i den valda källans sökväg tillåts; själva filen får inte vara symlänk. Den privata byråmappen är oförändrat strikt. |
| Layout | `rendering.py`, endast v6: separerade länkar, `cantSplit` för korta rader, upprepad rubrikrad. B1:s delrubriker är `Underrubrik` i modellen (`arb_v6.py`) och omfattas av sakgranskning och återbyggnad. |
| Längd | Användarens beslut 2026-10-17: realistiskt läsprov 3 500–5 000 huvudord (riktbudget 4 700), AI-maxprov med synlig längdvarning och bevarad analys. Upprepade ID-listor visas som intervall med alla referenser kvar. |

**Slutverifiering:** `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY -u BOLAGSVERKET_CLIENT_ID -u BOLAGSVERKET_CLIENT_SECRET .venv/bin/pytest -q -p no:cacheprovider` gav **2 107 passerade, ett bortvalt livetest, 1 147,52 s**, exitkod 0. Regelbas 1.5.0 validerar (107 krav, 11 tjänster, 201/201 paragrafer i tre länspaket, ej_granskad); `git diff --check` passerar.

**Uppmätt längd (LibreOffice-PDF):** demo 4 510 huvudord, 15 huvudsidor; AI-max 5 239 huvudord med längdvarning, 16 huvudsidor; utlandsvariant med AI-max 5 943 huvudord, 19 huvudsidor. B1 är cirka 12 700 ord och 42 sidor. Demot klarar ordmålet men inte det redaktionella sidmålet 9–12; sidantal i Microsoft Word är inte verifierat.

**Teknisk modellrapport:** ogranskat paket `modellrapport-ogranskad-v4` med PDF, typad rapportbeskrivning och modellinventarium (23 filer, modellbindning `sha256:938ab629…`), exporterat och verifierat med programmets egen funktion. Evidens och skript: `~/.local/share/riskanalys/provkorningar/ab-modellrapport-20261017/`. Status `ej_granskad`, M1 `ej_provat`.

**Kvarstår:** verklig sakkunnig metodvalidering och M1–M4, namngiven modellansvarig och byråbeslutsansvarig, medarbetarläsprov och kontroll i Microsoft Word. Ingen commit eller push har gjorts.
