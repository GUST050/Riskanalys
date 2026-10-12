from riskanalys.bedomning.korning import kor_bedomning, las_bedomning
from riskanalys.dokument.faktablad import bygg_faktablad, faktablad_json, visa_tal
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.profil.lagring import spara_profil


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
