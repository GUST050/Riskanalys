# Plan: myndighetsdata i byråintaget

**Mål:** hämta avgiftsfria SCB-uppgifter till lokala, källbundna förslag och minska dubbel inmatning utan att tillskriva registret faktisk verksamhetskunskap. Användaren har begärt research och implementation, utan befintlig API-åtkomst.

**Beslut:** SCB AFR v1 enligt officiell OpenAPI och variabelbeskrivning kontrollerade 2026-10-10. Personlig nyckel via lokal miljövariabel; inget konto skapas. Lokalt importerat SCB-JSON är ett alternativ, tydligt märkt som ej verifierat ursprung. Bolagsverkets HVD blir nästa adapter när dess tekniska kontrakt och åtkomst verifierats. Inga Allabolag-anrop eller webbskrapning.

Registerdata lagras separat från profilen, privat utanför Git. Bara namn, säteslän och antal registrerade arbetsställen kan överföras efter explicit bekräftelse genom ordinarie typning och beroendehantering. Anställdas/omsättningens klasser, år, SNI, juridisk form och status är bakgrund, aldrig exakt antal, erbjudna tjänster eller risknivå. Inga råa registeruppgifter går till AI.

## Uppgifter

- [x] 1. Kontrakt och SCB-klient (`foretagsdata/modeller.py`, `scb.py`, tester): juridiskt organisationsnummer, Luhn och peOrgNr=16+nummer; identitetskontroll, strikt projektion, begränsad HTTPS-transport utan omdirigering och redigerade fel. Saknad nyckel ger användbar instruktion, inga nätanrop.
- [x] 2. Privat lagring och bekräftelse (`foretagsdata/lagring.py`, `intag/register.py`, tester): frysta ögonblicksbilder med summa och tid, CAS vid överföring, skydda bekräftade svar från hämtning, visa avvikande värden; ordinarie svarshantering vid uttrycklig bekräftelse, kontroll av gammalt underlag och byråidentitet.
- [x] 3. Lokalt formulär (`intag/registervy.py`, `webb.py`, `vyer.py`, tester): organisationsnummer och hämtknapp före/efter start, filimport via JSON-text utan godtycklig lokal filläsning, källa/tid/år och skillnader, säteslän föreslås vid start; användaren väljer och bekräftar förslagen. Befintliga manuella frågor och webbskydd kvarstår.
- [x] 4. Dokumentera hämtas/frågas, nyckelregistrering och begränsningar i befintlig spec/research/README/STATUS. Färsk helsvit, regelbasvalidering, webbläsarprov med syntetisk transport och fristående slutgranskning.

## Gränssnitt och verifiering

`SCBLeverantor.hamta(orgnr) -> Registerbild`. `tolka_scb(data, orgnr, ursprung) -> Registerbild` används av nätanrop och lokal JSON-import. `spara_bild(mapp,bild)` bevarar oföränderliga snapshots och aktuell pekare under lås. `bekrafta_register(tjanst,bildsumma,falt,roll,datum,revision)` läser exakt snapshot, kräver explicit rätt-byrå-bekräftelse i HTTP-flödet och sparar vanligt `IntagSvar`.

Tester använder syntetiska identiteter, riktig modell/lagring/server och endast falsk nättransport. Negativa fall: fel nummer, fel identitet, överstor/ogiltig respons, omdirigering, nyckel i fel, saknade värden, historisk omsättning, redan bekräftade uppgifter, samtidiga flikar och ändrat säteslän. Heltesterna ska fortsatt bevisa tom profil → Word och fastställelsegrindar. Live SCB-anrop kan inte verifieras utan personlig nyckel; redovisas separat.

Ingen commit/push ingår i uppdraget. Oberoende slutgranskare ska främst kontrollera källbevis, feltolkade klassuppgifter, identitetskoppling, profilinvalidering och skydd för hemligheter.

## Genomförande 2026-10-10

Uppgift 1–3 implementerade med test först. Före implementation fallerade import/klient-, lagrings- och HTTP-proven mot de saknade gränssnitten. Färsk fokuserad körning efter sluträttelser: **57 passerade, 8,44 s**. Klienten använder exakt officiell v1-path och personlig header; identitet, Luhn, begränsad respons, minimal projektion och inga omdirigeringar är prövade.

Självgranskning hittade felbehörighet för byråmappen före profil och skadad registerbild som kraschade även felrenderingen. Båda reproducerade före rättning och har regressioner. Namn med XML-ogiltiga kontrolltecken avvisas. Fristående granskning hittade dessutom obehandlade HTTP-protokollfel och UTC-datum som kunde bli fel svensk dag vid midnatt. RED→GREEN för båda: HTTPException redigeras vid öppning/läsning och hämtningsdag konverteras till Europe/Stockholm i båda överföringsvägarna. Återgranskaren verifierade de fem relevanta regressionerna och fann inga kvarvarande konkreta P1/P2 i granskade registerflödet.

Verkligt webbläsarprov med syntetisk transport: hämta nummer → visa klasser/år och förslag → bekräfta rätt byrå och säteslän → starta profil → bekräfta namn/arbetsställen → omladdning bevarar svar → nästa fråga kräver verkligt personantal inklusive ägare. Privata syntetiska data i `/tmp/riskanalys-register-syntetiskt-prov`; provbild utanför Git i `../underlag/register-syntetiskt-prov-2026-10-10.png`. Inga riktiga byråuppgifter eller API-nycklar användes.

Regelbasvalidering: giltig `1.1.0`, 107 krav, 11 tjänster, 201/201 paragrafer per län; status fortsatt ej_granskad. Bolagsverket HVD och Allabolag är inte byggda adaptrar. Juridiska organisationsnummer stöds i första connectorn; enskilda firmor använder ordinarie intag manuellt. Autentiserat SCB-uppslag återstår när en personlig nyckel finns.

**Färsk slutverifiering:** `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest -q` gav **938 passerade, 1 livetest bortvalt, 454,56 s**, exitkod 0. Det omfattar 57 nya registerprov, föregående intags tom-profil→Word-flöden och hela M0–M2-sviten inklusive negativa fastställelseprov/återställning. Regelbasvalidering, `compileall` för berörda moduler och `git diff --check` passerar. Kod och data har inte ändrats efter denna helsvit; bara verifieringsnoterna uppdateras. Ingen installation, ingen personlig API-nyckel, inget autentiserat SCB-anrop, ingen commit och ingen push.

## Efterföljande Claude-granskning 2026-10-10

Tidigare helsvit och granskningsomdöme gäller den då provade versionen och avgränsningen. Senare Claude-fynd är nu rättade och redovisas per punkt i [intagsplanens rättningslogg](2026-10-10-intag-och-hel-riskbedomning.md#claude-granskning-och-rättelser-2026-10-10). Registerstart kräver egen filialkälla och ny hämtning/import efter bedömningsdatum avvisas utan att ersätta tidigare bild. Djupt JSON ger åtgärdbart fel. Kodtabellerna har återkontrollerats mot officiella PDF:n och var korrekta. Fullsvit på slutlig kod redovisas nedan.

Nästa bygge börjar enligt användarens beslut 2026-10-11 med ett **manuellt pilotintag för pilotbyrån**. Inventera vilka exporter som faktiskt finns, deras kolumner, perioder och definitioner; bevara pilotunderlaget utanför Git. Bygg därefter CSV/XLSX-import för det verifierade formatet, med period/bolag/källa och tydlig bekräftelse av förslagen. En generell import ska inte byggas före detta pilotprov. Bolagsverkets digitala årsredovisningar kan följa efter verifierat kontrakt. Se [research 10, avsnitt 14.2](../../research/10-kallkontroll-och-gapinventering-m2.md#142-utvidgad-research-mindre-manuell-inmatning-2026-10-10). Pilotintaget och den nya importen är ännu inte genomförda.

**Slutverifiering efter Claude-rättningarna och län/paket-återgranskningen:** 959 passerade, 1 livetest bortvalt, 465,53 s, exitkod 0. Regelbasvalidering, compileall och diff --check passerar. Detaljer om första fullsvitens fel, båda nya länregressionerna och den fristående återgranskningen finns i intagsplanens rättningslogg. Bara dokumentationsnoter ändrade efter sista helsvitens start. Ingen autentiserad livehämtning, installation, commit eller push.

## Datumoberoende återprov 2026-10-11

Registerprovens fasta bedömningsdag blandades med verklig körningsdag. En lokal testklocka låser nu båda till samma syntetiska dag och behåller olika tidsstämplar för successiva hämtningar. Historik-, framtids-, midnatts- och konfliktgrindarna är oförändrade. [Intagsplanens återprov](2026-10-10-intag-och-hel-riskbedomning.md#datumoberoende-prov-och-cli-längdfel-2026-10-11) beskriver RED/GREEN och simulerade omgivningsdatum 2025/2030.

**Färsk helsvit:** ordinarie `.venv/bin/pytest` utan AI-/SCB-nycklar gav **965 passerade, 1 livetest bortvalt, 458,81 s**, exitkod 0. Logg: `/tmp/riskanalys-2026-10-11-full-pytest.log`. Regelbasvalidering, compileall och diff --check passerar. Ingen commit/push. Verklig pilot och autentiserad API-åtkomst återstår.

## Förenklat godkännandeflöde 2026-10-11

Användaren har godkänt flödet organisationsnummer → granska hämtade förslag → godkänn → komplettera luckorna och begärt research, robusthet och snabbare användning. Arbetet sker i befintligt smutsigt arbetsläge utan commit/push. Verkliga svar från pilotbyrån och den körande pilotservern lämnas orörda.

- [x] Samlad registerstart och samlad bekräftelse av valda namn/län/ställen. Ordinarie svarshantering i minnet, ett CAS-sparande; uttryckligt ersättningsval för avvikelser. Omarkerade uppgifter bevaras.
- [x] Samla de elva tjänsteutbudsfrågorna med gemensam källa/roll/datum, uttrycklig bekräftelse av hela listan och enskilt läge för osäkra svar.
- [x] Visa sparade registerförslag även från motsvarande ordinarie fråga; föreslå tidigare funktion, visa källa/datum automatiskt och minska upprepade formulär.
- [x] Visa bekräftade uppgifter och frågor som kan besvaras nu. Fullständighetsgrinden behålls. En profilläsning per fråge-/översiktsrendering och kompatibilitetsvy utanför tabell-loopen; benchmark med samma syntetiska HTTP-fall före/efter.
- [x] F-skatt/moms/arbetsgivarstatus från befintligt verifierat SCB-svar som bakgrund, versionshanterad snapshot med bevarade v1-summor. Nyckel kan anges i lokalt lösenordsfält för sessionen; aldrig återsändas eller sparas i profil/snapshot.
- [x] Negativa regressioner först, webbläsarprov med syntetisk transport, fristående slutgranskning och helsvit. Ny forskning i befintlig researchsammanställning.

Avgränsning: ingen ny Bolagsverket-integration innan separat åtkomst och körbart kontrakt verifierats. Ingen generell CSV/XLSX-import före inventerad export från pilotbyrån. Inga nya riskmetodregler, inga implicit bekräftade kontroller, inga personuppgifter till AI.

### Genomförandelogg för förenklingen

- Samlad start/bekräftelse, konflikters ersättningsval, ordinarie validering i minnet och en CAS-sparning är införda. Den första gruppen gav 7 röda/1 grönt prov innan implementation. Skattestatus/v1-proven gav 2 röda och sessionsnyckelprovet 1 rött. Tre nya tjänsteprov gav först 3 röda.
- Fristående slutgranskning identifierade markörfri registerstart som P2 och rollförslag i fältordning som P3. Båda reproducerades i två röda regressioner. Starten kräver nu urval inklusive säteslän; äldre county-only- och filialkällprov har fått explicit länmarkör och behåller sina ursprungliga säkerhetsassertioner. Sessionen föreslår senaste framgångsrikt sparade roll, utan att ändra andra svar. 98 berörda prov passerade därefter (34,85 s).
- Sista HTML-kontrollen fångade dubblett-ID:n när samlad och enskild tjänsteform visades samtidigt. Ett rött etikettprov blev grönt med separata ID:n. Alla 23 nya samlat-prov passerade (22,42 s). Den då pågående preliminära helsviten avbröts efter 470 passerade/1 bortvalt (56,76 s) för denna rättning. Slutlig helsvit startades om på slutlig kod.
- Webbläsarprov med syntetisk transport: nummer → samlad start av namn/län/ställen → personantalfrågan utan dubbel namnfråga → två erbjudna tjänster och uttryckligt nej för övriga → sparande och omladdning → registerjämförelse bevarar svar → expanderad F-skatt/moms/arbetsgivarstatus. Slutlig layout har tjänster i två kolumner och unika formuläretiketter. Bildbevis ligger utanför Git i `/Users/gt/.codex/visualizations/2026/10/11/01a12a55-3718-74f2-bc3b-588e958dab72/intag-register.jpg` och `intag-tjanster.jpg`. Ingen autentiserad SCB-, AI- eller pilotbyrådata användes.
- Lokal HTTP-benchmark: sex fall ×100 mätningar, median 8–47 % kortare svarstid, med begränsningar och fulla data i [research 10 §14.3](../../research/10-kallkontroll-och-gapinventering-m2.md#143-ny-källkontroll-och-förenklat-godkännande-2026-10-11). Ingen generell beläggcache; ingen uppmätt snabbare extern SCB-tjänst.
- `riskanalys regelbas validera`, compileall och diff --check passerar. Sakkunnigstatus är fortfarande `ej_granskad`. Ingen commit/push. **Slutlig helsvit:** `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest` gav **990 passerade, 1 livetest bortvalt, 441,32 s (7:21)**, exitkod 0, utan varningar. Logg: `/tmp/riskanalys-smidigt-final-full-pytest.log`. Ingen kod eller testuppsättning ändrades efter slutkörningens start; därefter endast dokumentationsnoter.

## Fortsättning: underlagsval och faktisk leverans 2026-10-11

Användaren frågar om varje fakta behöver en källa, vilka fler källor som bör hämtas och vad intaget faktiskt skapar. Avgränsningen är att minska upprepningar med synliga relevanta förslag, utan att import bli bekräftelse eller kontrollbelägg. Spec revision 16 och [research 10 §14.4](../../research/10-kallkontroll-och-gapinventering-m2.md#144-fler-källor-underlagsval-och-tydlig-leverans-2026-10-11) är uppdaterade; ingen parallell plan skapad.

- [x] RED för enkla verksamhetsfakta med egen kännedom, otillåtna statistik-/kontrollval, tidigare underlag inom samma kategori och exakt period, ogiltiga val, gammal revision, okänt svar och samlad tjänstelista. Kontrollprovets ursprungliga felstavade fält korrigerades till det verkliga fältet och kördes RED innan produktionsändringen. Förväntningar behölls.
- [x] Bygg `intag/underlag.py` och `underlagsvy.py`, integrera i ordinarie/samlat tjänsteformulär och HTTP-sparande. Endast aktuella bekräftade manuella underlag, högst åtta deduplicerade val; färsk profil, kategorigräns, exakt period och befintligt CAS. Statistikperiod föreslås från aktuell bas. Egna äldre formulärklienter fungerar fortsatt.
- [x] Leveranskort på start/översikt samt tydlig skrivrubrik: allmän riskbedömning som Word-utkast. Faktisk exportkedja kontrollerad; inga separata rutindokument/kundbedömningar lovas.
- [x] Kontrollera officiell SCB-definition och `agKat`-kontrakt. Snapshot v3 med villkorat koncernmoder=nej-förslag endast för kod 41. RED→GREEN för HTTP-bekräftelse samt negativa koder, ingen automatisk bekräftelse och exakt bevarad v2-serialisering/hash.
- [x] Inventera Bolagsverket, Skatteverket, Polisen, EU/FATF och egna exporter. Separat BV-åtkomst/maskinellt kontrakt återstår; ny NRA 2026 om juridiska personer är en gapnotering, inte en ändrad fryst riskregel. Pilot- och exportinventering kvarstår före ny CSV/XLSX-import.
- [x] Fristående slutgranskning utan egna kodändringar: inga konkreta fynd i kategori-/period-/CAS-/kontroll-/snapshotgränserna. **83 fokuserade prov passerade (35,50 s)**; alla berörda intags-/företagsdataprov **172 passerade (186,90 s)**. Syntetiskt webbläsarprov verifierade nya förslag, sparad egen kännedom, återanvänt kundunderlag/period och avskild omsättningskälla. Ingen riktig SCB-, AI- eller pilotbyrådata användes.

**Slutlig fullsvit:** `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest` gav **1008 passerade, 1 livetest bortvalt, 466,39 s (7:46)**, exitkod 0, utan varningar. Logg: `/tmp/riskanalys-underlagsval-final-full-pytest.log`. Regelbasvalidering, compileall och diff --check passerar; sakkunnigstatus fortfarande `ej_granskad`. Kod/testuppsättning ändrades inte efter fullsvitens start; därefter endast dokumentationsnoter. Syntetisk provflik/server avslutade. Ingen commit/push; verklig pilotserver lämnad orörd. Samma sparade intags-ID ska återanvändas när användaren startar om, även om stavningen skiljer sig från byråns namn.
