import pytest
from tester.enhet.test_riktning_v2 import fall
from tester.conftest import regelbas_v1
from tester.enhet.test_gemensam_provning_v2 import provfall
from riskanalys.analys import modeller as m
from riskanalys.analys.gemensam import tackningssumma


@pytest.mark.parametrize('riktning',['oklar','mojlig_underskattning'])
def test_galler_annorlunda_saknar_inte_riktningsprovning_utan_katalogfaktor(fall,riktning):
    from riskanalys.analys.provning_v2 import gemensamma_analysbrister
    p,t,prov=provfall(fall,komplett=True);a=p.tjanster[0];app=a.sarbarhetstillampningar[0]
    app=app.model_copy(update={'stallningstagande':'galler_annorlunda','riktningsval':m.Riktningsval(riktning=riktning,
        motivering='Syntetiskt belagd men inte klarlagd högre lokal exponering',belagg=(p.belagg[0].id,)),
        'motivering':'Syntetisk avvikelse behöver lokal riktningsprövning','belagg':(p.belagg[0].id,)})
    a=a.model_copy(update={'sarbarhetstillampningar':(app,)})
    p=p.model_copy(update={'tjanster':(a,)})
    prover=tuple(x.model_copy(update={'visad_summa':tackningssumma(fall.rb,p,t,x)}) for x in a.tackningsprovningar)
    p=p.model_copy(update={'tjanster':(a.model_copy(update={'tackningsprovningar':prover}),)})
    fel=gemensamma_analysbrister(fall.rb,fall.profil,fall.bedomning,p)
    assert any('gäller annorlunda' in x and ('oklar' in x or 'underskattning' in x) for x in fel)
