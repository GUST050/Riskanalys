"""Provisoriska metodval binds till innehåll och körbar implementation."""
import pytest
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.sakkunnig import granskningsobjekt
from riskanalys.regelverk.validering import validera


def test_alla_beslut_ar_egna_ogranskade_objekt(regelbas_v1):
    rb=regelbas_v1
    assert set(rb.metodbeslut)=={'D'+str(n) for n in range(1,10)}|{'D-LAGRE'}
    for id,b in rb.metodbeslut.items():
        assert b.sakkunnig.status=='ej_granskad'
        assert b.objekt and b.modellfiler and b.kallbelagg and len(b.alternativ)>=2
        assert id in granskningsobjekt(rb,'RP-RED-VG')
    assert not validera(rb)


def test_historisk_regelbas_utan_beslut_bevarar_dump(regelbas_v1):
    data=regelbas_v1.model_dump(mode='json');data.pop('metodbeslut')
    assert Regelbas.model_validate(data).model_dump(mode='json')==data


def test_andrat_bundet_objekt_andrar_beslutsattesten(regelbas_v1):
    rb=regelbas_v1
    fore=granskningsobjekt(rb,'RP-RED-VG')['D1']
    t=rb.tjanster['T-RED-04'].model_copy(update={'beskrivning':'Syntetiskt ändrad omfattning'})
    ny=rb.model_copy(update={'tjanster':{**rb.tjanster,t.id:t}})
    assert granskningsobjekt(ny,'RP-RED-VG')['D1']!=fore
    assert any('D1' in x and 'T-RED-04' in x for x in validera(ny))


def test_andrad_modellfil_andrar_attest_och_stoppar(regelbas_v1,monkeypatch):
    from riskanalys.regelverk import metodbeslut as m
    rb=regelbas_v1;fore=granskningsobjekt(rb,'RP-RED-VG')['D1'];orig=m.for_fil
    monkeypatch.setattr(m,'for_fil',lambda p:'sha256:'+'0'*64 if p.name=='scenarier.py' else orig(p))
    assert granskningsobjekt(rb,'RP-RED-VG')['D1']!=fore
    assert any('D1' in x and 'scenarier.py' in x for x in validera(rb))


def test_loneavgransning_och_ideell_tf_only(regelbas_v1):
    rb=regelbas_v1
    assert not {'H-01','H-MOD-02'}&set(rb.tjanster['T-RED-04'].hot)
    assert {'H-02','H-TJ-04'}<=set(rb.tjanster['T-RED-04'].hot)
    assert rb.sarbarheter['S-ARB-05'].galler=='terrorfinansiering'
    assert all(not s.nivaeffekt for s in rb.lagre_risk.values())
