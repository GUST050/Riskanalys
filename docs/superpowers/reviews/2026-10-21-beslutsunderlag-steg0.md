# Beslutsunderlag för steg 0: D3, D5, D6, D8 och D9

Förberett av Claude Code, 21 oktober 2026. **Detta är beslutsunderlag, inga beslut.** Ingen sakkunnig har prövat alternativen. Alternativen är ogranskade förslag. Regelbasen och sakkunnigstatusen är oförändrade.

Frågorna finns redan i [13-scenariomotor-katalog.md](../../research/13-scenariomotor-katalog.md#öppna-sakkunnigbeslut). Där finns även källstöd och beslutsprotokollets krav. Det här dokumentet lägger till körda prov som visar vad dagens metod faktiskt gör, och vad några alternativ skulle ändra.

## Så räknar metoden i dag

- **PT:** Redovisningstjänsterna har grundsannolikhet *medel* och konsekvens *betydande*. Utan faktorer blir risken *måttlig*.
  - Varje möjliggörande faktor höjer sårbarhetsnivån ett steg, upp till *hög*.
  - Hög sannolikhet med betydande konsekvens ger *hög*. PT kan alltså bara bli måttlig eller hög. Redan en faktor ger hög.
  - Skatterådgivning och bolagstjänster har grundsannolikhet *hög* och är därför höga även utan faktorer.
- **TF:** Grundsannolikheten är *låg* och konsekvensen alltid *allvarlig*. Det ger måttlig utan faktorer, hög med en faktor och mycket hög med två eller fler faktorer i samma scenario.
- **Tjänstens nivå** är det högsta scenariot (max). En kontroll sänker ett steg, men bara i de scenarier vars hot den riktar sig mot.

## Prov 1: en enda faktor i en byrå utan andra faktorer

Syntetisk profil A (`tester/fixturer/faktorer.py`): alla tjänster erbjuds, bankdata finns och kontrollerna har belagd effekt. En faktor i taget slås på. Skript: [`docs/research/verktyg/enskilda_faktorer.py`](../../research/verktyg/enskilda_faktorer.py). Motorn är oförändrad på grenen `feat/steg-1-3`.

Förkortningar: M = måttlig, H = hög. Varje cell visar *PT före / PT efter kontroll / TF i dag / TF om konsekvensen vore betydande*.

| Faktor (tröskel) | Bokföring | Bokslut | Deklaration | Lön | Skatterådgivning | Bolagsbildning |
|---|---|---|---|---|---|---|
| Ingen faktor | M/M/M/M | M/M/M/M | M/M/M/M | M/M/M/M | H/M/M/M | H/M/M/M |
| S-KUND-01 riskbransch (≥ 20 %) | H/H/M/M | H/H/M/M | H/H/M/M | H/H/M/M | H/M/M/M | H/M/M/M |
| S-KUND-02 kontanter (≥ 10 %) | H/H/H/M | H/H/H/M | H/H/H/M | H/M/H/M | H/M/H/M | H/M/H/M |
| S-KANAL-01 digitalt utan bankdata | H/H/M/M | H/H/M/M | H/H/M/M | H/H/M/M | H/M/M/M | H/M/M/M |
| S-VERK-01 juniora konsulter | H/M/M/M | H/M/M/M | H/M/M/M | H/H/M/M | H/M/M/M | H/M/M/M |
| S-GEO-01 utlandstransaktion (**> 0**; profilen har 100 av 100 kunder, 1 av 100 ger samma utfall, se prov 3) | H/M/H/M | H/M/H/M | H/M/H/M | H/M/H/M | H/M/H/M | H/M/H/M |
| S-ARB-01 nära relation | H/H/H/M | H/H/H/M | H/H/H/M | H/H/H/M | H/M/H/M | H/M/H/M |
| S-ARB-02–14 (ägare, PEP, ideell, distans, land m.m.) | H/M/H/M | H/M/H/M | H/M/H/M | H/M/H/M | H/M/H/M | H/M/H/M |
| S-ARB-15, 16, 18 (utbildning, en person, utkontraktering) | H/M/H/M | H/M/H/M | H/M/H/M | H/H/H/M | H/M/H/M | H/M/H/M |
| S-ARB-17 kundberoende | H/H/H/M | H/H/H/M | H/H/H/M | H/H/H/M | H/M/H/M | H/M/H/M |

**Iakttagelser** (fakta om dagens metod, inte bedömningar av rätt nivå):

1. **PT:** alla 24 faktorer ger ensamma *hög* inneboende PT i alla tjänster.
2. **TF:** 20 av 24 faktorer ger ensamma *hög* TF i alla tjänster. Det är exakt de 20 som är markerade för både PT och TF (`galler: bada`). Två faktorer i samma TF-scenario ger *mycket hög*.
3. **Kvarstående PT** är det enda som skiljer faktorerna åt. Det beror på vilka hot kontrollerna riktar sig mot, inte på faktorn i sig.
4. **Fem trösklar utlöses av en enda kund eller ett enda ja:** S-GEO-01, S-ARB-04, S-ARB-08, S-ARB-11 och S-ARB-14 har villkoret `> 0`.
5. **Enmansbyråer:** S-ARB-16 ("en person utför uppdrag, kontroll och alla ansvarsfunktioner") gäller i praktiken alltid en enmansbyrå. Varje enmansbyrå får därmed hög PT och hög TF i alla tjänster, oavsett kundkrets.

## Prov 2: de tio befintliga H7.1-kontrasterna

Alla 40 tjänsteutfall blir PT hög, kvarstående hög och TF mycket hög (se [granskningen](2026-10-21-granskning-av-andringsplan.md)). Fyrtjänstbyrån i fixturen har åtta faktorer bakom H-03 och positiva fördelningar i alla fyra tjänster. Den har till exempel 5 kontantkunder av 45 i lön, alltså 11 %, mot byråns 10 %.

Ett alternativ som bara lägger till tjänstevis fördelning (D3 B nedan) ändrar därför **inte** dessa fall. De identiska nivåerna kan vara rimliga för just den här byrån. Kontrasterna visar att metoden inte *kan* skilja tjänsterna åt, men inte att den *borde* göra det för denna profil. Det är skälet till att prov 1 behövs.

## Prov 3: provkörda alternativ för D6 och D9

Skript: [`docs/research/verktyg/metodalternativ.py`](../../research/verktyg/metodalternativ.py). Alternativen sätts bara i minnet; regelbasen och motorns kod är oförändrade. Profilerna är syntetiska (profil A med bankdata och belagda kontroller). Cell: *PT före / PT efter kontroll / TF*. Kolumnerna visar bokföring (representativ för redovisningstjänsterna) respektive skatterådgivning (representativ för skatte- och bolagstjänsterna). MH = mycket hög. Faktorer med `> 0`-villkor utlöses i fixturen med 100 % av kunderna; där det står 100 % är det profilens faktiska andel.

| Profil | I dag | D6 B betydande | D6 C1 katalogfilter | D6 C2 H-03 bara PT | D9 B påslag efter antal områden | D9 B + D6 B |
|---|---|---|---|---|---|---|
| Ingen faktor | M/M/M · H/M/M | M/M/M · H/M/M | M/M/M · H/M/M | M/M/M · H/M/M | M/M/M · H/M/M | M/M/M · H/M/M |
| 1 av 100 kunder med utlandstransaktion | H/M/H · H/M/H | H/M/M · H/M/M | H/M/H · H/M/H | H/M/H · H/M/H | M/M/M · H/M/M | M/M/M · H/M/M |
| 100 av 100 kunder med utlandstransaktion | H/M/H · H/M/H | H/M/M · H/M/M | H/M/H · H/M/H | H/M/H · H/M/H | M/M/M · H/M/M | M/M/M · H/M/M |
| Kontanter | H/H/H · H/M/H | H/H/M · H/M/M | H/H/H · H/M/H | H/H/H · H/M/H | M/M/M · H/M/M | M/M/M · H/M/M |
| PEP | H/M/H · H/M/H | H/M/M · H/M/M | H/M/M · H/M/M | H/M/M · H/M/M | M/M/M · H/M/M | M/M/M · H/M/M |
| Enmansbyrå (S-ARB-16) | H/M/H · H/M/H | H/M/M · H/M/M | H/M/H · H/M/H | H/M/M · H/M/H | M/M/M · H/M/M | M/M/M · H/M/M |
| Enmansbyrå + utland 100 % | H/M/MH · H/M/MH | H/M/H · H/M/H | H/M/MH · H/M/MH | H/M/H · H/M/H | H/M/H · H/M/H | H/M/M · H/M/M |
| Distans + extern KYC (samma område) | H/M/MH · H/M/MH | H/M/H · H/M/H | H/M/MH · H/M/MH | H/M/M · H/M/MH | M/M/M · H/M/M | M/M/M · H/M/M |
| Utland 100 % + distans + extern KYC | H/M/MH · H/M/MH | H/M/H · H/M/H | H/M/MH · H/M/MH | H/M/H · H/M/MH | H/M/H · H/M/H | H/M/M · H/M/M |
| Ideell + PEP | H/M/MH · H/M/MH | H/M/H · H/M/H | H/M/H · H/M/H | H/M/H · H/M/H | M/M/M · H/M/M | M/M/M · H/M/M |
| Riskbransch + kontanter + utland 100 % + nära relation | H/H/MH · H/M/MH | H/H/H · H/M/H | H/H/MH · H/M/MH | H/H/MH · H/M/MH | H/M/H · H/M/H | H/M/M · H/M/M |

| Alternativ | Enskilda faktorer (av 24) som ger PT hög / TF hög eller mer i bokföring | H7.1-kontrasterna |
|---|---|---|
| I dag | 24 / 20 | Alla tio fall: H/H/MH i alla fyra tjänster |
| D6 B | 24 / 0 | Alla tio fall: H/H/H |
| D6 C1 katalogfilter | 24 / 15 | Oförändrat mot i dag |
| D6 C2 | 24 / 9 | Oförändrat mot i dag |
| D9 B påslag efter antal områden | 0 / 0 | Bokslut och deklaration får kvarstående M i nio fall; i fallet *ingen belagd effekt* förblir de H. Bokföring och lön förblir H/H/MH. |
| D9 B + D6 B | 0 / 0 | Som D9 B, men TF hög i stället för mycket hög |

**Iakttagelser** (fakta om alternativen, inte rekommendationer):

1. **D6 B** sänker TF ett steg nästan överallt och gör *mycket hög* oåtkomlig. Det ändrar inte vilka byråer som skiljer sig åt, bara nivån.
2. **D6 C1 är ett katalogfilter**, inte en prövning av TF-relevans. Det filtrerar på om faktorn är länkad till ett H-TF-ID. Avsaknad av sådan länk visar inte att faktorn saknar saklig TF-relevans; det gemensamma hotet H-03 omfattar uttryckligen både PT och TF. Filtret ändrar lite, eftersom de flesta faktorer redan är länkade till något H-TF-hot. **D6 C2** gör större skillnad, eftersom H-03 i dag samlar nästan alla faktorer i TF.
3. **D9 B (påslag efter antal områden)** är det enda provade alternativet som ger skillnader mellan H7.1-fallen. Det är ett experiment, inte ett verifierat metodval. Kontrolleffekten når då tjänstens kvarstående nivå i bokslut och deklaration, och försvinner när effekten inte är belagd. Det är en skillnad i rätt riktning, men inget facit visar att nivåerna är riktiga.
4. **D9 B** gör samtidigt att varje enskild faktor, till exempel PEP, högrisktredjeland eller ideell kund, *ensam* aldrig höjer nivån. Penningtvättslagen kräver skärpta åtgärder när kunden eller dess verkliga huvudman är en person i politiskt utsatt ställning (3 kap. 19 §) och när kunden är etablerad i ett av EU-kommissionen utpekat högrisktredjeland (3 kap. 17 §). Bestämmelserna gäller kundåtgärder, inte direkt den allmänna riskbedömningens nivå, och de omfattar inte ideella kunder som sådana. En regel där PEP- eller högrisktredjelandsanknytning ensam aldrig höjer nivån behöver ändå uttrycklig motivering. Ett mellanläge vore att vissa namngivna faktorer höjer ensamma.
5. **D9 B räknar katalogområden, inte belagt oberoende orsaker.** Två oberoende orsaker inom samma område ger inget påslag; distans och extern KYC (båda kanal) höjer därför inte tillsammans. Omvänt kan två sammanhängande indikatorer i olika områden ge påslag. Om och hur oberoende ska prövas är en sakfråga.
6. **Ingen av de provade modellerna skiljer exponeringarna åt.** 1 av 100 och 100 av 100 kunder med utlandstransaktion ger samma utfall i alla sex kolumner. Ändrade trösklar (D9 C) eller andra sätt att väga exponering skulle kunna ge skillnad, men inget sådant är provkört.

## Beslutsfrågor och alternativ

Inget alternativ är prövat mot ett sakligt facit. Att ett alternativ ger fler olika nivåer visar inte i sig att metoden blir bättre. Målet är att verkliga skillnader i exponering, mandat och kontroll behandlas med hållbar motivering, inte spridning för dess egen skull.

Alla alternativ förutsätter samma princip: en ändring ges ny regelversion och ny modellbindning, bevarade föreutfall, frysta facit och sakkunnigprövning före operativ användning.

### D6 – Konsekvens och sannolikhet för terrorfinansiering

| Alternativ | Innebörd | Effekt i prov 1 |
|---|---|---|
| A Behåll | Konsekvensen är alltid allvarlig. | 20/24 enskilda faktorer ger TF hög; två faktorer ger mycket hög. |
| B Betydande konsekvens | Samma sannolikhetsväg men konsekvens betydande. | Alla enskilda faktorer ger TF måttlig. Två faktorer i samma TF-scenario ger hög. *Mycket hög* nås aldrig. |
| C1 Katalogfilter på H-TF-länk | En faktor räknas i TF bara om katalogen länkar den till ett H-TF-hot. Fem faktorer saknar sådan länk (S-ARB-02, 06, 07, 12, 17). Det visar inte att de saknar saklig TF-relevans; H-03 omfattar både PT och TF. | 15/24 enskilda faktorer ger TF hög (i dag 20). Kombinationer når fortfarande mycket hög. Se prov 3. |
| C2 H-03 bara PT | Scenariot H-03 *oförklarade in- och utflöden* räknas bara som PT. TF avgörs av de tre H-TF-scenarierna. | 9/24 enskilda faktorer ger TF hög. Skatte- och bolagstjänster når fortfarande mycket hög med två faktorer som är länkade till H-TF-hot. Se prov 3. |
| D Kvalitativ TF | Ingen matris. TF beskrivs per scenario med motiverad nivå. | Ej kört. Kräver ny modell för motivering och granskning. |

Att pröva: projektets egna källanteckningar säger att NRA anger inga kända TF-tillvägagångssätt för skatterådgivning (s. 128) och bolagstjänster (s. 146). Finanspolisens lägesbild är rapporteringsbaserad. Det finns ingen regel om att TF ska vara lägre än PT.

### D9 – Summering, trösklar och tak

| Alternativ | Innebörd | Effekt |
|---|---|---|
| A Behåll | Varje faktor ger +1, tak *hög*. | En faktor ger samma nivå som åtta. Se iakttagelse 1. |
| B Påslag efter antal områden (experiment) | Sårbarhetsnivån höjs ett steg per katalogområde (kund, kanal, geografi, verksamhet, tjänst) utöver det första som möjliggör samma scenario. Räknar områden, inte belagt oberoende orsaker. | Ingen enskild faktor och inga faktorer från samma område höjer längre. Fyrtjänstbyrån förblir hög inneboende, men bokslut och deklaration får måttlig kvarstående när kontrollernas effekt är belagd. Se prov 3. |
| C Se över `> 0`-trösklar | Andel eller antal i stället för "minst en", till exempel för utlandstransaktion och distanskund. | Ändrar vilka byråer som utlöser faktorn, inte metoden i övrigt. Trösklarna behöver källstöd eller märkning som metodval. |
| D Egen regel för enmansbyrå | S-ARB-16 bedöms mot byråns storlek, där en ensam person inte är en brist i sig utan kräver annan kompensation. | Redovisningstjänsterna i en enmansbyrå utan andra faktorer går från H till M. Skatte- och bolagstjänster är höga redan genom grundnivån. |

### D3 – Byrågemensam eller tjänstebunden exponering

| Alternativ | Innebörd | Effekt |
|---|---|---|
| A Behåll | Kund- och geografifaktorer gäller alla tjänster med hotet. | Fördelning och mandat påverkar inte nivån (H7.7). |
| B Bekräftad nolla undantar | En kundfaktor gäller inte en tjänst där bekräftad, periodlik fördelning visar 0 kunder. Okänd fördelning behandlas som att faktorn gäller. | Ingen ändring i H7.1-fallen, eftersom alla har mer än 0. Ändrar tjänster som verkligen saknar exponering. |
| C Tjänstens egen andel | Samma tröskel tillämpas på tjänstens andel (antal med faktorn delat med tjänstens kunder). | Kräver beslut om tjänstens population och om kundöverlapp (D4). Ändrar fall där tjänsten ligger under respektive över byråns andel. |

Organisationsfaktorer (S-ARB-15–18, S-VERK-01) gäller av naturen hela byrån. Beslutet behöver ange vilka faktorer som får göras tjänstebundna.

### D5 – Maxregeln

| Alternativ | Innebörd |
|---|---|
| A Behåll max | Tjänstens nivå är det högsta scenariot. Enkelt och försiktigt, men döljer bredd. |
| B Max och bredd | Behåll max, men redovisa intill nivån hur många scenarier som ligger på maxnivån och vilka som är otäckta. Ingen ny beräkning, bara tydligare redovisning. |
| C Max över relevanta scenarier | Ett scenario som byrån med giltigt granskningsbeslut prövat som *ej relevant* (D1/D2) utesluts. Kräver regler för vem som får besluta det och hur. |

Medelvärden avråds i projektets tidigare underlag och föreslås inte här.

### D8 – Kontrollavdrag

| Alternativ | Innebörd |
|---|---|
| A Ett steg vid tillräcklig täckning | Gäller nu i godkännandeprövningen (steg 2 på grenen `feat/steg-1-3`). Delvis täckning ger inget godkänt avdrag. |
| B Kontrollmål per arbetsmoment | Kontrollmålen prövas mot faktiska arbetsmoment och mandat. Till exempel riktar sig C-TJ-08/09 i dag mot alla PT-hot. |
| C Synligt kvarstående otäckt hot | Inget ändrat avdrag. Rapporten visar i stället vilket otäckt scenario som håller kvar nivån (jämför D5 B). |

## Beslutsprotokoll att fylla i

För varje D-ID, enligt `13-scenariomotor-katalog.md`:

| Fält | D3 | D5 | D6 | D8 | D9 |
|---|---|---|---|---|---|
| Sakkunnig (namn, kompetens/roll) | | | | | |
| Datum | | | | | |
| Lästa källor och versioner | | | | | |
| Valt alternativ (behåll/ändra) | | | | | |
| Skäl | | | | | |
| Osäkerhet och giltighet per uppdragsform | | | | | |
| Konsekvens för PT och TF | | | | | |
| Godkänt facit (vilka rader i prov 1 och 2 ska ändras, och till vad) | | | | | |
| Beslutsansvarig | | | | | |

Efter beslut genomförs steg 4: ett beslutat D-ID i taget, med facit från tabellen som test före kod.
