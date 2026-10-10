from datetime import datetime,timezone
import json
import pytest
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.manifest import skriv_manifest,las_manifest,programproveniens
from riskanalys.lagring.korningar import ny_korningsmapp,senaste_korning
from riskanalys.lagring.yamlfil import las_yaml
from riskanalys.regelverk.villkor import tolka_villkor,Faltdef


def test_utc_sortering_vid_hostens_tidsomstallning(tmp_path):
 r=tmp_path/'x';r.mkdir()
 for namn,t in [('20261025T025900','2026-10-25T00:59:00Z'),('20261025T020100','2026-10-25T01:01:00Z')]:
  m=r/namn;m.mkdir();skriv_manifest(m,{})
  p=m/'manifest.json';d=json.loads(p.read_text());d['skapad']=t;p.write_text(json.dumps(d))
 assert senaste_korning(tmp_path,'x','x').name=='20261025T020100'
 assert ny_korningsmapp(tmp_path,'x').name.endswith('Z')

def test_manifest_saknat_faller_inte_tillbaka(tmp_path):
 r=tmp_path/'x';r.mkdir();m=r/'old';m.mkdir();skriv_manifest(m,{})
 (r/'new').mkdir()
 with pytest.raises(RiskanalysFel,match='Återställ'):senaste_korning(tmp_path,'x','x')


def test_proveniens_utan_git_och_gammalt_manifest(tmp_path):
 (tmp_path/'src').mkdir();(tmp_path/'src/code.py').write_text('x = 1')
 a=programproveniens(tmp_path);assert a.commit is None and a.arbetskopia=='okand'
 (tmp_path/'src/code.py').write_text('x = 2');assert programproveniens(tmp_path).innehallssumma!=a.innehallssumma
 m=tmp_path/'run';m.mkdir();skriv_manifest(m,{})
 p=m/'manifest.json';d=json.loads(p.read_text());d.pop('programproveniens');p.write_text(json.dumps(d))
 assert las_manifest(m).programproveniens.arbetskopia=='okand'

@pytest.mark.parametrize('data',[b'\xff',b'x: ['])
def test_olastbar_yaml_ar_atgardbart_fel(tmp_path,data):
 p=tmp_path/'skadad.yaml';p.write_bytes(data)
 with pytest.raises(RiskanalysFel,match='skadad.yaml'):las_yaml(p)

@pytest.mark.parametrize('falt,op',[([], '=='),('x',[]),(2,'=='),('x',{})])
def test_icke_text_villkor_fangade(falt,op):
 with pytest.raises(RiskanalysFel):tolka_villkor({'falt':falt,'op':op,'varde':True},{'x':Faltdef('x','bool')})
