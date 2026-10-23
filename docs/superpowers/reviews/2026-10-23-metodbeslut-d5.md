# D5 – ombindningar

Regelbas 2.7.0. **Provisoriskt metodval, ej_granskad. Ingen sakkunnigprövning utförd.**

Val: Behåll max per dimension med synlig bredd. Alternativ: Vikta eller medelvärdesbilda scenarier.

En väsentlig exponeringskedja ska inte döljas av många låga scenarier. Högsta inneboende risk respektive högsta kvarstående PT beräknas var för sig. Alla avgörande scenarier och otäckta maxled redovisas; PT och TF hålls åtskilda. Max är ett provisoriskt metodval, inte en föreskriven formel.

Osäkerhet: Antal scenarier är katalogberoende och är inte en sannolikhet eller exponeringsandel. Max kan dölja bredd i slutnivån, därför måste full scenariomatris och motivering läsas.

## Lästa källbelägg

- SRC-TS-2026-14, Fysisk PDF-sida, sida 10: ”hur stora konsekvenserna skulle bli”. Kräver analys av sannolikhet och konsekvens; anger ingen matris, faktorvikt eller kontrollreduktion.

## Genomförande och beroenden

Granskningsobjektet D5 binder följande sakobjekt med exakta innehållssummor i `regelbas/beslutstabeller/metodbeslut.yaml`: BT-TJ-01, H-01, H-02, H-03, H-MOD-01, H-MOD-02, H-MOD-03, H-MOD-04, H-MOD-05, H-MOD-06, H-MOD-07, H-TF-01, H-TF-02, H-TF-03, H-TJ-01, H-TJ-02, H-TJ-03, H-TJ-04, H-TJ-05, H-TJ-06, H-TJ-07, H-TJ-08, H-TJ-09, H-TJ-10, H-TJ-11, H-TJ-12, H-TJ-13, SRC-TS-2026-14, T-BOLAG-01, T-BOLAG-02, T-BOLAG-03, T-RED-01, T-RED-02, T-RED-03, T-RED-04, T-RED-05, T-RED-06, T-RED-07, T-RED-08, T-RED-09, T-SKATT-01. Hela modellfilinventariet och gemensamma laddnings-/validerings-/attestfiler samt rapportens metodmoduler binds separat. Beslutets innehåll, aktuella sakobjekt och aktuella filhashar ingår i samma attest; befintlig modellvalidering krävs därutöver.

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

Fulla före-/efterutfall, varje numerisk sänkning, borttaget scenario, regelbas och modellfilmanifest: `.superpowers/evidens/2026-10-23-metodbeslut/D5/`. En oförändrad slutnivå är inte bevis för att ett modellval är riktigt. Kontrastprov och samlade regressioner körs vid slutet enligt användarens instruktion.

## Avslag

Vid avslag: ompröva D5 och dess angivna sakobjekt/modellfiler i ny regelversion. Avslaget får inte kringgås med ändrad text. Bind om alla beslut som delar ändrade objekt/filer, fortsätt med ej_granskad och nytt expertbeslut. Räkna om varje scenario i sexfallen och kontraster, revidera berörda modellfacit/valideringsrapporter, bygg nya analyser/skrivunderlag/V10-rapporter/PDF:er och tre expertpaket, kräv ny samlad sakgranskning. Låsta historiska paket ändras inte.

Regelbasvalidering och beräkningsbygge passerar; ingen grön testsvit påstås. Ingen push eller merge.
