"""R6: samma skydd och aktualitet för alla tre nedladdningarna."""
import threading
import pytest
from tester.fixturer.resultatkedja import resultatkedja_bas,resultatkedja,DAG
from tester.intag.test_webb import anrop
from riskanalys.granskning.korning import kor_granskning,las_granskning
from riskanalys.dokument.export import kor_export_utkast,UTKASTFIL
from riskanalys.intag.dokument import uppdatera_export
from riskanalys.profil.lagring import profilrevision


@pytest.fixture
def webb(resultatkedja,monkeypatch):
    from riskanalys.intag.webb import skapa_server
    from riskanalys.intag.tjanst import Intagstjanst
    k=resultatkedja;f=k.fall
    monkeypatch.setenv('RISKANALYS_DATA',str(f.byramapp.parent))
    g=kor_granskning(f.byramapp,f.regelbas,DAG,rapportformat='v10')
    e=kor_export_utkast(f.byramapp,DAG,granskningsmapp=g,regelbas=f.regelbas)
    s=skapa_server(Intagstjanst(f.byramapp.name,f.regelbas));s.utkast=e/UTKASTFIL;s.utkastrevision=profilrevision(f.profil)
    thread=threading.Thread(target=s.serve_forever,daemon=True);thread.start()
    yield s,k
    s.shutdown();s.server_close();thread.join(timeout=2)


def test_tre_tydligt_namngivna_nedladdningar(webb):
    s,k=webb;status,text,_=anrop(s,'?oversikt=1')
    assert status==200 and 'Hämta resultatrapport' in text and 'Hämta analysbilaga' in text and 'Hämta underlagsbilaga' in text
    for route in ('word','analysbilaga','underlag'):
        status,text,h=anrop(s,route)
        assert status==200 and 'attachment;' in h['Content-Disposition']


def test_analysbilaga_far_samma_aktualitetskontroll_som_resultatrapport(webb):
    from riskanalys.analys.lagring import las_analys,spara_analys
    from riskanalys.analys.provning import registersumma
    s,k=webb;a=las_analys(k.fall.byramapp)
    t=a.tjanster[0].model_copy(update={'pt_motivering':a.tjanster[0].pt_motivering+' Ny dokumenterad lokal prövning.'})
    spara_analys(k.fall.byramapp,a.model_copy(update={'tjanster':(t,*a.tjanster[1:])}),forvantad_summa=registersumma(a))
    for route in ('word','analysbilaga','underlag'):
        status,text,_=anrop(s,route)
        assert status in (400,409) and 'Analys' in text or status in (400,409) and 'analys' in text


def test_ogiltig_revision_eller_fel_route_ger_ingen_export(webb):
    s,k=webb;fore=tuple((k.fall.byramapp/'export').iterdir())
    assert anrop(s,'analysbilaga?fil=profil.yaml')[0] in (400,404)
    assert anrop(s,'uppdaterautkast',{'csrf':s.csrf,'revision':'gammal','rapportformat':'v10'})[0] in (400,409)
    assert tuple((k.fall.byramapp/'export').iterdir())==fore


def test_uppdatera_v8_till_v10_anropar_inte_ai_och_bevarar_original(resultatkedja,monkeypatch):
    from riskanalys.dokument import skrivning
    from riskanalys.dokument import rapportversion
    k=resultatkedja;f=k.fall
    gammal=kor_export_utkast(f.byramapp,DAG,granskningsmapp=k.granskningsmapp,regelbas=f.regelbas)/UTKASTFIL
    original=gammal.read_bytes()
    def forbjudet(*a,**kw):pytest.fail('Formatbyte anropade skrivning')
    monkeypatch.setattr(skrivning,'kor_skrivning',forbjudet)
    monkeypatch.setattr(rapportversion,'AKTUELL_DOKUMENTVERSION',rapportversion.V10)
    vanlig=uppdatera_export(f.byramapp,f.regelbas,gammal)
    assert las_granskning(vanlig.parent/'granskning')[0].formatversion==rapportversion.V8
    ny=uppdatera_export(f.byramapp,f.regelbas,gammal,rapportformat='v10')
    assert las_granskning(ny.parent/'granskning')[0].formatversion==rapportversion.V10
    assert gammal.read_bytes()==original and ny!=gammal


def test_formatbyte_visar_behov_av_fornyad_sakgranskning(resultatkedja,monkeypatch):
    from riskanalys.intag.webb import skapa_server
    from riskanalys.intag.tjanst import Intagstjanst
    k=resultatkedja;f=k.fall;monkeypatch.setenv('RISKANALYS_DATA',str(f.byramapp.parent))
    e=kor_export_utkast(f.byramapp,DAG,granskningsmapp=k.granskningsmapp,regelbas=f.regelbas)
    s=skapa_server(Intagstjanst(f.byramapp.name,f.regelbas));s.utkast=e/UTKASTFIL;s.utkastrevision=profilrevision(f.profil)
    t=threading.Thread(target=s.serve_forever,daemon=True);t.start()
    try:
        status,text,_=anrop(s,'?oversikt=1')
        assert status==200 and 'förnyad sakgranskning av alla tre delar' in text
    finally:s.shutdown();s.server_close();t.join(timeout=2)
