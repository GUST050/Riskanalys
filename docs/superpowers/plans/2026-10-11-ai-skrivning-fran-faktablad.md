# AI-skrivning från faktablad – implementeringsplan

> **För agentic workers:** OBLIGATORISK DELSKILL: använd superpowers:subagent-driven-development (rekommenderas) eller superpowers:executing-plans för att genomföra planen uppgift för uppgift. Stegen använder kryssrutor (`- [ ]`) för uppföljning.

**Goal:** AI skriver den analyserande texten i varje tjänsts analysdelar från ett kontrollerat faktablad, medan koden äger tal, nivåer, låsta stycken och format, så att utkastet blir läsbart utan att AI fattar beslut.

**Architecture:** Del A gör kontrollerna och de kodskrivna meningarna rätt i dagens flöde med ett anrop per tjänst. Del B inför faktablad, platshållare, en gemensam systemprompt med delmoduler, ett anrop per analysdel (design B), delkontroller, mallreserv och en ny granskningsgrind som bygger om tjänsteavsnittet ur maskinellt validerade delresultat. Allt är experimentellt tills sakkunnigutvärderingen i spec 8.4.8 är genomförd.

**Tech Stack:** Python 3.12+, Pydantic, Anthropic Python-SDK (`client.beta.messages`), python-docx, pytest. Inga nya beroenden.

**Spec:** `docs/superpowers/specs/2026-10-08-riskanalys-design.md` revision 17, §8.2–8.4. Underlag: `docs/research/12-promptdesign-ai-skrivning.md`.

## Global Constraints

- AI fattar inga beslut. Risknivåer, poäng och regler kommer från regelbasen och riskmotorn. AI skriver bara text i ett låst schema (AGENTS.md regel 1).
- Inga personuppgifter till AI. AI-underlag byggs bara ur tillåtelselistan i `regelbas/tillatelselistor.yaml`. Personer skrivs som `{roll:FfR}` (regel 2).
- Byrådata aldrig i repot; prov använder bara syntetiska uppgifter (regel 3).
- Regelbasen ändras bara med källa; skalor, gränser och poäng märks `metodval` (regel 4).
- Tester före commit: kör `.venv/bin/pytest` och se att allt är grönt. Skriv testet först (regel 6).
- Inga anrop mot riktiga API:t i automatiska tester. Använd `Testleverantor`. Livetester markeras `@pytest.mark.live` (regel 7).
- Sakkunnigstatus ändras aldrig till `verifierad` (regel 8).
- Användartexter på svenska; identifierare på svenska utan å, ä och ö. Fel som användaren kan åtgärda ärver från `riskanalys.fel.RiskanalysFel`.
- Funktioner returnerar nya objekt i stället för att ändra befintliga.
- Commit: `<typ>: <beskrivning>` med typerna feat, fix, refactor, docs, test, chore.
- Design B, modell och effort är preliminära tills spec 8.4.8 är genomförd. "Fyra av fem underkännanden försvinner" är en hypotes som uppgift 4 mäter.
- Faktabladet innehåller aldrig profilens fria källtext, dokumentnamn, sökvägar eller bekräftarens identitet; smågruppsskyddet gäller oförändrat (spec 8.4.2).
- Tillåtna platshållare i AI-text: `{tal:ID}` och `{roll:FfR}` eller `{roll:Ansvarsfunktion}`. Okända, otillåtna eller olösta platshållare stoppar delen eller sammanställningen (spec 8.4.5).

## Review Focus

1. **Ett skyddat litet antal refereras med `{tal:ID}`.** Förväntat: delen underkänns och det skyddade värdet visas aldrig. Prov i uppgift 6.
2. **Profilen ändras mellan skrivning och sammanställning.** Förväntat: talen hämtas ur bedömningens frysta profil, och grinden fångar avvikelsen. Prov i uppgift 11.
3. **Claude svarar med ett `enum`-värde i fel skiftläge.** Förväntat: värdet normaliseras till kanoniskt ID och godkänns. Prov i uppgift 2.
4. **Ett avbrott eller ogiltigt svar i en enskild del.** Förväntat: delen körs om och används sedan som mall med fynd. Hela körningen kraschar inte. Prov i uppgift 9 och 10.
5. **Ett gammalt sakgodkännande av ett tjänsteavsnitt i format v2 efter övergången till v3.** Förväntat: godkännandet gäller inte längre. Prov i uppgift 11.

## Avvikelser från specen, med skäl

- Spec 8.4.5 säger att platshållare ersätts vid rendering. Här ersätts de när dokumentets avsnitt sammanställs ur bedömningens frysta profil (`bygg_tjanstavsnitt_v3`). Sakgranskningen gäller då exakt den text som exporteras, och renderingen behöver inte få regelbas och bedömning. En platshållare som inte kan ersättas stoppar sammanställningen, alltså före rendering.
- Spec 8.4.3 låter AI skriva de byråövergripande avsnitten D-ARB.2, 4, 5, 7 och 9. De kräver en ny tillåtelselista med källor (regel 4) och en egen grind. De får därför en uppföljningsplan efter piloten med tjänsteavsnitten. Den här planen ändrar dem inte.
- Spec 8.4.3 skriver sårbarheter och kontroller parallellt. Här körs delarna i följd, eftersom det är enklare och deterministiskt. Parallell körning är en senare optimering som inte ändrar resultatet.
- Design A (ett anrop per tjänst) byggs efter pilotens första mätning. Tills dess ger inställningen ett tydligt fel.

## Utanför planen

- Kryssfrågor (spec 14.5): egen plan, eftersom svarsalternativen först måste tas fram med källor.
- Utvärderingen i spec 8.4.8: egen plan när sakkunnig finns. Uppgift 4 ger mätfunktionen som piloten använder.
- Klartext i de låsta stycken som i dag innehåller fält-ID och villkorsuttryck (bilaga B1).

## Filkarta

| Fil | Ansvar | Uppgift |
|---|---|---|
| `src/riskanalys/dokument/validering.py` | Svenska tal; förbud mot nivåord i AI-text | 1, 3 |
| `src/riskanalys/dokument/modeller.py` | `AISvar`, `AIStycke`, `AIOklarhet` | 2 |
| `src/riskanalys/dokument/aischema.py` (ny) | JSON-schema med `enum`; tolkning av AI-svar | 2 |
| `src/riskanalys/dokument/claude.py` | Schema per anrop; anrop per del; strömning; cachefält | 2, 9 |
| `src/riskanalys/dokument/skrivning.py` | Tolkning via `aischema`; nytt flöde för format v3 | 2, 10 |
| `src/riskanalys/dokument/nivatext.py` (ny) | Kodskrivna nivåmeningar | 3 |
| `src/riskanalys/dokument/tjanstavsnitt.py` | Nivåmeningar i del 5; `bygg_tjanstavsnitt_v3` | 3, 11 |
| `src/riskanalys/dokument/arb.py` | Nivåmeningar i äldre format; v3-avsnitt | 3, 11 |
| `src/riskanalys/granskning/analys.py` | Grinden: låsta stycken plus validerade delar | 3, 11, 12 |
| `src/riskanalys/dokument/matning.py` (ny) | Sammanfattning av skrivkörningar | 4 |
| `src/riskanalys/dokument/faktablad.py` (ny) | Faktablad med källtyp och smågruppsskydd | 5 |
| `src/riskanalys/dokument/platshallare.py` (ny) | Kontroll och ersättning av platshållare; fält-ID i text | 6 |
| `src/riskanalys/dokument/promptar/` (ny) | Systemprompt, delmoduler, meddelandebyggare, kontrollsummor | 7 |
| `src/riskanalys/dokument/delvalidering.py` (ny) | Gemensamma kontroller och kontroller per del | 8 |
| `src/riskanalys/dokument/leverantor.py` | `Delanrop`, `skriv_del` för test- och Claude-leverantör | 9 |
| `src/riskanalys/dokument/delskrivning.py` (ny) | Anropsflöde, omförsök, effortsteg, mallreserv | 10 |
| `src/riskanalys/granskning/korning.py` | Läser v3-resultat; oklarheter ur delar | 11 |
| `src/riskanalys/intag/dokument.py` | Kräver inte längre godkänt AI-utkast i v3 | 11 |
| `src/riskanalys/dokument/likhet.py` (ny) | Likhet mellan samma del i olika tjänster | 12 |

---

## Del A – Kontroller och kodskrivna meningar

### Task 1: Svenska tal i valideringen

**Files:**
- Modify: `src/riskanalys/dokument/validering.py:30` (`_TAL`) och `:232-234` (`_normalisera`)
- Test: `tester/enhet/test_validering_utkast.py`

**Interfaces:**
- Consumes: befintliga fixturer `giltigt_utkast`, `real_underlag` i `tester/conftest.py`.
- Produces: `validera_utkast` godtar "2 300 000", "2 300 000" och "2 300 000" när underlaget har 2300000.

- [x] **Step 1: Skriv de fallerande proven**

Lägg till i `tester/enhet/test_validering_utkast.py`:

```python
from riskanalys.dokument.modeller import UnderlagUppgift


def _med_omsattning(utkast, underlag, skrivet):
    uppgift = UnderlagUppgift(id="P-VERK.omsattning", fraga="Omsättning", varde="2300000.0", bekraftad=True)
    nytt_underlag = underlag.model_copy(update={"uppgifter": (*underlag.uppgifter, uppgift)})
    stycke = utkast.stycken[0]
    nytt_utkast = _andra(utkast, 0, text=stycke.text + f" Omsättningen var {skrivet} kr.",
                         referenser=[*stycke.referenser, "P-VERK.omsattning"])
    return nytt_utkast, nytt_underlag


@pytest.mark.parametrize("skrivet", ["2 300 000", "2 300 000", "2 300 000", "2300000"])
def test_svenska_tusentalsavgransare_godtas(giltigt_utkast, real_underlag, skrivet):
    utkast, underlag = _med_omsattning(giltigt_utkast, real_underlag, skrivet)
    assert not [fel for fel in validera_utkast(utkast, underlag, PERSONER) if "talet" in fel]


def test_fel_belopp_med_tusentalsavgransare_underkanns(giltigt_utkast, real_underlag):
    utkast, underlag = _med_omsattning(giltigt_utkast, real_underlag, "2 400 000")
    fel = validera_utkast(utkast, underlag, PERSONER)
    assert "Stycke 1 innehåller talet 2400000, som inte finns i underlaget." in fel
```

- [x] **Step 2: Kör proven och se dem fallera**

Run: `.venv/bin/pytest tester/enhet/test_validering_utkast.py -k "tusentals" -v`
Expected: FAIL. "2 300 000" ger fel om talen 300 och 000.

- [x] **Step 3: Implementera**

I `src/riskanalys/dokument/validering.py`, ersätt `_TAL` och `_normalisera`:

```python
# Svenska belopp skrivs med mellanslag, hårt mellanslag eller smalt hårt mellanslag mellan tusental.
_TAL = re.compile(r"\d{1,3}(?:[   ]\d{3})+(?:,\d+)?|\d+(?:[.,]\d+)?")
_TUSENTAL = str.maketrans("", "", "   ")


def _normalisera(tal: str) -> str:
    med_punkt = tal.translate(_TUSENTAL).replace(",", ".")
    return med_punkt.rstrip("0").rstrip(".") if "." in med_punkt else med_punkt
```

- [x] **Step 4: Kör proven och hela valideringssviten**

Run: `.venv/bin/pytest tester/enhet/test_validering_utkast.py -v`
Expected: PASS, även befintliga prov.

- [ ] **Step 5: Commit**

```bash
git add src/riskanalys/dokument/validering.py tester/enhet/test_validering_utkast.py
git commit -m "fix: godta svenska tusentalsavgränsare i AI-valideringen"
```

---

### Task 2: AI-svarsschema med enum och utan avsnittsfält

**Files:**
- Modify: `src/riskanalys/dokument/modeller.py` (nya modeller efter `AvsnittsUtkast`)
- Create: `src/riskanalys/dokument/aischema.py`
- Modify: `src/riskanalys/dokument/claude.py:28-29` (`SCHEMA`, `PROMPT_KONTROLLSUMMA`) och `:52-60` (anropet)
- Modify: `src/riskanalys/dokument/skrivning.py:79-90` (`_bedom_leverans`)
- Test: `tester/enhet/test_aischema.py` (ny), `tester/enhet/test_claude.py`

**Interfaces:**
- Produces:
  - `AISvar(stycken: list[AIStycke], oklarheter: list[AIOklarhet])`, `AIStycke(typ, referenser, text)`, `AIOklarhet(uppgift_id, fraga)` i `dokument/modeller.py`.
  - `aischema.SCHEMAVERSION: str`, `aischema.INGEN_UPPGIFT: str`, `aischema.ai_schema(tillatna_id: frozenset[str], uppgift_id: frozenset[str]) -> dict`, `aischema.tolka_ai_svar(text: str, avsnitt: str, tillatna_id: frozenset[str]) -> AvsnittsUtkast` (kastar `pydantic.ValidationError` om varken nytt eller äldre format passar).

- [x] **Step 1: Skriv de fallerande proven**

Skapa `tester/enhet/test_aischema.py`:

```python
import json

import pytest
from pydantic import ValidationError

from riskanalys.dokument.aischema import INGEN_UPPGIFT, ai_schema, tolka_ai_svar

TILLATNA = frozenset({"T-RED-01", "H-01", "S-KUND-01", "P-KUND.andel_riskbransch"})


def test_schemat_har_enum_och_alla_falt_obligatoriska():
    schema = ai_schema(TILLATNA, frozenset({"P-KUND.andel_riskbransch"}))
    stycke = schema["properties"]["stycken"]["items"]
    assert list(stycke["properties"]) == ["typ", "referenser", "text"]
    assert stycke["required"] == ["typ", "referenser", "text"]
    assert stycke["properties"]["referenser"]["items"]["enum"] == sorted(TILLATNA)
    assert "avsnitt" not in schema["properties"]
    assert schema["additionalProperties"] is False


def test_tom_uppgiftslista_ger_giltigt_enum():
    schema = ai_schema(TILLATNA, frozenset())
    enum = schema["properties"]["oklarheter"]["items"]["properties"]["uppgift_id"]["enum"]
    assert enum == [INGEN_UPPGIFT]


def test_svar_tolkas_med_avsnitt_fran_koden_och_skiftlage_normaliseras():
    text = json.dumps({"stycken": [{"typ": "analys", "referenser": ["h-01", "T-RED-01"], "text": "Text."}],
                       "oklarheter": [{"uppgift_id": "p-kund.andel_riskbransch", "fraga": "Vilken period?"}]})
    utkast = tolka_ai_svar(text, "D-ARB.6.1", TILLATNA)
    assert utkast.avsnitt == "D-ARB.6.1"
    assert utkast.stycken[0].referenser == ["H-01", "T-RED-01"]
    assert utkast.oklarheter[0].saknad_uppgift == "P-KUND.andel_riskbransch"


def test_aldre_svar_med_avsnittsfalt_godtas(giltigt_utkast):
    utkast = tolka_ai_svar(giltigt_utkast.model_dump_json(), "D-ARB.6.1", TILLATNA)
    assert utkast == giltigt_utkast


def test_ogiltigt_svar_kastar_valideringsfel():
    with pytest.raises(ValidationError):
        tolka_ai_svar('{"stycken": "fel"}', "D-ARB.6.1", TILLATNA)
```

- [x] **Step 2: Kör proven och se dem fallera**

Run: `.venv/bin/pytest tester/enhet/test_aischema.py -v`
Expected: FAIL med `ModuleNotFoundError: riskanalys.dokument.aischema`.

- [x] **Step 3: Lägg till modellerna**

I `src/riskanalys/dokument/modeller.py`, efter `class AvsnittsUtkast`:

```python
class AIStycke(Last):
    """Ett stycke som AI skriver. Referenserna står före texten så att de väljs först."""

    typ: Literal["analys", "motivering", "scenario"]
    referenser: list[str]
    text: str


class AIOklarhet(Last):
    uppgift_id: str
    fraga: str


class AISvar(Last):
    """Det AI svarar med. Avsnittets ID känner koden redan till och ingår därför inte."""

    stycken: list[AIStycke]
    oklarheter: list[AIOklarhet]
```

- [x] **Step 4: Skapa `aischema.py`**

```python
"""Schemat som AI svarar i. API:t garanterar formen; valideringen kontrollerar innehållet (spec 8.4.2)."""

from pydantic import ValidationError

from riskanalys.dokument.modeller import AISvar, AvsnittsUtkast, Oklarhet, Textstycke

SCHEMAVERSION = "ai-svar-v1"
INGEN_UPPGIFT = "ingen_uppgift"
STYCKETYPER = ("analys", "motivering", "scenario")


def ai_schema(tillatna_id: frozenset[str], uppgift_id: frozenset[str]) -> dict:
    """JSON-schema med enum för referenser och oklarheter. Ett tomt enum är ogiltigt, därav reservvärdet."""
    stycke = {
        "type": "object",
        "additionalProperties": False,
        "required": ["typ", "referenser", "text"],
        "properties": {
            "typ": {"type": "string", "enum": list(STYCKETYPER)},
            "referenser": {"type": "array", "items": {"type": "string", "enum": sorted(tillatna_id)}},
            "text": {"type": "string"},
        },
    }
    oklarhet = {
        "type": "object",
        "additionalProperties": False,
        "required": ["uppgift_id", "fraga"],
        "properties": {
            "uppgift_id": {"type": "string", "enum": sorted(uppgift_id) or [INGEN_UPPGIFT]},
            "fraga": {"type": "string"},
        },
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["stycken", "oklarheter"],
        "properties": {
            "stycken": {"type": "array", "items": stycke},
            "oklarheter": {"type": "array", "items": oklarhet},
        },
    }


def _kanonisk(varde: str, tillatna: frozenset[str]) -> str:
    """API:t garanterar inte skiftläget i enum-värden; jämför utan hänsyn till det."""
    return {id.lower(): id for id in tillatna}.get(varde.lower(), varde)


def tolka_ai_svar(text: str, avsnitt: str, tillatna_id: frozenset[str]) -> AvsnittsUtkast:
    """AI-svaret som AvsnittsUtkast. Äldre svar med avsnittsfält godtas för testsvar och sparade körningar."""
    try:
        svar = AISvar.model_validate_json(text)
    except ValidationError:
        return AvsnittsUtkast.model_validate_json(text)
    return AvsnittsUtkast(
        avsnitt=avsnitt,
        stycken=[
            Textstycke(typ=s.typ, text=s.text, referenser=[_kanonisk(r, tillatna_id) for r in s.referenser])
            for s in svar.stycken
        ],
        oklarheter=[Oklarhet(fraga=o.fraga, saknad_uppgift=_kanonisk(o.uppgift_id, tillatna_id)) for o in svar.oklarheter],
    )
```

- [x] **Step 5: Använd schemat i leverantören och skrivningen**

I `src/riskanalys/dokument/claude.py`: ta bort `SCHEMA = AvsnittsUtkast.model_json_schema()` och ersätt kontrollsumman:

```python
from riskanalys.dokument.aischema import SCHEMAVERSION, ai_schema

PROMPT_KONTROLLSUMMA = for_text(SYSTEMPROMPT + "\n" + SCHEMAVERSION)
```

I `ClaudeLeverantor.skriv`, före anropet:

```python
        schema = ai_schema(underlag.tillatna_id(), frozenset(u.id for u in underlag.uppgifter))
```

och i anropet: `output_config={"effort": self.effort, "format": {"type": "json_schema", "schema": schema}},`.

I `src/riskanalys/dokument/skrivning.py`, `_bedom_leverans`:

```python
from riskanalys.dokument.aischema import tolka_ai_svar
...
    try:
        svar = tolka_ai_svar(leverans.text, underlag.avsnitt, underlag.tillatna_id())
    except ValidationError as fel:
        return None, (
            f"Svaret följde inte schemat för AI-utkast ({fel.error_count()} fel). Svara bara med JSON enligt schemat.",
        )
```

Run: `grep -n "SCHEMA" tester/enhet/test_claude.py` och uppdatera prov som läser `claude.SCHEMA` så att de i stället kontrollerar att `output_config["format"]["schema"] == ai_schema(underlag.tillatna_id(), frozenset(u.id for u in underlag.uppgifter))` för samma underlag.

- [x] **Step 6: Kör proven**

Run: `.venv/bin/pytest tester/enhet/test_aischema.py tester/enhet/test_claude.py tester/enhet/test_skrivning.py -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/riskanalys/dokument/modeller.py src/riskanalys/dokument/aischema.py src/riskanalys/dokument/claude.py src/riskanalys/dokument/skrivning.py tester/enhet/test_aischema.py tester/enhet/test_claude.py
git commit -m "feat: AI-schema med enum-referenser och utan avsnittsfält"
```

---

### Task 3: Kodskrivna nivåmeningar och förbud mot nivåord i AI-text

**Files:**
- Create: `src/riskanalys/dokument/nivatext.py`
- Modify: `src/riskanalys/dokument/validering.py` (`_nivafel`, `_motiveringar`, `validera_utkast`; ta bort `KRAVDA_NIVAER` och `_kravda_nivaer`)
- Modify: `src/riskanalys/dokument/tjanstavsnitt.py:66` (del 5)
- Modify: `src/riskanalys/dokument/arb.py:182-190` (`_riskavsnitt` i äldre format)
- Modify: `src/riskanalys/granskning/analys.py:9-19`
- Modify: `src/riskanalys/dokument/underlag.py:31-42` (`INSTRUKTION`), `src/riskanalys/dokument/claude.py:18-27` (`SYSTEMPROMPT`)
- Modify: `tester/conftest.py:342-` (`giltigt_utkast`), `tester/fixturer/m2.py:30-39` (`bygg_testsvar`)
- Test: `tester/intag/test_nivatext.py` (ny), `tester/enhet/test_validering_utkast.py`

**Interfaces:**
- Consumes: `Tjanstbedomning` med `inneboende: Riskdel`, `terrorfinansiering: Riskdel`, `kvarstaende: Risk | None`, `sanktionsrisk: Sanktionsbedomning | None`, `regelspar` (`bedomning/modeller.py`).
- Produces: `nivatext.nivastycken(t: Tjanstbedomning) -> tuple[Textstycke, ...]`. Del 5 i tjänsteavsnittet är `(*nivastycken(t), *AI-stycken)`. `validera_utkast` underkänner varje nivåpåstående i AI-text.

- [x] **Step 1: Skriv de fallerande proven**

Skapa `tester/intag/test_nivatext.py`:

```python
from riskanalys.bedomning.korning import kor_bedomning, las_bedomning
from riskanalys.dokument.nivatext import nivastycken
from riskanalys.dokument.validering import nivapastaenden
from riskanalys.profil.lagring import spara_profil


def test_nivameningarna_motsvarar_motorns_nivaer(tmp_path, rb_intag, klar):
    spara_profil(tmp_path, klar)
    b = las_bedomning(kor_bedomning(tmp_path, rb_intag))
    t = next(t for t in b.tjanster if t.inneboende is not None)
    angivna = dict(p for s in nivastycken(t) for p in nivapastaenden(s.text))
    assert angivna["inneboende_risk"] == t.inneboende.risk
    assert angivna["inneboende_sannolikhet"] == t.inneboende.sannolikhet
    assert angivna["terrorfinansiering_risk"] == t.terrorfinansiering.risk
    if t.kvarstaende:
        assert angivna["kvarstaende_risk"] == t.kvarstaende
    if t.sanktionsrisk and t.sanktionsrisk.inneboende:
        assert angivna["sanktioner_risk"] == t.sanktionsrisk.inneboende.risk
    assert all(s.referenser[0] == t.tjanst for s in nivastycken(t))
```

Lägg till i `tester/enhet/test_validering_utkast.py`:

```python
def test_ai_text_far_inte_ange_nivaer_inte_heller_for_delfaktorer(giltigt_utkast, real_underlag):
    utkast = _andra(giltigt_utkast, 0, text=giltigt_utkast.stycken[0].text + " Risken för osanna fakturor är hög.")
    fel = validera_utkast(utkast, real_underlag, PERSONER)
    assert any(f.startswith("Stycke 1 anger en nivå för den inneboende risken.") for f in fel)


def test_fixturen_saknar_nivapastaenden(giltigt_utkast):
    assert not [p for s in giltigt_utkast.stycken for p in nivapastaenden(s.text)]
```

- [x] **Step 2: Kör proven och se dem fallera**

Run: `.venv/bin/pytest tester/intag/test_nivatext.py tester/enhet/test_validering_utkast.py -k "niva or fixturen" -v`
Expected: FAIL (`nivatext` saknas; fixturen innehåller nivåmeningar; en nivå som stämmer med motorn godtas i dag).

- [x] **Step 3: Skapa `nivatext.py`**

```python
"""Risknivåmeningar skrivs av programmet, aldrig av AI (spec 8.4.1)."""

from riskanalys.bedomning.modeller import Tjanstbedomning
from riskanalys.dokument.modeller import Textstycke


def nivastycken(t: Tjanstbedomning) -> tuple[Textstycke, ...]:
    """Motorns nivåer med formuleringar som valideringens mönster känner igen."""
    refs = [t.tjanst, *t.regelspar]
    rader = [
        f"Sannolikheten bedöms som {t.inneboende.sannolikhet}. Konsekvensen är {t.inneboende.konsekvens}. "
        f"Den inneboende risken är {t.inneboende.risk}.",
        f"Sannolikheten för terrorfinansiering bedöms som {t.terrorfinansiering.sannolikhet}. "
        f"Konsekvensen för terrorfinansiering är {t.terrorfinansiering.konsekvens}. "
        f"Risken för finansiering av terrorism bedöms som {t.terrorfinansiering.risk}.",
    ]
    if t.kvarstaende:
        rader.append(f"Den kvarstående risken är {t.kvarstaende}.")
    if t.sanktionsrisk and t.sanktionsrisk.inneboende:
        rader.append(f"Sanktionsrisken är {t.sanktionsrisk.inneboende.risk}.")
        if t.sanktionsrisk.kvarstaende:
            rader.append(f"Den kvarstående sanktionsrisken är {t.sanktionsrisk.kvarstaende}.")
    return tuple(Textstycke(typ="beskrivning", text=rad, referenser=refs) for rad in rader)
```

- [x] **Step 4: Ändra valideringen**

I `src/riskanalys/dokument/validering.py`:

```python
def validera_utkast(utkast: AvsnittsUtkast, underlag: Avsnittsunderlag, personnamn: tuple[str, ...]) -> list[str]:
    """Returnerar alla fel i utkastet. Meddelandena skickas tillbaka till AI och innehåller aldrig personnamn."""
    tillatna_tal = _tal_i(underlag.model_dump_json())
    stycken = [
        fel
        for nummer, stycke in enumerate(utkast.stycken, start=1)
        for fel in _stycke(nummer, stycke, underlag, tillatna_tal, personnamn)
    ]
    return [*_helhet(utkast, underlag), *stycken, *_motiveringar(utkast)]


def _nivafel(nummer: int, text: str) -> list[str]:
    """AI anger aldrig nivåer, inte heller för delfaktorer; programmet skriver nivåmeningarna (regel 1)."""
    return [
        f"Stycke {nummer} anger en nivå för {BENAMNINGAR[nyckel]}. Programmet skriver alla nivåmeningar; "
        "beskriv delfaktorer med andel, antal, period och egenskap i stället."
        for nyckel in dict.fromkeys(nyckel for nyckel, _ in nivapastaenden(text))
    ]


def _motiveringar(utkast: AvsnittsUtkast) -> list[str]:
    motiveringar = [(nummer, stycke) for nummer, stycke in enumerate(utkast.stycken, start=1) if stycke.typ == "motivering"]
    if not motiveringar:
        return ["Utkastet saknar ett stycke av typen motivering."]
    return [
        f"Motiveringen i stycke {nummer} måste hänvisa till minst ett hot (H-) och en sårbarhet (S-) eller uppgift (P-)."
        for nummer, stycke in motiveringar
        if not motivering_har_hot_och_sarbarhet(stycke)
    ]
```

I `_stycke`: ersätt `fel += _nivafel(nummer, stycke.text, underlag.nivaer)` med `fel += _nivafel(nummer, stycke.text)`. Ta bort `KRAVDA_NIVAER` och `_kravda_nivaer`.

Run: `grep -rn "KRAVDA_NIVAER\|riskmotorn anger\|Utkastet anger inte\|Ingen motivering anger" src tester`
Ta bort eller skriv om varje prov som väntar sig det gamla beteendet. Ett prov som krävde att en nivå *anges* ska i stället kräva att nivån *underkänns*.

- [x] **Step 5: Lägg in nivåmeningarna i dokumentet och grinden**

I `src/riskanalys/dokument/tjanstavsnitt.py:66`, ersätt `('Risknivåer och motivering', tuple(utkast.stycken))` med `('Risknivåer och motivering', (*nivastycken(t), *utkast.stycken))` och lägg till `from riskanalys.dokument.nivatext import nivastycken`.

I `src/riskanalys/dokument/arb.py`, `_riskavsnitt`: `stycken=(*nivastycken(tjanst), *utkast[avsnitt_id].stycken),` med samma import.

I `src/riskanalys/granskning/analys.py`, `_tjanstanalys_stammer`, ersätt raden som bygger `utkast`:

```python
    lasta = nivastycken(tjanst)
    utkast = AvsnittsUtkast(avsnitt=avsnitt.id, stycken=list(avsnitt.stycken[start + len(lasta):slut]), oklarheter=[])
```

med `from riskanalys.dokument.nivatext import nivastycken`. Ombyggnaden lägger själv till de låsta nivåmeningarna, så en ändrad nivåmening ger fortfarande en avvikande kontrollsumma.

- [x] **Step 6: Uppdatera instruktionerna och fixturerna**

I `src/riskanalys/dokument/underlag.py`, ersätt meningarna i `INSTRUKTION` från "Återge nivåerna exakt" till och med "bedöms som måttlig.\" " med:

```python
    "Programmet skriver alla risknivåmeningar. Ange själv ingen nivå för risk, sannolikhet eller konsekvens, "
    "inte heller för delfaktorer; beskriv dem med andel, antal, period och egenskap. "
```

I `src/riskanalys/dokument/claude.py`, `SYSTEMPROMPT`, ersätt de tre reglerna om nivåer (raderna som börjar "Risknivåerna kommer från en regelmotor", "Skriv varje nivå så att" och "Minst ett stycke ska vara en motivering") med:

```text
- Risknivåerna kommer från en regelmotor, och programmet skriver nivåmeningarna själv. Ange ingen nivå för risk, sannolikhet eller konsekvens, inte heller för delfaktorer, eftersom en egen nivå läses som en motsägelse mot motorn. Beskriv delfaktorer med andel, antal, period och egenskap.
- Minst ett stycke ska vara en motivering som hänvisar till hot och till sårbarheter eller uppgifter och förklarar hur de leder till motorns nivå.
```

I `tester/conftest.py`, `giltigt_utkast`, skriv om varje mening som anger en nivå. Motiveringsstycket blir:

```python
                    "text": (
                        "Sannolikheten påverkas av att 30 % av kunderna finns i riskbranscher och att 80 % av "
                        "underlaget kommer in digitalt medan bankdata bara finns för 40 % av kunderna. "
                        "Osanna fakturor kan därför bokföras utan att flödet kan stämmas av mot banken."
                    ),
```

Gör samma sak för andra stycken i fixturen som anger terrorfinansieringsrisk eller kvarstående risk.

I `tester/fixturer/m2.py`, `bygg_testsvar`, ersätt texterna och ta bort variabeln `n`, som då inte används:

```python
        text="Tjänstens ekonomiska flöden kan utnyttjas för att föra in osanna underlag och ge brottsvinster ett legalt utseende."
        refs=[u.hot[0].id,u.sarbarheter[0].id]
        a=AvsnittsUtkast(avsnitt=id,stycken=[Textstycke(typ='analys',text=text,referenser=list(u.regelspar)),Textstycke(typ='motivering',text="Hoten kan utnyttja sårbarheterna i kundunderlagen, och spårbara kontroller och uppföljning behövs för att motverka dem.",referenser=refs)],oklarheter=[])
```

- [x] **Step 7: Kör de berörda proven och hela sviten**

Run: `.venv/bin/pytest tester/intag/test_nivatext.py tester/enhet/test_validering_utkast.py tester/enhet/test_skrivning.py tester/regelkontrakt/test_arb_utvidgning.py -v`
Expected: PASS.
Run: `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest -q`
Expected: allt grönt. Prov som jämför exporterade texter med nivåer i AI-delen uppdateras så att nivåerna förväntas i de låsta styckena.

- [ ] **Step 8: Commit**

```bash
git add -A src/riskanalys/dokument src/riskanalys/granskning/analys.py tester
git commit -m "feat: programmet skriver risknivåmeningarna och AI-text får inte ange nivåer"
```

---

### Task 4: Sammanfattning av skrivkörningar

**Files:**
- Create: `src/riskanalys/dokument/matning.py`
- Modify: `src/riskanalys/kommandon/skriv_kommando.py` (skriv ut sammanfattningen efter körningen)
- Test: `tester/enhet/test_matning.py` (ny)

**Interfaces:**
- Consumes: `Skrivresultat`, `Forsok` i `dokument/skrivning.py`; `Tokenanvandning`, `Anropsdata` i `dokument/leverantor.py`.
- Produces: `Skrivsammanfattning`, `sammanfatta(resultat: Iterable[Skrivresultat]) -> Skrivsammanfattning`, `felklass(fel: str) -> str`, `kostnad_usd(s: Skrivsammanfattning, indatapris: float, utdatapris: float) -> float`.

- [x] **Step 1: Skriv de fallerande proven**

```python
from datetime import datetime, timezone

from riskanalys.dokument.leverantor import Anropsdata, Tokenanvandning
from riskanalys.dokument.matning import felklass, kostnad_usd, sammanfatta
from riskanalys.dokument.skrivning import Forsok, Skrivresultat


def _forsok(nummer, fel, indata=1000, utdata=500):
    anrop = Anropsdata(leverantor="test", begard_modell="m", svarsmodell="m", effort="high", prompt_kontrollsumma=None,
                       svar_id=None, stop_reason="end_turn", reservmodell_svarade=False,
                       anvandning=(Tokenanvandning(typ="message", modell=None, indata_token=indata, utdata_token=utdata),),
                       tidpunkt=datetime.now(timezone.utc))
    return Forsok(nummer=nummer, anrop=anrop, text="{}", svar=None, fel=tuple(fel))


def test_sammanfattning_raknar_forsta_forsok_och_felklasser(real_underlag):
    direkt = Skrivresultat(underlag=real_underlag, leverantor="test", modell="m", forsok=(_forsok(1, []),))
    andra = Skrivresultat(underlag=real_underlag, leverantor="test", modell="m",
                          forsok=(_forsok(1, ["Stycke 1 innehåller talet 000, som inte finns i underlaget."]), _forsok(2, [])))
    s = sammanfatta([direkt, andra])
    assert (s.avsnitt, s.godkanda_forsta_forsoket, s.anrop) == (2, 1, 3)
    assert s.felklasser == {"tal": 1}
    assert kostnad_usd(s, 2.0, 10.0) == round(3000 * 2 / 1e6 + 1500 * 10 / 1e6, 4)


def test_felklasser():
    assert felklass("Stycke 2 anger en nivå för risken.") == "niva"
    assert felklass("Oklarhet 1: saknad_uppgift måste vara ett tillåtet fält.") == "oklarhet"
    assert felklass("Stycke 1 hänvisar till X, som inte finns i underlaget.") == "referens"
    assert felklass("Svaret följde inte schemat för AI-utkast (2 fel).") == "schema"
    assert felklass("Något annat.") == "ovrigt"
```

- [x] **Step 2: Kör proven och se dem fallera**

Run: `.venv/bin/pytest tester/enhet/test_matning.py -v`
Expected: FAIL (`matning` saknas).

- [x] **Step 3: Implementera**

```python
"""Mätning av skrivkörningar: förstaförsök, omförsök, felklasser och tokens (spec 8.4.7–8.4.8)."""

from collections import Counter
from collections.abc import Iterable

from riskanalys.dokument.modeller import Last

_KLASSER = (("talet", "tal"), ("anger en nivå", "niva"), ("Oklarhet", "oklarhet"), ("hänvisar till", "referens"),
            ("schemat", "schema"), ("platshållare", "platshallare"))


class Skrivsammanfattning(Last):
    avsnitt: int
    godkanda_forsta_forsoket: int
    anrop: int
    indata_token: int
    utdata_token: int
    felklasser: dict[str, int]


def felklass(fel: str) -> str:
    return next((klass for nyckel, klass in _KLASSER if nyckel in fel), "ovrigt")


def sammanfatta(resultat: Iterable) -> Skrivsammanfattning:
    lista = list(resultat)
    forsok = [f for r in lista for f in r.forsok]
    poster = [p for f in forsok for p in f.anrop.anvandning]
    return Skrivsammanfattning(
        avsnitt=len(lista),
        godkanda_forsta_forsoket=sum(1 for r in lista if r.forsok and not r.forsok[0].fel),
        anrop=len(forsok),
        indata_token=sum(p.indata_token for p in poster),
        utdata_token=sum(p.utdata_token for p in poster),
        felklasser=dict(Counter(felklass(fel) for f in forsok for fel in f.fel)),
    )


def kostnad_usd(s: Skrivsammanfattning, indatapris: float, utdatapris: float) -> float:
    """Pris i USD per miljon token."""
    return round(s.indata_token * indatapris / 1e6 + s.utdata_token * utdatapris / 1e6, 4)
```

I `src/riskanalys/kommandon/skriv_kommando.py`, efter att `kor_skrivning` returnerat `mapp`:

```python
    from riskanalys.dokument.matning import sammanfatta
    from riskanalys.dokument.skrivning import las_skrivresultat
    s = sammanfatta(las_skrivresultat(mapp))
    print(f"Avsnitt: {s.avsnitt}, godkända direkt: {s.godkanda_forsta_forsoket}, anrop: {s.anrop}, "
          f"token in/ut: {s.indata_token}/{s.utdata_token}.")
```

- [x] **Step 4: Kör proven**

Run: `.venv/bin/pytest tester/enhet/test_matning.py tester/enhet/test_skriv_kommando.py -v`
Expected: PASS.

- [ ] **Step 5: Mät hypotesen (manuellt, kostar pengar)**

Kör bara med användarens uttryckliga godkännande. Använd en syntetisk byrå och kör `riskanalys skriv <byrå> --modell claude-sonnet-5-5 --effort high`. Anteckna sammanfattningen i `docs/STATUS.md`: andel avsnitt godkända direkt och felklasser före och efter del A (före del A: 0 av 5 direkt, med felklasserna tal, niva, oklarhet, referens).

- [ ] **Step 6: Commit**

```bash
git add src/riskanalys/dokument/matning.py src/riskanalys/kommandon/skriv_kommando.py tester/enhet/test_matning.py
git commit -m "feat: sammanfattning av skrivkörningar för förstaförsök och felklasser"
```

---

## Del B – Promptarkitektur och ett anrop per del

### Task 5: Faktablad med sluten källtyp och smågruppsskydd

**Files:**
- Create: `src/riskanalys/dokument/faktablad.py`
- Test: `tester/intag/test_faktablad.py` (ny)

**Interfaces:**
- Consumes: `bygg_underlag` i `dokument/underlag.py` (tillåtelselistan och smågruppsskyddet finns redan där); `EGEN_KANNEDOM` i `intag/underlag.py`.
- Produces:
  - `Faktapost(id, etikett, visningsvarde, period, kalltyp, status, tal)`; `Faktablad(avsnitt, tjanst_id, tjanst_namn, poster, hot, sarbarheter, kontroller, regelspar)` med `tillatna_id() -> frozenset[str]`, `uppgift_id() -> frozenset[str]`, `numeriska() -> dict[str, str]`.
  - `bygg_faktablad(regelbas, profil, tjanstbedomning, avsnitt_id) -> Faktablad`, `faktablad_json(fb: Faktablad) -> str`, `visa_tal(varde: float) -> str`.

- [x] **Step 1: Skriv de fallerande proven**

```python
from riskanalys.bedomning.korning import kor_bedomning, las_bedomning
from riskanalys.dokument.faktablad import bygg_faktablad, faktablad_json, visa_tal
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.profil.lagring import spara_profil


def _faktablad(mapp, rb, profil):
    mapp.mkdir(parents=True, exist_ok=True)
    spara_profil(mapp, profil)
    b = las_bedomning(kor_bedomning(mapp, rb))
    avsnitt_id, t = tjanster_med_avsnitt(b)[0]
    return bygg_faktablad(rb, profil, t, avsnitt_id)


def test_ingen_fri_kalltext_eller_bekraftare_lamnar_datorn(tmp_path, rb_intag, klar):
    hemligt = "Kim Testsson /Users/x/kundregister.xlsx"
    upp = {k: (u.model_copy(update={"kalla": hemligt, "bekraftad_av": "roll:Kim Testsson"}) if u.kalla else u)
           for k, u in klar.uppgifter.items()}
    fb = _faktablad(tmp_path, rb_intag, klar.model_copy(update={"uppgifter": upp}))
    text = faktablad_json(fb)
    assert "Kim Testsson" not in text and "/Users/" not in text and "kundregister" not in text
    assert {p.kalltyp for p in fb.poster} <= {None, "register", "intern_statistik", "egen_kannedom", "dokument", "harledning"}


def test_skyddade_varden_saknar_tal(tmp_path, rb_intag, klar):
    fb = _faktablad(tmp_path, rb_intag, klar)
    for p in fb.poster:
        if p.visningsvarde.startswith(("färre än", "undertryckt")):
            assert p.status == "skyddad" and p.tal is None and p.id not in fb.numeriska()


def test_faktabladet_ar_byte_for_byte_stabilt(tmp_path, rb_intag, klar):
    assert faktablad_json(_faktablad(tmp_path / "a", rb_intag, klar)) == faktablad_json(_faktablad(tmp_path / "b", rb_intag, klar))


def test_svenskt_talformat():
    assert visa_tal(2300000.0) == "2 300 000"
    assert visa_tal(46.5) == "46,5"
```

- [x] **Step 2: Kör proven och se dem fallera**

Run: `.venv/bin/pytest tester/intag/test_faktablad.py -v`
Expected: FAIL (`faktablad` saknas).

- [x] **Step 3: Implementera**

```python
"""Faktabladet: det enda AI får veta om en tjänst (spec 8.4.2). Byggs ur det tillåtelselistade underlaget."""

import json
from typing import Literal

from riskanalys.dokument.modeller import Last, UnderlagHot, UnderlagKontroll, UnderlagSarbarhet
from riskanalys.dokument.underlag import bygg_underlag
from riskanalys.profil.modeller import Profil, Uppgift
from riskanalys.regelverk.modeller import Falt, Regelbas

Kalltyp = Literal["register", "intern_statistik", "egen_kannedom", "dokument", "harledning"]
_SKYDDADE = ("färre än", "undertryckt")
_NUMERISKA = ("heltal", "tal", "andel")


class Faktapost(Last):
    id: str
    etikett: str
    visningsvarde: str
    period: str | None
    kalltyp: Kalltyp | None
    status: Literal["bekräftad", "okänd", "skyddad"]
    tal: float | None = None


class Faktablad(Last):
    avsnitt: str
    tjanst_id: str
    tjanst_namn: str
    poster: tuple[Faktapost, ...]
    hot: tuple[UnderlagHot, ...]
    sarbarheter: tuple[UnderlagSarbarhet, ...]
    kontroller: tuple[UnderlagKontroll, ...]
    regelspar: tuple[str, ...]

    def tillatna_id(self) -> frozenset[str]:
        return frozenset({self.tjanst_id, *(p.id for p in self.poster), *(h.id for h in self.hot),
                          *(s.id for s in self.sarbarheter), *(k.id for k in self.kontroller), *self.regelspar})

    def uppgift_id(self) -> frozenset[str]:
        return frozenset(p.id for p in self.poster)

    def numeriska(self) -> dict[str, str]:
        """Värden som AI får hänvisa till med {tal:ID}; skyddade och okända värden saknas."""
        return {p.id: p.visningsvarde for p in self.poster if p.tal is not None}


def visa_tal(varde: float) -> str:
    heltal = round(varde)
    if abs(varde - heltal) < 1e-9:
        return f"{heltal:,}".replace(",", " ")
    return f"{varde:.1f}".replace(".", ",")


def kalltyp(uppgift: Uppgift, falt: Falt) -> Kalltyp | None:
    """Sluten källtyp som koden härleder. Profilens fria källtext lämnar aldrig datorn."""
    from riskanalys.intag.underlag import EGEN_KANNEDOM
    kalla = uppgift.kalla or ""
    if not kalla:
        return None
    if kalla == EGEN_KANNEDOM:
        return "egen_kannedom"
    if kalla.startswith("Härledning:"):
        return "harledning"
    if kalla.startswith(("SCB AFR API", "Lokalt importerat SCB")):
        return "register"
    if falt.periodkrav or falt.typ in _NUMERISKA:
        return "intern_statistik"
    return "dokument"


def _post(regelbas: Regelbas, profil: Profil, u) -> Faktapost:
    falt = regelbas.falt[u.id]
    uppgift = profil.uppgifter.get(u.id, Uppgift())
    skyddad = u.varde.startswith(_SKYDDADE)
    tal = None
    if not skyddad and u.bekraftad and falt.typ in _NUMERISKA and type(uppgift.varde) in (int, float):
        tal = float(uppgift.varde) * (100 if falt.typ == "andel" else 1)
    visning = (visa_tal(tal) + (" %" if falt.typ == "andel" else "")) if tal is not None else u.varde
    return Faktapost(
        id=u.id, etikett=u.fraga, visningsvarde=visning,
        period=f"{u.period[0]}–{u.period[1]}" if u.period else None,
        kalltyp=kalltyp(uppgift, falt),
        status="skyddad" if skyddad else "bekräftad" if u.bekraftad else "okänd",
        tal=tal,
    )


def bygg_faktablad(regelbas: Regelbas, profil: Profil, tjanstbedomning, avsnitt_id: str) -> Faktablad:
    underlag = bygg_underlag(regelbas, profil, tjanstbedomning, avsnitt_id)
    return Faktablad(
        avsnitt=avsnitt_id, tjanst_id=underlag.tjanst_id, tjanst_namn=underlag.tjanst_namn,
        poster=tuple(_post(regelbas, profil, u) for u in underlag.uppgifter),
        hot=underlag.hot, sarbarheter=underlag.sarbarheter, kontroller=underlag.kontroller, regelspar=underlag.regelspar,
    )


def faktablad_json(fb: Faktablad) -> str:
    """Sorterade nycklar och fast ordning, så att cachen kan träffa (spec 8.4.2)."""
    return json.dumps(fb.model_dump(mode="json"), sort_keys=True, ensure_ascii=False, indent=1)
```

Läs signaturen för `bygg_underlag` i `src/riskanalys/dokument/underlag.py` och anpassa anropet om den skiljer sig, utan att ändra underlagets innehåll.

- [x] **Step 4: Kör proven**

Run: `.venv/bin/pytest tester/intag/test_faktablad.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/riskanalys/dokument/faktablad.py tester/intag/test_faktablad.py
git commit -m "feat: faktablad med sluten källtyp och oförändrat smågruppsskydd"
```

---

### Task 6: Platshållare för tal och förbud mot fält-ID i AI-text

**Files:**
- Create: `src/riskanalys/dokument/platshallare.py`
- Test: `tester/enhet/test_platshallare.py` (ny)

**Interfaces:**
- Consumes: `ROLLER` i `dokument/rendering.py`.
- Produces: `platshallarfel(nummer: int, text: str, referenser: list[str], numeriska: dict[str, str]) -> list[str]`, `faltid_fel(nummer: int, text: str) -> list[str]`, `ersatt_tal(text: str, numeriska: dict[str, str]) -> str` (kastar `RiskanalysFel`).

- [x] **Step 1: Skriv de fallerande proven**

```python
import pytest

from riskanalys.dokument.platshallare import ersatt_tal, faltid_fel, platshallarfel
from riskanalys.fel import RiskanalysFel

NUM = {"P-TJ.red01_antal_kunder": "110", "P-KUND.antal_aktiva": "120"}


def test_giltig_platshallare_godtas():
    assert platshallarfel(1, "Tjänsten används av {tal:P-TJ.red01_antal_kunder} kunder.",
                          ["P-TJ.red01_antal_kunder"], NUM) == []


@pytest.mark.parametrize("text,refs,del_av_fel", [
    ("{tal:P-OKAND.x} kunder", ["P-OKAND.x"], "okänt eller skyddat"),
    ("{tal:P-KUND.antal_aktiva} kunder", ["T-RED-01"], "saknas bland styckets referenser"),
    ("{tal:P-KUND.antal_aktiva kunder", ["P-KUND.antal_aktiva"], "felskriven"),
    ("{antal} kunder", [], "otillåten platshållare"),
])
def test_otillatna_platshallare_underkanns(text, refs, del_av_fel):
    assert any(del_av_fel in f for f in platshallarfel(1, text, refs, NUM))


def test_skyddat_varde_kan_inte_refereras():
    assert platshallarfel(1, "{tal:P-GEO.antal_hogrisktredjeland}", ["P-GEO.antal_hogrisktredjeland"], NUM)


def test_falt_id_i_lopande_text_underkanns_men_inte_i_platshallare():
    assert faltid_fel(1, "Andelen P-KUND.andel_riskbransch är 15 %.")
    assert faltid_fel(1, "Hotet H-01 gäller.")
    assert faltid_fel(1, "Tjänsten har {tal:P-KUND.antal_aktiva} kunder och {roll:FfR} ansvarar.") == []


def test_ersattning_och_stopp_vid_olost():
    assert ersatt_tal("{tal:P-KUND.antal_aktiva} kunder", NUM) == "120 kunder"
    with pytest.raises(RiskanalysFel):
        ersatt_tal("{tal:P-GEO.saknas} kunder", NUM)
```

- [x] **Step 2: Kör proven och se dem fallera**

Run: `.venv/bin/pytest tester/enhet/test_platshallare.py -v`
Expected: FAIL (`platshallare` saknas).

- [x] **Step 3: Implementera**

```python
"""Platshållare i AI-text (spec 8.4.5). Koden ersätter talen; AI skriver aldrig fält-ID i löptext."""

import re

from riskanalys.dokument.rendering import ROLLER
from riskanalys.fel import RiskanalysFel

_TAL = re.compile(r"\{tal:([^{}\s]+)\}")
_ROLL = re.compile(r"\{roll:(\w+)\}")
_KLAMMER = re.compile(r"\{[^{}]*\}")
_OPPEN = re.compile(r"\{tal:[^}]*$|\{tal:[^}]*\s")
_FALTID = re.compile(r"\b(?:P|S|H|C|T|BT|D|K)-[A-Z0-9][A-Za-z0-9]*(?:[._-][A-Za-z0-9]+)*\b")


def platshallarfel(nummer: int, text: str, referenser: list[str], numeriska: dict[str, str]) -> list[str]:
    fel = []
    if _OPPEN.search(text):
        fel.append(f"Stycke {nummer} har en felskriven platshållare. Skriv {{tal:ID}} med ett ID från faktabladet.")
    for traff in _KLAMMER.finditer(text):
        hel = traff.group(0)
        tal = _TAL.fullmatch(hel)
        roll = _ROLL.fullmatch(hel)
        if roll and roll.group(1) in ROLLER:
            continue
        if not tal:
            fel.append(f"Stycke {nummer} innehåller en otillåten platshållare {hel}. Tillåtna är {{tal:ID}} och {{roll:FfR}}.")
            continue
        id = tal.group(1)
        if id not in numeriska:
            fel.append(f"Stycke {nummer}: {hel} är okänt eller skyddat. Använd bara tal-ID som finns i faktabladet.")
        elif id not in referenser:
            fel.append(f"Stycke {nummer}: {id} i {hel} saknas bland styckets referenser.")
    return fel


def faltid_fel(nummer: int, text: str) -> list[str]:
    utan = _KLAMMER.sub(" ", text)
    return [f"Stycke {nummer} innehåller ID:t {id} i löptexten. Lägg ID:n i referenser och skriv klartext."
            for id in dict.fromkeys(_FALTID.findall(utan))]


def ersatt_tal(text: str, numeriska: dict[str, str]) -> str:
    def ersatt(traff: re.Match[str]) -> str:
        if traff.group(1) not in numeriska:
            raise RiskanalysFel(f"Platshållaren {traff.group(0)} kan inte ersättas. Skriv om delen innan dokumentet sammanställs.")
        return numeriska[traff.group(1)]
    return _TAL.sub(ersatt, text)
```

- [x] **Step 4: Kör proven**

Run: `.venv/bin/pytest tester/enhet/test_platshallare.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/riskanalys/dokument/platshallare.py tester/enhet/test_platshallare.py
git commit -m "feat: platshållare för tal och förbud mot fält-ID i AI-text"
```

---

### Task 7: Systemprompt och delmoduler

**Files:**
- Create: `src/riskanalys/dokument/promptar/__init__.py`, `promptar/system.py`, `promptar/delar.py`, `promptar/meddelande.py`
- Modify: `tester/enhet/conftest.py` (fixturen `faktablad_exempel`)
- Test: `tester/enhet/test_promptar.py` (ny)

**Interfaces:**
- Consumes: `Faktablad`, `faktablad_json` (uppgift 5); `SCHEMAVERSION` (uppgift 2).
- Produces:
  - `promptar.DELAR: tuple[str, ...] = ("hot", "sarbarheter", "kontroller", "risknivaer", "slutsatser")`.
  - `promptar.systemprompt(modell: str) -> str`, `promptar.delmodul(del_id: str) -> str`, `promptar.promptsumma(modell: str, del_id: str) -> str`.
  - `promptar.bygg_innehall(fb: Faktablad, del_id: str, lasta: tuple[str, ...], maskinellt_validerat: tuple[str, ...], aterkoppling: tuple[str, ...]) -> list[dict]`.

- [x] **Step 1: Skriv de fallerande proven**

```python
import re

from riskanalys.dokument.promptar import DELAR, bygg_innehall, delmodul, promptsumma, systemprompt


def _taggar(block):
    return [b["text"].split(">")[0] + ">" for b in block]


def test_systemprompten_ar_fast_lang_nog_och_utan_datum():
    text = systemprompt("claude-opus-5-5")
    assert text == systemprompt("claude-opus-5-5")
    assert len(text) >= 2400  # cirka 512 token eller mer, så att den kan cachas
    assert not re.search(r"\b20\d\d-\d\d-\d\d\b", text)
    assert "MUST" not in text and "VIKTIGT" not in text


def test_sonnetraden_bara_for_sonnet():
    assert systemprompt("claude-sonnet-5-5").endswith("Think the problem through before you answer.")
    assert "Think the problem" not in systemprompt("claude-opus-5-5")


def test_varje_del_har_modul_och_egen_summa():
    assert len({promptsumma("claude-opus-5-5", d) for d in DELAR}) == len(DELAR)
    for d in DELAR:
        assert len(delmodul(d)) > 400


def test_innehallet_har_fast_ordning_och_cachebrytpunkt(faktablad_exempel):
    block = bygg_innehall(faktablad_exempel, "hot", ("Låst mening.",), (), ())
    assert block[0]["cache_control"] == {"type": "ephemeral"}
    assert _taggar(block) == ["<faktablad>", "<lasta_meningar>", '<uppgift del="hot">']
    med = bygg_innehall(faktablad_exempel, "risknivaer", (), ("Godkänd text.",), ("Fel 1.",))
    assert _taggar(med) == ["<faktablad>", "<maskinellt_validerat>", '<uppgift del="risknivaer">', "<aterkoppling>"]
```

Lägg till i `tester/enhet/conftest.py`:

```python
@pytest.fixture
def faktablad_exempel():
    from riskanalys.dokument.faktablad import Faktablad, Faktapost
    from riskanalys.dokument.modeller import UnderlagHot
    return Faktablad(avsnitt="D-ARB.6.1", tjanst_id="T-RED-01", tjanst_namn="Löpande bokföring",
                     poster=(Faktapost(id="P-KUND.antal_aktiva", etikett="Aktiva kunder", visningsvarde="120",
                                       period="2025-01-01–2025-12-31", kalltyp="intern_statistik", status="bekräftad", tal=120.0),),
                     hot=(UnderlagHot(id="H-01", namn="Osanna fakturor", beskrivning="Syntetisk beskrivning."),
                          UnderlagHot(id="H-02", namn="Brottsvinster som intäkter", beskrivning="Syntetisk beskrivning.")),
                     sarbarheter=(), kontroller=(), regelspar=())
```

- [x] **Step 2: Kör proven och se dem fallera**

Run: `.venv/bin/pytest tester/enhet/test_promptar.py -v`
Expected: FAIL (`promptar` saknas).

- [x] **Step 3: Systemprompten (`promptar/system.py`)**

```python
"""Den fasta systemprompten. Identisk i alla anrop för samma modell (spec 8.4.2)."""

SYSTEMTEXT = """<roll>
Du skriver analyserande text i en svensk redovisningsbyrås allmänna riskbedömning enligt lagen (2017:630) om åtgärder mot penningtvätt och finansiering av terrorism. Läsarna är byråns ledning och personal och Länsstyrelsens handläggare. Texten ska visa att byrån förstår hur just dess tjänster, kunder, kanaler och geografi kan utnyttjas, och vad det betyder för byråns arbete.
</roll>

<arbetsfordelning>
Byråns regelmotor har redan fastställt vilka hot, sårbarheter och kontroller som gäller och vilka risknivåer varje tjänst har. Programmet skriver själv alla tal, nivåmeningar, obligatoriska meningar och datum. Din uppgift är texten mellan dem: hur tjänsten kan utnyttjas hos just den här byrån, varför uppgifterna i faktabladet spelar roll och hur faktorerna hänger ihop. Det är den analysen som tillsynen oftast saknar i riskbedömningar.
</arbetsfordelning>

<regler>
Använd bara uppgifterna i faktabladet. Dokumentet ska kunna spåras till byråns eget underlag vid tillsyn, och programmet redovisar luckor separat, så ett påstående utan stöd i faktabladet gör mer skada än en lucka.

Ange ingen nivå för risk, sannolikhet eller konsekvens, inte heller för enskilda faktorer. Bara regelmotorn bedömer risk, och en egen nivå läses som en motsägelse mot motorn. Beskriv i stället faktorerna med andel, antal, period och egenskap, till exempel att en viss andel av kunderna finns i en riskbransch.

Skriv tal som platshållare i formen {tal:ID}, där ID är en faktarad med ett tal, och ange samma ID i styckets referenser. Programmet formaterar talen och kontrollerar att de stämmer, så du behöver aldrig skriva siffror själv.

Ange i varje stycke vilka faktarader det bygger på genom deras ID i fältet referenser. Välj referenserna först och skriv sedan stycket utifrån dem. Skriv aldrig ID, fältnamn eller villkorsuttryck i själva texten, eftersom läsaren inte känner till dem.

Om en uppgift du behöver saknas eller inte är bekräftad: skriv [VERIFIERA] i stycket och lägg till en oklarhet med faktaradens ID. Ett utkast med luckor får inte se färdigt ut, och att skriva att underlag saknas är ett korrekt svar.

Beskriv ett samband mellan två faktorer som belagt bara när faktabladet visar att de avser samma kunder. Annars skriver du sambandet som ett villkorligt scenario med stycketypen scenario, eller konstaterar att ingen kombination är belagd. Två uppgifter om hela kundbasen visar inte att samma kunder berörs.

Skriv personer som {roll:FfR}, eftersom underlaget är avidentifierat och programmet sätter in namnen lokalt.

Skriv om byråns egna förhållanden och inte om branschen i allmänhet. Tillsynen underkänner riskbedömningar som skulle kunna gälla vilken byrå som helst.

Få eller inga misstankerapporter visar inte att ett hot saknas. Den nationella riskbedömningen tolkar få rapporter från sektorn som låg riskmedvetenhet, så skriv aldrig att avsaknad av rapporter visar låg risk.

Upprepa eller ändra inte programmets låsta meningar. Bygg vidare på dem.

Skriv sakligt och på klar svenska, i hela meningar och utan punktlistor.
</regler>

<exempel>
Illustrativt, inte en mall för den här byrån:
1. Delfaktor beskriven utan nivåord: "{tal:P-KUND.andel_riskbransch} av kunderna i tjänsten finns i branscher där kontanter och underentreprenörer är vanliga, vilket gör det svårare att stämma av fakturor mot verkliga prestationer."
2. Okänd uppgift: "Byrån har inte bekräftat hur många kunder som har ägare utanför EES. [VERIFIERA]" med en oklarhet för den faktaraden.
3. Villkorligt scenario: "Om de kunder som saknar bankdata också är verksamma i riskbranscher kan osanna fakturor passera utan avstämning. Underlaget visar inte om det gäller samma kunder."
</exempel>"""

SONNETRAD = "Think the problem through before you answer."


def systemprompt(modell: str) -> str:
    """Sonnet 5.5 hoppar ofta över tänkandet med strukturerade svar; raden sist motverkar det."""
    return SYSTEMTEXT + ("\n\n" + SONNETRAD if "sonnet" in modell else "")
```

- [x] **Step 4: Delmodulerna (`promptar/delar.py`)**

```python
"""En modul per analysdel: mål, krav med skäl och fällor med skäl (spec 8.4.4)."""

DELAR = ("hot", "sarbarheter", "kontroller", "risknivaer", "slutsatser")

MODULER = {
    "hot": (
        "Skriv delen Hot och egna erfarenheter för tjänsten. Beskriv minst två konkreta sätt som just den här tjänsten "
        "kan utnyttjas hos byrån, utifrån hoten i faktabladet och tjänstens kunder. Ta med finansiering av terrorism när "
        "faktabladet har sådana hot, och beskriv tillvägagångssättet, inte bara att risken finns. Förklara att byrån kan "
        "utnyttjas omedvetet, genom att någon ser mellan fingrarna eller genom medverkan, eftersom penningtvättslagen "
        "kräver att hotet analyseras utifrån hur verksamheten faktiskt kan användas.\n"
        "Programmet har redan skrivit meningen om byråns egen rapportering. Hänvisa till den men upprepa den inte.\n"
        "Undvik allmänna hot som skulle gälla alla tjänster, eftersom tillsynen kritiserar just det.\n"
        "Exempel, illustrativt: \"En kund kan lämna fakturor från bolag utan verklig verksamhet för bokföring som vanliga "
        "kostnader. Eftersom byrån konterar underlagen löpande kan sådana fakturor ge brottsvinster ett legalt utseende "
        "innan någon stämmer av dem mot leveranser.\""
    ),
    "sarbarheter": (
        "Skriv delen Sårbarheter och motivering för tjänsten. Gå igenom kunder, distributionskanaler, geografi och "
        "verksamhetsspecifika förhållanden. Säg för varje kategori om sårbarheterna i faktabladet gäller, inte gäller "
        "eller är okända, varför, och hur stor andel som berörs. Föreskrifterna kräver att sårbarheterna analyseras per "
        "kategori, och ett \"gäller inte\" utan skäl räknas som en brist.\n"
        "Geografin omfattar mer än sanktionslistor: ägare, verksamhet och betalningsflöden, även inom Sverige. Att "
        "kunderna är svenska utesluter inte geografisk risk. Långa kundrelationer är ingen trygghet i sig; nära relationer "
        "kan minska vaksamheten.\n"
        "Beskriv samverkan mellan faktorer som belagd bara när faktabladet visar att de gäller samma kunder; annars "
        "skriver du ett villkorligt scenario med stycketypen scenario.\n"
        "Programmet har redan skrivit underlagsstycket för geografin. Bygg vidare på det."
    ),
    "kontroller": (
        "Skriv delen Kontroller och effekt för tjänsten. Programmet har redan skrivit varje kontrolls status och belägg. "
        "Förklara vilken risk varje kontroll riktar sig mot och vad belägget visar. Om effekten inte är belagd ska det "
        "framgå att kontrollen inte sänker risknivån, eftersom vägledningen kräver att effekten bedöms innan riskerna "
        "vägs samman.\n"
        "Skriv bara att en kontroll minskar, begränsar eller reducerar risk när faktabladet visar en belagd effekt. En "
        "beskriven kontroll, någon annans kundkännedom eller ett system ersätter inte en belagd effekt, och hög "
        "inneboende risk kan inte elimineras helt med kontroller."
    ),
    "risknivaer": (
        "Skriv motiveringen under Risknivåer och motivering. Programmet har redan skrivit nivåmeningarna och jämförelsen "
        "med sektorns nivå; ange inga nivåer själv. Förklara nivån som en kedja: vilka hot som kan utnyttja vilka "
        "sårbarheter, hur tjänstens omfattning påverkar sannolikheten och vilken konsekvensen blir. Om tjänstens nivå "
        "avviker från sektorns nivå i den nationella riskbedömningen, förklara avvikelsen med regelspåren i faktabladet, "
        "eftersom föreskrifterna kräver att risknivåerna motiveras.\n"
        "Använd de maskinellt validerade delarna som underlag och upprepa dem inte. Minst ett stycke ska ha typen "
        "motivering och hänvisa till minst ett hot och en sårbarhet eller uppgift."
    ),
    "slutsatser": (
        "Skriv delen Slutsatser för tjänsten. Förklara vad motorns nivå betyder för just den här tjänsten: vilken "
        "kundkännedom som behövs, vad övervakningen ska fokusera på och vad utbildningen ska innehålla, kopplat till de "
        "identifierade hoten. Penningtvättslagen kräver att riskbedömningen ligger till grund för rutiner och utbildning, "
        "och tillsynen kritiserar slutsatser som bara upprepar nivån eller lovar allmänt att rutinerna ska anpassas.\n"
        "Programmet har redan skrivit meningen om byråns ansvar och beslut. Skriv inte att kundkännedom kan utelämnas."
    ),
}
```

- [x] **Step 5: Meddelandebyggaren och paketet**

`promptar/meddelande.py`:

```python
"""Användarmeddelandet i fast ordning: faktablad först, uppgiften sist (spec 8.4.2)."""

from riskanalys.dokument.faktablad import Faktablad, faktablad_json
from riskanalys.dokument.promptar.delar import MODULER


def _block(tagg: str, innehall: str, *, attribut: str = "") -> dict:
    return {"type": "text", "text": f"<{tagg}{attribut}>\n{innehall}\n</{tagg}>"}


def bygg_innehall(fb: Faktablad, del_id: str, lasta: tuple[str, ...], maskinellt_validerat: tuple[str, ...],
                  aterkoppling: tuple[str, ...]) -> list[dict]:
    block = [{**_block("faktablad", faktablad_json(fb)), "cache_control": {"type": "ephemeral"}}]
    if lasta:
        block.append(_block("lasta_meningar", "\n".join(lasta)))
    if maskinellt_validerat:
        block.append(_block("maskinellt_validerat", "\n\n".join(maskinellt_validerat)))
    block.append(_block("uppgift", MODULER[del_id], attribut=f' del="{del_id}"'))
    if aterkoppling:
        rader = "\n".join(f"- {rad}" for rad in aterkoppling)
        block.append(_block("aterkoppling", f"Förra försöket underkändes. Rätta detta:\n{rader}"))
    return block
```

`promptar/__init__.py`:

```python
"""Promptarnas delar och deras kontrollsummor."""

from riskanalys.dokument.aischema import SCHEMAVERSION
from riskanalys.dokument.promptar.delar import DELAR, MODULER
from riskanalys.dokument.promptar.meddelande import bygg_innehall
from riskanalys.dokument.promptar.system import systemprompt
from riskanalys.lagring.kontrollsumma import for_text


def delmodul(del_id: str) -> str:
    return MODULER[del_id]


def promptsumma(modell: str, del_id: str) -> str:
    """Kontrollsumma över systemprompt, delmodul och schemaversion (spec 8.4.7)."""
    return for_text("\n".join((systemprompt(modell), MODULER[del_id], SCHEMAVERSION)))


__all__ = ["DELAR", "bygg_innehall", "delmodul", "promptsumma", "systemprompt"]
```

- [x] **Step 6: Kör proven**

Run: `.venv/bin/pytest tester/enhet/test_promptar.py -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/riskanalys/dokument/promptar tester/enhet/test_promptar.py tester/enhet/conftest.py
git commit -m "feat: gemensam systemprompt med regler och skäl samt delmoduler"
```

---

### Task 8: Delkontroller

**Files:**
- Create: `src/riskanalys/dokument/delvalidering.py`
- Test: `tester/enhet/test_delvalidering.py` (ny)

**Interfaces:**
- Consumes: `platshallarfel`, `faltid_fel` (6); `nivapastaenden`, `FORBJUDNA_FORMULERINGAR`, `VERIFIERA` i `validering.py`; `Faktablad` (5); `AISvar` (2); `kontrollstatus` i `dokument/underlag.py`.
- Produces: `validera_del(del_id: str, svar: AISvar, fb: Faktablad, personnamn: tuple[str, ...], lasta: tuple[str, ...]) -> list[str]`; `LANGD: dict[str, tuple[int, int]]` (ord per del, metodval).

- [x] **Step 1: Skriv de fallerande proven**

```python
from riskanalys.dokument.delvalidering import validera_del
from riskanalys.dokument.modeller import AIStycke, AISvar

FYLLNAD = " Byrån konterar kundernas underlag och stämmer av dem mot bankens uppgifter varje månad." * 10


def _svar(*stycken):
    return AISvar(stycken=[AIStycke(typ=t, referenser=r, text=x) for t, r, x in stycken], oklarheter=[])


def test_hot_kraver_tva_hot_id(faktablad_exempel):
    fel = validera_del("hot", _svar(("analys", ["T-RED-01", "H-01"], "Hotet gäller." + FYLLNAD)), faktablad_exempel, (), ())
    assert any("minst två hot" in f for f in fel)


def test_noll_rapporter_far_inte_bli_argument(faktablad_exempel):
    text = "Inga rapporter har lämnats, vilket visar att hotet är litet." + FYLLNAD
    fel = validera_del("hot", _svar(("analys", ["T-RED-01", "H-01", "H-02"], text)), faktablad_exempel, (), ())
    assert any("rapporter" in f for f in fel)


def test_siffror_utanfor_platshallare_underkanns(faktablad_exempel):
    fel = validera_del("hot", _svar(("analys", ["T-RED-01", "H-01", "H-02"], "Tjänsten har 120 kunder." + FYLLNAD)),
                       faktablad_exempel, (), ())
    assert any("siffror" in f for f in fel)


def test_slutsatser_maste_namna_kundkannedom_overvakning_utbildning(faktablad_exempel):
    fel = validera_del("slutsatser", _svar(("analys", ["T-RED-01", "H-01"], "Byrån följer upp." + FYLLNAD)), faktablad_exempel, (), ())
    assert any("kundkännedom" in f for f in fel)


def test_last_mening_far_inte_upprepas(faktablad_exempel):
    last = "Den kvarstående risken är hög."
    fel = validera_del("risknivaer", _svar(("motivering", ["T-RED-01", "H-01", "P-KUND.antal_aktiva"], last + FYLLNAD)),
                       faktablad_exempel, (), (last,))
    assert any("låst mening" in f for f in fel)


def test_godkand_del_ger_inga_fel(faktablad_exempel):
    text = "Osanna fakturor kan bokföras som kostnader och brottsvinster kan redovisas som intäkter." + FYLLNAD
    assert validera_del("hot", _svar(("analys", ["T-RED-01", "H-01", "H-02"], text)), faktablad_exempel, (), ()) == []
```

Lägg dessutom till prov för kontroller (ett stycke med "minskar" utan referens till en kontroll med belagd effekt underkänns) och sårbarheter (ett analysstycke med två `S-`-referenser underkänns, samma stycke som `scenario` godkänns). Bygg dem på en kopia av `faktablad_exempel` med `UnderlagKontroll` och `UnderlagSarbarhet` tillagda.

- [x] **Step 2: Kör proven och se dem fallera**

Run: `.venv/bin/pytest tester/enhet/test_delvalidering.py -v`
Expected: FAIL (`delvalidering` saknas).

- [x] **Step 3: Implementera**

```python
"""Kontroller per analysdel (spec 8.4.4–8.4.5). Avgör bara det som kan avgöras maskinellt."""

import re

from riskanalys.dokument.faktablad import Faktablad
from riskanalys.dokument.modeller import AISvar
from riskanalys.dokument.platshallare import faltid_fel, platshallarfel
from riskanalys.dokument.validering import FORBJUDNA_FORMULERINGAR, VERIFIERA, nivapastaenden

# Ord per del. Metodval som prövas i piloten.
LANGD = {"hot": (80, 450), "sarbarheter": (100, 600), "kontroller": (60, 400), "risknivaer": (80, 400), "slutsatser": (80, 400)}
_NOLL_RAPPORTER = re.compile(r"\b(?:inga|få|noll)\s+(?:misstanke)?rapporter\b[^.]*\b(?:visar|därför|innebär|tyder)\b", re.IGNORECASE)
_MINSKNING = re.compile(r"\b(?:minskar|begränsar|reducerar|sänker)\b", re.IGNORECASE)
_TILLATNA_SIFFROR = re.compile(r"\{[^{}]*\}|\[VERIFIERA\]|\b(?:19|20)\d\d\b|\b\d+\s*(?:kap\.|§)")
_BELAGD_EFFEKT = "belagd effekt"  # ändra till den text som kontrollstatus() använder för belagd effekt


def _stycke(n: int, s, fb: Faktablad, numeriska: dict[str, str], okanda: set[str], personnamn, lasta) -> list[str]:
    liten = s.text.lower()
    fel = [] if s.referenser else [f"Stycke {n} saknar referenser."]
    fel += [f"Stycke {n} hänvisar till {r}, som inte finns i faktabladet." for r in s.referenser if r not in fb.tillatna_id()]
    fel += platshallarfel(n, s.text, s.referenser, numeriska)
    fel += faltid_fel(n, s.text)
    if nivapastaenden(s.text):
        fel.append(f"Stycke {n} anger en nivå. Programmet skriver alla nivåmeningar; beskriv faktorer med andel, antal, period och egenskap.")
    if re.search(r"\d", _TILLATNA_SIFFROR.sub("", s.text)):
        fel.append(f"Stycke {n} innehåller siffror. Skriv tal som {{tal:ID}}.")
    if set(s.referenser) & okanda and VERIFIERA not in s.text:
        fel.append(f"Stycke {n} bygger på obekräftade uppgifter men saknar {VERIFIERA}.")
    fel += [f'Stycke {n} innehåller den förbjudna formuleringen "{f}".' for f in FORBJUDNA_FORMULERINGAR if f in liten]
    if any(namn.lower() in liten for namn in personnamn):
        fel.append(f"Stycke {n} innehåller ett personnamn. Skriv {{roll:FfR}} i stället.")
    fel += [f"Stycke {n} upprepar en låst mening. Bygg vidare på den i stället." for last in lasta if last and last in s.text]
    return fel


def _gemensamma(svar: AISvar, fb: Faktablad, personnamn, lasta) -> list[str]:
    numeriska = fb.numeriska()
    okanda = {p.id for p in fb.poster if p.status != "bekräftad"}
    fel = [] if svar.stycken else ["Delen har inga stycken."]
    fel += [f"Oklarhet {n}: {o.uppgift_id} finns inte i faktabladet." for n, o in enumerate(svar.oklarheter, 1)
            if o.uppgift_id not in fb.uppgift_id()]
    for n, s in enumerate(svar.stycken, 1):
        fel += _stycke(n, s, fb, numeriska, okanda, personnamn, lasta)
    return fel


def _per_del(del_id: str, svar: AISvar, fb: Faktablad) -> list[str]:
    refs = [r for s in svar.stycken for r in s.referenser]
    text = " ".join(s.text for s in svar.stycken)
    fel = []
    if del_id == "hot":
        if len({r for r in refs if r.startswith("H-")}) < 2:
            fel.append("Delen ska hänvisa till minst två hot (H-) ur faktabladet.")
        if _NOLL_RAPPORTER.search(text):
            fel.append("Få eller inga rapporter får inte användas som belägg för att hotet är litet.")
    if del_id == "sarbarheter":
        fel += [f"Stycke {n} beskriver en kombination utan belagt överlapp. Använd stycketypen scenario."
                for n, s in enumerate(svar.stycken, 1)
                if s.typ == "analys" and len({r for r in s.referenser if r.startswith("S-")}) >= 2]
    if del_id == "kontroller":
        belagda = {k.id for k in fb.kontroller if _BELAGD_EFFEKT in k.status}
        fel += [f"Stycke {n} säger att risken minskar utan hänvisning till en kontroll med belagd effekt."
                for n, s in enumerate(svar.stycken, 1) if _MINSKNING.search(s.text) and not set(s.referenser) & belagda]
    if del_id == "risknivaer" and not any(
            s.typ == "motivering" and any(r.startswith("H-") for r in s.referenser)
            and any(r.startswith(("S-", "P-")) for r in s.referenser) for s in svar.stycken):
        fel.append("Minst ett stycke av typen motivering ska hänvisa till ett hot och en sårbarhet eller uppgift.")
    if del_id == "slutsatser":
        fel += [f"Slutsatserna ska ta upp {ord_} i tjänsten." for ord_ in ("kundkännedom", "övervakning", "utbildning")
                if ord_ not in text.lower()]
        if not any(r.startswith("H-") for r in refs):
            fel.append("Slutsatserna ska hänvisa till minst ett hot (H-).")
    lagst, hogst = LANGD[del_id]
    antal = len(text.split())
    if not lagst <= antal <= hogst:
        fel.append(f"Delen ska vara {lagst}–{hogst} ord; den är {antal} ord.")
    return fel


def validera_del(del_id: str, svar: AISvar, fb: Faktablad, personnamn: tuple[str, ...], lasta: tuple[str, ...]) -> list[str]:
    return [*_gemensamma(svar, fb, personnamn, lasta), *_per_del(del_id, svar, fb)]
```

Läs `kontrollstatus` i `src/riskanalys/dokument/underlag.py` och sätt `_BELAGD_EFFEKT` till exakt den delsträng som funktionen använder när effekten är belagd. Lägg till ett prov som bygger statusen med `kontrollstatus` för en belagd kontroll, så att konstanten och funktionen inte kan glida isär.

- [x] **Step 4: Kör proven**

Run: `.venv/bin/pytest tester/enhet/test_delvalidering.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/riskanalys/dokument/delvalidering.py tester/enhet/test_delvalidering.py
git commit -m "feat: maskinella kontroller per analysdel"
```

---

### Task 9: Leverantörsanrop per del med strömning och cachefält

**Files:**
- Modify: `src/riskanalys/dokument/leverantor.py` (`Tokenanvandning`, `Anropsdata`, ny `Delanrop`, `Textleverantor`, `Testleverantor`)
- Modify: `src/riskanalys/dokument/claude.py` (ny `skriv_del`, `_anvandning`)
- Test: `tester/enhet/test_leverantor.py`, `tester/enhet/test_claude.py`

**Interfaces:**
- Produces:
  - `Delanrop(del_id: str, system: str, innehall: list[dict], schema: dict, effort: str, max_tokens: int, promptsumma: str)`.
  - `Textleverantor.skriv_del(anrop: Delanrop) -> Leveranssvar`.
  - `Tokenanvandning.cache_lasning_token: int = 0`, `cache_skrivning_token: int = 0`; `Anropsdata.del_id: str | None = None`.
  - `ClaudeLeverantor.skriv_del` strömmar när `max_tokens > 16000`. Stoppskälen `max_tokens` och `refusal` blir `avbrott`; anroparen (uppgift 10) räknar det som misslyckat försök.

- [x] **Step 1: Skriv de fallerande proven**

I `tester/enhet/test_leverantor.py`:

```python
from riskanalys.dokument.leverantor import Delanrop, Testleverantor
from riskanalys.dokument.modeller import AIStycke, AISvar

ANROP = Delanrop(del_id="hot", system="s", innehall=[{"type": "text", "text": "x"}], schema={}, effort="high",
                 max_tokens=16000, promptsumma="abc")


def test_testleverantor_skriver_delar_i_tur_och_ordning():
    svar = AISvar(stycken=[AIStycke(typ="analys", referenser=["T-RED-01"], text="Text.")], oklarheter=[])
    lev = Testleverantor([svar, "inte json"])
    forsta = lev.skriv_del(ANROP)
    assert forsta.text == svar.model_dump_json()
    assert (forsta.anrop.del_id, forsta.anrop.prompt_kontrollsumma, forsta.anrop.effort) == ("hot", "abc", "high")
    assert lev.skriv_del(ANROP).text == "inte json"
    assert lev.delanrop == [ANROP, ANROP]
```

I `tester/enhet/test_claude.py`, utöka filens befintliga falska klient så att `beta.messages.stream(**kw)` är en kontexthanterare med `get_final_message()` som räknar `stromningar`, och så att en variant returnerar `stop_reason="max_tokens"`. Prov:

```python
def test_skriv_del_strommar_vid_hog_max_tokens(falsk_klient):
    lev = ClaudeLeverantor(klient=falsk_klient)
    lev.skriv_del(Delanrop(del_id="hot", system="s", innehall=[{"type": "text", "text": "x"}], schema={"type": "object"},
                           effort="high", max_tokens=32000, promptsumma="abc"))
    assert falsk_klient.stromningar == 1


def test_max_tokens_blir_avbrott(falsk_klient_max_tokens):
    svar = ClaudeLeverantor(klient=falsk_klient_max_tokens).skriv_del(
        Delanrop(del_id="hot", system="s", innehall=[], schema={}, effort="high", max_tokens=16000, promptsumma="abc"))
    assert svar.avbrott is not None and svar.anrop.del_id == "hot"
```

- [x] **Step 2: Kör proven och se dem fallera**

Run: `.venv/bin/pytest tester/enhet/test_leverantor.py tester/enhet/test_claude.py -v`
Expected: FAIL (`Delanrop` saknas).

- [x] **Step 3: Implementera i `leverantor.py`**

```python
class Tokenanvandning(Last):
    """Tokenanvändning för ett försök hos leverantören."""

    typ: str
    modell: str | None
    indata_token: int
    utdata_token: int
    cache_lasning_token: int = 0
    cache_skrivning_token: int = 0


class Delanrop(Last):
    """Ett anrop för en analysdel: fast systemprompt, innehåll i fast ordning och schema (spec 8.4.2)."""

    del_id: str
    system: str
    innehall: list[dict]
    schema: dict
    effort: str
    max_tokens: int
    promptsumma: str
```

Lägg till `del_id: str | None = None` sist i `Anropsdata` och `def skriv_del(self, anrop: Delanrop) -> Leveranssvar: ...` i `Textleverantor`.

I `Testleverantor`: `self.delanrop: list[Delanrop] = []` i `__init__`, typen för `svar` blir `list[AvsnittsUtkast | AISvar | str]`, och:

```python
    def skriv_del(self, anrop: Delanrop) -> Leveranssvar:
        self.delanrop.append(anrop)
        nummer = len(self.anrop) + len(self.delanrop)
        if nummer > len(self._svar):
            raise LeverantorFel(f"Testleverantören har bara {len(self._svar)} förberedda svar.")
        svar = self._svar[nummer - 1]
        return Leveranssvar(
            anrop=Anropsdata(leverantor=self.namn, begard_modell=self.modell, svarsmodell=self.modell, effort=anrop.effort,
                             prompt_kontrollsumma=anrop.promptsumma, svar_id=f"test-{nummer}", stop_reason="end_turn",
                             reservmodell_svarade=False, anvandning=(), tidpunkt=datetime.now(timezone.utc),
                             del_id=anrop.del_id),
            text=svar if isinstance(svar, str) else svar.model_dump_json(),
            avbrott=None,
        )
```

- [x] **Step 4: Implementera i `claude.py`**

```python
STROMNINGSGRANS = 16000

    def skriv_del(self, anrop: Delanrop) -> Leveranssvar:
        parametrar = dict(
            model=self.modell, max_tokens=anrop.max_tokens, system=anrop.system,
            messages=[{"role": "user", "content": anrop.innehall}],
            output_config={"effort": anrop.effort, "format": {"type": "json_schema", "schema": anrop.schema}},
            betas=[FALLBACK_BETA], fallbacks="default",
        )
        try:
            if anrop.max_tokens > STROMNINGSGRANS:
                with self._klient.beta.messages.stream(**parametrar) as strom:
                    svar = strom.get_final_message()
            else:
                svar = self._klient.beta.messages.create(**parametrar)
        except anthropic.APIStatusError as fel:
            raise LeverantorFel(f"Claude-API:t svarade med fel {fel.status_code}: {fel.message}") from fel
        except anthropic.APIConnectionError as fel:
            raise LeverantorFel("Kunde inte nå Claude-API:t. Kontrollera nätverket och försök igen.") from fel
        leverans = self._leveranssvar(svar)
        anropsdata = leverans.anrop.model_copy(update={"del_id": anrop.del_id, "prompt_kontrollsumma": anrop.promptsumma,
                                                       "effort": anrop.effort})
        return leverans.model_copy(update={"anrop": anropsdata})
```

I `_anvandning`, lägg till i varje `Tokenanvandning`:

```python
            cache_lasning_token=getattr(post, "cache_read_input_tokens", 0) or 0,
            cache_skrivning_token=getattr(post, "cache_creation_input_tokens", 0) or 0,
```

- [x] **Step 5: Kör proven**

Run: `.venv/bin/pytest tester/enhet/test_leverantor.py tester/enhet/test_claude.py tester/enhet/test_skrivning.py -v`
Expected: PASS. Sparade körningar utan de nya fälten kan fortfarande läsas, eftersom fälten har standardvärden.

- [ ] **Step 6: Commit**

```bash
git add src/riskanalys/dokument/leverantor.py src/riskanalys/dokument/claude.py tester/enhet/test_leverantor.py tester/enhet/test_claude.py
git commit -m "feat: leverantörsanrop per del med strömning och cachefält"
```

---

### Task 10: Anropsflöde per tjänst med omförsök och mallreserv

**Files:**
- Create: `src/riskanalys/dokument/delskrivning.py`
- Modify: `src/riskanalys/dokument/skrivning.py` (`kor_skrivning` använder det nya flödet för det nya dokumentformatet; `las_skrivresultat`)
- Test: `tester/intag/test_delskrivning.py` (ny)

**Interfaces:**
- Consumes: `bygg_faktablad` (5), `promptar.*` (7), `validera_del` (8), `Delanrop`, `skriv_del` (9), `ai_schema`, `AISvar` (2), `nivastycken` (3); befintliga `erfarenhetsstycke`, `sarbarhetsstycke`, `kontrollstycken`.
- Produces:
  - `FORMATVERSION = "D-ARB-tjanst-v3"`, `ANSVARSMENING: str`, `MAX_OMFORSOK = 2`, `EFFORTSTEG: dict[str, str]`.
  - `Delforsok(nummer, effort, anrop, text, svar: AISvar | None, fel)`; `Delresultat(del_id, forsok, mall)` med `godkant_svar -> AISvar | None` och `kontrollsumma() -> str`; `Tjanstresultat(avsnitt, tjanst, design, formatversion, faktablad, delar)` med `del_(del_id) -> Delresultat`.
  - `lasta_texter(regelbas, profil, t, del_id) -> tuple[str, ...]`.
  - `skriv_tjanst(leverantor, regelbas, profil, t, avsnitt_id, *, design: Literal["A", "B"] = "B", effort: str, personnamn: tuple[str, ...], spara: Callable[[str, Delforsok], None]) -> Tjanstresultat`.

- [x] **Step 1: Skriv de fallerande proven**

```python
import pytest

from riskanalys.bedomning.korning import kor_bedomning, las_bedomning
from riskanalys.dokument.delskrivning import skriv_tjanst
from riskanalys.dokument.leverantor import LeverantorFel, Testleverantor
from riskanalys.dokument.modeller import AIStycke, AISvar
from riskanalys.dokument.promptar import DELAR
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.profil.lagring import spara_profil

FYLLNAD = " Byrån konterar kundernas underlag och stämmer av dem mot bankens uppgifter varje månad." * 10


def tjanst_for_prov(mapp, rb, profil):
    spara_profil(mapp, profil)
    b = las_bedomning(kor_bedomning(mapp, rb))
    return tjanster_med_avsnitt(b)[0]


def godkant_delsvar(del_id, t):
    hot = list(t.hot)
    sar = list(t.tillampade_sarbarheter[:1]) or ["S-KUND-01"]
    referenser = {"hot": [t.tjanst, *hot[:2]], "sarbarheter": [t.tjanst, *sar], "kontroller": [t.tjanst],
                  "risknivaer": [t.tjanst, hot[0], *sar], "slutsatser": [t.tjanst, hot[0]]}[del_id]
    extra = " Kundkännedom, övervakning och utbildning anpassas efter hoten." if del_id == "slutsatser" else ""
    typ = "motivering" if del_id == "risknivaer" else "analys"
    return AISvar(stycken=[AIStycke(typ=typ, referenser=referenser, text="Tjänstens flöden kan utnyttjas." + FYLLNAD + extra)],
                  oklarheter=[])


def _skriv(lev, rb, profil, t, avsnitt_id, effort="high", design="B"):
    return skriv_tjanst(lev, rb, profil, t, avsnitt_id, design=design, effort=effort, personnamn=(), spara=lambda d, f: None)


def test_design_b_ett_anrop_per_del_och_kedjat_underlag(tmp_path, rb_intag, klar):
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    lev = Testleverantor([godkant_delsvar(d, t) for d in DELAR])
    res = _skriv(lev, rb_intag, klar, t, avsnitt_id)
    assert [a.del_id for a in lev.delanrop] == list(DELAR)
    assert not any(d.mall for d in res.delar)
    motivering = next(a for a in lev.delanrop if a.del_id == "risknivaer")
    assert any(b["text"].startswith("<maskinellt_validerat>") for b in motivering.innehall)


def test_underkand_del_kors_om_hogst_tva_ganger_med_hojd_effort_och_blir_mall(tmp_path, rb_intag, klar):
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    dalig = AISvar(stycken=[AIStycke(typ="analys", referenser=[t.tjanst], text="Risken är hög.")], oklarheter=[])
    lev = Testleverantor([dalig, dalig, dalig] + [godkant_delsvar(d, t) for d in DELAR[1:]])
    hot = _skriv(lev, rb_intag, klar, t, avsnitt_id, effort="medium").del_("hot")
    assert hot.mall and len(hot.forsok) == 3
    assert [f.effort for f in hot.forsok] == ["medium", "medium", "high"]


def test_ogiltigt_svar_i_en_del_kraschar_inte_hela_tjansten(tmp_path, rb_intag, klar):
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    lev = Testleverantor(["", "", ""] + [godkant_delsvar(d, t) for d in DELAR[1:]])
    res = _skriv(lev, rb_intag, klar, t, avsnitt_id)
    assert res.del_("hot").mall and not res.del_("slutsatser").mall


def test_design_a_ger_tydligt_fel_tills_den_byggts(tmp_path, rb_intag, klar):
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    with pytest.raises(LeverantorFel, match="Design A"):
        _skriv(Testleverantor([]), rb_intag, klar, t, avsnitt_id, design="A")
```

Flytta `FYLLNAD`, `tjanst_for_prov` och `godkant_delsvar` till `tester/fixturer/m2.py` om uppgift 11 behöver dem (den gör det), och importera dem därifrån i båda provfilerna.

- [x] **Step 2: Kör proven och se dem fallera**

Run: `.venv/bin/pytest tester/intag/test_delskrivning.py -v`
Expected: FAIL (`delskrivning` saknas).

- [x] **Step 3: Implementera `delskrivning.py`**

```python
"""Anropsflöde per tjänst: ett anrop per analysdel, kedjat, med omförsök och mallreserv (spec 8.4.3, 8.4.5)."""

from collections.abc import Callable
from typing import Literal

from pydantic import ValidationError

from riskanalys.dokument.aischema import ai_schema
from riskanalys.dokument.analysunderlag import erfarenhetsstycke, sarbarhetsstycke
from riskanalys.dokument.delvalidering import validera_del
from riskanalys.dokument.faktablad import Faktablad, bygg_faktablad
from riskanalys.dokument.leverantor import Anropsdata, Delanrop, LeverantorFel
from riskanalys.dokument.modeller import AISvar, Last
from riskanalys.dokument.nivatext import nivastycken
from riskanalys.dokument.promptar import DELAR, bygg_innehall, promptsumma, systemprompt
from riskanalys.dokument.tjanstavsnitt import kontrollstycken
from riskanalys.lagring.kontrollsumma import for_text

FORMATVERSION = "D-ARB-tjanst-v3"
MAX_OMFORSOK = 2
MAX_TOKENS = 16000
EFFORTSTEG = {"low": "medium", "medium": "high", "high": "xhigh", "xhigh": "max", "max": "max"}
ANSVARSMENING = ("Byrån beslutar ansvariga, tidsfrister, faktisk kundkännedom och uppföljningstakt. "
                 "Texten är ett analysunderlag och intygar inte genomförda åtgärder.")


class Delforsok(Last):
    nummer: int
    effort: str
    anrop: Anropsdata
    text: str
    svar: AISvar | None
    fel: tuple[str, ...]


class Delresultat(Last):
    del_id: str
    forsok: tuple[Delforsok, ...]
    mall: bool

    @property
    def godkant_svar(self) -> AISvar | None:
        if self.mall or not self.forsok or self.forsok[-1].fel:
            return None
        return self.forsok[-1].svar

    def kontrollsumma(self) -> str:
        svar = self.godkant_svar
        return for_text(svar.model_dump_json() if svar else "mall")


class Tjanstresultat(Last):
    avsnitt: str
    tjanst: str
    design: Literal["A", "B"]
    formatversion: str = FORMATVERSION
    faktablad: Faktablad
    delar: tuple[Delresultat, ...]

    def del_(self, del_id: str) -> Delresultat:
        return next(d for d in self.delar if d.del_id == del_id)


def lasta_texter(regelbas, profil, t, del_id: str) -> tuple[str, ...]:
    """Kodens låsta stycken i delen. AI får se dem men inte upprepa dem (spec 8.4.1)."""
    if del_id == "hot":
        return (erfarenhetsstycke(regelbas, profil, t).text,)
    if del_id == "sarbarheter":
        tj = regelbas.tjanster[t.tjanst]
        return tuple(sarbarhetsstycke(regelbas, profil, t.tjanst, id).text
                     for id in tj.sarbarheter if regelbas.sarbarheter[id].omrade == "geo")
    if del_id == "kontroller":
        return tuple(s.text for s in kontrollstycken(regelbas, profil, t))
    if del_id == "risknivaer":
        return tuple(s.text for s in nivastycken(t))
    return (ANSVARSMENING,)


def _tolka(text: str) -> tuple[AISvar | None, tuple[str, ...]]:
    try:
        return AISvar.model_validate_json(text), ()
    except ValidationError as fel:
        return None, (f"Svaret följde inte schemat ({fel.error_count()} fel). Svara bara med JSON enligt schemat.",)


def skriv_del(leverantor, fb: Faktablad, regelbas, profil, t, del_id: str, validerat: tuple[str, ...], *,
              effort: str, personnamn: tuple[str, ...], spara: Callable[[str, Delforsok], None]) -> Delresultat:
    lasta = lasta_texter(regelbas, profil, t, del_id)
    schema = ai_schema(fb.tillatna_id(), fb.uppgift_id())
    forsok: tuple[Delforsok, ...] = ()
    aterkoppling: tuple[str, ...] = ()
    for nummer in range(1, MAX_OMFORSOK + 2):
        niva = effort if nummer <= MAX_OMFORSOK else EFFORTSTEG[effort]
        anrop = Delanrop(del_id=del_id, system=systemprompt(leverantor.modell),
                         innehall=bygg_innehall(fb, del_id, lasta, validerat, aterkoppling), schema=schema,
                         effort=niva, max_tokens=MAX_TOKENS, promptsumma=promptsumma(leverantor.modell, del_id))
        leverans = leverantor.skriv_del(anrop)
        svar, fel = (None, (leverans.avbrott,)) if leverans.avbrott else _tolka(leverans.text)
        if svar is not None:
            fel = tuple(validera_del(del_id, svar, fb, personnamn, lasta))
        post = Delforsok(nummer=nummer, effort=niva, anrop=leverans.anrop, text=leverans.text, svar=svar, fel=fel)
        spara(del_id, post)
        forsok = (*forsok, post)
        if not fel:
            return Delresultat(del_id=del_id, forsok=forsok, mall=False)
        aterkoppling = fel
    return Delresultat(del_id=del_id, forsok=forsok, mall=True)


def skriv_tjanst(leverantor, regelbas, profil, t, avsnitt_id: str, *, design: Literal["A", "B"] = "B", effort: str,
                 personnamn: tuple[str, ...], spara: Callable[[str, Delforsok], None]) -> Tjanstresultat:
    if design != "B":
        raise LeverantorFel("Design A är inte byggd ännu; använd design B.")
    fb = bygg_faktablad(regelbas, profil, t, avsnitt_id)
    delar: dict[str, Delresultat] = {}

    def validerad(*ids: str) -> tuple[str, ...]:
        return tuple(s.text for id in ids if (svar := delar[id].godkant_svar) for s in svar.stycken)

    for del_id in DELAR:
        underlag = {"risknivaer": validerad("hot", "sarbarheter", "kontroller"),
                    "slutsatser": validerad("risknivaer")}.get(del_id, ())
        delar[del_id] = skriv_del(leverantor, fb, regelbas, profil, t, del_id, underlag,
                                  effort=effort, personnamn=personnamn, spara=spara)
    return Tjanstresultat(avsnitt=avsnitt_id, tjanst=t.tjanst, design=design, faktablad=fb, delar=tuple(delar.values()))
```

- [x] **Step 4: Koppla in flödet i `kor_skrivning`**

I `src/riskanalys/dokument/skrivning.py`, `kor_skrivning`: när `regelbas.metod.omfattning` är satt (det nya dokumentformatet), skriv varje tjänst med `skriv_tjanst`. Det äldre flödet behålls för regelbaser utan `metod.omfattning`.

```python
        if regelbas.metod.omfattning:
            from riskanalys.dokument.delskrivning import skriv_tjanst
            resultat = skriv_tjanst(leverantor, regelbas, profil, tjanst, avsnitt_id, design="B",
                                    effort=getattr(leverantor, "effort", None) or "high", personnamn=namn,
                                    spara=partial(_spara_delforsok, avsnittsmapp))
        else:
            resultat = skriv_avsnitt(leverantor, underlag, namn, partial(_spara_forsok, avsnittsmapp))
```

```python
def _spara_delforsok(avsnittsmapp: Path, del_id: str, forsok) -> None:
    (avsnittsmapp / f"{del_id}-forsok-{forsok.nummer}.json").write_text(forsok.model_dump_json(indent=2), encoding="utf-8")
```

Lägg `"format": "D-ARB-tjanst-v3"` och `"design": "B"` i manifestets metadata när det nya flödet används. Låt `las_skrivresultat` läsa en fil som `Tjanstresultat` när den innehåller `"formatversion": "D-ARB-tjanst-v3"` och som `Skrivresultat` annars.

- [x] **Step 5: Kör proven**

Run: `.venv/bin/pytest tester/intag/test_delskrivning.py tester/enhet/test_skrivning.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/riskanalys/dokument/delskrivning.py src/riskanalys/dokument/skrivning.py tester/intag/test_delskrivning.py tester/fixturer/m2.py
git commit -m "feat: ett anrop per analysdel med omförsök, effortsteg och mallreserv"
```

---

### Task 11: Tjänsteavsnitt av delresultat och ny granskningsgrind

**Files:**
- Modify: `src/riskanalys/dokument/tjanstavsnitt.py` (ny `bygg_tjanstavsnitt_v3`)
- Modify: `src/riskanalys/dokument/arb.py:56-70` (v3-resultat ger v3-avsnitt)
- Modify: `src/riskanalys/granskning/korning.py:31-62` (`godkanda_utkast` läser `Tjanstresultat`; `oppna_fragor`)
- Modify: `src/riskanalys/granskning/analys.py` (grinden enligt spec 8.4.6; `mallfynd`)
- Modify: `src/riskanalys/intag/dokument.py:22-23` (kräver inte godkända AI-delar i v3)
- Test: `tester/intag/test_v3_grind.py` (ny), `tester/enhet/test_sakgranskning.py`

**Interfaces:**
- Consumes: `Tjanstresultat`, `Delresultat`, `ANSVARSMENING` (10); `ersatt_tal` (6); `bygg_faktablad` (5); `nivastycken` (3); befintliga `bygg_tjanstavsnitt`, `erfarenhetsstycke`, `sarbarhetsstycke`, `kontrollstycken`, `slutsatsstycken`.
- Produces: `bygg_tjanstavsnitt_v3(rb, p, t, resultat: Tjanstresultat, avsnitt_id: str) -> Avsnitt` (kastar `RiskanalysFel` vid olöst platshållare); `analys.mallfynd(resultat: Tjanstresultat) -> list[dict]`.

- [x] **Step 1: Skriv de fallerande proven**

```python
import pytest

from riskanalys.dokument.delskrivning import skriv_tjanst
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.modeller import AIStycke
from riskanalys.dokument.promptar import DELAR
from riskanalys.dokument.tjanstavsnitt import bygg_tjanstavsnitt_v3
from riskanalys.fel import RiskanalysFel
from riskanalys.granskning.analys import mallfynd
from tester.fixturer.m2 import godkant_delsvar, tjanst_for_prov


@pytest.fixture
def v3(tmp_path, rb_intag, klar):
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    res = skriv_tjanst(Testleverantor([godkant_delsvar(d, t) for d in DELAR]), rb_intag, klar, t, avsnitt_id,
                       design="B", effort="high", personnamn=(), spara=lambda d, f: None)
    return rb_intag, klar, t, res, avsnitt_id


def _med_hottext(res, t, text):
    def byt(d):
        if d.del_id != "hot":
            return d
        sista = d.forsok[-1]
        svar = sista.svar.model_copy(update={"stycken": [AIStycke(typ="analys", referenser=[t.tjanst], text=text)]})
        return d.model_copy(update={"forsok": (*d.forsok[:-1], sista.model_copy(update={"svar": svar}))})
    return res.model_copy(update={"delar": tuple(byt(d) for d in res.delar)})


def test_v3_har_sex_delar_och_lasta_stycken_pa_plats(v3):
    rb, p, t, res, avsnitt_id = v3
    a = bygg_tjanstavsnitt_v3(rb, p, t, res, avsnitt_id)
    assert [u.rubrik for u in a.underrubriker] == ["Beskrivning och omfattning", "Hot och egna erfarenheter",
        "Sårbarheter och motivering", "Kontroller och effekt", "Risknivåer och motivering", "Slutsatser"]
    texter = [s.text for s in a.stycken]
    assert any(x.startswith("Egen erfarenhet i hotanalysen") for x in texter)
    assert texter[-1].startswith("Byrån beslutar ansvariga")


def test_samma_underlag_ger_samma_summa_och_andrad_ai_text_avviker(v3):
    rb, p, t, res, avsnitt_id = v3
    a = bygg_tjanstavsnitt_v3(rb, p, t, res, avsnitt_id)
    assert a.kontrollsumma() == bygg_tjanstavsnitt_v3(rb, p, t, res, avsnitt_id).kontrollsumma()
    assert bygg_tjanstavsnitt_v3(rb, p, t, _med_hottext(res, t, "Ändrad."), avsnitt_id).kontrollsumma() != a.kontrollsumma()


def test_olost_platshallare_stoppar_sammanstallningen(v3):
    rb, p, t, res, avsnitt_id = v3
    with pytest.raises(RiskanalysFel):
        bygg_tjanstavsnitt_v3(rb, p, t, _med_hottext(res, t, "{tal:P-SAKNAS.x} kunder."), avsnitt_id)


def test_ny_profil_efter_skrivning_ger_annan_summa(v3):
    rb, p, t, res, avsnitt_id = v3
    numeriska = res.faktablad.numeriska()
    if not numeriska:
        pytest.skip("profilen saknar numeriska faktarader")
    id = next(iter(numeriska))
    text = f"Tjänsten berör {{tal:{id}}} kunder." + " Byrån konterar kundernas underlag." * 30
    def byt(d):
        if d.del_id != "hot":
            return d
        sista = d.forsok[-1]
        svar = sista.svar.model_copy(update={"stycken": [AIStycke(typ="analys", referenser=[t.tjanst, id], text=text)]})
        return d.model_copy(update={"forsok": (*d.forsok[:-1], sista.model_copy(update={"svar": svar}))})
    med_tal = res.model_copy(update={"delar": tuple(byt(d) for d in res.delar)})
    a = bygg_tjanstavsnitt_v3(rb, p, t, med_tal, avsnitt_id)
    andrad = p.model_copy(update={"uppgifter": {**p.uppgifter, id: p.uppgifter[id].model_copy(update={"varde": 999})}})
    assert bygg_tjanstavsnitt_v3(rb, andrad, t, med_tal, avsnitt_id).kontrollsumma() != a.kontrollsumma()


def test_mall_del_ger_blockerande_fynd(v3):
    rb, p, t, res, avsnitt_id = v3
    mall = res.model_copy(update={"delar": tuple(d.model_copy(update={"mall": d.del_id == "hot"}) for d in res.delar)})
    fynd = mallfynd(mall)
    assert len(fynd) == 1 and fynd[0]["allvar"] == "blockerande" and "hot" in fynd[0]["beskrivning"]
```

Lägg dessutom till ett regressionsprov i `tester/enhet/test_sakgranskning.py`. Ett sakgodkännande som sparats för ett tjänsteavsnitt i v2 ska inte gälla när samma tjänst byggs i v3. Använd filens befintliga hjälpfunktioner för att skapa ett godkännande och kontrollera att det rapporteras som inaktuellt.

- [x] **Step 2: Kör proven och se dem fallera**

Run: `.venv/bin/pytest tester/intag/test_v3_grind.py -v`
Expected: FAIL (`bygg_tjanstavsnitt_v3` saknas).

- [x] **Step 3: Implementera `bygg_tjanstavsnitt_v3`**

I `src/riskanalys/dokument/tjanstavsnitt.py`:

```python
def _ai_stycken(svar, numeriska: dict[str, str]) -> tuple[Textstycke, ...]:
    from riskanalys.dokument.platshallare import ersatt_tal
    return tuple(stycke(ersatt_tal(s.text, numeriska), s.referenser, typ=s.typ) for s in svar.stycken)


def bygg_tjanstavsnitt_v3(rb: Regelbas, p: Profil, t: Tjanstbedomning, resultat, avsnitt_id: str) -> Avsnitt:
    """Låsta stycken byggs om ur profil och bedömning; AI-stycken kommer från maskinellt validerade delar (spec 8.4.6)."""
    from riskanalys.dokument.delskrivning import ANSVARSMENING
    from riskanalys.dokument.faktablad import bygg_faktablad
    from riskanalys.dokument.nivatext import nivastycken
    tj = rb.tjanster[t.tjanst]
    numeriska = bygg_faktablad(rb, p, t, avsnitt_id).numeriska()

    def ai(del_id: str, mall: tuple[Textstycke, ...]) -> tuple[Textstycke, ...]:
        svar = resultat.del_(del_id).godkant_svar
        return _ai_stycken(svar, numeriska) if svar else mall

    gammal = bygg_tjanstavsnitt(rb, p, t, AvsnittsUtkast(avsnitt=avsnitt_id, stycken=[], oklarheter=[]), avsnitt_id)
    beskrivning = gammal.stycken[:gammal.underrubriker[1].fore_stycke]
    hotmall = tuple(stycke(f'{rb.hot[id].namn}: {rb.hot[id].beskrivning}', [t.tjanst, id, *rb.hot[id].kallor]) for id in t.hot)
    geo = tuple(sarbarhetsstycke(rb, p, t.tjanst, id) for id in tj.sarbarheter if rb.sarbarheter[id].omrade == "geo")
    sarmall = tuple(sarbarhetsstycke(rb, p, t.tjanst, id) for id in tj.sarbarheter if rb.sarbarheter[id].omrade != "geo")
    mallmotivering = (stycke("Motiveringen kunde inte skrivas maskinellt och behöver kompletteras i sakgranskningen. [VERIFIERA]",
                             [t.tjanst], typ="motivering"),)
    delar = [
        ("Beskrivning och omfattning", tuple(beskrivning)),
        ("Hot och egna erfarenheter", (*ai("hot", hotmall), erfarenhetsstycke(rb, p, t))),
        ("Sårbarheter och motivering", (*geo, *ai("sarbarheter", sarmall))),
        ("Kontroller och effekt", (*kontrollstycken(rb, p, t), *ai("kontroller", ()))),
        ("Risknivåer och motivering", (*nivastycken(t), *ai("risknivaer", mallmotivering))),
        ("Slutsatser", (*ai("slutsatser", slutsatsstycken(rb, t)), stycke(ANSVARSMENING, [t.tjanst], typ="beskrivning"))),
    ]
    stycken, rubriker = [], []
    for rubrik, texter in delar:
        rubriker.append(Underrubrik(fore_stycke=len(stycken), rubrik=rubrik))
        stycken.extend(texter)
    return Avsnitt(id=avsnitt_id, rubrik=f'Analys av {tj.namn.lower()}', kalla='ai', stycken=tuple(stycken), underrubriker=tuple(rubriker))
```

Befintliga `bygg_tjanstavsnitt` ändras inte; den används bara för beskrivningsdelen.

- [x] **Step 4: Grinden, granskningen och utkastkedjan**

I `src/riskanalys/granskning/analys.py`:

```python
def mallfynd(resultat) -> list[dict]:
    """En del som skrivits av mallen är inget analysutkast; den ska skrivas om före fastställelse (spec 8.4.5)."""
    return [dict(typ="tackning", allvar="blockerande", grund="metodval", avsnitt=resultat.avsnitt,
                 beskrivning=f"{resultat.tjanst}: delen {d.del_id} kunde inte skrivas maskinellt och består av programmets mall.",
                 atgard="Komplettera underlaget eller skriv om delen och sakgranska den.")
            for d in resultat.delar if d.mall]


def _tjanstanalys_v3_stammer(regelbas, profil, tjanst, avsnitt, resultat) -> bool:
    from riskanalys.dokument.tjanstavsnitt import bygg_tjanstavsnitt_v3
    from riskanalys.fel import RiskanalysFel
    try:
        return avsnitt.kontrollsumma() == bygg_tjanstavsnitt_v3(regelbas, profil, tjanst, resultat, avsnitt.id).kontrollsumma()
    except RiskanalysFel:
        return False
```

Låt `analysfynd(regelbas, bedomning, profil, dokument, utkast=None)` ta emot ordboken från `godkanda_utkast`. För en tjänst vars utkast är ett `Tjanstresultat`: använd `_tjanstanalys_v3_stammer` i stället för `_tjanstanalys_stammer` och lägg till `mallfynd(resultat)`. B-09, B-10 och B-15 lämnas oförändrade, eftersom de låsta styckena finns kvar byte för byte i v3.

I `src/riskanalys/granskning/korning.py`, `godkanda_utkast`: för v3-körningar är värdet i ordboken ett `Tjanstresultat` (alla tjänster, även med mall-delar). `oppna_fragor` hämtar oklarheterna ur de godkända delarnas `AISvar.oklarheter` som `(avsnitt, Oklarhet(fraga=o.fraga, saknad_uppgift=o.uppgift_id))`. Skicka `utkast` vidare till `analysfynd`.

I `src/riskanalys/dokument/arb.py`: när `utkast[id]` är ett `Tjanstresultat`, bygg avsnittet med `bygg_tjanstavsnitt_v3(rb, profil, t, utkast[id], id)`.

I `src/riskanalys/intag/dokument.py`, `skapa_utkast`: låt kontrollen `if any(not p.godkant_utkast ...)` gälla bara `Skrivresultat` i det äldre formatet. I v3 skapas utkastet även när en del blivit mall; mallfyndet hindrar fastställelse.

- [x] **Step 5: Kör proven och hela sviten**

Run: `.venv/bin/pytest tester/intag/test_v3_grind.py tester/enhet/test_sakgranskning.py tester/regelkontrakt/test_arb_utvidgning.py tester/intag/test_kedja.py -v`
Expected: PASS.
Run: `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest -q`
Expected: allt grönt. Prov som skapar utkast i det nya formatet behöver testsvar per del: lägg till `bygg_delsvar(rb, profil, bedomning) -> list[AISvar]` i `tester/fixturer/m2.py` (fem `godkant_delsvar` per tjänst i ordningen från `tjanster_med_avsnitt`) och använd den där `bygg_testsvar` används med regelbaser som har `metod.omfattning`.

- [ ] **Step 6: Commit**

```bash
git add -A src/riskanalys tester
git commit -m "feat: tjänsteavsnitt av maskinellt validerade delar med ny granskningsgrind"
```

---

### Task 12: Likhetsfynd, livetest för cachen och dokumentation

**Files:**
- Create: `src/riskanalys/dokument/likhet.py`
- Modify: `src/riskanalys/granskning/analys.py` (likhetsfynd efter alla tjänster)
- Create: `tester/intag/test_cache_del_live.py`
- Modify: `docs/STATUS.md`, `README.md`
- Test: `tester/enhet/test_likhet.py` (ny)

**Interfaces:**
- Consumes: `Tjanstresultat` (10).
- Produces: `likhet(a: str, b: str) -> float` (Jaccard över ordtrigram), `likhetsfynd(resultat: list[Tjanstresultat], grans: float = 0.6) -> list[dict]`.

- [x] **Step 1: Skriv det fallerande provet**

```python
from riskanalys.dokument.likhet import likhet


def test_lika_texter_far_hog_likhet_och_olika_lag():
    text = "Kunden kan lämna fakturor från bolag utan verklig verksamhet för bokföring som vanliga kostnader."
    assert likhet(text, text) == 1.0
    assert likhet(text, "Lönehanteringen kan användas för att betala ut ersättning till personer som inte arbetar.") < 0.2
```

- [x] **Step 2: Kör provet och se det fallera**

Run: `.venv/bin/pytest tester/enhet/test_likhet.py -v`
Expected: FAIL (`likhet` saknas).

- [x] **Step 3: Implementera**

```python
"""Signal för text som inte är tjänstespecifik (tillsynsbrist B-04). Ett fynd, inte ett underkännande."""


def _trigram(text: str) -> set[tuple[str, ...]]:
    ord_ = text.lower().split()
    return {tuple(ord_[i:i + 3]) for i in range(max(len(ord_) - 2, 0))}


def likhet(a: str, b: str) -> float:
    x, y = _trigram(a), _trigram(b)
    return len(x & y) / len(x | y) if x | y else 0.0


def likhetsfynd(resultat: list, grans: float = 0.6) -> list[dict]:
    """Gränsen är ett metodval som prövas i piloten."""
    fynd = []
    for i, a in enumerate(resultat):
        for b in resultat[i + 1:]:
            for d in a.delar:
                sa, sb = d.godkant_svar, b.del_(d.del_id).godkant_svar
                if sa and sb and likhet(" ".join(s.text for s in sa.stycken), " ".join(s.text for s in sb.stycken)) >= grans:
                    fynd.append(dict(typ="tackning", allvar="hög", grund="metodval", avsnitt=a.avsnitt,
                                     beskrivning=f"Delen {d.del_id} är nästan likadan för {a.tjanst} och {b.tjanst}.",
                                     atgard="Skriv om delen så att den beskriver varje tjänsts egna förhållanden."))
    return fynd
```

Lägg till `likhetsfynd` på resultatet från `analysfynd` när alla tjänster är v3. Om `B-04` finns i `regelbas.bristmonster`, använd `typ="bristmonster", regel="B-04"` i stället för `typ="tackning"`.

- [ ] **Step 4: Livetest för cachen (körs bara med `-m live`)**

`tester/intag/test_cache_del_live.py` (i `tester/intag` där fixturerna `rb_intag` och `klar` finns):

```python
import os

import pytest

from riskanalys.dokument.claude import ClaudeLeverantor
from riskanalys.dokument.delskrivning import skriv_tjanst
from tester.fixturer.m2 import tjanst_for_prov

pytestmark = pytest.mark.live


@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="kräver riktig nyckel")
def test_andra_delanropet_traffar_cachen(tmp_path, rb_intag, klar):
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    res = skriv_tjanst(ClaudeLeverantor(modell="claude-sonnet-5-5", effort="high"), rb_intag, klar, t, avsnitt_id,
                       design="B", effort="high", personnamn=(), spara=lambda d, f: None)
    andra = res.delar[1].forsok[0].anrop.anvandning
    assert sum(p.cache_lasning_token for p in andra) > 0
```

Provsvitens isolering av nyckelfilen (`tester/conftest.py`) gör att testet hoppas över om nyckeln inte är satt i terminalen.

- [x] **Step 5: Dokumentation**

Lägg till ett avsnitt i `docs/STATUS.md` med datum, vad som byggts (del A och B), mätningen från uppgift 4 och att design, modell och effort är preliminära tills spec 8.4.8 är genomförd. Komplettera README:s avsnitt om skrivning: AI skriver analysdelarna, programmet skriver tal och nivåer, och en del som inte klarar kontrollerna blir mall med ett fynd som hindrar fastställelse.

- [x] **Step 6: Kör hela sviten**

Run: `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest -q && .venv/bin/riskanalys regelbas validera && git diff --check`
Expected: allt grönt.

- [ ] **Step 7: Commit**

```bash
git add src/riskanalys/dokument/likhet.py src/riskanalys/granskning/analys.py tester/enhet/test_likhet.py tester/intag/test_cache_del_live.py docs/STATUS.md README.md
git commit -m "feat: likhetsfynd mellan tjänster, livetest för cachen och dokumentation"
```

---

## Efter planen

1. **Pilot enligt spec 8.4.8 steg 1**, med användarens godkännande eftersom den kostar pengar: 2–3 syntetiska profiler med C0 och design B på Sonnet 5.5 `high`. Sammanfatta med `matning.sammanfatta`.
2. **Design A** som separat uppgift, om piloten visar att jämförelsen behövs.
3. **Uppföljningsplan för de byråövergripande avsnitten** D-ARB.2, 4, 5, 7 och 9: ny tillåtelselista med källor, delmoduler och grind.
4. **Egen plan för kryssfrågorna** (spec 14.5).


## Genomförande 2026-10-11

Del A och B är implementerade i befintlig feature-branch `codex/m0-m1`. Tester skrevs och kördes fallerande före respektive beteendeändring. Ingen commit eller push görs utan användarens uttryckliga begäran.

| Uppgift | Leverans |
|---|---|
| 1 | Svenska tusentalsavskiljare och decimalkomma normaliseras i äldre talkontroll. |
| 2 | Slutet AI-schema med tillåtna ID-listor och skiftlägesnormalisering. |
| 3 | Programmet skriver motorns nivåmeningar, AI motiverar utan egna nivåbeslut. |
| 4 | Sammanfattning av alla försök, felklasser och token; uttryckliga priser inklusive cache. |
| 5 | Stabilt faktablad ur skyddat underlag, sluten källtyp och smågruppsskydd. |
| 6 | Tal- och rollplatshållare valideras; trasiga eller olösta uttryck stoppar sammanställningen. |
| 7 | Fast systemprompt och fem delmoduler. |
| 8 | Validering per del: hot, terrorfinansiering, sårbarhetskategorier, kontroller, motivering, slutsatser och oklarheter. |
| 9 | Delanrop i test-/Claudeleverantör, strömning över gränsen, cacheförbrukning och stoppskäl. |
| 10 | Design B med kedjat underlag, begränsade omförsök och direkt sparade försök. |
| 11 | V3-dokument, råsvar omtolkas och omvalideras, fryst faktablad kontrolleras, reservmall blockerar fastställelse; CLI, granskning och export anpassade. |
| 12 | Likhetsfynd i granskningen samt separat spärrat livetest för cache. |

### Konkretiseringar av planens kodexempel

- Planens råa låsta stycken kan innehålla personnamn, lokal fritext, källtexter och exakta smågruppstal. De stannar lokalt för validering och dokumentbygge; AI får säkra kodskrivna sammanfattningar. Detta följer AGENTS.md:s integritetsgräns och ändrar inget belägg i dokumentet.
- Faktabladets numeriska värde hämtas från redan skyddad visning, aldrig tillbaka från råprofilen. Maskerad eller okänd visning ger ingen talplatshållare.
- V3-grinden litar inte på en sparad tom fellista: råsvar och sparat svar måste stämma, delarna omvalideras och faktabladet jämförs med profil/bedömning. Planexemplet om att ett gammalt svar kan användas med ny profil har ersatts med ett prov som kräver ny skrivning.
- Metadata om sårbarhetskategori, terrorhot, motorns nivåer och sektorsreferens finns i faktabladet. Koden återger sektorsreferensen på dess egen skala; AI ska inte likställa skalorna.
- Alla siffror i ny AI-prosa kräver talplatshållare. Planexemplets undantag för godtyckliga årtal och paragrafnummer togs bort eftersom det annars kan släppa igenom uppdiktade uppgifter. Juridiska källhänvisningar skrivs av programmet.
- Tal ersätts vid sammanställning, före sakgranskning, enligt planens redan dokumenterade avvikelse. Gamla format kan fortfarande läsas; nya körningar med den nuvarande regelbasen ger v3.

### Verifiering och återstående utvärdering

Slutlig fullsvit är grön: **1 183 tester passerar, två livetester bortvalda, 656,80 s**, med `ANTHROPIC_API_KEY` och `RISKANALYS_SCB_API_KEY` borttagna ur körmiljön. En oberoende kodgranskare hittade generiska AI-nivåpåståenden, inklusive pluralformer, och felaktig underkänning av negation om riskminskning. Fynden fick fallerande regressionstester, rättades och återkontrollerades utan kvarstående anmärkningar. Även manifestets format/design och B-04-kopplingen återkontrollerades. Regelbasvalideringen och `git diff --check` är gröna, med oförändrad kontrollsumma och sakkunnigstatus `ej_granskad`.

Livetestet är byggt i `tester/live/test_delcache.py`, men livetestet och piloten har **inte körts**: de kräver ett uttryckligt beslut om riktiga API-anrop och kostnad. Dessa provsteg och alla commitsteg lämnas därför okryssade. Ingen faktisk före-/eftermätning eller sakkunnig bedömning har tillkommit. Design A, parallella delanrop, byråövergripande skrivning och 14.5:s källbaserade kryssalternativ kvarstår som avgränsat efterarbete; de ingår inte i detta bygge.

### Rättelser efter Claudes granskning, 2026-10-12

Fem fynd rättades efter fallerande regressioner: permanenta API-fel och slut på testsvar avbryter skrivningen; en explicit klassning tillåter omförsök för 429, 5xx och nätverksfel. Perioder har den kodersatta platshållaren `{period:ID}`; även ”under statistikperioden” godtas. Kombinationskontrollen skiljer två S-referenser från två gällande/okända sårbarheter och kontrollerar samverkansord. Sårbarhetsmodulen förklarar alla fem kategorikoderna. Bara tjänstresultatets faktabladskopia sparas; grinden bygger fortfarande aktuellt underlag för jämförelse.

Regressionerna omfattar leverantörsgränsen med syntetiska HTTP-fel, begränsade omförsök, uttömda testsvar, periodens referens och ersättning före sakgranskning, negativa/okända sårbarheter, kategorierna i anropsmodulen samt sparande och återläsning med giltigt manifest. Slutlig fullsvit: **1 213 passerar, två livetester bortvalda, 653,71 s**, med båda API-nycklarna borttagna ur körmiljön. Regelbasvalidering och `git diff --check` är gröna. Inga riktiga API-anrop, commits eller pushar har gjorts.

### Pilotens token- och maskningsrättelser, 2026-10-12

Efter användarens rapport om åtta pilotanrop och fyra svar klippta vid 16 000 token höjdes delanropen till 64 000 token med befintlig strömning. Ett `max_tokens`-avbrott bland delens tidigare försök hindrar effort-höjning i sista omförsöket. Avbrottsmeddelandet använder delanropets faktiska gräns. Endast status `okänd` kräver verifieringsmarkering och oklarhet; status `skyddad` är maskerat bekräftat underlag och dess exakta tal lämnas fortsatt utanför talplatshållarna.

CLI-valet `--effort` fanns redan för Claude. Det är nu validerat och överförs uttryckligen till hela v3-körningen, inklusive testleverantören, samt sparas i manifestet. Det gör jämförelse av `medium` och `high` möjlig på samma frysta bedömning. Tio token-/maskningsregressioner och tre CLI-regressioner fallerade före rättningarna; 87 riktade prov passerar. Slutlig fullsvit: **1 226 passerar, två livetester bortvalda, 655,29 s**, med båda API-nycklarna borttagna ur körmiljön. Regelbasvalidering och `git diff --check` är gröna. `LANGD`, regelbasen och sakkunnigstatus är oförändrade. Codex har inte kört någon ny betald pilot, gjort riktiga API-anrop, committat eller pushat.

---

## Del C – Kalibrering efter piloten 2026-10-12

Pilot på en tjänst (löpande bokföring, syntetisk byrå, Sonnet 5.5): effort `medium` 419 s och 0,67 USD, effort `high` 1 081 s och 1,63 USD. Båda gav 4 av 5 delar godkända efter omförsök, 0 av 5 direkt. Alla första försök underkändes för längd (430–900 ord mot gränser på 400–450), eftersom prompten inte angav gränsen. Sårbarhetsdelen blev mall i båda körningarna, eftersom kombinationsregeln slog till på stycken som nämnde två tillämpliga sårbarheter utan att påstå ett samband. AI-texten i godkända delar höll god kvalitet. Effort och modell beslutas av projektägaren (spec 8.4.8).

### Task 13: Längdintervall i delmodulerna

**Files:**
- Modify: `src/riskanalys/dokument/promptar/delar.py` (ny funktion `modultext`)
- Modify: `src/riskanalys/dokument/promptar/__init__.py` (`delmodul`, `promptsumma` använder `modultext`)
- Modify: `src/riskanalys/dokument/promptar/meddelande.py:18` (uppgiftsblocket använder `modultext`)
- Test: `tester/enhet/test_promptar.py`

**Interfaces:**
- Consumes: `LANGD` i `dokument/delvalidering.py`.
- Produces: `promptar.delar.modultext(del_id: str) -> str` = modulen plus raden "Skriv {lägst}–{högst} ord i delen. Längre text underkänns och måste skrivas om." `delmodul` och `promptsumma` använder samma text, så kontrollsumman ändras när gränsen ändras.

- [ ] **Step 1: Skriv de fallerande proven**

```python
from riskanalys.dokument.delvalidering import LANGD


def test_varje_delmodul_anger_sitt_langdintervall():
    for d in DELAR:
        lagst, hogst = LANGD[d]
        assert f"{lagst}–{hogst} ord" in delmodul(d)


def test_uppgiftsblocket_innehaller_langdintervallet(faktablad_exempel):
    block = bygg_innehall(faktablad_exempel, "hot", (), (), ())
    lagst, hogst = LANGD["hot"]
    assert f"{lagst}–{hogst} ord" in next(b["text"] for b in block if b["text"].startswith('<uppgift del="hot">'))
```

- [ ] **Step 2: Kör och se dem fallera**

Run: `.venv/bin/pytest tester/enhet/test_promptar.py -v`
Expected: FAIL (ingen längdrad i modulerna).

- [ ] **Step 3: Implementera**

I `promptar/delar.py`:

```python
def modultext(del_id: str) -> str:
    """Modulen med delens längdintervall. Gränsen kommer från valideringen så att de inte glider isär."""
    from riskanalys.dokument.delvalidering import LANGD
    lagst, hogst = LANGD[del_id]
    return f"{MODULER[del_id]}\nSkriv {lagst}–{hogst} ord i delen. Längre text underkänns och måste skrivas om."
```

I `promptar/__init__.py`: `delmodul(del_id)` returnerar `modultext(del_id)`, och `promptsumma` använder `modultext(del_id)` i stället för `MODULER[del_id]`. I `promptar/meddelande.py:18`: använd `modultext(del_id)` i uppgiftsblocket.

- [ ] **Step 4: Kör proven och hela promptsviten**

Run: `.venv/bin/pytest tester/enhet/test_promptar.py tester/intag/test_delskrivning.py -v`
Expected: PASS.

### Task 14: Kombinationsregeln kräver ett påstått samband

**Files:**
- Modify: `src/riskanalys/dokument/delvalidering.py:73-77`
- Modify: `src/riskanalys/dokument/promptar/delar.py` (modulen `sarbarheter`)
- Test: `tester/enhet/test_delvalidering.py`

**Interfaces:**
- Consumes: `_SAMVERKAN` och `Faktablad.sarbarheter` (med `galler`).
- Produces: ett analysstycke underkänns som kombination bara när texten innehåller samverkansord **och** stycket refererar minst två sårbarheter som gäller eller är okända.

- [ ] **Step 1: Skriv de fallerande proven**

```python
from riskanalys.dokument.modeller import UnderlagSarbarhet


def _fb_med_sarbarheter(fb):
    return fb.model_copy(update={
        "sarbarheter": (UnderlagSarbarhet(id="S-KUND-01", namn="Riskbransch", galler="ja"),
                        UnderlagSarbarhet(id="S-KUND-02", namn="Kontanter", galler="ja")),
        "sarbarhetsomraden": {"S-KUND-01": "kund", "S-KUND-02": "kund"}})


def _kombinationsfel(fb, text, typ="analys"):
    svar = _svar((typ, ["T-RED-01", "S-KUND-01", "S-KUND-02"], text + FYLLNAD))
    return [f for f in validera_del("sarbarheter", svar, fb, (), ()) if "kombination" in f]


def test_tva_tillampliga_sarbarheter_utan_sambandsord_godtas(faktablad_exempel):
    assert _kombinationsfel(_fb_med_sarbarheter(faktablad_exempel), "Både riskbranscher och kontanthantering förekommer bland kunderna.") == []


def test_pastatt_samband_utan_overlapp_maste_vara_scenario(faktablad_exempel):
    fb = _fb_med_sarbarheter(faktablad_exempel)
    assert _kombinationsfel(fb, "Riskbranscher och kontanthantering samverkar och ökar risken.")
    assert _kombinationsfel(fb, "Riskbranscher och kontanthantering samverkar och ökar risken.", typ="scenario") == []


def test_sambandsord_med_en_sarbarhet_godtas(faktablad_exempel):
    fb = _fb_med_sarbarheter(faktablad_exempel)
    svar = _svar(("analys", ["T-RED-01", "S-KUND-01"], "Riskbranscher förekommer tillsammans med många små kunder." + FYLLNAD))
    assert not [f for f in validera_del("sarbarheter", svar, fb, (), ()) if "kombination" in f]
```

- [ ] **Step 2: Kör och se dem fallera**

Run: `.venv/bin/pytest tester/enhet/test_delvalidering.py -k "sarbarhet or samband" -v`
Expected: FAIL (två tillämpliga sårbarheter utan sambandsord underkänns i dag, och sambandsord med en sårbarhet underkänns också).

- [ ] **Step 3: Implementera**

I `delvalidering.py`, ersätt villkoret i kombinationsregeln:

```python
                if s.typ == "analys" and _SAMVERKAN.search(s.text) and
                    len({r.id for r in fb.sarbarheter if r.id in s.referenser and r.galler != "nej"}) >= 2]
```

Lägg till sist i modulen `sarbarheter` i `promptar/delar.py`:

```python
        "\nBehandla gärna varje sårbarhet i ett eget stycke. Ord som samverkar, tillsammans, kombination eller "
        "förstärker betyder att du påstår ett samband; använd då stycketypen scenario om faktabladet inte visar "
        "att samma kunder berörs."
```

- [ ] **Step 4: Kör proven och hela sviten**

Run: `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest -q`
Expected: allt grönt.
