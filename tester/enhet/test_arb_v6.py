"""V6 bygger ett läsbart utkast utan att låtsas ha en lokal attest."""
from datetime import date
import importlib.util

import docx
import pytest

from riskanalys.bedomning.motor import bedom
from riskanalys.dokument.arb import bygg_arb
from riskanalys.dokument.delskrivning import skriv_tjanst
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.modeller import Avsnitt, Dokument, Tabellcell, Textstycke
from riskanalys.dokument.rendering import rendera_docx
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.drift.historik import Handelse, Historik
from riskanalys.profil.hantering import skapa_profil
from riskanalys.profil.modeller import Byra
from riskanalys.regelverk.urval import valj
from tester.fixturer.m2 import DAG, godkant_delsvar, komplett_profil


@pytest.fixture(scope='module')
def v6underlag(regelbas_v1):
    rb = regelbas_v1
    p = komplett_profil(rb, skapa_profil(rb, Byra(id='ab4b', regelpaket='RP-RED-VG', lan='Västra Götaland', datum=DAG)))
    b = bedom(rb, valj(rb, p.byra.regelpaket, DAG, p.byra.lan), p)
    resultat = {id: skriv_tjanst(Testleverantor([godkant_delsvar(d, t) for d in ('hot', 'sarbarheter')]),
        rb, p, t, id, effort='medium', personnamn=(), spara=lambda *a: None) for id, t in tjanster_med_avsnitt(b)}
    h = Historik(handelser=(Handelse(datum=date(2026, 10, 1), typ='utvärdering', beskrivning='Prövning.'),
        Handelse(datum=date(2026, 10, 8), typ='uppdatering', beskrivning='Uppdatering.')))
    return rb, p, b, resultat, h


def bygg(underlag, **kwargs):
    assert importlib.util.find_spec('riskanalys.dokument.arb_v6'), 'V6-byggaren saknas'
    from riskanalys.dokument.arb_v6 import bygg_arb_v6
    return bygg_arb_v6(*underlag, analys=None, **kwargs)


def test_v6_oversikt_forst_ogranskad_analys_och_berakning_i_b1(v6underlag):
    d = bygg(v6underlag)
    assert d.formatversion == 'D-ARB-tjanst-v6'
    assert [a.id for a in d.avsnitt[:2]] == ['D-ARB.1', 'D-ARB.8']
    assert 'saknas' in ' '.join(s.text for s in d.avsnitt[1].stycken).lower()
    bilaga = d.avsnitt_med_id()['D-ARB.B1']
    assert len([t for t in bilaga.tabeller if t.id.endswith('-utfall')]) == len(v6underlag[3])
    assert not any(t.id.endswith('-utfall') for a in d.avsnitt[:-1] for t in a.tabeller)
    assert bygg_arb(*v6underlag, analys=None) == d


def test_v6_visar_separat_utvarderings_och_uppdateringsdatum(v6underlag):
    d = bygg(v6underlag)
    text = ' '.join(s.text for s in d.avsnitt_med_id()['D-ARB.10'].stycken)
    assert all(x in text for x in ('2026-10-01', '2026-10-08', '2027-10-01'))
    from riskanalys.dokument.arb_v6 import utvarderingsavsnitt_v6
    text = ' '.join(s.text for s in utvarderingsavsnitt_v6(Historik()).stycken)
    assert 'Ingen registrerad separat uppdatering' in text


def test_v6_lokal_proveniens_utlamnas_i_aldre_payload():
    gammalt = Textstycke(typ='analys', text='Gammal text.', referenser=[])
    assert 'proveniens' not in gammalt.model_dump()
    lokalt = Textstycke(typ='analys', text='Lokal bedömning.', referenser=[], proveniens='lokal')
    cell = Tabellcell(text='Lokal cell.', proveniens='lokal')
    a = Avsnitt(id='D-ARB.6.1', rubrik='Lokal analys', kalla='lokal', formatversion='D-ARB-tjanst-v6', stycken=(lokalt,))
    assert lokalt.model_dump()['proveniens'] == cell.model_dump()['proveniens'] == 'lokal'
    assert Dokument(id='D-ARB', titel='Prov', avsnitt=(a,)).formatversion == 'D-ARB-tjanst-v6'


def test_v6_word_renderar_tabeller_och_b1_sidbrytning(v6underlag, tmp_path):
    d = bygg(v6underlag)
    fil = rendera_docx(d, v6underlag[1], 'UTKAST', tmp_path / 'prov.docx')
    word = docx.Document(fil)
    assert len(word.tables) == sum(len(a.tabeller) for a in d.avsnitt)
    b1 = next(p for p in word.paragraphs if p.text.startswith('B1 ') and p.style.name == 'Heading 1')
    assert b1.paragraph_format.page_break_before


def test_v6_avvisar_historiska_femdelar_i_ny_byggvag(v6underlag):
    from riskanalys.fel import RiskanalysFel
    rb, p, b, _, h = v6underlag
    gamla = {id: skriv_tjanst(Testleverantor([godkant_delsvar(d, t) for d in ('hot', 'sarbarheter', 'kontroller', 'risknivaer', 'slutsatser')]),
        rb, p, t, id, effort='medium', personnamn=(), spara=lambda *a: None, formatversion='D-ARB-tjanst-v5') for id, t in tjanster_med_avsnitt(b)}
    with pytest.raises(RiskanalysFel, match='identitet'):
        bygg_arb(rb, p, b, gamla, h)


def test_v6_langdvarning_vid_4700_ord_bevarar_hela_lokala_analysen(v6underlag):
    from riskanalys.dokument.matning import med_langdvarning
    text = 'Lokal analys måste bevaras. ' * 1200
    a = Avsnitt(id='D-ARB.6.1', rubrik='Analys', kalla='lokal', formatversion='D-ARB-tjanst-v6',
        stycken=(Textstycke(typ='analys', text=text, referenser=[], proveniens='lokal'),))
    d = Dokument(id='D-ARB', titel='Riskbedömning', avsnitt=(a,))
    nytt = med_langdvarning(d, v6underlag[1])
    assert nytt.avsnitt[0].stycken[0].text == text
    assert any('4 700' in s.text for s in nytt.avsnitt[0].stycken)
    assert med_langdvarning(nytt, v6underlag[1]) == nytt


@pytest.mark.parametrize('parser', ['tolka_ai_svar', 'tolka_delsvar'])
def test_ai_kan_inte_ange_lokal_proveniens_i_rasvar(parser):
    import json
    from pydantic import ValidationError
    from riskanalys.dokument.aischema import tolka_ai_svar, tolka_delsvar
    data = {'stycken': [{'typ': 'analys', 'text': 'En lokal kontroll har genomförts.', 'referenser': ['T-RED-01'], 'proveniens': 'lokal'}], 'oklarheter': []}
    if parser == 'tolka_ai_svar':
        data['avsnitt'] = 'D-ARB.6.1'
    with pytest.raises(ValidationError):
        if parser == 'tolka_ai_svar':
            tolka_ai_svar(json.dumps(data), 'D-ARB.6.1', frozenset({'T-RED-01'}))
        else:
            tolka_delsvar(json.dumps(data), frozenset({'T-RED-01'}), frozenset())


def test_v6_namnsparrat_hot_bevarar_katalogunderlag_utan_ai_text(v6underlag):
    rb, p, b, resultat, h = v6underlag
    id, t = tjanster_med_avsnitt(b)[0]
    r = resultat[id]
    hot = r.del_('hot').model_copy(update={'mall': True, 'lokal_sparr': 'personnamn'})
    resultat = {**resultat, id: r.model_copy(update={'delar': (hot, r.del_('sarbarheter'))})}
    d = bygg((rb, p, b, resultat, h))
    stycken = d.avsnitt_med_id()[id].stycken
    assert any(rb.hot[t.hot[0]].beskrivning in s.text and s.proveniens == 'regelbas' for s in stycken)


SANKTIONSFALT = 'P-GEO.sanktionsanknytning'
SANKTIONSNOTIS = 'Frågan omformulerades 2026-10-17. Tidigare svar läses som att ingen anknytning har identifierats.'


def b1_text(dokument):
    return ' '.join(s.text for s in dokument.avsnitt_med_id()['D-ARB.B1'].stycken)


@pytest.fixture(scope='module')
def v6_dokument_med_nej_svar(v6underlag):
    assert v6underlag[1].uppgifter[SANKTIONSFALT].varde is False
    return bygg(v6underlag)


def test_b1_visar_att_sanktionsfragan_omformulerats(v6_dokument_med_nej_svar):
    assert 'omformulerades 2026-10-17' in b1_text(v6_dokument_med_nej_svar)
    rad = next(s.text for s in v6_dokument_med_nej_svar.avsnitt_med_id()['D-ARB.B1'].stycken if s.referenser == [SANKTIONSFALT])
    assert rad.startswith('Identifierad sanktionsanknytning') and rad.endswith(SANKTIONSNOTIS)


def test_b1_utan_sanktionssvar_saknar_omformuleringsnotis(v6underlag):
    from riskanalys.dokument.intagsunderlag import bygg_underlagsbilaga
    rb, p, *_ = v6underlag
    utan = p.model_copy(update={'uppgifter': {k: u for k, u in p.uppgifter.items() if k != SANKTIONSFALT}})
    bilaga = bygg_underlagsbilaga(rb, utan)
    assert [s for s in bilaga.stycken if s.referenser == [SANKTIONSFALT]]
    assert not any('omformulerades' in s.text for s in bilaga.stycken)
