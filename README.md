# Riskanalys

Ett program som tar fram och förvaltar den dokumentation som verksamhetsutövare behöver enligt penningtvättsregelverket: allmän riskbedömning, rutiner och riktlinjer, kundriskmodell, kravmatris och löpande uppföljning. Dokumentationen anpassas till den egna verksamheten, och varje påstående går att spåra till en källa.

Första målgrupp är redovisnings- och konsultbyråer under Länsstyrelsens tillsyn.

> **Status:** etapp M1 (tunn kedja) är byggd och körs med syntetiska uppgifter. Regelbasen är inte sakkunniggranskad, så inget kan fastställas för en riktig byrå än. Se [docs/STATUS.md](docs/STATUS.md).

## Dokumentation

| Dokument | Innehåll |
|---|---|
| [Designspecifikation](docs/superpowers/specs/2026-10-08-riskanalys-design.md) | Föreslagen struktur, datamodell, riskmetod, AI-lager, granskning och etapper |
| [Research](docs/research/README.md) | Källmaterial, kravkarta, tillsyn och sanktioner, EU-regelverk, metod, teknik och referensdata |
| [Tillsynsmaterial och granskningsfall](docs/research/09-tillsynsbeslut-2026.md#bevarat-underlag-och-återanvändbara-granskningsfall) | Bevarade original utanför repot och syntetiska fall med förväntade fynd för bygget och utvärderingen |
| [Status](docs/STATUS.md) | Framsteg, beslut och nästa steg |

## Princip i korthet

```
Källor ─► Kravregister och kataloger ─► Regelpaket
                                            │
Byråprofil ─────────────────────────────────┤
                                            ▼
                                       Riskmotor ─► AI-skribent ─► Granskare ─► Export och fastställelse
                                            ▲                                          │
                                            └──────────────── Drift ◄──────────────────┘
```

- Risknivåer räknas fram av regler, inte av AI.
- AI skriver text inom ett låst schema och måste hänvisa till regelbasen.
- En granskare kontrollerar täckning och spårbarhet och letar efter de brister som tillsynen oftast påtalar.
- En ansvarig person sakgranskar varje avsnitt innan något fastställs. Ett fastställt paket låses med kontrollsummor.

## Kom igång

Kräver Python 3.12 eller senare. Byråns uppgifter sparas i `$RISKANALYS_DATA` (standard `~/RiskanalysData`), aldrig i repot.

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest
.venv/bin/riskanalys regelbas validera
```

Flödet för en byrå, med syntetiska uppgifter:

```bash
riskanalys ny testbyra --regelpaket RP-RED-VG --lan "Västra Götaland" --datum 2026-11-01
riskanalys profil testbyra                       # visar vilka uppgifter som saknas
riskanalys bekrafta testbyra P-KUND.andel_riskbransch "30 %" --kalla "Kundregistret"
riskanalys bedom testbyra
riskanalys skriv testbyra                        # kräver ANTHROPIC_API_KEY, eller --leverantor test --testsvar FIL
riskanalys utvardera testbyra --beskrivning "Första riskbedömningen."
riskanalys granska testbyra
riskanalys exportera testbyra --utkast
riskanalys sakgranska testbyra --avsnitt D-ARB.6.1 --godkann --namn "..."   # för varje avsnitt
riskanalys faststall testbyra --organ styrelsen --datum 2026-11-15 --namn "..."
riskanalys verifiera testbyra 1
```

`faststall` vägrar så länge kraven i regelbasen inte är granskade av en sakkunnig.

## Ansvar

Programmet ger underlag. Verksamhetsutövaren fastställer dokumentationen och ansvarar för att regelverket följs.
