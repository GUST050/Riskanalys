# D9 – ombindningar

Regelbas 2.11.0. **Provisoriskt metodval, ej_granskad. Ingen sakkunnigprövning utförd.**

Val: Behåll indikatorpåslag och tak med scenarioavgränsad ersättning. Alternativ: Inför kalibrerade vikter, områdespoäng eller nya trösklar.

Effekter summeras med golv låg och tak hög i samma hot och dimension. Ersättning gäller bara när ersättande faktor själv verkar i scenariot. +1, minst-en-/andelströsklar och tak är provisoriska heuristiska metodval, inga sannolikhetsestimat eller antaganden om oberoende. Varje kvarvarande orsak och tillämpat villkor redovisas även efter mättnad. B:s snävare distansvillkor bevaras.

Osäkerhet: Korrelerade indikatorer kan mätta modellen. Katalogområden bevisar inte självständiga orsaker och alternativa vikter saknar kalibreringsunderlag. En kontra flera orsaker kan därför ha samma nivå utan att orsaksbilden är densamma.

## Lästa källbelägg

- SRC-TS-2026-14, Fysisk PDF-sida, sida 7: ”i kombination”. Stöder prövning av samverkan men anger inte oberoende, vikt, tröskel eller tak.
- SRC-TS-2026-14, Fysisk PDF-sida, sida 10: ”hur stora konsekvenserna skulle bli”. Kräver analys av sannolikhet och konsekvens; anger ingen matris, faktorvikt eller kontrollreduktion.

## Genomförande och beroenden

Granskningsobjektet D9 binder följande sakobjekt med exakta innehållssummor i `regelbas/beslutstabeller/metodbeslut.yaml`: BT-SANN-02-01, BT-SANN-02-02, BT-SANN-02-03, BT-SANN-02-04, BT-SANN-02-05, BT-SANN-02-06, BT-SANN-02-07, BT-SANN-02-08, BT-SANN-02-09, BT-SARB-01, P-GEO.andel_agare_utanfor_ees, P-GEO.andel_hogrisktredjeland, P-GEO.andel_transaktion_utanfor_ees, P-GEO.andel_utland_agare, P-GEO.andel_utland_transaktion, P-GEO.andel_utsatt_omrade, P-GEO.antal_agare_utanfor_ees, P-GEO.antal_hemvist_ovriga_ees, P-GEO.antal_hemvist_sverige, P-GEO.antal_hemvist_utanfor_ees, P-GEO.antal_hogrisktredjeland, P-GEO.antal_transaktion_utanfor_ees, P-GEO.antal_utland_agare, P-GEO.antal_utland_transaktion, P-GEO.antal_utsatt_omrade, P-GEO.sanktionsanknytning, P-KANAL.andel_digitalt_underlag, P-KANAL.andel_hanvisade, P-KANAL.antal_bankdata, P-KANAL.antal_digitalt_underlag, P-KANAL.antal_hanvisade, P-KANAL.bankdata_andel, P-KUND.andel_juridisk, P-KUND.andel_kontant, P-KUND.andel_nya, P-KUND.andel_riskbransch, P-KUND.andel_utan_mote, P-KUND.antal_aktiva, P-KUND.antal_juridisk, P-KUND.antal_kontant, P-KUND.antal_nominella_agare, P-KUND.antal_nya, P-KUND.antal_offentlig, P-KUND.antal_okand_betalare, P-KUND.antal_osaker_distansidentitet, P-KUND.antal_personlig_formogenhet, P-KUND.antal_reglerad_marknad, P-KUND.antal_riskbransch, P-KUND.antal_sanktionshemvist, P-KUND.antal_terrorhemvist, P-KUND.antal_utan_mote, P-ORG.antal_anstallda, P-ORG.koncernmoder, P-ORG.namn, P-ORG.sarskilda_funktioner, P-ORG.sateslan, P-ORG.utlandsk_filial, P-ORG.verksamhetsstallen, P-RISK.ensam_roller, P-RISK.extern_kyc, P-RISK.hogrisktredjeland, P-RISK.ideell, P-RISK.komplex_agare, P-RISK.korruption, P-RISK.kortlivad, P-RISK.kundberoende, P-RISK.nara_relation, P-RISK.ombud, P-RISK.overtagen, P-RISK.pep, P-RISK.svagt_aml, P-RISK.utan_mote, P-RISK.utan_utbildning, P-RISK.utkontraktering, P-RISK.utlandsk_agare, P-RISK.utsatt_omrade, S-ARB-01, S-ARB-02, S-ARB-03, S-ARB-04, S-ARB-05, S-ARB-06, S-ARB-07, S-ARB-08, S-ARB-09, S-ARB-10, S-ARB-11, S-ARB-12, S-ARB-13, S-ARB-14, S-ARB-15, S-ARB-16, S-ARB-17, S-ARB-18, S-ARB-19, S-ARB-20, S-ARB-21, S-ARB-22, S-ARB-23, S-GEO-01, S-KANAL-01, S-KOMB-01, S-KUND-01, S-KUND-02, S-TJ-01, S-TJ-02, S-TJ-03, S-TJ-04, S-VERK-01, SRC-TS-2026-14, T-BOLAG-01, T-BOLAG-02, T-BOLAG-03, T-RED-01, T-RED-02, T-RED-03, T-RED-04, T-RED-05, T-RED-06, T-RED-07, T-RED-08, T-RED-09, T-SKATT-01. Hela modellfilinventariet och gemensamma laddnings-/validerings-/attestfiler samt rapportens metodmoduler binds separat. Beslutets innehåll, aktuella sakobjekt och aktuella filhashar ingår i samma attest; befintlig modellvalidering krävs därutöver.

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

Fulla före-/efterutfall, varje numerisk sänkning, borttaget scenario, regelbas och modellfilmanifest: `.superpowers/evidens/2026-10-23-metodbeslut/D9/`. En oförändrad slutnivå är inte bevis för att ett modellval är riktigt. Kontrastprov och samlade regressioner körs vid slutet enligt användarens instruktion.

## Avslag

Vid avslag: ompröva D9 och dess angivna sakobjekt/modellfiler i ny regelversion. Avslaget får inte kringgås med ändrad text. Bind om alla beslut som delar ändrade objekt/filer, fortsätt med ej_granskad och nytt expertbeslut. Räkna om varje scenario i sexfallen och kontraster, revidera berörda modellfacit/valideringsrapporter, bygg nya analyser/skrivunderlag/V10-rapporter/PDF:er och tre expertpaket, kräv ny samlad sakgranskning. Låsta historiska paket ändras inte.

Regelbasvalidering och beräkningsbygge passerar; ingen grön testsvit påstås. Ingen push eller merge.
