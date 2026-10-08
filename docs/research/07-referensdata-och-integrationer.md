# 07 Referensdata och integrationer

Data som ändras över tid och som regelbasen behöver hålla aktuell med datum och version.

| Referensdata | Källa | Uppdateras | Format och åtkomst | Används till |
|---|---|---|---|---|
| Penningtvättslagen (2017:630), konsoliderad | Riksdagens öppna data. Lagen.nu som sekundär kontroll. | Vid lagändring. Ändrad bland annat 2025 (SFS 2025:255 och 2025:603). Lagen.nu anger ändringar införda till och med SFS 2026:1075 (läst 2026-10-08). | REST-API med JSON och text. Exakt adress verifieras i M2. | Kravregister, paragrafkarta |
| Länsstyrelsernas föreskrifter | Länsstyrelsernas webbplatser | Vid ny föreskrift | PDF | Kravregister |
| EU:s förteckning över högrisktredjeländer | Delegerad förordning (EU) 2016/1675 med ändringar, EUR-Lex | Flera gånger per år | EUR-Lex | Geografiska riskfaktorer, kundmodell |
| EU:s konsoliderade sanktionslista | EU Financial Sanctions Files (FSF) | Dagligen | XML. Även via OpenSanctions. | Sanktionskontroll (fas 2), sanktionsrisk |
| FATF:s listor (förstärkt övervakning respektive uppmaning till åtgärder) | FATF | Tre gånger per år | Webbsida | Geografi |
| Korruptionsindex | Transparency International (CPI) | Årligen | Webbsida och CSV | Geografi |
| EU:s förteckning över icke samarbetsvilliga jurisdiktioner i skattefrågor | EU-rådet | Två gånger per år | Webbsida | Geografi |
| Nationell riskbedömning 2024/2025 | Samordningsfunktionen (Polisen) | Vart tredje till fjärde år | PDF | Sektorsrisk, hot |
| Polisens lägesbild över utsatta områden | Polisen | Periodvis | PDF | Lokal geografisk riskfaktor |
| Finanspolisens årsrapport och tematiska rapporter | Polisen | Årligen och löpande | PDF | Hot och varningssignaler |
| Länsstyrelsernas nyhetsbrev och ingripanden | Länsstyrelserna | Löpande | Webbsidor | Omvärldsbevakning, bristmönster |
| AMLA:s riktlinjer och tekniska standarder | AMLA | Löpande till 2028 | Webbsida och PDF | AMLR-regelpaket |

## Integrationer för kundnivån (fas 2)

| Integration | Status oktober 2026 | Kommentar |
|---|---|---|
| Bolagsverket: grundläggande företagsuppgifter | Kostnadsfritt API för värdefulla datamängder. Betald version med styrelse och firmateckning. | Identitetskontroll av juridisk person, registreringsbevis |
| Bolagsverket: registret över verkliga huvudmän | Prop. 2025/26:129 om elektroniskt utlämnande till verksamhetsutövare. Ändringarna föreslogs gälla från 2026-07-01. Inget bekräftat API. | Följs upp före fas 2 |
| BankID och e-legitimation | Via certifierade leverantörer | Identitetskontroll på distans |
| PEP- och sanktionskontroll | Kommersiella tjänster (till exempel Capego KYC) eller öppna data (OpenSanctions) | Verktygets kontroller ersätter inte konsultens bedömning |
| goAML | Finanspolisens rapporteringsportal | Ingen integration planeras. Programmet stödjer intern hantering och loggning. |

## Princip för referensdata

Varje lista lagras med källa, hämtningsdatum, giltighetsdatum och kontrollsumma. En bedömning låser vilka versioner den gjordes mot. När en ny version kommer jämför driften versionerna och visar vilka avsnitt och kunder som påverkas.
