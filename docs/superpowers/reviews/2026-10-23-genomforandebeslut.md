# Genomförandebeslut och kvarvarande begränsningar

Samtliga beslut noterade som `Ruling:` i arbetsloggen för C–E, i den ordning de fattades. Användarens uttryckliga val av rapportalternativ och PDF-godkännanden redovisas separat i plan/status och ändras inte här.

| Beslut | Grund och konsekvens om antagandet visar sig fel |
|---|---|
| Samla testerna till slutet där möjligt och fortsätt mellan arbetsstegen. | Användaren bad uttryckligen om detta. Fel kan upptäckas senare och kräva omtag; grön fullsvit krävs fortfarande före slutleverans. |
| Bind varje D-beslut till det gemensamma modell- och attestgenomförandet. | Ett beslut får inte skiljas från körbart genomförande. Gemensamma filändringar kan kräva ombindning och ny prövning av fler beslut. |
| Börja den enda samlade slutreviewns koddel medan PDF-kontrollen och E inväntas. | Användaren bad om snabbare genomförande. Samma reviewer måste även läsa den färdiga E-delen innan ett samlat slutomdöme kan ges. Detta är nu gjort. |
| Utvidga D-bindningen konservativt till samtliga 244 appfiler. | Ett konkret P2 visade saknade transitiva hjälpare. Även orelaterade appändringar kan nu kräva ombindning och ny expertprövning. |
| Lämna rättslig riktighet och metodkalibrering till verklig sakkunnig. | Alla val är provisoriska och `ej_granskad`; spärren står kvar. Modellen, faciten och rapporterna kan behöva ändras efter expertprövning. |
| Behåll fullständigt innehåll även över tiorsidorsriktmärket. | Uppdraget prioriterar innehåll och föreskriver faktisk PDF-kontroll; användaren har godkänt båda huvudrapporterna. Ett senare krav på tio sidor kan kräva redaktionell omarbetning och ny samlad granskning. |
| Behåll befintlig manifestintegritet utan ny signaturtjänst. | Ny identitets-/signaturinfrastruktur ingår inte i uppdraget. Befintlig begränsning kvarstår för en angripare som kan skriva om både alla filer och deras manifest. |
| Låt CLI `granska` bygga en ny rapport; vanlig uppdatering av äldre utkast behåller sparat format tills byte väljs. | Historiskt V9-paket verifierar, och explicit V8/V9/V10 täcks av regressioner. En annan önskad CLI-standard kräver separat flödesändring; historiska filer skrivs inte om. |
| Bevara äldre Europol-hash och bifoga endast rätt identifierad ny fil. | Exakta äldre PDF-bytes saknas; inget aktuellt granskat sakobjekt hänvisar till äldre ID. Det äldre originalet måste återanskaffas för historisk källkontroll. |
| Begränsa den visuella PDF-omkontrollen i E till huvudrapporterna och deras ändrade versionssidor. | Bilagornas fulla text, Word-innehåll, källor och bindningar kontrolleras maskinellt, men alla bilagesidor är inte visuellt genomgångna. Ett rent bilagelayoutfel kan kräva ny rendering och granskning före faktisk användning. |
| Låt huvudagentens exakta fullsvit vara slutlig teknisk kontroll. | E-reviewern har granskat paketen och har inte kört fullsviten eller gjort omreview av kodrättningarna. Nya testfel kräver rättning och en ny fullkontroll före grönt slutbesked. |

Inga mindre granskningsfynd skjuts upp. Samtliga betydelsefulla kodfynd har reproducerande prov; E:s paketeringsfynd har kontrollerats mot faktiska fil- och profilhashar. Aktuellt testutfall finns i [slutprovsunderlaget](2026-10-23-regelbas-slutprov.md). Ingen push eller merge.
