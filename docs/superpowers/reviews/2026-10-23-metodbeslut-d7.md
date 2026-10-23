# D7 – ombindningar

Regelbas 2.9.0. **Provisoriskt metodval, ej_granskad. Ingen sakkunnigprövning utförd.**

Val: Ideell indikator höjer endast TF. Alternativ: Låt organisationsformen höja både PT och TF.

Den lästa TF-lägesbilden stöder TF-relevans men ger inte en självständig generell PT-kedja av organisationsformen. S-ARB-05 verkar därför bara i TF-dimensionen. H-03 är fortsatt både PT och TF och andra belagda PT-faktorer kvarstår. Organisationsformen ensam är inte bevis för missbruk.

Osäkerhet: Detta kan sänka PT-sårbarhet och risk i tidigare ideellscenarier. Samma kanaler som PT bevisar inte generell PT-effekt av organisationsformen. PEP och ideell får fortfarande summeras som portföljindikatorer i TF utan att faktisk gemensam kund påstås; överlapp är en separat kunskapslucka enligt D4.

## Lästa källbelägg

- SRC-FIPO-TF-2025, Fysisk PDF-sida, sida 2: ”plattform för finansiering av terrorism”. Direkt stöd för TF; inte en fristående PT-höjning av associationsformen.
- SRC-FIPO-TF-2025, Fysisk PDF-sida, sida 4: ”samma kanaler”. Gemensamma kanaler bevisar inte att just organisationsformen höjer PT.

## Genomförande och beroenden

Granskningsobjektet D7 binder följande sakobjekt med exakta innehållssummor i `regelbas/beslutstabeller/metodbeslut.yaml`: H-03, H-TF-01, H-TF-03, S-ARB-05, S-KUND-02, SRC-FIPO-TF-2025, T-BOLAG-01, T-BOLAG-02, T-BOLAG-03, T-RED-01, T-RED-02, T-RED-03, T-RED-04, T-RED-05, T-RED-06, T-RED-07, T-RED-08, T-RED-09, T-SKATT-01. Hela modellfilinventariet och gemensamma laddnings-/validerings-/attestfiler samt rapportens metodmoduler binds separat. Beslutets innehåll, aktuella sakobjekt och aktuella filhashar ingår i samma attest; befintlig modellvalidering krävs därutöver.

Ombindningar av tidigare, fortsatt ogranskade beslut: [{"beslut": "D3", "objekt": ["S-ARB-05"]}, {"beslut": "D6", "objekt": ["S-ARB-05"]}].

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

Fulla före-/efterutfall, varje numerisk sänkning, borttaget scenario, regelbas och modellfilmanifest: `.superpowers/evidens/2026-10-23-metodbeslut/D7/`. En oförändrad slutnivå är inte bevis för att ett modellval är riktigt. Kontrastprov och samlade regressioner körs vid slutet enligt användarens instruktion.

## Avslag

Vid avslag: ompröva D7 och dess angivna sakobjekt/modellfiler i ny regelversion. Avslaget får inte kringgås med ändrad text. Bind om alla beslut som delar ändrade objekt/filer, fortsätt med ej_granskad och nytt expertbeslut. Räkna om varje scenario i sexfallen och kontraster, revidera berörda modellfacit/valideringsrapporter, bygg nya analyser/skrivunderlag/V10-rapporter/PDF:er och tre expertpaket, kräv ny samlad sakgranskning. Låsta historiska paket ändras inte.

Regelbasvalidering och beräkningsbygge passerar; ingen grön testsvit påstås. Ingen push eller merge.
