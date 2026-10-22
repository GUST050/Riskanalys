# Kravstöd och tjänsteexponering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Använd `superpowers:executing-plans` vid ett separat beställt genomförande, uppgift för uppgift. Checklistorna avser framtida arbete; denna beställning gäller planen.

**Revision:** 3, den 21 oktober 2026. Revision 2:s granskningspunkter är åtgärdade. Denna revision förtydligar Python-miljö, erbjudandeövergångar/rättelser, historikens bindning och urvalet av gemensamma faktordefinitioner efter den uppföljande granskningen i chatten. Kodbasen är fortsatt `288fa66` och den ursprungliga granskningen finns i `8915f0d`; endast dokument ändras.

**Goal:** Verifiera stödet för de 36 kravpunkterna och införa belagda luckrättningar så att tjänstens underlag kan följas genom hot, sårbarheter och riskfaktorer till motiverad tjänsterisk.

**Architecture:** Behåll scenariomotorn, den lokala analysen, befintlig evidenshantering och rapport V8. Komplettera profilen med lokala tjänsteplaner och deklarerade kombinationsgrupper. Ändra riskberäkningen först när D3/D5/D6/D8/D9 anger exakt tillämpning och facit; bygg ingen parallell bedömningsmotor.

**Tech Stack:** Python 3.12 för godkända verifieringskörningar, Pydantic, YAML, pytest och python-docx enligt befintligt projekt. Detta preciserar testmiljön, inte ett nytt generellt stöd för andra Python-versioner.

**Spec:** [Kravstöd och tjänsteexponering](../specs/2026-10-21-kravstod-och-tjansteexponering-design.md). Läs även originalspecen `docs/superpowers/specs/2026-10-08-riskanalys-design.md` och repoets `AGENTS.md` vid genomförandet.

**Kodbas:** `GUST050/Riskanalys`, `feat/steg-1-3`, kod-SHA `288fa6650ea400fda04cdcef965f8ac17adc3575`. Granskningen finns i det efterföljande dokumentationscommitet `8915f0d154416bcbd482b2b926a6523e7f9405d8`, verifierad fjärr-HEAD vid denna revision. Kodbasen innehåller 13 commits efter `fc82b6754537cd3de0eee74dcb2a32b82c1a39a9`; granskningen är det fjortonde. Sökvägar till produktkod nedan avser detta repo. Planen ligger i dokumentarbetsytan, som inte innehåller produktkoden.

**Granskning:** [Granskningsunderlag för 288fa66](https://github.com/GUST050/Riskanalys/blob/8915f0d154416bcbd482b2b926a6523e7f9405d8/docs/superpowers/reviews/2026-10-21-granskning-kravstodsplan.md).

## Global Constraints

- AI skriver text men fattar inga riskbeslut.
- Inga personuppgifter, privata råsvar eller kontrollutfall till AI; återkoppling vid omförsök följer samma gräns.
- Byrådata ligger utanför Git; tester använder syntetiska uppgifter.
- Ändringar av metod, modell och bindningsalgoritm identifieras uttryckligen. Gamla godkännanden får inte tyst få ny innebörd.
- Låsordning, revisionsskydd, kontrollsummor och atomisk export bevaras.
- Sakkunnigstatus ändras bara efter verklig granskning. Teknisk verifiering är en separat status.
- Ingen hård ordgräns, automatisk radering av historik eller generell omskrivning av tidigare format.
- Planposter och kombinationsgrupper stannar lokalt; ingen utökning av AI-tillåtelselistan ingår.
- Inget obligatoriskt kunduppdragsregister, inget analysschema 2, ingen `ProvadBedomning`, ingen V9 och ingen ny AI-blockindelning ingår.
- Uppgifterna börjar med relevanta fallerande tester före produktkod. Dokumentinventering verifieras med täckning och källhänvisningar, inte meningslösa tester av Markdown-text.
- Alla test- och mätkommandon använder en verifierad Python 3.12-miljö i genomförandets checkout. Sätt `RISKANALYS_VENV` till dess absoluta katalog; namnet behöver inte vara `.venv`. Använd befintlig `.venv312` om dess interpreter och projektinstallation stämmer, annars skapa en separat `.venv312` med `python3.12`. Bygg inte om en använd `.venv` med Python 3.14. Kontrollera `"$RISKANALYS_VENV/bin/python" -c 'import sys; assert sys.version_info[:2] == (3, 12); print(sys.executable); print(sys.version)'`. Annan version räknas inte som verifiering av denna plan.
- Kravmatrisen får begränsa, dela eller skjuta upp uppgift 3a–5 och 3b. Varje sådan avgränsning kopplas till en kravrad och ett verifierat befintligt stöd.

## Review Focus

1. En planerad tjänst med noll befintliga kunder kan få en sakligt dokumenterad förändringsutvärdering utan att motorbedömning krävs. Om 3b införs märks dess begränsning tydligt; noll kunder betyder inte låg risk. Ägs av uppgift 3a, 3b och 7.
2. Samma marginaltal med faktiskt gemensamma respektive separata egenskaper får olika underlagsspår; okänt överlapp får inte bli en belagd kombination. Ägs av uppgift 2, 4 och 6.
3. Uppdrag kontra kunder, inaktuella uppgifter och olika perioder får inte blandas till en andel. Överlappande grupper får inte summeras till en unik total. Ägs av uppgift 4.
4. Ändrade privata grupper, planeringsuppgifter eller belägg ska upphäva berörd sakprövning men aldrig ändra AI-begäran direkt eller via omförsök. Ägs av uppgift 3a, 4, 5, eventuell 3b och 7.
5. Historisk läsning och alla 13 återanvända commits ska bestå. Förklaringar placeras gemensamt med lokal tillämpning per tjänst; fulla motorberäkningar förblir i B1. Ny metod eller ändrad plan återanvänder inte gamla godkännanden. Ägs av uppgift 0, 3a, 5, 6 och 7.

---

## Ordning och leveransgränser

**Huvudspår: 0 → 1 → 3a → 4 → 5 → 3b (frivillig senare etapp) → 6 → 7.** Uppgift 2 kompletterar det redan befintliga beslutsformuläret efter 1, samtidigt med övrigt förberedande arbete, och måste vara färdig för de beslut som ska införas i 6. Den blockerar inte 3a.

3a är den första funktionsleveransen: planpost, saklig utvärdering och bindning inför förändring. 3b krävs inte för att leverera 3a, 4 eller 5 och får skjutas upp utan att blockera oberoende metodändringar i 6 eller slutprov av levererad omfattning. Inget i denna plan startar 3b automatiskt.

Uppgift 6 har en verklig beslutsgräns. Om beslut saknas levereras den färdiga underlagsfunktionen som sådan; den får inte marknadsföras som en färdigvaliderad ny riskmetod. Den beslutade delen av uppgift 6 ska preciseras till körbara tester innan den implementeras. Inga okända riskvärden fylls i av implementeraren.

Den här planen ersätter den äldre ändringsplanens återstående planering inom detta område. De gamla stegen 1–3 och de tio senare committerna återanvänds i uppgift 0. Uppgift 1 avgör återstående omfattning: färdiga delar i 3a–5 återanvänds, mindre luckor ger mindre uppgifter, och obehövliga utbyggnader utgår med dokumenterat skäl. Ytterligare luckor får egna avgränsade tilläggsuppgifter.

### Uppgift 0 Kontrollera arbetsbas och återanvänd redan gjorda rättningar

**Läs:** `AGENTS.md`, `docs/STATUS.md`, aktuell originalspec och tidigare planer. Jämför de två angivna grenarna. Relevant befintlig kod finns i `src/riskanalys/analys/{modeller,provning,lagring}.py` och `src/riskanalys/dokument/{nivamotivering_v8,atgardsgrupper}.py`.

**Leverans:** `docs/superpowers/reviews/2026-10-21-kravstod-baslinje.md` i produktrepot, med SHA, arbetsstatus, faktisk testkörning och återanvända commits. Inga andra chattars arbetskopior används.

- [ ] Läs aktuell gren/HEAD och lokal diff. Välj befintlig lämplig checkout eller skapa isolering vid genomförandet enligt worktree-skillen; använd prefix `codex/` om en ny gren behövs.
- [ ] Kontrollera miljön i just denna checkout. Enligt den uppföljande granskningen kör befintliga `.venv` Python 3.14, medan en `.venv312` finns i granskarens arbetskopia. Detta är en rapporterad lokal observation, inte en här utförd miljökontroll. Välj en giltig lokal `.venv312` eller skapa den med `python3.12 -m venv .venv312` om katalogen saknas. Sätt `RISKANALYS_VENV` till den absoluta sökvägen, kontrollera 3.12 enligt ovan och installera projektet där med `"$RISKANALYS_VENV/bin/python" -m pip install -e '.[dev]'` om det behövs. En annan checkouts editable-installation eller en redan befintlig felaktig miljö återanvänds inte tyst. Dokumentera valt körbart program och version innan tester räknas.
- [ ] Verifiera att kodbasen innehåller alla 13 commits: `25be85a`, `d47dadd`, `688629f`, `5c8e96f`, `4827095`, `4f69288`, `74c0b12`, `23932aa`, `2014557`, `8fd6116`, `b50ca76`, `cda6f80`, `288fa66`. Dokumentera `8915f0d` separat som granskning. Utgå från denna historik i stället för att cherry-picka äldre delar eller återskapa färdiga rättningar. Nyare ändringar inventeras innan integrationsbasen ändras.
- [ ] Kör `"$RISKANALYS_VENV/bin/python" -m pytest tester/enhet/test_analyslagring.py tester/enhet/test_reduktionssparr_scenario.py tester/enhet/test_atgardsgrupper.py tester/typfall/test_analys_hela_kedjan.py -q` och `"$RISKANALYS_VENV/bin/riskanalys" regelbas validera` i produktrepot. Godkänt är exit 0; körda antal/fel dokumenteras utan att gamla körningar tillskrivs denna bas.
- [ ] Dokumentera befintligt stöd för sakbindning, reduktionsstöd och åtgärder samt beslutsformulärets åtta par, rapportmätning, gemensamt faktaunderlag, deterministisk källnot och beräkningstabeller i B1. Kör även `tester/enhet/test_rendering_v8.py`, `tester/enhet/test_arb_v8.py` och `tester/intag/test_rapportflode_v8.py`. Ange konkret fel om återanvändningsproven inte passerar.

**Klart när:** Nästa uppgift har en entydig integrationsbas och redan implementerat arbete inte dubbelbeställs. Dokumentera baslinjen i en separat dokumentationscommit efter kontroll.

### Uppgift 1 Verifiera samtliga 36 kravpunkter mot befintliga funktioner

**Läs:** `regelbas/krav/allman_riskbedomning.yaml`, `regelbas/krav/foreskrifter.yaml`, `regelbas/lydelser.yaml`, `regelbas/kallor.yaml`, tjänste- och sårbarhetskatalogerna, `src/riskanalys/analys/provning.py`, `src/riskanalys/drift/historik.py` och granskning/fastställelse. Återanvänd befintlig kravkarta i regelbasen i stället för en parallell produktkatalog.

**Skapa:** `docs/superpowers/reviews/2026-10-21-kravmatris-36.md`. Detta är ett granskningsprotokoll, inte en ny körbar regelbas.

**Kontrakt:** Exakt en huvudrad för varje nummer 1–36 med kravtext, grundtyp, tillämplighet, befintlig krav-ID, status (`finns`, `delvis`, `saknas`), kodfunktion, namngivet test/körresultat, rapportplacering och kvarstående lucka. Ej körd verifiering anges separat; den gör inte en kodobservation till ett bevis på full funktion.

- [ ] Läs användarens båda källdokument och stäm av rättslig grund mot tillämpligt daterat regelpaket. Kontrollera särskilt utvärdering före förändring för samtliga stödda län.
- [ ] Spåra varje rad från intag/regel till lokal analys, granskningsvillkor och rapport. Ett obligatoriskt formulärfält ensamt ger inte status `finns` för ett analyskrav.
- [ ] Kör de befintliga tester som faktiskt stöder raden. Referera till samma test på flera rader när det täcker dem; skapa inte 36 spegeltester.
- [ ] Kontrollera att täckningen är exakt 1–36 utan luckor eller dubbla huvudrader. Skilj tekniskt stöd från byråns faktiska informations-, utbildnings- och åtgärdsarbete.
- [ ] Prioritera bara belagda luckor. Ange per uppgift 3a, 4, 5 och 3b: genomför, minska, återanvänd befintligt eller skjut upp, med berörda kravnummer och bevis. Uppgift 6 kräver dessutom metodbeslut. Spara matrisen och uppdatera `docs/STATUS.md`.

**Klart när:** Kravkartan visar vad som redan fungerar och vilket konkret bevis som återstår, utan att sexdelningen behandlas som en ombyggnadsbeställning.

### Uppgift 2 Frys två genomgående fall och precisera metodbesluten

**Återanvänd:** `docs/research/13-scenariomotor-katalog.md`, `docs/superpowers/reviews/2026-10-21-beslutsunderlag-steg0.md`, `docs/superpowers/reviews/2026-10-21-beslutsformular-jamforelsepar.md`, `tester/fixturer/rapportlasprov.py`, `tester/fixturer/faktorer.py`, `tester/typfall/test_rapportlasprov.py` och de befintliga verktygen för enskilda faktorer och metodalternativ.

**Komplettera:** `tester/fixturer/kravstod.py` med endast de saknade planerings- och gruppfallen. Skapa `tester/typfall/test_kravstod_hela_kedjan.py` för acceptansfallen i uppgift 7, inte en parallell kontrastkatalog.

**Leverans:** Komplettera det befintliga beslutsformulärets åtta par med par 9 (planerad förändring kontra befintlig tjänst) och par 10 (belagd samtidig respektive åtskild exponering, med okänt överlapp som tredje variant). Återanvänd svarsmall, status och precisering per riskmått. Skapa inget nytt beslutsprotokoll. Fall-ID:n `planerad_tjanst` och gruppvarianterna återanvänds i tester utan kundidentiteter.

- [ ] Spara nuvarande scenarioresultat, faktorer, kontrollkopplingar och sammanfattningar för de befintliga H7.1-kontrasterna. Kör `"$RISKANALYS_VENV/bin/python" -m pytest tester/typfall/test_rapportlasprov.py tester/regelkontrakt/test_scenariomotor.py -q`.
- [ ] Beskriv syntetiskt planfall med erbjudande `false` och avsedda arbetsmoment, insyn, leverans och geografi. Dokumentera nuvarande begränsning innan stödet införs.
- [ ] Beskriv en tjänst med 100 uppdrag: 8 med båda egenskaperna; jämför med två disjunkta grupper om 8 med var sin egenskap och med okänt överlapp. Håll marginaltal, tjänst och period lika.
- [ ] Lägg till kontrollkontrasten ett respektive två maxscenarier samt kontroll av bara ett. Bevara nuvarande numeriska utfall även om etiketten är densamma.
- [ ] Låt D3 ange population/tjänsteavgränsning/okänt; D4 tillåtet överlappsbevis; D5 max och liten väsentlig grupp; D6 TF-kedja/konsekvens; D8 effekt/täckning; D9 korrelation/summering/tak. D1/D2/D7 behandlas om relevanskopplingar påverkas.
- [ ] För varje beslutat ändringsfall: ange exakt förväntad faktoraktivering, scenario- och tjänstenivå, eller motiverat oförändrat resultat. Ange verklig ansvarig, granskare, källversion och datum. Förslag och hypotetiska körningar är inte beslut.

**Klart när:** Tekniska föreutfall är frysta och varje numerisk ändring har ett specificerat beslutsunderlag i samma formulär. Uppgift 3a, 4 och 5 kan gå vidare med oförändrad beräkningsmetod medan beslut återstår.

### Uppgift 3a Planpost och bunden utvärdering före förändring

**Ändra:** `src/riskanalys/profil/modeller.py`, `profil/hantering.py`, `drift/historik.py`, `intag/utvardering.py`, `intag/tjanst.py`, `intag/webb.py`, `kommandon/profil_kommando.py`, `faststallelse/grindar.py` och befintlig återgivning av utvärderingshistorik där kravmatrisen visar behov. Ingen omläggning av bedömnings-, skriv- eller analysmappar ingår i 3a.

**Skapa:** `src/riskanalys/profil/planering.py`, `src/riskanalys/intag/planeringsvy.py`, `tester/enhet/test_tjansteplanering.py`, `tester/intag/test_tjansteplanering.py`.

**Gränssnitt:**
- `Tjansteplan` i `profil/modeller.py`: `id: str`, `tjanst: str`, `typ: Literal['ny_tjanst','vasentligt_andrad_tjanst','ny_marknad','annan_forandring']`, `beskrivning: str`, `avsett_inforande: date | None`, `uppgifter: dict[str, Uppgift]`.
- `Profil.tjansteplaner: tuple[Tjansteplan, ...] = ()`; tomt fält utelämnas vid serialisering. `id` unikt, tjänst finns i regelpaketet, uppgifts-ID:n finns i fältregistret och värden valideras med befintlig typkontroll.
- `plansumma(rb: Regelbas, profil: Profil, plan_id: str) -> str` i `profil/planering.py`: bind planens innehåll, relevanta sakuppgifter och regelbasens identitet; exkludera historikhändelsen själv och det förväntade bytet av erbjudandeflaggan. Dokumentera exakt kanonisk payload och versionsmarkör. Annars skulle själva införandet omedelbart göra utvärderingen inaktuell.
- `forandringshinder(rb: Regelbas, fore: Profil, efter: Profil, historik: Historik, datum: date, *, rattelse: Erbjudanderattelse | None = None) -> tuple[str, ...]` i `profil/planering.py`. Kontrollera registrerade förändringar före sparning och motsvarande aktualitet före ny fastställelse. Samma kontroll används av CLI och webb; lägg inte diskåtkomst i den rena funktionen `bekrafta`.
- **Erbjudandeövergångar, projektets regel:** jämför den sparade profilens före-värde med hela den föreslagna transaktionens efter-värde. Bekräftat, giltigt `false` → bekräftat `true` kräver registrerad plan och aktuell bunden utvärdering. Okänt → bekräftat `true` behandlas som första kartläggning, om ingen registrerad plan eller uttryckligt nytt införande anger annat. `true` → `true` kräver inte plan enbart på grund av flaggan; planerad ny marknad eller väsentlig ändring prövas ändå. Flera formulärsvar i samma sparning får inte dölja ursprungligt nej genom ett mellanliggande okänt värde. En känd historisk nej-uppgift som senare blivit inaktuell är inte belägg för en första kartläggning; använd plan eller dokumenterad rättelse när historiken visar detta. Detta är ett sätt att styra programflödet, inte olika lagkrav för ja/nej/okänt.
- **Rättelseväg:** ett felregistrerat nej får rättas till ja utan att låtsas att ett nytt införande sker. Inför ett uttryckligt rättelseläge i CLI/webb. Definiera `Erbjudanderattelse` i `drift/historik.py` med `tjanst: str`, `fore: Uppgift`, `efter: Uppgift`, `motivering: str`, `kalla: str`, `ansvarig: str`, `datum: date`, `profilrevision: str`. Alla textbelägg är obligatoriska och före-/efteruppgiften ska stämma med transaktionen. Utöka `Handelse.typ` med `rättelse` och `Handelse.rattelse: Erbjudanderattelse | None`; datum ska stämma med händelsen och osatt post utelämnas vid historisk serialisering. Spara rättelsespåret med befintlig lås-/revisionskontroll. En vanlig nej→ja-sparning får inte automatiskt klassas som rättelse, och en verklig registrerad förändringsplan kringgås inte med rättelseläget. Rättelse ersätter inte andra krav på uppdaterad bedömning/analys.
- Utöka befintlig historikhändelse med frivilliga `plan_id` och `plansumma`, utelämnade när de saknas. En sådan händelse beskriver faktiskt genomförd utvärdering av den allmänna riskbedömningen med hänsyn till planen: berörda hot/sårbarheter, påverkan på risk/rutiner, underlag och beslut om uppdatering eller motiverat behållande. Motorbedömning krävs inte. En registrerad händelse är inte i sig bevis på sakligt fullgjord utvärdering.
- Historik för en avgränsad plan får inte automatiskt flytta fristen för utvärdering av hela den allmänna riskbedömningen. `senaste_utvardering` och `nasta_genomgang` skiljer planbunden händelse från full utvärdering; gamla händelser behåller tidigare innebörd.
- **Effekt på befintlig analys:** `analys/lagring.py:bygg_bindning` binder hela historikfilens kontrollsumma, och `analysaktualitetshinder` jämför den levande bindningen. En planutvärdering eller rättelse gör därför befintligt analyspaket och dess aktuella beslut inaktuella även om risketiketten är oförändrad. Behåll denna konservativa regel i 3a; filtrera inte bort planhändelser från bindningen. Visa användaren vad som behöver förnyas. Historiska beslut ligger kvar, men gäller inte för det ändrade underlaget. Profiländring kräver dessutom ny aktuell bedömning enligt befintligt flöde; enbart historikändring kräver inte i sig en ny numerisk motorberäkning. Förnya bindning och sakpröva innan ny fastställelse.
- Planeringsuppgifterna får omfatta måltjänstens egna `P-TJ.<slug>_...`-fält och uttryckligen valda `P-GEO.*`, `P-KUND.*`, `P-KANAL.*` eller relevanta `P-RISK.*`-fält som definieras i regelbasen. Validera ID och typ, märk som planantaganden och använd aldrig planvärden för att ändra aktuell profil. Roll-/personfält, andra tjänsters erbjudande, härledda andelar och kontrollernas utfall/effekt är inte tillåtna ersättningsfält. Ingen numerisk tillämpning av planvärden införs i 3a.

- [ ] Skriv `test_plan_sparas_utan_att_erbjudandet_andras`, `test_plan_kan_utvarderas_utan_motorresultat` och `test_registrerad_plan_stoppar_ja_utan_bunden_utvardering` för både CLI och webb. Noll befintliga kunder ska inte hindra registrering eller ge en automatisk risknivå.
- [ ] Skriv `test_bekraftat_nej_till_ja_kraver_plan`, `test_okant_till_ja_ar_kartlaggning`, `test_okant_med_registrerad_plan_kringgar_inte_utvardering`, `test_batch_bevarar_ursprungligt_nej` och `test_ja_till_ja_utloser_inte_nytt_inforande`. Skriv också `test_rattelse_av_felaktigt_nej_kraver_motivering_och_belagg`, `test_rattelse_sparas_med_fore_och_efter` och `test_vanlig_andring_blir_inte_automatisk_rattelse`. Verifiera både CLI och webb med samma tjänsteregler innan implementation.
- [ ] Skriv `test_arlig_utvardering_godtar_inte_annan_plan`, `test_andrad_plan_kraver_ny_utvardering`, `test_inforandets_erbjudandeflagga_bryter_inte_bindningen`, `test_planutvardering_flyttar_inte_arsfristen`, `test_framtida_utvardering_avvisas`, `test_otillatna_planfalt_avvisas` och `test_gammal_profil_och_historik_serialiseras_lika`. Kör och bekräfta relevanta fel före implementation.
- [ ] Implementera planpost, planeringsformulär, saklig utvärdering, bindning och gemensam ändringskontroll. Utvärderingen får kräva uppdaterad analys/rutiner när sakprövningen visar det; den är ingen generell automatisk införandeattest.
- [ ] Lägg till `test_planutvardering_gor_alla_aktuella_analysbeslut_inaktuella` och `test_fornyad_analys_kravs_efter_rattelse` i befintliga bindnings-/analysprov. Kontrollera faktisk `analysaktualitetshinder` och spärr mot nytt godkännande, inte bara att en hash ändras. Ingen automatisk omattest eller återställning av giltighet ingår.
- [ ] Anslut kontrollen till ändring av erbjudande och ny fastställelse för registrerad plan. För ny marknad eller ändring av en redan erbjuden tjänst kontrolleras även planens berörda fält och genomförandebeslut; oförändrad ja-flagga är ingen genväg. Ett uttryckligt nytt införande kräver planregistrering; skilj det från första kartläggning av redan befintliga tjänster. Historiska paket får läsas som tidigare utan retroaktiv planpost eller påhittad utvärdering. Kravkartan dokumenterar vad programmet kan kontrollera och vad verksamheten måste göra utanför det.
- [ ] Kör de två nya testfilerna samt `tester/enhet/test_historik.py`, `tester/enhet/test_profil.py` och befintliga fastställelseprov som uppgift 1 identifierat. Kontrollera att nya vyer har samma lås-, revisions- och CSRF-skydd som befintligt intag.
- [ ] Commit: `feat: stöd utvärdering inför planerade tjänster`.

**Klart när:** En plan kan få en genomförd, sakligt dokumenterad och bunden förändringsutvärdering innan erbjudandet ändras, utan krav på ett nytt motor- eller rapportflöde.

### Uppgift 4 Registrera deklarerade kombinationsgrupper lokalt

**Ändra:** `src/riskanalys/profil/modeller.py`, `profil/hantering.py`, `intag/fordelning.py`, `intag/tjanst.py`, `intag/webb.py`, `analys/exponering.py`, `analys/provning.py` och befintlig lokal underlagsrapport.

**Skapa:** `src/riskanalys/profil/kombinationer.py`, `src/riskanalys/intag/kombinationsvy.py`, `tester/enhet/test_kombinationsgrupper.py`, `tester/intag/test_kombinationsgrupper.py`.

**Gränssnitt:**
- `Kombinationsgrupp` i `profil/modeller.py`: `id: str`, `tjanst: str`, `population: Literal['kunder','uppdrag']`, `avgransning: str`, `beskrivning: str`, `sarbarheter: tuple[str, ...]`, `antal: Uppgift`, `bas: Uppgift`. Ett gemensamt `population` gäller både antal och bas. Ingen redundant `bas_population` lagras. Vid manuell registrering bekräftas att båda talen avser samma enhet; vid import av separat enhetstaggade tal avvisas enhetskonflikter före konstruktion av modellen.
- `Profil.kombinationsgrupper: tuple[Kombinationsgrupp, ...] = ()`; tomt fält utelämnas vid historisk serialisering. Sårbarhets-ID:n är analysreferenser, inte ett direkt numeriskt villkor. Bekräftelse avser gruppens sakbeskrivning och omfattning, inte en sakkunnigattest av risken.
- `kombinationsbrister(rb: Regelbas, profil: Profil) -> tuple[str, ...]` och `grupper_for_tjanst(rb: Regelbas, profil: Profil, tjanst: str) -> tuple[Kombinationsgrupp, ...]` i `profil/kombinationer.py`. Ingen summerad unik total produceras.

- [ ] Skriv `test_noll_och_okant_ar_olika`, `test_antal_over_bas_avvisas`, `test_olika_perioder_far_inte_ge_andel`, `test_population_galler_bade_antal_och_bas`, `test_ogiltig_tjanst_eller_sarbarhet_avvisas` och `test_overlappande_grupper_summeras_inte`. Prova även bool som tal, negativa tal och bas 0. Systemet får inte påstå sig kunna upptäcka ett felaktigt deklarerat källinnehåll enbart ur talet.
- [ ] Skriv `test_samma_marginaltal_bevisar_inte_kombination`, `test_gruppsyns_bara_i_ratt_tjanst`, `test_gamla_profiler_behaller_samma_payload` och `test_andrad_grupp_gor_analys_inaktuell`. Kör före implementation och kontrollera de relevanta felen.
- [ ] Implementera modell och kontroller. Antal/bas återanvänder `Uppgift` för bekräftelse, källa och period. Motstridiga eller inaktuella underlag ger kompletteringsbehov; de får inte tyst bli noll. Ett gruppantal jämförs med andra marginaltal bara när population, period och avgränsning faktiskt är jämförbara.
- [ ] Anslut gruppändringar till befintlig profilrevision och snapshotbindning: ny eller ändrad grupp kräver ny aktuell bedömning och förnyad berörd analysbindning, även om risketiketterna består. Testa hela detta förlopp, inte bara en ändrad hash.
- [ ] Lägg till lokal registrering/ändring och återgivning i befintlig tjänsteanalys. Behåll frivilliga tjänstefördelningar och alla fem faktorområden. Inget krav på individuella kundposter införs.
- [ ] Kör de nya testfilerna och `tester/intag/test_tjanstefordelning.py`. Kör samma befintliga motorfall före/efter: scenario- och sammanfattningsnivåer ska vara identiska i denna uppgift, eftersom D3/D9 ännu inte har anslutits.
- [ ] Commit: `feat: dokumentera kombinerad tjänsteexponering utan kundregister`.

**Klart när:** En byrå kan belägga att exempelvis 8 av 100 uppdrag har angivna egenskaper tillsammans, och systemet skiljer det från okänt överlapp utan att hitta på poäng eller kundidentiteter.

### Uppgift 5 Gemensam faktormekanism och kort lokal tillämpning

**Ändra efter kravmatrisens avgränsning:** `src/riskanalys/dokument/gemensamt_v8.py`, `dokument/arb_v8.py`, `dokument/nivamotivering_v8.py`, `dokument/operationskarta_v8.py`, `dokument/tjanstavsnitt_v8.py`, `dokument/analysunderlag.py` och berörda granskningsprov. Utgå från `288fa66`: gemensamt faktaunderlag är D-ARB.5 och fullständiga motorberäkningar ligger i B1. Använd befintlig `Sarbarhet.metodmotivering`, `kallhanvisningar`, lokala prövningar och scenarioreferenser.

**Test:** `tester/enhet/test_faktorskal_v8.py` och befintliga V8-prov. Ingen ny produktmodul behövs som förhandskrav; lägg de två avgränsade funktionerna i befintliga moduler.

**Gränssnitt:** `gemensamma_faktormekanismer(rb: Regelbas, bedomning: Bedomning) -> tuple[Textstycke, ...]` i `dokument/gemensamt_v8.py` skriver mekanism och källa en gång per entydig faktor-ID och definitionsversion i D-ARB.5. Urvalet är unionen av `Scenariobedomning.sarbarheter` för tjänster där `erbjuds is True`; vid äldre resultat utan scenarier används deras `tillampade_sarbarheter`. Återge inte hela katalogen eller ej aktiverade faktorer här. Definitionen betyder inte att faktorn gäller samtliga tjänster; preliminär aktivering och osäkerhet märks i den lokala tillämpningen. Ej tillämpliga faktorer och bedömda avgränsningar bevaras i sårbarhetsprövningen/B1. `lokala_faktorskal(rb: Regelbas, profil: Profil, paket: Analyspaket, tjanst: Tjanstbedomning) -> tuple[Textstycke, ...]` i `dokument/nivamotivering_v8.py` återger bara tjänstens relevans, avvikelse, berörda exponering och utfall med hänvisning till den gemensamma definitionen. Fulla faktorer och beräkningsspår förblir i B1. Funktionerna ändrar inga nivåer och anropar inte AI. Registrera exakta källfält i V8:s befintliga produktionskarta.

- [ ] Mät basen med `"$RISKANALYS_VENV/bin/python" docs/research/verktyg/rapportmatning.py med_betalningsmandat` och samma kommando med `fyra_tjanster`. Spara utdata med SHA och Python 3.12-version i granskningsprotokollet. De tidigare rapporterade 12 354 orden är en referens, inte en ny körning eller en hård gräns.
- [ ] Skriv `test_faktormekanism_staar_en_gang_gemensamt`, `test_tjansten_visar_lokal_betydelse_och_hanvisning`, `test_motorberakningar_stannar_i_b1`, `test_exponering_under_troskel_ar_inte_franvaro`, `test_ersatta_faktorer_forklaras_utan_dubbelrakning` och `test_samma_namn_med_olika_id_blandas_inte`. Kräv källa, mekanism och korrekt lokal tillämpning, inte bara texten `+1`.
- [ ] Lägg till `test_gemensamma_definitioner_begransas_till_aktiverade_faktorer_i_erbjudna_tjanster`, `test_faktor_enbart_i_ej_erbjuden_tjanst_utelamnas` och `test_ej_tillampliga_faktorer_bevaras_i_underlag`. Prova att preliminär aktivering inte beskrivs som en bekräftad sakuppgift och att historiska resultat utan scenarier har samma urvalsprincip.
- [ ] Skriv `test_privata_grupper_och_planer_andrar_inte_ai_begaran`, inklusive frysta omförsök. Två profiler som endast skiljer sig i nya lokala uppgifter ska ge identisk utgående AI-begäran. Kör före implementation.
- [ ] Implementera endast det förklaringsstöd som kravmatrisen visar saknas. Utöka D-ARB.5 med gemensamma definitioner och tjänsterna med lokal tillämpning. Behåll deterministisk källnot och flytten av motortabeller till B1; kopiera inte tillbaka dem till läsrapporten. Om mekanism saknas visas kompletteringsbehov i underlaget, inte en påhittad AI-förklaring.
- [ ] Kontrollera katalogposternas befintliga motiveringar innan innehåll läggs till. Ändrade tolkningar får källstöd och separat granskning; befintliga giltiga motiveringar skrivs inte om rutinmässigt.
- [ ] Kör nya tester, `tester/enhet/test_arb_v8.py`, `tester/intag/test_skyddad_begaran.py` och V8:s produktions-/källfältsprov som uppgift 1 har identifierat. Verifiera att motorutfallen är oförändrade.
- [ ] Kör samma två rapportmätningar efter ändringen. Redovisa före/efter och delta för ord i läsrapport och B1 samt ordagrann upprepning mellan tjänster. Skilj det från verktygets mått på likartad struktur. Motivera varje ökning; använd inget automatiskt ordtak. Tjänstespecifika sakskäl får inte tas bort för att korta text.
- [ ] Commit: `feat: förklara faktorernas betydelse i tjänstens riskscenarier`.

**Klart när:** Mekanismen förklaras gemensamt och tillämpningen lokalt, källspåret består och före-/eftermätningen visar omfattning och upprepning med förklarade förändringar.

### Uppgift 3b Valfri senare motororientering för en plan

**Status:** Kan skjutas upp. Kravstödet i 3a kräver varken denna funktion eller en ny väg genom skrivning, lokal analys, granskning och fastställelse. Ta ställning efter uppgift 1 och 5 om funktionen tillför användbar information.

**Om den väljs:** Återanvänd `src/riskanalys/bedomning/motor.py` från en liten ny `src/riskanalys/bedomning/planering.py`; lägg ett kort deterministiskt planunderlag i `src/riskanalys/dokument/planering_v8.py`. Lägg inte planresultat i `bedomningar/` och gör ingen generell omkoppling av V8-kedjans mappreferenser. Dokumentet är ett separat planunderlag i byråns privata data, med plan-ID, plansumma, profil-/modellbindning och tydligt syfte. Ingen ny AI-skrivning ingår.

**Gränssnitt:** `orientera_plan(rb: Regelbas, profil: Profil, plan_id: str) -> Tjanstbedomning` aktiverar måltjänstens erbjudandeflagga i en tillfällig kopia, lämnar byråns befintliga kund-/riskfaktorer oförändrade och markerar måltjänstens kontrolluppgifter som okända. Samma motor återanvänds; originalprofil och aktuell bedömning ändras inte. `planeringsstycken(rb: Regelbas, profil: Profil, plan_id: str, resultat: Tjanstbedomning) -> tuple[Textstycke, ...]` skriver ett kort underlag genom projektets befintliga dokumentmodell. Koppla exporten till befintlig exporttjänst med explicit plan-ID, aldrig som senaste aktuell bedömning.

- [ ] Skriv `test_planorientering_andrar_inte_aktuell_profil`, `test_planorientering_valjs_inte_som_aktuell_bedomning`, `test_plan_med_noll_kunder_betyder_inte_lag_risk`, `test_planrapport_markerar_metodbegransning` och `test_planorientering_arver_inte_belagd_kontrolleffekt`. Kör före implementation.
- [ ] Skriv `test_planantaganden_andrar_inte_motorutfall_fore_d3`: två planer med olika framtida mandat, insyn eller geografi men samma aktuella byråfaktorer får samma motorresultat före beslutad D3-anslutning. Underlagstexten visar deras olika antaganden. Alla planfält som kan ersättas efter D3 har redan tillåtet ID-/typkontrakt i 3a; faktisk numerisk anslutning får en uttrycklig beslutad fältlista i 6.
- [ ] Implementera orientering och kort separat dokument. Skriv uttryckligen: före D3 visar motorn katalogens grundnivåer och byråns befintliga faktorer som om tjänsten erbjöds. Planens egna uppgifter redovisas som antaganden och påverkar inte nivån. Redovisa inneboende PT/TF och att kontrollverkan i planen inte är belagd; återanvänd ingen befintlig kontrollreduktion som faktisk effekt i planen. En senare annan hantering kräver preciserat D8-beslut.
- [ ] Kör nya planeringsprov och mät dokumentets längd separat från aktuell läsrapport. Kravmatrisen anger om 3b genomförts eller skjutits upp. Commit: `feat: separat katalogbaserat underlag för planerad tjänst`.

**Klart när, om genomförd:** Resultatet är reproducerbart, avgränsat och tydligt märkt som motororientering med kända begränsningar. Det ersätter inte förändringsutvärderingen i 3a.

### Uppgift 6 Anslut endast beslutade metodändringar till motorn

**Beslutsberoende:** Godkända svar i befintligt beslutsformulär, kompletterat i 2, samt berörda underlagskontrakt i 3a och 4. 3b är ett beroende endast om beslutet gäller numerisk tillämpning av planantaganden. Ändringar i risknivåer börjar inte innan berört D-beslut anger exakta indata, villkor och facit.

**Berörda befintliga filer:** `src/riskanalys/bedomning/{motor,scenarier,modeller}.py`, `regelverk/{modeller,validering_scenario}.py`, `drift/modellidentitet.py`, `regelbas/kataloger/{sarbarheter,tjanster,kontroller}.yaml`, `regelbas/beslutstabeller/metod.yaml` och `regelbas/version.yaml`. Underlagsåtkomst placeras i en liten `src/riskanalys/bedomning/exponering.py` så att motorn inte blir beroende av webbformulär.

**Gränssnitt inför D3:** `bygg_exponeringsunderlag(rb: Regelbas, profil: Profil, tjanst: str) -> Exponeringsunderlag`, där en fryst dataklass samlar giltiga befintliga fördelningar, deklarerade grupper, källreferenser och osäkerheter. Den innehåller inga självvalda riskvikter. Återanvänd eller flytta befintlig ren fördelningsvalidering med bakåtkompatibla anrop från `intag/fordelning.py`; kopiera inte logiken.

- [ ] Precisera godkända svar i det befintliga beslutsformuläret med exakt katalog-/regel-ID, gamla/nya värden eller algoritm, underlagsfält, källor, motivering och kontrastfacit. Använd svarsmallens mått PT före kontroll, kvarstående PT och TF; skapa inget konkurrerande protokoll. Om uppgifter saknas återgår just det beslutet till metodprövning; oberoende färdiga uppgifter fortsätter.
- [ ] Skriv beslutat kontrastfacit som fallerande test i `tester/regelkontrakt/test_scenariomotor.py` eller en liten `test_tjansteexponering.py`. Testet ska visa både aktiverade faktorer och scenarioresultat, inte bara högsta etiketten.
- [ ] Implementera ett D-ID i taget. D3 styr tjänsteavgränsning och okänd fördelning; D4/D9 styr om och hur gruppbevis ersätter ett antagande om samförekomst. D5 styr relevant mängd och sammanvägning. D6 styr TF. D8 styr reduktion. Inga fria analysbeslut eller grupptexter tolkas till poäng.
- [ ] Behåll riskutfall för scenarier som fortfarande är relevanta enligt beslutet. Ett lokalt `ej_relevant` får inte ensamt ta bort ett motorscenario utan den särskilda behörighets-, evidens- och bindningsregel som D5 beslutat.
- [ ] Versionsändra metod och modellbindning. Gamla bedömningar och attester bevaras; nytt underlag kräver ny beräkning och berörd granskning. Uppdatera inte en gammal fryst risknivå i rapportlagret.
- [ ] Kör de berörda regelkontrakten och befintliga H7.1-kontraster. Redovisa scenarioändringar, ändrade sammanfattningar och sakligt motiverade oförändrade utfall. Om två jämförelsefall fortfarande ger samma nivå ska spåret visa om skillnaden behandlats och varför etiketten består.
- [ ] Commit per beslut: `feat: tillämpa beslutad metod D-ID för tjänsteexponering` med faktiskt ID i stället för platshållaren.

**Klart när:** Varje införd metodändring motsvarar ett verkligt beslut och ett godkänt sakfacit. Ingen regel väljs enbart för att ge lägre risk eller fler olika nivåer.

### Uppgift 7 Följ hela kedjan och slutför kravkartan

**Ändra:** `tester/typfall/test_kravstod_hela_kedjan.py`, relevanta befintliga export-/historikprov och granskningsprotokollen från 0–2. Återanvänd `tester/typfall/test_analys_hela_kedjan.py` och V8:s befintliga frysta AI-fixturer.

**Leverans:** `docs/superpowers/reviews/2026-10-21-kravstod-slutprov.md`, uppdaterad kravmatris, teknisk modellvalidering där metoden ändrats samt `docs/STATUS.md`.

- [ ] Skriv och kör först saknade acceptansprov för minimileveransen: plan registreras → saklig förändringsutvärdering genomförs och binds → registrerat erbjudande kan ändras → ändrad plan kräver omprövning. Kontrollera att ingen motorbedömning krävs i 3a, att planeringsdatum inte blir genomförandedatum och att en avgränsad planutvärdering inte skjuter upp hela årsgenomgången.
- [ ] Om 3b ingår: följ separat planorientering → kort planunderlag, med begränsningen före D3 och oförändrad aktuell bedömning. Om 3b skjutits upp ska detta framgå; låt inte dess acceptansprov blockera färdig 3a eller köras som om funktionen vore implementerad.
- [ ] Följ gruppfallet från källa/period/bas genom rätt tjänsts sårbarheter, hot, scenarioresultat, sammanfattning, rapport, rutinåtgärd och senare utvärdering. Jämför samtidig, åtskild och okänd exponering med samma marginaltal. Markera eventuella kvarstående öppna metodbeslut.
- [ ] Pröva oförändrad årlig utvärdering, uppdatering vid ändrad exponering, ny marknad, väsentlig tjänsteändring, gammal modell och ändrat privat belägg. Kontrollera att bara genomförda utvärderingar registreras och att gamla godkännanden inte återanvänds på nya fakta.
- [ ] Följ särskilt planutvärdering → ändrad historiksumma → inaktuellt analyspaket och samtliga aktuella analysbeslut → uttrycklig förnyelse och sakprövning → ny fastställelse. Prova att detta gäller även vid oförändrad numerisk nivå, och att enbart historikändring inte felaktigt påstås ändra motorns risk. Kontrollera också nej→ja med plan respektive motiverad rättelse och okänt→ja vid kartläggning.
- [ ] Prova faktisk informationsåtkomst och rapportexport. För krav 31–32 skiljs programstödet från verksamhetens dokumenterade information/utbildning; inga tester räknas som verklig utbildning eller sakkunnigattest.
- [ ] Verifiera Python 3.12 enligt miljökontrollen ovan. När alla beslutade koduppgifter är färdiga: `"$RISKANALYS_VENV/bin/python" -m pytest`, `"$RISKANALYS_VENV/bin/riskanalys" regelbas validera` och `git diff --check`. Godkänt: exit 0, inga fel och livetester hanteras enligt projektets markeringar utan riktiga API-anrop. Dokumentera interpreter och paketversioner; andra Python-versioners utfall räknas separat.
- [ ] Exportera gruppfallet och förändringsutvärderingens levererade dokumentation via befintliga vägar. Rendera med projektets renderingskedja (LibreOffice/Poppler) eller motsvarande och kontrollera berörda sidor, tabeller, källspår och att inget lokalt underlag saknas eller felaktigt beskrivs som faktisk historik. Om 3b genomförts renderas dess korta planunderlag separat. Ingen specifik agentmiljös skill eller runtime är ett genomförandekrav.
- [ ] Upprepa rapportmätningarna från 5 med samma syntetiska profiler och frysta AI-svar. Redovisa ord per leveransdel, ordagrann upprepning och förklarade ökningar i slutprovet. Blanda inte omflyttning till B1 med faktisk minskning av den totala dokumentationen.
- [ ] Slutför alla 36 rader i matrisen med faktiskt körda bevis. Skilj `finns`, kvarstående `delvis` och `saknas`; dölj inte öppna punkter genom en generell klarstatus. Rapportera teknisk verifiering, verklig metodgranskning och verksamhetsåtgärder separat.
- [ ] Commit: `test: verifiera kravstöd och tjänsteexponering genom hela kedjan`. Lämna konkret granskningsunderlag före integration enligt användarens senare instruktion.

**Klart när:** De genomförda funktionerna och beslutade metoden kan följas genom hela kedjan, alla kravpunkter har ett spårbart läge och historik/integritet är verifierade. Planen är inte en utfästelse om att externa verksamhetsåtgärder redan har utförts.

## Status för denna planbeställning

Revision 3 kompletterar den avstämda revision 2 med uppföljande återkoppling i chatten. Historikbindningen och erbjudandesparningen har kontrollerats mot `288fa66`; uppgifterna om lokala Python-miljöer är granskarens observation och ska kontrolleras i genomförandets checkout. Plan och design har reviderats lokalt; inga produktfiler har ändrats, inga produkttester eller rapportmätningar har körts och inga metodbeslut eller sakkunnigattester har registrerats. Genomförandet börjar med uppgift 0 vid en senare implementationsbeställning.

## Genomförandestatus 2026-10-22

Beställd underlagsleverans genomförd på `codex/kravstod-tjansteexponering`. Basen och de 36 kraven är inventerade; 3a, 4 och den avgränsade 5 är införda. Befintligt beslutsformulär har par 9–10. 3b är uppskjuten enligt planens frivilliga gräns och 6 avvaktar verkliga preciserade metodbeslut. Full svit efter granskningsrättningar: 3 010 godkända, 1 avmarkerat livetest, exit 0 i Python 3.12.15. Se [slutprov och avgränsningar](../reviews/2026-10-21-kravstod-slutprov.md); ursprungliga checklistor ovan är den godkända beställningen och ska inte tolkas som att expertbeslut eller verkliga verksamhetsåtgärder utförts.
