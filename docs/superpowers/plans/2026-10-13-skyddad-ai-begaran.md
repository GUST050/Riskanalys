# Skyddad AI-begäran och kvarvarande klartext – implementeringsplan

> **För agentiska utförare:** OBLIGATORISK DELFÄRDIGHET: använd superpowers:subagent-driven-development (rekommenderas) eller superpowers:executing-plans för att genomföra planen uppgift för uppgift. Stegen använder kryssrutor (`- [ ]`).

**Mål:** Den utgående AI-begäran ska vara identisk för byråer som bara skiljer sig i värden som omfattas av smågruppsskyddet. Planen rättar också visningen av mycket små och mycket stora andelar, flyttar katalogkoder och kontrollsummor ur löptexten och lägger till en uttrycklig formatspärr före fastställelse.

**Arkitektur:**
- **Faktabladet och delanropen tappar alla motorspår.** Motorns nivåer, regelspår och nivåmeningar skickas aldrig till AI. Nivåmeningarna skrivs fortfarande lokalt av koden.
- **Skyddat utfall.** En sårbarhet vars villkor läser ett smågruppsvärde som AI inte får se exakt får utfallet `skyddat` i faktabladet. Beslutet fattas ur den synliga vyn, inte ur råvärdet.
- **Ett prov på identitet.** Ett prov bygger hela begäran (systemprompt, innehåll och schema för alla fem delar) för par av profiler och kräver att paren är identiska.
- **Övrigt:** en gemensam visningsfunktion för andelar, en hjälpfunktion som ersätter katalogkoder med titlar och namn, och en ren funktion för formatspärren.

**Teknik:** Python 3.12, Pydantic, pytest.

**Spec:** `docs/superpowers/specs/2026-10-08-riskanalys-design.md`, främst 8.4.1, 8.4.4, 8.4.9 och den nya 8.4.10 som uppgift 1 skriver.

## Bakgrund

Granskningen 2026-10-13 visade att smågruppsskyddet läcker. Med 0 respektive 3 kunder med transaktioner utanför Sverige visar faktabladet samma maskerade värde, ”färre än 5”. Ändå skiljer sig AI-begäran på 96 rader, kontrollerat med syntetiska data:
- **Risknivåer:** inneboende risk måttlig blir hög, terrorfinansiering måttlig blir hög.
- **Regelspår:** BT-MATRIS-05 blir BT-MATRIS-08, och BT-MATRIS-03 blir BT-MATRIS-06.
- **Sårbarhetens utfall:** nej blir ja.
- **Nivåmeningarna** bland de låsta instruktionerna till delen risknivåer.
- **Svarsschemat,** som räknar upp regelspåren som tillåtna ID.

Användaren valde 2026-10-13 att AI aldrig ska få nivåer, regelspår eller nivåmeningar, och att utfallet för sårbarheter som bygger på skyddade värden ska stå som skyddat.

Granskningen bekräftade också att en andel som 8 av 2 000 kunder blir `0 %` i faktabladet, och att `{tal:…}` då ersätts med `0 %` medan gränsmeningen säger ”mindre än 1 %”. Den rekommenderade dessutom:
- att katalogkoder och kontrollsummor flyttas från löptexten till referenser och bilaga B1
- en uttrycklig formatkontroll före fastställelse, där äldre paket fortfarande kan läsas
- en första pilot efter rättningarna, på en tjänst med `medium`

## Global Constraints

- AGENTS.md regel 1: ”AI fattar inga beslut.” Motorns lokala bedömning, nivåer, regelspår och utfall ändras inte. Bara det som skickas till AI ändras.
- AGENTS.md regel 2: ”Inga personuppgifter till AI.” Smågruppsskyddet (`SMA_GRUPPER_GRANS = 5`) och tillåtelselistan gäller oförändrat.
- AGENTS.md regel 4: regelbasen ändras inte i denna plan.
- AGENTS.md regel 6: ”Tester före commit … Skriv testet först.” Regel 7: inga anrop mot riktiga API:t i automatiska tester.
- Stil: ”Användartexter och dokumentation på svenska. Identifierare i koden på svenska utan å, ä och ö.” ”Funktioner returnerar nya objekt i stället för att ändra befintliga.”
- Den frysta M1-kedjan ska ge byte för byte samma dokument. Det gyllene provet `tester/enhet/test_gyllene_m1.py` och `tester/typfall/` ska passera utan ändringar.
- `tester/enhet/test_faststall.py` och `tester/enhet/test_manifest.py` ska passera utan ändringar. Fastställda paket byggs aldrig om.
- `visa_varde` i `profil/hantering.py` ändras inte, eftersom den frysta kedjan använder den.
- Dokumentformatet förblir `D-ARB-tjanst-v4`. De låsta styckena i tjänsteavsnittet ändras inte av skyddsrättningen.

## Review Focus

1. **Ett smågruppsvärde utanför tillåtelselistan** (till exempel `P-GEO.andel_agare_utanfor_ees` i S-ARB-04) visas aldrig för AI, men påverkar utfallet. Sårbarheten ska maskeras. Testas i uppgift 3.
2. **Litet komplement** (98 av 100) maskeras som ”undertryckt” och får samma begäran som 99 av 100. Testas i uppgift 3.
3. **”okänt” för ett smågruppsfält med bekräftat råvärde** (saknad bas) ska maskeras, eftersom motorn ändå läser råvärdet. Testas i uppgift 3.
4. **Andel nära 100 %** (999 av 1 000) visas som ”mer än 99 %” lokalt, inte ”100 %”. Testas i uppgift 4.
5. **Regelpaketets namn innehåller koden** (”…: RP-RED-VG”) och måste visas utan den i D-ARB.1. Testas i uppgift 5.

Medvetet utanför planen: 18 sårbarheter (S-ARB-01 till S-ARB-18) har villkor på uppgifter utanför tillåtelselistan utan smågruppsskydd, främst `P-RISK`-uppgifterna. Deras utfall skickas som i dag. Om det ska ändras är ett separat beslut för användaren, och STATUS anger det.

## Filer

| Fil | Ansvar | Uppgift |
|---|---|---|
| `docs/superpowers/specs/2026-10-08-riskanalys-design.md` | Revision 19 | 1 |
| `src/riskanalys/dokument/faktablad.py`, `dokument/delskrivning.py`, `dokument/promptar/delar.py` | Inga nivåer eller regelspår till AI | 2 |
| `src/riskanalys/dokument/modeller.py`, `dokument/underlag.py`, `dokument/faktablad.py`, `dokument/promptar/delar.py` | Skyddat utfall | 3 |
| `src/riskanalys/profil/hantering.py`, `dokument/underlag.py`, `dokument/faktablad.py`, `dokument/klartext.py` | Visning av små och stora andelar | 4 |
| `src/riskanalys/dokument/klartext.py`, `dokument/arb.py`, `dokument/uppfoljning.py` | Katalogkoder ur löptexten | 5 |
| `src/riskanalys/faststallelse/faststall.py` | Formatspärr | 6 |
| `docs/STATUS.md` | Status | 7 |

---

### Före uppgift 1: Spara start-SHA

- [ ] Skriv `START=bc6e45ed65c3a14a8b5db252f98121aa977090ff` på raden `START=` under ”Genomförandelogg” sist i denna plan. Uppgift 1 committar planen med raden, och uppgift 7 jämför mot detta SHA.

---

### Uppgift 1: Spec revision 19

**Files:**
- Modify: `docs/superpowers/specs/2026-10-08-riskanalys-design.md`
- Modify: `docs/superpowers/plans/2026-10-13-skyddad-ai-begaran.md` (bara raden `START=`)

**Interfaces:** inga.

- [ ] **Steg 1: Statusraden.** Ersätt `revision 18 (2026-10-12)` med `revision 19 (2026-10-13)` på rad 3.

- [ ] **Steg 2: Tabellen i 8.4.4.** I raden som börjar `| Risknivåer och motivering |`, ersätt `Nivån som en kedja av hot, sårbarhet, omfattning och konsekvens; förklara avvikelse från NRA:s sektorsnivå` med `Riskbilden som en kedja av hot, sårbarhet, omfattning och konsekvens, utan att AI ser motorns nivåer; förklara skillnader mot NRA:s sektorsnivå`. I raden som börjar `| Slutsatser |`, ersätt `Vad nivån betyder för kundkännedom, övervakning och utbildning i just denna tjänst` med `Vad riskbilden betyder för kundkännedom, övervakning och utbildning i just denna tjänst`.

- [ ] **Steg 3: Tre punkter sist i 8.4.9**, efter punkt 6:

```markdown
7. En andel över noll som avrundas till 0 % skrivs ”mindre än 1 %”, och en andel under 100 % som avrundas till 100 % skrivs ”mer än 99 %”. Det gäller på samma sätt i låsta stycken, faktablad och platshållare.
8. Katalogkoder och kontrollsummor (regelpaket, källor) står bara i referenser och i bilagan `D-ARB.B1`. Löptexten använder titlar och namn.
9. Ny fastställelse kräver att granskningens dokument har aktuellt format. Äldre fastställda paket kan fortfarande läsas.
```

- [ ] **Steg 4: Nytt avsnitt 8.4.10**, direkt efter 8.4.9 och före `## 9 Granskning (maskinell)`:

```markdown
#### 8.4.10 Skyddad AI-begäran

1. Hela den utgående begäran till AI – systemprompt, varje dels innehåll och svarsschema – ska vara identisk för två profiler som bara skiljer sig i värden som omfattas av smågruppsskyddet: värden som AI ser maskerade (”färre än 5”, ”undertryckt”) eller som okända, och smågruppsfält utanför tillåtelselistan.
2. AI får därför aldrig motorns risknivåer, regelspår eller de kodskrivna nivåmeningarna. Nivåmeningarna skrivs som tidigare lokalt i dokumentet. AI motiverar riskbilden utifrån hot, sårbarheter och faktauppgifter utan att ange nivåer.
3. En sårbarhet vars villkor läser ett sådant värde får utfallet ”skyddat” i faktabladet, med beskedet att den prövas lokalt. Beslutet fattas ur det AI får se, inte ur råvärdet. Motorns lokala bedömning ändras inte.
4. Ett prov visar att begäran är identisk för 0 och 3 kunder, för ett litet komplement och för ett smågruppsfält utanför tillåtelselistan.
5. Utfall för sårbarheter som bara bygger på uppgifter utan smågruppsskydd skickas som tidigare.
```

- [ ] **Steg 5: Rad 19 i revisionsloggen**, direkt efter rad 18:

```markdown
| 19 | 2026-10-13 | Efter granskning med syntetiska data: AI-begäran blir identisk för profiler som bara skiljer sig i smågruppsskyddade värden – inga nivåer, regelspår eller nivåmeningar till AI och utfallet ”skyddat” för berörda sårbarheter (8.4.10). Andelar nära 0 och 100 % visas konsekvent, katalogkoder och kontrollsummor flyttas till referenser och bilaga B1, och fastställelse kräver aktuellt dokumentformat (8.4.9). Inga ändrade regler, gränser eller nivåer. |
```

- [ ] **Steg 6: Commit**

```bash
git add docs/superpowers/specs/2026-10-08-riskanalys-design.md docs/superpowers/plans/2026-10-13-skyddad-ai-begaran.md
git commit -m "docs: spec revision 19, skyddad AI-begäran"
```

---

### Uppgift 2: Inga nivåer, regelspår eller nivåmeningar till AI

**Files:**
- Modify: `src/riskanalys/dokument/faktablad.py` (`bygg_faktablad`)
- Modify: `src/riskanalys/dokument/delskrivning.py` (`skyddade_lasta_texter`)
- Modify: `src/riskanalys/dokument/promptar/delar.py` (modulerna `risknivaer` och `slutsatser`)
- Test: `tester/intag/test_skyddad_begaran.py` (ny), `tester/intag/test_v3_grind.py:88-95`, `tester/enhet/test_promptar.py`

**Interfaces:**
- Produces: `Faktablad.nivaer == {}` och `Faktablad.regelspar == ()` för alla nya faktablad. Fälten finns kvar, så äldre sparade resultat kan läsas. `tillatna_id()` innehåller därmed inga regelspår.
- Produces: testhjälpen `begaran(rb, profil) -> list[dict]` i `tester/intag/test_skyddad_begaran.py`, som returnerar `Delanrop.model_dump()` för alla fem delar. Uppgift 3 använder den.

- [ ] **Steg 1: Skriv de fallerande testerna**

`tester/intag/test_skyddad_begaran.py`:

```python
import json
import tempfile
from pathlib import Path

from riskanalys.dokument.delskrivning import skriv_tjanst
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.promptar import DELAR

from tester.fixturer.m2 import godkant_delsvar, tjanst_for_prov


def begaran(rb, profil):
    """Hela den utgående AI-begäran för första tjänsten: systemprompt, innehåll och schema per del."""
    with tempfile.TemporaryDirectory() as mapp:
        avsnitt_id, t = tjanst_for_prov(Path(mapp), rb, profil)
        lev = Testleverantor([godkant_delsvar(d, t) for d in DELAR])
        skriv_tjanst(lev, rb, profil, t, avsnitt_id, effort="medium", personnamn=(), spara=lambda d, f: None)
        return [a.model_dump(mode="json") for a in lev.delanrop]


def test_ai_far_inga_nivaer_eller_regelspar(rb_intag, klar):
    text = json.dumps(begaran(rb_intag, klar), ensure_ascii=False)
    assert "BT-" not in text
    for ord_ in ("inneboende_risk", "kvarstaende_risk", "Sannolikheten bedöms som", "Den kvarstående risken är"):
        assert ord_ not in text
```

I `tester/intag/test_v3_grind.py`, ersätt testet `test_nivaer_och_sektorskala_ar_kodskrivna_och_tillgangliga_for_ai` med:

```python
def test_nivaer_ar_kodskrivna_men_inte_tillgangliga_for_ai(v3):
    rb,p,t,res,id=v3
    ref=rb.sektorsreferenser[rb.tjanster[t.tjanst].sektorreferens]
    assert res.faktablad.nivaer=={} and res.faktablad.regelspar==()
    assert res.faktablad.sektorsreferens.skala==ref.skala
    a=bygg_tjanstavsnitt_v3(rb,p,t,res,id)
    start,slut=[u.fore_stycke for u in a.underrubriker[4:]]
    assert any(t.inneboende.risk in s.text and s.text.startswith("Sannolikheten bedöms som") for s in a.stycken[start:slut])
    assert any('Källans skala är separat' in s.text and ref.kalla in s.referenser for s in a.stycken[start:slut])
```

I `tester/enhet/test_promptar.py`, lägg till:

```python
def test_risknivamodulen_sager_att_ai_inte_ser_nivaerna():
    assert "du ser inte motorns nivåer" in delmodul("risknivaer")
    assert "motorns nivå" not in delmodul("slutsatser")
```

- [ ] **Steg 2: Kör testerna och se dem fallera**

Kör: `.venv/bin/pytest tester/intag/test_skyddad_begaran.py tester/intag/test_v3_grind.py tester/enhet/test_promptar.py -q`
Förväntat: FAIL. Begäran innehåller "BT-" och nivåer, och modulen saknar meningen.

- [ ] **Steg 3: Implementera**

I `faktablad.py`, `bygg_faktablad`: ersätt `nivaer=underlag.nivaer` med `nivaer={}` och `regelspar=underlag.regelspar` med `regelspar=()`. Lägg en kommentar på raden ovanför: `# Motorns nivåer och regelspår skickas aldrig till AI (spec 8.4.10).`

I `delskrivning.py`, `skyddade_lasta_texter`: ersätt grenen för `risknivaer` med:

```python
    if del_id == "risknivaer":
        return ("Programmet skriver nivåmeningarna och sektorsreferensen lokalt. Du ser inte motorns nivåer och anger inga nivåer.",)
```

I `promptar/delar.py`, ersätt modulen `risknivaer` med:

```python
    "risknivaer": (
        "Skriv motiveringen under Risknivåer och motivering. Programmet skriver nivåmeningarna och sektorsreferensen "
        "på källans egen skala lokalt; du ser inte motorns nivåer och anger inga nivåer själv. Förklara riskbilden som en "
        "kedja: vilka hot som kan utnyttja vilka sårbarheter, hur tjänstens omfattning påverkar sannolikheten och vilken "
        "konsekvensen blir. Pröva tjänstens egna förhållanden mot sektorsreferensen i faktabladet, utan att likställa skalorna; "
        "motivera skillnader med det belagda underlaget, eftersom föreskrifterna kräver att risknivåerna motiveras. "
        "Sårbarheter med utfallet skyddat prövas lokalt; skriv inte om de gäller.\n"
        "Använd de maskinellt validerade delarna som underlag och upprepa dem inte. Minst ett stycke ska ha typen "
        "motivering och hänvisa till minst ett hot och en sårbarhet eller uppgift."
    ),
```

och i modulen `slutsatser` ersätt `Förklara vad motorns nivå betyder för just den här tjänsten:` med `Förklara vad riskbilden betyder för just den här tjänsten:` och `slutsatser som bara upprepar nivån` med `slutsatser som bara upprepar riskbilden`.

Sök efter andra prov som kräver nivåer eller regelspår i faktabladet eller begäran (`grep -rn "nivaer\|regelspar" tester/intag tester/enhet`). Uppdatera dem till den nya regeln och lista dem i rapporten. Lokala prov för nivåmeningarna i dokumentet (till exempel `tester/intag/test_nivatext.py`) ska inte ändras.

- [ ] **Steg 4: Kör testerna**

Kör: `.venv/bin/pytest tester/intag tester/enhet/test_promptar.py tester/enhet/test_delvalidering.py -q`
Förväntat: PASS.

- [ ] **Steg 5: Commit**

```bash
git add src/riskanalys/dokument/faktablad.py src/riskanalys/dokument/delskrivning.py src/riskanalys/dokument/promptar/delar.py tester/intag/test_skyddad_begaran.py tester/intag/test_v3_grind.py tester/enhet/test_promptar.py
git commit -m "fix: AI får inga nivåer, regelspår eller nivåmeningar"
```

---

### Uppgift 3: Skyddat utfall och identisk begäran

**Files:**
- Modify: `src/riskanalys/dokument/modeller.py` (`UnderlagSarbarhet.galler`)
- Modify: `src/riskanalys/dokument/underlag.py` (ny `skyddat_villkor`, konstanten `SKYDDAT_UTFALL`)
- Modify: `src/riskanalys/dokument/faktablad.py` (`bygg_faktablad`)
- Modify: `src/riskanalys/dokument/promptar/delar.py` (modulen `sarbarheter`)
- Test: `tester/intag/test_skyddad_begaran.py`, `tester/enhet/test_promptar.py`

**Interfaces:**
- Consumes: `begaran(rb, profil)` från uppgift 2. `SKYDDADE_VISNINGAR` och `_uppgift` i `underlag.py`.
- Produces: `UnderlagSarbarhet.galler: Literal["ja", "nej", "okänt", "skyddat"]`. `underlag.skyddat_villkor(regelbas, profil, sarbarhet_id, tillatna) -> bool`.

- [ ] **Steg 1: Skriv de fallerande testerna**

Lägg till i `tester/intag/test_skyddad_begaran.py`:

```python
import pytest

from riskanalys.profil.omfattning import harled_andelar


def _med_antal(rb, profil, falt_id, antal):
    u = profil.uppgifter[falt_id].model_copy(update={"varde": antal})
    ny = profil.model_copy(update={"uppgifter": {**profil.uppgifter, falt_id: u}})
    return harled_andelar(ny, rb, frozenset({falt_id}))


@pytest.mark.parametrize("falt_id,a,b", [
    ("P-GEO.antal_utland_transaktion", 0, 3),      # liten grupp, "färre än 5"
    ("P-KUND.antal_riskbransch", 97, 99),          # litet komplement, "undertryckt"
    ("P-GEO.antal_agare_utanfor_ees", 0, 3),       # smågruppsfält utanför tillåtelselistan
])
def test_begaran_ar_identisk_nar_bara_skyddade_varden_skiljer(rb_intag, klar, falt_id, a, b):
    assert begaran(rb_intag, _med_antal(rb_intag, klar, falt_id, a)) == begaran(rb_intag, _med_antal(rb_intag, klar, falt_id, b))


def test_skyddat_utfall_i_faktabladet(rb_intag, klar):
    text = json.dumps(begaran(rb_intag, _med_antal(rb_intag, klar, "P-GEO.antal_utland_transaktion", 3)), ensure_ascii=False)
    assert '"galler": "skyddat"' in text and "prövas lokalt" in text
```

Kontrollera först namnet på antalsfälten (`antalfalt` för `P-GEO.andel_utland_transaktion`, `P-KUND.andel_riskbransch` och `P-GEO.andel_agare_utanfor_ees` i `regelbas/falt.yaml`) och använd de verkliga ID:na. Testprofilen har 100 aktiva kunder.

Lägg till i `tester/enhet/test_promptar.py`:

```python
def test_sarbarhetsmodulen_beskriver_skyddat_utfall():
    assert "utfall är skyddat" in delmodul("sarbarheter")
```

- [ ] **Steg 2: Kör testerna och se dem fallera**

Kör: `.venv/bin/pytest tester/intag/test_skyddad_begaran.py tester/enhet/test_promptar.py -q`
Förväntat: FAIL för identiteten (utfall och motivering skiljer) och för det skyddade utfallet.

- [ ] **Steg 3: Implementera**

`modeller.py`, `UnderlagSarbarhet`: `galler: Literal["ja", "nej", "okänt", "skyddat"]`.

`underlag.py`, lägg till efter `SKYDDADE_VISNINGAR`:

```python
SKYDDAT_UTFALL = ("Utfallet redovisas inte eftersom underlaget omfattas av skyddet för små grupper; "
                  "sårbarheten prövas lokalt.")


def skyddat_villkor(regelbas: Regelbas, profil: Profil, sarbarhet_id: str, tillatna: tuple[str, ...]) -> bool:
    """Sant när villkoret läser ett smågruppsfält som AI inte ser exakt. Avgörs ur den synliga vyn (spec 8.4.10)."""
    from riskanalys.regelverk.villkor import falt_i
    villkor = tolka_villkor(regelbas.sarbarheter[sarbarhet_id].villkor, regelbas.faltdefinitioner())
    for falt_id in falt_i(villkor):
        if not regelbas.falt[falt_id].smagrupp:
            continue
        if falt_id not in tillatna:
            return True
        visning = _uppgift(regelbas, profil, falt_id).varde
        if visning.startswith(SKYDDADE_VISNINGAR) or visning == "okänt":
            return True
    return False
```

`faktablad.py`, `bygg_faktablad`: hämta `tillatna = regelbas.tillatelselistor[AVSNITTSTYP].falt` (importera `AVSNITTSTYP`, `SKYDDAT_UTFALL` och `skyddat_villkor` från `riskanalys.dokument.underlag`) och bygg sårbarheterna som

```python
        sarbarheter=tuple(
            s.model_copy(update={"galler": "skyddat", "motivering": SKYDDAT_UTFALL})
            if skyddat_villkor(regelbas, profil, s.id, tillatna) else s
            for s in underlag.sarbarheter),
```

`promptar/delar.py`, modulen `sarbarheter`: lägg till följande rad direkt före raden `"Programmet har redan skrivit underlagsstycket för geografin. Bygg vidare på det."`:

```python
        "Om en sårbarhets utfall är skyddat skriver du att den prövas lokalt, utan att säga om den gäller.\n"
```

Kontrollera att inget valideringsprov eller granskningsprov förutsätter att `galler` bara kan vara ja, nej eller okänt (`grep -rn "galler" src/riskanalys`). Den lokala bedömningen och dokumentets låsta stycken använder motorns utfall och ska inte ändras.

- [ ] **Steg 4: Kör testerna**

Kör: `.venv/bin/pytest tester/intag tester/enhet -q`
Förväntat: PASS, även `tester/enhet/test_gyllene_m1.py`.

- [ ] **Steg 5: Commit**

```bash
git add src/riskanalys/dokument/modeller.py src/riskanalys/dokument/underlag.py src/riskanalys/dokument/faktablad.py src/riskanalys/dokument/promptar/delar.py tester/intag/test_skyddad_begaran.py tester/enhet/test_promptar.py
git commit -m "fix: skyddat utfall och identisk AI-begäran vid smågruppsskydd"
```

---

### Uppgift 4: Små och stora andelar visas konsekvent

**Files:**
- Modify: `src/riskanalys/profil/hantering.py` (ny `visa_varde_klartext`)
- Modify: `src/riskanalys/dokument/underlag.py` (`visa_for_ai`)
- Modify: `src/riskanalys/dokument/faktablad.py` (`_post`)
- Modify: `src/riskanalys/dokument/klartext.py` (`uppgiftstext`, `gransmening`, `gransmening_text`)
- Test: `tester/intag/test_klartext.py`, `tester/intag/test_faktablad.py`

**Interfaces:**
- Produces: `visa_varde_klartext(falt: Falt, varde) -> str`. För `typ == "andel"`: `0 < varde < 0.005` ger "mindre än 1 %", `0.995 <= varde < 1` ger "mer än 99 %", annars `visa_varde(falt, varde)`. Andra typer går direkt till `visa_varde`.

- [ ] **Steg 1: Skriv de fallerande testerna**

Lägg till i `tester/intag/test_faktablad.py`:

```python
from riskanalys.dokument.analysunderlag import sarbarhetsstycke
from riskanalys.dokument.faktablad import bygg_faktablad
from riskanalys.dokument.platshallare import ersatt_tal


def _kundbas(rb, klar, aktiva, riskbransch):
    upp = dict(klar.uppgifter)
    for falt_id, varde in (("P-KUND.antal_aktiva", aktiva), ("P-KUND.antal_riskbransch", riskbransch)):
        upp[falt_id] = upp[falt_id].model_copy(update={"varde": varde})
    return harled_andelar(klar.model_copy(update={"uppgifter": upp}), rb,
                          frozenset({"P-KUND.antal_aktiva", "P-KUND.antal_riskbransch"}))


def test_liten_andel_ar_mindre_an_en_procent_genom_hela_kedjan(tmp_path, rb_intag, klar):
    profil = _kundbas(rb_intag, klar, 2000, 8)
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, profil)
    fb = bygg_faktablad(rb_intag, profil, t, avsnitt_id)
    post = next(p for p in fb.poster if p.id == RISKBRANSCH)
    assert post.visningsvarde == "mindre än 1 %" and post.tal is not None
    assert ersatt_tal(f"{{tal:{RISKBRANSCH}}} av kunderna", fb.numeriska(), fb.perioder()) == "mindre än 1 % av kunderna"
    stycke = sarbarhetsstycke(rb_intag, profil, t.tjanst, _sarb(rb_intag)).text
    assert "mindre än 1 %" in stycke and "är 0 %" not in stycke


def test_stor_andel_ar_mer_an_99_procent_lokalt(tmp_path, rb_intag, klar):
    profil = _kundbas(rb_intag, klar, 1000, 999)
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, profil)
    stycke = sarbarhetsstycke(rb_intag, profil, t.tjanst, _sarb(rb_intag)).text
    assert "mer än 99 %" in stycke and "100 %" not in stycke
```

Importera `tjanst_for_prov` från `tester.fixturer.m2` om filen inte redan gör det. `_sarb` och `RISKBRANSCH` finns redan i filen.

Lägg till i `tester/intag/test_klartext.py`:

```python
from riskanalys.profil.hantering import visa_varde_klartext


@pytest.mark.parametrize("varde,text", [(0.004, "mindre än 1 %"), (0.0, "0 %"), (0.15, "15 %"), (0.996, "mer än 99 %"), (1.0, "100 %")])
def test_visa_varde_klartext_for_andelar(rb_intag, varde, text):
    assert visa_varde_klartext(rb_intag.falt["P-KUND.andel_riskbransch"], varde) == text
```

- [ ] **Steg 2: Kör testerna och se dem fallera**

Kör: `.venv/bin/pytest tester/intag/test_faktablad.py tester/intag/test_klartext.py -q -k "andel or kedjan or klartext_for"`
Förväntat: FAIL (`ImportError: visa_varde_klartext` och "0 %" i faktabladet).

- [ ] **Steg 3: Implementera**

`profil/hantering.py`, efter `visa_varde`:

```python
def visa_varde_klartext(falt: Falt, varde) -> str:
    """Som visa_varde, men en andel avrundas aldrig till 0 % eller 100 % när den inte är det (spec 8.4.9 punkt 7)."""
    if falt.typ == "andel" and type(varde) in (int, float):
        if 0 < varde < 0.005:
            return "mindre än 1 %"
        if 0.995 <= varde < 1:
            return "mer än 99 %"
    return visa_varde(falt, varde)
```

`underlag.py`, `visa_for_ai`: sista raden blir `return visa_varde_klartext(falt, uppgift.varde)` (importera från `riskanalys.profil.hantering`).

`faktablad.py`, `_post`: ett visat värde som börjar med "mindre än " eller "mer än " behåller sin text som `visningsvarde`, och `tal` sätts till talet i texten (1 respektive 99), så att `numeriska()` tar med det och `{tal:…}` ersätts med texten. Skyddade värden ("färre än …", "undertryckt …") får som förut `tal=None`. Lägg konstanten `_GRANSVISNINGAR = ("mindre än ", "mer än ")` i filen.

`klartext.py`: `uppgiftstext` och `gransmening` använder `visa_varde_klartext` i stället för `visa_varde` för värdet. I `gransmening_text` tas specialfallet för "0 %" bort, eftersom värdet redan kommer rätt.

- [ ] **Steg 4: Kör testerna**

Kör: `.venv/bin/pytest tester/intag tester/enhet -q`
Förväntat: PASS, även det gyllene M1-provet.

- [ ] **Steg 5: Commit**

```bash
git add src/riskanalys/profil/hantering.py src/riskanalys/dokument/underlag.py src/riskanalys/dokument/faktablad.py src/riskanalys/dokument/klartext.py tester/intag/test_faktablad.py tester/intag/test_klartext.py
git commit -m "fix: andelar nära 0 och 100 procent visas konsekvent"
```

---

### Uppgift 5: Katalogkoder och kontrollsummor ur löptexten

**Files:**
- Modify: `src/riskanalys/dokument/klartext.py` (nya `paketnamn`, `kod_till_namn`)
- Modify: `src/riskanalys/dokument/arb.py` (`_syfte` D-ARB.1, D-ARB.4 på rad cirka 68, `_metod` hindertexten)
- Modify: `src/riskanalys/dokument/uppfoljning.py` (`bevakningsavsnitt`)
- Test: `tester/intag/test_lasta_stycken.py`, `tester/intag/test_klartext.py`

**Interfaces:**
- Produces:
  - `paketnamn(paket) -> str` tar bort ett avslutande ": {paket.id}" ur paketets namn.
  - `kod_till_namn(regelbas, text) -> str` ersätter kända regelpaket-ID (`RP-…`) med `paketnamn` och kända käll-ID (`SRC-…`) med källans titel. Okända koder lämnas.

- [ ] **Steg 1: Skriv de fallerande testerna**

Lägg till i `tester/intag/test_klartext.py`:

```python
from riskanalys.dokument.klartext import kod_till_namn, paketnamn


def test_paketnamn_utan_kod(rb_intag):
    assert paketnamn(rb_intag.regelpaket["RP-RED-VG"]) == "Bokföring, skatterådgivning och bolagstjänster"


def test_kod_till_namn(rb_intag):
    titel = rb_intag.kallor["SRC-PTL"].titel
    assert kod_till_namn(rb_intag, "Lästa: SRC-PTL och SRC-OKAND.") == f"Lästa: {titel} och SRC-OKAND."
```

Lägg till i `tester/intag/test_lasta_stycken.py` ett prov som bygger hela dokumentet för den kompletta syntetiska profilen (som de befintliga D-ARB.2-proven gör) och, med `P-BEVAKNING.kallor` satt till två registrerade käll-ID med kontrollsumma, kräver för varje avsnitt utom `D-ARB.B1`:

```python
import re
KOD = re.compile(r"\b(?:RP|SRC)-[A-Z0-9]")
...
    for avsnitt in dokument.avsnitt:
        if avsnitt.id == "D-ARB.B1":
            continue
        for s in avsnitt.stycken:
            assert not KOD.search(s.text) and "sha256:" not in s.text, (avsnitt.id, s.text[:120])
```

och att D-ARB.11:s stycke fortfarande har käll-ID:na i `referenser`.

- [ ] **Steg 2: Kör testerna och se dem fallera**

Kör: `.venv/bin/pytest tester/intag/test_klartext.py tester/intag/test_lasta_stycken.py -q -k "paketnamn or kod or katalogkod"`
Förväntat: FAIL.

- [ ] **Steg 3: Implementera**

`klartext.py`:

```python
_KATALOGKOD = re.compile(r"\b(?:RP|SRC)-[A-Z0-9][A-Z0-9-]*\b")


def paketnamn(paket) -> str:
    """Regelpaketets namn utan avslutande kod."""
    return paket.namn.removesuffix(f": {paket.id}")


def kod_till_namn(regelbas: Regelbas, text: str) -> str:
    """Ersätt kända regelpaket- och käll-ID med namn och titlar; okända koder lämnas (spec 8.4.9 punkt 8)."""
    def namn(traff: re.Match[str]) -> str:
        kod = traff.group(0)
        if kod in regelbas.regelpaket:
            return paketnamn(regelbas.regelpaket[kod])
        if kod in regelbas.kallor:
            return regelbas.kallor[kod].titel
        return kod
    return _KATALOGKOD.sub(namn, text)
```

`arb.py`:
- I `_syfte`, använd `paketnamn(paket)` i stället för `paket.namn`.
- I D-ARB.4 (raden med `f'{rb.kallor[k].titel} ({k})'`), skriv bara `rb.kallor[k].titel`. Referenserna behåller `hotkallor`.
- I `_metod`, kör `kod_till_namn` på hindertexten efter `id_till_namn`.

`uppfoljning.py`, `bevakningsavsnitt`:
- Ersätt `' Lästa versioner: ' + '; '.join((id + ' ' + rb.kallor[id].kontrollsumma for id in kanda)) + '. '` med `' Lästa källor: ' + '; '.join(rb.kallor[id].titel for id in kanda) + '. Version och kontrollsumma för varje källa redovisas i bilaga B1. '`.
- Kör `kod_till_namn(rb, text)` på den färdiga texten innan stycket byggs, så att käll-ID i byråns svar på `P-BEVAKNING.kallor` visas som titlar. Referenserna är oförändrade.

- [ ] **Steg 4: Kör testerna**

Kör: `.venv/bin/pytest tester/intag tester/regelkontrakt tester/m2 tester/typfall tester/enhet -q`
Förväntat: PASS. Om ett äldre prov kräver koden i löptexten, ändra det till att kräva koden i referenserna och lista det i rapporten.

- [ ] **Steg 5: Commit**

```bash
git add src/riskanalys/dokument/klartext.py src/riskanalys/dokument/arb.py src/riskanalys/dokument/uppfoljning.py tester/intag/test_klartext.py tester/intag/test_lasta_stycken.py
git commit -m "fix: katalogkoder och kontrollsummor står bara i referenser och bilaga"
```

---

### Uppgift 6: Formatspärr före fastställelse

**Files:**
- Modify: `src/riskanalys/faststallelse/faststall.py` (ny `formathinder`, anrop i `kedjehinder`)
- Test: `tester/enhet/test_formathinder.py` (ny)

**Interfaces:**
- Produces: `formathinder(regelbas: Regelbas, dokument: Dokument) -> list[str]`.

- [ ] **Steg 1: Skriv de fallerande testerna**

```python
from riskanalys.dokument.delskrivning import FORMATVERSION
from riskanalys.dokument.modeller import Avsnitt, Dokument, Textstycke
from riskanalys.faststallelse.faststall import formathinder
from riskanalys.regelverk.laddning import ladda_regelbas
from pathlib import Path


def _dok(version):
    a = Avsnitt(id="D-ARB.6.1", rubrik="Analys", kalla="ai",
                stycken=(Textstycke(typ="beskrivning", text="Text.", referenser=["T-RED-01"]),), formatversion=version)
    return Dokument(id="D", titel="T", avsnitt=(a,))


def test_aldre_format_stoppar_ny_faststallelse():
    hinder = formathinder(ladda_regelbas(), _dok("D-ARB-tjanst-v3"))
    assert hinder and "Skriv om utkastet" in hinder[0]


def test_aktuellt_format_godtas():
    assert formathinder(ladda_regelbas(), _dok(FORMATVERSION)) == []


def test_aldre_regelbas_utan_omfattningsmetod_berors_inte():
    v0 = ladda_regelbas(Path(__file__).resolve().parents[1] / "fixturer" / "regelbas_v0")
    assert formathinder(v0, _dok(None)) == []
```

- [ ] **Steg 2: Kör testerna och se dem fallera**

Kör: `.venv/bin/pytest tester/enhet/test_formathinder.py -q`
Förväntat: FAIL (`ImportError: formathinder`).

- [ ] **Steg 3: Implementera** i `faststall.py`:

```python
def formathinder(regelbas: Regelbas, dokument: Dokument) -> list[str]:
    """Ny fastställelse kräver aktuellt dokumentformat; äldre fastställda paket läses som förut (spec 8.4.9 punkt 9)."""
    from riskanalys.dokument.delskrivning import FORMATVERSION
    if regelbas.metod.omfattning and dokument.formatversion != FORMATVERSION:
        return [f"Granskningen har dokumentformatet {dokument.formatversion}, men aktuellt format är {FORMATVERSION}. "
                "Skriv om utkastet och granska på nytt."]
    return []
```

Lägg `*formathinder(regelbas, las_granskning(granskningsmapp)[0])` sist i listan som `kedjehinder` returnerar. Importera `Dokument` från `riskanalys.dokument.modeller` om den inte redan finns där.

- [ ] **Steg 4: Kör testerna**

Kör: `.venv/bin/pytest tester/enhet/test_formathinder.py tester/enhet/test_faststall.py tester/enhet/test_manifest.py tester/m2 -q`
Förväntat: PASS, och `test_faststall.py` och `test_manifest.py` är oförändrade.

- [ ] **Steg 5: Commit**

```bash
git add src/riskanalys/faststallelse/faststall.py tester/enhet/test_formathinder.py
git commit -m "feat: formatspärr före fastställelse"
```

---

### Uppgift 7: Helhetskontroll och status

**Files:**
- Modify: `docs/STATUS.md`

- [ ] **Steg 1: Kontroller**

Kör: `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest -q`. Förväntat: alla gröna, två livetester bortvalda.

Kör: `.venv/bin/riskanalys regelbas validera && git diff --check`. Förväntat: grönt, regelbas 1.3.0, oförändrad kontrollsumma jämfört med START.

Kör: `START=$(grep -m1 '^START=' docs/superpowers/plans/2026-10-13-skyddad-ai-begaran.md | cut -d= -f2)` och sedan `git diff "$START"..HEAD --stat -- regelbas/ tester/typfall/ tester/enhet/test_faststall.py tester/enhet/test_manifest.py tester/enhet/test_gyllene_m1.py tester/fixturer/`. Förväntat: ingen diff.

- [ ] **Steg 2: Uppdatera `docs/STATUS.md`** med ett nytt avsnitt överst, under ”Senast uppdaterad” (ändra datumet till 2026-10-13), med rubriken `## Skyddad AI-begäran, 2026-10-13`. Avsnittet ska säga:
- att AI aldrig får nivåer, regelspår eller nivåmeningar, och att sårbarheter som bygger på smågruppsskyddade värden har utfallet skyddat
- att ett prov visar identisk begäran för 0 och 3 kunder, för ett litet komplement och för ett smågruppsfält utanför tillåtelselistan
- att andelar nära 0 och 100 % visas som ”mindre än 1 %” och ”mer än 99 %” överallt
- att katalogkoder och kontrollsummor bara står i referenser och bilaga B1
- att ny fastställelse kräver aktuellt dokumentformat
- fullsvitens resultat
- under Kvar: beslutet om utfall för sårbarheter som bygger på uppgifter utanför tillåtelselistan utan smågruppsskydd (S-ARB-01 till S-ARB-18), samt en pilot på en tjänst med `medium` för att pröva formuleringen för faktorer under gränsen och skyddat utfall

- [ ] **Steg 3: Commit**

```bash
git add docs/STATUS.md
git commit -m "docs: status för skyddad AI-begäran"
```

---

## Självgranskning

- **Täckning:**
  - Fynd 1 (läckan): uppgift 2 (nivåer, regelspår, nivåmeningar, schema) och uppgift 3 (utfall, motivering, identitetsprov).
  - Fynd 2 (0 %): uppgift 4.
  - Rekommendationerna: katalogkoder (uppgift 5), formatspärr (uppgift 6), pilot (STATUS, uppgift 7).
- **Typkonsekvens:** `begaran(rb, profil)` definieras i uppgift 2 och används i uppgift 3. `skyddat_villkor(regelbas, profil, sarbarhet_id, tillatna)` och `visa_varde_klartext(falt, varde)` används med samma signatur överallt.
- **Det som inte ändras:** motorns lokala bedömning, dokumentets nivåmeningar, regelbasen och den frysta kedjan.

## Genomförandelogg

START=
