"""Riktiga korta HTTP-gränsprov och frågekontrakt för alla länsvarianter."""
import pytest
from tester.intag.test_webb import webb,anrop
from tester.fixturer.m2 import DAG,komplett_profil


@pytest.mark.parametrize('lan,filial,paket',[('Västra Götaland',False,'RP-RED-VG'),('Skåne',False,'RP-RED-SKANE'),('Skåne',True,'RP-RED-STHLM')])
def test_lan_och_filial_valjer_paket_och_bevarar_fragetyper(webb,rb_intag,lan,filial,paket):
    from riskanalys.intag.fragor import fragor
    s,t=webb
    status,html,_=anrop(s,'skapa',dict(csrf=s.csrf,revision='',lan=lan,filial='ja' if filial else 'nej',datum=str(DAG),kalla='Syntetiskt',roll='Test'))
    assert status==200 and '<form' in html
    p=t.profil();assert p.byra.regelpaket==paket
    assert p.byra.lan==('Stockholm' if filial else lan)
    assert p.uppgifter['P-ORG.sateslan'].varde==lan
    assert p.uppgifter['P-ORG.utlandsk_filial'].varde==filial
    klar=komplett_profil(rb_intag,p)
    klar=klar.model_copy(update={'uppgifter':{**klar.uppgifter,**{k:p.uppgifter[k] for k in ('P-ORG.sateslan','P-ORG.utlandsk_filial')}}})
    fragelista=fragor(rb_intag,klar);ids=[q.falt.id for q in fragelista]
    assert len(ids)==len(set(ids)) and len(ids)>50
    assert all(not q.falt.alias_for and not q.falt.basfalt for q in fragelista)
    assert any(q.falt.periodkrav for q in fragelista)
    assert all(klar.uppgifter[q.falt.id].period is not None for q in fragelista if q.falt.periodkrav)
    assert 'P-KUND.antal_aktiva' in ids and 'P-KUND.andel_kontant' not in ids
