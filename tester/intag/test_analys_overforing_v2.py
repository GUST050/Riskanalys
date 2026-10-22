import pytest
from riskanalys.cli import main
from riskanalys.analys.tjanst import Analystjanst
from riskanalys.analys.lagring import las_analys,ANALYSFIL
from riskanalys.analys.provning import registersumma
from tester.intag.test_analys import analysmiljo,start
from tester.intag.conftest import rb_intag,tom,klar,intagsklocka
from tester.intag.test_webb import anrop


def test_cli_overforing_kraver_cas_och_jamforelse(capsys):
    assert main(['analys','finns-inte','--overfor-schema','2'])==1
    assert '--revision' in capsys.readouterr().err
    assert main(['analys','finns-inte','--overfor-schema','2','--revision','x'])==1
    assert '--jamfort' in capsys.readouterr().err
    with pytest.raises(SystemExit):main(['analys','finns-inte','--overfor-schema','2','--import','x.yaml'])


def test_overforing_i_webb_kraver_jamforelse_och_bevarar_original(analysmiljo):
    s,t=analysmiljo;start(s);p=las_analys(t.mapp);fore=(t.mapp/ANALYSFIL).read_bytes()
    kod,html,_=anrop(s,'analys?overfor=ja')
    assert kod==200 and 'Jämför schema 1 med schema 2' in html
    assert (t.mapp/ANALYSFIL).read_bytes()==fore
    data={'csrf':s.csrf,'revision':registersumma(p)}
    assert anrop(s,'analysoverfor',data)[0]==400
    assert (t.mapp/ANALYSFIL).read_bytes()==fore
    assert anrop(s,'analysoverfor',{**data,'jamfort':'ja'})[0]==200
    q=las_analys(t.mapp);assert q.schemaversion==2 and not q.beslut
    assert fore in [f.read_bytes() for f in (t.mapp/'analys/historik').glob('*.yaml')]
    assert anrop(s,'analysoverfor',{**data,'jamfort':'ja'})[0]==409
    assert las_analys(t.mapp)==q


@pytest.mark.parametrize('fel',['csrf','origin','extra'])
def test_overforingspost_med_fel_ar_utan_sidoeffekt(analysmiljo,fel):
    s,t=analysmiljo;start(s);p=las_analys(t.mapp)
    d={'csrf':s.csrf,'revision':registersumma(p),'jamfort':'ja'}
    if fel=='csrf':d['csrf']='fel'
    if fel=='extra':d['godkand']='ja'
    assert anrop(s,'analysoverfor',d,headers={'Origin':'https://example.invalid'} if fel=='origin' else None)[0] in (400,403)
    assert las_analys(t.mapp)==p


def test_cli_genomfor_uttrycklig_overforing_med_aktuell_revision(analysmiljo,capsys):
    s,t=analysmiljo;start(s);a=las_analys(t.mapp)
    assert main(['analys',t.mapp.name,'--overfor-schema','2','--jamfort','--revision',registersumma(a)])==0
    assert las_analys(t.mapp).schemaversion==2
    assert 'registersumma' in capsys.readouterr().out


def test_overforing_nekar_andrat_privat_belagg_utan_ny_sparning(analysmiljo,tmp_path):
    from riskanalys.fel import RiskanalysFel
    from tester.fixturer.m2 import DAG
    s,t=analysmiljo;start(s);at=Analystjanst(t.mapp,t.rb);a=las_analys(t.mapp)
    fil=tmp_path.resolve()/'privat.txt';fil.write_text('Syntetiskt originalunderlag')
    at.importera_belagg(fil,'syntetiskt:privat',DAG,registersumma(a));a=las_analys(t.mapp)
    ref=next(b for b in a.belagg if b.id=='syntetiskt:privat')
    (t.mapp/'analys/belagg'/ref.dokument).write_text('Ändrade syntetiska bytes')
    fore=(t.mapp/ANALYSFIL).read_bytes()
    with pytest.raises(RiskanalysFel):at.overfor(registersumma(a),True)
    assert (t.mapp/ANALYSFIL).read_bytes()==fore and las_analys(t.mapp).schemaversion==1
