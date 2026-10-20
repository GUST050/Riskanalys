from datetime import date
import pytest
from riskanalys.analys.modeller import Analysbindning, Analyspaket, Tjansteanalys, Rutinatgard
from riskanalys.dokument.atgardsgrupper import Atgardsgrupp, gruppera_rutinatgarder


def paket(*poster):
    return Analyspaket(bindning=Analysbindning(**{k:'syntetisk' for k in ('byra','profilrevision','bedomningsmanifest','utkastmanifest','regelbas','kallunderlag','historik','modell')},bedomningsdatum=date(2026,10,19)),tjanster=tuple(Tjansteanalys(tjanst=f'T{i}',rutinatgarder=(p,)) for i,p in enumerate(poster)))


def test_atgardsrubrik_bevarar_tjanstevisa_skillnader():
    a=Rutinatgard(id='A1',atgard='Kontrollera',ansvar='Roll A',uppfoljning=date(2026,11,1))
    b=a.model_copy(update={'id':'A2','status':'genomford','ansvar':'Roll B','uppfoljning':date(2026,12,1)})
    assert gruppera_rutinatgarder(paket(a,b))==(Atgardsgrupp((('T0',a),('T1',b))),)
    with pytest.raises(ValueError): Atgardsgrupp(())


def test_tom_atgard_samordnas_inte():
    assert len(gruppera_rutinatgarder(paket(Rutinatgard(id='A'),Rutinatgard(id='B'))))==2


@pytest.mark.parametrize('andring',[{'atgard':' Kontrollera'},{'rutin_id':'R2'},{'rutin_version':'2'}])
def test_olika_ratext_eller_rutin_samordnas_inte(andring):
    a=Rutinatgard(id='A',atgard='Kontrollera')
    assert len(gruppera_rutinatgarder(paket(a,a.model_copy(update=andring))))==2
