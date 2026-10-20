"""Samlade svar ska ge samma belägg och spärrar som enskilda svar."""
import re

import pytest

from riskanalys.intag.tjanst import profilrevision
from riskanalys.profil.lagring import PROFILFIL
from riskanalys.profil.modeller import Period
from tester.fixturer.m2 import DAG
from tester.intag.test_underlagsval import lagg
from tester.intag.test_webb import anrop, starta, webb
from tester.intag.test_registerwebb import webb as registerwebb, hamta


def formular(s, t, grupp='kunder', **rader):
    return dict(csrf=s.csrf, revision=profilrevision(t.profil()), grupp=grupp,
                bekrafta='ja', underlag='eget', kalla='Syntetisk kundstatistik',
                datum=str(DAG), roll='Ansvarig', period_fran='2026-01-01',
                period_till=str(DAG), **rader)


def test_intervjun_visar_samlad_verksamhet_och_enskild_fraga_finns_kvar(webb):
    s, t = webb
    starta(s)
    html = anrop(s)[1]
    assert 'name="grupp" value="verksamhet"' in html
    assert 'name="text_P-ORG.namn"' in html
    assert 'name="text_P-VERK.bokforing"' in html
    assert 'name="falt" value="P-ORG.namn"' in anrop(s, '?falt=P-ORG.namn')[1]
    assert 'samlat?grupp=kunder' in anrop(s, 'samlat')[1]


def test_kundformular_samlar_antal_men_inte_kontroller_eller_andelar(webb):
    s, t = webb
    starta(s)
    status, html, _ = anrop(s, 'samlat?grupp=kunder')
    assert status == 200
    for id in ('P-KUND.antal_aktiva', 'P-KUND.antal_kontant', 'P-KANAL.antal_bankdata', 'P-GEO.antal_utland_agare'):
        assert f'name="text_{id}"' in html
    assert 'name="text_P-KONTROLL.' not in html
    assert 'name="text_P-KUND.andel_kontant"' not in html
    assert html.count('name="period_fran"') == 1
    assert html.count('name="kalla"') == 1
    assert 'name="text_P-KUND.antal_kontant" type="text" value=""' in html


def test_samlat_sparar_kalla_period_och_harleder_andelar(webb):
    s, t = webb
    starta(s)
    d = formular(s, t, **{'text_P-KUND.antal_aktiva': '10', 'text_P-KUND.antal_kontant': '2',
                           'text_P-KANAL.antal_bankdata': '0'})
    status, html, _ = anrop(s, 'samlat', d)
    assert status == 200, html
    p = t.profil()
    for id, value in [('P-KUND.antal_aktiva', 10), ('P-KUND.antal_kontant', 2), ('P-KANAL.antal_bankdata', 0)]:
        u = p.uppgifter[id]
        assert u.varde == value and p.ar_bekraftad(id)
        assert u.kalla == 'Syntetisk kundstatistik' and u.bekraftad_av == 'roll:Ansvarig'
        assert u.datum == DAG and str(u.period.fran) == '2026-01-01' and u.period.till == DAG
    assert p.uppgifter['P-KUND.andel_kontant'].varde == 0.2
    assert p.ar_bekraftad('P-KUND.andel_kontant')
    assert p.uppgifter['P-KUND.antal_riskbransch'].varde is None
    before = (t.mapp / PROFILFIL).read_bytes()
    assert anrop(s, 'samlat', d)[0] == 409
    assert (t.mapp / PROFILFIL).read_bytes() == before


def test_okant_bevarar_tidigare_belagg_och_kraver_inte_roll_eller_period(webb):
    s, t = webb
    starta(s)
    lagg(t, 'P-ORG.namn', 'Syntetisk byrå', 'Tidigare källa')
    old = t.profil().uppgifter['P-ORG.namn']
    d = formular(s, t, 'verksamhet', **{'status_P-ORG.namn': 'okänt',
                 'text_P-ORG.namn': 'Detta ska inte ersätta',
                 'motivering_P-ORG.namn': 'Kontrollera med ansvarig'})
    d.update(bekrafta='', roll='', kalla='', period_fran='', period_till='')
    assert anrop(s, 'samlat', d)[0] == 200
    u = t.profil().uppgifter['P-ORG.namn']
    assert u.varde == old.varde and u.kalla == old.kalla and u.datum == old.datum
    assert u.bekraftad_av == old.bekraftad_av and u.status == 'föreslagen'


def test_blandade_svar_och_uttryckligt_nej_fungerar(webb):
    s, t = webb
    starta(s)
    d = formular(s, t, 'verksamhet', **{'text_P-ORG.namn': 'Syntetisk byrå',
                   'text_P-VERK.bokforing': 'nej', 'status_P-ORG.koncernmoder': 'okänt',
                   'motivering_P-ORG.koncernmoder': 'Kontrollera strukturen'})
    d.update(underlag='egen_kannedom', period_fran='', period_till='')
    status, html, _ = anrop(s, 'samlat', d)
    assert status == 200, html
    p = t.profil()
    assert p.uppgifter['P-VERK.bokforing'].varde is False
    assert p.uppgifter['P-ORG.namn'].kalla == 'Egen kännedom om verksamheten'
    assert p.uppgifter['P-ORG.koncernmoder'].status == 'föreslagen'
    assert not p.ar_bekraftad('P-VERK.skatteradgivning')


@pytest.mark.parametrize('extra', [
    {'bekrafta': ''}, {'kalla': ''}, {'period_fran': ''},
    {'period_fran': '', 'period_till': ''}, {'period_till': '2027-01-01'},
    {'text_P-KUND.antal_kontant': '-1'}, {'text_P-KUND.antal_kontant': 'fel'},
    {'status_P-KUND.antal_kontant': 'okänt', 'motivering_P-KUND.antal_kontant': ''},
    {'underlag': 'egen_kannedom'}, {'underlag': 'hittat_pa'},
    {'text_P-KONTROLL.C-07.genomforande': 'belagt'},
    {'text_P-VERK.omsattning': '10'}, {'text_P-KUND.andel_kontant': '0.2'},
    {'status_P-KUND.antal_kontant': 'ej_tillämplig'}, {'okant_falt': 'x'},
])
def test_fel_i_en_rad_sparar_ingenting(webb, extra):
    s, t = webb
    starta(s)
    d = formular(s, t, **{'text_P-KUND.antal_aktiva': '10', 'text_P-KUND.antal_kontant': '2'})
    d.update(extra)
    before = (t.mapp / PROFILFIL).read_bytes()
    status, html, _ = anrop(s, 'samlat', d)
    assert status == 400, html
    assert (t.mapp / PROFILFIL).read_bytes() == before
    assert 'name="text_P-KUND.antal_aktiva" type="text" value="10"' in html


def test_osparade_inmatningar_escapas_och_revision_bevaras_vid_fel(webb):
    s, t = webb
    starta(s)
    d = formular(s, t, 'beskrivningar', **{'text_P-BESK.verksamhet': '<script>syntetiskt</script>'})
    d.update(bekrafta='', period_fran='', period_till='')
    status, html, _ = anrop(s, 'samlat', d)
    assert status == 400
    assert '&lt;script&gt;syntetiskt&lt;/script&gt;' in html
    assert '<script>syntetiskt</script>' not in html
    assert f'name="revision" value="{d["revision"]}"' in html


def test_sparade_svar_undantas_som_standard_och_kan_lamnas_ororda(webb):
    s, t = webb
    starta(s)
    lagg(t, 'P-ORG.namn', 'Syntetisk byrå', 'Ursprungligt underlag')
    old = t.profil().uppgifter['P-ORG.namn']
    html = anrop(s, 'samlat?grupp=verksamhet')[1]
    assert re.search(r'name="status_P-ORG.namn".*?<option value="behall" selected', html)
    d = formular(s, t, 'verksamhet', **{'text_P-ORG.namn': 'Ska ignoreras',
                        'status_P-ORG.namn': 'behall', 'text_P-VERK.bokforing': 'ja'})
    d.update(underlag='egen_kannedom', period_fran='', period_till='')
    assert anrop(s, 'samlat', d)[0] == 200
    assert t.profil().uppgifter['P-ORG.namn'] == old


def test_andrad_bas_omprovar_osparade_foljdsvar(webb):
    s, t = webb
    starta(s)
    d = formular(s, t, **{'text_P-KUND.antal_aktiva': '10', 'text_P-KUND.antal_kontant': '2'})
    assert anrop(s, 'samlat', d)[0] == 200
    d = formular(s, t, **{'text_P-KUND.antal_aktiva': '20'})
    assert anrop(s, 'samlat', d)[0] == 200
    assert not t.profil().ar_bekraftad('P-KUND.antal_kontant')
    assert t.profil().uppgifter['P-KUND.antal_kontant'].varde == 2


def test_tjanstefragor_kraver_bekraftat_erbjudad_tjanst(webb):
    s, t = webb
    starta(s)
    d = formular(s, t, 'tjanst-T-RED-01', **{'text_P-TJ.red01_arbetssatt': 'Syntetiskt arbetssätt'})
    assert anrop(s, 'samlat', d)[0] == 400
    lagg(t, 'P-TJ.red01_erbjuds', 'ja', 'Egen genomgång')
    status, html, _ = anrop(s, 'samlat?grupp=tjanst-T-RED-01')
    assert status == 200 and 'name="text_P-TJ.red01_arbetssatt"' in html
    assert 'name="text_P-TJ.red02_arbetssatt"' not in html


def test_samlat_behaller_webbskydd_och_rensar_utkast_enbart_efter_sparning(webb):
    s, t = webb
    starta(s)
    d = formular(s, t, **{'text_P-KUND.antal_aktiva': '10'})
    before = (t.mapp / PROFILFIL).read_bytes()
    s.utkast = 'gammalt-utkast'
    assert anrop(s, 'samlat', d, {'Origin': 'https://evil.example'})[0] == 403
    assert anrop(s, 'samlat', {**d, 'csrf': 'fel'})[0] == 403
    assert (t.mapp / PROFILFIL).read_bytes() == before and s.utkast == 'gammalt-utkast'
    assert anrop(s, 'samlat', d)[0] == 200
    assert s.utkast is None and anrop(s, 'word')[0] == 404


def test_tomt_urval_och_okand_grupp_ger_fel_utan_sparning(webb):
    s, t = webb
    starta(s)
    before = (t.mapp / PROFILFIL).read_bytes()
    assert anrop(s, 'samlat', formular(s, t))[0] == 400
    assert anrop(s, 'samlat?grupp=okand')[0] == 400
    assert anrop(s, 'samlat', formular(s, t, 'okand'))[0] == 400
    assert (t.mapp / PROFILFIL).read_bytes() == before


def test_tidigare_underlag_far_anvandas_bara_for_ratt_period_och_kategori(webb):
    s, t = webb
    starta(s)
    lagg(t, 'P-KUND.antal_aktiva', '10', 'Syntetiskt kundregister', Period(fran=DAG.replace(month=1, day=1), till=DAG))
    html = anrop(s, 'samlat?grupp=kunder')[1]
    token = re.search(r'<option value="(tidigare:[^"]+)"', html)[1]
    d = formular(s, t, **{'text_P-KUND.antal_kontant': '2'})
    d.update(underlag=token, period_fran='2026-02-01')
    before = (t.mapp / PROFILFIL).read_bytes()
    assert anrop(s, 'samlat', d)[0] == 400
    assert (t.mapp / PROFILFIL).read_bytes() == before
    d = formular(s, t, 'ekonomi', **{'text_P-VERK.omsattning': '100'})
    d['underlag'] = token
    assert anrop(s, 'samlat', d)[0] == 400
    assert (t.mapp / PROFILFIL).read_bytes() == before
    d = formular(s, t, **{'text_P-KUND.antal_kontant': '2'})
    d['underlag'] = token
    assert anrop(s, 'samlat', d)[0] == 200
    assert t.profil().uppgifter['P-KUND.antal_kontant'].kalla == 'Syntetiskt kundregister'


def test_gammal_flik_bevarar_revision_i_felvyn_och_kan_inte_sparas_igen(webb):
    s, t = webb
    starta(s)
    d = formular(s, t, **{'text_P-KUND.antal_aktiva': '10'})
    lagg(t, 'P-ORG.namn', 'Nyare svar', 'Syntetiskt underlag')
    before = (t.mapp / PROFILFIL).read_bytes()
    for _ in range(2):
        status, html, _ = anrop(s, 'samlat', d)
        assert status == 409
        assert f'name="revision" value="{d["revision"]}"' in html
        assert (t.mapp / PROFILFIL).read_bytes() == before


def test_flera_giltiga_langa_svar_ryms_i_samma_formular(webb):
    s, t = webb
    starta(s)
    d = formular(s, t, 'beskrivningar', **{'text_P-BESK.verksamhet': 'å' * 6000,
                       'text_P-BESK.geografi': 'å' * 6000})
    d.update(underlag='egen_kannedom', period_fran='', period_till='')
    assert anrop(s, 'samlat', d)[0] == 200
    assert t.profil().uppgifter['P-BESK.verksamhet'].varde == 'å' * 6000
    assert t.profil().uppgifter['P-BESK.geografi'].varde == 'å' * 6000


def test_samlat_avvisar_alltfor_stor_kropp_utan_sparning(webb):
    from http.client import HTTPConnection
    s, t = webb
    starta(s)
    before = (t.mapp / PROFILFIL).read_bytes()
    # Servern ska avvisa längden före kroppsläsning; undvik klientens BrokenPipe
    # när den annars fortsätter sända en redan avvisad stor kropp.
    conn = HTTPConnection('127.0.0.1', s.server_port, timeout=5)
    try:
        conn.putrequest('POST', s.prefix + 'samlat')
        conn.putheader('Origin', s.origin)
        conn.putheader('Content-Type', 'application/x-www-form-urlencoded')
        conn.putheader('Content-Length', '1100000')
        conn.endheaders()
        response = conn.getresponse()
        assert response.status == 413
        response.read()
    finally:
        conn.close()
    assert (t.mapp / PROFILFIL).read_bytes() == before


def test_registerforslag_bevaras_utan_nastlade_formular_eller_automatisk_bekraftelse(registerwebb):
    from html.parser import HTMLParser

    class Formular(HTMLParser):
        def __init__(self):
            super().__init__()
            self.djup = 0
            self.maxdjup = 0
            self.actions = []
            self.ids = []

        def handle_starttag(self, tag, attrs):
            d = dict(attrs)
            if tag == 'form':
                self.djup += 1
                self.maxdjup = max(self.djup, self.maxdjup)
                self.actions.append(d.get('action'))
            if 'id' in d:
                self.ids.append(d['id'])

        def handle_endtag(self, tag):
            if tag == 'form':
                self.djup -= 1

    s, t = registerwebb
    starta(s)
    hamta(s)
    before = (t.mapp / PROFILFIL).read_bytes()
    status, html, _ = anrop(s)
    assert status == 200 and 'Syntetisk byrå AB' in html
    forms = Formular()
    forms.feed(html)
    assert forms.actions.count(s.prefix + 'registersamlat') == 1
    assert forms.actions.count(s.prefix + 'samlat') == 1
    assert forms.maxdjup == 1 and forms.djup == 0
    assert len(forms.ids) == len(set(forms.ids))
    assert (t.mapp / PROFILFIL).read_bytes() == before
    assert not t.profil().ar_bekraftad('P-ORG.namn')
