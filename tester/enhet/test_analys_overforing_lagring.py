import pytest
from tester.conftest import regelbas_v1
from tester.enhet.test_analysschema_v2 import gammal_data
from riskanalys.analys import lagring as l,modeller as m
from riskanalys.analys.provning import registersumma,underlagssumma,svarssumma
from riskanalys.fel import RiskanalysFel


def sparat(tmp_path):
    p=m.Analyspaket.model_validate(gammal_data());l.spara_analys(tmp_path,p,forvantad_summa='')
    return l.las_analys(tmp_path)


def test_overforing_bevarar_exakta_originalbytes_och_hojer_revision(tmp_path):
    p=sparat(tmp_path);fore=(tmp_path/l.ANALYSFIL).read_bytes()
    q=p.model_copy(update={'schemaversion':2,'beslut':()})
    with l.analyslas(tmp_path):l.spara_overforing_last(tmp_path,q,forvantad_summa=registersumma(p))
    nytt=l.las_analys(tmp_path)
    assert nytt.schemaversion==2 and nytt.revision==p.revision+1 and not nytt.beslut
    assert fore in [f.read_bytes() for f in (tmp_path/'analys/historik').glob('*.yaml')]
    with l.analyslas(tmp_path),pytest.raises(RiskanalysFel):l.spara_overforing_last(tmp_path,q,forvantad_summa=registersumma(nytt))


def test_overforing_med_beslut_eller_gammal_flik_sparar_inget(tmp_path):
    p=sparat(tmp_path);fore=(tmp_path/l.ANALYSFIL).read_bytes()
    b=m.Analysbeslut(tjanst=p.tjanster[0].tjanst,revision=p.revision,underlagssumma=underlagssumma(p),svarssumma=svarssumma(p),
        namn='Syntetisk',roll='FfR',godkand=True,datum=p.bindning.bedomningsdatum)
    for q,cas in ((p.model_copy(update={'schemaversion':2,'beslut':(b,)}),registersumma(p)),(p.model_copy(update={'schemaversion':2}),'')):
        with l.analyslas(tmp_path),pytest.raises(RiskanalysFel):l.spara_overforing_last(tmp_path,q,forvantad_summa=cas)
        assert (tmp_path/l.ANALYSFIL).read_bytes()==fore


def test_avbrott_i_overforing_bevarar_original_och_historikkopia(tmp_path,monkeypatch):
    p=sparat(tmp_path);fore=(tmp_path/l.ANALYSFIL).read_bytes()
    def avbrott(*args,**kwargs):raise OSError('syntetiskt avbrott före publicering')
    monkeypatch.setattr(l,'_atomiskt',avbrott)
    with pytest.raises(RiskanalysFel):
        with l.analyslas(tmp_path):l.spara_overforing_last(tmp_path,p.model_copy(update={'schemaversion':2}),forvantad_summa=registersumma(p))
    assert (tmp_path/l.ANALYSFIL).read_bytes()==fore
    assert fore in [f.read_bytes() for f in (tmp_path/'analys/historik').glob('*.yaml')]
