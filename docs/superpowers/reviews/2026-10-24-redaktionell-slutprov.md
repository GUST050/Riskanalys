# Redaktionell V10 – produktkoppling och slutprov

Arbetsgren `codex/regelbas-inventering`. Bas `d8a91a1`, offlineförslag `da27e11`, produktkoppling `89864ec`, slutgranskningens rättning `43abc07`. Ingen push eller merge ingår.

## Levererad förändring

Resultatrapporten visar svenska etiketter, formaterade tal och perioder. Fritext bevaras ordagrant. Råkoder i en originaltext ger synlig konflikt och stoppar den nya presentationen, i stället för att originalet skrivs om. Katalog-ID får stå med förklarande namn. De fullständiga hot-, metod-, tjänste-, erfarenhets- och kontrolluppgifterna finns i A/B1 med verifierat flyttregister.

Ny presentationsversion är `D-ARB-v10-presentation-2`, med policy `V10-redaktionell-original-2`. Nya analyser använder den nya presentationen. Ett befintligt V10-utkast behåller sparad presentation vid vanlig uppdatering. Ett uttryckligt byte i gränssnittet eller `--rapportformat v10-redaktionell` bygger ny presentation och ogiltigförklarar gamla strukturberoende sakgodkännanden. Huvudrapporten kräver ny samlad sakgranskning; A och B1 granskas fortsatt var för sig. Historisk återspelning använder frysta källor och sparad presentationsversion.

## Separat teknisk regelbasändring

D-besluten binder konservativt hela appens Python-genomförande. Uppdragets undantag för nödvändig separat regelbasändring har därför tillämpats och redovisats före ombindningen. Validatorn och filinventariets omfattningsregel har inte lättats.

- Före: 2.12.2, `sha256:21cf1f9fc25a110f31ce5addc47c133b1ed5689b2ac64b117409e5ce63dcb4c0`.
- Efter: 2.12.3, `sha256:1da79fddaf069377ce1b141714da09f27a70505bfe12f91c125caa2b49a6dedc`.
- Endast version, övergripande kontrollsumma och D-posternas `modellfiler` skiljer regelbasens modell från den frysta basen. Inga sakobjekt, metodval, nivåer, intagsfrågor eller sakkunnigstatusar har ändrats. Alla D-poster är fortsatt `ej_granskad`.
- Samtliga tio D-poster binder nu 249 appfiler, tidigare 244. Regelbasvalidering: 0 fel. Exakt normaliserad jämförelse prövas i automatiskt kontraktsprov.
- Tolv fasta profilfiler och 40 kontrastprofiler räknas om med samma bytes. Hela bedömningsobjektet är identiskt efter normalisering av endast regelbasversion och regelbaskontrollsumma. Före-/efterfiler behåller sina ursprungliga versioner; dagens utfall läggs separat i `metod/slut-2.12.3/`.

Gamla sakkunnigmallar kan inte importeras som godkännande av den nya filbindningen. Historiska rapportpaket skrivs inte om.

## Referensfiler och PDF-kontroll

Syntetiska källor är de tidigare frysta V10-fallen. AI-text och lokala svar återanvänds exakt; inga riktiga API-anrop eller byråuppgifter används. Aktuella produktreferenser ligger under `.superpowers/evidens/2026-10-24-redaktionell-produkt/referenser-3/`.

| Fall | Resultatrapport | A | B1 | Exakt bevarade flyttdelar | Hela originaltexter |
|---|---:|---:|---:|---:|---:|
| Fyra tjänster | 19 | 44 | 199 | 231 | 52 |
| Med betalningsmandat | 19 | 46 | 204 | 231 | 59 |

Riktmärket högst tio huvud-PDF-sidor är **inte uppnått**. Textstorleken har behållits och inget innehåll har kapats. Alla huvudsidors text är kontrollerad för förbjudna råvärden och ord utanför sidan; samtliga 38 huvudsidor är visuellt lästa. Ändrade bilageavsnitt och tabellfortsättningar har stickprovsgranskats. Varje bilagesida har inte lästs visuellt.

Slutgranskningens fritexträttning ändrar inte den synliga texten i de två huvudrapporterna eller bilaga A jämfört med den visuellt lästa produktreferensen. Samtliga 38 slutliga huvudsidor är även pixelidentiska med de visuellt lästa sidorna. Bilaga B1 innehåller samma fulla fyndmängd med samma multiplicitet; ordning och löpnummer för likvärdiga maskinfynd kan variera mellan separata körningar. Detta är kontrollerat genom exakt jämförelse av alla fyndfält utom löp-ID. Slutpaketets egna ID:n och referenser binds samman av dess manifest. Flyttregistret kontrollerar originalstycken, tabellrubriker, kolumnrubriker och varje cell med exakt källa/mål/innehållssumma. Gemensamma scenarier grupperas endast med identisk motorpost och utan lokal variant.

## Färsk samlad slutgranskning

En färsk granskare (`gpt-6-astra`, separat kontext) granskade hela ändringen `d8a91a1..89864ec` och provbyggda expertpaket. Inga Critical-fynd. Ett Important-fynd: gemensamma fritextfält skyddades inte fullständigt. Rättat i en fixpass före fullsviten, inklusive offlinekopian.

Fyra delade regressionsprov för gemensam beskrivning/motivering visade först fel och därefter godkänt. Två ytterligare kontraktsprov skyddar katalog-ID när namnet är bokstavlig originaltext. Formatkontrollen använder hela textsammanhanget och matchar original på ord-/ID-gräns, så att ett versionsvärde som `1` inte delar upp ett program-ID. Berörda prov: **51 godkända, 0 fel**, 76,92 sekunder. Slutlig snabbprofil: **140 godkända, 0 fel**, verifierat oförändrat snapshot, 60,22 sekunder.

Ett mindre fynd skjuts upp: övriga detaljerade formatterarkontrakt är ännu inte alla parametriserade mot båda kopiorna. De nya originalbevarandeproven körs mot båda. Framtida separata formatteringsändringar behöver fortsatt explicit regressionsprov för båda vägarna.

## Fullsvit och slutlig paketering

Fullsviten körs på `43abc07`, utan live-API: `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv312/bin/python scripts/testa.py full --ut /private/tmp/redaktionell-full-slut-1`. Insamling: 3 594 ordinarie prov, ett livetest bortvalt. **Utfall: 3 594 godkända, 0 fel, 0 överhoppade, exitkod 0.** Insamling och JUnit matchar. Alla 863 snapshotresurser är exakt oförändrade, även vid separat kontroll efteråt. Körningen tog **3 973,446 sekunder (66 min 13 s)**; JUnit summerar 3 969,764 provsekunder. Föregående fullkörning tog 3 129,232 sekunder. Kod, tester, regelbas och verktyg ändrades inte under körningen; endast dokumentation färdigställs efteråt.

Varje region får fullständigt tekniskt underlag och läsversion. Tolv gemensamma filer är byteidentiska: guide, objektgenomgång, obesvarad mall, metodsammanställning, beroenden, före-/efterskillnader samt båda fallens tre PDF-delar. Läsversionens manifest binds till fullpaketets manifest. Exakt filantal och byte mäts efter slutbygget. ZIP skapas först därefter.

## Redovisade genomförandebeslut och begränsningar

1. Offlineförslaget byggdes utanför produktkoden före PDF-klartecken. Kostnaden var en separat produktintegration och D-filombindning efter klartecknet; båda är genomförda.
2. Upprepad TF-indikatorförteckning och omvärldsbevakningens källkoder fick bevarade mål i B1 E4/E5. Kostnaden är två extra flyttgrupper att följa; exakta original finns kvar och kontrolleras.
3. Sidmålets avvikelse redovisas öppet. Ett hårt tiomax kräver ytterligare redaktionella beslut; inget sakinnehåll har kapats för att uppnå ett sidantal.
4. Nödvändig teknisk regelbasversion 2.12.3 används för full konservativ D-filbindning. Kostnaden är nya aktuella expertbeslut för den nya versionen; ingen gammal attest överförs.
5. Oförändrad juridik/metod lämnas till verklig sakkunnigprövning. Teknisk leverans innebär inget rättsligt godkännande.
6. Slutgranskaren har inte gjort om implementerarens fulla PDF-läsning. Bilagorna är visuellt stickprovsgranskade; kod- och bevarandekontroller ersätter inte en sakkunnigs genomläsning.

## Var testtiden ligger

Tiderna kommer från den enda nya fullkörningens JUnit; ingen extra testkörning har startats för mätningen. De största filgrupperna är:

| Provfil | Sekunder |
|---|---:|
| `tester.intag.test_webb` | 429.859 |
| `tester.typfall.test_gemensam_analys_hela_kedjan` | 364.805 |
| `tester.m2.test_m2_kedja` | 258.893 |
| `tester.m2.test_m2_grindar` | 202.108 |
| `tester.intag.test_analys` | 186.012 |
| `tester.intag.test_rapportflode_v8` | 160.678 |
| `tester.enhet.test_analysgrind` | 159.583 |
| `tester.typfall.test_analys_hela_kedjan` | 140.374 |

Det enskilda formulärprovet fram till Word tog 362,804 s och provet av fastställelse av gemensam analys 246,407 s. M2:s tre regionala kedjeprov tog cirka 84–85 s vardera. Mätningen visar var tiden förbrukas; den är ingen profilering av orsaken till tidsskillnaden mot föregående körning. Hela tidsfördelningen och JUnit-kontrollsumman finns i fullpaketets `slutprov/tidsanalys.json`.
