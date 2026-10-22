from riskanalys.profil.lagring import profilrevision
from tester.intag.test_webb import webb, starta, anrop
from tester.fixturer.m2 import DAG


def urval(s, t, **val):
    d = dict(csrf=s.csrf, revision=profilrevision(t.profil()), urvalsformat='2',
        hela_listan='ja', underlag='eget', kalla='Syntetisk genomgång av tjänsterna',
        roll='Metodansvarig', datum=str(DAG))
    d.update({'tjanst_'+x.erbjuds_falt: 'bevara' for x in t.rb.tjanster.values()})
    d.update({'tjanst_'+k: v for k, v in val.items()})
    return d


def test_katalogforslag_ar_inte_byrans_fakta(webb):
    s, t = webb
    starta(s)
    p = t.profil()
    status, html, _ = anrop(s, 'tjanster')
    assert status == 200 and 'Ogranskat förslag' in html
    assert 'Arbetsmoment' in html and 'Befogenheter' in html
    assert t.profil() == p
    assert not any(p.ar_bekraftad(x.erbjuds_falt) for x in t.rb.tjanster.values())


def test_samlat_urval_skiljer_ja_nej_okant(webb):
    s, t = webb
    starta(s)
    d = urval(s, t, **{'P-TJ.red01_erbjuds': 'ja', 'P-TJ.red02_erbjuds': 'nej', 'P-TJ.red03_erbjuds': 'okant'})
    assert anrop(s, 'tjanster', d)[0] == 200
    p = t.profil()
    assert p.uppgifter['P-TJ.red01_erbjuds'].varde is True
    assert p.uppgifter['P-TJ.red02_erbjuds'].varde is False
    u = p.uppgifter['P-TJ.red03_erbjuds']
    assert u.varde is None and not p.ar_bekraftad('P-TJ.red03_erbjuds')
    assert all(p.uppgifter[f'P-TJ.red{i:02}_erbjuds'].kalla == d['kalla'] and
        p.uppgifter[f'P-TJ.red{i:02}_erbjuds'].datum == DAG and
        p.uppgifter[f'P-TJ.red{i:02}_erbjuds'].bekraftad_av.endswith('Metodansvarig') for i in (1, 2, 3))


def test_bevara_skriver_inte_over_tidigare_belagg(webb):
    s, t = webb
    starta(s)
    assert anrop(s, 'tjanster', urval(s, t, **{'P-TJ.red01_erbjuds': 'ja'}))[0] == 200
    p = t.profil()
    d = urval(s, t, **{'P-TJ.red02_erbjuds': 'nej'})
    d['kalla'] = 'Ett nytt annat underlag'
    assert anrop(s, 'tjanster', d)[0] == 200
    assert t.profil().uppgifter['P-TJ.red01_erbjuds'] == p.uppgifter['P-TJ.red01_erbjuds']


def test_osaker_ersatter_aldrig_tidigare_ja_med_bekraftat_ja(webb):
    s, t = webb
    starta(s)
    assert anrop(s, 'tjanster', urval(s, t, **{'P-TJ.red01_erbjuds': 'ja'}))[0] == 200
    assert anrop(s, 'tjanster', urval(s, t, **{'P-TJ.red01_erbjuds': 'okant'}))[0] == 200
    p = t.profil()
    assert p.uppgifter['P-TJ.red01_erbjuds'].varde is None
    assert not p.ar_bekraftad('P-TJ.red01_erbjuds')


def test_format_tva_kraver_alla_rader_och_belagg(webb):
    s, t = webb
    starta(s)
    p = t.profil()
    d = urval(s, t)
    d.pop('tjanst_P-TJ.red02_erbjuds')
    assert anrop(s, 'tjanster', d)[0] == 400 and t.profil() == p
    d = urval(s, t)
    d['kalla'] = ''
    assert anrop(s, 'tjanster', d)[0] == 400 and t.profil() == p
