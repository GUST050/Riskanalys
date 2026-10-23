# Regelbasens steg B Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Genomför inline med TDD och en samlad oberoende slutgranskning.

**Goal:** Komplettera katalogerna enligt godkänd inventering och användarens preciseringar, utan steg C/D:s nivå- eller metodkalibrering.

**Architecture:** Behåll den typade deterministiska motorn. Lägg till två tjänster med befintligt intags-/kontrollmönster, sex räknade riskuppgifter och separat datakatalog för fem lägre-risk-indikatorer utan nivåeffekt. Bind källversioner och nya granskningsobjekt; lägg stödomfattningsstopp i den gemensamma rättsliga omfattningen så det syns i utkast och hindrar fastställelse.

**Tech Stack:** Python 3.12, Pydantic, YAML, pytest; syntetiska data och Testleverantor.

**Spec:** `docs/superpowers/reviews/2026-10-23-katalogluckor.md` med användarens beslut i `/Users/danieltrogen/riskanalys-steg1-3/docs/superpowers/reviews/2026-10-23-uppdrag-codex-r4-r7-och-regelbas.md`, avsnitt Beslut efter granskningen av steg A.

## Global Constraints

- Endast T-RED-08/09 byggs. Trust/nominee-ja stoppar fastställelse men inte utkast.
- Sex nya högre-risk-frågor är kundantal med period och stöd för okänt.
- En samlad fördelningsfråga Sverige/övriga EES/utanför EES. Ingen individuell landsbedömning hos byrån. Regelbasens bedömning får vara okänd när källstöd saknas.
- Lägre-risk-indikatorer är data utan riskavdrag. Ingen ändring i AI-tillåtelselistan.
- H-MOD-06 beskriver PT/TF-grund. Källversionen för Europol registreras innan nya hänvisningar.
- Alla nya/ändrade katalog-/metodobjekt är ej_granskad. En regelversion/commit för steg B. Ingen push/merge.
- Färsk fullsvit krävs före slutleverans/PR/merge. B är ett granskningsbart arbetssteg: berörda tester och snabbprofil före arbetscommit. Granskning efter B innan C.

## Review Focus

1. Äldre profiler saknar nya fält: saknat ska bli okänt, aldrig noll och inte en obelagd sänkning.
2. Trust/nominee-ja ska stoppa även om gammal bedömning eller intagsväg används; utkast får skapas och förklara hindret.
3. Separata hemvistantal får inte användas till att gissa enskilda utom-EES-länder eller försumma period/summakontroll.
4. Äldre signerade paket ska bevara innehållssummor när nya schemasamlingar är tomma.
5. Nya tjänsters frågor, kontroller och hot ska nås genom verkligt intag, urval, analys och dokumentation; inget hårdkodat tyst bortfall.

### Task 1: Baslinje, källversioner och omfattningsstopp

**Files:** `regelbas/kallor.yaml`, `src/riskanalys/regelverk/tillsyn.py`, `src/riskanalys/regelverk/sakkunnig.py`, `tester/regelkontrakt/test_katalogkomplettering_b.py`.
**Interfaces:** befintlig `rattlig_omfattning(rb, profil)` producerar hinder för motor/utkast/fastställelse. Ny källa behåller original-ID/checksumma och får eget versions-ID.

- [x] Spara samma syntetiska profiler och motorutfall före B i ignorerat evidensarkiv.
- [x] RED: trust/nominee-ja ger hinder, nej ger inte stödhinder, okänt blir preliminärt; ny Europolversion är separat från originalet.
- [x] GREEN: lägg stödhinder i gemensam omfattning och källversion i registret. Notera 01FS-avvikelsen i sakkunnigunderlaget.

### Task 2: Typade indikatorer och kundantal

**Files:** `regelbas/falt.yaml`, `regelbas/kataloger/sarbarheter.yaml`, ny `regelbas/kataloger/lagre_risk.yaml`, modeller/laddning/validering/sakkunnig under `src/riskanalys/regelverk/`, `src/riskanalys/profil/omfattning.py`, intagets samlade formulär, testfilen ovan.
**Interfaces:** ny samling `Regelbas.lagre_risk` med fem källbundna granskningsobjekt, ingen koppling till motorhöjning/sänkning. Geografiskt underlag och bedömning ligger i regelbasens objekt, aldrig AI.

- [x] RED: sex heltalsfrågor har period, noll och okänt hålls isär; fem lägre-indikatorer ger ingen motoreffekt; hemvistfrågan samlas och antal/period måste stämma med basen.
- [x] GREEN: fem nya sårbarheter, snävare distansvillkor, två lägre-risk-antal och tre samlade hemvistantal. Länder utanför EES kan inte bedömas ur en totalsiffra och visas okända; det är ett uttryckligt centralt metodval, inte en fråga per kund.
- [x] Kontrollera att nya objekt finns i granskningsmallen och gamla schemasummor består med tom ny samling.

### Task 3: Tjänster, modus och katalogpreciseringar

**Files:** `regelbas/kataloger/{tjanster,hot,kontroller,sarbarheter}.yaml`, `regelbas/falt.yaml`, regionala paket och intags-/tjänstmetadata där ny tjänst kräver registrering, testfilen ovan.
**Interfaces:** T-RED-08/09 följer tjänstmodellens ordinarie fält, hot och kontroller. Nya modus H-MOD-05/06/07 och tjänstehot har oförändrat ogranskat medel som standard i väntan på C.

- [x] RED: båda tjänsterna kan erbjudas och bedömas, deras frågor aktiveras i intaget, nya hot har källlocator och PT/TF-grund; inga trust-/nomineetjänster finns.
- [x] GREEN: komplettera två tjänstegrenar/kontroller, tre modus och motiverade kopplingar. Förtydliga fakturering, lön, strukturer, krypto/plattformar och styrelserepresentation. Byt fyra läsbara S-TJ-namn.
- [x] Kör katalogvalidering och berörda tester; rätta faktiska kontraktsbrott. Ändra aldrig frysta historiska fixturer för att få nya katalogfacit att passa.

### Task 4: Samlad verifiering och granskningsleverans

**Files:** ny `docs/superpowers/reviews/2026-10-23-regelbas-steg-b.md`, `docs/STATUS.md`, beroenden/före-efter i granskningsunderlaget, `regelbas/version.yaml`.
**Interfaces:** slutlig 2.1.0 jämförs med baslinjen 2.0.0, samma profiler; historiska frysta paket verifieras med egna källor.

- [x] Räkna nya intagsfält mot 324 och skilj samlad fråga från antalet fält. Redovisa beroenden, okända uppgifter och varje eventuell sänkning.
- [x] Kör riktad svit och snabbprofil, en samlad oberoende granskning, åtgärda betydelsefulla fynd med RED/GREEN.
- [x] Starta fullsvitskontroll med snapshot/collection/JUnit och redovisa röda/avbrutna urval. Slutlig grön fullsvit krävs före slutleverans/PR/merge, inte före start av varje arbetssteg.
- [x] Arbetscommit för B med dokumenterad version, känd fullsvitsstatus och lokal ren gren. Stanna före C för användarens granskning.
