# Planåterkallelse och införandeval Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rätta övergivna planer och automatisk genomförandemarkering av flera planer utan att försvaga införandespärren eller förlora historik.

**Architecture:** Behåll planens genomförandepost och lägg till en alternativ, oföränderlig återkallelsepost. En gemensam kärna tar uttryckligt planval per tjänst; webb och CLI använder den och sparar hela erbjudandeövergången atomiskt. Detta är en fristående första leverans före strukturändringen.

**Tech Stack:** Python 3.12, befintlig Pydantic 2, YAML, pytest och lokal HTTP-server. Inga nya beroenden.

**Spec:** [Godkänd design revision 2, särskilt avsnitt 3 och 9](../specs/2026-10-22-forenklad-riskbedomning-design.md). [Huvudplanen](2026-10-22-forenklad-riskbedomning-plan.md) tar vid efter denna leverans.

## Global Constraints

- Produktbas: `91a3ece`; arbetsbas med godkänd design: `837917253c4d0edc99969bd056f19afd9695a85d` på `codex/kravstod-tjansteexponering`. Lås faktiskt start-SHA och arbetsstatus i körloggen.
- Godkänd teknisk verifiering använder Python 3.12, syntetiska uppgifter och testleverantör. På nuvarande dator används `.venv312/bin/python`; kontrollera `sys.version_info[:2] == (3, 12)` och att importen kommer från avsedd checkout. Återskapa inte `.venv` med datorns standard-Python.
- Webb och CLI använder samma kärna. Återkallelse och genomförande sparas atomiskt med profilen, under befintlig låsordning och CAS.
- Årsfristen för hela bedömningen förblir separat. Planval och återkallelse är privata och tillförs inte AI-underlaget.
- Terminal historik kontrolleras inte mot senare byråfakta. Äldre serialisering och fastställda paket bevaras.
- Riskmotor, vikter, maxregel, kontrollavdrag, tillåtelselista och sakkunnigstatus ändras inte. Ändrad profilmodell kan ändra modellidentiteten och ska förklaras i uppgraderingsinformationen.
- Ingen produktkod skrivs vid planleveransen. Vid genomförande: test först, verifiera rätt felsymtom, implementera, granska uppgiften och fortsätt. AGENTS kräver grön fullsvit före produktcommit; samla denna sammanhängande rättning i leveranscommit efter A3 i stället för att committa halvfärdiga kontrakt mellan uppgifterna.

## Review Focus

1. Historiskt nej via alias eller mellanliggande okänt ska kräva samma införandeval som ett aktuellt nej. Prov i A2.
2. En gemensam erbjudandebekräftelse med två införanderader och ett felaktigt planval får inte spara någon av raderna. Prov i A3.
3. Återkallelse via YAML/import eller återöppning av terminal post får inte kringgå kärnans särskilda flöde. Prov i A1.
4. Första kartläggning utan plan ska fungera, medan flera aktiva planer aldrig får genomföras implicit. Prov i A2 och A3.
5. Ändrade kandidater efter formulärets visning eller avbruten profilsparning får inte lämna falsk historik. Prov i A1 och A3.

## Filer och ansvar

| Fil | Ansvar |
|---|---|
| `src/riskanalys/profil/modeller.py` | `Planaterkallelse`, `Planval` och planens ömsesidigt uteslutande terminalposter. |
| `src/riskanalys/profil/planlivslopp.py` | Aktivitet, bevarat innehåll och rena avslutsbyggare. |
| Ny `src/riskanalys/profil/planval.py` | Typat införandebehov, kandidater och valprövning utan I/O. |
| `src/riskanalys/profil/forandringar.py` | Lås, historiskt nej, CAS och en enda profilsparning. |
| `src/riskanalys/profil/planering.py`, `src/riskanalys/intag/utvardering.py`, `src/riskanalys/profil/text.py` | Spärrar, utvärderingsstatus och textvalidering. |
| `src/riskanalys/intag/{tjanst.py,planeringsvy.py,tjanstvy.py,webb.py}` | Återkallelse och planval vid enskilt/samlat erbjudande. |
| `src/riskanalys/kommandon/{profil_kommando.py,drift_kommando.py}` | CLI till samma kärna. |
| `src/riskanalys/dokument/forandringar_v8.py` | Återkallad historik i B1. |

Nya namn nedan är planerade gränssnitt. Behåll befintliga namn och beteenden utöver uttryckligt angivna kontraktsändringar.

## A1 Återkallelse som terminal historik

**Files:** Ändra `profil/{modeller.py,planlivslopp.py,forandringar.py,planering.py,text.py}` och `intag/utvardering.py`. Skapa `tester/enhet/test_planaterkallelse.py`; utöka `tester/enhet/test_planens_livslopp.py` och `tester/enhet/test_planens_genomforande.py`.

**Interfaces:**

- `Planaterkallelse`: `datum: date`, `ansvarig: str`, `motivering: str`, `fore_revision: str`, `planinnehallssumma: str`. Använd samma längdgränser som genomförandets ansvarig/utvärdering: 200 respektive 12 000 tecken, icke blank text och XML-säkerhet. `Tjansteplan.aterkallelse: Planaterkallelse | None = None`; validator förbjuder samtidig `genomforande`.
- `Planval`: fryst modell med `tjanst: str`, `plan_id: str`; samma ID-regler som befintlig plan. Urvalets unika tjänster valideras i A2.
- `aktiv_plan(plan: Tjansteplan) -> bool` i `planlivslopp.py` är sann endast när båda terminalposterna saknas.
- `med_aterkallelse(profil: Profil, plan_id: str, datum: date, ansvarig: str, motivering: str, fore_revision: str) -> Profil` är ren och kontrollerar aktiv plan, datum senast idag och text.
- `aterkalla_plan(mapp: Path, rb: Regelbas, plan_id: str, datum: date, ansvarig: str, motivering: str, revision: str) -> Profil` i `forandringar.py` låser, läser och CAS-sparar en gång. Ingen bunden utvärdering krävs för att överge en ännu inte genomförd plan.

- [ ] **1. Skriv reproducerande prov.** Återanvänd `profil`, `plan`, `ja`, `DAG`, `upp`, `utvardering` i `tester/enhet/test_tjansteplanering.py`. Utöka hjälparna med uttryckligt `Planval` först i A2; försvaga inga befintliga påståenden. Lägg fallen `test_aterkallad_plan_utgar_ur_aktuell_planprovning`, `test_terminal_plan_far_inte_aterkallas_eller_genomforas`, `test_import_far_inte_skriva_terminal_historik`, `test_aterkallelsens_utvardering_bevaras_men_galler_inte` och `test_skrivavbrott_bevarar_aktiv_plan`. Första fallet prövar att en återkallad gammal plan inte längre räknas aktiv eller bidrar med ett planhinder; det fullständiga nya införandet provas med A2:s spargräns. Kräv oförändrad historik och årsfrist samt att tomt nytt fält inte ändrar äldre bytes eller innehållssummor.
- [ ] **2. Kör RED:** `.venv312/bin/python -m pytest tester/enhet/test_planaterkallelse.py -q`. Förväntat: saknat återkallelsegränssnitt eller återkallad post räknas aktiv; inte miljö-/importfel i befintlig kod. Bevara före-rättningens reproduktion i körloggen.
- [ ] **3. Implementera gränssnitten.** Utelämna tom återkallelse vid serialisering; planens egen innehållssumma undantar båda terminalposterna. Använd `aktiv_plan` i spärr, genomförande och aktuell planutvärdering. Avvisa ny utvärdering för återkallad/genomförd plan. Vanlig profilsparning får varken lägga till, ändra, radera eller återöppna terminalmetadata. Terminal post valideras mot sitt bevarade innehåll, även om tjänst/fält senare saknas i katalogen. Ingen ny separat historikskrivning som kan lyckas före profilsparningen.
- [ ] **4. Kör GREEN:** samma nya testfil samt `tester/enhet/test_planens_livslopp.py`, `test_planens_genomforande.py`, `test_tjansteplanering.py`, `test_historik.py`. Alla valda prov ska passera. Bekräfta att framtida datum, blank motivering/ansvarig och båda terminalposterna avvisas. Oberoende uppgiftsgranskning ska särskilt kontrollera import och avbrott; ingen commit före A3:s fullsvit.

## A2 Uttryckligt planval i spargränsen

**Files:** Skapa `profil/planval.py` och `tester/enhet/test_inforandeval.py`; ändra `profil/{forandringar.py,planering.py}`, `intag/tjanst.py` och berörda befintliga testhjälpare för giltiga införanden.

**Interfaces:**

- `Inforandebehov`: fryst dataclass med `tjanst: str`, `kandidater: tuple[str, ...]`.
- `inforandebehov(rb: Regelbas, fore: Profil, efter: Profil) -> tuple[Inforandebehov, ...]` använder kompatibilitetsvyer. Kräver val vid bekräftat/historiskt nej till ja; även ett uttryckligt införande med registrerad aktiv ny-tjänst-plan ska ha valt plan-ID. Första okänt till ja utan registrerad införandeavsikt är kartläggning. Genomförd/återkallad post är aldrig kandidat.
- `validera_planval(rb: Regelbas, fore: Profil, efter: Profil, val: tuple[Planval, ...]) -> dict[str, Tjansteplan]` kräver exakt ett aktivt `ny_tjanst`-val per införandetjänst och avvisar dubletter, främmande tjänst, fel typ och val för oförändrat erbjudande. Ingen automatisk första/enda-kandidat i kärnan.
- `inforandebehov_for_andring(mapp: Path, rb: Regelbas, efter: Profil, revision: str) -> tuple[Inforandebehov, ...]` i `forandringar.py` gör skrivfri förhandsprövning med CAS och `_tidigare_nej`. Den är vägledning för UI; samma kontroll görs igen under sparlåset.
- Utöka `spara_andring(..., *, rattelse=None, lokalt_underlag=False, planval: tuple[Planval, ...] = ()) -> Profil` samt `Intagstjanst.spara`/`spara_flera` med keyword `planval`. Lägg `Intagstjanst.planbehov(svar: tuple[IntagSvar, ...], revision: str) -> tuple[Inforandebehov, ...]`; beräkna efterprofil genom befintlig `besvara` utan sparning.

- [ ] **1. Skriv RED-prov:** `test_bara_vald_plan_genomfors` ska ha två giltigt utvärderade aktiva planer för samma tjänst, välja den andra och kräva att första förblir aktiv. `test_flera_eller_en_kandidat_utan_val_sparar_inget`, `test_fel_tjanst_typ_eller_terminalt_val_avvisas`, `test_alias_och_historiskt_nej_kraver_val`, `test_forsta_kartlaggning_kraver_inte_plan` och `test_aterkallad_plan_bar_inte_val` spikar övriga fall. Lägg `test_aterkallad_plan_sparrar_inte_nytt_inforande`: återkalla den övergivna planen, välj en ny giltigt utvärderad plan och spara införandet; bara den nya blir genomförd. Ett saknat val får inte ändra profil, historik eller genomförandeposter.
- [ ] **2. Kör:** `.venv312/bin/python -m pytest tester/enhet/test_inforandeval.py -q`. Förväntat RED på saknat planvalsgränssnitt/automatisk markering av alla, inte på testets underlagsbindning.
- [ ] **3. Implementera.** Ersätt loopen som genomför alla aktiva nya-tjänst-planer med de validerade valen. Bunden utvärdering ska gälla efterprofilens sakunderlag; normaliseringen för förväntad inaktualisering av erbjudandets följdsvar behålls. Övriga aktiva planer behålls och deras befintliga prövningskrav upphävs inte. Felregistreringsrättelse kan inte kombineras med ett verkligt införandeval för samma rad. Förhandsgranskning håller inget lås över en mänsklig väntan; sparning läser om allt under lås.
- [ ] **4. Kör** de nya proven och samtliga plan-/historikprov från A1. Testa även ändrat kandidat-ID efter visning och inaktuell utvärdering. Uppdatera positiva befintliga införandetester så att de gör det nya uttryckliga valet; gamla negativa kontroller ska fortsätta avvisa samma kringgåenden. Granska uppgiften före A3.

## A3 Webb, CLI, rapport och leverans

**Files:** Ändra `intag/{planeringsvy.py,tjanstvy.py,webb.py,tjanst.py}`, `kommandon/{profil_kommando.py,drift_kommando.py}`, `dokument/forandringar_v8.py`, `docs/kravstod.md`, `docs/STATUS.md`. Utöka `tester/intag/test_tjansteplanering.py`, `tester/enhet/test_profil_kommando.py`, `tester/enhet/test_arb_v8.py`, `tester/intag/test_skyddad_begaran.py`; skapa `tester/intag/test_tjansteurval_planval.py`.

**Interfaces:**

- CLI: `aterkalla-plan BYRA PLAN --ansvarig TEXT --motivering TEXT [--datum ÅÅÅÅ-MM-DD] [--regelbas PATH]`; `bekrafta ... --plan PLAN_ID` för enskilt införande. Befintligt `genomfor-plan` avvisar återkallade planer.
- HTTP: ny skyddad `POST planaterkalla` med `csrf, revision, plan_id, datum, ansvarig, motivering`. `POST svar` får valfritt `plan_id`; `POST tjanster` tar strikt mappade `plan_<tjanst-ID>` för de införanderader som A2 visar. Okända fält/dubbletter avvisas.
- Tjänstelistan visar planval vid berörd rad och behåller samtliga inskrivna värden/belägg i kompletteringssteget. Förhandsvisning sparar inga erbjudanden. En kandidat föreslås men kräver explicit bekräftelse; flera kräver val. Efter skapad/utvärderad plan jämförs den nya profilen med de bevarade formulärvalen före slutlig bekräftelse.

- [ ] **1. Skriv integrationsprov före UI-koden.** `test_tva_inforanderader_med_ett_fel_sparar_inget` kräver oförändrad profil/historik för hela batchen. `test_planval_visas_per_rad_och_belagg_bevaras` följer lista → komplettering → bekräftelse och kräver exakt valda genomföranden. Lägg CSRF/origin, stale revision, återkallelse via webb/CLI och läsbar terminal sida utan redigerings-/utvärderingsformulär. B1 ska visa återkallad, datum, ansvarig och motivering samt gamla utvärderingar som historik. AI-provet jämför hela begäran inklusive omförsök med/utan återkallelse/planval.
- [ ] **2. Kör RED:** `.venv312/bin/python -m pytest tester/intag/test_tjansteurval_planval.py tester/intag/test_tjansteplanering.py -q`. Tillåt loopbackbindning i miljöer där den kräver särskilt verktygstillstånd. Förväntat nya rutter/planval saknas; befintliga skydd förblir gröna.
- [ ] **3. Implementera** rutter och kommandon med A1/A2, befintliga formulär-/textskydd, ingen parallell sparväg och ingen delvis sparning. Sätt tjänstelistans formgräns till 64 fält för urval och planval; prova legitimt maximalt urval och avvisning över gränsen. UI guidar till saknade val; direkt ogiltig POST avvisas fortfarande. Terminala planer läses utan att kräva dagens katalogfält. Dokumentera uppgraderingens nya modellidentitet och att aldrig automatiskt anta återkallande utifrån ålder/datum.
- [ ] **4. Verifiera riktat** alla A-prov, AI-provet, profil-CLI, historik och V8. Exportera syntetisk återkallad plan och vald genomförd plan; rendera och öppna berörda rapportsidor. Gör en mänskligt läsbar loopbackkontroll av flerplansvalet med syntetisk byrå. Redovisa vad som faktiskt kontrollerats.
- [ ] **5. Leveranskontroll och commit.** Kör `.venv312/bin/python -m pytest -q`, `.venv312/bin/riskanalys regelbas validera`, `git diff --check`. Alla valda prov ska passera, inga verkliga API-anrop. Spara SHA, Python-version, exakta utfall och eventuell reparationshistorik i `docs/superpowers/reviews/2026-10-22-planlivslopp-slutprov.md`. Bevara loggar utanför versionshanterad byrådata. Granska hela rättningen och committa först när inga blockerande fynd återstår, exempelvis `fix: stöd återkallade planer och uttryckligt införandeval`. Pusha/merga inte som del av denna plan. Skriv det faktiska produkt-SHA:t som B-planens bas.

## Klart för nästa leverans

Den fristående planrättningen är klar först när en återkallad plan inte spärrar ett giltigt nytt införande, bara valt plan-ID blir genomfört, årsfrist/historik bevaras och UI/CLI använder samma atomiska gräns. Ett grönt testresultat för basen `91a3ece` räknas inte som verifiering av denna nya rättning.

## Genomförande 2026-10-22

A1–A3 är implementerade och tekniskt slutverifierade: 3 063 passerade, ett bortvalt livetest, exit 0 på Python 3.12.15. Den frysta filförteckningen, regelbasvalideringen och diffkontrollen passerar. [Slutprovsrapporten](../reviews/2026-10-22-planlivslopp-slutprov.md) redovisar RED/GREEN, två verifierade följdrättningar, webbprov och riktad visuell kontroll av Word-bilagan. Ursprungliga plansteg behålls ovan som granskningskontrakt; faktisk körstatus finns i rapporten. Användaren granskar den samlade leveransen med Claude enligt valt arbetssätt. Plan B är inte implementerad i denna leverans.
