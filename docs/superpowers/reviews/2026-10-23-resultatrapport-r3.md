# R3: fryst presentation och tre Word-delar – underlag till Claude

Datum: 2026-10-23. Kodbas: `35b5be0caeaf41b268f1fca88466d61511c793bd`, gren `codex/kravstod-tjansteexponering`. Detta dokument hör till efterföljande R3-arbetscommit. Ingen push eller merge.

## Avgränsning och klartecken

Användaren skrev uttryckligen ”gå vidare med r3” efter Claudes godkännande av R2. Kontrollsummorna för de godkända R2-PDF-filerna verifierades: fyra tjänster `74c98f3f959d13d9dec6cf5cf66a5047e6177b7b2a17fe07b359bf6c1aeb820f`, betalningsmandat `e0e7c9f81c1d42564e800d7d1f6f752b782bf25c56ae4df543d7f906c7d30a0f`.

R3 är implementerad för granskning. R4–R7 återstår. V8 är fortsatt standard och AI:s skrivformat är V8. Det finns ännu ingen V9-produktkedja för granskning, exportmanifest, sakgranskningsattester, fastställelse eller nedladdning. De nya filerna är syntetiska utkast, inte fastställda paket.

## Implementation

- `leverans_v9.py`: strikt leveransobjekt med datum, bedömnings- och granskningsidentitet, tre versionsbundna filnamn och fast mall för status/inledning/hänvisningar. Version och beslutsorgan måste finnas tillsammans. Slutstatus i en ren renderingsenhet är ingen genomförd fastställelse.
- `presentation_v9.py`: fryser originalens kontrollsummor, urval, transformationer, konstruktionsspår, alla tre text-/tabellvyer, vystruktur, literalpositioner, hänvisningar och fullständiga åtgärds-/fyndkällor efter angiven slutlig fyndlista. Fel källprofil, analys eller bedömning avvisas.
- `rendering_v9.py`: kontrollerar presentation, mall, vyer och frysta listrader före skrivning. Återger bara den frysta texten och tillåtna leveransvärden. Befintliga målfiler skrivs inte över. Det är en renderer, inte den atomiska produktpublicering som ska byggas i R5.
- Delade Word-primitiver får V9-stöd med A4, brödtext 11 punkter och tabeller minst 9,5 punkter. V8:s befintliga policy behålls. Den gamla enkelfilsrenderaren avvisar V9 uttryckligen för att inte tyst tappa tabeller.
- Fullständiga åtgärder och maskinfynd står i B1; huvudrapportens maskinfyndindex hålls isär från analysluckorna. Ingen rekursiv återbyggnad eller ny riskberäkning införs.

## Claudes fyra förfiningar och ett kompletterande fynd

1. Matrisen säger ”Egen mekanism, se R5.4” när tjänsten faktiskt har en annan lokal mekanism. Verkligt saknade, okända och ej relevanta fall märks inte om.
2. Mandatfixturens lönetjänst har en egen full TF-motivering som uttryckligen tar upp betalningsmandatet. Övriga tre tjänsters identiska motivering står gemensamt.
3. Meningen om skilda utfall och kontrollbegränsningar står en gång under tabellen.
4. När R5 redan förklarar varför en sänkning inte godtas används inte också det generiska ”ska prövas separat”. Där inga sådana avslag finns behålls den allmänna kontrollbegränsningen.

Under Word-provet upptäcktes att den lokala H-MOD-01-mekanismen för löner saknades i urvalet eftersom den varken avgjorde nivån eller innehöll en sänkning. Den inkluderas nu som uttrycklig lokal avvikelse enligt befintlig innehållsregel K04. Därmed har även dess matrislänk ett fullständigt scenario i R5. Ett regressionstest skyddar detta. Alla 44 nivåavgörande led och de tidigare kontrollbegränsningarna finns kvar; inga risknivåer eller vikter ändras.

R1/R3:s permanenta ord ”förhandsvisning” är ersatta av neutral text som hänvisar till leveransstatus. Syntetiska prov förblir tydligt märkta UTKAST i sidhuvud och inledning. Offlineverktyget behåller sin separata märkning att ingen fastställelse skett.

## Verifiering

Python **3.12.15**. Reproducerande RED-prov finns för R3-API, de fyra formuleringarna, bindningsavslag, gammal renderer, leveransstatus och den icke nivåavgörande lokala varianten. Efter rättning:

- **78 godkända, 89,60 s:** `test_rendering_v9.py`, `test_resultatrapport_granskningsfynd.py`, `test_resultatrapport_v9.py`, `test_resultatunderlag_v9.py`, `test_rendering_v8.py`, `test_rapportvyer_v9.py`, `test_resultatrapport_offline.py`.
- **140 godkända, 49,709 s:** `scripts/testa.py snabb`. Collection och JUnit matchar, noll fel eller överhoppade prov. Fryst källsnapshot oförändrat efter dokumentationen.
- Samtliga sex DOCX: ordnad följd av all synlig bröd-/tabelltext matchar exakt den frysta presentationen plus tillåtna dekorationer, hänvisningar och listrader. Alla källpekare är giltiga. Profil och motorbedömning är exakt identiska med de godkända R2-källorna.
- Regelbas och riskmodellens `MODELLFILER` är oförändrade. `git diff --check` passerar.

Ingen färsk fullsvit i detta arbetssteg. Fullsvit och produktgrind kvarstår enligt R7 och AGENTS regel 6. Provresultaten ovan ersätter inte den kontrollen.

## Filer och sidkontroll

Byggverktyg: `docs/research/verktyg/resultatrapport_wordprov.py`. Renderare: **LibreOfficeDev 26.8.0.0.alpha0**, build `2c87e51eeaa2b413ff4ae097b2705eea1995d8e5`, via befintligt lokalt dokumentverktyg. Alla huvudrapportens **15 sidor** är visuellt granskade: inga observerade klippningar eller överlappningar, återkommande tabellhuvuden och läsbar textstorlek.

Bilagornas fulla texter, struktur och Word/XML är kontrollerade. Bilagorna är **inte fullsidigt visuellt granskade** och levereras här som Word för fortsatt granskning, inte som layoutverifierade bilage-PDF-filer.

Evidensen ligger lokalt i `.superpowers/evidens/2026-10-23-resultatrapport-r3/` och är Git-ignorerad. Öppna länkarna från denna arbetskopia. De följer inte med en senare Git-push av enbart koden.

### Fyra tjänster

- [Resultatrapport PDF](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r3/fyra_tjanster/rendering/allman-riskbedomning-UTKAST.pdf>)
- [Resultatrapport Word](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r3/fyra_tjanster/allman-riskbedomning-UTKAST.docx>)
- [Bilaga A – analys](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r3/fyra_tjanster/analysbilaga-UTKAST.docx>)
- [Bilaga B1 – underlag](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r3/fyra_tjanster/underlagsbilaga-UTKAST.docx>)

**7 sidor.** PDF SHA-256: `ae3d8958242c43b0dff6be64a9d5733381f20e885af4087ba69ed62d31ec6d9a`.

### Med betalningsmandat

- [Resultatrapport PDF](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r3/med_betalningsmandat/rendering/allman-riskbedomning-UTKAST.pdf>)
- [Resultatrapport Word](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r3/med_betalningsmandat/allman-riskbedomning-UTKAST.docx>)
- [Bilaga A – analys](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r3/med_betalningsmandat/analysbilaga-UTKAST.docx>)
- [Bilaga B1 – underlag](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r3/med_betalningsmandat/underlagsbilaga-UTKAST.docx>)

**8 sidor.** PDF SHA-256: `342449720de2780338cfe4a278f299246eebcd9b0b5c309a68fcb5431ddbc73f`.

## Mätning och begränsningar

| Fall | Kanoniska ord R / A / B1 | Totalt V9 | V8, samma ordkontrakt | Faktiska Word-ord R / A / B1 |
|---|---:|---:|---:|---:|
| Fyra tjänster | 2637 / 13728 / 35794 | 52159 | 49503 | 2736 / 14213 / 36348 |
| Betalningsmandat | 3289 / 14702 / 36888 | 54879 | 51571 | 3388 / 15187 / 37450 |

Kanoniskt kontrakt: titel, stycken och dataceller i de frysta vyerna. Faktiska Word-ord inkluderar dessutom dekoration, tabellrubriker, filhänvisningar och bilagans fulla åtgärdslistor; sidhuvud/-fot ingår inte. Olika kontrakt får inte jämföras som en förkortning. Den korta huvudrapporten uppnås genom disposition; totalen är längre. Ingen total textminskning påstås.

R3:s syntetiska filprov använder en **uttryckligen tom maskinfyndlista**, inte en körd V9-produktgranskning. Icke tomma fulla fyndposter, deras ordning och bindningar prövas i enhetstester. R4 ska skapa den riktiga slutliga fyndlistan och R7 ska mäta de färdiga exporterna igen; sidantalet här är ingen garanti för de kommande produktfilerna. Fri text och erfarenhetstexterna har inte kortats. R6-tabell och koppling genom antaganden har inte införts.

[Kontrollsummor, mätning och provkvitto](</Users/danieltrogen/Documents/ChatGPT/Riskbedömning/Riskanalys/.superpowers/evidens/2026-10-23-resultatrapport-r3/kontroll.json>). Båda fallen innehåller `bygge.json`, `presentation.json`, `leverans.json`, `kallor.json`, `matning.json` och `wordkontroll.json`. RED/GREEN-loggar finns i `.superpowers/sdd/2026-10-22-resultatrapport-plan/`.

## Fokus för Claudes granskning

Kontrollera att alla tre delarna hör ihop, att fullständiga åtgärds-/fyndposter verkligen fryses, att inga ändrade vyer eller mallar kan renderas som tidigare granskade och att V8 inte påverkas. Läs särskilt mandatfallets matrislänkar och hela egna TF-motivering. R4:s granskningsintegration och R5:s atomiska paketexport ska inte betraktas som implementerade av dessa rena renderings-API:er.
