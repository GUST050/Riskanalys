# Skyddad AI-begäran och kvarvarande klartext – implementeringsplan

> **För agentiska utförare:** OBLIGATORISK DELFÄRDIGHET: använd superpowers:subagent-driven-development (rekommenderas) eller superpowers:executing-plans för att genomföra planen uppgift för uppgift. Stegen använder kryssrutor (`- [ ]`).

**Mål:** Den utgående AI-begäran ska bara bero på det AI får se. Två byråer som skiljer sig enbart i uppgifter utanför tillåtelselistan eller i smågruppsskyddade värden ska ge exakt samma begäran. Planen rättar också visningen av andelar nära 0 och 100 %, flyttar katalogkoder och kontrollsummor ur löptexten, lägger en formatspärr per tjänsteavsnitt före fastställelse och stänger den äldre skrivvägen för riktiga AI-anrop.

**Arkitektur:**
- **Inga motorspår till AI.** Faktabladet och delanropen innehåller aldrig motorns nivåer, regelspår eller nivåmeningar. Nivåmeningarna skrivs fortfarande lokalt av koden.
- **Utfallet "prövas lokalt".** En sårbarhet vars villkor läser en uppgift utanför tillåtelselistan, eller ett smågruppsvärde som AI inte ser exakt, får utfallet `prövas lokalt` i faktabladet. Beslutet fattas ur det AI får se, inte ur råvärdet.
- **Kontrollernas kategorifält** läggs uttryckligen in i tillåtelselistan (användarens beslut 2026-10-13). Därmed bygger kontrollstatusen på tillåtna uppgifter.
- **Prov på identitet.** Ett prov bygger hela begäran (systemprompt, innehåll och schema för alla delar, även omförsök) och kräver identitet för grupper av profiler.
- **Övrigt:**
  - Gränsvisning av andelar som bestäms ur den avrundade texten.
  - Ett intervallfält i faktaposterna.
  - En hjälpfunktion för katalogkoder.
  - En formatspärr per tjänsteavsnitt.
  - En spärr i den äldre skrivvägen.

**Teknik:** Python 3.12, Pydantic, pytest, YAML-regelbas.

**Spec:** `docs/superpowers/specs/2026-10-08-riskanalys-design.md`, främst 8.4.1, 8.4.4, 8.4.9 och den nya 8.4.10 som uppgift 1 skriver.

## Bakgrund

Granskningen 2026-10-13 visade att smågruppsskyddet läcker. Med 0 respektive 3 kunder med transaktioner utanför Sverige visar faktabladet samma maskerade värde, ”färre än 5”. Ändå skiljer sig AI-begäran på 96 rader, kontrollerat med syntetiska data:
- risknivåer (måttlig blir hög)
- regelspår (BT-MATRIS-05 blir BT-MATRIS-08)
- sårbarhetens utfall (nej blir ja)
- nivåmeningarna bland de låsta instruktionerna
- svarsschemat, som räknar upp regelspåren som tillåtna ID

Användaren valde att AI aldrig ska få nivåer, regelspår eller nivåmeningar.

Planens granskning 2026-10-13 krävde dessutom:
1. **Utfall som avslöjar uppgifter utanför tillåtelselistan** ska också maskeras, som ”prövas lokalt”, tills det uttryckligen beslutats vilka uppgifter AI får se. 18 sårbarheter (S-ARB-01 till S-ARB-18) har villkor på sådana uppgifter; fyra av dem (S-ARB-04, S-ARB-08, S-ARB-11, S-ARB-14) innehåller också smågruppsfält.
2. **Andelsvisningen** missade exakt 0,5 % (Python avrundar 0,5 till 0 och 99,5 till 100). Ett intervall får inte lagras som talet 1 eller 99.
3. **Formatspärren** ska kontrollera varje tjänsteavsnitt, så att ett dokument med både v3 och v4 inte passerar.
4. **Den äldre skrivvägen** (`skriv_avsnitt` i `skrivning.py`) skickar fortfarande nivåer och regelspår. Den stoppas för riktiga AI-anrop. Historiska paket kan fortfarande läsas.
5. **Identitetsproven** ska omfatta 0, 1, 3 och 4 kunder, saknad bas och omförsök med samma syntetiska svar.
6. **Inga automatiska commits.** Bygggodkännande innebär inte commitgodkännande.

Kontrollernas status härleds ur `P-KONTROLL`-fält som inte fanns i tillåtelselistan. Användaren beslutade 2026-10-13 att kontrollernas kategorifält (`utformning`, `genomforande`, `effekt`) läggs in i tillåtelselistan. Utfallsfältet, som är fritext, läggs inte in.

Planens tredje granskning 2026-10-13 visade:
1. **Kontrollstatusen avslöjar utfallsfältet.** Med samma kategorier skickas "belagd riskreducerande verkan" när utfallstexten är ifylld och "ingen riskreduktion är belagd" när den är tom (`bedomning/motor.py`, `_kontroll`: `effekt_belagd` kräver att `utfall_falt` är belagt). AI:s kontrollstatus ska därför byggas enbart av de tillåtna kategorierna. Bedömningen av belagd riskreduktion stannar lokalt.
2. **Testhjälpen** ska använda verkliga fält-ID i en dictionary.
3. **Restgruppen.** 96, 97 och 99 av 100 visas som "undertryckt", men 100 av 100 visas öppet som 100 %. Identitet krävs inom den maskerade gruppen, och 100 testas separat.

## Global Constraints

- AGENTS.md regel 1: ”AI fattar inga beslut.” Motorns lokala bedömning, nivåer, regelspår och utfall ändras inte. Bara det som skickas till AI ändras.
- AGENTS.md regel 2: ”Inga personuppgifter till AI. AI-underlag byggs bara ur tillåtelselistan i regelbas/tillatelselistor.yaml.” Smågruppsskyddet (`SMA_GRUPPER_GRANS = 5`) gäller oförändrat.
- AGENTS.md regel 4: regelbasen ändras bara i `regelbas/tillatelselistor.yaml` (39 kategorifält för kontroller, med grund i en kommentar). Version 1.3.0 behålls (inte släppt). Inga regler, gränser, källor eller sakkunnigstatus ändras.
- AGENTS.md regel 6: ”Tester före commit … Skriv testet först.” Regel 7: inga anrop mot riktiga API:t i automatiska tester.
- Stil: ”Användartexter och dokumentation på svenska. Identifierare i koden på svenska utan å, ä och ö.” ”Funktioner returnerar nya objekt i stället för att ändra befintliga.”
- Den frysta M1-kedjan ska ge byte för byte samma dokument: `tester/enhet/test_m1_gyllene_dokument.py` och `tester/typfall/` ska passera utan ändringar.
- `tester/enhet/test_faststall.py` och `tester/enhet/test_manifest.py` ska passera utan ändringar. Fastställda paket byggs aldrig om och kan fortfarande läsas.
- `visa_varde` i `profil/hantering.py` ändras inte.
- Dokumentformatet förblir `D-ARB-tjanst-v4`.
- **Inga commits.** Varje uppgift lämnar sina ändringar ostagade. Efter godkänd granskning stagear controllern uppgiftens filer med `git add`, så att nästa uppgifts diff (`git diff`) blir separat. Commit sker först när användaren godkänt det.

## Review Focus

1. **En bool utanför tillåtelselistan** (till exempel `P-RISK.pep`) som avgör utfallet ska inte synas i begäran. Testas i uppgift 3.
2. **Saknad bas:** ett smågruppsfält visas som ”okänt” men har ett bekräftat råvärde som motorn läser. Testas i uppgift 3.
3. **Omförsök:** återkopplingen till ett andra försök får inte bero på skyddade värden. Testas i uppgift 3.
4. **Exakt 0,5 % och 99,5 %** och värden strax intill. Testas i uppgift 5.
5. **Blandat format** (v3 och v4 i samma dokument) och saknad formatmarkering i ett tjänsteavsnitt. Testas i uppgift 7.

## Filer

| Fil | Ansvar | Uppgift |
|---|---|---|
| `docs/superpowers/specs/2026-10-08-riskanalys-design.md` | Revision 19 | 1 |
| `src/riskanalys/dokument/faktablad.py`, `delskrivning.py`, `promptar/delar.py` | Inga motorspår till AI | 2 |
| `src/riskanalys/dokument/modeller.py`, `underlag.py`, `faktablad.py`, `promptar/delar.py` | Utfallet prövas lokalt, identitetsprov | 3 |
| `regelbas/tillatelselistor.yaml`, `src/riskanalys/dokument/underlag.py`, `faktablad.py`, `promptar/delar.py` | Kontrollernas kategorifält och kontrollstatus för AI | 4 |
| `src/riskanalys/profil/hantering.py`, `dokument/underlag.py`, `dokument/faktablad.py`, `dokument/klartext.py` | Andelar nära 0 och 100 % | 5 |
| `src/riskanalys/dokument/klartext.py`, `arb.py`, `uppfoljning.py` | Katalogkoder ur löptexten | 6 |
| `src/riskanalys/faststallelse/faststall.py` | Formatspärr per tjänsteavsnitt | 7 |
| `src/riskanalys/dokument/skrivning.py` | Äldre skrivväg stängd för riktiga AI-anrop | 8 |
| `docs/STATUS.md` | Status | 9 |

---

### Före uppgift 1: Spara start-SHA

- [ ] Skriv `START=e71e99e` följt av hela SHA:t (`git rev-parse e71e99e`) på raden `START=` under ”Genomförandelogg” sist i denna plan. Uppgift 9 jämför mot detta SHA.

---

### Uppgift 1: Spec revision 19

**Files:**
- Modify: `docs/superpowers/specs/2026-10-08-riskanalys-design.md`

- [ ] **Steg 1: Statusraden.** Ersätt `revision 18 (2026-10-12)` med `revision 19 (2026-10-13)` på rad 3.

- [ ] **Steg 2: Tabellen i 8.4.4.** I raden som börjar `| Risknivåer och motivering |`, ersätt `Nivån som en kedja av hot, sårbarhet, omfattning och konsekvens; förklara avvikelse från NRA:s sektorsnivå` med `Riskbilden som en kedja av hot, sårbarhet, omfattning och konsekvens, utan att AI ser motorns nivåer; förklara skillnader mot NRA:s sektorsnivå`. I raden som börjar `| Slutsatser |`, ersätt `Vad nivån betyder för kundkännedom, övervakning och utbildning i just denna tjänst` med `Vad riskbilden betyder för kundkännedom, övervakning och utbildning i just denna tjänst`.

- [ ] **Steg 3: Tre punkter sist i 8.4.9**, efter punkt 6:

```markdown
7. En andel som är större än noll men skulle visas som 0 % skrivs ”mindre än 1 %”, och en andel under 100 % som skulle visas som 100 % skrivs ”mer än 99 %”. Det gäller på samma sätt i låsta stycken, faktablad och platshållare. Ett sådant intervall lagras inte som ett exakt tal.
8. Katalogkoder och kontrollsummor (regelpaket, källor) står bara i referenser och i bilagan `D-ARB.B1`. Löptexten använder titlar och namn.
9. Ny fastställelse kräver att varje tjänsteavsnitt i granskningens dokument har aktuellt format. Äldre fastställda paket kan fortfarande läsas.
```

- [ ] **Steg 4: Nytt avsnitt 8.4.10**, direkt efter 8.4.9 och före `## 9 Granskning (maskinell)`:

```markdown
#### 8.4.10 Skyddad AI-begäran

1. Hela den utgående begäran till AI – systemprompt, varje dels innehåll, återkoppling vid omförsök och svarsschema – ska bara bero på det AI får se. Två profiler som bara skiljer sig i uppgifter utanför tillåtelselistan eller i smågruppsskyddade värden (värden som AI ser maskerade eller som okända) ska ge identisk begäran.
2. AI får därför aldrig motorns risknivåer, regelspår eller de kodskrivna nivåmeningarna. Nivåmeningarna skrivs som tidigare lokalt i dokumentet. AI motiverar riskbilden utifrån hot, sårbarheter, kontroller och faktauppgifter utan att ange nivåer.
3. En sårbarhet vars villkor läser en uppgift utanför tillåtelselistan eller ett smågruppsskyddat värde får utfallet ”prövas lokalt” i faktabladet. Beslutet fattas ur det AI får se, inte ur råvärdet. Motorns lokala bedömning ändras inte. Sårbarhetskatalogen beskriver fortfarande möjliga hot och faktorer, medan programmet skriver den lokala tillämpningen.
4. Kontrollernas kategorifält (utformning, genomförande och bedömd effekt) ingår i tillåtelselistan efter beslut 2026-10-13. Kontrollernas utfallstext ingår inte. Kontrollstatusen till AI byggs enbart av kategorierna. Om en kontroll räknas som riskreducerande avgörs lokalt, eftersom den bedömningen också bygger på utfallsfältet, och AI skriver aldrig att en kontroll minskar risken.
5. Den äldre skrivvägen utan faktablad får inte användas med riktiga AI-anrop. Historiska utkast och paket kan fortfarande läsas.
6. Prov visar identisk begäran för 0, 1, 3 och 4 kunder, för ett maskerat litet komplement, för saknad bas, för ett smågruppsfält och en ja/nej-uppgift utanför tillåtelselistan, för kontrollernas utfallstext och vid omförsök.
```

- [ ] **Steg 5: Rad 19 i revisionsloggen**, direkt efter rad 18:

```markdown
| 19 | 2026-10-13 | Efter granskning med syntetiska data: AI-begäran beror bara på det AI får se – inga nivåer, regelspår eller nivåmeningar till AI, utfallet ”prövas lokalt” för sårbarheter som bygger på uppgifter utanför tillåtelselistan eller smågruppsskyddade värden, kontrollernas kategorifält i tillåtelselistan och den äldre skrivvägen stängd för riktiga AI-anrop (8.4.10). Andelar nära 0 och 100 % visas konsekvent, katalogkoder och kontrollsummor flyttas till referenser och bilaga B1, och fastställelse kräver aktuellt format i varje tjänsteavsnitt (8.4.9). Inga ändrade regler, gränser eller nivåer. |
```

- [ ] **Steg 6:** Ingen commit. Lämna ändringen ostagad för granskning.

---

### Uppgift 2: Inga nivåer, regelspår eller nivåmeningar till AI

**Files:**
- Modify: `src/riskanalys/dokument/faktablad.py` (`bygg_faktablad`)
- Modify: `src/riskanalys/dokument/delskrivning.py` (`skyddade_lasta_texter`)
- Modify: `src/riskanalys/dokument/promptar/delar.py` (modulerna `risknivaer` och `slutsatser`)
- Test: `tester/intag/test_skyddad_begaran.py` (ny), `tester/intag/test_v3_grind.py:88-95`, `tester/enhet/test_promptar.py`

**Interfaces:**
- Produces: `Faktablad.nivaer == {}` och `Faktablad.regelspar == ()` för nya faktablad. Fälten finns kvar, så äldre sparade resultat kan läsas. `tillatna_id()` innehåller inga regelspår.
- Produces: testhjälpen `begaran(rb, profil, svar=None) -> list[dict]` i `tester/intag/test_skyddad_begaran.py`. `svar` är en funktion `t -> list[AISvar]`; utan den används `godkant_delsvar` för alla delar.

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


def begaran(rb, profil, svar=None):
    """Hela den utgående AI-begäran för första tjänsten: systemprompt, innehåll och schema för varje anrop."""
    with tempfile.TemporaryDirectory() as mapp:
        avsnitt_id, t = tjanst_for_prov(Path(mapp), rb, profil)
        svarslista = svar(t) if svar else [godkant_delsvar(d, t) for d in DELAR]
        lev = Testleverantor(svarslista)
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

- [ ] **Steg 2: Kör och se dem fallera.** `.venv/bin/pytest tester/intag/test_skyddad_begaran.py tester/intag/test_v3_grind.py tester/enhet/test_promptar.py -q` ger FAIL: begäran innehåller "BT-" och nivåer, och modulen saknar meningen.

- [ ] **Steg 3: Implementera**

I `faktablad.py`, `bygg_faktablad`: ersätt `nivaer=underlag.nivaer` med `nivaer={}` och `regelspar=underlag.regelspar` med `regelspar=()`. Lägg kommentaren `# Motorns nivåer och regelspår skickas aldrig till AI (spec 8.4.10).` på raden ovanför.

I `delskrivning.py`, `skyddade_lasta_texter`, ersätt grenen för `risknivaer` med:

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
        "motivera skillnader med det belagda underlaget, eftersom föreskrifterna kräver att risknivåerna motiveras.\n"
        "Använd de maskinellt validerade delarna som underlag och upprepa dem inte. Minst ett stycke ska ha typen "
        "motivering och hänvisa till minst ett hot och en sårbarhet eller uppgift."
    ),
```

I modulen `slutsatser`, ersätt `Förklara vad motorns nivå betyder för just den här tjänsten:` med `Förklara vad riskbilden betyder för just den här tjänsten:` och `slutsatser som bara upprepar nivån` med `slutsatser som bara upprepar riskbilden`.

Sök efter andra prov som kräver nivåer eller regelspår i faktabladet eller i begäran (`grep -rn "nivaer\|regelspar" tester/intag tester/enhet`). Uppdatera dem till den nya regeln och lista dem i rapporten. Prov för de lokala nivåmeningarna (till exempel `tester/intag/test_nivatext.py`) ändras inte.

- [ ] **Steg 4: Kör.** `.venv/bin/pytest tester/intag tester/enhet/test_promptar.py tester/enhet/test_delvalidering.py -q` ger PASS.

- [ ] **Steg 5:** Ingen commit. Lämna ändringarna ostagade.

---

### Uppgift 3: Utfallet ”prövas lokalt” och identisk begäran

**Files:**
- Modify: `src/riskanalys/dokument/modeller.py` (`UnderlagSarbarhet.galler`)
- Modify: `src/riskanalys/dokument/underlag.py` (ny `provas_lokalt`, konstanten `LOKALT_UTFALL`)
- Modify: `src/riskanalys/dokument/faktablad.py` (`bygg_faktablad`)
- Modify: `src/riskanalys/dokument/promptar/delar.py` (modulerna `sarbarheter` och `risknivaer`)
- Test: `tester/intag/test_skyddad_begaran.py`, `tester/enhet/test_promptar.py`

**Interfaces:**
- Consumes: `begaran(rb, profil, svar=None)` från uppgift 2. `SKYDDADE_VISNINGAR` och `_uppgift` i `underlag.py`.
- Produces: `UnderlagSarbarhet.galler: Literal["ja", "nej", "okänt", "prövas lokalt"]`. `underlag.provas_lokalt(regelbas, profil, sarbarhet_id, tillatna) -> bool`.

- [ ] **Steg 1: Skriv de fallerande testerna.** Lägg till i `tester/intag/test_skyddad_begaran.py`:

```python
import pytest

from riskanalys.dokument.modeller import AIStycke, AISvar
from riskanalys.profil.modeller import Uppgift
from riskanalys.profil.omfattning import harled_andelar


def _med(rb, profil, varden: dict):
    """Ny profil med ändrade värden (verkliga fält-ID som nycklar); andelar härleds på nytt ur ändrade antal."""
    upp = dict(profil.uppgifter)
    for falt_id, varde in varden.items():
        upp[falt_id] = upp[falt_id].model_copy(update={"varde": varde})
    ny = profil.model_copy(update={"uppgifter": upp})
    return harled_andelar(ny, rb, frozenset(varden))


def _lika(rb, profiler, svar=None):
    forsta = begaran(rb, profiler[0], svar)
    return all(begaran(rb, p, svar) == forsta for p in profiler[1:])


def test_liten_grupp_0_1_3_4_ger_samma_begaran(rb_intag, klar):
    assert _lika(rb_intag, [_med(rb_intag, klar, {"P-GEO.antal_utland_transaktion": n}) for n in (0, 1, 3, 4)])


def test_maskerat_litet_komplement_ger_samma_begaran(rb_intag, klar):
    # 96, 97 och 99 av 100 visas som "undertryckt"; 100 av 100 visas öppet och prövas separat.
    assert _lika(rb_intag, [_med(rb_intag, klar, {"P-KUND.antal_riskbransch": n}) for n in (96, 97, 99)])


def test_hela_kundbasen_visas_oppet(tmp_path, rb_intag, klar):
    from riskanalys.dokument.faktablad import bygg_faktablad
    profil = _med(rb_intag, klar, {"P-KUND.antal_riskbransch": 100})
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, profil)
    fb = bygg_faktablad(rb_intag, profil, t, avsnitt_id)
    assert next(p for p in fb.poster if p.id == "P-KUND.andel_riskbransch").visningsvarde == "100 %"
    assert next(s for s in fb.sarbarheter if s.id == "S-KUND-01").galler == "ja"


def test_smagruppsfalt_utanfor_tillatelselistan_ger_samma_begaran(rb_intag, klar):
    assert _lika(rb_intag, [_med(rb_intag, klar, {"P-GEO.antal_agare_utanfor_ees": n}) for n in (0, 1, 3, 4)])


def test_ja_nej_uppgift_utanfor_tillatelselistan_ger_samma_begaran(rb_intag, klar):
    assert _lika(rb_intag, [_med(rb_intag, klar, {"P-RISK.pep": v}) for v in (True, False)])


def test_saknad_bas_ger_samma_begaran(rb_intag, klar):
    def utan_bas(andel):
        upp = dict(klar.uppgifter)
        upp["P-GEO.antal_utland_transaktion"] = Uppgift()
        upp["P-GEO.andel_utland_transaktion"] = upp["P-KUND.antal_aktiva"].model_copy(update={"varde": andel})
        return klar.model_copy(update={"uppgifter": upp})
    assert _lika(rb_intag, [utan_bas(0.0), utan_bas(0.03)])


def test_omforsok_ger_samma_begaran(rb_intag, klar):
    def svar(t):
        from riskanalys.dokument.promptar import DELAR
        from tester.fixturer.m2 import godkant_delsvar
        dalig = AISvar(stycken=[AIStycke(typ="analys", referenser=[t.tjanst], text="Risken är hög.")], oklarheter=[])
        return [dalig] + [godkant_delsvar(d, t) for d in DELAR]
    assert _lika(rb_intag, [_med(rb_intag, klar, {"P-GEO.antal_utland_transaktion": n}) for n in (0, 3)], svar)


def test_utfallet_provas_lokalt_i_faktabladet(rb_intag, klar):
    text = json.dumps(begaran(rb_intag, klar), ensure_ascii=False)
    assert '"galler": "prövas lokalt"' in text
```

Fält-ID:n är verifierade mot regelbasen: antalsfälten för `P-GEO.andel_utland_transaktion`, `P-KUND.andel_riskbransch` och `P-GEO.andel_agare_utanfor_ees` är `P-GEO.antal_utland_transaktion`, `P-KUND.antal_riskbransch` och `P-GEO.antal_agare_utanfor_ees`. Testprofilen har 100 aktiva kunder. Om ett fält saknas i testprofilen, använd en `Uppgift` kopierad från `P-KUND.antal_aktiva` med nytt värde. Om 100 av 100 i testprofilen ändå visas maskerat, skriv det i rapporten och låt `test_hela_kundbasen_visas_oppet` pröva det verkliga beteendet i stället för att ändra skyddet.

I `tester/enhet/test_promptar.py`:

```python
def test_modulerna_beskriver_utfallet_provas_lokalt():
    assert "prövas lokalt" in delmodul("sarbarheter")
    assert "prövas lokalt" in delmodul("risknivaer")
```

- [ ] **Steg 2: Kör och se dem fallera.** `.venv/bin/pytest tester/intag/test_skyddad_begaran.py tester/enhet/test_promptar.py -q` ger FAIL för identitet och utfall.

- [ ] **Steg 3: Implementera**

`modeller.py`, `UnderlagSarbarhet`: `galler: Literal["ja", "nej", "okänt", "prövas lokalt"]`.

`underlag.py`, efter `SKYDDADE_VISNINGAR`:

```python
LOKALT_UTFALL = "Utfallet redovisas inte i faktabladet; sårbarheten prövas lokalt."


def provas_lokalt(regelbas: Regelbas, profil: Profil, sarbarhet_id: str, tillatna: tuple[str, ...]) -> bool:
    """Sant när villkoret läser en uppgift som AI inte får se exakt: utanför tillåtelselistan, eller ett
    smågruppsfält som visas maskerat eller okänt. Avgörs ur den synliga vyn (spec 8.4.10)."""
    from riskanalys.regelverk.villkor import falt_i
    villkor = tolka_villkor(regelbas.sarbarheter[sarbarhet_id].villkor, regelbas.faltdefinitioner())
    for falt_id in falt_i(villkor):
        if falt_id not in tillatna:
            return True
        if regelbas.falt[falt_id].smagrupp:
            visning = _uppgift(regelbas, profil, falt_id).varde
            if visning.startswith(SKYDDADE_VISNINGAR) or visning == "okänt":
                return True
    return False
```

`faktablad.py`, `bygg_faktablad`: hämta `tillatna = regelbas.tillatelselistor[AVSNITTSTYP].falt` (importera `AVSNITTSTYP`, `LOKALT_UTFALL` och `provas_lokalt` från `riskanalys.dokument.underlag`) och bygg sårbarheterna som

```python
        sarbarheter=tuple(
            s.model_copy(update={"galler": "prövas lokalt", "motivering": LOKALT_UTFALL})
            if provas_lokalt(regelbas, profil, s.id, tillatna) else s
            for s in underlag.sarbarheter),
```

`promptar/delar.py`:
- I modulen `sarbarheter`, lägg till raden `"Om en sårbarhets utfall är prövas lokalt skriver du att den prövas lokalt, utan att säga om den gäller.\n"` direkt före raden `"Programmet har redan skrivit underlagsstycket för geografin. Bygg vidare på det."`.
- I modulen `risknivaer`, lägg till meningen ` Sårbarheter med utfallet prövas lokalt beskriver du inte som gällande eller inte gällande.` direkt efter `eftersom föreskrifterna kräver att risknivåerna motiveras.` (före `\n`).

Kontrollera att ingen kod förutsätter att `galler` bara kan vara ja, nej eller okänt (`grep -rn "galler" src/riskanalys`). Den lokala bedömningen och de låsta styckena använder motorns utfall och ändras inte.

- [ ] **Steg 4: Kör.** `.venv/bin/pytest tester/intag tester/enhet -q` ger PASS, även `tester/enhet/test_m1_gyllene_dokument.py`.

- [ ] **Steg 5:** Ingen commit.

---

### Uppgift 4: Kontrollernas kategorifält och kontrollstatus för AI

**Files:**
- Modify: `regelbas/tillatelselistor.yaml` (listan `risk_per_tjanst`)
- Modify: `src/riskanalys/dokument/underlag.py` (ny `kontrollstatus_for_ai`)
- Modify: `src/riskanalys/dokument/faktablad.py` (`bygg_faktablad`, kontrollernas status)
- Modify: `src/riskanalys/dokument/promptar/delar.py` (modulen `kontroller`)
- Test: `tester/regelkontrakt/test_tillatelselista_kontroller.py` (ny), `tester/intag/test_skyddad_begaran.py`, `tester/enhet/test_promptar.py`

**Interfaces:**
- Consumes: `begaran` och `_lika` från uppgift 2 och 3.
- Produces: för varje kontroll `k` i regelbasen finns `k.utformning_falt`, `k.genomforande_falt` och `k.effekt_falt` i `risk_per_tjanst`; `k.utfall_falt` finns inte där.
- Produces: `underlag.kontrollstatus_for_ai(kontroll: Kontrollbedomning) -> str`, byggd enbart av `utformning`, `genomforande` och `effekt`. Faktabladets kontroller får den statusen. Den lokala `kontrollstatus` och motorns `effekt_belagd`/`fungerar_och_ar_belagd` ändras inte.

- [ ] **Steg 1: Skriv de fallerande testerna**

`tester/regelkontrakt/test_tillatelselista_kontroller.py`:

```python
from riskanalys.dokument.underlag import AVSNITTSTYP
from riskanalys.regelverk.laddning import ladda_regelbas


def test_kontrollernas_kategorifalt_ar_tillatna_men_inte_utfallstexten():
    rb = ladda_regelbas()
    tillatna = set(rb.tillatelselistor[AVSNITTSTYP].falt)
    for k in rb.kontroller.values():
        for falt_id in (k.utformning_falt, k.genomforande_falt, k.effekt_falt):
            assert falt_id in tillatna and rb.falt[falt_id].typ == "val", falt_id
        if k.utfall_falt:
            assert k.utfall_falt not in tillatna
```

Lägg till i `tester/intag/test_skyddad_begaran.py`:

```python
def test_kontrollernas_utfallstext_ger_samma_begaran(rb_intag, klar):
    # Samma kategorier (utformning, genomförande, effekt); bara den otillåtna utfallstexten skiljer.
    kontroller = rb_intag.tjanster["T-RED-01"].kontroller
    utfall = [rb_intag.kontroller[k].utfall_falt for k in kontroller if rb_intag.kontroller[k].utfall_falt]
    ifylld = klar
    tom = klar.model_copy(update={"uppgifter": {**klar.uppgifter, **{f: Uppgift() for f in utfall}}})
    assert utfall and _lika(rb_intag, [ifylld, tom])


def test_ai_far_ingen_bedomning_av_belagd_riskreduktion(rb_intag, klar):
    text = json.dumps(begaran(rb_intag, klar), ensure_ascii=False)
    assert "belagd riskreducerande verkan" not in text and "ingen riskreduktion är belagd" not in text
```

Kontrollera att `tjanst_for_prov` väljer T-RED-01 för testprofilen. Gör den inte det, använd den tjänst den väljer.

Lägg till i `tester/enhet/test_promptar.py`:

```python
def test_kontrollmodulen_sager_att_riskreduktion_avgors_lokalt():
    assert "avgör programmet lokalt" in delmodul("kontroller")
```

- [ ] **Steg 2: Kör och se dem fallera.** `.venv/bin/pytest tester/regelkontrakt/test_tillatelselista_kontroller.py tester/intag/test_skyddad_begaran.py tester/enhet/test_promptar.py -q -k "kontroll or riskreduktion"` ger FAIL.

- [ ] **Steg 3: Implementera**

`regelbas/tillatelselistor.yaml`: lägg till de 39 fälten (13 kontroller × utformning, genomförande och effekt) sist i listan `falt` under `risk_per_tjanst`, i kontrollernas ordning i `regelbas/kataloger/kontroller.yaml`. Skriv en kommentarsrad före dem: `# Kontrollernas kategorifält (fasta val, ingen fritext); beslut 2026-10-13, spec 8.4.10 punkt 4.` Ändra inget annat i regelbasen.

`underlag.py`, efter `kontrollstatus`:

```python
def kontrollstatus_for_ai(kontroll: Kontrollbedomning) -> str:
    """Kontrollens status för AI, byggd enbart av tillåtna kategorifält. Om riskreduktionen är belagd bygger
    även på utfallsfältet och avgörs därför lokalt (spec 8.4.10 punkt 4)."""
    return (f"utformning {kontroll.utformning or 'okänd'}, genomförande {kontroll.genomforande or 'okänt'}, "
            f"bedömd effekt {kontroll.effekt or 'okänd'}; om kontrollen räknas som riskreducerande avgör programmet lokalt")
```

`faktablad.py`, `bygg_faktablad`: bygg en uppslagning av tjänstens kontrollbedömningar (`tjanstbedomning.kontroller` plus `tjanstbedomning.sanktionsrisk.kontroll` när den finns) och ge varje kontroll i faktabladet statusen `kontrollstatus_for_ai(...)`:

```python
    bedomda = {k.id: k for k in (*tjanstbedomning.kontroller,
               *((tjanstbedomning.sanktionsrisk.kontroll,) if tjanstbedomning.sanktionsrisk and tjanstbedomning.sanktionsrisk.kontroll else ()))}
    ...
        kontroller=tuple(k.model_copy(update={"status": kontrollstatus_for_ai(bedomda[k.id])}) for k in underlag.kontroller),
```

`promptar/delar.py`, ersätt modulen `kontroller` med:

```python
    "kontroller": (
        "Skriv delen Kontroller och effekt för tjänsten. Programmet har redan skrivit varje kontrolls status och belägg. "
        "Förklara vilken risk varje kontroll riktar sig mot och vad utformning, genomförande och bedömd effekt innebär "
        "för tjänsten, eftersom vägledningen kräver att effekten bedöms innan riskerna vägs samman.\n"
        "Om en kontroll räknas som riskreducerande avgör programmet lokalt. Skriv därför aldrig att en kontroll minskar, "
        "begränsar eller reducerar risk. En beskriven kontroll, någon annans kundkännedom eller ett system ersätter inte "
        "en belagd effekt, och hög inneboende risk kan inte elimineras helt med kontroller."
    ),
```

Valideringen i `delvalidering.py` (`_BELAGD_EFFEKT` i kontrollens status) fortsätter att underkänna påståenden om minskad risk. Med den nya statusen finns ingen kontroll med belagd effekt i faktabladet, så alla sådana påståenden underkänns. Valideringens egna enhetsprov med syntetiska faktablad ändras inte.

- [ ] **Steg 4: Kör.** `.venv/bin/pytest tester/regelkontrakt tester/intag tester/enhet -q && .venv/bin/riskanalys regelbas validera` ger PASS och grön validering, version 1.3.0, ny kontrollsumma. Om ett prov pinnar tillåtelselistans innehåll eller regelbasens kontrollsumma, uppdatera bara det värdet och lista det i rapporten.

- [ ] **Steg 5:** Ingen commit.

---

### Uppgift 5: Andelar nära 0 och 100 % visas konsekvent

**Files:**
- Modify: `src/riskanalys/profil/hantering.py` (ny `visa_varde_klartext`)
- Modify: `src/riskanalys/dokument/underlag.py` (`visa_for_ai`)
- Modify: `src/riskanalys/dokument/faktablad.py` (`Faktapost`, `_post`, `Faktablad.numeriska`)
- Modify: `src/riskanalys/dokument/klartext.py` (`uppgiftstext`, `gransmening`, `gransmening_text`)
- Test: `tester/intag/test_klartext.py`, `tester/intag/test_faktablad.py`

**Interfaces:**
- Produces: `visa_varde_klartext(falt, varde) -> str`. För `typ == "andel"` och ett numeriskt värde: om `visa_varde` ger "0 %" fast värdet är större än 0 blir det "mindre än 1 %", och om `visa_varde` ger "100 %" fast värdet är mindre än 1 blir det "mer än 99 %". Annars gäller `visa_varde`.
- Produces: `Faktapost.intervall: bool = False`. En post med intervallvisning har `tal=None` och `intervall=True`, och `numeriska()` tar med den, så att `{tal:ID}` ersätts med intervalltexten.

- [ ] **Steg 1: Skriv de fallerande testerna**

I `tester/intag/test_klartext.py`:

```python
from riskanalys.profil.hantering import visa_varde_klartext


@pytest.mark.parametrize("varde,text", [
    (0.0, "0 %"), (0.0049, "mindre än 1 %"), (0.005, "mindre än 1 %"), (0.0051, "1 %"),
    (0.9949, "99 %"), (0.995, "mer än 99 %"), (0.9951, "mer än 99 %"), (1.0, "100 %"), (0.15, "15 %"),
])
def test_visa_varde_klartext_for_andelar(rb_intag, varde, text):
    assert visa_varde_klartext(rb_intag.falt["P-KUND.andel_riskbransch"], varde) == text
```

Om `visa_varde` avrundar 0,0051 eller 0,9949 annorlunda än ovan, behåll testets princip (ingen visning ”0 %” över noll och ingen ”100 %” under ett) och justera bara förväntningen för de värden som inte är gränsfall. Skriv i rapporten vad `visa_varde` ger.

I `tester/intag/test_faktablad.py`:

```python
from riskanalys.dokument.analysunderlag import sarbarhetsstycke
from riskanalys.dokument.faktablad import bygg_faktablad
from riskanalys.dokument.platshallare import ersatt_tal
from tester.fixturer.m2 import tjanst_for_prov


def _kundbas(rb, klar, aktiva, riskbransch):
    upp = dict(klar.uppgifter)
    for falt_id, varde in (("P-KUND.antal_aktiva", aktiva), ("P-KUND.antal_riskbransch", riskbransch)):
        upp[falt_id] = upp[falt_id].model_copy(update={"varde": varde})
    return harled_andelar(klar.model_copy(update={"uppgifter": upp}), rb,
                          frozenset({"P-KUND.antal_aktiva", "P-KUND.antal_riskbransch"}))


@pytest.mark.parametrize("aktiva,antal", [(2000, 8), (2000, 10)])  # 0,4 % och exakt 0,5 %
def test_liten_andel_ar_ett_intervall_genom_hela_kedjan(tmp_path, rb_intag, klar, aktiva, antal):
    profil = _kundbas(rb_intag, klar, aktiva, antal)
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, profil)
    fb = bygg_faktablad(rb_intag, profil, t, avsnitt_id)
    post = next(p for p in fb.poster if p.id == RISKBRANSCH)
    assert post.visningsvarde == "mindre än 1 %" and post.tal is None and post.intervall
    assert ersatt_tal(f"{{tal:{RISKBRANSCH}}} av kunderna", fb.numeriska(), fb.perioder()) == "mindre än 1 % av kunderna"
    stycke = sarbarhetsstycke(rb_intag, profil, t.tjanst, _sarb(rb_intag)).text
    assert "mindre än 1 %" in stycke and "är 0 %" not in stycke


@pytest.mark.parametrize("aktiva,antal", [(1000, 999), (1000, 995)])  # 99,9 % och exakt 99,5 %
def test_stor_andel_ar_mer_an_99_procent_lokalt(tmp_path, rb_intag, klar, aktiva, antal):
    profil = _kundbas(rb_intag, klar, aktiva, antal)
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, profil)
    stycke = sarbarhetsstycke(rb_intag, profil, t.tjanst, _sarb(rb_intag)).text
    assert "mer än 99 %" in stycke and "100 %" not in stycke
```

- [ ] **Steg 2: Kör och se dem fallera.** `.venv/bin/pytest tester/intag/test_faktablad.py tester/intag/test_klartext.py -q -k "andel or intervall or klartext_for"` ger FAIL.

- [ ] **Steg 3: Implementera**

`profil/hantering.py`, efter `visa_varde`:

```python
def visa_varde_klartext(falt: Falt, varde) -> str:
    """Som visa_varde, men en andel visas aldrig som 0 % eller 100 % när den inte är det (spec 8.4.9 punkt 7).
    Gränsen bestäms ur den avrundade texten, så att avrundningsregeln alltid följs."""
    text = visa_varde(falt, varde)
    if falt.typ == "andel" and type(varde) in (int, float):
        if text == "0 %" and varde > 0:
            return "mindre än 1 %"
        if text == "100 %" and varde < 1:
            return "mer än 99 %"
    return text
```

Kontrollera vilken exakt sträng `visa_varde` ger för 0 och 1 (till exempel `"0 %"` med vanligt eller hårt mellanslag) och jämför mot just den.

`underlag.py`, `visa_for_ai`: sista raden blir `return visa_varde_klartext(falt, uppgift.varde)`.

`faktablad.py`:
- `Faktapost` får fältet `intervall: bool = False`.
- I `_post`: ett visat värde som börjar med "mindre än " eller "mer än " (konstanten `_INTERVALLVISNINGAR = ("mindre än ", "mer än ")`) ger `visningsvarde` = texten, `tal=None` och `intervall=True`. Skyddade värden behandlas som förut.
- `numeriska()` returnerar `{p.id: p.visningsvarde for p in self.poster if p.tal is not None or p.intervall}`.

`klartext.py`: `uppgiftstext` och `gransmening` använder `visa_varde_klartext` för värdet. Specialfallet för "0 %" i `gransmening_text` tas bort.

Kontrollera att ingen validering använder `Faktapost.tal` på ett sätt som påverkas av att ett intervall har `tal=None` (`grep -rn "\.tal\b" src/riskanalys`).

- [ ] **Steg 4: Kör.** `.venv/bin/pytest tester/intag tester/enhet -q` ger PASS, även det gyllene M1-provet.

- [ ] **Steg 5:** Ingen commit.

---

### Uppgift 6: Katalogkoder och kontrollsummor ur löptexten

**Files:**
- Modify: `src/riskanalys/dokument/klartext.py` (nya `paketnamn`, `kod_till_namn`)
- Modify: `src/riskanalys/dokument/arb.py` (`_syfte` D-ARB.1, D-ARB.4 på raden med `f'{rb.kallor[k].titel} ({k})'`, `_metod` hindertexten)
- Modify: `src/riskanalys/dokument/uppfoljning.py` (`bevakningsavsnitt`)
- Test: `tester/intag/test_klartext.py`, `tester/intag/test_lasta_stycken.py`

**Interfaces:**
- Produces: `paketnamn(paket) -> str` tar bort ett avslutande ": {paket.id}". `kod_till_namn(regelbas, text) -> str` ersätter kända `RP-…` med `paketnamn` och kända `SRC-…` med källans titel; okända koder lämnas.

- [ ] **Steg 1: Skriv de fallerande testerna**

I `tester/intag/test_klartext.py`:

```python
from riskanalys.dokument.klartext import kod_till_namn, paketnamn


def test_paketnamn_utan_kod(rb_intag):
    assert paketnamn(rb_intag.regelpaket["RP-RED-VG"]) == "Bokföring, skatterådgivning och bolagstjänster"


def test_kod_till_namn(rb_intag):
    titel = rb_intag.kallor["SRC-PTL"].titel
    assert kod_till_namn(rb_intag, "Lästa: SRC-PTL och SRC-OKAND.") == f"Lästa: {titel} och SRC-OKAND."
```

I `tester/intag/test_lasta_stycken.py`: ett prov som bygger hela dokumentet för den kompletta syntetiska profilen (som de befintliga D-ARB.2-proven gör), med `P-BEVAKNING.kallor` satt till två registrerade käll-ID med kontrollsumma. För varje avsnitt utom `D-ARB.B1` och varje stycke ska `re.search(r"\b(?:RP|SRC)-[A-Z0-9]", s.text)` vara falskt och `"sha256:" not in s.text`. D-ARB.11:s stycke ska ha käll-ID:na i `referenser`.

- [ ] **Steg 2: Kör och se dem fallera.**

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
- I D-ARB.4, skriv bara `rb.kallor[k].titel` (referenserna behåller `hotkallor`).
- I `_metod`, kör `kod_till_namn` på hindertexten efter `id_till_namn`.

`uppfoljning.py`, `bevakningsavsnitt`:
- Ersätt raden med `' Lästa versioner: '` med `text += ' Lästa källor: ' + '; '.join(rb.kallor[id].titel for id in kanda) + '. Version och kontrollsumma för varje källa redovisas i bilaga B1. '`.
- Kör `kod_till_namn(rb, text)` på den färdiga texten innan stycket byggs. Referenserna är oförändrade.

- [ ] **Steg 4: Kör.** `.venv/bin/pytest tester/intag tester/regelkontrakt tester/m2 tester/typfall tester/enhet -q` ger PASS. Om ett äldre prov kräver koden i löptexten, låt det kräva koden i referenserna och lista det i rapporten.

- [ ] **Steg 5:** Ingen commit.

---

### Uppgift 7: Formatspärr per tjänsteavsnitt

**Files:**
- Modify: `src/riskanalys/faststallelse/faststall.py` (ny `formathinder`, anrop i `kedjehinder`)
- Test: `tester/enhet/test_formathinder.py` (ny)

**Interfaces:**
- Produces: `formathinder(regelbas: Regelbas, dokument: Dokument) -> list[str]`, en rad per tjänsteavsnitt (`id` som börjar med `"D-ARB.6."`) vars `formatversion` inte är `FORMATVERSION`, när regelbasen har omfattningsmetod.

- [ ] **Steg 1: Skriv de fallerande testerna**

```python
from pathlib import Path

from riskanalys.dokument.delskrivning import FORMATVERSION
from riskanalys.dokument.modeller import Avsnitt, Dokument, Textstycke
from riskanalys.faststallelse.faststall import formathinder
from riskanalys.regelverk.laddning import ladda_regelbas


def _avsnitt(id, version):
    return Avsnitt(id=id, rubrik="Analys", kalla="ai",
                   stycken=(Textstycke(typ="beskrivning", text="Text.", referenser=["T-RED-01"]),), formatversion=version)


def _dok(*avsnitt):
    return Dokument(id="D", titel="T", avsnitt=avsnitt)


def test_blandat_format_stoppar():
    hinder = formathinder(ladda_regelbas(), _dok(_avsnitt("D-ARB.6.1", FORMATVERSION), _avsnitt("D-ARB.6.2", "D-ARB-tjanst-v3")))
    assert len(hinder) == 1 and "D-ARB.6.2" in hinder[0] and "Skriv om utkastet" in hinder[0]


def test_saknad_formatmarkering_i_tjansteavsnitt_stoppar():
    assert formathinder(ladda_regelbas(), _dok(_avsnitt("D-ARB.6.1", None)))


def test_aktuellt_format_i_alla_tjansteavsnitt_godtas():
    assert formathinder(ladda_regelbas(), _dok(_avsnitt("D-ARB.6.1", FORMATVERSION), _avsnitt("D-ARB.2", None))) == []


def test_aldre_regelbas_utan_omfattningsmetod_berors_inte():
    v0 = ladda_regelbas(Path(__file__).resolve().parents[1] / "fixturer" / "regelbas_v0")
    assert formathinder(v0, _dok(_avsnitt("D-ARB.6.1", None))) == []
```

Lägg också till ett prov som visar att `kedjehinder` anropar spärren. Använd samma kedja som `tester/enhet/test_faststall.py` bygger (dess fixturer, till exempel `kedja`, `signerad_regelbas_rot` och `signerad_regelbas`; flytta inte fixturerna). Ersätt `riskanalys.faststallelse.faststall.formathinder` med `monkeypatch` så att den returnerar `["SPÄRR"]`, och kontrollera att `"SPÄRR"` finns i det `kedjehinder` returnerar. Om fixturerna bara finns i `test_faststall.py`, lägg provet där utan att ändra befintliga prov.

- [ ] **Steg 2: Kör och se dem fallera.** `ImportError: formathinder`.

- [ ] **Steg 3: Implementera** i `faststall.py`:

```python
def formathinder(regelbas: Regelbas, dokument: Dokument) -> list[str]:
    """Varje tjänsteavsnitt ska ha aktuellt format före ny fastställelse; äldre paket läses som förut (spec 8.4.9 punkt 9)."""
    from riskanalys.dokument.delskrivning import FORMATVERSION
    if not regelbas.metod.omfattning:
        return []
    return [f"Tjänsteavsnittet {a.id} har formatet {a.formatversion or 'utan formatmarkering'}, men aktuellt format är "
            f"{FORMATVERSION}. Skriv om utkastet och granska på nytt."
            for a in dokument.avsnitt if a.id.startswith("D-ARB.6.") and a.formatversion != FORMATVERSION]
```

Lägg `*formathinder(regelbas, las_granskning(granskningsmapp)[0])` sist i listan som `kedjehinder` returnerar. Importera `Dokument` från `riskanalys.dokument.modeller` om den saknas.

- [ ] **Steg 4: Kör.** `.venv/bin/pytest tester/enhet/test_formathinder.py tester/enhet/test_faststall.py tester/enhet/test_manifest.py tester/m2 -q` ger PASS. De befintliga proven i `test_faststall.py` och `test_manifest.py` är oförändrade.

- [ ] **Steg 5:** Ingen commit.

---

### Uppgift 8: Den äldre skrivvägen stängs för riktiga AI-anrop

**Files:**
- Modify: `src/riskanalys/dokument/skrivning.py` (`kor_skrivning`, grenen utan omfattningsmetod)
- Test: `tester/enhet/test_aldre_skrivvag.py` (ny)

**Interfaces:**
- Produces: `kor_skrivning` med en regelbas utan omfattningsmetod och en leverantör vars `namn` inte är `Testleverantor.namn` ger `LeverantorFel` innan något anrop görs.

- [ ] **Steg 1: Skriv de fallerande testerna.** Bygg en bedömning med den frysta v0-basen, som proven i `tester/typfall` gör. Använd en egen leverantörsklass med `namn = "claude"`, `modell = "prov"`, och en `skriv`-metod som registrerar anrop. Kontrollera:
- att `kor_skrivning` ger `LeverantorFel` med texten "äldre skrivvägen"
- att leverantören inte fick något anrop
- att samma körning med `Testleverantor` fortfarande fungerar

- [ ] **Steg 2: Kör och se dem fallera.**

- [ ] **Steg 3: Implementera.** I `kor_skrivning`, före loopen över tjänster:

```python
    if not regelbas.metod.omfattning and leverantor.namn != Testleverantor.namn:
        raise LeverantorFel("Den äldre skrivvägen skyddar inte AI-begäran och är stängd för riktiga AI-anrop. "
                            "Använd en regelbas med omfattningsmetod (spec 8.4.10 punkt 5).")
```

Importera `Testleverantor` från `riskanalys.dokument.leverantor`. Läsning av historiska utkast och paket (`las_skrivresultat`, fastställelse) ändras inte.

- [ ] **Steg 4: Kör.** `.venv/bin/pytest tester/enhet tester/typfall -q` ger PASS.

- [ ] **Steg 5:** Ingen commit.

---

### Uppgift 9: Helhetskontroll och status

**Files:**
- Modify: `docs/STATUS.md`

- [ ] **Steg 1: Kontroller**

- Kör `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest -q`. Förväntat: alla gröna, två livetester bortvalda.
- Kör `.venv/bin/riskanalys regelbas validera && git diff --check`. Förväntat: grönt, regelbas 1.3.0.
- Kör `START=$(grep -m1 '^START=' docs/superpowers/plans/2026-10-13-skyddad-ai-begaran.md | cut -d= -f2)` och sedan `git diff "$START" --stat -- regelbas/ tester/typfall/ tester/enhet/test_faststall.py tester/enhet/test_manifest.py tester/enhet/test_m1_gyllene_dokument.py tester/fixturer/`. Förväntat: enbart `regelbas/tillatelselistor.yaml`. `test_faststall.py` får bara ha det nya provet från uppgift 7, om det lades där.

- [ ] **Steg 2: Uppdatera `docs/STATUS.md`.** Lägg ett nytt avsnitt överst under ”Senast uppdaterad” (datum 2026-10-13), med rubriken `## Skyddad AI-begäran, 2026-10-13`. Det ska säga:
- att AI aldrig får nivåer, regelspår eller nivåmeningar
- att sårbarheter som bygger på uppgifter utanför tillåtelselistan eller smågruppsskyddade värden har utfallet ”prövas lokalt”
- att kontrollernas kategorifält är tillåtna efter beslut, att AI:s kontrollstatus bygger enbart på dem och att belagd riskreduktion avgörs lokalt
- att prov visar identisk begäran för 0, 1, 3 och 4 kunder, maskerat litet komplement, saknad bas, fält utanför tillåtelselistan, kontrollernas utfallstext och omförsök
- att andelar nära 0 och 100 % visas som ”mindre än 1 %” och ”mer än 99 %” och lagras som intervall
- att katalogkoder och kontrollsummor bara står i referenser och bilaga B1
- att fastställelse kräver aktuellt format i varje tjänsteavsnitt
- att den äldre skrivvägen är stängd för riktiga AI-anrop
- fullsvitens resultat
- under Kvar: en pilot på en tjänst med `medium` för att pröva formuleringen för faktorer under gränsen och utfallet ”prövas lokalt”, samt ett beslut om vilka fler uppgifter AI får se

- [ ] **Steg 3:** Ingen commit. Controllern stagear efter granskning, och commit sker först efter användarens godkännande.

---

## Självgranskning

- **Täckning:**
  - Läckan: uppgifterna 2, 3 och 4.
  - Granskningens punkter: 1 (uppgift 3), 2 (uppgift 5), 3 (uppgift 7), 4 (uppgift 8) och skärpta identitetsprov (uppgift 3).
  - Tredje granskningen: kontrollstatus ur kategorier (uppgift 4), verkliga fält-ID och restgruppen utan 100 av 100 (uppgift 3).
  - Katalogkoder: uppgift 6. Inga commits: varje uppgift.
- **Typkonsekvens:**
  - `begaran(rb, profil, svar=None)` definieras i uppgift 2 och används i uppgift 3.
  - `provas_lokalt(regelbas, profil, sarbarhet_id, tillatna)`, `visa_varde_klartext(falt, varde)` och `formathinder(regelbas, dokument)` används med samma signatur överallt.
- **Det som inte ändras:** motorns lokala bedömning, dokumentets nivåmeningar, regler och gränser i regelbasen, den frysta kedjan och fastställda paket.

## Genomförandelogg

START=e71e99ed154e33993974fc6f9159721df6bb59f7
