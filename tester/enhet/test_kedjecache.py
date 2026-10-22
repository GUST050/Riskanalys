from datetime import date
from pathlib import Path
import pytest
import yaml
from riskanalys.analys.modeller import Analyspaket,Analysbindning
from riskanalys.analys import lagring as l
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.kontrollsumma import for_bytes
from tester.fixturer.analys_hela_kedjan import BundenKedja,SyntetisktFall


def liten_bas(rot,markor='ett'):
    byra=rot/'byra';(byra/'analys/belagg').mkdir(parents=True)
    (byra/'analys/belagg/rutin.txt').write_bytes(markor.encode())
    a=Analyspaket(bindning=Analysbindning(byra='test',profilrevision='p',bedomningsmanifest='b',utkastmanifest='u',regelbas=markor,kallunderlag='k',historik='',bedomningsdatum=date(2026,10,15),modell='m'))
    (byra/'analys/analys.yaml').write_text(yaml.safe_dump(a.model_dump(mode='json')))
    for namn in ('bedomningar/b','utkast/u','granskning/g'):(byra/namn).mkdir(parents=True)
    rb=rot/'regelbas';rb.mkdir();(rb/'version.yaml').write_text(markor)
    return BundenKedja(SyntetisktFall(None,None,None,a,byra),byra/'bedomningar/b',byra/'utkast/u',byra/'granskning/g',rb)


def test_mutation_i_klon_andrar_inte_bas_eller_nasta_klon(tmp_path):
    from tester.fixturer.kedjecache import klona_kedja
    bas=liten_bas(tmp_path/'bas');ett=klona_kedja(bas,tmp_path/'ett')
    (ett.fall.byramapp/'analys/belagg/rutin.txt').write_bytes(b'andrat')
    (ett.regelrot/'version.yaml').write_text('andrat')
    tva=klona_kedja(bas,tmp_path/'tva')
    assert (bas.fall.byramapp/'analys/belagg/rutin.txt').read_bytes()==b'ett'
    assert (tva.fall.byramapp/'analys/belagg/rutin.txt').read_bytes()==b'ett'
    assert (tva.regelrot/'version.yaml').read_text()=='ett'


def test_klon_laser_endast_sina_egna_privata_belagg(tmp_path):
    from tester.fixturer.kedjecache import klona_kedja
    bas=liten_bas(tmp_path/'bas');k=klona_kedja(bas,tmp_path/'ny')
    (bas.fall.byramapp/'analys/belagg/rutin.txt').write_bytes(b'andrat original')
    assert l.las_belaggsfil(k.fall.byramapp,'rutin.txt',for_bytes(b'ett'))==b'ett'
    (bas.fall.byramapp/'analys/belagg/utanforkopia.txt').symlink_to(tmp_path/'annan')
    with pytest.raises(ValueError,match='symlänk'):klona_kedja(bas,tmp_path/'avvisad')


def test_korrupt_kopia_far_inte_atervanda_aldre_godkannande(tmp_path):
    from tester.fixturer.kedjecache import klona_kedja
    bas=liten_bas(tmp_path/'bas');k=klona_kedja(bas,tmp_path/'ny')
    (k.fall.byramapp/'analys/analys.yaml').write_text('inte: [giltig yaml')
    with pytest.raises(RiskanalysFel):l.las_analys(k.fall.byramapp)
    assert l.las_analys(bas.fall.byramapp)==bas.fall.analys


def test_baser_med_olika_schema_eller_regelbas_delar_inte_lage(tmp_path):
    from tester.fixturer.kedjecache import klona_kedja
    a=liten_bas(tmp_path/'a','a');b=liten_bas(tmp_path/'b','b')
    x=klona_kedja(a,tmp_path/'x');y=klona_kedja(b,tmp_path/'y')
    assert l.las_analys(x.fall.byramapp).bindning.regelbas=='a'
    assert l.las_analys(y.fall.byramapp).bindning.regelbas=='b'
