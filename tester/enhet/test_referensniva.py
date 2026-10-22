import pytest
from tester.enhet.test_riktning_v2 import fall

@pytest.mark.parametrize('dimension',['pt','tf'])
def test_plus_ett_anvander_befintlig_scenarioregel_pt_och_tf(fall,dimension):
    from riskanalys.analys.referens import referensniva
    from riskanalys.bedomning.motor import RISKNIVAER
    t=next(t for t in fall.bedomning.tjanster if t.erbjuds)
    fore=t.model_dump_json();rbfore=fall.rb.model_dump_json()
    for s in t.scenarier:
        if s.dimension==dimension:
            risk=referensniva(fall.rb,fall.profil,t,s.hot,dimension,'inneboende')
            assert RISKNIVAER.index(risk)>=RISKNIVAER.index(s.risk)
    assert t.model_dump_json()==fore and fall.rb.model_dump_json()==rbfore

def test_saknat_scenario_ger_ingen_pahittad_referens(fall):
    from riskanalys.analys.referens import referensniva
    t=next(t for t in fall.bedomning.tjanster if t.erbjuds)
    assert referensniva(fall.rb,fall.profil,t,'finns-inte','pt','inneboende') is None
    assert referensniva(fall.rb,fall.profil,t,'H-TF-01','tf','kvarstaende') is None


def test_referensen_motsvarar_faktisk_scenarioregel_med_plus_ett(fall):
    from riskanalys.analys.referens import referensniva
    from riskanalys.bedomning.scenarier import _scenario
    from riskanalys.regelverk.modeller import Sarbarhet,Effekt
    t=next(t for t in fall.bedomning.tjanster if t.erbjuds);kat=fall.rb.tjanster[t.tjanst]
    for s in t.scenarier:
        extra=Sarbarhet(id='PROV',namn='Kontrafaktisk',omrade='verk',grund='metodval',villkor={'falt':kat.erbjuds_falt,'op':'==','varde':True},
            effekt=Effekt(sannolikhet=1),galler='bada',kallor=('SRC-PTL',),hot=(s.hot,))
        valda=tuple(fall.rb.sarbarheter[id] for id in s.sarbarheter)+(extra,)
        kontrafaktisk=_scenario(fall.rb,kat,fall.rb.hot[s.hot],s.dimension,valda,t.kontroller,frozenset((s.hot,)) if s.iakttaget else frozenset())
        assert referensniva(fall.rb,fall.profil,t,s.hot,s.dimension,'inneboende')==kontrafaktisk.risk
        if s.dimension=='pt':assert referensniva(fall.rb,fall.profil,t,s.hot,s.dimension,'kvarstaende')==kontrafaktisk.kvarstaende
