"""Fryst V10-presentation avvisar ändringar före rendering."""
import pytest
from tester.fixturer.resultatrapport import resultatfall
from tester.enhet.test_resultatrapport_v10 import bygg
from riskanalys.dokument.presentation_v10 import bygg_presentation_v10
from riskanalys.dokument.rapportvyer_v10 import bygg_rapportvyer_v10
from riskanalys.dokument.rendering_v10 import kontrollera_presentation
from riskanalys.fel import RiskanalysFel


@pytest.fixture(scope='module')
def presentation(resultatfall):
    f = resultatfall
    b = bygg(f)
    p = bygg_presentation_v10(b, analys=f.analys, fynd=(), bedomning=f.bedomning, profil=f.profil)
    return f, b, p, bygg_rapportvyer_v10(b.dokument)


@pytest.mark.parametrize('andring', ['konstruktion', 'policy', 'profil', 'cell'])
def test_andring_avvisas(presentation, andring):
    f, b, p, v = presentation
    if andring == 'konstruktion':
        k = p.konstruktioner[0].model_copy(update={'produktionsslag': 'lokalt_original'})
        if k == p.konstruktioner[0]:
            k = k.model_copy(update={'produktionsslag': 'programmall'})
        p = p.model_copy(update={'konstruktioner': (k, *p.konstruktioner[1:])})
    elif andring == 'policy':
        p = p.model_copy(update={'renderingspolicy': 'ändrad'})
    elif andring == 'profil':
        p = p.model_copy(update={'profil': 'sha256:' + '0' * 64})
    else:
        a = v.resultatrapport.avsnitt[0]
        t = a.tabeller[0]
        r = t.rader[0]
        c = r.celler[0].model_copy(update={'text': 'Ändrad cell'})
        r = r.model_copy(update={'celler': (c, *r.celler[1:])})
        t = t.model_copy(update={'rader': (r, *t.rader[1:])})
        a = a.model_copy(update={'tabeller': (t,)})
        from dataclasses import replace
        v = replace(v, resultatrapport=v.resultatrapport.model_copy(update={
            'avsnitt': (a, *v.resultatrapport.avsnitt[1:])}))
    with pytest.raises(RiskanalysFel):
        kontrollera_presentation(v, f.profil, p)


def test_rundresa_och_tre_disjunkta_vyer(presentation):
    from riskanalys.dokument.resultatmodell_v10 import ResultatbyggeV10
    _, b, _, v = presentation
    assert ResultatbyggeV10.model_validate_json(b.model_dump_json()) == b
    ids = [a.id for d in (v.resultatrapport, v.analysbilaga, v.underlagsbilaga) for a in d.avsnitt]
    assert len(ids) == len(set(ids)) and 'D-ARB.B1' in ids
