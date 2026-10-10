# 02 Kravkarta

Översikt över skyldigheterna för verksamhetsutövare under Länsstyrelsens tillsyn och vad programmet ska leverera för var och en. Kartan är utgångspunkt för kravregistret (`regelbas/krav/`). **Lagrumshänvisningar ska verifieras mot gällande lydelse innan de förs in i regelbasen.**

PTL = lagen (2017:630) om åtgärder mot penningtvätt och finansiering av terrorism.
LSF = Länsstyrelsens föreskrifter (01FS 2024:20, 14FS 2024:11, 12FS 2024:8).

## Skyldigheter och utdata

| # | Skyldighet | Rättslig grund | Belägg som tillsynen vill se | Utdata i programmet |
|---|---|---|---|---|
| 1 | Anmälan till Bolagsverkets register mot penningtvätt och anmälan av ledningsförändringar. Registrering som rapportör i goAML hålls som separat operativ åtgärd. | PTL 7 kap. 3 och 6 §§; separat källa från Finanspolisen för goAML | Anmälningsdatum och aktuella uppgifter | Kravregister i M2, statuspost i drift och kravmatris i M4/M6 |
| 2 | Allmän riskbedömning: tjänster, hot, sårbarheter (kunder, kanaler, geografi, verksamhetsspecifika omständigheter) och motiverade risknivåer. Dokumenterad. Utvärderas minst årligen och före nya tjänster eller marknader. Datum anges. | PTL 2 kap. 1–2 §§; LSF 2 kap. 1–3 §§ | Dokumentet med datum | Allmän riskbedömning och metodbilaga |
| 3 | Riskbedömning av varje kund (riskprofil) | PTL 2 kap. 3–5 §§; LSF 2 kap. 4 § | Hur riskprofiler bedöms och följs upp | Kundriskmodell och kundformulär |
| 4 | Rutiner och riktlinjer med detaljerade handlingsregler, anpassade efter risk, storlek och art. Utvärderas minst årligen med datum. | PTL 2 kap. 8–10, 13, 15 §§ och 6 kap. 1 §; LSF 2 kap. 5–8 §§ | Dokumentet med datum | Rutiner och riktlinjer, arbetsinstruktioner |
| 5 | Kundkännedom: identifiering och identitetskontroll (tabell 1), ombud och företrädare, verklig huvudman (alltid sökning i Bolagsverkets register), alternativ verklig huvudman, PEP och RCA, högrisktredjeland, sanktionskontroll, syfte och art, förväntat beteende, förenklade och skärpta åtgärder, löpande uppföljning, stopp vid otillräcklig kännedom | PTL 3 kap.; LSF 3 kap. | Faktiska exempel per risknivå | Rutiner (fas 1). Kundmodul (fas 2). |
| 6 | Övervakning av affärsförbindelser och enstaka transaktioner. Granskning av avvikelser. Rapportering till Finanspolisen utan dröjsmål. Meddelandeförbud. | PTL 4 kap. | Antal rapporterade och ej rapporterade misstankar | Rutin och misstankelogg (fas 2) |
| 7 | System för uppgiftslämning: kunna svara om affärsförbindelser de senaste fem åren | PTL 4 kap. 6–7 §§; LSF 4 kap. | Strukturerat, sökbart system | Rutin, femårsregister (fas 2) |
| 8 | Bevarande av handlingar och behandling av personuppgifter: fem år, högst tio, sökbart | PTL 5 kap.; LSF 5 kap. | Rutin | Rutin |
| 9 | Intern kontroll: bedömning av om särskilda funktioner behövs, annars en funktion för regelefterlevnad. Det ska framgå vem som har funktionen. | PTL 6 kap. 1–2 §§; LSF 6 kap. | Namngivna funktioner, kontrollplan | Rutin, kontrollplan, drift |
| 10 | Personal: lämplighetsprövning, utbildning (dokumenteras med innehåll, namn och datum), skydd mot hot, hämnd och repressalier, visselblåsning | PTL 2 kap. 13–15 §§ och 6 kap. 4–5 §§; LSF 2 kap. 6, 9–12 §§ | Rutiner, utbildningsdokumentation | Rutiner, utbildningslogg |
| 11 | Uppgiftslämning till Länsstyrelsen periodiskt eller på begäran | LSF 7 kap. | Uppgifter om verksamhet, kunder, riskbedömningar och rutiner | Tillsynspaket och kundstatistik i profilen |

## Kontrollpunkter

Ett tidigare AI-genererat paket bröt ned kraven i **65 kontrollpunkter** i tre grupper:

- **S:** skapa rutiner och riktlinjer, 15 krav med delpunkter
- **L:** lär känna kunderna och riskbedöm dem, 27 krav med delpunkter
- **P:** kompletterande krav ur lag och föreskrifter, 8 krav

Varje kontrollpunkt har tre statusnivåer: *beskrivet*, *infört* och *kontrollerat*. Uppdelningen fungerar bra och återanvänds i kravregistret. Varje punkt ska dock verifieras mot källan, eftersom paketet genererades av AI.

## Krav som lätt missas

Följande krav fanns i lag eller föreskrift men saknades eller var otydliga i den ursprungliga dokumentationen hos referensbyrån:

- Datum för varje utvärdering och uppdatering ska framgå av dokumentet.
- Övervakningen ska fånga även aktiviteter som inte avviker men kan ingå i penningtvätt.
- Undantag från förbudet mot affärsförbindelse vid rättsligt förfarande (skatterådgivare).
- Undantag från rapporterings- och uppgiftsskyldighet för vissa anförtrodda uppgifter (PTL 4 kap. 8 §). Det prövas separat från kundkännedomsundantaget och är inte ett generellt undantag för alla skatterådgivningsuppgifter.
- Högrisktredjeland: skärpt övervakning och lagens informationskrav, med samtliga villkor prövade innan undantaget för vissa EES-filialer/dotterföretag används (PTL 3 kap. 17 §).
- Alternativ verklig huvudman även när den identifierade personen inte antas vara den verkliga huvudmannen.
- Distanskontroll utan e-legitimation har två moment: kontroll mot oberoende källa och sedan bekräftelse till folkbokföringsadressen eller vidimerad kopia.
- Förlängt bevarande efter begäran från myndighet och stopp för gallring.
- Registreringsbevis högst en vecka gammalt. Detta är ett allmänt råd och inte bindande.
- Modellriskhantering för riskmodeller (PTL 6 kap. 1 §).
- Utbildningen ska anpassas när riskbedömningen uppdateras.
- Slutsatser från hot och hämnd ska föras tillbaka till riskbedömningen (LSF 2 kap. 12 §).

Kompletterat 2026-10-10 mot [PTL:s officiella text](https://rkrattsbaser.gov.se/sfst?bet=2017:630); teknisk källkontroll, inte sakkunnigattest. Den fulla inventeringen och rättsliga avgränsningen finns i [research 10](10-kallkontroll-och-gapinventering-m2.md) och [M2-planen](../superpowers/plans/2026-10-10-m2-regelbas-v1-och-juridisk-granskning.md).
