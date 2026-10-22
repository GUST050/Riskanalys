import pytest
from riskanalys.analys import modeller as m
from riskanalys.analys.gemensam import effektiv_tjanst,postsumma
from riskanalys.fel import RiskanalysFel
from tester.enhet.test_gemensam_analys_v2 import paket

def start():
 p=paket()
 return p.model_copy(update={'tjanster':tuple(t.model_copy(update={'sarbarhetstillampningar':tuple(x.model_copy(update={'bekraftad':False}) for x in t.sarbarhetstillampningar)}) for t in p.tjanster)})

def test_ett_svar_anvands_i_fyra_tjanster_utan_lokala_kopior():
 from riskanalys.analys.engangssvar import bygg_gemensam_bekraftelse,visade_celler
 p=start();ids=tuple(t.tjanst for t in p.tjanster);q=bygg_gemensam_bekraftelse(p,ids,visade_celler(p,ids),'Syntetisk')
 assert len(ids)==4 and len(q.gemensamma_sarbarhetsprovningar)==1
 assert all(t.sarbarhetstillampningar[0].bekraftad for t in q.tjanster)
 for t,a in zip(p.tjanster,q.tjanster,strict=True):
  assert t.sarbarhetsprovningar==a.sarbarhetsprovningar
  assert any('Gemensam unik kundanalys' in x.motivering for x in effektiv_tjanst(q,a.tjanst).sarbarhetsprovningar)
 assert q.model_dump_json().count('Gemensam unik kundanalys')==1 and not q.beslut

@pytest.mark.parametrize('stallning',['beror_inte','otillrackligt','galler_annorlunda'])
def test_samlad_handling_bevarar_avvikelse_och_otillrackligt(stallning):
 from riskanalys.analys.engangssvar import bygg_gemensam_bekraftelse,visade_celler
 p=start();a=p.tjanster[0];app=a.sarbarhetstillampningar[0].model_copy(update={'stallningstagande':stallning})
 p=p.model_copy(update={'tjanster':(a.model_copy(update={'sarbarhetstillampningar':(app,)}),*p.tjanster[1:])});ids=tuple(t.tjanst for t in p.tjanster)
 celler=visade_celler(p,ids);assert len(celler)==3
 q=bygg_gemensam_bekraftelse(p,ids,celler,'Syntetisk');assert q.tjanster[0].sarbarhetstillampningar==(app,)
 assert all(t.sarbarhetstillampningar[0].bekraftad for t in q.tjanster[1:])

@pytest.mark.parametrize('fel',['borttagen','extra','dubblett','gammal_summa','okand_tjanst'])
def test_exakt_visad_cellmangd_kravs(fel):
 from riskanalys.analys.engangssvar import bygg_gemensam_bekraftelse,visade_celler
 p=start();ids=tuple(t.tjanst for t in p.tjanster);c=visade_celler(p,ids)
 if fel=='borttagen':c=c[:-1]
 elif fel=='extra':c=(*c,c[0].model_copy(update={'post':'finns-inte'}))
 elif fel=='dubblett':c=(*c,c[0])
 elif fel=='gammal_summa':c=(c[0].model_copy(update={'postsumma':'sha256:'+'a'*64}),*c[1:])
 else:ids=(*ids,'FINNS-INTE')
 fore=p.model_dump_json()
 with pytest.raises(RiskanalysFel):bygg_gemensam_bekraftelse(p,ids,c,'Syntetisk')
 assert p.model_dump_json()==fore

def test_antagande_forblir_antagande():
 from riskanalys.analys.engangssvar import bygg_gemensam_bekraftelse,visade_celler
 p=start();p=p.model_copy(update={'gemensamma_sarbarhetsprovningar':(p.gemensamma_sarbarhetsprovningar[0].model_copy(update={'status':'antagande'}),)})
 ids=tuple(t.tjanst for t in p.tjanster);q=bygg_gemensam_bekraftelse(p,ids,visade_celler(p,ids),'Syntetisk')
 assert q.gemensamma_sarbarhetsprovningar[0].status=='antagande'
 assert any(x.relevans=='okant' for x in effektiv_tjanst(q,ids[0]).sarbarhetsprovningar)

def test_schemat_och_falt_ar_strikta():
 from riskanalys.analys.engangssvar import GemensamCell,bygg_gemensam_bekraftelse
 from pydantic import ValidationError
 with pytest.raises(ValidationError):GemensamCell(tjanst='T',slag='sarbarhet',post='x',postsumma='s',riktning='lagre')
 with pytest.raises(RiskanalysFel):bygg_gemensam_bekraftelse(m.Analyspaket(bindning=start().bindning),('T',),(),'Syntetisk')


def test_verksamhet_och_ny_tjanst_far_standardtillampning_utan_nya_svar():
 from riskanalys.analys.engangssvar import bygg_gemensam_bekraftelse,visade_celler
 p=start();g=m.GemensamVerksamhetspost(id='erfarenhet',slag='erfarenhet',text='En gemensam erfarenhetskälla',status='bekraftad')
 a=m.Tjansteanalys(tjanst='syntetisk-ny')
 p=p.model_copy(update={'gemensamma_verksamhetsposter':(g,),'tjanster':(*p.tjanster,a)})
 ids=tuple(t.tjanst for t in p.tjanster);q=bygg_gemensam_bekraftelse(p,ids,visade_celler(p,ids),'Syntetisk')
 assert len(q.gemensamma_verksamhetsposter)==1 and not q.beslut
 assert all(t.verksamhetstillampningar[0].bekraftad for t in q.tjanster)
 assert q.tjanster[-1].sarbarhetstillampningar[0].bekraftad
 assert q.tjanster[-1].sarbarhetsprovningar==()


def test_operationen_provar_aktuellt_utbud_och_cas(tmp_path,regelbas_v1,monkeypatch):
 from types import SimpleNamespace
 from tester.enhet.test_gemensamma_operationer import Minne
 from riskanalys.analys.engangssvar import visade_celler
 from riskanalys.analys.provning import registersumma
 at=Minne(start(),regelbas_v1,tmp_path);ids=tuple(a.tjanst for a in at.p.tjanster)
 b=SimpleNamespace(tjanster=tuple(SimpleNamespace(tjanst=id,erbjuds=i!=0) for i,id in enumerate(ids)))
 monkeypatch.setattr('riskanalys.analys.gemensamma_operationer.las_bedomning',lambda _:b)
 fore=at.p;rev=registersumma(fore)
 with pytest.raises(RiskanalysFel,match='erbjudna'):at.bekrafta_byraunderlag(ids,visade_celler(fore,ids),rev,'Syntetisk')
 assert at.p==fore
 b.tjanster=tuple(SimpleNamespace(tjanst=id,erbjuds=True) for id in ids)
 at.bekrafta_byraunderlag(ids,visade_celler(fore,ids),rev,'Syntetisk')
 assert all(t.sarbarhetstillampningar[0].bekraftad for t in at.p.tjanster)
 q=at.p
 with pytest.raises(RiskanalysFel):at.bekrafta_byraunderlag(ids,visade_celler(q,ids),rev,'Syntetisk')
 assert at.p==q

@pytest.mark.parametrize('fel',['extra','cellfalt','stor','saknas'])
def test_cli_underlagsfil_ar_strikt_och_begransad(tmp_path,fel):
 import json
 from pydantic import ValidationError
 from riskanalys.kommandon.gemensam_analys import helhet
 from riskanalys.analys.engangssvar import visade_celler
 p=start();ids=tuple(a.tjanst for a in p.tjanster)
 raw={'tjanster':ids,'celler':[x.model_dump() for x in visade_celler(p,ids)]}
 if fel=='extra':raw['godkand']=True
 elif fel=='cellfalt':raw['celler'][0]['riktning']='lagre'
 fil=tmp_path/'prov.json'
 if fel!='saknas':fil.write_text(json.dumps(raw) if fel!='stor' else ' '*65537)
 with pytest.raises((RiskanalysFel,ValidationError)):helhet(fil)
