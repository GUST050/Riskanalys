"""Planval och återkallelse genom riktiga skyddade HTTP-/CLI-gränser."""
import threading
import pytest

from riskanalys.intag.webb import skapa_server
from riskanalys.intag.modeller import IntagSvar
from riskanalys.intag.utvardering import registrera_utvardering
from riskanalys.profil.modeller import Tjansteplan
from riskanalys.profil.lagring import profilrevision
from riskanalys.drift.historik import las_historik
from riskanalys.cli import main
from tester.intag.test_webb import anrop
from tester.intag.test_tjansteplanering import tjanst, svar
from tester.fixturer.m2 import DAG


@pytest.fixture
def server(tjanst):
    s = skapa_server(tjanst)
    trad = threading.Thread(target=s.serve_forever, daemon=True)
    trad.start()
    yield s
    s.shutdown()
    s.server_close()
    trad.join(timeout=2)


def planer(t):
    p = t.spara_flera(tuple(IntagSvar(falt=f'P-TJ.red{i:02}_erbjuds', text='nej',
        kalla='Syntetiskt utbud', datum=DAG) for i in (1, 2)), profilrevision(t.profil()))
    for id, tjanst_id in (('ett', 'T-RED-01'), ('alternativ', 'T-RED-01'), ('tva', 'T-RED-02')):
        p = t.spara_plan(Tjansteplan(id=id, tjanst=tjanst_id, typ='ny_tjanst',
            beskrivning='Planerade uppdrag med dokumenterad insyn'), profilrevision(p))
    for plan in p.tjansteplaner:
        registrera_utvardering(t, DAG, 'Prövat hot och sårbarheter mot underlaget samt rutinerna.',
                               profilrevision(p), plan_id=plan.id)
    return p


def urval(s, p):
    return dict(csrf=s.csrf, revision=profilrevision(p), hela_listan='ja', underlag='eget',
        kalla='Bevara hela underlaget', roll='Metodansvarig', datum=str(DAG),
        **{'tjanst_P-TJ.red01_erbjuds': 'ja', 'tjanst_P-TJ.red02_erbjuds': 'ja'})


def test_tva_inforanderader_med_ett_fel_sparar_inget(tjanst, server):
    p = planer(tjanst)
    h = las_historik(tjanst.mapp)
    data = {**urval(server, p), 'plan_T-RED-01': 'alternativ', 'plan_T-RED-02': 'saknas'}
    assert anrop(server, 'tjanster', data)[0] == 400
    assert tjanst.profil() == p and las_historik(tjanst.mapp) == h


def test_planval_visas_per_rad_och_belagg_bevaras(tjanst, server):
    p = planer(tjanst)
    data = urval(server, p)
    status, html, _ = anrop(server, 'tjanster', data)
    assert status == 400 and tjanst.profil() == p
    assert 'name="plan_T-RED-01"' in html and 'name="plan_T-RED-02"' in html
    assert 'Bevara hela underlaget' in html and 'Metodansvarig' in html
    assert 'value="alternativ"' in html
    import re
    val = re.search(r'name="tjanst_P-TJ.red01_erbjuds"[^>]*>(.*?)</select>', html, re.S)
    assert val and '<option value="ja" selected>' in val.group(1)
    data.update({'plan_T-RED-01': 'alternativ', 'plan_T-RED-02': 'tva'})
    assert anrop(server, 'tjanster', data)[0] == 200
    p = tjanst.profil()
    assert {t.id for t in p.tjansteplaner if t.genomforande} == {'alternativ', 'tva'}
    assert all(p.uppgifter[f'P-TJ.red{i:02}_erbjuds'].kalla == 'Bevara hela underlaget' for i in (1, 2))


def test_stale_urval_bevaras_for_ny_jamforelse(tjanst, server):
    p = planer(tjanst)
    data = urval(server, p)
    tjanst.spara_plan(Tjansteplan(id='senare', tjanst='T-RED-02', typ='ny_tjanst',
        beskrivning='Ett senare alternativ'), profilrevision(p))
    ny = tjanst.profil()
    status, html, _ = anrop(server, 'tjanster', data)
    assert status == 409 and tjanst.profil() == ny
    assert 'Bevara hela underlaget' in html
    assert f'name="revision" value="{profilrevision(ny)}"' in html
    assert 'jämför' in html.lower() and 'senare' in html


def test_aterkallelse_webb_cli_terminal_sida_och_rapport(tjanst, server):
    p = planer(tjanst)
    data = dict(csrf=server.csrf, revision=profilrevision(p), plan_id='ett', datum=str(DAG),
                ansvarig='Ansvarig funktion', motivering='<script>Övergiven avsikt</script>')
    assert anrop(server, 'planaterkalla', {**data, 'csrf': 'fel'})[0] == 403
    assert anrop(server, 'planaterkalla', data, {'Origin': 'https://evil.example'})[0] == 403
    assert anrop(server, 'planaterkalla', data)[0] == 200
    assert anrop(server, 'planaterkalla', data)[0] == 409
    status, html, _ = anrop(server, 'planering?plan=ett')
    assert status == 200 and 'Återkallad' in html
    assert '&lt;script&gt;' in html and '<script>Övergiven' not in html
    assert 'name="beskrivning"' not in html and 'planutvardera' not in html
    assert main(['aterkalla-plan', tjanst.mapp.name, 'alternativ', '--ansvarig', 'Ansvarig',
                 '--motivering', 'Övergivet alternativ', '--datum', str(DAG)]) == 0
    from riskanalys.dokument.forandringar_v8 import planunderlag
    text = ' '.join(s.text for s in planunderlag(tjanst.profil(), las_historik(tjanst.mapp)))
    assert 'Återkallad' in text and 'Övergivet alternativ' in text and 'Historisk' in text


def test_enskilt_inforande_kraver_planval_i_webb_och_cli(tjanst, server):
    p = planer(tjanst)
    data = dict(csrf=server.csrf, revision=profilrevision(p), falt='P-TJ.red01_erbjuds', text='ja',
                kalla='Syntetiskt avtal', datum=str(DAG), roll='Metodansvarig')
    status, html, _ = anrop(server, 'svar', data)
    assert status == 400 and 'name="plan_id"' in html and tjanst.profil() == p
    assert anrop(server, 'svar', {**data, 'plan_id': 'alternativ'})[0] == 200
    assert main(['bekrafta', tjanst.mapp.name, 'P-TJ.red02_erbjuds', 'ja', '--kalla', 'Syntetiskt avtal',
                 '--datum', str(DAG), '--plan', 'tva']) == 0
    assert {t.id for t in tjanst.profil().tjansteplaner if t.genomforande} == {'alternativ', 'tva'}


def test_okanda_planfalt_och_for_stora_formular_avvisas(tjanst, server):
    p = planer(tjanst)
    d = urval(server, p)
    assert anrop(server, 'tjanster', {**d, 'plan_saknas': 'ett'})[0] == 400
    assert anrop(server, 'tjanster', {**d, **{f'extra_{i}': 'x' for i in range(65)}})[0] == 400
    assert tjanst.profil() == p


def test_aterkallelsens_etiketter_pekar_pa_egna_falt(tjanst, server):
    from html.parser import HTMLParser
    planer(tjanst)
    status, html, _ = anrop(server, 'planering?plan=ett')
    assert status == 200
    class Etiketter(HTMLParser):
        def __init__(self):
            super().__init__()
            self.aterkallelse = False
            self.ids = []
            self.mal = []
        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if tag == 'form':
                self.aterkallelse = a.get('action', '').endswith('planaterkalla')
            if a.get('id'):
                self.ids.append(a['id'])
            if tag == 'label' and self.aterkallelse and a.get('for'):
                self.mal.append(a['for'])
    parser = Etiketter()
    parser.feed(html)
    assert len(parser.mal) == 2
    assert all(parser.ids.count(id) == 1 for id in parser.mal), 'Återkallelsens etiketter måste peka på unika egna datum-/ansvarigfält.'
