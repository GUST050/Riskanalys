"""Facit granskas separat utan att ändra en regelpaketsattest."""
from datetime import date
import json
import shutil
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from riskanalys.fel import RiskanalysFel
from riskanalys.regelverk.laddning import STANDARD_REGELBAS, ladda_regelbas
from riskanalys.regelverk.sakkunnig import exportera_sakkunnigunderlag

DAG = date(2026,10,10)


def granskat(rb, ut):
    exportera_sakkunnigunderlag(rb, 'RP-RED-VG', DAG, ut)
    p = ut/'facitgranskningsmall.yaml'
    d = yaml.safe_load(p.read_text())
    d.update(granskare='Syntetisk facitgranskare', kompetens='Syntetisk tillsynskompetens', oberoende=True)
    for obj in d['objekt'].values():
        obj.update(beslut='verifierad', kommentar='Syntetiskt prov')
    p.write_text(yaml.safe_dump(d,allow_unicode=True))
    return p


def test_export_och_import_binder_exakt_22_facitobjekt(tmp_path):
    from riskanalys.regelverk.facit import las_facitgranskning, tillampa_facitgranskning
    rot=tmp_path/'rb';shutil.copytree(STANDARD_REGELBAS,rot)
    fil=granskat(rot,tmp_path/'ut')
    rb=ladda_regelbas(rot);summa=rb.paketets_innehallssumma('RP-RED-VG')
    beslut=las_facitgranskning(fil,rb.facit)
    assert len(beslut.objekt)==22
    tillampa_facitgranskning(rot,beslut)
    sparat=las_facitgranskning(rot/'facitgranskning.yaml',ladda_regelbas(rot).facit)
    assert sparat==beslut
    assert not (rot/'granskning.yaml').exists()
    assert ladda_regelbas(rot).paketets_innehallssumma('RP-RED-VG')==summa
    nytt=json.loads(json.dumps(rb.facit));nytt['version']='0.2.0'
    with pytest.raises(RiskanalysFel,match='facit|Facit'):
        las_facitgranskning(fil,nytt)


@pytest.mark.parametrize('fel',['oberoende','saknad','kommentar'])
def test_ofullstandigt_facitbeslut_avvisas(tmp_path,regelbas_v1,fel):
    from riskanalys.regelverk.facit import las_facitgranskning
    fil=granskat(STANDARD_REGELBAS,tmp_path/'ut');d=yaml.safe_load(fil.read_text())
    if fel=='oberoende':d['oberoende']=False
    elif fel=='saknad':d['objekt'].pop(next(iter(d['objekt'])))
    else:next(iter(d['objekt'].values()))['kommentar']=' '
    fil.write_text(yaml.safe_dump(d,allow_unicode=True))
    with pytest.raises(RiskanalysFel):las_facitgranskning(fil,regelbas_v1.facit)


def test_facitimport_via_cli_frigor_inget_regelpaket(tmp_path):
    rot = tmp_path/'rb'
    shutil.copytree(STANDARD_REGELBAS, rot)
    fil = granskat(rot, tmp_path/'ut')
    env = {k: os.environ[k] for k in ('PATH', 'HOME', 'LANG') if k in os.environ}
    r = subprocess.run([str(Path(sys.executable).parent/'riskanalys'), 'regelbas',
                        'importera-facitgranskning', str(fil), '--regelbas', str(rot)],
                       capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    assert (rot/'facitgranskning.yaml').is_file()
    assert not (rot/'granskning.yaml').exists()
    assert all(p.granskning.status == 'ej_granskad' for p in ladda_regelbas(rot).regelpaket.values())


def test_facitrevision_lamnar_importerade_juridiska_attester_giltiga(tmp_path):
    from riskanalys.regelverk.sakkunnig import las_granskningsfil, tillampa_granskning
    rot = tmp_path/'rb'
    shutil.copytree(STANDARD_REGELBAS, rot)
    exportera_sakkunnigunderlag(rot, 'RP-RED-VG', DAG, tmp_path/'ut')
    fil = tmp_path/'ut/granskningsmall.yaml'
    d = yaml.safe_load(fil.read_text())
    d.update(granskare='Syntetisk granskare', kompetens='Syntetisk testkompetens', oberoende=True)
    for obj in d['objekt'].values():
        obj.update(beslut='verifierad', kommentar='Syntetiskt prov')
    fil.write_text(yaml.safe_dump(d, allow_unicode=True))
    rb = ladda_regelbas(rot)
    tillampa_granskning(rot, las_granskningsfil(fil, rb, 'RP-RED-VG'))
    summa = ladda_regelbas(rot).kontrollsumma
    facitfil = rot/'referensdata/facit.json'
    facit = json.loads(facitfil.read_text())
    facit['version'] = '0.2.0'
    facitfil.write_text(json.dumps(facit))
    rb = ladda_regelbas(rot)
    assert rb.kontrollsumma == summa
    assert rb.regelpaket['RP-RED-VG'].granskning.galler(rb.paketets_innehallssumma('RP-RED-VG'))
