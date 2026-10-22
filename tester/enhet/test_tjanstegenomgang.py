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


@pytest.mark.parametrize('aktivering,etikett',[('aktiv','Aktivt'),('ej_tillamplig','Ej tillämpligt')])
def test_samlad_vy_visar_aktivering_och_motivering_fore_stampling(grund,aktivering,etikett):
 from riskanalys.intag.engangsvy import genomgang
 f,p=grund;a=p.tjanster[0]
 motiv='Unikt <avgränsningsskäl> att läsa före bekräftelse'
 a=a.model_copy(update={'block':tuple(b.model_copy(update={'aktivering':aktivering,'motivering':motiv}) if b.nummer==3 else b for b in a.block)})
 p=p.model_copy(update={'tjanster':(a,*p.tjanster[1:])})
 html=genomgang(f.regelbas,f.profil,f.bedomning,p,a.tjanst,'/syntetisk/','csrf','revision')
 assert 'Aktivering: '+etikett in html
 assert 'Unikt &lt;avgränsningsskäl&gt; att läsa före bekräftelse' in html
 assert motiv not in html


def test_native_kontroll_och_rutin_kan_sparas_fore_samlat_scenarioval(grund):
 from riskanalys.analys.utkast import forifyll_analys
 from riskanalys.intag.analysformular import las_blockformular
 f,p=grund
 nytt=forifyll_analys(f.regelbas,f.profil,f.bedomning,p.bindning,schema=2)
 a=nytt.tjanster[0];assert not a.scenariokopplingar
 scenario=next(s for s in nytt.gemensamma_scenarier if set(s.hot)<=set(f.regelbas.tjanster[a.tjanst].hot))
 for block,data in ((10,{'kontroller.0.anvand':'ja','kontroller.0.scenario':scenario.id,'kontroller.0.kontroll':f.regelbas.tjanster[a.tjanst].kontroller[0]}),
                    (16,{'rutinatgarder.0.anvand':'ja','rutinatgarder.0.id':'ny-rutin','rutinatgarder.0.scenarier':scenario.id})):
  andring=las_blockformular(nytt,a.tjanst,block,{'operation':'spara','forfattare':'Syntetisk',**data},rb=f.regelbas)
  assert not andring.tjanst.scenariokopplingar
  assert not any(b.bekraftad_summa for b in andring.tjanst.block)
 # Fullt sakunderlag utan preparerade gemensamma kopplingar ska även klara slutgenomgången.
 p=globalt(p);a=p.tjanster[0].model_copy(update={'scenariokopplingar':()})
 p=p.model_copy(update={'tjanster':(a,*p.tjanster[1:])})
 andring=las_blockformular(p,a.tjanst,10,{'operation':'spara','forfattare':'Syntetisk','kontroller.0.scenario':a.kontroller[0].scenario},rb=f.regelbas)
 p=p.model_copy(update={'tjanster':(andring.tjanst,*p.tjanster[1:])})
 q=bekrafta(f,p)
 assert all(k.bekraftad for k in q.tjanster[0].scenariokopplingar)
 assert not p.tjanster[0].scenariokopplingar and not q.beslut


def scenarioavvikelse(p):
 """Syntetisk giltig lokal variant; kontroll- och rutinreferenser följer varianten."""
 from riskanalys.analys.provning import scenariosumma
 a=p.tjanster[0];kop=a.scenariokopplingar[0]
 s=next(s for s in p.gemensamma_scenarier if s.id==kop.scenario)
 lokalt=s.model_copy(update={'id':'lokal:avvikelse','handelseforlopp':s.handelseforlopp+' Lokalt dokumenterat leveransled.'})
 def refs(v):return tuple(lokalt.id if x==s.id else x for x in v)
 a=a.model_copy(update={
  'scenarier':(*a.scenarier,lokalt),
  'scenariokopplingar':tuple(k.model_copy(update={'tillampning':'avviker','lokal_scenario':lokalt.id,'motivering':'Lokalt dokumenterat leveransled avviker från den gemensamma beskrivningen.','bekraftad':True,'scenariosumma':scenariosumma(s)}) if k.scenario==s.id else k for k in a.scenariokopplingar),
  'sarbarhetsprovningar':tuple(x.model_copy(update={'scenarier':refs(x.scenarier)}) for x in a.sarbarhetsprovningar),
  'kontroller':tuple(x.model_copy(update={'scenario':lokalt.id}) if x.scenario==s.id else x for x in a.kontroller),
  'rutinatgarder':tuple(x.model_copy(update={'scenarier':refs(x.scenarier)}) for x in a.rutinatgarder)})
 return p.model_copy(update={'tjanster':(a,*p.tjanster[1:])}),s


@pytest.mark.parametrize('fel',['andrat_scenario','obekraftad'])
def test_samlad_genomgang_fornyar_inte_gammal_scenarioavvikelse(grund,fel):
 f,p=grund;p,s=scenarioavvikelse(globalt(p));a=p.tjanster[0]
 # Det giltiga utgångsfallet måste klara den ordinarie samlade grinden.
 q=bekrafta(f,p)
 assert next(k for k in q.tjanster[0].scenariokopplingar if k.scenario==s.id)==next(k for k in a.scenariokopplingar if k.scenario==s.id)
 if fel=='andrat_scenario':
  p=p.model_copy(update={'gemensamma_scenarier':tuple(x.model_copy(update={'handelseforlopp':x.handelseforlopp+' Ett nytt internationellt flöde.'}) if x.id==s.id else x for x in p.gemensamma_scenarier)})
 else:
  a=a.model_copy(update={'scenariokopplingar':tuple(k.model_copy(update={'bekraftad':False}) if k.scenario==s.id else k for k in a.scenariokopplingar)})
  p=p.model_copy(update={'tjanster':(a,*p.tjanster[1:])})
 fore=p.model_dump_json()
 assert any('Scenariokopplingen '+s.id+' är inte aktuellt bekräftad' in x for x in analysbrister(f.regelbas,f.profil,f.bedomning,p))
 with pytest.raises(RiskanalysFel,match='pröva avvikelsen'):
  bekrafta(f,p)
 assert p.model_dump_json()==fore


def test_inaktuell_scenarioavvikelse_marks_med_lank_till_ny_provning(grund):
 from riskanalys.intag.engangsvy import genomgang
 f,p=grund;p,s=scenarioavvikelse(globalt(p))
 p=p.model_copy(update={'gemensamma_scenarier':tuple(x.model_copy(update={'motivering':x.motivering+' Ny sakuppgift.'}) if x.id==s.id else x for x in p.gemensamma_scenarier)})
 html=genomgang(f.regelbas,f.profil,f.bedomning,p,p.tjanster[0].tjanst,'/syntetisk/','csrf','revision')
 assert 'Det gemensamma scenariot har ändrats sedan avvikelsen; pröva avvikelsen på nytt' in html
 assert 'scenario='+s.id.replace(':','%3A') in html
 assert 'Pröva avvikelsen på nytt' in html


def test_standard_samma_far_fornyas_efter_visat_gemensamt_scenario(grund):
 from riskanalys.analys.provning import scenariosumma
 f,p=grund;p=globalt(p);a=p.tjanster[0];kop=a.scenariokopplingar[0]
 s=next(s for s in p.gemensamma_scenarier if s.id==kop.scenario)
 ny=s.model_copy(update={'handelseforlopp':s.handelseforlopp+' Gemensam komplettering att läsa.'})
 p=p.model_copy(update={'gemensamma_scenarier':tuple(ny if x.id==s.id else x for x in p.gemensamma_scenarier)})
 q=bekrafta(f,p)
 k=next(k for k in q.tjanster[0].scenariokopplingar if k.scenario==s.id)
 assert k.bekraftad and k.scenariosumma==scenariosumma(ny) and k.tillampning=='samma'
 assert not q.beslut
