# D-LAGRE – ombindningar

Regelbas 2.12.0. **Provisoriskt metodval, ej_granskad. Ingen sakkunnigprövning utförd.**

Val: Enbart redovisning, ingen automatisk nivåeffekt. Alternativ: Avdrag efter belagd relevans-, överlapps- och kontrollprövning.

PTL:s omständigheter kan tyda på låg risk men anger inga automatiska avdrag. Nuvarande data räcker inte för att knyta lägre kundrisk till varje tjänsts specifika missbruksscenario eller skilja överlapp från redan tillgodoräknade kontroller. Alla fem indikatorer redovisas separat utan nivåeffekt. EES-hemvist neutraliserar inte riskbransch, kontanter eller andra högre indikatorer.

Osäkerhet: Ett framtida tjänsteavdrag kräver kalibrering, kund-/tjänsterelevans, känd samtidighet och prövning av dubbelräkning. Okända länder eller saknat centralt landunderlag är inte låg risk. Valet att avstå automatisk sänkning är också ett ej granskat metodval.

## Lästa källbelägg

- SRC-PTL, 2 kap. 4 §; registrerad lydelse 2020-01-01, sida ej sidnumrerad lagtext: ”kan tyda på”. Möjlig indikator, inte föreskrivet automatiskt avdrag i tjänstens allmänna riskbedömning.

## Genomförande och beroenden

Granskningsobjektet D-LAGRE binder följande sakobjekt med exakta innehållssummor i `regelbas/beslutstabeller/metodbeslut.yaml`: L-PTL-04-01, L-PTL-04-02, L-PTL-04-03, L-PTL-04-04, L-PTL-04-05, P-GEO.antal_hemvist_ovriga_ees, P-GEO.antal_hemvist_sverige, P-GEO.antal_hemvist_utanfor_ees, P-KUND.antal_aktiva, P-KUND.antal_offentlig, P-KUND.antal_reglerad_marknad, SRC-PTL. Hela modellfilinventariet och gemensamma laddnings-/validerings-/attestfiler samt rapportens metodmoduler binds separat. Beslutets innehåll, aktuella sakobjekt och aktuella filhashar ingår i samma attest; befintlig modellvalidering krävs därutöver.

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

Fulla före-/efterutfall, varje numerisk sänkning, borttaget scenario, regelbas och modellfilmanifest: `.superpowers/evidens/2026-10-23-metodbeslut/D-LAGRE/`. En oförändrad slutnivå är inte bevis för att ett modellval är riktigt. Kontrastprov och samlade regressioner körs vid slutet enligt användarens instruktion.

## Avslag

Vid avslag: ompröva D-LAGRE och dess angivna sakobjekt/modellfiler i ny regelversion. Avslaget får inte kringgås med ändrad text. Bind om alla beslut som delar ändrade objekt/filer, fortsätt med ej_granskad och nytt expertbeslut. Räkna om varje scenario i sexfallen och kontraster, revidera berörda modellfacit/valideringsrapporter, bygg nya analyser/skrivunderlag/V10-rapporter/PDF:er och tre expertpaket, kräv ny samlad sakgranskning. Låsta historiska paket ändras inte.

Regelbasvalidering och beräkningsbygge passerar; ingen grön testsvit påstås. Ingen push eller merge.
