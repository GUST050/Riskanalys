"""Verklig schema-2-start; frysta rapportfall hålls åtskilda från komplett attestprov."""
import json
import pytest
from riskanalys.analys.gemensam import effektiv_tjanst
from tester.fixturer.rapportlasprov import bygg_rapportlasprov


@pytest.fixture(scope='module',params=('fyra_tjanster','med_betalningsmandat'))
def direkt(request,regelbas_v1,tmp_path_factory):
 from tester.fixturer.gemensam_analys import bygg_direkt_gemensamt_fall
 rot=tmp_path_factory.mktemp('direkt-'+request.param)
 # Förbjud konvertering av ett ifyllt schema-1-paket, även via förifyllnadsfunktionen.
 from unittest.mock import patch
 from riskanalys.analys.gemensam import forifyll_gemensamt
 def bara_utkast(rb,p):
  assert not any(t.forfattare for t in p.tjanster)
  return forifyll_gemensamt(rb,p)
 with patch('riskanalys.analys.overforing.foresla_overforing',side_effect=AssertionError('Överföring i direkt2')),patch('riskanalys.analys.gemensam.forifyll_gemensamt',side_effect=bara_utkast):
  f=bygg_direkt_gemensamt_fall(regelbas_v1,rot,request.param)
 fore=bygg_rapportlasprov(regelbas_v1,rot/'jamforelse',request.param)
 return f,fore,json.loads((rot/'engangssvar-handlingar.json').read_text())


def test_direktlage_bevarar_semantiska_svar_motor_och_underlag(direkt):
 from riskanalys.dokument.radata_v8 import fria_analysfalt
 from tester.enhet.test_arb_v8 import skriv
 from docs.research.verktyg.matkontrakt import frysta_skrivsvar
 from types import SimpleNamespace
 f,fore,logg=direkt
 assert f.profil.model_dump(mode='json')==fore.profil.model_dump(mode='json')
 assert f.bedomning==fore.bedomning
 assert f.paket.belagg==fore.analys.belagg
 gamla={x.text for x in fria_analysfalt(fore.analys) if x.sokvag.rsplit('/',1)[-1] not in ('forfattare',)}
 nya={x.text for x in fria_analysfalt(f.paket)}
 saknas=sorted(t for t in gamla if not any(t in n for n in nya))
 assert not saknas,saknas
 assert frysta_skrivsvar(skriv(fore))==frysta_skrivsvar(skriv(SimpleNamespace(regelbas=f.rb,profil=f.profil,bedomning=f.bedomning)))
 assert all(not a.sarbarhetsprovningar or all(x.omrade=='tjanst' for x in a.sarbarhetsprovningar) for a in f.paket.tjanster)
 for a in f.paket.tjanster:
  assert not a.leverantorsmotivering and not a.erfarenhetsprovning and not a.sanktioner
  assert effektiv_tjanst(f.paket,a.tjanst).erfarenhetsprovning
 assert logg['gemensamma_svar']==7 and logg['lokala_gemensamma_kopior']==0
 assert logg['tackningsprovningar_kravda']==logg['tackningsprovningar_utforda']==0
 assert logg['handlingar'].count('gemensam_bekraftelse')==1
 assert logg['handlingar'].count('tjanstegenomgang')+logg['handlingar'].count('tjanstegenomgang_nekad')==4
 assert logg['hinder']  # Rapportläsprovens avsiktliga luckor får inte döljas.


def test_direktrapport_och_bilaga_bevarar_svar_och_attribution(direkt):
 from riskanalys.dokument.arb_v8 import bygg_arb_v8
 from riskanalys.drift.historik import Historik
 from riskanalys.dokument.radata_v8 import fria_analysfalt,textplaceringar
 from tester.enhet.test_arb_v8 import skriv
 from types import SimpleNamespace
 f,_,_=direkt;svar=skriv(SimpleNamespace(regelbas=f.rb,profil=f.profil,bedomning=f.bedomning))
 d=bygg_arb_v8(f.rb,f.profil,f.bedomning,svar,Historik(),analys=f.paket)
 b1='\n'.join(t for _,t in textplaceringar(d.avsnitt_med_id()['D-ARB.B1']))
 assert all(x.text in b1 for x in fria_analysfalt(f.paket))
 assert all(g.forfattare in b1 for g in (*f.paket.gemensamma_sarbarhetsprovningar,*f.paket.gemensamma_verksamhetsposter))
 assert all(a.forfattare in b1 for a in f.paket.tjanster)
 assert not f.paket.beslut


def test_d9_villkor_skrivs_inte_om_for_varje_hot_och_tjanst(direkt):
 from riskanalys.dokument.gemensam_provning_v8 import tjanstens_tillampningsstycken,d9_upplysningar
 from riskanalys.analys.riktning import harled_riktningar
 f,_,_=direkt;gem='\n'.join(s.text for s in d9_upplysningar(f.rb,f.profil,f.paket,f.bedomning))
 assert 'Villkor:' in gem
 for t in f.bedomning.tjanster:
  if not t.erbjuds:continue
  lokalt='\n'.join(s.text for s in tjanstens_tillampningsstycken(f.rb,f.profil,f.paket,t))
  assert 'Villkor:' not in lokalt and 'D9 C' in lokalt
  for r in harled_riktningar(f.rb,f.profil,f.paket,t):
   if r.riktning not in ('under_troskel','villkor_ej_uppfyllt'):continue
   assert r.sarbarhet in lokalt and r.sarbarhet in gem
   assert t.tjanst+'/'+r.hot+'/'+r.dimension in gem
   assert all(falt in gem for falt in r.profilfalt)


def test_native_tjanstevyn_visar_gemensamt_arv_period_och_identifierbar_faktor(direkt):
 from riskanalys.intag.engangsvy import genomgang
 from riskanalys.analys.riktning import harled_riktningar
 f,_,_=direkt;a=f.paket.tjanster[0]
 html=genomgang(f.rb,f.profil,f.bedomning,f.paket,a.tjanst,'/syntetisk/','csrf','revision')
 assert 'datetime.date(' not in html
 assert 'Gemensamma sårbarheter återanvänds' in html
 t=next(t for t in f.bedomning.tjanster if t.tjanst==a.tjanst)
 assert all(r.sarbarhet in html for r in harled_riktningar(f.rb,f.profil,f.paket,t) if r.sarbarhet)


def test_d9_sammanfattas_en_gang_per_tjanst_med_samtliga_spar(direkt):
 from riskanalys.dokument.gemensam_provning_v8 import tjanstens_tillampningsstycken
 from riskanalys.analys.riktning import harled_riktningar
 f,_,_=direkt
 for t in f.bedomning.tjanster:
  if not t.erbjuds:continue
  d9=[x for x in tjanstens_tillampningsstycken(f.rb,f.profil,f.paket,t) if 'D9 C' in x.text]
  assert len(d9)==1
  assert '22 gemensamma faktorer' in d9[0].text and 'B1' in d9[0].text
  assert len(d9[0].text.split())<100
  for r in harled_riktningar(f.rb,f.profil,f.paket,t):
   if r.riktning not in ('under_troskel','villkor_ej_uppfyllt'):continue
   assert r.sarbarhet in d9[0].text and r.sarbarhet in d9[0].referenser
   assert 'ANALYS:gemensam_sarbarhet:'+r.post in d9[0].referenser
   assert all(x in d9[0].referenser for x in (*r.profilfalt,*r.regelspar))
