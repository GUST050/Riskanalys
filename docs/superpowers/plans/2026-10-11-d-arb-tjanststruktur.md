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
