"""Versionsgränsen hindrar fem historiska AI-delar från att bli v6."""
import pytest
from pydantic import ValidationError

from riskanalys.dokument.delskrivning import Tjanstresultat, kontrollera_resultat, skriv_tjanst
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.promptar import promptsumma
from riskanalys.fel import RiskanalysFel
from tester.fixturer.m2 import godkant_delsvar, tjanst_for_prov


def skriv(lev, rb, p, t, id, **kwargs):
    return skriv_tjanst(lev, rb, p, t, id, effort='medium', personnamn=(), spara=lambda d, f: None, **kwargs)


def test_ny_skrivning_gor_bara_tva_anrop_och_kan_aterverifieras(tmp_path, rb_intag, klar):
    id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    lev = Testleverantor([godkant_delsvar(d, t) for d in ('hot', 'sarbarheter')])
    r = skriv(lev, rb_intag, klar, t, id)
    assert r.formatversion == 'D-ARB-tjanst-v6'
    assert [a.del_id for a in lev.delanrop] == ['hot', 'sarbarheter']
    assert not any(d.mall for d in r.delar)
    kontrollera_resultat(rb_intag, klar, t, r, id)


def test_v6_omforsok_stannar_inom_de_tva_delarna(tmp_path, rb_intag, klar):
    id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    lev = Testleverantor(['{}', godkant_delsvar('hot', t), godkant_delsvar('sarbarheter', t)])
    r = skriv(lev, rb_intag, klar, t, id)
    assert [a.del_id for a in lev.delanrop] == ['hot', 'hot', 'sarbarheter']
    assert not any(d.mall for d in r.delar)


def test_v5_kraver_explicit_historiskt_kontrakt_och_far_inte_markas_om(tmp_path, rb_intag, klar):
    id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    lev = Testleverantor([godkant_delsvar(d, t) for d in ('hot', 'sarbarheter', 'kontroller', 'risknivaer', 'slutsatser')])
    r = skriv(lev, rb_intag, klar, t, id, formatversion='D-ARB-tjanst-v5')
    kontrollera_resultat(rb_intag, klar, t, r, id, formatversion='D-ARB-tjanst-v5')
    with pytest.raises(RiskanalysFel, match='identitet'):
        kontrollera_resultat(rb_intag, klar, t, r, id)
    data = r.model_dump(mode='json')
    data['formatversion'] = 'D-ARB-tjanst-v6'
    with pytest.raises(ValidationError):
        Tjanstresultat.model_validate(data)


def test_promptidentitet_skiller_v6_fran_historiskt_v5():
    from riskanalys.dokument.aischema import SCHEMAVERSION
    from riskanalys.dokument.promptar import delmodul, systemprompt
    from riskanalys.lagring.kontrollsumma import for_text
    gammal = for_text('\n'.join((systemprompt('testleverantor'), delmodul('hot'), SCHEMAVERSION)))
    assert promptsumma('testleverantor', 'hot', formatversion='D-ARB-tjanst-v5') == gammal
    assert promptsumma('testleverantor', 'hot', formatversion='D-ARB-tjanst-v6') != gammal


def test_ny_skrivkorning_sparar_v6_manifest_och_tva_delar(tmp_path, rb_intag, klar):
    from riskanalys.bedomning.korning import kor_bedomning, las_bedomning
    from riskanalys.dokument.skrivning import kor_skrivning, las_skrivresultat
    from riskanalys.dokument.underlag import tjanster_med_avsnitt
    from riskanalys.lagring.manifest import las_manifest
    from riskanalys.profil.lagring import spara_profil
    spara_profil(tmp_path, klar)
    b = las_bedomning(kor_bedomning(tmp_path, rb_intag))
    lev = Testleverantor([godkant_delsvar(d, t) for _, t in tjanster_med_avsnitt(b) for d in ('hot', 'sarbarheter')])
    mapp = kor_skrivning(tmp_path, rb_intag, lev)
    metadata = las_manifest(mapp).metadata
    assert metadata['format'] == 'D-ARB-tjanst-v6'
    assert metadata['skrivformat'] == 'D-ARB-tjanst-v6'
    assert all(tuple(d.del_id for d in r.delar) == ('hot', 'sarbarheter') for r in las_skrivresultat(mapp))


def test_lokal_namnsparr_andrar_inte_v6s_andra_anrop(tmp_path, rb_intag, klar):
    id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    hot = godkant_delsvar('hot', t)
    hot = hot.model_copy(update={'stycken': [s.model_copy(update={'text': s.text + ' Kim Testsson granskar underlagen.'}) for s in hot.stycken]})
    svar = [hot, godkant_delsvar('sarbarheter', t)]
    lev1, lev2 = Testleverantor(svar), Testleverantor(svar)
    r1 = skriv(lev1, rb_intag, klar, t, id)
    r2 = skriv_tjanst(lev2, rb_intag, klar, t, id, effort='medium', personnamn=('Kim Testsson',), spara=lambda d, f: None)
    assert not r1.del_('hot').mall and r2.del_('hot').lokal_sparr == 'personnamn'
    assert lev1.delanrop == lev2.delanrop
