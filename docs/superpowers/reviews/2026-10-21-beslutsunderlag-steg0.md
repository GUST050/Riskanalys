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
| S-GEO-01 utlandstransaktion (**> 0**) | H/M/H/M | H/M/H/M | H/M/H/M | H/M/H/M | H/M/H/M | H/M/H/M |
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

## Beslutsfrågor och alternativ

Inget alternativ är prövat mot ett sakligt facit. Att ett alternativ ger fler olika nivåer visar inte i sig att metoden blir bättre. Målet är att verkliga skillnader i exponering, mandat och kontroll behandlas med hållbar motivering, inte spridning för dess egen skull.

Alla alternativ förutsätter samma princip: en ändring ges ny regelversion och ny modellbindning, bevarade föreutfall, frysta facit och sakkunnigprövning före operativ användning.

### D6 – Konsekvens och sannolikhet för terrorfinansiering

| Alternativ | Innebörd | Effekt i prov 1 |
|---|---|---|
| A Behåll | Konsekvensen är alltid allvarlig. | 20/24 enskilda faktorer ger TF hög; två faktorer ger mycket hög. |
| B Betydande konsekvens | Samma sannolikhetsväg men konsekvens betydande. | Alla enskilda faktorer ger TF måttlig. Två faktorer i samma TF-scenario ger hög. *Mycket hög* nås aldrig. |
| C Endast TF-specifika faktorer | Bara faktorer med visad TF-kedja (till exempel utland, ideell, högrisktredjeland, kontanter) räknas i TF-scenarierna. Övriga syns i PT. | Ej kört. Kräver en genomgång faktor för faktor av `galler`. I dag är 20 av 24 faktorer markerade för både PT och TF. |
| D Kvalitativ TF | Ingen matris. TF beskrivs per scenario med motiverad nivå. | Ej kört. Kräver ny modell för motivering och granskning. |

Att pröva: projektets egna källanteckningar säger att NRA anger inga kända TF-tillvägagångssätt för skatterådgivning (s. 128) och bolagstjänster (s. 146). Finanspolisens lägesbild är rapporteringsbaserad. Det finns ingen regel om att TF ska vara lägre än PT.

### D9 – Summering, trösklar och tak

| Alternativ | Innebörd | Effekt |
|---|---|---|
| A Behåll | Varje faktor ger +1, tak *hög*. | En faktor ger samma nivå som åtta. Se iakttagelse 1. |
| B Två oberoende orsaker | Sårbarhetsnivån höjs först när minst två faktorer från olika områden möjliggör samma scenario. | Ingen enskild faktor höjer längre PT. Raderna i prov 1 blir M för redovisningstjänsterna. Fyrtjänstbyrån förblir hög (H-03 har åtta faktorer från flera områden). |
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
