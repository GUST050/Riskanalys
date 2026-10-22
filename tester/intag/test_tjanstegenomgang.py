import pytest
from riskanalys.analys.lagring import las_analys
from riskanalys.analys.provning import registersumma
from tester.intag.test_gemensam_analys_v2 import gemensam_miljo
from tester.intag.test_analys import analysmiljo
from tester.intag.test_webb import anrop


def test_gemensamma_fragor_aterkommer_inte_som_tjanstens_inmatningsfalt(gemensam_miljo):
 s,t=gemensam_miljo;p=las_analys(t.mapp);a=p.tjanster[0]
 kod,html,_=anrop(s,'analys?tjanst='+a.tjanst)
 assert kod==200 and 'Samlad tjänstegenomgång' in html and 'analysbekraftatjansteunderlag' in html
 for key in ('leverantorsmotivering','erfarenhetsprovning','sanktioner','sarbarheter','beskrivning','stallningstagande'):
  assert 'name="'+key+'"' not in html
 assert html.count('name="forfattare"')==1
 assert 'analysbeslut' not in html and las_analys(t.mapp)==p

@pytest.mark.parametrize('fel',['innehall','csrf','origin','extra','stale'])
def test_tjanstehandling_sparar_ingenting_vid_fel(gemensam_miljo,fel):
 s,t=gemensam_miljo;p=las_analys(t.mapp)
 d=dict(csrf=s.csrf,revision=registersumma(p),tjanst=p.tjanster[0].tjanst,forfattare='Syntetisk',bekrafta='ja');headers=None
 if fel=='csrf':d['csrf']='fel'
 elif fel=='origin':headers={'Origin':'https://example.invalid'}
 elif fel=='extra':d['riktning']='lagre'
 elif fel=='stale':d['revision']='sha256:'+'0'*64
 kod,html,_=anrop(s,'analysbekraftatjansteunderlag',d,headers=headers)
 assert kod in (400,403,409)
 assert las_analys(t.mapp)==p
 if fel=='innehall':assert 'gemensamma underlaget först' in html

@pytest.mark.parametrize('block,falt',[(5,'leverantorsmotivering'),(9,'erfarenhetsprovning'),(15,'sanktioner')])
def test_lokal_komplettering_fragar_inte_om_gemensamma_verksamhetssvar(gemensam_miljo,block,falt):
 s,t=gemensam_miljo;p=las_analys(t.mapp)
 kod,html,_=anrop(s,'analys?tjanst='+p.tjanster[0].tjanst+'&block='+str(block))
 assert kod==200 and 'name="'+falt+'"' not in html
 assert 'återanvänds från' in html and 'gemensamt underlag' in html


def test_cli_tjanstegenomgang_anvander_ordinarie_grind(gemensam_miljo,monkeypatch,capsys):
 from riskanalys.cli import main
 s,t=gemensam_miljo;p=las_analys(t.mapp)
 monkeypatch.setattr('riskanalys.kommandon.analys_kommando.befintlig_byramapp',lambda _:t.mapp)
 monkeypatch.setattr('riskanalys.kommandon.analys_kommando.ladda_giltig_regelbas',lambda _:t.rb)
 assert main(['analys','syntetisk','--bekrafta-tjansteunderlag',p.tjanster[0].tjanst,'--revision',registersumma(p),'--forfattare','Syntetisk CLI'])==1
 assert 'gemensamma underlaget först' in capsys.readouterr().err
 assert las_analys(t.mapp)==p
