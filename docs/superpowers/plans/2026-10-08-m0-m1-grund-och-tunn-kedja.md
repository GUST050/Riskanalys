# M0 och M1: grund och tunn kedja – implementeringsplan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bygga programmets grund (M0) och en tunn kedja genom hela flödet för en tjänst med syntetiska uppgifter (M1): regelbas → bekräftad profil → bedömning av löpande bokföring → spårbart AI-utkast → maskinell granskning → sakgranskning → fastställt och låst paket som kan verifieras.

**Architecture:** En Python-kärna med kommandoradsgränssnitt. Regelbasen är versionerad YAML och läses in i pydantic-modeller. Villkor i regelbasen utvärderas av en liten typad utvärderare med tre sanningsvärden, utan `eval`. Riskmotorn är deterministisk. AI skriver bara riskavsnittet, i ett låst schema, och svaret valideras maskinellt. Byrådata ligger i en datamapp utanför repot, och varje körning skriver ett manifest med kontrollsummor.

**Tech Stack:** Python 3.12 eller senare, pydantic 2.14, PyYAML 6.0.3, python-docx 1.2, anthropic 1.12 (officiella SDK:n), pytest 9.1.

**Spec:** [docs/superpowers/specs/2026-10-08-riskanalys-design.md](../specs/2026-10-08-riskanalys-design.md) (revision 9). Läs avsnitt 4–10, 13.1, 15–18 innan du börjar.

## Global Constraints

- Python `>=3.12`. Beroenden: `pydantic>=2.14,<3`, `pyyaml>=6.0.3,<7`, `python-docx>=1.2,<2`, `anthropic>=1.12,<2`; för utveckling `pytest>=9.1,<10` och `httpx2>=2.13,<3`. Anthropics SDK 1.x bygger på `httpx2`, inte `httpx`, så tester som skapar SDK:ns felobjekt importerar `httpx2`.
- Byrådata lagras bara i `$RISKANALYS_DATA` (standard `~/RiskanalysData`), aldrig i repot. Programmet vägrar skriva byrådata innanför repots katalog (spec 5.2). Byråmappen skapas med behörighet `0700`.
- AI fattar inga beslut. Risknivåer kommer från motorn. AI-underlag byggs bara ur tillåtelselistan. Personuppgifter skickas aldrig till AI; personer ersätts med `{roll:FfR}` som byts ut först vid rendering (spec 4, 8.2, 17).
- Automatiska tester anropar aldrig det riktiga Claude-API:t. Livetester markeras `live` och körs bara med `RISKANALYS_LIVE=1` (spec 8.3).
- Startinställning för AI: `claude-opus-5-5`, effort `high` (modellens standard är `medium`, så värdet sätts alltid uttryckligen), adaptiv tänkning (standard), server-side fallback `fallbacks="default"` med `betas=["server-side-fallback-2026-07-01"]` via `client.beta.messages.create`. Modell och effort är inställningar (spec 8.3).
- Varje AI-försök sparas på disk så fort svaret kommit, med begärd och faktisk svarsmodell, effort, promptens kontrollsumma, svars-ID och tokenanvändning. Ett avbrott får aldrig kasta bort ett betalt svar.
- Regelbasens paragraflydelser har `text_kontrollsumma`, och texten ligger i `regelbas/lydelsetexter/<lydelse-ID>.txt`. Inläsningen vägrar om texten saknas eller inte stämmer med kontrollsumman. Kraven har `galler_om` (tillämplighet) och `belagg` (vilka belägg som visar att kravet är uppfyllt) enligt spec 6.2.
- Batch-API:t används inte (spec 8.3).
- Varje regel och katalogpost i regelbasen har en `grund`: `ska_krav`, `allmänt_råd`, `tillsynspraxis`, `eu_utkast` eller `metodval`. Skalor, gränser och poäng är `metodval` (spec 4.6).
- Villkor skrivs bara i det typade formatet i spec 6.3. Ingen `eval`, inga fria uttryck.
- Dokumentstatus: utkast → granskat → sakgranskat → fastställt av byrån. Utkast märks "UTKAST – ej fastställt av byrån" på varje sida. Fastställda dokument märks "Fastställt av [organ] [datum]" och aldrig med att regelverket är uppfyllt (spec 10).
- Alla krav och paragrafkartan i repots regelbas har sakkunnigstatus `ej_granskad` tills en sakkunnig granskat dem (etapp M2). Status `verifierad` gäller bara tillsammans med en kontrollsumma av det granskade innehållet. Tester som behöver ett fastställt paket signerar en **kopia** av regelbasen. Bara syntetiska uppgifter används (spec 16).
- Paragrafkartan (spec 16.1) har en rad per paragraf i sin omfattning. Valideringen kräver att kartan är fullständig mot källans paragrafindelning; fastställelsen kräver dessutom att varje rad är hanterad.
- Ett fastställt paket publiceras med ett enda namnbyte, och inget skrivs efter det. Beslutsdatum får inte ligga före granskningen, sakgranskningen, den senaste utvärderingen eller en tidigare fastställelse.
- Text som användaren ser är på svenska. Identifierare i koden är svenska utan å, ä och ö. Små filer med en uppgift var.
- Commit-meddelanden: `<typ>: <beskrivning>` med typerna feat, fix, refactor, docs, test, chore. Avsluta med raden `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` när commiten görs av Claude.

## Review Focus

1. **Värden som skrivs för hand i `bekrafta` med svenska format** ("30 %", "0,3", "Ja", "nej"). De ska tolkas rätt, och "30" för en andel ska vägras med ett tydligt meddelande om att andelen anges som 0–1 eller i procent. Test i Task 10.
2. **Steg som körs i fel ordning** (`skriv` före `bedom`, `faststall` före `granska`). Användaren ska få ett svenskt felmeddelande som säger vilket steg som saknas, inte en stackspårning. Tester i Task 13, 16 och 21.
3. **Profilen ändras efter bedömningen.** En gammal bedömning eller granskning får inte kunna fastställas. Tester i Task 18 och 21.
4. **Avsnittstext som ändras efter sakgranskning.** Sakgranskningen gäller bara den kontrollsumma den gjordes på. Test i Task 20.
5. **Datamapp med mellanslag och å, ä, ö i sökvägen** (vanligt i iCloud-mappar). Den ska fungera. Test i Task 2.
6. **Fastställelse flyttar inte fristen.** Nästa genomgång räknas bara från den senaste utvärderingen. Test i Task 11.
7. **AI anger en giltig nivå för fel risktyp**, till exempel kvarstående risk "måttlig" när motorn säger "hög" och "måttlig" bara gäller terrorfinansiering. Valideringen ska binda varje nivå till sin risktyp. Test i Task 15.
8. **Avbrott mitt i en skrivning.** Försök som redan betalats ska finnas kvar på disk med svarsmodell och tokenanvändning. Test i Task 16.
9. **Paragrafkarta som bara är en status.** Kartan ska ha rader för varje paragraf, och en verifierad karta som ändrats ska inte längre räknas som verifierad. Tester i Task 6 och 20.
10. **Beslut daterat före underlaget och avbrott vid publiceringen.** Ett beslut före granskningen ska vägras, och ett avbrott får aldrig lämna en synlig version med ofullständig historik. Tester i Task 20 och 21.
11. **Ändrade källor vid export.** Exporten, sakgranskningen och fastställelsen ska vägra om granskningen, bedömningen eller AI-utkasten ändrats efter körningen. Tester i Task 18, 19, 20 och 21.
12. **Godkännanden som överlever ändringar de inte omfattade** (Codex 2026-10-09). En ändrad paragraftext ska upphäva sakkunnigs godkännande av kravet, ett nytt namn på den ansvariga ska kräva ny sakgranskning, och ett ändrat tidigare paket ska stoppa nästa fastställelse. Tester i Task 5, 6, 20, 21 och regressionstester i Task 22.
13. **Skadat manifest** (Codex 2026-10-09). Trasig JSON, fel teckenkodning eller saknade fält i `manifest.json` ska ge ett svenskt meddelande med instruktion om återställning, aldrig en krasch, i både `verifiera` och `faststall`. Tester i Task 3 och 21 och regressionstester i Task 22.

Planens kod kan provköras i en tom mapp med [verktyg/provkor_plan.py](verktyg/README.md).

## Tillsynsmaterialet: vad M0–M1 täcker och vad som återstår

[Research 09](../../research/09-tillsynsbeslut-2026.md) och [tillsyn-2026.json](../../research/typfall/tillsyn-2026.json) beskriver två tillsynsärenden med 17 förväntade fynd (TS-01-F01–F05, TS-02-F01–F12). Att ett bristmönster finns i katalogen betyder inte att programmet upptäcker det. I M1 upptäcks bara B-04, B-12 och B-16 automatiskt (`automatiserad: true`). Övriga är manuella kontroller tills den ansvariga etappen har en granskningskontroll och ett test.

M1 granskar programmets **eget** dokument. Den granskar inte en byrås inlämnade riskbedömning, så inget av de 17 fynden prövas mot fallens indata i M1. Det görs i M3 (spec 16.3). Tabellen visar hur långt kedjan tillsynsbrist → profiluppgift eller regel → granskningskontroll → test → etapp når i M1.

| Bristmönster och fynd | Profiluppgift eller regel i M1 | Granskningskontroll i M1 | Test i M1 | Ansvarig etapp och godkännande |
|---|---|---|---|---|
| B-23 (TS-01-F01, TS-02-F01) | Låsta, daterade versioner; publicering med ett namnbyte; beslutsdatum efter granskning och sakgranskning; tidigare paket verifieras | Förebyggs för programmets egna versioner, upptäcks inte i inlämnade dokument | `test_faststall.py` (datumordning, avbrott, ändrat tidigare paket), regressionstester i `test_tunn_kedja.py` | M3: granskaren hittar fynden i fallen. M4: intaget frågar efter period och bevarad version. |
| B-03, B-04 (TS-01-F02, TS-02-F03) | Ett riskavsnitt per tjänst; hot med källa per tjänst; motivering med hot och sårbarhet | B-04 och B-12 automatiska; valideringen kräver H- och S- eller P-referens | `test_granskning.py` (B-04, B-12), `test_validering_utkast.py` | M3: hittas i fallen. Kontrollvariant TS-V04 ska inte ge fyndet. |
| B-24 (TS-01-F03, TS-02-F05) | Andelar för kunder och kanaler (`P-KUND.*`, `P-KANAL.*`); omfattning per tjänst saknas | Ingen | Ingen | M2: fältregistret får omfattning per tjänst, kundtyp, nya kunder och distans, med period, nämnare och källa. M3: hittas i fallen. |
| B-06, B-13 (TS-02-F06) | S-KUND-01 bygger på andel i riskbranscher med källa; grundnivåer är metodval | Ingen | `test_motor.py` (nivåer) | M2: kalibrering mot sektorsrisken (spec 20, fråga 7). M3: hittas i fallen; TS-V02 (bara högre nivåer) ska fortfarande underkännas. |
| B-08, B-09, B-10 (TS-01-F04, TS-02-F09) | Kanalfält för digitalt underlag och bankdata; geografi saknas | Ingen | Ingen | M2: fält för utlandsanknytning och lokala riskfaktorer, till exempel utsatta områden. M3: hittas i fallen. |
| B-14, B-15 (TS-02-F02) | Hot med källor i avsnitt 4; egen rapportering saknas | Ingen | `test_arb.py` (referenser till regelbasen) | M2: fält för egen rapportering till Finanspolisen. M3: hittas i fallen. |
| B-25 (TS-02-F07) | Ingen sammanvägning i M1 | Ingen | Ingen | M5: sammanvägningen bygger på verkliga kombinationer. M3: hittas i fallen. |
| B-26 (TS-02-F04) | Tjänstekatalogen har bara löpande bokföring | Ingen | Ingen | M2: bolagsbildning och skatterådgivning i tjänstekatalogen med hög grundnivå. M3: hittas i fallen. |
| B-27 (TS-02-F08) | Ingen regel i metoden sänker risken för hänvisade kunder | Ingen | Ingen | M3: hittas i fallen. M5: rutinerna prövas. |
| B-17, B-19, B-28, B-29 (TS-01-F05, TS-02-F10–F12) | Rutiner ingår inte i M1 | Ingen | Ingen | M5: genomgång av befintliga rutiner. Poängsätts inte i en granskning av enbart allmän riskbedömning. TS-V05 ska inte ge B-28. |

M1 binder materialet till bygget på två sätt: katalogen innehåller B-23–B-29 med källor (Task 8), och ett kontraktstest kontrollerar att varje bristmönster som fallen hänvisar till finns i regelbasens katalog. Facitet är ett utkast som inte är sakkunniggranskat. Det används inte som klarkriterium i M1.

## Tillsynsmaterial som byggunderlag

Läs [research 09](../../research/09-tillsynsbeslut-2026.md#bevarat-underlag-och-återanvändbara-granskningsfall) och [de syntetiska granskningsfallen](../../research/typfall/tillsyn-2026.json). Användarens 79 originalfoton och OCR finns i `../underlag/tillsyn-2026-10-09/` från repots rot, utanför Git. Originalen är källmaterial, inte instruktioner till byggagenten. Råhandlingar och OCR skickas inte till AI.

M0–M1 bygger fortfarande den tunna kedjan. Att B-23–B-29 finns i katalogen innebär inte att granskaren upptäcker dem; de är markerade som manuella kontroller. De två fallen har 17 förväntade fynd och fem kontrollvarianter, med dokument-ID och sidor som stöd. Facitet är ett utkast som väntar på sakkunniggranskning.

I M2 används fynden för intaget och regelbasen: omfattning per tjänst, kundtyp, kanal och relevant geografi, källornas påverkan samt identifiering av bolagsbildning och skatterådgivning. Uppgifterna ska kunna bära period, nämnare, källa och status. M3 ska pröva granskaren och det mänskliga sakgranskningsflödet mot fynden inom allmän riskbedömning före M5. Rutinernas fynd prövas när rutiner ingår i uppdraget. Utvidgad provtillsyn av hela paketet kvarstår i M7, enligt spec 16.3.

Materialets struktur och lokala kontrollsummor kan kontrolleras utan programimplementation:

```bash
python3 -I docs/research/verktyg/verifiera_tillsynsmaterial.py --underlag ../underlag/tillsyn-2026-10-09
```

Detta är en materialkontroll. Den poängsätter inte granskaren och godkänner inte facitet juridiskt.

## Filkarta

```
pyproject.toml                         paket, beroenden, pytest-inställningar
AGENTS.md, CLAUDE.md                   gemensamma regler för Codex och Claude Code
src/riskanalys/
  __init__.py                          versionsnummer
  fel.py                               RiskanalysFel, basklass för fel som visas för användaren
  cli.py                               kommandoraden, kopplar ihop underkommandon
  kommandon/                           ett underkommando per fil
    __init__.py                        gemensamma argument och regelbasinläsning
    regelbas_kommando.py               regelbas validera
    profil_kommando.py                 ny, bekrafta, profil
    drift_kommando.py                  utvardera
    bedom_kommando.py                  bedom
    skriv_kommando.py                  skriv
    granska_kommando.py                granska
    exportera_kommando.py              exportera --utkast
    sakgranska_kommando.py             sakgranska
    faststall_kommando.py              faststall, verifiera
  lagring/
    kontrollsumma.py                   SHA-256
    datamapp.py                        datamappen utanför repot
    manifest.py                        manifest och verifiering
    yamlfil.py                         läs och skriv YAML
    korningar.py                       tidsstämplade körningsmappar
  regelverk/
    villkor.py                         typat villkorsformat och utvärderare
    modeller.py                        pydantic-modeller för regelbasen
    laddning.py                        inläsning av YAML
    validering.py                      korsreferenser och villkor
    urval.py                           datumstyrt urval av krav och lydelser
  profil/
    modeller.py                        Byra, Uppgift, Profil
    hantering.py                       skapa, bekräfta, kritiska fält
    lagring.py                         läs och spara profil
  drift/
    historik.py                        versionshistorik och nästa genomgång
  bedomning/
    modeller.py                        bedömningsresultat
    motor.py                           deterministisk riskmotor
    korning.py                         körning med manifest
  dokument/
    modeller.py                        AI-schema, underlag, avsnitt, dokument
    leverantor.py                      gränssnitt och testleverantör
    underlag.py                        avsnittsunderlag ur tillåtelselistan
    validering.py                      maskinell validering av AI-utkast
    skrivning.py                       skrivning med omförsök
    claude.py                          Claude-leverantör
    arb.py                             sammanställning av allmän riskbedömning
    rendering.py                       Word-export
    export.py                          export av utkast ur den senaste granskningen
  granskning/
    modeller.py                        Fynd
    kontroller.py                      täckning, spårbarhet, bristmönster
    korning.py                         granskningskörning
  faststallelse/
    modeller.py                        Sakgranskning, Beslut
    sakgranskning.py                   registrering och giltighet
    grindar.py                         villkor för fastställelse
    faststall.py                       låsning och verifiering
regelbas/                              versionerad regelbas v0.1.0 (M1-omfattning)
  lydelsetexter/                       paragraftexten per lydelse, en .txt per lydelse-ID
tester/
  conftest.py                          gemensamma fixturer
  enhet/  regelkontrakt/  typfall/  live/
```

---

## M0 Grund

### Task 1: Projektgrund och arbetsregler

**Files:**
- Create: `pyproject.toml`
- Create: `src/riskanalys/__init__.py`
- Create: `src/riskanalys/fel.py`
- Create: `AGENTS.md`
- Create: `CLAUDE.md`
- Test: `tester/enhet/test_projekt.py`

**Interfaces:**
- Consumes: inget.
- Produces: paketet `riskanalys` med `__version__ = "0.1.0"`; `riskanalys.fel.RiskanalysFel(Exception)`.

- [ ] **Step 1: Skriv `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"

[project]
name = "riskanalys"
version = "0.1.0"
description = "Verksamhetsanpassad dokumentation enligt penningtvättsregelverket"
requires-python = ">=3.12"
dependencies = [
  "pydantic>=2.14,<3",
  "pyyaml>=6.0.3,<7",
  "python-docx>=1.2,<2",
  "anthropic>=1.12,<2",
]

[project.optional-dependencies]
dev = ["pytest>=9.1,<10", "httpx2>=2.13,<3"]

[project.scripts]
riskanalys = "riskanalys.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tester"]
addopts = "--import-mode=importlib -m 'not live'"
markers = [
  "live: anropar riktiga Claude-API:t, kostar pengar och körs bara med RISKANALYS_LIVE=1",
]
```

- [ ] **Step 2: Skriv det felande testet `tester/enhet/test_projekt.py`**

```python
import riskanalys
from riskanalys.fel import RiskanalysFel


def test_paketet_har_versionsnummer():
    assert riskanalys.__version__ == "0.1.0"


def test_riskanalysfel_ar_ett_vanligt_undantag():
    fel = RiskanalysFel("Något gick fel.")
    assert isinstance(fel, Exception)
    assert str(fel) == "Något gick fel."
```

- [ ] **Step 3: Skapa virtuell miljö och kör testet för att se att det fallerar**

Run:
```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest tester/enhet/test_projekt.py -v
```
Expected: installationen fallerar eller testet fallerar med `ModuleNotFoundError: No module named 'riskanalys'`, eftersom `src/riskanalys` saknas.

- [ ] **Step 4: Skriv `src/riskanalys/__init__.py`**

```python
"""Riskanalys – verksamhetsanpassad dokumentation enligt penningtvättsregelverket."""

__version__ = "0.1.0"
```

- [ ] **Step 5: Skriv `src/riskanalys/fel.py`**

```python
"""Gemensam basklass för fel som visas för användaren."""


class RiskanalysFel(Exception):
    """Ett fel som användaren kan åtgärda. Kommandoraden visar meddelandet utan stackspårning."""
```

- [ ] **Step 6: Skriv `AGENTS.md`**

````markdown
# Arbetsregler för Riskanalys

Gäller för alla som skriver kod i repot, både människor, Codex och Claude Code.

## Läs först

- Spec: `docs/superpowers/specs/2026-10-08-riskanalys-design.md`
- Aktuell plan: `docs/superpowers/plans/`
- Status och beslut: `docs/STATUS.md`

## Kommandon

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest                      # alla tester utom livetester
.venv/bin/riskanalys regelbas validera
```

## Regler som inte får brytas

1. **AI fattar inga beslut.** Risknivåer, poäng och regler kommer från regelbasen och riskmotorn. AI skriver bara text i ett låst schema.
2. **Inga personuppgifter till AI.** AI-underlag byggs bara ur tillåtelselistan i `regelbas/tillatelselistor.yaml`. Personer skrivs som `{roll:FfR}`.
3. **Byrådata aldrig i repot.** Den ligger i `$RISKANALYS_DATA`. Lägg aldrig in riktiga byråuppgifter i tester, bara syntetiska.
4. **Regelbasen ändras bara med källa.** Varje krav, katalogpost och regel har `kallor` eller `kalla` och en `grund`. Skalor, gränser och poäng märks `metodval`.
5. **Inga fria uttryck i regelbasen.** Villkor skrivs i det typade formatet (spec 6.3). Ingen `eval`.
6. **Tester före commit.** Kör `.venv/bin/pytest` och se att allt är grönt innan du committar. Skriv testet först.
7. **Inga anrop mot riktiga API:t i automatiska tester.** Använd `Testleverantor`. Livetester markeras `@pytest.mark.live`.
8. **Ändra aldrig sakkunnigstatus i repots regelbas** till `verifierad` utan en verklig sakkunnig granskning. Tester signerar en kopia.

## Stil

- Användartexter och dokumentation på svenska. Identifierare i koden på svenska utan å, ä och ö.
- Små filer med en uppgift var. En funktion gör en sak.
- Fel som användaren kan åtgärda ärver från `riskanalys.fel.RiskanalysFel` och har ett meddelande som säger vad som ska göras.
- Funktioner returnerar nya objekt i stället för att ändra befintliga.
- Commit: `<typ>: <beskrivning>` med typerna feat, fix, refactor, docs, test, chore.
````

- [ ] **Step 7: Skriv `CLAUDE.md`**

```markdown
# Claude Code

Samma regler som för Codex gäller. Läs och följ:

@AGENTS.md
```

- [ ] **Step 8: Installera och kör testet igen**

Run:
```bash
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest tester/enhet/test_projekt.py -v
```
Expected: 2 passed.

- [ ] **Step 9: Commit**

```bash
git add pyproject.toml src/riskanalys/__init__.py src/riskanalys/fel.py AGENTS.md CLAUDE.md tester/enhet/test_projekt.py
git commit -m "chore: projektgrund, arbetsregler för Codex och Claude Code"
```

---

### Task 2: Kontrollsummor och datamapp

**Files:**
- Create: `src/riskanalys/lagring/__init__.py`
- Create: `src/riskanalys/lagring/kontrollsumma.py`
- Create: `src/riskanalys/lagring/datamapp.py`
- Test: `tester/enhet/test_lagring_grund.py`

**Interfaces:**
- Consumes: `riskanalys.fel.RiskanalysFel`.
- Produces:
  - `kontrollsumma.for_bytes(data: bytes) -> str`, `for_text(text: str) -> str`, `for_fil(sokvag: Path) -> str`. Alla returnerar `"sha256:<hex>"`.
  - `datamapp.MILJOVARIABEL = "RISKANALYS_DATA"`, `datamapp.REPO_ROT: Path`, `datamapp.DatamappFel(RiskanalysFel)`.
  - `datamapp.datamapp() -> Path`, `byramapp(byra_id: str) -> Path`, `skapa_byramapp(byra_id: str) -> Path`, `befintlig_byramapp(byra_id: str) -> Path`.

- [ ] **Step 1: Skriv det felande testet `tester/enhet/test_lagring_grund.py`**

```python
import stat

import pytest

from riskanalys.lagring import datamapp as dm
from riskanalys.lagring.kontrollsumma import for_bytes, for_fil, for_text


def test_kontrollsumma_for_text_ar_stabil_och_markt():
    assert for_text("abc") == for_text("abc")
    assert for_text("abc").startswith("sha256:")
    assert for_text("abc") != for_text("abd")


def test_kontrollsumma_for_fil_motsvarar_innehallet(tmp_path):
    fil = tmp_path / "a.txt"
    fil.write_bytes(b"innehall")
    assert for_fil(fil) == for_bytes(b"innehall")


def test_datamapp_las_fran_miljovariabel(tmp_path, monkeypatch):
    monkeypatch.setenv(dm.MILJOVARIABEL, str(tmp_path / "data"))
    assert dm.datamapp() == (tmp_path / "data").resolve()


def test_datamapp_med_mellanslag_och_svenska_tecken_fungerar(tmp_path, monkeypatch):
    monkeypatch.setenv(dm.MILJOVARIABEL, str(tmp_path / "Mapp med å ä ö"))
    mapp = dm.skapa_byramapp("testbyra")
    assert mapp.is_dir()
    assert mapp.parent.name == "Mapp med å ä ö"


def test_datamapp_i_repot_vagras(monkeypatch):
    monkeypatch.setenv(dm.MILJOVARIABEL, str(dm.REPO_ROT / "data"))
    with pytest.raises(dm.DatamappFel, match="ligger i repot"):
        dm.datamapp()


@pytest.mark.parametrize("ogiltigt", ["", "../annan", "Byrå", "a b", "-borjar-med-streck", "x" * 64])
def test_ogiltigt_byra_id_vagras(tmp_path, monkeypatch, ogiltigt):
    monkeypatch.setenv(dm.MILJOVARIABEL, str(tmp_path))
    with pytest.raises(dm.DatamappFel, match="Ogiltigt byrå-ID"):
        dm.byramapp(ogiltigt)


def test_skapa_byramapp_ger_behorighet_bara_for_anvandaren(tmp_path, monkeypatch):
    monkeypatch.setenv(dm.MILJOVARIABEL, str(tmp_path / "data"))
    mapp = dm.skapa_byramapp("testbyra")
    assert stat.S_IMODE(mapp.stat().st_mode) == 0o700


def test_skapa_byramapp_tva_ganger_vagras(tmp_path, monkeypatch):
    monkeypatch.setenv(dm.MILJOVARIABEL, str(tmp_path))
    dm.skapa_byramapp("testbyra")
    with pytest.raises(dm.DatamappFel, match="finns redan"):
        dm.skapa_byramapp("testbyra")


def test_befintlig_byramapp_kraver_att_byran_finns(tmp_path, monkeypatch):
    monkeypatch.setenv(dm.MILJOVARIABEL, str(tmp_path))
    with pytest.raises(dm.DatamappFel, match="finns inte"):
        dm.befintlig_byramapp("saknas")
```

- [ ] **Step 2: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/enhet/test_lagring_grund.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.lagring'`.

- [ ] **Step 3: Skriv `src/riskanalys/lagring/__init__.py`**

```python
"""Lagring av byrådata, manifest och kontrollsummor."""
```

- [ ] **Step 4: Skriv `src/riskanalys/lagring/kontrollsumma.py`**

```python
"""SHA-256-kontrollsummor för filer och text."""

import hashlib
from pathlib import Path

_BLOCKSTORLEK = 65536


def for_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def for_text(text: str) -> str:
    return for_bytes(text.encode("utf-8"))


def for_fil(sokvag: Path) -> str:
    summa = hashlib.sha256()
    with sokvag.open("rb") as fil:
        for block in iter(lambda: fil.read(_BLOCKSTORLEK), b""):
            summa.update(block)
    return "sha256:" + summa.hexdigest()
```

- [ ] **Step 5: Skriv `src/riskanalys/lagring/datamapp.py`**

```python
"""Datamappen där byråernas uppgifter lagras. Den får aldrig ligga i repot (spec 5.2)."""

import os
import re
from pathlib import Path

from riskanalys.fel import RiskanalysFel

MILJOVARIABEL = "RISKANALYS_DATA"
STANDARDMAPP = Path("~/RiskanalysData")
REPO_ROT = Path(__file__).resolve().parents[3]
_BYRA_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")


class DatamappFel(RiskanalysFel):
    """Datamappen eller byrå-ID:t är ogiltigt."""


def datamapp() -> Path:
    """Returnerar datamappen. Vägrar om den ligger i repot."""
    mapp = Path(os.environ.get(MILJOVARIABEL, STANDARDMAPP)).expanduser().resolve()
    if mapp.is_relative_to(REPO_ROT):
        raise DatamappFel(
            f"Datamappen {mapp} ligger i repot. Byrådata får aldrig lagras i repot. "
            f"Sätt {MILJOVARIABEL} till en mapp utanför {REPO_ROT}."
        )
    return mapp


def byramapp(byra_id: str) -> Path:
    """Returnerar mappen för en byrå utan att skapa den."""
    if not _BYRA_ID.match(byra_id):
        raise DatamappFel(
            f"Ogiltigt byrå-ID {byra_id!r}. Använd a–z, 0–9 och bindestreck, "
            "börja med bokstav eller siffra och använd högst 63 tecken."
        )
    return datamapp() / byra_id


def skapa_byramapp(byra_id: str) -> Path:
    """Skapar byråns mapp med behörighet bara för användaren."""
    mapp = byramapp(byra_id)
    if mapp.exists():
        raise DatamappFel(f"Byrån {byra_id} finns redan i {mapp}.")
    mapp.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    mapp.mkdir(mode=0o700)
    return mapp


def befintlig_byramapp(byra_id: str) -> Path:
    """Returnerar mappen för en byrå som måste finnas."""
    mapp = byramapp(byra_id)
    if not mapp.is_dir():
        raise DatamappFel(f"Byrån {byra_id} finns inte i {datamapp()}. Skapa den med 'riskanalys ny'.")
    return mapp
```

- [ ] **Step 6: Kör testet**

Run: `.venv/bin/pytest tester/enhet/test_lagring_grund.py -v`
Expected: alla tester passerar.

- [ ] **Step 7: Commit**

```bash
git add src/riskanalys/lagring tester/enhet/test_lagring_grund.py
git commit -m "feat: kontrollsummor och datamapp utanför repot"
```

---

### Task 3: Manifest

**Files:**
- Create: `src/riskanalys/lagring/manifest.py`
- Test: `tester/enhet/test_manifest.py`

**Interfaces:**
- Consumes: `kontrollsumma.for_fil`, `riskanalys.__version__`, `RiskanalysFel`.
- Produces:
  - `MANIFESTNAMN = "manifest.json"`.
  - `Manifest(skapad: datetime, programversion: str, git_commit: str, metadata: dict[str, str], filer: dict[str, str])`.
  - `skriv_manifest(mapp: Path, metadata: dict[str, str]) -> Manifest`: tar med alla filer i mappen och undermapparna utom toppmappens egen `manifest.json`.
  - `ManifestFel(RiskanalysFel)`, `skadat_manifest(mapp: Path) -> str`.
  - `las_manifest(mapp: Path) -> Manifest`: kastar `ManifestFel` med instruktion om återställning om manifestet inte går att läsa.
  - `verifiera_manifest(mapp: Path) -> list[str]`: tom lista om allt stämmer, annars meddelanden som börjar med "Fil saknas:", "Fil ändrad:" eller "Fil finns inte i manifestet:", eller ett enda meddelande om att manifestet saknas eller är skadat. Funktionen kraschar aldrig på ett skadat manifest.

- [ ] **Step 1: Skriv det felande testet `tester/enhet/test_manifest.py`**

```python
import pytest

from riskanalys.lagring.manifest import MANIFESTNAMN, ManifestFel, las_manifest, skriv_manifest, verifiera_manifest


def _paket(mapp):
    (mapp / "a.txt").write_text("a", encoding="utf-8")
    (mapp / "under").mkdir()
    (mapp / "under" / "b.txt").write_text("b", encoding="utf-8")
    (mapp / "under" / MANIFESTNAMN).write_text("{}", encoding="utf-8")


def test_manifest_tar_med_alla_filer_utom_sitt_eget(tmp_path):
    _paket(tmp_path)
    manifest = skriv_manifest(tmp_path, {"typ": "test"})
    assert set(manifest.filer) == {"a.txt", "under/b.txt", f"under/{MANIFESTNAMN}"}
    assert las_manifest(tmp_path).metadata == {"typ": "test"}


def test_oforandrat_paket_verifieras(tmp_path):
    _paket(tmp_path)
    skriv_manifest(tmp_path, {})
    assert verifiera_manifest(tmp_path) == []


def test_andrad_fil_upptacks(tmp_path):
    _paket(tmp_path)
    skriv_manifest(tmp_path, {})
    (tmp_path / "a.txt").write_text("ändrad", encoding="utf-8")
    assert verifiera_manifest(tmp_path) == ["Fil ändrad: a.txt"]


def test_borttagen_fil_upptacks(tmp_path):
    _paket(tmp_path)
    skriv_manifest(tmp_path, {})
    (tmp_path / "under" / "b.txt").unlink()
    assert verifiera_manifest(tmp_path) == ["Fil saknas: under/b.txt"]


def test_tillagd_fil_upptacks(tmp_path):
    _paket(tmp_path)
    skriv_manifest(tmp_path, {})
    (tmp_path / "ny.txt").write_text("x", encoding="utf-8")
    assert verifiera_manifest(tmp_path) == ["Fil finns inte i manifestet: ny.txt"]


def test_saknat_manifest_rapporteras(tmp_path):
    assert verifiera_manifest(tmp_path) == [f"Manifest saknas i {tmp_path}."]


def test_manifest_innehaller_programversion_och_commit(tmp_path):
    manifest = skriv_manifest(tmp_path, {})
    assert manifest.programversion == "0.1.0"
    assert manifest.git_commit


@pytest.mark.parametrize("innehall", ["{inte json", "{}", '{"skapad": "igår"}'])
def test_skadat_manifest_rapporteras_utan_krasch(tmp_path, innehall):
    _paket(tmp_path)
    skriv_manifest(tmp_path, {})
    (tmp_path / MANIFESTNAMN).write_text(innehall, encoding="utf-8")
    assert verifiera_manifest(tmp_path) == [f"Manifestet i {tmp_path} är skadat och kan inte läsas."]
    with pytest.raises(ManifestFel, match="Återställ mappen från säkerhetskopian"):
        las_manifest(tmp_path)


def test_manifest_med_fel_kodning_rapporteras_utan_krasch(tmp_path):
    skriv_manifest(tmp_path, {})
    (tmp_path / MANIFESTNAMN).write_bytes(b"\xff\xfe\x00")
    assert verifiera_manifest(tmp_path) == [f"Manifestet i {tmp_path} är skadat och kan inte läsas."]
```

- [ ] **Step 2: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/enhet/test_manifest.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.lagring.manifest'`.

- [ ] **Step 3: Skriv `src/riskanalys/lagring/manifest.py`**

```python
"""Manifest med kontrollsummor för alla filer i en mapp (spec 5.3).

Kontrollsummorna visar att sparade filer är oförändrade. De återskapar inga förlorade filer.
"""

import subprocess
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ConfigDict, ValidationError

from riskanalys import __version__
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.kontrollsumma import for_fil

MANIFESTNAMN = "manifest.json"


class ManifestFel(RiskanalysFel):
    """Manifestet finns men kan inte läsas: trasig JSON, fel kodning eller saknade fält."""


class Manifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skapad: datetime
    programversion: str
    git_commit: str
    metadata: dict[str, str]
    filer: dict[str, str]


def _git_commit() -> str:
    try:
        resultat = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent,
        )
    except (OSError, subprocess.CalledProcessError):
        return "okänd"
    return resultat.stdout.strip()


def _filer(mapp: Path) -> dict[str, str]:
    eget_manifest = mapp / MANIFESTNAMN
    return {
        sokvag.relative_to(mapp).as_posix(): for_fil(sokvag)
        for sokvag in sorted(mapp.rglob("*"))
        if sokvag.is_file() and sokvag != eget_manifest
    }


def skriv_manifest(mapp: Path, metadata: dict[str, str]) -> Manifest:
    """Skriver manifest.json med kontrollsumma för varje fil i mappen och dess undermappar."""
    manifest = Manifest(
        skapad=datetime.now(timezone.utc),
        programversion=__version__,
        git_commit=_git_commit(),
        metadata=metadata,
        filer=_filer(mapp),
    )
    (mapp / MANIFESTNAMN).write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    return manifest


def skadat_manifest(mapp: Path) -> str:
    return f"Manifestet i {mapp} är skadat och kan inte läsas."


def las_manifest(mapp: Path) -> Manifest:
    """Läser manifestet. Ett manifest som inte går att läsa ger ManifestFel med instruktion om återställning."""
    try:
        return Manifest.model_validate_json((mapp / MANIFESTNAMN).read_text(encoding="utf-8"))
    except (ValidationError, UnicodeDecodeError) as fel:
        raise ManifestFel(
            f"{skadat_manifest(mapp)} Återställ mappen från säkerhetskopian och försök igen."
        ) from fel


def verifiera_manifest(mapp: Path) -> list[str]:
    """Jämför filerna med manifestet. Tom lista betyder att allt stämmer.

    Ett saknat eller skadat manifest rapporteras som en avvikelse, aldrig som en krasch.
    """
    if not (mapp / MANIFESTNAMN).is_file():
        return [f"Manifest saknas i {mapp}."]
    try:
        manifest = las_manifest(mapp)
    except ManifestFel:
        return [skadat_manifest(mapp)]
    nuvarande = _filer(mapp)
    fel = []
    for namn, summa in manifest.filer.items():
        if namn not in nuvarande:
            fel.append(f"Fil saknas: {namn}")
        elif nuvarande[namn] != summa:
            fel.append(f"Fil ändrad: {namn}")
    for namn in sorted(nuvarande.keys() - manifest.filer.keys()):
        fel.append(f"Fil finns inte i manifestet: {namn}")
    return fel
```

- [ ] **Step 4: Kör testet**

Run: `.venv/bin/pytest tester/enhet/test_manifest.py -v`
Expected: 11 passed.

- [ ] **Step 5: Commit**

```bash
git add src/riskanalys/lagring/manifest.py tester/enhet/test_manifest.py
git commit -m "feat: manifest med kontrollsummor och verifiering"
```

---

### Task 4: Villkorsformat och utvärderare

**Files:**
- Create: `src/riskanalys/regelverk/__init__.py`
- Create: `src/riskanalys/regelverk/villkor.py`
- Test: `tester/regelkontrakt/test_villkor.py`

**Interfaces:**
- Consumes: `riskanalys.fel.RiskanalysFel`.
- Produces:
  - `Sanning` (enum: `SANT`, `FALSKT`, `OKANT`), `Kunskap` (enum: `KAND`, `OKAND`, `EJ_TILLAMPLIG`).
  - `Faltvarde(kunskap: Kunskap, varde: Any = None)`, `Faltdef(id: str, typ: str, val: tuple[str, ...] = ())`.
  - Villkorsträd: `Jamforelse(falt, op, varde=None)`, `Alla(delar)`, `Nagon(delar)`, `Inte(inre)`; typalias `Villkor`.
  - `Utfall(sanning: Sanning, okanda: frozenset[str] = frozenset())`.
  - `VillkorsFel(RiskanalysFel)`.
  - `kontrollera_varde(definition: Faltdef, varde: Any) -> None`
  - `tolka_villkor(data: Any, falt: dict[str, Faltdef]) -> Villkor`
  - `utvardera(villkor: Villkor, varden: dict[str, Faltvarde]) -> Utfall`
  - `falt_i(villkor: Villkor) -> frozenset[str]`

- [ ] **Step 1: Skriv det felande testet `tester/regelkontrakt/test_villkor.py`**

```python
from datetime import date

import pytest

from riskanalys.regelverk.villkor import (
    Alla,
    Faltdef,
    Faltvarde,
    Inte,
    Jamforelse,
    Kunskap,
    Nagon,
    Sanning,
    VillkorsFel,
    falt_i,
    kontrollera_varde,
    tolka_villkor,
    utvardera,
)

FALT = {
    "P-B": Faltdef("P-B", "bool"),
    "P-H": Faltdef("P-H", "heltal"),
    "P-T": Faltdef("P-T", "tal"),
    "P-A": Faltdef("P-A", "andel"),
    "P-X": Faltdef("P-X", "text"),
    "P-V": Faltdef("P-V", "val", ("finns", "saknas")),
    "P-D": Faltdef("P-D", "datum"),
}
S, F, O = Sanning.SANT, Sanning.FALSKT, Sanning.OKANT


def kand(varde):
    return Faltvarde(Kunskap.KAND, varde)


def test_tolkar_jamforelse():
    assert tolka_villkor({"falt": "P-A", "op": ">=", "varde": 0.2}, FALT) == Jamforelse("P-A", ">=", 0.2)


def test_tolkar_kombinatorer():
    data = {
        "alla": [
            {"falt": "P-B", "op": "==", "varde": True},
            {"nagon": [{"inte": {"falt": "P-X", "op": "finns"}}]},
        ]
    }
    vantat = Alla((Jamforelse("P-B", "==", True), Nagon((Inte(Jamforelse("P-X", "finns")),))))
    assert tolka_villkor(data, FALT) == vantat


@pytest.mark.parametrize(
    ("data", "meddelande"),
    [
        ({"falt": "P-OKANT", "op": "==", "varde": 1}, "Okänt fält"),
        ({"falt": "P-H", "op": "~=", "varde": 1}, "Okänd operator"),
        ({"falt": "P-H", "op": "finns", "varde": 1}, "tar inget värde"),
        ({"falt": "P-H", "op": "=="}, "kräver ett värde"),
        ({"falt": "P-B", "op": "<", "varde": True}, "kan inte användas"),
        ({"falt": "P-X", "op": ">", "varde": "a"}, "kan inte användas"),
        ({"falt": "P-H", "op": "i", "varde": []}, "kräver en lista"),
        ({"falt": "P-H", "op": "i", "varde": 3}, "kräver en lista"),
        ({"falt": "P-A", "op": "==", "varde": 1.5}, "passar inte typen andel"),
        ({"falt": "P-H", "op": "==", "varde": True}, "passar inte typen heltal"),
        ({"falt": "P-V", "op": "==", "varde": "kanske"}, "passar inte typen val"),
        ({"falt": "P-D", "op": "<", "varde": "2026-01-01"}, "passar inte typen datum"),
        ({"alla": {"falt": "P-B", "op": "finns"}}, "måste innehålla en lista"),
        ({"falt": "P-B", "op": "finns", "extra": 1}, "Okänd villkorsform"),
        ({}, "måste vara en mappning"),
        ("P-B == true", "måste vara en mappning"),
    ],
)
def test_felaktiga_villkor_vagras(data, meddelande):
    with pytest.raises(VillkorsFel, match=meddelande):
        tolka_villkor(data, FALT)


@pytest.mark.parametrize(
    ("op", "varde", "falt_varde", "vantat"),
    [
        ("==", 3, 3, S), ("==", 3, 4, F),
        ("!=", 3, 4, S), ("!=", 3, 3, F),
        ("<", 3, 2, S), ("<", 3, 3, F),
        ("<=", 3, 3, S), ("<=", 3, 4, F),
        (">", 3, 4, S), (">", 3, 3, F),
        (">=", 3, 3, S), (">=", 3, 2, F),
    ],
)
def test_jamforande_operatorer_pa_heltal(op, varde, falt_varde, vantat):
    villkor = tolka_villkor({"falt": "P-H", "op": op, "varde": varde}, FALT)
    assert utvardera(villkor, {"P-H": kand(falt_varde)}).sanning is vantat


def test_andel_gransfall():
    villkor = tolka_villkor({"falt": "P-A", "op": ">=", "varde": 0.2}, FALT)
    assert utvardera(villkor, {"P-A": kand(0.2)}).sanning is S
    assert utvardera(villkor, {"P-A": kand(0.19)}).sanning is F


def test_datum_jamfors_pa_bada_sidor_om_gransen():
    villkor = tolka_villkor({"falt": "P-D", "op": "<", "varde": date(2026, 11, 20)}, FALT)
    assert utvardera(villkor, {"P-D": kand(date(2026, 11, 19))}).sanning is S
    assert utvardera(villkor, {"P-D": kand(date(2026, 11, 20))}).sanning is F


def test_operatorn_i():
    villkor = tolka_villkor({"falt": "P-V", "op": "i", "varde": ["finns"]}, FALT)
    assert utvardera(villkor, {"P-V": kand("finns")}).sanning is S
    assert utvardera(villkor, {"P-V": kand("saknas")}).sanning is F


def test_finns_och_saknas():
    finns = tolka_villkor({"falt": "P-X", "op": "finns"}, FALT)
    saknas = tolka_villkor({"falt": "P-X", "op": "saknas"}, FALT)
    assert utvardera(finns, {"P-X": kand("text")}).sanning is S
    assert utvardera(saknas, {"P-X": kand(None)}).sanning is S
    assert utvardera(finns, {"P-X": kand(None)}).sanning is F


def test_okant_falt_ger_okant_och_listas():
    villkor = tolka_villkor({"falt": "P-A", "op": ">=", "varde": 0.2}, FALT)
    utfall = utvardera(villkor, {})
    assert utfall.sanning is O
    assert utfall.okanda == frozenset({"P-A"})


def test_ej_tillampligt_falt():
    jamforelse = tolka_villkor({"falt": "P-A", "op": ">=", "varde": 0.2}, FALT)
    saknas = tolka_villkor({"falt": "P-A", "op": "saknas"}, FALT)
    varden = {"P-A": Faltvarde(Kunskap.EJ_TILLAMPLIG)}
    assert utvardera(jamforelse, varden).sanning is F
    assert utvardera(saknas, varden).sanning is S


def test_kant_tomt_varde_ger_falskt_vid_jamforelse():
    villkor = tolka_villkor({"falt": "P-H", "op": ">", "varde": 1}, FALT)
    assert utvardera(villkor, {"P-H": kand(None)}).sanning is F


def _konstant(sanning):
    """Ett villkor som ger angivet sanningsvärde med VARDEN nedan."""
    return {
        S: Jamforelse("P-B", "==", True),
        F: Jamforelse("P-B", "==", False),
        O: Jamforelse("P-OKAND", "==", True),
    }[sanning]


VARDEN = {"P-B": kand(True)}


@pytest.mark.parametrize(
    ("a", "b", "vantat"),
    [(S, S, S), (S, F, F), (S, O, O), (F, S, F), (F, F, F), (F, O, F), (O, S, O), (O, F, F), (O, O, O)],
)
def test_alla_sanningstabell(a, b, vantat):
    assert utvardera(Alla((_konstant(a), _konstant(b))), VARDEN).sanning is vantat


@pytest.mark.parametrize(
    ("a", "b", "vantat"),
    [(S, S, S), (S, F, S), (S, O, S), (F, S, S), (F, F, F), (F, O, O), (O, S, S), (O, F, O), (O, O, O)],
)
def test_nagon_sanningstabell(a, b, vantat):
    assert utvardera(Nagon((_konstant(a), _konstant(b))), VARDEN).sanning is vantat


@pytest.mark.parametrize(("inre", "vantat"), [(S, F), (F, S), (O, O)])
def test_inte_sanningstabell(inre, vantat):
    assert utvardera(Inte(_konstant(inre)), VARDEN).sanning is vantat


def test_tomma_kombinatorer():
    assert utvardera(Alla(()), {}).sanning is S
    assert utvardera(Nagon(()), {}).sanning is F


def test_okanda_samlas_fran_alla_delar():
    villkor = Nagon((_konstant(O), Jamforelse("P-ANNAN", "finns")))
    assert utvardera(villkor, VARDEN).okanda == frozenset({"P-OKAND", "P-ANNAN"})


def test_falt_i_listar_alla_falt_i_tradet():
    villkor = Alla((Jamforelse("P-A", ">=", 0.2), Nagon((Inte(Jamforelse("P-B", "finns")),))))
    assert falt_i(villkor) == frozenset({"P-A", "P-B"})


@pytest.mark.parametrize(
    ("definition", "varde"),
    [
        (Faltdef("x", "bool"), True),
        (Faltdef("x", "heltal"), 3),
        (Faltdef("x", "tal"), 2.5),
        (Faltdef("x", "andel"), 0),
        (Faltdef("x", "andel"), 1),
        (Faltdef("x", "text"), "a"),
        (Faltdef("x", "val", ("a",)), "a"),
        (Faltdef("x", "datum"), date(2026, 1, 1)),
    ],
)
def test_giltiga_varden_godtas(definition, varde):
    kontrollera_varde(definition, varde)


def test_okand_typ_vagras():
    with pytest.raises(VillkorsFel, match="Okänd typ"):
        kontrollera_varde(Faltdef("x", "lista"), [])
```

- [ ] **Step 2: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/regelkontrakt/test_villkor.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.regelverk'`.

- [ ] **Step 3: Skriv `src/riskanalys/regelverk/__init__.py`**

```python
"""Regelbasen: källor, krav, kataloger, villkor och urval."""
```

- [ ] **Step 4: Skriv `src/riskanalys/regelverk/villkor.py`**

```python
"""Typat villkorsformat för regelbasen (spec 6.3).

Formatet är medvetet litet: kombinatorerna alla, nagon och inte samt jämförelser
mellan ett registrerat fält och ett värde. Inga fria uttryck och ingen eval.
Utvärderingen har tre sanningsvärden: sant, falskt och okänt.
"""

from __future__ import annotations

import operator
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any

from riskanalys.fel import RiskanalysFel

ORDNADE_TYPER = frozenset({"heltal", "tal", "andel", "datum"})
OPERATORER = frozenset({"==", "!=", "<", "<=", ">", ">=", "i", "finns", "saknas"})
ORDNINGSOPERATORER = frozenset({"<", "<=", ">", ">="})
UTAN_VARDE = frozenset({"finns", "saknas"})
_JAMFOR = {
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}


class VillkorsFel(RiskanalysFel):
    """Ett villkor eller ett värde i regelbasen är felaktigt."""


class Sanning(Enum):
    SANT = "sant"
    FALSKT = "falskt"
    OKANT = "okänt"


class Kunskap(Enum):
    KAND = "känd"
    OKAND = "okänd"
    EJ_TILLAMPLIG = "ej_tillämplig"


@dataclass(frozen=True)
class Faltvarde:
    kunskap: Kunskap
    varde: Any = None


@dataclass(frozen=True)
class Faltdef:
    id: str
    typ: str
    val: tuple[str, ...] = ()


@dataclass(frozen=True)
class Jamforelse:
    falt: str
    op: str
    varde: Any = None


@dataclass(frozen=True)
class Alla:
    delar: tuple[Villkor, ...]


@dataclass(frozen=True)
class Nagon:
    delar: tuple[Villkor, ...]


@dataclass(frozen=True)
class Inte:
    inre: Villkor


Villkor = Jamforelse | Alla | Nagon | Inte


@dataclass(frozen=True)
class Utfall:
    sanning: Sanning
    okanda: frozenset[str] = frozenset()


def kontrollera_varde(definition: Faltdef, varde: Any) -> None:
    """Kontrollerar att ett värde passar fältets typ."""
    typ = definition.typ
    ar_tal = isinstance(varde, (int, float)) and not isinstance(varde, bool)
    if typ == "bool":
        ok = isinstance(varde, bool)
    elif typ == "heltal":
        ok = isinstance(varde, int) and not isinstance(varde, bool)
    elif typ == "tal":
        ok = ar_tal
    elif typ == "andel":
        ok = ar_tal and 0 <= varde <= 1
    elif typ == "text":
        ok = isinstance(varde, str)
    elif typ == "val":
        ok = isinstance(varde, str) and varde in definition.val
    elif typ == "datum":
        ok = isinstance(varde, date)
    else:
        raise VillkorsFel(f"Okänd typ {typ!r} för fältet {definition.id}.")
    if not ok:
        raise VillkorsFel(f"Värdet {varde!r} passar inte typen {typ} för fältet {definition.id}.")


def tolka_villkor(data: Any, falt: dict[str, Faltdef]) -> Villkor:
    """Tolkar ett villkor från YAML-data och kontrollerar fält, operatorer och typer."""
    if not isinstance(data, dict) or not data:
        raise VillkorsFel(f"Ett villkor måste vara en mappning, fick {data!r}.")
    nycklar = set(data)
    if nycklar in ({"alla"}, {"nagon"}):
        (nyckel,) = nycklar
        delar = data[nyckel]
        if not isinstance(delar, list):
            raise VillkorsFel(f"'{nyckel}' måste innehålla en lista.")
        tolkade = tuple(tolka_villkor(del_, falt) for del_ in delar)
        return Alla(tolkade) if nyckel == "alla" else Nagon(tolkade)
    if nycklar == {"inte"}:
        return Inte(tolka_villkor(data["inte"], falt))
    if {"falt", "op"} <= nycklar <= {"falt", "op", "varde"}:
        return _tolka_jamforelse(data, falt)
    raise VillkorsFel(f"Okänd villkorsform med nycklarna {sorted(nycklar)}.")


def _tolka_jamforelse(data: dict[str, Any], falt: dict[str, Faltdef]) -> Jamforelse:
    falt_id, op = data["falt"], data["op"]
    if falt_id not in falt:
        raise VillkorsFel(f"Okänt fält {falt_id!r}. Fältet måste finnas i fältregistret.")
    if op not in OPERATORER:
        raise VillkorsFel(f"Okänd operator {op!r} för fältet {falt_id}.")
    definition = falt[falt_id]
    if op in UTAN_VARDE:
        if "varde" in data:
            raise VillkorsFel(f"Operatorn {op} tar inget värde ({falt_id}).")
        return Jamforelse(falt_id, op)
    if "varde" not in data:
        raise VillkorsFel(f"Operatorn {op} kräver ett värde ({falt_id}).")
    if op in ORDNINGSOPERATORER and definition.typ not in ORDNADE_TYPER:
        raise VillkorsFel(f"Operatorn {op} kan inte användas på typen {definition.typ} ({falt_id}).")
    varde = data["varde"]
    if op == "i":
        if not isinstance(varde, list) or not varde:
            raise VillkorsFel(f"Operatorn i kräver en lista med minst ett värde ({falt_id}).")
        for del_ in varde:
            kontrollera_varde(definition, del_)
        return Jamforelse(falt_id, op, tuple(varde))
    kontrollera_varde(definition, varde)
    return Jamforelse(falt_id, op, varde)


def utvardera(villkor: Villkor, varden: dict[str, Faltvarde]) -> Utfall:
    """Utvärderar ett villkor med tre sanningsvärden."""
    if isinstance(villkor, Jamforelse):
        return _utvardera_jamforelse(villkor, varden)
    if isinstance(villkor, Inte):
        inre = utvardera(villkor.inre, varden)
        return Utfall(_inte(inre.sanning), inre.okanda)
    if isinstance(villkor, (Alla, Nagon)):
        utfall = [utvardera(del_, varden) for del_ in villkor.delar]
        sanningar = [u.sanning for u in utfall]
        okanda = frozenset().union(*(u.okanda for u in utfall))
        sanning = _alla(sanningar) if isinstance(villkor, Alla) else _nagon(sanningar)
        return Utfall(sanning, okanda)
    raise VillkorsFel(f"Okänt villkor {villkor!r}.")


def falt_i(villkor: Villkor) -> frozenset[str]:
    """Alla fält som ett villkor bygger på."""
    if isinstance(villkor, Jamforelse):
        return frozenset({villkor.falt})
    if isinstance(villkor, Inte):
        return falt_i(villkor.inre)
    return frozenset().union(*(falt_i(del_) for del_ in villkor.delar))


def _inte(sanning: Sanning) -> Sanning:
    return {Sanning.SANT: Sanning.FALSKT, Sanning.FALSKT: Sanning.SANT}.get(sanning, Sanning.OKANT)


def _alla(sanningar: list[Sanning]) -> Sanning:
    if Sanning.FALSKT in sanningar:
        return Sanning.FALSKT
    if Sanning.OKANT in sanningar:
        return Sanning.OKANT
    return Sanning.SANT


def _nagon(sanningar: list[Sanning]) -> Sanning:
    if Sanning.SANT in sanningar:
        return Sanning.SANT
    if Sanning.OKANT in sanningar:
        return Sanning.OKANT
    return Sanning.FALSKT


def _sanning(uppfyllt: bool) -> Sanning:
    return Sanning.SANT if uppfyllt else Sanning.FALSKT


def _utvardera_jamforelse(jamforelse: Jamforelse, varden: dict[str, Faltvarde]) -> Utfall:
    faltvarde = varden.get(jamforelse.falt, Faltvarde(Kunskap.OKAND))
    if faltvarde.kunskap is Kunskap.OKAND:
        return Utfall(Sanning.OKANT, frozenset({jamforelse.falt}))
    if faltvarde.kunskap is Kunskap.EJ_TILLAMPLIG:
        return Utfall(_sanning(jamforelse.op == "saknas"))
    varde = faltvarde.varde
    if jamforelse.op == "finns":
        return Utfall(_sanning(varde is not None))
    if jamforelse.op == "saknas":
        return Utfall(_sanning(varde is None))
    if varde is None:
        return Utfall(Sanning.FALSKT)
    if jamforelse.op == "i":
        return Utfall(_sanning(varde in jamforelse.varde))
    return Utfall(_sanning(_JAMFOR[jamforelse.op](varde, jamforelse.varde)))
```

- [ ] **Step 5: Kör testet**

Run: `.venv/bin/pytest tester/regelkontrakt/test_villkor.py -v`
Expected: alla tester passerar.

- [ ] **Step 6: Commit**

```bash
git add src/riskanalys/regelverk tester/regelkontrakt/test_villkor.py
git commit -m "feat: typat villkorsformat med tre sanningsvärden"
```

---
### Task 5: Regelbasmodeller och inläsning

**Files:**
- Create: `src/riskanalys/regelverk/modeller.py`
- Create: `src/riskanalys/regelverk/laddning.py`
- Create: `tester/conftest.py`
- Test: `tester/enhet/test_laddning.py`

**Interfaces:**
- Consumes: `villkor.Faltdef`, `kontrollsumma.for_fil`, `kontrollsumma.for_text`, `RiskanalysFel`.
- Produces:
  - Modeller i `regelverk/modeller.py`: `Falt`, `Kalla` (med `paragrafer`), `Lydelse` (med `text_kontrollsumma`), `Sakkunnig` (med `kontrollsumma` och `galler(innehallssumma) -> bool`), `Krav` (med `galler_om` och `belagg`), `Kartrad` (med `hanterad`), `Kartomfattning`, `Paragrafkarta` (med `galler(datum) -> bool` och `ohanterade()`), `Hot`, `Effekt`, `Sarbarhet`, `Kontroll`, `Tjanst`, `Bristmonster`, `MatrisRad`, `Regel`, `Metod` (med `regler()`), `Tillatelselista`, `Regelpaket`, `Regelbas`. Typalias `Grund`, `Sannolikhet`, `Konsekvens`, `Risk`, `Allvar`, `Belagg`.
  - `Regelbas.faltdefinitioner() -> dict[str, Faltdef]`, `Regelbas.alla_id() -> set[str]`, `Regelbas.kravets_innehallssumma(krav_id) -> str` och `Regelbas.kartans_innehallssumma(paket_id) -> str`. `KALLANS_GILTIGHET` anger vilka uppgifter om en källa som ingår i summorna.
  - `laddning.STANDARD_REGELBAS: Path`, `laddning.LYDELSETEXTER = "lydelsetexter"`, `laddning.RegelbasFel(RiskanalysFel)` med attributet `fel: list[str]`.
  - `laddning.ladda_regelbas(rot: Path = STANDARD_REGELBAS) -> Regelbas`, `regelbasens_kontrollsumma(rot: Path) -> str`, `regelbasfiler(rot: Path) -> list[Path]` (YAML-filer och lydelsetexter), `lydelsetextens_kontrollsumma(text: str) -> str`.
  - Fixturer i `tester/conftest.py`: `minimal_filer`, `skriv_minimal_regelbas`, `minimal_rot`, `minimal_regelbas`. Testerna når lydelsetexten och dess summa genom `minimal_filer`, inte genom att importera `conftest`.

Specen visar `lydelse` i ental på kravet. Planen använder `lydelser` (lista), så att ett krav kan följa sin paragraf genom flera lydelser över tid (spec 6.4). Specen är uppdaterad i samma riktning.

Lydelsens `text_kontrollsumma` beräknas på paragraftexten efter att alla blanktecken slagits ihop till ett mellanslag. Då påverkar radbrytningar och avstavning i källan inte summan, men varje ändrat ord gör det. Texten ligger i `regelbas/lydelsetexter/<lydelse-ID>.txt`, så att en sakkunnig kan läsa den och summan kan kontrolleras. Svenska författningar är inte skyddade av upphovsrätt (1 kap. 9 § upphovsrättslagen).

`galler_om` är ett villkor i formatet i spec 6.3. Ett krav som gäller alla verksamhetsutövare har `galler_om: {alla: []}`. `belagg` anger vilka slags belägg som visar att kravet är uppfyllt: `dokument`, `datum`, `logg`, `beslut` eller `register`.

Varje regelpaket har en **paragrafkarta** (spec 16.1). Den anger för ett datumintervall vilka kapitel i vilka källor den täcker (`omfattning`) och har en rad per paragraf. Raden anger de krav paragrafen ger upphov till, eller varför den inte gäller sektorn (`ej_tillamplig` med motivering). En rad utan något av dem är en paragraf som regelbasen ännu inte hanterar. Källans paragrafindelning står i källans `paragrafer`, så att valideringen (Task 6) kan kontrollera att kartan är fullständig.

En sakkunnigs status `verifierad` gäller bara det innehåll som granskades. Därför har `Sakkunnig` en `kontrollsumma`, som ska vara lika med `Regelbas.kravets_innehallssumma` eller `Regelbas.kartans_innehallssumma`. Summorna omfattar också det som kravet och kartan hänvisar till, eftersom ett godkännande av ett krav är ett godkännande av hur det läser paragrafen:

- **Krav:** kravet utan sakkunnigstatus, varje refererad lydelse (lagrum, ikraft, upphor, införd genom, primärkälla och textkontrollsumma), källans giltighetsuppgifter (typ, utgivare, geografi, beslutsdatum, konsolidering och dokumentets kontrollsumma) och definitionerna av fälten i `galler_om`.
- **Paragrafkarta:** kartan utan sakkunnigstatus, paketets län och krav, källornas paragrafindelning och giltighetsuppgifter samt alla lydelser i de källor kartan omfattar.

Ändras en paragraftext, ett giltighetsdatum eller en källas geografi slutar alltså godkännandet att gälla, även om kravet självt är oförändrat. Hämtningsdatum, URL och titel ingår inte, eftersom de kan ändras utan att innehållet gör det. Summan räknas utan själva sakkunnigstatusen, så att signaturen kan skrivas in utan att summan ändras.

Regelbasens filer:

```
regelbas/
  version.yaml                 regelbas_version
  falt.yaml                    fältregister (lista)
  kallor.yaml                  källor (lista)
  lydelser.yaml                paragraflydelser (lista)
  lydelsetexter/<id>.txt       paragraftexten för varje lydelse
  krav/*.yaml                  krav (listor)
  kataloger/hot.yaml, sarbarheter.yaml, kontroller.yaml, tjanster.yaml, bristmonster.yaml
  tillatelselistor.yaml        tillåtelselistor för AI-underlag (lista)
  beslutstabeller/metod.yaml   riskmatris och regler (mappning)
  regelpaket/*.yaml            ett regelpaket per fil (mappning)
```

- [ ] **Step 1: Skriv fixturerna i `tester/conftest.py`**

```python
"""Gemensamma fixturer. Alla uppgifter är syntetiska."""

import copy
from datetime import date

import pytest
import yaml

from riskanalys.lagring.kontrollsumma import for_text

LYDELSETEXT = "Verksamhetsutövaren ska göra en allmän\nriskbedömning. Syntetisk testtext.\n"
LYDELSESUMMA = for_text(" ".join(LYDELSETEXT.split()))


def _matris() -> list[dict]:
    nivaer = [
        ("låg", "begränsad", "låg"),
        ("låg", "betydande", "måttlig"),
        ("låg", "allvarlig", "måttlig"),
        ("medel", "begränsad", "måttlig"),
        ("medel", "betydande", "måttlig"),
        ("medel", "allvarlig", "hög"),
        ("hög", "begränsad", "måttlig"),
        ("hög", "betydande", "hög"),
        ("hög", "allvarlig", "mycket hög"),
    ]
    return [
        {
            "id": f"BT-MATRIS-{nummer:02d}",
            "sannolikhet": sannolikhet,
            "konsekvens": konsekvens,
            "risk": risk,
            "grund": "metodval",
            "forklaring": f"{sannolikhet} sannolikhet och {konsekvens} konsekvens ger {risk} risk.",
        }
        for nummer, (sannolikhet, konsekvens, risk) in enumerate(nivaer, start=1)
    ]


def _regel(regel_id: str) -> dict:
    return {"id": regel_id, "grund": "metodval", "forklaring": "Testregel."}


METOD = {
    "riskmatris": _matris(),
    "sannolikhet": _regel("BT-SANN-01"),
    "konsekvens": _regel("BT-KONS-01"),
    "terrorfinansiering": _regel("BT-TF-01"),
    "kvarstaende_ej_belagd": _regel("BT-KVAR-01"),
    "kvarstaende_sankning": _regel("BT-KVAR-02"),
}

MINIMAL = {
    "version.yaml": {"regelbas_version": "0.0.1"},
    "falt.yaml": [
        {"id": "P-TJ.T-1.erbjuds", "typ": "bool", "fraga": "Erbjuds tjänsten?", "varfor": "Test."},
        {"id": "P-A", "typ": "andel", "fraga": "Hur stor andel?", "varfor": "Test."},
        {"id": "P-NAMN", "typ": "text", "fraga": "Namn?", "varfor": "Test.", "personuppgift": True},
        {"id": "P-C.utf", "typ": "val", "fraga": "Finns kontrollen?", "varfor": "Test.", "val": ["finns", "saknas"]},
        {"id": "P-C.gen", "typ": "val", "fraga": "Är den belagd?", "varfor": "Test.", "val": ["belagt", "ej_belagt"]},
    ],
    "kallor.yaml": [
        {
            "id": "SRC-1",
            "titel": "Testkälla",
            "typ": "föreskrift",
            "utgivare": "Test",
            "url": "https://example.se",
            "hamtad": date(2026, 10, 1),
            "geografi": ["Västra Götaland"],
            "paragrafer": ["1 kap. 1 §", "2 kap. 1 §", "2 kap. 2 §"],
        }
    ],
    "lydelser.yaml": [
        {
            "id": "LYD-1",
            "kalla": "SRC-1",
            "lagrum": "2 kap. 1 §",
            "ikraft": date(2024, 7, 1),
            "primarkalla": "test",
            "text_kontrollsumma": LYDELSESUMMA,
        }
    ],
    "lydelsetexter/LYD-1.txt": LYDELSETEXT,
    "krav/test.yaml": [
        {
            "id": "KRV-1",
            "kalla": "SRC-1",
            "lagrum": "2 kap. 1 §",
            "lydelser": ["LYD-1"],
            "grund": "ska_krav",
            "text": "Testkrav.",
            "galler_om": {"alla": []},
            "belagg": ["dokument"],
            "uppfylls_i": ["D-ARB.1"],
        }
    ],
    "kataloger/hot.yaml": [{"id": "H-1", "namn": "Testhot", "beskrivning": "Test.", "kallor": ["SRC-1"]}],
    "kataloger/sarbarheter.yaml": [
        {
            "id": "S-1",
            "namn": "Testsårbarhet",
            "omrade": "kund",
            "grund": "metodval",
            "villkor": {"falt": "P-A", "op": ">=", "varde": 0.2},
            "effekt": {"sannolikhet": 1},
            "kallor": ["SRC-1"],
        }
    ],
    "kataloger/kontroller.yaml": [
        {
            "id": "C-1",
            "namn": "Testkontroll",
            "beskrivning": "Test.",
            "utformning_falt": "P-C.utf",
            "genomforande_falt": "P-C.gen",
        }
    ],
    "kataloger/tjanster.yaml": [
        {
            "id": "T-1",
            "namn": "Testtjänst",
            "sektor": "redovisning",
            "beskrivning": "Test.",
            "erbjuds_falt": "P-TJ.T-1.erbjuds",
            "hot": ["H-1"],
            "sarbarheter": ["S-1"],
            "kontroller": ["C-1"],
            "grund_sannolikhet": "medel",
            "grund_konsekvens": "betydande",
            "grund_tf_sannolikhet": "låg",
            "kallor": ["SRC-1"],
        }
    ],
    "kataloger/bristmonster.yaml": [
        {
            "id": "B-1",
            "namn": "Testbrist",
            "upptacks": "Test.",
            "automatiserad": False,
            "allvar": "medel",
            "grund": "tillsynspraxis",
            "kallor": ["SRC-1"],
        }
    ],
    "tillatelselistor.yaml": [{"id": "risk_per_tjanst", "falt": ["P-A"], "undvik": ["B-1"]}],
    "beslutstabeller/metod.yaml": METOD,
    "regelpaket/test.yaml": {
        "id": "RP-1",
        "namn": "Testpaket",
        "sektor": "redovisning",
        "lan": ["Västra Götaland"],
        "kallor": ["SRC-1"],
        "krav": ["KRV-1"],
        "tjanster": ["T-1"],
        "paragrafkarta": {
            "giltig_fran": date(2024, 7, 1),
            "omfattning": [{"kalla": "SRC-1", "kapitel": ["2 kap."]}],
            "rader": [
                {"kalla": "SRC-1", "lagrum": "2 kap. 1 §", "krav": ["KRV-1"]},
                {"kalla": "SRC-1", "lagrum": "2 kap. 2 §", "ej_tillamplig": "Testmotivering."},
            ],
        },
    },
}


@pytest.fixture
def minimal_filer():
    """En kopia av den minimala regelbasen som testet får ändra i."""
    return copy.deepcopy(MINIMAL)


@pytest.fixture
def skriv_minimal_regelbas():
    """Skriver den minimala regelbasen, med valfria ersättningar per fil, till en mapp.

    Filer som slutar på .txt skrivs som text, övriga som YAML.
    """

    def skriv(rot, ersattningar=None):
        filer = copy.deepcopy(MINIMAL)
        filer.update(ersattningar or {})
        for relativ, innehall in filer.items():
            sokvag = rot / relativ
            sokvag.parent.mkdir(parents=True, exist_ok=True)
            if relativ.endswith(".txt"):
                sokvag.write_text(innehall, encoding="utf-8")
            else:
                sokvag.write_text(yaml.safe_dump(innehall, allow_unicode=True, sort_keys=False), encoding="utf-8")
        return rot

    return skriv


@pytest.fixture
def minimal_rot(tmp_path, skriv_minimal_regelbas):
    return skriv_minimal_regelbas(tmp_path / "regelbas")


@pytest.fixture
def minimal_regelbas(minimal_rot):
    from riskanalys.regelverk.laddning import ladda_regelbas

    return ladda_regelbas(minimal_rot)
```

- [ ] **Step 2: Skriv det felande testet `tester/enhet/test_laddning.py`**

```python
from datetime import date

import pytest

from riskanalys.regelverk.laddning import (
    RegelbasFel,
    ladda_regelbas,
    lydelsetextens_kontrollsumma,
    regelbasens_kontrollsumma,
    regelbasfiler,
)
from riskanalys.regelverk.modeller import Sakkunnig
from riskanalys.regelverk.villkor import Faltdef


def test_minimal_regelbas_laddas(minimal_rot):
    regelbas = ladda_regelbas(minimal_rot)
    assert regelbas.version == "0.0.1"
    assert set(regelbas.krav) == {"KRV-1"}
    assert set(regelbas.regelpaket) == {"RP-1"}
    assert regelbas.metod.sannolikhet.id == "BT-SANN-01"
    assert regelbas.kontrollsumma.startswith("sha256:")
    assert regelbas.krav["KRV-1"].galler_om == {"alla": []}
    assert regelbas.krav["KRV-1"].belagg == ("dokument",)


def test_paragrafkartan_laddas_med_rader_och_giltighet(minimal_regelbas):
    karta = minimal_regelbas.regelpaket["RP-1"].paragrafkarta
    assert [(rad.lagrum, rad.hanterad) for rad in karta.rader] == [("2 kap. 1 §", True), ("2 kap. 2 §", True)]
    assert karta.ohanterade() == ()
    assert karta.galler(date(2024, 7, 1))
    assert not karta.galler(date(2024, 6, 30))


def _med_krav(regelbas, **andringar):
    krav = regelbas.krav["KRV-1"].model_copy(update=andringar)
    return regelbas.model_copy(update={"krav": {**regelbas.krav, "KRV-1": krav}})


def _med_lydelse(regelbas, **andringar):
    lydelse = regelbas.lydelser["LYD-1"].model_copy(update=andringar)
    return regelbas.model_copy(update={"lydelser": {**regelbas.lydelser, "LYD-1": lydelse}})


def _med_kalla(regelbas, **andringar):
    kalla = regelbas.kallor["SRC-1"].model_copy(update=andringar)
    return regelbas.model_copy(update={"kallor": {**regelbas.kallor, "SRC-1": kalla}})


def test_sakkunnigstatus_galler_bara_det_granskade_innehallet(minimal_regelbas):
    summa = minimal_regelbas.kravets_innehallssumma("KRV-1")
    signatur = Sakkunnig(status="verifierad", av="Testsakkunnig", datum=date(2026, 10, 1), kontrollsumma=summa)
    signerad = _med_krav(minimal_regelbas, sakkunnig=signatur)
    assert signerad.kravets_innehallssumma("KRV-1") == summa
    assert signatur.galler(signerad.kravets_innehallssumma("KRV-1"))
    assert not signatur.galler(_med_krav(signerad, text="Ett annat krav.").kravets_innehallssumma("KRV-1"))


@pytest.mark.parametrize(
    ("andra", "andras"),
    [
        (lambda rb: _med_lydelse(rb, text_kontrollsumma="sha256:" + "1" * 64), True),
        (lambda rb: _med_lydelse(rb, upphor=date(2030, 1, 1)), True),
        (lambda rb: _med_kalla(rb, geografi=("Västra Götaland", "Halland")), True),
        (lambda rb: _med_kalla(rb, hamtad=date(2026, 12, 1), url="https://example.se/ny"), False),
    ],
)
def test_kravets_summa_omfattar_refererad_lydelse_och_kallans_giltighet(minimal_regelbas, andra, andras):
    fore = minimal_regelbas.kravets_innehallssumma("KRV-1")
    assert (andra(minimal_regelbas).kravets_innehallssumma("KRV-1") != fore) is andras


def test_kartans_summa_omfattar_lydelser_och_paragrafindelning(minimal_regelbas):
    fore = minimal_regelbas.kartans_innehallssumma("RP-1")
    assert _med_lydelse(minimal_regelbas, text_kontrollsumma="sha256:" + "1" * 64).kartans_innehallssumma("RP-1") != fore
    assert _med_kalla(minimal_regelbas, paragrafer=("2 kap. 1 §", "2 kap. 2 §")).kartans_innehallssumma("RP-1") != fore


def test_lydelsetextens_kontrollsumma_bortser_fran_radbrytningar(minimal_filer):
    text = minimal_filer["lydelsetexter/LYD-1.txt"]
    summa = minimal_filer["lydelser.yaml"][0]["text_kontrollsumma"]
    assert lydelsetextens_kontrollsumma(text) == summa
    assert lydelsetextens_kontrollsumma("  " + text.replace("\n", "\n   ")) == summa
    assert lydelsetextens_kontrollsumma(text.replace("allmän", "särskild")) != summa


def test_saknad_lydelsetext_rapporteras(minimal_rot):
    (minimal_rot / "lydelsetexter" / "LYD-1.txt").unlink()
    with pytest.raises(RegelbasFel, match="lydelsetexter/LYD-1.txt: texten till lydelsen LYD-1 saknas"):
        ladda_regelbas(minimal_rot)


def test_andrad_lydelsetext_rapporteras(minimal_rot):
    (minimal_rot / "lydelsetexter" / "LYD-1.txt").write_text("En annan text.", encoding="utf-8")
    with pytest.raises(RegelbasFel, match="stämmer inte med text_kontrollsumma"):
        ladda_regelbas(minimal_rot)


def test_lydelse_utan_textkontrollsumma_vagras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    lydelser = minimal_filer["lydelser.yaml"]
    del lydelser[0]["text_kontrollsumma"]
    rot = skriv_minimal_regelbas(tmp_path / "rb", {"lydelser.yaml": lydelser})
    with pytest.raises(RegelbasFel, match="lydelser.yaml, post 1: text_kontrollsumma"):
        ladda_regelbas(rot)


def test_krav_utan_tillamplighet_eller_belagg_vagras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    krav = minimal_filer["krav/test.yaml"]
    del krav[0]["galler_om"]
    krav[0]["belagg"] = []
    rot = skriv_minimal_regelbas(tmp_path / "rb", {"krav/test.yaml": krav})
    with pytest.raises(RegelbasFel) as fel:
        ladda_regelbas(rot)
    assert "krav/test.yaml, post 1: galler_om" in str(fel.value)
    assert "belagg" in str(fel.value)


def test_okant_slag_av_belagg_vagras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    krav = minimal_filer["krav/test.yaml"]
    krav[0]["belagg"] = ["mejl"]
    rot = skriv_minimal_regelbas(tmp_path / "rb", {"krav/test.yaml": krav})
    with pytest.raises(RegelbasFel, match="krav/test.yaml, post 1: belagg"):
        ladda_regelbas(rot)


def test_lydelsetexterna_ingar_i_regelbasens_filer(minimal_rot):
    assert minimal_rot / "lydelsetexter" / "LYD-1.txt" in regelbasfiler(minimal_rot)


def test_faltdefinitioner(minimal_regelbas):
    assert minimal_regelbas.faltdefinitioner()["P-C.utf"] == Faltdef("P-C.utf", "val", ("finns", "saknas"))


def test_alla_id_innehaller_poster_och_regler(minimal_regelbas):
    alla = minimal_regelbas.alla_id()
    assert {"P-A", "SRC-1", "LYD-1", "KRV-1", "H-1", "S-1", "C-1", "T-1", "B-1"} <= alla
    assert {"BT-MATRIS-01", "BT-SANN-01", "BT-KVAR-02"} <= alla


def test_saknad_mapp_vagras(tmp_path):
    with pytest.raises(RegelbasFel, match="finns inte"):
        ladda_regelbas(tmp_path / "saknas")


def test_saknad_fil_rapporteras(minimal_rot):
    (minimal_rot / "falt.yaml").unlink()
    with pytest.raises(RegelbasFel, match="Filen saknas"):
        ladda_regelbas(minimal_rot)


def test_ogiltig_yaml_rapporteras(minimal_rot):
    (minimal_rot / "kataloger" / "hot.yaml").write_text("- id: [", encoding="utf-8")
    with pytest.raises(RegelbasFel, match="Ogiltig YAML"):
        ladda_regelbas(minimal_rot)


def test_okand_nyckel_i_post_rapporteras_med_fil_och_post(tmp_path, skriv_minimal_regelbas, minimal_filer):
    hot = minimal_filer["kataloger/hot.yaml"]
    hot[0]["okand"] = "x"
    rot = skriv_minimal_regelbas(tmp_path / "rb", {"kataloger/hot.yaml": hot})
    with pytest.raises(RegelbasFel, match="kataloger/hot.yaml, post 1"):
        ladda_regelbas(rot)


def test_dubblett_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    hot = minimal_filer["kataloger/hot.yaml"]
    rot = skriv_minimal_regelbas(tmp_path / "rb", {"kataloger/hot.yaml": hot + hot})
    with pytest.raises(RegelbasFel, match="H-1 finns redan"):
        ladda_regelbas(rot)


def test_alla_fel_samlas_i_ett_undantag(minimal_rot):
    (minimal_rot / "falt.yaml").unlink()
    (minimal_rot / "kallor.yaml").unlink()
    with pytest.raises(RegelbasFel) as fel:
        ladda_regelbas(minimal_rot)
    assert len(fel.value.fel) == 2


def test_kontrollsumman_andras_nar_en_fil_andras(minimal_rot):
    fore = regelbasens_kontrollsumma(minimal_rot)
    (minimal_rot / "version.yaml").write_text("regelbas_version: '0.0.2'\n", encoding="utf-8")
    assert regelbasens_kontrollsumma(minimal_rot) != fore
```

- [ ] **Step 3: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/enhet/test_laddning.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.regelverk.laddning'`.

- [ ] **Step 4: Skriv `src/riskanalys/regelverk/modeller.py`**

```python
"""Datamodeller för regelbasen (spec avsnitt 6)."""

import json
from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from riskanalys.lagring.kontrollsumma import for_text
from riskanalys.regelverk.villkor import Faltdef

Grund = Literal["ska_krav", "allmänt_råd", "tillsynspraxis", "eu_utkast", "metodval"]
Sannolikhet = Literal["låg", "medel", "hög"]
Konsekvens = Literal["begränsad", "betydande", "allvarlig"]
Risk = Literal["låg", "måttlig", "hög", "mycket hög"]
Allvar = Literal["blockerande", "hög", "medel", "låg"]
Belagg = Literal["dokument", "datum", "logg", "beslut", "register"]
KONTROLLSUMMA = r"^sha256:[0-9a-f]{64}$"
KALLANS_GILTIGHET = frozenset({"id", "typ", "utgivare", "geografi", "beslutad", "konsoliderad_tom", "kontrollsumma"})


class Strikt(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Falt(Strikt):
    id: str
    typ: Literal["bool", "heltal", "tal", "andel", "text", "val", "datum"]
    fraga: str
    varfor: str
    personuppgift: bool = False
    kritisk: bool = False
    smagrupp: bool = False
    val: tuple[str, ...] = ()


class Kalla(Strikt):
    id: str
    titel: str
    typ: Literal[
        "lag",
        "förordning",
        "föreskrift",
        "allmänt_råd",
        "vägledning",
        "tillsynsrapport",
        "riskbedömning",
        "beslut",
        "eu_förordning",
        "eu_riktlinje_utkast",
    ]
    utgivare: str
    url: str
    hamtad: date
    geografi: tuple[str, ...] = ()
    beslutad: date | None = None
    konsoliderad_tom: str | None = None
    kontrollsumma: str | None = None
    paragrafer: tuple[str, ...] = ()


class Lydelse(Strikt):
    id: str
    kalla: str
    lagrum: str
    ikraft: date
    upphor: date | None = None
    inford_genom: str | None = None
    primarkalla: str
    text_kontrollsumma: str = Field(pattern=KONTROLLSUMMA)


class Sakkunnig(Strikt):
    """Sakkunnig granskning. Status verifierad gäller bara det innehåll som kontrollsumman beskriver."""

    status: Literal["ej_granskad", "verifierad", "ändras"] = "ej_granskad"
    av: str | None = None
    datum: date | None = None
    kontrollsumma: str | None = None

    def galler(self, innehallssumma: str) -> bool:
        return self.status == "verifierad" and self.kontrollsumma == innehallssumma


class Krav(Strikt):
    id: str
    kalla: str
    lagrum: str
    lydelser: tuple[str, ...] = Field(min_length=1)
    grund: Grund
    text: str
    galler_om: dict[str, Any]
    belagg: tuple[Belagg, ...] = Field(min_length=1)
    uppfylls_i: tuple[str, ...] = Field(min_length=1)
    ikraft: date | None = None
    upphor: date | None = None
    sakkunnig: Sakkunnig = Sakkunnig()


class Hot(Strikt):
    id: str
    namn: str
    beskrivning: str
    kallor: tuple[str, ...] = Field(min_length=1)
    galler_tf: bool = False


class Effekt(Strikt):
    sannolikhet: int = Field(ge=1, le=2)


class Sarbarhet(Strikt):
    id: str
    namn: str
    omrade: Literal["kund", "kanal", "geo", "verk", "tj"]
    grund: Grund
    villkor: dict[str, Any]
    vid_okant: Literal["preliminart_galler", "preliminart_galler_ej"] = "preliminart_galler"
    effekt: Effekt
    galler: Literal["penningtvatt", "terrorfinansiering", "bada"] = "penningtvatt"
    kallor: tuple[str, ...] = Field(min_length=1)


class Kontroll(Strikt):
    id: str
    namn: str
    beskrivning: str
    utformning_falt: str
    genomforande_falt: str
    kallor: tuple[str, ...] = ()


class Tjanst(Strikt):
    id: str
    namn: str
    sektor: str
    beskrivning: str
    erbjuds_falt: str
    hot: tuple[str, ...] = Field(min_length=1)
    sarbarheter: tuple[str, ...] = ()
    kontroller: tuple[str, ...] = ()
    grund_sannolikhet: Sannolikhet
    grund_konsekvens: Konsekvens
    grund_tf_sannolikhet: Sannolikhet
    kallor: tuple[str, ...] = Field(min_length=1)


class Bristmonster(Strikt):
    id: str
    namn: str
    upptacks: str
    automatiserad: bool
    allvar: Allvar
    grund: Grund
    kallor: tuple[str, ...] = Field(min_length=1)


class MatrisRad(Strikt):
    id: str
    sannolikhet: Sannolikhet
    konsekvens: Konsekvens
    risk: Risk
    grund: Grund
    forklaring: str


class Regel(Strikt):
    id: str
    grund: Grund
    forklaring: str


class Metod(Strikt):
    riskmatris: tuple[MatrisRad, ...]
    sannolikhet: Regel
    konsekvens: Regel
    terrorfinansiering: Regel
    kvarstaende_ej_belagd: Regel
    kvarstaende_sankning: Regel

    def regler(self) -> tuple[Regel, ...]:
        return (
            self.sannolikhet,
            self.konsekvens,
            self.terrorfinansiering,
            self.kvarstaende_ej_belagd,
            self.kvarstaende_sankning,
        )


class Tillatelselista(Strikt):
    id: str
    falt: tuple[str, ...]
    undvik: tuple[str, ...] = ()


class Kartrad(Strikt):
    """En paragraf på paragrafkartan: de krav den ger upphov till, eller varför den inte gäller sektorn.

    En rad utan krav och utan motivering är en paragraf som regelbasen ännu inte hanterar.
    """

    kalla: str
    lagrum: str
    krav: tuple[str, ...] = ()
    ej_tillamplig: str | None = None

    @property
    def hanterad(self) -> bool:
        return bool(self.krav) or bool(self.ej_tillamplig)


class Kartomfattning(Strikt):
    """Vilka kapitel i en källa som kartan ska täcka, till exempel 2 kap. i 14FS 2024:11."""

    kalla: str
    kapitel: tuple[str, ...] = Field(min_length=1)


class Paragrafkarta(Strikt):
    """Varje paragraf i de relevanta kapitlen för ett datumintervall (spec 16.1)."""

    giltig_fran: date
    giltig_till: date | None = None
    omfattning: tuple[Kartomfattning, ...] = Field(min_length=1)
    rader: tuple[Kartrad, ...] = Field(min_length=1)
    sakkunnig: Sakkunnig = Sakkunnig()

    def galler(self, datum: date) -> bool:
        return self.giltig_fran <= datum and (self.giltig_till is None or datum < self.giltig_till)

    def ohanterade(self) -> tuple[Kartrad, ...]:
        return tuple(rad for rad in self.rader if not rad.hanterad)


class Regelpaket(Strikt):
    id: str
    namn: str
    sektor: str
    lan: tuple[str, ...] = Field(min_length=1)
    kallor: tuple[str, ...]
    krav: tuple[str, ...] = Field(min_length=1)
    tjanster: tuple[str, ...] = Field(min_length=1)
    paragrafkarta: Paragrafkarta


class Regelbas(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: str
    falt: dict[str, Falt]
    kallor: dict[str, Kalla]
    lydelser: dict[str, Lydelse]
    krav: dict[str, Krav]
    hot: dict[str, Hot]
    sarbarheter: dict[str, Sarbarhet]
    kontroller: dict[str, Kontroll]
    tjanster: dict[str, Tjanst]
    bristmonster: dict[str, Bristmonster]
    metod: Metod
    tillatelselistor: dict[str, Tillatelselista]
    regelpaket: dict[str, Regelpaket]
    kontrollsumma: str

    def faltdefinitioner(self) -> dict[str, Faltdef]:
        return {falt.id: Faltdef(falt.id, falt.typ, falt.val) for falt in self.falt.values()}

    def alla_id(self) -> set[str]:
        """Alla ID:n som text i ett dokument får hänvisa till."""
        samlingar = (
            self.falt,
            self.kallor,
            self.lydelser,
            self.krav,
            self.hot,
            self.sarbarheter,
            self.kontroller,
            self.tjanster,
            self.bristmonster,
        )
        alla = {nyckel for samling in samlingar for nyckel in samling}
        alla |= {rad.id for rad in self.metod.riskmatris}
        alla |= {regel.id for regel in self.metod.regler()}
        return alla

    def kravets_innehallssumma(self, krav_id: str) -> str:
        """Det en sakkunnig godkänner för ett krav: kravet, dess lydelser med giltighet och textsumma,
        källans giltighetsuppgifter och definitionerna av de fält som villkoret galler_om använder."""
        krav = self.krav[krav_id]
        kalla = self.kallor.get(krav.kalla)
        underlag = {
            "krav": krav.model_dump(mode="json", exclude={"sakkunnig"}),
            "lydelser": [self.lydelser[i].model_dump(mode="json") for i in krav.lydelser if i in self.lydelser],
            "kalla": kalla.model_dump(mode="json", include=KALLANS_GILTIGHET) if kalla else None,
            "falt": [
                self.falt[falt_id].model_dump(mode="json")
                for falt_id in sorted(_falt_i_villkorsdata(krav.galler_om))
                if falt_id in self.falt
            ],
        }
        return _summa(underlag)

    def kartans_innehallssumma(self, paket_id: str) -> str:
        """Det en sakkunnig godkänner för en paragrafkarta: kartans rader och giltighet, paketets län och krav,
        källornas paragrafindelning och giltighet samt lydelserna i de källor kartan omfattar."""
        paket = self.regelpaket[paket_id]
        karta = paket.paragrafkarta
        kalla_ids = sorted({omfattning.kalla for omfattning in karta.omfattning})
        underlag = {
            "karta": karta.model_dump(mode="json", exclude={"sakkunnig"}),
            "paket": {"id": paket.id, "lan": list(paket.lan), "krav": list(paket.krav)},
            "kallor": [
                self.kallor[kalla_id].model_dump(mode="json", include=KALLANS_GILTIGHET | {"paragrafer"})
                for kalla_id in kalla_ids
                if kalla_id in self.kallor
            ],
            "lydelser": [
                lydelse.model_dump(mode="json")
                for lydelse in sorted(self.lydelser.values(), key=lambda post: post.id)
                if lydelse.kalla in kalla_ids
            ],
        }
        return _summa(underlag)


def _summa(underlag: dict[str, Any]) -> str:
    return for_text(json.dumps(underlag, sort_keys=True, ensure_ascii=False))


def _falt_i_villkorsdata(data: Any) -> set[str]:
    """Fält som ett villkor i YAML-form nämner, utan att villkoret behöver vara giltigt."""
    if isinstance(data, dict):
        egna = {data["falt"]} if isinstance(data.get("falt"), str) else set()
        return egna.union(*(_falt_i_villkorsdata(varde) for varde in data.values()))
    if isinstance(data, list):
        return set().union(*(_falt_i_villkorsdata(del_) for del_ in data))
    return set()
```

- [ ] **Step 5: Skriv `src/riskanalys/regelverk/laddning.py`**

```python
"""Läser in regelbasen från YAML-filer och lydelsetexter (spec 5.1)."""

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ValidationError

from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.kontrollsumma import for_fil, for_text
from riskanalys.regelverk.modeller import (
    Bristmonster,
    Falt,
    Hot,
    Kalla,
    Kontroll,
    Krav,
    Lydelse,
    Metod,
    Regelbas,
    Regelpaket,
    Sarbarhet,
    Tillatelselista,
    Tjanst,
)

STANDARD_REGELBAS = Path(__file__).resolve().parents[3] / "regelbas"
LYDELSETEXTER = "lydelsetexter"
REGELBASFILER = frozenset({".yaml", ".txt"})

LISTFILER: dict[str, tuple[str, type[BaseModel]]] = {
    "falt": ("falt.yaml", Falt),
    "kallor": ("kallor.yaml", Kalla),
    "lydelser": ("lydelser.yaml", Lydelse),
    "hot": ("kataloger/hot.yaml", Hot),
    "sarbarheter": ("kataloger/sarbarheter.yaml", Sarbarhet),
    "kontroller": ("kataloger/kontroller.yaml", Kontroll),
    "tjanster": ("kataloger/tjanster.yaml", Tjanst),
    "bristmonster": ("kataloger/bristmonster.yaml", Bristmonster),
    "tillatelselistor": ("tillatelselistor.yaml", Tillatelselista),
}


class RegelbasFel(RiskanalysFel):
    """Regelbasen kan inte läsas in eller innehåller fel."""

    def __init__(self, fel: list[str]) -> None:
        super().__init__("Regelbasen har fel:\n" + "\n".join(f"- {rad}" for rad in fel))
        self.fel = fel


def regelbasfiler(rot: Path) -> list[Path]:
    """Alla filer i regelbasen (YAML och lydelsetexter), sorterade."""
    return sorted(sokvag for sokvag in rot.rglob("*") if sokvag.is_file() and sokvag.suffix in REGELBASFILER)


def regelbasens_kontrollsumma(rot: Path) -> str:
    """En kontrollsumma för hela regelbasen, byggd av varje fils kontrollsumma."""
    rader = [f"{sokvag.relative_to(rot).as_posix()} {for_fil(sokvag)}" for sokvag in regelbasfiler(rot)]
    return for_text("\n".join(rader))


def lydelsetextens_kontrollsumma(text: str) -> str:
    """Kontrollsumma för en paragraftext där alla blanktecken slagits ihop till ett mellanslag."""
    return for_text(" ".join(text.split()))


def ladda_regelbas(rot: Path = STANDARD_REGELBAS) -> Regelbas:
    if not rot.is_dir():
        raise RegelbasFel([f"Regelbasmappen {rot} finns inte."])
    fel: list[str] = []
    data: dict[str, Any] = {}
    for namn, (relativ, modell) in LISTFILER.items():
        data[namn] = _poster(rot, [rot / relativ], modell, fel)
    data["krav"] = _poster(rot, sorted((rot / "krav").glob("*.yaml")), Krav, fel)
    data["regelpaket"] = _poster(rot, sorted((rot / "regelpaket").glob("*.yaml")), Regelpaket, fel, en_per_fil=True)
    version = _las_yaml(rot / "version.yaml", fel)
    metod = _las_yaml(rot / "beslutstabeller" / "metod.yaml", fel)
    fel += _lydelsetexter(rot, data["lydelser"].values())
    if fel:
        raise RegelbasFel(fel)
    try:
        return Regelbas(
            version=str(version["regelbas_version"]),
            metod=Metod.model_validate(metod),
            kontrollsumma=regelbasens_kontrollsumma(rot),
            **data,
        )
    except (ValidationError, KeyError, TypeError) as undantag:
        raise RegelbasFel([f"version.yaml eller beslutstabeller/metod.yaml: {undantag}"]) from undantag


def _lydelsetexter(rot: Path, lydelser: Iterable[Lydelse]) -> list[str]:
    """Kontrollerar att varje lydelse har sin text och att texten stämmer med kontrollsumman."""
    fel = []
    for lydelse in lydelser:
        relativ = f"{LYDELSETEXTER}/{lydelse.id}.txt"
        sokvag = rot / relativ
        if not sokvag.is_file():
            fel.append(f"{relativ}: texten till lydelsen {lydelse.id} saknas.")
        elif lydelsetextens_kontrollsumma(sokvag.read_text(encoding="utf-8")) != lydelse.text_kontrollsumma:
            fel.append(f"{relativ}: texten stämmer inte med text_kontrollsumma för {lydelse.id}.")
    return fel


def _las_yaml(sokvag: Path, fel: list[str]) -> Any:
    try:
        return yaml.safe_load(sokvag.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fel.append(f"Filen saknas: {sokvag}")
    except yaml.YAMLError as undantag:
        fel.append(f"Ogiltig YAML i {sokvag}: {undantag}")
    return None


def _poster(
    rot: Path,
    filer: list[Path],
    modell: type[BaseModel],
    fel: list[str],
    en_per_fil: bool = False,
) -> dict[str, Any]:
    resultat: dict[str, Any] = {}
    for fil in filer:
        relativ = fil.relative_to(rot).as_posix()
        innehall = _las_yaml(fil, fel)
        if innehall is None:
            continue
        poster = [innehall] if en_per_fil else innehall
        if not isinstance(poster, list):
            fel.append(f"{relativ}: ska innehålla en lista.")
            continue
        for nummer, post in enumerate(poster, start=1):
            try:
                objekt = modell.model_validate(post)
            except ValidationError as undantag:
                fel.append(f"{relativ}, post {nummer}: {_kort(undantag)}")
                continue
            if objekt.id in resultat:
                fel.append(f"{relativ}: ID:t {objekt.id} finns redan.")
                continue
            resultat[objekt.id] = objekt
    return resultat


def _kort(undantag: ValidationError) -> str:
    return "; ".join(
        f"{'.'.join(str(del_) for del_ in fel['loc']) or 'posten'}: {fel['msg']}" for fel in undantag.errors()
    )
```

- [ ] **Step 6: Kör testet**

Run: `.venv/bin/pytest tester/enhet/test_laddning.py -v`
Expected: alla tester passerar.

Lydelsetexterna kontrolleras vid inläsningen, eftersom bara inläsningen har tillgång till filerna. Ett fel i en text samlas med övriga fel i samma `RegelbasFel`.

- [ ] **Step 7: Commit**

```bash
git add src/riskanalys/regelverk/modeller.py src/riskanalys/regelverk/laddning.py tester/conftest.py tester/enhet/test_laddning.py
git commit -m "feat: regelbasmodeller och inläsning av YAML"
```

---

### Task 6: Validering av regelbasen

**Files:**
- Create: `src/riskanalys/regelverk/validering.py`
- Test: `tester/regelkontrakt/test_validering_regelbas.py`

**Interfaces:**
- Consumes: `Regelbas` och dess `faltdefinitioner()`, `tolka_villkor`, `VillkorsFel`, fixturerna `minimal_regelbas`, `minimal_filer`, `skriv_minimal_regelbas`.
- Produces: `validering.validera(regelbas: Regelbas) -> list[str]`. Tom lista betyder giltig regelbas. `validering.AVSNITT_ID` (regex för avsnitts-ID som `D-ARB.6.1`) och `validering.KAPITEL` (regex för kapitlet i ett lagrum).

Inläsningen (Task 5) kontrollerar varje post för sig. Valideringen kontrollerar att posterna hänger ihop: att hänvisningar pekar på något som finns, att villkoren går att tolka, att riskmatrisen är fullständig, att varje paragrafkarta har exakt en rad för varje paragraf i sin omfattning enligt källans paragrafindelning, att varje krav i paketet står på kartan, och att status `verifierad` har granskare, datum och samma kontrollsumma som innehållet har nu.

Valideringen kräver inte att varje rad är hanterad. En paragraf som regelbasen ännu inte hanterar är tillåten i regelbasen, men stoppar fastställelsen (Task 20). Så syns luckan i stället för att döljas.

- [ ] **Step 1: Skriv det felande testet `tester/regelkontrakt/test_validering_regelbas.py`**

```python
from datetime import date

from riskanalys.regelverk.laddning import ladda_regelbas, lydelsetextens_kontrollsumma
from riskanalys.regelverk.validering import validera


def _fel(tmp_path, skriv_minimal_regelbas, ersattningar):
    rot = skriv_minimal_regelbas(tmp_path / "rb", ersattningar)
    return validera(ladda_regelbas(rot))


def test_minimal_regelbas_ar_giltig(minimal_regelbas):
    assert validera(minimal_regelbas) == []


def test_saknad_kalla_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    hot = minimal_filer["kataloger/hot.yaml"]
    hot[0]["kallor"] = ["SRC-SAKNAS"]
    fel = _fel(tmp_path, skriv_minimal_regelbas, {"kataloger/hot.yaml": hot})
    assert "H-1: hänvisar till källan SRC-SAKNAS som inte finns." in fel


def test_lydelse_som_upphor_fore_ikrafttradandet_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    lydelser = minimal_filer["lydelser.yaml"]
    lydelser[0]["upphor"] = date(2024, 1, 1)
    fel = _fel(tmp_path, skriv_minimal_regelbas, {"lydelser.yaml": lydelser})
    assert "LYD-1: upphör 2024-01-01 måste vara efter ikraftträdandet 2024-07-01." in fel


def test_krav_med_saknad_lydelse_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    krav = minimal_filer["krav/test.yaml"]
    krav[0]["lydelser"] = ["LYD-SAKNAS"]
    fel = _fel(tmp_path, skriv_minimal_regelbas, {"krav/test.yaml": krav})
    assert "KRV-1: hänvisar till lydelsen LYD-SAKNAS som inte finns." in fel


def test_krav_med_lydelse_ur_annan_kalla_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    kallor = minimal_filer["kallor.yaml"]
    kallor.append({**kallor[0], "id": "SRC-2"})
    krav = minimal_filer["krav/test.yaml"]
    krav[0]["kalla"] = "SRC-2"
    fel = _fel(tmp_path, skriv_minimal_regelbas, {"kallor.yaml": kallor, "krav/test.yaml": krav})
    assert "KRV-1: lydelsen LYD-1 hör till källan SRC-1, inte SRC-2." in fel


def test_felaktigt_villkor_for_tillamplighet_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    krav = minimal_filer["krav/test.yaml"]
    krav[0]["galler_om"] = {"falt": "P-SAKNAS", "op": "finns"}
    fel = _fel(tmp_path, skriv_minimal_regelbas, {"krav/test.yaml": krav})
    assert any(rad.startswith("KRV-1: villkoret galler_om: Okänt fält 'P-SAKNAS'") for rad in fel)


def test_avsnitts_id_med_fel_form_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    krav = minimal_filer["krav/test.yaml"]
    krav[0]["uppfylls_i"] = ["ARB.1"]
    fel = _fel(tmp_path, skriv_minimal_regelbas, {"krav/test.yaml": krav})
    assert "KRV-1: avsnittet ARB.1 har fel form. Använd till exempel D-ARB.6.1." in fel


def test_erbjuds_falt_maste_vara_bool(tmp_path, skriv_minimal_regelbas, minimal_filer):
    tjanster = minimal_filer["kataloger/tjanster.yaml"]
    tjanster[0]["erbjuds_falt"] = "P-A"
    fel = _fel(tmp_path, skriv_minimal_regelbas, {"kataloger/tjanster.yaml": tjanster})
    assert "T-1: fältet P-A för erbjuds måste finnas och vara av typen bool." in fel


def test_tjanst_med_saknat_hot_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    tjanster = minimal_filer["kataloger/tjanster.yaml"]
    tjanster[0]["hot"] = ["H-SAKNAS"]
    fel = _fel(tmp_path, skriv_minimal_regelbas, {"kataloger/tjanster.yaml": tjanster})
    assert "T-1: hänvisar till H-SAKNAS som inte finns." in fel


def test_felaktigt_villkor_i_sarbarhet_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    sarbarheter = minimal_filer["kataloger/sarbarheter.yaml"]
    sarbarheter[0]["villkor"] = {"falt": "P-A", "op": ">=", "varde": 2}
    fel = _fel(tmp_path, skriv_minimal_regelbas, {"kataloger/sarbarheter.yaml": sarbarheter})
    assert any(rad.startswith("S-1: Värdet 2 passar inte typen andel") for rad in fel)


def test_kontrollfalt_med_fel_alternativ_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    falt = minimal_filer["falt.yaml"]
    falt[3]["val"] = ["ja", "nej"]
    fel = _fel(tmp_path, skriv_minimal_regelbas, {"falt.yaml": falt})
    assert "C-1: fältet P-C.utf måste vara ett val med alternativen finns, saknas." in fel


def test_personuppgift_i_tillatelselista_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    listor = minimal_filer["tillatelselistor.yaml"]
    listor[0]["falt"] = ["P-A", "P-NAMN"]
    fel = _fel(tmp_path, skriv_minimal_regelbas, {"tillatelselistor.yaml": listor})
    assert "risk_per_tjanst: fältet P-NAMN är en personuppgift och får inte skickas till AI." in fel


def test_tillatelselista_med_saknat_bristmonster_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    listor = minimal_filer["tillatelselistor.yaml"]
    listor[0]["undvik"] = ["B-SAKNAS"]
    fel = _fel(tmp_path, skriv_minimal_regelbas, {"tillatelselistor.yaml": listor})
    assert "risk_per_tjanst: hänvisar till B-SAKNAS som inte finns." in fel


def test_regelpaket_med_saknat_krav_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    paket = minimal_filer["regelpaket/test.yaml"]
    paket["krav"] = ["KRV-SAKNAS"]
    fel = _fel(tmp_path, skriv_minimal_regelbas, {"regelpaket/test.yaml": paket})
    assert "RP-1: hänvisar till KRV-SAKNAS som inte finns." in fel


def test_ofullstandig_riskmatris_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    metod = minimal_filer["beslutstabeller/metod.yaml"]
    metod["riskmatris"] = metod["riskmatris"][:-1]
    fel = _fel(tmp_path, skriv_minimal_regelbas, {"beslutstabeller/metod.yaml": metod})
    assert "Riskmatrisen ska ha exakt en rad för hög sannolikhet och allvarlig konsekvens, har 0." in fel


def _karta(tmp_path, skriv_minimal_regelbas, minimal_filer, andra):
    """Ändrar paragrafkartan i RP-1 med funktionen andra och returnerar valideringsfelen."""
    paket = minimal_filer["regelpaket/test.yaml"]
    andra(paket["paragrafkarta"])
    return _fel(tmp_path, skriv_minimal_regelbas, {"regelpaket/test.yaml": paket})


def test_paragraf_som_saknas_pa_kartan_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    fel = _karta(tmp_path, skriv_minimal_regelbas, minimal_filer, lambda karta: karta["rader"].pop())
    assert "Paragrafkartan för RP-1 saknar SRC-1 2 kap. 2 §." in fel


def test_paragraf_utanfor_kallans_indelning_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    rad = {"kalla": "SRC-1", "lagrum": "2 kap. 9 §", "ej_tillamplig": "Test."}
    fel = _karta(tmp_path, skriv_minimal_regelbas, minimal_filer, lambda karta: karta["rader"].append(rad))
    assert "Paragrafkartan för RP-1: SRC-1 2 kap. 9 § ingår inte i kartans omfattning eller källans paragrafindelning." in fel


def test_krav_i_paketet_som_inte_star_pa_kartan_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    def andra(karta):
        karta["rader"][0] = {"kalla": "SRC-1", "lagrum": "2 kap. 1 §", "ej_tillamplig": "Test."}

    fel = _karta(tmp_path, skriv_minimal_regelbas, minimal_filer, andra)
    assert "Paragrafkartan för RP-1: kravet KRV-1 i paketet står inte på kartan." in fel


def test_rad_med_bade_krav_och_motivering_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    def andra(karta):
        karta["rader"][0]["ej_tillamplig"] = "Test."

    fel = _karta(tmp_path, skriv_minimal_regelbas, minimal_filer, andra)
    assert "Paragrafkartan för RP-1, SRC-1 2 kap. 1 §: ange antingen krav eller ej_tillamplig, inte båda." in fel


def test_krav_pa_fel_paragraf_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    def andra(karta):
        karta["rader"] = [
            {"kalla": "SRC-1", "lagrum": "2 kap. 1 §", "ej_tillamplig": "Test."},
            {"kalla": "SRC-1", "lagrum": "2 kap. 2 §", "krav": ["KRV-1"]},
        ]

    fel = _karta(tmp_path, skriv_minimal_regelbas, minimal_filer, andra)
    assert "Paragrafkartan för RP-1, SRC-1 2 kap. 2 §: kravet KRV-1 gäller SRC-1 2 kap. 1 §." in fel


def test_kalla_utan_paragrafindelning_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    kallor = minimal_filer["kallor.yaml"]
    kallor[0]["paragrafer"] = []
    fel = _fel(tmp_path, skriv_minimal_regelbas, {"kallor.yaml": kallor})
    assert "Paragrafkartan för RP-1: källan SRC-1 saknas eller har ingen paragrafindelning." in fel


def test_verifierat_krav_som_andrats_rapporteras(tmp_path, skriv_minimal_regelbas, minimal_filer):
    krav = minimal_filer["krav/test.yaml"]
    krav[0]["sakkunnig"] = {
        "status": "verifierad",
        "av": "Testsakkunnig",
        "datum": date(2026, 10, 1),
        "kontrollsumma": "sha256:" + "0" * 64,
    }
    fel = _fel(tmp_path, skriv_minimal_regelbas, {"krav/test.yaml": krav})
    assert any(rad.startswith("KRV-1: innehållet har ändrats efter sakkunniggranskningen.") for rad in fel)


def test_verifierat_krav_galler_inte_efter_andrad_paragraftext(
    tmp_path, skriv_minimal_regelbas, minimal_filer, minimal_regelbas
):
    summa = minimal_regelbas.kravets_innehallssumma("KRV-1")
    krav = minimal_filer["krav/test.yaml"]
    krav[0]["sakkunnig"] = {"status": "verifierad", "av": "Testsakkunnig", "datum": date(2026, 10, 1), "kontrollsumma": summa}
    assert _fel(tmp_path, skriv_minimal_regelbas, {"krav/test.yaml": krav}) == []
    ny_text = "Verksamhetsutövaren ska göra en helt annan bedömning."
    lydelser = minimal_filer["lydelser.yaml"]
    lydelser[0]["text_kontrollsumma"] = lydelsetextens_kontrollsumma(ny_text)
    andrad = {"krav/test.yaml": krav, "lydelser.yaml": lydelser, "lydelsetexter/LYD-1.txt": ny_text}
    fel = _fel(tmp_path, skriv_minimal_regelbas, andrad)
    assert any(rad.startswith("KRV-1: innehållet har ändrats efter sakkunniggranskningen.") for rad in fel)


def test_verifierad_karta_galler_bara_sitt_innehall(tmp_path, skriv_minimal_regelbas, minimal_filer, minimal_regelbas):
    summa = minimal_regelbas.kartans_innehallssumma("RP-1")
    signatur = {"status": "verifierad", "av": "Testsakkunnig", "datum": date(2026, 10, 1), "kontrollsumma": summa}

    def signera(karta):
        karta["sakkunnig"] = signatur

    assert _karta(tmp_path, skriv_minimal_regelbas, minimal_filer, signera) == []

    def signera_och_andra(karta):
        karta["sakkunnig"] = signatur
        karta["rader"][1]["ej_tillamplig"] = "En annan motivering."

    fel = _karta(tmp_path, skriv_minimal_regelbas, minimal_filer, signera_och_andra)
    assert any(rad.startswith("Paragrafkartan för RP-1: innehållet har ändrats efter sakkunniggranskningen.") for rad in fel)
```

- [ ] **Step 2: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/regelkontrakt/test_validering_regelbas.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.regelverk.validering'`.

- [ ] **Step 3: Skriv `src/riskanalys/regelverk/validering.py`**

```python
"""Kontrollerar att regelbasens poster hänger ihop (spec 6 och 16)."""

import re
from collections import Counter
from collections.abc import Iterable
from itertools import product

from riskanalys.regelverk.modeller import Kartrad, Regelbas, Regelpaket
from riskanalys.regelverk.villkor import VillkorsFel, tolka_villkor

AVSNITT_ID = re.compile(r"^D-[A-Z]+(\.\d+)+$")
KAPITEL = re.compile(r"^(\d+ kap\.)")
KONTROLLVAL = {
    "utformning_falt": ("finns", "saknas"),
    "genomforande_falt": ("belagt", "ej_belagt"),
}
SANNOLIKHETER = ("låg", "medel", "hög")
KONSEKVENSER = ("begränsad", "betydande", "allvarlig")


def validera(regelbas: Regelbas) -> list[str]:
    """Returnerar alla fel i regelbasen. Tom lista betyder att regelbasen är giltig."""
    return [
        *_kallor(regelbas),
        *_lydelser(regelbas),
        *_krav(regelbas),
        *_tjanster(regelbas),
        *_sarbarheter(regelbas),
        *_kontroller(regelbas),
        *_tillatelselistor(regelbas),
        *_regelpaket(regelbas),
        *_sakkunnig(regelbas),
        *_matris(regelbas),
    ]


def _saknas(post_id: str, referenser: Iterable[str], finns: Iterable[str], slag: str = "") -> list[str]:
    tillgangliga = set(finns)
    return [f"{post_id}: hänvisar till {slag}{ref} som inte finns." for ref in referenser if ref not in tillgangliga]


def _kallor(regelbas: Regelbas) -> list[str]:
    samlingar = (
        regelbas.hot,
        regelbas.sarbarheter,
        regelbas.kontroller,
        regelbas.tjanster,
        regelbas.bristmonster,
        regelbas.regelpaket,
    )
    med_lista = [
        fel
        for samling in samlingar
        for post in samling.values()
        for fel in _saknas(post.id, post.kallor, regelbas.kallor, "källan ")
    ]
    med_en = [
        fel
        for post in (*regelbas.lydelser.values(), *regelbas.krav.values())
        for fel in _saknas(post.id, (post.kalla,), regelbas.kallor, "källan ")
    ]
    return med_lista + med_en


def _lydelser(regelbas: Regelbas) -> list[str]:
    return [
        f"{lydelse.id}: upphör {lydelse.upphor} måste vara efter ikraftträdandet {lydelse.ikraft}."
        for lydelse in regelbas.lydelser.values()
        if lydelse.upphor is not None and lydelse.upphor <= lydelse.ikraft
    ]


def _krav(regelbas: Regelbas) -> list[str]:
    definitioner = regelbas.faltdefinitioner()
    fel: list[str] = []
    for krav in regelbas.krav.values():
        try:
            tolka_villkor(krav.galler_om, definitioner)
        except VillkorsFel as undantag:
            fel.append(f"{krav.id}: villkoret galler_om: {undantag}")
        fel += _saknas(krav.id, krav.lydelser, regelbas.lydelser, "lydelsen ")
        fel += [
            f"{krav.id}: lydelsen {lydelse_id} hör till källan {regelbas.lydelser[lydelse_id].kalla}, inte {krav.kalla}."
            for lydelse_id in krav.lydelser
            if lydelse_id in regelbas.lydelser and regelbas.lydelser[lydelse_id].kalla != krav.kalla
        ]
        fel += [
            f"{krav.id}: avsnittet {avsnitt} har fel form. Använd till exempel D-ARB.6.1."
            for avsnitt in krav.uppfylls_i
            if not AVSNITT_ID.match(avsnitt)
        ]
        if krav.ikraft and krav.upphor and krav.upphor <= krav.ikraft:
            fel.append(f"{krav.id}: upphör {krav.upphor} måste vara efter ikraftträdandet {krav.ikraft}.")
    return fel


def _tjanster(regelbas: Regelbas) -> list[str]:
    fel: list[str] = []
    for tjanst in regelbas.tjanster.values():
        falt = regelbas.falt.get(tjanst.erbjuds_falt)
        if falt is None or falt.typ != "bool":
            fel.append(f"{tjanst.id}: fältet {tjanst.erbjuds_falt} för erbjuds måste finnas och vara av typen bool.")
        fel += _saknas(tjanst.id, tjanst.hot, regelbas.hot)
        fel += _saknas(tjanst.id, tjanst.sarbarheter, regelbas.sarbarheter)
        fel += _saknas(tjanst.id, tjanst.kontroller, regelbas.kontroller)
    return fel


def _sarbarheter(regelbas: Regelbas) -> list[str]:
    definitioner = regelbas.faltdefinitioner()
    fel: list[str] = []
    for sarbarhet in regelbas.sarbarheter.values():
        try:
            tolka_villkor(sarbarhet.villkor, definitioner)
        except VillkorsFel as undantag:
            fel.append(f"{sarbarhet.id}: {undantag}")
    return fel


def _kontroller(regelbas: Regelbas) -> list[str]:
    fel: list[str] = []
    for kontroll in regelbas.kontroller.values():
        for attribut, alternativ in KONTROLLVAL.items():
            falt_id = getattr(kontroll, attribut)
            falt = regelbas.falt.get(falt_id)
            if falt is None or falt.typ != "val" or tuple(falt.val) != alternativ:
                fel.append(
                    f"{kontroll.id}: fältet {falt_id} måste vara ett val med alternativen {', '.join(alternativ)}."
                )
    return fel


def _tillatelselistor(regelbas: Regelbas) -> list[str]:
    fel: list[str] = []
    for lista in regelbas.tillatelselistor.values():
        fel += _saknas(lista.id, lista.falt, regelbas.falt)
        fel += [
            f"{lista.id}: fältet {falt_id} är en personuppgift och får inte skickas till AI."
            for falt_id in lista.falt
            if falt_id in regelbas.falt and regelbas.falt[falt_id].personuppgift
        ]
        fel += _saknas(lista.id, lista.undvik, regelbas.bristmonster)
    return fel


def _regelpaket(regelbas: Regelbas) -> list[str]:
    return [
        fel
        for paket in regelbas.regelpaket.values()
        for fel in (
            *_saknas(paket.id, paket.krav, regelbas.krav),
            *_saknas(paket.id, paket.tjanster, regelbas.tjanster),
            *_paragrafkarta(regelbas, paket),
        )
    ]


def _kapitel(lagrum: str) -> str:
    traff = KAPITEL.match(lagrum)
    return traff.group(1) if traff else ""


def _paragrafkarta(regelbas: Regelbas, paket: Regelpaket) -> list[str]:
    """Kartan ska ha exakt en rad för varje paragraf i sin omfattning, och varje krav i paketet ska stå på den."""
    karta = paket.paragrafkarta
    namn = f"Paragrafkartan för {paket.id}"
    fel = []
    if karta.giltig_till is not None and karta.giltig_till <= karta.giltig_fran:
        fel.append(f"{namn}: giltig_till måste vara efter giltig_fran.")
    forvantade: list[tuple[str, str]] = []
    for omfattning in karta.omfattning:
        kalla = regelbas.kallor.get(omfattning.kalla)
        if kalla is None or not kalla.paragrafer:
            fel.append(f"{namn}: källan {omfattning.kalla} saknas eller har ingen paragrafindelning.")
            continue
        forvantade += [(kalla.id, lagrum) for lagrum in kalla.paragrafer if _kapitel(lagrum) in omfattning.kapitel]
    rader = Counter((rad.kalla, rad.lagrum) for rad in karta.rader)
    fel += [f"{namn} saknar {kalla} {lagrum}." for kalla, lagrum in forvantade if (kalla, lagrum) not in rader]
    fel += [f"{namn} har {kalla} {lagrum} mer än en gång." for (kalla, lagrum), antal in rader.items() if antal > 1]
    fel += [
        f"{namn}: {kalla} {lagrum} ingår inte i kartans omfattning eller källans paragrafindelning."
        for kalla, lagrum in rader
        if (kalla, lagrum) not in set(forvantade)
    ]
    fel += [rad_fel for rad in karta.rader for rad_fel in _kartrad(regelbas, paket, namn, rad)]
    pa_kartan = {krav_id for rad in karta.rader for krav_id in rad.krav}
    fel += [f"{namn}: kravet {krav_id} i paketet står inte på kartan." for krav_id in paket.krav if krav_id not in pa_kartan]
    return fel


def _kartrad(regelbas: Regelbas, paket: Regelpaket, namn: str, rad: Kartrad) -> list[str]:
    plats = f"{namn}, {rad.kalla} {rad.lagrum}"
    if rad.krav and rad.ej_tillamplig:
        return [f"{plats}: ange antingen krav eller ej_tillamplig, inte båda."]
    fel = []
    for krav_id in rad.krav:
        krav = regelbas.krav.get(krav_id)
        if krav is None or krav_id not in paket.krav:
            fel.append(f"{plats}: kravet {krav_id} finns inte i regelpaketet.")
        elif (krav.kalla, krav.lagrum) != (rad.kalla, rad.lagrum):
            fel.append(f"{plats}: kravet {krav_id} gäller {krav.kalla} {krav.lagrum}.")
    return fel


def _sakkunnig(regelbas: Regelbas) -> list[str]:
    """Status verifierad ska ha granskare, datum och samma kontrollsumma som innehållet har nu."""
    poster = [(krav.id, krav.sakkunnig, regelbas.kravets_innehallssumma(krav.id)) for krav in regelbas.krav.values()] + [
        (f"Paragrafkartan för {paket.id}", paket.paragrafkarta.sakkunnig, regelbas.kartans_innehallssumma(paket.id))
        for paket in regelbas.regelpaket.values()
    ]
    fel = []
    for namn, sakkunnig, summa in poster:
        if sakkunnig.status != "verifierad":
            continue
        if not sakkunnig.av or sakkunnig.datum is None:
            fel.append(f"{namn}: status verifierad kräver att av och datum är ifyllda.")
        if sakkunnig.kontrollsumma != summa:
            fel.append(
                f"{namn}: innehållet har ändrats efter sakkunniggranskningen. Sätt status till ändras, "
                f"eller låt en sakkunnig granska igen och ange kontrollsumman {summa}."
            )
    return fel


def _matris(regelbas: Regelbas) -> list[str]:
    antal = Counter((rad.sannolikhet, rad.konsekvens) for rad in regelbas.metod.riskmatris)
    return [
        f"Riskmatrisen ska ha exakt en rad för {sannolikhet} sannolikhet och {konsekvens} konsekvens, "
        f"har {antal[(sannolikhet, konsekvens)]}."
        for sannolikhet, konsekvens in product(SANNOLIKHETER, KONSEKVENSER)
        if antal[(sannolikhet, konsekvens)] != 1
    ]
```

- [ ] **Step 4: Kör testet**

Run: `.venv/bin/pytest tester/regelkontrakt/test_validering_regelbas.py -v`
Expected: alla tester passerar.

- [ ] **Step 5: Commit**

```bash
git add src/riskanalys/regelverk/validering.py tester/regelkontrakt/test_validering_regelbas.py
git commit -m "feat: validering av korsreferenser och villkor i regelbasen"
```

---

### Task 7: Datumstyrt urval av krav och lydelser

**Files:**
- Create: `src/riskanalys/regelverk/urval.py`
- Test: `tester/regelkontrakt/test_urval.py`

**Interfaces:**
- Consumes: `Regelbas`, `Krav`, `Lydelse`, `Regelpaket`, `RiskanalysFel`, `Faltvarde`, `Kunskap`, `Sanning`, `tolka_villkor`, `utvardera`, fixturerna `minimal_regelbas`, `minimal_filer`, `skriv_minimal_regelbas`.
- Produces:
  - `UrvalsFel(RiskanalysFel)`.
  - `ValtKrav(krav: Krav, lydelse: Lydelse)`, `VantandeAndring(krav_id: str, avsnitt: tuple[str, ...], lydelse: Lydelse)`.
  - `Urval(regelpaket: Regelpaket, datum: date, lan: str, krav: tuple[ValtKrav, ...], tjanster: tuple[str, ...])`.
  - `lydelse_galler(lydelse: Lydelse, datum: date) -> bool`.
  - `valj(regelbas: Regelbas, paket_id: str, datum: date, lan: str) -> Urval`.
  - `vantande_andringar(regelbas: Regelbas, urval: Urval) -> tuple[VantandeAndring, ...]`, sorterade på (ikraft, krav-ID).
  - `beskriv_vantande(andring: VantandeAndring) -> str`.
  - `kravet_galler(regelbas: Regelbas, krav: Krav, varden: dict[str, Faltvarde]) -> bool`.

Regler (spec 6.4): en lydelse gäller när `ikraft ≤ datum < upphor`. Ett krav med egna datum gäller bara inom dem. En källa med `geografi` gäller bara i de länen; en källa utan geografi gäller i hela landet. Två giltiga lydelser för samma krav samma dag är ett fel i regelbasen.

Urvalet görs innan byråns uppgifter är kända och tar därför med alla krav i paketet. Om ett krav gäller just den här byrån avgörs av `kravet_galler` med kravets `galler_om`. Är svaret okänt räknas kravet som gällande, eftersom ett krav som felaktigt hoppas över är värre än ett som granskas i onödan. Granskningen (Task 18) och fastställelsegrinden (Task 20) använder funktionen.

- [ ] **Step 1: Skriv det felande testet `tester/regelkontrakt/test_urval.py`**

```python
from datetime import date, timedelta

import pytest

from riskanalys.regelverk.laddning import ladda_regelbas
from riskanalys.regelverk.urval import UrvalsFel, beskriv_vantande, kravet_galler, valj, vantande_andringar
from riskanalys.regelverk.villkor import Faltvarde, Kunskap

GRANS = date(2026, 11, 20)
VG = "Västra Götaland"


def _ny_lydelse(minimal_filer, **andringar):
    """En kopia av LYD-1 med ändrade fält. Texten är densamma, så LYD-1:s textfil kan återanvändas."""
    return {**minimal_filer["lydelser.yaml"][0], **andringar}


@pytest.fixture
def tva_lydelser(tmp_path, skriv_minimal_regelbas, minimal_filer):
    """KRV-1 med en lydelse som upphör och en som träder i kraft vid GRANS."""
    lydelser = [_ny_lydelse(minimal_filer, upphor=GRANS), _ny_lydelse(minimal_filer, id="LYD-2", ikraft=GRANS)]
    krav = [{**minimal_filer["krav/test.yaml"][0], "lydelser": ["LYD-1", "LYD-2"]}]
    paket = {**minimal_filer["regelpaket/test.yaml"], "lan": [VG, "Stockholm"]}
    rot = skriv_minimal_regelbas(
        tmp_path / "rb",
        {
            "lydelser.yaml": lydelser,
            "lydelsetexter/LYD-2.txt": minimal_filer["lydelsetexter/LYD-1.txt"],
            "krav/test.yaml": krav,
            "regelpaket/test.yaml": paket,
        },
    )
    return ladda_regelbas(rot)


def test_dagen_fore_gransen_galler_den_gamla_lydelsen(tva_lydelser):
    urval = valj(tva_lydelser, "RP-1", GRANS - timedelta(days=1), VG)
    assert [(valt.krav.id, valt.lydelse.id) for valt in urval.krav] == [("KRV-1", "LYD-1")]


def test_samma_dag_som_gransen_galler_den_nya_lydelsen(tva_lydelser):
    urval = valj(tva_lydelser, "RP-1", GRANS, VG)
    assert [(valt.krav.id, valt.lydelse.id) for valt in urval.krav] == [("KRV-1", "LYD-2")]


def test_fore_forsta_lydelsen_finns_inget_krav(tva_lydelser):
    assert valj(tva_lydelser, "RP-1", date(2024, 6, 30), VG).krav == ()


def test_overlappande_lydelser_ger_fel(tmp_path, skriv_minimal_regelbas, minimal_filer):
    lydelser = [*minimal_filer["lydelser.yaml"], _ny_lydelse(minimal_filer, id="LYD-2", ikraft=GRANS)]
    krav = [{**minimal_filer["krav/test.yaml"][0], "lydelser": ["LYD-1", "LYD-2"]}]
    ersattningar = {
        "lydelser.yaml": lydelser,
        "lydelsetexter/LYD-2.txt": minimal_filer["lydelsetexter/LYD-1.txt"],
        "krav/test.yaml": krav,
    }
    regelbas = ladda_regelbas(skriv_minimal_regelbas(tmp_path / "rb", ersattningar))
    with pytest.raises(UrvalsFel, match="flera giltiga lydelser"):
        valj(regelbas, "RP-1", GRANS, VG)


def test_kravets_egna_datum_begransar_urvalet(tmp_path, skriv_minimal_regelbas, minimal_filer):
    krav = [{**minimal_filer["krav/test.yaml"][0], "upphor": date(2025, 1, 1)}]
    regelbas = ladda_regelbas(skriv_minimal_regelbas(tmp_path / "rb", {"krav/test.yaml": krav}))
    assert len(valj(regelbas, "RP-1", date(2024, 12, 31), VG).krav) == 1
    assert valj(regelbas, "RP-1", date(2025, 1, 1), VG).krav == ()


def test_kalla_med_geografi_galler_bara_i_sina_lan(tva_lydelser):
    assert valj(tva_lydelser, "RP-1", GRANS, "Stockholm").krav == ()


def test_okant_regelpaket_ger_fel_med_tillgangliga_paket(minimal_regelbas):
    with pytest.raises(UrvalsFel, match="RP-SAKNAS finns inte. Tillgängliga: RP-1"):
        valj(minimal_regelbas, "RP-SAKNAS", GRANS, VG)


def test_lan_utanfor_paketet_ger_fel(minimal_regelbas):
    with pytest.raises(UrvalsFel, match="gäller inte Skåne"):
        valj(minimal_regelbas, "RP-1", GRANS, "Skåne")


def test_urvalet_tar_med_paketets_tjanster(minimal_regelbas):
    assert valj(minimal_regelbas, "RP-1", GRANS, VG).tjanster == ("T-1",)


def test_vantande_andring_visas_fore_gransen(tva_lydelser):
    urval = valj(tva_lydelser, "RP-1", GRANS - timedelta(days=1), VG)
    andringar = vantande_andringar(tva_lydelser, urval)
    assert [(a.krav_id, a.avsnitt, a.lydelse.id) for a in andringar] == [("KRV-1", ("D-ARB.1",), "LYD-2")]


def test_inga_vantande_andringar_samma_dag_som_gransen(tva_lydelser):
    urval = valj(tva_lydelser, "RP-1", GRANS, VG)
    assert vantande_andringar(tva_lydelser, urval) == ()


def test_beskrivning_av_vantande_andring(tva_lydelser):
    urval = valj(tva_lydelser, "RP-1", GRANS - timedelta(days=1), VG)
    (andring,) = vantande_andringar(tva_lydelser, urval)
    assert beskriv_vantande(andring) == "KRV-1 (avsnitt D-ARB.1) får ny lydelse av 2 kap. 1 § från 2026-11-20."


def _med_tillamplighet(tmp_path, skriv_minimal_regelbas, minimal_filer, galler_om):
    krav = [{**minimal_filer["krav/test.yaml"][0], "galler_om": galler_om}]
    return ladda_regelbas(skriv_minimal_regelbas(tmp_path / "rb", {"krav/test.yaml": krav}))


def test_krav_utan_villkor_galler_alltid(minimal_regelbas):
    assert kravet_galler(minimal_regelbas, minimal_regelbas.krav["KRV-1"], {})


@pytest.mark.parametrize(
    ("varden", "vantat"),
    [
        ({"P-A": Faltvarde(Kunskap.KAND, 0.3)}, True),
        ({"P-A": Faltvarde(Kunskap.KAND, 0.1)}, False),
        ({}, True),
    ],
)
def test_tillamplighet_foljer_villkoret_och_okant_raknas_som_att_kravet_galler(
    tmp_path, skriv_minimal_regelbas, minimal_filer, varden, vantat
):
    regelbas = _med_tillamplighet(
        tmp_path, skriv_minimal_regelbas, minimal_filer, {"falt": "P-A", "op": ">=", "varde": 0.2}
    )
    assert kravet_galler(regelbas, regelbas.krav["KRV-1"], varden) is vantat
```

- [ ] **Step 2: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/regelkontrakt/test_urval.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.regelverk.urval'`.

- [ ] **Step 3: Skriv `src/riskanalys/regelverk/urval.py`**

```python
"""Datumstyrt urval av krav och paragraflydelser (spec 6.4) och kravens tillämplighet."""

from dataclasses import dataclass
from datetime import date

from riskanalys.fel import RiskanalysFel
from riskanalys.regelverk.modeller import Krav, Lydelse, Regelbas, Regelpaket
from riskanalys.regelverk.villkor import Faltvarde, Sanning, tolka_villkor, utvardera


class UrvalsFel(RiskanalysFel):
    """Regelpaket, län eller datum ger inget entydigt urval."""


@dataclass(frozen=True)
class ValtKrav:
    krav: Krav
    lydelse: Lydelse


@dataclass(frozen=True)
class VantandeAndring:
    krav_id: str
    avsnitt: tuple[str, ...]
    lydelse: Lydelse


@dataclass(frozen=True)
class Urval:
    regelpaket: Regelpaket
    datum: date
    lan: str
    krav: tuple[ValtKrav, ...]
    tjanster: tuple[str, ...]


def lydelse_galler(lydelse: Lydelse, datum: date) -> bool:
    return lydelse.ikraft <= datum and (lydelse.upphor is None or datum < lydelse.upphor)


def valj(regelbas: Regelbas, paket_id: str, datum: date, lan: str) -> Urval:
    """Väljer de krav och lydelser i ett regelpaket som gäller ett visst datum i ett visst län."""
    paket = _paket(regelbas, paket_id, lan)
    valda = (_valt_krav(regelbas, regelbas.krav[krav_id], datum, lan) for krav_id in paket.krav)
    return Urval(
        regelpaket=paket,
        datum=datum,
        lan=lan,
        krav=tuple(valt for valt in valda if valt is not None),
        tjanster=paket.tjanster,
    )


def vantande_andringar(regelbas: Regelbas, urval: Urval) -> tuple[VantandeAndring, ...]:
    """Lydelser i paketets krav som ännu inte trätt i kraft vid urvalets datum."""
    andringar = [
        VantandeAndring(krav.id, krav.uppfylls_i, regelbas.lydelser[lydelse_id])
        for krav in (regelbas.krav[krav_id] for krav_id in urval.regelpaket.krav)
        if _galler_i_lan(regelbas, krav, urval.lan)
        for lydelse_id in krav.lydelser
        if regelbas.lydelser[lydelse_id].ikraft > urval.datum
    ]
    return tuple(sorted(andringar, key=lambda andring: (andring.lydelse.ikraft, andring.krav_id)))


def beskriv_vantande(andring: VantandeAndring) -> str:
    return (
        f"{andring.krav_id} (avsnitt {', '.join(andring.avsnitt)}) får ny lydelse av "
        f"{andring.lydelse.lagrum} från {andring.lydelse.ikraft.isoformat()}."
    )


def kravet_galler(regelbas: Regelbas, krav: Krav, varden: dict[str, Faltvarde]) -> bool:
    """Om kravet gäller byrån enligt galler_om. Ett okänt utfall räknas som att kravet gäller."""
    utfall = utvardera(tolka_villkor(krav.galler_om, regelbas.faltdefinitioner()), varden)
    return utfall.sanning is not Sanning.FALSKT


def _paket(regelbas: Regelbas, paket_id: str, lan: str) -> Regelpaket:
    if paket_id not in regelbas.regelpaket:
        tillgangliga = ", ".join(sorted(regelbas.regelpaket))
        raise UrvalsFel(f"Regelpaketet {paket_id} finns inte. Tillgängliga: {tillgangliga}.")
    paket = regelbas.regelpaket[paket_id]
    if lan not in paket.lan:
        raise UrvalsFel(f"Regelpaketet {paket_id} gäller inte {lan}. Det gäller: {', '.join(paket.lan)}.")
    return paket


def _valt_krav(regelbas: Regelbas, krav: Krav, datum: date, lan: str) -> ValtKrav | None:
    if not _krav_galler(krav, datum) or not _galler_i_lan(regelbas, krav, lan):
        return None
    giltiga = [regelbas.lydelser[i] for i in krav.lydelser if lydelse_galler(regelbas.lydelser[i], datum)]
    if len(giltiga) > 1:
        raise UrvalsFel(
            f"{krav.id} har flera giltiga lydelser {datum.isoformat()}: "
            f"{', '.join(lydelse.id for lydelse in giltiga)}. Rätta datumen i regelbas/lydelser.yaml."
        )
    return ValtKrav(krav, giltiga[0]) if giltiga else None


def _krav_galler(krav: Krav, datum: date) -> bool:
    efter_start = krav.ikraft is None or krav.ikraft <= datum
    fore_slut = krav.upphor is None or datum < krav.upphor
    return efter_start and fore_slut


def _galler_i_lan(regelbas: Regelbas, krav: Krav, lan: str) -> bool:
    geografi = regelbas.kallor[krav.kalla].geografi
    return not geografi or lan in geografi
```

- [ ] **Step 4: Kör testet**

Run: `.venv/bin/pytest tester/regelkontrakt/test_urval.py -v`
Expected: alla tester passerar.

- [ ] **Step 5: Commit**

```bash
git add src/riskanalys/regelverk/urval.py tester/regelkontrakt/test_urval.py
git commit -m "feat: datumstyrt urval av krav och paragraflydelser"
```

---
### Task 8: Regelbas v0.1.0 och kommandot `regelbas validera`

**Files:**
- Create: `regelbas/version.yaml`, `regelbas/falt.yaml`, `regelbas/kallor.yaml`, `regelbas/lydelser.yaml`
- Create: `regelbas/lydelsetexter/LYD-LSF-2-1-2024-07-01.txt`, `LYD-LSF-2-2-2024-07-01.txt`, `LYD-LSF-2-3-2024-07-01.txt`
- Create: `regelbas/krav/allman_riskbedomning.yaml`
- Create: `regelbas/kataloger/hot.yaml`, `sarbarheter.yaml`, `kontroller.yaml`, `tjanster.yaml`, `bristmonster.yaml`
- Create: `regelbas/tillatelselistor.yaml`, `regelbas/beslutstabeller/metod.yaml`, `regelbas/regelpaket/redovisning-vg.yaml`
- Create: `src/riskanalys/cli.py`
- Create: `src/riskanalys/kommandon/__init__.py`
- Create: `src/riskanalys/kommandon/regelbas_kommando.py`
- Modify: `tester/conftest.py` (lägg till `REPO_REGELBAS` och fixturen `regelbas`)
- Test: `tester/regelkontrakt/test_regelbas_v0.py`, `tester/enhet/test_cli.py`

**Interfaces:**
- Consumes: `ladda_regelbas`, `STANDARD_REGELBAS`, `RegelbasFel`, `validera`, `valj`, `UrvalsFel`, `RiskanalysFel`.
- Produces:
  - Repots regelbas v0.1.0 med regelpaketet `RP-RED-VG`, tjänsten `T-RED-01`, kraven `KRV-LSF-001`–`KRV-LSF-006`, bristmönstren `B-01`–`B-29` och tillåtelselistan `risk_per_tjanst`.
  - `cli.KOMMANDON: list[ModuleType]`, `cli.main(argv: list[str] | None = None) -> int`. Varje kommandomodul har `lagg_till(underparsers: Any) -> None` som registrerar underkommandon med `set_defaults(kor=funktion)`, där `funktion(args: argparse.Namespace) -> int`.
  - `kommandon.regelbasargument(parser: argparse.ArgumentParser) -> None` (lägger till `--regelbas`), `kommandon.ladda_giltig_regelbas(rot: Path) -> Regelbas`.
  - Kommandona `regelbas validera` (visar också hur stor del av varje paragrafkarta som är hanterad) och `regelbas summor` (innehållssummorna för krav och paragrafkartor, som en sakkunnig skriver in i `sakkunnig.kontrollsumma` efter att ha verifierat innehållet).
  - Fixtur `regelbas` (sessionsomfång) och konstanten `REPO_REGELBAS` i `tester/conftest.py`.
- Avsnitt som kraven pekar på: `D-ARB.1`, `D-ARB.3`, `D-ARB.4`, `D-ARB.5`, `D-ARB.6` (uppfylls av `D-ARB.6.1`, `D-ARB.6.2` och så vidare) och `D-ARB.10`.

Regelbasen i M1 är medvetet liten: en tjänst, ett regelpaket och de sex krav i föreskrifternas 2 kap. 1–3 §§ som rör den allmänna riskbedömningen. Kravtexterna är sammanfattningar och har sakkunnigstatus `ej_granskad`. Paragraftexterna i `lydelsetexter/` är däremot ordagranna avskrifter ur 14FS 2024:11, med avstavningen i PDF:en borttagen. Alla sex krav gäller varje verksamhetsutövare under föreskrifterna och har därför `galler_om: {alla: []}`. Föreskrifternas paragrafindelning (7 kapitel, 31 paragrafer) står i källan. Paragrafkartan täcker 2 kap.: 1–3 §§ är kopplade till kraven, och 4–12 §§ (riskbedömning av kunder och rutiner) är ännu inte hanterade. Kartan är därför giltig men ofullständig, och den stoppar fastställelsen tills M2 lagt in de kraven. Gränsvärdena i sårbarheterna är `metodval`. Källornas URL:er och kontrollsummor för hela källdokument preciseras i M2.

- [ ] **Step 1: Skriv det felande testet `tester/regelkontrakt/test_regelbas_v0.py`**

```python
import json
from collections import Counter
from datetime import date
from pathlib import Path

import pytest

from riskanalys.regelverk.laddning import lydelsetextens_kontrollsumma
from riskanalys.regelverk.urval import UrvalsFel, valj
from riskanalys.regelverk.validering import validera

REPO_REGELBAS = Path(__file__).resolve().parents[2] / "regelbas"
TILLSYNSFALL = REPO_REGELBAS.parent / "docs" / "research" / "typfall" / "tillsyn-2026.json"
VG = "Västra Götaland"
KRAV = [f"KRV-LSF-{nummer:03d}" for nummer in range(1, 7)]


def test_repots_regelbas_ar_giltig(regelbas):
    assert validera(regelbas) == []
    assert regelbas.version == "0.1.0"


def test_inget_krav_ar_markt_som_sakkunniggranskat(regelbas):
    assert {krav.sakkunnig.status for krav in regelbas.krav.values()} == {"ej_granskad"}
    assert {paket.paragrafkarta.sakkunnig.status for paket in regelbas.regelpaket.values()} == {"ej_granskad"}


def test_paragrafindelningen_for_foreskrifterna(regelbas):
    paragrafer = regelbas.kallor["SRC-14FS-2024-11"].paragrafer
    per_kapitel = Counter(lagrum.split(" kap.")[0] for lagrum in paragrafer)
    assert per_kapitel == {"1": 2, "2": 12, "3": 7, "4": 1, "5": 2, "6": 4, "7": 3}


def test_paragrafkartan_tacker_2_kap_och_visar_vad_som_saknas(regelbas):
    karta = regelbas.regelpaket["RP-RED-VG"].paragrafkarta
    assert [rad.lagrum for rad in karta.rader] == [f"2 kap. {nummer} §" for nummer in range(1, 13)]
    assert [rad.lagrum for rad in karta.rader if rad.hanterad] == ["2 kap. 1 §", "2 kap. 2 §", "2 kap. 3 §"]
    assert len(karta.ohanterade()) == 9
    assert karta.galler(date(2026, 11, 1))


def test_varje_lydelse_har_text_med_kontrollsumma(regelbas):
    for lydelse_id, lydelse in regelbas.lydelser.items():
        text = (REPO_REGELBAS / "lydelsetexter" / f"{lydelse_id}.txt").read_text(encoding="utf-8")
        assert lydelsetextens_kontrollsumma(text) == lydelse.text_kontrollsumma


def test_lydelsen_av_2_kap_3_kraver_arlig_utvardering_med_datum(regelbas):
    text = (REPO_REGELBAS / "lydelsetexter" / "LYD-LSF-2-3-2024-07-01.txt").read_text(encoding="utf-8")
    assert "minst en gång per år" in text
    assert "Datum för utvärdering och eventuell uppdatering ska framgå" in " ".join(text.split())


def test_varje_krav_har_tillamplighet_och_belagg(regelbas):
    assert {krav.id: krav.galler_om for krav in regelbas.krav.values()} == {krav_id: {"alla": []} for krav_id in KRAV}
    assert all(krav.belagg for krav in regelbas.krav.values())
    assert regelbas.krav["KRV-LSF-006"].belagg == ("dokument", "datum")


def test_bristmonsterkatalogen_ar_komplett(regelbas):
    assert sorted(regelbas.bristmonster) == [f"B-{nummer:02d}" for nummer in range(1, 30)]
    assert regelbas.bristmonster["B-01"].allvar == "blockerande"


def test_automatiserade_bristmonster(regelbas):
    automatiserade = {post.id for post in regelbas.bristmonster.values() if post.automatiserad}
    assert automatiserade == {"B-04", "B-12", "B-16"}


def test_tillsynsfallens_bristmonster_finns_i_katalogen(regelbas):
    """Varje bristmönster som tillsynsfallen hänvisar till ska finnas i regelbasen (research 09)."""
    fall = json.loads(TILLSYNSFALL.read_text(encoding="utf-8"))
    refererade = {
        monster for post in fall["fall"] for fynd in post["forvantade_fynd"] for monster in fynd["bristmonster"]
    }
    assert len(refererade) == 18
    assert refererade <= set(regelbas.bristmonster)


def test_riskmatrisen(regelbas):
    matris = {(rad.sannolikhet, rad.konsekvens): rad.risk for rad in regelbas.metod.riskmatris}
    assert matris[("medel", "betydande")] == "måttlig"
    assert matris[("hög", "betydande")] == "hög"
    assert matris[("låg", "allvarlig")] == "måttlig"
    assert matris[("hög", "allvarlig")] == "mycket hög"


def test_tillatelselistan_innehaller_inga_personuppgifter(regelbas):
    lista = regelbas.tillatelselistor["risk_per_tjanst"]
    assert not any(regelbas.falt[falt_id].personuppgift for falt_id in lista.falt)
    assert "P-ROLL.ffr_namn" not in lista.falt


def test_urval_for_vastra_gotaland(regelbas):
    urval = valj(regelbas, "RP-RED-VG", date(2026, 11, 1), VG)
    assert [valt.krav.id for valt in urval.krav] == KRAV
    assert urval.tjanster == ("T-RED-01",)


def test_foreskrifterna_galler_inte_dagen_fore_ikrafttradandet(regelbas):
    assert valj(regelbas, "RP-RED-VG", date(2024, 6, 30), VG).krav == ()


def test_foreskrifterna_galler_samma_dag_som_ikrafttradandet(regelbas):
    assert [valt.krav.id for valt in valj(regelbas, "RP-RED-VG", date(2024, 7, 1), VG).krav] == KRAV


def test_paketet_galler_inte_stockholm(regelbas):
    with pytest.raises(UrvalsFel, match="gäller inte Stockholm"):
        valj(regelbas, "RP-RED-VG", date(2026, 11, 1), "Stockholm")
```

- [ ] **Step 2: Lägg till fixturen `regelbas` i `tester/conftest.py`**

Lägg till `from pathlib import Path` bland importerna överst i filen. Lägg sedan till följande sist i filen:

```python
REPO_REGELBAS = Path(__file__).resolve().parents[1] / "regelbas"


@pytest.fixture(scope="session")
def regelbas():
    """Repots riktiga regelbas. Får inte ändras av tester."""
    from riskanalys.regelverk.laddning import ladda_regelbas

    return ladda_regelbas(REPO_REGELBAS)
```

- [ ] **Step 3: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/regelkontrakt/test_regelbas_v0.py -v`
Expected: FAIL med `RegelbasFel: Regelbasen har fel: - Regelbasmappen .../regelbas finns inte.`

- [ ] **Step 4: Skriv `regelbas/version.yaml`**

```yaml
regelbas_version: "0.1.0"
```

- [ ] **Step 5: Skriv `regelbas/falt.yaml`**

```yaml
# Fältregister. Varje uppgift i byråprofilen har ett fält med typ.
- id: P-ORG.namn
  typ: text
  fraga: Vad heter byrån?
  varfor: Den allmänna riskbedömningen ska avse den egna verksamheten.
- id: P-ORG.antal_anstallda
  typ: heltal
  kritisk: true
  smagrupp: true
  fraga: Hur många personer arbetar på byrån, inklusive ägare?
  varfor: Storleken påverkar hur omfattande riskbedömningen och rutinerna ska vara.
- id: P-ORG.verksamhetsstallen
  typ: heltal
  kritisk: true
  fraga: På hur många orter eller kontor bedriver byrån verksamhet?
  varfor: Fler verksamhetsställen ger fler kanaler och kräver tydligare ansvarsfördelning.
- id: P-ROLL.ffr_namn
  typ: text
  personuppgift: true
  kritisk: true
  fraga: Vem utövar funktionen för regelefterlevnad?
  varfor: Ansvaret ska framgå av dokumentationen. Namnet skickas aldrig till AI.
- id: P-TJ.T-RED-01.erbjuds
  typ: bool
  fraga: Erbjuder byrån löpande bokföring?
  varfor: Varje tjänst som erbjuds ska identifieras och bedömas för sig (14FS 2024:11 2 kap. 2 §).
- id: P-KUND.andel_riskbransch
  typ: andel
  fraga: Hur stor andel av kunderna finns i branscher med förhöjd risk enligt den nationella riskbedömningen, till exempel bygg, restaurang, städ och transport?
  varfor: Kunder är en sårbarhet som särskilt ska beaktas (14FS 2024:11 2 kap. 2 §).
- id: P-KUND.andel_kontant
  typ: andel
  fraga: Hur stor andel av kunderna har en betydande kontanthantering?
  varfor: Kontanter gör det svårare att spåra pengarnas ursprung.
- id: P-KANAL.andel_digitalt_underlag
  typ: andel
  fraga: Hur stor andel av kunderna lämnar sitt underlag digitalt, till exempel via app eller e-post, utan personligt möte?
  varfor: Distributionskanaler är en sårbarhet som särskilt ska beaktas (14FS 2024:11 2 kap. 2 §).
- id: P-KANAL.bankdata_andel
  typ: andel
  fraga: För hur stor andel av kunderna har byrån direkt tillgång till bankdata, till exempel bankfil eller bankkoppling?
  varfor: Utan bankdata kan byrån inte stämma av underlaget mot verkliga transaktioner.
- id: P-VERK.juniora_konsulter
  typ: bool
  fraga: Arbetar konsulter med mindre än två års erfarenhet självständigt mot kunder?
  varfor: Verksamhetsspecifika omständigheter ska beaktas (14FS 2024:11 2 kap. 2 §).
- id: P-KONTROLL.C-07.utformning
  typ: val
  val: [finns, saknas]
  fraga: Finns bankavstämning mot underlag beskriven i byråns rutiner?
  varfor: En kontroll sänker bara risken om den finns i rutinerna.
- id: P-KONTROLL.C-07.genomforande
  typ: val
  val: [belagt, ej_belagt]
  fraga: Kan byrån belägga att bankavstämningen görs, till exempel med signerade avstämningar?
  varfor: En kontroll sänker bara risken om det går att visa att den genomförs.
```

- [ ] **Step 6: Skriv `regelbas/kallor.yaml`**

```yaml
- id: SRC-PTL
  titel: Lag (2017:630) om åtgärder mot penningtvätt och finansiering av terrorism
  typ: lag
  utgivare: Riksdagen
  url: https://rkrattsbaser.gov.se/sfst?bet=2017:630
  hamtad: 2026-10-08
  konsoliderad_tom: SFS 2026:1075
- id: SRC-14FS-2024-11
  titel: Länsstyrelsen i Västra Götalands läns föreskrifter och allmänna råd om åtgärder mot penningtvätt och finansiering av terrorism (14FS 2024:11)
  typ: föreskrift
  utgivare: Länsstyrelsen i Västra Götalands län
  url: https://www.lansstyrelsen.se/vastra-gotaland/samhalle/betalning-ekonomi-och-pengar/forhindra-penningtvatt-och-finansiering-av-terrorism.html
  hamtad: 2026-10-06
  beslutad: 2024-05-20
  geografi: [Dalarna, Gävleborg, Halland, Värmland, Västra Götaland, Örebro]
  paragrafer:
    - 1 kap. 1 §
    - 1 kap. 2 §
    - 2 kap. 1 §
    - 2 kap. 2 §
    - 2 kap. 3 §
    - 2 kap. 4 §
    - 2 kap. 5 §
    - 2 kap. 6 §
    - 2 kap. 7 §
    - 2 kap. 8 §
    - 2 kap. 9 §
    - 2 kap. 10 §
    - 2 kap. 11 §
    - 2 kap. 12 §
    - 3 kap. 1 §
    - 3 kap. 2 §
    - 3 kap. 3 §
    - 3 kap. 4 §
    - 3 kap. 5 §
    - 3 kap. 6 §
    - 3 kap. 7 §
    - 4 kap. 1 §
    - 5 kap. 1 §
    - 5 kap. 2 §
    - 6 kap. 1 §
    - 6 kap. 2 §
    - 6 kap. 3 §
    - 6 kap. 4 §
    - 7 kap. 1 §
    - 7 kap. 2 §
    - 7 kap. 3 §
- id: SRC-TS-2026-14
  titel: Erfarenheter från länsstyrelsernas penningtvättstillsyn – fokus den allmänna riskbedömningen, rapport 2026:14
  typ: tillsynsrapport
  utgivare: Länsstyrelserna i Skåne, Stockholms och Västra Götalands län
  url: https://www.lansstyrelsen.se/vastra-gotaland/samhalle/betalning-ekonomi-och-pengar/forhindra-penningtvatt-och-finansiering-av-terrorism.html
  hamtad: 2026-10-06
- id: SRC-VAGL-2025-03
  titel: Information till redovisningskonsulter och skatterådgivare om penningtvätt och finansiering av terrorism (mars 2025)
  typ: vägledning
  utgivare: Samordningsfunktionen mot penningtvätt och finansiering av terrorism
  url: https://polisen.se
  hamtad: 2026-10-06
- id: SRC-NRA-2024-25
  titel: Nationell riskbedömning av penningtvätt och finansiering av terrorism i Sverige 2024/2025
  typ: riskbedömning
  utgivare: Samordningsfunktionen mot penningtvätt och finansiering av terrorism
  url: https://polisen.se/0c34c8d8c94e1a371d8cca457b84fb0a/siteassets/dokument/om-polisen/penningtvatt/nationell-riskbedomning-av-penningtvatt-och-finansiering-av-terrorism-i-sverige-2024_2025.pdf
  hamtad: 2026-10-08
- id: SRC-LST-INGRIPANDEN
  titel: Ingripanden och sanktioner penningtvätt
  typ: beslut
  utgivare: Länsstyrelsen i Stockholms län och Länsstyrelsen i Västra Götalands län
  url: https://www.lansstyrelsen.se/vastra-gotaland/samhalle/betalning-ekonomi-och-pengar/forhindra-penningtvatt-och-finansiering-av-terrorism.html
  hamtad: 2026-09-29
- id: SRC-LST-VG-6045-2026
  titel: Beslut om sanktionsavgift, diarienummer 6045-2026 (redovisningsbyrå, se docs/research/09-tillsynsbeslut-2026.md)
  typ: beslut
  utgivare: Länsstyrelsen i Västra Götalands län
  url: https://www.lansstyrelsen.se/vastra-gotaland/samhalle/betalning-ekonomi-och-pengar/forhindra-penningtvatt-och-finansiering-av-terrorism.html
  hamtad: 2026-10-09
  beslutad: 2026-05-26
- id: SRC-LST-VG-6572-2026
  titel: Beslut om sanktionsavgift, diarienummer 6572-2026 (redovisningsbyrå, se docs/research/09-tillsynsbeslut-2026.md)
  typ: beslut
  utgivare: Länsstyrelsen i Västra Götalands län
  url: https://www.lansstyrelsen.se/vastra-gotaland/samhalle/betalning-ekonomi-och-pengar/forhindra-penningtvatt-och-finansiering-av-terrorism.html
  hamtad: 2026-10-09
  beslutad: 2026-09-10
```

- [ ] **Step 7: Skriv `regelbas/lydelser.yaml`**

```yaml
- id: LYD-LSF-2-1-2024-07-01
  kalla: SRC-14FS-2024-11
  lagrum: 2 kap. 1 §
  ikraft: 2024-07-01
  primarkalla: Västra Götalands läns författningssamling, 14FS 2024:11
  text_kontrollsumma: sha256:0f4688782bf1c983f8f577b967984f0a22e6904dabcc0f07705c64e377af0866
- id: LYD-LSF-2-2-2024-07-01
  kalla: SRC-14FS-2024-11
  lagrum: 2 kap. 2 §
  ikraft: 2024-07-01
  primarkalla: Västra Götalands läns författningssamling, 14FS 2024:11
  text_kontrollsumma: sha256:095c5931cec8543f738dd097fc8f4ae78f7ea076461ac6ddd0ce0b7d8de71e84
- id: LYD-LSF-2-3-2024-07-01
  kalla: SRC-14FS-2024-11
  lagrum: 2 kap. 3 §
  ikraft: 2024-07-01
  primarkalla: Västra Götalands läns författningssamling, 14FS 2024:11
  text_kontrollsumma: sha256:391c8aa5d3b04ccd5dbfc3a4376bb3d29f4dacc40da09bb4495f97094f5ee709
```

- [ ] **Step 7b: Skriv lydelsetexterna**

Texterna är avskrivna ur 14FS 2024:11 (utkom från trycket 2024-05-22). Kopiera dem exakt, tecken för tecken. Kontrollsummorna ovan är beräknade på just dessa texter, och inläsningen vägrar om ett ord skiljer sig.

`regelbas/lydelsetexter/LYD-LSF-2-1-2024-07-01.txt`:

```text
Bestämmelser om innehållet i och omfattningen av verksamhetsutövarens allmänna riskbedömning finns i 2 kap. 1 och 2 §§ lagen (2017:630) om åtgärder mot penningtvätt och finansiering av terrorism.
Verksamhetsutövarens allmänna riskbedömning ska enligt 2 kap. 2 § samma lag vara dokumenterad.
```

`regelbas/lydelsetexter/LYD-LSF-2-2-2024-07-01.txt`:

```text
Verksamhetsutövaren ska i den allmänna riskbedömningen göra följande:
– Identifiera de produkter och tjänster som tillhandahålls i verksamheten.
– Identifiera och analysera de hot som är relevanta för de produkter och tjänster som tillhandahålls i verksamheten. Vid denna bedömning ska verksamhetsutövaren särskilt ta hänsyn till uppgifter som kommer fram vid verksamhetsutövarens rapportering av misstänkta aktiviteter och transaktioner. Verksamhetsutövaren ska också särskilt ta hänsyn till information om tillvägagångssätt för penningtvätt och finansiering av terrorism och andra relevanta uppgifter som myndigheter lämnar.
– Identifiera och analysera de sårbarheter som kan innebära att de produkter och tjänster som tillhandahålls i verksamheten utnyttjas för penningtvätt eller finansiering av terrorism. Vid denna bedömning ska verksamhetsutövaren särskilt beakta vilka kunder och distributionskanaler som finns samt vilka geografiska riskfaktorer som föreligger. Verksamhetsutövaren ska även beakta andra relevanta verksamhetsspecifika omständigheter som kan innebära en sårbarhet för att verksamhetens produkter och tjänster utnyttjas för penningtvätt eller finansiering av terrorism.
– Värdera riskerna som är förenade med de bedömda hoten och sårbarheterna. Verksamhetsutövaren ska motivera angivna risknivåer.
```

`regelbas/lydelsetexter/LYD-LSF-2-3-2024-07-01.txt`:

```text
Verksamhetsutövaren ska utvärdera den allmänna riskbedömningen regelbundet, minst en gång per år, och uppdatera den vid behov.
Den allmänna riskbedömningen ska alltid utvärderas innan verksamhetsutövaren
1. erbjuder nya eller väsentligt förändrade produkter eller tjänster,
2. riktar sig till nya marknader, eller
3. gör andra förändringar som är relevanta för verksamheten.
Verksamhetsutövaren ska dokumentera datum för utvärdering och eventuell uppdatering av den allmänna riskbedömningen. Datum för utvärdering och eventuell uppdatering ska framgå av den allmänna riskbedömningen.
```

Strecken i 2 § är tankstreck (U+2013), som i föreskriften.

- [ ] **Step 8: Skriv `regelbas/krav/allman_riskbedomning.yaml`**

```yaml
# Sammanfattningar av föreskrifternas krav. Sakkunnig granskning sker i M2.
- id: KRV-LSF-001
  kalla: SRC-14FS-2024-11
  lagrum: 2 kap. 1 §
  lydelser: [LYD-LSF-2-1-2024-07-01]
  grund: ska_krav
  text: Den allmänna riskbedömningen ska vara dokumenterad. Innehåll och omfattning följer av 2 kap. 1 och 2 §§ penningtvättslagen.
  galler_om: {alla: []}
  belagg: [dokument]
  uppfylls_i: [D-ARB.1]
- id: KRV-LSF-002
  kalla: SRC-14FS-2024-11
  lagrum: 2 kap. 2 §
  lydelser: [LYD-LSF-2-2-2024-07-01]
  grund: ska_krav
  text: Verksamhetsutövaren ska identifiera de produkter och tjänster som tillhandahålls i verksamheten.
  galler_om: {alla: []}
  belagg: [dokument]
  uppfylls_i: [D-ARB.3]
- id: KRV-LSF-003
  kalla: SRC-14FS-2024-11
  lagrum: 2 kap. 2 §
  lydelser: [LYD-LSF-2-2-2024-07-01]
  grund: ska_krav
  text: Verksamhetsutövaren ska identifiera och analysera de hot som är relevanta för tjänsterna, med särskild hänsyn till egen rapportering av misstänkta aktiviteter och myndigheternas information om tillvägagångssätt.
  galler_om: {alla: []}
  belagg: [dokument]
  uppfylls_i: [D-ARB.4]
- id: KRV-LSF-004
  kalla: SRC-14FS-2024-11
  lagrum: 2 kap. 2 §
  lydelser: [LYD-LSF-2-2-2024-07-01]
  grund: ska_krav
  text: Verksamhetsutövaren ska identifiera och analysera sårbarheter, särskilt kunder, distributionskanaler, geografiska riskfaktorer och andra verksamhetsspecifika omständigheter.
  galler_om: {alla: []}
  belagg: [dokument]
  uppfylls_i: [D-ARB.5]
- id: KRV-LSF-005
  kalla: SRC-14FS-2024-11
  lagrum: 2 kap. 2 §
  lydelser: [LYD-LSF-2-2-2024-07-01]
  grund: ska_krav
  text: Verksamhetsutövaren ska värdera riskerna som är förenade med hoten och sårbarheterna och motivera angivna risknivåer.
  galler_om: {alla: []}
  belagg: [dokument]
  uppfylls_i: [D-ARB.6]
- id: KRV-LSF-006
  kalla: SRC-14FS-2024-11
  lagrum: 2 kap. 3 §
  lydelser: [LYD-LSF-2-3-2024-07-01]
  grund: ska_krav
  text: Den allmänna riskbedömningen ska utvärderas minst en gång per år och före nya tjänster, nya marknader eller andra relevanta förändringar. Datum för utvärdering och uppdatering ska framgå av riskbedömningen.
  galler_om: {alla: []}
  belagg: [dokument, datum]
  uppfylls_i: [D-ARB.10]
```

- [ ] **Step 9: Skriv `regelbas/kataloger/hot.yaml`**

```yaml
- id: H-01
  namn: Osanna och falska fakturor
  beskrivning: Fakturor utan verklig prestation används för att flytta pengar, dölja brottsvinster eller göra felaktiga avdrag. De passerar byrån som vanliga verifikationer.
  kallor: [SRC-VAGL-2025-03, SRC-NRA-2024-25]
- id: H-02
  namn: Brottsvinster redovisas som intäkter
  beskrivning: Pengar från brott blandas in i en lagligt bedriven verksamhet och redovisas som försäljning, så att de ser legala ut.
  kallor: [SRC-VAGL-2025-03, SRC-NRA-2024-25]
- id: H-03
  namn: Oförklarade in- och utflöden
  beskrivning: Insättningar, uttag och överföringar saknar underlag eller affärsmässig förklaring och kan dölja penningtvätt eller finansiering av terrorism.
  galler_tf: true
  kallor: [SRC-VAGL-2025-03]
```

- [ ] **Step 10: Skriv `regelbas/kataloger/sarbarheter.yaml`**

```yaml
# Gränsvärdena är metodval och prövas i modellvalideringen (M2).
- id: S-KUND-01
  namn: Kunder i branscher med förhöjd risk
  omrade: kund
  grund: metodval
  villkor: {falt: P-KUND.andel_riskbransch, op: ">=", varde: 0.2}
  effekt: {sannolikhet: 1}
  kallor: [SRC-NRA-2024-25, SRC-TS-2026-14]
- id: S-KUND-02
  namn: Kunder med betydande kontanthantering
  omrade: kund
  grund: metodval
  villkor: {falt: P-KUND.andel_kontant, op: ">=", varde: 0.1}
  effekt: {sannolikhet: 1}
  galler: bada
  kallor: [SRC-PTL, SRC-VAGL-2025-03]
- id: S-KANAL-01
  namn: Digitalt underlag utan tillgång till bankdata
  omrade: kanal
  grund: metodval
  villkor:
    alla:
      - {falt: P-KANAL.andel_digitalt_underlag, op: ">=", varde: 0.5}
      - {falt: P-KANAL.bankdata_andel, op: "<", varde: 0.5}
  effekt: {sannolikhet: 1}
  kallor: [SRC-TS-2026-14]
- id: S-VERK-01
  namn: Juniora konsulter arbetar självständigt
  omrade: verk
  grund: metodval
  villkor: {falt: P-VERK.juniora_konsulter, op: "==", varde: true}
  effekt: {sannolikhet: 1}
  kallor: [SRC-TS-2026-14]
```

- [ ] **Step 11: Skriv `regelbas/kataloger/kontroller.yaml`**

```yaml
- id: C-07
  namn: Bankavstämning mot underlag
  beskrivning: Byrån stämmer av kundens bankkonton mot bokfört underlag och utreder differenser och transaktioner som saknar underlag.
  utformning_falt: P-KONTROLL.C-07.utformning
  genomforande_falt: P-KONTROLL.C-07.genomforande
  kallor: [SRC-TS-2026-14]
```

- [ ] **Step 12: Skriv `regelbas/kataloger/tjanster.yaml`**

```yaml
- id: T-RED-01
  namn: Löpande bokföring
  sektor: redovisning
  beskrivning: Kontering av verifikationer, kund- och leverantörsreskontra, bankavstämning och periodrapporter.
  erbjuds_falt: P-TJ.T-RED-01.erbjuds
  hot: [H-01, H-02, H-03]
  sarbarheter: [S-KUND-01, S-KUND-02, S-KANAL-01, S-VERK-01]
  kontroller: [C-07]
  grund_sannolikhet: medel
  grund_konsekvens: betydande
  grund_tf_sannolikhet: låg
  kallor: [SRC-VAGL-2025-03, SRC-NRA-2024-25]
```

- [ ] **Step 13: Skriv `regelbas/kataloger/bristmonster.yaml`**

```yaml
# Bristmönsterkatalogen. Ersätter tabellen i docs/research/03-tillsyn-och-sanktioner.md.
- {id: B-01, namn: Den allmänna riskbedömningen saknas eller förväxlas med kundbedömning eller rutiner, upptacks: Kontrollera att dokumentet finns och har de fyra obligatoriska delarna., automatiserad: false, allvar: blockerande, grund: tillsynspraxis, kallor: [SRC-TS-2026-14]}
- {id: B-02, namn: Mallen är inte anpassad till verksamheten, upptacks: Låg andel referenser till byråprofilen och hög andel generiska formuleringar., automatiserad: false, allvar: hög, grund: tillsynspraxis, kallor: [SRC-TS-2026-14]}
- {id: B-03, namn: Otillräcklig identifiering och analys av hot och sårbarheter, upptacks: Varje erbjuden tjänst ska ha hot med källa och sårbarheter., automatiserad: false, allvar: hög, grund: tillsynspraxis, kallor: [SRC-TS-2026-14]}
- {id: B-04, namn: Tjänster beskrivs tillsammans utan individuell analys, upptacks: Varje tjänst ska ha eget avsnitt., automatiserad: true, allvar: hög, grund: tillsynspraxis, kallor: [SRC-TS-2026-14]}
- {id: B-05, namn: Fokus på ett eller få hot och nya hot fångas inte upp, upptacks: Jämför hoten mot hotkatalogen och aktuell omvärldsbevakning., automatiserad: false, allvar: medel, grund: tillsynspraxis, kallor: [SRC-TS-2026-14]}
- {id: B-06, namn: Kundkategorier utan förklaring av hur de ökar risken, upptacks: Varje kundkategori ska ha motivering., automatiserad: false, allvar: medel, grund: tillsynspraxis, kallor: [SRC-TS-2026-14]}
- {id: B-07, namn: Nära kundrelationer förbises som sårbarhet, upptacks: Kontrollera att sårbarheten finns med., automatiserad: false, allvar: medel, grund: tillsynspraxis, kallor: [SRC-TS-2026-14]}
- {id: B-08, namn: Distributionskanaler och leveranssätt identifieras inte, upptacks: Kontrollera avsnittet om kanaler., automatiserad: false, allvar: medel, grund: tillsynspraxis, kallor: [SRC-TS-2026-14]}
- {id: B-09, namn: Geografi kopplas bara till sanktionslistor, upptacks: Kontrollera att utlandskopplingar och lokala riskfaktorer analyseras., automatiserad: false, allvar: hög, grund: tillsynspraxis, kallor: [SRC-TS-2026-14]}
- {id: B-10, namn: Påstående om att geografiska risker saknas utan motivering, upptacks: Ingen nivå får anges utan motivering., automatiserad: false, allvar: medel, grund: tillsynspraxis, kallor: [SRC-TS-2026-14]}
- {id: B-11, namn: Verksamhetsspecifika omständigheter saknas, upptacks: Kontrollera avsnittet., automatiserad: false, allvar: medel, grund: tillsynspraxis, kallor: [SRC-TS-2026-14]}
- {id: B-12, namn: Sammantagen risk utan analys av hur nivån nåtts, upptacks: Varje nivå ska ha regelspår och motivering., automatiserad: true, allvar: hög, grund: tillsynspraxis, kallor: [SRC-TS-2026-14]}
- {id: B-13, namn: Alla nivåer låga utan hänsyn till sektorsrisken i den nationella riskbedömningen, upptacks: Jämför med sektorsnivån och kräv motivering vid avvikelse., automatiserad: false, allvar: hög, grund: tillsynspraxis, kallor: [SRC-TS-2026-14]}
- {id: B-14, namn: Källor för hot anges inte, upptacks: Kontrollera källförteckningen., automatiserad: false, allvar: medel, grund: tillsynspraxis, kallor: [SRC-TS-2026-14]}
- {id: B-15, namn: Egen rapportering till Finanspolisen vägs inte in, upptacks: Kontrollera att uppgiften finns i profilen och texten., automatiserad: false, allvar: medel, grund: tillsynspraxis, kallor: [SRC-TS-2026-14]}
- {id: B-16, namn: Datum för utvärdering och uppdatering saknas, upptacks: Kontrollera versionsloggen., automatiserad: true, allvar: hög, grund: tillsynspraxis, kallor: [SRC-TS-2026-14]}
- {id: B-17, namn: Rutinerna saknar koppling till den allmänna riskbedömningen, upptacks: Kontrollera att rutinerna hänvisar till de risker som riskbedömningen pekar ut., automatiserad: false, allvar: medel, grund: tillsynspraxis, kallor: [SRC-LST-INGRIPANDEN]}
- {id: B-18, namn: Det framgår inte hur kundernas riskprofiler följs upp och ändras, upptacks: Kontrollera att rutinerna beskriver när och hur kundens riskprofil följs upp., automatiserad: false, allvar: medel, grund: tillsynspraxis, kallor: [SRC-LST-INGRIPANDEN]}
- {id: B-19, namn: Det står att åtgärder vidtagits men inte hur, upptacks: Kontrollera att varje åtgärd beskrivs med vem som gör vad och när., automatiserad: false, allvar: medel, grund: tillsynspraxis, kallor: [SRC-LST-INGRIPANDEN]}
- {id: B-20, namn: Rutiner för lämplighetsprövning och utbildning saknas, upptacks: Kontrollera att rutinerna finns och att utbildning dokumenteras med innehåll och datum. Myndigheters informationsträffar räcker inte., automatiserad: false, allvar: medel, grund: tillsynspraxis, kallor: [SRC-LST-INGRIPANDEN]}
- {id: B-21, namn: Hänvisning till branschstandard i stället för egna rutiner, upptacks: Kontrollera att rutinerna är byråns egna och inte bara hänvisar till en branschstandard., automatiserad: false, allvar: medel, grund: tillsynspraxis, kallor: [SRC-LST-INGRIPANDEN]}
- {id: B-22, namn: Ansvarig för regelefterlevnad anges utan rutin för hur ansvaret utövas, upptacks: Kontrollera att rutinerna beskriver hur funktionen för regelefterlevnad utövar sitt ansvar., automatiserad: false, allvar: medel, grund: tillsynspraxis, kallor: [SRC-LST-INGRIPANDEN]}
- {id: B-23, namn: "Riskbedömningen är upprättad efter den period den ska gälla, eller tidigare versioner har skrivits över", upptacks: "Kontrollera versionshistoriken och att varje fastställd version är låst och daterad.", automatiserad: false, allvar: hög, grund: tillsynspraxis, kallor: [SRC-LST-VG-6045-2026, SRC-LST-VG-6572-2026]}
- {id: B-24, namn: "Det framgår inte i vilken utsträckning tjänster, kundtyper, kanaler och riskfaktorer förekommer", upptacks: "Kontrollera att profilen har omfattning per tjänst och fördelning per kundtyp, och att texten anger andelar.", automatiserad: false, allvar: hög, grund: tillsynspraxis, kallor: [SRC-LST-VG-6045-2026, SRC-LST-VG-6572-2026]}
- {id: B-25, namn: "Riskfaktorer bedöms var för sig, och samverkan bedöms inte för de kombinationer som faktiskt förekommer", upptacks: "Kontrollera att sammanvägningen hänvisar till konkreta kombinationer av tjänst, kundtyp och kanal.", automatiserad: false, allvar: medel, grund: tillsynspraxis, kallor: [SRC-LST-VG-6572-2026]}
- {id: B-26, namn: "Tjänster med hög risk enligt den nationella riskbedömningen, till exempel bolagsbildning och skatterådgivning, känns inte igen", upptacks: "Kontrollera att tjänstekatalogen frågar efter dem och ger dem hög grundnivå.", automatiserad: false, allvar: hög, grund: tillsynspraxis, kallor: [SRC-LST-VG-6572-2026, SRC-NRA-2024-25]}
- {id: B-27, namn: "Risken sänks med hänvisning till att någon annan gjort kundkännedom, utan stöd i 3 kap. 21–24 §§ PTL", upptacks: "Kontrollera att ingen regel eller text sänker risken för hänvisade kunder.", automatiserad: false, allvar: hög, grund: tillsynspraxis, kallor: [SRC-LST-VG-6572-2026]}
- {id: B-28, namn: "Rutinen medger att kundkännedomsåtgärder helt utelämnas när risken är låg", upptacks: "Kontrollera rutinen för förenklade åtgärder.", automatiserad: false, allvar: hög, grund: tillsynspraxis, kallor: [SRC-LST-VG-6572-2026]}
- {id: B-29, namn: "Bedömningen av politiskt utsatt ställning görs bara för den verkliga huvudmannen", upptacks: "Kontrollera att rutinen omfattar kunden och andra relevanta personer.", automatiserad: false, allvar: medel, grund: tillsynspraxis, kallor: [SRC-LST-VG-6572-2026]}
```

- [ ] **Step 14: Skriv `regelbas/tillatelselistor.yaml`**

```yaml
# Fält som får skickas till AI per avsnittstyp. Personuppgifter får aldrig stå här.
- id: risk_per_tjanst
  falt:
    - P-ORG.antal_anstallda
    - P-KUND.andel_riskbransch
    - P-KUND.andel_kontant
    - P-KANAL.andel_digitalt_underlag
    - P-KANAL.bankdata_andel
    - P-VERK.juniora_konsulter
  undvik: [B-02, B-03, B-04, B-12, B-13, B-24, B-25]
```

- [ ] **Step 15: Skriv `regelbas/beslutstabeller/metod.yaml`**

```yaml
# Riskmetoden. Skalor, steg och matris är metodval (spec 4.6 och 7).
riskmatris:
  - {id: BT-MATRIS-01, sannolikhet: låg, konsekvens: begränsad, risk: låg, grund: metodval, forklaring: Låg sannolikhet och begränsad konsekvens ger låg risk.}
  - {id: BT-MATRIS-02, sannolikhet: låg, konsekvens: betydande, risk: måttlig, grund: metodval, forklaring: Låg sannolikhet och betydande konsekvens ger måttlig risk.}
  - {id: BT-MATRIS-03, sannolikhet: låg, konsekvens: allvarlig, risk: måttlig, grund: metodval, forklaring: Låg sannolikhet och allvarlig konsekvens ger måttlig risk.}
  - {id: BT-MATRIS-04, sannolikhet: medel, konsekvens: begränsad, risk: måttlig, grund: metodval, forklaring: Medelhög sannolikhet och begränsad konsekvens ger måttlig risk.}
  - {id: BT-MATRIS-05, sannolikhet: medel, konsekvens: betydande, risk: måttlig, grund: metodval, forklaring: Medelhög sannolikhet och betydande konsekvens ger måttlig risk.}
  - {id: BT-MATRIS-06, sannolikhet: medel, konsekvens: allvarlig, risk: hög, grund: metodval, forklaring: Medelhög sannolikhet och allvarlig konsekvens ger hög risk.}
  - {id: BT-MATRIS-07, sannolikhet: hög, konsekvens: begränsad, risk: måttlig, grund: metodval, forklaring: Hög sannolikhet och begränsad konsekvens ger måttlig risk.}
  - {id: BT-MATRIS-08, sannolikhet: hög, konsekvens: betydande, risk: hög, grund: metodval, forklaring: Hög sannolikhet och betydande konsekvens ger hög risk.}
  - {id: BT-MATRIS-09, sannolikhet: hög, konsekvens: allvarlig, risk: mycket hög, grund: metodval, forklaring: Hög sannolikhet och allvarlig konsekvens ger mycket hög risk.}
sannolikhet:
  id: BT-SANN-01
  grund: metodval
  forklaring: Sannolikheten utgår från tjänstens grundnivå i katalogen. Varje sårbarhet som gäller höjer den med sin effekt, som högst till hög.
konsekvens:
  id: BT-KONS-01
  grund: metodval
  forklaring: Konsekvensen är tjänstens grundnivå i katalogen.
terrorfinansiering:
  id: BT-TF-01
  grund: metodval
  forklaring: Terrorfinansiering bedöms separat. Sannolikheten utgår från tjänstens grundnivå för terrorfinansiering och höjs av sårbarheter som gäller terrorfinansiering. Konsekvensen är alltid allvarlig.
kvarstaende_ej_belagd:
  id: BT-KVAR-01
  grund: metodval
  forklaring: Om ingen kontroll både finns i rutinerna och är belagd är den kvarstående risken lika med den inneboende risken.
kvarstaende_sankning:
  id: BT-KVAR-02
  grund: metodval
  forklaring: Om minst en kontroll finns i rutinerna och är belagd sänks risken ett steg per tjänst. Hög eller mycket hög inneboende risk blir därmed aldrig lägre än måttlig.
```

- [ ] **Step 16: Skriv `regelbas/regelpaket/redovisning-vg.yaml`**

```yaml
id: RP-RED-VG
namn: Redovisningskonsulter under tillsyn av Länsstyrelsen i Västra Götalands län
sektor: redovisning
lan: [Dalarna, Gävleborg, Halland, Värmland, Västra Götaland, Örebro]
kallor: [SRC-PTL, SRC-14FS-2024-11, SRC-TS-2026-14, SRC-VAGL-2025-03, SRC-NRA-2024-25]
krav: [KRV-LSF-001, KRV-LSF-002, KRV-LSF-003, KRV-LSF-004, KRV-LSF-005, KRV-LSF-006]
tjanster: [T-RED-01]
# Paragrafkartan täcker i M1 bara föreskrifternas 2 kap. Paragraferna 4–12 § hanteras ännu inte
# i regelbasen. Det är avsiktligt synligt: de stoppar fastställelsen tills M2 har lagt in kraven.
paragrafkarta:
  giltig_fran: 2024-07-01
  omfattning:
    - {kalla: SRC-14FS-2024-11, kapitel: [2 kap.]}
  rader:
    - {kalla: SRC-14FS-2024-11, lagrum: 2 kap. 1 §, krav: [KRV-LSF-001]}
    - {kalla: SRC-14FS-2024-11, lagrum: 2 kap. 2 §, krav: [KRV-LSF-002, KRV-LSF-003, KRV-LSF-004, KRV-LSF-005]}
    - {kalla: SRC-14FS-2024-11, lagrum: 2 kap. 3 §, krav: [KRV-LSF-006]}
    - {kalla: SRC-14FS-2024-11, lagrum: 2 kap. 4 §}
    - {kalla: SRC-14FS-2024-11, lagrum: 2 kap. 5 §}
    - {kalla: SRC-14FS-2024-11, lagrum: 2 kap. 6 §}
    - {kalla: SRC-14FS-2024-11, lagrum: 2 kap. 7 §}
    - {kalla: SRC-14FS-2024-11, lagrum: 2 kap. 8 §}
    - {kalla: SRC-14FS-2024-11, lagrum: 2 kap. 9 §}
    - {kalla: SRC-14FS-2024-11, lagrum: 2 kap. 10 §}
    - {kalla: SRC-14FS-2024-11, lagrum: 2 kap. 11 §}
    - {kalla: SRC-14FS-2024-11, lagrum: 2 kap. 12 §}
  sakkunnig:
    status: ej_granskad
```

- [ ] **Step 17: Kör regelbastestet**

Run: `.venv/bin/pytest tester/regelkontrakt/test_regelbas_v0.py -v`
Expected: alla tester passerar. Om valideringen rapporterar fel, rätta YAML-filen som meddelandet pekar på.

- [ ] **Step 18: Skriv det felande testet `tester/enhet/test_cli.py`**

```python
from riskanalys.cli import main


def test_regelbas_validera_godkanner_repots_regelbas(capsys):
    assert main(["regelbas", "validera"]) == 0
    utskrift = capsys.readouterr().out
    assert "Regelbasen är giltig." in utskrift
    assert "Version: 0.1.0" in utskrift
    assert "Krav: 6" in utskrift
    assert "Paragrafkarta RP-RED-VG: 3 av 12 paragrafer hanterade, sakkunnigstatus ej_granskad." in utskrift


def test_regelbas_summor_visar_det_som_ska_signeras(capsys):
    assert main(["regelbas", "summor"]) == 0
    rader = capsys.readouterr().out.splitlines()
    assert len(rader) == 7
    assert rader[0].startswith("KRV-LSF-001 sha256:")
    assert rader[-1].startswith("RP-RED-VG paragrafkarta sha256:")


def test_regelbas_validera_visar_fel_utan_stackspar(tmp_path, skriv_minimal_regelbas, minimal_filer, capsys):
    hot = minimal_filer["kataloger/hot.yaml"]
    hot[0]["kallor"] = ["SRC-SAKNAS"]
    rot = skriv_minimal_regelbas(tmp_path / "rb", {"kataloger/hot.yaml": hot})
    assert main(["regelbas", "validera", "--regelbas", str(rot)]) == 1
    fel = capsys.readouterr().err
    assert fel.startswith("Fel: Regelbasen har fel:")
    assert "H-1: hänvisar till källan SRC-SAKNAS som inte finns." in fel
    assert "Traceback" not in fel


def test_saknad_regelbasmapp_ger_felkod(tmp_path, capsys):
    assert main(["regelbas", "validera", "--regelbas", str(tmp_path / "saknas")]) == 1
    assert "finns inte" in capsys.readouterr().err
```

- [ ] **Step 19: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/enhet/test_cli.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.cli'`.

- [ ] **Step 20: Skriv `src/riskanalys/kommandon/__init__.py`**

```python
"""Underkommandon. Varje modul har lagg_till(underparsers) och kör-funktioner som returnerar en felkod."""

import argparse
from pathlib import Path

from riskanalys.regelverk.laddning import STANDARD_REGELBAS, RegelbasFel, ladda_regelbas
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.validering import validera


def regelbasargument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--regelbas",
        type=Path,
        default=STANDARD_REGELBAS,
        help="Mapp med regelbasen. Standard är repots regelbas.",
    )


def ladda_giltig_regelbas(rot: Path) -> Regelbas:
    """Läser in regelbasen och vägrar om den har fel."""
    regelbas = ladda_regelbas(rot)
    fel = validera(regelbas)
    if fel:
        raise RegelbasFel(fel)
    return regelbas
```

- [ ] **Step 21: Skriv `src/riskanalys/kommandon/regelbas_kommando.py`**

```python
"""riskanalys regelbas validera"""

import argparse
from typing import Any

from riskanalys.kommandon import ladda_giltig_regelbas, regelbasargument
from riskanalys.regelverk.laddning import ladda_regelbas


def lagg_till(underparsers: Any) -> None:
    parser = underparsers.add_parser("regelbas", help="Arbeta med regelbasen.")
    under = parser.add_subparsers(dest="regelbaskommando", required=True, metavar="underkommando")
    validera = under.add_parser("validera", help="Läs in regelbasen och kontrollera att den hänger ihop.")
    regelbasargument(validera)
    validera.set_defaults(kor=kor_validera)
    summor = under.add_parser("summor", help="Visa kontrollsummorna som en sakkunnig signerar.")
    regelbasargument(summor)
    summor.set_defaults(kor=kor_summor)


def kor_validera(args: argparse.Namespace) -> int:
    regelbas = ladda_giltig_regelbas(args.regelbas)
    print("Regelbasen är giltig.")
    print(f"Version: {regelbas.version}")
    print(f"Krav: {len(regelbas.krav)}")
    print(f"Tjänster: {len(regelbas.tjanster)}")
    for paket in regelbas.regelpaket.values():
        karta = paket.paragrafkarta
        hanterade = len(karta.rader) - len(karta.ohanterade())
        print(
            f"Paragrafkarta {paket.id}: {hanterade} av {len(karta.rader)} paragrafer hanterade, "
            f"sakkunnigstatus {karta.sakkunnig.status}."
        )
    print(f"Kontrollsumma: {regelbas.kontrollsumma}")
    return 0


def kor_summor(args: argparse.Namespace) -> int:
    """En sakkunnig som verifierat ett krav eller en karta skriver in summan i sakkunnig.kontrollsumma.

    Regelbasen läses utan validering, eftersom summorna behövs just när en tidigare verifiering slutat gälla.
    """
    regelbas = ladda_regelbas(args.regelbas)
    for krav in regelbas.krav.values():
        print(f"{krav.id} {regelbas.kravets_innehallssumma(krav.id)}")
    for paket in regelbas.regelpaket.values():
        print(f"{paket.id} paragrafkarta {regelbas.kartans_innehallssumma(paket.id)}")
    return 0
```

- [ ] **Step 22: Skriv `src/riskanalys/cli.py`**

```python
"""Kommandoraden: riskanalys <kommando> (spec 12)."""

import argparse
import sys

from riskanalys.fel import RiskanalysFel
from riskanalys.kommandon import regelbas_kommando

KOMMANDON = [regelbas_kommando]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="riskanalys",
        description="Verksamhetsanpassad dokumentation enligt penningtvättsregelverket.",
    )
    underparsers = parser.add_subparsers(dest="kommando", required=True, metavar="kommando")
    for kommando in KOMMANDON:
        kommando.lagg_till(underparsers)
    args = parser.parse_args(argv)
    try:
        return args.kor(args)
    except RiskanalysFel as fel:
        print(f"Fel: {fel}", file=sys.stderr)
        return 1
```

- [ ] **Step 23: Kör alla tester och kommandot för hand**

Run:
```bash
.venv/bin/pytest -v
.venv/bin/riskanalys regelbas validera
```
Expected: alla tester passerar. Kommandot skriver "Regelbasen är giltig." och versionen 0.1.0.

- [ ] **Step 24: Commit**

```bash
git add regelbas src/riskanalys/cli.py src/riskanalys/kommandon tester/conftest.py tester/regelkontrakt/test_regelbas_v0.py tester/enhet/test_cli.py
git commit -m "feat: regelbas v0.1.0 och kommandot regelbas validera"
```

---

### Task 9: Dokumentmodeller och testleverantör

**Files:**
- Create: `src/riskanalys/dokument/__init__.py`
- Create: `src/riskanalys/dokument/modeller.py`
- Create: `src/riskanalys/dokument/leverantor.py`
- Test: `tester/enhet/test_dokumentmodeller.py`, `tester/enhet/test_leverantor.py`

**Interfaces:**
- Consumes: `kontrollsumma.for_text`, `RiskanalysFel`.
- Produces i `dokument/modeller.py`:
  - AI-schemat: `Textstycke(typ: Literal["beskrivning", "analys", "motivering", "scenario"], text: str, referenser: list[str])`, `Oklarhet(fraga: str, saknad_uppgift: str)`, `AvsnittsUtkast(avsnitt: str, stycken: list[Textstycke], oklarheter: list[Oklarhet])`.
  - Underlaget till AI: `UnderlagHot(id, namn, beskrivning)`, `UnderlagSarbarhet(id, namn, galler: Literal["ja", "nej", "okänt"])`, `UnderlagKontroll(id, namn, status)`, `UnderlagUppgift(id, fraga, varde: str, bekraftad: bool)`, `UnderlagBrist(id, namn)`, `Avsnittsunderlag(avsnitt, rubrik, instruktion, tjanst_id, tjanst_namn, tjanst_beskrivning, nivaer: dict[str, str], hot, sarbarheter, kontroller, uppgifter, regelspar: tuple[str, ...], undvik)` med `tillatna_id() -> frozenset[str]`.
  - Dokumentet: `Avsnitt(id, rubrik, kalla: Literal["regelbas", "ai"], stycken: tuple[Textstycke, ...])` med `kontrollsumma() -> str`; `Dokument(id, titel, avsnitt: tuple[Avsnitt, ...])` med `avsnitt_med_id() -> dict[str, Avsnitt]`.
- Produces i `dokument/leverantor.py`:
  - `LeverantorFel(RiskanalysFel)`.
  - `Tokenanvandning(typ: str, modell: str | None, indata_token: int, utdata_token: int)`: en post per försök hos API:t. Vid fallback finns en post för den modell som avböjde och en av typen `fallback_message` för den som svarade.
  - `Anropsdata(leverantor, begard_modell, svarsmodell, effort: str | None, prompt_kontrollsumma: str | None, svar_id: str | None, stop_reason: str | None, reservmodell_svarade: bool, anvandning: tuple[Tokenanvandning, ...], tidpunkt: datetime)`.
  - `Leveranssvar(anrop: Anropsdata, text: str, avbrott: str | None)`: det råa svaret och dess anropsdata. `avbrott` är satt när leverantören stoppade svaret, till exempel när modellen avböjde.
  - Protokollet `Textleverantor` (`namn: str`, `modell: str`, `skriv(underlag: Avsnittsunderlag, aterkoppling: list[str]) -> Leveranssvar`).
  - `Testleverantor(svar: list[AvsnittsUtkast | str])` med `namn = "test"`, `modell = "testleverantor"` och listan `anrop`. En sträng skickas som den är, så att tester kan prova svar som inte följer schemat.
  - `ladda_testleverantor(fil: Path) -> Testleverantor`.

AI-schemat skickas som JSON-schema i API-anropet. Strukturerade svar kräver att varje objekt har `additionalProperties: false` och att alla fält är obligatoriska. Därför används `list` och inga standardvärden i schemamodellerna.

Leverantören tolkar inte svaret. Den lämnar tillbaka råtexten och anropsdatan, och skrivningen (Task 16) sparar försöket innan texten tolkas och valideras. Då finns ett betalt svar kvar även om det inte gick att tolka. `LeverantorFel` kastas bara när inget svar kom, till exempel vid nätverksfel.

- [ ] **Step 1: Skriv det felande testet `tester/enhet/test_dokumentmodeller.py`**

```python
import pytest
from pydantic import ValidationError

from riskanalys.dokument.modeller import (
    Avsnitt,
    Avsnittsunderlag,
    AvsnittsUtkast,
    Dokument,
    Textstycke,
    UnderlagHot,
    UnderlagKontroll,
    UnderlagSarbarhet,
    UnderlagUppgift,
)


def _objekt(schema):
    yield schema
    yield from schema.get("$defs", {}).values()


def test_ai_schemat_ar_last():
    for objekt in _objekt(AvsnittsUtkast.model_json_schema()):
        assert objekt["additionalProperties"] is False
        assert set(objekt["required"]) == set(objekt["properties"])


def test_ai_svar_med_okant_falt_vagras():
    with pytest.raises(ValidationError):
        AvsnittsUtkast.model_validate({"avsnitt": "D-ARB.6.1", "stycken": [], "oklarheter": [], "extra": 1})


def test_ai_svar_med_okand_stycketyp_vagras():
    with pytest.raises(ValidationError):
        Textstycke.model_validate({"typ": "slutsats", "text": "x", "referenser": []})


def test_tillatna_id_i_underlaget():
    underlag = Avsnittsunderlag(
        avsnitt="D-ARB.6.1",
        rubrik="Löpande bokföring",
        instruktion="Skriv.",
        tjanst_id="T-1",
        tjanst_namn="Tjänst",
        tjanst_beskrivning="Beskrivning.",
        nivaer={"inneboende_risk": "hög"},
        hot=(UnderlagHot(id="H-1", namn="Hot", beskrivning="B."),),
        sarbarheter=(UnderlagSarbarhet(id="S-1", namn="Sårbarhet", galler="ja"),),
        kontroller=(UnderlagKontroll(id="C-1", namn="Kontroll", status="finns, ej belagd"),),
        uppgifter=(UnderlagUppgift(id="P-A", fraga="Andel?", varde="30 %", bekraftad=True),),
        regelspar=("BT-MATRIS-08",),
        undvik=(),
    )
    assert underlag.tillatna_id() == {"T-1", "H-1", "S-1", "C-1", "P-A", "BT-MATRIS-08"}


def test_avsnittets_kontrollsumma_andras_med_texten():
    avsnitt = Avsnitt(id="D-ARB.1", rubrik="Syfte", kalla="regelbas", stycken=())
    andrat = avsnitt.model_copy(
        update={"stycken": (Textstycke(typ="beskrivning", text="Ny text.", referenser=[]),)}
    )
    assert avsnitt.kontrollsumma().startswith("sha256:")
    assert avsnitt.kontrollsumma() != andrat.kontrollsumma()


def test_dokument_sparas_och_lases_oforandrat():
    stycke = Textstycke(typ="analys", text="Text.", referenser=["H-1"])
    dokument = Dokument(
        id="D-ARB",
        titel="Allmän riskbedömning",
        avsnitt=(Avsnitt(id="D-ARB.1", rubrik="Syfte", kalla="regelbas", stycken=(stycke,)),),
    )
    assert Dokument.model_validate_json(dokument.model_dump_json()) == dokument
    assert set(dokument.avsnitt_med_id()) == {"D-ARB.1"}
```

- [ ] **Step 2: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/enhet/test_dokumentmodeller.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.dokument'`.

- [ ] **Step 3: Skriv `src/riskanalys/dokument/__init__.py`**

```python
"""Dokument: AI-underlag, AI-utkast, validering, sammanställning och export."""
```

- [ ] **Step 4: Skriv `src/riskanalys/dokument/modeller.py`**

```python
"""Modeller för AI-schemat, AI-underlaget och dokumenten (spec 8 och 11)."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from riskanalys.lagring.kontrollsumma import for_text


class Last(BaseModel):
    """Basklass: okända fält vägras och objekten ändras inte efter att de skapats."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class Textstycke(Last):
    typ: Literal["beskrivning", "analys", "motivering", "scenario"]
    text: str
    referenser: list[str]


class Oklarhet(Last):
    fraga: str
    saknad_uppgift: str


class AvsnittsUtkast(Last):
    """Det låsta schema som AI svarar i."""

    avsnitt: str
    stycken: list[Textstycke]
    oklarheter: list[Oklarhet]


class UnderlagHot(Last):
    id: str
    namn: str
    beskrivning: str


class UnderlagSarbarhet(Last):
    id: str
    namn: str
    galler: Literal["ja", "nej", "okänt"]


class UnderlagKontroll(Last):
    id: str
    namn: str
    status: str


class UnderlagUppgift(Last):
    id: str
    fraga: str
    varde: str
    bekraftad: bool


class UnderlagBrist(Last):
    id: str
    namn: str


class Avsnittsunderlag(Last):
    """Allt AI får veta om ett avsnitt. Byggs bara ur tillåtelselistan."""

    avsnitt: str
    rubrik: str
    instruktion: str
    tjanst_id: str
    tjanst_namn: str
    tjanst_beskrivning: str
    nivaer: dict[str, str]
    hot: tuple[UnderlagHot, ...]
    sarbarheter: tuple[UnderlagSarbarhet, ...]
    kontroller: tuple[UnderlagKontroll, ...]
    uppgifter: tuple[UnderlagUppgift, ...]
    regelspar: tuple[str, ...]
    undvik: tuple[UnderlagBrist, ...]

    def tillatna_id(self) -> frozenset[str]:
        """De ID:n som texten får hänvisa till."""
        return frozenset(
            {
                self.tjanst_id,
                *(post.id for post in self.hot),
                *(post.id for post in self.sarbarheter),
                *(post.id for post in self.kontroller),
                *(post.id for post in self.uppgifter),
                *self.regelspar,
            }
        )


class Avsnitt(Last):
    id: str
    rubrik: str
    kalla: Literal["regelbas", "ai"]
    stycken: tuple[Textstycke, ...]

    def kontrollsumma(self) -> str:
        return for_text(self.model_dump_json())


class Dokument(Last):
    id: str
    titel: str
    avsnitt: tuple[Avsnitt, ...]

    def avsnitt_med_id(self) -> dict[str, Avsnitt]:
        return {avsnitt.id: avsnitt for avsnitt in self.avsnitt}
```

- [ ] **Step 5: Kör testet**

Run: `.venv/bin/pytest tester/enhet/test_dokumentmodeller.py -v`
Expected: alla tester passerar.

- [ ] **Step 6: Skriv det felande testet `tester/enhet/test_leverantor.py`**

```python
import pytest

from riskanalys.dokument.leverantor import LeverantorFel, Testleverantor, ladda_testleverantor
from riskanalys.dokument.modeller import Avsnittsunderlag, AvsnittsUtkast


def _underlag():
    return Avsnittsunderlag(
        avsnitt="D-ARB.6.1",
        rubrik="Tjänst",
        instruktion="Skriv.",
        tjanst_id="T-1",
        tjanst_namn="Tjänst",
        tjanst_beskrivning="Beskrivning.",
        nivaer={},
        hot=(),
        sarbarheter=(),
        kontroller=(),
        uppgifter=(),
        regelspar=(),
        undvik=(),
    )


def _utkast(text):
    return AvsnittsUtkast.model_validate(
        {"avsnitt": "D-ARB.6.1", "stycken": [{"typ": "analys", "text": text, "referenser": []}], "oklarheter": []}
    )


def _text(leveranssvar):
    return AvsnittsUtkast.model_validate_json(leveranssvar.text).stycken[0].text


def test_testleverantorn_svarar_i_tur_och_ordning_och_sparar_anropen():
    leverantor = Testleverantor([_utkast("ett"), _utkast("två")])
    forsta = leverantor.skriv(_underlag(), [])
    assert _text(forsta) == "ett"
    assert _text(leverantor.skriv(_underlag(), ["Rätta talet."])) == "två"
    assert [aterkoppling for _, aterkoppling in leverantor.anrop] == [[], ["Rätta talet."]]


def test_testleverantorn_fyller_i_anropsdata():
    svar = Testleverantor([_utkast("ett")]).skriv(_underlag(), [])
    assert (svar.anrop.leverantor, svar.anrop.begard_modell, svar.anrop.svarsmodell) == (
        "test",
        "testleverantor",
        "testleverantor",
    )
    assert (svar.anrop.svar_id, svar.anrop.reservmodell_svarade, svar.avbrott) == ("test-1", False, None)


def test_testleverantorn_kan_ge_ett_svar_som_inte_foljer_schemat():
    assert Testleverantor(['{"avsnitt": "D-ARB.6.1"}']).skriv(_underlag(), []).text == '{"avsnitt": "D-ARB.6.1"}'


def test_testleverantorn_utan_fler_svar_ger_fel():
    leverantor = Testleverantor([_utkast("ett")])
    leverantor.skriv(_underlag(), [])
    with pytest.raises(LeverantorFel, match="1 förberedda svar"):
        leverantor.skriv(_underlag(), [])


def test_testsvar_lases_fran_fil(tmp_path):
    fil = tmp_path / "svar.json"
    fil.write_text("[" + _utkast("ett").model_dump_json() + "]", encoding="utf-8")
    leverantor = ladda_testleverantor(fil)
    assert _text(leverantor.skriv(_underlag(), [])) == "ett"


def test_saknad_testsvarsfil_ger_fel(tmp_path):
    with pytest.raises(LeverantorFel, match="saknas"):
        ladda_testleverantor(tmp_path / "saknas.json")


def test_ogiltig_testsvarsfil_ger_fel(tmp_path):
    fil = tmp_path / "svar.json"
    fil.write_text('[{"avsnitt": "D-ARB.6.1"}]', encoding="utf-8")
    with pytest.raises(LeverantorFel, match="ogiltig"):
        ladda_testleverantor(fil)
```

- [ ] **Step 7: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/enhet/test_leverantor.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.dokument.leverantor'`.

- [ ] **Step 8: Skriv `src/riskanalys/dokument/leverantor.py`**

```python
"""Gränssnitt för textleverantörer och en testleverantör för automatiska tester (spec 8.3)."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from pydantic import TypeAdapter, ValidationError

from riskanalys.dokument.modeller import Avsnittsunderlag, AvsnittsUtkast, Last
from riskanalys.fel import RiskanalysFel

_SVARSLISTA = TypeAdapter(list[AvsnittsUtkast])


class LeverantorFel(RiskanalysFel):
    """Textleverantören kunde inte leverera något svar."""


class Tokenanvandning(Last):
    """Tokenanvändning för ett försök hos leverantören."""

    typ: str
    modell: str | None
    indata_token: int
    utdata_token: int


class Anropsdata(Last):
    """Vem som svarade, med vilka inställningar, och vad anropet förbrukade."""

    leverantor: str
    begard_modell: str
    svarsmodell: str
    effort: str | None
    prompt_kontrollsumma: str | None
    svar_id: str | None
    stop_reason: str | None
    reservmodell_svarade: bool
    anvandning: tuple[Tokenanvandning, ...]
    tidpunkt: datetime


class Leveranssvar(Last):
    """Ett svar från leverantören: råtexten, anropsdatan och eventuellt avbrott."""

    anrop: Anropsdata
    text: str
    avbrott: str | None


class Textleverantor(Protocol):
    namn: str
    modell: str

    def skriv(self, underlag: Avsnittsunderlag, aterkoppling: list[str]) -> Leveranssvar: ...


class Testleverantor:
    """Returnerar förberedda svar i tur och ordning. Används i alla automatiska tester."""

    __test__ = False  # namnet börjar på Test, men klassen är ingen testklass för pytest
    namn = "test"
    modell = "testleverantor"

    def __init__(self, svar: list[AvsnittsUtkast | str]) -> None:
        self._svar = tuple(svar)
        self.anrop: list[tuple[Avsnittsunderlag, list[str]]] = []

    def skriv(self, underlag: Avsnittsunderlag, aterkoppling: list[str]) -> Leveranssvar:
        self.anrop.append((underlag, list(aterkoppling)))
        nummer = len(self.anrop)
        if nummer > len(self._svar):
            raise LeverantorFel(f"Testleverantören har bara {len(self._svar)} förberedda svar.")
        svar = self._svar[nummer - 1]
        return Leveranssvar(
            anrop=Anropsdata(
                leverantor=self.namn,
                begard_modell=self.modell,
                svarsmodell=self.modell,
                effort=None,
                prompt_kontrollsumma=None,
                svar_id=f"test-{nummer}",
                stop_reason="end_turn",
                reservmodell_svarade=False,
                anvandning=(),
                tidpunkt=datetime.now(timezone.utc),
            ),
            text=svar if isinstance(svar, str) else svar.model_dump_json(),
            avbrott=None,
        )


def ladda_testleverantor(fil: Path) -> Testleverantor:
    """Läser förberedda svar från en JSON-fil med en lista av AI-utkast."""
    try:
        svar = _SVARSLISTA.validate_json(fil.read_text(encoding="utf-8"))
    except FileNotFoundError as undantag:
        raise LeverantorFel(f"Filen med testsvar saknas: {fil}") from undantag
    except ValidationError as undantag:
        raise LeverantorFel(f"Filen med testsvar {fil} är ogiltig: {undantag.error_count()} fel.") from undantag
    return Testleverantor(list(svar))
```

- [ ] **Step 9: Kör alla tester**

Run: `.venv/bin/pytest -v`
Expected: alla tester passerar. Etapp M0 är klar.

- [ ] **Step 10: Commit**

```bash
git add src/riskanalys/dokument tester/enhet/test_dokumentmodeller.py tester/enhet/test_leverantor.py
git commit -m "feat: dokumentmodeller, låst AI-schema och testleverantör"
```

---

## M1 Tunn kedja

### Task 10: Byråprofil och kommandona `ny`, `bekrafta` och `profil`

**Files:**
- Create: `src/riskanalys/lagring/yamlfil.py`
- Create: `src/riskanalys/profil/__init__.py`, `modeller.py`, `hantering.py`, `lagring.py`
- Create: `src/riskanalys/kommandon/profil_kommando.py`
- Modify: `src/riskanalys/kommandon/__init__.py` (lägg till `datumargument`)
- Modify: `src/riskanalys/cli.py` (registrera `profil_kommando`)
- Modify: `tester/conftest.py` (fixturerna `datamapp`, `real_varden`, `real_varden_text`, `profil_fabrik`)
- Test: `tester/enhet/test_profil.py`, `tester/enhet/test_profil_kommando.py`

**Interfaces:**
- Consumes: `Regelbas`, `Falt`, `Faltdef`, `Faltvarde`, `Kunskap`, `kontrollera_varde`, `tolka_villkor`, `falt_i`, `VillkorsFel`, `Urval`, `valj`, `vantande_andringar`, `beskriv_vantande`, `skapa_byramapp`, `befintlig_byramapp`, `ladda_giltig_regelbas`, `regelbasargument`.
- Produces:
  - `lagring/yamlfil.py`: `spara_yaml(sokvag: Path, data: Any) -> None`, `las_yaml(sokvag: Path) -> Any` (fel blir `RiskanalysFel`).
  - `profil/modeller.py`: `Status` (`saknas`, `föreslagen`, `bekräftad`, `ej_tillämplig`), `Uppgift(varde: Any = None, status: Status = "saknas", kalla: str | None = None, datum: date | None = None, bekraftad_av: str | None = None, motivering: str | None = None)`, `Byra(id, regelpaket, datum: date, lan)`, `Profil(byra: Byra, uppgifter: dict[str, Uppgift])` med `faltvarden() -> dict[str, Faltvarde]` och `ar_bekraftad(falt_id: str) -> bool`.
  - `profil/hantering.py`: `ProfilFel(RiskanalysFel)`, `ANDEL_HJALP`, `skapa_profil(regelbas, byra) -> Profil`, `tolka_varde(falt: Falt, text: str) -> Any`, `visa_varde(falt: Falt, varde: Any) -> str`, `beskriv_uppgift(falt: Falt, uppgift: Uppgift) -> str`, `bekrafta(profil, regelbas, falt_id, text, kalla: str | None, roll: str, datum: date) -> Profil`, `markera_ej_tillamplig(profil, regelbas, falt_id, motivering: str | None, roll: str, datum: date) -> Profil`, `kritiska_falt(regelbas, urval: Urval) -> frozenset[str]`, `saknade_kritiska(profil, regelbas, urval: Urval) -> tuple[str, ...]`, `personnamn(profil, regelbas) -> tuple[str, ...]`.
  - `profil/lagring.py`: `PROFILFIL = Path("profil") / "profil.yaml"`, `spara_profil(byramapp: Path, profil: Profil) -> Path`, `las_profil(byramapp: Path) -> Profil`.
  - `kommandon.datumargument(text: str) -> date` (argparse-typ med svenskt felmeddelande).
  - Kommandona `ny`, `bekrafta` och `profil`.
  - Fixturer: `datamapp` (sätter `RISKANALYS_DATA` till en tillfällig mapp), `real_varden` (dict med det verklighetsnära testfallets värden), `real_varden_text` (samma värden som text för kommandoraden), `profil_fabrik(regelbas, varden, okanda=(), ej_tillampliga=()) -> Profil`.

Kritiska uppgifter är de som riskbedömningen bygger på: fält märkta `kritisk`, varje tjänsts erbjuds-fält, kontrollernas fält, alla fält som sårbarheternas villkor använder och alla fält som avgör om ett krav i urvalet gäller byrån (`galler_om`). De måste vara bekräftade eller ej tillämpliga innan riskbedömningen kan fastställas (spec 10). Den som bekräftar sparas som roll, till exempel `roll:FfR`, aldrig med namn.

- [ ] **Step 1: Lägg till fixturer sist i `tester/conftest.py`**

```python
@pytest.fixture
def datamapp(tmp_path, monkeypatch):
    """En tom datamapp utanför repot, bara för testet."""
    mapp = tmp_path / "data"
    monkeypatch.setenv("RISKANALYS_DATA", str(mapp))
    return mapp


REAL_VARDEN = {
    "P-ORG.namn": "Testbyrån AB",
    "P-ORG.antal_anstallda": 8,
    "P-ORG.verksamhetsstallen": 1,
    "P-ROLL.ffr_namn": "Testa Testsson",
    "P-TJ.T-RED-01.erbjuds": True,
    "P-KUND.andel_riskbransch": 0.3,
    "P-KUND.andel_kontant": 0.05,
    "P-KANAL.andel_digitalt_underlag": 0.8,
    "P-KANAL.bankdata_andel": 0.4,
    "P-VERK.juniora_konsulter": False,
    "P-KONTROLL.C-07.utformning": "finns",
    "P-KONTROLL.C-07.genomforande": "ej_belagt",
}

REAL_VARDEN_TEXT = [
    ("P-ORG.namn", "Testbyrån AB"),
    ("P-ORG.antal_anstallda", "8"),
    ("P-ORG.verksamhetsstallen", "1"),
    ("P-ROLL.ffr_namn", "Testa Testsson"),
    ("P-TJ.T-RED-01.erbjuds", "ja"),
    ("P-KUND.andel_riskbransch", "30 %"),
    ("P-KUND.andel_kontant", "5 %"),
    ("P-KANAL.andel_digitalt_underlag", "0,8"),
    ("P-KANAL.bankdata_andel", "40%"),
    ("P-VERK.juniora_konsulter", "Nej"),
    ("P-KONTROLL.C-07.utformning", "finns"),
    ("P-KONTROLL.C-07.genomforande", "ej_belagt"),
]


@pytest.fixture
def real_varden():
    """Det verklighetsnära testfallet. Alla uppgifter är syntetiska."""
    return dict(REAL_VARDEN)


@pytest.fixture
def real_varden_text():
    """Samma värden som de skrivs på kommandoraden, med blandade svenska format."""
    return list(REAL_VARDEN_TEXT)


@pytest.fixture
def profil_fabrik():
    """Bygger en profil där givna värden är bekräftade och övriga saknas."""
    from riskanalys.profil.modeller import Byra, Profil, Uppgift

    testdag = date(2026, 10, 1)

    def uppgift(falt_id, varden, okanda, ej_tillampliga):
        if falt_id in ej_tillampliga:
            return Uppgift(
                status="ej_tillämplig", motivering="Syntetiskt testfall.", datum=testdag, bekraftad_av="roll:FfR"
            )
        if falt_id in varden and falt_id not in okanda:
            return Uppgift(
                varde=varden[falt_id],
                status="bekräftad",
                kalla="Syntetiskt testfall",
                datum=testdag,
                bekraftad_av="roll:FfR",
            )
        return Uppgift()

    def fabrik(regelbas, varden, okanda=(), ej_tillampliga=()):
        paket = next(iter(regelbas.regelpaket.values()))
        byra = Byra(id="testbyra", regelpaket=paket.id, datum=date(2026, 11, 1), lan="Västra Götaland")
        uppgifter = {falt_id: uppgift(falt_id, varden, okanda, ej_tillampliga) for falt_id in regelbas.falt}
        return Profil(byra=byra, uppgifter=uppgifter)

    return fabrik
```

- [ ] **Step 2: Skriv det felande testet `tester/enhet/test_profil.py`**

```python
from datetime import date

import pytest

from riskanalys.lagring.datamapp import skapa_byramapp
from riskanalys.profil.hantering import (
    ProfilFel,
    bekrafta,
    kritiska_falt,
    markera_ej_tillamplig,
    personnamn,
    saknade_kritiska,
    skapa_profil,
    tolka_varde,
    visa_varde,
)
from riskanalys.profil.lagring import las_profil, spara_profil
from riskanalys.profil.modeller import Byra
from riskanalys.regelverk.urval import valj
from riskanalys.regelverk.villkor import Kunskap

BYRA = Byra(id="testbyra", regelpaket="RP-RED-VG", datum=date(2026, 11, 1), lan="Västra Götaland")
DAG = date(2026, 10, 1)
KRITISKA = {
    "P-ORG.antal_anstallda",
    "P-ORG.verksamhetsstallen",
    "P-ROLL.ffr_namn",
    "P-TJ.T-RED-01.erbjuds",
    "P-KUND.andel_riskbransch",
    "P-KUND.andel_kontant",
    "P-KANAL.andel_digitalt_underlag",
    "P-KANAL.bankdata_andel",
    "P-VERK.juniora_konsulter",
    "P-KONTROLL.C-07.utformning",
    "P-KONTROLL.C-07.genomforande",
}


def test_ny_profil_saknar_alla_uppgifter(regelbas):
    profil = skapa_profil(regelbas, BYRA)
    assert set(profil.uppgifter) == set(regelbas.falt)
    assert {uppgift.status for uppgift in profil.uppgifter.values()} == {"saknas"}


@pytest.mark.parametrize(
    ("falt_id", "text", "vantat"),
    [
        ("P-VERK.juniora_konsulter", "Ja", True),
        ("P-VERK.juniora_konsulter", "nej", False),
        ("P-KUND.andel_riskbransch", "30 %", 0.3),
        ("P-KUND.andel_riskbransch", "30%", 0.3),
        ("P-KUND.andel_riskbransch", "0,3", 0.3),
        ("P-KUND.andel_riskbransch", "1", 1.0),
        ("P-ORG.antal_anstallda", "8", 8),
        ("P-KONTROLL.C-07.utformning", "finns", "finns"),
        ("P-ORG.namn", " Testbyrån AB ", "Testbyrån AB"),
    ],
)
def test_varden_med_svenska_format_tolkas(regelbas, falt_id, text, vantat):
    assert tolka_varde(regelbas.falt[falt_id], text) == vantat


def test_andel_over_ett_utan_procenttecken_vagras(regelbas):
    with pytest.raises(ProfilFel, match="0–1 eller i procent"):
        tolka_varde(regelbas.falt["P-KUND.andel_riskbransch"], "30")


@pytest.mark.parametrize(
    ("falt_id", "text", "meddelande"),
    [
        ("P-KUND.andel_riskbransch", "130 %", "0–1 eller i procent"),
        ("P-VERK.juniora_konsulter", "kanske", "ja eller nej"),
        ("P-KONTROLL.C-07.utformning", "delvis", "Välj ett av: finns, saknas"),
        ("P-ORG.antal_anstallda", "åtta", "Skriv ett tal"),
        ("P-ORG.namn", "  ", "passar inte"),
    ],
)
def test_ogiltiga_varden_vagras_med_hjalptext(regelbas, falt_id, text, meddelande):
    with pytest.raises(ProfilFel, match=meddelande):
        tolka_varde(regelbas.falt[falt_id], text)


@pytest.mark.parametrize(
    ("falt_id", "varde", "vantat"),
    [
        ("P-KUND.andel_kontant", 0.05, "5 %"),
        ("P-VERK.juniora_konsulter", False, "nej"),
        ("P-ORG.antal_anstallda", 8, "8"),
    ],
)
def test_varden_visas_pa_svenska(regelbas, falt_id, varde, vantat):
    assert visa_varde(regelbas.falt[falt_id], varde) == vantat


def test_bekrafta_ger_ny_profil_och_lamnar_den_gamla_orord(regelbas):
    profil = skapa_profil(regelbas, BYRA)
    ny = bekrafta(profil, regelbas, "P-KUND.andel_riskbransch", "30 %", "Kundregistret", "FfR", DAG)
    assert ny.uppgifter["P-KUND.andel_riskbransch"].varde == 0.3
    assert ny.uppgifter["P-KUND.andel_riskbransch"].bekraftad_av == "roll:FfR"
    assert profil.uppgifter["P-KUND.andel_riskbransch"].status == "saknas"


def test_bekrafta_kraver_kalla(regelbas):
    with pytest.raises(ProfilFel, match="--kalla"):
        bekrafta(skapa_profil(regelbas, BYRA), regelbas, "P-ORG.antal_anstallda", "8", None, "FfR", DAG)


def test_bekrafta_okant_falt_vagras(regelbas):
    with pytest.raises(ProfilFel, match="P-SAKNAS finns inte"):
        bekrafta(skapa_profil(regelbas, BYRA), regelbas, "P-SAKNAS", "1", "Källa", "FfR", DAG)


def test_ej_tillampligt_kraver_motivering(regelbas):
    with pytest.raises(ProfilFel, match="--motivering"):
        markera_ej_tillamplig(skapa_profil(regelbas, BYRA), regelbas, "P-VERK.juniora_konsulter", None, "FfR", DAG)


def test_faltvarden_foljer_status(regelbas):
    profil = bekrafta(skapa_profil(regelbas, BYRA), regelbas, "P-ORG.antal_anstallda", "8", "Lönelistan", "FfR", DAG)
    profil = markera_ej_tillamplig(
        profil, regelbas, "P-VERK.juniora_konsulter", "Byrån har inga anställda konsulter.", "FfR", DAG
    )
    varden = profil.faltvarden()
    assert varden["P-ORG.antal_anstallda"].kunskap is Kunskap.KAND
    assert varden["P-VERK.juniora_konsulter"].kunskap is Kunskap.EJ_TILLAMPLIG
    assert varden["P-KUND.andel_kontant"].kunskap is Kunskap.OKAND


def _urval(regelbas):
    return valj(regelbas, BYRA.regelpaket, BYRA.datum, BYRA.lan)


def test_kritiska_falt_for_lopande_bokforing(regelbas):
    assert kritiska_falt(regelbas, _urval(regelbas)) == KRITISKA


def test_falt_som_avgor_om_ett_krav_galler_ar_kritiska(regelbas):
    krav = regelbas.krav["KRV-LSF-001"]
    villkor = {"falt": "P-ORG.namn", "op": "finns"}
    andrad = regelbas.model_copy(
        update={"krav": {**regelbas.krav, krav.id: krav.model_copy(update={"galler_om": villkor})}}
    )
    assert kritiska_falt(andrad, _urval(andrad)) == KRITISKA | {"P-ORG.namn"}


def test_saknade_kritiska_uppgifter(regelbas, profil_fabrik, real_varden):
    assert len(saknade_kritiska(skapa_profil(regelbas, BYRA), regelbas, _urval(regelbas))) == 11
    assert saknade_kritiska(profil_fabrik(regelbas, real_varden), regelbas, _urval(regelbas)) == ()


def test_personnamn_hamtas_ur_bekraftade_personuppgifter(regelbas, profil_fabrik, real_varden):
    assert personnamn(profil_fabrik(regelbas, real_varden), regelbas) == ("Testa Testsson",)


def test_profilen_sparas_och_lases_oforandrad(datamapp, regelbas, profil_fabrik, real_varden):
    mapp = skapa_byramapp("testbyra")
    profil = profil_fabrik(regelbas, real_varden)
    spara_profil(mapp, profil)
    assert las_profil(mapp) == profil
```

- [ ] **Step 3: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/enhet/test_profil.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.profil'`.

- [ ] **Step 4: Skriv `src/riskanalys/lagring/yamlfil.py`**

```python
"""Läs och skriv YAML med svenska tecken."""

from pathlib import Path
from typing import Any

import yaml

from riskanalys.fel import RiskanalysFel


def spara_yaml(sokvag: Path, data: Any) -> None:
    sokvag.parent.mkdir(parents=True, exist_ok=True)
    sokvag.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def las_yaml(sokvag: Path) -> Any:
    try:
        return yaml.safe_load(sokvag.read_text(encoding="utf-8"))
    except FileNotFoundError as undantag:
        raise RiskanalysFel(f"Filen {sokvag} saknas.") from undantag
    except yaml.YAMLError as undantag:
        raise RiskanalysFel(f"Filen {sokvag} är inte giltig YAML: {undantag}") from undantag
```

- [ ] **Step 5: Skriv `src/riskanalys/profil/__init__.py`**

```python
"""Byråprofilen: uppgifter om byrån med status och källa."""
```

- [ ] **Step 6: Skriv `src/riskanalys/profil/modeller.py`**

```python
"""Byråprofilen (spec 6.2). Varje uppgift har status, källa och datum."""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from riskanalys.regelverk.villkor import Faltvarde, Kunskap

Status = Literal["saknas", "föreslagen", "bekräftad", "ej_tillämplig"]


class Fryst(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Uppgift(Fryst):
    varde: Any = None
    status: Status = "saknas"
    kalla: str | None = None
    datum: date | None = None
    bekraftad_av: str | None = None
    motivering: str | None = None


class Byra(Fryst):
    id: str
    regelpaket: str
    datum: date
    lan: str


class Profil(Fryst):
    byra: Byra
    uppgifter: dict[str, Uppgift]

    def faltvarden(self) -> dict[str, Faltvarde]:
        """Uppgifterna som fältvärden för villkorsutvärderaren. Bara bekräftade värden är kända."""
        return {falt_id: _faltvarde(uppgift) for falt_id, uppgift in self.uppgifter.items()}

    def ar_bekraftad(self, falt_id: str) -> bool:
        uppgift = self.uppgifter.get(falt_id)
        return uppgift is not None and uppgift.status == "bekräftad"


def _faltvarde(uppgift: Uppgift) -> Faltvarde:
    if uppgift.status == "bekräftad":
        return Faltvarde(Kunskap.KAND, uppgift.varde)
    if uppgift.status == "ej_tillämplig":
        return Faltvarde(Kunskap.EJ_TILLAMPLIG)
    return Faltvarde(Kunskap.OKAND)
```

- [ ] **Step 7: Skriv `src/riskanalys/profil/hantering.py`**

```python
"""Skapa och ändra byråprofilen (spec 6.2 och 14)."""

import math
import re
from collections.abc import Callable
from datetime import date
from typing import Any

from riskanalys.fel import RiskanalysFel
from riskanalys.profil.modeller import Byra, Profil, Uppgift
from riskanalys.regelverk.modeller import Falt, Regelbas
from riskanalys.regelverk.urval import Urval
from riskanalys.regelverk.villkor import Faltdef, VillkorsFel, falt_i, kontrollera_varde, tolka_villkor

SANT = frozenset({"ja", "sant", "true", "1"})
FALSKT = frozenset({"nej", "falskt", "false", "0"})
ANDEL_HJALP = "Andelen anges som 0–1 eller i procent, till exempel 0,3 eller 30 %."
_PROCENT = re.compile(r"^(\d+(?:[.,]\d+)?)\s*%$")
_HJALP = {
    "andel": ANDEL_HJALP,
    "bool": "Skriv ja eller nej.",
    "heltal": "Skriv ett tal.",
    "tal": "Skriv ett tal.",
    "datum": "Skriv datumet som ÅÅÅÅ-MM-DD.",
}


class ProfilFel(RiskanalysFel):
    """En uppgift i profilen kan inte sparas."""


def skapa_profil(regelbas: Regelbas, byra: Byra) -> Profil:
    """En ny profil där alla uppgifter saknas."""
    return Profil(byra=byra, uppgifter={falt_id: Uppgift() for falt_id in regelbas.falt})


def tolka_varde(falt: Falt, text: str) -> Any:
    """Tolkar ett värde som användaren skrivit, med svenska format."""
    try:
        varde = _TOLKARE[falt.typ](text.strip())
    except ValueError as undantag:
        raise ProfilFel(f"Värdet {text!r} passar inte fältet {falt.id}.{_hjalp(falt)}") from undantag
    try:
        kontrollera_varde(Faltdef(falt.id, falt.typ, falt.val), varde)
    except VillkorsFel as undantag:
        raise ProfilFel(f"{undantag}{_hjalp(falt)}") from undantag
    return varde


def visa_varde(falt: Falt, varde: Any) -> str:
    """Ett värde som text på svenska."""
    if falt.typ == "bool":
        return "ja" if varde else "nej"
    if falt.typ == "andel":
        return f"{round(varde * 100)} %"
    if isinstance(varde, date):
        return varde.isoformat()
    return str(varde)


def beskriv_uppgift(falt: Falt, uppgift: Uppgift) -> str:
    if uppgift.status == "bekräftad":
        return f"{visa_varde(falt, uppgift.varde)} (bekräftad {uppgift.datum}, källa: {uppgift.kalla})"
    if uppgift.status == "ej_tillämplig":
        return f"ej tillämplig ({uppgift.motivering})"
    return uppgift.status


def bekrafta(
    profil: Profil,
    regelbas: Regelbas,
    falt_id: str,
    text: str,
    kalla: str | None,
    roll: str,
    datum: date,
) -> Profil:
    """Returnerar en ny profil där uppgiften är bekräftad."""
    falt = _falt(regelbas, falt_id)
    if not kalla or not kalla.strip():
        raise ProfilFel("Ange varifrån uppgiften kommer med --kalla, till exempel --kalla \"Kundregistret 2026-09-30\".")
    uppgift = Uppgift(
        varde=tolka_varde(falt, text),
        status="bekräftad",
        kalla=kalla.strip(),
        datum=datum,
        bekraftad_av=f"roll:{roll}",
    )
    return _med(profil, falt.id, uppgift)


def markera_ej_tillamplig(
    profil: Profil,
    regelbas: Regelbas,
    falt_id: str,
    motivering: str | None,
    roll: str,
    datum: date,
) -> Profil:
    """Returnerar en ny profil där uppgiften är markerad som ej tillämplig."""
    falt = _falt(regelbas, falt_id)
    if not motivering or not motivering.strip():
        raise ProfilFel("Ange varför uppgiften inte är tillämplig med --motivering.")
    uppgift = Uppgift(status="ej_tillämplig", motivering=motivering.strip(), datum=datum, bekraftad_av=f"roll:{roll}")
    return _med(profil, falt.id, uppgift)


def kritiska_falt(regelbas: Regelbas, urval: Urval) -> frozenset[str]:
    """Uppgifter som riskbedömningen bygger på och som måste vara kända före fastställelse."""
    definitioner = regelbas.faltdefinitioner()
    tjanster = [regelbas.tjanster[tjanst_id] for tjanst_id in urval.tjanster]
    uttryckliga = {falt.id for falt in regelbas.falt.values() if falt.kritisk}
    tillamplighet = {
        falt_id for valt in urval.krav for falt_id in falt_i(tolka_villkor(valt.krav.galler_om, definitioner))
    }
    erbjuds = {tjanst.erbjuds_falt for tjanst in tjanster}
    kontroller = {
        falt_id
        for tjanst in tjanster
        for kontroll_id in tjanst.kontroller
        for falt_id in (
            regelbas.kontroller[kontroll_id].utformning_falt,
            regelbas.kontroller[kontroll_id].genomforande_falt,
        )
    }
    villkor = {
        falt_id
        for tjanst in tjanster
        for sarbarhet_id in tjanst.sarbarheter
        for falt_id in falt_i(tolka_villkor(regelbas.sarbarheter[sarbarhet_id].villkor, definitioner))
    }
    return frozenset(uttryckliga | tillamplighet | erbjuds | kontroller | villkor)


def saknade_kritiska(profil: Profil, regelbas: Regelbas, urval: Urval) -> tuple[str, ...]:
    """Kritiska uppgifter som varken är bekräftade eller ej tillämpliga."""
    klara = {"bekräftad", "ej_tillämplig"}
    return tuple(
        sorted(
            falt_id
            for falt_id in kritiska_falt(regelbas, urval)
            if profil.uppgifter.get(falt_id, Uppgift()).status not in klara
        )
    )


def personnamn(profil: Profil, regelbas: Regelbas) -> tuple[str, ...]:
    """Bekräftade personuppgifter i textform. De får aldrig förekomma i AI-text."""
    return tuple(
        str(uppgift.varde)
        for falt_id, uppgift in profil.uppgifter.items()
        if falt_id in regelbas.falt
        and regelbas.falt[falt_id].personuppgift
        and uppgift.status == "bekräftad"
        and uppgift.varde
    )


def _falt(regelbas: Regelbas, falt_id: str) -> Falt:
    if falt_id not in regelbas.falt:
        raise ProfilFel(f"Fältet {falt_id} finns inte i regelbasen. Se alla fält med 'riskanalys profil'.")
    return regelbas.falt[falt_id]


def _med(profil: Profil, falt_id: str, uppgift: Uppgift) -> Profil:
    return profil.model_copy(update={"uppgifter": {**profil.uppgifter, falt_id: uppgift}})


def _hjalp(falt: Falt) -> str:
    if falt.typ == "val":
        return f" Välj ett av: {', '.join(falt.val)}."
    return f" {_HJALP[falt.typ]}" if falt.typ in _HJALP else ""


def _tal(text: str) -> float:
    varde = float(text.replace(" ", "").replace(",", "."))
    if not math.isfinite(varde):
        raise ValueError("inget ändligt tal")
    return varde


def _andel(text: str) -> float:
    procent = _PROCENT.match(text)
    if procent:
        return _tal(procent.group(1)) / 100
    varde = _tal(text)
    if varde > 1:
        raise ValueError("andel över 1 utan procenttecken")
    return varde


def _bool(text: str) -> bool:
    if text.lower() in SANT:
        return True
    if text.lower() in FALSKT:
        return False
    raise ValueError("inte ja eller nej")


def _heltal(text: str) -> int:
    return int(text.replace(" ", ""))


def _text(text: str) -> str:
    if not text:
        raise ValueError("tom text")
    return text


_TOLKARE: dict[str, Callable[[str], Any]] = {
    "bool": _bool,
    "heltal": _heltal,
    "tal": _tal,
    "andel": _andel,
    "text": _text,
    "val": _text,
    "datum": date.fromisoformat,
}
```

- [ ] **Step 8: Skriv `src/riskanalys/profil/lagring.py`**

```python
"""Läs och spara byråprofilen i byråns datamapp."""

from pathlib import Path

from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.yamlfil import las_yaml, spara_yaml
from riskanalys.profil.modeller import Profil

PROFILFIL = Path("profil") / "profil.yaml"


def spara_profil(byramapp: Path, profil: Profil) -> Path:
    sokvag = byramapp / PROFILFIL
    spara_yaml(sokvag, profil.model_dump(mode="python"))
    return sokvag


def las_profil(byramapp: Path) -> Profil:
    sokvag = byramapp / PROFILFIL
    if not sokvag.is_file():
        raise RiskanalysFel(f"Profilen saknas i {byramapp}. Skapa byrån med 'riskanalys ny'.")
    return Profil.model_validate(las_yaml(sokvag))
```

Profilen sparas med `mode="python"` så att datum förblir datum i YAML-filen och läses tillbaka som datum.

- [ ] **Step 9: Kör testet**

Run: `.venv/bin/pytest tester/enhet/test_profil.py -v`
Expected: alla tester passerar.

- [ ] **Step 10: Skriv det felande testet `tester/enhet/test_profil_kommando.py`**

```python
import pytest

from riskanalys.cli import main
from riskanalys.lagring.datamapp import byramapp
from riskanalys.profil.lagring import las_profil

NY = ["ny", "testbyra", "--regelpaket", "RP-RED-VG", "--lan", "Västra Götaland", "--datum", "2026-11-01"]


def test_ny_skapar_byra_med_tom_profil(datamapp, capsys):
    assert main(NY) == 0
    assert las_profil(byramapp("testbyra")).byra.regelpaket == "RP-RED-VG"
    assert "Nästa steg" in capsys.readouterr().out


def test_ny_med_okant_regelpaket_skapar_ingen_mapp(datamapp, capsys):
    assert main([*NY[:3], "RP-SAKNAS", *NY[4:]]) == 1
    assert "RP-SAKNAS finns inte" in capsys.readouterr().err
    assert not byramapp("testbyra").exists()


def test_ny_tva_ganger_vagras(datamapp, capsys):
    main(NY)
    assert main(NY) == 1
    assert "finns redan" in capsys.readouterr().err


def test_ogiltigt_datum_ger_svenskt_meddelande(datamapp, capsys):
    with pytest.raises(SystemExit):
        main([*NY[:-1], "1 november"])
    assert "ÅÅÅÅ-MM-DD" in capsys.readouterr().err


def test_bekrafta_med_procent(datamapp):
    main(NY)
    assert main(["bekrafta", "testbyra", "P-KUND.andel_riskbransch", "30 %", "--kalla", "Kundregistret"]) == 0
    assert las_profil(byramapp("testbyra")).uppgifter["P-KUND.andel_riskbransch"].varde == 0.3


def test_bekrafta_andel_utan_procenttecken_vagras(datamapp, capsys):
    main(NY)
    assert main(["bekrafta", "testbyra", "P-KUND.andel_riskbransch", "30", "--kalla", "Kundregistret"]) == 1
    assert "0–1 eller i procent" in capsys.readouterr().err


def test_bekrafta_utan_kalla_vagras(datamapp, capsys):
    main(NY)
    assert main(["bekrafta", "testbyra", "P-ORG.antal_anstallda", "8"]) == 1
    assert "--kalla" in capsys.readouterr().err


def test_bekrafta_ej_tillampligt(datamapp):
    main(NY)
    argv = ["bekrafta", "testbyra", "P-VERK.juniora_konsulter", "--ej-tillampligt", "--motivering", "Inga konsulter."]
    assert main(argv) == 0
    assert las_profil(byramapp("testbyra")).uppgifter["P-VERK.juniora_konsulter"].status == "ej_tillämplig"


def test_alla_varden_i_testfallet_kan_bekraftas(datamapp, real_varden, real_varden_text):
    main(NY)
    for falt_id, text in real_varden_text:
        assert main(["bekrafta", "testbyra", falt_id, text, "--kalla", "Syntetiskt testfall"]) == 0
    uppgifter = las_profil(byramapp("testbyra")).uppgifter
    assert {falt_id: uppgifter[falt_id].varde for falt_id in real_varden} == real_varden


def test_profil_visar_saknade_kritiska_uppgifter(datamapp, capsys):
    main(NY)
    capsys.readouterr()
    assert main(["profil", "testbyra"]) == 0
    assert "Kritiska uppgifter som saknas: 11" in capsys.readouterr().out


def test_kommando_for_okand_byra(datamapp, capsys):
    assert main(["profil", "saknas"]) == 1
    assert "finns inte" in capsys.readouterr().err
```

- [ ] **Step 11: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/enhet/test_profil_kommando.py -v`
Expected: FAIL, kommandoraden känner inte till `ny` (`SystemExit: 2` med "invalid choice: 'ny'").

- [ ] **Step 12: Lägg till `datumargument` i `src/riskanalys/kommandon/__init__.py`**

Lägg till `from datetime import date` bland importerna och lägg till funktionen sist i filen:

```python
def datumargument(text: str) -> date:
    """Argparse-typ för datum med svenskt felmeddelande."""
    try:
        return date.fromisoformat(text)
    except ValueError as undantag:
        raise argparse.ArgumentTypeError(
            f"{text!r} är inget datum. Skriv ÅÅÅÅ-MM-DD, till exempel 2026-11-01."
        ) from undantag
```

- [ ] **Step 13: Skriv `src/riskanalys/kommandon/profil_kommando.py`**

```python
"""riskanalys ny, bekrafta och profil"""

import argparse
from datetime import date
from typing import Any

from riskanalys.kommandon import datumargument, ladda_giltig_regelbas, regelbasargument
from riskanalys.lagring.datamapp import befintlig_byramapp, skapa_byramapp
from riskanalys.profil.hantering import (
    ProfilFel,
    bekrafta,
    beskriv_uppgift,
    kritiska_falt,
    markera_ej_tillamplig,
    saknade_kritiska,
    skapa_profil,
)
from riskanalys.profil.lagring import las_profil, spara_profil
from riskanalys.profil.modeller import Byra, Uppgift
from riskanalys.regelverk.urval import beskriv_vantande, valj, vantande_andringar


def lagg_till(underparsers: Any) -> None:
    ny = underparsers.add_parser("ny", help="Skapa en ny byrå med tom profil.")
    ny.add_argument("byra", help="Byrå-ID, till exempel testbyra.")
    ny.add_argument("--regelpaket", required=True, help="Till exempel RP-RED-VG.")
    ny.add_argument("--lan", required=True, help='Länet där byrån har sitt säte, till exempel "Västra Götaland".')
    ny.add_argument("--datum", required=True, type=datumargument, help="Datum som regelverket väljs för.")
    regelbasargument(ny)
    ny.set_defaults(kor=kor_ny)

    bekraftelse = underparsers.add_parser("bekrafta", help="Bekräfta en uppgift i profilen.")
    bekraftelse.add_argument("byra")
    bekraftelse.add_argument("falt", help="Fältets ID, till exempel P-KUND.andel_riskbransch.")
    bekraftelse.add_argument("varde", nargs="?", help="Värdet, till exempel 30 %%, 0,3, ja eller finns.")
    bekraftelse.add_argument("--kalla", help="Varifrån uppgiften kommer.")
    bekraftelse.add_argument("--roll", default="FfR", help="Rollen som bekräftar. Standard är FfR.")
    bekraftelse.add_argument("--ej-tillampligt", action="store_true", help="Markera uppgiften som ej tillämplig.")
    bekraftelse.add_argument("--motivering", help="Krävs med --ej-tillampligt.")
    bekraftelse.add_argument("--datum", type=datumargument, default=None, help="Standard är dagens datum.")
    regelbasargument(bekraftelse)
    bekraftelse.set_defaults(kor=kor_bekrafta)

    visning = underparsers.add_parser("profil", help="Visa byråns profil och vilka uppgifter som saknas.")
    visning.add_argument("byra")
    regelbasargument(visning)
    visning.set_defaults(kor=kor_profil)


def kor_ny(args: argparse.Namespace) -> int:
    regelbas = ladda_giltig_regelbas(args.regelbas)
    urval = valj(regelbas, args.regelpaket, args.datum, args.lan)
    mapp = skapa_byramapp(args.byra)
    byra = Byra(id=args.byra, regelpaket=args.regelpaket, datum=args.datum, lan=args.lan)
    spara_profil(mapp, skapa_profil(regelbas, byra))
    print(f"Byrån {args.byra} är skapad i {mapp}.")
    print(f"Regelpaket {urval.regelpaket.id} för {args.lan}: {len(urval.krav)} krav gäller {args.datum.isoformat()}.")
    for andring in vantande_andringar(regelbas, urval):
        print(f"Ändring som väntar: {beskriv_vantande(andring)}")
    print(f"Nästa steg: bekräfta uppgifterna. Se vilka som saknas med 'riskanalys profil {args.byra}'.")
    return 0


def kor_bekrafta(args: argparse.Namespace) -> int:
    mapp = befintlig_byramapp(args.byra)
    regelbas = ladda_giltig_regelbas(args.regelbas)
    profil = las_profil(mapp)
    datum = args.datum or date.today()
    if args.ej_tillampligt:
        ny_profil = markera_ej_tillamplig(profil, regelbas, args.falt, args.motivering, args.roll, datum)
    elif args.varde is None:
        raise ProfilFel("Ange ett värde, eller --ej-tillampligt med --motivering.")
    else:
        ny_profil = bekrafta(profil, regelbas, args.falt, args.varde, args.kalla, args.roll, datum)
    spara_profil(mapp, ny_profil)
    print(f"{args.falt}: {beskriv_uppgift(regelbas.falt[args.falt], ny_profil.uppgifter[args.falt])}")
    return 0


def kor_profil(args: argparse.Namespace) -> int:
    mapp = befintlig_byramapp(args.byra)
    regelbas = ladda_giltig_regelbas(args.regelbas)
    profil = las_profil(mapp)
    byra = profil.byra
    urval = valj(regelbas, byra.regelpaket, byra.datum, byra.lan)
    kritiska = kritiska_falt(regelbas, urval)
    print(f"Profil för {byra.id} ({byra.regelpaket}, {byra.lan}, {byra.datum.isoformat()})")
    for falt in regelbas.falt.values():
        markering = "*" if falt.id in kritiska else " "
        print(f"{markering} {falt.id}: {beskriv_uppgift(falt, profil.uppgifter.get(falt.id, Uppgift()))}")
        print(f"    {falt.fraga}")
    print("* = kritisk uppgift. Den måste vara bekräftad eller ej tillämplig innan riskbedömningen kan fastställas.")
    print(f"Kritiska uppgifter som saknas: {len(saknade_kritiska(profil, regelbas, urval))}")
    return 0
```

I hjälptexten för `varde` står `30 %%`, eftersom argparse annars tolkar `%` som en formatkod.

- [ ] **Step 14: Registrera kommandona i `src/riskanalys/cli.py`**

Ersätt raderna

```python
from riskanalys.kommandon import regelbas_kommando

KOMMANDON = [regelbas_kommando]
```

med

```python
from riskanalys.kommandon import profil_kommando, regelbas_kommando

KOMMANDON = [regelbas_kommando, profil_kommando]
```

- [ ] **Step 15: Kör testerna**

Run: `.venv/bin/pytest tester/enhet/test_profil.py tester/enhet/test_profil_kommando.py -v`
Expected: alla tester passerar.

- [ ] **Step 16: Commit**

```bash
git add src/riskanalys/lagring/yamlfil.py src/riskanalys/profil src/riskanalys/kommandon src/riskanalys/cli.py tester/conftest.py tester/enhet/test_profil.py tester/enhet/test_profil_kommando.py
git commit -m "feat: byråprofil med svenska värdeformat och kommandona ny, bekrafta och profil"
```

---

### Task 11: Versionshistorik och kommandot `utvardera`

**Files:**
- Create: `src/riskanalys/drift/__init__.py`, `src/riskanalys/drift/historik.py`
- Create: `src/riskanalys/kommandon/drift_kommando.py`
- Modify: `src/riskanalys/cli.py`
- Test: `tester/enhet/test_historik.py`

**Interfaces:**
- Consumes: `spara_yaml`, `las_yaml`, `befintlig_byramapp`, `datumargument`.
- Produces:
  - `HISTORIKFIL = Path("drift") / "historik.yaml"`, `GENOMGANG_MANADER = 12`, `UTVARDERING = "utvärdering"`.
  - `Handelse(datum: date, typ: Literal["utvärdering", "uppdatering", "fastställelse"], beskrivning: str, version: int | None = None)`.
  - `Historik(handelser: tuple[Handelse, ...] = ())` med `med(handelse) -> Historik`, `senaste_utvardering() -> date | None`, `nasta_genomgang() -> date | None`.
  - `lagg_till_manader(datum: date, manader: int) -> date`.
  - `las_historik(byramapp: Path) -> Historik` (tom historik om filen saknas), `spara_historik(byramapp: Path, historik: Historik) -> None`.
  - `historikens_kontrollsumma(byramapp: Path) -> str` (tom sträng om filen saknas). Granskningen sparar den så att fastställelsen kan upptäcka en ändrad historik.
  - Kommandot `utvardera <byra> --beskrivning TEXT [--datum D]`.

Föreskrifterna kräver utvärdering minst en gång per år och att datum för utvärdering och uppdatering framgår (14FS 2024:11 2 kap. 3 §). Nästa genomgång är tolv månader efter den senaste **utvärderingen** (spec 13.1). Uppdateringar och fastställelser kan stå i en historik men flyttar inte fristen, eftersom ett beslut att fastställa inte är en ny utvärdering. Byråns historikfil innehåller det byrån registrerar. Fastställelserna läses ur de låsta paketen (Task 21). Senaste händelse av typen utvärdering räknas efter datum, inte efter ordningen i filen.

- [ ] **Step 1: Skriv det felande testet `tester/enhet/test_historik.py`**

```python
from datetime import date

import pytest

from riskanalys.cli import main
from riskanalys.drift.historik import (
    Handelse,
    Historik,
    historikens_kontrollsumma,
    lagg_till_manader,
    las_historik,
    spara_historik,
)
from riskanalys.lagring.datamapp import skapa_byramapp


@pytest.mark.parametrize(
    ("datum", "manader", "vantat"),
    [
        (date(2026, 11, 1), 12, date(2027, 11, 1)),
        (date(2024, 2, 29), 12, date(2025, 2, 28)),
        (date(2026, 1, 31), 1, date(2026, 2, 28)),
        (date(2026, 12, 15), 1, date(2027, 1, 15)),
    ],
)
def test_lagg_till_manader(datum, manader, vantat):
    assert lagg_till_manader(datum, manader) == vantat


def test_tom_historik_har_ingen_nasta_genomgang():
    assert Historik().nasta_genomgang() is None


def test_nasta_genomgang_ar_tolv_manader_efter_den_senaste_utvarderingen():
    historik = Historik().med(Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Första."))
    historik = historik.med(Handelse(datum=date(2027, 3, 1), typ="utvärdering", beskrivning="Andra."))
    assert historik.senaste_utvardering() == date(2027, 3, 1)
    assert historik.nasta_genomgang() == date(2028, 3, 1)


def test_senare_faststallelse_eller_uppdatering_flyttar_inte_fristen():
    historik = Historik().med(Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Första."))
    historik = historik.med(Handelse(datum=date(2026, 11, 20), typ="fastställelse", beskrivning="v1", version=1))
    historik = historik.med(Handelse(datum=date(2027, 2, 1), typ="uppdatering", beskrivning="Ny rutin."))
    assert historik.senaste_utvardering() == date(2026, 11, 1)
    assert historik.nasta_genomgang() == date(2027, 11, 1)


def test_historik_utan_utvardering_har_ingen_nasta_genomgang():
    historik = Historik().med(Handelse(datum=date(2026, 11, 20), typ="fastställelse", beskrivning="v1", version=1))
    assert historik.senaste_utvardering() is None
    assert historik.nasta_genomgang() is None


def test_senaste_utvardering_raknas_efter_datum_inte_ordning():
    historik = Historik().med(Handelse(datum=date(2027, 3, 1), typ="utvärdering", beskrivning="Andra."))
    historik = historik.med(Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Inlagd i efterhand."))
    assert historik.senaste_utvardering() == date(2027, 3, 1)


def test_med_lamnar_den_gamla_historiken_orord():
    historik = Historik()
    historik.med(Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Första."))
    assert historik.handelser == ()


def test_historiken_sparas_och_lases(datamapp):
    mapp = skapa_byramapp("testbyra")
    assert las_historik(mapp) == Historik()
    historik = Historik().med(Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Första."))
    spara_historik(mapp, historik)
    assert las_historik(mapp) == historik


def test_historikens_kontrollsumma_andras_med_historiken(datamapp):
    mapp = skapa_byramapp("testbyra")
    assert historikens_kontrollsumma(mapp) == ""
    spara_historik(mapp, Historik().med(Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Första.")))
    forsta = historikens_kontrollsumma(mapp)
    spara_historik(mapp, las_historik(mapp).med(Handelse(datum=date(2027, 11, 1), typ="utvärdering", beskrivning="Andra.")))
    assert forsta.startswith("sha256:")
    assert historikens_kontrollsumma(mapp) != forsta


def test_utvardera_kommandot(datamapp, capsys):
    skapa_byramapp("testbyra")
    argv = ["utvardera", "testbyra", "--beskrivning", "Första riskbedömningen.", "--datum", "2026-11-01"]
    assert main(argv) == 0
    assert "Nästa genomgång senast 2027-11-01." in capsys.readouterr().out
```

- [ ] **Step 2: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/enhet/test_historik.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.drift'`.

- [ ] **Step 3: Skriv `src/riskanalys/drift/__init__.py`**

```python
"""Minsta drift: versionshistorik och nästa genomgång."""
```

- [ ] **Step 4: Skriv `src/riskanalys/drift/historik.py`**

```python
"""Versionshistorik och nästa genomgång (spec 13.1)."""

import calendar
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

from riskanalys.lagring.kontrollsumma import for_fil
from riskanalys.lagring.yamlfil import las_yaml, spara_yaml

HISTORIKFIL = Path("drift") / "historik.yaml"
GENOMGANG_MANADER = 12
UTVARDERING = "utvärdering"


class Handelse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    datum: date
    typ: Literal["utvärdering", "uppdatering", "fastställelse"]
    beskrivning: str
    version: int | None = None


class Historik(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    handelser: tuple[Handelse, ...] = ()

    def med(self, handelse: Handelse) -> "Historik":
        return Historik(handelser=(*self.handelser, handelse))

    def senaste_utvardering(self) -> date | None:
        """Datum för den senaste utvärderingen. Fastställelser och uppdateringar räknas inte."""
        return max((handelse.datum for handelse in self.handelser if handelse.typ == UTVARDERING), default=None)

    def nasta_genomgang(self) -> date | None:
        senaste = self.senaste_utvardering()
        return None if senaste is None else lagg_till_manader(senaste, GENOMGANG_MANADER)


def lagg_till_manader(datum: date, manader: int) -> date:
    """Lägger till månader. Finns inte dagen i målmånaden blir det månadens sista dag."""
    index = datum.month - 1 + manader
    ar, manad = datum.year + index // 12, index % 12 + 1
    return date(ar, manad, min(datum.day, calendar.monthrange(ar, manad)[1]))


def las_historik(byramapp: Path) -> Historik:
    sokvag = byramapp / HISTORIKFIL
    if not sokvag.is_file():
        return Historik()
    return Historik.model_validate(las_yaml(sokvag))


def spara_historik(byramapp: Path, historik: Historik) -> None:
    spara_yaml(byramapp / HISTORIKFIL, historik.model_dump(mode="json"))


def historikens_kontrollsumma(byramapp: Path) -> str:
    sokvag = byramapp / HISTORIKFIL
    return for_fil(sokvag) if sokvag.is_file() else ""
```

- [ ] **Step 5: Skriv `src/riskanalys/kommandon/drift_kommando.py`**

```python
"""riskanalys utvardera"""

import argparse
from datetime import date
from typing import Any

from riskanalys.drift.historik import Handelse, las_historik, spara_historik
from riskanalys.kommandon import datumargument
from riskanalys.lagring.datamapp import befintlig_byramapp


def lagg_till(underparsers: Any) -> None:
    parser = underparsers.add_parser("utvardera", help="Registrera en utvärdering av riskbedömningen.")
    parser.add_argument("byra")
    parser.add_argument("--beskrivning", required=True, help="Vad utvärderingen omfattade och vad den ledde till.")
    parser.add_argument("--datum", type=datumargument, default=None, help="Standard är dagens datum.")
    parser.set_defaults(kor=kor_utvardera)


def kor_utvardera(args: argparse.Namespace) -> int:
    mapp = befintlig_byramapp(args.byra)
    datum = args.datum or date.today()
    historik = las_historik(mapp).med(Handelse(datum=datum, typ="utvärdering", beskrivning=args.beskrivning))
    spara_historik(mapp, historik)
    print(f"Utvärdering registrerad {datum.isoformat()}. Nästa genomgång senast {historik.nasta_genomgang()}.")
    return 0
```

- [ ] **Step 6: Registrera kommandot i `src/riskanalys/cli.py`**

Ersätt raderna

```python
from riskanalys.kommandon import profil_kommando, regelbas_kommando

KOMMANDON = [regelbas_kommando, profil_kommando]
```

med

```python
from riskanalys.kommandon import drift_kommando, profil_kommando, regelbas_kommando

KOMMANDON = [regelbas_kommando, profil_kommando, drift_kommando]
```

- [ ] **Step 7: Kör testet**

Run: `.venv/bin/pytest tester/enhet/test_historik.py -v`
Expected: alla tester passerar.

- [ ] **Step 8: Commit**

```bash
git add src/riskanalys/drift src/riskanalys/kommandon/drift_kommando.py src/riskanalys/cli.py tester/enhet/test_historik.py
git commit -m "feat: versionshistorik, nästa genomgång och kommandot utvardera"
```

---

### Task 12: Deterministisk riskmotor

**Files:**
- Create: `src/riskanalys/bedomning/__init__.py`, `modeller.py`, `motor.py`
- Test: `tester/regelkontrakt/test_motor.py`

**Interfaces:**
- Consumes: `Regelbas`, `Tjanst`, `Sarbarhet`, `Kontroll`, `MatrisRad`, typaliasen `Sannolikhet`, `Konsekvens`, `Risk`, `Urval`, `Profil.faltvarden()`, `tolka_villkor`, `utvardera`, `Sanning`, `Kunskap`, `Faltvarde`, `Utfall`.
- Produces:
  - `bedomning/modeller.py`: `Riskdel(sannolikhet, konsekvens, risk)`, `Kontrollbedomning(id, utformning: str | None, genomforande: str | None, fungerar_och_ar_belagd: bool)`, `Tjanstbedomning(tjanst, erbjuds: bool | None, status: Literal["preliminär", "slutlig"], hot: tuple[str, ...], tillampade_sarbarheter: tuple[str, ...], inneboende: Riskdel | None, terrorfinansiering: Riskdel | None, kontroller: tuple[Kontrollbedomning, ...], kvarstaende: Risk | None, regelspar: tuple[str, ...], okanda_uppgifter: tuple[str, ...])`, `Bedomning(byra, regelpaket, datum, lan, regelbas_version, regelbas_kontrollsumma, status, tjanster: tuple[Tjanstbedomning, ...])`.
  - `bedomning/motor.py`: `SANNOLIKHETER`, `RISKNIVAER`, `TF_KONSEKVENS = "allvarlig"`, `steg(niva: str, antal: int, skala: tuple[str, ...]) -> str`, `bedom(regelbas, urval, profil) -> Bedomning`, `bedom_tjanst(regelbas, tjanst, profil) -> Tjanstbedomning`.
- `regelspar` har alltid ordningen: sannolikhetsregel, konsekvensregel, matrisrad för inneboende risk, terrorfinansieringsregel, matrisrad för terrorfinansiering, regel för kvarstående risk.

Metoden (spec 7, regler i `beslutstabeller/metod.yaml`):

1. En tjänst som inte erbjuds får inga nivåer. Är det okänt om den erbjuds bedöms den ändå, preliminärt.
2. Sannolikheten börjar på tjänstens grundnivå och höjs med effekten av varje sårbarhet som gäller (BT-SANN-01). Ett okänt villkor gäller preliminärt om sårbarheten har `vid_okant: preliminart_galler`.
3. Konsekvensen är tjänstens grundnivå (BT-KONS-01). Risken läses ur riskmatrisen.
4. Terrorfinansiering bedöms separat med egen grundnivå och konsekvensen allvarlig (BT-TF-01).
5. En kontroll fungerar bara om den finns i rutinerna och är belagd. Finns minst en sådan sänks risken ett steg (BT-KVAR-02), annars är den kvarstående risken lika med den inneboende (BT-KVAR-01).
6. Varje okänd uppgift som påverkar resultatet listas, och bedömningen blir preliminär.

- [ ] **Step 1: Skriv det felande testet `tester/regelkontrakt/test_motor.py`**

```python
from datetime import date

import pytest

from riskanalys.bedomning.motor import RISKNIVAER, SANNOLIKHETER, bedom, steg
from riskanalys.regelverk.urval import valj


def _bedom(regelbas, profil):
    urval = valj(regelbas, "RP-RED-VG", date(2026, 11, 1), "Västra Götaland")
    return bedom(regelbas, urval, profil)


def _nivaer(del_):
    return (del_.sannolikhet, del_.konsekvens, del_.risk)


def test_verklighetsnara_fall(regelbas, profil_fabrik, real_varden):
    bedomning = _bedom(regelbas, profil_fabrik(regelbas, real_varden))
    (tjanst,) = bedomning.tjanster
    assert bedomning.status == "slutlig"
    assert tjanst.erbjuds is True
    assert tjanst.tillampade_sarbarheter == ("S-KUND-01", "S-KANAL-01")
    assert _nivaer(tjanst.inneboende) == ("hög", "betydande", "hög")
    assert _nivaer(tjanst.terrorfinansiering) == ("låg", "allvarlig", "måttlig")
    assert tjanst.kvarstaende == "hög"
    assert tjanst.regelspar == ("BT-SANN-01", "BT-KONS-01", "BT-MATRIS-08", "BT-TF-01", "BT-MATRIS-03", "BT-KVAR-01")
    assert tjanst.okanda_uppgifter == ()


def test_belagd_kontroll_sanker_kvarstaende_risk_ett_steg(regelbas, profil_fabrik, real_varden):
    varden = {**real_varden, "P-KONTROLL.C-07.genomforande": "belagt"}
    (tjanst,) = _bedom(regelbas, profil_fabrik(regelbas, varden)).tjanster
    assert tjanst.kontroller[0].fungerar_och_ar_belagd is True
    assert tjanst.kvarstaende == "måttlig"
    assert tjanst.regelspar[-1] == "BT-KVAR-02"


def test_kontroll_som_saknas_i_rutinerna_sanker_inte_risken(regelbas, profil_fabrik, real_varden):
    varden = {**real_varden, "P-KONTROLL.C-07.utformning": "saknas", "P-KONTROLL.C-07.genomforande": "belagt"}
    (tjanst,) = _bedom(regelbas, profil_fabrik(regelbas, varden)).tjanster
    assert tjanst.kvarstaende == "hög"
    assert tjanst.regelspar[-1] == "BT-KVAR-01"


def test_tjanst_som_inte_erbjuds_far_inga_nivaer(regelbas, profil_fabrik, real_varden):
    varden = {**real_varden, "P-TJ.T-RED-01.erbjuds": False}
    bedomning = _bedom(regelbas, profil_fabrik(regelbas, varden))
    (tjanst,) = bedomning.tjanster
    assert tjanst.erbjuds is False
    assert tjanst.inneboende is None
    assert tjanst.kvarstaende is None
    assert bedomning.status == "slutlig"


def test_okand_uppgift_ger_forsiktig_och_preliminar_bedomning(regelbas, profil_fabrik, real_varden):
    profil = profil_fabrik(regelbas, real_varden, okanda=("P-KUND.andel_riskbransch",))
    bedomning = _bedom(regelbas, profil)
    (tjanst,) = bedomning.tjanster
    assert bedomning.status == "preliminär"
    assert tjanst.okanda_uppgifter == ("P-KUND.andel_riskbransch",)
    assert "S-KUND-01" in tjanst.tillampade_sarbarheter


def test_okant_erbjudande_bedoms_preliminart(regelbas, profil_fabrik, real_varden):
    profil = profil_fabrik(regelbas, real_varden, okanda=("P-TJ.T-RED-01.erbjuds",))
    (tjanst,) = _bedom(regelbas, profil).tjanster
    assert tjanst.erbjuds is None
    assert tjanst.inneboende is not None
    assert tjanst.status == "preliminär"


def test_okand_kontrolluppgift_ger_preliminar_bedomning(regelbas, profil_fabrik, real_varden):
    profil = profil_fabrik(regelbas, real_varden, okanda=("P-KONTROLL.C-07.genomforande",))
    (tjanst,) = _bedom(regelbas, profil).tjanster
    assert tjanst.okanda_uppgifter == ("P-KONTROLL.C-07.genomforande",)
    assert tjanst.kontroller[0].fungerar_och_ar_belagd is False
    assert tjanst.kvarstaende == "hög"


def test_alla_sarbarheter_ger_hogsta_sannolikhet_och_hojd_terrorfinansiering(regelbas, profil_fabrik, real_varden):
    varden = {**real_varden, "P-KUND.andel_kontant": 0.2, "P-VERK.juniora_konsulter": True}
    (tjanst,) = _bedom(regelbas, profil_fabrik(regelbas, varden)).tjanster
    assert tjanst.inneboende.sannolikhet == "hög"
    assert _nivaer(tjanst.terrorfinansiering) == ("medel", "allvarlig", "hög")
    assert tjanst.regelspar[4] == "BT-MATRIS-06"


def test_ingen_sarbarhet_ger_grundnivaerna(regelbas, profil_fabrik, real_varden):
    varden = {**real_varden, "P-KUND.andel_riskbransch": 0.1, "P-KANAL.andel_digitalt_underlag": 0.2}
    (tjanst,) = _bedom(regelbas, profil_fabrik(regelbas, varden)).tjanster
    assert tjanst.tillampade_sarbarheter == ()
    assert _nivaer(tjanst.inneboende) == ("medel", "betydande", "måttlig")
    assert tjanst.regelspar[2] == "BT-MATRIS-05"


@pytest.mark.parametrize(
    ("niva", "antal", "skala", "vantat"),
    [
        ("medel", 2, SANNOLIKHETER, "hög"),
        ("låg", -1, SANNOLIKHETER, "låg"),
        ("mycket hög", -1, RISKNIVAER, "hög"),
        ("låg", -1, RISKNIVAER, "låg"),
    ],
)
def test_steg_stannar_inom_skalan(niva, antal, skala, vantat):
    assert steg(niva, antal, skala) == vantat


def test_bedomningen_ar_deterministisk_och_bar_regelbasens_version(regelbas, profil_fabrik, real_varden):
    profil = profil_fabrik(regelbas, real_varden)
    forsta, andra = _bedom(regelbas, profil), _bedom(regelbas, profil)
    assert forsta == andra
    assert forsta.regelbas_version == "0.1.0"
    assert forsta.regelbas_kontrollsumma == regelbas.kontrollsumma
```

- [ ] **Step 2: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/regelkontrakt/test_motor.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.bedomning'`.

- [ ] **Step 3: Skriv `src/riskanalys/bedomning/__init__.py`**

```python
"""Riskbedömning: deterministisk motor och körningar."""
```

- [ ] **Step 4: Skriv `src/riskanalys/bedomning/modeller.py`**

```python
"""Bedömningsresultat (spec 7). Allt här kommer från motorn, inget från AI."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict

from riskanalys.regelverk.modeller import Konsekvens, Risk, Sannolikhet

Bedomningsstatus = Literal["preliminär", "slutlig"]


class Fryst(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Riskdel(Fryst):
    sannolikhet: Sannolikhet
    konsekvens: Konsekvens
    risk: Risk


class Kontrollbedomning(Fryst):
    id: str
    utformning: str | None
    genomforande: str | None
    fungerar_och_ar_belagd: bool


class Tjanstbedomning(Fryst):
    tjanst: str
    erbjuds: bool | None
    status: Bedomningsstatus
    hot: tuple[str, ...]
    tillampade_sarbarheter: tuple[str, ...]
    inneboende: Riskdel | None
    terrorfinansiering: Riskdel | None
    kontroller: tuple[Kontrollbedomning, ...]
    kvarstaende: Risk | None
    regelspar: tuple[str, ...]
    okanda_uppgifter: tuple[str, ...]


class Bedomning(Fryst):
    byra: str
    regelpaket: str
    datum: date
    lan: str
    regelbas_version: str
    regelbas_kontrollsumma: str
    status: Bedomningsstatus
    tjanster: tuple[Tjanstbedomning, ...]
```

- [ ] **Step 5: Skriv `src/riskanalys/bedomning/motor.py`**

```python
"""Deterministisk riskmotor (spec 7). Samma regelbas och profil ger alltid samma resultat."""

from riskanalys.bedomning.modeller import Bedomning, Kontrollbedomning, Riskdel, Tjanstbedomning
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Konsekvens, Kontroll, MatrisRad, Regelbas, Risk, Sannolikhet, Sarbarhet, Tjanst
from riskanalys.regelverk.urval import Urval
from riskanalys.regelverk.villkor import Faltvarde, Kunskap, Sanning, Utfall, tolka_villkor, utvardera

SANNOLIKHETER: tuple[Sannolikhet, ...] = ("låg", "medel", "hög")
RISKNIVAER: tuple[Risk, ...] = ("låg", "måttlig", "hög", "mycket hög")
TF_KONSEKVENS: Konsekvens = "allvarlig"
PENNINGTVATT = frozenset({"penningtvatt", "bada"})
TERRORFINANSIERING = frozenset({"terrorfinansiering", "bada"})
_OKAND = Faltvarde(Kunskap.OKAND)


def steg(niva: str, antal: int, skala: tuple[str, ...]) -> str:
    """Flyttar en nivå i skalan, som lägst till första och som högst till sista nivån."""
    index = min(max(skala.index(niva) + antal, 0), len(skala) - 1)
    return skala[index]


def bedom(regelbas: Regelbas, urval: Urval, profil: Profil) -> Bedomning:
    tjanster = tuple(bedom_tjanst(regelbas, regelbas.tjanster[tjanst_id], profil) for tjanst_id in urval.tjanster)
    preliminar = any(tjanst.status == "preliminär" for tjanst in tjanster)
    return Bedomning(
        byra=profil.byra.id,
        regelpaket=urval.regelpaket.id,
        datum=urval.datum,
        lan=urval.lan,
        regelbas_version=regelbas.version,
        regelbas_kontrollsumma=regelbas.kontrollsumma,
        status="preliminär" if preliminar else "slutlig",
        tjanster=tjanster,
    )


def bedom_tjanst(regelbas: Regelbas, tjanst: Tjanst, profil: Profil) -> Tjanstbedomning:
    varden = profil.faltvarden()
    erbjuds = varden.get(tjanst.erbjuds_falt, _OKAND)
    if erbjuds.kunskap is Kunskap.EJ_TILLAMPLIG or (erbjuds.kunskap is Kunskap.KAND and erbjuds.varde is False):
        return _erbjuds_inte(tjanst)
    okant_erbjudande = frozenset({tjanst.erbjuds_falt}) if erbjuds.kunskap is Kunskap.OKAND else frozenset()
    sarbarheter, okanda_sarbarheter = _tillampade_sarbarheter(regelbas, tjanst, varden)
    kontroller, okanda_kontroller = _kontroller(regelbas, tjanst, varden)
    hojning = _hojning(sarbarheter, PENNINGTVATT)
    inneboende, rad = _riskdel(regelbas, tjanst.grund_sannolikhet, tjanst.grund_konsekvens, hojning)
    tf_hojning = _hojning(sarbarheter, TERRORFINANSIERING)
    terrorfinansiering, tf_rad = _riskdel(regelbas, tjanst.grund_tf_sannolikhet, TF_KONSEKVENS, tf_hojning)
    kvarstaende, kvar_regel = _kvarstaende(regelbas, inneboende.risk, kontroller)
    okanda = okant_erbjudande | okanda_sarbarheter | okanda_kontroller
    metod = regelbas.metod
    return Tjanstbedomning(
        tjanst=tjanst.id,
        erbjuds=None if okant_erbjudande else True,
        status="preliminär" if okanda else "slutlig",
        hot=tjanst.hot,
        tillampade_sarbarheter=tuple(sarbarhet.id for sarbarhet in sarbarheter),
        inneboende=inneboende,
        terrorfinansiering=terrorfinansiering,
        kontroller=kontroller,
        kvarstaende=kvarstaende,
        regelspar=(metod.sannolikhet.id, metod.konsekvens.id, rad.id, metod.terrorfinansiering.id, tf_rad.id, kvar_regel),
        okanda_uppgifter=tuple(sorted(okanda)),
    )


def _erbjuds_inte(tjanst: Tjanst) -> Tjanstbedomning:
    return Tjanstbedomning(
        tjanst=tjanst.id,
        erbjuds=False,
        status="slutlig",
        hot=(),
        tillampade_sarbarheter=(),
        inneboende=None,
        terrorfinansiering=None,
        kontroller=(),
        kvarstaende=None,
        regelspar=(),
        okanda_uppgifter=(),
    )


def _tillampade_sarbarheter(
    regelbas: Regelbas, tjanst: Tjanst, varden: dict[str, Faltvarde]
) -> tuple[tuple[Sarbarhet, ...], frozenset[str]]:
    definitioner = regelbas.faltdefinitioner()
    utfall = [
        (sarbarhet, utvardera(tolka_villkor(sarbarhet.villkor, definitioner), varden))
        for sarbarhet in (regelbas.sarbarheter[sarbarhet_id] for sarbarhet_id in tjanst.sarbarheter)
    ]
    tillampade = tuple(sarbarhet for sarbarhet, resultat in utfall if _galler(sarbarhet, resultat))
    okanda = frozenset().union(*(resultat.okanda for _, resultat in utfall))
    return tillampade, okanda


def _galler(sarbarhet: Sarbarhet, utfall: Utfall) -> bool:
    if utfall.sanning is Sanning.OKANT:
        return sarbarhet.vid_okant == "preliminart_galler"
    return utfall.sanning is Sanning.SANT


def _hojning(sarbarheter: tuple[Sarbarhet, ...], galler: frozenset[str]) -> int:
    return sum(sarbarhet.effekt.sannolikhet for sarbarhet in sarbarheter if sarbarhet.galler in galler)


def _riskdel(regelbas: Regelbas, grund: str, konsekvens: str, hojning: int) -> tuple[Riskdel, MatrisRad]:
    sannolikhet = steg(grund, hojning, SANNOLIKHETER)
    rad = next(
        rad
        for rad in regelbas.metod.riskmatris
        if rad.sannolikhet == sannolikhet and rad.konsekvens == konsekvens
    )
    return Riskdel(sannolikhet=sannolikhet, konsekvens=konsekvens, risk=rad.risk), rad


def _kontroller(
    regelbas: Regelbas, tjanst: Tjanst, varden: dict[str, Faltvarde]
) -> tuple[tuple[Kontrollbedomning, ...], frozenset[str]]:
    resultat = [_kontroll(regelbas.kontroller[kontroll_id], varden) for kontroll_id in tjanst.kontroller]
    return tuple(bedomning for bedomning, _ in resultat), frozenset().union(*(okanda for _, okanda in resultat))


def _kontroll(kontroll: Kontroll, varden: dict[str, Faltvarde]) -> tuple[Kontrollbedomning, frozenset[str]]:
    utformning = varden.get(kontroll.utformning_falt, _OKAND)
    genomforande = varden.get(kontroll.genomforande_falt, _OKAND)
    okanda = frozenset(
        falt_id
        for falt_id, varde in ((kontroll.utformning_falt, utformning), (kontroll.genomforande_falt, genomforande))
        if varde.kunskap is Kunskap.OKAND
    )
    bedomning = Kontrollbedomning(
        id=kontroll.id,
        utformning=_kant(utformning),
        genomforande=_kant(genomforande),
        fungerar_och_ar_belagd=_kant(utformning) == "finns" and _kant(genomforande) == "belagt",
    )
    return bedomning, okanda


def _kant(varde: Faltvarde) -> str | None:
    return varde.varde if varde.kunskap is Kunskap.KAND else None


def _kvarstaende(regelbas: Regelbas, risk: str, kontroller: tuple[Kontrollbedomning, ...]) -> tuple[str, str]:
    if any(kontroll.fungerar_och_ar_belagd for kontroll in kontroller):
        return steg(risk, -1, RISKNIVAER), regelbas.metod.kvarstaende_sankning.id
    return risk, regelbas.metod.kvarstaende_ej_belagd.id
```

- [ ] **Step 6: Kör testet**

Run: `.venv/bin/pytest tester/regelkontrakt/test_motor.py -v`
Expected: alla tester passerar.

- [ ] **Step 7: Commit**

```bash
git add src/riskanalys/bedomning tester/regelkontrakt/test_motor.py
git commit -m "feat: deterministisk riskmotor med regelspår och preliminära resultat"
```

---

### Task 13: Körningar och kommandot `bedom`

**Files:**
- Create: `src/riskanalys/lagring/korningar.py`
- Create: `src/riskanalys/bedomning/korning.py`
- Create: `src/riskanalys/kommandon/bedom_kommando.py`
- Modify: `src/riskanalys/cli.py`
- Modify: `tester/conftest.py` (fixturen `byra_med_profil`)
- Test: `tester/enhet/test_korningar.py`, `tester/enhet/test_bedomning_korning.py`

**Interfaces:**
- Consumes: `skriv_manifest`, `las_manifest`, `MANIFESTNAMN`, `for_fil`, `las_yaml`, `las_profil`, `PROFILFIL`, `valj`, `bedom`, `Bedomning`, `Profil`, `RiskanalysFel`.
- Produces:
  - `lagring/korningar.py`: `TIDSFORMAT`, `ny_korningsmapp(byramapp: Path, undermapp: str) -> Path`, `avslutade_korningar(byramapp: Path, undermapp: str) -> list[Path]` (bara mappar med manifest, äldst först), `senaste_korning(byramapp: Path, undermapp: str, kommando: str) -> Path` (fel som säger vilket kommando som ska köras).
  - `bedomning/korning.py`: `BEDOMNINGAR = "bedomningar"`, `BEDOMNINGSFIL = "bedomning.json"`, `PROFILKOPIA = "profil.yaml"`, `kor_bedomning(byramapp: Path, regelbas: Regelbas) -> Path`, `las_bedomning(mapp: Path) -> Bedomning`, `las_bedomningsprofil(mapp: Path) -> Profil`, `profilen_har_andrats(byramapp: Path, bedomningsmapp: Path) -> bool`, `regelbasen_har_andrats(bedomningsmapp: Path, regelbas: Regelbas) -> bool`, `aktualitetshinder(byramapp: Path, bedomningsmapp: Path, regelbas: Regelbas) -> list[str]` och `kontrollera_aktuell(byramapp: Path, bedomningsmapp: Path, regelbas: Regelbas) -> None` (kastar `RiskanalysFel` med samma meddelanden). Senare steg (skriv, granska, faststall) använder dem.
  - `kommandon/bedom_kommando.py`: `beskriv_tjanstbedomning(regelbas, tjanst: Tjanstbedomning) -> str` och kommandot `bedom <byra>`.
  - Fixtur `byra_med_profil`: en byrå i datamappen med det verklighetsnära testfallets uppgifter bekräftade. Returnerar byråmappen.
- Manifestets metadata för en bedömning: `typ`, `regelpaket`, `datum`, `lan`, `regelbas_version`, `regelbas_kontrollsumma`, `status`.

Varje körning sparas i en ny tidsstämplad mapp och skrivs aldrig över. En körning utan manifest avbröts och räknas inte. Bedömningsmappen innehåller en exakt kopia av profilen, så att senare steg kan upptäcka om profilen ändrats.

- [ ] **Step 1: Lägg till fixturen sist i `tester/conftest.py`**

```python
@pytest.fixture
def byra_med_profil(datamapp, regelbas, profil_fabrik, real_varden):
    """En byrå i datamappen där alla uppgifter i det verklighetsnära testfallet är bekräftade."""
    from riskanalys.lagring.datamapp import skapa_byramapp
    from riskanalys.profil.lagring import spara_profil

    mapp = skapa_byramapp("testbyra")
    spara_profil(mapp, profil_fabrik(regelbas, real_varden))
    return mapp
```

- [ ] **Step 2: Skriv det felande testet `tester/enhet/test_korningar.py`**

```python
import pytest

from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.korningar import avslutade_korningar, ny_korningsmapp, senaste_korning
from riskanalys.lagring.manifest import skriv_manifest


def test_utan_korning_namns_kommandot_som_ska_koras_forst(tmp_path):
    with pytest.raises(RiskanalysFel, match="Kör 'riskanalys bedom testbyra' först"):
        senaste_korning(tmp_path, "bedomningar", "bedom testbyra")


def test_korningsmappar_skrivs_aldrig_over(tmp_path):
    mappar = [ny_korningsmapp(tmp_path, "x") for _ in range(3)]
    assert len(set(mappar)) == 3
    for mapp in mappar:
        skriv_manifest(mapp, {})
    assert avslutade_korningar(tmp_path, "x") == mappar


def test_avbruten_korning_utan_manifest_raknas_inte(tmp_path):
    forsta = ny_korningsmapp(tmp_path, "x")
    skriv_manifest(forsta, {})
    ny_korningsmapp(tmp_path, "x")
    assert senaste_korning(tmp_path, "x", "k") == forsta
```

- [ ] **Step 3: Skriv det felande testet `tester/enhet/test_bedomning_korning.py`**

```python
from datetime import date

import pytest

from riskanalys.bedomning.korning import (
    BEDOMNINGSFIL,
    aktualitetshinder,
    kontrollera_aktuell,
    kor_bedomning,
    las_bedomning,
    las_bedomningsprofil,
    profilen_har_andrats,
    regelbasen_har_andrats,
)
from riskanalys.cli import main
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.datamapp import skapa_byramapp
from riskanalys.lagring.manifest import las_manifest, verifiera_manifest
from riskanalys.profil.hantering import bekrafta
from riskanalys.profil.lagring import las_profil, spara_profil


def test_korningen_sparar_bedomning_profilkopia_och_manifest(byra_med_profil, regelbas):
    mapp = kor_bedomning(byra_med_profil, regelbas)
    assert verifiera_manifest(mapp) == []
    metadata = las_manifest(mapp).metadata
    assert metadata["typ"] == "bedomning"
    assert metadata["regelbas_kontrollsumma"] == regelbas.kontrollsumma
    assert metadata["status"] == "slutlig"
    assert las_bedomning(mapp).tjanster[0].kvarstaende == "hög"
    assert las_bedomningsprofil(mapp) == las_profil(byra_med_profil)


def test_andrad_profil_upptacks(byra_med_profil, regelbas):
    mapp = kor_bedomning(byra_med_profil, regelbas)
    assert not profilen_har_andrats(byra_med_profil, mapp)
    profil = bekrafta(
        las_profil(byra_med_profil), regelbas, "P-KUND.andel_kontant", "20 %", "Kassarapport", "FfR", date(2026, 10, 2)
    )
    spara_profil(byra_med_profil, profil)
    assert profilen_har_andrats(byra_med_profil, mapp)


def test_andrad_regelbas_upptacks(byra_med_profil, regelbas, minimal_regelbas):
    mapp = kor_bedomning(byra_med_profil, regelbas)
    assert not regelbasen_har_andrats(mapp, regelbas)
    assert regelbasen_har_andrats(mapp, minimal_regelbas)


def test_aktuell_bedomning_har_inga_hinder(byra_med_profil, regelbas):
    mapp = kor_bedomning(byra_med_profil, regelbas)
    assert aktualitetshinder(byra_med_profil, mapp, regelbas) == []
    kontrollera_aktuell(byra_med_profil, mapp, regelbas)


def test_andrad_profil_ger_hinder_som_sager_vad_som_ska_goras(byra_med_profil, regelbas):
    mapp = kor_bedomning(byra_med_profil, regelbas)
    profil = bekrafta(
        las_profil(byra_med_profil), regelbas, "P-ORG.antal_anstallda", "9", "Lönelistan", "FfR", date(2026, 10, 2)
    )
    spara_profil(byra_med_profil, profil)
    with pytest.raises(RiskanalysFel, match="Profilen har ändrats sedan bedömningen. Kör 'riskanalys bedom' igen."):
        kontrollera_aktuell(byra_med_profil, mapp, regelbas)


def test_manipulerad_bedomningsfil_ger_hinder(byra_med_profil, regelbas):
    mapp = kor_bedomning(byra_med_profil, regelbas)
    fil = mapp / BEDOMNINGSFIL
    fil.write_text(fil.read_text(encoding="utf-8").replace('"hög"', '"låg"'), encoding="utf-8")
    assert any("Fil ändrad: bedomning.json" in rad for rad in aktualitetshinder(byra_med_profil, mapp, regelbas))


def test_bedom_kommandot_visar_nivaerna(byra_med_profil, capsys):
    assert main(["bedom", "testbyra"]) == 0
    utskrift = capsys.readouterr().out
    assert "T-RED-01 Löpande bokföring: inneboende risk hög, terrorfinansiering måttlig, kvarstående risk hög." in utskrift


def test_bedom_med_okand_uppgift_ar_preliminar(datamapp, regelbas, profil_fabrik, real_varden, capsys):
    mapp = skapa_byramapp("testbyra")
    spara_profil(mapp, profil_fabrik(regelbas, real_varden, okanda=("P-KUND.andel_kontant",)))
    assert main(["bedom", "testbyra"]) == 0
    assert "preliminär" in capsys.readouterr().out


def test_bedom_for_okand_byra(datamapp, capsys):
    assert main(["bedom", "saknas"]) == 1
    assert "finns inte" in capsys.readouterr().err
```

- [ ] **Step 4: Kör testerna för att se att de fallerar**

Run: `.venv/bin/pytest tester/enhet/test_korningar.py tester/enhet/test_bedomning_korning.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.lagring.korningar'`.

- [ ] **Step 5: Skriv `src/riskanalys/lagring/korningar.py`**

```python
"""Tidsstämplade körningsmappar. Varje körning sparas i en egen mapp och skrivs aldrig över."""

from datetime import datetime
from pathlib import Path

from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.manifest import MANIFESTNAMN

TIDSFORMAT = "%Y%m%dT%H%M%S%f"
_MAX_FORSOK = 100


def ny_korningsmapp(byramapp: Path, undermapp: str) -> Path:
    rot = byramapp / undermapp
    rot.mkdir(parents=True, exist_ok=True)
    stampel = datetime.now().strftime(TIDSFORMAT)
    for nummer in range(_MAX_FORSOK):
        mapp = rot / (stampel if nummer == 0 else f"{stampel}-{nummer:02d}")
        try:
            mapp.mkdir()
        except FileExistsError:
            continue
        return mapp
    raise RiskanalysFel(f"Kunde inte skapa en ny körningsmapp i {rot}.")


def avslutade_korningar(byramapp: Path, undermapp: str) -> list[Path]:
    """Körningar med manifest, äldst först. En körning utan manifest avbröts och räknas inte."""
    rot = byramapp / undermapp
    if not rot.is_dir():
        return []
    return sorted(mapp for mapp in rot.iterdir() if (mapp / MANIFESTNAMN).is_file())


def senaste_korning(byramapp: Path, undermapp: str, kommando: str) -> Path:
    korningar = avslutade_korningar(byramapp, undermapp)
    if not korningar:
        raise RiskanalysFel(f"Det finns ingen körning i {undermapp}. Kör 'riskanalys {kommando}' först.")
    return korningar[-1]
```

- [ ] **Step 6: Skriv `src/riskanalys/bedomning/korning.py`**

```python
"""Bedömningskörning: sparar bedömningen med en kopia av profilen och ett manifest (spec 5.3)."""

import shutil
from pathlib import Path

from riskanalys.bedomning.modeller import Bedomning
from riskanalys.bedomning.motor import bedom
from riskanalys.lagring.kontrollsumma import for_fil
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.korningar import ny_korningsmapp
from riskanalys.lagring.manifest import las_manifest, skriv_manifest, verifiera_manifest
from riskanalys.lagring.yamlfil import las_yaml
from riskanalys.profil.lagring import PROFILFIL, las_profil
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.urval import valj

BEDOMNINGAR = "bedomningar"
BEDOMNINGSFIL = "bedomning.json"
PROFILKOPIA = "profil.yaml"


def kor_bedomning(byramapp: Path, regelbas: Regelbas) -> Path:
    profil = las_profil(byramapp)
    byra = profil.byra
    bedomning = bedom(regelbas, valj(regelbas, byra.regelpaket, byra.datum, byra.lan), profil)
    mapp = ny_korningsmapp(byramapp, BEDOMNINGAR)
    shutil.copyfile(byramapp / PROFILFIL, mapp / PROFILKOPIA)
    (mapp / BEDOMNINGSFIL).write_text(bedomning.model_dump_json(indent=2), encoding="utf-8")
    skriv_manifest(
        mapp,
        {
            "typ": "bedomning",
            "regelpaket": bedomning.regelpaket,
            "datum": bedomning.datum.isoformat(),
            "lan": bedomning.lan,
            "regelbas_version": bedomning.regelbas_version,
            "regelbas_kontrollsumma": bedomning.regelbas_kontrollsumma,
            "status": bedomning.status,
        },
    )
    return mapp


def las_bedomning(mapp: Path) -> Bedomning:
    return Bedomning.model_validate_json((mapp / BEDOMNINGSFIL).read_text(encoding="utf-8"))


def las_bedomningsprofil(mapp: Path) -> Profil:
    return Profil.model_validate(las_yaml(mapp / PROFILKOPIA))


def profilen_har_andrats(byramapp: Path, bedomningsmapp: Path) -> bool:
    return for_fil(byramapp / PROFILFIL) != for_fil(bedomningsmapp / PROFILKOPIA)


def regelbasen_har_andrats(bedomningsmapp: Path, regelbas: Regelbas) -> bool:
    return las_manifest(bedomningsmapp).metadata["regelbas_kontrollsumma"] != regelbas.kontrollsumma


def aktualitetshinder(byramapp: Path, bedomningsmapp: Path, regelbas: Regelbas) -> list[str]:
    """Skäl att inte bygga vidare på bedömningen: ändrade filer, ändrad regelbas eller ändrad profil."""
    andrade = [f"Bedömningen är ändrad efter körningen. {rad}" for rad in verifiera_manifest(bedomningsmapp)]
    regelbas_hinder = (
        ["Regelbasen har ändrats sedan bedömningen. Kör 'riskanalys bedom' igen."]
        if regelbasen_har_andrats(bedomningsmapp, regelbas)
        else []
    )
    profil_hinder = (
        ["Profilen har ändrats sedan bedömningen. Kör 'riskanalys bedom' igen."]
        if profilen_har_andrats(byramapp, bedomningsmapp)
        else []
    )
    return andrade + regelbas_hinder + profil_hinder


def kontrollera_aktuell(byramapp: Path, bedomningsmapp: Path, regelbas: Regelbas) -> None:
    hinder = aktualitetshinder(byramapp, bedomningsmapp, regelbas)
    if hinder:
        raise RiskanalysFel(" ".join(hinder))
```

- [ ] **Step 7: Skriv `src/riskanalys/kommandon/bedom_kommando.py`**

```python
"""riskanalys bedom"""

import argparse
from typing import Any

from riskanalys.bedomning.korning import kor_bedomning, las_bedomning
from riskanalys.bedomning.modeller import Tjanstbedomning
from riskanalys.kommandon import ladda_giltig_regelbas, regelbasargument
from riskanalys.lagring.datamapp import befintlig_byramapp
from riskanalys.regelverk.modeller import Regelbas


def lagg_till(underparsers: Any) -> None:
    parser = underparsers.add_parser("bedom", help="Kör riskmotorn på byråns profil.")
    parser.add_argument("byra")
    regelbasargument(parser)
    parser.set_defaults(kor=kor_bedom)


def beskriv_tjanstbedomning(regelbas: Regelbas, tjanst: Tjanstbedomning) -> str:
    namn = regelbas.tjanster[tjanst.tjanst].namn
    if tjanst.inneboende is None or tjanst.terrorfinansiering is None:
        return f"{tjanst.tjanst} {namn}: erbjuds inte."
    text = (
        f"{tjanst.tjanst} {namn}: inneboende risk {tjanst.inneboende.risk}, "
        f"terrorfinansiering {tjanst.terrorfinansiering.risk}, kvarstående risk {tjanst.kvarstaende}."
    )
    if tjanst.okanda_uppgifter:
        text += f" Preliminär. Okända uppgifter: {', '.join(tjanst.okanda_uppgifter)}."
    return text


def kor_bedom(args: argparse.Namespace) -> int:
    byramapp = befintlig_byramapp(args.byra)
    regelbas = ladda_giltig_regelbas(args.regelbas)
    mapp = kor_bedomning(byramapp, regelbas)
    bedomning = las_bedomning(mapp)
    for tjanst in bedomning.tjanster:
        print(beskriv_tjanstbedomning(regelbas, tjanst))
    if bedomning.status == "preliminär":
        print("Bedömningen är preliminär. Den kan inte fastställas förrän de okända uppgifterna är bekräftade.")
    print(f"Sparad i {mapp}.")
    print(f"Nästa steg: 'riskanalys skriv {args.byra}'.")
    return 0
```

- [ ] **Step 8: Registrera kommandot i `src/riskanalys/cli.py`**

Ersätt raderna

```python
from riskanalys.kommandon import drift_kommando, profil_kommando, regelbas_kommando

KOMMANDON = [regelbas_kommando, profil_kommando, drift_kommando]
```

med

```python
from riskanalys.kommandon import bedom_kommando, drift_kommando, profil_kommando, regelbas_kommando

KOMMANDON = [regelbas_kommando, profil_kommando, drift_kommando, bedom_kommando]
```

- [ ] **Step 9: Kör testerna**

Run: `.venv/bin/pytest tester/enhet/test_korningar.py tester/enhet/test_bedomning_korning.py -v`
Expected: alla tester passerar.

- [ ] **Step 10: Commit**

```bash
git add src/riskanalys/lagring/korningar.py src/riskanalys/bedomning/korning.py src/riskanalys/kommandon/bedom_kommando.py src/riskanalys/cli.py tester/conftest.py tester/enhet/test_korningar.py tester/enhet/test_bedomning_korning.py
git commit -m "feat: tidsstämplade körningar och kommandot bedom"
```

---

### Task 14: AI-underlag ur tillåtelselistan

**Files:**
- Create: `src/riskanalys/dokument/underlag.py`
- Modify: `tester/conftest.py` (fixturerna `underlag_fabrik` och `real_underlag`)
- Test: `tester/enhet/test_underlag.py`

**Interfaces:**
- Consumes: `Bedomning`, `Tjanstbedomning`, `Kontrollbedomning`, modellerna `Avsnittsunderlag`, `UnderlagHot`, `UnderlagSarbarhet`, `UnderlagKontroll`, `UnderlagUppgift`, `UnderlagBrist`, `visa_varde`, `Profil`, `Uppgift`, `tolka_villkor`, `utvardera`, `Sanning`, `RiskanalysFel`.
- Produces:
  - `AVSNITTSTYP = "risk_per_tjanst"`, `SMA_GRUPPER_GRANS = 5`, `INSTRUKTION`, `UnderlagsFel(RiskanalysFel)`.
  - `avsnitt_for_tjanst(nummer: int) -> str` (`D-ARB.6.1`, `D-ARB.6.2` …).
  - `tjanster_med_avsnitt(bedomning: Bedomning) -> list[tuple[str, Tjanstbedomning]]` (bara tjänster med risknivåer).
  - `sarbarhet_status(regelbas, profil, sarbarhet_id) -> Literal["ja", "nej", "okänt"]`.
  - `kontrollstatus(kontroll: Kontrollbedomning) -> str`.
  - `visa_for_ai(regelbas, falt_id, uppgift: Uppgift) -> str`.
  - `bygg_underlag(regelbas, profil, tjanstbedomning, avsnitt_id) -> Avsnittsunderlag`.
  - `NIVANYCKLAR`: nycklarna i `Avsnittsunderlag.nivaer`, i ordningen `inneboende_sannolikhet`, `inneboende_konsekvens`, `inneboende_risk`, `terrorfinansiering_sannolikhet`, `terrorfinansiering_konsekvens`, `terrorfinansiering_risk`, `kvarstaende_risk`. Valideringen i Task 15 binder varje nivå i texten till en av dem.
  - Fixturer: `underlag_fabrik(profil) -> Avsnittsunderlag` (bygger underlaget för den enda tjänsten i repots regelbas) och `real_underlag` (underlaget för det verklighetsnära testfallet).

AI får bara se det som står i tillåtelselistan för avsnittstypen, plus regelbasens egna texter om tjänsten, hoten, sårbarheterna och kontrollerna. Byråns namn och personuppgifter skickas aldrig. Obekräftade uppgifter skickas som "okänt". Heltal i fält märkta `smagrupp` visas som "färre än 5" när de är små (spec 17). Står en personuppgift i tillåtelselistan stoppas bygget, även om valideringen av regelbasen skulle ha missat det.

- [ ] **Step 1: Lägg till fixturer sist i `tester/conftest.py`**

```python
@pytest.fixture
def underlag_fabrik(regelbas):
    """Bygger AI-underlaget för den enda tjänsten i repots regelbas utifrån en profil."""
    from riskanalys.bedomning.motor import bedom
    from riskanalys.dokument.underlag import bygg_underlag, tjanster_med_avsnitt
    from riskanalys.regelverk.urval import valj

    def fabrik(profil):
        byra = profil.byra
        bedomning = bedom(regelbas, valj(regelbas, byra.regelpaket, byra.datum, byra.lan), profil)
        ((avsnitt_id, tjanst),) = tjanster_med_avsnitt(bedomning)
        return bygg_underlag(regelbas, profil, tjanst, avsnitt_id)

    return fabrik


@pytest.fixture
def real_underlag(underlag_fabrik, regelbas, profil_fabrik, real_varden):
    return underlag_fabrik(profil_fabrik(regelbas, real_varden))
```

- [ ] **Step 2: Skriv det felande testet `tester/enhet/test_underlag.py`**

```python
from datetime import date

import pytest

from riskanalys.bedomning.motor import bedom
from riskanalys.dokument.underlag import NIVANYCKLAR, UnderlagsFel, bygg_underlag, tjanster_med_avsnitt
from riskanalys.regelverk.modeller import Tillatelselista
from riskanalys.regelverk.urval import valj


def _bedomning(regelbas, profil):
    return bedom(regelbas, valj(regelbas, "RP-RED-VG", date(2026, 11, 1), "Västra Götaland"), profil)


def test_underlaget_for_lopande_bokforing(real_underlag):
    assert real_underlag.avsnitt == "D-ARB.6.1"
    assert real_underlag.tjanst_id == "T-RED-01"
    assert real_underlag.nivaer == {
        "inneboende_sannolikhet": "hög",
        "inneboende_konsekvens": "betydande",
        "inneboende_risk": "hög",
        "terrorfinansiering_sannolikhet": "låg",
        "terrorfinansiering_konsekvens": "allvarlig",
        "terrorfinansiering_risk": "måttlig",
        "kvarstaende_risk": "hög",
    }
    assert tuple(real_underlag.nivaer) == NIVANYCKLAR
    assert {uppgift.id: uppgift.varde for uppgift in real_underlag.uppgifter} == {
        "P-ORG.antal_anstallda": "8",
        "P-KUND.andel_riskbransch": "30 %",
        "P-KUND.andel_kontant": "5 %",
        "P-KANAL.andel_digitalt_underlag": "80 %",
        "P-KANAL.bankdata_andel": "40 %",
        "P-VERK.juniora_konsulter": "nej",
    }
    assert {post.id: post.galler for post in real_underlag.sarbarheter} == {
        "S-KUND-01": "ja",
        "S-KUND-02": "nej",
        "S-KANAL-01": "ja",
        "S-VERK-01": "nej",
    }
    assert [post.status for post in real_underlag.kontroller] == ["finns i rutinerna men är inte belagd"]
    assert [post.id for post in real_underlag.undvik] == ["B-02", "B-03", "B-04", "B-12", "B-13", "B-24", "B-25"]
    assert "BT-MATRIS-08" in real_underlag.tillatna_id()


def test_underlaget_innehaller_inga_personuppgifter_eller_byranamn(real_underlag):
    text = real_underlag.model_dump_json()
    assert "Testa Testsson" not in text
    assert "Testbyrån AB" not in text


def test_sma_grupper_visas_inte_exakt(underlag_fabrik, regelbas, profil_fabrik, real_varden):
    underlag = underlag_fabrik(profil_fabrik(regelbas, {**real_varden, "P-ORG.antal_anstallda": 3}))
    anstallda = next(uppgift for uppgift in underlag.uppgifter if uppgift.id == "P-ORG.antal_anstallda")
    assert anstallda.varde == "färre än 5"


def test_okand_uppgift_skickas_som_okand(underlag_fabrik, regelbas, profil_fabrik, real_varden):
    underlag = underlag_fabrik(profil_fabrik(regelbas, real_varden, okanda=("P-KUND.andel_riskbransch",)))
    uppgift = next(uppgift for uppgift in underlag.uppgifter if uppgift.id == "P-KUND.andel_riskbransch")
    assert (uppgift.varde, uppgift.bekraftad) == ("okänt", False)
    assert next(post for post in underlag.sarbarheter if post.id == "S-KUND-01").galler == "okänt"


def test_personuppgift_i_tillatelselistan_stoppas(regelbas, profil_fabrik, real_varden):
    lista = regelbas.tillatelselistor["risk_per_tjanst"]
    felaktig = Tillatelselista(id=lista.id, falt=(*lista.falt, "P-ROLL.ffr_namn"), undvik=lista.undvik)
    andrad = regelbas.model_copy(update={"tillatelselistor": {lista.id: felaktig}})
    profil = profil_fabrik(andrad, real_varden)
    ((avsnitt_id, tjanst),) = tjanster_med_avsnitt(_bedomning(andrad, profil))
    with pytest.raises(UnderlagsFel, match="P-ROLL.ffr_namn är en personuppgift"):
        bygg_underlag(andrad, profil, tjanst, avsnitt_id)


def test_tjanst_som_inte_erbjuds_far_inget_riskavsnitt(regelbas, profil_fabrik, real_varden):
    profil = profil_fabrik(regelbas, {**real_varden, "P-TJ.T-RED-01.erbjuds": False})
    assert tjanster_med_avsnitt(_bedomning(regelbas, profil)) == []
```

- [ ] **Step 3: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/enhet/test_underlag.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.dokument.underlag'`.

- [ ] **Step 4: Skriv `src/riskanalys/dokument/underlag.py`**

```python
"""AI-underlag för ett riskavsnitt. Byggs bara ur tillåtelselistan (spec 8.2 och 17)."""

from typing import Literal

from riskanalys.bedomning.modeller import Bedomning, Kontrollbedomning, Tjanstbedomning
from riskanalys.dokument.modeller import (
    Avsnittsunderlag,
    UnderlagBrist,
    UnderlagHot,
    UnderlagKontroll,
    UnderlagSarbarhet,
    UnderlagUppgift,
)
from riskanalys.fel import RiskanalysFel
from riskanalys.profil.hantering import visa_varde
from riskanalys.profil.modeller import Profil, Uppgift
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.villkor import Sanning, tolka_villkor, utvardera

AVSNITTSTYP = "risk_per_tjanst"
SMA_GRUPPER_GRANS = 5
NIVANYCKLAR = (
    "inneboende_sannolikhet",
    "inneboende_konsekvens",
    "inneboende_risk",
    "terrorfinansiering_sannolikhet",
    "terrorfinansiering_konsekvens",
    "terrorfinansiering_risk",
    "kvarstaende_risk",
)
INSTRUKTION = (
    "Skriv avsnittet om risken i tjänsten. Beskriv hur tjänsten kan utnyttjas, analysera hoten och "
    "sårbarheterna och motivera risknivåerna med uppgifterna i underlaget. Återge nivåerna exakt och "
    "skriv tydligt vilken nivå som avser vad, till exempel \"Den kvarstående risken är hög.\" eller "
    "\"Risken för finansiering av terrorism bedöms som måttlig.\" "
    "Hänvisa till ID:n i underlaget i fältet referenser. Saknas en uppgift, skriv [VERIFIERA] och "
    "lägg till en oklarhet."
)
_STATUS = {Sanning.SANT: "ja", Sanning.FALSKT: "nej", Sanning.OKANT: "okänt"}


class UnderlagsFel(RiskanalysFel):
    """AI-underlaget kan inte byggas utan att bryta mot tillåtelselistan."""


def avsnitt_for_tjanst(nummer: int) -> str:
    return f"D-ARB.6.{nummer}"


def tjanster_med_avsnitt(bedomning: Bedomning) -> list[tuple[str, Tjanstbedomning]]:
    """Tjänster med risknivåer, numrerade i ordning. En tjänst som inte erbjuds får inget riskavsnitt."""
    bedomda = [tjanst for tjanst in bedomning.tjanster if tjanst.inneboende is not None]
    return [(avsnitt_for_tjanst(nummer), tjanst) for nummer, tjanst in enumerate(bedomda, start=1)]


def sarbarhet_status(regelbas: Regelbas, profil: Profil, sarbarhet_id: str) -> Literal["ja", "nej", "okänt"]:
    villkor = tolka_villkor(regelbas.sarbarheter[sarbarhet_id].villkor, regelbas.faltdefinitioner())
    return _STATUS[utvardera(villkor, profil.faltvarden()).sanning]


def kontrollstatus(kontroll: Kontrollbedomning) -> str:
    if kontroll.utformning is None:
        return "okänt om kontrollen finns i rutinerna"
    if kontroll.utformning == "saknas":
        return "saknas i rutinerna"
    if kontroll.genomforande is None:
        return "finns i rutinerna, okänt om den är belagd"
    if kontroll.genomforande == "belagt":
        return "finns i rutinerna och är belagd"
    return "finns i rutinerna men är inte belagd"


def visa_for_ai(regelbas: Regelbas, falt_id: str, uppgift: Uppgift) -> str:
    falt = regelbas.falt[falt_id]
    if uppgift.status == "ej_tillämplig":
        return "ej tillämplig"
    if uppgift.status != "bekräftad":
        return "okänt"
    if falt.smagrupp and falt.typ == "heltal" and uppgift.varde < SMA_GRUPPER_GRANS:
        return f"färre än {SMA_GRUPPER_GRANS}"
    return visa_varde(falt, uppgift.varde)


def bygg_underlag(
    regelbas: Regelbas, profil: Profil, tjanstbedomning: Tjanstbedomning, avsnitt_id: str
) -> Avsnittsunderlag:
    lista = regelbas.tillatelselistor[AVSNITTSTYP]
    _kontrollera_lista(regelbas, lista.falt)
    tjanst = regelbas.tjanster[tjanstbedomning.tjanst]
    return Avsnittsunderlag(
        avsnitt=avsnitt_id,
        rubrik=tjanst.namn,
        instruktion=INSTRUKTION,
        tjanst_id=tjanst.id,
        tjanst_namn=tjanst.namn,
        tjanst_beskrivning=tjanst.beskrivning,
        nivaer=_nivaer(tjanstbedomning),
        hot=tuple(
            UnderlagHot(id=hot.id, namn=hot.namn, beskrivning=hot.beskrivning)
            for hot in (regelbas.hot[hot_id] for hot_id in tjanstbedomning.hot)
        ),
        sarbarheter=tuple(
            UnderlagSarbarhet(
                id=sarbarhet_id,
                namn=regelbas.sarbarheter[sarbarhet_id].namn,
                galler=sarbarhet_status(regelbas, profil, sarbarhet_id),
            )
            for sarbarhet_id in tjanst.sarbarheter
        ),
        kontroller=tuple(
            UnderlagKontroll(id=kontroll.id, namn=regelbas.kontroller[kontroll.id].namn, status=kontrollstatus(kontroll))
            for kontroll in tjanstbedomning.kontroller
        ),
        uppgifter=tuple(_uppgift(regelbas, profil, falt_id) for falt_id in lista.falt),
        regelspar=tjanstbedomning.regelspar,
        undvik=tuple(UnderlagBrist(id=brist_id, namn=regelbas.bristmonster[brist_id].namn) for brist_id in lista.undvik),
    )


def _kontrollera_lista(regelbas: Regelbas, falt: tuple[str, ...]) -> None:
    for falt_id in falt:
        if falt_id not in regelbas.falt:
            raise UnderlagsFel(f"Fältet {falt_id} i tillåtelselistan finns inte i regelbasen.")
        if regelbas.falt[falt_id].personuppgift:
            raise UnderlagsFel(f"Fältet {falt_id} är en personuppgift och får inte skickas till AI. Rätta tillåtelselistan.")


def _nivaer(tjanst: Tjanstbedomning) -> dict[str, str]:
    if tjanst.inneboende is None or tjanst.terrorfinansiering is None or tjanst.kvarstaende is None:
        raise UnderlagsFel(f"Tjänsten {tjanst.tjanst} saknar risknivåer och kan inte få ett riskavsnitt.")
    return {
        "inneboende_sannolikhet": tjanst.inneboende.sannolikhet,
        "inneboende_konsekvens": tjanst.inneboende.konsekvens,
        "inneboende_risk": tjanst.inneboende.risk,
        "terrorfinansiering_sannolikhet": tjanst.terrorfinansiering.sannolikhet,
        "terrorfinansiering_konsekvens": tjanst.terrorfinansiering.konsekvens,
        "terrorfinansiering_risk": tjanst.terrorfinansiering.risk,
        "kvarstaende_risk": tjanst.kvarstaende,
    }


def _uppgift(regelbas: Regelbas, profil: Profil, falt_id: str) -> UnderlagUppgift:
    uppgift = profil.uppgifter.get(falt_id, Uppgift())
    return UnderlagUppgift(
        id=falt_id,
        fraga=regelbas.falt[falt_id].fraga,
        varde=visa_for_ai(regelbas, falt_id, uppgift),
        bekraftad=uppgift.status == "bekräftad",
    )
```

- [ ] **Step 5: Kör testet**

Run: `.venv/bin/pytest tester/enhet/test_underlag.py -v`
Expected: alla tester passerar.

- [ ] **Step 6: Commit**

```bash
git add src/riskanalys/dokument/underlag.py tester/conftest.py tester/enhet/test_underlag.py
git commit -m "feat: AI-underlag ur tillåtelselistan utan personuppgifter"
```

---

### Task 15: Maskinell validering av AI-utkast

**Files:**
- Create: `src/riskanalys/dokument/validering.py`
- Modify: `tester/conftest.py` (fixturen `giltigt_utkast`)
- Test: `tester/enhet/test_validering_utkast.py`

**Interfaces:**
- Consumes: `AvsnittsUtkast`, `Avsnittsunderlag`, `Textstycke`, fixturerna `real_underlag`, `underlag_fabrik`, `profil_fabrik`.
- Produces:
  - `VERIFIERA = "[VERIFIERA]"`, `FORBJUDNA_FORMULERINGAR: tuple[str, ...]`, `BENAMNINGAR: dict[str, str]` (nivånyckel till text i felmeddelanden).
  - `nivapastaenden(text: str) -> list[tuple[str, str]]`: varje nivåpåstående i texten som par av nivånyckel och nivå, till exempel `("kvarstaende_risk", "hög")`.
  - `validera_utkast(utkast: AvsnittsUtkast, underlag: Avsnittsunderlag, personnamn: tuple[str, ...]) -> list[str]`. Tom lista betyder godkänt.
  - `motivering_har_hot_och_sarbarhet(stycke: Textstycke) -> bool` (används också av granskningen, B-12).
  - Fixtur `giltigt_utkast`: ett AI-utkast för `D-ARB.6.1` som klarar valideringen mot `real_underlag`.

Valideringen (spec 8.4) kontrollerar varje stycke: att det har referenser, att alla referenser finns i underlaget, att varje tal finns i underlaget, att varje uttryckt nivå stämmer med motorns nivå **för samma risktyp**, att stycken som bygger på obekräftade uppgifter har `[VERIFIERA]`, att inga förbjudna formuleringar eller personnamn förekommer. Dessutom ska det finnas minst en motivering, varje motivering ska hänvisa till ett hot och en sårbarhet eller uppgift, och någon motivering ska ange den inneboende risknivån. Felmeddelandena skickas tillbaka till AI vid nästa försök. De får därför aldrig innehålla personnamn.

Ett nivåpåstående är ett subjekt, ett verb och en nivå: "Risken är hög", "Den kvarstående risken bedöms som måttlig", "Sannolikheten för finansiering av terrorism är låg", "Konsekvensen är betydande". Subjektet avgör nyckeln:

| Subjekt | Nyckel |
|---|---|
| risk, risken, risknivån (även "inneboende risken" och "risken för penningtvätt") | `inneboende_risk` |
| kvarstående risk(en) | `kvarstaende_risk` |
| risken för terrorfinansiering, risken för finansiering av terrorism, terrorfinansieringsrisken | `terrorfinansiering_risk` |
| sannolikhet(en), med eller utan "för penningtvätt" | `inneboende_sannolikhet` |
| sannolikheten för terrorfinansiering eller finansiering av terrorism | `terrorfinansiering_sannolikhet` |
| konsekvens(en), med eller utan "för penningtvätt" | `inneboende_konsekvens` |
| konsekvensen för terrorfinansiering eller finansiering av terrorism | `terrorfinansiering_konsekvens` |

Mellan subjektet och verbet får det stå högst tre ord, till exempel "Risken i tjänsten är hög". Verben är "är", "blir", "bedöms som" och "bedöms vara". En nivå som inte hör till nyckeln, eller en nyckel som underlaget saknar (till exempel kvarstående risk för terrorfinansiering), ger ett fel. Formuleringar utanför mönstret upptäcks inte av den här kontrollen. Därför instruerar underlaget AI att skriva nivåerna i just den här formen, och sakgranskningen läser texten.

- [ ] **Step 1: Lägg till fixturen sist i `tester/conftest.py`**

```python
@pytest.fixture
def giltigt_utkast():
    """Ett AI-utkast för löpande bokföring som klarar valideringen mot real_underlag."""
    from riskanalys.dokument.modeller import AvsnittsUtkast

    return AvsnittsUtkast.model_validate(
        {
            "avsnitt": "D-ARB.6.1",
            "stycken": [
                {
                    "typ": "analys",
                    "text": (
                        "Löpande bokföring hanterar kundernas verifikationer och ligger närmast deras transaktioner. "
                        "Osanna fakturor och brottsvinster som redovisas som intäkter kan därför passera genom "
                        "byråns bokföring."
                    ),
                    "referenser": ["T-RED-01", "H-01", "H-02"],
                },
                {
                    "typ": "motivering",
                    "text": (
                        "Sannolikheten bedöms som hög eftersom 30 % av kunderna finns i riskbranscher och 80 % av "
                        "underlaget kommer in digitalt medan bankdata bara finns för 40 % av kunderna. "
                        "Konsekvensen är betydande. Risken är hög."
                    ),
                    "referenser": [
                        "H-01",
                        "S-KUND-01",
                        "S-KANAL-01",
                        "P-KUND.andel_riskbransch",
                        "P-KANAL.andel_digitalt_underlag",
                        "P-KANAL.bankdata_andel",
                        "BT-MATRIS-08",
                    ],
                },
                {
                    "typ": "analys",
                    "text": (
                        "Risken för finansiering av terrorism bedöms som måttlig. Bankavstämningen mot underlag finns "
                        "i rutinerna men är inte belagd, så den kvarstående risken är hög."
                    ),
                    "referenser": ["BT-MATRIS-03", "C-07", "BT-KVAR-01"],
                },
                {
                    "typ": "scenario",
                    "text": (
                        "En byggkund laddar upp leverantörsfakturor via en app och byrån saknar bankdata för kunden. "
                        "Ett upplägg med osanna fakturor kan då pågå utan att avvikelser syns i avstämningen."
                    ),
                    "referenser": ["H-01", "S-KUND-01", "S-KANAL-01"],
                },
            ],
            "oklarheter": [],
        }
    )
```

- [ ] **Step 2: Skriv det felande testet `tester/enhet/test_validering_utkast.py`**

```python
import pytest

from riskanalys.dokument.validering import VERIFIERA, nivapastaenden, validera_utkast

PERSONER = ("Testa Testsson",)


def _andra(utkast, index, **andringar):
    stycken = list(utkast.stycken)
    stycken[index] = stycken[index].model_copy(update=andringar)
    return utkast.model_copy(update={"stycken": stycken})


def _ersatt(utkast, index, gammal, ny):
    text = utkast.stycken[index].text
    assert gammal in text
    return _andra(utkast, index, text=text.replace(gammal, ny))


def test_giltigt_utkast_godkanns(giltigt_utkast, real_underlag):
    assert validera_utkast(giltigt_utkast, real_underlag, PERSONER) == []


def test_fel_avsnitt(giltigt_utkast, real_underlag):
    fel = validera_utkast(giltigt_utkast.model_copy(update={"avsnitt": "D-ARB.6.2"}), real_underlag, PERSONER)
    assert "Utkastet gäller avsnitt D-ARB.6.2, men underlaget gäller D-ARB.6.1." in fel


def test_tomt_utkast(giltigt_utkast, real_underlag):
    fel = validera_utkast(giltigt_utkast.model_copy(update={"stycken": []}), real_underlag, PERSONER)
    assert "Utkastet har inga stycken." in fel
    assert "Utkastet saknar ett stycke av typen motivering." in fel


def test_okand_referens(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 0, referenser=["T-RED-01", "H-99"])
    assert "Stycke 1 hänvisar till H-99, som inte finns i underlaget." in validera_utkast(utkast, real_underlag, PERSONER)


def test_stycke_utan_referenser(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 0, referenser=[])
    assert "Stycke 1 saknar referenser." in validera_utkast(utkast, real_underlag, PERSONER)


def test_pahittat_tal(giltigt_utkast, real_underlag):
    utkast = _ersatt(giltigt_utkast, 1, "30 %", "45 %")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert "Stycke 2 innehåller talet 45, som inte finns i underlaget." in fel


@pytest.mark.parametrize(
    ("text", "vantat"),
    [
        ("Risken är hög.", [("inneboende_risk", "hög")]),
        ("Risknivån bedöms som mycket hög.", [("inneboende_risk", "mycket hög")]),
        ("Den inneboende risken i tjänsten är måttlig.", [("inneboende_risk", "måttlig")]),
        ("Risken för penningtvätt blir låg.", [("inneboende_risk", "låg")]),
        ("Den kvarstående risken är hög.", [("kvarstaende_risk", "hög")]),
        ("Risken bedöms därför som låg.", [("inneboende_risk", "låg")]),
        ("Risken för finansiering av terrorism bedöms som måttlig.", [("terrorfinansiering_risk", "måttlig")]),
        ("Terrorfinansieringsrisken är låg.", [("terrorfinansiering_risk", "låg")]),
        ("Sannolikheten bedöms vara hög.", [("inneboende_sannolikhet", "hög")]),
        ("Sannolikheten för terrorfinansiering är låg.", [("terrorfinansiering_sannolikhet", "låg")]),
        ("Konsekvensen är betydande.", [("inneboende_konsekvens", "betydande")]),
        ("Konsekvensen för finansiering av terrorism är allvarlig.", [("terrorfinansiering_konsekvens", "allvarlig")]),
        (
            "Den kvarstående risken för terrorfinansiering är låg.",
            [("kvarstaende_terrorfinansiering_risk", "låg")],
        ),
        (
            "Konsekvensen är betydande. Risken är hög, och den kvarstående risken är måttlig.",
            [("inneboende_konsekvens", "betydande"), ("inneboende_risk", "hög"), ("kvarstaende_risk", "måttlig")],
        ),
        ("En hög andel av kunderna betalar kontant.", []),
    ],
)
def test_nivapastaenden_binds_till_risktyp(text, vantat):
    assert nivapastaenden(text) == vantat


def test_inneboende_riskniva_som_inte_kommer_fran_motorn(giltigt_utkast, real_underlag):
    utkast = _ersatt(giltigt_utkast, 1, "Risken är hög.", "Risken är låg.")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert "Stycke 2 anger att den inneboende risken är låg, men riskmotorn anger hög." in fel
    assert any(rad.startswith("Ingen motivering anger den inneboende risknivån (hög)") for rad in fel)


def test_tva_giltiga_nivaer_som_bytt_plats_upptacks(giltigt_utkast, real_underlag):
    utkast = _ersatt(giltigt_utkast, 2, "bedöms som måttlig", "bedöms som hög")
    utkast = _ersatt(utkast, 2, "kvarstående risken är hög", "kvarstående risken är måttlig")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert "Stycke 3 anger att risken för terrorfinansiering är hög, men riskmotorn anger måttlig." in fel
    assert "Stycke 3 anger att den kvarstående risken är måttlig, men riskmotorn anger hög." in fel


def test_kvarstaende_niva_som_bara_galler_terrorfinansiering_upptacks(giltigt_utkast, real_underlag):
    utkast = _ersatt(giltigt_utkast, 2, "kvarstående risken är hög", "kvarstående risken är måttlig")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert fel == ["Stycke 3 anger att den kvarstående risken är måttlig, men riskmotorn anger hög."]


def test_fel_sannolikhet_och_konsekvens_upptacks(giltigt_utkast, real_underlag):
    utkast = _ersatt(giltigt_utkast, 1, "Sannolikheten bedöms som hög", "Sannolikheten bedöms som medel")
    utkast = _ersatt(utkast, 1, "Konsekvensen är betydande", "Konsekvensen är allvarlig")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert "Stycke 2 anger att sannolikheten är medel, men riskmotorn anger hög." in fel
    assert "Stycke 2 anger att konsekvensen är allvarlig, men riskmotorn anger betydande." in fel


def test_niva_for_risktyp_som_motorn_inte_bedomer(giltigt_utkast, real_underlag):
    text = giltigt_utkast.stycken[2].text + " Den kvarstående risken för terrorfinansiering är låg."
    fel = validera_utkast(_andra(giltigt_utkast, 2, text=text), real_underlag, PERSONER)
    assert (
        "Stycke 3 anger en nivå för den kvarstående risken för terrorfinansiering, men underlaget har ingen sådan nivå."
        in fel
    )


def test_obekraftad_uppgift_kraver_verifiera(giltigt_utkast, underlag_fabrik, regelbas, profil_fabrik, real_varden):
    underlag = underlag_fabrik(profil_fabrik(regelbas, real_varden, okanda=("P-KUND.andel_riskbransch",)))
    meddelande = f"Stycke 2 bygger på obekräftade uppgifter (P-KUND.andel_riskbransch) men saknar {VERIFIERA}."
    assert meddelande in validera_utkast(giltigt_utkast, underlag, PERSONER)
    markerat = _andra(giltigt_utkast, 1, text=giltigt_utkast.stycken[1].text + f" {VERIFIERA}")
    assert meddelande not in validera_utkast(markerat, underlag, PERSONER)


def test_forbjuden_formulering(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 0, text=giltigt_utkast.stycken[0].text + " Det finns inga risker i övrigt.")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert 'Stycke 1 innehåller den förbjudna formuleringen "det finns inga risker".' in fel


def test_personnamn_stoppas_utan_att_namnet_upprepas(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 0, text=giltigt_utkast.stycken[0].text + " Testa Testsson ansvarar.")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert "Stycke 1 innehåller ett personnamn. Skriv {roll:FfR} i stället." in fel
    assert not any("Testa Testsson" in rad for rad in fel)


def test_motivering_utan_hot(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 1, referenser=["S-KUND-01", "BT-MATRIS-08"])
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert (
        "Motiveringen i stycke 2 måste hänvisa till minst ett hot (H-) och en sårbarhet (S-) eller uppgift (P-)." in fel
    )
```

- [ ] **Step 3: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/enhet/test_validering_utkast.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.dokument.validering'`.

- [ ] **Step 4: Skriv `src/riskanalys/dokument/validering.py`**

```python
"""Maskinell validering av AI-utkast (spec 8.4). Ett utkast som inte klarar valideringen används aldrig."""

import re

from riskanalys.dokument.modeller import Avsnittsunderlag, AvsnittsUtkast, Textstycke

VERIFIERA = "[VERIFIERA]"
FORBJUDNA_FORMULERINGAR = (
    "enligt gällande lagstiftning",
    "i enlighet med branschpraxis",
    "som alla redovisningsbyråer",
    "det finns inga risker",
    "risken är generellt låg",
)
BENAMNINGAR = {
    "inneboende_sannolikhet": "sannolikheten",
    "inneboende_konsekvens": "konsekvensen",
    "inneboende_risk": "den inneboende risken",
    "terrorfinansiering_sannolikhet": "sannolikheten för terrorfinansiering",
    "terrorfinansiering_konsekvens": "konsekvensen för terrorfinansiering",
    "terrorfinansiering_risk": "risken för terrorfinansiering",
    "kvarstaende_risk": "den kvarstående risken",
    "kvarstaende_terrorfinansiering_risk": "den kvarstående risken för terrorfinansiering",
}
_TAL = re.compile(r"\d+(?:[.,]\d+)?")
_VERB = r"\s+(?:är|blir|bedöms(?:\s+\w+)?\s+(?:som|vara))\s+"
_AMNE = r"(?:\s+för\s+(?P<amne>finansiering\s+av\s+terrorism|terrorfinansiering|penningtvätt))?"
_FYLLNAD = r"(?:\s+\w+){0,3}?"
_TF = r"(?P<tf>terrorfinansierings)?"
_PASTAENDEN = (
    (
        "risk",
        re.compile(
            r"\b(?P<led>kvarstående\s+|inneboende\s+)?" + _TF + r"risk(?:en|nivån)?" + _AMNE + _FYLLNAD + _VERB
            + r"(?P<niva>mycket\s+hög|låg|måttlig|hög)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "sannolikhet",
        re.compile(
            r"\b" + _TF + r"sannolikhet(?:en)?" + _AMNE + _FYLLNAD + _VERB + r"(?P<niva>medelhög|medel|låg|hög)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "konsekvens",
        re.compile(
            r"\b" + _TF + r"konsekvens(?:en)?" + _AMNE + _FYLLNAD + _VERB + r"(?P<niva>begränsad|betydande|allvarlig)\b",
            re.IGNORECASE,
        ),
    ),
)


def validera_utkast(utkast: AvsnittsUtkast, underlag: Avsnittsunderlag, personnamn: tuple[str, ...]) -> list[str]:
    """Returnerar alla fel i utkastet. Meddelandena skickas tillbaka till AI och innehåller aldrig personnamn."""
    tillatna_tal = _tal_i(underlag.model_dump_json())
    stycken = [
        fel
        for nummer, stycke in enumerate(utkast.stycken, start=1)
        for fel in _stycke(nummer, stycke, underlag, tillatna_tal, personnamn)
    ]
    return [*_helhet(utkast, underlag), *stycken, *_motiveringar(utkast, underlag)]


def motivering_har_hot_och_sarbarhet(stycke: Textstycke) -> bool:
    har_hot = any(ref.startswith("H-") for ref in stycke.referenser)
    har_grund = any(ref.startswith(("S-", "P-")) for ref in stycke.referenser)
    return har_hot and har_grund


def nivapastaenden(text: str) -> list[tuple[str, str]]:
    """Nivåpåståenden i texten som (nivånyckel, nivå), i den ordning de står."""
    traffar = [
        (traff.start(), _nyckel(storhet, traff), " ".join(traff["niva"].lower().split()))
        for storhet, monster in _PASTAENDEN
        for traff in monster.finditer(text)
    ]
    return [(nyckel, niva) for _, nyckel, niva in sorted(traffar)]


def _nyckel(storhet: str, traff: re.Match[str]) -> str:
    grupper = traff.groupdict()
    ar_tf = bool(grupper.get("tf")) or "terror" in (grupper.get("amne") or "").lower()
    if storhet != "risk":
        return f"{'terrorfinansiering' if ar_tf else 'inneboende'}_{storhet}"
    if (grupper.get("led") or "").strip().lower() == "kvarstående":
        return "kvarstaende_terrorfinansiering_risk" if ar_tf else "kvarstaende_risk"
    return "terrorfinansiering_risk" if ar_tf else "inneboende_risk"


def _helhet(utkast: AvsnittsUtkast, underlag: Avsnittsunderlag) -> list[str]:
    fel = []
    if utkast.avsnitt != underlag.avsnitt:
        fel.append(f"Utkastet gäller avsnitt {utkast.avsnitt}, men underlaget gäller {underlag.avsnitt}.")
    if not utkast.stycken:
        fel.append("Utkastet har inga stycken.")
    return fel


def _nivafel(nummer: int, text: str, nivaer: dict[str, str]) -> list[str]:
    fel = []
    for nyckel, niva in nivapastaenden(text):
        benamning = BENAMNINGAR[nyckel]
        vantat = nivaer.get(nyckel)
        if vantat is None:
            fel.append(f"Stycke {nummer} anger en nivå för {benamning}, men underlaget har ingen sådan nivå.")
        elif niva != vantat.lower():
            fel.append(f"Stycke {nummer} anger att {benamning} är {niva}, men riskmotorn anger {vantat}.")
    return fel


def _stycke(
    nummer: int,
    stycke: Textstycke,
    underlag: Avsnittsunderlag,
    tillatna_tal: set[str],
    personnamn: tuple[str, ...],
) -> list[str]:
    tillatna_id = underlag.tillatna_id()
    obekraftade = {uppgift.id for uppgift in underlag.uppgifter if not uppgift.bekraftad}
    liten = stycke.text.lower()
    fel = [] if stycke.referenser else [f"Stycke {nummer} saknar referenser."]
    fel += [
        f"Stycke {nummer} hänvisar till {ref}, som inte finns i underlaget."
        for ref in stycke.referenser
        if ref not in tillatna_id
    ]
    fel += [
        f"Stycke {nummer} innehåller talet {tal}, som inte finns i underlaget."
        for tal in sorted(_tal_i(stycke.text) - tillatna_tal)
    ]
    fel += _nivafel(nummer, stycke.text, underlag.nivaer)
    beroenden = sorted(set(stycke.referenser) & obekraftade)
    if beroenden and VERIFIERA not in stycke.text:
        fel.append(f"Stycke {nummer} bygger på obekräftade uppgifter ({', '.join(beroenden)}) men saknar {VERIFIERA}.")
    fel += [
        f'Stycke {nummer} innehåller den förbjudna formuleringen "{formulering}".'
        for formulering in FORBJUDNA_FORMULERINGAR
        if formulering in liten
    ]
    if any(namn.lower() in liten for namn in personnamn):
        fel.append(f"Stycke {nummer} innehåller ett personnamn. Skriv {{roll:FfR}} i stället.")
    return fel


def _motiveringar(utkast: AvsnittsUtkast, underlag: Avsnittsunderlag) -> list[str]:
    motiveringar = [(nummer, stycke) for nummer, stycke in enumerate(utkast.stycken, start=1) if stycke.typ == "motivering"]
    if not motiveringar:
        return ["Utkastet saknar ett stycke av typen motivering."]
    fel = [
        f"Motiveringen i stycke {nummer} måste hänvisa till minst ett hot (H-) och en sårbarhet (S-) eller uppgift (P-)."
        for nummer, stycke in motiveringar
        if not motivering_har_hot_och_sarbarhet(stycke)
    ]
    inneboende = underlag.nivaer.get("inneboende_risk", "").lower()
    if not any(("inneboende_risk", inneboende) in nivapastaenden(stycke.text) for _, stycke in motiveringar):
        fel.append(f'Ingen motivering anger den inneboende risknivån ({inneboende}), till exempel "Risken är {inneboende}."')
    return fel


def _tal_i(text: str) -> set[str]:
    return {_normalisera(tal) for tal in _TAL.findall(text)}


def _normalisera(tal: str) -> str:
    med_punkt = tal.replace(",", ".")
    return med_punkt.rstrip("0").rstrip(".") if "." in med_punkt else med_punkt
```

- [ ] **Step 5: Kör testet**

Run: `.venv/bin/pytest tester/enhet/test_validering_utkast.py -v`
Expected: alla tester passerar.

- [ ] **Step 6: Commit**

```bash
git add src/riskanalys/dokument/validering.py tester/conftest.py tester/enhet/test_validering_utkast.py
git commit -m "feat: maskinell validering av AI-utkast"
```

---

### Task 16: Skrivning med omförsök, Claude-leverantör och kommandot `skriv`

**Files:**
- Create: `src/riskanalys/dokument/skrivning.py`
- Create: `src/riskanalys/dokument/claude.py`
- Create: `src/riskanalys/kommandon/skriv_kommando.py`
- Modify: `src/riskanalys/cli.py`
- Modify: `tester/conftest.py` (fixturen `testsvarsfil`)
- Test: `tester/enhet/test_skrivning.py`, `tester/enhet/test_claude.py`, `tester/enhet/test_skriv_kommando.py`, `tester/live/test_claude_live.py`

**Interfaces:**
- Consumes: `Textleverantor`, `Testleverantor`, `Leveranssvar`, `Anropsdata`, `Tokenanvandning`, `ladda_testleverantor`, `LeverantorFel`, `validera_utkast`, `bygg_underlag`, `tjanster_med_avsnitt`, `personnamn`, `senaste_korning`, `ny_korningsmapp`, `skriv_manifest`, `BEDOMNINGAR`, `las_bedomning`, `las_bedomningsprofil`, `kontrollera_aktuell`, `for_text`.
- Produces:
  - `dokument/skrivning.py`: `MAX_FORSOK = 3`, `UTKAST = "utkast"`, `UNDERLAGSFIL = "underlag.json"`, `Forsok(nummer: int, anrop: Anropsdata, text: str, svar: AvsnittsUtkast | None, fel: tuple[str, ...])`, `Skrivresultat(underlag, leverantor: str, modell: str, forsok: tuple[Forsok, ...])` med egenskapen `godkant_utkast -> AvsnittsUtkast | None`, `skriv_avsnitt(leverantor, underlag, personnamn, spara: Callable[[Forsok], None] = ..., max_forsok=MAX_FORSOK) -> Skrivresultat`, `kor_skrivning(byramapp: Path, regelbas: Regelbas, leverantor: Textleverantor) -> Path`, `las_skrivresultat(mapp: Path) -> list[Skrivresultat]`.
  - `dokument/claude.py`: `STANDARDMODELL = "claude-opus-5-5"`, `STANDARDEFFORT = "high"`, `MAX_TOKENS = 16000`, `FALLBACK_BETA = "server-side-fallback-2026-07-01"`, `SYSTEMPROMPT`, `SCHEMA`, `PROMPT_KONTROLLSUMMA`, `bygg_meddelande(underlag, aterkoppling) -> str`, `ClaudeLeverantor(modell=STANDARDMODELL, effort=STANDARDEFFORT, klient=None)` med `namn = "claude"`.
  - Kommandot `skriv <byra> [--leverantor claude|test] [--testsvar FIL] [--modell M] [--effort E]`. Returnerar 0 om alla avsnitt godkändes och 2 om något underkändes.
  - Manifestets metadata för utkast: `typ = "utkast"`, `leverantor`, `modell` (begärd modell), `bedomning` (namnet på bedömningsmappen). Faktisk svarsmodell per försök står i försöksfilerna.
  - Fixtur `testsvarsfil`: en JSON-fil med `[giltigt_utkast]`.

Ett AI-utkast som underkänns skickas tillbaka med felmeddelandena som återkoppling, högst tre försök (spec 8.4). Ett svar som inte följer schemat räknas som ett underkänt försök. Stoppar leverantören svaret (modellen avböjde eller svaret blev för långt) avbryts skrivningen.

**Varje försök sparas så fort svaret kommit**, innan det tolkas och innan nästa anrop görs. Körningsmappen skapas före första anropet med en undermapp per avsnitt:

```
utkast/<tid>/
  D-ARB.6.1/underlag.json      det som skickades till AI
  D-ARB.6.1/forsok-1.json      råsvar, tolkat utkast, valideringsfel och anropsdata
  D-ARB.6.1/forsok-2.json
  D-ARB.6.1.json               sammanställt Skrivresultat (skrivs när avsnittet är klart)
  manifest.json                skrivs sist, när alla avsnitt är klara
```

Avbryts körningen finns försöken kvar, men mappen saknar manifest och räknas därför inte som en avslutad körning (Task 13). Felmeddelandet säger var försöken ligger.

Claude-leverantören anropar `client.beta.messages.create` med strukturerat svar enligt AI-schemat, `betas=[FALLBACK_BETA]` och `fallbacks="default"` (SDK 1.12 typar värdet `"default"`). Adaptiv tänkning är standard för modellen och sätts därför inte. Effort sätts alltid, eftersom modellens standard är `medium`. Svaret kan innehålla tänkandeblock och, vid fallback, ett block av typen `fallback` före textblocket, så leverantören läser första textblocket. Anropsdatan tas ur svaret: `model` är modellen som faktiskt skrev svaret, `id` är svarets ID och `usage.iterations` har en post per försök hos API:t, där en post av typen `fallback_message` betyder att en reservmodell svarade. `PROMPT_KONTROLLSUMMA` är en kontrollsumma av systemprompten och schemat, så att det går att se om två försök fick samma instruktioner.

- [ ] **Step 1: Lägg till fixturen sist i `tester/conftest.py`**

```python
@pytest.fixture
def testsvarsfil(tmp_path, giltigt_utkast):
    """En fil med förberedda svar för --leverantor test."""
    fil = tmp_path / "testsvar.json"
    fil.write_text("[" + giltigt_utkast.model_dump_json() + "]", encoding="utf-8")
    return fil
```

- [ ] **Step 2: Skriv det felande testet `tester/enhet/test_skrivning.py`**

```python
import pytest

from riskanalys.dokument.leverantor import LeverantorFel, Testleverantor
from riskanalys.dokument.skrivning import las_skrivresultat, skriv_avsnitt
from riskanalys.lagring.manifest import skriv_manifest

AVBROTT = "Claude avböjde att skriva avsnittet."


def _felaktigt(utkast):
    return utkast.model_copy(update={"avsnitt": "D-ARB.6.2"})


class AvbrytandeLeverantor:
    """Svarar som när modellen avböjer: ett tomt svar med avbrott."""

    namn = "test"
    modell = "testleverantor"

    def skriv(self, underlag, aterkoppling):
        return Testleverantor([""]).skriv(underlag, aterkoppling).model_copy(update={"avbrott": AVBROTT})


def test_godkant_pa_forsta_forsoket(giltigt_utkast, real_underlag):
    resultat = skriv_avsnitt(Testleverantor([giltigt_utkast]), real_underlag, ("Testa Testsson",))
    assert len(resultat.forsok) == 1
    assert resultat.godkant_utkast == giltigt_utkast
    assert (resultat.leverantor, resultat.modell) == ("test", "testleverantor")
    assert (resultat.forsok[0].nummer, resultat.forsok[0].anrop.svar_id) == (1, "test-1")


def test_aterkoppling_skickas_vid_nytt_forsok(giltigt_utkast, real_underlag):
    leverantor = Testleverantor([_felaktigt(giltigt_utkast), giltigt_utkast])
    resultat = skriv_avsnitt(leverantor, real_underlag, ())
    assert len(resultat.forsok) == 2
    assert leverantor.anrop[0][1] == []
    assert leverantor.anrop[1][1] == list(resultat.forsok[0].fel)
    assert resultat.godkant_utkast == giltigt_utkast


def test_underkant_efter_tre_forsok(giltigt_utkast, real_underlag):
    leverantor = Testleverantor([_felaktigt(giltigt_utkast)] * 3)
    resultat = skriv_avsnitt(leverantor, real_underlag, ())
    assert len(resultat.forsok) == 3
    assert resultat.godkant_utkast is None


def test_svar_som_inte_foljer_schemat_ar_ett_underkant_forsok(giltigt_utkast, real_underlag):
    leverantor = Testleverantor(['{"avsnitt": "D-ARB.6.1"}', giltigt_utkast])
    resultat = skriv_avsnitt(leverantor, real_underlag, ())
    forsta = resultat.forsok[0]
    assert (forsta.svar, forsta.text) == (None, '{"avsnitt": "D-ARB.6.1"}')
    assert forsta.fel[0].startswith("Svaret följde inte schemat")
    assert resultat.godkant_utkast == giltigt_utkast


def test_varje_forsok_sparas_innan_nasta_anrop(giltigt_utkast, real_underlag):
    sparade = []
    with pytest.raises(LeverantorFel, match="1 förberedda svar"):
        skriv_avsnitt(Testleverantor([_felaktigt(giltigt_utkast)]), real_underlag, (), spara=sparade.append)
    assert [forsok.nummer for forsok in sparade] == [1]
    assert sparade[0].fel


def test_avbrott_sparas_och_stoppar_skrivningen(real_underlag):
    sparade = []
    with pytest.raises(LeverantorFel, match="avböjde"):
        skriv_avsnitt(AvbrytandeLeverantor(), real_underlag, (), spara=sparade.append)
    assert [(forsok.nummer, forsok.fel) for forsok in sparade] == [(1, (AVBROTT,))]


def test_skrivresultat_sparas_och_lases(tmp_path, giltigt_utkast, real_underlag):
    resultat = skriv_avsnitt(Testleverantor([giltigt_utkast]), real_underlag, ())
    (tmp_path / "D-ARB.6.1.json").write_text(resultat.model_dump_json(), encoding="utf-8")
    skriv_manifest(tmp_path, {})
    assert las_skrivresultat(tmp_path) == [resultat]
```

- [ ] **Step 3: Skriv det felande testet `tester/enhet/test_claude.py`**

```python
from types import SimpleNamespace

import anthropic
import httpx2
import pytest

from riskanalys.dokument.claude import (
    FALLBACK_BETA,
    MAX_TOKENS,
    PROMPT_KONTROLLSUMMA,
    SCHEMA,
    STANDARDEFFORT,
    STANDARDMODELL,
    ClaudeLeverantor,
)
from riskanalys.dokument.leverantor import LeverantorFel
from riskanalys.dokument.modeller import AvsnittsUtkast

API_URL = "https://api.anthropic.com/v1/messages"


class FalskKlient:
    """Ersätter anthropic.Anthropic i tester. Sparar anropen och returnerar ett förberett svar."""

    def __init__(self, svar=None, undantag=None):
        self.anrop = []
        self._svar = svar
        self._undantag = undantag
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._skapa))

    def _skapa(self, **kwargs):
        self.anrop.append(kwargs)
        if self._undantag is not None:
            raise self._undantag
        return self._svar


def _svar(text, stop_reason="end_turn", modell=STANDARDMODELL, iterationer=None):
    return SimpleNamespace(
        id="msg_test_1",
        model=modell,
        stop_reason=stop_reason,
        content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=text)],
        usage=SimpleNamespace(input_tokens=1200, output_tokens=800, iterations=iterationer),
    )


def test_anropet_foljer_installningarna(giltigt_utkast, real_underlag):
    klient = FalskKlient(_svar(giltigt_utkast.model_dump_json()))
    svar = ClaudeLeverantor(klient=klient).skriv(real_underlag, [])
    assert AvsnittsUtkast.model_validate_json(svar.text) == giltigt_utkast
    (anrop,) = klient.anrop
    assert anrop["model"] == STANDARDMODELL == "claude-opus-5-5"
    assert anrop["max_tokens"] == MAX_TOKENS
    assert anrop["output_config"] == {
        "effort": STANDARDEFFORT,
        "format": {"type": "json_schema", "schema": AvsnittsUtkast.model_json_schema()},
    }
    assert anrop["betas"] == [FALLBACK_BETA]
    assert anrop["fallbacks"] == "default"
    meddelande = anrop["messages"][0]["content"]
    assert real_underlag.model_dump_json(indent=2) in meddelande
    assert "Testa Testsson" not in meddelande


def test_anropsdata_sparas(giltigt_utkast, real_underlag):
    anrop = ClaudeLeverantor(klient=FalskKlient(_svar(giltigt_utkast.model_dump_json()))).skriv(real_underlag, []).anrop
    assert (anrop.leverantor, anrop.begard_modell, anrop.svarsmodell, anrop.effort) == (
        "claude",
        "claude-opus-5-5",
        "claude-opus-5-5",
        "high",
    )
    assert (anrop.svar_id, anrop.stop_reason, anrop.reservmodell_svarade) == ("msg_test_1", "end_turn", False)
    assert anrop.prompt_kontrollsumma == PROMPT_KONTROLLSUMMA
    assert [(post.typ, post.indata_token, post.utdata_token) for post in anrop.anvandning] == [("message", 1200, 800)]


def test_faktisk_svarsmodell_sparas_vid_fallback(giltigt_utkast, real_underlag):
    iterationer = [
        SimpleNamespace(type="message", input_tokens=1200, output_tokens=0),
        SimpleNamespace(type="fallback_message", model="claude-opus-4-8", input_tokens=1200, output_tokens=900),
    ]
    svar = _svar(giltigt_utkast.model_dump_json(), modell="claude-opus-4-8", iterationer=iterationer)
    anrop = ClaudeLeverantor(klient=FalskKlient(svar)).skriv(real_underlag, []).anrop
    assert (anrop.begard_modell, anrop.svarsmodell, anrop.reservmodell_svarade) == (
        "claude-opus-5-5",
        "claude-opus-4-8",
        True,
    )
    assert [(post.typ, post.modell, post.utdata_token) for post in anrop.anvandning] == [
        ("message", None, 0),
        ("fallback_message", "claude-opus-4-8", 900),
    ]


def test_promptens_kontrollsumma_bygger_pa_systemprompt_och_schema():
    assert PROMPT_KONTROLLSUMMA.startswith("sha256:")
    assert SCHEMA == AvsnittsUtkast.model_json_schema()


def test_aterkopplingen_skickas_med(giltigt_utkast, real_underlag):
    klient = FalskKlient(_svar(giltigt_utkast.model_dump_json()))
    ClaudeLeverantor(klient=klient).skriv(real_underlag, ["Stycke 2 innehåller talet 45."])
    assert "- Stycke 2 innehåller talet 45." in klient.anrop[0]["messages"][0]["content"]


@pytest.mark.parametrize(("stop_reason", "meddelande"), [("refusal", "avböjde"), ("max_tokens", "för långt")])
def test_avbrutna_svar_returneras_med_avbrott_och_anropsdata(real_underlag, stop_reason, meddelande):
    svar = ClaudeLeverantor(klient=FalskKlient(_svar("", stop_reason))).skriv(real_underlag, [])
    assert meddelande in svar.avbrott
    assert (svar.anrop.stop_reason, svar.anrop.svar_id) == (stop_reason, "msg_test_1")


def test_api_fel_blir_leverantorsfel(real_underlag):
    begaran = httpx2.Request("POST", API_URL)
    fel = anthropic.RateLimitError("För många anrop.", response=httpx2.Response(429, request=begaran), body=None)
    with pytest.raises(LeverantorFel, match="429"):
        ClaudeLeverantor(klient=FalskKlient(undantag=fel)).skriv(real_underlag, [])


def test_natverksfel_blir_leverantorsfel(real_underlag):
    fel = anthropic.APIConnectionError(request=httpx2.Request("POST", API_URL))
    with pytest.raises(LeverantorFel, match="nätverket"):
        ClaudeLeverantor(klient=FalskKlient(undantag=fel)).skriv(real_underlag, [])
```

- [ ] **Step 4: Kör testerna för att se att de fallerar**

Run: `.venv/bin/pytest tester/enhet/test_skrivning.py tester/enhet/test_claude.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.dokument.skrivning'` respektive `'riskanalys.dokument.claude'`.

- [ ] **Step 5: Skriv `src/riskanalys/dokument/skrivning.py`**

```python
"""Skrivning av AI-avsnitt med validering och omförsök (spec 8.4). Varje försök sparas direkt."""

from collections.abc import Callable
from functools import partial
from pathlib import Path

from pydantic import BaseModel, ConfigDict, ValidationError

from riskanalys.bedomning.korning import BEDOMNINGAR, kontrollera_aktuell, las_bedomning, las_bedomningsprofil
from riskanalys.dokument.leverantor import Anropsdata, Leveranssvar, LeverantorFel, Textleverantor
from riskanalys.dokument.modeller import Avsnittsunderlag, AvsnittsUtkast
from riskanalys.dokument.underlag import bygg_underlag, tjanster_med_avsnitt
from riskanalys.dokument.validering import validera_utkast
from riskanalys.lagring.korningar import ny_korningsmapp, senaste_korning
from riskanalys.lagring.manifest import MANIFESTNAMN, skriv_manifest
from riskanalys.profil.hantering import personnamn
from riskanalys.regelverk.modeller import Regelbas

MAX_FORSOK = 3
UTKAST = "utkast"
UNDERLAGSFIL = "underlag.json"


class Forsok(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    nummer: int
    anrop: Anropsdata
    text: str
    svar: AvsnittsUtkast | None
    fel: tuple[str, ...]


class Skrivresultat(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    underlag: Avsnittsunderlag
    leverantor: str
    modell: str
    forsok: tuple[Forsok, ...]

    @property
    def godkant_utkast(self) -> AvsnittsUtkast | None:
        """Det sista försöket, om det klarade valideringen."""
        if not self.forsok or self.forsok[-1].fel:
            return None
        return self.forsok[-1].svar


def _spara_inte(forsok: Forsok) -> None:
    """Standard för skriv_avsnitt när anroparen inte vill spara försöken."""


def skriv_avsnitt(
    leverantor: Textleverantor,
    underlag: Avsnittsunderlag,
    personnamn: tuple[str, ...],
    spara: Callable[[Forsok], None] = _spara_inte,
    max_forsok: int = MAX_FORSOK,
) -> Skrivresultat:
    """Skriver ett avsnitt med omförsök. Varje försök lämnas till spara innan nästa anrop görs."""
    forsok: tuple[Forsok, ...] = ()
    aterkoppling: list[str] = []
    for nummer in range(1, max_forsok + 1):
        leverans = leverantor.skriv(underlag, aterkoppling)
        svar, fel = _bedom_leverans(leverans, underlag, personnamn)
        post = Forsok(nummer=nummer, anrop=leverans.anrop, text=leverans.text, svar=svar, fel=fel)
        spara(post)
        forsok = (*forsok, post)
        if leverans.avbrott is not None:
            raise LeverantorFel(f"Avsnitt {underlag.avsnitt}: {leverans.avbrott}")
        if not fel:
            break
        aterkoppling = list(fel)
    return Skrivresultat(underlag=underlag, leverantor=leverantor.namn, modell=leverantor.modell, forsok=forsok)


def _bedom_leverans(
    leverans: Leveranssvar, underlag: Avsnittsunderlag, personnamn: tuple[str, ...]
) -> tuple[AvsnittsUtkast | None, tuple[str, ...]]:
    if leverans.avbrott is not None:
        return None, (leverans.avbrott,)
    try:
        svar = AvsnittsUtkast.model_validate_json(leverans.text)
    except ValidationError as fel:
        return None, (
            f"Svaret följde inte schemat för AI-utkast ({fel.error_count()} fel). Svara bara med JSON enligt schemat.",
        )
    return svar, tuple(validera_utkast(svar, underlag, personnamn))


def kor_skrivning(byramapp: Path, regelbas: Regelbas, leverantor: Textleverantor) -> Path:
    """Skriver ett riskavsnitt per bedömd tjänst utifrån den senaste bedömningen."""
    bedomningsmapp = senaste_korning(byramapp, BEDOMNINGAR, f"bedom {byramapp.name}")
    kontrollera_aktuell(byramapp, bedomningsmapp, regelbas)
    bedomning = las_bedomning(bedomningsmapp)
    profil = las_bedomningsprofil(bedomningsmapp)
    namn = personnamn(profil, regelbas)
    mapp = ny_korningsmapp(byramapp, UTKAST)
    try:
        for avsnitt_id, tjanst in tjanster_med_avsnitt(bedomning):
            underlag = bygg_underlag(regelbas, profil, tjanst, avsnitt_id)
            avsnittsmapp = mapp / avsnitt_id
            avsnittsmapp.mkdir()
            (avsnittsmapp / UNDERLAGSFIL).write_text(underlag.model_dump_json(indent=2), encoding="utf-8")
            resultat = skriv_avsnitt(leverantor, underlag, namn, partial(_spara_forsok, avsnittsmapp))
            (mapp / f"{avsnitt_id}.json").write_text(resultat.model_dump_json(indent=2), encoding="utf-8")
    except LeverantorFel as fel:
        raise LeverantorFel(
            f"{fel} Försöken som hann göras är sparade i {mapp}. Körningen räknas inte, eftersom den avbröts."
        ) from fel
    metadata = {
        "typ": "utkast",
        "leverantor": leverantor.namn,
        "modell": leverantor.modell,
        "bedomning": bedomningsmapp.name,
    }
    skriv_manifest(mapp, metadata)
    return mapp


def _spara_forsok(avsnittsmapp: Path, forsok: Forsok) -> None:
    (avsnittsmapp / f"forsok-{forsok.nummer}.json").write_text(forsok.model_dump_json(indent=2), encoding="utf-8")


def las_skrivresultat(mapp: Path) -> list[Skrivresultat]:
    return [
        Skrivresultat.model_validate_json(sokvag.read_text(encoding="utf-8"))
        for sokvag in sorted(mapp.glob("*.json"))
        if sokvag.name != MANIFESTNAMN
    ]
```

- [ ] **Step 6: Skriv `src/riskanalys/dokument/claude.py`**

```python
"""Claude som textleverantör via den officiella SDK:n (spec 8.3)."""

import json
from datetime import datetime, timezone
from typing import Any

import anthropic

from riskanalys.dokument.leverantor import Anropsdata, Leveranssvar, LeverantorFel, Tokenanvandning
from riskanalys.dokument.modeller import Avsnittsunderlag, AvsnittsUtkast
from riskanalys.lagring.kontrollsumma import for_text

STANDARDMODELL = "claude-opus-5-5"
STANDARDEFFORT = "high"
MAX_TOKENS = 16000
FALLBACK_BETA = "server-side-fallback-2026-07-01"
RESERVMODELLENS_POST = "fallback_message"
SYSTEMPROMPT = """Du skriver ett avsnitt i en redovisningsbyrås allmänna riskbedömning enligt penningtvättsregelverket.

Regler:
- Använd bara uppgifterna i underlaget. Hitta inte på tal, hot, sårbarheter, kontroller eller källor.
- Risknivåerna kommer från en regelmotor. Återge dem exakt och ändra dem aldrig.
- Skriv varje nivå så att det framgår vad den avser, i någon av formerna "Sannolikheten bedöms som hög.", "Konsekvensen är betydande.", "Risken är hög.", "Risken för finansiering av terrorism bedöms som måttlig." och "Den kvarstående risken är hög."
- Varje stycke ska ha referenser till ID:n i underlaget.
- Minst ett stycke ska vara en motivering som hänvisar till hot och till sårbarheter eller uppgifter och anger den inneboende risknivån, till exempel "Risken är hög."
- Om ett stycke bygger på en uppgift som inte är bekräftad, skriv [VERIFIERA] i stycket och lägg till en oklarhet.
- Skriv aldrig namn på personer. Skriv {roll:FfR} när funktionen för regelefterlevnad avses.
- Undvik bristmönstren i underlaget. Skriv konkret om just den här byrån, inte generellt.
- Skriv sakligt och på svenska."""
SCHEMA = AvsnittsUtkast.model_json_schema()
PROMPT_KONTROLLSUMMA = for_text(SYSTEMPROMPT + "\n" + json.dumps(SCHEMA, sort_keys=True, ensure_ascii=False))
_AVBROTT = {
    "refusal": "Claude avböjde att skriva avsnittet.",
    "max_tokens": f"Svaret blev för långt och avbröts vid {MAX_TOKENS} token.",
}


class ClaudeLeverantor:
    namn = "claude"

    def __init__(self, modell: str = STANDARDMODELL, effort: str = STANDARDEFFORT, klient: Any = None) -> None:
        self.modell = modell
        self.effort = effort
        self._klient = klient if klient is not None else anthropic.Anthropic()

    def skriv(self, underlag: Avsnittsunderlag, aterkoppling: list[str]) -> Leveranssvar:
        try:
            svar = self._klient.beta.messages.create(
                model=self.modell,
                max_tokens=MAX_TOKENS,
                system=SYSTEMPROMPT,
                messages=[{"role": "user", "content": bygg_meddelande(underlag, aterkoppling)}],
                output_config={"effort": self.effort, "format": {"type": "json_schema", "schema": SCHEMA}},
                betas=[FALLBACK_BETA],
                fallbacks="default",
            )
        except anthropic.APIStatusError as fel:
            raise LeverantorFel(f"Claude-API:t svarade med fel {fel.status_code}: {fel.message}") from fel
        except anthropic.APIConnectionError as fel:
            raise LeverantorFel("Kunde inte nå Claude-API:t. Kontrollera nätverket och försök igen.") from fel
        return self._leveranssvar(svar)

    def _leveranssvar(self, svar: Any) -> Leveranssvar:
        anvandning = _anvandning(svar.usage)
        text = next((block.text for block in svar.content if block.type == "text"), "")
        avbrott = _AVBROTT.get(svar.stop_reason) or (None if text else "Claude-svaret saknade text.")
        reservmodell = svar.stop_reason != "refusal" and any(post.typ == RESERVMODELLENS_POST for post in anvandning)
        anrop = Anropsdata(
            leverantor=self.namn,
            begard_modell=self.modell,
            svarsmodell=svar.model,
            effort=self.effort,
            prompt_kontrollsumma=PROMPT_KONTROLLSUMMA,
            svar_id=svar.id,
            stop_reason=svar.stop_reason,
            reservmodell_svarade=reservmodell,
            anvandning=anvandning,
            tidpunkt=datetime.now(timezone.utc),
        )
        return Leveranssvar(anrop=anrop, text=text, avbrott=avbrott)


def bygg_meddelande(underlag: Avsnittsunderlag, aterkoppling: list[str]) -> str:
    delar = ["Underlag för avsnittet, som JSON:", underlag.model_dump_json(indent=2)]
    if aterkoppling:
        rader = "\n".join(f"- {rad}" for rad in aterkoppling)
        delar.append(f"Det förra utkastet underkändes av den maskinella granskningen. Rätta detta:\n{rader}")
    return "\n\n".join(delar)


def _anvandning(usage: Any) -> tuple[Tokenanvandning, ...]:
    """En post per försök hos API:t. Utan iterationer finns bara svarets egen användning."""
    poster = getattr(usage, "iterations", None) or [usage]
    return tuple(
        Tokenanvandning(
            typ=getattr(post, "type", "message"),
            modell=getattr(post, "model", None),
            indata_token=post.input_tokens,
            utdata_token=post.output_tokens,
        )
        for post in poster
    )
```

- [ ] **Step 7: Kör testerna**

Run: `.venv/bin/pytest tester/enhet/test_skrivning.py tester/enhet/test_claude.py -v`
Expected: alla tester passerar.

- [ ] **Step 8: Skriv det felande testet `tester/enhet/test_skriv_kommando.py`**

```python
from riskanalys.bedomning.korning import BEDOMNINGAR
from riskanalys.cli import main
from riskanalys.dokument.skrivning import UTKAST, Forsok
from riskanalys.lagring.korningar import avslutade_korningar
from riskanalys.lagring.manifest import las_manifest


def _skriv(fil):
    return main(["skriv", "testbyra", "--leverantor", "test", "--testsvar", str(fil)])


def test_skriv_fore_bedom_sager_vilket_steg_som_saknas(byra_med_profil, testsvarsfil, capsys):
    assert _skriv(testsvarsfil) == 1
    assert "Kör 'riskanalys bedom testbyra' först" in capsys.readouterr().err


def test_skriv_med_testleverantor(byra_med_profil, testsvarsfil, capsys):
    main(["bedom", "testbyra"])
    assert _skriv(testsvarsfil) == 0
    assert "D-ARB.6.1 Löpande bokföring: godkänt efter 1 försök." in capsys.readouterr().out
    (mapp,) = avslutade_korningar(byra_med_profil, UTKAST)
    manifest = las_manifest(mapp)
    assert manifest.metadata["bedomning"] == avslutade_korningar(byra_med_profil, BEDOMNINGAR)[-1].name
    assert {"D-ARB.6.1.json", "D-ARB.6.1/underlag.json", "D-ARB.6.1/forsok-1.json"} <= set(manifest.filer)


def test_underkant_utkast_ger_felkod_2(byra_med_profil, tmp_path, giltigt_utkast, capsys):
    felaktigt = giltigt_utkast.model_copy(update={"avsnitt": "D-ARB.6.2"}).model_dump_json()
    fil = tmp_path / "fel.json"
    fil.write_text("[" + ",".join([felaktigt] * 3) + "]", encoding="utf-8")
    main(["bedom", "testbyra"])
    assert _skriv(fil) == 2
    assert "underkänt efter 3 försök" in capsys.readouterr().out


def test_avbruten_skrivning_behaller_forsoken_men_raknas_inte(byra_med_profil, tmp_path, giltigt_utkast, capsys):
    felaktigt = giltigt_utkast.model_copy(update={"avsnitt": "D-ARB.6.2"}).model_dump_json()
    fil = tmp_path / "ett_svar.json"
    fil.write_text("[" + felaktigt + "]", encoding="utf-8")
    main(["bedom", "testbyra"])
    assert _skriv(fil) == 1
    assert "Försöken som hann göras är sparade" in capsys.readouterr().err
    assert avslutade_korningar(byra_med_profil, UTKAST) == []
    (sparat,) = (byra_med_profil / UTKAST).glob("*/D-ARB.6.1/forsok-1.json")
    forsok = Forsok.model_validate_json(sparat.read_text(encoding="utf-8"))
    assert (forsok.anrop.svar_id, forsok.anrop.svarsmodell) == ("test-1", "testleverantor")
    assert forsok.fel


def test_skriv_efter_andrad_profil_vagras(byra_med_profil, testsvarsfil, capsys):
    main(["bedom", "testbyra"])
    main(["bekrafta", "testbyra", "P-ORG.antal_anstallda", "9", "--kalla", "Lönelistan"])
    assert _skriv(testsvarsfil) == 1
    assert "Profilen har ändrats sedan bedömningen" in capsys.readouterr().err


def test_claude_utan_api_nyckel_ger_tydligt_fel(byra_med_profil, monkeypatch, capsys):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    main(["bedom", "testbyra"])
    assert main(["skriv", "testbyra"]) == 1
    assert "ANTHROPIC_API_KEY" in capsys.readouterr().err


def test_testleverantor_utan_fil_ger_tydligt_fel(byra_med_profil, capsys):
    main(["bedom", "testbyra"])
    assert main(["skriv", "testbyra", "--leverantor", "test"]) == 1
    assert "--testsvar" in capsys.readouterr().err
```

- [ ] **Step 9: Skriv `src/riskanalys/kommandon/skriv_kommando.py`**

```python
"""riskanalys skriv"""

import argparse
import os
from pathlib import Path
from typing import Any

from riskanalys.dokument.claude import STANDARDEFFORT, STANDARDMODELL, ClaudeLeverantor
from riskanalys.dokument.leverantor import LeverantorFel, Textleverantor, ladda_testleverantor
from riskanalys.dokument.skrivning import kor_skrivning, las_skrivresultat
from riskanalys.kommandon import ladda_giltig_regelbas, regelbasargument
from riskanalys.lagring.datamapp import befintlig_byramapp


def lagg_till(underparsers: Any) -> None:
    parser = underparsers.add_parser("skriv", help="Låt AI skriva riskavsnitten utifrån den senaste bedömningen.")
    parser.add_argument("byra")
    parser.add_argument("--leverantor", choices=["claude", "test"], default="claude")
    parser.add_argument("--testsvar", type=Path, help="JSON-fil med förberedda svar. Krävs med --leverantor test.")
    parser.add_argument("--modell", default=STANDARDMODELL, help=f"Standard är {STANDARDMODELL}.")
    parser.add_argument("--effort", default=STANDARDEFFORT, help=f"Standard är {STANDARDEFFORT}.")
    regelbasargument(parser)
    parser.set_defaults(kor=kor_skriv)


def valj_leverantor(args: argparse.Namespace) -> Textleverantor:
    if args.leverantor == "test":
        if args.testsvar is None:
            raise LeverantorFel("Ange en fil med förberedda svar med --testsvar.")
        return ladda_testleverantor(args.testsvar)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise LeverantorFel(
            "Sätt miljövariabeln ANTHROPIC_API_KEY för att använda Claude, eller använd --leverantor test."
        )
    return ClaudeLeverantor(modell=args.modell, effort=args.effort)


def kor_skriv(args: argparse.Namespace) -> int:
    byramapp = befintlig_byramapp(args.byra)
    regelbas = ladda_giltig_regelbas(args.regelbas)
    mapp = kor_skrivning(byramapp, regelbas, valj_leverantor(args))
    resultat = las_skrivresultat(mapp)
    for post in resultat:
        status = "godkänt" if post.godkant_utkast else "underkänt"
        print(f"{post.underlag.avsnitt} {post.underlag.rubrik}: {status} efter {len(post.forsok)} försök.")
        if post.godkant_utkast is None:
            for rad in post.forsok[-1].fel:
                print(f"  - {rad}")
    print(f"Sparad i {mapp}.")
    if all(post.godkant_utkast for post in resultat):
        print(f"Nästa steg: registrera utvärderingen med 'riskanalys utvardera {args.byra}' om det inte är gjort.")
        print(f"Granska sedan med 'riskanalys granska {args.byra}'.")
        return 0
    print("Minst ett avsnitt underkändes. Kör 'riskanalys skriv' igen eller rätta underlaget.")
    return 2
```

`valj_leverantor` kontrollerar `ANTHROPIC_API_KEY` innan klienten skapas, så att användaren får ett svenskt meddelande. Den som i stället loggat in med `ant auth login` sätter variabeln eller använder `--leverantor test`; inloggning utan nyckel kan läggas till senare.

- [ ] **Step 10: Registrera kommandot i `src/riskanalys/cli.py`**

Ersätt raderna

```python
from riskanalys.kommandon import bedom_kommando, drift_kommando, profil_kommando, regelbas_kommando

KOMMANDON = [regelbas_kommando, profil_kommando, drift_kommando, bedom_kommando]
```

med

```python
from riskanalys.kommandon import (
    bedom_kommando,
    drift_kommando,
    profil_kommando,
    regelbas_kommando,
    skriv_kommando,
)

KOMMANDON = [regelbas_kommando, profil_kommando, drift_kommando, bedom_kommando, skriv_kommando]
```

- [ ] **Step 11: Skriv livetestet `tester/live/test_claude_live.py`**

```python
"""Livetest mot det riktiga Claude-API:t. Kostar pengar. Körs bara med RISKANALYS_LIVE=1."""

import os

import pytest

from riskanalys.dokument.claude import ClaudeLeverantor
from riskanalys.dokument.skrivning import skriv_avsnitt

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(os.environ.get("RISKANALYS_LIVE") != "1", reason="Livetester körs bara med RISKANALYS_LIVE=1."),
]


def test_claude_skriver_ett_godkant_avsnitt(real_underlag):
    resultat = skriv_avsnitt(ClaudeLeverantor(), real_underlag, ("Testa Testsson",))
    assert resultat.godkant_utkast is not None, resultat.forsok[-1].fel
    anrop = resultat.forsok[-1].anrop
    assert anrop.svar_id
    assert anrop.svarsmodell
    assert sum(post.utdata_token for post in anrop.anvandning) > 0
```

Livetestet körs för hand med `RISKANALYS_LIVE=1 .venv/bin/pytest -m live tester/live -v`. Det andra `-m` på kommandoraden ersätter `-m 'not live'` från `pyproject.toml`. Livetestet bekräftar också att API:t godtar anropets form (`betas`, `fallbacks="default"`, `output_config`), vilket de automatiska testerna med falsk klient inte kan visa.

- [ ] **Step 12: Kör alla tester utom livetester**

Run: `.venv/bin/pytest -v`
Expected: alla tester passerar och livetestet räknas som avvalt (deselected).

- [ ] **Step 13: Commit**

```bash
git add src/riskanalys/dokument/skrivning.py src/riskanalys/dokument/claude.py src/riskanalys/kommandon/skriv_kommando.py src/riskanalys/cli.py tester/conftest.py tester/enhet/test_skrivning.py tester/enhet/test_claude.py tester/enhet/test_skriv_kommando.py tester/live/test_claude_live.py
git commit -m "feat: AI-skrivning med löpande sparade försök, Claude-leverantör och kommandot skriv"
```

---

### Task 17: Sammanställning av den allmänna riskbedömningen

**Files:**
- Create: `src/riskanalys/dokument/arb.py`
- Test: `tester/enhet/test_arb.py`

**Interfaces:**
- Consumes: `Bedomning`, `Tjanstbedomning`, `Avsnitt`, `AvsnittsUtkast`, `Dokument`, `Textstycke`, `sarbarhet_status`, `tjanster_med_avsnitt`, `VERIFIERA`, `Historik`, `visa_varde`, `Profil`, `tolka_villkor`, `falt_i`.
- Produces:
  - `DOKUMENT_ID = "D-ARB"`, `TITEL = "Allmän riskbedömning"`, `ROLL_FFR = "{roll:FfR}"`.
  - `bygg_arb(regelbas, profil, bedomning, utkast: dict[str, AvsnittsUtkast], historik: Historik) -> Dokument`.
  - Avsnitt i ordning: `D-ARB.1` Syfte, omfattning och ansvar; `D-ARB.3` Byråns tjänster; `D-ARB.4` Hot; `D-ARB.5` Sårbarheter; `D-ARB.6.n` Risk i tjänsten (bara om ett godkänt AI-utkast finns); `D-ARB.10` Utvärdering och uppdatering. Avsnitt 2 och 7–9 tillkommer i M5.

Bara riskavsnitten skrivs av AI. Övriga avsnitt byggs direkt ur regelbasen och profilen. Personer skrivs som `{roll:FfR}` och byts ut först vid rendering. En uppgift som inte är bekräftad skrivs som `[VERIFIERA]`.

- [ ] **Step 1: Skriv det felande testet `tester/enhet/test_arb.py`**

```python
from datetime import date

from riskanalys.bedomning.motor import bedom
from riskanalys.dokument.arb import bygg_arb
from riskanalys.drift.historik import Handelse, Historik
from riskanalys.regelverk.urval import valj

HISTORIK = Historik().med(Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Första."))


def _arb(regelbas, profil, utkast, historik=HISTORIK):
    bedomning = bedom(regelbas, valj(regelbas, "RP-RED-VG", date(2026, 11, 1), "Västra Götaland"), profil)
    return bygg_arb(regelbas, profil, bedomning, utkast, historik)


def _texter(dokument, avsnitt_id):
    return [stycke.text for stycke in dokument.avsnitt_med_id()[avsnitt_id].stycken]


def test_avsnitten_kommer_i_ordning(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    dokument = _arb(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast})
    assert [avsnitt.id for avsnitt in dokument.avsnitt] == [
        "D-ARB.1",
        "D-ARB.3",
        "D-ARB.4",
        "D-ARB.5",
        "D-ARB.6.1",
        "D-ARB.10",
    ]
    riskavsnitt = dokument.avsnitt_med_id()["D-ARB.6.1"]
    assert riskavsnitt.kalla == "ai"
    assert list(riskavsnitt.stycken) == giltigt_utkast.stycken


def test_personer_skrivs_som_roll(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    text = _arb(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast}).model_dump_json()
    assert "{roll:FfR}" in text
    assert "Testa Testsson" not in text
    assert "Testbyrån AB" in text


def test_alla_referenser_finns_i_regelbasen(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    dokument = _arb(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast})
    referenser = {ref for avsnitt in dokument.avsnitt for stycke in avsnitt.stycken for ref in stycke.referenser}
    assert referenser <= regelbas.alla_id()


def test_utan_godkant_utkast_saknas_riskavsnittet(regelbas, profil_fabrik, real_varden):
    dokument = _arb(regelbas, profil_fabrik(regelbas, real_varden), {})
    assert "D-ARB.6.1" not in dokument.avsnitt_med_id()


def test_utan_historik_markeras_datumet(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    dokument = _arb(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast}, Historik())
    assert _texter(dokument, "D-ARB.10") == ["Datum för utvärdering saknas. [VERIFIERA]"]


def test_utvarderingsdatum_och_nasta_genomgang(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    dokument = _arb(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast})
    (text,) = _texter(dokument, "D-ARB.10")
    assert text.startswith("Riskbedömningen utvärderades senast 2026-11-01. Nästa utvärdering görs senast 2027-11-01")


def test_faststallelse_andrar_inte_utvarderingsdatumet(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    historik = HISTORIK.med(Handelse(datum=date(2026, 11, 20), typ="fastställelse", beskrivning="v1", version=1))
    dokument = _arb(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast}, historik)
    (text,) = _texter(dokument, "D-ARB.10")
    assert "utvärderades senast 2026-11-01" in text
    assert "senast 2027-11-01" in text


def test_okanda_uppgifter_markeras(regelbas, profil_fabrik, real_varden):
    profil = profil_fabrik(regelbas, real_varden, okanda=("P-ORG.antal_anstallda", "P-KUND.andel_riskbransch"))
    dokument = _arb(regelbas, profil, {})
    assert "[VERIFIERA]" in _texter(dokument, "D-ARB.1")[0]
    assert "Kunder i branscher med förhöjd risk (Löpande bokföring): Okänt, eftersom uppgifter saknas. [VERIFIERA]" in (
        _texter(dokument, "D-ARB.5")
    )


def test_sarbarheterna_beskrivs_enligt_profilen(regelbas, profil_fabrik, real_varden):
    texter = _texter(_arb(regelbas, profil_fabrik(regelbas, real_varden), {}), "D-ARB.5")
    assert "Kunder i branscher med förhöjd risk (Löpande bokföring): Gäller enligt byråns uppgifter." in texter
    assert "Juniora konsulter arbetar självständigt (Löpande bokföring): Gäller inte enligt byråns uppgifter." in texter
```

- [ ] **Step 2: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/enhet/test_arb.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.dokument.arb'`.

- [ ] **Step 3: Skriv `src/riskanalys/dokument/arb.py`**

```python
"""Sammanställer den allmänna riskbedömningen (spec 11). Bara riskavsnitten är skrivna av AI."""

from riskanalys.bedomning.modeller import Bedomning, Tjanstbedomning
from riskanalys.dokument.modeller import Avsnitt, AvsnittsUtkast, Dokument, Textstycke
from riskanalys.dokument.underlag import sarbarhet_status, tjanster_med_avsnitt
from riskanalys.dokument.validering import VERIFIERA
from riskanalys.drift.historik import Historik
from riskanalys.profil.hantering import visa_varde
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.villkor import falt_i, tolka_villkor

DOKUMENT_ID = "D-ARB"
TITEL = "Allmän riskbedömning"
ROLL_FFR = "{roll:FfR}"
FALT_NAMN = "P-ORG.namn"
FALT_ANSTALLDA = "P-ORG.antal_anstallda"
FALT_VERKSAMHETSSTALLEN = "P-ORG.verksamhetsstallen"
FALT_FFR = "P-ROLL.ffr_namn"
_SARBARHETSTEXT = {
    "ja": "Gäller enligt byråns uppgifter.",
    "nej": "Gäller inte enligt byråns uppgifter.",
    "okänt": f"Okänt, eftersom uppgifter saknas. {VERIFIERA}",
}


def bygg_arb(
    regelbas: Regelbas,
    profil: Profil,
    bedomning: Bedomning,
    utkast: dict[str, AvsnittsUtkast],
    historik: Historik,
) -> Dokument:
    erbjudna = [tjanst for tjanst in bedomning.tjanster if tjanst.inneboende is not None]
    return Dokument(
        id=DOKUMENT_ID,
        titel=TITEL,
        avsnitt=(
            _syfte(regelbas, profil, bedomning),
            _tjanster(regelbas, bedomning),
            _hot(regelbas, erbjudna),
            _sarbarheter(regelbas, profil, erbjudna),
            *_riskavsnitt(regelbas, bedomning, utkast),
            _utvardering(historik),
        ),
    )


def _stycke(typ: str, text: str, referenser: list[str]) -> Textstycke:
    return Textstycke(typ=typ, text=text, referenser=referenser)


def _varde(regelbas: Regelbas, profil: Profil, falt_id: str) -> str:
    if not profil.ar_bekraftad(falt_id):
        return VERIFIERA
    return visa_varde(regelbas.falt[falt_id], profil.uppgifter[falt_id].varde)


def _syfte(regelbas: Regelbas, profil: Profil, bedomning: Bedomning) -> Avsnitt:
    paket = regelbas.regelpaket[bedomning.regelpaket]
    roll = ROLL_FFR if profil.ar_bekraftad(FALT_FFR) else VERIFIERA
    stycken = (
        _stycke(
            "beskrivning",
            f"Den här allmänna riskbedömningen gäller {_varde(regelbas, profil, FALT_NAMN)}. "
            f"Antal personer i verksamheten, inklusive ägare: {_varde(regelbas, profil, FALT_ANSTALLDA)}. "
            f"Antal verksamhetsställen: {_varde(regelbas, profil, FALT_VERKSAMHETSSTALLEN)}.",
            [FALT_NAMN, FALT_ANSTALLDA, FALT_VERKSAMHETSSTALLEN],
        ),
        _stycke(
            "beskrivning",
            f"Bedömningen följer regelpaketet {paket.namn} för {bedomning.lan} och gäller regelverket per "
            f"{bedomning.datum.isoformat()}. Den bygger på regelbas version {bedomning.regelbas_version}.",
            [],
        ),
        _stycke(
            "beskrivning",
            f"Funktionen för regelefterlevnad utövas av {roll}. Funktionen ansvarar för att riskbedömningen "
            "utvärderas och hålls aktuell.",
            [FALT_FFR],
        ),
    )
    return Avsnitt(id="D-ARB.1", rubrik="Syfte, omfattning och ansvar", kalla="regelbas", stycken=stycken)


def _tjanster(regelbas: Regelbas, bedomning: Bedomning) -> Avsnitt:
    stycken = tuple(_tjanststycke(regelbas, tjanst) for tjanst in bedomning.tjanster)
    return Avsnitt(id="D-ARB.3", rubrik="Byråns tjänster", kalla="regelbas", stycken=stycken)


def _tjanststycke(regelbas: Regelbas, tjanstbedomning: Tjanstbedomning) -> Textstycke:
    tjanst = regelbas.tjanster[tjanstbedomning.tjanst]
    if tjanstbedomning.erbjuds is False:
        text = f"{tjanst.namn}: erbjuds inte."
    elif tjanstbedomning.erbjuds is None:
        text = f"{tjanst.namn}: okänt om tjänsten erbjuds. {VERIFIERA}"
    else:
        text = f"{tjanst.namn}: erbjuds. {tjanst.beskrivning}"
    return _stycke("beskrivning", text, [tjanst.id, tjanst.erbjuds_falt])


def _hot(regelbas: Regelbas, erbjudna: list[Tjanstbedomning]) -> Avsnitt:
    stycken = tuple(
        _stycke(
            "analys",
            f"{hot.namn} ({regelbas.tjanster[tjanst.tjanst].namn}). {hot.beskrivning} "
            f"Källor: {', '.join(regelbas.kallor[kalla].titel for kalla in hot.kallor)}.",
            [hot.id, tjanst.tjanst, *hot.kallor],
        )
        for tjanst in erbjudna
        for hot in (regelbas.hot[hot_id] for hot_id in tjanst.hot)
    )
    return Avsnitt(id="D-ARB.4", rubrik="Hot", kalla="regelbas", stycken=stycken)


def _sarbarheter(regelbas: Regelbas, profil: Profil, erbjudna: list[Tjanstbedomning]) -> Avsnitt:
    definitioner = regelbas.faltdefinitioner()
    stycken = tuple(
        _stycke(
            "analys",
            f"{sarbarhet.namn} ({regelbas.tjanster[tjanst.tjanst].namn}): "
            f"{_SARBARHETSTEXT[sarbarhet_status(regelbas, profil, sarbarhet.id)]}",
            [sarbarhet.id, *sorted(falt_i(tolka_villkor(sarbarhet.villkor, definitioner)))],
        )
        for tjanst in erbjudna
        for sarbarhet in (regelbas.sarbarheter[sid] for sid in regelbas.tjanster[tjanst.tjanst].sarbarheter)
    )
    return Avsnitt(id="D-ARB.5", rubrik="Sårbarheter", kalla="regelbas", stycken=stycken)


def _riskavsnitt(regelbas: Regelbas, bedomning: Bedomning, utkast: dict[str, AvsnittsUtkast]) -> tuple[Avsnitt, ...]:
    return tuple(
        Avsnitt(
            id=avsnitt_id,
            rubrik=f"Risk i {regelbas.tjanster[tjanst.tjanst].namn.lower()}",
            kalla="ai",
            stycken=tuple(utkast[avsnitt_id].stycken),
        )
        for avsnitt_id, tjanst in tjanster_med_avsnitt(bedomning)
        if avsnitt_id in utkast
    )


def _utvardering(historik: Historik) -> Avsnitt:
    senaste, nasta = historik.senaste_utvardering(), historik.nasta_genomgang()
    if senaste is None or nasta is None:
        text = f"Datum för utvärdering saknas. {VERIFIERA}"
    else:
        text = (
            f"Riskbedömningen utvärderades senast {senaste.isoformat()}. Nästa utvärdering görs senast "
            f"{nasta.isoformat()}, och alltid innan byrån erbjuder nya eller väsentligt ändrade tjänster, riktar "
            "sig till nya marknader eller gör andra förändringar som är relevanta för verksamheten."
        )
    return Avsnitt(
        id="D-ARB.10",
        rubrik="Utvärdering och uppdatering",
        kalla="regelbas",
        stycken=(_stycke("beskrivning", text, []),),
    )
```

- [ ] **Step 4: Kör testet**

Run: `.venv/bin/pytest tester/enhet/test_arb.py -v`
Expected: alla tester passerar.

- [ ] **Step 5: Commit**

```bash
git add src/riskanalys/dokument/arb.py tester/enhet/test_arb.py
git commit -m "feat: sammanställning av den allmänna riskbedömningen"
```

---

### Task 18: Maskinell granskning och kommandot `granska`

**Files:**
- Create: `src/riskanalys/granskning/__init__.py`, `modeller.py`, `kontroller.py`, `korning.py`
- Create: `src/riskanalys/kommandon/granska_kommando.py`
- Modify: `src/riskanalys/cli.py`
- Modify: `tester/conftest.py` (hjälpfunktionen `kor_till_skrivning` och fixturen `skriven_byra`)
- Test: `tester/regelkontrakt/test_granskning.py`, `tester/enhet/test_granskning_korning.py`

**Interfaces:**
- Consumes: `Regelbas`, `Urval`, `valj`, `kravet_galler`, `Profil`, `Bedomning`, `Dokument`, `Historik`, `las_historik`, `historikens_kontrollsumma`, `tjanster_med_avsnitt`, `VERIFIERA`, `motivering_har_hot_och_sarbarhet`, `bygg_arb`, `UTKAST`, `las_skrivresultat`, `BEDOMNINGAR`, `kontrollera_aktuell`, `las_bedomning`, `las_bedomningsprofil`, `avslutade_korningar`, `senaste_korning`, `ny_korningsmapp`, `skriv_manifest`, `las_manifest`, typaliasen `Allvar` och `Grund`.
- Produces:
  - `granskning/modeller.py`: `Fynd(id, typ: Literal["tackning", "sparbarhet", "bristmonster", "provtillsyn", "sakgranskning"], regel: str | None = None, allvar: Allvar, grund: Grund, avsnitt: str | None = None, beskrivning: str, atgard: str, status: Literal["öppen", "åtgärdad", "accepterad_metodavvikelse", "sakkunnigbedömd"] = "öppen", motivering: str | None = None, hanterad_av: str | None = None)`.
  - `granskning/kontroller.py`: `granska(regelbas, urval, profil, bedomning, dokument, historik, granskningsdatum: date) -> tuple[Fynd, ...]`. Fynd-ID har formen `F-ÅÅÅÅ-MM-DD-001`. Profilen används för att avgöra vilka krav som gäller byrån (`kravet_galler`).
  - `granskning/korning.py`: `GRANSKNING = "granskning"`, `DOKUMENTFIL = "dokument.json"`, `FYNDFIL = "fynd.json"`, `godkanda_utkast(byramapp, bedomningsmapp) -> tuple[dict[str, AvsnittsUtkast], Path | None]`, `kor_granskning(byramapp, regelbas, granskningsdatum) -> Path`, `las_granskning(mapp) -> tuple[Dokument, tuple[Fynd, ...]]`, `granskningens_profil(byramapp, granskningsmapp) -> Profil`, `andrade_kallor(byramapp, granskningsmapp) -> list[str]` och `kontrollera_kallor(byramapp, granskningsmapp) -> None`. Alla senare steg som läser en granskning (export, sakgranskning, fastställelse) kontrollerar först granskningens, bedömningens och AI-utkastens manifest med dem.
  - Manifestets metadata för granskning: `typ = "granskning"`, `bedomning`, `utkast` (mappnamn eller tom sträng), `historik` (historikens kontrollsumma), `blockerande` (antal), `datum`.
  - Kommandot `granska <byra> [--datum D]`. Returnerar 0 utan blockerande fynd och 2 med blockerande fynd.
  - I `tester/conftest.py`: hjälpfunktionen `kor_till_skrivning(byramapp, regelbas, utkast)` och fixturen `skriven_byra` (byrå med bedömning, godkänt AI-utkast och registrerad utvärdering 2026-11-01).

Granskningen bygger dokumentet ur den senaste bedömningen och de godkända AI-utkasten som hör till just den bedömningen. Utkast från en äldre bedömning används aldrig. Kontrollerna i M1 (spec 9):

| Kontroll | Fynd | Allvar och grund |
|---|---|---|
| Täckning: varje krav som gäller byrån har sitt avsnitt | `tackning`, regel = krav-ID | blockerande, kravets grund |
| Bedömningen är preliminär | `tackning` | hög, ska_krav |
| `[VERIFIERA]` i ett avsnitt | `sparbarhet` | hög, ska_krav |
| Referens som inte finns i regelbasen | `sparbarhet` | blockerande, metodval |
| B-04 tjänst utan eget riskavsnitt | `bristmonster` | enligt katalogen |
| B-12 riskavsnitt utan motivering med hot och sårbarhet | `bristmonster` | enligt katalogen |
| B-16 datum för utvärdering saknas | `bristmonster` | enligt katalogen |

- [ ] **Step 1: Lägg till hjälpfunktion och fixtur sist i `tester/conftest.py`**

```python
def kor_till_skrivning(byramapp, regelbas, utkast):
    """Kör bedömning och skrivning med testleverantören och registrerar en utvärdering 2026-11-01."""
    from riskanalys.bedomning.korning import kor_bedomning
    from riskanalys.dokument.leverantor import Testleverantor
    from riskanalys.dokument.skrivning import kor_skrivning
    from riskanalys.drift.historik import Handelse, las_historik, spara_historik

    kor_bedomning(byramapp, regelbas)
    kor_skrivning(byramapp, regelbas, Testleverantor([utkast]))
    handelse = Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Första riskbedömningen.")
    spara_historik(byramapp, las_historik(byramapp).med(handelse))


@pytest.fixture
def skriven_byra(byra_med_profil, regelbas, giltigt_utkast):
    """En byrå med bedömning, godkänt AI-utkast och registrerad utvärdering."""
    kor_till_skrivning(byra_med_profil, regelbas, giltigt_utkast)
    return byra_med_profil
```

- [ ] **Step 2: Skriv det felande testet `tester/regelkontrakt/test_granskning.py`**

```python
from datetime import date

from riskanalys.bedomning.motor import bedom
from riskanalys.dokument.arb import bygg_arb
from riskanalys.drift.historik import Handelse, Historik
from riskanalys.granskning.kontroller import granska
from riskanalys.regelverk.urval import valj

DAG = date(2026, 11, 2)
HISTORIK = Historik().med(Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Första."))


def _granska(regelbas, profil, utkast, historik=HISTORIK):
    urval = valj(regelbas, "RP-RED-VG", date(2026, 11, 1), "Västra Götaland")
    bedomning = bedom(regelbas, urval, profil)
    dokument = bygg_arb(regelbas, profil, bedomning, utkast, historik)
    return granska(regelbas, urval, profil, bedomning, dokument, historik, DAG)


def test_fullstandigt_dokument_ger_inga_fynd(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    assert _granska(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast}) == ()


def test_saknat_riskavsnitt_ger_tackningsfynd_och_b04(regelbas, profil_fabrik, real_varden):
    fynd = {post.regel: post for post in _granska(regelbas, profil_fabrik(regelbas, real_varden), {})}
    assert set(fynd) == {"KRV-LSF-005", "B-04"}
    assert (fynd["KRV-LSF-005"].allvar, fynd["KRV-LSF-005"].grund) == ("blockerande", "ska_krav")
    assert (fynd["B-04"].allvar, fynd["B-04"].typ) == ("hög", "bristmonster")


def test_krav_som_inte_galler_byran_kravs_inte(regelbas, profil_fabrik, real_varden):
    krav = regelbas.krav["KRV-LSF-005"]
    villkor = {"falt": "P-VERK.juniora_konsulter", "op": "==", "varde": True}
    andrad = regelbas.model_copy(
        update={"krav": {**regelbas.krav, krav.id: krav.model_copy(update={"galler_om": villkor})}}
    )
    fynd = _granska(andrad, profil_fabrik(andrad, real_varden), {})
    assert {post.regel for post in fynd} == {"B-04"}


def test_krav_med_okand_tillamplighet_kravs(regelbas, profil_fabrik, real_varden):
    krav = regelbas.krav["KRV-LSF-005"]
    villkor = {"falt": "P-VERK.juniora_konsulter", "op": "==", "varde": True}
    andrad = regelbas.model_copy(
        update={"krav": {**regelbas.krav, krav.id: krav.model_copy(update={"galler_om": villkor})}}
    )
    profil = profil_fabrik(andrad, real_varden, okanda=("P-VERK.juniora_konsulter",))
    assert "KRV-LSF-005" in {post.regel for post in _granska(andrad, profil, {})}


def test_saknad_utvardering_ger_b16(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    fynd = _granska(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast}, Historik())
    assert {post.regel for post in fynd} == {None, "B-16"}
    assert any(post.beskrivning == "Avsnitt D-ARB.10 innehåller [VERIFIERA]." for post in fynd)


def test_okand_referens_ar_blockerande(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    stycken = list(giltigt_utkast.stycken)
    stycken[0] = stycken[0].model_copy(update={"referenser": ["T-RED-01", "H-99"]})
    utkast = giltigt_utkast.model_copy(update={"stycken": stycken})
    (fynd,) = _granska(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": utkast})
    assert (fynd.typ, fynd.allvar) == ("sparbarhet", "blockerande")
    assert fynd.beskrivning == "Avsnitt D-ARB.6.1 hänvisar till H-99, som inte finns i regelbasen."


def test_preliminar_bedomning_ger_fynd(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    profil = profil_fabrik(regelbas, real_varden, okanda=("P-KUND.andel_kontant",))
    fynd = _granska(regelbas, profil, {"D-ARB.6.1": giltigt_utkast})
    assert [post.beskrivning for post in fynd] == [
        "Bedömningen är preliminär. Okända uppgifter: P-KUND.andel_kontant.",
        "Avsnitt D-ARB.5 innehåller [VERIFIERA].",
    ]


def test_motivering_utan_hot_ger_b12(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    stycken = [stycke.model_copy(update={"typ": "analys"}) for stycke in giltigt_utkast.stycken]
    utkast = giltigt_utkast.model_copy(update={"stycken": stycken})
    fynd = _granska(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": utkast})
    assert [post.regel for post in fynd] == ["B-12"]


def test_fynd_far_lopnummer_med_datum(regelbas, profil_fabrik, real_varden):
    fynd = _granska(regelbas, profil_fabrik(regelbas, real_varden), {})
    assert [post.id for post in fynd] == ["F-2026-11-02-001", "F-2026-11-02-002"]
```

- [ ] **Step 3: Skriv det felande testet `tester/enhet/test_granskning_korning.py`**

```python
from datetime import date

import pytest

from riskanalys.bedomning.korning import BEDOMNINGAR, kor_bedomning
from riskanalys.cli import main
from riskanalys.dokument.skrivning import UTKAST
from riskanalys.fel import RiskanalysFel
from riskanalys.granskning.korning import (
    andrade_kallor,
    granskningens_profil,
    kontrollera_kallor,
    kor_granskning,
    las_granskning,
)
from riskanalys.lagring.korningar import avslutade_korningar
from riskanalys.lagring.manifest import las_manifest
from riskanalys.profil.hantering import bekrafta
from riskanalys.profil.lagring import las_profil, spara_profil

DAG = date(2026, 11, 2)


def test_granska_fore_bedom_sager_vilket_steg_som_saknas(byra_med_profil, regelbas):
    with pytest.raises(RiskanalysFel, match="Kör 'riskanalys bedom testbyra' först"):
        kor_granskning(byra_med_profil, regelbas, DAG)


def test_granskning_av_skriven_byra(skriven_byra, regelbas):
    mapp = kor_granskning(skriven_byra, regelbas, DAG)
    dokument, fynd = las_granskning(mapp)
    assert fynd == ()
    assert "D-ARB.6.1" in dokument.avsnitt_med_id()
    metadata = las_manifest(mapp).metadata
    assert metadata["bedomning"] == avslutade_korningar(skriven_byra, BEDOMNINGAR)[-1].name
    assert metadata["blockerande"] == "0"
    assert metadata["historik"].startswith("sha256:")


def test_profil_andrad_efter_bedomningen_stoppar_granskningen(skriven_byra, regelbas):
    profil = bekrafta(las_profil(skriven_byra), regelbas, "P-ORG.antal_anstallda", "9", "Lönelistan", "FfR", DAG)
    spara_profil(skriven_byra, profil)
    with pytest.raises(RiskanalysFel, match="Profilen har ändrats sedan bedömningen"):
        kor_granskning(skriven_byra, regelbas, DAG)


def test_utkast_fran_en_aldre_bedomning_anvands_inte(skriven_byra, regelbas):
    kor_bedomning(skriven_byra, regelbas)
    dokument, fynd = las_granskning(kor_granskning(skriven_byra, regelbas, DAG))
    assert "D-ARB.6.1" not in dokument.avsnitt_med_id()
    assert {"KRV-LSF-005", "B-04"} <= {post.regel for post in fynd}


def test_kallorna_till_en_ny_granskning_ar_oforandrade(skriven_byra, regelbas):
    assert andrade_kallor(skriven_byra, kor_granskning(skriven_byra, regelbas, DAG)) == []


def test_granskningens_profil_ar_bedomningens_kopia(skriven_byra, regelbas):
    assert granskningens_profil(skriven_byra, kor_granskning(skriven_byra, regelbas, DAG)) == las_profil(skriven_byra)


def _andra_fil(fil):
    fil.write_text(fil.read_text(encoding="utf-8").replace("Testbyrån AB", "Annan byrå AB"), encoding="utf-8")


def test_andrad_profilkopia_i_bedomningen_upptacks(skriven_byra, regelbas):
    mapp = kor_granskning(skriven_byra, regelbas, DAG)
    bedomningsmapp = skriven_byra / BEDOMNINGAR / las_manifest(mapp).metadata["bedomning"]
    _andra_fil(bedomningsmapp / "profil.yaml")
    assert andrade_kallor(skriven_byra, mapp) == ["Bedömningen är ändrad efter körningen. Fil ändrad: profil.yaml"]
    with pytest.raises(RiskanalysFel, match="Kör om kedjan från 'riskanalys bedom'"):
        kontrollera_kallor(skriven_byra, mapp)


def test_andrat_ai_utkast_upptacks(skriven_byra, regelbas):
    mapp = kor_granskning(skriven_byra, regelbas, DAG)
    utkastfil = skriven_byra / UTKAST / las_manifest(mapp).metadata["utkast"] / "D-ARB.6.1.json"
    utkastfil.write_text(utkastfil.read_text(encoding="utf-8").replace("byggkund", "kund"), encoding="utf-8")
    assert andrade_kallor(skriven_byra, mapp) == ["AI-utkasten är ändrade efter skrivningen. Fil ändrad: D-ARB.6.1.json"]


def test_andrad_granskning_upptacks_forst(skriven_byra, regelbas):
    mapp = kor_granskning(skriven_byra, regelbas, DAG)
    _andra_fil(mapp / "dokument.json")
    assert andrade_kallor(skriven_byra, mapp) == ["Granskningen är ändrad efter körningen. Fil ändrad: dokument.json"]


def test_granska_kommandot(skriven_byra, capsys):
    assert main(["granska", "testbyra", "--datum", "2026-11-02"]) == 0
    assert "Fynd: 0." in capsys.readouterr().out


def test_blockerande_fynd_ger_felkod_2(byra_med_profil, capsys):
    main(["bedom", "testbyra"])
    assert main(["granska", "testbyra"]) == 2
    assert "blockerande" in capsys.readouterr().out
```

- [ ] **Step 4: Kör testerna för att se att de fallerar**

Run: `.venv/bin/pytest tester/regelkontrakt/test_granskning.py tester/enhet/test_granskning_korning.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.granskning'`.

- [ ] **Step 5: Skriv `src/riskanalys/granskning/__init__.py`**

```python
"""Maskinell granskning: täckning, spårbarhet och bristmönster."""
```

- [ ] **Step 6: Skriv `src/riskanalys/granskning/modeller.py`**

```python
"""Fynd från granskningen (spec 9 och 10)."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from riskanalys.regelverk.modeller import Allvar, Grund


class Fynd(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    typ: Literal["tackning", "sparbarhet", "bristmonster", "provtillsyn", "sakgranskning"]
    regel: str | None = None
    allvar: Allvar
    grund: Grund
    avsnitt: str | None = None
    beskrivning: str
    atgard: str
    status: Literal["öppen", "åtgärdad", "accepterad_metodavvikelse", "sakkunnigbedömd"] = "öppen"
    motivering: str | None = None
    hanterad_av: str | None = None
```

- [ ] **Step 7: Skriv `src/riskanalys/granskning/kontroller.py`**

```python
"""Maskinell granskning av dokumentet: täckning, spårbarhet och bristmönster (spec 9)."""

from datetime import date
from typing import Any

from riskanalys.bedomning.modeller import Bedomning
from riskanalys.dokument.modeller import Dokument
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.dokument.validering import VERIFIERA, motivering_har_hot_och_sarbarhet
from riskanalys.drift.historik import Historik
from riskanalys.fel import RiskanalysFel
from riskanalys.granskning.modeller import Fynd
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.urval import Urval, kravet_galler

RISKAVSNITT = "D-ARB.6."


def granska(
    regelbas: Regelbas,
    urval: Urval,
    profil: Profil,
    bedomning: Bedomning,
    dokument: Dokument,
    historik: Historik,
    granskningsdatum: date,
) -> tuple[Fynd, ...]:
    utkast = [
        *_tackning(regelbas, urval, profil, dokument),
        *_preliminar(bedomning),
        *_verifiera(dokument),
        *_sparbarhet(regelbas, dokument),
        *_b04(regelbas, bedomning, dokument),
        *_b12(regelbas, dokument),
        *_b16(regelbas, historik),
    ]
    return tuple(
        Fynd(id=f"F-{granskningsdatum.isoformat()}-{nummer:03d}", **falt)
        for nummer, falt in enumerate(utkast, start=1)
    )


def _tackning(regelbas: Regelbas, urval: Urval, profil: Profil, dokument: Dokument) -> list[dict[str, Any]]:
    finns = [avsnitt.id for avsnitt in dokument.avsnitt]
    varden = profil.faltvarden()
    return [
        {
            "typ": "tackning",
            "regel": valt.krav.id,
            "allvar": "blockerande",
            "grund": valt.krav.grund,
            "avsnitt": avsnitt,
            "beskrivning": f"Kravet {valt.krav.id} ({valt.krav.lagrum}) ska uppfyllas i avsnitt {avsnitt}, "
            "men avsnittet saknas.",
            "atgard": "Skapa avsnittet. Är det ett riskavsnitt, kör 'riskanalys skriv' och sedan 'riskanalys granska'.",
        }
        for valt in urval.krav
        if kravet_galler(regelbas, valt.krav, varden)
        for avsnitt in valt.krav.uppfylls_i
        if not any(befintligt == avsnitt or befintligt.startswith(avsnitt + ".") for befintligt in finns)
    ]


def _preliminar(bedomning: Bedomning) -> list[dict[str, Any]]:
    if bedomning.status != "preliminär":
        return []
    okanda = sorted({falt_id for tjanst in bedomning.tjanster for falt_id in tjanst.okanda_uppgifter})
    return [
        {
            "typ": "tackning",
            "allvar": "hög",
            "grund": "ska_krav",
            "beskrivning": f"Bedömningen är preliminär. Okända uppgifter: {', '.join(okanda)}.",
            "atgard": "Bekräfta uppgifterna med 'riskanalys bekrafta' och kör 'riskanalys bedom' igen.",
        }
    ]


def _verifiera(dokument: Dokument) -> list[dict[str, Any]]:
    return [
        {
            "typ": "sparbarhet",
            "allvar": "hög",
            "grund": "ska_krav",
            "avsnitt": avsnitt.id,
            "beskrivning": f"Avsnitt {avsnitt.id} innehåller {VERIFIERA}.",
            "atgard": "Bekräfta de uppgifter som saknas och kör om bedömning, skrivning och granskning.",
        }
        for avsnitt in dokument.avsnitt
        if any(VERIFIERA in stycke.text for stycke in avsnitt.stycken)
    ]


def _sparbarhet(regelbas: Regelbas, dokument: Dokument) -> list[dict[str, Any]]:
    kanda = regelbas.alla_id()
    return [
        {
            "typ": "sparbarhet",
            "allvar": "blockerande",
            "grund": "metodval",
            "avsnitt": avsnitt.id,
            "beskrivning": f"Avsnitt {avsnitt.id} hänvisar till {ref}, som inte finns i regelbasen.",
            "atgard": "Ta bort hänvisningen eller rätta regelbasen.",
        }
        for avsnitt in dokument.avsnitt
        for ref in sorted({ref for stycke in avsnitt.stycken for ref in stycke.referenser} - kanda)
    ]


def _bristmonster(regelbas: Regelbas, monster_id: str, avsnitt: str, beskrivning: str, atgard: str) -> dict[str, Any]:
    post = regelbas.bristmonster.get(monster_id)
    if post is None:
        raise RiskanalysFel(f"Bristmönstret {monster_id} saknas i regelbasen.")
    return {
        "typ": "bristmonster",
        "regel": monster_id,
        "allvar": post.allvar,
        "grund": post.grund,
        "avsnitt": avsnitt,
        "beskrivning": beskrivning,
        "atgard": atgard,
    }


def _b04(regelbas: Regelbas, bedomning: Bedomning, dokument: Dokument) -> list[dict[str, Any]]:
    finns = {avsnitt.id for avsnitt in dokument.avsnitt}
    return [
        _bristmonster(
            regelbas,
            "B-04",
            avsnitt_id,
            f"{regelbas.tjanster[tjanst.tjanst].namn} saknar eget riskavsnitt ({avsnitt_id}).",
            "Kör 'riskanalys skriv' så att varje tjänst får ett eget avsnitt.",
        )
        for avsnitt_id, tjanst in tjanster_med_avsnitt(bedomning)
        if avsnitt_id not in finns
    ]


def _b12(regelbas: Regelbas, dokument: Dokument) -> list[dict[str, Any]]:
    return [
        _bristmonster(
            regelbas,
            "B-12",
            avsnitt.id,
            f"Avsnitt {avsnitt.id} saknar en motivering som hänvisar till hot och sårbarheter.",
            "Skriv om avsnittet med 'riskanalys skriv'.",
        )
        for avsnitt in dokument.avsnitt
        if avsnitt.id.startswith(RISKAVSNITT)
        and not any(
            stycke.typ == "motivering" and motivering_har_hot_och_sarbarhet(stycke) for stycke in avsnitt.stycken
        )
    ]


def _b16(regelbas: Regelbas, historik: Historik) -> list[dict[str, Any]]:
    if historik.nasta_genomgang() is not None:
        return []
    return [
        _bristmonster(
            regelbas,
            "B-16",
            "D-ARB.10",
            "Datum för utvärdering och uppdatering saknas.",
            "Registrera utvärderingen med 'riskanalys utvardera'.",
        )
    ]
```

- [ ] **Step 8: Skriv `src/riskanalys/granskning/korning.py`**

```python
"""Granskningskörning: bygger dokumentet, granskar det och sparar resultatet med manifest."""

from datetime import date
from pathlib import Path

from pydantic import TypeAdapter

from riskanalys.bedomning.korning import BEDOMNINGAR, kontrollera_aktuell, las_bedomning, las_bedomningsprofil
from riskanalys.dokument.arb import bygg_arb
from riskanalys.dokument.modeller import AvsnittsUtkast, Dokument
from riskanalys.dokument.skrivning import UTKAST, las_skrivresultat
from riskanalys.drift.historik import historikens_kontrollsumma, las_historik
from riskanalys.fel import RiskanalysFel
from riskanalys.granskning.kontroller import granska
from riskanalys.granskning.modeller import Fynd
from riskanalys.lagring.korningar import avslutade_korningar, ny_korningsmapp, senaste_korning
from riskanalys.lagring.manifest import las_manifest, skriv_manifest, verifiera_manifest
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.urval import valj

GRANSKNING = "granskning"
DOKUMENTFIL = "dokument.json"
FYNDFIL = "fynd.json"
_FYNDLISTA = TypeAdapter(tuple[Fynd, ...])


def godkanda_utkast(byramapp: Path, bedomningsmapp: Path) -> tuple[dict[str, AvsnittsUtkast], Path | None]:
    """Godkända AI-utkast från den senaste skrivningen som hör till just den här bedömningen."""
    horande = [
        mapp
        for mapp in avslutade_korningar(byramapp, UTKAST)
        if las_manifest(mapp).metadata.get("bedomning") == bedomningsmapp.name
    ]
    if not horande:
        return {}, None
    mapp = horande[-1]
    utkast = {
        post.underlag.avsnitt: post.godkant_utkast
        for post in las_skrivresultat(mapp)
        if post.godkant_utkast is not None
    }
    return utkast, mapp


def kor_granskning(byramapp: Path, regelbas: Regelbas, granskningsdatum: date) -> Path:
    bedomningsmapp = senaste_korning(byramapp, BEDOMNINGAR, f"bedom {byramapp.name}")
    kontrollera_aktuell(byramapp, bedomningsmapp, regelbas)
    bedomning = las_bedomning(bedomningsmapp)
    profil = las_bedomningsprofil(bedomningsmapp)
    urval = valj(regelbas, bedomning.regelpaket, bedomning.datum, bedomning.lan)
    utkast, utkastmapp = godkanda_utkast(byramapp, bedomningsmapp)
    historik = las_historik(byramapp)
    dokument = bygg_arb(regelbas, profil, bedomning, utkast, historik)
    fynd = granska(regelbas, urval, profil, bedomning, dokument, historik, granskningsdatum)
    mapp = ny_korningsmapp(byramapp, GRANSKNING)
    (mapp / DOKUMENTFIL).write_text(dokument.model_dump_json(indent=2), encoding="utf-8")
    (mapp / FYNDFIL).write_text(_FYNDLISTA.dump_json(fynd, indent=2).decode("utf-8"), encoding="utf-8")
    metadata = {
        "typ": "granskning",
        "bedomning": bedomningsmapp.name,
        "utkast": utkastmapp.name if utkastmapp else "",
        "historik": historikens_kontrollsumma(byramapp),
        "blockerande": str(sum(1 for post in fynd if post.allvar == "blockerande")),
        "datum": granskningsdatum.isoformat(),
    }
    skriv_manifest(mapp, metadata)
    return mapp


def las_granskning(mapp: Path) -> tuple[Dokument, tuple[Fynd, ...]]:
    dokument = Dokument.model_validate_json((mapp / DOKUMENTFIL).read_text(encoding="utf-8"))
    fynd = _FYNDLISTA.validate_json((mapp / FYNDFIL).read_text(encoding="utf-8"))
    return dokument, fynd


def granskningens_profil(byramapp: Path, granskningsmapp: Path) -> Profil:
    """Profilkopian i den bedömning som granskningen bygger på. Den gäller för sakgranskning, export och fastställelse."""
    return las_bedomningsprofil(byramapp / BEDOMNINGAR / las_manifest(granskningsmapp).metadata["bedomning"])


def andrade_kallor(byramapp: Path, granskningsmapp: Path) -> list[str]:
    """Filer som ändrats efter körningen i granskningen, i bedömningen den bygger på och i AI-utkasten den använde."""
    granskning = [f"Granskningen är ändrad efter körningen. {rad}" for rad in verifiera_manifest(granskningsmapp)]
    if granskning:
        return granskning
    metadata = las_manifest(granskningsmapp).metadata
    bedomning = [
        f"Bedömningen är ändrad efter körningen. {rad}"
        for rad in verifiera_manifest(byramapp / BEDOMNINGAR / metadata["bedomning"])
    ]
    utkast = [
        f"AI-utkasten är ändrade efter skrivningen. {rad}"
        for rad in (verifiera_manifest(byramapp / UTKAST / metadata["utkast"]) if metadata["utkast"] else [])
    ]
    return [*bedomning, *utkast]


def kontrollera_kallor(byramapp: Path, granskningsmapp: Path) -> None:
    """Stoppar med ett svenskt meddelande om granskningen eller något den bygger på har ändrats."""
    hinder = andrade_kallor(byramapp, granskningsmapp)
    if hinder:
        raise RiskanalysFel(" ".join(hinder) + " Kör om kedjan från 'riskanalys bedom'.")
```

- [ ] **Step 9: Skriv `src/riskanalys/kommandon/granska_kommando.py`**

```python
"""riskanalys granska"""

import argparse
from datetime import date
from typing import Any

from riskanalys.granskning.korning import kor_granskning, las_granskning
from riskanalys.kommandon import datumargument, ladda_giltig_regelbas, regelbasargument
from riskanalys.lagring.datamapp import befintlig_byramapp


def lagg_till(underparsers: Any) -> None:
    parser = underparsers.add_parser("granska", help="Bygg dokumentet och granska det maskinellt.")
    parser.add_argument("byra")
    parser.add_argument("--datum", type=datumargument, default=None, help="Granskningsdatum. Standard är i dag.")
    regelbasargument(parser)
    parser.set_defaults(kor=kor_granska)


def kor_granska(args: argparse.Namespace) -> int:
    byramapp = befintlig_byramapp(args.byra)
    regelbas = ladda_giltig_regelbas(args.regelbas)
    mapp = kor_granskning(byramapp, regelbas, args.datum or date.today())
    dokument, fynd = las_granskning(mapp)
    print(f"Dokumentet har {len(dokument.avsnitt)} avsnitt. Fynd: {len(fynd)}.")
    for post in fynd:
        print(f"{post.id} [{post.allvar}] {post.beskrivning} Åtgärd: {post.atgard}")
    print(f"Sparad i {mapp}.")
    if any(post.allvar == "blockerande" for post in fynd):
        print("Det finns blockerande fynd. Åtgärda dem innan dokumentet kan fastställas.")
        return 2
    print(f"Nästa steg: 'riskanalys exportera {args.byra} --utkast' och 'riskanalys sakgranska {args.byra}'.")
    return 0
```

- [ ] **Step 10: Registrera kommandot i `src/riskanalys/cli.py`**

Lägg till `granska_kommando` i importen från `riskanalys.kommandon` och sist i `KOMMANDON`:

```python
from riskanalys.kommandon import (
    bedom_kommando,
    drift_kommando,
    granska_kommando,
    profil_kommando,
    regelbas_kommando,
    skriv_kommando,
)

KOMMANDON = [regelbas_kommando, profil_kommando, drift_kommando, bedom_kommando, skriv_kommando, granska_kommando]
```

- [ ] **Step 11: Kör testerna**

Run: `.venv/bin/pytest tester/regelkontrakt/test_granskning.py tester/enhet/test_granskning_korning.py -v`
Expected: alla tester passerar.

- [ ] **Step 12: Commit**

```bash
git add src/riskanalys/granskning src/riskanalys/kommandon/granska_kommando.py src/riskanalys/cli.py tester/conftest.py tester/regelkontrakt/test_granskning.py tester/enhet/test_granskning_korning.py
git commit -m "feat: maskinell granskning med täckning, spårbarhet och bristmönster"
```

---

### Task 19: Word-export och kommandot `exportera --utkast`

**Files:**
- Create: `src/riskanalys/dokument/rendering.py`
- Create: `src/riskanalys/dokument/export.py`
- Create: `src/riskanalys/kommandon/exportera_kommando.py`
- Modify: `src/riskanalys/cli.py`
- Test: `tester/enhet/test_rendering.py`, `tester/enhet/test_exportera_kommando.py`

**Interfaces:**
- Consumes: `Dokument`, `Oklarhet`, `Fynd`, `Profil`, `GRANSKNING`, `las_granskning`, `kontrollera_kallor`, `BEDOMNINGAR`, `las_bedomningsprofil`, `UTKAST`, `las_skrivresultat`, `senaste_korning`, `ny_korningsmapp`, `skriv_manifest`, `las_manifest`, `datumargument`, `befintlig_byramapp`, `RiskanalysFel`, python-docx.
- Produces:
  - `dokument/rendering.py`: `ROLLER = {"FfR": "P-ROLL.ffr_namn"}`, `UTKASTMARKERING = "UTKAST – ej fastställt av byrån"`, `BILAGERUBRIK = "Bilaga: Åtgärdslista"`, `ersatt_platshallare(text: str, profil: Profil) -> str`, `renderat_avsnitt(avsnitt: Avsnitt, profil: Profil) -> Avsnitt`, `avsnittsnummer(avsnitt_id: str) -> str`, `utkaststatus(datum: date) -> str`, `faststalld_status(organ: str, datum: date, version: int) -> str`, `atgardslista(fynd: Iterable[Fynd], oklarheter: Iterable[tuple[str, Oklarhet]]) -> tuple[str, ...]`, `rendera_docx(dokument: Dokument, profil: Profil, statusrad: str, sokvag: Path, bilaga: tuple[str, ...] = ()) -> Path`.
  - `dokument/export.py`: `EXPORT = "export"`, `UTKASTFIL = "allman-riskbedomning-UTKAST.docx"`, `utkastens_oklarheter(byramapp: Path, utkastnamn: str) -> tuple[tuple[str, Oklarhet], ...]`, `kor_export_utkast(byramapp: Path, datum: date) -> Path`.
  - Kommandot `exportera <byra> --utkast [--datum D]`. Utan `--utkast` ges felet "En fastställd version skapas med 'riskanalys faststall'. Använd --utkast för ett utkast."
  - Manifestets metadata för export: `typ = "export_utkast"`, `granskning` (granskningsmappens namn), `datum`.

Exporten bygger på den senaste granskningen: dokumentet och fynden ur granskningsmappen, profilen ur den bedömning som granskningen hör till och AI:ns oklarheter ur de utkast som granskningen använde. Innan något läses kontrolleras alla tre mot sina manifest med `kontrollera_kallor` (Task 18). Export som utkast är alltid tillåten (spec 10). Varje sida får statusraden "UTKAST – ej fastställt av byrån. Skapat ÅÅÅÅ-MM-DD." i sidhuvudet, och åtgärdslistan med öppna fynd och oklarheter bifogas sist.

Personnamn sätts in först här. Texten innehåller `{roll:FfR}`, som byts mot det bekräftade namnet ur profilen. Saknas namnet blir det `[VERIFIERA: FfR]`. `renderat_avsnitt` är den enda platsen där det sker. Exporten använder den, och sakgranskningen (Task 20) räknar sin kontrollsumma på den, så att ett godkännande gäller exakt den text som skrivs ut. Namnen hålls fortfarande utanför AI-underlaget, eftersom AI bara ser mallen med `{roll:FfR}`. Word-filen hamnar i byråns datamapp och lämnar aldrig datorn genom programmet.

Exporten görs till Word med python-docx. PDF skjuts till etapp M4 (beslut i `docs/STATUS.md`, Task 22).

- [ ] **Step 1: Skriv det felande testet `tester/enhet/test_rendering.py`**

```python
from datetime import date

import docx

from riskanalys.bedomning.motor import bedom
from riskanalys.dokument.arb import bygg_arb
from riskanalys.dokument.modeller import Oklarhet
from riskanalys.dokument.rendering import (
    BILAGERUBRIK,
    atgardslista,
    avsnittsnummer,
    ersatt_platshallare,
    faststalld_status,
    renderat_avsnitt,
    rendera_docx,
    utkaststatus,
)
from riskanalys.drift.historik import Handelse, Historik
from riskanalys.granskning.modeller import Fynd
from riskanalys.regelverk.urval import valj

HISTORIK = Historik().med(Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Första."))
FYND = Fynd(
    id="F-2026-11-02-001",
    typ="bristmonster",
    regel="B-04",
    allvar="hög",
    grund="tillsynspraxis",
    beskrivning="Löpande bokföring saknar eget riskavsnitt.",
    atgard="Kör 'riskanalys skriv'.",
)


def _dokument(regelbas, profil, utkast):
    bedomning = bedom(regelbas, valj(regelbas, "RP-RED-VG", date(2026, 11, 1), "Västra Götaland"), profil)
    return bygg_arb(regelbas, profil, bedomning, utkast, HISTORIK)


def test_rollen_ersatts_med_bekraftat_namn(regelbas, profil_fabrik, real_varden):
    profil = profil_fabrik(regelbas, real_varden)
    assert ersatt_platshallare("Utövas av {roll:FfR}.", profil) == "Utövas av Testa Testsson."


def test_roll_utan_bekraftat_namn_markeras(regelbas, profil_fabrik, real_varden):
    profil = profil_fabrik(regelbas, real_varden, okanda=("P-ROLL.ffr_namn",))
    assert ersatt_platshallare("Utövas av {roll:FfR}.", profil) == "Utövas av [VERIFIERA: FfR]."
    assert ersatt_platshallare("{roll:Okand}", profil) == "[VERIFIERA: Okand]"


def test_renderat_avsnitt_byter_namn_och_andrar_kontrollsumman(regelbas, profil_fabrik, real_varden):
    profil = profil_fabrik(regelbas, real_varden)
    mall = _dokument(regelbas, profil, {}).avsnitt_med_id()["D-ARB.1"]
    renderat = renderat_avsnitt(mall, profil)
    assert any("Testa Testsson" in stycke.text for stycke in renderat.stycken)
    assert not any("{roll:" in stycke.text for stycke in renderat.stycken)
    ny_ansvarig = profil_fabrik(regelbas, {**real_varden, "P-ROLL.ffr_namn": "Ny Person"})
    assert renderat_avsnitt(mall, ny_ansvarig).kontrollsumma() != renderat.kontrollsumma()


def test_avsnittsnummer():
    assert avsnittsnummer("D-ARB.6.1") == "6.1"
    assert avsnittsnummer("D-ARB.10") == "10"


def test_statusrader():
    assert utkaststatus(date(2026, 11, 2)) == "UTKAST – ej fastställt av byrån. Skapat 2026-11-02."
    assert faststalld_status("styrelsen", date(2026, 11, 15), 1) == "Fastställt av styrelsen 2026-11-15. Version 1."


def test_atgardslistan_tar_med_oppna_fynd_och_oklarheter():
    atgardat = FYND.model_copy(update={"id": "F-2026-11-02-002", "status": "åtgärdad"})
    oklarhet = Oklarhet(fraga="Har byrån bankkoppling för alla kunder?", saknad_uppgift="P-KANAL.bankdata_andel")
    assert atgardslista([FYND, atgardat], [("D-ARB.6.1", oklarhet)]) == (
        "F-2026-11-02-001 (hög): Löpande bokföring saknar eget riskavsnitt. Åtgärd: Kör 'riskanalys skriv'.",
        "D-ARB.6.1: Har byrån bankkoppling för alla kunder? Uppgift som saknas: P-KANAL.bankdata_andel.",
    )


def test_word_filen_har_statusrad_rubriker_namn_och_bilaga(tmp_path, regelbas, profil_fabrik, real_varden, giltigt_utkast):
    profil = profil_fabrik(regelbas, real_varden)
    statusrad = utkaststatus(date(2026, 11, 2))
    sokvag = rendera_docx(
        _dokument(regelbas, profil, {"D-ARB.6.1": giltigt_utkast}), profil, statusrad, tmp_path / "ut" / "a.docx", ("Rad.",)
    )
    word = docx.Document(str(sokvag))
    assert all(sektion.header.paragraphs[0].text == statusrad for sektion in word.sections)
    texter = [stycke.text for stycke in word.paragraphs]
    assert texter[:2] == ["Allmän riskbedömning", statusrad]
    assert "6.1 Risk i löpande bokföring" in texter
    assert "10 Utvärdering och uppdatering" in texter
    assert any("Testa Testsson" in text for text in texter)
    assert not any("{roll:" in text for text in texter)
    assert texter[-2:] == [BILAGERUBRIK, "Rad."]


def test_utan_bilaga_finns_ingen_atgardslista(tmp_path, regelbas, profil_fabrik, real_varden):
    profil = profil_fabrik(regelbas, real_varden)
    sokvag = rendera_docx(_dokument(regelbas, profil, {}), profil, "Status.", tmp_path / "b.docx")
    assert BILAGERUBRIK not in [stycke.text for stycke in docx.Document(str(sokvag)).paragraphs]
```

- [ ] **Step 2: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/enhet/test_rendering.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.dokument.rendering'`.

- [ ] **Step 3: Skriv `src/riskanalys/dokument/rendering.py`**

```python
"""Word-export (spec 10 och 11). Personnamn sätts in först här och skickas aldrig till AI."""

import re
from collections.abc import Iterable
from datetime import date
from pathlib import Path

import docx

from riskanalys.dokument.modeller import Avsnitt, Dokument, Oklarhet
from riskanalys.granskning.modeller import Fynd
from riskanalys.profil.modeller import Profil

ROLLER = {"FfR": "P-ROLL.ffr_namn"}
UTKASTMARKERING = "UTKAST – ej fastställt av byrån"
BILAGERUBRIK = "Bilaga: Åtgärdslista"
_PLATSHALLARE = re.compile(r"\{roll:(\w+)\}")


def ersatt_platshallare(text: str, profil: Profil) -> str:
    """Byter {roll:X} mot det bekräftade namnet, eller mot [VERIFIERA: X] om namnet saknas."""

    def ersatt(traff: re.Match[str]) -> str:
        roll = traff.group(1)
        falt_id = ROLLER.get(roll)
        if falt_id is None or not profil.ar_bekraftad(falt_id):
            return f"[VERIFIERA: {roll}]"
        return str(profil.uppgifter[falt_id].varde)

    return _PLATSHALLARE.sub(ersatt, text)


def avsnittsnummer(avsnitt_id: str) -> str:
    """D-ARB.6.1 blir 6.1."""
    return avsnitt_id.split(".", 1)[1]


def renderat_avsnitt(avsnitt: Avsnitt, profil: Profil) -> Avsnitt:
    """Avsnittet som granskaren ser och exporten innehåller: platshållarna utbytta mot namn eller [VERIFIERA: roll]."""
    stycken = tuple(
        stycke.model_copy(update={"text": ersatt_platshallare(stycke.text, profil)}) for stycke in avsnitt.stycken
    )
    return avsnitt.model_copy(update={"stycken": stycken})


def utkaststatus(datum: date) -> str:
    return f"{UTKASTMARKERING}. Skapat {datum.isoformat()}."


def faststalld_status(organ: str, datum: date, version: int) -> str:
    """Statusraden för en fastställd version. Den påstår aldrig att regelverket är uppfyllt (spec 10)."""
    return f"Fastställt av {organ} {datum.isoformat()}. Version {version}."


def atgardslista(fynd: Iterable[Fynd], oklarheter: Iterable[tuple[str, Oklarhet]]) -> tuple[str, ...]:
    """Öppna fynd och AI:ns oklarheter, en rad var (spec 11)."""
    fyndrader = [
        f"{post.id} ({post.allvar}): {post.beskrivning} Åtgärd: {post.atgard}" for post in fynd if post.status == "öppen"
    ]
    oklarhetsrader = [
        f"{avsnitt}: {oklarhet.fraga} Uppgift som saknas: {oklarhet.saknad_uppgift}." for avsnitt, oklarhet in oklarheter
    ]
    return (*fyndrader, *oklarhetsrader)


def rendera_docx(
    dokument: Dokument, profil: Profil, statusrad: str, sokvag: Path, bilaga: tuple[str, ...] = ()
) -> Path:
    """Skriver dokumentet som Word-fil med statusraden i sidhuvudet, så att den syns på varje sida."""
    word = docx.Document()
    for sektion in word.sections:
        sektion.header.paragraphs[0].text = statusrad
    word.add_heading(dokument.titel, level=0)
    word.add_paragraph().add_run(statusrad).bold = True
    for avsnitt in (renderat_avsnitt(post, profil) for post in dokument.avsnitt):
        word.add_heading(f"{avsnittsnummer(avsnitt.id)} {avsnitt.rubrik}", level=1)
        for stycke in avsnitt.stycken:
            word.add_paragraph(stycke.text)
    if bilaga:
        word.add_heading(BILAGERUBRIK, level=1)
        for rad in bilaga:
            word.add_paragraph(rad, style="List Bullet")
    sokvag.parent.mkdir(parents=True, exist_ok=True)
    word.save(str(sokvag))
    return sokvag
```

- [ ] **Step 4: Kör testet**

Run: `.venv/bin/pytest tester/enhet/test_rendering.py -v`
Expected: alla tester passerar.

- [ ] **Step 5: Skriv det felande testet `tester/enhet/test_exportera_kommando.py`**

```python
from datetime import date

import docx

from riskanalys.bedomning.korning import BEDOMNINGAR, kor_bedomning
from riskanalys.cli import main
from riskanalys.dokument.export import EXPORT, UTKASTFIL, kor_export_utkast
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.modeller import Oklarhet
from riskanalys.dokument.rendering import BILAGERUBRIK
from riskanalys.dokument.skrivning import UTKAST, kor_skrivning
from riskanalys.granskning.korning import kor_granskning
from riskanalys.lagring.korningar import avslutade_korningar
from riskanalys.lagring.manifest import las_manifest, verifiera_manifest


def _texter(mapp):
    return [stycke.text for stycke in docx.Document(str(mapp / UTKASTFIL)).paragraphs]


def test_export_utan_utkastflagga_vagras(skriven_byra, capsys):
    assert main(["exportera", "testbyra"]) == 1
    assert "Använd --utkast för ett utkast." in capsys.readouterr().err


def test_export_fore_granskning_sager_vilket_steg_som_saknas(skriven_byra, capsys):
    assert main(["exportera", "testbyra", "--utkast"]) == 1
    assert "Kör 'riskanalys granska testbyra' först" in capsys.readouterr().err


def test_export_av_utkast(skriven_byra, regelbas, capsys):
    kor_granskning(skriven_byra, regelbas, date(2026, 11, 2))
    assert main(["exportera", "testbyra", "--utkast", "--datum", "2026-11-02"]) == 0
    (mapp,) = avslutade_korningar(skriven_byra, EXPORT)
    assert verifiera_manifest(mapp) == []
    assert las_manifest(mapp).metadata["typ"] == "export_utkast"
    word = docx.Document(str(mapp / UTKASTFIL))
    assert word.sections[0].header.paragraphs[0].text == "UTKAST – ej fastställt av byrån. Skapat 2026-11-02."
    assert BILAGERUBRIK not in _texter(mapp)
    assert UTKASTFIL in capsys.readouterr().out


def test_exporten_tar_med_fynd_och_oklarheter(byra_med_profil, regelbas, giltigt_utkast):
    oklarhet = Oklarhet(fraga="Har byrån bankkoppling för alla kunder?", saknad_uppgift="P-KANAL.bankdata_andel")
    utkast = giltigt_utkast.model_copy(update={"oklarheter": [oklarhet]})
    kor_bedomning(byra_med_profil, regelbas)
    kor_skrivning(byra_med_profil, regelbas, Testleverantor([utkast]))
    kor_granskning(byra_med_profil, regelbas, date(2026, 11, 2))
    texter = _texter(kor_export_utkast(byra_med_profil, date(2026, 11, 2)))
    bilaga = texter[texter.index(BILAGERUBRIK) + 1 :]
    assert any("Datum för utvärdering och uppdatering saknas." in rad for rad in bilaga)
    assert "D-ARB.6.1: Har byrån bankkoppling för alla kunder? Uppgift som saknas: P-KANAL.bankdata_andel." in bilaga


def _andra(fil, gammalt, nytt):
    fil.write_text(fil.read_text(encoding="utf-8").replace(gammalt, nytt), encoding="utf-8")


def test_manipulerad_granskning_exporteras_inte(skriven_byra, regelbas, capsys):
    mapp = kor_granskning(skriven_byra, regelbas, date(2026, 11, 2))
    _andra(mapp / "dokument.json", "Testbyrån AB", "Annan byrå AB")
    assert main(["exportera", "testbyra", "--utkast"]) == 1
    assert "Granskningen är ändrad efter körningen. Fil ändrad: dokument.json" in capsys.readouterr().err


def test_manipulerad_profilkopia_exporteras_inte(skriven_byra, regelbas, capsys):
    mapp = kor_granskning(skriven_byra, regelbas, date(2026, 11, 2))
    bedomningsmapp = skriven_byra / BEDOMNINGAR / las_manifest(mapp).metadata["bedomning"]
    _andra(bedomningsmapp / "profil.yaml", "Testa Testsson", "Någon Annan")
    assert main(["exportera", "testbyra", "--utkast"]) == 1
    assert "Bedömningen är ändrad efter körningen. Fil ändrad: profil.yaml" in capsys.readouterr().err
    assert avslutade_korningar(skriven_byra, EXPORT) == []


def test_manipulerade_oklarheter_exporteras_inte(skriven_byra, regelbas, capsys):
    mapp = kor_granskning(skriven_byra, regelbas, date(2026, 11, 2))
    utkastfil = skriven_byra / UTKAST / las_manifest(mapp).metadata["utkast"] / "D-ARB.6.1.json"
    _andra(utkastfil, '"oklarheter": []', '"oklarheter": [{"fraga": "Påhittad?", "saknad_uppgift": "P-X"}]')
    assert main(["exportera", "testbyra", "--utkast"]) == 1
    assert "AI-utkasten är ändrade efter skrivningen. Fil ändrad: D-ARB.6.1.json" in capsys.readouterr().err
```

- [ ] **Step 6: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/enhet/test_exportera_kommando.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.dokument.export'`.

- [ ] **Step 7: Skriv `src/riskanalys/dokument/export.py`**

```python
"""Export av ett utkast till Word utifrån den senaste granskningen (spec 10)."""

from datetime import date
from pathlib import Path

from riskanalys.dokument.modeller import Oklarhet
from riskanalys.dokument.rendering import atgardslista, rendera_docx, utkaststatus
from riskanalys.dokument.skrivning import UTKAST, las_skrivresultat
from riskanalys.granskning.korning import GRANSKNING, granskningens_profil, kontrollera_kallor, las_granskning
from riskanalys.lagring.korningar import ny_korningsmapp, senaste_korning
from riskanalys.lagring.manifest import las_manifest, skriv_manifest

EXPORT = "export"
UTKASTFIL = "allman-riskbedomning-UTKAST.docx"


def utkastens_oklarheter(byramapp: Path, utkastnamn: str) -> tuple[tuple[str, Oklarhet], ...]:
    """Oklarheterna i de godkända AI-utkast som granskningen använde."""
    if not utkastnamn:
        return ()
    return tuple(
        (post.underlag.avsnitt, oklarhet)
        for post in las_skrivresultat(byramapp / UTKAST / utkastnamn)
        if post.godkant_utkast is not None
        for oklarhet in post.godkant_utkast.oklarheter
    )


def kor_export_utkast(byramapp: Path, datum: date) -> Path:
    """Exporterar den senaste granskningens dokument som ett märkt utkast med åtgärdslista.

    Granskningen, bedömningen (profilkopian) och AI-utkasten (oklarheterna) kontrolleras mot sina manifest
    innan något läses, så att ändrade filer aldrig hamnar i exporten.
    """
    granskningsmapp = senaste_korning(byramapp, GRANSKNING, f"granska {byramapp.name}")
    kontrollera_kallor(byramapp, granskningsmapp)
    metadata = las_manifest(granskningsmapp).metadata
    profil = granskningens_profil(byramapp, granskningsmapp)
    dokument, fynd = las_granskning(granskningsmapp)
    bilaga = atgardslista(fynd, utkastens_oklarheter(byramapp, metadata["utkast"]))
    mapp = ny_korningsmapp(byramapp, EXPORT)
    rendera_docx(dokument, profil, utkaststatus(datum), mapp / UTKASTFIL, bilaga)
    skriv_manifest(mapp, {"typ": "export_utkast", "granskning": granskningsmapp.name, "datum": datum.isoformat()})
    return mapp
```

- [ ] **Step 8: Skriv `src/riskanalys/kommandon/exportera_kommando.py`**

```python
"""riskanalys exportera"""

import argparse
from datetime import date
from typing import Any

from riskanalys.dokument.export import UTKASTFIL, kor_export_utkast
from riskanalys.fel import RiskanalysFel
from riskanalys.kommandon import datumargument
from riskanalys.lagring.datamapp import befintlig_byramapp


def lagg_till(underparsers: Any) -> None:
    parser = underparsers.add_parser("exportera", help="Skapa ett Word-dokument av den senaste granskningen.")
    parser.add_argument("byra")
    parser.add_argument("--utkast", action="store_true", help="Exportera som utkast med åtgärdslista.")
    parser.add_argument("--datum", type=datumargument, default=None, help="Datum i statusraden. Standard är i dag.")
    parser.set_defaults(kor=kor_exportera)


def kor_exportera(args: argparse.Namespace) -> int:
    if not args.utkast:
        raise RiskanalysFel("En fastställd version skapas med 'riskanalys faststall'. Använd --utkast för ett utkast.")
    mapp = kor_export_utkast(befintlig_byramapp(args.byra), args.datum or date.today())
    print(f"Utkastet är sparat i {mapp / UTKASTFIL}.")
    print("Varje sida är märkt UTKAST. Öppna fynd och oklarheter står i åtgärdslistan sist i dokumentet.")
    print(f"Nästa steg: sakgranska avsnitten med 'riskanalys sakgranska {args.byra}'.")
    return 0
```

- [ ] **Step 9: Registrera kommandot i `src/riskanalys/cli.py`**

Lägg till `exportera_kommando` i importen från `riskanalys.kommandon` och sist i `KOMMANDON`:

```python
from riskanalys.kommandon import (
    bedom_kommando,
    drift_kommando,
    exportera_kommando,
    granska_kommando,
    profil_kommando,
    regelbas_kommando,
    skriv_kommando,
)

KOMMANDON = [
    regelbas_kommando,
    profil_kommando,
    drift_kommando,
    bedom_kommando,
    skriv_kommando,
    granska_kommando,
    exportera_kommando,
]
```

- [ ] **Step 10: Kör testerna**

Run: `.venv/bin/pytest tester/enhet/test_rendering.py tester/enhet/test_exportera_kommando.py -v`
Expected: alla tester passerar.

- [ ] **Step 11: Commit**

```bash
git add src/riskanalys/dokument/rendering.py src/riskanalys/dokument/export.py src/riskanalys/kommandon/exportera_kommando.py src/riskanalys/cli.py tester/enhet/test_rendering.py tester/enhet/test_exportera_kommando.py
git commit -m "feat: Word-export av utkast med statusrad och åtgärdslista"
```

---

### Task 20: Sakgranskning, grindar och kommandot `sakgranska`

**Files:**
- Create: `src/riskanalys/faststallelse/__init__.py`, `modeller.py`, `sakgranskning.py`, `grindar.py`
- Create: `src/riskanalys/kommandon/sakgranska_kommando.py`
- Modify: `src/riskanalys/cli.py`
- Modify: `tester/conftest.py` (fixturerna `signerad_regelbas_rot` och `signerad_regelbas`)
- Test: `tester/enhet/test_sakgranskning.py`, `tester/regelkontrakt/test_grindar.py`, `tester/enhet/test_sakgranska_kommando.py`

**Interfaces:**
- Consumes: `Dokument`, `Avsnitt`, `Fynd`, `Bedomning`, `Historik`, `Profil`, `Regelbas`, `Urval`, `kravet_galler`, `saknade_kritiska`, `VERIFIERA`, `las_yaml`, `spara_yaml`, `GRANSKNING`, `las_granskning`, `BEDOMNINGAR`, `las_bedomningsprofil`, `senaste_korning`, `las_manifest`, `ersatt_platshallare`, `datumargument`, `befintlig_byramapp`, `RiskanalysFel`.
- Produces:
  - `faststallelse/modeller.py`: `Sakgranskning(avsnitt, kontrollsumma, godkand: bool, roll, namn, datum: date, kommentar: str | None = None)`, `Beslut(organ, datum: date, namn, roll)`.
  - `faststallelse/sakgranskning.py`: `SAKGRANSKNINGSFIL = Path("sakgranskning") / "sakgranskningar.yaml"`, `SakgranskningsFel(RiskanalysFel)`, `las_sakgranskningar(byramapp) -> tuple[Sakgranskning, ...]`, `spara_sakgranskningar(byramapp, sakgranskningar) -> None`, `granskad_summa(avsnitt: Avsnitt, profil: Profil) -> str`, `registrera_sakgranskning(sakgranskningar, dokument, profil, avsnitt_id, godkand, roll, namn, datum, kommentar=None) -> tuple[Sakgranskning, ...]`, `galler_sakgranskning(sakgranskningar, avsnitt: Avsnitt, profil: Profil) -> Sakgranskning | None`, `sakgranskningsstatus(sakgranskningar, avsnitt: Avsnitt, profil: Profil) -> str`.
  - `faststallelse/grindar.py`: `ICKE_BINDANDE`, `Faststallelseunderlag(regelbas, urval, profil, bedomning, dokument, fynd, sakgranskningar, historik, granskningsdatum)` där `historik` är versionshistoriken inklusive tidigare fastställelser, `fyndhinder(fynd: Fynd) -> list[str]`, `hinder_for_faststallelse(underlag: Faststallelseunderlag, beslutsdatum: date) -> list[str]`.
  - Kommandot `sakgranska <byra> [--avsnitt ID] [--godkann | --underkann] [--kommentar TEXT] [--namn NAMN] [--roll FfR] [--datum D]`.
  - Fixturer: `signerad_regelbas_rot` (en kopia av repots regelbas där en påhittad sakkunnig har gjort paragrafkartan komplett och verifierat alla krav och kartan med rätt kontrollsummor) och `signerad_regelbas` (den kopian inläst). Paragraferna utanför testfallet markeras som ej tillämpliga i kopian. Det är bara för att testa en fastställelse; repots regelbas visar dem som ohanterade.

En sakgranskning gäller ett avsnitt i en bestämd lydelse. Den sparar kontrollsumman för **det granskaren ser**: avsnittet med namnen insatta av `renderat_avsnitt` (Task 19), samma text som exporten skriver ut. Den gäller bara så länge den texten är oförändrad (spec 10, Review Focus 4). Byts den ansvariga personen i profilen ändras texten, och avsnittet måste sakgranskas igen. Profilen är den som granskningen bygger på (`granskningens_profil`, Task 18). Ändras texten, till exempel efter en ny skrivning, måste avsnittet sakgranskas igen. Sakgranskningarna ligger i en fil per byrå och läggs till i tur och ordning. Den senaste som gäller avsnittets nuvarande kontrollsumma avgör.

Grinden prövar specens villkor för fastställelse (spec 10) och returnerar ett hinder per brist, som en mening som säger vad som saknas:

| Villkor i spec 10 | Hinder när |
|---|---|
| 1. Kritiska uppgifter | någon kritisk uppgift varken är bekräftad eller ej tillämplig |
| 2. Preliminärt och `[VERIFIERA]` | bedömningen är preliminär, eller ett avsnitt innehåller `[VERIFIERA]` |
| 3. Sakkunnig | ett krav som gäller byrån (`galler_om`) inte är verifierat i sin nuvarande lydelse; paragrafkartan inte är verifierad i sin nuvarande lydelse, har paragrafer som regelbasen inte hanterar eller inte gäller bedömningens datum |
| 4. Fynd | se nedan |
| 5. Sakgranskning | ett avsnitt saknar godkänd sakgranskning för sin nuvarande kontrollsumma, eller är underkänt |
| 6. Drift | nästa genomgång saknas, eller har passerat på beslutsdagen |
| Datumordning | beslutsdatum är före granskningen, den senaste gällande sakgranskningen, den senaste utvärderingen eller en tidigare fastställelse |

Datumordningen följer av spec 10: ett organ fattar beslut på ett underlag som redan finns. Ett beslut daterat före granskningen eller sakgranskningen skulle fastställa något som ännu inte var granskat.

Fynd (villkor 4): ett blockerande fynd är alltid ett hinder. Andra fynd är hinder tills de är åtgärdade eller hanterade. Ett fynd om ett ska-krav får bara hanteras av en sakkunnig (`sakkunnigbedömd` med motivering), aldrig accepteras som metodavvikelse av byrån. Ett fynd om ett metodval får accepteras som metodavvikelse med motivering. Ett fynd om ett allmänt råd, tillsynspraxis eller ett EU-utkast får accepteras om motiveringen hänvisar till det bindande krav (`KRV-`) som ändå uppfylls. I M1 finns inget kommando som ändrar ett fynds status (det kommer med `riskanalys avvikelse`), men grinden och dess tester finns redan, så att reglerna är låsta när kommandot byggs.

- [ ] **Step 1: Lägg till fixturerna sist i `tester/conftest.py`**

Lägg till `import shutil` bland importerna överst i filen. Lägg sedan till följande sist i filen:

```python
SAKKUNNIG_TEST = {"status": "verifierad", "av": "Testsakkunnig", "datum": date(2026, 10, 1)}
UTANFOR_TESTFALLET = "Syntetiskt testfall: paragrafen ligger utanför den tunna kedjans omfattning."


def _skriv_yaml(fil, data):
    fil.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


@pytest.fixture
def signerad_regelbas_rot(tmp_path):
    """En kopia av repots regelbas som en påhittad sakkunnig har gjort komplett och verifierat.

    Bara för tester. Repots regelbas ändras aldrig. Paragrafer utanför testfallet markeras som
    ej tillämpliga, vilket en riktig sakkunnig inte skulle göra.
    """
    from riskanalys.regelverk.laddning import ladda_regelbas

    rot = tmp_path / "signerad_regelbas"
    shutil.copytree(REPO_REGELBAS, rot)
    paketfiler = sorted((rot / "regelpaket").glob("*.yaml"))
    for fil in paketfiler:
        paket = yaml.safe_load(fil.read_text(encoding="utf-8"))
        rader = [
            rad if rad.get("krav") else {**rad, "ej_tillamplig": UTANFOR_TESTFALLET}
            for rad in paket["paragrafkarta"]["rader"]
        ]
        _skriv_yaml(fil, {**paket, "paragrafkarta": {**paket["paragrafkarta"], "rader": rader}})
    regelbas = ladda_regelbas(rot)
    for fil in (rot / "krav").glob("*.yaml"):
        poster = yaml.safe_load(fil.read_text(encoding="utf-8"))
        signerade = [
            {**post, "sakkunnig": {**SAKKUNNIG_TEST, "kontrollsumma": regelbas.kravets_innehallssumma(post["id"])}}
            for post in poster
        ]
        _skriv_yaml(fil, signerade)
    for fil in paketfiler:
        paket = yaml.safe_load(fil.read_text(encoding="utf-8"))
        summa = regelbas.kartans_innehallssumma(paket["id"])
        karta = {**paket["paragrafkarta"], "sakkunnig": {**SAKKUNNIG_TEST, "kontrollsumma": summa}}
        _skriv_yaml(fil, {**paket, "paragrafkarta": karta})
    return rot


@pytest.fixture
def signerad_regelbas(signerad_regelbas_rot):
    from riskanalys.regelverk.laddning import ladda_regelbas

    return ladda_regelbas(signerad_regelbas_rot)
```

- [ ] **Step 2: Skriv det felande testet `tester/enhet/test_sakgranskning.py`**

```python
from datetime import date

import pytest

from riskanalys.dokument.modeller import Avsnitt, Dokument, Textstycke
from riskanalys.faststallelse.sakgranskning import (
    SakgranskningsFel,
    galler_sakgranskning,
    granskad_summa,
    las_sakgranskningar,
    registrera_sakgranskning,
    sakgranskningsstatus,
    spara_sakgranskningar,
)
from riskanalys.lagring.datamapp import skapa_byramapp

DAG = date(2026, 11, 3)


@pytest.fixture
def profil(regelbas, profil_fabrik, real_varden):
    return profil_fabrik(regelbas, real_varden)


def _dokument(text="Byrån erbjuder löpande bokföring."):
    stycke = Textstycke(typ="beskrivning", text=text, referenser=["T-RED-01"])
    avsnitt = Avsnitt(id="D-ARB.3", rubrik="Byråns tjänster", kalla="regelbas", stycken=(stycke,))
    return Dokument(id="D-ARB", titel="Allmän riskbedömning", avsnitt=(avsnitt,))


def test_godkannande_registreras_med_den_granskade_textens_kontrollsumma(profil):
    dokument = _dokument()
    (post,) = registrera_sakgranskning((), dokument, profil, "D-ARB.3", True, "FfR", "Testa Testsson", DAG)
    assert post.kontrollsumma == granskad_summa(dokument.avsnitt[0], profil)
    assert galler_sakgranskning((post,), dokument.avsnitt[0], profil) == post
    assert sakgranskningsstatus((post,), dokument.avsnitt[0], profil) == "godkänt 2026-11-03 av Testa Testsson, roll FfR"


def test_godkannandet_galler_texten_med_insatt_namn(regelbas, profil_fabrik, real_varden, profil):
    dokument = _dokument("Funktionen för regelefterlevnad utövas av {roll:FfR}.")
    (post,) = registrera_sakgranskning((), dokument, profil, "D-ARB.3", True, "FfR", "Testa Testsson", DAG)
    assert post.kontrollsumma != dokument.avsnitt[0].kontrollsumma()
    ny_ansvarig = profil_fabrik(regelbas, {**real_varden, "P-ROLL.ffr_namn": "Ny Person"})
    assert galler_sakgranskning((post,), dokument.avsnitt[0], ny_ansvarig) is None
    assert sakgranskningsstatus((post,), dokument.avsnitt[0], ny_ansvarig) == "ändrat efter sakgranskningen, granska igen"


def test_sakgranskningen_galler_inte_andrad_text(profil):
    poster = registrera_sakgranskning((), _dokument(), profil, "D-ARB.3", True, "FfR", "Testa Testsson", DAG)
    andrat = _dokument("Byrån erbjuder löpande bokföring och lönehantering.").avsnitt[0]
    assert galler_sakgranskning(poster, andrat, profil) is None
    assert sakgranskningsstatus(poster, andrat, profil) == "ändrat efter sakgranskningen, granska igen"


def test_senaste_sakgranskningen_av_samma_lydelse_galler(profil):
    dokument = _dokument()
    poster = registrera_sakgranskning((), dokument, profil, "D-ARB.3", False, "FfR", "Testa Testsson", DAG, "Fel tjänst.")
    poster = registrera_sakgranskning(poster, dokument, profil, "D-ARB.3", True, "FfR", "Testa Testsson", DAG)
    assert galler_sakgranskning(poster, dokument.avsnitt[0], profil).godkand is True


def test_underkannande_kraver_kommentar(profil):
    with pytest.raises(SakgranskningsFel, match="--kommentar"):
        registrera_sakgranskning((), _dokument(), profil, "D-ARB.3", False, "FfR", "Testa Testsson", DAG)


def test_sakgranskning_kraver_namn(profil):
    with pytest.raises(SakgranskningsFel, match="--namn"):
        registrera_sakgranskning((), _dokument(), profil, "D-ARB.3", True, "FfR", None, DAG)


def test_okant_avsnitt_vagras(profil):
    with pytest.raises(SakgranskningsFel, match="D-ARB.9 finns inte"):
        registrera_sakgranskning((), _dokument(), profil, "D-ARB.9", True, "FfR", "Testa Testsson", DAG)


def test_ej_sakgranskat_avsnitt(profil):
    assert sakgranskningsstatus((), _dokument().avsnitt[0], profil) == "ej sakgranskat"


def test_sakgranskningar_sparas_och_lases(datamapp, profil):
    mapp = skapa_byramapp("testbyra")
    assert las_sakgranskningar(mapp) == ()
    poster = registrera_sakgranskning((), _dokument(), profil, "D-ARB.3", True, "FfR", "Testa Testsson", DAG)
    spara_sakgranskningar(mapp, poster)
    assert las_sakgranskningar(mapp) == poster
```

- [ ] **Step 3: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/enhet/test_sakgranskning.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.faststallelse'`.

- [ ] **Step 4: Skriv `src/riskanalys/faststallelse/__init__.py`**

```python
"""Fastställelse: sakgranskning, grindar, låsning och verifiering."""
```

- [ ] **Step 5: Skriv `src/riskanalys/faststallelse/modeller.py`**

```python
"""Sakgranskning och beslut om fastställelse (spec 10)."""

from datetime import date

from pydantic import BaseModel, ConfigDict


class Fryst(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Sakgranskning(Fryst):
    """En persons granskning av ett avsnitt i en bestämd lydelse, identifierad med kontrollsumman."""

    avsnitt: str
    kontrollsumma: str
    godkand: bool
    roll: str
    namn: str
    datum: date
    kommentar: str | None = None


class Beslut(Fryst):
    """Beslutet att fastställa: vilket organ, när och vem som undertecknar."""

    organ: str
    datum: date
    namn: str
    roll: str
```

- [ ] **Step 6: Skriv `src/riskanalys/faststallelse/sakgranskning.py`**

```python
"""Sakgranskning per avsnitt (spec 10).

En sakgranskning gäller exakt den text som granskaren såg: avsnittet med namnen insatta, så som exporten
skriver ut det. Ändras texten eller ett namn som sätts in i den slutar sakgranskningen att gälla.
"""

from datetime import date
from pathlib import Path

from pydantic import TypeAdapter

from riskanalys.dokument.modeller import Avsnitt, Dokument
from riskanalys.dokument.rendering import renderat_avsnitt
from riskanalys.faststallelse.modeller import Sakgranskning
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.yamlfil import las_yaml, spara_yaml
from riskanalys.profil.modeller import Profil

SAKGRANSKNINGSFIL = Path("sakgranskning") / "sakgranskningar.yaml"
_LISTA = TypeAdapter(tuple[Sakgranskning, ...])


class SakgranskningsFel(RiskanalysFel):
    """En sakgranskning kan inte registreras."""


def granskad_summa(avsnitt: Avsnitt, profil: Profil) -> str:
    """Kontrollsumman för det granskaren ser och exporten innehåller."""
    return renderat_avsnitt(avsnitt, profil).kontrollsumma()


def las_sakgranskningar(byramapp: Path) -> tuple[Sakgranskning, ...]:
    sokvag = byramapp / SAKGRANSKNINGSFIL
    if not sokvag.is_file():
        return ()
    return _LISTA.validate_python(las_yaml(sokvag) or [])


def spara_sakgranskningar(byramapp: Path, sakgranskningar: tuple[Sakgranskning, ...]) -> None:
    spara_yaml(byramapp / SAKGRANSKNINGSFIL, [post.model_dump(mode="python") for post in sakgranskningar])


def registrera_sakgranskning(
    sakgranskningar: tuple[Sakgranskning, ...],
    dokument: Dokument,
    profil: Profil,
    avsnitt_id: str,
    godkand: bool,
    roll: str,
    namn: str | None,
    datum: date,
    kommentar: str | None = None,
) -> tuple[Sakgranskning, ...]:
    """Returnerar sakgranskningarna med en ny post för avsnittet så som det ser ut med profilens namn."""
    avsnitt = dokument.avsnitt_med_id().get(avsnitt_id)
    if avsnitt is None:
        tillgangliga = ", ".join(dokument.avsnitt_med_id())
        raise SakgranskningsFel(f"Avsnittet {avsnitt_id} finns inte i dokumentet. Avsnitt: {tillgangliga}.")
    if not namn or not namn.strip():
        raise SakgranskningsFel("Ange vem som sakgranskar med --namn.")
    if not godkand and not (kommentar and kommentar.strip()):
        raise SakgranskningsFel("Ett underkännande kräver --kommentar som säger vad som är fel.")
    post = Sakgranskning(
        avsnitt=avsnitt.id,
        kontrollsumma=granskad_summa(avsnitt, profil),
        godkand=godkand,
        roll=roll,
        namn=namn.strip(),
        datum=datum,
        kommentar=kommentar.strip() if kommentar else None,
    )
    return (*sakgranskningar, post)


def galler_sakgranskning(
    sakgranskningar: tuple[Sakgranskning, ...], avsnitt: Avsnitt, profil: Profil
) -> Sakgranskning | None:
    """Den senaste sakgranskningen av avsnittet i exakt den lydelse som exporten skulle få."""
    summa = granskad_summa(avsnitt, profil)
    giltiga = [post for post in sakgranskningar if post.avsnitt == avsnitt.id and post.kontrollsumma == summa]
    return giltiga[-1] if giltiga else None


def sakgranskningsstatus(sakgranskningar: tuple[Sakgranskning, ...], avsnitt: Avsnitt, profil: Profil) -> str:
    galler = galler_sakgranskning(sakgranskningar, avsnitt, profil)
    if galler is not None:
        utfall = "godkänt" if galler.godkand else f"underkänt ({galler.kommentar})"
        return f"{utfall} {galler.datum.isoformat()} av {galler.namn}, roll {galler.roll}"
    if any(post.avsnitt == avsnitt.id for post in sakgranskningar):
        return "ändrat efter sakgranskningen, granska igen"
    return "ej sakgranskat"
```

- [ ] **Step 7: Kör testet**

Run: `.venv/bin/pytest tester/enhet/test_sakgranskning.py -v`
Expected: alla tester passerar.

- [ ] **Step 8: Skriv det felande testet `tester/regelkontrakt/test_grindar.py`**

```python
from dataclasses import replace
from datetime import date

import pytest

from riskanalys.bedomning.motor import bedom
from riskanalys.dokument.arb import bygg_arb
from riskanalys.drift.historik import Handelse, Historik
from riskanalys.faststallelse.grindar import Faststallelseunderlag, fyndhinder, hinder_for_faststallelse
from riskanalys.faststallelse.modeller import Sakgranskning
from riskanalys.faststallelse.sakgranskning import granskad_summa
from riskanalys.granskning.kontroller import granska
from riskanalys.granskning.modeller import Fynd
from riskanalys.regelverk.urval import valj
from riskanalys.regelverk.validering import validera

GRANSKNINGSDAG = date(2026, 11, 2)
SAKGRANSKNINGSDAG = date(2026, 11, 3)
BESLUTSDAG = date(2026, 11, 15)
HISTORIK = Historik().med(Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Första."))


def _underlag(regelbas, profil, utkast, historik=HISTORIK):
    urval = valj(regelbas, "RP-RED-VG", date(2026, 11, 1), "Västra Götaland")
    bedomning = bedom(regelbas, urval, profil)
    dokument = bygg_arb(regelbas, profil, bedomning, utkast, historik)
    fynd = granska(regelbas, urval, profil, bedomning, dokument, historik, GRANSKNINGSDAG)
    sakgranskningar = tuple(
        Sakgranskning(
            avsnitt=avsnitt.id,
            kontrollsumma=granskad_summa(avsnitt, profil),
            godkand=True,
            roll="FfR",
            namn="Testa Testsson",
            datum=SAKGRANSKNINGSDAG,
        )
        for avsnitt in dokument.avsnitt
    )
    return Faststallelseunderlag(
        regelbas=regelbas,
        urval=urval,
        profil=profil,
        bedomning=bedomning,
        dokument=dokument,
        fynd=fynd,
        sakgranskningar=sakgranskningar,
        historik=historik,
        granskningsdatum=GRANSKNINGSDAG,
    )


@pytest.fixture
def komplett(signerad_regelbas, profil_fabrik, real_varden, giltigt_utkast):
    return _underlag(signerad_regelbas, profil_fabrik(signerad_regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast})


def _med_andrat_krav(underlag, krav_id, **andringar):
    regelbas = underlag.regelbas
    krav = regelbas.krav[krav_id].model_copy(update=andringar)
    andrad = regelbas.model_copy(update={"krav": {**regelbas.krav, krav_id: krav}})
    return replace(underlag, regelbas=andrad, urval=valj(andrad, "RP-RED-VG", date(2026, 11, 1), "Västra Götaland"))


def _med_andrad_karta(underlag, **andringar):
    regelbas = underlag.regelbas
    paket = regelbas.regelpaket["RP-RED-VG"]
    andrat = paket.model_copy(update={"paragrafkarta": paket.paragrafkarta.model_copy(update=andringar)})
    andrad = regelbas.model_copy(update={"regelpaket": {paket.id: andrat}})
    return replace(underlag, regelbas=andrad, urval=valj(andrad, "RP-RED-VG", date(2026, 11, 1), "Västra Götaland"))


def test_den_signerade_testkopian_ar_en_giltig_regelbas(signerad_regelbas):
    assert validera(signerad_regelbas) == []


def test_komplett_underlag_har_inga_hinder(komplett):
    assert hinder_for_faststallelse(komplett, BESLUTSDAG) == []


def test_osignerad_regelbas_ger_hinder_for_krav_och_paragrafkarta(regelbas, profil_fabrik, real_varden, giltigt_utkast):
    underlag = _underlag(regelbas, profil_fabrik(regelbas, real_varden), {"D-ARB.6.1": giltigt_utkast})
    hinder = hinder_for_faststallelse(underlag, BESLUTSDAG)
    assert len([rad for rad in hinder if "är inte verifierat av sakkunnig" in rad]) == 6
    assert (
        "Paragrafkartan för regelpaketet RP-RED-VG är inte verifierad av sakkunnig i sin nuvarande lydelse "
        "(status ej_granskad)." in hinder
    )
    (ohanterade,) = [rad for rad in hinder if "ännu inte hanterar" in rad]
    assert ohanterade.startswith(
        "Paragrafkartan för regelpaketet RP-RED-VG har paragrafer som regelbasen ännu inte hanterar: "
        "SRC-14FS-2024-11 2 kap. 4 §, "
    )


def test_krav_som_inte_galler_byran_behover_inte_vara_verifierat(komplett):
    villkor = {"falt": "P-VERK.juniora_konsulter", "op": "==", "varde": True}
    krav = komplett.regelbas.krav["KRV-LSF-001"]
    underlag = _med_andrat_krav(
        komplett, "KRV-LSF-001", galler_om=villkor, sakkunnig=krav.sakkunnig.model_copy(update={"status": "ej_granskad"})
    )
    assert hinder_for_faststallelse(replace(underlag, fynd=()), BESLUTSDAG) == []


def test_krav_som_andrats_efter_verifieringen_ar_hinder(komplett):
    underlag = _med_andrat_krav(komplett, "KRV-LSF-001", text="Ett ändrat krav.")
    assert hinder_for_faststallelse(underlag, BESLUTSDAG) == [
        "Kravet KRV-LSF-001 (2 kap. 1 §) är inte verifierat av sakkunnig i sin nuvarande lydelse (status verifierad)."
    ]


def test_paragrafkarta_som_andrats_efter_verifieringen_ar_hinder(komplett):
    karta = komplett.regelbas.regelpaket["RP-RED-VG"].paragrafkarta
    rader = (*karta.rader[:-1], karta.rader[-1].model_copy(update={"ej_tillamplig": "En annan motivering."}))
    hinder = hinder_for_faststallelse(_med_andrad_karta(komplett, rader=rader), BESLUTSDAG)
    assert hinder == [
        "Paragrafkartan för regelpaketet RP-RED-VG är inte verifierad av sakkunnig i sin nuvarande lydelse "
        "(status verifierad)."
    ]


def test_paragrafkarta_som_inte_galler_bedomningens_datum_ar_hinder(komplett):
    hinder = hinder_for_faststallelse(_med_andrad_karta(komplett, giltig_fran=date(2027, 1, 1)), BESLUTSDAG)
    assert "Paragrafkartan för regelpaketet RP-RED-VG gäller inte bedömningens datum 2026-11-01." in hinder


def test_saknad_kritisk_uppgift_och_preliminar_bedomning(signerad_regelbas, profil_fabrik, real_varden, giltigt_utkast):
    profil = profil_fabrik(signerad_regelbas, real_varden, okanda=("P-KUND.andel_kontant",))
    hinder = hinder_for_faststallelse(_underlag(signerad_regelbas, profil, {"D-ARB.6.1": giltigt_utkast}), BESLUTSDAG)
    assert "Kritiska uppgifter saknas: P-KUND.andel_kontant. Bekräfta dem med 'riskanalys bekrafta'." in hinder
    assert any(rad.startswith("Bedömningen är preliminär.") for rad in hinder)
    assert "Avsnitt D-ARB.5 innehåller [VERIFIERA]." in hinder


def test_blockerande_fynd_ar_alltid_hinder(signerad_regelbas, profil_fabrik, real_varden):
    underlag = _underlag(signerad_regelbas, profil_fabrik(signerad_regelbas, real_varden), {})
    hinder = hinder_for_faststallelse(underlag, BESLUTSDAG)
    assert any("blockerande fynd" in rad and "KRV-LSF-005" in rad for rad in hinder)
    assert any("Löpande bokföring saknar eget riskavsnitt" in rad for rad in hinder)


def test_avsnitt_som_andrats_efter_sakgranskningen_ar_hinder(komplett):
    (forsta, *ovriga) = komplett.dokument.avsnitt
    stycke = forsta.stycken[0].model_copy(update={"text": forsta.stycken[0].text + " Tillägg."})
    andrat = forsta.model_copy(update={"stycken": (stycke, *forsta.stycken[1:])})
    dokument = komplett.dokument.model_copy(update={"avsnitt": (andrat, *ovriga)})
    assert hinder_for_faststallelse(replace(komplett, dokument=dokument), BESLUTSDAG) == [
        "Avsnitt D-ARB.1 är inte sakgranskat i nuvarande lydelse."
    ]


def test_byte_av_ansvarig_person_efter_sakgranskningen_ar_hinder(komplett, profil_fabrik, real_varden):
    ny_ansvarig = profil_fabrik(komplett.regelbas, {**real_varden, "P-ROLL.ffr_namn": "Ny Person"})
    assert hinder_for_faststallelse(replace(komplett, profil=ny_ansvarig), BESLUTSDAG) == [
        "Avsnitt D-ARB.1 är inte sakgranskat i nuvarande lydelse."
    ]


def test_underkant_avsnitt_ar_hinder(komplett):
    avsnitt = komplett.dokument.avsnitt[0]
    underkant = Sakgranskning(
        avsnitt=avsnitt.id,
        kontrollsumma=granskad_summa(avsnitt, komplett.profil),
        godkand=False,
        roll="FfR",
        namn="Testa Testsson",
        datum=date(2026, 11, 4),
        kommentar="Fel antal anställda.",
    )
    underlag = replace(komplett, sakgranskningar=(*komplett.sakgranskningar, underkant))
    assert hinder_for_faststallelse(underlag, BESLUTSDAG) == [
        "Avsnitt D-ARB.1 underkändes vid sakgranskningen: Fel antal anställda."
    ]


def test_utvardering_saknas_eller_har_passerat(komplett):
    utan = replace(komplett, historik=Historik())
    assert "Datum för utvärdering saknas. Registrera utvärderingen med 'riskanalys utvardera'." in (
        hinder_for_faststallelse(utan, BESLUTSDAG)
    )
    assert hinder_for_faststallelse(komplett, date(2027, 11, 2)) == [
        "Nästa genomgång skulle ha gjorts senast 2027-11-01. Utvärdera riskbedömningen igen."
    ]


def test_beslut_fore_granskningen_och_sakgranskningen_ar_hinder(komplett):
    assert hinder_for_faststallelse(komplett, date(2026, 11, 1)) == [
        "Beslutsdatum 2026-11-01 är före granskningen 2026-11-02.",
        "Beslutsdatum 2026-11-01 är före den senaste sakgranskningen 2026-11-03.",
    ]


def test_beslut_samma_dag_som_sakgranskningen_godtas(komplett):
    assert hinder_for_faststallelse(komplett, SAKGRANSKNINGSDAG) == []


def test_beslut_fore_senaste_utvarderingen_ar_hinder(komplett):
    historik = HISTORIK.med(Handelse(datum=date(2026, 11, 20), typ="utvärdering", beskrivning="Andra."))
    assert hinder_for_faststallelse(replace(komplett, historik=historik), BESLUTSDAG) == [
        "Beslutsdatum 2026-11-15 är före den senaste utvärderingen 2026-11-20."
    ]


def test_beslut_fore_en_tidigare_faststallelse_ar_hinder(komplett):
    faststallelse = Handelse(datum=date(2026, 11, 20), typ="fastställelse", beskrivning="v1", version=1)
    assert hinder_for_faststallelse(replace(komplett, historik=HISTORIK.med(faststallelse)), BESLUTSDAG) == [
        "Beslutsdatum 2026-11-15 är före den senaste fastställelsen 2026-11-20."
    ]


def _fynd(allvar="hög", grund="tillsynspraxis", status="öppen", motivering=None):
    return Fynd(
        id="F-2026-11-02-001",
        typ="bristmonster",
        regel="B-04",
        allvar=allvar,
        grund=grund,
        beskrivning="Beskrivning.",
        atgard="Åtgärd.",
        status=status,
        motivering=motivering,
    )


@pytest.mark.parametrize(
    ("fynd", "hinder"),
    [
        (_fynd(), "fyndet är öppet"),
        (_fynd(allvar="medel"), "fyndet är öppet"),
        (_fynd(status="åtgärdad"), None),
        (_fynd(allvar="blockerande", status="åtgärdad"), "blockerande fynd"),
        (_fynd(grund="ska_krav", status="accepterad_metodavvikelse", motivering="KRV-LSF-005 uppfylls."), "sakkunnig"),
        (_fynd(grund="ska_krav", status="sakkunnigbedömd", motivering="Kravet är uppfyllt genom avsnitt 6."), None),
        (_fynd(grund="ska_krav", status="sakkunnigbedömd"), "saknar motivering"),
        (_fynd(grund="metodval", status="accepterad_metodavvikelse", motivering="Annan skala."), None),
        (_fynd(grund="metodval", status="accepterad_metodavvikelse"), "saknar motivering"),
        (_fynd(status="accepterad_metodavvikelse", motivering="Vi gör på annat sätt."), "KRV-"),
        (_fynd(status="accepterad_metodavvikelse", motivering="KRV-LSF-005 uppfylls i avsnitt 6."), None),
        (_fynd(grund="eu_utkast", status="accepterad_metodavvikelse", motivering="Inte bindande än."), "KRV-"),
    ],
)
def test_fyndhinder_foljer_fyndets_grund(fynd, hinder):
    if hinder is None:
        assert fyndhinder(fynd) == []
    else:
        (rad,) = fyndhinder(fynd)
        assert hinder in rad
```

- [ ] **Step 9: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/regelkontrakt/test_grindar.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'riskanalys.faststallelse.grindar'`.

- [ ] **Step 10: Skriv `src/riskanalys/faststallelse/grindar.py`**

```python
"""Villkor för fastställelse (spec 10). Varje hinder är en mening som säger vad som saknas."""

from dataclasses import dataclass
from datetime import date

from riskanalys.bedomning.modeller import Bedomning
from riskanalys.dokument.modeller import Dokument
from riskanalys.dokument.validering import VERIFIERA
from riskanalys.drift.historik import Historik
from riskanalys.faststallelse.modeller import Sakgranskning
from riskanalys.faststallelse.sakgranskning import galler_sakgranskning
from riskanalys.granskning.modeller import Fynd
from riskanalys.profil.hantering import saknade_kritiska
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.urval import Urval, kravet_galler

ICKE_BINDANDE = frozenset({"allmänt_råd", "tillsynspraxis", "eu_utkast"})
FASTSTALLELSE = "fastställelse"


@dataclass(frozen=True)
class Faststallelseunderlag:
    """Allt som grinden prövar. Läses från den senaste granskningen och den bedömning den hör till.

    historik är versionshistoriken inklusive tidigare fastställelser. granskningsdatum är granskningens datum.
    """

    regelbas: Regelbas
    urval: Urval
    profil: Profil
    bedomning: Bedomning
    dokument: Dokument
    fynd: tuple[Fynd, ...]
    sakgranskningar: tuple[Sakgranskning, ...]
    historik: Historik
    granskningsdatum: date


def hinder_for_faststallelse(underlag: Faststallelseunderlag, beslutsdatum: date) -> list[str]:
    """Alla skäl att inte fastställa. Tom lista betyder att villkoren i spec 10 är uppfyllda."""
    return [
        *_uppgifter(underlag),
        *_bedomning(underlag),
        *_verifiera(underlag),
        *_sakkunnig(underlag),
        *_paragrafkarta(underlag),
        *(rad for post in underlag.fynd for rad in fyndhinder(post)),
        *_sakgranskning(underlag),
        *_drift(underlag, beslutsdatum),
        *_kronologi(underlag, beslutsdatum),
    ]


def fyndhinder(post: Fynd) -> list[str]:
    """Hinder från ett fynd, efter fyndets allvar, status och grund (spec 10, villkor 4)."""
    if post.allvar == "blockerande":
        return [f"{post.id}: blockerande fynd måste åtgärdas. {post.beskrivning}"]
    if post.status == "åtgärdad":
        return []
    if post.status == "öppen":
        return [f"{post.id}: fyndet är öppet. {post.beskrivning}"]
    motivering = (post.motivering or "").strip()
    if post.status == "sakkunnigbedömd":
        return [] if motivering else [f"{post.id}: den sakkunniga bedömningen saknar motivering."]
    if post.grund == "ska_krav":
        return [f"{post.id}: ett lagkrav kan inte accepteras som metodavvikelse. Det kräver en sakkunnig bedömning."]
    if not motivering:
        return [f"{post.id}: avvikelsen saknar motivering."]
    if post.grund in ICKE_BINDANDE and "KRV-" not in motivering:
        return [f"{post.id}: avvikelse från {post.grund} ska hänvisa till det bindande krav (KRV-) som ändå uppfylls."]
    return []


def _uppgifter(underlag: Faststallelseunderlag) -> list[str]:
    saknade = saknade_kritiska(underlag.profil, underlag.regelbas, underlag.urval)
    if not saknade:
        return []
    return [f"Kritiska uppgifter saknas: {', '.join(saknade)}. Bekräfta dem med 'riskanalys bekrafta'."]


def _bedomning(underlag: Faststallelseunderlag) -> list[str]:
    if underlag.bedomning.status != "preliminär":
        return []
    return ["Bedömningen är preliminär. Bekräfta de okända uppgifterna och kör 'riskanalys bedom' igen."]


def _verifiera(underlag: Faststallelseunderlag) -> list[str]:
    return [
        f"Avsnitt {avsnitt.id} innehåller {VERIFIERA}."
        for avsnitt in underlag.dokument.avsnitt
        if any(VERIFIERA in stycke.text for stycke in avsnitt.stycken)
    ]


def _sakkunnig(underlag: Faststallelseunderlag) -> list[str]:
    """Varje krav som gäller byrån ska vara verifierat i just den lydelse det har nu."""
    varden = underlag.profil.faltvarden()
    return [
        f"Kravet {valt.krav.id} ({valt.krav.lagrum}) är inte verifierat av sakkunnig i sin nuvarande lydelse "
        f"(status {valt.krav.sakkunnig.status})."
        for valt in underlag.urval.krav
        if kravet_galler(underlag.regelbas, valt.krav, varden)
        and not valt.krav.sakkunnig.galler(underlag.regelbas.kravets_innehallssumma(valt.krav.id))
    ]


def _paragrafkarta(underlag: Faststallelseunderlag) -> list[str]:
    """Kartan ska vara verifierad i sin nuvarande lydelse, hantera varje paragraf och gälla bedömningens datum."""
    paket = underlag.urval.regelpaket
    karta = paket.paragrafkarta
    namn = f"Paragrafkartan för regelpaketet {paket.id}"
    hinder = []
    if not karta.sakkunnig.galler(underlag.regelbas.kartans_innehallssumma(paket.id)):
        hinder.append(
            f"{namn} är inte verifierad av sakkunnig i sin nuvarande lydelse (status {karta.sakkunnig.status})."
        )
    ohanterade = karta.ohanterade()
    if ohanterade:
        lista = ", ".join(f"{rad.kalla} {rad.lagrum}" for rad in ohanterade)
        hinder.append(f"{namn} har paragrafer som regelbasen ännu inte hanterar: {lista}.")
    if not karta.galler(underlag.bedomning.datum):
        hinder.append(f"{namn} gäller inte bedömningens datum {underlag.bedomning.datum.isoformat()}.")
    return hinder


def _sakgranskning(underlag: Faststallelseunderlag) -> list[str]:
    hinder = []
    for avsnitt in underlag.dokument.avsnitt:
        galler = galler_sakgranskning(underlag.sakgranskningar, avsnitt, underlag.profil)
        if galler is None:
            hinder.append(f"Avsnitt {avsnitt.id} är inte sakgranskat i nuvarande lydelse.")
        elif not galler.godkand:
            hinder.append(f"Avsnitt {avsnitt.id} underkändes vid sakgranskningen: {galler.kommentar}")
    return hinder


def _drift(underlag: Faststallelseunderlag, beslutsdatum: date) -> list[str]:
    nasta = underlag.historik.nasta_genomgang()
    if nasta is None:
        return ["Datum för utvärdering saknas. Registrera utvärderingen med 'riskanalys utvardera'."]
    if nasta < beslutsdatum:
        return [f"Nästa genomgång skulle ha gjorts senast {nasta.isoformat()}. Utvärdera riskbedömningen igen."]
    return []


def _kronologi(underlag: Faststallelseunderlag, beslutsdatum: date) -> list[str]:
    """Ett beslut kan inte fattas innan underlaget finns: granskning, sakgranskning, utvärdering och tidigare beslut."""
    sakgranskade = [
        galler.datum
        for avsnitt in underlag.dokument.avsnitt
        if (galler := galler_sakgranskning(underlag.sakgranskningar, avsnitt, underlag.profil)) is not None
    ]
    faststallda = [handelse.datum for handelse in underlag.historik.handelser if handelse.typ == FASTSTALLELSE]
    tidigare = (
        ("granskningen", underlag.granskningsdatum),
        ("den senaste sakgranskningen", max(sakgranskade, default=None)),
        ("den senaste utvärderingen", underlag.historik.senaste_utvardering()),
        ("den senaste fastställelsen", max(faststallda, default=None)),
    )
    return [
        f"Beslutsdatum {beslutsdatum.isoformat()} är före {namn} {datum.isoformat()}."
        for namn, datum in tidigare
        if datum is not None and beslutsdatum < datum
    ]
```

- [ ] **Step 11: Kör testet**

Run: `.venv/bin/pytest tester/regelkontrakt/test_grindar.py -v`
Expected: alla tester passerar.

- [ ] **Step 12: Skriv det felande testet `tester/enhet/test_sakgranska_kommando.py`**

```python
from datetime import date

from riskanalys.cli import main
from riskanalys.faststallelse.sakgranskning import las_sakgranskningar
from riskanalys.granskning.korning import kor_granskning

GODKANN = ["--godkann", "--namn", "Testa Testsson", "--datum", "2026-11-03"]


def test_sakgranska_fore_granskning_sager_vilket_steg_som_saknas(skriven_byra, capsys):
    assert main(["sakgranska", "testbyra"]) == 1
    assert "Kör 'riskanalys granska testbyra' först" in capsys.readouterr().err


def test_listan_visar_status_per_avsnitt(skriven_byra, regelbas, capsys):
    kor_granskning(skriven_byra, regelbas, date(2026, 11, 2))
    assert main(["sakgranska", "testbyra"]) == 0
    rader = capsys.readouterr().out.splitlines()
    assert "D-ARB.6.1 Risk i löpande bokföring: ej sakgranskat" in rader
    assert sum(1 for rad in rader if rad.startswith("D-ARB.")) == 6


def test_visa_avsnitt_med_namn_insatt(skriven_byra, regelbas, capsys):
    kor_granskning(skriven_byra, regelbas, date(2026, 11, 2))
    assert main(["sakgranska", "testbyra", "--avsnitt", "D-ARB.1"]) == 0
    utskrift = capsys.readouterr().out
    assert "Funktionen för regelefterlevnad utövas av Testa Testsson." in utskrift
    assert "{roll:FfR}" not in utskrift


def test_godkann_avsnitt(skriven_byra, regelbas, capsys):
    kor_granskning(skriven_byra, regelbas, date(2026, 11, 2))
    assert main(["sakgranska", "testbyra", "--avsnitt", "D-ARB.6.1", *GODKANN]) == 0
    (post,) = las_sakgranskningar(skriven_byra)
    assert (post.avsnitt, post.godkand, post.roll) == ("D-ARB.6.1", True, "FfR")
    main(["sakgranska", "testbyra"])
    assert "D-ARB.6.1 Risk i löpande bokföring: godkänt 2026-11-03 av Testa Testsson, roll FfR" in capsys.readouterr().out


def test_underkann_utan_kommentar_vagras(skriven_byra, regelbas, capsys):
    kor_granskning(skriven_byra, regelbas, date(2026, 11, 2))
    assert main(["sakgranska", "testbyra", "--avsnitt", "D-ARB.6.1", "--underkann", "--namn", "Testa Testsson"]) == 1
    assert "--kommentar" in capsys.readouterr().err
    assert las_sakgranskningar(skriven_byra) == ()


def test_godkann_utan_avsnitt_vagras(skriven_byra, regelbas, capsys):
    kor_granskning(skriven_byra, regelbas, date(2026, 11, 2))
    assert main(["sakgranska", "testbyra", *GODKANN]) == 1
    assert "--avsnitt" in capsys.readouterr().err


def test_andrad_granskning_kan_inte_sakgranskas(skriven_byra, regelbas, capsys):
    mapp = kor_granskning(skriven_byra, regelbas, date(2026, 11, 2))
    fil = mapp / "dokument.json"
    fil.write_text(fil.read_text(encoding="utf-8").replace("Testbyrån AB", "Annan byrå AB"), encoding="utf-8")
    assert main(["sakgranska", "testbyra", "--avsnitt", "D-ARB.1", *GODKANN]) == 1
    assert "Granskningen är ändrad efter körningen. Fil ändrad: dokument.json" in capsys.readouterr().err
    assert las_sakgranskningar(skriven_byra) == ()
```

- [ ] **Step 13: Skriv `src/riskanalys/kommandon/sakgranska_kommando.py`**

```python
"""riskanalys sakgranska"""

import argparse
from datetime import date
from typing import Any

from riskanalys.dokument.rendering import renderat_avsnitt
from riskanalys.faststallelse.sakgranskning import (
    SakgranskningsFel,
    las_sakgranskningar,
    registrera_sakgranskning,
    sakgranskningsstatus,
    spara_sakgranskningar,
)
from riskanalys.granskning.korning import GRANSKNING, granskningens_profil, kontrollera_kallor, las_granskning
from riskanalys.kommandon import datumargument
from riskanalys.lagring.datamapp import befintlig_byramapp
from riskanalys.lagring.korningar import senaste_korning


def lagg_till(underparsers: Any) -> None:
    parser = underparsers.add_parser("sakgranska", help="Gå igenom och godkänn avsnitten ett och ett.")
    parser.add_argument("byra")
    parser.add_argument("--avsnitt", help="Avsnittets ID, till exempel D-ARB.6.1. Utan beslut visas texten.")
    beslut = parser.add_mutually_exclusive_group()
    beslut.add_argument("--godkann", action="store_true", help="Godkänn avsnittet i sin nuvarande lydelse.")
    beslut.add_argument("--underkann", action="store_true", help="Underkänn avsnittet. Kräver --kommentar.")
    parser.add_argument("--kommentar", help="Vad som är fel, eller annan kommentar.")
    parser.add_argument("--namn", help="Namn på den som sakgranskar.")
    parser.add_argument("--roll", default="FfR", help="Rollen hos den som sakgranskar. Standard är FfR.")
    parser.add_argument("--datum", type=datumargument, default=None, help="Standard är dagens datum.")
    parser.set_defaults(kor=kor_sakgranska)


def kor_sakgranska(args: argparse.Namespace) -> int:
    byramapp = befintlig_byramapp(args.byra)
    granskningsmapp = senaste_korning(byramapp, GRANSKNING, f"granska {args.byra}")
    kontrollera_kallor(byramapp, granskningsmapp)
    dokument, _ = las_granskning(granskningsmapp)
    profil = granskningens_profil(byramapp, granskningsmapp)
    sakgranskningar = las_sakgranskningar(byramapp)
    if args.godkann or args.underkann:
        if not args.avsnitt:
            raise SakgranskningsFel("Ange vilket avsnitt beslutet gäller med --avsnitt.")
        nya = registrera_sakgranskning(
            sakgranskningar,
            dokument,
            profil,
            args.avsnitt,
            args.godkann,
            args.roll,
            args.namn,
            args.datum or date.today(),
            args.kommentar,
        )
        spara_sakgranskningar(byramapp, nya)
        print(f"{args.avsnitt}: {sakgranskningsstatus(nya, dokument.avsnitt_med_id()[args.avsnitt], profil)}")
        return 0
    if args.avsnitt:
        avsnitt = dokument.avsnitt_med_id().get(args.avsnitt)
        if avsnitt is None:
            raise SakgranskningsFel(f"Avsnittet {args.avsnitt} finns inte i dokumentet.")
        print(f"{avsnitt.id} {avsnitt.rubrik} ({sakgranskningsstatus(sakgranskningar, avsnitt, profil)})")
        for stycke in renderat_avsnitt(avsnitt, profil).stycken:
            print(f"\n[{stycke.typ}] {stycke.text}")
            print(f"Hänvisningar: {', '.join(stycke.referenser) or 'inga'}")
        return 0
    for avsnitt in dokument.avsnitt:
        print(f"{avsnitt.id} {avsnitt.rubrik}: {sakgranskningsstatus(sakgranskningar, avsnitt, profil)}")
    print(f"Visa ett avsnitt med 'riskanalys sakgranska {args.byra} --avsnitt <ID>'.")
    return 0
```

- [ ] **Step 14: Registrera kommandot i `src/riskanalys/cli.py`**

Lägg till `sakgranska_kommando` i importen från `riskanalys.kommandon` och sist i `KOMMANDON`:

```python
from riskanalys.kommandon import (
    bedom_kommando,
    drift_kommando,
    exportera_kommando,
    granska_kommando,
    profil_kommando,
    regelbas_kommando,
    sakgranska_kommando,
    skriv_kommando,
)

KOMMANDON = [
    regelbas_kommando,
    profil_kommando,
    drift_kommando,
    bedom_kommando,
    skriv_kommando,
    granska_kommando,
    exportera_kommando,
    sakgranska_kommando,
]
```

- [ ] **Step 15: Kör testerna**

Run: `.venv/bin/pytest tester/enhet/test_sakgranskning.py tester/regelkontrakt/test_grindar.py tester/enhet/test_sakgranska_kommando.py -v`
Expected: alla tester passerar.

- [ ] **Step 16: Commit**

```bash
git add src/riskanalys/faststallelse src/riskanalys/kommandon/sakgranska_kommando.py src/riskanalys/cli.py tester/conftest.py tester/enhet/test_sakgranskning.py tester/regelkontrakt/test_grindar.py tester/enhet/test_sakgranska_kommando.py
git commit -m "feat: sakgranskning per avsnitt och villkor för fastställelse"
```

---

### Task 21: Fastställelse, låst paket och kommandona `faststall` och `verifiera`

**Files:**
- Create: `src/riskanalys/faststallelse/faststall.py`
- Create: `src/riskanalys/kommandon/faststall_kommando.py`
- Modify: `src/riskanalys/cli.py`
- Modify: `tester/conftest.py` (hjälpfunktionen `kor_kedja` och fixturen `kedja`)
- Test: `tester/enhet/test_faststall.py`, `tester/enhet/test_faststall_kommando.py`

**Interfaces:**
- Consumes: `Beslut`, `Faststallelseunderlag`, `hinder_for_faststallelse`, `las_sakgranskningar`, `registrera_sakgranskning`, `spara_sakgranskningar`, `GRANSKNING`, `las_granskning`, `andrade_kallor`, `kor_granskning`, `BEDOMNINGAR`, `aktualitetshinder`, `las_bedomning`, `las_bedomningsprofil`, `UTKAST`, `Handelse`, `las_historik`, `spara_historik`, `historikens_kontrollsumma`, `faststalld_status`, `rendera_docx`, `regelbasens_kontrollsumma`, `valj`, `senaste_korning`, `avslutade_korningar`, `skriv_manifest`, `las_manifest`, `verifiera_manifest`, `spara_yaml`, `datumargument`, `regelbasargument`, `ladda_giltig_regelbas`, `befintlig_byramapp`, `RiskanalysFel`.
- Produces:
  - `faststallelse/faststall.py`: `FASTSTALLDA = "faststallda"`, `BESLUTSFIL = "beslut.yaml"`, `FaststallelseFel(RiskanalysFel)` med attributet `hinder: list[str]`, `paketfil(version: int) -> str`, `faststallda_versioner(byramapp: Path) -> tuple[tuple[int, Path], ...]`, `nasta_version(byramapp: Path) -> int`, `skadade_versioner(byramapp: Path) -> list[str]`, `versionshistorik(byramapp: Path) -> Historik` (kastar `RiskanalysFel` om ett tidigare paket inte stämmer med sitt manifest), `kedjehinder(byramapp: Path, regelbas_rot: Path, regelbas: Regelbas, granskningsmapp: Path) -> list[str]`, `faststall(byramapp: Path, regelbas_rot: Path, regelbas: Regelbas, beslut: Beslut) -> Path`, `verifiera_version(byramapp: Path, version: int) -> list[str]`.
  - Kommandona `faststall <byra> --organ ORGAN --datum D --namn NAMN [--roll FfR] [--regelbas MAPP]` och `verifiera <byra> <version>`. `verifiera` returnerar 0 när paketet stämmer och 2 när det inte gör det.
  - Manifestets metadata för ett fastställt paket: `typ = "faststallt_paket"`, `version`, `organ`, `beslutsdatum`, `regelpaket`, `datum`, `lan`, `regelbas_version`, `regelbas_kontrollsumma`, `granskning`.
  - I `tester/conftest.py`: `kor_kedja(byramapp, regelbas, utkast)` (kör allt fram till och med godkänd sakgranskning av varje avsnitt) och fixturen `kedja` (byrå där `kor_kedja` körts med den signerade regelbasen).

Specen skriver `faststall <byrå> --beslut "styrelsen 2026-11-15"`. Planen delar upp beslutet i `--organ`, `--datum`, `--namn` och `--roll`, eftersom spec 10 kräver att namn, roll och datum registreras och en sammanslagen sträng måste tolkas.

Fastställelsen prövar först att kedjan hänger ihop (`kedjehinder`) och sedan villkoren i spec 10 (`hinder_for_faststallelse`, Task 20). Kedjan hänger ihop när:

0. varje tidigare fastställd version stämmer med sitt manifest (`skadade_versioner`). Tidigare paket läses för versionshistoriken och datumordningen, så ett ändrat beslut i v1 får inte följa med in i v2. Ett ändrat eller ofullständigt paket stoppar allt tills det återställts från säkerhetskopian,
1. granskningen, bedömningen den bygger på och AI-utkasten den använde stämmer med sina manifest (`andrade_kallor`, Task 18),
2. granskningen hör till den senaste bedömningen,
3. bedömningen är aktuell: samma regelbas och samma profil (`aktualitetshinder`, Task 13),
4. granskningen inte redan är fastställd som en tidigare version,
5. byråns registrerade versionshistorik är densamma som när granskningen gjordes, och
6. regelbasmappen som kopieras in är exakt den regelbas som är inläst.

Finns ett hinder fastställs ingenting, och felet räknar upp alla hinder.

**Publiceringen är ett enda steg.** Paketet byggs i en arbetsmapp `faststallda/.v{n}-pagaende`. Där skrivs allt: kopiorna, beslutet, Word-filen, sakgranskningarna, versionshistoriken med det nya beslutet och sist manifestet. Därefter byter arbetsmappen namn till `faststallda/v{n}`, vilket sker helt eller inte alls. Efter namnbytet skrivs ingenting mer. Avbryts fastställelsen före namnbytet finns ingen version, och nästa försök tar bort arbetsmappen och börjar om. Avbryts den efter namnbytet är versionen redan komplett.

Därför skrivs fastställelsen inte till byråns historikfil. Byråns `drift/historik.yaml` innehåller de utvärderingar och uppdateringar som byrån registrerar, och `versionshistorik` lägger till varje fastställd version ur de låsta paketen. Paketets egen `drift/historik.yaml` är versionshistoriken vid beslutet, inklusive beslutet självt.

Paketet är fristående (spec 5.3): det innehåller kopior av bedömningen, granskningen, AI-utkasten, sakgranskningarna (`sakgranskning/`), versionshistoriken (`drift/`), beslutet och hela regelbasen, samt Word-filen med statusraden "Fastställt av [organ] [datum]. Version [n]." En ny version kräver en ny granskning och ett beslut som inte är daterat före den (Task 20). Sakgranskningarna gäller fortfarande för de avsnitt vars text inte ändrats.

- [ ] **Step 1: Lägg till hjälpfunktion och fixturer sist i `tester/conftest.py`**

```python
def kor_kedja(byramapp, regelbas, utkast):
    """Kör kedjan fram till och med godkänd sakgranskning av varje avsnitt."""
    from riskanalys.faststallelse.sakgranskning import registrera_sakgranskning, spara_sakgranskningar
    from riskanalys.granskning.korning import granskningens_profil, kor_granskning, las_granskning

    kor_till_skrivning(byramapp, regelbas, utkast)
    granskningsmapp = kor_granskning(byramapp, regelbas, date(2026, 11, 2))
    dokument, _ = las_granskning(granskningsmapp)
    profil = granskningens_profil(byramapp, granskningsmapp)
    sakgranskningar = ()
    for avsnitt in dokument.avsnitt:
        sakgranskningar = registrera_sakgranskning(
            sakgranskningar, dokument, profil, avsnitt.id, True, "FfR", "Testa Testsson", date(2026, 11, 3)
        )
    spara_sakgranskningar(byramapp, sakgranskningar)


@pytest.fixture
def kedja(byra_med_profil, signerad_regelbas, giltigt_utkast):
    """En byrå där hela kedjan fram till sakgranskning är körd med den signerade regelbasen."""
    kor_kedja(byra_med_profil, signerad_regelbas, giltigt_utkast)
    return byra_med_profil


@pytest.fixture
def osignerad_kedja(byra_med_profil, regelbas, giltigt_utkast):
    """Samma kedja med repots regelbas, som inte är sakkunniggranskad. Den får aldrig gå att fastställa."""
    kor_kedja(byra_med_profil, regelbas, giltigt_utkast)
    return byra_med_profil
```

- [ ] **Step 2: Skriv det felande testet `tester/enhet/test_faststall.py`**

```python
from datetime import date

import docx
import pytest

from riskanalys.bedomning.korning import kor_bedomning
from riskanalys.drift.historik import historikens_kontrollsumma, las_historik
from riskanalys.faststallelse import faststall as faststallmodul
from riskanalys.faststallelse.faststall import (
    FASTSTALLDA,
    FaststallelseFel,
    faststall,
    faststallda_versioner,
    nasta_version,
    paketfil,
    verifiera_version,
    versionshistorik,
)
from riskanalys.faststallelse.modeller import Beslut
from riskanalys.faststallelse.sakgranskning import spara_sakgranskningar
from riskanalys.fel import RiskanalysFel
from riskanalys.granskning.korning import kor_granskning
from riskanalys.lagring.manifest import las_manifest, verifiera_manifest
from riskanalys.profil.hantering import bekrafta
from riskanalys.profil.lagring import las_profil, spara_profil
from riskanalys.regelverk.laddning import STANDARD_REGELBAS

BESLUT = Beslut(organ="styrelsen", datum=date(2026, 11, 15), namn="Testa Testsson", roll="FfR")
SENARE_BESLUT = BESLUT.model_copy(update={"datum": date(2026, 11, 20)})
PAKETFILER = [
    "bedomning/bedomning.json",
    "bedomning/profil.yaml",
    "granskning/dokument.json",
    "utkast/D-ARB.6.1.json",
    "utkast/D-ARB.6.1/forsok-1.json",
    "sakgranskning/sakgranskningar.yaml",
    "drift/historik.yaml",
    "beslut.yaml",
    "regelbas/version.yaml",
    "regelbas/lydelsetexter/LYD-LSF-2-3-2024-07-01.txt",
]


def test_lyckad_faststallelse_ger_ett_fristaende_och_last_paket(kedja, signerad_regelbas_rot, signerad_regelbas):
    mapp = faststall(kedja, signerad_regelbas_rot, signerad_regelbas, BESLUT)
    assert mapp == kedja / FASTSTALLDA / "v1"
    assert verifiera_manifest(mapp) == []
    for fil in [*PAKETFILER, paketfil(1)]:
        assert (mapp / fil).is_file(), fil
    metadata = las_manifest(mapp).metadata
    assert (metadata["typ"], metadata["version"], metadata["organ"]) == ("faststallt_paket", "1", "styrelsen")
    assert metadata["regelbas_kontrollsumma"] == signerad_regelbas.kontrollsumma


def test_word_filen_ar_markt_som_faststalld_av_byran(kedja, signerad_regelbas_rot, signerad_regelbas):
    mapp = faststall(kedja, signerad_regelbas_rot, signerad_regelbas, BESLUT)
    word = docx.Document(str(mapp / paketfil(1)))
    assert word.sections[0].header.paragraphs[0].text == "Fastställt av styrelsen 2026-11-15. Version 1."
    texter = " ".join(stycke.text for stycke in word.paragraphs)
    assert "UTKAST" not in texter
    assert "Testa Testsson" in texter


def test_faststallelsen_skriver_bara_i_paketet(kedja, signerad_regelbas_rot, signerad_regelbas):
    """Efter publiceringen skrivs ingenting mer. Byråns historikfil är orörd och fastställelsen läses ur paketet."""
    fore = historikens_kontrollsumma(kedja)
    mapp = faststall(kedja, signerad_regelbas_rot, signerad_regelbas, BESLUT)
    assert historikens_kontrollsumma(kedja) == fore
    historik = versionshistorik(kedja)
    assert [(handelse.typ, handelse.version) for handelse in historik.handelser] == [
        ("utvärdering", None),
        ("fastställelse", 1),
    ]
    assert historik.nasta_genomgang() == date(2027, 11, 1)
    assert las_historik(mapp) == historik


def test_en_redan_faststalld_granskning_kan_inte_faststallas_igen(kedja, signerad_regelbas_rot, signerad_regelbas):
    faststall(kedja, signerad_regelbas_rot, signerad_regelbas, BESLUT)
    with pytest.raises(FaststallelseFel, match="är redan fastställd som version 1"):
        faststall(kedja, signerad_regelbas_rot, signerad_regelbas, SENARE_BESLUT)
    assert nasta_version(kedja) == 2


def test_beslut_daterat_fore_en_ny_granskning_vagras(kedja, signerad_regelbas_rot, signerad_regelbas):
    faststall(kedja, signerad_regelbas_rot, signerad_regelbas, BESLUT)
    kor_granskning(kedja, signerad_regelbas, date(2026, 11, 16))
    with pytest.raises(FaststallelseFel, match="Beslutsdatum 2026-11-15 är före granskningen 2026-11-16"):
        faststall(kedja, signerad_regelbas_rot, signerad_regelbas, BESLUT)
    assert faststall(kedja, signerad_regelbas_rot, signerad_regelbas, SENARE_BESLUT).name == "v2"
    assert [version for version, _ in faststallda_versioner(kedja)] == [1, 2]
    assert [handelse.version for handelse in versionshistorik(kedja).handelser if handelse.version] == [1, 2]
    assert verifiera_version(kedja, 1) == []


def test_manipulerad_fil_i_paketet_upptacks(kedja, signerad_regelbas_rot, signerad_regelbas):
    mapp = faststall(kedja, signerad_regelbas_rot, signerad_regelbas, BESLUT)
    (mapp / "beslut.yaml").write_text("organ: någon annan\n", encoding="utf-8")
    assert verifiera_version(kedja, 1) == ["Fil ändrad: beslut.yaml"]


def test_osignerad_regelbas_kan_inte_faststallas(osignerad_kedja, regelbas):
    with pytest.raises(FaststallelseFel) as fel:
        faststall(osignerad_kedja, STANDARD_REGELBAS, regelbas, BESLUT)
    assert len([rad for rad in fel.value.hinder if "inte verifierat av sakkunnig" in rad]) == 6
    assert any("ännu inte hanterar" in rad for rad in fel.value.hinder)
    assert faststallda_versioner(osignerad_kedja) == ()


def test_andrad_profil_efter_bedomningen_stoppar(kedja, signerad_regelbas_rot, signerad_regelbas):
    profil = bekrafta(
        las_profil(kedja), signerad_regelbas, "P-ORG.antal_anstallda", "9", "Lönelistan", "FfR", date(2026, 11, 4)
    )
    spara_profil(kedja, profil)
    with pytest.raises(FaststallelseFel, match="Profilen har ändrats sedan bedömningen"):
        faststall(kedja, signerad_regelbas_rot, signerad_regelbas, BESLUT)


def test_granskning_av_en_aldre_bedomning_stoppar(kedja, signerad_regelbas_rot, signerad_regelbas):
    kor_bedomning(kedja, signerad_regelbas)
    with pytest.raises(FaststallelseFel, match="Granskningen hör inte till den senaste bedömningen"):
        faststall(kedja, signerad_regelbas_rot, signerad_regelbas, BESLUT)


def test_andrad_profilkopia_i_bedomningen_stoppar(kedja, signerad_regelbas_rot, signerad_regelbas):
    (bedomningsmapp,) = (kedja / "bedomningar").iterdir()
    fil = bedomningsmapp / "profil.yaml"
    fil.write_text(fil.read_text(encoding="utf-8").replace("Testa Testsson", "Någon Annan"), encoding="utf-8")
    with pytest.raises(FaststallelseFel, match="Bedömningen är ändrad efter körningen. Fil ändrad: profil.yaml"):
        faststall(kedja, signerad_regelbas_rot, signerad_regelbas, BESLUT)


def test_osakgranskade_avsnitt_stoppar(kedja, signerad_regelbas_rot, signerad_regelbas):
    spara_sakgranskningar(kedja, ())
    with pytest.raises(FaststallelseFel, match="Avsnitt D-ARB.6.1 är inte sakgranskat i nuvarande lydelse"):
        faststall(kedja, signerad_regelbas_rot, signerad_regelbas, BESLUT)


def test_annan_regelbasmapp_an_den_inlasta_stoppar(kedja, signerad_regelbas):
    with pytest.raises(FaststallelseFel, match="stämmer inte med den inlästa regelbasen"):
        faststall(kedja, STANDARD_REGELBAS, signerad_regelbas, BESLUT)


def test_faststall_fore_granskning_sager_vilket_steg_som_saknas(byra_med_profil, signerad_regelbas_rot, signerad_regelbas):
    with pytest.raises(RiskanalysFel, match="Kör 'riskanalys granska testbyra' först"):
        faststall(byra_med_profil, signerad_regelbas_rot, signerad_regelbas, BESLUT)


@pytest.mark.parametrize("steg", ["rendera_docx", "_publicera"])
def test_avbrott_under_bygget_eller_vid_publiceringen_lamnar_ingen_version(
    kedja, signerad_regelbas_rot, signerad_regelbas, monkeypatch, steg
):
    historik_fore = historikens_kontrollsumma(kedja)

    def avbryt(*args, **kwargs):
        raise OSError("Strömavbrott.")

    monkeypatch.setattr(faststallmodul, steg, avbryt)
    with pytest.raises(OSError):
        faststall(kedja, signerad_regelbas_rot, signerad_regelbas, BESLUT)
    assert faststallda_versioner(kedja) == ()
    assert nasta_version(kedja) == 1
    assert historikens_kontrollsumma(kedja) == historik_fore
    monkeypatch.undo()
    assert faststall(kedja, signerad_regelbas_rot, signerad_regelbas, BESLUT).name == "v1"
    assert [mapp.name for mapp in (kedja / FASTSTALLDA).iterdir()] == ["v1"]


def test_andrat_tidigare_paket_stoppar_nasta_faststallelse(kedja, signerad_regelbas_rot, signerad_regelbas):
    mapp = faststall(kedja, signerad_regelbas_rot, signerad_regelbas, BESLUT)
    fil = mapp / "beslut.yaml"
    fil.write_text(fil.read_text(encoding="utf-8").replace("styrelsen", "ledningsgruppen"), encoding="utf-8")
    kor_granskning(kedja, signerad_regelbas, date(2026, 11, 16))
    with pytest.raises(FaststallelseFel, match="Version 1 stämmer inte med sitt manifest: Fil ändrad: beslut.yaml"):
        faststall(kedja, signerad_regelbas_rot, signerad_regelbas, SENARE_BESLUT)
    assert [version for version, _ in faststallda_versioner(kedja)] == [1]
    with pytest.raises(RiskanalysFel, match="Version 1 stämmer inte med sitt manifest"):
        versionshistorik(kedja)


def test_tidigare_paket_utan_manifest_stoppar_med_begripligt_fel(kedja, signerad_regelbas_rot, signerad_regelbas):
    mapp = faststall(kedja, signerad_regelbas_rot, signerad_regelbas, BESLUT)
    (mapp / "manifest.json").unlink()
    kor_granskning(kedja, signerad_regelbas, date(2026, 11, 16))
    with pytest.raises(FaststallelseFel, match="Version 1 stämmer inte med sitt manifest: Manifest saknas"):
        faststall(kedja, signerad_regelbas_rot, signerad_regelbas, SENARE_BESLUT)


def test_verifiera_okand_version(kedja):
    with pytest.raises(RiskanalysFel, match="Version 7 finns inte"):
        verifiera_version(kedja, 7)
```

- [ ] **Step 3: Kör testet för att se att det fallerar**

Run: `.venv/bin/pytest tester/enhet/test_faststall.py -v`
Expected: FAIL med `ImportError: cannot import name 'faststall' from 'riskanalys.faststallelse'`, eftersom modulen saknas. (Rättat 2026-10-10: testet importerar modulen från paketet, så felet är ImportError och inte ModuleNotFoundError.)

- [ ] **Step 4: Skriv `src/riskanalys/faststallelse/faststall.py`**

```python
"""Fastställelse: kontroll av kedjan och grindarna, låst paket och verifiering (spec 5.3 och 10).

Publiceringen är ett enda namnbyte. Allt, också versionshistoriken med det nya beslutet, skrivs i en
arbetsmapp som byter namn till v{n} när den är klar. Efter namnbytet skrivs ingenting mer, så en
fastställelse är antingen helt gjord eller inte gjord alls. Därför läses fastställelserna ur de låsta
paketen och inte ur byråns historikfil.
"""

import re
import shutil
from datetime import date
from pathlib import Path

from riskanalys.bedomning.korning import BEDOMNINGAR, aktualitetshinder, las_bedomning, las_bedomningsprofil
from riskanalys.dokument.rendering import faststalld_status, rendera_docx
from riskanalys.dokument.skrivning import UTKAST
from riskanalys.drift.historik import Handelse, Historik, historikens_kontrollsumma, las_historik, spara_historik
from riskanalys.faststallelse.grindar import FASTSTALLELSE, Faststallelseunderlag, hinder_for_faststallelse
from riskanalys.faststallelse.modeller import Beslut
from riskanalys.faststallelse.sakgranskning import las_sakgranskningar, spara_sakgranskningar
from riskanalys.fel import RiskanalysFel
from riskanalys.granskning.korning import GRANSKNING, andrade_kallor, las_granskning
from riskanalys.lagring.korningar import senaste_korning
from riskanalys.lagring.manifest import las_manifest, skriv_manifest, verifiera_manifest
from riskanalys.lagring.yamlfil import las_yaml, spara_yaml
from riskanalys.regelverk.laddning import regelbasens_kontrollsumma
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.urval import valj

FASTSTALLDA = "faststallda"
BESLUTSFIL = "beslut.yaml"
_VERSION = re.compile(r"^v(\d+)$")
_IGNORERA = shutil.ignore_patterns("__pycache__", ".DS_Store")


class FaststallelseFel(RiskanalysFel):
    """Villkoren för fastställelse är inte uppfyllda. hinder räknar upp vad som saknas."""

    def __init__(self, hinder: list[str]) -> None:
        super().__init__("Kan inte fastställa:\n" + "\n".join(f"- {rad}" for rad in hinder))
        self.hinder = hinder


def paketfil(version: int) -> str:
    return f"allman-riskbedomning-v{version}.docx"


def faststallda_versioner(byramapp: Path) -> tuple[tuple[int, Path], ...]:
    """Publicerade versioner i nummerordning. En arbetsmapp som aldrig bytte namn räknas inte."""
    rot = byramapp / FASTSTALLDA
    if not rot.is_dir():
        return ()
    versioner = [
        (int(traff.group(1)), mapp) for mapp in rot.iterdir() if mapp.is_dir() and (traff := _VERSION.match(mapp.name))
    ]
    return tuple(sorted(versioner))


def nasta_version(byramapp: Path) -> int:
    return max((version for version, _ in faststallda_versioner(byramapp)), default=0) + 1


def skadade_versioner(byramapp: Path) -> list[str]:
    """Tidigare versioner som inte stämmer med sitt manifest. Inget får läsas ur dem förrän de återställts."""
    return [
        f"Version {version} stämmer inte med sitt manifest: {rad} Återställ paketet från säkerhetskopian."
        for version, mapp in faststallda_versioner(byramapp)
        for rad in verifiera_manifest(mapp)
    ]


def versionshistorik(byramapp: Path) -> Historik:
    """Byråns registrerade utvärderingar och uppdateringar samt varje fastställd version, ur de låsta paketen.

    Paketen kontrolleras mot sina manifest först. Ett ändrat eller ofullständigt paket stoppar med ett fel.
    """
    skadade = skadade_versioner(byramapp)
    if skadade:
        raise RiskanalysFel(" ".join(skadade))
    historik = las_historik(byramapp)
    for version, mapp in faststallda_versioner(byramapp):
        historik = historik.med(_faststallelse(Beslut.model_validate(las_yaml(mapp / BESLUTSFIL)), version))
    return historik


def kedjehinder(byramapp: Path, regelbas_rot: Path, regelbas: Regelbas, granskningsmapp: Path) -> list[str]:
    """Skäl att inte lita på att tidigare versioner, granskningen, bedömningen, utkasten och regelbasen hör ihop."""
    skadade = skadade_versioner(byramapp)
    if skadade:
        return skadade
    andrade = andrade_kallor(byramapp, granskningsmapp)
    if andrade:
        return andrade
    metadata = las_manifest(granskningsmapp).metadata
    senaste = senaste_korning(byramapp, BEDOMNINGAR, f"bedom {byramapp.name}")
    if metadata["bedomning"] != senaste.name:
        return ["Granskningen hör inte till den senaste bedömningen. Kör 'riskanalys granska' igen."]
    redan = [
        f"Granskningen {granskningsmapp.name} är redan fastställd som version {version}. "
        "Gör en ny granskning för en ny version."
        for version, mapp in faststallda_versioner(byramapp)
        if las_manifest(mapp).metadata.get("granskning") == granskningsmapp.name
    ]
    historik = (
        ["Versionshistoriken har ändrats sedan granskningen. Kör 'riskanalys granska' igen."]
        if historikens_kontrollsumma(byramapp) != metadata["historik"]
        else []
    )
    regelbas_hinder = (
        [f"Regelbasen i {regelbas_rot} stämmer inte med den inlästa regelbasen."]
        if regelbasens_kontrollsumma(regelbas_rot) != regelbas.kontrollsumma
        else []
    )
    return [*aktualitetshinder(byramapp, senaste, regelbas), *redan, *historik, *regelbas_hinder]


def faststall(byramapp: Path, regelbas_rot: Path, regelbas: Regelbas, beslut: Beslut) -> Path:
    """Fastställer den senaste granskningen och publicerar den som en ny, låst version."""
    granskningsmapp = senaste_korning(byramapp, GRANSKNING, f"granska {byramapp.name}")
    hinder = kedjehinder(byramapp, regelbas_rot, regelbas, granskningsmapp)
    if hinder:
        raise FaststallelseFel(hinder)
    underlag = _underlag(byramapp, regelbas, granskningsmapp)
    hinder = hinder_for_faststallelse(underlag, beslut.datum)
    if hinder:
        raise FaststallelseFel(hinder)
    version = nasta_version(byramapp)
    pagaende = _tom_arbetsmapp(byramapp, version)
    _bygg_paket(pagaende, byramapp, regelbas_rot, granskningsmapp, underlag, beslut, version)
    skriv_manifest(pagaende, _metadata(underlag, beslut, version, granskningsmapp))
    return _publicera(pagaende, byramapp / FASTSTALLDA / f"v{version}")


def verifiera_version(byramapp: Path, version: int) -> list[str]:
    """Jämför ett fastställt paket med dess manifest. Tom lista betyder att paketet är oförändrat."""
    mapp = byramapp / FASTSTALLDA / f"v{version}"
    if not mapp.is_dir():
        raise RiskanalysFel(f"Version {version} finns inte i {byramapp / FASTSTALLDA}.")
    return verifiera_manifest(mapp)


def _faststallelse(beslut: Beslut, version: int) -> Handelse:
    return Handelse(
        datum=beslut.datum,
        typ=FASTSTALLELSE,
        beskrivning=f"Version {version} fastställd av {beslut.organ}.",
        version=version,
    )


def _underlag(byramapp: Path, regelbas: Regelbas, granskningsmapp: Path) -> Faststallelseunderlag:
    metadata = las_manifest(granskningsmapp).metadata
    bedomningsmapp = byramapp / BEDOMNINGAR / metadata["bedomning"]
    bedomning = las_bedomning(bedomningsmapp)
    dokument, fynd = las_granskning(granskningsmapp)
    return Faststallelseunderlag(
        regelbas=regelbas,
        urval=valj(regelbas, bedomning.regelpaket, bedomning.datum, bedomning.lan),
        profil=las_bedomningsprofil(bedomningsmapp),
        bedomning=bedomning,
        dokument=dokument,
        fynd=fynd,
        sakgranskningar=las_sakgranskningar(byramapp),
        historik=versionshistorik(byramapp),
        granskningsdatum=date.fromisoformat(metadata["datum"]),
    )


def _tom_arbetsmapp(byramapp: Path, version: int) -> Path:
    """En tom mapp att bygga paketet i. Rester av ett avbrutet försök är kopior och tas bort."""
    pagaende = byramapp / FASTSTALLDA / f".v{version}-pagaende"
    if pagaende.exists():
        shutil.rmtree(pagaende)
    pagaende.mkdir(parents=True)
    return pagaende


def _bygg_paket(
    pagaende: Path,
    byramapp: Path,
    regelbas_rot: Path,
    granskningsmapp: Path,
    underlag: Faststallelseunderlag,
    beslut: Beslut,
    version: int,
) -> None:
    """Kopierar underlaget till arbetsmappen och skriver beslut, versionshistorik och Word-fil där."""
    metadata = las_manifest(granskningsmapp).metadata
    shutil.copytree(byramapp / BEDOMNINGAR / metadata["bedomning"], pagaende / "bedomning")
    shutil.copytree(granskningsmapp, pagaende / "granskning")
    if metadata["utkast"]:
        shutil.copytree(byramapp / UTKAST / metadata["utkast"], pagaende / "utkast")
    shutil.copytree(regelbas_rot, pagaende / "regelbas", ignore=_IGNORERA)
    spara_sakgranskningar(pagaende, underlag.sakgranskningar)
    spara_historik(pagaende, underlag.historik.med(_faststallelse(beslut, version)))
    spara_yaml(pagaende / BESLUTSFIL, beslut.model_dump(mode="python"))
    statusrad = faststalld_status(beslut.organ, beslut.datum, version)
    rendera_docx(underlag.dokument, underlag.profil, statusrad, pagaende / paketfil(version))


def _metadata(underlag: Faststallelseunderlag, beslut: Beslut, version: int, granskningsmapp: Path) -> dict[str, str]:
    return {
        "typ": "faststallt_paket",
        "version": str(version),
        "organ": beslut.organ,
        "beslutsdatum": beslut.datum.isoformat(),
        "regelpaket": underlag.bedomning.regelpaket,
        "datum": underlag.bedomning.datum.isoformat(),
        "lan": underlag.bedomning.lan,
        "regelbas_version": underlag.regelbas.version,
        "regelbas_kontrollsumma": underlag.regelbas.kontrollsumma,
        "granskning": granskningsmapp.name,
    }


def _publicera(pagaende: Path, slutlig: Path) -> Path:
    """Det enda steget som gör versionen synlig. Ett namnbyte inom samma mapp sker helt eller inte alls."""
    pagaende.rename(slutlig)
    return slutlig
```

- [ ] **Step 5: Kör testet**

Run: `.venv/bin/pytest tester/enhet/test_faststall.py -v`
Expected: alla tester passerar.

- [ ] **Step 6: Skriv det felande testet `tester/enhet/test_faststall_kommando.py`**

```python
import pytest

from riskanalys.cli import main
from riskanalys.faststallelse.faststall import FASTSTALLDA

BESLUT = ["--organ", "styrelsen", "--datum", "2026-11-15", "--namn", "Testa Testsson"]


def test_faststall_och_verifiera(kedja, signerad_regelbas_rot, capsys):
    assert main(["faststall", "testbyra", *BESLUT, "--regelbas", str(signerad_regelbas_rot)]) == 0
    utskrift = capsys.readouterr().out
    assert "v1 är fastställd av styrelsen 2026-11-15" in utskrift
    assert "riskanalys verifiera testbyra 1" in utskrift
    assert "Nästa genomgång senast 2027-11-01." in utskrift
    assert main(["verifiera", "testbyra", "1"]) == 0
    assert "Version 1 stämmer med manifestet." in capsys.readouterr().out


def test_verifiera_rapporterar_andrad_fil_med_felkod_2(kedja, signerad_regelbas_rot, capsys):
    main(["faststall", "testbyra", *BESLUT, "--regelbas", str(signerad_regelbas_rot)])
    (kedja / FASTSTALLDA / "v1" / "beslut.yaml").write_text("organ: någon annan\n", encoding="utf-8")
    capsys.readouterr()
    assert main(["verifiera", "testbyra", "1"]) == 2
    utskrift = capsys.readouterr().out
    assert "- Fil ändrad: beslut.yaml" in utskrift
    assert "Återställ versionen från säkerhetskopian" in utskrift


def test_hinder_visas_som_lista_utan_stackspar(osignerad_kedja, capsys):
    assert main(["faststall", "testbyra", *BESLUT]) == 1
    fel = capsys.readouterr().err
    assert fel.startswith("Fel: Kan inte fastställa:")
    assert (
        "- Kravet KRV-LSF-001 (2 kap. 1 §) är inte verifierat av sakkunnig i sin nuvarande lydelse (status ej_granskad)."
        in fel
    )
    assert "Traceback" not in fel


def test_faststall_kraver_beslutsuppgifter(kedja, capsys):
    with pytest.raises(SystemExit):
        main(["faststall", "testbyra", "--organ", "styrelsen"])
    assert "--datum" in capsys.readouterr().err
```

- [ ] **Step 7: Skriv `src/riskanalys/kommandon/faststall_kommando.py`**

```python
"""riskanalys faststall och verifiera"""

import argparse
from typing import Any

from riskanalys.faststallelse.faststall import faststall, verifiera_version, versionshistorik
from riskanalys.faststallelse.modeller import Beslut
from riskanalys.kommandon import datumargument, ladda_giltig_regelbas, regelbasargument
from riskanalys.lagring.datamapp import befintlig_byramapp


def lagg_till(underparsers: Any) -> None:
    fastst = underparsers.add_parser("faststall", help="Fastställ den senaste granskade versionen och lås paketet.")
    fastst.add_argument("byra")
    fastst.add_argument("--organ", required=True, help='Organet som beslutat, till exempel "styrelsen".')
    fastst.add_argument("--datum", required=True, type=datumargument, help="Beslutsdatum, ÅÅÅÅ-MM-DD.")
    fastst.add_argument("--namn", required=True, help="Namn på den som undertecknar beslutet.")
    fastst.add_argument("--roll", default="FfR", help="Rollen hos den som undertecknar. Standard är FfR.")
    regelbasargument(fastst)
    fastst.set_defaults(kor=kor_faststall)

    verifiering = underparsers.add_parser("verifiera", help="Kontrollera ett fastställt paket mot dess manifest.")
    verifiering.add_argument("byra")
    verifiering.add_argument("version", type=int, help="Versionsnummer, till exempel 1.")
    verifiering.set_defaults(kor=kor_verifiera)


def kor_faststall(args: argparse.Namespace) -> int:
    byramapp = befintlig_byramapp(args.byra)
    regelbas = ladda_giltig_regelbas(args.regelbas)
    beslut = Beslut(organ=args.organ, datum=args.datum, namn=args.namn, roll=args.roll)
    mapp = faststall(byramapp, args.regelbas, regelbas, beslut)
    version = mapp.name.removeprefix("v")
    print(f"{mapp.name} är fastställd av {beslut.organ} {beslut.datum.isoformat()} och låst i {mapp}.")
    print(f"Kontrollera paketet när som helst med 'riskanalys verifiera {args.byra} {version}'.")
    print(f"Nästa genomgång senast {versionshistorik(byramapp).nasta_genomgang()}.")
    return 0


def kor_verifiera(args: argparse.Namespace) -> int:
    fel = verifiera_version(befintlig_byramapp(args.byra), args.version)
    if fel:
        print(f"Version {args.version} stämmer inte med manifestet:")
        for rad in fel:
            print(f"- {rad}")
        print("Återställ versionen från säkerhetskopian och kör 'riskanalys verifiera' igen.")
        return 2
    print(f"Version {args.version} stämmer med manifestet.")
    return 0
```

- [ ] **Step 8: Registrera kommandot i `src/riskanalys/cli.py`**

Lägg till `faststall_kommando` i importen från `riskanalys.kommandon` och sist i `KOMMANDON`:

```python
from riskanalys.kommandon import (
    bedom_kommando,
    drift_kommando,
    exportera_kommando,
    faststall_kommando,
    granska_kommando,
    profil_kommando,
    regelbas_kommando,
    sakgranska_kommando,
    skriv_kommando,
)

KOMMANDON = [
    regelbas_kommando,
    profil_kommando,
    drift_kommando,
    bedom_kommando,
    skriv_kommando,
    granska_kommando,
    exportera_kommando,
    sakgranska_kommando,
    faststall_kommando,
]
```

- [ ] **Step 9: Kör testerna**

Run: `.venv/bin/pytest tester/enhet/test_faststall.py tester/enhet/test_faststall_kommando.py -v`
Expected: alla tester passerar.

- [ ] **Step 10: Commit**

```bash
git add src/riskanalys/faststallelse/faststall.py src/riskanalys/kommandon/faststall_kommando.py src/riskanalys/cli.py tester/conftest.py tester/enhet/test_faststall.py tester/enhet/test_faststall_kommando.py
git commit -m "feat: fastställelse med låst paket och kommandona faststall och verifiera"
```

---

### Task 22: Typfall genom hela kedjan, återställningsprov och dokumentation

**Files:**
- Test: `tester/typfall/test_tunn_kedja.py`
- Modify: `README.md`, `docs/STATUS.md`, `docs/research/06-ai-och-teknik.md`

**Interfaces:**
- Consumes: alla kommandon via `riskanalys.cli.main`, fixturerna `datamapp`, `signerad_regelbas_rot`, `real_varden_text` och `testsvarsfil`, samt `FASTSTALLDA`, `las_manifest`, `verifiera_manifest` och `ladda_regelbas`.
- Produces: typfallstestet som är M1:s klarkriterium (spec 15: "Kedjan körs i ett typfallstest, och `riskanalys verifiera` godkänner paketet"), återställningsprovet (spec 5.3 och 16) och sex regressionstester för felen som Codex reproducerade 2026-10-09: ändrad paragraftext efter sakkunniggranskning, byte av ansvarig person efter sakgranskning, ändrat eller ofullständigt tidigare paket, och tidigare paket med skadat manifest (trasig JSON eller saknade fält).

Typfallet kör varje steg som en användare gör, i rätt ordning, via kommandoraden. Det körs två gånger: med en signerad kopia av regelbasen, där fastställelsen ska lyckas, och med repots regelbas, där fastställelsen ska stoppas eftersom ingen sakkunnig har granskat kraven. Återställningsprovet kopierar det fastställda paketet till en säkerhetskopia, återställer det i en tom datamapp som om det vore en ny dator och verifierar det där.

Detta typfall visar M1:s tekniska kedja. Tillsynsfallen i `docs/research/typfall/tillsyn-2026.json` är separat underlag för M2–M5 och M7 enligt spec 16.3; de 17 förväntade fynden får inte redovisas som passerande tester när bara denna kedja har körts.

- [ ] **Step 1: Skriv testet `tester/typfall/test_tunn_kedja.py`**

```python
"""Typfall för M1: hela kedjan via kommandoraden med syntetiska uppgifter (spec 15).

Filen innehåller också regressionstester för tre brister som Codex reproducerade 2026-10-09.
De går genom kommandoraden, så att de kan köras mot planens kod både före och efter rättningen.
"""

import shutil

import pytest
import yaml

from riskanalys.cli import main
from riskanalys.faststallelse.faststall import FASTSTALLDA
from riskanalys.lagring.manifest import las_manifest, verifiera_manifest
from riskanalys.regelverk.laddning import ladda_regelbas, lydelsetextens_kontrollsumma

NY = ["ny", "testbyra", "--regelpaket", "RP-RED-VG", "--lan", "Västra Götaland", "--datum", "2026-11-01"]
BESLUT = ["--organ", "styrelsen", "--datum", "2026-11-15", "--namn", "Testa Testsson"]
SENARE_BESLUT = ["--organ", "styrelsen", "--datum", "2026-11-20", "--namn", "Testa Testsson"]
LYDELSE = "LYD-LSF-2-3-2024-07-01"
GODKANN = ["--godkann", "--namn", "Testa Testsson", "--datum", "2026-11-03"]


def _kor_fram_till_faststallelse(regelbasargument, real_varden_text, testsvarsfil, capsys):
    """Kör varje steg som en användare gör och kontrollerar att det lyckas."""
    assert main([*NY, *regelbasargument]) == 0
    for falt_id, text in real_varden_text:
        bekraftelse = ["bekrafta", "testbyra", falt_id, text, "--kalla", "Syntetiskt testfall", "--datum", "2026-10-01"]
        assert main([*bekraftelse, *regelbasargument]) == 0
    capsys.readouterr()
    assert main(["profil", "testbyra", *regelbasargument]) == 0
    assert "Kritiska uppgifter som saknas: 0" in capsys.readouterr().out
    assert main(["bedom", "testbyra", *regelbasargument]) == 0
    assert main(["skriv", "testbyra", "--leverantor", "test", "--testsvar", str(testsvarsfil), *regelbasargument]) == 0
    assert main(["utvardera", "testbyra", "--beskrivning", "Första riskbedömningen.", "--datum", "2026-11-01"]) == 0
    assert main(["granska", "testbyra", "--datum", "2026-11-02", *regelbasargument]) == 0
    assert main(["exportera", "testbyra", "--utkast", "--datum", "2026-11-02"]) == 0
    capsys.readouterr()
    assert main(["sakgranska", "testbyra"]) == 0
    avsnitt = [rad.split()[0] for rad in capsys.readouterr().out.splitlines() if rad.startswith("D-ARB.")]
    assert avsnitt == ["D-ARB.1", "D-ARB.3", "D-ARB.4", "D-ARB.5", "D-ARB.6.1", "D-ARB.10"]
    for avsnitt_id in avsnitt:
        assert main(["sakgranska", "testbyra", "--avsnitt", avsnitt_id, *GODKANN]) == 0


def test_hela_kedjan_med_signerad_regelbas(datamapp, signerad_regelbas_rot, real_varden_text, testsvarsfil, capsys):
    regelbasargument = ["--regelbas", str(signerad_regelbas_rot)]
    _kor_fram_till_faststallelse(regelbasargument, real_varden_text, testsvarsfil, capsys)
    assert main(["faststall", "testbyra", *BESLUT, *regelbasargument]) == 0
    assert main(["verifiera", "testbyra", "1"]) == 0


def test_repots_regelbas_kan_inte_faststallas_utan_sakkunnig(datamapp, real_varden_text, testsvarsfil, capsys):
    _kor_fram_till_faststallelse([], real_varden_text, testsvarsfil, capsys)
    capsys.readouterr()
    assert main(["faststall", "testbyra", *BESLUT]) == 1
    assert "inte verifierat av sakkunnig" in capsys.readouterr().err
    assert not (datamapp / "testbyra" / FASTSTALLDA).exists()


def test_aterstallningsprov(
    datamapp, tmp_path, monkeypatch, signerad_regelbas_rot, real_varden_text, testsvarsfil, capsys
):
    """Ett fastställt paket återställs från säkerhetskopia i en tom datamapp och verifieras (spec 5.3 och 16)."""
    regelbasargument = ["--regelbas", str(signerad_regelbas_rot)]
    _kor_fram_till_faststallelse(regelbasargument, real_varden_text, testsvarsfil, capsys)
    assert main(["faststall", "testbyra", *BESLUT, *regelbasargument]) == 0
    sakerhetskopia = tmp_path / "sakerhetskopia" / "v1"
    shutil.copytree(datamapp / "testbyra" / FASTSTALLDA / "v1", sakerhetskopia)

    ny_datamapp = tmp_path / "ny_dator" / "data"
    monkeypatch.setenv("RISKANALYS_DATA", str(ny_datamapp))
    aterstalld = ny_datamapp / "testbyra" / FASTSTALLDA / "v1"
    shutil.copytree(sakerhetskopia, aterstalld)
    capsys.readouterr()
    assert main(["verifiera", "testbyra", "1"]) == 0
    assert "Version 1 stämmer med manifestet." in capsys.readouterr().out
    assert verifiera_manifest(aterstalld) == []
    regelbas = ladda_regelbas(aterstalld / "regelbas")
    assert regelbas.kontrollsumma == las_manifest(aterstalld).metadata["regelbas_kontrollsumma"]


def _skriv_yaml(fil, data):
    fil.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _andra_paragraftext(rot, lydelse_id, ny_text):
    """Ändrar en paragraftext och dess textkontrollsumma, så att regelbasen fortfarande går att läsa in."""
    (rot / "lydelsetexter" / f"{lydelse_id}.txt").write_text(ny_text, encoding="utf-8")
    fil = rot / "lydelser.yaml"
    lydelser = yaml.safe_load(fil.read_text(encoding="utf-8"))
    summa = lydelsetextens_kontrollsumma(ny_text)
    _skriv_yaml(fil, [{**post, "text_kontrollsumma": summa} if post["id"] == lydelse_id else post for post in lydelser])


def _signera_om(rot, summor):
    """Det en sakkunnig gör efter ny granskning: skriver in de nya summorna."""
    for fil in (rot / "krav").glob("*.yaml"):
        poster = yaml.safe_load(fil.read_text(encoding="utf-8"))
        _skriv_yaml(fil, [{**post, "sakkunnig": {**post["sakkunnig"], "kontrollsumma": summor[post["id"]]}} for post in poster])
    for fil in (rot / "regelpaket").glob("*.yaml"):
        paket = yaml.safe_load(fil.read_text(encoding="utf-8"))
        karta = paket["paragrafkarta"]
        ny_signatur = {**karta["sakkunnig"], "kontrollsumma": summor[f"{paket['id']} paragrafkarta"]}
        _skriv_yaml(fil, {**paket, "paragrafkarta": {**karta, "sakkunnig": ny_signatur}})


def test_regression_andrad_paragraftext_kraver_ny_sakkunniggranskning(datamapp, signerad_regelbas_rot, capsys):
    """Fel A: ett godkänt krav fortsatte att gälla när den paragraf det bygger på fick ny text."""
    regelbasargument = ["--regelbas", str(signerad_regelbas_rot)]
    _andra_paragraftext(signerad_regelbas_rot, LYDELSE, "Verksamhetsutövaren ska utvärdera riskbedömningen vartannat år.")
    assert main(["regelbas", "validera", *regelbasargument]) == 1
    assert "KRV-LSF-006: innehållet har ändrats efter sakkunniggranskningen." in capsys.readouterr().err
    assert main([*NY, *regelbasargument]) == 1
    assert not (datamapp / "testbyra").exists()
    capsys.readouterr()
    assert main(["regelbas", "summor", *regelbasargument]) == 0
    summor = dict(rad.rsplit(" ", 1) for rad in capsys.readouterr().out.splitlines())
    _signera_om(signerad_regelbas_rot, summor)
    assert main(["regelbas", "validera", *regelbasargument]) == 0


def test_regression_byte_av_ansvarig_person_kraver_ny_sakgranskning(
    datamapp, signerad_regelbas_rot, real_varden_text, testsvarsfil, capsys
):
    """Fel B: godkännandet av mallen med {roll:FfR} följde med när ett annat namn sattes in vid exporten."""
    regelbasargument = ["--regelbas", str(signerad_regelbas_rot)]
    _kor_fram_till_faststallelse(regelbasargument, real_varden_text, testsvarsfil, capsys)
    bekraftelse = ["bekrafta", "testbyra", "P-ROLL.ffr_namn", "Ny Person", "--kalla", "Styrelseprotokoll"]
    assert main([*bekraftelse, "--datum", "2026-11-04", *regelbasargument]) == 0
    assert main(["bedom", "testbyra", *regelbasargument]) == 0
    assert main(["skriv", "testbyra", "--leverantor", "test", "--testsvar", str(testsvarsfil), *regelbasargument]) == 0
    assert main(["granska", "testbyra", "--datum", "2026-11-05", *regelbasargument]) == 0
    capsys.readouterr()
    assert main(["faststall", "testbyra", *BESLUT, *regelbasargument]) == 1
    assert "Avsnitt D-ARB.1 är inte sakgranskat i nuvarande lydelse." in capsys.readouterr().err
    assert not (datamapp / "testbyra" / FASTSTALLDA).exists()


def test_regression_andrat_tidigare_paket_foljer_inte_med(
    datamapp, signerad_regelbas_rot, real_varden_text, testsvarsfil, capsys
):
    """Fel C: ett ändrat beslut i v1 lästes in i versionshistoriken och följde med till v2."""
    regelbasargument = ["--regelbas", str(signerad_regelbas_rot)]
    _kor_fram_till_faststallelse(regelbasargument, real_varden_text, testsvarsfil, capsys)
    assert main(["faststall", "testbyra", *BESLUT, *regelbasargument]) == 0
    beslut = datamapp / "testbyra" / FASTSTALLDA / "v1" / "beslut.yaml"
    beslut.write_text(beslut.read_text(encoding="utf-8").replace("styrelsen", "ledningsgruppen"), encoding="utf-8")
    assert main(["granska", "testbyra", "--datum", "2026-11-16", *regelbasargument]) == 0
    capsys.readouterr()
    assert main(["faststall", "testbyra", *SENARE_BESLUT, *regelbasargument]) == 1
    assert "Version 1 stämmer inte med sitt manifest: Fil ändrad: beslut.yaml" in capsys.readouterr().err
    assert not (datamapp / "testbyra" / FASTSTALLDA / "v2").exists()


def test_regression_ofullstandigt_tidigare_paket_ger_begripligt_fel(
    datamapp, signerad_regelbas_rot, real_varden_text, testsvarsfil, capsys
):
    """Fel C: ett tidigare paket utan manifest gav en krasch i stället för ett meddelande."""
    regelbasargument = ["--regelbas", str(signerad_regelbas_rot)]
    _kor_fram_till_faststallelse(regelbasargument, real_varden_text, testsvarsfil, capsys)
    assert main(["faststall", "testbyra", *BESLUT, *regelbasargument]) == 0
    (datamapp / "testbyra" / FASTSTALLDA / "v1" / "manifest.json").unlink()
    assert main(["granska", "testbyra", "--datum", "2026-11-16", *regelbasargument]) == 0
    capsys.readouterr()
    assert main(["faststall", "testbyra", *SENARE_BESLUT, *regelbasargument]) == 1
    assert "Version 1 stämmer inte med sitt manifest: Manifest saknas" in capsys.readouterr().err


@pytest.mark.parametrize("innehall", ["{inte json", "{}"], ids=["trasig_json", "saknade_falt"])
def test_regression_skadat_manifest_i_tidigare_paket_ger_begripligt_fel(
    datamapp, signerad_regelbas_rot, real_varden_text, testsvarsfil, capsys, innehall
):
    """Codex 2026-10-09: ett skadat manifest gav en krasch i både verifiera och faststall."""
    regelbasargument = ["--regelbas", str(signerad_regelbas_rot)]
    _kor_fram_till_faststallelse(regelbasargument, real_varden_text, testsvarsfil, capsys)
    assert main(["faststall", "testbyra", *BESLUT, *regelbasargument]) == 0
    (datamapp / "testbyra" / FASTSTALLDA / "v1" / "manifest.json").write_text(innehall, encoding="utf-8")
    capsys.readouterr()
    assert main(["verifiera", "testbyra", "1"]) == 2
    utskrift = capsys.readouterr().out
    assert "är skadat och kan inte läsas." in utskrift
    assert "Återställ versionen från säkerhetskopian" in utskrift
    assert main(["granska", "testbyra", "--datum", "2026-11-16", *regelbasargument]) == 0
    capsys.readouterr()
    assert main(["faststall", "testbyra", *SENARE_BESLUT, *regelbasargument]) == 1
    fel = capsys.readouterr().err
    assert "Version 1 stämmer inte med sitt manifest: Manifestet i" in fel
    assert "Återställ paketet från säkerhetskopian." in fel
    assert not (datamapp / "testbyra" / FASTSTALLDA / "v2").exists()
```

- [ ] **Step 2: Kör typfallet**

Run: `.venv/bin/pytest tester/typfall -v`
Expected: 9 passed: tre typfall och sex regressionstester. Ingen ny programkod behövs. Fallerar ett steg är det ett fel i en tidigare task: rätta där, med ett regressionstest, och kör om.

- [ ] **Step 3: Kör hela testsviten och kommandot för hand**

Run:
```bash
.venv/bin/pytest -v
.venv/bin/riskanalys regelbas validera
```
Expected: alla tester passerar och livetestet räknas som avvalt. Regelbasen är giltig, version 0.1.0.

- [ ] **Step 4: Uppdatera `README.md`**

Ersätt statusraden

```markdown
> **Status:** designfas. Ingen programkod ännu. Se [docs/STATUS.md](docs/STATUS.md).
```

med

```markdown
> **Status:** etapp M1 (tunn kedja) är byggd och körs med syntetiska uppgifter. Regelbasen är inte sakkunniggranskad, så inget kan fastställas för en riktig byrå än. Se [docs/STATUS.md](docs/STATUS.md).
```

Lägg sedan till följande avsnitt efter avsnittet "Princip i korthet":

````markdown
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
````

- [ ] **Step 5: Uppdatera `docs/STATUS.md`**

1. Sätt **Fas** till "M1 klar. Nästa etapp är M2 (regelbas v1 och juridisk granskning)."
2. Sätt status för raden "Etapp M0 (grund) och M1 (tunn kedja)" till "Klara. Typfallet och återställningsprovet passerar." Ta bort meningen om att implementationen inte är påbörjad i raden "Senaste kodblocksgranskningen".
3. Lägg till följande rader sist i tabellen över beslut, med dagens datum:

| Beslut | Motivering |
|---|---|
| Word-export med python-docx i M1. PDF skjuts till M4. | Word räcker för sakgranskning och fastställelse i M1. PDF-konvertering prövas tillsammans med användningsprovet. |
| `faststall` tar `--organ`, `--datum`, `--namn` och `--roll` i stället för en sammanslagen `--beslut` | Spec 10 kräver namn, roll och datum. Separata argument behöver inte tolkas. |

4. Uppdatera **Nästa steg** utan att skriva om listan. Ta bort punkterna om att granska implementeringsplanen och bygga M0 och M1, eftersom de är klara. Lägg först till: "Sakkunniggranskning av kraven och paragrafkartan i M2." **Behåll övriga punkter**, särskilt att en sakkunnig ska bekräfta eller revidera tillsynsfallens facitutkast mot de lokalt bevarade originalen och att granskningen prövas med fallen i M3 enligt spec 16.3. Numrera om listan.

- [ ] **Step 6: Uppdatera `docs/research/06-ai-och-teknik.md`**

Ersätt raden för PDF i tabellen över tekniska val:

```markdown
| PDF | Konvertering från Word (till exempel LibreOffice i kommandoradsläge) | Bestäms i etapp M1, där den första testexporten görs |
```

med

```markdown
| PDF | Konvertering från Word (till exempel LibreOffice i kommandoradsläge) | Skjuts till etapp M4. M1 exporterar Word med python-docx. |
```

- [ ] **Step 7: Kör hela testsviten igen**

Run: `.venv/bin/pytest -v`
Expected: alla tester passerar.

- [ ] **Step 8: Commit**

```bash
git add tester/typfall/test_tunn_kedja.py README.md docs/STATUS.md docs/research/06-ai-och-teknik.md
git commit -m "test: typfall genom hela kedjan och återställningsprov; docs: M1 klar"
```

M1 är klar när typfallet och återställningsprovet passerar och `riskanalys verifiera` godkänner paketet.

---

## Genomförande 2026-10-10

Planen genomfördes med Superpowers executing-plans i repots arbetskatalog. Vid genomförandet gjordes inga commits, på användarens dåvarande begäran. Användaren har därefter, 2026-10-10, bett Codex att committa och pusha det granskade bygget på `codex/m0-m1`. Koden fördes över ur planens kodblock steg för steg, med varje test skrivet och kört före koden. Efter Task 22 var `src/`, `tester/`, `regelbas/`, `pyproject.toml`, `AGENTS.md` och `CLAUDE.md` byte för byte lika med planens kodblock, och hela sviten gav 452 passerar och ett bortvalt livetest.

### Avvikelser från planens text

| Var | Avvikelse | Skäl |
|---|---|---|
| Alla tasks | Commit-stegen kördes inte. | Användaren bad uttryckligen om ingen commit eller push. |
| Task 21 Step 3 | Expected-raden rättad: testet fallerar med `ImportError`, inte `ModuleNotFoundError`. | Testet importerar modulen från paketet. Orsaken är densamma: modulen saknas. |
| Task 22 Step 4 | README-exemplet anger `--testsvar FIL` för testleverantören och att varje avsnitt ska sakgranskas. | `skriv --leverantor test` kräver en svarsfil, och fastställelsen kräver sakgranskning av alla avsnitt. |

### Rättelser efter slutgranskningen

En fristående granskare (Claude Opus) granskade hela implementationen mot planen och specen. Inga kritiska fynd. Sex viktiga fynd rättades, vart och ett med ett test som fallerade före rättningen. **Koden i filerna nedan skiljer sig därför från planens kodblock.** Provkörningsverktyget bygger fortfarande planens ursprungliga kod.

| Fynd | Rättelse | Filer | Tester |
|---|---|---|---|
| 1. Risknivåer i AI-texten kunde saknas eller stå i en form som valideringen inte kände igen ("låg kvarstående risk"), och sakgranskaren såg inte motorns nivåer. | Valideringen kräver att risken för terrorfinansiering och den kvarstående risken anges (den inneboende krävdes redan), känner igen entydiga former med nivån före subjektet, efter kolon, "kvarstår en låg risk" och "bedömer … som låg", och `sakgranska --avsnitt` visar motorns nivåer för riskavsnitt. Inget motorskrivet stycke läggs till i dokumentet. | `dokument/validering.py`, `kommandon/sakgranska_kommando.py`, `granskning/korning.py` | `test_validering_utkast.py`, `test_sakgranska_kommando.py` |
| 2. En okänd rollplatshållare (`{roll:VD}`) blev `[VERIFIERA: VD]` i ett fastställt dokument. | Valideringen vägrar okända roller och egna varianter av `[VERIFIERA]`. Granskningen och grinden prövar texten så som den skrivs ut. | `dokument/rendering.py`, `dokument/validering.py`, `granskning/kontroller.py`, `faststallelse/grindar.py` | `test_validering_utkast.py`, `test_granskning.py`, `test_grindar.py` |
| 3. `.DS_Store` från Finder gjorde ett oförändrat paket ogiltigt och stoppade nästa fastställelse. | Systemfiler (`.DS_Store`, `._*`, `Icon\r`, `.localized`, `Thumbs.db`, `desktop.ini`) ingår inte i manifest. | `lagring/manifest.py` | `test_manifest.py` |
| 4. Ett manifest som saknade en uppgift i metadata gav `KeyError` och stackspår (Review Focus 13). | `manifestets_metadata()` och `granskningens_metadata()` ger ett svenskt fel med instruktion om återställning. Alla uppslag använder dem. | `lagring/manifest.py`, `granskning/korning.py`, `bedomning/korning.py`, `faststallelse/faststall.py`, `dokument/export.py` | `test_faststall_kommando.py` |
| 5. Profilens värden prövades inte mot fältregistret. Ett handredigerat värde kunde krascha `bedom` eller i tysthet ändra risknivån. | `kontrollera_profil()` prövar varje bekräftat värde innan motorn körs. En profil som inte följer schemat ger ett svenskt fel. | `profil/hantering.py`, `profil/lagring.py`, `bedomning/korning.py` | `test_bedomning_korning.py` |
| 6. En datamapp i repot skriven med annat skiftläge (`/users/...`) godtogs på macOS. | Spärren jämför med `os.path.samefile` mot närmaste befintliga mapp i sökvägen. | `lagring/datamapp.py` | `test_lagring_grund.py` |

Codex granskade därefter implementationen och fann två brister till. De rättades på samma sätt, med tester som fallerade före rättningen:

| Fynd | Rättelse | Filer | Tester |
|---|---|---|---|
| 7. AI:ns öppna frågor (`oklarheter`) visades bara i utkastets åtgärdslista. Granskningen gav noll fynd, och paketet kunde fastställas. | Varje öppen fråga blir ett granskningsfynd (spårbarhet, hög, ska-krav) som stoppar fastställelsen tills uppgiften är bekräftad och kedjan körts om. `sakgranska --avsnitt` visar frågan. Utkastets åtgärdslista visar frågan både som fynd och som fråga. | `granskning/kontroller.py`, `granskning/korning.py`, `kommandon/sakgranska_kommando.py` | `test_granskning_korning.py`, `test_faststall.py`, `test_sakgranska_kommando.py` |
| 8. En handredigerad profil godtogs med status bekräftad utan källa, datum eller bekräftare, och ej tillämplig utan motivering. | `belaggsbrister()` kräver beläggen för varje status. `bedom` stoppar, och grindens villkor 1 ger ett hinder. | `profil/hantering.py`, `faststallelse/grindar.py` | `test_bedomning_korning.py`, `test_grindar.py` |

Hela sviten efter rättelserna: 495 passerar, ett livetest bortvalt. Kommandokedjan, återställningsprovet och ett prov med `.DS_Store` i paketet kördes om och gav väntat utfall.

### Mindre punkter till senare etapper

Slutgranskningen förde också fram tretton mindre punkter. De är inte rättade. Etappen är ett förslag.

| | Punkt | Förslag |
|---|---|---|
| a | En sakgranskning kan dateras före granskningen. | M4 |
| b | Framtida datum godtas, och `--datum` för `granska` och `utvardera` jämförs inte med när körningen faktiskt gjordes. | M4 |
| c | `utvardera --beskrivning ""` godtas, fast spec 13.1 kräver en motivering. | M4 |
| d | FfR markerad som ej tillämplig ger alltid `[VERIFIERA]` i D-ARB.1. `P-ORG.namn` är inte kritisk men stoppar fastställelsen utan att nämnas. | M2 |
| e | Argparse-fel visas på engelska, till exempel för `30 %` utan citattecken. Andelen "1" tolkas som 100 %. | M4 |
| f | Manifestet sparar git-commit utan markering för ej committade ändringar. | M2 |
| g | Ingen fsync före publiceringens namnbyte. Profil, historik och sakgranskningar skrivs på plats. | M4 |
| h | Ett skadat körningsmanifest ger i `faststall` ett fel utan instruktion om återställning, och ett skadat gammalt utkastmanifest stoppar `granska`. | M2 |
| i | Ingen varning när en lydelse träder i kraft mellan bedömningens datum och beslutsdatum. Blir verkligt med PTL 1 kap. 2 § 2026-11-20. | M2 |
| j | Körningsmappar namnges efter lokal tid, så ett byte till vintertid kan ge fel "senaste" körning. | M2 |
| k | Spärren mot repot och standardregelbasen förutsätter en redigerbar installation (`pip install -e`). | M4 |
| l | Andra stackspår: trasig `historik.yaml` eller `sakgranskningar.yaml`, fel teckenkodning i testsvar och lydelsetexter, villkor där `falt` eller `op` inte är text. | M2 |
| m | AI:ns oklarheter valideras inte, så `saknad_uppgift` kan vara ett fält som inte finns. | M3 |

### Verifiering

- Hela sviten utan `ANTHROPIC_API_KEY`: 495 passerar, ett livetest bortvalt.
- Codex två scenarier körda via kommandoraden efter rättelsen: en öppen AI-fråga ger ett fynd, syns i `sakgranska` och stoppar `faststall` utan att något paket skapas; en profil med bekräftelse utan belägg och ej tillämplig utan motivering stoppar `bedom` med ett svenskt meddelande.
- Kommandokedjan `ny → bekrafta → bedom → skriv → utvardera → granska → exportera → sakgranska → faststall → verifiera` körd för hand med syntetiska uppgifter och testleverantören, i en datamapp utanför repot med mellanslag och å, ä, ö. Med en signerad testkopia av regelbasen fastställdes och verifierades version 1. Med repots regelbas stoppades fastställelsen: sex krav och paragrafkartan är inte sakkunniggranskade, och nio paragrafer är inte hanterade.
- Återställningsprov: paketet kopierat till en säkerhetskopia, återställt i en tom datamapp och verifierat. En ändrad `beslut.yaml` i kopian rapporterades.
- Regressionstesterna i Task 22 prövade genom att felen återinfördes i en kopia av koden: ändrad paragraftext, byte av ansvarig person, ändrat och ofullständigt tidigare paket och skadat manifest fångades alla.
- `verifiera_tillsynsmaterial.py`: 2 fall, 17 förväntade fynd, 5 kontrollvarianter, 14 dokument, 79 original och 173 kontrollsummor stämmer. Facitet är fortfarande inte sakkunniggranskat, och M1:s tester prövar inte de 17 fynden.
- Inte kört: livetestet mot Claude (kostar pengar), täckningsmätning (`pytest-cov` ingår inte i beroendena) och PDF (skjuten till M4).
