# 08 Lärdomar från ett tidigare AI-genererat dokumentpaket

Under september och oktober 2026 togs ett dokumentpaket fram med AI-hjälp för en referensbyrå, i versionerna 0.7–0.11. Paketet består av allmän riskbedömning, rutiner och riktlinjer, kundformulär och kontrollista. Paketet publiceras inte här. Nedan följer de lärdomar som påverkar programmets design.

## Det som fungerade och tas över

| Inslag | Varför det är bra |
|---|---|
| Tjänstekatalog med 9 tjänster och undertjänster, där tjänster som inte erbjuds står kvar som "erbjuds ej" | Varje tjänst analyseras för sig, som tillsynen kräver |
| Hotkatalog med 15 hot, med berörda tjänster och källor per hot | Hoten kopplas till myndighetskällor |
| Sårbarheter per riskfaktor (kunder, kanaler, geografi, verksamhetsspecifika omständigheter, tjänstens egenskaper, terrorfinansiering) | Följer föreskriftens struktur |
| Genomgång av lagens exempel på låg och hög risk punkt för punkt | Visar att lagens exempel beaktats |
| Sannolikhet × konsekvens per tjänst med motivering och ett kombinationsscenario | Visar hur faktorer samverkar |
| Terrorfinansiering bedömd separat med alltid allvarlig konsekvens | Följer myndigheternas vägledning |
| Risk före åtgärder. Kontroller får sänka risken bara när effekten är utvärderad. | Samma princip som AMLA:s inneboende och kvarstående risk |
| Kundriskmodell i fem steg: hinder, alltid hög risk, poängsatta faktorer, lågriskfaktorer, nivå och justeringsregler | Enhetlig och spårbar |
| Svarsalternativen *Ja*, *Nej*, *Inte verifierat* och *Ej tillämpligt*, där en ej verifierad uppgift alltid ger det försiktiga svaret | Hindrar att okunskap ger låg risk |
| Lagkrav skilda från byråns egna val | Gör det tydligt vad som kan ändras |
| Kontrollista med statusnivåerna *beskrivet*, *infört* och *kontrollerat* | Skiljer text från verklighet |
| Kontrollplan med mått på åtgärdernas effekt | Ger belägg för kontrollernas genomförande |

## Problem som programmet ska lösa

| Problem | Belägg | Lösning i designen |
|---|---|---|
| Fakta om byrån saknas | 79 öppna `[VERIFIERA]`: 57 i riskbedömningen, 19 i rutinerna, 3 i kundformulären | Strukturerat intag före text. Profiluppgifter med status. |
| Täckningen går inte att bevisa | Kontrollistan byggdes i efterhand och har delvis beskrivna krav | Kravregister med täckningskontroll som stoppar export |
| Dokumenten hålls ihop för hand | Kravet att formulär och bilaga alltid ska ha samma versionsnummer. Riskbedömningen nådde version 0.19. | En datamodell som alla dokument genereras ur |
| Beskrivet men inte infört | Alla 65 kontrollpunkter har tomma fält för *Infört* och *Kontrollerat* | Driftdel med belägg som blir indata till nästa bedömning |
| För omfattande | Cirka 33 sidor riskbedömning och 40 sidor rutiner för en mindre byrå | Proportionalitetsnivå och korta arbetsinstruktioner per roll |
| Källor och datum går inte att lita på utan kontroll | Rapporttitlar, datum och landlistor angavs av AI | Regelbas med verifierade och daterade källor. AI får bara hänvisa till ID:n. |
| Skräddarsytt för en byrå | Ny genomgång krävs för varje byrå | Samma regelbas och motor för alla. Bara profilen skiljer. |

## Används som facit

- Referensbyråns ursprungliga dokument från 2023 ska **underkännas** av granskaren. Byrån fick sanktionsavgift för just dessa brister.
- Paketet i version 0.11 ska i stort **godkännas** och används för att kalibrera granskaren.
- Programmets egen version för samma byrå ska godkännas med färre öppna verifieringspunkter.
