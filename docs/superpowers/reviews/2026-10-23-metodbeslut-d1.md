# D1 – löneberedning och momskarusell

Provisoriskt metodval, regelbas 2.3.0. Ingen sakkunniggranskning utförd. Ren T-RED-04 avgränsas från H-MOD-02. H-TJ-04 och H-02 kvarstår för lönens eget falska underlag respektive löneuttag av brottsvinst. Ett kombinerat moms-/betalningsuppdrag bedöms i sina erbjudna tjänster; ingen kundsamförekomst antas. Alternativet var fortsatt generell indirekt momsanknytning i lön.

Källa: läst marsvägledning 2025, fysisk PDF-sida 23, citat ”transportdokumenten”; NRA 2024/2025 7.19 s. 123, ”lön och utdelning”; tillsynsrapport 2026:14 s. 7, ”individuell analys”. Källorna ger stöd för arbetsmomentsprövning men föreskriver inte denna katalogavgränsning. Den är `metodval`, `ej_granskad`.

## Genomförande och granskning

Eget typat D1-objekt i `regelbas/beslutstabeller/metodbeslut.yaml` binder T-RED-04, H-MOD-02, H-TJ-04, H-02, C-TJ-04 och dess räckvidd KR-C-TJ-04-T-RED-04 samt de tre använda källposterna. H-MOD-02 tas även bort ur den okända räckviddens scenarieförteckning; kontrollens faktiska mål utvidgas inte.

D1 binder hela aktuella modellfilinventariet, modellidentiteten, laddning, validering, expertimport/-applicering och de två rapportmoduler som visar metoden. En ändrad sakpost eller genomförandefil ändrar beslutsattesten och ger valideringshinder. Tomt beslutsregister utelämnas i äldre regelbasers dump. Metodbeslut ingår i granskningsmall, import och ordinarie fastställelsespärr. Befintlig separat modellvalidering kvarstår. Den grova filbindningen innebär att en ändring i gemensam modellfil kräver ombindning av flera beslut; inget gammalt godkännande återanvänds tyst.

## Effekt och möjliga sänkningar

Tolv identiska profilbytes körda: sex frysta byråer, vardera ursprungligt ofullständigt och explicit kompletterat syntetiskt intag. Fulla tjänste-/scenarioutfall före/efter och samlat mot 2.0.0 finns i `.superpowers/evidens/2026-10-23-metodbeslut/D1/`. Beräkningen använder den faktiska modellen utan experimentmutation. Inga kvarvarande scenarioled sänks numeriskt av D1 och ingen tjänstnivå ändras. Fyra momsscenarier försvinner; detta redovisas som potentiell riskminskning i modellens täckning, inte som bevis för frånvaro av hot.

| Profilvariant | Ändrade tjänster | Sänkta kvarvarande led | Borttagna scenarier |
|---|---:|---:|---:|
| referens_standard_ursprunglig | 0 | 0 | 0 |
| referens_standard | 0 | 0 | 0 |
| referens_fyra_ursprunglig | 1 | 0 | 1 |
| referens_fyra | 1 | 0 | 1 |
| enmansbyra_ursprunglig | 0 | 0 | 0 |
| enmansbyra | 0 | 0 | 0 |
| betalningsmandat_ursprunglig | 1 | 0 | 1 |
| betalningsmandat | 1 | 0 | 1 |
| riskbranscher_ursprunglig | 0 | 0 | 0 |
| riskbranscher | 0 | 0 | 0 |
| fa_faktorer_ursprunglig | 0 | 0 | 0 |
| fa_faktorer | 0 | 0 | 0 |

## Avslag och återföring

Återställ eller villkora T-RED-04:s H-MOD-02-länk i ny regelversion, ompröva kontrollräckvidden, bind om D1 och alla senare beslut som binder samma objekt/filer. Räkna om sexfall och kontraster, uppdatera modellfacit/validering och bygg om analys-, skrivunderlags-, rapport-, PDF- och expertpaket. Nya samlade sakgranskningar krävs; låsta historiska paket bevaras. Separat commit är inte hela återföringsförfarandet.

Regelbasvalidering passerar. Regressioner är skrivna men ännu inte körda enligt användarens sluttestinstruktion. Testet som kräver alla tio beslut blir uppfyllt först efter hela D. Ingen grön fullsvit eller fastställelse påstås. Ingen push eller merge.
