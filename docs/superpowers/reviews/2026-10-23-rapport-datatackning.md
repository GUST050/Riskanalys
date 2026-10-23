# Del 3 – datatäckning och fyra val före rapportbygge

Underlag: uppdrag revision 3, exempelrapportens form, B `902da79` och C regelbas 2.2.0. Exemplet är fiktivt; inga siffror, åtgärdskrav, kundriskpoäng eller antaganden därifrån följer med.

Ingen ny rapportkod är byggd. Tabellen nedan täcker hela dispositionen. Varje återgiven uppgift ska dessutom bindas till sin konkreta källpointer och sitt konstruktionsslag i den nya presentationen. Rapporten använder en ny version; historiska V9-paket och V9-utkast behåller sitt format.

## Mappning av dispositionen

| Plats/uppgift | Befintlig källa | Hantering när underlag saknas |
|---|---|---|
| Faktaruta: verksamhetsutövare | `profil.uppgifter[P-ORG.namn]`, `profil.byra.id` | Okänt namn. Byrå-ID är inte organisationsnummer. |
| Organisationsnummer och registrering i Bolagsverkets register | Egna strukturerade fält saknas. Bekräftad fri verksamhetsbeskrivning kan innehålla uppgiften men får inte maskintolkas som registerbevis. | Okänt. Inga nya fält föreslås utan särskilt beslut. |
| Tillsynsmyndighet | `bedomning.omfattning.paket_id`, regelpaket och den befintliga PTF-/tillsynsområdestabellen | Okänt vid preliminär/motstridig omfattning. Sätets län likställs inte med tillsynsmyndighet. |
| Avser datum | `bedomning.datum`, profilens bekräftade perioder | Datum anges separat från observationsperiod och exporttid. |
| Ansvarig för dokumentet | `P-ROLL.*`, ansvar i lokal analys/bevakning där uppgiften faktiskt är uttryckt | Roll/namn är okänt om uttrycklig dokumentansvarig saknas. Ingen roll gissas från analysförfattaren. |
| Fastställd av/version | Fastställelsebeslut och leveransmetadata vid riktig fastställelse | Utkast: ej fastställd. Exportdatum är inte beslutsdatum. |
| Senaste och nästa utvärdering | `Historik.senaste_utvardering()` och `.nasta_genomgang()` | Okänt när verklig samlad utvärdering saknas. En skrivning eller avgränsad planutvärdering räknas inte som årsutvärdering. |
| Läsanvisning | Programmall för versionens 0–5 samt A/B1 | Mall beskriver endast verkliga delar och avsnitts-ID:n. |
| 0 Slutsats och risktabell | `bedomning.tjanster`, samma `slutsats` och lokala slutsatser som V9 | PT/TF hålls isär; okänd risk får inte sorteras som låg. Risktabellen sorteras deterministiskt högst kvarstående PT, PT före och TF först; inget nytt byråmått. |
| 1.1 Verksamhetens fakta | `P-ORG.*`, `P-VERK.omsattning`, `P-KUND.antal_aktiva/antal_nya/antal_juridisk`, motsvarande härledda andelar, `P-VERK.tidigare_tillsyn`, `P-ROLL.*` | Bekräftat värde med egen period/källa. Antal juniora saknas: endast befintligt ja/nej om självständigt arbete visas. Antal kontor och säteslän blir inte påhittade ortnamn. |
| 1.1 Kunder per riskklass | Ingen kundriskmodell och inga räknarfält | Användarval 2 nedan. Inga riskklasser härleds ur tjänstens nivå. |
| 1.2 Tjänster: vad den innebär, kunder, mandat, insyn, leverans | `regelbas.tjanster`, `P-TJ.<slug>_erbjuds/arbetssatt/antal_kunder/leverans/betalningsmandat/bankinsyn/attest`, lokalt `betalningsinsyn`/`uppdragsprovning` | Skilj befogenhet, faktisk insyn och utförd kontroll. Inte antal kunder med visst mandat om endast en kategorisk mandatfråga är besvarad. |
| 1.2 Bekräftat ej erbjudna tjänster | Varje tjänsts bekräftade erbjudandefält | Endast bekräftat nej. Saknat/okänt listas separat och blir inte nej. |
| 1.3 Omfattning | `bedomning.proportionalitet`, `P-OMFATTNING.motivering`, `bedomning.omfattning` | Hela motiveringen eller tydlig hänvisning till A; rättsliga stödhinder syns. |
| 2 Hot: antal, PT/TF, namn, beskrivning, källor | De erbjudna/okända tjänsternas kataloghot, `Hot.dimensioner`, namn/beskrivning/kallhanvisningar och C:s nivåmotivering | Räkna unika hot och dimensioner separat. Ett hot kan ingå i båda dimensionerna; ingen enkel summering som dubbelräknar. |
| 2.1 Egen erfarenhet | `P-VERK.antal_rapporter/antal_avbojanden`, `P-BESK.erfarenheter`, gemensam erfarenhetspost och tjänsternas erfarenhetsprövning | Noll rapporter är inget frånvarobevis. Period/källa och full fri text bevaras. |
| 3.1–3.5 Alla riskindikatorer | Alla 33 `regelbas.sarbarheter`, typade villkor, `profil.faltvarden()`, tillämpliga tjänsters listor och motorns scenario-/faktorspår | Fem statusar enligt uppdraget. Konservativt motorpåslag vid okända data får inte presenteras som bekräftad förekomst. Områdesnivå enligt val 1. |
| 3 Faktakolumn och förstärkta hot | De faktiska villkorsfälten med period/källa samt tjänstens verksamma hot-/dimensionskoppling | Inga kundidentiteter eller påståenden om samma kunder ur marginaltal. Under-tröskel kräver känd positiv förekomst och relevant tröskel; komplext falskt villkor räcker inte ensamt. |
| 3.6 Samverkan | `S-KOMB-01`, typade villkor/ersättning och `profil.kombinationsgrupper` | Val 4. S-KOMB-01 är en kombination på modell-/byrånivå och bevisar inte att samma kunder har båda faktorer. |
| 3.7 TF-sårbarheter | Faktorer med `galler=bada/terrorfinansiering`, verksamma TF-hot, TF-scenarier och fulla lokala TF-motiveringar | Allmän beskrivning märks som katalog/metod; inte en iakttagen kundhändelse. |
| Lägre risk, egen tabell | `regelbas.lagre_risk`, kundantal och hemvistgrupper, centrala `landbedomningar` | Sverige/EES är inte automatiskt positivt beslut om effektivt AML-system/låg korruption. `underlag_saknas` syns. Relevans/överlapp/effekt följer D:s beslut. |
| 3.8 PTL 2:4, alla fem punkter | `L-PTL-04-01`–`05` och deras faktiska fält/centrala bedömningar | Varje punkt får rad och hänvisning. Saknat landstöd är okänt även med känd hemvistfördelning. |
| 3.8 PTL 2:5, alla tio punkter | p.1 `S-ARB-03`, p.2 `S-KUND-02`, p.3–4 `S-ARB-19/20`, p.5–6 `S-ARB-13/12`, p.7–8 `S-ARB-21/22`, p.9 `S-ARB-08`, p.10 `S-ARB-23` | p.5–6:s befintliga frågor avser bredare anknytning än kundens hemvist. Bekräftad anknytning är inte automatiskt bevis för just lagens hemvistexempel; denna databegränsning ska synas. |
| 4.1 Skalor, matris och metod | Bunden regelbas: metodens skalor/tabeller/förklaringar, konsekvensregler, aggregering och D:s beslut | Inga exempelvärden eller statisk text om TF/reduktion. Åtgärdskrav per nivå införs inte utan beslutad regel. |
| 4.2 Scenariomatris | V9:s befintliga resultatunderlag: varje cells oförändrade `Scenariobedomning`, lokal mekanism, medlemmar och källor | Gemensamma kedjor en gång, lokala avvikelser bevaras; saknas/ej relevant/okänt hålls isär. Oprövade sänkningar märks och förklaras. |
| 4.3 Motivering per tjänst | Befintlig lokal PT-/TF-motivering, sannolikhet, konsekvens, slutsats, scenario, mandat/insyn och exponeringsbelägg | Hela utvalda fria motiveringar återges med författare/status. Exponering kan hänvisas till A. Inga AI-sammanfattningar. |
| 4.4 Kontroller/kvarstående | Katalogens mål/räckvidd, bedömda kontroller, lokal `Kontrollprovning`, reduktionsprövning och metodregler | Utformning/genomförande/effekt skiljs åt. Katalogmål är inte belägg för täckning. TF efter kontroll följer aktuell regelversion. |
| 4.5 Tjänsterisk och kundrisk | Motorutfall per tjänst samt beskrivning av gränsen mot kundriskbedömning | Programmet har ingen kundriskmodell. Inga kundriskpoäng eller automatisk klassning införs. |
| 5.1 Luckor och åtgärder | `Analysgap`, `Rutinatgard`, ansvar, tidpunkt, status/prioritet och befintliga maskinfynd | Öppna/osäkra/beslutade uppgifter hålls isär. Registreringsordning blir inte prioritet. Hela saktexter bevaras. |
| 5.2 Rutinkoppling | `Rutinatgard.rutin_id/rutin_version/rutinbelagg`, åtgärdens frekvens/ansvar samt `P-BESK.rutiner` | Val 3. Saknat rutin-ID/underlag visas som saknat; inget avsnittsnummer hittas på. |
| 5.3 Utvärdering/omvärld | Full `P-BEVAKNING.*`, `P-BESK.uppdatering`, historik och förändringsplaner | Lästa källor skiljs från registrerade källor; faktisk utvärdering från exporttid. |
| 5.4 Versionslogg | `Historik.handelser`, bedömningens regelversion, leverans-/beslutsmetadata när de finns | Inga fiktiva tidigare versioner eller beslut. Utkastets revisions-/exportdatum märks som sådant. |
| A och B1 | Befintlig V8-analysdisposition transformerad till den nya trepartsleveransen | Dispositionen bevaras. Innehållet följer C/D:s regelversion. Råa lokala svar och belägg kapas inte. |

## Fyra val

| Val | Rekommenderat alternativ | Andra alternativet | Nya frågor |
|---|---|---|---|
| 1 Nivå per område | Visa områdets fulla motivering och faktastatus, utan ett nytt nivåord. | Lägg ett uttryckligt manuellt nivåfält på den gemensamma områdesposten, med motivering/författare. Ingen AI-nivå. | 0 respektive ett nivåfält per relevant gemensamt område; tjänstespecifika områden behöver motsvarande explicit källa. |
| 2 Kunder per riskklass | Utelämna raden tills det finns ett eget kundriskunderlag. | Tre nya aggregaträknare för låg/normal/hög, med period/källa och kontroll mot kundbasen samt uttryckligt stöd för okänt. | 0 respektive 3. Detta är statistik, ingen ny kundriskmodell. |
| 3 Rutinavsnitt | Hänvisa till faktiskt angivet rutindokument/ID och version utan avsnittsnummer. | Ny frivillig avsnittshänvisning per åtgärds-/rutinrad, med lokal registrering. | 0 respektive ett fält per rutinrad, inte en ny gemensam uppgift per tjänst. |
| 4 Samverkan | Visa bara belagd modell-/kombinationsgruppssamverkan; annars skriv att underlag saknas och kundöverlapp är okänt. | Utelämna samverkansavsnittet helt när belagt underlag saknas. | 0 i båda alternativen. Inga nya påståenden om samma kunder ur separata antal. |

Alla fyra rekommendationer innebär **0 nya frågor** utöver B:s 56. De kräver användarens val före rapportbygge enligt del 3:s kontrollpunkt 1. Fortsatt C/kartläggning kan ske under tiden. Okända organisations-/registeruppgifter ovan visas som okända; ingen extra kompletteringsintervju smygs in.
