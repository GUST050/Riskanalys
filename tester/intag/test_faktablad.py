import pytest

from riskanalys.bedomning.korning import kor_bedomning, las_bedomning
from riskanalys.dokument.analysunderlag import sarbarhetsstycke
from riskanalys.dokument.faktablad import bygg_faktablad, faktablad_json, visa_tal
from riskanalys.dokument.klartext import uppgiftstext
from riskanalys.dokument.platshallare import ersatt_tal
from riskanalys.dokument.underlag import SKYDDAD_VISNING, _sarbarhetsmotivering, tjanster_med_avsnitt
from riskanalys.profil.lagring import spara_profil
from riskanalys.profil.modeller import Uppgift
from riskanalys.profil.omfattning import harled_andelar
from tester.fixturer.m2 import tjanst_for_prov


def _faktablad(mapp, rb, profil):
    mapp.mkdir(parents=True, exist_ok=True)
    spara_profil(mapp, profil)
    b = las_bedomning(kor_bedomning(mapp, rb))
    avsnitt_id, t = tjanster_med_avsnitt(b)[0]
    return bygg_faktablad(rb, profil, t, avsnitt_id)


def test_ingen_fri_kalltext_eller_bekraftare_lamnar_datorn(tmp_path, rb_intag, klar):
    hemligt = "Kim Testsson /Users/x/kundregister.xlsx"
    upp = {k: (u.model_copy(update={"kalla": hemligt, "bekraftad_av": "roll:Kim Testsson"}) if u.kalla else u)
           for k, u in klar.uppgifter.items()}
    fb = _faktablad(tmp_path, rb_intag, klar.model_copy(update={"uppgifter": upp}))
    text = faktablad_json(fb)
    assert "Kim Testsson" not in text and "/Users/" not in text and "kundregister" not in text
    assert {p.kalltyp for p in fb.poster} <= {None, "register", "intern_statistik", "egen_kannedom", "dokument", "harledning"}


def test_skyddade_varden_saknar_tal(tmp_path, rb_intag, klar):
    fb = _faktablad(tmp_path, rb_intag, klar)
    for p in fb.poster:
        if p.visningsvarde == SKYDDAD_VISNING:
            assert p.status == "skyddad" and p.tal is None and p.id not in fb.numeriska()


def test_faktabladet_ar_byte_for_byte_stabilt(tmp_path, rb_intag, klar):
    assert faktablad_json(_faktablad(tmp_path / "a", rb_intag, klar)) == faktablad_json(_faktablad(tmp_path / "b", rb_intag, klar))


def test_svenskt_talformat():
    assert visa_tal(2300000.0) == "2 300 000"
    assert visa_tal(46.5) == "46,5"


def test_okant_skyddat_underlag_far_inte_aterskapas_fran_ravarde(rb_intag, klar):
    from riskanalys.dokument.faktablad import _post
    from riskanalys.dokument.modeller import UnderlagUppgift
    id = 'P-KUND.antal_aktiva'
    u = UnderlagUppgift(id=id, fraga='Aktiva kunder', varde='okänt', bekraftad=True)
    post = _post(rb_intag, klar, u)
    assert post.tal is None and post.visningsvarde == 'okänt'


RISKBRANSCH = "P-KUND.andel_riskbransch"


def _sarb(rb):
    return next(s.id for s in rb.sarbarheter.values() if s.villkor.get("falt") == RISKBRANSCH)


def _med_riskbransch(rb, klar, antal):
    """Testprofilen har 100 aktiva kunder; andelen härleds ur antalet, som i intaget."""
    u = klar.uppgifter["P-KUND.antal_riskbransch"].model_copy(update={"varde": antal})
    profil = klar.model_copy(update={"uppgifter": {**klar.uppgifter, "P-KUND.antal_riskbransch": u}})
    return harled_andelar(profil, rb, frozenset({"P-KUND.antal_riskbransch"}))


def test_motiveringen_sager_att_faktorn_forekommer_under_gransen(rb_intag, klar):
    rb_intag = _med_tillatna_komponenter(rb_intag)
    text = _sarbarhetsmotivering(rb_intag, _med_riskbransch(rb_intag, klar, 15), _sarb(rb_intag), (RISKBRANSCH,))
    assert "Faktorn förekommer: andel kunder i riskbranscher är 15 %, men det ligger under metodens gräns på 20 %" in text


def test_motiveringen_for_litet_positivt_antal_skriver_mindre_an_en_procent(rb_intag, klar):
    rb_intag = _med_tillatna_komponenter(rb_intag)
    # 8 av 2 000 är 0,4 % och visas som "mindre än 1 %" i faktabladet och i meningen, aldrig som "0 %".
    aktiva = klar.uppgifter["P-KUND.antal_aktiva"].model_copy(update={"varde": 2000})
    profil = klar.model_copy(update={"uppgifter": {**klar.uppgifter, "P-KUND.antal_aktiva": aktiva}})
    profil = harled_andelar(_med_riskbransch(rb_intag, profil, 8), rb_intag, frozenset({"P-KUND.antal_aktiva"}))
    text = _sarbarhetsmotivering(rb_intag, profil, _sarb(rb_intag), (RISKBRANSCH,))
    assert "Faktorn förekommer: andel kunder i riskbranscher är mindre än 1 %, men det ligger under metodens gräns på 20 %" in text


def test_falt_utanfor_tillatelselistan_far_ingen_gransmening(rb_intag, klar):
    text = _sarbarhetsmotivering(rb_intag, _med_riskbransch(rb_intag, klar, 15), _sarb(rb_intag), ())
    assert "gräns" not in text and "15 %" not in text


def test_skyddad_vy_ger_samma_text_for_noll_och_tre_kunder(rb_intag, klar):
    # 0 och 3 av 100 visas båda som skyddat värde. Texten får inte avslöja vilket det är (granskning 2026-10-12).
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


def test_okant_antal_ger_samma_motivering_for_noll_och_tre_procent(rb_intag, klar):
    # Utan bekräftat antal kan smågruppsskyddet inte pröva andelen. Visningen blir "okänt", så ingen gränsmening skrivs
    # och 0 % ser likadant ut som 3 %.
    def motivering(andel):
        andelsuppgift = klar.uppgifter[RISKBRANSCH].model_copy(update={"varde": andel})
        uppgifter = {**klar.uppgifter, "P-KUND.antal_riskbransch": Uppgift(), RISKBRANSCH: andelsuppgift}
        return _sarbarhetsmotivering(rb_intag, klar.model_copy(update={"uppgifter": uppgifter}), _sarb(rb_intag),
                                     (RISKBRANSCH,))
    noll, tre = motivering(0.0), motivering(0.03)
    assert noll == tre
    assert "okänt" in tre and "gräns" not in tre and "förekommer" not in tre and "3 %" not in tre


def _kundbas(rb, klar, aktiva, riskbransch):
    upp = dict(klar.uppgifter)
    for falt_id, varde in (("P-KUND.antal_aktiva", aktiva), ("P-KUND.antal_riskbransch", riskbransch)):
        upp[falt_id] = upp[falt_id].model_copy(update={"varde": varde})
    return harled_andelar(klar.model_copy(update={"uppgifter": upp}), rb,
                          frozenset({"P-KUND.antal_aktiva", "P-KUND.antal_riskbransch"}))


@pytest.mark.parametrize("aktiva,antal", [(2000, 8), (2000, 10)])  # 0,4 % och exakt 0,5 %
def test_liten_andel_ar_ett_intervall_genom_hela_kedjan(tmp_path, rb_intag, klar, aktiva, antal):
    rb_intag = _med_tillatna_komponenter(rb_intag)
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


def test_maskering_gar_fore_intervall_for_tre_av_tvatusen(tmp_path, rb_intag, klar):
    # 3 av 2 000 är 0,15 % och skulle bli "mindre än 1 %". Smågruppsskyddet gäller först.
    profil = _kundbas(rb_intag, klar, 2000, 3)
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, profil)
    fb = bygg_faktablad(rb_intag, profil, t, avsnitt_id)
    post = next(p for p in fb.poster if p.id == RISKBRANSCH)
    assert post.visningsvarde == SKYDDAD_VISNING and post.status == "skyddad"
    assert not post.intervall and post.tal is None
    assert RISKBRANSCH not in fb.numeriska()

def _med_antal(rb, profil, varden: dict):
    upp = dict(profil.uppgifter)
    for falt_id, varde in varden.items():
        upp[falt_id] = upp[falt_id].model_copy(update={"varde": varde})
    return harled_andelar(profil.model_copy(update={"uppgifter": upp}), rb, frozenset(varden))


def test_195_av_1000_visas_under_gransen_i_faktablad_och_lokalt(tmp_path, rb_intag, klar):
    rb_intag = _med_tillatna_komponenter(rb_intag)
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
    rb_intag = _med_tillatna_komponenter(rb_intag)
    profil = _med_antal(rb_intag, klar, {"P-KUND.antal_riskbransch": 204, "P-KUND.antal_aktiva": 1000})
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, profil)
    post = next(p for p in bygg_faktablad(rb_intag, profil, t, avsnitt_id).poster if p.id == "P-KUND.andel_riskbransch")
    assert post.visningsvarde == "20,4 %"


def test_skyddat_litet_varde_nara_gransen_forblir_maskerat(tmp_path, rb_intag, klar):
    profil = _med_antal(rb_intag, klar, {"P-KUND.antal_riskbransch": 3, "P-KUND.antal_aktiva": 15})
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, profil)
    post = next(p for p in bygg_faktablad(rb_intag, profil, t, avsnitt_id).poster if p.id == "P-KUND.andel_riskbransch")
    assert post.visningsvarde == SKYDDAD_VISNING and post.tal is None


@pytest.mark.parametrize("antal,bas,visning,tal", [
    (2004, 10000, "20,04 %", 20.04),
    (19996, 100000, "strax under 20 %", None),
    (200001, 1000000, "strax över 20 %", None),
])
def test_gransprecision_bevaras_genom_platshallarkedjan(tmp_path, rb_intag, klar, antal, bas, visning, tal):
    rb_intag = _med_tillatna_komponenter(rb_intag)
    profil = _kundbas(rb_intag, klar, bas, antal)
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, profil)
    fb = bygg_faktablad(rb_intag, profil, t, avsnitt_id)
    post = next(p for p in fb.poster if p.id == RISKBRANSCH)
    assert post.visningsvarde == visning
    assert post.tal == tal and post.intervall == (tal is None)
    assert ersatt_tal(f"{{tal:{RISKBRANSCH}}} av kunderna", fb.numeriska(), fb.perioder()) == visning + " av kunderna"
    assert visning in uppgiftstext(rb_intag, profil, RISKBRANSCH)
    assert visning in sarbarhetsstycke(rb_intag, profil, t.tjanst, "S-KUND-01").text

@pytest.mark.parametrize('uteslut', ['P-KUND.antal_riskbransch', 'P-KUND.antal_aktiva'])
def test_harledd_andel_begransas_nar_en_komponent_inte_ar_tillaten(tmp_path, rb_intag, klar, uteslut):
    lista = rb_intag.tillatelselistor['risk_per_tjanst']
    tillatna = tuple(set(lista.falt) | {'P-KUND.antal_riskbransch', 'P-KUND.antal_aktiva'})
    lista = lista.model_copy(update={'falt': tuple(f for f in tillatna if f != uteslut)})
    rb = rb_intag.model_copy(update={'tillatelselistor': {**rb_intag.tillatelselistor, 'risk_per_tjanst': lista}})
    profil = _med_antal(rb, klar, {'P-KUND.antal_riskbransch': 195, 'P-KUND.antal_aktiva': 1000})
    fb = _faktablad(tmp_path, rb, profil)
    post = next(p for p in fb.poster if p.id == RISKBRANSCH)
    assert post.visningsvarde == 'strax under 20 %' and post.tal is None and post.intervall
    assert fb.numeriska()[RISKBRANSCH] == 'strax under 20 %'
    sarb = next(s for s in fb.sarbarheter if s.id == 'S-KUND-01')
    assert sarb.galler == 'nej' and '19,5' not in sarb.motivering
    assert '19,5 %' in uppgiftstext(rb, profil, RISKBRANSCH)


def _med_tillatna_komponenter(rb):
    """Syntetisk tillåtelselista isolerar visningsprecision från integritetspolicyn."""
    lista = rb.tillatelselistor['risk_per_tjanst']
    lista = lista.model_copy(update={'falt': tuple(dict.fromkeys((*lista.falt, 'P-KUND.antal_riskbransch', 'P-KUND.antal_aktiva')))})
    return rb.model_copy(update={'tillatelselistor': {**rb.tillatelselistor, 'risk_per_tjanst': lista}})


def test_standardregelbas_begransar_195_men_lokal_visning_bevarar_precision(tmp_path, rb_intag, klar):
    profil = _med_antal(rb_intag, klar, {'P-KUND.antal_riskbransch': 195, 'P-KUND.antal_aktiva': 1000})
    fb = _faktablad(tmp_path, rb_intag, profil)
    post = next(p for p in fb.poster if p.id == RISKBRANSCH)
    assert post.visningsvarde == 'strax under 20 %' and post.tal is None
    assert '19,5' not in faktablad_json(fb)
    assert '19,5 %' in uppgiftstext(rb_intag, profil, RISKBRANSCH)


def test_intagsoversikt_visar_lokal_precision(tmp_path, rb_intag, klar):
    from types import SimpleNamespace
    from riskanalys.intag.vyer import oversikt
    profil = _med_antal(rb_intag, klar, {'P-KUND.antal_riskbransch': 195, 'P-KUND.antal_aktiva': 1000})
    falt = rb_intag.falt[RISKBRANSCH].model_copy(update={'intag': SimpleNamespace(obligatorisk=False)})
    t = SimpleNamespace(besvarade=1, antal=1, komplett=False, saknade=(), hinder=())
    s = SimpleNamespace(prefix='/', csrf='test', kompletteringar=(), utkast=None, tjanst=SimpleNamespace(rb=rb_intag, mapp=tmp_path, oversikt=lambda p:t, finns=lambda:True))
    text = oversikt(s, profil=profil, qs=[SimpleNamespace(falt=falt)])
    assert '19,5 %' in text


def test_hela_kundbasen_visas_nar_bada_komponenter_ar_tillatna(tmp_path, rb_intag, klar):
    rb = _med_tillatna_komponenter(rb_intag)
    profil = _med_antal(rb, klar, {'P-KUND.antal_riskbransch': 1000, 'P-KUND.antal_aktiva': 1000})
    post = next(p for p in _faktablad(tmp_path, rb, profil).poster if p.id == RISKBRANSCH)
    assert post.visningsvarde == '100 %' and post.tal == 100


@pytest.mark.parametrize('antal', [(195,199),(200,205)])
def test_begransad_precision_ger_samma_hela_begaran_med_omforsok(rb_intag, klar, antal):
    from tester.intag.test_skyddad_begaran import begaran, _svar_med_nivakandidater
    profiler = [_med_antal(rb_intag, klar, {'P-KUND.antal_riskbransch': n, 'P-KUND.antal_aktiva': 1000}) for n in antal]
    anrop = [begaran(rb_intag, p, _svar_med_nivakandidater) for p in profiler]
    assert anrop[0] == anrop[1]
    from riskanalys.dokument.promptar import DELAR
    assert len(anrop[0]) > len(DELAR)


def test_brakgrans_bevaras_i_lokal_gransmening(rb_intag, klar):
    from riskanalys.dokument.klartext import gransmening, UnderGrans
    profil = _med_antal(rb_intag, klar, {'P-KUND.antal_riskbransch': 204, 'P-KUND.antal_aktiva': 1000})
    assert 'metodens gräns på 20,5 %' in gransmening(rb_intag, profil, UnderGrans(RISKBRANSCH, .205))
