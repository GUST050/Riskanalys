import pytest
from tester.conftest import regelbas_v1
from tester.enhet.test_arb_v8 import v8fall,bygg,texter
from riskanalys.analys.gemensam import forifyll_gemensamt,postsumma,effektiv_tjanst
from riskanalys.analys import modeller as m
from dataclasses import replace


@pytest.mark.parametrize('slag,falt',[('leverantorer','leverantorsmotivering'),('erfarenhet','erfarenhetsprovning'),('sanktionsanknytning','sanktioner')])
def test_annorlunda_verksamhet_bevarar_tjanstens_egna_svar_och_rapport(v8fall,slag,falt):
    f,r=v8fall;p=forifyll_gemensamt(f.regelbas,f.analys);a=p.tjanster[0]
    g=next(g for g in p.gemensamma_verksamhetsposter if g.slag==slag).model_copy(update={
        'text':'Gemensamt syntetiskt normalsvar som inte gäller oförändrat här.','status':'bekraftad','forfattare':'Syntetisk gemensam',
        'belagg':(p.belagg[0].id,)})
    lokal='Unikt lokalt verksamhetssvar som måste fortsätta användas efter avvikelsen.'
    a=a.model_copy(update={falt:lokal,'verksamhetstillampningar':(m.GemensamTillampning(post=g.id,postsumma=postsumma(g),
        stallningstagande='galler_annorlunda',bekraftad=True,motivering='Lokala arbetsmoment och belägg motiverar ett annat genomförande.',belagg=g.belagg),)})
    p=p.model_copy(update={'gemensamma_verksamhetsposter':(g,),'tjanster':(a,*p.tjanster[1:])})
    effektiv=effektiv_tjanst(p,a.tjanst)
    assert lokal in getattr(effektiv,falt)
    if slag=='leverantorer':assert effektiv.leverantorer==a.leverantorer
    d=bygg(replace(f,analys=p),r)
    av=d.avsnitt_med_id()['D-ARB.6.1']
    assert lokal in texter(av)
