# 03 Tillsyn och sanktioner

## Så går tillsynen till

- Tre länsstyrelser delar ansvaret: Stockholm, Västra Götaland och Skåne.
- Tillsynen sker oftast som skrivbordskontroll genom föreläggande att inkomma med uppgifter. Platsbesök förekommer.
- Ett föreläggande går inte att överklaga. En sanktionsavgift kan överklagas till förvaltningsrätten.
- Länsstyrelserna gör **återkontroller** hos verksamheter som fått ingripanden. Brister som kvarstår räknas som försvårande omständighet.
- Sanktionsavgiften ligger mellan 5 000 kr och 10 miljoner kr. Den är inte avdragsgill. Länsstyrelsen väger in att bristande efterlevnad kan ha gett konkurrensfördelar.

## Standardföreläggandet (Länsstyrelsen Stockholm)

Återgivet i sammanfattning. Det är i praktiken en kravspecifikation för vad programmet ska kunna leverera.

| # | Begärd uppgift | Leverans från programmet |
|---|---|---|
| 1 | Allmän riskbedömning och hur ofta den utvärderas och uppdateras | Allmän riskbedömning med versionslogg |
| 2 | Hur risker med olika typer av kundrelationer bedöms | Kundriskmodell |
| 3 | Rutiner för kundkännedom, övervakning och rapportering samt personuppgifter, och hur ofta de uppdateras | Rutiner och riktlinjer med versionslogg |
| 4 | Sex anonymiserade exempel på kundkännedom: två vardera för normal, låg och hög risk | Kundmodul (fas 2). I fas 1 kundformulär. |
| 5 | Rutiner för intern kontroll och anmälan av misstänkta överträdelser | Rutiner |
| 6 | Vem som ansvarar för regelefterlevnad | Rollbeskrivning i rutinerna |
| 7 | Rutiner för lämplighetsprövning | Rutiner |
| 8 | Hur personalen får utbildning och information | Rutiner och utbildningslogg |
| 9 | Rutiner för skydd mot hot, hämnd och fientliga åtgärder | Rutiner |
| 10 | Dokumentation av genomförda utbildningar under en period | Utbildningslogg |
| 11 | Lista över aktiva kunder med organisationsnummer och årligt arvode | Kundregister (fas 2) |
| 12 | Kundkännedom för de tio största kunderna: identitet, verklig huvudman, PEP, högrisktredjeland, syfte och art, medlens ursprung, riskprofil och underlag | Kundmodul (fas 2) |
| 13 | Tjänster till de tio största kunderna | Kundmodul (fas 2) |
| 14 | Antal rapporterade misstankar | Misstankelogg (fas 2) |
| 15 | Antal misstankar som inte rapporterats | Misstankelogg (fas 2) |

Länsstyrelsen Västra Götalands motsvarighet har sju punkter. Den kräver bland annat riskbedömning av tre kunder (hög, normal och låg risk) med beskrivning, analys och slutsats.

## Vanliga brister enligt tillsynsrapport 2026:14

Detta är **bristmönsterkatalogen v0**. ID:na nedan gäller. Specen hänvisar till dem, och i etapp M0 flyttas katalogen till `regelbas/kataloger/bristmonster.yaml`, som därefter är den enda källan. Programmets granskare ska kontrollera varje mönster.

| ID | Bristmönster | Hur granskaren kan upptäcka det |
|---|---|---|
| B-01 | Den allmänna riskbedömningen saknas eller förväxlas med kundbedömning eller rutiner | Kontrollera att dokumentet finns och har de fyra obligatoriska delarna |
| B-02 | Mallen är inte anpassad till verksamheten | Låg andel referenser till byråprofilen och hög andel generiska formuleringar |
| B-03 | Otillräcklig identifiering och analys av hot och sårbarheter | Varje erbjuden tjänst ska ha hot med källa och sårbarheter |
| B-04 | Tjänster beskrivs tillsammans utan individuell analys | Varje tjänst ska ha eget avsnitt |
| B-05 | Fokus på ett eller få hot, nya hot fångas inte upp | Jämför hoten mot hotkatalogen och aktuell omvärldsbevakning |
| B-06 | Kundkategorier utan förklaring av hur de ökar risken | Varje kundkategori ska ha motivering |
| B-07 | Nära kundrelationer förbises som sårbarhet | Kontrollera att sårbarheten finns med |
| B-08 | Distributionskanaler och leveranssätt identifieras inte | Kontrollera avsnittet om kanaler |
| B-09 | Geografi kopplas bara till sanktionslistor | Kontrollera att utlandskopplingar och lokala riskfaktorer analyseras |
| B-10 | Påstående om att geografiska risker saknas utan motivering | Ingen nivå får anges utan motivering |
| B-11 | Verksamhetsspecifika omständigheter saknas | Kontrollera avsnittet |
| B-12 | Sammantagen risk utan analys av hur nivån nåtts | Varje nivå ska ha regelspår och motivering |
| B-13 | Alla nivåer låga utan hänsyn till sektorsrisken i den nationella riskbedömningen | Jämför med sektorsnivån och kräv motivering vid avvikelse |
| B-14 | Källor för hot anges inte | Kontrollera källförteckningen |
| B-15 | Egen rapportering till Finanspolisen vägs inte in | Kontrollera att uppgiften finns i profilen och texten |
| B-16 | Datum för utvärdering och uppdatering saknas | Kontrollera versionsloggen |

Ytterligare mönster ur sanktionsbeslut och branschlitteratur:

| ID | Bristmönster |
|---|---|
| B-17 | Rutinerna saknar koppling till den allmänna riskbedömningen |
| B-18 | Det framgår inte hur kundernas riskprofiler följs upp och ändras |
| B-19 | Det står att åtgärder vidtagits, men inte hur |
| B-20 | Rutiner för lämplighetsprövning och utbildning saknas. Att personalen går på myndigheters informationsträffar räcker inte. |
| B-21 | Hänvisning till branschstandard (REX, Reko) i stället för egna rutiner |
| B-22 | Påstående om ansvarig för regelefterlevnad utan rutin för hur ansvaret utövas |

## Sanktionsstatistik

**Underlag:** Länsstyrelsen Stockholms och Länsstyrelsen Västra Götalands sidor om ingripanden, sparade i september och oktober 2026. Sammanställt med [verktyg/sanktionsstatistik.py](verktyg/sanktionsstatistik.py).

**Begränsningar:**
- Klassificeringen bygger på textmönster i beslutens sammanfattningar.
- Årtal är det första årtal som nämns och kan ibland vara tillsynsperiodens år.
- Skånes beslut ingår inte. Skåne fattade flest beslut om sanktionsavgift under 2024 (24 stycken, varav 14 mot redovisningsbyråer).

| Mått | Värde |
|---|---|
| Publicerade ingripanden | 185 (Stockholm 105, Västra Götaland 80) |
| Varav sanktionsavgifter | 139 |
| Varav föreläggande att upphöra med vite | 2 |
| Övriga (förelägganden, varningar m.m.) | 44 |
| Ingripanden som gäller den allmänna riskbedömningen, ensam eller med rutiner | 133 (72 %) |
| Sanktionsavgift, lägsta / högsta | 5 000 kr / 8 800 000 kr |
| Sanktionsavgift, kvartiler | 90 000 kr / **245 000 kr (median)** / 550 000 kr |
| Sanktionsavgift, medelvärde | cirka 568 000 kr |
| Median när bara den allmänna riskbedömningen granskats | 310 000 kr |
| Median för redovisnings- och ekonomibyråer (namnbaserat urval, 57 beslut) | 310 000 kr |

Ingripanden per år enligt textmönster: 2020: 14, 2021: 26, 2022: 43, 2023: 18, 2024: 19, 2025: 45, 2026 (till och med september): 13.

**Mönster:**
- Från 2023 granskar länsstyrelserna allt oftare enbart den allmänna riskbedömningen, och avgifterna i de besluten är jämförelsevis höga.
- Formuleringen "synnerligen allvarlig överträdelse som markant har ökat risken" återkommer i många beslut 2025–2026.
- Flera beslut har överklagats utan framgång. I ett fall från 2023 avslog förvaltningsrätten överklagandet, och varken kammarrätten eller Högsta förvaltningsdomstolen beviljade prövningstillstånd.
- Advokatsamfundet har begärt att Länsstyrelsen prövar sanktionsavgift för advokatbyråer med bristande allmän riskbedömning.
