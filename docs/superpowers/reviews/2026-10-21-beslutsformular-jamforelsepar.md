# Beslutsformulär: vilka skillnader ska påverka bedömningen?

Underlag för metodbesluten i [beslutsunderlaget](2026-10-21-beslutsunderlag-steg0.md). Formuläret fylls i av metodansvarig eller en sakkunnig.

**Status för svaren:** varje svar är en *hypotes* tills metodansvarig har prövat och godkänt det. Först då blir svaret en fastställd testförväntning i steg 4. AI kan föreslå källstödda svar och räkna konsekvenser, men får inte fylla i fälten *beslut* eller *ansvarig*.

## Så fylls formuläret i

För varje par:

1. **Läs de fasta förhållandena.** De är lika i A och B, så att bara den angivna skillnaden prövas.
2. **Ange för varje led om B jämfört med A ger** *högre*, *lägre*, *oförändrat* eller *otillräckligt underlag*. Leden är scenariots relevans, sannolikhet, konsekvens och kontrollens effekt. Ange vilka scenarier (hot) svaret gäller.
3. **Ange därefter om tjänstens sammanfattade nivå påverkas.** En skillnad kan ändra ett scenario utan att tjänstens högsta nivå ändras. Det är ett giltigt svar.
4. **Fyll i motivering, källa, osäkerhet, beslutsfattare och datum.**

*Otillräckligt underlag* är ett giltigt svar. Det betyder att frågan inte kan avgöras med nuvarande källor, inte att svaret är *oförändrat*.

Kolumnen *Dagens modell* visar programmets nuvarande utfall som jämförelse, inte som facit.

## Svarsmall (kopiera per par)

| Led | Svar (högre / lägre / oförändrat / otillräckligt underlag) | Berörda scenarier (hot) |
|---|---|---|
| Scenariots relevans | | |
| Sannolikhet | | |
| Konsekvens | | |
| Kontrollens effekt | | |
| **Tjänstens sammanfattade nivå** | | |

| Fält | Svar |
|---|---|
| Motivering | |
| Källa (dokument, avsnitt, sida) | |
| Osäkerhet | |
| Status | hypotes / prövad och godkänd / avvisad |
| Ansvarig beslutsfattare (namn, roll) | |
| Datum | |

## Par 1: exponering inom tjänsten (D3, D9)

| | A | B |
|---|---|---|
| Fast | Löpande bokföring, 100 kunder som använder tjänsten, samma period, samma kontroller, inga andra riskfaktorer | |
| Skillnad | 1 av 100 kunder har transaktioner med utlandsanknytning | 40 av 100 kunder har transaktioner med utlandsanknytning |
| Dagens modell | PT hög, TF hög | PT hög, TF hög (ingen skillnad; villkoret är `> 0`) |

Tilläggsfråga: ska en kund med utlandstransaktion i en *annan* tjänst påverka denna tjänst? (D3)

## Par 2: mandat (D3, D8)

| | A | B |
|---|---|---|
| Fast | Lönehantering, samma 45 kunder, samma period, samma kundfaktorer och kontroller | |
| Skillnad | Kunden verkställer löneutbetalningarna; byrån beräknar lön och upprättar arbetsgivardeklaration utan betalningsmandat | Byrån verkställer löneutbetalningarna enligt kundens attest, med betalningsmandat och full bankinsyn |
| Dagens modell | Identiska nivåer; mandat påverkar inte motorn (H7.7) | |

Tilläggsfråga: påverkar mandatet *vilka hot* som är relevanta, *hur sannolika* de är, *vad kontrollerna kan upptäcka*, eller flera av dessa?

## Par 3: kontrollens effekt – okänt är inte frånvarande (D8)

Samma tjänst, kunder, period och scenarier. Bara uppgiften om kontrollens effekt skiljer sig. Jämför B och C var för sig mot A.

| | A | B | C |
|---|---|---|---|
| Effekt | Belagd verksam effekt med utfall och begränsningar | Effekten är inte bedömd eller inte belagd (okänd) | Effekten är bedömd och belagt verkningslös |
| Dagens modell | Sänker täckta scenarier ett steg | Ingen sänkning | Ingen sänkning |

Tilläggsfråga: ska B (okänt) och C (belagt verkningslös) behandlas lika i nivån, och hur ska skillnaden synas i rapporten?

## Par 4: täckningsgrad (D8)

| | A | B |
|---|---|---|
| Fast | Samma kontroll, scenario, period och belägg för genomförande | |
| Skillnad | Byrån bedömer täckningen som tillräcklig för scenariot | Byrån bedömer täckningen som delvis, till exempel ett stickprov som inte omfattar alla betalningsled |
| Dagens modell | Ett stegs sänkning godtas | Sänkningen godtas inte (steg 2) |

Tilläggsfråga: ska delvis täckning ge någon effekt, och i så fall hur ska den redovisas på en skala med fyra nivåer?

## Par 5: enmansbyrå prövad genom arbetssätt (D9)

Samma kunder, tjänster och period. Ingen annan riskfaktor. Jämför B, C och D var för sig mot A.

| | A | B | C | D |
|---|---|---|---|---|
| Arbetssätt | En person utför uppdrag och kontroll; ingen extern granskning; aktuell AML-utbildning | Som A, men med dokumenterad extern granskning av urval av uppdrag minst årligen | Som A, men utan aktuell AML-utbildning | Två personer; utförande och kontroll är åtskilda |
| Dagens modell (bokföring) | PT hög, TF hög (S-ARB-16) | Samma som A; intaget har ingen uppgift om extern granskning | PT hög, TF mycket hög (S-ARB-15 och S-ARB-16 i samma TF-scenario) | PT måttlig, TF måttlig |

Tilläggsfrågor:
- Är antalet personer i sig en sårbarhet, eller avgör kompetens, kontroll och oberoende granskning?
- Behöver intaget en uppgift om extern granskning eller andra kompenserande arbetssätt?

## Par 6: terrorfinansiering (D6)

| | A | B |
|---|---|---|
| Fast | Löpande bokföring, 100 kunder, samma period och kontroller | |
| Skillnad | Inga kunder med kontanthantering eller utlandsanknytning | 10 av 100 kunder har betydande kontanthantering, ingen utlandsanknytning |
| Dagens modell | TF måttlig | TF hög |

Tilläggsfrågor:
- Vad mäter konsekvensen för terrorfinansiering, och ska den alltid vara *allvarlig*?
- Vilka faktorer har en visad kedja till terrorfinansiering i just denna tjänst?

## Efter ifyllandet

Godkända svar blir förväntade utfall per scenario och per tjänst. Varje godkänt par blir ett test innan någon metodändring kodas (steg 4). Svar med status *hypotes* eller *otillräckligt underlag* kodas inte.
