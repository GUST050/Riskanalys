"""R4/R5: verklig granskning, tre exportdelar och frysta källor."""
import json
import pytest
from tester.fixturer.resultatkedja import resultatkedja_bas,resultatkedja,DAG
from riskanalys.granskning.korning import kor_granskning,las_granskning
from riskanalys.lagring.manifest import verifiera_manifest,las_manifest,skriv_manifest
from riskanalys.dokument.export import kor_export_utkast
from riskanalys.fel import RiskanalysFel


@pytest.fixture
def granskad(resultatkedja):
    k=resultatkedja;f=k.fall;gm=kor_granskning(f.byramapp,f.regelbas,DAG,rapportformat='v9')
    return k,gm


def test_fyndlistan_skapar_inte_rekursiv_rapport(granskad):
    from riskanalys.dokument.rapportpaket_v9 import las_presentation_v9
    k,g=granskad;f=k.fall;d,fynd=las_granskning(g)
    assert not fynd
    p=las_presentation_v9(g,f.bedomning,f.profil,regelbas=f.regelbas)
    assert p.fyndkalla==fynd
    assert all((g/x).is_file() for x in ('analysdokument-v8.json','resultatunderlag-v9.json','transformationer-v9.json','resultatbygge-v9.json','kallor-v9.json','kravkarta-v9.json'))
    assert verifiera_manifest(g)==[]


def test_v7_skrivresultat_far_inte_markas_om(resultatkedja,monkeypatch):
    import riskanalys.granskning.korning as g
    from riskanalys.dokument.delskrivning import Tjanstresultat
    k=resultatkedja;orig=g.godkanda_utkast
    def gammalt(*a,**kw):
        r,m=orig(*a,**kw)
        return {id:v.model_copy(update={'formatversion':'D-ARB-tjanst-v7'}) for id,v in r.items()},m
    monkeypatch.setattr(g,'godkanda_utkast',gammalt)
    with pytest.raises(RiskanalysFel,match='V8-skrivresultat'):
        kor_granskning(k.fall.byramapp,k.fall.regelbas,DAG,rapportformat='v9')


def test_tre_exportfiler_och_verifiering(granskad):
    k,g=granskad;f=k.fall;e=kor_export_utkast(f.byramapp,DAG,granskningsmapp=g,regelbas=f.regelbas)
    assert verifiera_manifest(e)==[]
    assert len(list(e.glob('*.docx')))==3
    assert (e/'analysbilaga-UTKAST.docx').is_file()
    assert json.loads((e/'leverans.json').read_text())['version'] is None


@pytest.mark.parametrize('fel',['analysbilaga','ytterhint','fryst_kalla','dokument_saknas'])
def test_saknad_del_eller_andrad_kalla_avvisas(granskad,fel):
    k,g=granskad;f=k.fall;e=kor_export_utkast(f.byramapp,DAG,granskningsmapp=g,regelbas=f.regelbas)
    meta=las_manifest(e).metadata
    if fel=='analysbilaga':(e/'analysbilaga-UTKAST.docx').unlink()
    elif fel=='ytterhint':
        meta['dokumentformat']='D-ARB-tjanst-v8';(e/'analysbilaga-UTKAST.docx').unlink()
    elif fel=='dokument_saknas':(e/'granskning/dokument.json').unlink()
    else:(e/'granskning/kallor-v9.json').write_text('{}')
    # Även ett omskrivet yttre manifest kan inte legitimera saknade frysta delar.
    skriv_manifest(e,meta)
    assert verifiera_manifest(e)


def test_fel_vid_tredje_filen_publicerar_ingenting(granskad,monkeypatch):
    import docx.document
    k,g=granskad;f=k.fall;orig=docx.document.Document.save
    fore=set((f.byramapp/'export').glob('*'));n=0
    def fel(self,*a,**kw):
        nonlocal n
        n+=1
        if n==3:raise OSError('Syntetiskt skrivfel på tredje filen')
        return orig(self,*a,**kw)
    monkeypatch.setattr(docx.document.Document,'save',fel)
    with pytest.raises(RiskanalysFel):kor_export_utkast(f.byramapp,DAG,granskningsmapp=g,regelbas=f.regelbas)
    assert set((f.byramapp/'export').glob('*'))==fore


def test_v9_aterskapas_fran_frysta_kallor_pa_tom_datamapp(granskad,tmp_path):
    import shutil
    from riskanalys.dokument.rapportpaket_v9 import las_presentation_v9
    from riskanalys.dokument.rapportvyer_v9 import bygg_rapportvyer_v9
    from riskanalys.dokument.leverans_v9 import LeveransV9
    from riskanalys.dokument.rendering_v9 import rendera_rapportvyer_v9
    k,g=granskad;f=k.fall;kopia=tmp_path/'fryst';shutil.copytree(g,kopia)
    p=las_presentation_v9(kopia,f.bedomning,f.profil,aktuell=False)
    d,_=las_granskning(kopia)
    paths=rendera_rapportvyer_v9(bygg_rapportvyer_v9(d),f.profil,tmp_path/'tom',presentation=p,
        leverans=LeveransV9(datum=DAG,bedomning='fryst',granskning='fryst'))
    assert len(paths)==3 and all(x.is_file() for x in paths)
