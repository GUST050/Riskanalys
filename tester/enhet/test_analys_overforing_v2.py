import pytest
from tester.conftest import regelbas_v1
from tester.enhet.test_analysschema_v2 import gammal_data
from riskanalys.analys.modeller import Analyspaket
from riskanalys.regelverk.modeller import hot_dimensioner


def test_overforing_ar_uttryckligt_forslag_och_bevarar_originalet(regelbas_v1):
    from riskanalys.analys.overforing import foresla_overforing
    p=Analyspaket.model_validate(gammal_data());fore=p.model_dump_json()
    q=foresla_overforing(regelbas_v1,p)
    assert p.model_dump_json()==fore and p.schemaversion==1
    assert q.schemaversion==2 and not q.beslut
    assert all(b.bekraftad_summa is None for t in q.tjanster for b in t.block)
    assert not any(x.bekraftad for t in q.tjanster for x in t.sarbarhetstillampningar)
    assert all(g.forfattare is None and g.status=='antagande' for g in q.gemensamma_sarbarhetsprovningar)
    assert all(t.sarbarhetsprovningar==next(a for a in p.tjanster if a.tjanst==t.tjanst).sarbarhetsprovningar for t in q.tjanster)
    assert all(t.forfattare==next(a for a in p.tjanster if a.tjanst==t.tjanst).forfattare for t in q.tjanster)


def test_identisk_text_med_olika_belagg_far_inte_slas_ihop(regelbas_v1):
    from riskanalys.analys.overforing import foresla_overforing
    p=Analyspaket.model_validate(gammal_data());a,b,*rest=p.tjanster
    rad=a.sarbarhetsprovningar[0];bela=tuple(x.id for x in p.belagg[:2])
    a=a.model_copy(update={'sarbarhetsprovningar':(rad.model_copy(update={'id':'a','belagg':bela[:1]}),)})
    b=b.model_copy(update={'sarbarhetsprovningar':(rad.model_copy(update={'id':'b','belagg':bela[1:]}),)})
    p=p.model_copy(update={'tjanster':(a,b)})
    q=foresla_overforing(regelbas_v1,p)
    # Det finns kvar två separata källsvar och ingen kandidat som förfalskar gemensamt belägg.
    assert q.tjanster[0].sarbarhetsprovningar[0].belagg!=q.tjanster[1].sarbarhetsprovningar[0].belagg
    assert not any(g.beskrivning==rad.motivering for g in q.gemensamma_sarbarhetsprovningar)


def test_identiska_svar_med_skild_relevans_far_inte_slas_ihop(regelbas_v1):
    from riskanalys.analys.overforing import foresla_overforing
    p=Analyspaket.model_validate(gammal_data());a,b,*_=p.tjanster;rad=a.sarbarhetsprovningar[0]
    a=a.model_copy(update={'sarbarhetsprovningar':(rad,)})
    b=b.model_copy(update={'sarbarhetsprovningar':(rad.model_copy(update={'id':'annan','relevans':'ej_relevant'}),)})
    q=foresla_overforing(regelbas_v1,p.model_copy(update={'tjanster':(a,b)}))
    assert not any(g.beskrivning==rad.motivering for g in q.gemensamma_sarbarhetsprovningar)


def tva_lika(p):
    from riskanalys.analys.modeller import Scenarioanalys
    a,b,*_=p.tjanster
    scenario=Scenarioanalys(id='lokal:overforingsprov',hot=('H-03',),rubrik='Syntetiskt gemensamt hot',
        handelseforlopp='Samma underlag kan dölja affärens verkliga ändamål.',relevans='relevant',motivering='Samma syntetiska mekanism',belagg=(p.belagg[0].id,))
    ts=[]
    for i,t in enumerate((a,b)):
        lokal=scenario.model_copy(update={'id':t.tjanst+':overforingsprov'})
        rad=a.sarbarhetsprovningar[0].model_copy(update={'id':'gammal:'+str(i),'omrade':'kund','scenarier':(lokal.id,),
            'motivering':'Helt identisk syntetisk prövning','belagg':(p.belagg[0].id,)})
        ts.append(t.model_copy(update={'sarbarhetsprovningar':(rad,),'scenarier':(*t.scenarier,lokal)}))
    q=p.model_copy(update={'tjanster':tuple(ts)})
    return Analyspaket.model_validate(q.model_dump(mode='json'))


def test_semantiskt_identiska_svar_blir_en_obekraftad_kandidat(regelbas_v1):
    from riskanalys.analys.overforing import foresla_overforing
    p=tva_lika(Analyspaket.model_validate(gammal_data()));q=foresla_overforing(regelbas_v1,p)
    kandidater=[g for g in q.gemensamma_sarbarhetsprovningar if g.beskrivning=='Helt identisk syntetisk prövning']
    assert len(kandidater)==1 and kandidater[0].hot==('H-03',)
    assert kandidater[0].forfattare is None and kandidater[0].status=='antagande'
    assert all(not x.bekraftad for t in q.tjanster for x in t.sarbarhetstillampningar)


@pytest.mark.parametrize('skillnad',['period','dimension','lokalt_innehall'])
def test_skiljda_perioder_hotdimensioner_och_lokala_svar_slas_inte_ihop(regelbas_v1,skillnad):
    from riskanalys.analys.overforing import foresla_overforing
    p=tva_lika(Analyspaket.model_validate(gammal_data()));a,b=p.tjanster;s=b.sarbarhetsprovningar[0]
    if skillnad=='period':
        from riskanalys.profil.modeller import Period
        from datetime import date
        e=p.belagg[0].model_copy(update={'id':'annan-period','period':Period(fran=date(2025,1,1),till=date(2025,9,30))})
        p=p.model_copy(update={'belagg':(*p.belagg,e)})
        s=s.model_copy(update={'belagg':(e.id,)})
    elif skillnad=='dimension':
        scenario=p.gemensamma_scenarier[-1].model_copy(update={'id':'lokal:annan-dimension','hot':(next(h.id for h in regelbas_v1.hot.values() if 'tf' in hot_dimensioner(h) and h.id!='H-03'),)})
        b=b.model_copy(update={'scenarier':(*b.scenarier,scenario)})
        s=s.model_copy(update={'scenarier':(scenario.id,)})
    else:s=s.model_copy(update={'motivering':'Samma syntetiska kundförhållande berör uttryckligen inte denna tjänst.'})
    p=p.model_copy(update={'tjanster':(a,b.model_copy(update={'sarbarhetsprovningar':(s,)}))})
    q=foresla_overforing(regelbas_v1,p)
    assert not any(g.beskrivning=='Helt identisk syntetisk prövning' for g in q.gemensamma_sarbarhetsprovningar)
    assert q.tjanster[0].sarbarhetsprovningar==a.sarbarhetsprovningar
    assert q.tjanster[1].sarbarhetsprovningar==(s,)
