# D – samlat underlag och slutkontroll av rapporten

D1–D9 och D-LAGRE är inbyggda som provisoriska `metodval`, samtliga `ej_granskad`, med egen regelversion 2.3.0–2.12.0 och egen lokal commit. [Genomförandeplanen](../plans/2026-10-23-metodbeslut-d.md) anger alternativ och ordning. Varje beslut har en egen granskningshandling i denna mapp, exakta sakobjekt-/filbindningar i regelbasen och före-/efterutfall inklusive kumulativ jämförelse mot 2.0.0. Inga verkliga expertattester, push eller merge.

- D1–D2: H-MOD-02 respektive H-01 avgränsas från ren löneberedning. H-TJ-04 och H-02 kvarstår. I tolv fasta profilvarianter försvinner fyra scenarier per steg, åtta samlat. Inga kvarvarande riskled eller tjänstnivåer sänks i sexfallen.
- D3–D6: konservativ portföljmodell, bara belagd kundsamförekomst, max per dimension och allvarlig TF-konsekvens behålls med uttryckliga evidensgränser. Beräkningen ändras inte.
- D7: ideell indikator verkar enbart i TF. [Sänkningsredovisningen](2026-10-23-metodbeslut-d7.md) visar åtta lägre inneboende PT-tjänstenivåer och en lägre kvarstående tjänstenivå i ideell-ensam-kontrasten. TF oförändrad. Ingen sänkning i de sex fasta fallen.
- D8–D9: befintlig scenario-/effektprövning och högst ett PT-steg respektive påslag/tak behålls. Inga utvidgade kontrollmål eller nya kalibreringspåståenden.
- D-LAGRE: alla fem indikatorer redovisas utan automatisk nivåeffekt. Saknat centralt landunderlag är fortsatt okänt.

## Reproducerbar evidens

`.superpowers/evidens/2026-10-23-metodbeslut/` innehåller 2.0.0-baslinje och varje stegs regelbas, modellfilmanifest, tolv identiska profilvarianter och fulla tjänste-/scenarioutfall. `kontraster3/` innehåller 40 validerbara profiler, varje stegs jämförelse och två tillåtna kundfördelningar med samma 60 kunder och marginaltal 24/24/24/24 men olika faktiskt överlapp (24 respektive 12 flertjänstkunder). Inga motorvikter ändras ur marginaltalen. Verktyg: `docs/research/verktyg/metodsteg.py` och `metodkontraster.py`.

## Rapport efter D – kontrollpunkt 4

Slutunderlag: `.superpowers/evidens/2026-10-23-rapport-v10-efter-d2/`, aktuell regelbas 2.12.0. Huvudrapporter **20/21 sidor**, A **38/40**, B1 **195/200**. Maskinfynd **430/432**, ofiltrerade, 0 presentationsfynd. Metodtabellen visar de tio faktiska provisoriska valen och deras status. Fyndminskningen i mandatfallet följer borttagna irrelevanta syntetiska mandatkopior av H-01/H-MOD-02; produktens kataloggrind behålls. Ursprungliga prov och misslyckat första efter-D-bygge finns kvar.

Båda huvudrapporterna är visuellt genomgångna på kontaktark. Inga ord utanför sidgränsen. Fulla originalmotiveringar, 33 högre och fem lägre indikatorer, 15 lagexempel och samtliga Word-stycken/-celler är kontrollerade. A/B1 motsvarar V9 från samma aktuella källor bortsett från formatstämpeln; deras innehåll följer regeländringarna. Datumtyper återställs enligt fältkatalogen vid kontroll från JSON så att bokstavliga datumspann jämförs korrekt. Bilagornas alla sidor är inte visuellt genomgångna i denna kontroll.

Tiorsidorsriktmärket är fortfarande inte uppnått. Ingen text har kapats. Användarens läsning/godkännande enligt kontrollpunkt 4 har begärts före E. Riktade samlade tester pågår; snabb/full återstår. Inget grönt slutbesked ges före faktisk verifiering.

## Kodreview och rättning 2.12.1

Fyra P2 rättade med RED→GREEN: besluten binder konservativt samtliga 244 Python-filer i appen (även transitiva hjälpare), källösa kundgrupper är okända, fria profiltexter bevaras bokstavligt i sammansatta stycken, och samtliga 40 kontraster jämförs också mot ursprungliga 2.0.0. Publik bygg_arb har fått saknad V10-dispatch, med först två röda och sedan två gröna prov. Äldre format behåller sina uttryckliga vägar.

Reviewurval: 26 godkända/26,93 s; inte grön fullsvit. Slutliga PDF:er i `.superpowers/evidens/2026-10-23-rapport-v10-slutkontroll/`. D-val och riskutfall är oförändrade mot 2.12.0. Patchen rättar belägg-/text-/attestbindning.

Kumulativa kontraster mot 2.0.0: 48 sänkta led och 80 borttagna scenarier. De 48 leden är två ekvivalenta ideellprofiler × sex jämförbara äldre tjänster × fyra led. D7:s stegvisa jämförelse innehåller också två nya tjänster T-RED-08/09, alltså 64 led. Dessa två saknar 2.0.0-utfall och får inte beskrivas som sänkta mot en obefintlig nivå. Fulla före-/efterutfall bevaras även för nya tjänster.

## PDF-klartecken, rättning 2.12.2 och E

Användaren har nu uttryckligen godkänt båda PDF:erna efter D. Fullsvitens två produktfynd är rättade: preliminära tjänster utan bekräftat utbud kan sorteras i V10, och lönefrågans iakttagna hot följer D1–D2:s katalogavgränsning. Båda reproducerades RED→GREEN; ny regelversion/D-bindning är 2.12.2. Tolv fasta profilvarianter har identiska tjänste- och scenarioled mot D-slut.

Nya huvud-PDF:er i `.superpowers/evidens/2026-10-23-rapport-v10-2.12.2/` är textidentiska med de godkända utom versionsangivelsen på första och sista sidan; samma sidantal och fyndantal. [E:s guide/paket och oberoende granskningsresultat](2026-10-23-regelbas-steg-e.md) är färdiga. [Ny fullsvit och exakta provresultat](2026-10-23-regelbas-slutprov.md) återstår före grönt slutbesked.
