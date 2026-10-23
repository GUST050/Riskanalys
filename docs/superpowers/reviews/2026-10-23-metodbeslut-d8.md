# D8 – ombindningar

Regelbas 2.10.0. **Provisoriskt metodval, ej_granskad. Ingen sakkunnigprövning utförd.**

Val: Behåll högst ett PT-steg per belagt täckt scenario. Alternativ: Kalibrera avdrag efter kontrollgrad och scenariotäckning.

Motoravdrag kräver belagd utformning, genomförande och verksam effekt samma period samt katalogmål för samma tjänst och hot. Högst ett PT-steg, golv låg, är provisoriskt metodval. Katalogmål bevisar inte lokalt uppdrag, stickprov eller full täckning. Lokal analys prövar observationsunderlag, begränsningar och godtagbarhet; en oprövad sänkning märks och får inte framställas som godkänd. TF får inget avdrag.

Osäkerhet: Ett steg och minst en verksam kontroll är inte myndighetskalibrerade. C-TJ-08/09:s äldre breda PT-mål kräver lokal prövning; de utvidgas inte till nya MOD-hot för att sänka tjänstens max. En kontroll på ett maxscenario täcker inte andra maxscenarier.

## Lästa källbelägg

- SRC-TS-2026-14, Fysisk PDF-sida, sida 10: ”hur stora konsekvenserna skulle bli”. Kräver analys av sannolikhet och konsekvens; anger ingen matris, faktorvikt eller kontrollreduktion.

## Genomförande och beroenden

Granskningsobjektet D8 binder följande sakobjekt med exakta innehållssummor i `regelbas/beslutstabeller/metodbeslut.yaml`: BT-KVAR-01, BT-KVAR-02, BT-KVAR-03, C-07, C-SANK, C-TJ-01, C-TJ-02, C-TJ-03, C-TJ-04, C-TJ-05, C-TJ-06, C-TJ-07, C-TJ-08, C-TJ-09, C-TJ-10, C-TJ-11, C-TJ-12, C-TJ-13, KR-C-07-T-RED-01, KR-C-TJ-01-T-RED-01, KR-C-TJ-02-T-RED-02, KR-C-TJ-03-T-RED-03, KR-C-TJ-04-T-RED-04, KR-C-TJ-05-T-RED-05, KR-C-TJ-06-T-RED-06, KR-C-TJ-07-T-RED-07, KR-C-TJ-08-T-SKATT-01, KR-C-TJ-09-T-BOLAG-01, KR-C-TJ-10-T-BOLAG-02, KR-C-TJ-11-T-BOLAG-03, KR-C-TJ-12-T-RED-08, KR-C-TJ-13-T-RED-09, SRC-TS-2026-14, T-BOLAG-01, T-BOLAG-02, T-BOLAG-03, T-RED-01, T-RED-02, T-RED-03, T-RED-04, T-RED-05, T-RED-06, T-RED-07, T-RED-08, T-RED-09, T-SKATT-01. Hela modellfilinventariet och gemensamma laddnings-/validerings-/attestfiler samt rapportens metodmoduler binds separat. Beslutets innehåll, aktuella sakobjekt och aktuella filhashar ingår i samma attest; befintlig modellvalidering krävs därutöver.

Ombindningar av tidigare, fortsatt ogranskade beslut: inga.

## Före och efter

Tolv oförändrade profilbytes: de sex fasta byråfallen, ursprunglig och explicit kompletterad variant. Alla tjänste-/scenarioutfall sparas, inklusive perioder, osäkerhet, kontrollmål och regelsprår.

Mot föregående steg: `{'andrade_tjanster': 0, 'sankta_led': 0, 'borttagna_scenarier': 0}`. Samlat mot 2.0.0: `{'andrade_tjanster': 52, 'sankta_led': 0, 'borttagna_scenarier': 8}`.

| Profilvariant | Ändrade tjänster | Sänkta led | Borttagna scenarier |
|---|---:|---:|---:|
| referens_standard_ursprunglig | 0 | 0 | 0 |
| referens_standard | 0 | 0 | 0 |
| referens_fyra_ursprunglig | 0 | 0 | 0 |
| referens_fyra | 0 | 0 | 0 |
| enmansbyra_ursprunglig | 0 | 0 | 0 |
| enmansbyra | 0 | 0 | 0 |
| betalningsmandat_ursprunglig | 0 | 0 | 0 |
| betalningsmandat | 0 | 0 | 0 |
| riskbranscher_ursprunglig | 0 | 0 | 0 |
| riskbranscher | 0 | 0 | 0 |
| fa_faktorer_ursprunglig | 0 | 0 | 0 |
| fa_faktorer | 0 | 0 | 0 |

Fulla före-/efterutfall, varje numerisk sänkning, borttaget scenario, regelbas och modellfilmanifest: `.superpowers/evidens/2026-10-23-metodbeslut/D8/`. En oförändrad slutnivå är inte bevis för att ett modellval är riktigt. Kontrastprov och samlade regressioner körs vid slutet enligt användarens instruktion.

## Avslag

Vid avslag: ompröva D8 och dess angivna sakobjekt/modellfiler i ny regelversion. Avslaget får inte kringgås med ändrad text. Bind om alla beslut som delar ändrade objekt/filer, fortsätt med ej_granskad och nytt expertbeslut. Räkna om varje scenario i sexfallen och kontraster, revidera berörda modellfacit/valideringsrapporter, bygg nya analyser/skrivunderlag/V10-rapporter/PDF:er och tre expertpaket, kräv ny samlad sakgranskning. Låsta historiska paket ändras inte.

Regelbasvalidering och beräkningsbygge passerar; ingen grön testsvit påstås. Ingen push eller merge.
