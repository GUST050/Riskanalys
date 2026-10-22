# Engångssvar och automatisk återanvändning – genomförandeplan F

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Genomför själv; användaren vill granska införandet med Claude.

**Goal:** Byrån besvarar gemensamma sårbarhetsfrågor en gång; svaren används automatiskt i alla valda tjänster, och användaren arbetar med tjänstespecifika uppgifter och avvikelser.

**Architecture:** Återanvänd schema 2:s gemensamma poster och interna tillämpningar. Lägg till en gemensam bekräftelsehandling för alla valda tjänster och en samlad tjänstegenomgång som registrerar interna block-/scenariobekräftelser först efter full innehållskontroll. Särskilda täckningsprövningar, analysbeslut och sakgranskningar hålls separata.

**Tech Stack:** Python 3.12.15, befintlig pytest, Pydantic, typade analysmodeller, befintligt HTTP-/CLI- och V8-flöde. Inga nya beroenden eller riskmetoder.

**Spec:** `docs/superpowers/specs/2026-10-22-engangssvar-och-testtid-design.md`, avsnitt 4–6; kompletterar godkänd design `2026-10-22-forenklad-riskbedomning-design.md`. Status: genomförande godkänt med granskningsändringarna. Bas efter godkänd plan T; produktbas `f66a70f`.

## Global Constraints

- Gemensamma fakta lagras en gång i nya analyser. Äldre originalsvar och attributioner bevaras vid överföring.
- Behåll schema 1:s bytes och historiska attestkontrakt; inget schema 3 behövs.
- Automatiskt återanvända fakta betyder inte lika riskpåverkan i alla tjänster. Motorn och D3/D9 lämnas oförändrade.
- Antaganden/kunskapsluckor får inte upphöjas till bekräftade fakta. Avvikelser och otillräckligt underlag skrivs aldrig över samlat.
- Alla sparande handlingar kontrollerar revision, referenser och författare atomiskt inom befintligt analyslås.
- Analysgodkännande, täckningsprövning, dokumentets sakgranskning och fastställelse är separata handlingar.
- Inga privata analysuppgifter till AI, inga verkliga API-anrop i prov och inga ändrade sakkunnigstatusar i repot.
- Använd T:s riktade körpolicy och en fullsvit vid slutleveransen. Ingen fullsvit efter varje delsteg.

## Review Focus

1. En tjänst med avvikelse får inte skrivas över av ”gäller för alla”: F1 provar blandad fyrtjänstmatris.
2. Gemensam faktaändring efter visning får inte bulkbekräfta gamla uppgifter: F1 provar revision/postsumma och atomiskt avslag.
3. En samlad tjänstehandling får inte dölja saknad lokal sårbarhet, obelagt kontrollavdrag eller otäckt TF: F2 provar varje grind innan stämpling.
4. Ny/återinförd tjänst får använda gemensamma fakta men inte gamla tjänstebeslut eller en genomförd plan: F2 provar nytt urval och A:s planflöde.
5. En kortare rapport kan ha tappat svar eller attribution: F3 jämför semantiska fakta, B1-original, källreferenser och båda renderade dokumentdelarna.

## Task 1: F1 Gemensamt underlag en gång för samtliga tjänster

**Files:** Create `src/riskanalys/analys/engangssvar.py`, `tester/enhet/test_engangssvar.py`, `tester/intag/test_gemensam_helhetsbekraftelse.py`. Modify `analys/{gemensam.py,gemensamma_operationer.py}`, `intag/{gemensamvy.py,gemensamformular.py,webb.py}`, `kommandon/analys_kommando.py`.

**Interfaces:** Icke persistent fryst strikt `GemensamCell(tjanst: str, slag: Literal['sarbarhet','verksamhet'], post: str, postsumma: str)`. `visade_celler(paket, tjanster: tuple[str,...]) -> tuple[GemensamCell,...]` ger exakt de visade oförändrade cellerna. `bygg_gemensam_bekraftelse(paket, tjanster, celler, forfattare) -> Analyspaket` kräver exakt samma cellmängd och inga dubbletter. `bekrafta_byraunderlag(tjanster, celler, revision, forfattare) -> str` kontrollerar erbjudna tjänster och sparar en gång inom låset.

- [ ] Skriv `test_ett_svar_anvands_i_fyra_tjanster_utan_lokala_kopior`: en källpost i paketet, samma sakuppgift i fyra effektiva läsvyer, inga duplicerade gemensamma originalsvar. Skriv `test_samlad_handling_bevarar_avvikelse_och_otillrackligt`, `test_antagande_forblir_antagande`, `test_andrad_post_eller_fel_tjanst_sparar_ingenting` och `test_svarimport_kan_inte_skapa_helhetsbekraftelse`.

Testfilens nya lokala fixtur `en_post_fyra_tjanster` ger `(paket, referenser)` med en belagd gemensam post vars beskrivning är `Gemensamt provunderlag.`, fyra tjänster och oförändrade standardtillämpningar. Lokala tjänsteposter får finnas men inga kopior av den gemensamma posten.

```python
def test_ett_svar_anvands_i_fyra_tjanster_utan_lokala_kopior(en_post_fyra_tjanster):
    paket, referenser = en_post_fyra_tjanster
    ids = tuple(t.tjanst for t in paket.tjanster)
    nytt = bygg_gemensam_bekraftelse(paket, ids, visade_celler(paket, ids), 'Syntetisk författare')
    assert len(ids) == 4
    assert len(nytt.gemensamma_sarbarhetsprovningar) == 1
    for fore, efter in zip(paket.tjanster, nytt.tjanster, strict=True):
        assert fore.sarbarhetsprovningar == efter.sarbarhetsprovningar
        assert any('Gemensamt provunderlag.' in p.motivering
                   for p in effektiv_tjanst(nytt, efter.tjanst).sarbarhetsprovningar)
```

- [ ] Kör RED: `.venv312/bin/python -m pytest tester/enhet/test_engangssvar.py -q`. Implementera ren ombyggnad och låst operation. Bara synligt föreslagna oförändrade celler med `galler` uppdateras; befintliga avvikelser/osäkerhetsval lämnas och redovisas. Ogiltig revision/post/service avvisar hela skrivningen. Bygg alla tillämpningar före senare blocksummor.
- [ ] Låt den låsta operationen läsa aktuell bedömning och avvisa ej erbjudna/okända tjänster som mål, liksom dubbla mål/referenser. Den rena funktionen kontrollerar paketets ID och referenser; den får inte ensam användas som bevis för att ett lagrat äldre tjänste-ID fortfarande erbjuds.
- [ ] Gör gemensamma frågeformuläret till den enda normala redigeringen av gemensamma fakta. Visa automatisk återanvändning i en gemensam serviceöversikt, inte en obligatorisk checklista per tjänst/post. Handlingen ”Bekräfta gemensamt underlag för valda tjänster” visar exakt vilka oförändrade tillämpningar som omfattas och vilka undantag som lämnas.
- [ ] Lägg skyddad POST `analysbekraftabyraunderlag` samt CLI `analys BYRA --bekrafta-byraunderlag FIL --revision SUMMA --forfattare NAMN`; filen har explicit `tjanster` och typade `celler` med tjänst/post/summa. Exakt mängd jämförs med serverns visade giltiga celler; servern får inte tyst hoppa över eller lägga till en cell. Strikt fält-/storlekskontroll, CSRF/origin, escaping och CAS enligt befintliga rutter. Inget nytt tillåtelselisteinnehåll till AI.
- [ ] Kör nya enhets-/HTTP-/CLI-prov plus befintliga schema-/import-/riktning-/evidensprov. Lägg till nya node-ID i T:s profiler. Commit: `feat: återanvänd gemensamma svar för alla valda tjänster`.

## Task 2: F2 En samlad tjänstegenomgång, interna kontrollblock

**Files:** Modify `analys/{provning.py,engangssvar.py,gemensamma_operationer.py,tjanst.py}`, `intag/{analysvy.py,gemensamvy.py,webb.py}`, `kommandon/analys_kommando.py`. Create `tester/enhet/test_tjanstegenomgang.py`, `tester/intag/test_tjanstegenomgang.py`. Extend `tester/typfall/test_gemensam_analys_hela_kedjan.py`.

**Interfaces:** `bygg_tjanstbekraftelse(rb, profil, bedomning, paket, tjanst: str, forfattare: str) -> Analyspaket` ändrar inga tillämpningar: de måste redan vara aktuellt bekräftade före täckningsprövning. Bygg kandidat med visade scenarioval och blocksummor, pröva genom ordinarie `analysbrister` (som inkluderar `gemensamma_analysbrister`). För tjänstegenomgången används en ren prövningsprojektion med endast målservice i bedömning/paket men alla gemensamma poster, belägg och bindningar kvar; inga globala fel filtreras bort genom textprefix. Projektionen sparas aldrig. Ingen `krav_bekraftelser`-flagga införs. `bekrafta_tjansteunderlag(tjanst, revision, forfattare) -> str` publicerar originalpaketets validerade kandidat atomiskt.

- [ ] Skriv ordningsprov: gemensam handling → täckningsprövning → tjänstegenomgång lämnar allt aktuellt. Tjänstegenomgång före gemensam handling/täckning avvisas med tydlig nästa åtgärd. Efterföljande ändrad täckningsprövning gör genomgången inaktuell enligt befintlig hash.
- [ ] Skriv positivt prov där ett komplett fyrtjänstfall bekräftas genom en gemensam handling och fyra tjänstegenomgångar; inga extra klick för 32 scenarier eller 64 block krävs. Kontrollera att interna stämplar är aktuella, samma motorutfall, och inga analysbeslut/sakgranskningar har skapats.
- [ ] Skriv negativa prov för saknat lokalt tjänsteinnehåll, oklar aktivering/relevans, fel hot, saknat belägg, otillräcklig kontrollräckvidd, egen PT/TF-risk utan rätt obligatoriskt riskled, för låg jämförelsenivå utan motivering och stale revision. Varje fel ska lämna alla stämplar och originalbytes oförändrade. Kontrollera att falska importerade stämplar fortfarande nollställs/avvisas.
- [ ] Kör RED på de nya proven. Använd endast ordinarie grinden på kandidaten, inklusive globala gemensamma fel. Bekräfta inte egna täckningsprövningar, oklara scenarioval eller kvarstående metodkonflikter automatiskt. Räkna blocksummor efter att kandidatens samtliga tillämpningar/scenarioval fått sitt slutliga innehåll så att inga nystämplade block omedelbart blir inaktuella.
- [ ] Visa ett tjänsteavsnitt med gemensamma fakta som läst underlag, lokala uppgifter och undantag som redigering, samt sammanvägning/hot/PT/TF. Ge handlingen ”Bekräfta visat tjänsteunderlag”. POST `analysbekraftatjansteunderlag` och CLI `--bekrafta-tjansteunderlag TJANST_ID` använder samma operation. Analysgodkännande och sakgranskning ska fortfarande vara egna handlingar.
- [ ] Sammanställ automatiskt redan kända tjänstefakta från bekräftad tjänstebeskrivning/profil och länkade gemensamma poster. Kräv inte att de skrivs om i fritext. Saknad koppling eller tjänstespecifik uppgift blir en konkret komplettering, inte ett påhittat sakförhållande. Provet `test_gemensamma_fragor_aterkommer_inte_som_tjanstens_inmatningsfalt` ska verifiera det normala formuläret; ett dolt gammalt obligatoriskt fält är inte en förenkling.
- [ ] Prova tillagd/återinförd tjänst efter redan bekräftad gemensam analys: automatiskt gemensamt läsunderlag, dess standardtillämpningar bekräftas först gemensamt före eventuell täckningsprövning och tjänstegenomgång, inga omskrivna gemensamma svar och inga ärvda tjänstebeslut. Giltig plan krävs fortfarande vid bekräftat nej → ja; gamla terminala planer återöppnas aldrig.
- [ ] Ändrad gemensam post gör tidigare tillämpning/tjänstegenomgång inaktuell och alla paketbeslut inaktuella. Visa en samlad väg för återbekräftelse efter jämförelse, utan att radera avvikelser. Kör nya prov, analysprofil och befintliga negativa grindar. Commit: `feat: bekräfta tjänsteunderlag utan separata blockklick`.

## Task 3: F3 Mät det verkliga nya arbetssättet och slutverifiera

**Files:** Modify `tester/fixturer/{gemensam_analys.py,fylld_gemensam.py}`, `docs/research/verktyg/{rapportmatning.py,forenklad_slutprov.py}`, `dokument/{gemensam_provning_v8.py,tjanstavsnitt_v8.py}` bara för visade dubbletter, `intag/gemensamformular.py`, `docs/{kravstod.md,STATUS.md}`. Create `tester/typfall/test_engangssvar_arbetsflode.py`, `docs/superpowers/reviews/2026-10-22-engangssvar-slutprov.md`. Extend `tester/enhet/test_forenklat_slutprovsverktyg.py`, `tester/typfall/test_gemensam_analys_ai_grans.py`.

**Interfaces:** Lägg `--analyslage schema1|direkt2|overforing2` på båda mät-/slutprovsverktygen. Utan ny flagga behåller rapportmätningen sitt schema1-standardläge och slutprovsverktyget sitt overforing2-läge. Behåll `--analys-schema` i rapportmätningen som kompatibilitetsalias till dess nuvarande beteende; samtidig motstridig angivelse ger fel. Ny fixtur `bygg_direkt_gemensamt_fall(rb, rot: Path, namn: str) -> GemensamtFall` använder den befintliga returtypen i `tester/fixturer/gemensam_analys.py` och bygger via schema-2-start, gemensamma svar och F1/F2:s publika handlingar, aldrig `foresla_overforing`. Rå resultatdata anger läge, underlags-/motor-/skrivsvarshash, ord per dokumentdel och kategoriserad handlingslogg.

- [ ] Skriv RED-prov som förbjuder att direkt2 anropar överföringsfunktionen. Kontrollera identiska semantiska fakta, motorutfall och frysta skrivsvar i schema1/direkt2; struktursumman får skilja när lagringsstrukturen skiljer. Historiskt overforing2 bevarar alla originalsvar och redovisas separat.
- [ ] Låt direkt2 starta med `forifyll_analys(..., schema=2)` och besvara gemensamma poster genom de publika sparhandlingarna. Det får använda samma frysta profil/motor/skrivsvar som jämförelsen, men inte ta en färdig schema-1-analys och köra `forifyll_gemensamt` på den. Kontrollera att det nya fallet har lokala tjänstesvar men inga dubbellagrade gemensamma svar.
- [ ] Kör båda fallen `fyra_tjanster` och `med_betalningsmandat`. Mät antal svar per gemensam fråga, sparade lokala kopior, redigeringar, tillämpnings-/scenario-/blockhandlingar, tjänstegenomgångar, analysbeslut, täckningsprövningar och sakgranskningar separat. För rent fyrtjänstfall: en gemensam + fyra tjänstehandlingar efter svarsinmatning, inga dolda extra block-/scenariobekräftelser. Redovisa också total faktisk handlingslogg och faktiskt antal nödvändiga/utförda täckningsprövningar i vartdera fallet; kalla inte fem bekräftelser fem totala klick.
- [ ] Mät läsrapport, B1, total och upprepning för direkt2 mot schema1 med samma sakunderlag. Gemensamma beskrivningar står en gång; lokala resonemang får finnas per tjänst. Bevara relevanta belägg, original och attributioner. Redovisa faktisk skillnad även om rapporten inte blir kortare; gör ingen obeställd redaktionell ombyggnad.
- [ ] Rätta den kända formulärbristen vid byte bort från `galler_annorlunda`: ignorera endast de gamla manuella riktningsfälten i den tillåtna övergången och kassera dem; behåll avvisning av förfalskad programhärledd riktning. RED/GREEN för båda fallen. Dokumentera reserverat `gemensam:` som intern referens, inte ett ID användaren ska skriva.
- [ ] Kör hela privata AI-begäransjämförelsen inklusive omförsök/reserv; öppna det nya huvudflödet och en avvikelse i syntetisk UI-session. Exportera båda faktiska V8-delar i direkt2 och kontrollera berörda sidor för gemensamma fakta, tjänstens avvikelse, risk och B1. Riktad layoutkontroll redovisas som riktad, inte fullsidig.
- [ ] Kör snabb-/analysprofil under arbetet. Därefter frys källorna och kör **en** komplett icke-live-svit, regelbasvalidering och diffkontroll med T:s verktyg. Verifiera aktuell collection/JUnit/snapshot. Kodrättning efter slutkörningen kräver ny grön fullsvit; oförändrad grön körning upprepas inte för slutdokumentation.
- [ ] Dokumentera faktisk testtid, arbetsbörda och rapportlängd, kvarstående produkt-/metodbegränsningar och lokala commit-SHA i granskningsunderlaget. Commit: `feat: verifiera engångssvar och direkt schema-2-flöde`. Lämna till användarens Claude-granskning; ingen push/merge.

## Självkontroll och avgränsning

Gemensamma fakta är källan; tjänstens analys är en tillämpning, inte en ny frågeomgång. F1 provar en gång/fyra tjänster och atomisk undantagshantering. F2 provar samlad bekräftelse med oförändrade sakgrindar och ny tjänst. F3 provar verklig arbetsbörda, direkt skapad rapport, historik och AI-gräns. Alla fem Review Focus-rader har konkreta prov. Detta är mer än att slå ihop block 5/7/9:s knappar, men återanvänder de befintliga interna modellerna. Manuell nivåbedömning av tjänster utanför katalogen och metodbeslut D3/D9 ingår fortfarande inte.
