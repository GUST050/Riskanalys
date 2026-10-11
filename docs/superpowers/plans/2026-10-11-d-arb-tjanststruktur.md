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
