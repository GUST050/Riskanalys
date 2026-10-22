# Oberoende slutgranskning av T och F, 2026-10-22

En fristående read-only granskare (gpt-6-astra) granskade hela diffen `f66a70f..70492b6` mot de båda planerna och designunderlaget. Inga fler granskare eller subagenter användes av granskaren. Slutomdömet var **med rättningar**: fyra Important, inga Critical eller Minor. Nedan bevaras de konkreta fynden och hur de prövas i den samlade rättningspassningen. Den slutliga fullsviten är en separat efterföljande leveransgrind; ingen andra granskning beställdes.

## Fynd och rättning

1. **Native scenarioreferenser.** Ett nytt schema-2-utkast saknar registrerade scenariokopplingar. Block 10 visade ändå gemensamma scenarier men sparad kontroll avvisades, eftersom formuläradaptern bara godtog registrerade kopplingar. Detta tvingade fram separata scenarioval före den samlade tjänstehandlingen. Granskaren följde även verklig ny tjänst T-RED-05 via plan, utvärdering, bedömning, skrivning och analysförnyelse; original/beslut hanterades rätt men samma sparfel uppstod. Rättningen tillåter tjänstens giltiga synliga standardförslag som utkastreferenser, utan att registrera eller bekräfta kopplingar. Native kontroll-/rutinprov och en verkligt bunden positiv kedja utan förberedda kopplingar verifierar vägen.
2. **Dolda aktiveringsskäl.** Den samlade vyn visade inte blockens aktivering/motivering men stämplade dem ändå. Unik motivering i block 3 saknades i HTML. Rättningen visar båda fälten för alla block; aktivt och ej tillämpligt block provas med HTML-escaping.
3. **Ändrade privata belägg.** F1 och F2 godtog ändrat privat kontrollbelägg och stämplade aktuella block, medan status redan rapporterade ändrade bytes. Senare godkännande/fastställelse spärrade fortfarande; detta var inte en påvisad kringgång av slutgrindarna. Rättningen läser samtliga registrerade privata analys-/modellbelägg under analyslåset med den befintliga säkra läsaren. Fyra bundna prov kontrollerar ändrad/saknad fil för båda handlingarna och oförändrad analysfil vid avslag.
4. **Ofullständigt verifieringssnapshot.** JSON-fixturer, YAML under testfixturer och regelbasens textkällor ingick inte i snapshotet. Rättningen omfattar alla filer under program-, test-, regelbas-, skript- och forskningsverktygsmapparna, med uttryckligt undantag endast för genererad bytekod/cache. Nio prov ändrar/lägger till/tar bort JSON, fixture-YAML och källtext under körningen och kräver ej verifierat resultat. Ett separat prov bevarar cacheundantaget.

## Styrkor och avgränsningar

Granskaren bekräftade exakt cellmängd/CAS, bevarade avvikelser, ordinarie tjänstesakgrind med globala poster och bevis kvar, inga automatiska analysbeslut/täckningsprövningar, verkliga positiva/negativa CLI-/HTTP-gränser, isolerade kloner och spårbar påståendematris. Ingen ny informationsförlust identifierades i D9-grupperingen.

Granskaren avgjorde inte följande; genomförandebeslut med kostnader finns också i slutprovet och den bevarade arbetsloggen:

- Slutlig fullsvit återstod efter granskningen och måste vara grön före leverans.
- Full kombinerad återinförandekedja efter en terminal plan kördes inte; befintliga planprov granskades och faktisk ny tjänst följdes. Separata livslopps-/förnyelseprov behålls.
- Juridisk/metodisk nivåkorrekthet och sakkunnigprövning kräver verklig sakgranskning.
- Ingen allmän rapportförkortning krävs utöver visad dubblering; ökningen redovisas öppet.
- Frysta jämförelsefall har avsiktliga sakluckor och får inte beskrivas som färdiga riskbedömningar.
- Ingen fullsidig Word-layoutkontroll eller uppmätt mänsklig lästid genomfördes; riktad kontroll redovisas som sådan.

Slutligt RED/GREEN-, fullsvits-, snapshot- och commitutfall anges i [leveransens slutprov](2026-10-22-engangssvar-slutprov.md). Inga Minor är uppskjutna från denna granskning. Ingen push eller merge ingår.
