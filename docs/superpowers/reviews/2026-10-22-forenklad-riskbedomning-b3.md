# Mellanleverans B1–B3: underlag för Claude

Bas: produkt A `b3cf49080fc20e70665d2917042a3a3a6122bf9e`, dokumentationsbas `d0b75d2`. Leveransen ligger på `codex/kravstod-tjansteexponering`. Ingen push eller merge ingår.

Leveransen inför källbundna, ogranskade tjänsteförslag och ett trevärdigt urval. Ett kvarvarande ja i formuläret blir en byråuppgift först efter uttrycklig bekräftelse med källa, datum och ansvarig. Osäker blir okänt; historiskt nej får inte kringgå införandeplanen via okänt.

Analysschema 2 har gemensamma sårbarhets- och verksamhetsposter, innehållsbundna tjänstetillämpningar, manuell riktning endast för ”gäller annorlunda” och uttrycklig täckningsprövning av egen sårbarhet. Schema 1 läses och serialiseras som tidigare. Gemensamt innehåll projiceras till en ren läsvy vid innehållsprövningen; bekräftelser och beslut binds till originalpaketet. Ändring gör tidigare godkännanden inaktuella enligt den befintliga globala bindningen.

Riktningen härleds per faktor, hot och dimension. Känt falskt tröskelvillkor, annat falskt villkor, faktisk ersättare i samma scenario och uttryckligen saknad koppling skiljs åt. Okänt underlag är aldrig under tröskeln. Ingen allmän ”båda”-angivelse skapar automatiska TF-påståenden. Relevanta egna sårbarheter kräver ett belagt lokalt scenario med rätt hot, dimension och riskled; en allmänt hög nivå räcker inte. +1-referensen ändrar ingen verklig risknivå, vikt eller kontrollregel.

CLI har `analys BYRA --forifyll|--forslag --schema 2`. Svarimport rensar importerade bekräftelser och tillåter inte byte av befintligt schema. Förnyelse behåller det sparade schemat. Vanlig import kan inte föra in godkännanden.

## Mellanversionens begränsning

Schema 2 kan ännu inte bli en rapport. V8-byggaren avvisar det uttryckligen tills B5 är verifierat. Denna mellanversion ska inte lämnas till verklig användning. Webbhandlingarna för gemensam redigering och tillämpning införs i B4. De förbereds med ytterligare evidens- och referensprov före exponering. Tjänster utanför katalogen får fortfarande inget motorutfall; separat omfattningsunderlag och framtida manuell tjänsteanalys tillhör nästa leverans.

## Verifiering

- Python 3.12.15 i `.venv312`; ingen verklig API-nyckel eller byrådata används.
- 186 berörda analys-, CLI-, lagrings-, reducerings- och webbprov passerar.
- 34 nya schema-/orsaks-/täcknings-/referensprov passerar.
- Regelbasvalidering och `git diff --check` passerar. Ny regelbaskontrollsumma: `sha256:b4dc7018b05b340e746d31efd0a49ee837fa1312c126a24f5571445a27132a58`.
- Historisk schema-1-serialisering och registersummor är kontrollerade. Frysta AI-begäranden och profilbytes är oförändrade. Den frysta motorjämförelsen normaliserar enbart den avsiktligt ändrade regelbasbindningen och jämför fortfarande samtliga faktiska motorfält mot sin gamla kontrollsumma.
- Första fullsviten med fyra processer avbröts: HTTP-proven fick tidsgränsfel av belastningen. Den räknas inte som godkänd. Den accepterade fullsviten körs sekventiellt med en källögonblicksbild före/efter.

Detaljerade kommandon, RED/GREEN-loggar, basmätningar och fullsvitens JUnit/källögonblicksbild finns lokalt i den ignorerade körmappen `.superpowers/sdd/2026-10-22-forenklad-riskbedomning-plan/`. B4–B6-utkast där påverkar inte installerad kod eller fullsvitens testurval.

Accepterad fullsvit: **3 107 godkända, 1 livetest bortvalt, exitkod 0**, 1 951,07 sekunder. Källögonblicksbilden är oförändrad. JUnit har inga fel eller överhoppade valda prov.
