# Slutprov för kravstöd och tjänsteexponering

Planrevision 3 är genomförd inom den beslutade underlagsleveransen. Slutverifieringen avslutades den 22 oktober 2026. Uppgift 3b är uttryckligen uppskjuten och uppgift 6 avvaktar verkliga metodbeslut. Ingen ny numerisk riskmetod, sakkunnigattest, juridisk verifiering eller produktionsrelease påstås.

## Leverans och bas

Isolerad checkout `Riskanalys`, gren `codex/kravstod-tjansteexponering`, utgår från `8915f0d154416bcbd482b2b926a6523e7f9405d8` med kodbas `288fa6650ea400fda04cdcef965f8ac17adc3575`. Alla 13 kod-/underlagscommits återanvändes; den fjortonde är ursprungsgranskningen. Användarens båda befintliga programcheckouter har inte ändrats. Kodleveransen är commit `bd8577f` ovanpå dokumentationscommitet `4521f3d`. Ingen push eller integration utförs inom denna leverans.

| Uppgift | Resultat |
|---|---|
| 0 | Bas och miljö kontrollerade, 170 baslinjeprov godkända; se baslinjeprotokollet. |
| 1 | Exakt 36 huvudrader med källgrund, tillämplighet, befintliga krav-ID:n, kod, rapportplats, prov och kvarstående gränser. |
| 2 | Samma beslutsformulär kompletterat med par 9–10. H7.1 och befintliga scenario-/kontrollkontraster återanvända. Syntetiska plan-/gruppfall tillagda; nuvarande scenarioresultat i `2026-10-21-kravstod-foreutfall.json` är teknisk baslinje, inte sakkunnigfacit. Inga besluts-/ansvarsfält har fyllts i av AI. |
| 3a | Planpost, saklig bunden utvärdering, införandespärr, rättelse och årsfristseparering införda i CLI/webb, befintlig lagring och fastställelse. |
| 4 | Lokala deklarerade grupper med en population, antal/bas, period, källa och ansvarig; skilda spår för samtidig, åtskild och okänd exponering. Inget kundregister. |
| 5 | Befintliga mekanismer en gång per aktiverat faktor-ID i D-ARB.5, endast för erbjudna tjänster. Lokal tillämpning vid tjänsten; motortabellerna kvar i B1. |
| 3b | Uppskjuten enligt planens valfria avgränsning; förhandsutvärderingen kräver ingen separat motororientering. |
| 6 | Inga riskvikter/algoritmer ändrade. D3/D4/D5/D6/D8/D9 och eventuellt berörda relevansbeslut kräver verkliga preciserade beslut innan numerisk anslutning. |
| 7 | Riktade prov, genomgående fall, full svit, regelbasvalidering, rapportmätning och berörda renderade sidor kontrollerade. |

Användarens MHTML-kopia och DOCX-sammanställning lästes som källor. Befintliga daterade regelpaket och källregister återanvänds; deras sakkunnigstatus är oförändrad. [Kravmatrisen](2026-10-21-kravmatris-36.md) redovisar kvarstående `delvis`, särskilt numerisk tjänsteexponering, TF/metodkalibrering och faktiskt informations-/utbildningsarbete.

## Genomgående kontroll

Planfallet provas från registrering med erbjudande nej till genomförd utvärdering och införande, utan motorbedömning. Ändrat planinnehåll eller belägg upphäver planens utvärderingsbindning. Själva erbjudandeövergången och dess automatiska inaktualisering av följdsvar är normaliserade i plansumman; verkliga värden, källor, datum, status och belägg ingår fortsatt. Profilrevision och analysbindning normaliseras inte. Äldre alias och historiskt nej efter ett mellanliggande okänt svar kan inte behandlas som första kartläggning. Hela den föreslagna batchen jämförs mot sparat före-läge.

Rättelser kräver uttrycklig motivering, källa, ansvarig, datum och matchande före-/eftervärden samt profilrevision. En plan kan inte flyttas till en annan tjänst för att öppna rättelsevägen. Begärd rättelse journalförs före profilens atomiska sparning; eftervärdet i sparad profil visar om rättelsen genomförts vid ett eventuellt avbrott.

Planutvärderingen ändrar hela historikens kontrollsumma. Ett genomgående prov med fyra tidigare syntetiskt godkända analysbeslut visar: ändrad historik → inaktuellt underlag → samtliga nya beslutsförsök nekas → uttrycklig förnyelse → alla gamla beslut kvar som historia men inget är längre gällande, och alla block kräver ny bekräftelse. Endast historikfältet ändras i den aktuella bindningskontrasten; inget nytt numeriskt motorresultat påstås. Planutvärderingen flyttar inte årsfristen.

Gruppfallet har 100 uppdrag och samma deklarerade marginaltal i tre varianter: samma åtta har båda egenskaperna, två belagt åtskilda grupper om åtta, respektive okänt överlapp. Profilrevision och rapportspår skiljer sig; exakta motorresultat är lika före metodbeslut. Inaktuella, negativa, feltypade och oförenliga antal/perioder nekas som bekräftat underlag. Okänt och 0 hålls isär, bas 0 betyder inte låg risk och grupper summeras inte till unika totaler. Programmet kontrollerar deklarerad population och metadata, inte den verkliga enheten bakom ett bart heltal.

AI-proven jämför hela utgående begäran inklusive omförsök: enbart privata plan-/gruppändringar ger identiska externa bytes. Ingen tillåtelselista har utökats. Befintlig lokal analys, kontrollprövning och rutinåtgärder återanvänds. Registrering av gruppen ersätter inte byråns sakprövning eller uppdatering av tidigare analysprosa.

Dessutom genomfördes två separata syntetiska CLI-kontroller i tillfälliga privata datamappar: vanligt nej→ja nekades och explicit revisionsbunden rättelse godtogs; separat sparat nej→okänt→ja nekades, varefter plan→utvärdering→införande gick igenom med oförändrad årsfrist.

## Faktisk verifiering

Vald interpreter: checkoutens `.venv312/bin/python`, **Python 3.12.15**. Pydantic 2.14.1, PyYAML 6.0.3, python-docx 1.2.0, anthropic 1.17.0, pytest 9.1.1.

macOS markerade miljöns `.pth`-filer som dolda, vilket Python 3.12 ignorerar. Den isolerade miljön har därför en lokal `site-packages/riskanalys`-symlänk direkt till denna checkouts `src/riskanalys`. Regelbasens standardrot och modellens källrot löser fortsatt till denna checkout. Ingen annan miljö eller checkout ändrades.

| Körning | Utfall |
|---|---|
| Oförändrad bas: analyslagring, reduktionsspärr, åtgärdsgrupper, hela kedjan, V8, rendering och rapportflöde | 170 godkända, 232,74 s |
| Riktade regressioner: plan/grupp, V8, rendering, H7.1 och scenariomotor | 168 godkända, 43,53 s |
| Faktorförklaring och skyddad AI-begäran | 30 godkända, 18,27 s |
| Granskningsrättningar och genomgående fall | 35 godkända, 30,48 s |
| **Full svit efter samtliga kodrättningar**: `.venv312/bin/python -m pytest -q` | **3 010 godkända, 1 avmarkerat, 1 909,08 s, exit 0** |
| `.venv312/bin/riskanalys regelbas validera` | Exit 0; 107 krav, 11 tjänster, tre län med vardera 201/201 paragrafer hanterade. Sakkunnigstatus ej_granskad. |
| `git diff --check` | Exit 0 |
| Kravmatrisens huvudrader | Exakt 1–36, inga luckor eller dubbletter |

Det avmarkerade provet är livetest enligt projektets ordinarie `-m 'not live'`. Lokala HTTP-prov kördes med tillfälliga loopbackservrar. Inga produktfiler ändrades under den slutliga fullsviten. Äldre delkörningar avbröts för att ersättas av slutkörningen efter granskningen; de räknas inte som godkända slutprov. Fullsvitens logg och de fyra rapportmätningarna är bevarade i [kravstod-2026-10-21](kravstod-2026-10-21/hela-sviten.log). Enbart radslutens avslutande blanktecken är normaliserade i de sparade textloggarna; siffror och innehåll är oförändrade. Avbrutna körningar ingår inte i slutbevisen.

Regelbasens kontrollsumma är fortsatt `sha256:7e0f77726a35b5e9fd47b8d324b43236cbeab5ded78c107ccfe54570cc97285f`. Metoden ändras inte, men `profil.modeller` ingår i befintlig källbunden modellidentitet: nya profilmodeller ger därför ny modellbindning. Äldre modellunderlag eller attester får inte märkas om till nya. Inget modellriskunderlag eller mänskligt beslut har skapats för en verklig byrå.

## Rapportmätning och rendering

Samma H7.1-profiler, frysta svar och `docs/research/verktyg/rapportmatning.py` användes före och efter. Slutmätningen bekräftade eftervärdena.

| Fall | Läsrapport före | Efter | Delta | B1 före/efter | Totalt före → efter |
|---|---:|---:|---:|---:|---:|
| fyra_tjanster | 12 665 | 13 352 | +687 | 34 440 | 47 105 → 47 792 |
| med_betalningsmandat | 12 342 | 13 029 | +687 | 34 609 | 46 951 → 47 638 |

Ökningen utgörs av mekanismernas förklaringar, avgränsning mot bekräftad exponering och tjänsternas lokala faktorkopplingar. Ingen text har flyttats till B1 för att presenteras som en längdminskning. B1 är oförändrad i dessa jämförelsefall. Nya faktiskt registrerade plan-/gruppuppgifter lägger därutöver till sitt eget underlag; jämförelseprofilerna hålls oförändrade för mätningen.

Verktygets mått för ordagrann text som finns i alla fyra tjänster minskar från 1 062 till 1 057 ord i fyrtjänstfallet och från 973 till 968 i mandatfallet. Måttet för likartad struktur ökar från 310 till 394 ord. Det senare är inte ordagrann upprepning. Ingen total textminskning eller allmän lästidsvinst påstås.

Ett separat syntetiskt grupp-/planfall exporterades med befintliga `bygg_rapportvyer` och `rendera_rapportvyer`, två DOCX-delar. Den paketerade LibreOffice/Poppler-renderaren skapade 38 läsrapportsidor och 99 bilagesidor. Detta sidantal gäller det separata QA-fallet och jämförs inte med ordmätningens två andra profiler.

Visuellt öppnade och kontrollerade berörda PNG-sidor: läsrapport 6 (mekanismer), 10 (lokal faktorkoppling och grupp), bilaga 64 (beräkningstabellens fortsättning, plan, antagande, utvärderingsdatum/plansumma och källregister). Ingen materiell klippning, överlappning eller förlorad text på dessa sidor. Detta är riktad visuell kontroll, inte fullsidig Word-QA av alla 137 sidor eller en sakkunnig sakgranskning. Historiska V5–V7-kontrakt och V8:s fullständiga text-/cell-/ursprungskartor verifieras av de automatiska proven.

## Oberoende granskning och ställningstaganden

En separat granskare läste hela diffen, nya filer, planen och designen utan att ändra checkouten. Fem Important och två Minor hittades, inga Critical. Alla fem Important reproducerades som fallerande prov och rättades: automatisk inaktualisering vid införande; äldre alias; gruppbeläggens kronologi; flytt av planens tjänstidentitet; och beläggsbyte trots oförändrat värde. Förlust av inmatad utvärdering vid valideringsfel uppgraderades till Important utifrån användarpåverkan och rättades. Även säker återgivning av felaktigt tjänsteval rättades. Inga fynd har skjutits upp. Ett ytterligare prov skyddar möjligheten att utvärdera en framtida planperiod utan att behandla den som faktisk grupphistorik. Fullsviten ovan kördes efter rättningarna; ingen andra reviewomgång har räknats som bevis.

Avgränsningar som granskaren inte avgjorde: valfria 3b, nya numeriska metodbeslut, sakligt tillräcklig mänsklig utvärderingstext, extern rättslig aktualitet och faktiskt utbildnings-/informationsarbete. Dessa är fortsatt uttryckliga gränser; slutprov och rendering verifierades separat enligt ovan.

Beslut under genomförandet:

- Isolerad lokal klon i behörig arbetsyta i stället för att ändra den befintliga programcheckouten; kostnad om fel: en extra checkout att hantera.
- Svensk plan med 3a/3b gav inte stöd i skillens engelska Task-skript; journal/checklista fördes direkt; kostnad om fel: manuell fullständighetskontroll krävs. Kontroll mot samtliga uppgifter och 36 huvudrader genomförd.
- Deluppgifternas commits väntade på den fulla sviten enligt AGENTS; kostnad om fel: mindre granularitet i mellanliggande implementationshistorik.
- Aktuella true→true-sakuppgifter kan kompletteras innan omprövning; fastställelse kontrollerar alla registrerade planer. Det undviker cirkulära redigeringskrav. Granskaren fann ingen separat bypass; kostnad om fel: ingen automatisk spärr mot genomförande i verkligheten utanför programmet.
- 3b uppskjuten och inga egna metodbeslut i 6; kostnad om fel: synligt bättre gruppunderlag ger fortsatt samma risknivå tills verkliga beslut finns.
- Planens slutpunkt lämnar integration till senare instruktion. Den lokala grenen och checkouten behålls; ingen ny bekräftelse behövs för att lämna det redan beställda granskningsunderlaget.

Programstödet är tekniskt verifierat i denna omfattning. Saklig metodvalidering, verksamhetens åtgärder och mänskliga attester förblir separata skyldigheter.
