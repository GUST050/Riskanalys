"""Verkliga CLI-val och attestbindning mot en isolerad syntetisk kedja."""
from pathlib import Path
import shutil
from tester.fixturer.resultatkedja import resultatkedja_bas,resultatkedja,DAG


def test_cli_ny_standard_och_samlad_granskning(resultatkedja,tmp_path,monkeypatch,capsys):
    from riskanalys.cli import main
    from riskanalys.granskning.korning import las_granskning
    from riskanalys.lagring.korningar import senaste_korning
    from riskanalys.faststallelse.sakgranskning import las_sakgranskningar,spara_sakgranskningar
    from riskanalys.dokument.leverantor import Testleverantor
    def forbjudet(*a,**kw):raise AssertionError('Formatbyte får inte skriva ny AI-text')
    monkeypatch.setattr(Testleverantor,'skriv_del',forbjudet)
    k=resultatkedja;data=tmp_path/'data';byra=data/k.fall.profil.byra.id
    shutil.copytree(k.fall.byramapp,byra);monkeypatch.setenv('RISKANALYS_DATA',str(data))
    grund=[byra.name,'--regelbas',str(k.regelrot),'--datum',DAG.isoformat()]
    assert main(['granska',*grund])==0
    gm=senaste_korning(byra,'granskning','granska')
    d,_=las_granskning(gm);assert d.formatversion=='D-ARB-resultat-v9'
    spara_sakgranskningar(byra,())
    assert main(['sakgranska',*grund,'--resultatrapport'])==0
    visat=capsys.readouterr().out
    summa=next(x.removeprefix('Visad struktursumma: ') for x in visat.splitlines() if x.startswith('Visad struktursumma: '))
    assert 'Resultatrapport, analysbilaga och underlagsbilaga' in visat
    assert 'Läsrapport och kompletterande underlagsbilaga' not in visat
    assert all(a.id in visat for a in d.avsnitt if a.leveransdel=='resultatrapport')
    assert main(['sakgranska',*grund,'--resultatrapport','--godkann','--namn','Syntetisk',
                 '--visad-struktursumma','fel'])==1
    assert las_sakgranskningar(byra)==()
    assert main(['sakgranska',*grund,'--resultatrapport','--godkann','--namn','Syntetisk',
                 '--visad-struktursumma',summa])==0
    assert tuple(p.avsnitt for p in las_sakgranskningar(byra))==tuple(a.id for a in d.avsnitt if a.leveransdel=='resultatrapport')
    assert main(['granska',*grund,'--rapportformat','v8'])==0
    d8,_=las_granskning(senaste_korning(byra,'granskning','granska'))
    assert d8.formatversion=='D-ARB-tjanst-v8'
