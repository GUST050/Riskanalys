# Redaktionell runda för V10 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Genomför inline; en samlad färsk slutreview efter produktanpassning och läsversion. Offline-PDF är första användarkontrollpunkten.

**Goal:** Läsbar och kortare resultatrapport med fullständigt bevarat sakinnehåll och en mindre läsversion av sakkunnigunderlaget.
**Architecture:** En separat offlinepresentation byggs ur exakt frysta V10-källor från d8a91a1. Ny presentationsversion, oförändrade källor och produktvägar. Gemensam formatterare använder fältkatalog och fast ordlista; varje flytt har källposition, målposition och innehållssumma. Efter PDF-godkännande beslutas produktkopplingen uttryckligen och därefter byggs expertunderlag om en gång.
**Tech Stack:** Python 3.12, befintliga dokumentmodeller, python-docx, LibreOffice/Poppler, pytest.
**Spec:** `/Users/danieltrogen/riskanalys-steg1-3/docs/superpowers/reviews/2026-10-24-uppdrag-codex-redaktionell-runda.md`.

## Global Constraints

- Inga ändringar i motor, regelbas, nivåer, statusar eller spärrar. Ingen push/merge. Inga AI-anrop eller verkliga byrådata.
- Byråns fritext bevaras hel och ordagrant. Programetiketter formateras separat från original.
- Samtliga flyttade stycken och tabeller bevaras i A/B1 med exakt källa, mål och innehållssumma. Sänkningar, åtgärder och nivåer ska finnas kvar i huvudrapporten.
- Riktmärke högst tio faktiska huvud-PDF-sidor; ingen kapning eller oläsligt liten text för att nå det.
- Först alla sex offline-PDF:er och användarens klartecken; sedan produktkedja; sist fullständigt sakkunnigunderlag/läsversion. ZIP byggs endast på slutet enligt användaren.
- Riktade prov och snabbprofil under arbetet. Ny fullsvit på slutlig produktkod före slutleverans, inte upprepad mellan offlineiterationer.
- Befintliga D-beslut binder alla appfiler. Offlineverktygen ligger utanför appkoden. Konflikten mellan framtida produktkod och oförändrad regelbassumma redovisas före produktkontrollpunkten; ingen bindning lättas eller skrivs om i smyg.

## Review Focus

1. Fritext som innehåller koder eller rollklamrar får aldrig skrivas om av formatteraren; en konflikt ska visas, inte döljas.
2. Färre rader får inte slå ihop lokala scenariovarianter, olika nivåvägar, kontrollmål eller statusar.
3. Varje flyttad originaltext och varje tabellcell ska kunna hittas oförändrad vid sitt registrerade mål; brutna mål upptäcks.
4. Äldre V10-presentationer och historiska V8/V9/V10-filer ska behålla sina bytes och verifieringsvägar.
5. Läsunderlagets gemensamma filer måste vara byteidentiska med slutligt fullständigt expertunderlag.

### Task 1: Offlineformat och flyttkontrakt

**Files:** `docs/research/verktyg/redaktionell_v10.py`, `tester/enhet/test_redaktionell_offline.py`.
**Interfaces:** konsumerar frysta `kallor.json` och `presentation.json`; producerar separata renderade dokument och transformationslista med källa/mål/summa.

- [x] RED: formatterare ger svenska etiketter, fem riskstatusar, belopp/andel/period, rollnamn och bevarad fritext.
- [x] GREEN: implementera gemensam formatterare utan ändring i appen eller regelbasen.
- [x] RED→GREEN: flyttverifiering avvisar saknat/ändrat mål och godtar exakt bevarade original.

### Task 2: Redaktionellt offlinebygge

**Files:** samma verktyg, kompletterande regressioner och granskningsunderlag.
**Interfaces:** producerar ny offlineversion, alla tre delar, råvärdeskontroll, medlemslista och bevarandekontroll.

- [x] Flytta hottabell och källregister till B1, tjänsteerfarenheter/metodtexter/full kontrolltabell till A; registrera varje text och cell.
- [x] Samla katalogmekanismer för de nya hoten i 4.2 endast med identiska nivåvägar/kontrollpåverkan/status. Lokala varianter stannar i 4.3.
- [x] Behåll alla nivåer, statusar, åtgärder, ursprungliga motiveringar och korta sänkningsförklaringar. Kort tjänstetabell hänvisar till exakta original i A.
- [x] Riktat och snabbprofil; jämför källbytes, motorutfall och regelbassumma mot basen.

### Task 3: Första kontrollpunkten

**Files:** sex PDF:er och transformationslistor under `.superpowers/evidens/2026-10-24-redaktionell-offline/`, rapport i `docs/superpowers/reviews/`.

- [x] Rendera faktiska PDF:er. Läs varje huvudsida, stickprova ändrade bilagesidor, mät sidantal och kontrollera synlig text.
- [ ] Lämna förhandsvisningen för användarens PDF-klartecken. Produktkedja och expertpaket ändras inte före respektive kontrollpunkt.

### Task 4: Efter PDF-klartecken

- [ ] Redovisa och lös D-filbindningens konflikt med oförändrad regelbassumma genom ett uttryckligt godkänt upplägg innan produktkod ändras.
- [ ] Integrera ny presentationsversion med uttryckligt formatbyte och förnyad samlad sakgranskning; bevara historiska verifieringsvägar.
- [ ] Skapa läsversion per region med identiska gemensamma filer, redovisad storlek/antal och hänvisning till fullständigt underlag. Bygg ZIP en gång på slutet.
- [ ] Samlad slutreview, riktade prov, snabbprofil och färsk fullsvit på exakt slutligt snapshot. Redovisa var fullsvitens tid ligger genom JUnit-data. Ingen push/merge.

Genomförandeval: befintlig ren featuregren återanvänds. Uppdragets uttryckliga beställning av offlineförhandsvisning är klartecken till detta avgränsade bygge; inga extra allmänna plan-/designgodkännanden införs före PDF-kontrollpunkten.
