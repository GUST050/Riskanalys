# Svar på plangranskning: förenklad riskbedömning

Datum: 2026-10-22. Produktbas `91a3ece`, godkänd design revision 2 vid `8379172`. Detta är ett svar på användarens granskning i chatten, inte en ny oberoende granskning eller en verifierad implementation.

[Plan A](../plans/2026-10-22-planaterkallelse-och-inforandeval-plan.md) är godkänd och lämnas oförändrad. [Plan B, planrevision 2](../plans/2026-10-22-forenklad-riskbedomning-plan.md) har reviderats enligt nedan. Designens revision ändras inte.

| Synpunkt | Kontroll och ändring i planrevision 2 |
|---|---|
| Under tröskel är inte i sig en modellucka | `bedomning/motor.py:_valda_sarbarheter` prövar villkoret före scenariots hot-/dimensionsfilter. Planens B3 kräver därför känt villkorsutfall med regel-/fältspår. 0,05 kontantandel mot S-KUND-02:s 0,1 ger upplysning, inget nytt riskutfall eller ensamt en spärr. Okänt är inte falskt. B5 samlar upplysningarna som underlag till befintligt D9 C, utan nytt beslutsprotokoll. |
| Saknad koppling måste vara ett uttryckligt påstående | Typad `Hotanknytning` anger just hot och dimension. Generell PT/TF-angivelse blir ingen automatisk korsprodukt och skapar ingen TF-konflikt ensam. Uttryckligt påstådd saknad koppling ger fortsatt metodkonflikt. Motorns ersättningsregler kan också förklara en frånvarande faktor och provas separat. |
| Egen sårbarhet behöver täckningsväg | Designens avsnitt 5 kräver detta; förra planen gjorde felaktigt varje omappad risk till en automatisk metodkonflikt. B2–B4 inför `Tackningsprovning` med samma tjänst, hot, dimension, lokalt händelseförlopp, valt riskled, jämförelsenivå, motivering och belägg. Scenario, nivå och innehållsbindning kontrolleras maskinellt; mekanismen motiveras av byrån och sakgranskas. Allmänt hög nivå räcker inte. Ej täckt eller oklar risk spärrar. B7 provar både giltig täckning och kvarstående hinder genom fastställelsen. |
| Flera leveranscommits | Efter B3, B5 och B7 rekommenderas commit med färsk grön fullsvit, regelbasvalidering och diffkontroll. CLI-import/validering flyttas fram till B3. Schema 2 väljs uttryckligen där; dess rapportstöd aktiveras först i B5. Schema 1 behåller fungerande ordinarie kedja under mellanleveransen. |
| Ogranskat kataloginnehåll | B1 kräver källa och `grund`, uttryckligt `sakkunnig.status: ej_granskad` för ändrat innehåll och märkning som ogranskat förslag. En gammal attest får inte ge sken av att omfatta ny text. |
| Miljöoberoende dokumentkontroll | B7 anger samma visuella godkännandekriterier med Codex-renderare eller Word/LibreOffice. Metod och faktiskt granskade sidor ska redovisas. |

## För Claude-granskningen

Användaren vill granska införandet med Claude. Läs planrevision 2 tillsammans med den godkända designens avsnitt 5 och denna ändringskarta. Kontrollera särskilt att:

- Ett neutralt under-tröskel-besked inte döljer ett separat uttryckligt påstående om högre, otäckt risk.
- Täckningsnivån jämförs för samma hot/dimension och samma riskled; inneboende nivå får inte styrka ett påstående om kvarstående risk.
- Nivåjämförelsen kompletteras med mekanism, belägg och sakgranskning. Den egna sårbarheten får inte försvinna för att en tjänst redan har hög nivå.
- Import och ändrade underlag inte återanvänder förfalskade/inaktuella bekräftelser eller täckningsprövningar.
- B3:s mellanleverans har användbar CLI och korrekt validering, tydligt avgränsat rapportstöd och grön fullsvit; inga gamla spärrprov har stängts av.

Vid faktisk leverans ska granskningsunderlaget innehålla bas/slut-SHA, diff, ändrade kontrakt, körda prov med utfall samt kvarstående begränsningar. De uppgifterna fylls först när genomförandet har skett.

## Verifieringsgräns

Kontrollen i denna omgång avser dokument och befintlig kod: villkorsutvärdering, okändhantering, scenario-/dimensionsfilter, ersättningsregler och befintliga riskfält. Produktkod, regelbas och tester är inte ändrade. Ingen ny fullsvit eller visuell produktkontroll har körts; planerade testfall är inte utförda prov.
