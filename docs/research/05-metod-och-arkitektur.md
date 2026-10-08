# 05 Metod och arkitektur

## FATF: riskbaserat förhållningssätt för redovisningsbranschen (2019)

FATF:s vägledning delar riskbedömningen i:

- landrisk och geografisk risk
- kundrisk
- transaktions- och tjänsterisk
- variabler som påverkar risken
- dokumentation av riskbedömningen

Därefter följer riskreducering: kundkännedom, PEP, löpande övervakning och rapportering samt intern kontroll. Vägledningen betonar att byråer skiljer sig mycket åt i storlek och tjänsteutbud och att bedömningen ska anpassas därefter. Den tar inte hänsyn till FATF:s revidering av rekommendation 1 år 2025.

**Följd:** samma kategorier som i svenska föreskrifter och i AMLR. Hot- och faktorkatalogerna kan därför byggas en gång och märkas med vilken källa varje post stöds av.

## NIST OSCAL: krav som data i lager

OSCAL är NIST:s standard för säkerhetskrav. Den är inte en programvara utan ett dataformat i lager:

| OSCAL-lager | Motsvarighet i programmet |
|---|---|
| Catalog (krav med mål och bedömningsmetod) | Kravregister och kunskapskataloger |
| Profile (urval och anpassning) | Regelpaket |
| Component definition / System security plan (hur kraven uppfylls) | Byråprofil, rutiner och dokument |
| Assessment results (bedömning, belägg, fynd) | Granskare och drift |
| POA&M (åtgärdsplan) | Åtgärdslista |

Två principer tas över:

1. **Hänvisa, kopiera inte.** Senare lager refererar till poster i tidigare lager. Ett krav finns på ett ställe.
2. **Spårbarhet från bedömning till katalog.** Varje fynd pekar tillbaka på det krav det gäller.

OSCAL-formatet i sig används inte. Det är byggt för IT-säkerhet och skulle göra regelbasen svårare att läsa och redigera.

## Regler som kod

Erfarenheter från OpenFisca (Frankrike, Nya Zeeland m.fl.) och Catala:

- Logik som är gömd i kod blir en svart låda som inte går att granska. Reglerna ska vara läsbara för den som kan juridiken.
- Varje regel ska kunna testas mot ett konkret fall.
- Regler ändras över tid och ska versioneras med giltighetsdatum.
- Översättningen från lag till kod är ett påstående som ska verifieras. Catala-projektet hittade fel i officiella implementeringar.
- Beslutstabeller med en rad per regel, ID, källa och test per rad ger spårbarhet från regel till test till genomförande.

**Följd:** beslutstabeller i YAML med ID, villkor, utfall, källa, typ och förklaring. Ett test per rad. Sakkunniggranskning av regelbasen.

## Val av arkitektur

Tre alternativ jämfördes:

| Alternativ | Fördelar | Nackdelar | Beslut |
|---|---|---|---|
| 1 AI gör allt (promptkedja) | Snabbt att börja | Olika resultat varje körning, påhittade fakta, täckning kan inte bevisas, svårt att testa | Avvisat |
| 2 Regelbas och motor, AI som skribent | Reproducerbart, spårbart, testbart, återanvändbart mellan byråer, versionerbart | Mer arbete i början | **Valt** |
| 3 Textblock utan AI | Helt förutsägbart | Ger den generiska text som tillsynen underkänner | Avvisat |

## Riskskalor

| Källa | Skala |
|---|---|
| Nationell riskbedömning 2024/2025 | Fyra nivåer för penningtvätt. Terrorfinansiering beskrivs kvalitativt. |
| AMLA (utkast till RTS för tillsynens riskbedömning) | Kontrollkvalitet 1–4 |
| Branschlitteraturens exempel | Låg, normal, hög och mycket hög via matris av tjänsterisk och sannolikhet |
| Tidigare AI-utkast | Sannolikhet och konsekvens i tre nivåer, risk i fyra nivåer, terrorfinansiering separat med alltid allvarlig konsekvens |

**Följd:** fyrgradig riskskala som standard, för att kunna jämföras med den nationella riskbedömningen. Fyrgradig kontrollkvalitet. Skalorna är verksamhetens val och går att ändra.
