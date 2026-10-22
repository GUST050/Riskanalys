"""Återkallande är ett uttryckligt terminalt beslut med bevarad historik."""
from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from riskanalys.profil import forandringar as f, modeller as m, planlivslopp as liv
from riskanalys.profil.lagring import spara_profil, las_profil, profilrevision
from riskanalys.profil.planering import planbrister, forandringshinder, aktuell_planutvardering
from riskanalys.drift.historik import Historik, spara_historik, las_historik
from riskanalys.intag.utvardering import registrera_utvardering
from riskanalys.fel import RiskanalysFel
from tester.enhet.test_tjansteplanering import rb, profil, plan, ja, utvardering, DAG, upp


def aterkallad(rb, mapp):
    p = plan(profil())
    spara_profil(mapp, p)
    spara_historik(mapp, Historik(handelser=(utvardering(rb, p),)))
    return f.aterkalla_plan(mapp, rb, 'ny', DAG, 'Ansvarig funktion',
                          'Förändringen ska inte genomföras', profilrevision(p))


def test_aterkallad_plan_utgar_ur_aktuell_planprovning(rb, tmp_path):
    p = aterkallad(rb, tmp_path)
    a = p.tjansteplaner[0].aterkallelse
    assert a.datum == DAG and a.ansvarig == 'Ansvarig funktion'
    assert a.motivering == 'Förändringen ska inte genomföras'
    assert a.planinnehallssumma == liv.planinnehallssumma(p.tjansteplaner[0])
    assert not liv.aktiv_plan(p.tjansteplaner[0])
    assert las_profil(tmp_path) == p
    # Återkallelsen upphäver inte kravet på en ny plan vid ett verkligt införande.
    hinder = forandringshinder(rb, p, ja(p), las_historik(tmp_path), DAG)
    assert any('registrera en plan' in x for x in hinder)
    assert not any(x.startswith('ny: genomför') for x in hinder)
    assert not planbrister(rb, p)


def test_aterkallelsens_utvardering_bevaras_men_galler_inte(rb, tmp_path):
    p = plan(profil())
    h = Historik(handelser=(utvardering(rb, p),))
    p = aterkallad(rb, tmp_path)
    assert las_historik(tmp_path) == h
    assert las_historik(tmp_path).senaste_utvardering() is None
    assert not aktuell_planutvardering(rb, p, p.tjansteplaner[0], h, DAG)
    with pytest.raises(RiskanalysFel, match='historik|återkallad'):
        registrera_utvardering(SimpleNamespace(mapp=tmp_path, rb=rb), DAG,
                               'En annan prövning', profilrevision(p), plan_id='ny')


def test_terminal_plan_far_inte_aterkallas_eller_genomforas(rb, tmp_path):
    p = aterkallad(rb, tmp_path)
    for handling in (
        lambda: f.aterkalla_plan(tmp_path, rb, 'ny', DAG, 'Ansvarig', 'En gång till', profilrevision(p)),
        lambda: f.registrera_genomforande(tmp_path, rb, 'ny', DAG, 'Ansvarig', profilrevision(p)),
        lambda: liv.med_genomforande(rb, p, 'ny', las_historik(tmp_path), DAG, 'Ansvarig', profilrevision(p)),
    ):
        with pytest.raises(RiskanalysFel):
            handling()
    from tester.enhet.test_planens_genomforande import inford
    genomford = inford(rb, tmp_path / 'genomford')
    with pytest.raises(RiskanalysFel):
        f.aterkalla_plan(tmp_path / 'genomford', rb, 'ny', DAG,
                        'Ansvarig', 'För sent', profilrevision(genomford))


@pytest.mark.parametrize('andring', [
    {'aterkallelse': None}, {'beskrivning': 'Omskriven historik'}, {'uppgifter': {'P-TJ.red01_arbetssatt': upp('Nytt')}},
])
def test_aterkallad_plan_far_inte_ateroppnas_eller_redigeras(rb, tmp_path, andring):
    p = aterkallad(rb, tmp_path)
    nytt = p.model_copy(update={'tjansteplaner': (p.tjansteplaner[0].model_copy(update=andring),)})
    with pytest.raises(RiskanalysFel, match='historik'):
        f.spara_andring(tmp_path, rb, nytt, profilrevision(p), lokalt_underlag=True)
    assert las_profil(tmp_path) == p


def test_import_far_inte_skriva_terminal_historik(rb, tmp_path):
    p = aterkallad(rb, tmp_path / 'avslutad')
    fore = plan(profil())
    spara_profil(tmp_path / 'annan', fore)
    with pytest.raises(RiskanalysFel, match='särskilda flödet'):
        f.spara_andring(tmp_path / 'annan', rb, p, profilrevision(fore), lokalt_underlag=True)


def test_skrivavbrott_bevarar_aktiv_plan(rb, tmp_path, monkeypatch):
    p = plan(profil())
    spara_profil(tmp_path, p)
    h = las_historik(tmp_path)
    def avbrott(*args, **kwargs):
        raise RiskanalysFel('Syntetiskt skrivfel')
    monkeypatch.setattr(f, 'spara_profil', avbrott)
    with pytest.raises(RiskanalysFel, match='skrivfel'):
        f.aterkalla_plan(tmp_path, rb, 'ny', DAG, 'Ansvarig', 'Övergiven', profilrevision(p))
    assert las_profil(tmp_path) == p
    assert las_historik(tmp_path) == h


@pytest.mark.parametrize('datum,ansvarig,motivering', [
    (date.today() + timedelta(days=1), 'Ansvarig', 'Skäl'),
    (DAG, ' ', 'Skäl'), (DAG, 'A' * 201, 'Skäl'),
    (DAG, 'Ansvarig', ' '), (DAG, 'Ansvarig', 'A' * 12001),
    (DAG, 'Ansvarig', 'Otillåtet\x01tecken'),
])
def test_ogiltig_aterkallelse_sparas_inte(rb, tmp_path, datum, ansvarig, motivering):
    p = plan(profil())
    spara_profil(tmp_path, p)
    with pytest.raises((RiskanalysFel, ValidationError)):
        f.aterkalla_plan(tmp_path, rb, 'ny', datum, ansvarig, motivering, profilrevision(p))
    assert las_profil(tmp_path) == p


def test_aldre_planbevis_bevaras_och_terminalt_innehall_kontrolleras(rb, tmp_path):
    p = plan(profil())
    before = p.model_dump_json()
    assert 'aterkallelse' not in before
    assert m.Profil.model_validate_json(before).model_dump_json() == before
    oldsum = liv.planinnehallssumma(p.tjansteplaner[0])
    p = aterkallad(rb, tmp_path)
    assert liv.planinnehallssumma(p.tjansteplaner[0]) == oldsum
    annan_rb = rb.model_copy(update={'tjanster': {}, 'falt': {}})
    assert not planbrister(annan_rb, p)
    andrad = p.model_copy(update={'tjansteplaner': (p.tjansteplaner[0].model_copy(update={'beskrivning': 'Förfalskad'}),)})
    assert planbrister(rb, andrad)


def test_bada_terminalposterna_forbjudna(rb, tmp_path):
    from tester.enhet.test_planens_genomforande import inford
    p = inford(rb, tmp_path / 'genomford')
    a = aterkallad(rb, tmp_path / 'aterkallad')
    data = p.tjansteplaner[0].model_dump(mode='json')
    data['aterkallelse'] = a.tjansteplaner[0].aterkallelse.model_dump(mode='json')
    with pytest.raises(ValidationError):
        m.Tjansteplan.model_validate(data)


def test_aterkallelse_bevarar_avgransad_modellbindning(rb):
    from riskanalys.drift.modellidentitet import modellbindning
    # Alla bedömningar och exporter behöver kunna bindas till den nya profilmodellen.
    assert modellbindning(rb).startswith('sha256:')
