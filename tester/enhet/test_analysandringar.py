"""Blockkommandon får bara ändra det namngivna blocket under revisionsskydd."""
from dataclasses import replace
import pytest
from riskanalys.fel import RiskanalysFel
from tester.enhet.test_analysguide import paket


def test_typad_andring_innehaller_bara_blockets_svar():
    from riskanalys.intag.analysformular import las_blockandring
    from riskanalys.analys.andringar import tillampa_block
    p = paket()
    c = las_blockandring(p, 'T-0', 13, {'csrf':'hemlig', 'revision':'r', 'forfattare':'Ada', 'pt_motivering':'Lokal PT'}, revision='r')
    assert c.revision == 'r' and c.tjanst == 'T-0'
    assert dict(c.varden) == {'pt_motivering': 'Lokal PT'}
    nytt = tillampa_block(p, c)
    assert nytt.tjanster[0].pt_motivering == 'Lokal PT'
    assert nytt.tjanster[0].tf_motivering == ''
    assert not nytt.tjanster[0].block[12].bekraftad_summa


def test_manipulerad_delta_far_inte_andra_ett_annat_block():
    from riskanalys.intag.analysformular import las_blockandring
    from riskanalys.analys.andringar import tillampa_block
    c = las_blockandring(paket(), 'T-0', 13, {'forfattare':'Ada'}, revision='r')
    with pytest.raises(RiskanalysFel, match='block'):
        tillampa_block(paket(), replace(c, varden=(('tf_motivering', 'Smyg'),)))


def test_andrad_radidentitet_avvisas_aven_for_typad_konsument():
    from riskanalys.intag.analysformular import las_blockandring
    from riskanalys.analys.andringar import tillampa_block
    p = paket()
    c = las_blockandring(p, 'T-0', 6, {'forfattare':'Ada'}, revision='r')
    s = p.tjanster[0].scenarier[0].model_copy(update={'id':'smyg'})
    with pytest.raises(RiskanalysFel, match='rad-ID'):
        tillampa_block(p, replace(c, varden=(('scenarier',(s,)),)))


def test_bekraftelse_kraver_det_visade_blockets_summa():
    from riskanalys.intag.analysformular import las_blockandring
    from riskanalys.analys.andringar import tillampa_block
    p = paket()
    c = las_blockandring(p, 'T-0', 13, {'forfattare':'Ada'}, revision='r')
    with pytest.raises(RiskanalysFel, match='ändrats'):
        tillampa_block(p, replace(c, operation='bekrafta', visad_summa='fel'))


def _samtidig_blockskrivning(rot, andring, start, svar):
    from types import SimpleNamespace
    from riskanalys.analys.tjanst import Analystjanst
    class LokalTjanst(Analystjanst):
        # Isolerar underlagets dyra dokumentuppbyggnad; lås, CAS, delta,
        # domänkontroller och lagring är verkliga.
        def _underlag(self, version=2):
            return None,None,paket().bindning
    rb=SimpleNamespace(falt={},hot={},sarbarheter={},kontroller={},
        tjanster={f'T-{n}':SimpleNamespace(hot=(),kontroller=()) for n in range(4)})
    try:
        start.wait(timeout=10)
        LokalTjanst(rot,rb).spara_block(andring)
        svar.put('sparat')
    except RiskanalysFel as exc:
        svar.put('inaktuellt' if 'annan flik' in str(exc) else str(exc))


def test_tva_processer_med_samma_revision_far_en_vinnare(tmp_path):
    import multiprocessing
    from riskanalys.analys import lagring as l, provning as p
    from riskanalys.intag.analysformular import las_blockandring
    l.spara_analys(tmp_path,paket(),forvantad_summa='')
    sparat=l.las_analys(tmp_path)
    ctx=multiprocessing.get_context('fork')
    start=ctx.Barrier(2)
    svar=ctx.Queue()
    processer=[]
    for text in ('Första svaret','Andra svaret'):
        c=las_blockandring(sparat,'T-0',13,{'forfattare':'Ada','pt_motivering':text},revision=p.registersumma(sparat))
        q=ctx.Process(target=_samtidig_blockskrivning,args=(tmp_path,c,start,svar))
        q.start();processer.append(q)
    try:
        for q in processer:
            q.join(timeout=20)
            assert q.exitcode==0
        assert sorted(svar.get(timeout=2) for _ in processer)==['inaktuellt','sparat']
        assert l.las_analys(tmp_path).revision==2
    finally:
        for q in processer:
            if q.is_alive():q.terminate();q.join()
        svar.close()


@pytest.mark.parametrize('nummer',[10,11,12])
@pytest.mark.parametrize('fall',['befintlig','ny','redigerad','bekrafta'])
def test_kontrollrader_har_sammansatt_identitet(nummer,fall):
    from riskanalys.analys.modeller import Kontrollprovning, Scenarioanalys
    from riskanalys.analys import provning as p
    from riskanalys.analys.andringar import tillampa_block
    from riskanalys.intag.analysformular import las_blockandring
    q=paket();a=q.tjanster[0]
    a=a.model_copy(update={'kontroller':() if fall=='ny' else (Kontrollprovning(scenario='lokal-0',kontroll='K-1'),),
        'scenarier':(*a.scenarier,Scenarioanalys(id='annan'))})
    q=q.model_copy(update={'tjanster':(a,*q.tjanster[1:])})
    data={'forfattare':'Ada'}
    if fall in ('ny','redigerad'):
        data.update({'kontroller.0.anvand':'ja','kontroller.0.scenario':'annan','kontroller.0.kontroll':'K-2'})
    if fall=='bekrafta':data.update(operation='bekrafta',visad_summa=p.blocksumma(q,'T-0',nummer))
    c=las_blockandring(q,'T-0',nummer,data,revision='r')
    nytt=tillampa_block(q,c)
    k=nytt.tjanster[0].kontroller
    assert len(k)==1
    assert (k[0].scenario,k[0].kontroll)==(('annan','K-2') if fall in ('ny','redigerad') else ('lokal-0','K-1'))
    if fall=='bekrafta':
        assert nytt.tjanster[0].block[nummer-1].bekraftad_summa==p.blocksumma(nytt,'T-0',nummer)


def test_typat_kommando_avvisar_dubblerade_belaggsreferenser():
    from datetime import date
    from riskanalys.analys.modeller import Analysbelagg
    from riskanalys.analys.andringar import tillampa_block
    from riskanalys.intag.analysformular import las_blockandring
    q=paket().model_copy(update={'belagg':(Analysbelagg(id='B-1',profilfalt=('P-X',),datum=date(2026,10,24)),)})
    c=las_blockandring(q,'T-0',1,{'forfattare':'Ada'},revision='r')
    vals=dict(c.varden);vals['exponeringsbelagg']=('B-1','B-1')
    with pytest.raises(RiskanalysFel,match='unika'):
        tillampa_block(q,replace(c,varden=tuple(vals.items())))


from tester.fixturer.resultatkedja import resultatkedja_bas, resultatkedja


@pytest.mark.parametrize('nummer',[10,11,12])
def test_cli_bekraftar_befintliga_kontroller_utan_att_kora_ai(resultatkedja,monkeypatch,nummer):
    from riskanalys.cli import main
    from riskanalys.analys import lagring as l, provning as p
    k=resultatkedja;f=k.fall
    monkeypatch.setenv('RISKANALYS_DATA',str(f.byramapp.parent))
    q=l.las_analys(f.byramapp)
    a=next(t for t in q.tjanster if t.kontroller)
    skrivningar=set((f.byramapp/'utkast').iterdir())
    assert main(['analys',f.byramapp.name,'--regelbas',str(k.regelrot),'--bekrafta-block',str(nummer),
        '--tjanst',a.tjanst,'--forfattare',a.forfattare,'--revision',p.registersumma(q),
        '--visad-summa',p.blocksumma(q,a.tjanst,nummer)])==0
    nytt=l.las_analys(f.byramapp)
    b=next(t for t in nytt.tjanster if t.tjanst==a.tjanst)
    assert b.kontroller==a.kontroller
    assert next(x for x in b.block if x.nummer==nummer).bekraftad_summa==p.blocksumma(nytt,a.tjanst,nummer)
    assert set((f.byramapp/'utkast').iterdir())==skrivningar


def _med_aldre_dubbelt_belagg(nummer):
    from datetime import date
    from riskanalys.analys.modeller import Analysbelagg, Analysgap
    q=paket();a=q.tjanster[0]
    refs=('B-1','B-1')
    v={'exponeringsbelagg':refs} if nummer==1 else {
        'gap':(Analysgap(id='aldre',typ='kunskapslucka',belagg=refs),)}
    return q.model_copy(update={
        'belagg':(Analysbelagg(id='B-1',profilfalt=('P-X',),datum=date(2026,10,24)),),
        'tjanster':(a.model_copy(update=v),*q.tjanster[1:])})


@pytest.mark.parametrize('nummer',[1,16])
def test_oforandrade_aldre_referenser_bevaras_vid_bekraftelse(nummer):
    from riskanalys.analys.andringar import tillampa_block
    from riskanalys.analys.provning import BLOCKFALT,blocksumma
    from riskanalys.intag.analysformular import las_blockandring
    q=_med_aldre_dubbelt_belagg(nummer)
    c=las_blockandring(q,'T-0',nummer,{'operation':'bekrafta','forfattare':'Ada',
        'visad_summa':blocksumma(q,'T-0',nummer)},revision='r')
    nytt=tillampa_block(q,c)
    assert all(getattr(nytt.tjanster[0],f)==getattr(q.tjanster[0],f) for f in BLOCKFALT[nummer])
    assert nytt.tjanster[0].block[nummer-1].bekraftad_summa==blocksumma(nytt,'T-0',nummer)


def test_aldre_dubbla_referenser_far_inte_kopieras_till_ny_rad():
    from riskanalys.analys.andringar import tillampa_block
    from riskanalys.intag.analysformular import las_blockandring
    q=_med_aldre_dubbelt_belagg(16)
    c=las_blockandring(q,'T-0',16,{'forfattare':'Ada'},revision='r')
    vals=dict(c.varden);vals['gap']=(q.tjanster[0].gap[0].model_copy(update={'id':'ny'}),)
    c=replace(c,varden=tuple(vals.items()),nya_rader=(('gap','ny'),),borttagna_rader=(('gap','aldre'),))
    with pytest.raises(RiskanalysFel,match='unika'):
        tillampa_block(q,c)
