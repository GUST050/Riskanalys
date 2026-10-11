# Lås fakta i koden, låt Claude analysera

Promptarna bör byggas av **en gemensam systemprompt som aldrig ändras och ett eget användarmeddelande per dokumentdel**. I användarmeddelandet ligger faktabladet först inom XML-taggar och delens instruktion sist. Varje del ska alltså inte ha en egen systemprompt. För tjänsteavsnitten rekommenderas **ett anrop per analysdel** (design B). Anropen kedjas så att motiveringen och slutsatserna får de redan godkända delarna som underlag. Design A, ett anrop per tjänst för alla delar, behålls som jämförelse i utvärderingen. Delinstruktionerna skrivs som separata moduler, så att valet mellan A och B blir en inställning och inte kräver omskrivning. Den viktigaste ändringen gäller ändå inte promptens text. **Fyra av testkörningens fem underkännandeorsaker bör försvinna när tal, nivåmeningar, obligatoriska meningar, avsnitts-ID och formatet för oklarheter flyttas från prompten till kod och schema.** Det är en hypotes som piloten ska pröva, inte ett uppmätt resultat. Det följer Anthropics råd att det som kan kontrolleras i kod ska kontrolleras i kod. Varje analysdel motsvarar bindande krav i 2 kap. 1–2 §§ penningtvättslagen (PTL) och 2 kap. 2–3 §§ i Länsstyrelsernas föreskrifter, och varje del har sina återkommande tillsynsbrister. Delinstruktionerna ska därför styra mot fyra saker:

- hur utnyttjandet faktiskt går till hos just den här byrån
- nivåmotivering som en kedja av hot, sårbarhet och omfattning, med jämförelse mot den höga sektorsrisk som den nationella riskbedömningen (NRA) anger
- kontroller som beskrivs som riskminskande bara när effekten är belagd
- att få eller inga rapporter aldrig används som belägg för låg risk.

Den deterministiska valideraren ska fortsätta avgöra om ett utkast godkänns. Forskningen visar att en språkmodell som granskar sig själv utan extern kontroll sällan förbättrar resultatet. Valideraren behöver däremot rättas på en punkt (tusentalsavgränsare i tal) och få kontroller för varje del. Utvärderingen före drift bör bygga på 24–30 syntetiska byråprofiler med checklistor skrivna av en sakkunnig, tre lager av bedömning och sakgranskningstiden som mått på nyttan. **API-kostnaden för hela utvärderingen blir några hundra dollar. Det är den sakkunniges tid som begränsar.** Den största osäkerheten är att ingen har jämfört A och B för Claude 5.5 på svensk regeltext. Därför ska utvärderingen avgöra valet, inte den här rapporten.

## Fyra av fem underkännanden var kodens ansvar

Rekommendationen bygger vidare på dagens kod. **I dag skriver Claude bara ett avsnitt per tjänst**: riskmotiveringen under rubriken "Risknivåer och motivering". De övriga fem analysdelarna och alla byråövergripande avsnitt byggs av mallar i kod ([tjanstavsnitt.py](../../src/riskanalys/dokument/tjanstavsnitt.py); [arb.py](../../src/riskanalys/dokument/arb.py)). Systemprompten är en punktlista med tio regler utan skäl. Instruktionen ligger som ett fält i underlagets JSON och blandas alltså med data ([claude.py](../../src/riskanalys/dokument/claude.py); [underlag.py](../../src/riskanalys/dokument/underlag.py)). Projektets testkörning med en syntetisk byrå gav 12 anrop, 156 000 indatatoken och 87 000 utdatatoken. Den kostade 1,18 USD på Sonnet 5.5. **Utdata stod för 74 procent av kostnaden**, och ett anrop hade i snitt cirka 13 000 token in och 7 250 ut (anteckningar om Anthropics promptråd (lokal researchanteckning, inte i repot)). Rapporten handlar alltså om hur promptarna ska se ut när AI ska skriva fler delar än i dag.

Testkörningens fem underkännandeorsaker är den bästa vägledningen. De pekar mot kod, inte mot bättre prosa:

1. **Talet "2 300 000"** underkändes på grund av ett fel i valideraren. Mönstret `\d+(?:[.,]\d+)?` delar strängen i "2", "300" och "000", och de talen finns inte i underlaget ([validering.py](../../src/riskanalys/dokument/validering.py)).
2. **Nivåord om delfaktorer** lästes som motsägelser mot motorn. Den här orsaken behandlas för sig nedan.
3. **Oklarheter i fel format** kan uteslutas redan när svaret genereras, med en `enum` (en fast lista med tillåtna värden) i schemat.
4. **Avsnitts-ID skrivet med rubrik** försvinner om fältet tas bort, eftersom koden redan känner till ID:t.
5. **En saknad obligatorisk mening om sanktionsrisk** försvinner om koden skriver meningen själv. Datamodellen stöder redan stycken märkta `kalla: "regelbas"` ([modeller.py](../../src/riskanalys/dokument/modeller.py)).

Det är Anthropics egen princip. Enligt Anthropics granskningsguide för prompter ska det som kan kontrolleras i kod kontrolleras i kod. Uppslagstabeller, poängsystem och aritmetik flyttas till data och kod, och modellen får behålla bedömningsdelen (prompt-audit.md i Anthropics claude-api-skill (Anthropics claude-api-skill 2.1.293, `shared/prompt-audit.md`; lokal kopia, inte i repot)). Skill-filerna som citeras i rapporten är lokala, tillfälliga kopior av Anthropics claude-api-skill version 2.1.293. Där det finns en officiell webbsida länkas den i stället.

**Orsak 2 behöver en egen tolkning.** Anteckningen om Anthropics råd beskriver den som ett för brett mönster i valideraren. Men en mening som "risken för osanna fakturor är hög" är en riskgradering som regelmotorn aldrig har gjort, och projektets första regel säger att AI inte bestämmer några nivåer ([AGENTS.md](../../AGENTS.md)). Valideraren hade alltså rätt i sak. Det som saknades var att prompten förklarade varför. Rätt åtgärd har tre delar. Koden skriver alla nivåmeningar. Prompten förklarar, med några exempel, att delfaktorer beskrivs med uppgifter (andel, antal, period, egenskap) och inte med nivåord. Mönstret i valideraren behålls lika strängt som i dag.

Forskningen stöder den här arbetsfördelningen. Även när en modell bara ska återge givna fakta blir det ofta fel. I Kasner och Dušeks test av öppna modeller hade **över 80 procent av texterna minst ett semantiskt fel** ([ACL 2024](https://aclanthology.org/2024.acl-long.651)). På Google DeepMinds test FACTS Grounding var de bästa modellerna helt grundade i underlaget i 62–84 procent av fallen när testet lanserades ([arXiv 2501.03200](https://arxiv.org/pdf/2501.03200)). Siffrorna gäller äldre eller andra modeller än Claude 5.5, men de pekar åt samma håll. Tidigare forskning om text som skrivs ur tabeller tog bort påhittade tal genom att låta modellen skriva platshållare som koden sedan fyllde i ([ACL 2021](https://preview.aclanthology.org/moar-dois/2021.acl-long.115.pdf)).

Slutsatsen för Riskanalys: **koden äger allt som är fakta eller beslut, det vill säga tal, nivåer, obligatoriska meningar, datum och källförteckningar. Claude skriver den analyserande texten mellan dem.** Den texten förklarar hur tjänsten kan utnyttjas hos just den här byrån, varför en uppgift spelar roll och hur faktorerna samverkar. Det är också den text som tillsynen oftast saknar, vilket avsnittet om regelkrav visar.

## En gemensam systemprompt, faktabladet först och uppgiften sist

På den första delfrågan är underlaget entydigt och anteckningarna eniga: **en gemensam systemprompt för alla anrop och ett eget användarmeddelande per dokumentdel**, inte en separat systemprompt per del. Anthropic lägger rollen i systemprompten ("Even a single sentence makes a difference"). Långa dokument ska ligga högst upp och frågan sist. I Anthropics tester gav det upp till 30 procent bättre svar för komplexa underlag på över 20 000 token ([Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)). Faktabladet här är cirka 13 000 token, så vinsten är inte säker, men ordningen kostar inget. XML-taggar som `<faktablad>`, `<uppgift>` och `<exempel>` håller isär instruktioner och data, vilket dagens kod inte gör när instruktionen ligger som ett fält i underlagets JSON.

Cachning av prompten (prompt caching) leder till samma upplägg. Cachningen jämför början av varje anrop med tidigare anrop, och varje ändrad byte gör allt efter den ogiltigt. Systemprompten ska därför vara exakt densamma i varje anrop, utan datum och utan avsnitt som bara tas med ibland. JSON ska skrivas med sorterade nycklar (prompt-caching.md (Anthropics claude-api-skill 2.1.293, `shared/prompt-caching.md`; lokal kopia, inte i repot)). En prompt måste vara minst 512 token lång för att cachas på Opus 5.5 och Sonnet 5.5. Dagens systemprompt är cirka 170 ord och cachas därför troligen inte alls. **Cachningen sparar ändå lite pengar.** En cachad systemprompt på 3 000 token över fem anrop sparar ungefär 0,03 USD på Sonnet 5.5, eftersom det är utdata som kostar ([Pricing](https://platform.claude.com/docs/en/about-claude/pricing)). Det starkaste skälet för en gemensam prompt är att reglerna och skälen bakom dem finns på ett enda ställe och inte glider isär mellan kopior.

Hur prompten skrivs spelar större roll än var den ligger. Anthropic skriver att prompter för äldre modeller ofta styr för hårt för dagens modeller och "actively degrade behavior". Tryckspråk som `CRITICAL: You MUST` ska ersättas med raka formuleringar. Regler i punktlistor skiljs från sina skäl ("sever rules from reasons") (prompt-audit.md (Anthropics claude-api-skill 2.1.293, `shared/prompt-audit.md`; lokal kopia, inte i repot)). Att förklara varför fungerar bättre än ett naket förbud, eftersom modellen kan tillämpa förklaringen på nya fall ([Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)). Förbud som speglar verkliga regel- eller efterlevnadskrav ska däremot stå kvar, helst med skälet bredvid.

Dagens tio punktregler bör därför skrivas om som löptext med "eftersom". Två exempel:

- AI återger inte nivåerna, eftersom bara regelmotorn bedömer risk och dokumentet ska kunna spåras vid tillsyn.
- Personer skrivs som platshållare för sin roll, eftersom underlaget är avidentifierat.

Bristmönstren skickas i dag som en lista med namn i datafältet `undvik`. De bör i stället förklaras i delinstruktionen, eftersom en förbudslista kan dra modellen mot just det felet ("anchor it toward that failure").

Exempel är enligt Anthropic "one of the most reliable ways to steer" format och ton. Rådet är 3–5 varierade exempel inom `<example>`-taggar, märkta som illustrativa. Ett enda mönsterexempel gör att modellen härmar det för nära ([Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)). I Riskanalys passar exempel bäst där formen är känslig:

- hur en delfaktor beskrivs utan nivåord
- hur `[VERIFIERA]` och en oklarhet skrivs
- hur ett stycke väljer sina referenser.

Exemplen ska bygga på syntetiska fakta som tydligt skiljer sig från riktiga, så att modellen inte kopierar innehållet. Instruktioner som "tänk noga" bör strykas för Opus 5.5, eftersom det är effortnivån som styr hur mycket modellen tänker ([Prompting Claude Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5)).

Anthropic har ingen dokumentation om svensk utdata, och ingen studie i underlaget mäter fel i svenska talformat eller i svensk text skriven ur data. Promptens stil påverkar svarets stil ([Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)), så prompten bör skrivas på samma sakliga svenska som dokumentet.

### Schemat garanterar formen i stället för att be om den

Strukturerad utdata (structured outputs) garanterar på båda modellerna att svaret följer JSON-schemat, eftersom modellen bara kan välja tecken som schemat tillåter. Schemat kan använda bland annat `enum`, `const`, `required` och `$ref`, men inte längdgränser, talintervall eller rekursion, och `additionalProperties: false` krävs ([Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)). Funktionen kan inte kombineras med Anthropics API för källhänvisningar (Citations), så projektets egna referens-ID:n är rätt sätt att knyta texten till underlaget. Det beslutet har specen redan tagit ([spec 8.3](../superpowers/specs/2026-10-08-riskanalys-design.md)). Tre detaljer gör stor skillnad:

- **Alla fält ska vara obligatoriska.** Fälten kommer i schemats ordning, men obligatoriska fält före valfria.
- **`referenser` ska ligga före `text` i varje stycke.** Då väljer modellen sina fakta innan den skriver meningen. Det motsvarar metoden "Attribute First, then Generate": när innehållet valdes före skrivandet blev citaten kortare och tiden för faktagranskning nästan halverades ([Slobodkin m.fl., ACL 2024](https://arxiv.org/pdf/2403.17104)).
- **Schemat ska inte ha något fält som ber om modellens resonemang.** Ett sådant fält kan leda till att modellen avböjer (`reasoning_extraction`). Resonemanget sker i modellens tänkande ([Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)).

Den sista punkten är särskilt viktig för Sonnet 5.5. Med strukturerad utdata innehåller svaret bara JSON, så modellen kan resonera bara i sitt tänkande, och på effortnivåerna `low` och `medium` hoppar den ibland över det. Anthropic rekommenderar raden "Think the problem through before you answer." sist i systemprompten. På `high` gav raden nästan samma korrekthet som `xhigh`, mot en måttlig ökning av antalet utdatatoken ([Prompting Claude Sonnet 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5)). Mätningen gällde resonemangsuppgifter, inte lång prosa.

En ofta citerad studie ("Let Me Speak Freely") fann att JSON-format gav stora försämringar på matematikuppgifterna i GSM8K. En upprepning med likvärdiga prompter fann ingen skillnad. Försämringen berodde på att svaret placerades före resonemanget ([Tam m.fl.](https://arxiv.org/html/2408.02442v1); [dottxt](https://blog.dottxt.ai/say-what-you-mean.html)). För uppgifter som handlar om att återge och formulera, som här, är stödet för att JSON försämrar resultatet svagt.

## Ett anrop per analysdel, kedjat där delarna bygger på varandra

Här går anteckningarna isär, och frågan avgör hur anropen ska ordnas.

**Anteckningen om Anthropics råd förordar ett anrop per tjänst** som skriver alla sex delar. Delarna bygger på samma fakta och måste hänga ihop, och Anthropic skriver att adaptivt tänkande låter Claude sköta det mesta av resonemanget i flera steg internt ([Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)). Anteckningen stöder sig också på en mätning där en ensam modell slog en samordnande modell "when the work is one dependent chain, or fits in a single context" (cost-optimization.md (Anthropics claude-api-skill 2.1.293, `shared/cost-optimization.md`; lokal kopia, inte i repot)).

**Anteckningen om grundad textgenerering förordar ett anrop per del.** Den bygger på tre studier:

- Följsamheten sjunker när antalet samtidiga krav växer. I en färsk preprint bröt den samman vid mer än ungefär 5–6 villkor. Att planera före skrivandet flyttade inte gränsen, och självkorrigering flyttade den bara 1–2 villkor ([arXiv 2608.12426](https://arxiv.org/pdf/2608.12426)).
- I IFScale klarade den bästa frontmodellen 68 procent vid 500 krav. Claude-sonnet-4 försämrades i jämn takt, och modellerna följde helst instruktioner som stod tidigt ([arXiv 2507.11538](https://arxiv.org/html/2507.11538v1)).
- I mallstyrda finansrapporter gav en kedjad prompt per avsnitt signifikant bredare täckning än agenter som fick hela mallen på en gång ([Tian m.fl., SIGIR 2025](https://arxiv.org/abs/2504.14233)).

Båda ståndpunkterna har svagheter. Mätningen som anteckningen om Anthropics råd lutar sig mot gällde en samordnande modell som lämnar över arbete till billigare modeller, inte en fast kedja av avsnittsprompter till samma modell. Den är alltså en analogi och inget belägg. Studierna om antalet villkor gäller andra modeller än Claude 5.5 och krav på nyckelord snarare än regelstyrd prosa. En studie av flera uppgifter i samma anrop fann att det gick 1,46 gånger snabbare och gav upp till 12 procent bättre resultat, men den gällde korta, oberoende uppgifter ([MTI Bench](https://huggingface.co/papers/2402.11597.md)). Ingen källa mäter sammanhang och motsägelser mellan avsnitt när ett enda anrop jämförs med kedjade anrop i långa regelstyrda dokument.

Avgörandet ligger därför i hur Riskanalys är byggt, och där talar tre omständigheter för uppdelning:

1. **Delarna hänger redan ihop genom faktabladet och regelmotorn.** Motorn har bestämt vilka hot, sårbarheter och kontroller som gäller och vilka nivåer tjänsten har. Delarna hänger ihop genom att peka på samma ID:n och behöver inte känna till varandras text. Argumentet om sammanhang väger därför lättare här än vid fri skrivning.
2. **Varje del har egna regelkrav och fällor.** Avsnittet om regelkrav visar fyra till sex obligatoriska element och tre till fem fällor per del. Ett anrop för sex delar skulle alltså bära uppemot fyrtio delspecifika regler samtidigt, långt mer än de mätta modellerna klarar pålitligt.
3. **Varje del ska kunna granskas och valideras för sig.** Anthropic skriver att explicit kedjning fortfarande är användbar "when you need to inspect intermediate outputs or enforce a specific pipeline structure" ([Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)). Validering per del ger dessutom riktade omförsök: bara den del som underkändes skrivs om, med återkoppling som bara gäller den.

Projektets egen stilregel, "Små filer med en uppgift var", pekar åt samma håll ([AGENTS.md](../../AGENTS.md)).

**Rekommendationen blir design B som standard, med en kedja för de delar som bygger på andra delar:**

- **Beskrivning och omfattning förblir kod.** Byråns egna fritexter skickas inte till AI ([STATUS](../STATUS.md)), och resten av delen består av tal.
- **Hot, sårbarheter och kontroller skrivs parallellt** ur samma cachade faktablad.
- **Motiveringen** får de godkända texterna från de tre delarna i en egen tagg och ska bygga vidare på dem utan att upprepa dem.
- **Slutsatserna** får den godkända motiveringen.

Kedjan motverkar upprepning, som är den största risken med uppdelningen. STORM-projektet skriver text avsnitt för avsnitt och rapporterar just att orelaterade fakta kopplas ihop ("over-association of unrelated facts") och att texterna krävde betydande redigering ([STORM](https://arxiv.org/abs/2402.14207v2)).

Det viktigaste är att **delinstruktionerna skrivs som separata moduler**. Design A blir då samma moduler sammanfogade i ett anrop, med ett schema med sex fält. Valet mellan A och B blir en inställning som utvärderingen kan mäta, inte en omskrivning. Om A klarar samma krav med kortare sakgranskningstid eller lägre kostnad per godkänt avsnitt ska A väljas.

De byråövergripande avsnitten har andra fakta och andra krav än tjänsteavsnitten och bör få egna anrop. Där är anteckningarna eniga. AI gör mest nytta i fem avsnitt:

- motiveringen av omfattningen (D-ARB.2)
- hur källorna och byråns egen erfarenhet påverkat bedömningen (D-ARB.4)
- de gemensamma sårbarheterna (D-ARB.5)
- bedömningen av kontrollerna (D-ARB.7)
- följderna för rutinerna (D-ARB.9).

Syfte och ansvar, listan över tjänster, risksammanställningen och avsnittet med datum är listor, tabeller och datum som ska förbli kod.

### Omförsök, effort och modell

Antalet omförsök har stöd både i specen och i forskningen. Specen stoppar ett avsnitt efter tre försök ([spec 8.2](../superpowers/specs/2026-10-08-riskanalys-design.md)). I studien Self-Refine kom den största förbättringen redan i första omarbetningen, utom för uppgifter med många villkor, medan kostnaden växer ungefär lika mycket för varje omarbetning ([Madaan m.fl.](https://arxiv.org/html/2303.17651v2); [arXiv 2608.10729](https://arxiv.org/pdf/2608.10729)). I samma studie slog specifik och konkret återkoppling allmän återkoppling i alla uppgifter. Valideraren vet exakt vad som är fel, så återkopplingen bör citera meningen, säga vad som var fel och ange vad som är tillåtet.

Anthropic rapporterar att det lönar sig att köra om underkända fall på en högre effortnivå. I deras körningar blev andelen godkända lika hög som när allt kördes på den högre nivån, till lite mer än halva kostnaden (cost-optimization.md (Anthropics claude-api-skill 2.1.293, `shared/cost-optimization.md`; lokal kopia, inte i repot)). Ett fel som finns kvar efter två omförsök tyder på ett systematiskt problem. Då bör delen falla tillbaka på dagens mall, och ett granskningsfynd skapas.

Effortnivån bör först följa Anthropics standard och sedan mätas:

- **Opus 5.5** har `medium` som standard och **Sonnet 5.5** `high`. Anthropic säger åt användaren att ange effort uttryckligen och prova nivåerna en i taget. Opus 5.5 på `medium` är minst lika bra som Opus 5 på `high` för kunskapsarbete, med ungefär 40 procent färre utdatatoken ([Effort](https://platform.claude.com/docs/en/build-with-claude/effort); [Prompting Claude Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5)). Kodens `STANDARDEFFORT = "high"` för Opus 5.5 ligger alltså en nivå över Anthropics standard ([claude.py](../../src/riskanalys/dokument/claude.py)).
- **Källorna säger olika om startnivån för textskrivning på Sonnet 5.5.** Den officiella promptsidan anger `high` och skill-dokumentet `low`. Den officiella sidan bör gälla som start, och mätningen får avgöra ([Prompting Claude Sonnet 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5)).
- **Effort ska vara fast per anropstyp**, eftersom ett byte gör cachen ogiltig.
- **Ett avbrott på `max_tokens`** ska räknas som ett misslyckat försök även när JSON:en är giltig.

Opus 5.5 är enligt Anthropic "much less likely to state an incorrect figure or cite the wrong source" ([Prompting Claude Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5)). Det gör modellen till en stark kandidat, men den kostar dubbelt så mycket per token och måste visa sig bättre i mätningen.

På Sonnet 5.5 kan säkerhetskategorin `general_harms` avböja även harmlöst arbete. Serverns automatiska reserv (server-side fallback) försöker då inte igen, eftersom den bara gäller kategorierna `cyber` och `frontier_llm` ([Prompting Claude Sonnet 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5)). Avböjanden ska därför loggas och kunna köras om på Opus. Batch API halverar alla tokenpriser men tar inte emot parametern `fallbacks` ([Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing)).

### Uppdelningen kostar mer i API men lite i kronor

Med ett anrop per del tänker modellen i varje anrop, och det är den verkliga merkostnaden. En uppskattning med uttalade antaganden:

- **Utgångspunkt.** Dagens enda AI-del gav i snitt cirka 7 250 utdatatoken per anrop på Sonnet 5.5 `high`. Antagandet är att varje delanrop kostar ungefär lika mycket.
- **Design B** för en byrå med fem tjänster blir då cirka 30 anrop: fem AI-delar per tjänst plus fem byråövergripande avsnitt. Det ger omkring **2,5–3 USD per körning** på Sonnet 5.5, före omförsök. Tack vare cachningen stannar indatadelen på cirka 0,4 USD.
- **Design A** med sex anrop och 10 000–15 000 utdatatoken per anrop hamnar runt **0,75–1 USD**.
- **Opus 5.5** har dubbelt tokenpris men använder troligen färre utdatatoken på `medium`. **Batch** halverar alla priser ([Pricing](https://platform.claude.com/docs/en/about-claude/pricing)).

Samtidigt blir omförsöken billigare med uppdelningen, eftersom bara en del skrivs om. Även om B kostar tre gånger så mycket rör det sig om några dollar per byrå och år. Det kan jämföras med medianavgiften på 245 000 kronor i publicerade ingripanden ([research 03](03-tillsyn-och-sanktioner.md)) och med den sakkunniges tid för granskningen. API-kostnaden ska därför inte avgöra valet av design. Det ska sakgranskningstiden och kvaliteten göra.

## Tillsynen läser en kedja från tjänst till följd

Lagen och föreskrifterna kräver ingen bestämd mall eller ordning. De kräver att vissa analys- och dokumentationssteg går att följa.

**Penningtvättslagen.** Enligt PTL 2 kap. 1 § ska bedömningen visa hur byråns tjänster kan utnyttjas för penningtvätt eller finansiering av terrorism och "hur stor risken är för att detta sker". Byrån ska särskilt ta hänsyn till tjänster, kunder, distributionskanaler och geografiska riskfaktorer. Den ska också ta hänsyn till uppgifter från sin egen rapportering och till myndigheternas information om tillvägagångssätt. Enligt 2 kap. 2 § bestäms omfattningen efter byråns storlek, art och risker. Bedömningen ska kunna ligga till grund för rutinerna och ska dokumenteras och hållas uppdaterad ([PTL](https://rkrattsbaser.gov.se/sfst?bet=2017:630)).

**Länsstyrelsernas föreskrifter.** 2 kap. 2 § i 14FS 2024:11 gör fyra moment obligatoriska ([14FS 2024:11](https://www.lansstyrelsen.se/download/18.74c322ef18f9ee08a2929/1716358223326/2024-11%20Penningtv%C3%A4tt%20Dalarnas%20l%C3%A4n%20G%C3%A4vleborgs%20l%C3%A4n%20Hallands%20l%C3%A4n%20V%C3%A4rmlands%20l%C3%A4n%20V%C3%A4stra%20G%C3%B6talands%20l%C3%A4n%20%C3%96rebro%20l%C3%A4n.pdf)):

1. identifiera tjänsterna
2. identifiera och analysera hot, med särskild hänsyn till uppgifter från byråns egen rapportering
3. identifiera och analysera sårbarheter
4. värdera riskerna; "Verksamhetsutövaren ska motivera angivna risknivåer."

Enligt 2 kap. 3 § ska bedömningen utvärderas minst en gång om året och innan byrån erbjuder nya eller väsentligt ändrade tjänster. Datum för utvärdering och uppdatering ska framgå av dokumentet.

**Kopplingen till resten av lagen.** Kundens riskprofil (PTL 2 kap. 3 §), rutinerna (2 kap. 8 §) och utbildningen (2 kap. 14 §) ska alla utgå från den allmänna riskbedömningen ([PTL](https://rkrattsbaser.gov.se/sfst?bet=2017:630)).

**Länsstyrelsernas vägledning** lägger till fem punkter ([Gör en allmän riskbedömning](https://www.lansstyrelsen.se/vastra-gotaland/samhalle/betalning-ekonomi-och-pengar/forhindra-penningtvatt-och-finansiering-av-terrorism/gor-en-allman-riskbedomning.html); [Rapport 2026:14](https://www.lansstyrelsen.se/download/18.51b8c30c19d05558bd82e18e/1774259142687/Erfarenheter%20fr%C3%A5n%20l%C3%A4nsstyrelsernas%20penningtv%C3%A4ttstillsyn.pdf)):

- Varje tjänst ska få en nivå, och motiveringen ska redovisas tydligt.
- Risk beskrivs som sannolikheten att hot utnyttjar sårbarheter, och alla riskfaktorer vägs samman per tjänst.
- Det är frivilligt att ta med kontroller. Tas de med ska deras effekt bedömas innan riskerna vägs samman.
- Det ska framgå hur omfattningen har bestämts.
- Källorna ska anges.

Tillsynsbesluten visar vad som faktiskt underkänns. Länsstyrelsernas rapport 2026:14 räknar upp brister som återkommer ([Rapport 2026:14](https://www.lansstyrelsen.se/download/18.51b8c30c19d05558bd82e18e/1774259142687/Erfarenheter%20fr%C3%A5n%20l%C3%A4nsstyrelsernas%20penningtv%C3%A4ttstillsyn.pdf)):

- för allmänt hållna mallar
- hot och sårbarheter som räknas upp utan analys
- tjänster som beskrivs tillsammans
- kunder som delas in efter bransch utan förklaring av hur det ökar risken
- distributionskanaler som inte analyseras
- geografi som bara kopplas till sanktionslistor
- nivåer utan analys
- alla tjänster bedömda som låga utan hänsyn till sektorsrisken i den nationella riskbedömningen.

Två beslut från 2026 underkände också fyra saker ([research 09](09-tillsynsbeslut-2026.md)):

- en gemensam nivå för alla tjänster
- att omfattningen inte framgick
- att samverkan mellan riskfaktorer bara beskrevs allmänt
- att källor räknades upp utan att det framgick hur de använts.

Besluten återger Kammarrätten i Göteborgs dom i mål 6806-23: det räcker inte att räkna upp riskområden, utan byrån ska visa hur ett utnyttjande faktiskt skulle gå till i den egna verksamheten. Domen är inte läst i original. Omkring 72 procent av 185 publicerade ingripanden i Stockholm och Västra Götaland gäller den allmänna riskbedömningen ([research 03](03-tillsyn-och-sanktioner.md)). Siffran bygger på en klassificering efter textmönster.

Myndigheternas underlag sätter riktningen för innehållet. Den nationella riskbedömningen 2024/2025 bedömer **sektorsrisken som hög** för bokförings- och revisionstjänster, skatterådgivare och bolagsbildare. Den beskriver tillvägagångssätt som osanna fakturor, brottsvinster som bokförs som försäljning och tas ut som lön, felbetalningar och omvänd penningtvätt. Om de 140 misstankerapporterna från sektorn 2024 skriver den att det är "förhållandevis få rapporter i förhållandet till sektorns storlek" ([NRA 2024/2025](https://polisen.se/0c34c8d8c94e1a371d8cca457b84fb0a/siteassets/dokument/om-polisen/penningtvatt/nationell-riskbedomning-av-penningtvatt-och-finansiering-av-terrorism-i-sverige-2024_2025.pdf)). EU-kommissionens överstatliga riskbedömning från 2022 drar samma slutsats om de flesta yrken utanför finanssektorn: få rapporter visar att "suspicions are not being effectively detected and reported" ([SNRA 2022](https://amlcft.public.lu/dam-assets/portail-lbcft/evaluations-des-risques/i-2022-snra-outcomes-mitigating-measures-and-recommendations.pdf)).

EU-reglerna och FATF beskriver samma kedja:

- **AMLR.** Från 2027-07-10 kräver EU:s penningtvättsförordning (AMLR) art. 10 att bedömningen minst beaktar riskvariablerna i bilagorna I–III, den överstatliga och den nationella riskbedömningen samt kundbasen. Den ska också omfatta risken att riktade ekonomiska sanktioner kringgås, och den ska godkännas av ledningsorganet ([AMLR](https://eur-lex.europa.eu/legal-content/SV/TXT/HTML/?uri=CELEX:32024R1624)).
- **AMLA:s utkast.** EU:s penningtvättsmyndighet AMLA har tagit fram ett utkast till riktlinjer. Remisstiden stängde 2026-07-15, och slutliga riktlinjer väntas tidigast under fjärde kvartalet 2026. Enligt utkastet får bedömningen inte vara "a mere formalistic exercise". Kontrollerna bedöms på utformning och genomförande med belägg, och hög inneboende risk "cannot be completely mitigated by control measures" ([AMLA:s konsultationsdokument](https://www.amla.europa.eu/document/download/f2db8372-e12a-4818-a991-6a3d45a0cd91_en?filename=Consultation%20Paper%20On%20draft%20Guidelines%20under%20Article%2010%284%29%20of%20Regulation%20%28EU%29%2020241624.pdf)).
- **FATF.** Den internationella arbetsgruppen FATF:s vägledning för redovisningsyrket från 2019 kräver en helhetsbedömning och "a short explanation of the reasons for each attribution". Den varnar för att lita helt på en checklista ([FATF RBA Accounting Profession](https://www.fatf-gafi.org/en/publications/Fatfrecommendations/Rba-accounting-profession.html)).

Av detta följer fyra regler som gäller alla delinstruktioner:

1. Varje påstående bygger på byråns egna uppgifter, med omfattning och period.
2. Varje nivå motiveras som hot, sårbarhet och omfattning, och nivån kommer från motorn.
3. En kontroll beskrivs som riskminskande bara när effekten är belagd.
4. Att byrån saknar rapporter, utlandskunder eller incidenter används aldrig som belägg för låg risk.

Källorna drar åt olika håll på tre punkter, och prompterna bör ta ställning:

- **Långa kundrelationer.** FATF punkt 81 anger att långvariga relationer med tät kontakt "may present less risk". Länsstyrelsernas rapport ser nära relationer som en sårbarhet, eftersom byrån kan bli mindre vaksam. För svensk tillsyn bör texten behandla långa relationer som en sårbarhet och nämna en positiv effekt bara om den kan beläggas.
- **Olika skalor.** NRA:s skala (låg, medel, betydande, hög) och motorns skala (låg, måttlig, hög, mycket hög) skiljer sig. Hur de jämförs är ett metodval som ingen källa avgör. Därför ska koden skriva jämförelsemeningen, inte AI.
- **Krav som ännu inte gäller.** AMLR:s krav om sanktioner gäller först 2027 och kan nämnas under omvärldsbevakning som kommande krav. AMLA:s utkast är metodstöd, inte rättslig grund.

En begränsning gäller alla delinstruktioner: **prompten kan styra mot kedjan men inte skapa innehåll som saknas i faktabladet.** Om intaget inte har samlat in till exempel andelen kunder som tagits emot utan fysiskt möte, är `[VERIFIERA]` det enda godtagbara svaret.

## Valideraren avgör, modellen granskar inte sig själv

Anthropics dokumentation säger två saker om självgranskning. Sidan med bästa praxis säger att Claude kan be granska sitt eget svar och att det fångar fel "reliably, especially for coding and math" ([Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)). Migreringsguiden för Opus 5 säger däremot att instruktioner om självkontroll ledde till överdriven verifiering och att det inte försämrade förmågan att ta bort dem. För Opus 5.5 ska saken prövas på nytt (model-migration.md (Anthropics claude-api-skill 2.1.293, `shared/model-migration.md`; lokal kopia, inte i repot)).

Forskningen avgör frågan till förmån för extern kontroll:

- En kritisk översikt fann att inget tidigare arbete visar att självkorrigering fungerar med återkoppling från språkmodellen själv, utom i uppgifter som är särskilt lämpade för det. Självkorrigering fungerar när det finns en pålitlig extern signal ([Kamoi m.fl., TACL 2024](https://arxiv.org/pdf/2406.01297)).
- Utan extern återkoppling sjönk resultatet ibland efter självkorrigering ([Huang m.fl., ICLR 2024](https://arxiv.org/abs/2310.01798)).
- Modellernas självkritik var oftast sämre än vanlig promptning, eftersom de missade många av sina egna fel. **En språkmodell kombinerad med en pålitlig extern verifierare förbättrade däremot resultatet tydligt** ([Stechly m.fl., ICLR 2025](https://arxiv.org/abs/2402.08115v2)).

Riskanalys har redan en sådan verifierare. Prompten ska därför inte innehålla någon instruktion om att dubbelkolla. Valideraren är kontrollen, och den ska fortsätta avgöra om ett utkast godkänns.

Att ett stycke har referenser bevisar inte att påståendet stöds:

- I en granskning av fyra generativa sökmotorer stöddes bara 51,5 procent av meningarna fullt ut av sina källhänvisningar, och bara 74,5 procent av hänvisningarna stödde sin mening ([Liu, Zhang och Liang, 2023](https://arxiv.org/abs/2304.09848)).
- Upp till 57 procent av källhänvisningarna lades till i efterhand för att motivera texten, i ett test som var utformat för att stressa modellen ([Wallat m.fl.](https://arxiv.org/pdf/2412.18004)).

En `enum` över giltiga ID:n garanterar alltså bara att referensen finns, inte att den stöder påståendet. Nästa steg är därför en **kontroll per stycke**: varje tal och varje fakta i ett stycke ska höra till de ID:n som just det stycket refererar till, inte till vilken post som helst i faktabladet. Risken för efterhandsmotiveringar är mindre här än i en vanlig sökmodell, eftersom modellen inte kan något om byråns siffror. Risken finns däremot för allmänna påståenden om penningtvätt. Sådana påståenden ska ha ett ID i regelbasen med källa, annars ska de inte få förekomma.

Specen säger själv att maskinell validering inte visar att en formulering stöds av källan, utan att det avgörs av sakgranskningen ([spec 8.2](../superpowers/specs/2026-10-08-riskanalys-design.md)). Två komplement är rimliga, men bara som signaler till människan och aldrig som något som kan godkänna text som valideraren har underkänt:

- **Separat verifiering som inte ser utkastet.** I Chain-of-Verification slog verifiering i separata anrop verifiering i samma anrop. Andelen korrekta fakta i biografier (FActScore) blev 63,7 mot 60,8, från 55,9 utan verifiering ([Dhuliawala m.fl.](https://arxiv.org/html/2309.11495v2)).
- **En liten faktakontrollmodell.** MiniCheck nådde samma träffsäkerhet som GPT-4 till ungefär 400 gånger lägre kostnad ([Tang m.fl., EMNLP 2024](https://arxiv.org/pdf/2404.10774)).

Juridiska AI-verktyg som marknadsfördes som fria från hallucinationer hallucinerade i 17–33 procent av fallen ([Magesh m.fl.](https://nlp.stanford.edu/~manning/papers/Magesh-Hallucination%E2%80%90Free-2025.pdf)). Sakgranskningen per avsnitt ska därför finnas kvar även när alla automatiska kontroller är gröna.

## Utvärdera med checklistor, tre bedömningslager och sakgranskarens klocka

Utvärderingen ska svara på tre frågor: om AI-texten håller, om design A eller B är bättre och vilken modell och effortnivå som ska användas. **Måttstocken är dagens mallar** med AI-skriven motivering, här kallad C0. AI-skrivna delar måste slå mallarna på tjänstespecifik analys och i den sakkunniges bedömning, utan att bli mindre trogna underlaget. Annars är mallen bättre för den delen.

**Hur många fall behövs.** Anthropic rekommenderar att börja med 20–50 uppgifter som hämtats från verkliga fel ([Demystifying evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)). Skill-dokumentet anger 15–100 indata och en osäkerhet på ungefär ±14 procentenheter vid 25 fall med två upprepningar (build-eval.md (Anthropics claude-api-skill 2.1.293, `shared/evals/build-eval.md`; lokal kopia, inte i repot)). Syntetiska fall ska förankras i verkliga exempel. Här finns de två syntetiska tillsynsfallen med 17 förväntade fynd och felen från testkörningen. Rekommendationen är 24–30 profiler, vilket ger ungefär 100–150 tjänsteavsnitt. Profilerna ska täcka de kända svåra fallen:

- en liten högrisktjänst bland stora lågrisktjänster
- noll rapporter
- okända uppgifter
- många tjänster
- alla nivåer låga
- en kontroll utan belägg
- utlandsgeografi
- olika nivåer för penningtvätt och terrorfinansiering.

Därtill kommer 6–8 par där exakt en uppgift ändrats. Om texten inte ändras när en uppgift ändras är den inte tjänstespecifik. Det testet kräver inget facit.

**Facit.** Den sakkunnige skriver en **checklista per fall och del** med obligatoriska element och förbjudna påståenden, i stället för hela referenstexter. Om modellens text jämförs med en modells eller en expertens text belönas imitation snarare än korrekthet (eval-audit.md (Anthropics claude-api-skill 2.1.293, `shared/evals/eval-audit.md`; lokal kopia, inte i repot)). Profilerna delas slumpmässigt så att varje kategori finns i båda grupperna: två tredjedelar för utveckling och en tredjedel för test. Testprofilerna öppnas aldrig under arbetet med prompterna, vilket specen redan kräver.

**Bedömningen sker i tre lager:**

1. **Deterministiska kontroller.** De körs alltid och kostar inget.
2. **En AI-domare med en ja/nej-fråga per kriterium.** Varje kriterium bedöms i ett eget anrop med svaren godkänt, underkänt eller okänt.
3. **En sakkunnig som granskar blint.** Den sakkunnige vet inte vilken design som skrivit texten, och tiden för varje avsnitt mäts.

Anthropic beskriver bedömning med kod som snabbast och pålitligast och mänsklig bedömning som bäst men långsam. En AI-domare ska först testas för pålitlighet. Domaren bör vara en annan modell än den som skrev texten ([Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)).

Domarens träffsäkerhet ska redovisas separat för godkända och underkända fall. En domare som alltid säger godkänt får 95 procent överensstämmelse om bara 5 procent av fallen är underkända ([Hamel Husain](https://hamel.dev/blog/posts/llm-judge/)). Målet bör vara minst 0,9 i båda grupperna, mätt mot 60–100 exempel som den sakkunnige har bedömt för vart och ett av de två eller tre viktigaste kriterierna.

AI-domare gynnar sina egna texter ([Panickssery m.fl.](https://arxiv.org/abs/2404.13076)). En panel av mindre modeller från olika modellfamiljer slog en enda stor domare och var mer än sju gånger billigare ([Verga m.fl.](https://arxiv.org/abs/2404.18796)). Men att ta in en annan leverantör är ett policybeslut. Det som verkligen motverkar snedvridningen är att domaren kalibreras mot den sakkunnige.

**Parvis jämförelse eller betyg på varje text.** Källorna går isär. Skill-dokumentet och OpenAI förordar att domaren jämför två texter. En studie fann att parvisa omdömen vände i ungefär 35 procent av fallen när texterna hade ytliga drag som domaren gillade, mot 9 procent för betyg på varje text för sig ([Tripathi m.fl., COLM 2025](https://arxiv.org/abs/2504.14716)). Godkännandekraven bör därför bygga på ja/nej-betyg för varje text. Parvis jämförelse används bara som komplement när A och B jämförs, med texterna i båda ordningarna och med möjlighet till oavgjort.

**Statistik.** Resultaten ska grupperas per byrå, eftersom avsnitt från samma byrå bygger på samma fakta. I Anthropics analys var medelfelen mer än tre gånger större när frågor som delade källa grupperades än när de inte gjorde det ([A statistical approach to model evaluations](https://www.anthropic.com/research/statistical-approach-to-model-evals)). Design A och B ska jämföras på samma avsnitt, i par.

Med 100–150 avsnittspar kan utvärderingen se skillnader på 10–15 procentenheter. En skillnad på 5 procentenheter kräver ungefär 470 par. Den beräkningen är gjord i anteckningarna och bygger på antagna felandelar. Om utvärderingen hittar noll sakfel bland 100 avsnitt betyder det bara att felandelen med 95 procents säkerhet är högst ungefär 3 procent. Därför ska varje verkligt dokument fortfarande sakgranskas.

EU:s AI-förordning artikel 50.4 kräver märkning av AI-text om den inte har granskats av en människa och någon har redaktionellt ansvar. Kommissionens riktlinjer beskriver granskningen som en medveten prövning av innehållet av personer med relevant kompetens ([artificialintelligenceact.eu](https://artificialintelligenceact.eu/transparency-rules-article-50/)). Ett internt riskbedömningsdokument omfattas troligen inte, men det är en tolkning och ingen juridisk bedömning. Kravbilden talar ändå för att granskarens godkännande sparas per version.

**Kostnaden.** API-kostnaden är liten i förhållande till den sakkunniges tid. Planeringssiffrorna i överlämningen nedan bygger på testkörningens förbrukning per anrop. De ska ersättas med verkliga siffror ur API:ets användningsdata efter en pilot med 2–3 profiler, vilket skill-dokumentet uttryckligen kräver (build-eval.md (Anthropics claude-api-skill 2.1.293, `shared/evals/build-eval.md`; lokal kopia, inte i repot)). Batch API halverar priset men sparar anrop och svar i upp till 29 dagar. Enligt specen får det bara användas för underlag utan personuppgifter, och batcherna ska raderas när resultatet har hämtats ([spec 8.3](../superpowers/specs/2026-10-08-riskanalys-design.md); [Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing)). För de helt syntetiska profilerna i utvärderingen är det därför tillåtet.

## Överlämning till utvecklarna

Detta avsnitt är skrivet för den som bygger (Codex eller Claude Code). Det samlar rekommendationerna ovan i en form som kan genomföras direkt. Källan till varje krav är länkad i avsnitten ovan.

### Promptarkitekturen

Koden sätter ihop varje anrop av tre delar: den fasta systemprompten, ett användarmeddelande och ett schema. Skissen nedan är en mall för utvecklaren, inte en färdig prompt. Raden "Think the problem through before you answer." tas bara med för Sonnet 5.5. Cachen är ändå separat per modell, så den skillnaden kostar ingen cachning.

```text
SYSTEMPROMPT (identisk i alla anrop, minst 512 token, utan datum eller villkorade avsnitt)

<roll>
Du skriver analyserande text i en svensk redovisningsbyrås allmänna riskbedömning enligt
lagen (2017:630) om åtgärder mot penningtvätt och finansiering av terrorism. Läsarna är
byråns ledning och personal och Länsstyrelsens handläggare.
</roll>

<arbetsfordelning>
Byråns regelmotor har redan fastställt vilka hot, sårbarheter och kontroller som gäller och
vilka risknivåer varje tjänst har. Programmet skriver själv alla tal, nivåmeningar,
obligatoriska meningar och datum. Din uppgift är texten mellan dem: hur tjänsten kan
utnyttjas hos just den här byrån, varför uppgifterna spelar roll och hur faktorerna samverkar.
</arbetsfordelning>

<regler>  [löptext, en regel per stycke, varje regel med sitt skäl]
Använd bara uppgifterna i faktabladet, eftersom dokumentet ska kunna spåras till byråns
eget underlag vid tillsyn.
Ange ingen nivå för risk, sannolikhet eller konsekvens, inte heller för delfaktorer,
eftersom bara regelmotorn bedömer risk och en egen nivå läses som en motsägelse. Beskriv
delfaktorer med andel, antal, period och egenskap.
Skriv tal som platshållare {tal:ID}, eftersom programmet formaterar talen.
Om en uppgift saknas eller inte är bekräftad: skriv [VERIFIERA] i stycket och lägg till en
oklarhet, eftersom ett utkast med luckor inte får se färdigt ut. Att skriva att underlag
saknas är ett korrekt svar.
Skriv personer som {roll:FfR}, eftersom underlaget är avidentifierat.
Skriv om byråns egna förhållanden och inte om branschen i allmänhet, eftersom tillsynen
underkänner mallar som skulle kunna gälla vilken byrå som helst.
Upprepa eller ändra inte programmets låsta meningar. Bygg vidare på dem.
</regler>

<referenser>
Välj först de ID:n som stycket bygger på och skriv sedan stycket utifrån dem. Varje
analysstycke ska ha minst ett ID som är specifikt för tjänsten.
</referenser>

<exempel> 3–5 korta syntetiska exempel, märkta "illustrativt": en delfaktor beskriven
utan nivåord, [VERIFIERA] med oklarhet, ett stycke där referenserna valts först </exempel>

Think the problem through before you answer.          [bara Sonnet 5.5]

ANVÄNDARMEDDELANDE (ett per del)

<faktablad tjanst="T-…"> JSON med sorterade nycklar. Varje post har id, etikett,
  visningsvarde, period, kalla och status (bekräftad/okänd). Inga lokala fritexter. </faktablad>
                                                ← cachebrytpunkt (cache_control) här
<lasta_meningar> programmets meningar i delen, till exempel nivåmeningen </lasta_meningar>
<redan_godkant> godkänd text från tidigare delar (bara för motivering och slutsatser) </redan_godkant>
<uppgift del="…"> delmodulens mål, krav med skäl, fällor med skäl, 2–3 delspecifika exempel </uppgift>
<aterkoppling> bara vid omförsök: den citerade meningen, felet och de tillåtna värdena </aterkoppling>

SCHEMA (ett per tjänst, samma för alla delar i tjänsten; alla fält obligatoriska; fältet "avsnitt" tas bort)
{ "stycken":    [ { "typ": enum, "referenser": [enum över tjänstens ID], "text": string } ],
  "oklarheter": [ { "uppgift_id": enum över tjänstens uppgifts-ID, "fraga": string } ] }
```

**Flödet för varje tjänst:**

1. Koden bygger faktabladet ur tillåtelselistan och skriver delen "Beskrivning och omfattning" samt alla låsta meningar.
2. Anropet för hot skickas först. När det första svarstecknet har kommit skickas sårbarheter och kontroller parallellt. Parallella anrop med samma början får ingen cacheträff förrän det första svaret har börjat strömma (prompt-caching.md (Anthropics claude-api-skill 2.1.293, `shared/prompt-caching.md`; lokal kopia, inte i repot)).
3. Varje del valideras för sig. En underkänd del körs om högst två gånger, och andra omförsöket görs på en högre effortnivå.
4. Därefter skrivs motiveringen med de godkända delarna som underlag och sedan slutsatserna med den godkända motiveringen.

Avsnitten D-ARB.2, D-ARB.4, D-ARB.5 och D-ARB.7 skrivs i egna anrop. D-ARB.9 skrivs sist, med tjänsternas godkända slutsatser som underlag.

**Detta sparas för varje anrop:**

- en kontrollsumma över systemprompt, delmodul och schemaversion (det ersätter dagens enda `PROMPT_KONTROLLSUMMA`)
- design, begärd modell och den modell som faktiskt svarade
- effortnivå
- tokenanvändning, inklusive cachefälten
- stoppskäl (`stop_reason`) och kategorin vid avböjande
- försökets nummer
- valideringsfelen sorterade efter felklass.

Ett livetest märkt `@pytest.mark.live` kontrollerar att `cache_read_input_tokens` är större än noll vid det andra anropet till samma tjänst.

### Delinstruktioner per analysdel

| Del | Skrivs av | Delinstruktionens mål | Krav som styr | Fällor som förklaras med skäl | Maskinell kontroll |
|---|---|---|---|---|---|
| 1. Beskrivning och omfattning | Kod. Lokala fritexter får inte skickas till AI. | Ingen AI-uppgift. | 14FS 2:2 p. 1. Vägledningen: "tillräckligt specifik". Besluten 2026 kritiserar att omfattningen inte framgick. | Ingen AI-uppgift. | Antal eller andel kunder, andel av omsättningen och period finns för varje tjänst. Om tjänsten omfattar bolagsbildning eller skatterådgivning finns kodmeningen om NRA:s sektorsnivå. |
| 2. Hot och egna erfarenheter | AI. Koden skriver meningen om egen rapportering. | Beskriv minst två konkreta sätt som just denna tjänst kan utnyttjas hos byrån, kopplade till tjänstens kundtyper och andelar och till regelbasens hot-ID med källa. Ta med finansiering av terrorism när faktabladet har sådana hot. Förklara att byrån kan utnyttjas omedvetet, genom att någon ser mellan fingrarna eller genom medverkan. | PTL 2:1. 14FS 2:2 p. 2. Rapport 2026:14 s. 6–7 och 11. NRA 7.19. Kammarrätten 6806-23. | Ett eller två allmänna hot som gäller alla tjänster (B-05). Terrorfinansiering med nivå men utan tillvägagångssätt. "Inga rapporter, alltså litet hot", eftersom NRA tolkar få rapporter som låg medvetenhet. | Minst två hot-ID med källa. Minst ett hot om terrorfinansiering när ett sådant finns. Hänvisning till uppgiften om egen erfarenhet. Förbjudna mönster: "inga rapporter … därför", "inte rapporterat … vilket visar". |
| 3. Sårbarheter och motivering | AI | Gå igenom kunder, distributionskanaler, geografi och verksamhetsspecifika omständigheter. Säg för varje kategori om sårbarheten gäller, inte gäller eller är okänd, varför och hur stor andel som berörs. Analysera minst en kombination av faktorer som faktiskt förekommer i profilen. Behandla nära kundrelationer som en risk för minskad vaksamhet. | 14FS 2:2 p. 3. Vägledningen. Rapport 2026:14 s. 8–10. Besluten 2026 p. 5, 6 och 8. AMLR bilaga I. | "Gäller inte" utan motivering (B-09, B-10). "Bara svenska kunder, därför normal geografisk risk". Allmänna formuleringar om att riskfaktorer kan samverka. Långa kundrelationer som trygghet. | Minst ett sårbarhets-ID för var och en av de fyra kategorierna. Geografistycket nämner mer än sanktionslistor. Kombinationsstycket hänvisar till minst två sårbarhets-ID. Ingen "gäller inte" utan referens. |
| 4. Kontroller och effekt | Kod skriver status och belägg. AI skriver kopplingen till risken. | Förklara vilken risk varje införd kontroll riktar sig mot och vad belägget visar. Om effekten saknar belägg ska det stå uttryckligen att kontrollen inte sänker nivån. | Vägledningen: effekten bedöms innan riskerna vägs samman. AMLA p. 25–29. FATF p. 86. | Att en kontroll finns beskriven betyder inte att risken sänks. Att någon annan har gjort kundkännedom sänker inte risken. Ett system ersätter inte personalens vaksamhet. Hög inneboende risk kan inte elimineras helt. | "Minskar", "begränsar" och "reducerar" risken får bara stå i stycken som hänvisar till en kontroll med belagd effekt. Inga kontroller utan status "införd". |
| 5. Risknivåer och motivering | Kod skriver nivåmeningarna och jämförelsen med NRA. AI skriver motiveringen. | Förklara nivån som en kedja: vilka hot som kan utnyttja vilka sårbarheter, hur omfattningen påverkar sannolikheten, vilken konsekvensen blir och hur faktorerna vägs samman. Förklara en avvikelse från NRA:s sektorsnivå med motorns spår. | 14FS 2:2 p. 4 ("motivera"). Vägledningen. Rapport 2026:14 s. 10. AMLA p. 14–16. FATF p. 84. | Nivå utan motivering. Samma nivå för alla tjänster. Låg nivå utan att NRA nämns (B-13). En enskild faktor som bär hela nivån. Text som tonar ned motorns nivå. | Minst ett hot-ID och ett sårbarhets-ID. Inga nivåpåståenden i AI-texten. Kodmeningen om NRA finns. Hänvisning till motorns regelspår. |
| 6. Slutsatser | AI. Koden skriver meningen om ansvar och beslut. | Förklara vad nivån betyder för just denna tjänst: kundkännedom (standard, skärpt eller förenklad, och vad förenklad inte innebär), vad övervakningen ska fokusera på och vad utbildningen ska innehålla. Koppla till de identifierade hoten. | PTL 2:2, 2:3, 2:8 och 2:14. 14FS 2:10. Tillsynens huvudgrund: rutiner som inte är anpassade till verksamheten. | En slutsats som bara upprepar nivån. Allmänna löften som "rutinerna anpassas". "Kundkännedom kan utelämnas" (B-28). | Kundkännedom, övervakning och utbildning nämns. Minst ett hot-ID refereras. Förbjudna mönster saknas. |

### Byråövergripande avsnitt

| Avsnitt | Skrivs av | Mål för AI-delen | Krav som styr | Maskinell kontroll |
|---|---|---|---|---|
| D-ARB.2 Metod och omfattning | Kod för storlek och art. AI för motiveringen. | Förklara hur byråns storlek (omsättning, anställda, kontor) och art (tjänster, komplexitet) har styrt omfattningen. | PTL 2:2. Vägledningen: det ska framgå hur omfattningen bestämts. | Uppgifterna om storlek och art refereras. Länets föreskrift anges av koden. Ingen formulering om att "enkel verksamhet" ersätter grundkraven. |
| D-ARB.4 Myndighetsunderlag och egna erfarenheter | Kod för källförteckning och antal. AI för hur källorna påverkat. | Förklara för varje källa hur den har påverkat bedömningen av byråns tjänster. Väg in egen rapportering och avböjda uppdrag i hotanalysen. Ange NRA:s sektorsnivåer för de tjänster byrån erbjuder. | PTL 2:1. 14FS 2:2. Rapport 2026:14 s. 11. Besluten 2026 p. 9. AMLA p. 17 och 20. | Varje källa har minst ett stycke som knyter den till en tjänst. Förbjudna mönster om noll rapporter. |
| D-ARB.5 Gemensamma riskförhållanden | AI | Beskriv sårbarheter som gäller hela byrån, uppdelade på de fyra kategorierna. Hänvisa till analysen per tjänst och ersätt den inte. | 14FS 2:2 p. 3. Vägledningen: analysen ska göras per tjänst. | De fyra kategorierna finns. Inga nivåpåståenden. |
| D-ARB.7 Kontroller | Kod för status och belägg. AI för bedömningen. | Bedöm för varje kontroll vilken risk den riktar sig mot, om den är införd som avsett, om utformningen är ändamålsenlig och vad belägget visar. | Vägledningen. AMLA p. 25–29. FATF p. 86. | Samma regel om riskminskning som i del 4. |
| D-ARB.9 Följder för rutinerna | AI, med tjänsternas slutsatser som underlag | Ange vilken tjänst och vilken risk som leder till vilken skärpt åtgärd, vilken utbildning och vilken uppföljning. | PTL 2:2, 2:8 och 2:14. 14FS 2:9–10. FATF p. 84 och 86. | Varje tjänst med hög nivå nämns. Allmänna löften utan tjänst-ID underkänns. |
| D-ARB.1, 3, 8, 10 och omvärldsbevakning | Kod | Ingen AI-uppgift: syfte, tjänstelista, nivåtabell, datum, grunder för uppdatering (14FS 2:3 och 2:12, AMLR:s händelsegrund från 2027), lästa källor med datum. | 14FS 2:3 och 2:12. AMLR art. 10.2. | Datum för utvärdering finns. Grunderna för uppdatering finns. |

### Ändringar i valideraren

| Ändring | Varför | Effekt |
|---|---|---|
| Läs tal med mellanslag, hårt mellanslag (U+00A0) och smalt hårt mellanslag (U+202F) som tusentalsavgränsare och decimalkomma som decimaltecken, och jämför hela tal. Inför därefter platshållare `{tal:ID}` som koden fyller i. | Orsak 1 var ett fel i valideraren. Med platshållare skriver modellen inga tal alls. | Inga felaktiga underkännanden av svenska tal. Hela felklassen försvinner med platshållarna. |
| Kontroll per stycke: platshållare och påståenden i ett stycke ska höra till styckets egna referenser. | Att en referens finns bevisar inte att den stöder påståendet (Liu m.fl., Wallat m.fl.). | Fångar en giltig referens som sitter på fel påstående. |
| Inga nivåpåståenden i AI-text. Koden skriver nivåmeningarna, och mönstren behålls strikta. Felmeddelandet visar hur en delfaktor beskrivs med uppgifter. | Orsak 2 och projektregel 1. | Varje träff är ett verkligt fel. Mönstren behöver inte snävas in. |
| Ändra schemat: ta bort `avsnitt`, gör oklarheter till objekt med `enum` och referenser till `enum` per tjänst, lägg `referenser` före `text` och gör alla fält obligatoriska. Jämför `enum`-värden utan hänsyn till stora och små bokstäver. | Orsak 3 och 4. Fältordningen ger "attribute first". Anthropic garanterar inte stora och små bokstäver i `enum`-värden. | Formfelen försvinner redan när svaret genereras. |
| Obligatoriska meningar skrivs av koden (`kalla: "regelbas"`). Kontrollera att AI-texten inte återger dem. | Orsak 5. | Felklassen försvinner. |
| Kontroller per del enligt tabellen ovan, i en egen funktion per del. | Varje del har egna regelkrav. | Riktad återkoppling och riktade omförsök. |
| Fler förbjudna och allmänna fraser ("fungerar väl", "god kännedom om kunderna" utan referens, "låg risk eftersom byrån är liten"). Interna fält-ID får inte stå i löptexten. Lägsta och högsta längd per del. | Tillsynens brister B-02 och B-04. Längden behövs också för att kontrollera domarens förkärlek för långa texter. | Fångar mallartad text och utfyllnad. |
| Jämför hur lika samma del är i olika tjänster hos samma byrå (n-gramlikhet). | B-04: tjänster som beskrivs tillsammans. | Signalerar text som inte är tjänstespecifik. |
| Logga resultatet av första försöket separat. Räkna stoppskälet `max_tokens` som misslyckat. Logga kategorin vid avböjande. | Specens mått och Anthropics råd om `max_tokens`. | Ger data för val av effort och design. |
| Högst två omförsök per del. Bara den del som underkändes körs om, med en citerad mening och tillåtna värden. Andra omförsöket görs på en högre effortnivå. Därefter används mallen (C0) och ett granskningsfynd skapas. | Self-Refine: störst vinst i första omförsöket. Anthropic: att köra om på högre effort ger samma andel godkända till ungefär halva kostnaden. Specen stoppar efter tre försök. | Billigare omförsök, och avsnittet stannar aldrig tyst. |

### Utvärderingsplan med kostnader

Kostnaderna i tabellen är egna uppskattningar som bygger på testkörningens förbrukning per anrop. De ska ersättas med verkliga siffror efter piloten. Priserna är hämtade från [Pricing](https://platform.claude.com/docs/en/about-claude/pricing).

| Steg | Innehåll | API-kostnad (uppskattning) |
|---|---|---|
| 1. Pilot | 2–3 profiler. C0 samt design A och B på Sonnet 5.5 `high`, en körning var. Kostnaden per byrå räknas fram ur användningsdata. Kontroll med ett facitsvar som ska få fullt betyg, ett tomt svar som ska få noll och ett framkallat API-fel som ska registreras som fel, inte som betyg 0. | Cirka 15–25 USD |
| 2. Fall och facit | 24–30 profiler i de kategorier som räknas upp ovan, plus 6–8 par där en uppgift ändrats. Delning 2/3 för utveckling och 1/3 för test, så att varje kategori finns i båda, och delningen låses. Den sakkunnige skriver checklistor per fall och del, bekräftar facit för tillsynsfallen och skriver 5–8 referensavsnitt att kalibrera domaren mot. | 0 USD. Kräver sakkunnigtid. |
| 3. Bedömning | Lager 1: deterministiska kontroller. Lager 2: AI-domare med sju kriterier (trohet per stycke, tjänstespecifik analys, koppling mellan faktor och nivå, kontrollernas effekt, egen erfarenhet, följder för rutinerna, täckning av checklistan). Domaren är en annan modell än skribenten, och Haiku 5.5 används för enkla kriterier. Kalibrering med 60–100 bedömda exempel för de 2–3 viktigaste kriterierna. Lager 3: blind sakkunnig granskning med tidtagning. | Domarkostnaden räknas fram i piloten; antagande 50–150 USD totalt |
| 4. Körningar, en inställning i taget | C0, A och B på Sonnet `high`, därefter B på Sonnet `medium`, B på Opus `medium` och C (lägre effort först, högre vid omförsök). Utvecklingsprofilerna körs en gång och testprofilerna tre gånger, vilket ger 50 byråkörningar per inställning. Körningarna görs via Batch, och batcherna raderas efter hämtning. | Med Batch, per inställning: C0 cirka 30, A 20–25, B Sonnet `high` 65–75, B Sonnet `medium` 40–50, B Opus `medium` 100–150, C 40–60 USD. Totalt med domare cirka 350–550 USD; ungefär dubbelt utan Batch. |
| 5. Krav för godkännande (metodval som projektägaren beslutar) | Noll sakfel och noll nivåfel i den sakkunniges granskning av testprofilerna. Alla avsnitt som inte stoppats klarar den maskinella valideringen till slut, och högst 2 procent stoppas efter tre försök. Högst 2 procent ogrundade stycken och inga ogrundade påståenden om kontrollers effekt. Minst 95 procent täckning per kriterium, och 100 procent för att en liten högrisktjänst lyfts fram och att okända uppgifter markeras med `[VERIFIERA]`. Alla tre körningar klarar de hårda kriterierna för varje testprofil. Domaren når minst 0,9 träffsäkerhet för både godkända och underkända fall innan den används som krav. Sakgranskningen går fortare än med C0. | 0 USD |
| 6. Val och rapport | Bland inställningarna som klarar kraven väljs den med lägst kostnad per godkänt avsnitt och kortast sakgranskningstid. Skillnader inom den statistiska osäkerheten räknas som oavgjorda, och då vinner den billigare och enklare inställningen. Resultaten på testprofilerna redovisas med osäkerhetsintervall i M3-rapporten. | 0 USD |
| 7. Löpande regressionstester | Nivå 0 vid varje `pytest`: sparade svar bedöms om med de deterministiska kontrollerna (gratis). Nivå 1 när en promptkontrollsumma ändras: tre utvecklingsprofiler, märkta som livetest (cirka 5–10 USD). Nivå 2 före byte av prompt, design, modell eller effort: hela utvärderingen via Batch. Kontrollsummor sparas för prompter, schema, domarprompt, bedömningsmall, utvärderingsmängd, bedömningskod och regelbasversion. | Enligt ovan |

Den sakkunniges tid sätter den verkliga gränsen. Tiden behövs för checklistor till 24–30 profiler, 150–300 bedömda kalibreringsexempel och en blind granskning av ungefär 120–160 avsnitt från testprofilerna. Varje minut av den tiden ska kunna användas igen: checklistorna och de bedömda exemplen blir regressionstester, och den sakkunniges motiveringar från utvecklingsprofilerna blir exempel för domaren.

## Där anteckningarna går isär och vad som fortfarande är osäkert

| Fråga | Ståndpunkter | Avgörande och skäl | Kvar att visa |
|---|---|---|---|
| Ett anrop per tjänst eller per del | Anthropic-anteckningen: per tjänst, för sammanhangets och kostnadens skull. Anteckningen om grundad text: per del, eftersom följsamheten sjunker med antalet villkor och omförsöken kan riktas. | Per del som standard, kedjat för motivering och slutsatser. A behålls som jämförelse med samma moduler. Skäl: sammanhanget är redan förankrat i fakta och motor, kraven per del är många, och delarna ska granskas var för sig. Mätningen om samordnande modeller gäller ett annat upplägg. | Inga mätningar på Claude 5.5 eller svensk regeltext. B kostar uppskattningsvis 2–3 gånger mer i API. |
| Nivåord om delfaktorer | Anthropic-anteckningen: snäva in mönstret och lägg till exempel. Anteckningen om grundad text: låt modellen deklarera sina nivåpåståenden strukturerat. | Koden skriver alla nivåmeningar, AI graderar inte delfaktorer, och mönstret behålls strikt. Skäl: projektregel 1 och färre rörliga delar. | Om den sakkunnige tycker att texten blir stel kan strukturerade nivåpåståenden användas som reserv. |
| Tal | Normalisera och förformatera, eller använda platshållare. | Båda: normalisera nu, platshållare som mål. | En platshållare kan peka på fel ID, vilket kontrollen per stycke fångar. |
| Självgranskning | Sidan med bästa praxis: be Claude kontrollera sitt svar. Migreringsguiden för Opus 5 och forskningen: överdriven verifiering, och ingen vinst utan extern signal. | Ingen instruktion om självkontroll. Valideraren är kontrollen. | Opus 5.5 är inte mätt. |
| Startnivå för effort på Sonnet 5.5 | Den officiella sidan: `high`. Skill-dokumentet: `low` för textskrivning. | `high` som start, sedan mätning. | Mätningen avgör. |
| Pris för cacheläsning på Sonnet 5.5 | Prissidan: 0,10 USD per miljon token. Skill-dokumentet: 0,20 USD. | Prissidan gäller. | Påverkar kostnaden mycket lite. |
| Parvis jämförelse eller betyg på varje text | Skill-dokumentet och OpenAI: parvis. Tripathi m.fl.: parvisa omdömen vänder i 35 procent av fallen mot 9 procent. | Ja/nej-betyg på varje text för godkännandekraven. Parvis jämförelse bara för designvalet, i båda ordningarna. | Inte prövat på långa avsnitt. |
| Omförsök som omarbetning eller ny text | Anthropic-anteckningen: fortsätt i samma konversation och behåll cachen. Verifieringsforskningen: en omarbetning kan föra vidare fel från utkastet. | Behåll nytt anrop med den citerade felmeningen. Pröva det andra senare som en separat inställning. | Ingen studie jämför de två för den här typen av fel. |
| Schema per tjänst eller samma för alla | Anthropic-anteckningen: samma schema för cachens skull, eller acceptera förlusten. | `enum` per tjänst och samma schema för alla delar i tjänsten. Cacheförlusten mellan tjänster är försumbar. | Det är oklart hur mycket av cachen som blir ogiltig när formatet byts. Det ska mätas i användningsdata. |

Utöver tabellen finns fem kunskapsluckor:

- **Ingen svensk eller europeisk tillsynsmyndighet har vägledning om AI-skrivna riskbedömningar** i det underlag som granskats.
- **Svensk text saknas i studierna.** Ingen studie mäter fel i svenska talformat eller kvaliteten hos svensk text skriven ur data.
- **Flera källor är preprints.** Studierna om att följsamheten bryter samman vid 5–6 villkor och om kostnaden för omarbetningar är inte granskade av andra forskare.
- **Några regelkällor är inte lästa i original.** FATF:s vägledning lästes ur en kopia hos en annan myndighet. Prop. 2016/17:173 lästes via en automatisk sammanfattning. Kammarrättsdomarna är inte lästa i original. AMLA:s slutliga riktlinjer är inte publicerade.
- **Ingen källa anger hur långt varje del ska vara** eller vilken detaljnivå som räcker för en liten byrå.

## Slutsats

Frågan om ett anrop per tjänst eller per del väger lättare än den först verkar. Den största vinsten kommer av att minska det modellen ansvarar för, inte av hur anropen ordnas. När koden äger tal, nivåer, obligatoriska meningar och format blir varje AI-uppgift liten nog för att ett anrop ska klara den, och då blir A och B två mätbara inställningar i stället för två arkitekturer. Den nya insikten är att valideraren inte gjorde fel i det mest omdiskuterade underkännandet. Nivåord om delfaktorer är AI-bedömningar av risk, alltså just det som projektets första regel förbjuder. Lösningen var en förklaring i prompten och en mening skriven av koden, inte en mildare kontroll.

För fortsättningen betyder det att AI måste förtjäna varje del. Dagens mallar är måttstocken. En AI-skriven del ska bara ersätta mallen om den visar mer tjänstespecifik analys utan att bli mindre trogen underlaget och om sakgranskningen går fortare. Eftersom det är den sakkunniges tid och inte API-kostnaden som begränsar, ska utvärderingen byggas så att varje checklista, varje bedömt exempel och varje uppmätt granskningsminut kan användas igen som regressionstest när regelbasen, modellerna och AMLA:s riktlinjer ändras inför 2027.
