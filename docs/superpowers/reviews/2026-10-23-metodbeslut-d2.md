# D2 – ombindningar

Regelbas 2.4.0. **Provisoriskt metodval, ej_granskad. Ingen sakkunnigprövning utförd.**

Val: Avgränsa fakturahotet, behåll brottsvinst som lön. Alternativ: Behåll H-01 och H-02 i varje löneuppdrag.

Ren löneberedning behandlar löneuppgifter, inte generellt leverantörsfakturor. Falskt löneunderlag finns i H-TJ-04; löneuttag som legitimerar brottsvinst finns i H-02. H-01 prövas i separat erbjuden faktura-/bokföringstjänst och vid nytt utvidgat arbetsmoment.

Osäkerhet: En byrå kan ha kombinerade uppdrag och korskopplad insyn. Avgränsningen förutsätter tjänstekatalogens rena löneuppdrag; den bevisar inte att fakturakedjor saknas hos kunden.

## Lästa källbelägg

- SRC-NRA-2024-25, 7.19; fysisk PDF-sida, sida 123: ”lön och utdelning”. Brottsvinster kan tas ut som lön; det bevisar inte att löneberedaren ser leverantörsfakturan.
- SRC-TS-2026-14, Fysisk PDF-sida, sida 7: ”individuell analys”. Kräver motiverad analys per tjänst; ingen numerisk kalibrering.
- SRC-VAGL-2025-03, Fysisk PDF-sida, sida 17: ”lön och utdelning”. Stöder löneuttag, inte allmän fakturainsyn i en ren löneberedning.

## Genomförande och beroenden

Granskningsobjektet D2 binder följande sakobjekt med exakta innehållssummor i `regelbas/beslutstabeller/metodbeslut.yaml`: C-TJ-04, H-01, H-02, H-TJ-04, KR-C-TJ-04-T-RED-04, SRC-NRA-2024-25, SRC-TS-2026-14, SRC-VAGL-2025-03, T-RED-04. Hela modellfilinventariet och gemensamma laddnings-/validerings-/attestfiler samt rapportens metodmoduler binds separat. Beslutets innehåll, aktuella sakobjekt och aktuella filhashar ingår i samma attest; befintlig modellvalidering krävs därutöver.

Ombindningar av tidigare, fortsatt ogranskade beslut: [{"beslut": "D1", "objekt": ["T-RED-04", "C-TJ-04", "KR-C-TJ-04-T-RED-04"]}].

## Före och efter

Tolv oförändrade profilbytes: de sex fasta byråfallen, ursprunglig och explicit kompletterad variant. Alla tjänste-/scenarioutfall sparas, inklusive perioder, osäkerhet, kontrollmål och regelsprår.

Mot föregående steg: `{'andrade_tjanster': 4, 'sankta_led': 0, 'borttagna_scenarier': 4}`. Samlat mot 2.0.0: `{'andrade_tjanster': 52, 'sankta_led': 0, 'borttagna_scenarier': 8}`.

| Profilvariant | Ändrade tjänster | Sänkta led | Borttagna scenarier |
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

Fulla före-/efterutfall, varje numerisk sänkning, borttaget scenario, regelbas och modellfilmanifest: `.superpowers/evidens/2026-10-23-metodbeslut/D2/`. En oförändrad slutnivå är inte bevis för att ett modellval är riktigt. Kontrastprov och samlade regressioner körs vid slutet enligt användarens instruktion.

## Avslag

Vid avslag: ompröva D2 och dess angivna sakobjekt/modellfiler i ny regelversion. Avslaget får inte kringgås med ändrad text. Bind om alla beslut som delar ändrade objekt/filer, fortsätt med ej_granskad och nytt expertbeslut. Räkna om varje scenario i sexfallen och kontraster, revidera berörda modellfacit/valideringsrapporter, bygg nya analyser/skrivunderlag/V10-rapporter/PDF:er och tre expertpaket, kräv ny samlad sakgranskning. Låsta historiska paket ändras inte.

Regelbasvalidering och beräkningsbygge passerar; ingen grön testsvit påstås. Ingen push eller merge.
