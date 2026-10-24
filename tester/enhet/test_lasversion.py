"""Läsversionens kopior binds byte för byte till det fullständiga paketet."""
import json
from pathlib import Path
import pytest
from riskanalys.lagring.manifest import skriv_manifest,verifiera_manifest


def underlag(tmp_path):
    full=tmp_path/'full';full.mkdir()
    for name in ('sakkunniggranskning.md','objektgenomgang.md','granskningsmall.yaml',
                 'metod/sammanstallning.md','metod/beslut-och-beroenden.json','metod/fore-efter.json',
                 *(f'referensrapporter/{c}/{d}.pdf' for c in ('fyra_tjanster','med_betalningsmandat')
                   for d in ('allman-riskbedomning-UTKAST','analysbilaga-UTKAST','underlagsbilaga-UTKAST'))):
        p=full/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(('Syntetisk fil '+name).encode())
    (full/'stor-teknisk-fil.bin').write_bytes(b'x'*10000)
    skriv_manifest(full,{'typ':'sakkunnigunderlag','regelpaket':'RP-RED-VG'})
    return full


def test_lasversion_har_exakt_samma_gemensamma_filer(tmp_path):
    from riskanalys.regelverk.lasversion import skapa_lasversion
    full=underlag(tmp_path);ut=skapa_lasversion(full,tmp_path/'las')
    data=json.loads((ut/'lasversion.json').read_text())
    assert len(data['gemensamma'])==12
    for name,summa in data['gemensamma'].items():
        assert (ut/name).read_bytes()==(full/name).read_bytes()
    assert not (ut/'stor-teknisk-fil.bin').exists()
    assert data['storlek_byte']<sum(p.stat().st_size for p in full.rglob('*') if p.is_file())
    assert not verifiera_manifest(ut)
    assert 'tekniska grunden' in (ut/'LAS-MIG.md').read_text()


@pytest.mark.parametrize('fel',['andrad','saknad','befintlig'])
def test_lasversion_stoppar_andrat_eller_ofullstandigt_fullpaket(tmp_path,fel):
    from riskanalys.regelverk.lasversion import skapa_lasversion
    from riskanalys.fel import RiskanalysFel
    full=underlag(tmp_path);ut=tmp_path/'las'
    if fel=='andrad':(full/'objektgenomgang.md').write_text('ändrat')
    elif fel=='saknad':
        (full/'granskningsmall.yaml').unlink();skriv_manifest(full,{'typ':'sakkunnigunderlag'})
    else:ut.mkdir()
    with pytest.raises(RiskanalysFel):skapa_lasversion(full,ut)
    if fel!='befintlig':assert not ut.exists()
