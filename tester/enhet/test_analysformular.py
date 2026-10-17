"""Typade HTML-adaptrar får ändra svar, aldrig skapa en attest."""
from html.parser import HTMLParser

import pytest

from riskanalys.analys.modeller import Tjansteanalys
from riskanalys.fel import RiskanalysFel
from tester.enhet.test_analysguide import paket


class Kontroller(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.namn = []; self.feed(text)

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag in ('input', 'select', 'textarea'):
            self.namn.append(d.get('name'))


def test_guidad_html_visar_typade_uppdragsfalt_utan_json():
    from riskanalys.intag.analysvy import blockformular
    html = blockformular(paket(), 'T-0', 4, prefix='/privat/', csrf='token', revision='summa')
    namn = Kontroller(html).namn
    assert 'uppdragsprovning.status' in namn
    assert 'uppdragsprovning.handlingsalternativ' in namn
    assert 'uppdragsprovning.kompetens_och_insyn' in namn
    assert 'jsontext' not in namn
    assert 'Spara utkast' in html and 'Spara och bekräfta visade svar' in html
    assert 'Godkänn analys' not in html


def test_utkast_bevarar_annat_block_och_skapar_inte_bekraftelse():
    from riskanalys.intag.analysformular import las_blockformular
    p = paket()
    resultat = las_blockformular(p, 'T-0', 13, {'pt_motivering': '  Lokal PT  ', 'operation': 'spara', 'forfattare': ' Anna ', 'aktivering': 'aktiv', 'aktiveringsmotivering': 'Prövat'})
    assert resultat.tjanst.pt_motivering == 'Lokal PT'
    assert resultat.tjanst.tf_motivering == ''
    assert resultat.tjanst.forfattare is None
    assert not resultat.tjanst.block[12].bekraftad_summa
    assert resultat.operation == 'spara'
    assert resultat.forfattare == 'Anna'


@pytest.mark.parametrize('data', [
    {'profil.kunder': '999'}, {'pt_motivering': 'x', 'operation': 'godkann'},
    {'pt_motivering': 'x', 'revision': 'r', 'egen_granskning': 'ja'},
])
def test_frammande_faktanycklar_och_godkannande_avvisas(data):
    from riskanalys.intag.analysformular import las_blockformular
    with pytest.raises(RiskanalysFel):
        las_blockformular(paket(), 'T-0', 13, data)


def test_ny_typad_scenario_rad_laggs_till_utan_att_dela_bekraftelse():
    from riskanalys.intag.analysformular import las_blockformular
    r = las_blockformular(paket(), 'T-0', 6, {'operation': 'spara', 'forfattare': 'Anna', 'aktivering': 'aktiv', 'scenarier.1.anvand': 'ja', 'scenarier.1.id': 'ny', 'scenarier.1.rubrik': 'Nytt scenario', 'scenarier.1.hot': 'H-1, H-2', 'scenarier.1.relevans': 'relevant'})
    assert len(r.tjanst.scenarier) == 2
    assert r.tjanst.scenarier[1].hot == ('H-1', 'H-2')
    assert not r.tjanst.scenariokopplingar


def test_sparad_text_och_fel_escapas():
    from riskanalys.intag.analysvy import blockformular
    html = blockformular(paket(), 'T-0', 13, prefix='/p/', csrf='c', revision='r', data={'pt_motivering': '</textarea><script>fel</script>'}, fel='<img onerror=x>')
    assert '<script>' not in html and '<img onerror=x>' not in html
    assert '&lt;script&gt;' in html and '&lt;img onerror=x&gt;' in html


def test_delat_scenario_har_inget_forvalt_samma_och_kraver_visad_summa():
    from riskanalys.intag.analysvy import scenarioformular
    from riskanalys.intag.analysformular import las_scenarioval
    from riskanalys.analys.provning import scenariosumma
    p = paket()
    html = scenarioformular(p, 'T-0', 'gem', prefix='/p/', csrf='c', revision='r')
    assert 'value="samma" selected' not in html
    assert 'value="avviker" selected' not in html
    with pytest.raises(RiskanalysFel):
        las_scenarioval(p, 'T-0', 'gem', {'tillampning': 'samma', 'visad_summa': 'gammal'})
    with pytest.raises(RiskanalysFel):
        las_scenarioval(p, 'T-0', 'gem', {'visad_summa': scenariosumma(p.gemensamma_scenarier[0])})
    k = las_scenarioval(p, 'T-0', 'gem', {'tillampning': 'samma', 'visad_summa': scenariosumma(p.gemensamma_scenarier[0])})
    assert k.tillampning == 'samma'
    assert k.bekraftad is False


def test_delad_avvikelse_kraver_lokal_variant_och_motivering():
    from riskanalys.intag.analysformular import las_scenarioval
    from riskanalys.analys.provning import scenariosumma
    p = paket()
    d = {'tillampning': 'avviker', 'visad_summa': scenariosumma(p.gemensamma_scenarier[0]), 'lokal_scenario': 'lokal-1', 'motivering': 'Annat arbetsmoment'}
    with pytest.raises(RiskanalysFel):
        las_scenarioval(p, 'T-0', 'gem', d)
    d['lokal_scenario'] = 'lokal-0'
    assert las_scenarioval(p, 'T-0', 'gem', d).lokal_scenario == 'lokal-0'


def test_ogiltig_extra_rad_avvisas_utan_att_andra_original():
    from riskanalys.intag.analysformular import las_blockformular
    p = paket()
    with pytest.raises(RiskanalysFel):
        las_blockformular(p, 'T-0', 6, {'scenarier.999.id': 'smyg'})
    assert len(p.tjanster[0].scenarier) == 1


@pytest.mark.parametrize('nummer', range(1, 17))
def test_varje_guidesteg_har_vanliga_falt_och_separata_operationer(nummer):
    from riskanalys.intag.analysvy import blockformular
    html = blockformular(paket(), 'T-0', nummer, prefix='/p/', csrf='c', revision='r')
    namn = Kontroller(html).namn
    assert 'forfattare' in namn and 'visad_summa' in namn
    assert 'operation' not in namn  # operation väljs av separat submit-knapp
    assert '<textarea' in html
    assert 'value="spara"' in html and 'value="bekrafta"' in html


def test_ogiltigt_typat_statusval_ger_kort_svenskt_fel():
    from riskanalys.intag.analysformular import las_blockformular
    with pytest.raises(RiskanalysFel, match='Kontrollera status'):
        las_blockformular(paket(), 'T-0', 4, {'uppdragsprovning.handlingsalternativ': 'skicka_till_kund'})


def test_redigerade_visade_svar_far_bekraftas_med_aktuell_bassumma():
    from riskanalys.intag.analysformular import las_blockformular
    from riskanalys.analys.provning import blocksumma
    p = paket()
    with pytest.raises(RiskanalysFel):
        las_blockformular(p, 'T-0', 13, {'operation': 'bekrafta', 'visad_summa': 'gammal'})
    andrat = las_blockformular(p, 'T-0', 13, {'operation': 'bekrafta', 'visad_summa': blocksumma(p, 'T-0', 13), 'pt_motivering': 'Ändrad analys'})
    assert andrat.tjanst.pt_motivering == 'Ändrad analys'
    assert andrat.operation == 'bekrafta'
    assert andrat.tjanst.block[12].bekraftad_summa is None
    r = las_blockformular(p, 'T-0', 13, {'operation': 'bekrafta', 'visad_summa': blocksumma(p, 'T-0', 13)})
    assert r.operation == 'bekrafta'
    assert r.tjanst.block[12].bekraftad_summa is None


def test_befintlig_radidentitet_far_inte_skrivas_om():
    from riskanalys.intag.analysformular import las_blockformular
    with pytest.raises(RiskanalysFel):
        las_blockformular(paket(), 'T-0', 6, {'scenarier.0.id': 'annat-id'})


def test_okant_belagg_och_scenarioreferens_avvisas():
    from riskanalys.intag.analysformular import las_blockformular
    with pytest.raises(RiskanalysFel):
        las_blockformular(paket(), 'T-0', 1, {'exponeringsbelagg': 'B-finns-inte'})
    with pytest.raises(RiskanalysFel):
        las_blockformular(paket(), 'T-0', 10, {'kontroller.0.anvand': 'ja', 'kontroller.0.scenario': 'lokal-1', 'kontroller.0.kontroll': 'K-test'})


def test_tekniska_enumvarden_har_svenska_synliga_etiketter():
    from riskanalys.intag.analysvy import blockformular
    html = blockformular(paket(), 'T-0', 4, prefix='/p/', csrf='c', revision='r')
    assert '>Kan inte hanteras</option>' in html
    assert '>Avböj uppdrag</option>' in html
    assert '>kan inte hanteras</option>' not in html


def test_katalogreferenser_avvisas_nar_de_inte_tillhor_tjansten():
    from riskanalys.intag.analysformular import las_blockformular
    from riskanalys.regelverk.laddning import ladda_regelbas
    from riskanalys.analys.modeller import Tjansteanalys
    rb = ladda_regelbas()
    p = paket().model_copy(update={'tjanster': (Tjansteanalys(tjanst='T-RED-01'),)})
    with pytest.raises(RiskanalysFel):
        las_blockformular(p, 'T-RED-01', 6, {'scenarier.0.anvand': 'ja', 'scenarier.0.id': 'ny', 'scenarier.0.hot': 'H-FINNS-INTE'}, rb=rb)


def test_villkorat_ej_aktivt_block_kraver_inte_pahittad_fritext():
    from riskanalys.intag.analysformular import las_blockformular
    r = las_blockformular(paket(), 'T-0', 3, {'aktivering': 'ej_tillamplig', 'aktiveringsmotivering': 'Inga betalningsmoment i uppdraget'})
    assert r.tjanst.betalningsinsyn.synliga_floden == ''
    assert r.tjanst.block[2].aktivering == 'ej_tillamplig'


def test_upprepade_belaggsid_avvisas_som_dubbelreferens():
    from riskanalys.analys.modeller import Analysbelagg
    from riskanalys.intag.analysformular import las_blockformular
    from datetime import date
    p = paket().model_copy(update={'belagg': (Analysbelagg(id='B-1', profilfalt=('P-test',), datum=date(2026, 1, 1)),)})
    with pytest.raises(RiskanalysFel):
        las_blockformular(p, 'T-0', 1, {'exponeringsbelagg': 'B-1,B-1'})


def test_oversikt_visar_sparad_forfattare_och_granskare():
    from datetime import date
    from riskanalys.analys.modeller import Analysbeslut
    from riskanalys.analys.provning import registrera_beslut, underlagssumma, svarssumma
    from riskanalys.intag.analysvy import analysoversikt
    p = paket()
    a = p.tjanster[0].model_copy(update={'forfattare':'Syntetisk Ada'})
    p = p.model_copy(update={'tjanster':(a, *p.tjanster[1:])})
    b = Analysbeslut(tjanst=a.tjanst, revision=p.revision, underlagssumma=underlagssumma(p), svarssumma=svarssumma(p), godkand=True, namn='Syntetisk Bo', roll='Ansvarig', datum=date(2026,1,1))
    p = registrera_beslut(p, b)
    html = analysoversikt(p, prefix='/p/')
    assert 'Syntetisk Ada' in html and 'Syntetisk Bo' in html and 'Ansvarig' in html
    assert 'Samma person har skrivit och godkänt' not in html
