# Riskanalys

Ett program som tar fram och förvaltar den dokumentation som verksamhetsutövare behöver enligt penningtvättsregelverket: allmän riskbedömning, rutiner och riktlinjer, kundriskmodell, kravmatris och löpande uppföljning. Dokumentationen anpassas till den egna verksamheten, och varje påstående går att spåra till en källa.

Första målgrupp är redovisnings- och konsultbyråer under Länsstyrelsens tillsyn.

> **Status:** designfas. Ingen programkod ännu. Se [docs/STATUS.md](docs/STATUS.md).

## Dokumentation

| Dokument | Innehåll |
|---|---|
| [Designspecifikation](docs/superpowers/specs/2026-10-08-riskanalys-design.md) | Föreslagen struktur, datamodell, riskmetod, AI-lager, granskning och etapper |
| [Research](docs/research/README.md) | Källmaterial, kravkarta, tillsyn och sanktioner, EU-regelverk, metod, teknik och referensdata |
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

## Ansvar

Programmet ger underlag. Verksamhetsutövaren fastställer dokumentationen och ansvarar för att regelverket följs.
