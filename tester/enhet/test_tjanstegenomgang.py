from dataclasses import replace
import pytest
from riskanalys.analys import modeller as m
from riskanalys.analys.provning import analysbrister,blocksumma
from riskanalys.fel import RiskanalysFel

@pytest.fixture(scope='module')
def grund(regelbas_v1,tmp_path_factory):
 from tester.fixturer.analys_hela_kedjan import skapa_fall,_positiv_bankavstamning,syntetisk_expertkopia
 from tester.fixturer.fylld_gemensam import ifylld_analys
 rot=tmp_path_factory.mktemp('engangsprov');_,rb=syntetisk_expertkopia(rot/'expert')
 f=skapa_fall(rb,rot/'fall')
 p=ifylld_analys(rb,f.profil,f.bedomning,_positiv_bankavstamning(rb,f.analys))
 return f,p

def globalt(p):
 from riskanalys.analys.engangssvar import bygg_gemensam_bekraftelse,visade_celler
 ids=tuple(a.tjanst for a in p.tjanster)
 return bygg_gemensam_bekraftelse(p,ids,visade_celler(p,ids),'Syntetisk')

def bekrafta(f,p,tid=None):
 from riskanalys.analys.engangssvar import bygg_tjanstbekraftelse
 return bygg_tjanstbekraftelse(f.regelbas,f.profil,f.bedomning,p,tid or p.tjanster[0].tjanst,'Syntetisk')

def test_en_global_och_fyra_tjanstehandlingar_utan_scenarioklick(grund):
 f,p=grund;p=globalt(p);motor=f.bedomning.model_dump_json()
 for a in p.tjanster:p=bekrafta(f,p,a.tjanst)
 assert not analysbrister(f.regelbas,f.profil,f.bedomning,p)
 assert all(b.bekraftad_summa==blocksumma(p,a.tjanst,b.nummer) for a in p.tjanster for b in a.block)
 assert all(k.bekraftad for a in p.tjanster for k in a.scenariokopplingar)
 assert not p.beslut and motor==f.bedomning.model_dump_json()

@pytest.mark.parametrize('fel',['lokalt','aktivering','relevans','hot','belagg','kontroll','tf','globalt'])
def test_ordinarie_innehallsgrind_kan_inte_kringgas(grund,fel):
 f,p=grund;p=globalt(p);a=p.tjanster[0]
 if fel=='lokalt':a=a.model_copy(update={'pt_motivering':''})
 elif fel=='aktivering':a=a.model_copy(update={'block':tuple(b.model_copy(update={'aktivering':'okand'}) if b.nummer==1 else b for b in a.block)})
 elif fel=='relevans':
  s=p.gemensamma_scenarier[0];p=p.model_copy(update={'gemensamma_scenarier':(s.model_copy(update={'relevans':'okant'}),*p.gemensamma_scenarier[1:])})
 elif fel=='hot':a=a.model_copy(update={'scenarier':(m.Scenarioanalys(id='fel',hot=('finns-inte',),relevans='relevant'),)})
 elif fel=='belagg':p=p.model_copy(update={'belagg':()})
 elif fel=='kontroll':a=a.model_copy(update={'kontroller':()})
 elif fel=='tf':a=a.model_copy(update={'tf_motivering':''})
 else:
  # Inget tjänsteprefix: måste ändå stoppa genomgången av en annan tjänst.
  g=p.gemensamma_verksamhetsposter[0].model_copy(update={'text':''})
  p=p.model_copy(update={'gemensamma_verksamhetsposter':(g,*p.gemensamma_verksamhetsposter[1:])});p=globalt(p);a=p.tjanster[0]
 p=p.model_copy(update={'tjanster':(a,*p.tjanster[1:])});fore=p.model_dump_json()
 ord={'lokalt':'pt_motivering', 'aktivering':'Block 1','relevans':'relevans','hot':'hot utanför','belagg':'belägg','kontroll':'sänkning','tf':'tf_motivering','globalt':'gemensamt verksamhetssvar'}[fel]
 with pytest.raises(RiskanalysFel,match=ord):bekrafta(f,p)
 assert p.model_dump_json()==fore

def test_gemensam_handling_kravs_forst_och_andrar_inte_tillampningar(grund):
 f,p=grund
 with pytest.raises(RiskanalysFel,match='gemensamma underlaget först'):bekrafta(f,p)
 p=globalt(p);q=bekrafta(f,p)
 assert q.tjanster[0].sarbarhetstillampningar==p.tjanster[0].sarbarhetstillampningar
 assert q.tjanster[0].verksamhetstillampningar==p.tjanster[0].verksamhetstillampningar

def test_andra_tjansters_obekraftade_block_stoppar_inte_forsta_genomgangen(grund):
 f,p=grund;p=globalt(p)
 # Sakfelet i en annan tjänst ska prövas när den tjänsten genomgås.
 a=p.tjanster[1].model_copy(update={'pt_motivering':''})
 p=p.model_copy(update={'tjanster':(p.tjanster[0],a,*p.tjanster[2:])})
 q=bekrafta(f,p)
 assert q.tjanster[1:]==p.tjanster[1:]
 assert all(b.bekraftad_summa for b in q.tjanster[0].block)


def eget_fall(f,p):
 from riskanalys.analys.gemensam import postsumma,tackningssumma
 from riskanalys.analys.provning import scenariosumma
 from riskanalys.analys.provning_v2 import kravda_riskled
 post=m.GemensamSarbarhetsprovning(id='egen-prov',omrade='kund',hot=('H-03',),dimension='pt',relevans='relevant',status='bekraftad',
  beskrivning='Alternativt dokumentformat kan bära samma osanna affärshändelse.',motivering='Formatets mekanism täcks av befintligt underlagsscenario.',belagg=('ab6:mandat',),forfattare='Syntetisk')
 a=p.tjanster[0];app=m.Sarbarhetstillampning(post=post.id,postsumma=postsumma(post),stallningstagande='galler')
 p=p.model_copy(update={'gemensamma_sarbarhetsprovningar':(*p.gemensamma_sarbarhetsprovningar,post),
  'tjanster':(a.model_copy(update={'sarbarhetstillampningar':(*a.sarbarhetstillampningar,app)}),*p.tjanster[1:])})
 p=globalt(p);a=p.tjanster[0];s=next(s for s in p.gemensamma_scenarier if 'H-03' in s.hot)
 # Ett uttryckligt scenario som ska bära egen täckning prövas före täckningshandlingen.
 a=a.model_copy(update={'scenariokopplingar':tuple(k.model_copy(update={'bekraftad':True,'scenariosumma':scenariosumma(s)}) if k.scenario==s.id else k for k in a.scenariokopplingar)})
 p=p.model_copy(update={'tjanster':(a,*p.tjanster[1:])});t=next(t for t in f.bedomning.tjanster if t.tjanst==a.tjanst)
 prov=[]
 for led in kravda_riskled(t,'H-03','pt'):
  q=m.Tackningsprovning(ursprung='gemensam',post=post.id,hot='H-03',dimension='pt',riskled=led,stallningstagande='tacks_av_scenario',
   lokalt_scenario=s.id,jamforelseniva='låg',motivering='Samma dokumentformat och kontrollens dokumenterade stickprov omfattas i detta riskled.',
   referensmotivering='Samma orsak ingår redan genom katalogfaktorn, enligt det belagda provet.',belagg=('ab6:kontroll',),forfattare='Syntetisk')
  prov.append(q.model_copy(update={'visad_summa':tackningssumma(f.regelbas,p,t,q)}))
 a=a.model_copy(update={'tackningsprovningar':tuple(prov)});return p.model_copy(update={'tjanster':(a,*p.tjanster[1:])})


def test_global_tackning_tjanst_lamnar_alla_hashar_aktuella(grund):
 from riskanalys.analys.provning_v2 import tackningsbrister
 f,p=grund;p=eget_fall(f,p);q=bekrafta(f,p);t=next(t for t in f.bedomning.tjanster if t.tjanst==q.tjanster[0].tjanst)
 assert not tackningsbrister(f.regelbas,q,t)
 assert q.tjanster[0].tackningsprovningar==p.tjanster[0].tackningsprovningar
 assert len(q.tjanster[0].tackningsprovningar)==2

@pytest.mark.parametrize('fel',['saknas','bara_inneboende','fel_tf','referens','forst_scenario'])
def test_egen_risk_kraver_separat_aktuell_provning(grund,fel):
 f,p=grund;p=eget_fall(f,p);a=p.tjanster[0];prov=a.tackningsprovningar
 if fel=='saknas':a=a.model_copy(update={'tackningsprovningar':()})
 elif fel=='bara_inneboende':a=a.model_copy(update={'tackningsprovningar':prov[:1]})
 elif fel=='fel_tf':a=a.model_copy(update={'tackningsprovningar':(prov[0].model_copy(update={'dimension':'tf'}),*prov[1:])})
 elif fel=='referens':a=a.model_copy(update={'tackningsprovningar':tuple(x.model_copy(update={'referensmotivering':''}) for x in prov)})
 else:a=a.model_copy(update={'scenariokopplingar':tuple(k.model_copy(update={'bekraftad':False}) for k in a.scenariokopplingar)})
 p=p.model_copy(update={'tjanster':(a,*p.tjanster[1:])});fore=p.model_dump_json()
 with pytest.raises(RiskanalysFel) as exc:bekrafta(f,p)
 if fel=='forst_scenario':assert 'Bekräfta scenariovalet före täckningsprövningen' in str(exc.value)
 assert p.model_dump_json()==fore


def test_ny_tjanst_far_visade_standardscenarier_utan_extra_klick(grund):
 from riskanalys.analys.engangssvar import visade_scenarioval
 f,p=grund;p=globalt(p);a=p.tjanster[0]
 a=a.model_copy(update={'scenariokopplingar':()})
 p=p.model_copy(update={'tjanster':(a,*p.tjanster[1:])})
 assert visade_scenarioval(f.regelbas,p,a.tjanst)
 q=bekrafta(f,p)
 assert all(k.bekraftad for k in q.tjanster[0].scenariokopplingar)
 assert not p.tjanster[0].scenariokopplingar and not q.beslut


def test_bekraftad_tjanstebeskrivning_ateranvands_med_kalla_datum_och_ansvarig(grund):
 from riskanalys.analys.engangssvar import tjanstefakta
 f,p=grund;id=p.tjanster[0].tjanst;prefix=f.regelbas.tjanster[id].erbjuds_falt.removesuffix('_erbjuds')
 falt=prefix+'_arbetssatt';u=f.profil.uppgifter[falt]
 rows=tjanstefakta(f.regelbas,f.profil,id)
 rad=next(r for r in rows if r[0]==falt)
 assert rad[2]==u.varde and rad[3:]==(u.kalla,u.datum,u.period,u.bekraftad_av)
 assert not any(r[0].startswith('P-TJ.red02_') for r in rows)


def test_genomgangen_visar_lokal_verksamhetsavvikelse_och_belagg(grund):
 from riskanalys.intag.engangsvy import genomgang
 f,p=grund;p=globalt(p);a=p.tjanster[0]
 post=next(x for x in p.gemensamma_verksamhetsposter if x.slag=='erfarenhet')
 appar=tuple(x.model_copy(update={'stallningstagande':'galler_annorlunda','motivering':'Lokalt undantag med belägg','belagg':('ab6:bevakning',)}) if x.post==post.id else x for x in a.verksamhetstillampningar)
 a=a.model_copy(update={'verksamhetstillampningar':appar,'erfarenhetsprovning':'Unik lokal <verksamhetsanalys>'})
 p=p.model_copy(update={'tjanster':(a,*p.tjanster[1:])})
 html=genomgang(f.regelbas,f.profil,f.bedomning,p,a.tjanst,'/syntetisk/','csrf','revision')
 assert 'Unik lokal &lt;verksamhetsanalys&gt;' in html
 assert 'Lokalt undantag med belägg' in html and 'ab6:bevakning' in html
 assert '<verksamhetsanalys>' not in html and 'name="erfarenhetsprovning"' not in html
