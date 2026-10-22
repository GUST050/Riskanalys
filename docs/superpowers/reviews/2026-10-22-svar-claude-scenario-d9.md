# Rättning av scenarioavvikelse och D9-upprepning

Bas `fc1a329`, befintlig gren `codex/kravstod-tjansteexponering`. Båda granskningsfynden är reproducerade och rättade lokalt. Färsk fullsvit återstår före leverans. Ingen push eller merge; den andra klonen/grenen `feat/steg-1-3` har inte ändrats.

## Scenarioavvikelsen

Orsaken var att den samlade tjänstegenomgången skrev `bekraftad=True` och aktuell `scenariosumma` på alla scenariokopplingar innan den ordinarie grinden kördes. Därmed maskerades den gamla avvikelsen. Nu måste `avviker` redan vara separat bekräftad mot det aktuella gemensamma scenariot. En giltig avvikelse lämnas oförändrad. Både inaktuell summa och obekräftat avvikelseval stoppar den samlade handlingen. Standardvalet `samma` får fortsatt förnyas efter genomgången av den visade texten.

Vyn använder samma kontroll och visar en varning med länken ”Pröva avvikelsen på nytt”. Ändrat scenario ger meddelandet ”Det gemensamma scenariot har ändrats sedan avvikelsen; pröva avvikelsen på nytt”. Ett rent obekräftat val skiljs från ett faktiskt ändrat scenario. Separat scenarioprövning mot den nya summan följd av tjänstegenomgång fungerar.

Tre regressionsfall blev röda av rätt skäl (två felaktigt godtagna avvikelser och saknad UI-markering); standardvalets positiva skydd var grönt. Första testutkastets kontroll jämförde även andra, automatiska standardval och rättades innan den riktiga reproduktionen. Därefter passerade **27 enhetsprov/9,07 s**. Ett verkligt bundet publikt prov gick igenom separat giltig avvikelse → ändrat gemensamt scenario → atomiskt avslag utan ändrad analysfil → ny uttrycklig avvikelseprövning → lyckad tjänstegenomgång. Inga analysbeslut skapades.

## D9-raden och faktisk längd

Reproducerande prov visade **16 D9-stycken per tjänst**, inte en sammanfattning. Nu finns en rad per tjänst med alla berörda faktor-ID och samtliga tidigare faktor-/post-/profil-/regelreferenser. Bara känt falska villkor/under tröskel sammanfattas. Fulla fakta, villkor och tjänst-/hot-/dimensionskopplingar finns fortsatt i B1. Ingen risknivå eller tröskel ändras.

De två nya rapportfallen blev röda och därefter passerade **16 rapport-/native-prov/22,53 s**, inklusive original, attribution, D9-referenser och proveniens. Det publika scenarioprovet i samma reproduktionskörning passerade; körningen gav två förväntade rapportfel och ett godkänt prov på 34,83 s.

Fyra nya faktiska Word-filer är exporterade (två fall × läsrapport/B1). Profil-, motor-, skrivsvars- och regelbashashar matchar såväl föregående direkt2 som den frysta schema-1-basen.

| Fall | Schema 1 läsrapport | Direkt2 före | Direkt2 efter | Skillnad mot schema 1 | B1 före/efter |
| --- | ---: | ---: | ---: | ---: | ---: |
| fyra_tjanster | 13 756 | 16 446 | 14 126 | +370 | 36 005 |
| med_betalningsmandat | 13 433 | 16 123 | 13 803 | +370 | 36 150 |

**2 320 färre ord i läsrapporten i vartdera fallet**, och D9-styckena minskar från 64 till fyra. Hela tvåfilsleveransen har 50 131 respektive 49 953 ord, fortsatt 1 717/1 693 fler än schema 1. I den faktiska Word-exporten innehåller de gamla D9-styckena 2 552 synliga ord och de nya 232. Granskningens 3 064 ord och slutsats att läsrapporten blir kortare än schema 1 kunde inte återskapas med detta räkningskontrakt. Ingen annan saktext har tagits bort för att nå ett längdmål.

B1:s ordantal och samtliga saktexter är oförändrade. Den enda skiljande synliga texten i Word-bilagan är revisionsradens tre kontrollsummor; detta avgränsade metadataundantag kontrolleras uttryckligen. Ingen information flyttades till B1. Båda läsrapporterna renderades till PDF/PNG, 38 sidor vardera. **Riktad visuell kontroll av sidorna 13 och 33 i båda fallen** visar läsbara sammanfattningar och efterföljande riskresonemang utan observerad klippning/överlapp; inte fullsidig QA.

## Verifiering och befogenhet

Python 3.12.15. Snabbprofil **119 godkända/34,784 s**, exakt collection/JUnit och oförändrat aktuellt snapshot. Analysprofil och fullsvit slutredovisas efter körning på frysta källor. Regel 6 i AGENTS.md är oförändrad i denna rättning; dess policyändring ingick i det tidigare godkända genomförandeuppdraget. Ingen ny bekräftelse av samma godkännande behövs. Nya rättningar kräver färsk fullsvit innan leverans, push eller merge.

Råbevis, mätdata och exporter ligger lokalt i `.superpowers/evidens/2026-10-22-claude-scenario-d9/`. Tidigare bevis under `.superpowers/evidens/2026-10-22-engangssvar/` är bevarade separat. Rapportens avsiktliga sakluckor och oförändrade metodbegränsningar gäller fortsatt.
