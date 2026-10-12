from riskanalys.bedomning.korning import kor_bedomning, las_bedomning
from riskanalys.dokument.nivatext import nivastycken
from riskanalys.dokument.validering import nivapastaenden
from riskanalys.profil.lagring import spara_profil


def test_nivameningarna_motsvarar_motorns_nivaer(tmp_path, rb_intag, klar):
    spara_profil(tmp_path, klar)
    b = las_bedomning(kor_bedomning(tmp_path, rb_intag))
    t = next(t for t in b.tjanster if t.inneboende is not None)
    angivna = dict(p for s in nivastycken(t) for p in nivapastaenden(s.text))
    assert angivna["inneboende_risk"] == t.inneboende.risk
    assert angivna["inneboende_sannolikhet"] == t.inneboende.sannolikhet
    assert angivna["terrorfinansiering_risk"] == t.terrorfinansiering.risk
    if t.kvarstaende:
        assert angivna["kvarstaende_risk"] == t.kvarstaende
    if t.sanktionsrisk and t.sanktionsrisk.inneboende:
        assert angivna["sanktioner_risk"] == t.sanktionsrisk.inneboende.risk
    assert all(s.referenser[0] == t.tjanst for s in nivastycken(t))
