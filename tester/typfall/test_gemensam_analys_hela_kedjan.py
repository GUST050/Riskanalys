"""Riktig schema2-kedja med enbart syntetiska sak-/modellattester i tempkopia."""
from dataclasses import replace
from collections import Counter
import shutil
import pytest
from tester.fixturer.analys_hela_kedjan import DAG,syntetisk_expertkopia,bygg_bunden_kedja
from riskanalys.analys import lagring as l,provning as p,modeller as m
from riskanalys.analys.gemensam import postsumma,tackningssumma
from riskanalys.analys.tjanst import Analystjanst
from riskanalys.fel import RiskanalysFel


@pytest.fixture(scope='module')
def bas(tmp_path_factory):
    from tester.fixturer.fylld_gemensam import ifylld_analys,bekrafta_innehall
    from riskanalys.granskning.korning import kor_granskning,las_granskning
    rot=tmp_path_factory.mktemp('gemensam-slutkedja').resolve();regelrot,rb=syntetisk_expertkopia(rot/'expert')
    k=bygg_bunden_kedja(rb,rot/'kedja',regelrot=regelrot,godkann=True);f=k.fall
    at=Analystjanst(f.byramapp,rb);original=l.las_analys(f.byramapp)
    gammalt_motor=f.bedomning.model_dump_json()
    at.overfor(p.registersumma(original),True)
    ny=l.las_analys(f.byramapp)
    # Uttryckligt syntetiska lokalsvar + ny användningsprövning. Ingen produktväg skapar dessa.
    q=ifylld_analys(rb,f.profil,f.bedomning,original,avvikelse=True,egen=True).model_copy(update={'revision':ny.revision})
    l.spara_analys(f.byramapp,q,forvantad_summa=p.registersumma(ny))
    handlingar=bekrafta_innehall(at,egen=True);a=l.las_analys(f.byramapp)
    assert not p.analysbrister(rb,f.profil,f.bedomning,a)
    for t in a.tjanster:
        at.beslut(t.tjanst,True,'Syntetisk slutgranskare','FfR',DAG,'Prövat underlag, avvikelse och täckning',p.registersumma(l.las_analys(f.byramapp)))
    a=l.las_analys(f.byramapp);gm=kor_granskning(f.byramapp,rb,DAG);d,fynd=las_granskning(gm)
    assert fynd==() and f.bedomning.model_dump_json()==gammalt_motor
    return replace(k,fall=replace(f,analys=a),granskningsmapp=gm),tuple(handlingar)


@pytest.fixture
def kedja(bas,tmp_path):
    from tester.fixturer.kedjecache import klona_kedja
    k,logg=bas
    return klona_kedja(k,tmp_path),logg


def test_sakgranskad_gemensam_analys_kan_faststallas(kedja):
    from riskanalys.granskning.korning import las_granskning
    from riskanalys.faststallelse.sakgranskning import registrera_sakgranskning,spara_sakgranskningar,struktur_summa
    from riskanalys.faststallelse.resultatgranskning import registrera_resultatgranskning
    from riskanalys.dokument.rapportpaket_v10 import las_presentation_v10 as las_presentation
    from riskanalys.faststallelse.faststall import faststall,verifiera_version
    from riskanalys.faststallelse.modeller import Beslut
    from riskanalys.analys.riktning import harled_riktningar
    k,logg=kedja;f=k.fall;a=l.las_analys(f.byramapp);d,fynd=las_granskning(k.granskningsmapp)
    rows=[r for t in f.bedomning.tjanster if t.erbjuds for r in harled_riktningar(f.regelbas,f.profil,a,t)]
    assert any(r.riktning=='lagre' for r in rows) and any(r.riktning=='tackt_av_scenario' for r in rows)
    assert all(r.riktning not in ('oklar','mojlig_underskattning') for r in rows)
    text=' '.join(s.text for av in d.avsnitt for s in av.stycken)
    assert 'Referens: samma scenario med ytterligare +1' in text and 'Syntetisk belagd gemensam orsak' in text
    pres=las_presentation(k.granskningsmapp,f.bedomning,f.profil,regelbas=f.regelbas)
    poster=registrera_resultatgranskning((),d,f.profil,presentation=pres,
        visad_struktursumma=struktur_summa(d,presentation=pres),analysbindning=p.registersumma(a),
        godkand=True,roll='FfR',namn='Syntetisk dokumentgranskare',datum=DAG)
    for av in d.avsnitt:
        if av.leveransdel!='resultatrapport':
            poster=registrera_sakgranskning(poster,d,f.profil,av.id,True,'FfR','Syntetisk dokumentgranskare',DAG,analysbindning=p.registersumma(a),presentation=pres)
    spara_sakgranskningar(f.byramapp,poster)
    version=faststall(f.byramapp,k.regelrot,f.regelbas,Beslut(organ='styrelsen',namn='Syntetisk beslutsfattare',roll='FfR',datum=DAG))
    assert verifiera_version(f.byramapp,1)==[]
    assert all((version/f).is_file() for f in ('allman-riskbedomning-v1.docx','analysbilaga-v1.docx','underlagsbilaga-v1.docx'))
    assert Counter(logg)=={'samlad_tillampning':4,'lokal_avvikelse':4,'scenarioval':46,'tackningsprovning':2,'blockbekraftelse':64}


@pytest.mark.parametrize('fel,ord',[('bara_inneboende','kvarstående'),('bara_kvarstaende','inneboende'),('utan_tackning','saknar uttrycklig täckning'),('referens','under referensen'),('fel_dimension','hot/dimension'),('oklar','oklar'),('saknad_koppling','saknar tjänst')])
def test_egna_och_oklara_risker_kan_inte_gommas_med_stangd_lucka(kedja,fel,ord):
    from riskanalys.granskning.korning import kor_granskning,las_granskning
    from riskanalys.faststallelse.faststall import faststall,FaststallelseFel
    from riskanalys.faststallelse.modeller import Beslut
    k,_=kedja;f=k.fall;a=l.las_analys(f.byramapp);t=a.tjanster[0]
    if fel in ('bara_inneboende','bara_kvarstaende'):
        riskled='inneboende' if fel=='bara_inneboende' else 'kvarstaende'
        t=t.model_copy(update={'tackningsprovningar':tuple(x for x in t.tackningsprovningar if x.riskled==riskled)})
    elif fel=='utan_tackning':t=t.model_copy(update={'tackningsprovningar':()})
    elif fel in ('referens','fel_dimension'):
        prov=t.tackningsprovningar[0].model_copy(update={'referensmotivering':''} if fel=='referens' else {'dimension':'tf'})
        t=t.model_copy(update={'tackningsprovningar':(prov,)})
    else:
        appar=list(t.sarbarhetstillampningar);i=next(i for i,x in enumerate(appar) if x.post!='egen:slutprov')
        if fel=='oklar':appar[i]=appar[i].model_copy(update={'stallningstagande':'galler_annorlunda','riktningsval':m.Riktningsval()})
        else:appar[i]=appar[i].model_copy(update={'stallningstagande':'galler','hotkopplingar':(m.Hotanknytning(hot='H-TJ-05',dimension='pt'),)})
        t=t.model_copy(update={'sarbarhetstillampningar':tuple(appar)})
    # Luckor kan tas bort eller stängas, men härledda riskbrister måste finnas kvar.
    t=t.model_copy(update={'gap':tuple(g.model_copy(update={'status':'atgardat'}) for g in t.gap)})
    a=a.model_copy(update={'tjanster':(t,*a.tjanster[1:])})
    motor=next(x for x in f.bedomning.tjanster if x.tjanst==t.tjanst)
    if t.tackningsprovningar:
        prov=t.tackningsprovningar[0];prov=prov.model_copy(update={'visad_summa':tackningssumma(f.regelbas,a,motor,prov)})
        t=t.model_copy(update={'tackningsprovningar':(prov,)})
        a=a.model_copy(update={'tjanster':(t,*a.tjanster[1:])})
    from tester.fixturer.analys_hela_kedjan import _bekrafta
    a=_bekrafta(a)
    assert any(ord in x for x in p.analysbrister(f.regelbas,f.profil,f.bedomning,a))
    cas=l.spara_analys(f.byramapp,a,forvantad_summa=p.registersumma(l.las_analys(f.byramapp)))
    with pytest.raises(RiskanalysFel):Analystjanst(f.byramapp,f.regelbas).beslut(t.tjanst,True,'Syntetisk','FfR',DAG,'',cas)
    gm=kor_granskning(f.byramapp,f.regelbas,DAG);assert any(x.allvar=='blockerande' for x in las_granskning(gm)[1])
    with pytest.raises(FaststallelseFel):faststall(f.byramapp,k.regelrot,f.regelbas,Beslut(organ='styrelsen',namn='Syntetisk',roll='FfR',datum=DAG))


@pytest.fixture(scope='module')
def engangsbas(tmp_path_factory):
    rot=tmp_path_factory.mktemp('engangskedja').resolve()
    regelrot,rb=syntetisk_expertkopia(rot/'expert')
    return bygg_bunden_kedja(rb,rot/'kedja',regelrot=regelrot,godkann=True)


@pytest.mark.fullkedja
@pytest.mark.parametrize('egen',[False,True])
def test_publika_engangshandlingar_bevarar_tackning_och_analysgrind(engangsbas,tmp_path,egen):
    from tester.fixturer.fylld_gemensam import bekrafta_innehall,ifylld_analys
    from tester.fixturer.kedjecache import klona_kedja
    k=klona_kedja(engangsbas,tmp_path);f=k.fall;at=Analystjanst(f.byramapp,f.regelbas)
    original=l.las_analys(f.byramapp);at.overfor(p.registersumma(original),True)
    sparat=l.las_analys(f.byramapp)
    p0=ifylld_analys(f.regelbas,f.profil,f.bedomning,original,avvikelse=egen,egen=egen).model_copy(update={'revision':sparat.revision})
    p0=p0.model_copy(update={'beslut':(),'tjanster':tuple(a.model_copy(update={
        'block':tuple(b.model_copy(update={'bekraftad_summa':None}) for b in a.block),
        'sarbarhetstillampningar':tuple(x.model_copy(update={'bekraftad':False}) for x in a.sarbarhetstillampningar),
        'verksamhetstillampningar':tuple(x.model_copy(update={'bekraftad':False}) for x in a.verksamhetstillampningar),
        'scenariokopplingar':tuple(x.model_copy(update={'bekraftad':False}) for x in a.scenariokopplingar),
        'tackningsprovningar':()}) for a in p0.tjanster)})
    if not egen:
        p0=p0.model_copy(update={'gemensamma_sarbarhetsprovningar':tuple(g for g in p0.gemensamma_sarbarhetsprovningar if g.id!='egen:slutprov'),
            'tjanster':tuple(a.model_copy(update={'scenariokopplingar':(),'sarbarhetstillampningar':tuple(x.model_copy(update={'stallningstagande':'galler'}) for x in a.sarbarhetstillampningar if x.post!='egen:slutprov')}) for a in p0.tjanster)})
    l.spara_analys(f.byramapp,p0,forvantad_summa=p.registersumma(l.las_analys(f.byramapp)))
    if not egen:
        # Vanliga bundna sparningar måste fungera före F2, utan importerade kopplingar.
        for a in l.las_analys(f.byramapp).tjanster:
            assert not a.scenariokopplingar
            for nummer,data in ((10,{'kontroller.0.scenario':a.kontroller[0].scenario}),
                                (16,{'rutinatgarder.0.scenarier':','.join(a.rutinatgarder[0].scenarier)})):
                at.spara_block(a.tjanst,nummer,{'operation':'spara','forfattare':'Syntetisk',**data},p.registersumma(l.las_analys(f.byramapp)))
            sparat=l.las_analys(f.byramapp)
            assert not next(x for x in sparat.tjanster if x.tjanst==a.tjanst).scenariokopplingar
            assert not sparat.beslut
    logg=bekrafta_innehall(at,egen=egen,samlat=True);q=l.las_analys(f.byramapp)
    assert Counter(logg)==({'lokal_avvikelse':4,'gemensam_bekraftelse':1,'scenarioval':1,'tackningsprovning':2,'tjanstegenomgang':4} if egen else {'gemensam_bekraftelse':1,'tjanstegenomgang':4})
    assert not p.analysbrister(f.regelbas,f.profil,f.bedomning,q) and not q.beslut
    assert all(b.bekraftad_summa==p.blocksumma(q,a.tjanst,b.nummer) for a in q.tjanster for b in a.block)
    # Senare ändrad täckning gör genomgången inaktuell enligt den befintliga summan.
    if not egen:return
    a=q.tjanster[0];prov=a.tackningsprovningar[0].model_copy(update={'motivering':'Ny syntetisk täckningsmotivering'})
    t=next(t for t in f.bedomning.tjanster if t.tjanst==a.tjanst)
    prov=prov.model_copy(update={'visad_summa':tackningssumma(f.regelbas,q,t,prov)})
    at.spara_tackningsprovning(a.tjanst,prov,p.registersumma(q),prov.forfattare)
    n=l.las_analys(f.byramapp)
    assert p.blocksumma(n,a.tjanst,1)!=p.blocksumma(q,a.tjanst,1)


@pytest.mark.parametrize('operation',['gemensamt','tjanst'])
@pytest.mark.parametrize('fel',['andrat','saknas'])
def test_samlad_bekraftelse_kontrollerar_privata_belaggsbytes_atomiskt(engangsbas,tmp_path,operation,fel):
 from riskanalys.analys.engangssvar import visade_celler
 from tester.fixturer.fylld_gemensam import ifylld_analys
 from tester.fixturer.kedjecache import klona_kedja
 k=klona_kedja(engangsbas,tmp_path);f=k.fall;at=Analystjanst(f.byramapp,f.regelbas)
 original=l.las_analys(f.byramapp);at.overfor(p.registersumma(original),True)
 sparat=l.las_analys(f.byramapp)
 nytt=ifylld_analys(f.regelbas,f.profil,f.bedomning,original).model_copy(update={'revision':sparat.revision})
 l.spara_analys(f.byramapp,nytt,forvantad_summa=p.registersumma(sparat))
 nytt=l.las_analys(f.byramapp)
 ids=tuple(a.tjanst for a in nytt.tjanster)
 at.bekrafta_byraunderlag(ids,visade_celler(nytt,ids),p.registersumma(nytt),'Syntetisk')
 aktuellt=l.las_analys(f.byramapp)
 b=next(b for b in aktuellt.belagg if b.id=='ab6:kontroll')
 fil=f.byramapp/'analys/belagg'/b.dokument
 if fel=='saknas':fil.unlink()
 else:fil.write_bytes(b'Andrat syntetiskt kontrollunderlag')
 fore=(f.byramapp/l.ANALYSFIL).read_bytes()
 with pytest.raises(RiskanalysFel,match='Belägget har ändrats|Beläggskopian saknas'):
  if operation=='gemensamt':at.bekrafta_byraunderlag(ids,visade_celler(aktuellt,ids),p.registersumma(aktuellt),'Syntetisk')
  else:at.bekrafta_tjansteunderlag(ids[0],p.registersumma(aktuellt),'Syntetisk')
 assert (f.byramapp/l.ANALYSFIL).read_bytes()==fore


def test_andrat_gemensamt_scenario_kraver_ny_separat_avvikelseprovning(engangsbas,tmp_path):
 from tester.fixturer.kedjecache import klona_kedja
 from tester.fixturer.fylld_gemensam import ifylld_analys
 from tester.enhet.test_tjanstegenomgang import scenarioavvikelse
 from riskanalys.analys.engangssvar import visade_celler
 k=klona_kedja(engangsbas,tmp_path);f=k.fall;at=Analystjanst(f.byramapp,f.regelbas)
 original=l.las_analys(f.byramapp);at.overfor(p.registersumma(original),True)
 sparat=l.las_analys(f.byramapp)
 nytt=ifylld_analys(f.regelbas,f.profil,f.bedomning,original).model_copy(update={'revision':sparat.revision})
 nytt,s=scenarioavvikelse(nytt)
 l.spara_analys(f.byramapp,nytt,forvantad_summa=p.registersumma(sparat))
 def paket():return l.las_analys(f.byramapp)
 nytt=paket();ids=tuple(a.tjanst for a in nytt.tjanster);id=ids[0]
 at.bekrafta_byraunderlag(ids,visade_celler(nytt,ids),p.registersumma(nytt),'Syntetisk')
 at.bekrafta_tjansteunderlag(id,p.registersumma(paket()),'Syntetisk')
 at.spara_gemensamt(s.id,{'forfattare':'Syntetisk','visad_summa':p.scenariosumma(s),'handelseforlopp':s.handelseforlopp+' Nytt dokumenterat flöde.'},p.registersumma(paket()))
 fore=(f.byramapp/l.ANALYSFIL).read_bytes();q=paket();a=q.tjanster[0]
 with pytest.raises(RiskanalysFel,match='Det gemensamma scenariot har ändrats sedan avvikelsen; pröva avvikelsen på nytt'):
  at.bekrafta_tjansteunderlag(id,p.registersumma(q),'Syntetisk')
 assert (f.byramapp/l.ANALYSFIL).read_bytes()==fore and not paket().beslut
 # Explicit separat val mot den nya scenariotexten, inte en samlad omstämpling.
 ny=next(x for x in q.gemensamma_scenarier if x.id==s.id)
 kop=next(x for x in a.scenariokopplingar if x.scenario==s.id)
 at.spara_scenarioval(id,s.id,{'tillampning':'avviker','lokal_scenario':kop.lokal_scenario,'motivering':kop.motivering+' Ny jämförelse utförd.','visad_summa':p.scenariosumma(ny),'forfattare':'Syntetisk prövare'},p.registersumma(q))
 at.bekrafta_tjansteunderlag(id,p.registersumma(paket()),'Syntetisk')
 q=paket();assert not q.beslut
 assert all(b.bekraftad_summa==p.blocksumma(q,id,b.nummer) for b in q.tjanster[0].block)
