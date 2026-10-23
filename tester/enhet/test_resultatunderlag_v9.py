"""Urvalet får inte tappa riskled, lokal osäkerhet eller ursprung vid delning."""
import pytest
from tester.fixturer.resultatrapport import resultatfall, underlag


def test_alla_avgorande_fore_och_efter_bevaras_per_dimension(resultatfall):
    f = resultatfall
    u = underlag(f)
    expected = {(t.tjanst, s.hot, s.dimension, led) for t in f.bedomning.tjanster if t.erbjuds
                for s in t.scenarier for led, valt in (
                    ('inneboende', s.avgorande), ('kvarstaende', s.dimension == 'pt'
                     and s.kvarstaende is not None and s.kvarstaende == t.kvarstaende)) if valt}
    actual = {(p.tjanst, h, p.dimension, p.riskled) for p in u.poster
              if 'avgor_fore' in p.skal or 'avgor_efter' in p.skal for h in p.hot}
    assert actual == expected


def test_lagre_tf_hot_forsvinner_inte_bakom_pt(resultatfall):
    u = underlag(resultatfall)
    assert {r.hot for r in u.matris if r.dimension == 'tf'} == {'H-03', 'H-TF-01', 'H-TF-02', 'H-TF-03'}


def test_gemensam_kedja_har_alla_tjanstemedlemmar(resultatfall):
    row = next(r for r in underlag(resultatfall).matris if r.hot == 'H-01' and r.dimension == 'pt')
    assert [c.tjanst for c in row.celler] == ['T-RED-01','T-RED-02','T-RED-03','T-RED-04']
    assert all(c.kallor and c.medlemmar for c in row.celler)


def test_samma_hot_med_olika_kontrolleffekt_bevarar_varje_cells_hela_scenario(resultatfall):
    row = next(r for r in underlag(resultatfall).matris if r.hot == 'H-01' and r.dimension == 'pt')
    assert [c.scenario.kvarstaende for c in row.celler] == ['hög','måttlig','måttlig','hög']
    for cell, t in zip(row.celler, (t for t in resultatfall.bedomning.tjanster if t.erbjuds), strict=True):
        assert cell.scenario == next(s for s in t.scenarier if s.hot == 'H-01' and s.dimension == 'pt')


def test_lika_niva_med_olika_mekanism_far_inte_samma_forklaring(resultatfall):
    f = resultatfall
    a = f.analys.tjanster[0]
    from riskanalys.analys.modeller import Scenarioanalys
    local = Scenarioanalys(id='eget-annat', hot=('H-01',), handelseforlopp='Helt annan lokal mekanism.',
                           relevans='relevant', motivering='Annat genomförande.')
    kopplingar = tuple(k.model_copy(update={'tillampning':'avviker','lokal_scenario':local.id})
                       if k.scenario == 'gem:H-01' else k for k in a.scenariokopplingar)
    nytt = a.model_copy(update={'scenarier':(*a.scenarier,local),'scenariokopplingar':kopplingar})
    paket = f.analys.model_copy(update={'tjanster':(nytt,*f.analys.tjanster[1:])})
    rows = [r for r in underlag(f, analys=paket).matris if r.hot == 'H-01' and r.dimension == 'pt']
    assert len(rows) == 2
    assert sorted(sum(c.status=='beraknad' for c in r.celler) for r in rows) == [1,3]


def test_matris_skiljer_saknat_ej_relevant_okant_och_tf_utan_efterniva(resultatfall):
    from riskanalys.dokument.resultatmodell_v9 import ScenariocellV9
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        ScenariocellV9(tjanst='T-RED-01',status='beraknad',scenario=None,medlemmar=(),kallor=())
    assert {ScenariocellV9(tjanst='T',status=s,scenario=None,medlemmar=(),kallor=()).status
            for s in ('saknas','ej_relevant','okant')} == {'saknas','ej_relevant','okant'}
    assert all(c.scenario.kvarstaende is None for r in underlag(resultatfall).matris
               if r.dimension == 'tf' for c in r.celler if c.scenario)


@pytest.mark.parametrize('status', ['bekraftad','antagande','kunskapslucka'])
def test_egen_sarbarhet_utan_motoraktivering_tas_med(resultatfall, status):
    from riskanalys.analys.modeller import GemensamSarbarhetsprovning
    p = GemensamSarbarhetsprovning(id='egen-test', omrade='verk', beskrivning='Egen risk utan katalog.',
                                 status=status, relevans='relevant', hot=('H-TF-01',))
    f = resultatfall
    paket = f.analys.model_copy(update={'gemensamma_sarbarhetsprovningar':(*f.analys.gemensamma_sarbarhetsprovningar,p)})
    u = underlag(f,analys=paket)
    assert any('egen_sarbarhet' in x.skal and any('/egen' in k.pointer or 'gemensamma_sarbarhetsprovningar' in k.pointer
               for k in x.kallor) for x in u.poster)


def test_antagande_och_okant_villkor_forblir_osakert(resultatfall):
    f = resultatfall
    p = f.analys.gemensamma_sarbarhetsprovningar[0].model_copy(update={'status':'antagande'})
    paket = f.analys.model_copy(update={'gemensamma_sarbarhetsprovningar':(p,*f.analys.gemensamma_sarbarhetsprovningar[1:])})
    assert any('osakerhet' in x.skal for x in underlag(f,analys=paket).poster)


def test_bekraftad_ej_relevant_post_far_bilagereferens(resultatfall):
    f = resultatfall
    p = f.analys.gemensamma_sarbarhetsprovningar[0].model_copy(update={'status':'bekraftad','relevans':'ej_relevant'})
    paket = f.analys.model_copy(update={'gemensamma_sarbarhetsprovningar':(p,*f.analys.gemensamma_sarbarhetsprovningar[1:])})
    assert any(x.hantering=='hanvisas' and 'ej_relevant' in x.skal for x in underlag(f,analys=paket).poster)


def test_d9_under_troskel_ar_inte_modellkonflikt(resultatfall):
    u = underlag(resultatfall)
    assert any('metoduppfoljning' in p.skal and p.hantering=='hanvisas' for p in u.poster)
    assert not any('under_troskel' in b.kod for b in u.brister)


def test_noll_egen_rapportering_aterges(resultatfall):
    assert any('erfarenhet' in p.skal for p in underlag(resultatfall).poster)


def test_kallpointer_pekar_pa_original_inte_lasvy(resultatfall):
    from riskanalys.dokument.resultatmodell_v9 import kallartefakter, los_referens
    f = resultatfall
    k = kallartefakter(f.regelbas,f.profil,f.bedomning,f.resultat,f.historik,f.analys,f.dokument)
    u = underlag(f)
    for p in u.poster:
        for ref in p.kallor:
            los_referens(k,ref)
    ref = u.poster[0].kallor[0]
    with pytest.raises(ValueError):
        los_referens(k,ref.model_copy(update={'summa':'sha256:'+'0'*64}))
