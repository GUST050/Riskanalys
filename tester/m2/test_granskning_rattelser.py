"""Regressioner för fynden i den externa M2-granskningen."""
from datetime import date
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
import yaml

from riskanalys.bedomning.motor import bedom
from riskanalys.dokument.underlag import bygg_underlag
from riskanalys.profil.hantering import bekrafta, skapa_profil
from riskanalys.profil.modeller import Byra, Uppgift
from riskanalys.regelverk.laddning import STANDARD_REGELBAS, ladda_regelbas
from riskanalys.regelverk.urval import valj
from riskanalys.regelverk.validering import validera
from tester.fixturer.m2 import komplett_profil

DAG = date(2026, 10, 10)


def profil(rb):
    p = skapa_profil(rb, Byra(id='syntetisk', regelpaket='RP-RED-VG', datum=DAG, lan='Västra Götaland'))
    return komplett_profil(rb, p)


@pytest.mark.parametrize('version', ['2.0.0', '10.0.0'])
def test_ny_innehallsversion_bevarar_m2_grindar_och_integritet(regelbas_v1, version):
    rb = regelbas_v1.model_copy(update={'version': version})
    p = profil(rb)
    u = p.uppgifter['P-TJ.red01_antal_kunder'].model_copy(update={'status': 'saknas', 'varde': None})
    p = p.model_copy(update={'uppgifter': {**p.uppgifter, 'P-TJ.red01_antal_kunder': u}})
    b = bedom(rb, valj(rb, p.byra.regelpaket, DAG, p.byra.lan), p)
    assert b.omfattning is not None
    t = next(t for t in b.tjanster if t.tjanst == 'T-RED-01')
    assert t.sanktionsrisk is not None
    a = bygg_underlag(rb, p, t, 'D-ARB.6.1')
    assert next(u for u in a.uppgifter if u.id == 'P-TJ.red01_omsattning').varde == 'okänt'
    rb = rb.model_copy(update={'sanktionsmetod': None, 'kundmall': None})
    assert any('sanktionsmetod' in f for f in validera(rb))
    assert any('kundmall' in f for f in validera(rb))


def test_oberoende_bekraftelse_bevarar_gammal_andel_och_belagg(regelbas_v1):
    p = profil(regelbas_v1)
    gammal = Uppgift(varde=.2, status='bekräftad', kalla='Kundregistret 2026-09-30',
                    datum=DAG, bekraftad_av='Syntetisk granskare')
    uppgifter = {**p.uppgifter, 'P-KUND.andel_riskbransch': gammal}
    uppgifter['P-KUND.antal_riskbransch'] = Uppgift()
    p = p.model_copy(update={'uppgifter': uppgifter})
    ny = bekrafta(p, regelbas_v1, 'P-ORG.antal_anstallda', '2', 'Syntetisk personalförteckning', 'FfR', DAG)
    u = ny.uppgifter['P-KUND.andel_riskbransch']
    assert u.varde == gammal.varde and u.kalla == gammal.kalla
    assert u.datum == gammal.datum and u.bekraftad_av == gammal.bekraftad_av
    assert u.inaktuell
    assert not ny.ar_bekraftad('P-KUND.andel_riskbransch')
    assert ny.faltvarden()['P-KUND.andel_riskbransch'].varde is None


def test_import_med_okant_paket_ger_svenskt_fel_utan_stacktrace(tmp_path):
    fil = tmp_path/'granskning.yaml'
    fil.write_text(yaml.safe_dump(dict(paket='RP-SAKNAS', version='1.0.0', datum=str(DAG),
        granskningsdatum=str(DAG), kontrollsumma='sha256:'+'0'*64, granskare='Test',
        kompetens='Test', oberoende=True, objekt={})))
    env = {k: os.environ[k] for k in ('PATH', 'HOME', 'LANG') if k in os.environ}
    r = subprocess.run([str(Path(sys.executable).parent/'riskanalys'), 'regelbas',
        'importera-granskning', str(fil)], capture_output=True, text=True, env=env)
    assert r.returncode == 1
    assert 'Traceback' not in r.stderr
    assert 'RP-SAKNAS' in r.stderr and 'paket' in r.stderr


def test_facitrevision_upphaver_inte_paketets_juridiska_attest(regelbas_v1):
    from riskanalys.regelverk.sakkunnig import granskningsobjekt
    rb = regelbas_v1
    nytt = json.loads(json.dumps(rb.facit))
    nytt['version'] = '0.2.0'
    nytt['fall'][0]['forvantade_fynd'][0]['beskrivning'] = 'Syntetiskt reviderad facittext'
    andrad = rb.model_copy(update={'facit': nytt})
    assert andrad.paketets_innehallssumma('RP-RED-VG') == rb.paketets_innehallssumma('RP-RED-VG')
    assert not any(id.startswith('TS-') for id in granskningsobjekt(rb, 'RP-RED-VG'))


def test_facit_har_en_kanonisk_fil_och_paverkar_inte_operativ_checksumma(tmp_path):
    from riskanalys.regelverk.laddning import regelbasens_kontrollsumma
    original = STANDARD_REGELBAS/'referensdata/facit.json'
    assert original.is_symlink()
    assert original.resolve() == STANDARD_REGELBAS.parent/'docs/research/typfall/tillsyn-2026.json'
    rb = tmp_path/'rb'
    shutil.copytree(STANDARD_REGELBAS, rb)
    gammal = regelbasens_kontrollsumma(rb)
    (rb/'referensdata/facit.json').write_text('{"version":"ändrad syntetisk kopia"}')
    assert regelbasens_kontrollsumma(rb) == gammal


def test_manuell_andel_bevaras_tills_basen_uttryckligen_bekraftas(regelbas_v1):
    from tester.fixturer.m2 import PERIOD
    p = profil(regelbas_v1)
    gammal = Uppgift(varde=.2, status='bekräftad', kalla='Syntetiskt äldre kundregister',
                    datum=DAG, bekraftad_av='Syntetisk granskare', period=PERIOD)
    p = p.model_copy(update={'uppgifter': {**p.uppgifter, 'P-KUND.andel_riskbransch': gammal}})
    p = bekrafta(p, regelbas_v1, 'P-ORG.antal_anstallda', '2', 'Test', 'FfR', DAG)
    assert p.uppgifter['P-KUND.andel_riskbransch'].kalla == gammal.kalla
    assert p.uppgifter['P-KUND.andel_riskbransch'].inaktuell
    p = bekrafta(p, regelbas_v1, 'P-KUND.antal_riskbransch', '10', 'Ny syntetisk statistik',
                'FfR', DAG, period=PERIOD)
    u = p.uppgifter['P-KUND.andel_riskbransch']
    assert u.varde == .1 and u.harledd and not u.inaktuell
    assert p.ar_bekraftad('P-KUND.andel_riskbransch')


def test_inaktuell_harledd_andel_bevaras_men_stoppar_och_skickas_inte_till_ai(regelbas_v1):
    from riskanalys.dokument.underlag import _uppgift
    from riskanalys.profil.hantering import kontrollera_profil, ProfilFel
    p = profil(regelbas_v1)
    gammal = p.uppgifter['P-KUND.andel_riskbransch']
    p = p.model_copy(update={'uppgifter': {**p.uppgifter, 'P-KUND.antal_riskbransch': Uppgift()}})
    p = bekrafta(p, regelbas_v1, 'P-ORG.antal_anstallda', '2', 'Test', 'FfR', DAG)
    u = p.uppgifter['P-KUND.andel_riskbransch']
    assert u.inaktuell and u.varde == gammal.varde and u.kalla == gammal.kalla
    ai = _uppgift(regelbas_v1, p, 'P-KUND.andel_riskbransch')
    assert ai.varde == 'okänt' and not ai.bekraftad
    with pytest.raises(ProfilFel):
        kontrollera_profil(p, regelbas_v1)


def test_export_med_okant_paket_ger_atgardbart_fel(tmp_path):
    from riskanalys.regelverk.sakkunnig import exportera_sakkunnigunderlag
    from riskanalys.fel import RiskanalysFel
    with pytest.raises(RiskanalysFel, match='RP-SAKNAS'):
        exportera_sakkunnigunderlag(STANDARD_REGELBAS, 'RP-SAKNAS', DAG, tmp_path/'ut')
    assert not (tmp_path/'ut').exists()


@pytest.mark.parametrize('grupp', ['P-KUND.antal_juridisk', 'P-TJ.red01_antal_kunder'])
def test_litet_komplement_avslojas_inte_via_antal_andel_eller_intakt(regelbas_v1, grupp):
    from riskanalys.profil.omfattning import harled_andelar
    from riskanalys.dokument.underlag import _uppgift
    p = profil(regelbas_v1)
    p = p.model_copy(update={'uppgifter': {**p.uppgifter, grupp:p.uppgifter[grupp].model_copy(update={'varde':97})}})
    p = harled_andelar(p, regelbas_v1)
    idn = [grupp, next(f.id for f in regelbas_v1.falt.values() if f.antalfalt == grupp)]
    if grupp.startswith('P-TJ.'):
        idn += ['P-TJ.red01_omsattning', 'P-TJ.red01_andel_omsattning']
    for id in idn:
        u = _uppgift(regelbas_v1, p, id)
        assert u.varde == 'undertryckt (litet komplement)'
        assert u.bas is None
