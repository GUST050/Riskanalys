"""H1/H2: syntetiskt underlag genom motor, AI-gräns och dokumentgranskning.

Nya dokument byggs i D-ARB-tjanst-v6 (två AI-delar via Testleverantor). Prov som bara
gäller motorn eller AI-underlaget bygger inget dokument. Historisk v5-verifiering prövas
uttryckligen med bygg_arb_v5.
"""

import pytest

from riskanalys.dokument.underlag import SKYDDAD_VISNING, bygg_underlag, tjanster_med_avsnitt
from tester.fixturer.arb_kedja import (
    ai_begaran, andrat, bedom_kedja, granska_kedja, med_avsnitt, syntetisk_profil, v5_kedja, v6_kedja,
)
from tester.fixturer.m2 import PERIOD

RAPPORTER = "P-VERK.antal_rapporter"
AVBOJANDEN = "P-VERK.antal_avbojanden"
HEMLIGT = ("HEMLIG_KALLA", "HEMLIG_PERSON", "LOKAL_HEMLIG_ERFARENHET")
OBELAGDA = [
    {"status": "saknas"}, {"inaktuell": True}, {"kalla": None}, {"datum": None},
    {"bekraftad_av": None}, {"period": None}, {"varde": -1},
]


@pytest.fixture
def profil(regelbas_v1):
    return syntetisk_profil(regelbas_v1)


def blockerade_avsnitt(fynd):
    return {f.avsnitt for f in fynd if f.allvar == "blockerande"}


@pytest.mark.parametrize("antal,status", [(0, "inga"), (3, "finns"), (12, "finns")])
def test_motorn_beaktar_egen_rapportering_utan_att_gora_antal_till_riskpoang(regelbas_v1, profil, antal, status):
    _, bas = bedom_kedja(regelbas_v1, profil)
    _, b = bedom_kedja(regelbas_v1, andrat(profil, RAPPORTER, varde=antal))
    erbjudna = [t for t in b.tjanster if t.erbjuds]
    assert all(t.egen_erfarenhet.rapporter == status and t.egen_erfarenhet.belagd for t in erbjudna)
    assert [t.inneboende for t in b.tjanster] == [t.inneboende for t in bas.tjanster]
    assert all(t.egen_erfarenhet is None for t in b.tjanster if t.erbjuds is False)


@pytest.mark.parametrize("uppdatering", OBELAGDA)
def test_obelagd_rapportering_ar_okand_och_ger_b15(regelbas_v1, profil, uppdatering):
    p = andrat(profil, RAPPORTER, **uppdatering)
    k = v6_kedja(regelbas_v1, p)
    assert all(t.egen_erfarenhet.rapporter == "saknas" for t in k.bedomning.tjanster if t.erbjuds)
    fynd = granska_kedja(regelbas_v1, k, p)
    # V6 blockerar varje erbjuden tjänsts avsnitt när erfarenhetsbelägget saknas ...
    assert {id for id, _ in tjanster_med_avsnitt(k.bedomning)} <= blockerade_avsnitt(fynd)
    # ... och fyndet ska bära regelbasens automatiserade bristmönster B-15.
    assert any(f.regel == "B-15" for f in fynd), "V6-granskningen märker inte fyndet med B-15."


@pytest.mark.parametrize("uppdatering", OBELAGDA)
def test_historisk_v5_verifiering_ger_b15_for_obelagd_rapportering(regelbas_v1, profil, uppdatering):
    # Historiska v5-paket verifieras fortfarande med B-15 (granskning/dokument_v5.py).
    p = andrat(profil, RAPPORTER, **uppdatering)
    k = v5_kedja(regelbas_v1, p)
    assert k.dokument.formatversion == "D-ARB-tjanst-v5"
    assert any(f.regel == "B-15" and f.allvar == "blockerande" for f in granska_kedja(regelbas_v1, k, p))


def test_ai_far_skyddade_antal_men_inte_kalla_namn_eller_fritext(regelbas_v1, profil):
    p = andrat(profil, RAPPORTER, varde=3, kalla="HEMLIG_KALLA", bekraftad_av="HEMLIG_PERSON")
    p = andrat(p, "P-BESK.erfarenheter", varde="LOKAL_HEMLIG_ERFARENHET")
    _, b = bedom_kedja(regelbas_v1, p)
    for id, t in tjanster_med_avsnitt(b):
        underlag = bygg_underlag(regelbas_v1, p, t, id)
        uppgifter = {v.id: v for v in underlag.uppgifter}
        assert uppgifter[RAPPORTER].varde == SKYDDAD_VISNING
        assert uppgifter[AVBOJANDEN].period == (str(PERIOD.fran), str(PERIOD.till))
        assert all(text not in underlag.model_dump_json() for text in HEMLIGT)
    # V6: faktabladet och de två faktiska delanropen per tjänst.
    k = v6_kedja(regelbas_v1, p)
    for r in k.resultat.values():
        assert next(x for x in r.faktablad.poster if x.id == RAPPORTER).status == "skyddad"
    assert k.delanrop and all(text not in ai_begaran(k) for text in HEMLIGT)


def test_rapportantalets_intagskoppling_ar_hot(regelbas_v1):
    assert regelbas_v1.falt[RAPPORTER].intag.avsnitt == ("D-ARB.4",)
    assert regelbas_v1.falt[AVBOJANDEN].intag.avsnitt == ("D-ARB.4",)
    assert regelbas_v1.bristmonster["B-15"].automatiserad


def test_hotanalysen_beaktar_noll_och_erfarenheter_per_tjanst(regelbas_v1, profil):
    # V6: varje erbjuden tjänsts eget analysavsnitt ska bära programmets låsta
    # erfarenhetsstycke, oavsett vad AI-delen hot skriver.
    k = v6_kedja(regelbas_v1, profil)
    avsnitt = k.dokument.avsnitt_med_id()
    for id, t in tjanster_med_avsnitt(k.bedomning):
        analys = [s for s in avsnitt[id].stycken if {t.tjanst, RAPPORTER, AVBOJANDEN} <= set(s.referenser)]
        assert len(analys) == 1, f"{id}: tjänstavsnittet saknar det låsta erfarenhetsstycket."
        assert "Noll rapporter" in analys[0].text
        assert "inte frånvaro av hot" in analys[0].text
        assert str(PERIOD.fran) in analys[0].text


def test_b15_hittar_borttagen_analys_trots_att_antal_finns_i_dokumentet(regelbas_v1, profil):
    k = v6_kedja(regelbas_v1, profil)
    # Antalen finns kvar i dokumentet: v6 redovisar dem i bilaga B1.
    assert any(RAPPORTER in s.referenser for s in k.dokument.avsnitt_med_id()["D-ARB.B1"].stycken)
    id, _ = tjanster_med_avsnitt(k.bedomning)[0]
    a = k.dokument.avsnitt_med_id()[id]
    kvar = tuple(s for s in a.stycken if not {RAPPORTER, AVBOJANDEN} <= set(s.referenser))
    assert len(kvar) < len(a.stycken), f"{id}: erfarenhetsanalysen som B-15 skyddar finns inte i v6-avsnittet."
    nytt = med_avsnitt(k.dokument, a.model_copy(update={"stycken": kvar}))
    fynd = [f for f in granska_kedja(regelbas_v1, k, profil, nytt) if f.regel == "B-15"]
    assert len(fynd) == 1


def test_sarbarhet_motiveras_med_villkor_varde_period_och_kalla(regelbas_v1, profil):
    # V6: för varje tjänst med S-GEO-01 ska tjänstavsnittet ha programmets låsta
    # geografimotivering bredvid AI-delen sårbarheter (tidigare prövat för första tjänsten
    # här och för alla tjänster i docx-provet).
    k = v6_kedja(regelbas_v1, profil)
    avsnitt = k.dokument.avsnitt_med_id()
    provade = 0
    for id, t in tjanster_med_avsnitt(k.bedomning):
        if "S-GEO-01" not in regelbas_v1.tjanster[t.tjanst].sarbarheter:
            continue
        provade += 1
        geo = [s for s in avsnitt[id].stycken if "S-GEO-01" in s.referenser]
        assert all("inga geografiska risker" not in s.text.lower() for s in geo)
        motiverade = [s for s in geo if "Sårbarheten gäller om" in s.text]
        assert len(motiverade) == 1, f"{id}: tjänstavsnittet saknar låst motivering av S-GEO-01."
        stycke = motiverade[0]
        assert "0 %" in stycke.text
        assert str(PERIOD.fran) in stycke.text and "Syntetisk testkälla" in stycke.text
        assert "P-BESK.geografi" in stycke.referenser
    assert provade


@pytest.mark.parametrize("fel", ["omotiverat", "felvarde", "felreferenser", "saknas"])
def test_geografi_utan_riktig_underlagsmotivering_blockeras(regelbas_v1, profil, fel):
    k = v6_kedja(regelbas_v1, profil)
    id, _ = tjanster_med_avsnitt(k.bedomning)[0]
    a = k.dokument.avsnitt_med_id()[id]
    stycken = []
    for s in a.stycken:
        if "S-GEO-01" in s.referenser:
            if fel == "saknas":
                continue
            text = "Gäller inte enligt byråns uppgifter." if fel == "omotiverat" else s.text + " Felaktigt tillägg."
            refs = ["S-GEO-01"] if fel == "felreferenser" else s.referenser
            s = s.model_copy(update={"text": text, "referenser": refs})
        stycken.append(s)
    nytt = med_avsnitt(k.dokument, a.model_copy(update={"stycken": tuple(stycken)}))
    fynd = granska_kedja(regelbas_v1, k, profil, nytt)
    # V6 återbygger avsnittet och blockerar varje avvikelse ...
    assert a.id in blockerade_avsnitt(fynd)
    # ... och ska märka den saknade eller felaktiga geografimotiveringen som B-10.
    b10 = [f for f in fynd if f.regel == "B-10"]
    assert b10 and all(f.allvar == "blockerande" for f in b10), "V6-granskningen ger inget B-10-fynd."


def test_obekraftad_geografibeskrivning_ger_b09(regelbas_v1, profil):
    p = andrat(profil, "P-BESK.geografi", inaktuell=True)
    k = v6_kedja(regelbas_v1, p)
    fynd = granska_kedja(regelbas_v1, k, p)
    assert {id for id, _ in tjanster_med_avsnitt(k.bedomning)} <= blockerade_avsnitt(fynd)
    assert any(f.regel == "B-09" and f.allvar == "blockerande" for f in fynd), "V6-granskningen märker inte fyndet med B-09."


def test_historisk_v5_verifiering_ger_b09_for_obekraftad_geografi(regelbas_v1, profil):
    p = andrat(profil, "P-BESK.geografi", inaktuell=True)
    k = v5_kedja(regelbas_v1, p)
    assert any(f.regel == "B-09" and f.allvar == "blockerande" for f in granska_kedja(regelbas_v1, k, p))


def test_ai_sarbarhetsmotivering_skyddar_sma_grupper(regelbas_v1, profil):
    p = andrat(profil, "P-GEO.antal_utland_transaktion", varde=2, kalla="HEMLIG_KALLA")
    _, b = bedom_kedja(regelbas_v1, p)
    id, t = tjanster_med_avsnitt(b)[0]
    u = bygg_underlag(regelbas_v1, p, t, id)
    s = next(s for s in u.sarbarheter if s.id == "S-GEO-01")
    assert SKYDDAD_VISNING in s.motivering and "2 %" not in s.motivering
    assert "HEMLIG_KALLA" not in u.model_dump_json()
    # V6: inte heller faktabladet eller delanropen visar det lilla antalet eller källan.
    k = v6_kedja(regelbas_v1, p)
    assert all("2 %" not in r.faktablad.model_dump_json() for r in k.resultat.values())
    assert "2 %" not in ai_begaran(k) and "HEMLIG_KALLA" not in ai_begaran(k)
