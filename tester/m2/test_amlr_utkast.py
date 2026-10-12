from datetime import date
import shutil
import pytest
from riskanalys.fel import RiskanalysFel
from riskanalys.regelverk.amlr import ladda_amlr_utkast
from riskanalys.regelverk.laddning import STANDARD_REGELBAS,ladda_regelbas,regelbasens_kontrollsumma,regelbasfiler
from riskanalys.regelverk.urval import valj

@pytest.mark.parametrize('d',[date(2027,7,9),date(2027,7,10),date(2029,7,10)])
def test_utkast_ar_aldrig_operativt(regelbas_v1,d):
 with pytest.raises(RiskanalysFel):valj(regelbas_v1,'RP-AMLR-UTKAST',d,'Västra Götaland')

def test_full_kravkarta_och_checksummaisolering(tmp_path):
 u=ladda_amlr_utkast(STANDARD_REGELBAS/'utkast/amlr')
 assert {a.id for a in u.artiklar}=={f'Artikel {i}' for i in range(1,91)}|{f'Bilaga {n}' for n in ('I','II','III','IV','V','VI')}
 assert u.status=='utkast' and u.tillampas_fran==date(2027,7,10)
 r=tmp_path/'rb';shutil.copytree(STANDARD_REGELBAS,r)
 summa=regelbasens_kontrollsumma(r);(r/'utkast/amlr/README.md').write_text('ändrat utkast')
 (r/'utkast/amlr/extra.yaml').write_text('x: y')
 assert regelbasens_kontrollsumma(r)==summa
 assert not any('utkast' in p.relative_to(r).parts for p in regelbasfiler(r))

@pytest.mark.parametrize('fel',['saknat_manifest','andrad_fil'])
def test_utkastets_eget_manifest_skyddar_alla_filer(tmp_path,fel):
 r=tmp_path/'amlr';shutil.copytree(STANDARD_REGELBAS/'utkast/amlr',r)
 if fel=='saknat_manifest':
  (r/'manifest.json').unlink(missing_ok=True)
 else:
  (r/'README.md').write_text('förändrat underlag')
 with pytest.raises(RiskanalysFel,match='manifest|Manifest'):
  ladda_amlr_utkast(r)
