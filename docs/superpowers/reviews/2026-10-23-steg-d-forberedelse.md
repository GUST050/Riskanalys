# Steg D – förberedelse och beroenden

Detta är förberedelse, inte genomförda metodbeslut. Ordningen i uppdrag revision 3 är C → del 3 med PDF-kontroll och produktintegration → D → nya PDF:er → E. C är sparat som `6a83ffd`, regelbas 2.2.0. Del 3 inväntar användarens fyra dataval. Ingen motor, regel eller sakkunnigstatus ändras genom denna handling.

## Lästa underlag och deras gränser

- `docs/research/13-scenariomotor-katalog.md`, tabellen D1–D9 och protokollkraven.
- Tidigare beslutsunderlag och jämförelseformulär, båda daterade 2026-10-21, i referensklonens `docs/superpowers/reviews/`. De beskriver hypoteser och experiment, inte godkänt facit. Uppdragets senare tillstånd att bygga provisoriskt med `ej_granskad` gäller för det kommande D-arbetet.
- Nuvarande `bedomning/motor.py`, `scenarier.py`, `analys/riktning.py`, metodtabeller, kataloger, objektattest och modellfilmanifest.
- Källsidor som redan lästs i A–C: vägledningen 2025 s. 16–17 och 23; NRA 2024/2025 kap. 7.19 s. 122–123 samt relevanta skatte-/bolagsavsnitt; Finanspolisens TF-lägesbild 2025 s. 1–2 och 4; Länsstyrelsernas tillsynsrapport 2026:14 s. 7–8. Slutligt beslut ska ange eget kort citat och locator från just den lästa versionen.

Tidigare prov avser 21 hot och 24 prövade enskilda faktorer. Nu finns 26 hot och 33 högre-risk-indikatorer efter B–C. Äldre antal och provresultat får därför inte återanvändas som aktuellt facit. Experimentet med områdesvis påslag räknar katalogområden, vilket inte bevisar oberoende orsaker. Det får inte presenteras som validerad metod bara för att nivåerna varierar mer.

## Genomförandekarta inför besluten

Sökvägarna nedan är relativa till repot. Filreferenser under `bedomning`, `analys`, `profil`, `regelverk` och `drift` avser `src/riskanalys/`.

| Beslut | Nuvarande genomförande och relevanta objekt | Kontrast som måste bevaras och räknas om | Följder vid avslag/ändrat val |
|---|---|---|---|
| D1 Lön–moms | `kataloger/tjanster.yaml`: `T-RED-04` och dess kopplingsmotivering till `H-MOD-02`. `H-MOD-02`, `C-TJ-04`; `bedomning/scenarier.py::bedom_scenarier`. | Ren löneberedning utan moms-/betalningsmoment respektive samma kund med uttryckligt relevant arbetsmoment. Direkt relevans skiljs från indirekt exponering. | Bygg om tjänstens hoturval och lokala scenariokopplingar, ompröva alla referenser till hotet i lön samt V10:s hotantal/matris/motiveringar. Lokal fritext får inte bli motorvillkor. |
| D2 Lön–faktura/intäkter | `T-RED-04`, `H-01`, `H-02`, `C-TJ-04` och dess räckvidd. Samma scenariogenerering som D1. | Falskt löneunderlag; leverantörsfaktura utanför insynen; belagd korskoppling faktura–lön. | Katalogmotivering, relevansspår och lokal kontrollprövning behöver byggas om. Begränsad insyn bevisar varken frånvaro av hot eller belagd kontrollverkan. |
| D3 Portfölj/tjänst | `motor.py::_valda_sarbarheter`, `scenarier.py::_mojliggorande`; `falt.yaml`, `Tjanst.sarbarheter` och de befintliga tjänstefördelningarna. | Samma byråportfölj, men belagd nolla, positiv tjänsteexponering respektive okänd fördelning. Fel period/källa ska förbli okänt. Organisations-/utbildningsfaktorer prövas separat. | Vid tjänstevillkor ändras modellbindningen; härledda andelar, statistikvalidering, lokal riktning och alla sex jämförelsefall måste räknas om. Inga härledda nollor vid saknad fördelning. |
| D4 Överlapp | `Profil.kombinationsgrupper`, `profil/kombinationer.py`, `S-KOMB-01`. Separata marginaltal saknar kundidentiteter. | Samma marginaltal med olika tillåtna kundfördelningar; känd kombinationsgrupp mot okänt kundöverlapp. | Bygg om kombinationsvalidering och redovisning i V10 3.6. Påståenden om gemensamma riskkunder får inte följa av tjänstesummor. |
| D5 Max och bredd | `BT-TJ-01`, `scenarier.py::sammanfatta_scenarier`, `_hogsta`, `_markera_avgorande`; underlagets avgörande före-/efterled. | Ett högt bland många låga, två maxscenarier där bara ett täcks, liten väsentlig exponering. Antal maxscenarier och otäckta led ska synas utan ny byrånivå. | Ny aggregation påverkar motor, underlag, rapportens urval/ordning och samtliga referenser. Vid bibehållen maxregel kan bredd redovisas utan ändrad nivå. |
| D6 TF | `BT-TF-01`, nio riskmatrisrader, `BT-SANN-02-*`, `scenarier.py::_scenario`, `motor.py::TF_KONSEKVENS`, faktorernas `galler` och hotens `dimensioner`. | Alla nio celler; PT-faktor med/utan belagd TF-kedja; känt TF-modus; belagd respektive okänd TF-kontroll. | Konsekvens, faktortillämplighet och kontrollreduktion är olika beslutspunkter och får inte blandas. Alla TF-led samt V10:s aktuella metodförklaring måste räknas om. TF behöver inte vara lägre än PT. |
| D7 Ideell/H-03 | `S-ARB-05`, `H-03`, `H-TF-*`, faktorernas dimensions-/hotkopplingar och `scenarier.py::_mojliggorande`. | Ideell ensam, PEP ensam, båda med känt respektive okänt överlapp. | Ompröva PT och TF var för sig; redovisa varje sänkt scenarioled. Bevarad historisk nivå är inte bevis för rätt nivå. |
| D8 Kontrollmål | `BT-KVAR-03`, `C-TJ-*` med mål och räckvidder, `motor.py::_kontroll`, `scenarier.py::_tackande_kontroller`/`_kvarstaende`, lokal reduktionsprövning i `analys/provning.py`. | Fel tjänst/rätt hot; rätt mål/okänd effekt; smalt stickprov; ett otäckt maxhot; C-TJ-08/09:s gamla PT-mål. Kontrollernas nya MOD-mål får inte utvidgas för att ge lägre max. | Ändrad katalogräckvidd eller avdragsregel kräver ny objektattest, modellbindning och lokala effekt-/täckningsprov. Redovisa mekaniskt motoravdrag separat från godtaget lokalt avdrag. |
| D9 Summering/tak | `BT-SARB-01`, `Sarbarhet.effekt`, `ersatter`, villkor i `sarbarheter.yaml`, `motor.py::_utan_ersatta`, `scenarier.py::_mojliggorande`/`_scenario`, `analys/riktning.py`. | Samma bakomliggande orsak med två indikatorer; två belagt skilda orsaker; ersättning över olika hot/dimensioner; en kontra många faktorer vid tak; enmansbyrå med olika kontrollarbetssätt. | Ändrade vikter/trösklar kräver nytt fryst facit och omräkning av alla sex fall. Områden är inte självständiga orsaker. Avslag ska kunna återföra just beslutet utan att B:s juridiska precisering av distansidentifiering går förlorad. |
| Lägre risk | `L-PTL-04-01`–`05`, centrala landbedömningar och `nivaeffekt=false`; egen tabell i V10 3.8. | Relevant/irrelevant, känd/okänd hemvist, saknat landunderlag, överlapp med högre risk och dubbelräkning med kontroll. | Ingen nivåeffekt innan relevans, överlapp och kontrollräkning är prövade enligt beslut. Även valet att bara redovisa behöver eget granskningsobjekt och förklaring. |

För D4 är nedre gränsen i det tidigare räkneexemplet endast ett villkorat mängdpåstående: 60 kunder, exakt 96 kund–tjänstkopplingar och högst fyra tjänster per kund ger minst 12 kunder med flera tjänster, eftersom högst tre extra kopplingar kan bäras av en kund. Det anger inte vilka kunder, deras riskfaktorer eller faktiskt överlapp. Population och fullständighet måste vara kända innan något sådant gränsvärde visas i en rapport.

## Objektattest och modellbindning

Nuvarande `regelverk/sakkunnig.py::granskningsobjekt` binder katalogposter, räckvidder, metodregler och kundmallar till innehållssummor. `drift/modellidentitet.py` binder den körbara modellen separat. Enbart en ny beslutsbeskrivning eller ett nytt D-ID i guiden skulle därför inte uppfylla uppdraget.

Vid D:s implementation behövs följande, inom respektive besluts arbetscommit:

1. Ett typat granskningsobjekt per D-ID och ett för lägre risk, med provisoriskt valt alternativ, källor/locator, skäl/osäkerhet, exakt objektförteckning samt berörda modellfilers kontrollsummor. Ingen verklig sakkunnig eller beslutsansvarig fylls i av AI.
2. Laddning, validering, export, import, attestapplicering och fastställelseprövning måste omfatta dessa objekt. Gamla regelbaser utan beslut behåller äldre serialisering/summor. Oregistrerade eller ändrade genomförandefiler ska inte kunna döljas bakom oförändrat D-ID.
3. Innehållssumman får inte vara självberoende. Katalog-/regelreferenser och filhashar ska bindas utan att beslutets egen kontrollsumma ingår i sin indata. Beslutens metadata får inte ge cirkulära kontrollsummor.
4. Om ett senare beslut ändrar en gemensam modellfil uppdateras de tidigare beslutens berörda filbindningar; de förblir `ej_granskad`. Följdändringen ska synas i beroendeförteckningen och räknas som ombindning, inte som ett nytt sakkunnigbeslut.
5. Varje avslag beskriver konkret vilka objekt, facit, analys-/skriv-/rapportartefakter, PDF:er och sakkunnigpaket som blir inaktuella. En `git revert` ensam är inte ett återföringsförfarande.

Befintlig modellvalideringsrapport och dess attest ska fortfarande krävas där produktkedjan kräver dem. D-objektet ersätter inte den prövningen.

## Före-/efterunderlag

Behåll de sex oföränderliga B-profilerna och deras 2.0.0-föreutfall. C:s fullständiga 2.2.0-snapshot finns i `.superpowers/evidens/2026-10-23-regelbas-c-rapport-d-e/regelbas-c.json`; C:s jämförelse visar identiska motorutfall mot B för de sex fallen och 27 erbjudna tjänster.

För varje D-beslut sparas separat: regelbas före/efter, modellfilsmanifest, exakt samma profilbytes, hela tjänste-/scenarioutfall och diff. Därtill behövs beslutets egna kontrastprofiler. Jämförelsen ska ange PT/TF, sannolikhet, konsekvens, inneboende och kvarstående där beräknat, kontrollmål och lokal godtagbarhet. Alla sänkta led listas även när tjänstens maxnivå är oförändrad. Efter sista beslutet upprepas jämförelsen samlat mot 2.0.0.

De tidigare experimentskripten muterar moduler i minnet. De kan användas som historiskt diskussionsunderlag, men slutligt facit ska använda den faktiska laddade versionsbundna implementationen utan sådana experimentkopplingar.

## Nästa bindande steg

Denna förberedelse gör inte D körklart före rapportdelen. Först inväntas datavalen, sedan byggs den konkreta V10-rapporten offline och användaren läser PDF:erna. Efter godkänd produktintegration väljs och genomförs ett provisoriskt metodbeslut åt gången, med egen regelversion, commit och effektredovisning. Tester samlas till slutet enligt användarens instruktion; inget påstående om grön slutverifiering görs före faktisk full körning.
