import pytest
from tester.fixturer.m2 import DAG, PERIOD
from riskanalys.fel import RiskanalysFel
from riskanalys.profil.modeller import Uppgift
from riskanalys.intag.fragor import fragor
from riskanalys.intag.tackning import tackning
from riskanalys.intag.svar import besvara
from riskanalys.intag.modeller import IntagSvar


def svar(id, text, **kw):
    return IntagSvar(falt=id, text=text, kalla='Syntetisk källa', datum=DAG, **kw)


def test_aktivering_fore_foljdfraga_och_inga_dubbletter(rb_intag, tom):
    ids=[q.falt.id for q in fragor(rb_intag,tom)]
    assert 'P-TJ.red01_erbjuds' in ids
    assert 'P-TJ.red01_arbetssatt' not in ids
    assert not any(rb_intag.falt[i].alias_for or rb_intag.falt[i].basfalt for i in ids)
    p=besvara(rb_intag,tom,svar('P-TJ.red01_erbjuds','ja'))
    assert 'P-TJ.red01_arbetssatt' in [q.falt.id for q in fragor(rb_intag,p)]
    p=besvara(rb_intag,p,svar('P-TJ.red01_erbjuds','nej'))
    assert 'P-TJ.red01_arbetssatt' not in [q.falt.id for q in fragor(rb_intag,p)]


def test_tackning_kraver_beskrivning_och_belagg(rb_intag,klar):
    assert tackning(rb_intag,klar).komplett
    for id in ('P-BESK.verksamhet','P-TJ.red01_arbetssatt'):
        p=klar.model_copy(update={'uppgifter':{**klar.uppgifter,id:Uppgift()}})
        t=tackning(rb_intag,p)
        assert not t.komplett and id in t.saknade
    u=klar.uppgifter['P-BESK.verksamhet'].model_copy(update={'kalla':' '})
    assert not tackning(rb_intag,klar.model_copy(update={'uppgifter':{**klar.uppgifter,'P-BESK.verksamhet':u}})).komplett


@pytest.mark.parametrize('kw', [{'text':''},{'kalla':''},{'status':'ej_tillämplig','motivering':'jag vill inte svara'}])
def test_ogiltigt_eller_ej_tillampligt_aktivt_svar(rb_intag,tom,kw):
    data=dict(falt='P-ORG.namn',text='Test',kalla='Test',datum=DAG);data.update(kw)
    with pytest.raises(RiskanalysFel):besvara(rb_intag,tom,IntagSvar(**data))


def test_andring_ogiltigforklarar_belagda_beroenden(rb_intag,klar):
    p=besvara(rb_intag,klar,svar('P-TJ.red01_erbjuds','nej'))
    assert p.uppgifter['P-TJ.red01_arbetssatt'].inaktuell
    assert p.uppgifter['P-TJ.red01_arbetssatt'].kalla == klar.uppgifter['P-TJ.red01_arbetssatt'].kalla
    p=besvara(rb_intag,p,svar('P-TJ.red01_erbjuds','ja'))
    assert 'P-TJ.red01_arbetssatt' in tackning(rb_intag,p).saknade


def test_periodbyte_kraver_nya_antal(rb_intag,klar):
    from riskanalys.profil.modeller import Period
    from datetime import date
    p=besvara(rb_intag,klar,svar('P-KUND.antal_aktiva','100',period=Period(fran=date(2025,1,1),till=date(2025,9,30))))
    assert p.uppgifter['P-KUND.antal_kontant'].inaktuell


def test_okant_sparas_men_ar_aldrig_klart(rb_intag,tom):
    p=besvara(rb_intag,tom,svar('P-ORG.namn','',status='okänt',motivering='Kontrolleras senare'))
    assert p.uppgifter['P-ORG.namn'].status == 'föreslagen'
    assert 'P-ORG.namn' in tackning(rb_intag,p).saknade


def test_ovriga_riskforhallanden_stoppar_automatisk_fullstandighet(rb_intag,klar):
    p=besvara(rb_intag,klar,svar('P-BESK.ovriga_forhallanden','ja'))
    assert not tackning(rb_intag,p).komplett
    assert any('riskmodellen' in h for h in tackning(rb_intag,p).hinder)


def test_andrad_kontroll_ateranvander_inte_gamla_belagg(rb_intag,klar):
    id='P-KONTROLL.C-TJ-01.utformning'
    p=besvara(rb_intag,klar,svar(id,'saknas'))
    p=besvara(rb_intag,p,svar(id,'finns'))
    assert p.uppgifter['P-KONTROLL.C-TJ-01.genomforande'].inaktuell
    assert p.uppgifter['P-KONTROLL.C-TJ-01.belagg'].inaktuell
    assert not tackning(rb_intag,p).komplett


def test_geografibyte_omprovar_tjansternas_underlag(rb_intag,klar):
    p=besvara(rb_intag,klar,svar('P-BESK.geografi','Nya utlandsmarknader och nya ägarländer'))
    assert p.uppgifter['P-TJ.red01_geografi'].inaktuell
    assert not tackning(rb_intag,p).komplett


def test_fragornas_ordning_respekterar_belaggsberoenden(rb_intag,klar):
    ids=[q.falt.id for q in fragor(rb_intag,klar)]
    assert ids.index('P-TJ.red01_arbetssatt') < ids.index('P-KONTROLL.C-TJ-01.utformning')
    assert ids.index('P-KONTROLL.C-TJ-01.utformning') < ids.index('P-KONTROLL.C-TJ-01.genomforande')


def test_aldre_aliasprofil_kan_rattas_utan_osynlig_konflikt(rb_intag,klar):
    id='P-TJ.red01_erbjuds';alias='P-TJ.T-RED-01.erbjuds'
    upp={**klar.uppgifter,alias:klar.uppgifter[id],id:Uppgift()}
    gammal=klar.model_copy(update={'uppgifter':upp})
    p=besvara(rb_intag,gammal,svar(id,'nej'))
    from riskanalys.profil.omfattning import omfattningsbrister
    assert not any('motstridiga' in h for h in omfattningsbrister(p,rb_intag))
    assert p.uppgifter[alias].inaktuell or p.uppgifter[alias].varde is False


@pytest.mark.parametrize('andring',['framtida_period','noll_personer','framtida_bekraftelse'])
def test_handandrad_profil_kan_inte_kringga_intagsregler(rb_intag,klar,andring):
    from datetime import date,timedelta
    from riskanalys.profil.modeller import Period
    from riskanalys.profil.omfattning import harled_andelar
    upp=dict(klar.uppgifter)
    if andring=='framtida_period':
        upp={k:u.model_copy(update={'period':Period(fran=date(2027,1,1),till=date(2027,9,30))}) if u.period else u for k,u in upp.items()}
    elif andring=='noll_personer':upp['P-ORG.antal_anstallda']=upp['P-ORG.antal_anstallda'].model_copy(update={'varde':0})
    else:upp['P-ORG.namn']=upp['P-ORG.namn'].model_copy(update={'datum':DAG+timedelta(days=1)})
    p=harled_andelar(klar.model_copy(update={'uppgifter':upp}),rb_intag)
    assert not tackning(rb_intag,p).komplett


def test_intaget_kraver_fakta_men_inte_att_anvandaren_skriver_riskanalysen(rb_intag,klar):
    p=klar.model_copy(update={'uppgifter':{k:v for k,v in klar.uppgifter.items() if not k.endswith('_sektorsmotivering')}})
    assert tackning(rb_intag,p).komplett
    assert all(not f.intag.obligatorisk for f in rb_intag.falt.values() if f.id.endswith('_sektorsmotivering'))


def test_gammal_sektorsmotivering_kan_inte_godtas_efter_andrade_fakta(rb_intag,klar):
    from riskanalys.bedomning.korning import bedom
    from riskanalys.granskning.kontroller import sektorsfynd
    from riskanalys.profil.hantering import visa_varde
    p=besvara(rb_intag,klar,svar('P-BESK.geografi','Nya syntetiska faktiska geografiska förhållanden'))
    for q in fragor(rb_intag,p):
        if q.falt.intag.obligatorisk and not q.besvarad:
            u=p.uppgifter[q.falt.id]
            p=besvara(rb_intag,p,svar(q.falt.id,visa_varde(q.falt,u.varde),period=u.period))
    assert tackning(rb_intag,p).komplett
    assert p.uppgifter['P-TJ.red01_sektorsmotivering'].inaktuell
    from riskanalys.regelverk.urval import valj
    b=bedom(rb_intag,valj(rb_intag,p.byra.regelpaket,p.byra.datum,p.byra.lan),p)
    assert any(f['regel']=='B-13' for f in sektorsfynd(rb_intag,b,p))
