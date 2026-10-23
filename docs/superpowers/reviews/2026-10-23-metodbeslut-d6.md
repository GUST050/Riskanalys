# D6 – ombindningar

Regelbas 2.8.0. **Provisoriskt metodval, ej_granskad. Ingen sakkunnigprövning utförd.**

Val: Behåll allvarlig TF-konsekvens och separat sannolikhet. Alternativ: Kalibrera TF-konsekvens och kontrollavdrag per tjänst.

TF bedöms separat. Konsekvensens skyddsintresse är möjlig skada på människor och samhälle vid terrorändamål; bedömningsenheten är ett relevant missbruksscenario i tjänsten, inte kundens betalningsbelopp. Allvarlig konsekvens behålls provisoriskt. Sannolikhet följer scenariots relevanta hot och TF-faktorer i aktuell matris. Ingen TF-kontrollreduktion beräknas; verksam TF-kontroll kan beskrivas lokalt men har ingen kalibrerad avdragsskala.

Osäkerhet: Skyddsintresse, fast konsekvens och matrisceller är ej granskade metodval. Myndighetens lägesbild fastställer inte dessa val och rapportantal är inte frekvens. TF behöver inte vara lägre än PT.

## Lästa källbelägg

- SRC-TS-2026-14, Fysisk PDF-sida, sida 10: ”hur stora konsekvenserna skulle bli”. Kräver analys av sannolikhet och konsekvens; anger ingen matris, faktorvikt eller kontrollreduktion.
- SRC-FIPO-TF-2025, Fysisk PDF-sida, sida 4: ”legala medel”. Visar att brottsligt ursprung och belopp inte kan användas som generell TF-avgränsning; anger ingen konsekvensskala.

## Genomförande och beroenden

Granskningsobjektet D6 binder följande sakobjekt med exakta innehållssummor i `regelbas/beslutstabeller/metodbeslut.yaml`: BT-MATRIS-01, BT-MATRIS-02, BT-MATRIS-03, BT-MATRIS-04, BT-MATRIS-05, BT-MATRIS-06, BT-MATRIS-07, BT-MATRIS-08, BT-MATRIS-09, BT-SANN-02-01, BT-SANN-02-02, BT-SANN-02-03, BT-SANN-02-04, BT-SANN-02-05, BT-SANN-02-06, BT-SANN-02-07, BT-SANN-02-08, BT-SANN-02-09, BT-TF-01, H-01, H-02, H-03, H-MOD-01, H-MOD-02, H-MOD-03, H-MOD-04, H-MOD-05, H-MOD-06, H-MOD-07, H-TF-01, H-TF-02, H-TF-03, H-TJ-01, H-TJ-02, H-TJ-03, H-TJ-04, H-TJ-05, H-TJ-06, H-TJ-07, H-TJ-08, H-TJ-09, H-TJ-10, H-TJ-11, H-TJ-12, H-TJ-13, S-ARB-01, S-ARB-02, S-ARB-03, S-ARB-04, S-ARB-05, S-ARB-06, S-ARB-07, S-ARB-08, S-ARB-09, S-ARB-10, S-ARB-11, S-ARB-12, S-ARB-13, S-ARB-14, S-ARB-15, S-ARB-16, S-ARB-17, S-ARB-18, S-ARB-19, S-ARB-20, S-ARB-21, S-ARB-22, S-ARB-23, S-GEO-01, S-KANAL-01, S-KOMB-01, S-KUND-01, S-KUND-02, S-TJ-01, S-TJ-02, S-TJ-03, S-TJ-04, S-VERK-01, SRC-FIPO-TF-2025, SRC-TS-2026-14, T-BOLAG-01, T-BOLAG-02, T-BOLAG-03, T-RED-01, T-RED-02, T-RED-03, T-RED-04, T-RED-05, T-RED-06, T-RED-07, T-RED-08, T-RED-09, T-SKATT-01. Hela modellfilinventariet och gemensamma laddnings-/validerings-/attestfiler samt rapportens metodmoduler binds separat. Beslutets innehåll, aktuella sakobjekt och aktuella filhashar ingår i samma attest; befintlig modellvalidering krävs därutöver.

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

Fulla före-/efterutfall, varje numerisk sänkning, borttaget scenario, regelbas och modellfilmanifest: `.superpowers/evidens/2026-10-23-metodbeslut/D6/`. En oförändrad slutnivå är inte bevis för att ett modellval är riktigt. Kontrastprov och samlade regressioner körs vid slutet enligt användarens instruktion.

## Avslag

Vid avslag: ompröva D6 och dess angivna sakobjekt/modellfiler i ny regelversion. Avslaget får inte kringgås med ändrad text. Bind om alla beslut som delar ändrade objekt/filer, fortsätt med ej_granskad och nytt expertbeslut. Räkna om varje scenario i sexfallen och kontraster, revidera berörda modellfacit/valideringsrapporter, bygg nya analyser/skrivunderlag/V10-rapporter/PDF:er och tre expertpaket, kräv ny samlad sakgranskning. Låsta historiska paket ändras inte.

Regelbasvalidering och beräkningsbygge passerar; ingen grön testsvit påstås. Ingen push eller merge.
