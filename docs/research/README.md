# Research – sammanställning

Underlag för [designspecifikationen](../superpowers/specs/2026-10-08-riskanalys-design.md). Researchen gjordes 2026-10-08.

## Innehåll

| Fil | Innehåll |
|---|---|
| [01-kallmaterial.md](01-kallmaterial.md) | Vilka dokument som lästs och vad varje källa säger |
| [02-kravkarta.md](02-kravkarta.md) | Skyldigheter, lagrum och vad programmet ska leverera |
| [03-tillsyn-och-sanktioner.md](03-tillsyn-och-sanktioner.md) | Hur tillsynen går till, vanliga brister, sanktionsstatistik, bristmönsterkatalog |
| [04-eu-regelverk.md](04-eu-regelverk.md) | AMLR, AMLA:s utkast till riktlinjer och svensk lagändring |
| [05-metod-och-arkitektur.md](05-metod-och-arkitektur.md) | FATF, OSCAL, regler som kod och val av arkitektur |
| [06-ai-och-teknik.md](06-ai-och-teknik.md) | Claude-API, Python-verktyg och datahantering |
| [07-referensdata-och-integrationer.md](07-referensdata-och-integrationer.md) | Listor, register och datakällor som behöver hållas aktuella |
| [08-lardomar-fran-ai-utkast.md](08-lardomar-fran-ai-utkast.md) | Vad ett tidigare AI-genererat dokumentpaket visar |
| [09-tillsynsbeslut-2026.md](09-tillsynsbeslut-2026.md) | Två fullständiga sanktionsbeslut från 2026: vad Länsstyrelsen underkänner, nya bristmönster B-23–B-29 |
| [typfall/tillsyn-2026.json](typfall/tillsyn-2026.json) | Två syntetiska granskningsfall, 17 förväntade fynd och fem kontrollvarianter med sidhänvisningar. Facitutkast för M2–M5 och M7. |
| [kallor.md](kallor.md) | Källförteckning med länkar |
| [verktyg/](verktyg/) | Skript som användes för att extrahera text och sammanställa statistik |

## Metod

1. Allt källmaterial (PDF, sparade webbsidor, Word, Excel, Pages) konverterades till text med [verktyg/extrahera_text.py](verktyg/extrahera_text.py). Dubbletter identifierades med kontrollsumma och lästes en gång.
2. Föreskrifterna från Länsstyrelsen i Stockholm och Västra Götaland jämfördes ord för ord.
3. Sanktionsbesluten på Länsstyrelsens webbsidor sammanställdes med [verktyg/sanktionsstatistik.py](verktyg/sanktionsstatistik.py).
4. Kompletterande webbresearch om EU-regelverket, metodstandarder och teknik. Källor i [kallor.md](kallor.md).
5. Användarens 79 fotograferade tillsynssidor importerades 2026-10-09 till ett lokalt arkiv utanför repot, med SHA-256, OCR och sidkarta. Användning och verifieringskommando finns i [09](09-tillsynsbeslut-2026.md#bevarat-underlag-och-återanvändbara-granskningsfall). Testindata är nyskrivna syntetiska omskrivningar.

Upphovsrättsskyddat material återges inte. Interna dokument från en referensbyrå och kunduppgifter har inte publicerats. De beskrivs bara på ett anonymiserat och övergripande sätt.

## De viktigaste slutsatserna

1. **Tillsynen frågar hur, inte att.** Mallar som inte anpassats till den egna verksamheten underkänns uttryckligen.
2. **Den allmänna riskbedömningen fäller flest.** Omkring 72 % av 185 publicerade ingripanden i Stockholm och Västra Götaland gäller den allmänna riskbedömningen, ensam eller tillsammans med rutinerna. Medianen för sanktionsavgifterna är 245 000 kr.
3. **Tillsynen är förutsägbar.** Länsstyrelsens standardföreläggande har 15 punkter som i praktiken är en kravspecifikation för programmet.
4. **Samma metod gäller före och efter 2027.** Svenska föreskrifter, FATF och AMLA:s utkast beskriver samma kedja: verksamhetsöversikt, inneboende risk, kontrollernas kvalitet, kvarstående risk och åtgärder.
5. **Regelverket ändras snart.** AMLR gäller från 2027-07-10, AMLA:s riktlinjer väntas under fjärde kvartalet 2026, och ny svensk penningtvättslag är på remiss. Regelbasen måste därför versionshanteras.
6. **AI ska skriva, inte besluta.** Ett tidigare AI-genererat dokumentpaket blev metodiskt bra men krävde många versioner, hade 79 öppna verifieringspunkter och gick inte att bevisa fullständigt. Strukturen i specen löser det med regelbas, deterministisk motor och validerad AI-text.
