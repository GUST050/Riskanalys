# Slutlig paketering 2.12.3

Alla fyra ZIP-arkiv är byggda en gång på slutet, efter verifierat grön fullsvit. ZIP-integritet samt SHA-256 för varje arkiverad fil mot dess verifierade paketmapp är kontrollerade. Äldre paket är bevarade. Ingen push eller merge.

Leveransmapp: `../underlag/sakkunnigpaket-2.12.3-2026-10-24/` relativt repot. Börja med läsversionen för rätt region. Fullpaketet är den tekniska grunden.

| Region | Fullpaket filer | Fullpaket byte | Läsversion filer | Läsversion byte | Identiska gemensamma filer |
|---|---:|---:|---:|---:|---:|
| RP-RED-SKANE | 571 | 412436955 | 15 | 34567540 | 12 |
| RP-RED-STHLM | 571 | 412436987 | 15 | 34567572 | 12 |
| RP-RED-VG | 571 | 412436972 | 15 | 34567563 | 12 |

Läsversionerna har 15 filer i stället för 571 och cirka 91,6 procent mindre okomprimerad datamängd. De gemensamma filerna är guide, objektgenomgång med alla 276 objekt, obesvarad mall, metodsammanställning, beroenden, före-/efterskillnader och sex PDF:er. Alla mallar har tom identitet/kompetens, oberoende=False och samtliga objekt ej_granskad.

| Arkiv | Byte | SHA-256 |
|---|---:|---|
| `lasversion-RP-RED-SKANE-2.12.3.zip` | 3289037 | `sha256:72f2a50e6cc890be454a776ae3c169b09182ad621a781a520f81c925a00b9da1` |
| `lasversion-RP-RED-STHLM-2.12.3.zip` | 3289037 | `sha256:40780f3c1e733de4394d9957b43981960993302456b3a6891922e65382484209` |
| `lasversion-RP-RED-VG-2.12.3.zip` | 3288940 | `sha256:aee8e99eb517c25efd2449677937a5240a8636a5388ba1a0e03df6f2fb655dfe` |
| `fullstandigt-sakkunnigunderlag-2.12.3.zip` | 203709669 | `sha256:fc2835ebb270fcf9d75a7717a663ce2ab939fea6d554321ef144a9e6179e0d0b` |

ZIP-läsversionerna är cirka 3,3 MB vardera; ZIP-fullpaketet för alla tre regioner är cirka 203,7 MB. Fullpaketen innehåller också slutprovsresultat, JUnit, det verifierade källsnapshotet, insamling, logg, tidsanalys och PDF-kontroller. Läsversionernas JSON binder till respektive slutligt fullmanifest.

Exakta maskinuppgifter finns i leveransmappens paketkontroll.json och SHA256SUMS.txt. Källkodens slutliga fullsvit: 3 594 godkända, 0 fel, 863/863 oförändrade resurser. Ingen sakkunnigstatus har frigivits.
