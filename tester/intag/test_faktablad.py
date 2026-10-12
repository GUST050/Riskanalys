from riskanalys.bedomning.korning import kor_bedomning, las_bedomning
from riskanalys.dokument.faktablad import bygg_faktablad, faktablad_json, visa_tal
from riskanalys.dokument.underlag import _sarbarhetsmotivering, tjanster_med_avsnitt
from riskanalys.profil.lagring import spara_profil
from riskanalys.profil.modeller import Uppgift
from riskanalys.profil.omfattning import harled_andelar


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
        if p.visningsvarde.startswith(("färre än", "undertryckt")):
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
    text = _sarbarhetsmotivering(rb_intag, _med_riskbransch(rb_intag, klar, 15), _sarb(rb_intag), (RISKBRANSCH,))
    assert "Faktorn förekommer: andel kunder i riskbranscher är 15 %, men det ligger under metodens gräns på 20 %" in text


def test_motiveringen_for_litet_positivt_antal_skriver_mindre_an_en_procent(rb_intag, klar):
    # 8 av 2 000 är 0,4 % och visas som "0 %" i faktabladet; meningen skriver "mindre än 1 %" i stället.
    aktiva = klar.uppgifter["P-KUND.antal_aktiva"].model_copy(update={"varde": 2000})
    profil = klar.model_copy(update={"uppgifter": {**klar.uppgifter, "P-KUND.antal_aktiva": aktiva}})
    profil = harled_andelar(_med_riskbransch(rb_intag, profil, 8), rb_intag, frozenset({"P-KUND.antal_aktiva"}))
    text = _sarbarhetsmotivering(rb_intag, profil, _sarb(rb_intag), (RISKBRANSCH,))
    assert "Faktorn förekommer: andel kunder i riskbranscher är mindre än 1 %, men det ligger under metodens gräns på 20 %" in text


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
