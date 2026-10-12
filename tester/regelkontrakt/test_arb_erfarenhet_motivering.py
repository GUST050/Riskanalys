"""H1/H2: syntetiskt underlag genom motor, AI-gräns och dokumentgranskning."""

import pytest

from riskanalys.bedomning.motor import bedom
from riskanalys.dokument.arb import bygg_arb
from riskanalys.dokument.modeller import AvsnittsUtkast
from riskanalys.dokument.underlag import bygg_underlag, tjanster_med_avsnitt
from riskanalys.drift.historik import Handelse, Historik
from riskanalys.granskning.kontroller import granska
from riskanalys.profil.hantering import skapa_profil
from riskanalys.profil.modeller import Byra
from riskanalys.regelverk.urval import valj
from tester.fixturer.m2 import DAG, PERIOD, bygg_testsvar, komplett_profil

RAPPORTER = "P-VERK.antal_rapporter"
AVBOJANDEN = "P-VERK.antal_avbojanden"
HISTORIK = Historik().med(Handelse(datum=DAG, typ="utvärdering", beskrivning="Syntetiskt prov."))


@pytest.fixture
def profil(regelbas_v1):
    p = skapa_profil(regelbas_v1, Byra(id="syntetisk", regelpaket="RP-RED-VG", lan="Västra Götaland", datum=DAG))
    return komplett_profil(regelbas_v1, p)


def andrat(profil, falt, **uppdatering):
    return profil.model_copy(update={"uppgifter": {**profil.uppgifter, falt: profil.uppgifter[falt].model_copy(update=uppdatering)}})


def kedja(rb, profil):
    urval = valj(rb, profil.byra.regelpaket, DAG, profil.byra.lan)
    b = bedom(rb, urval, profil)
    utkast = {a["avsnitt"]: AvsnittsUtkast.model_validate(a) for a in bygg_testsvar(rb, profil, b)}
    d = bygg_arb(rb, profil, b, utkast, HISTORIK)
    return urval, b, d


@pytest.mark.parametrize("antal,status", [(0, "inga"), (3, "finns"), (12, "finns")])
def test_motorn_beaktar_egen_rapportering_utan_att_gora_antal_till_riskpoang(regelbas_v1, profil, antal, status):
    _, bas, _ = kedja(regelbas_v1, profil)
    _, b, _ = kedja(regelbas_v1, andrat(profil, RAPPORTER, varde=antal))
    erbjudna = [t for t in b.tjanster if t.erbjuds]
    assert all(t.egen_erfarenhet.rapporter == status and t.egen_erfarenhet.belagd for t in erbjudna)
    assert [t.inneboende for t in b.tjanster] == [t.inneboende for t in bas.tjanster]
    assert all(t.egen_erfarenhet is None for t in b.tjanster if t.erbjuds is False)


@pytest.mark.parametrize("uppdatering", [
    {"status": "saknas"}, {"inaktuell": True}, {"kalla": None}, {"datum": None},
    {"bekraftad_av": None}, {"period": None}, {"varde": -1},
])
def test_obelagd_rapportering_ar_okand_och_ger_b15(regelbas_v1, profil, uppdatering):
    p = andrat(profil, RAPPORTER, **uppdatering)
    u, b, d = kedja(regelbas_v1, p)
    assert all(t.egen_erfarenhet.rapporter == "saknas" for t in b.tjanster if t.erbjuds)
    assert any(f.regel == "B-15" for f in granska(regelbas_v1, u, p, b, d, HISTORIK, DAG))


def test_ai_far_skyddade_antal_men_inte_kalla_namn_eller_fritext(regelbas_v1, profil):
    p = andrat(profil, RAPPORTER, varde=3, kalla="HEMLIG_KALLA", bekraftad_av="HEMLIG_PERSON")
    p = andrat(p, "P-BESK.erfarenheter", varde="LOKAL_HEMLIG_ERFARENHET")
    _, b, _ = kedja(regelbas_v1, p)
    for id, t in tjanster_med_avsnitt(b):
        underlag = bygg_underlag(regelbas_v1, p, t, id)
        uppgifter = {v.id: v for v in underlag.uppgifter}
        assert uppgifter[RAPPORTER].varde == "färre än 5"
        assert uppgifter[AVBOJANDEN].period == (str(PERIOD.fran), str(PERIOD.till))
        assert all(text not in underlag.model_dump_json() for text in ("HEMLIG_KALLA", "HEMLIG_PERSON", "LOKAL_HEMLIG_ERFARENHET"))


def test_rapportantalets_intagskoppling_ar_hot(regelbas_v1):
    assert regelbas_v1.falt[RAPPORTER].intag.avsnitt == ("D-ARB.4",)
    assert regelbas_v1.falt[AVBOJANDEN].intag.avsnitt == ("D-ARB.4",)
    assert regelbas_v1.bristmonster["B-15"].automatiserad


def test_hotanalysen_beaktar_noll_och_erfarenheter_per_tjanst(regelbas_v1, profil):
    _, b, d = kedja(regelbas_v1, profil)
    stycken = tuple(s for a in d.avsnitt if a.id.startswith("D-ARB.6.") for s in a.stycken)
    for t in b.tjanster:
        if not t.erbjuds:
            continue
        analys = [s for s in stycken if {t.tjanst, RAPPORTER, AVBOJANDEN} <= set(s.referenser)]
        assert len(analys) == 1
        assert "Noll rapporter" in analys[0].text
        assert "inte frånvaro av hot" in analys[0].text
        assert str(PERIOD.fran) in analys[0].text


def test_b15_hittar_borttagen_analys_trots_att_antal_finns_i_dokumentet(regelbas_v1, profil):
    u, b, d = kedja(regelbas_v1, profil)
    a = next(a for a in d.avsnitt if a.id.startswith("D-ARB.6."))
    p = tuple(s for s in a.stycken if not {RAPPORTER, AVBOJANDEN} <= set(s.referenser))
    nytt = a.model_copy(update={"stycken": p})
    d = d.model_copy(update={"avsnitt": tuple(nytt if s.id == a.id else s for s in d.avsnitt)})
    fynd = [f for f in granska(regelbas_v1, u, profil, b, d, HISTORIK, DAG) if f.regel == "B-15"]
    assert len(fynd) == 1


def test_sarbarhet_motiveras_med_villkor_varde_period_och_kalla(regelbas_v1, profil):
    _, _, d = kedja(regelbas_v1, profil)
    stycke = next(s for s in next(a for a in d.avsnitt if a.id.startswith("D-ARB.6.")).stycken if "S-GEO-01" in s.referenser)
    assert "Sårbarheten gäller om" in stycke.text and "0 %" in stycke.text
    assert str(PERIOD.fran) in stycke.text and "Syntetisk testkälla" in stycke.text
    assert "inga geografiska risker" not in stycke.text.lower()
    assert "P-BESK.geografi" in stycke.referenser


@pytest.mark.parametrize("fel", ["omotiverat", "felvarde", "felreferenser", "saknas"])
def test_geografi_utan_riktig_underlagsmotivering_blockeras(regelbas_v1, profil, fel):
    u, b, d = kedja(regelbas_v1, profil)
    a = next(a for a in d.avsnitt if a.id.startswith("D-ARB.6."))
    stycken = []
    for s in a.stycken:
        if "S-GEO-01" in s.referenser:
            if fel == "saknas":
                continue
            text = "Gäller inte enligt byråns uppgifter." if fel == "omotiverat" else s.text + " Felaktigt tillägg."
            refs = ["S-GEO-01"] if fel == "felreferenser" else s.referenser
            s = s.model_copy(update={"text": text, "referenser": refs})
        stycken.append(s)
    nytt = a.model_copy(update={"stycken": tuple(stycken)})
    d = d.model_copy(update={"avsnitt": tuple(nytt if s.id == a.id else s for s in d.avsnitt)})
    fynd = [f for f in granska(regelbas_v1, u, profil, b, d, HISTORIK, DAG) if f.regel == "B-10"]
    assert fynd and all(f.allvar == "blockerande" for f in fynd)


def test_obekraftad_geografibeskrivning_ger_b09(regelbas_v1, profil):
    p = andrat(profil, "P-BESK.geografi", inaktuell=True)
    u, b, d = kedja(regelbas_v1, p)
    assert any(f.regel == "B-09" and f.allvar == "blockerande" for f in granska(regelbas_v1, u, p, b, d, HISTORIK, DAG))


def test_ai_sarbarhetsmotivering_skyddar_sma_grupper(regelbas_v1, profil):
    p = andrat(profil, "P-GEO.antal_utland_transaktion", varde=2, kalla="HEMLIG_KALLA")
    _, b, _ = kedja(regelbas_v1, p)
    id, t = tjanster_med_avsnitt(b)[0]
    u = bygg_underlag(regelbas_v1, p, t, id)
    s = next(s for s in u.sarbarheter if s.id == "S-GEO-01")
    assert "färre än 5" in s.motivering and "2 %" not in s.motivering
    assert "HEMLIG_KALLA" not in u.model_dump_json()
