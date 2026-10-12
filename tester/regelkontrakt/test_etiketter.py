import re
from pathlib import Path

from riskanalys.bedomning.erfarenheter import ERFARENHETSFALT
from riskanalys.dokument.klartext import har_eget_namn
from riskanalys.regelverk import tillsyn
from riskanalys.regelverk.laddning import ladda_regelbas
from riskanalys.regelverk.modeller import Falt
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


def test_varje_harledd_andel_har_ett_eget_namn():
    rb = ladda_regelbas()
    andelar = [f.id for f in rb.falt.values() if f.antalfalt and f.basfalt and not f.alias_for]
    assert andelar
    assert [i for i in andelar if not har_eget_namn(rb, i)] == []


def test_falt_i_omfattningens_hindertexter_har_ett_eget_namn():
    # rattlig_omfattning skriver fält-ID i hindertexterna; id_till_namn byter dem mot kortnamn i D-ARB.2.
    rb = ladda_regelbas()
    namnda = sorted(set(re.findall(r"P-[A-Z]+\.[a-z_]+", Path(tillsyn.__file__).read_text(encoding="utf-8"))))
    assert len(namnda) >= 8
    assert [i for i in namnda if i in rb.falt and not har_eget_namn(rb, i)] == []
    assert [i for i in namnda if i not in rb.falt] == []


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
