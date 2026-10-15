# Kedja, begränsad precision och namnfält: byggplan

> **För agenter:** OBLIGATORISK DELSKILL: använd superpowers:subagent-driven-development (rekommenderas) eller superpowers:executing-plans för att bygga planen uppgift för uppgift. Stegen använder kryssrutor (`- [x]`).

**Godkännande:** Användaren godkände 2026-10-14 att AI:s egen text får följa kedjan utan profilbekräftelse och att större antal, inklusive hela kundbasen, kan vara exakt härledbara. Godkännandet omfattar inte svagare smågruppsskydd.

**Mål:** Genomföra besluten från 2026-10-14:
- Kedjan mellan analysdelarna återställs med ett avgränsat beslut.
- De tillåtna kundandelarna visas åter för AI, men med begränsad precision, och ett prov redovisar vilka antal som går att härleda.
- Namnfält anges med en egenskap i regelbasen.
- Dessutom ett kedjeprov hela vägen till dokumentbygget, restgruppsprov som faktiskt prövar något, återanvänt gränsindex, felposition för platshållare och korrekt STATUS.

**Arkitektur:**
- `skriv_tjanst` skickar åter de godkända delsvarens text vidare i kedjan. Den lokala namnkontrollen körs som nu först efter alla anrop.
- `_skyddad_harledning` byts mot `_begransad_precision`. Den maskerar inte, utan låter `visa_for_ai` använda den nya visningsfunktionen `visa_andel_begransad`.
- `Falt` får `namnfalt`, som bara serialiseras när den är satt.

**Teknik:** Python 3.12/3.13, Pydantic, pytest, YAML-regelbas 1.3.0.

**Spec:** `docs/superpowers/specs/2026-10-08-riskanalys-design.md`, revision 22:
- 8.4.3 punkt 4 och stycket om platshållare
- 8.4.9 punkt 10–11
- 8.4.10 punkt 7–9

**Git:** inga commitsteg. Ändringarna lämnas ostagade. Den stageade versionen i indexet är läget före förra omgången och kan användas för att återställa enskilda prov (`git show :<sökväg>`).

## Genomförande

Uppgift 1–4 är implementerade med röda och gröna riktade prov. Härledningsprovet samlar de tre egenskaperna i ett prov för att undvika upprepad uppräkning (18,51 s inklusive hela begäran). Baslinjen skiljer avsiktligt hela kundbasen från avrundade nästan-100-procentvärden. Gränsindexet prövas även för hela dokumentet. Oberoende slutgranskning: inga åtgärdskrävande fynd. Fullsviten kördes samlat efter integration i stället för efter varje uppgift. Tre äldre testförväntningar rättades och omgranskades; ny fullsvit: 1 486 godkända, ett livetest bortvalt (708,62 s). Regelbasvalidering och diffkontroll är gröna; skyddade filer och index är bevarade. Inga commits eller stage-steg.

## Globala villkor

- AGENTS.md regel 1–8 gäller. Bara syntetiska data i proven, och inga riktiga API-anrop.
- Den utgående AI-begäran och antalet anrop får bara bero på det AI får se. Den lokala namnkontrollens resultat får aldrig påverka nästa anrop (spec 8.4.10 punkt 1, 7 och 9).
- Kedjan för bara vidare AI:s egen maskinellt validerade text. Inga namn eller andra profiluppgifter läggs till.
- Lägg inte fler antalsfält på tillåtelselistan.
- Den enda ändringen i regelbasen är `namnfalt: true` på `P-ROLL.ffr_namn` (uppgift 3). Den ger en ny kontrollsumma, som ska redovisas i STATUS.
- Tester före kod. Hela sviten ska vara grön: `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest -q`.
- Ändra inte `tester/typfall/` eller `tester/enhet/test_m1_gyllene_dokument.py`. Om något av dem faller: rapportera NEEDS_CONTEXT med diffen.

## Granskningsfokus

1. En andel exakt på gränsen (200 av 1 000) ska visas för AI som "minst 20 %", inte som "20 %". Annars avslöjar visningen att antalet är exakt 200. Provet finns i uppgift 2.
2. Andelen 100 av 100, alltså hela kundbasen, visas öppet som förut. Härledningsprovet ska godta det och inte behandla resten 0 som en liten restgrupp. Uppgift 2.
3. Ett namn i AI:s eget svar följer med i kedjan, men blir mall lokalt. Kedjans innehåll ska vara identiskt för profiler med olika namn. Uppgift 1.
4. Historiska regelbaser utan `namnfalt` ska ge samma kontrollsumma som förut. Uppgift 3.
5. Platshållarnas ordningsnummer räknar alla `{…}` i stycket, även rollplatshållare, så att numret stämmer med texten AI skrev. Uppgift 4.

---

### Uppgift 1: Kedjan återställs

**Filer:**
- Ändra: `src/riskanalys/dokument/delskrivning.py` (`skriv_del`, `skriv_tjanst`)
- Ändra: `src/riskanalys/dokument/promptar/delar.py` (modulen `risknivaer`)
- Prov: `tester/intag/test_delskrivning.py`, `tester/intag/test_skyddad_begaran.py`

**Gränssnitt:**
- `skriv_del(leverantor, fb, t, del_id, validerat: tuple[str, ...], *, effort, spara)`. Parametern `validerat` kommer tillbaka på sin gamla plats.

- [x] **Steg 1: Prov först**

Återställ `test_design_b_ett_anrop_per_del_och_kedjat_underlag` i `tester/intag/test_delskrivning.py` ur den stageade versionen (`git show :tester/intag/test_delskrivning.py`), och ta bort ersättaren `test_design_b_ett_anrop_per_del_med_oberoende_faktablad`.

I `tester/intag/test_skyddad_begaran.py`, ersätt `test_tidigare_ai_text_med_namn_skickas_aldrig_vidare` med:

```python
def test_kedjan_ar_identisk_for_olika_namn_och_paverkas_inte_av_namnkontrollen(rb_intag, klar):
    # Beslut 2026-10-14 (spec 8.4.10 punkt 9): AI:s egen text får följa med i kedjan, men den lokala
    # namnkontrollens resultat får aldrig påverka nästa anrop.
    anna, bertil = _anna_och_bertil(rb_intag, klar)
    anrop_anna, res_anna = _skriv_med_namn(rb_intag, anna, _svar_med_namn)
    anrop_bertil, res_bertil = _skriv_med_namn(rb_intag, bertil, _svar_med_namn)
    assert anrop_anna == anrop_bertil and len(anrop_anna) == len(DELAR)
    risknivaer = next(a for a in anrop_anna if a["del_id"] == "risknivaer")
    assert "Anna Svenssons arbetsrutin följs." in json.dumps(risknivaer, ensure_ascii=False)
    assert res_anna.del_("hot").lokal_sparr == "personnamn" and res_bertil.del_("hot").lokal_sparr is None


def test_kedjan_innehaller_bara_godkand_ai_text(rb_intag, klar):
    anrop, res = _skriv_med_namn(rb_intag, klar, lambda t: [godkant_delsvar(d, t) for d in DELAR])
    def text(*ids):
        return "\n\n".join(s.text for id in ids for s in res.del_(id).godkant_svar.stycken)
    innehall = {a["del_id"]: json.dumps(a, ensure_ascii=False) for a in anrop}
    assert json.dumps(text("hot", "sarbarheter", "kontroller"), ensure_ascii=False)[1:-1] in innehall["risknivaer"]
    assert json.dumps(text("risknivaer"), ensure_ascii=False)[1:-1] in innehall["slutsatser"]
    assert "Testa Testsson" not in innehall["risknivaer"] + innehall["slutsatser"]
```

Om blocket i `bygg_innehall` fogar ihop texterna på något annat sätt än med `"\n\n"`, anpassa förväntan till det sätt som `meddelande.py` använder, och nämn det i rapporten.

- [x] **Steg 2: Kör proven och se dem fallera**

Kör: `.venv/bin/pytest -q tester/intag/test_delskrivning.py tester/intag/test_skyddad_begaran.py`

Väntat utfall: kedjeproven faller, eftersom risknivå- och slutsatsdelarna saknar tidigare text.

- [x] **Steg 3: Implementera**

I `skriv_tjanst`:
- Återställ `validerad(*ids)`. Den läser `delar[id].godkant_svar` ur resultaten från slingan, alltså **före** `_utan_personnamn`.
- Underlaget blir `validerad("hot", "sarbarheter", "kontroller")` för `risknivaer`, `validerad("risknivaer")` för `slutsatser` och `()` för övriga delar.
- Skicka det som `validerat` till `skriv_del`, och därifrån till `bygg_innehall(fb, del_id, lasta, validerat, aterkoppling)`.
- `_utan_personnamn` körs som nu först i `return`.

Ersätt kommentaren om att fri AI-text aldrig skickas vidare med:

```python
    # Kedjan för bara vidare AI:s egen maskinellt validerade text (spec 8.4.10 punkt 9). Namnkontrollen körs
    # först efter alla anrop, så att dess resultat aldrig påverkar nästa anrop.
```

I modulen `risknivaer` i `promptar/delar.py`, återställ meningen "Använd de maskinellt validerade delarna som underlag och upprepa dem inte." i stället för "Använd faktabladets strukturerade uppgifter som underlag." Hämta den ordagrant ur den stageade versionen.

- [x] **Steg 4: Kör proven gröna, och därefter hela sviten**

---

### Uppgift 2: Begränsad precision för kundandelar, härledningsprov och restgruppsprov

**Filer:**
- Ändra: `src/riskanalys/profil/hantering.py` (ny `visa_andel_begransad`)
- Ändra: `src/riskanalys/dokument/underlag.py` (`_skyddad_harledning` blir `_begransad_precision`; ändringar i `visa_for_ai`, `_uppgift` och `provas_lokalt`)
- Ändra: `src/riskanalys/dokument/faktablad.py` (`_INTERVALLVISNINGAR`)
- Prov: skapa `tester/intag/test_harledbara_antal.py`; ändra `tester/intag/test_faktablad.py`, `tester/intag/test_skyddad_begaran.py` och `tester/enhet/test_andel_vid_grans.py`

**Gränssnitt:**
- Producerar: `visa_andel_begransad(falt: Falt, varde: float, granser: tuple[float, ...]) -> str` i `hantering`.
- Producerar: `_begransad_precision(regelbas: Regelbas, falt_id: str) -> bool` i `underlag`, med samma villkor som `_skyddad_harledning` har i dag.

- [x] **Steg 1: Prov först**

I `tester/enhet/test_andel_vid_grans.py`:

```python
from riskanalys.profil.hantering import visa_andel_begransad


@pytest.mark.parametrize(("varde", "vantat"), [
    (0.195, "strax under 20 %"), (0.1999, "strax under 20 %"), (0.2, "minst 20 %"), (0.204, "minst 20 %"),
    (0.205, "minst 20 %"), (0.2051, "21 %"), (0.1949, "19 %"), (0.33, "33 %"),
    (0.003, "mindre än 1 %"), (0.997, "mer än 99 %"),
])
def test_begransad_andel_visar_hela_procent_och_bara_sidan_vid_grans(andel, varde, vantat):
    assert visa_andel_begransad(andel, varde, (0.2,)) == vantat
```

Skapa `tester/intag/test_harledbara_antal.py`. Det räknar ut vilka antal i riskbranscher som går att härleda ur AI-visningen och den tillåtna kundbasen:

```python
from collections import defaultdict

from riskanalys.dokument.underlag import SKYDDAD_VISNING, SMA_GRUPPER_GRANS, _uppgift
from riskanalys.profil.hantering import visa_varde
from riskanalys.profil.omfattning import kompatibilitetsvy
from riskanalys.regelverk.granser import metodgranser

ANDEL = "P-KUND.andel_riskbransch"
BASER = (20, 50, 100, 150, 199, 200, 250, 399, 401, 1000)


def _visningar(rb, klar, bas):
    from tester.intag.test_faktablad import _kundbas
    return {antal: _uppgift(rb, kompatibilitetsvy(_kundbas(rb, klar, bas, antal), rb), ANDEL).varde
            for antal in range(bas + 1)}


def _grupper(nycklar: dict) -> dict:
    grupper = defaultdict(set)
    for antal, nyckel in nycklar.items():
        grupper[nyckel].add(antal)
    return grupper


def _synliga(visningar):
    return {a: v for a, v in visningar.items() if v != SKYDDAD_VISNING}


def test_sma_grupper_och_sma_restgrupper_gar_aldrig_att_harleda(rb_intag, klar):
    for bas in BASER:
        for visning, antal in _grupper(_synliga(_visningar(rb_intag, klar, bas))).items():
            # Hela kundbasen (rest 0) visas öppet med avsikt.
            assert all(a >= SMA_GRUPPER_GRANS and (bas - a >= SMA_GRUPPER_GRANS or a == bas) for a in antal), (bas, visning)


def test_visningen_avslojar_inte_mer_an_hela_procent_och_sidan_om_gransen(rb_intag, klar):
    falt, granser = rb_intag.falt[ANDEL], metodgranser(rb_intag, ANDEL)
    for bas in BASER:
        synliga = _synliga(_visningar(rb_intag, klar, bas))
        per_visning = _grupper(synliga)
        baslinje = _grupper({a: (visa_varde(falt, a / bas), tuple(a / bas >= g for g in granser)) for a in synliga})
        for antal in synliga:
            samma_baslinje = next(g for g in baslinje.values() if antal in g)
            assert samma_baslinje <= per_visning[synliga[antal]], (bas, antal)


def test_exakt_harledbara_antal_redovisas_per_provbas(rb_intag, klar):
    exakta = {(bas, next(iter(antal))) for bas in BASER
              for antal in _grupper(_synliga(_visningar(rb_intag, klar, bas))).values() if len(antal) == 1}
    assert exakta, "provet ska visa att små kundbaser kan ge exakt härledbara antal"
    hela = {(bas, antal) for bas, antal in exakta if antal == bas}
    ovriga = exakta - hela
    assert hela == {(bas, bas) for bas in BASER}
    assert ovriga
    # Redovisa uppmätta resultat per provbas, inte en generell 400-gräns.
```

Utöver andelsprovet ska hela serialiserade AI-begäran (faktabladets andra antal, gränsmeningar, sårbarhetsutfall, schema, kedja och återkoppling) jämföras för skyddade små grupper och restgrupper, med samma syntetiska AI-svar. Testa också att 90 av 100 visas öppet. Rapportera exakta antal och största provbas separat för hela kundbasen respektive övriga; ungefärliga 200/400-gränser är inte garantier.

Om `_kundbas` inte går att importera från `test_faktablad`: flytta den till `tester/fixturer/` och importera den därifrån i båda filerna. Om filen tar mer än 30 sekunder: räkna ut visningarna en gång per bas och pröva alla tre egenskaperna i ett och samma prov.

I `tester/intag/test_faktablad.py`, ändra proven från förra omgången (`test_harledd_andel_skyddas_nar_en_komponent_inte_ar_tillaten`, `test_standardregelbas_doljer_195_men_lokal_visning_bevarar_precision`, `test_hela_kundbasen_visas_nar_bada_komponenter_ar_tillatna`, `test_dolt_antal_195_och_204_ger_samma_hela_begaran_med_omforsok`, `test_195_av_1000_…` och `test_204_av_1000_…`) så att de kräver följande:
- **195 av 1 000:** AI ser "strax under 20 %" (intervall, inget tal), och AI:s gränsmening säger "är strax under 20 %, men det ligger under metodens gräns på 20 %". Lokalt står "19,5 %" i gränsmeningen och i `uppgiftstext`.
- **200 och 204 av 1 000:** AI ser "minst 20 %". Lokalt står "20 %" respektive "20,4 %".
- **195 och 199 av 1 000** ger identisk hel begäran, även vid omförsök. Det gäller också **200 och 205 av 1 000**.
- **Annars:** en tillåten kundandel visas för AI i hela procent, till exempel 330 av 1 000 som "33 %", och dess bas visas som förut.
- **När både antal och bas är tillåtna** (P-GEO.* och P-TJ.*) visar AI decimaler som i punkt 10.

I `tester/intag/test_skyddad_begaran.py`:
- Byt namn på `test_hela_kundbasen_med_otillaten_taljare_skyddas` tillbaka till `test_hela_kundbasen_visas_oppet`, med förväntan "100 %".
- Lägg till restgruppsprov på ett fält där värdet annars visas:

```python
def test_restgrupp_pa_falt_som_annars_visas_ger_samma_begaran(tmp_path, rb_intag, klar):
    # Kontroll: 90 av 100 visas öppet, så att provet inte går igenom på en maskering som alltid gäller.
    oppen = _med(rb_intag, klar, {"P-GEO.antal_utland_transaktion": 90})
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, oppen)
    post = next(p for p in bygg_faktablad(rb_intag, oppen, t, avsnitt_id).poster if p.id == "P-GEO.andel_utland_transaktion")
    assert post.visningsvarde == "90 %"
    assert _lika(rb_intag, [_med(rb_intag, klar, {"P-GEO.antal_utland_transaktion": n}) for n in (96, 97, 99)])
    assert _lika(rb_intag, [_med(rb_intag, klar, {"P-GEO.antal_utland_transaktion": n}) for n in (3, 97)])
```

Om `P-GEO.andel_utland_transaktion` inte finns i faktabladet för provtjänsten, använd ett annat fält där både antal och bas är tillåtna (till exempel `P-TJ.red01_antal_kunder`) och nämn det i rapporten.

- [x] **Steg 2: Kör proven och se dem fallera**

Kör: `.venv/bin/pytest -q tester/enhet/test_andel_vid_grans.py tester/intag/test_harledbara_antal.py tester/intag/test_faktablad.py tester/intag/test_skyddad_begaran.py`

Väntat utfall:
- ImportError för `visa_andel_begransad`.
- Därefter faller proven för visningen och härledningen, eftersom kundandelarna i dag alltid maskeras.

- [x] **Steg 3: Implementera**

I `hantering.py`:

```python
HALV_PROCENTENHET = Decimal("0.5")  # metodval (spec 8.4.9 punkt 11)


def visa_andel_begransad(falt: Falt, varde: float, granser: tuple[float, ...]) -> str:
    """Andel för AI när dess antal eller bas inte är tillåtna: hela procent, och nära en metodgräns bara sidan
    om gränsen (spec 8.4.9 punkt 11). Lokala texter behåller decimalerna."""
    text = visa_varde(falt, varde)
    if text == "0 %" and varde > 0:
        return "mindre än 1 %"
    if text == "100 %" and varde < 1:
        return "mer än 99 %"
    procent = Decimal(str(varde)) * 100
    for grans in granser:
        if abs(procent - Decimal(str(grans)) * 100) <= HALV_PROCENTENHET:
            return f"{'strax under' if varde < grans else 'minst'} {visa_grans(falt, grans)}"
    return text
```

`Decimal` importeras överst i modulen. Ta samtidigt bort de lokala `from decimal import Decimal` i `visa_grans` och `visa_varde_klartext`.

I `underlag.py`:
- Byt namn på `_skyddad_harledning` till `_begransad_precision` och ändra docstringen till "En andel vars antal eller bas inte är tillåtna visas för AI med begränsad precision (spec 8.4.9 punkt 11).".
- `visa_for_ai`: smågruppsskyddet först, som före förra omgången. Därefter `if _begransad_precision(regelbas, falt_id): return visa_andel_begransad(falt, uppgift.varde, metodgranser(regelbas, falt_id, gransindex))`, och annars `visa_varde_klartext(...)` som nu.
- `_uppgift`: ta bort `and not _skyddad_harledning(regelbas, falt_id)` ur `visa_bas`, så att basen visas som förut.
- `provas_lokalt`: återställ villkoret till `if regelbas.falt[falt_id].smagrupp:`.

I `faktablad.py`: `_INTERVALLVISNINGAR = ("mindre än ", "mer än ", "strax under ", "strax över ", "minst ")`.

- [x] **Steg 4: Kör proven gröna, och därefter hela sviten**

Skriv i rapporten vilka par av bas och antal som `test_exakt_harledbara_antal_redovisas_per_provbas` hittade, samt den största basen. Det ska in i STATUS.

---

### Uppgift 3: Namnfält som egenskap i regelbasen

**Filer:**
- Ändra: `src/riskanalys/regelverk/modeller.py` (`Falt`)
- Ändra: `regelbas/falt.yaml` (`P-ROLL.ffr_namn`)
- Ändra: `src/riskanalys/profil/hantering.py` (`personnamn`)
- Prov: skapa `tester/regelkontrakt/test_namnfalt.py`

- [x] **Steg 1: Prov först**

```python
import pytest

from riskanalys.profil.hantering import personnamn
from riskanalys.regelverk.laddning import ladda_regelbas
from riskanalys.regelverk.modeller import Falt


def test_ffr_namn_ar_namnfalt_och_alla_namnfalt_ar_personuppgifter_av_typen_text():
    rb = ladda_regelbas()
    assert rb.falt["P-ROLL.ffr_namn"].namnfalt
    assert all(f.personuppgift and f.typ == "text" for f in rb.falt.values() if f.namnfalt)
    assert not rb.falt["P-ROLL.ansvarsfunktion"].namnfalt


def test_namnfalt_serialiseras_bara_nar_det_ar_satt():
    bas = dict(id="P-X.namn", typ="text", fraga="Namn?", varfor="Prov.", personuppgift=True)
    assert "namnfalt" not in Falt(**bas).model_dump()
    assert Falt(**bas, namnfalt=True).model_dump()["namnfalt"] is True


def test_namnfalt_kraver_personuppgift_av_typen_text():
    with pytest.raises(ValueError):
        Falt(id="P-X.n", typ="heltal", fraga="?", varfor="Prov.", personuppgift=True, namnfalt=True)


def test_personnamn_foljer_egenskapen_inte_ett_hardkodat_id(rb_intag, klar):
    falt = rb_intag.falt["P-ROLL.ansvarsfunktion"].model_copy(update={"namnfalt": True})
    rb = rb_intag.model_copy(update={"falt": {**rb_intag.falt, falt.id: falt}})
    profil = klar.model_copy(update={"uppgifter": {**klar.uppgifter, falt.id: klar.uppgifter["P-ROLL.ffr_namn"].model_copy(update={"varde": "Cecilia Ek"})}})
    assert "Cecilia Ek" in personnamn(profil, rb)
```

Om `rb_intag` och `klar` inte finns som fixturer i `tester/regelkontrakt/`, lägg provet `test_personnamn_foljer_…` i `tester/intag/test_skyddad_begaran.py` i stället. Om `Falt` validerar med `pydantic.ValidationError`, räcker det eftersom den ärver från `ValueError`.

- [x] **Steg 2: Kör proven och se dem fallera**

Kör: `.venv/bin/pytest -q tester/regelkontrakt/test_namnfalt.py`

Väntat utfall: fel om okänt fält, eller faller på att `namnfalt` saknas.

- [x] **Steg 3: Implementera**

I `Falt`:

```python
    namnfalt: bool = False  # Fältet innehåller ett personnamn som prövas lokalt (spec 8.4.10 punkt 7).
```

I `serialisera`, efter etikettraden: `if not self.namnfalt: data.pop("namnfalt", None)`. Ändra docstringen till "Utelämna saknat kortnamn och osatt namnfält, så att historiska innehålls- och attestsummor består.".

Lägg till en validator efter modellens:

```python
    @model_validator(mode="after")
    def _namnfalt_ar_personuppgift(self):
        if self.namnfalt and not (self.personuppgift and self.typ == "text"):
            raise ValueError(f"{self.id}: ett namnfält måste vara en personuppgift av typen text.")
        return self
```

Om `Falt` redan har en `model_validator`, lägg kontrollen i den.

I `regelbas/falt.yaml`, under `P-ROLL.ffr_namn`: `namnfalt: true`, med kommentaren `# Namnfält som prövas lokalt i AI-text; beslut 2026-10-14, spec 8.4.10 punkt 7.`.

I `personnamn()`: byt `falt_id == "P-ROLL.ffr_namn"` mot `regelbas.falt[falt_id].namnfalt`. Ordningen ska vara `falt_id in regelbas.falt and regelbas.falt[falt_id].namnfalt and ...`. Ändra docstringen till "Bekräftade värden i regelbasens namnfält (`namnfalt`); ansvarsfunktionens rolltext är inte ett namn.".

- [x] **Steg 4: Kör proven gröna, och därefter hela sviten**

Kör `.venv/bin/riskanalys regelbas validera` och skriv den nya kontrollsumman i rapporten. Proven mot frysta kontrollsummor ska vara gröna utan att ändras.

---

### Uppgift 4: Kedjeprov till dokumentbygget, felposition för platshållare och återanvänt gränsindex

**Filer:**
- Ändra: `src/riskanalys/dokument/platshallare.py` (`platshallarfel`, `faltid_fel`)
- Ändra: `src/riskanalys/dokument/klartext.py` (`uppgiftstext` och `gransmening` får `gransindex`)
- Ändra: anroparna i dokumentbygget, enligt steg 3
- Prov: `tester/intag/test_lokal_sparr_rapportering.py`, `tester/enhet/test_delvalidering.py` eller en ny `tester/enhet/test_platshallare_position.py`

- [x] **Steg 1: Prov först**

Kedjeprov i `tester/intag/test_lokal_sparr_rapportering.py`. Ett namn i AI:s svar ska följas från skrivningen till granskningens blockerande fynd och dokumentets mall:

```python
def test_namnstopp_hela_vagen_till_dokument_och_blockerande_fynd(tmp_path, rb_intag, klar):
    spara_profil(tmp_path, klar)
    bedomning = las_bedomning(kor_bedomning(tmp_path, rb_intag))
    svar = bygg_delsvar(rb_intag, klar, bedomning)
    hot = svar[0]
    svar[0] = hot.model_copy(update={"stycken": [hot.stycken[0].model_copy(update={
        "text": "Testa Testssons rutin följs. " + hot.stycken[0].text}), *hot.stycken[1:]]})
    kor_skrivning(tmp_path, rb_intag, Testleverantor(svar))
    dokument, fynd = las_granskning(kor_granskning(tmp_path, rb_intag, DAG))
    namnfynd = [f for f in fynd if "innehöll ett bekräftat personnamn" in f.beskrivning]
    assert len(namnfynd) == 1 and namnfynd[0].allvar == "blockerande"
    assert all("Testa Testssons rutin" not in s.text for a in dokument.avsnitt for s in a.stycken)
```

Följ mönstret i `tester/enhet/test_granskning_korning.py` för `DAG`, och för det som granskningen kräver innan den kan köras, till exempel en registrerad utvärdering. Kontrollera att `bygg_delsvar` ger hotdelen för första tjänsten först. Annars, välj ut den via `DELAR`.

Felposition utan citat:

```python
def test_aterkopplingen_anger_platshallarens_nummer_men_citerar_inte(faktablad_exempel):
    fel = platshallarfel(1, "Text {roll:FfR} och {Anna Svensson} samt {tal:OKAND}.", [], faktablad_exempel.numeriska())
    assert any("platshållare nummer 2" in f for f in fel) and any("platshållare nummer 3" in f for f in fel)
    assert all("Anna" not in f and "OKAND" not in f for f in fel)
```

Lägg ett motsvarande prov för `faltid_fel` med två fält-ID, som ska ge "fält-ID nummer 1" och "nummer 2" utan att ID:na citeras.

Prov för gränsindexet: ersätt `riskanalys.regelverk.granser.metodgransindex` med en räknande omslagsfunktion via `monkeypatch`. Den fångar varje omräkning som sker när `metodgranser` anropas utan index. Bygg sedan ett tjänsteavsnitt med `bygg_tjanstavsnitt_v3`, med fixturen `v3` i `tester/intag/test_v3_grind.py`, och kräv att räknaren visar högst 1.

- [x] **Steg 2: Kör proven och se dem fallera**

- [x] **Steg 3: Implementera**

I `platshallarfel`, numrera alla `{…}` i stycket med `for nr, traff in enumerate(_KLAMMER.finditer(text), 1)`, även rollplatshållare. Meddelandena blir:
- "Stycke {nummer}: platshållare nummer {nr} är inte tillåten. Tillåtna är {{tal:ID}}, {{period:ID}} och {{roll:FfR}}."
- "Stycke {nummer}: platshållare nummer {nr} har ett okänt eller skyddat värde. Använd bara {typ}-ID som finns i faktabladet."
- "Stycke {nummer}: platshållare nummer {nr} saknar sitt ID bland styckets referenser."

I `faltid_fel`, numrera de unika ID:na i den ordning de förekommer: "Stycke {nummer}: fält-ID nummer {k} i löptexten ska bort. Lägg ID:n i referenser och skriv klartext."

Gränsindexet:
- `uppgiftstext(..., gransindex: dict | None = None)` och `gransmening(..., gransindex: dict | None = None)` skickar det vidare till `metodgranser(regelbas, falt_id, gransindex)`.
- `bygg_tjanstavsnitt_v3` och övriga byggare av avsnitt räknar ut `metodgransindex(rb)` en gång och skickar ned det via ett nyckelordsargument `gransindex`. Det gäller `analysunderlag` (sårbarhets-, erfarenhets- och beläggstycken), `tjanstavsnitt`, `intagsunderlag` och `uppfoljning`.
- Intagsvyn (`vyer.py:71`) räknar ut indexet en gång per vy, som rad 131 redan gör.

- [x] **Steg 4: Kör proven gröna, och därefter hela sviten**

---

### Uppgift 5: STATUS och slutkontroll

- [x] **Steg 1: Uppdatera `docs/STATUS.md`**

Avsnittet för 2026-10-14 ska ange följande:
- **Kedjan** är återställd med det avgränsade beslutet: AI:s egen validerade text följer med, och namnkontrollen påverkar aldrig nästa anrop. Ett namn som AI själv skrivit kan skickas tillbaka till AI, utan att programmet bekräftar att det finns i profilen.
- **Tillåtna kundandelar** visas åter för AI: hela procent, och "strax under" eller "minst" vid en metodgräns. Lokala texter har decimaler.
- **Härledningsprovets resultat:** vilka baser som gav exakt härledbara antal, och den största basen. Hela kundbasen redovisas separat. Testerna styrker skyddet inom prövade profiler och baser, inte för varje möjlig kombination av uppgifter.
- **Sårbarheter som prövas lokalt:** rätta raden om de fem sårbarheterna, så att den stämmer med beteendet efter uppgift 2.
- **Namnfält:** `namnfalt` på `P-ROLL.ffr_namn`, och regelbasens nya kontrollsumma (gamla och nya). Bedömningar som gjorts före ändringen är inaktuella.
- **Återkopplingen** om platshållare och fält-ID anger ordningsnummer utan att citera.
- **Verifieringsraden:** fullsvitens antal och tid.

- [x] **Steg 2: Slutkontroll**

Kör:
- `env -u ANTHROPIC_API_KEY -u RISKANALYS_SCB_API_KEY .venv/bin/pytest -q`
- `.venv/bin/riskanalys regelbas validera`
- `git diff --check`

Inga commits.
