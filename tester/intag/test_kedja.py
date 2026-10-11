from datetime import date
from docx import Document
import pytest
from riskanalys.bedomning.korning import kor_bedomning, las_bedomning
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.modeller import AvsnittsUtkast
from riskanalys.profil.lagring import spara_profil
from riskanalys.intag.dokument import skapa_utkast
from riskanalys.fel import RiskanalysFel
from riskanalys.intag.tackning import tackning
from tester.fixturer.m2 import bygg_testsvar


def test_hel_kedja_ger_word_utan_fritext_till_ai(tmp_path, rb_intag, klar):
    text='LOKALT_UNDERLAG_MED_UNIKT_PERSONNAMN'
    upp={**klar.uppgifter,'P-TJ.red01_arbetssatt':klar.uppgifter['P-TJ.red01_arbetssatt'].model_copy(update={'varde':text})}
    p=klar.model_copy(update={'uppgifter':upp})
    spara_profil(tmp_path,p)
    b=las_bedomning(kor_bedomning(tmp_path,rb_intag))
    provider=Testleverantor([AvsnittsUtkast.model_validate(a) for a in bygg_testsvar(rb_intag,p,b)])
    fil=skapa_utkast(tmp_path,rb_intag,provider)
    assert fil.exists()
    dokument=Document(fil)
    alltext='\n'.join(p.text for p in dokument.paragraphs)
    assert text in alltext and 'UTKAST' in alltext
    assert all(text not in u.model_dump_json() for u,_ in provider.anrop)
    assert not list((tmp_path/'faststallelser').glob('*'))


def test_ofullstandigt_stoppar_fore_ai(tmp_path,rb_intag,tom):
    spara_profil(tmp_path,tom)
    provider=Testleverantor([])
    with pytest.raises(RiskanalysFel,match='komplettera|Komplettera'):
        skapa_utkast(tmp_path,rb_intag,provider)
    assert not provider.anrop


@pytest.mark.parametrize('senare',['bedomning','underkand_skrivning'])
def test_omexport_bevarar_ursprungliga_riskavsnitt_efter_ny_bedomning(tmp_path,rb_intag,klar,senare):
    from riskanalys.intag.dokument import uppdatera_export
    from riskanalys.granskning.korning import GRANSKNING,las_granskning
    from riskanalys.lagring.manifest import manifestets_metadata
    spara_profil(tmp_path,klar)
    b=las_bedomning(kor_bedomning(tmp_path,rb_intag))
    provider=Testleverantor([AvsnittsUtkast.model_validate(a) for a in bygg_testsvar(rb_intag,klar,b)])
    gammal=skapa_utkast(tmp_path,rb_intag,provider)
    meta=manifestets_metadata(gammal.parent,'granskning')
    ursprung,_=las_granskning(tmp_path/GRANSKNING/meta['granskning'])
    # En annan session bedömer identiska fakta, utan en ny godkänd AI-skrivning.
    if senare=='bedomning':
        kor_bedomning(tmp_path,rb_intag)
    else:
        from riskanalys.dokument.skrivning import kor_skrivning
        kor_skrivning(tmp_path,rb_intag,Testleverantor(['Ogiltigt syntetiskt svar']*9))
    ny=uppdatera_export(tmp_path,rb_intag,gammal)
    meta=manifestets_metadata(ny.parent,'granskning')
    nytt,_=las_granskning(tmp_path/GRANSKNING/meta['granskning'])
    assert {a.id for a in nytt.avsnitt} == {a.id for a in ursprung.avsnitt}
