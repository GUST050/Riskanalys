# Klartext i låsta stycken – implementeringsplan

> **För agentiska utförare:** OBLIGATORISK DELFÄRDIGHET: använd superpowers:subagent-driven-development (rekommenderas) eller superpowers:executing-plans för att genomföra planen uppgift för uppgift. Stegen använder kryssrutor (`- [ ]`).

**Mål:** Programmets låsta stycken ska kunna läsas av byrån och sakgranskaren utan fält-ID, villkorsuttryck eller katalogkoder, i dokumentformatet `D-ARB-tjanst-v4`.

**Arkitektur:**
- **En ny modul, `dokument/klartext.py`.** Den äger svensk klartext för fältnamn, uppgifter, villkor och faktorer under metodens gräns. Alla som i dag bygger låsta stycken går via den: `analysunderlag.py`, `uppfoljning.py`, `intagsunderlag.py`, `nivatext.py`, `tjanstavsnitt.py` och faktabladet i `underlag.py`.
- **Kortnamn i regelbasen.** Varje fält kan få ett kortnamn (`etikett`) i regelbasen. Tjänste- och kontrollfält får namn efter tjänstens och kontrollens namn.
- **Spårbarheten finns kvar.** Varje stycke behåller sina referenser, och bilagan `D-ARB.B1` visar både kortnamn och fält-ID.
- **Gamla paket rörs inte.** Formatet höjs till v4, och fastställda paket byggs aldrig om.

**Teknik:** Python 3.12, Pydantic, pytest, YAML-regelbas.

**Spec:** `docs/superpowers/specs/2026-10-08-riskanalys-design.md`, främst 8.4.1, 8.4.6 och den nya 8.4.9 som uppgift 1 skriver.

## Bakgrund

Piloten 2026-10-12 visade låsta stycken som läsaren inte kan tolka, till exempel ”Villkoret P-GEO.andel_utland_transaktion > 0 % är uppfyllt. P-GEO.andel_utland_transaktion = 8 %.” och ”Sektorsreferens SEKTOR-REDOVISNING: hög på källans skala (…)”. Sårbarheten kunder i riskbranscher redovisades som att den inte gäller, fast 15 % av kunderna finns i riskbranscher. Metodens gräns är 20 % (`P-KUND.andel_riskbransch >= 0.2` i `regelbas/kataloger/sarbarheter.yaml`).

Granskarens preciseringar 2026-10-12, som planen genomför:
1. **Alla källor till låsta stycken ingår.** Planen täcker `nivatext.py` och `tjanstavsnitt.py`, inte bara `analysunderlag.py` och `underlag.py`.
2. **15 % riskbranscher:** texten ska säga att faktorn förekommer men ligger under metodens gräns på 20 % för automatiskt riskpåslag. Tröskeln ändras inte.
3. **Godkännanden:** övergången till v4 kräver ny sakgranskning av den ändrade texten. Tidigare fastställda paket bevaras oförändrade.

Planens andra granskning 2026-10-12, inarbetad:
1. **Gränsmeningen får inte läcka förekomst.** 0 och 3 kunder visas båda som ”färre än 5” i faktabladet. Gränsmeningen till AI byggs därför bara från den skyddade vyn: när värdet är skyddat skrivs ingen gränsmening alls (uppgift 6).
2. **Kortnamnet får inte ändra historiska attestsummor.** Saknat kortnamn utelämnas vid serialisering och testas mot frysta summor (uppgift 3).
3. **Slutkontrollen jämför mot planens start-SHA, inte `main`** (”Före uppgift 1” och uppgift 7).
4. **Återanvändning av v3-utkast är utredd** i avsnittet ”Återanvändning av v3-utkast” före självgranskningen.

## Global Constraints

- AGENTS.md regel 1: ”AI fattar inga beslut.” Motorns utfall (`galler`), nivåer och poäng ändras inte; bara texten.
- AGENTS.md regel 2: ”Inga personuppgifter till AI.” Tillåtelselistan och smågruppsskyddet (`SMA_GRUPPER_GRANS = 5`) gäller oförändrat för allt som når faktabladet.
- AGENTS.md regel 4: ”Regelbasen ändras bara med källa.” Kortnamnet `etikett` är visningstext och ändrar ingen regel, gräns eller källa. Gränsvärden i `sarbarheter.yaml` får inte ändras.
- AGENTS.md regel 6: ”Tester före commit … Skriv testet först.”
- AGENTS.md regel 7: inga anrop mot riktiga API:t i automatiska tester.
- AGENTS.md regel 8: ändra aldrig sakkunnigstatus i repots regelbas till `verifierad`.
- Stil: ”Användartexter och dokumentation på svenska. Identifierare i koden på svenska utan å, ä och ö.” ”Funktioner returnerar nya objekt i stället för att ändra befintliga.”
- Den frysta M1-kedjan (`not regelbas.utokade_krav`, testerna i `tester/typfall/`) ska ge byte för byte samma text som före ändringen.
- Fastställda paket under `FASTSTALLDA` byggs aldrig om. `tester/enhet/test_faststall.py` och `tester/enhet/test_manifest.py` ska passera utan ändringar.
- B-09 bygger på att `[VERIFIERA]` står i det låsta geografistycket när underlag saknas. Markeringen ska finnas kvar i klartexten.

## Review Focus

1. **Skyddat smågruppsvärde i gränsmeningen till AI.** Gränsmeningen byggs bara från den skyddade vyn. 0 och 3 kunder ger samma faktabladstext, och ett litet komplement ger ingen gränsmening. Tester i uppgift 6.
2. **Fält utanför tillåtelselistan.** Ingen gränsmening om fältet får nå AI. Test i uppgift 6.
3. **Okänt, föreslaget eller noll-värde.** Ingen gränsmening, och `[VERIFIERA]` står kvar när underlag saknas. Tester i uppgift 3 och uppgift 4.
4. **Förkortningar mitt i en mening** (PEP, EU-högrisktredjeland) behåller versalerna. Test i uppgift 3.
5. **Historiskt v3-dokument och gammal sakgranskning.** Ett v3-dokument kan fortfarande läsas, men en sakgranskning av v3-text gäller inte v4-texten. Tester i uppgift 2.

Medvetet utanför planen: om AI ändå skriver att en sårbarhet under gränsen ”inte gäller” kan maskinen inte avgöra det säkert ur fri text. Faktabladet och prompten styr mot rätt formulering, och nästa pilot kontrollerar det.

## Filer

| Fil | Ansvar | Uppgift |
|---|---|---|
| `docs/superpowers/specs/2026-10-08-riskanalys-design.md` | Ny 8.4.9, revision 18 | 1 |
| `src/riskanalys/dokument/delskrivning.py`, `dokument/modeller.py`, `dokument/tjanstavsnitt.py` | Format v4 | 2 |
| `src/riskanalys/regelverk/modeller.py`, `regelbas/falt.yaml`, `regelbas/version.yaml` | Kortnamn | 3 |
| `src/riskanalys/dokument/klartext.py` (ny) | Klartext för fält, uppgifter och villkor | 3 |
| `src/riskanalys/dokument/analysunderlag.py`, `uppfoljning.py`, `intagsunderlag.py` | Låsta stycken och bilaga B1 | 4 |
| `src/riskanalys/dokument/nivatext.py`, `tjanstavsnitt.py` | Sektorsreferens och tjänstebeskrivning | 5 |
| `src/riskanalys/dokument/underlag.py`, `faktablad.py`, `promptar/delar.py` | Faktabladet och prompten | 6 |
| `docs/STATUS.md` | Status | 7 |

---

### Före uppgift 1: Spara start-SHA

- [ ] Kör `git rev-parse HEAD` innan något ändras och skriv resultatet på raden `START=` under rubriken ”Genomförandelogg” sist i denna plan, till exempel `START=13cf075…`. Uppgift 1 committar planen med raden. Slutkontrollen i uppgift 7 jämför mot detta SHA, inte mot `main`, eftersom `main` saknar grenens tidigare katalog- och teständringar.

---

### Uppgift 1: Spec revision 18

**Files:**
- Modify: `docs/superpowers/specs/2026-10-08-riskanalys-design.md`

**Interfaces:** inga.

- [ ] **Steg 1: Ändra statusraden (rad 3)**

Ersätt `revision 17 (2026-10-11)` med `revision 18 (2026-10-12)`.

- [ ] **Steg 2: Lägg in 8.4.9 direkt före rubriken `## 9 Granskning (maskinell)`**

```markdown
#### 8.4.9 Klartext i låsta stycken (format `D-ARB-tjanst-v4`)

Låsta stycken skrivs för läsaren, inte för programmet:

1. Löptexten innehåller inga fält-ID, villkorsuttryck eller katalogkoder. En uppgift skrivs med fältets kortnamn, värde, period, källa och datum. Kortnamnet (`etikett`) är visningstext i regelbasen och ändrar ingen regel. Tjänste- och kontrollfält får namn efter tjänstens och kontrollens namn.
2. Villkor skrivs i ord, till exempel ”Sårbarheten gäller om andel kunder i riskbranscher är minst 20 %”.
3. När en jämförelse med en gräns inte är uppfylld men det bekräftade värdet är större än noll, skriver programmet att faktorn förekommer men ligger under metodens gräns för automatiskt riskpåslag. Motorns utfall och gränsen ändras inte. I faktabladet gäller tillåtelselistan och smågruppsskyddet. När värdet är skyddat eller inte får nå AI skriver faktabladet ingen gränsmening, så att texten blir densamma oavsett det skyddade värdet.
4. Sektorsreferensen anges med källans titel, nivå, skala och sida.
5. Spårbarheten finns kvar. Varje stycke behåller sina referenser, och bilagan `D-ARB.B1` anger kortnamn och fält-ID för varje uppgift.
6. Övergången till v4 ändrar texten i låsta stycken och upphäver därför tidigare sakgodkännanden enligt 8.4.6 punkt 5. Utkast i v3 skrivs om. Fastställda paket byggs aldrig om och förblir oförändrade.
```

- [ ] **Steg 3: Lägg till rad 18 i revisionsloggen, direkt efter rad 17**

```markdown
| 18 | 2026-10-12 | Efter pilot på tre tjänster: låsta stycken i klartext med kortnamn i regelbasen, villkor i ord, faktorer under metodens gräns beskrivs som förekommande, sektorsreferens med källans titel och spårbarhet via referenser och bilaga B1. Format `D-ARB-tjanst-v4` med ny sakgranskning; fastställda paket oförändrade (8.4.9). Inga ändrade regler, gränser eller nivåer. |
```

- [ ] **Steg 4: Commit**

```bash
git add docs/superpowers/specs/2026-10-08-riskanalys-design.md docs/superpowers/plans/2026-10-12-klartext-i-lasta-stycken.md
git commit -m "docs: spec revision 18, klartext i låsta stycken"
```

---

### Uppgift 2: Dokumentformat v4

**Files:**
- Modify: `src/riskanalys/dokument/delskrivning.py:20,57`
- Modify: `src/riskanalys/dokument/modeller.py:110,136-140`
- Modify: `src/riskanalys/dokument/tjanstavsnitt.py:113`
- Test: `tester/intag/test_format_v4.py` (ny), `tester/enhet/test_sakgranskning.py`, `tester/intag/test_v3_grind.py:63-68`, `tester/intag/test_kedja.py:75,87`

**Interfaces:**
- Produces: `delskrivning.FORMATVERSION == "D-ARB-tjanst-v4"`. `Tjanstresultat.formatversion` och `Avsnitt.formatversion` godtar både `"D-ARB-tjanst-v3"` och `"D-ARB-tjanst-v4"`. `Dokument.formatversion` returnerar v4 före v3.

- [ ] **Steg 1: Skriv de fallerande testerna**

`tester/intag/test_format_v4.py`:

```python
import pytest

from riskanalys.dokument.delskrivning import FORMATVERSION, kontrollera_resultat, skriv_tjanst
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.modeller import Avsnitt, Dokument, Textstycke
from riskanalys.dokument.promptar import DELAR
from riskanalys.fel import RiskanalysFel

from tester.fixturer.m2 import godkant_delsvar, tjanst_for_prov


def _avsnitt(version):
    return Avsnitt(id="D-ARB.6.1", rubrik="Analys", kalla="ai",
                   stycken=(Textstycke(typ="beskrivning", text="Text.", referenser=["T-RED-01"]),),
                   formatversion=version)


def test_aktuellt_format_ar_v4():
    assert FORMATVERSION == "D-ARB-tjanst-v4"


def test_dokument_i_v3_kan_fortfarande_lasas():
    gammalt = Dokument(id="D", titel="T", avsnitt=(_avsnitt("D-ARB-tjanst-v3"),))
    assert Dokument.model_validate_json(gammalt.model_dump_json()).formatversion == "D-ARB-tjanst-v3"
    assert Dokument(id="D", titel="T", avsnitt=(_avsnitt("D-ARB-tjanst-v4"),)).formatversion == "D-ARB-tjanst-v4"


def test_ny_formatversion_ger_ny_kontrollsumma():
    assert _avsnitt("D-ARB-tjanst-v3").kontrollsumma() != _avsnitt("D-ARB-tjanst-v4").kontrollsumma()


def test_utkast_i_v3_maste_skrivas_om(tmp_path, rb_intag, klar):
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    lev = Testleverantor([godkant_delsvar(d, t) for d in DELAR])
    res = skriv_tjanst(lev, rb_intag, klar, t, avsnitt_id, effort="medium", personnamn=(), spara=lambda d, f: None)
    gammal = type(res).model_validate_json(res.model_copy(update={"formatversion": "D-ARB-tjanst-v3"}).model_dump_json())
    with pytest.raises(RiskanalysFel, match="Skriv om"):
        kontrollera_resultat(rb_intag, klar, t, gammal, avsnitt_id)
```

I `tester/enhet/test_sakgranskning.py`, lägg till efter `test_v2_godkannande_galler_inte_ny_formatversion`:

```python
def test_v3_godkannande_galler_inte_v4(profil):
    a = _dokument().avsnitt[0].model_copy(update={"formatversion": "D-ARB-tjanst-v3"})
    doc = _dokument().model_copy(update={"avsnitt": (a,)})
    poster = registrera_sakgranskning((), doc, profil, a.id, True, "FfR", "Testa Testsson", DAG)
    assert galler_sakgranskning(poster, a, profil) is not None
    assert galler_sakgranskning(poster, a.model_copy(update={"formatversion": "D-ARB-tjanst-v4"}), profil) is None
```

- [ ] **Steg 2: Kör testerna och se dem fallera**

Kör: `.venv/bin/pytest tester/intag/test_format_v4.py tester/enhet/test_sakgranskning.py -q`
Förväntat: FAIL. `FORMATVERSION` är v3, och `Avsnitt` godtar inte `"D-ARB-tjanst-v4"` (ValidationError).

- [ ] **Steg 3: Implementera**

`delskrivning.py` rad 20 och 57:

```python
FORMATVERSION = "D-ARB-tjanst-v4"
```
```python
    formatversion: Literal["D-ARB-tjanst-v3", "D-ARB-tjanst-v4"] = FORMATVERSION
```

`modeller.py` rad 110:

```python
    formatversion: Literal["D-ARB-tjanst-v3", "D-ARB-tjanst-v4"] | None = None
```

`modeller.py`, egenskapen `Dokument.formatversion`:

```python
    @property
    def formatversion(self) -> str:
        for version in ("D-ARB-tjanst-v4", "D-ARB-tjanst-v3"):
            if any(a.formatversion == version for a in self.avsnitt):
                return version
        return "D-ARB-tjanst-v2" if any(a.underrubriker for a in self.avsnitt) else "D-ARB-v1"
```

`tjanstavsnitt.py`, i `bygg_tjanstavsnitt_v3`: importera `FORMATVERSION` på samma rad som `ANSVARSMENING` (`from riskanalys.dokument.delskrivning import ANSVARSMENING, FORMATVERSION`) och ersätt `formatversion="D-ARB-tjanst-v3"` på rad 113 med `formatversion=FORMATVERSION`. Funktionsnamnet behålls för att diffen ska bli liten.

- [ ] **Steg 4: Uppdatera tester som kontrollerar det aktuella formatet**

- `tester/intag/test_v3_grind.py:63-68`: byt namn till `test_aktuellt_format_sparas_och_skild_fran_v2`. Ersätt båda `"D-ARB-tjanst-v3"` med `FORMATVERSION` och importera den från `riskanalys.dokument.delskrivning`.
- `tester/intag/test_kedja.py:75` och `:87`: ersätt `'D-ARB-tjanst-v3'` med `FORMATVERSION`, importerad på samma sätt.
- `tester/enhet/test_sakgranskning.py:94` testar att ett historiskt format upphäver ett v2-godkännande. Lämna raden orörd.

- [ ] **Steg 5: Kör de berörda testerna**

Kör: `.venv/bin/pytest tester/intag tester/enhet/test_sakgranskning.py tester/enhet/test_faststall.py tester/enhet/test_manifest.py -q`
Förväntat: PASS. `test_faststall.py` och `test_manifest.py` ska passera utan att ändras.

- [ ] **Steg 6: Commit**

```bash
git add src/riskanalys/dokument/delskrivning.py src/riskanalys/dokument/modeller.py src/riskanalys/dokument/tjanstavsnitt.py tester/intag/test_format_v4.py tester/enhet/test_sakgranskning.py tester/intag/test_v3_grind.py tester/intag/test_kedja.py
git commit -m "feat: dokumentformat D-ARB-tjanst-v4"
```

---

### Uppgift 3: Kortnamn och modulen klartext

**Files:**
- Modify: `src/riskanalys/regelverk/modeller.py:39-55` (klassen `Falt`)
- Modify: `regelbas/falt.yaml` (43 fält), `regelbas/version.yaml`
- Create: `src/riskanalys/dokument/klartext.py`
- Test: `tester/intag/test_klartext.py` (ny), `tester/regelkontrakt/test_etiketter.py` (ny)

**Interfaces:**
- Produces, i `riskanalys.dokument.klartext`:
  - `VERIFIERA: str` med värdet `"[VERIFIERA]"`
  - `gemen(text: str) -> str`
  - `faltnamn(regelbas: Regelbas, falt_id: str) -> str`
  - `har_eget_namn(regelbas: Regelbas, falt_id: str) -> bool`
  - `uppgiftstext(regelbas, profil, falt_id, *, namn: str | None = None, med_id: bool = False) -> str`
  - `villkorstext(data: dict, regelbas: Regelbas) -> str`
  - `UnderGrans`, en frusen dataklass med fälten `falt_id: str` och `grans: float`
  - `under_grans(profil: Profil, data: dict) -> tuple[UnderGrans, ...]`
  - `gransmening(regelbas, profil, g: UnderGrans) -> str`
- Produces, i regelbasen: `Falt.etikett: str | None`. Den utelämnas vid serialisering när den saknas, så att `kravets_innehallssumma`, `paketets_innehallssumma` och kundmodellens `c_innehallssumma` blir oförändrade för regelbaser utan kortnamn.

- [ ] **Steg 1: Skriv de fallerande testerna**

`tester/intag/test_klartext.py`:

```python
from datetime import date

import pytest

from riskanalys.dokument.klartext import faltnamn, gemen, gransmening, under_grans, uppgiftstext, villkorstext
from riskanalys.profil.modeller import Byra, Period, Profil, Uppgift

PER = Period(fran=date(2025, 1, 1), till=date(2025, 12, 31))


def _u(varde, status="bekräftad"):
    return Uppgift(varde=varde, period=PER, status=status, kalla="Syntetisk statistik",
                   datum=date(2026, 10, 10), bekraftad_av="roll:FfR")


def _profil(uppgifter):
    return Profil(byra=Byra(id="syntetisk", regelpaket="RP-RED-VG", datum=date(2026, 10, 10), lan="Västra Götaland"),
                  uppgifter=uppgifter)


GRANS = {"falt": "P-KUND.andel_riskbransch", "op": ">=", "varde": 0.2}


def test_faltnamn_anvander_etikett_och_monster(rb_intag):
    assert faltnamn(rb_intag, "P-KUND.andel_riskbransch") == "Andel kunder i riskbranscher"
    assert faltnamn(rb_intag, "P-TJ.red01_antal_kunder") == "Antal kunder i löpande bokföring"
    assert faltnamn(rb_intag, "P-KONTROLL.C-07.effekt") == "Dokumenterad verkan av kontrollen bankavstämning mot underlag"


def test_gemen_behaller_forkortningar():
    assert gemen("Andel kunder i riskbranscher") == "andel kunder i riskbranscher"
    assert gemen("PEP, familjemedlem eller känd medarbetare") == "PEP, familjemedlem eller känd medarbetare"
    assert gemen("EU-högrisktredjeland") == "EU-högrisktredjeland"


@pytest.mark.parametrize("villkor,text", [
    (GRANS, "andel kunder i riskbranscher är minst 20 %"),
    ({"falt": "P-GEO.andel_utland_transaktion", "op": ">", "varde": 0},
     "andel kunder med transaktioner utanför Sverige är större än 0 %"),
    ({"falt": "P-KANAL.bankdata_andel", "op": "<", "varde": 0.5},
     "andel kunder där byrån har tillgång till bankdata är mindre än 50 %"),
    ({"falt": "P-RISK.korruption", "op": "==", "varde": True},
     "anknytning till land eller område med korruption förekommer"),
    ({"alla": [GRANS, {"falt": "P-KANAL.bankdata_andel", "op": "<", "varde": 0.5}]},
     "andel kunder i riskbranscher är minst 20 % och andel kunder där byrån har tillgång till bankdata är mindre än 50 %"),
])
def test_villkor_skrivs_i_ord(rb_intag, villkor, text):
    assert villkorstext(villkor, rb_intag) == text


def test_faktor_under_gransen_beskrivs_som_forekommande(rb_intag):
    p = _profil({"P-KUND.andel_riskbransch": _u(0.15)})
    (g,) = under_grans(p, GRANS)
    assert gransmening(rb_intag, p, g) == (
        "Faktorn förekommer: andel kunder i riskbranscher är 15 %, men det ligger under metodens gräns "
        "på 20 % för automatiskt riskpåslag.")


@pytest.mark.parametrize("uppgift", [None, _u(0), _u(0.25), _u(0.15, status="föreslagen")])
def test_ingen_gransmening_utan_bekraftad_forekomst_under_gransen(uppgift):
    p = _profil({"P-KUND.andel_riskbransch": uppgift} if uppgift else {})
    assert under_grans(p, GRANS) == ()


def test_uppgiftstext_utan_falt_id_och_med_id_i_bilagan(rb_intag):
    p = _profil({"P-KUND.andel_riskbransch": _u(0.15)})
    assert uppgiftstext(rb_intag, p, "P-KUND.andel_riskbransch") == (
        "Andel kunder i riskbranscher: 15 % (period 2025-01-01–2025-12-31; källa: Syntetisk statistik; "
        "bekräftad 2026-10-10).")
    assert uppgiftstext(rb_intag, p, "P-KUND.andel_riskbransch", med_id=True).startswith(
        "Andel kunder i riskbranscher (P-KUND.andel_riskbransch): 15 %")


def test_saknat_underlag_behaller_verifiera(rb_intag):
    assert uppgiftstext(rb_intag, _profil({}), "P-KUND.andel_riskbransch") == (
        "Andel kunder i riskbranscher: aktuellt bekräftat underlag saknas. [VERIFIERA]")
```

`tester/regelkontrakt/test_etiketter.py`:

```python
import re

from riskanalys.bedomning.erfarenheter import ERFARENHETSFALT
from riskanalys.dokument.klartext import har_eget_namn
from riskanalys.regelverk.laddning import ladda_regelbas
from riskanalys.regelverk.villkor import falt_i, tolka_villkor

UPPFOLJNING = ("P-BEVAKNING.kallor", "P-BEVAKNING.datum", "P-BEVAKNING.ansvarig", "P-BEVAKNING.relevans",
               "P-OMFATTNING.motivering", "P-ORG.antal_anstallda", "P-ORG.verksamhetsstallen", "P-VERK.goaml",
               "P-VERK.omsattning", "P-VERK.spridning", "P-VERK.tidigare_tillsyn")
TJANSTSUFFIX = ("_erbjuds", "_antal_kunder", "_andel_kunder", "_andel_omsattning", "_arbetssatt", "_geografi",
                "_ovriga_risker")


def _falt_i_lasta_stycken(rb):
    d = rb.faltdefinitioner()
    ids = {f for s in rb.sarbarheter.values() for f in falt_i(tolka_villkor(s.villkor, d))}
    ids |= set(ERFARENHETSFALT) | {"P-BESK.geografi", "P-BESK.erfarenheter"} | set(UPPFOLJNING)
    ids |= {f for k in rb.kontroller.values() for f in (k.effekt_falt, k.utfall_falt) if f}
    for t in rb.tjanster.values():
        slug = t.erbjuds_falt.removesuffix("_erbjuds")
        ids |= {slug + s for s in TJANSTSUFFIX}
    return sorted(i for i in ids if i in rb.falt)


def test_varje_falt_i_lasta_stycken_har_ett_eget_namn():
    rb = ladda_regelbas()
    assert [i for i in _falt_i_lasta_stycken(rb) if not har_eget_namn(rb, i)] == []


def test_etiketter_ar_korta_och_utan_falt_id():
    rb = ladda_regelbas()
    for f in rb.falt.values():
        if f.etikett:
            assert len(f.etikett) <= 80 and not re.search(r"\b[PSHCT]-[A-Z]", f.etikett), f.id


# Summor räknade på oförändrade regelbaser före kortnamnen (2026-10-12). En sakkunnigattest gäller exakt dessa.
V0 = Path(__file__).resolve().parents[1] / "fixturer" / "regelbas_v0"
V0_PAKET = "sha256:55d2dc582f5e7fa6cb31a9c7976e335a766d7ce153607efb613a8e2e40a784ef"
KRV_PTL_2_9 = "sha256:590224c27d2076d8d9c7680af66535110c621238cf9a35e36ad879434663fb0e"


def test_saknat_kortnamn_andrar_inte_historiska_attestsummor():
    assert ladda_regelbas(V0).paketets_innehallssumma("RP-RED-VG") == V0_PAKET


def test_kravattest_bestar_nar_kravets_falt_saknar_kortnamn():
    rb = ladda_regelbas()
    assert rb.kravets_innehallssumma("KRV-PTL-2-9") == KRV_PTL_2_9


def test_saknat_kortnamn_serialiseras_inte():
    f = Falt(id="P-X", typ="bool", fraga="Fråga?", varfor="Test")
    assert "etikett" not in f.model_dump(mode="json")
    assert Falt(id="P-X", typ="bool", fraga="Fråga?", varfor="Test", etikett="Namn").model_dump()["etikett"] == "Namn"
```

Lägg till `from pathlib import Path` och `from riskanalys.regelverk.modeller import Falt` bland importerna i filen. `KRV-PTL-2-9` villkoras inte av något fält som får kortnamn, så summan ska bestå även i 1.3.0. Paketsummorna för 1.3.0 ändras däremot, eftersom kortnamnen är nytt innehåll i regelbasen. Ingen verklig attest finns, och testerna signerar kopior med summor de räknar själva.

- [ ] **Steg 2: Kör testerna och se dem fallera**

Kör: `.venv/bin/pytest tester/intag/test_klartext.py tester/regelkontrakt/test_etiketter.py -q`
Förväntat: FAIL med `ModuleNotFoundError: riskanalys.dokument.klartext`.

- [ ] **Steg 3: Lägg till `etikett` i `Falt`, först utan serialiserare**

I `regelverk/modeller.py`, klassen `Falt`, efter `enhet: str | None = None`:

```python
    etikett: str | None = None  # Kortnamn i löptext; visningstext som inte ändrar någon regel (spec 8.4.9).
```

Kör: `.venv/bin/pytest tester/regelkontrakt/test_etiketter.py -q -k "attest or serialiseras"`
Förväntat: FAIL. Summorna ändras, eftersom `"etikett": null` kommer med i serialiseringen. Det är felet som granskningen reproducerade.

Lägg sedan till serialiseraren i samma klass och importera `model_serializer` från `pydantic` på rad 7:

```python
    @model_serializer(mode="wrap")
    def serialisera(self, handler):
        """Utelämna saknat kortnamn, så att historiska innehålls- och attestsummor består."""
        data = handler(self)
        if self.etikett is None:
            data.pop("etikett", None)
        return data
```

Kör samma kommando igen. Förväntat: PASS.

- [ ] **Steg 4: Skriv kortnamnen i `regelbas/falt.yaml`**

Lägg till raden `etikett: <text>` direkt efter `fraga:` för exakt dessa 43 fält. Ändra inget annat i posterna.

| Fält | etikett |
|---|---|
| P-BESK.erfarenheter | Byråns egna erfarenheter av misstankar och avböjda uppdrag |
| P-BESK.geografi | Kundernas, ägarnas och betalningsflödenas geografi |
| P-GEO.andel_agare_utanfor_ees | Andel kunder med ägare utanför EES |
| P-GEO.andel_hogrisktredjeland | Andel kunder etablerade i EU-högrisktredjeland |
| P-GEO.andel_utland_transaktion | Andel kunder med transaktioner utanför Sverige |
| P-GEO.andel_utsatt_omrade | Andel kunder med anknytning till utsatt område |
| P-KANAL.andel_digitalt_underlag | Andel kunder som lämnar digitalt underlag |
| P-KANAL.bankdata_andel | Andel kunder där byrån har tillgång till bankdata |
| P-KUND.andel_kontant | Andel kunder med betydande kontanthantering |
| P-KUND.andel_riskbransch | Andel kunder i riskbranscher |
| P-KUND.andel_utan_mote | Andel kunder antagna utan fysiskt möte |
| P-RISK.ensam_roller | En person utför uppdrag, kontroll och alla ansvarsfunktioner |
| P-RISK.extern_kyc | Extern leverantör för kundkännedom eller penningtvättsarbete |
| P-RISK.hogrisktredjeland | Anknytning till EU-högrisktredjeland |
| P-RISK.ideell | Ideella föreningar eller liknande organisationer bland kunderna |
| P-RISK.komplex_agare | Komplex eller svårförklarad ägarstruktur |
| P-RISK.korruption | Anknytning till land eller område med korruption |
| P-RISK.kortlivad | Företrädare med återkommande kortlivade bolag |
| P-RISK.kundberoende | Ekonomiskt beroende av en eller få kunder |
| P-RISK.nara_relation | Nära kundrelation som kan försvaga granskningen |
| P-RISK.ombud | Ombud eller tredje part i kundkontakt eller leverans |
| P-RISK.overtagen | Övertagna bolag eller täta byten av företrädare |
| P-RISK.pep | PEP, familjemedlem eller känd medarbetare bland kunder eller huvudmän |
| P-RISK.svagt_aml | Anknytning till land med svagt regelverk mot penningtvätt |
| P-RISK.utan_mote | Kundrelation etablerad utan fysiskt möte |
| P-RISK.utan_utbildning | Personal eller uppdragstagare utan aktuell utbildning |
| P-RISK.utkontraktering | Utkontrakterade delar av uppdrag eller penningtvättsarbete |
| P-RISK.utlandsk_agare | Utländsk ägarstruktur som kräver ytterligare verifiering |
| P-RISK.utsatt_omrade | Anknytning till utsatt område i Sverige |
| P-VERK.antal_avbojanden | Antal avböjda kundrelationer eller transaktioner på grund av misstanke |
| P-VERK.antal_rapporter | Antal egna misstankerapporter |
| P-VERK.juniora_konsulter | Konsulter med mindre än två års erfarenhet arbetar självständigt |
| P-BEVAKNING.kallor | Källor som byrån har läst i omvärldsbevakningen |
| P-BEVAKNING.datum | Datum då byrån läste och utvärderade källorna |
| P-BEVAKNING.ansvarig | Ansvarsfunktion för omvärldsbevakningen |
| P-BEVAKNING.relevans | Hur lästa källor påverkar tjänsternas risker |
| P-OMFATTNING.motivering | Motivering av vald analysomfattning |
| P-ORG.antal_anstallda | Antal personer som arbetar på byrån |
| P-ORG.verksamhetsstallen | Antal orter eller kontor |
| P-VERK.goaml | Registrering och rapporteringsförmåga i goAML |
| P-VERK.omsattning | Byråns omsättning |
| P-VERK.spridning | Spridning av riskbedömningen inom byrån |
| P-VERK.tidigare_tillsyn | Tidigare tillsyn och uppföljning av brister |

I `regelbas/version.yaml`: `regelbas_version: 1.2.0` blir `regelbas_version: 1.3.0`. Sakkunnigstatusen ändras inte.

- [ ] **Steg 5: Skriv `src/riskanalys/dokument/klartext.py`**

```python
"""Svensk klartext för låsta stycken: fältnamn, uppgifter och villkor utan fält-ID (spec 8.4.9)."""

from dataclasses import dataclass

from riskanalys.bedomning.erfarenheter import belagd_uppgift
from riskanalys.profil.hantering import visa_varde
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas

VERIFIERA = "[VERIFIERA]"

_TJANSTFALT = {
    "_erbjuds": "{namn} erbjuds",
    "_antal_kunder": "Antal kunder i {liten}",
    "_andel_kunder": "Andel av byråns kunder i {liten}",
    "_omsattning": "Omsättning från {liten}",
    "_andel_omsattning": "Andel av omsättningen från {liten}",
    "_arbetssatt": "Uppdrag och arbetssätt i {liten}",
    "_geografi": "Geografi i {liten}",
    "_ovriga_risker": "Övriga riskförhållanden i {liten}",
}
_KONTROLLFALT = {
    "effekt": "Dokumenterad verkan av kontrollen {liten}",
    "utfall": "Prov och utfall för kontrollen {liten}",
}
_JAMFORELSE = {">=": "är minst", ">": "är större än", "<": "är mindre än", "<=": "är högst", "==": "är", "!=": "inte är"}


@dataclass(frozen=True)
class UnderGrans:
    """En jämförelse mot en gräns som inte är uppfylld fast faktorn förekommer."""

    falt_id: str
    grans: float


def gemen(text: str) -> str:
    """Liten begynnelsebokstav mitt i en mening, men inte i förkortningar som PEP och EU."""
    if len(text) > 1 and text[1].isupper():
        return text
    return text[:1].lower() + text[1:]


def _monsternamn(regelbas: Regelbas, falt_id: str) -> str | None:
    for tjanst in regelbas.tjanster.values():
        slug = tjanst.erbjuds_falt.removesuffix("_erbjuds")
        mall = _TJANSTFALT.get(falt_id[len(slug):]) if falt_id.startswith(slug + "_") else None
        if mall:
            return mall.format(namn=tjanst.namn, liten=gemen(tjanst.namn))
    delar = falt_id.split(".")
    if len(delar) == 3 and delar[0] == "P-KONTROLL" and delar[1] in regelbas.kontroller and delar[2] in _KONTROLLFALT:
        return _KONTROLLFALT[delar[2]].format(liten=gemen(regelbas.kontroller[delar[1]].namn))
    return None


def har_eget_namn(regelbas: Regelbas, falt_id: str) -> bool:
    return bool(regelbas.falt[falt_id].etikett or _monsternamn(regelbas, falt_id))


def faltnamn(regelbas: Regelbas, falt_id: str) -> str:
    """Kortnamnet, annars ett namn efter tjänst eller kontroll, annars frågan utan frågetecken."""
    falt = regelbas.falt[falt_id]
    return falt.etikett or _monsternamn(regelbas, falt_id) or falt.fraga.removesuffix(" (beräknad andel)").rstrip("?")


def uppgiftstext(regelbas: Regelbas, profil: Profil, falt_id: str, *, namn: str | None = None,
                 med_id: bool = False) -> str:
    """'Kortnamn: värde (period …; källa: …; bekräftad …).' Fält-ID visas bara i bilagan (med_id)."""
    rubrik = namn or faltnamn(regelbas, falt_id)
    if med_id:
        rubrik = f"{rubrik} ({falt_id})"
    if not belagd_uppgift(regelbas, profil, falt_id):
        return f"{rubrik}: aktuellt bekräftat underlag saknas. {VERIFIERA}"
    u = profil.uppgifter[falt_id]
    delar = [f"period {u.period.fran}–{u.period.till}"] if u.period else []
    delar += [f"källa: {u.kalla}", f"bekräftad {u.datum}"]
    varde = str(visa_varde(regelbas.falt[falt_id], u.varde)).rstrip(".")
    return f"{rubrik}: {varde} ({'; '.join(delar)})."


def _jamforelsetext(data: dict, regelbas: Regelbas) -> str:
    falt = regelbas.falt[data["falt"]]
    namn = gemen(faltnamn(regelbas, falt.id))
    op = data["op"]
    if op == "finns":
        return f"{namn} är angiven"
    if op == "saknas":
        return f"{namn} saknas"
    if falt.typ == "bool" and op in ("==", "!="):
        forekommer = (data["varde"] in (True, "ja")) == (op == "==")
        return f"{namn} förekommer" if forekommer else f"{namn} inte förekommer"
    if op == "i":
        return f"{namn} är något av {', '.join(str(visa_varde(falt, v)) for v in data['varde'])}"
    return f"{namn} {_JAMFORELSE[op]} {visa_varde(falt, data['varde'])}"


def villkorstext(data: dict, regelbas: Regelbas) -> str:
    """Villkoret i ord, till exempel 'andel kunder i riskbranscher är minst 20 %'."""
    if "falt" in data:
        return _jamforelsetext(data, regelbas)
    if "inte" in data:
        return f"det inte gäller att {villkorstext(data['inte'], regelbas)}"
    nyckel, bindeord = ("alla", " och ") if "alla" in data else ("nagon", " eller ")
    return bindeord.join(villkorstext(d, regelbas) if "falt" in d else f"({villkorstext(d, regelbas)})"
                         for d in data[nyckel])


def under_grans(profil: Profil, data: dict) -> tuple[UnderGrans, ...]:
    """Jämförelser 'minst' eller 'större än' där ett bekräftat värde över noll inte når gränsen."""
    if "falt" in data:
        u = profil.uppgifter.get(data["falt"])
        if (data["op"] not in (">=", ">") or u is None or u.status != "bekräftad" or u.inaktuell
                or type(u.varde) not in (int, float)):
            return ()
        uppfyllt = u.varde >= data["varde"] if data["op"] == ">=" else u.varde > data["varde"]
        return (UnderGrans(data["falt"], data["varde"]),) if 0 < u.varde and not uppfyllt else ()
    if "inte" in data:
        return ()
    return tuple(g for d in data.get("alla", data.get("nagon", [])) for g in under_grans(profil, d))


def gransmening(regelbas: Regelbas, profil: Profil, g: UnderGrans) -> str:
    falt = regelbas.falt[g.falt_id]
    return (f"Faktorn förekommer: {gemen(faltnamn(regelbas, g.falt_id))} är "
            f"{visa_varde(falt, profil.uppgifter[g.falt_id].varde)}, men det ligger under metodens gräns på "
            f"{visa_varde(falt, g.grans)} för automatiskt riskpåslag.")
```

- [ ] **Steg 6: Kör testerna**

Kör: `.venv/bin/pytest tester/intag/test_klartext.py tester/regelkontrakt/test_etiketter.py -q && .venv/bin/riskanalys regelbas validera`
Förväntat: PASS. Valideringen är grön, med ny kontrollsumma och `ej_granskad` som förut. Om ett annat regelkontrakttest fallerar för att det kräver ett visst versionsnummer, uppdatera det till 1.3.0 och ange det i commitmeddelandet.

- [ ] **Steg 7: Commit**

```bash
git add src/riskanalys/regelverk/modeller.py regelbas/falt.yaml regelbas/version.yaml src/riskanalys/dokument/klartext.py tester/intag/test_klartext.py tester/regelkontrakt/test_etiketter.py
git commit -m "feat: kortnamn för fält och modulen klartext (regelbas 1.3.0)"
```

---

### Uppgift 4: Låsta stycken i analysunderlag, uppföljning och bilaga B1

**Files:**
- Modify: `src/riskanalys/dokument/analysunderlag.py` (`_belagg`, `erfarenhetsstycke`, `_villkorstext`, `sarbarhetsstycke`)
- Modify: `src/riskanalys/dokument/intagsunderlag.py:41-57` (`bygg_underlagsbilaga`)
- Test: `tester/intag/test_lasta_stycken.py` (ny), `tester/regelkontrakt/test_arb_erfarenhet_motivering.py:104`, `tester/regelkontrakt/test_arb_utvidgning.py:58`

**Interfaces:**
- Consumes: `uppgiftstext`, `villkorstext`, `under_grans`, `gransmening` och `VERIFIERA` från uppgift 3.
- Produces: `_belagg(regelbas, profil, id)` behåller signaturen men returnerar `uppgiftstext(...)`, så `tjanstavsnitt.py` och `uppfoljning.py` får klartext utan egna ändringar. `analysunderlag.VERIFIERA` finns kvar, importerad från `klartext`.

- [ ] **Steg 1: Skriv de fallerande testerna**

`tester/intag/test_lasta_stycken.py`:

```python
from riskanalys.dokument.analysunderlag import sarbarhetsstycke
from riskanalys.dokument.intagsunderlag import bygg_underlagsbilaga
from riskanalys.dokument.platshallare import faltid_fel
from riskanalys.profil.omfattning import harled_andelar


def _id_for(rb, falt_id):
    return next(s.id for s in rb.sarbarheter.values() if s.villkor.get("falt") == falt_id)


def _med_riskbransch(rb, klar, antal):
    """Testprofilen har 100 aktiva kunder; andelen härleds ur antalet, som i intaget."""
    u = klar.uppgifter["P-KUND.antal_riskbransch"].model_copy(update={"varde": antal})
    profil = klar.model_copy(update={"uppgifter": {**klar.uppgifter, "P-KUND.antal_riskbransch": u}})
    return harled_andelar(profil, rb, frozenset({"P-KUND.antal_riskbransch"}))


def test_sarbarhetsstycke_ar_klartext_med_referenser(rb_intag, klar):
    id = _id_for(rb_intag, "P-GEO.andel_utland_transaktion")
    s = sarbarhetsstycke(rb_intag, klar, "T-RED-01", id)
    assert not faltid_fel(1, s.text) and "SEKTOR-" not in s.text and ">" not in s.text
    assert "Sårbarheten gäller om andel kunder med transaktioner utanför Sverige är större än 0 %." in s.text
    assert "P-GEO.andel_utland_transaktion" in s.referenser


def test_faktor_under_gransen_i_lasta_stycket(rb_intag, klar):
    id = _id_for(rb_intag, "P-KUND.andel_riskbransch")
    s = sarbarhetsstycke(rb_intag, _med_riskbransch(rb_intag, klar, 15), "T-RED-01", id)
    assert "Villkoret är inte uppfyllt." in s.text
    assert "Faktorn förekommer: andel kunder i riskbranscher är 15 %, men det ligger under metodens gräns på 20 %" in s.text


def test_saknat_geografiunderlag_ger_fortfarande_verifiera(rb_intag, klar):
    utan = klar.model_copy(update={"uppgifter": {k: v for k, v in klar.uppgifter.items() if k != "P-BESK.geografi"}})
    geo = next(id for id in rb_intag.tjanster["T-RED-01"].sarbarheter if rb_intag.sarbarheter[id].omrade == "geo")
    assert "[VERIFIERA]" in sarbarhetsstycke(rb_intag, utan, "T-RED-01", geo).text


def test_bilagan_visar_kortnamn_och_falt_id(rb_intag, klar):
    bilaga = bygg_underlagsbilaga(rb_intag, klar)
    rad = next(s.text for s in bilaga.stycken if s.referenser == ["P-KUND.andel_riskbransch"])
    assert rad.startswith("Andel kunder i riskbranscher (P-KUND.andel_riskbransch): ")
```

`_id_for` hittar S-KUND-01 och S-GEO-01, som har enkla villkor på respektive fält (kontrollerat mot regelbas 1.2.0).

- [ ] **Steg 2: Kör testerna och se dem fallera**

Kör: `.venv/bin/pytest tester/intag/test_lasta_stycken.py -q`
Förväntat: FAIL. Texten innehåller i dag fält-ID och ”Villkoret P-…”.

- [ ] **Steg 3: Implementera i `analysunderlag.py`**

Ersätt `VERIFIERA = "[VERIFIERA]"` och `_belagg` med:

```python
from riskanalys.dokument.klartext import VERIFIERA, gransmening, under_grans, uppgiftstext, villkorstext


def _belagg(regelbas: Regelbas, profil: Profil, id: str) -> str:
    return uppgiftstext(regelbas, profil, id)
```

I `erfarenhetsstycke`, ersätt `text += f" {rubrik}: " + (_belagg(regelbas, profil, id))` med:

```python
        text += " " + uppgiftstext(regelbas, profil, id, namn=rubrik)
```

Ta bort funktionen `_villkorstext`. I `sarbarhetsstycke`, ersätt raden som börjar `text = f"{s.namn} ({regelbas.tjanster[tjanst].namn}): Villkoret …` och raden `text += " ".join(_belagg(...))` med:

```python
    text = (f"{s.namn} ({regelbas.tjanster[tjanst].namn}): Sårbarheten gäller om {villkorstext(s.villkor, regelbas)}. "
            f"Villkoret är {status}. ")
    text += " ".join(gransmening(regelbas, profil, g) for g in under_grans(profil, s.villkor))
    text += " " + " ".join(_belagg(regelbas, profil, ref) for ref in sorted(falt_i(villkor)))
```

`status` är oförändrat (`uppfyllt`, `inte uppfyllt` eller `okänt`). `profil` är redan kompatibilitetsvyn i funktionen. Resten av funktionen (betydelse, `[VERIFIERA]`, geografi) behålls.

- [ ] **Steg 4: Implementera bilagan i `intagsunderlag.py`**

I `bygg_underlagsbilaga`, ersätt importen av `_belagg` och raden `text=f'{f.fraga} '+_belagg(rb,profil,f.id)` med:

```python
    from riskanalys.dokument.klartext import uppgiftstext
```
```python
            text=uppgiftstext(rb,profil,f.id,med_id=True)
```

- [ ] **Steg 5: Uppdatera två äldre påståenden**

- `tester/regelkontrakt/test_arb_erfarenhet_motivering.py:104`: `assert "Villkoret" in stycke.text and "0 %" in stycke.text` blir `assert "Sårbarheten gäller om" in stycke.text and "0 %" in stycke.text`.
- `tester/regelkontrakt/test_arb_utvidgning.py:58`: `'Villkoret' in s.text` blir `'Sårbarheten gäller om' in s.text`.

- [ ] **Steg 6: Kör testerna, även den frysta M1-kedjan**

Kör: `.venv/bin/pytest tester/intag tester/regelkontrakt tester/typfall tester/m2 -q`
Förväntat: PASS. Om något test i `tester/typfall/` fallerar på ändrad text har den frysta M1-kedjan påverkats. Stoppa då och rapportera; ändra inte typfallstesterna.

- [ ] **Steg 7: Commit**

```bash
git add src/riskanalys/dokument/analysunderlag.py src/riskanalys/dokument/intagsunderlag.py tester/intag/test_lasta_stycken.py tester/regelkontrakt/test_arb_erfarenhet_motivering.py tester/regelkontrakt/test_arb_utvidgning.py
git commit -m "feat: låsta stycken och bilaga B1 i klartext"
```

---

### Uppgift 5: Sektorsreferens och tjänstebeskrivning

**Files:**
- Modify: `src/riskanalys/dokument/nivatext.py` (`sektorsstycken`)
- Modify: `src/riskanalys/dokument/tjanstavsnitt.py:60-68` (beskrivningen i `bygg_tjanstavsnitt`)
- Test: `tester/intag/test_lasta_stycken.py`, `tester/m2/test_integrationskrav.py:34`

**Interfaces:**
- Consumes: `uppgiftstext` (uppgift 3), `_belagg` (uppgift 4), `FORMATVERSION` (uppgift 2).

- [ ] **Steg 1: Skriv de fallerande testerna**

Lägg till i `tester/intag/test_lasta_stycken.py`:

```python
from riskanalys.dokument.delskrivning import skriv_tjanst
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.nivatext import sektorsstycken
from riskanalys.dokument.promptar import DELAR
from riskanalys.dokument.tjanstavsnitt import bygg_tjanstavsnitt_v3

from tester.fixturer.m2 import godkant_delsvar, tjanst_for_prov


def test_sektorsreferensen_anges_med_kallans_titel(tmp_path, rb_intag, klar):
    _, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    (s,) = sektorsstycken(rb_intag, t)
    ref = rb_intag.sektorsreferenser[rb_intag.tjanster[t.tjanst].sektorreferens]
    assert s.text.startswith(f"{rb_intag.kallor[ref.kalla].titel} anger risknivån {ref.niva} för sektorn {ref.sektor}")
    assert "SEKTOR-" not in s.text and ref.id in s.referenser


def test_inga_falt_id_i_tjanstavsnittets_lasta_stycken(tmp_path, rb_intag, klar):
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    lev = Testleverantor([godkant_delsvar(d, t) for d in DELAR])
    res = skriv_tjanst(lev, rb_intag, klar, t, avsnitt_id, effort="medium", personnamn=(), spara=lambda d, f: None)
    avsnitt = bygg_tjanstavsnitt_v3(rb_intag, klar, t, res, avsnitt_id)
    texter = [s.text for s in avsnitt.stycken]
    assert [x for n, x in enumerate(texter, 1) if faltid_fel(n, x)] == []
    assert not [x for x in texter if "SEKTOR-" in x or " >= " in x or " == " in x]
    assert texter[0].count("Antal kunder i tjänsten") == 1
```

- [ ] **Steg 2: Kör testerna och se dem fallera**

Kör: `.venv/bin/pytest tester/intag/test_lasta_stycken.py -q -k "sektor or tjanstavsnittets"`
Förväntat: FAIL. Sektorstexten börjar med ”Sektorsreferens SEKTOR-…”, och beskrivningen innehåller ”Antal kunder i tjänsten: Antal kunder i löpande bokföring: …”.

- [ ] **Steg 3: Implementera**

`nivatext.py`, i `sektorsstycken`: ersätt tilldelningen av `text` med:

```python
    titel = rb.kallor[ref.kalla].titel
    text = (f"{titel} anger risknivån {ref.niva} för sektorn {ref.sektor} på sin egen skala "
            f"({', '.join(ref.skala)}), sida {ref.sida}. Källans skala är separat från byråns motor och likställs "
            "inte med tjänstens risknivå. Motiveringen ska pröva tjänstens egna förhållanden mot denna sektorsreferens.")
```

`tjanstavsnitt.py`, i `bygg_tjanstavsnitt`: importera `uppgiftstext` från `riskanalys.dokument.klartext` och ersätt `text += label + ': ' + _belagg(rb, p, id) + ' '` med:

```python
            text += uppgiftstext(rb, p, id, namn=label) + ' '
```

`tester/m2/test_integrationskrav.py:34`: `'Sektorsreferens' in text` blir `'för sektorn' in text`.

- [ ] **Steg 4: Kör testerna**

Kör: `.venv/bin/pytest tester/intag tester/m2 tester/regelkontrakt tester/typfall -q`
Förväntat: PASS.

- [ ] **Steg 5: Commit**

```bash
git add src/riskanalys/dokument/nivatext.py src/riskanalys/dokument/tjanstavsnitt.py tester/intag/test_lasta_stycken.py tester/m2/test_integrationskrav.py
git commit -m "feat: sektorsreferens och tjänstebeskrivning i klartext"
```

---

### Uppgift 6: Faktabladet och prompten

**Files:**
- Modify: `src/riskanalys/dokument/underlag.py:130-143` (`_sarbarhetsmotivering`)
- Modify: `src/riskanalys/dokument/faktablad.py:93-94` (`_post`, fältet `etikett`)
- Modify: `src/riskanalys/dokument/promptar/delar.py` (modulen `sarbarheter`)
- Test: `tester/intag/test_faktablad.py`, `tester/enhet/test_promptar.py`

**Interfaces:**
- Consumes: `faltnamn`, `gemen`, `under_grans` (uppgift 3). `_uppgift` finns redan i `underlag.py` och maskar små grupper och små komplement.
- Produces: `UnderlagSarbarhet.motivering` med kortnamn och, när faktorn förekommer under gränsen, en gränsmening. `Faktapost.etikett == faltnamn(regelbas, id)`.

- [ ] **Steg 1: Skriv de fallerande testerna**

Lägg till i `tester/intag/test_faktablad.py`:

```python
import pytest

from riskanalys.dokument.underlag import _sarbarhetsmotivering
from riskanalys.profil.omfattning import harled_andelar

RISKBRANSCH = "P-KUND.andel_riskbransch"


def _sarb(rb):
    return next(s.id for s in rb.sarbarheter.values() if s.villkor.get("falt") == RISKBRANSCH)


def _med_riskbransch(rb, klar, antal):
    """Testprofilen har 100 aktiva kunder; andelen härleds ur antalet, som i intaget."""
    u = klar.uppgifter["P-KUND.antal_riskbransch"].model_copy(update={"varde": antal})
    profil = klar.model_copy(update={"uppgifter": {**klar.uppgifter, "P-KUND.antal_riskbransch": u}})
    return harled_andelar(profil, rb, frozenset({"P-KUND.antal_riskbransch"}))


def test_motiveringen_sager_att_faktorn_forekommer_under_gransen(rb_intag, klar):
    text = _sarbarhetsmotivering(rb_intag, _med_riskbransch(rb_intag, klar, 15), _sarb(rb_intag), (RISKBRANSCH,))
    assert "Faktorn förekommer: andel kunder i riskbranscher är 15 %, men det ligger under metodens gräns på 20 %" in text


def test_falt_utanfor_tillatelselistan_far_ingen_gransmening(rb_intag, klar):
    text = _sarbarhetsmotivering(rb_intag, _med_riskbransch(rb_intag, klar, 15), _sarb(rb_intag), ())
    assert "gräns" not in text and "15 %" not in text


def test_skyddad_vy_ger_samma_text_for_noll_och_tre_kunder(rb_intag, klar):
    # 0 och 3 av 100 visas båda som "färre än 5". Texten får inte avslöja vilket det är (granskning 2026-10-12).
    noll, tre = (_sarbarhetsmotivering(rb_intag, _med_riskbransch(rb_intag, klar, antal), _sarb(rb_intag), (RISKBRANSCH,))
                 for antal in (0, 3))
    assert noll == tre
    assert "gräns" not in tre and "förekommer" not in tre


def test_litet_komplement_ger_ingen_gransmening(rb_intag, klar):
    # 98 av 100 lämnar ett litet komplement som maskas. Gränsen höjs bara i en kopia av regelbasen.
    villkor = {"falt": RISKBRANSCH, "op": ">=", "varde": 0.99}
    sarb = rb_intag.sarbarheter[_sarb(rb_intag)].model_copy(update={"villkor": villkor})
    rb = rb_intag.model_copy(update={"sarbarheter": {**rb_intag.sarbarheter, sarb.id: sarb}})
    text = _sarbarhetsmotivering(rb, _med_riskbransch(rb_intag, klar, 98), sarb.id, (RISKBRANSCH,))
    assert "gräns" not in text and "förekommer" not in text and "98 %" not in text
```

Repots regelbas ändras inte. Testerna visar att ett maskat värde aldrig ger en gränsmening, och att 0 och 3 kunder ger identisk text.

Lägg till i `tester/enhet/test_promptar.py`:

```python
def test_sarbarhetsmodulen_styr_formuleringen_under_gransen():
    assert "förekommer men ligger under metodens gräns" in delmodul("sarbarheter")
```

- [ ] **Steg 2: Kör testerna och se dem fallera**

Kör: `.venv/bin/pytest tester/intag/test_faktablad.py tester/enhet/test_promptar.py -q`
Förväntat: FAIL för gränsmeningen och promptinstruktionen. Motiveringen innehåller i dag bara ”P-KUND.andel_riskbransch: 15 %.”. De två skyddstesterna passerar redan, eftersom dagens kod saknar gränsmening. De ska fortsätta passera efter steg 3 och skyddar mot att den nya meningen läcker.

- [ ] **Steg 3: Implementera `_sarbarhetsmotivering`**

```python
def _sarbarhetsmotivering(regelbas: Regelbas, profil: Profil, id: str, tillatna: tuple[str, ...]) -> str:
    from riskanalys.dokument.klartext import faltnamn, gemen, under_grans
    from riskanalys.profil.omfattning import kompatibilitetsvy
    from riskanalys.regelverk.villkor import falt_i
    s = regelbas.sarbarheter[id]
    status = sarbarhet_status(regelbas, profil, id)
    falt = sorted(falt_i(tolka_villkor(s.villkor, regelbas.faltdefinitioner())))
    rader = []
    for ref in falt:
        if ref not in tillatna:
            rader.append(f"{faltnamn(regelbas, ref)}: underlaget finns i byråns lokala belägg; motiveringen behöver granskas lokalt.")
            continue
        u = _uppgift(regelbas, profil, ref)
        period = f" Period: {'–'.join(u.period)}." if u.period else ""
        rader.append(f"{faltnamn(regelbas, ref)} ({ref}): {u.varde}.{period}")
    for g in under_grans(kompatibilitetsvy(profil, regelbas), s.villkor):
        if g.falt_id not in tillatna:
            continue
        visning = _uppgift(regelbas, profil, g.falt_id).varde
        # Bara den skyddade vyn styr: ett maskat värde ger ingen mening alls, så att 0 och 3 kunder ser likadana ut.
        if visning.startswith(SKYDDADE_VISNINGAR) or visning == "okänt":
            continue
        grans = visa_varde(regelbas.falt[g.falt_id], g.grans)
        rader.append(f"Faktorn förekommer: {gemen(faltnamn(regelbas, g.falt_id))} är {visning}, men det ligger "
                     f"under metodens gräns på {grans} för automatiskt riskpåslag.")
    return f"Det registrerade villkorets utfall är {status}. " + " ".join(rader)
```

Flytta konstanten `_SKYDDADE = ("färre än", "undertryckt")` från `faktablad.py` till `underlag.py` som `SKYDDADE_VISNINGAR`, och låt `faktablad.py` importera den därifrån. Skyddet har då en enda källa. Importera `visa_varde` från `riskanalys.profil.hantering` överst i `underlag.py` om den inte redan finns där. Fält-ID står bara inom parentes i faktabladet, där AI behöver dem för referenser och `{tal:ID}`. Raden för fält utanför tillåtelselistan visar inget ID, eftersom AI inte kan referera till dem.

- [ ] **Steg 4: Kortnamn i faktaposterna**

I `faktablad.py`, `_post`: ersätt `etikett=u.fraga` med `etikett=faltnamn(regelbas, u.id)` och importera `faltnamn` från `riskanalys.dokument.klartext`.

- [ ] **Steg 5: Instruktion i sårbarhetsmodulen**

I `promptar/delar.py`, modulen `sarbarheter`: lägg till följande rad direkt före raden `"Programmet har redan skrivit underlagsstycket för geografin. Bygg vidare på det."`:

```python
        "Om faktabladet säger att en faktor förekommer men ligger under metodens gräns, skriver du just det. Skriv "
        "inte att faktorn saknas eller att sårbarheten inte berör byrån.\n"
```

Kontrollera att `modultext("sarbarheter")` fortfarande ryms inom ordintervallets prompttext. Längdtesterna i `test_promptar.py` ska passera.

- [ ] **Steg 6: Kör testerna**

Kör: `.venv/bin/pytest tester/intag tester/enhet/test_promptar.py tester/enhet/test_delvalidering.py -q`
Förväntat: PASS. Testet `test_inget_anrop_kommenterar_vad_ai_far_se` ska fortfarande passera.

- [ ] **Steg 7: Commit**

```bash
git add src/riskanalys/dokument/underlag.py src/riskanalys/dokument/faktablad.py src/riskanalys/dokument/promptar/delar.py tester/intag/test_faktablad.py tester/enhet/test_promptar.py
git commit -m "feat: faktabladet anger faktorer under metodens gräns med kortnamn"
```

---

### Uppgift 7: Helhetskontroll och status

**Files:**
- Modify: `docs/STATUS.md`

**Interfaces:** inga.

- [ ] **Steg 1: Hela sviten och regelbasen**

Kör: `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest -q`
Förväntat: alla gröna, två livetester bortvalda.

Kör: `.venv/bin/riskanalys regelbas validera && git diff --check`
Förväntat: grönt, regelbas 1.3.0, sakkunnigstatus `ej_granskad`.

Kör: `START=$(grep -m1 '^START=' docs/superpowers/plans/2026-10-12-klartext-i-lasta-stycken.md | cut -d= -f2)`
Kör: `git diff "$START"..HEAD -- regelbas/kataloger/sarbarheter.yaml regelbas/kundfalt.yaml`
Förväntat: ingen diff. Gränserna och kundmodellens fält är oförändrade.

Kör: `git diff "$START"..HEAD --stat -- tester/enhet/test_faststall.py tester/enhet/test_manifest.py tester/typfall/ tester/fixturer/regelbas_v0/`
Förväntat: ingen diff.

- [ ] **Steg 2: Uppdatera `docs/STATUS.md`**

Lägg ett nytt avsnitt överst, under ”Senast uppdaterad”, med rubriken `## Klartext i låsta stycken (format v4), <datum>`. Avsnittet ska säga:
- att låsta stycken nu skrivs med kortnamn, villkor i ord, gränsmeningar och sektorsreferens med källans titel
- att `D-ARB.B1` visar kortnamn och fält-ID
- att regelbasen är 1.3.0 med 43 kortnamn och oförändrade regler och gränser
- att formatet är `D-ARB-tjanst-v4`, att utkast i v3 måste skrivas om och sakgranskas på nytt, och att fastställda paket är oförändrade
- fullsvitens resultat
- att nästa pilot ska kontrollera att AI inte skriver att en sårbarhet under gränsen ”inte gäller”

- [ ] **Steg 3: Commit**

```bash
git add docs/STATUS.md
git commit -m "docs: status för klartext i låsta stycken"
```

---

## Återanvändning av v3-utkast (utredning)

Frågan är om redan skrivna AI-delar kan föras över till v4 med lokal omvalidering och ny sakgranskning, i stället för att skrivas om mot betalt API.

**Vad som hindrar direkt återanvändning:**
- Ett v3-resultat bär sitt frysta faktablad.
- v4 ändrar faktabladets motiveringar och etiketter, så `kontrollera_resultat` underkänner v3-resultatet mot aktuellt underlag.
- Formatversionen skiljer sig också.

**Vad som talar för att det går:**
- AI-delarna refererar samma ID:n som i v4 och använder platshållare som fortfarande går att ersätta.
- Råsvaret för varje godkänd del kan tolkas och valideras om lokalt mot v4-faktabladet, med samma `_tolka` och `validera_del` som grinden använder. Det kostar inga API-anrop.

**Vad som talar emot:**
- Texten skrevs från v3-faktabladet. Den kan säga att en faktor under gränsen ”inte gäller”, vilket v4 ska rätta.
- Delar med interna AI-kommentarer underkänns nu av valideringen och skulle bli reservmall.
- Sakgranskning krävs ändå för v4-texten.

**Kostnad att skriva om:** i piloten kostade `medium` 0,23–0,31 USD per tjänst och `high` 0,49–0,62 USD. En byrå med fem tjänster kostar alltså omkring 1,50 USD med `medium`. Inga verkliga v3-utkast är kända. Piloterna har körts på den syntetiska byrån.

**Rekommendation:** bygg inte återanvändningen i denna plan. Skriv om v3-utkast med `medium` när det behövs. Om en byrå har v3-utkast under pågående sakgranskning kan en egen liten plan bygga det enligt skissen nedan.

**Skiss, om den behövs:** `uppgradera_resultat(rb, p, t, gammal, avsnitt_id) -> Tjanstresultat`
- **Formatkrav:** kräver `gammal.formatversion == "D-ARB-tjanst-v3"`.
- **Nytt faktablad:** bygger v4-faktabladet.
- **Delar som var mall** förblir mall.
- **Godkända delar:** varje godkänd del tolkas och valideras om mot v4-faktabladet. En del som klarar det behåller sina försök och märks `omvaliderad=True`, ett fält som bara serialiseras när det är sant. En del som inte klarar det blir mall med blockerande fynd.
- **Spårbarhet:** manifestet anger `uppgraderad_fran`.
- **Granskningsfynd:** granskningen lägger ett fynd på omvaliderade delar, så att sakgranskaren prövar faktorer under metodens gräns särskilt.
- **Tester:** inga leverantörsanrop sker (en `Testleverantor` utan svar), en omvaliderad del klarar `kontrollera_resultat`, och en del med en intern AI-kommentar blir mall.

## Självgranskning

- **Täckning:**
  - Preciseringarna täcks av uppgift 4 och 5 (nivatext, tjanstavsnitt, analysunderlag), uppgift 3, 4 och 6 (15 % under gränsen) och uppgift 2 (v4 och sakgranskning).
  - Uppföljningsavsnitten får klartext via `_belagg` (uppgift 4) och kortnamn för sina fält (uppgift 3).
  - Spårbarheten täcks av referenserna och B1 (uppgift 4).
- **Fastställda paket:** de läses men byggs aldrig om. Testerna för paket och manifest körs oförändrade i uppgift 2 och 7.
- **Andra granskningen:**
  - Läckaget via gränsmeningen stängs i uppgift 6, med testet för 0 mot 3 kunder.
  - Historiska attestsummor skyddas i uppgift 3, med frysta summor för v0-basen och `KRV-PTL-2-9`.
  - Slutkontrollen använder start-SHA.
  - Återanvändningen av v3-utkast är utredd med en rekommendation.
- **Typkonsekvens:** `under_grans(profil, data)` tar ingen regelbas; `gransmening(regelbas, profil, g)` gör det. `uppgiftstext(..., namn=, med_id=)` används med samma nyckelord i uppgift 4, 5 och 6.

## Genomförandelogg

START=6736edea6a4e9ef07a08a5721fbc8c083658e62e
