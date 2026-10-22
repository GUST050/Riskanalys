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
    from riskanalys.faststallelse.sakgranskning import registrera_sakgranskning,spara_sakgranskningar
    from riskanalys.dokument.rapportpaket_v8 import las_presentation
    from riskanalys.faststallelse.faststall import faststall,verifiera_version
    from riskanalys.faststallelse.modeller import Beslut
    from riskanalys.analys.riktning import harled_riktningar
    k,logg=kedja;f=k.fall;a=l.las_analys(f.byramapp);d,fynd=las_granskning(k.granskningsmapp)
    rows=[r for t in f.bedomning.tjanster if t.erbjuds for r in harled_riktningar(f.regelbas,f.profil,a,t)]
    assert any(r.riktning=='lagre' for r in rows) and any(r.riktning=='tackt_av_scenario' for r in rows)
    assert all(r.riktning not in ('oklar','mojlig_underskattning') for r in rows)
    text=' '.join(s.text for av in d.avsnitt for s in av.stycken)
    assert 'Referens: samma scenario med ytterligare +1' in text and 'Syntetisk belagd gemensam orsak' in text
    pres=las_presentation(k.granskningsmapp,f.bedomning,f.profil,regelbas=f.regelbas);poster=()
    for av in d.avsnitt:
        poster=registrera_sakgranskning(poster,d,f.profil,av.id,True,'FfR','Syntetisk dokumentgranskare',DAG,analysbindning=p.registersumma(a),presentation=pres)
    spara_sakgranskningar(f.byramapp,poster)
    version=faststall(f.byramapp,k.regelrot,f.regelbas,Beslut(organ='styrelsen',namn='Syntetisk beslutsfattare',roll='FfR',datum=DAG))
    assert verifiera_version(f.byramapp,1)==[]
    assert (version/'allman-riskbedomning-v1.docx').is_file() and (version/'underlagsbilaga-v1.docx').is_file()
    assert Counter(logg)=={'samlad_tillampning':4,'lokal_avvikelse':4,'scenarioval':32,'tackningsprovning':2,'blockbekraftelse':64}


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
