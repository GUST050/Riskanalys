"""H6:s gränser prövas mot faktiska svar, inte bara konstanter."""
import pytest
from riskanalys.dokument.delvalidering import validera_del
from riskanalys.dokument.modeller import AISvar, AIStycke


@pytest.mark.parametrize('del_id,lagst,hogst', [
    ('hot',80,160),('sarbarheter',100,220),('kontroller',60,120),
    ('risknivaer',80,120),('slutsatser',80,130)])
@pytest.mark.parametrize('grans', ['min-1','min','max','max+1'])
def test_h6_langdgrans(del_id, lagst, hogst, grans, faktablad_exempel):
    antal = {'min-1':lagst-1,'min':lagst,'max':hogst,'max+1':hogst+1}[grans]
    text = ' '.join(['underlag'] * antal)
    svar = AISvar(stycken=[AIStycke(typ='motivering',referenser=['H-01','H-02','P-KUND.antal_aktiva'],text=text)],oklarheter=[])
    fel = validera_del(del_id,svar,faktablad_exempel,(),())
    assert bool([f for f in fel if 'ord;' in f]) is (grans in ('min-1','max+1'))


@pytest.mark.parametrize('text', [
    'Därför är risknivån motiverad av kundernas verksamhet.',
    'Risknivån avviker från sektorns nivå eftersom kunderna har annan verksamhet.',
])
def test_riskdelen_far_inte_motivera_motorutfall(text,faktablad_exempel):
    svar=AISvar(stycken=[AIStycke(typ='motivering',referenser=['H-01','P-KUND.antal_aktiva'],text=text+' underlag'*85)],oklarheter=[])
    assert any('motorutfall' in f for f in validera_del('risknivaer',svar,faktablad_exempel,(),()))


def test_villkorligt_samband_godtas_utan_nivamotivering(faktablad_exempel):
    text = ('Om kunden använder osanna fakturor kan bristande underlag försvåra granskningen. '
            'Sambandet måste prövas lokalt mot dokumenterade affärshändelser. ' + 'underlag ' * 65)
    svar = AISvar(stycken=[AIStycke(typ='motivering',referenser=['H-01','P-KUND.antal_aktiva'],text=text)],oklarheter=[])
    assert validera_del('risknivaer',svar,faktablad_exempel,(),()) == []
