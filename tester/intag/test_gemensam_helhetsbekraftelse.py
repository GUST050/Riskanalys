import json
import pytest
from riskanalys.analys.lagring import las_analys
from riskanalys.analys.provning import registersumma
from riskanalys.analys.tjanst import Analystjanst
from tester.intag.test_gemensam_analys_v2 import gemensam_miljo
from tester.intag.test_analys import analysmiljo
from tester.intag.test_webb import anrop


def data(s,p):
 from riskanalys.analys.engangssvar import visade_celler
 ids=tuple(a.tjanst for a in p.tjanster)
 return dict(csrf=s.csrf,revision=registersumma(p),forfattare='Syntetisk',bekrafta='ja',
             tjanster=','.join(ids),celler=json.dumps([c.model_dump() for c in visade_celler(p,ids)]))

def test_en_handling_bekraftar_alla_tjanster_utan_nya_svar_eller_ai(gemensam_miljo):
 s,t=gemensam_miljo;p=las_analys(t.mapp);n=len(s.leverantor.delanrop)
 kod,html,_=anrop(s,'analys?byraanalys=ja')
 assert kod==200 and 'analysbekraftabyraunderlag' in html
 assert 'Bekräfta gemensamt underlag för valda tjänster' in html
 d=data(s,p);assert anrop(s,'analysbekraftabyraunderlag',d)[0]==200
 q=las_analys(t.mapp)
 assert all(x.bekraftad for a in q.tjanster for x in (*a.sarbarhetstillampningar,*a.verksamhetstillampningar))
 assert q.gemensamma_sarbarhetsprovningar==p.gemensamma_sarbarhetsprovningar
 assert not q.beslut and len(s.leverantor.delanrop)==n
 assert anrop(s,'analysbekraftabyraunderlag',d)[0]==409 and las_analys(t.mapp)==q

@pytest.mark.parametrize('fel',['saknad','dubblett','extra_falt','gammal_summa','okand','csrf','origin','ej_bekraftat'])
def test_hela_bekraftelsen_avvisas_utan_delvis_sparning(gemensam_miljo,fel):
 s,t=gemensam_miljo;p=las_analys(t.mapp);d=data(s,p);headers=None
 c=json.loads(d['celler'])
 if fel=='saknad':d['celler']=json.dumps(c[:-1])
 elif fel=='dubblett':d['celler']=json.dumps([*c,c[0]])
 elif fel=='extra_falt':d['riktning']='lagre'
 elif fel=='gammal_summa':c[0]['postsumma']='sha256:'+'0'*64;d['celler']=json.dumps(c)
 elif fel=='okand':d['tjanster']+=',FINNS-INTE'
 elif fel=='csrf':d['csrf']='fel'
 elif fel=='origin':headers={'Origin':'https://example.invalid'}
 else:d['bekrafta']='nej'
 assert anrop(s,'analysbekraftabyraunderlag',d,headers=headers)[0] in (400,403,409)
 assert las_analys(t.mapp)==p


def test_svarimport_kan_inte_skapa_helhetsbekraftelse(gemensam_miljo,tmp_path):
 import yaml
 from riskanalys.analys.tjanst import Analystjanst
 s,t=gemensam_miljo;p=las_analys(t.mapp)
 assert anrop(s,'analysbekraftabyraunderlag',data(s,p))[0]==200
 p=las_analys(t.mapp);fil=tmp_path/'syntetisk-import.yaml'
 fil.write_text(yaml.safe_dump(p.model_dump(mode='json')))
 Analystjanst(t.mapp,t.rb).importera_svar(fil,'Syntetisk import',registersumma(p))
 q=las_analys(t.mapp)
 assert all(not x.bekraftad for a in q.tjanster for x in (*a.sarbarhetstillampningar,*a.verksamhetstillampningar))
 assert not q.beslut


def test_cli_helhet_anvander_samma_atomiska_operation(gemensam_miljo,tmp_path,monkeypatch,capsys):
 from riskanalys.cli import main
 s,t=gemensam_miljo;p=las_analys(t.mapp);d=data(s,p);fil=tmp_path/'val.json'
 fil.write_text(json.dumps({'tjanster':d['tjanster'].split(','),'celler':json.loads(d['celler'])}))
 monkeypatch.setattr('riskanalys.kommandon.analys_kommando.befintlig_byramapp',lambda _:t.mapp)
 monkeypatch.setattr('riskanalys.kommandon.analys_kommando.ladda_giltig_regelbas',lambda _:t.rb)
 assert main(['analys','syntetisk','--bekrafta-byraunderlag',str(fil),'--revision',registersumma(p),'--forfattare','Syntetisk CLI'])==0
 assert 'registersumma' in capsys.readouterr().out
 q=las_analys(t.mapp)
 assert all(x.bekraftad for a in q.tjanster for x in a.sarbarhetstillampningar) and not q.beslut
