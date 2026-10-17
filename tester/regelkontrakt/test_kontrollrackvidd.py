"""Beskrivande räckvidd binds till källa och attest, aldrig till ny riskreduktion."""
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from riskanalys.regelverk import modeller
from riskanalys.regelverk.laddning import ladda_regelbas
from riskanalys.regelverk.modeller import Kontroll, Sakkunnig, _summa, utan_granskningsmetadata
from riskanalys.regelverk.sakkunnig import (
    Granskningsbeslut, Objektbeslut, applicera_attester, granskningsobjekt,
)
from riskanalys.regelverk.validering import validera
from riskanalys.regelverk.validering_m2 import attesthinder


def _rackvidd(**andringar):
    data = dict(id="KR-PROV", tjanst="T-RED-01", hot=("H-TJ-01",),
                kan_belagga="  Differenser i tillgängligt underlag.  ",
                begransningar="Styrker inte att fakturan motsvarar en verklig affär.",
                forutsattningar="Tillgång till avstämningsunderlag och oberoende prövning.",
                grund="metodval", kallhanvisningar=({"kalla": "SRC-NRA-2024-25", "avsnitt": "7.19", "sida": 123},))
    return modeller.Kontrollrackvidd.model_validate({**data, **andringar})


def _med(rb, *poster):
    kontroll = rb.kontroller["C-07"].model_copy(update={"rackvidd": poster})
    return rb.model_copy(update={"kontroller": {**rb.kontroller, kontroll.id: kontroll}})


@pytest.mark.parametrize("fel", ["tjanst", "hot", "hot_annan_tjanst", "kalla", "obunden", "dubbel", "kollision", "fel_kontroll"])
def test_rackvidd_kraver_precis_kalla_och_giltiga_korsreferenser(regelbas_v1, fel):
    rb = regelbas_v1
    data = {}
    if fel == "tjanst": data["tjanst"] = "T-SAKNAS"
    if fel == "hot": data["hot"] = ("H-SAKNAS",)
    if fel == "hot_annan_tjanst": data["hot"] = (next(h for h in rb.hot if h not in rb.tjanster["T-RED-01"].hot),)
    if fel == "kalla": data["kallhanvisningar"] = ({"kalla": "SRC-SAKNAS", "avsnitt": "7.19", "sida": 123},)
    if fel == "obunden": data["kallhanvisningar"] = ({"kalla": "SRC-PTL", "avsnitt": "2 kap. 1 §", "sida": 1},)
    if fel == "kollision": data["id"] = "H-TJ-01"
    if fel == "fel_kontroll": data.update(tjanst="T-RED-02", hot=rb.tjanster["T-RED-02"].hot)
    post = _rackvidd(**data)
    rb = _med(rb, post, post) if fel == "dubbel" else _med(rb, post)
    assert any(post.id in rad for rad in validera(rb))


@pytest.mark.parametrize("falt,varde", [("id", " "), ("kan_belagga", " "), ("begransningar", "[KOMPLETTERA]"), ("forutsattningar", ""), ("hot", ()), ("kallhanvisningar", ()), ("extra_falt", "x")])
def test_rackvidd_ar_fryst_strikt_och_har_sakliga_svar(falt, varde):
    with pytest.raises(ValidationError): _rackvidd(**{falt: varde})


def test_rackvidd_trimmar_text_och_precis_hanvisning(regelbas_v1):
    post = _rackvidd()
    assert post.kan_belagga == "Differenser i tillgängligt underlag."
    with pytest.raises(ValidationError): post.kan_belagga = "Ändrat"
    rb = _med(regelbas_v1, _rackvidd(kallhanvisningar=({"kalla": "SRC-NRA-2024-25", "avsnitt": " ", "sida": 123},)))
    assert any("KR-PROV" in rad for rad in validera(rb))


def test_tom_rackvidd_bevarar_historiska_objektsummor():
    rb = ladda_regelbas(Path(__file__).resolve().parents[1] / "fixturer/regelbas_v0")
    assert rb.paketets_innehallssumma("RP-RED-VG") == "sha256:55d2dc582f5e7fa6cb31a9c7976e335a766d7ce153607efb613a8e2e40a784ef"
    # Fryst 1.3.0-payload: endast räckvidd och dess nytillagda källor utelämnas.
    nu = ladda_regelbas().kontroller["C-07"]
    gammal = nu.model_copy(update={"rackvidd": (), "kallor": ("SRC-TS-2026-14", "SRC-NRA-2024-25")})
    assert _summa(utan_granskningsmetadata(gammal.model_dump(mode="json"))) == "sha256:be0a12923658e8b9babd58fef01c4e651b48e58569cfa01657c3bd15363404e4"
    kontroll = rb.kontroller["C-07"]
    assert kontroll.rackvidd == ()
    assert "rackvidd" not in kontroll.model_dump(mode="json")
    data = kontroll.model_dump(mode="json")
    assert _summa(utan_granskningsmetadata(Kontroll.model_validate({**data, "rackvidd": []}).model_dump(mode="json"))) == _summa(utan_granskningsmetadata(data))


def _signera(rb):
    beslut = Granskningsbeslut(paket="RP-RED-VG", version=rb.version, datum=date(2026,10,15), granskningsdatum=date(2026,10,15),
        kontrollsumma=rb.paketets_innehallssumma("RP-RED-VG"), granskare="Syntetisk testgranskare", kompetens="Syntetisk kompetens", oberoende=True,
        objekt={id: Objektbeslut(beslut="verifierad", kommentar="Endast syntetiskt test") for id in granskningsobjekt(rb,"RP-RED-VG")})
    return applicera_attester(rb, beslut), beslut


def test_andrad_rackvidd_kraver_ny_attest(regelbas_v1):
    rb, beslut = _signera(_med(regelbas_v1, _rackvidd()))
    assert not attesthinder(rb,"RP-RED-VG")
    gammal = granskningsobjekt(rb,"RP-RED-VG")
    post = rb.kontroller["C-07"].rackvidd[0]
    nytt = _med(rb, post.model_copy(update={"begransningar": "Även dolda betalningsled kräver separat underlag."}))
    summor = granskningsobjekt(nytt,"RP-RED-VG")
    assert summor[post.id] != gammal[post.id] and summor["C-07"] != gammal["C-07"]
    assert any(post.id in rad for rad in attesthinder(nytt,"RP-RED-VG"))
    assert any("C-07" in rad for rad in attesthinder(nytt,"RP-RED-VG"))
    assert not applicera_attester(nytt, beslut).kontroller["C-07"].rackvidd[0].sakkunnig.galler(summor[post.id])
    nytt = nytt.model_copy(update={"version": "1.99.0"})
    assert any(post.id in rad for rad in attesthinder(nytt,"RP-RED-VG"))


def test_statusandring_i_underpost_andrar_inte_hash_men_stoppar_attest(regelbas_v1):
    rb, _ = _signera(_med(regelbas_v1, _rackvidd()))
    post = rb.kontroller["C-07"].rackvidd[0]
    nytt = _med(rb, post.model_copy(update={"sakkunnig": Sakkunnig()}))
    assert granskningsobjekt(nytt,"RP-RED-VG") == granskningsobjekt(rb,"RP-RED-VG")
    assert nytt.paketets_innehallssumma("RP-RED-VG") == rb.paketets_innehallssumma("RP-RED-VG")
    assert any(post.id in rad for rad in attesthinder(nytt,"RP-RED-VG"))
    assert post.id in rb.alla_id()


@pytest.mark.parametrize("fall", ["bas", "leverantor", "plattform"])
def test_rackvidd_andrar_inte_motorutfall(regelbas_v1, profil_fabrik, real_varden, fall):
    from riskanalys.bedomning.motor import bedom_tjanst
    from riskanalys.dokument.faktablad import bygg_faktablad, faktablad_json
    rb = regelbas_v1
    assert any(k.rackvidd for k in rb.kontroller.values())
    utan = rb.model_copy(update={"kontroller": {id: k.model_copy(update={"rackvidd": ()}) for id,k in rb.kontroller.items()}})
    varden = dict(real_varden)
    if fall == "leverantor": varden.update({"P-RISK.extern_kyc": True, "P-RISK.utkontraktering": True})
    if fall == "plattform": varden.update({"P-TJ.red01_erbjuds": True, "P-TJ.red01_geografi": "Syntetiskt uppdrag med PSP, okända bakomliggande parter och syfte."})
    assert set(varden) <= set(rb.falt)
    profil = profil_fabrik(rb,varden)
    for t in rb.tjanster.values():
        fore = bedom_tjanst(utan,t,profil)
        efter = bedom_tjanst(rb,t,profil)
        assert efter == fore  # nivåer, villkor, regelspar och kontrollernas reduktionsbeslut
        if efter.inneboende is not None:
            assert faktablad_json(bygg_faktablad(rb,profil,efter,"D-ARB.6.1")) == faktablad_json(bygg_faktablad(utan,profil,fore,"D-ARB.6.1"))


def test_katalogens_rackvidd_ar_ogranskad_och_avgransad(regelbas_v1):
    rb = regelbas_v1
    assert rb.version == "1.6.0"
    assert not validera(rb)
    for t in rb.tjanster.values():
        for id in t.kontroller:
            assert any(r.tjanst == t.id for r in rb.kontroller[id].rackvidd)
    assert all(r.sakkunnig.status == "ej_granskad" and r.grund == "metodval" for k in rb.kontroller.values() for r in k.rackvidd)
    assert "SRC-FIPO-PLATTFORM-2026" in rb.kallor
    assert "PSP" in rb.kontroller["C-07"].rackvidd[0].begransningar


def test_rackvidds_id_ar_unikt_mellan_kontroller(regelbas_v1):
    rb = _med(regelbas_v1, _rackvidd())
    kontroll = rb.kontroller['C-TJ-01']
    kontroll = kontroll.model_copy(update={'rackvidd': (_rackvidd(),)})
    rb = rb.model_copy(update={'kontroller': {**rb.kontroller, kontroll.id: kontroll}})
    assert any('KR-PROV' in rad and 'unikt' in rad for rad in validera(rb))


def test_oforandrad_rackviddsattest_bevaras_vid_inaktuell_annan_paketimport(regelbas_v1):
    rb, beslut = _signera(_med(regelbas_v1, _rackvidd()))
    post = rb.kontroller['C-07'].rackvidd[0]
    gammalt = beslut.model_copy(update={'version': '1.3.0'})
    nytt = applicera_attester(rb, gammalt)
    assert nytt.kontroller['C-07'].rackvidd[0].sakkunnig == post.sakkunnig


def test_falsk_verifierad_rackviddsstatus_utan_summa_ger_valideringsfel(regelbas_v1):
    post = _rackvidd(sakkunnig={'status': 'verifierad', 'av': 'Syntetisk', 'datum': '2026-10-15'})
    assert any('KR-PROV' in rad and 'innehållet' in rad for rad in validera(_med(regelbas_v1, post)))


@pytest.mark.parametrize('status', ['full_tackning', '', 'verifierad', 1])
def test_beskrivningsstatus_avvisar_otillatet_varde(status):
    with pytest.raises(ValidationError):
        _rackvidd(beskrivningsstatus=status)


@pytest.mark.parametrize('status', ['beskriven', 'okand'])
def test_beskrivningsstatus_ar_explicit_serialiserad(status):
    post = _rackvidd(beskrivningsstatus=status)
    assert post.beskrivningsstatus == status
    assert post.model_dump(mode='json')['beskrivningsstatus'] == status


def test_aldre_oangiven_beskrivningsstatus_bevarar_v1_4_summor(regelbas_v1):
    post = _rackvidd()
    assert post.beskrivningsstatus is None
    assert 'beskrivningsstatus' not in post.model_dump(mode='json')
    assert _rackvidd(beskrivningsstatus=None).model_dump(mode='json') == post.model_dump(mode='json')
    # Exakta summor fångade på godkänd 1.4.0-katalog före denna schemaändring.
    for id, eget, foralder in [
        ('C-07', 'sha256:16361e7c8fe10c036c7d261345cbcbbc7328374e7ba763257d4c5bf041efb837', 'sha256:9b814be13c4eb15b010ffc39f6a35e5f2912dc8fb9125ac0e55d9a9814324d50'),
        ('C-TJ-01', 'sha256:f2515458e07ba4a2b313035f1e6463d67c52d768d25c5763ab3405e53b22ceeb', 'sha256:3b1a378209fc2f19cd4fbc76982b125e5dca761b91b80fbe561ecd86a6b25778'),
    ]:
        kontroll = regelbas_v1.kontroller[id]
        aldre = kontroll.model_copy(update={'rackvidd': tuple(r.model_copy(update={'beskrivningsstatus': None}) for r in kontroll.rackvidd)})
        assert _summa(utan_granskningsmetadata(aldre.rackvidd[0].model_dump(mode='json'))) == eget
        assert _summa(utan_granskningsmetadata(aldre.model_dump(mode='json'))) == foralder


def test_andrad_beskrivningsstatus_upphaver_egen_och_foralders_attest(regelbas_v1):
    rb, _ = _signera(_med(regelbas_v1, _rackvidd(beskrivningsstatus='beskriven')))
    gammalt = granskningsobjekt(rb, 'RP-RED-VG')
    post = rb.kontroller['C-07'].rackvidd[0]
    nytt = _med(rb, post.model_copy(update={'beskrivningsstatus': 'okand'}))
    summor = granskningsobjekt(nytt, 'RP-RED-VG')
    assert summor[post.id] != gammalt[post.id]
    assert summor['C-07'] != gammalt['C-07']
    hinder = attesthinder(nytt, 'RP-RED-VG')
    assert any(post.id in rad for rad in hinder)
    assert any('C-07' in rad for rad in hinder)


def test_sakkunnigattest_kan_bekrafta_okand_utan_statuspromotion(regelbas_v1):
    rb, _ = _signera(_med(regelbas_v1, _rackvidd(beskrivningsstatus='okand')))
    post = rb.kontroller['C-07'].rackvidd[0]
    assert post.sakkunnig.status == 'verifierad'
    assert post.beskrivningsstatus == 'okand'
    assert not attesthinder(rb, 'RP-RED-VG')


def test_katalogen_skiller_beskriven_observation_fran_okant(regelbas_v1):
    poster = [r for k in regelbas_v1.kontroller.values() for r in k.rackvidd]
    assert len(poster) == 12
    assert [(r.id, r.beskrivningsstatus) for r in poster if r.beskrivningsstatus == 'beskriven'] == [('KR-C-07-T-RED-01', 'beskriven')]
    assert sum(r.beskrivningsstatus == 'okand' for r in poster) == 11
    assert all(r.sakkunnig.status == 'ej_granskad' for r in poster)
