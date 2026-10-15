# Personnamn, maskering och avrundning: byggplan

> **För agenter:** OBLIGATORISK DELSKILL: använd superpowers:subagent-driven-development (rekommenderas) eller superpowers:executing-plans för att bygga planen uppgift för uppgift. Stegen använder kryssrutor (`- [ ]`).

**Mål:** Stänga de tre luckor som granskningen 2026-10-14 hittade efter planen för skyddad AI-begäran. Personnamn ska inte påverka AI-flödet, smågruppsskyddade värden ska visas för AI med en gemensam text, och andelar nära metodens gränser ska visas med tillräcklig precision.

**Arkitektur:**
- Namnkontrollen flyttas ur omförsöksslingan i `skriv_del` till ett lokalt steg i `skriv_tjanst`, efter tjänstens alla AI-anrop. En del med namn ersätts av mallen och märks `lokal_sparr="personnamn"`.
- Maskeringen får en enda konstant, `SKYDDAD_VISNING`.
- Visningen av andelar får tillgång till metodens gränser för fältet via en ny liten modul, `regelverk/granser.py`.

**Teknik:** Python 3.12/3.13, Pydantic (frysta modeller), pytest, YAML-regelbas 1.3.0.

**Spec:** `docs/superpowers/specs/2026-10-08-riskanalys-design.md`, revision 20: 8.4.9 punkt 10 och 8.4.10 punkt 6–8.

**Git:** planen innehåller inga commitsteg. Att bygget är godkänt betyder inte att commit är godkänd. Ändringarna lämnas ostagade till controllern.

## Globala villkor

- AI fattar inga beslut. Risknivåer, poäng och regler kommer från regelbasen och riskmotorn (AGENTS.md regel 1).
- Inga personuppgifter till AI. AI-underlag byggs bara ur `regelbas/tillatelselistor.yaml` (regel 2).
- Bara syntetiska data i tester (regel 3).
- Regelbasen ändras inte i den här planen. Inga regler, gränser eller nivåer ändras.
- Tester före kod. Hela sviten ska vara grön: `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest -q` (regel 6).
- Inga riktiga API-anrop i tester. Använd `Testleverantor` (regel 7).
- Användartexter på svenska. Identifierare på svenska utan å, ä och ö. Funktioner returnerar nya objekt.
- Den utgående AI-begäran (systemprompt, innehåll, återkoppling vid omförsök, schema) och antalet anrop får bara bero på det AI får se (spec 8.4.10 punkt 1 och 7).

## Granskningsfokus

1. Identitetsproven ska köras med profilens verkliga personnamn, inte `personnamn=()`. Det åtgärdas i uppgift 1, där hjälparen `begaran` ändras.
2. Ett namn som bara står i en oklarhetsfråga ska fångas lokalt. Uppgift 1 har enhetsprovet för `innehaller_personnamn`.
3. Ett sparat tjänstresultat utan fältet `lokal_sparr` ska fortfarande kunna läsas. Uppgift 1 har ett prov för det.
4. En andel som ligger exakt på gränsen visas som "20 %". Ett skyddat litet värde nära en gräns förblir maskerat. Uppgift 3 har proven.
5. Andelar nära 0 och 100 % ska fortfarande visas som intervall ("mindre än 1 %" och "mer än 99 %"), även när fältet har gränser. Uppgift 3 har provet.

---

### Uppgift 1: Personnamn prövas bara lokalt

**Filer:**
- Ändra: `src/riskanalys/dokument/delvalidering.py` (namnkontrollen i `_stycke` och `_gemensamma`; ny `innehaller_personnamn`)
- Ändra: `src/riskanalys/dokument/delskrivning.py` (`Delresultat`, `skriv_del`, `skriv_tjanst`)
- Ändra: `src/riskanalys/granskning/analys.py` (`mallfynd`)
- Prov: `tester/intag/test_skyddad_begaran.py`, `tester/enhet/test_delvalidering.py`, `tester/intag/test_v3_grind.py`

**Gränssnitt:**
- Producerar: `innehaller_personnamn(svar: AISvar, personnamn: tuple[str, ...]) -> bool` i `delvalidering`.
- Producerar: `Delresultat.lokal_sparr: Literal["personnamn"] | None = None`.
- Ändrar: `skriv_del(leverantor, fb, t, del_id, validerat, *, effort, spara)`. Parametrarna `regelbas`, `profil` och `personnamn` tas bort; enda anroparen är `skriv_tjanst`.
- Oförändrat: `skriv_tjanst(...)` har samma signatur och tar fortfarande `personnamn`.

- [x] **Steg 1: Skriv de fallerande proven**

Gör följande ändringar i `tester/intag/test_skyddad_begaran.py`.

Lägg till importen:

```python
from riskanalys.profil.hantering import personnamn
```

I hjälparen `begaran`, ersätt `personnamn=()` med `personnamn=personnamn(profil, rb)`, så att alla identitetsprov körs med profilens verkliga namn (spec 8.4.10 punkt 6).

Lägg till sist i filen:

```python
def _skriv_med_namn(rb, profil, svar):
    """Utgående begäran och tjänstresultat med profilens verkliga personnamn."""
    with tempfile.TemporaryDirectory() as mapp:
        avsnitt_id, t = tjanst_for_prov(Path(mapp), rb, profil)
        lev = Testleverantor(svar(t))
        res = skriv_tjanst(lev, rb, profil, t, avsnitt_id, effort="medium", personnamn=personnamn(profil, rb),
                           spara=lambda d, f: None)
        return [a.model_dump(mode="json") for a in lev.delanrop], res


def _svar_med_namn(t):
    """Godkända svar, men hotdelen nämner Anna Svensson i genitiv."""
    hot = godkant_delsvar("hot", t)
    forsta = hot.stycken[0].model_copy(update={"text": "Anna Svenssons arbetsrutin följs. " + hot.stycken[0].text})
    return [AISvar(stycken=[forsta, *hot.stycken[1:]], oklarheter=[]) if d == "hot" else godkant_delsvar(d, t)
            for d in DELAR]


def _anna_och_bertil(rb, klar):
    anna = _med(rb, klar, {"P-ROLL.ffr_namn": "Anna Svensson"})
    bertil = _med(rb, klar, {"P-ROLL.ffr_namn": "Bertil Berg"})
    assert "Anna Svensson" in personnamn(anna, rb) and "Bertil Berg" in personnamn(bertil, rb)
    return anna, bertil


def test_personnamn_paverkar_varken_aterkoppling_eller_antal_anrop(rb_intag, klar):
    anna, bertil = _anna_och_bertil(rb_intag, klar)
    kord_anna, _ = _skriv_med_namn(rb_intag, anna, _svar_med_namn)
    kord_bertil, _ = _skriv_med_namn(rb_intag, bertil, _svar_med_namn)
    assert len(kord_anna) == len(DELAR) and kord_anna == kord_bertil


def test_del_med_personnamn_i_genitiv_ersatts_av_mallen_lokalt(rb_intag, klar):
    anna, bertil = _anna_och_bertil(rb_intag, klar)
    _, res_anna = _skriv_med_namn(rb_intag, anna, _svar_med_namn)
    _, res_bertil = _skriv_med_namn(rb_intag, bertil, _svar_med_namn)
    hot = res_anna.del_("hot")
    assert hot.mall and hot.lokal_sparr == "personnamn" and hot.godkant_svar is None
    assert not res_bertil.del_("hot").mall and res_bertil.del_("hot").lokal_sparr is None


def test_sparat_tjanstresultat_utan_lokal_sparr_kan_lasas(rb_intag, klar):
    _, res = _skriv_med_namn(rb_intag, klar, lambda t: [godkant_delsvar(d, t) for d in DELAR])
    data = json.loads(res.model_dump_json())
    for d in data["delar"]:
        d.pop("lokal_sparr")
    assert type(res).model_validate(data) == res
```

I `tester/enhet/test_delvalidering.py`: importera `innehaller_personnamn` från `riskanalys.dokument.delvalidering`, och `AIOklarhet`, `AIStycke` och `AISvar` från `riskanalys.dokument.modeller` (om de inte redan är importerade). Lägg sedan till:

```python
def test_innehaller_personnamn_fangar_genitiv_skiftlage_och_oklarheter():
    stycke = AIStycke(typ="analys", referenser=["T-RED-01"], text="ANNA SVENSSONS rutin följs.")
    assert innehaller_personnamn(AISvar(stycken=[stycke], oklarheter=[]), ("Anna Svensson",))
    fraga = AISvar(stycken=[stycke.model_copy(update={"text": "Rutinen följs."})],
                   oklarheter=[AIOklarhet(uppgift_id="P-KUND.antal_aktiva", fraga="Har Anna Svensson bekräftat?")])
    assert innehaller_personnamn(fraga, ("Anna Svensson",))
    assert not innehaller_personnamn(fraga, ("Bertil Berg",))
    assert not innehaller_personnamn(fraga, ())
```

Om `AIOklarhet` har fler obligatoriska fält, fyll dem med syntetiska värden och nämn det i rapporten.

I `tester/intag/test_v3_grind.py`, lägg till efter `test_mall_del_ger_blockerande_fynd`:

```python
def test_mall_del_med_personnamn_ger_eget_fynd(v3):
    rb, p, t, res, avsnitt_id = v3
    mall = res.model_copy(update={"delar": tuple(
        d.model_copy(update={"mall": True, "lokal_sparr": "personnamn"}) if d.del_id == "hot" else d
        for d in res.delar)})
    fynd = mallfynd(mall)
    assert len(fynd) == 1 and fynd[0]["allvar"] == "blockerande"
    assert "innehöll ett bekräftat personnamn" in fynd[0]["beskrivning"]
```

- [x] **Steg 2: Kör proven och se dem fallera**

Kör: `.venv/bin/pytest -q tester/intag/test_skyddad_begaran.py tester/enhet/test_delvalidering.py tester/intag/test_v3_grind.py`

Väntat utfall:
- `test_personnamn_paverkar_...` faller. Annas profil får omförsök med återkopplingen om personnamn, och leverantören får fler anrop eller tar slut på svar.
- `test_del_med_personnamn_...`, `test_sparat_tjanstresultat_...` och `test_mall_del_med_personnamn_...` faller på att fältet `lokal_sparr` inte finns.
- `test_innehaller_personnamn_...` faller med ImportError.
- Spara utdata.

- [x] **Steg 3: Implementera**

I `src/riskanalys/dokument/delvalidering.py`, lägg till ovanför `_stycke`:

```python
def _har_namn(text: str, personnamn: tuple[str, ...]) -> bool:
    """Delsträng utan hänsyn till skiftläge, så att också genitiv och sammansättningar fångas."""
    liten = text.lower()
    return any(namn.lower() in liten for namn in personnamn if namn)


def innehaller_personnamn(svar: AISvar, personnamn: tuple[str, ...]) -> bool:
    """Lokal namnkontroll efter tjänstens alla AI-anrop (spec 8.4.10 punkt 7)."""
    texter = (*(s.text for s in svar.stycken), *(o.fraga for o in svar.oklarheter))
    return any(_har_namn(text, personnamn) for text in texter)
```

Byt sedan två rader:
- I `_stycke`: `if any(namn.lower() in liten for namn in personnamn):` blir `if _har_namn(s.text, personnamn):`.
- I `_gemensamma`: `if any(namn.lower() in o.fraga.lower() for namn in personnamn):` blir `if _har_namn(o.fraga, personnamn):`.

Variabeln `liten` i `_stycke` används fortfarande av `FORBJUDNA_FORMULERINGAR` och ska vara kvar.

I `src/riskanalys/dokument/delskrivning.py`:

```python
from riskanalys.dokument.delvalidering import innehaller_personnamn, validera_del
```

```python
class Delresultat(Last):
    del_id: str
    forsok: tuple[Delforsok, ...]
    mall: bool
    lokal_sparr: Literal["personnamn"] | None = None
```

`skriv_del` får den nya signaturen. Valideringen i slingan körs utan namn:

```python
def skriv_del(leverantor, fb: Faktablad, t, del_id: str, validerat: tuple[str, ...], *,
              effort: str, spara: Callable[[str, Delforsok], None]) -> Delresultat:
    # Valideringen får bara jämföra mot det AI faktiskt har sett. De riktiga låsta texterna och personnamnen
    # prövas bara lokalt (spec 8.4.10 punkt 1, 2 och 7).
    lasta = skyddade_lasta_texter(fb, t, del_id)
    ...
        if svar is not None:
            fel = tuple(validera_del(del_id, svar, fb, (), lasta))
```

Lägg till ovanför `skriv_tjanst`:

```python
def _utan_personnamn(d: Delresultat, personnamn: tuple[str, ...]) -> Delresultat:
    """Namnen prövas först när tjänstens alla AI-anrop är gjorda, så att varken återkoppling eller antal anrop
    beror på dem (spec 8.4.10 punkt 7). En del med namn ersätts av mallen."""
    svar = d.godkant_svar
    if svar is None or not innehaller_personnamn(svar, personnamn):
        return d
    return d.model_copy(update={"mall": True, "lokal_sparr": "personnamn"})
```

Ändra i `skriv_tjanst`:
- Anropet blir `skriv_del(leverantor, fb, t, del_id, underlag, effort=effort, spara=spara)`.
- Returen bygger `delar=tuple(_utan_personnamn(d, personnamn) for d in delar.values())`.
- `kontrollera_resultat` ändras inte. Den prövar fortfarande namnen i varje del som inte är mall, före dokumentbygget.

I `src/riskanalys/granskning/analys.py`:

```python
_MALLORSAK = {
    None: "kunde inte skrivas maskinellt och består av programmets mall",
    "personnamn": "innehöll ett bekräftat personnamn och har ersatts av programmets mall",
}
```

och i `mallfynd`: `beskrivning=f"{resultat.tjanst}: delen {d.del_id} {_MALLORSAK[d.lokal_sparr]}.",`.

- [x] **Steg 4: Kör proven gröna**

Kör samma kommando som i steg 2. Väntat utfall: alla passerar, även de befintliga identitetsproven, som nu körs med "Testa Testsson".

- [x] **Steg 5: Kör hela sviten**

Kör: `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest -q`. Väntat utfall: allt grönt.

---

### Uppgift 2: Gemensam maskeringstext för AI

**Filer:**
- Ändra: `src/riskanalys/dokument/underlag.py` (konstanten, `visa_for_ai`, `_uppgift`, `provas_lokalt`, `_sarbarhetsmotivering`)
- Ändra: `src/riskanalys/dokument/faktablad.py` (import och `_post`)
- Prov: `tester/intag/test_skyddad_begaran.py`, plus förväntningarna i proven som listas i steg 1

**Gränssnitt:**
- Producerar: `SKYDDAD_VISNING = "skyddat värde, prövas lokalt"` i `underlag`.
- Tar bort: `SKYDDADE_VISNINGAR`.

- [x] **Steg 1: Skriv det fallerande provet och uppdatera förväntningarna**

I `tester/intag/test_skyddad_begaran.py`, efter `test_litet_komplement_ger_utfallet_provas_lokalt`:

```python
def test_liten_grupp_och_liten_restgrupp_ger_samma_begaran(rb_intag, klar):
    # 3 av 100 är en liten grupp och 97 av 100 en liten restgrupp; AI ska inte se vilken sida (spec 8.4.10 punkt 8).
    assert _lika(rb_intag, [_med(rb_intag, klar, {"P-KUND.antal_riskbransch": n}) for n in (3, 97)])
```

Importera `SKYDDAD_VISNING` från `riskanalys.dokument.underlag` i varje provfil nedan och byt förväntningarna:

| Fil:rad (ungefär) | Före | Efter |
|---|---|---|
| `tester/intag/test_skyddad_begaran.py:79` | `.visningsvarde.startswith("undertryckt")` | `.visningsvarde == SKYDDAD_VISNING` |
| `tester/intag/test_skyddad_begaran.py:62, 75` (kommentarer) | "undertryckt …" | "skyddat värde" |
| `tester/intag/test_faktablad.py:35` | `p.visningsvarde.startswith(("färre än", "undertryckt"))` | `p.visningsvarde == SKYDDAD_VISNING` |
| `tester/intag/test_faktablad.py:154` | `post.visningsvarde == "färre än 5"` | `post.visningsvarde == SKYDDAD_VISNING` |
| `tester/intag/test_faktablad.py:91, 149` (kommentarer) | "färre än 5" | "skyddat värde" |
| `tester/enhet/test_underlag.py:56` | `anstallda.varde == "färre än 5"` | `anstallda.varde == SKYDDAD_VISNING` |
| `tester/enhet/test_underlag.py:93` | `("färre än 5" if antal<5 else "5 %")` | `(SKYDDAD_VISNING if antal<5 else "5 %")` |
| `tester/enhet/test_delvalidering.py:182, 191` | `'visningsvarde': 'färre än 5'` | `'visningsvarde': SKYDDAD_VISNING` |
| `tester/m2/test_integrationskrav.py:47, 69, 70` | `=='färre än 5'` | `==SKYDDAD_VISNING` |
| `tester/m2/test_granskning_rattelser.py:150` | `== 'undertryckt (litet komplement)'` | `== SKYDDAD_VISNING` |
| `tester/regelkontrakt/test_arb_erfarenhet_motivering.py:67` | `== "färre än 5"` | `== SKYDDAD_VISNING` |
| `tester/regelkontrakt/test_arb_erfarenhet_motivering.py:141` | `"färre än 5" in s.motivering` | `SKYDDAD_VISNING in s.motivering` |

Kontrollera med `grep -rn "färre än\|undertryckt" tester src` att ingen förväntan på den gamla AI-texten finns kvar. Lokala texter som visar verkliga värden ska inte ändras.

- [x] **Steg 2: Kör proven och se dem fallera**

Kör: `.venv/bin/pytest -q tester/intag/test_skyddad_begaran.py tester/intag/test_faktablad.py tester/enhet/test_underlag.py tester/enhet/test_delvalidering.py tester/m2/test_integrationskrav.py tester/m2/test_granskning_rattelser.py tester/regelkontrakt/test_arb_erfarenhet_motivering.py`

Väntat utfall:
- ImportError för `SKYDDAD_VISNING`.
- När importen finns faller det nya identitetsprovet, eftersom 3 visas som "färre än 5" och 97 som "undertryckt (litet komplement)".

- [x] **Steg 3: Implementera**

I `src/riskanalys/dokument/underlag.py`:

```python
SKYDDAD_VISNING = "skyddat värde, prövas lokalt"  # samma text för liten grupp och liten restgrupp (spec 8.4.10 punkt 8)
```

Ersätt `SKYDDADE_VISNINGAR` på fyra ställen:
- `visa_for_ai`: `return f"färre än {SMA_GRUPPER_GRANS}"` blir `return SKYDDAD_VISNING`.
- `_uppgift`: `varde = "undertryckt (litet komplement)"` blir `varde = SKYDDAD_VISNING`.
- `provas_lokalt` och `_sarbarhetsmotivering`: `if visning.startswith(SKYDDADE_VISNINGAR) or visning == "okänt":` blir `if visning in (SKYDDAD_VISNING, "okänt"):`.

Ta bort `SKYDDADE_VISNINGAR`.

I `src/riskanalys/dokument/faktablad.py`:
- Importera `SKYDDAD_VISNING` i stället för `SKYDDADE_VISNINGAR`.
- I `_post`: `skyddad = u.varde == SKYDDAD_VISNING`.

- [x] **Steg 4: Kör proven gröna**

Kör samma kommando som i steg 2. Väntat utfall: alla passerar.

- [x] **Steg 5: Kör hela sviten**

Väntat utfall: allt grönt. Om `tester/typfall` eller `tester/enhet/test_m1_gyllene_dokument.py` faller enbart på grund av den nya texten: ändra inte de filerna. Rapportera NEEDS_CONTEXT med diffen.

---

### Uppgift 3: Andelar nära metodens gränser

**Filer:**
- Skapa: `src/riskanalys/regelverk/granser.py`
- Ändra: `src/riskanalys/profil/hantering.py` (`visa_varde_klartext` och ny `_andel_vid_grans`)
- Ändra: `src/riskanalys/dokument/klartext.py` (`uppgiftstext`, `gransmening`)
- Ändra: `src/riskanalys/dokument/underlag.py` (`visa_for_ai`)
- Ändra: `src/riskanalys/dokument/faktablad.py` (`_INTERVALLVISNINGAR`, `_post`)
- Prov: skapa `tester/enhet/test_andel_vid_grans.py`; ändra `tester/intag/test_faktablad.py`

**Gränssnitt:**
- Producerar: `metodgranser(regelbas: Regelbas, falt_id: str) -> tuple[float, ...]`. Den ger unika, sorterade gränser strikt mellan 0 och 1 som sårbarheternas villkor jämför fältet med (`>=`, `>`, `<`, `<=`).
- Ändrar: `visa_varde_klartext(falt: Falt, varde: Any, granser: tuple[float, ...] = ()) -> str`.

- [x] **Steg 1: Skriv de fallerande proven**

Skapa `tester/enhet/test_andel_vid_grans.py`:

```python
import pytest

from riskanalys.profil.hantering import visa_varde_klartext
from riskanalys.regelverk.granser import metodgranser
from riskanalys.regelverk.laddning import ladda_regelbas


@pytest.fixture(scope="module")
def rb():
    return ladda_regelbas()


@pytest.fixture(scope="module")
def andel(rb):
    return rb.falt["P-KUND.andel_riskbransch"]


@pytest.mark.parametrize(("varde", "vantat"), [
    (0.195, "19,5 %"), (0.204, "20,4 %"), (0.2004, "20,04 %"), (0.0995, "9,95 %"),
    (0.19996, "strax under 20 %"), (0.200001, "strax över 20 %"), (0.2, "20 %"), (0.33, "33 %"),
])
def test_andel_nara_grans_visas_pa_ratt_sida(andel, varde, vantat):
    assert visa_varde_klartext(andel, varde, (0.1, 0.2)) == vantat


def test_utan_granser_ar_visningen_oforandrad(andel):
    assert visa_varde_klartext(andel, 0.195) == "20 %"


def test_intervall_vid_noll_och_hundra_gar_fore_gransen(andel):
    assert visa_varde_klartext(andel, 0.003, (0.2,)) == "mindre än 1 %"
    assert visa_varde_klartext(andel, 0.997, (0.2,)) == "mer än 99 %"


def test_metodgranser_ar_unika_sorterade_och_strikt_mellan_noll_och_ett(rb):
    assert metodgranser(rb, "P-KUND.andel_riskbransch") == (0.2,)
    # Bara jämförelsen '> 0' finns för det här fältet; den hanteras av intervallregeln (8.4.9 punkt 7).
    assert metodgranser(rb, "P-GEO.andel_utland_transaktion") == ()
```

Om `P-KUND.andel_riskbransch` har fler gränser i katalogen än 0,2, ändra förväntan till de faktiska gränserna och nämn det i rapporten.

I `tester/intag/test_faktablad.py`, lägg till (importera `harled_andelar` från `riskanalys.profil.omfattning`, `sarbarhetsstycke` från `riskanalys.dokument.analysunderlag` och `uppgiftstext` från `riskanalys.dokument.klartext`, om de inte redan är importerade):

```python
def _med_antal(rb, profil, varden: dict):
    upp = dict(profil.uppgifter)
    for falt_id, varde in varden.items():
        upp[falt_id] = upp[falt_id].model_copy(update={"varde": varde})
    return harled_andelar(profil.model_copy(update={"uppgifter": upp}), rb, frozenset(varden))


def test_195_av_1000_visas_under_gransen_i_faktablad_och_lokalt(tmp_path, rb_intag, klar):
    profil = _med_antal(rb_intag, klar, {"P-KUND.antal_riskbransch": 195, "P-KUND.antal_aktiva": 1000})
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, profil)
    fb = bygg_faktablad(rb_intag, profil, t, avsnitt_id)
    post = next(p for p in fb.poster if p.id == "P-KUND.andel_riskbransch")
    assert post.visningsvarde == "19,5 %" and post.tal == 19.5
    mening = "är 19,5 %, men det ligger under metodens gräns på 20 %"
    assert mening in next(s for s in fb.sarbarheter if s.id == "S-KUND-01").motivering
    assert mening in sarbarhetsstycke(rb_intag, profil, t.tjanst, "S-KUND-01").text
    assert "19,5 %" in uppgiftstext(rb_intag, profil, "P-KUND.andel_riskbransch")


def test_204_av_1000_visas_over_gransen(tmp_path, rb_intag, klar):
    profil = _med_antal(rb_intag, klar, {"P-KUND.antal_riskbransch": 204, "P-KUND.antal_aktiva": 1000})
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, profil)
    post = next(p for p in bygg_faktablad(rb_intag, profil, t, avsnitt_id).poster if p.id == "P-KUND.andel_riskbransch")
    assert post.visningsvarde == "20,4 %"


def test_skyddat_litet_varde_nara_gransen_forblir_maskerat(tmp_path, rb_intag, klar):
    profil = _med_antal(rb_intag, klar, {"P-KUND.antal_riskbransch": 3, "P-KUND.antal_aktiva": 15})
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, profil)
    post = next(p for p in bygg_faktablad(rb_intag, profil, t, avsnitt_id).poster if p.id == "P-KUND.andel_riskbransch")
    assert post.visningsvarde == SKYDDAD_VISNING and post.tal is None
```

`tjanst_for_prov` importeras från `tester.fixturer.m2`, om filen inte redan har den. Om `S-KUND-01` blir "prövas lokalt" vid 195 av 1 000: kontrollera varför, och rapportera det i stället för att ändra förväntan.

- [x] **Steg 2: Kör proven och se dem fallera**

Kör: `.venv/bin/pytest -q tester/enhet/test_andel_vid_grans.py tester/intag/test_faktablad.py`

Väntat utfall:
- ImportError för `regelverk.granser`.
- När modulen finns faller visningsproven, eftersom "20 %" visas för både 195 och 204.

- [x] **Steg 3: Implementera**

Skapa `src/riskanalys/regelverk/granser.py`:

```python
"""Metodens jämförelsegränser per fält, för visning av andelar nära en gräns (spec 8.4.9 punkt 10)."""

from riskanalys.regelverk.modeller import Regelbas

JAMFORELSER = (">=", ">", "<", "<=")


def _granser(data: dict, falt_id: str) -> tuple[float, ...]:
    if "falt" in data:
        varde = data.get("varde")
        traff = (data["falt"] == falt_id and data.get("op") in JAMFORELSER
                 and type(varde) in (int, float) and 0 < varde < 1)
        return (float(varde),) if traff else ()
    if "inte" in data:
        return _granser(data["inte"], falt_id)
    return tuple(g for d in data.get("alla", data.get("nagon", [])) for g in _granser(d, falt_id))


def metodgranser(regelbas: Regelbas, falt_id: str) -> tuple[float, ...]:
    """Gränser strikt mellan 0 och 1 som sårbarheternas villkor jämför fältet med, unika och sorterade."""
    return tuple(sorted({g for s in regelbas.sarbarheter.values() for g in _granser(s.villkor or {}, falt_id)}))
```

I `src/riskanalys/profil/hantering.py`:

```python
MAX_DECIMALER_VID_GRANS = 2  # metodval (spec 8.4.9 punkt 10)


def _andel_vid_grans(varde: float, grans: float) -> str:
    """Så många decimaler som behövs för att andelen ska hamna på rätt sida om gränsen (spec 8.4.9 punkt 10)."""
    procentgrans = round(grans * 100, 6)
    for decimaler in range(1, MAX_DECIMALER_VID_GRANS + 1):
        tal = round(varde * 100, decimaler)
        if tal != procentgrans and (tal < procentgrans) == (varde < grans):
            return f"{tal:.{decimaler}f}".replace(".", ",") + " %"
    return f"strax {'under' if varde < grans else 'över'} {round(grans * 100)} %"


def visa_varde_klartext(falt: Falt, varde: Any, granser: tuple[float, ...] = ()) -> str:
    """Som visa_varde, men en andel visas aldrig som 0 % eller 100 % när den inte är det (spec 8.4.9 punkt 7),
    och aldrig som en av metodens gränser när den inte är lika med gränsen (punkt 10)."""
    text = visa_varde(falt, varde)
    if falt.typ == "andel" and type(varde) in (int, float):
        if text == "0 %" and varde > 0:
            return "mindre än 1 %"
        if text == "100 %" and varde < 1:
            return "mer än 99 %"
        for grans in granser:
            if varde != grans and text == visa_varde(falt, grans):
                return _andel_vid_grans(varde, grans)
    return text
```

I `src/riskanalys/dokument/klartext.py`, importera `from riskanalys.regelverk.granser import metodgranser` och skicka med gränserna:
- I `uppgiftstext`: `visa_varde_klartext(regelbas.falt[falt_id], u.varde, metodgranser(regelbas, falt_id))`.
- I `gransmening`: `visa_varde_klartext(falt, profil.uppgifter[g.falt_id].varde, metodgranser(regelbas, g.falt_id))`.
- Gränsen själv visas oförändrat med `visa_varde(falt, g.grans)`.

I `src/riskanalys/dokument/underlag.py`, i `visa_for_ai`: `return visa_varde_klartext(falt, uppgift.varde, metodgranser(regelbas, falt_id))`. Maskeringen före den raden ändras inte, så skyddade värden förblir maskerade.

I `src/riskanalys/dokument/faktablad.py`:

```python
_INTERVALLVISNINGAR = ("mindre än ", "mer än ", "strax under ", "strax över ")
```

och i `_post` behålls den färdiga visningen för andelar, så att decimaler inte avrundas bort:

```python
    visning = ((u.varde if falt.typ == "andel" else visa_tal(tal)) if tal is not None else u.varde)
```

- [x] **Steg 4: Kör proven gröna**

Kör samma kommando som i steg 2, och dessutom `tester/intag/test_klartext.py` och `tester/intag/test_lasta_stycken.py`. Väntat utfall: alla passerar.

- [x] **Steg 5: Kör hela sviten**

Väntat utfall: allt grönt. Om `tester/typfall` eller `tester/enhet/test_m1_gyllene_dokument.py` faller enbart på grund av den nya visningen: ändra inte de filerna. Rapportera NEEDS_CONTEXT med diffen.

---

### Uppgift 4: STATUS och slutkontroll

**Filer:**
- Ändra: `docs/STATUS.md` (avsnittet "Skyddad AI-begäran, 2026-10-13", plus ett nytt kort stycke för 2026-10-14)

- [x] **Steg 1: Uppdatera STATUS**

I avsnittet om skyddad AI-begäran:
- Personnamn prövas bara lokalt efter tjänstens alla AI-anrop. En del med namn ersätts av mallen och ger ett blockerande fynd. Identitetsproven körs med profilens verkliga namn (spec 8.4.10 punkt 6 och 7).
- Smågruppsskyddade värden visas för AI som "skyddat värde, prövas lokalt" för både liten grupp och liten restgrupp (punkt 8).
- Andelar nära metodens gränser visas med tillräcklig precision, till exempel 19,5 % och 20,4 % mot 20 % (8.4.9 punkt 10). Ta bort Kvar-punkten om avrundning vid gräns.
- Rätta regelbasmeningen så att den säger att tillåtelselistan har fått 39 kategorifält för kontrollerna och en ny kontrollsumma (`sha256:12180a97…26c3d9`), medan regler, gränser och nivåer är oförändrade.
- Under Kvar: pilot på en tjänst med effort `medium` och ett uttryckligt kostnadstak, inklusive omförsök, efter användarens godkännande.
- Verifieringsraden får fullsvitens antal och tid efter uppgift 3.

- [x] **Steg 2: Slutkontroll**

Kör:
- `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest -q`
- `.venv/bin/riskanalys regelbas validera`, som ska vara oförändrad (`sha256:12180a97…26c3d9`)
- `git diff --check`

Inga commits.

## Genomförande 2026-10-14

Alla fyra uppgifter genomförda. Regressionstester kördes röda före kodändringarna och gröna efteråt. Uppgifterna granskades separat; slutgranskningen godkändes utan kvarstående fynd. Fullsvitens steg konsoliderades till en körning efter integration och slutgranskning: 1 433 passerade, ett livetest bortvalt, 683,92 s. Regelbasvalidering och diffkontroll är gröna. Skyddade jämförelsefiler, regelbas och motor är oförändrade mot arbetskopian vid start. Inga API-anrop, commits eller pushar. Befintligt index bevarat; denna plans ändringar ligger ostagade.

## Rättning efter eftergranskning, 2026-10-14

Användaren har begärt rättning av granskningsfynden. Denna omgång ersätter delsträngsmatchning med hela namn och genitiv från uttryckliga namnfält. Tidigare fri AI-text skickas inte vidare mellan delar. Härledda andelar med otillåtet antal eller otillåten bas maskeras i AI-underlaget, medan lokal precision behålls. Även decimalgränser och intagsvisning rättas. CLI, mätning och granskningsfynd redovisar lokala namnstopp med konkret åtgärd. Villkorsgenomgång och återanvändning av metodgränser ses över.

Regressioner körs röda före respektive kodrättning. Riktade tester följs av oberoende granskning och hela sviten. Skyddade jämförelsefiler ändras inte. Inga riktiga API-anrop, commits eller pushar.

Rättningsomgången verifierad: 1 461 passerade, ett livetest bortvalt, 699,99 s. Regelbasvalidering och diffkontroll gröna. Inga skyddade jämförelsefiler eller regelbasposter ändrade. Även fri text i återkoppling för felaktiga platshållare och fält-ID togs bort efter granskning och ett fallerande kedjeprov. Samtliga ändringar lämnas utan commit eller push.
