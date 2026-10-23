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


def test_loneberedning_och_separat_bokforing_bedomer_egna_hot(regelbas_v1):
    from tester.fixturer.faktorer import faktorprofil
    from tester.fixturer.arb_kedja import bedom_kedja
    _,b=bedom_kedja(regelbas_v1,faktorprofil(regelbas_v1,(),alla_tjanster=True))
    ts={t.tjanst:t for t in b.tjanster}
    assert not {'H-01','H-MOD-02'}&{s.hot for s in ts['T-RED-04'].scenarier}
    assert {'H-01','H-MOD-02'}<={s.hot for s in ts['T-RED-01'].scenarier}
    assert 'H-02' in {s.hot for s in ts['T-RED-04'].scenarier}


def test_ideell_ensam_hojer_inte_pt_men_finns_i_tf(regelbas_v1):
    from tester.fixturer.faktorer import faktorprofil
    from tester.fixturer.arb_kedja import bedom_kedja
    _,b=bedom_kedja(regelbas_v1,faktorprofil(regelbas_v1,('S-ARB-05',),alla_tjanster=True))
    scenarios=[s for t in b.tjanster if t.erbjuds for s in t.scenarier]
    assert all('S-ARB-05' not in s.sarbarheter for s in scenarios if s.dimension=='pt')
    assert any('S-ARB-05' in s.sarbarheter for s in scenarios if s.dimension=='tf')


def test_pep_och_ideell_redovisas_utan_antaget_kundoverlapp(regelbas_v1):
    from tester.fixturer.faktorer import faktorprofil
    from tester.fixturer.arb_kedja import bedom_kedja
    profil=faktorprofil(regelbas_v1,('S-ARB-05','S-KUND-02'),alla_tjanster=True)
    _,b=bedom_kedja(regelbas_v1,profil)
    assert not profil.kombinationsgrupper
    assert any({'S-ARB-05','S-KUND-02'}<=set(s.sarbarheter) for t in b.tjanster for s in t.scenarier if s.dimension=='tf' and s.hot=='H-03')


def test_tf_har_allvarlig_konsekvens_utan_kontrollavdrag(regelbas_v1):
    from tester.fixturer.faktorer import faktorprofil
    from tester.fixturer.arb_kedja import bedom_kedja
    _,b=bedom_kedja(regelbas_v1,faktorprofil(regelbas_v1,(),alla_tjanster=True))
    tf=[s for t in b.tjanster for s in t.scenarier if s.dimension=='tf']
    assert tf and all(s.konsekvens=='allvarlig' and s.kvarstaende is None and not s.tackande_kontroller for s in tf)


def test_saknad_genomforandefil_kan_inte_godkannas(regelbas_v1):
    rb=regelbas_v1;b=rb.metodbeslut['D1'];f=dict(b.modellfiler);f.pop(next(iter(f)))
    ny=rb.model_copy(update={'metodbeslut':{**rb.metodbeslut,'D1':b.model_copy(update={'modellfiler':f})}})
    assert any('D1' in x and 'obligatoriska' in x for x in validera(ny))


def test_ny_mandatfixtur_skapa_bara_tjanstens_aktuella_hot(regelbas_v1,tmp_path):
    from tester.fixturer.rapportlasprov import bygg_rapportlasprov
    f=bygg_rapportlasprov(regelbas_v1,tmp_path,'med_betalningsmandat')
    for t in f.analys.tjanster:
        assert all(set(s.hot)<=set(regelbas_v1.tjanster[t.tjanst].hot) for s in t.scenarier)


@pytest.mark.parametrize('id,fil',[('D4','profil/kombinationer.py'),('D-LAGRE','dokument/faktorstatus_v10.py'),('D8','analys/provning.py')])
def test_transitiv_hjalpfil_ogiltigforklarar_beslut(regelbas_v1,monkeypatch,id,fil):
    from riskanalys.regelverk import metodbeslut as m
    rb=regelbas_v1;fore=granskningsobjekt(rb,'RP-RED-VG')[id];orig=m.for_fil
    monkeypatch.setattr(m,'for_fil',lambda p:'sha256:'+'0'*64 if p.as_posix().endswith(fil) else orig(p))
    assert granskningsobjekt(rb,'RP-RED-VG')[id]!=fore
    assert any(id+':' in x and fil in x for x in validera(rb))
