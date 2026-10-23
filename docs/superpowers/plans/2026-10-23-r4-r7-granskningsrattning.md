# Rättning efter R4–R7 – genomförandeplan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking. Genomför här i befintlig separat klon; inga subagenter, ingen push eller merge.

**Goal:** Kräva styrkt samlad R-granskning före ny V9-fastställelse och rätta de fyra mindre granskningspunkterna.

**Architecture:** Den enskilda domänfunktionen avvisar V9:s resultatavsnitt. Den samlade vägen använder en privat gemensam registreringsfunktion och märker posterna med `granskningssatt: samlad_resultatrapport`. Giltighetskontrollen kräver märkningen för R. Saknat nytt fält utelämnas vid serialisering. Historisk verifiering läser fortfarande frysta paket utan aktuell sakprövning. Presentationens fasta mall/policy versionsändras vid text- och layoutändringar.

**Tech Stack:** Python 3.12.15, Pydantic, pytest och befintlig Word/PDF-rendering.

**Spec:** Del 1 i användarens godkända uppdrag revision 3, `/Users/danieltrogen/riskanalys-steg1-3/docs/superpowers/reviews/2026-10-23-uppdrag-codex-r4-r7-och-regelbas.md`; befintlig resultatrapportdesign `../specs/2026-10-22-resultatrapport-design.md`.

## Global Constraints

- Ingen ändring av riskmetod, regelbas, AI-anrop eller sakkunnigstatus.
- Python 3.12 via `.venv312/bin/python`; syntetiska uppgifter och Testleverantor.
- Riktade RED/GREEN-prov och snabbprofil före arbetscommit; färsk fullsvit före leverans enligt AGENTS regel 6.
- A/B1 ska fortfarande kunna granskas enskilt. Historiska V8/V9-paket ska verifieras oförändrade.
- Stanna efter levererad del 1 för användarens granskning före regelbasens steg A.

## Review Focus

1. Direkt domänanrop får inte kringgå CLI-spärren för R.
2. Ett äldre godkännande med rätt text-, struktur- och analyssumma får inte räcka för ny fastställelse.
3. Den senaste underkända granskningen får inte ersättas med ett äldre godkännande.
4. Saknat nytt fält får inte ändra historisk serialisering; befintliga frysta paket verifieras efter uppgraderingen.
5. Läsbara tider och bilagehänvisningar får inte ändra eller kapa lokala saktexter.

## Task 1: Samlad granskning och historisk kompatibilitet

**Files:** `src/riskanalys/faststallelse/{modeller,sakgranskning,resultatgranskning}.py`; `tester/enhet/test_resultatgranskning_v9.py`, `tester/enhet/test_resultatrapport_cli.py`, `tester/typfall/{test_resultatrapport_hela_kedjan,test_gemensam_analys_hela_kedjan}.py`.

**Interfaces:** Publika `registrera_sakgranskning(...)` behåller sin signatur. Privat `_registrera_sakgranskning(...)` delar postbyggnad, med valfritt `granskningssatt`. `registrera_resultatgranskning(...)` behåller sin signatur. `Sakgranskning.granskningssatt` är `Literal['samlad_resultatrapport'] | None`, standard `None`.

- [x] Skriv prov för avvisat enskilt godkännande/underkännande av R, fortsatt A/B1-granskning, märkta samlade poster, äldre poster utan märkning och oförändrad äldre serialisering.
- [x] Kör `.venv312/bin/python -m pytest -q tester/enhet/test_resultatgranskning_v9.py tester/enhet/test_resultatrapport_cli.py` och bekräfta förväntad RED för den saknade spärren/märkningen.
- [x] Inför domänspärr, privat postbyggnad, samlad märkning och krav vid giltighetskontroll. Äldre R-status ger en konkret uppmaning om förnyad samlad granskning.
- [x] Prova CLI-avslag utan ändrad sparfil samt verklig fastställelse som avvisar äldre R-poster men godtar nya samlade poster och A/B1. Prova historiska paket utan omrendering och utan granskningssättfält.
- [x] Kör berörda sakgransknings-/V8-/V9-prov; Expected: alla passerar, inga försvagade spärrar.

## Task 2: Läsbar leverans och bilagans sidflöde

**Files:** `src/riskanalys/dokument/{presentation_v9,leverans_v9,rendering_v9}.py`, `tester/enhet/test_rendering_v9.py`, `docs/testning.md`.

**Interfaces:** Ny leveransmallversion och renderingspolicy. UTC-körningsidentiteter visas som datum/tid i Europe/Stockholm; full identitet finns kvar i `LeveransV9`/manifestet. Icke-tidsbaserade identiteter återges som tidigare.

- [x] Skriv och kör RED-prov för texten `Blockerande fynd hindrar fastställelse` och läsbar tid med oförändrad leveransidentitet.
- [x] Lägg till fyndförklaringen efter antalet blockerande fynd. Versionsändra leveransmallen och formatera bara visningstexten.
- [x] Förankra bilagehänvisningen till föregående stycke med Word-sidflöde; bevara all text. Kontrollera båda referensfallen via faktisk PDF. Tvinga inte sidminskning om det kräver kapning.
- [x] Förtydliga accepterad analysprofiltid 376,465 s mot målet 180 s i `docs/testning.md`.
- [x] Kör berörda presentations-/renderings-/kedjeprov och snabbprofil. Expected: grön, oförändrat källsnapshot under varje profil.

## Task 3: Leveransgrind och granskningssvar

**Files:** `docs/superpowers/reviews/2026-10-23-svar-r4-r7-granskning.md`, `docs/STATUS.md`.

- [x] Granska hela diffen mot del 1 och de fem Review Focus-punkterna.
- [x] Kör `.venv312/bin/python scripts/testa.py full --ut /private/tmp/riskanalys-r4-r7-rattning-full-<unikt>`; Expected: verifierad, collection/JUnit matchar, noll fel/skippade, oförändrat snapshot.
- [x] Skriv kort granskningssvar med ändringar, RED/GREEN, PDF-kontroll, testresultat och kvarstående begränsningar. Uppdatera STATUS.
- [x] Commit lokalt efter gröna kontroller; kontrollera att levererat snapshot matchar fullsvitens. Ingen push eller merge.
