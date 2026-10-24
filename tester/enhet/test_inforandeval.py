"""Valet är en del av erbjudandetransaktionen, aldrig en implicit katalogordning."""
import pytest

from riskanalys.profil import forandringar as f, modeller as m
from riskanalys.profil.lagring import spara_profil, las_profil, profilrevision
from riskanalys.profil.planering import plansumma
from riskanalys.drift.historik import Historik, spara_historik, las_historik
from riskanalys.fel import RiskanalysFel
from tester.enhet.test_tjansteplanering import rb, profil, plan, ja, utvardering, DAG, upp


def lagra_planer(rb, mapp, antal=2):
    p = plan(profil())
    if antal == 2:
        p = p.model_copy(update={'tjansteplaner': (*p.tjansteplaner,
            p.tjansteplaner[0].model_copy(update={'id': 'alternativ', 'beskrivning': 'Ett annat införande'}))})
    spara_profil(mapp, p)
    h = tuple(utvardering(rb, p).model_copy(update={'plan_id': t.id, 'plansumma': plansumma(rb, p, t.id)})
              for t in p.tjansteplaner)
    spara_historik(mapp, Historik(handelser=h))
    return p


def test_bara_vald_plan_genomfors(rb, tmp_path):
    p = lagra_planer(rb, tmp_path)
    nytt = f.spara_andring(tmp_path, rb, ja(p), profilrevision(p),
                          planval=(m.Planval(tjanst='T-RED-01', plan_id='alternativ'),))
    assert nytt.tjansteplaner[0].genomforande is None
    assert nytt.tjansteplaner[1].genomforande is not None
    assert las_profil(tmp_path) == nytt


@pytest.mark.parametrize('antal', [1, 2])
def test_flera_eller_en_kandidat_utan_val_sparar_inget(rb, tmp_path, antal):
    p = lagra_planer(rb, tmp_path, antal)
    h = las_historik(tmp_path)
    with pytest.raises(RiskanalysFel, match='välj|Välj|planval'):
        f.spara_andring(tmp_path, rb, ja(p), profilrevision(p))
    assert las_profil(tmp_path) == p and las_historik(tmp_path) == h


@pytest.mark.parametrize('val', [
    (('T-RED-01', 'saknas'),), (('T-RED-02', 'ny'),),
    (('T-RED-01', 'ny'), ('T-RED-01', 'alternativ')),
])
def test_fel_tjanst_eller_dubblett_avvisas(rb, tmp_path, val):
    p = lagra_planer(rb, tmp_path)
    with pytest.raises(RiskanalysFel):
        f.spara_andring(tmp_path, rb, ja(p), profilrevision(p),
                       planval=tuple(m.Planval(tjanst=t, plan_id=id) for t, id in val))
    assert las_profil(tmp_path) == p


def test_fel_plantyp_och_val_utan_overgang_avvisas(rb, tmp_path):
    p = lagra_planer(rb, tmp_path, 1)
    p = p.model_copy(update={'tjansteplaner': (p.tjansteplaner[0].model_copy(update={'typ': 'ny_marknad'}),)})
    spara_profil(tmp_path, p)
    val = (m.Planval(tjanst='T-RED-01', plan_id='ny'),)
    for efter in (ja(p), p):
        with pytest.raises(RiskanalysFel):
            f.spara_andring(tmp_path, rb, efter, profilrevision(p), planval=val)


def test_alias_och_historiskt_nej_kraver_val(rb, tmp_path):
    p = profil().model_copy(update={'uppgifter': {'P-TJ.T-RED-01.erbjuds': upp(False)}})
    spara_profil(tmp_path, p)
    p = p.model_copy(update={'uppgifter': {}})
    spara_profil(tmp_path, p)
    behov = f.inforandebehov_for_andring(tmp_path, rb, ja(p), profilrevision(p))
    assert [(b.tjanst, b.kandidater) for b in behov] == [('T-RED-01', ())]
    with pytest.raises(RiskanalysFel):
        f.spara_andring(tmp_path, rb, ja(p), profilrevision(p))
    assert las_profil(tmp_path) == p


def test_forsta_kartlaggning_kraver_inte_plan(rb, tmp_path):
    p = profil().model_copy(update={'uppgifter': {}})
    spara_profil(tmp_path, p)
    assert f.inforandebehov_for_andring(tmp_path, rb, ja(p), profilrevision(p)) == ()
    assert f.spara_andring(tmp_path, rb, ja(p), profilrevision(p)).uppgifter['P-TJ.red01_erbjuds'].varde is True


def test_aterkallad_plan_sparrar_inte_nytt_inforande(rb, tmp_path):
    p = lagra_planer(rb, tmp_path)
    p = f.aterkalla_plan(tmp_path, rb, 'ny', DAG, 'Ansvarig', 'Väljer den andra planen', profilrevision(p))
    h = las_historik(tmp_path)
    nytt = f.spara_andring(tmp_path, rb, ja(p), profilrevision(p),
                          planval=(m.Planval(tjanst='T-RED-01', plan_id='alternativ'),))
    assert nytt.tjansteplaner[0].aterkallelse is not None
    assert nytt.tjansteplaner[0].genomforande is None
    assert nytt.tjansteplaner[1].genomforande is not None
    assert las_historik(tmp_path) == h


def test_aterkallad_plan_bar_inte_val(rb, tmp_path):
    p = lagra_planer(rb, tmp_path)
    p = f.aterkalla_plan(tmp_path, rb, 'ny', DAG, 'Ansvarig', 'Väljer den andra planen', profilrevision(p))
    behov = f.inforandebehov_for_andring(tmp_path, rb, ja(p), profilrevision(p))
    assert behov[0].kandidater == ('alternativ',)
    with pytest.raises(RiskanalysFel):
        f.spara_andring(tmp_path, rb, ja(p), profilrevision(p), planval=(m.Planval(tjanst='T-RED-01', plan_id='ny'),))
    assert las_profil(tmp_path) == p


def test_inaktuell_utvardering_och_andrad_kandidat_sparar_inget(rb, tmp_path):
    p = lagra_planer(rb, tmp_path)
    nytt = p.model_copy(update={'tjansteplaner': tuple(t.model_copy(update={'beskrivning': 'Ändrad plan'}) for t in p.tjansteplaner)})
    nytt = f.spara_andring(tmp_path, rb, nytt, profilrevision(p), lokalt_underlag=True)
    val = (m.Planval(tjanst='T-RED-01', plan_id='alternativ'),)
    with pytest.raises(RiskanalysFel, match='utvärdering'):
        f.spara_andring(tmp_path, rb, ja(nytt), profilrevision(nytt), planval=val)
    with pytest.raises(RiskanalysFel, match='ändrats'):
        f.spara_andring(tmp_path, rb, ja(p), profilrevision(p), planval=val)
    assert las_profil(tmp_path) == nytt


def test_historiken_tolkas_en_gang_per_kontroll_med_flera_nya_tjanster(rb, tmp_path, monkeypatch):
    # Varje sparat svar lägger ett profilsnapshot i historiken. Att läsa om alla per tjänst
    # gjorde varje sidvisning långsammare ju fler svar byrån hade lämnat.
    from pathlib import Path
    nej = profil().model_copy(update={'uppgifter': {'P-TJ.red02_erbjuds': upp(False)}})
    spara_profil(tmp_path, nej)
    p = nej
    for i in range(3):
        p = p.model_copy(update={'uppgifter': {'P-ORG.namn': upp(f'Syntetisk byrå {i}')}})
        spara_profil(tmp_path, p)
    assert len(list((tmp_path/'profil'/'historik').glob('*.yaml'))) == 3
    lasta = []
    for metod in ('read_text', 'read_bytes'):
        original = getattr(Path, metod)
        def raknad(self, *a, _o=original, **k):
            if 'historik' in self.parts:
                lasta.append(self.name)
            return _o(self, *a, **k)
        monkeypatch.setattr(Path, metod, raknad)
    efter = p.model_copy(update={'uppgifter': {**p.uppgifter, 'P-TJ.red01_erbjuds': upp(True),
                                               'P-TJ.red02_erbjuds': upp(True)}})
    behov = f.inforandebehov_for_andring(tmp_path, rb, efter, profilrevision(p))
    assert [b.tjanst for b in behov] == ['T-RED-02']
    assert len(lasta) == len(set(lasta)) <= 3
