import pytest
from riskanalys.fel import RiskanalysFel


@pytest.mark.parametrize('stallning',['galler','beror_inte','otillrackligt'])
def test_byte_fran_annorlunda_kasserar_gamla_manuella_riktningsfalt(stallning):
    from riskanalys.intag.gemensamformular import las_tillampning
    from tester.enhet.test_gemensam_analys_v2 import paket
    from riskanalys.analys import modeller as m
    p=paket();a=p.tjanster[0];app=a.sarbarhetstillampningar[0].model_copy(update={'stallningstagande':'galler_annorlunda','riktningsval':m.Riktningsval()})
    p=p.model_copy(update={'tjanster':(a.model_copy(update={'sarbarhetstillampningar':(app,)}),*p.tjanster[1:])})
    data={'slag':'sarbarhet','post':app.post,'tjanst':a.tjanst,'postsumma':app.postsumma,'stallningstagande':stallning,
          'riktningsval.riktning':'lagre','riktningsval.motivering':'Gammalt manuellt val','riktningsval.belagg':'prov'}
    ref,ny=las_tillampning(data,paket=p)
    assert ny.riktningsval is None
    with pytest.raises(RiskanalysFel):las_tillampning({**data,'riktning':'lagre'},paket=p)
    with pytest.raises(RiskanalysFel):las_tillampning(data,paket=paket())
