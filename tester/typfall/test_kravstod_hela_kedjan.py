"""Underlag → rapport/bindning, med uttryckligt oförändrad numerisk metod."""
from datetime import date
from dataclasses import replace
import pytest
from tester.fixturer.kravstod import gruppvariant, planerad_tjanst
from tester.enhet.test_arb_v8 import v8fall, bygg
from tester.typfall.test_analys_hela_kedjan import positiv_bas, positiv


def test_samtidig_atskild_och_okand_grupp_ger_skilda_spar_samma_motor(v8fall):
    from riskanalys.bedomning.motor import bedom
    from riskanalys.profil.kombinationer import kombinationsbrister
    from riskanalys.profil.lagring import profilrevision
    from riskanalys.regelverk.urval import valj
    f,r=v8fall
    texter=[]; revisioner=[]
    for variant in ('samtidig','atskild','okand'):
        p=gruppvariant(f.regelbas,f.profil,variant)
        assert not kombinationsbrister(f.regelbas,p)
        b=bedom(f.regelbas,valj(f.regelbas,p.byra.regelpaket,p.byra.datum,p.byra.lan),p)
        assert b == f.bedomning
        revisioner.append(profilrevision(p))
        d=bygg(replace(f,profil=p,bedomning=b),r)
        texter.append(' '.join(s.text for a in d.avsnitt for s in a.stycken if any(ref.startswith('LOKAL-GRUPP:') for ref in s.referenser)))
    assert len(set(revisioner))==len(set(texter))==3
    assert 'Antal 8, bas 100' in texter[0]
    assert 'belagt åtskild' in texter[1]
    assert 'okänt aktuellt antal' in texter[2]


def test_planutvardering_andrar_historikbindningen_och_kraver_fornyelse_av_alla_beslut(positiv):
    from riskanalys.analys import lagring as l, provning as p
    from riskanalys.analys.tjanst import Analystjanst
    from riskanalys.drift.historik import Handelse, registrera_handelse, las_historik
    from riskanalys.fel import RiskanalysFel
    from riskanalys.profil.modeller import Tjansteplan
    from riskanalys.profil.planering import plansumma
    from riskanalys.profil.lagring import las_profil
    k=positiv;f=k.fall
    gammal=l.las_analys(f.byramapp)
    assert len(gammal.beslut)==4
    # Planen representeras här separat för att isolera historikhändelsens effekt:
    # ingen profilsparning och ingen ny numerisk beräkning görs i denna kontrast.
    plan=Tjansteplan(id='ny_marknad',tjanst='T-RED-01',typ='ny_marknad',beskrivning='Syntetiskt utvärderad marknad')
    profil=las_profil(f.byramapp).model_copy(update={'tjansteplaner':(plan,)})
    fore=l.bygg_bindning(f.byramapp,f.regelbas,k.bedomningsmapp,k.utkastmapp)
    frist=las_historik(f.byramapp).nasta_genomgang()
    registrera_handelse(f.byramapp,Handelse(datum=f.profil.byra.datum,typ='utvärdering',beskrivning='Saklig prövning av hot och rutiner; motiverat behållande.',plan_id=plan.id,plansumma=plansumma(f.regelbas,profil,plan.id)))
    efter=l.bygg_bindning(f.byramapp,f.regelbas,k.bedomningsmapp,k.utkastmapp)
    assert efter.historik != fore.historik
    assert efter.model_dump(exclude={'historik'}) == fore.model_dump(exclude={'historik'})
    assert las_historik(f.byramapp).nasta_genomgang()==frist
    hinder=l.analysaktualitetshinder(f.byramapp,f.regelbas,gammal,f.profil.byra.datum,bedomningsmapp=k.bedomningsmapp,utkastmapp=k.utkastmapp)
    assert any('underlag har ändrats' in h for h in hinder)
    t=Analystjanst(f.byramapp,f.regelbas)
    for beslut in gammal.beslut:
        with pytest.raises(RiskanalysFel):
            t.beslut(beslut.tjanst,True,'Syntetisk','FfR',f.profil.byra.datum,'',p.registersumma(gammal))
    t.fornya(p.registersumma(gammal))
    nytt=l.las_analys(f.byramapp)
    assert nytt.beslut==gammal.beslut
    assert all(p.gallande_beslut(nytt,b.tjanst) is None for b in gammal.beslut)
    assert all(b.bekraftad_summa is None for a in nytt.tjanster for b in a.block)
