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


def test_flervalsfalt_laddas_och_validerar(tmp_path, skriv_minimal_regelbas, minimal_filer):
    falt = minimal_filer["falt.yaml"]
    falt.append({"id": "P-TJ.T-1_iakttagna_hot", "typ": "flerval", "fraga": "Vilka hot har iakttagits?",
                 "varfor": "Test.", "val": ["H-1"]})
    rot = skriv_minimal_regelbas(tmp_path / "rb", {"falt.yaml": falt})
    rb = ladda_regelbas(rot)
    assert rb.falt["P-TJ.T-1_iakttagna_hot"].typ == "flerval"
    assert validera(rb) == []


def test_flervalsfalt_utan_alternativ_kan_inte_laddas(tmp_path, skriv_minimal_regelbas, minimal_filer):
    import pytest

    from riskanalys.regelverk.laddning import RegelbasFel

    falt = minimal_filer["falt.yaml"]
    falt.append({"id": "P-X", "typ": "flerval", "fraga": "Vilka?", "varfor": "Test."})
    rot = skriv_minimal_regelbas(tmp_path / "rb", {"falt.yaml": falt})
    with pytest.raises(RegelbasFel, match="flerval"):
        ladda_regelbas(rot)
